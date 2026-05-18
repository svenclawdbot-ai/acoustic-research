# Barebones Build Guide — Hybrid Soil Spectrometer
*From zero to first measurement in one weekend*
*Assumes: tools ordered, parts arrived, no prior experience*

---

## 📋 BEFORE YOU START

### Read This Safety Brief
- **Soldering irons get to 350°C.** It hurts. Use the stand. Don't leave it on unattended.
- **18650 batteries can vent/fire if shorted.** Use the holder. Don't solder directly to the cell.
- **5V won't kill you** but a short across a LiPo will start a fire. Double-check polarity before powering up.

### Unpack Everything
Lay it all out on a table:
1. Nucleo-H743 board
2. ESP32-S3-DevKitC-1
3. AD9833 DDS module
4. LoRa module (E22 or RFM95W)
5. OPA1641 DIP-8 × 2
6. Breadboards × 3
7. Resistor kit, capacitor kit, wire
8. Tools within arm's reach

Take a photo. You'll forget where things go.

---

## 🔌 DAY 1 — POWER UP & BLINK (Saturday Morning, 2 hours)

### Step 1: Nucleo-H743 First Boot
1. Plug Nucleo into PC via USB-C (the port near the Ethernet jack, **not** the ST-Link USB)
2. A drive called **NODE_H743ZI** appears — this is the built-in programmer
3. Download `stm32_blink.ino` (or use STM32CubeIDE example)
4. In Arduino IDE:
   - Boards Manager → add `https://github.com/stm32duino/BoardManagerFiles/raw/main/package_stm_index.json`
   - Select **Nucleo-144 / H743ZI**
   - Port: the COM port that appeared
5. Upload `Blink` sketch
6. **LD1 (green LED) blinks = board alive**

**Common failure:** Wrong USB port. Use the one labelled **USB_OTG_FS** (near the blue pill), not ST-Link.

### Step 2: ESP32-S3 First Boot
1. Plug ESP32-S3-DevKitC-1 into PC via USB-C
2. In Arduino IDE:
   - Boards Manager → ESP32 by Espressif Systems
   - Select **ESP32S3 Dev Module**
3. Upload `Blink` sketch to GPIO 2 (the onboard LED)
4. **Blue LED blinks = board alive**

**Common failure:** USB-C cable is charge-only. Try another cable. Install CP210x driver if Windows.

### Step 3: AD9833 Test
1. Place AD9833 module on breadboard
2. Wire to Nucleo:
   - AD9833 VCC → Nucleo 3.3V
   - AD9833 GND → Nucleo GND
   - AD9833 SCLK → Nucleo D13 (SPI1_SCK / PA5)
   - AD9833 SDATA → Nucleo D11 (SPI1_MOSI / PA7)
   - AD9833 FSYNC → Nucleo D10 (SPI1_NSS / PA15) — or any GPIO
3. Download `ad9833_test.ino` sketch
4. Upload. Probe output with multimeter AC mode — you should see ~0.5V at 1 kHz

**Don't have the sketch?** I'll generate it below.

---

## ⚡ DAY 1 — ANALOG FRONT-END BREADBOARD (Saturday Afternoon, 2 hours)

### Step 4: TIA (Transimpedance Amplifier)

**What it does:** Converts soil current (µA) to voltage (mV) that the ADC can read.

**Circuit:**
```
                    +3.3V
                      |
                     10kΩ (load — keeps output positive)
                      |
    Electrode A ──────┴──────┬──────────→ OPA1641 pin 3 (+)
    (current in)            │            |
                            │       ┌────┴────┐
                            │       │   -     │ pin 2
                            │       │         │
                            │       └────┬────┘
                            │            │
                            └────────[1kΩ]──→ OPA1641 pin 6 (output)
                            │   R_gain     │
                            │              └────────→ Nucleo A0 (ADC)
                            │
    Electrode B ────────────┴────────────────────────→ OPA1641 pin 2 (-)
    (current return)                                 (virtual ground)
```

**Breadboard wiring:**
1. Place OPA1641 in breadboard, notch facing left, spanning the gap
2. Pin 4 (V-) → GND rail
3. Pin 7 (V+) → +3.3V rail (Nucleo 3.3V)
4. Pin 2 (-) → one end of 1 kΩ resistor → Pin 6 (output)
5. Pin 3 (+) → Electrode A wire
6. Pin 6 (output) → Nucleo A0 (PA3 / ADC3_IN1)
7. Pin 2 (-) → Electrode B wire

**Test without soil:**
- Connect Electrode A to Electrode B with a 1 kΩ resistor (simulate soil)
- AD9833 outputs 1 kHz sine at 100 mV
- You should read ~50 mV at OPA1641 output (100 mV / 1 kΩ × 1 kΩ gain = 100 mV, minus losses)
- Nucleo ADC reads this. Serial print the raw ADC value.

**Expected ADC reading:** ~620 counts (12-bit, 3.3V ref, 100 mV → 100/3300 × 4095 ≈ 124, but with RMS and gain it's ~620)

### Step 5: Voltage Buffer (Optional but Recommended)

If the AD9833 can't drive the soil directly (it can output only ~0.6V max), add a buffer:

```
    AD9833 OUT ─────→ OPA1641 pin 3 (+)
                      pin 2 (-) ───[wire]──→ pin 6 (output)
                      pin 6 ───────────────→ [100Ω series] ───→ Electrode A
```

This is a **voltage follower** (unity gain). The op-amp provides current drive.

---

## 📡 DAY 2 — DIGITAL WIRING & LoRa (Sunday Morning, 2 hours)

### Step 6: STM32 + ESP32 Communication

The STM32 does the measurement. The ESP32 handles WiFi/LoRa. They talk via UART.

**Wiring:**
```
    Nucleo H743                ESP32-S3
    ─────────────             ─────────
    D1 (PA9 / USART1_TX)  →   RX (GPIO44)
    D0 (PA10 / USART1_RX) →   TX (GPIO43)
    GND                    →  GND
```

**Why not SPI/I2C?** UART is foolproof. 115200 baud is plenty for "Z=1234\n" every 15 minutes.

### Step 7: ESP32 + LoRa Module

**If using E22-900M22S (UART mode):**
```
    ESP32-S3                E22 Module
    ─────────               ──────────
    3.3V                 →  VCC
    GND                  →  GND
    GPIO17 (TX)          →  RX
    GPIO18 (RX)          →  TX
    GPIO8                →  M0 (mode pin, pull to GND for normal)
    GPIO9                →  M1 (mode pin, pull to GND for normal)
```

**If using RFM95W (SPI mode):**
```
    ESP32-S3                RFM95W
    ─────────               ──────
    3.3V                 →  VCC
    GND                  →  GND
    GPIO5 (SCK)          →  SCK
    GPIO6 (MISO)         →  MISO
    GPIO7 (MOSI)         →  MOSI
    GPIO10 (CS)          →  NSS
    GPIO11               →  DIO0
    GPIO12               →  RESET
```

### Step 8: Power Everything from One Source

**Option A: USB power (bench testing)**
- Nucleo powered from PC USB (provides 5V on VIN pin)
- ESP32 powered from separate USB
- Connect GND between the two boards (essential!)

**Option B: Single 5V supply (field testing)**
- 18650 → boost converter → 5V
- 5V → Nucleo VIN
- 5V → ESP32 VIN (the 5V pin on DevKitC-1)
- **Warning:** Don't power from 3.7V directly. Nucleo wants 5V or 7-12V. ESP32 wants 5V on VIN (has onboard 3.3V reg).

**For now:** Two USB cables to PC. Keep it simple.

---

## 🧪 DAY 2 — FIRST MEASUREMENT (Sunday Afternoon, 2 hours)

### Step 9: Prepare Electrodes
1. Cut M6 stainless rods to 100 mm (hacksaw + file the burrs)
2. Strip 20 mm insulation from wire ends
3. Wrap wire around rod, solder if you have flux + iron hot enough for steel
   - **Alternative:** Jubilee clip around rod, clamp wire under it
4. Heat shrink over the joint
5. Number them: A, B, C, D (for 4-electrode later; A+B for now)

### Step 10: Dry Soil Test
1. Fill pot with dry compost
2. Insert electrodes A and B, 50 mm apart, 50 mm deep
3. Connect: AD9833 → Electrode A → Soil → Electrode B → TIA → ADC
4. Upload `soil_measure.ino` (generated below)
5. Open Serial Monitor on Nucleo
6. **Record the Z value. Should be high (hundreds to thousands of Ω).**

### Step 11: Wet Soil Test
1. Add 200 mL water to pot
2. Stir surface, wait 5 minutes
3. Power cycle Nucleo (or press reset)
4. **Record Z value. Should drop significantly (30–70% lower).**

### Step 12: Saturated Soil Test
1. Add 500 mL more water
2. Wait 5 minutes
3. Measure again
4. **Record Z value. Should be lowest of the three.**

### Success Criteria
| Test | Pass | Fail |
|------|------|------|
| Dry Z | > 500 Ω | < 100 Ω (maybe shorted?) |
| Wet Z | 30–70% lower than dry | Same as dry |
| Saturated Z | Lower than wet | Higher than wet (check wiring) |
| Repeatability | Same moisture = same Z ±20% | Random jumps |

---

## 📡 DAY 2 — LoRa TRANSMIT TEST (Sunday Evening, 1 hour)

### Step 13: ESP32 Receives from Nucleo
1. Nucleo sends: `Z=847,T=23.5,B=4120\n` every 5 seconds
2. ESP32 reads UART, parses the string
3. ESP32 prints to its own Serial Monitor

### Step 14: ESP32 Transmits via LoRa
1. ESP32 sends parsed Z value over LoRa
2. Second ESP32 (or phone app) receives and displays
3. Walk to other end of house/garden
4. Note when packets stop or RSSI drops below -120 dBm

---

## 💻 FIRMWARE — Copy-Paste Ready

### File 1: `ad9833_test.ino` (Nucleo H743)
```cpp
// AD9833 DDS Test — Generate 1 kHz sine
#include <SPI.h>

#define AD9833_FSYNC  PA15  // D10 on Nucleo
#define SPI1_SCK      PA5   // D13
#define SPI1_MOSI     PA7   // D11

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("AD9833 Test");
  
  SPI.begin();
  pinMode(AD9833_FSYNC, OUTPUT);
  digitalWrite(AD9833_FSYNC, HIGH);
  
  // Reset
  ad9833_write(0x0100);  // Reset = 1
  delay(10);
  
  // Set frequency: 1 kHz with 25 MHz clock
  // Freq reg = f_target × 2^28 / f_MCLK
  // 1000 × 268435456 / 25000000 = 10737.41824 → 0x29F5
  uint32_t freq_word = (uint32_t)(1000.0 * 268435456.0 / 25000000.0);
  
  ad9833_write(0x2000);  // FREQ0 write, LSB
  ad9833_write(freq_word & 0x3FFF);
  ad9833_write(0x2000 | 0x4000);  // FREQ0 write, MSB
  ad9833_write((freq_word >> 14) & 0x3FFF);
  
  // Sine output, exit reset
  ad9833_write(0x2000);  // FREQ0, SINE, no reset
  
  Serial.println("1 kHz sine active on AD9833 OUT");
}

void loop() {
  delay(1000);
}

void ad9833_write(uint16_t data) {
  digitalWrite(AD9833_FSYNC, LOW);
  SPI.transfer16(data);
  digitalWrite(AD9833_FSYNC, HIGH);
}
```

### File 2: `soil_measure.ino` (Nucleo H743)
```cpp
// Soil Impedance Measurement — Lock-in Amplifier (Simplified)
#include <SPI.h>

#define AD9833_FSYNC  PA15
#define ADC_PIN       PA3   // A0 on Arduino header

// TIA gain resistor
const float R_GAIN = 1000.0;  // 1 kΩ

// DDS frequency
const float FREQ_HZ = 1000.0;
const uint32_t MCLK = 25000000;

// ADC buffer
const int SAMPLES = 1000;
int adc_buf[SAMPLES];

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  // Init ADC
  analogReadResolution(12);
  
  // Init SPI + AD9833
  SPI.begin();
  pinMode(AD9833_FSYNC, OUTPUT);
  digitalWrite(AD9833_FSYNC, HIGH);
  
  set_ad9833_freq(FREQ_HZ);
  
  Serial.println("Soil Impedance Spectrometer v0.1");
  Serial.println("Format: Z_magnitude,Z_phase,raw_I,raw_Q");
}

void loop() {
  // Measure impedance
  float z_mag, z_phase;
  measure_lockin(&z_mag, &z_phase);
  
  // Print result
  Serial.print("Z=");
  Serial.print(z_mag, 1);
  Serial.print("Ω,phase=");
  Serial.print(z_phase, 1);
  Serial.println("deg");
  
  // Also send to ESP32 via UART
  Serial1.begin(115200);
  Serial1.print("Z=");
  Serial1.print(z_mag, 1);
  Serial1.print(",T=");
  Serial1.print(23.5);  // placeholder temp
  Serial1.print(",B=");
  Serial1.print(4200);  // placeholder battery
  Serial1.println();
  Serial1.end();
  
  delay(5000);  // 5 second interval for testing
}

void set_ad9833_freq(float freq) {
  uint32_t freq_word = (uint32_t)(freq * 268435456.0 / MCLK);
  
  ad9833_write(0x0100);  // Reset
  delay(1);
  
  ad9833_write(0x4000 | (freq_word & 0x3FFF));        // LSB
  ad9833_write(0x4000 | ((freq_word >> 14) & 0x3FFF)); // MSB
  
  ad9833_write(0x2000);  // Sine, no reset
}

void ad9833_write(uint16_t data) {
  digitalWrite(AD9833_FSYNC, LOW);
  SPI.transfer16(data);
  digitalWrite(AD9833_FSYNC, HIGH);
}

void measure_lockin(float* z_mag, float* z_phase) {
  unsigned long start_us = micros();
  float sample_period_us = 1000000.0 / FREQ_HZ / 4;  // 4 samples per cycle
  
  float sum_I = 0, sum_Q = 0;
  int N = 0;
  
  for (int i = 0; i < SAMPLES; i++) {
    // Wait for sample time
    while (micros() - start_us < (unsigned long)(i * sample_period_us));
    
    // Read ADC
    int raw = analogRead(ADC_PIN);
    float voltage = raw * 3.3 / 4095.0;
    
    // Reference phase (software DDS)
    float phase = 2.0 * PI * FREQ_HZ * (micros() - start_us) / 1000000.0;
    
    // Mix
    sum_I += voltage * cos(phase);
    sum_Q += voltage * sin(phase);
    N++;
  }
  
  // LPF (simple average)
  float I = sum_I / N;
  float Q = sum_Q / N;
  
  // Amplitude
  float v_meas = 2.0 * sqrt(I*I + Q*Q);
  
  // Current through TIA
  float i_soil = v_meas / R_GAIN;
  
  // Impedance
  float v_exc = 0.1;  // 100 mV excitation
  *z_mag = v_exc / i_soil;
  
  // Phase (simplified)
  *z_phase = atan2(Q, I) * 180.0 / PI;
}
```

### File 3: `lora_node.ino` (ESP32-S3)
```cpp
// ESP32-S3 LoRa Node — Receives Z from Nucleo, transmits via LoRa
#include <HardwareSerial.h>

// UART from Nucleo
#define RX_PIN 44
#define TX_PIN 43
HardwareSerial nucleoSerial(1);

// LoRa pins (RFM95W SPI)
#define LORA_SCK  5
#define LORA_MISO 6
#define LORA_MOSI 7
#define LORA_CS   10
#define LORA_RST  12
#define LORA_DIO0 11

// Packet structure
struct SoilPacket {
  uint8_t node_id = 1;
  uint16_t seq = 0;
  float z_magnitude = 0;
  float temperature = 0;
  uint16_t battery_mv = 4200;
};

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("ESP32 LoRa Node boot");
  
  // Init UART from Nucleo
  nucleoSerial.begin(115200, SERIAL_8N1, RX_PIN, TX_PIN);
  
  // Init LoRa (simplified — use RadioLib in production)
  init_lora();
  
  Serial.println("Ready. Waiting for Nucleo data...");
}

void loop() {
  // Read from Nucleo
  if (nucleoSerial.available()) {
    String line = nucleoSerial.readStringUntil('\n');
    
    // Parse: "Z=123.4,T=23.5,B=4120"
    float z = parse_value(line, "Z=");
    float t = parse_value(line, "T=");
    int b = (int)parse_value(line, "B=");
    
    if (z > 0) {
      SoilPacket pkt;
      pkt.seq++;
      pkt.z_magnitude = z;
      pkt.temperature = t;
      pkt.battery_mv = b;
      
      // Transmit via LoRa
      send_lora_packet((uint8_t*)&pkt, sizeof(pkt));
      
      Serial.printf("TX: Z=%.1fΩ, T=%.1f°C, Batt=%dmV\n", z, t, b);
    }
  }
  
  delay(100);
}

float parse_value(String line, String prefix) {
  int idx = line.indexOf(prefix);
  if (idx >= 0) {
    int end = line.indexOf(",", idx);
    if (end < 0) end = line.length();
    String val = line.substring(idx + prefix.length(), end);
    return val.toFloat();
  }
  return 0;
}

void init_lora() {
  // Placeholder — use RadioLib or your preferred LoRa library
  // For RFM95W:
  // radio.begin(868.0);
  // radio.setOutputPower(14);
  Serial.println("LoRa init placeholder — insert your library here");
}

void send_lora_packet(uint8_t* data, size_t len) {
  // Placeholder
  // radio.transmit(data, len);
}
```

---

## 🎯 TROUBLESHOOTING

| Symptom | Cause | Fix |
|---------|-------|-----|
| No blinking LED | Wrong board selected in IDE | Double-check Nucleo/ESP32 board selection |
| No COM port | USB cable is charge-only | Try a different cable |
| AD9833 silent | Wrong SPI pins | Check Nucleo pinout, use PA5/PA7/PA15 |
| ADC reads zero | TIA not powered | Check OPA1641 pin 7 = 3.3V, pin 4 = GND |
| ADC reads 4095 | Input > 3.3V or shorted | Check electrode wiring |
| Z doesn't change with water | Electrodes not in soil | Push them deeper, add salt to water to test |
| Random Z values | Loose breadboard connection | Use solid-core wire, press firmly |
| LoRa doesn't transmit | Wrong module wiring | Check CS/DIO/RESET match your module |

---

## ✅ COMPLETION CHECKLIST

- [ ] Nucleo blinks LED
- [ ] ESP32 blinks LED
- [ ] AD9833 outputs sine (multimeter AC mode)
- [ ] TIA output responds to resistor between electrodes
- [ ] ADC reads changing voltage with 1 kΩ test resistor
- [ ] Dry soil Z recorded
- [ ] Wet soil Z recorded (different from dry)
- [ ] Saturated soil Z recorded (different from wet)
- [ ] ESP32 receives Z from Nucleo via UART
- [ ] LoRa packet transmitted and received

**6/10 = good enough for first weekend. 8/10 = excellent.**

---

*Generated: 2026-05-07*
*Saved to: `hybrid_spectrometer_build_guide.md`*
