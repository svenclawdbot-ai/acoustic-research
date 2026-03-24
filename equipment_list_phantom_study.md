# Experimental Equipment List: Shear Wave Elastography Phantom Study

## Project: Validation of Viscoelastic Models (KV, Zener, Power-Law)

---

## 1. PHANTOM FABRICATION

### Core Materials
| Item | Specification | Qty | Est. Cost | Supplier |
|------|--------------|-----|-----------|----------|
| Gelatin, Type A | 300 Bloom, porcine skin | 1 kg | £45 | Sigma-Aldrich (G2500) |
| Gelatin, Type B | 200 Bloom, bovine | 1 kg | £40 | Sigma-Aldrich (G9391) |
| Graphite powder | 99%, 50 μm particle | 500 g | £25 | Sigma-Aldrich (332461) |
| Cellulose fibres | Microcrystalline | 250 g | £30 | Sigma-Aldrich (435236) |
| Propylene glycol | USP grade (softener) | 500 ml | £15 | Fisher Scientific |
| Formaldehyde | 37% solution (crosslinker) | 100 ml | £20 | Sigma-Aldrich |

### Mold Fabricature
| Item | Specification | Qty | Est. Cost | Supplier |
|------|--------------|-----|-----------|----------|
| Acrylic sheets | 5 mm, cast | 4× A4 | £40 | RS Components |
| Acrylic cement | Tensol 12 or equivalent | 1 | £15 | RS Components |
| Silicone molds | Cylindrical, 60 mm × 100 mm | 3 | £60 | Custom/Smooth-On |
| Release agent | Silicone spray | 1 | £12 | RS Components |
| Mixing vessels | Polypropylene, 1L | 5 | £15 | Lab supplier |

**Phantom Fabrication Subtotal: ~£340**

---

## 2. WAVE GENERATION SYSTEM

### Option A: Piezoelectric Transducers (Recommended)
| Item | Specification | Qty | Est. Cost | Supplier |
|------|--------------|-----|-----------|----------|
| Shear wave transducers | 100 kHz, 10 mm diameter | 2 | £400 | Olympus/Verasonics |
| Compression transducers | 1 MHz, 12 mm diameter | 2 | £300 | Olympus |
| Signal generator | 25 MHz, arbitrary waveform | 1 | £800 | Rigol DG5252 or equivalent |
| Power amplifier | 50 W, 40 dB gain, 200 kHz BW | 1 | £600 | Falco Systems WMA-300 |
| Matching network | Tunable L-network | 1 | £150 | Custom build |
| Transducer holders | XYZ micrometer stage | 2 | £400 | Thorlabs PT1/M |

**Piezo Option Subtotal: ~£2,650**

### Option B: Acoustic Radiation Force (ARFI)
| Item | Specification | Qty | Est. Cost | Supplier |
|------|--------------|-----|-----------|----------|
| Focused transducer | 2.5 MHz, f/2, 38 mm focal | 1 | £600 | Olympus A309S |
| Ultrasound system | Research platform (open) | 1 | £5,000+ | Verasonics Vantage |
| OR: USB oscilloscope | 100 MHz, 2 ch | 1 | £400 | Picoscope 3403D |

**ARFI Option Subtotal: ~£6,000+ (or £1,000 with USB scope)**

---

## 3. DETECTION SYSTEM

### Option A: Laser Doppler Vibrometry (Gold Standard)
| Item | Specification | Qty | Est. Cost | Supplier |
|------|--------------|-----|-----------|----------|
| Laser vibrometer | 0-50 kHz, velocity | 1 | £8,000 | Polytec OFV-5000 (used) |
| OR: Single-point LDV | Entry level | 1 | £3,500 | Polytec PDV-100 |
| Reflective tape | Microprismatic | 1 roll | £25 | 3M Scotchlite |
| Positioning stage | Linear, 100 mm travel | 1 | £500 | Thorlabs NRT100/M |

**LDV Subtotal: £3,500-£8,500**

### Option B: Ultrasonic Pulse-Echo (Cost-Effective)
| Item | Specification | Qty | Est. Cost | Supplier |
|------|--------------|-----|-----------|----------|
| Receiving transducer | 5 MHz, broadband | 1 | £250 | Olympus V310 |
| Preamplifier | 40 dB, low noise | 1 | £300 | Olympus 5660B |
| Digitizer | 50 MHz, 14-bit | 1 | £1,200 | NI USB-5133 |
| Positioning | Manual scan stage | 1 | £200 | Custom build |

**Pulse-Echo Subtotal: ~£1,950**

### Option C: Optical (Research-Grade DIY)
| Item | Specification | Qty | Est. Cost | Supplier |
|------|--------------|-----|-----------|----------|
| Laser diode | 635 nm, 50 mW, modulated | 1 | £150 | Thorlabs L635P005 |
| Photodetector | 100 MHz bandwidth | 1 | £200 | Thorlabs DET10A2 |
| Interferometer setup | Michelson configuration | 1 | £500 | Optics + Thorlabs |
| Vibration isolation | Optical table or pads | 1 | £300 | Thorlabs |

**Optical DIY Subtotal: ~£1,150**

---

## 4. DATA ACQUISITION & CONTROL

| Item | Specification | Qty | Est. Cost | Supplier |
|------|--------------|-----|-----------|----------|
| Oscilloscope | 200 MHz, 4 ch, deep memory | 1 | £1,200 | Keysight DSOX1204G |
| DAQ system | 16-bit, 250 kS/s/ch, 4 ch | 1 | £800 | NI USB-4431 |
| Computer | i7, 16GB, SSD for real-time | 1 | £800 | Standard PC |
| Python/MATLAB | Data analysis software | - | £0/£500 | Open source/MathWorks |
| Cables & connectors | BNC, SMA, coaxial | Assortment | £150 | RS Components |
| Anti-vibration mat | 600×600 mm | 1 | £80 | Thorlabs |

**DAQ Subtotal: ~£3,030**

---

## 5. CHARACTERIZATION TOOLS

| Item | Specification | Qty | Est. Cost | Supplier |
|------|--------------|-----|-----------|----------|
| Dynamic mechanical analyzer | For material validation | Access | £0 | University facility |
| Tensile tester | For elastic modulus | Access | £0 | University facility |
| Caliper/digital micrometer | 0.01 mm resolution | 1 | £50 | Mitutoyo |
| Thermometer/Hygrometer | Lab grade | 1 | £30 | RS Components |
| pH meter | For gel preparation | 1 | £80 | Fisher Scientific |
| Balance | 0.01 g resolution | 1 | £200 | Mettler Toledo |
| Hot plate/stirrer | For gelatin dissolution | 1 | £150 | IKA |

**Characterization Subtotal: ~£510**

---

## 6. CONSUMABLES (6-month supply)

| Item | Specification | Qty | Est. Cost |
|------|--------------|-----|-----------|
| Distilled water | 20 L containers | 4 | £40 |
| Isopropyl alcohol | 99%, cleaning | 5 L | £25 |
| Lint-free wipes | Electronics grade | 1 box | £15 |
| Gloves | Nitrile, powder-free | 1 box | £12 |
| Pipette tips | Various sizes | Assorted | £30 |
| Parafilm | Sealing | 1 roll | £15 |

**Consumables Subtotal: ~£140**

---

## TOTAL COST ESTIMATES

### Budget Option (Pulse-echo detection, piezo generation)
| Category | Cost |
|----------|------|
| Phantom fab | £340 |
| Generation | £2,650 |
| Detection (pulse-echo) | £1,950 |
| DAQ | £3,030 |
| Characterization | £510 |
| Consumables | £140 |
| **Total** | **~£8,600** |

### Recommended Option (Entry LDV, piezo generation)
| Category | Cost |
|----------|------|
| Phantom fab | £340 |
| Generation | £2,650 |
| Detection (LDV) | £3,500 |
| DAQ | £3,030 |
| Characterization | £510 |
| Consumables | £140 |
| **Total** | **~£10,200** |

### Full System (Research-grade LDV, ARFI)
| Category | Cost |
|----------|------|
| Phantom fab | £340 |
| Generation (ARFI) | £6,000 |
| Detection (full LDV) | £8,500 |
| DAQ | £3,030 |
| Characterization | £510 |
| Consumables | £140 |
| **Total** | **~£18,500** |

---

## RECOMMENDED SUPPLIERS

| Supplier | Specialization | Contact |
|----------|---------------|---------|
| **Thorlabs** | Optomechanics, lasers | www.thorlabs.com |
| **Olympus/EVIDENT** | Ultrasonic transducers | www.olympus-ims.com |
| **Verasonics** | Research ultrasound | www.verasonics.com |
| **Polytec** | Laser vibrometry | www.polytec.com |
| **National Instruments** | DAQ systems | www.ni.com |
| **Sigma-Aldrich** | Chemicals, materials | www.sigmaaldrich.com |
| **RS Components** | Electronics, hardware | uk.rs-online.com |
| **Farnell** | Electronics | uk.farnell.com |

---

## EQUIPMENT AVAILABILITY CHECKLIST

### To verify before ordering:
- [ ] Access to mechanical testing lab (DMA, tensile tester)
- [ ] Clean room or dust-free environment for optics
- [ ] Vibration isolation (existing optical table?)
- [ ] Temperature-controlled environment (±1°C)
- [ ] Safety approval for laser use (if LDV selected)
- [ ] Electrical safety check for high-voltage amplifier

### Space requirements:
- Optical table or vibration-isolated bench: 1.5 m × 0.8 m minimum
- Phantom preparation area: 1 m × 0.6 m
- Storage for chemicals: Fume hood or ventilated cabinet

---

## NOTES

1. **Transducer frequencies**: 100 kHz shear waves provide ~2 cm wavelength in soft tissue (c_s ≈ 2 m/s). Lower frequencies penetrate deeper; higher frequencies give better resolution.

2. **Gelatin phantoms**: Type A (acid-processed) gives clearer gels than Type B. Graphite adds scattering for ultrasound visibility. Cellulose adds structural integrity.

3. **LDV alternative**: If budget constrained, consider borrowing from university mechanical engineering or vibration lab.

4. **Ultrasound system**: Verasonics Vantage is the gold standard for research but expensive. Consider collaborating with clinical ultrasound group.

5. **Timeline**: Allow 4-6 weeks for delivery of custom transducers and LDV systems.

---

*Equipment list prepared: March 16, 2026*
*For: Acoustic NDE / Shear Wave Elastography Research Project*
