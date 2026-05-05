///////////////////////////////////////////////////////////////////////////////
// TurboQuant V5 MUX Controller
// ==============================
//
// AXI-Lite controlled state machine for DG408 8:1 analog MUX.
// 
// Features:
// - Software-controlled channel selection via AXI GPIO
// - Hardware-accelerated scanning sequence (auto-increment)
// - Settling time: programmable 1-10μs
// - Trigger output for ADC synchronization
//
// Register map (32-bit word):
//   [31:4] Reserved
//   [3]    /EN (active low, 1=disabled, 0=enabled)
//   [2:0]  Channel select (S2,S1,S0)
//
// Author: April 22, 2026
///////////////////////////////////////////////////////////////////////////////

`timescale 1 ns / 1 ps

module v5_mux_controller (
    // AXI-Lite interface
    input  wire        s_axi_aclk,
    input  wire        s_axi_aresetn,
    input  wire [31:0] s_axi_awaddr,
    input  wire        s_axi_awvalid,
    output wire        s_axi_awready,
    input  wire [31:0] s_axi_wdata,
    input  wire [3:0]  s_axi_wstrb,
    input  wire        s_axi_wvalid,
    output wire        s_axi_wready,
    output wire [1:0]  s_axi_bresp,
    output wire        s_axi_bvalid,
    input  wire        s_axi_bready,
    input  wire [31:0] s_axi_araddr,
    input  wire        s_axi_arvalid,
    output wire        s_axi_arready,
    output wire [31:0] s_axi_rdata,
    output wire [1:0]  s_axi_rresp,
    output wire        s_axi_rvalid,
    input  wire        s_axi_rready,
    
    // MUX control outputs (to Red Pitaya E1 connector GPIO)
    output wire [3:0]  gpio_out,
    
    // Trigger output (to ADC trigger)
    output wire        trigger_out,
    
    // Status
    output wire        busy,
    output wire [2:0]  current_channel
);

    // =========================================================================
    // AXI-Lite Register Interface
    // =========================================================================
    
    reg [31:0] control_reg;
    reg [31:0] status_reg;
    
    // Control register bits
    wire        ctrl_en      = control_reg[0];     // Enable scanning
    wire        ctrl_trigger = control_reg[1];     // Software trigger
    wire        ctrl_auto    = control_reg[2];     // Auto-scan mode
    wire [2:0]  ctrl_channel = control_reg[6:4];   // Manual channel select
    wire [7:0]  ctrl_settle  = control_reg[15:8];  // Settling time in clock cycles
    wire        ctrl_en_mux  = control_reg[16];    // /EN control (0=enabled, 1=disabled)
    
    // Status register
    wire [2:0]  stat_channel = status_reg[2:0];
    wire        stat_busy    = status_reg[3];
    wire        stat_done    = status_reg[4];
    
    // AXI-Lite write logic
    reg aw_en;
    reg ar_en;
    
    always @(posedge s_axi_aclk or negedge s_axi_aresetn) begin
        if (!s_axi_aresetn) begin
            control_reg <= 32'h0001_000F;  // Default: disabled, settle=1, channel=0
            aw_en <= 1'b1;
            ar_en <= 1'b1;
        end else begin
            if (s_axi_awvalid && s_axi_awready) begin
                aw_en <= 1'b0;
            end
            if (s_axi_wvalid && s_axi_wready) begin
                aw_en <= 1'b0;
                if (s_axi_awaddr[3:0] == 4'h0) begin
                    control_reg <= s_axi_wdata;
                end
            end
            if (s_axi_bvalid && s_axi_bready) begin
                aw_en <= 1'b1;
            end
            
            if (s_axi_arvalid && s_axi_arready) begin
                ar_en <= 1'b0;
            end
            if (s_axi_rvalid && s_axi_rready) begin
                ar_en <= 1'b1;
            end
        end
    end
    
    assign s_axi_awready = aw_en;
    assign s_axi_wready  = aw_en;
    assign s_axi_bresp   = 2'b00;
    assign s_axi_bvalid  = !aw_en;
    assign s_axi_arready = ar_en;
    assign s_axi_rresp   = 2'b00;
    assign s_axi_rdata   = (s_axi_araddr[3:0] == 4'h0) ? control_reg : status_reg;
    assign s_axi_rvalid  = !ar_en;
    
    // =========================================================================
    // MUX State Machine
    // =========================================================================
    
    localparam IDLE     = 3'b000;
    localparam SET_MUX  = 3'b001;
    localparam SETTLE   = 3'b010;
    localparam TRIGGER  = 3'b011;
    localparam WAIT     = 3'b100;
    localparam NEXT     = 3'b101;
    localparam DONE     = 3'b110;
    
    reg [2:0] state;
    reg [2:0] channel_counter;
    reg [15:0] settle_counter;
    reg [15:0] wait_counter;
    reg trigger_reg;
    
    wire [7:0] settle_target = (ctrl_settle == 0) ? 8'd125 : ctrl_settle;  // Default 1μs @ 125MHz
    wire [15:0] wait_target = 16'd12500;  // 100μs wait for acquisition
    
    always @(posedge s_axi_aclk or negedge s_axi_aresetn) begin
        if (!s_axi_aresetn) begin
            state <= IDLE;
            channel_counter <= 3'd0;
            settle_counter <= 16'd0;
            wait_counter <= 16'd0;
            trigger_reg <= 1'b0;
            status_reg <= 32'd0;
        end else begin
            case (state)
                IDLE: begin
                    trigger_reg <= 1'b0;
                    settle_counter <= 16'd0;
                    wait_counter <= 16'd0;
                    
                    if (ctrl_en && ctrl_trigger) begin
                        state <= SET_MUX;
                        channel_counter <= 3'd0;
                        status_reg[3] <= 1'b1;  // busy
                        status_reg[4] <= 1'b0;  // done
                    end else begin
                        status_reg[3] <= 1'b0;
                    end
                end
                
                SET_MUX: begin
                    // Assert /EN low (enable MUX), set channel
                    state <= SETTLE;
                    settle_counter <= 16'd0;
                end
                
                SETTLE: begin
                    // Wait for MUX settling
                    if (settle_counter >= settle_target) begin
                        state <= TRIGGER;
                    end else begin
                        settle_counter <= settle_counter + 1'b1;
                    end
                end
                
                TRIGGER: begin
                    // Assert trigger pulse
                    trigger_reg <= 1'b1;
                    state <= WAIT;
                    wait_counter <= 16'd0;
                end
                
                WAIT: begin
                    // Wait for acquisition complete
                    trigger_reg <= 1'b0;
                    if (wait_counter >= wait_target) begin
                        state <= NEXT;
                    end else begin
                        wait_counter <= wait_counter + 1'b1;
                    end
                end
                
                NEXT: begin
                    // Move to next channel or finish
                    if (ctrl_auto && channel_counter < 3'd7) begin
                        channel_counter <= channel_counter + 1'b1;
                        state <= SET_MUX;
                    end else begin
                        state <= DONE;
                    end
                end
                
                DONE: begin
                    status_reg[3] <= 1'b0;  // not busy
                    status_reg[4] <= 1'b1;  // done
                    state <= IDLE;
                end
                
                default: state <= IDLE;
            endcase
        end
    end
    
    // =========================================================================
    // Output Assignments
    // =========================================================================
    
    // GPIO output: [3]=/EN (active low), [2:0]=channel
    // In SET_MUX, SETTLE, TRIGGER, WAIT states: /EN=0 (enabled)
    // Otherwise: /EN=1 (disabled) or controlled by software
    assign gpio_out[3] = (state == IDLE) ? ctrl_en_mux : 1'b0;  // /EN
    assign gpio_out[2:0] = (state == IDLE) ? ctrl_channel : channel_counter;
    
    // Trigger output
    assign trigger_out = trigger_reg;
    
    // Status outputs
    assign busy = status_reg[3];
    assign current_channel = channel_counter;
    
    // Update status register
    always @(*) begin
        status_reg[2:0] = channel_counter;
    end

endmodule
