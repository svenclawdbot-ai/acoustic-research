#!/usr/bin/env python3
"""
Generate tx_switch.kicad_sch for TurboQuant V5
8-channel IRF830 TX switch with gate protection
"""

def generate_tx_switch():
    lines = []
    
    # Header
    lines.extend([
        "(kicad_sch",
        "  (version 20250114)",
        "  (generator \"eeschema\")",
        "  (generator_version \"9.0\")",
        '  (uuid "22222222-3333-4444-5555-666666666664")',
        '  (paper "A3")',
        "  (title_block",
        '    (title "TX Switch - 8x IRF830 Pulser Drivers")',
        '    (date "2026-04-26")',
        '    (rev "5.0")',
        '    (company "TurboQuant")',
        "  )",
        "",
        "  (lib_symbols",
        "    ; Standard library symbols referenced by lib_id",
        "  )",
        "",
    ])
    
    # Hierarchical pins
    lines.extend([
        "  ; === HIERARCHICAL PINS ===",
        '  (hierarchical_pin "+12V" (at 25.4 25.4 180) (effects (font (size 1.27 1.27)) (justify right)) (uuid "hier-12v-in") (pin_type passive))',
        '  (hierarchical_pin "GND" (at 25.4 30.48 180) (effects (font (size 1.27 1.27)) (justify right)) (uuid "hier-gnd-in") (pin_type passive))',
        "",
        '  (hierarchical_pin "GATE0" (at 25.4 50.8 180) (effects (font (size 1.27 1.27)) (justify right)) (uuid "hier-g0") (pin_type input))',
        '  (hierarchical_pin "GATE1" (at 25.4 53.34 180) (effects (font (size 1.27 1.27)) (justify right)) (uuid "hier-g1") (pin_type input))',
        '  (hierarchical_pin "GATE2" (at 25.4 55.88 180) (effects (font (size 1.27 1.27)) (justify right)) (uuid "hier-g2") (pin_type input))',
        '  (hierarchical_pin "GATE3" (at 25.4 58.42 180) (effects (font (size 1.27 1.27)) (justify right)) (uuid "hier-g3") (pin_type input))',
        '  (hierarchical_pin "GATE4" (at 25.4 60.96 180) (effects (font (size 1.27 1.27)) (justify right)) (uuid "hier-g4") (pin_type input))',
        '  (hierarchical_pin "GATE5" (at 25.4 63.5 180) (effects (font (size 1.27 1.27)) (justify right)) (uuid "hier-g5") (pin_type input))',
        '  (hierarchical_pin "GATE6" (at 25.4 66.04 180) (effects (font (size 1.27 1.27)) (justify right)) (uuid "hier-g6") (pin_type input))',
        '  (hierarchical_pin "GATE7" (at 25.4 68.58 180) (effects (font (size 1.27 1.27)) (justify right)) (uuid "hier-g7") (pin_type input))',
        "",
        '  (hierarchical_pin "TX_BUS" (at 200.66 81.28 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "hier-tx-bus") (pin_type output))',
        "",
    ])
    
    # Power symbols
    lines.extend([
        "  ; === POWER SYMBOLS ===",
        '  (symbol (lib_id "power:+12V") (at 38.1 25.4 0) (unit 1)',
        '    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)',
        '    (uuid "pwr-12v-01")',
        '    (property "Reference" "#PWR01" (at 38.1 29.21 0) (effects (font (size 1.27 1.27)) hide))',
        '    (property "Value" "+12V" (at 38.1 21.59 0) (effects (font (size 1.27 1.27))))',
        '    (pin "1" (uuid "pwr-12v-p1")))',
        "",
        '  (symbol (lib_id "power:GND") (at 38.1 30.48 0) (unit 1)',
        '    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)',
        '    (uuid "pwr-gnd-01")',
        '    (property "Reference" "#PWR02" (at 38.1 34.29 0) (effects (font (size 1.27 1.27)) hide))',
        '    (property "Value" "GND" (at 38.1 26.67 0) (effects (font (size 1.27 1.27))))',
        '    (pin "1" (uuid "pwr-gnd-p1")))',
        "",
    ])
    
    # TX_BUS output connector
    lines.extend([
        "  ; === TX_BUS OUTPUT ===",
        '  (symbol (lib_id "Connector:SMA") (at 182.88 81.28 0) (unit 1)',
        '    (exclude_from_sim no) (in_bom no) (on_board no) (dnp yes)',
        '    (uuid "j1-tx-out")',
        '    (property "Reference" "J1" (at 182.88 86.36 0) (effects (font (size 1.27 1.27))))',
        '    (property "Value" "TX_BUS" (at 182.88 88.9 0) (effects (font (size 1.27 1.27))))',
        '    (property "Footprint" "" (at 182.88 81.28 0) (effects (font (size 1.27 1.27)) hide))',
        '    (pin "1" (uuid "j1-p1")) (pin "2" (uuid "j1-p2")))',
        "",
    ])
    
    # 8× IRF830 channels with gate protection
    gate_y = [50.8, 53.34, 55.88, 58.42, 60.96, 63.5, 66.04, 68.58]
    
    for ch in range(8):
        y = gate_y[ch]
        
        lines.extend([
            f"  ; === CH{ch} IRF830 + Gate Protection ===",
            "",
            f"  ; Gate series resistor 100Ω (damping)",
            f'  (symbol (lib_id "Device:R") (at 50.8 {y} 0) (unit 1)',
            '    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)',
            f'    (uuid "r1-ch{ch}")',
            f'    (property "Reference" "R{ch*3+1}" (at 54.61 {y-1.27} 0) (effects (font (size 1.27 1.27)) (justify left)))',
            f'    (property "Value" "100R" (at 47.01 {y} 0) (effects (font (size 1.27 1.27)) (justify right)))',
            '    (property "Footprint" "Resistor_SMD:R_0603_1608Metric" (at 50.8 25.4 0) (effects (font (size 1.27 1.27)) hide))',
            f'    (pin "1" (uuid "r1-ch{ch}-p1")) (pin "2" (uuid "r1-ch{ch}-p2")))',
            "",
            f"  ; Gate pull-down resistor 1kΩ (fast OFF)",
            f'  (symbol (lib_id "Device:R") (at 63.5 {y+5.08} 90) (unit 1)',
            '    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)',
            f'    (uuid "r2-ch{ch}")',
            f'    (property "Reference" "R{ch*3+2}" (at 66.04 {y+8.89} 0) (effects (font (size 1.27 1.27)) (justify left)))',
            f'    (property "Value" "1k" (at 66.04 {y+1.27} 0) (effects (font (size 1.27 1.27)) (justify left)))',
            '    (property "Footprint" "Resistor_SMD:R_0603_1608Metric" (at 63.5 33.02 0) (effects (font (size 1.27 1.27)) hide))',
            f'    (pin "1" (uuid "r2-ch{ch}-p1")) (pin "2" (uuid "r2-ch{ch}-p2")))',
            "",
            f"  ; Gate Zener clamp 12V (BZX84C12)",
            f'  (symbol (lib_id "Device:D_Zener") (at 63.5 {y-2.54} 0) (unit 1)',
            '    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)',
            f'    (uuid "z1-ch{ch}")',
            f'    (property "Reference" "Z{ch+1}" (at 59.69 {y} 0) (effects (font (size 1.27 1.27))))',
            f'    (property "Value" "BZX84C12" (at 59.69 {y-5.08} 0) (effects (font (size 1.27 1.27))))',
            '    (property "Footprint" "Diode_SMD:D_SOD-323" (at 63.5 30.48 0) (effects (font (size 1.27 1.27)) hide))',
            f'    (pin "1" (uuid "z1-ch{ch}-k")) (pin "2" (uuid "z1-ch{ch}-a")))',
            "",
            f"  ; IRF830 N-channel MOSFET (500V, 4.5A)",
            f'  (symbol (lib_id "Transistor_FET:IRF830") (at 76.2 {y} 0) (unit 1)',
            '    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)',
            f'    (uuid "q1-ch{ch}")',
            f'    (property "Reference" "Q{ch+1}" (at 72.39 {y+2.54} 0) (effects (font (size 1.27 1.27))))',
            f'    (property "Value" "IRF830" (at 72.39 {y-2.54} 0) (effects (font (size 1.27 1.27))))',
            '    (property "Footprint" "Package_TO_SOT_THT:TO-220-3_Vertical" (at 76.2 25.4 0) (effects (font (size 1.27 1.27)) hide))',
            f'    (pin "1" (uuid "q1-ch{ch}-g")) (pin "2" (uuid "q1-ch{ch}-d")) (pin "3" (uuid "q1-ch{ch}-s")))',
            "",
        ])
    
    # Wires
    lines.extend([
        "  ; === WIRES ===",
        "",
        "  ; Power distribution",
        '  (wire (pts (xy 25.4 25.4) (xy 38.1 25.4)) (stroke (width 0)) (uuid "w-12v-in"))',
        '  (wire (pts (xy 25.4 30.48) (xy 38.1 30.48)) (stroke (width 0)) (uuid "w-gnd-in"))',
        "",
        "  ; +12V rail distribution to all drain pull-ups",
        '  (wire (pts (xy 38.1 25.4) (xy 38.1 43.18)) (stroke (width 0)) (uuid "w-12v-v1"))',
    ])
    
    # +12V to all drain pull-up points
    for ch in range(8):
        y = gate_y[ch]
        lines.append(f'  (wire (pts (xy 38.1 43.18) (xy 81.28 {y})) (stroke (width 0)) (uuid "w-12v-ch{ch}"))')
    
    lines.append("")
    lines.append("  ; GND distribution to all source pins")
    lines.append('  (wire (pts (xy 38.1 30.48) (xy 38.1 114.3)) (stroke (width 0)) (uuid "w-gnd-v1"))')
    
    for ch in range(8):
        y = gate_y[ch]
        lines.append(f'  (wire (pts (xy 38.1 114.3) (xy 81.28 {y+5.08})) (stroke (width 0)) (uuid "w-gnd-ch{ch}"))')
    
    lines.append("")
    
    # Gate input wiring from hierarchical pins
    for ch in range(8):
        y = gate_y[ch]
        lines.extend([
            f"  ; CH{ch} gate input wiring",
            f'  (wire (pts (xy 25.4 {y}) (xy 46.99 {y})) (stroke (width 0)) (uuid "w-g{ch}-in"))',
            f'  (wire (pts (xy 46.99 {y}) (xy 46.99 {y})) (stroke (width 0)) (uuid "w-r1-ch{ch}-in"))',
            f'  (wire (pts (xy 54.61 {y}) (xy 63.5 {y})) (stroke (width 0)) (uuid "w-r1-ch{ch}-out"))',
            f'  (wire (pts (xy 63.5 {y}) (xy 72.39 {y})) (stroke (width 0)) (uuid "w-g{ch}-gate"))',
            "",
            f"  ; CH{ch} gate protection wiring",
            f'  (wire (pts (xy 63.5 {y}) (xy 63.5 {y+2.54})) (stroke (width 0)) (uuid "w-z1-ch{ch}-k"))',
            f'  (wire (pts (xy 63.5 {y+2.54}) (xy 63.5 {y+5.08})) (stroke (width 0)) (uuid "w-r2-ch{ch}-in"))',
            f'  (wire (pts (xy 63.5 {y+5.08}) (xy 81.28 {y+5.08})) (stroke (width 0)) (uuid "w-r2-ch{ch}-out"))',
            "",
        ])
    
    # TX_BUS output wiring (drains connected together)
    lines.extend([
        "  ; TX_BUS output (all drains connected)",
    ])
    
    for ch in range(8):
        y = gate_y[ch]
        lines.append(f'  (wire (pts (xy 81.28 {y}) (xy 96.52 {y})) (stroke (width 0)) (uuid "w-drain-ch{ch}"))')
    
    # Connect all drains to TX_BUS
    lines.append('  (wire (pts (xy 96.52 50.8) (xy 96.52 81.28)) (stroke (width 0)) (uuid "w-tx-bus-v"))')
    lines.append('  (wire (pts (xy 96.52 81.28) (xy 182.88 81.28)) (stroke (width 0)) (uuid "w-tx-bus-h"))')
    lines.append('  (wire (pts (xy 182.88 81.28) (xy 200.66 81.28)) (stroke (width 0)) (uuid "w-tx-bus-out"))')
    lines.append("")
    
    # Footer
    lines.extend([
        ")",
    ])
    
    return "\n".join(lines)

if __name__ == "__main__":
    sch = generate_tx_switch()
    with open("/home/james/.openclaw/workspace/turboquant_v5/hardware/schematics/tx_switch.kicad_sch", "w") as f:
        f.write(sch)
    print(f"Generated tx_switch.kicad_sch ({len(sch)} bytes)")
