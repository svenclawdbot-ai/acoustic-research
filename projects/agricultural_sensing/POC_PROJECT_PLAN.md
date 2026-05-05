# PoC Project Plan — Soil Impedance Sensor + LoRa

*Date: 2026-05-05*  
*Goal: Prove dry-vs-wet soil impedance measurement via LoRa this week*  
*Budget: £50*  
*Time: ~6–8 hours across the week*

---

## Bill of Materials

### Core Electronics

| Item | Qty | Spec | Supplier | Part # / Search | Est. Cost | Alt. |
|------|-----|------|----------|-----------------|-----------|------|
| **ESP32-S3-DevKitC-1** | 2 | N8R8 (8MB flash, 8MB PSRAM) | [AliExpress](https://www.aliexpress.com/wholesale?SearchText=ESP32-S3-DevKitC-1-N8R8) | `ESP32-S3-DevKitC-1-N8R8` | £12 (2× £6) | Amazon UK ~£8 each |
| **SX1262 LoRa Module** | 2 | Ebyte E22-900M22S or Heltec HT-RA62 | [AliExpress](https://www.aliexpress.com/wholesale?SearchText=E22-900M22S) | `E22-900M22S` | £16 (2× £8) | [The Pi Hut](https://thepihut.com/) for RFM95W ~£10 each |
| **868 MHz Antenna (SMA)** | 2 | Whip, 3 dBi | AliExpress bundle with module | Usually bundled | £4 (2× £2) | If not bundled: `868MHz antenna SMA` ~£1 each |
| **SMA Pigtail (optional)** | 2 | IPEX to SMA if module has IPEX | AliExpress | `IPEX to SMA` | £2 (2× £1) | Often bundled with module |
| **Dupont wires (M-M, M-F)** | 2 sets | 20 cm, assorted colours | [Amazon](https://www.amazon.co.uk/s?k=dupont+wires) | `Dupont line 40pin` | £4 (2× £2) | In stock at CPC/Farnell if needed today |
| **Half-size breadboard** | 2 | 400 tie-points | [Amazon](https://www.amazon.co.uk/s?k=breadboard) or CPC | `Breadboard 400` | £3 (2× £1.50) | Poundshop / any electronics supplier |

**Electronics subtotal: ~£41**

### Passive Components (check your bin first)

| Item | Qty | Value | Tolerance | Where to find |
|------|-----|-------|-----------|---------------|
| **Resistor** | 2 | 1 kΩ | 1% | Your parts bin / [CPC](https://cpc.farnell.com/) `resistor 1k 0.25W` ~£0.02 |
| **Resistor** | 2 | 100 Ω | 1% | Your parts bin / CPC ~£0.02 |
| **Ceramic cap** | 2 | 100 nF | — | Decoupling near LoRa module (optional but good) |

**Passives subtotal: ~£0–1**

### Electrodes & Mechanical

| Item | Qty | Spec | Supplier | Cost |
|------|-----|------|----------|------|
| **Stainless steel rod** | 2 | M6 × 150 mm (A2 or 316) | [Screwfix](https://www.screwfix.com/) `threaded rod M6` or hardware store | £2 |
| **Pot + compost** | 1 | 2 L pot, multi-purpose compost | Any garden centre / Tesco / B&Q | £4 |
| **Jubilee clip / tape** | 1 | To hold wires to electrodes | In your toolbox | £0 |

**Mechanical subtotal: ~£6**

### Tools You Need (assumed available)

- USB-C cable (ESP32-S3)
- Computer with Arduino IDE or PlatformIO
- Wire cutters / strippers
- Multimeter

---

## Grand Total

| Category | Cost |
|----------|------|
| Core electronics | £41 |
| Passives | £1 |
| Mechanical | £6 |
| **Total** | **~£48** |

**If you already have:** breadboards, Dupont wires, resistors → **~£34**

---

## Day-by-Day Build Plan

### Day 1 (Tuesday Evening, ~2h) — Order + Prep

**Tasks:**
- [ ] Order parts (AliExpress for ESP32 + LoRa, Amazon for breadboard/wires if you need them fast)
- [ ] Install Arduino IDE or PlatformIO on your laptop
- [ ] Install ESP32-S3 board support (via Arduino Boards Manager: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`)
- [ ] Install RadioLib library (Arduino Library Manager: search "RadioLib")
- [ ] Read through `POC_BUILD_GUIDE.md` — know the wiring before parts arrive
- [ ] Find 2× resistors in your parts bin

**Deliverable:** Dev environment ready, order placed.

**Risk:** AliExpress 2–3 day shipping to UK? Usually 7–14 days. **Mitigation:** If you need it *this* week, order from Amazon UK or The Pi Hut for ESP32 + RFM95W (slightly more expensive, arrives tomorrow).

---

### Day 2 (Wednesday Evening, ~1h) — Bench Test (No Soil)

**Assumption:** Parts arrived (or you have ESP32s already).

**Tasks:**
- [ ] Wire node on breadboard: ESP32 + LoRa module + 2 resistors
- [ ] Wire receiver on second breadboard
- [ ] Flash `gateway_poc.ino` to receiver, check Serial Monitor says "Waiting for packets..."
- [ ] Flash `soil_node_poc.ino` to node
- [ ] Test: Node transmits, receiver prints packet
- [ ] Range test: walk to other end of house/garden, note when RSSI drops below -100 dBm

**Deliverable:** LoRa link proven. You know your reliable range.

**Risk:** RadioLib init fails. **Mitigation:** Check CS/RST/DIO/BUSY pins match your exact module. Ebyte E22 uses UART mode by default — may need to solder/pull CS low for SPI. Read module datasheet.

---

### Day 3 (Thursday Evening, ~1.5h) — Electrode Test

**Tasks:**
- [ ] Cut/thread M6 rods to ~100 mm if too long
- [ ] Connect rods to breadboard via wire + alligator clips (or solder short wire to rod, heatshrink)
- [ ] Insert 5 cm apart in pot of dry compost
- [ ] Flash node, power from USB battery pack (or extension lead to garden)
- [ ] Record Z value for dry soil (write it down)
- [ ] Add 200 mL water, wait 5 min
- [ ] Power node again, record Z value
- [ ] Add 500 mL more water (nearly saturated)
- [ ] Power node again, record Z value

**Deliverable:** 3 data points: dry / moist / wet. Clear difference required.

**Risk:** Z values don't change much. **Mitigation:** Check electrodes actually make good contact (push them firmly). Add a pinch of salt to the water — conductivity should spike dramatically. If still flat, check DAC is outputting (probe with multimeter AC mode on GPIO 17).

---

### Day 4 (Friday Evening, ~1h) — Deep Sleep + Interval

**Tasks:**
- [ ] Add `esp_sleep_enable_timer_wakeup()` to node firmware
- [ ] Set interval to 5 minutes (for testing — not 15)
- [ ] Power node from 18650 or USB power bank
- [ ] Place node in pot, receiver indoors
- [ ] Confirm packet every 5 minutes for 30 minutes
- [ ] Note battery voltage trend (if you have a real battery)

**Deliverable:** Autonomous node proven. It wakes, measures, transmits, sleeps, repeats.

**Risk:** Deep sleep doesn't wake. **Mitigation:** Ensure `esp_sleep_enable_timer_wakeup()` is called *before* `esp_deep_sleep_start()`. Check Serial output before sleep to confirm it reached that line.

---

### Day 5 (Saturday, ~2h) — Calibration + Documentation

**Tasks:**
- [ ] Do a proper dry → field capacity → saturation cycle
  - Dry: leave pot unwatered 24h (or oven-dry a sample)
  - Field capacity: water until drain, wait 2h
  - Saturation: water until pooling on surface
- [ ] Record Z for each state, plus soil temperature (if you have DS18B20), weight of pot (kitchen scales)
- [ ] Calculate approximate moisture % from weight: `(wet - dry) / dry × 100`
- [ ] Plot Z vs moisture % (even if just 3 points)
- [ ] Take photos of setup, wiring, electrodes
- [ ] Write notes in `memory/2026-05-09.md` or `projects/agricultural_sensing/poc_notes.md`

**Deliverable:** Calibration curve (even rough). Evidence the concept works.

**Risk:** Oven-drying takes too long. **Mitigation:** Skip oven. Just do "dry as is" / "watered yesterday" / "saturated now". The relative change is what matters for PoC.

---

### Day 6 (Sunday, ~1h) — Retrospective + Next Steps

**Tasks:**
- [ ] Review: what worked, what didn't
- [ ] Measure power consumption if possible (multimeter in series with battery)
- [ ] Calculate: if 18650 = 2600 mAh, how many 5-min cycles before dead?
- [ ] Decide: proceed to 8-channel node, or iterate on measurement quality?
- [ ] Update `POC_BUILD_GUIDE.md` with your actual values, supplier links, gotchas
- [ ] Commit everything to git

**Deliverable:** Go / no-go decision for Phase 2 (8-channel + gateway + irrigation).

---

## Success Criteria

| Test | Pass | Fail |
|------|------|------|
| LoRa link | Receiver prints packet from node at 20 m+ | No packets, or only at <5 m |
| Impedance change | Dry Z ≥ 2× Wet Z | Dry and Wet Z within 20% |
| Repeatability | Same moisture state gives same Z ±15% | Z jumps randomly |
| Deep sleep | Node wakes and transmits every 5 min for 1h | Hangs, crashes, or doesn't wake |

**2 of 4 passing = concept proven. 3 of 4 = solid foundation for Phase 2.**

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| AliExpress parts late (7–14 days) | High | Delays week | Order from UK supplier (Amazon/Pi Hut) for +£10–15 |
| LoRa module incompatibility (Ebyte vs RadioLib) | Medium | Stuck Day 2 | Buy 2× RFM95W (better Arduino support) as backup |
| Soil Z doesn't change with water | Low | Concept doubt | Add salt to water; if still flat, check DAC output with scope/multimeter |
| ESP32-S3 not recognised by IDE | Low | Stuck Day 1 | Use USB-C cable with data lines (not charge-only). Install CP210x driver if needed. |
| No time this week | Medium | Project slips | Minimum viable: Day 2 bench test only (1h). Prove LoRa + measurement circuit. Soil test next week. |

---

## Fast-Track Option (If You Need It This Week)

**Skip AliExpress. Buy from UK stock today:**

| Item | UK Supplier | Price | Delivery |
|------|-------------|-------|----------|
| ESP32-S3-DevKitC-1 | [The Pi Hut](https://thepihut.com/products/esp32-s3-devkitc-1) | £9.50 | Next day |
| RFM95W LoRa Module | [The Pi Hut](https://thepihut.com/products/adafruit-rfm95w-868mhz) | £9.60 | Next day |
| Breadboard + wires | [CPC](https://cpc.farnell.com/) / Amazon | £5 | Same day (Amazon) |
| Resistors | CPC / any | £0.50 | Same day |

**Total: ~£38, arrives tomorrow.**

**Trade-off:** RFM95W uses SX1276 (not SX1262). Slightly less range, different RadioLib init:
```cpp
RFM95 radio = new Module(LORA_CS, LORA_DIO, LORA_RST);
radio.begin(868.0);  // Same API, different chip underneath
```

Everything else (firmware logic, wiring, test protocol) stays identical.

---

## Suppliers Quick Links

- **AliExpress** (cheapest, 7–14 day shipping): `aliexpress.com` → search `E22-900M22S`, `ESP32-S3-DevKitC-1`
- **The Pi Hut** (UK, next day): `thepihut.com` → search `ESP32-S3`, `RFM95W`
- **CPC/Farnell** (UK trade, next day): `cpc.farnell.com` → search `resistor 1k`, `breadboard`
- **Amazon UK** (same day Prime): `amazon.co.uk` → search `ESP32-S3`, `breadboard 400`
- **Screwfix** (local): `screwfix.com` → search `threaded rod M6`

---

## First Action Right Now

1. **Check your parts bin:** Do you have any ESP32 boards? Any LoRa modules? Resistors? Breadboard?
2. **Place order:** If nothing in bin, open AliExpress or Amazon and order.
3. **Install IDE:** Arduino IDE + ESP32 board support + RadioLib.

**Time to first order: 10 minutes.**

*Document saved to: `projects/agricultural_sensing/POC_PROJECT_PLAN.md`*
