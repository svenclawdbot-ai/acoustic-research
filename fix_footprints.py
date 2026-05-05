#!/usr/bin/env python3
import re

# Read the schematic file
with open('/home/james/.openclaw/workspace/kicad/red_pitaya_mux_board/red_pitaya_mux_board.kicad_sch', 'r') as f:
    content = f.read()

# Footprint mappings
footprints = {
    '74HC595': 'Package_SO:SOIC-16_3.9x9.9mm_P1.27mm',
    'CD4051B': 'Package_SO:SOIC-16_3.9x9.9mm_P1.27mm', 
    'OPA657': 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',
    'BSS138': 'Package_TO_SOT_SMD:SOT-23',
    'BAV99': 'Package_TO_SOT_SMD:SOT-23',
    'LM7805': 'Package_TO_SOT_SMD:SOT-223-3_TabPin2',
    'AMS1117-3V3': 'Package_TO_SOT_SMD:SOT-223-3_TabPin2',
    'SMA': 'Connector_Coaxial:SMA_Amphenol_132134-11_Vertical',
    'Conn_2x10': 'Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical',
    'R': 'Resistor_SMD:R_0805_2012Metric',
    'C': 'Capacitor_SMD:C_0805_2012Metric'
}

# Replace empty footprints based on Value property
for comp, fp in footprints.items():
    pattern = rf'(\(symbol "{comp}".*?\(property "Value" "[^"]*".*?\(property "Footprint" ")"'
    replacement = rf'\1{fp}"'
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Write back
with open('/home/james/.openclaw/workspace/kicad/red_pitaya_mux_board/red_pitaya_mux_board.kicad_sch', 'w') as f:
    f.write(content)

print("Footprints assigned!")
