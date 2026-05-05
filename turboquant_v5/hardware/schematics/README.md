# TurboQuant MUX/LNA Board — V5 KiCad Project

**Version:** 5.0  
**Date:** 2026-05-02  
**Status:** Schematics complete — PCB partially routed, needs KiCad GUI migration

---

## What Changed from V3/V4

| Component | Old (v3/v4) | V5 |
|-----------|-------------|-----|
| Shift Register | 74HC595 | **74HCT595** (TTL levels, 3.3V compatible) |
| Analog MUX | PE4259 / CD4051B | **DG408** (8:1, 100V capable) |
| LNA | ADL5610 / AD8332 | **OPA1641** (low-noise, configurable gain) |
| TX Switch | BSS138 only | **IRF830** (500V HV) + gate protection |
| 5V Regulator | LM7805 TO-220 | **LM7805 DPAK** (thermal adequate for ~50mA) |

---

## Schematic Status

### ✅ Digital (`digital.kicad_sch`)
- 74HCT595 shift register with TTL input levels
- 8× BSS138 gate drivers (100Ω series + 10kΩ pull-down)
- 10kΩ pull-ups on ~OE and SRCLR
- 6-pin control header (SER, SRCLK, RCLK, SRCLR, ~OE, GND)

### ✅ Power (`power.kicad_sch`)
- 12V input → polyfuse → SS34 Schottky → TVS
- LM7805 DPAK (TO-252) with copper pour heatsink
- AMS1117-3.3 for 3.3V rail
- Full decoupling: 100µF + 100nF on input, 10µF + 100nF on each output

### ✅ Analog (`analog.kicad_sch`)
- 8× T/R Switch blocks (passive diode bridge, 200V)
  - 4× MUR120 fast recovery diodes per channel (32 total)
  - Bias network: 10kΩ + 100kΩ + BZX84C5V1 zener per channel
- 2× DG408 8:1 MUX (SOIC-16)
  - VDD = 12V, VSS = GND, VL = 5V
  - Address lines A/B/C with 10kΩ pull-downs
  - EN with 10kΩ pull-down
- 2× OPA1641 non-inverting amplifier (SOIC-8)
  - Gain = 10 (Rg=1k, Rf=9.09k)
- 10:1 attenuator + BAV99 clamping diodes before LNA inputs

### ✅ TX Switch (`tx_switch.kicad_sch`)
- 8× IRF830 TO-220 MOSFETs
- 4× TC4427 gate drivers (2 channels each)
- Each gate: 100Ω series + 1kΩ pull-down + BZX84C12 Zener clamp
- Source → GND, Drain → TX_BUS / per-channel outputs

---

## GPIO Pinout (Red Pitaya E1)

```
E1 Connector:
  Pin 7  → DIO0_P → SER (shift register data)
  Pin 8  → DIO0_N → SRCLK (shift clock)
  Pin 9  → DIO1_P → RCLK (storage latch)
  Pin 10 → DIO1_N → MUX_A (address bit 0)
  Pin 11 → DIO2_P → MUX_B (address bit 1)
  Pin 12 → DIO2_N → MUX_C (address bit 2)
  Pin 13 → DIO3_P → MUX_EN (enable)
  Pin 14 → DIO3_N → TRIGGER (emission sync)

  Pin 1/2 → 3.3V (supply for logic/reference)
  Pin 25/26 → GND
```

---

## Layout Notes

- **Layers:** 4 (Signal / GND / Power / Signal)
- **Size:** 100mm × 80mm
- **HV clearances:** >2mm for 100V traces
- **Thermal:** Copper pour under LM7805 DPAK tab
- **Partitioning:** Power (top-left), Digital (top-right), Analog (center), TX (bottom)

See `PCB_LAYOUT_PLAN.md` for detailed floorplan and `ROUTING_CHECKLIST.md` for routing priorities.

---

## Known Issues

1. **PCB file format:** `turboquant_mux_lna_v5.kicad_pcb` is KiCad v7 format. KiCad 9 (installed) requires GUI migration on first open.
2. **kicad-cli DRC unavailable:** Cannot run automated DRC until PCB is migrated to v9.
3. **Trace routing approximate:** Coordinates are estimates; review in GUI before fabrication.

---

## Procurement

See `../../docs/bom/BOM_v5.md` for full BOM and procurement tracker.

**Critical parts to order:**
1. Red Pitaya STEMlab 125-14 Gen 2 (£250)
2. DG408 ×2, 74HCT595 ×1, IRF830 ×8, OPA1641 ×2

---

*V5.0 — May 2, 2026*
