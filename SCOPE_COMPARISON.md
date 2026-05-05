# Scope & Logic Analyzer Comparison — TurboQuant V5 Bring-Up

**Date:** 2026-04-21
**Use Case:** 8-ch ultrasound MUX/LNA board bring-up + Red Pitaya integration

---

## What You Actually Need to Debug

| Signal Type | Frequency | Voltage | Tool Needed |
|-------------|-----------|---------|-------------|
| Power rails (12V, 5V, 3.3V) | DC + ripple | 0-12V | Scope |
| Shift register SPI (SER/SRCLK/RCLK) | <1 MHz | 3.3V/5V | **Logic analyzer** |
| MUX address lines (A/B/C/EN) | <1 MHz | 5V | Logic analyzer |
| TX switch gate drive | <1 MHz | 0-5V | Scope or logic |
| LNA output (RX0/RX1) | 100 kHz – 20 MHz | <5V | **Scope** |
| TX pulse (HV) | 100 kHz – 5 MHz | up to 100V | **Scope** (10× probe) |
| Red Pitaya ADC/DAC | 125 MHz sample | ±1V | Already on RP |

**Bottom line:** You need **both** analog scope capability *and* digital logic analysis. The question is whether to get them in one box or two.

---

## Option A: FNIRSI / Pocket Scope

**Models:** FNIRSI-1013D, FNIRSI-138PRO, Hantek 2D72

| Spec | Typical |
|------|---------|
| Bandwidth | 50-100 MHz (claimed) |
| Sample rate | 250 MSa/s – 1 GSa/s |
| Channels | 2 |
| Screen | 2.8-3.5" touchscreen |
| Price | £40-80 |

**Pros:**
- ✅ Dirt cheap — if it dies, buy another
- ✅ Battery powered — good for field work
- ✅ Portable — fits in a pocket
- ✅ Some have waveform generator built-in (handy for testing LNA)

**Cons:**
- ❌ Triggering is basic — will struggle with single-shot TX pulses
- ❌ Screen is tiny — you'll squint
- ❌ No PC connectivity for screenshots/logging
- ❌ FFT/math is rudimentary
- ❌ No logic analyzer channels
- ❌ Fake 100 MHz bandwidth on cheaper models (actual ~20-30 MHz useful)

**Verdict for TurboQuant:** OK for "is there 5V on this pin?" but frustrating for real signal debugging. The TX pulse is single-shot and short — pocket scopes often miss it entirely.

---

## Option B: Rigol DS1054Z (or DS1104Z Plus)

| Spec | Value |
|------|-------|
| Bandwidth | 50 MHz (hackable to 100 MHz) |
| Sample rate | 1 GSa/s |
| Channels | 4 |
| Memory | 12 Mpts |
| Screen | 7" colour |
| Price | £300-350 (used/new) |

**Pros:**
- ✅ 4 channels — can watch power, digital control, and analog signal simultaneously
- ✅ Deep memory (12 Mpts) — capture long DMA bursts
- ✅ Excellent triggering (pulse, edge, serial decode) — catch single TX pulses
- ✅ Serial decode (SPI, I2C, UART) — debug shift register for free
- ✅ Hackable bandwidth to 100 MHz with software key
- ✅ LAN/USB for screenshots and remote control
- ✅ FFT for frequency analysis
- ✅ Pass/fail mask testing

**Cons:**
- ❌ Bulky — takes desk space
- ❌ No logic analyzer (digital channels) on base model
- ❌ UI can feel slow
- ❌ Noisy fan

**Verdict for TurboQuant:** The gold standard for bench bring-up. 4 channels let you watch 5V rail, shift register clock, LNA output, and TX pulse all at once. Serial decode on SPI means you don't need a separate logic analyzer for the 74HCT595 debugging.

---

## Option C: PicoScope 2000 Series

**Models:** 2204A (2-ch, 10 MHz), 2205A (2-ch, 25 MHz), 2406B (4-ch, 50 MHz), 2208B (2-ch, 100 MHz)

| Spec | 2204A | 2206B | 2408B |
|------|-------|-------|-------|
| Bandwidth | 10 MHz | 50 MHz | 100 MHz |
| Sample rate | 100 MSa/s | 500 MSa/s | 1 GSa/s |
| Channels | 2 | 4 | 8 |
| Resolution | 8-bit | 12-bit | 12-bit |
| Price | £120 | £350 | £650 |

**Pros:**
- ✅ **12-bit resolution** on 2206B/2408B — 16× better vertical detail than 8-bit scopes. Critical for seeing small LNA signals riding on noise.
- ✅ USB powered — laptop + scope = portable lab
- ✅ **PicoScope 7 software** is genuinely excellent — FFT, serial decode, mask testing, math channels
- ✅ Some models have **built-in AWG** (waveform generator) — test LNA without RP
- ✅ Optional **MSO pods** — add 16 digital channels to any model
- ✅ Super compact

**Cons:**
- ❌ No physical knobs — all mouse/keyboard control (love it or hate it)
- ❌ USB latency for single-shot triggers is slightly worse than bench scope
- ❌ 10 MHz on 2204A is too slow for this project
- ❌ 4-channel 50 MHz model (2406B) is same price as Rigol but only 2× resolution advantage

**Verdict for TurboQuant:** The 12-bit resolution is genuinely useful for ultrasound — you'll see signals the Rigol misses. But you need at least the 2206B (50 MHz, 4-ch) or you're bandwidth-limited. The software is better than Rigol's but knob-less control annoys some people.

---

## Option D: Saleae Logic (Logic 8 / Logic Pro 8)

| Spec | Logic 8 | Logic Pro 8 |
|------|---------|-------------|
| Digital channels | 8 | 8 |
| Analog channels | 0 | 0 |
| Analog sampling | N/A | N/A |
| Bandwidth | Digital only | Digital only |
| Price | £300 | £500 |

Wait — **Saleae Logic is digital-only.** No analog scope capability at all. The "analog" on Logic Pro is just 0/1 threshold comparison, not true analog sampling.

For TurboQuant: **Not sufficient alone.** You'd still need a scope for LNA output and power rails.

---

## Option E: Saleae Logic Pro 16 (or Logic MSO)

| Spec | Logic Pro 16 |
|------|-------------|
| Digital channels | 16 |
| Analog channels | 0 |
| Price | £700+ |

Same issue — digital only. Saleae doesn't make a true mixed-signal scope. They do protocol analysis brilliantly but you can't watch an analog waveform.

---

## Option F: True MSO — Rigol MSO5074 / Siglent SDS2104X Plus

| Spec | Rigol MSO5074 | Siglent SDS2104X Plus |
|------|---------------|------------------------|
| Analog bandwidth | 70 MHz | 100 MHz |
| Analog channels | 4 | 4 |
| Digital channels | 16 | 16 |
| Sample rate | 4 GSa/s | 2 GSa/s |
| Price | £700 | £650 |

**Pros:**
- ✅ **Everything in one box** — 4 analog + 16 digital
- ✅ No compromises on either front
- ✅ Serial decode on all channels simultaneously

**Cons:**
- ❌ Expensive — this is "buy once, cry once" territory
- ❌ Overkill for a single project

---

## The Real Comparison Table

| | FNIRSI | Rigol DS1054Z | Pico 2206B | Saleae Logic | MSO (Rigol/Siglent) |
|---|---|---|---|---|---|
| **Price** | £50 | £330 | £350 | £300 | £700 |
| **Analog ch** | 2 | 4 | 4 | 0 | 4 |
| **Digital ch** | 0 | 0 (SW decode) | 0 (+£150 MSO pod) | 8-16 | 16 |
| **Bandwidth** | ~30 MHz* | 50 MHz | 50 MHz | N/A | 70-100 MHz |
| **Resolution** | 8-bit | 8-bit | **12-bit** | N/A | 8-bit |
| **Memory** | 2K | 12M | 32M | N/A | 100M |
| **Trigger** | Basic | Excellent | Good | N/A | Excellent |
| **SPI decode** | No | Yes | Yes | Excellent | Excellent |
| **Portability** | Excellent | Poor | Good | Good | Poor |
| **TX pulse catch** | Poor | Excellent | Good | N/A | Excellent |
| **LNA signal detail** | Poor | Good | **Excellent** | N/A | Good |

*Fake 100 MHz specs on cheap models — real useful bandwidth ~20-30 MHz.

---

## My Recommendation for TurboQuant

### Best Value: Rigol DS1054Z (£330) + Saleae Logic 8 (£300) = £630

Why this combo:
- Rigol handles analog (LNA, power, TX pulse) with 4 channels and deep memory
- Saleae handles digital debugging (shift register SPI, MUX addressing) with 8 channels and superb software
- You can watch *all* digital control lines simultaneously — something no scope can do
- Total cost is less than an MSO, more flexible than either alone

### If You Want One Box: PicoScope 2406B with MSO pod (£350 + £150 = £500)

- 4 analog channels at 12-bit — better LNA visibility than Rigol
- 16 digital channels via pod — full logic analyzer capability
- USB powered — take it to the lab, friend's house, anywhere
- Software is genuinely great for protocol analysis
- Downside: no physical knobs

### Budget Option: PicoScope 2206B alone (£350), add logic later

- 12-bit analog is the killer feature for ultrasound
- SPI decode in software handles basic shift register debugging
- If you hit a wall with digital debugging, add a £25 8-channel USB logic analyzer (DSLogic / LA2016) later

### Skip: FNIRSI as primary tool

- Fine as a "throw in the bag" secondary tool
- You'll regret it as your only scope for this project
- The TX pulse and LNA output will frustrate you

### Skip: Saleae Logic alone

- It's digital-only — you can't see the analog signals that matter
- Fine as an *addition* to a scope, useless as the only tool

---

## Specific TurboQuant Scenarios

| Scenario | Best Tool |
|----------|-----------|
| "Why isn't the 74HCT595 shifting?" | Saleae Logic (watch SER/SRCLK/RCLK/OE simultaneously) |
| "Is the LNA actually amplifying?" | Pico 2206B 12-bit (see 10mV signals) or Rigol |
| "Did the TX switch fire?" | Rigol (single-shot trigger on 100V pulse) |
| "Is 5V drooping during pulse?" | Rigol channel 3, AC coupled, 20ms window |
| "MUX address lines floating?" | Saleae Logic (all 8 outputs + 3 address lines at once) |
| "Measure LNA bandwidth" | Pico 2206B (FFT + AWG sweep) or Rigol |

---

## Bottom Line

| Budget | Recommendation |
|--------|----------------|
| **£350** | **PicoScope 2206B** — best analog performance for the money, software SPI decode handles basic digital |
| **£500** | **PicoScope 2406B + MSO pod** — one box, everything, 12-bit analog |
| **£630** | **Rigol DS1054Z + Saleae Logic 8** — best overall capability, two specialised tools |
| **£700+** | **Rigol MSO5074 or Siglent SDS2104X Plus** — no compromises, future-proof |
| **£50** | FNIRSI pocket scope — secondary/travel tool only |

For the TurboQuant project specifically: **12-bit resolution matters.** The LNA outputs will be millivolts to hundreds of millivolts. An 8-bit scope quantizes that into ~20mV steps — you'll miss detail. The Pico 2206B's 12-bit gives you ~1mV steps at the same vertical scale. That's the difference between "signal looks clean" and "signal has a 5mV glitch that explains your noise floor."

---

*Generated: April 21, 2026*
