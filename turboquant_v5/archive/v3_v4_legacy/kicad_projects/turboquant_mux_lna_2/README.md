# TurboQuant Mux LNA Board - KiCad 9.0

Hierarchical schematic design for 8-element ultrasound array interface with multiplexed LNA channels.

## ⚠️ IMPORTANT: Embedded Symbols

**The power.kicad_sch now includes EMBEDDED symbol definitions** in the `lib_symbols` section. This means:
- ✅ Symbols will display correctly even without external libraries
- ✅ No dependency on `${KICAD9_SYMBOL_DIR}` environment variable
- ✅ Portable - works on any system with KiCad 9.0

## Project Structure

| File | Description |
|------|-------------|
| `tuboquant_mux_lna.kicad_pro` | KiCad 9.0 project file |
| `tuboquant_mux_lna.kicad_sch` | Root schematic with hierarchical sheets |
| `power.kicad_sch` | Power supplies (12V→5V→3.3V) - **EMBEDDED SYMBOLS** |
| `digital.kicad_sch` | Digital control (74HC595 shift register) |
| `analog.kicad_sch` | Analog frontend (mux, LNA) |
| `sym-lib-table` | Symbol library configuration (absolute paths) |

## Opening in KiCad 9.0

### Method 1: Direct Open (Recommended)
```bash
cd ~/.openclaw/workspace/kicad/turboquant_mux_lna_2
kicad tuboquant_mux_lna.kicad_pro
```

Then click **Schematic Editor**.

### Method 2: If Symbols Still Don't Show

1. Open KiCad 9.0
2. File → Open Project → Select `tuboquant_mux_lna.kicad_pro`
3. Click **Schematic Editor**
4. Go to **Tools → Update Symbols from Library**
5. Click **Update All**

### Method 3: Rescue/Remap Symbols

If you see "?" or broken symbols:
1. Tools → **Remap Symbols to Library**
2. Or: Edit → **Symbol Fields and References**
3. Check that symbols point to correct libraries

## Hierarchical Design

```
tuboquant_mux_lna.kicad_sch (Root)
├── POWER_SUPPLIES (power.kicad_sch)
│   ├── +12V, +5V, +3V3 power symbols (EMBEDDED)
│   ├── C1-C5 capacitors (EMBEDDED)
│   ├── R1-R2 resistors (EMBEDDED)  
│   ├── D2-D3 LEDs (EMBEDDED)
│   └── GND power symbols (EMBEDDED)
├── DIGITAL_CONTROL (digital.kicad_sch)
│   └── 74HC595 shift register
└── ANALOG_FRONTEND (analog.kicad_sch)
    └── BSS138, CD4051B, OPA690
```

## Embedded Symbols in power.kicad_sch

The following symbols have full graphics embedded:
- `power:+12V`, `power:+5V`, `power:+3V3`, `power:GND`
- `Device:C` (capacitor)
- `Device:R` (resistor)
- `Device:LED`

This means the power sheet will display correctly without any external libraries.

## Troubleshooting

### "${KICAD9_SYMBOL_DIR}" shown in path
This means KiCad can't expand the environment variable. Solutions:
1. Use the embedded symbol version (power.kicad_sch is already set up this way)
2. Or set the environment variable: `export KICAD9_SYMBOL_DIR=/usr/share/kicad/symbols`
3. Or use absolute paths in sym-lib-table (already done)

### Symbols show "?"
1. Check **Preferences → Configure Symbol Libraries**
2. Ensure libraries point to correct paths
3. Try **Tools → Update Symbols from Library**
4. Or use **Tools → Edit Symbol Library References**

### Check Library Setup
```bash
# Verify libraries exist
ls /usr/share/kicad/symbols/*.kicad_sym | head -10

# Check specific symbol
grep '"C"' /usr/share/kicad/symbols/Device.kicad_sym
```

## Technical Details

### KiCad 9.0 Format Features Used
- `(version 20250114)` - KiCad 9 format version
- `(generator_version "9.0")` - Generator version tag
- Full symbol embedding in `lib_symbols` section
- `(unit 1)` for each symbol instance
- `(exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)` flags
- `(symbol_instances)` section for annotation

### Symbol References
Symbols use `Library:SymbolName` format:
- `power:GND` - Ground power symbol
- `Device:C` - Capacitor
- `Device:R` - Resistor
- `Device:LED` - LED
