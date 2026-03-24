# 3.5 MHz Focused Ultrasound Transducer — Specification Sheet
**Design Reference:** TR-3.5-PHANTOM-001  
**Date:** 2026-03-18  
**Application:** Phantom imaging, research calibration

---

## 1. ACOUSTIC SPECIFICATIONS

### Operating Parameters
| Parameter | Value | Notes |
|-----------|-------|-------|
| Centre frequency (f₀) | 3.5 MHz | ±5% tolerance |
| -6 dB bandwidth | 1.5–5.5 MHz | ~114% fractional BW |
| Pulse duration | ~0.5 μs | -20 dB envelope |
| Pulse repetition rate | 1–10 kHz | Adjustable |
| Maximum pressure | <0.5 MPa | MI < 0.7 for phantom safety |

### Geometry & Focusing
| Parameter | Value | Derivation |
|-----------|-------|------------|
| Active aperture diameter (D) | 19 mm | Standard ½" crystal |
| Radius of curvature (R) | 40 mm | Focal depth |
| f-number | f/2.1 | R/D = 40/19 |
| Near-field length (N) | 205 mm | D²/(4λ) |
| Focal position | N/5.1 | Within near-field (optimal) |

### Resolution Performance
| Parameter | Value | Formula |
|-----------|-------|---------|
| Wavelength (λ) | 0.44 mm | c/f = 1540/(3.5×10⁶) |
| **Lateral resolution (-6 dB)** | **0.90 mm** | 1.02 × λ × f/# |
| **Axial resolution (-6 dB)** | **0.22 mm** | 0.5 × λ (pulse length) |
| Focal zone depth (-6 dB) | 4.0 mm | 7.0 × λ × (f/#)² |
| Depth of field (-20 dB) | ~12 mm | 3× focal zone |

### Beam Characteristics (Phantom: c=1540 m/s, ρ=1000 kg/m³)
| Depth | Beam Width | Intensity | Notes |
|-------|------------|-----------|-------|
| 20 mm | 1.8 mm | -6 dB | Pre-focal (converging) |
| **40 mm** | **0.9 mm** | **0 dB** | **Focal point** |
| 60 mm | 2.1 mm | -6 dB | Post-focal (diverging) |
| 80 mm | 3.2 mm | -12 dB | Far field (Sidelobes visible) |

---

## 2. MATERIAL SELECTION

### Active Element
| Property | PZT-5H | Notes |
|----------|--------|-------|
| Acoustic impedance (Z) | 34.5 MRayl | High energy conversion |
| Coupling coefficient (kₜ) | 0.50 | Strong thickness mode |
| Dielectric constant (ε₃₃) | 3400 | Good for matching |
| Thickness (t) | **0.64 mm** | t = λ/2 = c/(2f) |
| Mechanical Q | 65 | Moderate damping |

### Backing Material
| Property | Tungsten-epoxy (3:1) | Purpose |
|----------|---------------------|---------|
| Acoustic impedance (Z) | 3.6 MRayl | Heavy backing for short pulse |
| Attenuation | >400 dB/cm @ 3.5 MHz | Eliminate ring-down |
| Thickness | >3 mm | >5λ for complete absorption |
| Bonding | Epoxy (Epo-Tek 301) | Vacuum degas, 24h cure |

**Trade-off:** Heavy backing reduces pulse length (0.5 μs) but reduces sensitivity by ~15 dB. Acceptable for phantom work requiring resolution.

### Matching Layer
| Property | Impedance-graded epoxy | Purpose |
|----------|----------------------|---------|
| Target impedance (Z) | 3.0–3.5 MRayl | √(Z_pzt × Z_phantom) |
| Composition | Alumina-loaded epoxy | 40% Al₂O₃ by weight |
| Thickness | **0.11 mm** | λ/4 = c/(4f×Z_ratio) |
| Attenuation | <2 dB @ 3.5 MHz | Minimal insertion loss |
| Bonding | Same as backing | Thin, uniform layer |

**Double matching option:**
- Layer 1: 4.5 MRayl, 55 μm (facing PZT)
- Layer 2: 2.3 MRayl, 83 μm (facing tissue)
- Broader bandwidth (~130%) but harder to fabricate

### Housing
| Component | Material | Notes |
|-----------|----------|-------|
| Housing | Brass (nickel-plated) | RF shielding |
| Lens | PMMA (acrylic) | Concave, R=40 mm |
| Cable | RG174/U, 50 Ω | 1.5 m, shielded |
| Connector | BNC or SMA | Match pulser impedance |

---

## 3. ELECTRICAL SPECIFICATIONS

| Parameter | Value | Notes |
|-----------|-------|-------|
| Electrical impedance | 20–30 Ω (real) @ f₀ | Parallel resonance |
| Capacitance | 250–350 pF | Depends on electrode area |
| Tuning | Series inductor 6.5 μH | Cancel capacitance @ 3.5 MHz |
| Drive voltage | ±50–100 V | 2-cycle tone burst typical |
| Sensitivity | -50 dB re 1 V/μPa | Receive mode (estimated) |

### Impedance Matching Network
```
PZT (Cp ≈ 300 pF) --- Ls (6.5 μH) --- 50 Ω Pulser/Receiver
                     |
                    Cs (optional for fine-tuning)
```

Calculated Q ≈ 3–5 for 1.5 MHz bandwidth.

---

## 4. PULSE-ECHO SENSITIVITY ANALYSIS

### Two-Way Insertion Loss Budget
| Component | Loss (dB) | Notes |
|-----------|-----------|-------|
| Matching layer | -0.5 | Optimized λ/4 transformer |
| Tissue coupling | -0.3 | Ultrasound gel interface |
| Phantom attenuation (round-trip) | -2.0 | 0.5 dB/cm/MHz² × 8 cm × 3.5² |
| Target reflection (anechoic cyst) | -40 | Edge diffraction from 2 mm cyst |
| **Received signal** | **-42.8 dB** | Relative to transmit |
| System noise floor | -60 dB | With 40 dB gain |
| **Dynamic range margin** | **17.2 dB** | Acceptable for imaging |

### Key Assumptions
- Phantom: ATS 539 or equivalent (μ = 0.5 dB/cm/MHz²)
- Target: 2 mm diameter anechoic cyst at 40 mm depth
- System: 40 dB TGC, 50 Ω impedance
- Cable: <1 dB loss at 3.5 MHz (1.5 m RG174)

### Signal-to-Noise Ratio Estimate
| Scenario | SNR (dB) | Image Quality |
|----------|----------|---------------|
| Specular reflector (plane interface) | 45 dB | Excellent |
| 2 mm anechoic cyst | 25 dB | Good (detectable) |
| 1 mm anechoic cyst | 15 dB | Fair (visible, reduced contrast) |
| Speckle region | 20 dB (peak-to-peak) | Standard for B-mode |

---

## 5. FABRICATION NOTES

### Process Flow
1. **PZT preparation:** Dice 0.64 mm thick PZT-5H sheet to 19 mm diameter
2. **Electroplating:** Chrome/gold electrodes (500 Å) on both faces
3. **Backing:** Cast tungsten-epoxy (3:1 ratio) in vacuum, cure 24h at 60°C
4. **Matching layer:** Spin-cast alumina-loaded epoxy to 110 μm, cure 12h
5. **Housing:** Press-fit into brass housing with ground electrode contact
6. **Lens bonding:** Epoxy concave PMMA lens (R=40 mm) to front surface
7. **Cable:** Solder coaxial cable, seal with potting compound
8. **Testing:** Impedance analyzer sweep, pulse-echo in water tank

### Quality Control Checkpoints
- [ ] Impedance: 20–30 Ω @ 3.5 MHz
- [ ] Bandwidth: >100% (-6 dB)
- [ ] Pulse duration: <0.6 μs
- [ ] Focal length: 40 ± 2 mm (water tank)
- [ ] Sidelobe level: <-20 dB

---

## 6. TESTING PROTOCOL

### Phantom Validation (ATS 539 or CIRS 040)
1. **Axial resolution:** Visualize 0.05 mm wire targets at 30, 40, 50 mm
2. **Lateral resolution:** Measure -6 dB beam width at focal plane
3. **Contrast resolution:** Detect 2 mm anechoic cysts at 40 mm depth
4. **Penetration:** Image to 80 mm with acceptable SNR (>10 dB)
5. **Uniformity:** Check for ring-down artifacts and reverberation

### Expected Results
- Axial: 0.20–0.25 mm (wire targets)
- Lateral @ 40 mm: 0.85–0.95 mm
- Cyst detection: 2 mm @ 40 mm depth (90% confidence)

---

## 7. SUMMARY TABLE

| Spec | Value |
|------|-------|
| Centre frequency | 3.5 MHz |
| Aperture diameter | 19 mm |
| Focal depth | 40 mm |
| f-number | f/2.1 |
| Lateral resolution | 0.90 mm |
| Axial resolution | 0.22 mm |
| Active element | PZT-5H, 0.64 mm thick |
| Backing | Tungsten-epoxy (3:1), 3.6 MRayl |
| Matching layer | Alumina-epoxy, 0.11 mm thick, 3.2 MRayl |
| Housing | Brass with PMMA lens |
| Electrical impedance | 25 Ω @ 3.5 MHz |
| Bandwidth (-6 dB) | 114% (1.5–5.5 MHz) |
| Pulse duration | 0.5 μs |

---

**Document generated:** 2026-03-18 07:17 UTC  
**Design reference:** TR-3.5-PHANTOM-001  
**Next action:** Fabrication or FEM simulation validation
