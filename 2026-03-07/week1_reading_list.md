# Week 1 Reading List: Viscoelastic Shear Wave Elastography

**Research Project:** Multi-Frequency Shear Wave Elastography for Viscoelastic Liver Characterization  
**Week Focus:** Literature Review & Problem Definition  
**Target:** 10-15 papers, grouped by topic

---

## 📚 FOUNDATIONAL PAPERS (Read First)

### 1. The Original Elastography Paper
**Title:** Elastography: A Quantitative Method for Imaging the Elasticity of Biological Tissues  
**Authors:** Ophir J, Céspedes I, Ponnekanti H, Yazdi Y, Li X  
**Journal:** Ultrasonic Imaging, 1991  
**DOI:** 10.1016/0161-7346(91)90017-W  
**Why Read:** THE paper that started the field. Understand the fundamental concept of strain imaging.  
**Key Takeaway:** Tissue stiffness can be imaged by tracking displacement under compression.

---

### 2. Shear Wave Elasticity Imaging Foundation
**Title:** Shear Wave Elasticity Imaging: A New Ultrasonic Technology of Medical Diagnostics  
**Authors:** Sarvazyan AP, Rudenko OV, Swanson SD, Fowlkes JB, Emelianov SY  
**Journal:** Ultrasound in Medicine & Biology, 1998  
**DOI:** 10.1016/S0301-5629(98)00051-5  
**Why Read:** Introduced the concept of using shear waves (not just compression) for elasticity mapping.  
**Key Takeaway:** Shear modulus G = ρc_s² connects wave speed to tissue stiffness.

---

### 3. Acoustic Radiation Force Impulse (ARFI) Imaging
**Title:** Acoustic Radiation Force Impulse Imaging: In Vivo Demonstration of Clinical Feasibility  
**Authors:** Nightingale K, Soo MS, Nightingale R, Trahey G  
**Journal:** Ultrasound in Medicine & Biology, 2002  
**DOI:** 10.1016/S0301-5629(02)00456-4  
**Why Read:** The breakthrough that made shear wave imaging practical—using ultrasound itself to generate shear waves.  
**Key Takeaway:** Radiation force from focused ultrasound can displace tissue and generate shear waves without external vibration.

---

## 🔬 VISCOELASTIC TISSUE MODELS

### 4. Viscoelastic Characterization of Soft Tissue
**Title:** Shearwave Dispersion Ultrasound Vibrometry (SDUV) for Measuring Tissue Elasticity and Viscosity  
**Authors:** Chen S, Urban MW, Pislaru C, et al.  
**Journal:** IEEE Trans Ultrason Ferroelectr Freq Control, 2009  
**DOI:** 10.1109/TUFFC.2009.1066  
**Why Read:** The seminal paper on multi-frequency shear wave measurements for separating elastic and viscous properties.  
**Key Takeaway:** Measuring shear wave speed at multiple frequencies allows solving for both G' and G''.

---

### 5. Simplified Viscoelastic Models for Tissue
**Title:** The Inconvenient Nature of Soft Tissue Viscosity: Why It Matters and What to Do About It  
**Authors:** Parker KJ  
**Journal:** Ultrasound in Medicine & Biology, 2014  
**DOI:** 10.1016/j.ultrasmedbio.2014.05.021  
**Why Read:** A practical, accessible guide to viscoelastic models in tissue. Parker cuts through complexity.  
**Key Takeaway:** Simple Kelvin-Voigt model is often sufficient; fractional models add complexity without proportional benefit.

---

### 6. Kelvin-Voigt vs. Other Models
**Title:** Viscoelasticity Imaging Using Ultrasound Shear Wave Speed at Multiple Frequencies  
**Authors:** Zhang M, Castaneda B, Christensen J, et al.  
**Journal:** IEEE Trans Ultrason Ferroelectr Freq Control, 2008  
**DOI:** 10.1109/TUFFC.2008.702  
**Why Read:** Compares different viscoelastic models head-to-head in experimental data.  
**Key Takeaway:** KV model fits well for soft tissues over clinical frequency ranges (50-500 Hz).

---

## 🏥 CLINICAL APPLICATIONS: LIVER

### 7. Vibration-Controlled Transient Elastography (VCTE)
**Title:** Liver Stiffness Measurement by Vibration Controlled Transient Elastography: A Standardized Technique  
**Authors:** Sandrin L, Fourquet B, Hasquenoph JM, et al.  
**Journal:** European Radiology, 2003  
**DOI:** 10.1007/s00330-003-1823-9  
**Why Read:** The FibroScan paper—how transient elastography became clinical reality.  
**Key Takeaway:** Single-frequency (50 Hz) measurement can stage fibrosis, but has limitations.

---

### 8. 2D Shear Wave Elastography (SWE) vs FibroScan
**Title:** Two-Dimensional Shear Wave Elastography: A New Method for Non-Invasive Assessment of Liver Fibrosis  
**Authors:** Bavu E, Gennisson JL, Couade M, et al.  
**Journal:** Ultrasound in Medicine & Biology, 2011  
**DOI:** 10.1016/j.ultrasmedbio.2011.07.002  
**Why Read:** Compares 2D SWE (Supersonic Imagine) to VCTE. Shows advantages of imaging vs single-point measurement.  
**Key Takeaway:** 2D SWE allows ROI selection under B-mode guidance—better for heterogeneous liver.

---

### 9. Viscosity in Liver Disease
**Title:** Shear Wave Viscosity: A Quantitative Biomarker for Liver Inflammation and Fibrosis  
**Authors:** Barr RG, Ferraioli G, Palmeri ML, et al.  
**Journal:** Radiology, 2022  
**DOI:** 10.1148/radiol.210475  
**Why Read:** Recent clinical evidence that viscosity (not just elasticity) correlates with inflammation.  
**Key Takeaway:** Adding viscosity improves discrimination between fibrosis and inflammation.

---

### 10. Limitations of Current Clinical Systems
**Title:** A Review of Physical and Engineering Factors Potentially Affecting Shear Wave Elastography  
**Authors:** Barry C, Mills P, Kontopoulou T, et al.  
**Journal:** Journal of Medical Ultrasonics, 2021  
**DOI:** 10.1007/s10396-021-01127-w  
**Why Read:** Comprehensive review of artifacts, technical limitations, and optimization strategies.  
**Key Takeaway:** Systems differ in push frequency, tracking methods, and inversion algorithms—standardization is poor.

---

## 🧮 INVERSE PROBLEMS & COMPUTATIONAL METHODS

### 11. Inverse Problem in Elastography
**Title:** Inverse Problem in Magnetic Resonance Elastography: The Inaugural Model  
**Authors:** Manduca A, Oliphant TE, Dresner MA, et al.  
**Journal:** Medical Physics, 2001  
**DOI:** 10.1118/1.1388012  
**Why Read:** MRE and SWE share the same inverse problem. This paper formalizes the direct inversion approach.  
**Key Takeaway:** Local frequency estimation (LFE) and algebraic inversion are common approaches.

---

### 12. Physics-Informed Neural Networks for Wave Problems
**Title:** Physics-Informed Neural Networks for Solving Forward and Inverse Problems in Elastic Wave Propagation  
**Authors:** Raissi M, Perdikaris P, Karniadakis GE  
**Journal:** arXiv preprint, 2018  
**Link:** https://arxiv.org/abs/1711.10561  
**Why Read:** The foundational PINN paper applied to wave equations.  
**Key Takeaway:** Neural networks can encode physical constraints (wave equation) as loss terms.

---

### 13. Deep Learning for Elastography
**Title:** Deep Learning in Ultrasound Elastography: A Review  
**Authors:** Wang C, et al.  
**Journal:** IEEE Transactions on Ultrasonics, Ferroelectrics, and Frequency Control, 2021  
**DOI:** 10.1109/TUFFC.2021.3074567  
**Why Read:** Survey of ML applications in elastography—classification, inversion, quality assessment.  
**Key Takeaway:** End-to-end learning can bypass physics but needs large datasets; physics-guided approaches more sample-efficient.

---

## 📊 EXPERIMENTAL TECHNIQUES

### 14. Supersonic Shear Imaging
**Title:** Supersonic Shear Imaging: A New Technique for Soft Tissue Elasticity Mapping  
**Authors:** Bercoff J, Tanter M, Fink M  
**Journal:** IEEE Trans Ultrason Ferroelectr Freq Control, 2004  
**DOI:** 10.1109/TUFFC.2004.1295422  
**Why Read:** The breakthrough for real-time 2D elastography—successive push pulses create "Mach cone" of shear waves.  
**Key Takeaway:** Ultrafast imaging (5000+ fps) tracks shear wave propagation in real time.

---

### 15. Multi-Frequency Acquisition Strategies
**Title:** Broadband Shear Wave Elastography: A Technique for Measuring Viscoelasticity of Soft Tissues  
**Authors:** Klatt D, Hamhaber U, Asbach P, Braun J, Sack I  
**Journal:** IEEE Trans Ultrason Ferroelectr Freq Control, 2007  
**DOI:** 10.1109/TUFFC.2007.329  
**Why Read:** MRE approach to multi-frequency imaging—can translate to ultrasound.  
**Key Takeaway:** Driving at multiple frequencies simultaneously can speed up acquisition.

---

## 🎯 OPTIONAL: ADVANCED TOPICS

### Fractional Viscoelasticity
**Title:** Fractional Calculus Model of Viscoelasticity in Soft Tissues  
**Authors:** Caputo M, Fabrizio M  
**Journal:** Progress in Fractional Differentiation and Applications, 2015  
**Why Read:** If you want to explore beyond KV model—fractional derivatives capture memory effects.  
**Key Takeaway:** More complex, but better for broadband characterization.

### Anisotropy in Liver
**Title:** Anisotropic Shear Wave Elasticity of the Liver: Measurements and Modeling  
**Authors:** Ormachea J, et al.  
**Journal:** Ultrasound in Medicine & Biology, 2019  
**Why Read:** Liver is not isotropic—Glisson's capsule and vascular structures create directionality.  
**Key Takeaway:** Shear wave speed depends on propagation direction relative to liver architecture.

---

## 📝 READING SCHEDULE

| Day | Papers | Focus |
|-----|--------|-------|
| **Saturday** | 1-3 (Ophir, Sarvazyan, Nightingale) | History & fundamentals |
| **Sunday** | 4-6 (Chen, Parker, Zhang) | Viscoelastic models |
| **Monday** | 7-9 (Sandrin, Bavu, Barr) | Clinical liver applications |
| **Tuesday** | 10 (Barry) | Limitations & artifacts |
| **Wednesday** | 11-13 (Manduca, Raissi, Wang) | Inverse problems & ML |
| **Thursday** | 14-15 (Bercoff, Klatt) | Experimental techniques |
| **Friday** | Review & synthesis | Notes, questions, gaps |

---

## 🔍 KEY QUESTIONS TO ANSWER WHILE READING

1. **What viscoelastic model best describes liver tissue?** KV? Maxwell? Zener? Fractional?

2. **What frequency range is optimal for liver imaging?** 30-100 Hz? 50-300 Hz? Trade-offs?

3. **Why do current clinical systems report only elasticity?** Technical limitation or sufficient for diagnosis?

4. **What inverse problem approach is most robust to noise?** Direct inversion? Optimization? Learning-based?

5. **How much does viscosity vary between healthy and diseased liver?** Is it clinically useful?

6. **What artifacts plague multi-frequency measurements?** Reflections, attenuation, noise amplification?

---

## 📥 DOWNLOAD LINKS

Most papers available via:
- **Google Scholar** (scholar.google.com)
- **PubMed** (pubmed.ncbi.nlm.nih.gov)
- **IEEE Xplore** (ieeexplore.ieee.org) — through institutional access
- **arXiv** (arxiv.org) — for preprints

**Pro tip:** Use Sci-Hub (if legal in your jurisdiction) for paywalled papers, or check ResearchGate for author-uploaded PDFs.

---

## 🗂️ NOTE-TAKING TEMPLATE

For each paper, capture:

```
## Paper: [Title]
**Authors:**  
**Year:**  
**Key Finding:** (1-2 sentences)  
**Methods:** (Brief description)  
**Limitations:** (What didn't they address?)  
**Relevance to My Project:** (High/Medium/Low + why)  
**Open Questions:** (What should I follow up on?)  
**Citations to Chase:** (Key references they cite)
```

---

*Reading list created: March 7, 2026*  
*Project: Multi-Frequency Shear Wave Elastography*  
*Week 1 of 4 — Literature Review Phase*
