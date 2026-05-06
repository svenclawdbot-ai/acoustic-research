# IEEE T-UFFC Submission — Refined Abstract

---

## Final Abstract (IEEE Transactions on Ultrasonics, Ferroelectrics, and Frequency Control)

**Title:** Bayesian Calibration of Viscoelastic Properties from Shear Wave Dispersion: Addressing Numerical Artifacts and Parameter Degeneracy

**Abstract (248 words):**

Shear wave elastography enables non-invasive characterization of viscoelastic tissue properties through frequency-dependent wave velocity measurements. However, inverse estimation of material parameters from dispersion data faces two fundamental challenges: (1) numerical dispersion introduced by finite-difference time-domain (FDTD) simulations, which can deviate 30% from analytical predictions, and (2) parameter degeneracy in the Zener viscoelastic model, particularly between high-frequency modulus ($G_\infty$) and relaxation time ($\tau_\sigma$).

This paper presents a Bayesian framework for robust parameter estimation that addresses both challenges. We introduce forward model calibration, wherein apparent Zener parameters are fitted to match observed numerical dispersion (RMSE: 0.017 m/s). Markov Chain Monte Carlo (MCMC) sampling with adaptive Metropolis-Hastings proposals then provides full posterior distributions, enabling rigorous uncertainty quantification beyond point estimates. Analysis of 2D parameter misfit landscapes reveals a 3000:1 curvature ratio between storage modulus ($G_0$) and $G_\infty$, explaining the latter's weak identifiability from dispersion data alone.

Validation on synthetic data demonstrates: (1) $G_0$ recovery within ±20% at 20 dB SNR, (2) proper characterization of the $G_\infty$–$\tau_\sigma$ anti-correlation, and (3) convergence diagnostics consistent with optimal MCMC performance (24.7% acceptance). Experimental design recommendations derived from the analysis—minimum 25 dB SNR, $\lambda/4$ receiver spacing, 300–1200 Hz excitation bandwidth—provide practical guidelines for phantom studies.

**Keywords:** shear wave elastography, inverse problem, Bayesian inference, MCMC, viscoelasticity, Zener model, numerical dispersion, parameter estimation

---

## Abstract Strengths

✓ **Clear problem statement** — two challenges identified upfront
✓ **Novel contribution** — calibration + Bayesian framework
✓ **Quantitative results** — specific numbers (30%, 3000:1, 20 dB, etc.)
✓ **Practical impact** — experimental guidelines for practitioners
✓ **Technical depth** — appropriate for T-UFFC audience

---

## Optional Additions (if journal allows longer abstracts)

If the journal permits ~300 words, consider adding:

**Additional sentence on methodology:**
> "Log-normal priors centered on calibrated values guide the inference, while Gaussian likelihoods with frequency-dependent weighting account for measurement uncertainty."

**Additional sentence on impact:**
> "This framework enables reliable tissue characterization essential for clinical differentiation of healthy versus pathological states, particularly in liver fibrosis staging where $G_0$ values span 2–20 kPa."

---

## Title Alternatives

If you want options:

1. **Current:** Bayesian Calibration of Viscoelastic Properties from Shear Wave Dispersion: Addressing Numerical Artifacts and Parameter Degeneracy

2. **Shorter:** Bayesian Inverse Estimation of Viscoelastic Parameters from Shear Wave Dispersion

3. **Emphasis on uncertainty:** Uncertainty Quantification in Shear Wave Elastography via Calibrated Bayesian Inference

4. **Emphasis on methodology:** MCMC-Based Calibration of Zener Model Parameters for Shear Wave Dispersion Analysis

---

## Next Steps for Paper

### Immediate (This Week)
- [ ] Finalize author list and affiliations
- [ ] Draft introduction (motivation + prior work)
- [ ] Write methods section (calibration + MCMC details)
- [ ] Prepare figures:
  - Fig 1: Forward model calibration
  - Fig 2: MCMC posterior distributions
  - Fig 3: 2D parameter misfit landscapes
  - Fig 4: Noise robustness results

### Next Week
- [ ] Results section (validation on synthetic data)
- [ ] Discussion (limitations, clinical relevance)
- [ ] Conclusion + future work
- [ ] References (aim for 30–40 citations)

### Submission Checklist
- [ ] Manuscript formatted per IEEE T-UFFC guidelines
- [ ] All figures at 300 DPI minimum
- [ ] Supplementary material (code repository link)
- [ ] Cover letter highlighting contributions
- [ ] Suggested reviewers (3–5 names)

---

Ready to move on to the introduction, or want to refine the abstract further?
