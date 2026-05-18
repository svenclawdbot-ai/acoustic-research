#!/bin/bash
set -euo pipefail

# GlassHouse Backend Setup Script
# ================================
# One-command setup for the complete backend stack

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "========================================"
echo "  GlassHouse Backend Setup"
echo "========================================"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker not found. Install from https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "ERROR: Docker Compose not found. Install from https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if .env exists, create if not
if [ ! -f .env ]; then
    echo "Creating .env file with default passwords..."
    cat > .env << 'EOF'
# GlassHouse Backend Environment
# ================================
# Change these defaults before production use!

DB_PASSWORD=glasshouse_secure_2026
GRAFANA_PASSWORD=admin
EOF
    echo "✓ Created .env — edit it to change default passwords"
    echo ""
fi

# Source .env
set -a
source .env
set +a

echo "Building and starting services..."
echo ""

# Build and start
if docker compose version &> /dev/null; then
    docker compose up --build -d
else
    docker-compose up --build -d
fi

echo ""
echo "Waiting for services to be healthy..."
sleep 5

# Wait for TimescaleDB
for i in {1..30}; do
    if docker exec gh_timescaledb pg_isready -U gh_user -d glasshouse &> /dev/null; then
        echo "✓ TimescaleDB ready"
        break
    fi
    echo "  Waiting for TimescaleDB... ($i/30)"
    sleep 2
    if [ $i -eq 30 ]; then
        echo "✗ TimescaleDB failed to start. Check logs: docker logs gh_timescaledb"
        exit 1
    fi
done

# Wait for MQTT
for i in {1..30}; do
    if docker exec gh_mqtt mosquitto_pub -t health -m test -r &> /dev/null; then
        echo "✓ MQTT broker ready"
        break
    fi
    echo "  Waiting for MQTT... ($i/30)"
    sleep 1
    if [ $i -eq 30 ]; then
        echo "✗ MQTT failed to start. Check logs: docker logs gh_mqtt"
        exit 1
    fi
done

# Wait for API
for i in {1..30}; do
    if curl -s http://localhost:8000/health | grep -q "ok"; then
        echo "✓ API ready"
        break
    fi
    echo "  Waiting for API... ($i/30)"
    sleep 1
    if [ $i -eq 30 ]; then
        echo "✗ API failed to start. Check logs: docker logs gh_api"
        exit 1
    fi
done

# Wait for Grafana
for i in {1..30}; do
    if curl -s http://localhost:3000/api/health | grep -q "ok"; then
        echo "✓ Grafana ready"
        break
    fi
    echo "  Waiting for Grafana... ($i/30)"
    sleep 1
    if [ $i -eq 30 ]; then
        echo "✗ Grafana failed to start. Check logs: docker logs gh_grafana"
        exit 1
    fi
done

echo ""
echo "========================================"
echo "  🍅 GlassHouse Backend is LIVE"
echo "========================================"
echo ""
echo "Services:"
echo "  📊 Grafana:     http://localhost:3000"
echo "                 Login: admin / ${GRAFANA_PASSWORD:-admin}"
echo "  🔌 API:         http://localhost:8000"
echo "  📡 MQTT:        localhost:1883"
echo "  🗄️  Database:   localhost:5432"
echo ""
echo "Dashboard:"
echo "  Open Grafana → Dashboards → GlassHouse → 'GlassHouse Tomatoes — Soil Monitor'"
echo ""
echo "Test data injection:"
echo "  mosquitto_pub -h localhost -t 'glasshouse/gh-n01/telemetry' -m '{\"node_id\":\"gh-n01\",\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"vwc_percent\":28.5,\"temp_c\":21.3,\"battery_mv\":3850,\"rssi_dbm\":-65,\"seq\":1}'"
echo ""
echo "View logs:"
echo "  docker logs -f gh_mqtt_bridge   # MQTT → DB ingestion"
echo "  docker logs -f gh_api           # REST API"
echo ""
echo "Stop everything:"
echo "  docker compose down"
echo ""
