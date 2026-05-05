#!/usr/bin/env python3
"""
Generate KiCad 8 schematic for Red Pitaya 8-Element Ultrasound Mux Board.

Run: python3 generate_schematic.py
Output: red_pitaya_mux_board.kicad_sch

Design: See DESIGN.md for full circuit description.
"""

import uuid
import math

def uid():
    return str(uuid.uuid4())

class SchematicGenerator:
    def __init__(self):
        self.lib_symbols = []
        self.instances = []
        self.wires = []
        self.labels = []
        self.global_labels = []
        self.texts = []
        self.no_connects = []
        self.power_symbols = []
        self.junctions = []
        self._ref_count = {}

    # ── Symbol library definitions ──────────────────────────────

    def _make_ic_symbol(self, name, pins, width=5.08, desc=""):
        """Create a generic IC symbol with labeled pins.
        pins: list of (pin_name, pin_number, side, pin_type, y_offset)
            side: 'L' or 'R'
            pin_type: 'input', 'output', 'passive', 'power_in', 'bidirectional'
        """
        half_w = width / 2
        # Calculate height from pin count
        left_pins = [p for p in pins if p[2] == 'L']
        right_pins = [p for p in pins if p[2] == 'R']
        max_pins = max(len(left_pins), len(right_pins))
        height = max(max_pins * 2.54 + 2.54, 5.08)
        half_h = height / 2

        pin_strs = []
        for pname, pnum, side, ptype, yoff in pins:
            if side == 'L':
                px = -(half_w + 2.54)
                angle = 0
            else:
                px = half_w + 2.54
                angle = 180
            py = yoff
            pin_strs.append(
                f'      (pin {ptype} line (at {px:.2f} {py:.2f} {angle}) (length 2.54)\n'
                f'        (name "{pname}" (effects (font (size 1.016 1.016))))\n'
                f'        (number "{pnum}" (effects (font (size 1.016 1.016))))\n'
                f'      )'
            )

        sym = (
            f'  (symbol "{name}" (in_bom yes) (on_board yes)\n'
            f'    (property "Reference" "U" (at 0 {half_h + 1.27:.2f} 0)\n'
            f'      (effects (font (size 1.27 1.27)))\n'
            f'    )\n'
            f'    (property "Value" "{name}" (at 0 {-(half_h + 1.27):.2f} 0)\n'
            f'      (effects (font (size 1.27 1.27)))\n'
            f'    )\n'
            f'    (property "Footprint" "" (at 0 0 0)\n'
            f'      (effects (font (size 1.27 1.27)) hide)\n'
            f'    )\n'
            f'    (property "Datasheet" "" (at 0 0 0)\n'
            f'      (effects (font (size 1.27 1.27)) hide)\n'
            f'    )\n'
            f'    (property "Description" "{desc}" (at 0 0 0)\n'
            f'      (effects (font (size 1.27 1.27)) hide)\n'
            f'    )\n'
            f'    (symbol "{name}_0_1"\n'
            f'      (rectangle (start {-half_w:.2f} {half_h:.2f}) (end {half_w:.2f} {-half_h:.2f})\n'
            f'        (stroke (width 0.254) (type default))\n'
            f'        (fill (type background))\n'
            f'      )\n'
            f'    )\n'
            f'    (symbol "{name}_1_1"\n'
            + '\n'.join(pin_strs) + '\n'
            f'    )\n'
            f'  )'
        )
        self.lib_symbols.append(sym)

    def _make_2pin_symbol(self, name, p1_name="1", p2_name="2", desc=""):
        """Create a simple 2-pin passive symbol (resistor, cap, etc.)."""
        sym = (
            f'  (symbol "{name}" (in_bom yes) (on_board yes)\n'
            f'    (property "Reference" "R" (at 0 2.54 0)\n'
            f'      (effects (font (size 1.27 1.27)))\n'
            f'    )\n'
            f'    (property "Value" "{name}" (at 0 -2.54 0)\n'
            f'      (effects (font (size 1.27 1.27)))\n'
            f'    )\n'
            f'    (property "Footprint" "" (at 0 0 0)\n'
            f'      (effects (font (size 1.27 1.27)) hide)\n'
            f'    )\n'
            f'    (property "Datasheet" "" (at 0 0 0)\n'
            f'      (effects (font (size 1.27 1.27)) hide)\n'
            f'    )\n'
            f'    (symbol "{name}_0_1"\n'
            f'      (rectangle (start -1.016 2.54) (end 1.016 -2.54)\n'
            f'        (stroke (width 0.254) (type default))\n'
            f'        (fill (type background))\n'
            f'      )\n'
            f'    )\n'
            f'    (symbol "{name}_1_1"\n'
            f'      (pin passive line (at 0 3.81 270) (length 1.27)\n'
            f'        (name "{p1_name}" (effects (font (size 1.016 1.016))))\n'
            f'        (number "1" (effects (font (size 1.016 1.016))))\n'
            f'      )\n'
            f'      (pin passive line (at 0 -3.81 90) (length 1.27)\n'
            f'        (name "{p2_name}" (effects (font (size 1.016 1.016))))\n'
            f'        (number "2" (effects (font (size 1.016 1.016))))\n'
            f'      )\n'
            f'    )\n'
            f'  )'
        )
        self.lib_symbols.append(sym)

    def _make_connector_symbol(self, name, num_pins, desc=""):
        """Create a connector symbol with N pins."""
        half_h = num_pins * 2.54 / 2
        pin_strs = []
        for i in range(num_pins):
            y = half_h - (i + 0.5) * 2.54
            pin_strs.append(
                f'      (pin passive line (at {-5.08:.2f} {y:.2f} 0) (length 2.54)\n'
                f'        (name "Pin_{i+1}" (effects (font (size 1.016 1.016))))\n'
                f'        (number "{i+1}" (effects (font (size 1.016 1.016))))\n'
                f'      )'
            )
        sym = (
            f'  (symbol "{name}" (in_bom yes) (on_board yes)\n'
            f'    (property "Reference" "J" (at 0 {half_h + 1.27:.2f} 0)\n'
            f'      (effects (font (size 1.27 1.27)))\n'
            f'    )\n'
            f'    (property "Value" "{name}" (at 0 {-(half_h + 1.27):.2f} 0)\n'
            f'      (effects (font (size 1.27 1.27)))\n'
            f'    )\n'
            f'    (property "Footprint" "" (at 0 0 0)\n'
            f'      (effects (font (size 1.27 1.27)) hide)\n'
            f'    )\n'
            f'    (property "Datasheet" "" (at 0 0 0)\n'
            f'      (effects (font (size 1.27 1.27)) hide)\n'
            f'    )\n'
            f'    (symbol "{name}_0_1"\n'
            f'      (rectangle (start -2.54 {half_h:.2f}) (end 2.54 {-half_h:.2f})\n'
            f'        (stroke (width 0.254) (type default))\n'
            f'        (fill (type background))\n'
            f'      )\n'
            f'    )\n'
            f'    (symbol "{name}_1_1"\n'
            + '\n'.join(pin_strs) + '\n'
            f'    )\n'
            f'  )'
        )
        self.lib_symbols.append(sym)

    def _make_sma_symbol(self, name="SMA"):
        """Create a 2-pin SMA connector symbol."""
        sym = (
            f'  (symbol "{name}" (in_bom yes) (on_board yes)\n'
            f'    (property "Reference" "J" (at 0 3.81 0)\n'
            f'      (effects (font (size 1.27 1.27)))\n'
            f'    )\n'
            f'    (property "Value" "{name}" (at 0 -3.81 0)\n'
            f'      (effects (font (size 1.27 1.27)))\n'
            f'    )\n'
            f'    (property "Footprint" "" (at 0 0 0)\n'
            f'      (effects (font (size 1.27 1.27)) hide)\n'
            f'    )\n'
            f'    (property "Datasheet" "" (at 0 0 0)\n'
            f'      (effects (font (size 1.27 1.27)) hide)\n'
            f'    )\n'
            f'    (symbol "{name}_0_1"\n'
            f'      (circle (center 0 0) (radius 2.54)\n'
            f'        (stroke (width 0.254) (type default))\n'
            f'        (fill (type background))\n'
            f'      )\n'
            f'    )\n'
            f'    (symbol "{name}_1_1"\n'
            f'      (pin passive line (at -5.08 0 0) (length 2.54)\n'
            f'        (name "Signal" (effects (font (size 1.016 1.016))))\n'
            f'        (number "1" (effects (font (size 1.016 1.016))))\n'
            f'      )\n'
            f'      (pin passive line (at 0 -5.08 90) (length 2.54)\n'
            f'        (name "GND" (effects (font (size 1.016 1.016))))\n'
            f'        (number "2" (effects (font (size 1.016 1.016))))\n'
            f'      )\n'
            f'    )\n'
            f'  )'
        )
        self.lib_symbols.append(sym)

    def _make_mosfet_symbol(self, name="BSS138"):
        """Create an N-channel MOSFET symbol."""
        sym = (
            f'  (symbol "{name}" (in_bom yes) (on_board yes)\n'
            f'    (property "Reference" "Q" (at 2.54 1.27 0)\n'
            f'      (effects (font (size 1.27 1.27)) (justify left))\n'
            f'    )\n'
            f'    (property "Value" "{name}" (at 2.54 -1.27 0)\n'
            f'      (effects (font (size 1.27 1.27)) (justify left))\n'
            f'    )\n'
            f'    (property "Footprint" "" (at 0 0 0)\n'
            f'      (effects (font (size 1.27 1.27)) hide)\n'
            f'    )\n'
            f'    (property "Datasheet" "" (at 0 0 0)\n'
            f'      (effects (font (size 1.27 1.27)) hide)\n'
            f'    )\n'
            f'    (symbol "{name}_0_1"\n'
            f'      (polyline (pts (xy 0 -2.54) (xy 0 2.54))\n'
            f'        (stroke (width 0.254) (type default))\n'
            f'      )\n'
            f'      (polyline (pts (xy 0.762 -1.524) (xy 0.762 -2.54) (xy 2.54 -2.54))\n'
            f'        (stroke (width 0.254) (type default))\n'
            f'      )\n'
            f'      (polyline (pts (xy 0.762 1.524) (xy 0.762 2.54) (xy 2.54 2.54))\n'
            f'        (stroke (width 0.254) (type default))\n'
            f'      )\n'
            f'      (polyline (pts (xy 0.762 -0.762) (xy 0.762 0.762))\n'
            f'        (stroke (width 0.254) (type default))\n'
            f'      )\n'
            f'    )\n'
            f'    (symbol "{name}_1_1"\n'
            f'      (pin input line (at -2.54 0 0) (length 2.54)\n'
            f'        (name "G" (effects (font (size 1.016 1.016))))\n'
            f'        (number "1" (effects (font (size 1.016 1.016))))\n'
            f'      )\n'
            f'      (pin passive line (at 2.54 2.54 180) (length 2.54)\n'
            f'        (name "D" (effects (font (size 1.016 1.016))))\n'
            f'        (number "2" (effects (font (size 1.016 1.016))))\n'
            f'      )\n'
            f'      (pin passive line (at 2.54 -2.54 180) (length 2.54)\n'
            f'        (name "S" (effects (font (size 1.016 1.016))))\n'
            f'        (number "3" (effects (font (size 1.016 1.016))))\n'
            f'      )\n'
            f'    )\n'
            f'  )'
        )
        self.lib_symbols.append(sym)

    def _make_diode_symbol(self, name="BAV99"):
        """Create a dual diode symbol (back-to-back for T/R protection)."""
        sym = (
            f'  (symbol "{name}" (in_bom yes) (on_board yes)\n'
            f'    (property "Reference" "D" (at 0 3.81 0)\n'
            f'      (effects (font (size 1.27 1.27)))\n'
            f'    )\n'
            f'    (property "Value" "{name}" (at 0 -3.81 0)\n'
            f'      (effects (font (size 1.27 1.27)))\n'
            f'    )\n'
            f'    (property "Footprint" "" (at 0 0 0)\n'
            f'      (effects (font (size 1.27 1.27)) hide)\n'
            f'    )\n'
            f'    (property "Datasheet" "" (at 0 0 0)\n'
            f'      (effects (font (size 1.27 1.27)) hide)\n'
            f'    )\n'
            f'    (symbol "{name}_0_1"\n'
            f'      (polyline (pts (xy -1.27 1.27) (xy 0 0) (xy 1.27 1.27))\n'
            f'        (stroke (width 0.254) (type default))\n'
            f'      )\n'
            f'      (polyline (pts (xy -1.27 -1.27) (xy 0 0) (xy 1.27 -1.27))\n'
            f'        (stroke (width 0.254) (type default))\n'
            f'      )\n'
            f'    )\n'
            f'    (symbol "{name}_1_1"\n'
            f'      (pin passive line (at 0 3.81 270) (length 2.54)\n'
            f'        (name "A" (effects (font (size 1.016 1.016))))\n'
            f'        (number "1" (effects (font (size 1.016 1.016))))\n'
            f'      )\n'
            f'      (pin passive line (at -3.81 0 0) (length 2.54)\n'
            f'        (name "COM" (effects (font (size 1.016 1.016))))\n'
            f'        (number "2" (effects (font (size 1.016 1.016))))\n'
            f'      )\n'
            f'      (pin passive line (at 0 -3.81 90) (length 2.54)\n'
            f'        (name "K" (effects (font (size 1.016 1.016))))\n'
            f'        (number "3" (effects (font (size 1.016 1.016))))\n'
            f'      )\n'
            f'    )\n'
            f'  )'
        )
        self.lib_symbols.append(sym)

    def _make_power_symbol(self, name, value):
        """Create a power flag/port symbol."""
        sym = (
            f'  (symbol "{name}" (power) (in_bom yes) (on_board yes)\n'
            f'    (property "Reference" "#PWR" (at 0 -2.54 0)\n'
            f'      (effects (font (size 1.27 1.27)) hide)\n'
            f'    )\n'
            f'    (property "Value" "{value}" (at 0 2.54 0)\n'
            f'      (effects (font (size 1.016 1.016)))\n'
            f'    )\n'
            f'    (property "Footprint" "" (at 0 0 0)\n'
            f'      (effects (font (size 1.27 1.27)) hide)\n'
            f'    )\n'
            f'    (property "Datasheet" "" (at 0 0 0)\n'
            f'      (effects (font (size 1.27 1.27)) hide)\n'
            f'    )\n'
            f'    (symbol "{name}_0_1"\n'
            f'      (polyline (pts (xy -1.27 1.27) (xy 0 2.54) (xy 1.27 1.27) (xy -1.27 1.27))\n'
            f'        (stroke (width 0) (type default))\n'
            f'        (fill (type value))\n'
            f'      )\n'
            f'    )\n'
            f'    (symbol "{name}_1_1"\n'
            f'      (pin power_in line (at 0 0 90) (length 1.27)\n'
            f'        (name "{value}" (effects (font (size 1.016 1.016))))\n'
            f'        (number "1" (effects (font (size 1.016 1.016))))\n'
            f'      )\n'
            f'    )\n'
            f'  )'
        )
        self.lib_symbols.append(sym)

    def _make_gnd_symbol(self):
        """Create GND power symbol."""
        sym = (
            '  (symbol "GND" (power) (in_bom yes) (on_board yes)\n'
            '    (property "Reference" "#PWR" (at 0 -3.81 0)\n'
            '      (effects (font (size 1.27 1.27)) hide)\n'
            '    )\n'
            '    (property "Value" "GND" (at 0 -2.54 0)\n'
            '      (effects (font (size 1.016 1.016)))\n'
            '    )\n'
            '    (property "Footprint" "" (at 0 0 0)\n'
            '      (effects (font (size 1.27 1.27)) hide)\n'
            '    )\n'
            '    (property "Datasheet" "" (at 0 0 0)\n'
            '      (effects (font (size 1.27 1.27)) hide)\n'
            '    )\n'
            '    (symbol "GND_0_1"\n'
            '      (polyline (pts (xy -1.27 0) (xy 1.27 0) (xy 0 -1.27) (xy -1.27 0))\n'
            '        (stroke (width 0) (type default))\n'
            '        (fill (type value))\n'
            '      )\n'
            '    )\n'
            '    (symbol "GND_1_1"\n'
            '      (pin power_in line (at 0 1.27 270) (length 1.27)\n'
            '        (name "GND" (effects (font (size 1.016 1.016))))\n'
            '        (number "1" (effects (font (size 1.016 1.016))))\n'
            '      )\n'
            '    )\n'
            '  )'
        )
        self.lib_symbols.append(sym)

    # ── Instance placement ──────────────────────────────────────

    def _next_ref(self, prefix):
        """Get next reference designator."""
        self._ref_count[prefix] = self._ref_count.get(prefix, 0) + 1
        return f"{prefix}{self._ref_count[prefix]}"

    def place_symbol(self, lib_name, x, y, ref_prefix="U", value=None,
                     rotation=0, mirror=False, ref_override=None):
        """Place a symbol instance on the schematic."""
        ref = ref_override or self._next_ref(ref_prefix)
        val = value or lib_name
        u = uid()
        mirror_str = ""
        if mirror:
            mirror_str = " (mirror y)"

        inst = (
            f'  (symbol (lib_id "{lib_name}") (at {x:.2f} {y:.2f} {rotation}){mirror_str}\n'
            f'    (uuid {u})\n'
            f'    (property "Reference" "{ref}" (at {x:.2f} {y - 5.08:.2f} 0)\n'
            f'      (effects (font (size 1.27 1.27)))\n'
            f'    )\n'
            f'    (property "Value" "{val}" (at {x:.2f} {y + 5.08:.2f} 0)\n'
            f'      (effects (font (size 1.27 1.27)))\n'
            f'    )\n'
            f'    (instances\n'
            f'      (project "red_pitaya_mux_board"\n'
            f'        (path "/e63e39d7-6ac0-4ffd-8aa3-1841a4541b3a"\n'
            f'          (reference "{ref}") (unit 1)\n'
            f'        )\n'
            f'      )\n'
            f'    )\n'
            f'  )'
        )
        self.instances.append(inst)
        return ref

    def add_wire(self, x1, y1, x2, y2):
        """Add a wire segment."""
        w = (
            f'  (wire (pts (xy {x1:.2f} {y1:.2f}) (xy {x2:.2f} {y2:.2f}))\n'
            f'    (stroke (width 0) (type default))\n'
            f'    (uuid {uid()})\n'
            f'  )'
        )
        self.wires.append(w)

    def add_label(self, text, x, y, rotation=0):
        """Add a net label."""
        lbl = (
            f'  (label "{text}" (at {x:.2f} {y:.2f} {rotation})\n'
            f'    (effects (font (size 1.27 1.27)))\n'
            f'    (uuid {uid()})\n'
            f'  )'
        )
        self.labels.append(lbl)

    def add_global_label(self, text, x, y, rotation=0, shape="bidirectional"):
        """Add a global net label."""
        lbl = (
            f'  (global_label "{text}" (shape {shape}) (at {x:.2f} {y:.2f} {rotation})\n'
            f'    (effects (font (size 1.27 1.27)))\n'
            f'    (uuid {uid()})\n'
            f'    (property "Intersheets" ""\n'
            f'      (at {x:.2f} {y:.2f} 0)\n'
            f'      (effects (font (size 1.27 1.27)) hide)\n'
            f'    )\n'
            f'  )'
        )
        self.global_labels.append(lbl)

    def add_text(self, text, x, y, size=2.54):
        """Add a text annotation."""
        t = (
            f'  (text "{text}" (at {x:.2f} {y:.2f} 0)\n'
            f'    (effects (font (size {size:.2f} {size:.2f})))\n'
            f'    (uuid {uid()})\n'
            f'  )'
        )
        self.texts.append(t)

    # ── Build the schematic ─────────────────────────────────────

    def build(self):
        """Define all library symbols."""
        # Power symbols
        self._make_power_symbol("+5V", "+5V")
        self._make_power_symbol("+3V3", "+3V3")
        self._make_power_symbol("+12V", "+12V")
        self._make_gnd_symbol()

        # SMA connector
        self._make_sma_symbol("SMA")

        # 74HC595 shift register
        self._make_ic_symbol("74HC595", [
            ("SER",   "14", "L", "input",   7.62),
            ("SRCLK", "11", "L", "input",   5.08),
            ("RCLK",  "12", "L", "input",   2.54),
            ("OE",    "13", "L", "input",   0.00),
            ("SRCLR", "10", "L", "input",  -2.54),
            ("VCC",   "16", "L", "power_in", -5.08),
            ("GND",    "8", "L", "power_in", -7.62),
            ("Q0",    "15", "R", "output",  7.62),
            ("Q1",     "1", "R", "output",  5.08),
            ("Q2",     "2", "R", "output",  2.54),
            ("Q3",     "3", "R", "output",  0.00),
            ("Q4",     "4", "R", "output", -2.54),
            ("Q5",     "5", "R", "output", -5.08),
            ("Q6",     "6", "R", "output", -7.62),
            ("Q7",     "7", "R", "output",-10.16),
        ], width=7.62, desc="8-bit shift register — TX element selection")

        # CD4051B analog mux
        self._make_ic_symbol("CD4051B", [
            ("X0",  "13", "L", "bidirectional",  8.89),
            ("X1",  "14", "L", "bidirectional",  6.35),
            ("X2",  "15", "L", "bidirectional",  3.81),
            ("X3",  "12", "L", "bidirectional",  1.27),
            ("X4",   "1", "L", "bidirectional", -1.27),
            ("X5",   "5", "L", "bidirectional", -3.81),
            ("X6",   "2", "L", "bidirectional", -6.35),
            ("X7",   "4", "L", "bidirectional", -8.89),
            ("COM",  "3", "R", "bidirectional",  5.08),
            ("A",   "11", "R", "input",          1.27),
            ("B",   "10", "R", "input",         -1.27),
            ("C",    "9", "R", "input",         -3.81),
            ("INH",  "6", "R", "input",         -6.35),
            ("VDD", "16", "R", "power_in",       8.89),
            ("VEE",  "7", "R", "power_in",      -8.89),
            ("VSS",  "8", "R", "power_in",     -11.43),
        ], width=7.62, desc="8:1 Analog mux — RX element selection")

        # BSS138 MOSFET
        self._make_mosfet_symbol("BSS138")

        # BAV99 protection diode
        self._make_diode_symbol("BAV99")

        # LM7805 regulator
        self._make_ic_symbol("LM7805", [
            ("IN",  "1", "L", "input",    2.54),
            ("GND", "2", "L", "power_in", 0.00),
            ("OUT", "3", "R", "output",   2.54),
        ], width=5.08, desc="5V voltage regulator")

        # AMS1117-3.3
        self._make_ic_symbol("AMS1117-3V3", [
            ("IN",   "3", "L", "input",    2.54),
            ("GND",  "1", "L", "power_in", 0.00),
            ("OUT",  "2", "R", "output",   2.54),
        ], width=5.08, desc="3.3V LDO regulator")

        # OPA657 LNA op-amp
        self._make_ic_symbol("OPA657", [
            ("IN+", "3", "L", "input",    2.54),
            ("IN-", "2", "L", "input",    0.00),
            ("V+",  "7", "L", "power_in", -2.54),
            ("V-",  "4", "L", "power_in", -5.08),
            ("OUT", "6", "R", "output",   2.54),
        ], width=5.08, desc="Wideband LNA op-amp (1.6 GHz)")

        # Generic resistor and capacitor
        self._make_2pin_symbol("R", "1", "2", "Resistor")
        self._make_2pin_symbol("C", "1", "2", "Capacitor")

        # GPIO header (2x10)
        self._make_connector_symbol("Conn_2x10", 20, "Red Pitaya GPIO Extension E1")

    def populate(self):
        """Place all component instances and labels."""
        # ── Section headers ──
        self.add_text("RED PITAYA MUX BOARD — Rev 1", 25, 15, 3.81)
        self.add_text("8-Element Ultrasound Array Interface", 25, 22, 2.54)
        self.add_text("TX SWITCH ARRAY", 85, 35, 2.54)
        self.add_text("ELEMENT CONNECTORS", 155, 35, 2.54)
        self.add_text("RX MUX + LNA", 230, 35, 2.54)
        self.add_text("POWER SUPPLY", 85, 215, 2.54)
        self.add_text("CONTROL (GPIO)", 25, 35, 2.54)

        # ═══════════════════════════════════════════════════════
        # CONNECTORS — Left side
        # ═══════════════════════════════════════════════════════

        # GPIO header (J1)
        self.place_symbol("Conn_2x10", 30, 100, "J", "RP_GPIO_E1", ref_override="J1")
        # Label key GPIO pins
        self.add_global_label("SER",    24.92, 75.69, 180, "input")   # Pin 7
        self.add_global_label("SRCLK",  24.92, 78.23, 180, "input")   # Pin 8
        self.add_global_label("RCLK",   24.92, 80.77, 180, "input")   # Pin 9
        self.add_global_label("MUX_A",  24.92, 83.31, 180, "input")   # Pin 10
        self.add_global_label("MUX_B",  24.92, 85.85, 180, "input")   # Pin 11
        self.add_global_label("MUX_C",  24.92, 88.39, 180, "input")   # Pin 12
        self.add_global_label("TRIGGER",24.92, 90.93, 180, "input")   # Pin 13

        # TX input SMA (J2)
        self.place_symbol("SMA", 30, 155, "J", "TX_IN", ref_override="J2")
        self.add_global_label("TX_BUS", 24.92, 155, 180, "bidirectional")

        # RX output SMAs (J11, J12)
        self.place_symbol("SMA", 30, 175, "J", "RX0_OUT", ref_override="J11")
        self.add_global_label("RX0_OUT", 24.92, 175, 180, "output")

        self.place_symbol("SMA", 30, 195, "J", "RX1_OUT", ref_override="J12")
        self.add_global_label("RX1_OUT", 24.92, 195, 180, "output")

        # ═══════════════════════════════════════════════════════
        # 74HC595 SHIFT REGISTER — TX element control
        # ═══════════════════════════════════════════════════════

        self.place_symbol("74HC595", 85, 75, "U", "74HC595", ref_override="U1")
        # Control inputs
        self.add_global_label("SER",    77.38, 67.38, 180, "input")
        self.add_global_label("SRCLK",  77.38, 69.92, 180, "input")
        self.add_global_label("RCLK",   77.38, 72.46, 180, "input")
        # OE tied to GND (always enabled)
        self.add_global_label("GND", 77.38, 75.00, 180, "passive")
        # SRCLR tied to +5V (never clear)
        self.add_global_label("+5V", 77.38, 77.54, 180, "passive")
        self.add_global_label("+5V", 77.38, 80.08, 180, "passive")
        self.add_global_label("GND", 77.38, 82.62, 180, "passive")

        # Outputs to MOSFET gates
        for i in range(8):
            y = 67.38 + i * 2.54
            self.add_global_label(f"GATE_{i}", 92.62, y, 0, "output")

        # ═══════════════════════════════════════════════════════
        # MOSFETs Q1-Q8 — TX switches
        # ═══════════════════════════════════════════════════════

        for i in range(8):
            x = 120
            y = 50 + i * 17.78
            self.place_symbol("BSS138", x, y, "Q", "BSS138", ref_override=f"Q{i+1}")
            # Gate from shift register
            self.add_global_label(f"GATE_{i}", x - 2.54, y, 180, "input")
            # Drain to element
            self.add_global_label(f"EL{i}", x + 2.54, y + 2.54, 0, "bidirectional")
            # Source from TX bus
            self.add_global_label("TX_BUS", x + 2.54, y - 2.54, 0, "passive")

        # ═══════════════════════════════════════════════════════
        # ELEMENT CONNECTORS (J3-J10) — Center
        # ═══════════════════════════════════════════════════════

        for i in range(8):
            x = 155
            y = 50 + i * 17.78
            ref = f"J{i+3}"
            self.place_symbol("SMA", x, y, "J", f"EL{i}", ref_override=ref)
            self.add_global_label(f"EL{i}", x - 5.08, y, 180, "bidirectional")

        # ═══════════════════════════════════════════════════════
        # T/R PROTECTION DIODES (D1-D8)
        # ═══════════════════════════════════════════════════════

        for i in range(8):
            x = 180
            y = 50 + i * 17.78
            self.place_symbol("BAV99", x, y, "D", "BAV99", ref_override=f"D{i+1}")
            self.add_global_label(f"EL{i}", x - 3.81, y, 180, "bidirectional")
            self.add_global_label("+5V", x, y - 3.81, 270, "passive")
            self.add_global_label("GND", x, y + 3.81, 90, "passive")

        # ═══════════════════════════════════════════════════════
        # RX MUX — CD4051B × 2
        # ═══════════════════════════════════════════════════════

        # U2 — RX Channel 0
        self.place_symbol("CD4051B", 215, 75, "U", "CD4051B_RX0", ref_override="U2")
        for i in range(8):
            y = 75 - 8.89 + i * (-2.54 if i < 4 else 2.54)  # approximate pin Y
            # Map element inputs
        # Element connections to mux inputs
        el_pin_y = [66.11, 68.65, 71.19, 73.73, 76.27, 78.81, 81.35, 83.89]
        for i in range(8):
            self.add_global_label(f"EL{i}", 207.38, el_pin_y[i], 180, "bidirectional")

        # Mux control
        self.add_global_label("MUX_A", 222.62, 73.73, 0, "input")
        self.add_global_label("MUX_B", 222.62, 76.27, 0, "input")
        self.add_global_label("MUX_C", 222.62, 78.81, 0, "input")
        self.add_global_label("GND",   222.62, 81.35, 0, "passive")   # INH
        self.add_global_label("+5V",   222.62, 66.11, 0, "passive")   # VDD
        self.add_global_label("GND",   222.62, 83.89, 0, "passive")   # VEE
        self.add_global_label("GND",   222.62, 86.43, 0, "passive")   # VSS
        self.add_global_label("MUX0_COM", 222.62, 69.92, 0, "output") # COM

        # U3 — RX Channel 1
        self.place_symbol("CD4051B", 215, 120, "U", "CD4051B_RX1", ref_override="U3")
        el_pin_y_u3 = [y + 45 for y in el_pin_y]
        for i in range(8):
            self.add_global_label(f"EL{i}", 207.38, el_pin_y_u3[i], 180, "bidirectional")

        self.add_global_label("MUX_A", 222.62, 118.73, 0, "input")
        self.add_global_label("MUX_B", 222.62, 121.27, 0, "input")
        self.add_global_label("MUX_C", 222.62, 123.81, 0, "input")
        self.add_global_label("GND",   222.62, 126.35, 0, "passive")
        self.add_global_label("+5V",   222.62, 111.11, 0, "passive")
        self.add_global_label("GND",   222.62, 128.89, 0, "passive")
        self.add_global_label("GND",   222.62, 131.43, 0, "passive")
        self.add_global_label("MUX1_COM", 222.62, 114.92, 0, "output")

        # ═══════════════════════════════════════════════════════
        # LNA — OPA657 × 2
        # ═══════════════════════════════════════════════════════

        # U4 — LNA Channel 0
        self.place_symbol("OPA657", 260, 75, "U", "OPA657_RX0", ref_override="U4")
        self.add_global_label("MUX0_COM", 254.92, 72.46, 180, "input")   # IN+
        self.add_global_label("+5V",      254.92, 77.54, 180, "passive")  # V+
        self.add_global_label("GND",      254.92, 80.08, 180, "passive")  # V-
        self.add_global_label("RX0_OUT",  265.08, 72.46, 0, "output")    # OUT

        # U5 — LNA Channel 1
        self.place_symbol("OPA657", 260, 120, "U", "OPA657_RX1", ref_override="U5")
        self.add_global_label("MUX1_COM", 254.92, 117.46, 180, "input")
        self.add_global_label("+5V",      254.92, 122.54, 180, "passive")
        self.add_global_label("GND",      254.92, 125.08, 180, "passive")
        self.add_global_label("RX1_OUT",  265.08, 117.46, 0, "output")

        # ═══════════════════════════════════════════════════════
        # POWER SUPPLY — Bottom section
        # ═══════════════════════════════════════════════════════

        # Power input connector
        self.place_symbol("SMA", 50, 235, "J", "12V_IN", ref_override="J13")
        self.add_global_label("+12V", 44.92, 235, 180, "input")

        # LM7805 (U6)
        self.place_symbol("LM7805", 100, 235, "U", "LM7805", ref_override="U6")
        self.add_global_label("+12V", 94.92, 232.46, 180, "input")
        self.add_global_label("GND",  94.92, 235.00, 180, "passive")
        self.add_global_label("+5V",  105.08, 232.46, 0, "output")

        # AMS1117-3.3 (U7)
        self.place_symbol("AMS1117-3V3", 155, 235, "U", "AMS1117-3V3", ref_override="U7")
        self.add_global_label("+5V",  149.92, 232.46, 180, "input")
        self.add_global_label("GND",  149.92, 235.00, 180, "passive")
        self.add_global_label("+3V3", 160.08, 232.46, 0, "output")

        # Decoupling caps annotations
        self.add_text("C_bypass: 100nF on each IC VCC", 85, 250, 1.5)
        self.add_text("C_bulk: 10uF on each power rail", 85, 255, 1.5)

    def render(self):
        """Render the complete .kicad_sch file."""
        sheet_uuid = "e63e39d7-6ac0-4ffd-8aa3-1841a4541b3a"

        header = (
            f'(kicad_sch\n'
            f'  (version 20231120)\n'
            f'  (generator "python_gen")\n'
            f'  (generator_version "1.0")\n'
            f'  (uuid {sheet_uuid})\n'
            f'  (paper "A3")\n'
            f'  (title_block\n'
            f'    (title "Red Pitaya 8-Element Ultrasound Mux Board")\n'
            f'    (date "2026-03-27")\n'
            f'    (rev "1.0")\n'
            f'    (company "Home Workshop")\n'
            f'    (comment 1 "8-element array interface for STEMlab 125-14")\n'
            f'    (comment 2 "TX: 74HC595 + BSS138 switches")\n'
            f'    (comment 3 "RX: CD4051B mux + OPA657 LNA")\n'
            f'    (comment 4 "See DESIGN.md for full documentation")\n'
            f'  )\n'
        )

        # Lib symbols section
        lib_section = '  (lib_symbols\n' + '\n'.join(self.lib_symbols) + '\n  )\n'

        # All placed elements
        elements = '\n'.join(
            self.instances + self.wires + self.labels +
            self.global_labels + self.texts
        )

        footer = ')\n'

        return header + lib_section + elements + '\n' + footer


def main():
    gen = SchematicGenerator()
    gen.build()
    gen.populate()
    sch = gen.render()

    outpath = "red_pitaya_mux_board.kicad_sch"
    with open(outpath, 'w') as f:
        f.write(sch)
    print(f"✅ Generated: {outpath}")
    print(f"   File size: {len(sch):,} bytes")
    print(f"   Components: {len(gen.instances)}")
    print(f"   Labels: {len(gen.labels) + len(gen.global_labels)}")
    print(f"   Wires: {len(gen.wires)}")
    print(f"\nOpen in KiCad 8 to verify and complete wiring.")
    print("All nets use global labels — ERC should show connectivity.")


if __name__ == "__main__":
    main()
