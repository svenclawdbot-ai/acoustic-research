# TurboQuant V5 — KiCad Schematic Tutorial

A step-by-step guide to building the complete hierarchical schematic in KiCad 8.x.

---

## 1. Project Setup

```bash
# In KiCad, File → New Project → TurboQuant_v5
# This creates:
#   TurboQuant_v5/TurboQuant_v5.kicad_pro   (project settings)
#   TurboQuant_v5/TurboQuant_v5.kicad_sch    (root schematic)
```

**Project Settings** (right-click project → Project Settings):
- **Schematic format**: KiCad 8.x (S-expression)
- **Netlist format**: Default
- **Annotation style**: Incremental (U1, U2, U3...)
- **Cross-reference style**: U?A, U?B for multi-unit symbols

---

## 2. Sheet Hierarchy (Root + 4 Subsheets)

The design uses a **hierarchical schematic** with 1 root sheet and 4 subsheets.

### Root Sheet Setup

1. Open `TurboQuant_v5.kicad_sch` (root)
2. Place hierarchical sheets: **Place → Hierarchical Sheet** (or `S` key)
3. Draw 4 rectangles with these properties:

| Sheet | Filename | Size (grid units) | Label |
|-------|----------|-------------------|-------|
| Power Supplies | `power.kicad_sch` | 60×50 mm | "Power Supplies" |
| Digital Control | `digital.kicad_sch` | 75×60 mm | "Digital Control" |
| Analog Frontend | `analog.kicad_sch` | 130×65 mm | "Analog Frontend" |
| TX Switch | `tx_switch.kicad_sch` | 75×65 mm | "TX Switch" |

4. **Add hierarchical pins** to each sheet box: **Place → Hierarchical Pin**

**Root Sheet Pin Assignments:**

```
Sheet: Power Supplies (power.kicad_sch)
  OUT: +12V, +5V, +3.3V, GND

Sheet: Digital Control (digital.kicad_sch)  
  IN:  +5V, GND, SER, SRCLK, RCLK, ~OE, SRCLR
  OUT: GATE0..GATE7

Sheet: Analog Frontend (analog.kicad_sch)
  IN:  +5V, +12V, GND, TX_BUS, MUX_A, MUX_B, MUX_C, MUX_EN
  OUT: RX0_OUT, RX1_OUT

Sheet: TX Switch (tx_switch.kicad_sch)
  IN:  +12V, GND, GATE0..GATE7
  OUT: TX_BUS
```

### Wiring the Root Sheet

Use **Place → Wire** (`W` key) to connect hierarchical pins:

- **+12V rail**: Red, 2.5mm wide — runs from Power → Analog → TX Switch
- **+5V rail**: Blue, 2mm wide — runs from Power → Digital → Analog
- **GND**: Gray, 1.5mm wide — common ground to all sheets
- **SPI bus** (green): SER, SRCLK, RCLK, ~OE, SRCLR from root → Digital
- **TX_BUS** (orange): TX Switch → Analog (bidirectional for pulse)
- **MUX control** (black): Digital → Analog (MUX_A..MUX_EN)
- **GATE bus** (orange): Digital → TX Switch (GATE0..GATE7)

**Tip**: Use **Place → Label** (`L` key) for net names instead of drawing long wires. Labels with the same name connect implicitly.

---

## 3. Symbol Libraries Setup

KiCad needs symbol libraries for the custom components. Either use built-in or create a project-specific library.

### Built-in Libraries to Add

Go to **Preferences → Symbol Library Manager**:

```
Device          (R, C, L, D, Q, U)
Connector       (headers, terminals)
Power           (VCC, GND, +5V, +12V symbols)
Transistor_FET  (IRF830, BSS138 if available)
Interface       (74HCT595)
```

### Project-Specific Library (turboquant_library.kicad_sym)

Create **File → New Library → Project** → name it `turboquant`.

Add these custom symbols:

| Symbol | Type | Pins | Notes |
|--------|------|------|-------|
| DG408 | IC | 16 | MUX analog switch |
| OPA1641 | IC | 8 | Dual op-amp (use as single) |
| TC4427 | IC | 8 | Dual MOSFET driver |
| IRF830 | MOSFET | 3 | N-channel HV |
| BSS138 | MOSFET | 3 | Small-signal N-ch |
| LM7805 | Regulator | 3 | +5V linear |
| AMS1117-3.3 | Regulator | 4 | +3.3V LDO |
| RP2040_GPIO | Connector | 40 | Raspberry Pi E1 header |

**Creating a symbol**: Symbol Editor → New Symbol → Draw rectangle → Add pins.

**Pin naming for DG408**:
```
Left side (analog inputs):  S1, S2, S3, S4, S5, S6, S7, S8
Right side:  EN, V+, A, B, C, V-, X, GND
```

---

## 4. Building Each Subsheet

### Sheet 1: Power Supplies (`power.kicad_sch`)

**Components** (Place → Symbol, `A` key):
```
J1  - 2-pin terminal block (12V DC input)
F1  - Polyfuse, 1A (Device library)
D1  - SS34 Schottky diode (Device: D_Schottky)
U1  - LM7805 (TO-220, your custom symbol)
U2  - AMS1117-3.3 (SOT-223, your custom symbol)
C1  - 100nF ceramic (Device: C)
C2  - 10µF electrolytic (Device: C_Polarized)
C3  - 100nF ceramic
C4  - 10µF electrolytic
```

**Power symbols** (Place → Power Symbol, `P` key):
- Place `+12V` at input rail
- Place `+5V` at U1 output rail  
- Place `+3.3V` at U2 output rail
- Place `GND` at bottom rail

**Wiring**:
```
J1 → F1 → D1 → U1(VIN)
U1(VOUT) → C2 → +5V rail
U1(VOUT) → U2(VIN) via +5V rail
U2(VOUT) → C4 → +3.3V rail
U1/U2 GND pins → GND rail
C1 across U1 input, C3 across U2 input
```

**Hierarchical pins** (outgoing):
```
+12V, +5V, +3.3V, GND
```

---

### Sheet 2: Analog Frontend (`analog.kicad_sch`)

**Components per channel** (×8):
```
Z0-Z7  - 100Ω resistor (matching)
R0a-R7a - 10kΩ resistor (bias)
D0-D31 - 1N4148 diodes (4 per channel for bridge)
```

**MUX ICs**:
```
U1 - DG408 (channels 0-3)
U2 - DG408 (channels 4-7)
```

**LNA ICs**:
```
U3 - OPA1641 (RX0)
U4 - OPA1641 (RX1)
```

**Passive networks**:
```
C3, C6  - 100pF (input coupling)
R5, R31 - 1kΩ (gain set)
R6, R32 - 10kΩ (feedback)
```

**Layout approach** (left to right):
1. **Left edge**: Hierarchical pins (TX_BUS, MUX_A..MUX_EN)
2. **Left block**: 8 T/R bridge channels stacked vertically
3. **Center**: U1 (top) and U2 (bottom) — 20mm gap between them
4. **Right**: U3 (top) and U4 (bottom)
5. **Far right**: Output pins (RX0_OUT, RX1_OUT)
6. **Top edge**: Power pins (+5V, +12V, GND)

**Wiring order** (to avoid overlaps):
1. Draw TX_BUS horizontal from left pin, tap to each channel bridge
2. Draw channel outputs (8 horizontal wires) to center routing area
3. Use L-wires (Place → Wire with corners) from channel outputs to MUX inputs
4. Draw MUX control lines from top-left pins, stagger x-positions for each signal
5. MUX outputs → capacitors → LNA inputs
6. Feedback resistors to right of each LNA
7. Power drops from top rail to each IC (place outside component edges)

**Critical net names**:
```
CH0_OUT..CH7_OUT   (between bridge and MUX)
MUX0_OUT, MUX1_OUT (MUX outputs to LNAs)
RX0_OUT, RX1_OUT   (LNA outputs)
```

---

### Sheet 3: Digital Control (`digital.kicad_sch`)

**Components**:
```
J3  - 40-pin header (RP E1 GPIO)
U5  - 74HCT595 (shift register)
R3-R10 - 100Ω (gate resistors)
Q1-Q8  - BSS138 (MOSFET drivers)
```

**Layout** (left to right):
1. **Left edge**: Hierarchical input pins (SER, SRCLK, RCLK, ~OE, SRCLR, +5V, GND)
2. **Left**: J3 connector (representing E1 header)
3. **Center**: U5 shift register
4. **Right**: 8× resistor + BSS138 pairs, stacked vertically
5. **Right edge**: GATE0..GATE7 output pins

**Wiring**:
```
J3 pins → U5 pins (5 green SPI wires, staggered entry)
U5 QA..QH → R3..R10 → Q1..Q8 gates
Q1..Q8 sources → common GND bus (vertical left of FETs)
Q1..Q8 drains → GATE0..GATE7 outputs
```

**Net naming**:
```
SER, SRCLK, RCLK, OE, SRCLR  (SPI bus)
MUX_A, MUX_B, MUX_C, MUX_EN  (from shift register, decoded)
GATE0..GATE7                 (drain outputs)
```

**Note**: In the actual design, a 3-to-8 decoder or additional shift register generates MUX_A..MUX_EN from the 74HCT595 outputs. Document this clearly with a text note.

---

### Sheet 4: TX Switch (`tx_switch.kicad_sch`)

**Components**:
```
U1-U4  - TC4427 (4 dual drivers = 8 channels)
Q1-Q8  - IRF830 (HV MOSFETs)
4× 100nF - decoupling caps (one per driver)
```

**Layout** (left to right):
1. **Left edge**: GATE0..GATE7 inputs, +12V, GND
2. **Left-center**: 4 TC4427 drivers, spaced horizontally (28mm apart)
3. **Right**: 8 IRF830 MOSFETs, stacked vertically (7mm spacing)
4. **Far right**: TX_BUS output pin

**Wiring** (crucial — avoid overlaps):
```
GATE0..GATE7 → horizontal to x=38
L-wires from x=38 to each driver input (A_in/B_in)
   - U1: GATE0→A_in, GATE1→B_in
   - U2: GATE2→A_in, GATE3→B_in
   - etc.

Driver outputs → L-wires to MOSFET gates:
   - From (driver_x+10, out_y) to (driver_x+20, out_y)
   - Then vertical to channel y
   - Then horizontal to x=160
   - Then to MOSFET gate at x=175-8=167

MOSFET sources → vertical down to common source bus
Source bus → GND rail

MOSFET drains → horizontal to TX_BUS rail
```

**Power**:
```
+12V rail at top → each driver VCC pin
GND rail at bottom → each driver GND + source bus
```

---

## 5. Power Distribution Strategy

### Global Power Symbols

Use **Place → Power Symbol** for these nets (they connect implicitly across sheets):
```
+12V  (red)
+5V   (blue)
+3.3V (lighter blue)
GND   (gray/black)
```

### Sheet-Specific Power Pins

On each subsheet, add **hierarchical pins** for power:
```
Analog:  +5V (MUX), +12V (LNA), GND
Digital: +5V, GND
TX:      +12V, GND
Power:   (generates all rails)
```

**Important**: On each subsheet, place the power symbols and connect them to the hierarchical pins. This makes power flow explicit and ERC-checkable.

---

## 6. ERC (Electrical Rules Check)

Run **Inspect → Electrical Rules Checker** frequently.

### Common ERC Issues to Fix

| Error | Cause | Fix |
|-------|-------|-----|
| "Pin not driven" | Input pin with no source | Check hierarchical pin direction (IN vs OUT) |
| "Power pin not connected" | VCC/GND not wired | Add power symbols, not just labels |
| "No connection for pin X" | NC pins | Place "No Connect" flag (`Q` key) on unused pins |
| "Duplicate net name" | Same label on different nets | Merge or rename |
| "Hierarchical pin not matched" | Sheet pin missing in parent | Check root sheet has matching pin |

### TurboQuant-Specific ERC Notes

```
DG408 pins:
  - Unused analog inputs: No Connect (if <8 channels used)
  - V+ pin: Must connect to +5V power symbol
  - V- pin: Connect to GND (single supply)

OPA1641 pins:
  - Unused op-amp in dual package: No Connect or buffer to ground
  - Power pins: +5V and GND (not +12V! LNAs run on +5V)

TC4427 pins:
  - Unused inputs: Tie to GND (don't float)
  - VDD: +12V, VSS: GND

IRF830 pins:
  - Gate: High-Z, needs pull-down when off
  - Body diode: Implicit in symbol, no extra diode needed
```

---

## 7. Annotation & RefDes Strategy

**Tools → Annotate Schematic** (`Ctrl+Shift+A`):

Use ** sheet-based annotation** for clarity:
```
Power sheet:      U1-U2, J1, F1, D1, C1-C4
Analog sheet:     U1-U4, D1-D32, R1-R32, C3-C6
Digital sheet:    U5, J3, R3-R10, Q1-Q8
TX sheet:         U1-U4, Q1-Q8
```

KiCad will handle cross-sheet uniqueness automatically. The "U1" in analog and "U1" in TX are different because they're on different sheets — KiCad uses full path annotation.

---

## 8. Net Classes Setup

**File → Schematic Setup → Project → Net Classes**:

Create these net classes for PCB layout hints:

| Net Class | Nets | Trace Width | Clearance | Purpose |
|-----------|------|-------------|-----------|---------|
| Power_12V | +12V, VDD | 1.0mm | 0.5mm | High current drivers |
| Power_5V | +5V | 0.6mm | 0.3mm | Digital/analog supply |
| Power_3V3 | +3.3V | 0.4mm | 0.3mm | Logic supply |
| HV_Pulse | TX_BUS | 1.5mm | 2.0mm | 100V pulse, needs isolation |
| Analog | CH*_OUT, MUX*_OUT, RX*_OUT | 0.3mm | 0.5mm | Sensitive analog |
| Digital | SER, SRCLK, RCLK, GATE* | 0.25mm | 0.25mm | Digital control |

---

## 9. BOM Generation

**Tools → Generate Bill of Materials**:

Fields to include:
```
Reference, Value, Footprint, Datasheet, Manufacturer, MPN, Supplier, Cost
```

Pre-populated fields during schematic entry save time later.

---

## 10. Tips for This Specific Design

### Diode Bridge Arrays
Instead of placing 32 individual diodes (4 per channel × 8), consider:
- **BAV99 dual diode arrays** (2 per package) — reduces part count
- **Schottky bridge modules** (integrated 4-diode bridge) — better matching

### High-Voltage Clearances
For the TX switch:
- TX_BUS carries ±100V pulses
- Keep TX_BUS traces away from low-voltage signals (>2mm clearance)
- Use thicker traces (1.5mm+) for TX_BUS
- Consider guard rings around HV areas

### MUX Routing
The DG408 analog MUX passes ±100V when off. Ensure:
- Analog inputs have protection diodes to rails
- MUX power supply (+5V) can handle fault current briefly
- Output has series resistor before LNA (already in design: C3/C6 + input resistance)

### Decoupling Strategy
```
Every IC gets a 100nF ceramic as close as possible to power pins:
  - U1(DG408): pin 16(V+) to GND
  - U3/U4(OPA1641): between V+ and V-
  - U1-U4(TC4427): between VDD and GND
  - U5(74HCT595): pin 16(VCC) to GND
  - U2(AMS1117): input + output caps (C3+C4)
```

---

## Quick Reference: KiCad Shortcuts

| Action | Key |
|--------|-----|
| Place Symbol | `A` |
| Place Wire | `W` |
| Place Label | `L` |
| Place Hierarchical Sheet | `S` |
| Place Hierarchical Pin | `P` (in sheet) |
| Place Power Symbol | `P` (global) |
| Place No Connect | `Q` |
| Place Junction | `J` (auto-placed on T-junctions) |
| Annotate | `Ctrl+Shift+A` |
| ERC | `I` → Electrical Rules Checker |
| Save | `Ctrl+S` |

---

## Files You'll Create

```
TurboQuant_v5/
├── TurboQuant_v5.kicad_pro        # Project file
├── TurboQuant_v5.kicad_sch        # Root schematic
├── power.kicad_sch                # Subsheet 1
├── analog.kicad_sch               # Subsheet 2
├── digital.kicad_sch             # Subsheet 3
├── tx_switch.kicad_sch            # Subsheet 4
├── turboquant_library.kicad_sym   # Custom symbols
├── sym-lib-table                   # Library references
└── fp-lib-table                    # (for PCB, later)
```

---

*Start with the root sheet, add the 4 hierarchical blocks, then drill into each subsheet. Build power first (simplest), then digital, then analog, then TX switch (most complex wiring). Run ERC after completing each sheet.*
