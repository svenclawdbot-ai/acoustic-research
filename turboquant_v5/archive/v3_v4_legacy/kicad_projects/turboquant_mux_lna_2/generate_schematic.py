#!/usr/bin/env python3
"""
Generate TurboQuant Mux LNA Board Schematics
Hierarchical design with Power, Digital, and Analog sheets
"""
import uuid

def uid():
    return str(uuid.uuid4())

def gen_power_sch():
    """Generate POWER_SUPPLIES sheet"""
    sch = '''(kicad_sch
  (version 20231120)
  (generator "eeschema")
  (uuid "a1b2c3d4-e5f6-7890-abcd-ef1234567890")
  (paper "A4")
  (title_block
    (title "TurboQuant Mux LNA - Power Supplies")
    (date "2026-03-30")
    (rev "1.0")
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
  
  (symbol (lib_id "Connector:Barrel_Jack") (at 20 40 0) (uuid "pwr-j1")
    (property "Reference" "J1" (at 20 46.48 0) (effects (font (size 1.27 1.27))))
    (property "Value" "12V_IN" (at 20 33.52 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Connector_BarrelJack:BarrelJack_Horizontal" (at 20 40 0) (effects hide))
  )
  
  (symbol (lib_id "Diode:1N4007") (at 35 40 0) (uuid "pwr-d1")
    (property "Reference" "D1" (at 35 43.16 0) (effects (font (size 1.27 1.27))))
    (property "Value" "1N4007" (at 35 36.84 0) (effects (font (size 1.27 1.27))))
  )
  
  (symbol (lib_id "Device:C") (at 35 55 0) (uuid "pwr-c1")
    (property "Reference" "C1" (at 37.54 55 0) (effects (font (size 1.27 1.27))))
    (property "Value" "10uF" (at 32.46 55 0) (effects (font (size 1.27 1.27))))
  )
  
  (symbol (lib_id "Regulator_Linear:LM7805") (at 60 40 0) (uuid "pwr-u1")
    (property "Reference" "U1" (at 60 46.48 0) (effects (font (size 1.27 1.27))))
    (property "Value" "LM7805" (at 60 33.52 0) (effects (font (size 1.27 1.27))))
  )
  
  (symbol (lib_id "Device:C") (at 50 55 0) (uuid "pwr-c2")
    (property "Reference" "C2" (at 52.54 55 0) (effects (font (size 1.27 1.27))))
    (property "Value" "100nF" (at 47.46 55 0) (effects (font (size 1.27 1.27))))
  )
  
  (symbol (lib_id "Device:C") (at 70 55 0) (uuid "pwr-c3")
    (property "Reference" "C3" (at 72.54 55 0) (effects (font (size 1.27 1.27))))
    (property "Value" "10uF" (at 67.46 55 0) (effects (font (size 1.27 1.27))))
  )
  
  (symbol (lib_id "Regulator_Linear:AMS1117-3.3") (at 100 40 0) (uuid "pwr-u2")
    (property "Reference" "U2" (at 100 46.48 0) (effects (font (size 1.27 1.27))))
    (property "Value" "AMS1117-3.3" (at 100 33.52 0) (effects (font (size 1.27 1.27))))
  )
  
  (symbol (lib_id "Device:C") (at 90 55 0) (uuid "pwr-c4")
    (property "Reference" "C4" (at 92.54 55 0) (effects (font (size 1.27 1.27))))
    (property "Value" "100nF" (at 87.46 55 0) (effects (font (size 1.27 1.27))))
  )
  
  (symbol (lib_id "Device:C") (at 110 55 0) (uuid "pwr-c5")
    (property "Reference" "C5" (at 112.54 55 0) (effects (font (size 1.27 1.27))))
    (property "Value" "10uF" (at 107.46 55 0) (effects (font (size 1.27 1.27))))
  )
  
  (symbol (lib_id "Device:LED") (at 80 70 0) (uuid "pwr-d2")
    (property "Reference" "D2" (at 80 73.16 0) (effects (font (size 1.27 1.27))))
    (property "Value" "GREEN" (at 80 66.84 0) (effects (font (size 1.27 1.27))))
  )
  
  (symbol (lib_id "Device:R") (at 70 70 0) (uuid "pwr-r1")
    (property "Reference" "R1" (at 67.46 70 0) (effects (font (size 1.27 1.27))))
    (property "Value" "1k" (at 72.54 70 0) (effects (font (size 1.27 1.27))))
  )
  
  (symbol (lib_id "Device:LED") (at 120 70 0) (uuid "pwr-d3")
    (property "Reference" "D3" (at 120 73.16 0) (effects (font (size 1.27 1.27))))
    (property "Value" "BLUE" (at 120 66.84 0) (effects (font (size 1.27 1.27))))
  )
  
  (symbol (lib_id "Device:R") (at 110 70 0) (uuid "pwr-r2")
    (property "Reference" "R2" (at 107.46 70 0) (effects (font (size 1.27 1.27))))
    (property "Value" "1k" (at 112.54 70 0) (effects (font (size 1.27 1.27))))
  )
  
  (symbol (lib_id "power:+12V") (at 20 25 0) (uuid "pwr-pf1")
    (property "Reference" "#PWR01" (at 20 22.46 0) (effects hide))
    (property "Value" "+12V" (at 20 27.54 0) (effects (font (size 1.27 1.27))))
  )
  
  (symbol (lib_id "power:GND") (at 20 65 0) (mirror y) (uuid "pwr-pf2")
    (property "Reference" "#PWR02" (at 20 67.54 0) (effects hide))
    (property "Value" "GND" (at 20 62.46 0) (effects (font (size 1.27 1.27))))
  )
  
  (symbol (lib_id "power:+5V") (at 70 25 0) (uuid "pwr-pf3")
    (property "Reference" "#PWR03" (at 70 22.46 0) (effects hide))
    (property "Value" "+5V" (at 70 27.54 0) (effects (font (size 1.27 1.27))))
  )
  
  (symbol (lib_id "power:+3V3") (at 110 25 0) (uuid "pwr-pf4")
    (property "Reference" "#PWR04" (at 110 22.46 0) (effects hide))
    (property "Value" "+3V3" (at 110 27.54 0) (effects (font (size 1.27 1.27))))
  )
  
  (global_label "+12V" (shape passive) (at 130 40 0) (effects (font (size 1.27 1.27))))
  (global_label "+5V" (shape passive) (at 130 50 0) (effects (font (size 1.27 1.27))))
  (global_label "+3V3" (shape passive) (at 130 60 0) (effects (font (size 1.27 1.27))))
  (global_label "GND" (shape passive) (at 130 65 0) (effects (font (size 1.27 1.27))))
  
  (wire (pts (xy 20 25) (xy 20 33.52)) (stroke (width 0) (type default)))
  (wire (pts (xy 25.08 40) (xy 31.92 40)) (stroke (width 0) (type default)))
  (wire (pts (xy 38.08 40) (xy 55.92 40)) (stroke (width 0) (type default)))
  (wire (pts (xy 64.08 40) (xy 85.92 40)) (stroke (width 0) (type default)))
  (wire (pts (xy 94.08 40) (xy 105.92 40)) (stroke (width 0) (type default)))
  (wire (pts (xy 114.08 40) (xy 130 40)) (stroke (width 0) (type default)))
  
  (wire (pts (xy 20 65) (xy 20 46.48)) (stroke (width 0) (type default)))
  (wire (pts (xy 60 35.56) (xy 60 30)) (stroke (width 0) (type default)))
  (wire (pts (xy 100 35.56) (xy 100 30)) (stroke (width 0) (type default)))
  
  (junction (at 60 30) (diameter 0))
  (junction (at 100 30) (diameter 0))
  
  (sheet_instances (path "/" (page "1")))
)'''
    return sch

def gen_digital_sch():
    """Generate DIGITAL_CONTROL sheet"""
    sch = '''(kicad_sch
  (version 20231120)
  (generator "eeschema")
  (uuid "b2c3d4e5-f6a7-8901-bcde-f23456789012")
  (paper "A4")
  (title_block
    (title "TurboQuant Mux LNA - Digital Control")
    (date "2026-03-30")
    (rev "1.0")
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
  
  (symbol (lib_id "Connector:Conn_02x10") (at 25 50 0) (uuid "dig-j1")
    (property "Reference" "J2" (at 25 65.97 0) (effects (font (size 1.27 1.27))))
    (property "Value" "GPIO_HEADER" (at 25 34.03 0) (effects (font (size 1.27 1.27))))
  )
  
  (symbol (lib_id "74xx:74HC595") (at 70 50 0) (uuid "dig-u1")
    (property "Reference" "U3" (at 62.38 64.77 0) (effects (font (size 1.27 1.27))))
    (property "Value" "74HC595" (at 70 50 0) (effects (font (size 1.27 1.27))))
  )
  
  (symbol (lib_id "Device:R") (at 100 30 90) (uuid "dig-r3")
    (property "Reference" "R3" (at 102.54 30 90) (effects (font (size 1.27 1.27))))
    (property "Value" "1k" (at 97.46 30 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 105 30 90) (uuid "dig-r4")
    (property "Reference" "R4" (at 107.54 30 90) (effects (font (size 1.27 1.27))))
    (property "Value" "1k" (at 102.46 30 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 110 30 90) (uuid "dig-r5")
    (property "Reference" "R5" (at 112.54 30 90) (effects (font (size 1.27 1.27))))
    (property "Value" "1k" (at 107.46 30 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 115 30 90) (uuid "dig-r6")
    (property "Reference" "R6" (at 117.54 30 90) (effects (font (size 1.27 1.27))))
    (property "Value" "1k" (at 112.46 30 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 120 30 90) (uuid "dig-r7")
    (property "Reference" "R7" (at 122.54 30 90) (effects (font (size 1.27 1.27))))
    (property "Value" "1k" (at 117.46 30 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 125 30 90) (uuid "dig-r8")
    (property "Reference" "R8" (at 127.54 30 90) (effects (font (size 1.27 1.27))))
    (property "Value" "1k" (at 122.46 30 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 130 30 90) (uuid "dig-r9")
    (property "Reference" "R9" (at 132.54 30 90) (effects (font (size 1.27 1.27))))
    (property "Value" "1k" (at 127.46 30 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 135 30 90) (uuid "dig-r10")
    (property "Reference" "R10" (at 137.54 30 90) (effects (font (size 1.27 1.27))))
    (property "Value" "1k" (at 132.46 30 90) (effects (font (size 1.27 1.27))))
  )
  
  (symbol (lib_id "power:+5V") (at 60 30 0) (uuid "dig-pf1")
    (property "Reference" "#PWR05" (at 60 27.46 0) (effects hide))
    (property "Value" "+5V" (at 60 32.54 0) (effects (font (size 1.27 1.27))))
  )
  
  (symbol (lib_id "power:GND") (at 60 75 0) (mirror y) (uuid "dig-pf2")
    (property "Reference" "#PWR06" (at 60 77.54 0) (effects hide))
    (property "Value" "GND" (at 60 72.46 0) (effects (font (size 1.27 1.27))))
  )
  
  (global_label "SER" (shape input) (at 15 40 180) (effects (font (size 1.27 1.27))))
  (global_label "SRCLK" (shape input) (at 15 45 180) (effects (font (size 1.27 1.27))))
  (global_label "RCLK" (shape input) (at 15 50 180) (effects (font (size 1.27 1.27))))
  (global_label "MUX_A" (shape input) (at 15 55 180) (effects (font (size 1.27 1.27))))
  (global_label "MUX_B" (shape input) (at 15 60 180) (effects (font (size 1.27 1.27))))
  (global_label "MUX_C" (shape input) (at 15 65 180) (effects (font (size 1.27 1.27))))
  (global_label "+5V" (shape passive) (at 45 25 0) (effects (font (size 1.27 1.27))))
  (global_label "GND" (shape passive) (at 45 80 0) (effects (font (size 1.27 1.27))))
  (global_label "GATE0" (shape output) (at 145 35 0) (effects (font (size 1.27 1.27))))
  (global_label "GATE1" (shape output) (at 145 40 0) (effects (font (size 1.27 1.27))))
  (global_label "GATE2" (shape output) (at 145 45 0) (effects (font (size 1.27 1.27))))
  (global_label "GATE3" (shape output) (at 145 50 0) (effects (font (size 1.27 1.27))))
  (global_label "GATE4" (shape output) (at 145 55 0) (effects (font (size 1.27 1.27))))
  (global_label "GATE5" (shape output) (at 145 60 0) (effects (font (size 1.27 1.27))))
  (global_label "GATE6" (shape output) (at 145 65 0) (effects (font (size 1.27 1.27))))
  (global_label "GATE7" (shape output) (at 145 70 0) (effects (font (size 1.27 1.27))))
  
  (sheet_instances (path "/" (page "1")))
)'''
    return sch

def main():
    # Generate power sheet
    power = gen_power_sch()
    with open("power.kicad_sch", "w") as f:
        f.write(power)
    print("Generated: power.kicad_sch")
    
    # Generate digital sheet
    digital = gen_digital_sch()
    with open("digital.kicad_sch", "w") as f:
        f.write(digital)
    print("Generated: digital.kicad_sch")
    
    print("\n✅ Power and Digital sheets generated!")

if __name__ == "__main__":
    main()

def gen_analog_sch():
    """Generate ANALOG_FRONTEND sheet - Mux and LNA section"""
    sch = '''(kicad_sch
  (version 20231120)
  (generator "eeschema")
  (uuid "c3d4e5f6-a7b8-9012-cdef-345678901234")
  (paper "A3")
  (title_block
    (title "TurboQuant Mux LNA - Analog Frontend")
    (date "2026-03-30")
    (rev "1.0")
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
  
  (symbol (lib_id "Connector:Conn_Coaxial") (at 25 30 0) (uuid "ana-j3")
    (property "Reference" "J3" (at 25 34.89 0) (effects (font (size 1.27 1.27))))
    (property "Value" "TX_IN" (at 25 25.11 0) (effects (font (size 1.27 1.27))))
  )
  
  (symbol (lib_id "Transistor_FET:BSS138") (at 50 30 0) (uuid "ana-q1")
    (property "Reference" "Q1" (at 52.54 31.27 0) (effects (font (size 1.27 1.27)) (justify left)))
    (property "Value" "BSS138" (at 52.54 28.73 0) (effects (font (size 1.27 1.27)) (justify left)))
  )
  (symbol (lib_id "Transistor_FET:BSS138") (at 50 40 0) (uuid "ana-q2")
    (property "Reference" "Q2" (at 52.54 41.27 0) (effects (font (size 1.27 1.27)) (justify left)))
    (property "Value" "BSS138" (at 52.54 38.73 0) (effects (font (size 1.27 1.27)) (justify left)))
  )
  (symbol (lib_id "Transistor_FET:BSS138") (at 50 50 0) (uuid "ana-q3")
    (property "Reference" "Q3" (at 52.54 51.27 0) (effects (font (size 1.27 1.27)) (justify left)))
    (property "Value" "BSS138" (at 52.54 48.73 0) (effects (font (size 1.27 1.27)) (justify left)))
  )
  (symbol (lib_id "Transistor_FET:BSS138") (at 50 60 0) (uuid "ana-q4")
    (property "Reference" "Q4" (at 52.54 61.27 0) (effects (font (size 1.27 1.27)) (justify left)))
    (property "Value" "BSS138" (at 52.54 58.73 0) (effects (font (size 1.27 1.27)) (justify left)))
  )
  (symbol (lib_id "Transistor_FET:BSS138") (at 50 70 0) (uuid "ana-q5")
    (property "Reference" "Q5" (at 52.54 71.27 0) (effects (font (size 1.27 1.27)) (justify left)))
    (property "Value" "BSS138" (at 52.54 68.73 0) (effects (font (size 1.27 1.27)) (justify left)))
  )
  (symbol (lib_id "Transistor_FET:BSS138") (at 50 80 0) (uuid "ana-q6")
    (property "Reference" "Q6" (at 52.54 81.27 0) (effects (font (size 1.27 1.27)) (justify left)))
    (property "Value" "BSS138" (at 52.54 78.73 0) (effects (font (size 1.27 1.27)) (justify left)))
  )
  (symbol (lib_id "Transistor_FET:BSS138") (at 50 90 0) (uuid "ana-q7")
    (property "Reference" "Q7" (at 52.54 91.27 0) (effects (font (size 1.27 1.27)) (justify left)))
    (property "Value" "BSS138" (at 52.54 88.73 0) (effects (font (size 1.27 1.27)) (justify left)))
  )
  (symbol (lib_id "Transistor_FET:BSS138") (at 50 100 0) (uuid "ana-q8")
    (property "Reference" "Q8" (at 52.54 101.27 0) (effects (font (size 1.27 1.27)) (justify left)))
    (property "Value" "BSS138" (at 52.54 98.73 0) (effects (font (size 1.27 1.27)) (justify left)))
  )
  
  (symbol (lib_id "Device:R") (at 60 30 90) (uuid "ana-rs1")
    (property "Reference" "RS1" (at 62.54 30 90) (effects (font (size 1.27 1.27))))
    (property "Value" "100" (at 57.46 30 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 60 40 90) (uuid "ana-rs2")
    (property "Reference" "RS2" (at 62.54 40 90) (effects (font (size 1.27 1.27))))
    (property "Value" "100" (at 57.46 40 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 60 50 90) (uuid "ana-rs3")
    (property "Reference" "RS3" (at 62.54 50 90) (effects (font (size 1.27 1.27))))
    (property "Value" "100" (at 57.46 50 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 60 60 90) (uuid "ana-rs4")
    (property "Reference" "RS4" (at 62.54 60 90) (effects (font (size 1.27 1.27))))
    (property "Value" "100" (at 57.46 60 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 60 70 90) (uuid "ana-rs5")
    (property "Reference" "RS5" (at 62.54 70 90) (effects (font (size 1.27 1.27))))
    (property "Value" "100" (at 57.46 70 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 60 80 90) (uuid "ana-rs6")
    (property "Reference" "RS6" (at 62.54 80 90) (effects (font (size 1.27 1.27))))
    (property "Value" "100" (at 57.46 80 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 60 90 90) (uuid "ana-rs7")
    (property "Reference" "RS7" (at 62.54 90 90) (effects (font (size 1.27 1.27))))
    (property "Value" "100" (at 57.46 90 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 60 100 90) (uuid "ana-rs8")
    (property "Reference" "RS8" (at 62.54 100 90) (effects (font (size 1.27 1.27))))
    (property "Value" "100" (at 57.46 100 90) (effects (font (size 1.27 1.27))))
  )
  
  (symbol (lib_id "Connector:Conn_Coaxial") (at 75 30 0) (uuid "ana-j4")
    (property "Reference" "J4" (at 75 34.89 0) (effects (font (size 1.27 1.27))))
    (property "Value" "EL0" (at 75 25.11 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Connector:Conn_Coaxial") (at 75 40 0) (uuid "ana-j5")
    (property "Reference" "J5" (at 75 44.89 0) (effects (font (size 1.27 1.27))))
    (property "Value" "EL1" (at 75 35.11 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Connector:Conn_Coaxial") (at 75 50 0) (uuid "ana-j6")
    (property "Reference" "J6" (at 75 54.89 0) (effects (font (size 1.27 1.27))))
    (property "Value" "EL2" (at 75 45.11 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Connector:Conn_Coaxial") (at 75 60 0) (uuid "ana-j7")
    (property "Reference" "J7" (at 75 64.89 0) (effects (font (size 1.27 1.27))))
    (property "Value" "EL3" (at 75 55.11 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Connector:Conn_Coaxial") (at 75 70 0) (uuid "ana-j8")
    (property "Reference" "J8" (at 75 74.89 0) (effects (font (size 1.27 1.27))))
    (property "Value" "EL4" (at 75 65.11 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Connector:Conn_Coaxial") (at 75 80 0) (uuid "ana-j9")
    (property "Reference" "J9" (at 75 84.89 0) (effects (font (size 1.27 1.27))))
    (property "Value" "EL5" (at 75 75.11 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Connector:Conn_Coaxial") (at 75 90 0) (uuid "ana-j10")
    (property "Reference" "J10" (at 75 94.89 0) (effects (font (size 1.27 1.27))))
    (property "Value" "EL6" (at 75 85.11 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Connector:Conn_Coaxial") (at 75 100 0) (uuid "ana-j11")
    (property "Reference" "J11" (at 75 104.89 0) (effects (font (size 1.27 1.27))))
    (property "Value" "EL7" (at 75 95.11 0) (effects (font (size 1.27 1.27))))
  )
  
  (symbol (lib_id "Diode:BAV99") (at 90 30 0) (uuid "ana-d4")
    (property "Reference" "D4" (at 90 33.16 0) (effects (font (size 1.27 1.27))))
    (property "Value" "BAV99" (at 90 26.84 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Diode:BAV99") (at 90 40 0) (uuid "ana-d5")
    (property "Reference" "D5" (at 90 43.16 0) (effects (font (size 1.27 1.27))))
    (property "Value" "BAV99" (at 90 36.84 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Diode:BAV99") (at 90 50 0) (uuid "ana-d6")
    (property "Reference" "D6" (at 90 53.16 0) (effects (font (size 1.27 1.27))))
    (property "Value" "BAV99" (at 90 46.84 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Diode:BAV99") (at 90 60 0) (uuid "ana-d7")
    (property "Reference" "D7" (at 90 63.16 0) (effects (font (size 1.27 1.27))))
    (property "Value" "BAV99" (at 90 56.84 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Diode:BAV99") (at 90 70 0) (uuid "ana-d8")
    (property "Reference" "D8" (at 90 73.16 0) (effects (font (size 1.27 1.27))))
    (property "Value" "BAV99" (at 90 66.84 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Diode:BAV99") (at 90 80 0) (uuid "ana-d9")
    (property "Reference" "D9" (at 90 83.16 0) (effects (font (size 1.27 1.27))))
    (property "Value" "BAV99" (at 90 76.84 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Diode:BAV99") (at 90 90 0) (uuid "ana-d10")
    (property "Reference" "D10" (at 90 93.16 0) (effects (font (size 1.27 1.27))))
    (property "Value" "BAV99" (at 90 86.84 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Diode:BAV99") (at 90 100 0) (uuid "ana-d11")
    (property "Reference" "D11" (at 90 103.16 0) (effects (font (size 1.27 1.27))))
    (property "Value" "BAV99" (at 90 96.84 0) (effects (font (size 1.27 1.27))))
  )
  
  (symbol (lib_id "Device:R") (at 100 30 90) (uuid "ana-rm1")
    (property "Reference" "RM1" (at 102.54 30 90) (effects (font (size 1.27 1.27))))
    (property "Value" "100" (at 97.46 30 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 100 40 90) (uuid "ana-rm2")
    (property "Reference" "RM2" (at 102.54 40 90) (effects (font (size 1.27 1.27))))
    (property "Value" "100" (at 97.46 40 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 100 50 90) (uuid "ana-rm3")
    (property "Reference" "RM3" (at 102.54 50 90) (effects (font (size 1.27 1.27))))
    (property "Value" "100" (at 97.46 50 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 100 60 90) (uuid "ana-rm4")
    (property "Reference" "RM4" (at 102.54 60 90) (effects (font (size 1.27 1.27))))
    (property "Value" "100" (at 97.46 60 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 100 70 90) (uuid "ana-rm5")
    (property "Reference" "RM5" (at 102.54 70 90) (effects (font (size 1.27 1.27))))
    (property "Value" "100" (at 97.46 70 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 100 80 90) (uuid "ana-rm6")
    (property "Reference" "RM6" (at 102.54 80 90) (effects (font (size 1.27 1.27))))
    (property "Value" "100" (at 97.46 80 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 100 90 90) (uuid "ana-rm7")
    (property "Reference" "RM7" (at 102.54 90 90) (effects (font (size 1.27 1.27))))
    (property "Value" "100" (at 97.46 90 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 100 100 90) (uuid "ana-rm8")
    (property "Reference" "RM8" (at 102.54 100 90) (effects (font (size 1.27 1.27))))
    (property "Value" "100" (at 97.46 100 90) (effects (font (size 1.27 1.27))))
  )
  
  (symbol (lib_id "Analog_Switch:CD4051B") (at 130 50 0) (uuid "ana-u4")
    (property "Reference" "U4" (at 122.38 63.92 0) (effects (font (size 1.27 1.27))))
    (property "Value" "CD4051B" (at 130 50 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Analog_Switch:CD4051B") (at 130 90 0) (uuid "ana-u5")
    (property "Reference" "U5" (at 122.38 103.92 0) (effects (font (size 1.27 1.27))))
    (property "Value" "CD4051B" (at 130 90 0) (effects (font (size 1.27 1.27))))
  )
  
  (symbol (lib_id "Device:C") (at 145 40 0) (uuid "ana-c6")
    (property "Reference" "C6" (at 147.54 40 0) (effects (font (size 1.27 1.27))))
    (property "Value" "100nF" (at 142.46 40 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:C") (at 145 80 0) (uuid "ana-c7")
    (property "Reference" "C7" (at 147.54 80 0) (effects (font (size 1.27 1.27))))
    (property "Value" "100nF" (at 142.46 80 0) (effects (font (size 1.27 1.27))))
  )
  
  (symbol (lib_id "Amplifier_Operational:OPA657") (at 170 50 0) (uuid "ana-u6")
    (property "Reference" "U6" (at 162.38 58.62 0) (effects (font (size 1.27 1.27))))
    (property "Value" "OPA657" (at 170 50 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Amplifier_Operational:OPA657") (at 170 90 0) (uuid "ana-u7")
    (property "Reference" "U7" (at 162.38 98.62 0) (effects (font (size 1.27 1.27))))
    (property "Value" "OPA657" (at 170 90 0) (effects (font (size 1.27 1.27))))
  )
  
  (symbol (lib_id "Device:R") (at 165 35 0) (uuid "ana-rf1")
    (property "Reference" "RF1" (at 165 32.46 0) (effects (font (size 1.27 1.27))))
    (property "Value" "1k" (at 165 37.54 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 175 35 0) (uuid "ana-rg1")
    (property "Reference" "RG1" (at 175 32.46 0) (effects (font (size 1.27 1.27))))
    (property "Value" "100" (at 175 37.54 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 165 75 0) (uuid "ana-rf2")
    (property "Reference" "RF2" (at 165 72.46 0) (effects (font (size 1.27 1.27))))
    (property "Value" "1k" (at 165 77.54 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:R") (at 175 75 0) (uuid "ana-rg2")
    (property "Reference" "RG2" (at 175 72.46 0) (effects (font (size 1.27 1.27))))
    (property "Value" "100" (at 175 77.54 0) (effects (font (size 1.27 1.27))))
  )
  
  (symbol (lib_id "Device:C") (at 185 50 90) (uuid "ana-cc1")
    (property "Reference" "CC1" (at 187.54 50 90) (effects (font (size 1.27 1.27))))
    (property "Value" "100nF" (at 182.46 50 90) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Device:C") (at 185 90 90) (uuid "ana-cc2")
    (property "Reference" "CC2" (at 187.54 90 90) (effects (font (size 1.27 1.27))))
    (property "Value" "100nF" (at 182.46 90 90) (effects (font (size 1.27 1.27))))
  )
  
  (symbol (lib_id "Connector:Conn_Coaxial") (at 200 50 0) (uuid "ana-j12")
    (property "Reference" "J12" (at 200 54.89 0) (effects (font (size 1.27 1.27))))
    (property "Value" "RX0_OUT" (at 200 45.11 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "Connector:Conn_Coaxial") (at 200 90 0) (uuid "ana-j13")
    (property "Reference" "J13" (at 200 94.89 0) (effects (font (size 1.27 1.27))))
    (property "Value" "RX1_OUT" (at 200 85.11 0) (effects (font (size 1.27 1.27))))
  )
  
  (symbol (lib_id "power:+5V") (at 140 25 0) (uuid "ana-pf1")
    (property "Reference" "#PWR07" (at 140 22.46 0) (effects hide))
    (property "Value" "+5V" (at 140 27.54 0) (effects (font (size 1.27 1.27))))
  )
  (symbol (lib_id "power:GND") (at 140 115 0) (mirror y) (uuid "ana-pf2")
    (property "Reference" "#PWR08" (at 140 117.54 0) (effects hide))
    (property "Value" "GND" (at 140 112.46 0) (effects (font (size 1.27 1.27))))
  )
  
  (global_label "GATE0" (shape input) (at 40 30 180) (effects (font (size 1.27 1.27))))
  (global_label "GATE1" (shape input) (at 40 40 180) (effects (font (size 1.27 1.27))))
  (global_label "GATE2" (shape input) (at 40 50 180) (effects (font (size 1.27 1.27))))
  (global_label "GATE3" (shape input) (at 40 60 180) (effects (font (size 1.27 1.27))))
  (global_label "GATE4" (shape input) (at 40 70 180) (effects (font (size 1.27 1.27))))
  (global_label "GATE5" (shape input) (at 40 80 180) (effects (font (size 1.27 1.27))))
  (global_label "GATE6" (shape input) (at 40 90 180) (effects (font (size 1.27 1.27))))
  (global_label "GATE7" (shape input) (at 40 100 180) (effects (font (size 1.27 1.27))))
  (global_label "MUX_A" (shape input) (at 115 40 180) (effects (font (size 1.27 1.27))))
  (global_label "MUX_B" (shape input) (at 115 45 180) (effects (font (size 1.27 1.27))))
  (global_label "MUX_C" (shape input) (at 115 50 180) (effects (font (size 1.27 1.27))))
  (global_label "+5V" (shape passive) (at 25 20 0) (effects (font (size 1.27 1.27))))
  (global_label "GND" (shape passive) (at 25 120 0) (effects (font (size 1.27 1.27))))
  
  (sheet_instances (path "/" (page "1")))
)'''
    return sch

def gen_main_sch():
    """Generate main schematic with hierarchical sheets"""
    sch = '''(kicad_sch
  (version 20231120)
  (generator "eeschema")
  (uuid "c91386be-ef17-4bcb-aaad-5175b258204a")
  (paper "A3")
  (title_block
    (title "TurboQuant Mux LNA Board")
    (date "2026-03-30")
    (rev "1.0")
    (company "TurboQuant")
    (comment 1 "8-Element Ultrasound Array Interface")
    (comment 2 "Hierarchical Design: Power | Digital | Analog")
  )
  (lib_symbols)
  
  (sheet (at 13.97 16.51) (size 80.01 71.12) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (stroke (width 0.1524) (type solid))
    (fill (color 0 0 0 0.0000))
    (uuid "31e7358f-421c-4108-98a5-1bd5cbdf3861")
    (property "Sheetname" "POWER_SUPPLIES" (at 13.97 15.7984 0) (effects (font (size 1.27 1.27)) (justify left bottom)))
    (property "Sheetfile" "power.kicad_sch" (at 13.97 88.2146 0) (effects (font (size 1.27 1.27)) (justify left top)))
    (instances (project "tuboquant_mux_lna" (path "/c91386be-ef17-4bcb-aaad-5175b258204a" (page "2"))))
  )
  
  (sheet (at 105.41 16.51) (size 100 80) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (stroke (width 0.1524) (type solid))
    (fill (color 0 0 0 0.0000))
    (uuid "bf41dd9b-ce45-467e-ac10-028c71ad2a9a")
    (property "Sheetname" "DIGITAL_CONTROL" (at 105.41 15.7984 0) (effects (font (size 1.27 1.27)) (justify left bottom)))
    (property "Sheetfile" "digital.kicad_sch" (at 105.41 97.7146 0) (effects (font (size 1.27 1.27)) (justify left top)))
    (instances (project "tuboquant_mux_lna" (path "/c91386be-ef17-4bcb-aaad-5175b258204a" (page "3"))))
  )
  
  (sheet (at 13.97 102.87) (size 191.44 55.88) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (stroke (width 0.1524) (type solid))
    (fill (color 0 0 0 0.0000))
    (uuid "da55019f-ccad-455b-840f-c04df8128d6c")
    (property "Sheetname" "ANALOG_FRONTEND" (at 13.97 102.1584 0) (effects (font (size 1.27 1.27)) (justify left bottom)))
    (property "Sheetfile" "analog.kicad_sch" (at 13.97 159.3346 0) (effects (font (size 1.27 1.27)) (justify left top)))
    (instances (project "tuboquant_mux_lna" (path "/c91386be-ef17-4bcb-aaad-5175b258204a" (page "4"))))
  )
  
  (sheet_instances (path "/" (page "1")))
)'''
    return sch

def gen_project_file():
    """Generate KiCad project file"""
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
    "ipc2581": {
      "dist": "",
      "distpn": "",
      "internal_id": "",
      "mfg": "",
      "mpn": ""
    },
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

# Full regeneration
def main():
    # Generate power sheet
    with open("power.kicad_sch", "w") as f:
        f.write(gen_power_sch())
    print("Generated: power.kicad_sch")
    
    # Generate digital sheet
    with open("digital.kicad_sch", "w") as f:
        f.write(gen_digital_sch())
    print("Generated: digital.kicad_sch")
    
    # Generate analog sheet
    with open("analog.kicad_sch", "w") as f:
        f.write(gen_analog_sch())
    print("Generated: analog.kicad_sch")
    
    # Generate main sheet
    with open("tuboquant_mux_lna.kicad_sch", "w") as f:
        f.write(gen_main_sch())
    print("Generated: tuboquant_mux_lna.kicad_sch (main)")
    
    # Generate project file
    with open("tuboquant_mux_lna.kicad_pro", "w") as f:
        f.write(gen_project_file())
    print("Generated: tuboquant_mux_lna.kicad_pro")
    
    print("\n✅ All files generated in turboquant_mux_lna_2!")

if __name__ == "__main__":
    main()
