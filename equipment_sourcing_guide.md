# Equipment Sourcing Guide
## Low-Cost Shear Wave Elastography Test Rig

**Date:** March 13, 2026  
**Target Budget:** £175-265  
**Goal:** Sub-£500 portable shear wave elastography device

---

## OPTION A: Echomods Kit Route (Recommended)

### Supplier: kelu124 / Murgen Project
**Website:** https://github.com/kelu124/echomods  
**Documentation:** https://kelu124.gitbooks.io/echomods/

| Component | Source | Part/Link | Cost |
|-----------|--------|-----------|------|
| **HV Pulser Board** | OSH Park / Tindie | "un0rick" or "murgen" pulser | £35-45 |
| **20 MSPS ADC HAT** | Hackaday Store / Tindie | ADC pHAT for Raspberry Pi | £45-60 |
| **Analog Front-end** | Included in kit | LNA + protection circuits | Included |
| **Total echomods** | | | **~£80-105** |

**Pros:**
- ✅ Proven, open-source design
- ✅ Active community support
- ✅ Python software included
- ✅ Modular and upgradable

**Cons:**
- ❌ May need to wait for PCB fabrication
- ❌ Some soldering required

**Order Link:**
- Pulser: https://www.tindie.com/products/kelu124/ (search "un0rick")
- ADC: Check Hackaday.io for "murgen" project

---

## OPTION B: Component-by-Component (More Control)

### 1. High-Voltage Pulser

**DIY Arduino Route (Budget: ~£35)**

| Component | Supplier | Part Number | Cost |
|-----------|----------|-------------|------|
| Arduino Nano | Amazon / eBay | Clone, ATmega328P | £8 |
| Gate Driver IC | RS Components / Farnell | TC4427CPA | £2 |
| MOSFET | RS Components | IRF830 | £3 |
| Pulse Transformer | Coilcraft / DIY | Custom or CTX01-14611 | £10 |
| DC-DC HV Module | Amazon / AliExpress | 100-200V boost | £15 |
| Prototyping PCB | Amazon | Breadboard or stripboard | £5 |
| **Total DIY Pulser** | | | **~£43** |

**Circuit Reference:**
```
Arduino → TC4427 → IRF830 → Pulse Transformer → Transducer
                ↑
         100-200V DC-DC
```

**Paper:** "A Pulse Generator Based on an Arduino Platform for Ultrasonic Applications"  
Physics Procedia 70 (2015): 1096-1099

---

### 2. ADC Board

| Option | Supplier | Specs | Cost |
|--------|----------|-------|------|
| **AD9200 Module** | AliExpress / eBay | 20 MSPS, 10-bit | £15-25 |
| **MCP3008 + Pi** | Amazon | 1 MSPS (slow), 10-bit | £10 |
| **HiFiBerry ADC** | HiFiBerry | 24-bit audio (not ideal) | £30 |
| **Recommended: AD9200** | | | **~£20** |

**Note:** The echomods ADC HAT is preferred if available (£45) for better integration.

---

### 3. Transducers (CRITICAL COMPONENT)

**Source 1: Piezo Hannas (China)**
- **Website:** Alibaba / Direct contact
- **Email:** piezohannas@163.com
- **Part:** 3.5 MHz, single element, 13mm diameter, unfocused
- **Cost:** £20-25 each + shipping
- **MOQ:** 2-5 pieces
- **Lead time:** 2-3 weeks

**Source 2: AliExpress (Faster)**
- Search: "3.5MHz ultrasound transducer single element"
- **Cost:** £25-35 each
- **Lead time:** 1-2 weeks
- **Risk:** Quality varies

**Source 3: NDT Supply Companies**
- **Olympus / Panametrics:** V106-RB (professional, £200+)
- **DAKOTA:** UT transducers (~£100)
- **Too expensive for this project**

**Recommended Order:**
| Qty | Source | Unit Cost | Total |
|-----|--------|-----------|-------|
| 3 | Piezo Hannas | £22 | £66 |
| 1 (spare) | AliExpress | £28 | £28 |
| **Total 4 transducers** | | | **£94** |

**Specs to Request:**
- Frequency: 3.5 MHz (or 5 MHz for higher resolution)
- Element diameter: 10-20 mm
- Focus: Unfocused or weakly focused (≥50 mm focal length)
- Connector: BNC or bare wires
- Housing: Metal or plastic

---

### 4. Raspberry Pi 4

| Source | Product | Cost | Notes |
|--------|---------|------|-------|
| **Pi Shop UK** | Pi 4 (4GB) | £55 | Official, fast shipping |
| **Amazon** | Pi 4 (4GB) + case + SD | £65-75 | Convenience |
| **Pimoroni** | Pi 4 (4GB) | £55 | UK supplier, good support |

**Also Need:**
- MicroSD card (32GB): £8
- Case: £5
- Power supply (USB-C): £8
- **Total Pi setup:** ~£75

---

### 5. Cables & Connectors

| Item | Qty | Supplier | Cost |
|------|-----|----------|------|
| BNC male-male cables (1m) | 4 | Amazon / RS | £12 |
| BNC to bare wire adapters | 4 | Amazon | £8 |
| SMA to BNC adapters (if needed) | 4 | Amazon | £6 |
| Coaxial cable (RG58, per meter) | 2m | RS Components | £4 |
| **Total cables** | | | **~£30** |

---

## OPTION C: Commercial Thickness Gauge Hack

**Approach:** Buy affordable thickness gauge, tap into analog output

| Product | Source | Cost | Notes |
|---------|--------|------|-------|
| **CNYST UT200** | Amazon UK | £150-180 | Comes with transducer |
| **Dakota MX-3** | eBay (used) | £100-150 | Industrial quality |
| **Olympus 38DL PLUS** | eBay (used) | £500+ | Overkill |

**Pros:**
- ✅ Immediate working hardware
- ✅ No soldering required
- ✅ Reliable transducer included

**Cons:**
- ❌ Less flexible (fixed pulse parameters)
- ❌ May need reverse engineering
- ❌ Harder to integrate with Python

**Verdict:** Good for quick validation, but limits long-term development.

---

## PHANTOM MATERIALS

### DIY Gelatin (Recommended Start)

| Component | Source | Amount | Cost |
|-----------|--------|--------|------|
| **Gelatin 300 bloom** | Amazon / Special Ingredients | 500g | £12 |
| **Graphite powder** | Amazon (art supply) | 100g | £8 |
| **Glycerin** | Pharmacy / Amazon | 500ml | £5 |
| **Mold (Tupperware)** | Supermarket | 2-3 containers | £5 |
| **Total per batch** | | | **~£30** |

**Recipe (5 kPa = healthy liver):**
- 100g gelatin
- 900ml hot water
- 10g graphite powder
- 20ml glycerin (for stability)
- Pour, refrigerate 4 hours

**Recipe (20 kPa = fibrotic liver):**
- 150g gelatin
- 850ml hot water
- Same graphite/glycerin

---

### Polyacrylamide (Better Stability)

| Component | Source | Cost |
|-----------|--------|------|
| Acrylamide/bis solution 40% | Sigma-Aldrich / Fisher | £30 |
| Ammonium persulfate | Sigma-Aldrich | £15 |
| TEMED | Sigma-Aldrich | £20 |
| Silica microspheres | Sigma-Aldrich | £25 |
| **Total** | | **~£90** |

**Warning:** Acrylamide is neurotoxic. Use gloves, work in ventilated area.

---

## COMPLETE SHOPPING LISTS

### Budget Build (3 transducers): £175

| Component | Source | Cost |
|-----------|--------|------|
| DIY Pulser (Arduino) | Amazon/RS | £43 |
| AD9200 ADC Module | AliExpress | £20 |
| 3× Transducers | Piezo Hannas | £66 |
| Raspberry Pi 4 + accessories | Pi Shop | £75 |
| Cables & connectors | Amazon | £20 |
| Gelatin phantom batch | Supermarket | £15 |
| **TOTAL** | | **~£240** |

**To hit £175:** Skip Pi case, use existing SD card, start with 2 transducers.

---

### Recommended Build (3 transducers): £265

| Component | Source | Cost |
|-----------|--------|------|
| **Echomods Pulser + ADC** | Tindie | £90 |
| 3× Transducers (3.5 MHz) | Piezo Hannas | £66 |
| Raspberry Pi 4 + case + SD | Pi Shop | £75 |
| BNC cables & adapters | Amazon | £25 |
| Gelatin phantom materials | Supermarket | £15 |
| **TOTAL** | | **~£270** |

---

### Optimal Build (4 transducers): £340

| Component | Source | Cost |
|-----------|--------|------|
| **Echomods Pulser + ADC** | Tindie | £90 |
| 4× Transducers (3.5 MHz) | Piezo Hannas | £88 |
| Raspberry Pi 4 + accessories | Pi Shop | £75 |
| BNC cables & adapters | Amazon | £30 |
| Multiple phantom batches | | £30 |
| Mechanical shaker (optional) | Amazon | £50 |
| **TOTAL** | | **~£365** |

---

## ORDER PRIORITY

### Phase 1: Proof of Concept (£100)
1. **Transducer ×1** (£25) — Test signal chain
2. **Arduino + components** (£40) — Build basic pulser
3. **Pi + ADC** (£75) — Acquisition system

**Goal:** See ultrasound echoes, validate hardware works

---

### Phase 2: Shear Wave Detection (£75 more)
4. **Transducers ×2 more** (£50) — For 3-receiver array
5. **Gelatin + graphite** (£15) — Make first phantom
6. **BNC cables** (£10) — Complete wiring

**Goal:** Detect shear wave propagation, measure group velocity

---

### Phase 3: Viscoelastic Characterization (£100 more)
7. **4th transducer** (£25) — Extended baseline
8. **Polyacrylamide kit** (£90) — Stable phantoms
9. **Mechanical shaker or better pulser** (£50)

**Goal:** Full G' + η recovery with Bayesian inference

---

## SUPPLIER CONTACTS

### Transducers (Piezo Hannas)
- **Email:** piezohannas@163.com
- **Response time:** 24-48 hours
- **Payment:** Alibaba Trade Assurance or wire transfer
- **Sample order:** Ask for 2-3 pieces first

**Email Template:**
```
Subject: Sample Order - 3.5 MHz Single Element Transducers

Hello,

I am researching low-cost medical ultrasound devices and would like
to order sample transducers:

- Quantity: 3 pieces
- Frequency: 3.5 MHz
- Element diameter: 13-20 mm
- Focus: Unfocused or weakly focused (focal length >50mm)
- Housing: Metal or plastic
- Connector: BNC preferred

Application: Shear wave elastography research (non-clinical)

Please quote price including shipping to UK.

Thank you,
[Your name]
```

---

### Echomods
- **GitHub:** https://github.com/kelu124/echomods
- **Tindie:** Search "un0rick" or "kelu124"
- **Contact:** Via GitHub issues

---

## TIMELINE

| Phase | Components | Lead Time | Start |
|-------|-----------|-----------|-------|
| **Week 1** | Pi + Arduino + 1 transducer | 3-5 days | Order now |
| **Week 2** | Build pulser, test echoes | — | Build |
| **Week 3** | 2 more transducers arrive | 2-3 weeks | Order Week 1 |
| **Week 4** | Make phantom, test shear waves | — | Experiment |
| **Week 5+** | 4th transducer, refine | — | Optimize |

---

## RISK MITIGATION

| Risk | Mitigation |
|------|-----------|
| Transducer delivery delay | Order from AliExpress as backup |
| Pulser doesn't work | Buy commercial thickness gauge (£150) |
| Phantom too soft/stiff | Iterate gelatin concentration |
| Signal too noisy | Add LNA (low-noise amplifier) |
| ADC insufficient | Upgrade to 16-bit later (£30 extra) |

---

## IMMEDIATE ACTION ITEMS

### Today:
1. [ ] Email Piezo Hannas for transducer quote
2. [ ] Order Raspberry Pi 4 from Pi Shop
3. [ ] Order Arduino + components from Amazon

### This Week:
4. [ ] Order echomods pulser/ADC from Tindie (or build DIY)
5. [ ] Buy gelatin and graphite from supermarket
6. [ ] Set up GitHub repo for hardware documentation

### Next Week:
7. [ ] Assemble pulser circuit
8. [ ] Test basic pulse-echo
9. [ ] Make first gelatin phantom

---

*Document created: March 13, 2026*  
*Next update: After first hardware tests*
