# GlassHouse Backend

Complete Docker-based backend for soil monitoring data.

## Architecture

```
Sensor Node (MQTT) → Mosquitto → MQTT Bridge → TimescaleDB → Grafana
                                          ↓
                                       FastAPI
```

| Service | Port | Purpose |
|---------|------|---------|
| TimescaleDB | 5432 | Time-series database |
| Mosquitto MQTT | 1883 / 9001 | Message broker |
| FastAPI | 8000 | REST API |
| Grafana | 3000 | Visualisation |
| MQTT Bridge | — | MQTT → DB ingestion |

## Quick Start

```bash
# One-command setup
./scripts/setup_backend.sh

# Or manually:
docker compose up --build -d
```

## Access Points

| Service | URL | Default Login |
|---------|-----|---------------|
| Grafana | http://localhost:3000 | admin / admin |
| API Docs | http://localhost:8000/docs | — |
| API Health | http://localhost:8000/health | — |

## Dashboard

The **GlassHouse Tomatoes — Soil Monitor** dashboard auto-provisions on first start.

### Dashboard Panels

| Panel | What It Shows |
|-------|---------------|
| **Soil Moisture (VWC)** | Time-series with colour thresholds (red <15%, green 15–35%, yellow 35–45%, red >45%) |
| **Soil Temperature** | Time-series with optimal range 20–24°C highlighted |
| **Battery Voltage** | Track battery life, alert at <3.3V |
| **WiFi Signal (RSSI)** | Monitor connectivity quality |
| **Recent Readings** | Table of last 20 measurements |
| **Watering Recommendation** | Auto-generated advice based on VWC |
| **Tomato Care Guide** | Markdown reference for watering, problems, growth stages |

### Variable: Node Selector

Top of dashboard has a dropdown to switch between sensor nodes. Auto-populates from `measurements` table.

## Injecting Test Data

```bash
# Publish a test measurement
mosquitto_pub -h localhost -t 'glasshouse/gh-n01/telemetry' -m '{
  "node_id": "gh-n01",
  "timestamp": "2026-05-10T14:30:00Z",
  "vwc_percent": 28.5,
  "temp_c": 21.3,
  "battery_mv": 3850,
  "rssi_dbm": -65,
  "seq": 1
}'

# Verify it arrived
curl http://localhost:8000/api/v1/measurements/latest?node_id=gh-n01
```

## API Endpoints

```
POST   /api/v1/measurements          # Ingest measurement
GET    /api/v1/measurements/latest   # Latest reading
GET    /api/v1/measurements/history  # Time-series query
GET    /api/v1/nodes                 # List all nodes
GET    /health                       # Health check
```

See `api/main.py` for full OpenAPI schema at `/docs`.

## File Structure

```
backend/
├── api/                    # FastAPI service
│   ├── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── mqtt_bridge/            # MQTT → TimescaleDB bridge
│   ├── bridge.py
│   └── Dockerfile
├── grafana_dashboards/     # Dashboard JSONs
│   └── glasshouse_dashboard.json
├── grafana_dashboards.yml  # Provisioning config
├── grafana_datasources.yml # Postgres datasource
└── mosquitto.conf          # MQTT broker config
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `connection refused` to DB | Wait 10s after `docker compose up` for TimescaleDB to initialise |
| Dashboard not appearing | Refresh Grafana UI, or check `docker logs gh_grafana` |
| No data in dashboard | Check `docker logs gh_mqtt_bridge` — is MQTT connecting? |
| MQTT publish fails | Verify broker is running: `docker exec gh_mqtt mosquitto_pub -t test -m ok` |

## Environment Variables

Create `.env` in project root:

```bash
DB_PASSWORD=your_secure_password
GRAFANA_PASSWORD=your_secure_password
```
