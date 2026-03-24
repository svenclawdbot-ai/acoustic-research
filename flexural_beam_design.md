# Flexural Beam Design for Shear Wave Generation
## Mechanical Coupling Solutions for Field-Deployable Systems

**Date:** March 16, 2026  
**Application:** Convert longitudinal piezo stack motion → transverse shear waves

---

## PHYSICS OF FLEXURAL CONVERSION

### How It Works

```
Piezo stack (longitudinal) → Base excitation → Beam bending → Tip (transverse)

     ↑ Longitudinal                  ↓ Transverse at tip
     motion                          (shear wave into tissue)
     
     ═══════════════════
     ║   PIEZO STACK     ║
     ═══════════════════
            │
     ┌──────┴──────┐
     │             │
     │  ALUMINUM   │  ← Bending mode
     │   BEAM      │
     │             │
     └──────┬──────┘
            │
        ═══════  ← Rounded tip contacts tissue
          TIP
```

### Governing Equation

Euler-Bernoulli beam with base excitation:

```
∂⁴w/∂x⁴ + (ρA/EI) ∂²w/∂t² = 0

where:
- w(x,t) = transverse displacement
- ρ = density
- A = cross-sectional area
- E = Young's modulus
- I = second moment of area
```

### Resonant Frequency

For cantilever beam with tip mass:

```
f₁ = (1/2π) √(k_eff / m_eff)

where:
k_eff = 3EI/L³ (cantilever stiffness)
m_eff = 0.23ρAL + m_tip (effective mass)
```

**Target:** f₁ = 100-200 Hz (shear wave frequency)

---

## DESIGN OPTION 1: Simple Cantilever (Beginner)

### Geometry
```
Material: Aluminum 6061-T6
Length (L): 60 mm
Width (b): 15 mm  
Thickness (h): 2 mm
Tip mass: 5 g (brass cylinder)
```

### Calculated Properties
```
I = bh³/12 = 15×(2)³/12 = 10 mm⁴ = 1×10⁻¹¹ m⁴
E = 69 GPa (aluminum)
ρ = 2700 kg/m³

k_eff = 3×69×10⁹×1×10⁻¹¹ / (0.06)³ = 9,600 N/m
m_beam = 0.23 × 2700 × (15×2×60)×10⁻⁹ = 1.1 g
m_eff = 1.1g + 5g = 6.1 g

f₁ = (1/2π) √(9600/0.0061) = 200 Hz ✓
```

### Fabrication
1. Cut aluminum strip (60×15×2 mm)
2. Drill 4 mm hole at base (for mounting)
3. Attach brass tip mass (M3 screw or epoxy)
4. Round tip to R5 mm radius
5. Bond piezo stack to base with epoxy

**Cost:** ~£5 in materials
**Build time:** 30 minutes
**Tools:** Hacksaw, drill, file

### Performance
| Parameter | Value |
|-----------|-------|
| Resonant frequency | 200 Hz |
| Q factor (aluminum) | 50-100 |
| Displacement gain | 15-30× |
| Tip displacement | 150-300 μm (from 10 μm piezo) |
| Effective shear force | ~1-2 N |

---

## DESIGN OPTION 2: Tuning Fork (Balanced)

### Geometry
```
Material: Aluminum 6061-T6
Total width: 40 mm
Tine width: 8 mm each
Tine length: 50 mm
Thickness: 2 mm
Gap between tines: 10 mm
```

### Assembly
```
Piezo stack excites base
         │
    ┌────┴────┐
    │ ═══════ │  ← Base block (15×40×10 mm)
    │  │   │  │
    │  │   │  │
    │  │   │  │  ← Two tines vibrate 180° out of phase
    │  │   │  │
    │  ▼   ▼  │
    │  ◯   ◯  │  ← Tips contact tissue
    └─────────┘
```

### Advantages
- **Balanced forces:** No net vibration transmitted to housing
- **Differential measurement:** Two contact points for shear sensing
- **Higher Q:** ~100-200 due to symmetry

### Calculated Properties (per tine)
```
I = 8×(2)³/12 = 5.3 mm⁴
k_eff = 3×69×10⁹×5.3×10⁻¹² / (0.05)³ = 8,800 N/m
m_eff ≈ 2 g (tine) + 3 g (tip) = 5 g
f₁ = 211 Hz ✓
```

### Fabrication
1. Machine from solid aluminum block, OR
2. Cut strip, bend U-shape, weld/solder joint

**Cost:** ~£8 in materials
**Build time:** 1-2 hours
**Tools:** Milling machine OR hacksaw + torch + solder

### Performance
| Parameter | Value |
|-----------|-------|
| Resonant frequency | 210 Hz |
| Q factor | 100-200 |
| Vibration isolation | Excellent |
| Tip displacement | 200-400 μm |

---

## DESIGN OPTION 3: Stacked Bimorph (High Displacement)

### Geometry
```
Two piezo elements bonded to center beam

     ↑ Voltage applied        ↓ Bending motion
     across thickness         (parallel to surface)
     
     ╔═══════════════╗
     ║  PIEZO (-)    ║
     ╠═══════════════╣
     ║  CENTER BEAM  ║  ← Brass or phosphor bronze
     ╠═══════════════╣
     ║  PIEZO (+)    ║
     ╚═══════════════╝
              │
           ═══════  ← Tip contact
```

### Dimensions
```
Material stack: Piezo + brass shim
Length: 40 mm
Width: 10 mm
Total thickness: 3 mm (1mm piezo + 0.5mm brass + 1mm piezo)
```

### Operation
- Voltage across piezo thickness induces extension/contraction
- Differential expansion creates bending
- **No separate stack needed** — piezo is the beam

### Calculated Properties
```
D = (2E_piezo×E_brass×(t_piezo+t_brass)×t_piezo×t_brass) / 
    (E_piezo×t_piezo + E_brass×t_brass)
    
≈ 0.05 N·m² (flexural rigidity)

f₁ ≈ 150 Hz for 40 mm length
Displacement: 50-100 μm at 100V (no mechanical gain needed)
```

### Advantages
- **No mechanical amplification needed** — piezo itself bends
- **Lower voltage** — 100V instead of 150V
- **Compact** — no separate stack
- **Bidirectional** — can apply ±V for push-pull

### Disadvantages
- **Fragile** — piezo ceramic in bending (risk of cracking)
- **Lower force** — can't drive stiff loads
- **Cost** — piezo bimorphs are £20-40 each

**Recommended sources:**
- Physik Instrumente (PI) Norex
- APC International bimorphs
- Custom: Bond PZT-5A discs to shim stock

---

## DESIGN OPTION 4: Torsional Mode (Shear-Optimized)

### Concept
Generate pure shear by twisting instead of bending.

```
Cross-section: Rectangular beam twisted about long axis

     ┌─────────────────┐
     │  PIEZO          │  ← Two stacks push differentially
     │  STACK A        │    (one up, one down)
     └────────┬────────┘
              │
     ╔════════╧════════╗
     ║                 ║
     ║   SQUARE BEAM   ║  ← Twists about centerline
     ║   (10×10 mm)    ║
     ║                 ║
     ╚════════╤════════╝
              │
         ═══════════  ← Flat tip (20×5 mm)
```

### Geometry
```
Beam: Steel drill rod, 10×10 mm, 80 mm long
Piezo stacks: Two 10×10×20 mm, differential drive
Tip: Flat plate 20×5 mm, soldered/brazed
```

### Operation
- Stack A extends, Stack B contracts → beam twists
- Tip moves **purely transversely** (shear)
- No normal force component

### Calculated Properties
```
Torsional stiffness: k_t = GJ/L
J = ab³[16/3 - 3.36(b/a)(1-b⁴/12a⁴)] ≈ 800 mm⁴ (for 10×10 mm)
G = 79 GPa (steel shear modulus)
k_t = 79×10⁹×8×10⁻¹⁰ / 0.08 = 790 N·m/rad

With piezo force F = 100 N, moment arm d = 5 mm:
θ = F×d/k_t = 0.1×0.005/790 = 6.3×10⁻⁴ rad

Tip displacement: δ = θ×L = 50 μm at 100 mm
```

### Advantages
- **Pure shear** — no compressional component
- **High stiffness** — good contact consistency
- **Differential drive** — common-mode rejection

### Disadvantages
- **Complex fabrication** — requires machining
- **Alignment sensitive** — stacks must be matched
- **Heavy** — steel construction

**Best for:** Laboratory validation, not field

---

## COMPARISON TABLE

| Design | Cost | Complexity | Displacement | Robustness | Best For |
|--------|------|-----------|--------------|-----------|----------|
| **Simple Cantilever** | £5 | Low | 150-300 μm | Good | **Field deployment** |
| **Tuning Fork** | £8 | Medium | 200-400 μm | Excellent | Handheld probe |
| **Piezo Bimorph** | £30 | Low | 50-100 μm | Poor | Low-force applications |
| **Torsional** | £25 | High | 50 μm | Excellent | Lab validation |

---

## RECOMMENDED: Simple Cantilever + Improvements

### Enhanced Design for Field Use

```
┌─────────────────────────────────────────┐
│           HOUSING (3D printed)          │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │  COMPRESSION SPRING (0.5 N)     │    │
│  │           ↓                     │    │
│  │  ┌─────────────────────────┐    │    │
│  │  │    PIEZO STACK          │    │    │
│  │  │    10×10×20 mm          │    │    │
│  │  │    (Preload: 0.5 N)     │    │    │
│  │  └──────────┬──────────────┘    │    │
│  │             │                   │    │
│  │  ┌──────────┴──────────┐        │    │
│  │  │   ALUMINUM BEAM     │        │    │
│  │  │   60×15×2 mm        │        │    │
│  │  │   (200 Hz resonant) │        │    │
│  │  │                     │        │    │
│  │  │   SILICONE          │        │    │
│  │  │   MATCHING LAYER    │        │    │
│  │  │   (1 mm thick)      │        │    │
│  │  │                     │        │    │
│  │  │   ═══════════════   │        │    │
│  │  │   R5 TIP RADIUS     │◄───────┼────┼─── Tissue contact
│  │  └─────────────────────┘        │    │
│  └─────────────────────────────────┘    │
│                                         │
│  [FORCE SENSOR] ← Optional for feedback │
│                                         │
└─────────────────────────────────────────┘
```

### Key Improvements

1. **Spring preload:** Maintains contact despite motion
2. **Silicone matching layer:** 1 mm of Shore A30 silicone
   - Impedance: ~0.5 MRayl (intermediate between tissue and aluminum)
   - Increases energy transmission ~3×
3. **Rounded tip:** R5 mm conforms to curved surfaces
4. **Optional force sensor:** FSR or strain gauge for contact verification

### Bill of Materials

| Component | Spec | Qty | Cost |
|-----------|------|-----|------|
| Aluminum strip | 60×15×2 mm | 1 | £2 |
| Piezo stack | 10×10×20 mm, 150V | 1 | £40 |
| Compression spring | 0.5 N/mm, 10 mm | 1 | £3 |
| Silicone sheet | 1 mm, Shore A30 | 1 | £5 |
| 3D printed housing | PLA/PETG | 1 | £5 |
| Screws, nuts | M3 stainless | Assort | £3 |
| **Total** | | | **£58** |

---

## FABRICATION PROTOCOL

### Step 1: Beam Preparation (15 min)
1. Cut aluminum to 60×15×2 mm
2. Drill 4 mm hole 10 mm from end (mounting)
3. File tip to R5 radius
4. Sand surface to 400 grit
5. Clean with isopropanol

### Step 2: Assembly (20 min)
1. Bond silicone layer to beam tip (silicone adhesive)
2. Mount piezo stack to beam base (epoxy, 24 hr cure)
3. Install in housing with spring preload
4. Wire piezo to connector

### Step 3: Tuning (10 min)
1. Measure resonant frequency (impact test or chirp)
2. If f < target: Shorten beam (file end)
3. If f > target: Add tip mass (brass washer)
4. Target: 150-200 Hz

### Step 4: Testing (15 min)
1. Drive with 100V, 200 Hz sine
2. Measure tip displacement (microscope or LDV)
3. Verify: >100 μm displacement
4. Test on phantom: Should generate clear shear wave

---

## PERFORMANCE VALIDATION

### Expected Results

| Test | Target | Pass Criteria |
|------|--------|--------------|
| Resonant frequency | 200 Hz | ±20 Hz |
| Q factor | >50 | >30 minimum |
| Tip displacement | 150 μm | >100 μm |
| Shear wave SNR | 20 dB | >10 dB |
| Repeatability | <5% | <10% variance |

### Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| No resonance | Loose bond | Re-epoxy, clamp during cure |
| Low Q | Material damping | Use aluminum instead of steel |
| Frequency drift | Temperature | Limit to 15-35°C operation |
| Inconsistent contact | Insufficient preload | Increase spring force |
| Double resonance | Asymmetric tip | Balance mass distribution |

---

## NEXT STEPS

1. **Procure materials** (£60 budget)
2. **Fabricate 3 prototypes** (test repeatability)
3. **Characterize on steel block** (known reference)
4. **Test on gelatin phantom** (tissue-equivalent)
5. **Integrate with ESP32 + MEMS** (full system)

Ready to proceed with procurement, or need CAD drawings for the housing?
