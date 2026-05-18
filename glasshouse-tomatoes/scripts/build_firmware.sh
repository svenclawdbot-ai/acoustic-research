#!/bin/bash
set -euo pipefail

# Build firmware for ESP32-S3 using Arduino CLI or PlatformIO

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
FIRMWARE_DIR="$PROJECT_DIR/firmware/glasshouse_node_v1"

if command -v pio &> /dev/null; then
    echo "Building with PlatformIO..."
    cd "$FIRMWARE_DIR"
    pio run
elif command -v arduino-cli &> /dev/null; then
    echo "Building with Arduino CLI..."
    cd "$FIRMWARE_DIR"
    arduino-cli compile --fqbn esp32:esp32:esp32s3 .
else
    echo "ERROR: Neither PlatformIO nor Arduino CLI found."
    echo "Install one of:"
    echo "  pip install platformio"
    echo "  or"
    echo "  curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh"
    exit 1
fi

echo "✓ Firmware build complete"
