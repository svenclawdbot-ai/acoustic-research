# Refreshed Research Plan: Theory & Modeling Focus
## Multi-Frequency Shear Wave Elastography for Viscoelastic Liver Characterization

**Project Type:** Computational Theory & Modeling Study  
**Duration:** 4 Weeks (April 2026)  
**Scope:** No experimental hardware — pure simulation, theory, and analysis  
**Last Updated:** March 7, 2026

---

## 🎯 REVISED OBJECTIVE

**Develop and validate a computational framework for multi-frequency shear wave elastography that can separate elastic (G') and viscous (G'') properties of viscoelastic tissue through physics-based modeling and synthetic data analysis.**

### Key Research Questions:

1. **Forward Problem:** Can we accurately model shear wave propagation in viscoelastic tissue using the Kelvin-Voigt model across clinical frequency ranges (50-500 Hz)?

2. **Inverse Problem:** How accurately can we recover G' and G'' from multi-frequency dispersion curves, and what are the fundamental limits imposed by measurement noise?

3. **Clinical Relevance:** Does adding viscous information (G'') improve discrimination of tissue states compared to elasticity-only (G') measurements?

4. **Methodological Comparison:** How do different inversion approaches (direct fitting, optimization, physics-informed neural networks) compare in accuracy and robustness?

---

## 📅 REVISED 4-WEEK TIMELINE

### **WEEK 1: Literature Deep Dive & Theoretical Framework**
**Dates:** April 1-7, 2026  
**Goal:** Master the physics and establish mathematical foundations

#### Deliverables:
- [ ] Complete reading of 5 essential papers (Sarvazyan, Nightingale, Chen, Parker, Barr)
- [ ] Derive full mathematical model from first principles
  - Wave equation in viscoelastic medium
  - Kelvin-Voigt constitutive relations
  - Dispersion relation derivation
- [ ] Document theoretical framework in LaTeX/Markdown
- [ ] Define parameter space (G', G'', frequency ranges)
- [ ] Create annotated bibliography with critical analysis

#### Mathematical Foundation to Establish:

**1. Governing Equation:**
```
ρ ∂²u/∂t² = G' ∇²u + η ∂(∇²u)/∂t

Where:
- ρ = tissue density (~1000 kg/m³)
- G' = storage modulus (elastic) — 2-50 kPa for liver
- η = viscosity — 0.5-20 Pa·s
- u = displacement field
```

**2. Dispersion Relation (Kelvin-Voigt):**
```
c_s(ω) = √[ √(G'² + (ωη)²) / ρ ]

Phase velocity depends on frequency through viscosity
```

**3. Complex Shear Modulus:**
```
G*(ω) = G' + iG'' = G' + iωη
|G*| = √(G'² + (ωη)²)
```

**4. Inverse Problem Formulation:**
```
Given: {c_s(ω₁), c_s(ω₂), ..., c_s(ωₙ)}
Find: {G', η} that minimize ||c_model(ω; G', η) - c_measured(ω)||²
```

#### Success Criteria:
- Can derive wave equation from KV constitutive relation
- Can explain dispersion physics intuitively
- Parameter ranges justified by literature
- Code skeleton for Week 2 ready

---

### **WEEK 2: Forward Model Implementation & Validation**
**Dates:** April 8-14, 2026  
**Goal:** Build robust simulation that generates realistic synthetic data

#### Deliverables:
- [ ] **1D Wave Propagation Solver**
  - FDTD implementation of viscoelastic wave equation
  - Multiple source types (tone burst, Ricker, broadband)
  - Absorbing boundary conditions
  - Validation against analytical solutions
  
- [ ] **2D Wave Propagation Solver (Stretch)**
  - Cylindrical/point source radiation pattern
  - Spatial heterogeneity capability (lesions, layers)
  - Visualization of wave fields
  
- [ ] **Parameter Sweep Framework**
  - Systematic variation of G' (2-50 kPa)
  - Systematic variation of η (0.5-20 Pa·s)
  - Frequency sampling: 50, 100, 150, 200, 300, 400, 500 Hz
  
- [ ] **Synthetic Dataset Generation**
  - 1000+ dispersion curves with ground truth (G', η)
  - Add controlled noise (SNR: ∞, 40, 30, 20, 10 dB)
  - Include realistic artifacts (reflections, attenuation)

#### Code Architecture:
```python
src/
├── forward_model/
│   ├── wave_solver_1d.py      # Core FDTD implementation
│   ├── wave_solver_2d.py      # 2D extension
│   ├── sources.py             # Tone burst, Ricker, etc.
│   ├── boundaries.py          # ABC implementations
│   └── validation.py          # Analytical comparisons
├── dispersion/
│   ├── extract_phase_velocity.py
│   ├── noise_models.py
│   └── synthetic_data.py      # Dataset generation
└── visualization/
    ├── wave_plots.py
    └── dispersion_plots.py
```

#### Validation Experiments:

**Test 1: Analytical Verification**
- Purely elastic case (η = 0): c_s should be constant vs frequency
- Compare numerical c_s to analytical √(G'/ρ)
- Tolerance: <1% error

**Test 2: Dispersion Check**
- Viscoelastic case: c_s should increase with frequency
- Compare to analytical KV dispersion relation
- Verify at multiple (G', η) combinations

**Test 3: Energy Conservation**
- Total energy (kinetic + potential) should decay correctly
- Viscous dissipation rate matches theory

#### Success Criteria:
- 1D solver validated against analytical solutions
- Can generate realistic-looking dispersion curves
- Synthetic dataset covers clinical parameter range
- Code documented and tested

---

### **WEEK 3: Inverse Problem & Method Comparison**
**Dates:** April 15-21, 2026  
**Goal:** Implement and compare multiple inversion approaches

#### Deliverables:

**[ ] Method 1: Direct Analytical Inversion**
```python
# For KV model, we can directly solve:
# c_s²(ω) = √(G'² + (ωη)²) / ρ

# Two frequencies → two equations → solve for G', η
# This is fast but sensitive to noise
```
- Implement closed-form solution
- Test on noise-free synthetic data
- Characterize noise sensitivity

**[ ] Method 2: Optimization-Based Inversion**
```python
# Minimize: Σᵢ [c_model(ωᵢ) - c_measured(ωᵢ)]²
# Subject to: G' > 0, η > 0
# With regularization: λ[(G'-G'₀)² + (η-η₀)²]
```
- Implement least-squares with bounds
- Add Tikhonov regularization
- Multiple initializations to avoid local minima
- Compare optimizers: L-BFGS-B, Nelder-Mead, differential evolution

**[ ] Method 3: Bayesian Inference**
```python
# Posterior: p(G', η | data) ∝ p(data | G', η) × p(G', η)
# Likelihood: Gaussian noise model
# Prior: Physically-informed ranges
```
- MCMC sampling (Metropolis-Hastings or NUTS)
- Posterior distributions → uncertainty quantification
- Credible intervals for recovered parameters

**[ ] Method 4: Physics-Informed Neural Network (Stretch)**
```python
# Neural network approximates solution
# Physics loss enforces wave equation
# Learn G' and η as trainable parameters
```
- JAX/PyTorch implementation
- Compare data efficiency vs traditional methods
- Uncertainty via ensemble or Bayesian layers

#### Comprehensive Evaluation Framework:

| Metric | Description |
|--------|-------------|
| **Accuracy** | Mean error: ‖(G'_est, η_est) - (G'_true, η_true)‖ |
| **Precision** | Standard deviation across multiple noise realizations |
| **Robustness** | Performance vs SNR (40 dB → 10 dB) |
| **Resolution** | Minimum distinguishable ΔG', Δη |
| **Uncertainty Calibration** | Do credible intervals contain true values at stated rate? |

#### Experimental Matrix:

**Experiment 1: Baseline Performance**
- 100 synthetic samples at each (G', η) combination
- SNR = 30 dB (realistic clinical level)
- Compare all 4 methods

**Experiment 2: Noise Robustness**
- Fix (G', η) = (10 kPa, 5 Pa·s)
- Vary SNR: ∞, 40, 30, 20, 15, 10 dB
- Characterize breakdown point for each method

**Experiment 3: Frequency Requirements**
- How many frequencies needed for stable inversion?
- Test: 2, 3, 5, 7 frequencies
- Optimal frequency spacing?

**Experiment 4: Clinical Discrimination**
- Simulate 4 tissue states:
  - Healthy: G'=4 kPa, η=2 Pa·s
  - Mild fibrosis: G'=8 kPa, η=3 Pa·s
  - Inflammation: G'=6 kPa, η=8 Pa·s
  - Severe fibrosis: G'=20 kPa, η=5 Pa·s
- Can we distinguish inflammation from fibrosis using (G', η) vs G' alone?

#### Success Criteria:
- At least 2 robust inversion methods working
- <10% error on (G', η) recovery at SNR ≥ 20 dB
- Quantified uncertainty bounds
- Clear comparison of method trade-offs

---

### **WEEK 4: Analysis, Synthesis & Documentation**
**Dates:** April 22-28, 2026  
**Goal:** Synthesize findings, write research report, publish code

#### Deliverables:

**[ ] Statistical Analysis**
- Aggregate results from all experiments
- Performance summaries with confidence intervals
- Sensitivity analyses (which parameters matter most?)
- Identification of method strengths/weaknesses

**[ ] Clinical Relevance Analysis**
- Quantify improvement from adding viscosity
- ROC curves for classification tasks
- Threshold analysis (when is multi-frequency worth the complexity?)

**[ ] Research Report (3000-5000 words)**

**Structure:**
1. **Abstract** (250 words)
   - Background, methods, key findings, implications
   
2. **Introduction** (500-700 words)
   - Clinical motivation (liver fibrosis staging)
   - Limitations of single-frequency elastography
   - Research objectives and contributions
   
3. **Theory** (800-1000 words)
   - Viscoelastic tissue models
   - Shear wave physics
   - Inverse problem formulation
   
4. **Methods** (800-1000 words)
   - Forward model implementation
   - Inversion algorithms (2-3 methods)
   - Validation approach
   - Synthetic data generation
   
5. **Results** (1000-1200 words)
   - Forward model validation
   - Inversion accuracy across methods
   - Noise robustness
   - Clinical discrimination performance
   - Figures: dispersion curves, error plots, ROC curves
   
6. **Discussion** (600-800 words)
   - Interpretation of findings
   - Comparison to prior work (Chen 2009, Barr 2022)
   - Limitations of modeling approach
   - Implications for clinical translation
   
7. **Conclusion** (200-300 words)
   - Summary of contributions
   - Practical recommendations
   - Future directions

**[ ] Code Repository**
- Clean, documented codebase
- README with installation and usage
- Jupyter notebooks for reproduction
- Requirements.txt / environment.yml
- Example outputs

**[ ] Presentation (Optional)**
- 10-15 slides for sharing findings
- Key figures and takeaways
- 5-minute summary version

#### Success Criteria:
- Report is self-contained and scientifically rigorous
- Results are reproducible from provided code
- Clear conclusions with practical implications
- Ready for peer review or preprint

---

## 📊 EXPECTED OUTCOMES

### Minimum Viable (Must Achieve):
- [ ] Working 1D viscoelastic wave solver
- [ ] 2 inversion methods (direct + optimization)
- [ ] Validation on synthetic data (100+ samples)
- [ ] Written report with clear findings

### Target Success (Aim For):
- [ ] 2D wave solver capability
- [ ] 3-4 inversion methods compared
- [ ] Comprehensive noise analysis
- [ ] Clinical relevance demonstrated
- [ ] Published code with documentation

### Stretch Goals (If Time Permits):
- [ ] Physics-informed neural network implementation
- [ ] Uncertainty quantification with credible intervals
- [ ] Extension to anisotropic or heterogeneous media
- [ ] Preprint on arXiv or technical report

---

## 🧪 SYNTHETIC DATA SPECIFICATIONS

Since we're not doing experiments, the synthetic data must be realistic:

### Parameter Ranges (Liver-Realistic):

| Parameter | Range | Clinical Context |
|-----------|-------|------------------|
| **G' (elastic)** | 2-50 kPa | 4-6 = healthy, 8-15 = fibrosis, 20+ = cirrhosis |
| **η (viscosity)** | 0.5-20 Pa·s | 2-5 = normal, 8-15 = inflammation |
| **Density ρ** | 1000-1050 kg/m³ | Fixed at 1000 for simplicity |
| **Frequencies** | 50-500 Hz | Clinical SWE range |

### Noise Model:
```python
def add_noise(c_s_clean, snr_db):
    """Add realistic measurement noise to phase velocity"""
    signal_power = np.mean(c_s_clean**2)
    noise_power = signal_power / (10**(snr_db/10))
    noise = np.random.normal(0, np.sqrt(noise_power), size=c_s_clean.shape)
    return c_s_clean + noise
```

### Realistic Artifacts (Advanced):
- **Reflections:** Shear waves reflecting from boundaries
- **Attenuation:** Amplitude decay with distance
- **Dispersion errors:** Limited frequency resolution

---

## 📚 KEY REFERENCES (Prioritized)

### Essential (Week 1):
1. **Sarvazyan (1998)** — Shear wave elasticity foundation
2. **Nightingale (2002)** — ARFI imaging
3. **Chen (2009)** — SDUV multi-frequency
4. **Parker (2014)** — Viscoelastic models
5. **Barr (2022)** — Clinical viscosity relevance

### Supporting (Week 2-3):
6. **Manduca (2001)** — Inverse problem formalization
7. **Zhang (2008)** — Multi-frequency KV validation
8. **Raissi (2018)** — PINNs for wave problems
9. **Barry (2021)** — SWE limitations and artifacts
10. **Bercoff (2004)** — Ultrafast imaging (context)

---

## 💻 SOFTWARE STACK

| Component | Tool | Purpose |
|-----------|------|---------|
| **Language** | Python 3.10+ | Main development |
| **Numerics** | NumPy, SciPy | Array operations, optimization |
| **Differentiation** | JAX | Gradients for PINN (optional) |
| **Deep Learning** | PyTorch | PINN implementation (optional) |
| **Visualization** | Matplotlib, Plotly | Figures, interactive plots |
| **Documentation** | Jupyter | Exploratory analysis |
| **Version Control** | Git + GitHub | Code management |

---

## 🎯 DECISIONS MADE (Scope Reduction)

| Original Plan | Revised Plan | Rationale |
|--------------|--------------|-----------|
| Hardware + experiments | Pure simulation | 4 weeks insufficient for both |
| Build benchtop setup | Synthetic data only | Theory focus, reproducible |
| Phantom experiments | Parameter sweeps | Faster iteration, controlled conditions |
| 2D/3D imaging | 1D (+ 2D stretch) | Manageable complexity |
| Real-time processing | Offline analysis | Focus on accuracy over speed |
| Clinical validation | Discrimination analysis | Synthetic clinical scenarios |

---

## 📈 SUCCESS METRICS

### Quantitative:
- **Accuracy:** <10% error on (G', η) recovery at SNR ≥ 20 dB
- **Precision:** Coefficient of variation <15% across noise realizations
- **Discrimination:** AUC-ROC improvement ≥0.05 with (G', η) vs G' alone
- **Reproducibility:** Full replication from code in <30 minutes

### Qualitative:
- Clear physical interpretation of results
- Honest discussion of limitations
- Actionable recommendations for future work
- Professional-quality documentation

---

## 🚀 IMMEDIATE NEXT STEPS

### This Week (Before April):
1. **Set up GitHub repo** `acoustic-research`
2. **Create Python environment** (conda with NumPy/SciPy/Matplotlib)
3. **Download essential papers** (Sarvazyan, Chen, Parker)
4. **Sketch wave equation derivation** — verify your understanding

### Week 1 Kickoff:
1. Derive full mathematical framework
2. Validate derivations against literature
3. Document in LaTeX/Markdown
4. Prepare Week 2 code skeleton

---

*Plan refreshed: March 7, 2026*  
*Scope: Theory & Modeling Only*  
*Duration: 4 Weeks | Target: Research Report + Validated Code*
