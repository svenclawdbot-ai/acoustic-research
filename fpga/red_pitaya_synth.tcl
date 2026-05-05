# Red Pitaya Synthesis Script (Vivado)

# Create project
set project_name "red_pitaya_beamformer"
set project_dir "./vivado_project"

# Clean and create
file delete -force $project_dir
create_project $project_name $project_dir -part xc7z010clg400-1

# Add source files
add_files {beamformer_top.v delay_line.v spi_slave.v}
set_property top beamformer_top [current_fileset]

# Add constraints (create if not exists)
set constraints_file "red_pitaya.xdc"
if {![file exists $constraints_file]} {
    # Create basic constraints file
    set fp [open $constraints_file w]
    puts $fp "# Red Pitaya STEMlab 125-14 Constraints"
    puts $fp "# 125 MHz system clock"
    puts $fp "create_clock -period 8.000 -name clk [get_ports clk]"
    puts $fp ""
    puts $fp "# SPI interface"
    puts $fp "set_property PACKAGE_PIN G17 [get_ports spi_sck]"
    puts $fp "set_property PACKAGE_PIN H16 [get_ports spi_mosi]"
    puts $fp "set_property PACKAGE_PIN H17 [get_ports spi_miso]"
    puts $fp "set_property PACKAGE_PIN J18 [get_ports spi_cs_n]"
    puts $fp ""
    puts $fp "# ADC inputs (E1 connector - GPIO)"
    puts $fp "# Assign based on your mux board pinout"
    puts $fp ""
    puts $fp "# IOSTANDARD"
    puts $fp "set_property IOSTANDARD LVCMOS33 [get_ports *]"
    close $fp
}
add_files $constraints_file

# Run synthesis
puts "Running synthesis..."
synth_design -top beamformer_top -part xc7z010clg400-1

# Run implementation
puts "Running implementation..."
opt_design
place_design
route_design

# Generate bitstream
puts "Generating bitstream..."
write_bitstream -force red_pitaya_beamformer.bit

puts "Synthesis complete! Bitstream: red_pitaya_beamformer.bit"
puts "Load to Red Pitaya: cat red_pitaya_beamformer.bit > /dev/xdevcfg"

close_project