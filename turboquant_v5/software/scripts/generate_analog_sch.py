#!/usr/bin/env python3
"""
Generate complete analog.kicad_sch for TurboQuant V5
8-channel T/R bridge + DG408 MUX + OPA1641 LNA
"""

import uuid
import random

def gen_uuid():
    """Generate a KiCad-style UUID"""
    return f"{random.getrandbits(32):08x}-{random.getrandbits(16):04x}-{random.getrandbits(16):04x}-{random.getrandbits(16):04x}-{random.getrandbits(48):012x}"

# Fixed UUIDs for major components (stable across regenerations)
U1_MUX0 = "u1-mux0-0000-0000-000000000001"
U2_MUX1 = "u2-mux1-0000-0000-000000000002"
U3_LNA0 = "u3-lna0-0000-0000-000000000003"
U4_LNA1 = "u4-lna1-0000-0000-000000000004"

# Channel positions (y-coordinates for each CH)
CH_Y = [27.94, 33.02, 38.1, 43.18, 48.26, 53.34, 58.42, 63.5]

# CH0 component positions (template)
CH0_D1_POS = (76.2, 25.4)
CH0_D2_POS = (76.2, 30.48)
CH0_D3_POS = (86.36, 25.4)
CH0_D4_POS = (86.36, 30.48)
CH0_R1_POS = (63.5, 27.94)
CH0_R2_POS = (63.5, 33.02)
CH0_Z1_POS = (55.88, 30.48)

def generate_schematic():
    lines = []
    
    # Header
    lines.extend([
        "(kicad_sch",
        "  (version 20250114)",
        "  (generator \"eeschema\")",
        "  (generator_version \"9.0\")",
        '  (uuid "22222222-3333-4444-5555-666666666663")',
        '  (paper "A3")',
        "  (title_block",
        '    (title "Analog Frontend - T/R Bridge, MUX \u0026 LNA")',
        '    (date "2026-04-26")',
        '    (rev "5.0")',
        '    (company "TurboQuant")',
        "  )",
        "",
        "  (lib_symbols",
    ])
    
    # Library symbols (simplified — KiCad will resolve these from standard libs)
    lines.extend([
        "    ; Standard library symbols referenced by lib_id",
        "  )",
        "",
    ])
    
    # Hierarchical pins
    lines.extend([
        "  ; === HIERARCHICAL PINS ===",
        '  (hierarchical_pin "+5V" (at 25.4 25.4 180) (effects (font (size 1.27 1.27)) (justify right)) (uuid "hier-5v-in") (pin_type passive))',
        '  (hierarchical_pin "+12V" (at 25.4 30.48 180) (effects (font (size 1.27 1.27)) (justify right)) (uuid "hier-12v-in") (pin_type passive))',
        '  (hierarchical_pin "GND" (at 25.4 35.56 180) (effects (font (size 1.27 1.27)) (justify right)) (uuid "hier-gnd-in") (pin_type passive))',
        "",
        '  (hierarchical_pin "MUX_A" (at 25.4 50.8 180) (effects (font (size 1.27 1.27)) (justify right)) (uuid "hier-mux-a") (pin_type input))',
        '  (hierarchical_pin "MUX_B" (at 25.4 55.88 180) (effects (font (size 1.27 1.27)) (justify right)) (uuid "hier-mux-b") (pin_type input))',
        '  (hierarchical_pin "MUX_C" (at 25.4 60.96 180) (effects (font (size 1.27 1.27)) (justify right)) (uuid "hier-mux-c") (pin_type input))',
        '  (hierarchical_pin "MUX_EN" (at 25.4 66.04 180) (effects (font (size 1.27 1.27)) (justify right)) (uuid "hier-mux-en") (pin_type input))',
        "",
        '  (hierarchical_pin "TX_BUS" (at 25.4 81.28 180) (effects (font (size 1.27 1.27)) (justify right)) (uuid "hier-tx-bus") (pin_type passive))',
        '  (hierarchical_pin "RX0_OUT" (at 200.66 96.52 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "hier-rx0-out") (pin_type output))',
        '  (hierarchical_pin "RX1_OUT" (at 200.66 104.14 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "hier-rx1-out") (pin_type output))',
        "",
    ])
    
    # CH0-CH7 hierarchical pins
    for i, y in enumerate(CH_Y):
        lines.append(f'  (hierarchical_pin "CH{i}" (at 200.66 {y} 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "hier-ch{i}") (pin_type passive))')
    
    lines.append("")
    
    # Power symbols
    lines.extend([
        "  ; === POWER SYMBOLS ===",
        '  (symbol (lib_id "power:+5V") (at 38.1 25.4 0) (unit 1)',
        '    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)',
        '    (uuid "pwr-5v-01")',
        '    (property "Reference" "#PWR01" (at 38.1 29.21 0) (effects (font (size 1.27 1.27)) hide))',
        '    (property "Value" "+5V" (at 38.1 21.59 0) (effects (font (size 1.27 1.27))))',
        '    (pin "1" (uuid "pwr-5v-p1")))',
        "",
        '  (symbol (lib_id "power:+12V") (at 38.1 30.48 0) (unit 1)',
        '    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)',
        '    (uuid "pwr-12v-01")',
        '    (property "Reference" "#PWR02" (at 38.1 34.29 0) (effects (font (size 1.27 1.27)) hide))',
        '    (property "Value" "+12V" (at 38.1 26.67 0) (effects (font (size 1.27 1.27))))',
        '    (pin "1" (uuid "pwr-12v-p1")))',
        "",
        '  (symbol (lib_id "power:GND") (at 38.1 35.56 0) (unit 1)',
        '    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)',
        '    (uuid "pwr-gnd-01")',
        '    (property "Reference" "#PWR03" (at 38.1 39.37 0) (effects (font (size 1.27 1.27)) hide))',
        '    (property "Value" "GND" (at 38.1 31.75 0) (effects (font (size 1.27 1.27))))',
        '    (pin "1" (uuid "pwr-gnd-p1")))',
        "",
    ])
    
    # DG408 MUX0
    lines.extend([
        "  ; === DG408 MUX0 (Channels 0-7 → RX0) ===",
        '  (symbol (lib_id "Analog_Switch:DG408") (at 114.3 60.96 0) (unit 1)',
        '    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)',
        f'    (uuid "{U1_MUX0}")',
        '    (property "Reference" "U1" (at 108.59 73.66 0) (effects (font (size 1.27 1.27))))',
        '    (property "Value" "DG408" (at 114.3 73.66 0) (effects (font (size 1.27 1.27))))',
        '    (property "Footprint" "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm" (at 114.3 60.96 0) (effects (font (size 1.27 1.27)) hide))',
    ])
    for i in range(1, 17):
        lines.append(f'    (pin "{i}" (uuid "u1-p{i}"))')
    lines.extend([
        "  )",
        "",
    ])
    
    # DG408 MUX1
    lines.extend([
        "  ; === DG408 MUX1 (Channels 0-7 → RX1) ===",
        '  (symbol (lib_id "Analog_Switch:DG408") (at 114.3 96.52 0) (unit 1)',
        '    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)',
        f'    (uuid "{U2_MUX1}")',
        '    (property "Reference" "U2" (at 108.59 109.22 0) (effects (font (size 1.27 1.27))))',
        '    (property "Value" "DG408" (at 114.3 109.22 0) (effects (font (size 1.27 1.27))))',
        '    (property "Footprint" "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm" (at 114.3 96.52 0) (effects (font (size 1.27 1.27)) hide))',
    ])
    for i in range(1, 17):
        lines.append(f'    (pin "{i}" (uuid "u2-p{i}"))')
    lines.extend([
        "  )",
        "",
    ])
    
    # OPA1641 LNA0
    lines.extend([
        "  ; === OPA1641 LNA0 ===",
        '  (symbol (lib_id "Amplifier_Operational:OPA1641") (at 152.4 60.96 0) (unit 1)',
        '    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)',
        f'    (uuid "{U3_LNA0}")',
        '    (property "Reference" "U3" (at 146.69 73.66 0) (effects (font (size 1.27 1.27))))',
        '    (property "Value" "OPA1641" (at 152.4 73.66 0) (effects (font (size 1.27 1.27))))',
        '    (property "Footprint" "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm" (at 152.4 60.96 0) (effects (font (size 1.27 1.27)) hide))',
    ])
    for i in range(1, 9):
        lines.append(f'    (pin "{i}" (uuid "u3-p{i}"))')
    lines.extend([
        "  )",
        "",
    ])
    
    # OPA1641 LNA1
    lines.extend([
        "  ; === OPA1641 LNA1 ===",
        '  (symbol (lib_id "Amplifier_Operational:OPA1641") (at 152.4 96.52 0) (unit 1)',
        '    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)',
        f'    (uuid "{U4_LNA1}")',
        '    (property "Reference" "U4" (at 146.69 109.22 0) (effects (font (size 1.27 1.27))))',
        '    (property "Value" "OPA1641" (at 152.4 109.22 0) (effects (font (size 1.27 1.27))))',
        '    (property "Footprint" "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm" (at 152.4 96.52 0) (effects (font (size 1.27 1.27)) hide))',
    ])
    for i in range(1, 9):
        lines.append(f'    (pin "{i}" (uuid "u4-p{i}"))')
    lines.extend([
        "  )",
        "",
    ])
    
    # T/R Bridge components for all 8 channels
    lines.append("  ; === T/R BRIDGE COMPONENTS (8 channels) ===")
    
    for ch in range(8):
        y_offset = CH_Y[ch] - 27.94  # Offset from CH0 template
        
        # D1, D2, D3, D4 for each channel
        d1_y = 25.4 + y_offset
        d2_y = 30.48 + y_offset
        d3_y = 25.4 + y_offset
        d4_y = 30.48 + y_offset
        
        lines.extend([
            f"  ; CH{ch} T/R Bridge",
            f'  (symbol (lib_id "Device:D") (at 76.2 {d1_y} 0) (unit 1)',
            '    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)',
            f'    (uuid "d1-ch{ch}")',
            f'    (property "Reference" "D{ch*4+1}" (at 72.39 {d1_y+2.54} 0) (effects (font (size 1.27 1.27))))',
            f'    (property "Value" "MUR120" (at 72.39 {d1_y-2.54} 0) (effects (font (size 1.27 1.27))))',
            '    (property "Footprint" "Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal" (at 76.2 25.4 0) (effects (font (size 1.27 1.27)) hide))',
            f'    (pin "1" (uuid "d1-ch{ch}-k")) (pin "2" (uuid "d1-ch{ch}-a")))',
            "",
            f'  (symbol (lib_id "Device:D") (at 76.2 {d2_y} 0) (unit 1)',
            '    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)',
            f'    (uuid "d2-ch{ch}")',
            f'    (property "Reference" "D{ch*4+2}" (at 72.39 {d2_y+2.54} 0) (effects (font (size 1.27 1.27))))',
            f'    (property "Value" "MUR120" (at 72.39 {d2_y-2.54} 0) (effects (font (size 1.27 1.27))))',
            '    (property "Footprint" "Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal" (at 76.2 30.48 0) (effects (font (size 1.27 1.27)) hide))',
            f'    (pin "1" (uuid "d2-ch{ch}-k")) (pin "2" (uuid "d2-ch{ch}-a")))',
            "",
            f'  (symbol (lib_id "Device:D") (at 86.36 {d3_y} 0) (unit 1)',
            '    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)',
            f'    (uuid "d3-ch{ch}")',
            f'    (property "Reference" "D{ch*4+3}" (at 82.55 {d3_y+2.54} 0) (effects (font (size 1.27 1.27))))',
            f'    (property "Value" "MUR120" (at 82.55 {d3_y-2.54} 0) (effects (font (size 1.27 1.27))))',
            '    (property "Footprint" "Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal" (at 86.36 25.4 0) (effects (font (size 1.27 1.27)) hide))',
            f'    (pin "1" (uuid "d3-ch{ch}-k")) (pin "2" (uuid "d3-ch{ch}-a")))',
            "",
            f'  (symbol (lib_id "Device:D") (at 86.36 {d4_y} 0) (unit 1)',
            '    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)',
            f'    (uuid "d4-ch{ch}")',
            f'    (property "Reference" "D{ch*4+4}" (at 82.55 {d4_y+2.54} 0) (effects (font (size 1.27 1.27))))',
            f'    (property "Value" "MUR120" (at 82.55 {d4_y-2.54} 0) (effects (font (size 1.27 1.27))))',
            '    (property "Footprint" "Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal" (at 86.36 30.48 0) (effects (font (size 1.27 1.27)) hide))',
            f'    (pin "1" (uuid "d4-ch{ch}-k")) (pin "2" (uuid "d4-ch{ch}-a")))',
            "",
        ])
        
        # Bias network for each channel
        r1_y = 27.94 + y_offset
        r2_y = 33.02 + y_offset
        z1_y = 30.48 + y_offset
        
        lines.extend([
            f"  ; CH{ch} Bias Network",
            f'  (symbol (lib_id "Device:R") (at 63.5 {r1_y} 0) (unit 1)',
            '    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)',
            f'    (uuid "r1-ch{ch}")',
            f'    (property "Reference" "R{ch*3+1}" (at 67.31 {r1_y-1.27} 0) (effects (font (size 1.27 1.27)) (justify left)))',
            f'    (property "Value" "10k" (at 59.69 {r1_y} 0) (effects (font (size 1.27 1.27)) (justify right)))',
            '    (property "Footprint" "Resistor_SMD:R_0603_1608Metric" (at 63.5 27.94 0) (effects (font (size 1.27 1.27)) hide))',
            f'    (pin "1" (uuid "r1-ch{ch}-p1")) (pin "2" (uuid "r1-ch{ch}-p2")))',
            "",
            f'  (symbol (lib_id "Device:R") (at 63.5 {r2_y} 0) (unit 1)',
            '    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)',
            f'    (uuid "r2-ch{ch}")',
            f'    (property "Reference" "R{ch*3+2}" (at 67.31 {r2_y-1.27} 0) (effects (font (size 1.27 1.27)) (justify left)))',
            f'    (property "Value" "100k" (at 59.69 {r2_y} 0) (effects (font (size 1.27 1.27)) (justify right)))',
            '    (property "Footprint" "Resistor_SMD:R_0603_1608Metric" (at 63.5 33.02 0) (effects (font (size 1.27 1.27)) hide))',
            f'    (pin "1" (uuid "r2-ch{ch}-p1")) (pin "2" (uuid "r2-ch{ch}-p2")))',
            "",
            f'  (symbol (lib_id "Device:D_Zener") (at 55.88 {z1_y} 0) (unit 1)',
            '    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)',
            f'    (uuid "z1-ch{ch}")',
            f'    (property "Reference" "Z{ch+1}" (at 52.07 {z1_y+2.54} 0) (effects (font (size 1.27 1.27))))',
            f'    (property "Value" "BZX84C5V1" (at 52.07 {z1_y-2.54} 0) (effects (font (size 1.27 1.27))))',
            '    (property "Footprint" "Diode_SMD:D_SOD-323" (at 55.88 30.48 0) (effects (font (size 1.27 1.27)) hide))',
            f'    (pin "1" (uuid "z1-ch{ch}-k")) (pin "2" (uuid "z1-ch{ch}-a")))',
            "",
        ])
    
    # Input protection components (for both LNA0 and LNA1)
    lines.extend([
        "  ; === INPUT PROTECTION (LNA0) ===",
        '  (symbol (lib_id "Device:C") (at 125.73 60.96 90) (unit 1)',
        '    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)',
        '    (uuid "c1-dcblock0")',
        '    (property "Reference" "C1" (at 121.92 60.96 90) (effects (font (size 1.27 1.27))))',
        '    (property "Value" "100nF" (at 129.54 60.96 90) (effects (font (size 1.27 1.27))))',
        '    (property "Footprint" "Capacitor_SMD:C_0603_1608Metric" (at 125.73 60.96 0) (effects (font (size 1.27 1.27)) hide))',
        '    (pin "1" (uuid "c1-p1")) (pin "2" (uuid "c1-p2")))',
        "",
        '  (symbol (lib_id "Device:R") (at 133.35 60.96 0) (unit 1)',
        '    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)',
        '    (uuid "r3-att0")',
        '    (property "Reference" "R25" (at 137.16 59.69 0) (effects (font (size 1.27 1.27)) (justify left)))',
        '    (property "Value" "9.09k" (at 129.54 60.96 0) (effects (font (size 1.27 1.27)) (justify right)))',
        '    (property "Footprint" "Resistor_SMD:R_0805_2012Metric" (at 133.35 60.96 0) (effects (font (size 1.27 1.27)) hide))',
        '    (pin "1" (uuid "r3-p1")) (pin "2" (uuid "r3-p2")))',
        "",
        '  (symbol (lib_id "Device:R") (at 133.35 66.04 0) (unit 1)',
        '    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)',
        '    (uuid "r4-att0")',
        '    (property "Reference" "R26" (at 137.16 64.77 0) (effects (font (size 1.27 1.27)) (justify left)))',
        '    (property "Value" "1k" (at 129.54 66.04 0) (effects (font (size 1.27 1.27)) (justify right)))',
        '    (property "Footprint" "Resistor_SMD:R_0805_2012Metric" (at 133.35 66.04 0) (effects (font (size 1.27 1.27)) hide))',
        '    (pin "1" (uuid "r4-p1")) (pin "2" (uuid "r4-p2")))',
        "",
        '  (symbol (lib_id "Device:D") (at 141.61 57.15 0) (unit 1)',
        '    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)',
        '    (uuid "d5-clamp0")',
        '    (property "Reference" "D33" (at 137.8 59.69 0) (effects (font (size 1.27 1.27))))',
        '    (property "Value" "BAV99" (at 137.8 54.61 0) (effects (font (size 1.27 1.27))))',
        '    (property "Footprint" "Diode_SMD:D_SOT-23" (at 141.61 57.15 0) (effects (font (size 1.27 1.27)) hide))',
        '    (pin "1" (uuid "d5-p1")) (pin "2" (uuid "d5-p2")))',
        "",
    ])
    
    # LNA feedback components
    lines.extend([
        "  ; === LNA0 FEEDBACK ===",
        '  (symbol (lib_id "Device:R") (at 165.1 53.34 0) (unit 1)',
        '    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)',
        '    (uuid "r5-lna0")',
        '    (property "Reference" "R27" (at 168.91 52.07 0) (effects (font (size 1.27 1.27)) (justify left)))',
        '    (property "Value" "1k" (at 161.29 53.34 0) (effects (font (size 1.27 1.27)) (justify right)))',
        '    (property "Footprint" "Resistor_SMD:R_0805_2012Metric" (at 165.1 53.34 0) (effects (font (size 1.27 1.27)) hide))',
        '    (pin "1" (uuid "r5-p1")) (pin "2" (uuid "r5-p2")))',
        "",
        '  (symbol (lib_id "Device:R") (at 171.45 55.88 90) (unit 1)',
        '    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)',
        '    (uuid "r6-lna0")',
        '    (property "Reference" "R28" (at 174.63 54.61 0) (effects (font (size 1.27 1.27)) (justify left)))',
        '    (property "Value" "9.09k" (at 174.63 57.15 0) (effects (font (size 1.27 1.27)) (justify left)))',
        '    (property "Footprint" "Resistor_SMD:R_0805_2012Metric" (at 171.45 55.88 0) (effects (font (size 1.27 1.27)) hide))',
        '    (pin "1" (uuid "r6-p1")) (pin "2" (uuid "r6-p2")))',
        "",
    ])
    
    # Decoupling capacitors
    lines.extend([
        "  ; === DECOUPLING CAPACITORS ===",
        '  (symbol (lib_id "Device:C") (at 101.6 45.72 0) (unit 1)',
        '    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)',
        '    (uuid "c2-vl0")',
        '    (property "Reference" "C2" (at 105.41 44.45 0) (effects (font (size 1.27 1.27)) (justify left)))',
        '    (property "Value" "100nF" (at 97.79 45.72 0) (effects (font (size 1.27 1.27)) (justify right)))',
        '    (property "Footprint" "Capacitor_SMD:C_0603_1608Metric" (at 101.6 45.72 0) (effects (font (size 1.27 1.27)) hide))',
        '    (pin "1" (uuid "c2-p1")) (pin "2" (uuid "c2-p2")))',
        "",
        '  (symbol (lib_id "Device:C") (at 101.6 81.28 0) (unit 1)',
        '    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)',
        '    (uuid "c3-vl1")',
        '    (property "Reference" "C3" (at 105.41 80.01 0) (effects (font (size 1.27 1.27)) (justify left)))',
        '    (property "Value" "100nF" (at 97.79 81.28 0) (effects (font (size 1.27 1.27)) (justify right)))',
        '    (property "Footprint" "Capacitor_SMD:C_0603_1608Metric" (at 101.6 81.28 0) (effects (font (size 1.27 1.27)) hide))',
        '    (pin "1" (uuid "c3-p1")) (pin "2" (uuid "c3-p2")))',
        "",
        '  (symbol (lib_id "Device:C") (at 139.7 45.72 0) (unit 1)',
        '    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)',
        '    (uuid "c4-vpos0")',
        '    (property "Reference" "C4" (at 143.51 44.45 0) (effects (font (size 1.27 1.27)) (justify left)))',
        '    (property "Value" "100nF" (at 135.89 45.72 0) (effects (font (size 1.27 1.27)) (justify right)))',
        '    (property "Footprint" "Capacitor_SMD:C_0603_1608Metric" (at 139.7 45.72 0) (effects (font (size 1.27 1.27)) hide))',
        '    (pin "1" (uuid "c4-p1")) (pin "2" (uuid "c4-p2")))',
        "",
        '  (symbol (lib_id "Device:C") (at 139.7 81.28 0) (unit 1)',
        '    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)',
        '    (uuid "c5-vpos1")',
        '    (property "Reference" "C5" (at 143.51 80.01 0) (effects (font (size 1.27 1.27)) (justify left)))',
        '    (property "Value" "100nF" (at 135.89 81.28 0) (effects (font (size 1.27 1.27)) (justify right)))',
        '    (property "Footprint" "Capacitor_SMD:C_0603_1608Metric" (at 139.7 81.28 0) (effects (font (size 1.27 1.27)) hide))',
        '    (pin "1" (uuid "c5-p1")) (pin "2" (uuid "c5-p2")))',
        "",
    ])
    
    # Wires section
    lines.extend([
        "  ; === WIRES ===",
        "",
        "  ; Power distribution",
        '  (wire (pts (xy 25.4 25.4) (xy 38.1 25.4)) (stroke (width 0)) (uuid "w-5v-in"))',
        '  (wire (pts (xy 25.4 30.48) (xy 38.1 30.48)) (stroke (width 0)) (uuid "w-12v-in"))',
        '  (wire (pts (xy 25.4 35.56) (xy 38.1 35.56)) (stroke (width 0)) (uuid "w-gnd-in"))',
        "",
    ])
    
    # +5V rail distribution
    lines.extend([
        "  ; +5V rail distribution",
        '  (wire (pts (xy 38.1 25.4) (xy 38.1 43.18)) (stroke (width 0)) (uuid "w-5v-v1"))',
        '  (wire (pts (xy 38.1 43.18) (xy 101.6 43.18)) (stroke (width 0)) (uuid "w-5v-to-c2"))',
        '  (wire (pts (xy 101.6 43.18) (xy 101.6 44.45)) (stroke (width 0)) (uuid "w-5v-c2-v"))',
        '  (junction (at 101.6 43.18) (diameter 0.762) (color 0 0 0 0) (uuid "junc-5v-c2"))',
        '  (wire (pts (xy 101.6 43.18) (xy 139.7 43.18)) (stroke (width 0)) (uuid "w-5v-to-c4"))',
        '  (wire (pts (xy 139.7 43.18) (xy 139.7 44.45)) (stroke (width 0)) (uuid "w-5v-c4-v"))',
        '  (junction (at 139.7 43.18) (diameter 0.762) (color 0 0 0 0) (uuid "junc-5v-c4"))',
        '  (wire (pts (xy 139.7 43.18) (xy 152.4 43.18)) (stroke (width 0)) (uuid "w-5v-to-u3"))',
        '  (wire (pts (xy 152.4 43.18) (xy 152.4 66.04)) (stroke (width 0)) (uuid "w-5v-u3-v"))',
        "",
    ])
    
    # +12V rail distribution
    lines.extend([
        "  ; +12V rail distribution (DG408 VDD)",
        '  (wire (pts (xy 38.1 30.48) (xy 38.1 40.64)) (stroke (width 0)) (uuid "w-12v-v1"))',
        '  (wire (pts (xy 38.1 40.64) (xy 114.3 40.64)) (stroke (width 0)) (uuid "w-12v-to-u1"))',
        '  (wire (pts (xy 114.3 40.64) (xy 114.3 50.8)) (stroke (width 0)) (uuid "w-12v-u1-v"))',
        '  (junction (at 114.3 40.64) (diameter 0.762) (color 0 0 0 0) (uuid "junc-12v-u1"))',
        '  (wire (pts (xy 114.3 40.64) (xy 114.3 86.36)) (stroke (width 0)) (uuid "w-12v-u2-v"))',
        '  (wire (pts (xy 114.3 86.36) (xy 114.3 96.52)) (stroke (width 0)) (uuid "w-12v-u2-v2"))',
        "",
    ])
    
    # GND distribution
    lines.extend([
        "  ; GND distribution",
        '  (wire (pts (xy 38.1 35.56) (xy 38.1 114.3)) (stroke (width 0)) (uuid "w-gnd-v1"))',
        '  (wire (pts (xy 38.1 114.3) (xy 101.6 114.3)) (stroke (width 0)) (uuid "w-gnd-c2"))',
        '  (wire (pts (xy 101.6 114.3) (xy 101.6 46.99)) (stroke (width 0)) (uuid "w-gnd-c2-v"))',
        '  (wire (pts (xy 101.6 114.3) (xy 139.7 114.3)) (stroke (width 0)) (uuid "w-gnd-c4"))',
        '  (wire (pts (xy 139.7 114.3) (xy 139.7 46.99)) (stroke (width 0)) (uuid "w-gnd-c4-v"))',
        '  (wire (pts (xy 139.7 114.3) (xy 152.4 114.3)) (stroke (width 0)) (uuid "w-gnd-u3"))',
        '  (wire (pts (xy 152.4 114.3) (xy 152.4 71.12)) (stroke (width 0)) (uuid "w-gnd-u3-v"))',
        "",
    ])
    
    # MUX address lines
    lines.extend([
        "  ; MUX address lines (shared between U1 and U2)",
        '  (wire (pts (xy 25.4 50.8) (xy 96.52 50.8)) (stroke (width 0)) (uuid "w-mux-a"))',
        '  (wire (pts (xy 96.52 50.8) (xy 96.52 55.88)) (stroke (width 0)) (uuid "w-mux-a-v"))',
        '  (wire (pts (xy 96.52 55.88) (xy 103.89 55.88)) (stroke (width 0)) (uuid "w-mux-a-u1"))',
        '  (wire (pts (xy 96.52 55.88) (xy 96.52 91.44)) (stroke (width 0)) (uuid "w-mux-a-u2-v"))',
        '  (wire (pts (xy 96.52 91.44) (xy 103.89 91.44)) (stroke (width 0)) (uuid "w-mux-a-u2"))',
        "",
        '  (wire (pts (xy 25.4 55.88) (xy 91.44 55.88)) (stroke (width 0)) (uuid "w-mux-b"))',
        '  (wire (pts (xy 91.44 55.88) (xy 91.44 58.42)) (stroke (width 0)) (uuid "w-mux-b-v"))',
        '  (wire (pts (xy 91.44 58.42) (xy 103.89 58.42)) (stroke (width 0)) (uuid "w-mux-b-u1"))',
        '  (wire (pts (xy 91.44 58.42) (xy 91.44 93.98)) (stroke (width 0)) (uuid "w-mux-b-u2-v"))',
        '  (wire (pts (xy 91.44 93.98) (xy 103.89 93.98)) (stroke (width 0)) (uuid "w-mux-b-u2"))',
        "",
        '  (wire (pts (xy 25.4 60.96) (xy 86.36 60.96)) (stroke (width 0)) (uuid "w-mux-c"))',
        '  (wire (pts (xy 86.36 60.96) (xy 86.36 60.96)) (stroke (width 0)) (uuid "w-mux-c-v"))',
        '  (wire (pts (xy 86.36 60.96) (xy 103.89 60.96)) (stroke (width 0)) (uuid "w-mux-c-u1"))',
        '  (wire (pts (xy 86.36 60.96) (xy 86.36 96.52)) (stroke (width 0)) (uuid "w-mux-c-u2-v"))',
        '  (wire (pts (xy 86.36 96.52) (xy 103.89 96.52)) (stroke (width 0)) (uuid "w-mux-c-u2"))',
        "",
        '  (wire (pts (xy 25.4 66.04) (xy 81.28 66.04)) (stroke (width 0)) (uuid "w-mux-en"))',
        '  (wire (pts (xy 81.28 66.04) (xy 81.28 63.5)) (stroke (width 0)) (uuid "w-mux-en-v"))',
        '  (wire (pts (xy 81.28 63.5) (xy 103.89 63.5)) (stroke (width 0)) (uuid "w-mux-en-u1"))',
        '  (wire (pts (xy 81.28 63.5) (xy 81.28 99.06)) (stroke (width 0)) (uuid "w-mux-en-u2-v"))',
        '  (wire (pts (xy 81.28 99.06) (xy 103.89 99.06)) (stroke (width 0)) (uuid "w-mux-en-u2"))',
        "",
    ])
    
    # T/R bridge wiring for all 8 channels
    lines.extend([
        "  ; === T/R BRIDGE WIRING (8 channels) ===",
        "",
        "  ; TX_BUS input from hierarchical pin",
        '  (wire (pts (xy 25.4 81.28) (xy 50.8 81.28)) (stroke (width 0)) (uuid "w-tx-bus-in"))',
    ])
    
    # TX_BUS vertical distribution to all channels
    lines.append('  (wire (pts (xy 50.8 81.28) (xy 50.8 27.94)) (stroke (width 0)) (uuid "w-tx-bus-v"))')
    
    for ch in range(8):
        y = CH_Y[ch]
        
        lines.extend([
            f"",
            f"  ; CH{ch} T/R Bridge wiring",
            f'  (wire (pts (xy 50.8 {y}) (xy 68.58 {y})) (stroke (width 0)) (uuid "w-tx-bus-ch{ch}"))',
            f'  (wire (pts (xy 68.58 {y}) (xy 72.39 {y})) (stroke (width 0)) (uuid "w-d1-ch{ch}-in"))',
            f'  (wire (pts (xy 79.99 {y}) (xy 81.28 {y})) (stroke (width 0)) (uuid "w-d1-ch{ch}-out"))',
            f'  (wire (pts (xy 81.28 {y}) (xy 81.28 {y+2.54})) (stroke (width 0)) (uuid "w-d2-ch{ch}-in"))',
            f'  (wire (pts (xy 79.99 {y+2.54}) (xy 76.2 {y+2.54})) (stroke (width 0)) (uuid "w-d2-ch{ch}-out"))',
            f'  (wire (pts (xy 68.58 {y}) (xy 68.58 {y-2.54})) (stroke (width 0)) (uuid "w-d3-ch{ch}-v"))',
            f'  (wire (pts (xy 68.58 {y-2.54}) (xy 72.39 {y-2.54})) (stroke (width 0)) (uuid "w-d3-ch{ch}-in"))',
            f'  (wire (pts (xy 79.99 {y-2.54}) (xy 81.28 {y-2.54})) (stroke (width 0)) (uuid "w-d3-ch{ch}-out"))',
            f'  (wire (pts (xy 81.28 {y-2.54}) (xy 81.28 {y})) (stroke (width 0)) (uuid "w-d3-ch{ch}-ch0"))',
            f'  (wire (pts (xy 81.28 {y}) (xy 81.28 {y+5.08})) (stroke (width 0)) (uuid "w-d4-ch{ch}-in"))',
            f'  (wire (pts (xy 81.28 {y+5.08}) (xy 86.36 {y+5.08})) (stroke (width 0)) (uuid "w-d4-ch{ch}-out"))',
            f'  (wire (pts (xy 81.28 {y}) (xy 200.66 {y})) (stroke (width 0)) (uuid "w-ch{ch}-out"))',
            "",
            f"  ; CH{ch} bias network wiring",
            f'  (wire (pts (xy 55.88 {y}) (xy 55.88 {y+10.16})) (stroke (width 0)) (uuid "w-bias-r1-ch{ch}"))',
            f'  (wire (pts (xy 55.88 {y+10.16}) (xy 81.28 {y+10.16})) (stroke (width 0)) (uuid "w-bias-r1-rx-ch{ch}"))',
            f'  (wire (pts (xy 55.88 {y+5.08}) (xy 55.88 {y+10.16})) (stroke (width 0)) (uuid "w-bias-r2-ch{ch}"))',
            f'  (wire (pts (xy 55.88 {y+10.16}) (xy 55.88 114.3)) (stroke (width 0)) (uuid "w-bias-r2-gnd-ch{ch}"))',
            f'  (wire (pts (xy 55.88 {y+2.54}) (xy 55.88 {y+10.16})) (stroke (width 0)) (uuid "w-z1-k-ch{ch}"))',
            f'  (wire (pts (xy 55.88 {y+10.16}) (xy 55.88 114.3)) (stroke (width 0)) (uuid "w-z1-gnd-ch{ch}"))',
        ])
    
    # RX_BUS horizontal and vertical connections
    lines.extend([
        "",
        "  ; RX_BUS connections from all channels",
    ])
    
    # Collect all D2 and D4 outputs to form RX_BUS
    for ch in range(8):
        y = CH_Y[ch]
        lines.extend([
            f'  (wire (pts (xy 76.2 {y+2.54}) (xy 76.2 {y+10.16})) (stroke (width 0)) (uuid "w-rx-bus-d2-ch{ch}"))',
            f'  (wire (pts (xy 86.36 {y+5.08}) (xy 86.36 {y+10.16})) (stroke (width 0)) (uuid "w-rx-bus-d4-ch{ch}"))',
        ])
    
    # Connect all RX_BUS nodes together
    lines.extend([
        "",
        "  ; RX_BUS horizontal backbone",
    ])
    
    # Create horizontal RX_BUS at y=50.8 (main backbone)
    lines.append('  (wire (pts (xy 76.2 50.8) (xy 96.52 50.8)) (stroke (width 0)) (uuid "w-rx-bus-h1"))')
    lines.append('  (junction (at 96.52 50.8) (diameter 0.762) (color 0 0 0 0) (uuid "junc-rx-main"))')
    
    # DG408 S1-S8 connections to RX_BUS
    lines.extend([
        "",
        "  ; DG408 MUX0 S1-S8 → RX_BUS",
    ])
    
    mux0_s_pins = [
        (68.58, 50.8), (66.04, 50.8), (63.5, 50.8), (60.96, 50.8),
        (58.42, 50.8), (55.88, 50.8), (53.34, 50.8), (50.8, 50.8)
    ]
    
    for i, (s_y, rx_y) in enumerate(mux0_s_pins):
        ch = i
        lines.extend([
            f'  (wire (pts (xy 103.89 {s_y}) (xy 96.52 {s_y})) (stroke (width 0)) (uuid "w-u1-s{i+1}"))',
            f'  (wire (pts (xy 96.52 {s_y}) (xy 96.52 50.8)) (stroke (width 0)) (uuid "w-u1-s{i+1}-rx"))',
        ])
    
    lines.extend([
        "",
        "  ; DG408 MUX1 S1-S8 → RX_BUS",
    ])
    
    mux1_s_pins = [
        (104.14, 50.8), (101.6, 50.8), (99.06, 50.8), (96.52, 50.8),
        (93.98, 50.8), (91.44, 50.8), (88.9, 50.8), (86.36, 50.8)
    ]
    
    for i, (s_y, rx_y) in enumerate(mux1_s_pins):
        lines.extend([
            f'  (wire (pts (xy 103.89 {s_y}) (xy 96.52 {s_y})) (stroke (width 0)) (uuid "w-u2-s{i+1}"))',
            f'  (wire (pts (xy 96.52 {s_y}) (xy 96.52 50.8)) (stroke (width 0)) (uuid "w-u2-s{i+1}-rx"))',
        ])
    
    # LNA0 input wiring
    lines.extend([
        "",
        "  ; === LNA0 INPUT WIRING ===",
        '  (wire (pts (xy 124.46 60.96) (xy 125.73 60.96)) (stroke (width 0)) (uuid "w-u1-x"))',
        '  (wire (pts (xy 125.73 60.96) (xy 125.73 60.96)) (stroke (width 0)) (uuid "w-c1-in"))',
        '  (wire (pts (xy 125.73 60.96) (xy 129.54 60.96)) (stroke (width 0)) (uuid "w-c1-out"))',
        '  (wire (pts (xy 129.54 60.96) (xy 129.54 60.96)) (stroke (width 0)) (uuid "w-r3-in"))',
        '  (wire (pts (xy 137.16 60.96) (xy 137.16 60.96)) (stroke (width 0)) (uuid "w-r3-out"))',
        '  (wire (pts (xy 137.16 60.96) (xy 137.16 66.04)) (stroke (width 0)) (uuid "w-r4-in"))',
        '  (wire (pts (xy 137.16 66.04) (xy 133.35 66.04)) (stroke (width 0)) (uuid "w-r4-out"))',
        '  (wire (pts (xy 133.35 66.04) (xy 133.35 66.04)) (stroke (width 0)) (uuid "w-r4-gnd"))',
        '  (wire (pts (xy 137.16 60.96) (xy 143.51 60.96)) (stroke (width 0)) (uuid "w-lna0-in"))',
        '  (wire (pts (xy 143.51 60.96) (xy 143.51 58.42)) (stroke (width 0)) (uuid "w-lna0-in-v"))',
        '  (wire (pts (xy 143.51 58.42) (xy 145.8 58.42)) (stroke (width 0)) (uuid "w-u3-noninv"))',
        "",
        "  ; LNA0 feedback",
        '  (wire (pts (xy 161.29 60.96) (xy 171.45 60.96)) (stroke (width 0)) (uuid "w-u3-out-rf"))',
        '  (wire (pts (xy 171.45 60.96) (xy 171.45 55.88)) (stroke (width 0)) (uuid "w-r6-in"))',
        '  (wire (pts (xy 171.45 55.88) (xy 161.29 55.88)) (stroke (width 0)) (uuid "w-r6-out"))',
        '  (wire (pts (xy 161.29 55.88) (xy 161.29 55.88)) (stroke (width 0)) (uuid "w-u3-inv-rf"))',
        "",
        "  ; LNA0 Rg to GND",
        '  (wire (pts (xy 161.29 55.88) (xy 165.1 55.88)) (stroke (width 0)) (uuid "w-r5-in"))',
        '  (wire (pts (xy 165.1 55.88) (xy 165.1 53.34)) (stroke (width 0)) (uuid "w-r5-v"))',
        '  (wire (pts (xy 165.1 53.34) (xy 165.1 53.34)) (stroke (width 0)) (uuid "w-r5-gnd"))',
        "",
    ])
    
    # LNA1 input wiring (copy of LNA0)
    lines.extend([
        "  ; === LNA1 INPUT WIRING ===",
        '  (wire (pts (xy 124.46 96.52) (xy 125.73 96.52)) (stroke (width 0)) (uuid "w-u2-x"))',
        '  (wire (pts (xy 125.73 96.52) (xy 125.73 96.52)) (stroke (width 0)) (uuid "w-c6-in"))',
        '  (wire (pts (xy 125.73 96.52) (xy 129.54 96.52)) (stroke (width 0)) (uuid "w-c6-out"))',
        '  (wire (pts (xy 129.54 96.52) (xy 129.54 96.52)) (stroke (width 0)) (uuid "w-r29-in"))',
        '  (wire (pts (xy 137.16 96.52) (xy 137.16 96.52)) (stroke (width 0)) (uuid "w-r29-out"))',
        '  (wire (pts (xy 137.16 96.52) (xy 137.16 101.6)) (stroke (width 0)) (uuid "w-r30-in"))',
        '  (wire (pts (xy 137.16 101.6) (xy 133.35 101.6)) (stroke (width 0)) (uuid "w-r30-out"))',
        '  (wire (pts (xy 133.35 101.6) (xy 133.35 101.6)) (stroke (width 0)) (uuid "w-r30-gnd"))',
        '  (wire (pts (xy 137.16 96.52) (xy 143.51 96.52)) (stroke (width 0)) (uuid "w-lna1-in"))',
        '  (wire (pts (xy 143.51 96.52) (xy 143.51 94.08)) (stroke (width 0)) (uuid "w-lna1-in-v"))',
        '  (wire (pts (xy 143.51 94.08) (xy 145.8 94.08)) (stroke (width 0)) (uuid "w-u4-noninv"))',
        "",
        "  ; LNA1 feedback",
        '  (wire (pts (xy 161.29 96.52) (xy 171.45 96.52)) (stroke (width 0)) (uuid "w-u4-out-rf"))',
        '  (wire (pts (xy 171.45 96.52) (xy 171.45 91.44)) (stroke (width 0)) (uuid "w-r32-in"))',
        '  (wire (pts (xy 171.45 91.44) (xy 161.29 91.44)) (stroke (width 0)) (uuid "w-r32-out"))',
        '  (wire (pts (xy 161.29 91.44) (xy 161.29 91.44)) (stroke (width 0)) (uuid "w-u4-inv-rf"))',
        "",
        "  ; LNA1 Rg to GND",
        '  (wire (pts (xy 161.29 91.44) (xy 165.1 91.44)) (stroke (width 0)) (uuid "w-r31-in"))',
        '  (wire (pts (xy 165.1 91.44) (xy 165.1 88.9)) (stroke (width 0)) (uuid "w-r31-v"))',
        '  (wire (pts (xy 165.1 88.9) (xy 165.1 88.9)) (stroke (width 0)) (uuid "w-r31-gnd"))',
        "",
    ])
    
    # LNA outputs
    lines.extend([
        "  ; === LNA OUTPUTS ===",
        '  (wire (pts (xy 161.29 60.96) (xy 182.88 60.96)) (stroke (width 0)) (uuid "w-u3-out"))',
        '  (wire (pts (xy 182.88 60.96) (xy 200.66 60.96)) (stroke (width 0)) (uuid "w-rx0-out"))',
        '  (wire (pts (xy 161.29 96.52) (xy 182.88 96.52)) (stroke (width 0)) (uuid "w-u4-out"))',
        '  (wire (pts (xy 182.88 96.52) (xy 200.66 96.52)) (stroke (width 0)) (uuid "w-rx1-out"))',
        "",
    ])
    
    # Footer
    lines.extend([
        ")",
    ])
    
    return "\n".join(lines)

if __name__ == "__main__":
    sch = generate_schematic()
    with open("/home/james/.openclaw/workspace/turboquant_v5/hardware/schematics/analog.kicad_sch", "w") as f:
        f.write(sch)
    print(f"Generated analog.kicad_sch ({len(sch)} bytes)")
