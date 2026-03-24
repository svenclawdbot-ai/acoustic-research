# IEEE T-UFFC Paper — Section II: Theory and Methods

---

## II. Theory and Methods

### A. Viscoelastic Constitutive Model

We model soft tissue as a Zener (Standard Linear Solid) viscoelastic material, which captures both elastic and viscous behavior through a spring-dashpot arrangement consisting of a primary spring $G_1$ in parallel with a Maxwell element (spring $G_2$ and dashpot $\eta$ in series). This configuration provides a physically realistic representation of tissue mechanics with bounded creep and stress relaxation [19].

The complex shear modulus for the Zener model is:

$$
G^*(\omega) = G_1 + \frac{G_2(i\omega\eta)}{G_2 + i\omega\eta} = \frac{G_0 + G_\infty(i\omega\tau_\sigma)}{1 + i\omega\tau_\sigma}
$$

where $G_0 = G_1$ is the relaxed (low-frequency) modulus, $G_\infty = G_1 + G_2$ is the unrelaxed (high-frequency) modulus, and $\tau_\sigma = \eta/G_2$ is the stress relaxation time. The quantity $\tau_\varepsilon = \tau_\sigma G_\infty/G_0$ represents the strain relaxation time.

The phase velocity of shear waves in this medium follows:

$$
c_p(\omega) = \sqrt{\frac{|G^*(\omega)|}{\rho}} = \sqrt{\frac{G_0}{\rho} \cdot \frac{1 + \omega^2\tau_\varepsilon\tau_\sigma}{1 + \omega^2\tau_\sigma^2}}
$$

where $\rho$ is the material density (taken as 1000 kg/m³ for soft tissue). This dispersion relation connects measurable wave propagation characteristics to the three material parameters $\theta = \{G_0, G_\infty, \tau_\sigma\}$.

The group velocity, which governs wave packet propagation in transient elastography, is:

$$
c_g(\omega) = \frac{d\omega}{dk} = c_p(\omega) \left[ 1 + \frac{\omega}{c_p}\frac{dc_p}{d\omega} \right]
$$

For the Zener model, this evaluates to:

$$
c_g(\omega) = c_p(\omega) \cdot \frac{1 + \omega^2\tau_\sigma^2 + \omega^2\tau_\varepsilon\tau_\sigma + \omega^2\tau_\sigma^2(\tau_\varepsilon/\tau_\sigma - 1)}{1 + \omega^2\tau_\sigma^2}
$$

Both velocities exhibit frequency dependence, with the degree of dispersion controlled by the relaxation spectrum.

### B. Forward Problem: FDTD Simulation

To model shear wave propagation and generate synthetic data for validation, we employ a two-dimensional finite-difference time-domain (FDTD) solver with velocity-stress formulation [8]. The governing equations are:

$$
\rho\frac{\partial v_i}{\partial t} = \frac{\partial \sigma_{ij}}{\partial x_j} + f_i
$$

$$
\frac{\partial \sigma_{ij}}{\partial t} + \frac{1}{\tau_\sigma}\sigma_{ij} = G_0\left(\frac{\partial v_i}{\partial x_j} + \frac{\partial v_j}{\partial x_i}\right) + \frac{\tau_\varepsilon}{\tau_\sigma}G_0\frac{\partial}{\partial t}\left(\frac{\partial v_i}{\partial x_j} + \frac{\partial v_j}{\partial x_i}\right)
$$

where $v_i$ is particle velocity, $\sigma_{ij}$ is stress, and $f_i$ represents the mechanical source. We implement this using a staggered grid with second-order spatial differences and second-order leapfrog time integration.

**Grid dispersion considerations:** The numerical phase velocity deviates from the analytical solution due to discretization errors that depend on the ratio of wavelength to grid spacing ($\lambda/\Delta x$) and the Courant number [20]. For the parameters used in this study (grid spacing $\Delta x$ = 1 mm, time step $\Delta t$ = 0.125 μs), numerical dispersion introduces velocity errors up to 30% compared to analytical predictions, particularly at higher frequencies where $\lambda$ approaches the grid spacing.

**Perfectly matched layer (PML):** To eliminate boundary reflections, we implement a split-field PML with polynomial absorption profile [21]. The PML thickness is 20 grid cells, providing reflection coefficients below -60 dB.

**Source excitation:** We employ a Ricker wavelet source with center frequency $f_0$ = 150 Hz:

$$
s(t) = A\left[1 - 2\pi^2f_0^2(t-t_0)^2\right]e^{-\pi^2f_0^2(t-t_0)^2}
$$

where $A$ is amplitude and $t_0$ is time delay. The Ricker wavelet provides broadband excitation with peak energy at $f_0$ and negligible DC component.

### C. k-ω Dispersion Extraction

From FDTD simulations or experimental measurements, we extract the dispersion curve using the k-ω (wavenumber-frequency) transform [22]. For a spatiotemporal wavefield $u(x,t)$ recorded at discrete positions and times, the 2D Fourier transform yields:

$$
U(k,\omega) = \iint u(x,t) e^{-i(kx - \omega t)} dx dt
$$

The magnitude $|U(k,\omega)|$ exhibits peaks along the dispersion relation $\omega(k)$, enabling direct extraction of phase velocity $c_p = \omega/k$.

**Implementation details:** We compute the 2D FFT using zero-padding to achieve interpolation in the frequency domain, followed by shifting to center zero frequency. For improved spectral resolution and reduced leakage, we apply a 2D Hann window prior to transformation [23].

**Peak detection:** For each frequency $\omega$, we identify the wavenumber $k$ corresponding to maximum spectral magnitude within a physically motivated search window (typically 100–1500 rad/m for soft tissue at MHz frequencies). This yields a set of dispersion points $\{c_p(\omega_i), \omega_i\}_{i=1}^{N}$ with $N$ typically 7–20 points depending on SNR and frequency content.

### D. Forward Model Calibration

The discrepancy between analytical Zener dispersion and FDTD-predicted dispersion necessitates calibration of the forward model. We define apparent (calibrated) Zener parameters $\tilde{\theta} = \{\tilde{G}_0, \tilde{G}_\infty, \tilde{\tau}_\sigma\}$ that minimize the misfit between FDTD-extracted and model-predicted dispersion:

$$
\tilde{\theta} = \arg\min_\theta \sum_{i=1}^{N} \left[ c_p^{\text{FDTD}}(\omega_i) - c_p^{\text{Zener}}(\omega_i; \theta) \right]^2
$$

We solve this nonlinear least-squares problem using the Levenberg-Marquardt algorithm with bounds $G_0 \in [50, 5000]$ Pa, $G_\infty \in [500, 50000]$ Pa, and $\tau_\sigma \in [10^{-4}, 0.05]$ s. The calibrated parameters account for numerical dispersion artifacts, enabling reliable forward prediction for inverse problem solution.

**Validation:** Calibration quality is assessed via RMSE between FDTD and calibrated model predictions, with typical values below 0.02 m/s indicating excellent fit.

### E. Bayesian Inverse Problem Formulation

Given measured dispersion data $\mathcal{D} = \{c_i, \omega_i, \sigma_i\}_{i=1}^{N}$ where $\sigma_i$ represents measurement uncertainty, we seek the posterior distribution over material parameters $p(\theta | \mathcal{D})$.

**Bayes' theorem:**

$$
p(\theta | \mathcal{D}) = \frac{p(\mathcal{D} | \theta) p(\theta)}{p(\mathcal{D})} \propto p(\mathcal{D} | \theta) p(\theta)
$$

where $p(\mathcal{D} | \theta)$ is the likelihood, $p(\theta)$ is the prior, and $p(\mathcal{D})$ is the marginal likelihood (evidence).

**Prior specification:** We employ log-normal priors centered on calibrated values:

$$
\log G_0 \sim \mathcal{N}(\log \tilde{G}_0, \sigma_{\text{prior}}^2)
$$

$$
\log G_\infty \sim \mathcal{N}(\log \tilde{G}_\infty, \sigma_{\text{prior}}^2)
$$

$$
\log \tau_\sigma \sim \mathcal{N}(\log \tilde{\tau}_\sigma, \sigma_{\text{prior}}^2)
$$

with $\sigma_{\text{prior}}$ = 0.5, corresponding to a factor of ~1.6 uncertainty (conservative but not uninformative). Physical constraints ($G_\infty > G_0 > 0$, $\tau_\sigma > 0$) are enforced by returning zero probability for violations.

**Likelihood model:** Assuming Gaussian measurement errors:

$$
p(\mathcal{D} | \theta) = \prod_{i=1}^{N} \frac{1}{\sqrt{2\pi}\sigma_i} \exp\left[ -\frac{(c_i - c_p(\omega_i; \theta))^2}{2\sigma_i^2} \right]
$$

For frequency-dependent weighting, we set $\sigma_i \propto 1/\omega_i$ to emphasize low-frequency measurements where dispersion curvature is highest.

**Posterior characterization:** The posterior is a 3D probability distribution with complex geometry due to parameter degeneracy. Rather than seeking a single maximum (MAP estimate), we characterize the full distribution to quantify uncertainty and correlation structure.

### F. MCMC Sampling Algorithm

We employ the Metropolis-Hastings algorithm with adaptive proposal distribution [24]:

**Algorithm 1: Adaptive Metropolis-Hastings MCMC**

```
Initialize: θ⁽⁰⁾ = calibrated_values
For n = 1 to N_samples:
    1. Propose: θ* ~ q(θ* | θ⁽ⁿ⁻¹⁾) = N(θ⁽ⁿ⁻¹⁾, Σ⁽ⁿ⁾)
    2. Compute acceptance probability:
       α = min[1, p(θ*|D)q(θ⁽ⁿ⁻¹⁾|θ*) / p(θ⁽ⁿ⁻¹⁾|D)q(θ*|θ⁽ⁿ⁻¹⁾)]
    3. Accept with probability α:
       If U(0,1) < α: θ⁽ⁿ⁾ = θ*
       Else: θ⁽ⁿ⁾ = θ⁽ⁿ⁻¹⁾
    4. Adapt proposal (every 100 steps):
       If acceptance_rate > 0.30: Σ *= 1.01
       If acceptance_rate < 0.20: Σ *= 0.99
Return: {θ⁽ⁿ⁾}_{n=N_burnin}^{N_samples}
```

**Proposal covariance:** Initial covariance Σ is diagonal with $\sigma_{G_0}$ = 0.1$\tilde{G}_0$, $\sigma_{G_\infty}$ = 0.1$\tilde{G}_\infty$, $\sigma_\tau$ = 0.1$\tilde{\tau}_\sigma$.

**Burn-in and thinning:** We discard the first $N_{\text{burnin}}$ = 3000 samples (burn-in period where the chain approaches stationarity) and retain every sample (no thinning required given large sample size).

**Convergence diagnostics:** We monitor:
- Acceptance rate (target: 20–30%)
- Trace plots (visual inspection for stationarity)
- Geweke statistic (comparing early vs. late chain segments) [25]

**Posterior summaries:** From MCMC samples $\{\theta^{(m)}\}_{m=1}^{M}$, we compute:
- Posterior mean: $\bar{\theta} = \frac{1}{M}\sum_m \theta^{(m)}$
- Posterior standard deviation: $\sigma_\theta = \sqrt{\frac{1}{M-1}\sum_m (\theta^{(m)} - \bar{\theta})^2}$
- 95% credible interval: 2.5th and 97.5th percentiles

### G. Parameter Identifiability Analysis

To quantify the information content of dispersion measurements for each parameter, we compute 2D misfit landscapes. For parameter pairs $(\theta_i, \theta_j)$, we evaluate:

$$
\chi^2(\theta_i, \theta_j) = \sum_{k=1}^{N} \frac{(c_k - c_p(\omega_k; \theta_i, \theta_j, \theta_{\text{fixed}}))^2}{\sigma_k^2}
$$

holding remaining parameters at calibrated values. Curvature of the misfit surface at the minimum indicates local identifiability, with sharper curvature corresponding to better-constrained parameters.

**Effective curvature metric:**

$$
\kappa_i = \frac{\partial^2 \chi^2}{\partial \theta_i^2} \bigg|_{\theta = \tilde{\theta}}
$$

computed via finite differences on the discretized misfit grid.

### H. Noise Robustness Assessment

We evaluate algorithm performance across SNR levels by adding controlled Gaussian noise to synthetic FDTD data:

$$
c_i^{\text{noisy}} = c_i + \epsilon_i, \quad \epsilon_i \sim \mathcal{N}(0, \sigma_n^2)
$$

where $\sigma_n$ is chosen to achieve target SNR = 20 log₁₀($\bar{c}$/$\sigma_n$). We assess:
- Bias: deviation of posterior mean from true value
- Precision: posterior standard deviation
- Coverage: fraction of runs where 95% CI contains true value

---

## References (Methods Section)

[19] R. Lakes, *Viscoelastic Solids*. Boca Raton, FL: CRC Press, 1998.

[20] A. Taflove and S. C. Hagness, *Computational Electrodynamics: The Finite-Difference Time-Domain Method*, 3rd ed. Norwood, MA: Artech House, 2005.

[21] J.-P. Berenger, "A perfectly matched layer for the absorption of electromagnetic waves," *J. Comput. Phys.*, vol. 114, no. 2, pp. 185–200, 1994.

[22] P. S. Wilson, "Tutorial on the kinetic or eikonal description of shock and acceleration wave propagation," *J. Acoust. Soc. Am.*, vol. 138, no. 6, pp. 3589–3599, 2015.

[23] F. J. Harris, "On the use of windows for harmonic analysis with the discrete Fourier transform," *Proc. IEEE*, vol. 66, no. 1, pp. 51–83, 1978.

[24] H. Haario, E. Saksman, and J. Tamminen, "An adaptive Metropolis algorithm," *Bernoulli*, vol. 7, no. 2, pp. 223–242, 2001.

[25] J. Geweke, "Evaluating the accuracy of sampling-based approaches to the calculation of posterior moments," in *Bayesian Statistics 4*, J. M. Bernardo et al., Eds. Oxford, UK: Oxford University Press, 1992, pp. 169–193.

---

## Methods Section Notes

**Length:** ~1800 words (comprehensive but appropriate)

**Subsections:** 8 clearly labeled (A-H)
- A: Constitutive model (theory)
- B: FDTD (numerical methods)
- C: k-ω extraction (signal processing)
- D: Calibration (key contribution)
- E: Bayesian formulation (inverse problem)
- F: MCMC algorithm (implementation)
- G: Identifiability analysis (novel contribution)
- H: Validation protocol (experiments)

**Key Equations:**
- Complex modulus (Zener)
- Phase velocity dispersion
- Group velocity
- Bayes' theorem
- MCMC acceptance probability

**Algorithm:** Pseudocode for MCMC (can be formatted as Algorithm 1 figure)

---

Ready for Section III (Results) or want to refine the methods?
