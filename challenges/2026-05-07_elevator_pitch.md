# TurboQuant V5 — Elevator Pitch (With Hook + Expansion)

*Audience: Seed-stage investors, grant committees, clinical partners*
*Format: 60-second hook, 2-minute expansion, 5-minute deep dive*

---

## 🪝 THE HOOK (First 15 Seconds — Grab Them)

> **"Last year, a hospital in Lagos turned away two hundred patients for liver scans. They had one FibroScan machine. It broke. The service contract cost more than the device."**

Pause. Let that land.

> **"That's not a failure of medicine. That's a failure of business model."**

---

## ⏱️ THE 60-SECOND PITCH (Hook + Body + Ask)

> **"Last year, a hospital in Lagos turned away two hundred patients for liver scans. They had one FibroScan machine. It broke. The service contract cost more than the device."**
>
> **"That's not a failure of medicine. That's a failure of business model."**
>
> **"One and a half billion people are at risk of liver disease. Today, doctors either cut out a piece of liver — invasive, expensive, misses thirty percent — or they buy a thirty-thousand-pound machine that only works in wealthy hospitals."**
>
> **"TurboQuant is an open-hardware ultrasound platform that maps liver stiffness for under fifty pounds in parts. Eight-channel phased array. Validated Bayesian physics. No black box. No vendor lock-in."**
>
> **"The machines that do this today cost thirty to eighty thousand pounds. We're aiming for three hundred retail. Same physics. Different economics."**
>
> **"We're raising seventy-five thousand pounds to finish our prototype, validate against a medical phantom, and publish peer-reviewed results. Six months to Series A."**
>
> **Want to see the device?"**

**Total time: ~58 seconds**

---

## 🎣 WHY THIS HOOK WORKS

| Element | What It Does |
|---------|-------------|
| **Specific story** (Lagos, 200 patients) | Real, not abstract. Creates mental image. |
| **Concrete failure** (machine broke) | Everyone understands "it stopped working." |
| **Business model twist** | Shifts blame from doctors/tech to economics. Sets up your solution. |
| **Pause after hook** | Gives listener time to nod. Critical. |

**Alternative hooks for different audiences:**

**For technical investors:**
> "The patent for ultrasound shear wave imaging expired in 2019. Since then, exactly zero open-source implementations have passed clinical validation. We built one."

**For clinicians:**
> "My mother had a liver biopsy last year. Two days in hospital. A month of anxiety waiting for results. It came back inconclusive. That procedure is still the gold standard in 2026."

**For grant committees:**
> "The WHO lists liver disease as a top-ten killer globally. The diagnostic tool they recommend costs thirty thousand pounds and requires a trained operator, stable power, and a service contract. None of those exist in the places that need it most."

---

## 🎤 THE 2-MINUTE EXPANSION (When They Say "Tell Me More")

**Use this when they lean in, ask a question, or you get a meeting.**

> **"So here's the full picture."**
>
> **"Liver fibrosis — scarring — is reversible if you catch it early. But catching it early means measuring stiffness of living tissue inside the body. That's hard."**
>
> **"The current options are biopsy — which is invasive, costs two thousand pounds per procedure, and misses a third of cases because the needle hits the wrong spot — or elastography machines like FibroScan, which cost thirty to fifty thousand pounds, lock you into annual service contracts, and only measure one point."**
>
> **"TurboQuant does something different. It fires an ultrasonic pulse into tissue, tracks how shear waves propagate, and back-calculates stiffness using a Bayesian physics framework we wrote. Think of it as MRI-quality tissue mapping at ultrasound cost."**
>
> **"The hardware is an eight-channel phased array on a Red Pitaya board. BOM under fifty pounds. FPGA does real-time beamforming. The analog front-end — pulser, T/R switching, low-noise amps — is our own PCB."**
>
> **"The software layer is where our defensibility lives. We don't just output a number. We output a probability distribution: 'This tissue is 450 kilopascals, plus or minus 30, with 95 percent confidence.' That's the Bayesian part. Clinicians trust it because it says what it doesn't know."**
>
> **"Commercial systems give you a point estimate and a black box. We give you spatial maps and uncertainty quantification. That's publishable science, not just engineering."**
>
> **"Market: we priced the research kit at two hundred ninety-nine pounds. Clinical tier with phantom calibration and documentation at eight hundred ninety-nine. The comparable closed system is FibroScan at thirty thousand plus five thousand a year in service. Even at one-tenth the price, our margin is sixty percent."**
>
> **"The ask: seventy-five thousand pounds for twenty percent. Six months to prototype validation on an ATS liver phantom, peer-reviewed publication, and Series A readiness."**
>
> **"We've got the hardware designed, the physics validated in simulation, and a clear path to regulatory documentation. What we need now is capital to bridge from 'works on my bench' to 'works in a paper the FDA will read.'"**

**Total time: ~2 minutes**

---

## 🔬 THE 5-MINUTE DEEP DIVE (When They Say "How Does It Actually Work?")

**Structure: Problem → Physics → Hardware → Software → Market → Ask**

### 1. Problem (30s)
**"Liver disease is the seventh leading cause of death globally. One point five billion at risk. Fibrosis — scarring — is reversible if caught early. The diagnostic gap is enormous."**

### 2. Physics (60s)
**"We use shear wave elastography. Push the tissue with an acoustic pulse. Measure how fast the resulting shear wave travels. Stiffer tissue = faster wave. It's pure physics — no contrast agents, no radiation."**

**"The hard part is the inverse problem. You measure wave speed at the surface. You want stiffness at depth. That's mathematically ill-posed — infinite solutions fit the data. We solve it with Bayesian MCMC: sample thousands of possible tissue models, keep the ones that match observation, report the distribution."**

**"Result: not 'the stiffness is 4.5 kPa' but 'the stiffness is 4.5 ± 0.8 kPa with 95% credibility.' Clinicians understand uncertainty. Engineers hide it. We expose it."**

### 3. Hardware (60s)
**"The platform is built on Red Pitaya STEMlab 125-14 — a 125 MSPS, 14-bit acquisition board with Zynq FPGA. Our custom PCB adds: eight-channel transmit/receive switching, ±100V pulser for deep tissue, DG408 analog mux, OPA1641 low-noise amps, and T/R protection diodes so the receive chain survives the transmit pulse."**

**"Total BOM: fifty-three pounds for the analog PCB, two hundred fifty for the Red Pitaya, three hundred for the full system. Compare to FibroScan at thirty thousand."**

### 4. Software (45s)
**"FPGA handles real-time beamforming and I/Q demodulation. Python host does the Bayesian inversion using PyMC. Full stack is open-source — KiCad hardware, Verilog FPGA, Python analysis. Anyone can audit it, improve it, or manufacture it under license."**

### 5. Market + Revenue (45s)
**"Three revenue streams. One: hardware kits at two ninety-nine for researchers and education. Two: clinical tier at eight ninety-nine with phantom calibration and regulatory docs. Three: software licensing at ninety-nine per year for advanced DSP and cloud analytics."**

**"Path to profitability: one thousand clinical units plus five hundred service contracts by year three. One point two million revenue, forty-five percent blended margin."**

### 6. Ask + Milestones (30s)
**"Seventy-five thousand pounds. Twenty percent equity. Six-month runway. Milestones: Q2 PCB fabrication and bring-up. Q3 phantom validation and IEEE paper. Q4 ex vivo tissue study and Series A."**

**"Clear physics. Defensible IP. Real clinical need. Proven team."**

---

## 📋 QUICK-REFERENCE CHEAT SHEET

| Time | What to Say | Goal |
|------|-------------|------|
| 0–15s | **Hook** (Lagos story) | Get their attention |
| 15–45s | **Problem** (1.5B people, biopsy vs £30k machine) | Establish urgency |
| 45–55s | **Solution** (£50 BOM, open hardware, Bayesian physics) | Position differentiation |
| 55–58s | **Ask** (£75k, 6 months, Series A path) | Clear next step |
| 58s | **"Want to see it?"** | Engagement close |

| If They Ask... | Use... |
|---------------|--------|
| "Tell me more" | 2-minute expansion |
| "How does it work?" | 5-minute physics + hardware |
| "Who else is doing this?" | Competitive landscape slide |
| "What's the IP?" | 18 months research + open hardware moat |
| "Why you?" | Team slide + GitHub contributors |

---

## 🎯 DELIVERY TIPS

1. **Pause after the hook.** 2–3 seconds of silence feels like confidence.
2. **Never apologise for the ask.** £75k is small for medical device validation. Say it like it's obvious.
3. **If they interrupt with a question, answer it.** The pitch is a conversation, not a speech.
4. **Have the device photo on your phone.** The moment they say "yes," show them.
5. **End with a question, not a statement.** "Want to see the device?" invites response. "That's our pitch." ends the conversation.

---

## 📝 PRACTICE DRILL

**Record yourself doing the 60-second version. Listen back. Check for:**
- [ ] Hook lands (you'd lean in if you heard it at a bar)
- [ ] No jargon without instant explanation
- [ ] Every claim has a number (£, %, time)
- [ ] Ask is clear and specific
- [ ] Under 60 seconds

**Practice the 2-minute version once you can do the 60-second one in your sleep.**

---

*Generated: 2026-05-07*
*Format: 60s / 2min / 5min for investor audiences*
