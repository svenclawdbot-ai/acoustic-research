## Red Pitaya STEMlab 125-14 Pin Constraints

### E1 Connector (GPIO) Pin Mapping

Based on Red Pitaya documentation, the E1 connector provides:
- Digital I/O pins (FPGA GPIO)
- Power and ground

### Key FPGA Pins for E1 Connector:

| Pin | Function | Package Pin | Notes |
|-----|----------|-------------|-------|
| DIO0_N | Digital I/O 0 | G17 | Can be input or output |
| DIO0_P | Digital I/O 0 | G18 | Can be input or output |
| DIO1_N | Digital I/O 1 | H16 | Can be input or output |
| DIO1_P | Digital I/O 1 | H17 | Can be input or output |
| DIO2_N | Digital I/O 2 | J18 | Can be input or output |
| DIO2_P | Digital I/O 2 | H18 | Can be input or output |
| DIO3_N | Digital I/O 3 | K17 | Can be input or output |
| DIO3_P | Digital I/O 3 | K18 | Can be input or output |
| DIO4_N | Digital I/O 4 | L14 | Can be input or output |
| DIO4_P | Digital I/O 4 | L15 | Can be input or output |
| DIO5_N | Digital I/O 5 | L16 | Can be input or output |
| DIO5_P | Digital I/O 5 | L17 | Can be input or output |
| DIO6_N | Digital I/O 6 | K14 | Can be input or output |
| DIO6_P | Digital I/O 6 | K16 | Can be input or output |
| DIO7_N | Digital I/O 7 | M14 | Can be input or output |
| DIO7_P | Digital I/O 7 | M15 | Can be input or output |

### Other Important Pins:

| Pin | Function | Package Pin | Notes |
|-----|----------|-------------|-------|
| LED0 | LED 0 | F16 | Status LED |
| LED1 | LED 1 | F17 | Status LED |
| LED2 | LED 2 | G15 | Status LED |
| LED3 | LED 3 | H15 | Status LED |
| LED4 | LED 4 | K14 | Status LED |
| LED5 | LED 5 | G14 | Status LED |
| LED6 | LED 6 | J15 | Status LED |
| LED7 | LED 7 | J14 | Status LED |

### System Pins:

| Pin | Function | Package Pin | Notes |
|-----|----------|-------------|-------|
| CLK125 | 125 MHz Clock | U18 | Main system clock |
| RST | Reset | - | Active low |

### Recommended Pin Assignments for Beamformer:

For the 8-channel beamformer connecting to your mux board:

| Signal | Direction | Recommended Pin | E1 Pin |
|--------|-----------|-----------------|--------|
| ADC_DATA_0 | Input | DIO0_P (G18) | DIO0_P |
| ADC_DATA_1 | Input | DIO0_N (G17) | DIO0_N |
| ADC_DATA_2 | Input | DIO1_P (H17) | DIO1_P |
| ADC_DATA_3 | Input | DIO1_N (H16) | DIO1_N |
| ADC_DATA_4 | Input | DIO2_P (H18) | DIO2_P |
| ADC_DATA_5 | Input | DIO2_N (J18) | DIO2_N |
| ADC_DATA_6 | Input | DIO3_P (K18) | DIO3_P |
| ADC_DATA_7 | Input | DIO3_N (K17) | DIO3_N |
| SPI_SCK | Input | DIO4_P (L15) | DIO4_P |
| SPI_MOSI | Input | DIO4_N (L14) | DIO4_N |
| SPI_MISO | Output | DIO5_P (L17) | DIO5_P |
| SPI_CS_N | Input | DIO5_N (L16) | DIO5_N |

### Power and Ground:

| Pin | Function |
|-----|----------|
| +5V | 5V power supply |
| +3.3V | 3.3V power supply |
| GND | Ground |

### Next Steps:

1. Create the XDC constraints file with these pin assignments
2. Define I/O standards (LVCMOS33)
3. Add timing constraints (125 MHz clock)
4. Verify against your mux board schematic
