//============================================================================
// Beamformer Testbench
// Tests 3 steering angles: 0°, +15°, -15°
// Verifies delay configuration and beamformed output
//============================================================================

`timescale 1ns/1ps

module tb_beamformer;

    // Parameters
    parameter ADC_WIDTH = 12;
    parameter SUM_WIDTH = 16;
    parameter CLK_PERIOD = 8;  // 125 MHz = 8ns period
    
    // Signals
    reg clk;
    reg rst_n;
    
    // ADC inputs
    reg signed [ADC_WIDTH-1:0] adc_data [0:7];
    reg adc_valid;
    
    // SPI interface
    reg spi_sck;
    reg spi_mosi;
    wire spi_miso;
    reg spi_cs_n;
    
    // Outputs
    wire signed [SUM_WIDTH-1:0] beamformed_out;
    wire output_valid;
    
    // Instantiate DUT
    beamformer_top #(
        .ADC_WIDTH(ADC_WIDTH),
        .SUM_WIDTH(SUM_WIDTH),
        .NUM_CHANNELS(8),
        .MAX_DELAY_TAPS(7)
    ) dut (
        .clk(clk),
        .rst_n(rst_n),
        .adc_data_0(adc_data[0]),
        .adc_data_1(adc_data[1]),
        .adc_data_2(adc_data[2]),
        .adc_data_3(adc_data[3]),
        .adc_data_4(adc_data[4]),
        .adc_data_5(adc_data[5]),
        .adc_data_6(adc_data[6]),
        .adc_data_7(adc_data[7]),
        .adc_valid(adc_valid),
        .spi_sck(spi_sck),
        .spi_mosi(spi_mosi),
        .spi_miso(spi_miso),
        .spi_cs_n(spi_cs_n),
        .beamformed_out(beamformed_out),
        .output_valid(output_valid)
    );
    
    // Clock generation
    initial clk = 0;
    always #(CLK_PERIOD/2) clk = ~clk;
    
    // SPI clock (lower speed)
    initial spi_sck = 0;
    
    // Test variables
    integer i;
    integer sample_count;
    reg signed [SUM_WIDTH-1:0] max_amplitude_0;
    reg signed [SUM_WIDTH-1:0] max_amplitude_15;
    reg signed [SUM_WIDTH-1:0] max_amplitude_minus15;
    
    // Task: Send SPI command
    task send_spi;
        input [2:0] channel;
        input [3:0] delay;
        integer j;
        reg [15:0] data;
        begin
            data = {5'b00000, channel, 4'b0000, delay};
            spi_cs_n = 0;
            #(CLK_PERIOD * 2);
            
            for (j = 15; j >= 0; j = j - 1) begin
                spi_mosi = data[j];
                spi_sck = 1;
                #(CLK_PERIOD * 4);
                spi_sck = 0;
                #(CLK_PERIOD * 4);
            end
            
            #(CLK_PERIOD * 2);
            spi_cs_n = 1;
            spi_mosi = 0;
            #(CLK_PERIOD * 4);
        end
    endtask
    
    // Task: Generate plane wave input
    // simulates a plane wave arriving from a given angle
    // delay_pattern: array of 8 delay values
    task generate_plane_wave;
        input [3:0] delay_pattern [0:7];
        input [31:0] num_samples;
        input integer phase;
        integer n, ch;
        reg signed [ADC_WIDTH-1:0] sample;
        begin
            for (n = 0; n < num_samples; n = n + 1) begin
                @(posedge clk);
                adc_valid = 1;
                
                // Generate sine wave with per-channel delay
                for (ch = 0; ch < 8; ch = ch + 1) begin
                    // Simple sine: amplitude 1000, frequency ~1/20 samples
                    sample = $rtoi(1000.0 * $sin(2.0 * 3.14159 * (n + phase + delay_pattern[ch]) / 20.0));
                    adc_data[ch] = sample;
                end
            end
            @(posedge clk);
            adc_valid = 0;
        end
    endtask
    
    // Main test sequence
    initial begin
        // Initialize
        rst_n = 0;
        adc_valid = 0;
        spi_sck = 0;
        spi_mosi = 0;
        spi_cs_n = 1;
        sample_count = 0;
        max_amplitude_0 = 0;
        max_amplitude_15 = 0;
        max_amplitude_minus15 = 0;
        
        for (i = 0; i < 8; i = i + 1) begin
            adc_data[i] = 0;
        end
        
        // Reset
        #(CLK_PERIOD * 10);
        rst_n = 1;
        #(CLK_PERIOD * 10);
        
        $display("============================================");
        $display("Beamformer Testbench - 3-Angle Verification");
        $display("============================================");
        
        //========================================
        // TEST 1: Broadside (0°)
        //========================================
        $display("\n[TEST 1] Steering angle: 0° (broadside)");
        $display("Setting delays: [0,0,0,0,0,0,0,0]");
        
        // Configure delays: all zeros
        for (i = 0; i < 8; i = i + 1) begin
            send_spi(i[2:0], 4'd0);
        end
        
        // Generate test signal (plane wave from 0°)
        // No steering needed - all channels aligned
        begin
            reg [3:0] delays_0 [0:7];
            for (i = 0; i < 8; i = i + 1) delays_0[i] = 0;
            generate_plane_wave(delays_0, 100, 0);
        end
        
        // Capture max amplitude
        repeat(20) @(posedge clk);
        max_amplitude_0 = beamformed_out;
        $display("Peak amplitude at 0°: %d", max_amplitude_0);
        
        //========================================
        // TEST 2: +15° steering
        //========================================
        $display("\n[TEST 2] Steering angle: +15°");
        $display("Setting delays: [0,1,2,3,4,5,6,6] (progressive)");
        
        // Configure delays for +15° steering
        send_spi(3'd0, 4'd0);
        send_spi(3'd1, 4'd1);
        send_spi(3'd2, 4'd2);
        send_spi(3'd3, 4'd3);
        send_spi(3'd4, 4'd4);
        send_spi(3'd5, 4'd5);
        send_spi(3'd6, 4'd6);
        send_spi(3'd7, 4'd6);
        
        // Generate test signal (aligned with +15° steering)
        begin
            reg [3:0] delays_15 [0:7];
            delays_15[0] = 0; delays_15[1] = 1; delays_15[2] = 2; delays_15[3] = 3;
            delays_15[4] = 4; delays_15[5] = 5; delays_15[6] = 6; delays_15[7] = 6;
            generate_plane_wave(delays_15, 100, 25);
        end
        
        repeat(20) @(posedge clk);
        max_amplitude_15 = beamformed_out;
        $display("Peak amplitude at +15°: %d", max_amplitude_15);
        
        //========================================
        // TEST 3: -15° steering
        //========================================
        $display("\n[TEST 3] Steering angle: -15°");
        $display("Setting delays: [6,6,5,4,3,2,1,0] (reverse progressive)");
        
        // Configure delays for -15° steering (reversed)
        send_spi(3'd0, 4'd6);
        send_spi(3'd1, 4'd6);
        send_spi(3'd2, 4'd5);
        send_spi(3'd3, 4'd4);
        send_spi(3'd4, 4'd3);
        send_spi(3'd5, 4'd2);
        send_spi(3'd6, 4'd1);
        send_spi(3'd7, 4'd0);
        
        // Generate test signal (aligned with -15° steering)
        begin
            reg [3:0] delays_minus15 [0:7];
            delays_minus15[0] = 6; delays_minus15[1] = 6; delays_minus15[2] = 5; delays_minus15[3] = 4;
            delays_minus15[4] = 3; delays_minus15[5] = 2; delays_minus15[6] = 1; delays_minus15[7] = 0;
            generate_plane_wave(delays_minus15, 100, 50);
        end
        
        repeat(20) @(posedge clk);
        max_amplitude_minus15 = beamformed_out;
        $display("Peak amplitude at -15°: %d", max_amplitude_minus15);
        
        //========================================
        // RESULTS
        //========================================
        $display("\n============================================");
        $display("RESULTS SUMMARY");
        $display("============================================");
        $display("0°   steering peak: %d", max_amplitude_0);
        $display("+15° steering peak: %d", max_amplitude_15);
        $display("-15° steering peak: %d", max_amplitude_minus15);
        
        // Check that steering improves response
        if (max_amplitude_0 > 1000)
            $display("✓ PASS: 0° steering shows constructive interference");
        else
            $display("✗ FAIL: 0° steering amplitude too low");
            
        if (max_amplitude_15 > 1000)
            $display("✓ PASS: +15° steering shows constructive interference");
        else
            $display("✗ FAIL: +15° steering amplitude too low");
            
        if (max_amplitude_minus15 > 1000)
            $display("✓ PASS: -15° steering shows constructive interference");
        else
            $display("✗ FAIL: -15° steering amplitude too low");
        
        $display("\nSimulation complete!");
        $finish;
    end
    
    // VCD dump for waveform viewing
    initial begin
        $dumpfile("beamformer.vcd");
        $dumpvars(0, tb_beamformer);
    end
    
    // Timeout watchdog
    initial begin
        #(CLK_PERIOD * 10000);
        $display("ERROR: Simulation timeout!");
        $finish;
    end

endmodule