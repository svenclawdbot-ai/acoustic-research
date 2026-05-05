#!/usr/bin/env python3
import re

with open('/home/james/.openclaw/workspace/kicad/red_pitaya_mux_board/red_pitaya_mux_board.kicad_sch', 'r') as f:
    content = f.read()

# Fix: add missing closing ) before (instances
# The pattern is: (effects ...) hide)\n    (instances
# Should be: (effects ...) hide)\n    )\n    (instances

content = re.sub(
    r'(\(effects \(font \(size 1\.27 1\.27\)\) hide\)\s*\n)(\s*\(instances)',
    r'\1    )\n\2',
    content
)

with open('/home/james/.openclaw/workspace/kicad/red_pitaya_mux_board/red_pitaya_mux_board.kicad_sch', 'w') as f:
    f.write(content)

print("Fixed missing closing parentheses!")
