#!/bin/bash

# Solana Sniper Bot - Startup Script

echo "🚀 Solana Sniper Bot"
echo "===================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Check environment file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "Creating from .env.example..."
    cp .env.example .env
    echo "Please edit .env with your wallet key before running."
    exit 1
fi

# Start mode selection
echo ""
echo "Select mode:"
echo "1) Dry Run (testing)"
echo "2) Live Trading (real funds)"
echo ""
read -p "Enter choice (1/2): " choice

if [ "$choice" = "1" ]; then
    echo "Starting in DRY RUN mode..."
    export SNIPER_DRY_RUN=true
    python src/main.py --dry-run
elif [ "$choice" = "2" ]; then
    echo "⚠️  WARNING: Starting in LIVE mode!"
    read -p "Are you sure? (yes/no): " confirm
    if [ "$confirm" = "yes" ]; then
        export SNIPER_DRY_RUN=false
        python src/main.py --live
    else
        echo "Cancelled."
        exit 0
    fi
else
    echo "Invalid choice."
    exit 1
fi
