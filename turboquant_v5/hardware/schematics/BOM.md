# TurboQuant V5 — Bill of Materials

*Generated: 2026-04-27 08:59 GMT+1*
*Schematic Revision: 5.0*

---

## ICs & Semiconductors

| Qty | Reference | Value | Footprint | Description | Est. Price |
|-----|-----------|-------|-----------|-------------|------------|
| 2 | U3, U4 | DG408 | SOIC-16 | 8-channel analog MUX | £3.00 |
| 2 | U6, U7 | OPA1641 | SOIC-8 | Precision JFET LNA | £4.00 |
| 4 | U8-U11 | TC4427 | SOIC-8 | Dual 1.5A MOSFET driver | £4.00 |
| 8 | Q9-Q16 | IRF830 | TO-220 | 500V/4.5A N-ch MOSFET | £8.00 |
| 1 | U5 | 74HCT595 | SOIC-16 | 8-bit shift register | £0.50 |
| 1 | U1 | LM7805 | TO-252 (DPAK) | 5V regulator | £0.50 |
| 1 | U2 | AMS1117-3.3 | SOT-223 | 3.3V LDO | £0.30 |
| **19** | | | | | **£20.30** |

## Diodes

| Qty | Reference | Value | Footprint | Description | Est. Price |
|-----|-----------|-------|-----------|-------------|------------|
| 32 | D1-D32 | MUR120 | DO-41 | Ultra-fast rectifier (T/R bridge) | £6.40 |
| 8 | Z1-Z8 (analog) | BZX84C5V1 | SOD-323 | 5.1V Zener (MUX protection) | £0.80 |
| 8 | Z9-Z16 (tx) | BZX84C12 | SOD-323 | 12V Zener (gate clamp) | £0.80 |
| 2 | D33-D34 | BAV99 | SOT-23 | Dual switching diode (LNA clamp) | £0.20 |
| 1 | D1 (power) | SS34 | SMA | Schottky (reverse protection) | £0.20 |
| **51** | | | | | **£8.40** |

## Resistors

| Qty | Reference | Value | Footprint | Description | Est. Price |
|-----|-----------|-------|-----------|-------------|------------|
| 8 | R1, R4, R7, R10, R13, R16, R19, R22 (tx) | 10Ω | 0603 | Gate series damping — **ALL 10Ω per your spec** | £0.08 |
| 8 | R2, R5, R8, R11, R14, R17, R20, R23 (tx) | 1kΩ | 0603 | Gate pull-down | £0.08 |
| 8 | R9-R16 | 1kΩ | 0603 | T/R bridge bias (pull-up) | £0.08 |
| 8 | R17-R24 | 100kΩ | 0603 | T/R bridge bias (pull-down) | £0.08 |
| 2 | R33-R34 | 9.09kΩ | 0603 | Attenuator (10:1) | £0.02 |
| 2 | R35-R36 | 1kΩ | 0603 | Attenuator | £0.02 |
| 1 | R3 (digital) | 100Ω | 0603 | Level shift series | £0.01 |
| **31** | | | | | **£0.35** |

## Capacitors

| Qty | Reference | Value | Footprint | Description | Est. Price |
|-----|-----------|-------|-----------|-------------|------------|
| 4 | C1-C4 (tx) | 100nF | 0603 | TC4427 decoupling | £0.04 |
| 2 | C7-C8 (analog) | 100nF | 0603 | MUX DC block | £0.02 |
| 3 | C1-C3 (analog) | 100nF | 0603 | LNA + MUX decoupling | £0.03 |
| 1 | C2 (power) | 100nF | 0805 | Regulator input | £0.01 |
| 1 | C3 (power) | 10µF | 0805 | Regulator output (5V) | £0.10 |
| 1 | C1 (power) | 100µF | Radial | Input bulk capacitor | £0.30 |
| **12** | | | | | **£0.50** |

## Passives / Other

| Qty | Reference | Value | Footprint | Description | Est. Price |
|-----|-----------|-------|-----------|-------------|------------|
| 1 | F1 | 2A polyfuse | 1206 | Input protection | £0.20 |
| 1 | J1 | 2-pin terminal | 5.08mm pitch | 12V input | £0.30 |
| 1 | J3 | 2×10 header | 2.54mm pitch | E1 GPIO | £0.50 |
| 3 | J2, J4, J5 | SMA edge | SMA | TX/RX connectors | £3.00 |
| **6** | | | | | **£4.00** |

---

## Summary

| Category | Qty | Est. Cost |
|----------|-----|-----------|
| ICs & Semiconductors | 19 | £20.30 |
| Diodes | 51 | £8.40 |
| Resistors | 31 | £0.35 |
| Capacitors | 12 | £0.50 |
| Passives / Other | 6 | £4.00 |
| **TOTAL** | **119** | **£33.55** |

---

## ⚠️ Known BOM Issues

### 1. Digital Sheet Incomplete
The `digital.kicad_sch` is missing:
- **R1-R2, R4-R5**: 74HCT595 pull-down resistors (should be ~5× 10kΩ)
- **C7**: 74HCT595 VCC decoupling capacitor (100nF)
- These were listed in `docs/bom/BOM_v5.md` but don't exist in the schematic file yet

### 2. Power Sheet Capacitors
- Only C1 (100µF), C2 (100nF), C3 (10µF) exist in `power.kicad_sch`
- `BOM_v5.md` lists C4-C6 for 3.3V regulator decoupling — not yet placed

### 3. Resistor Count Reduced
- **Gate series resistors**: Fixed from mixed 10R/100R → **all 10Ω** (8 qty)
- **T/R bridge bias**: BOM_v5 says 16× 10kΩ + 16× 100kΩ, but schematic shows **8× 1kΩ + 8× 100kΩ**
- The 10kΩ resistors may be for digital pull-downs (missing from schematic)

**Recommendation**: Complete digital sheet in KiCad GUI tonight, then re-run BOM extraction.

## Procurement Status

| Item | Supplier | Status | Ordered | Est. Arrival | Notes |
|------|----------|--------|---------|--------------|-------|
| Red Pitaya STEMlab 125-14 Gen 2 | Red Pitaya / Digi-Key | 🔴 **NOT ORDERED** | — | — | £250 — **ORDER NOW** |
| DG408 ×2 | Digi-Key / Mouser | 🔴 **NOT ORDERED** | — | — | SOIC-16 package |
| 74HCT595 ×1 | Digi-Key / LCSC | 🔴 **NOT ORDERED** | — | — | SOIC-16, TTL levels |
| IRF830 ×8 | Digi-Key / Mouser | 🔴 **NOT ORDERED** | — | — | TO-220, 500V |
| OPA1641 ×2 | Digi-Key / Mouser | 🔴 **NOT ORDERED** | — | — | SOIC-8 |
| TC4427 ×4 | Digi-Key / LCSC | 🔴 **NOT ORDERED** | — | — | SOIC-8 |
| MUR120 ×32 | Digi-Key / LCSC | 🔴 **NOT ORDERED** | — | — | DO-41 |
| Passives (resistors, caps, diodes) | LCSC | 🔴 **NOT ORDERED** | — | — | Bulk order |
| PCB fabrication | JLCPCB / PCBWay | 🔴 **NOT ORDERED** | — | — | 4-layer, 100×80mm |

### 🔴 CRITICAL: Nothing ordered yet!

**Next actions:**
1. **Order Red Pitaya STEMlab 125-14** — longest lead time item
2. **Submit Digi-Key/LCSC BOM** — rest of components
3. **Finalize PCB design** — analog schematic + TX switch sheet still incomplete
4. **Send PCB for fab** — after DRC clearance

---

*Previous notes below:*
