# Complete Workbench + Radar Shopping List

One consolidated procurement plan. Everything from the 2.4 GHz radar frontend to the soldering iron.

---

## Quick Summary

| Scenario | Total £ |
|----------|---------|
| **Everything** (including Red Pitaya + all tools) | **~£732** |
| **Radar only** (RP already owned, buy all tools) | **~£482** |
| **Minimum viable** (RP + basic tools already owned) | **~£120** |
| **Phase 1 order** (prove LO + signal chain) | **~£65** |

---

## Priority Legend

| Priority | Meaning | Buy When |
|----------|---------|----------|
| **Must** | Can't proceed without it | Phase 1 |
| **High** | Needed for core functionality | Phase 2 |
| **Medium** | Improves quality of life | Phase 3 |
| **Low** | Nice to have | Phase 4 or later |

---

## Phase 1: Prove the Signal Chain (~£65, 2–3 weeks delivery)

**Goal:** Verify ADF4351 outputs 2.4 GHz and that Red Pitaya can receive baseband.

| Item | £ | Why |
|------|---|-----|
| ADF4351 PLL module | 10 | LO source |
| SMA cables (mixed lengths) | 12 | Connections |
| 10 dB attenuators (×2) | 4 | Protect mixer inputs |
| RTL-SDR v3 | 22 | Debug/verify RF |
| 30 dB SMA attenuator | 3 | Protect SDR from strong signals |
| Breadboard (×2) + jumpers | 9 | Test circuits |
| Multimeter | 12 | Basic voltage/continuity |
| Dupont jumpers M-F + F-F | 4 | GPIO connections |
| **Phase 1 total** | **~76** | |

**Test at end of Phase 1:**
- ADF4351 outputs 2.4 GHz (verified on RTL-SDR waterfall)
- Red Pitaya captures I/Q via loopback cable
- Software runs without errors

---

## Phase 2: Build the RX Chain (~£35)

**Goal:** Downconvert 2.4 GHz to baseband with LT5560 + LNA.

| Item | £ | Why |
|------|---|-----|
| LT5560 IQ demodulator | 8 | Mix RF to baseband |
| SPF5189Z LNA | 5 | Boost weak reflections |
| OPA2197 op-amp | 3 | Buffer baseband to ADC |
| Passives kit | 5 | Caps/resistors for filters |
| Logic analyser | 10 | Debug SPI to ADF4351 |
| USB-TTL adapter | 3 | RP serial console |
| Kapton tape | 4 | Insulate/prototype |
| **Phase 2 total** | **~38** | |

**Test at end of Phase 2:**
- Inject 2.400001 GHz → see 1 kHz beat at Red Pitaya IN1
- LNA provides +20 dB gain
- Op-amp output swings ±0.5V

---

## Phase 3: Over-the-Air + Antennas (~£30)

**Goal:** Actual CW Doppler detection in free space.

| Item | £ | Why |
|------|---|-----|
| 2.4 GHz patch antennas (×2) | 10 | TX and RX |
| SMA splitter | 3 | Divide LO |
| SMA right-angle adapters (×2) | 2 | Tight enclosure |
| SMA DC block | 3 | Isolate DC |
| SPF2243 TX PA | 4 | Through-wall range |
| USB power meter | 5 | Debug current |
| 3.3V regulator | 1 | If needed |
| **Phase 3 total** | **~28** | |

**Test at end of Phase 3:**
- Detect hand waving at 2 m
- Doppler peak at expected frequency
- Spectrogram shows clean signal

---

## Phase 4: Scanning + Enclosure (~£25)

**Goal:** Full polar scanning radar with motion detection.

| Item | £ | Why |
|------|---|-----|
| SG90 pan servo | 2 | Scan antenna |
| SG90 tilt servo | 2 | Optional elevation |
| Pan-tilt bracket | 3 | Mechanical mount |
| Servo extension wires | 2 | Connect to RP |
| External 5V PSU | 5 | Power servos |
| M2 hardware set | 2 | Mount antennas |
| RF enclosure | 5 | Shield frontend |
| Barrel splitter / terminals | 4 | Power distribution |
| Buck converter | 2 | 5V→3.3V if needed |
| Cable ties + clips | 5 | Neaten wiring |
| **Phase 4 total** | **~32** | |

**Test at end of Phase 4:**
- Servo sweeps 0–180° smoothly
- Polar map shows motion sectors
- Activity summary identifies direction of movement

---

## Phase 0: Workbench Tools (One-Time Setup)

**These are reusable for TurboQuant and all future projects.**

| Item | £ | Why |
|------|---|-----|
| Temperature controlled soldering iron | 25 | Essential |
| Solder wire 60/40 | 4 | Standard |
| Flux pen | 3 | SMD soldering |
| Desoldering wick | 3 | Fix mistakes |
| Helping hands + magnifier | 8 | Hold boards |
| Tweezers ESD set | 5 | Place small parts |
| Side cutters | 3 | Trim leads |
| Wire stripper | 4 | Essential |
| Anti-static mat + wrist strap | 8 | Protect ICs |
| LED magnifying bench lamp | 18 | See what you're doing |
| Component organiser box | 8 | Store passives |
| Anti-static bags | 3 | Store ICs safely |
| Stackable bins | 10 | Organise hardware |
| Label maker | 15 | Label everything |
| Isopropyl alcohol + swabs | 6 | Clean boards |
| **Phase 0 total** | **~125** | |

---

## Overlap with TurboQuant V5 Procurement

Some items serve both projects:

| Shared Item | TurboQuant | Radar | Notes |
|-------------|-----------|-------|-------|
| Red Pitaya | Yes (main controller) | Yes (SDR + digitiser) | One device does both |
| PicoScope 2206B | Yes (bring-up debug) | Yes (baseband verification) | Same use |
| Bench PSU | Yes (power board) | Yes (power radar) | 5V/3A covers both |
| Soldering iron | Yes (assembly) | Yes (frontend build) | One-time purchase |
| Multimeter | Yes (continuity) | Yes (voltage check) | One-time purchase |
| Breadboard | Yes (test circuits) | Yes (prototype filters) | Reusable |
| Dupont jumpers | Yes (prototyping) | Yes (RP GPIO) | Reusable |
| Anti-static mat | Yes (handle ICs) | Yes (handle LNA/demod) | One-time |

**If you buy for TurboQuant first, the radar build only needs the RF-specific items (~£93 extra).**

---

## Ordering Strategy

### Option A: One Big AliExpress Order (~£150)
**Pros:** Everything arrives together, cheaper per item, free shipping  
**Cons:** 2–4 week wait, no ability to test early stages while waiting for later items

**Recommended for:** Patient builders who want to save money and don't mind the wait.

### Option B: Phased Ordering (Recommended)
**Pros:** Test each stage before buying next, catch mistakes early, spread cost  
**Cons:** Multiple postage fees, longer total elapsed time

**Phase 1 order:** AliExpress — ADF4351 + SMA cables + attenuators + antennas + LNA  
**Phase 2 order:** Digi-Key/LCSC — LT5560 + OPA2197 (fast shipping for ICs)  
**Phase 3 order:** AliExpress/Amazon — servo + PSU + enclosure + remaining cables

### Option C: Fast Track (Amazon Prime + Digi-Key)
**Pros:** Parts in 1–2 days, build this weekend  
**Cons:** 2–3× price vs AliExpress

**Best for:** Prototyping on a deadline, or if you value time over money.

---

## AliExpress Seller Tips

**Search terms that work:**
```
"ADF4351 development board" — pick one with SPI header
"SPF5189Z low noise amplifier" — confirm 5V operation
"SMA cable kit 6 pack" — variety lengths
"SMA attenuator kit" — often bundled 3/6/10/20 dB
"SG90 servo motor" — buy 5-pack for spares
"2.4GHz WiFi antenna SMA" — same as patch antenna
"Dupont line jumper wire" — 120 pack is cheap
```

**Red flags:**
- No reviews or < 4.5 stars
- Shipping time > 60 days
- No close-up photos of PCB
- Seller with < 95% positive rating

**Green flags:**
>1000 orders, photos show genuine ICs, seller responds to questions within 24h.

---

## Digi-Key vs LCSC vs Mouser

| Distributor | Best For | Shipping £ | Speed |
|-------------|----------|-----------|-------|
| **Digi-Key** | LT5560, OPA2197, Mini-Circuits | Free > £33 | 1–2 days |
| **Mouser** | Same as Digi-Key | Free > £33 | 1–2 days |
| **LCSC** | Chinese domestic parts, cheaper | ~£5 | 5–10 days |
| **Farnell** | UK stock, fast | Varies | 1 day |
| **RS Components** | UK stock, fast | Varies | 1 day |

**For LT5560:** Check all three — it's sometimes on backorder. Alternative: ADL5380 (similar, usually in stock).

---

## What's NOT on This List (And Why)

| Item | Why Not Included | If You Want It |
|------|-----------------|----------------|
| Spectrum analyser | £1000+ | RTL-SDR + software is £22 and covers 90% of needs |
| Vector network analyser | £300+ | Red Pitaya VNA app is free for antenna tuning |
| Signal generator | £200+ | ADF4351 acts as CW generator for self-tests |
| Hot air rework station | £80+ | Only needed for QFN/LGA packages. LT5560 is SSOP — solderable with iron |
| FPGA dev board | £150+ | Red Pitaya IS the FPGA dev board |
| 3D printer | £200+ | Buy bracket or cardboard prototype |
| Oscilloscope | £150+ | PicoScope 2206B already on TurboQuant list |

---

## Budget Scenarios

### Scenario A: Starting From Nothing
**Total:** ~£732  
You need: Red Pitaya + all tools + all RF parts + servo + cables  
**Time to working radar:** 4–6 weeks (including AliExpress delivery)

### Scenario B: TurboQuant Builder (Red Pitaya + Tools Owned)
**Total:** ~£120–150  
You need: RF frontend + servo + cables + antennas  
**Time to working radar:** 3–4 weeks  
**This is the most common scenario.**

### Scenario C: Electronics Hobbyist (Tools Owned, No RP)
**Total:** ~£350  
You need: Red Pitaya + RF frontend + servo  
**Time to working radar:** 3–4 weeks

### Scenario D: Fast Prototype (Amazon Prime Everything)
**Total:** ~£250 (RP already owned) or £500 (with RP)  
**Time to working radar:** 1 week  
**Premium paid:** ~£100 vs AliExpress

---

## Checklist: Before You Order

- [ ] Do I already own a Red Pitaya? (£250 saved)
- [ ] Do I have a soldering iron + multimeter? (£37 saved)
- [ ] Do I have breadboards + jumpers? (£15 saved)
- [ ] Do I have a 5V PSU or phone charger? (£8 saved)
- [ ] Do I have SMA cables from other RF projects? (£12 saved)
- [ ] Do I have a logic analyser or USB-TTL adapter? (£13 saved)
- [ ] Do I have storage/organisation supplies? (£36 saved)
- [ ] Am I comfortable with AliExpress 3-week delivery?
- [ ] Do I need this for a deadline? (If yes: Amazon/Digi-Key)

**Most first-time builders already own £80–120 worth of items on this list.**

---

## After Ordering: Preparation

While waiting for delivery:

1. **Set up Red Pitaya** — flash Pavel Demin's SDR transceiver image, verify network access
2. **Install Python environment** — `pip install -r requirements.txt` from `radar/cw_doppler/`
3. **Test `polar_scanner.py` in mock mode** — `python polar_scanner.py --mock-servo --mock-radar`
4. **Read datasheets** — ADF4351 programming guide, LT5560 pinout, SPF5189Z bias requirements
5. **Plan enclosure layout** — cardboard mockup of where each module sits
6. **Clear desk space** — you'll need 1 m × 0.5 m for the build + test area

---

## Final Notes

**This list is intentionally comprehensive.** You won't need everything on day one. The phased approach lets you spread cost and risk.

**The £120 minimum viable build is real** — if you already have Red Pitaya, soldering iron, multimeter, and breadboard. That gets you a genuine 2.4 GHz scanning CW Doppler radar that detects motion through walls.

**The £732 everything-included build** sets you up with a proper electronics workbench that handles TurboQuant, this radar, and whatever comes next.

**Either way, start with Phase 1.** Prove the LO, prove the signal chain. Everything else builds on that foundation.
