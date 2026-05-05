# TurboQuant V5 - Schematic Review Status

**Date:** 2026-05-02
**Project:** turboquant_mux_lna_v5
**Status:** Partial - Needs completion

---

## Schematic Sheets Overview

| Sheet | File | Lines | Status | Notes |
|-------|------|-------|--------|-------|
| **Root** | `turboquant_mux_lna_v5.kicad_sch` | 376 | ⚠️ Partial | Hierarchical blocks placed, needs wiring |
| **Power** | `power.kicad_sch` | 251 | ✅ Generated | 12V→5V→3.3V regulation |
| **Digital** | `digital.kicad_sch` | 224 | ✅ Generated | 74HCT595 + BSS138 drivers |
| **Analog** | `analog.kicad_sch` | 986 | ⚠️ Partial | Components placed, needs wiring |
| **TX Switch** | `tx_switch.kicad_sch` | 497 | ⚠️ Partial | Components placed, needs wiring |
| **RP Interface** | `turboquant_mux_lna_rp.kicad_sch` | 84 | ⚠️ Minimal | Placeholder only |

---

## Power Sheet - Complete ✅

### Components
| Ref | Value | Function |
|-----|-------|----------|
| J1 | 12V_IN | Power input terminal block |
| F1 | MF-NSMF200-2 | 2A polyfuse protection |
| D1 | SS34 | Schottky reverse polarity protection |
| D2 | SMAJ15A | TVS overvoltage protection |
| U1 | LM7805 | 5V linear regulator |
| U2 | AMS1117-3.3 | 3.3V linear regulator |
| C1 | 100µF | Input bulk capacitor |
| C2 | 100nF | 5V decoupling |
| C3 | 10µF | 3.3V output capacitor |

### Power Rails
- **+12V** → Input from terminal block
- **+5V** → LM7805 output (logic, OPA1641)
- **+3V3** → AMS1117 output (Red Pitaya reference)
- **GND** → Common ground

---

## Digital Sheet - Complete ✅

### Components
| Ref | Value | Function |
|-----|-------|----------|
| J3 | RP_E1_GPIO | Red Pitaya E1 connector (2×10) |
| U5 | 74HCT595 | 8-bit shift register |
| Q1-Q8 | BSS138 | NMOS gate drivers (8 channels) |
| R3 | 100Ω | Gate series resistor |

### Signals
- **Inputs:** SER, SRCLK, RCLK, OE, SRCLR (from RP E1)
- **Outputs:** GATE0-GATE7 (to TX switch sheet)

---

## Analog Sheet - Needs Wiring ⚠️

### Components Placed
| Ref | Value | Function | Status |
|-----|-------|----------|--------|
| U1 | DG408 | 8:1 MUX (channel 0-7) | Placed |
| U2 | DG408 | 8:1 MUX (channel 0-7) | Placed |
| U3 | OPA1641 | LNA (RX0) | Placed |
| U4 | OPA1641 | LNA (RX1) | Placed |
| D1-D32 | MUR120 | T/R bridge diodes | Placed |
| Z1-Z8 | BZX84C5V1 | Zener bias diodes | Placed |
| R1-R16 | Various | Bias/termination resistors | Placed |

### Missing
- [ ] Wire connections between T/R bridge and MUX inputs
- [ ] Wire connections between MUX outputs and LNAs
- [ ] Power connections to all ICs
- [ ] Hierarchical pin connections

---

## TX Switch Sheet - Needs Wiring ⚠️

### Components Placed
| Ref | Value | Function | Status |
|-----|-------|----------|--------|
| U8-U11 | TC4427 | Gate drivers (4 dual channels) | Placed |
| Q9-Q16 | IRF830 | HV MOSFET switches | Placed |
| Various | R/D/Z | Gate protection network | Placed |

### Missing
- [ ] Gate drive connections from digital sheet
- [ ] TX_BUS connections to analog sheet
- [ ] Power connections to gate drivers

---

## RP Interface Sheet - Needs Content ⚠️

Currently minimal - needs:
- [ ] SMA connectors for TX/RX
- [ ] E1 connector pinout
- [ ] Level shifting if needed

---

## Action Items

### Immediate (Today)
1. **Complete analog wiring** - Connect T/R bridge → MUX → LNA
2. **Complete TX switch wiring** - Connect gate drivers → MOSFETs
3. **Verify hierarchical connections** - All sheets must connect properly

### Short Term (This Week)
4. **Run ERC** - Electrical Rule Check on all sheets
5. **Add footprints** - Verify all components have valid footprints
6. **Generate netlist** - For PCB layout

### Before PCB Layout
7. **Component review** - Verify BOM matches schematic
8. **Design rule check** - HV clearances, trace widths
9. **Peer review** - Have someone else check the design

---

## Component Count Summary

| Category | Count | Notes |
|----------|-------|-------|
| ICs | 11 | 2×DG408, 2×OPA1641, 1×74HCT595, 4×TC4427 |
| Transistors | 16 | 8×BSS138, 8×IRF830 |
| Diodes | 40+ | 32×MUR120, Zeners, protection |
| Resistors | 30+ | Various values |
| Capacitors | 10+ | Decoupling, bulk |
| Connectors | 10+ | SMA, terminal blocks, headers |

---

## Critical Design Points

### High Voltage (TX_BUS ±100V)
- **Clearance:** >2mm from all low-voltage traces
- **Isolation:** T/R bridge provides galvanic isolation
- **Protection:** TVS + Zener clamps on all gates

### Signal Integrity
- **LNA input:** Guard ring + GND pour around OPA1641 inputs
- **MUX routing:** Differential pairs for RX0/RX1
- **Gate drive:** <20mm trace length, 10Ω series resistor

### Power Sequencing
- **+12V** first (external input)
- **+5V** second (LM7805 from 12V)
- **+3V3** third (AMS1117 from 5V)
- **Enable** digital last (prevent glitches)

---

## Next Steps

1. Open KiCad 9.0
2. Load `turboquant_mux_lna_v5.kicad_pro`
3. Update PCB from schematic (Tools → Update PCB)
4. Complete wiring in analog and TX switch sheets
5. Run ERC and fix errors
6. Proceed to PCB layout

---

*Generated: 2026-05-02*
*Status: Ready for wiring completion*
