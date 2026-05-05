## Constraint file for Red Pitaya STEMlab 125-14
## TurboQuant V5 Integration

## Clock (125 MHz differential)
set_property IOSTANDARD DIFF_SSTL15 [get_ports adc_clk_p_i]
set_property IOSTANDARD DIFF_SSTL15 [get_ports adc_clk_n_i]
set_property PACKAGE_PIN K9 [get_ports adc_clk_p_i]
set_property PACKAGE_PIN L9 [get_ports adc_clk_n_i]

## ADC0 (Channel 1 on Red Pitaya)
set_property IOSTANDARD LVCMOS18 [get_ports {adc_dat_a_i[*]}]
set_property PACKAGE_PIN M9 [get_ports {adc_dat_a_i[0]}]
set_property PACKAGE_PIN N9 [get_ports {adc_dat_a_i[1]}]
set_property PACKAGE_PIN P8 [get_ports {adc_dat_a_i[2]}]
set_property PACKAGE_PIN P9 [get_ports {adc_dat_a_i[3]}]
set_property PACKAGE_PIN T5 [get_ports {adc_dat_a_i[4]}]
set_property PACKAGE_PIN R5 [get_ports {adc_dat_a_i[5]}]
set_property PACKAGE_PIN N6 [get_ports {adc_dat_a_i[6]}]
set_property PACKAGE_PIN P6 [get_ports {adc_dat_a_i[7]}]
set_property PACKAGE_PIN R6 [get_ports {adc_dat_a_i[8]}]
set_property PACKAGE_PIN R7 [get_ports {adc_dat_a_i[9]}]
set_property PACKAGE_PIN T8 [get_ports {adc_dat_a_i[10]}]
set_property PACKAGE_PIN T9 [get_ports {adc_dat_a_i[11]}]
set_property PACKAGE_PIN M6 [get_ports {adc_dat_a_i[12]}]
set_property PACKAGE_PIN N7 [get_ports {adc_dat_a_i[13]}]

## ADC1 (Channel 2 on Red Pitaya - not used in V5)
set_property IOSTANDARD LVCMOS18 [get_ports {adc_dat_b_i[*]}]

## DAC0 (Channel 1 on Red Pitaya - source output)
set_property IOSTANDARD LVCMOS33 [get_ports {dac_dat_a_o[*]}]
set_property PACKAGE_PIN F8 [get_ports {dac_dat_a_o[0]}]
set_property PACKAGE_PIN E8 [get_ports {dac_dat_a_o[1]}]
set_property PACKAGE_PIN B8 [get_ports {dac_dat_a_o[2]}]
set_property PACKAGE_PIN A8 [get_ports {dac_dat_a_o[3]}]
set_property PACKAGE_PIN C8 [get_ports {dac_dat_a_o[4]}]
set_property PACKAGE_PIN C7 [get_ports {dac_dat_a_o[5]}]
set_property PACKAGE_PIN D7 [get_ports {dac_dat_a_o[6]}]
set_property PACKAGE_PIN A7 [get_ports {dac_dat_a_o[7]}]
set_property PACKAGE_PIN A6 [get_ports {dac_dat_a_o[8]}]
set_property PACKAGE_PIN B6 [get_ports {dac_dat_a_o[9]}]
set_property PACKAGE_PIN E6 [get_ports {dac_dat_a_o[10]}]
set_property PACKAGE_PIN E9 [get_ports {dac_dat_a_o[11]}]
set_property PACKAGE_PIN D6 [get_ports {dac_dat_a_o[12]}]
set_property PACKAGE_PIN D5 [get_ports {dac_dat_a_o[13]}]

## DAC1 (Channel 2 on Red Pitaya - not used in V5)
set_property IOSTANDARD LVCMOS33 [get_ports {dac_dat_b_o[*]}]

## GPIO (E1 connector) - MUX control
## DIO0_N (Pin 1)  -> S0 (MUX LSB)
## DIO0_P (Pin 2)  -> S1
## DIO1_N (Pin 3)  -> S2 (MUX MSB)
## DIO1_P (Pin 4)  -> /EN (active low)
set_property IOSTANDARD LVCMOS33 [get_ports {gpio_o[*]}]
set_property PACKAGE_PIN G17 [get_ports {gpio_o[0]}]  ;# DIO0_N -> S0
set_property PACKAGE_PIN H16 [get_ports {gpio_o[1]}]  ;# DIO0_P -> S1
set_property PACKAGE_PIN G18 [get_ports {gpio_o[2]}]  ;# DIO1_N -> S2
set_property PACKAGE_PIN H17 [get_ports {gpio_o[3]}]  ;# DIO1_P -> /EN

## Trigger output (to ADC trigger)
set_property IOSTANDARD LVCMOS33 [get_ports trigger_o]
set_property PACKAGE_PIN U17 [get_ports trigger_o]

## LED indicators
set_property IOSTANDARD LVCMOS33 [get_ports {led_o[*]}]
set_property PACKAGE_PIN F16 [get_ports {led_o[0]}]
set_property PACKAGE_PIN F17 [get_ports {led_o[1]}]
set_property PACKAGE_PIN G15 [get_ports {led_o[2]}]
set_property PACKAGE_PIN H15 [get_ports {led_o[3]}]
set_property PACKAGE_PIN K14 [get_ports {led_o[4]}]
set_property PACKAGE_PIN G14 [get_ports {led_o[5]}]
set_property PACKAGE_PIN J15 [get_ports {led_o[6]}]
set_property PACKAGE_PIN J16 [get_ports {led_o[7]}]

## Timing constraints
create_clock -period 8.000 -name adc_clk [get_ports adc_clk_p_i]

## False paths (async inputs)
set_false_path -from [get_ports {gpio_o[*]}]
set_false_path -to [get_ports {led_o[*]}]
