# Complete Digi-Key Order — TurboQuant V5 Build

**Date:** 2026-04-21
**Project:** TurboQuant MUX/LNA Board V5 + Red Pitaya + Assembly Tools
**Status:** Nothing ordered yet — this is the master list

---

## Phase 1: Red Pitaya (Order Direct — Not Digi-Key)

| Item | Spec | Supplier | Part # | Qty | Cost | Link |
|------|------|----------|--------|-----|------|------|
| STEMlab 125-14 Gen 2 | 2×ADC/DAC 125MSa/s 14-bit, Zynq 7010 | Red Pitaya | — | 1 | **£250.00** | <https://redpitaya.com/product/stemlab-125-14/> |
| SD Card 32GB | Class 10, for OS image | Amazon / Local | — | 1 | £8.00 | — |
| USB-C Cable 1m | 3A power + data | Amazon / Local | — | 1 | £5.00 | — |
| Ethernet Cable 2m | Cat 6, for host connection | Amazon / Local | — | 1 | £4.00 | — |

**Subtotal Phase 1:** £267.00

---

## Phase 2: PCB Components (Digi-Key)

### Priority ICs — Order First (Longest Lead / Most Critical)

| Digi-Key Part # | Manufacturer | MPN | Description | Qty | Unit £ | Line £ | Notes |
|-----------------|--------------|-----|-------------|-----|--------|--------|-------|
| DG408DY-T1-GE3CT-ND | Vishay | DG408DY-T1-E3 | 8:1 MUX, 100V, SOIC-16 | 3 | £2.50 | £7.50 | 2 for board + 1 spare |
| 296-1572-5-ND | TI | SN74HCT595DR | Shift reg, TTL, SOIC-16 | 3 | £0.40 | £1.20 | 1 for board + 2 spares |
| IRF830PBF-ND | Vishay | IRF830PBF | NMOS, 500V, 4.5A, TO-220 | 10 | £0.80 | £8.00 | 8 for board + 2 spares |
| 296-27891-5-ND | TI | OPA1641AID | Op-amp, low-noise, SOIC-8 | 4 | £1.50 | £6.00 | 2 for board + 2 spares |
| LM7805MPX/NOPBCT-ND | TI | LM7805MPX/NOPB | LDO 5V, DPAK (TO-252) | 3 | £0.50 | £1.50 | 1 for board + 2 spares |
| AMS1117-3.3CT-ND | AMS | AMS1117-3.3 | LDO 3.3V, SOT-223 | 3 | £0.20 | £0.60 | 1 for board + 2 spares |
| MF-NSMF200-2CT-ND | Bourns | MF-NSMF200-2 | Polyfuse, 2A, 1206 | 3 | £0.15 | £0.45 | 1 for board + 2 spares |
| SS34-E3/57TCT-ND | Vishay | SS34 | Schottky, 40V, 3A, SMA | 3 | £0.25 | £0.75 | 1 for board + 2 spares |
| SMAJ15A-E3/61CT-ND | Vishay | SMAJ15A | TVS, 15V, 400W, SMA | 3 | £0.20 | £0.60 | 1 for board + 2 spares |
| BZX84C12LT1GOSCT-ND | ON Semi | BZX84C12LT1G | Zener, 12V, 500mW, SOD-323 | 12 | £0.05 | £0.60 | 8 for board + 4 spares |
| BSS138-7-FCT-ND | Diodes Inc | BSS138-7-F | NMOS, 50V, SOT-23 | 15 | £0.13 | £1.95 | 10 for board + 5 spares |

**Priority ICs subtotal:** £29.15

---

### Passives (Digi-Key) — Order in Bulk Packs

| Digi-Key Part # | Description | Value | Package | Qty | Unit £ | Line £ |
|-----------------|-------------|-------|---------|-----|--------|--------|
| 311-10.0KHRCT-ND | Resistor, 1% | 10kΩ | 0603 | 100 | £0.01 | £1.00 |
| 311-100HRCT-ND | Resistor, 1% | 100Ω | 0603 | 100 | £0.01 | £1.00 |
| 311-1.00KCRCT-ND | Resistor, 1% | 1kΩ | 0805 | 100 | £0.01 | £1.00 |
| 311-1.00KLRCT-ND | Resistor, 1% | 1kΩ | 1206 | 50 | £0.02 | £1.00 |
| 311-9.09KCRCT-ND | Resistor, 1% | 9.09kΩ | 0805 | 50 | £0.01 | £0.50 |
| 490-GRM188R71H104KA01DCT-ND | Cap, X7R, 50V | 100nF | 0603 | 100 | £0.01 | £1.00 |
| 490-GRM21BR71H104KA01LCT-ND | Cap, X7R, 50V | 100nF | 0805 | 50 | £0.01 | £0.50 |
| 490-GRM21BR61C106KE15LCT-ND | Cap, X5R, 16V | 10µF | 0805 | 50 | £0.01 | £0.50 |
| 490-GRM21BR61A106KE19LCT-ND | Cap, X5R, 10V | 10µF | 0805 | 50 | £0.01 | £0.50 |
| P1234-ND | Cap, electrolytic | 100µF, 25V | Radial 6.3mm | 5 | £0.30 | £1.50 |

**Passives subtotal:** £8.00

---

### Connectors & Mechanical (Digi-Key)

| Digi-Key Part # | Description | Qty | Unit £ | Line £ |
|-----------------|-------------|-----|--------|--------|
| 132134-11-ND | SMA vertical jack (Amphenol) | 15 | £2.00 | £30.00 |
| TSW-106-07-G-S-ND | Header, 1×6, 2.54mm | 2 | £0.30 | £0.60 |
| TSW-102-07-G-S-ND | Header, 1×2, 2.54mm | 2 | £0.15 | £0.30 |
| S1011EC-40-ND | Header, 2×20, 2.54mm (for RP E1) | 2 | £2.40 | £4.80 |
| 277-1725656-ND | Terminal block, 2-pin, 5.08mm | 3 | £0.50 | £1.50 |
| 36-24443-ND | Standoff, M3, 10mm | 10 | £0.25 | £2.50 |
| 732-5318-ND | SMA edge-mount (for RP) | 4 | £1.85 | £7.40 |

**Connectors subtotal:** £47.10

---

### PCB Fabrication (JLCPCB — Not Digi-Key)

| Item | Spec | Qty | Cost |
|------|------|-----|------|
| 4-layer PCB, 100×80mm | 1.6mm, 1oz Cu, ENIG | 10 | ~£35.00 |
| SMT stencil | 0.12mm stainless | 1 | ~£8.00 |

**PCB subtotal:** £43.00

---

## Phase 3: Soldering & Assembly Tools (Digi-Key + Elsewhere)

### From Digi-Key

| Digi-Key Part # | Description | Qty | Unit £ | Line £ | Notes |
|-----------------|-------------|-----|--------|--------|-------|
| T18-D16 | Hakko T18-D16 tip, chisel 1.6mm | 2 | £5.00 | £10.00 | For THT + SMD |
| T18-I | Hakko T18-I tip, conical | 1 | £5.00 | £5.00 | Fine SMD work |
| 82-415-8 | Kester 63/37 solder, 0.8mm, 500g | 1 | £25.00 | £25.00 | Good flow, leaded |
| 83-1000-0955 | Kester 951 flux pen, no-clean | 2 | £8.00 | £16.00 | Essential for SMD |
| 83-3000-0000 | Desoldering braid, 2.0mm, 1.5m | 2 | £5.00 | £10.00 | For mistakes |
| 1528-1570 | Precision tweezers, ESD-safe, set of 6 | 1 | £12.00 | £12.00 | SMD placement |
| 1528-2228 | Helping hands + magnifier | 1 | £15.00 | £15.00 | Assembly aid |
| 501-1434 | Chip Quik SMD removal alloy | 1 | £8.00 | £8.00 | For desoldering ICs |
| SMDTCLP-1 | SMD test clips, set of 10 | 1 | £12.00 | £12.00 | Signal probing |
| 501-1436 | Kapton tape, 5mm, for reflow masking | 1 | £4.00 | £4.00 | Protect connectors |

**Digi-Key tools subtotal:** £117.00

### From Amazon / eBay / Local (Better Value)

| Item | Recommended | Est. £ | Where |
|------|-------------|--------|-------|
| **Oscilloscope** | PicoScope 2206B (50 MHz, 4-ch, 12-bit) | £350 | Amazon / PicoTech |
| **HV pulser** | MD1210 + IRF830 totem-pole DIY or eval board | £20-100 | Digi-Key / eBay |
| **Soldering station** | Hakko FX-888D or KSger T12 | £80-120 | Amazon / eBay |
| **Hot plate / preheater** | Miniware MHP30 or 300W hot plate | £40-80 | Amazon |
| **USB microscope** | Andonstar AD208, 1080p | £50-80 | Amazon |
| **Digital multimeter** | Aneng AN8008 or Uni-T UT139C | £25-40 | Amazon |
| **Solder paste** | Chip Quik SMD291AX, Sn63/Pb37, 35g | £15 | Amazon |
| **Solder wick + flux + alcohol** | 99% isopropyl alcohol, 500ml + wipes | £10 | Pharmacy / Amazon |
| **ESD mat + wrist strap** | 600×500mm mat + grounded strap | £15 | Amazon |
| **Flush cutters** | Engineer NK-15 or Knipex 78 61 125 | £12 | Amazon |
| **Wire stripper** | Knipex 12 40 200 | £15 | Amazon |
| **Third hand (heavy duty)** | Panavise or similar PCB holder | £25 | Amazon |

**Off-Digi-Key tools subtotal:** £647-707 (depending on scope choice)

---

## Order Summary

| Phase | Items | Est. Cost |
|-------|-------|-----------|
| **Red Pitaya + accessories** | Core platform | **£267** |
| **Digi-Key PCB components** | All ICs, passives, connectors | **£84** |
| **PCB fabrication (JLCPCB)** | 10 boards + stencil | **£43** |
| **Digi-Key soldering tools** | Tips, solder, flux, tweezers, etc. | **£117** |
| **PicoScope + bench tools (Amazon)** | 2206B + station + hot plate + microscope + multimeter | **£647-707** |
| | | |
| **TOTAL** | | **£1,041-1,101** |

---

## Recommended Order Sequence

### Today (Priority)
1. ✅ **Red Pitaya STEMlab 125-14 Gen 2** — order direct from redpitaya.com
2. ✅ **Digi-Key cart** — all V5 ICs + passives + connectors (Priority section above)
   - Target: place order for next-day / 2-day shipping

### This Week
3. **JLCPCB** — send v5 PCB files for fabrication (after layout complete)
4. **Amazon** — soldering station, hot plate, microscope, multimeter

### Next Week (After PCBs arrive)
5. **Amazon / eBay** — oscilloscope (if not already owned)
6. **Local** — isopropyl alcohol, solder paste (shorter shelf life, buy fresh)

---

## Digi-Key BOM Upload

To upload this to Digi-Key BOM Manager:
1. Go to <https://www.digikey.co.uk/en/resources/bom-manager>
2. Create new BOM
3. Paste the Priority ICs table (Digi-Key Part #, Qty)
4. Add passives and connectors

### Quick-Paste List for Digi-Key Cart

```
DG408DY-T1-GE3CT-ND,3
296-1572-5-ND,3
IRF830PBF-ND,10
296-27891-5-ND,4
LM7805MPX/NOPBCT-ND,3
AMS1117-3.3CT-ND,3
MF-NSMF200-2CT-ND,3
SS34-E3/57TCT-ND,3
SMAJ15A-E3/61CT-ND,3
BZX84C12LT1GOSCT-ND,12
BSS138-7-FCT-ND,15
132134-11-ND,15
TSW-106-07-G-S-ND,2
TSW-102-07-G-S-ND,2
S1011EC-40-ND,2
277-1725656-ND,3
36-24443-ND,10
732-5318-ND,4
```

---

## Notes

1. **No prior orders placed** — this list is complete and self-contained.
2. **Quantity strategy:** Ordered spares for all active ICs (2-3× board requirement). Passives in bulk packs of 50-100.
3. **Soldering approach:** Hand-solder THT (IRF830, connectors) + hot-plate reflow for SMD (MUX, LNA, shift register, passives).
4. **Oscilloscope:** If budget is tight, start with a £40-50 pocket scope (FNIRSI) for basic bring-up. Upgrade to Rigol later if needed.
5. **Red Pitaya lead time:** 3-5 days standard shipping. Order today to have it this week.

---

*Generated: April 21, 2026*
*For: TurboQuant V5 complete build*
