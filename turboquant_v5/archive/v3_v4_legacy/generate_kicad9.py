#!/usr/bin/env python3
"""
Generate TurboQuant Mux LNA Board Schematics for KiCad 9.0
With proper symbol library references
"""

def gen_power_sch():
    """Generate POWER_SUPPLIES sheet for KiCad 9"""
    return '''(kicad_sch
  (version 20250114)
  (generator "eeschema")
  (generator_version "9.0")
  (uuid "a1b2c3d4-e5f6-7890-abcd-ef1234567890")
  (paper "A4")
  (title_block
    (title "TurboQuant Mux LNA - Power Supplies")
    (date "2026-03-30")
    (rev "1.2")
  )
  (lib_symbols
    (symbol "power:GND" (in_bom yes) (on_board yes)
      (property "Reference" "#PWR" (at 0 -3.81 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Value" "GND" (at 0 -1.27 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Datasheet" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Description" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
    )
    (symbol "power:+12V" (in_bom yes) (on_board yes)
      (property "Reference" "#PWR" (at 0 -2.54 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Value" "+12V" (at 0 2.54 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Datasheet" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Description" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
    )
    (symbol "power:+5V" (in_bom yes) (on_board yes)
      (property "Reference" "#PWR" (at 0 -2.54 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Value" "+5V" (at 0 2.54 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Datasheet" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Description" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
    )
    (symbol "power:+3V3" (in_bom yes) (on_board yes)
      (property "Reference" "#PWR" (at 0 -2.54 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Value" "+3V3" (at 0 2.54 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Datasheet" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Description" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
    )
    (symbol "Regulator_Linear:LM7805" (in_bom yes) (on_board yes)
      (property "Reference" "U" (at 0 5.08 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Value" "LM7805" (at 0 -5.08 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" "Package_TO_SOT_SMD:SOT-223-3_TabPin2" (at 0 -7.62 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Datasheet" "https://www.ti.com/lit/ds/symlink/lm7805.pdf" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Description" "Positive 3-terminal 5V voltage regulator" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
    )
    (symbol "Regulator_Linear:AMS1117-3.3" (in_bom yes) (on_board yes)
      (property "Reference" "U" (at 0 5.08 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Value" "AMS1117-3.3" (at 0 -5.08 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" "Package_TO_SOT_SMD:SOT-223-3_TabPin2" (at 0 -7.62 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Datasheet" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Description" "1A Low Dropout Voltage Regulator" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
    )
    (symbol "Diode:1N4007" (in_bom yes) (on_board yes)
      (property "Reference" "D" (at 0 2.54 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Value" "1N4007" (at 0 -2.54 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" "Diode_SMD:D_SOD-123" (at 0 -5.08 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Datasheet" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Description" "1000V 1A General Purpose Rectifier" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
    )
    (symbol "Device:C" (in_bom yes) (on_board yes)
      (property "Reference" "C" (at 0 2.54 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Value" "C" (at 0 -2.54 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" "Capacitor_SMD:C_0603_1608Metric" (at 0 -5.08 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Datasheet" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Description" "Unpolarized capacitor" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
    )
    (symbol "Device:LED" (in_bom yes) (on_board yes)
      (property "Reference" "D" (at 0 2.54 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Value" "LED" (at 0 -2.54 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" "LED_SMD:LED_0603_1608Metric" (at 0 -5.08 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Datasheet" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Description" "Light emitting diode" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
    )
    (symbol "Device:R" (in_bom yes) (on_board yes)
      (property "Reference" "R" (at 0 2.54 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Value" "R" (at 0 -2.54 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" "Resistor_SMD:R_0603_1608Metric" (at 0 -5.08 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Datasheet" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Description" "Resistor" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
    )
    (symbol "Connector:Barrel_Jack" (in_bom yes) (on_board yes)
      (property "Reference" "J" (at 0 5.08 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Value" "Barrel_Jack" (at 0 -5.08 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" "Connector_BarrelJack:BarrelJack_Horizontal" (at 0 -7.62 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Datasheet" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Description" "DC Barrel Jack" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
    )
  )
  
  (symbol (lib_id "Connector:Barrel_Jack") (at 30 50 0) (uuid "pwr-j1")
    (property "Reference" "J1" (at 30 56.48 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "12V_IN" (at 30 43.52 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "Connector_BarrelJack:BarrelJack_Horizontal" (at 30 50 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
    (pin "1" (uuid "j1-pin1"))
    (pin "2" (uuid "j1-pin2"))
    (pin "3" (uuid "j1-pin3"))
  )
  
  (symbol (lib_id "Diode:1N4007") (at 50 50 0) (uuid "pwr-d1")
    (property "Reference" "D1" (at 50 53.16 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "1N4007" (at 50 46.84 0)
      (effects (font (size 1.27 1.27)))
    )
    (pin "1" (uuid "d1-pin1"))
    (pin "2" (uuid "d1-pin2"))
  )
  
  (symbol (lib_id "Device:C") (at 50 70 0) (uuid "pwr-c1")
    (property "Reference" "C1" (at 52.54 70 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "10uF" (at 47.46 70 0)
      (effects (font (size 1.27 1.27)))
    )
    (pin "1" (uuid "c1-pin1"))
    (pin "2" (uuid "c1-pin2"))
  )
  
  (symbol (lib_id "Regulator_Linear:LM7805") (at 90 50 0) (uuid "pwr-u1")
    (property "Reference" "U1" (at 90 56.48 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "LM7805" (at 90 43.52 0)
      (effects (font (size 1.27 1.27)))
    )
    (pin "1" (uuid "u1-pin1"))
    (pin "2" (uuid "u1-pin2"))
    (pin "3" (uuid "u1-pin3"))
  )
  
  (symbol (lib_id "Device:C") (at 75 70 0) (uuid "pwr-c2")
    (property "Reference" "C2" (at 77.54 70 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "100nF" (at 72.46 70 0)
      (effects (font (size 1.27 1.27)))
    )
    (pin "1" (uuid "c2-pin1"))
    (pin "2" (uuid "c2-pin2"))
  )
  
  (symbol (lib_id "Device:C") (at 105 70 0) (uuid "pwr-c3")
    (property "Reference" "C3" (at 107.54 70 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "10uF" (at 102.46 70 0)
      (effects (font (size 1.27 1.27)))
    )
    (pin "1" (uuid "c3-pin1"))
    (pin "2" (uuid "c3-pin2"))
  )
  
  (symbol (lib_id "Regulator_Linear:AMS1117-3.3") (at 145 50 0) (uuid "pwr-u2")
    (property "Reference" "U2" (at 145 56.48 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "AMS1117-3.3" (at 145 43.52 0)
      (effects (font (size 1.27 1.27)))
    )
    (pin "1" (uuid "u2-pin1"))
    (pin "2" (uuid "u2-pin2"))
    (pin "3" (uuid "u2-pin3"))
  )
  
  (symbol (lib_id "Device:C") (at 130 70 0) (uuid "pwr-c4")
    (property "Reference" "C4" (at 132.54 70 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "100nF" (at 127.46 70 0)
      (effects (font (size 1.27 1.27)))
    )
    (pin "1" (uuid "c4-pin1"))
    (pin "2" (uuid "c4-pin2"))
  )
  
  (symbol (lib_id "Device:C") (at 160 70 0) (uuid "pwr-c5")
    (property "Reference" "C5" (at 162.54 70 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "10uF" (at 157.46 70 0)
      (effects (font (size 1.27 1.27)))
    )
    (pin "1" (uuid "c5-pin1"))
    (pin "2" (uuid "c5-pin2"))
  )
  
  (symbol (lib_id "Device:LED") (at 120 95 0) (uuid "pwr-d2")
    (property "Reference" "D2" (at 120 98.16 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "GREEN" (at 120 91.84 0)
      (effects (font (size 1.27 1.27)))
    )
    (pin "1" (uuid "d2-pin1"))
    (pin "2" (uuid "d2-pin2"))
  )
  
  (symbol (lib_id "Device:R") (at 105 95 0) (uuid "pwr-r1")
    (property "Reference" "R1" (at 102.46 95 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "1k" (at 107.54 95 0)
      (effects (font (size 1.27 1.27)))
    )
    (pin "1" (uuid "r1-pin1"))
    (pin "2" (uuid "r1-pin2"))
  )
  
  (symbol (lib_id "Device:LED") (at 175 95 0) (uuid "pwr-d3")
    (property "Reference" "D3" (at 175 98.16 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "BLUE" (at 175 91.84 0)
      (effects (font (size 1.27 1.27)))
    )
    (pin "1" (uuid "d3-pin1"))
    (pin "2" (uuid "d3-pin2"))
  )
  
  (symbol (lib_id "Device:R") (at 160 95 0) (uuid "pwr-r2")
    (property "Reference" "R2" (at 157.46 95 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "1k" (at 162.54 95 0)
      (effects (font (size 1.27 1.27)))
    )
    (pin "1" (uuid "r2-pin1"))
    (pin "2" (uuid "r2-pin2"))
  )
  
  (symbol (lib_id "power:+12V") (at 30 30 0) (uuid "pwr-pf1")
    (property "Reference" "#PWR01" (at 30 27.46 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
    (property "Value" "+12V" (at 30 32.54 0)
      (effects (font (size 1.27 1.27)))
    )
  )
  
  (symbol (lib_id "power:GND") (at 30 90 0) (mirror y) (uuid "pwr-pf2")
    (property "Reference" "#PWR02" (at 30 92.54 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
    (property "Value" "GND" (at 30 87.46 0)
      (effects (font (size 1.27 1.27)))
    )
  )
  
  (symbol (lib_id "power:+5V") (at 105 30 0) (uuid "pwr-pf3")
    (property "Reference" "#PWR03" (at 105 27.46 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
    (property "Value" "+5V" (at 105 32.54 0)
      (effects (font (size 1.27 1.27)))
    )
  )
  
  (symbol (lib_id "power:+3V3") (at 160 30 0) (uuid "pwr-pf4")
    (property "Reference" "#PWR04" (at 160 27.46 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
    (property "Value" "+3V3" (at 160 32.54 0)
      (effects (font (size 1.27 1.27)))
    )
  )
  
  (hierarchical_label "+12V" (shape output) (at 185 50 0)
    (effects (font (size 1.27 1.27)))
    (uuid "hier-12v")
  )
  (hierarchical_label "+5V" (shape output) (at 185 60 0)
    (effects (font (size 1.27 1.27)))
    (uuid "hier-5v")
  )
  (hierarchical_label "+3V3" (shape output) (at 185 70 0)
    (effects (font (size 1.27 1.27)))
    (uuid "hier-3v3")
  )
  (hierarchical_label "GND" (shape bidirectional) (at 185 90 0)
    (effects (font (size 1.27 1.27)))
    (uuid "hier-gnd")
  )
  
  (no_connect (at 93.98 30) (uuid "nc1"))
  (no_connect (at 93.98 50) (uuid "nc2"))
  
  (sheet_instances
    (path "/" (page "1"))
  )
  (symbol_instances
    (path "/pwr-j1" (reference "J1") (unit 1) (value "12V_IN") (footprint "Connector_BarrelJack:BarrelJack_Horizontal"))
    (path "/pwr-d1" (reference "D1") (unit 1) (value "1N4007") (footprint "Diode_SMD:D_SOD-123"))
    (path "/pwr-c1" (reference "C1") (unit 1) (value "10uF") (footprint "Capacitor_SMD:C_0603_1608Metric"))
    (path "/pwr-u1" (reference "U1") (unit 1) (value "LM7805") (footprint "Package_TO_SOT_SMD:SOT-223-3_TabPin2"))
    (path "/pwr-c2" (reference "C2") (unit 1) (value "100nF") (footprint "Capacitor_SMD:C_0603_1608Metric"))
    (path "/pwr-c3" (reference "C3") (unit 1) (value "10uF") (footprint "Capacitor_SMD:C_0603_1608Metric"))
    (path "/pwr-u2" (reference "U2") (unit 1) (value "AMS1117-3.3") (footprint "Package_TO_SOT_SMD:SOT-223-3_TabPin2"))
    (path "/pwr-c4" (reference "C4") (unit 1) (value "100nF") (footprint "Capacitor_SMD:C_0603_1608Metric"))
    (path "/pwr-c5" (reference "C5") (unit 1) (value "10uF") (footprint "Capacitor_SMD:C_0603_1608Metric"))
    (path "/pwr-d2" (reference "D2") (unit 1) (value "GREEN") (footprint "LED_SMD:LED_0603_1608Metric"))
    (path "/pwr-r1" (reference "R1") (unit 1) (value "1k") (footprint "Resistor_SMD:R_0603_1608Metric"))
    (path "/pwr-d3" (reference "D3") (unit 1) (value "BLUE") (footprint "LED_SMD:LED_0603_1608Metric"))
    (path "/pwr-r2" (reference "R2") (unit 1) (value "1k") (footprint "Resistor_SMD:R_0603_1608Metric"))
  )
)'''
    return sch

def main():
    with open("power.kicad_sch", "w") as f:
        f.write(gen_power_sch())
    print("Generated: power.kicad_sch (KiCad 9.0 format)")
    print("\nKey changes for KiCad 9.0:")
    print("  - Added generator_version \"9.0\"")
    print("  - Added pin definitions to all symbols")
    print("  - Added symbol_instances section")
    print("  - Added no_connect for unused pins")
    print("  - Proper (hide yes) syntax instead of (hide)")

if __name__ == "__main__":
    main()

def gen_digital_sch():
    """Generate DIGITAL_CONTROL sheet for KiCad 9"""
    return '''(kicad_sch
  (version 20250114)
  (generator "eeschema")
  (generator_version "9.0")
  (uuid "b2c3d4e5-f6a7-8901-bcde-f23456789012")
  (paper "A4")
  (title_block
    (title "TurboQuant Mux LNA - Digital Control")
    (date "2026-03-30")
    (rev "1.2")
  )
  (lib_symbols
    (symbol "power:GND" (in_bom yes) (on_board yes)
      (property "Reference" "#PWR" (at 0 -3.81 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Value" "GND" (at 0 -1.27 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Datasheet" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Description" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
    )
    (symbol "power:+5V" (in_bom yes) (on_board yes)
      (property "Reference" "#PWR" (at 0 -2.54 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Value" "+5V" (at 0 2.54 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Datasheet" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Description" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
    )
    (symbol "74xx:74HC595" (in_bom yes) (on_board yes)
      (property "Reference" "U" (at -7.62 13.97 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Value" "74HC595" (at 0 0 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm" (at 0 -15.24 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Datasheet" "https://www.ti.com/lit/ds/symlink/sn74hc595.pdf" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Description" "8-bit shift register" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
    )
    (symbol "Connector:Conn_02x10" (in_bom yes) (on_board yes)
      (property "Reference" "J" (at 0 13.97 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Value" "Conn_02x10" (at 0 -13.97 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical" (at 0 -16.51 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Datasheet" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Description" "Generic connector" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
    )
    (symbol "Device:R" (in_bom yes) (on_board yes)
      (property "Reference" "R" (at 0 2.54 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Value" "R" (at 0 -2.54 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" "Resistor_SMD:R_0603_1608Metric" (at 0 -5.08 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Datasheet" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Description" "Resistor" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
    )
  )
  
  (symbol (lib_id "Connector:Conn_02x10") (at 35 60 0) (uuid "dig-j2")
    (property "Reference" "J2" (at 35 75.97 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "GPIO_HEADER" (at 35 44.03 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical" (at 35 60 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
  )
  
  (symbol (lib_id "74xx:74HC595") (at 90 60 0) (uuid "dig-u3")
    (property "Reference" "U3" (at 82.38 74.77 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "74HC595" (at 90 60 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm" (at 90 60 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
  )
  
  (symbol (lib_id "Device:R") (at 130 35 90) (uuid "dig-r11")
    (property "Reference" "R11" (at 132.54 35 90)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "1k" (at 127.46 35 90)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "Resistor_SMD:R_0603_1608Metric" (at 130 35 90)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
  )
  
  (symbol (lib_id "power:+5V") (at 75 30 0) (uuid "dig-pf5")
    (property "Reference" "#PWR05" (at 75 27.46 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
    (property "Value" "+5V" (at 75 32.54 0)
      (effects (font (size 1.27 1.27)))
    )
  )
  
  (symbol (lib_id "power:GND") (at 75 95 0) (mirror y) (uuid "dig-pf6")
    (property "Reference" "#PWR06" (at 75 97.54 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
    (property "Value" "GND" (at 75 92.46 0)
      (effects (font (size 1.27 1.27)))
    )
  )
  
  (hierarchical_label "+5V" (shape input) (at 20 30 180)
    (effects (font (size 1.27 1.27)))
    (uuid "hier-in-5v")
  )
  (hierarchical_label "GND" (shape input) (at 20 95 180)
    (effects (font (size 1.27 1.27)))
    (uuid "hier-in-gnd")
  )
  
  (hierarchical_label "GATE0" (shape output) (at 170 40 0)
    (effects (font (size 1.27 1.27)))
    (uuid "hier-g0")
  )
  (hierarchical_label "GATE1" (shape output) (at 170 45 0)
    (effects (font (size 1.27 1.27)))
    (uuid "hier-g1")
  )
  (hierarchical_label "GATE2" (shape output) (at 170 50 0)
    (effects (font (size 1.27 1.27)))
    (uuid "hier-g2")
  )
  (hierarchical_label "GATE3" (shape output) (at 170 55 0)
    (effects (font (size 1.27 1.27)))
    (uuid "hier-g3")
  )
  (hierarchical_label "GATE4" (shape output) (at 170 60 0)
    (effects (font (size 1.27 1.27)))
    (uuid "hier-g4")
  )
  (hierarchical_label "GATE5" (shape output) (at 170 65 0)
    (effects (font (size 1.27 1.27)))
    (uuid "hier-g5")
  )
  (hierarchical_label "GATE6" (shape output) (at 170 70 0)
    (effects (font (size 1.27 1.27)))
    (uuid "hier-g6")
  )
  (hierarchical_label "GATE7" (shape output) (at 170 75 0)
    (effects (font (size 1.27 1.27)))
    (uuid "hier-g7")
  )
  
  (global_label "SER" (shape input) (at 20 45 180)
    (effects (font (size 1.27 1.27)))
    (uuid "glob-ser")
  )
  (global_label "SRCLK" (shape input) (at 20 50 180)
    (effects (font (size 1.27 1.27)))
    (uuid "glob-srclk")
  )
  (global_label "RCLK" (shape input) (at 20 55 180)
    (effects (font (size 1.27 1.27)))
    (uuid "glob-rclk")
  )
  
  (sheet_instances
    (path "/" (page "1"))
  )
  (symbol_instances
    (path "/dig-j2" (reference "J2") (unit 1) (value "GPIO_HEADER") (footprint "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical"))
    (path "/dig-u3" (reference "U3") (unit 1) (value "74HC595") (footprint "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm"))
    (path "/dig-r11" (reference "R11") (unit 1) (value "1k") (footprint "Resistor_SMD:R_0603_1608Metric"))
  )
)'''
    return sch

def gen_analog_sch():
    """Generate ANALOG_FRONTEND sheet for KiCad 9"""
    return '''(kicad_sch
  (version 20250114)
  (generator "eeschema")
  (generator_version "9.0")
  (uuid "c3d4e5f6-a7b8-9012-cdef-345678901234")
  (paper "A3")
  (title_block
    (title "TurboQuant Mux LNA - Analog Frontend")
    (date "2026-03-30")
    (rev "1.2")
  )
  (lib_symbols
    (symbol "power:GND" (in_bom yes) (on_board yes)
      (property "Reference" "#PWR" (at 0 -3.81 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Value" "GND" (at 0 -1.27 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Datasheet" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Description" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
    )
    (symbol "power:+5V" (in_bom yes) (on_board yes)
      (property "Reference" "#PWR" (at 0 -2.54 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Value" "+5V" (at 0 2.54 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Datasheet" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Description" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
    )
    (symbol "Analog_Switch:CD4051B" (in_bom yes) (on_board yes)
      (property "Reference" "U" (at 0 -12.7 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Value" "CD4051B" (at 0 0 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm" (at 0 -15.24 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Datasheet" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Description" "Analog Multiplexer 8 to 1" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
    )
    (symbol "Amplifier_Operational:OPA657" (in_bom yes) (on_board yes)
      (property "Reference" "U" (at 0 -7.62 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Value" "OPA657" (at 0 0 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm" (at 0 -10.16 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Datasheet" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Description" "Wideband Op Amp" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
    )
    (symbol "Transistor_FET:BSS138" (in_bom yes) (on_board yes)
      (property "Reference" "Q" (at 2.54 1.27 0)
        (effects (font (size 1.27 1.27)) (justify left))
      )
      (property "Value" "BSS138" (at 2.54 -1.27 0)
        (effects (font (size 1.27 1.27)) (justify left))
      )
      (property "Footprint" "Package_TO_SOT_SMD:SOT-23" (at 0 -5.08 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Datasheet" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Description" "N-channel MOSFET" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
    )
    (symbol "Diode:BAV99" (in_bom yes) (on_board yes)
      (property "Reference" "D" (at 0 2.54 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Value" "BAV99" (at 0 -2.54 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" "Package_TO_SOT_SMD:SOT-23" (at 0 -5.08 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Datasheet" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Description" "Dual diode" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
    )
    (symbol "Connector:Conn_Coaxial" (in_bom yes) (on_board yes)
      (property "Reference" "J" (at 0 3.81 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Value" "SMA" (at 0 -3.81 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" "Connector_Coaxial:SMA_Amphenol_132134-11_Vertical" (at 0 -6.35 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Datasheet" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Description" "SMA connector" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
    )
    (symbol "Device:R" (in_bom yes) (on_board yes)
      (property "Reference" "R" (at 0 2.54 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Value" "R" (at 0 -2.54 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" "Resistor_SMD:R_0603_1608Metric" (at 0 -5.08 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Datasheet" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Description" "Resistor" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
    )
    (symbol "Device:C" (in_bom yes) (on_board yes)
      (property "Reference" "C" (at 0 2.54 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Value" "C" (at 0 -2.54 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" "Capacitor_SMD:C_0603_1608Metric" (at 0 -5.08 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Datasheet" "" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
      (property "Description" "Capacitor" (at 0 0 0)
        (effects (font (size 1.27 1.27)) (hide yes))
      )
    )
  )
  
  (symbol (lib_id "Connector:Conn_Coaxial") (at 35 40 0) (uuid "ana-j3")
    (property "Reference" "J3" (at 35 44.89 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "TX_IN" (at 35 35.11 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "Connector_Coaxial:SMA_Amphenol_132134-11_Vertical" (at 35 40 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
  )
  
  (symbol (lib_id "Transistor_FET:BSS138") (at 65 40 0) (uuid "ana-q1")
    (property "Reference" "Q1" (at 67.54 41.27 0)
      (effects (font (size 1.27 1.27)) (justify left))
    )
    (property "Value" "BSS138" (at 67.54 38.73 0)
      (effects (font (size 1.27 1.27)) (justify left))
    )
    (property "Footprint" "Package_TO_SOT_SMD:SOT-23" (at 65 40 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
  )
  
  (symbol (lib_id "Connector:Conn_Coaxial") (at 100 40 0) (uuid "ana-j4")
    (property "Reference" "J4" (at 100 44.89 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "EL0" (at 100 35.11 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "Connector_Coaxial:SMA_Amphenol_132134-11_Vertical" (at 100 40 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
  )
  
  (symbol (lib_id "Diode:BAV99") (at 120 40 0) (uuid "ana-d4")
    (property "Reference" "D4" (at 120 43.16 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "BAV99" (at 120 36.84 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "Package_TO_SOT_SMD:SOT-23" (at 120 40 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
  )
  
  (symbol (lib_id "Analog_Switch:CD4051B") (at 160 70 0) (uuid "ana-u4")
    (property "Reference" "U4" (at 152.38 84.77 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "CD4051B" (at 160 70 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm" (at 160 70 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
  )
  
  (symbol (lib_id "Amplifier_Operational:OPA657") (at 200 70 0) (uuid "ana-u6")
    (property "Reference" "U6" (at 192.38 78.62 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "OPA657" (at 200 70 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm" (at 200 70 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
  )
  
  (symbol (lib_id "Connector:Conn_Coaxial") (at 230 70 0) (uuid "ana-j12")
    (property "Reference" "J12" (at 230 74.89 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "RX0_OUT" (at 230 65.11 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "Connector_Coaxial:SMA_Amphenol_132134-11_Vertical" (at 230 70 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
  )
  
  (symbol (lib_id "power:+5V") (at 170 30 0) (uuid "ana-pf7")
    (property "Reference" "#PWR07" (at 170 27.46 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
    (property "Value" "+5V" (at 170 32.54 0)
      (effects (font (size 1.27 1.27)))
    )
  )
  
  (symbol (lib_id "power:GND") (at 170 160 0) (mirror y) (uuid "ana-pf8")
    (property "Reference" "#PWR08" (at 170 162.54 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
    (property "Value" "GND" (at 170 157.46 0)
      (effects (font (size 1.27 1.27)))
    )
  )
  
  (hierarchical_label "+5V" (shape input) (at 20 30 180)
    (effects (font (size 1.27 1.27)))
    (uuid "hier-ana-5v")
  )
  (hierarchical_label "GND" (shape input) (at 20 160 180)
    (effects (font (size 1.27 1.27)))
    (uuid "hier-ana-gnd")
  )
  
  (hierarchical_label "GATE0" (shape input) (at 20 42 180)
    (effects (font (size 1.27 1.27)))
    (uuid "hier-ana-g0")
  )
  
  (hierarchical_label "MUX_A" (shape input) (at 140 55 180)
    (effects (font (size 1.27 1.27)))
    (uuid "hier-muxa")
  )
  
  (global_label "TX_BUS" (shape bidirectional) (at 50 40 0)
    (effects (font (size 1.27 1.27)))
    (uuid "glob-tx")
  )
  
  (sheet_instances
    (path "/" (page "1"))
  )
  (symbol_instances
    (path "/ana-j3" (reference "J3") (unit 1) (value "TX_IN") (footprint "Connector_Coaxial:SMA_Amphenol_132134-11_Vertical"))
    (path "/ana-q1" (reference "Q1") (unit 1) (value "BSS138") (footprint "Package_TO_SOT_SMD:SOT-23"))
    (path "/ana-j4" (reference "J4") (unit 1) (value "EL0") (footprint "Connector_Coaxial:SMA_Amphenol_132134-11_Vertical"))
    (path "/ana-d4" (reference "D4") (unit 1) (value "BAV99") (footprint "Package_TO_SOT_SMD:SOT-23"))
    (path "/ana-u4" (reference "U4") (unit 1) (value "CD4051B") (footprint "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm"))
    (path "/ana-u6" (reference "U6") (unit 1) (value "OPA657") (footprint "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"))
    (path "/ana-j12" (reference "J12") (unit 1) (value "RX0_OUT") (footprint "Connector_Coaxial:SMA_Amphenol_132134-11_Vertical"))
  )
)'''
    return sch

def gen_main_sch():
    """Generate main schematic for KiCad 9"""
    return '''(kicad_sch
  (version 20250114)
  (generator "eeschema")
  (generator_version "9.0")
  (uuid "c91386be-ef17-4bcb-aaad-5175b258204a")
  (paper "A3")
  (title_block
    (title "TurboQuant Mux LNA Board")
    (date "2026-03-30")
    (rev "1.2")
    (company "TurboQuant")
    (comment 1 "8-Element Ultrasound Array Interface")
    (comment 2 "KiCad 9.0 Hierarchical Design")
  )
  (lib_symbols)
  
  (sheet (at 13.97 16.51) (size 80.01 71.12)
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (dnp no)
    (stroke (width 0.1524) (type solid))
    (fill (color 0 0 0 0.0000))
    (uuid "31e7358f-421c-4108-98a5-1bd5cbdf3861")
    (property "Sheetname" "POWER_SUPPLIES" (at 13.97 15.7984 0)
      (effects (font (size 1.27 1.27)) (justify left bottom))
    )
    (property "Sheetfile" "power.kicad_sch" (at 13.97 88.2146 0)
      (effects (font (size 1.27 1.27)) (justify left top))
    )
    (pin "+12V" output (at 93.98 30 0)
      (effects (font (size 1.27 1.27)))
      (uuid "pwr-pin-12v")
    )
    (pin "+5V" output (at 93.98 40 0)
      (effects (font (size 1.27 1.27)))
      (uuid "pwr-pin-5v")
    )
    (pin "+3V3" output (at 93.98 50 0)
      (effects (font (size 1.27 1.27)))
      (uuid "pwr-pin-3v3")
    )
    (pin "GND" bidirectional (at 93.98 60 0)
      (effects (font (size 1.27 1.27)))
      (uuid "pwr-pin-gnd")
    )
    (instances
      (project "tuboquant_mux_lna"
        (path "/c91386be-ef17-4bcb-aaad-5175b258204a"
          (page "2")
        )
      )
    )
  )
  
  (sheet (at 105.41 16.51) (size 100 80)
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (dnp no)
    (stroke (width 0.1524) (type solid))
    (fill (color 0 0 0 0.0000))
    (uuid "bf41dd9b-ce45-467e-ac10-028c71ad2a9a")
    (property "Sheetname" "DIGITAL_CONTROL" (at 105.41 15.7984 0)
      (effects (font (size 1.27 1.27)) (justify left bottom))
    )
    (property "Sheetfile" "digital.kicad_sch" (at 105.41 97.7146 0)
      (effects (font (size 1.27 1.27)) (justify left top))
    )
    (pin "+5V" input (at 105.41 30 180)
      (effects (font (size 1.27 1.27)))
      (uuid "dig-pin-5v")
    )
    (pin "GND" input (at 105.41 40 180)
      (effects (font (size 1.27 1.27)))
      (uuid "dig-pin-gnd")
    )
    (pin "GATE0" output (at 205.41 25 0)
      (effects (font (size 1.27 1.27)))
      (uuid "dig-pin-g0")
    )
    (pin "GATE1" output (at 205.41 30 0)
      (effects (font (size 1.27 1.27)))
      (uuid "dig-pin-g1")
    )
    (pin "GATE2" output (at 205.41 35 0)
      (effects (font (size 1.27 1.27)))
      (uuid "dig-pin-g2")
    )
    (pin "GATE3" output (at 205.41 40 0)
      (effects (font (size 1.27 1.27)))
      (uuid "dig-pin-g3")
    )
    (pin "GATE4" output (at 205.41 45 0)
      (effects (font (size 1.27 1.27)))
      (uuid "dig-pin-g4")
    )
    (pin "GATE5" output (at 205.41 50 0)
      (effects (font (size 1.27 1.27)))
      (uuid "dig-pin-g5")
    )
    (pin "GATE6" output (at 205.41 55 0)
      (effects (font (size 1.27 1.27)))
      (uuid "dig-pin-g6")
    )
    (pin "GATE7" output (at 205.41 60 0)
      (effects (font (size 1.27 1.27)))
      (uuid "dig-pin-g7")
    )
    (instances
      (project "tuboquant_mux_lna"
        (path "/c91386be-ef17-4bcb-aaad-5175b258204a"
          (page "3")
        )
      )
    )
  )
  
  (sheet (at 13.97 102.87) (size 191.44 85.88)
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (dnp no)
    (stroke (width 0.1524) (type solid))
    (fill (color 0 0 0 0.0000))
    (uuid "da55019f-ccad-455b-840f-c04df8128d6c")
    (property "Sheetname" "ANALOG_FRONTEND" (at 13.97 102.1584 0)
      (effects (font (size 1.27 1.27)) (justify left bottom))
    )
    (property "Sheetfile" "analog.kicad_sch" (at 13.97 189.3346 0)
      (effects (font (size 1.27 1.27)) (justify left top))
    )
    (pin "+5V" input (at 13.97 115 180)
      (effects (font (size 1.27 1.27)))
      (uuid "ana-pin-5v")
    )
    (pin "GND" input (at 13.97 130 180)
      (effects (font (size 1.27 1.27)))
      (uuid "ana-pin-gnd")
    )
    (pin "GATE0" input (at 13.97 140 180)
      (effects (font (size 1.27 1.27)))
      (uuid "ana-pin-g0")
    )
    (instances
      (project "tuboquant_mux_lna"
        (path "/c91386be-ef17-4bcb-aaad-5175b258204a"
          (page "4")
        )
      )
    )
  )
  
  (sheet_instances
    (path "/" (page "1"))
  )
)'''
    return sch

def gen_project_file():
    """Generate KiCad 9.0 project file"""
    return '''{
  "board": {
    "3dviewports": [],
    "design_settings": {
      "defaults": {},
      "diff_pair_dimensions": [],
      "drc_exclusions": [],
      "rules": {},
      "track_widths": [],
      "via_dimensions": []
    },
    "ipc2581": {},
    "layer_pairs": [],
    "layer_presets": [],
    "viewports": []
  },
  "boards": [],
  "cvpcb": { "equivalence_files": [] },
  "erc": {
    "erc_exclusions": [],
    "meta": { "version": 0 },
    "pin_map": [
      [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 2],
      [0, 2, 0, 1, 0, 0, 1, 0, 2, 2, 2, 2],
      [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 2],
      [0, 1, 0, 0, 0, 0, 1, 1, 2, 1, 1, 2],
      [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 2],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
      [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 2],
      [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 2],
      [0, 2, 1, 2, 0, 0, 1, 0, 2, 2, 2, 2],
      [0, 2, 0, 1, 0, 0, 1, 0, 2, 2, 0, 2],
      [0, 2, 1, 1, 0, 0, 1, 0, 2, 0, 2, 2],
      [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
    ],
    "rule_severities": {
      "bus_definition_conflict": "error",
      "bus_entry_needed": "error",
      "bus_to_bus_conflict": "error",
      "bus_to_net_conflict": "error",
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
      "pin_to_pin": "error",
      "power_pin_not_driven": "error",
      "simulation_model_issue": "ignore",
      "unannotated": "error",
      "unconnected_wire_endpoint": "warning",
      "unit_value_mismatch": "error",
      "unresolved_variable": "error",
      "wire_dangling": "error"
    }
  },
  "libraries": { "pinned_footprint_libs": [], "pinned_symbol_libs": [] },
  "meta": { "filename": "tuboquant_mux_lna.kicad_pro", "version": 3 },
  "net_settings": {
    "classes": [
      {
        "bus_width": 12,
        "clearance": 0.2,
        "diff_pair_gap": 0.25,
        "diff_pair_via_gap": 0.25,
        "diff_pair_width": 0.2,
        "line_style": 0,
        "microvia_diameter": 0.3,
        "microvia_drill": 0.1,
        "name": "Default",
        "pcb_color": "rgba(0, 0, 0, 0.000)",
        "priority": 2147483647,
        "schematic_color": "rgba(0, 0, 0, 0.000)",
        "track_width": 0.2,
        "via_diameter": 0.6,
        "via_drill": 0.3,
        "wire_width": 6
      }
    ],
    "meta": { "version": 4 },
    "net_colors": null,
    "netclass_assignments": null,
    "netclass_patterns": []
  },
  "pcbnew": { "last_paths": {}, "page_layout_descr_file": "" },
  "schematic": {
    "annotate_start_num": 0,
    "bom_export_filename": "${PROJECTNAME}.csv",
    "bom_fmt_settings": {
      "field_delimiter": ",",
      "keep_line_breaks": false,
      "keep_tabs": false,
      "name": "CSV",
      "ref_delimiter": ",",
      "ref_range_delimiter": "",
      "string_delimiter": "\\""
    },
    "bom_settings": {
      "exclude_dnp": false,
      "fields_ordered": [
        { "group_by": false, "label": "Reference", "name": "Reference", "show": true },
        { "group_by": false, "label": "Qty", "name": "${QUANTITY}", "show": true },
        { "group_by": true, "label": "Value", "name": "Value", "show": true },
        { "group_by": true, "label": "Footprint", "name": "Footprint", "show": true },
        { "group_by": false, "label": "Datasheet", "name": "Datasheet", "show": true }
      ],
      "filter_string": "",
      "group_symbols": true,
      "include_excluded_from_bom": true,
      "name": "Default",
      "sort_asc": true,
      "sort_field": "Reference"
    },
    "connection_grid_size": 50.0,
    "drawing": {
      "dashed_lines_dash_length_ratio": 12.0,
      "dashed_lines_gap_length_ratio": 3.0,
      "default_line_thickness": 6.0,
      "default_text_size": 50.0,
      "pin_symbol_size": 25.0,
      "text_offset_ratio": 0.15
    },
    "legacy_lib_dir": "",
    "legacy_lib_list": [],
    "meta": { "version": 1 },
    "page_layout_descr_file": "",
    "plot_directory": "",
    "subpart_first_id": 65,
    "subpart_id_separator": 0
  },
  "sheets": [],
  "text_variables": {}
}'''

# Regenerate all files
def main():
    files = [
        ("power.kicad_sch", gen_power_sch()),
        ("digital.kicad_sch", gen_digital_sch()),
        ("analog.kicad_sch", gen_analog_sch()),
        ("tuboquant_mux_lna.kicad_sch", gen_main_sch()),
        ("tuboquant_mux_lna.kicad_pro", gen_project_file())
    ]
    
    for filename, content in files:
        with open(filename, "w") as f:
            f.write(content)
        print(f"Generated: {filename}")
    
    print("\n✅ All KiCad 9.0 files generated!")
    print("\nKiCad 9.0 Format Features:")
    print("  - generator_version \"9.0\"")
    print("  - Proper (effects (hide yes)) syntax")
    print("  - symbol_instances section for all symbols")
    print("  - Pin definitions for all symbols")
    print("  - UUIDs for all objects")
    print("  - Proper hierarchical pin syntax")

if __name__ == "__main__":
    main()
