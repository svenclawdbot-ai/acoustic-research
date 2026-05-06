# Zener Dispersion Derivation — Worksheet
## Tuesday, March 24, 2026

---

## Part 1: Derive G*(ω) from the Mechanical Model

### Setup
The Zener model (Standard Linear Solid):

```
         ┌──[G_r]──┐
     σ ──┤         ├── ε
         └──[G_1]─[η]──┘
```

Where:
- G_r = relaxed modulus (parallel spring, active at all frequencies)
- G_1 = series spring in Maxwell branch (active only at high frequency)
- η = dashpot viscosity
- τσ = η/G_1 = stress relaxation time

At low frequency (ω → 0): G* → G_r (dashpot flows, series spring shielded)
At high frequency (ω → ∞): G* → G_r + G_1 = G_inf (dashpot frozen, both springs active)

### Your Task: Fill in the steps

**Step 1.1:** Write stress in each branch
- Branch 1 (spring G_r): σ₁ = ____
- Branch 2 (Maxwell): σ₂ + τσ·∂σ₂/∂t = ____

**Step 1.2:** Total stress relation
Since parallel: σ = σ₁ + σ₂, and ε₁ = ε₂ = ε

Take Fourier transform (∂/∂t → iω) and solve for G* = σ/ε:

```
G*(ω) = G_r + G_1·(iωτσ)/(1 + iωτσ)
```

**Step 1.3:** Rationalize by multiplying by (1 - iωτσ)/(1 - iωτσ)

Expand and separate into real and imaginary parts:

- **G'(ω) = [G_r + (G_r + G_1)(ωτσ)²] / [1 + (ωτσ)²]**
- **G''(ω) = [G_1·ωτσ] / [1 + (ωτσ)²]**

**Checkpoint 1:** 
- At ω = 0: G'(0) = G_r ✓
- At ω → ∞: G'(∞) = G_r + G_1 = G_inf ✓

---

## Part 2: Derive Phase Velocity cₚ(ω)

### Start from the wave equation
For shear waves: ρ·∂²u/∂t² = ∇·τ

In Fourier domain: -ρω²u = -k²G*(ω)u

Therefore: k² = ρω²/G*(ω)

### Your Task:

**Step 2.1:** Express k as complex quantity

k = kᵣ + ikᵢ = ω√(ρ/G*)

**Step 2.2:** Use the identity for complex modulus
Let G* = |G*|e^(iφ) where |G*| = √(G'² + G''²) and tan(φ) = G''/G'

Then: k = ω√(ρ/|G*|)·e^(-iφ/2)

Using Euler's formula: e^(-iφ/2) = cos(φ/2) - i·sin(φ/2)

**Step 2.3:** Identify real and imaginary parts
- kᵣ = Re(k) = ____________________
- kᵢ = Im(k) = ____________________

**Step 2.4:** Phase velocity
```
cₚ(ω) = ω/kᵣ = ____________________
```

Use half-angle formulas:
- cos(φ/2) = √((1 + cos(φ))/2)
- sin(φ/2) = √((1 - cos(φ))/2)
- cos(φ) = G'/|G*|

**Final Result:**
```
cₚ(ω) = √[2|G*|² / (ρ(|G*| + G'))]
```

---

## Part 3: Derive Attenuation α(ω)

### Your Task:

From kᵢ above, attenuation is:
```
α(ω) = -kᵢ = ____________________
```

Using the same half-angle approach:

**Final Result:**
```
α(ω) = ω·√[ρ(|G*| - G') / (2|G*|²)]
```

---

## Part 4: Limiting Behavior (Verification)

### Low frequency: ωτσ ≪ 1

**Step 4.1:** Show G'(ω) → G_r (parallel spring only)
**Step 4.2:** Show G''(ω) → (G_inf - G_r)ωτσ (linear in ω)
**Step 4.3:** Show |G*| → G_r
**Step 4.4:** Show cₚ → √(G_r/ρ) = c₀

### High frequency: ωτσ ≫ 1

**Step 4.5:** Show G'(ω) → G_inf = G_r + G_1 (both springs active)
**Step 4.6:** Show G''(ω) → 0 (dashpot "freezes")
**Step 4.7:** Show |G*| → G_inf
**Step 4.8:** Show cₚ → √(G_inf/ρ) = c∞

**Physical meaning:** At high frequency, the dashpot has no time to flow, so the series spring G_1 becomes fully active. Total stiffness = G_r + G_1.

---

## Part 5: Alternative Form (for coding)

### Direct formulas

Define:
- G_r = relaxed modulus (parallel spring)
- G_inf = unrelaxed modulus = G_r + G_1 (both springs at high frequency)
- G_1 = G_inf - G_r (series spring in Maxwell branch)
- τσ = η/G_1 (stress relaxation time)

**Storage modulus:**
```
G'(ω) = [G_r + G_inf·(ωτσ)²] / [1 + (ωτσ)²]
```

**Loss modulus:**
```
G''(ω) = [(G_inf - G_r)·ωτσ] / [1 + (ωτσ)²]
```

**Phase velocity:**
```
cₚ(ω) = (1/√ρ) · √[2|G*|² / (√(G'² + G''²) + G')]
```

**Attenuation (Np/m):**
```
α(ω) = ω · √[ρ(√(G'² + G''²) - G') / (2|G*|²)]
```

### Parameter reference for validation
- G_r = 5000 Pa
- G_inf = 8000 Pa  
- τσ = 0.001 s
- ρ = 1000 kg/m³

Expected:
- c₀ = √(G_r/ρ) = 2.236 m/s (low frequency)
- c∞ = √(G_inf/ρ) = 2.828 m/s (high frequency)

---

## Validation: Theory vs Simulation

Run `validate_zener_derivation.py` to check your formulas against the 2D simulation data.

Expected agreement: < 1% error for phase velocity, < 5% for attenuation.

---

## Deliverables Checklist

- [ ] Part 1: G*(ω) derivation complete
- [ ] Part 2: cₚ(ω) derivation complete  
- [ ] Part 3: α(ω) derivation complete
- [ ] Part 4: Limiting cases verified
- [ ] Validation plot: theory vs simulation
- [ ] Brief interpretation (2-3 sentences)

---

*Good luck! Take your time — deep understanding beats fast completion.*
