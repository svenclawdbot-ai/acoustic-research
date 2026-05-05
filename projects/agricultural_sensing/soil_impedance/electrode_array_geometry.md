# Electrode Array Geometry for Soil Impedance Sensing

*Date: 2026-04-27*
*Project: Agricultural Sensing — Soil Impedance Spectroscopy*

---

## Design Goals

1. **Eliminate contact resistance** — 4-electrode (Wenner) configuration
2. **Depth discrimination** — Variable electrode spacing
3. **Spatial mapping** — 8 channels across field
4. **Field-deployable** — Robust, waterproof, easy insertion
5. **Cost-effective** — Stainless steel or graphite, not Ag/AgCl

---

## 4-Electrode (Wenner) Array Theory

### Principle

Current is injected through outer electrodes (A, B). Voltage is measured across inner electrodes (M, N). Because no current flows through the voltage sense electrodes, contact resistance at M and N does not affect the measurement.

```
        A ────── M ────── N ────── B
        │        │        │        │
        ●        ●        ●        ●
        │        │        │        │
        └────────┴────────┴────────┘
                 SOIL
                 
        A, B = Current electrodes (outer)
        M, N = Voltage electrodes (inner)
        a    = Spacing between adjacent electrodes
```

### Apparent Resistivity

For Wenner array with equal spacing:

$$
\rho_a = 2\pi a \frac{V_{MN}}{I_{AB}}
$$

Where:
- ρ_a = apparent resistivity (Ω·m)
- a = electrode spacing (m)
- V_MN = measured voltage (V)
- I_AB = injected current (A)

### Depth of Investigation

The Wenner array samples a hemisphere with radius ≈ 1.5a:

| Spacing (a) | Investigation Depth | Application |
|-------------|---------------------|-------------|
| 5 cm | ~7.5 cm | Seedbed, topsoil moisture |
| 10 cm | ~15 cm | Root zone (shallow crops) |
| 20 cm | ~30 cm | Root zone (deep crops) |
| 50 cm | ~75 cm | Deep moisture, drainage |

---

## Array Configurations

### Option 1: Linear Wenner Array (Single Depth)

```
    ┌─────────────────────────────────────────┐
    │          LINEAR 4-ELECTRODE ARRAY        │
    │                                          │
    │   A        M        N        B            │
    │   ●────────●────────●────────●           │
    │   │        │        │        │           │
    │   │   a    │   a    │   a    │           │
    │   │        │        │        │           │
    │   └────────┴────────┴────────┘           │
    │              SOIL VOLUME                  │
    │                                          │
    │   Spacing: a = 10cm (typical)            │
    │   Total length: 3a = 30cm                 │
    │   Investigation depth: ~15cm              │
    └─────────────────────────────────────────┘
```

**Pros:** Simple, well-understood, easy to model
**Cons:** Single depth only, requires 4 wires per channel

### Option 2: Multi-Depth Array (Vertical Stack)

```
    ┌─────────────────────────────────────────┐
    │         VERTICAL MULTI-DEPTH ARRAY       │
    │                                          │
    │   A1 ──── M1 ──── N1 ──── B1            │  ← Depth 1 (5cm)
    │   ●───────●───────●───────●             │
    │   │       │       │       │             │
    │   A2 ──── M2 ──── N2 ──── B2            │  ← Depth 2 (15cm)
    │   ●───────●───────●───────●             │
    │   │       │       │       │             │
    │   A3 ──── M3 ──── N3 ──── B3            │  ← Depth 3 (25cm)
    │   ●───────●───────●───────●             │
    │   │       │       │       │             │
    │   └───────┴───────┴───────┘             │
    │              SOIL PROFILE                 │
    │                                          │
    │   3 depths × 4 electrodes = 12 pins      │
    │   Requires 3 MUX channels (one per depth)│
    └─────────────────────────────────────────┘
```

**Pros:** Vertical moisture profile, matches root zone architecture
**Cons:** More electrodes, complex wiring, mechanical stability

### Option 3: Azimuthal Array (Radial — Recommended)

```
    ┌─────────────────────────────────────────┐
    │         AZIMUTHAL RADIAL ARRAY           │
    │                                          │
    │              Center                      │
    │                ●                         │
    │                │                         │
    │    A ●────────┼────────● B               │
    │      │        │        │                │
    │      │    M ●─┼─● N    │                │
    │      │        │        │                │
    │      │        │        │                │
    │      └────────┴────────┘                │
    │                                          │
    │   Current injected radially (A→B)        │
    │   Voltage measured at M, N                 │
    │   Symmetric about center                  │
    │                                          │
    │   Advantage: Compact, shared center       │
    │   electrode reduces pin count            │
    └─────────────────────────────────────────┘
```

**Pros:** Compact, shared electrodes, good for small probes
**Cons:** Less standard, requires careful symmetry

### Option 4: 8-Channel Field Mapping Array (Recommended for V5)

```
    ┌─────────────────────────────────────────┐
    │      8-CHANNEL FIELD MAPPING ARRAY        │
    │                                          │
    │   CH0    CH1    CH2    CH3               │
    │   ●──────●──────●──────●                 │  ← Row 1 (10cm depth)
    │   │ 50cm │ 50cm │ 50cm │                 │
    │   │      │      │      │                 │
    │   ●──────●──────●──────●                 │  ← Row 2 (30cm depth)
    │   │      │      │      │                 │
    │   ●──────●──────●──────●                 │  ← Row 3 (50cm depth)
    │   CH4    CH5    CH6    CH7               │
    │                                          │
    │   Grid: 4 columns × 3 depths = 12 points  │
    │   But only 8 channels → 8 active at once  │
    │                                          │
    │   Each "●" = 4-electrode Wenner cell     │
    │   (A, M, N, B compressed into one probe)│
    └─────────────────────────────────────────┘
```

**Pros:** Spatial mapping, depth profiling, matches V5 8-channel MUX
**Cons:** Complex mechanical design, many electrodes

---

## Electrode Design Details

### Geometry

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Diameter | 6–10 mm | Sufficient contact area, easy insertion |
| Length (exposed) | 20–50 mm | Matches investigation depth |
| Tip shape | Conical 60° | Easy insertion, minimal soil disturbance |
| Surface finish | Smooth (Ra < 1µm) | Reduces polarisation |

### Materials

| Material | Cost | Durability | Polarisation | Best For |
|----------|------|------------|--------------|----------|
| **Stainless 316L** | Low | Excellent | Moderate | General purpose, long-term burial |
| **Graphite** | Low | Good | Low | Low-frequency (<1kHz), research |
| **Ag/AgCl** | High | Poor (fouls) | Very low | Reference standard, calibration |
| **Titanium** | Medium | Excellent | Low | Saline soils, coastal |
| **Platinum** | Very high | Excellent | Very low | Research, precision |

**Recommendation:** 316L stainless for field deployment. Graphite for research/calibration.

### Spacing Guidelines

```
    Minimum spacing: a ≥ 5 × electrode diameter
    → For 8mm electrodes: a ≥ 40mm
    
    Typical agricultural spacing:
    • Shallow (seedbed): a = 5–10 cm
    • Root zone: a = 10–20 cm
    • Deep drainage: a = 20–50 cm
```

---

## Mechanical Design

### Probe Body

```
    ┌─────────────────────────────────────────┐
    │           PROBE CROSS-SECTION             │
    │                                          │
    │   ┌─────────────────────────────┐       │
    │   │      PVC/HDPE tube          │       │  ← 25mm OD, 2mm wall
    │   │   ┌─────────────────────┐   │       │
    │   │   │   Internal cavity   │   │       │
    │   │   │   (wiring, epoxy)   │   │       │
    │   │   └─────────────────────┘   │       │
    │   │        │  │  │  │            │       │
    │   └────────┴──┴──┴──┴────────────┘       │
    │        E1  E2  E3  E4                    │
    │        ↑   ↑   ↑   ↑                     │
    │        A   M   N   B                     │
    │                                          │
    │   Electrodes: 4 × 8mm SS rods           │
    │   Spacing: 20mm (a = 20mm)              │
    │   Depth: 200mm insertion                 │
    │   Cable: 4-core shielded, 5m length      │
    │   Connector: IP67 M12                    │
    └─────────────────────────────────────────┘
```

### 8-Channel Probe Array (Field Version)

```
    ┌─────────────────────────────────────────┐
    │         FIELD DEPLOYMENT ARRAY           │
    │                                          │
    │    ●──────●──────●──────●               │  ← 4 probes, 1m spacing
    │    │      │      │      │                │
    │    │      │      │      │                │
    │    ●──────●──────●──────●               │  ← 4 more probes
    │                                          │
    │    Each ● = 4-electrode probe            │
    │    Connected to V5 MUX via M12 cables    │
    │    Total: 8 probes × 4 electrodes = 32  │
    │    But only 8 channels active at once    │
    │                                          │
    │    Alternative: 2 depths × 4 locations    │
    │    = 8 channels fully utilised           │
    └─────────────────────────────────────────┘
```

---

## Electrical Interface to V5

### Wiring Diagram

```
    ┌─────────────────────────────────────────┐
    │         V5 MUX CONNECTION                │
    │                                          │
    │   Probe 0 (CH0)                        │
    │   ┌─────────────────────────┐            │
    │   │ A0 ──→ MUX0 IN0        │            │
    │   │ M0 ──→ MUX0 IN1        │            │
    │   │ N0 ──→ MUX0 IN2        │            │
    │   │ B0 ──→ MUX0 IN3        │            │
    │   └─────────────────────────┘            │
    │        │                                 │
    │        ↓                                 │
    │   DG408 MUX0 (4:1)                     │
    │        │                                 │
    │        ↓                                 │
    │   OPA1641 LNA                            │
    │        │                                 │
    │        ↓                                 │
    │   Red Pitaya ADC                         │
    │                                          │
    │   Note: Only 1 electrode pair active    │
    │   at a time per probe. Full 4-electrode │
    │   requires 2 MUX channels per probe.    │
    └─────────────────────────────────────────┘
```

### Simplified: 2-Electrode Mode (Compromise)

For 8 independent channels with 2-electrode measurement:

```
    ┌─────────────────────────────────────────┐
    │      SIMPLIFIED 2-ELECTRODE ARRAY        │
    │                                          │
    │   CH0    CH1    CH2    CH3    CH4 ...   │
    │   ●      ●      ●      ●      ●         │  ← Drive electrodes
    │   │      │      │      │      │         │
    │   └──────┴──────┴──────┴──────┘         │
    │              Common return               │
    │              ●──────────●                │  ← Sense electrodes
    │                                          │
    │   Each channel: drive vs common          │
    │   Measures: bulk impedance (not true    │
    │   resistivity, but sufficient for       │
    │   relative moisture mapping)            │
    └─────────────────────────────────────────┘
```

**Trade-off:** Loses contact resistance elimination, but gains 8 independent points.

---

## Calibration & Error Sources

### Contact Resistance

| Soil Type | Expected R_contact | Mitigation |
|-----------|-------------------|------------|
| Sandy (dry) | 1–10 kΩ | Wet electrodes before insertion |
| Sandy (wet) | 100–500 Ω | 4-electrode eliminates this |
| Clay (dry) | 500 Ω–2 kΩ | Sharp tips, firm insertion |
| Clay (wet) | 50–200 Ω | Minimal issue |
| Compacted | 200 Ω–1 kΩ | Pre-drill if needed |

### Temperature Correction

Soil electrical conductivity increases ~2% per °C:

$$
EC_{25} = \frac{EC_T}{1 + 0.02(T - 25)}
$$

Always measure soil temperature and correct to 25°C reference.

### Salinity Effects

| EC_e (dS/m) | Classification | Crop Impact |
|-------------|----------------|-------------|
| < 0.7 | Non-saline | None |
| 0.7–2.0 | Slightly saline | Sensitive crops affected |
| 2.0–4.0 | Moderately saline | Most crops affected |
| 4.0–8.0 | Highly saline | Only tolerant crops |
| > 8.0 | Very highly saline | Few crops survive |

---

## Recommended Array for V5

### Final Design: 2-Depth × 4-Location Array

```
    ┌─────────────────────────────────────────┐
    │    V5 OPTIMISED SOIL SENSOR ARRAY        │
    │                                          │
    │   Location:    0      1      2      3   │
    │                 │      │      │      │    │
    │   Depth 1:     ●      ●      ●      ●   │  ← 10cm (CH0-CH3)
    │   (10cm)       │      │      │      │    │
    │                │      │      │      │    │
    │   Depth 2:     ●      ●      ●      ●   │  ← 30cm (CH4-CH7)
    │   (30cm)       │      │      │      │    │
    │                                          │
    │   Each ● = 4-electrode Wenner probe      │
    │   Spacing between locations: 50cm        │
    │   Total array: 2m × 0.3m (depth)         │
    │                                          │
    │   MUX usage:                             │
    │   • MUX0: Depth 1 (CH0-CH3)              │
    │   • MUX1: Depth 2 (CH4-CH7)              │
    │   • Both MUX → OPA1641 ×2                │
    │   • Perfect match to V5 hardware!         │
    └─────────────────────────────────────────┘
```

**Specifications:**
- 8 measurement points (4 locations × 2 depths)
- 4-electrode per point (true resistivity)
- Investigation depths: 15cm and 45cm
- Spatial resolution: 50cm lateral
- Total electrodes: 32 (8 probes × 4 electrodes)
- Wiring: 8 × 4-core cables to V5 MUX

---

## Bill of Materials (Electrode Array)

| Item | Qty | Unit Cost | Total | Supplier |
|------|-----|-----------|-------|----------|
| 316L SS rod, 8mm × 300mm | 32 | £2 | £64 | Metal supplier |
| PVC tube, 25mm OD, 2m | 8 | £3 | £24 | Plumbing |
| M12 connector, 4-pin, IP67 | 8 | £4 | £32 | RS/Farnell |
| 4-core shielded cable, 5m | 8 | £5 | £40 | Cable supplier |
| Epoxy potting compound | 1 kg | £15 | £15 | RS |
| 3D printed probe tip | 8 | £2 | £16 | Local/Shapeways |
| Mounting stakes | 8 | £1 | £8 | Garden centre |
| **Total** | | | **£219** | |

Plus V5 board (£34 components + £250 Red Pitaya) = **~£503 total**

---

## Next Steps

1. **Build single probe** — 4-electrode, test in known soil
2. **Validate 4-electrode vs 2-electrode** — measure contact resistance effect
3. **Design probe body** — CAD model, 3D print or machine
4. **Test array** — 2 probes, 2 depths, compare moisture readings
5. **Field trial** — Deploy 8-point array, correlate with gravimetric samples

---

*Document saved to: `projects/agricultural_sensing/soil_impedance/electrode_array_geometry.md`*
