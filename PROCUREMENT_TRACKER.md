# Master Procurement Tracker

**Last Updated:** 2026-05-04
**Projects Tracked:** ShearWave Test Rig, Red Pitaya Mux Board, Transducer Fabrication

---

## Legend

| Status | Icon | Meaning |
|--------|------|---------|
| Not Started | ⚪ | Identified but not ordered |
| Ordered | 🟡 | Order placed, awaiting shipment |
| Shipped | 🟠 | In transit |
| Received | 🟢 | Delivered and inspected |
| Cancelled | 🔴 | No longer needed |
| Issue | ⚠️ | Problem with order/item |

---

## PROJECT 1: ShearWave Test Rig

**Target Completion:** April 15, 2026 (may need updating)
**Total Budget:** £200-250
**Status:** 🔴 **STALLED** — awaiting order placement

### Priority 1 — Critical / Long Lead Time

| # | Item | Spec | Supplier | Part # | Qty | Cost | Status | Order Date | ETA | Notes |
|---|------|------|----------|--------|-----|------|--------|------------|-----|-------|
| 1.1 | Piezo Stack | 10×10×20mm, 150V, 12μm | PiezoDrive | PD0S020 | 1 | £32.00 | ⚪ | - | - | 1 week lead |
| 1.2 | HV DC-DC | 12V→150V, 2W boost | AliExpress | "High voltage boost 150V" | 2 | £24.00 | ⚪ | - | - | 2 week lead, order 2× |
| 1.3 | ESP32-S3 | DevKitC-1, WROOM-1 | RS/Farnell | ESP32-S3-DevKitC-1 | 1 | £8.00 | ⚪ | - | - | Stock item |
| 1.4 | ADXL355 Module | ±2g, 20-bit, SPI | Digi-Key | ADXL355Z | 1 | £15.00 | ⚪ | - | - | Stock item |

**Subtotal:** £79.00 | **Ordered:** £0.00 | **Received:** £0.00

### Priority 2 — Electronics (HV Driver)

| # | Item | Spec | Supplier | Part # | Qty | Cost | Status | Order Date | ETA | Notes |
|---|------|------|----------|--------|-----|------|--------|------------|-----|-------|
| 2.1 | Gate Driver IC | TC4427CPA, DIP-8 | RS | 542-771 | 1 | £2.50 | ⚪ | - | - | |
| 2.2 | Power MOSFET | IRF830, TO-220 | RS | 540-063 | 1 | £3.20 | ⚪ | - | - | |
| 2.3 | Gate Zener | BZX55-C15, 15V | RS | 247-8919 | 1 | £0.10 | ⚪ | - | - | CRITICAL — protects MOSFET |
| 2.4 | TVS Diode | P6KE200A, 200V | RS | 628-9786 | 1 | £0.30 | ⚪ | - | - | CRITICAL — piezo kickback |
| 2.5 | Current Sense R | 0.5Ω, 2W, 1% | RS | 146-988 | 1 | £0.20 | ⚪ | - | - | |
| 2.6 | LM7805 Regulator | 5V, TO-220 | RS | 298-8514 | 1 | £0.80 | ⚪ | - | - | |
| 2.7 | Electrolytic Caps | 10µF, 250V | RS | 711-2396 | 2 | £1.00 | ⚪ | - | - | |
| 2.8 | Ceramic Caps | 100nF, 50V | RS | 169-7148 | 5 | £0.50 | ⚪ | - | - | |
| 2.9 | Resistors (assorted) | 10Ω, 1kΩ, 10kΩ | RS | Assorted | 10 | £0.60 | ⚪ | - | - | |
| 2.10 | Diodes 1N4007 | 1kV, 1A | RS | 628-9220 | 2 | £0.30 | ⚪ | - | - | |
| 2.11 | LEDs | 3mm, any color | RS | 228-6282 | 2 | £0.30 | ⚪ | - | - | |
| 2.12 | Fuse + Holder | 1A fast, PCB mount | RS | 189-4821 | 1 | £0.50 | ⚪ | - | - | |

**Subtotal:** £10.80 | **Ordered:** £0.00 | **Received:** £0.00

### Priority 2b — Interconnect & Hardware

| # | Item | Spec | Supplier | Qty | Cost | Status | Order Date | ETA | Notes |
|---|------|------|----------|-----|------|--------|------------|-----|-------|
| 2.13 | HV Coax Cable | RG58, 2.5kV, 2m | RS | 360-971 | 1 | £4.50 | ⚪ | - | - | |
| 2.14 | BNC Connectors | Panel mount | RS | 467-596 | 2 | £5.60 | ⚪ | - | - | |
| 2.15 | PCB Prototype | 50×70mm stripboard | RS | 206-2130 | 2 | £6.00 | ⚪ | - | - | |
| 2.16 | Pin Headers | 40-way, 2.54mm | RS | 251-8576 | 2 | £4.00 | ⚪ | - | - | |
| 2.17 | Enclosure | 80×50×25mm ABS | RS | 548-676 | 1 | £5.00 | ⚪ | - | - | |
| 2.18 | Heat Sink | TO-220, 19°C/W | RS | 189-553 | 1 | £2.00 | ⚪ | - | - | |
| 2.19 | Thermal Pad | TO-220 size | RS | 789-2727 | 1 | £0.80 | ⚪ | - | - | |
| 2.20 | Cable Grommets | 6mm ID rubber | RS | 495-862 | 4 | £2.00 | ⚪ | - | - | |

**Subtotal:** £29.90 | **Ordered:** £0.00 | **Received:** £0.00

### Priority 3 — Mechanical / Printed Parts

| # | Item | Spec | Qty | Cost | Status | Order Date | ETA | Notes |
|---|------|------|-----|------|--------|------------|-----|-------|
| 3.1 | Phone Cradle | PETG, 3D printed | 1 | £2.00 | ⚪ | - | - | |
| 3.2 | Piezo Housing | PETG, 3D printed | 1 | £3.00 | ⚪ | - | - | |
| 3.3 | Positioning Rail | PETG, 3D printed | 1 | £2.00 | ⚪ | - | - | |
| 3.4 | Coupling Stand | TPU (flexible), 3D printed | 1 | £3.00 | ⚪ | - | - | |
| 3.5 | Aluminum Strip | 60×15×2mm, 6061 | 1 | £2.00 | ⚪ | - | - | Metal Supermarket |
| 3.6 | Compression Spring | 0.5 N/mm, OD 8mm | 2 | £5.60 | ⚪ | - | - | |
| 3.7 | Brass Tip | 8mm × 10mm cylinder | 1 | £1.50 | ⚪ | - | - | eBay/Model shop |
| 3.8 | Silicone Sheet | 50×50×1mm, Shore A30 | 1 | £5.00 | ⚪ | - | - | Amazon/Smooth-On |
| 3.9 | M3 Hardware | Screws, nuts, washers | Assorted | £3.00 | ⚪ | - | - | Hardware store |

**Subtotal:** £27.10 | **Ordered:** £0.00 | **Received:** £0.00

### Priority 4 — Phantom Materials

| # | Item | Spec | Qty | Cost | Status | Order Date | ETA | Notes |
|---|------|------|-----|------|--------|------------|-----|-------|
| 4.1 | Agar Powder | Bacteriological grade, 500g | 1 | £12.00 | ⚪ | - | - | |
| 4.2 | Graphite Powder | Conductive filler, 250g | 1 | £8.00 | ⚪ | - | - | |
| 4.3 | Glycerin | USP grade, 500ml | 1 | £5.00 | ⚪ | - | - | |
| 4.4 | Silicone Mold | Cylindrical, 50mm × 100mm | 2 | £10.00 | ⚪ | - | - | |
| 4.5 | Distilled Water | 5L | 1 | £3.00 | ⚪ | - | - | |

**Subtotal:** £38.00 | **Ordered:** £0.00 | **Received:** £0.00

**Project 1 Total: £184.60** | **Ordered: £0.00** | **Received: £0.00** | **Remaining: £184.60**

---

## PROJECT 2: Red Pitaya Mux Board

**Target:** 8-element ultrasound array
**Status:** 🟡 **IN PROGRESS** — Digi-Key order placed

### Order 1 — Red Pitaya (Core Platform)

| # | Item | Spec | Supplier | Cost | Status | Order Date | ETA | Notes |
|---|------|------|----------|------|--------|------------|-----|-------|
| 2.1.1 | STEMlab 125-14 Gen 2 | 2×ADC/DAC 125MSa/s 14-bit, Zynq 7010 | redpitaya.com | £250.00 | ⚪ | - | - | 3-5 day lead if in stock |

**Subtotal:** £250.00 | **Ordered:** £0.00 | **Received:** £0.00

### Order 2 — Mux Board Components (Digi-Key)

**Order Reference:** Digi-Key UK, placed 28/03/2026
**Order Total:** £68.26 (inc VAT & shipping)
**Expected Delivery:** March 31 — April 2, 2026

| # | Item | Spec | Part # | Qty | Cost | Status | Order Date | ETA | Notes |
|---|------|------|--------|-----|------|--------|------------|-----|-------|
| 2.2.1 | 74HC595 | 8-bit shift register, DIP-16 | 296-1600-5-ND | 2 | £1.04 | 🟢 | 2026-03-28 | Delivered | |
| 2.2.2 | CD4051BE | 8:1 analog mux, DIP-16 | 296-2057-5-ND | 3 | £1.74 | 🟢 | 2026-03-28 | Delivered | |
| 2.2.3 | AD8332 | Dual LNA/VGA (0-48 dB) | AD8332ARUZ-ND | 1 | £11.85 | 🟢 | 2026-03-28 | Delivered | TSSOP-20 |
| 2.2.4 | BSS138 | N-channel MOSFET, SOT-23, 50V | BSS138-7-FCT-ND | 10 | £1.30 | 🟢 | 2026-03-28 | Delivered | |
| 2.2.5 | LM7805 | 5V regulator, TO-220 | LM7805CT-ND | 2 | £1.56 | 🟢 | 2026-03-28 | Delivered | |
| 2.2.6 | AMS1117-3.3 | 3.3V LDO, SOT-223 | AMS1117-3.3CT-ND | 2 | £1.04 | 🟢 | 2026-03-28 | Delivered | |
| 2.2.7 | BAV99 | Dual series diode, SOT-23 | BAV99-7-F-ND | 10 | £1.10 | 🟢 | 2026-03-28 | Delivered | |
| 2.2.8 | 10kΩ resistor | 1/4W, 1%, 0805 | 311-10.0KFRCT-ND | 50 | £1.00 | 🟢 | 2026-03-28 | Delivered | |
| 2.2.9 | 100Ω resistor | 1/4W, 1%, 0805 | 311-100FRCT-ND | 50 | £1.00 | 🟢 | 2026-03-28 | Delivered | |
| 2.2.10 | 1kΩ resistor | 1/4W, 1%, 0805 | 311-1.00KFRCT-ND | 50 | £1.00 | 🟢 | 2026-03-28 | Delivered | |
| 2.2.11 | 100nF ceramic | 50V, 0805 | 311-100nFCT-ND | 50 | £1.50 | 🟢 | 2026-03-28 | Delivered | |
| 2.2.12 | 10µF electrolytic | 25V | Various | 5 | £0.75 | 🟢 | 2026-03-28 | Delivered | |
| 2.2.13 | 1µF ceramic | 16V, 0805 | 311-1.0uFCT-ND | 20 | £1.60 | 🟢 | 2026-03-28 | Delivered | |
| 2.2.14 | SMA edge-mount | 50Ω, PCB | 732-5318-ND | 4 | £7.40 | 🟢 | 2026-03-28 | Delivered | |
| 2.2.15 | 2×20 pin header | 2.54mm, for RP GPIO | S1011EC-40-ND | 2 | £2.40 | 🟢 | 2026-03-28 | Delivered | |
| 2.2.16 | 2-pin screw terminal | 5.08mm, power input | ED10561-ND | 2 | £0.90 | 🟢 | 2026-03-28 | Delivered | |
| 2.2.17 | Prototype PCB | 100×70mm, double-sided | 377-2095-ND | 2 | £7.70 | 🟢 | 2026-03-28 | Delivered | |

**Subtotal:** £68.26 | **Ordered:** £68.26 | **Received:** £68.26

**Project 2 Total: £318.26** | **Ordered: £68.26** | **Received: £68.26** | **Remaining: £250.00**

### Action Items
- [ ] Order Red Pitaya STEMlab 125-14 Gen 2 (blocking)
- [x] Download Red Pitaya OS image
- [ ] Flash SD card and test basic I/O
- [ ] Build mux board prototype

---

## PROJECT 3: Transducer Fabrication

**Date:** 2026-03-18
**Purpose:** Build 3.5 MHz focused transducer + establish home workshop
**Status:** 🔴 **NOT STARTED** — procurement pending

### Phase 1: Immediate (Week 1) — Critical Tools & Materials

| # | Item | Spec | Qty | Cost | Supplier | Status | Order Date | ETA | Notes |
|---|------|------|-----|------|----------|--------|------------|-----|-------|
| 3.1.1 | Vacuum chamber + pump | 2-gallon, 3 CFM | 1 | £150 | Amazon/Harbor Freight | ⚪ | - | - | Critical for degassing |
| 3.1.2 | PZT-5H Disc | 19mm diameter × 0.64mm, gold electroded | 3 | £60 | PI Ceramic / Steminc | ⚪ | - | - | Order 2–3 suppliers |
| 3.1.3 | Digital scale | 0.01g resolution, 500g | 1 | £20 | Amazon / RS | ⚪ | - | - | |
| 3.1.4 | Digital calipers | 0.01mm resolution, 150mm | 1 | £25 | Amazon | ⚪ | - | - | |
| 3.1.5 | Soldering station | 50W, temperature controlled | 1 | £40 | Amazon | ⚪ | - | - | |
| 3.1.6 | Tungsten powder | 5-10 μm, 99.9% | 100g | £35 | eBay / Scientific | ⚪ | - | - | |
| 3.1.7 | Epo-Tek 301 | Two-part, low viscosity | 100ml | £30 | Epotek / RS | ⚪ | - | - | |

**Subtotal:** £360 | **Ordered:** £0.00 | **Received:** £0.00

### Phase 2: Core Build (Week 2)

| # | Item | Spec | Qty | Cost | Supplier | Status | Order Date | ETA | Notes |
|---|------|------|-----|------|----------|--------|------------|-----|-------|
| 3.2.1 | Alumina powder | Al₂O₃, 1-5 μm | 50g | £15 | Ceramics supplier | ⚪ | - | - | |
| 3.2.2 | Brass tube | 20mm ID × 25mm OD × 30mm L | 3 | £15 | Metal supplier | ⚪ | - | - | |
| 3.2.3 | PMMA lens / rod | 25mm diameter (for lens) | 1 | £25 | Edmund Optics / Thorlabs | ⚪ | - | - | Or buy pre-made lens |
| 3.2.4 | RG174/U Coax | 50Ω, 1.5m | 3 | £12 | RS / Farnell | ⚪ | - | - | |
| 3.2.5 | SMA connectors | Panel mount, solder bucket | 6 | £12 | RS / Farnell | ⚪ | - | - | |
| 3.2.6 | Inductors | 6.5 μH, 5% | 5 | £5 | Digi-Key | ⚪ | - | - | |
| 3.2.7 | DIY Spin coater | DVD motor + controller | 1 | £80 | Build from parts | ⚪ | - | - | For matching layer |
| 3.2.8 | Copper tape | Conductive adhesive, 25mm wide | 1 roll | £8 | Amazon / RS | ⚪ | - | - | |
| 3.2.9 | Epoxy potting compound | Electronics grade | 100ml | £15 | RS Components | ⚪ | - | - | |

**Subtotal:** £187 | **Ordered:** £0.00 | **Received:** £0.00

### Phase 3: Testing (Week 3)

| # | Item | Spec | Qty | Cost | Supplier | Status | Order Date | ETA | Notes |
|---|------|------|-----|------|----------|--------|------------|-----|-------|
| 3.3.1 | Function generator | 25 MHz, arbitrary waveform | 1 | £80 | Rigol DG1022 (used eBay) | ⚪ | - | - | |
| 3.3.2 | USB oscilloscope | 50 MHz, 2-channel | 1 | £100 | Hantek 6022BE / Pico | ⚪ | - | - | Or use existing scope |
| 3.3.3 | BNC cables | 50Ω, various lengths | 1 set | £20 | Amazon | ⚪ | - | - | |
| 3.3.4 | BNC T-adapter | For testing | 1 | £5 | Amazon | ⚪ | - | - | |
| 3.3.5 | USB microscope | 200x, for inspection | 1 | £25 | Amazon | ⚪ | - | - | |
| 3.3.6 | Hot plate | For epoxy curing | 1 | £30 | Amazon / Lab supply | ⚪ | - | - | |
| 3.3.7 | Helping hands | With magnifier | 1 | £15 | Amazon | ⚪ | - | - | |
| 3.3.8 | Ultrasonic cleaner | 1L tank, for degreasing | 1 | £40 | Amazon | ⚪ | - | - | |
| 3.3.9 | Multimeter | True RMS, auto-ranging | 1 | £25 | Amazon / RS | ⚪ | - | - | |
| 3.3.10 | Heat gun | For shrink tubing | 1 | £20 | Amazon | ⚪ | - | - | |
| 3.3.11 | Third hand PCB holder | For soldering | 1 | £15 | Amazon | ⚪ | - | - | |
| 3.3.12 | Desoldering braid | For cleanup | 1 | £5 | RS | ⚪ | - | - | |
| 3.3.13 | Flush cutters | For component leads | 1 | £8 | Amazon | ⚪ | - | - | |
| 3.3.14 | Tweezers set | ESD-safe, various tips | 1 set | £12 | Amazon | ⚪ | - | - | |

**Subtotal:** £398 | **Ordered:** £0.00 | **Received:** £0.00

### Phase 4: Consumables

| # | Item | Spec | Qty | Cost | Status | Order Date | ETA | Notes |
|---|------|------|-----|------|--------|------------|-----|-------|
| 3.4.1 | Isopropyl alcohol | 99%, cleaning | 1 L | £10 | Amazon / Pharmacy | ⚪ | - | - | |
| 3.4.2 | Acetone | For degreasing | 500ml | £8 | Hardware store | ⚪ | - | - | |
| 3.4.3 | Lint-free wipes | Electronics grade | 1 pack | £8 | Amazon | ⚪ | - | - | |
| 3.4.4 | Nitrile gloves | Powder-free, medium | 1 box | £12 | Amazon | ⚪ | - | - | |
| 3.4.5 | Mixing cups | 30ml, disposable | 50 | £5 | Amazon | ⚪ | - | - | |
| 3.4.6 | Wooden stirrers | For epoxy | 100 | £3 | Amazon | ⚪ | - | - | |
| 3.4.7 | Syringes | 10ml, blunt needle | 10 | £8 | Amazon | ⚪ | - | - | |
| 3.4.8 | Release agent | Silicone spray | 1 | £8 | RS | ⚪ | - | - | |
| 3.4.9 | Kapton tape | High temp, 25mm | 1 roll | £10 | Amazon | ⚪ | - | - | |
| 3.4.10 | Heat shrink tubing | Assorted sizes | 1 set | £8 | Amazon | ⚪ | - | - | |
| 3.4.11 | Solder | Lead-free, 0.7mm | 100g | £8 | RS | ⚪ | - | - | |
| 3.4.12 | Flux pen | No-clean | 1 | £5 | RS | ⚪ | - | - | |

**Subtotal:** £103 | **Ordered:** £0.00 | **Received:** £0.00

**Project 3 Total: £1,048** | **Ordered: £0.00** | **Received: £0.00** | **Remaining: £1,048**

### Phase 5: Optional Upgrades (Future)

| # | Item | Spec | Cost | Status | Notes |
|---|------|------|------|--------|-------|
| 3.5.1 | Used bench scope | 100 MHz, 2-ch | £200 | ⚪ | If USB scope inadequate |
| 3.5.2 | Impedance analyzer | 1 MHz - 100 MHz | £500 | ⚪ | Full characterization |
| 3.5.3 | Hydrophone | Needle type, 1-20 MHz | £800 | ⚪ | Absolute pressure calibration |

**Subtotal:** £1,500 | **Ordered:** £0.00 | **Received:** £0.00

---

## GRAND SUMMARY

| Project | Total | Ordered | Received | Remaining | Status |
|---------|-------|---------|----------|-----------|--------|
| ShearWave Test Rig | £184.60 | £0.00 | £0.00 | £184.60 | 🔴 Stalled |
| Red Pitaya Mux Board | £318.26 | £68.26 | £68.26 | £250.00 | 🟡 In Progress |
| Transducer Fabrication | £1,048.00 | £0.00 | £0.00 | £1,048.00 | 🔴 Not Started |
| **TOTAL** | **£1,550.86** | **£68.26** | **£68.26** | **£1,482.60** | |

---

## SUPPLIER QUICK LINKS

| Supplier | URL | Used For |
|----------|-----|----------|
| RS Components | https://uk.rs-online.com | Electronics, passives |
| Digi-Key UK | https://www.digikey.co.uk | ICs, components |
| Farnell | https://uk.farnell.com | Electronics |
| Red Pitaya | https://redpitaya.com | STEMlab board |
| PiezoDrive | https://www.piezodrive.com | Piezo actuators |
| PI Ceramic | https://www.piceramic.com | PZT crystals |
| Edmund Optics | https://www.edmundoptics.com | Optical/lens components |
| Amazon UK | https://www.amazon.co.uk | Tools, general |
| AliExpress | https://www.aliexpress.com | HV supplies, budget items |
| eBay UK | https://www.ebay.co.uk | Used test equipment |
| Epotek | https://www.epotek.com | Acoustical epoxies |

---

## HOW TO UPDATE THIS TRACKER

When you order or receive items:

1. Find the item in the table above
2. Update the **Status** column:
   - ⚪ Not Started → 🟡 Ordered
   - 🟡 Ordered → 🟠 Shipped (when you get tracking)
   - 🟠 Shipped → 🟢 Received (when it arrives)
   - Any → ⚠️ Issue (if there's a problem)
3. Fill in **Order Date** and **ETA**
4. Update the summary totals
5. Update **Last Updated** at the top of the file

### Weekly Review Checklist

- [ ] Check for items that should have arrived but haven't
- [ ] Update ETAs from tracking emails
- [ ] Identify items ready to order (all dependencies met)
- [ ] Update project status based on blocker resolution
- [ ] Review budget vs. actual spend

---

## PROCUREMENT SCHEDULE

### This Week (May 4–10, 2026)
- [ ] **URGENT:** Order Red Pitaya STEMlab (Project 2 blocker)
- [ ] Review ShearWave Priority 1 items — place order if still needed

### Next 2 Weeks (May 11–24, 2026)
- [ ] Order Transducer Phase 1 items (if proceeding)
- [ ] Red Pitaya delivery → start mux board build

### Month 2 (June 2026)
- [ ] Transducer Phase 2 orders
- [ ] Complete Red Pitaya integration

---

*Created: 2026-05-04*
*Next Review: 2026-05-11*
