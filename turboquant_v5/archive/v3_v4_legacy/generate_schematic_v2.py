#!/usr/bin/env python3
"""
Generate TurboQuant Mux LNA Board Schematics - Version 2
Fixed hierarchical labels and references
"""

def gen_power_sch():
    """Generate POWER_SUPPLIES sheet with proper hierarchical labels"""
    return '''(kicad_sch
  (version 20231120)
  (generator "eeschema")
  (uuid "a1b2c3d4-e5f6-7890-abcd-ef1234567890")
  (paper "A4")
  (title_block
    (title "TurboQuant Mux LNA - Power Supplies")
    (date "2026-03-30")
    (rev "1.1")
  )
  (lib_symbols
    (symbol "power:GND" (power) (in_bom yes) (on_board yes)
      (property "Reference" "#PWR" (at 0 -3.81 0) (effects (font (size 1.27 1.27)) hide))
      (property "Value" "GND" (at 0 -1.27 0) (effects (font (size 1.27 1.27))))
    )
    (symbol "power:+12V" (power) (in_bom yes) (on_board yes)
      (property "Reference" "#PWR" (at 0 -2.54 0) (effects (font (size 1.27 1.27)) hide))
      (property "Value" "+12V" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
    )
    (symbol "power:+5V" (power) (in_bom yes) (on_board yes)
      (property "Reference" "#PWR" (at 0 -2.54 0) (effects (font (size 1.27 1.27)) hide))
      (property "Value" "+5V" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
    )
    (symbol "power:+3V3" (power) (in_bom yes) (on_board yes)
      (property "Reference" "#PWR" (at 0 -2.54 0) (effects (font (size 1.27 1.27)) hide))
      (property "Value" "+3V3" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
    )
    (symbol "Regulator_Linear:LM7805" (in_bom yes) (on_board yes)
      (property "Reference" "U" (at 0 5.08 0) (effects (font (size 1.27 1.27))))
      (property "Value" "LM7805" (at 0 -5.08 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_TO_SOT_SMD:SOT-223-3_TabPin2" (at 0 -7.62 0) (effects hide))
    )
    (symbol "Regulator_Linear:AMS1117-3.3" (in_bom yes) (on_board yes)
      (property "Reference" "U" (at 0 5.08 0) (effects (font (size 1.27 1.27))))
      (property "Value" "AMS1117-3.3" (at 0 -5.08 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_TO_SOT_SMD:SOT-223-3_TabPin2" (at 0 -7.62 0) (effects hide))
    )
    (symbol "Diode:1N4007" (in_bom yes) (on_board yes)
      (property "Reference" "D" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
      (property "Value" "1N4007" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Diode_SMD:D_SOD-123" (at 0 -5.08 0) (effects hide))
    )
    (symbol "Device:C" (in_bom yes) (on_board yes)
      (property "Reference" "C" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
      (property "Value" "C" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Capacitor_SMD:C_0603_1608Metric" (at 0 -5.08 0) (effects hide))
    )
    (symbol "Device:LED" (in_bom yes) (on_board yes)
      (property "Reference" "D" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
      (property "Value" "LED" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "LED_SMD:LED_0603_1608Metric" (at 0 -5.08 0) (effects hide))
    )
    (symbol "Device:R" (in_bom yes) (on_board yes)
      (property "Reference" "R" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
      (property "Value" "R" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Resistor_SMD:R_0603_1608Metric" (at 0 -5.08 0) (effects hide))
    )
    (symbol "Connector:Barrel_Jack" (in_bom yes) (on_board yes)
      (property "Reference" "J" (at 0 5.08 0) (effects (font (size 1.27 1.27))))
      (property "Value" "Barrel_Jack" (at 0 -5.08 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Connector_BarrelJack:BarrelJack_Horizontal" (at 0 -7.62 0) (effects hide))
    )
  )
  
  ; 12V Input Connector
  (symbol (lib_id "Connector:Barrel_Jack") (at 30 50 0) (uuid "pwr-j1")
    (property "Reference" "J1" (at 30 56.48 0) (effects (font (size 1.27 1.27))))
    (property "Value" "12V_IN" (at 30 43.52 0) (effects (font (size 1.27 1.27))))
  )
  
  ; Protection Diode D1
  (symbol (lib_id "Diode:1N4007") (at 50 50 0) (uuid "pwr-d1")
    (property "Reference" "D1" (at 50 53.16 0) (effects (font (size 1.27 1.27))))
    (property "Value" "1N4007" (at 50 46.84 0) (effects (font (size 1.27 1.27))))
  )
  
  ; Input Capacitor C1 (10uF)
  (symbol (lib_id "Device:C") (at 50 70 0) (uuid "pwr-c1")
    (property "Reference" "C1" (at 52.54 70 0) (effects (font (size 1.27 1.27))))
    (property "Value" "10uF" (at 47.46 70 0) (effects (font (size 1.27 1.27))))
  )
  
  ; LM7805 Regulator U1
  (symbol (lib_id "Regulator_Linear:LM7805") (at 90 50 0) (uuid "pwr-u1")
    (property "Reference" "U1" (at 90 56.48 0) (effects (font (size 1.27 1.27))))
    (property "Value" "LM7805" (at 90 43.52 0) (effects (font (size 1.27 1.27))))
  )
  
  ; 7805 Input Cap C2 (100nF)
  (symbol (lib_id "Device:C") (at 75 70 0) (uuid "pwr-c2")
    (property "Reference" "C2" (at 77.54 70 0) (effects (font (size 1.27 1.27))))
    (property "Value" "100nF" (at 72.46 70 0) (effects (font (size 1.27 1.27))))
  )
  
  ; 7805 Output Cap C3 (10uF)
  (symbol (lib_id "Device:C") (at 105 70 0) (uuid "pwr-c3")
    (property "Reference" "C3" (at 107.54 70 0) (effects (font (size 1.27 1.27))))
    (property "Value" "10uF" (at 102.46 70 0) (effects (font (size 1.27 1.27))))
  )
  
  ; AMS1117-3.3 Regulator U2
  (symbol (lib_id "Regulator_Linear:AMS1117-3.3") (at 145 50 0) (uuid "pwr-u2")
    (property "Reference" "U2" (at 145 56.48 0) (effects (font (size 1.27 1.27))))
    (property "Value" "AMS1117-3.3" (at 145 43.52 0) (effects (font (size 1.27 1.27))))
  )
  
  ; 1117 Input Cap C4 (100nF)
  (symbol (lib_id "Device:C") (at 130 70 0) (uuid "pwr-c4")
    (property "Reference" "C4" (at 132.54 70 0) (effects (font (size 1.27 1.27))))
    (property "Value" "100nF" (at 127.46 70 0) (effects (font (size 1.27 1.27))))
  )
  
  ; 1117 Output Cap C5 (10uF)
  (symbol (lib_id "Device:C") (at 160 70 0) (uuid "pwr-c5")
    (property "Reference" "C5" (at 162.54 70 0) (effects (font (size 1.27 1.27))))
    (property "Value" "10uF" (at 157.46 70 0) (effects (font (size 1.27 1.27))))
  )
  
  ; 5V LED D2 (Green)
  (symbol (lib_id "Device:LED") (at 120 95 0) (uuid "pwr-d2")
    (property "Reference" "D2" (at 120 98.16 0) (effects (font (size 1.27 1.27))))
    (property "Value" "GREEN" (at 120 91.84 0) (effects (font (size 1.27 1.27))))
  )
  
  ; 5V LED Resistor R1 (1k)
  (symbol (lib_id "Device:R") (at 105 95 0) (uuid "pwr-r1")
    (property "Reference" "R1" (at 102.46 95 0) (effects (font (size 1.27 1.27))))
    (property "Value" "1k" (at 107.54 95 0) (effects (font (size 1.27 1.27))))
  )
  
  ; 3.3V LED D3 (Blue)
  (symbol (lib_id "Device:LED") (at 175 95 0) (uuid "pwr-d3")
    (property "Reference" "D3" (at 175 98.16 0) (effects (font (size 1.27 1.27))))
    (property "Value" "BLUE" (at 175 91.84 0) (effects (font (size 1.27 1.27))))
  )
  
  ; 3.3V LED Resistor R2 (1k)
  (symbol (lib_id "Device:R") (at 160 95 0) (uuid "pwr-r2")
    (property "Reference" "R2" (at 157.46 95 0) (effects (font (size 1.27 1.27))))
    (property "Value" "1k" (at 162.54 95 0) (effects (font (size 1.27 1.27))))
  )
  
  ; Power Flags
  (symbol (lib_id "power:+12V") (at 30 30 0) (uuid "pwr-pf1")
    (property "Reference" "#PWR01" (at 30 27.46 0) (effects hide))
    (property "Value" "+12V" (at 30 32.54 0) (effects (font (size 1.27 1.27))))
  )
  
  (symbol (lib_id "power:GND") (at 30 90 0) (mirror y) (uuid "pwr-pf2")
    (property "Reference" "#PWR02" (at 30 92.54 0) (effects hide))
    (property "Value" "GND" (at 30 87.46 0) (effects (font (size 1.27 1.27))))
  )
  
  (symbol (lib_id "power:+5V") (at 105 30 0) (uuid "pwr-pf3")
    (property "Reference" "#PWR03" (at 105 27.46 0) (effects hide))
    (property "Value" "+5V" (at 105 32.54 0) (effects (font (size 1.27 1.27))))
  )
  
  (symbol (lib_id "power:+3V3") (at 160 30 0) (uuid "pwr-pf4")
    (property "Reference" "#PWR04" (at 160 27.46 0) (effects hide))
    (property "Value" "+3V3" (at 160 32.54 0) (effects (font (size 1.27 1.27))))
  )
  
  ; Hierarchical Labels (Sheet Outputs)
  (hierarchical_label "+12V" (shape output) (at 185 50 0) (effects (font (size 1.27 1.27))))
  (hierarchical_label "+5V" (shape output) (at 185 60 0) (effects (font (size 1.27 1.27))))
  (hierarchical_label "+3V3" (shape output) (at 185 70 0) (effects (font (size 1.27 1.27))))
  (hierarchical_label "GND" (shape bidirectional) (at 185 90 0) (effects (font (size 1.27 1.27))))
  
  ; Wires
  (wire (pts (xy 30 30) (xy 30 43.52)) (stroke (width 0) (type default)) (uuid "w1"))
  (wire (pts (xy 35.08 50) (xy 46.92 50)) (stroke (width 0) (type default)) (uuid "w2"))
  (wire (pts (xy 53.08 50) (xy 85.92 50)) (stroke (width 0) (type default)) (uuid "w3"))
  (wire (pts (xy 94.08 50) (xy 140.92 50)) (stroke (width 0) (type default)) (uuid "w4"))
  (wire (pts (xy 149.08 50) (xy 185 50)) (stroke (width 0) (type default)) (uuid "w5"))
  
  ; Ground connections
  (wire (pts (xy 30 90) (xy 30 56.48)) (stroke (width 0) (type default)) (uuid "w6"))
  (wire (pts (xy 90 44.44) (xy 90 40)) (stroke (width 0) (type default)) (uuid "w7"))
  (wire (pts (xy 145 44.44) (xy 145 40)) (stroke (width 0) (type default)) (uuid "w8"))
  (wire (pts (xy 90 40) (xy 145 40)) (stroke (width 0) (type default)) (uuid "w9"))
  (wire (pts (xy 145 40) (xy 185 40)) (stroke (width 0) (type default)) (uuid "w10"))
  (wire (pts (xy 185 40) (xy 185 90)) (stroke (width 0) (type default)) (uuid "w11"))
  
  ; Power distribution
  (wire (pts (xy 105 50) (xy 105 60)) (stroke (width 0) (type default)) (uuid "w12"))
  (wire (pts (xy 105 60) (xy 185 60)) (stroke (width 0) (type default)) (uuid "w13"))
  (wire (pts (xy 160 50) (xy 160 70)) (stroke (width 0) (type default)) (uuid "w14"))
  (wire (pts (xy 160 70) (xy 185 70)) (stroke (width 0) (type default)) (uuid "w15"))
  
  ; LED connections
  (wire (pts (xy 105 60) (xy 105 95)) (stroke (width 0) (type default)) (uuid "w16"))
  (wire (pts (xy 100.46 95) (xy 109.54 95)) (stroke (width 0) (type default)) (uuid "w17"))
  (wire (pts (xy 120 91.84) (xy 120 40)) (stroke (width 0) (type default)) (uuid "w18"))
  
  (wire (pts (xy 160 70) (xy 160 95)) (stroke (width 0) (type default)) (uuid "w19"))
  (wire (pts (xy 155.46 95) (xy 164.54 95)) (stroke (width 0) (type default)) (uuid "w20"))
  (wire (pts (xy 175 91.84) (xy 175 40)) (stroke (width 0) (type default)) (uuid "w21"))
  
  ; Junctions
  (junction (at 90 40) (diameter 0) (uuid "j1"))
  (junction (at 105 60) (diameter 0) (uuid "j2"))
  (junction (at 145 40) (diameter 0) (uuid "j3"))
  (junction (at 160 70) (diameter 0) (uuid "j4"))
  
  (sheet_instances (path "/" (page "1")))
)'''
    return sch

def gen_digital_sch():
    """Generate DIGITAL_CONTROL sheet with proper labels"""
    return '''(kicad_sch
  (version 20231120)
  (generator "eeschema")
  (uuid "b2c3d4e5-f6a7-8901-bcde-f23456789012")
  (paper "A4")
  (title_block
    (title "TurboQuant Mux LNA - Digital Control")
    (date "2026-03-30")
    (rev "1.1")
  )
  (lib_symbols
    (symbol "power:GND" (power) (in_bom yes) (on_board yes)
      (property "Reference" "#PWR" (at 0 -3.81 0) (effects (font (size 1.27 1.27)) hide))
      (property "Value" "GND" (at 0 -1.27 0) (effects (font (size 1.27 1.27))))
    )
    (symbol "power:+5V" (power) (in_bom yes) (on_board yes)
      (property "Reference" "#PWR" (at 0 -2.54 0) (effects (font (size 1.27 1.27)) hide))
      (property "Value" "+5V" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
    )
    (symbol "74xx:74HC595" (in_bom yes) (on_board yes)
      (property "Reference" "U" (at -7.62 13.97 0) (effects (font (size 1.27 1.27))))
      (property "Value" "74HC595" (at 0 0 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm" (at 0 -15.24 0) (effects hide))
    )
    (symbol "Connector:Conn_02x10" (in_bom yes) (on_board yes)
      (property "Reference" "J" (at 0 13.97 0) (effects (font (size 1.27 1.27))))
      (property "Value" "Conn_02x10" (at 0 -13.97 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical" (at 0 -16.51 0) (effects hide))
    )
    (symbol "Device:R" (in_bom yes) (on_board yes)
      (property "Reference" "R" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
      (property "Value" "R" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Resistor_SMD:R_0603_1608Metric" (at 0 -5.08 0) (effects hide))
    )
  )
  
  ; GPIO Header J2
  (symbol (lib_id "Connector:Conn_02x10") (at 35 60 0) (uuid "dig-j2")
    (property "Reference" "J2" (at 35 75.97 0) (effects (font (size 1.27 1.27))))
    (property "Value" "GPIO_HEADER" (at 35 44.03 0) (effects (font (size 1.27 1.27))))
  )
  
  ; 74HC595 Shift Register U3
  (symbol (lib_id "74xx:74HC595") (at 90 60 0) (uuid "dig-u3")
    (property "Reference" "U3" (at 82.38 74.77 0) (effects (font (size 1.27 1.27))))
    (property "Value" "74HC595" (at 90 60 0) (effects (font (size 1.27 1.27))))
  )
  
  ; Gate Resistors R11-R18 (1k each)
  (symbol (lib_id "Device:R") (at 130 35 90) (uuid "dig-r11")
    (property "Reference" "R11" (at 132.54 35 90) (effects (font (size 1.27 1.27))))
    (property "Value" "1k" (at 127.46 35 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 135 35 90) (uuid "dig-r12")
    (property "Reference" "R12" (at 137.54 35 90) (effects (font (size 1.27 1.27))))
    (property "Value" "1k" (at 132.46 35 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 140 35 90) (uuid "dig-r13")
    (property "Reference" "R13" (at 142.54 35 90) (effects (font (size 1.27 1.27))))
    (property "Value" "1k" (at 137.46 35 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 145 35 90) (uuid "dig-r14")
    (property "Reference" "R14" (at 147.54 35 90) (effects (font (size 1.27 1.27))))
    (property "Value" "1k" (at 142.46 35 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 150 35 90) (uuid "dig-r15")
    (property "Reference" "R15" (at 152.54 35 90) (effects (font (size 1.27 1.27))))
    (property "Value" "1k" (at 147.46 35 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 155 35 90) (uuid "dig-r16")
    (property "Reference" "R16" (at 157.54 35 90) (effects (font (size 1.27 1.27))))
    (property "Value" "1k" (at 152.46 35 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 160 35 90) (uuid "dig-r17")
    (property "Reference" "R17" (at 162.54 35 90) (effects (font (size 1.27 1.27))))
    (property "Value" "1k" (at 157.46 35 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 165 35 90) (uuid "dig-r18")
    (property "Reference" "R18" (at 167.54 35 90) (effects (font (size 1.27 1.27))))
    (property "Value" "1k" (at 162.46 35 90) (effects (font (size 1.27 1.27))))
  )
  
  ; Power Flags
  (symbol (lib_id "power:+5V") (at 75 30 0) (uuid "dig-pf5")
    (property "Reference" "#PWR05" (at 75 27.46 0) (effects hide))
    (property "Value" "+5V" (at 75 32.54 0) (effects (font (size 1.27 1.27))))
  )
  
  (symbol (lib_id "power:GND") (at 75 95 0) (mirror y) (uuid "dig-pf6")
    (property "Reference" "#PWR06" (at 75 97.54 0) (effects hide))
    (property "Value" "GND" (at 75 92.46 0) (effects (font (size 1.27 1.27))))
  )
  
  ; Hierarchical Labels - Inputs from parent sheet
  (hierarchical_label "+5V" (shape input) (at 20 30 180) (effects (font (size 1.27 1.27))))
  (hierarchical_label "GND" (shape input) (at 20 95 180) (effects (font (size 1.27 1.27))))
  
  ; Hierarchical Labels - Outputs to parent sheet
  (hierarchical_label "GATE0" (shape output) (at 180 40 0) (effects (font (size 1.27 1.27))))
  (hierarchical_label "GATE1" (shape output) (at 180 45 0) (effects (font (size 1.27 1.27))))
  (hierarchical_label "GATE2" (shape output) (at 180 50 0) (effects (font (size 1.27 1.27))))
  (hierarchical_label "GATE3" (shape output) (at 180 55 0) (effects (font (size 1.27 1.27))))
  (hierarchical_label "GATE4" (shape output) (at 180 60 0) (effects (font (size 1.27 1.27))))
  (hierarchical_label "GATE5" (shape output) (at 180 65 0) (effects (font (size 1.27 1.27))))
  (hierarchical_label "GATE6" (shape output) (at 180 70 0) (effects (font (size 1.27 1.27))))
  (hierarchical_label "GATE7" (shape output) (at 180 75 0) (effects (font (size 1.27 1.27))))
  
  ; Global Labels - Control signals from GPIO
  (global_label "SER" (shape input) (at 20 45 180) (effects (font (size 1.27 1.27))))
  (global_label "SRCLK" (shape input) (at 20 50 180) (effects (font (size 1.27 1.27))))
  (global_label "RCLK" (shape input) (at 20 55 180) (effects (font (size 1.27 1.27))))
  (global_label "MUX_A" (shape input) (at 20 60 180) (effects (font (size 1.27 1.27))))
  (global_label "MUX_B" (shape input) (at 20 65 180) (effects (font (size 1.27 1.27))))
  (global_label "MUX_C" (shape input) (at 20 70 180) (effects (font (size 1.27 1.27))))
  
  ; Wires
  (wire (pts (xy 20 30) (xy 20 32.54)) (stroke (width 0) (type default)) (uuid "wd1"))
  (wire (pts (xy 20 32.54) (xy 75 32.54)) (stroke (width 0) (type default)) (uuid "wd2"))
  (wire (pts (xy 75 32.54) (xy 75 45.46)) (stroke (width 0) (type default)) (uuid "wd3"))
  
  (wire (pts (xy 20 95) (xy 20 74.54)) (stroke (width 0) (type default)) (uuid "wd4"))
  (wire (pts (xy 20 74.54) (xy 75 74.54)) (stroke (width 0) (type default)) (uuid "wd5"))
  
  ; Gate output wires
  (wire (pts (xy 97.62 66.11) (xy 130 66.11)) (stroke (width 0) (type default)) (uuid "wg0"))
  (wire (pts (xy 130 66.11) (xy 130 36.27)) (stroke (width 0) (type default)) (uuid "wg1"))
  (wire (pts (xy 130 36.27) (xy 132.54 36.27)) (stroke (width 0) (type default)) (uuid "wg2"))
  (wire (pts (xy 132.54 33.73) (xy 132.54 30)) (stroke (width 0) (type default)) (uuid "wg3"))
  (wire (pts (xy 132.54 30) (xy 180 30)) (stroke (width 0) (type default)) (uuid "wg4"))
  (wire (pts (xy 180 30) (xy 180 40)) (stroke (width 0) (type default)) (uuid "wg5"))
  
  (junction (at 75 32.54) (diameter 0) (uuid "jd1"))
  
  (sheet_instances (path "/" (page "1")))
)'''
    return sch

def main():
    # Generate updated power sheet
    with open("power.kicad_sch", "w") as f:
        f.write(gen_power_sch())
    print("Generated: power.kicad_sch (v1.1)")
    
    # Generate updated digital sheet
    with open("digital.kicad_sch", "w") as f:
        f.write(gen_digital_sch())
    print("Generated: digital.kicad_sch (v1.1)")
    
    print("\n✅ Updated sheets with proper hierarchical labels!")
    print("\nChanges:")
    print("  • Power sheet: Added hierarchical labels for +12V, +5V, +3V3, GND outputs")
    print("  • Digital sheet: Added hierarchical labels for power inputs and GATE outputs")
    print("  • All labels use proper shape types (input/output/bidirectional)")

if __name__ == "__main__":
    main()

def gen_analog_sch():
    """Generate ANALOG_FRONTEND sheet with proper hierarchical labels"""
    return '''(kicad_sch
  (version 20231120)
  (generator "eeschema")
  (uuid "c3d4e5f6-a7b8-9012-cdef-345678901234")
  (paper "A3")
  (title_block
    (title "TurboQuant Mux LNA - Analog Frontend")
    (date "2026-03-30")
    (rev "1.1")
  )
  (lib_symbols
    (symbol "power:GND" (power) (in_bom yes) (on_board yes)
      (property "Reference" "#PWR" (at 0 -3.81 0) (effects (font (size 1.27 1.27)) hide))
      (property "Value" "GND" (at 0 -1.27 0) (effects (font (size 1.27 1.27))))
    )
    (symbol "power:+5V" (power) (in_bom yes) (on_board yes)
      (property "Reference" "#PWR" (at 0 -2.54 0) (effects (font (size 1.27 1.27)) hide))
      (property "Value" "+5V" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
    )
    (symbol "Analog_Switch:CD4051B" (in_bom yes) (on_board yes)
      (property "Reference" "U" (at 0 -12.7 0) (effects (font (size 1.27 1.27))))
      (property "Value" "CD4051B" (at 0 0 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm" (at 0 -15.24 0) (effects hide))
    )
    (symbol "Amplifier_Operational:OPA657" (in_bom yes) (on_board yes)
      (property "Reference" "U" (at 0 -7.62 0) (effects (font (size 1.27 1.27))))
      (property "Value" "OPA657" (at 0 0 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm" (at 0 -10.16 0) (effects hide))
    )
    (symbol "Transistor_FET:BSS138" (in_bom yes) (on_board yes)
      (property "Reference" "Q" (at 2.54 1.27 0) (effects (font (size 1.27 1.27)) (justify left)))
      (property "Value" "BSS138" (at 2.54 -1.27 0) (effects (font (size 1.27 1.27)) (justify left)))
      (property "Footprint" "Package_TO_SOT_SMD:SOT-23" (at 0 -5.08 0) (effects hide))
    )
    (symbol "Diode:BAV99" (in_bom yes) (on_board yes)
      (property "Reference" "D" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
      (property "Value" "BAV99" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_TO_SOT_SMD:SOT-23" (at 0 -5.08 0) (effects hide))
    )
    (symbol "Connector:Conn_Coaxial" (in_bom yes) (on_board yes)
      (property "Reference" "J" (at 0 3.81 0) (effects (font (size 1.27 1.27))))
      (property "Value" "SMA" (at 0 -3.81 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Connector_Coaxial:SMA_Amphenol_132134-11_Vertical" (at 0 -6.35 0) (effects hide))
    )
    (symbol "Device:R" (in_bom yes) (on_board yes)
      (property "Reference" "R" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
      (property "Value" "R" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Resistor_SMD:R_0603_1608Metric" (at 0 -5.08 0) (effects hide))
    )
    (symbol "Device:C" (in_bom yes) (on_board yes)
      (property "Reference" "C" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
      (property "Value" "C" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Capacitor_SMD:C_0603_1608Metric" (at 0 -5.08 0) (effects hide))
    )
  )
  
  ; TX Input SMA J3
  (symbol (lib_id "Connector:Conn_Coaxial") (at 35 40 0) (uuid "ana-j3")
    (property "Reference" "J3" (at 35 44.89 0) (effects (font (size 1.27 1.27))))
    (property "Value" "TX_IN" (at 35 35.11 0) (effects (font (size 1.27 1.27))))
  )
  
  ; MOSFET Switches Q1-Q8
  (symbol (lib_id "Transistor_FET:BSS138") (at 65 40 0) (uuid "ana-q1")
    (property "Reference" "Q1" (at 67.54 41.27 0) (effects (font (size 1.27 1.27)) (justify left)))
    (property "Value" "BSS138" (at 67.54 38.73 0) (effects (font (size 1.27 1.27)) (justify left)))
  )
  (symbol (lib_id "Transistor_FET:BSS138") (at 65 55 0) (uuid "ana-q2")
    (property "Reference" "Q2" (at 67.54 56.27 0) (effects (font (size 1.27 1.27)) (justify left)))
    (property "Value" "BSS138" (at 67.54 53.73 0) (effects (font (size 1.27 1.27)) (justify left)))
  )
  (symbol (lib_id "Transistor_FET:BSS138") (at 65 70 0) (uuid "ana-q3")
    (property "Reference" "Q3" (at 67.54 71.27 0) (effects (font (size 1.27 1.27)) (justify left)))
    (property "Value" "BSS138" (at 67.54 68.73 0) (effects (font (size 1.27 1.27)) (justify left)))
  )
  (symbol (lib_id "Transistor_FET:BSS138") (at 65 85 0) (uuid "ana-q4")
    (property "Reference" "Q4" (at 67.54 86.27 0) (effects (font (size 1.27 1.27)) (justify left)))
    (property "Value" "BSS138" (at 67.54 83.73 0) (effects (font (size 1.27 1.27)) (justify left)))
  )
  (symbol (lib_id "Transistor_FET:BSS138") (at 65 100 0) (uuid "ana-q5")
    (property "Reference" "Q5" (at 67.54 101.27 0) (effects (font (size 1.27 1.27)) (justify left)))
    (property "Value" "BSS138" (at 67.54 98.73 0) (effects (font (size 1.27 1.27)) (justify left)))
  )
  (symbol (lib_id "Transistor_FET:BSS138") (at 65 115 0) (uuid "ana-q6")
    (property "Reference" "Q6" (at 67.54 116.27 0) (effects (font (size 1.27 1.27)) (justify left)))
    (property "Value" "BSS138" (at 67.54 113.73 0) (effects (font (size 1.27 1.27)) (justify left)))
  )
  (symbol (lib_id "Transistor_FET:BSS138") (at 65 130 0) (uuid "ana-q7")
    (property "Reference" "Q7" (at 67.54 131.27 0) (effects (font (size 1.27 1.27)) (justify left)))
    (property "Value" "BSS138" (at 67.54 128.73 0) (effects (font (size 1.27 1.27)) (justify left)))
  )
  (symbol (lib_id "Transistor_FET:BSS138") (at 65 145 0) (uuid "ana-q8")
    (property "Reference" "Q8" (at 67.54 146.27 0) (effects (font (size 1.27 1.27)) (justify left)))
    (property "Value" "BSS138" (at 67.54 143.73 0) (effects (font (size 1.27 1.27)) (justify left)))
  )
  
  ; Series Resistors RS1-RS8
  (symbol (lib_id "Device:R") (at 80 40 90) (uuid "ana-rs1")
    (property "Reference" "RS1" (at 82.54 40 90) (effects (font (size 1.27 1.27))))
    (property "Value" "100" (at 77.46 40 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 80 55 90) (uuid "ana-rs2")
    (property "Reference" "RS2" (at 82.54 55 90) (effects (font (size 1.27 1.27))))
    (property "Value" "100" (at 77.46 55 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 80 70 90) (uuid "ana-rs3")
    (property "Reference" "RS3" (at 82.54 70 90) (effects (font (size 1.27 1.27))))
    (property "Value" "100" (at 77.46 70 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 80 85 90) (uuid "ana-rs4")
    (property "Reference" "RS4" (at 82.54 85 90) (effects (font (size 1.27 1.27))))
    (property "Value" "100" (at 77.46 85 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 80 100 90) (uuid "ana-rs5")
    (property "Reference" "RS5" (at 82.54 100 90) (effects (font (size 1.27 1.27))))
    (property "Value" "100" (at 77.46 100 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 80 115 90) (uuid "ana-rs6")
    (property "Reference" "RS6" (at 82.54 115 90) (effects (font (size 1.27 1.27))))
    (property "Value" "100" (at 77.46 115 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 80 130 90) (uuid "ana-rs7")
    (property "Reference" "RS7" (at 82.54 130 90) (effects (font (size 1.27 1.27))))
    (property "Value" "100" (at 77.46 130 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 80 145 90) (uuid "ana-rs8")
    (property "Reference" "RS8" (at 82.54 145 90) (effects (font (size 1.27 1.27))))
    (property "Value" "100" (at 77.46 145 90) (effects (font (size 1.27 1.27))))
  )
  
  ; Element Connectors J4-J11
  (symbol (lib_id "Connector:Conn_Coaxial") (at 100 40 0) (uuid "ana-j4")
    (property "Reference" "J4" (at 100 44.89 0) (effects (font (size 1.27 1.27))))
    (property "Value" "EL0" (at 100 35.11 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Connector:Conn_Coaxial") (at 100 55 0) (uuid "ana-j5")
    (property "Reference" "J5" (at 100 59.89 0) (effects (font (size 1.27 1.27))))
    (property "Value" "EL1" (at 100 50.11 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Connector:Conn_Coaxial") (at 100 70 0) (uuid "ana-j6")
    (property "Reference" "J6" (at 100 74.89 0) (effects (font (size 1.27 1.27))))
    (property "Value" "EL2" (at 100 65.11 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Connector:Conn_Coaxial") (at 100 85 0) (uuid "ana-j7")
    (property "Reference" "J7" (at 100 89.89 0) (effects (font (size 1.27 1.27))))
    (property "Value" "EL3" (at 100 80.11 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Connector:Conn_Coaxial") (at 100 100 0) (uuid "ana-j8")
    (property "Reference" "J8" (at 100 104.89 0) (effects (font (size 1.27 1.27))))
    (property "Value" "EL4" (at 100 95.11 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Connector:Conn_Coaxial") (at 100 115 0) (uuid "ana-j9")
    (property "Reference" "J9" (at 100 119.89 0) (effects (font (size 1.27 1.27))))
    (property "Value" "EL5" (at 100 110.11 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Connector:Conn_Coaxial") (at 100 130 0) (uuid "ana-j10")
    (property "Reference" "J10" (at 100 134.89 0) (effects (font (size 1.27 1.27))))
    (property "Value" "EL6" (at 100 125.11 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Connector:Conn_Coaxial") (at 100 145 0) (uuid "ana-j11")
    (property "Reference" "J11" (at 100 149.89 0) (effects (font (size 1.27 1.27))))
    (property "Value" "EL7" (at 100 140.11 0) (effects (font (size 1.27 1.27))))
  )
  
  ; Protection Diodes D4-D11
  (symbol (lib_id "Diode:BAV99") (at 120 40 0) (uuid "ana-d4")
    (property "Reference" "D4" (at 120 43.16 0) (effects (font (size 1.27 1.27))))
    (property "Value" "BAV99" (at 120 36.84 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Diode:BAV99") (at 120 55 0) (uuid "ana-d5")
    (property "Reference" "D5" (at 120 58.16 0) (effects (font (size 1.27 1.27))))
    (property "Value" "BAV99" (at 120 51.84 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Diode:BAV99") (at 120 70 0) (uuid "ana-d6")
    (property "Reference" "D6" (at 120 73.16 0) (effects (font (size 1.27 1.27))))
    (property "Value" "BAV99" (at 120 66.84 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Diode:BAV99") (at 120 85 0) (uuid "ana-d7")
    (property "Reference" "D7" (at 120 88.16 0) (effects (font (size 1.27 1.27))))
    (property "Value" "BAV99" (at 120 81.84 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Diode:BAV99") (at 120 100 0) (uuid "ana-d8")
    (property "Reference" "D8" (at 120 103.16 0) (effects (font (size 1.27 1.27))))
    (property "Value" "BAV99" (at 120 96.84 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Diode:BAV99") (at 120 115 0) (uuid "ana-d9")
    (property "Reference" "D9" (at 120 118.16 0) (effects (font (size 1.27 1.27))))
    (property "Value" "BAV99" (at 120 111.84 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Diode:BAV99") (at 120 130 0) (uuid "ana-d10")
    (property "Reference" "D10" (at 120 133.16 0) (effects (font (size 1.27 1.27))))
    (property "Value" "BAV99" (at 120 126.84 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Diode:BAV99") (at 120 145 0) (uuid "ana-d11")
    (property "Reference" "D11" (at 120 148.16 0) (effects (font (size 1.27 1.27))))
    (property "Value" "BAV99" (at 120 141.84 0) (effects (font (size 1.27 1.27))))
  )
  
  ; CD4051B Multiplexers U4-U5
  (symbol (lib_id "Analog_Switch:CD4051B") (at 160 70 0) (uuid "ana-u4")
    (property "Reference" "U4" (at 152.38 84.77 0) (effects (font (size 1.27 1.27))))
    (property "Value" "CD4051B" (at 160 70 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Analog_Switch:CD4051B") (at 160 115 0) (uuid "ana-u5")
    (property "Reference" "U5" (at 152.38 129.77 0) (effects (font (size 1.27 1.27))))
    (property "Value" "CD4051B" (at 160 115 0) (effects (font (size 1.27 1.27))))
  )
  
  ; OPA657 LNAs U6-U7
  (symbol (lib_id "Amplifier_Operational:OPA657") (at 200 70 0) (uuid "ana-u6")
    (property "Reference" "U6" (at 192.38 78.62 0) (effects (font (size 1.27 1.27))))
    (property "Value" "OPA657" (at 200 70 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Amplifier_Operational:OPA657") (at 200 115 0) (uuid "ana-u7")
    (property "Reference" "U7" (at 192.38 123.62 0) (effects (font (size 1.27 1.27))))
    (property "Value" "OPA657" (at 200 115 0) (effects (font (size 1.27 1.27))))
  )
  
  ; RX Output SMAs J12-J13
  (symbol (lib_id "Connector:Conn_Coaxial") (at 230 70 0) (uuid "ana-j12")
    (property "Reference" "J12" (at 230 74.89 0) (effects (font (size 1.27 1.27))))
    (property "Value" "RX0_OUT" (at 230 65.11 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Connector:Conn_Coaxial") (at 230 115 0) (uuid "ana-j13")
    (property "Reference" "J13" (at 230 119.89 0) (effects (font (size 1.27 1.27))))
    (property "Value" "RX1_OUT" (at 230 110.11 0) (effects (font (size 1.27 1.27))))
  )
  
  ; Hierarchical Labels - Power Inputs
  (hierarchical_label "+5V" (shape input) (at 20 30 180) (effects (font (size 1.27 1.27))))
  (hierarchical_label "GND" (shape input) (at 20 160 180) (effects (font (size 1.27 1.27))))
  
  ; Hierarchical Labels - Gate Inputs from Digital
  (hierarchical_label "GATE0" (shape input) (at 20 42 180) (effects (font (size 1.27 1.27))))
  (hierarchical_label "GATE1" (shape input) (at 20 57 180) (effects (font (size 1.27 1.27))))
  (hierarchical_label "GATE2" (shape input) (at 20 72 180) (effects (font (size 1.27 1.27))))
  (hierarchical_label "GATE3" (shape input) (at 20 87 180) (effects (font (size 1.27 1.27))))
  (hierarchical_label "GATE4" (shape input) (at 20 102 180) (effects (font (size 1.27 1.27))))
  (hierarchical_label "GATE5" (shape input) (at 20 117 180) (effects (font (size 1.27 1.27))))
  (hierarchical_label "GATE6" (shape input) (at 20 132 180) (effects (font (size 1.27 1.27))))
  (hierarchical_label "GATE7" (shape input) (at 20 147 180) (effects (font (size 1.27 1.27))))
  
  ; Hierarchical Labels - Mux Control from GPIO
  (hierarchical_label "MUX_A" (shape input) (at 140 55 180) (effects (font (size 1.27 1.27))))
  (hierarchical_label "MUX_B" (shape input) (at 140 60 180) (effects (font (size 1.27 1.27))))
  (hierarchical_label "MUX_C" (shape input) (at 140 65 180) (effects (font (size 1.27 1.27))))
  
  ; Power Flags
  (symbol (lib_id "power:+5V") (at 170 30 0) (uuid "ana-pf7")
    (property "Reference" "#PWR07" (at 170 27.46 0) (effects hide))
    (property "Value" "+5V" (at 170 32.54 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "power:GND") (at 170 160 0) (mirror y) (uuid "ana-pf8")
    (property "Reference" "#PWR08" (at 170 162.54 0) (effects hide))
    (property "Value" "GND" (at 170 157.46 0) (effects (font (size 1.27 1.27))))
  )
  
  (sheet_instances (path "/" (page "1")))
)'''
    return sch

def gen_main_sch():
    """Generate main schematic with proper hierarchical connections"""
    return '''(kicad_sch
  (version 20231120)
  (generator "eeschema")
  (uuid "c91386be-ef17-4bcb-aaad-5175b258204a")
  (paper "A3")
  (title_block
    (title "TurboQuant Mux LNA Board")
    (date "2026-03-30")
    (rev "1.1")
    (company "TurboQuant")
    (comment 1 "8-Element Ultrasound Array Interface")
    (comment 2 "Hierarchical Design with proper label connections")
  )
  (lib_symbols)
  
  ; Power Supplies Sheet with hierarchical pins
  (sheet (at 13.97 16.51) (size 80.01 71.12) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (stroke (width 0.1524) (type solid))
    (fill (color 0 0 0 0.0000))
    (uuid "31e7358f-421c-4108-98a5-1bd5cbdf3861")
    (property "Sheetname" "POWER_SUPPLIES" (at 13.97 15.7984 0) (effects (font (size 1.27 1.27)) (justify left bottom)))
    (property "Sheetfile" "power.kicad_sch" (at 13.97 88.2146 0) (effects (font (size 1.27 1.27)) (justify left top)))
    ; Hierarchical pins
    (pin "+12V" output (at 93.98 30 0) (uuid "pwr-pin-12v") (effects (font (size 1.27 1.27))))
    (pin "+5V" output (at 93.98 40 0) (uuid "pwr-pin-5v") (effects (font (size 1.27 1.27))))
    (pin "+3V3" output (at 93.98 50 0) (uuid "pwr-pin-3v3") (effects (font (size 1.27 1.27))))
    (pin "GND" bidirectional (at 93.98 60 0) (uuid "pwr-pin-gnd") (effects (font (size 1.27 1.27))))
    (instances (project "tuboquant_mux_lna" (path "/c91386be-ef17-4bcb-aaad-5175b258204a" (page "2"))))
  )
  
  ; Digital Control Sheet with hierarchical pins
  (sheet (at 105.41 16.51) (size 100 80) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (stroke (width 0.1524) (type solid))
    (fill (color 0 0 0 0.0000))
    (uuid "bf41dd9b-ce45-467e-ac10-028c71ad2a9a")
    (property "Sheetname" "DIGITAL_CONTROL" (at 105.41 15.7984 0) (effects (font (size 1.27 1.27)) (justify left bottom)))
    (property "Sheetfile" "digital.kicad_sch" (at 105.41 97.7146 0) (effects (font (size 1.27 1.27)) (justify left top)))
    ; Power inputs
    (pin "+5V" input (at 105.41 30 180) (uuid "dig-pin-5v") (effects (font (size 1.27 1.27))))
    (pin "GND" input (at 105.41 40 180) (uuid "dig-pin-gnd") (effects (font (size 1.27 1.27))))
    ; Gate outputs
    (pin "GATE0" output (at 205.41 25 0) (uuid "dig-pin-g0") (effects (font (size 1.27 1.27))))
    (pin "GATE1" output (at 205.41 30 0) (uuid "dig-pin-g1") (effects (font (size 1.27 1.27))))
    (pin "GATE2" output (at 205.41 35 0) (uuid "dig-pin-g2") (effects (font (size 1.27 1.27))))
    (pin "GATE3" output (at 205.41 40 0) (uuid "dig-pin-g3") (effects (font (size 1.27 1.27))))
    (pin "GATE4" output (at 205.41 45 0) (uuid "dig-pin-g4") (effects (font (size 1.27 1.27))))
    (pin "GATE5" output (at 205.41 50 0) (uuid "dig-pin-g5") (effects (font (size 1.27 1.27))))
    (pin "GATE6" output (at 205.41 55 0) (uuid "dig-pin-g6") (effects (font (size 1.27 1.27))))
    (pin "GATE7" output (at 205.41 60 0) (uuid "dig-pin-g7") (effects (font (size 1.27 1.27))))
    (instances (project "tuboquant_mux_lna" (path "/c91386be-ef17-4bcb-aaad-5175b258204a" (page "3"))))
  )
  
  ; Analog Frontend Sheet with hierarchical pins
  (sheet (at 13.97 102.87) (size 191.44 85.88) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (stroke (width 0.1524) (type solid))
    (fill (color 0 0 0 0.0000))
    (uuid "da55019f-ccad-455b-840f-c04df8128d6c")
    (property "Sheetname" "ANALOG_FRONTEND" (at 13.97 102.1584 0) (effects (font (size 1.27 1.27)) (justify left bottom)))
    (property "Sheetfile" "analog.kicad_sch" (at 13.97 189.3346 0) (effects (font (size 1.27 1.27)) (justify left top)))
    ; Power inputs
    (pin "+5V" input (at 13.97 115 180) (uuid "ana-pin-5v") (effects (font (size 1.27 1.27))))
    (pin "GND" input (at 13.97 130 180) (uuid "ana-pin-gnd") (effects (font (size 1.27 1.27))))
    ; Gate inputs
    (pin "GATE0" input (at 13.97 140 180) (uuid "ana-pin-g0") (effects (font (size 1.27 1.27))))
    (pin "GATE1" input (at 13.97 145 180) (uuid "ana-pin-g1") (effects (font (size 1.27 1.27))))
    (pin "GATE2" input (at 13.97 150 180) (uuid "ana-pin-g2") (effects (font (size 1.27 1.277))))
    (pin "GATE3" input (at 13.97 155 180) (uuid "ana-pin-g3") (effects (font (size 1.27 1.27))))
    (pin "GATE4" input (at 13.97 160 180) (uuid "ana-pin-g4") (effects (font (size 1.27 1.27))))
    (pin "GATE5" input (at 13.97 165 180) (uuid "ana-pin-g5") (effects (font (size 1.27 1.27))))
    (pin "GATE6" input (at 13.97 170 180) (uuid "ana-pin-g6") (effects (font (size 1.27 1.27))))
    (pin "GATE7" input (at 13.97 175 180) (uuid "ana-pin-g7") (effects (font (size 1.27 1.27))))
    ; Mux control inputs
    (pin "MUX_A" input (at 205.41 115 0) (uuid "ana-pin-muxa") (effects (font (size 1.27 1.27))))
    (pin "MUX_B" input (at 205.41 120 0) (uuid "ana-pin-muxb") (effects (font (size 1.27 1.27))))
    (pin "MUX_C" input (at 205.41 125 0) (uuid "ana-pin-muxc") (effects (font (size 1.27 1.27))))
    (instances (project "tuboquant_mux_lna" (path "/c91386be-ef17-4bcb-aaad-5175b258204a" (page "4"))))
  )
  
  ; Wire connections between sheets
  ; Power: +5V from Power to Digital
  (wire (pts (xy 93.98 40) (xy 100 40)) (stroke (width 0) (type default)) (uuid "wm1"))
  (wire (pts (xy 100 40) (xy 100 30)) (stroke (width 0) (type default)) (uuid "wm2"))
  (wire (pts (xy 100 30) (xy 105.41 30)) (stroke (width 0) (type default)) (uuid "wm3"))
  
  ; Power: GND from Power to Digital
  (wire (pts (xy 93.98 60) (xy 100 60)) (stroke (width 0) (type default)) (uuid "wm4"))
  (wire (pts (xy 100 60) (xy 100 40)) (stroke (width 0) (type default)) (uuid "wm5"))
  (wire (pts (xy 100 40) (xy 105.41 40)) (stroke (width 0) (type default)) (uuid "wm6"))
  
  ; Power: +5V from Power to Analog
  (wire (pts (xy 93.98 40) (xy 95 40)) (stroke (width 0) (type default)) (uuid "wm7"))
  (wire (pts (xy 95 40) (xy 95 115)) (stroke (width 0) (type default)) (uuid "wm8"))
  (wire (pts (xy 95 115) (xy 13.97 115)) (stroke (width 0) (type default)) (uuid "wm9"))
  
  ; Power: GND from Power to Analog
  (wire (pts (xy 93.98 60) (xy 90 60)) (stroke (width 0) (type default)) (uuid "wm10"))
  (wire (pts (xy 90 60) (xy 90 130)) (stroke (width 0) (type default)) (uuid "wm11"))
  (wire (pts (xy 90 130) (xy 13.97 130)) (stroke (width 0) (type default)) (uuid "wm12"))
  
  ; Gates from Digital to Analog
  (wire (pts (xy 205.41 25) (xy 210 25)) (stroke (width 0) (type default)) (uuid "wg0"))
  (wire (pts (xy 210 25) (xy 210 140)) (stroke (width 0) (type default)) (uuid "wg0b"))
  (wire (pts (xy 210 140) (xy 13.97 140)) (stroke (width 0) (type default)) (uuid "wg0c"))
  
  (wire (pts (xy 205.41 30) (xy 212 30)) (stroke (width 0) (type default)) (uuid "wg1"))
  (wire (pts (xy 212 30) (xy 212 145)) (stroke (width 0) (type default)) (uuid "wg1b"))
  (wire (pts (xy 212 145) (xy 13.97 145)) (stroke (width 0) (type default)) (uuid "wg1c"))
  
  (wire (pts (xy 205.41 35) (xy 214 35)) (stroke (width 0) (type default)) (uuid "wg2"))
  (wire (pts (xy 214 35) (xy 214 150)) (stroke (width 0) (type default)) (uuid "wg2b"))
  (wire (pts (xy 214 150) (xy 13.97 150)) (stroke (width 0) (type default)) (uuid "wg2c"))
  
  (wire (pts (xy 205.41 40) (xy 216 40)) (stroke (width 0) (type default)) (uuid "wg3"))
  (wire (pts (xy 216 40) (xy 216 155)) (stroke (width 0) (type default)) (uuid "wg3b"))
  (wire (pts (xy 216 155) (xy 13.97 155)) (stroke (width 0) (type default)) (uuid "wg3c"))
  
  (wire (pts (xy 205.41 45) (xy 218 45)) (stroke (width 0) (type default)) (uuid "wg4"))
  (wire (pts (xy 218 45) (xy 218 160)) (stroke (width 0) (type default)) (uuid "wg4b"))
  (wire (pts (xy 218 160) (xy 13.97 160)) (stroke (width 0) (type default)) (uuid "wg4c"))
  
  (wire (pts (xy 205.41 50) (xy 220 50)) (stroke (width 0) (type default)) (uuid "wg5"))
  (wire (pts (xy 220 50) (xy 220 165)) (stroke (width 0) (type default)) (uuid "wg5b"))
  (wire (pts (xy 220 165) (xy 13.97 165)) (stroke (width 0) (type default)) (uuid "wg5c"))
  
  (wire (pts (xy 205.41 55) (xy 222 55)) (stroke (width 0) (type default)) (uuid "wg6"))
  (wire (pts (xy 222 55) (xy 222 170)) (stroke (width 0) (type default)) (uuid "wg6b"))
  (wire (pts (xy 222 170) (xy 13.97 170)) (stroke (width 0) (type default)) (uuid "wg6c"))
  
  (wire (pts (xy 205.41 60) (xy 224 60)) (stroke (width 0) (type default)) (uuid "wg7"))
  (wire (pts (xy 224 60) (xy 224 175)) (stroke (width 0) (type default)) (uuid "wg7b"))
  (wire (pts (xy 224 175) (xy 13.97 175)) (stroke (width 0) (type default)) (uuid "wg7c"))
  
  ; Junctions
  (junction (at 100 40) (diameter 0) (uuid "jmain1"))
  
  (sheet_instances (path "/" (page "1")))
)'''
    return sch

# Regenerate all
def main():
    # Generate all sheets
    with open("power.kicad_sch", "w") as f:
        f.write(gen_power_sch())
    print("Generated: power.kicad_sch (v1.1 with hierarchical labels)")
    
    with open("digital.kicad_sch", "w") as f:
        f.write(gen_digital_sch())
    print("Generated: digital.kicad_sch (v1.1 with hierarchical labels)")
    
    with open("analog.kicad_sch", "w") as f:
        f.write(gen_analog_sch())
    print("Generated: analog.kicad_sch (v1.1 with hierarchical labels)")
    
    with open("tuboquant_mux_lna.kicad_sch", "w") as f:
        f.write(gen_main_sch())
    print("Generated: tuboquant_mux_lna.kicad_sch (v1.1 with proper connections)")
    
    print("\n✅ All schematics updated with proper hierarchical labels and connections!")
    print("\nLabel Structure:")
    print("  POWER sheet outputs: +12V, +5V, +3V3, GND (hierarchical labels)")
    print("  DIGITAL sheet inputs: +5V, GND / outputs: GATE0-7")
    print("  ANALOG sheet inputs: +5V, GND, GATE0-7, MUX_A/B/C")
    print("  MAIN sheet: Connects all hierarchical pins with wires")

if __name__ == "__main__":
    main()
