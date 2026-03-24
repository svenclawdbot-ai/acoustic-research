# Deep Dive: Zener Model (Standard Linear Solid) Dispersion
## Date: 2026-03-17 — Extension from Kelvin-Voigt

---

## The Problem with Kelvin-Voigt at High Frequencies

From KV derivation:
```
cₚ → c₀·√(ωτ)  as ωτ → ∞
```

Phase velocity grows without bound — **unphysical** for real materials.

**Why:** At infinite frequency, the dashpot becomes infinitely stiff (acts as rigid connection), leaving only the parallel spring. But the KV model has no series compliance to limit the response.

---

## Step 1: Zener Model Mechanics

### Mechanical Representation

```
         ┌─ Spring G_r ─┐
    σ ──┤              ├── ε
         └─ Maxwell ────┘
              │
         ┌─ Spring G_1 ─┐
    σ₁ ──┤              ├── ε₁
         └─ Dashpot η ──┘
```

The Zener model consists of:
1. A **spring** `G_r` (relaxed modulus) in parallel with
2. A **Maxwell element** (spring `G_1` in series with dashpot `η`)

### Total Strain and Stress Relations

Since parallel:
```
σ = σ_r + σ_1
ε = ε_r = ε_1  (same strain across both branches)
```

Branch stresses:
```
σ_r = G_r·ε                    (elastic branch)
σ_1 = G_1·(ε - ε_viscous)      (Maxwell branch)
```

For the Maxwell element, stress is same in spring and dashpot:
```
σ_1 = G_1·ε_1e = η·ε̇_1v
ε = ε_1e + ε_1v                (total strain in Maxwell branch)
```

---

## Step 2: Derive Constitutive Equation

From Maxwell branch:
```
ε̇ = ε̇_1e + ε̇_1v = (σ̇_1/G_1) + (σ_1/η)
```

Rearrange:
```
σ_1 + (η/G_1)·σ̇_1 = η·ε̇
```

Define **relaxation time for stress**:
```
τ_σ = η/G_1
```

So:
```
σ_1 + τ_σ·σ̇_1 = η·ε̇
```

But `σ_1 = σ - σ_r = σ - G_r·ε`, and `σ̇_1 = σ̇ - G_r·ε̇`:

```
(σ - G_r·ε) + τ_σ·(σ̇ - G_r·ε̇) = η·ε̇
```

Expand:
```
σ + τ_σ·σ̇ - G_r·ε - τ_σ·G_r·ε̇ = η·ε̇
```

Rearrange:
```
σ + τ_σ·σ̇ = G_r·ε + (τ_σ·G_r + η)·ε̇
```

Define **relaxation time for strain**:
```
τ_ε = τ_σ + η/G_r = η/G_1 + η/G_r = η·(1/G_1 + 1/G_r)
```

**Zener constitutive equation:**

```
σ + τ_σ·σ̇ = G_r·(ε + τ_ε·ε̇)
```

Or in standard form:

```
σ + τ_σ·(∂σ/∂t) = G_r·ε + G_r·τ_ε·(∂ε/∂t)
```

---

## Step 3: Complex Modulus Derivation

Assume harmonic time dependence: `∂/∂t → -iω`

Substitute into constitutive equation:
```
σ(1 - iωτ_σ) = G_r·ε(1 - iωτ_ε)
```

**Complex modulus G*(ω):**

```
G*(ω) = σ/ε = G_r·(1 - iωτ_ε) / (1 - iωτ_σ)
```

Rationalize by multiplying by complex conjugate:
```
G*(ω) = G_r·(1 - iωτ_ε)(1 + iωτ_σ) / (1 + ω²τ_σ²)
```

Expand numerator:
```
= G_r·[1 + iωτ_σ - iωτ_ε + ω²τ_ετ_σ] / (1 + ω²τ_σ²)

= G_r·[(1 + ω²τ_ετ_σ) + iω(τ_σ - τ_ε)] / (1 + ω²τ_σ²)
```

Separate into storage and loss modulus:

```
G'(ω) = G_r·(1 + ω²τ_ετ_σ) / (1 + ω²τ_σ²)

G''(ω) = G_r·ω(τ_ε - τ_σ) / (1 + ω²τ_σ²)
```

Note: `τ_ε > τ_σ` always, so `G'' > 0` (positive dissipation).

---

## Step 4: Alternative Parameterization (More Common)

Most texts use:
- `G_u` = unrelaxed modulus (high frequency limit)
- `G_r` = relaxed modulus (low frequency limit)
- Single relaxation time `τ`

From our model:
```
G_u = G_r + G_1  (both springs active at t=0)
G_r = G_r        (only relaxed spring at t→∞)
```

Define:
```
ΔG = G_u - G_r = G_1
```

With this, the complex modulus becomes:

```
G*(ω) = G_r + (G_u - G_r)/(1 + iωτ)

      = [G_r(1 + iωτ) + G_u - G_r] / (1 + iωτ)

      = (G_u + iωτG_r) / (1 + iωτ)
```

Rationalized:
```
G'(ω) = (G_u + G_r·ω²τ²) / (1 + ω²τ²)

G''(ω) = (G_u - G_r)·ωτ / (1 + ω²τ²)
```

---

## Step 5: Phase Velocity and Attenuation

From wave mechanics:
```
k² = ρω² / G*(ω)

k = ω√(ρ/G*)
```

The complex modulus in polar form:
```
G* = |G*|·exp(iδ)

tan(δ) = G''/G'
```

Therefore:
```
k = ω√(ρ/|G*|)·exp(-iδ/2)
```

Phase velocity:
```
cₚ = ω/Re(k) = √(|G*|/ρ) / cos(δ/2)
```

Attenuation:
```
α = Im(k) = ω√(ρ/|G*|)·sin(δ/2)
```

---

## Step 6: Limiting Behavior (Key Result)

### Low Frequency (ωτ ≪ 1):

```
G' ≈ G_r
G'' ≈ (G_u - G_r)·ωτ
```

```
cₚ ≈ √(G_r/ρ) = c_r      (relaxed wave speed)
α ∝ ω²                   (quadratic, same as KV)
```

### High Frequency (ωτ ≫ 1):

```
G' ≈ G_u                 (approaches unrelaxed modulus!)
G'' ≈ (G_u - G_r)/(ωτ)   → 0 at very high frequency
```

**Phase velocity limit:**
```
cₚ → √(G_u/ρ) = c_u      (bounded!)
```

**Attenuation limit:**
```
α → 0                    (loss decreases at high frequency)
```

**Physical interpretation:** At high frequency, the dashpot "freezes" (no time to flow), and the Maxwell spring G_1 takes over. Total stiffness approaches `G_u = G_r + G_1`, and since there's no viscous flow, attenuation vanishes.

---

## Step 7: Comparison — Kelvin-Voigt vs Zener

| Property | Kelvin-Voigt | Zener |
|----------|--------------|-------|
| Parameters | G', η | G_r, G_u, τ |
| Low-freq limit | c₀ = √(G'/ρ) | c_r = √(G_r/ρ) |
| High-freq limit | cₚ → ∞ (unphysical) | c_u = √(G_u/ρ) (bounded) |
| Attenuation peak | Monotonic increase | Peaks at ωτ ≈ 1 |
| Physical realism | Poor at high ω | Good across all ω |

---

## Step 8: Numerical Example (Your Parameters)

Match Zener to KV at low frequency:
```
G_r = 5000 Pa  (match G' from KV)
c_r = √(5000/1000) = 2.236 m/s
```

Choose reasonable unrelaxed modulus:
```
G_u = 7500 Pa  (50% increase at high frequency)
G_1 = G_u - G_r = 2500 Pa
```

Choose relaxation time:
```
τ = 1 ms = 0.001 s  (same as KV τ for comparison)
```

Calculate at f = 100 Hz (ω = 628.3 rad/s):

```
ωτ = 0.628
ω²τ² = 0.394

G'(ω) = (7500 + 5000×0.394) / (1 + 0.394)
      = (7500 + 1970) / 1.394
      = 9470 / 1.394
      = 6793 Pa

G''(ω) = (7500 - 5000)×0.628 / 1.394
       = 2500 × 0.628 / 1.394
       = 1126 Pa

|G*| = √(6793² + 1126²) = √(46.1×10⁶ + 1.27×10⁶)
     = √47.4×10⁶
     = 6884 Pa

delta = arctan(1126/6793) = arctan(0.166) = 0.164 rad = 9.4°

cₚ = √(6884/1000) / cos(0.082)
   = 2.62 / 0.997
   = 2.63 m/s

α = ω√(ρ/|G*|)·sin(δ/2)
  = 628.3 × √(1000/6884) × sin(0.082)
  = 628.3 × 0.381 × 0.082
  = 19.6 Np/m = 170 dB/m
```

Compare to KV at same parameters:
```
KV: cₚ = 3.31 m/s, α = 473 dB/m
Zener: cₚ = 2.63 m/s, α = 170 dB/m
```

**Key differences:**
- Zener has lower phase velocity (less dispersion at this frequency)
- Zener has much lower attenuation (factor of ~2.8)
- Zener predicts bounded behavior as f → ∞

---

## Step 9: Attenuation Peak Analysis

The Zener model predicts maximum attenuation at intermediate frequencies.

From:
```
G''(ω) = (G_u - G_r)·ωτ / (1 + ω²τ²)
```

Maximum occurs when `dG''/dω = 0`:
```
ω_peak = 1/τ

G''_max = (G_u - G_r)/2
```

**For your parameters:**
```
f_peak = 1/(2πτ) = 1/(2π×0.001) = 159 Hz

At f = 159 Hz:
G''_max = 2500/2 = 1250 Pa
```

This peak attenuation frequency is experimentally observable and can be used to identify the relaxation time in tissue characterization.

---

## Step 10: Wave Equation in Zener Medium

The time-domain wave equation is third-order in time:

```
τ_σ·ρ·(∂³u/∂t³) + ρ·(∂²u/∂t²) = G_r·τ_ε·(∂³u/∂x²∂t) + G_r·(∂²u/∂x²)
```

Or in standard form:
```
ρ·(∂²u/∂t²) + τ_σ·ρ·(∂³u/∂t³) = G_r·(∂²u/∂x²) + G_r·τ_ε·(∂³u/∂x²∂t)
```

**Physical interpretation:**
- Left side: Inertia + inertial memory (from stress relaxation)
- Right side: Elastic restoring + viscoelastic coupling

This third-order PDE requires careful numerical treatment — standard FDTD schemes may need modification for stability.

---

## Summary: When to Use Which Model

| Scenario | Recommended Model |
|----------|-------------------|
| Low frequencies (ωτ ≪ 1) | Kelvin-Voigt (simpler, same result) |
| Broadband characterization | Zener (physical at all frequencies) |
| High-frequency applications (>1 kHz in soft tissue) | Zener essential |
| Multiple relaxation processes | Generalized Zener (parallel Zener elements) |
| FDTD simulation with stability concerns | KV simpler; Zener needs careful implementation |

---

## Key Equations Reference

**Zener Complex Modulus:**
```
G*(ω) = G_r + (G_u - G_r)/(1 + iωτ)
```

**Storage Modulus:**
```
G'(ω) = (G_u + G_r·ω²τ²) / (1 + ω²τ²)
```

**Loss Modulus:**
```
G''(ω) = (G_u - G_r)·ωτ / (1 + ω²τ²)
```

**Phase Velocity:**
```
cₚ(ω) = √[2|G*(ω)|² / (ρ(|G*(ω)| + G'(ω)))]
```

**Attenuation:**
```
α(ω) = ω·√[ρ(|G*(ω)| - G'(ω)) / (2|G*(ω)|²)]
```

**Loss Tangent:**
```
tan(δ) = G''/G' = (G_u - G_r)·ωτ / (G_u + G_r·ω²τ²)
```

---

*Extended derivation complete: Zener (Standard Linear Solid) model*
*Key insight: High-frequency boundedness makes Zener physically realistic for broadband elastography*
