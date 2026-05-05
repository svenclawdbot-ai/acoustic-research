# Red Pitaya Integration for TurboQuant V5

## Overview

Connect the V5 8-channel acoustic NDE system to a **Red Pitaya STEMlab 125-14** (or 125-10) for real-time data acquisition and processing.

**Red Pitaya Specs:**
- Zynq 7010 SoC (ARM + FPGA)
- 2× ADC channels, 125 Msps, 14-bit
- 2× DAC channels, 125 Msps, 14-bit
- 1Gbps Ethernet
- FPGA programmable via Vivado/WebLab

**V5 Interface Requirements:**
- 8 piezo channels (via DG408 MUX) → 1 ADC input
- Source excitation (DAC output → power amp → source transducer)
- Trigger: software or hardware trigger for source-receiver sync

---

## 1. Hardware Interface

### Analog Front-End

```
Red Pitaya ADC0 (±1V, 50Ω) → Buffer amp → DG408 MUX output
Red Pitaya DAC0 (±1V, 50Ω) → Power amp (e.g., PA119) → Source piezo
```

**ADC path:**
- Red Pitaya ADC input: ±1V, 50Ω impedance
- V5 receiver signals: ±100mV typical (needs 10× gain)
- **Add low-noise preamp** (e.g., AD8429 or OPA637) with gain=10, BW>1MHz
- AC-couple to remove DC offset from piezo polarization

**DAC path:**
- Red Pitaya DAC output: ±1V
- Power amp gain: 10–20× to drive source piezo (needs ~10–20V for phantom)
- Bandwidth: >500kHz for 150Hz–250kHz signals
- **Pulse transformer** or **capacitive coupling** to isolate DC

### MUX Control Interface

```
Red Pitaya GPIO (E1 connector) → DG408 address pins (S0, S1, S2)
                          → DG408 inhibit (enable/disable)
```

**GPIO mapping (Red Pitaya E1 connector):**
| Pin | Function | DG408 Pin |
|-----|----------|-----------|
| DIO0_N | S0 (LSB) | Pin 11 (A0) |
| DIO0_P | S1 | Pin 10 (A1) |
| DIO1_N | S2 (MSB) | Pin 9 (A2) |
| DIO1_P | /EN (active low) | Pin 6 (EN) |

**Scanning sequence:**
1. Set S0-S2 to select channel (0–7)
2. Assert /EN low
3. Wait 1μs (MUX settling)
4. Trigger acquisition
5. De-assert /EN high
6. Move to next channel

**Total scan time:** 8 channels × (1μs settle + 10μs acquisition) = 88μs

---

## 2. FPGA Firmware

### Option A: Use Red Pitaya Base System + External Triggering

**Simplest approach:** Use Red Pitaya's default OS (STEMlab 0.98 or later) with SCPI commands.

```python
# Python acquisition loop
import redpitaya_scpi as scpi

rp = scpi.scpi("192.168.1.100")  # Red Pitaya IP

# Configure acquisition
rp.tx_txt('ACQ:DEC 64')          # 1.95 Msps (125Msps/64)
rp.tx_txt('ACQ:TRIG:LEV 0.05')   # 50mV trigger level
rp.tx_txt('ACQ:TRIG:DLY 8192')   # 8192 sample delay

for channel in range(8):
    # Set MUX address via GPIO
    set_mux_channel(channel)
    
    # Arm trigger
    rp.tx_txt('ACQ:START')
    rp.tx_txt('ACQ:TRIG NOW')
    
    # Wait for acquisition
    rp.tx_txt('ACQ:TRIG:STAT?')
    while rp.rx_txt() != 'TD':
        pass
    
    # Read data
    rp.tx_txt(f'ACQ:SOUR1:DATA?')
    data = rp.rx_txt()
    
    # Store
    waveforms[channel] = parse_data(data)
```

**Pros:** No FPGA development needed
**Cons:** ~10ms per SCPI round-trip → 80ms for 8 channels → too slow for real-time

### Option B: Custom FPGA Bitstream (Recommended)

**FPGA architecture:**
```
DAC0 → Source excitation (tone burst / chirp / Ricker)
ADC0 → 8192-sample buffer (circular, triggered)
Trigger → External or software
GPIO → MUX control state machine
AXI → DMA to ARM DDR
```

**Data flow:**
1. ARM writes excitation waveform to DAC BRAM
2. ARM triggers acquisition
3. FPGA: assert MUX channel 0, wait 1μs, trigger ADC
4. ADC captures 8192 samples @ 1.95 Msps → 4.2ms window
5. FPGA: DMA samples to DDR
6. FPGA: increment MUX channel, repeat for all 8
7. Interrupt ARM when all 8 channels done
8. Total: ~35ms for full 8-channel sweep

**FPGA modules needed:**
- `axis_red_pitaya_adc` — ADC interface (from Red Pitaya examples)
- `axis_red_pitaya_dac` — DAC interface
- `axis_trigger` — Trigger generator
- `axis_mux_controller` — GPIO state machine for MUX
- `axis_dma` — AXI DMA to DDR

**Vivado block design:**
```tcl
# Create block design
create_bd_design "v5_acquisition"

# Add Zynq PS
create_bd_cell -type ip -vlnv xilinx.com:ip:processing_system7:5.5 processing_system7_0

# Add Red Pitaya ADC
create_bd_cell -type ip -vlnv pavel-demin:user:axis_red_pitaya_adc:1.0 adc_0

# Add Red Pitaya DAC
create_bd_cell -type ip -vlnv pavel-demin:user:axis_red_pitaya_dac:1.0 dac_0

# Add AXI GPIO for MUX control
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_gpio:2.0 gpio_mux
set_property -dict [list CONFIG.C_GPIO_WIDTH {4} CONFIG.C_ALL_OUTPUTS {1}] [get_bd_cells gpio_mux]

# Add DMA
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_dma:7.1 dma_0
set_property -dict [list CONFIG.c_include_sg {0} CONFIG.c_include_mm2s {0}] [get_bd_cells dma_0]

# Add BRAM for DAC waveform
create_bd_cell -type ip -vlnv xilinx.com:ip:blk_mem_gen:8.4 bram_dac
set_property -dict [list CONFIG.Memory_Type {Single_Port_RAM}] [get_bd_cells bram_dac]
```

---

## 3. Software Stack

### Pavel Demin's Approach (Recommended)

Use Pavel's **Red Pitaya Notes** framework — pre-built FPGA images with Python API.

**Installation:**
```bash
# On Red Pitaya (SSH)
git clone https://github.com/pavel-demin/red-pitaya-notes.git
cd red-pitaya-notes
make PROJECT=v5_acquisition
```

**Python API:**
```python
import numpy as np
import v5_api  # Your custom API

# Initialize
rp = v5_api.RedPitaya("192.168.1.100")

# Configure source excitation
fs = 125e6 / 64  # 1.95 Msps after decimation
f0 = 150e3       # 150 kHz center frequency
waveform = v5_api.ricker_pulse(f0, fs, n_samples=8192)
rp.load_waveform(waveform)

# Acquire all 8 channels
waveforms = rp.acquire_channels(n_channels=8, decimation=64)
# Returns: dict {0: array(8192), 1: array(8192), ...}

# Process
import dsp
for ch, data in waveforms.items():
    # Bandpass filter
    filtered = dsp.bandpass(data, f_low=50e3, f_high=250e3, fs=fs)
    # Extract envelope
    envelope = dsp.envelope(filtered)
    # First arrival time
    t_arrival = dsp.first_arrival(envelope, threshold=0.1)
    print(f"Channel {ch}: arrival = {t_arrival*1e6:.1f} μs")
```

---

## 4. Real-Time Processing Pipeline

### Data Flow

```
[Red Pitaya FPGA] → [DMA to ARM DDR] → [Python processing] → [Parameter fitting]
     ↓                    ↓                    ↓                  ↓
  8 ch × 8192      8 ch × 8192 × 2B      Bandpass +          Zener fit
  @ 1.95 Msps      = 128 KB/frame         envelope             (MCMC)
  
  Frame rate: ~28 Hz (35ms/frame)
```

### Processing Steps (per frame)

1. **Preprocessing** (5ms)
   - Bandpass filter: 50–250 kHz
   - Remove DC offset
   - Normalize amplitude

2. **Feature extraction** (10ms)
   - Envelope detection (Hilbert transform)
   - First arrival detection
   - Cross-correlation between pairs → time delays

3. **Parameter fitting** (20ms)
   - Zener model fit to group velocity vs frequency
   - Or: FDTD-based correlation match (pre-computed library)
   - Output: G₀, G∞, τ

**Total latency:** ~35ms → **28 Hz update rate**

### Optimization for Real-Time

**Pre-computed FDTD library:**
```python
# Offline: generate library of waveforms for different (G0, Ginf, tau)
library = {}
for G0 in np.linspace(500, 5000, 20):
    for Ginf in np.linspace(1000, 10000, 20):
        for tau in np.linspace(0.001, 0.01, 10):
            # Run FDTD, extract 8-receiver waveforms
            u = simulate_8rx(G0, Ginf, tau)
            library[(G0, Ginf, tau)] = u

# Online: find best match via correlation
best_match = max(library.items(), 
                 key=lambda kv: correlation(kv[1], observed))
```

**Library size:** 20×20×10 = 4000 entries × 128KB = **512 MB**
**Query time:** ~10ms (vectorized correlation on ARM)

---

## 5. Power and Physical Integration

### Power Budget

| Component | Voltage | Current | Power |
|-----------|---------|---------|-------|
| Red Pitaya | 5V | 2A | 10W |
| V5 analog front-end | ±12V | 50mA | 1.2W |
| DG408 MUX | 5V | 10mA | 50mW |
| Preamp | ±12V | 20mA | 480mW |
| Power amp | ±24V | 200mA | 9.6W |
| **Total** | | | **~22W** |

### Enclosure Design

```
┌─────────────────────────────────────┐
│  Red Pitaya (stacked on V5 PCB)     │
│  ┌─────────┐  ┌─────────┐           │
│  │  Zynq   │  │  Analog │           │
│  │  FPGA   │  │  Front  │           │
│  └─────────┘  │  End    │           │
│               └─────────┘           │
│  ┌─────────────────────────────┐   │
│  │  V5 PCB (MUX + connectors)  │   │
│  └─────────────────────────────┘   │
│         ↓ 8 coax to phantom         │
└─────────────────────────────────────┘
```

**Connector panel:**
- BNC × 8: receiver channels
- BNC × 1: source output
- SMA × 2: Red Pitaya IO (trigger / sync)
- Power: 5V barrel jack + ±12V/±24V terminals
- Ethernet: 1Gbps to host PC

---

## 6. Testing Protocol

### Step 1: Loopback Test
1. Connect DAC0 directly to ADC0 (bypass V5)
2. Generate 150kHz tone burst
3. Verify received waveform matches transmitted

### Step 2: Single Channel Test
1. Connect 1 receiver piezo to V5 channel 0
2. Connect source piezo to power amp
3. Acquire single-shot waveform
4. Verify first arrival ~100–200μs (depending on phantom size)

### Step 3: MUX Scan Test
1. Connect 8 receivers (or resistive loads)
2. Scan all 8 channels
3. Verify channel isolation (>40dB between channels)

### Step 4: Full System Test
1. Place phantom (e.g., PDMS block with known properties)
2. Acquire 8-channel waveforms
3. Run model-based fitting
4. Compare fitted G₀ to known value

---

## 7. Next Steps

1. **Design analog front-end PCB** (preamp + power amp)
2. **Build FPGA bitstream** (or use Pavel's framework)
3. **Write Python acquisition API**
4. **Calibrate with known phantoms**
5. **Optimize processing pipeline for real-time**

**Time estimate:** 2–3 weeks for full integration

---

*Document: RED_PITAYA_INTEGRATION.md*
*Date: 2026-04-22*
