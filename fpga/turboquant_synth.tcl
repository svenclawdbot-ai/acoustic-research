# Red Pitaya Synthesis Script for TurboQuant Controller (Vivado)

# Create project
set project_name "red_pitaya_turboquant"
set project_dir "./vivado_project"

# Clean and create
file delete -force $project_dir
create_project $project_name $project_dir -part xc7z010clg400-1

# Add source files
add_files {turboquant_top.v turboquant_controller.v}
set_property top turboquant_top [current_fileset]

# Add constraints
add_files turboquant.xdc

# Run synthesis
puts "Running synthesis..."
synth_design -top turboquant_top -part xc7z010clg400-1

# Run implementation
puts "Running implementation..."
opt_design
place_design
route_design

# Generate bitstream
puts "Generating bitstream..."
write_bitstream -force red_pitaya_turboquant.bit

puts "Synthesis complete! Bitstream: red_pitaya_turboquant.bit"
puts "Load to Red Pitaya: cat red_pitaya_turboquant.bit > /dev/xdevcfg"

close_project
