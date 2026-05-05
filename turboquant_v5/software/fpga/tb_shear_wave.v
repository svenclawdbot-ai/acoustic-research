//============================================================================
// TurboQuant Shear Wave Testbench
//============================================================================
`timescale 1ns / 1ps

module tb_shear_wave_controller;

    // Parameters
    parameter CLK_PERIOD = 8;  // 125 MHz = 8ns period
    parameter ADC_WIDTH = 14;
    
    // Signals
    reg clk_125m;
    reg rst_n;
    
    // ADC
    reg [ADC_WIDTH-1:0] adc_dat_a;
    reg [ADC_WIDTH-1:0] adc_dat_b;
    wire adc_clk;
    
    // DAC
    wire [13:0] dac_dat_a;
    wire [13:0] dac_dat_b;
    
    // TurboQuant interface
    wire ser;
    wire srclk;
    wire rclk;
    wire pulser_gate;
    
    // LEDs
    wire [7:0] led;
    
    // AXI register interface
    reg [31:0] reg_addr;
    reg [31:0] reg_wdata;
    reg reg_wen;
    reg reg_ren;
    wire [31:0] reg_rdata;
    wire reg_ack;
    
    // DMA
    wire [31:0] dma_wdata;
    wire dma_wen;
    wire [15:0] dma_addr;
    reg dma_ready;
    
    // Instantiate DUT
    turboquant_shear_wave_top #(
        .CLK_FREQ(125_000_000),
        .ADC_WIDTH(ADC_WIDTH),
        .NUM_ELEMENTS(8),
        .NUM_FREQS(9),
        .SAMPLES_PER_ACQ(1024)  // Smaller for simulation
    ) dut (
        .clk_125m(clk_125m),
        .rst_n(rst_n),
        .adc_dat_a(adc_dat_a),
        .adc_dat_b(adc_dat_b),
        .adc_clk(adc_clk),
        .dac_dat_a(dac_dat_a),
        .dac_dat_b(dac_dat_b),
        .ser(ser),
        .srclk(srclk),
        .rclk(rclk),
        .pulser_gate(pulser_gate),
        .led(led),
        .reg_addr(reg_addr),
        .reg_wdata(reg_wdata),
        .reg_wen(reg_wen),
        .reg_ren(reg_ren),
        .reg_rdata(reg_rdata),
        .reg_ack(reg_ack),
        .dma_wdata(dma_wdata),
        .dma_wen(dma_wen),
        .dma_addr(dma_addr),
        .dma_ready(dma_ready)
    );
    
    // Clock generation
    initial begin
        clk_125m = 0;
        forever #(CLK_PERIOD/2) clk_125m = ~clk_125m;
    end
    
    assign adc_clk = clk_125m;
    
    // ADC data generation (fake signal)
    always @(posedge adc_clk) begin
        if (!rst_n) begin
            adc_dat_a <= 0;
            adc_dat_b <= 0;
        end else begin
            // Generate fake ADC data with some pattern
            adc_dat_a <= $random % 8192;  // Random data for now
            adc_dat_b <= $random % 8192;
        end
    end
    
    // DMA ready
    initial begin
        dma_ready = 1;
    end
    
    // Test sequence
    initial begin
        $display("========================================");
        $display("TurboQuant Shear Wave Controller Testbench");
        $display("========================================");
        
        // Initialize
        rst_n = 0;
        reg_addr = 0;
        reg_wdata = 0;
        reg_wen = 0;
        reg_ren = 0;
        
        // Release reset
        #(CLK_PERIOD * 10);
        rst_n = 1;
        #(CLK_PERIOD * 10);
        
        $display("\n[1] Configure for 100 Hz, 5 cycles, 5 frequencies");
        
        // Set frequency select (100 Hz = index 4)
        write_reg(32'h08, 32'd4);
        
        // Set burst cycles
        write_reg(32'h0C, 32'd5);
        
        // Set number of frequencies
        write_reg(32'h10, 32'd5);
        
        // Read back configuration
        $display("\n[2] Read back configuration");
        read_reg(32'h08);
        read_reg(32'h0C);
        read_reg(32'h10);
        
        // Start acquisition
        $display("\n[3] Start acquisition");
        write_reg(32'h00, 32'd1);  // Set start bit
        
        // Wait for acquisition
        $display("\n[4] Waiting for acquisition...");
        #(CLK_PERIOD * 1000);
        
        // Check status
        $display("\n[5] Check status");
        read_reg(32'h04);
        
        // Stop acquisition
        $display("\n[6] Stop acquisition");
        write_reg(32'h00, 32'd2);  // Set stop bit
        
        #(CLK_PERIOD * 100);
        
        // Check LEDs
        $display("\n[7] LED status: %b", led);
        
        $display("\n========================================");
        $display("Simulation complete");
        $display("========================================");
        
        #(CLK_PERIOD * 100);
        $finish;
    end
    
    // AXI write task
    task write_reg;
        input [31:0] addr;
        input [31:0] data;
        begin
            @(posedge clk_125m);
            reg_addr = addr;
            reg_wdata = data;
            reg_wen = 1;
            @(posedge clk_125m);
            wait(reg_ack);
            reg_wen = 0;
            $display("  Write: addr=0x%08X, data=0x%08X", addr, data);
        end
    endtask
    
    // AXI read task
    task read_reg;
        input [31:0] addr;
        begin
            @(posedge clk_125m);
            reg_addr = addr;
            reg_ren = 1;
            @(posedge clk_125m);
            wait(reg_ack);
            reg_ren = 0;
            $display("  Read: addr=0x%08X, data=0x%08X", addr, reg_rdata);
        end
    endtask
    
    // Monitor pulser gate
    initial begin
        $monitor("Time=%0t | Pulser Gate=%b | LED=%b | Busy=%b",
                 $time, pulser_gate, led, led[1]);
    end
    
    // Waveform dump
    initial begin
        $dumpfile("shear_wave_tb.vcd");
        $dumpvars(0, tb_shear_wave_controller);
    end

endmodule
