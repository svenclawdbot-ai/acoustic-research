#!/bin/bash
#============================================================================
# TurboQuant Shear Wave FPGA Synthesis Script
#============================================================================
# Synthesis script for Vivado targeting Red Pitaya STEMlab 125-14
#============================================================================

set -e

# Configuration
PROJECT_NAME="turboquant_shear_wave"
PART="xc7z010clg400-1"  # Zynq-7010 on Red Pitaya
TOP_MODULE="turboquant_shear_wave_top"

# Directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$SCRIPT_DIR"
OUT_DIR="$SCRIPT_DIR/../synthesis"

mkdir -p "$OUT_DIR"

echo "======================================================================"
echo "TurboQuant Shear Wave FPGA Synthesis"
echo "======================================================================"
echo "Source: $SRC_DIR"
echo "Output: $OUT_DIR"
echo "Part: $PART"
echo "======================================================================"

# Create Vivado Tcl script
cat > "$OUT_DIR/synth.tcl" << 'EOF'
# Vivado synthesis script
set_part xc7z010clg400-1

# Read source files
read_verilog {
    turboquant_controller.v
    shear_wave_controller.v
    turboquant_shear_wave_top.v
}

# Read constraints
read_xdc turboquant_shear_wave.xdc

# Synthesis
synth_design -top turboquant_shear_wave_top -part xc7z010clg400-1

# Optimization
opt_design

# Place and route
place_design
route_design

# Reports
report_utilization -file utilization.rpt
report_timing -file timing.rpt
report_power -file power.rpt

# Write bitstream
write_bitstream -force turboquant_shear_wave.bit

puts "Synthesis complete!"
puts "Bitstream: turboquant_shear_wave.bit"
EOF

echo ""
echo "Running Vivado synthesis..."
cd "$OUT_DIR"

# Check if Vivado is available
if command -v vivado &> /dev/null; then
    vivado -mode batch -source synth.tcl -log vivado.log -journal vivado.jou
    
    echo ""
    echo "======================================================================"
    echo "Synthesis Results"
    echo "======================================================================"
    
    if [ -f "turboquant_shear_wave.bit" ]; then
        echo "✓ Bitstream generated: turboquant_shear_wave.bit"
        ls -lh turboquant_shear_wave.bit
    else
        echo "✗ Bitstream not generated - check vivado.log"
    fi
    
    if [ -f "utilization.rpt" ]; then
        echo ""
        echo "Resource utilization:"
        grep -A 5 "Slice LUTs\|Slice Registers\|DSP\|BRAM" utilization.rpt || true
    fi
    
    if [ -f "timing.rpt" ]; then
        echo ""
        echo "Timing summary:"
        grep -A 3 "WNS\|TNS" timing.rpt | head -10 || true
    fi
    
else
    echo "ERROR: Vivado not found in PATH"
    echo "Please source Vivado settings script:"
    echo "  source /opt/Xilinx/Vivado/2022.2/settings64.sh"
    exit 1
fi

echo ""
echo "======================================================================"
echo "To program the Red Pitaya:"
echo "  1. Copy turboquant_shear_wave.bit to Red Pitaya"
echo "  2. Run: cat turboquant_shear_wave.bit > /dev/xdevcfg"
echo "======================================================================"
