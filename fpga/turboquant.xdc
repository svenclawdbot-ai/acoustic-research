# TurboQuant Controller Constraints for Red Pitaya STEMlab 125-14
# Target: xc7z010clg400-1

#============================================================================
# System Clock
#============================================================================
# 125 MHz differential clock from Red Pitaya
set_property PACKAGE_PIN U18 [get_ports clk]
set_property IOSTANDARD LVCMOS33 [get_ports clk]

create_clock -period 8.000 -name sys_clk [get_ports clk]

#============================================================================
# Reset (optional - can use internal POR)
#============================================================================
# Using internal power-on reset, no external reset pin needed

#============================================================================
# TurboQuant 74HC595 Interface (E1 Connector - DIO0/DIO1)
#============================================================================

# SER - Serial Data (DIO0_P)
set_property PACKAGE_PIN G18 [get_ports ser]
set_property IOSTANDARD LVCMOS33 [get_ports ser]

# SRCLK - Shift Register Clock (DIO0_N)
set_property PACKAGE_PIN G17 [get_ports srclk]
set_property IOSTANDARD LVCMOS33 [get_ports srclk]

# RCLK - Latch Clock (DIO1_P)
set_property PACKAGE_PIN H17 [get_ports rclk]
set_property IOSTANDARD LVCMOS33 [get_ports rclk]

#============================================================================
# Host Interface (AXI or direct register - using simple inputs for now)
# These would connect to Red Pitaya's CPU interface
#============================================================================

# Element select (3-bit, from CPU/AXI)
# Using DIO1_N, DIO2_P, DIO2_N for now (can be changed to AXI interface)
set_property PACKAGE_PIN H16 [get_ports {element_select[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {element_select[0]}]

set_property PACKAGE_PIN H18 [get_ports {element_select[1]}]
set_property IOSTANDARD LVCMOS33 [get_ports {element_select[1]}]

set_property PACKAGE_PIN J18 [get_ports {element_select[2]}]
set_property IOSTANDARD LVCMOS33 [get_ports {element_select[2]}]

# Element valid trigger (DIO3_P)
set_property PACKAGE_PIN K18 [get_ports element_valid]
set_property IOSTANDARD LVCMOS33 [get_ports element_valid]

#============================================================================
# Status LEDs (Optional - using Red Pitaya onboard LEDs)
#============================================================================
# LED0 - Blue
set_property PACKAGE_PIN F16 [get_ports led0]
set_property IOSTANDARD LVCMOS33 [get_ports led0]

# LED1 - Green
set_property PACKAGE_PIN F17 [get_ports led1]
set_property IOSTANDARD LVCMOS33 [get_ports led1]

# LED2 - Yellow
set_property PACKAGE_PIN G15 [get_ports led2]
set_property IOSTANDARD LVCMOS33 [get_ports led2]

# LED3 - Red
set_property PACKAGE_PIN H15 [get_ports led3]
set_property IOSTANDARD LVCMOS33 [get_ports led3]

# LED4 - (using DIO3_N for now, or can use other LED)
set_property PACKAGE_PIN K17 [get_ports led4]
set_property IOSTANDARD LVCMOS33 [get_ports led4]

# LED5
set_property PACKAGE_PIN L14 [get_ports led5]
set_property IOSTANDARD LVCMOS33 [get_ports led5]

# LED6
set_property PACKAGE_PIN L15 [get_ports led6]
set_property IOSTANDARD LVCMOS33 [get_ports led6]

# LED7
set_property PACKAGE_PIN L16 [get_ports led7]
set_property IOSTANDARD LVCMOS33 [get_ports led7]

#============================================================================
# Timing Constraints
#============================================================================

# Input delays for element_select and element_valid
set_input_delay -clock sys_clk 5.0 [get_ports element_select*]
set_input_delay -clock sys_clk 5.0 [get_ports element_valid]

# Output delays for 74HC595 interface (1 MHz SPI, so generous timing)
set_output_delay -clock sys_clk 10.0 [get_ports ser]
set_output_delay -clock sys_clk 10.0 [get_ports srclk]
set_output_delay -clock sys_clk 10.0 [get_ports rclk]

#============================================================================
# Configuration
#============================================================================
set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]
set_property BITSTREAM.CONFIG.UNUSEDPIN PULLUP [current_design]

#============================================================================
# Note on Pin Assignments
#============================================================================
# 
# The element_select and element_valid pins are currently mapped to E1 GPIO
# for direct control from Red Pitaya's CPU GPIO.
#
# For production use, these should be connected via AXI interface from 
# the Zynq ARM processor instead of direct GPIO pins.
#
# SER, SRCLK, RCLK are the critical signals to the TurboQuant board.
# These drive the 74HC595 shift register at 1 MHz SPI clock.
