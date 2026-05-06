#!/usr/bin/env python3
"""
TurboQuant Clean Symbol Library Generator
==========================================

Generates a self-contained KiCad 9.0 symbol library with embedded graphics
for all TurboQuant components. No external dependencies.

Usage:
    python3 generate_symbol_library.py
    
Output:
    turboquant_library.kicad_sym - Complete symbol library
    sym-lib-table - Library table with absolute path

Author: Research Project
Date: April 17, 2026
"""

import os
import sys
from pathlib import Path
from datetime import datetime


def generate_symbol_library(output_path: str = "turboquant_library.kicad_sym"):
    """
    Generate complete KiCad 9.0 symbol library with embedded graphics.
    """
    
    lines = []
    
    # Header
    lines.append("(kicad_symbol_lib")
    lines.append(f"  (version 20250114)")
    lines.append(f"  (generator \"turboquant_generator\")")
    lines.append(f"  (generator_version \"1.0\")")
    lines.append("")
    
    #====================================================================
    # Power Symbols
    #====================================================================
    
    # +12V Power Symbol
    lines.append("  (symbol \"power:+12V\" (power)")
    lines.append("    (pin_names (offset 0))")
    lines.append("    (exclude_from_sim no) (in_bom no) (on_board no)")
    lines.append("    (property \"Reference\" \"#PWR\" (at 0 -3.81 0)")
    lines.append("      (effects (font (size 1.27 1.27)) hide)")
    lines.append("    )")
    lines.append("    (property \"Value\" \"+12V\" (at 0 3.556 0)")
    lines.append("      (effects (font (size 1.27 1.27)))")
    lines.append("    )")
    lines.append("    (property \"Footprint\" \"\" (at 0 0 0)")
    lines.append("      (effects (font (size 1.27 1.27)) hide)")
    lines.append("    )")
    lines.append("    (symbol \"+12V_0_0\"")
    lines.append("      (polyline")
    lines.append("        (pts (xy 0 0) (xy 0 2.54))")
    lines.append("        (stroke (width 0)) (fill (type none))")
    lines.append("      )")
    lines.append("      (polyline")
    lines.append("        (pts (xy -1.27 2.54) (xy 1.27 2.54))")
    lines.append("        (stroke (width 0)) (fill (type none))")
    lines.append("      )")
    lines.append("      (polyline")
    lines.append("        (pts (xy -0.762 3.048) (xy 0.762 3.048))")
    lines.append("        (stroke (width 0)) (fill (type none))")
    lines.append("      )")
    lines.append("      (polyline")
    lines.append("        (pts (xy -0.254 3.556) (xy 0.254 3.556))")
    lines.append("        (stroke (width 0)) (fill (type none))")
    lines.append("      )")
    lines.append("    )")
    lines.append("    (symbol \"+12V_1_1\"")
    lines.append("      (pin power_in line (at 0 0 270) (length 0) hide")
    lines.append("        (name \"~\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"1\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("    )")
    lines.append("  )")
    lines.append("")
    
    # +5V Power Symbol
    lines.append("  (symbol \"power:+5V\" (power)")
    lines.append("    (pin_names (offset 0))")
    lines.append("    (exclude_from_sim no) (in_bom no) (on_board no)")
    lines.append("    (property \"Reference\" \"#PWR\" (at 0 -3.81 0)")
    lines.append("      (effects (font (size 1.27 1.27)) hide)")
    lines.append("    )")
    lines.append("    (property \"Value\" \"+5V\" (at 0 3.556 0)")
    lines.append("      (effects (font (size 1.27 1.27)))")
    lines.append("    )")
    lines.append("    (property \"Footprint\" \"\" (at 0 0 0)")
    lines.append("      (effects (font (size 1.27 1.27)) hide)")
    lines.append("    )")
    lines.append("    (symbol \"+5V_0_0\"")
    lines.append("      (polyline")
    lines.append("        (pts (xy 0 0) (xy 0 2.54))")
    lines.append("        (stroke (width 0)) (fill (type none))")
    lines.append("      )")
    lines.append("      (polyline")
    lines.append("        (pts (xy -1.27 2.54) (xy 1.27 2.54))")
    lines.append("        (stroke (width 0)) (fill (type none))")
    lines.append("      )")
    lines.append("      (polyline")
    lines.append("        (pts (xy -0.762 3.048) (xy 0.762 3.048))")
    lines.append("        (stroke (width 0)) (fill (type none))")
    lines.append("      )")
    lines.append("    )")
    lines.append("    (symbol \"+5V_1_1\"")
    lines.append("      (pin power_in line (at 0 0 270) (length 0) hide")
    lines.append("        (name \"~\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"1\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("    )")
    lines.append("  )")
    lines.append("")
    
    # +3.3V Power Symbol
    lines.append("  (symbol \"power:+3V3\" (power)")
    lines.append("    (pin_names (offset 0))")
    lines.append("    (exclude_from_sim no) (in_bom no) (on_board no)")
    lines.append("    (property \"Reference\" \"#PWR\" (at 0 -3.81 0)")
    lines.append("      (effects (font (size 1.27 1.27)) hide)")
    lines.append("    )")
    lines.append("    (property \"Value\" \"+3V3\" (at 0 3.556 0)")
    lines.append("      (effects (font (size 1.27 1.27)))")
    lines.append("    )")
    lines.append("    (property \"Footprint\" \"\" (at 0 0 0)")
    lines.append("      (effects (font (size 1.27 1.27)) hide)")
    lines.append("    )")
    lines.append("    (symbol \"+3V3_0_0\"")
    lines.append("      (polyline")
    lines.append("        (pts (xy 0 0) (xy 0 2.54))")
    lines.append("        (stroke (width 0)) (fill (type none))")
    lines.append("      )")
    lines.append("      (polyline")
    lines.append("        (pts (xy -1.27 2.54) (xy 1.27 2.54))")
    lines.append("        (stroke (width 0)) (fill (type none))")
    lines.append("      )")
    lines.append("    )")
    lines.append("    (symbol \"+3V3_1_1\"")
    lines.append("      (pin power_in line (at 0 0 270) (length 0) hide")
    lines.append("        (name \"~\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"1\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("    )")
    lines.append("  )")
    lines.append("")
    
    # GND Power Symbol
    lines.append("  (symbol \"power:GND\" (power)")
    lines.append("    (pin_names (offset 0))")
    lines.append("    (exclude_from_sim no) (in_bom no) (on_board no)")
    lines.append("    (property \"Reference\" \"#PWR\" (at 0 -6.35 0)")
    lines.append("      (effects (font (size 1.27 1.27)) hide)")
    lines.append("    )")
    lines.append("    (property \"Value\" \"GND\" (at 0 -3.81 0)")
    lines.append("      (effects (font (size 1.27 1.27)))")
    lines.append("    )")
    lines.append("    (property \"Footprint\" \"\" (at 0 0 0)")
    lines.append("      (effects (font (size 1.27 1.27)) hide)")
    lines.append("    )")
    lines.append("    (symbol \"GND_0_0\"")
    lines.append("      (polyline")
    lines.append("        (pts (xy 0 0) (xy 0 -1.905))")
    lines.append("        (stroke (width 0)) (fill (type none))")
    lines.append("      )")
    lines.append("      (polyline")
    lines.append("        (pts (xy -1.27 -1.905) (xy 1.27 -1.905))")
    lines.append("        (stroke (width 0)) (fill (type none))")
    lines.append("      )")
    lines.append("      (polyline")
    lines.append("        (pts (xy -0.762 -2.667) (xy 0.762 -2.667))")
    lines.append("        (stroke (width 0)) (fill (type none))")
    lines.append("      )")
    lines.append("      (polyline")
    lines.append("        (pts (xy -0.254 -3.429) (xy 0.254 -3.429))")
    lines.append("        (stroke (width 0)) (fill (type none))")
    lines.append("      )")
    lines.append("    )")
    lines.append("    (symbol \"GND_1_1\"")
    lines.append("      (pin power_in line (at 0 0 90) (length 0) hide")
    lines.append("        (name \"~\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"1\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("    )")
    lines.append("  )")
    lines.append("")
    
    #====================================================================
    # Passive Components
    #====================================================================
    
    # Resistor
    lines.append("  (symbol \"Device:R\" (in_bom yes) (on_board yes)")
    lines.append("    (property \"Reference\" \"R\" (at 2.032 0 90)")
    lines.append("      (effects (font (size 1.27 1.27)))")
    lines.append("    )")
    lines.append("    (property \"Value\" \"R\" (at 0 0 90)")
    lines.append("      (effects (font (size 1.27 1.27)) hide)")
    lines.append("    )")
    lines.append("    (property \"Footprint\" \"\" (at -1.778 0 90)")
    lines.append("      (effects (font (size 1.27 1.27)) hide)")
    lines.append("    )")
    lines.append("    (symbol \"R_0_1\"")
    lines.append("      (rectangle (start -1.016 -2.54) (end 1.016 2.54)")
    lines.append("        (stroke (width 0.254)) (fill (type none))")
    lines.append("      )")
    lines.append("    )")
    lines.append("    (symbol \"R_1_1\"")
    lines.append("      (pin passive line (at 0 3.81 270) (length 1.27)")
    lines.append("        (name \"~\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"1\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("      (pin passive line (at 0 -3.81 90) (length 1.27)")
    lines.append("        (name \"~\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"2\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("    )")
    lines.append("  )")
    lines.append("")
    
    # Capacitor
    lines.append("  (symbol \"Device:C\" (in_bom yes) (on_board yes)")
    lines.append("    (property \"Reference\" \"C\" (at 0.635 2.54 0)")
    lines.append("      (effects (font (size 1.27 1.27)))")
    lines.append("    )")
    lines.append("    (property \"Value\" \"C\" (at 0.635 -2.54 0)")
    lines.append("      (effects (font (size 1.27 1.27)) hide)")
    lines.append("    )")
    lines.append("    (property \"Footprint\" \"\" (at 0 -5.842 0)")
    lines.append("      (effects (font (size 1.27 1.27)) hide)")
    lines.append("    )")
    lines.append("    (symbol \"C_0_0\"")
    lines.append("      (polyline")
    lines.append("        (pts (xy -2.032 -0.762) (xy 2.032 -0.762))")
    lines.append("        (stroke (width 0.254)) (fill (type none))")
    lines.append("      )")
    lines.append("      (polyline")
    lines.append("        (pts (xy -2.032 0.762) (xy 2.032 0.762))")
    lines.append("        (stroke (width 0.254)) (fill (type none))")
    lines.append("      )")
    lines.append("    )")
    lines.append("    (symbol \"C_1_1\"")
    lines.append("      (pin passive line (at 0 3.81 270) (length 2.794)")
    lines.append("        (name \"~\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"1\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("      (pin passive line (at 0 -3.81 90) (length 2.794)")
    lines.append("        (name \"~\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"2\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("    )")
    lines.append("  )")
    lines.append("")
    
    # LED
    lines.append("  (symbol \"Device:LED\" (in_bom yes) (on_board yes)")
    lines.append("    (property \"Reference\" \"D\" (at -1.27 -3.81 90)")
    lines.append("      (effects (font (size 1.27 1.27)))")
    lines.append("    )")
    lines.append("    (property \"Value\" \"LED\" (at -1.27 3.81 90)")
    lines.append("      (effects (font (size 1.27 1.27)) hide)")
    lines.append("    )")
    lines.append("    (property \"Footprint\" \"\" (at 0 -5.08 0)")
    lines.append("      (effects (font (size 1.27 1.27)) hide)")
    lines.append("    )")
    lines.append("    (symbol \"LED_0_1\"")
    lines.append("      (polyline")
    lines.append("        (pts (xy -1.27 -1.27) (xy -1.27 1.27))")
    lines.append("        (stroke (width 0.254)) (fill (type none))")
    lines.append("      )")
    lines.append("      (polyline")
    lines.append("        (pts (xy 1.27 0) (xy -1.27 0))")
    lines.append("        (stroke (width 0)) (fill (type none))")
    lines.append("      )")
    lines.append("      (polyline")
    lines.append("        (pts (xy -1.27 -1.27) (xy 1.27 0) (xy -1.27 1.27))")
    lines.append("        (stroke (width 0.254)) (fill (type none))")
    lines.append("      )")
    lines.append("      (polyline")
    lines.append("        (pts (xy 0 1.27) (xy 1.905 2.54))")
    lines.append("        (stroke (width 0)) (fill (type none))")
    lines.append("      )")
    lines.append("      (polyline")
    lines.append("        (pts (xy 1.27 1.27) (xy 3.175 2.54))")
    lines.append("        (stroke (width 0)) (fill (type none))")
    lines.append("      )")
    lines.append("    )")
    lines.append("    (symbol \"LED_1_1\"")
    lines.append("      (pin passive line (at -3.81 0 0) (length 2.54)")
    lines.append("        (name \"K\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"1\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("      (pin passive line (at 3.81 0 180) (length 2.54)")
    lines.append("        (name \"A\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"2\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("    )")
    lines.append("  )")
    lines.append("")
    
    #====================================================================
    # Digital IC: 74HC595 Shift Register
    #====================================================================
    
    lines.append("  (symbol \"74xx:74HC595\" (in_bom yes) (on_board yes)")
    lines.append("    (property \"Reference\" \"U\" (at -7.62 13.97 0)")
    lines.append("      (effects (font (size 1.27 1.27)))")
    lines.append("    )")
    lines.append("    (property \"Value\" \"74HC595\" (at 7.62 13.97 0)")
    lines.append("      (effects (font (size 1.27 1.27)))")
    lines.append("    )")
    lines.append("    (property \"Footprint\" \"Package_SO:SOIC-16_3.9x9.9mm_P1.27mm\" (at 0 -15.24 0)")
    lines.append("      (effects (font (size 1.27 1.27)) hide)")
    lines.append("    )")
    lines.append("    (symbol \"74HC595_0_0\"")
    lines.append("      (rectangle (start -10.16 12.7) (end 10.16 -12.7)")
    lines.append("        (stroke (width 0.254)) (fill (type background))")
    lines.append("      )")
    lines.append("    )")
    lines.append("    (symbol \"74HC595_1_1\"")
    # Pins 1-8 (left side)
    lines.append("      (pin input line (at -12.7 10.16 0) (length 2.54)")
    lines.append("        (name \"QB\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"1\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("      (pin input line (at -12.7 7.62 0) (length 2.54)")
    lines.append("        (name \"QC\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"2\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("      (pin input line (at -12.7 5.08 0) (length 2.54)")
    lines.append("        (name \"QD\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"3\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("      (pin input line (at -12.7 2.54 0) (length 2.54)")
    lines.append("        (name \"QE\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"4\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("      (pin input line (at -12.7 0 0) (length 2.54)")
    lines.append("        (name \"QF\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"5\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("      (pin input line (at -12.7 -2.54 0) (length 2.54)")
    lines.append("        (name \"QG\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"6\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("      (pin input line (at -12.7 -5.08 0) (length 2.54)")
    lines.append("        (name \"QH\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"7\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("      (pin power_in line (at -12.7 -7.62 0) (length 2.54)")
    lines.append("        (name \"GND\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"8\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    # Pins 9-16 (right side, bottom to top)
    lines.append("      (pin output line (at 12.7 -7.62 180) (length 2.54)")
    lines.append("        (name \"QH'\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"9\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("      (pin input line (at 12.7 -5.08 180) (length 2.54)")
    lines.append("        (name \"SRCLR\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"10\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("      (pin input line (at 12.7 -2.54 180) (length 2.54)")
    lines.append("        (name \"SRCLK\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"11\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("      (pin input line (at 12.7 0 180) (length 2.54)")
    lines.append("        (name \"RCLK\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"12\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("      (pin input line (at 12.7 2.54 180) (length 2.54)")
    lines.append("        (name \"OE\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"13\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("      (pin input line (at 12.7 5.08 180) (length 2.54)")
    lines.append("        (name \"SER\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"14\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("      (pin output line (at 12.7 7.62 180) (length 2.54)")
    lines.append("        (name \"QA\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"15\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("      (pin power_in line (at 12.7 10.16 180) (length 2.54)")
    lines.append("        (name \"VCC\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"16\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("    )")
    lines.append("  )")
    lines.append("")
    
    #====================================================================
    # Analog Mux: CD4051B
    #====================================================================
    
    lines.append("  (symbol \"Analog_Mux:CD4051B\" (in_bom yes) (on_board yes)")
    lines.append("    (property \"Reference\" \"U\" (at -7.62 13.97 0)")
    lines.append("      (effects (font (size 1.27 1.27)))")
    lines.append("    )")
    lines.append("    (property \"Value\" \"CD4051B\" (at 7.62 13.97 0)")
    lines.append("      (effects (font (size 1.27 1.27)))")
    lines.append("    )")
    lines.append("    (property \"Footprint\" \"Package_SO:SOIC-16_3.9x9.9mm_P1.27mm\" (at 0 -15.24 0)")
    lines.append("      (effects (font (size 1.27 1.27)) hide)")
    lines.append("    )")
    lines.append("    (symbol \"CD4051B_0_0\"")
    lines.append("      (rectangle (start -10.16 12.7) (end 10.16 -12.7)")
    lines.append("        (stroke (width 0.254)) (fill (type background))")
    lines.append("      )")
    lines.append("    )")
    lines.append("    (symbol \"CD4051B_1_1\"")
    lines.append("      (pin passive line (at -12.7 10.16 0) (length 2.54)")
    lines.append("        (name \"CH4\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"1\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("      (pin passive line (at -12.7 7.62 0) (length 2.54)")
    lines.append("        (name \"CH6\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"2\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("      (pin passive line (at -12.7 5.08 0) (length 2.54)")
    lines.append("        (name \"COM\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"3\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("      (pin passive line (at -12.7 2.54 0) (length 2.54)")
    lines.append("        (name \"CH7\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"4\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("      (pin passive line (at -12.7 0 0) (length 2.54)")
    lines.append("        (name \"CH5\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"5\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("      (pin input line (at -12.7 -2.54 0) (length 2.54)")
    lines.append("        (name \"INH\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"6\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("      (pin power_in line (at -12.7 -5.08 0) (length 2.54)")
    lines.append("        (name \"VEE\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"7\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("      (pin power_in line (at -12.7 -7.62 0) (length 2.54)")
    lines.append("        (name \"VSS\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"8\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    # Right side
    lines.append("      (pin passive line (at 12.7 -7.62 180) (length 2.54)")
    lines.append("        (name \"CH2\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"13\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("      (pin passive line (at 12.7 -5.08 180) (length 2.54)")
    lines.append("        (name \"CH1\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"14\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("      (pin passive line (at 12.7 -2.54 180) (length 2.54)")
    lines.append("        (name \"CH0\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"11\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("      (pin input line (at 12.7 0 180) (length 2.54)")
    lines.append("        (name \"C\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"9\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("      (pin input line (at 12.7 2.54 180) (length 2.54)")
    lines.append("        (name \"B\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"10\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("      (pin input line (at 12.7 5.08 180) (length 2.54)")
    lines.append("        (name \"A\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"12\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("      (pin passive line (at 12.7 7.62 180) (length 2.54)")
    lines.append("        (name \"CH3\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"15\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("      (pin power_in line (at 12.7 10.16 180) (length 2.54)")
    lines.append("        (name \"VDD\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"16\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("    )")
    lines.append("  )")
    lines.append("")
    
    #====================================================================
    # Connectors
    #====================================================================
    
    # 2x10 Pin Header (Red Pitaya E1)
    lines.append("  (symbol \"Connector:Conn_02x10_Counter_Clockwise\" (in_bom yes) (on_board yes)")
    lines.append("    (pin_names (offset 1.016) hide)")
    lines.append("    (property \"Reference\" \"J\" (at 1.27 13.97 0)")
    lines.append("      (effects (font (size 1.27 1.27)))")
    lines.append("    )")
    lines.append("    (property \"Value\" \"Conn_02x10\" (at 1.27 -16.51 0)")
    lines.append("      (effects (font (size 1.27 1.27)))")
    lines.append("    )")
    lines.append("    (property \"Footprint\" \"Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical\" (at 0 0 0)")
    lines.append("      (effects (font (size 1.27 1.27)) hide)")
    lines.append("    )")
    lines.append("    (symbol \"Conn_02x10_Counter_Clockwise_0_0\"")
    lines.append("      (rectangle (start -1.27 12.7) (end 3.81 -15.24)")
    lines.append("        (stroke (width 0.254)) (fill (type background))")
    lines.append("      )")
    lines.append("    )")
    lines.append("    (symbol \"Conn_02x10_Counter_Clockwise_1_1\"")
    # Left side pins (1-10)
    for i in range(10):
        y = 11.43 - i * 2.54
        lines.append(f"      (pin passive line (at -5.08 {y:.2f} 0) (length 3.81)")
        lines.append(f"        (name \"Pin_{i+1}\" (effects (font (size 1.27 1.27))))")
        lines.append(f"        (number \"{i+1}\" (effects (font (size 1.27 1.27))))")
        lines.append("      )")
    # Right side pins (20-11)
    for i in range(10):
        y = 11.43 - i * 2.54
        pin_num = 20 - i
        lines.append(f"      (pin passive line (at 8.89 {y:.2f} 180) (length 3.81)")
        lines.append(f"        (name \"Pin_{pin_num}\" (effects (font (size 1.27 1.27))))")
        lines.append(f"        (number \"{pin_num}\" (effects (font (size 1.27 1.27))))")
        lines.append("      )")
    lines.append("    )")
    lines.append("  )")
    lines.append("")
    
    # SMA Connector
    lines.append("  (symbol \"Connector:SMA\" (in_bom yes) (on_board yes)")
    lines.append("    (pin_names hide)")
    lines.append("    (property \"Reference\" \"J\" (at 0 2.54 0)")
    lines.append("      (effects (font (size 1.27 1.27)))")
    lines.append("    )")
    lines.append("    (property \"Value\" \"SMA\" (at 0 -2.54 0)")
    lines.append("      (effects (font (size 1.27 1.27)))")
    lines.append("    )")
    lines.append("    (property \"Footprint\" \"Connector_Coaxial:SMA_EDGE\" (at 0 0 0)")
    lines.append("      (effects (font (size 1.27 1.27)) hide)")
    lines.append("    )")
    lines.append("    (symbol \"SMA_0_0\"")
    lines.append("      (circle (center 0 0) (radius 1.27)")
    lines.append("        (stroke (width 0.254)) (fill (type none))")
    lines.append("      )")
    lines.append("      (polyline")
    lines.append("        (pts (xy -1.27 0) (xy -2.54 0))")
    lines.append("        (stroke (width 0)) (fill (type none))")
    lines.append("      )")
    lines.append("    )")
    lines.append("    (symbol \"SMA_1_1\"")
    lines.append("      (pin passive line (at 0 5.08 270) (length 2.54)")
    lines.append("        (name \"Sig\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"1\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("      (pin passive line (at 0 -5.08 90) (length 2.54)")
    lines.append("        (name \"GND\" (effects (font (size 1.27 1.27))))")
    lines.append("        (number \"2\" (effects (font (size 1.27 1.27))))")
    lines.append("      )")
    lines.append("    )")
    lines.append("  )")
    lines.append("")
    
    # Footer
    lines.append(")")
    lines.append("")
    
    # Write file
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"✓ Generated symbol library: {output_path}")
    return output_path


def generate_library_table(library_path: str, output_path: str = "sym-lib-table"):
    """
    Generate sym-lib-table file with absolute path.
    """
    # Get absolute path
    abs_path = os.path.abspath(library_path)
    
    lines = [
        "(sym_lib_tables",
        "  (lib",
        f'    (name "turboquant") (type \"KiCad\") (uri "{abs_path}") (options \"\") (descr \"TurboQuant Custom Library\")',
        "  )",
        ")"
    ]
    
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"✓ Generated library table: {output_path}")
    print(f"  Points to: {abs_path}")
    return output_path


def copy_to_project(project_dir: str):
    """
    Copy library files to KiCad project directory.
    """
    # Find v3 or v4 project
    kicad_dirs = [
        os.path.expanduser("~/.openclaw/workspace/kicad/turboquant_mux_lna_v3"),
        os.path.expanduser("~/.openclaw/workspace/kicad/turboquant_mux_lna_v4"),
    ]
    
    target_dir = None
    for d in kicad_dirs:
        if os.path.exists(d):
            target_dir = d
            break
    
    if target_dir is None:
        print("ERROR: No KiCad project directory found")
        return False
    
    # Copy files
    import shutil
    
    src_lib = "turboquant_library.kicad_sym"
    src_table = "sym-lib-table"
    
    if os.path.exists(src_lib):
        dst_lib = os.path.join(target_dir, src_lib)
        shutil.copy2(src_lib, dst_lib)
        print(f"✓ Copied {src_lib} to {target_dir}")
    
    if os.path.exists(src_table):
        dst_table = os.path.join(target_dir, src_table)
        shutil.copy2(src_table, dst_table)
        print(f"✓ Copied {src_table} to {target_dir}")
    
    return True


def verify_library(library_path: str):
    """
    Verify the generated library can be parsed.
    """
    print(f"\nVerifying library: {library_path}")
    
    try:
        with open(library_path, 'r') as f:
            content = f.read()
        
        # Check structure
        checks = {
            'Header present': content.startswith('(kicad_symbol_lib'),
            'Power symbols': '+12V' in content and 'GND' in content,
            '74HC595': '74HC595' in content,
            'CD4051B': 'CD4051B' in content,
            'Passives': 'Device:R' in content and 'Device:C' in content,
            'Connectors': 'Conn_02x10' in content and 'SMA' in content,
            'Proper closing': content.rstrip().endswith(')'),
        }
        
        all_passed = True
        for check, passed in checks.items():
            status = "✓" if passed else "✗"
            print(f"  {status} {check}")
            if not passed:
                all_passed = False
        
        # Count symbols
        symbol_count = content.count('(symbol "')
        print(f"\n  Total symbols: {symbol_count}")
        
        if all_passed:
            print("\n✓ Library verification PASSED")
        else:
            print("\n✗ Library verification FAILED")
        
        return all_passed
        
    except Exception as e:
        print(f"✗ Verification error: {e}")
        return False


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate clean TurboQuest symbol library'
    )
    parser.add_argument('--output', '-o', default='turboquant_library.kicad_sym',
                       help='Output library file path')
    parser.add_argument('--copy', action='store_true',
                       help='Copy to KiCad project directory')
    parser.add_argument('--verify', action='store_true', default=True,
                       help='Verify generated library')
    
    args = parser.parse_args()
    
    print("="*70)
    print("TurboQuant Clean Symbol Library Generator")
    print("="*70)
    print()
    
    # Generate library
    lib_path = generate_symbol_library(args.output)
    
    # Generate library table
    table_path = generate_library_table(lib_path)
    
    # Verify
    if args.verify:
        verify_library(lib_path)
    
    # Copy to project
    if args.copy:
        print("\n" + "="*70)
        copy_to_project(None)
    
    print("\n" + "="*70)
    print("Generation complete!")
    print("="*70)
    print(f"\nNext steps:")
    print(f"  1. Open KiCad project")
    print(f"  2. Check Preferences → Configure Symbol Libraries")
    print(f"  3. Verify 'turboquant' library is listed")
    print(f"  4. Open schematic and remap symbols if needed")
    print(f"     Tools → Remap Symbols to Library")


if __name__ == '__main__':
    main()
