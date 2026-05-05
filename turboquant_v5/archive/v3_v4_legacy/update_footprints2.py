#!/usr/bin/env python3
"""Update KiCad schematic with footprints - line by line approach"""

with open('red_pitaya_mux_board.kicad_sch', 'r') as f:
    lines = f.readlines()

# Map of positions to footprints for resistors
resistor_positions = [
    (80, 55), (80, 71), (80, 87), (80, 103), (80, 119), (80, 135), (80, 151), (80, 167),  # RG
    (85, 50), (85, 66), (85, 82), (85, 98), (85, 114), (85, 130), (85, 146), (85, 162),  # RPD
    (90, 63), (90, 79), (90, 95), (90, 111), (90, 127), (90, 143), (90, 159), (90, 175),  # RS (TX series - will handle separately)
    (148, 67), (148, 83), (148, 99), (148, 115), (148, 131), (148, 147), (148, 163), (148, 179),  # RM
    (210, 65), (210, 120), (215, 55), (215, 110),  # RF, RG (LNA)
    (160, 200), (175, 200),  # LED resistors
]

updated_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Check if this is an empty footprint line
    if '"Footprint" ""' in line:
        # Look ahead for the position
        pos_found = False
        for j in range(i+1, min(i+5, len(lines))):
            pos_line = lines[j]
            # Check for various component positions
            
            # Resistors at specific positions
            for x, y in resistor_positions:
                if f'(at {x} {y} 0)' in pos_line:
                    line = line.replace('"Footprint" ""', '"Footprint" "Resistor_SMD:R_0603_1608Metric"')
                    pos_found = True
                    break
            
            # MOSFETs Q1-Q8
            for y in [55, 71, 87, 103, 119, 135, 151, 167]:
                if f'(at 90 {y} 0)' in pos_line:
                    line = line.replace('"Footprint" ""', '"Footprint" "Package_TO_SOT_SMD:SOT-23"')
                    pos_found = True
                    break
            
            # Diodes D1-D8
            for y in [67, 83, 99, 115, 131, 147, 163, 179]:
                if f'(at 140 {y} 0)' in pos_line:
                    line = line.replace('"Footprint" ""', '"Footprint" "Package_TO_SOT_SMD:SOT-23"')
                    pos_found = True
                    break
            
            # Capacitors
            cap_positions = [
                (50, 190), (65, 190), (115, 190), (175, 55), (175, 110), (235, 75), (235, 130)  # 0603
            ]
            for x, y in cap_positions:
                if f'(at {x} {y} 0)' in pos_line:
                    line = line.replace('"Footprint" ""', '"Footprint" "Capacitor_SMD:C_0603_1608Metric"')
                    pos_found = True
                    break
            
            # 0805 capacitors
            cap_0805_positions = [(90, 190), (140, 190)]
            for x, y in cap_0805_positions:
                if f'(at {x} {y} 0)' in pos_line:
                    line = line.replace('"Footprint" ""', '"Footprint" "Capacitor_SMD:C_0805_2012Metric"')
                    pos_found = True
                    break
            
            # LEDs
            if '(at 165 200 0)' in pos_line or '(at 180 200 0)' in pos_line:
                line = line.replace('"Footprint" ""', '"Footprint" "LED_SMD:LED_0603_1608Metric"')
                pos_found = True
                break
            
            # 1N4007 diode
            if '(at 50 200 0)' in pos_line:
                line = line.replace('"Footprint" ""', '"Footprint" "Diode_SMD:D_SOD-123"')
                pos_found = True
                break
            
            # Connectors
            if '(at 30 100 0)' in pos_line:  # GPIO header
                line = line.replace('"Footprint" ""', '"Footprint" "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical"')
                pos_found = True
                break
            
            # SMA connectors
            sma_positions = [(30, 140), (40, 200), (120, 67), (120, 83), (120, 99), (120, 115), 
                           (120, 131), (120, 147), (120, 163), (120, 179), (250, 75), (250, 130)]
            for x, y in sma_positions:
                if f'(at {x} {y} 0)' in pos_line:
                    line = line.replace('"Footprint" ""', '"Footprint" "Connector_Coaxial:SMA_Amphenol_132134-11_Vertical"')
                    pos_found = True
                    break
            
            if pos_found:
                break
    
    updated_lines.append(line)
    i += 1

with open('red_pitaya_mux_board.kicad_sch', 'w') as f:
    f.writelines(updated_lines)

print("Footprints updated successfully!")
