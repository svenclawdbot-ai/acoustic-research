# TurboQuant Unified System Guide

Complete guide for the unified TurboQuant acquisition, visualization, and analysis system.

---

## Overview

The unified system provides a single command-line interface for all TurboQuant operations:

```
turboquant [command] [subcommand] [options]
```

---

## Installation

### 1. Install Dependencies

```bash
cd /home/james/.openclaw/workspace
pip install -r requirements.txt
```

### 2. Make Executable

```bash
chmod +x turboquant.py
```

### 3. Optional: Add to PATH

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="/home/james/.openclaw/workspace:$PATH"
alias tq='turboquant.py'
```

---

## Quick Start

```bash
# 1. Scan for devices
turboquant device scan

# 2. Flash firmware (if needed)
turboquant device flash --port /dev/ttyUSB0

# 3. Start acquisition with recording
turboquant acquire --duration 60 --output test.h5

# 4. View real-time display
turboquant display --mode advanced

# 5. Analyze recorded data
turboquant analyze test.h5 --spectrogram
```

---

## Commands Reference

### Device Management

#### Scan for Devices
```bash
turboquant device scan
```

**Output:**
```
[INFO] Scanning for devices...

Found 2 serial port(s):
  1. /dev/ttyUSB0
     ✓ TurboQuant device detected
  2. /dev/ttyACM0

Use --port to specify device (e.g., --port /dev/ttyUSB0)
```

#### Flash Firmware
```bash
turboquant device flash --port /dev/ttyUSB0
```

**Requirements:**
- `esptool.py` installed (`pip install esptool`)
- Firmware binary at `build/array_control_firmware.bin`

#### Device Information
```bash
turboquant device info --port /dev/ttyUSB0
```

**Output:**
```json
{
  "status": "ok",
  "version": "1.2.0",
  "features": ["dma", "beamforming", "streaming"]
}
```

---

### Acquisition & Recording

#### Basic Recording
```bash
turboquant acquire --duration 60 --output session.h5
```

**Options:**
| Option | Default | Description |
|--------|---------|-------------|
| `--port` | `/dev/ttyUSB0` | Serial port |
| `--duration`, `-d` | `60` | Recording duration (seconds) |
| `--output`, `-o` | auto-generated | Output file |
| `--sample-rate` | `20e6` | Sample rate (Hz) |
| `--channels`, `-c` | `8` | Number of channels |

#### Format Selection (by extension)
```bash
turboquant acquire -d 300 -o session.h5    # HDF5
turboquant acquire -d 300 -o session.npz   # NumPy
turboquant acquire -d 300 -o session.wav   # WAV audio
turboquant acquire -d 300 -o session.tdms  # LabVIEW
turboquant acquire -d 300 -o session.bin   # Binary
```

#### Continuous Streaming + Recording
```bash
# Stream to network while recording locally
turboquant stream server --port /dev/ttyUSB0 --bind tcp://*:5555 &
turboquant acquire --duration 300 --output backup.h5
```

---

### Visualization

#### Basic Display
```bash
turboquant display --mode basic --port /dev/ttyUSB0
```

**Features:**
- 8-channel waveform display
- Simple trigger control
- FPS and latency monitoring

#### Advanced Display (Recommended)
```bash
turboquant display --mode advanced --port /dev/ttyUSB0
```

**Features:**
- Dual view: waveform + FFT
- Digital phosphor persistence
- Multiple trigger modes (auto, normal, single)
- Interactive cursors
- Measurements (Vpp, frequency, rise time)

#### Demo Mode (No Hardware)
```bash
turboquant display --mode demo
```

Generates synthetic ultrasound data for testing.

---

### Network Streaming

#### Server Mode
```bash
# With hardware
turboquant stream server --port /dev/ttyUSB0 --bind tcp://0.0.0.0:5555

# Demo mode (synthetic data)
turboquant stream server --demo --bind tcp://0.0.0.0:5555
```

**Network Configuration:**
- Data port: 5555 (PUB/SUB)
- Control port: 5556 (REP/REQ)

#### Client Mode
```bash
# Console mode
turboquant stream client --connect tcp://192.168.1.100:5555

# GUI mode
turboquant stream client --connect tcp://192.168.1.100:5555 --gui
```

#### Multiple Clients
One server can stream to many clients simultaneously:

```bash
# Terminal 1: Server
turboquant stream server --port /dev/ttyUSB0

# Terminal 2: Client (lab laptop)
turboquant stream client --connect tcp://server:5555 --gui

# Terminal 3: Client (office desktop)
turboquant stream client --connect tcp://server:5555 --gui

# Terminal 4: Client (cloud processing)
turboquant stream client --connect tcp://server:5555
```

---

### Data Analysis

#### File Information
```bash
turboquant analyze recording.h5 --info
```

**Output:**
```json
{
  "file": "recording.h5",
  "num_channels": 8,
  "total_samples": {"channel_0": 122880000},
  "duration_seconds": {"channel_0": 6.144},
  "statistics": {
    "channel_0": {
      "mean_mv": -2.3,
      "std_mv": 156.7,
      "vpp_mv": 892.4
    }
  }
}
```

#### Spectrogram
```bash
turboquant analyze recording.h5 --spectrogram --channel 0 --output spec.png
```

**Generates:**
- Time-domain waveform (top)
- Spectrogram (bottom)
- Color-coded frequency content over time

#### STFT (Short-Time Fourier Transform)
```bash
turboquant analyze recording.h5 --stft --channel 0
```

**Generates:**
- Time-domain waveform
- STFT magnitude (dB)
- STFT phase

#### Time Domain Plot
```bash
# All channels
turboquant analyze recording.h5 --time-domain

# Specific channels
turboquant analyze recording.h5 --time-domain --channels 0 2 4

# Limited duration
turboquant analyze recording.h5 --time-domain --duration 10
```

#### FFT Spectrum
```bash
# Individual + averaged spectrum
turboquant analyze recording.h5 --fft --channels 0 1 2 3
```

#### Interactive Viewer
```bash
turboquant analyze recording.h5 --interactive
```

Features:
- Scroll through time with slider
- 10ms window
- Real-time updates

#### Export Data
```bash
# Export to CSV (for Excel/MATLAB)
turboquant analyze recording.h5 --export csv --output data.csv

# Export to WAV (for audio analysis)
turboquant analyze recording.h5 --export wav --output audio.wav

# Export to NumPy
turboquant analyze recording.h5 --export npz --output data.npz
```

---

## Complete Workflow Examples

### Field Recording Session

```bash
# 1. Setup
turboquant device scan
turboquant device flash --port /dev/ttyUSB0

# 2. Start streaming server (for remote monitoring)
turboquant stream server --port /dev/ttyUSB0 --bind tcp://0.0.0.0:5555 &
SERVER_PID=$!

# 3. Record with real-time display
turboquant display --mode advanced &
DISPLAY_PID=$!

# 4. Start recording
turboquant acquire --duration 3600 --output field_session.h5

# 5. Cleanup
kill $SERVER_PID
kill $DISPLAY_PID
```

### Remote Collaboration

```bash
# At lab (server side)
turboquant stream server --port /dev/ttyUSB0 --bind tcp://0.0.0.0:5555

# At home (client side)
turboquant stream client --connect tcp://lab.public.ip:5555 --gui

# Cloud analysis (third client)
turboquant stream client --connect tcp://lab.public.ip:5555 | \
    python custom_analysis.py
```

### Post-Processing Pipeline

```bash
# 1. Record
turboquant acquire -d 300 -o experiment.h5

# 2. Generate spectrograms for all channels
for ch in 0 1 2 3 4 5 6 7; do
    turboquant analyze experiment.h5 --spectrogram --channel $ch \
        --output spec_ch${ch}.png
done

# 3. Export to MATLAB format
turboquant analyze experiment.h5 --export csv --output experiment.csv

# 4. Create report
python generate_report.py experiment.h5
```

---

## Configuration Files

### System-wide Config

Create `~/.turboquant/config.json`:

```json
{
  "default_port": "/dev/ttyUSB0",
  "default_baud": 921600,
  "default_sample_rate": 20000000,
  "default_channels": 8,
  "recording_directory": "~/recordings",
  "analysis": {
    "default_window": "hann",
    "default_nfft": 2048,
    "colormap": "viridis"
  }
}
```

### Per-Project Config

Create `turboquant.json` in project directory:

```json
{
  "sample_rate": 20000000,
  "channel_names": ["Element0", "Element1", "Element2", "Element3",
                   "Element4", "Element5", "Element6", "Element7"],
  "voltage_range_mv": 3300,
  "trigger_channel": 0,
  "notes": "8-element linear array, 0.5mm pitch"
}
```

---

## Troubleshooting

### "Device not found"
```bash
# Check permissions
ls -la /dev/ttyUSB*
sudo usermod -a -G dialout $USER

# Or use sudo temporarily
sudo turboquant device scan
```

### "Permission denied"
```bash
# Linux: Add user to dialout group
sudo usermod -a -G dialout $USER
# Log out and back in

# macOS: Grant permission in System Preferences
# Security & Privacy → Privacy → Developer Tools
```

### "Module not found"
```bash
# Install missing dependency
pip install pyserial numpy scipy matplotlib pyqtgraph h5py pyzmq

# Or use requirements.txt
pip install -r requirements.txt
```

### "Port busy"
```bash
# Find process using port
lsof /dev/ttyUSB0

# Kill process
kill -9 <PID>
```

### Low streaming performance
```bash
# Use compression
turboquant stream server --compression-level 6

# Reduce sample rate
turboquant acquire --sample-rate 10e6

# Use wired Ethernet instead of WiFi
```

---

## API Reference

### Python API

```python
from turboquant import SystemConfig
from data_recorder import DataRecorder, RecordingFormat
from network_stream import StreamServer, StreamClient
from data_analysis import analyze_file, generate_spectrogram

# Configuration
config = SystemConfig(
    default_port="/dev/ttyUSB0",
    default_sample_rate=20_000_000
)

# Recording
recorder = DataRecorder(
    'session.h5',
    format=RecordingFormat.HDF5
)
recorder.start_recording()
recorder.add_frame(timestamp, data)
stats = recorder.stop_recording()

# Streaming
server = StreamServer(StreamConfig(bind_address="tcp://*:5555"))
server.start()
server.send_frame(timestamp, data)

# Analysis
info = analyze_file('recording.h5')
generate_spectrogram('recording.h5', 'output.png', channel=0)
```

---

## Files Created

| File | Purpose | Lines |
|------|---------|-------|
| `turboquant.py` | Unified CLI launcher | 600 |
| `data_analysis.py` | HDF5 analysis tools | 550 |
| `TURBOQUANT_GUIDE.md` | This documentation | 500 |

---

## Next Steps

1. **Test the launcher:**
   ```bash
   turboquant --help
   turboquant device scan
   ```

2. **Try demo mode:**
   ```bash
   turboquant display --mode demo
   ```

3. **Record and analyze:**
   ```bash
   turboquant acquire -d 10 -o test.h5
   turboquant analyze test.h5 --spectrogram
   ```

4. **Set up streaming:**
   ```bash
   # Terminal 1
   turboquant stream server --demo
   
   # Terminal 2
   turboquant stream client --gui
   ```

---

**System Ready!** 🚀
