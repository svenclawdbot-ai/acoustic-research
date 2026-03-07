# Quick Reference: Refreshed Research Plan
## Multi-Frequency Shear Wave Elastography — Theory & Modeling Focus

**Date:** March 7, 2026  
**Scope:** Computational study only — no hardware/experiments  
**Duration:** 4 Weeks

---

## 🎯 REVISED OBJECTIVE

Develop and validate a **computational framework** for multi-frequency shear wave elastography that separates elastic (G') and viscous (G'') properties through physics-based modeling and synthetic data analysis.

**No experimental hardware.** Pure theory, simulation, and analysis.

---

## 📅 4-WEEK TIMELINE (Refreshed)

### **WEEK 1: Theory & Mathematical Framework**
- Read 5 essential papers (Sarvazyan, Nightingale, Chen, Parker, Barr)
- Derive wave equation from Kelvin-Voigt constitutive relations
- Establish dispersion relation: c_s(ω) = √[√(G'² + (ωη)²)/ρ]
- Document mathematical framework
- Define parameter space (G': 2-50 kPa, η: 0.5-20 Pa·s)

**Deliverable:** Theoretical foundation document

---

### **WEEK 2: Forward Model & Synthetic Data**
- Implement 1D FDTD wave solver (2D = stretch)
- Validate against analytical solutions
- Generate 1000+ synthetic dispersion curves
- Add controlled noise (SNR: 40, 30, 20, 10 dB)
- Parameter sweep across clinical ranges

**Deliverable:** Working simulator + synthetic dataset

---

### **WEEK 3: Inverse Problem & Method Comparison**
- **Method 1:** Direct analytical inversion
- **Method 2:** Optimization-based (least squares + regularization)
- **Method 3:** Bayesian inference (MCMC, uncertainty quantification)
- **Method 4:** PINN (stretch goal)

**Experiments:**
1. Accuracy vs SNR
2. Frequency requirements (2, 3, 5, 7 frequencies)
3. Clinical discrimination (can we separate inflammation from fibrosis?)

**Deliverable:** 2-3 working inversion methods + performance comparison

---

### **WEEK 4: Analysis & Writing**
- Statistical analysis of all experiments
- Research report (3000-5000 words)
- Code documentation + GitHub repository
- Key findings:
  - How accurately can we recover (G', η)?
  - Does adding viscosity improve clinical discrimination?
  - Which inversion method is best?

**Deliverable:** Research report + publishable code

---

## 🧪 SYNTHETIC DATA STRATEGY (Replacing Experiments)

### Why Synthetic?
- ✅ Controlled conditions (known ground truth)
- ✅ Fast iteration (no setup time)
- ✅ Reproducible (others can replicate exactly)
- ✅ Covers full parameter space
- ✅ Systematic noise analysis

### Dataset Specs:
- **1000+ dispersion curves** with known (G', η)
- **Frequency range:** 50-500 Hz (clinical SWE range)
- **Parameter coverage:**
  - G': 2, 4, 6, 8, 10, 15, 20, 30, 50 kPa
  - η: 0.5, 1, 2, 5, 8, 10, 15, 20 Pa·s
- **Noise levels:** SNR = ∞, 40, 30, 20, 15, 10 dB
- **Clinical scenarios:** 4 tissue states for discrimination testing

---

## 🔬 KEY RESEARCH QUESTIONS

1. **Forward Model:** Can we accurately model shear wave dispersion in KV viscoelastic media?

2. **Inverse Accuracy:** How well can we recover G' and η from multi-frequency data?

3. **Noise Robustness:** At what SNR does inversion break down?

4. **Clinical Value:** Does adding viscosity (G'') improve discrimination vs elasticity (G') alone?

5. **Method Comparison:** Direct, optimization, Bayesian, PINN — which is best?

---

## 📊 SUCCESS METRICS

| Metric | Target |
|--------|--------|
| **Inversion Accuracy** | <10% error on (G', η) at SNR ≥ 20 dB |
| **Precision** | Coefficient of variation <15% |
| **Discrimination** | AUC improvement ≥0.05 with (G', η) vs G' |
| **Reproducibility** | Full replication in <30 minutes from code |

---

## 💻 SOFTWARE STACK

- **Python 3.10+**
- **NumPy/SciPy** — numerics, optimization
- **Matplotlib/Plotly** — visualization
- **JAX** (optional) — gradients for PINN
- **PyMC** or **NumPyro** (optional) — Bayesian inference

---

## 📚 ESSENTIAL PAPERS (5 Only)

1. **Sarvazyan (1998)** — Shear wave foundation, G = ρc_s²
2. **Nightingale (2002)** — ARFI imaging, radiation force
3. **Chen (2009)** — SDUV multi-frequency, dispersion
4. **Parker (2014)** — Viscoelastic models (KV is sufficient)
5. **Barr (2022)** — Clinical relevance of viscosity

---

## ✅ WHAT CHANGED (Scope Reduction)

| Original | Revised | Rationale |
|----------|---------|-----------|
| Hardware + experiments | Synthetic data only | Time constraint |
| Build benchtop setup | Skip entirely | Focus on theory |
| Phantom experiments | Parameter sweeps | Faster, controlled |
| Real-time processing | Offline analysis | Accuracy over speed |
| 2D/3D imaging | 1D primary, 2D stretch | Manageable complexity |

---

## 🚀 IMMEDIATE NEXT STEPS

### This Week:
1. Set up GitHub repo `acoustic-research`
2. Create Python environment (conda)
3. Download 5 essential papers
4. Start deriving wave equation

### Week 1 Kickoff:
1. Complete mathematical framework
2. Document in LaTeX/Markdown
3. Prepare code skeleton for Week 2

---

*Plan refreshed: March 7, 2026*  
*Focus: Theory & Modeling | No Hardware*  
*Output: Research Report + Validated Simulation Code*
