/**
 * @file dma_acquisition.h
 * @brief DMA acquisition with PSRAM buffering for ESP32-S3
 * @details High-speed multi-channel ADC acquisition using DMA to PSRAM
 */

#ifndef DMA_ACQUISITION_H
#define DMA_ACQUISITION_H

#include <stdint.h>
#include <stdbool.h>
#include "esp_err.h"

#ifdef __cplusplus
extern "C" {
#endif

// ============================================================================
// CONFIGURATION
// ============================================================================

#define DMA_ACQ_MAX_CHANNELS        8       // Maximum ADC channels
#define DMA_ACQ_BUFFER_SIZE_MIN     1024    // Minimum burst size
#define DMA_ACQ_BUFFER_SIZE_MAX     65536   // Maximum burst size
#define DMA_ACQ_PSRAM_BUFFER_SIZE   (4 * 1024 * 1024)  // 4MB PSRAM ring buffer
#define DMA_ACQ_CIRCULAR_BUFFERS    2       // Ping-pong buffers

// ADC configuration
#define DMA_ACQ_ADC_UNIT            ADC_UNIT_1
#define DMA_ACQ_ADC_ATTEN           ADC_ATTEN_DB_12
#define DMA_ACQ_ADC_BIT_WIDTH       ADC_BITWIDTH_12

// Default timing
#define DMA_ACQ_DEFAULT_SAMPLE_RATE 20000000  // 20 MSa/s (theoretical max)

// ============================================================================
// DATA STRUCTURES
// ============================================================================

typedef enum {
    DMA_ACQ_STATE_IDLE = 0,
    DMA_ACQ_STATE_ARMED,
    DMA_ACQ_STATE_ACQUIRING,
    DMA_ACQ_STATE_TRANSFER,
    DMA_ACQ_STATE_ERROR
} dma_acq_state_t;

typedef enum {
    DMA_ACQ_TRIG_EXT = 0,   // External GPIO trigger
    DMA_ACQ_TRIG_SOFT,      // Software trigger
    DMA_ACQ_TRIG_TIMER      // Periodic timer trigger
} dma_acq_trigger_t;

typedef struct {
    // Acquisition parameters
    uint32_t sample_rate;           // Target sample rate (Hz)
    uint32_t num_channels;          // Number of channels (1-8)
    uint32_t samples_per_channel;   // Samples per channel per burst
    dma_acq_trigger_t trigger;      // Trigger mode
    uint32_t pre_trigger_samples;   // Samples to keep before trigger
    
    // Channel mapping (ADC channel numbers)
    uint8_t channel_map[DMA_ACQ_MAX_CHANNELS];
    
    // Trigger configuration
    uint8_t trigger_gpio;           // GPIO pin for external trigger
    uint32_t trigger_edge;          // 0=rising, 1=falling, 2=both
} dma_acq_config_t;

typedef struct {
    // State
    volatile dma_acq_state_t state;
    volatile uint64_t acquisition_count;
    volatile uint32_t buffer_overflows;
    volatile uint32_t trigger_count;
    
    // Timing
    uint64_t trigger_timestamp_us;
    uint64_t completion_timestamp_us;
    
    // Data integrity
    uint32_t samples_acquired;
    uint32_t samples_expected;
    uint32_t continuity_errors;
} dma_acq_status_t;

typedef struct {
    uint8_t *data;
    uint32_t size;
    volatile bool ready;
    volatile uint32_t bytes_written;
} dma_buffer_t;

// ============================================================================
// API FUNCTIONS
// ============================================================================

/**
 * @brief Initialize DMA acquisition subsystem
 * @param config Acquisition configuration
 * @return ESP_OK on success
 */
esp_err_t dma_acq_init(const dma_acq_config_t *config);

/**
 * @brief Deinitialize DMA acquisition
 */
void dma_acq_deinit(void);

/**
 * @brief Start burst acquisition
 * Arms the system and waits for trigger
 * @return ESP_OK on success
 */
esp_err_t dma_acq_start_burst(void);

/**
 * @brief Start continuous PSRAM buffering mode
 * @return ESP_OK on success
 */
esp_err_t dma_acq_start_continuous(void);

/**
 * @brief Stop acquisition
 */
void dma_acq_stop(void);

/**
 * @brief Software trigger (when in SOFT trigger mode)
 */
esp_err_t dma_acq_trigger_software(void);

/**
 * @brief Get current status
 * @param status Output status structure
 * @return ESP_OK on success
 */
esp_err_t dma_acq_get_status(dma_acq_status_t *status);

/**
 * @brief Read acquired data from SRAM buffer (burst mode)
 * @param buffer Output buffer
 * @param max_size Maximum bytes to read
 * @param bytes_read Actual bytes read
 * @return ESP_OK on success
 */
esp_err_t dma_acq_read_data(uint8_t *buffer, uint32_t max_size, uint32_t *bytes_read);

/**
 * @brief Read data from PSRAM (continuous mode)
 * @param offset Byte offset in PSRAM
 * @param buffer Output buffer
 * @param size Bytes to read
 * @return ESP_OK on success
 */
esp_err_t dma_acq_read_psram(uint32_t offset, uint8_t *buffer, uint32_t size);

/**
 * @brief Get PSRAM buffer info
 * @param total_size Total PSRAM buffer size
 * @param write_offset Current write position
 * @param overflow_count Number of overflows
 */
void dma_acq_get_psram_info(uint32_t *total_size, uint32_t *write_offset, uint32_t *overflow_count);

/**
 * @brief Verify data integrity (ramp test)
 * @param expected_pattern Expected starting value
 * @param error_count Output: number of discontinuities
 * @return ESP_OK if no errors
 */
esp_err_t dma_acq_verify_ramp(uint16_t expected_pattern, uint32_t *error_count);

/**
 * @brief Calculate actual sample rate from timestamps
 * @return Sample rate in Hz (0 if not available)
 */
float dma_acq_get_actual_sample_rate(void);

/**
 * @brief DMA ISR handler (internal use)
 */
void IRAM_ATTR dma_acq_isr_handler(void *arg);

/**
 * @brief GPIO trigger ISR (internal use)
 */
void IRAM_ATTR dma_acq_trigger_isr(void *arg);

#ifdef __cplusplus
}
#endif

#endif // DMA_ACQUISITION_H
