//============================================================================
// TurboQuant Shear Wave Controller - Frequency Generator Module
//============================================================================
// Generates variable frequency tone burst excitation (60-140 Hz) for shear wave
// elastography. Produces configurable bursts for sequential frequency
// acquisition.
//
// Features:
// - DDS-based frequency synthesis (60-140 Hz in 10 Hz steps)
// - Configurable burst duration (1-10 cycles)
// - External trigger input for synchronization
// - Ready for integration with TurboQuant HV pulser board
//============================================================================

`timescale 1ns / 1ps

module shear_wave_freq_gen #(
    parameter CLK_FREQ = 125_000_000,  // 125 MHz system clock
    parameter MAX_FREQ = 140,         // Maximum frequency (Hz)
    parameter MIN_FREQ = 60,          // Minimum frequency (Hz)
    parameter FREQ_STEP = 10,          // Frequency step (Hz)
    parameter NUM_FREQS = 9           // Number of frequencies (60-140 in 10 Hz steps)
)(
    // System
    input wire clk,                    // 125 MHz system clock
    input wire rst_n,                  // Active-low reset
    
    // Control interface
    input wire [$clog2(NUM_FREQS)-1:0] freq_select,  // 0-8: 60, 70, 80, ..., 140 Hz
    input wire burst_en,                 // Enable burst generation
    input wire [3:0] burst_cycles,       // Number of cycles in burst (1-15)
    input wire ext_trigger,              // External trigger input
    
    // Status outputs
    output reg freq_ready,               // High when frequency is valid
    output reg burst_active,             // High during burst generation
    output reg burst_done,               // Pulse when burst completes
    output reg [31:0] cycle_count,       // Current cycle count (for debug)
    
    // Output to pulser (HV gate signal)
    output reg pulser_gate               // Gate signal for HV pulser board
);

    // Frequency table (Hz)
    localparam [8:0][31:0] FREQ_TABLE = {
        32'd140, 32'd130, 32'd120, 32'd110, 32'd100,
        32'd90, 32'd80, 32'd70, 32'd60
    };
    
    // DDS parameters
    reg [31:0] phase_acc;                // Phase accumulator
    reg [31:0] phase_inc;                // Phase increment (tuning word)
    reg [31:0] current_freq;             // Currently selected frequency
    
    // DDS calculation: phase_inc = (freq * 2^32) / CLK_FREQ
    // For 125 MHz clock and target frequency:
    // 60 Hz: 60 * 2^32 / 125e6 = 2061584
    // 100 Hz: 100 * 2^32 / 125e6 = 3435974
    // 140 Hz: 140 * 2^32 / 125e6 = 4810364
    
    function automatic [31:0] calc_phase_inc;
        input [31:0] freq;
        begin
            calc_phase_inc = (freq << 32) / CLK_FREQ;
        end
    endfunction
    
    // State machine
    localparam IDLE = 2'd0;
    localparam GEN_BURST = 2'd1;
    localparam WAIT_REARM = 2'd2;
    
    reg [1:0] state;
    reg [31:0] sample_count;             // Sample counter for burst duration
    reg [31:0] target_samples;           // Target number of samples for burst
    reg [15:0] cycle_counter;            // Current cycle count
    reg trigger_sync, trigger_prev;      // Synchronization registers
    reg burst_trigger;                   // Internal burst trigger
    
    // Frequency selection
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            current_freq <= 32'd100;      // Default 100 Hz
            phase_inc <= 32'd3435974;     // Default for 100 Hz
        end else begin
            // Select frequency from table
            case (freq_select)
                4'd0: begin current_freq <= FREQ_TABLE[8]; phase_inc <= calc_phase_inc(FREQ_TABLE[8]); end // 60 Hz
                4'd1: begin current_freq <= FREQ_TABLE[7]; phase_inc <= calc_phase_inc(FREQ_TABLE[7]); end // 70 Hz
                4'd2: begin current_freq <= FREQ_TABLE[6]; phase_inc <= calc_phase_inc(FREQ_TABLE[6]); end // 80 Hz
                4'd3: begin current_freq <= FREQ_TABLE[5]; phase_inc <= calc_phase_inc(FREQ_TABLE[5]); end // 90 Hz
                4'd4: begin current_freq <= FREQ_TABLE[4]; phase_inc <= calc_phase_inc(FREQ_TABLE[4]); end // 100 Hz
                4'd5: begin current_freq <= FREQ_TABLE[3]; phase_inc <= calc_phase_inc(FREQ_TABLE[3]); end // 110 Hz
                4'd6: begin current_freq <= FREQ_TABLE[2]; phase_inc <= calc_phase_inc(FREQ_TABLE[2]); end // 120 Hz
                4'd7: begin current_freq <= FREQ_TABLE[1]; phase_inc <= calc_phase_inc(FREQ_TABLE[1]); end // 130 Hz
                4'd8: begin current_freq <= FREQ_TABLE[0]; phase_inc <= calc_phase_inc(FREQ_TABLE[0]); end // 140 Hz
                default: begin current_freq <= FREQ_TABLE[4]; phase_inc <= calc_phase_inc(FREQ_TABLE[4]); end // Default 100 Hz
            endcase
            freq_ready <= 1;
        end
    end
    
    // External trigger synchronization
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            trigger_sync <= 0;
            trigger_prev <= 0;
            burst_trigger <= 0;
        end else begin
            trigger_sync <= ext_trigger;
            trigger_prev <= trigger_sync;
            burst_trigger <= trigger_sync & ~trigger_prev;  // Rising edge detect
        end
    end
    
    // Burst generation state machine
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            burst_active <= 0;
            burst_done <= 0;
            pulser_gate <= 0;
            sample_count <= 0;
            target_samples <= 0;
            cycle_counter <= 0;
            cycle_count <= 0;
            phase_acc <= 0;
        end else begin
            // Default: clear done pulse
            burst_done <= 0;
            
            case (state)
                IDLE: begin
                    burst_active <= 0;
                    pulser_gate <= 0;
                    sample_count <= 0;
                    cycle_counter <= 0;
                    phase_acc <= 0;
                    
                    // Calculate target samples for requested burst duration
                    // target_samples = burst_cycles * CLK_FREQ / current_freq
                    if (burst_en && freq_ready) begin
                        target_samples <= (burst_cycles * CLK_FREQ) / current_freq;
                        
                        if (burst_trigger || ext_trigger) begin
                            state <= GEN_BURST;
                            burst_active <= 1;
                        end
                    end
                end
                
                GEN_BURST: begin
                    // Accumulate phase
                    phase_acc <= phase_acc + phase_inc;
                    sample_count <= sample_count + 1;
                    
                    // Generate pulser gate signal from MSB of phase accumulator
                    // This creates a square wave at the target frequency
                    pulser_gate <= phase_acc[31];
                    
                    // Count cycles (each half-cycle is one transition)
                    if (phase_acc[31] != phase_acc_prev) begin
                        cycle_counter <= cycle_counter + 1;
                    end
                    
                    // Check if burst is complete
                    if (sample_count >= target_samples - 1) begin
                        state <= WAIT_REARM;
                        burst_active <= 0;
                        burst_done <= 1;
                        pulser_gate <= 0;
                        cycle_count <= cycle_counter;
                    end
                end
                
                WAIT_REARM: begin
                    pulser_gate <= 0;
                    burst_active <= 0;
                    
                    // Wait for burst_en to go low before rearming
                    if (!burst_en) begin
                        state <= IDLE;
                    end
                end
            endcase
        end
    end
    
    // Store previous phase accumulator MSB for edge detection
    reg phase_acc_prev;
    always @(posedge clk) begin
        phase_acc_prev <= phase_acc[31];
    end

endmodule


//============================================================================
// Beamforming Delay Controller
//============================================================================
// Calculates and applies per-element delays for focused shear wave beams.
// Supports electronic steering and dynamic focusing.
//============================================================================

module beamforming_delay_controller #(
    parameter CLK_FREQ = 125_000_000,
    parameter NUM_ELEMENTS = 8,
    parameter MAX_DELAY_NS = 1000  // Maximum delay in nanoseconds (1 us)
)(
    // System
    input wire clk,
    input wire rst_n,
    
    // Control interface
    input wire [31:0] focus_depth_mm,    // Focus depth in mm (Q16.16 fixed point)
    input wire [15:0] steering_angle,    // Steering angle in degrees (0-360, Q8.8)
    input wire calc_delays,              // Pulse to calculate new delays
    
    // Element positions (in mm, Q16.16)
    input wire [NUM_ELEMENTS-1:0][31:0] element_positions,
    
    // Sound speed (m/s, Q16.16)
    input wire [31:0] sound_speed_ms,
    
    // Delay outputs (one per element)
    output reg [NUM_ELEMENTS-1:0][15:0] element_delays_ns,
    output reg delays_valid              // High when delays are calculated
);

    // Delay calculation state machine
    localparam IDLE = 2'd0;
    localparam CALC = 2'd1;
    localparam DONE = 2'd2;
    
    reg [1:0] state;
    reg [$clog2(NUM_ELEMENTS)-1:0] element_idx;
    
    // Trigonometry lookup tables (simplified - would use CORDIC in real implementation)
    // For now, using pre-calculated sine/cosine values
    
    // Focus calculation: delay = (path_length - max_path) / sound_speed
    // path_length = sqrt((x - x_focus)^2 + focus_depth^2)
    
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            element_idx <= 0;
            delays_valid <= 0;
            element_delays_ns <= {NUM_ELEMENTS{16'd0}};
        end else begin
            case (state)
                IDLE: begin
                    delays_valid <= 0;
                    element_idx <= 0;
                    
                    if (calc_delays) begin
                        state <= CALC;
                    end
                end
                
                CALC: begin
                    // Simplified delay calculation
                    // Full implementation would use CORDIC for sqrt/trig
                    
                    // For now: linear delay based on element position
                    // delay = element_x * sin(steering_angle) / sound_speed
                    
                    // Placeholder: calculate delays for current element
                    // This would be replaced with proper beamforming math
                    element_delays_ns[element_idx] <= element_idx * 50;  // 50ns per element
                    
                    if (element_idx == NUM_ELEMENTS - 1) begin
                        state <= DONE;
                    end else begin
                        element_idx <= element_idx + 1;
                    end
                end
                
                DONE: begin
                    delays_valid <= 1;
                    state <= IDLE;
                end
            endcase
        end
    end

endmodule


//============================================================================
// Acquisition Trigger Controller
//============================================================================
// Synchronizes ADC acquisition with shear wave firing. Manages sequential
// acquisition across multiple frequencies and receivers.
//============================================================================

module acquisition_trigger_controller #(
    parameter CLK_FREQ = 125_000_000,
    parameter ADC_WIDTH = 14,           // Red Pitaya ADC is 14-bit
    parameter NUM_CHANNELS = 2,       // Red Pitaya has 2 ADC inputs
    parameter SAMPLES_PER_ACQ = 8192  // Samples per acquisition
)(
    // System
    input wire clk,
    input wire rst_n,
    
    // Control interface
    input wire start_acquisition,        // Start acquisition sequence
    input wire [$clog2(9)-1:0] num_frequencies,  // Number of frequencies to acquire
    input wire [3:0] burst_cycles,     // Cycles per frequency
    
    // Frequency generator interface
    output reg [3:0] freq_select,      // Which frequency to select
    output reg burst_en,                 // Enable burst
    input wire burst_done,               // Burst complete
    input wire burst_active,             // Burst in progress
    
    // Element controller interface
    output reg [2:0] element_select,     // Which element to activate
    output reg element_valid,            // Update element selection
    
    // ADC interface (Red Pitaya)
    input wire [ADC_WIDTH-1:0] adc_data_a,   // ADC channel A
    input wire [ADC_WIDTH-1:0] adc_data_b,   // ADC channel B
    input wire adc_clk,                      // ADC clock
    output reg adc_enable,                   // ADC enable
    
    // DMA/Buffer interface
    output reg [ADC_WIDTH-1:0] sample_data,
    output reg sample_valid,
    output reg [$clog2(SAMPLES_PER_ACQ)-1:0] sample_addr,
    output reg acquisition_complete,
    
    // Status
    output reg [3:0] current_freq_idx,
    output reg [2:0] current_element,
    output reg acquiring
);

    // State machine
    localparam IDLE = 4'd0;
    localparam INIT_FREQ = 4'd1;
    localparam FIRE_BURST = 4'd2;
    localparam WAIT_BURST = 4'd3;
    localparam ACQUIRE_DATA = 4'd4;
    localparam STORE_SAMPLE = 4'd5;
    localparam NEXT_ELEMENT = 4'd6;
    localparam NEXT_FREQ = 4'd7;
    localparam COMPLETE = 4'd8;
    
    reg [3:0] state;
    
    // Counters
    reg [$clog2(SAMPLES_PER_ACQ)-1:0] sample_counter;
    reg [2:0] element_counter;
    reg [3:0] freq_counter;
    
    // Timing
    reg [31:0] wait_counter;
    localparam PRE_TRIG_DELAY = 100;    // Cycles before trigger
    localparam POST_TRIG_DELAY = 100;   // Cycles after burst
    
    // Acquisition state machine
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            freq_select <= 0;
            burst_en <= 0;
            element_select <= 0;
            element_valid <= 0;
            adc_enable <= 0;
            sample_valid <= 0;
            sample_counter <= 0;
            element_counter <= 0;
            freq_counter <= 0;
            current_freq_idx <= 0;
            current_element <= 0;
            acquiring <= 0;
            acquisition_complete <= 0;
            sample_addr <= 0;
        end else begin
            // Default: clear one-cycle signals
            element_valid <= 0;
            sample_valid <= 0;
            acquisition_complete <= 0;
            
            case (state)
                IDLE: begin
                    acquiring <= 0;
                    adc_enable <= 0;
                    burst_en <= 0;
                    
                    if (start_acquisition) begin
                        state <= INIT_FREQ;
                        freq_counter <= 0;
                        element_counter <= 0;
                        acquiring <= 1;
                    end
                end
                
                INIT_FREQ: begin
                    // Select current frequency
                    freq_select <= freq_counter;
                    current_freq_idx <= freq_counter;
                    element_counter <= 0;
                    state <= FIRE_BURST;
                end
                
                FIRE_BURST: begin
                    // Enable burst generation
                    burst_en <= 1;
                    
                    // Select element for firing (or fire all for plane wave)
                    element_select <= element_counter;
                    element_valid <= 1;
                    current_element <= element_counter;
                    
                    state <= WAIT_BURST;
                    wait_counter <= 0;
                end
                
                WAIT_BURST: begin
                    // Wait for burst to complete
                    if (burst_done) begin
                        burst_en <= 0;
                        state <= ACQUIRE_DATA;
                        sample_counter <= 0;
                        adc_enable <= 1;
                        wait_counter <= 0;
                    end
                end
                
                ACQUIRE_DATA: begin
                    // Wait for pre-trigger delay then start sampling
                    if (wait_counter < PRE_TRIG_DELAY) begin
                        wait_counter <= wait_counter + 1;
                    end else begin
                        // Start sampling
                        state <= STORE_SAMPLE;
                        sample_counter <= 0;
                    end
                end
                
                STORE_SAMPLE: begin
                    // Store ADC sample
                    sample_data <= adc_data_a;  // Or mux between A/B for 2-channel
                    sample_valid <= 1;
                    sample_addr <= sample_counter;
                    sample_counter <= sample_counter + 1;
                    
                    if (sample_counter >= SAMPLES_PER_ACQ - 1) begin
                        state <= NEXT_ELEMENT;
                    end
                end
                
                NEXT_ELEMENT: begin
                    // Move to next element or next frequency
                    if (element_counter >= NUM_ELEMENTS - 1) begin
                        state <= NEXT_FREQ;
                    end else begin
                        element_counter <= element_counter + 1;
                        state <= FIRE_BURST;
                    end
                end
                
                NEXT_FREQ: begin
                    // Move to next frequency
                    if (freq_counter >= num_frequencies - 1) begin
                        state <= COMPLETE;
                    end else begin
                        freq_counter <= freq_counter + 1;
                        state <= INIT_FREQ;
                    end
                end
                
                COMPLETE: begin
                    acquiring <= 0;
                    adc_enable <= 0;
                    burst_en <= 0;
                    acquisition_complete <= 1;
                    state <= IDLE;
                end
            endcase
        end
    end

endmodule
