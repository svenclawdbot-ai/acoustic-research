# TurboQuant Pulser Boost: 100V → 200-400V for CFRP NDE

*Date: 2026-05-07*
*Goal: Adapt V5 pulser for carbon fiber composite inspection (thick sections, high attenuation)*

---

## 🔍 WHY BOOST IS NEEDED

| Parameter | Soft Tissue (Liver) | Carbon Fiber Composite | Required Change |
|-----------|---------------------|------------------------|-----------------|
| **Thickness** | 50–150 mm | 5–50 mm (typical), up to 200 mm (wind blade spar) | Thinner but denser |
| **Attenuation @ 1 MHz** | 0.5 dB/cm | 5–20 dB/cm | **10–40× worse** |
| **Acoustic impedance** | 1.5 MRayl | 3.5 MRayl | 2.3× higher |
| **Current pulser** | ±100V | Needs ±200–400V | **2–4× boost** |
| **Pulse energy** | ~10 µJ | Needs ~40–160 µJ | **4–16× more** |

**Key insight:** Carbon fiber is stiffer and more attenuating than tissue. The ultrasound energy is lost faster. To get echoes back from deep delaminations (20+ mm) or thick wind blade sections, you need more transmit power.

**Rule of thumb:** Every 6 dB of additional attenuation needs 2× voltage. CFRP at 20 mm depth = ~40 dB round-trip loss vs. ~10 dB in tissue. That's 30 dB more = **5× voltage = 500V ideally**. But 200–400V is the practical compromise for safety and component availability.

---

## ⚡ CURRENT V5 PULSER — WHAT STAYS, WHAT GOES

### Current Design (from `HV_DESIGN_NOTE_100V.md` and `TURBOQUANT_HV_DESIGN.md`)

```
Red Pitaya DIO → 74HC595 → TXB0108 level shifter → TC4427 gate driver → IRF830 MOSFET
                                                                            ↓
                                                                       Pulse Transformer (1:1, T50-2 toroid)
                                                                            ↓
                                              HV DC-DC boost (12V→100V) → Transducer
                                              (100µF cap)
```

### Component Stress Analysis at 400V

| Component | 100V Rating | 400V Requirement | Verdict | Action |
|-----------|-------------|------------------|---------|--------|
| **IRF830 MOSFET** | 500V drain-source | 400V + 20% margin = 480V | ✅ **OK** | Keep. 500V > 480V. |
| **MUR120 T/R diode** | 200V reverse | 400V + 50% = 600V | ❌ **FAIL** | **Upgrade to MUR460 (600V)** |
| **TC4427 gate driver** | 12V supply, 1.5A | Same gate drive | ✅ **OK** | Keep. Gate drive independent of drain voltage. |
| **TXB0108 level shifter** | 5V/12V | Same logic levels | ✅ **OK** | Keep. |
| **74HC595 shift register** | 5V logic | Same | ✅ **OK** | Keep. |
| **Pulse transformer** | Hand-wound, 28 AWG | 400V insulation | ⚠️ **Marginal** | **Upgrade wire gauge or add insulation** |
| **HV supply** | 100V DC-DC boost | 400V output | ❌ **FAIL** | **New boost module or flyback design** |
| **HV capacitor** | 100µF, 250V | 400V working, 600V surge | ❌ **FAIL** | **Upgrade to 450V or 600V rating** |
| **PCB clearance** | 1 mm (100V) | 2.5–3 mm (400V) | ❌ **FAIL** | **New PCB layout or slot/cut isolation** |

**Summary:** 4 components OK, 4 need upgrading, 1 marginal.

---

## 🔧 BOOST OPTIONS (RANKED)

### Option A: External HV Pulser Module (Recommended for Speed)

**Concept:** Keep V5 board at 100V for medical. Add a **separate, external 400V pulser module** that plugs into the TX_IN SMA port for NDE mode.

```
V5 Board (medical mode):
  TX_IN (SMA) ←── 100V internal pulser ───→ transducer

V5 Board (NDE mode):
  TX_IN (SMA) ←── external 400V pulser ───→ transducer
                (separate box, battery-powered)
```

**External pulser block diagram:**
```
LiPo 7.4V → Boost to 400V (flyback converter) → 10µF 630V cap → MOSFET → pulse transformer → TX_IN
                                       ↑
                                  Trigger from RP DIO (BNC or SMA)
```

**Pros:**
- ✅ Fastest to implement — design external box in parallel with V5 medical bring-up
- ✅ V5 board stays simpler, safer (no 400V on main PCB)
- ✅ Can use off-the-shelf 400V DC-DC modules
- ✅ Easy to bypass if external pulser fails — fall back to 100V
- ✅ One external pulser can drive multiple V5 nodes (cost-effective for fleet)

**Cons:**
- ❌ Extra box to carry in field
- ❌ Extra battery to manage
- ❌ Cable between pulser and V5 (BNC/SMA)

**BOM cost:** ~£40–60 for external pulser

---

### Option B: Upgrade On-Board Pulser to 400V

**Concept:** Modify the V5 PCB to support 400V natively. Upgrade T/R diodes, HV supply, capacitors, and PCB clearances.

**Required changes:**

| Subsystem | Current | Upgraded | Cost |
|-----------|---------|----------|------|
| **HV DC-DC** | 12V→100V boost (~£15) | 12V→400V flyback (~£25) | +£10 |
| **HV capacitor** | 100µF 250V (~£1) | 10µF 450V (~£3) | +£2 |
| **T/R diodes (×32)** | MUR120 200V (~£9.60) | MUR460 600V (~£16) | +£6.40 |
| **Pulse transformer** | T50-2, 28 AWG (~£2) | T68-2, 26 AWG + Kapton tape (~£4) | +£2 |
| **PCB layout** | 1 mm clearance | 3 mm clearance + slots | +£0 (design time) |
| **Total upgrade** | | | **~£20 extra** |

**Pros:**
- ✅ Single integrated unit
- ✅ No external cables
- ✅ Same form factor

**Cons:**
- ❌ PCB redesign required (2–3 week delay)
- ❌ 400V on main board = safety risk if something fails
- ❌ Medical certification harder with HV on patient-facing board
- ❌ If 400V section fails, whole board may be damaged

**My take:** Do this for **NDE-only** product later. For now, use external module to get to market fast.

---

### Option C: Charge-Pump Doubler (Simplest, Limited)

**Concept:** Stack two 100V pulses in series using a diode-capacitor voltage doubler.

```
100V pulse ──→ Diode ──→ Capacitor ──→ Diode ──→ Capacitor ──→ 200V to transducer
                (charges)                (charges)
```

**Limitation:** Only gets you to 200V, not 400V. Slow repetition rate (needs time to charge caps).

**Verdict:** Not enough voltage for thick CFRP. Skip.

---

## 🎯 RECOMMENDED APPROACH: EXTERNAL 400V PULSER MODULE

### Circuit Design

```
┌─────────────────────────────────────────────────────────────────┐
│            EXTERNAL 400V PULSER (NDE Mode)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  7.4V LiPo (2S)                                                 │
│       │                                                          │
│       ↓                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │ MT3608       │───→│ Flyback      │───→│ 10µF 630V    │       │
│  │ Pre-boost    │    │ Transformer  │    │ HV Cap       │       │
│  │ (7.4V→12V)   │    │ (1:30 turns) │    │ (400V rail)  │       │
│  └──────────────┘    └──────────────┘    └──────┬───────┘       │
│                                                  │               │
│       Trigger (BNC) ───→ TC4427 ───→ IRF830 ───┘               │
│       (from RP DIO)        (12V)      (500V)                    │
│                                                  │               │
│                                              Pulse Transformer  │
│                                              (1:1, 600V rated)  │
│                                                  │               │
│                                             BNC Output          │
│                                             (to V5 TX_IN)       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Key Components

| Component | Part Number | Specs | Cost |
|-----------|-------------|-------|------|
| **Flyback controller** | UC3843 or LT3750 | 100–500V output | £3 |
| **Flyback transformer** | DIY or Coilcraft DA2034 | 1:20–1:30 step-up | £8 |
| **HV MOSFET (switching)** | IRF840 or STW9N150 | 500V, 8A | £2 |
| **HV diode (output)** | MUR460 or UF4007 | 600V, 4A | £1 |
| **HV capacitor** | 10µF 450V electrolytic | Low ESR | £3 |
| **Gate driver** | TC4427 (same as V5) | 1.5A, 12V | £2.50 |
| **Output MOSFET** | IRF830 (same as V5) | 500V, 4.5A | £3.20 |
| **Pulse transformer** | CTX01-14611 or DIY T68-2 | 1:1, 600V rated | £8 |
| **Enclosure** | Hammond 1591XX | 100×60×30mm | £5 |
| **Total** | | | **~£35** |

### Performance Specs

| Parameter | Target | Notes |
|-----------|--------|-------|
| **Output voltage** | 50–400V adjustable | Potentiometer or digital control |
| **Pulse width** | 50 ns – 10 µs | Set by trigger input |
| **Rise time** | <50 ns | Depends on gate drive and transformer |
| **PRF** | 1–1000 Hz | Limited by HV capacitor recharge |
| **Energy per pulse** | 10–160 µJ | 10µF @ 400V = 800µJ stored, 20% delivered |
| **Repetition burst** | 1–50 pulses | For ARFI-style push |
| **Battery life** | 2–4 hours | Depends on PRF and voltage |

---

## ⚠️ SAFETY CONSIDERATIONS AT 400V

| Hazard | 100V Risk | 400V Risk | Mitigation |
|--------|-----------|-----------|------------|
| **Electric shock** | Mild tingling | **Painful, potentially dangerous** | Insulated enclosure, warning labels, no user-serviceable HV parts |
| **Capacitor discharge** | 5 mJ (100µF @ 100V) | **80 mJ (10µF @ 400V)** | Bleeder resistor (100kΩ across HV cap, 5s discharge) |
| **Arc flash** | Unlikely at 100V | **Possible at 400V** | Proper PCB spacing, conformal coating, no exposed conductors |
| **Component failure** | Localized damage | **Can destroy adjacent components** | Fuse on HV rail, TVS diodes, current limiting |

**Required additions at 400V:**
1. **Bleeder resistor:** 100kΩ across HV capacitor → discharges to <50V in <5 seconds after power-off
2. **HV indicator LED:** Lights when >50V present
3. **Interlock:** Unit won't operate unless enclosure is closed
4. **Fuse:** 1A fast-blow on HV rail
5. **Warning labels:** "DANGER — HIGH VOLTAGE" in multiple languages

---

## 📋 V5 BOARD MODIFICATIONS (Minimal)

To use external 400V pulser with existing V5 board, you need:

### 1. TX_IN Path Isolation

```
Current V5:
  Red Pitaya DAC ──→ internal 100V pulser ──→ TX_IN SMA ──→ T/R switch ──→ element

NDE mode with external pulser:
  External 400V pulser ──→ TX_IN SMA ──→ T/R switch ──→ element
                                    ↑
                              Internal pulser MUST be disabled
```

**How to disable internal pulser:**
- Option A: Don't populate internal pulser components (TXB0108, TC4427, IRF830 for pulser section) — build V5 without pulser
- Option B: Add SPDT relay or analog switch to route TX_IN either from internal DAC or external SMA
- Option C: Software — keep internal pulser off (74HC595 bit = 0) when external pulser is connected

**Recommendation:** Option C for now (software control). Option A for NDE-only production boards.

### 2. T/R Diode Upgrade

Even with external pulser, the **MUR120 T/R diodes on V5 board see the full TX voltage**.

At 400V: MUR120 (200V) **will avalanche and fail**. Must upgrade to **MUR460 (600V)**.

| Channel | Current (100V) | Upgraded (400V) |
|---------|---------------|-----------------|
| 1× element | 4× MUR120 | 4× MUR460 |
| 8× elements | 32× MUR120 | 32× MUR460 |

**Cost delta:** £9.60 → £16.00 = **+£6.40**

### 3. Bias Voltage Adjustment

T/R diode bias network currently uses ±5V or ±12V. At 400V, the bias needs to ensure diodes stay reverse-biased during TX.

Current bias: +5V on D2 (blocking diode) — enough for 100V but marginal for 400V.

Better bias: **±12V** with current limiting resistors. The 100kΩ bias resistors are fine; just ensure bias supply is stable.

---

## 🧪 TESTING THE 400V PULSER

### Bench Test Protocol

**Phase 1: Low Voltage Verification (NO HV)**
1. Assemble logic and gate driver section with 12V supply only
2. Verify TC4427 outputs toggle with trigger input
3. Check IRF830 gate drive (scope): should see 12V pulses, clean edges

**Phase 2: Medium Voltage (100V)**
1. Connect 100V supply (same as current V5)
2. Scope drain waveform: should see 100V pulses into 50Ω load
3. Verify rise time <100 ns
4. Check for ringing (add damping if needed)

**Phase 3: Full Voltage (400V)**
1. Connect 400V supply
2. Use 50Ω HV load or attenuated scope probe (100:1)
3. Verify pulse shape at 200V, 300V, 400V
4. Measure actual output into real transducer (underwater or gel)
5. Check for corona/arcing (dark room, listen for hissing)

**Phase 4: Integration with V5**
1. Connect external pulser TX_IN to V5 board
2. Disable internal pulser (software)
3. Verify V5 RX path sees echoes (not destroyed by 400V)
4. Check T/R diode bias voltages during TX pulse
5. Measure RX path voltage during TX: must be <±1V at MUX input

---

## 💰 COST COMPARISON

| Approach | BOM Cost | Build Time | Risk | Best For |
|----------|----------|------------|------|----------|
| **External 400V pulser** | £35–50 | 4–6 hours | Low | **Prototyping, NDE beta** |
| **On-board 400V upgrade** | +£20 on V5 | 2–3 weeks (PCB) | Medium | Production NDE units |
| **Buy commercial pulser** | £200–500 | 0 hours | Lowest | If time is critical |

**Commercial options:**
- Panametrics 5077PR: £400, 400V, ultrasonic pulser-receiver
- Ritec SNAP: £300, 250V, compact
- Custom ultrasound pulser (AliExpress): £80–150, 200–400V

**My recommendation:** Build external pulser for £40. It gets you to CFRP testing in days, not weeks. If the market validates, design on-board 400V for production.

---

## 🎯 ACTION ITEMS — THIS WEEK

### External Pulser Build
- [ ] **Order flyback transformer** (Coilcraft DA2034 or equivalent) — Digi-Key/Mouser
- [ ] **Order MUR460 diodes × 32** — upgrade V5 T/R bridge
- [ ] **Order 10µF 450V capacitors × 2** — HV rail filtering
- [ ] **Order IRF840 × 1** — flyback switching MOSFET
- [ ] **Order UC3843 × 1** — flyback controller
- [ ] **Order Hammond 1591XX enclosure** — IP54 for field use

### V5 Board Prep
- [ ] **Replace MUR120 → MUR460** on existing V5 prototype (if built)
- [ ] **Software:** Add "external pulser mode" — disable internal pulser, accept external trigger
- [ ] **Test:** Verify T/R diodes handle 400V without breakdown

### Validation
- [ ] **Week 1:** External pulser assembled, outputting 200V pulses
- [ ] **Week 2:** 400V pulses verified, connected to V5, CFRP panel echoes received
- [ ] **Week 3:** Field test on wind blade section with 400V pulser

---

## 📚 REFERENCES

1. **"Design of High-Voltage Ultrasonic Pulser for NDE"** — Panametrics application note
2. **UC3843 Datasheet** — TI/ON Semi, current-mode PWM controller for flyback
3. **IRF830 / IRF840 Datasheet** — Vishay, 500V N-channel MOSFETs
4. **MUR460 Datasheet** — ON Semi, 600V ultrafast recovery diode
5. **"Ultrasonic Testing of CFRP Composites"** — Zhou et al. 2022 (see `turboquant_cfrp_nde_analysis.md`)

---

*Decision: External 400V pulser module for rapid prototyping. On-board 400V for production later.*
*Priority this week: Order flyback transformer + MUR460 diodes.*

---

*Saved to: `turboquant_400v_pulser_boost.md`*
