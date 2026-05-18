# On-Board 400V Pulser Upgrade — V5 PCB Changes

*Production path: Integrate 400V capability into TurboQuant V5 board*
*Date: 2026-05-07*

---

## 🎯 OBJECTIVE

Modify V5 PCB to natively support **100V (medical) AND 400V (NDE)** selectable per-channel or globally. No external boxes. Single integrated unit.

---

## 📋 CHANGE LIST (V5 → V5-HV)

### 1. HV DC-DC SUPPLY (New Subsystem)

| Item | Current | Upgrade | Footprint |
|------|---------|---------|-----------|
| **Topology** | 12V→100V boost (MT3608) | **12V→400V flyback** | Similar |
| **Controller** | MT3608 | **UC3843** or **LT3750** | SOIC-8 |
| **Switching MOSFET** | IRF830 (500V) | **IRF840 or STP10NK60Z** (600V) | TO-220 |
| **Transformer** | T50-2 toroid, 1:8 | **EE25 flyback transformer**, 1:30 | Custom |
| **Output diode** | MUR120 (200V) | **MUR460 (600V)** | DO-41 |
| **Output capacitor** | 100µF 250V | **10µF 450V** | 12.5×20mm |
| **Bleeder resistor** | None | **100kΩ 2W** | 0805 → 1206 |
| **Feedback divider** | 100k/10k | **10M/25k** (high-voltage rated) | 1206 + 0805 |

**Estimated area:** 40×30mm on PCB (top side, near power input)

---

### 2. T/R SWITCH UPGRADE (All 8 Channels)

| Item | Current | Upgrade | Cost Impact |
|------|---------|---------|-------------|
| **T/R diodes** | MUR120 × 32 (200V) | **MUR460 × 32 (600V)** | +£6.40 |
| **Bias zener** | BZX84C5V1 (5.1V) | **BZX84C12 (12V)** × 8 | +£0.40 |
| **Bias resistors** | 10kΩ + 100kΩ | **Same values, 1206 package** (higher voltage rating) | +£0.20 |
| **PCB clearance** | 1mm (100V) | **3mm + slot isolation** | Layout time only |
| **Conformal coating** | Optional | **Required on HV section** | +£1/board |

**Layout rule:** T/R diodes and bias network must be in a **dedicated HV zone** with 3mm creepage/clearance to low-voltage logic.

---

### 3. PULSE TRANSFORMER UPGRADE

| Item | Current | Upgrade | Notes |
|------|---------|---------|-------|
| **Core** | T50-2 (red/yellow) | **T68-2 or T80-2** (larger) | More inductance, better isolation |
| **Wire** | 28 AWG single | **26 AWG triple-insulated** | 600V rated per layer |
| **Winding** | 10:10 turns | **12:12 turns** | Slightly higher inductance |
| **Insulation** | None between windings | **Kapton tape between pri/sec** | 2 layers |
| **Potting** | None | **Epoxy or silicone** | Optional for production |

**Test:** Hi-pot to 1kV DC between windings (1 minute, <1µA leakage).

---

### 4. GATE DRIVER & LOGIC (Unchanged)

| Component | Status | Notes |
|-----------|--------|-------|
| 74HC595 shift register | ✅ Keep | 5V logic, unaffected by HV |
| TXB0108 level shifter | ✅ Keep | 3.3V→12V, independent |
| TC4427 gate driver | ✅ Keep | 12V supply, drives IRF830 gate |
| IRF830 MOSFET (TX switch) | ✅ Keep | 500V rating sufficient for 400V |

---

### 5. SELECTABLE VOLTAGE (Medical ↔ NDE Mode)

**Problem:** Medical needs 100V max. NDE needs 400V. How to switch?

#### Option A: Software-Controlled Flyback (Recommended)

```
Red Pitaya DIO (1 spare pin) ──→ Digital potentiometer ──→ Flyback feedback divider
                                                              ↓
                                                        HV output: 100V or 400V
```

**Circuit:**
```
                    +12V
                      |
                  UC3843
                      |
                Flyback Xfmr
                      |
                     +++ 400V max
                     | |
           ┌─────────┼─┼────────┐
           │         | |        │
        [10MΩ]   [Digital Pot]  [25kΩ]
           │         | |         │
           └─────────┼─┼────────┘
                     GND
```

**Digital potentiometer:** AD5241 or MCP41050 (SPI/I2C, 50kΩ range)
- Medical mode (100V): Pot = 0Ω → feedback divider = 10MΩ / 25kΩ → output ≈ 100V
- NDE mode (400V): Pot = 25kΩ → feedback divider = 10MΩ / 50kΩ → output ≈ 400V

**Pros:** Single flyback, software control, no mechanical switches
**Cons:** Digital pot must handle high voltage (use series resistor to limit voltage across pot)

**Alternative:** Two separate feedback resistors + analog switch (DG419) to select divider ratio.

---

#### Option B: Two-Stage Boost (Simplest)

```
Stage 1: 12V → 100V (existing MT3608) ──→ Stage 2: 100V → 400V (charge pump/doubler)
```

**Charge pump stage:**
```
100V ──→ Diode ──→ Capacitor ──→ Diode ──→ Capacitor ──→ 200V
                                              │
                                        (repeat for 400V)
```

**Pros:** Reuses existing 100V supply
**Cons:** Low current capability, slow, inefficient, can't do continuous wave

**Verdict:** Not suitable for pulse-echo. Skip.

---

#### Option C: Manual Jumper (Emergency / Field Hack)

Physical jumper on PCB selects between:
- Position A: 100V tap on flyback secondary
- Position B: 400V full secondary

**Pros:** Zero software, foolproof
**Cons:** Requires opening enclosure, not user-friendly

**Verdict:** Good as fallback, not primary solution.

---

### 6. SAFETY ADDITIONS (Required at 400V)

| Feature | Implementation | Cost |
|---------|---------------|------|
| **Bleeder resistor** | 100kΩ 2W across HV cap, 5s discharge to <50V | £0.30 |
| **HV LED indicator** | Neopixel or simple LED + zener (lights when >50V present) | £0.50 |
| **Interlock switch** | Magnetic or microswitch on enclosure lid | £1.00 |
| **HV fuse** | 1A 250V fast-blow on HV rail | £0.20 |
| **TVS protection** | 500V bidirectional TVS on each TX output | £2.00 |
| **Warning silkscreen** | "DANGER — HIGH VOLTAGE" in 5 languages | £0 |

---

## 🏗️ PCB LAYOUT RULES FOR 400V

### Zone Isolation

```
┌─────────────────────────────────────────┐
│  L1 (Top)                               │
│  ┌────────────┐  ┌────────────────────┐  │
│  │ HV ZONE    │  │                    │  │
│  │ (Red hatch)│  │  LOGIC ZONE        │  │
│  │            │  │  (No hatch)        │  │
│  │ • Flyback  │  │                    │  │
│  │ • HV cap   │  │  • 74HC595         │  │
│  │ • T/R      │  │  • DG408           │  │
│  │   diodes   │  │  • OPA1641         │  │
│  │            │  │  • RP connector    │  │
│  │            │  │                    │  │
│  └────────────┘  └────────────────────┘  │
│         ↑ 3mm slot ↑                    │
└─────────────────────────────────────────┘
```

**Rules:**
1. **3mm slot** (routed gap) between HV and logic zones — no copper, no traces
2. **Creepage distance:** 3mm minimum for 400V (IEC 60950 standard)
3. **HV traces:** Short, wide, on top layer only (no vias in HV zone if possible)
4. **Grounding:** Single-point ground connection between HV GND and logic GND (star point)
5. **No sensitive signals** (ADC, LNA input) under HV traces on other layers

### 4-Layer Stackup (Recommended)

```
L1 (Top):    HV components, pulse transformers, T/R diodes
L2 (GND):    Solid ground plane. Split: HV_GND (left) + LOGIC_GND (right)
L3 (PWR):    5V, 12V rails. No HV on this layer.
L4 (Bottom): Logic ICs, RP connector, control signals
```

---

## 📊 COST IMPACT SUMMARY

| Category | V5 (100V) | V5-HV (400V) | Delta |
|----------|-----------|--------------|-------|
| **HV supply** | £15 (MT3608) | £25 (UC3843 flyback) | +£10 |
| **T/R diodes** | £9.60 (MUR120) | £16.00 (MUR460) | +£6.40 |
| **HV capacitor** | £1.00 (100µF 250V) | £3.00 (10µF 450V) | +£2.00 |
| **Pulse transformer** | £2.00 (T50-2) | £4.00 (T68-2 + Kapton) | +£2.00 |
| **Safety components** | £0 | £4.00 (bleeder, LED, fuse, TVS) | +£4.00 |
| **Conformal coating** | £0 | £1.00 (HV zone only) | +£1.00 |
| **PCB (larger)** | £8.00 (100×80mm) | £10.00 (120×80mm) | +£2.00 |
| **TOTAL** | **£35.60** | **£60.00** | **+£24.40** |

**V5-HV BOM:** ~£60 (up from £53 for base V5)
**Full system with RP:** £60 + £250 = £310 (still 100× cheaper than commercial)

---

## 🧪 BRING-UP SEQUENCE (V5-HV)

### Phase 1: Low-Voltage Bring-Up (No HV components populated)
1. Populate logic, LNA, MUX, 5V/12V supplies
2. Verify 74HC595, DG408, OPA1641 all functional
3. Verify communication with Red Pitaya
4. ✅ Pass = board logic is good

### Phase 2: 100V Medical Mode
1. Populate MT3608 (or flyback in 100V mode) + 100V HV cap
2. Populate T/R diodes (use MUR460 even for 100V — they're compatible)
3. Test TX pulse at 100V into 50Ω load
4. Verify RX path sees echoes
5. ✅ Pass = medical mode functional

### Phase 3: 400V NDE Mode
1. Reconfigure flyback feedback for 400V (swap feedback resistor or use digital pot)
2. Verify 400V on HV rail (DMM, 1000V rated probe)
3. Verify bleeder resistor discharges to <50V in <5s
4. Verify HV LED lights
5. Verify interlock kills HV when lid opened
6. Test 400V pulse into HV load (100:1 scope probe or HV attenuator)
7. Verify T/R diodes clamp RX path to <±2V during 400V TX pulse
8. Connect transducer, verify echoes from CFRP panel
9. ✅ Pass = NDE mode functional, safe

---

## 🎯 DECISION: WHEN TO BUILD V5-HV vs. EXTERNAL

| Scenario | Build | Timing |
|----------|-------|--------|
| **Prototyping / Beta testing** | External pulser | Now (this week) |
| **First 20 NDE production units** | External pulser | Q3 2026 |
| **Medical-only units** | V5 100V (no change) | Ongoing |
| **Combined medical+NDE product** | V5-HV integrated | Q1 2027 |
| **High-volume NDE only** | V5-HV or custom ASIC | 2028+ |

**Recommended path:**
1. **Now:** Build external pulser for rapid CFRP testing
2. **Q3 2026:** Evaluate — if NDE sales justify it, design V5-HV PCB
3. **Q1 2027:** V5-HV production for integrated medical+NDE offering

---

## 📁 DELIVERABLES CREATED

| File | Description |
|------|-------------|
| `turboquant_400v_pulser_boost.md` | Full analysis of 100V→400V boost options |
| `turboquant_v5_hv_upgrade.md` (this file) | On-board upgrade specification |
| `pulser_external_schematic.txt` | ASCII schematic for external 400V module |
| `pulser_control.ino` | Arduino control code for external pulser |

---

*On-board upgrade: +£24, +2 weeks PCB, +3mm slot isolation, +conformal coating*
*External module: £35, 4–6 hours build, immediate testing*
*Decision: External first. V5-HV later if market validates.*

---

*Saved to: `turboquant_v5_hv_upgrade.md`*
