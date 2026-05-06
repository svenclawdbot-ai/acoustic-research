# Red Pitaya STEMlab 125-14 Constraints
# For 8-Channel Beamformer + Mux Board Interface
# Target: xc7z010clg400-1

#============================================================================
# System Clock
#============================================================================
# 125 MHz differential clock from Red Pitaya
set_property PACKAGE_PIN U18 [get_ports clk]
set_property IOSTANDARD LVCMOS33 [get_ports clk]

# Create clock constraint
create_clock -period 8.000 -name sys_clk [get_ports clk]

#============================================================================
# Reset
#============================================================================
# Using a GPIO pin for reset, or could use internal reset
# For now, we'll use an internal POR (Power-On Reset) in the FPGA logic
# If external reset needed, assign to one of the DIO pins

#============================================================================
# SPI Configuration Interface (E1 Connector - DIO4/DIO5)
#============================================================================
# SPI Clock (SCK)
set_property PACKAGE_PIN L15 [get_ports spi_sck]
set_property IOSTANDARD LVCMOS33 [get_ports spi_sck]

# SPI MOSI (Master Out Slave In)
set_property PACKAGE_PIN L14 [get_ports spi_mosi]
set_property IOSTANDARD LVCMOS33 [get_ports spi_mosi]

# SPI MISO (Master In Slave Out)
set_property PACKAGE_PIN L17 [get_ports spi_miso]
set_property IOSTANDARD LVCMOS33 [get_ports spi_miso]

# SPI Chip Select (Active Low)
set_property PACKAGE_PIN L16 [get_ports spi_cs_n]
set_property IOSTANDARD LVCMOS33 [get_ports spi_cs_n]

#============================================================================
# ADC Data Inputs (E1 Connector - DIO0 to DIO3)
# 8 channels from your mux board
#============================================================================

# Channel 0 (DIO0_P)
set_property PACKAGE_PIN G18 [get_ports adc_data_0]
set_property IOSTANDARD LVCMOS33 [get_ports adc_data_0]

# Channel 1 (DIO0_N)
set_property PACKAGE_PIN G17 [get_ports adc_data_1]
set_property IOSTANDARD LVCMOS33 [get_ports adc_data_1]

# Channel 2 (DIO1_P)
set_property PACKAGE_PIN H17 [get_ports adc_data_2]
set_property IOSTANDARD LVCMOS33 [get_ports adc_data_2]

# Channel 3 (DIO1_N)
set_property PACKAGE_PIN H16 [get_ports adc_data_3]
set_property IOSTANDARD LVCMOS33 [get_ports adc_data_3]

# Channel 4 (DIO2_P)
set_property PACKAGE_PIN H18 [get_ports adc_data_4]
set_property IOSTANDARD LVCMOS33 [get_ports adc_data_4]

# Channel 5 (DIO2_N)
set_property PACKAGE_PIN J18 [get_ports adc_data_5]
set_property IOSTANDARD LVCMOS33 [get_ports adc_data_5]

# Channel 6 (DIO3_P)
set_property PACKAGE_PIN K18 [get_ports adc_data_6]
set_property IOSTANDARD LVCMOS33 [get_ports adc_data_6]

# Channel 7 (DIO3_N)
set_property PACKAGE_PIN K17 [get_ports adc_data_7]
set_property IOSTANDARD LVCMOS33 [get_ports adc_data_7]

#============================================================================
# ADC Valid Signal (Optional - can use internal timing)
#============================================================================
# If your mux board provides a data valid strobe:
# set_property PACKAGE_PIN K16 [get_ports adc_valid]
# set_property IOSTANDARD LVCMOS33 [get_ports adc_valid]

#============================================================================
# Status LEDs (Optional - for debugging)
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

#============================================================================
# Timing Constraints
#============================================================================

# Input delay for ADC data (adjust based on your mux board timing)
# Assuming data is registered on the mux board and valid on clock edge
set_input_delay -clock sys_clk 2.0 [get_ports adc_data_*]

# Input delay for SPI (much slower, so generous)
set_input_delay -clock sys_clk 10.0 [get_ports spi_*]

# Output delay for SPI MISO
set_output_delay -clock sys_clk 5.0 [get_ports spi_miso]

#============================================================================
# False Paths (asynchronous inputs)
#============================================================================
# SPI signals are asynchronous to system clock until synchronized
set_false_path -from [get_ports spi_cs_n]

#============================================================================
# Configuration
#============================================================================
set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]
set_property BITSTREAM.CONFIG.UNUSEDPIN PULLUP [current_design]

#============================================================================
# Additional Constraints Notes
#============================================================================
# 
# 1. ADC_DATA signals:
#    - Your mux board should output 12-bit parallel data
#    - Data should be valid on rising edge of 125 MHz clock
#    - If using serial ADCs on mux board, add deserialization logic
#
# 2. SPI Interface:
#    - CPOL=0, CPHA=0 mode
#    - 16-bit transfers: [7:4] channel, [3:0] delay taps
#    - Max SPI clock: 10 MHz (limited by synchronization logic)
#
# 3. To modify for your specific mux board:
#    - Update pin assignments to match your KiCad schematic
#    - Adjust input delays based on actual signal propagation
#    - Add any additional control signals needed
#
# 4. LED outputs (optional):
#    - Connect to FPGA to show status
#    - LED0: System running
#    - LED1: SPI activity
#    - LED2: Data valid
#    - LED3: Error/overflow

