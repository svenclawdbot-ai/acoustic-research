# Anti-Overfitting Strategy for Shear Wave Elastography

## The Core Problem

When you estimate (G', η) from displacement data u(x,t), you have:
- **2 unknowns**: G' (storage modulus), η (viscosity)
- **Many data points**: u(x₁,t₁), u(x₂,t₂), ...

This seems overdetermined, BUT the forward problem is:
1. **Non-linear**: Wave speed depends on √G'
2. **Ill-posed**: High-frequency noise amplifies under differentiation
3. **Correlated parameters**: G' and η affect wave propagation similarly at certain frequencies

## 1. Theoretical Constraints (Strongest Protection)

### Physical Bounds as Priors
```python
# Hard constraints from tissue physics
G_prime_bounds = (100, 50000)      # Pa - soft tissue range
eta_bounds = (0.1, 100)            # Pa·s - physiological range

# Soft tissue typically:
# Liver:  G' ≈ 2-6 kPa, η ≈ 3-8 Pa·s
# Muscle: G' ≈ 10-15 kPa, η ≈ 5-15 Pa·s
```

### Dispersion Relationship Check
The theoretical dispersion relation MUST be satisfied:
```
c_s(ω) = √[2(G'² + (ωη)²) / (ρ(G' + √(G'² + (ωη)²)))]
```

**Validation**: If your estimated (G', η) don't reproduce the measured dispersion curve, you're overfitting.

## 2. Data Strategy

### Multi-Frequency Requirement
**Rule**: You need frequencies spanning at least one octave (2× frequency range).

```
✓ Good: 50 Hz, 100 Hz, 200 Hz, 400 Hz (factor of 8 span)
✗ Bad:  95 Hz, 100 Hz, 105 Hz, 110 Hz (factor of 1.15 span)
```

**Why**: G' dominates at low frequencies, η dominates at high frequencies. Without separation, they're indistinguishable.

### Spatial Sampling
**Nyquist for shear waves**:
```
dx ≤ λ_min/2 = c_s/(2*f_max)

For f_max = 400 Hz, c_s = 2 m/s:
dx ≤ 2/(2*400) = 2.5 mm
```

**Overfitting risk**: If you oversample spatially (dx << λ/10), you fit noise in the FDTD grid, not physics.

### Temporal Sampling
```
dt < dx/c_s  (CFL condition for stability)
dt < 1/(10*f_max)  (for source resolution)
```

## 3. Regularization Techniques

### Tikhonov (L2) Regularization
```python
# Cost function: J = ||u_measured - u_simulated||² + α||L·p||²
# where p = [G', η], L is regularization operator

def cost_function(params, data, alpha=0.01):
    G_prime, eta = params
    u_sim = forward_model(G_prime, eta)
    
    # Data misfit
    residual = np.sum((data - u_sim)**2)
    
    # Regularization (penalize deviation from expected values)
    # Physical prior: G' ≈ 5000, η ≈ 5 for liver
    prior_penalty = alpha * ((G_prime - 5000)**2/5000**2 + (eta - 5)**2/5**2)
    
    return residual + prior_penalty
```

### L1 Regularization (Sparsity)
Use when you expect piecewise-homogeneous tissue:
```python
penalty = alpha * (np.abs(G_prime - G_prime_neighbor) + 
                   np.abs(eta - eta_neighbor))
```

### Total Variation (TV) Regularization
For spatially varying parameters:
```python
tv_penalty = alpha * np.sum(np.abs(np.gradient(G_prime)) + 
                            np.abs(np.gradient(eta)))
```

## 4. Cross-Validation Strategy

### Leave-One-Frequency-Out
```python
frequencies = [50, 100, 200, 300, 400]
errors = []

for i in range(len(frequencies)):
    # Train on all frequencies except i
    train_freqs = frequencies[:i] + frequencies[i+1:]
    test_freq = frequencies[i]
    
    G_est, eta_est = invert(train_data, train_freqs)
    
    # Test on held-out frequency
    u_pred = forward_model(G_est, eta_est, f=test_freq)
    error = np.mean((u_test - u_pred)**2)
    errors.append(error)

mean_cv_error = np.mean(errors)  # Cross-validation score
```

**Interpretation**: If CV error >> training error, you're overfitting.

### Space-Time Split
```python
# Train on early time, test on late time (or vice versa)
train_mask = t < 0.02  # First 20ms
test_mask = t >= 0.02   # Later times

# Or spatial split
train_mask = x < 0.03   # Near field
test_mask = x >= 0.03   # Far field
```

## 5. Model Complexity Control

### Occam's Razor: Start Simple
```
Week 1: Homogeneous medium (constant G', η)
Week 2: 2-layer model (if data supports it)
Week 3: Continuous variation (only if CV improves)
```

**Rule**: Each additional parameter must improve CV score by >10%.

### Information Criteria
```python
def AIC(residual, n_params, n_data):
    """Akaike Information Criterion"""
    return n_data * np.log(residual/n_data) + 2 * n_params

def BIC(residual, n_params, n_data):
    """Bayesian Information Criterion (stronger penalty)"""
    return n_data * np.log(residual/n_data) + n_params * np.log(n_data)

# Compare models
model_1 = AIC(residual_1, n_params=2, n_data=1000)  # (G', η)
model_2 = AIC(residual_2, n_params=4, n_data=1000)  # (G', η) × 2 layers

if model_1 < model_2:
    print("Simpler model is better - don't overfit with layers")
```

## 6. Uncertainty Quantification

### Bootstrap Resampling
```python
n_bootstrap = 100
G_estimates = []
eta_estimates = []

for _ in range(n_bootstrap):
    # Resample data with replacement
    idx = np.random.choice(len(data), size=len(data), replace=True)
    data_boot = data[idx]
    
    G, eta = invert(data_boot)
    G_estimates.append(G)
    eta_estimates.append(eta)

# 95% confidence intervals
G_ci = np.percentile(G_estimates, [2.5, 97.5])
eta_ci = np.percentile(eta_estimates, [2.5, 97.5])

print(f"G' = {np.mean(G_estimates):.0f} [{G_ci[0]:.0f}, {G_ci[1]:.0f}] Pa")
print(f"η = {np.mean(eta_estimates):.1f} [{eta_ci[0]:.1f}, {eta_ci[1]:.1f}] Pa·s")

# If CI is huge relative to mean, you're overfitting
```

### Fisher Information Matrix
```python
# For Cramér-Rao lower bound (theoretical minimum variance)
def fisher_matrix(params, data):
    G, eta = params
    epsilon = 1e-6
    
    # Numerical derivatives
    u_G = (forward_model(G+epsilon, eta) - forward_model(G-epsilon, eta)) / (2*epsilon)
    u_eta = (forward_model(G, eta+epsilon) - forward_model(G, eta-epsilon)) / (2*epsilon)
    
    F = np.array([[np.sum(u_G**2), np.sum(u_G*u_eta)],
                  [np.sum(u_G*u_eta), np.sum(u_eta**2)]])
    return F

F = fisher_matrix([G_est, eta_est], data)
cov = np.linalg.inv(F)  # Covariance matrix
std_G = np.sqrt(cov[0,0])
std_eta = np.sqrt(cov[1,1])

print(f"Theoretical minimum std(G') = {std_G:.1f} Pa")
print(f"Theoretical minimum std(η) = {std_eta:.2f} Pa·s")

# If your bootstrap std >> Fisher std, check your noise model
```

## 7. Specific Red Flags for FDTD

### 1. Grid-Scale Oscillations
```python
# Check if solution has energy at grid scale
u_fft = np.fft.fft(u)
high_freq_energy = np.sum(np.abs(u_fft[nx//2:])) / np.sum(np.abs(u_fft))

if high_freq_energy > 0.1:
    print("WARNING: Possible numerical instability or overfitting to noise")
    print("→ Check CFL condition, reduce dt, or add artificial viscosity")
```

### 2. Non-Physical Dispersion
```python
# Plot phase velocity vs frequency
# If curve has wiggles not predicted by Kelvin-Voigt model:
# → You're fitting numerical dispersion, not physics

# Theoretical KV dispersion should be smooth and monotonic
```

### 3. Source Injection Artifacts
```python
# Check that source region doesn't dominate fit
# Weight residuals inversely by distance from source

weights = 1 / (1 + (x - x_source)**2 / sigma**2)
residual = np.sum(weights * (data - model)**2)
```

## 8. Validation Checklist

Before trusting your (G', η) estimates:

- [ ] **Physical bounds**: Are values in physiological range?
- [ ] **Cross-validation**: Does model predict held-out frequencies?
- [ ] **Dispersion fit**: Does estimated (G', η) reproduce full dispersion curve?
- [ ] **Bootstrap CI**: Are confidence intervals tight (<30% of mean)?
- [ ] **Residual analysis**: Are residuals random (not systematic)?
- [ ] **Grid convergence**: Do results change if you halve dx?
- [ ] **Time convergence**: Do results change if you halve dt?
- [ ] **AIC/BIC**: Does complexity improve information criteria?

## 9. Practical Implementation Order

```python
# Step 1: Generate synthetic data with KNOWN G', η
true_G, true_eta = 5000, 5
synthetic_data = forward_model(true_G, true_eta)
synthetic_data += 0.01 * np.random.randn(*synthetic_data.shape) * np.max(synthetic_data)

# Step 2: Recover parameters
estimated_G, estimated_eta = invert(synthetic_data)

# Step 3: Verify you can recover ground truth
assert np.abs(estimated_G - true_G) / true_G < 0.1  # Within 10%
assert np.abs(estimated_eta - true_eta) / true_eta < 0.2  # Within 20%

# Step 4: Now apply to real data with confidence
```

**Golden Rule**: If you can't recover known parameters from synthetic data with added noise, you won't recover them from real data.

## 10. Recommended Reading

1. **Oberai et al. (2004)** - "Linear and nonlinear elasticity imaging"
   - Section on regularization in inverse elasticity

2. **Barbosa et al. (2019)** - "Rapid multi-frequency MR elastography"
   - Multi-frequency regularization strategies

3. **Klatt et al. (2020)** - "MR elastography: Robust inversion"
   - Balancing data fidelity and model complexity

4. **Graham et al. (2018)** - "Fractional derivative models for viscoelasticity"
   - Model selection beyond Kelvin-Voigt

## Summary

**To avoid overfitting:**
1. Use physical bounds (100 < G' < 50000 Pa, 0.1 < η < 100 Pa·s)
2. Require multi-frequency data (span >2× frequency)
3. Regularize with L2 or TV (α determined by L-curve)
4. Cross-validate (leave-one-frequency-out)
5. Bootstrap for uncertainty
6. Verify on synthetic data first
7. Check grid/time convergence

**Red flags:**
- Parameters at bounds
- High-frequency oscillations in solution
- Huge bootstrap confidence intervals
- CV error >> training error
- Different results with dx/2
