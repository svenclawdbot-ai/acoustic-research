# Carbon Fiber Composite NDE — TurboQuant V5 Application Analysis

*Date: 2026-05-07*
*Status: Research phase — preliminary opportunity assessment*

---

## 🎯 THE OPPORTUNITY

Carbon fiber reinforced polymer (CFRP) composites are used everywhere strength-to-weight ratio matters:
- **Aerospace:** Boeing 787 fuselage (50% CFRP by weight), Airbus A350 wings
- **Wind energy:** Turbine blades 50–80m long
- **Automotive:** BMW i3/i8 body panels, Formula 1 monocoques
- **Sport:** High-end bicycles, racing shells, hockey sticks

**The problem:** Delaminations, voids, and matrix cracking happen inside the laminate. They're invisible from the outside. A blade or wing section can look pristine while losing 40% of its compressive strength.

**Current inspection:**
- **Ultrasonic C-scan:** Gold standard, but requires immersion tank or coupling gel, single-point scanning, hours per blade
- **X-ray CT:** Excellent resolution, but £500k+ machine, radiation hazard, not field-deployable
- **Thermography:** Fast but only catches surface-near defects
- **Tap test:** Literally tapping with a coin. Subjective. Used on 80% of wind blades because it's cheap.

**Gap:** No portable, quantitative, contactless stiffness mapping system exists for CFRP at under £1,000.

---

## 🔬 PHYSICS: WHY CFRP IS HARD FOR ULTRASOUND

### Material Properties

| Property | Soft Tissue (Liver) | Carbon Fiber Composite | Factor |
|----------|---------------------|------------------------|--------|
| Density | ~1,000 kg/m³ | ~1,600 kg/m³ | 1.6× |
| Longitudinal speed | 1,540 m/s | 3,000 m/s | 2× |
| Shear modulus G | 1–50 kPa | **3–30 GPa** | **600,000×** |
| Young's modulus E | 5–100 kPa | **70–200 GPa** | **2,000,000×** |
| Attenuation @ 1 MHz | 0.5 dB/cm | 5–20 dB/cm | 10–40× |

**Critical insight:** Carbon fiber is **six orders of magnitude stiffer** than soft tissue. Shear waves travel at **~1,800 m/s** in CFRP vs. **2–10 m/s** in liver. Your medical elastography calibration is completely irrelevant here.

### What This Means for TurboQuant V5

| Medical Parameter | CFRP Equivalent | V5 Status |
|-------------------|-----------------|-----------|
| 3.5 MHz transducer | 1–5 MHz for CFRP (lower freq = deeper penetration) | ⚠️ May need different probe |
| 100V pulser | 200–400V for thick sections (>10mm) | ⚠️ At limit, may need boost |
| Shear wave tracking @ 2 m/s | Shear wave tracking @ 1,800 m/s | ❌ Completely different regime |
| Kelvin-Voigt viscoelastic model | Anisotropic transversely isotropic model | ❌ Different physics needed |
| Isotropic assumption | Strongly anisotropic (fiber direction matters) | ❌ Must account for |

**Verdict: TurboQuant V5 hardware can be adapted, but the physics framework needs significant rework.**

---

## 📊 THE CFRP NDE MARKET

| Segment | Annual Spend | Current Method | TurboQuant Fit |
|---------|-------------|----------------|----------------|
| **Aerospace MRO** | £2.5B globally | Ultrasonic C-scan, X-ray | Medium — needs cert |
| **Wind blade inspection** | £800M globally | Tap test, visual, rope access | **High** — desperate for better |
| **Automotive motorsport** | £150M globally | X-ray, CT, destructive test | Medium — high value parts |
| **Marine (yachts, racing)** | £100M globally | Visual, tap test | Medium |
| **Sporting goods QA** | £50M globally | Destructive sampling | Low — cost sensitive |

**Most accessible entry:** Wind blade inspection. Why:
- Blades are inspected every 6–12 months
- Current method (tap test + visual) is laughably inadequate
- Rope-access technicians earn £800/day to tap blades with hammers
- Operators are desperate for quantitative data to justify maintenance spend
- Regulatory pressure (IEC 61400) increasing inspection frequency

---

## 🔧 TECHNICAL PATH: ADAPTING V5 FOR CFRP

### Hardware Changes Needed

| Subsystem | Medical V5 | CFRP Version | Effort |
|-----------|-----------|--------------|--------|
| **Transducer** | 3.5 MHz focused, 8mm diameter | 1–2 MHz broadband, 15–25mm diameter | Medium — new probe design |
| **Pulser voltage** | ±100V | ±200–400V | Medium — boost converter or external pulser |
| **T/R switching** | MUR120 diodes, 2 µs recovery | Same, or faster PIN diodes | Low — may work as-is |
| **LNA gain** | 40 dB (weak tissue echoes) | 20–30 dB (strong composite echoes) | Low — adjust feedback resistors |
| **MUX** | DG408 8:1 | Same, or upgrade to DG409 differential | Low |
| **FPGA processing** | Beamforming, I/Q demod | Lamb wave mode separation, dispersion tracking | **High** — new algorithms |

### Physics Changes Needed

| Medical Approach | CFRP Approach | Complexity |
|------------------|-------------|------------|
| Isotropic Kelvin-Voigt | **Transversely isotropic** stiffness tensor (5 independent constants) | High |
| Single shear wave mode | **Multiple Lamb wave modes** (A0, S0, A1, S1...) at each frequency | High |
| Point measurement | **Direction-dependent** stiffness (fiber vs. transverse vs. through-thickness) | High |
| Simple phase velocity | **Dispersion curve fitting** across frequencies | Medium |
| 2D plane | **Curved surface + thickness variation** | Medium |

### Simplified First Approach

For a minimum viable CFRP prototype, don't solve the full anisotropic problem. Instead:

**Approach: Guided Lamb wave tomography**
1. Use TurboQuant's 8-channel array to excite and receive **Lamb waves** (plate-guided modes)
2. Measure **group velocity** of A0 mode at multiple frequencies (100–500 kHz)
3. Back-project velocity variations to infer **delamination locations**
4. Don't quantify stiffness in GPa — just flag **"healthy / damaged / critical"** regions

**Why this works:**
- Lamb wave velocity drops 10–30% in delaminated regions — easily detectable
- A0 mode at low frequency is sensitive to delaminations but not fiber direction
- TurboQuant's FPGA can do real-time group velocity estimation
- No need for full stiffness tensor inversion

---

## 💰 REVISED BUSINESS CASE

### Option A: Medical First (Original Plan)
- Target: Liver fibrosis, breast lesion characterization
- Market: £4B medical ultrasound elastography
- Regulatory path: FDA 510(k) or CE-MDR (2–3 years, £500k+)
- Revenue: £299 research / £899 clinical kits

### Option B: NDE First (CFRP Pivot)
- Target: Wind blade inspection, aerospace MRO
- Market: £800M wind + £2.5B aerospace NDE
- Regulatory path: None for industrial NDE (faster)
- Revenue: £1,500–£3,000 per unit (industrial customers pay more)
- Service model: £500/month per turbine for continuous monitoring

### Option C: Dual-Track
- **Year 1:** Sell NDE units to wind industry (revenue, validation)
- **Year 2–3:** Use revenue + data to fund medical regulatory pathway
- **Advantage:** NDE revenue funds medical R&D; medical IP protects NDE from commodity competition

**My recommendation: Option C.**

NDE gets you to revenue in 6 months. Medical gets you to acquisition/IPO in 5 years. Both use the same hardware platform (TurboQuant V5). Different software stacks. Different pricing. Same brand.

---

## 🧪 PROOF-OF-CONCEPT PLAN (CFRP)

### Phase 1: Desktop Validation (4 weeks, £500)
1. Source 300×300×5mm CFRP panel with known delaminations (~£150)
2. Source 1 MHz broadband transducer (~£100)
3. Modify V5 pulser to 200V (new MOSFETs or external module, ~£50)
4. Write Lamb wave group velocity estimation in FPGA (~2 weeks)
5. Scan panel, compare to C-scan reference data

**Success criterion:** Detect delaminations >10mm with >80% accuracy vs. known defects.

### Phase 2: Wind Blade Field Test (8 weeks, £2,000)
1. Partner with wind farm operator or blade manufacturer
2. Deploy portable system on 45m blade (rope access or platform)
3. Compare to visual/tap test results + subsequent destructive inspection
4. Collect 50+ blade inspection datasets

**Success criterion:** Identify 90% of major delaminations, false positive rate <15%.

### Phase 3: Productize (12 weeks, £5,000)
1. Ruggedized enclosure (IP65, -20°C to +50°C)
2. Battery pack (4-hour operation)
3. Tablet interface with pass/fail/critical classification
4. Cloud reporting for fleet managers
5. Pricing: £2,499 unit + £99/month software

---

## ⚠️ RISKS & MITIGATIONS

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| CFRP anisotropy makes simple velocity measurement unreliable | Medium | High | Start with known-isotropic test panels; validate against CT |
| Attenuation too high for >20mm thick sections | Medium | Medium | Lower frequency (500 kHz) + coded excitation + pulse compression |
| Existing NDE players (Olympus, Mistras) launch low-cost competitor | Medium | High | Speed to market; community lock-in via open data formats |
| Wind industry slow to adopt new tech | Medium | Medium | Target early adopters (offshore operators with high blade-replacement costs) |
| Medical regulatory path delayed by dual-track focus | Low | High | Keep medical as 20% effort; don't let NDE consume all resources |

---

## 📚 KEY REFERENCES

1. **Zhou et al. (2022)** — "Ultrasonic Testing of Carbon Fiber-Reinforced Polymer Composites" — Comprehensive review of UT methods for CFRP
2. **Zhu & Rizzo (2022)** — "Array-guided wave reconstruction of composite stiffness matrix" — Genetic algorithm approach to CFRP characterization
3. **Springer (2024)** — "Numerical Simulation of CFRP Composite Delamination" — FEM validation of ultrasonic detection
4. **MDPI Applied Sciences (2024)** — "Recent Advancements in Guided Ultrasonic Waves for Structural Health Monitoring" — Lamb wave techniques
5. **Wiley (2022)** — "Automated Quantification of Interlaminar Delaminations" — CT-benchmarked ultrasonic method

---

## 🎯 DECISION POINT

**Does TurboQuant V5 become a medical device company with an NDE side-hustle, or an NDE company with a medical moonshot?**

The hardware is 80% the same. The physics stack is 40% the same. The markets are completely different.

**What's your instinct?**

A) **Medical first** — CFRP is a distraction from the bigger prize
B) **NDE first** — Revenue now, medical later
C) **Dual-track** — Both simultaneously, shared hardware platform
D) **NDE only** — Medical regulatory path is too painful

Pick one and I'll build the detailed roadmap.

---

*Saved to: `turboquant_cfrp_nde_analysis.md`*
