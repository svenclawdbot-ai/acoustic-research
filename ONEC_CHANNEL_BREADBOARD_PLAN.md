# TurboQuant V5 — One-Channel Breadboard Test Plan

**Date:** May 6, 2026
**Goal:** De-risk T/R bridge, MUX, LNA, and TX switch with a single-channel breadboard before 8-channel PCB commit
**Timeline:** 3-5 days
**Budget:** £50-80 (mostly parts you may already have)

---

## Why One Channel First?

| Risk | What Could Go Wrong on 8-Channel PCB | De-Risked By Breadboard |
|------|--------------------------------------|------------------------|
| **T/R bridge** | MUR120 isolation insufficient → destroys DG408/LNA | Test with 100V pulse, measure leakage |
| **Bias current** | 1kΩ resistor fix wrong → 21 dB insertion loss | Inject small signal, measure with/without bias |
| **MUX voltage** | DG408 can't handle TX pulse → failure | Verify 100V on signal pins |
| **LNA gain** | Gain=10 insufficient or clips | Inject known signal, verify output |
| **Gate drive** | IRF830 too slow for 5 MHz burst | Scope gate waveform, measure rise/fall |
| **Power** | LM7805 can't supply all 8 channels | Test single-channel load |

**If the breadboard works → confidence for PCB. If it doesn't → fix now, not after £500 PCB order.**

---

## What You Need

### Components (£20-40)

| Qty | Part | Package | Purpose | Cost |
|-----|------|---------|---------|------|
| 4 | MUR120 | DO-41 | T/R bridge diodes | £0.80 |
| 1 | DG408 | SOIC-16 (use adapter) | 8:1 MUX (use 1 channel) | £2.50 |
| 1 | OPA1641 | SOIC-8 (use adapter) | Low-noise amplifier | £1.50 |
| 1 | IRF830 | TO-220 | HV TX switch | £0.80 |
| 1 | TC4427 | SOIC-8 (use adapter) | Gate driver | £1.00 |
| 1 | 74HCT595 | DIP-16 or SOIC adapter | Shift register (just use 1 output) | £0.40 |
| 1 | BSS138 | SOT-23 | Logic-level gate driver | £0.10 |
| 1 | BZX84C5V1 | SOT-23 | 5.1V zener bias | £0.05 |
| 1 | BZX84C12 | SOT-23 | 12V zener gate protection | £0.05 |
| 2 | 1kΩ, 1% | 1/4W resistor | Bias + gate pull-down | £0.02 |
| 1 | 100kΩ, 1% | 1/4W resistor | DC bleed | £0.01 |
| 1 | 100Ω, 1% | 1/4W resistor | Gate series damping | £0.01 |
| 1 | 9.09kΩ, 1% | 1/4W resistor | LNA feedback (Rf) | £0.01 |
| 1 | 1kΩ, 1% | 1/4W resistor | LNA gain set (Rg) | £0.01 |
| 1 | 10kΩ, 1% | 1/4W resistor | MUX address pull-down | £0.01 |
| 2 | 100nF, 50V | Ceramic | Decoupling | £0.10 |
| 2 | 10µF, 16V | Electrolytic or ceramic | Bulk decoupling | £0.20 |
| 1 | 100µF, 25V | Electrolytic | Input bulk | £0.30 |
| 1 | LM7805 | TO-220 | 5V regulator | £0.50 |
| 1 | AMS1117-3.3 | SOT-223 or TO-252 | 3.3V regulator | £0.20 |
| 1 | Schottky SS34 | SMA or DO-41 | Reverse polarity | £0.25 |
| 1 | TVS SMAJ15A | SMA | Transient protection | £0.20 |
| 1 | Polyfuse 2A | 1206 or radial | Overcurrent protection | £0.15 |
| 2 | Banana jacks / headers | — | Power connections | £1.00 |
| 1 | SMA jack or BNC | — | Probe/transducer connector | £2.00 |
| 1 | Breadboard | 830 tie-point | Test platform | £5.00 |
| 1 | Jumper wires | — | Connections | £2.00 |
| **TOTAL** | | | | **~£18-25** |

### Tools (assumed available or borrow)

| Tool | Used For | If Not Owned |
|------|----------|-------------|
| **Oscilloscope** | 100 MHz+ bandwidth | Rigol DS1054Z (£250) or borrow |
| **Signal generator** | TX pulse, test signals | Red Pitaya DAC (already have) or FY6900 (£50) |
| **Bench power supply** | 12V, 5V, adjustable | £50-100 or use wall adapter + LM7805 |
| **Multimeter** | Continuity, voltage checks | £10-20 |
| **Soldering iron** | SOIC adapters, some connections | £15-30 |
| **Wire strippers** | Jumper wire prep | £5 |
| **SOIC-to-DIP adapters** | DG408, OPA1641, TC4427 on breadboard | £1-2 each |

---

## Circuit Diagram — One Channel

```
                         +12V_IN
                            │
                 ┌──────────┴──────────┐
                 │     POWER SECTION    │
                 │  F1 → D1 → D2 → U1  │
                 │  LM7805 → +5V        │
                 │  AMS1117 → +3.3V     │
                 └──────────┬──────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
         +12V (TX)     +5V (logic)   +3.3V (RP)
              │             │             │
              │             │             │
    ┌─────────┴─────────┐   │   ┌─────────┴──────────┐
    │   TX SWITCH       │   │   │  DIGITAL CONTROL   │
    │   TC4427 → IRF830 │   │   │  74HCT595 (1 bit)  │
    │   Gate: BSS138    │   │   │  → BSS138          │
    │   Gate: 100Ω +    │   │   │  → 1kΩ pull-down   │
    │   12V Zener       │   │   └──────────┬─────────┘
    │   +12V → drain    │   │              │
    │   Source → GND    │   │              │ GATE0 (0/5V)
    └─────────┬─────────┘   │              │
              │             │              │
         TX_PULSE (±100V)  │              │
              │             │              │
    ┌─────────┴─────────────┴──────────────┴─────────┐
    │              T/R BRIDGE (4× MUR120)            │
    │                                                  │
    │    TX_PULSE ──► D1 ──► D3 ──► PROBE/SMA        │
    │                   │      │                       │
    │                  D2      D4                     │
    │                   │      │                       │
    │                   └──────┘                       │
    │                      │                          │
    │                 BIAS CTRL                        │
    │                 (1k + 5V Zener)                │
    │                      │                          │
    └──────────────────────┼──────────────────────────┘
                           │
                RX_SIGNAL (<100mV echo)
                           │
    ┌──────────────────────┴──────────────────────────┐
    │              DG408 (1 channel used)            │
    │                                                  │
    │    IN0 ←── RX_SIGNAL                            │
    │    OUT ←── (selected when A=B=C=0)            │
    │    A,B,C,EN ←── 74HCT595 or tied to GND        │
    │    VDD=+12V, VL=+5V, VSS=GND                   │
    └──────────────────────┬──────────────────────────┘
                           │
    ┌──────────────────────┴──────────────────────────┐
    │              LNA (OPA1641)                     │
    │                                                  │
    │    +IN ←── 10:1 attenuator (9.09k + 1k)        │
    │           ←── BAV99 clamping diodes              │
    │    -IN ←── 1kΩ (Rg) → GND                      │
    │    OUT ←── 9.09kΩ (Rf) → -IN                  │
    │    VCC=+5V, GND                                  │
    │                                                  │
    └──────────────────────┬──────────────────────────┘
                           │
                     RX_OUT → SCOPE CH2
                           
```

---

## Step-by-Step Build

### Step 1: Power Section (30 min)

Build first — everything else needs power.

```
Breadboard layout:
  Top rail: +12V (red)
  Bottom rail: GND (blue)
  
Connections:
  12V_IN ──► F1 (polyfuse) ──► D1 (SS34 Schottky) ──► D2 (TVS) ──► U1 (LM7805)
  LM7805 OUT ──► +5V rail (second red rail or strip)
  LM7805 GND ──► GND
  
  +5V ──► U2 (AMS1117) ──► +3.3V rail
  
  Add 100µF electrolytic across 12V_IN/GND
  Add 100nF ceramic across +5V/GND (near LM7805)
  Add 10µF across +5V/GND (near AMS1117)
  Add 100nF across +3.3V/GND
```

**Test:** Power on with 12V bench supply. Measure:
- 12V rail: 11.5-12.5V ✅
- 5V rail: 4.9-5.1V ✅
- 3.3V rail: 3.2-3.4V ✅
- Current draw: <20mA at idle ✅

---

### Step 2: Digital Control (15 min)

```
74HCT595 on SOIC adapter or breadboard:
  VCC (pin 16) ──► +5V
  GND (pin 8) ──► GND
  SRCLR (pin 10) ──► +5V (inactive, tied high)
  OE (pin 13) ──► GND (active, always enabled)
  
  SER (pin 14) ──► jumper wire (manual toggle for test)
  SRCLK (pin 11) ──► jumper wire (manual clock)
  RCLK (pin 12) ──► jumper wire (manual latch)
  
  Q0 (pin 15) ──► BSS138 gate (or directly to TC4427 input)
  
BSS138:
  Gate ──► Q0 (from 74HCT595)
  Source ──► GND
  Drain ──► 1kΩ pull-down ──► GND
  
  Drain also ──► TC4427 input (INA, pin 2)
```

**Test:**
1. Set SER=HIGH, pulse SRCLK (0→5V transition), pulse RCLK
2. Q0 should go HIGH (~5V)
3. BSS138 drain should go HIGH (~5V)
4. Set SER=LOW, repeat — Q0 goes LOW, BSS138 drain goes LOW
5. Verify with scope: clean 0V/5V transitions, no ringing

---

### Step 3: TX Switch + Gate Drive (30 min)

```
TC4427 on SOIC adapter:
  VDD (pin 6) ──► +12V
  GND (pin 4) ──► GND
  INA (pin 2) ──► BSS138 drain (0/5V logic)
  OUTA (pin 7) ──► 100Ω series ──► IRF830 gate
  
IRF830 (TO-220):
  Gate ──► 100Ω (from TC4427) ──► 1kΩ pull-down ──► GND
       ──► BZX84C12 (12V Zener) ──► GND (gate protection)
  Drain ──► TX_BUS node (this goes to T/R bridge)
  Source ──► GND
  
  Add 100nF across drain-source (snubber, optional)
```

**Test (low voltage first!):**
1. Don't connect HV yet. Connect drain to scope via 10:1 probe.
2. Toggle Q0 HIGH → TC4427 should output ~12V → IRF830 turns ON
3. Drain should go to near-GND (conducting)
4. Toggle Q0 LOW → TC4427 outputs ~0V → IRF830 turns OFF
5. Drain should float (or go to whatever load voltage)
6. Measure gate waveform: rise time <100ns? ✅

---

### Step 4: T/R Bridge (30 min)

This is the critical section. Build carefully.

```
Diode bridge layout (MUR120 ×4):
  D1: Anode ──► TX_PULSE node, Cathode ──► PROBE node
  D2: Anode ──► PROBE node, Cathode ──► BIAS node
  D3: Anode ──► BIAS node, Cathode ──► RX node
  D4: Anode ──► RX node, Cathode ──► GND
  
  BIAS node:
    1kΩ resistor ──► +5V rail
    BZX84C5V1 (5.1V Zener) ──► GND (reverse biased, cathode at BIAS)
    100kΩ ──► GND (DC bleed)
    
  PROBE node: SMA or BNC connector (for transducer or dummy load)
  
  RX node: output to DG408 input
```

**Test 1 — Isolation (CRITICAL):**
1. Connect 100V pulse source (or use lower voltage first: 12V from bench supply)
2. Set BIAS: apply +5V to bias node (D1/D3 forward, D2/D4 reverse)
3. Apply TX pulse to TX_PULSE node
4. Measure RX node with scope (AC coupled, sensitive range)
5. **Target:** RX node sees <5V during TX pulse (>26 dB isolation from 100V)
6. If RX node sees >10V → isolation insufficient → check diode orientation

**Test 2 — Insertion Loss:**
1. Connect signal generator: 100mV @ 100 kHz to PROBE node
2. Set BIAS: remove +5V (D2/D4 forward or floating for RX)
3. Measure RX node
4. **Target:** RX signal >30mV (loss <10 dB)
5. If too weak → bias current issue → verify 1kΩ resistor (not 10k)

---

### Step 5: MUX + LNA (30 min)

```
DG408 on SOIC adapter:
  VDD (pin 16) ──► +12V
  VL (pin 1) ──► +5V
  VSS (pin 8) ──► GND
  EN (pin 7) ──► GND (enabled)
  A/B/C (pins 6,5,4) ──► GND (select channel 0)
  
  S1 (pin 13) ──► RX node (from T/R bridge)
  D (pin 3) ──► LNA input
  
OPA1641 on SOIC adapter:
  V+ (pin 7) ──► +5V
  V- (pin 4) ──► GND
  
  +IN (pin 3) ──► 100nF DC block ──► 9.09kΩ ──► DG408 D
             ──► 1kΩ ──► GND (10:1 attenuator)
             ──► BAV99 clamp to +5V/GND (optional for test)
  
  -IN (pin 2) ──► 1kΩ (Rg) ──► GND
            ──► 9.09kΩ (Rf) ──► OUT (pin 6)
  
  OUT (pin 6) ──► RX_OUT → scope
```

**Test:**
1. Inject 10mV @ 100 kHz at MUX input (S1, bypassing T/R bridge first)
2. Measure MUX output (D): should be ~10mV
3. Measure LNA output: should be ~100mV (gain=10) ✅
4. Verify no clipping: increase to 50mV input, output ~500mV (still <4.8V rail)
5. Now connect through T/R bridge and repeat

---

### Step 6: Integration Test (30 min)

Full loop: TX pulse → T/R bridge → probe → echo → MUX → LNA → scope

```
Setup:
  TX_PULSE ──► T/R bridge ──► SMA connector ──► transducer or dummy load
                                          ↓
  (echo signal) ←──────────────────────────┘
                    ↓
  T/R bridge (RX mode) → DG408 → OPA1641 → Scope CH2
  
  Gate control: Q0 toggle → TC4427 → IRF830 → TX pulse
```

**Test:**
1. Connect small transducer or 50Ω dummy load to PROBE
2. Set T/R to TX mode (bias ON)
3. Fire TX pulse (toggle Q0 HIGH for 0.5 µs, then LOW)
4. Immediately switch T/R to RX mode (bias OFF)
5. Capture echo on scope
6. Verify: echo visible, amplitude reasonable, timing correct
7. Repeat at PRF = 1 kHz, 5 kHz, 10 kHz

---

## Expected Results vs. Pass Criteria

| Test | Target | Measurement | Pass/Fail |
|------|--------|-------------|-----------|
| T/R isolation | >26 dB | 100V TX → <5V on RX | ✅ |
| T/R insertion loss | <10 dB | 100mV in → >30mV out | ✅ |
| LNA gain | 10× ±10% | 10mV in → 90-110mV out | ✅ |
| Gate drive | <100ns rise | Scope gate waveform | ✅ |
| PRF | ≥1 kHz | 1 ms period, clean switching | ✅ |
| Power rails | Stable | +5V ±5%, +3.3V ±5% | ✅ |
| Current | <50mA | Bench supply reading | ✅ |

---

## Troubleshooting Guide

### Problem: T/R isolation insufficient (<20 dB)
- **Check:** Diode orientation (MUR120 polarity)
- **Check:** Bias voltage (should be ~5V, not floating)
- **Try:** Add second diode in series for each arm (8 total)
- **Try:** PIN diode upgrade (MA4P7102, ~£2.50)

### Problem: Insertion loss too high (>15 dB)
- **Check:** Bias resistor is 1kΩ (not 10kΩ)
- **Check:** Bias current ~500µA (measure voltage across 1kΩ)
- **Try:** Reduce to 470Ω for more bias (watch power dissipation)
- **Try:** Shorter leads, better grounding

### Problem: LNA output clips or oscillates
- **Check:** Input not exceeding 500mV (attenuator working)
- **Check:** BAV99 clamping diodes installed
- **Check:** Power supply clean (scope +5V rail for noise)
- **Try:** Add 10pF feedback capacitor for stability

### Problem: Gate drive too slow (>200ns)
- **Check:** TC4427 VDD = +12V (not +5V)
- **Check:** 100Ω series resistor not higher
- **Check:** Gate pull-down is 1kΩ (not 10kΩ)
- **Try:** Shorter gate lead (<5cm)

---

## Decision Matrix

| Scenario | Action |
|----------|--------|
| **All tests pass** → | Order 8-channel PCB with confidence |
| **T/R bridge needs tweak** → | Fix on breadboard, update schematic, then order PCB |
| **Major component swap needed** → | Redesign, second breadboard iteration, delay PCB 1-2 weeks |
| **Multiple issues** → | Fix individually, document changes, **still worth doing before PCB** |

---

## Shopping List (Quick Order)

**From LCSC (7-10 day shipping, cheapest):**
- MUR120 × 10 (spare): C114516
- DG408 × 2: C115553
- OPA1641 × 2: C55823
- IRF830 × 2: C99
- TC4427 × 2: C132142
- BSS138 × 10: C7849
- BZX84C5V1 × 5: C32576
- BZX84C12 × 5: C32576
- Resistor kit (0603 or 1/4W through-hole): ~£3
- Capacitor kit: ~£3

**From Amazon/eBay (2-3 days, more expensive):**
- Breadboard: £5
- Jumper wires: £3
- SOIC-to-DIP adapters: £5
- If no scope: Rigol DS1054Z (£250) — **worth buying if you're doing hardware**

**Total: £25-40 in parts + £5-15 in tools/breadboard**

---

## One-Page Cheat Sheet

```
BREADBOARD BUILD ORDER:
1. Power (30 min) → test rails
2. Digital (15 min) → test Q0 toggle
3. TX switch (30 min) → test gate waveform
4. T/R bridge (30 min) → test isolation + loss
5. MUX + LNA (30 min) → test gain
6. Integration (30 min) → full loop

TOTAL: ~3 hours build + 2 hours test = 1 day

CRITICAL TEST: T/R isolation with 100V pulse
  → If >26 dB: GO for PCB
  → If <20 dB: FIX before PCB

CRITICAL TEST: LNA gain = 10×
  → If 9-11×: GO
  → If <8× or clips: FIX
```

---

*Document: One-Channel Breadboard Test Plan*
*Date: May 6, 2026*
*Next action: Order parts + start with power section*
