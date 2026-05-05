# TurboQuant V5 — Project Structure

*Organised: 2026-04-27*

## Directory Layout

```
turboquant_v5/
├── hardware/
│   ├── schematics/          # Current KiCad v5 schematics + PCB
│   │   ├── analog.kicad_sch
│   │   ├── digital.kicad_sch
│   │   ├── power.kicad_sch
│   │   ├── tx_switch.kicad_sch
│   │   ├── turboquant_mux_lna_v5.kicad_sch (top level)
│   │   ├── turboquant_mux_lna_v5.kicad_pcb
│   │   ├── turboquant_library.kicad_sym
│   │   ├── BOM.md
│   │   ├── PCB_LAYOUT_PLAN.md
│   │   └── README.md
│   ├── pcb/                 # Production files (Gerbers, drill, etc.)
│   ├── production/          # Manufacturing docs, assembly notes
│   └── archive/             # Old iterations (v3, v4, red_pitaya_mux_board)
│
├── software/
│   ├── fpga/                # Red Pitaya FPGA code
│   │   ├── v5_api.py
│   │   ├── turboquant_control.py
│   │   ├── v5_mux_controller.v
│   │   ├── v5_red_pitaya.xdc
│   │   └── ...
│   ├── api/                 # Python API + data logger
│   └── scripts/             # KiCad generation scripts
│       ├── generate_analog_sch.py
│       ├── generate_tx_switch.py
│       ├── generate_pcb.py
│       └── skidl variants
│
├── docs/
│   ├── design/              # Design decisions, change summaries
│   │   └── PCB_v5_CHANGE_SUMMARY.md
│   ├── bom/                 # Bill of materials
│   │   └── BOM_v5.md
│   ├── verification/        # Design verification, ERC/DRC reports
│   │   └── V5_DESIGN_VERIFICATION.md
│   └── procurement/         # Order tracking, supplier info
│
└── archive/
    └── v3_v4_legacy/        # All pre-v5 iterations (preserved)
        ├── v3 schematics
        ├── v4 PCB attempts
        ├── red_pitaya_mux_board/
        └── generation scripts
```

## What's Where

### Active Work (v5 Current)
- **Schematics:** `hardware/schematics/` — 4 sheets: power, digital, analog, tx_switch
- **PCB:** `hardware/schematics/*.kicad_pcb` — layout in progress
- **BOM:** `docs/bom/BOM_v5.md` + `hardware/schematics/BOM.md`
- **FPGA:** `software/fpga/` — v5 API, controllers, constraints

### Reference / Archive
- **v3/v4/red_pitaya:** `archive/v3_v4_legacy/` — preserved for history
- **Old scripts:** `software/scripts/` includes skidl variants from earlier iterations

## Next Steps
1. Complete PCB routing in KiCad
2. Run DRC → move files to `hardware/pcb/`
3. Generate Gerbers → `hardware/production/`
4. Order components using `docs/bom/BOM_v5.md`

---
*This structure keeps active work clean while preserving all historical iterations.*
