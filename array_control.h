/**
 * @file array_control.h
 * @brief Array control firmware for ultrasound beamforming
 * @details Multi-element array sequencer with real-time beamforming delays
 * 
 * Hardware: ESP32-S3 with shift register expansion (74HC595)
 * Supports 8+ channels via 74HC595 cascaded shift registers
 * Compatible with MD1210/TC6320 HV pulser chips
 */

#ifndef ARRAY_CONTROL_H
#define ARRAY_CONTROL_H

#include <Arduino.h>
#include <driver/spi_master.h>
#include <driver/dma.h>
#include <soc/spi_struct.h>

#ifdef __cplusplus
extern "C" {
#endif

// ============================================================================
// CONFIGURATION
// ============================================================================

#define ARRAY_MAX_ELEMENTS          16      // Maximum array elements supported
#define ARRAY_DEFAULT_ELEMENTS      8       // Default element count
#define ARRAY_MAX_DELAYS            1024    // Max delay LUT entries
#define ARRAY_DMA_BUFFER_SIZE       4096    // DMA buffer in samples
#define ARRAY_ADC_SAMPLE_RATE       20000000 // 20 MSa/s
#define ARRAY_DAC_SAMPLE_RATE       100000  // 100 kHz waveform update

// Pin definitions (ESP32-S3)
#define ARRAY_PIN_DATA              GPIO_NUM_4   // Shift register DATA (DS)
#define ARRAY_PIN_CLOCK             GPIO_NUM_5   // Shift register CLOCK (SHCP)
#define ARRAY_PIN_LATCH             GPIO_NUM_6   // Shift register LATCH (STCP)
#define ARRAY_PIN_HV_ENABLE         GPIO_NUM_7   // Global HV enable
#define ARRAY_PIN_SYNC_OUT          GPIO_NUM_8   // Sync output for scope
#define ARRAY_PIN_ADC_TRIGGER       GPIO_NUM_9   // ADC conversion trigger

// SPI for HV pulser chips (MD1210/TC6320)
#define ARRAY_SPI_HOST              SPI2_HOST
#define ARRAY_PIN_SPI_MOSI          GPIO_NUM_11
#define ARRAY_PIN_SPI_SCK           GPIO_NUM_12
#define ARRAY_PIN_SPI_CS0           GPIO_NUM_13  // Chip select element 0-7
#define ARRAY_PIN_SPI_CS1           GPIO_NUM_14  // Chip select element 8-15

// DMA channels
#define ARRAY_DMA_CHAN_ADC          DMA_CHAN_0
#define ARRAY_DMA_CHAN_UART         DMA_CHAN_1

// ============================================================================
// DATA TYPES
// ============================================================================

/**
 * @brief Array geometry configuration
 */
typedef struct {
    uint8_t numElements;                    // Number of active elements
    float elementPitch;                     // Center-to-center spacing (mm)
    float elementWidth;                     // Element width (mm)
    float centerFrequency;                  // Transducer frequency (MHz)
    float soundSpeed;                       // m/s in medium
    float aperture;                         // Total array aperture (mm)
} ArrayGeometry;

/**
 * @brief Beamforming parameters
 */
typedef struct {
    float focusDepth;                       // Focal depth (mm), 0 = plane wave
    float steeringAngle;                    // Steering angle (degrees), 0 = straight
    float fNumber;                          // F-number for dynamic aperture
    bool dynamicFocus;                      // Enable dynamic focusing on receive
} BeamformingParams;

/**
 * @brief Delay lookup table entry
 */
typedef struct {
    uint16_t sampleDelay;                   // Delay in ADC sample periods
    float fractionalDelay;                  // Fractional delay for interpolation
} DelayEntry;

/**
 * @brief Firing sequence step
 */
typedef struct {
    uint32_t elementMask;                   // Bitmask of elements to fire
    uint16_t delayUs;                       // Delay before this step (microseconds)
    uint16_t pulseWidth;                    // Pulse width in 100ns units
    uint8_t amplitude;                      // Amplitude (0-255)
} FiringStep;

/**
 * @brief Array acquisition configuration
 */
typedef struct {
    ArrayGeometry geometry;
    BeamformingParams beamform;
    uint16_t priUs;                         // Pulse repetition interval (us)
    uint16_t samplesPerChannel;             // Samples to acquire per element
    uint8_t numAverages;                    // Number of ensemble averages
    bool enableApodization;                 // Apply apodization window
} ArrayAcquisitionConfig;

/**
 * @brief Array control state
 */
typedef struct {
    bool initialized;
    bool acquiring;
    uint32_t sequenceCount;
    uint32_t acquisitionCount;
    uint32_t dmaOverflowCount;
    int64_t lastAcquisitionTime;
} ArrayState;

/**
 * @brief DMA buffer descriptor
 */
typedef struct {
    uint8_t *buffer;
    size_t size;
    bool ready;
    uint32_t timestamp;
} DmaBuffer;

// ============================================================================
// FUNCTION PROTOTYPES
// ============================================================================

// Initialization
bool array_init(void);
bool array_deinit(void);
bool array_configure_geometry(const ArrayGeometry *geom);

// Element control
bool array_set_element_pattern(uint32_t elementMask);
bool array_fire_elements(uint32_t elementMask, uint16_t pulseWidthUs);
bool array_sequence_fire(const FiringStep *steps, uint8_t numSteps);
bool array_clear_elements(void);

// Beamforming
bool array_compute_delays(const BeamformingParams *params, DelayEntry *delayLUT);
bool array_set_focus(float depthMm, float angleDeg);
float array_get_fnumber(const ArrayGeometry *geom, float depthMm);

// Acquisition
bool array_start_acquisition(const ArrayAcquisitionConfig *config);
bool array_stop_acquisition(void);
bool array_wait_for_acquisition(uint32_t timeoutMs);
size_t array_get_data(uint8_t *buffer, size_t maxLen);
bool array_acquire_single(const ArrayAcquisitionConfig *config, uint8_t *buffer, size_t bufferSize);

// DMA management
bool array_dma_init(void);
void array_dma_start(void);
void array_dma_stop(void);
bool array_dma_get_buffer(DmaBuffer **buffer);
void array_dma_release_buffer(DmaBuffer *buffer);

// Real-time beamforming (simplified)
bool array_beamform_delay_and_sum(const uint8_t *rawData, float *beamformed, 
                                   const DelayEntry *delays, uint16_t numSamples);

// Calibration
bool array_calibrate_delays(void);
bool array_set_element_delay(uint8_t elementIdx, int16_t delayNs);

// Status and diagnostics
const ArrayState* array_get_state(void);
void array_print_status(void);
uint32_t array_get_max_throughput(void);

// Utility
float array_wavelength(const ArrayGeometry *geom);
float array_near_field_distance(const ArrayGeometry *geom);
bool array_check_grating_lobes(const ArrayGeometry *geom, float steeringAngle);

// ============================================================================
// INLINE UTILITIES
// ============================================================================

/**
 * @brief Calculate time-of-flight delay for an element
 * @param xElement Element position (mm, 0 = center)
 * @param focusDepth Focus depth (mm)
 * @param soundSpeed Sound speed (m/s)
 * @return Delay in microseconds
 */
static inline float array_calc_tof_delay(float xElement, float focusDepth, float soundSpeed) {
    float pathLength = sqrtf(focusDepth * focusDepth + xElement * xElement);
    return (pathLength / 1000.0f) / soundSpeed * 1e6f; // us
}

/**
 * @brief Convert microseconds to ADC sample periods
 */
static inline uint16_t array_us_to_samples(float delayUs, uint32_t sampleRate) {
    return (uint16_t)(delayUs * sampleRate / 1e6f);
}

#ifdef __cplusplus
}
#endif

#endif // ARRAY_CONTROL_H
