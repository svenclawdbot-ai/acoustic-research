# Soil Probe — Single-Board Wiring Guide
# ESP32-S3 + AD9833 + TIA (OPA1641)

## AD9833 → ESP32-S3 Wiring (5 wires)

| AD9833 Pin | Wire Colour | ESP32-S3 Pin | GPIO | Function |
|------------|-------------|--------------|------|----------|
| VCC        | Red         | 3.3V         | —    | Power    |
| GND        | Black       | GND          | —    | Ground   |
| SDATA      | Yellow      | GPIO 11      | 11   | SPI MOSI |
| SCLK       | Blue        | GPIO 12      | 12   | SPI SCK  |
| FSYNC      | Green       | GPIO 10      | 10   | SPI CS   |

**Important:** AD9833 modules run at 3.3V logic. Do NOT connect to 5V.

## TIA Circuit — Breadboard Layout

### Components Needed
- OPA1641 (DIP-8) × 1
- 1 kΩ resistor (TIA gain) × 1
- 10 kΩ resistor (load/bias) × 1
- 100 nF capacitor (decoupling) × 2
- Breadboard jumpers

### Breadboard Layout (top view)
```
        Power Rail (+3.3V)          Power Rail (GND)
              |                           |
    [10k]    |                           |
     │       |                           |
     └───────┼──→ OPA1641 Pin 3 (+)      |
             │      |   _   |            |
             |   ┌──┴──( )──┴──┐         |
             |   │ 2 (-)   6(out)│──[1k]──┘
             |   │             │    │
             |   └──────┬──────┘    │
             |          │           │
    Electrode A ─────────┘           └──→ GPIO 1 (ADC)
    (current in)                     
                                     
    Electrode B ─────────────────────→ OPA1641 Pin 2 (-)
    (return)                         (virtual ground)
    
    OPA1641 Pin 4 (V-) → GND rail
    OPA1641 Pin 7 (V+) → +3.3V rail
    
    Decoupling caps:
    100nF between Pin 7 and Pin 4 (as close to chip as possible)
    100nF between +3.3V rail and GND rail
```

### Pin-by-Pin Connections
| OPA1641 Pin | Name | Connects To |
|-------------|------|-------------|
| 1 | NC | — |
| 2 | IN- | Electrode B + one end of 1kΩ resistor |
| 3 | IN+ | Electrode A + one end of 10kΩ resistor |
| 4 | V- | GND rail |
| 5 | NC | — |
| 6 | OUT | Other end of 1kΩ resistor → ESP32 GPIO 1 |
| 7 | V+ | +3.3V rail |
| 8 | NC | — |

### Test Points
- **TP1:** AD9833 OUT → should see ~0.5V AC at 1 kHz
- **TP2:** OPA1641 Pin 3 → same as TP1 (buffered)
- **TP3:** OPA1641 Pin 6 → should see voltage proportional to soil current

## Signal Chain
```
AD9833 OUT → Electrode A → Soil → Electrode B → OPA1641 (-) → TIA output → ESP32 ADC
                ↑                                    |
                └──── 10kΩ to 3.3V (bias, keeps signal positive) ─────┘
```

## Full System Wiring Diagram
```
ESP32-S3-DevKitC-1
┌─────────────────┐
│ 3.3V ─────┬─────┼──→ AD9833 VCC (red)
│           │     │
│ GND  ─────┼─────┼──→ AD9833 GND (black)
│           │     │
│ GPIO 11 ──┼─────┼──→ AD9833 SDATA (yellow)
│           │     │
│ GPIO 12 ──┼─────┼──→ AD9833 SCLK (blue)
│           │     │
│ GPIO 10 ──┼─────┼──→ AD9833 FSYNC (green)
│           │     │
│ GPIO 1  ←─┼─────┼──→ TIA output (from OPA1641 pin 6)
│           │     │
│ GND  ←────┼─────┼──→ Electrode B (return)
└───────────┼─────┘
            │
            │    Breadboard
            │    ┌─────────────────┐
            │    │                 │
            └────┼──→ OPA1641 V+    │
                 │      OPA1641 OUT ├──→ GPIO 1
                 │          │       │
                 │         [1k]     │
                 │          │       │
                 │      OPA1641 (-) ├──→ Electrode B
                 │          │       │
                 │      OPA1641 (+) ├──→ Electrode A
                 │          │       │
                 │         [10k]    │
                 │          │       │
                 └──────────┼───────┘
                            │
                    AD9833 OUT
                            │
                    ┌───────┴───────┐
                    │     SOIL      │
                    │   (Z_soil)    │
                    │               │
                    │  A      B    │
                    └───────────────┘
```

## Software Upload Steps
1. Connect ESP32-S3 to PC via USB-C (port near reset button)
2. Open Arduino IDE or `arduino-cli`
3. Select board: "ESP32S3 Dev Module"
4. Upload `soil_spectrometer_esp32s3.ino`
5. Open Serial Monitor at 115200 baud
6. Expected output: CSV rows with freq, |Z|, phase

## Quick Tests

### Test 1: DDS Alone (no TIA)
1. Wire only AD9833 → ESP32 (5 wires)
2. Upload `ad9833_test_esp32s3.ino`
3. Probe AD9833 OUT with multimeter AC
4. **Pass:** ~0.5V AC at 1 kHz

### Test 2: TIA with Dummy Resistor
1. Add TIA circuit to breadboard
2. Connect a 1 kΩ resistor between Electrodes A and B (simulate soil)
3. Upload `soil_spectrometer_esp32s3.ino`
4. **Expected:** |Z| ≈ 1 kΩ across all frequencies (resistor is real, no phase)

### Test 3: Real Soil
1. Prepare electrodes (M6 rods, 50mm apart, 50mm deep)
2. Insert into dry compost
3. Run sweep
4. **Expected:** |Z| > 500 Ω, phase near 0° (mostly resistive)
5. Add water, run again
6. **Expected:** |Z| drops 30-70%, phase becomes negative (capacitive)

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| No DDS output | FSYNC not toggling | Check GPIO 10 wire |
| DDS output weak | Powered from 5V | Use 3.3V |
| ADC reads 0 | TIA not powered | Check 3.3V to OPA1641 pin 7 |
| ADC reads 4095 (max) | Output saturated | Reduce excitation or gain |
| |Z| negative or NaN | i_soil = 0 (open circuit) | Check electrode connection |
| Phase random | DC offset not rejected | Add DC blocking cap or software offset removal |

## Safety
- 3.3V only — safe to touch
- AD9833 OUT is ~0.6V max — no shock hazard
- Keep soldering iron in stand when hot

---
*Generated: 2026-05-18*
