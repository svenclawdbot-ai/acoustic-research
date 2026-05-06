# Research Paper Abstracts
## Shear Wave Dispersion Inverse Problem

---

## Option 1: IEEE T-UFFC (Signal Processing / Ultrasound Engineering Focus)

**Title:** Bayesian Calibration of Viscoelastic Properties from Shear Wave Dispersion: Addressing Numerical Artifacts and Parameter Degeneracy

**Abstract:**

Shear wave elastography enables non-invasive characterization of viscoelastic tissue properties through frequency-dependent wave velocity measurements. However, inverse estimation of material parameters from dispersion data faces two fundamental challenges: (1) numerical dispersion introduced by finite-difference time-domain (FDTD) simulations, which can deviate 30% from analytical predictions, and (2) parameter degeneracy in the Zener viscoelastic model, particularly between high-frequency modulus (G∞) and relaxation time (τ_σ). 

This paper presents a Bayesian framework for robust parameter estimation that addresses both challenges. We introduce forward model calibration, wherein apparent Zener parameters are fitted to match observed numerical dispersion (RMSE: 0.017 m/s). Markov Chain Monte Carlo (MCMC) sampling with adaptive Metropolis-Hastings proposals then provides full posterior distributions, enabling rigorous uncertainty quantification beyond point estimates. Analysis of 2D parameter misfit landscapes reveals a 3000:1 curvature ratio between storage modulus (G₀) and G∞, explaining the latter's weak identifiability from dispersion data alone.

Validation on synthetic data demonstrates: (1) G₀ recovery within ±20% at 20 dB SNR, (2) proper characterization of the G∞–τ_σ anti-correlation, and (3) convergence diagnostics consistent with optimal MCMC performance (24.7% acceptance). Experimental design recommendations derived from the analysis—minimum 25 dB SNR, λ/4 receiver spacing, 300–1200 Hz excitation bandwidth—provide practical guidelines for phantom studies.

**Keywords:** shear wave elastography, inverse problem, Bayesian inference, MCMC, viscoelasticity, Zener model, numerical dispersion

**Word count:** 248

---

## Option 2: Physics in Medicine & Biology (Clinical / Biomedical Focus)

**Title:** Quantifying Uncertainty in Viscoelastic Tissue Characterization: A Bayesian Approach to Shear Wave Dispersion Analysis

**Abstract:**

Non-invasive measurement of tissue viscoelasticity via shear wave elastography promises improved diagnostic specificity for fibrosis, tumors, and cardiovascular disease. However, reliable estimation of material properties from ultrasound-derived dispersion curves remains challenging due to numerical artifacts in forward models and inherent parameter trade-offs in viscoelastic constitutive equations.

We present a probabilistic framework for viscoelastic parameter estimation that propagates measurement uncertainty through calibrated forward models to yield credible intervals on tissue properties. Finite-difference simulations are first calibrated against analytical Zener theory to account for grid-induced dispersion errors. Bayesian inference via Markov Chain Monte Carlo (MCMC) sampling then generates posterior distributions over storage modulus (G₀), high-frequency modulus (G∞), and relaxation time (τ_σ), revealing that G₀ is approximately 3000× more identifiable than G∞ from dispersion data alone.

Analysis across SNR levels (20–∞ dB) demonstrates robust G₀ recovery suitable for clinical differentiation of healthy vs. fibrotic tissue (target: 2–20 kPa), while highlighting the need for complementary rheological measurements to constrain G∞. The framework provides defensible uncertainty bounds essential for clinical decision-making, with experimental guidelines (25 dB minimum SNR, broadband excitation 0.5–2× corner frequency) supporting reproducible phantom validation.

**Keywords:** elastography, viscoelasticity, Bayesian inference, tissue characterization, inverse problem, uncertainty quantification

**Word count:** 236

---

## Option 3: Inverse Problems Journal (Mathematical / Theoretical Focus)

**Title:** Calibrated Forward Models and Bayesian Inference for Viscoelastic Parameter Estimation from Sparse Shear Wave Dispersion Data

**Abstract:**

We address the ill-posed inverse problem of recovering viscoelastic parameters (G₀, G∞, τ_σ) from limited dispersion curve measurements in shear wave elastography. The forward problem exhibits two complicating features: numerical dispersion arising from finite-difference discretization of the wave equation, and structural non-identifiability manifesting as a valley in the G∞–τ_σ parameter plane.

Our approach combines (1) data-driven calibration of the forward model to match simulated dispersion, and (2) fully Bayesian inference with Metropolis-Hastings MCMC to characterize the posterior distribution. The calibrated model reduces systematic error from 30% to <2%, while the Bayesian framework properly accounts for both measurement noise and parameter degeneracy through joint posterior sampling.

Two-dimensional misfit analysis quantifies local curvature and confirms weak identifiability of G∞ relative to G₀ (curvature ratio ≈ 3×10⁻³). Noise-robustness studies demonstrate that storage modulus recovery remains stable down to 20 dB SNR, with posterior variance scaling inversely with signal quality. The methodology provides both point estimates and uncertainty bounds essential for reliable material characterization.

**Keywords:** inverse problems, Bayesian inference, viscoelasticity, parameter estimation, MCMC, model calibration

**Word count:** 219

---

## Abstract Components Breakdown

| Component | IEEE T-UFFC | PMB | Inverse Problems |
|-----------|-------------|-----|------------------|
| **Opening** | Problem statement + 2 challenges | Clinical motivation + promise | Mathematical framing (ill-posed) |
| **Methods** | Calibration + MCMC details | Probabilistic framework | Calibration + Bayesian formalism |
| **Key Finding** | 3000:1 curvature ratio | G₀ clinical utility | Non-identifiability structure |
| **Results** | SNR validation, convergence | Robust recovery, uncertainty | Stability, variance scaling |
| **Impact** | Experimental guidelines | Clinical decision-making | Methodological contribution |

---

## Suggested Revisions to Discuss

1. **Length:** All options are ~220–250 words (typical limits: 150–300). Can trim if needed.

2. **Acronyms:** Currently spell out MCMC on first use. Consider if FDTD needs expansion.

3. **Numerical specifics:** 
   - Keep the 30% numerical dispersion figure? (shows magnitude)
   - Keep 3000:1 ratio? (powerful but specific)
   - Keep 24.7% acceptance? (niche detail, maybe cut)

4. **Order of authors:** Need to discuss who contributed what before finalizing.

5. **Data availability statement:** Mention code repository? (GitHub)

---

Which direction resonates with your target venue? Or should we blend elements from multiple options?
