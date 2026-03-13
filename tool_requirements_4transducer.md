# Tool Requirements for Shear Wave Elastography Test Rig
## 4-Transducer Build with DIY Pulser

**Date:** March 13, 2026  
**Configuration:** 4 transducers + DIY HV pulser + Raspberry Pi  
**Estimated Total Tool Cost:** £0-150 (depending on existing equipment)

---

## EXISTING TOOLS (From Your Workshop Notes)

| Tool | Status | Notes |
|------|--------|-------|
| ✅ **Oscilloscope** | Confirmed | Essential for debugging, signal verification |
| ✅ **Bench power supply** | Confirmed | Powering pulser circuits |
| ✅ **Soldering station** | Confirmed | Circuit assembly |
| ✅ **Multimeter** | Confirmed | Circuit testing, voltage checks |

**Assessment:** You have the core tools needed. Additional items below are helpful but not strictly required.

---

## REQUIRED TOOLS (Minimal)

### Electronics Assembly

| Tool | Purpose | Cost | Priority |
|------|---------|------|----------|
| **Wire strippers** | Preparing cables | £8 | Essential |
| **Needle-nose pliers** | Component handling | £6 | Essential |
| **Flush cutters** | Trimming leads | £5 | Essential |
| **Third hand / PCB holder** | Soldering assistance | £12 | Highly recommended |
| **Desoldering braid** | Mistake correction | £3 | Recommended |
| **Heat shrink tubing set** | Cable insulation | £8 | Recommended |
| **Helping hands with magnifier** | Precision work | £15 | Nice to have |

**Subtotal required tools:** ~£20-35

---

## RECOMMENDED TOOLS (Better Build Experience)

### Precision Electronics

| Tool | Purpose | Cost | Priority |
|------|---------|------|----------|
| **Digital calipers** | Measuring transformer cores, spacing | £15 | Recommended |
| **Component tester (LCR meter)** | Verify transformers, capacitors | £20 | Recommended |
| **Logic analyzer (cheap)** | Arduino timing verification | £15 | Nice to have |
| **Function generator** | Testing receiver chain | £30-50 | Nice to have |
| **Variable DC load** | Testing HV supply | £25 | Optional |

### Safety Equipment

| Item | Purpose | Cost | Priority |
|------|---------|------|----------|
| **Insulated gloves (HV rated)** | 1000V protection | £10 | **Essential for HV** |
| **Safety glasses** | Soldering splash protection | £5 | Recommended |
| **ESD wrist strap** | Protect sensitive components | £5 | Recommended |
| **Insulated screwdriver set** | HV adjustment | £8 | **Essential for HV** |
| **Discharge resistor (10kΩ, 10W)** | Safely discharge HV caps | £3 | **Essential for HV** |

**Subtotal safety equipment:** ~£30

---

## PHANTOM FABRICATION TOOLS

### DIY Gelatin Phantoms

| Tool | Purpose | Cost | Priority |
|------|---------|------|----------|
| **Kitchen scale (0.1g precision)** | Measuring gelatin | £12 | Essential |
| **Digital thermometer** | Water temperature (40-60°C) | £8 | Essential |
| **Silicone molds / Tupperware** | Phantom containers | £5 | Essential |
| **Whisk / hand mixer** | Mixing without bubbles | £10 | Recommended |
| **Fine mesh sieve** | Removing bubbles | £5 | Nice to have |
| **Plastic pipettes (10mL)** | Adding graphite evenly | £3 | Recommended |

**Subtotal phantom tools:** ~£15-30

### Polyacrylamide (If Attempting)

| Tool | Purpose | Cost | Priority |
|------|---------|------|----------|
| **Fume hood or ventilation** | Acrylamide is neurotoxic | — | **Essential** |
| **Nitrile gloves (box)** | Chemical protection | £8 | **Essential** |
| **Safety goggles (chemical)** | Splash protection | £5 | **Essential** |
| **Magnetic stirrer + hot plate** | Mixing solutions | £40 | Recommended |
| **pH strips or meter** | Checking polymerization | £10 | Recommended |
| **Vacuum chamber (DIY)** | Degassing gels | £30 | Nice to have |

**Note:** Polyacrylamide requires serious safety precautions. Start with gelatin.

---

## MECHANICAL TOOLS (Optional)

### Transducer Mounting

| Tool | Purpose | Cost | Priority |
|------|---------|------|----------|
| **Small drill press or Dremel** | Mounting holes in enclosure | £40 | Nice to have |
| **3D printer access** | Custom transducer holders | £0-300 | Optional |
| **Small vice** | Holding workpieces | £15 | Nice to have |
| **Calipers (digital)** | Precise spacing measurement | £15 | Recommended |

### Phantom Testing

| Tool | Purpose | Cost | Priority |
|------|---------|------|----------|
| **Rheometer access** | Validating phantom stiffness | University lab | Ideal |
| **Indentation tester** | Alternative stiffness check | University lab | Ideal |
| **Hot plate with stirrer** | Phantom fabrication | £25 | Recommended |

---

## SOFTWARE TOOLS (Free)

### Development

| Tool | Purpose | Cost |
|------|---------|------|
| **Arduino IDE** | Pulser control code | Free |
| **Python + Jupyter** | Signal processing | Free |
| **Git** | Version control | Free |
| **KiCad** | PCB design (if iterating) | Free |

### Signal Processing

| Library | Purpose | Cost |
|---------|---------|------|
| **NumPy / SciPy** | Array operations, filtering | Free |
| **Matplotlib** | Plotting results | Free |
| **PyMC3 or PyStan** | Bayesian inference | Free |
| **scikit-optimize** | Parameter fitting | Free |

---

## COMPLETE TOOLING CHECKLIST

### Already Have (Confirmed)
- [x] Oscilloscope
- [x] Bench power supply
- [x] Soldering station
- [x] Multimeter

### Need to Acquire (~£50-80)

**Essential (£30):**
- [ ] Wire strippers (£8)
- [ ] Needle-nose pliers (£6)
- [ ] Flush cutters (£5)
- [ ] Insulated gloves (£10)
- [ ] Insulated screwdriver set (£8)
- [ ] Discharge resistor (£3)

**Highly Recommended (£25):**
- [ ] Third hand / PCB holder (£12)
- [ ] Digital calipers (£15)
- [ ] Desoldering braid (£3)
- [ ] Heat shrink tubing (£8)

**Phantom Fabrication (£20):**
- [ ] Kitchen scale (£12)
- [ ] Digital thermometer (£8)
- [ ] Silicone molds / Tupperware (£5)

**Safety (£10):**
- [ ] Safety glasses (£5)
- [ ] ESD wrist strap (£5)

**TOTAL: ~£85** (if buying everything above)

---

## 4-TRANSDUCER BUILD SPECIFICS

### Spacing Requirements

With 4 transducers at **5, 10, 20, 30 mm** spacing:

| Pair | Distance | Use Case |
|------|----------|----------|
| R1-R2 | 5 mm | Short baseline, high SNR |
| R1-R3 | 15 mm | Medium baseline |
| R1-R4 | 25 mm | Long baseline, best dispersion resolution |
| R2-R3 | 10 mm | Redundancy check |
| R2-R4 | 20 mm | Medium-long baseline |
| R3-R4 | 10 mm | Short baseline at distance |

### Mounting Considerations

**Option 1: Linear Array (Recommended)**
```
Source → [5mm] R1 [5mm] R2 [10mm] R3 [10mm] R4
         ←———25mm max baseline————→
```

**Mounting Method:**
- 3D printed bracket (if you have access)
- Aluminum angle stock drilled for BNC connectors
- Acrylic sheet with precise holes

**Critical:** Spacing accuracy ±0.5 mm for valid dispersion measurements

---

## SHOPPING PRIORITY (Tools)

### Phase 1: Essential for Pulser Build
1. Wire strippers (£8)
2. Needle-nose pliers (£6)
3. Flush cutters (£5)
4. Insulated gloves (£10) — **Safety critical**
5. Insulated screwdriver (£8)

**Phase 1 Total: £37**

### Phase 2: Better Build Experience
6. Third hand (£12)
7. Digital calipers (£15)
8. Heat shrink tubing (£8)
9. Safety glasses (£5)

**Phase 2 Total: £40**

### Phase 3: Phantom Fabrication
10. Kitchen scale (£12)
11. Digital thermometer (£8)
12. Silicone molds (£5)

**Phase 3 Total: £25**

---

## TOOL SOURCES

| Supplier | Best For | Website |
|----------|----------|---------|
| **RS Components** | Electronics tools, safety | rs-online.com |
| **Farnell** | Professional electronics | farnell.com |
| **Amazon** | General tools, quick delivery | amazon.co.uk |
| **CPC** | Budget electronics tools | cpc.farnell.com |
| **Toolstation** | Hand tools | toolstation.com |
| **IKEA** | Kitchen scale | ikea.com |

---

## ESTIMATED TOTAL COSTS

### 4-Transducer Build + Tools

| Category | Cost |
|----------|------|
| Electronics (pulser + Pi + ADC) | £165 |
| 4× Transducers | £88 |
| Cables and connectors | £30 |
| Essential tools | £37 |
| Recommended tools | £40 |
| Phantom materials | £25 |
| **GRAND TOTAL** | **~£385** |

### Without Optional Tools: £305

If you skip Phase 2/3 tools initially and use existing kitchen equipment:
- Core electronics: £165
- 4 transducers: £88
- Cables: £30
- Essential tools only: £37
- Gelatin (supermarket): £10
- **Total: £330**

---

## IMMEDIATE TOOL ORDERS

**Today (if building pulser this weekend):**
1. [ ] Wire strippers — Amazon, £8
2. [ ] Insulated gloves — RS Components, £10
3. [ ] Flush cutters — Amazon, £5

**This week:**
4. [ ] Digital calipers — Amazon, £15
5. [ ] Kitchen scale — IKEA, £12
6. [ ] Third hand — Amazon, £12

---

## WORKSPACE SETUP

### Recommended Layout

```
┌─────────────────────────────────────────┐
│  BENCH POWER SUPPLY    OSCILLOSCOPE     │
│  (12V, 5V)            (Signal analysis) │
├─────────────────────────────────────────┤
│                                         │
│     SOLDERING STATION                   │
│     + Third hand                        │
│                                         │
│     [PULSER PCB BUILD AREA]             │
│                                         │
├─────────────────────────────────────────┤
│  Raspberry Pi + ADC    TRANSDUCER ARRAY │
│  (Acquisition)         (Test setup)     │
└─────────────────────────────────────────┘
           ↓
    PHANTOM FABRICATION
    (Kitchen scale, molds)
```

### Safety Zones
- **HV Zone:** Keep pulser +200V area clear, marked
- **Ground Reference:** Single-point ground for all equipment
- **Ventilation:** If using polyacrylamide (fume hood)

---

## 4-TRANSDUCER DECISION CONFIRMED

**Configuration:** 5, 10, 20, 30 mm spacing  
**Max baseline:** 25 mm  
**Pairs:** 6 (R1-R2, R1-R3, R1-R4, R2-R3, R2-R4, R3-R4)  
**Expected improvement:** 84% better η recovery vs 3-transducer  
**Additional cost:** £25 (1 transducer)  

**Verdict:** Worth it for research-quality data and publication potential.

---

*Document created: March 13, 2026*  
*Configuration: 4-transducer array with DIY pulser*
