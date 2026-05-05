# TurboQuant-HV: Integrated HV Pulser & T/R Switch Design

Complete integration of high-voltage pulser and transmit/receive switching into TurboQuant board.

---

## 🎯 Design Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TURBOQUANT-HV BLOCK DIAGRAM                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   POWER SECTION                    CONTROL SECTION                          │
│   ┌──────────────────┐            ┌──────────────────┐                       │
│   │ 7.4V LiPo Input  │            │ Red Pitaya E1    │                       │
│   │ (2S Battery)     │            │ ┌──────────────┐ │                       │
│   └────┬─────────────┘            │ │ SER          │ │                       │
│        │                           │ │ SRCLK        │ │                       │
│   ┌────┴─────────────┐            │ │ RCLK         │ │                       │
│   │ 12V Boost        │            │ └──────┬───────┘ │                       │
│   │ (MT3608)         │            └────────┼─────────┘                       │
│   └────┬─────────────┘                     │                                 │
│        │                                    ↓                                 │
│   ┌────┴─────────────┐            ┌──────────────────┐                       │
│   │ ±100V HV Supply  │            │ 74HC595 Shift Reg│                       │
│   │ (Boost Module)   │            │ (Element Select) │                       │
│   └────┬─────────────┘            └────────┬─────────┘                       │
│        │                                    │                                 │
│        ↓                                    ↓                                 │
│   ┌──────────────────────────────────────────────────────────────────┐       │
│   │                    PER-ELEMENT CHANNELS (×8)                    │       │
│   │                                                                   │       │
│   │  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐   │       │
│   │  │ Element  │←───│  T/R     │←───│ HV       │←───│ Level    │   │       │
│   │  │ Select   │    │ Switch   │    │ Pulser   │    │ Shifter  │   │       │
│   │  │ (Gate)   │    │ (PIN)    │    │ (FET)    │    │ (3.3→12V)│   │       │
│   │  └──────────┘    └────┬─────┘    └──────────┘    └──────────┘   │       │
│   │                        │                                        │       │
│   │                        ↓                                        │       │
│   │                   ┌──────────┐                                  │       │
│   │                   │ Pulse    │                                  │       │
│   │                   │ Xfmr     │                                  │       │
│   │                   │ (Hand-   │                                  │       │
│   │                   │  wound)  │                                  │       │
│   │                   └──────────┘                                  │       │
│   │                                                                   │       │
│   └──────────────────────────────────────────────────────────────────┘       │
│                                       │                                      │
│                                       ↓                                      │
│                              ┌──────────────┐                               │
│                              │ 8 SMA Ports  │←────→ Probe Elements 0-7      │
│                              └──────────────┘                               │
│                                       │                                      │
│                                       ↓                                      │
│   RX SECTION:                    ┌──────────────┐                           │
│   ┌──────────┐                   │ 2× CD4051B   │                           │
│   │ OPA657   │←─────────────────│ (8→2 Mux)    │                           │
│   │ LNA (×2) │                   └──────────────┘                           │
│   └────┬─────┘                                                              │
│        ↓                                                                     │
│   ┌──────────────┐                                                          │
│   │ SMA Output   │←────→ Red Pitaya ADC IN1/IN2                             │
│   └──────────────┘                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ HV Pulser Circuit (Per Element)

### Schematic

```
┌─────────────────────────────────────────────────────────────────┐
│              SINGLE CHANNEL HV PULSER                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  74HC595 Output                                                  │
│  (3.3V logic)                                                    │
│       │                                                          │
│       ↓                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │ TXB0108      │───→│ TC4427       │───→│ IRF830       │       │
│  │ Level Shift  │    │ Gate Driver  │    │ HV MOSFET    │       │
│  │ (3.3V→12V)   │    │ (12V, 1.5A)  │    │ (200V, 4.5A) │       │
│  └──────────────┘    └──────────────┘    └──────┬───────┘       │
│                                                  │               │
│                                                  ↓               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              PULSE TRANSFORMER (T50-2)                  │   │
│  │                                                          │   │
│  │  Primary: 10 turns (center-tapped) ←───────┐            │   │
│  │  Secondary: 10 turns over primary ───────→│───→ Probe  │   │
│  │  Wire: 28 AWG magnet wire                 │            │   │
│  │  Inductance: ~20-50 µH                    │            │   │
│  └────────────────────────────────────────────┼────────────┘   │
│                                               │                │
│  ±100V HV Supply ─────────────────────────────┘                │
│  (100µF cap to GND)                                            │
└─────────────────────────────────────────────────────────────────┘
```

### Component Selection

| Component | Part Number | Specs | Qty (×8) | Cost |
|-----------|-------------|-------|----------|------|
| **Level Shifter** | TXB0108PWR | 8-channel, 3.3V→5V/12V | 1 | £2 |
| **Gate Driver** | TC4427EPA | Dual 1.5A MOSFET driver | 4 | £10 |
| **HV MOSFET** | IRF830PBF | 200V, 4.5A, N-channel | 8 | £24 |
| **Pulse Xfmr** | T50-2 (DIY) | Hand-wound toroid | 8 | £16 |
| **Magnet Wire** | 28 AWG | ~20m total | 1 | £5 |
| **HV Caps** | 100µF, 250V | Filtering | 8 | £8 |

**Total HV section: ~£65**

---

## 🔒 T/R Switch Circuit (Per Element)

### PIN Diode T/R Switch

```
┌─────────────────────────────────────────────────────────────────┐
│              PIN DIODE T/R SWITCH                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│                          To Probe Element                        │
│                               │                                  │
│                               ↓                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │  TX Mode (Pulsing):                                     │   │
│  │  ─────────────────                                      │   │
│  │       │                                                  │   │
│  │       ↓                                                  │   │
│  │   ┌───┴───┐                                              │   │
│  │   │ D1    │←── HV Pulse (±100V)                          │   │
│  │   │ PIN   │     ( conducts → probe)                       │   │
│  │   │ Diode │                                              │   │
│  │   └───┬───┘                                              │   │
│  │       │                                                  │   │
│  │   ┌───┴───┐←── Bias (+5V via 1kΩ) = OFF                 │   │
│  │   │ D2    │     ( isolates RX)                           │   │
│  │   │ PIN   │                                              │   │
│  │   │ Diode │                                              │   │
│  │   └───┬───┘                                              │   │
│  │       │                                                  │   │
│  │       ↓                                                  │   │
│  │    To LNA (Protected)                                    │   │
│  │                                                          │   │
│  │  RX Mode (Receiving):                                   │   │
│  │  ───────────────────                                    │   │
│  │       │                                                  │   │
│  │       ↓                                                  │   │
│  │   ┌───┴───┐←── No bias = OFF                            │   │
│  │   │ D1    │     ( blocks HV leakage)                     │   │
│  │   │ PIN   │                                              │   │
│  │   └───┬───┘                                              │   │
│  │       │                                                  │   │
│  │   ┌───┴───┐←── Bias (0V or -5V) = ON                    │   │
│  │   │ D2    │     ( conducts echo to LNA)                  │   │
│  │   │ PIN   │                                              │   │
│  │   └───┬───┘                                              │   │
│  │       │                                                  │   │
│  │       ↓                                                  │   │
│  │    To LNA (Signal passes)                                │   │
│  │                                                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  PIN Diodes: MA4P7102-1072T (100V, 1A) or similar              │
│  Alternative: 1N5408 (150V, 3A) - not ideal but works          │
└─────────────────────────────────────────────────────────────────┘
```

### Bias Control

```
T/R Switch Bias Generation:

Red Pitaya GPIO (1 pin) ──→ TXB0108 ──→ 74HC595 Bit 9 ──→ Bias Driver
                                         (Global T/R control)

When TX active:
  - D1 bias: 0V (forward conducts)
  - D2 bias: +5V (reverse biased, OFF)

When RX active:
  - D1 bias: +5V (reverse biased, OFF)
  - D2 bias: 0V or -5V (forward conducts)
```

---

## 🔋 Battery Power Architecture

### Power Tree

```
┌─────────────────────────────────────────────────────────────────┐
│                    BATTERY POWER SYSTEM                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  7.4V LiPo Battery (2S, 2000mAh)                                │
│       │                                                          │
│       ↓                                                          │
│  ┌──────────────┐                                                │
│  │ BMS/Protection│←── Overcurrent, overdischarge protection      │
│  │ (2S 3A)      │                                                │
│  └──────┬───────┘                                                │
│         │                                                        │
│    ┌────┴────┬──────────────┬────────────────┐                  │
│    ↓         ↓              ↓                ↓                  │
│ ┌──────┐  ┌──────┐     ┌──────────┐    ┌──────────┐            │
│ │ 5V   │  │ 12V  │     │ ±100V    │    │ Charge   │            │
│ │ Buck │  │ Boost│     │ HV       │    │ Input    │            │
│ │(AMS) │  │(MT3608)    │ Supply   │    │ (USB-C)  │            │
│ └──┬───┘  └──┬───┘     └────┬─────┘    └──────────┘            │
│    │         │              │                                   │
│    ↓         ↓              ↓                                   │
│  ┌─────────────────────────────────────────┐                   │
│  │              LOADS                      │                   │
│  │  • 5V: 74HC595, logic, opamps          │                   │
│  │  • 12V: Gate drivers, level shifters   │                   │
│  │  • ±100V: Pulse transformers (TX only) │                   │
│  └─────────────────────────────────────────┘                   │
│                                                                  │
│  Current Budget:                                                 │
│  • 5V rail: ~100mA (logic + opamps)            = 0.5W           │
│  • 12V rail: ~50mA (gate drivers, ×8)          = 0.6W           │
│  • HV rail: ~10mA × 8 channels pulsing 1% duty = 0.8W           │
│  • Total: ~2W continuous, ~10W peak during TX burst             │
│  • Battery life: ~4-6 hours continuous scanning                 │
└─────────────────────────────────────────────────────────────────┘
```

### Power Components

| Function | Module | Specs | Cost |
|----------|--------|-------|------|
| Battery | 2S LiPo | 7.4V, 2000mAh | £15 |
| BMS | 2S 3A BMS | Protection circuit | £3 |
| 5V Buck | AMS1117-5.0 | 1A, LDO | £0.50 |
| 12V Boost | MT3608 | 2A, adjustable | £2 |
| HV Supply | DIY Boost | 12V→±100V | £10 |

---

## 📐 PCB Layout Considerations

### Board Stackup (4-Layer Recommended)

```
┌─────────────────────────────────────────────────────────────────┐
│ L1 (Top):     HV components, pulse transformers, SMA connectors │
├─────────────────────────────────────────────────────────────────┤
│ L2 (GND):     Solid ground plane, HV section isolation          │
├─────────────────────────────────────────────────────────────────┤
│ L3 (PWR):     Power rails: 5V, 12V, ±100V (separate polygons)  │
├─────────────────────────────────────────────────────────────────┤
│ L4 (Bottom):  Logic, 74HC595, CD4051B, control signals          │
└─────────────────────────────────────────────────────────────────┘
```

### Critical Layout Rules

1. **HV Isolation:**
   - Keep ±100V traces away from logic (min 3mm clearance)
   - Use slots/gaps between HV and low-voltage sections
   - Pulse transformers on top layer, away from sensitive analog

2. **Grounding:**
   - Single-point ground connection between HV and logic GND
   - Star grounding for pulse return currents
   - Separate analog GND for LNA section

3. **Signal Integrity:**
   - Gate drive traces: short, wide (minimize inductance)
   - Match lengths for 8 channels (within 5mm)
   - Decoupling caps close to each IC

4. **Thermal:**
   - IRF830s need small heat sink or copper pour
   - Gate drivers near MOSFETs (minimize loop area)

---

## 🎯 Integrated vs Modular Trade-offs

### Integrated (All-on-One-Board) ✅

**Pros:**
- Single PCB, single enclosure
- No inter-board cables
- Better signal integrity (shorter traces)
- Lower BOM cost (shared power supplies)
- Professional appearance

**Cons:**
- Larger PCB (~120×80mm vs 80×60mm)
- Higher complexity
- Harder to debug HV issues
- Risk of damaging logic if HV fails

### Modular (Separate HV Board)

**Pros:**
- Debug logic and HV independently
- Can upgrade HV section later
- Smaller main board
- Lower risk (isolated failures)

**Cons:**
- Cables between boards
- Multiple enclosures
- Higher total cost
- More assembly steps

**Recommendation:** Integrated for portable NDE use, modular for development.

---

## 📋 Revised TurboQuant-HV BOM

### Integrated Design (Full-Featured)

| Section | Components | Cost |
|---------|------------|------|
| **Logic/Control** | 74HC595, CD4051B, connectors | £15 |
| **RX Chain** | 2× OPA657, passives | £20 |
| **HV Pulser (×8)** | TXB0108, TC4427, IRF830, transformers | £65 |
| **T/R Switch (×8)** | PIN diodes, bias circuitry | £25 |
| **Power System** | Battery, BMS, converters | £35 |
| **Mechanical** | PCB, enclosure, SMAs | £40 |
| **Total** | | **~£200** |

---

## 🏗️ Implementation Plan

### Phase 1: Schematic (This Week)
- Integrate HV pulser into KiCad
- Add T/R switch circuitry
- Update power section for battery

### Phase 2: Layout (Next Week)
- 4-layer PCB design
- HV isolation verification
- Thermal analysis

### Phase 3: Prototype (2-3 Weeks)
- JLCPCB fabrication
- Hand-wind 8 pulse transformers
- Assembly and test

### Phase 4: Validation (Ongoing)
- Pulse characterization (scope)
- T/R isolation measurements
- Battery life testing
- Integration with Red Pitaya

---

## 🔧 Next Steps

1. **Review this design** - any changes?
2. **Update KiCad schematic** - add HV section
3. **Simulate critical paths** - gate drive, pulse shape
4. **Order prototypes** - PCB + components

Ready to update the TurboQuant KiCad schematic with this integrated design?