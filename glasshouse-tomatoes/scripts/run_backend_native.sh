#!/bin/bash
set -euo pipefail

# Native Python Backend Runner (no Docker required)
# ================================================
# Use this if Docker networking is unavailable or broken.
# Requires: Python 3.11+, pip, PostgreSQL 15+, Mosquitto MQTT

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "========================================"
echo "  GlassHouse Backend (Native Python)"
echo "========================================"
echo ""

# Check Python
if ! python3 --version | grep -q "3.11\|3.12"; then
    echo "WARNING: Python 3.11+ recommended. Found:"
    python3 --version
fi

# Create virtual environment if not exists
if [ ! -d .venv ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -q fastapi uvicorn sqlalchemy asyncpg psycopg2-binary pydantic pydantic-settings python-multipart httpx paho-mqtt

echo ""
echo "========================================"
echo "  Starting services..."
echo "========================================"
echo ""

# Check PostgreSQL
if ! pg_isready -h localhost -p 5432 &> /dev/null; then
    echo "WARNING: PostgreSQL not running on localhost:5432"
    echo "  Install: sudo apt install postgresql postgresql-contrib"
    echo "  Start:   sudo systemctl start postgresql"
    echo "  Create:  sudo -u postgres createdb glasshouse"
    echo ""
    read -p "Press Enter to continue anyway, or Ctrl+C to stop and set up Postgres first..."
fi

# Check Mosquitto
if ! pgrep -x mosquitto &> /dev/null; then
    echo "WARNING: Mosquitto MQTT broker not running"
    echo "  Install: sudo apt install mosquitto mosquitto-clients"
    echo "  Start:   sudo systemctl start mosquitto"
    echo ""
    read -p "Press Enter to continue anyway, or Ctrl+C to stop and set up Mosquitto first..."
fi

export DATABASE_URL="postgresql+asyncpg://gh_user:changeme@localhost:5432/glasshouse"
export MQTT_HOST="localhost"
export MQTT_PORT="1883"

# Start API in background
echo "Starting FastAPI on http://localhost:8000 ..."
python3 backend/api/main.py &
API_PID=$!

# Start MQTT bridge in background
echo "Starting MQTT Bridge..."
python3 backend/mqtt_bridge/bridge.py &
BRIDGE_PID=$!

echo ""
echo "========================================"
echo "  🍅 Backend running (native Python)"
echo "========================================"
echo ""
echo "  API:     http://localhost:8000"
echo "  Health:  http://localhost:8000/health"
echo "  PIDs:    API=$API_PID  Bridge=$BRIDGE_PID"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for interrupt
trap "echo 'Stopping services...'; kill $API_PID $BRIDGE_PID 2>/dev/null; exit 0" INT TERM
wait
