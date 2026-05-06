###############################################################################
# TurboQuant V5 FPGA Build Script
# ================================
#
# Complete Vivado build flow:
#   1. Create project
#   2. Add sources (BD, Verilog, XDC)  
#   3. Generate BD wrapper
#   4. Run synthesis
#   5. Run implementation
#   6. Generate bitstream + .bin for Red Pitaya
#
# Usage:
#   vivado -mode batch -source build_v5_bitstream.tcl
#
# Or in Vivado GUI:
#   source build_v5_bitstream.tcl
###############################################################################

# Configuration
set proj_name     "v5_acquisition"
set proj_dir      [pwd]/$proj_name
set fpga_dir      [file dirname [info script]]
set part          "xc7z010clg400-1"
set board_part    "em.avnet.com:red_pitaya:part0:1.0"

puts "========================================"
puts "TurboQuant V5 FPGA Build"
puts "========================================"
puts "Project: $proj_name"
puts "Part:    $part"
puts "Dir:     $proj_dir"
puts ""

# Step 1: Create project
puts "[1/7] Creating Vivado project..."
create_project $proj_name $proj_dir -part $part -force
set_property board_part $board_part [current_project]

# Step 1a: Check for Red Pitaya IP cores
puts "[1a/7] Checking Red Pitaya IP cores..."
set rp_cores_dir "$fpga_dir/red-pitaya-notes/cores"

if {![file exists $rp_cores_dir]} {
    puts "  Red Pitaya cores not found. Downloading..."
    exec git clone https://github.com/pavel-demin/red-pitaya-notes.git \
        $fpga_dir/red-pitaya-notes
    puts "  Download complete."
} else {
    puts "  Red Pitaya cores found."
}

# Add IP repository
set repo_paths [get_property ip_repo_paths [current_project]]
if {[lsearch -exact $repo_paths $rp_cores_dir] == -1} {
    lappend repo_paths $rp_cores_dir
    set_property ip_repo_paths $repo_paths [current_project]
    puts "  Added IP repo: $rp_cores_dir"
}

# Update IP catalog
update_ip_catalog -rebuild

# Step 2: Add Verilog sources
puts "[2/7] Adding Verilog sources..."
add_files -norecurse $fpga_dir/v5_mux_controller.v
set_property IS_GLOBAL_INCLUDE false [get_files v5_mux_controller.v]

# Step 3: Create block design
puts "[3/7] Creating block design..."
source $fpga_dir/v5_red_pitaya_bd.tcl

# Step 4: Add constraints
puts "[4/7] Adding constraints..."
add_files -fileset constrs_1 -norecurse $fpga_dir/v5_red_pitaya.xdc

# Step 5: Generate BD wrapper
puts "[5/7] Generating BD wrapper..."
make_wrapper -files [get_files $proj_dir/$proj_name.srcs/sources_1/bd/v5_acquisition/v5_acquisition.bd] -top
add_files -norecurse $proj_dir/$proj_name.srcs/sources_1/bd/v5_acquisition/hdl/v5_acquisition_wrapper.v
update_compile_order -fileset sources_1

# Step 6: Run synthesis
puts "[6/7] Running synthesis..."
launch_runs synth_1 -jobs 4
wait_on_run synth_1

set synth_status [get_property STATUS [get_runs synth_1]]
puts "Synthesis status: $synth_status"

if {$synth_status != "synth_design Complete!"} {
    puts "ERROR: Synthesis failed!"
    exit 1
}

# Step 7: Run implementation + bitstream
puts "[7/7] Running implementation and bitstream generation..."
launch_runs impl_1 -to_step write_bitstream -jobs 4
wait_on_run impl_1

set impl_status [get_property STATUS [get_runs impl_1]]
puts "Implementation status: $impl_status"

if {[string match "*Complete*" $impl_status]} {
    # Generate .bin file for Red Pitaya
    set bitstream_path $proj_dir/$proj_name.runs/impl_1/v5_acquisition_wrapper.bit
    set bin_path $proj_dir/$proj_name.runs/impl_1/v5_acquisition_wrapper.bin
    
    puts ""
    puts "========================================"
    puts "Build SUCCESS!"
    puts "========================================"
    puts "Bitstream: $bitstream_path"
    puts ""
    puts "To copy to Red Pitaya:"
    puts "  scp $bitstream_path root@192.168.1.100:/root/v5.bit"
    puts ""
    puts "To load on Red Pitaya:"
    puts "  cat /root/v5.bit > /dev/xdevcfg"
    puts ""
    puts "File sizes:"
    if {[file exists $bitstream_path]} {
        set bit_size [file size $bitstream_path]
        puts "  Bitstream: $bit_size bytes ([expr $bit_size / 1024] KB)"
    }
    puts "========================================"
} else {
    puts ""
    puts "========================================"
    puts "Build FAILED!"
    puts "Status: $impl_status"
    puts "Check logs in $proj_dir/$proj_name.runs/impl_1/"
    puts "========================================"
    exit 1
}

# Export hardware for SDK/Vitis if needed
write_hw_platform -fixed -force $proj_dir/v5_acquisition.xsa
puts ""
puts "Hardware platform exported: $proj_dir/v5_acquisition.xsa"

close_project
puts ""
puts "Done!"
