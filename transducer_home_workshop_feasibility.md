# Home Workshop Fabrication Feasibility Assessment
**Transducer:** TR-3.5-PHANTOM-001 (3.5 MHz, 19 mm, f/2.1)  
**Date:** 2026-03-18  
**Assessment Scope:** DIY fabrication with typical home workshop tools

---

## 1. FABRICATION STEP-BY-STEP FEASIBILITY

### Step 1: PZT Crystal Procurement ✅ EASY

**What you need:** 19 mm diameter × 0.64 mm thick PZT-5H disc

**Home workshop approach:**
- **Buy pre-cut discs:** PI Ceramic, APC International, Steminc
  - Cost: $15–40 per disc
  - Tolerance: ±0.05 mm thickness (acceptable)
  - Already electroded (chrome/gold)

**Avoid if possible:**
- Cutting your own from bulk PZT (requires diamond saw, risk of cracking)
- Lapping to thickness (requires precision grinding setup)

**Verdict:** ✅ **Trivial** — just order the right part

---

### Step 2: Backing Material (Tungsten-Epoxy) ⚠️ MODERATE

**What you need:** 3:1 tungsten powder to epoxy, 3.6 MRayl impedance

**Home workshop approach:**

**Materials:**
- Tungsten powder: ~$50/100g (eBay, scientific suppliers)
- Epoxy: Epo-Tek 301 or similar ($30)
- Mixing: Digital scale (0.01g resolution)

**Process:**
1. Weigh 3 parts tungsten : 1 part epoxy by mass
2. Mix thoroughly (5+ minutes)
3. **Vacuum degas** ← Critical step
4. Pour onto PZT back surface
5. Cure: 24h @ 60°C or 48h room temp

**Home workshop challenges:**

| Challenge | Severity | Workaround |
|-----------|----------|------------|
| **Vacuum degassing** | 🔴 High | Vacuum chamber required — $80 DIY or $200 lab grade |
| | | Without vacuum: voids → 3–6 dB sensitivity loss |
| | | Alternative: centrifuge while curing (jury-rigged) |
| **Thickness control** | 🟡 Medium | Target 3+ mm (not critical) |
| **Uniform mixing** | 🟡 Medium | Small batches, thorough stirring |

**DIY Vacuum Chamber Options:**
- **Budget:** $80 — Vacuum pump + acrylic chamber (Amazon)
- **Better:** $200 — 2-gallon vacuum chamber + pump (Harbor Freight)
- **Hack:** Use pressure cooker with vacuum port (DIY)

**Verdict:** ⚠️ **Moderate** — vacuum degassing is the critical barrier

---

### Step 3: Matching Layer (Alumina-Epoxy) ⚠️ MODERATE

**What you need:** 0.11 mm thick, 3.2 MRayl impedance, λ/4

**Home workshop approach:**

**Materials:**
- Alumina (Al₂O₃) powder: ~$20 (ceramic supply)
- Same epoxy as backing
- Target: ~40% alumina by weight

**Process:**
1. Mix alumina-epoxy to target impedance (iterative)
2. **Spin-coat or blade-coat** to 0.11 mm
3. Cure: 12h @ room temperature

**Home workshop challenges:**

| Challenge | Severity | Workaround |
|-----------|----------|------------|
| **Thickness precision (0.11 mm)** | 🔴 High | Spin coater ideal; blade/roller is hard |
| | | Caliper measurement while wet, adjust |
| | | Accept ±0.02 mm → frequency shift ±3% |
| **Impedance tuning** | 🟡 Medium | Requires network analyzer OR |
| | | Build test transducer, measure, iterate |

**DIY Spin Coater Options:**
- **Budget:** $60 — DVD motor + speed controller + 3D printed chuck
- **Better:** $150 — Used lab spin coater (eBay)
- **Manual:** Doctor blade + feeler gauges (less consistent)

**Iterative Impedance Matching (no network analyzer):**
1. Build test transducer
2. Connect to scope + function generator
3. Find resonance dip on receive
4. Adjust matching layer thickness for best bandwidth
5. Takes 2–3 iterations

**Verdict:** ⚠️ **Moderate-to-Hard** — thickness control is finicky

---

### Step 4: Housing & Lens ⚠️ MODERATE

**What you need:** Brass housing, PMMA lens with R=40 mm concave surface

**Home workshop approach:**

**Option A: Buy commercial housing**
- Olympus/Panametrics transducer housings: $30–50
- Drill out old element, install yours
- ✅ Easiest path

**Option B: Machine from brass**
- Requires lathe for cylindrical housing
- Requires milling for cable strain relief
- Requires turning for lens seat

**Option C: 3D print + shield**
- Housing: PETG or ABS ($5)
- Shield: Copper tape or conductive paint ($10)
- ⚠️ May have acoustic impedance mismatches

**Lens fabrication:**

| Method | Feasibility | Result |
|--------|-------------|--------|
| **Buy concave PMMA lens** | ✅ Easy | $20–40, optical supply |
| **Machine from PMMA rod** | ⚠️ Moderate | Requires lathe + form tool |
| **Cast in mold** | ⚠️ Moderate | 3D printed mold, epoxy resin |
| **Thermal form over ball** | 🟡 Hard | Risk of bubbles/thickness variation |

**Best home workshop path:**
- Buy concave PMMA lens ( Edmund Optics, Thorlabs)
- 3D print housing with lens seat
- Shield with copper tape

**Verdict:** ⚠️ **Moderate** — buying components beats machining

---

### Step 5: Cable & Electrical ✅ EASY

**What you need:** RG174/U coax, 50 Ω, BNC or SMA connector

**Home workshop approach:**
- Cable: $5 (Amazon)
- Connector: $3 (SMA preferred for lab work)
- Soldering: Standard iron, thin rosin-core solder

**Key considerations:**
- Keep ground connection short (<5 mm)
- Use ferrite bead on cable near housing (noise reduction)
- Seal entry with epoxy potting

**Verdict:** ✅ **Trivial** — basic soldering

---

### Step 6: Impedance Matching Network ✅ EASY

**What you need:** Series inductor 6.5 μH for tuning

**Home workshop approach:**
- Buy fixed inductor: $2 (Digi-Key, Mouser)
- OR wind your own: 20 turns on T37-2 toroid
- Solder in series with coax center conductor

**Optional fine-tuning:**
- Parallel capacitor (10–50 pF trimmer)
- Adjust for minimum VSWR at 3.5 MHz

**Verdict:** ✅ **Trivial**

---

## 2. EQUIPMENT REQUIREMENTS SUMMARY

### Essential (Must Have)

| Item | Cost | Purpose |
|------|------|---------|
| **Digital scale (0.01g)** | $15 | Weighing powders |
| **Vacuum chamber + pump** | $80–200 | Degassing epoxy |
| **Calipers (0.01 mm)** | $20 | Thickness measurement |
| **Soldering iron** | $30 | Electrical connections |
| **Basic hand tools** | $50 | Assembly |
| **Total essential** | **$195–315** | — |

### Highly Recommended

| Item | Cost | Purpose |
|------|------|---------|
| **Spin coater (DIY or used)** | $60–150 | Matching layer thickness |
| **Function generator** | $50–100 | Initial testing |
| **Oscilloscope (50+ MHz)** | $100–300 | Pulse observation |
| **Total recommended** | **$210–550** | — |

### Nice to Have (Not Critical)

| Item | Cost | Purpose |
|------|------|---------|
| **Network analyzer** | $500–3000 | Impedance characterization |
| **Hydrophone + preamp** | $2000–5000 | Beam profile measurement |
| **Scanning tank system** | $3000–10000 | Automated beam mapping |

---

## 3. REALISTIC QUALITY ACHIEVABLE

### What You CAN Achieve at Home

| Parameter | Target | Achievable at Home | Notes |
|-----------|--------|-------------------|-------|
| **Centre frequency** | 3.5 MHz | ±5% (3.3–3.7 MHz) | Thickness control |
| **Bandwidth** | 114% | 100–120% | Backing quality |
| **Pulse duration** | 0.5 μs | 0.6–0.7 μs | Some ring-down |
| **Sensitivity** | Reference | -3 to -6 dB vs. ideal | Voids in backing |
| **Beam profile** | Gaussian | Acceptable | Lens quality |
| **Lateral resolution** | 0.90 mm | 0.95–1.1 mm | Practical limit |

### What You CANNOT Easily Achieve

| Parameter | Why Not | Requires |
|-----------|---------|----------|
| **NIST-traceable specs** | No calibrated reference | $2–5K hydrophone calibration |
| **±2% frequency tolerance** | Thickness control limits | Precision lapping machine |
| **Sidelobes <-25 dB** | Lens precision | CNC machining or mold |
| **Cross-talk <-30 dB** | Array only — N/A for single | Array design |

---

## 4. REALISTIC BUDGET FOR HOME BUILD

### Minimal Viable Build ($250)
- Pre-cut PZT disc: $25
- Tungsten powder: $50
- Epoxy: $30
- Vacuum chamber: $80
- Housing (3D print + shield): $15
- Lens (buy concave PMMA): $25
- Cable/connectors: $10
- Misc (scale, calipers): $15

### Good Quality Build ($500)
- Pre-cut PZT disc: $25
- Tungsten powder: $50
- Epoxy: $30
- Vacuum chamber (better): $150
- Spin coater (DIY): $80
- Housing (machined brass): $50
- Lens (optical grade): $40
- Cable/connectors: $15
- Test equipment (used scope + FG): $200
- Misc: $20

### Comparison

| Build | Cost | Quality | Notes |
|-------|------|---------|-------|
| **Minimal DIY** | $250 | 70–80% of spec | Functional, some tolerance |
| **Good DIY** | $500 | 85–95% of spec | Near-commercial performance |
| **Commercial (CIRS)** | $1,500 | 100% | Documented, traceable |
| **Custom (lab built)** | $1,000+ | 100%+ | With full test equipment |

---

## 5. SKILL LEVEL REQUIRED

### Can a Beginner Do This?

**Short answer:** Yes, but expect 2–3 failed attempts first.

**Skill breakdown:**

| Skill | Level Needed | Learnable? |
|-------|--------------|------------|
| **Epoxy mixing/pouring** | Basic | ✅ Yes — practice on dummies |
| **Vacuum degassing** | Basic | ✅ Yes — straightforward |
| **Soldering** | Intermediate | ✅ Yes — need steady hand |
| **Spin coating** | Intermediate | ⚠️ Takes practice |
| **Impedance tuning** | Advanced | ⚠️ Requires test equipment |
| **Beam profiling** | Expert | ❌ Hard without hydrophone |

**Learning curve estimate:**
- **Attempt 1:** Likely fails (voids, wrong thickness, delamination)
- **Attempt 2:** Functional but poor specs (bandwidth, sensitivity)
- **Attempt 3:** Acceptable performance (within 10% of target)
- **Attempt 4+:** Consistent, repeatable builds

---

## 6. TIME ESTIMATE

### Per Transducer (Once Skilled)

| Step | Time | Notes |
|------|------|-------|
| PZT prep | 15 min | Clean, inspect |
| Backing | 2h + 24h cure | Mix, degas, pour, cure |
| Matching layer | 1h + 12h cure | Mix, spin coat, cure |
| Housing assembly | 1h | Lens bonding, cable |
| Electrical | 30 min | Solder, potting |
| Testing | 1h | Impedance, pulse-echo |
| **Total active time** | **6h** | Spread over 2–3 days |
| **Total calendar time** | **3 days** | Curing time dominates |

### First Build (Learning Included)
- **Calendar time:** 2–3 weeks
- Includes: material procurement, failed attempts, learning curve

---

## 7. RISK ASSESSMENT

### What Can Go Wrong

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Voids in backing** | High | -3–6 dB sensitivity | Vacuum degas thoroughly |
| **Matching layer too thick/thin** | Medium | Frequency shift | Caliper check while wet |
| **PZT cracking** | Low | Total loss | Handle carefully, no stress |
| **Delamination** | Medium | Total loss | Surface prep, proper epoxy |
| **Wrong impedance** | Medium | Poor sensitivity | Iterate matching layer |
| **Lens misalignment** | Low | Beam asymmetry | Careful bonding jig |

### Safety Considerations

| Hazard | Risk | Precaution |
|--------|------|------------|
| **Lead in PZT** | Moderate | Wash hands, don't sand without PPE |
| **Epoxy vapors** | Low | Work in ventilated area |
| **Tungsten dust** | Low | Don't inhale fine powder |
| **Vacuum chamber** | Low | Don't exceed pressure ratings |

---

## 8. VERDICT: IS HOME WORKSHOP REALISTIC?

### Overall Assessment: ✅ **YES, WITH CAVEATS**

**You CAN build a functional 3.5 MHz transducer at home if:**
1. You buy pre-cut PZT (don't try to machine it)
2. You get a vacuum chamber for degassing
3. You accept ±5% tolerance on frequency
4. You're willing to iterate 2–3 times

**You CANNOT easily achieve:**
1. NIST-traceable specifications
2. ±2% frequency precision
3. Automated beam profiling
4. Commercial-grade consistency (batch-to-batch)

### Recommended Approach for Home Workshop

**Phase 1: Proof of Concept ($250)**
- Buy all components pre-made
- Build one transducer
- Test with basic equipment (scope + function generator)
- Verify it produces an image in water/phantom

**Phase 2: Optimization ($250 more)**
- Add spin coater for better matching layer
- Build 2–3 units to establish repeatability
- Characterize beam profile by scanning in water tank

**Phase 3: Production (if needed)**
- Only if you need 5+ units
- Refine processes based on Phase 1–2 learnings

---

## 9. ALTERNATIVE: SEMI-DIY PATH

**If full DIY seems daunting, consider:**

### Option A: Transducer Kit
- Some suppliers (Olympus, custom labs) sell "unmounted" transducers
- You provide housing and cable
- Cost: $100–200 for element + backing
- You do: housing, lens, electrical, testing

### Option B: Refurbish Commercial
- Buy dead/damaged commercial transducer ($50–100 on eBay)
- Remove old element
- Install your custom element
- Keep commercial housing, lens, cable

### Option C: Collaboration
- Find university with hydrophone setup
- Build at home, characterize there
- Trade: your build skills for their test equipment

---

## 10. FINAL RECOMMENDATION

**For your elastography research specifically:**

| Approach | Recommendation | Rationale |
|----------|----------------|-----------|
| **Build from scratch** | ✅ **Do it** | You have the skills, bandwidth matters |
| **Home workshop** | ✅ **Viable** | $250–500 budget, 2–3 week timeline |
| **Full DIY** | ⚠️ **Partial** | Buy pre-cut PZT, pre-formed lens |
| **Testing** | ⚠️ **Limited** | Function generator + scope sufficient for go/no-go |

**Bottom line:** Yes, build it. The 114% bandwidth you designed exceeds commercial options and is valuable for shear wave imaging. Start with the minimal viable build ($250), iterate once or twice, and you'll have a research-grade transducer.

**Critical success factors:**
1. Get the vacuum chamber
2. Buy pre-cut PZT
3. Buy concave lens (don't try to make it)
4. Expect iteration — first one is a learning experience

---

**Document generated:** 2026-03-18 07:45 UTC  
**Next action:** Procure materials list or refine design for first build
