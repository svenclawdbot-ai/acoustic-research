# DMA Firmware Integration Guide

This guide shows how to integrate the DMA acquisition code into your existing array control firmware.

## Quick Start (Summary)

1. **Copy files** to your firmware directory
2. **Update CMakeLists.txt** to include new sources
3. **Update sdkconfig** to enable PSRAM
4. **Add command handlers** to your JSON router
5. **Wire the trigger** (see DMA_TRIGGER_WIRING.md)
6. **Build and flash**

---

## Step-by-Step Integration

### Step 1: File Placement

Copy these files to your firmware project directory:

```
your_firmware_project/
├── CMakeLists.txt              # Update this
├── sdkconfig.defaults          # Add PSRAM settings
├── main/
│   ├── CMakeLists.txt         # Or update top-level
│   ├── main.cpp               # Your existing main
│   ├── array_control.c        # Existing
│   ├── array_control.h        # Existing
│   ├── array_commands.cpp     # Existing - modify this
│   ├── array_commands.h       # Existing
│   │
│   ├── dma_acquisition.c      # <-- NEW (copy here)
│   ├── dma_acquisition.h      # <-- NEW (copy here)
│   ├── array_dma_integration.c # <-- NEW (copy here)
│   └── array_dma_integration.h # <-- NEW (copy here)
```

### Step 2: Update CMakeLists.txt

Add the new source files to your build:

```cmake
idf_component_register(
    SRCS 
        "main.cpp"
        "array_control.c"
        "array_commands.cpp"
        "dma_acquisition.c"           # <-- ADD
        "array_dma_integration.c"     # <-- ADD
    INCLUDE_DIRS 
        "."
    REQUIRES
        driver
        esp_adc
        esp_timer
        freertos
        json
        esp_psram                    # <-- ADD (for PSRAM support)
)
```

### Step 3: Enable PSRAM

Add to your `sdkconfig.defaults` or run `idf.py menuconfig`:

```
CONFIG_SPIRAM=y
CONFIG_SPIRAM_MODE_QUAD=y
CONFIG_SPIRAM_TYPE_AUTO=y
```

Or copy the provided defaults:
```bash
cp sdkconfig.defaults.dma sdkconfig.defaults
```

### Step 4: Integrate Command Router

Your existing `array_commands.cpp` likely has a command dispatcher. Add the DMA commands:

**Find your existing command handler (array_commands.cpp):**

```cpp
// Existing code - find this pattern
char* handle_command(const char* json_input) {
    cJSON *root = cJSON_Parse(json_input);
    cJSON *cmd = cJSON_GetObjectItem(root, "cmd");
    
    if (strcmp(cmd->valuestring, "ping") == 0) {
        return cmd_ping(root);
    } else if (strcmp(cmd->valuestring, "fire") == 0) {
        return cmd_fire(root);
    }
    // ... existing commands ...
    
    // ADD THESE NEW COMMANDS:
    else if (strcmp(cmd->valuestring, "dma_init") == 0) {
        return cmd_dma_init(root);
    } else if (strcmp(cmd->valuestring, "dma_start_burst") == 0) {
        return cmd_dma_start_burst(root);
    } else if (strcmp(cmd->valuestring, "dma_start_continuous") == 0) {
        return cmd_dma_start_continuous(root);
    } else if (strcmp(cmd->valuestring, "dma_stop") == 0) {
        return cmd_dma_stop(root);
    } else if (strcmp(cmd->valuestring, "dma_get_status") == 0) {
        return cmd_dma_get_status(root);
    } else if (strcmp(cmd->valuestring, "dma_read_data") == 0) {
        return cmd_dma_read_data(root);
    } else if (strcmp(cmd->valuestring, "dma_trigger") == 0) {
        return cmd_dma_trigger(root);
    } else if (strcmp(cmd->valuestring, "dma_psram_info") == 0) {
        return cmd_dma_psram_info(root);
    } else if (strcmp(cmd->valuestring, "dma_verify_ramp") == 0) {
        return cmd_dma_verify_ramp(root);
    }
    
    else {
        cJSON *response = cJSON_CreateObject();
        cJSON_AddStringToObject(response, "status", "error");
        cJSON_AddStringToObject(response, "error", "unknown_command");
        char *result = cJSON_PrintUnformatted(response);
        cJSON_Delete(response);
        return result;
    }
    
    cJSON_Delete(root);
}
```

**Include the DMA header at the top:**

```cpp
#include "array_dma_integration.h"
```

### Step 5: Connect Trigger to Array Firing

You need to generate the SYNC trigger when the array fires. Modify your existing fire function:

**In array_control.c, find your fire function:**

```cpp
// Add this helper function
static void generate_sync_pulse(void) {
    // Option 1: If using GPIO 8 for SYNC output
    gpio_set_level(ARRAY_PIN_SYNC_OUT, 1);
    esp_rom_delay_us(1);  // 1us pulse
    gpio_set_level(ARRAY_PIN_SYNC_OUT, 0);
    
    // Option 2: If using loopback (GPIO 8 -> GPIO 15)
    // The DMA trigger is already on GPIO 15, just pulse GPIO 8
    // (assuming jumper wire between 8 and 15)
}

// Modify your existing fire function
esp_err_t array_fire_focused(void) {
    // ... your existing fire code ...
    
    // ADD THIS at the point where elements actually fire:
    generate_sync_pulse();
    
    // ... rest of your code ...
}
```

### Step 6: Initialization in Main

Add DMA initialization to your main setup:

```cpp
// main.cpp
#include "array_dma_integration.h"

extern "C" void app_main() {
    // Your existing init
    array_control_init();
    
    // Initialize DMA integration
    array_dma_integration_init();
    
    // Optional: Pre-configure DMA with defaults
    // (or wait for host command)
    /*
    dma_acq_config_t dma_config = {
        .sample_rate = 20000000,
        .num_channels = 8,
        .samples_per_channel = 2048,
        .trigger = DMA_ACQ_TRIG_EXT,
        .trigger_gpio = 15
    };
    dma_acq_init(&dma_config);
    */
    
    // Your existing main loop
    while (1) {
        // Process commands...
    }
}
```

### Step 7: Build and Flash

```bash
# Set target (if not already)
idf.py set-target esp32s3

# Build
idf.py build

# Flash
idf.py -p /dev/ttyUSB0 flash

# Monitor
idf.py -p /dev/ttyUSB0 monitor
```

---

## Verification Steps

### 1. Check PSRAM is Working

In the monitor, you should see:
```
I (1234) DMA_ACQ: PSRAM buffer: 4 MB
```

### 2. Test Basic Commands

In the serial monitor, type:
```json
{"cmd": "ping"}
```
Should respond:
```json
{"status": "ok"}
```

### 3. Initialize DMA
```json
{"cmd": "dma_init", "num_channels": 8, "samples_per_channel": 1024}
```
Should respond:
```json
{"status": "ok", "sample_rate": 20000000, "num_channels": 8}
```

### 4. Check Status
```json
{"cmd": "dma_get_status"}
```
Should respond:
```json
{"status": "ok", "state": "idle"}
```

---

## Minimal Test Program

Create `main_minimal.cpp` for testing without full array control:

```cpp
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/uart.h"
#include "dma_acquisition.h"
#include "array_dma_integration.h"

static void echo_task(void *arg) {
    uint8_t data[256];
    
    while (1) {
        int len = uart_read_bytes(UART_NUM_0, data, sizeof(data) - 1, 
                                   pdMS_TO_TICKS(100));
        if (len > 0) {
            data[len] = '\0';
            char *response = handle_command((char*)data);
            if (response) {
                uart_write_bytes(UART_NUM_0, response, strlen(response));
                uart_write_bytes(UART_NUM_0, "\n", 1);
                free(response);
            }
        }
    }
}

extern "C" void app_main() {
    printf("DMA Test Firmware Starting...\n");
    
    array_dma_integration_init();
    
    // Create serial command task
    xTaskCreate(echo_task, "uart_echo", 4096, NULL, 5, NULL);
}
```

---

## Common Issues

### Issue: "undefined reference to `cmd_dma_init`"

**Solution:** Make sure `array_dma_integration.c` is in your CMakeLists.txt SRCS list.

### Issue: "PSRAM not found"

**Solution:** Check sdkconfig:
```bash
grep CONFIG_SPIRAM sdkconfig
```
Should show `CONFIG_SPIRAM=y`. If not, run:
```bash
idf.py menuconfig
# Component config -> ESP32S3-specific -> Support for external SPI-connected RAM
```

### Issue: "ADC channel already in use"

**Solution:** Ensure ADC isn't initialized elsewhere. The DMA code uses ADC1 which may conflict with Arduino analogRead().

### Issue: Trigger not working

**Solution:** Check wiring with multimeter (continuity test). Verify GPIO numbers match configuration.

---

## Next Steps After Integration

1. **Run integrity test:**
   ```bash
   python3 verify_dma_integrity.py --port /dev/ttyUSB0
   ```

2. **Run full pipeline test:**
   ```bash
   python3 full_pipeline_test.py --port /dev/ttyUSB0 --focus 50
   ```

3. **Connect real hardware** and verify with scope

---

## Files Checklist

- [ ] `dma_acquisition.h` copied to project
- [ ] `dma_acquisition.c` copied to project
- [ ] `array_dma_integration.h` copied to project
- [ ] `array_dma_integration.c` copied to project
- [ ] `CMakeLists.txt` updated with new sources
- [ ] `sdkconfig.defaults` has PSRAM enabled
- [ ] Command router updated with DMA commands
- [ ] SYNC trigger added to fire function
- [ ] Trigger wired (GPIO 15)
- [ ] ADC channels wired (GPIO 1-8)
- [ ] Firmware builds successfully
- [ ] `ping` command works
- [ ] `dma_init` command works
- [ ] Integrity test passes
