#!/usr/bin/env python3
"""Update TX series resistors to 0 ohms (effectively removing them)"""

with open('red_pitaya_mux_board.kicad_sch', 'r') as f:
    content = f.read()

# TX series resistor positions (RS? components)
tx_resistor_positions = [
    (90, 63), (90, 79), (90, 95), (90, 111),
    (90, 127), (90, 143), (90, 159), (90, 175)
]

for x, y in tx_resistor_positions:
    # Pattern to find RS? resistors with value 100 at these positions
    # and change them to 0
    old_pattern = f'(property "Value" "100"\n\t\t\t(at {x} {y} 90)'
    new_pattern = f'(property "Value" "0"\n\t\t\t(at {x} {y} 90)'
    content = content.replace(old_pattern, new_pattern)

with open('red_pitaya_mux_board.kicad_sch', 'w') as f:
    f.write(content)

print("TX series resistors changed to 0Ω (shorted)!")
