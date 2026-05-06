# Greenhouse Soil Monitoring Network — System Design

*Date: 2026-05-05*  
*Scope: Acre-scale greenhouse, solar-powered, LoRa mesh*

---

## Overview

Multi-node soil impedance network for acre-scale greenhouse. Nodes take measurements every 15–60 minutes, transmit via LoRa to a central gateway, which aggregates and optionally forwards to cloud.

**Key constraint:** Solar + battery only. No mains power at nodes.

---

## Network Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GREENHOUSE (1 acre ≈ 4047 m²)            │
│                                                              │
│    ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐                      │
│    │ N0  │  │ N1  │  │ N2  │  │ N3  │   ← Nodes (LoRa TX)  │
│    │Soil │  │Soil │  │Soil │  │Soil │      8-ch impedance   │
│    └─────┘  └─────┘  └─────┘  └─────┘                      │
│       │        │        │        │                           │
│    ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐                      │
│    │ N4  │  │ N5  │  │ N6  │  │ N7  │                      │
│    │Soil │  │Soil │  │Soil │  │Soil │                      │
│    └─────┘  └─────┘  └─────┘  └─────┘                      │
│       │        │        │        │                           │
│       └────────┴────────┴────────┘                           │
│                  LoRa 868/915 MHz                            │
│                        │                                     │
│              ┌─────────┴─────────┐                           │
│              │     GATEWAY        │  ← Central hub          │
│              │  (V5 + LoRa RX)   │     Full Red Pitaya       │
│              │                   │     + WiFi/Ethernet         │
│              │  • Collects data   │     + Local display       │
│              │  • Stores locally  │     + Cloud upload        │
│              │  • Optional cloud  │                           │
│              └───────────────────┘                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Node Layout

### Spacing

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Node spacing | 15–25 m | Greenhouse variability, root zone coverage |
| Electrodes per node | 8 points | 4 locations × 2 depths (10cm + 30cm) |
| Total nodes (1 acre) | 8–16 | 50m × 80m greenhouse |
| Gateway position | Centre or edge | Line-of-sight to all nodes |

### Example Layout (12 nodes)

```
    0────1────2────3
    │    │    │    │      Row spacing: 15m
    4────5────6────7      Column spacing: 20m
    │    │    │    │
    8────9───10───11
    
    Gateway at centre (between 5,6,9,10)
    Max distance to gateway: ~25m (excellent LoRa link)
```

---

## Sensor Node Hardware

### Simplified from V5

Remove from full V5:
- HV pulser (IRF830, TC4427, MUR120 diodes)
- Red Pitaya FPGA (not needed at node)
- Ethernet

Keep:
- ESP32-S3 (acquisition + LoRa control)
- DG408 MUX (8-ch)
- OPA1641 LNA (low-noise amplification)
- DAC for sine excitation (ESP32-S3 has 2× DAC)

Add:
- LoRa module (SX1262 / RFM95W)
- Solar panel (5W)
- Li-ion battery (18650, 2600mAh)
- Charge controller (TP4056 + protection)
- **DS18B20 temperature probe (1-Wire, waterproof)**

### Node Schematic

```
┌──────────────────────────────────────────────┐
│           SENSOR NODE (Soil Probe)           │
├──────────────────────────────────────────────┤
│                                              │
│  Solar Panel (5W)                            │
│       │                                      │
│       ↓                                      │
│  ┌─────────────┐    ┌─────────────┐          │
│  │ TP4056      │───→│ 18650       │          │
│  │ Charge Ctrl │    │ 2600mAh     │          │
│  └─────────────┘    └──────┬──────┘          │
│                            │                  │
│                            ↓ 3.3V            │
│  ┌─────────────────────────────────────┐    │
│  │         ESP32-S3                    │    │
│  │  ┌─────────┐  ┌─────────┐          │    │
│  │  │ DAC_1   │  │ DAC_2   │          │    │
│  │  │ (sine)  │  │ (sine)  │          │    │
│  │  └────┬────┘  └────┬────┘          │    │
│  │       │            │                │    │
│  │  ┌────┴────────────┴───┐            │    │
│  │  │  DG408 MUX (8-ch)  │            │    │
│  │  │  Select electrode  │            │    │
│  │  └────┬───────────────┘            │    │
│  │       │                            │    │
│  │       ↓                            │    │
│  │  ┌──────────┐   ┌──────────┐       │    │
│  │  │ Current  │──→│ Electrode│       │    │
│  │  │ Limit    │   │ Array    │       │    │
│  │  │ (1kΩ)    │   │ (4-Wenner│       │    │
│  │  └──────────┘   │  per ch) │       │    │
│  │       ↑         └────┬─────┘       │    │
│  │  ┌────┴───────────────┘            │    │
│  │  │  Sense Resistor (100Ω)          │    │
│  │  └────┬────────────────────────────┘    │
│  │       ↓                                 │
│  │  ┌──────────┐                          │
│  │  │ OPA1641  │                          │
│  │  │ LNA      │                          │
│  │  │ (G=10)   │                          │
│  │  └────┬─────┘                          │
│  │       ↓                                 │
│  │  ┌──────────┐                          │
│  │  │ ADC      │                          │
│  │  │ (12-bit) │                          │
│  │  └──────────┘                          │
│  │       │                                 │
│  │       ↓                                 │
│  │  ┌──────────┐                          │
│  │  │ Compute  │  Lock-in detection        │
│  │  │ I, Q, |Z│  on ESP32-S3              │
│  │  └────┬─────┘                          │
│  │       │                                 │
│  │  ┌────┴────┐                           │
│  │  │ SX1262  │───→ LoRa TX 868/915 MHz   │
│  │  │ LoRa    │                           │
│  │  └─────────┘                           │
│  └─────────────────────────────────────┘    │
│                                              │
└──────────────────────────────────────────────┘
```

### Bill of Materials (Per Node)

| Item | Qty | Unit | Cost | Supplier |
|------|-----|------|------|----------|
| ESP32-S3-DevKitC-1 | 1 | £6 | £6 | AliExpress / DigiKey |
| SX1262 LoRa module | 1 | £8 | £8 | AliExpress / DigiKey |
| DG408 MUX | 1 | £2 | £2 | DigiKey |
| OPA1641 | 1 | £3 | £3 | DigiKey |
| 18650 battery | 1 | £4 | £4 | Local / Amazon |
| TP4056 + protection | 1 | £1 | £1 | AliExpress |
| 5W solar panel | 1 | £8 | £8 | Amazon |
| **DS18B20 temp probe (waterproof)** | **1** | **£2.50** | **£2.50** | **AliExpress** |
| 4-electrode probe (SS) | 8 | £3 | £24 | Custom / AliExpress |
| Enclosure (IP67) | 1 | £5 | £5 | AliExpress |
| PCB / perfboard | 1 | £2 | £2 | - |
| Passive components | - | £3 | £3 | - |
| **Total per node** | | | **£68.50** | |

**12-node network:** 12 × £68.50 = **£822**
**Gateway:** Existing V5 + £15 LoRa module = **~£15 extra**

---

## Power Budget

### Measurement Cycle (15 min interval)

| Phase | Current | Duration | Energy |
|-------|---------|----------|--------|
| Deep sleep | 10 µA | 14m 55s | 0.002 mAh |
| Wake + warm-up | 50 mA | 500 ms | 0.007 mAh |
| MUX switching + acquisition | 80 mA | 2 s | 0.044 mAh |
| LoRa TX (SF7, 50 bytes) | 100 mA | 100 ms | 0.003 mAh |
| **Total per cycle** | | **~3 s** | **~0.06 mAh** |

### Daily Consumption

- Cycles per day: 96 (15 min interval)
- Daily energy: 96 × 0.06 mAh = **5.8 mAh/day**
- Battery capacity: 2600 mAh
- Days of autonomy (no sun): 2600 / 5.8 = **448 days**

Even with 50% efficiency (cold, ageing): **224 days autonomy**

### Solar Sizing

- Daily consumption: 5.8 mAh × 3.7V = 21.5 mWh/day
- Solar panel (5W): produces ~20 Wh/day in UK winter, ~50 Wh/day in summer
- **Massive overkill** — a 1W panel would suffice
- 5W chosen for: cloudy days, battery charging after dark periods, headroom

---

## LoRa Parameters

### Frequency Band

| Region | Frequency | Max Power | Notes |
|--------|-----------|-----------|-------|
| Europe | 868 MHz | 14 dBm (25 mW) | No license needed |
| US / Americas | 915 MHz | 30 dBm (1W) | FCC Part 15 |

### Link Budget (Greenhouse)

- Distance: 25m max (centre to corner)
- Path loss at 868 MHz, 25m: ~48 dB
- LoRa sensitivity at SF7: -123 dBm
- Node TX power: +14 dBm
- **Link margin: 14 - 48 - (-123) = 89 dB** — excellent

Even with greenhouse structure (metal frames, plants), margin > 50 dB.

### Duty Cycle (Europe 868 MHz)

- 1% duty cycle limit on most sub-bands
- Packet: 50 bytes at SF7 = ~56 ms airtime
- Max packets per hour: 3600 × 0.01 / 0.056 = **643 packets/hour**
- Our usage: 4 packets/hour (15 min interval)
- **Well within limits** (0.6% duty cycle)

### Packet Format

```c
typedef struct {
    uint8_t  node_id;        // 0–255
    uint16_t seq_num;        // Sequence number
    uint32_t timestamp;      // Unix timestamp (seconds)
    uint16_t battery_mv;     // Battery voltage (mV)
    int8_t   rssi;           // Last RX RSSI (for mesh)
    
    // Impedance data: 8 channels × 2 bytes
    // Format: uint16_t magnitude[8] (scaled ×1000)
    // Phase dropped to save bytes — compute at gateway if needed
    uint16_t z_mag[8];       // Impedance magnitude (mΩ)
    int16_t  soil_temp_c;    // Soil temperature (°C × 10, signed)
    
    uint16_t crc;            // CRC-16
} SoilPacket;  // Total: 34 bytes payload
```

Airtime at SF7, 125 kHz, explicit header: ~80 ms

---

## Range & Radio Performance

### What Controls Range

| Factor | Setting | Impact |
|--------|---------|--------|
| **Frequency** | 868 MHz (EU) / 915 MHz (US) | Lower = better penetration, longer range |
| **TX Power** | +14 dBm (25 mW) EU / +30 dBm (1W) US | Higher = longer range |
| **Spreading Factor (SF)** | SF7 (fast, short range) → SF12 (slow, long range) | Trade speed for sensitivity |
| **Bandwidth** | 125 kHz (standard) | Narrower = better sensitivity |
| **Antenna** | Whip vs dipole vs directional | Gain matters |
| **Environment** | Free space vs greenhouse vs urban | Obstructions cost 10–30 dB |

### Free-Space Range (Theoretical)

| Region | Frequency | TX Power | SF | Sensitivity | Max Range (free space) |
|--------|-----------|----------|-----|-------------|------------------------|
| Europe | 868 MHz | +14 dBm | 7 | -123 dBm | **~2 km** |
| Europe | 868 MHz | +14 dBm | 12 | -137 dBm | **~15 km** |
| US | 915 MHz | +30 dBm | 7 | -123 dBm | **~5 km** |
| US | 915 MHz | +30 dBm | 12 | -137 dBm | **~40 km** |

### Real-World Greenhouse Range

Free space is irrelevant. Your environment is a greenhouse:

```
Free space:          2 km (clear, no obstacles)
Greenhouse (typical):  100–300 m  ← metal frames, plants, humidity
Greenhouse (dense):     50–150 m  ← mature crop canopy, steel structure
Through wall / soil:    < 10 m     ← not applicable here
```

**Your layout:** 25 m max (centre to corner of acre). Even with heavy obstruction, link margin stays > 50 dB at SF7. **You could run SF7 comfortably at 100 m in a greenhouse.**

### Antenna Options

| Antenna | Gain | Cost | Best For | Range Impact |
|---------|------|------|----------|--------------|
| **Whip / monopole** | +2 dBi | £1–3 | Nodes, compact | Baseline |
| **Dipole (external)** | +3 dBi | £3–5 | Gateway, better coverage | +1.4× range |
| **Directional (Yagi)** | +8–12 dBi | £8–15 | Long haul, point-to-point | +2.5–4× range |
| **Stub (PCB)** | -2 dBi | £0 | Smallest nodes, cost cut | 0.6× range |

**Recommendation:** Whip on nodes, dipole on gateway. That's what the range numbers above assume.

### Practical Ranges for This Network

| Scenario | Range | Confidence |
|----------|-------|------------|
| Line-of-sight (same greenhouse bay) | 100–200 m | 99% packet success |
| One greenhouse wall + mature crop | 50–100 m | 95%+ packet success |
| Two bays, metal supports | 30–60 m | 90%+ packet success |
| Dense hydroponics / overhead irrigation | 20–40 m | May need SF9–SF10 |
| **Your 25 m max, SF7** | **25 m** | **>99% — trivial** |

### What If Range Is Too Short?

1. **Increase SF** — SF7 → SF9 adds 6 dB sensitivity, ~2× range. Costs: 4× airtime, more battery, tighter duty cycle.
2. **Add a relay node** — Any node can relay for others. Put one mid-field.
3. **Raise gateway antenna** — Mount gateway dipole high on greenhouse frame.
4. **US power** — If region allows, +30 dBm vs +14 dBm = 40× power, ~6× range.

### Link Budget Check for Your Deployment

```
Node TX power:           +14 dBm
Antenna gain (node):     +2 dBi
Path loss (868 MHz, 25 m):  -48 dB
Greenhouse attenuation:  -10 dB (conservative)
Antenna gain (gateway):  +3 dBi
Received at gateway:     -39 dBm

Gateway sensitivity (SF7): -123 dBm
Link margin:              84 dB

Required for reliable:    20 dB minimum
Your margin:              84 dB — absolutely solid
```

Even if you double to 50 m, lose another 10 dB to plants, and drop 5 dB on ageing antennas: **margin still > 40 dB.**

---

## Measurement Protocol

### Frequency Sweep (Simplified)

At each 15-minute interval:

```
For each of 8 electrode pairs:
    1. Select channel on MUX
    2. Generate 1 kHz sine on DAC (10 cycles for settling)
    3. Sample ADC at 100 kSa/s for 1000 samples
    4. Compute RMS of received signal
    5. Calculate |Z| = V_drive / I_sense
    
    6. Repeat at 10 kHz, 100 kHz
    7. Store magnitude at 3 frequencies

Pack into LoRa packet, transmit
Deep sleep
```

**Simplification:** Skip phase (saves computation + bytes). Just measure magnitude at 3 frequencies. Gateway can infer moisture from magnitude trend. Full spectroscopy only at gateway or on-demand.

### On-Demand Full Sweep

Gateway can request detailed measurement from any node:

```
Gateway → Node: {cmd: "FULL_SWEEP", node_id: 5}
Node 5 → Gateway: {z_mag[50], z_phase[50], freq[50]}  // 50-point sweep
```

Uses higher SF (SF10-SF12) for reliability, larger packet.

---

## Temperature Sensing

### Why Temperature Matters

| Effect | Impact on Measurements |
|--------|----------------------|
| Soil EC rises ~2% per °C | Without correction, dry warm soil reads as saltier than it is |
| Microbial activity | Nitrification, root uptake, germination all temperature-dependent |
| Irrigation timing | Warm soil + water = better uptake; cold soil + water = root rot risk |
| Frost protection | Greenhouse heating decisions |

### Hardware: DS18B20

**1-Wire bus, waterproof probe, ±0.5°C accuracy.**

```
ESP32-S3 GPIO 4 ──→ 1-Wire bus ──→ DS18B20 (soil temp at 10cm)
                                      └──→ Optional second probe (air temp)
```

Multiple probes on same wire (each has unique 64-bit ROM address). One at root zone depth minimum.

### Temperature-Corrected EC

Raw formula (Rhoades et al.):

```
EC₂₅ = EC_T / [1 + 0.02 × (T - 25)]
```

Example:
- Measure EC = 1.5 dS/m at 15°C
- EC₂₅ = 1.5 / [1 + 0.02 × (-10)] = **1.8 dS/m corrected**

Without correction: underestimate salinity by 20% in cool soil.

### Packet Integration

Temperature sent as `int16_t` (°C × 10) in every packet — 2 extra bytes. Gateway applies correction before storing.

### Cost Impact

| Item | Cost | Power |
|------|------|-------|
| DS18B20 waterproof probe | £2.50 | 1 mA active, parasitic power option |
| Second probe (optional air temp) | £2.50 | Same bus |
| **Total** | **£2.50–5** | **~0.1 mAh/day** |

---

## Gateway

### Hardware

- Existing V5 hardware (Red Pitaya + ESP32)
- Add SX1262 LoRa module (SPI to ESP32 or Red Pitaya)
- WiFi or Ethernet to internet
- Local storage (SD card or SSD)

### Software Stack

```
┌─────────────────────────────────────────────┐
│                 GATEWAY                      │
├─────────────────────────────────────────────┤
│                                              │
│  ┌────────────┐    ┌────────────┐           │
│  │ LoRa RX    │───→│ Packet      │           │
│  │ (SX1262)   │    │ Parser      │           │
│  └────────────┘    └──────┬─────┘           │
│                           │                  │
│              ┌────────────┴────────────┐     │
│              │                         │     │
│              ▼                         ▼     │
│  ┌─────────────────┐      ┌────────────────┐  │
│  │ Local SQLite    │      │ Real-time      │  │
│  │ Database        │      │ Dashboard      │  │
│  │ (per-node       │      │ (PyQtGraph /   │  │
│  │  time series)   │      │  web)          │  │
│  └────────┬────────┘      └────────────────┘  │
│           │                                  │
│           ▼                                  │
│  ┌─────────────────┐                        │
│  │ Analysis Engine │                        │
│  │ • Moisture map  │                        │
│  │ • Irrigation    │                        │
│  │   trigger       │                        │
│  │ • Anomaly       │                        │
│  │   detection     │                        │
│  └────────┬────────┘                        │
│           │                                  │
│  ┌────────┴────────┐                        │
│  │                 │                        │
│  ▼                 ▼                        │
│  WiFi / Ethernet  Optional                 │
│       │           Cloud Upload              │
│       ▼                                      │
│  Internet / MQTT                             │
│                                              │
└─────────────────────────────────────────────┘
```

### Data Flow

1. Node transmits every 15 min
2. Gateway receives, parses, timestamps
3. Store in SQLite (one table per node)
4. Update real-time dashboard
5. Run analysis (moisture mapping, irrigation logic)
6. Forward to cloud (optional, via MQTT or HTTP)

---

## Firmware — Sensor Node

### ESP32-S3 LoRa Node (Pseudocode)

```cpp
#include <Arduino.h>
#include <SX1262.h>
#include <driver/dac.h>
#include <driver/adc.h>

// Pins
#define LORA_CS     5
#define LORA_RST    6
#define LORA_DIO1   7
#define LORA_BUSY   8
#define MUX_A0      10
#define MUX_A1      11
#define MUX_A2      12
#define MUX_EN      13
#define ADC_PIN     ADC1_CHANNEL_0

// Config
const uint8_t NODE_ID = 0;
const uint32_t SLEEP_MS = 15 * 60 * 1000;  // 15 minutes
const uint16_t FREQS[] = {1000, 10000, 100000};  // Hz

struct SoilPacket {
    uint8_t  node_id;
    uint16_t seq_num;
    uint32_t timestamp;
    uint16_t battery_mv;
    uint16_t z_mag[8];  // Impedance magnitude (×1000)
} __attribute__((packed));

SX1262 radio;
uint16_t sequence = 0;

void setup() {
    Serial.begin(115200);
    
    // Init LoRa
    radio.begin(868.0, 125.0, 7, 5, 0x12, 14);  // Freq, BW, SF, CR, sync, power
    
    // Init DAC
    dac_output_enable(DAC_CHANNEL_1);
    
    // Init ADC
    adc1_config_width(ADC_WIDTH_BIT_12);
    adc1_config_channel_atten(ADC_PIN, ADC_ATTEN_DB_12);
    
    // Init MUX
    pinMode(MUX_A0, OUTPUT);
    pinMode(MUX_A1, OUTPUT);
    pinMode(MUX_A2, OUTPUT);
    pinMode(MUX_EN, OUTPUT);
    
    // Take first measurement
    measure_and_transmit();
    
    // Sleep
    go_to_sleep();
}

void loop() {
    // Wakes from deep sleep here
    measure_and_transmit();
    go_to_sleep();
}

void measure_and_transmit() {
    SoilPacket pkt;
    pkt.node_id = NODE_ID;
    pkt.seq_num = sequence++;
    pkt.timestamp = get_rtc_time();
    pkt.battery_mv = read_battery();
    
    // Measure 8 channels
    for (int ch = 0; ch < 8; ch++) {
        select_mux(ch);
        delay(50);  // Settle
        
        // Use 10 kHz as primary frequency (best moisture correlation)
        float drive_v = 0.5;  // DAC amplitude 0.5V
        float sense_v = measure_rms(10000);  // Measure at 10 kHz
        float current = sense_v / 100.0;  // 100Ω sense resistor
        float impedance = drive_v / current;
        
        // Scale: store as milliohms × 1000 = microohms
        pkt.z_mag[ch] = (uint16_t)(impedance * 1000.0);
    }
    
    // Read soil temperature
    pkt.soil_temp_c = (int16_t)(read_temperature() * 10.0);  // °C × 10
    
    // Transmit
    radio.transmit((uint8_t*)&pkt, sizeof(pkt));
    
    // Wait for TX complete
    while (radio.getStatus() == TX_BUSY);
}

float measure_rms(uint16_t freq_hz) {
    // Generate sine on DAC, sample ADC, compute RMS
    const int samples = 1000;
    const int sample_rate = 100000;  // 100 kSa/s
    
    float sum_sq = 0;
    for (int i = 0; i < samples; i++) {
        // DAC value: 0-255 sine
        uint8_t dac_val = 128 + 127 * sin(2 * PI * freq_hz * i / sample_rate);
        dac_output_voltage(DAC_CHANNEL_1, dac_val);
        
        // Small delay for DAC settling
        delayMicroseconds(10);
        
        // Read ADC
        int adc_val = adc1_get_raw(ADC_PIN);
        float voltage = adc_val * 3.3 / 4095.0;
        sum_sq += voltage * voltage;
        
        delayMicroseconds(1000000 / sample_rate - 10);
    }
    
    return sqrt(sum_sq / samples);
}

void select_mux(int ch) {
    digitalWrite(MUX_A0, ch & 0x01);
    digitalWrite(MUX_A1, ch & 0x02);
    digitalWrite(MUX_A2, ch & 0x04);
    digitalWrite(MUX_EN, LOW);  // Enable
}

void go_to_sleep() {
    // Disable MUX to save power
    digitalWrite(MUX_EN, HIGH);
    
    // Configure wake timer
    esp_sleep_enable_timer_wakeup(SLEEP_MS * 1000);
    
    // Deep sleep
    esp_deep_sleep_start();
}

uint16_t read_battery() {
    // Read via voltage divider on ADC
    int raw = adc1_get_raw(ADC1_CHANNEL_1);
    return (uint16_t)(raw * 3.3 * 2 / 4095 * 1000);  // mV, ×2 for divider
}

float read_temperature() {
    // DS18B20 1-Wire read
    OneWire ds(TEMP_PIN);  // GPIO pin for 1-Wire
    byte data[9];
    
    ds.reset();
    ds.select(addr);  // Node-specific ROM address
    ds.write(0x44);  // Start conversion
    delay(750);      // 750ms for 12-bit resolution
    
    ds.reset();
    ds.select(addr);
    ds.write(0xBE);  // Read scratchpad
    for (int i = 0; i < 9; i++) data[i] = ds.read();
    
    int16_t raw = (data[1] << 8) | data[0];
    return (float)raw / 16.0;  // °C
}

uint32_t get_rtc_time() {
    // Use ESP32 RTC (set on first boot from gateway or NTP)
    return rtc.getEpoch();
}
```

---

## Gateway Software (Python)

```python
#!/usr/bin/env python3
"""
gateway.py — LoRa receiver + data aggregation for greenhouse network
"""

import sqlite3
import json
import time
import struct
from datetime import datetime
from pathlib import Path
import zmq

# LoRa packet format (matches node firmware)
PACKET_FMT = '<BHHIH8HhH'  # node_id, seq, timestamp, battery, z_mag[8], temp_c, crc
PACKET_SIZE = struct.calcsize(PACKET_FMT)

class SoilGateway:
    def __init__(self, db_path='greenhouse.db', lora_port='/dev/ttyUSB1'):
        self.db = sqlite3.connect(db_path)
        self.init_db()
        self.zmq_ctx = zmq.Context()
        self.pub = self.zmq_ctx.socket(zmq.PUB)
        self.pub.bind('tcp://*:5556')  # Dashboard clients subscribe here
        
    def init_db(self):
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS soil_readings (
                id INTEGER PRIMARY KEY,
                node_id INTEGER,
                timestamp INTEGER,
                received_at REAL,
                battery_mv INTEGER,
                z_ch0 REAL, z_ch1 REAL, z_ch2 REAL, z_ch3 REAL,
                z_ch4 REAL, z_ch5 REAL, z_ch6 REAL, z_ch7 REAL,
                soil_temp_c REAL
            )
        ''')
        self.db.execute('''
            CREATE INDEX IF NOT EXISTS idx_time_node 
            ON soil_readings(node_id, timestamp)
        ''')
        self.db.commit()
    
    def on_lora_packet(self, raw_bytes):
        if len(raw_bytes) != PACKET_SIZE:
            return
        
        try:
            data = struct.unpack(PACKET_FMT, raw_bytes)
            node_id, seq, timestamp, battery = data[0], data[1], data[2], data[3]
            z_values = [v / 1000.0 for v in data[4:12]]  # Convert from ×1000
            temp_c = data[12] / 10.0  # °C (×10 in packet)
            
            # Store
            self.db.execute('''
                INSERT INTO soil_readings 
                (node_id, timestamp, received_at, battery_mv,
                 z_ch0, z_ch1, z_ch2, z_ch3, z_ch4, z_ch5, z_ch6, z_ch7,
                 soil_temp_c)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (node_id, timestamp, time.time(), battery, *z_values, temp_c))
            self.db.commit()
            
            # Broadcast to dashboard clients
            msg = {
                'node': node_id,
                'time': timestamp,
                'battery': battery,
                'impedance': z_values,
                'soil_temp_c': temp_c
            }
            self.pub.send_json(msg)
            
            # Log
            print(f"[{datetime.now()}] Node {node_id}: "
                  f"Z_avg={sum(z_values)/8:.1f}Ω, temp={temp_c:.1f}°C, batt={battery}mV")
                  
        except Exception as e:
            print(f"Packet error: {e}")
    
    def get_node_history(self, node_id, hours=24):
        """Get time series for a node"""
        since = time.time() - hours * 3600
        cursor = self.db.execute('''
            SELECT timestamp, z_ch0, z_ch1, z_ch2, z_ch3,
                   z_ch4, z_ch5, z_ch6, z_ch7, soil_temp_c
            FROM soil_readings
            WHERE node_id = ? AND timestamp > ?
            ORDER BY timestamp
        ''', (node_id, since))
        return cursor.fetchall()
    
    def run(self):
        """Main loop — read LoRa, store, broadcast"""
        print("Gateway running. Waiting for nodes...")
        while True:
            # Read from LoRa module (implementation depends on module)
            # This would use pyserial or SPI library
            packet = self.lora_receive()
            if packet:
                self.on_lora_packet(packet)
            time.sleep(0.1)

if __name__ == '__main__':
    gw = SoilGateway()
    gw.run()
```

---

## Dashboard (Real-Time)

```python
# Minimal PyQtGraph dashboard
gateway = SoilGateway()
app = pg.mkQApp()
win = pg.GraphicsLayoutWidget()
win.setWindowTitle('Greenhouse Soil Monitor')

# 8×2 grid of plots (8 channels × moisture over time)
plots = {}
for node in range(12):
    p = win.addPlot(row=node//4, col=node%4, title=f'Node {node}')
    plots[node] = p

def update():
    for node in range(12):
        data = gateway.get_node_history(node, hours=1)
        if data:
            t = [d[0] for d in data]
            z_avg = [sum(d[1:9])/8 for d in data]
            plots[node].plot(t, z_avg, clear=True)

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(15000)  # Update every 15 seconds

win.show()
app.exec()
```

---

## Irrigation Trigger Logic

```python
def check_irrigation_needed(node_readings, threshold=500.0):
    """
    Trigger irrigation when average impedance exceeds threshold.
    
    Higher impedance = drier soil (less conductive)
    Threshold calibrated for soil type.
    """
    z_avg = sum(node_readings) / len(node_readings)
    
    if z_avg > threshold:
        return {
            'action': 'irrigate',
            'node': node_id,
            'moisture': z_avg,
            'duration_min': min(30, (z_avg - threshold) / 10)
        }
    return None
```

---

## Build Roadmap

### Phase 1: Proof of Concept (2 weeks)
- [ ] Build 1 sensor node on breadboard
- [ ] Flash ESP32-S3 with measurement + LoRa TX firmware
- [ ] Build gateway with LoRa RX + SQLite logging
- [ ] Test in a pot with dry/wet soil
- [ ] Measure battery life (should be >30 days easily)

### Phase 2: Small Network (1 month)
- [ ] Build 4 nodes + 1 gateway
- [ ] Deploy in actual greenhouse corner
- [ ] Dashboard + SQLite backend
- [ ] Calibrate moisture vs impedance for local soil
- [ ] Irrigation trigger logic

### Phase 3: Full Deployment (2 months)
- [ ] 12 nodes across full acre
- [ ] Solar enclosures, proper electrode probes
- [ ] Cloud integration (MQTT to ThingsBoard / Grafana)
- [ ] Mobile app for alerts

### Phase 4: Optimisation (ongoing)
- [ ] Mesh networking (nodes relay for each other)
- [ ] Adaptive measurement interval (measure more often when changing)
- [ ] Machine learning: predict irrigation needs from weather + history

---

## Cost Summary

| Item | Qty | Unit | Total |
|------|-----|------|-------|
| Sensor nodes | 12 | £68.50 | £822 |
| Gateway (existing V5 + LoRa) | 1 | £15 | £15 |
| Dashboard PC / Raspberry Pi | 1 | £50 | £50 |
| **Total hardware** | | | **£857** |
| Enclosures, cables, mounts | | | ~£100 |
| **Grand total** | | | **~£987** |

Compare: Commercial greenhouse monitoring (Priva, Ridder) starts at £5,000+ per zone.

---

## Next Step

Build the first sensor node on breadboard. Start with:
1. ESP32-S3 + SX1262 basic LoRa TX/RX
2. Add MUX + ADC measurement loop
3. Test in a pot with wet/dry soil

Ready to start on the firmware?
