/**
 * @file array_dma_integration.h
 * @brief DMA integration with array control command interface
 */

#ifndef ARRAY_DMA_INTEGRATION_H
#define ARRAY_DMA_INTEGRATION_H

#include "cJSON.h"

#ifdef __cplusplus
extern "C" {
#endif

// Command handlers - return allocated JSON string (caller must free)
char* cmd_dma_init(const cJSON *params);
char* cmd_dma_start_burst(const cJSON *params);
char* cmd_dma_start_continuous(const cJSON *params);
char* cmd_dma_stop(const cJSON *params);
char* cmd_dma_get_status(const cJSON *params);
char* cmd_dma_read_data(const cJSON *params);
char* cmd_dma_trigger(const cJSON *params);
char* cmd_dma_psram_info(const cJSON *params);
char* cmd_dma_verify_ramp(const cJSON *params);

// Integration setup
void array_dma_integration_init(void);

// Default configuration (can be modified before init)
extern dma_acq_config_t g_default_dma_config;

#ifdef __cplusplus
}
#endif

#endif // ARRAY_DMA_INTEGRATION_H
