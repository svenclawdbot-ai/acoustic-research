# Proof of Concept — Soil Impedance + LoRa

*Scope: One node, one receiver, one pot, one weekend.*

---

## What We're Proving

1. ESP32 can generate sine wave, measure soil impedance
2. LoRa can transmit the reading reliably across a greenhouse
3. Gateway can receive, parse, and act on the data
4. Dry soil → high impedance. Wet soil → low impedance. Obvious difference.

---

## Hardware You Need (Shopping List)

### Node (Sender)

| Item | Qty | Cost | Where |
|------|-----|------|-------|
| **ESP32-S3-DevKitC-1** | 1 | £6 | AliExpress / DigiKey |
| **SX1262 LoRa module** (Ebyte E22-900M22S or Heltec HT-RA62) | 1 | £8 | AliExpress |
| **Antenna** (868 MHz whip, SMA) | 1 | £2 | AliExpress |
| **Stainless steel rod** (M6 × 150 mm) | 2 | £1 | Screwfix / hardware store |
| **Resistors** (1 kΩ, 100 Ω) | 2 | £0 | In your parts bin |
| **Dupont wires** | 10 | £0 | In your parts bin |
| **Breadboard** | 1 | £0 | In your parts bin |

**Node total: ~£17**

### Receiver (Gateway Stand-In)

| Item | Qty | Cost | Where |
|------|-----|------|-------|
| **ESP32-S3-DevKitC-1** | 1 | £6 | Same as above |
| **SX1262 LoRa module** | 1 | £8 | Same as above |
| **Antenna** | 1 | £2 | Same as above |
| **USB cable** | 1 | £0 | You have this |

**Receiver total: ~£16**

### Test Setup

| Item | Qty | Cost | Where |
|------|-----|------|-------|
| **Plant pot** (any, ~2 L) | 1 | £1 | Garden centre |
| **Compost / garden soil** | 1 bag | £3 | Garden centre |
| **Multimeter** | 1 | £0 | You have this |

**Grand total: ~£37**

---

## Wiring

### Node (Sender)

```
ESP32-S3          Components
├─ GPIO 17  ─────→ DAC_1 (sine output)
│                  │
│                  ├──[1kΩ]──→ Electrode A (drive)
│                  │
│                  ├──[100Ω]──┐
│                  │           │
│                  │        ┌──┴──┐
│                  │        │SOIL │
│                  │        │     │
│                  │        └──┬──┘
│                  │           │
│                  └──────────→ Electrode B (return)
│
├─ GPIO 1   ─────→ ADC_1 (sense, after 100Ω resistor)
│
├─ GPIO 4   ─────→ LoRa TX (SX1262 MOSI / UART depending on module)
├─ GPIO 5   ─────→ LoRa RX
├─ GPIO 6   ─────→ LoRa BUSY
├─ GPIO 7   ─────→ LoRa DIO1
├─ GPIO 8   ─────→ LoRa NSS
│
└─ GND / 3.3V ───→ Power (USB)
```

**Simplified PoC:** Skip the MUX and LNA. Just 2 electrodes, 2 resistors, ESP32 DAC + ADC.

### Receiver

```
ESP32-S3          LoRa Module
├─ GPIO 4  ──────→ TX
├─ GPIO 5  ──────→ RX
├─ GPIO 6  ──────→ BUSY
├─ GPIO 7  ──────→ DIO1
├─ GPIO 8  ──────→ NSS
└─ GND / 3.3V ───→ Power
```

---

## Node Firmware (Arduino)

```cpp
// soil_node_poc.ino
// PoC: measure one electrode pair, send impedance via LoRa

#include <RadioLib.h>  // SX1262 library

// Pins (ESP32-S3 DevKitC)
#define LORA_CS     8
#define LORA_DIO    7
#define LORA_RST    6
#define LORA_BUSY   6
#define DAC_PIN     17   // DAC_1
#define ADC_PIN     1    // ADC1_CHANNEL_0

// LoRa
SX1262 radio = new Module(LORA_CS, LORA_DIO, LORA_RST, LORA_BUSY);

// Measurement
const uint32_t SAMPLE_RATE = 100000;  // 100 kHz effective
const uint16_t FREQ_HZ = 10000;       // 10 kHz primary frequency
const int SAMPLES = 1000;
const float DRIVE_V = 0.5;          // DAC amplitude 0.5V
const float SENSE_R = 100.0;          // Ohms

// Timing
const uint64_t SLEEP_US = 15 * 60 * 1000000ULL;  // 15 minutes

struct __attribute__((packed)) SoilPacket {
  uint8_t  node_id = 0;
  uint16_t seq = 0;
  uint32_t timestamp = 0;
  uint16_t z_mag = 0;     // Impedance (Ω × 100)
  int16_t  temp_c = 0;    // No temp sensor in PoC, set 0
  uint16_t battery = 0;
};

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Soil Node PoC boot");

  // Init DAC
  dac_output_enable(DAC_CHANNEL_1);
  dac_output_voltage(DAC_CHANNEL_1, 128);  // 1.65V idle

  // Init ADC
  adc1_config_width(ADC_WIDTH_BIT_12);
  adc1_config_channel_atten(ADC1_CHANNEL_0, ADC_ATTEN_DB_12);

  // Init LoRa
  int state = radio.begin(868.0);  // MHz
  if (state == RADIOLIB_ERR_NONE) {
    Serial.println("LoRa init OK");
  } else {
    Serial.printf("LoRa init fail: %d\n", state);
    while (true);  // Halt
  }

  // Set TX power
  radio.setOutputPower(14);  // +14 dBm
  radio.setSpreadingFactor(7);
  radio.setBandwidth(125.0);
  radio.setCodingRate(5);

  // Take first measurement
  measure_and_send();

  // Deep sleep
  go_to_sleep();
}

void loop() {
  // Never reaches here in PoC (always sleeps)
}

void measure_and_send() {
  SoilPacket pkt;
  pkt.node_id = 0;
  pkt.seq++;
  pkt.timestamp = millis() / 1000;  // Seconds since boot (PoC)
  pkt.battery = read_battery();

  // Measure impedance
  float sense_v = measure_rms(FREQ_HZ);
  float current = sense_v / SENSE_R;
  float impedance = DRIVE_V / current;

  // Scale: Ω × 100 for uint16_t
  pkt.z_mag = (uint16_t)(impedance * 100.0);

  Serial.printf("Z = %.1f Ω, V_sense = %.3f V, batt = %d mV\n",
                impedance, sense_v, pkt.battery);

  // Send
  int state = radio.transmit((uint8_t*)&pkt, sizeof(pkt));
  if (state == RADIOLIB_ERR_NONE) {
    Serial.println("TX OK");
  } else {
    Serial.printf("TX fail: %d\n", state);
  }

  radio.sleep();
}

float measure_rms(uint16_t freq) {
  float sum_sq = 0.0;
  int period_us = 1000000 / freq;
  int sample_interval_us = 1000000 / SAMPLE_RATE;  // 10 µs

  for (int i = 0; i < SAMPLES; i++) {
    // Generate sine on DAC (0–255, centred at 128)
    float phase = 2.0 * PI * freq * i / SAMPLE_RATE;
    uint8_t dac_val = 128 + (uint8_t)(127.0 * sin(phase));
    dac_output_voltage(DAC_CHANNEL_1, dac_val);

    delayMicroseconds(sample_interval_us);

    // Read ADC
    int raw = adc1_get_raw(ADC1_CHANNEL_0);
    float voltage = raw * 3.3 / 4095.0;
    sum_sq += voltage * voltage;
  }

  // Idle DAC
  dac_output_voltage(DAC_CHANNEL_1, 128);

  return sqrt(sum_sq / SAMPLES);
}

uint16_t read_battery() {
  // Placeholder: ESP32-S3 USB powered in PoC
  // For real battery, read via voltage divider on ADC
  return 4200;  // 4.2V placeholder
}

void go_to_sleep() {
  Serial.println("Sleeping 15 min...");
  Serial.flush();

  esp_sleep_enable_timer_wakeup(SLEEP_US);
  esp_deep_sleep_start();
}
```

---

## Receiver Firmware (Arduino)

```cpp
// gateway_poc.ino
// PoC: receive LoRa, print to Serial (later: relay to Pi)

#include <RadioLib.h>

#define LORA_CS     8
#define LORA_DIO    7
#define LORA_RST    6
#define LORA_BUSY   6

SX1262 radio = new Module(LORA_CS, LORA_DIO, LORA_RST, LORA_BUSY);

struct __attribute__((packed)) SoilPacket {
  uint8_t  node_id;
  uint16_t seq;
  uint32_t timestamp;
  uint16_t z_mag;
  int16_t  temp_c;
  uint16_t battery;
};

void setup() {
  Serial.begin(115200);
  delay(1000);

  int state = radio.begin(868.0);
  if (state == RADIOLIB_ERR_NONE) {
    Serial.println("Gateway LoRa RX init OK");
  } else {
    Serial.printf("Init fail: %d\n", state);
    while (true);
  }

  radio.setOutputPower(14);
  radio.setSpreadingFactor(7);
  radio.setBandwidth(125.0);
  radio.setCodingRate(5);

  Serial.println("Waiting for packets...");
}

void loop() {
  uint8_t buf[sizeof(SoilPacket)];
  size_t len = sizeof(buf);

  int state = radio.receive(buf, len);

  if (state == RADIOLIB_ERR_NONE) {
    SoilPacket* pkt = (SoilPacket*)buf;

    float z = pkt->z_mag / 100.0;

    Serial.printf("[RX] Node %d | Seq %d | Z=%.1f Ω | Batt=%d mV | RSSI=%.1f dBm | SNR=%.1f dB\n",
                  pkt->node_id, pkt->seq, z, pkt->battery,
                  radio.getRSSI(), radio.getSNR());

    // PoC: simple threshold alarm
    if (z > 400.0) {
      Serial.println("  >>> SOIL DRY — would trigger irrigation");
    } else if (z < 150.0) {
      Serial.println("  >>> SOIL WET — no irrigation needed");
    }

  } else if (state != RADIOLIB_ERR_RX_TIMEOUT) {
    Serial.printf("RX error: %d\n", state);
  }
}
```

---

## Test Protocol

### Step 1: Bench Test (No Soil)

1. Flash node + receiver
2. Place 2 electrodes 5 cm apart in air
3. Power node
4. Receiver should print Z = very high (~5000+ Ω, essentially open circuit)
5. Short electrodes with wire
6. Node should print Z = very low (~10–50 Ω)

**Result:** Measurement circuit works.

### Step 2: Pot Test

1. Fill pot with dry compost
2. Insert electrodes 5 cm apart, 5 cm deep
3. Power node → note Z (should be ~300–800 Ω depending on soil)
4. Add 200 mL water, stir surface
5. Wait 5 min, power node again → note Z (should drop 30–50%)
6. Add 500 mL more water (saturated)
7. Power node → Z should drop further (~100–200 Ω)

**Result:** Dry vs wet is obvious and repeatable.

### Step 3: Range Test

1. Node in pot at one end of garden / greenhouse
2. Receiver at other end
3. Walk apart until packets drop or RSSI < -120 dBm
4. Note distance. Should be 50–100 m+ even with walls.

**Result:** LoRa range confirmed for your site.

---

## What You Learn

| Question | Answer After PoC |
|----------|------------------|
| Can I measure soil impedance with ESP32? | Yes / No (and why) |
| Is dry vs wet obvious? | Should be 2–5× difference |
| Does LoRa reach across greenhouse? | Should get 50+ m easily |
| Is 15-minute battery life realistic? | Measure current draw |
| What calibration do I need? | Note dry / wet / saturated values |

---

## What Comes Next

| If PoC works | Next step |
|-------------|-----------|
| Impedance measurement good | Add MUX (8-ch), LNA, proper electrodes |
| LoRa range good | Deploy 2-node test, add gateway Pi |
| Battery life good | Add solar panel, test 48-hour autonomy |
| Calibration unclear | Run full dry/FC/saturation cycle, record values |

---

## Order Today

**Minimum order to start:**
- 2× ESP32-S3-DevKitC-1 (£12)
- 2× SX1262 module (£16)
- 2× 868 MHz antenna (£4)
- 2× M6 stainless rod (£2)
- 1× bag compost (£3)

**Total: ~£37**

Flash code, stick electrodes in a pot, add water, watch numbers change.

Ready to order?
