# Bill of Materials: Flexural Beam Shear Wave Probe
## Field-Deployable Viscoelastic Imaging System

**Revision:** 1.0  
**Date:** March 16, 2026  
**Target Cost:** <£100 per unit  
**Lead Time:** 2-3 weeks

---

## ASSEMBLY 1: MECHANICAL HOUSING (3D Printed)

### Printed Parts
| Item | Qty | Material | Print Time | Cost | Notes |
|------|-----|----------|------------|------|-------|
| Main housing | 1 | PETG | 3h 20m | £2.40 | 80g @ £30/kg |
| Beam clamp | 1 | PETG | 45m | £0.50 | 17g |
| Spring cap | 1 | PETG | 20m | £0.25 | 8g |
| Silicone mold | 1 | PLA | 1h 10m | £0.85 | 28g |

**Subtotal Printed:** £4.00

### Printing Specifications
```
Material: PETG (main parts) for strength/temperature
         PLA (mold only) - disposable
Layer height: 0.2 mm
Infill: 20% gyroid (main housing), 40% (clamp)
Perimeters: 3
Top/bottom layers: 4
Support: None required (design is self-supporting)
Bed temp: 70°C (PETG), 60°C (PLA)
Nozzle temp: 240°C (PETG), 210°C (PLA)
```

**Slicer settings for strength:**
- Enable "detect thin walls"
- Enable "ironing" on top surfaces (sealing)
- 0.4mm nozzle standard

---

## ASSEMBLY 2: FLEXURAL BEAM

### Beam Components
| Item | Qty | Spec | Supplier | Part # | Cost | Lead |
|------|-----|------|----------|--------|------|------|
| Aluminum strip | 1 | 6061-T6, 60×15×2 mm | Metal Supermarket / Any | Cut to size | £2.00 | Stock |
| Brass tip mass | 1 | Cylinder, 8mm × 10mm | eBay / Model shop | N/A | £1.50 | Stock |
| Silicone sheet | 1 | 50×50×1mm, Shore A30 | Smooth-On / Amazon | EcoFlex 00-30 | £5.00 | 1 week |
| Mounting screw | 2 | M3×8mm, stainless | RS Components | 281-714 | £0.30 | Stock |
| Tip adhesive | 1 | Silicone adhesive tube | Hardware store | Generic | £3.00 | Stock |

**Subtotal Beam:** £11.80

### Machining Operations
| Operation | Tool | Time | Notes |
|-----------|------|------|-------|
| Cut to length | Hacksaw + file | 5 min | Clean edges with file |
| Drill mounting hole | Drill + 4mm bit | 2 min | 10mm from end |
| Radius tip | File + sandpaper | 10 min | R5mm radius, smooth |
| Surface prep | Sandpaper 400 grit | 5 min | For bonding |

**Total fab time:** ~25 minutes per beam

---

## ASSEMBLY 3: PIEZO ACTUATION

### Piezo Components
| Item | Qty | Spec | Supplier | Part # | Cost | Lead |
|------|-----|------|----------|--------|------|------|
| Piezo stack | 1 | 10×10×20mm, 150V, 12μm | Noliac | NAC2124-A01 | £38.50 | 2 weeks |
| OR: Alternative | 1 | 10×10×20mm, 150V | PiezoDrive / Physik Instrumente | PD0S020 | £32.00 | 1 week |
| HV cable | 0.5m | RG174, 50Ω | RS Components | 360-883 | £2.50 | Stock |
| Connector | 1 | LEMO 00.250 | RS Components | 111-2652 | £8.50 | 1 week |
| OR: BNC | 1 | Panel mount | RS Components | 467-596 | £2.80 | Stock |
| Bonding epoxy | 1 | 2-part, low viscosity | RS Components | 144-971 | £8.00 | Stock |
| Cleaning solvent | 1 | Isopropanol 99% | Amazon / Pharmacy | N/A | £5.00 | Stock |

**Subtotal Piezo:** £64.50 (LEMO) or £58.80 (BNC)

### Piezo Handling Notes
- **Polarity matters:** Mark + electrode before mounting
- **Preload required:** 0.5-1 N for optimal performance
- **Temperature limit:** 80°C (Curie point ~150°C)
- **Humidity sensitive:** Seal with conformal coating after assembly

---

## ASSEMBLY 4: SPRING PRELOAD SYSTEM

| Item | Qty | Spec | Supplier | Part # | Cost | Lead |
|------|-----|------|----------|--------|------|------|
| Compression spring | 1 | 0.5 N/mm, OD 8mm, L0=20mm | Springmasters / RS | C0550-008-0200S | £2.80 | Stock |
| Adjustment screw | 1 | M3×20mm, nylon tip | RS Components | 281-998 | £0.40 | Stock |
| Retaining ring | 1 | M3 hex nut | RS Components | 528-940 | £0.15 | Stock |
| Spring guide | 1 | PTFE washer, 8mm ID | eBay / Amazon | N/A | £0.50 | Stock |

**Subtotal Spring:** £3.85

### Spring Specifications
```
Free length (L0): 20 mm
Solid length (Ls): 12 mm
Working range: 14-18 mm (0.5-1.0 N preload)
Spring rate: 0.5 N/mm
Material: Stainless steel 302
End condition: Ground flat
```

---

## ASSEMBLY 5: ELECTRONICS (HV Drive)

| Item | Qty | Spec | Supplier | Part # | Cost | Lead |
|------|-----|------|----------|--------|------|------|
| Gate driver IC | 1 | TC4427CPA, DIP-8 | RS Components | 542-771 | £2.50 | Stock |
| MOSFET | 1 | IRF830, TO-220 | RS Components | 540-063 | £3.20 | Stock |
| HV DC-DC module | 1 | 12V → 150V, 2W | AliExpress / eBay | "High voltage boost" | £12.00 | 2 weeks |
| Microcontroller | 1 | Raspberry Pi Pico | RS Components | 191-7971 | £3.80 | Stock |
| Voltage reg | 1 | LM7805, TO-220 | RS Components | 298-8514 | £0.80 | Stock |
| Resistor 10Ω | 2 | 0.25W, 5% | RS Components | 146-982 | £0.20 | Stock |
| Resistor 1kΩ | 4 | 0.25W, 5% | RS Components | 146-987 | £0.20 | Stock |
| Resistor 10kΩ | 2 | 0.25W, 5% | RS Components | 146-997 | £0.20 | Stock |
| Cap 100nF | 4 | Ceramic, 50V | RS Components | 169-7148 | £0.40 | Stock |
| Cap 10µF | 2 | Electrolytic, 250V | RS Components | 711-2396 | £1.00 | Stock |
| Diode 1N4007 | 2 | 1kV, 1A | RS Components | 628-9220 | £0.30 | Stock |
| LED 3mm | 2 | Any color | RS Components | 228-6282 | £0.30 | Stock |
| Prototype PCB | 1 | 50×70mm, stripboard | RS Components | 206-2130 | £3.00 | Stock |
| BNC connector | 2 | Panel mount | RS Components | 467-596 | £5.60 | Stock |
| Pin headers | 1 | 40-way strip | RS Components | 251-8576 | £2.00 | Stock |
| Enclosure | 1 | 80×50×25mm, ABS | RS Components | 548-676 | £5.00 | Stock |
| Heat sink | 1 | TO-220, 19°C/W | RS Components | 189-553 | £2.00 | Stock |
| Thermal pad | 1 | TO-220 size | RS Components | 789-2727 | £0.80 | Stock |

**Subtotal Electronics:** £43.50

**OR: Pre-built alternative:**
| Item | Qty | Spec | Supplier | Cost |
|------|-----|------|----------|------|
| PiezoDrive PDm200 | 1 | 200V, ±200mA amplifier | PiezoDrive | £180 |

**DIY recommended for cost, pre-built for reliability**

---

## ASSEMBLY 6: CABLES & INTERCONNECT

| Item | Qty | Spec | Supplier | Part # | Cost | Lead |
|------|-----|------|----------|--------|------|------|
| HV coax cable | 1m | RG58, 2.5kV rated | RS Components | 360-971 | £4.50 | Stock |
| USB cable | 1 | USB-A to micro-USB, 1m | Amazon | N/A | £3.00 | Stock |
| Power cable | 1m | 2-core, 0.5mm² | RS Components | 361-3863 | £1.20 | Stock |
| Cable ties | 10 | 100mm, assorted | RS Components | 192-5904 | £2.00 | Stock |
| Heat shrink | 1 set | Assorted colors | RS Components | 687-4733 | £5.00 | Stock |
| Cable grommet | 2 | 6mm ID, rubber | RS Components | 495-862 | £1.00 | Stock |

**Subtotal Cables:** £16.70

---

## ASSEMBLY 7: FINISHING & LABELING

| Item | Qty | Spec | Supplier | Part # | Cost |
|------|-----|------|----------|--------|------|
| Spray paint | 1 | Matte black, 400ml | Hardware store | N/A | £6.00 |
| Label maker tape | 1 | 12mm, white on black | Brother / Dymo | N/A | £8.00 |
| Rubber feet | 4 | 10mm adhesive | RS Components | 549-949 | £1.20 |
| Velcro strap | 1 | Cable management | Amazon | N/A | £2.00 |

**Subtotal Finishing:** £17.20

---

## SUMMARY COST BREAKDOWN

| Assembly | Cost (DIY HV) | Cost (Pre-built HV) |
|----------|--------------|---------------------|
| Mechanical housing (printed) | £4.00 | £4.00 |
| Flexural beam | £11.80 | £11.80 |
| Piezo actuation | £64.50 | £64.50 |
| Spring preload | £3.85 | £3.85 |
| Electronics (HV drive) | £43.50 | £180.00 |
| Cables & interconnect | £16.70 | £16.70 |
| Finishing & labeling | £17.20 | £17.20 |
| **TOTAL** | **£161.55** | **£298.05** |

**Target achieved:** £161.55 < £200 budget

---

## ALTERNATIVE: COMPLETE KIT SOURCES

### Option A: PiezoDrive (Professional)
| Item | Cost | URL |
|------|------|-----|
| PDm200 amplifier | £180 | www.piezodrive.com |
| PSt 150/5×5/20 stack | £45 | www.piezodrive.com |
| **Subtotal** | **£225** | |

### Option B: Thorlabs (Research Grade)
| Item | Cost | URL |
|------|------|-----|
| AE0203D08F amplifier | £350 | www.thorlabs.com |
| PK4FA1P1 stack | £85 | www.thorlabs.com |
| **Subtotal** | **£435** | |

### Option C: Noliac (OEM)
| Item | Cost | URL |
|------|------|-----|
| Noliac NAC2014 amp | £150 | www.noliac.com |
| NAC2124 stack | £40 | www.noliac.com |
| **Subtotal** | **£190** | |

**DIY (Option D) remains most cost-effective at £162**

---

## PROCUREMENT PLAN

### Immediate (Day 1)
- [ ] Order piezo stack (Noliac or PiezoDrive) - **2 week lead**
- [ ] Order HV DC-DC module (AliExpress) - **2 week lead**
- [ ] Order PETG filament if not in stock
- [ ] Purchase aluminum strip, springs (local)

### Week 1
- [ ] Print housing components
- [ ] Fabricate flexural beam
- [ ] Machine aluminum

### Week 2
- [ ] Receive piezo and HV module
- [ ] Assemble and test electronics
- [ ] Bond piezo to beam

### Week 3
- [ ] Final assembly
- [ ] Resonance tuning
- [ ] Phantom testing

---

## SPARES & REDUNDANCY

Recommended to order:
| Item | Spare Qty | Reason |
|------|-----------|--------|
| Piezo stack | 1 | Fragile, long lead time |
| MOSFET | 2 | Easy to damage during soldering |
| Springs | 2 | May take set over time |
| PETG filament | 1 kg | Iterative housing design |
| Silicone sheet | 2 | Trial and error for tip |

**Spares budget:** +£60

---

## TOOLS REQUIRED

### Essential
- [ ] 3D printer (or access to service)
- [ ] Soldering iron (temperature controlled)
- [ ] Multimeter
- [ ] Hacksaw + files
- [ ] Drill + 4mm bit
- [ ] Screwdrivers (flat, Phillips, hex)

### Helpful
- [ ] Oscilloscope (for testing)
- [ ] Function generator
- [ ] Hot air rework station
- [ ] Caliper

---

## QUALITY CHECKLIST

### Before Assembly
- [ ] All dimensions verified against CAD
- [ ] Piezo capacitance measured (should be ~100-200 nF)
- [ ] Spring rate verified (should be 0.5 N/mm)
- [ ] 3D printed parts cleaned (no stringing)

### During Assembly
- [ ] Piezo polarity marked clearly
- [ ] Epoxy cure time respected (24 hours minimum)
- [ ] HV connections insulated properly
- [ ] Spring preload set to 0.5-1 N

### After Assembly
- [ ] Resonant frequency measured (target: 150-250 Hz)
- [ ] Tip displacement >100 μm at 100V, 200 Hz
- [ ] No electrical shorts (resistance >10 MΩ)
- [ ] Housing temperature <40°C during operation

---

## DOCUMENTATION REFERENCES

| Document | Location | Purpose |
|----------|----------|---------|
| CAD files | `./cad_output/` | Manufacturing files |
| Flexural beam design | `flexural_beam_design.md` | Theory & calculations |
| Assembly guide | `assembly_guide.md` (TODO) | Step-by-step build |
| Test protocol | `test_protocol.md` (TODO) | Validation procedures |

---

## REVISION HISTORY

| Rev | Date | Author | Changes |
|-----|------|--------|---------|
| 1.0 | 2026-03-16 | Sven | Initial release |

---

*Bill of Materials prepared for: Field-Deployable Shear Wave Probe*  
*Total system cost target: <£200 per unit*
