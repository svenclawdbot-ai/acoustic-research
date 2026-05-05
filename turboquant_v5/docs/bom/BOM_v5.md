# TurboQuant v5 - Bill of Materials (BOM)

**Board:** TurboQuant MUX/LNA v5  
**Date:** April 9, 2026  
**Revision:** 5.0  
**Quantity:** 1 board

---

## Power Section

| Ref | Qty | Description | Manufacturer | Part Number | Package | DigiKey | Mouser | LCSC | Unit Price | Notes |
|-----|-----|-------------|--------------|-------------|---------|---------|--------|------|------------|-------|
| F1 | 1 | Polyfuse, 2A, 1206 | Bourns | MF-NSMF200-2 | 1206 | MF-NSMF200-2CT-ND | 652-MF-NSMF200-2 | C3699 | $0.15 | Resettable fuse |
| D1 | 1 | Schottky, 40V, 3A | Vishay | SS34 | SMA | SS34-E3/57TCT-ND | 625-SS34-E3/57T | C8598 | $0.25 | Reverse polarity protection |
| D2 | 1 | TVS, 15V, 400W | Vishay | SMAJ15A | SMA | SMAJ15A-E3/61CT-ND | 625-SMAJ15A-E3/61 | C5141131 | $0.20 | Transient protection |
| U1 | 1 | LDO, 5V, 1A, DPAK | TI | LM7805MP | TO-252 | LM7805MPX/NOPBCT-ND | 926-LM7805MPX/NOPB | C58016 | $0.50 | Thermal vias required |
| U2 | 1 | LDO, 3.3V, 1A | AMS | AMS1117-3.3 | SOT-223 | AMS1117-3.3CT-ND | 621-AMS1117-3.3 | C6186 | $0.20 | |
| C1 | 1 | Cap, 100µF, 25V, electrolytic | Panasonic | EEU-FR1E101 | Radial 6.3mm | P1234-ND | - | C43850 | $0.30 | Input bulk |
| C2 | 1 | Cap, 100nF, 50V, X7R | Murata | GRM21BR71H104KA01L | 0805 | 490-GRM21BR71H104KA01LCT-ND | 81-GRM21BR71H104KA1L | C440198 | $0.05 | Input decoupling |
| C3 | 1 | Cap, 10µF, 16V, X5R | Murata | GRM21BR61C106KE15L | 0805 | 490-GRM21BR61C106KE15LCT-ND | 81-GRM21BR61C106KE15L | C440198 | $0.10 | 5V output |
| C4 | 1 | Cap, 100nF, 50V, X7R | Murata | GRM21BR71H104KA01L | 0805 | 490-GRM21BR71H104KA01LCT-ND | 81-GRM21BR71H104KA1L | C440198 | $0.05 | 5V decoupling |
| C5 | 1 | Cap, 10µF, 10V, X5R | Murata | GRM21BR61A106KE19L | 0805 | 490-GRM21BR61A106KE19LCT-ND | 81-GRM21BR61A106KE19L | C440198 | $0.10 | 3.3V output |
| C6 | 1 | Cap, 100nF, 50V, X7R | Murata | GRM21BR71H104KA01L | 0805 | 490-GRM21BR71H104KA01LCT-ND | 81-GRM21BR71H104KA1L | C440198 | $0.05 | 3.3V decoupling |
| J1 | 1 | Terminal block, 2-pin, 5.08mm | Phoenix Contact | 1725656 | 5.08mm | 277-1725656-ND | 651-1725656 | C8465 | $0.50 | 12V input |

**Power Section Subtotal:** ~$2.95

---

## Digital Control Section

| Ref | Qty | Description | Manufacturer | Part Number | Package | DigiKey | Mouser | LCSC | Unit Price | Notes |
|-----|-----|-------------|--------------|-------------|---------|---------|--------|------|------------|-------|
| U3 | 1 | Shift Register, 8-bit, TTL input | TI | SN74HCT595DR | SOIC-16 | 296-1572-5-ND | 595-SN74HCT595DR | C132142 | $0.40 | KEY CHANGE: HCT for 3.3V |
| C7 | 1 | Cap, 100nF, 50V, X7R | Murata | GRM188R71H104KA01D | 0603 | 490-GRM188R71H104KA01DCT-ND | 81-GRM188R71H104KA01D | C14663 | $0.05 | VCC decoupling |
| R1-R5 | 5 | Resistor, 10kΩ, 1% | Yageo | RC0603FR-0710KL | 0603 | 311-10.0KHRCT-ND | 603-RC0603FR-0710KL | C25804 | $0.01 | Pull-downs |

**Digital Section Subtotal:** ~$0.50

---

## Analog MUX Section (100V)

| Ref | Qty | Description | Manufacturer | Part Number | Package | DigiKey | Mouser | LCSC | Unit Price | Notes |
|-----|-----|-------------|--------------|-------------|---------|---------|--------|------|------------|-------|
| U4, U5 | 2 | Analog MUX, 8:1, 100V | Vishay | DG408DY-T1-E3 | SOIC-16 | DG408DY-T1-GE3CT-ND | 84-DG408DY-T1-GE3 | C115553 | $2.50 | KEY CHANGE: 100V capable |
| R6-R13 | 8 | Resistor, 10kΩ, 1% | Yageo | RC0603FR-0710KL | 0603 | 311-10.0KHRCT-ND | 603-RC0603FR-0710KL | C25804 | $0.01 | MUX address pull-downs |
| C8, C9 | 2 | Cap, 100nF, 50V, X7R | Murata | GRM188R71H104KA01D | 0603 | 490-GRM188R71H104KA01DCT-ND | 81-GRM188R71H104KA01D | C14663 | $0.05 | MUX decoupling |

**MUX Section Subtotal:** ~$5.30

---

## LNA Section

| Ref | Qty | Description | Manufacturer | Part Number | Package | DigiKey | Mouser | LCSC | Unit Price | Notes |
|-----|-----|-------------|--------------|-------------|---------|---------|--------|------|------------|-------|
| U6, U7 | 2 | Op-Amp, low-noise, JFET input | TI | OPA1641AID | SOIC-8 | 296-27891-5-ND | 595-OPA1641AID | C55823 | $1.50 | Low distortion |
| R14-R17 | 4 | Resistor, 1kΩ, 1%, 0805 | Yageo | RC0805FR-071KL | 0805 | 311-1.00KCRCT-ND | 603-RC0805FR-071KL | C17513 | $0.01 | Gain resistors Rg |
| R18-R21 | 4 | Resistor, 9.09kΩ, 1%, 0805 | Yageo | RC0805FR-079K09L | 0805 | 311-9.09KCRCT-ND | 603-RC0805FR-079K09L | C17475 | $0.01 | Gain resistors Rf |
| C10-C13 | 4 | Cap, 100nF, 50V, X7R | Murata | GRM188R71H104KA01D | 0603 | 490-GRM188R71H104KA01DCT-ND | 81-GRM188R71H104KA01D | C14663 | $0.05 | Power decoupling |

**LNA Section Subtotal:** ~$3.20

---

## TX Switch Section (100V)

| Ref | Qty | Description | Manufacturer | Part Number | Package | DigiKey | Mouser | LCSC | Unit Price | Notes |
|-----|-----|-------------|--------------|-------------|---------|---------|--------|------|------------|-------|
| Q1-Q8 | 8 | MOSFET, N-channel, 500V, 4.5A | Vishay | IRF830 | TO-220 | IRF830PBF-ND | 844-IRF830PBF | C99 | $0.80 | HV switches |
| R22-R29 | 8 | Resistor, 100Ω, 1%, 0603 | Yageo | RC0603FR-07100RL | 0603 | 311-100HRCT-ND | 603-RC0603FR-07100RL | C22775 | $0.01 | Gate series |
| R30-R37 | 8 | Resistor, 10kΩ, 1%, 0603 | Yageo | RC0603FR-0710KL | 0603 | 311-10.0KHRCT-ND | 603-RC0603FR-0710KL | C25804 | $0.01 | Gate pull-down |
| R38-R45 | 8 | Resistor, 1kΩ, 1%, 1206 | Yageo | RC1206FR-071KL | 1206 | 311-1.00KLRCT-ND | 603-RC1206FR-071KL | C114393 | $0.02 | Current limit |
| Z1-Z8 | 8 | Zener, 12V, 500mW | ON Semi | BZX84C12LT1G | SOD-323 | BZX84C12LT1GOSCT-ND | 863-BZX84C12LT1G | C32576 | $0.05 | Gate protection |

**TX Switch Section Subtotal:** ~$7.60

---

## Connectors

| Ref | Qty | Description | Manufacturer | Part Number | Package | DigiKey | Mouser | LCSC | Unit Price | Notes |
|-----|-----|-------------|--------------|-------------|---------|---------|--------|------|------------|-------|
| J2 | 1 | Header, 1x6, 2.54mm | Amphenol | TSW-106-07-G-S | Through-hole | TSW-106-07-G-S-ND | 649-TSW-106-07-G-S | C35419 | $0.30 | Control signals |
| J3 | 1 | Header, 1x2, 2.54mm | Amphenol | TSW-102-07-G-S | Through-hole | TSW-102-07-G-S-ND | 649-TSW-102-07-G-S | C35419 | $0.15 | 3.3V output |
| J4 | 1 | SMA, vertical, jack | Amphenol | 132134-11 | - | 132134-11-ND | 523-132134-11 | C496552 | $2.00 | TX_IN |
| J5-J12 | 8 | SMA, vertical, jack | Amphenol | 132134-11 | - | 132134-11-ND | 523-132134-11 | C496552 | $2.00 | TX_OUT (x8) |
| J13, J14 | 2 | SMA, vertical, jack | Amphenol | 132134-11 | - | 132134-11-ND | 523-132134-11 | C496552 | $2.00 | RX0, RX1 |

**Connectors Subtotal:** ~$22.45

---

## Mechanical

| Ref | Qty | Description | Manufacturer | Part Number | Package | DigiKey | Mouser | LCSC | Unit Price | Notes |
|-----|-----|-------------|--------------|-------------|---------|---------|--------|------|------------|-------|
| H1-H4 | 4 | Mounting hole | N/A | M3 | 3.2mm | - | - | - | $0.00 | PCB mounting |
| - | 4 | Standoff, M3, 10mm | Keystone | 24443 | - | 36-24443-ND | 534-24443 | C2904713 | $0.25 | PCB spacers |

**Mechanical Subtotal:** ~$1.00

---

## Cost Summary

| Section | Components | Cost (USD) |
|---------|------------|------------|
| Power | 12 | $2.95 |
| Digital Control | 7 | $0.50 |
| Analog MUX (2×) | 11 | $5.30 |
| LNA (2×) | 10 | $3.20 |
| TX Switch (8×) | 32 | $7.60 |
| Connectors | 13 | $22.45 |
| Mechanical | 4 | $1.00 |
| **Total** | **89** | **~$43.00** |

---

## Procurement Strategy

### Priority 1: Long Lead Time / Critical
Order first (may take 2-4 weeks):
- DG408 MUX (U4, U5) - specialty HV part
- IRF830 MOSFETs (Q1-Q8) - HV transistors
- SMA connectors (J4-J14) - expensive, order early

### Priority 2: Standard Components
Order with PCB (1 week lead time):
- All resistors, capacitors
- 74HCT595
- LM7805, AMS1117
- OPA1641

### Alternative Sources

**DigiKey:** Best for US, fast shipping, good stock
**Mouser:** Good for Europe, competitive pricing
**LCSC:** Best for Asia (China), lowest cost, 1-2 week shipping

### Quantity Pricing

| Quantity | Est. Total Cost | Per Board |
|----------|-----------------|-----------|
| 1 board | $43 | $43 |
| 5 boards | $172 | $34.40 |
| 10 boards | $301 | $30.10 |

**Recommendation:** Order components for 5-10 boards to get quantity discounts and have spares.

---

## Notes for Assembly

### Hand Assembly Priority
1. **Power section first** - verify voltages before other components
2. **Digital section** - 74HCT595 and pull-downs
3. **Analog section** - MUX and LNA (ESD sensitive)
4. **TX switches last** - HV section, most critical

### SMT Assembly (if using PCBA service)
- All components are standard SMT (0603, 0805, SOIC)
- No BGA or fine-pitch QFN
- TO-220/TO-252 can be hand-soldered after SMT

### Testing Sequence
1. Visual inspection
2. Power-on (check 5V, 3.3V)
3. Digital control (shift register)
4. Analog MUX (signal routing)
5. LNA (gain measurement)
6. TX switches (HV capability)
7. Full system integration

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| v4 | Mar 30 | Initial design with 74HC595, CD4051B |
| v5 | Apr 9 | Updated to 74HCT595, DG408, LM7805 DPAK |

---

*Generated: April 9, 2026*
