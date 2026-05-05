#!/bin/bash
# quick_test.sh - Quick validation script for DMA acquisition
# Usage: ./quick_test.sh [PORT]

PORT=${1:-/dev/ttyUSB0}

echo "======================================================"
echo "DMA Acquisition Quick Test"
echo "======================================================"
echo "Port: $PORT"
echo ""

# Check if port exists
if [ ! -e "$PORT" ]; then
    echo "Error: Port $PORT not found"
    echo "Available ports:"
    ls -la /dev/ttyUSB* 2>/dev/null || ls -la /dev/ttyACM* 2>/dev/null || echo "  (none found)"
    exit 1
fi

echo "Step 1: Data Integrity Verification"
echo "--------------------------------------"
python3 verify_dma_integrity.py --port $PORT --bursts 5 --samples 2048
if [ $? -ne 0 ]; then
    echo "✗ Integrity test failed"
    exit 1
fi

echo ""
echo "Step 2: Full Pipeline Test"
echo "--------------------------------------"
python3 full_pipeline_test.py --port $PORT --focus 50 --plot quick_test_result.png
if [ $? -ne 0 ]; then
    echo "✗ Pipeline test failed"
    exit 1
fi

echo ""
echo "======================================================"
echo "All tests passed!"
echo "Result plot: quick_test_result.png"
echo "======================================================"
