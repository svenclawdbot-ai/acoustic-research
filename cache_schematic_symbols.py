#!/usr/bin/env python3
"""
cache_schematic_symbols.py
Extracts symbols from KiCad standard libraries and injects them into schematic files.
Creates minimal symbols for missing ones.
"""

import os, re

BASE = "/home/james/.openclaw/workspace/turboquant_v5/hardware/schematics"
KICAD_LIBS = "/usr/share/kicad/symbols"
CUSTOM_LIB = os.path.join(BASE, "turboquant_library.kicad_sym")

# =============================================================================
# Extract symbol from a .kicad_sym file
# =============================================================================

def extract_symbol_from_lib(lib_path, symbol_name):
    """Extract a (symbol ...) block from a .kicad_sym file."""
    with open(lib_path, 'r') as f:
        text = f.read()
    
    # Find the symbol block
    pattern = rf'\(symbol "{re.escape(symbol_name)}"'
    match = re.search(pattern, text)
    if not match:
        return None
    
    start = match.start()
    
    # Find the matching close paren
    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        c = text[i]
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
        if depth == 0:
            end = i + 1
            break
    else:
        end = len(text)
    
    return text[start:end]

# =============================================================================
# Create minimal symbols for missing components
# =============================================================================

def make_minimal_dg408():
    """Minimal DG408 symbol with correct pinout."""
    return '''(symbol "Analog_Switch:DG408" (in_bom yes) (on_board yes)
    (property "Reference" "U" (at 0 10.16 0) (effects (font (size 1.27 1.27))))
    (property "Value" "DG408" (at 0 -10.16 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (symbol "DG408_0_0"
      (rectangle (start -5.08 -7.62) (end 5.08 7.62) (stroke (width 0.254)) (fill (type background))))
    (symbol "DG408_1_1"
      (pin passive line (at -7.62 6.35 0) (length 2.54) (name "S1" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27))))))
      (pin passive line (at -7.62 4.445 0) (length 2.54) (name "S2" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27))))))
      (pin passive line (at -7.62 2.54 0) (length 2.54) (name "S3" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27))))))
      (pin passive line (at -7.62 0.635 0) (length 2.54) (name "S4" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27))))))
      (pin passive line (at -7.62 -1.27 0) (length 2.54) (name "S5" (effects (font (size 1.27 1.27)))) (number "5" (effects (font (size 1.27 1.27))))))
      (pin passive line (at -7.62 -3.175 0) (length 2.54) (name "S6" (effects (font (size 1.27 1.27)))) (number "6" (effects (font (size 1.27 1.27))))))
      (pin passive line (at -7.62 -5.08 0) (length 2.54) (name "S7" (effects (font (size 1.27 1.27)))) (number "7" (effects (font (size 1.27 1.27))))))
      (pin passive line (at -7.62 -6.985 0) (length 2.54) (name "S8" (effects (font (size 1.27 1.27)))) (number "8" (effects (font (size 1.27 1.27))))))
      (pin power_in line (at -1.27 -10.16 90) (length 2.54) (name "GND" (effects (font (size 1.27 1.27)))) (number "9" (effects (font (size 1.27 1.27))))))
      (pin input line (at 7.62 -6.985 180) (length 2.54) (name "EN" (effects (font (size 1.27 1.27)))) (number "10" (effects (font (size 1.27 1.27))))))
      (pin input line (at 7.62 -5.08 180) (length 2.54) (name "A" (effects (font (size 1.27 1.27)))) (number "11" (effects (font (size 1.27 1.27))))))
      (pin input line (at 7.62 -3.175 180) (length 2.54) (name "B" (effects (font (size 1.27 1.27)))) (number "12" (effects (font (size 1.27 1.27))))))
      (pin input line (at 7.62 -1.27 180) (length 2.54) (name "C" (effects (font (size 1.27 1.27)))) (number "13" (effects (font (size 1.27 1.27))))))
      (pin passive line (at 7.62 0.635 180) (length 2.54) (name "X" (effects (font (size 1.27 1.27)))) (number "14" (effects (font (size 1.27 1.27))))))
      (pin power_in line (at 7.62 2.54 180) (length 2.54) (name "V-" (effects (font (size 1.27 1.27)))) (number "15" (effects (font (size 1.27 1.27))))))
      (pin power_in line (at 7.62 4.445 180) (length 2.54) (name "V+" (effects (font (size 1.27 1.27)))) (number "16" (effects (font (size 1.27 1.27))))))
    )
  )'''

def make_minimal_irf830():
    return '''(symbol "Transistor_FET:IRF830" (in_bom yes) (on_board yes)
    (property "Reference" "Q" (at 0 3.81 0) (effects (font (size 1.27 1.27))))
    (property "Value" "IRF830" (at 0 -3.81 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_TO_SOT_THT:TO-220F-3_Vertical" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (symbol "IRF830_0_1"
      (circle (center 0 0) (radius 2.54) (stroke (width 0.254)) (fill (type none))))
    (symbol "IRF830_1_1"
      (pin passive line (at 0 5.08 270) (length 2.54) (name "D" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27))))))
      (pin input line (at -2.54 0 0) (length 2.54) (name "G" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27))))))
      (pin passive line (at 0 -5.08 90) (length 2.54) (name "S" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27))))))
    )
  )'''

def make_minimal_tc4427():
    return '''(symbol "Driver_FET:TC4427" (in_bom yes) (on_board yes)
    (property "Reference" "U" (at 0 5.08 0) (effects (font (size 1.27 1.27))))
    (property "Value" "TC4427" (at 0 -5.08 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (symbol "TC4427_0_0"
      (rectangle (start -3.81 -3.81) (end 3.81 3.81) (stroke (width 0.254)) (fill (type background))))
    (symbol "TC4427_1_1"
      (pin input line (at -6.35 2.54 0) (length 2.54) (name "A_in" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27))))))
      (pin power_in line (at -3.81 -6.35 90) (length 2.54) (name "GND" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27))))))
      (pin output line (at 6.35 2.54 180) (length 2.54) (name "A_out" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27))))))
      (pin power_in line (at 0 6.35 270) (length 2.54) (name "VDD" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27))))))
      (pin output line (at 6.35 0 180) (length 2.54) (name "B_out" (effects (font (size 1.27 1.27)))) (number "5" (effects (font (size 1.27 1.27))))))
      (pin power_in line (at 3.81 -6.35 90) (length 2.54) (name "GND" (effects (font (size 1.27 1.27)))) (number "6" (effects (font (size 1.27 1.27))))))
      (pin input line (at -6.35 0 0) (length 2.54) (name "B_in" (effects (font (size 1.27 1.27)))) (number "7" (effects (font (size 1.27 1.27))))))
      (pin no_connect line (at -6.35 -2.54 0) (length 2.54) (name "NC" (effects (font (size 1.27 1.27)))) (number "8" (effects (font (size 1.27 1.27))))))
    )
  )'''

def make_minimal_diode():
    return '''(symbol "Device:D" (in_bom yes) (on_board yes)
    (property "Reference" "D" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
    (property "Value" "D" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Diode_SMD:D_SMA" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (symbol "D_0_1"
      (polyline (pts (xy -1.27 -1.27) (xy -1.27 1.27)) (stroke (width 0.254)) (fill (type none)))
      (polyline (pts (xy 1.27 -1.27) (xy 1.27 1.27)) (stroke (width 0.254)) (fill (type none)))
      (polyline (pts (xy -1.27 0) (xy 1.27 0)) (stroke (width 0.254)) (fill (type none)))
      (polyline (pts (xy -1.27 -1.27) (xy 0 -1.27)) (stroke (width 0.254)) (fill (type none))))
    (symbol "D_1_1"
      (pin passive line (at -3.81 0 0) (length 2.54) (name "A" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27))))))
      (pin passive line (at 3.81 0 180) (length 2.54) (name "K" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27))))))
    )
  )'''

def make_minimal_zener():
    return '''(symbol "Device:D_Zener" (in_bom yes) (on_board yes)
    (property "Reference" "Z" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
    (property "Value" "D_Zener" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Diode_SMD:D_SOD-323" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (symbol "D_Zener_0_1"
      (polyline (pts (xy -1.27 -1.27) (xy -1.27 1.27)) (stroke (width 0.254)) (fill (type none)))
      (polyline (pts (xy 1.27 -1.27) (xy 1.27 1.27)) (stroke (width 0.254)) (fill (type none)))
      (polyline (pts (xy -1.27 0) (xy 1.27 0)) (stroke (width 0.254)) (fill (type none)))
      (polyline (pts (xy 1.27 -1.27) (xy 0 -1.27)) (stroke (width 0.254)) (fill (type none))))
    (symbol "D_Zener_1_1"
      (pin passive line (at -3.81 0 0) (length 2.54) (name "A" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27))))))
      (pin passive line (at 3.81 0 180) (length 2.54) (name "K" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27))))))
    )
  )'''

# =============================================================================
# Build symbol cache for each sheet
# =============================================================================

SYMBOL_SOURCES = {
    # Sheet -> list of (lib_id, source_func_or_lib_path, symbol_name_in_lib)
    "analog.kicad_sch": [
        ("Analog_Switch:DG408", "custom", make_minimal_dg408),
        ("Amplifier_Operational:OPA1641", os.path.join(KICAD_LIBS, "Amplifier_Operational.kicad_sym"), "OPA1641"),
        ("Device:D", "custom", make_minimal_diode),
        ("Device:D_Zener", "custom", make_minimal_zener),
        ("Device:R", CUSTOM_LIB, "Device:R"),
        ("power:+5V", CUSTOM_LIB, "power:+5V"),
        ("power:+12V", CUSTOM_LIB, "power:+12V"),
        ("power:GND", CUSTOM_LIB, "power:GND"),
    ],
    "tx_switch.kicad_sch": [
        ("Driver_FET:TC4427", "custom", make_minimal_tc4427),
        ("Transistor_FET:IRF830", "custom", make_minimal_irf830),
        ("Device:C", CUSTOM_LIB, "Device:C"),
        ("Device:R", CUSTOM_LIB, "Device:R"),
        ("power:+12V", CUSTOM_LIB, "power:+12V"),
        ("power:GND", CUSTOM_LIB, "power:GND"),
        ("Connector:SMA", CUSTOM_LIB, "Connector:SMA"),
    ],
    "digital.kicad_sch": [
        ("74xx:74HCT595", os.path.join(KICAD_LIBS, "74xx.kicad_sym"), "74HCT595"),
        ("Transistor_FET:BSS138", os.path.join(KICAD_LIBS, "Transistor_FET.kicad_sym"), "BSS138"),
        ("Device:R", CUSTOM_LIB, "Device:R"),
        ("power:+5V", CUSTOM_LIB, "power:+5V"),
        ("power:GND", CUSTOM_LIB, "power:GND"),
        ("Connector:Conn_02x10_Counter_Clockwise", CUSTOM_LIB, "Connector:Conn_02x10_Counter_Clockwise"),
    ],
}

def get_symbol_definition(lib_id, source, name):
    if source == "custom":
        return name()  # name is a function for custom symbols
    else:
        return extract_symbol_from_lib(source, name)

def inject_lib_symbols(sch_file, symbols_block):
    path = os.path.join(BASE, sch_file)
    with open(path, 'r') as f:
        text = f.read()
    
    # Find or create lib_symbols section
    lib_start = text.find('  (lib_symbols')
    if lib_start == -1:
        # Insert after title_block
        tb_end = text.find('  )\n  \n  (hierarchical')
        if tb_end == -1:
            tb_end = text.find('  )\n\n  (hierarchical')
        if tb_end == -1:
            # Insert after first closing paren after title_block
            tb_end = text.find('  )\n  (hierarchical_label')
        if tb_end == -1:
            print(f"  Could not find insertion point for {sch_file}")
            return False
        
        insertion = f'\n\n  (lib_symbols\n{symbols_block}\n  )\n'
        new_text = text[:tb_end+1] + insertion + text[tb_end+1:]
    else:
        # Replace existing lib_symbols
        # Find the end of lib_symbols
        in_string = False
        escape = False
        depth = 0
        for i in range(lib_start, len(text)):
            c = text[i]
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
            if depth == 0 and i > lib_start:
                lib_end = i + 1
                break
        else:
            lib_end = len(text)
        
        new_text = text[:lib_start] + f'  (lib_symbols\n{symbols_block}\n  )' + text[lib_end:]
    
    with open(path, 'w') as f:
        f.write(new_text)
    return True

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    for sch_file, symbol_list in SYMBOL_SOURCES.items():
        print(f"\nProcessing {sch_file}...")
        blocks = []
        for lib_id, source, name in symbol_list:
            sym_def = get_symbol_definition(lib_id, source, name)
            if sym_def:
                blocks.append(sym_def)
                print(f"  ✓ {lib_id}")
            else:
                print(f"  ✗ {lib_id} NOT FOUND")
        
        symbols_block = '\n'.join(blocks)
        if inject_lib_symbols(sch_file, symbols_block):
            print(f"  → Injected {len(blocks)} symbols")
    
    print("\nDone. Test with: kicad-cli sch erc --format report <sheet>.kicad_sch")
