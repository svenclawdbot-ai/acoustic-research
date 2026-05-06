# CW Doppler Radar — Complete Procurement List (Ancillaries)

Everything you need, including the small stuff that gets forgotten.

---

## 1. Core RF Frontend (Already in BOM) ~£73

| Item | Qty | Est. £ | Source |
|------|-----|--------|--------|
| Red Pitaya STEMlab 125-14 | 1 | 250 | Red Pitaya store |
| ADF4351 PLL module | 1 | 10 | AliExpress |
| Resistive SMA splitter 2-way | 1 | 3 | AliExpress |
| SPF2243 2.4 GHz PA module | 1 | 4 | AliExpress |
| SPF5189Z LNA module | 1 | 5 | AliExpress |
| LT5560 IQ demodulator (SSOP-16) | 1 | 8 | LCSC / Digi-Key |
| OPA2197 dual op-amp (SOIC-8) | 1 | 3 | Digi-Key |
| 2.4 GHz patch antenna SMA | 2 | 10 | AliExpress |
| SMA cables (10/20/50 cm mix) | 6 | 12 | AliExpress |
| 10 dB SMA attenuator | 2 | 4 | AliExpress |
| SMA DC block | 1 | 3 | AliExpress |
| AMS1117-3.3 regulator | 1 | 1 | AliExpress |
| Passives (caps/resistors) | 1 | 5 | Local |
| ABS enclosure | 1 | 5 | AliExpress |

---

## 2. Servo Scanning Mechanism ~£10

| Item | Qty | Est. £ | Source | Notes |
|------|-----|--------|--------|-------|
| SG90 9g micro servo | 1 | 2 | AliExpress / Amazon | Pan |
| SG90 9g micro servo | 1 | 2 | AliExpress / Amazon | Tilt (optional) |
| Pan-tilt servo bracket | 1 | 3 | AliExpress / Thingiverse | 3D print or buy |
| Servo extension wires (30 cm) | 2 | 1 | AliExpress | Jumper to servo pins |
| External 5V 2A PSU | 1 | 5 | Amazon / old phone charger | USB-C or barrel jack |
| USB-to-barrel jack cable | 1 | 2 | AliExpress | If using USB PSU |
| M2 screws + nuts set | 1 | 2 | AliExpress | Mount antennas to servo horn |
| Hot glue gun + sticks | 1 | 3 | Amazon / local | Prototype mounting |
| **Subtotal** | | **~20** | | |

**Servo power critical:** SG90 draws ~100 mA when moving. Two servos = 200 mA. Red Pitaya 3.3V rail maxes at ~100 mA total. **Must use external 5V with shared ground.**

---

## 3. Cables, Adapters, Connectors ~£15

| Item | Qty | Est. £ | Source | Why |
|------|-----|--------|--------|-----|
| SMA male-to-male cables (10 cm) | 4 | 6 | AliExpress | Inter-board connections |
| SMA male-to-male cables (50 cm) | 2 | 4 | AliExpress | Antenna runs |
| SMA female-to-female barrel | 2 | 2 | AliExpress | Join cables |
| SMA 90° right-angle adapter | 2 | 2 | AliExpress | Tight enclosures |
| SMA-to-SMB or SMA-to-U.FL | 1 | 2 | AliExpress | If using PCB modules with different connectors |
| Jumper wires M-F (40 pack) | 1 | 2 | Amazon | Breadboard / GPIO connections |
| Jumper wires F-F (40 pack) | 1 | 2 | Amazon | GPIO connections |
| Dupont connector crimp kit | 1 | 5 | AliExpress | Make custom length cables |
| **Subtotal** | | **~25** | | |

---

## 4. Power Distribution ~£10

| Item | Qty | Est. £ | Source | Notes |
|------|-----|--------|--------|-------|
| 5V 3A bench PSU or adapter | 1 | 8 | Amazon | Powers RP + servos + amps |
| DC barrel jack splitter | 1 | 2 | AliExpress | 1 PSU → multiple devices |
| LM2596 buck converter module | 1 | 2 | AliExpress | 5V → 3.3V if needed |
| Barrel jack to screw terminal | 2 | 2 | AliExpress | Easy wiring |
| USB power meter (inline) | 1 | 5 | Amazon | Debug current draw |
| **Subtotal** | | **~19** | | |

**Recommended power architecture:**
```
5V/3A PSU ──┬──► Red Pitaya (5V barrel)
            ├──► Servos (5V, shared GND)
            ├──► LNA (5V)
            └──► AMS1117 ──► 3.3V rail (ADF4351, LT5560, op-amp)
```

---

## 5. Prototyping & Soldering ~£20

| Item | Qty | Est. £ | Source | Notes |
|------|-----|--------|--------|-------|
| Breadboard (830 tie-point) | 2 | 4 | Amazon | Baseband amp, filter tests |
| Breadboard jumper wires | 1 | 2 | Amazon | |
| Perfboard / stripboard 5×7 cm | 5 | 3 | Amazon | Permanent builds |
| Soldering iron (temperature controlled) | 1 | 15 | Amazon | Hakko 888 clone or TS100 |
| Solder wire (0.8 mm, leaded 60/40) | 1 | 3 | Amazon | Easier than lead-free |
| Desoldering wick | 1 | 2 | Amazon | Mistakes happen |
| Flux pen | 1 | 2 | Amazon | Makes SMD soldering possible |
| Helping hands / PCB holder | 1 | 6 | Amazon | Third hand essential |
| Wire stripper | 1 | 3 | Amazon | |
| Side cutters | 1 | 2 | Amazon | |
| Multimeter (cheap) | 1 | 8 | Amazon | Voltage, continuity, basic checks |
| **Subtotal** | | **~50** | | |

**If you already solder:** You probably have most of this. Check your stock before buying.

---

## 6. Test & Debug Accessories ~£25

| Item | Qty | Est. £ | Source | Why |
|------|-----|--------|--------|-----|
| RTL-SDR v3 dongle | 1 | 20 | Amazon / RTL-SDR.com | Verify 2.4 GHz LO, debug RF |
| Cheap WiFi spectrum analyser app | 0 | 0 | Phone app store | Rough frequency check |
| 30 dB SMA attenuator | 1 | 3 | AliExpress | Protect SDR dongle from strong signals |
| Signal generator (ADF4351 can self-test) | 0 | 0 | Use ADF4351 as generator | See hardware_2.4ghz.md |
| LED + resistor (3.3V) | 5 | 1 | AliExpress | GPIO debug — blink = logic high |
| Logic analyser (8-channel, USB) | 1 | 10 | AliExpress / Saleae clone | Debug SPI to ADF4351 |
| USB-to-TTL serial adapter | 1 | 3 | AliExpress | RP console access |
| **Subtotal** | | **~37** | | |

**RTL-SDR is your best debug friend:**
- Verify ADF4351 outputs at 2.4 GHz
- Check for spurs and harmonics
- Test antenna VSWR roughly (look for reflected power)
- Monitor nearby WiFi to avoid interference

---

## 7. Mechanical / Enclosure ~£15

| Item | Qty | Est. £ | Source | Notes |
|------|-----|--------|--------|-------|
| ABS project box 120×80×50 mm | 1 | 5 | AliExpress | Main enclosure |
| ABS project box 80×50×30 mm | 1 | 3 | AliExpress | RX frontend enclosure |
| SMA bulkhead connectors | 4 | 4 | AliExpress | Panel-mount antennas |
| Rubber grommets | 5 | 1 | AliExpress | Cable entry |
| PCB standoffs M3 10 mm | 20 | 2 | AliExpress | Mount boards |
| Heatsink small (for PA) | 1 | 2 | AliExpress | SPF2243 may need it at high duty |
| Thermal tape / pads | 1 | 2 | Amazon | |
| Cable ties (100 pack) | 1 | 2 | Amazon | |
| Adhesive cable clips | 1 | 2 | Amazon | |
| **Subtotal** | | **~23** | | |

**Enclosure strategy:**
- Box 1 (small): LT5560 + LNA + op-amp = RF frontend, near antennas
- Box 2 (medium): Red Pitaya + ADF4351 + power distribution
- Servo + antennas: External on tripod or mount

**Shielding note:** 2.4 GHz leaks everywhere. If you get self-oscillation or weird feedback, add aluminium foil tape inside enclosures. Ground the foil.

---

## 8. Documentation & Consumables ~£5

| Item | Qty | Est. £ | Source |
|------|-----|--------|--------|
| Label maker or permanent markers | 1 | 3 | Amazon |
| Kapton tape | 1 | 3 | Amazon | Insulate, mark, hold |
| SD card 16 GB (for RP OS images) | 1 | 5 | Amazon |
| SD card reader/writer | 1 | 3 | Amazon |
| Notebook / logbook | 1 | 2 | Local |
| **Subtotal** | | **~16** | |

---

## Grand Total

| Category | Est. £ |
|----------|--------|
| Core RF frontend | 73 |
| Servo scanning | 20 |
| Cables & adapters | 25 |
| Power distribution | 19 |
| Soldering & tools | 50 |
| Test & debug | 37 |
| Mechanical / enclosure | 23 |
| Documentation | 16 |
| **TOTAL (if buying everything)** | **~263** |
| **Plus Red Pitaya** | **+250 = 513** |
| **Minus items you already own** | **-??** |

**If you already have:** soldering iron, multimeter, cables, breadboard, PSU → **saves ~£80–100**

**Minimum viable spend (assuming you have tools and Red Pitaya):**
- Core RF: £73
- Servo: £10
- Cables: £10
- **Total: ~£93**

---

## AliExpress Shopping Strategy

**One big order (~£100) vs. multiple small orders:**
- AliExpress has free shipping but 2–4 week delivery
- Order everything at once to save time
- Some sellers bundle: "ADF4351 + SMA cables + attenuator kit"

**Recommended AliExpress search terms:**
```
"ADF4351 module"
"SPF5189Z LNA"
"SPF2243 2.4G"
"SMA cable kit"
"10dB SMA attenuator"
"SG90 servo"
"pan tilt servo mount"
"SMA DC block"
"SMA splitter 2 way"
```

**Digi-Key / Mouser (for quality parts):**
- LT5560 (check stock — sometimes on backorder)
- OPA2197 (usually in stock)
- Mini-Circuits ZAD-1+ (if LT5560 unavailable)

---

## What Can Be Skipped (Cost Savings)

| Skip | Save | Impact |
|------|------|--------|
| Tilt servo (pan only) | £4 | 2D scan only, no elevation |
| PA (SPF2243) | £4 | Desk/room test only, no through-wall |
| DC block | £3 | May work without, risk of DC damage to mixer |
| RTL-SDR debug dongle | £20 | Harder to debug RF issues |
| Logic analyser | £10 | SPI debugging by trial and error |
| Logic analyser | £10 | SPI debugging by trial and error |
| Fancy enclosure | £5 | Cardboard box works for prototyping |
| Heatsink | £2 | Only needed if PA runs hot |
| **Maximum skip savings** | **~£48** | |

---

## Procurement Priority Order

### Phase 1: Prove Signal Chain (£20, 2 weeks delivery)
1. ADF4351 module (£10)
2. SMA cables (£6)
3. 10 dB attenuators (£4)
4. RTL-SDR dongle (£20) — optional but highly recommended

**Test:** Verify 2.4 GHz LO output. Done with just these + Red Pitaya.

### Phase 2: Add RX Path (£15, order with Phase 1)
5. LT5560 (£8)
6. LNA (£5)
7. OPA2197 (£3)
8. Breadboard + passives (£5)

**Test:** Mixer downconversion with signal generator or coupled cable.

### Phase 3: Add TX + Antennas (£15, order with Phase 1)
9. PA (£4) — optional
10. Patch antennas (£10)
11. Splitter (£3)
12. DC block (£3)

**Test:** Over-the-air CW Doppler at 2 m.

### Phase 4: Scanning + Integration (£10, order anytime)
13. Servo + bracket (£7)
14. External 5V PSU (£5)
15. Enclosure (£5)

**Test:** Full polar scanning with motion detection.

---

## Checklist Before Ordering

- [ ] Red Pitaya already owned? (£250 saved if yes)
- [ ] Soldering iron and basic tools owned? (£50 saved if yes)
- [ ] Multimeter owned? (£8 saved)
- [ ] 5V PSU or old phone charger available? (£5 saved)
- [ ] SMA cables from other projects? (£10 saved)
- [ ] Breadboard and jumpers owned? (£5 saved)
- [ ] RTL-SDR or other SDR dongle owned? (£20 saved)
- [ ] 3D printer access for servo bracket? (£3 saved)

**Most people already own:** 30–50% of the ancillaries.

---

## Quick-Start Minimum Order (Assuming Red Pitaya + Tools)

If you just want to prove the concept with minimum spend:

| Item | £ |
|------|---|
| ADF4351 | 10 |
| SMA cables (6-pack) | 8 |
| LNA (SPF5189Z) | 5 |
| Patch antennas (2) | 8 |
| LT5560 | 8 |
| OPA2197 | 3 |
| Splitter | 3 |
| Attenuators (2) | 4 |
| Servo + bracket | 5 |
| 5V PSU | 5 |
| Passives + breadboard | 5 |
| **Minimum viable** | **~64** |

That's a complete 2.4 GHz CW Doppler with scanning for **£64** (assuming Red Pitaya and tools already owned).
