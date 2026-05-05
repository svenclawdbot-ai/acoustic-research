#!/usr/bin/env python3
import re

with open('/home/james/.openclaw/workspace/kicad/red_pitaya_mux_board/red_pitaya_mux_board.kicad_sch', 'r') as f:
    content = f.read()

# Map reference prefixes to footprints
footprint_map = {
    'U1': 'Package_SO:SOIC-16_3.9x9.9mm_P1.27mm',  # 74HC595
    'U2': 'Package_SO:SOIC-16_3.9x9.9mm_P1.27mm',  # CD4051B
    'U3': 'Package_SO:SOIC-16_3.9x9.9mm_P1.27mm',  # CD4051B
    'U4': 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',   # OPA657
    'U5': 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',   # OPA657
    'U6': 'Package_TO_SOT_SMD:SOT-223-3_TabPin2',  # LM7805
    'U7': 'Package_TO_SOT_SMD:SOT-223-3_TabPin2',  # AMS1117
    'Q': 'Package_TO_SOT_SMD:SOT-23',              # BSS138
    'D': 'Package_TO_SOT_SMD:SOT-23',              # BAV99
    'J': 'Connector_Coaxial:SMA_Amphenol_132134-11_Vertical',  # SMA
}

# Find all symbol instances and add footprint property after Value
pattern = r'(\(symbol \(lib_id "([^"]+)"\).*?\(property "Value" "([^"]+)".*?\)\n    \))(?!.*?\(property "Footprint")'

def add_footprint(match):
    full = match.group(1)
    lib_id = match.group(2)
    value = match.group(3)
    
    # Get reference from the full match
    ref_match = re.search(r'\(property "Reference" "([^"]+)"', full)
    ref = ref_match.group(1) if ref_match else ''
    
    # Determine footprint
    fp = None
    if ref.startswith('U') and ref in footprint_map:
        fp = footprint_map[ref]
    elif ref.startswith('Q'):
        fp = footprint_map['Q']
    elif ref.startswith('D'):
        fp = footprint_map['D']
    elif ref.startswith('J'):
        if ref == 'J1':
            fp = 'Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical'
        else:
            fp = footprint_map['J']
    
    if fp:
        # Add footprint property before the final closing
        new_prop = f'    (property "Footprint" "{fp}" (at 0 0 0)\n      (effects (font (size 1.27 1.27)) hide)\n    )\n  )'
        return full.rstrip()[:-1] + '\n' + new_prop
    return full

# Apply transformation
content = re.sub(pattern, add_footprint, content, flags=re.DOTALL)

with open('/home/james/.openclaw/workspace/kicad/red_pitaya_mux_board/red_pitaya_mux_board.kicad_sch', 'w') as f:
    f.write(content)

print("Added footprints to instances!")
