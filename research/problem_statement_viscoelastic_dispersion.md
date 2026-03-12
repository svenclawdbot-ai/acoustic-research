# Problem Statement
## Robust Viscoelastic Characterization via Shear Wave Dispersion with Limited Spatial Sampling

---

## 1. The Problem

Current shear wave elastography can measure tissue stiffness (elastic modulus) but **struggles to reliably separate elastic and viscous properties in realistic clinical scenarios**. This separation is critical because:

- **Cancer detection:** Malignant tumors are stiffer AND more viscous than benign masses
- **Liver fibrosis staging:** Viscosity may correlate with inflammation independent of fibrosis
- **Therapeutic monitoring:** Viscoelastic changes may precede structural changes

Existing methods require either:
- **Dense spatial sampling** (computationally expensive, limited field-of-view)
- **Homogeneous tissue assumptions** (invalid for layered organs)
- **Single-frequency measurements** (miss viscoelastic information)

---

## 2. The Gap

**No existing method robustly estimates both elastic modulus (G') and viscosity (η) in multi-layer, anisotropic tissues using limited spatial sampling (≤3 receiver points).**

Specific limitations of current approaches:

| Method | Limitation |
|--------|------------|
| Group velocity | Assumes non-dispersive medium (η ≈ 0) |
| Full-field inversion | Requires dense sampling, computationally intensive |
| Single-layer models | Fails in skin, eye, vascular walls |
| ARFI single-push | One frequency, no dispersion information |

---

## 3. The Approach

**Hypothesis:** By combining (1) reverberant shear wave excitation for broadband frequency content, (2) a multi-layer viscoelastic wave propagation model, and (3) sparse Bayesian inference for parameter estimation, we can accurately recover G' and η with as few as 2-3 spatial measurement points.

### Key Innovations:

1. **Reverberant Excitation**  
   Multiple simultaneous pushes create diffuse shear wave field → naturally multi-frequency, robust to boundaries

2. **Multi-Layer Kelvin-Voigt Model**  
   Extend Zhang et al. (2021) to reverberant fields: account for frequency-dependent penetration and interfacial coupling

3. **Sparse Bayesian Inversion**  
   Frame as probabilistic inverse problem: P(G', η | data) ∝ P(data | G', η) · P(G', η)  
   Prior: Physiological ranges (G' ∈ [1, 100] kPa, η ∈ [0.1, 10] Pa·s)

---

## 4. Specific Aims

### Aim 1: Theoretical Framework
Develop a forward model for reverberant shear wave propagation in multi-layer viscoelastic media.

**Deliverable:** Analytical/numerical model predicting dispersion curves given (G'₁, η₁, thickness₁, G'₂, η₂, ...)

### Aim 2: Inverse Algorithm
Implement sparse Bayesian inference to recover viscoelastic parameters from limited measurements.

**Deliverable:** Python implementation (MCMC or variational inference) validated on simulated data

### Aim 3: Experimental Validation
Build benchtop system (echomods + gelatin phantoms) to validate against ground-truth mechanical testing.

**Deliverable:** Phantom study comparing proposed method vs. rheometer measurements

### Aim 4: Research Paper
Synthesize theoretical framework, computational methods, and experimental results into a formal research paper suitable for submission to a peer-reviewed journal.

**Deliverable:** Complete research paper draft (IEEE Trans. UFFC or Physics in Medicine & Biology format)

---

## 5. Significance

**Clinical:** Enables point-of-care viscoelastic imaging with low-cost hardware (single transducer, minimal computing)

**Scientific:** First demonstration of sparse viscoelastic characterization in layered media

**Technical:** Bridges gap between high-end research systems (supersonic imaging) and clinical accessibility

---

## 6. Broader Impact

**Beyond medical imaging:** Same framework applicable to:
- **NDE:** Composite cure monitoring (viscosity tracks polymerization)
- **Food science:** Texture assessment (elasticity + viscosity = mouthfeel)
- **Materials:** Soft robotics characterization

---

## 7. Success Criteria

| Milestone | Metric |
|-----------|--------|
| Simulation | <10% error on G', <20% error on η for 2-layer phantoms |
| Phantom validation | Correlation R² > 0.9 with rheometer |
| Spatial sampling | Robust performance with ≤3 receiver points |
| Computational | Real-time capable (<1s per measurement) |
| **Research paper** | **Complete draft ready for peer review** |

---

## 8. Timeline (4-Week Sprint)

| Week | Focus | Deliverable |
|------|-------|-------------|
| **1** | Literature deep dive, theoretical framework derivation | Annotated bibliography, governing equations |
| **2** | Forward model implementation (2D FDTD with reverberant sources) | Working simulation code, dispersion curve validation |
| **3** | Inverse problem + Bayesian inference implementation | Python solver, parameter recovery validation |
| **4** | **Research paper writing** | **Complete draft manuscript (IEEE T-UFFC or PMB format)** |

---

## 9. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Model too complex | Start with 1-layer, then extend |
| Sparse data insufficient | Validate minimum sampling requirements via simulation |
| Phantom fabrication | Multiple recipes (gelatin, polyacrylamide, silicone) |
| Equipment delays | Simulation-first approach, hardware later |

---

## 10. Open Questions

1. What is the minimum frequency bandwidth required for robust G'/η separation?
2. How does anisotropy (fiber orientation) affect dispersion measurements?
3. Can we extend to 3+ layers (e.g., skin: epidermis/dermis/subcutis)?
4. What is the fundamental Cramér-Rao lower bound for sparse viscoelastic estimation?

---

*Problem Statement v1.1 — March 8, 2026*  
*Target: Journal submission (IEEE Trans. UFFC or Physics in Medicine & Biology)*
