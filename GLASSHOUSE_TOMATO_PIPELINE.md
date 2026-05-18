# GlassHouse Tomatoes — Project Development Pipeline

*Soil property monitoring system for home glasshouse tomato cultivation*
*Built on the OpenClaw soil impedance spectroscopy foundation*

---

## 1. PROJECT OVERVIEW

### Purpose
Transform the existing TurboQuant soil impedance spectrometer into a practical, affordable monitoring system for home glasshouse tomato growers. Measure soil moisture, conductivity, and temperature to optimise watering and detect stress before visible symptoms.

### Target Environment
- **Location:** Small home glasshouse (2m × 3m typical)
- **Crop:** Tomatoes (determinate + indeterminate varieties)
- **Growing medium:** Multi-purpose compost, coco coir, or peat-free mixes
- **User:** Home gardener, not an engineer. Must be plug-and-play.

### Key Metrics to Monitor
| Parameter | Why It Matters for Tomatoes | Target Accuracy |
|-----------|----------------------------|-----------------|
| Volumetric Water Content (VWC) | Prevents blossom end rot (under) and root rot (over) | ±5% |
| Bulk Electrical Conductivity (EC) | Tracks nutrient availability and salt buildup | ±10% |
| Soil Temperature | Affects nutrient uptake, germination, root health | ±0.5°C |
| pH (stretch goal) | Critical for micronutrient availability | ±0.3 |

### Existing Assets (What We Have)
| Asset | Status | Reuse |
|-------|--------|-------|
| `soil_impedance_model.py` | ✅ Complete physics model | Core algorithm |
| `lockin_spectrometer.py` | ✅ Full simulation chain | DSP reference implementation |
| `noise_budget_analysis.py` | ✅ Noise analysis validated | Hardware spec validation |
| `hybrid_spectrometer_build_guide.md` | ✅ Weekend build guide | Hardware v1 baseline |
| `firmware/pulser_400v_controller.ino` | ⚠️ Wrong domain (ultrasound) | Ignore for soil |
| `firmware/lora_node_radiolib.ino` | ✅ LoRa comms framework | Adapt for soil node |
| `firmware/lora_gateway_radiolib.ino` | ✅ Gateway framework | Adapt for soil gateway |

---

## 2. SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         GLASSHOUSE TOMATO SYSTEM                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                   │
│  │  SENSOR     │     │  SENSOR     │     │  SENSOR     │   ... up to 4     │
│  │  NODE 1     │     │  NODE 2     │     │  NODE 3     │   per glasshouse  │
│  │ (Soil + Air)│     │ (Soil only) │     │ (Soil only) │                   │
│  └──────┬──────┘     └──────┬──────┘     └──────┬──────┘                   │
│         │ 868 MHz LoRa       │                   │                          │
│         └────────────────────┴───────────────────┘                          │
│                              │                                              │
│                              ▼                                              │
│                    ┌─────────────────┐                                      │
│                    │  GATEWAY NODE   │  Raspberry Pi Zero 2 W + LoRa HAT   │
│                    │  (Indoor)       │  WiFi → Home Router → Internet      │
│                    └────────┬────────┘                                      │
│                             │                                               │
│         ┌───────────────────┼───────────────────┐                          │
│         ▼                   ▼                   ▼                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                     │
│  │ Local LCD   │    │ Mobile App  │    │ Cloud API   │                     │
│  │ Dashboard   │    │ (React      │    │ (TimeScaleDB│                     │
│  │ (optional)  │    │  Native)    │    │  + Grafana) │                     │
│  └─────────────┘    └─────────────┘    └─────────────┘                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Sensor Node Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    SENSOR NODE v1.0                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐  │
│  │ AD9833  │───→│ BUFFER  │───→│ ELECTRODES│──→│   TIA   │  │
│  │  DDS    │    │ OPA1641 │    │ (Wenner)  │    │ OPA1641 │  │
│  └─────────┘    └─────────┘    └─────────┘    └───┬─────┘  │
│      ▲                                            │         │
│      │ SPI                                        │         │
│  ┌───┴─────┐    ┌─────────┐    ┌─────────┐       │         │
│  │  ESP32  │←───│   ADC   │←───│  TEMP   │←──────┘         │
│  │  -S3    │    │ (12-bit)│    │ DS18B20 │                 │
│  │         │    └─────────┘    └─────────┘                 │
│  │         │                                                 │
│  │         │    ┌─────────┐                                 │
│  │         └───→│  LoRa   │────→ 868 MHz → Gateway          │
│  │         SPI  │  E22    │                                 │
│  │              └─────────┘                                 │
│  └────────────────────────────────────────────────────────┘  │
│                                                             │
│  Power: 18650 Li-ion + TP4056 charger + HT7333 3.3V LDO    │
│  Sleep current: < 50 µA | Active: ~80 mA for 2s every 15 min│
│  Battery life: ~6 months                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. DEVELOPMENT PHASES

### Phase 0: Foundation Hardening (Week 1)
**Goal:** Lock the physics, freeze the simulation, validate against real soil.

**Tasks:**
1. **Soil model calibration** (2 days)
   - Collect 3 compost samples: dry, moist, saturated
   - Measure with multimeter (resistance mode) at 1 kHz approximation
   - Compare to `soil_impedance_model.py` predictions
   - Adjust `soil_states` dict with real compost values
   - Add tomato-specific growth stages: seedling, vegetative, flowering, fruiting

2. **Simulation validation** (2 days)
   - Run `lockin_spectrometer.py` with calibrated soil states
   - Verify 1% accuracy target at 100 kHz–1 MHz
   - Confirm 12-bit ADC is sufficient for glasshouse compost
   - Document: which frequency gives best moisture sensitivity

3. **Noise budget for glasshouse** (1 day)
   - Run `noise_budget_analysis.py` with ESP32-S3 parameters
   - Validate: 100 mV excitation, 1 kΩ TIA gain, 1 MSPS ADC
   - Confirm SNR > 40 dB for all soil states
   - Output: `docs/noise_validation_glasshouse.md`

**Deliverable:** Calibrated simulation + validation report
**Go/No-Go:** Simulation predicts >30 dB SNR and <5% VWC error

---

### Phase 1: Hardware Prototype (Weeks 2–3)
**Goal:** Working sensor node on breadboard, sending real data.

**Hardware v1 — Minimal Viable Sensor:**
Drop the Nucleo-H743. For a home glasshouse, the ESP32-S3 alone is sufficient:
- 12-bit ADC: enough for ±5% VWC target
- 240 MHz: enough for lock-in DSP in software
- WiFi + Bluetooth: local comms without LoRa initially
- ~£10 vs £20 for Nucleo

**Revised BOM for v1:**
| Item | Qty | Price | Note |
|------|-----|-------|------|
| ESP32-S3-DevKitC-1 | 1 | £9.50 | Main controller |
| AD9833 module | 1 | £3.00 | Sine excitation |
| OPA1641 DIP-8 | 1 | £3.00 | TIA |
| DS18B20 + 4.7kΩ | 1 | £2.00 | Soil temp |
| M6 stainless rods | 4 | £4.00 | Electrodes |
| Breadboard + wires | 1 set | £5.00 | Prototyping |
| 18650 + holder + TP4056 | 1 set | £6.00 | Power |
| **Total** | | **£32.50** | Per node |

**Week 2 Tasks:**
- Day 1: ESP32 first boot + Arduino IDE setup
- Day 2: AD9833 sine output verified on scope/multimeter
- Day 3: TIA breadboarded, tested with 1 kΩ resistor
- Day 4: 4-electrode Wenner array in compost pot
- Day 5: Dry/moist/saturated calibration measurements

**Week 3 Tasks:**
- Day 1–2: Software lock-in amplifier on ESP32
- Day 3: WiFi data upload to local endpoint
- Day 4: Power management + sleep modes
- Day 5: Battery life test (target: 48 hours minimum)

**Deliverable:** Breadboard node that logs VWC every 15 min to serial/WiFi
**Go/No-Go:** Dry vs saturated Z differs by >50%, measurement repeatable ±10%

---

### Phase 2: Firmware Platform (Weeks 4–5)
**Goal:** Production-ready firmware with calibration, OTA updates, and robust comms.

**Firmware Architecture:**
```
main/
├── config.h              # Pin mappings, calibration constants
├── soil_spectrometer.cpp # Lock-in measurement engine
├── soil_spectrometer.h
├── calibration.cpp       # Factory + user calibration routines
├── calibration.h
├── wifi_manager.cpp      # AP setup + STA connection
├── wifi_manager.h
├── mqtt_client.cpp       # Data publish (local broker first)
├── mqtt_client.h
├── ota_updater.cpp       # Over-the-air firmware updates
├── ota_updater.h
├── power_manager.cpp     # Sleep, wake, battery monitor
├── power_manager.h
└── main.ino              # Setup, loop, state machine
```

**Key Design Decisions:**
1. **Measurement frequency:** Single-point at 100 kHz (not a sweep)
   - Why: Sweeps take seconds; single point takes 50 ms
   - VWC correlation is strong at 100 kHz (validated in Phase 0)
   - Phase 3 can add multi-frequency if needed

2. **Calibration strategy:**
   - Factory: Store R_gain, electrode spacing, offset
   - User: "Dry" button (press when soil feels dry), "Wet" button (after watering)
   - Auto: Learn from user's watering patterns over 2 weeks

3. **Data format (JSON):**
   ```json
   {
     "node_id": "gh01-n01",
     "timestamp": "2026-05-10T14:30:00Z",
     "vwc_percent": 23.5,
     "ec_ms_cm": 1.85,
     "temp_c": 21.3,
     "battery_mv": 3850,
     "rssi_dbm": -72,
     "seq": 1523
   }
   ```

**Week 4 Tasks:**
- Implement single-frequency lock-in (100 kHz)
- Add DS18B20 temperature reading
- Build calibration UI (serial CLI for now)
- Add deep sleep between measurements

**Week 5 Tasks:**
- WiFiManager captive portal for setup
- MQTT publish to local broker (Raspberry Pi or laptop)
- OTA update via Arduino IDE → web upload
- Battery monitor via voltage divider

**Deliverable:** `firmware/glasshouse_node_v1.ino` — flashable, configurable, calibratable
**Go/No-Go:** 24-hour burn-in test: no crashes, data every 15 min, battery drops <10%

---

### Phase 3: Backend & Data Pipeline (Weeks 6–7)
**Goal:** Time-series database, API, and basic visualisation.

**Backend Stack:**
| Layer | Technology | Why |
|-------|-----------|-----|
| Database | TimescaleDB (PostgreSQL extension) | Time-series optimised, SQL familiar |
| API | FastAPI (Python) | Async, auto-docs, quick to build |
| Message Queue | Mosquitto MQTT | Lightweight, ESP32-native |
| Visualisation | Grafana | Free, time-series native, alerts |
| Hosting | Raspberry Pi 4 or old laptop | Local first, no cloud dependency |

**Docker Compose Stack:**
```yaml
# docker-compose.yml
services:
  timescaledb:
    image: timescale/timescaledb:latest-pg15
    volumes:
      - tsdb_data:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}

  mqtt:
    image: eclipse-mosquitto:2
    ports:
      - "1883:1883"
    volumes:
      - ./mosquitto.conf:/mosquitto/config/mosquitto.conf

  api:
    build: ./api
    ports:
      - "8000:8000"
    depends_on:
      - timescaledb
      - mqtt

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
```

**API Endpoints:**
```
POST   /api/v1/measurements          # Ingest from MQTT bridge
GET    /api/v1/measurements/latest   # Latest reading from node
GET    /api/v1/measurements/history  # Time-series query
GET    /api/v1/nodes                 # List registered nodes
POST   /api/v1/nodes/{id}/calibrate # Trigger calibration
GET    /api/v1/alerts                # Active alerts
```

**Week 6 Tasks:**
- Set up Raspberry Pi with Docker
- Deploy TimescaleDB + Grafana
- Build MQTT-to-DB bridge (Python script)
- Verify data flowing end-to-end

**Week 7 Tasks:**
- FastAPI with auto-generated OpenAPI docs
- Grafana dashboard: VWC, temp, battery over time
- Basic alerting: VWC < 15% (dry) or VWC > 45% (saturated)
- Data retention policy: 1-minute resolution for 7 days, 1-hour for 1 year

**Deliverable:** `backend/` directory with docker-compose, API, and Grafana dashboards
**Go/No-Go:** 7-day continuous logging, no data loss, Grafana renders <2s

---

### Phase 4: Mobile App (Weeks 8–10)
**Goal:** iOS/Android app for the home gardener.

**App Architecture:**
- **Framework:** React Native (Expo) — one codebase, both platforms
- **State:** Zustand (lightweight, no Redux boilerplate)
- **Charts:** react-native-gifted-charts or victory-native
- **Local storage:** AsyncStorage for offline cache
- **Push notifications:** Expo Notifications for alerts

**Screens:**
1. **Dashboard** — Current readings for all nodes
   - Big numbers: VWC %, temp °C, battery %
   - Colour coding: green (OK), amber (watch), red (alert)
   - Last reading timestamp

2. **History** — Time-series charts
   - 24h / 7d / 30d / 1y views
   - Overlay: watering events, rainfall (manual entry)
   - Export: CSV for spreadsheet analysis

3. **Node Detail** — Per-node management
   - Edit name ("Tomato Bed A", "Pepper Pot 1")
   - Calibration wizard (dry/wet buttons)
   - Measurement interval (15 min / 1h / 6h)
   - Firmware version + OTA trigger

4. **Alerts** — Notification history + rules
   - "Soil too dry" — VWC < threshold for >2 hours
   - "Soil too wet" — VWC > threshold for >6 hours
   - "Battery low" — < 20%
   - Custom thresholds per node

5. **Settings** — App configuration
   - Backend URL (local IP or cloud)
   - Units (°C/°F, %VWC / kPa)
   - Dark mode

**Week 8 Tasks:**
- Expo project scaffold
- API client + Zustand store
- Dashboard screen with mock data

**Week 9 Tasks:**
- History charts with real data
- Node detail + calibration UI
- Pull-to-refresh + offline indicator

**Week 10 Tasks:**
- Push notification integration
- Alert configuration screen
- App icon, splash screen, store screenshots
- Build APK + TestFlight IPA

**Deliverable:** `mobile/` directory with Expo project, build scripts
**Go/No-Go:** Beta test with 2 users, no crashes, data matches Grafana

---

### Phase 5: PCB & Enclosure (Weeks 11–12)
**Goal:** Move from breadboard to deployable hardware.

**PCB v1.0 Spec:**
- Size: 50 mm × 80 mm (fits in 100×60×40mm enclosure)
- 2-layer, JLCPCB standard
- ESP32-S3-WROOM-1 module (soldered, not dev board)
- AD9833 SOIC-10 (or keep module for v1)
- OPA1641 SOIC-8
- JST-PH connectors for electrodes, temp sensor, battery
- USB-C for charging + programming
- Test points for debugging

**Enclosure:**
- Hammond 1591XXSSBK or 3D-printed PETG
- IP54 (splash resistant, not submersible)
- Solar panel option: 1W 5V panel + TP4056 for indefinite power

**Week 11 Tasks:**
- KiCad schematic (reuse verified breadboard circuit)
- Component placement
- Routing (keep analog away from digital)
- DRC + Gerber generation

**Week 12 Tasks:**
- JLCPCB order (5 boards, ~£15 + shipping)
- 3D print enclosure
- Assembly + bring-up
- Compare PCB node vs breadboard: accuracy should match

**Deliverable:** `hardware/` directory with KiCad files, Gerbers, BOM, STL
**Go/No-Go:** 3 PCAs assemble and measure within ±5% of breadboard

---

### Phase 6: Integration & Field Test (Weeks 13–14)
**Goal:** Real glasshouse deployment, tomato growing season validation.

**Field Test Protocol:**
1. **Setup:** 3 nodes in tomato grow bags, 1 control (no sensor)
2. **Baseline:** 2 weeks of logging without changing watering
3. **Intervention:** Use app alerts to guide watering for 4 weeks
4. **Control:** Water control bed on fixed schedule
5. **Metrics:**
   - Fruit yield (weight, count)
   - Blossom end rot incidence
   - Water usage ( litres per plant)
   - User satisfaction (1–5 scale)

**Week 13 Tasks:**
- Deploy 3-node system in glasshouse
- Daily monitoring: data quality, battery, connectivity
- Log all watering events in app
- Weekly soil sample analysis (lab EC meter comparison)

**Week 14 Tasks:**
- Compare sensor VWC to gravimetric (oven-dry) method
- Correlate EC readings to fertiliser schedule
- Adjust calibration if systematic bias found
- Document: accuracy achieved, user feedback, bugs

**Deliverable:** `docs/field_test_report.md` with accuracy validation and yield data
**Go/No-Go:** VWC within ±5% of gravimetric, user rates app ≥4/5, no hardware failures

---

### Phase 7: Polish & Release (Weeks 15–16)
**Goal:** Product-ready system for other growers.

**Tasks:**
- Finalise enclosure design with feedback
- Write assembly guide (like existing build guide, but polished)
- Create calibration video
- Set up GitHub repo with releases
- Publish app to App Store / Play Store
- List on OpenSourceEcology or similar

**Deliverable:** GitHub release v1.0.0, published apps, assembly guide

---

## 4. BUILD PROCESS & CI/CD

### Repository Structure
```
glasshouse-tomatoes/
├── README.md
├── AGENTS.md
├── docker-compose.yml
├── firmware/
│   ├── glasshouse_node_v1/
│   │   ├── glasshouse_node_v1.ino
│   │   ├── config.h
│   │   ├── soil_spectrometer.cpp
│   │   ├── soil_spectrometer.h
│   │   ├── calibration.cpp
│   │   ├── wifi_manager.cpp
│   │   ├── mqtt_client.cpp
│   │   ├── ota_updater.cpp
│   │   └── power_manager.cpp
│   └── platformio.ini       # PlatformIO for CI builds
├── backend/
│   ├── api/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── routes/
│   │   └── requirements.txt
│   ├── mqtt_bridge/
│   │   └── bridge.py
│   ├── migrations/
│   └── grafana_dashboards/
├── mobile/
│   ├── App.js
│   ├── package.json
│   ├── src/
│   │   ├── screens/
│   │   ├── components/
│   │   ├── store/
│   │   └── api/
│   └── eas.json             # Expo build config
├── hardware/
│   ├── kicad/
│   │   ├── glasshouse_node_v1.kicad_pro
│   │   ├── glasshouse_node_v1.kicad_sch
│   │   └── glasshouse_node_v1.kicad_pcb
│   ├── gerbers/
│   ├── bom/
│   └── enclosure/
│       └── node_enclosure.stl
├── simulation/
│   ├── soil_impedance_model.py      # (from existing)
│   ├── lockin_spectrometer.py       # (from existing)
│   ├── noise_budget_analysis.py     # (from existing)
│   └── validate_compost.py          # New: compost-specific validation
├── docs/
│   ├── assembly_guide.md
│   ├── calibration_guide.md
│   ├── api_reference.md
│   └── field_test_report.md
└── tests/
    ├── firmware/
    ├── backend/
    └── mobile/
```

### CI/CD Pipeline (GitHub Actions)
```yaml
# .github/workflows/ci.yml
name: GlassHouse CI

on: [push, pull_request]

jobs:
  simulation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install numpy matplotlib
      - run: python simulation/validate_compost.py
      - run: python simulation/noise_budget_analysis.py

  firmware:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: arduino/setup-arduino-cli@v1
      - run: arduino-cli compile --fqbn esp32:esp32:esp32s3 firmware/glasshouse_node_v1/

  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r backend/api/requirements.txt
      - run: pytest backend/tests/

  mobile:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: cd mobile && npm ci
      - run: cd mobile && npx eslint .
      - run: cd mobile && npx jest
```

### Build Scripts
```bash
# scripts/build_firmware.sh
#!/bin/bash
set -e
pio run -d firmware/glasshouse_node_v1/

# scripts/build_backend.sh
#!/bin/bash
set -e
docker-compose -f docker-compose.yml build

# scripts/build_mobile.sh
#!/bin/bash
set -e
cd mobile
eas build --platform android --profile preview
```

---

## 5. TESTING STRATEGY

### Firmware Tests
| Test | Method | Pass Criteria |
|------|--------|---------------|
| Unit: Lock-in DSP | Feed known sine, verify amplitude/phase | <1% amplitude error, <1° phase error |
| Unit: Calibration | Dry/wet/saturated resistors | VWC within ±5% of known |
| Integration: End-to-end | Resistor network simulating soil | Z matches simulation |
| Hardware-in-loop: 24h burn | Real compost, constant conditions | No crashes, drift <5% |
| Power: Battery life | Full charge, normal duty cycle | >30 days |

### Backend Tests
| Test | Method | Pass Criteria |
|------|--------|---------------|
| Unit: API endpoints | pytest + TestClient | All return 200, schema valid |
| Integration: MQTT→DB | Publish test messages, query DB | 100% delivery, correct timestamps |
| Load: 100 nodes | k6 or locust | <100 ms p95 response |
| Data retention | Verify aggregation jobs | 1h buckets for >1 year old |

### Mobile Tests
| Test | Method | Pass Criteria |
|------|--------|---------------|
| Unit: Store logic | Jest | All reducers pure, no side effects |
| Integration: API client | MSW mock server | Handles 200, 404, 500, timeout |
| E2E: Critical path | Maestro or Detox | Login → view dashboard → see chart |
| Accessibility | axe + screen reader | WCAG 2.1 AA |

---

## 6. RISK REGISTER

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| ESP32 ADC noise too high | Medium | High | Add external ADC (ADS1115) or oversample |
| Soil model doesn't match compost | Medium | High | Phase 0 calibration with real compost |
| WiFi doesn't reach glasshouse | Low | Medium | Add LoRa back in, or mesh node |
| Battery life <30 days | Medium | High | Reduce duty cycle, add solar panel |
| PCB assembly errors | Medium | Medium | Test points, bring-up checklist, 5-board batch |
| App store rejection | Low | Medium | Follow guidelines, no crypto, privacy policy |
| User calibration too hard | Medium | High | Auto-calibration from watering patterns |
| Tomato season ends before field test | Low | High | Start in May, test with peppers as backup |

---

## 7. TIMELINE SUMMARY

| Phase | Weeks | Calendar | Key Deliverable |
|-------|-------|----------|----------------|
| 0. Foundation | 1 | May 10–16 | Calibrated simulation |
| 1. Hardware proto | 2–3 | May 17–30 | Breadboard node |
| 2. Firmware | 4–5 | May 31–June 13 | Production firmware |
| 3. Backend | 6–7 | June 14–27 | Grafana + API live |
| 4. Mobile app | 8–10 | June 28–July 18 | Beta on TestFlight |
| 5. PCB + enclosure | 11–12 | July 19–Aug 1 | 5 PCAs assembled |
| 6. Field test | 13–14 | Aug 2–15 | Yield comparison |
| 7. Release | 15–16 | Aug 16–29 | GitHub v1.0, stores |

**Total: 16 weeks to v1.0 release**
**Budget: ~£150 (3 nodes + Pi + components) + £99 Apple dev account**

---

## 8. DECISION LOG

| Date | Decision | Rationale | Reversible? |
|------|----------|-----------|-------------|
| May 10 | Drop Nucleo-H743, use ESP32-S3 alone | Cost, simplicity, sufficient ADC | Yes — can add external ADC |
| May 10 | Single-frequency (100 kHz) vs sweep | Speed, battery, sufficient for VWC | Yes — add sweep in v2 |
| May 10 | Local backend (Pi) vs cloud | Privacy, no subscription, offline | Yes — add cloud mirror later |
| May 10 | React Native vs native | One team, both platforms, Expo ease | Yes — rewrite native if needed |
| May 10 | 18650 battery vs LiPo | Safer, user-replaceable, no soldering | No — committed for v1 |

---

## 9. NEXT ACTIONS

1. **Today:** Fork existing `soil_impedance_model.py` → `simulation/validate_compost.py`
2. **This week:** Buy compost + pot, run dry/moist/saturated calibration
3. **Order:** ESP32-S3, AD9833, OPA1641, DS18B20, breadboard kit (if not already owned)
4. **Set up:** GitHub repo `glasshouse-tomatoes`, push this pipeline as `ROADMAP.md`
5. **Schedule:** 30 min daily standup with yourself, track blockers in repo issues

---

*Pipeline created: May 10, 2026*
*Based on: OpenClaw soil impedance spectroscopy foundation*
*Target: Home glasshouse tomato growers, UK climate*
