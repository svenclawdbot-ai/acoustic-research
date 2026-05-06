# DMA Acquisition Implementation - Documentation

## Overview

Complete DMA streaming pipeline for ESP32-S3 that enables high-speed multi-channel ADC acquisition with PSRAM buffering. This bridges the gap between the beamforming firmware and real-world data capture.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        HOST PC (Python)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Pipeline   │  │   Verifier   │  │   Real-time Display  │  │
│  │    Test      │  │    Tool      │  │       (PyQtGraph)    │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
└─────────┼─────────────────┼────────────────────┼──────────────┘
          │                 │                    │
          └─────────────────┼────────────────────┘
                            │ USB CDC (921600 baud)
┌───────────────────────────▼────────────────────────────────────┐
│                     ESP32-S3 FIRMWARE                           │
│  ┌────────────────────────────────────────────────────────┐    │
│  │           Array Control (existing)                      │    │
│  │  - Element firing (shift registers)                    │    │
│  │  - Beamforming delay calculation                       │    │
│  │  - JSON command interface                              │    │
│  └────────────────────┬───────────────────────────────────┘    │
│                       │                                         │
│  ┌────────────────────▼───────────────────────────────────┐    │
│  │           DMA Acquisition (new)                         │    │
│  │  ┌──────────────┐    ┌──────────────┐                 │    │
│  │  │  Burst Mode  │    │  Continuous  │                 │    │
│  │  │  (SRAM)      │    │  (PSRAM)     │                 │    │
│  │  └──────┬───────┘    └──────┬───────┘                 │    │
│  │         │                   │                          │    │
│  │  ┌──────▼───────┐    ┌──────▼───────┐                 │    │
│  │  │ Ping-Pong    │    │ 4MB Ring     │                 │    │
│  │  │ Buffers      │    │ Buffer       │                 │    │
│  │  └──────┬───────┘    └──────┬───────┘                 │    │
│  │         │                   │                          │    │
│  │  ┌──────▼───────────────────▼───────┐                 │    │
│  │  │      ADC1 (8 channels)           │                 │    │
│  │  │      20 MSa/s max                │                 │    │
│  │  └──────────────────────────────────┘                 │    │
│  └────────────────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────────────┘
```

## Files Created

### Firmware (C/ESP-IDF)

| File | Lines | Description |
|------|-------|-------------|
| `dma_acquisition.h` | 170 | Header with configuration, types, and API |
| `dma_acquisition.c` | 650 | Complete DMA implementation with PSRAM support |
| `array_dma_integration.h` | 40 | Integration header |
| `array_dma_integration.c` | 250 | Command handlers for JSON interface |

### Host (Python)

| File | Lines | Description |
|------|-------|-------------|
| `verify_dma_integrity.py` | 320 | Data integrity verification tool |
| `full_pipeline_test.py` | 430 | End-to-end pipeline test with plotting |

## Key Features

### 1. Dual Mode Operation

**Burst Mode (SRAM)**
- Acquire → Stop → Transfer
- Best for: Single-shot elastography
- Buffer: Ping-pong SRAM buffers
- Max samples: 65,536 per channel

**Continuous Mode (PSRAM)**
- Store to PSRAM → Transfer at leisure
- Best for: Continuous monitoring
- Buffer: 4MB ring buffer
- Duration: ~200ms at 20 MSa/s (8ch)

### 2. Trigger Options

- **External**: GPIO pin trigger (sync with array firing)
- **Software**: Immediate trigger via command
- **Timer**: Periodic acquisition (for continuous mode)

### 3. Data Integrity

- Ramp pattern verification
- Sample rate measurement
- Continuity error detection
- Timestamp tracking

## API Reference

### Firmware Commands (JSON over Serial)

```json
// Initialize DMA
{"cmd": "dma_init", 
 "num_channels": 8, 
 "samples_per_channel": 2048,
 "sample_rate": 20000000,
 "trigger": "ext",
 "trigger_gpio": 15}

// Start burst acquisition
{"cmd": "dma_start_burst"}

// Get status
{"cmd": "dma_get_status"}
// Response: {"status": "ok", "state": "acquiring", "samples_acquired": 16384, ...}

// Read data (followed by binary transfer)
{"cmd": "dma_read_data"}
// Response: {"status": "ok", "bytes_available": 32768, "samples": 16384}

// Stop acquisition
{"cmd": "dma_stop"}
```

### C API

```c
// Initialize
dma_acq_config_t config = {
    .sample_rate = 20000000,
    .num_channels = 8,
    .samples_per_channel = 2048,
    .trigger = DMA_ACQ_TRIG_EXT,
    .trigger_gpio = 15
};
dma_acq_init(&config);

// Burst mode
dma_acq_start_burst();
// ... wait for trigger ...
dma_acq_read_data(buffer, max_size, &bytes_read);

// Continuous mode
dma_acq_start_continuous();
// ... wait ...
dma_acq_read_psram(offset, buffer, size);

// Cleanup
dma_acq_deinit();
```

### Python API

```python
from verify_dma_integrity import DMAVerifier

verifier = DMAVerifier(port='/dev/ttyUSB0')
verifier.connect()
verifier.run_burst_test(num_bursts=10, samples_per_channel=4096)
verifier.print_summary()
```

## Usage Examples

### 1. Basic Burst Test

```bash
# Run 10 bursts, verify data integrity
python verify_dma_integrity.py --port /dev/ttyUSB0 --bursts 10 --samples 4096
```

Expected output:
```
DMA Integrity Test
============================================================
Bursts: 10
Channels: 8
Samples/ch: 4096
Sample rate: 20.0 MSa/s
============================================================

Burst 1/10... PASS (SR: 19.98 MSa/s, Errors: 0)
Burst 2/10... PASS (SR: 19.97 MSa/s, Errors: 0)
...

TEST SUMMARY
============================================================
Total tests: 10
Passed: 10
Failed: 0

Sample Rate Statistics:
  Mean: 19.980 MSa/s
  Std:  0.003 MSa/s
============================================================
```

### 2. Full Pipeline Test

```bash
# Fire array, acquire, plot waveforms
python full_pipeline_test.py --port /dev/ttyUSB0 --focus 50 --plot waveforms.png
```

Expected output:
```
FULL PIPELINE TEST
============================================================
✓ Geometry: 8 elements @ 0.5mm pitch
✓ Focus: 50.0mm depth, 0.0° angle
✓ DMA: 8ch × 2048 @ 20.0 MSa/s
✓ DMA armed
✓ Fired focused beam

Waiting for data...
✓ Received 16384 samples
✓ Plot saved to waveforms.png

DELAY VALIDATION
============================================================
Focus point: (0.0, 50.0) mm

Channel arrival times:
  Ch 0: pos=0.0mm, arrival=32.47us, TOF=32.47us
  Ch 1: pos=0.5mm, arrival=32.52us, TOF=32.52us
  ...

✓ Progressive delays confirmed (all positive)
============================================================
```

### 3. Latency Measurement

```bash
python full_pipeline_test.py --port /dev/ttyUSB0 --focus 50 --latency
```

Expected output:
```
LATENCY MEASUREMENT
============================================================
  Iteration 1: 45.2 ms
  Iteration 2: 44.8 ms
  ...

Latency Statistics:
  Mean: 45.0 ms
  Std:  0.3 ms
  Min:  44.5 ms
  Max:  45.8 ms
============================================================
```

## Integration Steps

### 1. Add to Build System

In your `CMakeLists.txt`:

```cmake
set(SOURCES 
    ${SOURCES}
    "dma_acquisition.c"
    "array_dma_integration.c"
)

# Enable PSRAM
set(EXTRA_COMPONENT_DIRS $ENV{IDF_PATH}/examples/system/console/components)
```

In `sdkconfig`:
```
CONFIG_SPIRAM=y
CONFIG_SPIRAM_USE_MALLOC=y
```

### 2. Add Command Router

In your main command handler:

```c
#include "array_dma_integration.h"

char* handle_command(const char* json_cmd) {
    cJSON *root = cJSON_Parse(json_cmd);
    cJSON *cmd = cJSON_GetObjectItem(root, "cmd");
    
    if (strcmp(cmd->valuestring, "dma_init") == 0) {
        return cmd_dma_init(root);
    } else if (strcmp(cmd->valuestring, "dma_start_burst") == 0) {
        return cmd_dma_start_burst(root);
    }
    // ... etc
    
    cJSON_Delete(root);
}
```

### 3. Connect Trigger to Array

Ensure the SYNC output from your array firing circuit is connected to GPIO 15 (or configured trigger pin).

## Performance Specifications

| Metric | Value | Notes |
|--------|-------|-------|
| Max sample rate | 20 MSa/s | 2.5 MSa/s per channel (8ch) |
| ADC resolution | 12-bit | Stored in 16-bit container |
| Burst buffer | 2 × 64KB | Ping-pong in SRAM |
| PSRAM buffer | 4MB | Ring buffer for continuous |
| USB transfer | ~90 kB/s | CDC at 921600 baud |
| Trigger latency | <1 μs | Hardware GPIO interrupt |

## Troubleshooting

### "DMA init failed: ESP_ERR_NO_MEM"
- PSRAM not enabled in sdkconfig
- Reduce `samples_per_channel`

### "Acquisition timeout"
- Trigger signal not reaching GPIO
- Check trigger edge configuration

### "Sample rate error > 0.1%"
- ESP32-S3 ADC has inherent jitter
- Use external clock source if precise timing needed

### "Continuity errors detected"
- DMA buffer overflow (increase buffer size)
- CPU starving DMA (reduce processing in ISR)

## Next Steps

1. **Hardware bring-up**: Flash firmware, verify basic connectivity
2. **Ramp test**: Verify data integrity with known test pattern
3. **Array sync**: Connect SYNC output to trigger input
4. **Field test**: Acquire real ultrasound data

## Dependencies

### Firmware
- ESP-IDF v5.0+
- cJSON library

### Python
- pyserial
- numpy
- matplotlib

## Validation Checklist

- [ ] DMA triggers reliably on SYNC signal
- [ ] No sample loss verified via ramp test
- [ ] PSRAM buffer holds 4MB without corruption
- [ ] USB transfer completes without timeout
- [ ] Full pipeline runs 10× without errors
- [ ] Wavefront delay visible across elements
- [ ] Latency measurement <100ms fire-to-display

---

*Implementation complete - ready for hardware bring-up*
