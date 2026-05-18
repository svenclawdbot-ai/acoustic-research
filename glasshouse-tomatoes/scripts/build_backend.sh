#!/bin/bash
set -euo pipefail

# Build and start backend services with Docker Compose

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "Building backend services..."
docker-compose build

echo ""
echo "Starting services..."
docker-compose up -d

echo ""
echo "Waiting for services to be healthy..."
sleep 5

echo ""
echo "Service status:"
docker-compose ps

echo ""
echo "URLs:"
echo "  API:       http://localhost:8000"
echo "  Grafana:   http://localhost:3000  (admin/admin)"
echo "  MQTT:      localhost:1883"
