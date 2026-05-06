# Deep Dive: Kelvin-Voigt Dispersion Relation Derivation
## Date: 2026-03-17 (Tuesday Physics/Mathematics Challenge)

---

## Step 1: Constitutive Relation (Kelvin-Voigt Model)

For 1D shear deformation:

```
σ = G'·ε + η·ε̇
```

Where:
- `σ` = shear stress  
- `ε = ∂u/∂x` = shear strain  
- `G'` = storage modulus (elastic)  
- `η` = viscosity  
- `u(x,t)` = displacement

Substituting strain definition:

```
σ = G'·(∂u/∂x) + η·(∂²u/∂x∂t)
```

---

## Step 2: Equation of Motion

Newton's second law for continuum:

```
ρ·(∂²u/∂t²) = ∂σ/∂x
```

Substitute stress from Step 1:

```
ρ·(∂²u/∂t²) = G'·(∂²u/∂x²) + η·(∂³u/∂x²∂t)
```

**Term meanings:**
- `ρ·(∂²u/∂t²)` = inertial force
- `G'·(∂²u/∂x²)` = elastic restoring force
- `η·(∂³u/∂x²∂t)` = viscous damping force

---

## Step 3: Plane Wave Ansatz

Assume harmonic solution:

```
u(x,t) = u₀·exp[i(kx - ωt)]
```

Where:
- `k` = complex wavenumber
- `ω` = angular frequency (real)
- `u₀` = amplitude

**Complex wavenumber decomposition:**

```
k = k' - iα
```

- `k'` = real wavenumber (propagation)
- `α` = attenuation coefficient

---

## Step 4: Derive the Dispersion Relation

Substitute ansatz into PDE. For each derivative:

```
∂u/∂t     → -iω·u
∂²u/∂t²   → -ω²·u
∂u/∂x     → ik·u
∂²u/∂x²   → -k²·u
∂³u/∂x²∂t → iωk²·u
```

Substituting:

```
ρ·(-ω²) = G'·(-k²) + η·(iωk²)
```

Simplify:

```
-ρω² = -k²(G' - iωη)

ρω² = k²(G' + iωη)
```

**Fundamental dispersion relation:**

```
k² = ρω² / (G' + iωη)
```

---

## Step 5: Rationalize the Denominator

Define **complex modulus**:

```
G* = G' + iG''

where G'' = ωη  (loss modulus)
```

Multiply numerator and denominator by complex conjugate:

```
k² = ρω²(G' - iωη) / [(G')² + (ωη)²]
```

Define magnitude of complex modulus:

```
|G*| = √[(G')² + (ωη)²]
```

So:

```
k² = ρω²(G' - iωη) / |G*|²
```

---

## Step 6: Phase Velocity Derivation

From `k² = ρω²/G*`:

```
k = ω√(ρ/G*) = ω√(ρ/|G*|)·exp(-iδ/2)
```

Where **loss angle** `δ` is defined by:

```
tan(δ) = G''/G' = ωη/G' = ωτ

τ = η/G'  (relaxation time)
```

Separate real and imaginary parts using Euler's formula:

```
k = ω√(ρ/|G*|)·[cos(δ/2) - i·sin(δ/2)]
```

Therefore:

```
k' = ω√(ρ/|G*|)·cos(δ/2)   ← propagation
α  = ω√(ρ/|G*|)·sin(δ/2)   ← attenuation
```

**Phase velocity** `cₚ = ω/k'`:

```
cₚ = √(|G*|/ρ) / cos(δ/2)

   = √[|G*| / (ρ·cos²(δ/2))]
```

Using identity `2cos²(δ/2) = 1 + cos(δ)`:

```
cₚ = √[2|G*| / (ρ(1 + cos(δ)))]
```

Since `cos(δ) = G'/|G*|`:

```
cₚ = √[2|G*|² / (ρ(|G*| + G'))]
```

---

## Step 7: Final Compact Forms

Define dimensionless frequency `ωτ` where `τ = η/G'`:

```
|G*| = G'√[1 + (ωτ)²]

cos(δ) = 1/√[1 + (ωτ)²]

cos(δ/2) = √[(1 + cos(δ))/2]
```

**Phase velocity (final form):**

```
cₚ = c₀·√2·[1 + (ωτ)²]^(1/4)·cos[arctan(ωτ)/2]
```

Where `c₀ = √(G'/ρ)` = elastic wave speed.

**Attenuation coefficient:**

```
α = (ω/cₚ)·tan(δ/2)
```

Or explicitly:

```
α = (ω/c₀)·sin(δ/2) / {√2·[1 + (ωτ)²]^(1/4)}
```

---

## Step 8: Limiting Cases

### Low Frequency (ωτ ≪ 1):

Taylor expansion:

```
[1 + (ωτ)²]^(1/4) ≈ 1 + (ωτ)²/4

cos[arctan(ωτ)/2] ≈ 1 - (ωτ)²/8
```

Result:

```
cₚ ≈ c₀·[1 + (ωτ)²/8]      ← weak dispersion

α ≈ (ω²τ)/(2c₀)            ← α ∝ ω²
```

### High Frequency (ωτ ≫ 1):

```
[1 + (ωτ)²]^(1/4) ≈ (ωτ)^(1/2)

arctan(ωτ) ≈ π/2

cos(π/4) = 1/√2
```

Result:

```
cₚ ≈ c₀·√(ωτ)              ← cₚ ∝ √ω

α ≈ √(ω/2c₀τ)              ← α ∝ √ω
```

---

## Step 9: Numerical Evaluation (Your Parameters)

Given:
```
ρ   = 1000 kg/m³
G'  = 5000 Pa
η   = 5 Pa·s
τ   = η/G' = 0.001 s = 1 ms
f   = 100 Hz
ω   = 2πf = 628.3 rad/s
```

Calculate:

```
c₀  = √(G'/ρ) = √(5000/1000) = √5 = 2.236 m/s

ωτ  = 628.3 × 0.001 = 0.628

|G*| = G'√[1 + (ωτ)²] = 5000√[1 + 0.394] = 5000 × 1.180 = 5902 Pa

delta = arctan(0.628) = 0.558 rad = 32.0°

cₚ = c₀·√2·[1.394]^(1/4)·cos(0.279)
   = 2.236 × 1.414 × 1.087 × 0.961
   = 3.31 m/s

α = (ω/cₚ)·tan(δ/2)
  = (628.3/3.31)·tan(16°)
  = 189.8 × 0.287
  = 54.5 Np/m = 54.5 m⁻¹

In dB/m: α_dB = 20·log₁₀(e)·α ≈ 8.686 × 54.5 = 473 dB/m
```

**Over 10 wavelengths:**
```
λ = cₚ/f = 3.31/100 = 0.0331 m = 3.31 cm

Distance: 10λ = 0.331 m

Attenuation: 473 × 0.331 = 156 dB

→ Amplitude reduced by factor of 10^(156/20) = 10^7.8
```

**Physical interpretation:** At 100 Hz with η = 5 Pa·s, the wave is heavily attenuated. For your simulations, this suggests either:
- Lower η for observable propagation over cm scales
- Higher frequencies (though this increases α further)
- Verify your simulation shows this attenuation

---

## Key Physical Insights

1. **Relaxation time** `τ = η/G'` sets the frequency scale where viscous effects become important

2. **Loss tangent** `tan(δ) = ωτ` quantifies the ratio of viscous to elastic response

3. **Phase velocity** increases with frequency (normal dispersion) — high frequencies travel faster

4. **Attenuation** is always present in viscoelastic media — no propagation without loss

5. **Kelvin-Voigt limitation:** At very high frequencies, the model predicts unphysical behavior (cₚ → ∞). This is why the Zener model exists.

---

## Extension: Zener Model (Standard Linear Solid)

If time permits, derive for:

```
σ + τ_σ·∂σ/∂t = G_r·(ε + τ_ε·∂ε/∂t)
```

Where `τ_σ` and `τ_ε` are distinct relaxation times. The Zener model bounds the high-frequency phase velocity, addressing the KV limitation.

---

*Derived: 2026-03-17*
*Focus: Deep understanding of viscoelastic wave mechanics*
