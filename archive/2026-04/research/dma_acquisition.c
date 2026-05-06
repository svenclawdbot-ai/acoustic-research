/**
 * @file dma_acquisition.c
 * @brief DMA acquisition with PSRAM buffering for ESP32-S3
 * @details High-speed multi-channel ADC acquisition using DMA to PSRAM
 * 
 * Architecture:
 * - Burst mode: DMA → SRAM ping-pong buffer → USB
 * - Continuous mode: DMA → PSRAM ring buffer → USB (store & forward)
 */

#include "dma_acquisition.h"
#include "esp_log.h"
#include "esp_heap_caps.h"
#include "esp_psram.h"
#include "driver/adc.h"
#include "esp_adc/adc_continuous.h"
#include "driver/gptimer.h"
#include "driver/gpio.h"
#include "hal/adc_types.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "freertos/ringbuf.h"

static const char *TAG = "DMA_ACQ";

// ============================================================================
// INTERNAL STATE
// ============================================================================

static struct {
    // Configuration
    dma_acq_config_t config;
    bool initialized;
    
    // ADC handle
    adc_continuous_handle_t adc_handle;
    
    // DMA buffers (SRAM - burst mode)
    dma_buffer_t dma_buffers[DMA_ACQ_CIRCULAR_BUFFERS];
    uint8_t *dma_buffer_a;
    uint8_t *dma_buffer_b;
    volatile uint8_t active_buffer;
    
    // PSRAM buffer (continuous mode)
    uint8_t *psram_buffer;
    uint32_t psram_write_offset;
    uint32_t psram_overflow_count;
    bool use_psram;
    
    // Status
    dma_acq_status_t status;
    
    // Synchronization
    SemaphoreHandle_t completion_sem;
    SemaphoreHandle_t mutex;
    
    // Timing
    gptimer_handle_t timer_handle;
    uint64_t start_time_us;
    
} g_state = {0};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * @brief Get bytes per sample based on configuration
 */
static inline uint32_t get_bytes_per_sample(void) {
    return g_state.config.num_channels * sizeof(uint16_t);  // 12-bit ADC in 16-bit container
}

/**
 * @brief Calculate DMA buffer size for given samples
 */
static uint32_t calculate_dma_buffer_size(uint32_t samples_per_channel) {
    return samples_per_channel * get_bytes_per_sample();
}

// ============================================================================
// DMA ISR HANDLER
// ============================================================================

void IRAM_ATTR dma_acq_isr_handler(void *arg) {
    BaseType_t high_task_wakeup = pdFALSE;
    
    // Get ADC events
    adc_continuous_evt_cbs_t evt;
    uint32_t result_len = 0;
    
    // In continuous mode, copy to PSRAM
    if (g_state.use_psram && g_state.psram_buffer) {
        uint8_t *read_buf = g_state.dma_buffers[g_state.active_buffer].data;
        uint32_t buf_size = g_state.dma_buffers[g_state.active_buffer].size;
        
        // Read from ADC DMA buffer
        esp_err_t ret = adc_continuous_read(g_state.adc_handle, 
                                             read_buf, buf_size, 
                                             &result_len, 0);
        
        if (ret == ESP_OK && result_len > 0) {
            // Copy to PSRAM ring buffer
            uint32_t space_remaining = DMA_ACQ_PSRAM_BUFFER_SIZE - g_state.psram_write_offset;
            
            if (result_len <= space_remaining) {
                // Single copy
                memcpy(g_state.psram_buffer + g_state.psram_write_offset, read_buf, result_len);
                g_state.psram_write_offset += result_len;
            } else {
                // Wrap around
                memcpy(g_state.psram_buffer + g_state.psram_write_offset, read_buf, space_remaining);
                memcpy(g_state.psram_buffer, read_buf + space_remaining, result_len - space_remaining);
                g_state.psram_write_offset = result_len - space_remaining;
                g_state.psram_overflow_count++;
            }
            
            g_state.status.samples_acquired += result_len / get_bytes_per_sample();
        }
    } else {
        // Burst mode - swap buffers
        uint8_t next_buffer = (g_state.active_buffer + 1) % DMA_ACQ_CIRCULAR_BUFFERS;
        
        g_state.dma_buffers[g_state.active_buffer].ready = true;
        g_state.active_buffer = next_buffer;
        g_state.dma_buffers[next_buffer].ready = false;
        
        // Update sample count
        g_state.status.samples_acquired += 
            g_state.dma_buffers[g_state.active_buffer].size / get_bytes_per_sample();
        
        // Check if acquisition complete
        if (g_state.status.samples_acquired >= g_state.status.samples_expected) {
            g_state.status.state = DMA_ACQ_STATE_TRANSFER;
            g_state.status.completion_timestamp_us = esp_timer_get_time();
            
            if (g_state.completion_sem) {
                xSemaphoreGiveFromISR(g_state.completion_sem, &high_task_wakeup);
            }
        }
    }
    
    if (high_task_wakeup == pdTRUE) {
        portYIELD_FROM_ISR();
    }
}

// ============================================================================
// GPIO TRIGGER ISR
// ============================================================================

void IRAM_ATTR dma_acq_trigger_isr(void *arg) {
    BaseType_t high_task_wakeup = pdFALSE;
    
    if (g_state.status.state == DMA_ACQ_STATE_ARMED) {
        g_state.status.trigger_timestamp_us = esp_timer_get_time();
        g_state.status.trigger_count++;
        
        // Start ADC conversion
        if (!g_state.use_psram) {
            // Burst mode: single acquisition
            adc_continuous_start(g_state.adc_handle);
            g_state.status.state = DMA_ACQ_STATE_ACQUIRING;
        }
        
        g_state.start_time_us = esp_timer_get_time();
    }
    
    if (high_task_wakeup == pdTRUE) {
        portYIELD_FROM_ISR();
    }
}

// ============================================================================
// INITIALIZATION
// ============================================================================

esp_err_t dma_acq_init(const dma_acq_config_t *config) {
    if (g_state.initialized) {
        ESP_LOGW(TAG, "Already initialized");
        return ESP_ERR_INVALID_STATE;
    }
    
    if (config == NULL) {
        return ESP_ERR_INVALID_ARG;
    }
    
    // Validate configuration
    if (config->num_channels == 0 || config->num_channels > DMA_ACQ_MAX_CHANNELS) {
        ESP_LOGE(TAG, "Invalid channel count: %lu", config->num_channels);
        return ESP_ERR_INVALID_ARG;
    }
    
    if (config->samples_per_channel < DMA_ACQ_BUFFER_SIZE_MIN ||
        config->samples_per_channel > DMA_ACQ_BUFFER_SIZE_MAX) {
        ESP_LOGE(TAG, "Invalid sample count: %lu", config->samples_per_channel);
        return ESP_ERR_INVALID_ARG;
    }
    
    // Copy configuration
    memcpy(&g_state.config, config, sizeof(dma_acq_config_t));
    
    ESP_LOGI(TAG, "Initializing DMA acquisition:");
    ESP_LOGI(TAG, "  Channels: %lu", config->num_channels);
    ESP_LOGI(TAG, "  Samples/channel: %lu", config->samples_per_channel);
    ESP_LOGI(TAG, "  Trigger: %s", 
             config->trigger == DMA_ACQ_TRIG_EXT ? "External" :
             config->trigger == DMA_ACQ_TRIG_SOFT ? "Software" : "Timer");
    
    // Allocate synchronization primitives
    g_state.mutex = xSemaphoreCreateMutex();
    g_state.completion_sem = xSemaphoreCreateBinary();
    
    if (!g_state.mutex || !g_state.completion_sem) {
        ESP_LOGE(TAG, "Failed to create semaphores");
        return ESP_ERR_NO_MEM;
    }
    
    // Determine mode
    g_state.use_psram = (config->trigger == DMA_ACQ_TRIG_TIMER) || 
                        (config->samples_per_channel > 8192);
    
    if (g_state.use_psram) {
        ESP_LOGI(TAG, "Using PSRAM continuous mode");
        
        // Initialize PSRAM
        if (!esp_psram_is_initialized()) {
            esp_err_t ret = esp_psram_init();
            if (ret != ESP_OK) {
                ESP_LOGE(TAG, "Failed to init PSRAM: %s", esp_err_to_name(ret));
                return ret;
            }
        }
        
        // Allocate PSRAM buffer
        g_state.psram_buffer = heap_caps_malloc(DMA_ACQ_PSRAM_BUFFER_SIZE, 
                                                MALLOC_CAP_SPIRAM);
        if (!g_state.psram_buffer) {
            ESP_LOGE(TAG, "Failed to allocate PSRAM buffer");
            return ESP_ERR_NO_MEM;
        }
        
        g_state.psram_write_offset = 0;
        g_state.psram_overflow_count = 0;
        ESP_LOGI(TAG, "PSRAM buffer: %d MB", DMA_ACQ_PSRAM_BUFFER_SIZE / (1024 * 1024));
    }
    
    // Allocate DMA buffers in SRAM
    uint32_t dma_buf_size = calculate_dma_buffer_size(config->samples_per_channel);
    
    g_state.dma_buffer_a = heap_caps_malloc(dma_buf_size, MALLOC_CAP_DMA);
    g_state.dma_buffer_b = heap_caps_malloc(dma_buf_size, MALLOC_CAP_DMA);
    
    if (!g_state.dma_buffer_a || !g_state.dma_buffer_b) {
        ESP_LOGE(TAG, "Failed to allocate DMA buffers");
        return ESP_ERR_NO_MEM;
    }
    
    // Initialize buffer structures
    g_state.dma_buffers[0].data = g_state.dma_buffer_a;
    g_state.dma_buffers[0].size = dma_buf_size;
    g_state.dma_buffers[0].ready = false;
    g_state.dma_buffers[0].bytes_written = 0;
    
    g_state.dma_buffers[1].data = g_state.dma_buffer_b;
    g_state.dma_buffers[1].size = dma_buf_size;
    g_state.dma_buffers[1].ready = false;
    g_state.dma_buffers[1].bytes_written = 0;
    
    g_state.active_buffer = 0;
    
    // Configure ADC
    adc_continuous_handle_cfg_t adc_config = {
        .max_store_buf_size = dma_buf_size * 2,
        .conv_frame_size = dma_buf_size,
    };
    
    esp_err_t ret = adc_continuous_new_handle(&adc_config, &g_state.adc_handle);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to create ADC handle: %s", esp_err_to_name(ret));
        return ret;
    }
    
    // Configure ADC channels
    adc_continuous_config_t dig_cfg = {
        .sample_freq_hz = config->sample_rate,
        .conv_mode = ADC_CONV_SINGLE_UNIT_1,
        .format = ADC_DIGI_OUTPUT_FORMAT_TYPE2,
    };
    
    adc_digi_pattern_config_t adc_pattern[DMA_ACQ_MAX_CHANNELS] = {0};
    
    for (uint32_t i = 0; i < config->num_channels; i++) {
        adc_pattern[i].atten = DMA_ACQ_ADC_ATTEN;
        adc_pattern[i].channel = config->channel_map[i];
        adc_pattern[i].unit = ADC_UNIT_1;
        adc_pattern[i].bit_width = DMA_ACQ_ADC_BIT_WIDTH;
    }
    
    dig_cfg.pattern_num = config->num_channels;
    dig_cfg.adc_pattern = adc_pattern;
    
    ret = adc_continuous_config(g_state.adc_handle, &dig_cfg);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to config ADC: %s", esp_err_to_name(ret));
        return ret;
    }
    
    // Configure trigger
    if (config->trigger == DMA_ACQ_TRIG_EXT) {
        gpio_config_t io_conf = {
            .pin_bit_mask = (1ULL << config->trigger_gpio),
            .mode = GPIO_MODE_INPUT,
            .pull_up_en = GPIO_PULLUP_DISABLE,
            .pull_down_en = GPIO_PULLDOWN_ENABLE,
            .intr_type = config->trigger_edge == 0 ? GPIO_INTR_POSEDGE :
                         config->trigger_edge == 1 ? GPIO_INTR_NEGEDGE : GPIO_INTR_ANYEDGE
        };
        gpio_config(&io_conf);
        
        gpio_install_isr_service(0);
        gpio_isr_handler_add(config->trigger_gpio, dma_acq_trigger_isr, NULL);
        
        ESP_LOGI(TAG, "External trigger on GPIO %d", config->trigger_gpio);
    }
    
    // Reset status
    memset(&g_state.status, 0, sizeof(dma_acq_status_t));
    g_state.status.samples_expected = config->samples_per_channel * config->num_channels;
    
    g_state.initialized = true;
    ESP_LOGI(TAG, "Initialization complete");
    
    return ESP_OK;
}

void dma_acq_deinit(void) {
    if (!g_state.initialized) {
        return;
    }
    
    dma_acq_stop();
    
    if (g_state.adc_handle) {
        adc_continuous_deinit(g_state.adc_handle);
        g_state.adc_handle = NULL;
    }
    
    if (g_state.dma_buffer_a) {
        free(g_state.dma_buffer_a);
        g_state.dma_buffer_a = NULL;
    }
    
    if (g_state.dma_buffer_b) {
        free(g_state.dma_buffer_b);
        g_state.dma_buffer_b = NULL;
    }
    
    if (g_state.psram_buffer) {
        free(g_state.psram_buffer);
        g_state.psram_buffer = NULL;
    }
    
    if (g_state.mutex) {
        vSemaphoreDelete(g_state.mutex);
        g_state.mutex = NULL;
    }
    
    if (g_state.completion_sem) {
        vSemaphoreDelete(g_state.completion_sem);
        g_state.completion_sem = NULL;
    }
    
    g_state.initialized = false;
    ESP_LOGI(TAG, "Deinitialized");
}

// ============================================================================
// CONTROL FUNCTIONS
// ============================================================================

esp_err_t dma_acq_start_burst(void) {
    if (!g_state.initialized) {
        return ESP_ERR_INVALID_STATE;
    }
    
    xSemaphoreTake(g_state.mutex, portMAX_DELAY);
    
    // Reset buffers
    g_state.active_buffer = 0;
    g_state.dma_buffers[0].ready = false;
    g_state.dma_buffers[1].ready = false;
    g_state.status.samples_acquired = 0;
    
    if (g_state.config.trigger == DMA_ACQ_TRIG_SOFT) {
        // Start immediately for software trigger
        g_state.status.state = DMA_ACQ_STATE_ACQUIRING;
        g_state.start_time_us = esp_timer_get_time();
        
        esp_err_t ret = adc_continuous_start(g_state.adc_handle);
        if (ret != ESP_OK) {
            xSemaphoreGive(g_state.mutex);
            return ret;
        }
    } else {
        // Arm for external trigger
        g_state.status.state = DMA_ACQ_STATE_ARMED;
        ESP_LOGI(TAG, "Armed for external trigger");
    }
    
    xSemaphoreGive(g_state.mutex);
    return ESP_OK;
}

esp_err_t dma_acq_start_continuous(void) {
    if (!g_state.initialized || !g_state.use_psram) {
        return ESP_ERR_INVALID_STATE;
    }
    
    xSemaphoreTake(g_state.mutex, portMAX_DELAY);
    
    g_state.psram_write_offset = 0;
    g_state.psram_overflow_count = 0;
    g_state.status.samples_acquired = 0;
    g_state.status.state = DMA_ACQ_STATE_ACQUIRING;
    g_state.start_time_us = esp_timer_get_time();
    
    esp_err_t ret = adc_continuous_start(g_state.adc_handle);
    
    xSemaphoreGive(g_state.mutex);
    
    if (ret == ESP_OK) {
        ESP_LOGI(TAG, "Continuous acquisition started");
    }
    
    return ret;
}

void dma_acq_stop(void) {
    if (!g_state.initialized) {
        return;
    }
    
    adc_continuous_stop(g_state.adc_handle);
    g_state.status.state = DMA_ACQ_STATE_IDLE;
    
    ESP_LOGI(TAG, "Acquisition stopped");
}

esp_err_t dma_acq_trigger_software(void) {
    if (!g_state.initialized || g_state.config.trigger != DMA_ACQ_TRIG_SOFT) {
        return ESP_ERR_INVALID_STATE;
    }
    
    if (g_state.status.state != DMA_ACQ_STATE_ACQUIRING) {
        return ESP_ERR_INVALID_STATE;
    }
    
    g_state.status.trigger_timestamp_us = esp_timer_get_time();
    g_state.status.trigger_count++;
    
    return ESP_OK;
}

// ============================================================================
// STATUS & DATA RETRIEVAL
// ============================================================================

esp_err_t dma_acq_get_status(dma_acq_status_t *status) {
    if (!status) {
        return ESP_ERR_INVALID_ARG;
    }
    
    xSemaphoreTake(g_state.mutex, portMAX_DELAY);
    memcpy(status, &g_state.status, sizeof(dma_acq_status_t));
    xSemaphoreGive(g_state.mutex);
    
    return ESP_OK;
}

esp_err_t dma_acq_read_data(uint8_t *buffer, uint32_t max_size, uint32_t *bytes_read) {
    if (!buffer || !bytes_read || !g_state.initialized) {
        return ESP_ERR_INVALID_ARG;
    }
    
    *bytes_read = 0;
    
    // Read from both DMA buffers
    uint32_t total_samples = g_state.config.samples_per_channel * g_state.config.num_channels;
    uint32_t total_bytes = total_samples * sizeof(uint16_t);
    
    if (max_size < total_bytes) {
        ESP_LOGW(TAG, "Buffer too small, need %lu bytes", total_bytes);
        return ESP_ERR_INVALID_SIZE;
    }
    
    // In burst mode, read directly from ADC
    if (g_state.status.state == DMA_ACQ_STATE_TRANSFER ||
        g_state.status.state == DMA_ACQ_STATE_IDLE) {
        
        uint32_t result_len = 0;
        esp_err_t ret = adc_continuous_read(g_state.adc_handle, buffer, max_size, &result_len, 100);
        
        if (ret == ESP_OK) {
            *bytes_read = result_len;
        }
        
        return ret;
    }
    
    return ESP_ERR_INVALID_STATE;
}

esp_err_t dma_acq_read_psram(uint32_t offset, uint8_t *buffer, uint32_t size) {
    if (!g_state.initialized || !g_state.use_psram || !g_state.psram_buffer) {
        return ESP_ERR_INVALID_STATE;
    }
    
    if (offset + size > DMA_ACQ_PSRAM_BUFFER_SIZE) {
        return ESP_ERR_INVALID_SIZE;
    }
    
    memcpy(buffer, g_state.psram_buffer + offset, size);
    return ESP_OK;
}

void dma_acq_get_psram_info(uint32_t *total_size, uint32_t *write_offset, uint32_t *overflow_count) {
    if (total_size) *total_size = DMA_ACQ_PSRAM_BUFFER_SIZE;
    
    xSemaphoreTake(g_state.mutex, portMAX_DELAY);
    if (write_offset) *write_offset = g_state.psram_write_offset;
    if (overflow_count) *overflow_count = g_state.psram_overflow_count;
    xSemaphoreGive(g_state.mutex);
}

float dma_acq_get_actual_sample_rate(void) {
    if (g_state.status.samples_acquired == 0) {
        return 0.0f;
    }
    
    uint64_t elapsed_us = g_state.status.completion_timestamp_us - g_state.start_time_us;
    if (elapsed_us == 0) {
        return 0.0f;
    }
    
    return (float)(g_state.status.samples_acquired * 1000000ULL) / (float)elapsed_us;
}

esp_err_t dma_acq_verify_ramp(uint16_t expected_pattern, uint32_t *error_count) {
    if (!error_count) {
        return ESP_ERR_INVALID_ARG;
    }
    
    *error_count = 0;
    
    // Read back data
    uint8_t *verify_buf = malloc(g_state.dma_buffers[0].size);
    if (!verify_buf) {
        return ESP_ERR_NO_MEM;
    }
    
    uint32_t bytes_read = 0;
    esp_err_t ret = dma_acq_read_data(verify_buf, g_state.dma_buffers[0].size, &bytes_read);
    
    if (ret != ESP_OK) {
        free(verify_buf);
        return ret;
    }
    
    // Check continuity (assuming ramp pattern)
    uint16_t *samples = (uint16_t *)verify_buf;
    uint32_t num_samples = bytes_read / sizeof(uint16_t);
    
    for (uint32_t i = 1; i < num_samples; i++) {
        int16_t diff = (int16_t)(samples[i] - samples[i-1]);
        if (diff != 1 && diff != -4095) {  // Allow wrap around
            (*error_count)++;
        }
    }
    
    free(verify_buf);
    
    if (*error_count == 0) {
        ESP_LOGI(TAG, "Ramp verification passed: %lu samples", num_samples);
    } else {
        ESP_LOGW(TAG, "Ramp verification failed: %lu errors", *error_count);
    }
    
    return ESP_OK;
}
