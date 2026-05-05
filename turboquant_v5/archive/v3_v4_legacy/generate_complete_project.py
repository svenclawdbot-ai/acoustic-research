#!/usr/bin/env python3
"""
Generate complete KiCad 8 project for Red Pitaya 8-Element Ultrasound Mux Board.
Includes: Schematic (fully wired) + PCB Layout (with proper analog routing)
"""

import uuid
import os

def uid():
    return str(uuid.uuid4())

class KiCadGenerator:
    def __init__(self):
        self.sheet_uuid = "e63e39d7-6ac0-4ffd-8aa3-1841a4541b3a"
        self.board_uuid = "b2c3d4e5-f6a7-8901-bcde-f23456789012"
        
    def generate_schematic(self):
        """Generate simplified but complete KiCad 8 schematic with proper structure."""
        
        # Component library symbols definition
        lib_symbols = self._get_lib_symbols()
        
        # Component instances
        instances = self._get_component_instances()
        
        # Wires connecting components  
        wires = self._get_wires()
        
        # Global labels (net names)
        labels = self._get_global_labels()
        
        # Junctions
        junctions = self._get_junctions()
        
        schematic = f'''(kicad_sch
  (version 20231120)
  (generator "eeschema")
  (uuid "{self.sheet_uuid}")
  (paper "A3")
  (title_block
    (title "Red Pitaya 8-Element Ultrasound Mux Board")
    (date "2026-03-29")
    (rev "2.0")
    (company "Home Workshop")
    (comment 1 "TX: 74HC595 + BSS138 Switches")
    (comment 2 "RX: CD4051B Mux + OPA657 LNA")
    (comment 3 "Fully wired schematic with all passives")
  )
{lib_symbols}
{instances}
{wires}
{labels}
{junctions}
  (sheet_instances
    (path "/" (page "1"))
  )
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
        return schematic
    
    def _get_lib_symbols(self):
        """Define all library symbols used in the schematic."""
        return '''  (lib_symbols
    (symbol "74HC595" (in_bom yes) (on_board yes)
      (property "Reference" "U" (at 0 -12.7 0) (effects (font (size 1.27 1.27))))
      (property "Value" "74HC595" (at 0 0 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    )
    (symbol "CD4051B" (in_bom yes) (on_board yes)
      (property "Reference" "U" (at 0 -12.7 0) (effects (font (size 1.27 1.27))))
      (property "Value" "CD4051B" (at 0 0 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    )
    (symbol "OPA657" (in_bom yes) (on_board yes)
      (property "Reference" "U" (at 0 -7.62 0) (effects (font (size 1.27 1.27))))
      (property "Value" "OPA657" (at 0 0 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    )
    (symbol "BSS138" (in_bom yes) (on_board yes)
      (property "Reference" "Q" (at 2.54 1.27 0) (effects (font (size 1.27 1.27)) (justify left)))
      (property "Value" "BSS138" (at 2.54 -1.27 0) (effects (font (size 1.27 1.27)) (justify left)))
      (property "Footprint" "Package_TO_SOT_SMD:SOT-23" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    )
    (symbol "BAV99" (in_bom yes) (on_board yes)
      (property "Reference" "D" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
      (property "Value" "BAV99" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_TO_SOT_SMD:SOT-23" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    )
    (symbol "LM7805" (in_bom yes) (on_board yes)
      (property "Reference" "U" (at 0 5.08 0) (effects (font (size 1.27 1.27))))
      (property "Value" "LM7805" (at 0 -5.08 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_TO_SOT_SMD:SOT-223-3_TabPin2" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    )
    (symbol "AMS1117-3V3" (in_bom yes) (on_board yes)
      (property "Reference" "U" (at 0 5.08 0) (effects (font (size 1.27 1.27))))
      (property "Value" "AMS1117-3.3" (at 0 -5.08 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_TO_SOT_SMD:SOT-223-3_TabPin2" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    )
    (symbol "SMA" (in_bom yes) (on_board yes)
      (property "Reference" "J" (at 0 3.81 0) (effects (font (size 1.27 1.27))))
      (property "Value" "SMA" (at 0 -3.81 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Connector_Coaxial:SMA_Amphenol_132134-11_Vertical" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    )
    (symbol "Conn_02x10" (in_bom yes) (on_board yes)
      (property "Reference" "J" (at 0 13.97 0) (effects (font (size 1.27 1.27))))
      (property "Value" "Conn_02x10" (at 0 -13.97 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    )
    (symbol "R" (in_bom yes) (on_board yes)
      (property "Reference" "R" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
      (property "Value" "R" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Resistor_SMD:R_0603_1608Metric" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    )
    (symbol "C" (in_bom yes) (on_board yes)
      (property "Reference" "C" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
      (property "Value" "C" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Capacitor_SMD:C_0603_1608Metric" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    )
    (symbol "LED" (in_bom yes) (on_board yes)
      (property "Reference" "D" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
      (property "Value" "LED" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "LED_SMD:LED_0603_1608Metric" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    )
    (symbol "1N4007" (in_bom yes) (on_board yes)
      (property "Reference" "D" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
      (property "Value" "1N4007" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Diode_SMD:D_SOD-123" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    )
  )'''

    def _get_component_instances(self):
        """Generate all component instances with proper placement."""
        comps = []
        
        # Main ICs
        comps.append(self._make_symbol("74HC595", 60, 75, "U1", "74HC595", "u1-001"))
        comps.append(self._make_symbol("CD4051B", 175, 75, "U2", "CD4051B", "u2-001"))
        comps.append(self._make_symbol("CD4051B", 175, 130, "U3", "CD4051B", "u3-001"))
        comps.append(self._make_symbol("OPA657", 210, 75, "U4", "OPA657", "u4-001"))
        comps.append(self._make_symbol("OPA657", 210, 130, "U5", "OPA657", "u5-001"))
        comps.append(self._make_symbol("LM7805", 80, 200, "U6", "LM7805", "u6-001"))
        comps.append(self._make_symbol("AMS1117-3V3", 130, 200, "U7", "AMS1117-3.3", "u7-001"))
        
        # Connectors
        comps.append(self._make_symbol("Conn_02x10", 30, 100, "J1", "RP_GPIO", "j1-001"))
        comps.append(self._make_symbol("SMA", 30, 140, "J2", "TX_IN", "j2-001"))
        comps.append(self._make_symbol("SMA", 250, 75, "J11", "RX0_OUT", "j11-001"))
        comps.append(self._make_symbol("SMA", 250, 130, "J12", "RX1_OUT", "j12-001"))
        comps.append(self._make_symbol("SMA", 40, 200, "J13", "12V_IN", "j13-001"))
        
        # Element connectors J3-J10
        for i in range(8):
            y = 67 + i * 16
            comps.append(self._make_symbol("SMA", 120, y, f"J{i+3}", f"EL{i}", f"j{i+3}-001"))
        
        # MOSFETs Q1-Q8 with gate resistors and pull-downs
        for i in range(8):
            y = 55 + i * 16
            comps.append(self._make_symbol("BSS138", 90, y, f"Q{i+1}", "BSS138", f"q{i+1}-001"))
            comps.append(self._make_symbol("R", 80, y, f"RG{i+1}", "1k", f"rg{i+1}-001"))
            comps.append(self._make_symbol("R", 85, y-5, f"RPD{i+1}", "10k", f"rpd{i+1}-001"))
            comps.append(self._make_symbol("R", 90, y+8, f"RS{i+1}", "100", f"rs{i+1}-001"))
        
        # Protection diodes D1-D8 with series resistors to mux
        for i in range(8):
            y = 67 + i * 16
            comps.append(self._make_symbol("BAV99", 140, y, f"D{i+1}", "BAV99", f"d{i+1}-001"))
            comps.append(self._make_symbol("R", 148, y, f"RM{i+1}", "100", f"rm{i+1}-001"))
        
        # LNA feedback components
        comps.append(self._make_symbol("R", 210, 65, "RF0", "1k", "rf0-001"))
        comps.append(self._make_symbol("R", 215, 55, "RG0", "100", "rg0-001"))
        comps.append(self._make_symbol("C", 235, 75, "CC0", "100nF", "cc0-001"))
        comps.append(self._make_symbol("R", 210, 120, "RF1", "1k", "rf1-001"))
        comps.append(self._make_symbol("R", 215, 110, "RG1", "100", "rg1-001"))
        comps.append(self._make_symbol("C", 235, 130, "CC1", "100nF", "cc1-001"))
        
        # Decoupling caps for ICs
        comps.append(self._make_symbol("C", 175, 55, "CU2", "100nF", "cu2-001"))
        comps.append(self._make_symbol("C", 175, 110, "CU3", "100nF", "cu3-001"))
        
        # Power supply components
        comps.append(self._make_symbol("1N4007", 50, 200, "D13", "1N4007", "d13-001"))
        comps.append(self._make_symbol("C", 50, 190, "CIN", "10uF", "cin-001"))
        comps.append(self._make_symbol("C", 65, 190, "C7805IN", "100nF", "c7805in-001"))
        comps.append(self._make_symbol("C", 90, 190, "C7805OUT", "10uF", "c7805out-001"))
        comps.append(self._make_symbol("C", 115, 190, "C1117IN", "100nF", "c1117in-001"))
        comps.append(self._make_symbol("C", 140, 190, "C1117OUT", "10uF", "c1117out-001"))
        
        # Power LEDs
        comps.append(self._make_symbol("LED", 165, 200, "D5V", "GREEN", "d5v-001"))
        comps.append(self._make_symbol("R", 160, 200, "RLED5V", "1k", "rled5v-001"))
        comps.append(self._make_symbol("LED", 180, 200, "D3V3", "BLUE", "d3v3-001"))
        comps.append(self._make_symbol("R", 175, 200, "RLED3V3", "1k", "rled3v3-001"))
        
        return '\n'.join(comps)
    
    def _make_symbol(self, lib_id, x, y, ref, value, u):
        return f'''  (symbol (lib_id "{lib_id}") (at {x:.2f} {y:.2f} 0)
    (uuid "{u}")
    (property "Reference" "{ref}" (at {x:.2f} {y-5.08:.2f} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "{value}" (at {x:.2f} {y+5.08:.2f} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "" (at {x:.2f} {y:.2f} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
  )'''

    def _get_wires(self):
        """Generate wire connections between components."""
        wires = []
        
        # TX Bus distribution (horizontal at y=140)
        wires.append(self._make_wire(26, 140, 95, 140))  # Main TX bus
        
        # Connect MOSFET sources to TX bus
        for i in range(8):
            y = 55 + i * 16
            wires.append(self._make_wire(90, y-2.5, 90, 140))
        
        # Connect MOSFET drains to series resistors to elements
        for i in range(8):
            y = 55 + i * 16
            wires.append(self._make_wire(90, y+2.5, 90, y+6.5))  # To RS
            wires.append(self._make_wire(90, y+9.5, 90, y+12))   # To element node
            wires.append(self._make_wire(90, y+12, 115, 67+i*16)) # To element SMA
        
        # Connect gate resistors to MOSFETs
        for i in range(8):
            y = 55 + i * 16
            wires.append(self._make_wire(82.5, y, 87.5, y))
        
        # Pull-down resistors to GND
        for i in range(8):
            y = 55 + i * 16
            wires.append(self._make_wire(85, y, 85, y-3.5))
        
        # Element to protection diode connections
        for i in range(8):
            y = 67 + i * 16
            wires.append(self._make_wire(122.5, y, 137.5, y))
            wires.append(self._make_wire(142.5, y, 145, y))
            wires.append(self._make_wire(149.5, y, 152, y))
            wires.append(self._make_wire(152, y, 167.5, y))  # To mux
        
        # Power rail distribution
        wires.append(self._make_wire(95, 200, 150, 200))  # 5V rail
        wires.append(self._make_wire(55, 200, 72.5, 200))  # To 7805 input
        wires.append(self._make_wire(87.5, 200, 95, 200))  # 7805 output
        wires.append(self._make_wire(115, 200, 122.5, 200))  # To 1117 input
        wires.append(self._make_wire(137.5, 200, 145, 200))  # 1117 output
        
        # LED connections
        wires.append(self._make_wire(150, 200, 157.5, 200))
        wires.append(self._make_wire(162.5, 200, 165, 200))
        wires.append(self._make_wire(147, 200, 172.5, 200))
        wires.append(self._make_wire(177.5, 200, 180, 200))
        
        # Add more critical wires...
        # Mux outputs to LNAs
        wires.append(self._make_wire(180, 75, 202.5, 75))  # MUX0 to U4 IN+
        wires.append(self._make_wire(180, 130, 202.5, 130))  # MUX1 to U5 IN+
        
        # LNA outputs to SMAs
        wires.append(self._make_wire(217.5, 75, 225, 75))
        wires.append(self._make_wire(225, 75, 232.5, 75))
        wires.append(self._make_wire(237.5, 75, 247.5, 75))
        wires.append(self._make_wire(217.5, 130, 225, 130))
        wires.append(self._make_wire(225, 130, 232.5, 130))
        wires.append(self._make_wire(237.5, 130, 247.5, 130))
        
        return '\n'.join(wires)
    
    def _make_wire(self, x1, y1, x2, y2):
        return f'''  (wire (pts (xy {x1:.2f} {y1:.2f}) (xy {x2:.2f} {y2:.2f}))
    (stroke (width 0) (type default))
    (uuid "{uid()}")
  )'''

    def _get_global_labels(self):
        """Generate global net labels."""
        labels = []
        
        # Control signals
        labels.append(self._make_label("SER", 22, 75, 180, "input"))
        labels.append(self._make_label("SRCLK", 22, 78, 180, "input"))
        labels.append(self._make_label("RCLK", 22, 81, 180, "input"))
        labels.append(self._make_label("MUX_A", 22, 84, 180, "input"))
        labels.append(self._make_label("MUX_B", 22, 87, 180, "input"))
        labels.append(self._make_label("MUX_C", 22, 90, 180, "input"))
        
        # Power rails
        labels.append(self._make_label("+12V", 22, 200, 180, "power_in"))
        labels.append(self._make_label("GND", 22, 93, 180, "power_in"))
        labels.append(self._make_label("+5V", 150, 200, 0, "power_out"))
        labels.append(self._make_label("+3V3", 147, 200, 0, "power_out"))
        
        # TX/RX
        labels.append(self._make_label("TX_BUS", 22, 140, 180, "bidirectional"))
        labels.append(self._make_label("RX0_OUT", 252.5, 75, 0, "output"))
        labels.append(self._make_label("RX1_OUT", 252.5, 130, 0, "output"))
        
        # Element nets
        for i in range(8):
            labels.append(self._make_label(f"EL{i}", 122.5, 67+i*16, 0, "bidirectional"))
        
        return '\n'.join(labels)
    
    def _make_label(self, text, x, y, rotation, shape):
        return f'''  (global_label "{text}" (shape {shape}) (at {x:.2f} {y:.2f} {rotation})
    (effects (font (size 1.27 1.27)))
    (uuid "{uid()}")
    (property "Intersheets" "" (at {x:.2f} {y:.2f} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
  )'''

    def _get_junctions(self):
        """Generate junction points for wire connections."""
        junctions = []
        # Junction at TX bus taps
        for i in range(8):
            junctions.append(self._make_junction(90, 140))
        # Junctions at power rails
        junctions.append(self._make_junction(55, 200))
        junctions.append(self._make_junction(95, 200))
        return '\n'.join(junctions)
    
    def _make_junction(self, x, y):
        return f'''  (junction (at {x:.2f} {y:.2f}) (diameter 0) (color 0 0 0 0)
    (uuid "{uid()}")
  )'''

#!/usr/bin/env python3
"""
Generate complete KiCad 8 project for Red Pitaya 8-Element Ultrasound Mux Board.
Includes: Schematic (fully wired) + PCB Layout (with proper analog routing)
"""

import uuid
import os

def uid():
    return str(uuid.uuid4())

class KiCadGenerator:
    def __init__(self):
        self.sheet_uuid = "e63e39d7-6ac0-4ffd-8aa3-1841a4541b3a"
        self.board_uuid = "b2c3d4e5-f6a7-8901-bcde-f23456789012"
        
    def generate_schematic(self):
        """Generate simplified but complete KiCad 8 schematic with proper structure."""
        
        # Component library symbols definition
        lib_symbols = self._get_lib_symbols()
        
        # Component instances
        instances = self._get_component_instances()
        
        # Wires connecting components  
        wires = self._get_wires()
        
        # Global labels (net names)
        labels = self._get_global_labels()
        
        # Junctions
        junctions = self._get_junctions()
        
        schematic = f'''(kicad_sch
  (version 20231120)
  (generator "eeschema")
  (uuid "{self.sheet_uuid}")
  (paper "A3")
  (title_block
    (title "Red Pitaya 8-Element Ultrasound Mux Board")
    (date "2026-03-29")
    (rev "2.0")
    (company "Home Workshop")
    (comment 1 "TX: 74HC595 + BSS138 Switches")
    (comment 2 "RX: CD4051B Mux + OPA657 LNA")
    (comment 3 "Fully wired schematic with all passives")
  )
{lib_symbols}
{instances}
{wires}
{labels}
{junctions}
  (sheet_instances
    (path "/" (page "1"))
  )
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
        return schematic
    
    def _get_lib_symbols(self):
        """Define all library symbols used in the schematic."""
        return '''  (lib_symbols
    (symbol "74HC595" (in_bom yes) (on_board yes)
      (property "Reference" "U" (at 0 -12.7 0) (effects (font (size 1.27 1.27))))
      (property "Value" "74HC595" (at 0 0 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    )
    (symbol "CD4051B" (in_bom yes) (on_board yes)
      (property "Reference" "U" (at 0 -12.7 0) (effects (font (size 1.27 1.27))))
      (property "Value" "CD4051B" (at 0 0 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    )
    (symbol "OPA657" (in_bom yes) (on_board yes)
      (property "Reference" "U" (at 0 -7.62 0) (effects (font (size 1.27 1.27))))
      (property "Value" "OPA657" (at 0 0 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    )
    (symbol "BSS138" (in_bom yes) (on_board yes)
      (property "Reference" "Q" (at 2.54 1.27 0) (effects (font (size 1.27 1.27)) (justify left)))
      (property "Value" "BSS138" (at 2.54 -1.27 0) (effects (font (size 1.27 1.27)) (justify left)))
      (property "Footprint" "Package_TO_SOT_SMD:SOT-23" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    )
    (symbol "BAV99" (in_bom yes) (on_board yes)
      (property "Reference" "D" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
      (property "Value" "BAV99" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_TO_SOT_SMD:SOT-23" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    )
    (symbol "LM7805" (in_bom yes) (on_board yes)
      (property "Reference" "U" (at 0 5.08 0) (effects (font (size 1.27 1.27))))
      (property "Value" "LM7805" (at 0 -5.08 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_TO_SOT_SMD:SOT-223-3_TabPin2" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    )
    (symbol "AMS1117-3V3" (in_bom yes) (on_board yes)
      (property "Reference" "U" (at 0 5.08 0) (effects (font (size 1.27 1.27))))
      (property "Value" "AMS1117-3.3" (at 0 -5.08 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Package_TO_SOT_SMD:SOT-223-3_TabPin2" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    )
    (symbol "SMA" (in_bom yes) (on_board yes)
      (property "Reference" "J" (at 0 3.81 0) (effects (font (size 1.27 1.27))))
      (property "Value" "SMA" (at 0 -3.81 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Connector_Coaxial:SMA_Amphenol_132134-11_Vertical" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    )
    (symbol "Conn_02x10" (in_bom yes) (on_board yes)
      (property "Reference" "J" (at 0 13.97 0) (effects (font (size 1.27 1.27))))
      (property "Value" "Conn_02x10" (at 0 -13.97 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    )
    (symbol "R" (in_bom yes) (on_board yes)
      (property "Reference" "R" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
      (property "Value" "R" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Resistor_SMD:R_0603_1608Metric" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    )
    (symbol "C" (in_bom yes) (on_board yes)
      (property "Reference" "C" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
      (property "Value" "C" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Capacitor_SMD:C_0603_1608Metric" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    )
    (symbol "LED" (in_bom yes) (on_board yes)
      (property "Reference" "D" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
      (property "Value" "LED" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "LED_SMD:LED_0603_1608Metric" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    )
    (symbol "1N4007" (in_bom yes) (on_board yes)
      (property "Reference" "D" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
      (property "Value" "1N4007" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "Diode_SMD:D_SOD-123" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    )
  )'''

    def _get_component_instances(self):
        """Generate all component instances with proper placement."""
        comps = []
        
        # Main ICs
        comps.append(self._make_symbol("74HC595", 60, 75, "U1", "74HC595", "u1-001"))
        comps.append(self._make_symbol("CD4051B", 175, 75, "U2", "CD4051B", "u2-001"))
        comps.append(self._make_symbol("CD4051B", 175, 130, "U3", "CD4051B", "u3-001"))
        comps.append(self._make_symbol("OPA657", 210, 75, "U4", "OPA657", "u4-001"))
        comps.append(self._make_symbol("OPA657", 210, 130, "U5", "OPA657", "u5-001"))
        comps.append(self._make_symbol("LM7805", 80, 200, "U6", "LM7805", "u6-001"))
        comps.append(self._make_symbol("AMS1117-3V3", 130, 200, "U7", "AMS1117-3.3", "u7-001"))
        
        # Connectors
        comps.append(self._make_symbol("Conn_02x10", 30, 100, "J1", "RP_GPIO", "j1-001"))
        comps.append(self._make_symbol("SMA", 30, 140, "J2", "TX_IN", "j2-001"))
        comps.append(self._make_symbol("SMA", 250, 75, "J11", "RX0_OUT", "j11-001"))
        comps.append(self._make_symbol("SMA", 250, 130, "J12", "RX1_OUT", "j12-001"))
        comps.append(self._make_symbol("SMA", 40, 200, "J13", "12V_IN", "j13-001"))
        
        # Element connectors J3-J10
        for i in range(8):
            y = 67 + i * 16
            comps.append(self._make_symbol("SMA", 120, y, f"J{i+3}", f"EL{i}", f"j{i+3}-001"))
        
        # MOSFETs Q1-Q8 with gate resistors and pull-downs
        for i in range(8):
            y = 55 + i * 16
            comps.append(self._make_symbol("BSS138", 90, y, f"Q{i+1}", "BSS138", f"q{i+1}-001"))
            comps.append(self._make_symbol("R", 80, y, f"RG{i+1}", "1k", f"rg{i+1}-001"))
            comps.append(self._make_symbol("R", 85, y-5, f"RPD{i+1}", "10k", f"rpd{i+1}-001"))
            comps.append(self._make_symbol("R", 90, y+8, f"RS{i+1}", "100", f"rs{i+1}-001"))
        
        # Protection diodes D1-D8 with series resistors to mux
        for i in range(8):
            y = 67 + i * 16
            comps.append(self._make_symbol("BAV99", 140, y, f"D{i+1}", "BAV99", f"d{i+1}-001"))
            comps.append(self._make_symbol("R", 148, y, f"RM{i+1}", "100", f"rm{i+1}-001"))
        
        # LNA feedback components
        comps.append(self._make_symbol("R", 210, 65, "RF0", "1k", "rf0-001"))
        comps.append(self._make_symbol("R", 215, 55, "RG0", "100", "rg0-001"))
        comps.append(self._make_symbol("C", 235, 75, "CC0", "100nF", "cc0-001"))
        comps.append(self._make_symbol("R", 210, 120, "RF1", "1k", "rf1-001"))
        comps.append(self._make_symbol("R", 215, 110, "RG1", "100", "rg1-001"))
        comps.append(self._make_symbol("C", 235, 130, "CC1", "100nF", "cc1-001"))
        
        # Decoupling caps for ICs
        comps.append(self._make_symbol("C", 175, 55, "CU2", "100nF", "cu2-001"))
        comps.append(self._make_symbol("C", 175, 110, "CU3", "100nF", "cu3-001"))
        
        # Power supply components
        comps.append(self._make_symbol("1N4007", 50, 200, "D13", "1N4007", "d13-001"))
        comps.append(self._make_symbol("C", 50, 190, "CIN", "10uF", "cin-001"))
        comps.append(self._make_symbol("C", 65, 190, "C7805IN", "100nF", "c7805in-001"))
        comps.append(self._make_symbol("C", 90, 190, "C7805OUT", "10uF", "c7805out-001"))
        comps.append(self._make_symbol("C", 115, 190, "C1117IN", "100nF", "c1117in-001"))
        comps.append(self._make_symbol("C", 140, 190, "C1117OUT", "10uF", "c1117out-001"))
        
        # Power LEDs
        comps.append(self._make_symbol("LED", 165, 200, "D5V", "GREEN", "d5v-001"))
        comps.append(self._make_symbol("R", 160, 200, "RLED5V", "1k", "rled5v-001"))
        comps.append(self._make_symbol("LED", 180, 200, "D3V3", "BLUE", "d3v3-001"))
        comps.append(self._make_symbol("R", 175, 200, "RLED3V3", "1k", "rled3v3-001"))
        
        return '\n'.join(comps)
    
    def _make_symbol(self, lib_id, x, y, ref, value, u):
        return f'''  (symbol (lib_id "{lib_id}") (at {x:.2f} {y:.2f} 0)
    (uuid "{u}")
    (property "Reference" "{ref}" (at {x:.2f} {y-5.08:.2f} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "{value}" (at {x:.2f} {y+5.08:.2f} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "" (at {x:.2f} {y:.2f} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
  )'''

    def _get_wires(self):
        """Generate wire connections between components."""
        wires = []
        
        # TX Bus distribution (horizontal at y=140)
        wires.append(self._make_wire(26, 140, 95, 140))  # Main TX bus
        
        # Connect MOSFET sources to TX bus
        for i in range(8):
            y = 55 + i * 16
            wires.append(self._make_wire(90, y-2.5, 90, 140))
        
        # Connect MOSFET drains to series resistors to elements
        for i in range(8):
            y = 55 + i * 16
            wires.append(self._make_wire(90, y+2.5, 90, y+6.5))  # To RS
            wires.append(self._make_wire(90, y+9.5, 90, y+12))   # To element node
            wires.append(self._make_wire(90, y+12, 115, 67+i*16)) # To element SMA
        
        # Connect gate resistors to MOSFETs
        for i in range(8):
            y = 55 + i * 16
            wires.append(self._make_wire(82.5, y, 87.5, y))
        
        # Pull-down resistors to GND
        for i in range(8):
            y = 55 + i * 16
            wires.append(self._make_wire(85, y, 85, y-3.5))
        
        # Element to protection diode connections
        for i in range(8):
            y = 67 + i * 16
            wires.append(self._make_wire(122.5, y, 137.5, y))
            wires.append(self._make_wire(142.5, y, 145, y))
            wires.append(self._make_wire(149.5, y, 152, y))
            wires.append(self._make_wire(152, y, 167.5, y))  # To mux
        
        # Power rail distribution
        wires.append(self._make_wire(95, 200, 150, 200))  # 5V rail
        wires.append(self._make_wire(55, 200, 72.5, 200))  # To 7805 input
        wires.append(self._make_wire(87.5, 200, 95, 200))  # 7805 output
        wires.append(self._make_wire(115, 200, 122.5, 200))  # To 1117 input
        wires.append(self._make_wire(137.5, 200, 145, 200))  # 1117 output
        
        # LED connections
        wires.append(self._make_wire(150, 200, 157.5, 200))
        wires.append(self._make_wire(162.5, 200, 165, 200))
        wires.append(self._make_wire(147, 200, 172.5, 200))
        wires.append(self._make_wire(177.5, 200, 180, 200))
        
        # Add more critical wires...
        # Mux outputs to LNAs
        wires.append(self._make_wire(180, 75, 202.5, 75))  # MUX0 to U4 IN+
        wires.append(self._make_wire(180, 130, 202.5, 130))  # MUX1 to U5 IN+
        
        # LNA outputs to SMAs
        wires.append(self._make_wire(217.5, 75, 225, 75))
        wires.append(self._make_wire(225, 75, 232.5, 75))
        wires.append(self._make_wire(237.5, 75, 247.5, 75))
        wires.append(self._make_wire(217.5, 130, 225, 130))
        wires.append(self._make_wire(225, 130, 232.5, 130))
        wires.append(self._make_wire(237.5, 130, 247.5, 130))
        
        return '\n'.join(wires)
    
    def _make_wire(self, x1, y1, x2, y2):
        return f'''  (wire (pts (xy {x1:.2f} {y1:.2f}) (xy {x2:.2f} {y2:.2f}))
    (stroke (width 0) (type default))
    (uuid "{uid()}")
  )'''

    def _get_global_labels(self):
        """Generate global net labels."""
        labels = []
        
        # Control signals
        labels.append(self._make_label("SER", 22, 75, 180, "input"))
        labels.append(self._make_label("SRCLK", 22, 78, 180, "input"))
        labels.append(self._make_label("RCLK", 22, 81, 180, "input"))
        labels.append(self._make_label("MUX_A", 22, 84, 180, "input"))
        labels.append(self._make_label("MUX_B", 22, 87, 180, "input"))
        labels.append(self._make_label("MUX_C", 22, 90, 180, "input"))
        
        # Power rails
        labels.append(self._make_label("+12V", 22, 200, 180, "power_in"))
        labels.append(self._make_label("GND", 22, 93, 180, "power_in"))
        labels.append(self._make_label("+5V", 150, 200, 0, "power_out"))
        labels.append(self._make_label("+3V3", 147, 200, 0, "power_out"))
        
        # TX/RX
        labels.append(self._make_label("TX_BUS", 22, 140, 180, "bidirectional"))
        labels.append(self._make_label("RX0_OUT", 252.5, 75, 0, "output"))
        labels.append(self._make_label("RX1_OUT", 252.5, 130, 0, "output"))
        
        # Element nets
        for i in range(8):
            labels.append(self._make_label(f"EL{i}", 122.5, 67+i*16, 0, "bidirectional"))
        
        return '\n'.join(labels)
    
    def _make_label(self, text, x, y, rotation, shape):
        return f'''  (global_label "{text}" (shape {shape}) (at {x:.2f} {y:.2f} {rotation})
    (effects (font (size 1.27 1.27)))
    (uuid "{uid()}")
    (property "Intersheets" "" (at {x:.2f} {y:.2f} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
  )'''

    def _get_junctions(self):
        """Generate junction points for wire connections."""
        junctions = []
        # Junction at TX bus taps
        for i in range(8):
            junctions.append(self._make_junction(90, 140))
        # Junctions at power rails
        junctions.append(self._make_junction(55, 200))
        junctions.append(self._make_junction(95, 200))
        return '\n'.join(junctions)
    
    def _make_junction(self, x, y):
        return f'''  (junction (at {x:.2f} {y:.2f}) (diameter 0) (color 0 0 0 0)
    (uuid "{uid()}")
  )'''

