/*
 * GlassHouse Node v1.0 — Configuration
 * ====================================
 * Hardware: ESP32-S3-DevKitC-1 + AD9833 + OPA1641 TIA + DS18B20
 * Target: Home glasshouse soil monitoring (tomatoes)
 */

#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h>

// ─── Version ────────────────────────────────────────────────────────────────
#define FIRMWARE_VERSION    "1.0.0"
#define HARDWARE_REVISION   "A"

// ─── Node Identity ──────────────────────────────────────────────────────────
// Override at runtime via WiFiManager or serial CLI
#ifndef NODE_ID
  #define NODE_ID           "gh-n01"
#endif

// ─── Pin Mapping (ESP32-S3-DevKitC-1) ───────────────────────────────────────
// AD9833 DDS (SPI)
#define PIN_AD9833_FSYNC    10   // Chip select for AD9833
#define PIN_SPI_SCK         12   // SCK
#define PIN_SPI_MOSI        11   // MOSI

// ADC / Analog
#define PIN_ADC_TIA         1    // ADC1_CH0 (GPIO1) — TIA output
#define PIN_ADC_BATTERY     2    // ADC1_CH1 (GPIO2) — Battery voltage divider

// OneWire Temperature
#define PIN_ONEWIRE         4    // DS18B20 data

// Status LED
#define PIN_LED_STATUS      21   // Onboard RGB or external LED

// ─── Measurement Parameters ─────────────────────────────────────────────────
#define MEASUREMENT_INTERVAL_MS     900000UL   // 15 minutes
#define MEASUREMENT_DURATION_MS     2000UL     // 2 seconds active
#define SLEEP_INTERVAL_US           898000000ULL // 15 min - 2 sec in microseconds

// Excitation
#define EXC_FREQUENCY_HZ            100000.0f   // 100 kHz — validated for VWC
#define EXC_AMPLITUDE_V             0.10f       // 100 mV pp
#define AD9833_MCLK_HZ              25000000UL  // 25 MHz crystal on module

// TIA
#define TIA_GAIN_OHMS               1000.0f     // 1 kΩ feedback
#define TIA_BANDWIDTH_HZ            500000.0f   // ~500 kHz with OPA1641

// ADC
#define ADC_RESOLUTION_BITS         12
#define ADC_REFERENCE_V             3.3f
#define ADC_SAMPLES_PER_MEASUREMENT 1000

// ─── Calibration Defaults ───────────────────────────────────────────────────
// These are overwritten by user calibration via serial / app
struct CalibrationData {
    float tia_gain_ohms;
    float electrode_spacing_m;
    float vwc_dry;          // VWC at "dry" calibration point
    float vwc_wet;          // VWC at "wet" calibration point
    float z_dry;            // |Z| at dry point (Ohms)
    float z_wet;            // |Z| at wet point (Ohms)
    float temp_offset_c;
    bool calibrated;
};

// Flash storage address (EEPROM emulation via Preferences)
#define PREFS_NAMESPACE     "gh_cal"
#define PREFS_KEY_CAL       "calibration"

// ─── WiFi & MQTT ────────────────────────────────────────────────────────────
#define WIFI_CONNECT_TIMEOUT_MS     30000UL
#define MQTT_BROKER_DEFAULT         "192.168.1.100"
#define MQTT_PORT                   1883
#define MQTT_BROKER_DEFAULT         "192.168.1.100"
#define MQTT_TOPIC_TELEMETRY        "glasshouse/%s/telemetry"
#define MQTT_TOPIC_COMMAND          "glasshouse/%s/command"
#define MQTT_QOS                    1
#define MQTT_KEEPALIVE_S            60

// ─── Battery ────────────────────────────────────────────────────────────────
#define BATTERY_VOLTAGE_DIVIDER     2.0f        // R1 = R2 = 100k
#define BATTERY_ADC_MAX_V           3.3f
#define BATTERY_FULL_MV             4200
#define BATTERY_EMPTY_MV            3100
#define BATTERY_LOW_THRESHOLD_MV    3300

// ─── Debug ──────────────────────────────────────────────────────────────────
// Uncomment for verbose serial output
// #define DEBUG_VERBOSE

#ifdef DEBUG_VERBOSE
  #define DBG_PRINT(x)    Serial.print(x)
  #define DBG_PRINTLN(x)  Serial.println(x)
  #define DBG_PRINTF(...) Serial.printf(__VA_ARGS__)
#else
  #define DBG_PRINT(x)
  #define DBG_PRINTLN(x)
  #define DBG_PRINTF(...)
#endif

#endif // CONFIG_H
