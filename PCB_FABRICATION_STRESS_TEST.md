# PCB Fabrication Stress Test — Red Pitaya Mux Board
## Pre-Fabrication Design Validation

**Date:** 2026-04-08  
**Design Version:** Rev 2.1  
**Status:** 🔴 PENDING CRITICAL REVIEWS

---

## Executive Summary

Working backwards from Red Pitaya specifications to validate the mux board design is fabrication-ready.

| Category | Status | Critical Issues |
|----------|--------|-----------------|
| Red Pitaya Interface | ⚠️ | DRIVE STRENGTH, VOLTAGE LEVELS |
| Power Architecture | ✅ | Thermals verified |
| Signal Integrity | ⚠️ | IMPEDANCE, SKEW, ISOLATION |
| Component Selection | ⚠️ | FOOTPRINTS, AVAILABILITY |
| Manufacturing | ⚠️ | GERBER, DRC, PANELIZATION |

---

## 1. Red Pitaya Interface Validation (CRITICAL)

### 1.1 GPIO Drive Strength Analysis

**Red Pitaya STEMlab 125-14 GPIO Specs:**
- Voltage: 3.3V logic (E1/E2 connectors)
- Drive strength: 4-8 mA per pin (Zynq 7010)
- Max toggle rate: ~50 MHz (limited by Linux GPIO driver)

**Your Design Load:**

| Signal | Destination | Load | Issue |
|--------|-------------|------|-------|
| DIO0_P (SER) | 74HC595 pin 14 | CMOS input ~1µA | ✅ OK |
| DIO0_N (SRCLK) | 74HC595 pin 11 | CMOS input ~1µA | ✅ OK |
| DIO1_P (RCLK) | 74HC595 pin 12 | CMOS input ~1µA | ✅ OK |
| DIO1_N (MUX_A) | CD4051 pin 11 ×2 | CMOS ×2 = ~2µA | ✅ OK |
| DIO2_P (MUX_B) | CD4051 pin 10 ×2 | CMOS ×2 = ~2µA | ✅ OK |
| DIO2_N (MUX_C) | CD4051 pin 9 ×2 | CMOS ×2 = ~2µA | ✅ OK |

**Verdict:** ✅ GPIO loading is negligible. No buffer required.

### 1.2 Voltage Level Compatibility

**Potential Issue:** 74HC595 is 5V logic, Red Pitaya outputs 3.3V

**Analysis:**
- 74HC595 VIH(min) = 3.5V (at VCC=5V) — **EXCEEDS 3.3V INPUT!**
- This is a **CRITICAL DESIGN FLAW**

**Solutions:**
1. **Option A:** Power 74HC595 from 3.3V (becomes 74HC595 @ 3.3V, timing slower but OK)
2. **Option B:** Use 74HCT595 (TTL input levels, VIH=2V)
3. **Option C:** Add level shifter (TXB0108) — unnecessary complexity

**RECOMMENDATION:** Switch to **74HCT595** or power from 3.3V rail.

### 1.3 DAC Output Drive (TX Path)

**Red Pitaya DAC Specs:**
- Output: ±1V (low gain) or ±2V (high gain, Gen 2)
- Output impedance: 50Ω
- Max current: ~20 mA

**Your TX Path:**
```
DAC → 50Ω (internal) → SMA → 100Ω (series) → MOSFET → Element
```

**Voltage Divider Effect:**
- Total series R = 50Ω + 100Ω = 150Ω
- Element impedance (piezo): ~10-100Ω (frequency dependent)
- Actual voltage at element: reduced

**Expected Element Voltage:**
```
V_element = V_dac × (Z_element / (150Ω + Z_element))
For Z = 50Ω: V = 1V × (50/200) = 0.25V (too low!)
```

**VERDICT:** ⚠️ TX voltage may be insufficient for excitation.

**Solutions:**
1. Remove 100Ω series resistors (rely on 50Ω source only)
2. Add TX amplifier (LT6230, +20 dB)
3. Use external pulser (Rev 2)

**RECOMMENDATION:** For Rev 1, **remove series 100Ω resistors** on TX path.

---

## 2. RX Path Signal Chain Analysis

### 2.1 T/R Protection Diode Check

**BAV99 Specs:**
- Forward voltage: 0.7-1V
- Reverse breakdown: 75V (sufficient for low-voltage TX)
- Junction capacitance: 1.5 pF @ 0V

**Receive Signal Loss:**
- Expected echo amplitude: 1-100 mV
- Diode forward drop: 0.7V
- **Problem:** Diodes won't conduct on receive (good), but add 1.5pF shunt C

**Capacitive Loading:**
- 1.5 pF @ 5 MHz = 21 kΩ reactance
- Parallel with element (low Z) — negligible effect
- Parallel with mux input (~10 pF) — adds 15% capacitance

**Verdict:** ✅ BAV99 suitable for Rev 1.

### 2.2 CD4051B Analog MUX Analysis

**Critical Specs:**
- On-resistance (Ron): 125Ω @ 5V, 25°C
- Ron variation with signal: ±10Ω (0-5V)
- Channel isolation: -60 dB @ 1 MHz, -40 dB @ 10 MHz
- Crosstalk: -60 dB @ 1 MHz
- -3dB bandwidth: 40 MHz (typical)

**Noise Contribution:**
- 125Ω thermal noise: 1.4 nV/√Hz
- At 5 MHz BW: Vn = 1.4nV × √(5M) = 3.1 µV RMS
- Compared to echo (1 mV): 50 dB SNR contribution

**Verdict:** ✅ CD4051B adequate for 5 MHz ultrasound.

### 2.3 OPA657 LNA Design Check

**Circuit:** Non-inverting, Gain = 11 (20.8 dB)

**OPA657 Specs:**
- Gain bandwidth: 1.6 GHz
- Slew rate: 700 V/µs
- Input noise: 4.8 nV/√Hz
- Input bias current: 2 µA

**Gain Bandwidth Check:**
```
BW = GBW / Gain = 1600 MHz / 11 = 145 MHz
Target: 5-10 MHz ultrasound
Margin: 14× — EXCELLENT
```

**Slew Rate Check:**
```
Max output @ 5 MHz, 1V pk: SR_required = 2π × 5M × 1 = 31 V/µs
OPA657 SR: 700 V/µs
Margin: 22× — EXCELLENT
```

**Stability Check:**
- Feedback resistor: 1kΩ
- Gain resistor: 100Ω
- Parasitic capacitance at inverting input could cause peaking
- **Recommendation:** Add 10-22 pF feedback capacitor in parallel with 1kΩ

**Verdict:** ✅ OPA657 excellent choice, add feedback capacitor for stability.

### 2.4 RX Output Drive (To Red Pitaya ADC)

**Red Pitaya ADC Specs:**
- Input: ±1V or ±20V (selectable)
- Input impedance: High (MΩ range)
- Connector: 50Ω SMA

**OPA657 Output:**
- Can drive 50Ω load directly (short-circuit current 90 mA)
- But output will be current-limited

**For 50Ω load:**
```
Max output swing into 50Ω: I_max × R_load = 0.09 × 50 = 4.5V
Target output: ±1V into 50Ω requires 20 mA — OK
```

**Verdict:** ✅ Can drive 50Ω directly.

---

## 3. Power Supply Architecture Review

### 3.1 Power Tree

```
12V IN → LM7805 (5V) → AMS1117-3.3 (3.3V)
            │
            └──► 74HC595, CD4051B, OPA657
```

### 3.2 Current Budget

| Component | Quantity | Current Each | Total |
|-----------|----------|--------------|-------|
| 74HC595 | 1 | 6 mA | 6 mA |
| CD4051B | 2 | 2 mA | 4 mA |
| OPA657 | 2 | 16 mA | 32 mA |
| BSS138 (gate) | 8 | 0.1 mA | 0.8 mA |
| LEDs | 2 | 2 mA | 4 mA |
| **TOTAL** | | | **~47 mA** |

### 3.3 Thermal Analysis

**LM7805:**
```
Vin = 12V, Vout = 5V, Iout = 50 mA
P_diss = (12-5) × 0.05 = 0.35W
Thermal resistance (SOT-223): 60°C/W
Temperature rise: 0.35 × 60 = 21°C
Ambient 25°C → Junction 46°C — SAFE
```

**AMS1117-3.3:**
```
Vin = 5V, Vout = 3.3V, Iout = 10 mA
P_diss = (5-3.3) × 0.01 = 0.017W (negligible)
```

**Verdict:** ✅ Power supply adequate, no heatsink needed.

### 3.4 Decoupling Strategy

**Current Decoupling:**
- 100nF on each IC VCC pin — GOOD
- 10µF bulk on regulator outputs — GOOD

**Missing:**
- No 10µF on Red Pitaya 3.3V rail (if using)
- No ferrite beads for isolation

**Recommendation:** Add 10µF + ferrite bead on analog VCC to OPA657s.

---

## 4. Component Footprint & BOM Verification

### 4.1 Critical Component Availability

| Component | Footprint | Availability | Alt Part |
|-----------|-----------|--------------|----------|
| 74HC595 | SOIC-16 | ✅ Widely available | 74HCT595 (preferred) |
| CD4051B | SOIC-16 | ✅ Widely available | 74HC4051 |
| OPA657 | SOIC-8 | ⚠️ Check stock | OPA659, AD8099 |
| BSS138 | SOT-23 | ✅ Widely available | 2N7002, BSS123 |
| BAV99 | SOT-23 | ✅ Widely available | BAT54S |
| LM7805 | SOT-223 | ✅ Widely available | AMS1117-5.0 |
| AMS1117-3.3 | SOT-223 | ✅ Widely available | XC6206 |

### 4.2 Footprint Verification Checklist

Before generating Gerbers, verify in KiCad:
- [ ] All component footprints assigned (currently "")
- [ ] Pad sizes match manufacturer specs
- [ ] Silkscreen text sizes ≥ 0.8mm height
- [ ] Component keepouts respected
- [ ] SMA connector placement allows mating

### 4.3 BOM Consolidation

**Resistor Values:**
| Value | Qty | Used For |
|-------|-----|----------|
| 100Ω | 16 | TX series, RX series, LNA gain |
| 1kΩ | 10 | MOSFET gates, LNA feedback, LEDs |
| 10kΩ | 8 | MOSFET pull-down |

**Capacitor Values:**
| Value | Qty | Used For |
|-------|-----|----------|
| 100nF | 10 | Decoupling |
| 10µF | 4 | Bulk, regulator stability |

**Verdict:** ✅ BOM is streamlined, few unique values.

---

## 5. Signal Integrity & Layout Checks

### 5.1 TX Bus Impedance

**Current Design:**
- TX_BUS is a long trace with 8 taps (to each MOSFET)
- No controlled impedance
- Will have reflections

**For 5 MHz signals:**
- Wavelength on PCB (εr=4.5): λ = c/(f×√εr) = 30m/(5M×2.1) = 2.8m
- Trace length < λ/10 = 28cm — NO IMPEDANCE CONTROL NEEDED

**Verdict:** ✅ For 5 MHz, no controlled impedance required.

### 5.2 Trace Length Matching

**For beamforming, element delays must match:**
- Target delay match: ±1 sample @ 125 MSa/s = ±8 ns
- Trace delay: 6-7 ps/mm
- Allowed length difference: 8ns / 7ps = ~1.1m

**Your board:** 100mm — well within tolerance.

**Verdict:** ✅ No length matching required.

### 5.3 Ground Plane Strategy

**Critical:** Continuous ground plane under analog signals.

**Requirements:**
- [ ] Bottom layer: solid GND plane
- [ ] Via stitching every 20mm
- [ ] No slots or cuts in GND under U4/U5 (LNAs)
- [ ] TX_BUS return path: keep close to signal (bottom layer)

### 5.4 Isolation: TX vs RX

**Goal:** Minimize TX feedthrough to RX during receive.

**Current protection:**
- BAV99 diodes (clamp ±0.7V) — only protects against large signals
- Series 100Ω resistors (RX path) — limits current

**Expected TX feedthrough:**
- TX pulse: ±1V
- MOSFET off-state leakage: ~1 µA
- Into 100Ω: V = 1µA × 100Ω = 0.1 mV
- Compared to echo (1 mV): -20 dB isolation

**Verdict:** ⚠️ May see TX breakthrough. Consider:
- Lower value series resistors on RX (47Ω)
- Active T/R switch (Rev 2)

---

## 6. Manufacturing Checklist

### 6.1 Pre-Submission Verification

| Check | Tool | Status |
|-------|------|--------|
| ERC (Electrical Rules Check) | KiCad | ⚠️ PENDING |
| DRC (Design Rules Check) | KiCad | ⚠️ PENDING |
| Footprint assignment | KiCad | ⚠️ PENDING |
| Netlist verification | KiCad | ⚠️ PENDING |
| 3D collision check | KiCad | ⚠️ PENDING |
| Gerber output | KiCad | ⚠️ PENDING |

### 6.2 Fabrication Specs for JLCPCB

| Parameter | Value |
|-----------|-------|
| Layers | 2 |
| Dimensions | 100 × 70 mm |
| Quantity | 5 |
| Thickness | 1.6 mm |
| Color | Green (or your preference) |
| Surface finish | HASL (lead-free) |
| Copper weight | 1 oz |
| Min track/spacing | 0.25mm / 0.25mm |
| Min hole size | 0.3 mm |

### 6.3 Assembly Options

**Option A: Self-assembly**
- Order PCB only
- Hand-solder all components
- Cost: ~$5 for 5 PCBs

**Option B: JLCPCB SMT assembly**
- They place standard components
- You solder SMA connectors, ICs
- Cost: ~$30-50 for 5 assembled boards

**Recommendation:** Self-assembly for Rev 1 (learn the board).

---

## 7. Critical Issues Summary

### 🔴 BLOCKING (Must Fix Before Fab)

| Issue | Impact | Fix |
|-------|--------|-----|
| **74HC595 @ 5V with 3.3V inputs** | Won't recognize logic HIGH | Change to 74HCT595 or power from 3.3V |
| **No footprints assigned** | Cannot manufacture | Assign all footprints in KiCad |
| **100Ω TX series resistors** | Too much voltage drop | Remove or reduce to 47Ω |

### 🟡 HIGH PRIORITY (Fix if Time Permits)

| Issue | Impact | Fix |
|-------|--------|-----|
| **OPA657 stability** | Possible oscillation | Add 10pF feedback capacitor |
| **No test points** | Difficult debugging | Add 6-8 test points |
| **TX/RX isolation** | -20 dB may be insufficient | Evaluate after testing |

### 🟢 LOW PRIORITY (Future Revision)

| Issue | Impact | Fix |
|-------|--------|-----|
| **2-layer vs 4-layer** | Ground integrity | Upgrade to 4-layer for Rev 2 |
| **HV pulser** | Limited TX amplitude | Add in Rev 2 |
| **TGC amplifier** | No time-gain control | Add AD8332 in Rev 2 |

---

## 8. Pre-Fabrication Action Plan

### Week 1: Design Finalization

**Day 1-2: Critical Fixes**
- [ ] Replace 74HC595 with 74HCT595 in schematic
- [ ] Remove or reduce TX series resistors to 47Ω
- [ ] Assign all component footprints

**Day 3-4: Layout Completion**
- [ ] Complete PCB routing following guidelines
- [ ] Add ground pours (top and bottom)
- [ ] Add via stitching
- [ ] Place mounting holes (4× M3, corners)

**Day 5: Verification**
- [ ] Run ERC, fix all errors
- [ ] Run DRC, fix all violations
- [ ] Generate Gerbers
- [ ] Visual check in Gerber viewer

### Week 2: Manufacturing

**Day 1:**
- [ ] Upload to JLCPCB (or PCBWay)
- [ ] Verify DFM feedback
- [ ] Order 5 PCBs

**Day 2-5:**
- [ ] Order components from Digi-Key (if not already)
- [ ] Print 1:1 PCB template for mechanical fit check

### Week 3: Bring-up

**Day 1:**
- [ ] Inspect received PCBs
- [ ] Solder power supply section first
- [ ] Power-up test (5V, 3.3V rails)

**Day 2-3:**
- [ ] Solder digital section (74HCT595)
- [ ] Test shift register with logic analyzer

**Day 4-5:**
- [ ] Solder analog section
- [ ] Full functional test with Red Pitaya

---

## 9. Test Protocol for Bring-up

### Phase 1: Power Supply (No Red Pitaya)
1. Apply 12V via current-limited supply (100 mA limit)
2. Verify 5V rail (±5%)
3. Verify 3.3V rail (±5%)
4. Check current draw (< 50 mA expected)

### Phase 2: Digital Control (Red Pitaya Connected)
1. Connect GPIO only (no SMA cables)
2. Test shift register: toggle each output, measure with DMM
3. Test mux addressing: verify COM output routing

### Phase 3: Signal Path
1. Connect signal generator to TX input
2. Select element 0, verify signal at element connector
3. Route RX mux to element 0
4. Verify amplified signal at RX output

### Phase 4: Full System
1. Connect piezo element
2. Fire TX pulse
3. Capture echo on Red Pitaya
4. Verify A-scan waveform

---

## 10. Appendices

### A. Red Pitaya Connector Pinout

**E1 Connector (2×10, 2.54mm):**
```
Pin  1: +3.3V    Pin  2: +3.3V
Pin  3: NC       Pin  4: NC
Pin  5: GND      Pin  6: GND
Pin  7: DIO0_P   Pin  8: DIO0_N
Pin  9: DIO1_P   Pin 10: DIO1_N
Pin 11: DIO2_P   Pin 12: DIO2_N
Pin 13: DIO3_P   Pin 14: DIO3_N
Pin 15: DIO4_P   Pin 16: DIO4_N
Pin 17: DIO5_P   Pin 18: DIO5_N
Pin 19: DIO6_P   Pin 20: DIO6_N
```

### B. Component Datasheet Links

| Component | Datasheet |
|-----------|-----------|
| 74HCT595 | https://www.nexperia.com/products/analog-logic-ics/logic-ics/shift-registers/74HCT595.html |
| CD4051B | https://www.ti.com/product/CD4051B |
| OPA657 | https://www.ti.com/product/OPA657 |
| BSS138 | https://www.onsemi.com/products/discrete-power-modules/mosfets/bss138 |

### C. Design Calculations

**LNA Gain:**
```
Gain = 1 + (Rf / Rg) = 1 + (1000/100) = 11 (20.8 dB)
```

**Mux On-Resistance Noise:**
```
Vn = √(4kTRB) = √(4 × 1.38e-23 × 300 × 125 × 5e6) = 3.2 µV RMS
```

**Thermal Rise (7805):**
```
ΔT = P × RθJA = 0.35W × 60°C/W = 21°C
```

---

**End of Stress Test Report**

*Status: BLOCKING ISSUES IDENTIFIED — See Section 7*
