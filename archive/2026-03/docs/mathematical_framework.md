# Mathematical Framework for Viscoelastic Shear Wave Elastography
## Derivation from First Principles

**Project:** Multi-Frequency Shear Wave Elastography  
**Date:** March 7, 2026  
**Purpose:** Week 1 Theoretical Foundation

---

## 1. CONSTITUTIVE RELATION: KELVIN-VOIGT MODEL

### 1.1 Stress-Strain Relationship

For a linear viscoelastic material, the Kelvin-Voigt (KV) model combines:
- **Elastic element** (spring): Stress proportional to strain
- **Viscous element** (dashpot): Stress proportional to strain rate

**In parallel configuration:**

```
σ = σ_elastic + σ_viscous

σ_elastic = G' · ε        (Hooke's law)
σ_viscous = η · ∂ε/∂t     (Newton's law of viscosity)
```

**Combined:**
```
┌─────────────────────────────────────────┐
│                                         │
│   σ(t) = G' · ε(t) + η · ∂ε(t)/∂t      │
│                                         │
└─────────────────────────────────────────┘

Where:
- σ = shear stress (Pa)
- ε = shear strain (dimensionless)
- G' = storage modulus (elastic component) [Pa]
- η = viscosity [Pa·s]
- t = time [s]
```

### 1.2 Complex Modulus Representation

In frequency domain (harmonic excitation ε(t) = ε₀e^(iωt)):

```
ε(t) = ε₀ e^(iωt)
∂ε/∂t = iω ε₀ e^(iωt) = iω ε(t)

Substituting into KV model:
σ(t) = G' ε(t) + η (iω) ε(t)
     = (G' + iωη) ε(t)
     = G*(ω) ε(t)
```

**Complex shear modulus:**
```
┌─────────────────────────────────────────┐
│                                         │
│   G*(ω) = G' + iG''                    │
│                                         │
│   Where:                                │
│   G' = storage modulus (elastic)       │
│   G'' = ωη = loss modulus (viscous)    │
│                                         │
└─────────────────────────────────────────┘
```

**Magnitude and phase:**
```
|G*(ω)| = √(G'² + G''²) = √(G'² + (ωη)²)

tan(δ) = G''/G' = ωη/G'          (loss tangent)
δ = phase angle between stress and strain
```

---

## 2. GOVERNING EQUATION: WAVE PROPAGATION

### 2.1 Equation of Motion

From Newton's second law (conservation of momentum):

```
ρ ∂²u/∂t² = ∇·σ + f

Where:
- ρ = density [kg/m³]
- u = displacement vector [m]
- σ = stress tensor [Pa]
- f = body force [N/m³]
```

For shear waves in 1D (x-direction propagation, y-direction displacement):
```
ρ ∂²u_y/∂t² = ∂σ_xy/∂x
```

### 2.2 Strain-Displacement Relation

For simple shear:
```
ε_xy = ½ (∂u_y/∂x + ∂u_x/∂y)

For pure shear wave (u_x = 0, u_y = u(x,t)):
ε = ∂u/∂x
```

### 2.3 Deriving the Viscoelastic Wave Equation

Substitute constitutive relation into equation of motion:

```
Step 1: Differentiate constitutive relation
σ = G'ε + η ∂ε/∂t

Step 2: Take spatial derivative
∂σ/∂x = G' ∂ε/∂x + η ∂/∂x(∂ε/∂t)
      = G' ∂²u/∂x² + η ∂/∂t(∂²u/∂x²)

Step 3: Substitute into equation of motion
ρ ∂²u/∂t² = G' ∂²u/∂x² + η ∂³u/∂x²∂t
```

**Final 1D Viscoelastic Wave Equation:**
```
┌──────────────────────────────────────────────┐
│                                              │
│   ρ ∂²u/∂t² = G' ∂²u/∂x² + η ∂³u/∂x²∂t    │
│                                              │
│   Or equivalently:                           │
│   ∂²u/∂t² = (G'/ρ) ∂²u/∂x² + (η/ρ) ∂³u/∂x²∂t │
│                                              │
└──────────────────────────────────────────────┘
```

### 2.4 Physical Interpretation

| Term | Physical Meaning |
|------|-----------------|
| `ρ ∂²u/∂t²` | Inertial force (mass × acceleration) |
| `G' ∂²u/∂x²` | Elastic restoring force |
| `η ∂³u/∂x²∂t` | Viscous damping force |

**Elastic case (η = 0):**
```
∂²u/∂t² = c_s² ∂²u/∂x²    where c_s = √(G'/ρ)
```
Standard wave equation with constant wave speed.

**Viscous case (η ≠ 0):**
Wave speed becomes frequency-dependent (dispersion).

---

## 3. DISPERSION RELATION

### 3.1 Harmonic Wave Ansatz

Assume plane wave solution:
```
u(x,t) = u₀ e^(i(kx - ωt))

Where:
- u₀ = amplitude
- k = wavenumber [rad/m]
- ω = angular frequency [rad/s]
```

Derivatives:
```
∂u/∂t = -iω u
∂²u/∂t² = -ω² u

∂u/∂x = ik u
∂²u/∂x² = -k² u
∂³u/∂x²∂t = iωk² u
```

### 3.2 Substituting into Wave Equation

```
-ρω² u = -G'k² u + iωη(-k²) u

Divide by -u:
ρω² = G'k² - iωηk²
ρω² = (G' - iωη) k²
```

### 3.3 Complex Wavenumber

Define complex modulus G* = G' + iωη (note sign convention)
Actually, let's be careful with the sign...

From: ρω² = (G' - iωη)k²

This gives complex k. Instead, let's solve for phase velocity directly.

### 3.4 Phase Velocity Derivation

Define phase velocity: c_p = ω/k_real

For viscoelastic wave, k is complex: k = k' - iα
- k' = real wavenumber (propagation)
- α = attenuation coefficient

Substituting and solving (detailed algebra omitted for brevity):

```
For Kelvin-Voigt model, the phase velocity is:

┌──────────────────────────────────────────────────────┐
│                                                      │
│         ╱     ╱──────────────────────\              │
│   c_s = ╲    ╱   √(G'² + (ωη)²)                    │
│          ╲  ╱   ─────────────────                    │
│           ╲╱          ρ                             │
│                                                      │
│   Or equivalently:                                   │
│                                                      │
│   c_s(ω) = √(|G*(ω)| / ρ)                           │
│                                                      │
│   where |G*| = √(G'² + (ωη)²)                       │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### 3.5 Key Observations

**1. Frequency-Dependent Speed (Dispersion):**
```
As ω increases:
- |G*| increases (because ωη term grows)
- c_s(ω) increases

High frequencies travel faster than low frequencies!
```

**2. Elastic Limit (η → 0):**
```
c_s = √(G'/ρ) = constant

No dispersion — all frequencies travel at same speed.
```

**3. Low-Frequency Limit (ω → 0):**
```
c_s ≈ √(G'/ρ)

At low frequencies, viscosity has little effect.
```

**4. High-Frequency Limit (ω → ∞):**
```
c_s ≈ √(ωη/ρ) ∝ √ω

At high frequencies, viscosity dominates.
```

### 3.6 Numerical Examples

**Example 1: Healthy Liver**
```
G' = 4 kPa = 4000 Pa
η = 2 Pa·s
ρ = 1000 kg/m³

At ω = 2π × 50 Hz = 314 rad/s:
|G*| = √(4000² + (314×2)²) = √(16×10⁶ + 3.9×10⁵) ≈ 4048 Pa
c_s = √(4048/1000) ≈ 2.01 m/s

At ω = 2π × 200 Hz = 1257 rad/s:
|G*| = √(4000² + (1257×2)²) = √(16×10⁶ + 6.3×10⁶) ≈ 4726 Pa
c_s = √(4726/1000) ≈ 2.17 m/s

Dispersion: 2.17/2.01 ≈ 8% increase
```

**Example 2: Inflamed Liver (Higher Viscosity)**
```
G' = 6 kPa = 6000 Pa
η = 10 Pa·s
ρ = 1000 kg/m³

At ω = 2π × 50 Hz:
|G*| = √(6000² + (314×10)²) = √(36×10⁶ + 9.9×10⁶) ≈ 6776 Pa
c_s = √(6776/1000) ≈ 2.60 m/s

At ω = 2π × 200 Hz:
|G*| = √(6000² + (1257×10)²) = √(36×10⁶ + 158×10⁶) ≈ 13924 Pa
c_s = √(13924/1000) ≈ 3.73 m/s

Dispersion: 3.73/2.60 ≈ 43% increase (much stronger!)
```

**Key Insight:** High viscosity → strong dispersion → measurable effect!

---

## 4. INVERSE PROBLEM FORMULATION

### 4.1 Problem Statement

**Given:**
- Measurements: {c_s(ω₁), c_s(ω₂), ..., c_s(ωₙ)} at n frequencies
- Known density: ρ (typically ~1000 kg/m³)

**Find:**
- Storage modulus: G'
- Viscosity: η

### 4.2 Forward Model (Parameter-to-Data)

```
c_model(ω; G', η) = √[√(G'² + (ωη)²) / ρ]

This is our forward model: parameters → predictions
```

### 4.3 Inverse Problem (Data-to-Parameters)

**Objective:** Minimize discrepancy between model and data

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   min_{G', η}  Σᵢ₌₁ⁿ [c_model(ωᵢ; G', η) - c_measured(ωᵢ)]² │
│                                                             │
│   Subject to:                                               │
│     G' > 0                                                  │
│     η ≥ 0                                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.4 Regularized Formulation

Add regularization for stability:

```
min_{G', η}  ||c_model - c_measured||² 
             + λ₁(G' - G'₀)² + λ₂(η - η₀)²

Where:
- G'₀, η₀ = prior values (from literature)
- λ₁, λ₂ = regularization strengths
```

### 4.5 Bayesian Formulation

Treat as probabilistic inference:

```
Likelihood:    p(c_measured | G', η) ∝ exp(-½χ²)
                              where χ² = Σ[(c_m - c_d)/σ]²

Prior:         p(G', η) ∝ exp(-½[(G'-G'₀)²/σ_G'² + (η-η₀)²/σ_η²])

Posterior:     p(G', η | c) ∝ p(c | G', η) × p(G', η)

Goal:          Find posterior distribution over (G', η)
```

### 4.6 Analytical Solution (2 Frequencies)

With exactly 2 frequency measurements, we can solve directly:

```
Given: c₁ = c(ω₁), c₂ = c(ω₂)

From dispersion relation:
c₁² = √(G'² + (ω₁η)²) / ρ

c₂² = √(G'² + (ω₂η)²) / ρ

Let: A = c₁²ρ, B = c₂²ρ

Then:
A² = G'² + (ω₁η)²
B² = G'² + (ω₂η)²

Subtract:
A² - B² = η²(ω₁² - ω₂²)

Solve for η:
η = √[(A² - B²) / (ω₁² - ω₂²)]

Then solve for G':
G' = √[A² - (ω₁η)²]
```

**Limitations:**
- Requires exactly 2 frequencies
- Sensitive to measurement noise
- Can give imaginary results if noise is large
- No uncertainty quantification

**Advantages:**
- Fast (no iteration)
- Closed-form solution
- Good starting point for optimization

---

## 5. SUMMARY: KEY EQUATIONS

### 5.1 Constitutive Relation
```
σ = G'ε + η(∂ε/∂t)           (Kelvin-Voigt)
G* = G' + iωη                (Complex modulus)
```

### 5.2 Wave Equation
```
ρ ∂²u/∂t² = G' ∂²u/∂x² + η ∂³u/∂x²∂t
```

### 5.3 Dispersion Relation
```
c_s(ω) = √[√(G'² + (ωη)²) / ρ]
```

### 5.4 Inverse Problem
```
min ||c_model(ω; G', η) - c_measured(ω)||²
subject to: G' > 0, η ≥ 0
```

---

## 6. DIMENSIONAL ANALYSIS

Verify equation consistency:

| Quantity | Units | Check |
|----------|-------|-------|
| G' | Pa = N/m² = kg/(m·s²) | ✓ |
| η | Pa·s = kg/(m·s) | ✓ |
| ρ | kg/m³ | ✓ |
| ω | rad/s = 1/s | ✓ |
| c_s | m/s | ✓ |
| ωη | (1/s)(kg/(m·s)) = kg/(m·s²) = Pa | ✓ |
| G'/ρ | (kg/(m·s²))/(kg/m³) = m²/s² | ✓ (c²) |
| √(G'/ρ) | m/s | ✓ (c) |

---

## 7. CLINICAL PARAMETER RANGES

| Condition | G' (kPa) | η (Pa·s) | c_s at 50Hz (m/s) |
|-----------|----------|----------|-------------------|
| Healthy liver | 4-6 | 2-3 | 2.0-2.5 |
| Mild fibrosis (F1-F2) | 7-10 | 3-5 | 2.7-3.2 |
| Severe fibrosis (F3-F4) | 12-25 | 4-8 | 3.5-5.0 |
| Inflammation | 5-8 | 8-15 | 2.2-3.0 |
| Cirrhosis | 20-75 | 5-12 | 4.5-8.7 |

**Key Insight:** Inflammation increases η more than G', creating a unique (G', η) signature!

---

## 8. VALIDATION CHECKLIST

Your implementation should reproduce:

- [ ] Elastic limit: η=0 → c_s = √(G'/ρ) (constant vs frequency)
- [ ] Low-frequency limit: c_s → √(G'/ρ) as ω → 0
- [ ] High-frequency limit: c_s ∝ √ω as ω → ∞
- [ ] Higher η → stronger dispersion (steeper c_s vs ω curve)
- [ ] Inverse problem recovers (G', η) from dispersion curve

---

## 9. CODE IMPLEMENTATION SKETCH

```python
import numpy as np

def phase_velocity(omega, G_prime, eta, rho=1000):
    """
    Calculate shear wave phase velocity for Kelvin-Voigt model.
    
    Parameters:
    -----------
    omega : float or array
        Angular frequency(ies) [rad/s]
    G_prime : float
        Storage modulus [Pa]
    eta : float
        Viscosity [Pa·s]
    rho : float
        Density [kg/m³]
    
    Returns:
    --------
    c_s : float or array
        Phase velocity [m/s]
    """
    G_complex_magnitude = np.sqrt(G_prime**2 + (omega * eta)**2)
    c_s = np.sqrt(G_complex_magnitude / rho)
    return c_s

def inverse_direct(c1, c2, omega1, omega2, rho=1000):
    """
    Direct analytical inversion using 2 frequency measurements.
    
    Returns estimated (G_prime, eta).
    """
    A = c1**2 * rho
    B = c2**2 * rho
    
    eta_squared = (A**2 - B**2) / (omega1**2 - omega2**2)
    eta = np.sqrt(max(0, eta_squared))  # Ensure non-negative
    
    G_prime_squared = A**2 - (omega1 * eta)**2
    G_prime = np.sqrt(max(0, G_prime_squared))
    
    return G_prime, eta
```

---

*Mathematical framework derived: March 7, 2026*  
*Ready for Week 1 implementation*
