# Array Control Firmware - CMake Build Configuration

cmake_minimum_required(VERSION 3.5)

# Set target board
set(IDF_TARGET esp32s3)

# Include project
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(array_control_firmware)

# ============================================================================
# SOURCE FILES
# ============================================================================

set(COMPONENT_SRCS
    # Core array control
    array_control.c
    array_commands.cpp
    
    # DMA acquisition (NEW - add these)
    dma_acquisition.c
    array_dma_integration.c
    
    # Main entry point
    main.cpp
)

set(COMPONENT_ADD_INCLUDEDIRS
    .
    include
)

# ============================================================================
# COMPONENT CONFIGURATION
# ============================================================================

idf_component_register(
    SRCS ${COMPONENT_SRCS}
    INCLUDE_DIRS ${COMPONENT_ADD_INCLUDEDIRS}
    REQUIRES 
        driver
        esp_adc
        esp_timer
        freertos
        json        # For cJSON command interface
        esp_psram   # For PSRAM support
)

# ============================================================================
# COMPILER FLAGS
# ============================================================================

# Enable optimizations for DMA performance
target_compile_options(${COMPONENT_LIB} PRIVATE
    -O2
    -Wall
    -Wextra
    -DCONFIG_DMA_ACQUISITION_ENABLED=1
)

# ============================================================================
# LINKER OPTIONS
# ============================================================================

target_link_libraries(${COMPONENT_LIB} PRIVATE
    -lm  # Math library
)
