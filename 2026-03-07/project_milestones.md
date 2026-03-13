# Project Milestones: Multi-Frequency Shear Wave Elastography

**Project:** Multi-Frequency Shear Wave Elastography for Viscoelastic Liver Characterization  
**Duration:** 4 Weeks (April 2026)  
**Start Date:** Week of March 31, 2026  
**Repository:** `acoustic-research`

---

## 📋 MILESTONE OVERVIEW

| Milestone | Target Date | Status | Deliverable |
|-----------|-------------|--------|-------------|
| M1: Literature Review | Week 1 (Apr 1-7) | ⬜ Not Started | Annotated bibliography + Problem statement |
| M2: Forward Model | Week 2 (Apr 8-14) | ⬜ Not Started | Working 1D/2D wave simulator |
| M3: Inverse Problem | Week 3 (Apr 15-21) | ⬜ Not Started | Inversion algorithm + validation |
| M4: Analysis & Writing | Week 4 (Apr 22-28) | ⬜ Not Started | Research report + Code repository |

---

## 🎯 MILESTONE 1: Literature Review & Problem Definition
**Dates:** April 1-7, 2026  
**Status:** ⬜ Not Started

### Checklist

#### Reading (see week1_reading_list.md)
- [ ] Ophir et al. (1991) — Elastography foundations
- [ ] Sarvazyan et al. (1998) — Shear wave elasticity
- [ ] Nightingale et al. (2002) — ARFI imaging
- [ ] Chen et al. (2009) — SDUV multi-frequency
- [ ] Parker (2014) — Viscoelastic models
- [ ] Barr et al. (2022) — Viscosity in liver disease
- [ ] Barry et al. (2021) — SWE limitations review
- [ ] Bercoff et al. (2004) — Supersonic imaging
- [ ] 2-3 ML/inverse problem papers

#### Deliverables
- [ ] Annotated bibliography (10-15 papers)
- [ ] One-page problem statement document
- [ ] Research question refined and documented
- [ ] GitHub repo initialized with README
- [ ] Weekly standup notes

#### Success Criteria
- Can explain Kelvin-Voigt model to a peer
- Can articulate the clinical gap (elastic vs viscoelastic)
- Can describe at least 2 inverse problem approaches

---

## 🧮 MILESTONE 2: Forward Model Implementation
**Dates:** April 8-14, 2026  
**Status:** ⬜ Not Started

### Checklist

#### 1D Wave Solver (Starter provided)
- [ ] Implement Kelvin-Voigt FDTD solver
- [ ] Validate against analytical solutions
- [ ] Add multiple source types (Ricker, tone burst, broadband)
- [ ] Implement absorbing boundary conditions
- [ ] Create visualization tools

#### 2D Extension (Stretch)
- [ ] Extend to 2D finite difference or spectral method
- [ ] Implement cylindrical/point source radiation
- [ ] Add heterogeneity (lesions, layers)

#### Viscoelastic Models
- [ ] Kelvin-Voigt (spring + dashpot parallel)
- [ ] Maxwell (series) — compare behavior
- [ ] (Stretch) Zener model (standard linear solid)
- [ ] (Stretch) Fractional derivative model

#### Dispersion Analysis
- [ ] Multi-frequency source generation
- [ ] Phase velocity extraction algorithm
- [ ] Generate synthetic dispersion curves
- [ ] Parameter sweep: G' vs G'' space

#### Deliverables
- [ ] Working 1D/2D simulator (Python/JAX)
- [ ] Gallery of example wave fields
- [ ] Synthetic dataset for inversion testing
- [ ] Unit tests for numerical accuracy
- [ ] Code documentation

#### Success Criteria
- Simulator reproduces expected physics (wave speed, attenuation)
- Dispersion curves match analytical KV model
- Can generate realistic-looking "liver" data

---

## 🔍 MILESTONE 3: Inverse Problem & Validation
**Dates:** April 15-21, 2026  
**Status:** ⬜ Not Started

### Checklist

#### Direct Inversion
- [ ] Implement analytical KV fit to dispersion curve
- [ ] Add uncertainty estimation (bootstrap or analytical)
- [ ] Test on noise-free synthetic data

#### Optimization-Based Inversion
- [ ] Least-squares objective function
- [ ] Add regularization (Tikhonov, physical bounds)
- [ ] Multiple optimizers (scipy.optimize, JAX)
- [ ] Compare convergence and accuracy

#### (Stretch) Physics-Informed Neural Network
- [ ] PINN architecture design
- [ ] Wave equation as constraint in loss function
- [ ] Training on synthetic data
- [ ] Comparison to traditional methods

#### Validation Experiments
- [ ] **Experiment 1:** Parameter recovery accuracy vs SNR
  - SNR levels: 40 dB, 30 dB, 20 dB, 10 dB
  - G' range: 2-30 kPa (healthy to cirrhotic)
  - G'' range: 0.5-15 kPa
- [ ] **Experiment 2:** Frequency range requirements
  - Test: 50-100 Hz, 50-200 Hz, 50-500 Hz
  - Measure: Inversion stability and accuracy
- [ ] **Experiment 3:** Classification performance
  - Simulate 1000 "livers" with known (G', G'')
  - Compare: Elastic-only vs Viscoelastic metrics
  - Metric: AUC-ROC for fibrosis staging

#### Deliverables
- [ ] Inversion algorithm codebase
- [ ] Validation experiment results (figures, tables)
- [ ] Performance comparison across methods
- [ ] Preliminary findings document

#### Success Criteria
- Recovers (G', G'') within 10% for SNR > 20 dB
- Demonstrates improved classification with viscoelastic data
- Understands limitations and failure modes

---

## 📝 MILESTONE 4: Analysis, Writing & Publication
**Dates:** April 22-28, 2026  
**Status:** ⬜ Not Started

### Checklist

#### Analysis
- [ ] Statistical analysis of all experiments
- [ ] Sensitivity analysis (which parameters matter most?)
- [ ] Robustness testing (edge cases, outliers)
- [ ] Comparison to clinical literature benchmarks

#### Writing
- [ ] **Abstract** (250 words)
- [ ] **Introduction** — Clinical motivation, gap, contribution
- [ ] **Theory** — Viscoelastic wave physics
- [ ] **Methods** — Forward model, inverse algorithms
- [ ] **Results** — Validation experiments, figures
- [ ] **Discussion** — Implications, limitations, future work
- [ ] **Conclusion** — Summary of findings

#### Code Publication
- [ ] Clean up codebase
- [ ] Add requirements.txt / environment.yml
- [ ] Write comprehensive README
- [ ] Add example notebooks (Jupyter)
- [ ] (Optional) Create demo script with visualization
- [ ] Tag v1.0 release

#### Presentation
- [ ] 10-15 slide deck
- [ ] Key figures and animations
- [ ] 5-minute "elevator pitch" version

#### Deliverables
- [ ] Research report (3000-5000 words)
- [ ] GitHub repository (public)
- [ ] Presentation slides
- [ ] (Optional) Blog post for Engineering-Learning

#### Success Criteria
- Report is self-contained and understandable
- Code is reproducible by others
- Results are scientifically rigorous
- Ready to present to peers or advisors

---

## 📊 WEEKLY STANDUP TEMPLATE

Use this format for weekly check-ins:

```markdown
## Week X Standup — [Date]

### What was accomplished?
- Item 1
- Item 2
- Item 3

### What's blocked?
- Issue 1 → Action item
- Issue 2 → Help needed?

### What's next week?
- Goal 1
- Goal 2

### Risks/Concerns?
- Scope creep? Technical difficulty? Time constraints?
```

---

## 🗂️ FILE ORGANIZATION (Theory & Modeling)

```
acoustic-research/
├── README.md
├── requirements.txt
├── .gitignore
│
├── docs/
│   ├── week1_reading_list.md
│   ├── annotated_bibliography.md
│   ├── problem_statement.md
│   ├── mathematical_framework.md     # Derivations, theory
│   └── research_report.md            # Final paper
│
├── src/
│   ├── __init__.py
│   ├── forward_model/
│   │   ├── __init__.py
│   │   ├── wave_solver_1d.py         # FDTD implementation
│   │   ├── wave_solver_2d.py         # (Stretch)
│   │   ├── viscoelastic_models.py    # KV, Maxwell, etc.
│   │   ├── sources.py                # Tone burst, Ricker
│   │   └── validation.py             # Analytical checks
│   │
│   ├── inverse/
│   │   ├── __init__.py
│   │   ├── direct_inversion.py       # Analytical solution
│   │   ├── optimization.py           # Least squares
│   │   ├── bayesian.py               # MCMC inference
│   │   └── pinn.py                   # (Stretch)
│   │
│   ├── dispersion/
│   │   ├── __init__.py
│   │   ├── extract_phase_velocity.py
│   │   ├── noise_models.py           # SNR control
│   │   └── synthetic_data.py         # Dataset generation
│   │
│   └── utils/
│       ├── __init__.py
│       └── visualization.py
│
├── experiments/
│   ├── experiment_01_snr_robustness.py
│   ├── experiment_02_frequency_requirements.py
│   ├── experiment_03_discrimination.py    # Clinical scenarios
│   ├── experiment_04_method_comparison.py
│   └── run_all.py
│
├── notebooks/
│   ├── 01_mathematical_framework.ipynb    # Theory derivation
│   ├── 02_forward_model.ipynb             # Wave simulations
│   ├── 03_synthetic_data.ipynb            # Data generation
│   ├── 04_inverse_problem.ipynb           # Inversion methods
│   └── 05_results_analysis.ipynb          # Figures, stats
│
├── data/
│   ├── synthetic/                    # Generated datasets (1000+ curves)
│   └── figures/                      # Output plots
│
├── tests/
│   ├── test_wave_solver.py           # Validation tests
│   ├── test_inversion.py
│   └── test_dispersion.py
│
└── presentations/
    ├── weekly_updates/
    └── final_presentation.pdf
```

---

## ⚠️ RISK REGISTER

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Wave solver numerically unstable | Medium | High | Start with 1D, validate against analytical solutions |
| Inverse problem ill-posed/diverges | Medium | High | Regularization, physical bounds, multiple initial guesses |
| Not enough time for 2D | High | Medium | 1D is sufficient for proof-of-concept |
| Literature review takes too long | Medium | Medium | Prioritize foundational papers, skim the rest |
| PINN implementation too complex | Medium | Medium | Make it a stretch goal, focus on optimization first |
| Noisy data makes inversion impossible | Low | High | Test on clean data first, add noise gradually |

---

## 📈 SUCCESS METRICS

### Minimum Viable Product
- [ ] Working 1D viscoelastic wave simulator
- [ ] Basic inversion algorithm (least-squares)
- [ ] Validation on synthetic data
- [ ] Written report documenting methods and results

### Target Success
- [ ] 2D wave simulator
- [ ] Multiple inversion methods compared
- [ ] Sensitivity analysis completed
- [ ] Results show clinical relevance
- [ ] Code published on GitHub with documentation

### Stretch Goals
- [ ] PINN implementation working
- [ ] Realistic liver geometry/heterogeneity
- [ ] Comparison to published clinical data
- [ ] Conference submission or preprint

---

## 🔗 RESOURCES & REFERENCES

### Key Equations

**Kelvin-Voigt Constitutive Relation:**
```
σ = G'ε + η(dε/dt)
```

**Shear Wave Equation:**
```
ρ(∂²u/∂t²) = G'(∂²u/∂x²) + η(∂³u/∂x²∂t)
```

**Dispersion Relation (KV model):**
```
c_s(ω) = √[ (G' + iωη) / ρ ]
|c_s| = √[ √(G'² + (ωη)²) / ρ ]
```

### Software Tools
- **Python:** NumPy, SciPy, Matplotlib, JAX
- **Jupyter:** Interactive development and visualization
- **Git/GitHub:** Version control and collaboration

### Computational Resources
- Local machine (sufficient for 1D/2D)
- (Optional) Google Colab for GPU acceleration if doing deep learning

---

*Milestone tracker created: March 7, 2026*  
*Last updated: March 7, 2026*  
*Next review: After Week 1 completion*
