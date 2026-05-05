# Engineering Challenge — 2026-04-22

## Topic: Noise-Robust Dispersion Curve Extraction via Bayesian Inference

### Context
Yesterday you worked on material parameter inversion from dispersion curves using least-squares fitting. Today we step up robustness: real experimental data is noisy, and least-squares can fail catastrophically when dispersion curves are partially obscured or mode-mixed.

### 🎯 Challenge Tasks

1. **Synthetic Ground Truth**
   - Generate 2D shear wave field with known Kelvin-Voigt parameters (G', η)
   - Add realistic noise: AWGN at 0, -10, -20 dB SNR + coherent clutter
   - Save as `synthetic_wavefield_noisy.npy`

2. **Dispersion Extraction Pipeline**
   - Implement 2D FFT → f-k transform
   - Extract phase velocity c(f) = 2πf/k(f) for each SNR level
   - Quantify extraction error vs SNR

3. **Bayesian Parameter Estimation**
   - Set up probabilistic model: p(G', η | observed c(f))
   - Use uniform priors over plausible ranges (G' ~ [1e6, 1e9] Pa, η ~ [1e-3, 1e1] Pa·s)
   - Implement Metropolis-Hastings or NUTS sampler
   - Compare posterior credible intervals vs. least-squares point estimates

4. **Robustness Analysis**
   - Test on incomplete data: mask 30-50% of frequency range
   - Compare: least-squares (fails?) vs Bayesian (still converges?)
   - Report when each method breaks down

### 📦 Deliverables
- `bayesian_inversion.py` — working sampler + visualization
- `robustness_report.md` — table of SNR vs extraction accuracy for both methods
- Updated `memory/2026-04-22.md` with findings

### ⏱️ Time Budget: 2-3 hours focused work
### 🔗 Builds On: `dispersion_inverse_problem.py`, `validate_robust_extraction.py`
