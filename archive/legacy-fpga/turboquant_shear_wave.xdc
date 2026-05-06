#============================================================================
# TurboQuant Shear Wave Constraints
#============================================================================
# XDC constraints file for synthesis on Red Pitaya STEMlab 125-14
#============================================================================

# System clock (125 MHz from Red Pitaya)
set_property -dict {PACKAGE_PIN U18 IOSTANDARD LVCMOS33} [get_ports clk_125m]
create_clock -period 8.000 -name clk_125m [get_ports clk_125m]

# Reset (from Red Pitaya GPIO or button)
set_property -dict {PACKAGE_PIN F16 IOSTANDARD LVCMOS33} [get_ports rst_n]

#============================================================================
# Red Pitaya ADC (AD9613BCPZ-170)
#============================================================================
# ADC A channel
set_property -dict {PACKAGE_PIN Y17 IOSTANDARD LVCMOS33} [get_ports {adc_dat_a[0]}]
set_property -dict {PACKAGE_PIN W16 IOSTANDARD LVCMOS33} [get_ports {adc_dat_a[1]}]
set_property -dict {PACKAGE_PIN Y16 IOSTANDARD LVCMOS33} [get_ports {adc_dat_a[2]}]
set_property -dict {PACKAGE_PIN W15 IOSTANDARD LVCMOS33} [get_ports {adc_dat_a[3]}]
set_property -dict {PACKAGE_PIN W14 IOSTANDARD LVCMOS33} [get_ports {adc_dat_a[4]}]
set_property -dict {PACKAGE_PIN Y14 IOSTANDARD LVCMOS33} [get_ports {adc_dat_a[5]}]
set_property -dict {PACKAGE_PIN W13 IOSTANDARD LVCMOS33} [get_ports {adc_dat_a[6]}]
set_property -dict {PACKAGE_PIN V12 IOSTANDARD LVCMOS33} [get_ports {adc_dat_a[7]}]
set_property -dict {PACKAGE_PIN Y12 IOSTANDARD LVCMOS33} [get_ports {adc_dat_a[8]}]
set_property -dict {PACKAGE_PIN Y11 IOSTANDARD LVCMOS33} [get_ports {adc_dat_a[9]}]
set_property -dict {PACKAGE_PIN W11 IOSTANDARD LVCMOS33} [get_ports {adc_dat_a[10]}]
set_property -dict {PACKAGE_PIN V10 IOSTANDARD LVCMOS33} [get_ports {adc_dat_a[11]}]
set_property -dict {PACKAGE_PIN W10 IOSTANDARD LVCMOS33} [get_ports {adc_dat_a[12]}]
set_property -dict {PACKAGE_PIN V9 IOSTANDARD LVCMOS33} [get_ports {adc_dat_a[13]}]

# ADC B channel
set_property -dict {PACKAGE_PIN Y18 IOSTANDARD LVCMOS33} [get_ports {adc_dat_b[0]}]
set_property -dict {PACKAGE_PIN Y19 IOSTANDARD LVCMOS33} [get_ports {adc_dat_b[1]}]
set_property -dict {PACKAGE_PIN W18 IOSTANDARD LVCMOS33} [get_ports {adc_dat_b[2]}]
set_property -dict {PACKAGE_PIN V17 IOSTANDARD LVCMOS33} [get_ports {adc_dat_b[3]}]
set_property -dict {PACKAGE_PIN V18 IOSTANDARD LVCMOS33} [get_ports {adc_dat_b[4]}]
set_property -dict {PACKAGE_PIN V16 IOSTANDARD LVCMOS33} [get_ports {adc_dat_b[5]}]
set_property -dict {PACKAGE_PIN W17 IOSTANDARD LVCMOS33} [get_ports {adc_dat_b[6]}]
set_property -dict {PACKAGE_PIN V15 IOSTANDARD LVCMOS33} [get_ports {adc_dat_b[7]}]
set_property -dict {PACKAGE_PIN W12 IOSTANDARD LVCMOS33} [get_ports {adc_dat_b[8]}]
set_property -dict {PACKAGE_PIN V11 IOSTANDARD LVCMOS33} [get_ports {adc_dat_b[9]}]
set_property -dict {PACKAGE_PIN W8 IOSTANDARD LVCMOS33} [get_ports {adc_dat_b[10]}]
set_property -dict {PACKAGE_PIN V8 IOSTANDARD LVCMOS33} [get_ports {adc_dat_b[11]}]
set_property -dict {PACKAGE_PIN Y8 IOSTANDARD LVCMOS33} [get_ports {adc_dat_b[12]}]
set_property -dict {PACKAGE_PIN Y7 IOSTANDARD LVCMOS33} [get_ports {adc_dat_b[13]}]

# ADC clock
set_property -dict {PACKAGE_PIN U17 IOSTANDARD LVCMOS33} [get_ports adc_clk]
create_clock -period 8.000 -name adc_clk [get_ports adc_clk]

#============================================================================
# Red Pitaya DAC (AD9717BCPZ)
#============================================================================
# DAC A channel
set_property -dict {PACKAGE_PIN Y9 IOSTANDARD LVCMOS33} [get_ports {dac_dat_a[0]}]
set_property -dict {PACKAGE_PIN W9 IOSTANDARD LVCMOS33} [get_ports {dac_dat_a[1]}]
set_property -dict {PACKAGE_PIN Y6 IOSTANDARD LVCMOS33} [get_ports {dac_dat_a[2]}]
set_property -dict {PACKAGE_PIN Y5 IOSTANDARD LVCMOS33} [get_ports {dac_dat_a[3]}]
set_property -dict {PACKAGE_PIN W6 IOSTANDARD LVCMOS33} [get_ports {dac_dat_a[4]}]
set_property -dict {PACKAGE_PIN W5 IOSTANDARD LVCMOS33} [get_ports {dac_dat_a[5]}]
set_property -dict {PACKAGE_PIN U6 IOSTANDARD LVCMOS33} [get_ports {dac_dat_a[6]}]
set_property -dict {PACKAGE_PIN U5 IOSTANDARD LVCMOS33} [get_ports {dac_dat_a[7]}]
set_property -dict {PACKAGE_PIN W7 IOSTANDARD LVCMOS33} [get_ports {dac_dat_a[8]}]
set_property -dict {PACKAGE_PIN V7 IOSTANDARD LVCMOS33} [get_ports {dac_dat_a[9]}]
set_property -dict {PACKAGE_PIN U8 IOSTANDARD LVCMOS33} [get_ports {dac_dat_a[10]}]
set_property -dict {PACKAGE_PIN U7 IOSTANDARD LVCMOS33} [get_ports {dac_dat_a[11]}]
set_property -dict {PACKAGE_PIN U10 IOSTANDARD LVCMOS33} [get_ports {dac_dat_a[12]}]
set_property -dict {PACKAGE_PIN T9 IOSTANDARD LVCMOS33} [get_ports {dac_dat_a[13]}]

# DAC B channel
set_property -dict {PACKAGE_PIN Y4 IOSTANDARD LVCMOS33} [get_ports {dac_dat_b[0]}]
set_property -dict {PACKAGE_PIN Y3 IOSTANDARD LVCMOS33} [get_ports {dac_dat_b[1]}]
set_property -dict {PACKAGE_PIN W4 IOSTANDARD LVCMOS33} [get_ports {dac_dat_b[2]}]
set_property -dict {PACKAGE_PIN W3 IOSTANDARD LVCMOS33} [get_ports {dac_dat_b[3]}]
set_property -dict {PACKAGE_PIN V4 IOSTANDARD LVCMOS33} [get_ports {dac_dat_b[4]}]
set_property -dict {PACKAGE_PIN V3 IOSTANDARD LVCMOS33} [get_ports {dac_dat_b[5]}]
set_property -dict {PACKAGE_PIN U2 IOSTANDARD LVCMOS33} [get_ports {dac_dat_b[6]}]
set_property -dict {PACKAGE_PIN U1 IOSTANDARD LVCMOS33} [get_ports {dac_dat_b[7]}]
set_property -dict {PACKAGE_PIN T5 IOSTANDARD LVCMOS33} [get_ports {dac_dat_b[8]}]
set_property -dict {PACKAGE_PIN T4 IOSTANDARD LVCMOS33} [get_ports {dac_dat_b[9]}]
set_property -dict {PACKAGE_PIN T3 IOSTANDARD LVCMOS33} [get_ports {dac_dat_b[10]}]
set_property -dict {PACKAGE_PIN T2 IOSTANDARD LVCMOS33} [get_ports {dac_dat_b[11]}]
set_property -dict {PACKAGE_PIN T1 IOSTANDARD LVCMOS33} [get_ports {dac_dat_b[12]}]
set_property -dict {PACKAGE_PIN R3 IOSTANDARD LVCMOS33} [get_ports {dac_dat_b[13]}]

#============================================================================
# TurboQuant Board Interface (E1 connector - GPIO)
#============================================================================

# 74HC595 Shift Register
set_property -dict {PACKAGE_PIN G18 IOSTANDARD LVCMOS33} [get_ports ser]
set_property -dict {PACKAGE_PIN G17 IOSTANDARD LVCMOS33} [get_ports srclk]
set_property -dict {PACKAGE_PIN H17 IOSTANDARD LVCMOS33} [get_ports rclk]

# HV Pulser Gate
set_property -dict {PACKAGE_PIN H18 IOSTANDARD LVCMOS33} [get_ports pulser_gate]

#============================================================================
# Status LEDs
#============================================================================
set_property -dict {PACKAGE_PIN F16 IOSTANDARD LVCMOS33} [get_ports {led[0]}]
set_property -dict {PACKAGE_PIN F17 IOSTANDARD LVCMOS33} [get_ports {led[1]}]
set_property -dict {PACKAGE_PIN G15 IOSTANDARD LVCMOS33} [get_ports {led[2]}]
set_property -dict {PACKAGE_PIN H15 IOSTANDARD LVCMOS33} [get_ports {led[3]}]
set_property -dict {PACKAGE_PIN K14 IOSTANDARD LVCMOS33} [get_ports {led[4]}]
set_property -dict {PACKAGE_PIN G14 IOSTANDARD LVCMOS33} [get_ports {led[5]}]
set_property -dict {PACKAGE_PIN J15 IOSTANDARD LVCMOS33} [get_ports {led[6]}]
set_property -dict {PACKAGE_PIN J14 IOSTANDARD LVCMOS33} [get_ports {led[7]}]

#============================================================================
# Timing Constraints
#============================================================================

# Clock uncertainty
set_clock_uncertainty 0.100 [get_clocks clk_125m]

# False paths (async inputs)
set_false_path -from [get_ports rst_n]

# Output delay for shift register (1 MHz SPI)
set_output_delay -clock clk_125m -max 2.000 [get_ports {ser srclk rclk}]
set_output_delay -clock clk_125m -min -0.500 [get_ports {ser srclk rclk}]

# Pulser gate timing (relaxed, HV pulser is slow)
set_output_delay -clock clk_125m -max 5.000 [get_ports pulser_gate]
set_output_delay -clock clk_125m -min -2.000 [get_ports pulser_gate]

#============================================================================
# Configuration
#============================================================================

set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]
set_property BITSTREAM.CONFIG.CONFIGRATE 66 [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
set_property CFGBVS VCCO [current_design]
