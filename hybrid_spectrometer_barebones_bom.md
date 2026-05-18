# Barebones Hybrid Soil Spectrometer — Complete Order Sheet
*From-scratch build. Assumes zero tools, zero parts, zero experience.*
*Target: Order today, build next weekend, test in a pot.*

---

## 📦 PART 1: ELECTRONICS BILL OF MATERIALS

### Core Boards (Dev boards = no SMD soldering needed)
| # | Item | Qty | Spec | Supplier | Est. Price | Why |
|---|------|-----|------|----------|-----------|-----|
| 1 | **STM32 Nucleo-H743ZI2** | 1 | STM32H743, Arduino-compatible, built-in ST-Link debugger | Farnell/CPC: `Nucleo-H743ZI2` | £20 | 480 MHz, 1 MSPS ADC, no external programmer needed |
| 2 | **ESP32-S3-DevKitC-1** | 1 | N8R8, 8MB flash + 8MB PSRAM | The Pi Hut / Amazon | £9.50 | WiFi + Bluetooth, later add LoRa |
| 3 | **AD9833 DDS Module** | 1 | Breakout board, SPI, 0–12.5 MHz | AliExpress / Amazon | £3 | Clean sine generation, no analog hackery |
| 4 | **E22-900M22S LoRa Module** | 1 | SX1262, 868 MHz, UART/SPI | AliExpress | £8 | 10 km range, low power |
| 5 | **RFM95W LoRa Module** | 1 | SX1276, 868 MHz, SPI | The Pi Hut | £9.60 | **Backup** — better Arduino library support |

**Subtotal core: ~£50**

### Analog Front-End (Breadboard + through-hole only)
| # | Item | Qty | Spec | Supplier | Est. Price | Why |
|---|------|-----|------|----------|-----------|-----|
| 6 | **OPA1641 DIP-8** | 2 | Low-noise JFET op-amp, 5 nV/√Hz | Farnell/CPC | £3 each | TIA + buffer, DIP = no SMD |
| 7 | **LM358 DIP-8** | 2 | General-purpose dual op-amp | Any | £0.50 | Backup / second channel experiments |
| 8 | **Breadboard** | 3 | Half-size, 400 tie-points, adhesive back | Amazon (3-pack) | £5 | One for analog, one for digital, one spare |
| 9 | **Dupont wires** | 2 sets | M-M + M-F, 20 cm, 40-pin each | Amazon | £4 | Prototyping connections |
| 10 | **Hook-up wire** | 1 | 22 AWG stranded, 10 m, multicolour | CPC / Amazon | £4 | Solid breadboard connections |
| 11 | **Pin headers** | 2 strips | 2.54 mm, 1×40, male + female | Amazon | £2 | Breakouts, modules |
| 12 | **Resistor kit** | 1 | 1/4W, 1%, E12 series, 10–1 MΩ, 400 pcs | Amazon | £5 | Every value you'll need |
| 13 | **Capacitor kit** | 1 | Ceramic 100 pF–100 nF + electrolytic 1–100 µF | Amazon | £4 | Decoupling, filtering |
| 14 | **Potentiometer** | 2 | 10 kΩ linear, trimmer or panel mount | Any | £1 | Adjustable gain experiments |
| 15 | **Toggle switch** | 2 | SPDT, breadboard-friendly | Any | £1 | Gain switching (1k/10k later) |

**Subtotal analog: ~£30**

### Power & Cables
| # | Item | Qty | Spec | Supplier | Est. Price |
|---|------|-----|------|----------|-----------|
| 16 | **USB-C cable** | 2 | Data + power (not charge-only!) | Amazon | £6 |
| 17 | **USB wall charger** | 2 | 5V 2A, or use phone chargers | You have | £0 |
| 18 | **Jumper wires (thick)** | 1 | 22 AWG solid core, multicolour, 30 m | Amazon | £5 |
| 19 | **Battery holder** | 1 | 18650 × 1, with leads | Amazon | £1 |
| 20 | **18650 battery** | 1 | 3.7V, 2600 mAh, protected | Amazon | £5 |

**Subtotal power: ~£17**

### Electrodes & Mechanical
| # | Item | Qty | Spec | Supplier | Est. Price |
|---|------|-----|------|----------|-----------|
| 21 | **Stainless steel rod** | 4 | M6 × 150 mm, A2 or 316 | Screwfix / hardware store | £4 |
| 22 | **Jubilee clips** | 4 | 8–16 mm | Screwfix | £1 |
| 23 | **Electrical tape** | 1 | PVC, black | Any | £1 |
| 24 | **Cable ties** | 1 pack | 100 mm, assorted | Any | £2 |
| 25 | **Heat shrink tubing** | 1 | Assorted diameters, 3:1, black | Amazon | £3 |
| 26 | **Project box** | 1 | IP65, 100×100×50 mm, ABS | Amazon / CPC | £5 |
| 27 | **Gland / grommet** | 2 | PG7, for cable entry into box | Amazon | £2 |
| 28 | **Pot + compost** | 1 | 2 L pot, multi-purpose compost | Garden centre / Tesco | £4 |

**Subtotal mechanical: ~£22**

---

## 🔧 PART 2: TOOLS (Zero Assumption)

### Absolute Minimum (Buy These)
| # | Item | What to Buy | Where | Est. Price |
|---|------|-------------|-------|-----------|
| T1 | **Soldering iron — temperature controlled** | Pinecil v2 (USB-C, 65W) OR TS100 | The Pi Hut / AliExpress | £25–35 |
| T2 | **Solder — leaded, 0.8 mm** | 63/37, flux-cored, 100 g | Amazon | £8 |
| T3 | **Flux pen** | No-clean, for stubborn joints | Amazon | £5 |
| T4 | **Multimeter** | Auto-ranging, continuity beep | Amazon (Aneng AN8008) | £15 |
| T5 | **Wire strippers** | Auto-adjusting 10–24 AWG | Amazon | £8 |
| T6 | **Flush cutters** | Precision diagonal cutters | Amazon / CPC | £5 |
| T7 | **Tweezers** | Fine point, ESD-safe, straight + curved | Amazon (2-pack) | £5 |
| T8 | **Third hand / PCB holder** | Panavise Jr. or cheap helping hands | Amazon | £15 |
| T9 | **Screwdriver set** | Phillips + flat, precision | Any | £5 |
| T10 | **Hacksaw + junior hacksaw** | For cutting electrodes | Screwfix / B&Q | £8 |
| T11 | **File set** | 6-piece needle files | Amazon | £6 |
| T12 | **Hot glue gun** | For strain relief, temp mounting | Amazon | £5 |
| T13 | **USB-to-UART bridge** | CP2102 or CH340 module | Amazon / The Pi Hut | £3 |

**Subtotal tools: ~£110**

### Optional But Recommended
| # | Item | What to Buy | Est. Price |
|---|------|-------------|-----------|
| T14 | **Hot air rework station** | Quick 861DW or Atten | £60 |
| T15 | **Magnifying lamp** | Desk lamp + 2.5× lens | £20 |
| T16 | **Silicone soldering mat** | Magnetic, A3 size | £10 |
| T17 | **Brass tip cleaner** | Hakko 599B or wool | £5 |
| T18 | **Bench PSU** | Korad KA3005D 0–30V 0–5A | £45 |

**Subtotal optional: ~£140**

---

## 💰 GRAND TOTALS

| Scenario | Cost | What's Included |
|----------|------|-----------------|
| **Bare minimum** | **~£200** | Everything to build + test in a pot |
| **Comfortable build** | **~£260** | Above + hot air, magnifier, mat, bench PSU |
| **With spare LoRa + parts** | **~£290** | Above + RFM95W backup + extra passives |

**If you already have:** soldering iron, multimeter, breadboard → subtract £50–80

---

## 🛒 ORDERING STRATEGY

### Order Today (UK Stock — Arrives Tomorrow/Friday)
| Supplier | Items | Cost |
|----------|-------|------|
| **The Pi Hut** | ESP32-S3, Pinecil, LoRa | £45 |
| **Amazon UK** | Breadboards, wires, tools, multimeter, resistors, caps | £90 |
| **Farnell/CPC** | Nucleo-H743, OPA1641 | £25 |
| **Screwfix (click + collect)** | M6 rods, files, hacksaw, jubilee clips | £15 |
| **Garden centre / Tesco** | Pot + compost | £4 |

**Total: ~£180**

### Order Today (AliExpress — Arrives in 7–14 Days, Save ~£20)
| Supplier | Items | Cost |
|----------|-------|------|
| **AliExpress** | AD9833, E22 LoRa, extra modules | £20 |
| **Everything else** from UK suppliers above | | £160 |

**Total: ~£180** (same price, but AliExpress parts arrive later)

---

## ✅ ORDER CHECKLIST

Copy this into your notes app, tick as you order:

### Electronics
- [ ] Nucleo-H743ZI2 × 1
- [ ] ESP32-S3-DevKitC-1 × 1
- [ ] AD9833 module × 1
- [ ] E22-900M22S or RFM95W × 1
- [ ] OPA1641 DIP-8 × 2
- [ ] Breadboard × 3
- [ ] Dupont wires (M-M + M-F)
- [ ] Resistor kit
- [ ] Capacitor kit
- [ ] Pin headers
- [ ] Potentiometer 10 kΩ × 2
- [ ] Toggle switch × 2
- [ ] USB-C cable × 2
- [ ] 18650 battery + holder × 1

### Tools
- [ ] Pinecil / TS100 soldering iron
- [ ] Solder 63/37 0.8 mm
- [ ] Flux pen
- [ ] Multimeter (Aneng AN8008)
- [ ] Wire strippers
- [ ] Flush cutters
- [ ] Tweezers (2-pack)
- [ ] Third hand / PCB holder
- [ ] Screwdriver set
- [ ] Hacksaw + junior hacksaw
- [ ] File set
- [ ] Hot glue gun
- [ ] USB-to-UART bridge

### Mechanical
- [ ] M6 stainless rod × 4
- [ ] Jubilee clips × 4
- [ ] Electrical tape
- [ ] Cable ties
- [ ] Heat shrink tubing
- [ ] IP65 project box
- [ ] Cable gland × 2
- [ ] Pot + compost

---

## 🚚 PRIORITY SHIPPING

If you want to build **this weekend**, order **today before 15:00** from:
- The Pi Hut (next-day DPD)
- Amazon Prime (same-day/next-day)
- CPC/Farnell (next-day if ordered early)

AliExpress parts won't arrive in time — order them now for next month's build.

---

*Generated: 2026-05-07*
*Saved to: `hybrid_spectrometer_barebones_bom.md`*
