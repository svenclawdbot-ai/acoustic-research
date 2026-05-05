# TurboQuant V5 — PCB Routing Checklist

## Current Status (May 1, 2026)

**Board:** 100×80mm, 4-layer  
**Placement:** ✅ Complete — all components positioned in zones  
**Routing:** ❌ Not started  
**DRC:** ❌ Not run  
**Gerbers:** ❌ Not generated  

---

## Component Placement Summary

| Zone | Components | Position |
|------|-----------|----------|
| **Power** (top-left) | J1 (12V input), F1 (polyfuse), U1 (LM7805), U2 (AMS1117) | (5-25, 15-35) |
| **Digital** (top-right) | J3 (E1 GPIO), U5 (74HCT595) | (25-50, 15-35) |
| **Analog** (center) | U3-U4 (DG408), U6-U7 (OPA1641), 32× MUR120 | (0-50, 40-80) |
| **TX Switch** (bottom) | U8-U11 (TC4427), Q9-Q16 (IRF830), J2/J4/J5 (SMA) | (50-100, 40-80) |

---

## Routing Priority Order

### 1. Power Distribution (First)
- [ ] **+12V** from J1 → U1 (LM7805) → TX switch zone
- [ ] **+5V** from U1 → digital zone, analog zone (In2 plane)
- [ ] **+3V3** from U2 → digital zone
- [ ] **GND** solid plane (In1), stitch vias every 10mm
- [ ] Decoupling caps (100nF) within 5mm of each IC power pin

### 2. High Voltage TX Paths (Critical)
- [ ] **TX_BUS** (net 5) — wide trace (≥1mm), >2mm clearance from everything
- [ ] IRF830 drains → TX_BUS (short, wide)
- [ ] Keep TX traces on top layer, no vias near analog

### 3. Gate Drive Signals (Time-Critical)
- [ ] GATE0-GATE7 from digital sheet → TC4427 inputs
- [ ] TC4427 outputs → IRF830 gates (<20mm, 10Ω series)
- [ ] Gate pull-down 1kΩ to GND
- [ ] BZX84C12 Zener clamps

### 4. Analog Signal Paths (Sensitive)
- [ ] MUX outputs → DC block caps → attenuator → LNA inputs
- [ ] LNA outputs → SMA connectors (J4, J5)
- [ ] Guard ring / GND pour around LNA inputs
- [ ] Keep analog traces away from digital switching noise

### 5. Digital Control (Low Speed)
- [ ] SER, SRCLK, RCLK, ~OE, SRCLR from J3 → 74HCT595
- [ ] 74HCT595 outputs → MUX address lines (MUX_A/B/C/EN)
- [ ] 74HCT595 outputs → BSS138 level shifters → GATE signals

---

## Critical Layout Rules

| Rule | Value | Applies To |
|------|-------|-----------|
| HV clearance | >2mm | TX_BUS vs any other signal |
| TX trace width | ≥1mm | TX_BUS, drain connections |
| Gate trace length | <20mm | TC4427 → IRF830 gate |
| Gate trace width | 0.25mm | Gate drive |
| Analog trace length | <30mm | MUX → LNA |
| Decoupling distance | <5mm | Cap to IC power pin |
| Stitching vias | every 10mm | GND plane |

---

## Net Classes

- **Default:** 0.25mm trace, 0.2mm clearance, 0.8mm via
- **HV:** 1.0mm trace, 2.0mm clearance, 1.2mm via (TX_BUS only)

---

## Post-Routing Steps

1. [ ] Run DRC (Design Rule Check)
2. [ ] Fix all errors/warnings
3. [ ] Add silkscreen labels
4. [ ] Generate Gerbers (all layers + drill)
5. [ ] Generate fabrication notes
6. [ ] Order PCB (JLCPCB / PCBWay)

---

## KiCad Actions Needed

1. Open `turboquant_mux_lna_v5.kicad_pcb`
2. Tools → Update PCB from Schematic (if needed)
3. Route traces manually (interactive router)
4. Add stitching vias
5. Run DRC
6. File → Fabrication Outputs → Gerbers

---

*Created: 2026-05-01*  
*Next: Start routing in KiCad*
