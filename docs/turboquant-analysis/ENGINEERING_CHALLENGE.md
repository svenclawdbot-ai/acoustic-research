# Engineering Challenge — 2026-04-17 (Friday)

## Bayesian Parameter Estimation for Shear Wave Dispersion

### Problem Context

Yesterday you completed a systematic comparison of three time-domain delay estimation methods (envelope, standard GCC, GCC-PHAT). You discovered that GCC-PHAT only provides meaningful advantages at high noise levels (≥20%).

**The next frontier:** Moving beyond point estimates to quantify uncertainty. Your current fitting uses `scipy.optimize.curve_fit` which provides parameter errors, but this assumes Gaussian noise and doesn't capture how noise in the dispersion curve propagates to G' and η estimates.

**Today's goal:** Implement Bayesian inference for Kelvin-Voigt parameter estimation from noisy dispersion data. This will give you credible intervals (not just standard errors) and properly account for measurement uncertainty.

---

### Challenge

Implement Bayesian parameter estimation using MCMC (Markov Chain Monte Carlo) or nested sampling to extract G' and η from dispersion curves with proper uncertainty quantification.

---

### Technical Requirements

#### Part 1: Likelihood Function (30 min)

**Current state:** You fit by minimizing least-squares:
```python
def residuals(params, omega, velocities, uncertainties):
    G_prime, eta = params
    c_model = kelvin_voigt_velocity(omega, G_prime, eta, rho)
    return (velocities - c_model) / uncertainties
```

**Task:** Convert to proper likelihood for Bayesian inference.

**Likelihood model:**
```python
def log_likelihood(params, omega, velocities, uncertainties):
    """
    Gaussian likelihood accounting for measurement uncertainty.
    
    For each frequency point:
    log L_i = -0.5 * [(v_meas - v_model)²/σ² + log(2πσ²)]
    """
    G_prime, eta = params
    c_model = kelvin_voigt_velocity(omega, G_prime, eta, rho)
    
    # Variance includes measurement uncertainty
    sigma = uncertainties  # measurement noise
    
    residuals = velocities - c_model
    chi2 = np.sum((residuals / sigma)**2)
    log_norm = np.sum(np.log(2 * np.pi * sigma**2))
    
    return -0.5 * (chi2 + log_norm)
```

**Deliverable:**
- Function `log_likelihood(params, data)`
- Test on synthetic data: verify likelihood peaks at true parameters
- Plot likelihood surface over (G', η) grid to visualize shape

---

#### Part 2: Priors (15 min)

**Task:** Define physically-motivated priors for shear wave parameters.

**Priors for soft tissue:**
| Parameter | Physical Range | Prior Type | Justification |
|-----------|---------------|------------|---------------|
| G' (storage modulus) | 100 - 50,000 Pa | Log-uniform | Soft tissues span ~2 orders of magnitude |
| η (viscosity) | 0.001 - 100 Pa·s | Log-uniform | From water-like to highly viscous |
| ρ (density) | ~1000 kg/m³ | Fixed | Nearly constant for soft tissues |

**Deliverable:**
- `log_prior(params)` function
- Plot prior distributions
- Verify priors don't exclude physically reasonable values

---

#### Part 3: MCMC Sampling (45 min)

**Task:** Use `emcee` (affine-invariant ensemble sampler) or `dynesty` (nested sampling) to sample the posterior.

**With emcee:**
```python
import emcee

def log_probability(params, omega, velocities, uncertainties):
    lp = log_prior(params)
    if not np.isfinite(lp):
        return -np.inf
    return lp + log_likelihood(params, omega, velocities, uncertainties)

# Initialize walkers
n_walkers = 32
n_dim = 2
pos = [true_params + 1e-3 * np.random.randn(n_dim) for _ in range(n_walkers)]

sampler = emcee.EnsembleSampler(n_walkers, n_dim, log_probability,
                                args=(omega, velocities, uncertainties))
sampler.run_mcmc(pos, 5000, progress=True)
```

**Deliverable:**
- Working MCMC sampler producing converged chains
- Trace plots showing good mixing
- Corner plot showing parameter correlations
- Posterior summary statistics (median, 16th/84th percentiles)

---

#### Part 4: Comparison with Frequentist (30 min)

**Task:** Compare Bayesian credible intervals with frequentist confidence intervals.

**Generate test cases:**
| Noise Level | N frequencies | Test |
|-------------|---------------|------|
| 5% | 9 points | Well-constrained |
| 15% | 5 points | Moderately constrained |
| 25% | 3 points | Poorly constrained |

**Metrics to compare:**
1. Point estimate: MCMC median vs curve_fit MLE
2. Uncertainty: credible interval width vs std error
3. Coverage: Does 68% CI contain true value ~68% of repeated trials?

**Deliverable:**
- Table comparing Bayesian vs frequentist results
- Analysis: When does Bayesian approach provide different answers?

---

#### Part 5: Visualization (Optional — 30 min)

**Task:** Create publication-quality figures showing:

1. **Posterior predictive:** Sample model curves from posterior overlaid on data
   ```python
   # Sample 100 parameter sets from posterior
   # Plot c(ω) for each as thin grey lines
   # Highlight median and 95% credible band
   ```

2. **Uncertainty propagation:** Show how measurement uncertainty → parameter uncertainty
   - Plot 1σ measurement error bars on velocities
   - Show corresponding uncertainty region in (G', η) space

3. **Decision analysis:** If you need to distinguish tissue types:
   - Tissue A: G' = 2000 ± 300 Pa
   - Tissue B: G' = 3500 ± 400 Pa
   - Compute probability that B > A

---

### Key Equations

**Kelvin-Voigt dispersion (velocity model):**
```
|G*(ω)| = √(G'² + (ωη)²)
c(ω) = √(2/ρ) · √(|G*|² / (G' + |G*|))
```

**Gaussian likelihood:**
```
log L = -½ Σ [(v_i - c(ω_i; G', η))²/σ_i² + log(2πσ_i²)]
```

**Log-uniform prior:**
```
p(θ) = 1/(θ · log(θ_max/θ_min))  for θ ∈ [θ_min, θ_max]
```

---

### Hints

- **emcee** is good for well-behaved posteriors (your case)
- **dynesty** is better for complex posteriors with multiple modes
- Check convergence: `emcee.autocorr.integrated_time()` should be << chain length
- Burn-in: Discard first ~1000 steps as equilibrium hasn't been reached
- Thinning: Keep only every N-th sample if autocorrelation time is large

---

### Expected Results

On well-constrained data (9 frequencies, 5% noise):
- G': 2000 ± 100 Pa (tight constraint)
- η: 0.5 ± 0.1 Pa·s (weaker constraint — expected because η has subtle effect on velocities)

On poorly-constrained data (3 frequencies, 25% noise):
- G': 2000 ± 800 Pa (broad posterior)
- η: 0.5 ± 0.5 Pa·s (essentially unconstrained)

**Key insight:** Bayesian approach properly quantifies when parameters are poorly constrained, rather than giving spuriously small error bars.

---

### Deliverables Summary

1. **`bayesian_dispersion.py`** — Full MCMC implementation
2. **Likelihood surface plot** — Visualize the parameter space
3. **Corner plot** — Show posterior distributions and correlations
4. **Comparison table** — Bayesian vs frequentist on test cases
5. **Posterior predictive plot** — Model uncertainty visualization

---

**Difficulty:** Intermediate-Advanced (Bayesian statistics + MCMC)  
**Est. Time:** 2-2.5 hours  
**Topic:** Bayesian Inference / Uncertainty Quantification / Rheology

## Status: 🆕 NOT STARTED

*Generated: 2026-04-17 07:05 UTC*
