#!/usr/bin/env python3
"""Update KiCad schematic with footprints"""
import re

# Read file
with open('red_pitaya_mux_board.kicad_sch', 'r') as f:
    content = f.read()

# Define footprint mappings based on component positions
footprint_map = {
    # MOSFETs Q1-Q8 at specific positions
    '(at 90 55 0)': 'Package_TO_SOT_SMD:SOT-23',   # Q?
    '(at 90 71 0)': 'Package_TO_SOT_SMD:SOT-23',   # Q?
    '(at 90 87 0)': 'Package_TO_SOT_SMD:SOT-23',   # Q?
    '(at 90 103 0)': 'Package_TO_SOT_SMD:SOT-23',  # Q?
    '(at 90 119 0)': 'Package_TO_SOT_SMD:SOT-23',  # Q?
    '(at 90 135 0)': 'Package_TO_SOT_SMD:SOT-23',  # Q?
    '(at 90 151 0)': 'Package_TO_SOT_SMD:SOT-23',  # Q?
    '(at 90 167 0)': 'Package_TO_SOT_SMD:SOT-23',  # Q?
    
    # Diodes D1-D8 at specific positions  
    '(at 140 67 0)': 'Package_TO_SOT_SMD:SOT-23',   # D?
    '(at 140 83 0)': 'Package_TO_SOT_SMD:SOT-23',   # D?
    '(at 140 99 0)': 'Package_TO_SOT_SMD:SOT-23',   # D?
    '(at 140 115 0)': 'Package_TO_SOT_SMD:SOT-23',  # D?
    '(at 140 131 0)': 'Package_TO_SOT_SMD:SOT-23',  # D?
    '(at 140 147 0)': 'Package_TO_SOT_SMD:SOT-23',  # D?
    '(at 140 163 0)': 'Package_TO_SOT_SMD:SOT-23',  # D?
    '(at 140 179 0)': 'Package_TO_SOT_SMD:SOT-23',  # D?
    
    # Resistors (various positions)
    '(at 80 55 0)': 'Resistor_SMD:R_0603_1608Metric',   # RG?
    '(at 80 71 0)': 'Resistor_SMD:R_0603_1608Metric',   # RG?
    '(at 80 87 0)': 'Resistor_SMD:R_0603_1608Metric',   # RG?
    '(at 80 103 0)': 'Resistor_SMD:R_0603_1608Metric',  # RG?
    '(at 80 119 0)': 'Resistor_SMD:R_0603_1608Metric',  # RG?
    '(at 80 135 0)': 'Resistor_SMD:R_0603_1608Metric',  # RG?
    '(at 80 151 0)': 'Resistor_SMD:R_0603_1608Metric',  # RG?
    '(at 80 167 0)': 'Resistor_SMD:R_0603_1608Metric',  # RG?
    
    '(at 85 50 0)': 'Resistor_SMD:R_0603_1608Metric',   # RPD?
    '(at 85 66 0)': 'Resistor_SMD:R_0603_1608Metric',   # RPD?
    '(at 85 82 0)': 'Resistor_SMD:R_0603_1608Metric',   # RPD?
    '(at 85 98 0)': 'Resistor_SMD:R_0603_1608Metric',   # RPD?
    '(at 85 114 0)': 'Resistor_SMD:R_0603_1608Metric',  # RPD?
    '(at 85 130 0)': 'Resistor_SMD:R_0603_1608Metric',  # RPD?
    '(at 85 146 0)': 'Resistor_SMD:R_0603_1608Metric',  # RPD?
    '(at 85 162 0)': 'Resistor_SMD:R_0603_1608Metric',  # RPD?
    
    '(at 90 63 0)': 'Resistor_SMD:R_0603_1608Metric',   # RS?
    '(at 90 79 0)': 'Resistor_SMD:R_0603_1608Metric',   # RS?
    '(at 90 95 0)': 'Resistor_SMD:R_0603_1608Metric',   # RS?
    '(at 90 111 0)': 'Resistor_SMD:R_0603_1608Metric',  # RS?
    '(at 90 127 0)': 'Resistor_SMD:R_0603_1608Metric',  # RS?
    '(at 90 143 0)': 'Resistor_SMD:R_0603_1608Metric',  # RS?
    '(at 90 159 0)': 'Resistor_SMD:R_0603_1608Metric',  # RS?
    '(at 90 175 0)': 'Resistor_SMD:R_0603_1608Metric',  # RS?
    
    '(at 148 67 0)': 'Resistor_SMD:R_0603_1608Metric',  # RM?
    '(at 148 83 0)': 'Resistor_SMD:R_0603_1608Metric',  # RM?
    '(at 148 99 0)': 'Resistor_SMD:R_0603_1608Metric',  # RM?
    '(at 148 115 0)': 'Resistor_SMD:R_0603_1608Metric', # RM?
    '(at 148 131 0)': 'Resistor_SMD:R_0603_1608Metric', # RM?
    '(at 148 147 0)': 'Resistor_SMD:R_0603_1608Metric', # RM?
    '(at 148 163 0)': 'Resistor_SMD:R_0603_1608Metric', # RM?
    '(at 148 179 0)': 'Resistor_SMD:R_0603_1608Metric', # RM?
    
    '(at 210 65 0)': 'Resistor_SMD:R_0603_1608Metric',  # RF?
    '(at 210 120 0)': 'Resistor_SMD:R_0603_1608Metric', # RF?
    '(at 215 55 0)': 'Resistor_SMD:R_0603_1608Metric',  # RG?
    '(at 215 110 0)': 'Resistor_SMD:R_0603_1608Metric', # RG?
    
    '(at 160 200 0)': 'Resistor_SMD:R_0603_1608Metric', # RLED5V?
    '(at 175 200 0)': 'Resistor_SMD:R_0603_1608Metric', # RLED3V?
    
    # Capacitors
    '(at 50 190 0)': 'Capacitor_SMD:C_0603_1608Metric',   # CIN?
    '(at 65 190 0)': 'Capacitor_SMD:C_0603_1608Metric',   # C7805IN?
    '(at 90 190 0)': 'Capacitor_SMD:C_0805_2012Metric',   # C7805OUT?
    '(at 115 190 0)': 'Capacitor_SMD:C_0603_1608Metric',  # C1117IN?
    '(at 140 190 0)': 'Capacitor_SMD:C_0805_2012Metric',  # C1117OUT?
    '(at 175 55 0)': 'Capacitor_SMD:C_0603_1608Metric',   # CU?
    '(at 175 110 0)': 'Capacitor_SMD:C_0603_1608Metric',  # CU?
    '(at 235 75 0)': 'Capacitor_SMD:C_0603_1608Metric',   # CC?
    '(at 235 130 0)': 'Capacitor_SMD:C_0603_1608Metric',  # CC?
    
    # LEDs
    '(at 165 200 0)': 'LED_SMD:LED_0603_1608Metric',   # D5V?
    '(at 180 200 0)': 'LED_SMD:LED_0603_1608Metric',   # D3V?
    
    # 1N4007 diode
    '(at 50 200 0)': 'Diode_SMD:D_SOD-123',  # D?
    
    # Connectors
    '(at 30 100 0)': 'Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical',  # J1 GPIO
    '(at 30 140 0)': 'Connector_Coaxial:SMA_Amphenol_132134-11_Vertical',  # TX_IN
    '(at 40 200 0)': 'Connector_Coaxial:SMA_Amphenol_132134-11_Vertical',  # 12V_IN
}

# Pattern to match empty footprint with position
# This is a simplified approach - we look for the pattern and replace

for pos, footprint in footprint_map.items():
    # Create pattern to find empty footprint at this position
    old_pattern = f'"Footprint" ""\n\t\t\t(at {pos.split("(")[1].split(")")[0]}'
    new_pattern = f'"Footprint" "{footprint}"\n\t\t\t(at {pos.split("(")[1].split(")")[0]}'
    content = content.replace(old_pattern, new_pattern)

# Write updated content
with open('red_pitaya_mux_board.kicad_sch', 'w') as f:
    f.write(content)

print("Footprints updated!")
