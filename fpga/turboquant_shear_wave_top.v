//============================================================================
// TurboQuant Shear Wave Top-Level Integration
//============================================================================
// Top-level module integrating all shear wave elastography components for the
// Red Pitaya TurboQuant system.
//
// Architecture:
// - Frequency generator (60-140 Hz tone bursts)
// - Element sequencer (8-channel array control)
// - Beamforming delay controller
// - Acquisition trigger controller
// - DMA interface to Red Pitaya
//============================================================================

`timescale 1ns / 1ps

module turboquant_shear_wave_top #(
    parameter CLK_FREQ = 125_000_000,
    parameter ADC_WIDTH = 14,
    parameter NUM_ELEMENTS = 8,
    parameter NUM_FREQS = 9,        // 60, 70, 80, 90, 100, 110, 120, 130, 140 Hz
    parameter SAMPLES_PER_ACQ = 8192
)(
    // System
    input wire clk_125m,             // 125 MHz system clock
    input wire rst_n,                // Active-low reset
    
    // Red Pitaya ADC inputs
    input wire [ADC_WIDTH-1:0] adc_dat_a,    // ADC channel A
    input wire [ADC_WIDTH-1:0] adc_dat_b,    // ADC channel B
    input wire adc_clk,                       // ADC clock (125 MHz)
    
    // Red Pitaya DAC outputs (for signal generator or external trigger)
    output reg [13:0] dac_dat_a,     // DAC channel A
    output reg [13:0] dac_dat_b,     // DAC channel B
    
    // TurboQuant Board Interface
    output wire ser,                  // 74HC595 serial data
    output wire srclk,                // 74HC595 shift clock
    output wire rclk,                 // 74HC595 latch clock
    output wire pulser_gate,          // HV pulser gate signal
    
    // Status LEDs (Red Pitaya LEDs)
    output wire [7:0] led,
    
    // AXI-style register interface (from Red Pitaya CPU)
    input wire [31:0] reg_addr,
    input wire [31:0] reg_wdata,
    input wire reg_wen,
    input wire reg_ren,
    output reg [31:0] reg_rdata,
    output reg reg_ack,
    
    // DMA interface to Red Pitaya
    output wire [31:0] dma_wdata,
    output wire dma_wen,
    output wire [15:0] dma_addr,
    input wire dma_ready
);

    //====================================================================
    // Control Registers (AXI interface)
    //====================================================================
    
    // Register map
    localparam REG_CONTROL = 8'h00;     // Control register
    localparam REG_STATUS = 8'h04;      // Status register
    localparam REG_FREQ_SELECT = 8'h08; // Frequency selection
    localparam REG_BURST_CYCLES = 8'h0C; // Burst cycles
    localparam REG_NUM_FREQS = 8'h10;   // Number of frequencies
    localparam REG_FOCUS_DEPTH = 8'h14; // Focus depth
    localparam REG_STEERING = 8'h18;    // Steering angle
    localparam REG_ELEM_POS_0 = 8'h20;  // Element 0 position
    // ... more element positions
    localparam REG_SOUND_SPEED = 8'h60; // Sound speed
    
    // Control register bits
    reg ctrl_start;                     // Start acquisition
    reg ctrl_stop;                      // Stop acquisition
    reg ctrl_single_shot;               // Single shot mode
    
    // Status register bits
    wire status_acquiring;
    wire status_burst_active;
    wire status_freq_ready;
    wire [3:0] status_current_freq;
    wire [2:0] status_current_element;
    
    // Register storage
    reg [3:0] reg_freq_select;
    reg [3:0] reg_burst_cycles;
    reg [3:0] reg_num_freqs;
    reg [31:0] reg_focus_depth;
    reg [15:0] reg_steering_angle;
    reg [31:0] reg_sound_speed;
    
    // AXI register interface
    always @(posedge clk_125m or negedge rst_n) begin
        if (!rst_n) begin
            ctrl_start <= 0;
            ctrl_stop <= 0;
            ctrl_single_shot <= 0;
            reg_freq_select <= 4'd4;        // Default 100 Hz
            reg_burst_cycles <= 4'd5;       // Default 5 cycles
            reg_num_freqs <= 4'd5;          // Default 5 frequencies
            reg_focus_depth <= 32'd30000;    // Default 30 mm
            reg_steering_angle <= 0;
            reg_sound_speed <= 32'd1540 << 16; // Default 1540 m/s (Q16.16)
            reg_rdata <= 0;
            reg_ack <= 0;
        end else begin
            reg_ack <= 0;
            
            if (reg_wen) begin
                reg_ack <= 1;
                case (reg_addr[7:0])
                    REG_CONTROL: begin
                        ctrl_start <= reg_wdata[0];
                        ctrl_stop <= reg_wdata[1];
                        ctrl_single_shot <= reg_wdata[2];
                    end
                    REG_FREQ_SELECT: reg_freq_select <= reg_wdata[3:0];
                    REG_BURST_CYCLES: reg_burst_cycles <= reg_wdata[3:0];
                    REG_NUM_FREQS: reg_num_freqs <= reg_wdata[3:0];
                    REG_FOCUS_DEPTH: reg_focus_depth <= reg_wdata;
                    REG_STEERING: reg_steering_angle <= reg_wdata[15:0];
                    REG_SOUND_SPEED: reg_sound_speed <= reg_wdata;
                    default: ;
                endcase
            end else if (reg_ren) begin
                reg_ack <= 1;
                case (reg_addr[7:0])
                    REG_CONTROL: reg_rdata <= {29'd0, ctrl_single_shot, ctrl_stop, ctrl_start};
                    REG_STATUS: reg_rdata <= {24'd0, status_freq_ready, status_burst_active, status_acquiring};
                    REG_FREQ_SELECT: reg_rdata <= {28'd0, reg_freq_select};
                    REG_BURST_CYCLES: reg_rdata <= {28'd0, reg_burst_cycles};
                    default: reg_rdata <= 32'hDEAD_BEEF;
                endcase
            end
        end
    end
    
    //====================================================================
    // Instantiate Shear Wave Frequency Generator
    //====================================================================
    
    wire freq_gen_burst_active;
    wire freq_gen_burst_done;
    wire freq_gen_pulser_gate;
    wire freq_gen_ready;
    wire [31:0] freq_gen_cycle_count;
    
    shear_wave_freq_gen #(
        .CLK_FREQ(CLK_FREQ),
        .MAX_FREQ(140),
        .MIN_FREQ(60),
        .FREQ_STEP(10),
        .NUM_FREQS(9)
    ) freq_gen_inst (
        .clk(clk_125m),
        .rst_n(rst_n),
        .freq_select(reg_freq_select),
        .burst_en(acq_burst_en),
        .burst_cycles(reg_burst_cycles),
        .ext_trigger(1'b0),             // Internal trigger only for now
        .freq_ready(freq_gen_ready),
        .burst_active(freq_gen_burst_active),
        .burst_done(freq_gen_burst_done),
        .cycle_count(freq_gen_cycle_count),
        .pulser_gate(freq_gen_pulser_gate)
    );
    
    //====================================================================
    // Instantiate Element Controller
    //====================================================================
    
    wire [7:0] element_pattern;
    wire element_busy;
    
    turboquant_controller #(
        .CLK_FREQ(CLK_FREQ),
        .SPI_FREQ(1_000_000)
    ) element_ctrl_inst (
        .clk(clk_125m),
        .rst_n(rst_n),
        .element_select(acq_element_select),
        .element_valid(acq_element_valid),
        .busy(element_busy),
        .ser(ser),
        .srclk(srclk),
        .rclk(rclk),
        .current_pattern(element_pattern)
    );
    
    //====================================================================
    // Instantiate Acquisition Trigger Controller
    //====================================================================
    
    wire acq_burst_en;
    wire [2:0] acq_element_select;
    wire acq_element_valid;
    wire [ADC_WIDTH-1:0] acq_sample_data;
    wire acq_sample_valid;
    wire [$clog2(SAMPLES_PER_ACQ)-1:0] acq_sample_addr;
    wire acq_complete;
    
    acquisition_trigger_controller #(
        .CLK_FREQ(CLK_FREQ),
        .ADC_WIDTH(ADC_WIDTH),
        .NUM_CHANNELS(2),
        .SAMPLES_PER_ACQ(SAMPLES_PER_ACQ)
    ) acq_ctrl_inst (
        .clk(clk_125m),
        .rst_n(rst_n),
        .start_acquisition(ctrl_start),
        .num_frequencies(reg_num_freqs),
        .burst_cycles(reg_burst_cycles),
        .freq_select(),                  // Connected internally
        .burst_en(acq_burst_en),
        .burst_done(freq_gen_burst_done),
        .burst_active(freq_gen_burst_active),
        .element_select(acq_element_select),
        .element_valid(acq_element_valid),
        .adc_data_a(adc_dat_a),
        .adc_data_b(adc_dat_b),
        .adc_clk(adc_clk),
        .adc_enable(),                   // Output
        .sample_data(acq_sample_data),
        .sample_valid(acq_sample_valid),
        .sample_addr(acq_sample_addr),
        .acquisition_complete(acq_complete),
        .current_freq_idx(status_current_freq),
        .current_element(status_current_element),
        .acquiring(status_acquiring)
    );
    
    //====================================================================
    // DMA Interface
    //====================================================================
    
    // Simple DMA: write samples as they arrive
    assign dma_wdata = {{32-ADC_WIDTH{1'b0}}, acq_sample_data};
    assign dma_wen = acq_sample_valid;
    assign dma_addr = acq_sample_addr;
    
    //====================================================================
    // Output Assignments
    //====================================================================
    
    assign pulser_gate = freq_gen_pulser_gate;
    assign status_burst_active = freq_gen_burst_active;
    assign status_freq_ready = freq_gen_ready;
    
    // LED status indication
    assign led = {
        status_acquiring,      // LED 7: Acquiring
        status_burst_active,   // LED 6: Burst active
        freq_gen_ready,        // LED 5: Frequency ready
        acq_complete,          // LED 4: Acquisition complete
        ctrl_start,            // LED 3: Start commanded
        ctrl_stop,             // LED 2: Stop commanded
        element_busy,          // LED 1: Element controller busy
        1'b1                   // LED 0: System alive (heartbeat)
    };
    
    // DAC outputs (for monitoring/triggering)
    always @(posedge clk_125m) begin
        // DAC A: Pulser gate signal (for external monitoring)
        dac_dat_a <= {freq_gen_pulser_gate, 13'd0};
        
        // DAC B: Acquisition trigger
        dac_dat_b <= {acq_sample_valid, 13'd0};
    end
    
    //====================================================================
    // Optional: Beamforming Controller (instantiated but not fully connected)
    //====================================================================
    
    wire beamforming_delays_valid;
    
    beamforming_delay_controller #(
        .CLK_FREQ(CLK_FREQ),
        .NUM_ELEMENTS(NUM_ELEMENTS)
    ) beamform_inst (
        .clk(clk_125m),
        .rst_n(rst_n),
        .focus_depth_mm(reg_focus_depth),
        .steering_angle(reg_steering_angle),
        .calc_delays(1'b0),               // Disabled for now
        .element_positions({8{32'd0}}),   // Placeholder
        .sound_speed_ms(reg_sound_speed),
        .element_delays_ns(),             // Output (not connected)
        .delays_valid(beamforming_delays_valid)
    );

endmodule
