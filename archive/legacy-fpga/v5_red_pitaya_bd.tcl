###############################################################################
# Vivado Block Design Script for TurboQuant V5
# =================================================
# 
# Creates a complete Red Pitaya block design with:
# - ADC interface (axis_red_pitaya_adc)
# - DAC interface (axis_red_pitaya_dac)  
# - MUX controller (axi_gpio)
# - AXI DMA for data transfer to ARM
# - BRAM for DAC waveform storage
# - AXI Stream infrastructure
#
# Usage: Open Vivado, run: source v5_red_pitaya_bd.tcl
###############################################################################

# Create project
set proj_name "v5_acquisition"
set proj_dir [pwd]/$proj_name

create_project $proj_name $proj_dir -part xc7z010clg400-1

# Set board part (Red Pitaya STEMlab 125-14)
set_property board_part em.avnet.com:red_pitaya:part0:1.0 [current_project]

# Create block design
create_bd_design "v5_acquisition"

# ============================================================================
# 1. Zynq Processing System
# ============================================================================
create_bd_cell -type ip -vlnv xilinx.com:ip:processing_system7:5.5 processing_system7_0

# Configure Zynq (use board preset)
apply_bd_automation -rule xilinx.com:bd_rule:processing_system7 \
    -config {make_external "FIXED_IO, DDR" } \
    [get_bd_cells processing_system7_0]

# Enable HP0 AXI port (for DMA)
set_property -dict [list \
    CONFIG.PCW_USE_S_AXI_HP0 {1} \
    CONFIG.PCW_S_AXI_HP0_DATA_WIDTH {32} \
    CONFIG.PCW_USE_M_AXI_GP0 {1} \
] [get_bd_cells processing_system7_0]

# ============================================================================
# 2. Clock Generation (125 MHz from Red Pitaya oscillator)
# ============================================================================
create_bd_cell -type ip -vlnv xilinx.com:ip:clk_wiz:6.0 clk_wiz_0
set_property -dict [list \
    CONFIG.CLK_IN1_BOARD_INTERFACE {sys_diff_clock} \
    CONFIG.RESET_TYPE {ACTIVE_LOW} \
    CONFIG.CLKOUT1_REQUESTED_OUT_FREQ {125.000} \
    CONFIG.CLKOUT1_DRIVES {BUFG} \
    CONFIG.USE_LOCKED {false} \
    CONFIG.USE_RESET {false} \
] [get_bd_cells clk_wiz_0]

# ============================================================================
# 3. Red Pitaya ADC Interface
# ============================================================================
# Source from Pavel Demin's repo: github.com/pavel-demin/red-pitaya-notes
create_bd_cell -type ip -vlnv pavel-demin:user:axis_red_pitaya_adc:1.0 adc_0

# Configure ADC
set_property -dict [list \
    CONFIG.ADC_DATA_WIDTH {14} \
    CONFIG.AXIS_TDATA_WIDTH {32} \
] [get_bd_cells adc_0]

# ============================================================================
# 4. Red Pitaya DAC Interface  
# ============================================================================
create_bd_cell -type ip -vlnv pavel-demin:user:axis_red_pitaya_dac:1.0 dac_0

set_property -dict [list \
    CONFIG.DAC_DATA_WIDTH {14} \
    CONFIG.AXIS_TDATA_WIDTH {32} \
] [get_bd_cells dac_0]

# ============================================================================
# 5. AXI GPIO for MUX Control
# ============================================================================
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_gpio:2.0 gpio_mux
set_property -dict [list \
    CONFIG.C_GPIO_WIDTH {4} \
    CONFIG.C_ALL_OUTPUTS {1} \
    CONFIG.C_DOUT_DEFAULT {0x0000000F} \
] [get_bd_cells gpio_mux]

# GPIO bits: [3]=/EN (active low, default high=disabled), [2:0]=S2,S1,S0

# ============================================================================
# 6. AXI DMA (S2MM only — ADC to DDR)
# ============================================================================
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_dma:7.1 dma_0
set_property -dict [list \
    CONFIG.c_include_sg {0} \
    CONFIG.c_include_mm2s {0} \
    CONFIG.c_include_s2mm {1} \
    CONFIG.c_s2mm_burst_size {16} \
    CONFIG.c_sg_length_width {16} \
] [get_bd_cells dma_0]

# ============================================================================
# 7. AXI Stream Data FIFO (ADC buffer before DMA)
# ============================================================================
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_fifo_mm_s:4.2 axis_fifo_0
set_property -dict [list \
    CONFIG.C_USE_TX_DATA {0} \
    CONFIG.C_USE_TX_CTRL {0} \
    CONFIG.C_RX_FIFO_DEPTH {8192} \
    CONFIG.C_RX_FIFO_PF_THRESHOLD {8000} \
    CONFIG.C_USE_RX_CUT_THROUGH {1} \
    CONFIG.C_DATA_INTERFACE_TYPE {1} \
    CONFIG.C_AXI4_BASEADDR {0x43C10000} \
    CONFIG.C_AXI4_HIGHADDR {0x43C1FFFF} \
] [get_bd_cells axis_fifo_0]

# ============================================================================
# 8. BRAM Controller for DAC Waveform
# ============================================================================
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_bram_ctrl:4.1 bram_ctrl_0
set_property -dict [list \
    CONFIG.SINGLE_PORT_BRAM {1} \
    CONFIG.ECC_TYPE {0} \
] [get_bd_cells bram_ctrl_0]

create_bd_cell -type ip -vlnv xilinx.com:ip:blk_mem_gen:8.4 bram_dac
set_property -dict [list \
    CONFIG.Memory_Type {Single_Port_RAM} \
    CONFIG.Write_Width_A {32} \
    CONFIG.Write_Depth_A {8192} \
    CONFIG.Read_Width_A {32} \
    CONFIG.Operating_Mode_A {NO_CHANGE} \
    CONFIG.Enable_A {Always_Enabled} \
    CONFIG.Register_PortA_Output_of_Memory_Primitives {true} \
] [get_bd_cells bram_dac]

# ============================================================================
# 9. AXI Interconnect
# ============================================================================
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_interconnect:2.1 axi_interconnect_0
set_property -dict [list \
    CONFIG.NUM_MI {4} \
] [get_bd_cells axi_interconnect_0]

# ============================================================================
# 10. AXI Protocol Converter (for HP0 64-bit)
# ============================================================================
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_protocol_converter:2.1 axi_pc_0

# ============================================================================
# 11. AXI Stream Interconnect
# ============================================================================
create_bd_cell -type ip -vlnv xilinx.com:ip:axis_interconnect:2.1 axis_interconnect_0
set_property -dict [list \
    CONFIG.NUM_MI {1} \
    CONFIG.NUM_SI {1} \
] [get_bd_cells axis_interconnect_0]

# ============================================================================
# Connections
# ============================================================================

# Clock
connect_bd_net [get_bd_pins clk_wiz_0/clk_out1] \
    [get_bd_pins adc_0/adc_clk] \
    [get_bd_pins dac_0/dac_clk] \
    [get_bd_pins axis_fifo_0/s_axi_aclk] \
    [get_bd_pins axis_fifo_0/axi_str_txd_aclk] \
    [get_bd_pins dma_0/m_axi_s2mm_aclk] \
    [get_bd_pins dma_0/s_axi_lite_aclk] \
    [get_bd_pins bram_ctrl_0/s_axi_aclk] \
    [get_bd_pins axi_interconnect_0/ACLK] \
    [get_bd_pins axi_interconnect_0/M00_ACLK] \
    [get_bd_pins axi_interconnect_0/M01_ACLK] \
    [get_bd_pins axi_interconnect_0/M02_ACLK] \
    [get_bd_pins axi_interconnect_0/M03_ACLK] \
    [get_bd_pins axi_interconnect_0/S00_ACLK] \
    [get_bd_pins axi_pc_0/aclk]

# Reset
connect_bd_net [get_bd_pins processing_system7_0/FCLK_RESET0_N] \
    [get_bd_pins adc_0/adc_rstn] \
    [get_bd_pins dac_0/dac_rstn] \
    [get_bd_pins axis_fifo_0/s_axi_aresetn] \
    [get_bd_pins dma_0/axi_resetn] \
    [get_bd_pins bram_ctrl_0/s_axi_aresetn] \
    [get_bd_pins axi_interconnect_0/ARESETN] \
    [get_bd_pins axi_interconnect_0/M00_ARESETN] \
    [get_bd_pins axi_interconnect_0/M01_ARESETN] \
    [get_bd_pins axi_interconnect_0/M02_ARESETN] \
    [get_bd_pins axi_interconnect_0/M03_ARESETN] \
    [get_bd_pins axi_interconnect_0/S00_ARESETN] \
    [get_bd_pins axi_pc_0/aresetn]

# ADC → AXIS FIFO
connect_bd_intf_net [get_bd_intf_pins adc_0/M_AXIS] \
    [get_bd_intf_pins axis_interconnect_0/S00_AXIS]

connect_bd_intf_net [get_bd_intf_pins axis_interconnect_0/M00_AXIS] \
    [get_bd_intf_pins axis_fifo_0/AXI_STR_RXD]

# FIFO → DMA
connect_bd_intf_net [get_bd_intf_pins axis_fifo_0/AXI_STR_TXD] \
    [get_bd_intf_pins dma_0/S_AXIS_S2MM]

# BRAM → DAC
connect_bd_intf_net [get_bd_intf_pins bram_ctrl_0/BRAM_PORTA] \
    [get_bd_intf_pins bram_dac/BRAM_PORTA]

# BRAM → AXIS (for DAC — needs custom adapter, simplified here)
# In practice, add an AXI Stream BRAM reader

# AXI Interconnect → Peripherals
connect_bd_intf_net [get_bd_intf_pins axi_interconnect_0/M00_AXI] \
    [get_bd_intf_pins gpio_mux/S_AXI]

connect_bd_intf_net [get_bd_intf_pins axi_interconnect_0/M01_AXI] \
    [get_bd_intf_pins dma_0/S_AXI_LITE]

connect_bd_intf_net [get_bd_intf_pins axi_interconnect_0/M02_AXI] \
    [get_bd_intf_pins axis_fifo_0/S_AXI]

connect_bd_intf_net [get_bd_intf_pins axi_interconnect_0/M03_AXI] \
    [get_bd_intf_pins bram_ctrl_0/S_AXI]

# PS → AXI Interconnect
connect_bd_intf_net [get_bd_intf_pins processing_system7_0/M_AXI_GP0] \
    [get_bd_intf_pins axi_interconnect_0/S00_AXI]

# DMA → HP0 (via protocol converter)
connect_bd_intf_net [get_bd_intf_pins dma_0/M_AXI_S2MM] \
    [get_bd_intf_pins axi_pc_0/S_AXI]

connect_bd_intf_net [get_bd_intf_pins axi_pc_0/M_AXI] \
    [get_bd_intf_pins processing_system7_0/S_AXI_HP0]

# ============================================================================
# Address Map
# ============================================================================
create_bd_addr_seg -range 0x00010000 -offset 0x43C00000 \
    [get_bd_addr_spaces processing_system7_0/Data] \
    [get_bd_addr_segs gpio_mux/S_AXI/Reg] \
    SEG_gpio_mux_Reg

create_bd_addr_seg -range 0x00010000 -offset 0x43C10000 \
    [get_bd_addr_spaces processing_system7_0/Data] \
    [get_bd_addr_segs dma_0/S_AXI_LITE/Reg] \
    SEG_dma_0_Reg

create_bd_addr_seg -range 0x00010000 -offset 0x43C20000 \
    [get_bd_addr_spaces processing_system7_0/Data] \
    [get_bd_addr_segs axis_fifo_0/S_AXI/Mem0] \
    SEG_axis_fifo_0_Mem0

create_bd_addr_seg -range 0x00008000 -offset 0x43C30000 \
    [get_bd_addr_spaces processing_system7_0/Data] \
    [get_bd_addr_segs bram_ctrl_0/S_AXI/Mem0] \
    SEG_bram_ctrl_0_Mem0

# DMA scatter-gather (not used, but map for completeness)
create_bd_addr_seg -range 0x20000000 -offset 0x00000000 \
    [get_bd_addr_spaces dma_0/Data_S2MM] \
    [get_bd_addr_segs processing_system7_0/S_AXI_HP0/HP0_DDR_LOWOCM] \
    SEG_processing_system7_0_HP0_DDR_LOWOCM

# ============================================================================
# Validate and Save
# ============================================================================
validate_bd_design
save_bd_design

# Generate wrapper
make_wrapper -files [get_files $proj_dir/$proj_name.srcs/sources_1/bd/v5_acquisition/v5_acquisition.bd] -top
add_files -norecurse $proj_dir/$proj_name.srcs/sources_1/bd/v5_acquisition/hdl/v5_acquisition_wrapper.v

puts "Block design created successfully!"
puts "Next steps:"
puts "  1. Add constraints file (xdc) for pin mappings"
puts "  2. Run synthesis and implementation"
puts "  3. Generate bitstream"
puts "  4. Export hardware to SDK/Vitis"
