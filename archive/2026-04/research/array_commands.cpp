/**
 * @file array_commands.cpp
 * @brief JSON command interface for array control firmware
 * @details Implements command protocol over USB CDC/UART
 * 
 * Protocol: JSON commands in, JSON responses out
 * Binary data streaming for efficiency on ACQUISITION_DATA command
 */

#include <Arduino.h>
#include <ArduinoJson.h>
#include "array_control.h"

// For C++ features in Arduino framework
#ifdef __cplusplus
extern "C" {
#endif

// Include the C array control functions
#include "array_control.h"

#ifdef __cplusplus
}
#endif

static const char *TAG = "ARRAY_CMD";

// Command buffer
#define CMD_BUFFER_SIZE 512
static char g_cmdBuffer[CMD_BUFFER_SIZE];
static size_t g_cmdIndex = 0;

// Status LED pins (from firmware spec)
#define PIN_LED_READY       2
#define PIN_LED_ACQUIRING   5
#define PIN_LED_ERROR       21

// ============================================================================
// COMMAND HANDLERS
// ============================================================================

/**
 * @brief Handle PING command
 */
static void cmd_ping(JsonDocument &req, JsonDocument &resp) {
    resp["status"] = "ok";
    resp["version"] = "1.0.0";
    resp["platform"] = "ESP32-S3";
    resp["timestamp"] = millis();
}

/**
 * @brief Handle GET_STATUS command
 */
static void cmd_get_status(JsonDocument &req, JsonDocument &resp) {
    const ArrayState *state = array_get_state();
    
    resp["status"] = "ok";
    resp["initialized"] = state->initialized;
    resp["acquiring"] = state->acquiring;
    resp["sequence_count"] = state->sequenceCount;
    resp["acquisition_count"] = state->acquisitionCount;
    resp["dma_overflows"] = state->dmaOverflowCount;
}

/**
 * @brief Handle SET_GEOMETRY command
 */
static void cmd_set_geometry(JsonDocument &req, JsonDocument &resp) {
    ArrayGeometry geom;
    
    geom.numElements = req["num_elements"] | 8;
    geom.elementPitch = req["element_pitch"] | 0.5f;
    geom.elementWidth = req["element_width"] | 0.4f;
    geom.centerFrequency = req["center_frequency_mhz"] | 1.5f;
    geom.soundSpeed = req["sound_speed_ms"] | 1540.0f;
    geom.aperture = (geom.numElements - 1) * geom.elementPitch;
    
    if (array_configure_geometry(&geom)) {
        resp["status"] = "ok";
        resp["aperture_mm"] = geom.aperture;
        resp["wavelength_mm"] = (geom.soundSpeed / 1000.0f) / geom.centerFrequency;
    } else {
        resp["status"] = "error";
        resp["message"] = "Failed to configure geometry";
    }
}

/**
 * @brief Handle SET_FOCUS command
 */
static void cmd_set_focus(JsonDocument &req, JsonDocument &resp) {
    float depth = req["depth_mm"] | 50.0f;
    float angle = req["angle_deg"] | 0.0f;
    
    if (array_set_focus(depth, angle)) {
        resp["status"] = "ok";
        resp["depth_mm"] = depth;
        resp["angle_deg"] = angle;
        
        // Calculate and return F-number
        const ArrayGeometry *geom = nullptr;  // Need accessor
        // float fnumber = array_get_fnumber(geom, depth);
        // resp["f_number"] = fnumber;
    } else {
        resp["status"] = "error";
        resp["message"] = "Failed to set focus";
    }
}

/**
 * @brief Handle FIRE command
 */
static void cmd_fire(JsonDocument &req, JsonDocument &resp) {
    uint32_t elementMask = req["element_mask"] | 0xFF;
    uint16_t pulseWidth = req["pulse_width_us"] | 10;
    
    digitalWrite(PIN_LED_ACQUIRING, HIGH);
    
    if (array_fire_elements(elementMask, pulseWidth)) {
        resp["status"] = "ok";
        resp["elements_fired"] = elementMask;
        resp["pulse_width_us"] = pulseWidth;
    } else {
        resp["status"] = "error";
        resp["message"] = "Failed to fire elements";
    }
    
    digitalWrite(PIN_LED_ACQUIRING, LOW);
}

/**
 * @brief Handle ACQUIRE command
 */
static void cmd_acquire(JsonDocument &req, JsonDocument &resp) {
    ArrayAcquisitionConfig config;
    
    // Build config from request
    config.geometry.numElements = req["num_elements"] | 8;
    config.geometry.elementPitch = req["element_pitch"] | 0.5f;
    config.geometry.centerFrequency = req["frequency_mhz"] | 1.5f;
    config.geometry.soundSpeed = req["sound_speed"] | 1540.0f;
    
    config.beamform.focusDepth = req["focus_depth_mm"] | 0.0f;
    config.beamform.steeringAngle = req["steering_angle_deg"] | 0.0f;
    config.beamform.dynamicFocus = req["dynamic_focus"] | false;
    
    config.samplesPerChannel = req["samples"] | 1024;
    config.priUs = req["pri_us"] | 1000;
    config.numAverages = req["averages"] | 1;
    
    // Calculate buffer size needed
    size_t bufferSize = config.geometry.numElements * config.samplesPerChannel * 2;  // uint16
    uint8_t *buffer = (uint8_t *)ps_malloc(bufferSize);
    
    if (buffer == nullptr) {
        resp["status"] = "error";
        resp["message"] = "Failed to allocate acquisition buffer";
        return;
    }
    
    digitalWrite(PIN_LED_ACQUIRING, HIGH);
    
    if (array_acquire_single(&config, buffer, bufferSize)) {
        resp["status"] = "ok";
        resp["num_elements"] = config.geometry.numElements;
        resp["samples_per_channel"] = config.samplesPerChannel;
        resp["data_size_bytes"] = bufferSize;
        
        // Send response header
        serializeJson(resp, Serial);
        Serial.println();
        
        // Send binary data
        Serial.write(buffer, bufferSize);
        
        free(buffer);
        digitalWrite(PIN_LED_ACQUIRING, LOW);
        return;  // Skip normal response
    } else {
        resp["status"] = "error";
        resp["message"] = "Acquisition failed";
    }
    
    free(buffer);
    digitalWrite(PIN_LED_ACQUIRING, LOW);
}

/**
 * @brief Handle START_ACQUISITION command (continuous)
 */
static void cmd_start_acquisition(JsonDocument &req, JsonDocument &resp) {
    ArrayAcquisitionConfig config;
    
    config.geometry.numElements = req["num_elements"] | 8;
    config.geometry.elementPitch = req["element_pitch"] | 0.5f;
    config.geometry.centerFrequency = req["frequency_mhz"] | 1.5f;
    config.geometry.soundSpeed = req["sound_speed"] | 1540.0f;
    
    config.beamform.focusDepth = req["focus_depth_mm"] | 0.0f;
    config.beamform.steeringAngle = req["steering_angle_deg"] | 0.0f;
    
    config.samplesPerChannel = req["samples"] | 1024;
    config.priUs = req["pri_us"] | 1000;
    config.numAverages = req["averages"] | 1;
    
    if (array_start_acquisition(&config)) {
        resp["status"] = "ok";
        resp["message"] = "Acquisition started";
        digitalWrite(PIN_LED_ACQUIRING, HIGH);
    } else {
        resp["status"] = "error";
        resp["message"] = "Failed to start acquisition";
    }
}

/**
 * @brief Handle STOP_ACQUISITION command
 */
static void cmd_stop_acquisition(JsonDocument &req, JsonDocument &resp) {
    if (array_stop_acquisition()) {
        resp["status"] = "ok";
        resp["message"] = "Acquisition stopped";
        digitalWrite(PIN_LED_ACQUIRING, LOW);
    } else {
        resp["status"] = "error";
        resp["message"] = "Failed to stop acquisition";
    }
}

/**
 * @brief Handle GET_DATA command (for continuous mode)
 */
static void cmd_get_data(JsonDocument &req, JsonDocument &resp) {
    // In continuous mode, this would return buffered data
    // For now, return status
    const ArrayState *state = array_get_state();
    
    resp["status"] = "ok";
    resp["acquiring"] = state->acquiring;
    resp["acquisition_count"] = state->acquisitionCount;
}

/**
 * @brief Handle CALIBRATE command
 */
static void cmd_calibrate(JsonDocument &req, JsonDocument &resp) {
    // Run calibration sequence
    // 1. Measure element delays
    // 2. Compute compensation values
    // 3. Store in NVS
    
    resp["status"] = "ok";
    resp["message"] = "Calibration complete (stub)";
}

/**
 * @brief Handle RESET command
 */
static void cmd_reset(JsonDocument &req, JsonDocument &resp) {
    resp["status"] = "ok";
    resp["message"] = "Resetting...";
    
    serializeJson(resp, Serial);
    Serial.println();
    Serial.flush();
    
    delay(100);
    ESP.restart();
}

/**
 * @brief Handle GET_GEOMETRY command
 */
static void cmd_get_geometry(JsonDocument &req, JsonDocument &resp) {
    resp["status"] = "ok";
    resp["max_elements"] = ARRAY_MAX_ELEMENTS;
    resp["dma_buffer_size"] = ARRAY_DMA_BUFFER_SIZE;
    resp["adc_sample_rate"] = ARRAY_ADC_SAMPLE_RATE;
    resp["dac_sample_rate"] = ARRAY_DAC_SAMPLE_RATE;
}

// ============================================================================
// COMMAND DISPATCH
// ============================================================================

typedef void (*CommandHandler)(JsonDocument &req, JsonDocument &resp);

struct CommandEntry {
    const char *name;
    CommandHandler handler;
};

static const CommandEntry g_commands[] = {
    {"ping", cmd_ping},
    {"get_status", cmd_get_status},
    {"set_geometry", cmd_set_geometry},
    {"get_geometry", cmd_get_geometry},
    {"set_focus", cmd_set_focus},
    {"fire", cmd_fire},
    {"acquire", cmd_acquire},
    {"start_acquisition", cmd_start_acquisition},
    {"stop_acquisition", cmd_stop_acquisition},
    {"get_data", cmd_get_data},
    {"calibrate", cmd_calibrate},
    {"reset", cmd_reset},
    {nullptr, nullptr}
};

/**
 * @brief Process a single command
 */
static void process_command(const char *json) {
    StaticJsonDocument<512> req;
    StaticJsonDocument<512> resp;
    
    DeserializationError err = deserializeJson(req, json);
    
    if (err) {
        resp["status"] = "error";
        resp["message"] = "JSON parse error";
        resp["details"] = err.c_str();
        serializeJson(resp, Serial);
        Serial.println();
        return;
    }
    
    const char *cmd = req["cmd"];
    if (cmd == nullptr) {
        resp["status"] = "error";
        resp["message"] = "Missing 'cmd' field";
        serializeJson(resp, Serial);
        Serial.println();
        return;
    }
    
    // Find and execute handler
    bool found = false;
    for (int i = 0; g_commands[i].name != nullptr; i++) {
        if (strcmp(cmd, g_commands[i].name) == 0) {
            g_commands[i].handler(req, resp);
            found = true;
            break;
        }
    }
    
    if (!found) {
        resp["status"] = "error";
        resp["message"] = "Unknown command";
        resp["command"] = cmd;
    }
    
    // Send response (unless handler already sent it)
    if (strcmp(cmd, "acquire") != 0) {
        serializeJson(resp, Serial);
        Serial.println();
    }
}

// ============================================================================
// PUBLIC API
// ============================================================================

/**
 * @brief Initialize command interface
 */
void array_commands_init(void) {
    // Configure status LEDs
    pinMode(PIN_LED_READY, OUTPUT);
    pinMode(PIN_LED_ACQUIRING, OUTPUT);
    pinMode(PIN_LED_ERROR, OUTPUT);
    
    digitalWrite(PIN_LED_READY, LOW);
    digitalWrite(PIN_LED_ACQUIRING, LOW);
    digitalWrite(PIN_LED_ERROR, LOW);
    
    // Initialize serial
    Serial.begin(921600);
    while (!Serial && millis() < 5000) {
        delay(10);
    }
    
    g_cmdIndex = 0;
    
    // Signal ready
    digitalWrite(PIN_LED_READY, HIGH);
    
    Serial.println("{\"status\":\"ready\",\"version\":\"1.0.0\"}");
}

/**
 * @brief Process incoming serial data
 * Call this frequently in loop()
 */
void array_commands_process(void) {
    while (Serial.available()) {
        char c = Serial.read();
        
        // Accumulate until newline
        if (c == '\n' || c == '\r') {
            if (g_cmdIndex > 0) {
                g_cmdBuffer[g_cmdIndex] = '\0';
                process_command(g_cmdBuffer);
                g_cmdIndex = 0;
            }
        } else if (g_cmdIndex < CMD_BUFFER_SIZE - 1) {
            g_cmdBuffer[g_cmdIndex++] = c;
        } else {
            // Buffer overflow
            g_cmdIndex = 0;
            StaticJsonDocument<128> resp;
            resp["status"] = "error";
            resp["message"] = "Command too long";
            serializeJson(resp, Serial);
            Serial.println();
        }
    }
}

/**
 * @brief Send unsolicited status update
 */
void array_commands_notify(const char *event, JsonDocument &data) {
    StaticJsonDocument<256> notify;
    notify["event"] = event;
    notify["data"] = data;
    serializeJson(notify, Serial);
    Serial.println();
}

// ============================================================================
// SETUP AND LOOP (Arduino entry points)
// ============================================================================

void setup() {
    // Initialize array control
    if (!array_init()) {
        // Fatal error
        pinMode(PIN_LED_ERROR, OUTPUT);
        while (1) {
            digitalWrite(PIN_LED_ERROR, HIGH);
            delay(100);
            digitalWrite(PIN_LED_ERROR, LOW);
            delay(100);
        }
    }
    
    // Initialize command interface
    array_commands_init();
    
    // Print startup info
    Serial.println("Array Control Firmware v1.0.0");
    Serial.println("Commands: ping, get_status, set_geometry, set_focus, fire, acquire, ...");
}

void loop() {
    // Process incoming commands
    array_commands_process();
    
    // Other background tasks could go here
    
    delay(1);  // Yield to FreeRTOS
}
