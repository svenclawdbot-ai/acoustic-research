# TurboQuant V5 — Hardware Requirements (Consolidated)

**Date:** 2026-04-21
**Status:** Finalised — Ready for procurement & layout
**Active Design:** V5 only (v3/v4 archived)

---

## Architecture Summary

```
12V_IN → Power (LM7805 DPAK + AMS1117) → 5V / 3.3V
            ↓
Red Pitaya E1 GPIO → 74HCT595 → 8× BSS138 gate drivers
            ↓
8× TX_OUT (SMA) → IRF830 switches → DG408 8:1 MUX (×2) → OPA1641 LNA (×2) → RX0/RX1 (SMA)
            ↑
      TX_IN (SMA, from RP DAC)
```

**Key V5 changes:**
- 74HCT595 (TTL levels, 3.3V compatible) — replaces 74HC595
- DG408 100V 8:1 MUX (×2) — replaces CD4051B / PE4259
- OPA1641 low-noise op-amp (×2) — replaces ADL5610 / AD8332
- IRF830 500V MOSFET (×8) — new TX switching stage
- LM7805 DPAK — replaces TO-220, adequate for actual load (~50mA)

---

## Consolidated BOM

### Power Section

| Ref | Qty | Description | Manufacturer | Part # | Package | DigiKey | Mouser | LCSC | Unit |
|-----|-----|-------------|--------------|--------|---------|---------|--------|------|------|
| F1 | 1 | Polyfuse, 2A, 1206 | Bourns | MF-NSMF200-2 | 1206 | MF-NSMF200-2CT-ND | 652-MF-NSMF200-2 | C3699 | $0.15 |
| D1 | 1 | Schottky, 40V, 3A | Vishay | SS34 | SMA | SS34-E3/57TCT-ND | 625-SS34-E3/57 | C8598 | $0.25 |
| D2 | 1 | TVS, 15V, 400W | Vishay | SMAJ15A | SMA | SMAJ15A-E3/61CT-ND | 625-SMAJ15A-E3/61 | C5141131 | $0.20 |
| U1 | 1 | LDO, 5V, DPAK | TI | LM7805MP | TO-252 | LM7805MPX/NOPBCT-ND | 926-LM7805MPX/NOPB | C58016 | $0.50 |
| U2 | 1 | LDO, 3.3V, 1A | AMS | AMS1117-3.3 | SOT-223 | AMS1117-3.3CT-ND | 621-AMS1117-3.3 | C6186 | $0.20 |
| C1 | 1 | Cap, 100µF, 25V, electrolytic | Panasonic | EEU-FR1E101 | Radial 6.3mm | P1234-ND | - | C43850 | $0.30 |
| C2 | 1 | Cap, 100nF, 50V, X7R | Murata | GRM21BR71H104KA01L | 0805 | 490-GRM21BR71H104KA01LCT-ND | 81-GRM21BR71H104KA1L | C440198 | $0.05 |
| C3 | 1 | Cap, 10µF, 16V, X5R | Murata | GRM21BR61C106KE15L | 0805 | 490-GRM21BR61C106KE15LCT-ND | 81-GRM21BR61C106KE15L | C440198 | $0.10 |
| C4 | 1 | Cap, 100nF, 50V, X7R | Murata | GRM21BR71H104KA01L | 0805 | 490-GRM21BR71H104KA01LCT-ND | 81-GRM21BR71H104KA1L | C440198 | $0.05 |
| C5 | 1 | Cap, 10µF, 10V, X5R | Murata | GRM21BR61A106KE19L | 0805 | 490-GRM21BR61A106KE19LCT-ND | 81-GRM21BR61A106KE19L | C440198 | $0.10 |
| C6 | 1 | Cap, 100nF, 50V, X7R | Murata | GRM21BR71H104KA01L | 0805 | 490-GRM21BR71H104KA01LCT-ND | 81-GRM21BR71H104KA1L | C440198 | $0.05 |
| J1 | 1 | Terminal block, 2-pin, 5.08mm | Phoenix Contact | 1725656 | 5.08mm | 277-1725656-ND | 651-1725656 | C8465 | $0.50 |

**Power subtotal:** ~$2.95

---

### Digital Control Section

| Ref | Qty | Description | Manufacturer | Part # | Package | DigiKey | Mouser | LCSC | Unit |
|-----|-----|-------------|--------------|--------|---------|---------|--------|------|------|
| U3 | 1 | Shift Register, 8-bit, TTL | TI | SN74HCT595DR | SOIC-16 | 296-1572-5-ND | 595-SN74HCT595DR | C132142 | $0.40 |
| C7 | 1 | Cap, 100nF, 50V, X7R | Murata | GRM188R71H104KA01D | 0603 | 490-GRM188R71H104KA01DCT-ND | 81-GRM188R71H104KA01D | C14663 | $0.05 |
| R1-R5 | 5 | Resistor, 10kΩ, 1% | Yageo | RC0603FR-0710KL | 0603 | 311-10.0KHRCT-ND | 603-RC0603FR-0710KL | C25804 | $0.01 |

**Digital subtotal:** ~$0.50

---

### Analog MUX Section (100V)

| Ref | Qty | Description | Manufacturer | Part # | Package | DigiKey | Mouser | LCSC | Unit |
|-----|-----|-------------|--------------|--------|---------|---------|--------|------|------|
| U4, U5 | 2 | Analog MUX, 8:1, 100V | Vishay | DG408DY-T1-E3 | SOIC-16 | DG408DY-T1-GE3CT-ND | 84-DG408DY-T1-GE3 | C115553 | $2.50 |
| R6-R13 | 8 | Resistor, 10kΩ, 1% | Yageo | RC0603FR-0710KL | 0603 | 311-10.0KHRCT-ND | 603-RC0603FR-0710KL | C25804 | $0.01 |
| C8, C9 | 2 | Cap, 100nF, 50V, X7R | Murata | GRM188R71H104KA01D | 0603 | 490-GRM188R71H104KA01DCT-ND | 81-GRM188R71H104KA01D | C14663 | $0.05 |

**MUX subtotal:** ~$5.30

---

### LNA Section

| Ref | Qty | Description | Manufacturer | Part # | Package | DigiKey | Mouser | LCSC | Unit |
|-----|-----|-------------|--------------|--------|---------|---------|--------|------|------|
| U6, U7 | 2 | Op-Amp, low-noise, JFET input | TI | OPA1641AID | SOIC-8 | 296-27891-5-ND | 595-OPA1641AID | C55823 | $1.50 |
| R14-R17 | 4 | Resistor, 1kΩ, 1% | Yageo | RC0805FR-071KL | 0805 | 311-1.00KCRCT-ND | 603-RC0805FR-071KL | C17513 | $0.01 |
| R18-R21 | 4 | Resistor, 9.09kΩ, 1% | Yageo | RC0805FR-079K09L | 0805 | 311-9.09KCRCT-ND | 603-RC0805FR-079K09L | C17475 | $0.01 |
| C10-C13 | 4 | Cap, 100nF, 50V, X7R | Murata | GRM188R71H104KA01D | 0603 | 490-GRM188R71H104KA01DCT-ND | 81-GRM188R71H104KA01D | C14663 | $0.05 |

**LNA subtotal:** ~$3.20

---

### TX Switch + T/R Protection Section (100-200V)

| Ref | Qty | Description | Manufacturer | Part # | Package | DigiKey | Mouser | LCSC | Unit |
|-----|-----|-------------|--------------|--------|---------|---------|--------|------|------|
| Q1-Q8 | 8 | MOSFET, N-channel, 500V, 4.5A | Vishay | IRF830 | TO-220 | IRF830PBF-ND | 844-IRF830PBF | C99 | $0.80 |
| R22-R29 | 8 | Resistor, 100Ω, 1% | Yageo | RC0603FR-07100RL | 0603 | 311-100HRCT-ND | 603-RC0603FR-07100RL | C22775 | $0.01 |
| R30-R37 | 8 | Resistor, 10kΩ, 1% | Yageo | RC0603FR-0710KL | 0603 | 311-10.0KHRCT-ND | 603-RC0603FR-0710KL | C25804 | $0.01 |
| R38-R45 | 8 | Resistor, 1kΩ, 1% | Yageo | RC1206FR-071KL | 1206 | 311-1.00KLRCT-ND | 603-RC1206FR-071KL | C114393 | $0.02 |
| Z1-Z8 | 8 | Zener, 12V, 500mW | ON Semi | BZX84C12LT1G | SOD-323 | BZX84C12LT1GOSCT-ND | 863-BZX84C12LT1G | C32576 | $0.05 |
| D1-D32 | 32 | Diode, fast recovery, 200V, 50ns | ON Semi | MUR120G | DO-41 | MUR120GOS-ND | 863-MUR120G | C12345 | $0.30 |
| R46-R61 | 16 | Resistor, 10kΩ, 1% | Yageo | RC0603FR-0710KL | 0603 | 311-10.0KHRCT-ND | 603-RC0603FR-0710KL | C25804 | $0.01 |
| R62-R77 | 16 | Resistor, 100kΩ, 1% | Yageo | RC0603FR-07100KL | 0603 | 311-100KLRCT-ND | 603-RC0603FR-07100KL | C25804 | $0.01 |
| Z9-Z16 | 8 | Zener, 5.1V, 500mW | ON Semi | BZX84C5V1LT1G | SOD-323 | BZX84C5V1LT1GOSCT-ND | 863-BZX84C5V1LT1G | C32577 | $0.05 |

**TX + T/R subtotal:** $7.60 (MOSFETs) + $9.60 (diodes) + $0.32 (bias resistors) + $0.40 (zener) = **$17.92**

---

### Connectors

| Ref | Qty | Description | Manufacturer | Part # | Package | DigiKey | Mouser | LCSC | Unit |
|-----|-----|-------------|--------------|--------|---------|---------|--------|------|------|
| J2 | 1 | Header, 1×6, 2.54mm | Amphenol | TSW-106-07-G-S | Through-hole | TSW-106-07-G-S-ND | 649-TSW-106-07-G-S | C35419 | $0.30 |
| J3 | 1 | Header, 1×2, 2.54mm | Amphenol | TSW-102-07-G-S | Through-hole | TSW-102-07-G-S-ND | 649-TSW-102-07-G-S | C35419 | $0.15 |
| J4 | 1 | SMA, vertical, jack | Amphenol | 132134-11 | — | 132134-11-ND | 523-132134-11 | C496552 | $2.00 |
| J5-J12 | 8 | SMA, vertical, jack | Amphenol | 132134-11 | — | 132134-11-ND | 523-132134-11 | C496552 | $2.00 |
| J13, J14 | 2 | SMA, vertical, jack | Amphenol | 132134-11 | — | 132134-11-ND | 523-132134-11 | C496552 | $2.00 |

**Connectors subtotal:** ~$22.45

---

### Mechanical

| Ref | Qty | Description | Manufacturer | Part # | Cost |
|-----|-----|-------------|--------------|--------|------|
| H1-H4 | 4 | Mounting hole, M3 | — | 3.2mm | $0.00 |
| — | 4 | Standoff, M3, 10mm | Keystone | 24443 | $0.25 |

**Mechanical subtotal:** ~$1.00

---

## Grand Total

| Section | Cost |
|---------|------|
| Power | $2.95 |
| Digital | $0.50 |
| Analog MUX | $5.30 |
| LNA | $3.20 |
| **TX + T/R Switch** | **$17.92** |
| Connectors | $22.45 |
| Mechanical | $1.00 |
| **PCB components** | **$53.32** |
| Red Pitaya STEMlab 125-14 Gen 2 | $250.00 |
| **TOTAL** | **$293.00** |

---

## Procurement Tracker

### ✅ Already Ordered (March 28, 2026 — Digi-Key)

| Item | Part # | Qty | Status | Reusable? |
|------|--------|-----|--------|-----------|
| 74HC595 | 296-1600-5-ND | 2 | ❌ Wrong — need 74HCT595 | No |
| CD4051B | 296-2057-5-ND | 3 | ❌ Wrong — need DG408 | No |
| AD8332 | AD8332ARUZ-ND | 1 | ❌ Not in v5 design | No |
| BSS138 | BSS138-7-FCT-ND | 10 | ✅ Correct | Yes |
| LM7805 TO-220 | LM7805CT-ND | 2 | ⚠️ Wrong pkg — need DPAK | Maybe for testing |
| AMS1117-3.3 | AMS1117-3.3CT-ND | 2 | ✅ Correct | Yes |
| BAV99 | BAV99-7-F-ND | 10 | ⚠️ Not in v5 BOM | Maybe |
| Resistors (10k, 100, 1k) | Various | 150 | ✅ Correct | Yes |
| Capacitors (100nF, 10µF) | Various | 75 | ✅ Correct | Yes |
| SMA edge-mount | 732-5318-ND | 4 | ⚠️ Need 11 total | Partial |
| 2×20 pin header | S1011EC-40-ND | 2 | ✅ Correct | Yes |
| Screw terminal | ED10561-ND | 2 | ✅ Correct | Yes |
| Prototype PCB | 377-2095-ND | 2 | ✅ Correct | Yes |

**Order total:** £68.26
**Reusable value:** ~£35-40
**Write-off (wrong parts):** ~£25-30

---

### 🔴 Still Need to Order

**Priority 1 — Red Pitaya (3-5 day lead)**
- [ ] STEMlab 125-14 Gen 2 — £250 — https://redpitaya.com/product/stemlab-125-14/

**Priority 2 — V5-specific ICs (order ASAP)**
- [ ] DG408 ×2 — DG408DY-T1-GE3CT-ND — ~£5
- [ ] 74HCT595 ×1 — 296-1572-5-ND — ~£0.40
- [ ] IRF830 ×8 — IRF830PBF-ND — ~£6.40
- [ ] OPA1641 ×2 — 296-27891-5-ND — ~£3.00
- [ ] LM7805 DPAK ×1 — LM7805MPX/NOPBCT-ND — ~£0.50
- [ ] **MUR120 ×32 — MUR120GOS-ND — ~£9.60 — T/R switch diodes, 200V, 50ns**
- [ ] **BZX84C5V1 ×8 — BZX84C5V1LT1GOSCT-ND — ~£0.40 — T/R bias zener, 5.1V**
- [ ] **100kΩ resistors ×16 — RC0603FR-07100KL — ~£0.16 — T/R bias network**

**Priority 3 — Additional passives for v5**
- [ ] 9.09kΩ resistors ×4 — for LNA gain setting
- [ ] 1206 1kΩ resistors ×8 — for TX current limit
- [ ] BZX84C12 Zener ×8 — for gate protection
- [ ] Additional SMA connectors ×7 — (already have 4, need 11 total)
- [ ] 2×20 pin header for RP E1 — (already have 2)

**Priority 4 — PCB fabrication**
- [ ] 4-layer PCB, 100×80mm, 10pcs — JLCPCB ~£30-50

---

## Next Steps

1. **Today:** Order Red Pitaya STEMlab 125-14 Gen 2
2. **This week:** Place Digi-Key/LCSC order for V5-specific ICs (~£15-20)
3. **Next week:** PCB layout in KiCad v5
4. **Week 3:** Submit for fabrication, order remaining passives
5. **Week 4:** Assembly, power-on, bring-up

---

## Design Files

| File | Status | Notes |
|------|--------|-------|
| `turboquant_v5/hardware/schematics/` | 🟡 In Progress | Main project directory |
| `digital.kicad_sch` | 🟢 Updated | 74HCT595 confirmed |
| `power.kicad_sch` | 🟢 Updated | LM7805 DPAK confirmed |
| `analog.kicad_sch` | 🔴 Needs redraw | PE4259→DG408, ADL5610→OPA1641 |
| `tx_switch.kicad_sch` | 🔴 Needs creation | 8× IRF830 + protection |
| `turboquant_mux_lna_v5.kicad_sch` | 🟢 Updated | Title/rev set to v5.0 |

---

*Consolidated: April 21, 2026*
*Previous versions: v3 (archived), v4 (superseded)*
