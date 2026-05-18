# Hybrid Soil Spectrometer — Manufacturing Tools List

*Project: STM32 Lock-in Spectrometer + ESP32 LoRa Node*
*Scope: What you need to build, test, and deploy*

---

## 🔴 ESSENTIAL — Cannot Build Without These

### Electronics Assembly
| Tool | Purpose | What to Buy | Est. Cost |
|------|---------|-------------|-----------|
| **Soldering iron** | Solder TQFP/STM32, passives, headers | Pinecil v2 (USB-C, 65W) or KSGER T12 | £25–50 |
| **Solder** | Leaded 63/37, 0.8 mm, flux-cored | 100 g reel | £8 |
| **Flux** | Clean joints on tiny pads | No-clean flux pen (Kester 951) | £5 |
| **Desoldering braid** | Fix mistakes | 2 mm copper wick | £3 |
| **Wire strippers** | 22–28 AWG for signal wires | Engineer PA-09 or cheap adjustables | £8–25 |
| **Flush cutters** | Trim leads, cut headers | Hakko CHP-170 or equivalent | £5 |
| **Tweezers** | Place 0603 passives, ICs | ESD-safe fine point (curved + straight pair) | £8 |
| **Third hand / PCB holder** | Hold board while soldering | Panavise Jr. or cheap helping hands | £15–35 |

### Testing & Measurement
| Tool | Purpose | What to Buy | Est. Cost |
|------|---------|-------------|-----------|
| **Multimeter** | Check continuity, voltage, resistance | Aneng AN8008 or Uni-T UT139C | £15–25 |
| **USB-to-UART bridge** | Flash/debug STM32 and ESP32 | CP2102 or FT232RL module | £3–5 |
| **Logic analyzer (8-ch)** | Debug SPI/I2C/UART timing | Saleae Logic 8 clone (DSLogic) or genuine | £10–300 |

### Power
| Tool | Purpose | What to Buy | Est. Cost |
|------|---------|-------------|-----------|
| **Bench PSU (variable)** | Power board during bring-up, 0–30V / 0–5A | Korad KA3005D or Ruideng DPS5020 | £40–60 |
| **USB power meter** | Check current draw, debug power issues | AVHzY CT-3 or YZXStudio | £15–25 |

**Essential subtotal: ~£150–200**

---

## 🟡 RECOMMENDED — Makes the Build Pleasant

### Prototyping
| Tool | Purpose | What to Buy | Est. Cost |
|------|---------|-------------|-----------|
| **Breadboards** | Test analog front-end before soldering | 2× half-size (400 tie), 1× full-size | £8 |
| **Jumper wires (M-M, M-F, F-F)** | Prototype connections | 3× 40-pin assortments | £6 |
| **Hook-up wire (22 AWG, stranded, assorted)** | Solid connections on breadboard | 10 m spools: red/black/yellow/blue/green | £10 |
| **Pin headers (male + female)** | Breakouts, connectors | 2.54 mm: 1×40 strips, assorted | £5 |
| **IC sockets / ZIF** | Test chips without soldering | 2× TQFP-48 ZIF adapters for STM32 | £8 |

### Soldering Aids
| Tool | Purpose | What to Buy | Est. Cost |
|------|---------|-------------|-----------|
| **Brass sponge / tip cleaner** | Keep iron tip clean | Hakko 599B or brass wool | £5 |
| **Tip tinner / restorer** | Revive oxidised tips | Tip Tinner (Lead-free) | £4 |
| **Soldering mat (silicone, magnetic)** | Organise parts, prevent shorts | A4 or A3 silicone mat | £8 |
| **Magnifying lamp / headset** | See 0.5 mm pitch pins | Headband magnifier (2.5×/5×) or desk lamp | £10–25 |
| **Hot air rework station** | Remove/replace QFP chips, reflow passives | Quick 861DW or Atten ST-8802D | £50–120 |
| **Solder paste + stencil (optional)** | If doing SMD reflow instead of hand-soldering | Sn63Pb37 paste 50 g, syringe | £12 |
| **Preheater / hot plate** | Even reflow of bottom-side ground planes | Cheap hot plate or coffee mug warmer | £15–30 |

### Mechanical
| Tool | Purpose | What to Buy | Est. Cost |
|------|---------|-------------|-----------|
| **Hacksaw + junior hacksaw** | Cut stainless steel electrodes to length | Any hardware store set | £10 |
| **File set (needle + flat)** | Deburr cut metal | 6-piece needle file set | £6 |
| **Drill / Dremel** | Make holes in enclosure | Cordless drill or rotary tool | £20–40 |
| **Heat shrink tubing** | Waterproof wire joints | Assorted pack (3:1, black) | £5 |
| **Epoxy / potting compound** | Waterproof electronics | JB Weld Marine or conformal coating | £8 |

**Recommended subtotal: ~£150–250**

---

## 🟢 NICE TO HAVE — For Advanced/Debug Work

| Tool | Purpose | What to Buy | Est. Cost |
|------|---------|-------------|-----------|
| **Oscilloscope (2-ch, 50 MHz+)** | View analog waveforms, debug TIA output, check DDS | Rigol DS1054Z or FNIRSI 1013D (budget) | £60–350 |
| **Function generator** | Test TIA independently of DDS | FeelTech FY3200S or JDS6600 | £30–60 |
| **LCR meter** | Characterise passives, verify electrode capacitance | DER EE DE-5000 or Mastech MS5308 | £30–60 |
| **Thermal camera / IR thermometer** | Check for hot spots, TIA stability | Flir One (phone) or cheap IR gun | £20–200 |
| **3D printer** | Custom enclosures, electrode mounts | Ender 3 V2 or similar | £150–200 |
| **CNC / laser cutter** | Precise electrode spacing jigs | Not worth buying — use drill + template |
| **Network analyser (VNA)** | Characterise electrode impedance across frequency | NanoVNA v2 (3 GHz) | £50–80 |

**Nice-to-have subtotal: £300–900**

---

## 📦 SHOPPING STRATEGY

### Phase 1: Minimum Viable (£80–100)
Order only essentials. Breadboard everything. No soldering of STM32 needed if you buy a dev board with headers.

| Priority | Items |
|----------|-------|
| 1 | Pinecil + solder + flux |
| 2 | Multimeter + UART bridge |
| 3 | Breadboards + jumper wires |
| 4 | Wire strippers + flush cutters + tweezers |
| 5 | USB power meter |

### Phase 2: Comfortable Build (+£80–120)
Add recommended tools once you know you're committed.

| Priority | Items |
|----------|-------|
| 6 | Hot air station |
| 7 | Magnifying lamp |
| 8 | Bench PSU |
| 9 | Hook-up wire + headers |
| 10 | Soldering mat + brass sponge |

### Phase 3: Professional Finish (+£200–400)
If you're building multiple units or going to field deployment.

| Priority | Items |
|----------|-------|
| 11 | Oscilloscope |
| 12 | 3D printer (for enclosures) |
| 13 | VNA (for electrode characterisation) |
| 14 | LCR meter |

---

## 🛒 SUPPLIER LINKS (UK)

| Supplier | Best For | URL |
|----------|----------|-----|
| **CPC / Farnell** | Tools, passives, wire, bench PSU | cpc.farnell.com |
| **RS Components** | Professional tools, same-day | uk.rs-online.com |
| **The Pi Hut** | Pinecil, ESP32, modules | thepihut.com |
| **AliExpress** | Cheap clones: logic analyser, DPS5020, hot air | aliexpress.com |
| **Amazon UK** | Fast delivery: cutters, tweezers, breadboard | amazon.co.uk |
| **Banggood** | Hot air stations, oscilloscopes | banggood.com |
| **Screwfix / B&Q** | Hacksaw, files, drill bits, epoxy | screwfix.com |
| **eBay UK** | Second-hand scope, bench PSU deals | ebay.co.uk |

---

## ✅ CHECKLIST — What Do You Already Own?

- [ ] Soldering iron (what type? temperature controlled?)
- [ ] Multimeter (auto-ranging? True RMS?)
- [ ] Wire strippers / flush cutters
- [ ] Tweezers (fine point?)
- [ ] Breadboards + jumper wires
- [ ] USB-to-UART adapter
- [ ] Bench PSU (variable voltage/current?)
- [ ] Oscilloscope (bandwidth? channels?)
- [ ] Hot air station
- [ ] 3D printer
- [ ] Hacksaw / drill / files

**Reply with what you have — I'll generate a personalised order list for what's missing.**

---

*Saved to workspace: tools needed for hybrid spectrometer build*
