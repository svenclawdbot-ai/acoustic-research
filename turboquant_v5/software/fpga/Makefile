# Makefile for TurboQuant FPGA Controller

# Verilog sources (TurboQuant design)
SRCS = turboquant_top.v turboquant_controller.v
TB = tb_turboquant.v

# Simulation settings
SIM_TOP = tb_turboquant
VCD_FILE = turboquant.vcd

# Tools
IVERILOG = iverilog
VVP = vvp
GTKWAVE = gtkwave
VIVADO = vivado

.PHONY: all sim view synth clean

all: sim

# Compile and run simulation
sim:
	@echo "Compiling simulation..."
	$(IVERILOG) -o $(SIM_TOP).vvp -s $(SIM_TOP) $(SRCS) $(TB)
	@echo "Running simulation..."
	$(VVP) $(SIM_TOP).vvp

# View waveforms
view: sim
	$(GTKWAVE) $(VCD_FILE) &

# Synthesis for Red Pitaya (TurboQuant controller)
synth:
	@echo "Running Vivado synthesis for Red Pitaya..."
	$(VIVADO) -mode batch -source turboquant_synth.tcl

# Load to Red Pitaya (requires SSH access)
load:
	@echo "Loading bitstream to Red Pitaya..."
	scp red_pitaya_turboquant.bit root@red-pitaya:/tmp/
	ssh root@red-pitaya 'cat /tmp/red_pitaya_turboquant.bit > /dev/xdevcfg'

# Clean build artifacts
clean:
	rm -f *.vvp *.vcd
	rm -rf vivado_project/
	rm -f *.bit *.log *.jou

# Help
help:
	@echo "TurboQuant FPGA Controller Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  make sim    - Run Icarus Verilog simulation"
	@echo "  make view   - View waveforms with GTKWave"
	@echo "  make synth  - Synthesize for Red Pitaya (requires Vivado)"
	@echo "  make load   - Load bitstream to Red Pitaya"
	@echo "  make clean  - Remove build artifacts"
	@echo "  make help   - Show this help"
