# FMCW Chirp Generator — FPGA + Digital De-Chirp

Upgrade from CW Doppler to FMCW radar on Red Pitaya. Adds **range resolution** while keeping the existing 2.4 GHz frontend.

## Architecture

Keep the CW frontend (ADF4351 LO + LT5560 mixer + LNA + antennas) but replace the CW tone with a **linear frequency chirp**.

```
┌──────────────────────────────────────────────────────────────┐
│                    Red Pitaya FPGA                            │
│                                                               │
│  ┌──────────────┐    ┌──────────────┐                        │
│  │   Chirp Gen  │───►│  DAC OUT1    │──►[Upconverter]      │
│  │  (quadratic  │    │  125 MS/s    │    LO = 2.4 GHz        │
│  │   phase acc) │    │  0–50 MHz    │    RF = 2.4–2.45 GHz   │
│  └──────────────┘    └──────────────┘                        │
│         │                                                     │
│         │ (same waveform reference)                          │
│         ▼                                                     │
│  ┌──────────────┐    ┌──────────────┐    ┌─────────────────┐  │
│  │   ADC IN1    │───►│  De-Chirp    │───►│  CIC Decimator  │  │
│  │  125 MS/s    │    │  Complex Mult│    │  125M → 50k     │  │
│  │  delayed IF  │    │  × conj(chirp)│   │  LPF + ↓2500    │  │
│  └──────────────┘    └──────────────┘    └─────────────────┘  │
│                                                   │            │
│                                          AXI-Stream│            │
│                                                   ▼            │
│                                          ┌─────────────────┐  │
│                                          │  DMA S2MM       │  │
│                                          │  to DDR          │  │
│                                          └─────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                                                               │
                          ┌────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Python / ARM (Linux)                                        │
│  - Receive decimated I/Q blocks                             │
│  - FFT per chirp → range profile                            │
│  - Stacked range profiles → Range-Time-Intensity (RTI)      │
│  - CFAR detection → target ranges                           │
│  - Doppler across chirps → target speeds                    │
│  - Display: real-time range-Doppler or RTI plot             │
└─────────────────────────────────────────────────────────────┘
```

**How it works:**
1. FPGA generates a linear chirp at baseband (0–50 MHz over 1 ms)
2. DAC sends this to upconverter → 2.4–2.45 GHz RF
3. Reflected signal is delayed by round-trip time τ = 2R/c
4. Downconverter returns delayed chirp to baseband
5. FPGA multiplies received signal by **conjugate of transmitted chirp** → de-chirp
6. Result: constant-frequency tone at **beat frequency fb = (B/T) × τ**
7. CIC decimation + FFT → range peaks

---

## FMCW Theory Recap

### Beat Frequency

For a linear chirp sweeping bandwidth **B** over duration **T**:

```
fb = (B/T) × τ = (B/T) × (2R/c)
```

Solving for range:
```
R = (c × T × fb) / (2 × B)
```

### Example Parameters

| Parameter | Value | Result |
|-----------|-------|--------|
| Bandwidth B | 50 MHz | Range resolution ΔR = c/(2B) = **3 m** |
| Chirp duration T | 1 ms | |
| Chirp rate B/T | 50 GHz/s | |
| Max range R_max | 50 m | fb_max = (50e9)(2×50/3e8) = **16.7 kHz** |
| Sample rate fs | 125 MS/s | |
| Decimation | 2500× | Output rate = 50 kSps |
| FFT size | 1024 | Range bin width = 50 kSps/1024 ≈ **49 Hz/bin** |
| Range per bin | — | ΔR_bin = (c×T)/(2×B) × (fs_decim/N_fft) ≈ **0.14 m** |

Wait, let me recalculate range resolution properly:

The theoretical range resolution from bandwidth:
```
ΔR = c / (2 × B) = 3e8 / (2 × 50e6) = 3 meters
```

The FFT bin spacing in range:
```
Each FFT bin = fs_decim / N_fft = 50e3 / 1024 = 48.8 Hz
Range per bin = (c × T) / (2 × B) × (1/T) × bin_width  ... hmm
```

Actually, simpler:
```
fb = (2 × B × R) / (c × T)  → wait this isn't right either
```

Let me be precise. For a chirp with bandwidth B and duration T:
- Frequency sweeps from f0 to f0+B linearly: f_tx(t) = f0 + (B/T)·t
- Delayed signal: f_rx(t) = f_tx(t - τ) = f0 + (B/T)·(t - τ)
- Beat frequency (difference): fb = f_tx(t) - f_rx(t) = (B/T)·τ = (B/T)·(2R/c)
- This is constant during the chirp!

So: **R = (c × T × fb) / (2 × B)**

For our parameters:
- R = (3e8 × 1e-3 × fb) / (2 × 50e6) = (300 × fb) / 100e6 = **fb × 3×10⁻⁶ m/Hz**
- Or: **R = fb / 333.3** (R in meters, fb in Hz)

At fb = 333 Hz → R = 1 m
At fb = 3333 Hz → R = 10 m
At fb = 16667 Hz → R = 50 m

After decimation to 50 kSps and 1024-point FFT:
- FFT bin spacing = 50,000 / 1024 = 48.8 Hz
- Range per bin = 48.8 / 333.3 = **0.146 m**
- But actual resolution limited by bandwidth to **3 m**

The FFT oversamples the range. We get ~20 bins across the 3 m resolution cell. Good for interpolation, not for resolving two targets within 3 m.

### Doppler in FMCW

If the target is moving, the Doppler shift adds to the beat frequency:
```
f_measured = fb ± fdoppler
```

For 2.4 GHz:
- fd = 2v/λ = 2v / 0.125 = 16·v (Hz per m/s)
- Walking at 1 m/s: fd = 16 Hz
- This is small compared to fb (333 Hz at 1 m, 3333 Hz at 10 m)
- Doppler causes small range offset error

For simultaneous range + Doppler, use **multiple chirps** (triangle or sawtooth) and solve the pair of equations. Or use a longer coherent processing interval.

---

## FPGA Design

### 1. Chirp Generator (Quadratic Phase Accumulator)

A linear frequency sweep requires **quadratic phase**:
```
φ(t) = 2π × (f0·t + 0.5×(B/T)×t²)
```

In discrete time (fs = 125 MHz, dt = 8 ns):
```
φ[n] = φ[n-1] + Δφ[n]
Δφ[n] = Δφ[n-1] + ΔΔφ  (constant increment)
```

Where:
- ΔΔφ = 2π × (B/T) × dt² × (2^N / 2π) = (B/T) × dt² × 2^N
  (in DDS phase word units)

For 32-bit phase (N=32):
```
B = 50 MHz, T = 1 ms, dt = 1/125e6
ΔΔφ = (50e6 / 1e-3) × (1/125e6)² × 2^32
    = 50e9 × 6.4e-17 × 4.29e9
    ≈ 13,743
```

So each sample:
1. `freq_word += 13743`
2. `phase_acc += freq_word`
3. `sin_out, cos_out = lookup(phase_acc)`

**Verilog implementation:**

```verilog
///////////////////////////////////////////////////////////////////////////////
// FMCW Chirp Generator with Quadratic Phase Accumulator
// Generates linear frequency ramp: 0 -> B over T_chirp
///////////////////////////////////////////////////////////////////////////////

module fmcw_chirp_gen (
    input  wire        clk,           // 125 MHz
    input  wire        rst,
    input  wire        enable,        // Start chirp
    input  wire [31:0] chirp_rate,   // Frequency word increment (ΔΔφ)
    input  wire [31:0] start_freq,   // Initial frequency word
    input  wire [31:0] chirp_length, // Number of samples in chirp
    input  wire [31:0] guard_length, // Guard samples between chirps
    output reg  [13:0] dac_i,        // 14-bit signed I output
    output reg  [13:0] dac_q,        // 14-bit signed Q output
    output reg         chirp_active, // High during chirp
    output reg         chirp_sync,   // One-cycle pulse at chirp start
    output reg  [31:0] sample_counter
);

    // Phase accumulator
    reg [31:0] phase_acc;
    reg [31:0] freq_acc;
    
    // State machine
    localparam IDLE  = 2'b00;
    localparam CHIRP = 2'b01;
    localparam GUARD = 2'b10;
    
    reg [1:0] state;
    reg [31:0] counter;
    
    // Sine/Cosine lookup table (quarter-wave compressed)
    // 12-bit address → 14-bit output
    // Full table: 4096 entries × 14 bits = 57 kbit
    // Quarter table: 1024 entries × 14 bits = 14 kbit (fits in BRAM)
    
    reg [13:0] sin_lut [0:1023];
    reg [13:0] cos_lut [0:1023];
    
    initial begin
        // Initialize LUTs (synthesiser will load from .coe file)
        // Or use $readmemh in simulation
    end
    
    wire [11:0] phase_12bit = phase_acc[31:20]; // Upper 12 bits for LUT
    wire [1:0]  phase_quadrant = phase_acc[31:30];
    
    wire [13:0] sin_raw;
    wire [13:0] cos_raw;
    
    // Quadrant decoding for quarter-wave symmetry
    assign sin_raw = (phase_quadrant == 2'b00) ?  sin_lut[phase_12bit] :
                     (phase_quadrant == 2'b01) ?  cos_lut[1023 - phase_12bit] :
                     (phase_quadrant == 2'b10) ? -sin_lut[phase_12bit] :
                                                  -cos_lut[1023 - phase_12bit];
    
    assign cos_raw = (phase_quadrant == 2'b00) ?  cos_lut[phase_12bit] :
                     (phase_quadrant == 2'b01) ? -sin_lut[1023 - phase_12bit] :
                     (phase_quadrant == 2'b10) ? -cos_lut[phase_12bit] :
                                                   sin_lut[1023 - phase_12bit];
    
    // Scale to 14-bit signed: sin/cos in [-1,1] → [-8192, 8191]
    // (raw LUT values are already scaled)
    
    always @(posedge clk) begin
        if (rst) begin
            state <= IDLE;
            phase_acc <= 0;
            freq_acc <= 0;
            counter <= 0;
            chirp_active <= 0;
            chirp_sync <= 0;
            sample_counter <= 0;
            dac_i <= 0;
            dac_q <= 0;
        end else begin
            chirp_sync <= 0;
            
            case (state)
                IDLE: begin
                    if (enable) begin
                        state <= CHIRP;
                        freq_acc <= start_freq;
                        phase_acc <= 0;
                        counter <= 0;
                        chirp_sync <= 1;
                        sample_counter <= 0;
                    end
                end
                
                CHIRP: begin
                    chirp_active <= 1;
                    
                    // Quadratic phase accumulation
                    freq_acc <= freq_acc + chirp_rate;
                    phase_acc <= phase_acc + freq_acc;
                    
                    dac_i <= sin_raw;
                    dac_q <= cos_raw;
                    
                    counter <= counter + 1;
                    sample_counter <= sample_counter + 1;
                    
                    if (counter >= chirp_length - 1) begin
                        state <= GUARD;
                        counter <= 0;
                        chirp_active <= 0;
                    end
                end
                
                GUARD: begin
                    dac_i <= 0;
                    dac_q <= 0;
                    counter <= counter + 1;
                    
                    if (counter >= guard_length - 1) begin
                        state <= IDLE;
                    end
                end
            endcase
        end
    end

endmodule
```

**Alternative: Use Xilinx DDS Compiler IP**

The DDS Compiler v6.0 can be configured with "Phase Increment Programmability" set to "Streaming". You stream a new phase increment every clock cycle, creating the quadratic phase ramp.

Configuration:
- Phase Width: 32 bits
- Output Width: 14 bits  
- Noise Shaping: Phase Dithering
- Has Phase Out: No
- Has TREADY: Yes
- Frequency Resolution: 0.029 Hz

Then feed it with incrementing frequency words.

### 2. Digital De-Chirp (Complex Multiplier)

```verilog
module fmcw_dechirp (
    input  wire        clk,
    input  wire        rst,
    input  wire [13:0] adc_in,        // 14-bit signed ADC input (real)
    input  wire [13:0] chirp_i,       // Reference chirp I (from generator)
    input  wire [13:0] chirp_q,       // Reference chirp Q (from generator)
    input  wire        chirp_active,  // Only de-chirp during chirp
    output reg  [27:0] dechirp_i,     // 28-bit complex output I
    output reg  [27:0] dechirp_q      // 28-bit complex output Q
);

    // Complex multiplication: adc × conj(chirp)
    // conj(chirp_i + j·chirp_q) = chirp_i - j·chirp_q
    // adc × conj(chirp) = adc·chirp_i - j·adc·chirp_q
    // Real part: adc·chirp_i
    // Imag part: -adc·chirp_q
    
    wire signed [27:0] mult_i;
    wire signed [27:0] mult_q;
    
    assign mult_i = $signed(adc_in) * $signed(chirp_i);
    assign mult_q = -$signed(adc_in) * $signed(chirp_q);
    
    always @(posedge clk) begin
        if (rst) begin
            dechirp_i <= 0;
            dechirp_q <= 0;
        end else if (chirp_active) begin
            dechirp_i <= mult_i;
            dechirp_q <= mult_q;
        end else begin
            dechirp_i <= 0;
            dechirp_q <= 0;
        end
    end

endmodule
```

### 3. CIC Decimator

After de-chirping, the signal is in the kHz range. We can decimate aggressively.

**CIC filter parameters:**
- Decimation factor R = 2500 (125 MSps → 50 kSps)
- Differential delay M = 1
- Number of stages N = 4

Use Xilinx CIC Compiler v4.0:
- Filter Type: Decimation
- Number of Stages: 4
- Differential Delay: 1
- Sample Rate Change: Fixed (2500)
- Input Sample Frequency: 125 MHz
- Clock Frequency: 125 MHz
- Input Data Width: 28 bits
- Output Data Width: 28 bits
- Quantization: Truncation

Or implement in Verilog:

```verilog
module cic_decimator (
    input  wire        clk,
    input  wire        rst,
    input  wire [27:0] data_in_i,
    input  wire [27:0] data_in_q,
    input  wire        data_valid,
    output reg  [27:0] data_out_i,
    output reg  [27:0] data_out_q,
    output reg         out_valid
);
    // 4-stage CIC decimator, R=2500, M=1
    // Simplified: use Xilinx IP in production
    
    // Integrator stages (running at 125 MHz)
    reg signed [63:0] int1_i, int1_q;
    reg signed [63:0] int2_i, int2_q;
    reg signed [63:0] int3_i, int3_q;
    reg signed [63:0] int4_i, int4_q;
    
    // Comb stages (running at 50 kHz after decimation)
    // ... implemented with counter and sample/hold
    
    // For production, use Xilinx CIC Compiler IP
    // This stub shows the interface

endmodule
```

### 4. Complete Block Design (Vivado TCL)

```tcl
# fmcw_bd.tcl — Vivado block design for FMCW radar

# Create design
set design_name fmcw_radar

# Add Zynq PS
set ps [create_bd_cell -type ip -vlnv xilinx.com:ip:processing_system7:5.5 ps7]
# ... configure PS with HP0 AXI and clock

# Add AXI GPIO for chirp control
set gpio [create_bd_cell -type ip -vlnv xilinx.com:ip:axi_gpio:2.0 chirp_ctrl]
set_property -dict [list \
    CONFIG.C_GPIO_WIDTH {32} \
    CONFIG.C_ALL_OUTPUTS {1} \
] $gpio

# Add DDS Compiler for chirp generation
set dds [create_bd_cell -type ip -vlnv xilinx.com:ip:dds_compiler:6.0 chirp_dds]
set_property -dict [list \
    CONFIG.PartsPresent {Phase_Generator_and_SIN_COS_LUT} \
    CONFIG.DDS_Clock_Rate {125} \
    CONFIG.Frequency_Resolution {0.029} \
    CONFIG.Noise_Shaping {Phase_Dithering} \
    CONFIG.Phase_Width {32} \
    CONFIG.Output_Width {14} \
    CONFIG.Has_Phase_Out {false} \
    CONFIG.Has_ARESETn {true} \
] $dds

# Custom chirp controller (quadratic phase)
# Replaces direct DDS control with streaming phase increments
# ...

# Add AXI DMA for I/Q streaming
set dma [create_bd_cell -type ip -vlnv xilinx.com:ip:axi_dma:7.1 s2mm_dma]
set_property -dict [list \
    CONFIG.c_include_sg {0} \
    CONFIG.c_include_mm2s {0} \
    CONFIG.c_include_s2mm {1} \
    CONFIG.c_s2mm_burst_size {16} \
] $dma

# Add AXI Interconnect
set interconnect [create_bd_cell -type ip -vlnv xilinx.com:ip:axi_interconnect:2.1 axi_ic]

# Add AXI Stream FIFO (buffer decimated I/Q)
set fifo [create_bd_cell -type ip -vlnv xilinx.com:ip:axi_fifo_mm_s:4.2 axis_fifo]

# Add AXI Stream Data FIFO (between CIC and DMA)
set stream_fifo [create_bd_cell -type ip -vlnv xilinx.com:ip:axis_data_fifo:2.0 cic_to_dma]

# Connections:
# Zynq PS ──► AXI Interconnect ──► AXI GPIO (chirp parameters)
#                                     │
#                                     ▼
#                              Custom Chirp Controller
#                                     │
#                                     ▼
#                              DDS Compiler ──► DAC
#                                     │
#                                     ▼ (reference samples)
#                              Complex Multiplier (ADC × conj(DDS))
#                                     │
#                                     ▼
#                              CIC Decimator (125M → 50k)
#                                     │
#                                     ▼
#                              AXI Stream FIFO
#                                     │
#                                     ▼
#                              AXI DMA S2MM ──► DDR
#                                     │
#                                     ▼
#                              Linux / Python
```

---

## Software Processing

### Python FMCW Processor

```python
#!/usr/bin/env python3
"""
FMCW Radar Processor — Range Profile Extraction

Usage:
    python fmcw_processor.py --rp-ip 192.168.1.100 --mode fmcw
"""

import argparse
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
from collections import deque

from rp_sdr_client import RedPitayaSDR  # Same client, different processing


# ─── FMCW Parameters ─────────────────────────────────────────────────────────

DEFAULT_FMCW_CONFIG = {
    'bandwidth_hz': 50e6,        # 50 MHz chirp bandwidth
    'chirp_duration_ms': 1.0,     # 1 ms chirp
    'chirp_rate_hz_per_s': 50e9,  # B/T = 50 GHz/s
    'carrier_hz': 2.4e9,         # RF carrier (via upconverter)
    'sample_rate_decimated': 50e3, # After CIC decimation
    'fft_size': 1024,
    'guard_ms': 0.2,             # Guard time between chirps
    'max_range_m': 50.0,
}

# Range calculation: R = (c * T * fb) / (2 * B)
SPEED_OF_LIGHT = 299792458.0


def beat_freq_to_range(fb_hz: float, config: dict) -> float:
    """Convert beat frequency to range in meters."""
    B = config['bandwidth_hz']
    T = config['chirp_duration_ms'] / 1000.0
    return (SPEED_OF_LIGHT * T * fb_hz) / (2.0 * B)


def range_to_beat_freq(R_m: float, config: dict) -> float:
    """Convert range to beat frequency in Hz."""
    B = config['bandwidth_hz']
    T = config['chirp_duration_ms'] / 1000.0
    return (2.0 * B * R_m) / (SPEED_OF_LIGHT * T)


class FMCWProcessor:
    """
    Process FMCW I/Q samples from Red Pitaya.
    
    Assumes samples are already de-chirped and decimated by FPGA.
    Input: I/Q samples at 50 kSPS, one chirp period per buffer.
    """
    
    def __init__(self, config: dict = None):
        self.config = config or DEFAULT_FMCW_CONFIG
        self.fs = self.config['sample_rate_decimated']
        self.fft_size = self.config['fft_size']
        
        # Range axis
        self.freq_bins = np.fft.rfftfreq(self.fft_size, d=1.0/self.fs)
        self.range_bins = np.array([beat_freq_to_range(f, self.config) 
                                    for f in self.freq_bins])
        
        # Valid range mask (0 to max_range)
        self.valid_mask = (self.range_bins >= 0) & (self.range_bins <= self.config['max_range_m'])
        
        # History for range-time plot
        self.range_history = deque(maxlen=500)
        
        # CFAR parameters
        self.cfar_guard_cells = 4
        self.cfar_training_cells = 16
        self.cfar_threshold_factor = 15.0  # dB above noise
    
    def process_chirp(self, iq: np.ndarray) -> dict:
        """
        Process one chirp worth of de-chirped I/Q samples.
        Returns range profile and detections.
        """
        if len(iq) < self.fft_size:
            # Pad or return empty
            return {}
        
        # Window and FFT
        window = signal.windows.hann(self.fft_size)
        n_use = min(len(iq), self.fft_size)
        
        iq_windowed = iq[:n_use] * window[:n_use]
        spectrum = np.fft.rfft(iq_windowed, n=self.fft_size)
        power = np.abs(spectrum) ** 2
        power_db = 10 * np.log10(power + 1e-12)
        
        # Keep only valid range bins
        power_db_valid = power_db.copy()
        power_db_valid[~self.valid_mask] = -100
        
        # CFAR detection
        detections = self._cfar_detect(power_db_valid)
        
        result = {
            'range_bins': self.range_bins[self.valid_mask],
            'range_profile_db': power_db_valid[self.valid_mask],
            'detections': detections,
            'raw_power_db': power_db,
        }
        
        self.range_history.append(power_db_valid)
        
        return result
    
    def _cfar_detect(self, power_db: np.ndarray) -> list:
        """
        Cell-Averaging CFAR detector.
        Returns list of detections: [{'range_m': float, 'power_db': float}, ...]
        """
        detections = []
        n = len(power_db)
        
        g = self.cfar_guard_cells
        t = self.cfar_training_cells
        
        for i in range(g + t, n - g - t):
            # Cell under test
            cut = power_db[i]
            
            # Training cells (excluding guard)
            left_train = power_db[i-g-t : i-g]
            right_train = power_db[i+g+1 : i+g+t+1]
            
            if len(left_train) == 0 or len(right_train) == 0:
                continue
            
            noise_level = 10 * np.log10(
                (np.mean(10**(left_train/10)) + np.mean(10**(right_train/10))) / 2
            )
            
            threshold = noise_level + self.cfar_threshold_factor
            
            if cut > threshold:
                detections.append({
                    'range_m': self.range_bins[i],
                    'power_db': cut,
                    'snr_db': cut - noise_level,
                    'beat_freq_hz': self.freq_bins[i]
                })
        
        return detections
    
    def get_range_time_intensity(self) -> np.ndarray:
        """Return stacked range profiles for waterfall display."""
        if len(self.range_history) == 0:
            return np.array([])
        return np.array(list(self.range_history))


class FMCWVisualizer:
    """Real-time FMCW range profile display."""
    
    def __init__(self, processor: FMCWProcessor):
        self.proc = processor
        
        plt.ion()
        self.fig, self.axes = plt.subplots(2, 1, figsize=(12, 8))
        self.fig.suptitle("FMCW Radar — Range Profiles", fontsize=14)
        
        # Range profile
        self.ax_profile = self.axes[0]
        self.line_profile, = self.ax_profile.plot([], [], 'b-', lw=1)
        self.ax_profile.set_xlabel("Range (m)")
        self.ax_profile.set_ylabel("Power (dB)")
        self.ax_profile.set_xlim(0, processor.config['max_range_m'])
        self.ax_profile.set_ylim(-80, 0)
        self.ax_profile.grid(True, alpha=0.3)
        self.detection_markers = []
        
        # Range-Time Intensity (waterfall)
        self.ax_rti = self.axes[1]
        self.im_rti = None
        
        plt.tight_layout()
        plt.show(block=False)
    
    def update(self, result: dict):
        if not result:
            return
        
        # Update range profile
        ranges = result['range_bins']
        profile = result['range_profile_db']
        
        self.line_profile.set_data(ranges, profile)
        
        # Clear old detection markers
        for m in self.detection_markers:
            m.remove()
        self.detection_markers = []
        
        # Add detection markers
        for det in result['detections']:
            m = self.ax_profile.axvline(x=det['range_m'], color='r', 
                                        linestyle='--', alpha=0.5)
            self.detection_markers.append(m)
            
            # Annotation
            ann = self.ax_profile.annotate(
                f"{det['range_m']:.1f}m\n{det['snr_db']:.1f}dB",
                xy=(det['range_m'], det['power_db']),
                xytext=(det['range_m'] + 2, det['power_db'] + 5),
                fontsize=8,
                arrowprops=dict(arrowstyle='->', color='red')
            )
            self.detection_markers.append(ann)
        
        # Update RTI
        rti = self.proc.get_range_time_intensity()
        if len(rti) > 0 and self.im_rti is None:
            extent = [0, len(rti), 0, self.proc.config['max_range_m']]
            self.im_rti = self.ax_rti.imshow(
                rti.T, aspect='auto', origin='lower',
                extent=extent, cmap='viridis', vmin=-80, vmax=-20
            )
            self.ax_rti.set_xlabel("Chirp Number")
            self.ax_rti.set_ylabel("Range (m)")
            self.ax_rti.set_title("Range-Time Intensity")
            plt.colorbar(self.im_rti, ax=self.ax_rti, label="dB")
        elif self.im_rti is not None:
            self.im_rti.set_data(rti.T)
        
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()


def main():
    parser = argparse.ArgumentParser(description="FMCW Radar Processor")
    parser.add_argument("--rp-ip", default="192.168.1.100")
    parser.add_argument("--bandwidth", type=float, default=50e6)
    parser.add_argument("--chirp-ms", type=float, default=1.0)
    parser.add_argument("--max-range", type=float, default=50.0)
    parser.add_argument("--cfar-threshold", type=float, default=15.0)
    
    args = parser.parse_args()
    
    config = DEFAULT_FMCW_CONFIG.copy()
    config['bandwidth_hz'] = args.bandwidth
    config['chirp_duration_ms'] = args.chirp_ms
    config['max_range_m'] = args.max_range
    
    # Chirp period = chirp + guard
    chirp_period_ms = args.chirp_ms + 0.2
    samples_per_chirp = int(config['sample_rate_decimated'] * chirp_period_ms / 1000.0)
    
    print(f"FMCW Radar:")
    print(f"  Bandwidth: {args.bandwidth/1e6:.0f} MHz")
    print(f"  Chirp: {args.chirp_ms:.1f} ms")
    print(f"  Range resolution: {SPEED_OF_LIGHT/(2*args.bandwidth):.2f} m")
    print(f"  Max range: {args.max_range:.0f} m")
    print(f"  Samples/chirp: {samples_per_chirp}")
    
    # Connect to Red Pitaya
    rp = RedPitayaSDR(args.rp_ip)
    if not rp.connect():
        print("Connection failed")
        return
    
    try:
        rp.start_rx()
        rp.start_stream()
        
        processor = FMCWProcessor(config)
        viz = FMCWVisualizer(processor)
        
        print("Running... Press Ctrl+C to stop")
        
        while True:
            samples = rp.get_samples_n(samples_per_chirp, timeout=5.0)
            if len(samples) == 0:
                continue
            
            result = processor.process_chirp(samples)
            viz.update(result)
            
            if result['detections']:
                for det in result['detections']:
                    print(f"  🎯 Target at {det['range_m']:.1f} m | "
                          f"SNR {det['snr_db']:.1f} dB | "
                          f"fb {det['beat_freq_hz']:.0f} Hz")
    
    except KeyboardInterrupt:
        print("\nStopped")
    finally:
        rp.stop_rx()
        rp.disconnect()
        plt.ioff()
        plt.show()


if __name__ == "__main__":
    main()
```

---

## Expected Performance

| Parameter | CW Doppler | FMCW (this design) |
|-----------|-----------|-------------------|
| Range info | No | Yes, 3 m resolution |
| Speed info | Yes (Doppler) | Yes (Doppler across chirps) |
| Max range | Depends on power | 50 m (configurable) |
| Sample rate to PC | 100 kSPS | 50 kSPS (lighter) |
| FPGA load | Low (DDS only) | Medium (DDS + mult + CIC) |
| Through-wall | Walking only | Walking + approximate range |
| Target count | No | Yes, by range separation (>3 m) |

---

## Build Path

1. **Flash custom FPGA bitstream** with chirp generator + de-chirp + CIC
2. **Keep existing analog frontend** (ADF4351 LO + mixer + LNA + antennas)
3. **Run `fmcw_processor.py`** instead of `cw_doppler.py`
4. **See range profiles** in real-time

**Hardware changes from CW:**
- None on the analog side!
- Only the Red Pitaya FPGA bitstream changes
- Same BOM, same wiring, same antennas

**This is the most efficient upgrade path:** All the investment in the 2.4 GHz frontend is preserved. You just reprogram the FPGA and run different Python software.

---

## Next: Triangle Chirp for Simultaneous Range + Doppler

The current design uses **sawtooth chirp** (frequency always increasing). Doppler shifts the beat frequency, causing range error.

**Triangle chirp** (up then down) solves this:
```
Up-chirp:   fb_up = fb_range - fdoppler
Down-chirp: fb_down = fb_range + fdoppler
```

Solving the pair:
```
fb_range = (fb_up + fb_down) / 2
fdoppler = (fb_down - fb_up) / 2
```

This gives **simultaneous, unambiguous range and velocity** for each target.

Implementation: Change the FPGA chirp generator to ramp up then down. Double the chirp period. Software extracts both beat frequencies.

---

## Files Delivered

| File | Content |
|------|---------|
| This doc | Theory, parameters, performance |
| `fmcw_chirp.v` | Verilog chirp generator (quadratic phase DDS) |
| `fmcw_dechirp.v` | Digital de-chirp (complex multiplier) |
| `fmcw_bd.tcl` | Vivado block design skeleton |
| `fmcw_processor.py` | Python range profile + CFAR + visualisation |
