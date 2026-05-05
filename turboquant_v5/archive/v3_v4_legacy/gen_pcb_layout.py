#!/usr/bin/env python3
"""
Generate optimized PCB layout for Red Pitaya Mux Board.
Board: 100mm x 70mm, 2-layer
"""
import uuid

def uid():
    return str(uuid.uuid4())

def gen_pcb():
    # Board outline: 100mm x 70mm (origin at 20,20)
    # Effective area: x=20 to 120, y=20 to 90
    
    header = '''(kicad_pcb
  (version 20240108)
  (generator "pcbnew")
  (generator_version "8.0")
  (general
    (thickness 1.6)
    (legacy_teardrops no)
  )
  (paper "A4")
  (title_block
    (title "Red Pitaya 8-Element Ultrasound Mux Board")
    (date "2026-03-29")
    (rev "2.1")
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
    (pcbplotparams
      (layerselection 0x00010fc_ffffffff)
      (plot_on_all_layers_selection 0x0000000_00000000)
      (disableapertmacros no)
      (usegerberextensions no)
      (usegerberattributes yes)
      (usegerberadvancedattributes yes)
      (creategerberjobfile yes)
      (dashed_line_dash_ratio 12.000000)
      (dashed_line_gap_ratio 3.000000)
      (svgprecision 4)
      (plotframeref no)
      (viasonmask no)
      (mode 1)
      (useauxorigin no)
      (hpglpennumber 1)
      (hpglpenspeed 20)
      (hpglpendiameter 15.000000)
      (pdf_front_fp_property_popups yes)
      (pdf_back_fp_property_popups yes)
      (dxfpolygonmode yes)
      (dxfimperialunits yes)
      (dxfusepcbnewfont yes)
      (psnegative no)
      (psa4output no)
      (plotreference yes)
      (plotvalue yes)
      (plotfptext yes)
      (plotinvisibletext no)
      (sketchpadsonfab no)
      (subtractmaskfromsilk no)
      (outputformat 1)
      (mirror no)
      (drillshape 1)
      (scaleselection 1)
      (outputdirectory "")
    )
  )'''
    
    # Net definitions
    nets = '''  (net 0 "")
  (net 1 "GND")
  (net 2 "TX_BUS")
  (net 3 "+5V")
  (net 4 "+3V3")
  (net 5 "+12V")
  (net 6 "RX0_OUT")
  (net 7 "RX1_OUT")
  (net 8 "SER")
  (net 9 "SRCLK")
  (net 10 "RCLK")
  (net 11 "MUX_A")
  (net 12 "MUX_B")
  (net 13 "MUX_C")
  (net 14 "EL0")
  (net 15 "EL1")
  (net 16 "EL2")
  (net 17 "EL3")
  (net 18 "EL4")
  (net 19 "EL5")
  (net 20 "EL6")
  (net 21 "EL7")
  (net 22 "MUX0_COM")
  (net 23 "MUX1_COM")
  (net 24 "Net-(U1-QA)")
  (net 25 "Net-(U1-QB)")
  (net 26 "Net-(U1-QC)")
  (net 27 "Net-(U1-QD)")
  (net 28 "Net-(U1-QE)")
  (net 29 "Net-(U1-QF)")
  (net 30 "Net-(U1-QG)")
  (net 31 "Net-(U1-QH)")'''
    
    footprints = []
    
    # === LEFT SIDE: Red Pitaya Interface ===
    # J1: GPIO Header (2x10) - Left edge, middle
    footprints.append('  (footprint "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical" (layer "F.Cu") (at 28 55 90) (uuid "fp-j1") (property "Reference" "J1" (at 0 -13.97 90)) (property "Value" "RP_GPIO" (at 0 13.97 90)) (pad "" thru_hole rect (at -1.27 -11.43 90) (size 1.7 1.7) (drill 1) (layers "*.Cu" "*.Mask")))')
    
    # J2: TX Input SMA - Left edge, top
    footprints.append('  (footprint "Connector_Coaxial:SMA_Amphenol_132134-11_Vertical" (layer "F.Cu") (at 28 30 0) (uuid "fp-j2") (property "Reference" "J2" (at 0 5.08 0)) (property "Value" "TX_IN" (at 0 -5.08 0)))')
    
    # J13: 12V Power Input - Left edge, bottom
    footprints.append('  (footprint "Connector_BarrelJack:BarrelJack_Horizontal" (layer "F.Cu") (at 28 80 0) (uuid "fp-j13") (property "Reference" "J13" (at 0 5.08 0)) (property "Value" "12V_IN" (at 0 -5.08 0)))')
    
    # === CENTER-LEFT: TX Section ===
    # U1: 74HC595 Shift Register
    footprints.append('  (footprint "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm" (layer "F.Cu") (at 50 45 0) (uuid "fp-u1") (property "Reference" "U1" (at 0 -6.5 0)) (property "Value" "74HC595" (at 0 6.5 0)))')
    
    # Q1-Q8: BSS138 MOSFETs (in a column below U1)
    for i in range(8):
        y = 60 + i * 3.5
        footprints.append(f'  (footprint "Package_TO_SOT_SMD:SOT-23" (layer "F.Cu") (at 45 {y} 0) (uuid "fp-q{i+1}") (property "Reference" "Q{i+1}" (at 0 -2.5 0)) (property "Value" "BSS138" (at 0 2.5 0)))')
    
    # RG1-RG8: Gate resistors (1k) - next to MOSFETs
    for i in range(8):
        y = 60 + i * 3.5
        footprints.append(f'  (footprint "Resistor_SMD:R_0603_1608Metric" (layer "F.Cu") (at 52 {y} 0) (uuid "fp-rg{i+1}") (property "Reference" "RG{i+1}" (at 0 -1.5 0)) (property "Value" "1k" (at 0 1.5 0)))')
    
    # RPD1-RPD8: Pull-down resistors (10k)
    for i in range(8):
        y = 60 + i * 3.5
        footprints.append(f'  (footprint "Resistor_SMD:R_0603_1608Metric" (layer "F.Cu") (at 38 {y} 0) (uuid "fp-rpd{i+1}") (property "Reference" "RPD{i+1}" (at 0 -1.5 0)) (property "Value" "10k" (at 0 1.5 0)))')
    
    # RS1-RS8: Series resistors (100) - between MOSFETs and elements
    for i in range(8):
        y = 60 + i * 3.5
        footprints.append(f'  (footprint "Resistor_SMD:R_0603_1608Metric" (layer "F.Cu") (at 62 {y} 90) (uuid "fp-rs{i+1}") (property "Reference" "RS{i+1}" (at 2 0 90)) (property "Value" "100" (at -2 0 90)))')
    
    # === TOP EDGE: Element Connectors ===
    # J3-J10: Element SMA connectors (evenly spaced)
    for i in range(8):
        x = 40 + i * 9
        footprints.append(f'  (footprint "Connector_Coaxial:SMA_Amphenol_132134-11_Vertical" (layer "F.Cu") (at {x} 25 0) (uuid "fp-j{i+3}") (property "Reference" "J{i+3}" (at 0 5.08 0)) (property "Value" "EL{i}" (at 0 -5.08 0)))')
    
    # D1-D8: BAV99 Protection diodes (below element connectors)
    for i in range(8):
        x = 40 + i * 9
        footprints.append(f'  (footprint "Package_TO_SOT_SMD:SOT-23" (layer "F.Cu") (at {x} 32 0) (uuid "fp-d{i+1}") (property "Reference" "D{i+1}" (at 0 -2.5 0)) (property "Value" "BAV99" (at 0 2.5 0)))')
    
    # RM1-RM8: Mux input resistors (100)
    for i in range(8):
        x = 40 + i * 9
        footprints.append(f'  (footprint "Resistor_SMD:R_0603_1608Metric" (layer "F.Cu") (at {x} 38 90) (uuid "fp-rm{i+1}") (property "Reference" "RM{i+1}" (at 2 0 90)) (property "Value" "100" (at -2 0 90)))')
    
    # === CENTER-RIGHT: RX Multiplexers ===
    # U2: CD4051B Mux Channel 0
    footprints.append('  (footprint "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm" (layer "F.Cu") (at 85 50 0) (uuid "fp-u2") (property "Reference" "U2" (at 0 -6.5 0)) (property "Value" "CD4051B" (at 0 6.5 0)))')
    
    # U3: CD4051B Mux Channel 1
    footprints.append('  (footprint "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm" (layer "F.Cu") (at 85 65 0) (uuid "fp-u3") (property "Reference" "U3" (at 0 -6.5 0)) (property "Value" "CD4051B" (at 0 6.5 0)))')
    
    # CU2, CU3: Decoupling caps
    footprints.append('  (footprint "Capacitor_SMD:C_0603_1608Metric" (layer "F.Cu") (at 95 50 0) (uuid "fp-cu2") (property "Reference" "CU2" (at 0 -1.5 0)) (property "Value" "100nF" (at 0 1.5 0)))')
    footprints.append('  (footprint "Capacitor_SMD:C_0603_1608Metric" (layer "F.Cu") (at 95 65 0) (uuid "fp-cu3") (property "Reference" "CU3" (at 0 -1.5 0)) (property "Value" "100nF" (at 0 1.5 0)))')
    
    # === RIGHT SIDE: LNA Amplifiers ===
    # U4: OPA657 LNA Channel 0
    footprints.append('  (footprint "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm" (layer "F.Cu") (at 105 50 0) (uuid "fp-u4") (property "Reference" "U4" (at 0 -4 0)) (property "Value" "OPA657" (at 0 4 0)))')
    
    # U5: OPA657 LNA Channel 1
    footprints.append('  (footprint "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm" (layer "F.Cu") (at 105 65 0) (uuid "fp-u5") (property "Reference" "U5" (at 0 -4 0)) (property "Value" "OPA657" (at 0 4 0)))')
    
    # RF0, RF1: Feedback resistors (1k)
    footprints.append('  (footprint "Resistor_SMD:R_0603_1608Metric" (layer "F.Cu") (at 100 42 0) (uuid "fp-rf0") (property "Reference" "RF0" (at 0 -1.5 0)) (property "Value" "1k" (at 0 1.5 0)))')
    footprints.append('  (footprint "Resistor_SMD:R_0603_1608Metric" (layer "F.Cu") (at 100 57 0) (uuid "fp-rf1") (property "Reference" "RF1" (at 0 -1.5 0)) (property "Value" "1k" (at 0 1.5 0)))')
    
    # RG0, RG1: Gain resistors (100)
    footprints.append('  (footprint "Resistor_SMD:R_0603_1608Metric" (layer "F.Cu") (at 110 42 0) (uuid "fp-rg0") (property "Reference" "RG0" (at 0 -1.5 0)) (property "Value" "100" (at 0 1.5 0)))')
    footprints.append('  (footprint "Resistor_SMD:R_0603_1608Metric" (layer "F.Cu") (at 110 57 0) (uuid "fp-rg1") (property "Reference" "RG1" (at 0 -1.5 0)) (property "Value" "100" (at 0 1.5 0)))')
    
    # CC0, CC1: AC coupling caps (100nF)
    footprints.append('  (footprint "Capacitor_SMD:C_0603_1608Metric" (layer "F.Cu") (at 112 50 90) (uuid "fp-cc0") (property "Reference" "CC0" (at 2 0 90)) (property "Value" "100nF" (at -2 0 90)))')
    footprints.append('  (footprint "Capacitor_SMD:C_0603_1608Metric" (layer "F.Cu") (at 112 65 90) (uuid "fp-cc1") (property "Reference" "CC1" (at 2 0 90)) (property "Value" "100nF" (at -2 0 90)))')
    
    # J11, J12: RX Output SMAs
    footprints.append('  (footprint "Connector_Coaxial:SMA_Amphenol_132134-11_Vertical" (layer "F.Cu") (at 115 42 0) (uuid "fp-j11") (property "Reference" "J11" (at 0 5.08 0)) (property "Value" "RX0_OUT" (at 0 -5.08 0)))')
    footprints.append('  (footprint "Connector_Coaxial:SMA_Amphenol_132134-11_Vertical" (layer "F.Cu") (at 115 73 0) (uuid "fp-j12") (property "Reference" "J12" (at 0 5.08 0)) (property "Value" "RX1_OUT" (at 0 -5.08 0)))')
    
    # === BOTTOM: Power Supply ===
    # D13: Input protection diode
    footprints.append('  (footprint "Diode_SMD:D_SOD-123" (layer "F.Cu") (at 38 75 90) (uuid "fp-d13") (property "Reference" "D13" (at 0 -2 90)) (property "Value" "1N4007" (at 0 2 90)))')
    
    # CIN: Input bulk cap (10uF)
    footprints.append('  (footprint "Capacitor_SMD:C_0805_2012Metric" (layer "F.Cu") (at 45 75 0) (uuid "fp-cin") (property "Reference" "CIN" (at 0 -1.5 0)) (property "Value" "10uF" (at 0 1.5 0)))')
    
    # U6: LM7805 Regulator
    footprints.append('  (footprint "Package_TO_SOT_SMD:SOT-223-3_TabPin2" (layer "F.Cu") (at 58 75 0) (uuid "fp-u6") (property "Reference" "U6" (at 0 4.5 0)) (property "Value" "LM7805" (at 0 -4.5 0)))')
    
    # C7805IN, C7805OUT: 7805 caps
    footprints.append('  (footprint "Capacitor_SMD:C_0603_1608Metric" (layer "F.Cu") (at 52 82 0) (uuid "fp-c7805in") (property "Reference" "C7805IN" (at 0 -1.5 0)) (property "Value" "100nF" (at 0 1.5 0)))')
    footprints.append('  (footprint "Capacitor_SMD:C_0805_2012Metric" (layer "F.Cu") (at 64 82 0) (uuid "fp-c7805out") (property "Reference" "C7805OUT" (at 0 -1.5 0)) (property "Value" "10uF" (at 0 1.5 0)))')
    
    # U7: AMS1117-3.3 Regulator
    footprints.append('  (footprint "Package_TO_SOT_SMD:SOT-223-3_TabPin2" (layer "F.Cu") (at 78 75 0) (uuid "fp-u7") (property "Reference" "U7" (at 0 4.5 0)) (property "Value" "AMS1117-3.3" (at 0 -4.5 0)))')
    
    # C1117IN, C1117OUT: 1117 caps
    footprints.append('  (footprint "Capacitor_SMD:C_0603_1608Metric" (layer "F.Cu") (at 72 82 0) (uuid "fp-c1117in") (property "Reference" "C1117IN" (at 0 -1.5 0)) (property "Value" "100nF" (at 0 1.5 0)))')
    footprints.append('  (footprint "Capacitor_SMD:C_0805_2012Metric" (layer "F.Cu") (at 84 82 0) (uuid "fp-c1117out") (property "Reference" "C1117OUT" (at 0 -1.5 0)) (property "Value" "10uF" (at 0 1.5 0)))')
    
    # Power LEDs
    footprints.append('  (footprint "LED_SMD:LED_0603_1608Metric" (layer "F.Cu") (at 92 78 0) (uuid "fp-d5v") (property "Reference" "D5V" (at 0 -2 0)) (property "Value" "GREEN" (at 0 2 0)))')
    footprints.append('  (footprint "Resistor_SMD:R_0603_1608Metric" (layer "F.Cu") (at 88 78 0) (uuid "fp-rled5v") (property "Reference" "RLED5V" (at 0 -1.5 0)) (property "Value" "1k" (at 0 1.5 0)))')
    footprints.append('  (footprint "LED_SMD:LED_0603_1608Metric" (layer "F.Cu") (at 100 78 0) (uuid "fp-d3v3") (property "Reference" "D3V3" (at 0 -2 0)) (property "Value" "BLUE" (at 0 2 0)))')
    footprints.append('  (footprint "Resistor_SMD:R_0603_1608Metric" (layer "F.Cu") (at 96 78 0) (uuid "fp-rled3v3") (property "Reference" "RLED3V3" (at 0 -1.5 0)) (property "Value" "1k" (at 0 1.5 0)))')
    
    # Board outline
    outline = '''  (gr_rect (start 20 20) (end 120 90)
    (stroke (width 0.1) (type default))
    (fill none)
    (layer "Edge.Cuts")
    (uuid "board-outline")
  )'''
    
    # Ground zone (copper pour on bottom layer)
    gnd_zone = '''  (zone (net 1) (net_name "GND") (layer "B.Cu") (uuid "gnd-zone")
    (hatch edge 0.5)
    (connect_pads (clearance 0.2))
    (min_thickness 0.25)
    (filled_areas_thickness no)
    (fill yes (thermal_gap 0.5) (thermal_bridge_width 0.5))
    (polygon
      (pts
        (xy 20 20) (xy 120 20) (xy 120 90) (xy 20 90)
      )
    )
  )'''
    
    # Mounting holes (4 corners)
    holes = '''  (footprint "MountingHole:MountingHole_3.2mm_M3" (layer "F.Cu") (at 23 23) (uuid "mh1") (property "Reference" "H1") (property "Value" "MountingHole"))
  (footprint "MountingHole:MountingHole_3.2mm_M3" (layer "F.Cu") (at 117 23) (uuid "mh2") (property "Reference" "H2") (property "Value" "MountingHole"))
  (footprint "MountingHole:MountingHole_3.2mm_M3" (layer "F.Cu") (at 23 87) (uuid "mh3") (property "Reference" "H3") (property "Value" "MountingHole"))
  (footprint "MountingHole:MountingHole_3.2mm_M3" (layer "F.Cu") (at 117 87) (uuid "mh4") (property "Reference" "H4") (property "Value" "MountingHole"))'''
    
    footer = ')'
    
    return '\n'.join([header, nets] + footprints + [outline, gnd_zone, holes, footer])

def main():
    pcb = gen_pcb()
    with open("red_pitaya_mux_board.kicad_pcb", "w") as f:
        f.write(pcb)
    print(f"✅ Generated optimized PCB layout: {len(pcb)} bytes")
    print("\n📐 Layout Improvements:")
    print("  • Organized sections: Left (Control), Top (Elements), Right (RX), Bottom (Power)")
    print("  • MOSFETs in vertical column with resistors grouped")
    print("  • Element SMAs evenly spaced across top edge")
    print("  • LNA amplifiers close to RX output SMAs")
    print("  • Power regulators at bottom with input protection")
    print("  • Ground pour on bottom layer")
    print("  • 4 mounting holes at corners")

if __name__ == "__main__":
    main()
