//============================================================================
// Beamformer Top Module
// 8-channel dynamic beamformer for ultrasound NDE
// Red Pitaya STEMlab 125-14 compatible
//============================================================================

module beamformer_top #(
    parameter ADC_WIDTH = 12,
    parameter SUM_WIDTH = 16,
    parameter NUM_CHANNELS = 8,
    parameter MAX_DELAY_TAPS = 7,      // 0-6 taps = 0-48ns @ 125MHz
    parameter DELAY_ADDR_WIDTH = 3     // log2(NUM_CHANNELS)
)(
    // Clock and reset
    input wire clk,                     // 125 MHz system clock
    input wire rst_n,                   // Active-low reset
    
    // ADC inputs (8 channels, 12-bit each)
    input wire [ADC_WIDTH-1:0] adc_data_0,
    input wire [ADC_WIDTH-1:0] adc_data_1,
    input wire [ADC_WIDTH-1:0] adc_data_2,
    input wire [ADC_WIDTH-1:0] adc_data_3,
    input wire [ADC_WIDTH-1:0] adc_data_4,
    input wire [ADC_WIDTH-1:0] adc_data_5,
    input wire [ADC_WIDTH-1:0] adc_data_6,
    input wire [ADC_WIDTH-1:0] adc_data_7,
    input wire adc_valid,               // ADC data valid strobe
    
    // SPI configuration interface
    input wire spi_sck,
    input wire spi_mosi,
    output wire spi_miso,
    input wire spi_cs_n,
    
    // Beamformed output
    output reg [SUM_WIDTH-1:0] beamformed_out,
    output reg output_valid
);

    // Delay configuration registers (one per channel)
    reg [3:0] delay_taps [0:NUM_CHANNELS-1];
    
    // SPI interface for delay configuration
    wire spi_update;
    wire [7:0] spi_rx_data;
    wire [7:0] spi_tx_data;
    
    spi_slave spi_inst (
        .clk(clk),
        .rst_n(rst_n),
        .sck(spi_sck),
        .mosi(spi_mosi),
        .miso(spi_miso),
        .cs_n(spi_cs_n),
        .rx_data(spi_rx_data),
        .tx_data(spi_tx_data),
        .rx_valid(spi_update)
    );
    
    // Delay line outputs
    wire signed [ADC_WIDTH-1:0] delayed_data [0:NUM_CHANNELS-1];
    wire delayed_valid [0:NUM_CHANNELS-1];
    
    // Pack ADC data into array for generate loop
    wire [ADC_WIDTH-1:0] adc_data [0:NUM_CHANNELS-1];
    assign adc_data[0] = adc_data_0;
    assign adc_data[1] = adc_data_1;
    assign adc_data[2] = adc_data_2;
    assign adc_data[3] = adc_data_3;
    assign adc_data[4] = adc_data_4;
    assign adc_data[5] = adc_data_5;
    assign adc_data[6] = adc_data_6;
    assign adc_data[7] = adc_data_7;
    
    // Generate 8 delay lines
    genvar i;
    generate
        for (i = 0; i < NUM_CHANNELS; i = i + 1) begin : delay_gen
            delay_line #(
                .DATA_WIDTH(ADC_WIDTH),
                .MAX_TAPS(MAX_DELAY_TAPS)
            ) delay_inst (
                .clk(clk),
                .rst_n(rst_n),
                .din(adc_data[i]),
                .din_valid(adc_valid),
                .delay_sel(delay_taps[i]),
                .dout(delayed_data[i]),
                .dout_valid(delayed_valid[i])
            );
        end
    endgenerate
    
    // Summation stage with saturation
    // All channels should have aligned valid signals
    wire sum_valid = delayed_valid[0];
    
    reg signed [SUM_WIDTH-1:0] sum_stage1 [0:3];  // First level: 4 pairs
    reg signed [SUM_WIDTH-1:0] sum_stage2 [0:1];  // Second level: 2 pairs
    reg signed [SUM_WIDTH-1:0] sum_final;
    
    integer ch;
    
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (ch = 0; ch < 4; ch = ch + 1) sum_stage1[ch] <= 0;
            for (ch = 0; ch < 2; ch = ch + 1) sum_stage2[ch] <= 0;
            sum_final <= 0;
            beamformed_out <= 0;
            output_valid <= 0;
        end else begin
            // Pipeline stage 1: pair-wise sums
            sum_stage1[0] <= {{4{delayed_data[0][ADC_WIDTH-1]}}, delayed_data[0]} + 
                             {{4{delayed_data[1][ADC_WIDTH-1]}}, delayed_data[1]};
            sum_stage1[1] <= {{4{delayed_data[2][ADC_WIDTH-1]}}, delayed_data[2]} + 
                             {{4{delayed_data[3][ADC_WIDTH-1]}}, delayed_data[3]};
            sum_stage1[2] <= {{4{delayed_data[4][ADC_WIDTH-1]}}, delayed_data[4]} + 
                             {{4{delayed_data[5][ADC_WIDTH-1]}}, delayed_data[5]};
            sum_stage1[3] <= {{4{delayed_data[6][ADC_WIDTH-1]}}, delayed_data[6]} + 
                             {{4{delayed_data[7][ADC_WIDTH-1]}}, delayed_data[7]};
            
            // Pipeline stage 2: sum pairs
            sum_stage2[0] <= sum_stage1[0] + sum_stage1[1];
            sum_stage2[1] <= sum_stage1[2] + sum_stage1[3];
            
            // Pipeline stage 3: final sum
            sum_final <= sum_stage2[0] + sum_stage2[1];
            
            // Saturate to 16-bit output
            if (sum_final > 16'sd32767)
                beamformed_out <= 16'sd32767;
            else if (sum_final < -16'sd32768)
                beamformed_out <= -16'sd32768;
            else
                beamformed_out <= sum_final[15:0];
            
            output_valid <= sum_valid;
        end
    end
    
    // SPI configuration handling
    // SPI data format: [7:4] channel (0-7), [3:0] delay taps (0-6)
    reg [2:0] spi_channel;
    reg [3:0] spi_delay;
    
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            delay_taps[0] <= 0;
            delay_taps[1] <= 0;
            delay_taps[2] <= 0;
            delay_taps[3] <= 0;
            delay_taps[4] <= 0;
            delay_taps[5] <= 0;
            delay_taps[6] <= 0;
            delay_taps[7] <= 0;
        end else if (spi_update) begin
            spi_channel <= spi_rx_data[6:4];
            spi_delay <= spi_rx_data[3:0];
            if (spi_delay <= MAX_DELAY_TAPS)
                delay_taps[spi_channel] <= spi_delay;
        end
    end
    
    // SPI readback - return current delay setting
    assign spi_tx_data = {3'b000, spi_channel, 1'b0, delay_taps[spi_channel]};

endmodule