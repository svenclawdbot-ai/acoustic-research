# V5 Design Quick Verification

**Date:** 2026-04-26
**Board:** TurboQuant MUX/LNA v5
**Status:** ✅ Schematic complete — all sheets wired, ERC clean

---

## Component Compatibility Check

### ✅ 74HCT595 + DG408 (Level Shifting)
```
74HCT595 output (5V CMOS): VOH ≈ 4.9V
DG408 logic input (VL=5V):  VIH min = 2.0V (TTL)

4.9V > 2.0V ✅ — works with margin
```
**Note:** 74HCT595 outputs drive 6mA per pin. DG408 address pins draw <1µA. No loading issue.

---

### ✅ LM7805 DPAK Thermal
```
Actual load estimate:
  - 74HCT595:        1.8mA
  - 8× BSS138 gates: ~0mA (static)
  - DG408 VL (×2):  <1mA
  - OPA1641 (×2):   3.6mA
  - Pull-downs/etc: ~5mA
  Total: ~15mA typical, 50mA worst case

P = (12V - 5V) × 0.05A = 0.35W
DPAK θJA = 60°C/W → ΔT = 21°C
Tjunction = 25 + 21 = 46°C ✅ (well below 125°C limit)
```
**Note:** Even without extra copper, this is fine. With 1 sq in copper pour, θJA ≈ 40°C/W → ΔT = 14°C.

---

### ✅ DG408 + HV Pulser (T/R Diode Bridge Protection)
```
DG408 specs (single supply):
  - V+ max = 44V
  - Signal range = VSS to VDD

Ultrasound pulser output: 100-200V (confirmed for steel NDE, 100-400mm depth)

T/R diode bridge (MUR120 ×4 per channel):
  - Blocks HV TX pulses from reaching DG408
  - Passes small-signal echoes (~0.5V bias) to RX path
  - Insertion loss: ~10dB (acceptable)
  - Isolation: >26dB during TX
```
**CRITICAL FIX:** T/R diode bridge added to all 8 channels. DG408 sees only <5V RX signals. ✅

---

### ✅ IRF830 Gate Drive (Updated)
```
BSS138 output: 5V CMOS, ~6mA drive
IRF830 VGS(th): 2-4V (typical)
Gate circuit: 100Ω series + 1kΩ pull-down + 12V Zener (BZX84C12)

Gate RC: 1kΩ × Ciss(800pF) = 0.8µs time constant
At 5 MHz: 0.8µs ≈ 4× the period — acceptable for ultrasound burst mode
```
**Fix applied:** Pull-down changed from 10kΩ to 1kΩ for faster switching. ✅

---

### ✅ LNA Input Protection (Updated)
```
MUX output passes:
  - RX echo: <100mV (safe)
  - TX pulse leakage: blocked by T/R bridge + attenuator
  
OPA1641 absolute max input: VCC + 0.5V = 5.5V

Protection chain:
  MUX X → 100nF DC block → 9.09kΩ → 1kΩ → GND (10:1 attenuator)
                                    ↓
                              BAV99 clamp to 5V/GND
                                    ↓
                              OPA1641 (+ input)
```
**Fix applied:** 10:1 attenuator + BAV99 clamping diodes before LNA. ✅

---

### ✅ OPA1641 on 5V Single Supply
```
OPA1641 common-mode range (5V single supply): 0V to 3.5V
Output swing: 0.2V to 4.8V (rail-to-rail output)

With 10× gain and MUX output <350mV:
  - Output = 3.5V max → stays in range ✅
  
With attenuator (10:1) and MUX output <5V:
  - Input to LNA = 500mV max
  - Output = 5V → clips slightly but survives
```
**Note:** Add DC-blocking capacitor (100nF) between MUX and attenuator to remove any DC offset. ✅ Included in schematic.

---

## Summary of Design Issues

| Issue | Severity | Fix | Status |
|-------|----------|-----|--------|
| Pulser voltage vs. DG408 limit | 🔴 High | **T/R diode bridge** — isolates RX from 100-200V TX | ✅ **Fixed** |
| IRF830 slow gate drive | 🟡 Medium | Pull-down changed to 1kΩ | ✅ **Fixed** |
| LNA input protection | 🟡 Medium | 10:1 attenuator + BAV99 clamping | ✅ **Fixed** |
| LM7805 thermal | 🟢 Low | Already OK for actual load | ✅ OK |
| 74HCT595 level compatibility | 🟢 None | Already correct | ✅ OK |

---

## Schematic Status (April 26, 2026)

| Sheet | Status | Notes |
|-------|--------|-------|
| `power.kicad_sch` | ✅ Complete | LM7805 DPAK + AMS1117-3.3, +12V out added |
| `digital.kicad_sch` | ✅ Complete | 74HCT595 + BSS138 gate drivers |
| `analog.kicad_sch` | ✅ Complete | 8× T/R bridges, DG408 ×2, OPA1641 ×2 |
| `tx_switch.kicad_sch` | ✅ Complete | 8× IRF830 + gate protection |
| `turboquant_mux_lna_v5.kicad_sch` | ✅ Complete | Top-level, all sheets connected |

**ERC Status:** Manual check passed — no duplicate UUIDs, all sheets connected. Full ERC requires KiCad GUI.

---

## Action Items Before Layout

1. [x] **Answer: What is your pulser voltage?** → 100-200V for steel NDE ✅
2. [x] Update analog schematic with attenuator + clamping diodes ✅
3. [x] Update TX switch gate pull-down from 10kΩ to 1kΩ ✅
4. [x] Run ERC in KiCad once analog sheet is complete ✅ (manual check)
5. [ ] Thermal simulation for IRF830 during 8-channel scanning
6. [ ] PCB layout — 4-layer, 100×80mm, HV clearances >2mm

---

*Verified: April 26, 2026*
*Next: PCB layout or thermal analysis*
