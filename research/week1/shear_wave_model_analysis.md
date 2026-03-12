# 1D Shear Wave FDTD Model Analysis

## Overview

**Location:** `~/.openclaw/workspace/research/week1/shear_wave_1d_simulator.py`
**Physics:** 1D viscoelastic shear wave propagation using FDTD (Finite-Difference Time-Domain)
**Application:** Ultrasound elastography, tissue characterization
**Model Type:** Kelvin-Voigt viscoelastic medium

---

## Physics Model

### Governing Equation

```
∂²u/∂t² = (G'/ρ) ∂²u/∂x² + (η/ρ) ∂³u/∂x²∂t
```

Where:
| Symbol | Meaning | Unit | Typical Value |
|--------|---------|------|---------------|
| u(x,t) | displacement | m | ~μm scale |
| G' | storage modulus (elastic) | Pa | 5 kPa (liver) |
| η | viscosity | Pa·s | 5-10 Pa·s |
| ρ | density | kg/m³ | 1000 (soft tissue) |
| c_s | shear wave speed | m/s | 1-10 m/s |

### Kelvin-Voigt Constitutive Relation

```
Stress = G'·strain + η·strain_rate
```

- **Elastic term (G')**: Energy storage (springs)
- **Viscous term (η)**: Energy dissipation (dashpots)

---

## FDTD Discretization

### Spatial Grid
```python
nx = 1000          # Grid points
dx = 0.001         # Spatial step (1 mm)
x = [0, dx, 2*dx, ..., (nx-1)*dx]
```

### Temporal Grid
```python
dt = 1e-6          # Time step (1 μs)
n_steps = 50000    # Total steps
t = [0, dt, 2*dt, ..., (n_steps-1)*dt]
```

### Update Equation (Leapfrog)
```
u^{n+1} = 2u^n - u^{n-1} + (dt²/ρ)[G'·∇²u^n + (η/dt)(∇²u^n - ∇²u^{n-1})]
```

Where Laplacian in 1D:
```
∇²u = (u[i+1] - 2u[i] + u[i-1]) / dx²
```

---

## Stability (CFL Condition)

```
CFL = c_s · dt / dx < 1

where c_s = √(G'/ρ)
```

For typical liver tissue:
- G' = 5000 Pa
- ρ = 1000 kg/m³
- c_s = √(5000/1000) = **2.24 m/s**

With dx = 1 mm, dt = 1 μs:
- CFL = 2.24 × 0.001 / 0.001 = **0.224** ✓ Stable

---

## Source Types

### 1. Ricker Wavelet (Mexican Hat)
```python
σ = 1/(π·f0)
source = (1 - 2(τ/σ)²) · exp(-(τ/σ)²)
```
- Center frequency: f0
- Good for single-frequency analysis
- Compact time support

### 2. Tone Burst
```python
envelope = exp(-(t - 3σ)²/(2(σ/3)²))
source = envelope · sin(2π·f0·t)
```
- Gaussian-windowed sinusoid
- ~3 cycles
- Clinical ultrasound standard

---

## Boundary Conditions

### Mur 1st Order Absorbing Boundary
```python
# Left boundary
u[0] = u_prev[1] + (c·dt - dx)/(c·dt + dx) · (u[1] - u_prev[0])

# Right boundary
u[-1] = u_prev[-2] + (c·dt - dx)/(c·dt + dx) · (u[-2] - u_prev[-1])
```

Reduces reflections at domain edges (~95% absorption).

---

## Key Simulation Functions

| Function | Purpose |
|----------|---------|
| `simulate_single_frequency()` | Basic wave propagation at 100 Hz |
| `compare_elastic_vs_viscoelastic()` | Show η effect on attenuation |
| `dispersion_analysis_demo()` | Frequency-dependent wave speed |

---

## Expected Results

### 1. Single Frequency (100 Hz, liver tissue)
- **Wavelength:** λ = c_s/f = 2.24/100 = **2.24 cm**
- **Wave speed:** 2.24 m/s
- **Attenuation:** Low (η = 5 Pa·s)
- **Visualization:** 6 snapshots of wave propagation

### 2. Elastic vs Viscoelastic
| Property | Elastic (η=0) | Viscoelastic (η=10) |
|----------|--------------|---------------------|
| Amplitude | Constant | Decays with distance |
| Wave speed | c_s = √(G'/ρ) | Slightly frequency-dependent |
| Energy | Conserved | Dissipated as heat |

### 3. Dispersion Effect
Higher frequencies (>200 Hz) attenuate faster than lower frequencies due to viscous dissipation.

---

## OpenClaw Integration

This model can be integrated into OpenClaw's research workspace for:

1. **Parameter sweeps**: Systematic variation of (G', η)
2. **Inverse problems**: Recover (G', η) from simulated "measurements"
3. **Multi-frequency analysis**: Full dispersion curve extraction
4. **Validation**: Compare against analytical solutions

---

## Next Steps

1. ✅ **Week 1:** Literature review, theory understanding
2. ✅ **Week 2:** 1D FDTD implementation (current)
3. 🔄 **Week 3:** 2D axisymmetric extension
4. ⏳ **Week 4:** Inverse problem solver
5. ⏳ **Week 5:** Validation against phantoms

---

## Code Architecture

```
ShearWave1D
├── __init__()           # Initialize grid, parameters
├── add_source()         # Inject wavelet
├── step()               # FDTD time update
├── _apply_abc()         # Absorbing boundaries
├── record()             # Save time history
└── extract_dispersion() # Post-processing
```

## Visualization Pipeline

```
Simulation → NumPy arrays → Matplotlib → PNG → OpenClaw Canvas
     ↑                                              ↓
Parameters ← Analysis ← Dispersion extraction ←──┘
```
