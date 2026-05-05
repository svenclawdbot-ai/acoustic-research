import json

pro_file = "tuboquant_mux_lna.kicad_pro"

with open(pro_file, "r") as f:
    data = json.load(f)

# Add standard KiCad symbol libraries
data["libraries"] = {
    "pinned_footprint_libs": [],
    "pinned_symbol_libs": []
}

# Also need to add the library table reference
# KiCad 9 uses sym-lib-table for symbol libraries
with open(pro_file, "w") as f:
    json.dump(data, f, indent=2)

# Create sym-lib-table for symbol libraries
sym_lib_table = """(sym_lib_table
  (version 7)
  (lib (name "power")(type "KiCad")(uri "${KICAD9_SYMBOL_DIR}/power.kicad_sym")(options "")(descr ""))
  (lib (name "Device")(type "KiCad")(uri "${KICAD9_SYMBOL_DIR}/Device.kicad_sym")(options "")(descr ""))
  (lib (name "Connector")(type "KiCad")(uri "${KICAD9_SYMBOL_DIR}/Connector.kicad_sym")(options "")(descr ""))
  (lib (name "74xx")(type "KiCad")(uri "${KICAD9_SYMBOL_DIR}/74xx.kicad_sym")(options "")(descr ""))
  (lib (name "Regulator_Linear")(type "KiCad")(uri "${KICAD9_SYMBOL_DIR}/Regulator_Linear.kicad_sym")(options "")(descr ""))
  (lib (name "Diode")(type "KiCad")(uri "${KICAD9_SYMBOL_DIR}/Diode.kicad_sym")(options "")(descr ""))
  (lib (name "Transistor_FET")(type "KiCad")(uri "${KICAD9_SYMBOL_DIR}/Transistor_FET.kicad_sym")(options "")(descr ""))
  (lib (name "Analog_Switch")(type "KiCad")(uri "${KICAD9_SYMBOL_DIR}/Analog_Switch.kicad_sym")(options "")(descr ""))
  (lib (name "Amplifier_Operational")(type "KiCad")(uri "${KICAD9_SYMBOL_DIR}/Amplifier_Operational.kicad_sym")(options "")(descr ""))
)
"""

with open("sym-lib-table", "w") as f:
    f.write(sym_lib_table)

print("Updated project file and created sym-lib-table")
print("\nLibrary configuration:")
print("  - power (power symbols)")
print("  - Device (R, C, LED)")
print("  - Connector (headers, SMA)")
print("  - 74xx (74HC595)")
print("  - Regulator_Linear (LM7805, AMS1117)")
print("  - Diode (1N4007, BAV99)")
print("  - Transistor_FET (BSS138)")
print("  - Analog_Switch (CD4051B)")
print("  - Amplifier_Operational (OPA657)")
