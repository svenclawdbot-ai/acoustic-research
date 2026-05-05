#!/usr/bin/env python3
"""Generate complete analog.kicad_sch for turboquant_mux_lna_v3"""

import uuid

def gen_uuid():
    return str(uuid.uuid4())

# Header
content = """(kicad_sch
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
        (pin input line (at -5.08 0 0) (length 2.54) (name "B") (number "1"))
        (pin passive line (at 0 -5.08 90) (length 2.54) (name "E") (number "2"))
        (pin passive line (at 5.08 0 180) (length 2.54) (name "C") (number "3"))))
    
    (symbol "Analog_Switch:CD4051B"
      (exclude_from_sim no) (in_bom yes) (on_board yes)
      (property "Reference" "U" (at -7.62 16.51 0) (effects (font (size 1.27 1.27))))
      (property "Value" "CD4051B" (at 0 16.51 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "CD4051B_1_1"
        (rectangle (start -7.62 15.24) (end 7.62 -15.24) (stroke (width 0.254)) (fill (type background)))
        (pin passive line (at -10.16 12.7 0) (length 2.54) (name "X4") (number "1"))
        (pin passive line (at -10.16 10.16 0) (length 2.54) (name "X6") (number "2"))
        (pin passive line (at -10.16 7.62 0) (length 2.54) (name "X") (number "3"))
        (pin passive line (at -10.16 5.08 0) (length 2.54) (name "X5") (number "4"))
        (pin passive line (at -10.16 2.54 0) (length 2.54) (name "X7") (number "5"))
        (pin input line (at 10.16 0 180) (length 2.54) (name "INH") (number "6"))
        (pin power_in line (at 10.16 2.54 180) (length 2.54) (name "VEE") (number "7"))
        (pin power_in line (at 10.16 5.08 180) (length 2.54) (name "VSS") (number "8"))
        (pin input line (at 10.16 -7.62 180) (length 2.54) (name "A") (number "11"))
        (pin input line (at 10.16 -5.08 180) (length 2.54) (name "B") (number "10"))
        (pin input line (at 10.16 -2.54 180) (length 2.54) (name "C") (number "9"))
        (pin passive line (at -10.16 -2.54 0) (length 2.54) (name "X3") (number "13"))
        (pin passive line (at -10.16 -5.08 0) (length 2.54) (name "X0") (number "12"))
        (pin passive line (at -10.16 -7.62 0) (length 2.54) (name "X1") (number "14"))
        (pin passive line (at -10.16 -10.16 0) (length 2.54) (name "X2") (number "15"))
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
      (property "Footprint" "Connector_Coaxial:SMA_Amphenol_132134_EDGE" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "SMA_1_1"
        (pin passive line (at 0 5.08 270) (length 2.54) (name "Sig") (number "1"))
        (pin passive line (at 0 -5.08 90) (length 2.54) (name "GND") (number "2"))))
    
    (symbol "Device:R"
      (pin_numbers hide) (pin_names (offset 0))
      (exclude_from_sim no) (in_bom yes) (on_board yes)
      (property "Reference" "R" (at 2.54 0 90) (effects (font (size 1.27 1.27))))
      (property "Value" "R" (at -2.54 0 90) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "R_0_1"
        (rectangle (start -1.016 -2.54) (end 1.016 2.54) (stroke (width 0.254)) (fill (type none))))
      (symbol "R_1_1"
        (pin passive line (at 0 3.81 270) (length 1.27) (name "~") (number "1"))
        (pin passive line (at 0 -3.81 90) (length 1.27) (name "~") (number "2"))))
    
    (symbol "Device:C"
      (pin_numbers hide) (pin_names (offset 0.254))
      (exclude_from_sim no) (in_bom yes) (on_board yes)
      (property "Reference" "C" (at 0.635 2.54 0) (effects (font (size 1.27 1.27)) (justify left)))
      (property "Value" "C" (at 0.635 -2.54 0) (effects (font (size 1.27 1.27)) (justify left)))
      (property "Footprint" "" (at 0.9652 -3.81 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "C_0_1"
        (polyline (pts (xy -2.032 0.762) (xy 2.032 0.762)) (stroke (width 0.508)))
        (polyline (pts (xy -2.032 -0.762) (xy 2.032 -0.762)) (stroke (width 0.508))))
      (symbol "C_1_1"
        (pin passive line (at 0 3.81 270) (length 2.794) (name "~") (number "1"))
        (pin passive line (at 0 -3.81 90) (length 2.794) (name "~") (number "2"))))
    
    (symbol "power:+5V" (power)
      (property "Reference" "#PWR" (at 0 -3.81 0) (effects (font (size 1.27 1.27)) hide))
      (property "Value" "+5V" (at 0 3.556 0) (effects (font (size 1.27 1.27))))
      (symbol "+5V_1_1" (pin power_in line (at 0 0 90) (length 0) (name "~") (number "1"))))
    
    (symbol "power:GND" (power)
      (property "Reference" "#PWR" (at 0 -6.35 0) (effects (font (size 1.27 1.27)) hide))
      (property "Value" "GND" (at 0 -3.81 0) (effects (font (size 1.27 1.27))))
      (symbol "GND_1_1" (pin power_in line (at 0 0 270) (length 0) (name "~") (number "1")))))
"""

# Hierarchical pins
content += """
  (hierarchical_pin "GATE0" (at 25.4 91.44 180)
    (effects (font (size 1.27 1.27)) (justify right))
    (uuid "hier-g0-in")
    (pin_type input))
  (hierarchical_pin "GATE1" (at 25.4 93.98 180)
    (effects (font (size 1.27 1.27)) (justify right))
    (uuid "hier-g1-in")
    (pin_type input))
  (hierarchical_pin "GATE2" (at 25.4 96.52 180)
    (effects (font (size 1.27 1.27)) (justify right))
    (uuid "hier-g2-in")
    (pin_type input))
  (hierarchical_pin "GATE3" (at 25.4 99.06 180)
    (effects (font (size 1.27 1.27)) (justify right))
    (uuid "hier-g3-in")
    (pin_type input))
  (hierarchical_pin "GATE4" (at 25.4 101.6 180)
    (effects (font (size 1.27 1.27)) (justify right))
    (uuid "hier-g4-in")
    (pin_type input))
  (hierarchical_pin "GATE5" (at 25.4 104.14 180)
    (effects (font (size 1.27 1.27)) (justify right))
    (uuid "hier-g5-in")
    (pin_type input))
  (hierarchical_pin "GATE6" (at 25.4 106.68 180)
    (effects (font (size 1.27 1.27)) (justify right))
    (uuid "hier-g6-in")
    (pin_type input))
  (hierarchical_pin "GATE7" (at 25.4 109.22 180)
    (effects (font (size 1.27 1.27)) (justify right))
    (uuid "hier-g7-in")
    (pin_type input))
  (hierarchical_pin "+5V" (at 63.5 81.28 180)
    (effects (font (size 1.27 1.27)) (justify right))
    (uuid "hier-5v-analog")
    (pin_type power_in))
  (hierarchical_pin "GND" (at 63.5 86.36 180)
    (effects (font (size 1.27 1.27)) (justify right))
    (uuid "hier-gnd-analog")
    (pin_type power_in))
  (hierarchical_pin "RX_OUT" (at 165.1 101.6 0)
    (effects (font (size 1.27 1.27)) (justify left))
    (uuid "hier-rx-out")
    (pin_type output))
"""

# TX Switch Channels 0-7 (BAV99 + MMBT3904 + base resistor)
for i in range(8):
    y_pos = 91.44 + i * 7.62
    content += f"""
  (symbol (lib_id "Device:BAV99") (at 38.1 {y_pos:.2f} 90) (unit 1)
    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "{gen_uuid()}")
    (property "Reference" "D{i}" (at 33.02 {y_pos:.2f} 90) (effects (font (size 1.27 1.27))))
    (property "Value" "BAV99" (at 43.18 {y_pos:.2f} 90) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_TO_SOT_SMD:SOT-23" (at 38.1 {y_pos:.2f} 0) (effects (font (size 1.27 1.27)) hide))
    (pin "1" (uuid "{gen_uuid()}")) (pin "2" (uuid "{gen_uuid()}")) (pin "3" (uuid "{gen_uuid()}")))
  (symbol (lib_id "Device:MMBT3904") (at 50.8 {y_pos:.2f} 0) (unit 1)
    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "{gen_uuid()}")
    (property "Reference" "Q{i}" (at 50.8 {y_pos+5.08:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "MMBT3904" (at 50.8 {y_pos+7.62:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_TO_SOT_SMD:SOT-23" (at 50.8 {y_pos:.2f} 0) (effects (font (size 1.27 1.27)) hide))
    (pin "1" (uuid "{gen_uuid()}")) (pin "2" (uuid "{gen_uuid()}")) (pin "3" (uuid "{gen_uuid()}")))
  (symbol (lib_id "Device:R") (at 44.45 {y_pos-6.35:.2f} 0) (unit 1)
    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "{gen_uuid()}")
    (property "Reference" "R{i}" (at 48.26 {y_pos-6.35:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))
    (property "Value" "1k" (at 40.64 {y_pos-6.35:.2f} 0) (effects (font (size 1.27 1.27)) (justify right)))
    (property "Footprint" "Resistor_SMD:R_0805_2012Metric" (at 44.45 {y_pos-6.35:.2f} 0) (effects (font (size 1.27 1.27)) hide))
    (pin "1" (uuid "{gen_uuid()}")) (pin "2" (uuid "{gen_uuid()}")))
"""

print(content[:5000])
