# Real-Time Display Documentation

High-performance real-time waveform visualization for DMA acquisition using PyQtGraph.

## Features

- **8-channel simultaneous display** - All channels in stacked view with linked time axis
- **Low latency** - Target <50ms from acquisition to display
- **20 FPS update rate** - Smooth visualization
- **Trigger visualization** - Configurable trigger level with visual indicator
- **Performance metrics** - Real-time FPS, latency, and sample rate monitoring
- **Interactive controls** - Run/stop, single capture, timebase adjustment

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or manually:
pip install pyserial numpy matplotlib pyqtgraph PyQt5
```

### Launch Display

```bash
# Basic usage
python realtime_display.py --port /dev/ttyUSB0

# With custom settings
python realtime_display.py \
    --port COM3 \
    --rate 30 \
    --window 200 \
    --samples 4096
```

### Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--port` | `/dev/ttyUSB0` | Serial port device |
| `--baud` | `921600` | Baud rate |
| `--rate` | `20` | Display update rate (Hz) |
| `--window` | `100` | Time window (μs) |
| `--samples` | `2048` | Samples per update |

## Interface Guide

### Control Panel

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ● Connected (/dev/ttyUSB0)  ▶ Run  ◉ Single  Timebase: [100 μs ▼]  FPS: 20.1 │
└─────────────────────────────────────────────────────────────────────────────┘
```

- **Connection Status**: Green = connected, Red = disconnected
- **Run/Stop**: Toggle continuous acquisition
- **Single**: Capture one burst (not yet implemented)
- **Timebase**: Select time window (10μs to 1ms)
- **FPS**: Actual display frame rate

### Waveform Display

```
┌────────────────────────────────────────────────────────────────┐
│ Ch 0 (mV)  ╭╮      ╭╮                        [Trigger line]    │
│          ─╯╰╯──────╯╰─────────────────────── [---------------] │
├────────────────────────────────────────────────────────────────┤
│ Ch 1       ╭╮      ╭╮                                         │
│          ─╯╰╯──────╯╰─────────────────────────────────────────│
├────────────────────────────────────────────────────────────────┤
│ ...                                                            │
├────────────────────────────────────────────────────────────────┤
│ Ch 7                                                          │
│                                                               │
└────────────────────────────────────────────────────────────────┘
           0μs              50μs              100μs
```

- **Channel 0 (Yellow)**: Trigger channel with adjustable trigger level
- **Channels 1-7**: Standard waveform display
- **Grid**: Time and amplitude grid for measurements
- **Trigger Line**: Red dashed line on channel 0, draggable

### Statistics Panel

```
Samples: 16384  Latency: 45.2 ms  Rate: 20.0 MSa/s  Errors: 0
```

- **Samples**: Total samples acquired in buffers
- **Latency**: Time from trigger to display
- **Rate**: Actual sample rate from device
- **Errors**: Continuity errors detected

## Operation Modes

### Continuous Mode (Default)

1. Click **Run** to start
2. DMA continuously acquires to PSRAM
3. Display updates at ~20 FPS
4. Click **Stop** to halt

### Single Capture (Not Yet Implemented)

Will capture one burst and hold display.

## Performance Tuning

### For Lower Latency (<30ms)

```bash
python realtime_display.py \
    --rate 30 \        # Higher update rate
    --samples 1024     # Smaller chunks
```

### For Smoother Display

```bash
python realtime_display.py \
    --rate 60 \        # Max refresh
    --window 200       # Wider view
```

### For Longer Capture History

```bash
python realtime_display.py \
    --samples 8192 \   # Larger buffers
    --window 500       # Longer window
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Toggle Run/Stop |
| `S` | Single capture |
| `+/-` | Increase/decrease timebase |
| `T` | Auto-set trigger level |
| `R` | Reset view |

## Troubleshooting

### "No module named 'pyqtgraph'"

```bash
pip install pyqtgraph PyQt5
```

### "Connection Failed"

1. Check port: `ls /dev/ttyUSB*` (Linux) or `mode COM3` (Windows)
2. Check permissions: `sudo usermod -a -G dialout $USER` (Linux)
3. Verify firmware is flashed and running

### "Low FPS"

1. Reduce timebase: `--window 50`
2. Reduce update rate: `--rate 10`
3. Close other applications
4. Check CPU usage

### "Display laggy"

1. Reduce samples: `--samples 1024`
2. Check USB connection quality
3. Try different USB port

## Technical Details

### Architecture

```
ESP32-S3 ──USB CDC──▶ Python ──PyQtGraph──▶ Display
  20 FPS              200 Hz        60 FPS
   (DMA)              (Polling)    (Render)
```

### Timing Budget

| Stage | Target | Notes |
|-------|--------|-------|
| Acquisition | 5ms | DMA to PSRAM |
| USB Transfer | 10ms | 4096 samples @ 921600 baud |
| Processing | 2ms | Reshape, convert |
| Display | 16ms | 60 FPS render |
| **Total** | **~33ms** | Well under 100ms target |

### Memory Usage

- PSRAM buffer: 4MB (ESP32)
- Python buffers: ~64KB per channel
- Display buffer: ~1MB GPU memory

## Integration with Other Tools

### With verify_dma_integrity.py

```bash
# Terminal 1: Run display
python realtime_display.py --port /dev/ttyUSB0

# Terminal 2: Run tests
python verify_dma_integrity.py --port /dev/ttyUSB0
```

### With full_pipeline_test.py

Display can run concurrently with automated tests.

## Future Enhancements

- [ ] Persistence mode (digital phosphor)
- [ ] Measurement cursors (delta time, amplitude)
- [ ] FFT view (frequency domain)
- [ ] Recording to file
- [ ] Protocol decoding
- [ ] Remote display (network streaming)

## See Also

- `DMA_IMPLEMENTATION.md` - Firmware details
- `full_pipeline_test.py` - Automated testing
- `verify_dma_integrity.py` - Data validation
