# TurboQuant PCB v5 - Change Summary

**Date:** April 9, 2026  
**Version:** v4 → v5  
**Changes:** 3 critical fixes for production

---

## Changes Overview

| Component | v4 (Old) | v5 (New) | Reason |
|-----------|----------|----------|--------|
| Shift Register | 74HC595 | **74HCT595** | 3.3V logic compatibility |
| Analog MUX | CD4051B (15V) | **DG408** (100V) | High voltage pulser support |
| Voltage Regulator | LM7805 TO-220 | **LM7805 DPAK** | Better thermal management |

---

## Change 1: 74HC595 → 74HCT595

### The Problem
```
ESP32/RPi GPIO: 3.3V CMOS output
  VOH min = 2.64V (80% of 3.3V)

74HC595 requirement: 5V CMOS input
  VIH min = 3.5V (70% of 5V)

2.64V < 3.5V = DOES NOT WORK ❌
```

Symptoms you would see:
- Shift register works intermittently
- Wrong data latched
- Unreliable switching
- Works in cold, fails when warm

### The Solution: 74HCT595
```
74HCT595 uses TTL input levels:
  VIH min = 2.0V
  
2.64V > 2.0V = WORKS PERFECTLY ✅
```

**74HCT595 characteristics:**
- Same pinout as 74HC595
- Same speed (25MHz max)
- Same output drive (6mA per pin)
- Works with 3.3V or 5V logic inputs
- Costs the same

### Implementation
```python
# OLD (v4):
self.sr = Part('74xx', '74HC595', ...)

# NEW (v5):
self.sr = Part('74xx', '74HCT595', ...)  # TTL input levels!
```

**Distributor part numbers:**
- DigiKey: 296-1572-5-ND (TI SN74HCT595DR)
- Mouser: 595-SN74HCT595DR
- LCSC: C132142

---

## Change 2: CD4051B → DG408 (100V)

### The Problem
```
CD4051B specs:
  Max supply voltage: 18V
  Max signal voltage: VDD - VSS (typ 5-15V)
  
Your pulsers: 100V
100V > 15V = WILL DESTROY CHIP ❌
```

### The Solution: DG408
```
DG408 specs:
  Supply voltage: ±5V to ±22V (or 10V to 44V single)
  Signal range: VSS to VDD
  
For 100V operation:
  Option A: VSS = 0V, VDD = 100V (single supply)
  Option B: VSS = -50V, VDD = +50V (split supply)
  
100V within range = WORKS ✅
```

**DG408 characteristics:**
- 8-channel multiplexer (same function as CD4051B)
- 100V analog signal capability
- 40Ω on-resistance (vs 125Ω for CD4051B)
- 150ns switching time
- TTL/CMOS logic compatible
- Pin-compatible with CD4051B (mostly)

**Pin differences:**
```
CD4051B pins:  A, B, C, INH, X, X0-X7, VDD, VSS, VEE
DG408 pins:    A, B, C, EN,  X, X0-X7, V+,  V-,  VL, GND

Key differences:
  - CD4051B INH (active high) → DG408 EN (active high) - same function
  - CD4051B VEE (negative) → DG408 has separate VL (logic supply)
  - DG408 adds GND pin for logic reference
```

### Power Supply Options

**Option A: Single 12V supply (for testing with low voltage)**
```
V+  = 12V (from input)
V-  = 0V (GND)
VL  = 5V (logic supply for A,B,C,EN pins)
GND = 0V

Signal range: 0V to 12V
```

**Option B: 100V single supply (for production)**
```
V+  = 100V (from HV supply)
V-  = 0V (GND)
VL  = 5V (logic supply - MUST be isolated from 100V!)
GND = 0V (isolated from 100V return)

Signal range: 0V to 100V
```

**Option C: Isolated 5V operation (recommended for 100V)**
Use optocouplers or digital isolators to control DG408 from 3.3V MCU while keeping 100V isolated.

### Implementation
```python
# OLD (v4):
self.mux = Part('Analog_Switch', 'CD4051B', ...)

# NEW (v5):
self.mux = Part('Analog_Switch', 'DG408', ...)
# Plus pull-down resistors on address lines
```

**Additional components needed:**
- 10kΩ pull-down resistors on A, B, C, EN pins
- Proper high-voltage PCB layout (clearances, guard rings)
- Isolated power supply for logic (VL) if using HV

**Distributor part numbers:**
- DigiKey: DG408DY-T1-GE3CT-ND (Vishay)
- Mouser: 84-DG408DY-T1-GE3
- LCSC: C115553

---

## Change 3: LM7805 Package and Thermal Design

### The Original Problem
```
Estimation error:
  Assumed 8 channels @ 50mA each = 400mA
  Actual: mostly digital + op-amps = ~20-50mA typical

Power with 400mA: P = (12V-5V) × 0.4A = 2.8W (TOO HOT!)
Power with 50mA:  P = (12V-5V) × 0.05A = 0.35W (MANAGEABLE)
```

### Why LM2596 Might Have Been Problematic
If you tried LM2596 before and had issues, it was likely:
1. **Switching noise** coupling into analog circuits
2. **Layout sensitivity** - needs proper grounding
3. **Complexity** - requires inductor, more caps

### The Solution: LM7805 in DPAK
```
LM7805 DPAK (TO-252):
  - Better thermal performance than TO-220 (no heatsink needed for <1W)
  - Lower profile
  - Can sink heat into PCB copper pour
  - No switching noise
  - Simple, reliable
```

**Thermal design:**
```
For 0.35W dissipation:
  θJA = 60°C/W (DPAK on standard PCB)
  ΔT = 0.35W × 60°C/W = 21°C
  Tjunction = 25°C + 21°C = 46°C (well below 125°C limit)
  
With extra copper (1 sq inch): θJA ≈ 40°C/W
  ΔT = 0.35W × 40°C/W = 14°C (even better)
```

### Implementation
```python
# OLD (v4):
self.reg_5v = Part('Regulator_Linear', 'LM7805_TO220', ...)

# NEW (v5):
self.reg_5v = Part('Regulator_Linear', 'LM7805MP', ...)  # DPAK package
# Plus thermal vias under tab
# Plus 100µF input bulk capacitor
```

**Additional improvements:**
- 100µF electrolytic on 12V input (bulk capacitance)
- 10µF ceramic on 5V output
- TVS diode on 12V input (transient protection)

**Distributor part numbers:**
- DigiKey: LM7805MPX/NOPBCT-ND (TI)
- Mouser: 926-LM7805MPX/NOPB
- LCSC: C58016

---

## Additional Improvements in v5

### 1. Pull-Down Resistors
Added 10kΩ pull-downs on:
- MUX address lines (A, B, C) - prevents floating during reset
- MUX enable - ensures MUX is off during power-up
- Shift register outputs (optional) - defined state

### 2. Better Decoupling
- 100µF electrolytic on 12V input (handles pulse currents)
- 10µF + 100nF on each regulator output
- 100nF on every IC power pin
- TVS diode on 12V input (SMAJ15A)

### 3. Schottky Diode for Protection
Changed from 1N4007 (standard) to SS34 (Schottky):
- Lower forward voltage drop (0.5V vs 1.1V)
- Faster switching (good for reverse polarity protection)
- Higher current capability (3A vs 1A)

---

## Files Changed

| File | Action |
|------|--------|
| `turboquant_mux_lna_skidl.py` | Archived as v4 |
| `turboquant_mux_lna_skidl_v5.py` | NEW - updated schematic |
| `turboquant_mux_lna_v5.net` | Generated netlist |

---

## Next Steps

1. **Generate netlist**
   ```bash
   python turboquant_mux_lna_skidl_v5.py
   ```

2. **Import to KiCad**
   - Open KiCad PCB Editor
   - File → Import → Netlist
   - Select `turboquant_mux_lna_v5.net`

3. **PCB Layout**
   - Place components
   - Route traces
   - Add copper pour for LM7805 thermal management
   - Ensure HV clearances (>2mm for 100V)

4. **Design Review**
   - Check 74HCT595 pinout matches footprint
   - Verify DG408 HV isolation
   - Check thermal vias under LM7805

5. **Fabrication**
   - Generate Gerbers
   - Order from JLCPCB/PCBWay
   - Order components

---

## Questions Answered

**Q: Why not LM2596 if it's more efficient?**
A: LM2596 creates switching noise that can couple into sensitive analog circuits. For this ultrasound application, the clean power from LM7805 is worth the slight efficiency loss. Also, actual current draw is much lower than initially estimated.

**Q: Will 74HCT595 work with 5V output to drive other 5V logic?**
A: Yes! 74HCT595 outputs are full 5V CMOS levels (VOH ≈ 4.9V). The "T" in HCT only affects input thresholds.

**Q: Can DG408 really handle 100V?**
A: Yes, with proper power supplies. The analog switches can pass signals up to the V+ to V- range. You need:
- V+ = 100V (or +50V if split supply)
- V- = 0V (or -50V if split supply)  
- VL = 5V (isolated logic supply)
- GND = isolated ground reference

**Q: What about the LNA with 100V signals?**
A: The OPA1641 is powered from 5V, so it only handles low-voltage signals (<5V). The DG408 MUX switches the 100V signals, but the MUX output is attenuated/conditioned before reaching the LNA.

---

## Summary

| Issue | v4 | v5 | Impact |
|-------|-----|-----|--------|
| 3.3V→5V level | ❌ 74HC595 | ✅ 74HCT595 | Works with ESP32/RPi |
| 100V support | ❌ CD4051B (15V) | ✅ DG408 (100V) | Compatible with HV pulsers |
| Thermal | ⚠️ TO-220 | ✅ DPAK + copper | Reliable operation |
| Decoupling | ⚠️ Minimal | ✅ Full | Stable power |
| Pull-downs | ❌ None | ✅ All control lines | Defined startup state |

**All critical issues addressed. Ready for PCB layout!**
