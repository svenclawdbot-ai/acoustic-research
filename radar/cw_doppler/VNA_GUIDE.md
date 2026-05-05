# Red Pitaya VNA — Vector Network Analyzer for Antenna Tuning

Flash a different SD card image → your Red Pitaya becomes a £2,000 instrument.

## What is a VNA?

A Vector Network Analyzer measures how signals pass through or reflect from a device under test (DUT). It gives you **amplitude and phase** information, not just scalar power.

**Two key measurements:**
- **S11 (return loss / reflection coefficient):** How much power bounces back from the DUT. Critical for antenna tuning.
- **S21 (transmission / insertion loss):** How much power passes through the DUT. Used for filters, amplifiers, cables.

## Why You Need It for Radar

Your 2.4 GHz patch antennas must be resonant at exactly 2.400 GHz. If they're off by even 50 MHz, your radar loses 3–6 dB of power — that's half your range gone.

**Without a VNA:** You guess. You buy antennas and hope.  
**With a VNA:** You measure S11, see the dip at resonance, verify it's at 2.4 GHz.

## Pavel Demin's VNA

| Spec | Value |
|------|-------|
| Frequency range | 1–60 MHz (with baseband I/O) |
| With external mixer/upconverter | Extends to GHz |
| Output power | 0 dBm typical |
| Dynamic range | ~80 dB |
| Measurement type | S11 (reflection) + S21 (transmission) |
| Control | Python client via TCP |
| Cost | Free (SD card image + Python) |

**Architecture:**
```
Red Pitaya OUT1 ──► Directional Coupler / Bridge ──► DUT (antenna)
                         │
                         └── Reflected signal ──► Red Pitaya IN1

Red Pitaya OUT2 ──► DUT input ──► DUT output ──► Red Pitaya IN2 (for S21)
```

The FPGA generates a swept frequency tone. The reflected signal is compared to the reference. Phase and magnitude are extracted via I/Q mixing.

## Using VNA for 2.4 GHz Antennas

The base VNA covers 1–60 MHz. For 2.4 GHz, you need an **external mixer/upconverter** or use the VNA in an IF configuration.

### Option A: Direct IF Measurement (Simplest)

Use your existing radar frontend in reverse:
```
ADF4351 @ 2.4 GHz ──► LO port of LT5560
Red Pitaya OUT1 ──► IF input to LT5560 (sweep 0–50 MHz)
LT5560 RF port ──► Antenna under test
Reflected signal ──► back into RF port ──► downconverted to IF ──► Red Pitaya IN1
```

The LT5560 acts as both upconverter and downconverter. Red Pitaya sweeps the IF frequency, and the antenna sees a swept RF signal centred on 2.4 GHz.

**This uses the same hardware you're already building for the radar!**

### Option B: External Reflection Bridge (More Accurate)

Build or buy a directional bridge:
```
Red Pitaya OUT1 ──► Directional Coupler ──► Antenna
                         │
                         └── Coupled port ──► Red Pitaya IN1
```

The coupler separates forward and reflected waves. At 2.4 GHz, a simple resistive bridge or a commercial 2.4 GHz directional coupler works.

**Commercial option:** Mini-Circuits ZFDC-10-5-S+ (~£30) covers 2.4 GHz.

**DIY option:** Three-bead balun bridge (see Pavel's links) — costs pennies in ferrite beads and resistors.

### Option C: Use Standard VNA for Antenna Design

If your antenna is a simple PCB patch, design it at 2.4 GHz using the VNA in a lower-frequency test:

1. Build a **scaled test antenna** at 60 MHz (40× larger dimensions)
2. Measure S11 with the VNA directly
3. Verify the design methodology
4. Scale down to 2.4 GHz for the real build

This is how professional antenna engineers validate designs before fabrication.

## What You'll See

### Good Antenna (Tuned to 2.4 GHz)
```
S11 (dB)
   0 ┤                                    
     │         ╭──╮                      
 -10 ┤        ╱    ╲                     
     │       ╱      ╲                    
 -20 ┤──────╱        ╲────────────────  
     │     ╱          ╲                
 -30 ┤    ╱            ╲               
     │   ╱              ╲              
 -40 ┤──╱                ╲──────────── 
     └────┬────┬────┬────┬────┬────┬────
         2.35  2.38  2.40  2.42  2.45
              Frequency (GHz)

Deep dip at 2.40 GHz = resonance
S11 < -10 dB = 90% power radiated (10% reflected)
S11 < -20 dB = 99% power radiated
```

### Bad Antenna (Detuned)
```
S11 (dB)
   0 ┤                                    
     │                                    
 -10 ┤         ╭──╮                      
     │        ╱    ╲                     
 -20 ┤───────╱      ╲───────────────────  
     │      ╱        ╲                 
 -30 ┤     ╱          ╲                
     │    ╱            ╲               
 -40 ┤───╱              ╲───────────── 
     └────┬────┬────┬────┬────┬────┬────
         2.35  2.38  2.40  2.42  2.45
              Frequency (GHz)

Dip at 2.38 GHz = antenna is 20 MHz low
Need to trim patch or adjust substrate
```

## Measuring Your Radar Frontend

### Step 1: LNA Characterisation (S21)
```
Red Pitaya OUT1 ──► LNA input ──► LNA output ──► Red Pitaya IN2
```
- Verify gain at 2.4 GHz (should be +20 dB)
- Check for oscillation (spurious peaks)
- Measure noise figure (roughly, with known source)

### Step 2: Mixer Conversion Loss (S21)
```
Red Pitaya OUT1 ──► IF port of LT5560
ADF4351 ──► LO port
RF port ──► Red Pitaya IN2
```
- Measure IF-to-RF conversion gain/loss
- Verify at multiple LO frequencies

### Step 3: Filter Response (S21)
```
Red Pitaya OUT1 ──► Filter ──► Red Pitaya IN2
```
- Characterise any BPF or LPF in your chain
- Verify cutoff frequency and passband ripple

### Step 4: Antenna S11
```
Red Pitaya OUT1 ──► Directional Coupler ──► Antenna
                         │
                         └── Red Pitaya IN1
```
- Find resonance frequency
- Measure bandwidth (-10 dB points)
- Calculate VSWR: VSWR = (1+|Γ|)/(1-|Γ|) where Γ = 10^(S11/20)

## VNA Python Client

Pavel Demin's `vna.py` connects via TCP and sweeps frequencies:

```python
# vna_client.py — Simplified interface to Pavel's VNA

import numpy as np
import socket

class RedPitayaVNA:
    def __init__(self, ip="192.168.1.100", port=1001):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, port))
    
    def set_freq_range(self, start_hz, stop_hz, n_points=1000):
        """Set sweep parameters."""
        cmd = f"FREQ {start_hz} {stop_hz} {n_points}\n"
        self.sock.sendall(cmd.encode())
    
    def measure_s11(self):
        """Return (freqs, s11_db, s11_phase)."""
        self.sock.sendall(b"MEAS S11\n")
        # Parse response...
        # Returns complex S11 values
        pass
    
    def measure_s21(self):
        """Return (freqs, s21_db, s21_phase)."""
        self.sock.sendall(b"MEAS S21\n")
        pass
    
    def plot_smith(self, s11_complex):
        """Plot on Smith chart."""
        import matplotlib.pyplot as plt
        # Smith chart plotting code
        pass
```

## Practical Workflow

### Day 1: Flash VNA Image
1. Download `red-pitaya-alpine-*-vna.zip` from Pavel's releases
2. Flash to SD card with BalenaEtcher
3. Boot Red Pitaya
4. Run `vna.py` on your PC
5. Verify basic operation with a 50Ω load (S11 should be flat near 0 dB)

### Day 2: Characterise Radar Components
1. Measure your 2.4 GHz patch antennas
2. If resonance is off, trim patch or adjust feed point
3. Measure LNA gain
4. Document everything in your lab notebook

### Day 3: Iterate Antenna Design
1. If S11 at 2.4 GHz is poor (< -6 dB), redesign
2. Common fixes:
   - Patch too long → resonance low → trim edges
   - Patch too short → resonance high → add copper tape
   - Feed position wrong → impedance mismatch → move probe
   - Substrate εr wrong → recalculate dimensions

## Smith Chart Quick Reference

The VNA can display S11 on a Smith chart — a powerful tool for impedance matching.

| Smith Chart Position | Meaning | Action |
|---------------------|---------|--------|
| Centre (1+0j) | Perfect 50Ω match | Ideal |
| Right edge | Open circuit | Add shunt inductor |
| Left edge | Short circuit | Add series inductor |
| Top half | Inductive | Add shunt capacitor |
| Bottom half | Capacitive | Add shunt inductor |
| Edge of circle | High VSWR | Match with network |

For a patch antenna at resonance:
- Should be near centre of Smith chart
- Small loop around resonance frequency
- VSWR circle < 2:1 (return loss < -9.5 dB)

## What You Need to Add to Your BOM

| Item | Cost | Purpose |
|------|------|---------|
| Directional coupler 2.4 GHz | £5–30 | Separate forward/reflected |
| 50Ω termination (SMA) | £2 | Calibration load |
| Open/Short/Load cal kit | £10–50 | Full VNA calibration |
| Extra SD cards (×2) | £10 | VNA image + radar image + ultrasound image |

**Total VNA add-on: ~£20–50**

Without the coupler, you can still use the LT5560 in loopback mode as described above.

## Comparison: Red Pitaya VNA vs Commercial

| Feature | RP VNA | NanoVNA (~£50) | Rigol DSA815 (£1,000) | Keysight FieldFox (£8,000) |
|---------|--------|---------------|----------------------|---------------------------|
| Frequency | 1–60 MHz base | 50 kHz–900 MHz | 9 kHz–1.5 GHz | 4–6 GHz |
| With ext. mixer | To GHz | N/A | N/A | N/A |
| S11/S21 | Yes | Yes | Yes | Yes |
| Smith chart | Yes | Yes | Yes | Yes |
| Calibration | Basic | Basic | Full 2-port | Full 2-port |
| Dynamic range | ~80 dB | ~70 dB | >100 dB | >120 dB |
| Cost | Free + RP | £50 | £1,000 | £8,000 |

**For antenna tuning at 2.4 GHz:** The Red Pitaya VNA + external mixer beats the NanoVNA (which tops out at 900 MHz). It's not as good as a FieldFox, but it's £7,750 cheaper.

## Next Steps

1. **Download VNA image** and flash SD card
2. **Test with known load** (50Ω SMA terminator)
3. **Measure your antennas** before installing on the radar
4. **Iterate antenna design** until S11 < -10 dB at 2.4 GHz
5. **Characterise LNA and mixer** for documentation
6. **Switch back to radar SD card** and build with confidence

The VNA is the difference between "I hope this works" and "I know this works."
