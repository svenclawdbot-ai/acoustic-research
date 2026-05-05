//============================================================================
// Programmable Delay Line
// Shift-register based delay with selectable tap
//============================================================================

module delay_line #(
    parameter DATA_WIDTH = 12,
    parameter MAX_TAPS = 7              // 0-6 taps supported
)(
    input wire clk,
    input wire rst_n,
    input wire [DATA_WIDTH-1:0] din,
    input wire din_valid,
    input wire [3:0] delay_sel,         // 0 = no delay, 1-6 = delay in samples
    output reg [DATA_WIDTH-1:0] dout,
    output reg dout_valid
);

    // Delay shift register
    reg [DATA_WIDTH-1:0] shift_reg [0:MAX_TAPS-1];
    reg [MAX_TAPS-1:0] valid_pipe;
    
    integer i;
    
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (i = 0; i < MAX_TAPS; i = i + 1) begin
                shift_reg[i] <= {DATA_WIDTH{1'b0}};
            end
            valid_pipe <= {MAX_TAPS{1'b0}};
            dout <= {DATA_WIDTH{1'b0}};
            dout_valid <= 1'b0;
        end else begin
            // Shift data through delay line
            if (din_valid) begin
                shift_reg[0] <= din;
                for (i = 1; i < MAX_TAPS; i = i + 1) begin
                    shift_reg[i] <= shift_reg[i-1];
                end
            end
            
            // Valid signal pipeline
            valid_pipe <= {valid_pipe[MAX_TAPS-2:0], din_valid};
            
            // Select output based on delay_sel
            case (delay_sel)
                4'd0: dout <= din;
                4'd1: dout <= shift_reg[0];
                4'd2: dout <= shift_reg[1];
                4'd3: dout <= shift_reg[2];
                4'd4: dout <= shift_reg[3];
                4'd5: dout <= shift_reg[4];
                4'd6: dout <= shift_reg[5];
                default: dout <= din;
            endcase
            
            // Valid output aligned with data
            case (delay_sel)
                4'd0: dout_valid <= din_valid;
                4'd1: dout_valid <= valid_pipe[0];
                4'd2: dout_valid <= valid_pipe[1];
                4'd3: dout_valid <= valid_pipe[2];
                4'd4: dout_valid <= valid_pipe[3];
                4'd5: dout_valid <= valid_pipe[4];
                4'd6: dout_valid <= valid_pipe[5];
                default: dout_valid <= din_valid;
            endcase
        end
    end

endmodule