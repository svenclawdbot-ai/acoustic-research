#!/usr/bin/env python3
import re

with open('/home/james/.openclaw/workspace/kicad/red_pitaya_mux_board/red_pitaya_mux_board.kicad_sch', 'r') as f:
    content = f.read()

# Fix the structure: move instances inside symbol blocks
# Pattern: symbol block ending with ) followed by whitespace and instances block
pattern = r'(\(symbol \(lib_id[^)]+\)[^)]+\)\s*\)\s*\n  \)\s*\n    \(instances'

# Replace with the correct structure
# Actually let's just rewrite the file properly

# Read line by line and fix structure
lines = content.split('\n')
output = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Check if this is the closing of a symbol block followed by instances
    if line.strip() == ')' and i + 1 < len(lines):
        # Check next few lines for instances
        next_content = '\n'.join(lines[i+1:i+4])
        if '(instances' in next_content and '(project' in next_content:
            # This is a misplaced closing paren, skip it
            # The instances block should be inside, not outside
            i += 1
            continue
    
    output.append(line)
    i += 1

content = '\n'.join(output)

# Now fix: we need to move instances BEFORE the closing ) of symbol
# Pattern: symbol ... (property "Footprint" ...)\n  )\n    (instances ...\n    )\n  )
# Should be: symbol ... (property "Footprint" ...)\n    (instances ...\n    )\n  )

# Find all symbol blocks and fix them
symbol_pattern = r'(\(symbol \(lib_id "([^"]+)"\).*?\(property "Footprint" "[^"]+".*?\)\s*\)\s*\n)(\s*\)\s*\n\s*\(instances.*?\n\s*\)\s*\n\s*\))'

def fix_symbol(match):
    before = match.group(1)
    instances_section = match.group(3)
    # Remove extra )\n at end of before and fix indentation
    before = before.rstrip()
    if before.endswith(')'):
        before = before[:-1].rstrip()
    
    # Fix instances indentation (should be 2 spaces, not 4)
    lines = instances_section.split('\n')
    fixed_lines = []
    for line in lines:
        if line.strip() == ')':
            fixed_lines.append('  )')
        elif '(instances' in line:
            fixed_lines.append('    (instances' + line.split('(instances')[1])
        elif '(project' in line or '(reference' in line or '(path' in line:
            fixed_lines.append('      ' + line.strip())
        else:
            fixed_lines.append(line)
    
    return before + '\n' + '\n'.join(fixed_lines)

content = re.sub(symbol_pattern, fix_symbol, content, flags=re.DOTALL)

with open('/home/james/.openclaw/workspace/kicad/red_pitaya_mux_board/red_pitaya_mux_board.kicad_sch', 'w') as f:
    f.write(content)

print("Fixed structure!")
