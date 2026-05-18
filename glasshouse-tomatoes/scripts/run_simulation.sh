#!/bin/bash
set -euo pipefail

# Run simulation validation suite

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SIM_DIR="$PROJECT_DIR/simulation"

cd "$SIM_DIR"

echo "Running soil impedance model..."
python soil_impedance_model.py

echo ""
echo "Running lock-in spectrometer simulation..."
python lockin_spectrometer.py

echo ""
echo "Running noise budget analysis..."
python noise_budget_analysis.py

echo ""
echo "✓ All simulations complete. Check generated PNG files."
