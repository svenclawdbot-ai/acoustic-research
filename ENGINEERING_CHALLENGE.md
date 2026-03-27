# Engineering Challenge — 2026-03-27 (Friday)

## Array Beamforming for Shear Wave Elastography — Delay-and-Sum Implementation

### Problem Context

Your ESP32-S3 array controller firmware is ready for hardware integration. Today, implement the core beamforming algorithm that will drive it: **delay-and-sum beamforming** for focused shear wave generation in viscoelastic tissue.

This connects your Week 3 inverse problem work (recovering material properties) with the hardware control layer — the beamformer determines how energy is deposited to create measurable shear waves.

---

### Challenge

Implement and validate a delay-and-sum beamformer for an 8-element linear array (2.5 MHz elements, 0.6 mm pitch) that focuses shear waves at a target depth in viscoelastic tissue.

---

### Technical Requirements

#### Part 1: Time-of-Flight Calculation (40 min)

For an 8-element linear array with element positions xₙ = n·pitch (n = 0..7):

**Given:**
- Array: 8 elements, pitch = 0.6 mm
- Target focus: (x_f, z_f) = (2.4 mm, 10 mm) — centered, 10mm deep
- Shear wave speed: c_s = 2.0 m/s (tissue-like)

**Calculate:**
1. Distance from each element n to focus: dₙ = √[(x_f - xₙ)² + z_f²]
2. Time-of-flight: τₙ = dₙ / c_s
3. Relative delays: Δτₙ = τₙ - min(τₙ) [reference to earliest arrival]

**Deliverable:** Table of distances, TOF, and relative delays for all 8 elements.

---

#### Part 2: Apodization Weights (30 min)

Apodization reduces side lobes and improves focus quality.

**Implement three window functions:**

1. **Rectangular (no apodization):** wₙ = 1
2. **Hanning:** wₙ = 0.5 · [1 - cos(2πn/(N-1))]
3. **Hamming:** wₙ = 0.54 - 0.46 · cos(2πn/(N-1))

**Deliverable:** Plot all three apodization functions across the 8-element array.

---

#### Part 3: Delay-and-Sum Beamformer (60 min)

**Implement the beamformed excitation signal:**

```
sₙ(t) = wₙ · s₀(t - Δτₙ)
```

Where:
- s₀(t): Base excitation (e.g., 2.5 MHz tone burst, 3 cycles)
- wₙ: Apodization weight for element n
- Δτₙ: Relative delay for element n

**Tasks:**
1. Generate a 2.5 MHz, 3-cycle tone burst sampled at 20 MSa/s
2. Apply delays and weights to create 8 element signals
3. Simulate the field at the focal point by summing contributions
4. Calculate the **array gain**: coherent sum vs. single element

**Deliverable:** 
- Python script `beamformer_simulation.py`
- Plot showing all 8 delayed signals and their sum
- Array gain calculation (should be ~N² for coherent sum = ~18 dB for 8 elements)

---

#### Part 4: Pressure Field Simulation (50 min)

**Simulate the 2D pressure field** in the (x, z) plane:

1. Define a grid: x ∈ [0, 4.8] mm, z ∈ [2, 20] mm (100×100 points)
2. For each grid point (x, z), calculate the field as sum of contributions from all elements:
   ```
   p(x,z,t) = Σₙ wₙ · A(dₙ)/dₙ · s₀(t - dₙ/c)
   ```
   Where A(dₙ) ≈ √dₙ accounts for cylindrical spreading.

3. Calculate **peak pressure envelope**: P(x,z) = max_t |p(x,z,t)|

**Deliverable:**
- 2D colormap of peak pressure field
- Focal spot size measurement (-6 dB width in x and z)
- Compare with/without apodization

---

### Extension: Beam Steering (Optional — 30 min)

Modify your beamformer to steer the focus off-axis:

**Task:** Calculate delays for focal points at:
- (1.2 mm, 10 mm) — steered left
- (3.6 mm, 10 mm) — steered right

**Deliverable:** Three pressure field plots showing steering capability.

---

### Key Equations

**Element positions:**
```
xₙ = (n - (N-1)/2) · pitch,  n = 0, 1, ..., N-1
```

**Distance to focus:**
```
dₙ = √[(x_f - xₙ)² + z_f²]
```

**Time delay:**
```
τₙ = dₙ / c_s
```

**Beamformed signal at focus:**
```
p_focus(t) = Σₙ wₙ · s₀(t - τₙ)
```

**Array gain:**
```
G_array = 20·log₁₀(Σₙ wₙ / max(wₙ))  [dB]
```

---

### Hints

- Use `scipy.signal.hilbert` for envelope detection
- For speed, vectorize the field calculation with NumPy broadcasting
- The focal gain won't be exactly N² due to apodization — that's expected
- Consider using `matplotlib.animation` to visualize wave propagation

---

### Validation Checklist

- [ ] Delays are symmetric about array center for on-axis focus
- [ ] Sum of Hanning weights ≈ 0.5 × sum of rectangular
- [ ] Focal spot -6 dB width ≈ 1–2 wavelengths laterally
- [ ] Array gain with Hanning ≈ 15–16 dB (vs 18 dB rectangular)

---

### Connections to Current Work

| This Challenge | Your Existing Work |
|----------------|-------------------|
| Delay profiles | Will drive `array_control.c` timing |
| Apodization weights | Used in `set_apodization()` command |
| Focused field | Creates shear waves for Week 3 inverse problem |
| Array gain | Determines SNR for dispersion measurement |

---

### Deliverables Summary

1. **TOF calculation table** (8 elements)
2. **Apodization plot** (3 windows)
3. **`beamformer_simulation.py`** with delayed signals plot
4. **Pressure field colormap** with focal spot analysis
5. **Brief interpretation**: How does apodization trade main lobe width for side lobe suppression?

---

**Difficulty:** Intermediate (signal processing + spatial reasoning)  
**Est. Time:** 3 hours (2.5h core + 30m extension)  
**Topic:** Signal Processing / Acoustics / Beamforming

## Status: 🆕 NOT STARTED

*Generated: 2026-03-27 07:05 UTC*
