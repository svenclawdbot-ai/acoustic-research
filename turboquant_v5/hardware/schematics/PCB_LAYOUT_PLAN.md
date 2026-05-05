# PCB Layout Plan — TurboQuant V5

## Board Specifications
- **Dimensions:** 100mm × 80mm
- **Layers:** 4-layer
- **Stackup:**
  - Layer 1 (Top): Signal + components
  - Layer 2 (In1): GND plane
  - Layer 3 (In2): Power plane (+5V, +12V)
  - Layer 4 (Bottom): Signal + components

## Zone Partitioning

```
┌─────────────────┬─────────────────┐
│   POWER         │   DIGITAL       │
│   (top-left)    │   (top-right)   │
│   25×40mm       │   25×40mm       │
│                 │                 │
│   LM7805 DPAK   │   74HCT595      │
│   AMS1117-3.3   │   BSS138 ×8     │
│   12V input     │   E1 connector  │
│   terminal      │                 │
├─────────────────┼─────────────────┤
│   ANALOG        │   TX SWITCH     │
│   (center)      │   (bottom)      │
│   50×40mm       │   50×40mm       │
│                 │                 │
│   DG408 ×2      │   IRF830 ×8     │
│   OPA1641 ×2    │   TC4427 ×4     │
│   T/R bridges   │   Heatsink area │
│   ×8 channels   │   TX connector  │
└─────────────────┴─────────────────┘
```

## Component Placement

### Power Zone (0,0 to 25,40)
| Component | Position | Notes |
|-----------|----------|-------|
| J1 (12V input) | (5, 20) | Screw terminal, board edge |
| F1 (polyfuse) | (10, 20) | Near input |
| D1 (SS34) | (15, 20) | Reverse protection |
| U1 (LM7805) | (12, 30) | DPAK, copper pour under tab |
| U2 (AMS1117) | (18, 30) | SOT-223 |
| C1-C6 | Around regulators | 100nF + 10µF each |

### Digital Zone (25,0 to 50,40)
| Component | Position | Notes |
|-----------|----------|-------|
| J3 (E1 GPIO) | (45, 20) | 2×10 header, board edge |
| U5 (74HCT595) | (35, 25) | SOIC-16 |
| Q1-Q8 (BSS138) | (30-40, 10-35) | SOT-23, near 74HCT595 outputs |
| R1-R8 (gate series) | Between U5 and Q1-Q8 | 100Ω each |

### Analog Zone (0,40 to 50,80)
| Component | Position | Notes |
|-----------|----------|-------|
| U3 (DG408-0) | (15, 55) | SOIC-16, MUX0 |
| U4 (DG408-1) | (15, 65) | SOIC-16, MUX1 |
| U6 (OPA1641-0) | (35, 55) | SOIC-8, LNA0 |
| U7 (OPA1641-1) | (35, 65) | SOIC-8, LNA1 |
| D1-D32 (MUR120) | (5-20, 45-75) | DO-41, 4 per channel |
| R9-R32 (bias) | Near diodes | 10kΩ + 100kΩ per channel |
| Z1-Z8 (BZX84C5V1) | Near bias networks | SOD-323 |
| C7-C10 (DC block) | Near MUX outputs | 100nF |
| R33-R40 (attenuator) | Near LNAs | 9.09kΩ + 1kΩ |
| D33-D34 (BAV99) | Near LNA inputs | SOT-23 |

### TX Switch Zone (50,40 to 100,80)
| Component | Position | Notes |
|-----------|----------|-------|
| U8-U11 (TC4427) | (55, 50-70) | SOIC-8, 2 channels each |
| Q9-Q16 (IRF830) | (70-85, 45-75) | TO-220, heatsink area |
| R41-R48 (gate 10Ω) | Between TC4427 and IRF830 | 0603 |
| R49-R56 (pull-down 1kΩ) | Near gates | 0603 |
| Z9-Z16 (BZX84C12) | Near gates | SOD-323 |
| J2 (TX_BUS) | (95, 60) | SMA edge connector |
| C11-C14 (decoupling) | Near TC4427 | 100nF |

## Critical Layout Rules

### High Voltage (TX paths)
- **Clearance:** >2mm between TX traces and any other signals
- **Width:** TX_BUS trace ≥1mm (for 2A peak)
- **Drains:** Short, wide traces from IRF830 drains to TX_BUS
- **Isolation:** No vias on TX traces near sensitive analog

### Gate Drive
- **Length:** Gate traces <20mm from TC4427 to IRF830
- **Width:** 0.25mm minimum
- **Return path:** Direct GND return, no loops
- **Damping:** 10Ω resistor at TC4427 output

### Analog (RX paths)
- **Guarding:** Ground pour around LNA inputs
- **Length:** MUX-to-LNA traces <30mm
- **Shielding:** GND vias around attenuator network
- **Decoupling:** 100nF at each DG408 VDD pin

### Power Distribution
- **+12V:** Wide trace (≥0.5mm) from input to regulators and TX zone
- **+5V:** Power plane on In2 layer, stitched vias
- **GND:** Solid plane on In1 layer, minimal splits
- **Decoupling:** 100nF within 5mm of each IC power pin

## Layer Usage

### Top Layer (F.Cu)
- Component pads and short traces
- TX_BUS routing (wide, isolated)
- Gate drive traces (short, direct)
- Analog signal traces (guarded)

### Inner Layer 1 (In1.Cu) — GND Plane
- Solid ground plane under analog and digital
- Stitched vias every 10mm
- Keep-out under TX_BUS (HV isolation)

### Inner Layer 2 (In2.Cu) — Power Plane
- +5V pour (digital and analog)
- +12V pour (TX zone)
- Split at analog/TX boundary

### Bottom Layer (B.Cu)
- Additional signal routing
- GND connections for bottom components
- Test points and programming headers

## Manufacturing Notes
- **Min trace/space:** 0.15mm/0.15mm
- **Via:** 0.3mm drill, 0.6mm pad
- **Silkscreen:** Component designators, zone labels
- **Fabrication:** Standard FR4, 1.6mm thickness
- **Assembly:** SMD first, then THT (MUR120, IRF830)

---
*Layout plan generated: 2026-04-26*
*Next: Component placement in KiCad PCB editor*