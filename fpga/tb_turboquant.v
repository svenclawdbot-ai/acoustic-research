//============================================================================
// TurboQuant Controller Testbench
// Tests 74HC595 shift register interface
//============================================================================

`timescale 1ns/1ps

module tb_turboquant;

    // Parameters
    parameter CLK_PERIOD = 8;  // 125 MHz = 8ns period
    
    // Signals
    reg clk;
    reg rst_n;
    
    // Host interface
    reg [2:0] element_select;
    reg element_valid;
    wire busy;
    wire [7:0] current_pattern;
    
    // 74HC595 interface
    wire ser;
    wire srclk;
    wire rclk;
    
    // Status
    wire [7:0] led;
    
    // Instantiate DUT
    turboquant_controller #(
        .CLK_FREQ(125_000_000),
        .SPI_FREQ(1_000_000)
    ) dut (
        .clk(clk),
        .rst_n(rst_n),
        .element_select(element_select),
        .element_valid(element_valid),
        .busy(busy),
        .ser(ser),
        .srclk(srclk),
        .rclk(rclk),
        .current_pattern(current_pattern)
    );
    
    // Assign LEDs from current pattern
    assign led = current_pattern;
    
    // Clock generation
    initial clk = 0;
    always #(CLK_PERIOD/2) clk = ~clk;
    
    // Test sequence
    initial begin
        // Initialize
        rst_n = 0;
        element_select = 0;
        element_valid = 0;
        
        // Reset
        #(CLK_PERIOD * 10);
        rst_n = 1;
        #(CLK_PERIOD * 10);
        
        $display("============================================");
        $display("TurboQuant Controller Testbench");
        $display("============================================");
        
        // Test 1: Select element 0
        $display("\n[TEST 1] Select element 0");
        element_select = 3'd0;
        element_valid = 1;
        #(CLK_PERIOD);
        element_valid = 0;
        
        // Wait for operation to complete
        wait(!busy);
        #(CLK_PERIOD * 10);
        
        if (current_pattern == 8'b00000001)
            $display("✓ PASS: Element 0 selected, pattern = %08b", current_pattern);
        else
            $display("✗ FAIL: Expected 00000001, got %08b", current_pattern);
        
        // Test 2: Select element 3
        $display("\n[TEST 2] Select element 3");
        element_select = 3'd3;
        element_valid = 1;
        #(CLK_PERIOD);
        element_valid = 0;
        
        wait(!busy);
        #(CLK_PERIOD * 10);
        
        if (current_pattern == 8'b00001000)
            $display("✓ PASS: Element 3 selected, pattern = %08b", current_pattern);
        else
            $display("✗ FAIL: Expected 00001000, got %08b", current_pattern);
        
        // Test 3: Select element 7
        $display("\n[TEST 3] Select element 7");
        element_select = 3'd7;
        element_valid = 1;
        #(CLK_PERIOD);
        element_valid = 0;
        
        wait(!busy);
        #(CLK_PERIOD * 10);
        
        if (current_pattern == 8'b10000000)
            $display("✓ PASS: Element 7 selected, pattern = %08b", current_pattern);
        else
            $display("✗ FAIL: Expected 10000000, got %08b", current_pattern);
        
        // Test 4: Rapid switching test
        $display("\n[TEST 4] Rapid switching through all elements");
        repeat(3) begin
            integer i;
            for (i = 0; i < 8; i = i + 1) begin
                element_select = i[2:0];
                element_valid = 1;
                #(CLK_PERIOD);
                element_valid = 0;
                wait(!busy);
            end
        end
        $display("✓ Rapid switching completed");
        
        $display("\n============================================");
        $display("All tests completed!");
        $display("============================================");
        
        #(CLK_PERIOD * 100);
        $finish;
    end
    
    // Monitor signals
    initial begin
        $dumpfile("turboquant.vcd");
        $dumpvars(0, tb_turboquant);
    end
    
    // Timeout watchdog
    initial begin
        #(CLK_PERIOD * 50000);
        $display("ERROR: Simulation timeout!");
        $finish;
    end
    
    // Monitor 74HC595 signals
    initial begin
        $monitor("Time=%0t | element=%d | busy=%b | ser=%b srclk=%b rclk=%b | pattern=%08b",
                 $time, element_select, busy, ser, srclk, rclk, current_pattern);
    end

endmodule
