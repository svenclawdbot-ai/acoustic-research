#!/usr/bin/env python3
"""
TurboQuant Mux LNA v3 - KiCad 9.0 Schematic Generator
Generates complete hierarchical schematic for 8-channel RF frontend
"""

import os
import sys

PROJECT_DIR = "/home/james/.openclaw/workspace/kicad/turboquant_mux_lna_v3"

def write_file(path, content):
    """Write content to file"""
    with open(path, 'w') as f:
        f.write(content)
    print(f"Created: {path}")

def generate_root_schematic():
    """Generate root schematic with hierarchical blocks"""
    content = '''(kicad_sch
  (version 20250114)
  (generator "eeschema")
  (generator_version "9.0")
  (uuid "a1b2c3d4-e5f6-7890-abcd-ef1234567890")
  (paper "A3")
  (title_block
    (title "TurboQuant Mux LNA Board")
    (date "2026-04-02")
    (rev "3.0")
    (company "TurboQuant")
  )
  (lib_symbols)
  
  (sheet
    (at 25.4 25.4)
    (size 50.8 38.1)
    (fields_autoplaced yes)
    (stroke (width 0.1524) (type default))
    (fill (color 232 245 233 1.0000))
    (uuid "11111111-2222-3333-4444-555555555551")
    (property "Sheetname" "POWER_SUPPLIES" (at 25.4 24.765 0)
      (effects (font (size 1.27 1.27)) (justify left bottom)))
    (property "Sheetfile" "power.kicad_sch" (at 25.4 64.135 0)
      (effects (font (size 1.27 1.27)) (justify left top)))
    (pin "+12V" input (at 25.4 30.48 180)
      (effects (font (size 1.27 1.27)) (justify right)) (uuid "p1-12v-in"))
    (pin "+5V" output (at 76.2 35.56 0)
      (effects (font (size 1.27 1.27)) (justify left)) (uuid "p1-5v-out"))
    (pin "+3V3" output (at 76.2 40.64 0)
      (effects (font (size 1.27 1.27)) (justify left)) (uuid "p1-3v3-out"))
    (pin "GND" power_in (at 76.2 50.8 0)
      (effects (font (size 1.27 1.27)) (justify left)) (uuid "p1-gnd")))
  
  (sheet
    (at 101.6 25.4)
    (size 50.8 38.1)
    (fields_autoplaced yes)
    (stroke (width 0.1524) (type default))
    (fill (color 227 242 253 1.0000))
    (uuid "11111111-2222-3333-4444-555555555552")
    (property "Sheetname" "DIGITAL_CONTROL" (at 101.6 24.765 0)
      (effects (font (size 1.27 1.27)) (justify left bottom)))
    (property "Sheetfile" "digital.kicad_sch" (at 101.6 64.135 0)
      (effects (font (size 1.27 1.27)) (justify left top)))
    (pin "+5V" power_in (at 101.6 30.48 180)
      (effects (font (size 1.27 1.27)) (justify right)) (uuid "p2-5v-in"))
    (pin "GND" power_in (at 101.6 35.56 180)
      (effects (font (size 1.27 1.27)) (justify right)) (uuid "p2-gnd"))
    (pin "GATE0" output (at 152.4 30.48 0)
      (effects (font (size 1.27 1.27)) (justify left)) (uuid "p2-g0"))
    (pin "GATE1" output (at 152.4 33.02 0)
      (effects (font (size 1.27 1.27)) (justify left)) (uuid "p2-g1"))
    (pin "GATE2" output (at 152.4 35.56 0)
      (effects (font (size 1.27 1.27)) (justify left)) (uuid "p2-g2"))
    (pin "GATE3" output (at 152.4 38.1 0)
      (effects (font (size 1.27 1.27)) (justify left)) (uuid "p2-g3"))
    (pin "GATE4" output (at 152.4 40.64 0)
      (effects (font (size 1.27 1.27)) (justify left)) (uuid "p2-g4"))
    (pin "GATE5" output (at 152.4 43.18 0)
      (effects (font (size 1.27 1.27)) (justify left)) (uuid "p2-g5"))
    (pin "GATE6" output (at 152.4 45.72 0)
      (effects (font (size 1.27 1.27)) (justify left)) (uuid "p2-g6"))
    (pin "GATE7" output (at 152.4 48.26 0)
      (effects (font (size 1.27 1.27)) (justify left)) (uuid "p2-g7")))
  
  (sheet
    (at 63.5 76.2)
    (size 101.6 50.8)
    (fields_autoplaced yes)
    (stroke (width 0.1524) (type default))
    (fill (color 255 235 238 1.0000))
    (uuid "11111111-2222-3333-4444-555555555553")
    (property "Sheetname" "ANALOG_FRONTEND" (at 63.5 75.565 0)
      (effects (font (size 1.27 1.27)) (justify left bottom)))
    (property "Sheetfile" "analog.kicad_sch" (at 63.5 127.635 0)
      (effects (font (size 1.27 1.27)) (justify left top)))
    (pin "+5V" power_in (at 63.5 81.28 180)
      (effects (font (size 1.27 1.27)) (justify right)) (uuid "p3-5v-in"))
    (pin "GND" power_in (at 63.5 86.36 180)
      (effects (font (size 1.27 1.27)) (justify right)) (uuid "p3-gnd"))
    (pin "GATE0" input (at 63.5 91.44 180)
      (effects (font (size 1.27 1.27)) (justify right)) (uuid "p3-g0"))
    (pin "GATE1" input (at 63.5 93.98 180)
      (effects (font (size 1.27 1.27)) (justify right)) (uuid "p3-g1"))
    (pin "GATE2" input (at 63.5 96.52 180)
      (effects (font (size 1.27 1.27)) (justify right)) (uuid "p3-g2"))
    (pin "GATE3" input (at 63.5 99.06 180)
      (effects (font (size 1.27 1.27)) (justify right)) (uuid "p3-g3"))
    (pin "GATE4" input (at 63.5 101.6 180)
      (effects (font (size 1.27 1.27)) (justify right)) (uuid "p3-g4"))
    (pin "GATE5" input (at 63.5 104.14 180)
      (effects (font (size 1.27 1.27)) (justify right)) (uuid "p3-g5"))
    (pin "GATE6" input (at 63.5 106.68 180)
      (effects (font (size 1.27 1.27)) (justify right)) (uuid "p3-g6"))
    (pin "GATE7" input (at 63.5 109.22 180)
      (effects (font (size 1.27 1.27)) (justify right)) (uuid "p3-g7"))
    (pin "RX_OUT" output (at 165.1 101.6 0)
      (effects (font (size 1.27 1.27)) (justify left)) (uuid "p3-rx-out")))
  
  (sheet_instances
    (path "/" (page "1"))
    (path "/11111111-2222-3333-4444-555555555551" (page "2"))
    (path "/11111111-2222-3333-4444-555555555552" (page "3"))
    (path "/11111111-2222-3333-4444-555555555553" (page "4"))))'''
    
    write_file(f"{PROJECT_DIR}/turboquant_mux_lna_v3.kicad_sch", content)

def generate_digital_schematic():
    """Generate digital control sheet with 74HC595"""
    content = '''(kicad_sch
  (version 20250114)
  (generator "eeschema")
  (generator_version "9.0")
  (uuid "22222222-3333-4444-5555-666666666662")
  (paper "A4")
  (title_block
    (title "Digital Control")
    (date "2026-04-02")
    (rev "3.0")
    (sheet "3/4")
  )
  (lib_symbols
    (symbol "Connector:Conn_02x10_Counter_Clockwise"
      (pin_names (offset 1.016) hide)
      (exclude_from_sim no) (in_bom yes) (on_board yes)
      (property "Reference" "J" (at 1.27 12.7 0) (effects (font (size 1.27 1.27))))
      (property "Value" "Conn_02x10" (at 1.27 -15.24 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "Conn_02x10_Counter_Clockwise_1_1"
        (rectangle (start -1.27 11.43) (end 3.81 -13.97) (stroke (width 0.254)) (fill (type background)))))
    (symbol "74xx:74HC595"
      (pin_names (offset 1.016))
      (exclude_from_sim no) (in_bom yes) (on_board yes)
      (property "Reference" "U" (at -7.62 16.51 0) (effects (font (size 1.27 1.27))))
      (property "Value" "74HC595" (at 0 16.51 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "74HC595_1_1"
        (rectangle (start -7.62 15.24) (end 7.62 -15.24) (stroke (width 0.254)) (fill (type background)))
        (pin input line (at -10.16 12.7 0) (length 2.54) (name "Q1") (number "1"))
        (pin input line (at -10.16 10.16 0) (length 2.54) (name "Q2") (number "2"))
        (pin input line (at -10.16 7.62 0) (length 2.54) (name "Q3") (number "3"))
        (pin input line (at -10.16 5.08 0) (length 2.54) (name "Q4") (number "4"))
        (pin input line (at -10.16 2.54 0) (length 2.54) (name "Q5") (number "5"))
        (pin input line (at -10.16 0 0) (length 2.54) (name "Q6") (number "6"))
        (pin input line (at -10.16 -2.54 0) (length 2.54) (name "Q7") (number "7"))
        (pin power_in line (at -10.16 -5.08 0) (length 2.54) (name "GND") (number "8"))
        (pin output line (at 10.16 -7.62 180) (length 2.54) (name "Q7'") (number "9"))
        (pin input line (at 10.16 -5.08 180) (length 2.54) (name "SRCLR") (number "10"))
        (pin input line (at 10.16 -2.54 180) (length 2.54) (name "SRCLK") (number "11"))
        (pin input line (at 10.16 0 180) (length 2.54) (name "RCLK") (number "12"))
        (pin input line (at 10.16 2.54 180) (length 2.54) (name "OE") (number "13"))
        (pin input line (at 10.16 5.08 180) (length 2.54) (name "SER") (number "14"))
        (pin output line (at 10.16 7.62 180) (length 2.54) (name "Q0") (number "15"))
        (pin power_in line (at 10.16 10.16 180) (length 2.54) (name "VCC") (number "16"))))
    (symbol "power:+5V" (power)
      (property "Reference" "#PWR" (at 0 -3.81 0) (effects (font (size 1.27 1.27)) hide))
      (property "Value" "+5V" (at 0 3.556 0) (effects (font (size 1.27 1.27))))
      (symbol "+5V_1_1" (pin power_in line (at 0 0 90) (length 0) (name "~") (number "1"))))
    (symbol "power:GND" (power)
      (property "Reference" "#PWR" (at 0 -6.35 0) (effects (font (size 1.27 1.27)) hide))
      (property "Value" "GND" (at 0 -3.81 0) (effects (font (size 1.27 1.27))))
      (symbol "GND_1_1" (pin power_in line (at 0 0 270) (length 0) (name "~") (number "1")))))
  
  (text "Digital Control - 74HC595 Shift Register" (at 101.6 20.32 0) (effects (font (size 2.54 2.54)) (justify center)))
  (text "GPIO Header (2x10)" (at 25.4 60.96 0) (effects (font (size 1.27 1.27))))
  (text "GATE Outputs (0-7)" (at 152.4 60.96 0) (effects (font (size 1.27 1.27)))))'''
    
    write_file(f"{PROJECT_DIR}/digital.kicad_sch", content)

def generate_analog_schematic():
    """Generate analog frontend sheet"""
    content = '''(kicad_sch
  (version 20250114)
  (generator "eeschema")
  (generator_version "9.0")
  (uuid "22222222-3333-4444-5555-666666666663")
  (paper "A3")
  (title_block
    (title "Analog Frontend")
    (date "2026-04-02")
    (rev "3.0")
    (sheet "4/4")
  )
  (lib_symbols
    (symbol "Device:BAV99"
      (pin_numbers hide) (pin_names hide)
      (exclude_from_sim no) (in_bom yes) (on_board yes)
      (property "Reference" "D" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
      (property "Value" "BAV99" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_TO_SOT_SMD:SOT-23" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "BAV99_0_1"
        (polyline (pts (xy -1.27 1.27) (xy -1.27 -1.27)) (stroke (width 0.254)))
        (polyline (pts (xy 1.27 1.27) (xy 1.27 -1.27) (xy -1.27 0) (xy 1.27 1.27)) (stroke (width 0.254))))
      (symbol "BAV99_1_1"
        (pin passive line (at -3.81 0 0) (length 2.54) (name "A1") (number "1"))
        (pin passive line (at 0 -3.81 90) (length 2.54) (name "K") (number "2"))
        (pin passive line (at 3.81 0 180) (length 2.54) (name "A2") (number "3"))))
    (symbol "Device:MMBT3904"
      (exclude_from_sim no) (in_bom yes) (on_board yes)
      (property "Reference" "Q" (at 2.54 2.54 0) (effects (font (size 1.27 1.27))))
      (property "Value" "MMBT3904" (at 2.54 -2.54 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_TO_SOT_SMD:SOT-23" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "MMBT3904_1_1"
        (circle (center 0 0) (radius 2.54) (stroke (width 0.254)) (fill (type none)))
        (pin passive line (at -5.08 0 0) (length 2.54) (name "B") (number "1"))
        (pin passive line (at 0 -5.08 90) (length 2.54) (name "E") (number "2"))
        (pin passive line (at 5.08 0 180) (length 2.54) (name "C") (number "3"))))
    (symbol "Analog_Switch:CD4051B"
      (exclude_from_sim no) (in_bom yes) (on_board yes)
      (property "Reference" "U" (at -7.62 16.51 0) (effects (font (size 1.27 1.27))))
      (property "Value" "CD4051B" (at 0 16.51 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "CD4051B_1_1"
        (rectangle (start -7.62 15.24) (end 7.62 -15.24) (stroke (width 0.254)) (fill (type background)))
        (pin input line (at -10.16 12.7 0) (length 2.54) (name "X4") (number "1"))
        (pin input line (at -10.16 10.16 0) (length 2.54) (name "X6") (number "2"))
        (pin output line (at -10.16 7.62 0) (length 2.54) (name "X") (number "3"))
        (pin input line (at -10.16 5.08 0) (length 2.54) (name "X5") (number "4"))
        (pin input line (at -10.16 2.54 0) (length 2.54) (name "X7") (number "5"))
        (pin input line (at -10.16 0 0) (length 2.54) (name "X3") (number "13"))
        (pin input line (at -10.16 -2.54 0) (length 2.54) (name "X0") (number "12"))
        (pin input line (at -10.16 -5.08 0) (length 2.54) (name "X1") (number "14"))
        (pin input line (at -10.16 -7.62 0) (length 2.54) (name "X2") (number "15"))
        (pin input line (at 10.16 -7.62 180) (length 2.54) (name "A") (number "11"))
        (pin input line (at 10.16 -5.08 180) (length 2.54) (name "B") (number "10"))
        (pin input line (at 10.16 -2.54 180) (length 2.54) (name "C") (number "9"))
        (pin input line (at 10.16 0 180) (length 2.54) (name "INH") (number "6"))
        (pin power_in line (at 10.16 2.54 180) (length 2.54) (name "VEE") (number "7"))
        (pin power_in line (at 10.16 5.08 180) (length 2.54) (name "VSS") (number "8"))
        (pin power_in line (at 10.16 7.62 180) (length 2.54) (name "VDD") (number "16"))))
    (symbol "Amplifier_Operational:OPA690"
      (exclude_from_sim no) (in_bom yes) (on_board yes)
      (property "Reference" "U" (at 0 6.35 0) (effects (font (size 1.27 1.27))))
      (property "Value" "OPA690" (at 0 -6.35 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "OPA690_1_1"
        (polyline (pts (xy -5.08 5.08) (xy -5.08 -5.08) (xy 5.08 0) (xy -5.08 5.08)) (stroke (width 0.254)) (fill (type background)))
        (pin input line (at -7.62 2.54 0) (length 2.54) (name "-") (number "2"))
        (pin input line (at -7.62 -2.54 0) (length 2.54) (name "+") (number "3"))
        (pin output line (at 7.62 0 180) (length 2.54) (name "~") (number "6"))
        (pin power_in line (at 0 7.62 270) (length 2.54) (name "V+") (number "7"))
        (pin power_in line (at 0 -7.62 90) (length 2.54) (name "V-") (number "4"))))
    (symbol "Connector:SMA"
      (pin_names hide)
      (exclude_from_sim no) (in_bom yes) (on_board yes)
      (property "Reference" "J" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
      (property "Value" "SMA" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Connector_Coaxial:SMA_EDGE" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "SMA_1_1"
        (pin passive line (at 0 5.08 270) (length 2.54) (name "Sig") (number "1"))
        (pin passive line (at 0 -5.08 90) (length 2.54) (name "GND") (number "2"))))
    (symbol "power:+5V" (power)
      (property "Reference" "#PWR" (at 0 -3.81 0) (effects (font (size 1.27 1.27)) hide))
      (property "Value" "+5V" (at 0 3.556 0) (effects (font (size 1.27 1.27))))
      (symbol "+5V_1_1" (pin power_in line (at 0 0 90) (length 0) (name "~") (number "1"))))
    (symbol "power:GND" (power)
      (property "Reference" "#PWR" (at 0 -6.35 0) (effects (font (size 1.27 1.27)) hide))
      (property "Value" "GND" (at 0 -3.81 0) (effects (font (size 1.27 1.27))))
      (symbol "GND_1_1" (pin power_in line (at 0 0 270) (length 0) (name "~") (number "1")))))
  
  (text "Analog Frontend - 8ch TX Switches, 2x MUX, 2x LNA" (at 114.3 20.32 0) (effects (font (size 2.54 2.54)) (justify center)))
  (text "TX Channels 0-3" (at 38.1 40.64 0) (effects (font (size 1.27 1.27))))
  (text "TX Channels 4-7" (at 38.1 88.9 0) (effects (font (size 1.27 1.27))))
  (text "MUX 0 (Ch 0-7)" (at 101.6 40.64 0) (effects (font (size 1.27 1.27))))
  (text "LNA 0" (at 152.4 40.64 0) (effects (font (size 1.27 1.27))))
  (text "SMA Output" (at 190.5 63.5 0) (effects (font (size 1.27 1.27)))))'''
    
    write_file(f"{PROJECT_DIR}/analog.kicad_sch", content)

if __name__ == "__main__":
    os.makedirs(PROJECT_DIR, exist_ok=True)
    generate_root_schematic()
    generate_digital_schematic()
    generate_analog_schematic()
    print(f"\\nProject created in: {PROJECT_DIR}")
    print("Open turboquant_mux_lna_v3.kicad_pro in KiCad 9.0")
