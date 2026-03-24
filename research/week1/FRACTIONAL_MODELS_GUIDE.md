# Fractional Viscoelastic Models: Beyond Kelvin-Voigt

## The Problem with Integer-Order Models

Your current Kelvin-Voigt model:
```
σ = G'·ε + η·(dε/dt)
```

**Works well for:** Single-frequency or narrow-band experiments  
**Fails for:** Broad frequency ranges (10-500 Hz) typical in clinical elastography

**Why it fails:**
- Real tissues show **power-law** frequency dependence: G*(ω) ∝ ω^α
- KV model shows **linear** frequency dependence: G*(ω) = G' + iωη
- To fit broad bandwidth, you'd need multiple KV elements (complex)

## The KVFD Solution

**Kelvin-Voigt Fractional Derivative (KVFD)** model:

```
σ(t) = E₀·ε(t) + E₀·τ^α · D^α[ε(t)]
```

Where:
| Symbol | Meaning | Typical Value |
|--------|---------|---------------|
| E₀ | Quasi-static modulus | 2-10 kPa |
| τ | Characteristic time | 0.1-10 ms |
| α | Fractional order | 0.1-0.5 (tissue) |
| D^α | Fractional derivative | Caputo or Riemann-Liouville |

### Why 0 < α < 1?

- **α = 0**: Purely elastic (Hooke's law)
- **α = 1**: Purely viscous (Newtonian fluid)
- **0 < α < 1**: Viscoelastic with power-law memory

Biological tissues typically have **α ≈ 0.1-0.3**

## Complex Modulus (Frequency Domain)

The KVFD complex modulus:

```
G*(ω) = E₀ · (1 + (iωτ)^α)
```

Or in terms of storage and loss moduli:

```
G'(ω) = E₀ · [1 + (ωτ)^α · cos(απ/2)]
G''(ω) = E₀ · (ωτ)^α · sin(απ/2)
```

### Power-Law Behavior

**Attenuation coefficient:**
```
α_att(ω) ∝ ω^α
```

This matches experimental observations in tissue:
- Not linear (would be α = 1)
- Not quadratic (would be α = 2)
- Power-law with **α ≈ 0.5-1.5** depending on tissue

## Comparison: KV vs KVFD

| Feature | Kelvin-Voigt | KVFD |
|---------|--------------|------|
| Parameters | 2 (G', η) | 3 (E₀, τ, α) |
| Frequency dependence | Linear | Power-law |
| Broad band fit | Poor | Excellent |
| Physical basis | Simplistic | Fractal/microstructure |
| Memory | Local (instant) | Global (power-law) |

## Visual Comparison

### Storage Modulus vs Frequency

```
KV:      G'(ω) = constant (flat)
KVFD:    G'(ω) = E₀·[1 + (ωτ)^α·cos(απ/2)]  (increasing)

Real tissue: Increasing with frequency (KVFD matches)
```

### Loss Modulus vs Frequency

```
KV:      G''(ω) ∝ ω  (linear)
KVFD:    G''(ω) ∝ ω^α  (power-law)

Real tissue: Power-law (KVFD matches)
```

### Phase Velocity Dispersion

```
KV:      c(ω) increases then plateaus
KVFD:    c(ω) increases as power-law

Real tissue: Power-law increase (KVFD matches)
```

## Mathematical Implementation

### Fractional Derivative Definition

**Caputo fractional derivative** (most common for physical problems):

```
D^α[f(t)] = 1/Γ(1-α) · ∫₀ᵗ (t-τ)^(-α) · f'(τ) dτ
```

Where Γ is the gamma function.

### Grünwald-Letnikov Approximation (for FDTD)

For numerical implementation:

```
D^α[u^n] ≈ (1/Δt^α) · Σₖ₌₀ⁿ wₖ · u^(n-k)
```

Where weights:
```
w₀ = 1
wₖ = (k-1-α)/k · wₖ₋₁   for k ≥ 1
```

### KVFD-FDTD Update Equation

The 1D wave equation with KVFD:

```
ρ·∂²u/∂t² = E₀·∂²u/∂x² + E₀·τ^α·D^α[∂²u/∂x²]
```

Discretized:
```
u^(n+1) = 2u^n - u^(n-1) + (Δt²/ρ)·[E₀·∇²u^n + E₀·τ^α·D^α(∇²u^n)]
```

**Key difference:** The fractional derivative term requires **memory** of all previous time steps (computationally expensive!)

## Practical Implementation Strategy

### Option 1: Short Memory Approximation

Only keep last N time steps:

```python
def fractional_derivative_short(u_history, alpha, dt, N=100):
    """
    Approximate D^alpha using only last N steps.
    """
    weights = compute_grunwald_weights(alpha, N)
    result = 0
    for k in range(min(N, len(u_history))):
        result += weights[k] * u_history[-(k+1)]
    return result / (dt ** alpha)
```

**Trade-off:** Accuracy vs computation time. N=100-200 usually sufficient.

### Option 2: Frequency Domain (Fourier Spectral)

Transform to frequency domain, apply (iω)^α, transform back:

```python
def fractional_derivative_fft(u, alpha, dt):
    """
    Compute D^alpha using FFT (efficient for periodic domains).
    """
    u_fft = np.fft.fft(u)
    omega = 2 * np.pi * np.fft.fftfreq(len(u), dt)
    d_alpha_fft = (1j * omega) ** alpha * u_fft
    return np.fft.ifft(d_alpha_fft).real
```

**Trade-off:** Requires periodic BCs or large padding. Efficient for homogeneous media.

### Option 3: Prony Series Approximation

Approximate fractional derivative with multiple exponentials:

```
D^α[f(t)] ≈ Σᵢ aᵢ · exp(-bᵢ·t) * f(t)
```

**Trade-off:** More parameters, but local in time (no memory). Used in commercial FE codes.

## When Do You Need KVFD?

### Use KV (your current model) if:
- Single frequency analysis
- Narrow bandwidth (< 2× frequency span)
- Quick validation/testing
- Educational purposes

### Use KVFD if:
- Broad bandwidth (10-500 Hz)
- Characterizing tissue over wide frequency range
- Fitting power-law attenuation
- Clinical applications requiring accuracy

## Parameter Estimation for KVFD

### From Dispersion Data

Given measured c(ω) and α_att(ω):

```python
def kvfd_cost_function(params, omega, c_measured, alpha_measured):
    E0, tau, alpha = params
    
    # KVFD complex modulus
    G_star = E0 * (1 + (1j * omega * tau) ** alpha)
    
    # Phase velocity
    c_calc = np.sqrt(2 * np.abs(G_star) / (rho * (np.real(G_star)/np.abs(G_star) + 1)))
    
    # Attenuation
    alpha_calc = omega * np.imag(G_star) / (2 * rho * c_calc**3)
    
    # Misfit
    residual = np.sum((c_calc - c_measured)**2) + 
               np.sum((alpha_calc - alpha_measured)**2)
    
    return residual
```

### Constraints

```python
bounds = [
    (1000, 50000),    # E0: 1-50 kPa
    (1e-4, 1e-1),     # tau: 0.1-100 ms
    (0.05, 0.95)      # alpha: 0.05-0.95
]
```

## Validation: KVFD vs KV

### Synthetic Test

```python
# True KVFD parameters
E0_true, tau_true, alpha_true = 5000, 0.01, 0.2

# Generate synthetic data
omega = 2 * np.pi * np.linspace(10, 500, 50)
G_star = E0_true * (1 + (1j * omega * tau_true) ** alpha_true)
c_true = compute_phase_velocity(G_star)

# Fit with KV (2 params)
G_kv, eta_kv = fit_kv_model(omega, c_true)

# Fit with KVFD (3 params)
E0_kvfd, tau_kvfd, alpha_kvfd = fit_kvfd_model(omega, c_true)

# Compare
print(f"KV misfit: {compute_misfit_kv():.2e}")
print(f"KVFD misfit: {compute_misfit_kvfd():.2e}")
```

**Expected result:** KVFD misfit 10-100× smaller for broad bandwidth data.

## Example: Liver Tissue Parameters

From literature (Parker et al.):

| Parameter | Value | Interpretation |
|-----------|-------|----------------|
| E₀ | 2.5 kPa | Quasi-static modulus |
| τ | 2.5 ms | Characteristic relaxation time |
| α | 0.38 | Power-law exponent |

**Dispersion:**
- At 50 Hz: c ≈ 1.6 m/s
- At 200 Hz: c ≈ 2.1 m/s
- At 500 Hz: c ≈ 2.8 m/s

KV model cannot capture this frequency dependence!

## Summary

**Key Insights:**

1. **KVFD captures power-law rheology** observed in real tissues
2. **Only 3 parameters** vs many for Prony series
3. **Global memory** via fractional derivative (microstructural basis)
4. **Computationally expensive** but manageable with short-memory approximation

**Recommendation for your project:**

**Week 2-3:** Stick with KV for validation and learning  
**Week 4:** Implement KVFD if you have broad-bandwidth data  
**Validation:** Always compare KV vs KVFD fit quality on your data

**Reference:**
- Parker, K. J., et al. (2019). "Universal breast tissue ultrasound properties"
- Bonfanti, et al. (2020). "Power-law rheology in shear wave elastography"
- Treeby, B. E., & Cox, B. T. (2013). "Fractional wave equations for power law absorption"
