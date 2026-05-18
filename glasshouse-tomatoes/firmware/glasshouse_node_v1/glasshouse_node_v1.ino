/*
 * =============================================================================
 * GlassHouse Node v1.0 — Soil Impedance Monitor
 * =============================================================================
 * Hardware: ESP32-S3-DevKitC-1 + AD9833 DDS + OPA1641 TIA + DS18B20
 * Measures: Soil VWC via impedance at 1 kHz, temperature, battery
 * Comms:    WiFi + MQTT to local broker
 * Power:    Deep sleep 15 min, measure 100 ms, target 6+ months on 18650
 *
 * Build:    Arduino IDE 2.x, ESP32 board package >= 3.0.0
 *            Board: "ESP32S3 Dev Module"
 * =============================================================================
 */

#include "config.h"
#include <WiFi.h>
#include <WiFiManager.h>
#include <PubSubClient.h>
#include <Preferences.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <ArduinoJson.h>

// ─── AD9833 SPI (bit-banged for reliability on breadboard) ──────────────────
#define AD9833_FSYNC    10
#define AD9833_SCLK     12
#define AD9833_SDATA    11
#define AD9833_MCLK     25000000UL

// ─── Analog / Digital pins ──────────────────────────────────────────────────
#define PIN_ADC_TIA     1       // ADC1_CH0 — TIA output
#define PIN_ADC_BAT     2       // ADC1_CH1 — battery divider
#define PIN_ONEWIRE     4       // DS18B20 data
#define PIN_LED         21      // Onboard LED (active low on some boards)

// ─── Timing ─────────────────────────────────────────────────────────────────
#define EXC_FREQ_HZ         1000.0f
#define EXC_AMP_V           0.10f
#define TIA_GAIN_OHMS       1000.0f
#define ADC_SAMPLES         400     // 100 cycles × 4 samples/cycle
#define SAMPLE_PERIOD_US    250     // 1 / (4 × 1000 Hz) = 250 µs
#define MEASUREMENT_MS      120     // Slightly longer than 100 ms

// ─── Battery ────────────────────────────────────────────────────────────────
#define BAT_DIVIDER_RATIO   2.0f
#define BAT_FULL_MV         4200
#define BAT_EMPTY_MV        3100

// ─── MQTT / Telemetry ───────────────────────────────────────────────────────
#define MQTT_RETRY_MS       5000
#define WIFI_TIMEOUT_MS     30000

// ─── Calibration stored in flash ────────────────────────────────────────────
struct CalData {
    uint32_t magic;         // 0xCA1B0010
    float z_dry;            // |Z| at dry calibration (Ohms)
    float z_wet;            // |Z| at wet calibration (Ohms)
    float vwc_dry;          // VWC % for dry point
    float vwc_wet;          // VWC % for wet point
    float tia_gain;         // Actual TIA gain (Ohms)
    float exc_v;            // Actual excitation amplitude (V)
    float temp_offset;      // Temperature offset (°C)
    bool  calibrated;       // True after user calibration
    uint16_t crc;           // Simple checksum
};

// ─── Globals ────────────────────────────────────────────────────────────────
WiFiClient       wifiClient;
PubSubClient     mqttClient(wifiClient);
OneWire          oneWire(PIN_ONEWIRE);
DallasTemperature tempSensor(&oneWire);
Preferences      prefs;
CalData          cal;

float g_lastZ = 0;
float g_lastVWC = 0;
float g_lastTemp = 0;
int   g_lastBatteryMV = 0;
int   g_seq = 0;
bool  g_mqttConnected = false;

// ─── Forward declarations ───────────────────────────────────────────────────
void ad9833_init(void);
void ad9833_set_freq(float freq_hz);
void ad9833_write(uint16_t data);
void ad9833_sleep(void);
bool measure_lockin(float* out_z_mag, float* out_z_phase);
float compute_vwc(float z_mag);
bool read_temperature(float* out_temp);
int  read_battery_mv(void);
bool load_calibration(void);
void save_calibration(void);
uint16_t cal_crc(const CalData* c);
bool connect_wifi(void);
bool connect_mqtt(void);
void publish_telemetry(void);
void enter_deep_sleep(void);
void serial_cli(void);
void print_status(void);

// ═════════════════════════════════════════════════════════════════════════════
// SETUP
// ═════════════════════════════════════════════════════════════════════════════
void setup() {
    Serial.begin(115200);
    delay(300);
    Serial.println("\n========================================");
    Serial.println("  GlassHouse Node v1.0");
    Serial.println("  Soil Impedance Monitor");
    Serial.println("========================================");
    Serial.printf("  Firmware: %s\n", FIRMWARE_VERSION);
    Serial.printf("  Node ID:  %s\n", NODE_ID);
    Serial.printf("  Build:    %s %s\n", __DATE__, __TIME__);

    // LED
    pinMode(PIN_LED, OUTPUT);
    digitalWrite(PIN_LED, HIGH);

    // ADC setup
    analogReadResolution(ADC_RESOLUTION_BITS);
    analogSetAttenuation(ADC_11db);  // 0–3.3V range

    // OneWire temp sensor
    tempSensor.begin();
    int tempDevices = tempSensor.getDeviceCount();
    Serial.printf("  DS18B20 sensors found: %d\n", tempDevices);

    // Load calibration
    if (load_calibration()) {
        Serial.println("  ✓ Calibration loaded from flash");
        Serial.printf("     Dry Z=%.1fΩ  Wet Z=%.1fΩ  Cal=%s\n",
                      cal.z_dry, cal.z_wet, cal.calibrated ? "YES" : "NO");
    } else {
        Serial.println("  ! Default calibration — run 'cal' command");
        cal.z_dry = 3000.0f;
        cal.z_wet = 100.0f;
        cal.vwc_dry = 5.0f;
        cal.vwc_wet = 45.0f;
        cal.tia_gain = TIA_GAIN_OHMS;
        cal.exc_v = EXC_AMP_V;
        cal.temp_offset = 0.0f;
        cal.calibrated = false;
    }

    // AD9833 init
    ad9833_init();
    ad9833_set_freq(EXC_FREQ_HZ);
    Serial.printf("  AD9833: %.0f Hz sine active\n", EXC_FREQ_HZ);

    // Sequence counter from RTC memory (persists deep sleep)
    esp_sleep_wakeup_cause_t wakeup = esp_sleep_get_wakeup_cause();
    if (wakeup == ESP_SLEEP_WAKEUP_TIMER) {
        prefs.begin(PREFS_NAMESPACE, false);
        g_seq = prefs.getInt("seq", 0);
        prefs.end();
        Serial.printf("  Wake from deep sleep, seq=%d\n", g_seq);
    } else {
        g_seq = 0;
        Serial.println("  Power-on reset");
    }

    // Check for serial CLI mode (hold any key within 3s)
    Serial.println("\n  Press any key in 3s for CLI mode...");
    delay(3000);
    if (Serial.available()) {
        while (Serial.available()) Serial.read();
        serial_cli();
        // After CLI, continue to measurement
    }

    digitalWrite(PIN_LED, LOW);
    Serial.println("\n--- Starting measurement cycle ---\n");
}

// ═════════════════════════════════════════════════════════════════════════════
// LOOP
// ═════════════════════════════════════════════════════════════════════════════
void loop() {
    unsigned long cycleStart = millis();

    // ─── 1. Measure soil impedance ──────────────────────────────────────────
    float z_mag = 0, z_phase = 0;
    bool measureOk = measure_lockin(&z_mag, &z_phase);
    if (measureOk) {
        g_lastZ = z_mag;
        g_lastVWC = compute_vwc(z_mag);
        Serial.printf("[MEAS] Z=%.2fΩ  Phase=%.1f°  VWC=%.1f%%\n",
                      z_mag, z_phase, g_lastVWC);
    } else {
        Serial.println("[MEAS] ERROR — measurement failed");
        g_lastZ = 0;
        g_lastVWC = -1;
    }

    // ─── 2. Read temperature ────────────────────────────────────────────────
    float temp = 0;
    if (read_temperature(&temp)) {
        g_lastTemp = temp + cal.temp_offset;
        Serial.printf("[TEMP] %.1f°C\n", g_lastTemp);
    } else {
        g_lastTemp = -127.0f;
        Serial.println("[TEMP] ERROR — no sensor");
    }

    // ─── 3. Read battery ────────────────────────────────────────────────────
    g_lastBatteryMV = read_battery_mv();
    Serial.printf("[BATT] %dmV (%d%%)\n",
                  g_lastBatteryMV,
                  map(constrain(g_lastBatteryMV, BAT_EMPTY_MV, BAT_FULL_MV),
                      BAT_EMPTY_MV, BAT_FULL_MV, 0, 100));

    // ─── 4. Connect & publish ───────────────────────────────────────────────
    if (connect_wifi()) {
        if (connect_mqtt()) {
            publish_telemetry();
            mqttClient.disconnect();
        }
        WiFi.disconnect(true);
        WiFi.mode(WIFI_OFF);
    }

    // ─── 5. Save sequence counter ───────────────────────────────────────────
    g_seq++;
    prefs.begin(PREFS_NAMESPACE, false);
    prefs.putInt("seq", g_seq);
    prefs.end();

    // ─── 6. Blink success ───────────────────────────────────────────────────
    digitalWrite(PIN_LED, LOW);
    delay(50);
    digitalWrite(PIN_LED, HIGH);
    delay(50);
    digitalWrite(PIN_LED, LOW);

    Serial.printf("\nCycle complete in %lu ms. Sleeping %lu s...\n\n",
                  millis() - cycleStart, MEASUREMENT_INTERVAL_MS / 1000);

    enter_deep_sleep();
}

// ═════════════════════════════════════════════════════════════════════════════
// AD9833 DDS
// ═════════════════════════════════════════════════════════════════════════════
void ad9833_init(void) {
    pinMode(AD9833_FSYNC, OUTPUT);
    pinMode(AD9833_SCLK, OUTPUT);
    pinMode(AD9833_SDATA, OUTPUT);
    digitalWrite(AD9833_FSYNC, HIGH);
    digitalWrite(AD9833_SCLK, HIGH);
    digitalWrite(AD9833_SDATA, LOW);
}

void ad9833_write(uint16_t data) {
    digitalWrite(AD9833_FSYNC, LOW);
    delayMicroseconds(1);
    for (int i = 15; i >= 0; i--) {
        digitalWrite(AD9833_SCLK, LOW);
        digitalWrite(AD9833_SDATA, (data >> i) & 1);
        delayMicroseconds(1);
        digitalWrite(AD9833_SCLK, HIGH);
        delayMicroseconds(1);
    }
    digitalWrite(AD9833_FSYNC, HIGH);
    delayMicroseconds(1);
}

void ad9833_set_freq(float freq_hz) {
    uint32_t freq_word = (uint32_t)(freq_hz * 268435456.0 / AD9833_MCLK);

    ad9833_write(0x2100);  // Reset = 1, B28 = 1 (write 2 words for freq)
    delayMicroseconds(10);

    uint16_t lsb = freq_word & 0x3FFF;
    uint16_t msb = (freq_word >> 14) & 0x3FFF;
    ad9833_write(0x4000 | lsb);   // FREQ0 register, LSB
    ad9833_write(0x4000 | msb);   // FREQ0 register, MSB

    ad9833_write(0x2000);  // SINE output, exit reset
}

void ad9833_sleep(void) {
    ad9833_write(0x2028);  // Sleep DAC + internal clock
}

// ═════════════════════════════════════════════════════════════════════════════
// LOCK-IN AMPLIFIER DSP
// ═════════════════════════════════════════════════════════════════════════════
bool measure_lockin(float* out_z_mag, float* out_z_phase) {
    float sum_I = 0.0f;
    float sum_Q = 0.0f;
    float v_offset = 0.0f;

    // ─── Pre-measure DC offset (no excitation) ──────────────────────────────
    ad9833_sleep();
    delayMicroseconds(100);
    const int OFFSET_SAMPLES = 50;
    for (int i = 0; i < OFFSET_SAMPLES; i++) {
        v_offset += analogRead(PIN_ADC_TIA);
        delayMicroseconds(10);
    }
    v_offset /= OFFSET_SAMPLES;
    ad9833_set_freq(EXC_FREQ_HZ);
    delayMicroseconds(500);  // Let DDS settle

    // ─── Coherent sampling ──────────────────────────────────────────────────
    unsigned long t0 = micros();
    for (int n = 0; n < ADC_SAMPLES; n++) {
        unsigned long target = t0 + (unsigned long)(n * SAMPLE_PERIOD_US);
        while (micros() < target) { /* tight loop — ~10 µs jitter max */ }

        float raw = (float)analogRead(PIN_ADC_TIA) - v_offset;
        float v_adc = raw * ADC_REFERENCE_V / 4095.0f;

        float phase = 2.0f * PI * EXC_FREQ_HZ * (micros() - t0) / 1000000.0f;
        sum_I += v_adc * cosf(phase);
        sum_Q += v_adc * sinf(phase);
    }

    // ─── Extract amplitude & phase ──────────────────────────────────────────
    float I_avg = sum_I / ADC_SAMPLES;
    float Q_avg = sum_Q / ADC_SAMPLES;
    float v_meas = 2.0f * sqrtf(I_avg * I_avg + Q_avg * Q_avg);

    // Guard against noise floor
    if (v_meas < 0.001f) {
        *out_z_mag = 99999.0f;
        *out_z_phase = 0.0f;
        return false;
    }

    // ─── Compute impedance ──────────────────────────────────────────────────
    float i_soil = v_meas / cal.tia_gain;
    float z_mag = cal.exc_v / i_soil;
    float z_phase = -atan2f(Q_avg, I_avg) * 180.0f / PI;

    *out_z_mag = z_mag;
    *out_z_phase = z_phase;
    return true;
}

// ═════════════════════════════════════════════════════════════════════════════
// VWC CALCULATION (2-point linear interpolation)
// ═════════════════════════════════════════════════════════════════════════════
float compute_vwc(float z_mag) {
    if (!cal.calibrated) {
        // Fallback: rough estimate from default model
        return constrain(50.0f - 15.0f * log10f(z_mag), 0.0f, 60.0f);
    }
    if (z_mag >= cal.z_dry) return cal.vwc_dry;
    if (z_mag <= cal.z_wet) return cal.vwc_wet;

    // Linear interpolation on log(Z) — closer to physics
    float logZ = log10f(z_mag);
    float logDry = log10f(cal.z_dry);
    float logWet = log10f(cal.z_wet);
    float frac = (logDry - logZ) / (logDry - logWet);
    return cal.vwc_dry + frac * (cal.vwc_wet - cal.vwc_dry);
}

// ═════════════════════════════════════════════════════════════════════════════
// TEMPERATURE
// ═════════════════════════════════════════════════════════════════════════════
bool read_temperature(float* out_temp) {
    tempSensor.requestTemperatures();
    float t = tempSensor.getTempCByIndex(0);
    if (t == DEVICE_DISCONNECTED_C) return false;
    *out_temp = t;
    return true;
}

// ═════════════════════════════════════════════════════════════════════════════
// BATTERY
// ═════════════════════════════════════════════════════════════════════════════
int read_battery_mv(void) {
    int raw = analogRead(PIN_ADC_BAT);
    float v_adc = raw * ADC_REFERENCE_V / 4095.0f;
    float v_bat = v_adc * BAT_DIVIDER_RATIO;
    return (int)(v_bat * 1000.0f);
}

// ═════════════════════════════════════════════════════════════════════════════
// CALIBRATION (Flash storage)
// ═════════════════════════════════════════════════════════════════════════════
bool load_calibration(void) {
    prefs.begin(PREFS_NAMESPACE, true);
    size_t len = prefs.getBytesLength(PREFS_KEY_CAL);
    if (len != sizeof(CalData)) {
        prefs.end();
        return false;
    }
    prefs.getBytes(PREFS_KEY_CAL, &cal, sizeof(CalData));
    prefs.end();

    if (cal.magic != 0xCA1B0010) return false;
    if (cal.crc != cal_crc(&cal)) return false;
    return true;
}

void save_calibration(void) {
    cal.magic = 0xCA1B0010;
    cal.crc = cal_crc(&cal);
    prefs.begin(PREFS_NAMESPACE, false);
    prefs.putBytes(PREFS_KEY_CAL, &cal, sizeof(CalData));
    prefs.end();
}

uint16_t cal_crc(const CalData* c) {
    const uint8_t* p = (const uint8_t*)c;
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < sizeof(CalData) - sizeof(uint16_t); i++) {
        crc ^= (uint16_t)p[i] << 8;
        for (int j = 0; j < 8; j++) {
            crc = (crc & 0x8000) ? ((crc << 1) ^ 0x1021) : (crc << 1);
        }
    }
    return crc;
}

// ═════════════════════════════════════════════════════════════════════════════
// WiFi (captive portal via WiFiManager)
// ═════════════════════════════════════════════════════════════════════════════
bool connect_wifi(void) {
    WiFi.mode(WIFI_STA);
    WiFiManager wm;
    wm.setConfigPortalTimeout(180);  // 3 min portal, then give up
    wm.setConnectTimeout(30);

    Serial.print("[WIFI] Connecting");
    bool connected = wm.autoConnect("GlassHouse-Setup");

    if (connected) {
        Serial.printf(" → %s  IP=%s  RSSI=%d\n",
                      WiFi.SSID().c_str(),
                      WiFi.localIP().toString().c_str(),
                      WiFi.RSSI());
        return true;
    } else {
        Serial.println(" → FAILED (no credentials or AP not found)");
        return false;
    }
}

// ═════════════════════════════════════════════════════════════════════════════
// MQTT
// ═════════════════════════════════════════════════════════════════════════════
bool connect_mqtt(void) {
    mqttClient.setServer(MQTT_BROKER_DEFAULT, MQTT_PORT);

    char clientId[32];
    snprintf(clientId, sizeof(clientId), "gh-%s", NODE_ID);

    Serial.printf("[MQTT] Connecting to %s:%d ...", MQTT_BROKER_DEFAULT, MQTT_PORT);
    if (mqttClient.connect(clientId)) {
        Serial.println(" OK");
        g_mqttConnected = true;
        return true;
    } else {
        Serial.printf(" FAIL (rc=%d)\n", mqttClient.state());
        g_mqttConnected = false;
        return false;
    }
}

void publish_telemetry(void) {
    StaticJsonDocument<512> doc;
    doc["node_id"] = NODE_ID;
    doc["timestamp"] = "2026-05-10T14:30:00Z";  // Placeholder — add NTP in v1.1
    doc["vwc_percent"] = round(g_lastVWC * 10.0f) / 10.0f;
    doc["z_magnitude"] = round(g_lastZ * 100.0f) / 100.0f;
    doc["temp_c"] = round(g_lastTemp * 10.0f) / 10.0f;
    doc["battery_mv"] = g_lastBatteryMV;
    doc["rssi_dbm"] = WiFi.RSSI();
    doc["seq"] = g_seq;
    doc["fw"] = FIRMWARE_VERSION;
    doc["cal"] = cal.calibrated;

    char topic[64];
    snprintf(topic, sizeof(topic), MQTT_TOPIC_TELEMETRY, NODE_ID);

    char payload[512];
    size_t len = serializeJson(doc, payload, sizeof(payload));

    if (mqttClient.publish(topic, payload, len, MQTT_QOS)) {
        Serial.printf("[MQTT] Published to %s (%d bytes)\n", topic, (int)len);
    } else {
        Serial.println("[MQTT] Publish failed");
    }
}

// ═════════════════════════════════════════════════════════════════════════════
// DEEP SLEEP
// ═════════════════════════════════════════════════════════════════════════════
void enter_deep_sleep(void) {
    ad9833_sleep();
    digitalWrite(PIN_LED, LOW);
    Serial.flush();

    esp_sleep_enable_timer_wakeup(MEASUREMENT_INTERVAL_MS * 1000ULL);
    esp_deep_sleep_start();
}

// ═════════════════════════════════════════════════════════════════════════════
// SERIAL CLI (calibration & diagnostics)
// ═════════════════════════════════════════════════════════════════════════════
void serial_cli(void) {
    Serial.println("\n========== CLI MODE ==========");
    Serial.println("Commands:");
    Serial.println("  m         — Measure once");
    Serial.println("  cal-dry   — Set dry calibration point");
    Serial.println("  cal-wet   — Set wet calibration point");
    Serial.println("  status    — Show calibration & last readings");
    Serial.println("  reset-cal — Clear calibration");
    Serial.println("  wifi      — Restart WiFi portal");
    Serial.println("  sleep     — Exit CLI and sleep");
    Serial.println("==============================\n");

    while (true) {
        Serial.print("gh> ");
        while (!Serial.available()) { delay(10); }
        String cmd = Serial.readStringUntil('\n');
        cmd.trim();
        cmd.toLowerCase();

        if (cmd == "m") {
            float z, ph;
            if (measure_lockin(&z, &ph)) {
                float vwc = compute_vwc(z);
                Serial.printf("Z=%.2fΩ  Phase=%.1f°  VWC=%.1f%%\n", z, ph, vwc);
            } else {
                Serial.println("Measurement failed");
            }
        }
        else if (cmd == "cal-dry") {
            Serial.println("Measuring dry point... keep electrodes in DRY soil");
            delay(2000);
            float z, ph;
            if (measure_lockin(&z, &ph)) {
                cal.z_dry = z;
                cal.vwc_dry = 5.0f;  // User can override
                cal.calibrated = true;
                save_calibration();
                Serial.printf("Dry cal saved: Z=%.2fΩ\n", z);
            }
        }
        else if (cmd == "cal-wet") {
            Serial.println("Measuring wet point... keep electrodes in WET soil");
            delay(2000);
            float z, ph;
            if (measure_lockin(&z, &ph)) {
                cal.z_wet = z;
                cal.vwc_wet = 45.0f;  // User can override
                cal.calibrated = true;
                save_calibration();
                Serial.printf("Wet cal saved: Z=%.2fΩ\n", z);
            }
        }
        else if (cmd == "status") {
            print_status();
        }
        else if (cmd == "reset-cal") {
            cal.calibrated = false;
            save_calibration();
            Serial.println("Calibration cleared");
        }
        else if (cmd == "wifi") {
            WiFiManager wm;
            wm.resetSettings();
            Serial.println("WiFi credentials cleared. Reboot to reconfigure.");
        }
        else if (cmd == "sleep" || cmd == "exit") {
            Serial.println("Exiting CLI...");
            break;
        }
        else if (cmd.length() > 0) {
            Serial.println("Unknown command. Type 'status' for help.");
        }
    }
}

void print_status(void) {
    Serial.println("\n--- Node Status ---");
    Serial.printf("Node ID:     %s\n", NODE_ID);
    Serial.printf("Firmware:    %s\n", FIRMWARE_VERSION);
    Serial.printf("Calibrated:  %s\n", cal.calibrated ? "YES" : "NO");
    Serial.printf("Dry point:   Z=%.1fΩ  VWC=%.1f%%\n", cal.z_dry, cal.vwc_dry);
    Serial.printf("Wet point:   Z=%.1fΩ  VWC=%.1f%%\n", cal.z_wet, cal.vwc_wet);
    Serial.printf("TIA gain:    %.0fΩ\n", cal.tia_gain);
    Serial.printf("Excitation:  %.2fV\n", cal.exc_v);
    Serial.printf("Last Z:      %.2fΩ\n", g_lastZ);
    Serial.printf("Last VWC:    %.1f%%\n", g_lastVWC);
    Serial.printf("Last temp:   %.1f°C\n", g_lastTemp);
    Serial.printf("Battery:     %dmV\n", g_lastBatteryMV);
    Serial.printf("Sequence:    %d\n", g_seq);
    Serial.println("-------------------\n");
}
