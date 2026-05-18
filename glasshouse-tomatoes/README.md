# 🍅 GlassHouse Tomatoes

**Soil property monitoring for home glasshouse tomato cultivation.**

Built on the [OpenClaw](https://github.com/openclaw) soil impedance spectroscopy foundation, this project turns lab-grade physics into a practical, affordable monitoring system for home gardeners.

---

## What It Does

- **Measures soil moisture** (VWC) via electrical impedance spectroscopy
- **Tracks soil temperature** with DS18B20 probe
- **Monitors battery level** and wireless signal strength
- **Alerts you** when soil is too dry or too wet
- **Logs history** so you can optimise watering patterns
- **Works offline** — local backend on Raspberry Pi, no cloud required

## System Overview

```
Sensor Node (ESP32-S3)  →  MQTT  →  Raspberry Pi Backend  →  Mobile App
     │                                              │
     └─ 4-electrode Wenner array in compost         └─ TimescaleDB + Grafana
```

## Quick Start

### 1. Hardware (Breadboard Prototype)

See [`docs/assembly_guide.md`](docs/assembly_guide.md) for the weekend build guide.

**Parts needed (~£33 per node):**
- ESP32-S3-DevKitC-1
- AD9833 DDS module
- OPA1641 op-amp (DIP-8)
- DS18B20 temperature sensor
- 4× M6 stainless steel electrodes
- Breadboard, wires, 18650 battery

### 2. Backend (Docker)

```bash
# On your Raspberry Pi or laptop
git clone https://github.com/yourusername/glasshouse-tomatoes.git
cd glasshouse-tomatoes
./scripts/build_backend.sh

# Open Grafana at http://localhost:3000 (admin/admin)
```

### 3. Firmware

```bash
# Edit firmware/glasshouse_node_v1/config.h with your WiFi credentials
./scripts/build_firmware.sh

# Flash via USB-C
arduino-cli upload --fqbn esp32:esp32:esp32s3 \
  --port /dev/ttyUSB0 firmware/glasshouse_node_v1/
```

### 4. Mobile App

```bash
cd mobile
npm install
npx expo start

# Scan QR code with Expo Go app on your phone
```

## Project Structure

```
glasshouse-tomatoes/
├── firmware/           # ESP32-S3 Arduino/PlatformIO project
├── backend/            # FastAPI + TimescaleDB + Grafana + MQTT
├── mobile/             # React Native (Expo) app
├── hardware/           # KiCad PCB + 3D-printed enclosure
├── simulation/         # Python physics models (from OpenClaw)
├── docs/               # Assembly, calibration, API reference
└── scripts/            # Build, flash, and deploy helpers
```

## Development Roadmap

| Phase | Status | Deliverable |
|-------|--------|-------------|
| 0. Foundation | 🔄 In Progress | Calibrated simulation |
| 1. Hardware Prototype | 📋 Planned | Breadboard node |
| 2. Firmware | 📋 Planned | Production firmware |
| 3. Backend | 📋 Planned | Grafana + API live |
| 4. Mobile App | 📋 Planned | Beta on TestFlight |
| 5. PCB + Enclosure | 📋 Planned | 5 assembled nodes |
| 6. Field Test | 📋 Planned | Yield comparison |
| 7. Release | 📋 Planned | GitHub v1.0 |

See [`GLASSHOUSE_TOMATO_PIPELINE.md`](GLASSHOUSE_TOMATO_PIPELINE.md) for the full 16-week plan.

## Testing

```bash
# Run all simulations
./scripts/run_simulation.sh

# Run backend tests
pytest backend/tests/

# Run mobile tests
cd mobile && npx jest

# Run full CI locally
act -j simulation
```

## Contributing

1. Check the [Roadmap](GLASSHOUSE_TOMATO_PIPELINE.md) for open tasks
2. Open an issue to discuss your idea
3. Fork, branch, and submit a PR
4. All PRs must pass CI (simulation + firmware compile + backend tests)

## License

MIT — open hardware, open software. Build it, sell it, improve it. Just share your improvements.

---

*Built with 🍅 and 🔬 in the OpenClaw workspace.*
