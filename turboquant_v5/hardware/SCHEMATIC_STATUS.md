# TurboQuant V5 - Schematic Status Summary

**Date:** 2026-05-02  
**Project:** turboquant_mux_lna_v5  
**Status:** 🟡 Ready for Wiring Completion

---

## Current Status

### ✅ Complete Sheets
| Sheet | File | Status | Description |
|-------|------|--------|-------------|
| **Power** | `power.kicad_sch` | ✅ Generated | 12V→5V→3.3V with protection |
| **Digital** | `digital.kicad_sch` | ✅ Generated | 74HCT595 + 8×BSS138 drivers |

### ⚠️ Partial Sheets (Components Placed, Needs Wiring)
| Sheet | File | Status | Description |
|-------|------|--------|-------------|
| **Analog** | `analog.kicad_sch` | ⚠️ Partial | T/R bridge, MUX, LNA - needs connections |
| **TX Switch** | `tx_switch.kicad_sch` | ⚠️ Partial | Gate drivers, MOSFETs - needs connections |
| **RP Interface** | `turboquant_mux_lna_rp.kicad_sch` | ⚠️ Minimal | SMA connectors only |

### ✅ Root Schematic
| Sheet | File | Status | Description |
|-------|------|--------|-------------|
| **Root** | `turboquant_mux_lna_v5.kicad_sch` | ✅ Structure OK | All hierarchical blocks defined |

---

## Hierarchical Structure

```
turboquant_mux_lna_v5.kicad_sch (Root)
├── POWER_SUPPLIES (power.kicad_sch)
│   ├── +12V_IN → +5V → +3V3
│   ├── F1 (polyfuse), D1 (Schottky), D2 (TVS)
│   └── U1 (LM7805), U2 (AMS1117-3.3)
│
├── DIGITAL_CONTROL (digital.kicad_sch)
│   ├── J3 (RP E1 GPIO 2×10)
│   ├── U5 (74HCT595 shift register)
│   └── Q1-Q8 (BSS138 gate drivers)
│       └── Outputs: GATE0-GATE7
│
├── ANALOG_FRONTEND (analog.kicad_sch)
│   ├── CH0-CH7: T/R diode bridges (MUR120 ×32)
│   ├── U1-U2: DG408 8:1 MUX (×2)
│   ├── U3-U4: OPA1641 LNA (×2)
│   └── Outputs: RX0_OUT, RX1_OUT
│
└── TX_SWITCH (tx_switch.kicad_sch)
    ├── U8-U11: TC4427 gate drivers (×4)
    ├── Q9-Q16: IRF830 MOSFET switches (×8)
    └── TX_BUS (±100V)
```

---

## Signal Connections Needed

### 1. Analog Sheet Wiring
**Components placed but not connected:**
- [ ] T/R bridge diodes (D1-D32) → MUX inputs (U1, U2 pins 1-8)
- [ ] MUX outputs (U1, U2 pins 13, 14) → LNA inputs (U3, U3 pins 3)
- [ ] LNA outputs (U3, U4 pin 6) → hierarchical RX0_OUT, RX1_OUT
- [ ] Power: +5V → U3, U4 (VCC pins)
- [ ] Power: +12V → U1, U2 (VDD pins)
- [ ] Ground: GND → all ICs

### 2. TX Switch Sheet Wiring
**Components placed but not connected:**
- [ ] GATE0-GATE7 (from digital) → TC4427 inputs
- [ ] TC4427 outputs → IRF830 gates (with 10Ω series R)
- [ ] IRF830 drains → TX_BUS
- [ ] IRF830 sources → GND
- [ ] Power: +12V → TC4427 VDD
- [ ] Protection: Zener clamps on all gates

### 3. Root Sheet Wiring
**Hierarchical connections to wire:**
- [ ] Power sheet +5V → Digital sheet +5V
- [ ] Power sheet +5V → Analog sheet +5V
- [ ] Power sheet +12V → Analog sheet +12V
- [ ] Power sheet +12V → TX Switch sheet +12V
- [ ] Power sheet GND → All sheets GND
- [ ] Digital sheet MUX_A/B/C/EN → Analog sheet MUX_A/B/C/EN
- [ ] Digital sheet GATE0-7 → TX Switch sheet GATE0-7
- [ ] Analog sheet RX0/RX1 → Root SMA connectors

---

## Review Checklist

### Design Correctness
- [x] Power architecture: 12V → 5V → 3.3V cascade
- [x] Component values match BOM
- [x] Pin assignments verified against datasheets
- [x] Hierarchical pins match between sheets
- [ ] All nets have proper names
- [ ] No floating inputs
- [ ] Power pins connected on all ICs

### Manufacturability
- [x] All components have footprints assigned
- [x] SMD passives use standard packages (0603/0805)
- [x] ICs use standard packages (SOIC, SOT-23)
- [ ] THT components minimized (MUR120, TO-220)
- [ ] Test points added for critical signals

### Testability
- [ ] Test points on: +5V, +12V, TX_BUS, RX0, RX1
- [ ] Test points on: GATE0, MUX_A/B/C
- [ ] Debug header for SPI signals
- [ ] Current measurement points (0Ω resistors)

---

## Next Actions

### Option A: Complete Wiring in KiCad (Recommended)
1. Open KiCad 9.0
2. Load `turboquant_mux_lna_v5.kicad_pro`
3. Open each sheet and complete wire connections
4. Run ERC after each sheet
5. Update PCB from schematic

### Option B: Generate Wiring Script
1. Create Python script to add wire segments
2. Parse existing component placements
3. Generate wire connections programmatically
4. Validate with ERC

### Option C: Hybrid Approach
1. Use script for repetitive connections (power, ground)
2. Manual wiring for critical analog paths
3. Verify in KiCad with ERC

---

## Critical Paths for Review

### High Priority (Must Review)
1. **T/R Bridge Wiring** - 32 diodes, must be correct for HV isolation
2. **Gate Drive Wiring** - TC4427 to IRF830, critical for switching speed
3. **LNA Input Wiring** - OPA1641 inputs, sensitive to noise
4. **Power Distribution** - All ICs properly powered

### Medium Priority (Should Review)
5. **MUX Control Wiring** - DG408 select lines
6. **Protection Circuits** - Zener clamps, TVS diodes
7. **Connector Pinout** - RP E1, SMA connectors

### Low Priority (Nice to Have)
8. **Silkscreen Labels** - Component references
9. **Test Point Placement** - Accessibility
10. **Thermal Vias** - Under power ICs

---

## Questions for Design Review

1. **T/R Bridge:** Is the diode orientation correct for bidirectional switching?
2. **Gate Drive:** Is 10Ω series resistor sufficient for damping?
3. **LNA Gain:** Is gain=10 (1kΩ/9.09kΩ) adequate for expected echo amplitude?
4. **MUX Supply:** Is +12V sufficient for DG408 with 100V signal swing?
5. **Power Sequencing:** Do we need sequenced power-up (5V before 12V)?

---

## Files Ready for Review

| File | Purpose | Status |
|------|---------|--------|
| `SCHEMATIC_REVIEW.md` | Detailed review checklist | ✅ Ready |
| `SYSTEM_BLOCK_DIAGRAM.md` | Visual system overview | ✅ Ready |
| `power.kicad_sch` | Power regulation | ✅ Ready |
| `digital.kicad_sch` | Control logic | ✅ Ready |
| `analog.kicad_sch` | Signal chain | ⚠️ Needs wiring |
| `tx_switch.kicad_sch` | HV switching | ⚠️ Needs wiring |

---

*Ready for schematic review and wiring completion*
