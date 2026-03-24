/**
 * @file array_control.c
 * @brief Array control firmware implementation
 * @details ESP32-S3 based multi-element array controller with beamforming
 */

#include "array_control.h"
#include <string.h>
#include <math.h>
#include <driver/gpio.h>
#include <driver/gptimer.h>
#include <driver/adc.h>
#include <driver/dac.h>
#include <esp_timer.h>
#include <esp_log.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <freertos/semphr.h>
#include <freertos/queue.h>

static const char *TAG = "ARRAY_CTRL";

// ============================================================================
// STATIC STATE
// ============================================================================

static ArrayState g_state = {0};
static ArrayGeometry g_geometry = {0};
static BeamformingParams g_beamParams = {0};
static DelayEntry g_delayLUT[ARRAY_MAX_ELEMENTS] = {0};
static ArrayAcquisitionConfig g_acqConfig = {0};

// DMA double buffers
static uint8_t g_dmaBufferA[ARRAY_DMA_BUFFER_SIZE] __attribute__((aligned(4)));
static uint8_t g_dmaBufferB[ARRAY_DMA_BUFFER_SIZE] __attribute__((aligned(4)));
static DmaBuffer g_dmaBuffers[2] = {
    {g_dmaBufferA, ARRAY_DMA_BUFFER_SIZE, false, 0},
    {g_dmaBufferB, ARRAY_DMA_BUFFER_SIZE, false, 0}
};
static volatile uint8_t g_dmaActiveBuffer = 0;
static volatile bool g_dmaTransferComplete = false;

// Synchronization
static SemaphoreHandle_t g_acqSemaphore = NULL;
static SemaphoreHandle_t g_dmaMutex = NULL;
static TaskHandle_t g_acqTaskHandle = NULL;

// Hardware handles
gptimer_handle_t g_firingTimer = NULL;
static spi_device_handle_t g_spiHandle = NULL;
static intr_handle_t g_dmaIntrHandle = NULL;

// ============================================================================
// SHIFT REGISTER CONTROL
// ============================================================================

/**
 * @brief Initialize shift register GPIO pins
 */
static void shiftreg_init_gpio(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << ARRAY_PIN_DATA) | 
                       (1ULL << ARRAY_PIN_CLOCK) | 
                       (1ULL << ARRAY_PIN_LATCH) |
                       (1ULL << ARRAY_PIN_HV_ENABLE),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    ESP_ERROR_CHECK(gpio_config(&io_conf));
    
    // Initialize to safe state
    gpio_set_level(ARRAY_PIN_DATA, 0);
    gpio_set_level(ARRAY_PIN_CLOCK, 0);
    gpio_set_level(ARRAY_PIN_LATCH, 0);
    gpio_set_level(ARRAY_PIN_HV_ENABLE, 0);
}

/**
 * @brief Shift out data to 74HC595 chain
 * @param data Bit pattern, LSB = element 0
 * @param numBits Number of bits to shift (typically numElements)
 */
static void IRAM_ATTR shiftreg_write(uint32_t data, uint8_t numBits) {
    // Shift out bits (MSB first for natural element ordering)
    for (int i = numBits - 1; i >= 0; i--) {
        gpio_set_level(ARRAY_PIN_DATA, (data >> i) & 0x01);
        
        // Clock pulse (min 20ns @ 3.3V, but we use safe timing)
        gpio_set_level(ARRAY_PIN_CLOCK, 1);
        esp_rom_delay_us(1);  // 1us is plenty
        gpio_set_level(ARRAY_PIN_CLOCK, 0);
        esp_rom_delay_us(1);
    }
    
    // Latch the outputs
    gpio_set_level(ARRAY_PIN_LATCH, 1);
    esp_rom_delay_us(1);
    gpio_set_level(ARRAY_PIN_LATCH, 0);
}

// ============================================================================
// SPI INITIALIZATION (for HV pulser chips)
// ============================================================================

/**
 * @brief Initialize SPI bus for MD1210/TC6320 control
 */
static bool spi_init(void) {
    spi_bus_config_t buscfg = {
        .mosi_io_num = ARRAY_PIN_SPI_MOSI,
        .miso_io_num = -1,  // Not used
        .sclk_io_num = ARRAY_PIN_SPI_SCK,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1,
        .max_transfer_sz = 32
    };
    
    esp_err_t ret = spi_bus_initialize(ARRAY_SPI_HOST, &buscfg, SPI_DMA_CH_AUTO);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "SPI bus init failed: %d", ret);
        return false;
    }
    
    spi_device_interface_config_t devcfg = {
        .clock_speed_hz = 10 * 1000 * 1000,  // 10 MHz
        .mode = 0,  // CPOL=0, CPHA=0
        .spics_io_num = ARRAY_PIN_SPI_CS0,
        .queue_size = 1,
        .pre_cb = NULL,
        .post_cb = NULL
    };
    
    ret = spi_bus_add_device(ARRAY_SPI_HOST, &devcfg, &g_spiHandle);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "SPI device add failed: %d", ret);
        return false;
    }
    
    return true;
}

// ============================================================================
// TIMER ISR FOR FIRING SEQUENCES
// ============================================================================

/**
 * @brief Timer callback for precision firing timing
 */
static bool IRAM_ATTR firing_timer_callback(gptimer_handle_t timer, 
                                             const gptimer_alarm_event_data_t *edata,
                                             void *user_ctx) {
    // This runs in ISR context - keep it minimal
    // Signal acquisition task to fire next element group
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    if (g_acqTaskHandle != NULL) {
        vTaskNotifyGiveFromISR(g_acqTaskHandle, &xHigherPriorityTaskWoken);
    }
    return xHigherPriorityTaskWoken == pdTRUE;
}

/**
 * @brief Initialize firing timer (1us resolution)
 */
static bool firing_timer_init(void) {
    gptimer_config_t timer_config = {
        .clk_src = GPTIMER_CLK_SRC_DEFAULT,
        .direction = GPTIMER_COUNT_UP,
        .resolution_hz = 1000000,  // 1 MHz = 1us resolution
    };
    
    esp_err_t ret = gptimer_new_timer(&timer_config, &g_firingTimer);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Timer creation failed: %d", ret);
        return false;
    }
    
    gptimer_alarm_config_t alarm_config = {
        .reload_count = 0,
        .alarm_count = 100,  // Default 100us
        .flags.auto_reload_on_alarm = true
    };
    gptimer_set_alarm_action(g_firingTimer, &alarm_config);
    
    gptimer_event_callbacks_t cbs = {
        .on_alarm = firing_timer_callback
    };
    gptimer_register_event_callbacks(g_firingTimer, &cbs, NULL);
    
    return true;
}

// ============================================================================
// ADC DMA CONFIGURATION
// ============================================================================

/**
 * @brief Initialize ADC for continuous DMA sampling
 * Uses ADC1 on ESP32-S3 for high-speed sampling
 */
static bool adc_dma_init(void) {
    // Configure ADC
    adc_continuous_handle_cfg_t adc_config = {
        .max_store_buf_size = ARRAY_DMA_BUFFER_SIZE * 2,  // Double buffer
        .conv_frame_size = ARRAY_DMA_BUFFER_SIZE / 2      // Half buffer interrupt
    };
    
    adc_continuous_handle_t handle;
    esp_err_t ret = adc_continuous_new_handle(&adc_config, &handle);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "ADC handle creation failed: %d", ret);
        return false;
    }
    
    // Configure ADC pattern (scan multiple channels for multi-element)
    adc_digi_pattern_config_t adc_pattern[ARRAY_MAX_ELEMENTS] = {0};
    uint8_t numChannels = g_geometry.numElements > 8 ? 8 : g_geometry.numElements;
    
    for (int i = 0; i < numChannels; i++) {
        adc_pattern[i].atten = ADC_ATTEN_DB_12;      // 0-3.3V range
        adc_pattern[i].channel = i;                   // ADC1_CH0 through CH7
        adc_pattern[i].unit = ADC_UNIT_1;
        adc_pattern[i].bit_width = SOC_ADC_DIGI_MAX_BITWIDTH;
    }
    
    adc_continuous_config_t dig_cfg = {
        .sample_freq_hz = ARRAY_ADC_SAMPLE_RATE,
        .conv_mode = ADC_CONV_SINGLE_UNIT_1,
        .format = ADC_DIGI_OUTPUT_FORMAT_TYPE2,
        .pattern_num = numChannels,
        .adc_pattern = adc_pattern
    };
    
    ret = adc_continuous_config(handle, &dig_cfg);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "ADC config failed: %d", ret);
        return false;
    }
    
    // Note: ESP-IDF ADC continuous mode handles DMA internally
    // We would register a callback for buffer ready events
    
    return true;
}

// ============================================================================
// BEAMFORMING CALCULATIONS
// ============================================================================

/**
 * @brief Compute time-of-flight delays for all elements
 * @param params Beamforming parameters
 * @param delayLUT Output delay lookup table
 * @return true if successful
 */
bool array_compute_delays(const BeamformingParams *params, DelayEntry *delayLUT) {
    if (!g_state.initialized || delayLUT == NULL) {
        return false;
    }
    
    // Convert steering angle to radians
    float theta = params->steeringAngle * M_PI / 180.0f;
    float cos_theta = cosf(theta);
    float sin_theta = sinf(theta);
    
    // Calculate element positions (centered at 0)
    float totalWidth = (g_geometry.numElements - 1) * g_geometry.elementPitch;
    float xStart = -totalWidth / 2.0f;
    
    // Find maximum delay for normalization
    float maxDelay = 0;
    float delays[ARRAY_MAX_ELEMENTS];
    
    for (int i = 0; i < g_geometry.numElements; i++) {
        float x = xStart + i * g_geometry.elementPitch;
        
        if (params->focusDepth > 0) {
            // Focused beam: spherical delay profile
            // Path length from element to focal point
            float xf = x - params->focusDepth * sin_theta;
            float zf = params->focusDepth * cos_theta;
            float pathLength = sqrtf(xf * xf + zf * zf);
            
            // Time of flight
            delays[i] = (pathLength / 1000.0f) / g_geometry.soundSpeed * 1e6f; // us
        } else {
            // Plane wave: linear delay for steering
            delays[i] = (x * sin_theta / 1000.0f) / g_geometry.soundSpeed * 1e6f; // us
        }
        
        if (delays[i] > maxDelay) {
            maxDelay = delays[i];
        }
    }
    
    // Normalize delays (make all positive relative to earliest arrival)
    // and convert to sample periods
    for (int i = 0; i < g_geometry.numElements; i++) {
        float normalizedDelay = maxDelay - delays[i];  // Compensate for longer paths
        
        // Convert to samples
        float samples = normalizedDelay * ARRAY_ADC_SAMPLE_RATE / 1e6f;
        delayLUT[i].sampleDelay = (uint16_t)samples;
        delayLUT[i].fractionalDelay = samples - delayLUT[i].sampleDelay;
    }
    
    // Store for later use
    memcpy(g_delayLUT, delayLUT, sizeof(DelayEntry) * g_geometry.numElements);
    memcpy(&g_beamParams, params, sizeof(BeamformingParams));
    
    return true;
}

/**
 * @brief Set focus depth and steering angle
 */
bool array_set_focus(float depthMm, float angleDeg) {
    BeamformingParams params = {
        .focusDepth = depthMm,
        .steeringAngle = angleDeg,
        .fNumber = 2.0f,
        .dynamicFocus = true
    };
    
    return array_compute_delays(&params, g_delayLUT);
}

/**
 * @brief Calculate F-number for given geometry and depth
 */
float array_get_fnumber(const ArrayGeometry *geom, float depthMm) {
    float aperture = (geom->numElements - 1) * geom->elementPitch;
    return depthMm / aperture;
}

// ============================================================================
// PUBLIC API IMPLEMENTATION
// ============================================================================

bool array_init(void) {
    if (g_state.initialized) {
        return true;
    }
    
    ESP_LOGI(TAG, "Initializing array control...");
    
    // Initialize synchronization primitives
    g_acqSemaphore = xSemaphoreCreateBinary();
    g_dmaMutex = xSemaphoreCreateMutex();
    
    if (g_acqSemaphore == NULL || g_dmaMutex == NULL) {
        ESP_LOGE(TAG, "Failed to create semaphores");
        return false;
    }
    
    // Initialize hardware
    shiftreg_init_gpio();
    
    if (!spi_init()) {
        ESP_LOGE(TAG, "SPI init failed");
        return false;
    }
    
    if (!firing_timer_init()) {
        ESP_LOGE(TAG, "Timer init failed");
        return false;
    }
    
    // Set default geometry
    g_geometry.numElements = ARRAY_DEFAULT_ELEMENTS;
    g_geometry.elementPitch = 0.5f;  // 0.5mm (lambda/2 at 1.5MHz in tissue)
    g_geometry.elementWidth = 0.4f;
    g_geometry.centerFrequency = 1.5f;
    g_geometry.soundSpeed = 1540.0f;
    g_geometry.aperture = (ARRAY_DEFAULT_ELEMENTS - 1) * 0.5f;
    
    // Initialize ADC DMA
    if (!adc_dma_init()) {
        ESP_LOGW(TAG, "ADC DMA init failed - will retry on acquisition");
    }
    
    g_state.initialized = true;
    g_state.acquiring = false;
    
    ESP_LOGI(TAG, "Array control initialized: %d elements", g_geometry.numElements);
    return true;
}

bool array_deinit(void) {
    if (!g_state.initialized) {
        return true;
    }
    
    array_stop_acquisition();
    
    if (g_firingTimer) {
        gptimer_stop(g_firingTimer);
        gptimer_del_timer(g_firingTimer);
        g_firingTimer = NULL;
    }
    
    if (g_spiHandle) {
        spi_bus_remove_device(g_spiHandle);
        spi_bus_free(ARRAY_SPI_HOST);
        g_spiHandle = NULL;
    }
    
    if (g_acqSemaphore) {
        vSemaphoreDelete(g_acqSemaphore);
        g_acqSemaphore = NULL;
    }
    
    if (g_dmaMutex) {
        vSemaphoreDelete(g_dmaMutex);
        g_dmaMutex = NULL;
    }
    
    g_state.initialized = false;
    return true;
}

bool array_configure_geometry(const ArrayGeometry *geom) {
    if (!g_state.initialized || geom == NULL) {
        return false;
    }
    
    if (geom->numElements > ARRAY_MAX_ELEMENTS) {
        ESP_LOGE(TAG, "Too many elements: %d > %d", geom->numElements, ARRAY_MAX_ELEMENTS);
        return false;
    }
    
    memcpy(&g_geometry, geom, sizeof(ArrayGeometry));
    
    // Recalculate aperture
    g_geometry.aperture = (geom->numElements - 1) * geom->elementPitch;
    
    ESP_LOGI(TAG, "Geometry configured: %d elements, %.2f mm pitch", 
             g_geometry.numElements, g_geometry.elementPitch);
    
    return true;
}

bool array_set_element_pattern(uint32_t elementMask) {
    if (!g_state.initialized) {
        return false;
    }
    
    shiftreg_write(elementMask, g_geometry.numElements);
    return true;
}

bool array_fire_elements(uint32_t elementMask, uint16_t pulseWidthUs) {
    if (!g_state.initialized) {
        return false;
    }
    
    // Set element pattern
    shiftreg_write(elementMask, g_geometry.numElements);
    
    // Enable HV
    gpio_set_level(ARRAY_PIN_HV_ENABLE, 1);
    
    // Generate pulse (could use timer for precision, but delay for now)
    esp_rom_delay_us(pulseWidthUs);
    
    // Disable HV
    gpio_set_level(ARRAY_PIN_HV_ENABLE, 0);
    
    // Clear pattern
    shiftreg_write(0, g_geometry.numElements);
    
    g_state.sequenceCount++;
    return true;
}

bool array_clear_elements(void) {
    if (!g_state.initialized) {
        return false;
    }
    
    gpio_set_level(ARRAY_PIN_HV_ENABLE, 0);
    shiftreg_write(0, g_geometry.numElements);
    
    return true;
}

bool array_acquire_single(const ArrayAcquisitionConfig *config, 
                          uint8_t *buffer, size_t bufferSize) {
    if (!g_state.initialized || buffer == NULL) {
        return false;
    }
    
    // Store config
    memcpy(&g_acqConfig, config, sizeof(ArrayAcquisitionConfig));
    
    // Calculate required buffer size
    size_t requiredSize = config->geometry.numElements * config->samplesPerChannel * sizeof(uint16_t);
    if (bufferSize < requiredSize) {
        ESP_LOGE(TAG, "Buffer too small: %d < %d", bufferSize, requiredSize);
        return false;
    }
    
    // Configure delays if beamforming enabled
    if (config->beamform.focusDepth > 0 || config->beamform.steeringAngle != 0) {
        array_compute_delays(&config->beamform, g_delayLUT);
    }
    
    // Fire and acquire
    // This is simplified - real implementation would trigger DMA, wait for completion
    array_fire_elements(0xFF, 10);  // Fire all elements for 10us
    
    // Simulate acquisition delay
    esp_rom_delay_us(1000);
    
    g_state.acquisitionCount++;
    g_state.lastAcquisitionTime = esp_timer_get_time();
    
    return true;
}

bool array_start_acquisition(const ArrayAcquisitionConfig *config) {
    if (!g_state.initialized || g_state.acquiring) {
        return false;
    }
    
    memcpy(&g_acqConfig, config, sizeof(ArrayAcquisitionConfig));
    g_state.acquiring = true;
    
    // Start acquisition task or trigger DMA
    ESP_LOGI(TAG, "Acquisition started");
    
    return true;
}

bool array_stop_acquisition(void) {
    if (!g_state.acquiring) {
        return true;
    }
    
    g_state.acquiring = false;
    
    // Stop DMA
    // Stop timer
    if (g_firingTimer) {
        gptimer_stop(g_firingTimer);
    }
    
    // Clear elements
    array_clear_elements();
    
    ESP_LOGI(TAG, "Acquisition stopped");
    return true;
}

const ArrayState* array_get_state(void) {
    return &g_state;
}

void array_print_status(void) {
    ESP_LOGI(TAG, "=== Array Control Status ===");
    ESP_LOGI(TAG, "Initialized: %s", g_state.initialized ? "yes" : "no");
    ESP_LOGI(TAG, "Acquiring: %s", g_state.acquiring ? "yes" : "no");
    ESP_LOGI(TAG, "Elements: %d", g_geometry.numElements);
    ESP_LOGI(TAG, "Sequence count: %lu", g_state.sequenceCount);
    ESP_LOGI(TAG, "Acquisition count: %lu", g_state.acquisitionCount);
    ESP_LOGI(TAG, "DMA overflows: %lu", g_state.dmaOverflowCount);
    
    if (g_state.lastAcquisitionTime > 0) {
        ESP_LOGI(TAG, "Last acquisition: %lld us ago", 
                 esp_timer_get_time() - g_state.lastAcquisitionTime);
    }
}

float array_wavelength(const ArrayGeometry *geom) {
    return (geom->soundSpeed / 1000.0f) / geom->centerFrequency;  // mm
}

float array_near_field_distance(const ArrayGeometry *geom) {
    float a = geom->aperture;  // mm
    float lambda = array_wavelength(geom);  // mm
    return (a * a) / (4.0f * lambda);  // mm
}

bool array_check_grating_lobes(const ArrayGeometry *geom, float steeringAngle) {
    float lambda = array_wavelength(geom);
    float d = geom->elementPitch;
    float thetaMax = asinf(lambda / d - sinf(steeringAngle * M_PI / 180.0f)) * 180.0f / M_PI;
    
    // Grating lobe exists if |sin(theta_s) + lambda/d| <= 1
    float check = fabsf(sinf(steeringAngle * M_PI / 180.0f) + lambda / d);
    
    ESP_LOGI(TAG, "Grating lobe check: sin(theta) + lambda/d = %.3f", check);
    ESP_LOGI(TAG, "Max steering before grating lobe: %.1f deg", thetaMax);
    
    return check < 1.0f;
}

uint32_t array_get_max_throughput(void) {
    // Calculate theoretical max throughput
    // Elements × samples/channel × bytes/sample × acquisitions/sec
    float pri = g_acqConfig.priUs > 0 ? g_acqConfig.priUs : 1000;  // us
    float acquisitionsPerSec = 1e6f / pri;
    uint32_t bytesPerAcq = g_geometry.numElements * g_acqConfig.samplesPerChannel * 2;  // uint16
    
    return (uint32_t)(bytesPerAcq * acquisitionsPerSec);
}
