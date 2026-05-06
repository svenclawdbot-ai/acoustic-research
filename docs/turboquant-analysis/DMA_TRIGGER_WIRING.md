# DMA Trigger Wiring Guide

## Overview

This guide shows how to wire the DMA acquisition trigger to your existing array control hardware for synchronized data capture.

## Signal Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         TRIGGER ARCHITECTURE                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────────┐         ┌──────────────┐         ┌──────────────┐    │
│   │   Array      │  SYNC   │   ESP32-S3   │   DMA   │    ADC       │    │
│   │   Control    │────────▶│   GPIO 15    │────────▶│   (8-ch)     │    │
│   │   (HV Pulser)│  Signal │   (Trigger)  │  Start  │   20 MSa/s   │    │
│   └──────────────┘         └──────────────┘         └──────────────┘    │
│          │                        │                                     │
│          │                        │                                     │
│          ▼                        ▼                                     │
│   ┌──────────────┐         ┌──────────────┐                            │
│   │  Ultrasound  │         │  PSRAM/USB   │                            │
│   │   Transducer │         │   Data Out   │                            │
│   └──────────────┘         └──────────────┘                            │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Wiring Diagram

### Option 1: Direct Connection (Recommended)

If your array control board has a SYNC output:

```
Array Control Board          ESP32-S3 DevKit
┌─────────────────┐         ┌──────────────────┐
│                 │         │                  │
│  SYNC_OUT       │────────▶│  GPIO 15         │
│  (3.3V logic)   │         │  (Trigger Input) │
│                 │         │                  │
│  GND            │────────▶│  GND             │
│                 │         │                  │
└─────────────────┘         └──────────────────┘
```

### Option 2: Opto-Isolated (HV Isolation)

If your pulser generates high voltage and you need isolation:

```
Array Control (HV Side)         Isolation          ESP32-S3 (LV Side)
┌─────────────────┐         ┌──────────────┐         ┌──────────────────┐
│                 │         │              │         │                  │
│  SYNC_OUT       │────────▶│  Optocoupler │────────▶│  GPIO 15         │
│  (5V or HV ref) │         │  (PC817)     │         │  (3.3V input)    │
│                 │         │              │         │                  │
│  GND_HV         │────────▶│  ─────────── │    ┌───▶│  GND             │
│                 │         │              │    │    │                  │
└─────────────────┘         └──────────────┘    │    └──────────────────┘
                                                │
                                           10kΩ pull-up
                                           to 3.3V
```

**Optocoupler Wiring:**
- Pin 1 (Anode): SYNC_OUT via 330Ω resistor
- Pin 2 (Cathode): GND_HV
- Pin 3 (Emitter): ESP32 GND
- Pin 4 (Collector): GPIO 15 + 10kΩ pull-up to 3.3V

### Option 3: Using Existing SYNC_OUT Pin

Your existing `array_control.h` already defines SYNC_OUT on GPIO 8. You can loop this back:

```
ESP32-S3 Internal Loopback
┌─────────────────────────────────────────┐
│                                         │
│  GPIO 8 (SYNC_OUT) ──────┐              │
│                          │              │
│                          ▼              │
│  GPIO 15 (TRIGGER_IN) ◄──┘              │
│                          │              │
│                    (External            │
│                     jumper wire)        │
│                                         │
└─────────────────────────────────────────┘
```

**For testing without external pulser:**
```cpp
// In your main.cpp or setup:
gpio_pad_select_gpio(GPIO_NUM_8);
gpio_set_direction(GPIO_NUM_8, GPIO_MODE_OUTPUT);

// When firing array:
gpio_set_level(GPIO_NUM_8, 1);  // Trigger
delayMicroseconds(1);
gpio_set_level(GPIO_NUM_8, 0);
```

## Pin Assignments

| Signal | ESP32-S3 GPIO | Function | Direction |
|--------|---------------|----------|-----------|
| SYNC_OUT | GPIO 8 | Array sync output (existing) | Output |
| TRIGGER_IN | GPIO 15 | DMA trigger input | Input |
| ADC_CH0 | GPIO 1 | ADC1 Channel 0 | Analog In |
| ADC_CH1 | GPIO 2 | ADC1 Channel 1 | Analog In |
| ADC_CH2 | GPIO 3 | ADC1 Channel 2 | Analog In |
| ADC_CH3 | GPIO 4 | ADC1 Channel 3 | Analog In |
| ADC_CH4 | GPIO 5 | ADC1 Channel 4 | Analog In |
| ADC_CH5 | GPIO 6 | ADC1 Channel 5 | Analog In |
| ADC_CH6 | GPIO 7 | ADC1 Channel 6 | Analog In |
| ADC_CH7 | GPIO 8 | ADC1 Channel 7 | Analog In |

**Note:** GPIO 8 is used for both SYNC_OUT and ADC_CH7. Choose one function:
- If using external array pulser: Use GPIO 8 as SYNC_OUT, wire external trigger to GPIO 15
- If testing without pulser: Use GPIO 8 as TRIGGER_IN (jumper from GPIO 15 output)

## Physical Wiring Instructions

### Step 1: Identify SYNC Source

**If your TurboQuant board has SYNC output:**
1. Locate SYNC header (usually labeled "SYNC" or "TRIG")
2. Connect SYNC → ESP32 GPIO 15
3. Connect GND → ESP32 GND

**If using internal loopback for testing:**
1. Place jumper wire between GPIO 8 and GPIO 15
2. No external connections needed

### Step 2: ADC Input Connections

Connect your analog front-end (MUX/LNA board) to ESP32:

```
Your LNA/MUX Board          ESP32-S3
┌─────────────────┐         ┌──────────────────┐
│                 │         │                  │
│  CH0 Output     │────────▶│  GPIO 1 (ADC1_0) │
│  CH1 Output     │────────▶│  GPIO 2 (ADC1_1) │
│  CH2 Output     │────────▶│  GPIO 3 (ADC1_2) │
│  CH3 Output     │────────▶│  GPIO 4 (ADC1_3) │
│  CH4 Output     │────────▶│  GPIO 5 (ADC1_4) │
│  CH5 Output     │────────▶│  GPIO 6 (ADC1_5) │
│  CH6 Output     │────────▶│  GPIO 7 (ADC1_6) │
│  CH7 Output     │────────▶│  GPIO 8 (ADC1_7) │
│                 │         │                  │
│  GND            │────────▶│  GND             │
│  3.3V Ref       │────────▶│  3.3V            │
└─────────────────┘         └──────────────────┘
```

### Step 3: Complete Wiring Checklist

- [ ] SYNC/TRIGGER connected (GPIO 15)
- [ ] All 8 ADC channels connected
- [ ] Common GND between all boards
- [ ] 3.3V reference connected (if needed)
- [ ] USB connected to host PC
- [ ] Array HV power connected (if using external pulser)

## Signal Specifications

### Trigger Input (GPIO 15)

| Parameter | Specification | Notes |
|-----------|---------------|-------|
| Logic level | 3.3V CMOS | 5V tolerant with divider |
| Minimum pulse | 100 ns | Shorter pulses may be missed |
| Edge detection | Rising (default) | Configurable in firmware |
| Pull configuration | Pull-down enabled | Prevents false triggers |
| Latency | <1 μs | ISR to DMA start |

### SYNC Output (GPIO 8)

| Parameter | Specification | Notes |
|-----------|---------------|-------|
| Logic level | 3.3V CMOS | |
| Drive strength | 20 mA | Can drive optocoupler directly |
| Pulse width | 1 μs (default) | Configurable |
| Timing | Coincident with element firing | |

## Troubleshooting

### No trigger detected

**Symptoms:** DMA stays in "armed" state, never acquires

**Check:**
1. Verify continuity with multimeter (SYNC → GPIO 15)
2. Check trigger signal with oscilloscope
3. Ensure common GND between boards
4. Verify trigger edge setting matches signal

**Debug firmware:**
```cpp
// Add to main loop
static int last_trigger_count = 0;
if (g_state.status.trigger_count != last_trigger_count) {
    ESP_LOGI("DEBUG", "Trigger detected! Count: %d", 
             g_state.status.trigger_count);
    last_trigger_count = g_state.status.trigger_count;
}
```

### False triggers

**Symptoms:** Random acquisitions without firing

**Solutions:**
1. Add 100nF capacitor across trigger input (hardware debounce)
2. Increase minimum pulse width in firmware
3. Use opto-isolation to reject noise
4. Verify shielded cable for trigger line

### Trigger timing issues

**Symptoms:** Inconsistent delay between fire and acquisition start

**Check:**
1. Measure with oscilloscope: SYNC vs actual element firing
2. Ensure SYNC is generated at correct point in firing sequence
3. Check for variable delays in shift register path

## Advanced: External Trigger Sources

You can trigger from other sources:

### Function Generator
```
Function Gen          ESP32-S3
┌──────────┐         ┌──────────┐
│  Output  │────────▶│  GPIO 15 │
│  (3.3V)  │         │          │
│  GND     │────────▶│  GND     │
└──────────┘         └──────────┘
```

Use for:
- Testing without array hardware
- Calibrating sample rate
- Verifying DMA integrity

### Red Pitaya External Trigger
```
Red Pitaya            ESP32-S3
┌──────────┐         ┌──────────┐
│  DIO0_P  │────────▶│  GPIO 15 │
│  GND     │────────▶│  GND     │
└──────────┘         └──────────┘
```

Use for:
- Synchronized multi-platform acquisition
- Trigger from Red Pitaya signal generator

## Bill of Materials (Trigger Wiring)

| Item | Qty | Notes |
|------|-----|-------|
| Dupont jumper wires (M-M) | 10 | For prototyping |
| BNC-to-wire adapter | 1 | If using scope probes |
| PC817 optocoupler | 1 | For isolation (optional) |
| 330Ω resistor | 1 | Optocoupler LED resistor |
| 10kΩ resistor | 1 | Pull-up resistor |
| 100nF capacitor | 1 | Debounce (optional) |
| Shielded cable | 1m | For noise immunity |

## Verification

After wiring, run:

```bash
# Check trigger is detected
python3 -c "
import serial, json
ser = serial.Serial('/dev/ttyUSB0', 921600)
ser.write(b'{\"cmd\":\"dma_get_status\"}\n')
print(ser.readline())
"

# Should show: trigger_count increases after each fire
```
