#!/bin/bash
# Quick simulation script

echo "Beamformer Simulation"
echo "===================="
echo ""

# Check for iverilog
if ! command -v iverilog &> /dev/null; then
    echo "ERROR: Icarus Verilog not found. Install with:"
    echo "  sudo apt-get install iverilog"
    exit 1
fi

echo "Compiling..."
iverilog -o tb_beamformer.vvp -s tb_beamformer \
    beamformer_top.v \
    delay_line.v \
    spi_slave.v \
    tb_beamformer.v

if [ $? -ne 0 ]; then
    echo "Compilation failed!"
    exit 1
fi

echo "Running simulation..."
vvp tb_beamformer.vvp

if command -v gtkwave &> /dev/null; then
    echo ""
    read -p "Open GTKWave? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gtkwave beamformer.vcd &
    fi
fi