# Red Pitaya Logic Analyzer — Debug Without Extra Hardware

The Red Pitaya has a built-in logic analyzer in its standard OS. No FPGA programming needed. No extra cost.

## What It Is

A **16-channel digital oscilloscope** that captures logic levels (0/1) on the Red Pitaya's GPIO pins at up to **125 MSps**.

Compare to a cheap USB logic analyzer:
| Feature | Red Pitaya LA | Saleae Logic 8 | Cheap 8-ch LA |
|---------|--------------|----------------|---------------|
| Channels | 16 | 8 | 8 |
| Sample rate | 125 MSps | 100 MSps | 24 MSps |
| Buffer depth | Large (DDR) | 10M samples | Small |
| Protocol decode | Via software | Built-in | Limited |
| Trigger | Basic | Advanced | Basic |
| Cost | Free (included) | £400 | £10 |

**The Red Pitaya LA is better than a £400 Saleae for raw capture speed and channel count.** Protocol decoding is the only gap.

## Accessing It

### Method 1: Web Interface (Easiest)
1. Boot standard Red Pitaya OS (not Pavel's Alpine)
2. Open browser → `http://rp-f0xxxx.local/` (or IP address)
3. Click **Logic Analyzer** app
4. Select channels, set trigger, click Run

### Method 2: SCPI Commands (For Automation)
```python
import requests

rp_ip = "192.168.1.100"

# Start capture
requests.get(f"http://{rp_ip}/lajson", params={
    "command": "start",
    "channels": "0,1,2,3",  # DIO0_N to DIO3_N
    "samplerate": 125000000,
    "trigsource": "DIO0_N",
    "trigedge": "rising"
})

# Get data
r = requests.get(f"http://{rp_ip}/lajson", params={"command": "get"})
data = r.json()
```

### Method 3: Direct Memory Access (Fastest)
Use Pavel Demin's Playground bitstream for raw GPIO access via mmap.

## Pin Mapping

Red Pitaya STEMlab 125-14 **E1 Extension Connector**:

| Pin | Name | Direction | Logic Analyzer Channel |
|-----|------|-----------|----------------------|
| 1 | DIO0_N | In/Out | LA Ch 0 |
| 2 | DIO1_N | In/Out | LA Ch 1 |
| 3 | DIO2_N | In/Out | LA Ch 2 |
| 4 | DIO3_N | In/Out | LA Ch 3 |
| 5 | DIO4_N | In/Out | LA Ch 4 |
| 6 | DIO5_N | In/Out | LA Ch 5 |
| 7 | DIO6_N | In/Out | LA Ch 6 |
| 8 | DIO7_N | In/Out | LA Ch 7 |
| 9 | DIO8_N | In/Out | LA Ch 8 |
| 10 | DIO9_N | In/Out | LA Ch 9 |
| 11 | DIO10_N | In/Out | LA Ch 10 |
| 12 | DIO11_N | In/Out | LA Ch 11 |
| 13 | DIO12_N | In/Out | LA Ch 12 |
| 14 | DIO13_N | In/Out | LA Ch 13 |
| 15 | DIO14_N | In/Out | LA Ch 14 |
| 16 | DIO15_N | In/Out | LA Ch 15 |
| 17–20 | +3.3V / +5V / GND | Power | — |

**Important:**
- All DIO pins are **3.3V logic**. Connecting 5V will damage the FPGA.
- Max current per pin: ~8 mA source/sink
- Total current for all pins: ~100 mA

## Using It for Radar Debug

### Scenario 1: Debug ADF4351 SPI

**Wiring:**
```
ADF4351 LE  ──► RP DIO0_N (pin 1)  ──► LA Ch 0
ADF4351 CLK ──► RP DIO1_N (pin 2)  ──► LA Ch 1
ADF4351 DATA──► RP DIO2_N (pin 3)  ──► LA Ch 2
ADF4351 MUX ──► RP DIO3_N (pin 4)  ──► LA Ch 3 (lock detect output)
GND         ──► RP GND
```

**What to look for:**
1. **LE (latch enable):** Should pulse low for each 32-bit register write
2. **CLK:** Should toggle 32 times per register (SPI mode 0: data on falling edge)
3. **DATA:** Should show the 32-bit register value serially
4. **MUX:** Should go high when PLL locks (tune to 2.4 GHz and verify)

**Capture settings:**
- Sample rate: 1–10 MSps (SPI is slow, 1 MHz max)
- Trigger: Falling edge on DIO0_N (LE going low)
- Channels: 0, 1, 2, 3

**Expected waveform:**
```
LE:   ─────┐    ┌────────────────────┐    ┌────
           └────┘ 32 CLK cycles        └────┘

CLK:  ──────────┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌───────────
                └─┘ └─┘ └─┘ └─┘ └─┘

DATA: ──────────X─X─X─X─X─X─X─X─X────────────
                (32 data bits)

MUX:  ────────────────────────────┐    ┌─────
                                  └────┘ (lock)
```

### Scenario 2: Verify Servo PWM Timing

**Wiring:**
```
Servo signal (pan) ──► RP DIO0_N ──► LA Ch 0
Servo signal (tilt)──► RP DIO1_N ──► LA Ch 1
```

**What to look for:**
- 50 Hz PWM period (20 ms)
- Pulse width: 0.5–2.5 ms
- Check for jitter (pulse width should be stable ±10 µs)

**Capture settings:**
- Sample rate: 1 MSps
- Trigger: Rising edge on DIO0_N
- Duration: 100 ms (5 PWM periods)

### Scenario 3: Debug AXI GPIO Timing

If you're using AXI GPIO for MUX control in TurboQuant:
```
DG408 S0 ──► RP DIO0_N ──► LA Ch 0
DG408 S1 ──► RP DIO1_N ──► LA Ch 1
DG408 S2 ──► RP DIO2_N ──► LA Ch 2
DG408 /EN──► RP DIO3_N ──► LA Ch 3
```

Verify channel switching timing:
- How long between setting GPIO and MUX output changing?
- Is there glitching during transitions?
- Are all 8 channels correctly decoded?

### Scenario 4: Trigger Synchronisation

For FMCW radar, verify timing relationships:
```
Chirp start sync ──► RP DIO0_N ──► LA Ch 0
ADC sample trigger──► RP DIO1_N ──► LA Ch 1
DAC output valid ──► RP DIO2_N ──► LA Ch 2
```

Measure:
- Delay from chirp start to first ADC sample
- Jitter in sync pulse
- DAC settling time before valid output

## Protocol Decoding

The web interface shows raw waveforms. For SPI/I2C/UART decoding, export the data and process in Python:

```python
import numpy as np
import matplotlib.pyplot as plt

def decode_spi(clock, data, cpol=0, cpha=0):
    """
    Decode SPI from logic analyzer samples.
    clock, data: arrays of 0/1 values
    cpol, cpha: SPI mode (ADF4351 uses mode 0: CPOL=0, CPHA=0)
    """
    # Find clock edges
    if cpol == 0:
        # Data valid on rising edge
        edges = np.where(np.diff(clock) > 0)[0]
    else:
        edges = np.where(np.diff(clock) < 0)[0]
    
    # Sample data at edges
    bits = data[edges]
    
    # Group into bytes
    bytes_out = []
    for i in range(0, len(bits) - 7, 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | bits[i + j]
        bytes_out.append(byte)
    
    return bytes_out

def decode_adf4351_registers(bytes_stream):
    """
    ADF4351 registers are 32 bits each.
    First 3 bits = register address.
    """
    registers = []
    for i in range(0, len(bytes_stream) - 3, 4):
        reg = (bytes_stream[i] << 24) | (bytes_stream[i+1] << 16) | \
              (bytes_stream[i+2] << 8) | bytes_stream[i+3]
        reg_addr = reg & 0x7
        registers.append((reg_addr, reg))
    return registers

# Usage:
# la_data = load_from_red_pitaya_logic_analyzer()
# clock = la_data[:, 1]  # DIO1_N
# data = la_data[:, 2]   # DIO2_N
# bytes_stream = decode_spi(clock, data)
# regs = decode_adf4351_registers(bytes_stream)
# for addr, val in regs:
#     print(f"R{addr}: 0x{val:08X}")
```

## Advanced: Triggered Capture from Python

```python
import requests
import time

def capture_spi_transaction(rp_ip, duration_ms=10):
    """
    Capture a single SPI transaction with trigger.
    """
    # Configure LA
    config = {
        "command": "start",
        "channels": "0,1,2",      # LE, CLK, DATA
        "samplerate": 10000000,    # 10 MSps
        "size": 100000,            # 10k samples = 1 ms at 10 MSps
        "trigsource": "DIO0_N",    # Trigger on LE
        "trigedge": "falling",
        "triglevel": 1.5           # 1.5V threshold
    }
    
    # Start armed capture
    requests.get(f"http://{rp_ip}/lajson", params=config)
    
    # Wait for trigger
    time.sleep(0.1)
    
    # Poll for completion
    for _ in range(50):  # 5 second timeout
        r = requests.get(f"http://{rp_ip}/lajson", params={"command": "status"})
        if r.json().get("status") == "done":
            break
        time.sleep(0.1)
    
    # Get data
    r = requests.get(f"http://{rp_ip}/lajson", params={"command": "get"})
    data = r.json()
    
    return np.array(data["samples"])
```

## Comparison with External Logic Analyser

| Task | Red Pitaya LA | £10 USB LA | Saleae Logic 8 |
|------|--------------|-----------|---------------|
| ADF4351 SPI debug | ✅ Easy | ✅ Easy | ✅ Easy |
| Servo PWM verify | ✅ Easy | ✅ Easy | ✅ Easy |
| 8-channel MUX decode | ✅ Perfect | ⚠️ 8 ch max | ✅ Easy |
| 16-channel parallel bus | ✅ Perfect | ❌ No | ❌ 8 ch max |
| Protocol decode (auto) | ❌ Manual | ⚠️ Limited | ✅ Excellent |
| Export to CSV/VCD | ✅ Yes | ✅ Yes | ✅ Yes |
| Trigger on pattern | ⚠️ Basic | ⚠️ Basic | ✅ Advanced |
| Mixed analog/digital | ✅ Built-in | ❌ No | ✅ Analog too |

**The Red Pitaya LA wins for:**
- High channel count (16 vs 8)
- High sample rate (125 MSps)
- Mixed-signal (check analog and digital simultaneously)
- No extra hardware/cost

**External LA wins for:**
- Automatic protocol decoding (SPI, I2C, UART, CAN)
- Better triggering
- Portable (no network needed)

## Practical Workflow

### For Radar Build

**Step 1: Verify ADF4351 SPI before connecting RF**
1. Wire ADF4351 to RP DIO pins
2. Flash standard RP OS
3. Open Logic Analyzer web app
4. Set trigger on DIO0_N falling edge
5. Run your SPI setup code
6. Verify 32 clock cycles per register
7. Verify data bits match expected register values
8. Check MUX pin goes high (PLL lock)

**Step 2: Verify servo PWM**
1. Wire servo signal to DIO0_N
2. Set trigger on rising edge
3. Run `polar_scanner.py --mock-radar`
4. Verify 50 Hz period, 0.5–2.5 ms pulse
5. Check for jitter or missing pulses

**Step 3: Debug TurboQuant MUX**
1. Wire DG408 control lines to DIO pins
2. Trigger on channel change
3. Verify correct channel select timing
4. Check for glitches during transitions

## Files Delivered

| File | Content |
|------|---------|
| This doc | Complete LA guide |
| `la_spi_decoder.py` | SPI decode from LA samples |
| `la_triggered_capture.py` | Python triggered capture script |

## Summary

The Red Pitaya Logic Analyzer is:
- **Free** (included in standard OS)
- **Fast** (125 MSps, 16 channels)
- **Immediate** (no extra hardware, no programming)
- **Sufficient** for 90% of digital debug tasks

Use it to:
1. Verify ADF4351 SPI before powering RF
2. Debug servo timing without an oscilloscope
3. Check TurboQuant MUX switching
4. Validate FMCW sync pulses

For automatic protocol decoding, export the CSV and run the Python decoder, or buy a £10 USB LA as a secondary tool.
