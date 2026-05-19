# TurboQuant V5 — Action Plan
**Date:** 2026-05-19
**Status:** Schematic wiring in progress

---

## ✅ Completed Today

### A. Analog Frontend Sheet (`analog.kicad_sch`)
- **Status:** Wiring complete — visually verified via file parsing
- 73 symbols placed, ~200 wire segments, all T/R bridges → MUX → LNA connected
- Power rails (+5V, +12V, GND) distributed to all ICs
- Hierarchical pins: MUX_A/B/C/EN, TX_BUS, RX0_OUT, RX1_OUT wired

### B. TX Switch Sheet (`tx_switch.kicad_sch`)
- **Status:** Partial — power/decoupling wired, signal path needs GUI fix
- Fixed: All 8 gate series resistors standardized to **10Ω** (was mixed 10R/100R)
- Added: +12V to all 4 TC4427 VDD pins
- Added: GND to all 4 TC4427 GND pins (pins 2 & 6)
- Added: C1-C4 decoupling cap wiring across TC4427 VDD-GND
- **⚠️ CRITICAL:** TC4427 signal path bypassed — needs manual reroute in KiCad GUI

---

## 🔧 Remaining Schematic Work

### 1. TX Switch — Signal Path Fix (KiCad GUI Required)
**Priority:** HIGH

Current wiring connects GATE signals directly to series resistors, **skipping the TC4427 gate drivers entirely**.

**Fix in KiCad Eeschema:**
```
For each channel, change:
  GATE0 ──→ R1 ──→ Q1 gate
To:
  GATE0 ──→ U1 A_in ──→ U1 A_out ──→ R1 ──→ Q1 gate

  GATE1 ──→ U1 B_in ──→ U1 B_out ──→ R4 ──→ Q2 gate
  GATE2 ──→ U2 A_in ──→ U2 A_out ──→ R7 ──→ Q3 gate
  GATE3 ──→ U2 B_in ──→ U2 B_out ──→ R10 ──→ Q4 gate
  GATE4 ──→ U3 A_in ──→ U3 A_out ──→ R13 ──→ Q5 gate
  GATE5 ──→ U3 B_in ──→ U3 B_out ──→ R16 ──→ Q6 gate
  GATE6 ──→ U4 A_in ──→ U4 A_out ──→ R19 ──→ Q7 gate
  GATE7 ──→ U4 B_in ──→ U4 B_out ──→ R22 ──→ Q8 gate
```

**Steps:**
1. Open `tx_switch.kicad_sch` in KiCad
2. Delete direct wire from each hierarchical GATE pin to its series resistor
3. Wire GATE → TC4427 input (A_in or B_in)
4. Wire TC4427 output (A_out or B_out) → series resistor
5. Verify: series resistor → MOSFET gate (already correct)

### 2. Root Schematic — Hierarchical Connections
**Priority:** MEDIUM

**Check these are wired:**
- [ ] Power sheet +5V → Digital sheet +5V
- [ ] Power sheet +5V → Analog sheet +5V
- [ ] Power sheet +12V → Analog sheet +12V
- [ ] Power sheet +12V → TX Switch sheet +12V
- [ ] Power sheet GND → All sheets GND
- [ ] Digital sheet MUX_A/B/C/EN → Analog sheet MUX_A/B/C/EN
- [ ] Digital sheet GATE0-7 → TX Switch sheet GATE0-7
- [ ] Analog sheet RX0/RX1 → Root SMA connectors
- [ ] TX Switch sheet TX_BUS → Analog sheet TX_BUS

### 3. ERC (Electrical Rules Check)
**Priority:** HIGH — Do this after all wiring is complete

- Open root schematic in KiCad GUI
- Tools → Electrical Rules Checker
- Fix all errors before PCB layout

---

## 📋 Next Steps After Schematic

### 4. PCB Layout
**Priority:** MEDIUM

- Update PCB from schematic (F8 in KiCad)
- Component placement per `PCB_LAYOUT_PLAN.md`
- 4-layer board: signal/GND/power/signal
- HV clearances >2mm for TX_BUS (100V)
- Route sensitive analog paths (RX0, RX1) away from digital switching noise

### 5. BOM & Procurement
**Priority:** LOW (can order before PCB is fully routed)

- Verify all components have footprints assigned
- Cross-check against `TURBOQUANT_V5_HARDWARE.md`
- Order from Digi-Key: ~£15-20 for ICs
- Order Red Pitaya STEMlab 125-14: ~£250

### 6. Fabrication
**Priority:** LOW (after PCB complete)

- Generate Gerbers, drill files, pick-and-place
- Send to PCB manufacturer (JLCPCB, PCBWay, etc.)
- 4-layer, 100×80mm, ENIG finish recommended for SMA connectors

---

## 🎯 Tonight's Session Plan

**Suggested order:**
1. **Open KiCad** → load `turboquant_mux_lna_v5.kicad_pro`
2. **Fix TX Switch signal paths** (items 1 above) — ~30 min
3. **Verify root schematic connections** (item 2) — ~15 min
4. **Run ERC** — fix any errors — ~15 min
5. **Save all, commit** — `git add . && git commit -m "Complete schematic wiring"`

**If time permits:**
6. Update PCB from schematic, start component placement

---

## 📝 Notes

- KiCad CLI SVG export fails in headless mode — use GUI for schematic review
- All changes today committed to git — pull before starting
- Soil probe short circuit: troubleshoot separately (not this board)

---
*Generated: 2026-05-19 09:15 GMT+1*
