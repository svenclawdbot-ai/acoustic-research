# TurboQuant Dual-Track Strategy
*Revenue-first NDE + Medical moonshot*
*Date: 2026-05-07 | Decision: Dual-track confirmed*

---

## 🎯 THE DUAL-TRACK ARCHITECTURE

```
                    ┌─────────────────────────────────────┐
                    │      TURBOQUANT V5 HARDWARE         │
                    │  (Red Pitaya + Custom PCB + Probes) │
                    └──────────────┬──────────────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
    ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
    │   MEDICAL STACK │   │   NDE STACK     │   │  CORE PLATFORM  │
    │                 │   │                 │   │                 │
    │ • Shear wave    │   │ • Lamb wave     │   │ • FPGA beamform │
    │   elastography  │   │   tomography    │   │ • ADC/DAC       │
    │ • Kelvin-Voigt  │   │ • Group velocity│   │ • MUX control   │
    │   viscoelastic  │   │ • Delam flagging│   │ • Power mgmt    │
    │ • Bayesian MCMC │   │ • Pass/fail     │   │ • Comms         │
    │ • Liver staging │   │   classification│   │                 │
    │ • CE-MDR/FDA    │   │ • IEC 61400     │   │                 │
    │   pathway       │   │   compliance    │   │                 │
    │                 │   │                 │   │                 │
    │ PRICE: £899     │   │ PRICE: £2,499   │   │ BOM: £53 + RP   │
    │ MARGIN: 65%    │   │ MARGIN: 75%     │   │                 │
    └────────┬────────┘   └────────┬────────┘   └─────────────────┘
             │                     │
             ▼                     ▼
    ┌─────────────────┐   ┌─────────────────┐
    │ MEDICAL MARKET  │   │ NDE MARKET      │
    │                 │   │                 │
    │ • Hospitals     │   │ • Wind farms    │
    │ • Clinics       │   │ • Blade OEMs    │
    │ • Research      │   │ • MRO providers │
    │                 │   │ • Insurance     │
    │ REVENUE: Y3     │   │ REVENUE: Y1     │
    │ TAM: £4B        │   │ TAM: £3.3B      │
    └─────────────────┘   └─────────────────┘
```

**Core insight:** Same hardware platform, two software stacks. Medical validates the physics. NDE validates the business.

---

## 💰 REVENUE MODEL — NDE FIRST

### Year 1 Target: £50K–£100K (NDE Only)

| Quarter | Action | Revenue | Cumulative |
|---------|--------|---------|------------|
| **Q2 2026** | Build 5 NDE beta units. Field test with 2 wind operators. | £0 | £0 |
| **Q3 2026** | Sell 10 units @ £2,499 to early adopters. | £24,990 | £24,990 |
| **Q4 2026** | Sell 20 units + 15 software subscriptions @ £99/mo. | £54,460 | £79,450 |
| **Q1 2027** | Sell 25 units + 30 subscriptions. First service contracts. | £68,210 | £147,660 |

**Year 1 target: £80K–£100K** (realistic with 2 salespeople + demo program)

### Pricing Strategy

| Tier | Price | What's Included | Target Customer |
|------|-------|-----------------|-----------------|
| **NDE Research** | £1,999 | Hardware + basic software + documentation | Universities, research labs |
| **NDE Professional** | £2,999 | Hardware + full software + cloud reporting + 1yr support | Wind operators, MRO contractors |
| **NDE Enterprise** | £4,999 | 3 units + fleet management portal + priority support + annual calibration | Large wind farm operators (>50 turbines) |
| **Software Subscription** | £99/mo | Cloud analytics, trending, automated reporting, API access | All professional/enterprise |
| **Service Contract** | £499/yr | Calibration, firmware updates, email support | All tiers |

**Average revenue per customer (Year 1):** £2,800 (hardware + 3 months software)

---

## 🚀 NDE FAST-TRACK ROADMAP

### Phase 1: Prototype to Beta (Weeks 1–8) | £1,500 budget

**Goal:** Working NDE unit that detects delaminations in CFRP panel with >80% accuracy.

| Week | Task | Deliverable | Cost |
|------|------|-------------|------|
| 1–2 | Source CFRP test panel with known defects (15×15cm, 3 delaminations at known depths) | Panel delivered | £150 |
| 1–2 | Source 1 MHz broadband composite probe (15mm diameter, 50mm focus) | Probe delivered | £120 |
| 2–3 | Modify TurboQuant pulser: add external 200V boost module or swap IRF830 for higher-voltage MOSFET | ±200V pulses verified on scope | £80 |
| 3–4 | Write Lamb wave A0 mode excitation in FPGA (tone burst, 100–500 kHz sweep) | FPGA bitstream | Time |
| 4–5 | Implement group velocity estimation: cross-correlation between receiver channels | Algorithm validated on panel | Time |
| 5–6 | Build pass/fail classifier: healthy velocity = 2,800 m/s, damaged = <2,400 m/s | Threshold-based detection | Time |
| 6–7 | Integrate with tablet interface: simple "scan → map → report" workflow | Android/iOS app v0.1 | Time |
| 7–8 | Validate against panel: measure 50 positions, compare to known defect map | Accuracy report | £0 |

**Phase 1 success criteria:**
- [ ] Detect all 3 delaminations in test panel
- [ ] No false positives on healthy regions
- [ ] Scan time <5 minutes per 10×10cm area
- [ ] System fits in backpack (portable)

### Phase 2: Field Validation (Weeks 9–16) | £3,000 budget

**Goal:** Deploy on real wind blade. Compare to existing inspection methods. Generate case study.

| Week | Task | Deliverable |
|------|------|-------------|
| 9–10 | Identify wind operator partner (approach 5, close 1) | LOI signed |
| 10–11 | Site visit: measure blade access, curvature, thickness variation | Site report |
| 11–13 | Deploy 2 beta units. Train technician. Collect 100+ scans | Dataset |
| 13–14 | Compare to visual inspection + tap test results | Comparison report |
| 14–15 | If possible: destructive inspection of blade section for ground truth | Validation report |
| 15–16 | Write case study: "Detected 12cm delamination on 45m blade, operator replaced blade 6 months earlier than scheduled" | Published case study |

**Key metric:** Operator must say "this is better than tap test" in writing.

### Phase 3: Productize & Sell (Weeks 17–24) | £5,000 budget

**Goal:** Ruggedized product, first 10 sales, recurring revenue foundation.

| Week | Task | Deliverable |
|------|------|-------------|
| 17–18 | Design rugged enclosure (IP65, -20°C to +50°C, shock-mounted) | CAD files |
| 18–19 | Source battery pack (4-hour operation, hot-swappable) | Working prototype |
| 19–20 | Tablet interface v1.0: scan workflow, PDF report generation, cloud sync | App released |
| 20–21 | Cloud portal: fleet dashboard, trending, automated alerts | Web app live |
| 21–22 | Build 10 production units | Inventory |
| 22–23 | Launch: website, demo videos, pricing, sales deck | Go-to-market |
| 23–24 | First 10 sales + subscription signups | Revenue |

---

## 🏥 MEDICAL SLOW-TRACK (Parallel, Lower Priority)

### Year 1: 20% Effort

| Quarter | Action | Milestone |
|---------|--------|-----------|
| Q2 2026 | Continue phantom studies (ATS liver phantom, £3,000) | Baseline stiffness dataset |
| Q3 2026 | Submit conference abstract (IEEE UFFC or similar) | First publication |
| Q4 2026 | Full paper draft: Bayesian framework + phantom validation | Preprint on arXiv |
| Q1 2027 | Submit to journal (Ultrasound in Medicine & Biology) | Peer review |

### Year 2–3: Scale Up
- Q2 2027: Ex vivo tissue study (porcine liver, partnership with veterinary school)
- Q3 2027: Regulatory consultant engagement (CE-MDR gap analysis)
- Q4 2027: Clinical pilot (partner NHS hospital, ethics approval)
- 2028: CE marking submission, first clinical sales

**Medical is funded by NDE revenue.** No separate medical fundraising until NDE is profitable.

---

## 📊 RESOURCE ALLOCATION

### Time Split (Founder)

| Activity | % Time | Focus |
|----------|--------|-------|
| **NDE hardware/software** | 40% | Getting product to market |
| **NDE sales & partnerships** | 30% | Wind operators, demos, case studies |
| **Medical research** | 15% | Paper writing, phantom studies |
| **Platform/core** | 10% | FPGA, firmware, shared infrastructure |
| **Admin/fundraising** | 5% | Minimal until NDE revenue flowing |

### Budget Split (Year 1)

| Category | Amount | Source |
|----------|--------|--------|
| **NDE prototype development** | £3,000 | Seed / personal |
| **NDE field testing** | £3,000 | Seed / personal |
| **Medical phantom** | £3,000 | Seed / personal |
| **Medical paper costs** | £1,000 | Seed / personal |
| **Total Year 1 spend** | **£10,000** | **£75k seed covers 7.5 years at this burn** |

**This is why NDE-first makes sense:** You can validate the business on £10k. Medical needs £500k+ for regulatory.

---

## 🎯 IMMEDIATE NEXT STEPS (This Week)

### Monday
- [ ] **Decision confirmed:** Dual-track. Document in `memory/2026-05-07.md`.
- [ ] **Register domain:** `turboquant-nde.com` or brand domain if name chosen.

### Tuesday–Wednesday
- [ ] **Order CFRP test panel:** Search "CFRP delamination test specimen NDE" — suppliers in UK/Germany.
- [ ] **Order 1 MHz probe:** Contact Imperium/Verasonics distributor, or search "1 MHz broadband ultrasound transducer composite".

### Thursday–Friday
- [ ] **Pulser modification:** Design 200V boost circuit (flyback converter or charge pump).
- [ ] **FPGA Lamb wave code:** Start with simple tone burst generation at 200 kHz.

### Weekend
- [ ] **Build v0.1:** Assemble modified hardware, verify basic operation.

---

## 📈 SUCCESS METRICS

### Month 1 (June 2026)
- [ ] CFRP panel detected with >80% accuracy
- [ ] Modified pulser outputting 200V pulses
- [ ] FPGA generating Lamb wave tone bursts

### Month 3 (August 2026)
- [ ] 2 wind operator partners identified
- [ ] 1 site visit completed
- [ ] Beta unit deployed in field

### Month 6 (November 2026)
- [ ] First 3 NDE units sold
- [ ] First software subscription activated
- [ ] Case study published on website

### Month 12 (May 2027)
- [ ] 25 units sold, £70k revenue
- [ ] 20 active software subscriptions
- [ ] Medical paper under peer review
- [ ] Break-even on NDE operations

---

## 🚨 RISK: SPLIT FOCUS

**The danger of dual-track:** Neither track gets enough attention. Medical slides. NDE ships late.

**Mitigation:**
1. **Hard priority:** NDE is 70% of effort until first £10k revenue. No exceptions.
2. **Medical is "one day per week":** Saturday paper writing. Sunday phantom study. Rest of week = NDE.
3. **Kill criteria:** If NDE hasn't generated £10k by Month 6, pause medical entirely. If NDE generates £50k by Month 6, hire contractor for medical paper.

---

## 📝 DOCUMENTS TO CREATE

| Document | Purpose | Deadline |
|----------|---------|----------|
| `nde_product_spec.md` | Hardware/software requirements for NDE unit | Week 1 |
| `nde_roadmap.md` | Detailed weekly plan with tasks | Week 1 |
| `nde_sales_deck.md` | 5-slide pitch for wind operators | Week 8 |
| `nde_pricing.md` | Pricing tiers, margin analysis | Week 8 |
| `medical_paper_outline.md` | Structure for IEEE/UMB submission | Week 4 |

---

*Decision: Dual-track. NDE funds medical. Revenue target: £80k Year 1.*
*Focus this week: CFRP panel + 1 MHz probe + pulser modification.*

---

*Saved to: `turboquant_dual_track_strategy.md`*
