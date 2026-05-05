# Learning Challenge — 2026-04-08 (Wednesday)
## DSP Engineering: k-ω Transform for Dispersion Extraction

### Learning Objectives

By the end of this challenge, you will deeply understand:
- The mathematical foundation of the k-ω (wavenumber-frequency) transform
- How dispersion curves encode material viscoelastic properties
- Practical implementation trade-offs in discrete signal processing
- The connection between spatial and temporal frequency domains

**Focus:** Deep understanding, not just working code. Question every step.

---

### Part 1: Theoretical Foundation (45 min)

**The k-ω transform** maps a wavefield u(x,t) from space-time (x,t) to wavenumber-frequency (k,ω):

```
U(k,ω) = ∬ u(x,t) · e^(-i(kx - ωt)) dx dt
```

This is essentially a 2D Fourier transform with a specific sign convention matching wave physics.

**Questions to explore:**

1. **Physical meaning**: What does a point (k₀,ω₀) in the k-ω domain represent physically? Why do dispersive waves form curves rather than points?

2. **Resolution trade-offs**: 
   - Spatial resolution Δk ≈ 2π/L (L = spatial aperture)
   - Temporal resolution Δω ≈ 2π/T (T = temporal window)
   - How do these constrain what dispersion curves you can resolve?

3. **Aliasing in k-ω space**:
   - Spatial aliasing: k_max = π/Δx (Nyquist in space)
   - What happens if your receiver spacing is too large?
   - How does this manifest in elastography measurements?

**Deliverable:** Brief handwritten/typed notes answering these three questions with diagrams. Reference: Trefethen's "Finite Difference and Spectral Methods" or Fink's work on time-reversal.

---

### Part 2: Implementation — From First Principles (90 min)

**Do not use a pre-built k-ω library.** Build it yourself.

**Given:**
- Simulated wavefield data: 32 receivers, spaced Δx = 0.5 mm apart
- Temporal sampling: f_s = 100 kHz, duration T = 10 ms
- Shear wave in viscoelastic tissue: c_s(ω) = c₀(1 + iωτ)^β (dispersive)

**Step 1: Generate synthetic data (provided below)**

```python
import numpy as np
import matplotlib.pyplot as plt

# Parameters
nx, nt = 32, 1000
dx, dt = 0.5e-3, 1e-5  # 0.5mm spacing, 10μs sampling
x = np.arange(nx) * dx
t = np.arange(nt) * dt

# Dispersive wave: c(ω) = c0 * (1 + small dispersion)
c0 = 2.0  # m/s, base shear speed
alpha = 0.1  # dispersion strength

# Create wavefield with frequency-dependent velocity
u = np.zeros((nx, nt))
for freq_idx in range(5, 50):  # 5-50 kHz components
    f = freq_idx * 1e3
    omega = 2 * np.pi * f
    c = c0 * (1 + alpha * np.log(f/10e3))  # log-frequency dispersion
    k = omega / c
    
    # Wave from left, attenuating
    for xi in range(nx):
        phase = k * x[xi] - omega * t
        u[xi, :] += np.exp(-x[xi]/0.01) * np.sin(phase) * np.exp(-((t-0.003)/0.002)**2)

u += 0.05 * np.random.randn(nx, nt)  # noise
```

**Step 2: Implement 2D DFT manually**

```python
def dft2_manual(u, dx, dt):
    """
    Compute 2D DFT from first principles (O(N⁴) — slow but instructive).
    
    Returns:
        U: 2D spectrum
        k: wavenumber axis (rad/m)
        omega: angular frequency axis (rad/s)
    """
    nx, nt = u.shape
    
    # Frequency axes
    k = 2 * np.pi * np.fft.fftfreq(nx, dx)  # Spatial frequencies
    omega = 2 * np.pi * np.fft.fftfreq(nt, dt)  # Temporal frequencies
    
    U = np.zeros((nx, nt), dtype=complex)
    
    # Double sum (pedagogical — replace with FFT in practice)
    for ki in range(nx):
        for wi in range(nt):
            for xi in range(nx):
                for ti in range(nt):
                    U[ki, wi] += u[xi, ti] * np.exp(-1j * (k[ki]*x[xi] - omega[wi]*t[ti]))
    
    return U, k, omega
```

**Step 3: Switch to FFT-based version for speed**

Understand why:
```python
U = np.fft.fft2(u) * dx * dt
k = 2 * np.pi * np.fft.fftfreq(nx, dx)
omega = 2 * np.pi * np.fft.fftfreq(nt, dt)
```

**Step 4: Extract the dispersion curve**

For each ω, find k that maximizes |U(k,ω)|:
```python
def extract_dispersion(U, k, omega, omega_range=(2*np.pi*5e3, 2*np.pi*50e3)):
    """
    Extract c(ω) = ω/k(ω) from k-ω spectrum.
    
    Handle:
    - Mode selection (pick fundamental mode)
    - Phase vs group velocity (which are you measuring?)
    - Uncertainty quantification
    """
    # Your implementation here
    pass
```

**Deliverable:** 
- `komega_transform.py` with your implementation
- Plot: (a) wavefield u(x,t), (b) |U(k,ω)| colormap, (c) extracted c(ω) vs theory
- Brief analysis: Why does the dispersion curve deviate from theory at high frequencies?

---

### Part 3: Real-World Complications (45 min)

**Complication 1: Limited aperture**

Your array has only 8 elements (from Week 4). Simulate:
```python
u_8ch = u[::4, :]  # Downsample to 8 channels
```

How does k-resolution degrade? What does this do to dispersion curve uncertainty?

**Complication 2: Multiple modes**

Add a higher-order mode:
```python
# Add antisymmetric mode with different dispersion
k2 = 1.5 * k  # Different wavenumber
for xi in range(nx):
    u[xi, :] += 0.5 * np.sin(k2*x[xi] - omega*t) * mode_shape[xi]
```

How do you separate modes in k-ω space? (Hint: Look at slope signatures)

**Complication 3: Attenuation**

Viscoelastic materials have complex k:
```python
k_complex = omega/c + 1j*alpha  # alpha = attenuation (Np/m)
```

How does this affect the k-ω spectrum? Can you extract both c(ω) and α(ω)?

**Deliverable:** 
- Analysis of each complication with plots
- Discussion: Which is the dominant limitation for your 8-element array?

---

### Part 4: Extension — Bayesian Uncertainty (Optional, 30 min)

The extracted dispersion curve has uncertainty from:
- Noise
- Limited k-resolution
- Mode overlap

**Task:** Quantify uncertainty using the Bayesian approach from Week 3.

Model: k_obs(ω) ~ N(k_true(ω), σ_k²)

Prior: k_true follows a physical model (e.g., power-law dispersion)

**Deliverable:** Posterior distribution p(k|data) for one frequency, showing credible intervals.

---

### Deep Questions to Reflect On

1. **Why k-ω and not just ω?** What information does spatial sampling add that temporal sampling alone cannot provide?

2. **Causality and dispersion:** The Kramers-Kronig relations connect real and imaginary parts of k(ω). How does this constrain valid dispersion models?

3. **Sampling in two domains:** You have finite spatial and temporal samples. What are the fundamental resolution limits? How does this relate to the uncertainty principle?

4. **From data to G':** Your ultimate goal is estimating shear modulus G'(ω). Trace the full chain: u(x,t) → U(k,ω) → k(ω) → c(ω) → G'(ω). Where does error accumulate?

---

### Deliverables Summary

1. **Theory notes** (Part 1): Physical meaning, resolution, aliasing
2. **`komega_transform.py`** (Part 2): Working implementation with plots
3. **Complications analysis** (Part 3): Limited aperture, modes, attenuation
4. **Reflection** (Part 4): Answers to at least 2 deep questions

---

### Resources

- **Required:** Trefethen, "Finite Difference and Spectral Methods for ODE/PDE" (free online)
- **Recommended:** Sandrin et al., "Shear Elasticity Probe for Soft Tissues" (2003)
- **Advanced:** Fink et al., "Time-Reversal Acoustics" (Rev. Mod. Phys. 2001)

---

**Difficulty:** Intermediate-Advanced (requires comfort with Fourier analysis)  
**Est. Time:** 3 hours (2.5h core + 30m extension)  
**Prerequisites:** Week 3 inverse problem, familiarity with FFT  
**Topic:** Digital Signal Processing / Wave Physics

## Status: 🆕 NOT STARTED

*Generated: 2026-04-08 08:00 UTC*  
*Schedule: Wednesday = DSP Engineering*
