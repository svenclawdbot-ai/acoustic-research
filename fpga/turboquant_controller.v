//============================================================================
// TurboQuant Sequential Controller
// Controls 74HC595 shift register for 8-element TX/RX switching
// Compatible with TurboQuant Mux LNA board
//============================================================================

module turboquant_controller #(
    parameter CLK_FREQ = 125_000_000,  // 125 MHz system clock
    parameter SPI_FREQ = 1_000_000     // 1 MHz SPI clock for shift register
)(
    // System
    input wire clk,                     // 125 MHz system clock
    input wire rst_n,                   // Active-low reset
    
    // Control interface (from host/CPU)
    input wire [2:0] element_select,    // 0-7: which element to activate
    input wire element_valid,           // Pulse to update selection
    output reg busy,                    // High during shift operation
    
    // 74HC595 Shift Register Interface
    output reg ser,                     // Serial data
    output reg srclk,                   // Shift register clock
    output reg rclk,                    // Latch clock (RCLK)
    
    // Status
    output reg [7:0] current_pattern    // Current 8-bit gate pattern
);

    // Clock divider for SPI frequency
    localparam CLK_DIV = CLK_FREQ / (2 * SPI_FREQ);
    reg [$clog2(CLK_DIV)-1:0] clk_div;
    reg spi_clk_en;                     // SPI clock enable pulse
    
    // State machine
    localparam IDLE = 3'd0;
    localparam LOAD_DATA = 3'd1;
    localparam SHIFT_OUT = 3'd2;
    localparam LATCH = 3'd3;
    localparam DONE = 3'd4;
    reg [2:0] state;
    
    // Shift register for data output
    reg [7:0] shift_data;
    reg [3:0] bit_cnt;
    
    // Generate 1 MHz SPI clock enable from 125 MHz
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            clk_div <= 0;
            spi_clk_en <= 0;
        end else begin
            if (clk_div == CLK_DIV - 1) begin
                clk_div <= 0;
                spi_clk_en <= 1;
            end else begin
                clk_div <= clk_div + 1;
                spi_clk_en <= 0;
            end
        end
    end
    
    // State machine for 74HC595 control
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            ser <= 0;
            srclk <= 0;
            rclk <= 0;
            busy <= 0;
            bit_cnt <= 0;
            shift_data <= 8'b00000001;  // Default: element 0 active
            current_pattern <= 8'b00000001;
        end else begin
            case (state)
                IDLE: begin
                    busy <= 0;
                    srclk <= 0;
                    rclk <= 0;
                    
                    if (element_valid) begin
                        // Create one-hot pattern for selected element
                        shift_data <= 8'b1 << element_select;
                        busy <= 1;
                        state <= LOAD_DATA;
                        bit_cnt <= 0;
                    end
                end
                
                LOAD_DATA: begin
                    // Load MSB first
                    ser <= shift_data[7];
                    if (spi_clk_en) begin
                        state <= SHIFT_OUT;
                    end
                end
                
                SHIFT_OUT: begin
                    // Generate SRCLK pulse
                    if (spi_clk_en) begin
                        srclk <= ~srclk;
                        
                        if (srclk) begin
                            // Rising edge just occurred, prepare next bit
                            bit_cnt <= bit_cnt + 1;
                            if (bit_cnt < 7) begin
                                ser <= shift_data[6 - bit_cnt];
                            end else begin
                                state <= LATCH;
                            end
                        end
                    end
                end
                
                LATCH: begin
                    // Generate RCLK pulse to latch outputs
                    srclk <= 0;
                    if (spi_clk_en) begin
                        rclk <= ~rclk;
                        if (rclk) begin
                            // Latch complete
                            current_pattern <= shift_data;
                            state <= DONE;
                        end
                    end
                end
                
                DONE: begin
                    rclk <= 0;
                    busy <= 0;
                    state <= IDLE;
                end
                
                default: state <= IDLE;
            endcase
        end
    end

endmodule