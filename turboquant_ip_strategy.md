# TurboQuant IP Strategy — Patent Landscape + Protection Plan

*Date: 2026-05-07*
*Context: Shear wave elastography patent expiry, open hardware IP strategy*

---

## 🔓 WHAT PATENT EXPIRED

### The Foundational Patent: US6371912B1

| Field | Detail |
|-------|--------|
| **Title** | Method and apparatus for the identification and characterization of regions of altered stiffness |
| **Inventors** | Kathryn R. Nightingale, Gregg E. Trahey, Roger W. Nightingale, Mark L. Palmeri |
| **Assignee** | Duke University |
| **Filed** | 2000-09-18 |
| **Published** | 2002-04-16 |
| **Status** | **Expired - Lifetime** |
| **Expired** | **~2020** (20-year term from filing) |

**What it covers:** Using acoustic radiation force (ARF) to generate shear waves in tissue, then measuring the resulting displacement to characterize tissue stiffness. This is the foundational patent for **all** ARFI-based shear wave elastography.

**What this means for you:** The core concept — "push tissue with ultrasound, measure how it wiggles, infer stiffness" — is now in the public domain. You cannot be blocked from doing shear wave elastography on the basis of this patent.

---

## ⚠️ WHAT PATENTS ARE STILL LIVE

Just because the foundational patent expired doesn't mean you're in the clear. Major players have filed hundreds of improvement patents around the basic concept:

### SuperSonic Imagine (Hologic)
| Patent Family | What It Covers | Status |
|---------------|----------------|--------|
| Real-Time ShearWave® (SWE™) | Multi-push coherent beamforming for real-time 2D SWE | **Active** — filed ~2010–2015 |
| UltraFast® imaging | Plane wave imaging at 20,000 fps for shear wave tracking | **Active** |
| SWE reliability indicators | Algorithms to reject noisy measurements | **Active** |

**Risk: Medium.** These cover specific implementations (plane wave acquisition, real-time 2D mapping, reliability algorithms). Your sequential 8-channel scanning + Bayesian inversion is a different technical approach, but you need to verify non-infringement.

### Siemens Healthineers
| Patent Family | What It Covers | Status |
|---------------|----------------|--------|
| Virtual Touch Quantification (VTQ) | ARFI push with time-to-peak measurement | **Active** |
| Virtual Touch IQ (VTIQ) | 2D quantitative elastography | **Active** |

**Risk: Low-Medium.** VTQ/VTIQ is a different measurement approach (time-to-peak vs. your Bayesian inversion). But the ARFI push mechanism itself could overlap.

### Philips (formerly EPIQ/Affiniti)
| Patent Family | What It Covers | Status |
|---------------|----------------|--------|
| ElastQ Imaging | 2D shear wave elastography with quality metrics | **Active** |

**Risk: Low.** Different implementation.

### Canon (formerly Toshiba)
| Patent Family | What It Covers | Status |
|---------------|----------------|--------|
| Shear Wave Elastography | Various implementations | **Active** |

### General Electric
| Patent Family | What It Covers | Status |
|---------------|----------------|--------|
| 2D Shear Wave Elastography | Various | **Active** |

---

## 🎯 FREEDOM TO OPERATE (FTO) ANALYSIS

You need to check whether TurboQuant V5 infringes any **live** patents. Here's the systematic approach:

### Step 1: Identify Your Novel Technical Features
1. **8-channel sequential scanning** via 74HC595 shift register + DG408 MUX
2. **±100V pulser** with MUR120 T/R diode bridge protection
3. **Bayesian MCMC inversion** for viscoelastic parameter estimation
4. **Open-source FPGA beamforming** on Red Pitaya Zynq-7010
5. **Cost-optimized BOM** (£50 vs. £30k commercial systems)

### Step 2: Map Against Live Patents
| Your Feature | Patent Risk | Notes |
|--------------|-------------|-------|
| Shear wave generation via ARFI | **LOW** — US6371912 expired | Public domain |
| Time-of-flight stiffness measurement | **MEDIUM** — covered by multiple active patents | Your Bayesian approach may be different enough |
| Plane wave imaging (20,000 fps) | **N/A** — you don't do this | You're doing sequential scanning |
| Real-time 2D elastography map | **LOW** — your approach is different | You're not doing real-time 2D mapping |
| Multi-push coherent compounding | **N/A** — not in your design | |
| Your specific T/R switching circuit | **LOW** — implementation-specific | Novel if not published before |
| Your Bayesian MCMC framework | **LOW-MEDIUM** — method patent possible | Check if anyone patented Bayesian SWE specifically |

### Step 3: Professional FTO Search
**You should pay for a formal FTO search (~£3,000–£5,000) before seeking Series A.** But for now, do a DIY preliminary search:

1. **Google Patents** — search for: `shear wave elastography Bayesian`, `ultrasound MUX sequential scanning`, `open source FPGA beamforming`
2. **Espacenet** (European Patent Office) — free, comprehensive
3. **USPTO Patent Full-Text Database** — search claims, not just abstracts

**Red flags to watch for:**
- Claims covering "a method of measuring tissue stiffness using acoustic radiation force impulse combined with Bayesian statistical inversion"
- Claims covering "an 8-channel ultrasound acquisition system with sequential element switching"
- Claims covering "a low-cost open-hardware ultrasound platform for medical imaging"

---

## 🛡️ YOUR IP PROTECTION STRATEGY

You're building **open hardware**. That doesn't mean giving away everything. It means choosing what to protect and what to share.

### 1. TRADEMARK (Protect the Brand)

| What | Action | Cost | Priority |
|------|--------|------|----------|
| **TurboQuant™ name** | File UK trademark application (IPO) | £170 online | **HIGH — do this now** |
| **Logo / wordmark** | Include in trademark filing | Included above | HIGH |
| **Domain names** | Secure turboquant.com, .co.uk, .org | ~£50 | HIGH |
| **Social handles** | Claim @turboquant on Twitter/X, LinkedIn, GitHub | Free | MEDIUM |

**Why now:** If someone else registers "TurboQuant" while you're building, you lose the brand. UK IPO takes ~2–3 months if unopposed.

### 2. COPYRIGHT (Automatic, But Register Key Works)

| What | Protected By | Action |
|------|--------------|--------|
| **Software** (FPGA Verilog, Python analysis) | Automatic copyright | Add copyright headers to all source files |
| **Documentation** (design docs, build guides) | Automatic copyright | Same |
| **PCB designs** (KiCad files) | Automatic copyright | Same |
| **Pitch deck, website content** | Automatic copyright | Same |

**Practical step:** Add this header to every source file:
```
// Copyright (C) 2026 [Your Name / Company]
// Licensed under CERN-OHL-S-2.0 (see LICENSE file)
```

### 3. PATENT (Should You File?)

**The dilemma:** You're open hardware. Patents require public disclosure. But patents also give you exclusivity for 20 years.

**What you COULD patent (if novel and non-obvious):**

| Potential Patent | Novelty? | Likely? | Cost |
|----------------|----------|---------|------|
| Your specific T/R diode bridge + DG408 MUX topology | Maybe — depends on prior art | Medium | £8k–£15k (UK/EPO) |
| Bayesian MCMC + shear wave elastography combination | Possibly — check if prior art exists | Medium | Same |
| Cost-optimized sequential scanning architecture | Probably not novel enough | Low | — |
| 8-channel pulser timing with specific dead-time control | Maybe | Medium | Same |

**My recommendation for now:**
- **Don't file patents yet.** You're seed stage. Patents cost £10k+ and take 3–5 years.
- **Instead:** Keep detailed invention records (dated lab notebooks, git commits with timestamps). If you later decide to patent, you have priority evidence.
- **Exception:** If a competitor starts copying your exact T/R circuit or Bayesian framework before you open-source it, file a provisional patent application (£150 in UK) to secure priority date.

### 4. TRADE SECRETS (Keep Some Things Private)

Even open hardware projects have secrets:

| Secret | Why Keep It? | For How Long? |
|--------|-------------|---------------|
| **Calibration coefficients** for specific phantoms | Competitive advantage for clinical customers | Until you have enough market share |
| **Manufacturing test procedures** | Quality control edge | Always |
| **Supplier relationships / volume pricing** | Cost advantage | Always |
| **Customer pipeline / clinical partnerships** | Business development | Always |
| **Specific component tolerances that matter** | Reliability edge | Until published in peer review |

**How to protect:** NDA with partners, employees, manufacturers. Mark documents "CONFIDENTIAL — TRADE SECRET."

### 5. LICENSING STRATEGY (How You Open-Source)

Don't just dump files on GitHub. Choose a license that protects your interests.

**Recommended: CERN Open Hardware Licence v2 — Strongly Reciprocal (CERN-OHL-S-2.0)**

| License | What It Does | Why Consider It |
|---------|-------------|-----------------|
| **CERN-OHL-S-2.0** (Strongly Reciprocal) | Anyone using your design must share their modifications under the same license. Patent grant included. | ✅ **Best for TurboQuant** — prevents closed-source forks, ensures community contributions flow back |
| **CERN-OHL-W-2.0** (Weakly Reciprocal) | Modifications to your files must be shared, but larger projects incorporating your design don't need to be open. | If you want commercial adoption without forcing openness on derivative products |
| **CERN-OHL-P-2.0** (Permissive) | Anyone can use, modify, close-source. No reciprocity. | If you want maximum adoption, minimal control |
| **GPL-3.0** (Software only) | Strong copyleft for code. | Good for Python/Verilog, but not hardware |
| **MIT** | Do whatever you want. No protection. | ❌ Too permissive — competitors could close-source your work |

**My recommendation:**
- **Hardware (KiCad, BOM, docs):** CERN-OHL-S-2.0
- **Software (FPGA Verilog, Python):** GPL-3.0 or AGPL-3.0
- **Documentation:** CC-BY-SA-4.0

**Why S-2.0 matters:** If Siemens wanted to copy your PCB and sell it closed-source, CERN-OHL-S forces them to publish their modifications. This is your moat as an open hardware company.

---

## 📋 IMMEDIATE ACTION CHECKLIST

### This Week (Free / Cheap)
- [ ] **Register turboquant.com / .co.uk / .org** (~£50)
- [ ] **Claim @turboquant on Twitter/X, LinkedIn, GitHub** (free)
- [ ] **Add copyright headers** to all source files (free)
- [ ] **Draft CERN-OHL-S-2.0 LICENSE file** for repo (free)
- [ ] **Create CONTRIBUTING.md** with CLA (Contributor License Agreement) — ensures contributors grant you their IP (free)

### This Month (~£200)
- [ ] **File UK trademark for "TurboQuant"** (£170)
- [ ] **File UK trademark for logo** (if designed, £170)
- [ ] **Buy D&O insurance** (Directors & Officers) — protects you if someone sues for patent infringement (~£500/year)

### Before Series A (~£5,000)
- [ ] **Professional FTO search** by patent attorney (~£3k–£5k)
- [ ] **Patentability opinion** on T/R circuit + Bayesian framework (~£2k)
- [ ] **Decide:** file patents or rely on trade secrets + speed to market
- [ ] **International trademark** (EUIPO / WIPO Madrid Protocol) if expanding beyond UK (£1k+)

---

## 🎯 YOUR OPEN HARDWARE MOAT

Your real protection isn't patents. It's this combination:

| Layer | Protection | Duration |
|-------|-----------|----------|
| **Brand** | Trademark | Indefinite (renewable) |
| **Community** | Open source + network effects | As long as you're the hub |
| **Expertise** | 18 months of research, phantom protocols, calibration | Hard to replicate |
| **Speed** | Ship prototypes while competitors debate strategy | 6–12 month lead |
| **Trust** | Peer-reviewed validation | Permanent once published |
| **Reciprocity** | CERN-OHL-S forces competitors to contribute back | Permanent |

**The pitch to investors:** *"We're not betting on patent walls. We're betting on open-source network effects. Arduino, Raspberry Pi, and Red Pitaya all built billion-dollar ecosystems without patents. Our moat is the community that forms around validated, open medical physics."*

---

## ⚖️ LEGAL DISCLAIMERS

1. **I'm not a lawyer.** This is strategic guidance, not legal advice. Consult a UK patent attorney (e.g., Marks & Clerk, Mathys & Squire) before making patent decisions.

2. **Patent law is jurisdiction-specific.** US patents don't automatically apply in UK/EU. But major companies file in all jurisdictions.

3. **Freedom to operate ≠ patentability.** Just because you can practice the art (FTO) doesn't mean you can patent your specific implementation. Novelty and non-obviousness are separate tests.

4. **Publication destroys patent rights.** If you publish your Bayesian framework or T/R circuit in a paper or on GitHub before filing a patent application, you can't later patent it (except in US, which has a 1-year grace period).

---

*Key patent: US6371912B1 (Nightingale/Trahey/Duke, expired ~2020)*
*Live patent risk: Medium from SuperSonic Imagine, Siemens, Philips active portfolios*
*Recommended license: CERN-OHL-S-2.0*
*Immediate priority: Trademark "TurboQuant", domain names, copyright headers*

---

*Saved to: `turboquant_ip_strategy.md`*
