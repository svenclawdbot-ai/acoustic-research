// =============================================================================
// LoRa Gateway / Receiver — Production Firmware (RadioLib + RFM95W)
// Receives SoilPacket from field nodes, prints to Serial, forwards to MQTT/HTTP
// Run on: ESP32-S3, ESP32, or STM32 Nucleo with RFM95W
// =============================================================================

#include <RadioLib.h>

// ─────────────────────────────────────────────────────────────────────────────
// PIN DEFINITIONS
// ─────────────────────────────────────────────────────────────────────────────
#define PIN_LORA_CS     10
#define PIN_LORA_DIO0   11    // IRQ
#define PIN_LORA_RST    12
#define PIN_LORA_DIO1   13    // Optional

#define PIN_LED         2

// ─────────────────────────────────────────────────────────────────────────────
// RFM95W MODULE
// ─────────────────────────────────────────────────────────────────────────────
SX1276 radio = new Module(PIN_LORA_CS, PIN_LORA_DIO0, PIN_LORA_RST, PIN_LORA_DIO1);

// ─────────────────────────────────────────────────────────────────────────────
// PACKET STRUCTURE (must match transmitter)
// ─────────────────────────────────────────────────────────────────────────────
#pragma pack(push, 1)
struct SoilPacket {
    uint8_t  magic;           // 0xA5
    uint8_t  version;         // Protocol version
    uint8_t  node_id;         // Node ID
    uint16_t sequence;        // Sequence counter
    uint32_t timestamp;       // Unix timestamp
    float    z_magnitude;     // |Z| (Ω)
    float    z_phase;         // Phase (degrees)
    float    frequency;       // Frequency (Hz)
    int16_t  temp_c;          // Temperature × 100
    uint16_t battery_mv;      // Battery voltage (mV)
    uint16_t crc16;           // CRC-16
};
#pragma pack(pop)

// ─────────────────────────────────────────────────────────────────────────────
// CONFIGURATION (must match transmitter)
// ─────────────────────────────────────────────────────────────────────────────
const float FREQ_MHZ     = 868.0;
const float BANDWIDTH    = 125.0;
const uint8_t SPREADING  = 7;
const uint8_t CODING_RATE = 5;

// ─────────────────────────────────────────────────────────────────────────────
// STATISTICS
// ─────────────────────────────────────────────────────────────────────────────
uint32_t packetsRx = 0;
uint32_t packetsOk = 0;
uint32_t packetsBad = 0;
float lastRSSI = -999;
float lastSNR = -999;

// ─────────────────────────────────────────────────────────────────────────────
// CRC-16 (must match transmitter)
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

bool verifyPacketCRC(const SoilPacket& pkt) {
    size_t crcLen = sizeof(pkt) - sizeof(pkt.crc16);
    uint16_t expected = crc16((const uint8_t*)&pkt, crcLen);
    return pkt.crc16 == expected;
}

// ─────────────────────────────────────────────────────────────────────────────
// SETUP
// ─────────────────────────────────────────────────────────────────────────────
void setup() {
    Serial.begin(115200);
    delay(500);
    Serial.println("\n========================================");
    Serial.println("  Hybrid Soil Spectrometer — Gateway");
    Serial.println("========================================");

    pinMode(PIN_LED, OUTPUT);
    digitalWrite(PIN_LED, LOW);

    Serial.print("[LoRa] Init RFM95W @ ");
    Serial.print(FREQ_MHZ);
    Serial.println(" MHz ...");

    int state = radio.begin(FREQ_MHZ, BANDWIDTH, SPREADING, CODING_RATE);
    if (state == RADIOLIB_ERR_NONE) {
        Serial.println("[LoRa] ✓ Init OK — waiting for packets...\n");
    } else {
        Serial.printf("[LoRa] ✗ Init failed: %d\n", state);
        while (true) {
            digitalWrite(PIN_LED, HIGH); delay(100);
            digitalWrite(PIN_LED, LOW); delay(100);
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// MAIN LOOP
// ─────────────────────────────────────────────────────────────────────────────
void loop() {
    // Check for incoming packet
    int state = radio.receive((uint8_t*)&lastPacket, sizeof(SoilPacket));

    if (state == RADIOLIB_ERR_NONE) {
        packetsRx++;
        digitalWrite(PIN_LED, HIGH);

        // Get signal stats
        lastRSSI = radio.getRSSI();
        lastSNR = radio.getSNR();

        // Verify packet
        if (lastPacket.magic == 0xA5 && verifyPacketCRC(lastPacket)) {
            packetsOk++;
            printPacket(lastPacket);
            printStats();
        } else {
            packetsBad++;
            Serial.println("[RX] BAD PACKET (wrong magic or CRC fail)");
            Serial.printf("       Magic: 0x%02X (expected 0xA5)\n", lastPacket.magic);
            Serial.printf("       CRC:   0x%04X\n", lastPacket.crc16);
        }

        digitalWrite(PIN_LED, LOW);
    } else if (state != RADIOLIB_ERR_RX_TIMEOUT) {
        Serial.printf("[RX] Error: %d\n", state);
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// PRINT PACKET
// ─────────────────────────────────────────────────────────────────────────────
void printPacket(const SoilPacket& pkt) {
    Serial.println("\n[RX] ═══════════════════════════════════════");
    Serial.printf("     Node:      #%d\n", pkt.node_id);
    Serial.printf("     Seq:       %d\n", pkt.sequence);
    Serial.printf("     |Z|:       %.2f Ω @ %.1f Hz\n", pkt.z_magnitude, pkt.frequency);
    Serial.printf("     Phase:     %.2f°\n", pkt.z_phase);
    Serial.printf("     Temp:      %.1f °C\n", pkt.temp_c / 100.0);
    Serial.printf("     Battery:   %.2f V\n", pkt.battery_mv / 1000.0);
    Serial.printf("     RSSI:      %.1f dBm\n", lastRSSI);
    Serial.printf("     SNR:       %.1f dB\n", lastSNR);

    // Simple soil moisture inference
    if (pkt.z_magnitude > 5000) {
        Serial.println("     ★ SOIL:    DRY — needs water!");
    } else if (pkt.z_magnitude > 1000) {
        Serial.println("     ★ SOIL:    MODERATE");
    } else if (pkt.z_magnitude > 200) {
        Serial.println("     ★ SOIL:    MOIST — good");
    } else {
        Serial.println("     ★ SOIL:    SATURATED");
    }
    Serial.println("     ═══════════════════════════════════════");
}

// ─────────────────────────────────────────────────────────────────────────────
// PRINT STATISTICS
// ─────────────────────────────────────────────────────────────────────────────
void printStats() {
    if (packetsRx % 10 == 0) {
        Serial.printf("\n[STATS] Total: %d | OK: %d | Bad: %d | Success: %.1f%%\n\n",
                      packetsRx, packetsOk, packetsBad,
                      packetsRx > 0 ? (100.0 * packetsOk / packetsRx) : 0);
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// GLOBALS (for loop access)
// ─────────────────────────────────────────────────────────────────────────────
SoilPacket lastPacket;

// ─────────────────────────────────────────────────────────────────────────────
// END
// ─────────────────────────────────────────────────────────────────────────────
