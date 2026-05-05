/**
 * @file array_dma_integration.c
 * @brief Integration of DMA acquisition with array control commands
 * @details Adds DMA commands to the existing array control JSON interface
 */

#include "array_control.h"
#include "dma_acquisition.h"
#include "esp_log.h"
#include "cJSON.h"
#include <string.h>

static const char *TAG = "ARRAY_DMA";

// Default DMA configuration
dma_acq_config_t g_default_dma_config = {
    .sample_rate = 20000000,  // 20 MSa/s
    .num_channels = 8,
    .samples_per_channel = 2048,
    .trigger = DMA_ACQ_TRIG_EXT,
    .pre_trigger_samples = 0,
    .channel_map = {0, 1, 2, 3, 4, 5, 6, 7},  // ADC1 channels 0-7
    .trigger_gpio = 15,
    .trigger_edge = 0  // Rising
};

/**
 * @brief Handle DMA initialization command
 * JSON: {"cmd": "dma_init", "num_channels": 8, "samples_per_channel": 2048, ...}
 */
char* cmd_dma_init(const cJSON *params) {
    dma_acq_config_t config = g_default_dma_config;
    
    // Parse optional parameters
    cJSON *item = cJSON_GetObjectItem(params, "num_channels");
    if (item) config.num_channels = item->valueint;
    
    item = cJSON_GetObjectItem(params, "samples_per_channel");
    if (item) config.samples_per_channel = item->valueint;
    
    item = cJSON_GetObjectItem(params, "sample_rate");
    if (item) config.sample_rate = item->valueint;
    
    item = cJSON_GetObjectItem(params, "trigger");
    if (item) {
        if (strcmp(item->valuestring, "soft") == 0) {
            config.trigger = DMA_ACQ_TRIG_SOFT;
        } else if (strcmp(item->valuestring, "timer") == 0) {
            config.trigger = DMA_ACQ_TRIG_TIMER;
        } else {
            config.trigger = DMA_ACQ_TRIG_EXT;
        }
    }
    
    item = cJSON_GetObjectItem(params, "trigger_gpio");
    if (item) config.trigger_gpio = item->valueint;
    
    item = cJSON_GetObjectItem(params, "trigger_edge");
    if (item) config.trigger_edge = item->valueint;
    
    // Initialize DMA
    esp_err_t ret = dma_acq_init(&config);
    
    cJSON *response = cJSON_CreateObject();
    if (ret == ESP_OK) {
        cJSON_AddStringToObject(response, "status", "ok");
        cJSON_AddNumberToObject(response, "sample_rate", config.sample_rate);
        cJSON_AddNumberToObject(response, "num_channels", config.num_channels);
        cJSON_AddNumberToObject(response, "samples_per_channel", config.samples_per_channel);
    } else {
        cJSON_AddStringToObject(response, "status", "error");
        cJSON_AddStringToObject(response, "error", esp_err_to_name(ret));
    }
    
    char *json_str = cJSON_PrintUnformatted(response);
    cJSON_Delete(response);
    return json_str;
}

/**
 * @brief Handle DMA start burst command
 * JSON: {"cmd": "dma_start_burst"}
 */
char* cmd_dma_start_burst(const cJSON *params) {
    esp_err_t ret = dma_acq_start_burst();
    
    cJSON *response = cJSON_CreateObject();
    if (ret == ESP_OK) {
        cJSON_AddStringToObject(response, "status", "ok");
    } else {
        cJSON_AddStringToObject(response, "status", "error");
        cJSON_AddStringToObject(response, "error", esp_err_to_name(ret));
    }
    
    char *json_str = cJSON_PrintUnformatted(response);
    cJSON_Delete(response);
    return json_str;
}

/**
 * @brief Handle DMA start continuous command
 * JSON: {"cmd": "dma_start_continuous"}
 */
char* cmd_dma_start_continuous(const cJSON *params) {
    esp_err_t ret = dma_acq_start_continuous();
    
    cJSON *response = cJSON_CreateObject();
    if (ret == ESP_OK) {
        cJSON_AddStringToObject(response, "status", "ok");
    } else {
        cJSON_AddStringToObject(response, "status", "error");
        cJSON_AddStringToObject(response, "error", esp_err_to_name(ret));
    }
    
    char *json_str = cJSON_PrintUnformatted(response);
    cJSON_Delete(response);
    return json_str;
}

/**
 * @brief Handle DMA stop command
 * JSON: {"cmd": "dma_stop"}
 */
char* cmd_dma_stop(const cJSON *params) {
    dma_acq_stop();
    
    cJSON *response = cJSON_CreateObject();
    cJSON_AddStringToObject(response, "status", "ok");
    
    char *json_str = cJSON_PrintUnformatted(response);
    cJSON_Delete(response);
    return json_str;
}

/**
 * @brief Handle DMA get status command
 * JSON: {"cmd": "dma_get_status"}
 */
char* cmd_dma_get_status(const cJSON *params) {
    dma_acq_status_t status;
    esp_err_t ret = dma_acq_get_status(&status);
    
    cJSON *response = cJSON_CreateObject();
    if (ret == ESP_OK) {
        cJSON_AddStringToObject(response, "status", "ok");
        
        const char* state_str = "unknown";
        switch (status.state) {
            case DMA_ACQ_STATE_IDLE: state_str = "idle"; break;
            case DMA_ACQ_STATE_ARMED: state_str = "armed"; break;
            case DMA_ACQ_STATE_ACQUIRING: state_str = "acquiring"; break;
            case DMA_ACQ_STATE_TRANSFER: state_str = "transfer"; break;
            case DMA_ACQ_STATE_ERROR: state_str = "error"; break;
        }
        cJSON_AddStringToObject(response, "state", state_str);
        cJSON_AddNumberToObject(response, "acquisition_count", status.acquisition_count);
        cJSON_AddNumberToObject(response, "samples_acquired", status.samples_acquired);
        cJSON_AddNumberToObject(response, "samples_expected", status.samples_expected);
        cJSON_AddNumberToObject(response, "buffer_overflows", status.buffer_overflows);
        cJSON_AddNumberToObject(response, "trigger_count", status.trigger_count);
        cJSON_AddNumberToObject(response, "continuity_errors", status.continuity_errors);
        
        if (status.trigger_timestamp_us > 0) {
            cJSON_AddNumberToObject(response, "trigger_timestamp_us", status.trigger_timestamp_us);
        }
        if (status.completion_timestamp_us > 0) {
            cJSON_AddNumberToObject(response, "completion_timestamp_us", status.completion_timestamp_us);
            cJSON_AddNumberToObject(response, "elapsed_us", 
                status.completion_timestamp_us - status.trigger_timestamp_us);
        }
        
        float actual_sr = dma_acq_get_actual_sample_rate();
        if (actual_sr > 0) {
            cJSON_AddNumberToObject(response, "actual_sample_rate", actual_sr);
        }
    } else {
        cJSON_AddStringToObject(response, "status", "error");
        cJSON_AddStringToObject(response, "error", esp_err_to_name(ret));
    }
    
    char *json_str = cJSON_PrintUnformatted(response);
    cJSON_Delete(response);
    return json_str;
}

/**
 * @brief Handle DMA read data command
 * JSON: {"cmd": "dma_read_data"}
 * Followed by binary data transmission
 */
char* cmd_dma_read_data(const cJSON *params) {
    // Get status to check available data
    dma_acq_status_t status;
    dma_acq_get_status(&status);
    
    cJSON *response = cJSON_CreateObject();
    cJSON_AddStringToObject(response, "status", "ok");
    
    // Calculate bytes available
    uint32_t bytes_available = status.samples_acquired * sizeof(uint16_t);
    cJSON_AddNumberToObject(response, "bytes_available", bytes_available);
    cJSON_AddNumberToObject(response, "samples", status.samples_acquired);
    cJSON_AddNumberToObject(response, "channels", 8);  // Fixed for now
    
    char *json_str = cJSON_PrintUnformatted(response);
    cJSON_Delete(response);
    return json_str;
}

/**
 * @brief Handle DMA software trigger command
 * JSON: {"cmd": "dma_trigger"}
 */
char* cmd_dma_trigger(const cJSON *params) {
    esp_err_t ret = dma_acq_trigger_software();
    
    cJSON *response = cJSON_CreateObject();
    if (ret == ESP_OK) {
        cJSON_AddStringToObject(response, "status", "ok");
    } else {
        cJSON_AddStringToObject(response, "status", "error");
        cJSON_AddStringToObject(response, "error", esp_err_to_name(ret));
    }
    
    char *json_str = cJSON_PrintUnformatted(response);
    cJSON_Delete(response);
    return json_str;
}

/**
 * @brief Handle DMA PSRAM info command
 * JSON: {"cmd": "dma_psram_info"}
 */
char* cmd_dma_psram_info(const cJSON *params) {
    uint32_t total_size, write_offset, overflow_count;
    dma_acq_get_psram_info(&total_size, &write_offset, &overflow_count);
    
    cJSON *response = cJSON_CreateObject();
    cJSON_AddStringToObject(response, "status", "ok");
    cJSON_AddNumberToObject(response, "total_size", total_size);
    cJSON_AddNumberToObject(response, "write_offset", write_offset);
    cJSON_AddNumberToObject(response, "overflow_count", overflow_count);
    
    char *json_str = cJSON_PrintUnformatted(response);
    cJSON_Delete(response);
    return json_str;
}

/**
 * @brief Handle DMA verify ramp command
 * JSON: {"cmd": "dma_verify_ramp", "expected_pattern": 0}
 */
char* cmd_dma_verify_ramp(const cJSON *params) {
    uint16_t expected = 0;
    cJSON *item = cJSON_GetObjectItem(params, "expected_pattern");
    if (item) expected = item->valueint;
    
    uint32_t error_count = 0;
    esp_err_t ret = dma_acq_verify_ramp(expected, &error_count);
    
    cJSON *response = cJSON_CreateObject();
    if (ret == ESP_OK) {
        cJSON_AddStringToObject(response, "status", "ok");
        cJSON_AddNumberToObject(response, "error_count", error_count);
        cJSON_AddBoolToObject(response, "passed", error_count == 0);
    } else {
        cJSON_AddStringToObject(response, "status", "error");
        cJSON_AddStringToObject(response, "error", esp_err_to_name(ret));
    }
    
    char *json_str = cJSON_PrintUnformatted(response);
    cJSON_Delete(response);
    return json_str;
}

/**
 * @brief Initialize DMA command handlers
 * Call this from main command router
 */
void array_dma_integration_init(void) {
    ESP_LOGI(TAG, "DMA integration initialized");
    ESP_LOGI(TAG, "Available commands:");
    ESP_LOGI(TAG, "  - dma_init");
    ESP_LOGI(TAG, "  - dma_start_burst");
    ESP_LOGI(TAG, "  - dma_start_continuous");
    ESP_LOGI(TAG, "  - dma_stop");
    ESP_LOGI(TAG, "  - dma_get_status");
    ESP_LOGI(TAG, "  - dma_read_data");
    ESP_LOGI(TAG, "  - dma_trigger");
    ESP_LOGI(TAG, "  - dma_psram_info");
    ESP_LOGI(TAG, "  - dma_verify_ramp");
}
