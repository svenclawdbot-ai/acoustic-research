#!/bin/bash
# Repo organization script for acoustic-research
# Keep turboquant_v5 as main project, sort everything else

set -e
cd /home/james/.openclaw/workspace

echo "=== Repo Organization Plan ==="

# 1. Create folder structure
echo "Creating folders..."
mkdir -p archive/2026-03/{research,outputs,docs}
mkdir -p archive/2026-04/{research,outputs,docs}
mkdir -p archive/legacy-fpga
mkdir -p archive/legacy-kicad
mkdir -p potential-projects/radar-cw-doppler
mkdir -p potential-projects/agricultural-sensing
mkdir -p potential-projects/trading-bot
mkdir -p potential-projects/solana-sniper
mkdir -p potential-projects/react-native-app
mkdir -p potential-projects/phone-imu-app
mkdir -p docs/turboquant-analysis

echo "Folders created."
