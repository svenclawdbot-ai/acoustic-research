#!/usr/bin/env python3
"""Update TX series resistors to 0 ohms (effectively removing them) - fixed version"""

with open('red_pitaya_mux_board.kicad_sch', 'r') as f:
    lines = f.readlines()

# TX series resistor positions (RS? components)
tx_resistor_y_positions = [63, 79, 95, 111, 127, 143, 159, 175]

updated_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Check if this line contains the position for a TX resistor
    for y in tx_resistor_y_positions:
        if f'(at 90 {y} 90)' in line:
            # Look for Value "100" in the next 20 lines and change to "0"
            for j in range(i, min(i+20, len(lines))):
                if '(property "Value" "100"' in lines[j]:
                    lines[j] = lines[j].replace('"100"', '"0"')
                    print(f"Updated resistor at y={y} to 0 ohms")
                    break
    
    updated_lines.append(line)
    i += 1

with open('red_pitaya_mux_board.kicad_sch', 'w') as f:
    f.writelines(updated_lines)

print("TX series resistors updated!")
