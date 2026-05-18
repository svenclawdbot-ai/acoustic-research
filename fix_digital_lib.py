#!/usr/bin/env python3
"""Remove broken lib_symbols from digital.kicad_sch so KiCad uses standard libraries."""

path = "/home/james/.openclaw/workspace/turboquant_v5/hardware/schematics/digital.kicad_sch"

with open(path, 'r') as f:
    text = f.read()

# Find the lib_symbols block and remove it entirely
lib_start = text.find('  (lib_symbols\n')
hier_start = text.find('  \n  ; Hierarchical')

if lib_start == -1 or hier_start == -1:
    print(f"Could not find lib_symbols block: start={lib_start}, hier={hier_start}")
    exit(1)

# Remove lib_symbols block, keeping the hierarchical labels section
new_text = text[:lib_start] + text[hier_start+1:]

with open(path, 'w') as f:
    f.write(new_text)

print(f"Removed lib_symbols block ({lib_start}-{hier_start}). File saved.")

# Verify balance
import uuid as uuid_mod

def balanced(t):
    depth = 0
    in_string = False
    escape = False
    for c in t:
        if escape:
            escape = False
            continue
        if c == '\\':
            escape = True
            continue
        if c == '"' and not in_string:
            in_string = True
            continue
        if c == '"' and in_string:
            in_string = False
            continue
        if in_string:
            continue
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
        if depth < 0:
            return False, depth
    return True, depth

ok, depth = balanced(new_text)
print(f"File balanced={ok}, depth={depth}")
