# Mux Board Design — Rev 1
## 8-Element Ultrasound Array Interface for Red Pitaya STEMlab 125-14

**Rev:** 1.0  
**Date:** 2026-03-27  
**Author:** Sven / James  
**Board size target:** 100×70mm (fits standard prototype PCB)

---

## Block Diagram

```
                          MUX BOARD
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  RED PITAYA            TX PATH              ELEMENTS         │
│  ┌──────┐                                                    │
│  │DAC 0 ├──► SMA ──► [Series R] ──┐                         │
│  │      │   (J2)      100Ω        │                         │
│  └──────┘                         │    ┌──── SMA (J3)  EL0  │
│                                   │    │                     │
│  ┌──────┐    TX SWITCH ARRAY      ├──►─┤ Q1 (BSS138)        │
│  │GPIO  ├──► 74HC595 (U1) ───────►├──►─┤ Q2          EL1   │
│  │      │    shift reg             ├──►─┤ Q3          EL2   │
│  │      │    8-bit element select  ├──►─┤ Q4          EL3   │
│  └──────┘                         ├──►─┤ Q5          EL4   │
│                                   ├──►─┤ Q6          EL5   │
│               RX PATH             ├──►─┤ Q7          EL6   │
│  ┌──────┐                         └──►─┤ Q8          EL7   │
│  │ADC 0 ◄── SMA ◄── LNA ◄── MUX ◄────┤                    │
│  │      │  (J11)  (U4a) (U2:4051)     │  BAV99 T/R         │
│  └──────┘                              │  protection on     │
│  ┌──────┐                              │  each element      │
│  │ADC 1 ◄── SMA ◄── LNA ◄── MUX ◄────┤                    │
│  │      │  (J12)  (U4b) (U3:4051)     │                    │
│  └──────┘                         └────┘                    │
│                                                              │
│  POWER: 12V in → LM7805 → 5V → AMS1117 → 3.3V             │
└──────────────────────────────────────────────────────────────┘
```

---

## Circuit Sections

### 1. TX Switch Array

**Purpose:** Route the TX pulse to selected element(s).

```
Schematic per element (×8):

TX_BUS ──[100Ω]──┬──► ELEMENT_N
                  │
            ┌─────┴─────┐
            │  BSS138    │
            │  D ←── S   │
            │     G      │
            └─────┬──────┘
                  │
          74HC595 QN
```

**74HC595 (U1) connections:**
| Pin | Function | Connected to |
|-----|----------|-------------|
| 14 (SER) | Serial data | RP DIO0_P (E1 pin 7) |
| 11 (SRCLK) | Shift clock | RP DIO0_N (E1 pin 8) |
| 12 (RCLK) | Latch | RP DIO1_P (E1 pin 9) |
| 13 (OE) | Output enable | GND (always enabled) |
| 10 (SRCLR) | Clear | VCC (never clear) |
| Q0-Q7 | Outputs | Q1-Q8 gates via 1kΩ |
| VCC | Power | +5V |
| GND | Ground | GND |

**MOSFET (Q1-Q8) BSS138:**
- Gate: from 74HC595 via 1kΩ + 10kΩ pull-down
- Source: GND (for N-channel low-side switch) 
- Drain: to element via series 100Ω

**NOTE Rev 1:** In low-voltage mode, the BSS138 acts as a simple on/off switch. The Red Pitaya DAC output (±1V, 50Ω) drives the TX bus. When Q_N is ON, current flows through the 100Ω series resistor to element N. Only 1-2 elements are active at a time.

**For HV operation (Rev 2):** Replace BSS138 with IRF830 (500V), add gate driver (TC4427), and insert HV pulser between DAC and TX bus.

---

### 2. T/R Protection

**Purpose:** Protect RX mux inputs from TX pulse voltages.

```
Per element (×8):

ELEMENT_N ──┬──[100Ω]──┬──► TO_MUX_INPUT
            │          │
            │    ┌─────┴─────┐
            │    │   BAV99   │
            │    │  D1a  D1b │
            │    └──┬────┬───┘
            │       │    │
            │      GND  VCC
            │
            └── (to TX switch drain)
```

**BAV99 (D1-D8):** Back-to-back series diodes. Clamps the voltage at the mux input to within ±0.7V of the supply rails. Protects CD4051 inputs during TX pulse.

**Series resistor (100Ω):** Limits current through the protection diodes during TX. Also provides some isolation between TX and RX paths.

---

### 3. RX Multiplexer

**Purpose:** Select which element to listen to on each RX channel.

**CD4051B (U2 — RX Channel 0):**
| Pin | Function | Connected to |
|-----|----------|-------------|
| 9 (C0/X0) | Input 0 | Element 0 (via T/R protection) |
| 10 (C1/X1) | Input 1 | Element 1 |
| 11 (C2/X2) | Input 2 | Element 2 |
| 12 (C3/X3) | Input 3 | Element 3 |
| 13 (C4/X4) | Input 4 | Element 4 |
| 14 (C5/X5) | Input 5 | Element 5 |
| 15 (C6/X6) | Input 6 | Element 6 |
| 1 (C7/X7) | Input 7 | Element 7 |
| 3 (COM/Z) | Common out | LNA input (U4a) |
| 11 (A) | Address 0 | RP DIO1_N (E1 pin 10) |
| 10 (B) | Address 1 | RP DIO2_P (E1 pin 11) |
| 9 (C) | Address 2 | RP DIO2_N (E1 pin 12) |
| 6 (INH) | Inhibit | GND (always active) |
| 16 (VDD) | Power | +5V |
| 7 (VEE) | Neg supply | GND (single supply) |
| 8 (VSS) | Ground | GND |

**CD4051B (U3 — RX Channel 1):** Same connections to elements, but:
- COM output → LNA input (U4b)
- Address lines shared with U2 OR independent (use RP DIO3-5 for independent selection)

**Rev 1 decision:** Share address lines between U2 and U3 (both listen to same element). This simplifies wiring. For independent element selection, jumper the address lines to separate GPIO.

---

### 4. Low-Noise Amplifier (LNA)

**Purpose:** Amplify weak receive signals before sending to Red Pitaya ADC.

**Option A — AD8332 (recommended for Rev 2, TSSOP-20):**
- Dual-channel, 0-48 dB variable gain
- Specifically designed for ultrasound receive
- Requires careful PCB layout (high frequency)

**Option B — Discrete with OPA657 (recommended for Rev 1, DIP-8):**

```
Per channel (×2):

MUX_OUT ──[100nF]──┬──[1kΩ]──┐
                   │          │
                   │    ┌─────┴─────┐
                   │    │  OPA657   │
                   │    │ IN- ─ OUT ├──► TO ADC (SMA)
                   │    │ IN+      │
                   │    └─────┬─────┘
                   │          │
                   └──────────┘
                         │
                        GND (via 100Ω)

Non-inverting config:
- R_f = 1kΩ (feedback)
- R_g = 100Ω (to GND)
- Gain = 1 + 1000/100 = 11 (20.8 dB)
- BW = 1.6 GHz / 11 = 145 MHz (plenty for 5 MHz ultrasound)
```

**If OPA657 unavailable, alternatives:**
- OPA659 (DIP-8, 650 MHz, similar specs)
- AD8099 (SOIC-8, 3.8 GHz — if SMD OK)
- LMH6629 (SOT-23-5, 900 MHz, ultra-low noise)

---

### 5. Power Supply

```
12V IN (J13) ──┬──[LM7805 (U5)]──┬──► +5V (CD4051, 74HC595, LNA)
               │                  │
               │              [10µF + 100nF]
               │                  │
               │                 GND
               │
               └──────────────────┬──[AMS1117-3.3 (U6)]──► +3.3V (RP GPIO level)
                                  │
                              [10µF + 100nF]
                                  │
                                 GND
```

**Power budget:**
| Rail | Consumers | Current |
|------|-----------|---------|
| +5V | 74HC595 (6 mA), 2×CD4051 (2 mA), 2×OPA657 (16 mA), BSS138 gates (~1 mA) | ~25 mA |
| +3.3V | Level matching only | ~5 mA |
| +12V | LM7805 input, future HV boost | ~50 mA |

---

## Net List

```
NET             FROM                    TO
────────────────────────────────────────────────────────
TX_BUS          J2 (SMA center)         Q1-Q8 source (via 100Ω each)
EL0             J3 (SMA center)         Q1 drain, D1 anode, U2 pin 13, U3 pin 13
EL1             J4 (SMA center)         Q2 drain, D2 anode, U2 pin 14, U3 pin 14
EL2             J5 (SMA center)         Q3 drain, D3 anode, U2 pin 15, U3 pin 15
EL3             J6 (SMA center)         Q4 drain, D4 anode, U2 pin 12, U3 pin 12
EL4             J7 (SMA center)         Q5 drain, D5 anode, U2 pin 1, U3 pin 1
EL5             J8 (SMA center)         Q6 drain, D6 anode, U2 pin 5, U3 pin 5
EL6             J9 (SMA center)         Q7 drain, D7 anode, U2 pin 2, U3 pin 2
EL7             J10 (SMA center)        Q8 drain, D8 anode, U2 pin 4, U3 pin 4
RX0_OUT         U4a output              J11 (SMA center)
RX1_OUT         U4b output              J12 (SMA center)
MUX0_COM        U2 pin 3 (COM)          U4a non-inv input
MUX1_COM        U3 pin 3 (COM)          U4b non-inv input
SER             RP DIO0_P               U1 pin 14
SRCLK           RP DIO0_N               U1 pin 11
RCLK            RP DIO1_P               U1 pin 12
MUX_A           RP DIO1_N               U2 pin 11, U3 pin 11
MUX_B           RP DIO2_P               U2 pin 10, U3 pin 10
MUX_C           RP DIO2_N               U2 pin 9, U3 pin 9
TRIGGER         RP DIO3_N               Test point (optional)
+5V             U5 output               U1 VCC, U2 VDD, U3 VDD, U4 V+
+3.3V           U6 output               Level shifter (if needed)
GND             Common ground           All grounds, SMA shields
```

---

## Schematic Sheets

The KiCad project is organized as a flat single-sheet schematic:

| Area | X range | Y range | Contents |
|------|---------|---------|----------|
| Top-left | 20-80 | 20-60 | Title block, revision info |
| Left | 20-50 | 70-200 | Red Pitaya connectors (J1, J2, J11, J12) |
| Center-left | 60-100 | 70-140 | 74HC595 + MOSFET switches |
| Center | 110-150 | 70-200 | Element connectors (J3-J10) + T/R protection |
| Center-right | 160-200 | 70-140 | CD4051 mux (U2, U3) |
| Right | 210-260 | 70-140 | LNA (U4a, U4b) |
| Bottom | 20-260 | 210-260 | Power supply section |

---

## Test Plan (Rev 1)

### Phase 1: Power-up
1. Apply 12V, verify 5V and 3.3V rails
2. Check current draw (<50 mA quiescent)

### Phase 2: Digital control
1. Connect Red Pitaya GPIO
2. Shift register test: toggle each Q output, verify with LED/scope
3. Mux address test: sweep A/B/C, verify COM output routing

### Phase 3: Signal path
1. Inject 5 MHz test signal into TX SMA
2. Select element 0 (shift register)
3. Verify signal appears at J3 (element 0 SMA)
4. Set RX mux to element 0
5. Verify amplified signal at RX0 output

### Phase 4: Full loop
1. Connect piezo element to J3
2. Fire TX pulse
3. Capture echo on RX
4. Verify A-scan waveform on Red Pitaya oscilloscope app

---

## Future Revisions

### Rev 2 — HV Operation
- Add HV pulser module (external or on-board)
- Replace BSS138 with IRF830 + TC4427 gate driver
- Add TVS protection (P6KE200A)

### Rev 3 — 64-Element Expansion
- Replace 74HC595 with 8× daisy-chained 74HC595
- Replace CD4051 (8:1) with ADG732 (32:1) ×2
- 4-layer PCB for proper HV/signal isolation
- Add on-board FPGA mezzanine for real-time beamforming
