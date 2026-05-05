# TurboQuant System Integration Guide

Complete physical connection diagram for the 8-element ultrasound NDE system.

---

## 🎯 System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ULTRASOUND NDE SYSTEM                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌──────────────┐         ┌──────────────────┐         ┌──────────────┐    │
│   │   PROBE      │         │   TURBOQUANT     │         │  RED PITAYA  │    │
│   │  (8-element) │←───────→│   MUX LNA BOARD  │←───────→│   STEMLAB    │    │
│   │              │ 8×SMA   │                  │ 3×GPIO  │   125-14     │    │
│   │ EL0 ──┐      │         │  ┌────────────┐  │         │              │    │
│   │ EL1 ──┤      │         │  │ 74HC595    │  │         │ ┌──────────┐ │    │
│   │ EL2 ──┤      │         │  │ (8→1 TX)   │  │         │ │ Zynq     │ │    │
│   │ EL3 ──┼──────┤         │  └────────────┘  │         │ │  FPGA    │ │    │
│   │ EL4 ──┤      │         │  ┌────────────┐  │         │ └────┬─────┘ │    │
│   │ EL5 ──┤      │         │  │ 2×CD4051B  │  │         │      │       │    │
│   │ EL6 ──┤      │         │  │ (8→2 RX)   │  │         │ ┌────┴─────┐ │    │
│   │ EL7 ──┘      │         │  └────────────┘  │         │ │   ADC    │ │    │
│   │              │         │  ┌────────────┐  │         │ │ IN1/IN2  │ │    │
│   └──────────────┘         │  │ 2×OPA657   │  │         │ └──────────┘ │    │
│                            │  │   LNA      │  │         │              │    │
│                            │  └────────────┘  │         └──────────────┘    │
│                            └──────────────────┘              ↑               │
│                                                              │               │
│                                                         ┌────┴────┐          │
│                                                         │  HOST   │          │
│                                                         │  (PC)   │          │
│                                                         └─────────┘          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔌 Physical Connections

### 1. Ultrasound Probe → TurboQuant Board

**Connection:** 8 × SMA coaxial cables (or single multi-conductor cable)

| Probe Element | TurboQuant Port | Signal Type |
|---------------|-----------------|-------------|
| Element 0 | EL0 (SMA) | TX/RX bidirectional |
| Element 1 | EL1 (SMA) | TX/RX bidirectional |
| Element 2 | EL2 (SMA) | TX/RX bidirectional |
| Element 3 | EL3 (SMA) | TX/RX bidirectional |
| Element 4 | EL4 (SMA) | TX/RX bidirectional |
| Element 5 | EL5 (SMA) | TX/RX bidirectional |
| Element 6 | EL6 (SMA) | TX/RX bidirectional |
| Element 7 | EL7 (SMA) | TX/RX bidirectional |

**Cable Requirements:**
- Type: RG316 or RG174 (flexible coax)
- Impedance: 50Ω
- Length: Matched within 1cm (for phase consistency)
- Connectors: SMA male (probe) → SMA female (board)

**Probe Specifications (Typical):**
- Frequency: 1-10 MHz (NDE applications)
- Element pitch: 0.5-2mm (linear array)
- Impedance: ~50Ω
- Capacitance: ~100-500 pF per element

---

### 2. TurboQuant Board → Red Pitaya

**Connection:** E1 GPIO Header (2×10 pin, 2.54mm pitch)

| TurboQuant Signal | TurboQuant Pin | Red Pitaya E1 | FPGA Pin | Type |
|-------------------|----------------|---------------|----------|------|
| SER (Serial Data) | J2 Pin 1 | DIO0_P | G18 | Output |
| SRCLK (Shift Clock) | J2 Pin 3 | DIO0_N | G17 | Output |
| RCLK (Latch Clock) | J2 Pin 5 | DIO1_P | H17 | Output |
| GND | J2 Pin 2,4,6,8... | GND | - | Ground |
| +5V (Optional) | - | +5V | - | Power |

**Cable:**
- 20-pin ribbon cable (2×10)
- Female-to-female IDC connectors
- Length: 10-30cm (keep short for signal integrity)

**Note:** TurboQuant has onboard 5V regulator (12V→5V), but can optionally use Red Pitaya's +5V.

---

### 3. Red Pitaya → Host PC

**Connection 1: Ethernet (Primary)**
```
Red Pitaya RJ45 ←──Cat5e/6──→ Router/Switch ←──→ Host PC
                         (or direct connection)
```
- IP: Static 192.168.1.100 (default) or DHCP
- Protocol: SSH, SCP, HTTP (web interface)

**Connection 2: USB (Console)**
```
Red Pitaya Micro-USB ←→ USB Cable ←→ Host PC
```
- Serial console (115200 baud)
- Power (if not using external)
- For debugging only

---

## ⚡ Power Distribution

### Power Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      POWER ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐                                           │
│  │  12V DC      │←── Wall Adapter (2A minimum)              │
│  │  Supply      │    or Battery Pack                        │
│  └──────┬───────┘                                           │
│         │                                                    │
│    ┌────┴────┬──────────────┐                               │
│    ↓         ↓              ↓                               │
│ ┌──────┐  ┌──────┐      ┌──────┐                           │
│ │LM7805│  │      │      │      │                           │
│ │5V    │  │Turbo-│      │Red   │                           │
│ │Reg   │  │Quant │      │Pitaya│                           │
│ └──┬───┘  │Power │      │Power │                           │
│    │      │Distrib│      │      │                           │
│    ↓      └──────┘      └──┬───┘                           │
│ ┌──────┐                   │                                │
│ │AMS   │←── 3.3V ──────────┘                                │
│ │1117  │     (for logic)                                    │
│ │3.3V  │                                                    │
│ └──────┘                                                    │
│    │                                                        │
│    ↓                                                        │
│ ┌────────────────────────────────────────┐                  │
│ │  3.3V Loads:                           │                  │
│ │  • 74HC595 (shift register)            │                  │
│ │  • CD4051B (muxes, 2×)                 │                  │
│ │  • OPA657 (LNAs, 2× - ±5V rails)       │                  │
│ └────────────────────────────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

### Power Requirements

| Board | Input | Current (Typ) | Current (Max) |
|-------|-------|---------------|---------------|
| TurboQuant | 12V DC | 50mA | 200mA |
| Red Pitaya | 5V DC or 12V DC | 300mA | 800mA |
| **Total** | 12V | 350mA | **1A** |

**Recommended Supply:** 12V DC, 2A minimum

---

## 📡 Signal Flow

### TX Mode (Transmit)

```
┌─────────────────────────────────────────────────────────────────┐
│                     TRANSMIT SIGNAL FLOW                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Red Pitaya                                                     │
│  ┌──────────┐    GPIO    ┌──────────────┐    74HC595           │
│  │   FPGA   │── SER ───→│  Shift Reg   │── GATE0-7 ──┐         │
│  │          │── SRCLK ─→│  (8-bit)     │             │         │
│  │          │── RCLK ──→│              │             │         │
│  └──────────┘           └──────────────┘             │         │
│                                                       ↓         │
│                                             ┌──────────────┐    │
│                                             │  MOSFET      │    │
│                                             │  Switches    │    │
│                                             │  (8× BSS138) │    │
│                                             └──────┬───────┘    │
│                                                    │            │
│  Probe                                            ↓            │
│  ┌──────────┐                             ┌──────────────┐    │
│  │ Element  │←── HV Pulse (±1V to ±100V)──┤ TX_IN (SMA)  │    │
│  │   0-7    │         (Selectable)        │              │    │
│  └──────────┘                             └──────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

**Timing:**
1. FPGA loads 8-bit pattern (one-hot)
2. RCLK latches pattern to outputs
3. Selected GATE goes HIGH
4. MOSFET switch closes
5. TX pulse drives selected element

**Switch Time:** ~10μs (74HC595 shift + latch)

---

### RX Mode (Receive)

```
┌─────────────────────────────────────────────────────────────────┐
│                    RECEIVE SIGNAL FLOW                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Probe                                                          │
│  ┌──────────┐    Weak echo      ┌──────────────┐               │
│  │ Element  │── (mV range) ────→│  T/R Switch  │               │
│  │   0-7    │                   │  (BAV99      │               │
│  └──────────┘                   │   diodes)    │               │
│                                 └──────┬───────┘               │
│                                        │                       │
│                                        ↓                       │
│  TurboQuant                  ┌──────────────┐                  │
│  ┌──────────┐                │  CD4051B     │                  │
│  │ Element  │───────────────→│  8:1 Mux     │                  │
│  │ Lines    │   (Selected    │  (×2 banks)  │                  │
│  └──────────┘    by FPGA)    └──────┬───────┘                  │
│                                     │                          │
│                                     ↓                          │
│                              ┌──────────────┐                  │
│                              │  OPA657 LNA  │                  │
│                              │  (Low Noise  │                  │
│                              │   Amplifier) │                  │
│                              └──────┬───────┘                  │
│                                     │                          │
│                                     ↓                          │
│  Red Pitaya                 ┌──────────────┐                   │
│  ┌──────────┐    Analog     │   ADC IN1    │                   │
│  │   ADC    │←── (amplified)│   or IN2     │                   │
│  │125MSa/s  │               │  (±1V range) │                   │
│  └──────────┘               └──────────────┘                   │
│       │                                                        │
│       ↓                                                        │
│  ┌──────────┐                                                  │
│  │   Zynq   │                                                  │
│  │   ARM    │←── Digital samples                               │
│  │  + FPGA  │     (14-bit, 125MHz)                             │
│  └──────────┘                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Signal Chain Gain:**
1. Element output: ~10μV - 100mV
2. T/R switch loss: ~0.3dB
3. CD4051B loss: ~0.5dB
4. OPA657 gain: ~20-40dB (set by resistors)
5. ADC input: Optimized to ±1V full scale

---

## 🔧 Mechanical Integration

### Enclosure Layout

```
┌──────────────────────────────────────────────────────────────┐
│                    ENCLOSURE (Top View)                       │
│                    200mm × 150mm × 80mm                       │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│   ┌────────────┐    ┌────────────┐    ┌────────────┐        │
│   │  RED       │    │  TURBO-    │    │  12V       │        │
│   │  PITAYA    │    │  QUANT     │    │  POWER     │        │
│   │  (FPGA)    │    │  (MUX/LNA) │    │  INPUT     │        │
│   │            │    │            │    │            │        │
│   │  Ethernet──┼────┤            │    │  Barrel    │        │
│   │  USB───────┤    │  8×SMA─────┼────┤  Jack      │        │
│   │            │    │  (to probe)│    │            │        │
│   └────────────┘    └────────────┘    └────────────┘        │
│          ↑                 ↑                                   │
│          │                 │                                   │
│          └─────────────────┘                                   │
│         20-pin ribbon cable                                   │
│                                                               │
│   [Probe Connector: 8×SMA or custom multi-pin]               │
│                    ↑                                          │
│                    │                                          │
│              ┌──────────┐                                     │
│              │  PROBE   │  (External, handheld)               │
│              │ (8-elem) │                                     │
│              └──────────┘                                     │
└──────────────────────────────────────────────────────────────┘
```

### Cable Management

| Connection | Cable Type | Length | Routing |
|------------|------------|--------|---------|
| Probe → TurboQuant | 8× SMA | 0.5-2m | External (flexible) |
| TurboQuant → Red Pitaya | 20-pin ribbon | 10-20cm | Internal (short) |
| Red Pitaya → Host | Cat6 Ethernet | 1-10m | External |
| Power → System | Barrel jack | 1-2m | External |

---

## 🧪 Probe Interface Details

### Custom Probe Connector (Recommended)

**Option 1: 8× SMA Bulkhead Panel**
```
┌─────────────────────────────┐
│  Panel Mount (Rear)         │
│                             │
│  [SMA] [SMA] [SMA] [SMA]    │  ← Elements 0-3
│  [SMA] [SMA] [SMA] [SMA]    │  ← Elements 4-7
│                             │
│        [    CABLE    ]      │  ← To probe
└─────────────────────────────┘
```

**Option 2: High-Density Connector (Lemo, Fischer, or custom)**
- 16-pin connector (8 signals + 8 grounds)
- Shielded twisted pairs
- Locking mechanism for reliability
- Better for handheld NDE probes

### Probe Cable (Flexible)

**Construction:**
- 8× coaxial lines (micro-coax, ~1mm OD)
- Common braided shield
- Polyurethane jacket
- Strain relief at both ends

**Specifications:**
- Length: 1-2 meters typical
- Flex life: >10,000 cycles
- Temperature: -20°C to +80°C
- Chemical resistant (for NDE coupling gel)

---

## 📋 Assembly Checklist

### Mechanical
- [ ] Mount Red Pitaya in enclosure
- [ ] Mount TurboQuant board
- [ ] Install SMA bulkhead connectors (8×)
- [ ] Route ribbon cable (E1 connection)
- [ ] Install power jack
- [ ] Install Ethernet/USB cutouts

### Electrical
- [ ] Connect 20-pin E1 ribbon cable
- [ ] Connect 12V power to TurboQuant
- [ ] Connect SMA cables (element 0-7)
- [ ] Verify 5V and 3.3V rails
- [ ] Test continuity on all signals
- [ ] Check for shorts

### Initial Power-Up
- [ ] Power on without FPGA bitstream
- [ ] Verify LEDs on both boards
- [ ] Check voltages: 12V, 5V, 3.3V
- [ ] Load FPGA bitstream
- [ ] Run Python control script
- [ ] Test element selection (all 8)

---

## ⚠️ Important Notes

### T/R Switching
- TurboQuant has T/R (Transmit/Receive) switches per element
- When TX pulse is active, RX path is protected (clamped)
- After TX, switch opens for RX within microseconds
- **Critical:** Don't TX and RX simultaneously on same element

### Grounding
- Single-point ground at power supply
- All shields connected at enclosure
- Avoid ground loops
- Use coaxial cables (shield = return path)

### Thermal
- OPA657 LNAs may warm up during operation
- Ensure ventilation in enclosure
- Monitor for thermal drift in calibration

### Safety
- 12V DC only (isolated from mains)
- Low voltage system (safe to touch)
- TX pulses are low energy (safe)
- Standard lab safety practices apply

---

## 🔗 Complete System Bill of Materials

| Item | Description | Qty | Source |
|------|-------------|-----|--------|
| Red Pitaya | STEMlab 125-14 Gen 2 | 1 | redpitaya.com |
| TurboQuant | Mux LNA board (your PCB) | 1 | JLCPCB/assembly |
| Probe | 8-element linear array | 1 | NDT supplier |
| Enclosure | 200×150×80mm ABS/Al | 1 | Hammond/eBay |
| Power Supply | 12V DC, 2A | 1 | Amazon/Digi-Key |
| SMA Cables | RG316, SMA-M to SMA-M | 8 | Amazon |
| Ribbon Cable | 20-pin IDC, 20cm | 1 | Digi-Key |
| Ethernet Cable | Cat6, 2m | 1 | Local |

---

## 📸 Physical Photos (To Be Added)

Once assembled, document:
1. Overall system view
2. Internal wiring
3. Probe connection
4. Oscilloscope capture of TX/RX signals

---

## 🚀 Next Steps

1. **Order PCBs:** JLCPCB with assembly for TurboQuant
2. **Order Probe:** Contact NDE supplier or fabricate
3. **Mechanical:** Design/print enclosure
4. **Assembly:** Solder and connect
5. **Test:** Run Python script to verify all elements
6. **Calibration:** Characterize each channel
7. **Imaging:** Implement delay-and-sum beamforming in software

Questions about any specific connection?