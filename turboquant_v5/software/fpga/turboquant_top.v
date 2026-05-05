//============================================================================
// TurboQuant Top-Level Module for Red Pitaya
// Sequential controller for 8-element ultrasound scanning
// Uses Red Pitaya built-in ADCs (IN1, IN2) for RX
//============================================================================

module turboquant_top (
    // System clock
    input wire clk,                     // 125 MHz from Red Pitaya
    input wire rst_n,                   // Active-low reset
    
    // Host interface (AXI or SPI - using simple register interface here)
    // These would connect to Red Pitaya's CPU interface
    input wire [2:0] element_select,    // Element to activate (0-7)
    input wire element_valid,           // Trigger update
    output wire busy,                   // Controller busy
    output wire [7:0] current_pattern,  // Current gate pattern
    
    // TurboQuant Board Interface (E1 Connector)
    output wire ser,                    // 74HC595 SER (Serial Data)
    output wire srclk,                  // 74HC595 SRCLK (Shift Clock)
    output wire rclk,                   // 74HC595 RCLK (Latch Clock)
    
    // Status LEDs (optional)
    output wire led0,                   // Element 0 indicator
    output wire led1,                   // Element 1 indicator
    output wire led2,                   // Element 2 indicator
    output wire led3,                   // Element 3 indicator
    output wire led4,                   // Element 4 indicator
    output wire led5,                   // Element 5 indicator
    output wire led6,                   // Element 6 indicator
    output wire led7                    // Element 7 indicator
);

    // Internal signals
    wire [7:0] gate_pattern;
    
    // TurboQuant sequential controller
    turboquant_controller #(
        .CLK_FREQ(125_000_000),
        .SPI_FREQ(1_000_000)
    ) controller (
        .clk(clk),
        .rst_n(rst_n),
        .element_select(element_select),
        .element_valid(element_valid),
        .busy(busy),
        .ser(ser),
        .srclk(srclk),
        .rclk(rclk),
        .current_pattern(gate_pattern)
    );
    
    // LED outputs show which element is active
    assign led0 = gate_pattern[0];
    assign led1 = gate_pattern[1];
    assign led2 = gate_pattern[2];
    assign led3 = gate_pattern[3];
    assign led4 = gate_pattern[4];
    assign led5 = gate_pattern[5];
    assign led6 = gate_pattern[6];
    assign led7 = gate_pattern[7];
    
    // Output current pattern for status reading
    assign current_pattern = gate_pattern;

endmodule