# GlassHouse Node v1.0 Firmware

Complete ESP32-S3 firmware for soil impedance monitoring.

## Quick Start

1. **Install libraries** — see `LIBRARIES.md`
2. **Edit `config.h`** — set your `NODE_ID` and MQTT broker IP
3. **Compile & flash** — select "ESP32S3 Dev Module", upload
4. **Open Serial Monitor** (115200 baud)
5. **Configure WiFi** — connect to `GlassHouse-Setup` AP, enter your WiFi password
6. **Calibrate** — type `cal-dry` with electrodes in dry soil, then `cal-wet` in wet soil

## Files

| File | Purpose |
|------|---------|
| `glasshouse_node_v1.ino` | Main sketch — measurement, WiFi, MQTT, sleep, CLI |
| `config.h` | Pin mappings, timing, calibration defaults |
| `platformio.ini` | PlatformIO build config |
| `LIBRARIES.md` | Required Arduino libraries |

## Serial CLI Commands

| Command | Action |
|---------|--------|
| `m` | Measure once (shows Z, phase, VWC) |
| `cal-dry` | Set dry calibration point |
| `cal-wet` | Set wet calibration point |
| `status` | Show calibration and last readings |
| `reset-cal` | Clear calibration |
| `wifi` | Reset WiFi credentials |
| `sleep` / `exit` | Exit CLI and go to sleep |

## Power Profile

| State | Current | Duration |
|-------|---------|----------|
| Deep sleep | ~45 µA | 14 min 59 s |
| Wake + measure | ~80 mA | ~150 ms |
| WiFi connect + MQTT | ~120 mA | ~3 s |
| **Average** | **~0.3 mA** | — |
| **Battery life** | **~6 months** | 2600 mAh 18650 |

## Measurement Parameters

- **Excitation:** 1 kHz sine, 100 mV pp
- **Sampling:** 400 samples at 250 µs interval (4 samples/cycle)
- **Integration:** 100 cycles
- **Measurement time:** ~120 ms
- **Interval:** 15 minutes (configurable in `config.h`)
