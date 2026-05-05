# Vivado Guide for TurboQuant Controller

Complete walkthrough for synthesizing the TurboQuant FPGA design on Red Pitaya STEMlab 125-14.

## Table of Contents

1. [Installation](#installation)
2. [Project Setup](#project-setup)
3. [Synthesis Flow](#synthesis-flow)
4. [TCL Scripting](#tcl-scripting)
5. [Troubleshooting](#troubleshooting)

---

## Installation

### Download Vivado

1. Go to https://www.xilinx.com/support/download.html
2. Download **Vivado Design Suite - HLx Editions**
3. Choose **Vivado HL WebPACK** (free for Zynq-7010)
4. Version 2023.2 or later recommended

### Installation Steps

```bash
# Make installer executable
chmod +x Xilinx_Unified_2023.2_1013_2256_Lin64.bin

# Run installer
sudo ./Xilinx_Unified_2023.2_1013_2256_Lin64.bin
```

**Select during install:**
- ✓ Vivado (not Vitis)
- ✓ Zynq-7000 devices (Z-7010, Z-7020)
- ✗ No Ultrascale (not needed)
- ✗ No Versal (not needed)

### License

WebPACK is free but requires license:
```bash
# Generate node-locked license at Xilinx.com
# Download .lic file
# Load in Vivado: Help → Manage License
```

---

## Project Setup

### Method 1: GUI (Recommended for beginners)

**Step 1: Create New Project**

```
File → New Project → Next
Project Name: red_pitaya_turboquant
Project Location: /home/james/projects/
☑ Create project subdirectory
```

**Step 2: Project Type**

```
☑ RTL Project
☑ Do not specify sources at this time
```

**Step 3: Default Part**

```
Parts → Zynq-7000 → xc7z010clg400-1
(Click this exact part number)
```

**Step 4: Add Sources**

```
Project Manager → Add Sources (left sidebar)

Add or Create Design Sources:
  ☑ Add Files
  → turboquant_top.v
  → turboquant_controller.v

Add or Create Constraints:
  ☑ Add Files
  → turboquant.xdc
```

**Step 5: Verify Hierarchy**

```
Sources → Design Sources
Should show:
  turboquant_top (top module)
    └── turboquant_controller
```

---

### Method 2: Batch Mode (Fast, repeatable)

Use the TCL script provided:

```bash
cd /home/james/.openclaw/workspace/fpga

# Option A: Command line
vivado -mode batch -source turboquant_synth.tcl

# Option B: GUI with TCL
vivado -source turboquant_synth.tcl
```

---

## Synthesis Flow

### Step-by-Step GUI Flow

**1. Run Synthesis**

```
Flow Navigator → Synthesis → Run Synthesis

Settings:
  Strategy: Flow_PerfOptimized_high
  ☑ Enable multi-threading (max 8)
```

**2. Review Results**

```
Project Summary → Synthesis
Check:
  - Utilization (should be <10% for this design)
  - Timing (WNS should be positive)
  - Warnings (ignore info/warnings, fix errors)
```

**3. Run Implementation**

```
Flow Navigator → Implementation → Run Implementation

Settings:
  Strategy: Performance_Explore
```

**4. Generate Bitstream**

```
Flow Navigator → Program and Debug → Generate Bitstream

Settings:
  ☑ Enable Bitstream compression
  ☑ Disable unused pins (pull-up)
```

**5. Export Hardware**

```
File → Export → Export Hardware
☑ Include bitstream
```

---

## Understanding the Reports

### Synthesis Report

Open: `red_pitaya_turboquant.runs/synth_1/turboquant_top_utilization_synth.rpt`

```
+----------------------------+------+-------+--------+-------+---------+
|          Site Type         | Used | Fixed | Prohibited | Available | Util% |
+----------------------------+------+-------+--------+-------+---------+
| Slice LUTs                 |  127 |     0 |          0 |     17600 |  0.72 |
|   LUT as Logic             |  127 |     0 |          0 |     17600 |  0.72 |
| Slice Registers            |  184 |     0 |          0 |     35200 |  0.52 |
|   Register as Flip Flop    |  184 |     0 |          0 |     35200 |  0.52 |
+----------------------------+------+-------+--------+-------+---------+
```

**Expected for TurboQuant:**
- LUTs: ~100-200 (<1%)
- FFs: ~150-250 (<1%)
- BRAM: 0
- DSP: 0

### Timing Report

Open: `red_pitaya_turboquant.runs/impl_1/turboquant_top_timing_summary_routed.rpt`

```
WNS (Worst Negative Slack): 5.234 ns
TNS (Total Negative Slack): 0.000 ns
WHS (Worst Hold Slack):    0.089 ns
```

**Good values:**
- WNS > 0 (positive = meets timing)
- TNS = 0 (no failing paths)
- WHS > 0

---

## TCL Scripting Deep Dive

### Understanding `turboquant_synth.tcl`

```tcl
# Set project name and device
set project_name "red_pitaya_turboquant"
set part_name "xc7z010clg400-1"

# Clean previous runs
file delete -force $project_dir

# Create project
create_project $project_name $project_dir -part $part_name

# Add Verilog sources
add_files [glob *.v]

# Set top module
set_property top turboquant_top [current_fileset]

# Add constraints
add_files turboquant.xdc

# Run synthesis
synth_design -top turboquant_top -part $part_name

# Run implementation
opt_design    ;# Optimize logic
place_design  ;# Place cells on chip
route_design  ;# Route connections

# Generate bitstream
write_bitstream -force red_pitaya_turboquant.bit
```

### Custom TCL Commands

```tcl
# Open existing project
open_project red_pitaya_turboquant.xpr

# Run specific steps
synth_design -top turboquant_top
launch_runs synth_1 -jobs 8

# View reports
report_utilization -file utilization.txt
report_timing_summary -file timing.txt

# Export for SDK/Vitis
write_hw_platform -fixed -force -file turboquant.xsa
```

---

## Advanced Topics

### 1. Multi-Threading

```tcl
# Use all CPU cores
set_param general.maxThreads 8
```

### 2. Incremental Compilation

```tcl
# Reuse previous implementation
read_checkpoint -incremental turboquant_top_routed.dcp
```

### 3. Area vs Speed

```tcl
# Optimize for area
synth_design -top turboquant_top -part $part_name -directive AreaOptimized_high

# Optimize for speed
synth_design -top turboquant_top -part $part_name -directive Performance_Explore
```

### 4. Debugging with ILA

Add Integrated Logic Analyzer for signal debugging:

```verilog
// In your Verilog
ila_0 your_instance_name (
    .clk(clk),                  // input wire clk
    .probe0(element_select),    // input wire [2:0]  probe0
    .probe1(current_pattern),   // input wire [7:0]  probe1
    .probe2(ser),               // input wire [0:0]  probe2
    .probe3(srclk),             // input wire [0:0]  probe3
    .probe4(rclk)               // input wire [0:0]  probe4
);
```

---

## Troubleshooting

### Common Issues

**Q: "No valid parts found"**
```
Solution: Install Zynq-7000 device support during Vivado install
Or: Tools → Manage IP Catalog → Update IP Catalog
```

**Q: "Timing constraints not met"**
```
Check: Review turboquant.xdc constraints
Fix: Increase clock period or optimize design
```

**Q: "I/O standard mismatch"**
```
Error: [DRC NSTD-1] Unspecified I/O Standard
Fix: Add to XDC: set_property IOSTANDARD LVCMOS33 [get_ports *]
```

**Q: "Unable to open /dev/mem"**
```
On Red Pitaya, run as root:
sudo python3 turboquant.py
```

### Useful Vivado Commands

```bash
# Open GUI from command line
vivado red_pitaya_turboquant.xpr

# Run with journal/log
vivado -log vivado.log -jou vivado.jou -source turboquant_synth.tcl

# Check Vivado version
vivado -version
```

---

## Loading to Red Pitaya

### Method 1: JTAG (Development)

```
Hardware Manager → Open Target → Auto Connect
Program Device → Select red_pitaya_turboquant.bit
```

### Method 2: SCP + xdevcfg (Production)

```bash
# Copy bitstream to Red Pitaya
scp red_pitaya_turboquant.bit root@192.168.1.100:/tmp/

# Load bitstream (on Red Pitaya)
ssh root@192.168.1.100 'cat /tmp/red_pitaya_turboquant.bit > /dev/xdevcfg'

# Verify loaded
cat /sys/devices/soc0/amba/f8007000.devcfg/prog_done
# Should return: 1
```

### Method 3: Boot from SD Card

```bash
# Copy to SD card boot partition
cp red_pitaya_turboquant.bit /media/boot/

# Rename to standard name
mv /media/boot/red_pitaya_turboquant.bit /media/boot/red_pitaya.bit

# On boot, Red Pitaya loads this automatically
```

---

## Next Steps

1. **Install Vivado** (if not done)
2. **Run synthesis** using the TCL script
3. **Check reports** for utilization and timing
4. **Load bitstream** to Red Pitaya
5. **Run Python script** to test

Need help with a specific step?