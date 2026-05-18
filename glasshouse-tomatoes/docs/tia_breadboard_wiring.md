# TIA Breadboard Wiring Guide — GlassHouse Node v1.0
*Build the analog front-end in 30 minutes. Every wire, every resistor, every pin.*

---

## 🧰 BEFORE YOU START

### Parts on Your Desk
| Qty | Part | Check |
|-----|------|-------|
| 1 | ESP32-S3-DevKitC-1 | ☐ |
| 1 | AD9833 DDS module | ☐ |
| 1 | OPA1641 DIP-8 | ☐ |
| 1 | LM358 DIP-8 | ☐ |
| 1 | DS18B20 waterproof probe | ☐ |
| 2 | Breadboard (half-size, 400 tie-points) | ☐ |
| | **Resistors** | |
| 2 | 10 kΩ (brown-black-black-red-brown) | ☐ |
| 1 | 1 kΩ (brown-black-black-brown-brown) | ☐ |
| 1 | 100 Ω (brown-black-black-gold-brown) | ☐ |
| 2 | 100 kΩ (brown-black-black-orange-brown) | ☐ |
| 1 | 4.7 kΩ (yellow-violet-black-brown-brown) | ☐ |
| | **Capacitors** | |
| 1 | 100 nF ceramic (104 marking) | ☐ |
| 2 | 100 nF ceramic (104 marking) — decoupling | ☐ |
| 1 | 10 µF electrolytic | ☐ |
| | **Wire** | |
| ~20 | Dupont M-M (male-male) 20 cm | ☐ |
| ~10 | Dupont M-F (male-female) 20 cm | ☐ |
| ~5 | Solid core 22 AWG, various colours | ☐ |

### Tools Needed
- Multimeter (continuity + voltage)
- Soldering iron (only for electrodes — everything else is breadboard)
- Wire strippers
- Flush cutters

### Safety
- **Power off** when moving ICs or changing wiring
- **Check polarity** on electrolytic capacitors
- **Never short** the 18650 battery terminals

---

## 🗺️ BREADBOARD LAYOUT OVERVIEW

We use **two half-size breadboards** side by side:

```
┌─────────────────────────────┬─────────────────────────────┐
│     BREADBOARD 1            │     BREADBOARD 2            │
│     (Analog)                │     (Digital + Power)       │
│                             │                             │
│  ┌─────────┐                │  ┌─────────┐  ┌─────────┐   │
│  │ OPA1641 │                │  │ LM358   │  │ AD9833  │   │
│  │  (TIA)  │                │  │ (Buffer)│  │  (DDS)  │   │
│  └─────────┘                │  └─────────┘  └─────────┘   │
│                             │                             │
│  1.65V bias                 │  ESP32-S3 connections       │
│  Electrode B input          │  DS18B20 temp               │
│  TIA output → ADC           │  Battery divider            │
│                             │                             │
└─────────────────────────────┴─────────────────────────────┘
```

---

## 📐 STEP 0: UNDERSTAND THE BREADBOARD

```
         A B C D E F G H I J
      ┌────────────────────────┐
   1  │ ● ● ● ● ●   ● ● ● ● ● │  ← Row 1 (power rail area)
      │ ● ● ● ● ●   ● ● ● ● ● │  ← Row 2
      │ ● ● ● ● ●   ● ● ● ● ● │  ← Row 3
      │  ... 10 rows total ... │
   10 │ ● ● ● ● ●   ● ● ● ● ● │  ← Row 10
      └────────────────────────┘
          │ │ │ │ │   │ │ │ │ │
          └─┴─┴─┴─┘   └─┴─┴─┴─┘
           Left bus     Right bus
           (A–E)        (F–J)

    Top red/blue strips: Power rails (+3.3V / GND)
    Bottom red/blue strips: Power rails (+3.3V / GND)
```

**Rule:** Each row's 5 holes (A–E or F–J) are connected horizontally. The gap in the middle is NOT connected. The power rails run the full length vertically.

---

## 🔌 STEP 1: POWER RAILS

**On BOTH breadboards:**

1. Connect the **top red (+) rail** to **bottom red (+) rail** with a red jumper wire at each end
2. Connect the **top blue (-) rail** to **bottom blue (-) rail** with a blue jumper wire at each end
3. Connect ** Breadboard 1 red rail** to **Breadboard 2 red rail** with a red wire
4. Connect **Breadboard 1 blue rail** to **Breadboard 2 blue rail** with a blue wire

```
    Breadboard 1                Breadboard 2
    ┌──────────┐                ┌──────────┐
    │ +  +++++ │←red wire→│ +  +++++ │
    │ -  ----- │←blue→│ -  ----- │
    │          │                │          │
    │          │                │          │
    │ -  ----- │←blue→│ -  ----- │
    │ +  +++++ │←red wire→│ +  +++++ │
    └──────────┘                └──────────┘
```

**Result:** One unified 3.3V rail and one unified GND rail across both breadboards.

---

## ⚡ STEP 2: 1.65V BIAS (Mid-Rail Reference)

The OPA1641 TIA needs its (+) input sitting at half the supply voltage so the AC signal can swing both up and down without hitting the rails.

**On Breadboard 1, left side (columns A–E):**

```
    Row 1:  [3.3V]──[10kΩ]──[●]──[10kΩ]──[GND]
                              │
    Row 2:                   [100nF]
                              │
    Row 3:                  [GND]
```

**Wiring:**
1. Place **10kΩ resistor** between **3.3V rail** and **hole E1**
2. Place **10kΩ resistor** between **hole E1** and **GND rail**
3. Place **100nF capacitor** between **hole E2** and **GND rail** (any row on blue rail)
   - Ceramic capacitor: no polarity. Either way round.
4. **Hole E1** is now your **1.65V bias point**. We'll call this **BIAS** from now on.

**Check with multimeter:**
- Red probe on E1, black on GND → should read **~1.65V**

---

## 🔊 STEP 3: AD9833 DDS MODULE

Place the AD9833 module on **Breadboard 2, right side** (columns F–J).

```
    AD9833 Module Pinout (top view, looking at component side)
    ┌─────────────────┐
    │ VCC  GND  DAT  CLK  FSYN │
    │  ●    ●    ●    ●    ●   │
    └─────────────────┘
```

**Connections:**

| AD9833 Pin | Connect To | Wire Colour | Notes |
|------------|-----------|-------------|-------|
| **VCC** | 3.3V rail | Red | Power |
| **GND** | GND rail | Blue | Ground |
| **DAT** (SDATA) | ESP32 GPIO 11 | Yellow | MOSI / data |
| **CLK** (SCLK) | ESP32 GPIO 12 | Orange | SPI clock |
| **FSYN** (FSYNC) | ESP32 GPIO 10 | White | Chip select |
| **OUT** | → LM358 Pin 3 | Green | Sine wave output |

**Wiring diagram on breadboard:**

```
    Breadboard 2 (right side)
    ┌────────────────────────────────────────┐
    │  + rail        GND rail                │
    │    │             │                     │
    │  [VCC]──────────[GND]   AD9833        │
    │    │             │        module       │
    │  [DAT]──→ GPIO11 │      (F5–J5 area)   │
    │  [CLK]──→ GPIO12 │                     │
    │  [FSYN]─→ GPIO10 │                     │
    │  [OUT]──→ LM358  │                     │
    │                    │                     │
    └────────────────────────────────────────┘
```

**Important:** Some AD9833 modules have a **5V / 3.3V jumper**. Set it to **3.3V**.

---

## 🔧 STEP 4: LM358 BUFFER

The LM358 buffers the AD9833 output so it can drive the soil electrodes with low impedance.

**LM358 DIP-8 Pinout:**
```
        ┌────────┐
    1OUT│ 1    8 │VCC (+3.3V)
    1IN-│ 2    7 │2OUT (unused)
    1IN+│ 3    6 │2IN- (unused)
    VCC-│ 4    5 │2IN+ (unused)
        └────────┘
```

**Place the LM358** straddling the breadboard gap on **Breadboard 2, left side**, around **rows 10–13**.

**Connections:**

| LM358 Pin | Connect To | Wire Colour |
|-----------|-----------|-------------|
| **Pin 1 (1OUT)** | → 100Ω resistor → Electrode A | Green |
| **Pin 2 (1IN-)** | → Pin 1 (feedback wire) | Green |
| **Pin 3 (1IN+)** | → AD9833 OUT | Yellow |
| **Pin 4 (V-)** | GND rail | Blue |
| **Pin 5 (2IN+)** | GND rail (tie unused input low) | Blue |
| **Pin 6 (2IN-)** | GND rail (tie unused input low) | Blue |
| **Pin 7 (2OUT)** | Leave unconnected | — |
| **Pin 8 (V+)** | 3.3V rail | Red |

**Wiring diagram:**

```
    Breadboard 2, LM358 area (rows 10–13)
    ┌────────────────────────────────────────┐
    │                                        │
    │   10  [AD9833 OUT]──────→ [J10] Pin3   │
    │   11            │                      │
    │   12  [Pin2]←───┼──→[Pin1]──[100Ω]──→A │
    │   13  [Pin4 GND] [Pin8 3.3V]           │
    │   14  [Pin5 GND] [Pin6 GND]            │
    │                                        │
    └────────────────────────────────────────┘
```

**Note:** The wire from Pin 2 back to Pin 1 is a **feedback loop** — it makes the op-amp a unity-gain follower. Use a short green Dupont wire.

---

## 🎯 STEP 5: OPA1641 TIA

This is the heart of the measurement — it converts the tiny current flowing through your soil into a measurable voltage.

**OPA1641 DIP-8 Pinout:**
```
        ┌────────┐
    NC  │ 1    8 │NC
    IN- │ 2    7 │V+ (+3.3V)
    IN+ │ 3    6 │OUT
    V-  │ 4    5 │NC
        └────────┘
```

**Place the OPA1641** straddling the breadboard gap on **Breadboard 1, left side**, around **rows 15–18**.

**Connections:**

| OPA1641 Pin | Connect To | Wire Colour |
|-------------|-----------|-------------|
| **Pin 1 (NC)** | Nothing | — |
| **Pin 2 (IN-)** | → Electrode B + 1kΩ feedback | White |
| **Pin 3 (IN+)** | → BIAS point (E1, the 1.65V divider) | Purple |
| **Pin 4 (V-)** | GND rail | Blue |
| **Pin 5 (NC)** | Nothing | — |
| **Pin 6 (OUT)** | → 1kΩ → Pin 2 + ESP32 ADC | Orange |
| **Pin 7 (V+)** | 3.3V rail | Red |
| **Pin 8 (NC)** | Nothing | — |

**Wiring diagram:**

```
    Breadboard 1, OPA1641 area (rows 15–18)
    ┌────────────────────────────────────────┐
    │                                        │
    │   15  [NC]         [NC]                │
    │   16  [Pin2]←──────[Pin6]──→ ESP32 ADC │
    │        │             │                 │
    │   17  [Elec B]    [1kΩ]←──┘           │
    │   18  [Pin3]────→ BIAS (E1)            │
    │   19  [Pin4 GND]  [Pin7 3.3V]          │
    │                                        │
    └────────────────────────────────────────┘
```

**Critical wiring:**
1. **1kΩ feedback resistor** between OPA1641 **Pin 6** and **Pin 2**
   - This sets the transimpedance gain. 1kΩ = 1V per 1mA of soil current.
   - If you want more sensitivity for dry soil, use **10kΩ** instead. But 10kΩ will saturate on wet soil.

2. **OPA1641 Pin 3** → **BIAS point (E1)** using a purple wire
   - This sets the virtual ground to 1.65V.

3. **OPA1641 Pin 6** → **ESP32 GPIO 1 (ADC1_CH0)** using an orange wire
   - The ESP32 reads the amplified AC signal here.

---

## 🌱 STEP 6: ELECTRODES

### Preparing the Electrodes
1. Cut **M6 stainless rod** to **100 mm** using junior hacksaw
2. File the cut end smooth (no burrs)
3. Strip 15 mm of insulation from wire ends
4. Wrap wire around rod near one end
5. Solder the wire to the rod (use flux + high heat — steel needs 350°C+)
   - **Alternative:** If soldering fails, use a jubilee clip to clamp the wire
6. Slide heat shrink over the joint, heat with lighter or heat gun
7. Label electrodes: **A** and **B**

### Electrode Placement (Wenner Array, 2-electrode simplified)
- Push electrodes into soil **50 mm apart**
- Insert **50 mm deep** into compost
- Keep electrodes parallel

### Wiring Electrodes to Breadboard

```
    Electrode A wire ──→ 100Ω resistor ──→ LM358 Pin 1 (buffer output)
    
    Electrode B wire ──→ OPA1641 Pin 2 (TIA input)
```

The 100Ω resistor between the buffer and Electrode A limits fault current if electrodes touch.

---

## 🌡️ STEP 7: DS18B20 TEMPERATURE SENSOR

**DS18B20 Waterproof Probe Wiring:**

| Wire Colour | Function | Connect To |
|-------------|----------|-----------|
| **Red** | VCC (3.3V) | 3.3V rail |
| **Black** | GND | GND rail |
| **Yellow** | Data | ESP32 GPIO 4 |

**Add 4.7kΩ pull-up resistor** between Yellow (data) and Red (3.3V).

```
    DS18B20 Probe
    ┌─────────────┐
    │  Red   ──→ 3.3V rail         │
    │  Black ──→ GND rail          │
    │  Yellow ──→ GPIO 4           │
    │       ↑                      │
    │   [4.7kΩ] to 3.3V            │
    └─────────────┘
```

**Placement:** Insert the stainless probe into the soil near the impedance electrodes, ~20 mm away from Electrode B.

---

## 🔋 STEP 8: BATTERY MONITOR

**Voltage divider** (100k + 100k) scales the 4.2V battery down to 2.1V for the ESP32 ADC.

```
    Battery + (4.2V max)
        │
     [100kΩ]
        │
        ├──→ ESP32 GPIO 2 (ADC1_CH1)
        │
     [100kΩ]
        │
      GND
```

**On Breadboard 2, right side:**
1. **100kΩ** from 3.3V rail to hole J20 (this is a placeholder — actually use battery + rail)
2. **100kΩ** from hole J20 to GND rail
3. **Hole J20** → ESP32 GPIO 2

**Note:** For initial breadboard testing, skip the battery and power from USB. Add the divider when you switch to battery power.

---

## 📟 STEP 9: ESP32-S3 CONNECTIONS

Place the ESP32-S3-DevKitC-1 on **Breadboard 2, left side**, with pins in the top rows.

**Key connections summary:**

| ESP32 Pin | Function | Connect To | Wire Colour |
|-----------|----------|-----------|-------------|
| **3.3V** | Power out | 3.3V rail | Red |
| **GND** | Ground | GND rail | Blue |
| **GPIO 10** | AD9833 FSYNC | AD9833 FSYN | White |
| **GPIO 11** | AD9833 SDATA | AD9833 DAT | Yellow |
| **GPIO 12** | AD9833 SCLK | AD9833 CLK | Orange |
| **GPIO 1** | ADC1_CH0 | OPA1641 Pin 6 (TIA out) | Orange |
| **GPIO 2** | ADC1_CH1 | Battery divider (optional) | Grey |
| **GPIO 4** | OneWire | DS18B20 Data | Green |
| **GPIO 21** | Status LED | Onboard LED (already on dev board) | — |

**Power the ESP32:**
- For now, power via **USB-C cable** to your computer
- The ESP32's 3.3V regulator powers the breadboard rails through a jumper wire
- **Later:** Add 18650 + TP4056 module for battery power

---

## 🔘 STEP 10: DECOUPLING CAPACITORS

Add **100nF ceramic capacitors** across the power pins of each IC:

| IC | Placement |
|----|-----------|
| **OPA1641** | 100nF between Pin 7 (V+) and Pin 4 (V-), as close to the chip as possible |
| **LM358** | 100nF between Pin 8 (V+) and Pin 4 (V-), as close to the chip as possible |
| **AD9833** | 100nF between VCC and GND pins on the module (usually already present) |

These capacitors filter high-frequency noise from the power supply. Place them physically close to the chips.

---

## 🖼️ COMPLETE BREADBOARD DIAGRAM

```
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                           BREADBOARD 1  (ANALOG)                                     ║
║  Columns A–E                          Columns F–J                                    ║
╠══════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                      ║
║  Row 1  [3.3V]─[10k]─[●E1]─[10k]─[GND]          (1.65V BIAS created here)          ║
║  Row 2          [100nF]─[GND]                                                        ║
║  Row 3                                                                               ║
║  Row 4                                                                               ║
║  Row 5                                                                               ║
║  Row 6                                                                               ║
║  Row 7                                                                               ║
║  Row 8                                                                               ║
║  Row 9                                                                               ║
║  Row 10                                                                              ║
║  Row 11                                                                              ║
║  Row 12                                                                              ║
║  Row 13                                                                              ║
║  Row 14                                                                              ║
║  Row 15  OPA1641 Pin 1 (NC)              OPA1641 Pin 8 (NC)                         ║
║  Row 16  OPA1641 Pin 2 (IN-) ←───────→ OPA1641 Pin 7 (V+ → 3.3V)                   ║
║          │           ↑                 ↑                                             ║
║  Row 17  │      Elec B            [100nF decoupling]                                 ║
║          │           │                 │                                             ║
║  Row 18  OPA1641 Pin 3 (IN+) → BIAS   OPA1641 Pin 6 (OUT) ──→ GPIO 1 (ADC)          ║
║          │                            │                                              ║
║  Row 19  OPA1641 Pin 4 (V- → GND)    └────[1kΩ feedback]────┘                       ║
║  Row 20                                                                              ║
║                                                                                      ║
║  Power rails: Red = +3.3V    Blue = GND                                            ║
╚══════════════════════════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════════════════════════╗
║                           BREADBOARD 2  (DIGITAL + POWER)                            ║
║  Columns A–E                          Columns F–J                                    ║
╠══════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                      ║
║  Row 1   ESP32 3.3V → red rail        ESP32 GND → blue rail                        ║
║  Row 2   ESP32 GPIO 10 → AD9833 FSYN                                               ║
║  Row 3   ESP32 GPIO 11 → AD9833 DAT                                                ║
║  Row 4   ESP32 GPIO 12 → AD9833 CLK                                                ║
║  Row 5   ESP32 GPIO 1  → OPA1641 OUT                                               ║
║  Row 6   ESP32 GPIO 2  → Battery divider (optional)                                ║
║  Row 7   ESP32 GPIO 4  → DS18B20 Data                                              ║
║  Row 8                                                                               ║
║  Row 9                                                                               ║
║  Row 10                    AD9833 OUT → LM358 Pin 3                                ║
║  Row 11                                                                              ║
║  Row 12  LM358 Pin 2 ←────┬────→ LM358 Pin 1 ──[100Ω]──→ Elec A                   ║
║  Row 13  LM358 Pin 4 GND  LM358 Pin 8 3.3V                                         ║
║  Row 14  LM358 Pin 5 GND  LM358 Pin 6 GND  (unused ch2 tied low)                   ║
║  Row 15                                                                              ║
║  Row 16  AD9833 VCC → 3.3V    AD9833 GND → GND                                     ║
║  Row 17  AD9833 module sits here (F16–J18 area)                                    ║
║  Row 18                                                                              ║
║  Row 19  DS18B20 Red → 3.3V   [4.7k] → 3.3V (pull-up)                             ║
║  Row 20  DS18B20 Black → GND   DS18B20 Yellow → GPIO 4                              ║
║                                                                                      ║
║  Power rails: Red = +3.3V    Blue = GND                                            ║
╚══════════════════════════════════════════════════════════════════════════════════════╝
```

---

## ✅ STEP-BY-STEP BUILD ORDER

**Build in this exact order. Don't skip steps.**

### Phase A: Power (5 min)
1. ☐ Connect power rails between breadboards
2. ☐ Verify 3.3V rail and GND rail are continuous with multimeter (continuity beep)
3. ☐ Build 1.65V bias divider (2× 10k + 100nF)
4. ☐ Measure 1.65V with multimeter

### Phase B: Digital (5 min)
5. ☐ Place ESP32-S3 on Breadboard 2
6. ☐ Power ESP32 via USB-C (upload empty sketch first to verify)
7. ☐ Connect 3.3V from ESP32 to breadboard red rail
8. ☐ Connect GND from ESP32 to breadboard blue rail
9. ☐ Place AD9833 module and wire SPI (GPIO 10/11/12)

### Phase C: Buffer (5 min)
10. ☐ Place LM358 on Breadboard 2
11. ☐ Wire LM358 power (Pin 8 → 3.3V, Pin 4 → GND)
12. ☐ Tie unused inputs low (Pin 5 → GND, Pin 6 → GND)
13. ☐ Wire buffer: Pin 3 → AD9833 OUT, Pin 2 → Pin 1
14. ☐ Add 100Ω series resistor from Pin 1 → Electrode A

### Phase D: TIA (5 min)
15. ☐ Place OPA1641 on Breadboard 1
16. ☐ Wire OPA1641 power (Pin 7 → 3.3V, Pin 4 → GND)
17. ☐ Wire Pin 3 → BIAS (1.65V point)
18. ☐ Place 1kΩ feedback between Pin 6 and Pin 2
19. ☐ Wire Pin 6 → ESP32 GPIO 1
20. ☐ Wire Electrode B → Pin 2

### Phase E: Sensors (3 min)
21. ☐ Wire DS18B20 (Red → 3.3V, Black → GND, Yellow → GPIO 4 + 4.7kΩ pull-up)
22. ☐ Insert temperature probe into soil
23. ☐ Insert Electrodes A and B into soil, 50 mm apart, 50 mm deep

### Phase F: Decoupling (2 min)
24. ☐ Add 100nF across OPA1641 power pins
25. ☐ Add 100nF across LM358 power pins
26. ☐ Verify no loose wires, no shorts

---

## 🧪 FIRST POWER-ON TEST

### Test 1: No-Load Check (5 min)
1. **Power on** via USB-C
2. **Open Serial Monitor** (115200 baud)
3. **Check voltages** with multimeter:
   - 3.3V rail → 3.30V ± 0.1V
   - BIAS point → 1.65V ± 0.05V
   - OPA1641 Pin 6 → 1.65V ± 0.1V (DC, no excitation)
   - LM358 Pin 1 → ~1.65V ± 0.3V (AC from AD9833)
4. **Feel chips** — should be room temperature. If hot, power off immediately (short circuit)

### Test 2: AD9833 Output (2 min)
1. Set multimeter to **AC voltage** (200mV range)
2. Probe LM358 Pin 1 and GND
3. Should read **~150–200 mV AC** (the 0.6V pp sine)
4. If 0V, check AD9833 wiring and SPI connections

### Test 3: TIA with Test Resistor (5 min)
1. Disconnect Electrode B from soil
2. Connect a **1kΩ resistor** between Electrode A and Electrode B (simulates moderate soil)
3. In Serial Monitor, type `m` (measure)
4. Expected: **Z ≈ 1.1kΩ ± 10%**
   - If Z = 99999Ω → measurement failed (check TIA wiring)
   - If Z = 0Ω → short circuit (electrodes touching)
   - If Z wildly different → check 1kΩ feedback resistor value

### Test 4: TIA with 100Ω Resistor (2 min)
1. Replace with **100Ω resistor** (simulates wet soil)
2. Type `m`
3. Expected: **Z ≈ 100–120Ω**

### Test 5: Open Circuit (2 min)
1. Remove resistor (open circuit = very dry soil)
2. Type `m`
3. Expected: **Z very high or measurement failed** — this is correct

---

## 🗺️ FULL SYSTEM WIRING TABLE

| From | To | Colour | Gauge | Length |
|------|-----|--------|-------|--------|
| ESP32 3.3V | Breadboard red rail | Red | 22 AWG | 10 cm |
| ESP32 GND | Breadboard blue rail | Blue | 22 AWG | 10 cm |
| BB1 red rail | BB2 red rail | Red | 22 AWG | 15 cm |
| BB1 blue rail | BB2 blue rail | Blue | 22 AWG | 15 cm |
| 3.3V rail | 10kΩ → E1 | — | — | — |
| E1 | 10kΩ → GND | — | — | — |
| E1 | 100nF → GND | — | — | — |
| E1 | OPA1641 Pin 3 | Purple | Dupont | 10 cm |
| AD9833 VCC | 3.3V rail | Red | Dupont | 10 cm |
| AD9833 GND | GND rail | Blue | Dupont | 10 cm |
| AD9833 DAT | ESP32 GPIO 11 | Yellow | Dupont | 15 cm |
| AD9833 CLK | ESP32 GPIO 12 | Orange | Dupont | 15 cm |
| AD9833 FSYN | ESP32 GPIO 10 | White | Dupont | 15 cm |
| AD9833 OUT | LM358 Pin 3 | Green | Dupont | 10 cm |
| LM358 Pin 8 | 3.3V rail | Red | Dupont | 5 cm |
| LM358 Pin 4 | GND rail | Blue | Dupont | 5 cm |
| LM358 Pin 3 | AD9833 OUT | Yellow | Dupont | 5 cm |
| LM358 Pin 2 | LM358 Pin 1 | Green | Dupont | 3 cm |
| LM358 Pin 1 | 100Ω → Electrode A | Green | Solid core | 30 cm |
| LM358 Pin 5 | GND rail | Blue | Dupont | 5 cm |
| LM358 Pin 6 | GND rail | Blue | Dupont | 5 cm |
| OPA1641 Pin 7 | 3.3V rail | Red | Dupont | 5 cm |
| OPA1641 Pin 4 | GND rail | Blue | Dupont | 5 cm |
| OPA1641 Pin 3 | BIAS (E1) | Purple | Dupont | 10 cm |
| OPA1641 Pin 6 | 1kΩ → Pin 2 | — | Resistor | 3 cm |
| OPA1641 Pin 6 | ESP32 GPIO 1 | Orange | Dupont | 15 cm |
| OPA1641 Pin 2 | Electrode B | White | Solid core | 30 cm |
| DS18B20 Red | 3.3V rail | Red | Probe wire | — |
| DS18B20 Black | GND rail | Black | Probe wire | — |
| DS18B20 Yellow | ESP32 GPIO 4 | Green | Dupont | 15 cm |
| GPIO 4 | 4.7kΩ → 3.3V | — | Resistor | — |
| Elec A | 100Ω → LM358 Pin 1 | Green | Solid core | — |

---

## ❌ COMMON MISTAKES

| Symptom | Cause | Fix |
|---------|-------|-----|
| **Nothing on serial** | Wrong USB port / charge-only cable | Try different cable, different USB port |
| **OPA1641 gets hot** | Power reversed (Pin 7 ↔ Pin 4) | Power off, flip chip 180°, check notch direction |
| **LM358 gets hot** | Output shorted to ground | Check Pin 1 not touching GND rail |
| **AD9833 silent** | SPI wires swapped | Check DAT→GPIO11, CLK→GPIO12, FSYN→GPIO10 |
| **Z always 99999** | TIA output saturated / no signal | Check 1kΩ feedback, check BIAS = 1.65V, check Electrode B connected |
| **Z doesn't change** | Electrodes not in soil | Push deeper, add water, check electrode wire continuity |
| **Random Z values** | Loose breadboard connection | Press wires firmly, use solid core for permanent connections |
| **ADC reads 4095** | TIA output > 3.3V (saturated) | Normal for very wet soil — reduce watering or increase excitation series R |
| **ADC reads 0** | TIA output shorted to GND | Check Pin 6 not touching GND rail |
| **Temp reads -127** | DS18B20 wiring wrong / no pull-up | Check red→3.3V, black→GND, yellow→GPIO4, 4.7kΩ pull-up present |
| **WiFi won't connect** | Wrong password / 5GHz network | WiFiManager only supports 2.4GHz. Reconfigure via portal. |

---

## 🔬 CIRCUIT THEORY (Why This Works)

### Signal Path
1. **AD9833** generates a 1 kHz sine wave (0.6V pp, centred on ~1.65V)
2. **LM358 buffer** drives the signal with low impedance through 100Ω to **Electrode A**
3. **Current flows** through the soil from Electrode A to Electrode B
4. **OPA1641 TIA** forces its inverting input (Pin 2) to stay at 1.65V (virtual ground)
5. The **feedback resistor** (1kΩ) converts current to voltage: V_out = 1.65V ± (I_soil × 1kΩ)
6. **ESP32 ADC** samples the output 400 times at 4 kSPS
7. **Lock-in DSP** extracts the amplitude by mixing with reference sine/cosine and averaging
8. **Ohm's Law**: Z = V_excitation / I_soil = V_excitation × R_gain / V_measured

### Why 1.65V Bias?
The ESP32 ADC can only read 0–3.3V. The AC signal swings both positive and negative. By biasing at 1.65V (mid-rail), the signal can swing ±1.65V before clipping. The firmware subtracts the DC offset before processing.

### Why the LM358 Buffer?
The AD9833 has ~200Ω output impedance. With soil Z = 100Ω, most of the voltage drops across the AD9833's internal resistance, not the soil. The buffer presents a low impedance (<50Ω) to the soil, ensuring the full excitation voltage appears across the electrodes.

### Why 100Ω Series Resistor?
If the electrodes touch (short circuit), current would be 3.3V / 50Ω = 66mA. The 100Ω resistor limits this to 22mA, protecting the LM358 and battery.

---

## 🚀 NEXT STEPS AFTER WIRING

1. Flash the firmware (`glasshouse_node_v1.ino`)
2. Open Serial Monitor, press any key → enter CLI mode
3. Type `m` with 1kΩ test resistor between electrodes → verify Z ≈ 1kΩ
4. Push electrodes into **dry** compost → type `cal-dry`
5. Water the compost → type `cal-wet`
6. Type `status` to confirm calibration saved
7. Type `sleep` → node enters 15-minute cycle
8. Set up backend (Docker) and watch data arrive

---

*Document: TIA Breadboard Wiring Guide*
*Version: 1.0*
*For: GlassHouse Tomatoes v1.0*
*Estimated build time: 30 minutes*
