# GlassHouse Tomatoes — Complete Order Sheet
*Order today, build this weekend, tomatoes monitored by Monday*
*Revised for ESP32-only v1.0 — no Nucleo, no LoRa (WiFi first)*

---

## 📦 PART 1: ELECTRONICS BILL OF MATERIALS

### Core Controller & Comms
| # | Item | Qty | Part Number / Search Term | Supplier | Est. Price | Link / Notes |
|---|------|-----|---------------------------|----------|-----------|--------------|
| 1 | **ESP32-S3-DevKitC-1-N8R8** | 1 | "ESP32-S3-DevKitC-1" or "ESP32-S3-DevKitC-1-N8R8" | [The Pi Hut](https://thepihut.com/) £10.50 | £10.50 | Dev board with USB-C, 8MB flash, 8MB PSRAM |
| | | | | [Amazon UK](https://www.amazon.co.uk/s?k=esp32-s3-devkitc-1) | £9–14 | Check seller ratings; avoid "ESP32-S3-DevKitC-1U" (different pinout) |
| 2 | **AD9833 DDS Module** | 1 | "AD9833 module SPI" | [Amazon UK](https://www.amazon.co.uk/s?k=AD9833+module) | £3.50 | Breakout with crystal; confirm 25 MHz MCLK |
| | | | | [AliExpress](https://www.aliexpress.com/wholesale?SearchText=AD9833+module) | £1.80 | 2–3 week delivery; buy 2 for spare |

**Subtotal core: ~£14**

### Analog Front-End
| # | Item | Qty | Part Number / Search Term | Supplier | Est. Price | Notes |
|---|------|-----|---------------------------|----------|-----------|-------|
| 3 | **OPA1641 DIP-8** | 1 | OPA1641AP | [Farnell UK](https://uk.farnell.com/) 3122209 | £2.80 | Low-noise JFET, 5 nV/√Hz. One is enough for v1 (TIA only). |
| | | | | [CPC UK](https://cpc.farnell.com/) SC12755 | £2.80 | Same stock pool as Farnell |
| | | | | [RS Components](https://uk.rs-online.com/) 738-0328 | £3.20 | Backup supplier |
| 4 | **LM358 DIP-8** | 1 | LM358N/NOPB | [CPC](https://cpc.farnell.com/) SC10504 | £0.45 | Cheap backup / buffer experiments |
| 5 | **Resistor kit** | 1 | "E12 1% 1/4W 400pcs" | [Amazon UK](https://www.amazon.co.uk/s?k=resistor+kit+e12+1%25+1%2F4w) | £5.00 | 10Ω–1MΩ. Must include: 100Ω, 1kΩ, 10kΩ, 100kΩ |
| 6 | **Capacitor kit** | 1 | "Ceramic + electrolytic capacitor kit" | [Amazon UK](https://www.amazon.co.uk/s?k=ceramic+capacitor+kit) | £4.50 | 100pF–100µF. Must include: 100nF (decoupling), 10µF (bulk) |
| 7 | **Potentiometer 10kΩ** | 1 | "3362P 10k trimmer" or panel mount | [Amazon UK](https://www.amazon.co.uk/s?k=10k+trimmer+potentiometer) | £0.80 | Optional — for gain tuning experiments |
| 8 | **Battery voltage divider** | 2× 100kΩ | Included in resistor kit above | — | £0.00 | 1% 100kΩ × 2 for battery monitor |
| 9 | **4.7kΩ pull-up** | 1 | Included in resistor kit | — | £0.00 | DS18B20 data line pull-up |

**Subtotal analog: ~£14**

### Temperature & Power
| # | Item | Qty | Part Number / Search Term | Supplier | Est. Price | Notes |
|---|------|-----|---------------------------|----------|-----------|-------|
| 10 | **DS18B20 temperature sensor** | 1 | DS18B20+PAR (waterproof probe) | [The Pi Hut](https://thepihut.com/) £4.00 | £4.00 | Get the **waterproof probe** version, not the bare TO-92. Stainless probe goes in soil. |
| | | | DS18B20+ (bare TO-92) | [CPC](https://cpc.farnell.com/) SC10437 | £1.80 | Cheaper but needs waterproofing yourself |
| 11 | **TP4056 charger module** | 1 | "TP4056 Type-C" or "TP4056 micro-USB" | [Amazon UK](https://www.amazon.co.uk/s?k=TP4056+charger+module) | £1.50 | 1A Li-ion charger with protection. Get **Type-C** version if possible. |
| | | | | [AliExpress](https://www.aliexpress.com/wholesale?SearchText=TP4056+type-c) | £0.80 | Buy 3–5 pack, you'll use them |
| 12 | **18650 battery holder** | 1 | "18650 battery holder single with leads" | [Amazon UK](https://www.amazon.co.uk/s?k=18650+battery+holder+leads) | £1.20 | With wire leads, not PCB mount |
| 13 | **18650 battery (protected)** | 1 | "18650 2600mAh protected" | [Amazon UK](https://www.amazon.co.uk/s?k=18650+protected+2600mah) | £5.50 | **Must be protected** (overcharge/discharge). Samsung 25R, LG MJ1, or Nitecore. |
| | | | | [The Pi Hut](https://thepihut.com/) | £6.00 | UK stock, guaranteed genuine |
| 14 | **HT7333 LDO regulator** | 1 | HT7333-A or AMS1117-3.3 | [Amazon UK](https://www.amazon.co.uk/s?k=AMS1117-3.3+module) | £1.50 | 3.3V LDO for clean analog power. AMS1117 module with caps is easiest. |
| 15 | **Schottky diode 1N5819** | 2 | 1N5819 or SS14 | [CPC](https://cpc.farnell.com/) SC10625 | £0.30 | Battery protection / reverse polarity. Or use TP4056 built-in protection. |

**Subtotal temp/power: ~£14**

### Prototyping Supplies
| # | Item | Qty | Part Number / Search Term | Supplier | Est. Price | Notes |
|---|------|-----|---------------------------|----------|-----------|-------|
| 16 | **Breadboard** | 2 | "Half-size breadboard 400 tie-points" | [Amazon UK](https://www.amazon.co.uk/s?k=breadboard+half+size) | £4.00 | 2-pack. One for analog, one for digital. |
| 17 | **Dupont jumper wires** | 2 sets | "Dupont line M-M + M-F 40pin" | [Amazon UK](https://www.amazon.co.uk/s?k=dupont+jumper+wires) | £3.50 | Male-Male + Male-Female. 20 cm length. |
| 18 | **Solid core hook-up wire** | 1 | "22 AWG solid core wire kit" | [Amazon UK](https://www.amazon.co.uk/s?k=22+awg+solid+core+wire) | £5.00 | Better than Dupont for permanent breadboard connections. |
| 19 | **Pin headers** | 1 strip | "2.54mm pin header 40pin male" | [Amazon UK](https://www.amazon.co.uk/s?k=pin+header+2.54+male) | £1.50 | Break off as needed. |
| 20 | **USB-C cable (data)** | 2 | "USB-C data cable 1m" | [Amazon UK](https://www.amazon.co.uk/s?k=usb+c+cable+data) | £6.00 | **Must support data**, not charge-only. Anker/Belkin reliable. |
| 21 | **USB-C wall charger 5V 2A** | 1 | Any phone charger | You have | £0.00 | Or buy: Anker Nano £10 |
| 22 | **Micro-USB cable** | 1 | If your TP4056 is micro-USB | [Amazon UK](https://www.amazon.co.uk/s?k=micro+usb+cable) | £3.00 | Only if TP4056 isn't Type-C |

**Subtotal prototyping: ~£23**

### Electrodes & Mechanical
| # | Item | Qty | Part Number / Search Term | Supplier | Est. Price | Notes |
|---|------|-----|---------------------------|----------|-----------|-------|
| 23 | **M6 stainless steel rod** | 4 | "M6 threaded rod A2 150mm" or "M6 studding" | [Screwfix](https://www.screwfix.com/) 17626 | £3.50 | A2 (304) or A4 (316). Cut to 100 mm with hacksaw. |
| | | | | [B&Q](https://www.diy.com/) | £4.00 | Also check local hardware store |
| 24 | **Jubilee clips / hose clamps** | 4 | "Jubilee clip 8-16mm" | [Screwfix](https://www.screwfix.com/) 86534 | £1.50 | Clamp wire to rod if not soldering. |
| 25 | **Heat shrink tubing** | 1 set | "Heat shrink tubing assortment 3:1" | [Amazon UK](https://www.amazon.co.uk/s?k=heat+shrink+tubing+assortment) | £3.50 | Waterproof electrode connections. Get adhesive-lined if possible. |
| 26 | **Electrical tape** | 1 | PVC insulating tape | [Screwfix](https://www.screwfix.com/) 94144 | £1.00 | Strain relief, temp insulation |
| 27 | **Project box** | 1 | "IP65 enclosure 100×100×50 ABS" | [Amazon UK](https://www.amazon.co.uk/s?k=ip65+enclosure+100x100x50) | £4.50 | Optional for breadboard stage. Needed for deployment. |
| 28 | **Cable gland PG7** | 2 | "PG7 cable gland nylon" | [Amazon UK](https://www.amazon.co.uk/s?k=pg7+cable+gland) | £1.50 | For electrode wires entering box. |
| 29 | **4-core cable** | 2m | "4-core alarm cable 0.5mm²" or "4-pair telephone cable" | [Screwfix](https://www.screwfix.com/) | £2.00 | Run from electrodes to electronics. 4 conductors for Wenner array. |
| 30 | **Grow bag + tomato plants** | 1 | Any garden centre | [B&Q](https://www.diy.com/) / local | £6.00 | Or existing glasshouse setup |

**Subtotal mechanical: ~£23**

---

## 🔧 PART 2: TOOLS, WORKSTATION & ANCILLARIES

*Everything you need if you're building from zero. If you already solder, you probably own 60% of this.*

### 2.1 Soldering Station
| # | Item | What to Buy | Supplier | Est. Price | Why This One |
|---|------|-------------|----------|-----------|--------------|
| T1 | **Soldering iron — portable, temperature controlled** | **Pinecil v2** (USB-C, 65W, 12–24V) | [The Pi Hut](https://thepihut.com/products/pinecil-smart-mini-portable-soldering-iron) | £30 | Best value portable iron. Heats to 350°C in 6s. USB-C or DC barrel input. Firmware upgradable. Tips cheap. |
| | | **TS100** (older, still good) | [Amazon UK](https://www.amazon.co.uk/s?k=ts100+soldering+iron) | £45 | Same tips as Pinecil. Slightly slower heat. |
| | | **FX888D** (bench station) | [Farnell](https://uk.farnell.com/) 2322170 | £95 | If you plan 10+ projects. Bulletproof. |
| T2 | **Soldering iron tip — conical 1.2mm** | Pinecil tip "B2" or TS-B2 | [The Pi Hut](https://thepihut.com/) £4 | £4 | Default tip is fine for DIP-8, breadboard wires. |
| T3 | **Soldering iron tip — chisel 2.4mm** | Pinecil tip "D24" or TS-D24 | [The Pi Hut](https://thepihut.com/) £4 | £4 | Better for soldering to stainless steel electrodes. More heat mass. |
| T4 | **Solder — leaded 63/37, 0.8mm, flux-cored** | "MG Chemicals 4890" or "Solder Wire 63/37" 100g | [Amazon UK](https://www.amazon.co.uk/s?k=63%2F37+solder+wire+0.8mm+100g) | £8 | 63/37 melts at 183°C — eutectic, no pasty range. Easier than lead-free. |
| T5 | **Solder — lead-free SAC305 (backup)** | "Lead-free solder 0.8mm" 50g | [Amazon UK](https://www.amazon.co.uk/s?k=lead+free+solder+0.8mm) | £5 | Required for anything that touches food/plants long-term. Higher melt (217°C). |
| T6 | **Flux pen — no-clean, rosin-based** | "Kester 951" or "Electronics flux pen" | [Amazon UK](https://www.amazon.co.uk/s?k=flux+pen+electronics) | £5 | Essential for soldering to stainless steel. Apply before heating. |
| T7 | **Flux paste — RMA, in tub** | "Amtech NC-559-V2" or "Kingbo RMA-218" 50g | [Amazon UK](https://www.amazon.co.uk/s?k=rma+flux+paste) | £6 | More flux than pen for big joints (battery holder, electrodes). |
| T8 | **Desoldering braid / solder wick** | "Soder-Wick 2.0mm" or generic 2.5mm 1.5m | [Amazon UK](https://www.amazon.co.uk/s?k=desoldering+braid) | £3 | Removes excess solder, fixes bridges. Dip in flux first. |
| T9 | **Solder sucker / desoldering pump** | "Engineer SS-02" or generic aluminium pump | [Amazon UK](https://www.amazon.co.uk/s?k=solder+sucker) | £5 | For removing through-hole parts. Pump, heat, release. |
| T10 | **Tip cleaner — brass wool** | "Hakko 599B" or generic brass shavings in tin | [Amazon UK](https://www.amazon.co.uk/s?k=brass+wool+tip+cleaner) | £5 | Better than wet sponge — no thermal shock to tip. |
| T11 | **Tip tinner / refresher** | "Tip Tinner" paste in tin | [Amazon UK](https://www.amazon.co.uk/s?k=tip+tinner) | £4 | Revives oxidised tips. Dip hot tip in paste. |

**Subtotal soldering: ~£79**

### 2.2 Cutting, Stripping & Shaping
| # | Item | What to Buy | Supplier | Est. Price | Notes |
|---|------|-------------|----------|-----------|-------|
| T12 | **Wire strippers — automatic, 10–24 AWG** | "Knipex 1240200" or "Irwin Vise-Grip" | [Amazon UK](https://www.amazon.co.uk/s?k=automatic+wire+stripper) | £12 | Auto-adjusts to wire size. Essential. |
| | | Budget option | [Amazon UK](https://www.amazon.co.uk/s?k=wire+stripper+tool) | £6 | OK for occasional use. |
| T13 | **Flush cutters / diagonal cutters** | "Knipex 7803125" or "Engineer NZ-12" | [Amazon UK](https://www.amazon.co.uk/s?k=flush+cutters) | £8 | Cuts flush to PCB. Don't use for steel — get separate for that. |
| T14 | **Heavy-duty side cutters** | "Knipex 7001160" or Stanley | [Amazon UK](https://www.amazon.co.uk/s?k=side+cutter+heavy+duty) | £10 | For cutting M6 rod, thick wire. Don't ruin your flush cutters. |
| T15 | **Hacksaw + junior hacksaw** | "Draper 300mm hacksaw" + junior | [Screwfix](https://www.screwfix.com/) 55326 | £8 | Junior hacksaw for cutting electrodes to length. |
| T16 | **Junior hacksaw blades** | Pack of 10 | [Screwfix](https://www.screwfix.com/) | £3 | Spare blades — stainless steel dulls them fast. |
| T17 | **File set — needle files, 6-piece** | "Draper 6pc needle file set" | [Amazon UK](https://www.amazon.co.uk/s?k=needle+file+set) | £6 | Deburr electrode ends after cutting. Round + flat essential. |
| T18 | **Wire brush (brass)** | Small brass brush | [Amazon UK](https://www.amazon.co.uk/s?k=brass+wire+brush) | £3 | Clean oxidation off stainless rod before soldering. |
| T19 | **Sandpaper assortment** | 120 / 240 / 400 grit, 10 sheets | [Amazon UK](https://www.amazon.co.uk/s?k=sandpaper+assortment) | £3 | Clean electrode surfaces, smooth cuts. |

**Subtotal cutting: ~£53**

### 2.3 Holding, Clamping & Magnification
| # | Item | What to Buy | Supplier | Est. Price | Notes |
|---|------|-------------|----------|-----------|-------|
| T20 | **Helping hands / third hand** | "Panavise Jr." or "QuadHands" with 4 arms | [Amazon UK](https://www.amazon.co.uk/s?k=helping+hands+soldering) | £15 | Heavy base, adjustable alligator clips. Worth the money. |
| | | Budget option: basic helping hands | [Amazon UK](https://www.amazon.co.uk/s?k=third+hand+soldering) | £8 | OK for light work. Base is often too light. |
| T21 | **Magnifying lamp / desk magnifier** | "Brightech LightView Pro" or "Daylight" 3-diopter LED | [Amazon UK](https://www.amazon.co.uk/s?k=magnifying+lamp+led) | £25 | Essential for checking solder joints, reading part numbers. |
| | | Budget: headband magnifier | [Amazon UK](https://www.amazon.co.uk/s?k=headband+magnifier) | £8 | Less convenient but portable. |
| T22 | **Tweezers — ESD-safe, fine point** | "Vetus ESD-11 straight + ESD-15 curved" 2-pack | [Amazon UK](https://www.amazon.co.uk/s?k=vetus+tweezers+esd) | £5 | Place small components, hold wires while soldering. |
| T23 | **Silicone soldering mat** | "Soldering mat magnetic 45×30cm" | [Amazon UK](https://www.amazon.co.uk/s?k=silicone+soldering+mat+magnetic) | £10 | Heat resistant to 500°C. Built-in compartments for screws/parts. Magnetic strips hold screws. |
| T24 | **Bench vice (small)** | "Draper 75mm bench vice" or jeweller's vice | [Amazon UK](https://www.amazon.co.uk/s?k=small+bench+vice) | £15 | Hold electrodes while cutting/filing. Clamp to table. |
| T25 | **Clamps — G-clamps or spring clamps** | "Spring clamps 50mm" 4-pack | [Amazon UK](https://www.amazon.co.uk/s?k=spring+clamps) | £5 | Hold boxes, cables, boards while working. |

**Subtotal holding: ~£75**

### 2.4 Test, Measurement & Debug
| # | Item | What to Buy | Supplier | Est. Price | Notes |
|---|------|-------------|----------|-----------|-------|
| T26 | **Multimeter — auto-ranging, true RMS** | **Aneng AN8008** or **KAIWEETS HT118A** | [Amazon UK](https://www.amazon.co.uk/s?k=aneng+an8008) | £15 | Auto-ranging, continuity beep, frequency, capacitance. Enough for this project. |
| | | Upgrade: **Uni-T UT139C** | [Amazon UK](https://www.amazon.co.uk/s?k=uni-t+ut139c) | £30 | Better accuracy, backlight, NCV detector. |
| T27 | **Multimeter probes — fine tip** | "Multimeter probes needle tip" | [Amazon UK](https://www.amazon.co.uk/s?k=multimeter+needle+tip+probes) | £5 | Fine tips for probing breadboard/DIP pins without shorts. |
| T28 | **Logic probe (optional)** | Simple LED logic probe | [Amazon UK](https://www.amazon.co.uk/s?k=logic+probe) | £5 | Quick 0/1 check on digital pins. Multimeter works too. |
| T29 | **USB-to-UART bridge** | "CP2102 module" or "CH340 module" | [Amazon UK](https://www.amazon.co.uk/s?k=cp2102+usb+uart) | £3 | If ESP32 USB port fails. Also useful for other projects. |
| T30 | **Jumper wires — silicone, assorted colours** | "Silicone jumper wire 22AWG 5m each colour" | [Amazon UK](https://www.amazon.co.uk/s?k=silicone+jumper+wire+22awg) | £8 | Better than PVC for breadboard — soft, flexible, heat resistant. |

**Subtotal test: ~£36**

### 2.5 Cleaning, Maintenance & Consumables
| # | Item | What to Buy | Supplier | Est. Price | Notes |
|---|------|-------------|----------|-----------|-------|
| T31 | **Isopropyl alcohol (IPA) 99.9%** | "IPA 99.9% 500ml" | [Amazon UK](https://www.amazon.co.uk/s?k=isopropyl+alcohol+99.9) | £6 | Cleans flux residue, degreases surfaces, cleans PCB. |
| T32 | **Cotton swabs / cleaning sticks** | "Precision cotton swabs 400pcs" (pointed + round) | [Amazon UK](https://www.amazon.co.uk/s?k=precision+cotton+swabs) | £3 | Apply IPA, clean small areas. Don't use cheap fluffy ones. |
| T33 | **Lint-free wipes** | "Kimtech wipes" or "Lens cleaning cloths" 100pk | [Amazon UK](https://www.amazon.co.uk/s?k=lint+free+wipes) | £4 | Clean flux without leaving fibres. |
| T34 | **Contact cleaner / DeoxIT** | "DeoxIT D5" or "Servisol Super 10" 200ml | [Amazon UK](https://www.amazon.co.uk/s?k=deoxit+d5) | £10 | Cleans switches, pots, battery contacts. Extends life. |
| T35 | **Hot glue gun + glue sticks** | "Stanley hot glue gun" + 12 sticks | [Amazon UK](https://www.amazon.co.uk/s?k=hot+glue+gun+stanley) | £6 | Strain relief, temp mounting, waterproofing cable entries. |
| T36 | **Epoxy resin / JB Weld** | "JB Weld Original" twin-tube | [Amazon UK](https://www.amazon.co.uk/s?k=jb+weld) | £6 | Permanent electrode-to-wire joints if soldering steel fails. |
| T37 | **Cable ties — assorted sizes** | "Cable ties 100mm + 200mm + 300mm" 300pk | [Amazon UK](https://www.amazon.co.uk/s?k=cable+ties+assorted) | £3 | Organise wiring, secure cables. |
| T38 | **Cable tie mounts + adhesive** | "Cable tie mounts self-adhesive" 50pk | [Amazon UK](https://www.amazon.co.uk/s?k=cable+tie+mounts) | £3 | Stick inside project box for tidy cable routing. |
| T39 | **Heat gun (for heat shrink)** | "Wagner HT1000" or "Einhell" 2000W | [Amazon UK](https://www.amazon.co.uk/s?k=heat+gun+2000w) | £15 | Far better than lighter for heat shrink. Also strips paint. |
| | | Budget: lighter or hair dryer | You have | £0 | Hair dryer on high works for small heat shrink. |
| T40 | **Thread-locking compound (Loctite)** | "Loctite 243 medium strength" 5ml | [Amazon UK](https://www.amazon.co.uk/s?k=loctite+243) | £5 | Prevents screws vibrating loose in project box. |
| T41 | **Silicone sealant / gasket maker** | "Clear RTV silicone" 80ml tube | [Amazon UK](https://www.amazon.co.uk/s?k=rtv+silicone+clear) | £4 | Waterproof cable gland entries, potting electronics. |
| T42 | **Label maker / tape** | "Dymo LetraTag" or sharpies + masking tape | [Amazon UK](https://www.amazon.co.uk/s?k=dymo+letratag) | £15 | Label nodes, electrodes, cables. Essential when you have 3+ nodes. |
| | | Budget: permanent marker + masking tape | [Amazon UK](https://www.amazon.co.uk/s?k=permanent+marker+masking+tape) | £3 | Low-tech, works fine. |

**Subtotal cleaning/consumables: ~£80**

### 2.6 Safety & PPE
| # | Item | What to Buy | Supplier | Est. Price | Notes |
|---|------|-------------|----------|-----------|-------|
| T43 | **Safety glasses** | "3M Virtua" or "Bollé Tracker" | [Amazon UK](https://www.amazon.co.uk/s?k=safety+glasses+3m) | £5 | Molten solder, clipped wires, flux splash. Wear them. |
| T44 | **Fume extractor / fan** | "Kotto fume extractor" or 120mm PC fan + carbon filter | [Amazon UK](https://www.amazon.co.uk/s?k=solder+fume+extractor) | £20 | Solder fumes are lead/rosin — not good to breathe. Open window + fan minimum. |
| | | Budget: desk fan + open window | You have | £0 | Minimum viable. |
| T45 | **Anti-static wrist strap** | "ESD wrist strap + grounding lead" | [Amazon UK](https://www.amazon.co.uk/s?k=esd+wrist+strap) | £4 | ESP32-S3 is ESD sensitive. Ground yourself before touching pins. |
| T46 | **Anti-static mat** | "ESD mat 30×40cm + grounding lead" | [Amazon UK](https://www.amazon.co.uk/s?k=esd+mat+30x40) | £10 | Work surface protection. Optional if careful. |
| T47 | **Nitrile gloves** | "Nitrile gloves 100pk medium" | [Amazon UK](https://www.amazon.co.uk/s?k=nitrile+gloves+100) | £5 | Flux, IPA, epoxy — keeps hands clean. |
| T48 | **Fire extinguisher / blanket** | "1kg ABC powder extinguisher" or fire blanket | [Amazon UK](https://www.amazon.co.uk/s?k=1kg+fire+extinguisher) | £12 | 18650 batteries can vent fire if shorted. Be prepared. |
| T49 | **First aid kit — burns** | "Burn dressing 10×10cm" + "Burn gel" | [Amazon UK](https://www.amazon.co.uk/s?k=burn+dressing) | £5 | Soldering iron at 350°C causes instant burns. |

**Subtotal safety: ~£56**

### 2.7 Organisation & Storage
| # | Item | What to Buy | Supplier | Est. Price | Notes |
|---|------|-------------|----------|-----------|-------|
| T50 | **Component storage box** | "Stackable component box 24 compartments" | [Amazon UK](https://www.amazon.co.uk/s?k=component+storage+box) | £8 | Sort resistors, caps, ICs. Label compartments. |
| T51 | **Small parts trays / dishes** | "Magnetic parts tray" or "Silicone parts tray" 4-pack | [Amazon UK](https://www.amazon.co.uk/s?k=magnetic+parts+tray) | £6 | Screws, nuts, cut resistor leads. Magnetic ones stick to vice. |
| T52 | **Project notebook** | "Rite in the Rain" or any waterproof notebook | [Amazon UK](https://www.amazon.co.uk/s?k=rite+in+the+rain+notebook) | £6 | Write down calibration values, wiring changes, observations. Invaluable. |
| T53 | **Digital callipers** | "Neiko digital callipers 150mm" or "Vernier digital" | [Amazon UK](https://www.amazon.co.uk/s?k=digital+callipers+150mm) | £12 | Measure electrode spacing (must be 50 mm ±1 mm). |
| T54 | **Torch / headlamp** | "LED headlamp USB rechargeable" | [Amazon UK](https://www.amazon.co.uk/s?k=led+headlamp+usb) | £8 | Glasshouse work, checking wiring in dark corners. |
| T55 | **Multi-tool / Swiss Army Knife** | "Leatherman Rev" or "Victorinox Hiker" | [Amazon UK](https://www.amazon.co.uk/s?k=leatherman+rev) | £40 | Wire stripper, knife, pliers, file — one tool for glasshouse trips. |
| | | Budget: basic multi-tool | [Amazon UK](https://www.amazon.co.uk/s?k=multi+tool) | £10 | Functional, not heirloom. |

**Subtotal organisation: ~£42**

---

## 💰 COMPLETE ORDER TOTALS

### Scenario A: Starting From Zero (No Tools)
| Category | Cost |
|----------|------|
| Electronics (node + spares) | £78 |
| Mechanical | £23 |
| Soldering station | £79 |
| Cutting/stripping | £53 |
| Holding/magnification | £75 |
| Test/measurement | £36 |
| Cleaning/consumables | £80 |
| Safety/PPE | £56 |
| Organisation | £42 |
| **GRAND TOTAL** | **£522** |

### Scenario B: Already Have Basic Tools (Multimeter, Iron, Cutters)
| Category | Cost |
|----------|------|
| Electronics (node + spares) | £78 |
| Mechanical | £23 |
| Missing tools & consumables | £120 |
| **TOTAL** | **£221** |

### Scenario C: Minimal Build (Tools Owned, No Extras)
| Category | Cost |
|----------|------|
| Core electronics | £44 |
| Mechanical | £15 |
| **MINIMAL TOTAL** | **£59** |

### Per Additional Node (No Tools)
| Item | Cost |
|------|------|
| ESP32-S3 | £10.50 |
| AD9833 | £3.50 |
| OPA1641 | £2.80 |
| DS18B20 probe | £4.00 |
| TP4056 + battery + holder | £8.20 |
| Passives/wires (portion) | £4.00 |
| Electrodes + hardware | £7.00 |
| **Per node** | **~£40** |

---

## 🛒 PRIORITY ORDERING GUIDE

### Order TODAY for This Weekend (UK Next-Day)

**The Pi Hut** — Free UK shipping over £30
- [ ] ESP32-S3-DevKitC-1 (£10.50)
- [ ] DS18B20 waterproof probe (£4.00)
- [ ] Pinecil v2 + tips (£38.00)

**Amazon UK** (Prime = next-day)
- [ ] AD9833 module (£3.50)
- [ ] Resistor kit (£5.00)
- [ ] Capacitor kit (£4.50)
- [ ] Breadboard 2-pack (£4.00)
- [ ] Dupont wires (£3.50)
- [ ] 18650 protected battery (£5.50)
- [ ] TP4056 Type-C module (£1.50)
- [ ] Heat shrink assortment (£3.50)
- [ ] Project box IP65 (£4.50)
- [ ] Solder 63/37 100g (£8.00)
- [ ] Flux pen (£5.00)
- [ ] Wire strippers (£12.00)
- [ ] Flush cutters (£8.00)
- [ ] Helping hands (£15.00)
- [ ] Multimeter (£15.00)
- [ ] IPA 99.9% (£6.00)
- [ ] Safety glasses (£5.00)

**Farnell/CPC** (Next-day if ordered before 19:00)
- [ ] OPA1641AP (£2.80) — CPC part SC12755
- [ ] LM358N (£0.45) — CPC part SC10504

**Screwfix Click + Collect**
- [ ] M6 threaded rod (£3.50)
- [ ] Jubilee clips (£1.50)
- [ ] Hacksaw (£8.00) — if needed

**Total UK next-day order (zero tools): ~£200**
**Total UK next-day order (have basic tools): ~£90**

### Order from AliExpress (2–3 weeks, Save ~£20)
- [ ] AD9833 module 2-pack (£3.60)
- [ ] TP4056 modules 5-pack (£3.00)
- [ ] 18650 holders 5-pack (£2.50)
- [ ] DS18B20 probes 3-pack (£4.50)
- [ ] Dupont wires 5-set pack (£4.00)
- [ ] Resistor + capacitor kit combo (£6.00)
- [ ] Silicone soldering mat (£5.00)
- [ ] ESD mat + wrist strap (£4.00)

---

## ✅ MASTER ORDER CHECKLIST

### Core Electronics
- [ ] ESP32-S3-DevKitC-1 × 1
- [ ] AD9833 DDS module × 1
- [ ] OPA1641 DIP-8 × 1
- [ ] LM358 DIP-8 × 1
- [ ] Resistor kit (1%, E12, 10Ω–1MΩ)
- [ ] Capacitor kit (ceramic + electrolytic)
- [ ] DS18B20 waterproof probe × 1
- [ ] TP4056 charger module × 1
- [ ] 18650 protected battery × 1
- [ ] 18650 battery holder × 1
- [ ] AMS1117-3.3 module × 1
- [ ] 1N5819 Schottky diode × 2
- [ ] Breadboard × 2
- [ ] Dupont wires M-M + M-F
- [ ] Solid core hook-up wire 22 AWG
- [ ] Pin headers
- [ ] USB-C data cable × 2
- [ ] Micro-USB cable × 1 (if needed)

### Mechanical
- [ ] M6 stainless steel rod × 4 (or 1m length)
- [ ] Jubilee clips 8-16mm × 4
- [ ] Heat shrink tubing assortment
- [ ] 4-core cable 2m
- [ ] Electrical tape
- [ ] Project box IP65
- [ ] Cable glands PG7 × 2
- [ ] Grow bag + tomato plants

### Soldering Station
- [ ] Temperature-controlled soldering iron (Pinecil v2 / TS100 / FX888D)
- [ ] Conical tip 1.2mm
- [ ] Chisel tip 2.4mm
- [ ] Solder 63/37 0.8mm 100g
- [ ] Solder lead-free SAC305 50g (optional)
- [ ] Flux pen (no-clean)
- [ ] Flux paste RMA (tub)
- [ ] Desoldering braid 2.5mm
- [ ] Solder sucker
- [ ] Brass wool tip cleaner
- [ ] Tip tinner / refresher

### Cutting & Shaping
- [ ] Wire strippers (automatic)
- [ ] Flush cutters
- [ ] Heavy-duty side cutters
- [ ] Hacksaw + junior hacksaw
- [ ] Hacksaw blades (pack of 10)
- [ ] Needle file set (6pc)
- [ ] Brass wire brush
- [ ] Sandpaper assortment

### Holding & Magnification
- [ ] Helping hands / third hand
- [ ] Magnifying lamp or headband magnifier
- [ ] ESD-safe tweezers (straight + curved)
- [ ] Silicone soldering mat
- [ ] Small bench vice
- [ ] Spring clamps

### Test & Measurement
- [ ] Auto-ranging multimeter (Aneng AN8008 / Uni-T UT139C)
- [ ] Fine-tip multimeter probes
- [ ] USB-to-UART bridge (CP2102 / CH340)
- [ ] Silicone jumper wire assortment

### Cleaning & Consumables
- [ ] Isopropyl alcohol 99.9% 500ml
- [ ] Precision cotton swabs (pointed)
- [ ] Lint-free wipes
- [ ] Contact cleaner / DeoxIT
- [ ] Hot glue gun + sticks
- [ ] JB Weld / epoxy
- [ ] Cable ties assorted
- [ ] Cable tie mounts
- [ ] Heat gun (or use hair dryer)
- [ ] Loctite 243 threadlocker
- [ ] Clear RTV silicone
- [ ] Label maker or permanent markers

### Safety & PPE
- [ ] Safety glasses
- [ ] Fume extractor or desk fan
- [ ] ESD wrist strap
- [ ] ESD mat (optional)
- [ ] Nitrile gloves
- [ ] Fire extinguisher / blanket
- [ ] Burn dressing + burn gel

### Organisation
- [ ] Component storage box (24 compartments)
- [ ] Magnetic parts tray
- [ ] Project notebook
- [ ] Digital callipers 150mm
- [ ] LED headlamp
- [ ] Multi-tool

---

## ⚠️ CRITICAL BUYING NOTES

1. **ESP32-S3 variant:** Buy **N8R8** (8MB flash + 8MB PSRAM). Avoid N4 (4MB only) or "U" variants (different pinout). The DevKitC-1 has the blue LED on GPIO 2 and breaks out all useful pins.

2. **18650 battery:** **Must be protected** (built-in PCB). Unprotected cells can over-discharge and become dangerous. Samsung 25R, LG MJ1, or Nitecore NL1835HP are reliable. Avoid "UltraFire" brand — often fake capacity.

3. **AD9833 module:** Verify it has a **25 MHz crystal** (silver can next to the chip). Some cheap modules have slow resonators and won't reach 1 MHz accurately.

4. **USB-C cables:** Many cheap cables are **charge-only** (no data wires). Test with a phone or buy from a known brand (Anker, Belkin, Ugreen). You need data for programming the ESP32.

5. **M6 rod:** Buy **A2 (304) stainless**, not zinc-plated steel. Zinc corrodes in soil and affects electrical readings. A4 (316) is overkill but fine.

6. **Soldering iron:** The Pinecil v2 runs on USB-C PD (65W) or DC 12–24V. Your laptop charger probably won't deliver enough wattage. Use a 65W+ PD charger or a DC barrel supply (e.g., old laptop brick 19V).

7. **Flux for stainless steel:** Standard rosin flux won't wet stainless steel well. Use **RMA flux paste** (Amtech NC-559) or **acid flux** (washed off immediately). Alternatively, use jubilee clips instead of soldering.

---

*Generated: 2026-05-10*
*For: GlassHouse Tomatoes v1.0 — ESP32-only breadboard build*
*Next: Flash firmware, run `cal-dry` + `cal-wet` in dry/moist compost*
