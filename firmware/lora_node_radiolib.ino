// =============================================================================
// ESP32-S3 LoRa Node — Production Firmware (RadioLib + RFM95W)
// Receives impedance data from Nucleo-H743 via UART
// Transmits via LoRa 868 MHz every measurement cycle
// Deep sleep between transmissions for battery life
// =============================================================================

#include <RadioLib.h>
#include <HardwareSerial.h>

// ─────────────────────────────────────────────────────────────────────────────
// PIN DEFINITIONS (ESP32-S3 DevKitC-1)
// ─────────────────────────────────────────────────────────────────────────────
#define PIN_LORA_CS     10
#define PIN_LORA_DIO0   11    // DIO0 / IRQ
#define PIN_LORA_RST    12
#define PIN_LORA_DIO1   13    // DIO1 (optional, for CAD)

#define PIN_NUCLEO_TX   43    // ESP32 TX → Nucleo RX
#define PIN_NUCLEO_RX   44    // ESP32 RX ← Nucleo TX

#define PIN_LED         2     // Onboard blue LED
#define PIN_BAT_ADC     1     // Battery voltage divider (if present)

// ─────────────────────────────────────────────────────────────────────────────
// RFM95W MODULE (RadioLib)
// ─────────────────────────────────────────────────────────────────────────────
SX1276 radio = new Module(PIN_LORA_CS, PIN_LORA_DIO0, PIN_LORA_RST, PIN_LORA_DIO1);

// ─────────────────────────────────────────────────────────────────────────────
// UART FROM NUCLEO
// ─────────────────────────────────────────────────────────────────────────────
HardwareSerial nucleoSerial(1);  // UART1 on ESP32-S3

// ─────────────────────────────────────────────────────────────────────────────
// PACKET STRUCTURE (packed binary — efficient over air)
// ─────────────────────────────────────────────────────────────────────────────
#pragma pack(push, 1)
struct SoilPacket {
    uint8_t  magic;           // 0xA5 — packet sync
    uint8_t  version;         // Protocol version
    uint8_t  node_id;         // This node ID
    uint16_t sequence;        // Incrementing sequence
    uint32_t timestamp;       // Unix timestamp (if available)
    float    z_magnitude;     // Impedance |Z| (Ω)
    float    z_phase;         // Phase angle (degrees)
    float    frequency;       // Measurement frequency (Hz)
    int16_t  temp_c;          // Temperature × 100 (centidegrees)
    uint16_t battery_mv;      // Battery voltage (mV)
    uint16_t crc16;           // CRC-16 for integrity
};
#pragma pack(pop)

// ─────────────────────────────────────────────────────────────────────────────
// CONFIGURATION
// ─────────────────────────────────────────────────────────────────────────────
const uint8_t  NODE_ID      = 1;        // Change per node
const uint16_t TX_INTERVAL  = 300;      // Seconds between transmissions (5 min)
const float    FREQ_MHZ     = 868.0;    // EU ISM band
const float    TX_POWER     = 14.0;     // dBm (max 20 for RFM95W)
const uint8_t  SPREADING    = 7;        // SF7 (fast, short range) — use SF9/10 for range
const float    BANDWIDTH    = 125.0;    // kHz
const uint8_t  CODING_RATE  = 5;        // 4/5

// ─────────────────────────────────────────────────────────────────────────────
// STATE
// ─────────────────────────────────────────────────────────────────────────────
SoilPacket lastPacket;
uint16_t sequenceCounter = 0;
bool loraOk = false;

// ─────────────────────────────────────────────────────────────────────────────
// CRC-16 (CCITT-FALSE)
// ─────────────────────────────────────────────────────────────────────────────
uint16_t crc16(const uint8_t* data, size_t length) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < length; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (int j = 0; j < 8; j++) {
            crc = (crc & 0x8000) ? ((crc << 1) ^ 0x1021) : (crc << 1);
        }
    }
    return crc;
}

// ─────────────────────────────────────────────────────────────────────────────
// SETUP
// ─────────────────────────────────────────────────────────────────────────────
void setup() {
    Serial.begin(115200);
    delay(500);
    Serial.println("\n========================================");
    Serial.println("  Hybrid Soil Spectrometer — LoRa Node");
    Serial.println("========================================");

    // LED
    pinMode(PIN_LED, OUTPUT);
    digitalWrite(PIN_LED, LOW);

    // Init UART from Nucleo
    nucleoSerial.begin(115200, SERIAL_8N1, PIN_NUCLEO_RX, PIN_NUCLEO_TX);
    Serial.println("[UART] Nucleo link @ 115200 baud");

    // Init LoRa
    Serial.print("[LoRa] Init RFM95W @ ");
    Serial.print(FREQ_MHZ);
    Serial.println(" MHz ...");

    int state = radio.begin(FREQ_MHZ, BANDWIDTH, SPREADING, CODING_RATE);
    if (state == RADIOLIB_ERR_NONE) {
        radio.setOutputPower(TX_POWER);
        loraOk = true;
        Serial.println("[LoRa] ✓ Init OK");
        Serial.printf("       SF=%d, BW=%.0fkHz, CR=4/%d, PWR=%.0fdBm\n",
                      SPREADING, BANDWIDTH, CODING_RATE, TX_POWER);
    } else {
        Serial.printf("[LoRa] ✗ Init failed: %d\n", state);
        flashError(3);
    }

    // Init packet template
    memset(&lastPacket, 0, sizeof(lastPacket));
    lastPacket.magic = 0xA5;
    lastPacket.version = 1;
    lastPacket.node_id = NODE_ID;

    Serial.println("[MAIN] Ready. Waiting for Nucleo data...\n");
}

// ─────────────────────────────────────────────────────────────────────────────
// MAIN LOOP
// ─────────────────────────────────────────────────────────────────────────────
void loop() {
    // 1. Read from Nucleo (non-blocking, timeout after 30s)
    SoilPacket pkt = readFromNucleo(30000);

    // 2. If valid packet received, transmit via LoRa
    if (pkt.z_magnitude > 0) {
        digitalWrite(PIN_LED, HIGH);

        pkt.sequence = ++sequenceCounter;
        pkt.battery_mv = readBattery();
        pkt.crc16 = computePacketCRC(pkt);

        // Print locally
        printPacket(pkt);

        // Transmit
        if (loraOk) {
            transmitPacket(pkt);
        }

        digitalWrite(PIN_LED, LOW);
    } else {
        Serial.println("[MAIN] No data from Nucleo this cycle");
    }

    // 3. Sleep until next interval
    goToDeepSleep(TX_INTERVAL);
}

// ─────────────────────────────────────────────────────────────────────────────
// READ FROM NUCLEO VIA UART
// Parses: "Z=123.45,P=-12.34,F=1000.00,T=23.50\n"
// ─────────────────────────────────────────────────────────────────────────────
SoilPacket readFromNucleo(unsigned long timeoutMs) {
    SoilPacket pkt;
    memset(&pkt, 0, sizeof(pkt));
    pkt.magic = 0xA5;
    pkt.version = 1;
    pkt.node_id = NODE_ID;

    unsigned long start = millis();
    String buffer = "";

    while (millis() - start < timeoutMs) {
        while (nucleoSerial.available()) {
            char c = nucleoSerial.read();
            if (c == '\n') {
                // Parse line
                pkt.z_magnitude = parseValue(buffer, "Z=");
                pkt.z_phase     = parseValue(buffer, "P=");
                pkt.frequency   = parseValue(buffer, "F=");
                pkt.temp_c      = (int16_t)(parseValue(buffer, "T=") * 100);

                if (pkt.z_magnitude > 0) {
                    Serial.printf("[UART] RX: %s", buffer.c_str());
                    return pkt;
                }
                buffer = "";
            } else {
                buffer += c;
                if (buffer.length() > 128) buffer = "";  // Overflow protection
            }
        }
        delay(10);
    }

    return pkt;  // Returns empty if timeout
}

float parseValue(const String& line, const char* prefix) {
    int idx = line.indexOf(prefix);
    if (idx >= 0) {
        int start = idx + strlen(prefix);
        int end = line.indexOf(",", start);
        if (end < 0) end = line.indexOf("\n", start);
        if (end < 0) end = line.length();
        String val = line.substring(start, end);
        return val.toFloat();
    }
    return 0.0;
}

// ─────────────────────────────────────────────────────────────────────────────
// TRANSMIT VIA LORA
// ─────────────────────────────────────────────────────────────────────────────
void transmitPacket(const SoilPacket& pkt) {
    Serial.print("[LoRa] TX ... ");

    // RadioLib transmit
    int state = radio.transmit((uint8_t*)&pkt, sizeof(pkt));

    if (state == RADIOLIB_ERR_NONE) {
        Serial.printf("OK | RSSI=%.1f dBm | SNR=%.1f dB\n",
                      radio.getRSSI(), radio.getSNR());
    } else if (state == RADIOLIB_ERR_PACKET_TOO_LONG) {
        Serial.println("FAIL: Packet too long");
    } else if (state == RADIOLIB_ERR_TX_TIMEOUT) {
        Serial.println("FAIL: TX timeout");
    } else {
        Serial.printf("FAIL: Error %d\n", state);
    }

    // Put radio to sleep (low power)
    radio.sleep();
}

// ─────────────────────────────────────────────────────────────────────────────
// PACKET CRC
// ─────────────────────────────────────────────────────────────────────────────
uint16_t computePacketCRC(const SoilPacket& pkt) {
    // CRC over everything except the crc16 field itself
    size_t crcLen = sizeof(pkt) - sizeof(pkt.crc16);
    return crc16((const uint8_t*)&pkt, crcLen);
}

bool verifyPacketCRC(const SoilPacket& pkt) {
    uint16_t expected = computePacketCRC(pkt);
    return pkt.crc16 == expected;
}

// ─────────────────────────────────────────────────────────────────────────────
// BATTERY READING (voltage divider on PIN_BAT_ADC)
// ─────────────────────────────────────────────────────────────────────────────
uint16_t readBattery() {
    // If no voltage divider, return placeholder
    // 18650 nominal: 3.7V, full: 4.2V, empty: 3.0V
    // Divider: 100k / 100k = 1/2, so 4.2V → 2.1V at ADC
    // ADC 12-bit @ 3.3V: 4095 × 2.1/3.3 ≈ 2607

    #ifdef PIN_BAT_ADC
    int raw = analogRead(PIN_BAT_ADC);
    // Convert to mV: raw × 2 × 3300 / 4095
    return (uint16_t)((uint32_t)raw * 6600 / 4095);
    #else
    return 4200;  // Placeholder
    #endif
}

// ─────────────────────────────────────────────────────────────────────────────
// DEEP SLEEP
// ─────────────────────────────────────────────────────────────────────────────
void goToDeepSleep(uint16_t seconds) {
    Serial.printf("[SLEEP] Entering deep sleep for %u seconds...\n", seconds);
    Serial.flush();

    // Configure wake-up source: timer
    esp_sleep_enable_timer_wakeup((uint64_t)seconds * 1000000ULL);

    // Optional: configure UART wake (if you want instant wake on Nucleo data)
    // esp_sleep_enable_uart_wakeup(1);

    // Go to sleep
    esp_deep_sleep_start();
    // Execution never reaches here
}

// ─────────────────────────────────────────────────────────────────────────────
// DEBUG / UTILITIES
// ─────────────────────────────────────────────────────────────────────────────
void printPacket(const SoilPacket& pkt) {
    Serial.println("[PACKET] ───────────────────────────────");
    Serial.printf("  Node:      %d\n", pkt.node_id);
    Serial.printf("  Seq:       %d\n", pkt.sequence);
    Serial.printf("  |Z|:       %.2f Ω\n", pkt.z_magnitude);
    Serial.printf("  Phase:     %.2f°\n", pkt.z_phase);
    Serial.printf("  Freq:      %.1f Hz\n", pkt.frequency);
    Serial.printf("  Temp:      %.1f °C\n", pkt.temp_c / 100.0);
    Serial.printf("  Battery:   %.2f V\n", pkt.battery_mv / 1000.0);
    Serial.printf("  CRC:       0x%04X (%s)\n", pkt.crc16,
                  verifyPacketCRC(pkt) ? "OK" : "FAIL");
    Serial.println("────────────────────────────────────────");
}

void flashError(int count) {
    for (int i = 0; i < count; i++) {
        digitalWrite(PIN_LED, HIGH);
        delay(200);
        digitalWrite(PIN_LED, LOW);
        delay(200);
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// SETUP() / LOOP() WRAPPER FOR ARDUINO
// ─────────────────────────────────────────────────────────────────────────────
// (Already defined above — this file is complete)
