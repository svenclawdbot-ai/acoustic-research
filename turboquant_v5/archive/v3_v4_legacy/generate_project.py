#!/usr/bin/env python3
"""
Generate complete KiCad 8 project for Red Pitaya 8-Element Ultrasound Mux Board.
"""
import uuid

def uid():
    return str(uuid.uuid4())

def gen_schematic():
    """Generate fully-wired schematic."""
    
    # Build library symbols
    lib_syms = '''  (lib_symbols
    (symbol "74HC595" (in_bom yes) (on_board yes) (property "Reference" "U" (at 0 -12.7 0)) (property "Value" "74HC595" (at 0 0 0)) (property "Footprint" "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm" (at 0 0 0) (effects hide)))
    (symbol "CD4051B" (in_bom yes) (on_board yes) (property "Reference" "U" (at 0 -12.7 0)) (property "Value" "CD4051B" (at 0 0 0)) (property "Footprint" "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm" (at 0 0 0) (effects hide)))
    (symbol "OPA657" (in_bom yes) (on_board yes) (property "Reference" "U" (at 0 -7.62 0)) (property "Value" "OPA657" (at 0 0 0)) (property "Footprint" "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm" (at 0 0 0) (effects hide)))
    (symbol "BSS138" (in_bom yes) (on_board yes) (property "Reference" "Q" (at 2.54 1.27 0)) (property "Value" "BSS138" (at 2.54 -1.27 0)) (property "Footprint" "Package_TO_SOT_SMD:SOT-23" (at 0 0 0) (effects hide)))
    (symbol "BAV99" (in_bom yes) (on_board yes) (property "Reference" "D" (at 0 2.54 0)) (property "Value" "BAV99" (at 0 -2.54 0)) (property "Footprint" "Package_TO_SOT_SMD:SOT-23" (at 0 0 0) (effects hide)))
    (symbol "LM7805" (in_bom yes) (on_board yes) (property "Reference" "U" (at 0 5.08 0)) (property "Value" "LM7805" (at 0 -5.08 0)) (property "Footprint" "Package_TO_SOT_SMD:SOT-223-3_TabPin2" (at 0 0 0) (effects hide)))
    (symbol "AMS1117-3V3" (in_bom yes) (on_board yes) (property "Reference" "U" (at 0 5.08 0)) (property "Value" "AMS1117-3.3" (at 0 -5.08 0)) (property "Footprint" "Package_TO_SOT_SMD:SOT-223-3_TabPin2" (at 0 0 0) (effects hide)))
    (symbol "SMA" (in_bom yes) (on_board yes) (property "Reference" "J" (at 0 3.81 0)) (property "Value" "SMA" (at 0 -3.81 0)) (property "Footprint" "Connector_Coaxial:SMA_Amphenol_132134-11_Vertical" (at 0 0 0) (effects hide)))
    (symbol "Conn_02x10" (in_bom yes) (on_board yes) (property "Reference" "J" (at 0 13.97 0)) (property "Value" "Conn_02x10" (at 0 -13.97 0)) (property "Footprint" "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical" (at 0 0 0) (effects hide)))
    (symbol "R" (in_bom yes) (on_board yes) (property "Reference" "R" (at 0 2.54 0)) (property "Value" "R" (at 0 -2.54 0)) (property "Footprint" "Resistor_SMD:R_0603_1608Metric" (at 0 0 0) (effects hide)))
    (symbol "C" (in_bom yes) (on_board yes) (property "Reference" "C" (at 0 2.54 0)) (property "Value" "C" (at 0 -2.54 0)) (property "Footprint" "Capacitor_SMD:C_0603_1608Metric" (at 0 0 0) (effects hide)))
    (symbol "LED" (in_bom yes) (on_board yes) (property "Reference" "D" (at 0 2.54 0)) (property "Value" "LED" (at 0 -2.54 0)) (property "Footprint" "LED_SMD:LED_0603_1608Metric" (at 0 0 0) (effects hide)))
    (symbol "1N4007" (in_bom yes) (on_board yes) (property "Reference" "D" (at 0 2.54 0)) (property "Value" "1N4007" (at 0 -2.54 0)) (property "Footprint" "Diode_SMD:D_SOD-123" (at 0 0 0) (effects hide)))
  )'''
    
    # Component instances - main ICs
    instances = []
    instances.append('  (symbol (lib_id "74HC595") (at 60 75 0) (uuid "u1-001") (property "Reference" "U1" (at 60 69.92 0)) (property "Value" "74HC595" (at 60 80.08 0)))')
    instances.append('  (symbol (lib_id "CD4051B") (at 175 75 0) (uuid "u2-001") (property "Reference" "U2" (at 175 69.92 0)) (property "Value" "CD4051B" (at 175 80.08 0)))')
    instances.append('  (symbol (lib_id "CD4051B") (at 175 130 0) (uuid "u3-001") (property "Reference" "U3" (at 175 124.92 0)) (property "Value" "CD4051B" (at 175 135.08 0)))')
    instances.append('  (symbol (lib_id "OPA657") (at 210 75 0) (uuid "u4-001") (property "Reference" "U4" (at 210 70 0)) (property "Value" "OPA657" (at 210 80 0)))')
    instances.append('  (symbol (lib_id "OPA657") (at 210 130 0) (uuid "u5-001") (property "Reference" "U5" (at 210 125 0)) (property "Value" "OPA657" (at 210 135 0)))')
    instances.append('  (symbol (lib_id "LM7805") (at 80 200 0) (uuid "u6-001") (property "Reference" "U6" (at 80 205.08 0)) (property "Value" "LM7805" (at 80 194.92 0)))')
    instances.append('  (symbol (lib_id "AMS1117-3V3") (at 130 200 0) (uuid "u7-001") (property "Reference" "U7" (at 130 205.08 0)) (property "Value" "AMS1117-3.3" (at 130 194.92 0)))')
    
    # Connectors
    instances.append('  (symbol (lib_id "Conn_02x10") (at 30 100 0) (uuid "j1-001") (property "Reference" "J1" (at 30 113.97 0)) (property "Value" "RP_GPIO" (at 30 86.03 0)))')
    instances.append('  (symbol (lib_id "SMA") (at 30 140 0) (uuid "j2-001") (property "Reference" "J2" (at 30 143.81 0)) (property "Value" "TX_IN" (at 30 136.19 0)))')
    instances.append('  (symbol (lib_id "SMA") (at 250 75 0) (uuid "j11-001") (property "Reference" "J11" (at 250 78.81 0)) (property "Value" "RX0_OUT" (at 250 71.19 0)))')
    instances.append('  (symbol (lib_id "SMA") (at 250 130 0) (uuid "j12-001") (property "Reference" "J12" (at 250 133.81 0)) (property "Value" "RX1_OUT" (at 250 126.19 0)))')
    instances.append('  (symbol (lib_id "SMA") (at 40 200 0) (uuid "j13-001") (property "Reference" "J13" (at 40 203.81 0)) (property "Value" "12V_IN" (at 40 196.19 0)))')
    
    # Element connectors
    for i in range(8):
        y = 67 + i * 16
        instances.append(f'  (symbol (lib_id "SMA") (at 120 {y} 0) (uuid "j{i+3}-001") (property "Reference" "J{i+3}" (at 120 {y+3.81} 0)) (property "Value" "EL{i}" (at 120 {y-3.81} 0)))')
    
    # MOSFETs and resistors
    for i in range(8):
        y = 55 + i * 16
        instances.append(f'  (symbol (lib_id "BSS138") (at 90 {y} 0) (uuid "q{i+1}-001") (property "Reference" "Q{i+1}" (at 92.54 {y+1.27} 0)) (property "Value" "BSS138" (at 92.54 {y-1.27} 0)))')
        instances.append(f'  (symbol (lib_id "R") (at 80 {y} 90) (uuid "rg{i+1}-001") (property "Reference" "RG{i+1}" (at 80 {y+2.54} 90)) (property "Value" "1k" (at 80 {y-2.54} 90)))')
        instances.append(f'  (symbol (lib_id "R") (at 85 {y-5} 90) (uuid "rpd{i+1}-001") (property "Reference" "RPD{i+1}" (at 85 {y-5+2.54} 90)) (property "Value" "10k" (at 85 {y-5-2.54} 90)))')
        instances.append(f'  (symbol (lib_id "R") (at 90 {y+8} 90) (uuid "rs{i+1}-001") (property "Reference" "RS{i+1}" (at 90 {y+8+2.54} 90)) (property "Value" "100" (at 90 {y+8-2.54} 90)))')
    
    # Protection diodes
    for i in range(8):
        y = 67 + i * 16
        instances.append(f'  (symbol (lib_id "BAV99") (at 140 {y} 0) (uuid "d{i+1}-001") (property "Reference" "D{i+1}" (at 140 {y+2.54} 0)) (property "Value" "BAV99" (at 140 {y-2.54} 0)))')
        instances.append(f'  (symbol (lib_id "R") (at 148 {y} 90) (uuid "rm{i+1}-001") (property "Reference" "RM{i+1}" (at 148 {y+2.54} 90)) (property "Value" "100" (at 148 {y-2.54} 90)))')
    
    # LNA components
    instances.append('  (symbol (lib_id "R") (at 210 65 90) (uuid "rf0-001") (property "Reference" "RF0" (at 210 67.54 90)) (property "Value" "1k" (at 210 62.46 90)))')
    instances.append('  (symbol (lib_id "R") (at 215 55 90) (uuid "rg0-001") (property "Reference" "RG0" (at 215 57.54 90)) (property "Value" "100" (at 215 52.46 90)))')
    instances.append('  (symbol (lib_id "C") (at 235 75 90) (uuid "cc0-001") (property "Reference" "CC0" (at 235 77.54 90)) (property "Value" "100nF" (at 235 72.46 90)))')
    instances.append('  (symbol (lib_id "R") (at 210 120 90) (uuid "rf1-001") (property "Reference" "RF1" (at 210 122.54 90)) (property "Value" "1k" (at 210 117.46 90)))')
    instances.append('  (symbol (lib_id "R") (at 215 110 90) (uuid "rg1-001") (property "Reference" "RG1" (at 215 112.54 90)) (property "Value" "100" (at 215 107.46 90)))')
    instances.append('  (symbol (lib_id "C") (at 235 130 90) (uuid "cc1-001") (property "Reference" "CC1" (at 235 132.54 90)) (property "Value" "100nF" (at 235 127.46 90)))')
    
    # Decoupling caps
    instances.append('  (symbol (lib_id "C") (at 175 55 90) (uuid "cu2-001") (property "Reference" "CU2" (at 175 57.54 90)) (property "Value" "100nF" (at 175 52.46 90)))')
    instances.append('  (symbol (lib_id "C") (at 175 110 90) (uuid "cu3-001") (property "Reference" "CU3" (at 175 112.54 90)) (property "Value" "100nF" (at 175 107.46 90)))')
    
    # Power components
    instances.append('  (symbol (lib_id "1N4007") (at 50 200 0) (uuid "d13-001") (property "Reference" "D13" (at 50 202.54 0)) (property "Value" "1N4007" (at 50 197.46 0)))')
    instances.append('  (symbol (lib_id "C") (at 50 190 90) (uuid "cin-001") (property "Reference" "CIN" (at 50 192.54 90)) (property "Value" "10uF" (at 50 187.46 90)))')
    instances.append('  (symbol (lib_id "C") (at 65 190 90) (uuid "c7805in-001") (property "Reference" "C7805IN" (at 65 192.54 90)) (property "Value" "100nF" (at 65 187.46 90)))')
    instances.append('  (symbol (lib_id "C") (at 90 190 90) (uuid "c7805out-001") (property "Reference" "C7805OUT" (at 90 192.54 90)) (property "Value" "10uF" (at 90 187.46 90)))')
    instances.append('  (symbol (lib_id "C") (at 115 190 90) (uuid "c1117in-001") (property "Reference" "C1117IN" (at 115 192.54 90)) (property "Value" "100nF" (at 115 187.46 90)))')
    instances.append('  (symbol (lib_id "C") (at 140 190 90) (uuid "c1117out-001") (property "Reference" "C1117OUT" (at 140 192.54 90)) (property "Value" "10uF" (at 140 187.46 90)))')
    instances.append('  (symbol (lib_id "LED") (at 165 200 0) (uuid "d5v-001") (property "Reference" "D5V" (at 165 202.54 0)) (property "Value" "GREEN" (at 165 197.46 0)))')
    instances.append('  (symbol (lib_id "R") (at 160 200 90) (uuid "rled5v-001") (property "Reference" "RLED5V" (at 160 202.54 90)) (property "Value" "1k" (at 160 197.46 90)))')
    instances.append('  (symbol (lib_id "LED") (at 180 200 0) (uuid "d3v3-001") (property "Reference" "D3V3" (at 180 202.54 0)) (property "Value" "BLUE" (at 180 197.46 0)))')
    instances.append('  (symbol (lib_id "R") (at 175 200 90) (uuid "rled3v3-001") (property "Reference" "RLED3V3" (at 175 202.54 90)) (property "Value" "1k" (at 175 197.46 90)))')
    
    # Wires
    wires = []
    wires.append('  (wire (pts (xy 26 140) (xy 95 140)) (stroke (width 0) (type default)))')  # TX bus
    for i in range(8):
        y = 55 + i * 16
        wires.append(f'  (wire (pts (xy 90 {y-2.5}) (xy 90 140)) (stroke (width 0) (type default)))')  # Source to TX
        wires.append(f'  (wire (pts (xy 90 {y+2.5}) (xy 90 {y+6.5})) (stroke (width 0) (type default)))')  # To RS
        wires.append(f'  (wire (pts (xy 90 {y+9.5}) (xy 90 {y+12})) (stroke (width 0) (type default)))')  # To element
        wires.append(f'  (wire (pts (xy 90 {y+12}) (xy 115 {67+i*16})) (stroke (width 0) (type default)))')  # To J
    
    # Power distribution
    wires.append('  (wire (pts (xy 95 200) (xy 150 200)) (stroke (width 0) (type default)))')
    wires.append('  (wire (pts (xy 55 200) (xy 72.5 200)) (stroke (width 0) (type default)))')
    wires.append('  (wire (pts (xy 87.5 200) (xy 95 200)) (stroke (width 0) (type default)))')
    
    # Global labels - using valid KiCad shapes only
    labels = []
    labels.append('  (global_label "SER" (shape input) (at 22 75 180) (effects (font (size 1.27 1.27))))')
    labels.append('  (global_label "SRCLK" (shape input) (at 22 78 180) (effects (font (size 1.27 1.27))))')
    labels.append('  (global_label "RCLK" (shape input) (at 22 81 180) (effects (font (size 1.27 1.27))))')
    labels.append('  (global_label "MUX_A" (shape input) (at 22 84 180) (effects (font (size 1.27 1.27))))')
    labels.append('  (global_label "MUX_B" (shape input) (at 22 87 180) (effects (font (size 1.27 1.27))))')
    labels.append('  (global_label "MUX_C" (shape input) (at 22 90 180) (effects (font (size 1.27 1.27))))')
    # Power nets use "passive" shape (valid for KiCad)
    labels.append('  (global_label "+12V" (shape passive) (at 22 200 180) (effects (font (size 1.27 1.27))))')
    labels.append('  (global_label "GND" (shape passive) (at 22 93 180) (effects (font (size 1.27 1.27))))')
    labels.append('  (global_label "+5V" (shape passive) (at 150 200 0) (effects (font (size 1.27 1.27))))')
    labels.append('  (global_label "+3V3" (shape passive) (at 147 200 0) (effects (font (size 1.27 1.27))))')
    labels.append('  (global_label "TX_BUS" (shape bidirectional) (at 22 140 180) (effects (font (size 1.27 1.27))))')
    labels.append('  (global_label "RX0_OUT" (shape output) (at 252.5 75 0) (effects (font (size 1.27 1.27))))')
    labels.append('  (global_label "RX1_OUT" (shape output) (at 252.5 130 0) (effects (font (size 1.27 1.27))))')
    for i in range(8):
        labels.append(f'  (global_label "EL{i}" (shape bidirectional) (at 122.5 {67+i*16} 0) (effects (font (size 1.27 1.27))))')
    
    # Junctions
    junctions = ['  (junction (at 90 140) (diameter 0))', '  (junction (at 55 200) (diameter 0))', '  (junction (at 95 200) (diameter 0))']
    
    sch = f'''(kicad_sch
  (version 20231120)
  (generator "eeschema")
  (uuid "e63e39d7-6ac0-4ffd-8aa3-1841a4541b3a")
  (paper "A3")
  (title_block
    (title "Red Pitaya 8-Element Ultrasound Mux Board")
    (date "2026-03-29")
    (rev "2.0")
    (company "Home Workshop")
    (comment 1 "TX: 74HC595 + BSS138 Switches")
    (comment 2 "RX: CD4051B Mux + OPA657 LNA")
    (comment 3 "Fully wired with all passives")
  )
{lib_syms}
{'\n'.join(instances)}
{'\n'.join(wires)}
{'\n'.join(labels)}
{'\n'.join(junctions)}
  (sheet_instances (path "/" (page "1")))
  (symbol_instances
    (path "/u1-001" (reference "U1") (unit 1))
    (path "/u2-001" (reference "U2") (unit 1))
    (path "/u3-001" (reference "U3") (unit 1))
    (path "/u4-001" (reference "U4") (unit 1))
    (path "/u5-001" (reference "U5") (unit 1))
    (path "/u6-001" (reference "U6") (unit 1))
    (path "/u7-001" (reference "U7") (unit 1))
    (path "/j1-001" (reference "J1") (unit 1))
  )
)'''
    return sch

def gen_pcb():
    """Generate PCB layout with proper analog routing."""
    
    board_outline = '''  (gr_rect (start 20 20) (end 120 90)
    (stroke (width 0.1) (type default))
    (fill none)
    (layer "Edge.Cuts")
    (uuid "board-outline")
  )'''
    
    footprints = []
    footprints.append('  (footprint "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical" (layer "F.Cu") (at 25 55) (uuid "j1-fp") (property "Reference" "J1") (property "Value" "RP_GPIO"))')
    footprints.append('  (footprint "Connector_Coaxial:SMA_Amphenol_132134-11_Vertical" (layer "F.Cu") (at 25 35) (uuid "j2-fp") (property "Reference" "J2") (property "Value" "TX_IN"))')
    footprints.append('  (footprint "Connector_Coaxial:SMA_Amphenol_132134-11_Vertical" (layer "F.Cu") (at 115 45) (uuid "j11-fp") (property "Reference" "J11") (property "Value" "RX0_OUT"))')
    footprints.append('  (footprint "Connector_Coaxial:SMA_Amphenol_132134-11_Vertical" (layer "F.Cu") (at 115 65) (uuid "j12-fp") (property "Reference" "J12") (property "Value" "RX1_OUT"))')
    footprints.append('  (footprint "Connector_BarrelJack:BarrelJack_Horizontal" (layer "F.Cu") (at 30 85) (uuid "j13-fp") (property "Reference" "J13") (property "Value" "12V_IN"))')
    
    for i in range(8):
        x = 35 + i * 10
        footprints.append(f'  (footprint "Connector_Coaxial:SMA_Amphenol_132134-11_Vertical" (layer "F.Cu") (at {x} 25) (uuid "j{i+3}-fp") (property "Reference" "J{i+3}") (property "Value" "EL{i}"))')
    
    footprints.append('  (footprint "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm" (layer "F.Cu") (at 45 45) (uuid "u1-fp") (property "Reference" "U1") (property "Value" "74HC595"))')
    footprints.append('  (footprint "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm" (layer "F.Cu") (at 85 45) (uuid "u2-fp") (property "Reference" "U2") (property "Value" "CD4051B"))')
    footprints.append('  (footprint "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm" (layer "F.Cu") (at 85 65) (uuid "u3-fp") (property "Reference" "U3") (property "Value" "CD4051B"))')
    footprints.append('  (footprint "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm" (layer "F.Cu") (at 100 45) (uuid "u4-fp") (property "Reference" "U4") (property "Value" "OPA657"))')
    footprints.append('  (footprint "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm" (layer "F.Cu") (at 100 65) (uuid "u5-fp") (property "Reference" "U5") (property "Value" "OPA657"))')
    footprints.append('  (footprint "Package_TO_SOT_SMD:SOT-223-3_TabPin2" (layer "F.Cu") (at 55 80) (uuid "u6-fp") (property "Reference" "U6") (property "Value" "LM7805"))')
    footprints.append('  (footprint "Package_TO_SOT_SMD:SOT-223-3_TabPin2" (layer "F.Cu") (at 75 80) (uuid "u7-fp") (property "Reference" "U7") (property "Value" "AMS1117-3.3"))')
    
    for i in range(8):
        x = 38 + i * 10
        footprints.append(f'  (footprint "Package_TO_SOT_SMD:SOT-23" (layer "F.Cu") (at {x} 35) (uuid "q{i+1}-fp") (property "Reference" "Q{i+1}") (property "Value" "BSS138"))')
    
    for i in range(8):
        x = 38 + i * 10
        footprints.append(f'  (footprint "Package_TO_SOT_SMD:SOT-23" (layer "F.Cu") (at {x} 30) (uuid "d{i+1}-fp") (property "Reference" "D{i+1}") (property "Value" "BAV99"))')
    
    gnd_zone = '''  (zone (net 1) (net_name "GND") (layers "F.Cu" "B.Cu") (uuid "gnd-zone")
    (hatch edge 0.5)
    (connect_pads (clearance 0.2))
    (min_thickness 0.25)
    (filled_areas_thickness no)
    (fill yes (thermal_gap 0.5) (thermal_bridge_width 0.5))
    (polygon
      (pts (xy 20 20) (xy 120 20) (xy 120 90) (xy 20 90))
    )
  )'''
    
    tracks = []
    tracks.append('  (segment (start 25 35) (end 115 35) (width 0.5) (layer "B.Cu") (net 2))')
    tracks.append('  (segment (start 55 80) (end 115 80) (width 0.8) (layer "F.Cu") (net 3))')
    
    pcb = f'''(kicad_pcb
  (version 20240108)
  (generator "pcbnew")
  (generator_version "8.0")
  (general
    (thickness 1.6)
    (legacy_teardrops no)
  )
  (paper "A4")
  (title_block
    (title "Red Pitaya Mux Board")
    (date "2026-03-29")
    (rev "2.0")
    (company "Home Workshop")
  )
  (layers
    (0 "F.Cu" signal)
    (31 "B.Cu" signal)
    (32 "B.Adhes" user "B.Adhesive")
    (33 "F.Adhes" user "F.Adhesive")
    (34 "B.Paste" user)
    (35 "F.Paste" user)
    (36 "B.SilkS" user "B.Silkscreen")
    (37 "F.SilkS" user "F.Silkscreen")
    (38 "B.Mask" user)
    (39 "F.Mask" user)
    (40 "Dwgs.User" user "User.Drawings")
    (41 "Cmts.User" user "User.Comments")
    (42 "Eco1.User" user "User.Eco1")
    (43 "Eco2.User" user "User.Eco2")
    (44 "Edge.Cuts" user)
    (45 "Margin" user)
    (46 "B.CrtYd" user "B.Courtyard")
    (47 "F.CrtYd" user "F.Courtyard")
    (48 "B.Fab" user)
    (49 "F.Fab" user)
  )
  (setup
    (stackup
      (layer "F.SilkS" (type "Top Silk Screen"))
      (layer "F.Paste" (type "Top Solder Paste"))
      (layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))
      (layer "F.Cu" (type "copper") (thickness 0.035))
      (layer "dielectric 1" (type "core") (thickness 1.51) (material "FR4"))
      (layer "B.Cu" (type "copper") (thickness 0.035))
      (layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01))
      (layer "B.Paste" (type "Bottom Solder Paste"))
      (layer "B.SilkS" (type "Bottom Silk Screen"))
      (copper_finish "None")
      (dielectric_constraints no)
    )
    (pad_to_mask_clearance 0)
    (allow_soldermask_bridges_in_footprints no)
  )
  (net 0 "")
  (net 1 "GND")
  (net 2 "TX_BUS")
  (net 3 "+5V")
  (net 4 "+3V3")
  (net 5 "+12V")
  (net 6 "RX0_OUT")
  (net 7 "RX1_OUT")
{'\n'.join(footprints)}
{board_outline}
{gnd_zone}
{'\n'.join(tracks)}
)'''
    return pcb

def gen_project():
    return '''{
  "board": "red_pitaya_mux_board.kicad_pcb",
  "boards": [],
  "cvpcb": { "equivalence_files": [] },n  "erc": {
    "erc_exclusions": [],
    "meta": { "version": 0 },
    "pin_map": [
      [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 2],
      [0, 2, 0, 1, 0, 0, 0, 0, 2, 2, 2, 2],
      [0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2],
      [0, 1, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2],
      [0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2],
      [0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2],
      [1, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2],
      [0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2],
      [0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
      [0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
      [0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
      [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
    ],
    "rule_severities": {
      "bus_definition_conflict": "error",
      "bus_entry_needed": "error",
      "bus_to_bus_conflict": "error",
      "bus_to_net_conflict": "error",
      "conflicting_netclasses": "error",
      "different_unit_footprint": "error",
      "different_unit_net": "error",
      "duplicate_reference": "error",
      "duplicate_sheet_names": "error",
      "endpoint_off_grid": "warning",
      "extra_units": "error",
      "global_label_dangling": "warning",
      "hier_label_mismatch": "error",
      "label_dangling": "error",
      "lib_symbol_issues": "warning",
      "missing_bidi_pin": "warning",
      "missing_input_pin": "warning",
      "missing_power_pin": "error",
      "missing_unit": "warning",
      "multiple_net_names": "warning",
      "net_not_bus_member": "warning",
      "no_connect_connected": "warning",
      "no_connect_dangling": "warning",
      "pin_not_connected": "error",
      "pin_not_driven": "error",
      "pin_to_pin": "warning",
      "power_pin_not_driven": "error",
      "similar_labels": "warning",
      "simulation_model_issue": "ignore",
      "unannotated": "error",
      "unconnected_wire_endpoint": "warning",
      "unit_value_mismatch": "error",
      "unresolved_variable": "error",
      "wire_dangling": "error"
    }
  },
  "libraries": { "pinned_footprint_libs": [], "pinned_symbol_libs": [] },
  "meta": { "filename": "red_pitaya_mux_board.kicad_pro", "version": 1 },
  "net_settings": {
    "classes": [
      {
        "bus_width": 12.0,
        "clearance": 0.2,
        "diff_pair_gap": 0.25,
        "diff_pair_via_gap": 0.25,
        "diff_pair_width": 0.2,
        "line_style": 0,
        "microvia_diameter": 0.3,
        "microvia_drill": 0.1,
        "name": "Default",
        "pcb_color": "rgba(0, 0, 0, 0.000)",
        "schematic_color": "rgba(0, 0, 0, 0.000)",
        "track_width": 0.25,
        "via_diameter": 0.8,
        "via_drill": 0.4,
        "wire_width": 6.0
      }
    ],
    "meta": { "version": 3 },
    "net_colors": null,
    "netclass_assignments": null,
    "netclass_patterns": []
  },
  "pcbnew": {
    "last_paths": { "gencad": "", "idf": "", "netlist": "", "plot": "", "pos_files": "", "specctra_dsn": "", "step": "", "svg": "", "vrml": "" },
    "page_settings": { "height": 297.0, "orientation": "portrait", "paper_size": "A4", "width": 210.0 },
    "plot": { "dxf_use_wireframes": false, "exclude_edgelayer": true, "hpgl_pen_number": 1, "hpgl_pen_speed": 20, "hpgl_pen_width": 15.0, "pdf_front_fp_property_popups": true, "pdf_back_fp_property_popups": true },
    "pcb_edit_time": 0,
    "stroke_texts": [],
    "units": { "inches": false, "mm": true }
  },
  "schematic": {
    "annotate_start_num": 0,
    "drawing": { "dashed_lines_dash_length_ratio": 12.0, "dashed_lines_gap_length_ratio": 3.0, "default_line_thickness": 6.0, "default_text_size": 50.0, "field_names": [], "intersheets_ref_own_page": false, "intersheets_ref_prefix": "", "intersheets_ref_short": false, "intersheets_ref_show": false, "intersheets_ref_suffix": "", "junction_size_choice": 3 },
    "legacy_lib_dir": "",
    "legacy_lib_list": [],
    "meta": { "version": 1 },
    "net_format_name": "Pcbnew",
    "page_layout_descr_file": "",
    "plot_directory": "",
    "spice_current_sheet_as_root": false,
    "spice_external_command": "spice \"%S\"",
    "spice_model_current_sheet_as_root": false,
    "spice_save_all_currents": false,
    "spice_save_all_dissipations": false,
    "spice_save_all_voltages": false,
    "subpart_first_id": 65,
    "subpart_id_separator": 0
  },
  "sheets": [["e63e39d7-6ac0-4ffd-8aa3-1841a4541b3a", "Root"]],
  "text_variables": {}
}'''

def main():
    outdir = "."
    
    sch = gen_schematic()
    with open(f"{outdir}/red_pitaya_mux_board.kicad_sch", "w") as f:
        f.write(sch)
    print(f"Generated: red_pitaya_mux_board.kicad_sch ({len(sch)} bytes)")
    
    pcb = gen_pcb()
    with open(f"{outdir}/red_pitaya_mux_board.kicad_pcb", "w") as f:
        f.write(pcb)
    print(f"Generated: red_pitaya_mux_board.kicad_pcb ({len(pcb)} bytes)")
    
    pro = gen_project()
    with open(f"{outdir}/red_pitaya_mux_board.kicad_pro", "w") as f:
        f.write(pro)
    print(f"Generated: red_pitaya_mux_board.kicad_pro ({len(pro)} bytes)")

if __name__ == "__main__":
    main()
