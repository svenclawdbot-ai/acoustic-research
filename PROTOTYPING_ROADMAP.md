# TurboQuant V5 — Executive Summary & Prototyping Roadmap

**Date:** May 6, 2026
**Project:** TurboQuant MUX/LNA v5
**Status:** Schematic 70% complete — PCB layout not started
**Target:** Working prototype for phantom validation by August 2026

---

## 1. WHERE WE ARE NOW

### What's Proven ✅

| Item | Status | Evidence |
|------|--------|----------|
| **System architecture** | ✅ Locked | 4-sheet hierarchical schematic defined |
| **Component selection** | ✅ Validated | DG408, IRF830, OPA1641, 74HCT595 all justified |
| **Power design** | ✅ Complete | 12V→5V→3.3V, thermal verified (LM7805 OK at ~50mA) |
| **Digital control** | ✅ Complete | 74HCT595 + BSS138 gate drivers, SPI interface |
| **T/R bridge analysis** | ✅ Complete | MUR120: >26dB isolation, <10dB loss with 1k bias |
| **BOM** | ✅ Generated | ~£42 total, all parts from LCSC/DigiKey |
| **PCB floorplan** | ✅ Documented | 100×80mm, 4-layer, zone partitioning defined |
| **Physics framework** | ✅ Published-ready | Bayesian MCMC, 2D FDTD, Zener calibration |
| **FPGA control** | 🟡 Partial | Red Pitaya API exists, needs integration testing |
| **Investor materials** | ✅ Complete | Pitch deck + one-pager committed |

### What's Blocking 🔴

| Blocker | Severity | Effort to Clear |
|---------|----------|-----------------|
| **Analog schematic wiring** | 🔴 High | 2-3 days — T/R diodes→MUX→LNA connections |
| **TX switch schematic wiring** | 🔴 High | 1-2 days — gate drivers→MOSFETs→TX_BUS |
| **Root hierarchical connections** | 🔴 High | 1 day — power/signal routing between sheets |
| **ERC validation** | 🟡 Medium | 1 day — run KiCad ERC, fix errors/warnings |
| **PCB layout** | 🔴 Critical | 1-2 weeks — 4-layer, HV clearances, thermal |
| **DRC + Gerber generation** | 🟡 Medium | 2-3 days — JLCPCB design rules |

### What We Haven't Started 🔴

- PCB layout (not started)
- Fabrication (dependent on layout)
- Assembly (dependent on fabrication)
- Bench validation (dependent on assembly)
- Phantom testing (dependent on bench validation)

---

## 2. PATH TO PROTOTYPING — PHASE BY PHASE

### Phase 1: Schematic Completion (Weeks 1-2)

**Goal:** ERC-clean schematic ready for PCB layout

**Tasks:**
1. **Analog sheet wiring** (3-4 days)
   - Connect D1-D32 T/R bridge outputs to U1/U2 DG408 inputs (pins 1-8)
   - Connect DG408 outputs (pins 13, 14) to U3/U4 OPA1641 inputs (pin 3)
   - Connect OPA1641 outputs (pin 6) to hierarchical RX0_OUT/RX1_OUT
   - Add power: +5V → U3/U4 VCC, +12V → U1/U2 VDD
   - Verify ground connections to all ICs

2. **TX switch sheet wiring** (1-2 days)
   - Connect GATE0-GATE7 from digital sheet to TC4427 inputs
   - Connect TC4427 outputs to IRF830 gates (with 100Ω series R)
   - Connect IRF830 drains to TX_BUS, sources to GND
   - Add +12V to TC4427 VDD pins
   - Verify Zener clamps on all gates

3. **Root sheet wiring** (1 day)
   - Hierarchical power connections (+5V, +12V, GND)
   - Digital→analog control signals (MUX_A/B/C/EN)
   - Digital→TX switch (GATE0-7)
   - Analog→root (RX0/RX1 to SMA connectors)

4. **ERC run** (1 day)
   - Run KiCad electrical rule check
   - Fix all errors (unconnected pins, power violations)
   - Fix warnings (missing footprints, net naming)

**Deliverable:** `turboquant_mux_lna_v5.kicad_sch` — ERC clean, 0 errors, 0 warnings

**Dependencies:** None — can start immediately

---

### Phase 2: PCB Layout (Weeks 3-4)

**Goal:** Fabrication-ready PCB with DRC pass

**Tasks:**
1. **Component placement** (3-4 days)
   - Power zone (top-left): LM7805, AMS1117, input terminal
   - Digital zone (top-right): 74HCT595, BSS138, E1 header
   - Analog zone (center): DG408×2, OPA1641×2, T/R bridges
   - TX zone (bottom): IRF830×8, TC4427×4, heatsink area
   - SMA connectors: board edge, grouped by channel

2. **Routing** (4-5 days)
   - Layer 1 (Top): HV traces, SMA pads, short signals
   - Layer 2 (GND): Solid ground plane, stitched vias
   - Layer 3 (PWR): +5V pour, +12V pour (split zones)
   - Layer 4 (Bottom): Additional signals, test points
   - Critical: >2mm clearance for ±100V traces
   - Gate drive traces: <20mm, matched lengths for 8 channels
   - LNA inputs: guard ring, shielded from TX zone

3. **DRC + validation** (2 days)
   - KiCad DRC: clearance, width, annular ring, silkscreen
   - JLCPCB capability check (min 0.15mm trace/space)
   - HV clearance review (2mm for 100V)
   - Thermal review: IRF830 copper pour, LM7805 tab

4. **Gerber generation** (1 day)
   - Generate Gerbers, drill files, pick-and-place
   - Create fabrication notes (stackup, finish, silkscreen)
   - Export BOM for assembly quote

**Deliverable:** `turboquant_mux_lna_v5_gerbers.zip` + `BOM_for_JLCPCB.xlsx`

**Dependencies:** Phase 1 complete (ERC-clean schematic)

---

### Phase 3: Fabrication + Procurement (Weeks 5-6)

**Goal:** PCBs and components in hand

**Tasks:**
1. **PCB fabrication** (5-7 days)
   - Vendor: JLCPCB (4-layer, 100×80mm, standard FR4)
   - Quantity: 10 boards (~$30-50 including shipping)
   - Options: ENIG finish, white silkscreen, 1.6mm thickness
   - Lead time: 5-7 days to UK

2. **Component procurement** (parallel, 5-7 days)
   - Primary: LCSC (China, cheapest for passives, ~7-10 days)
   - Secondary: DigiKey UK (ICs, faster, ~2-3 days)
   - Critical path items: DG408×2, IRF830×8, OPA1641×2
   - Budget: ~£50/board × 10 = £500 components

3. **Tooling prep** (1-2 days)
   - Soldering iron + fine tip (for SMD 0603)
   - Hot plate or reflow oven (for SOIC-16, SOT-23)
   - Microscope or magnifying lamp
   - Multimeter, oscilloscope (for bring-up)

**Deliverable:** 10 bare PCBs + full component kit

**Dependencies:** Phase 2 complete (Gerbers + BOM)

---

### Phase 4: Assembly + Power-On (Week 7)

**Goal:** First board powers on without smoke

**Tasks:**
1. **SMD assembly** (2-3 days)
   - Start with power section (LM7805, AMS1117, passives)
   - Add digital (74HCT595, BSS138)
   - Add analog (DG408, OPA1641, SMD resistors/caps)
   - Add THT last (MUR120, IRF830, SMA connectors, terminal block)

2. **Power-on test** (1 day)
   - Visual inspection: shorts, cold joints, wrong parts
   - Smoke test: 12V input, check for heat/smoke
   - Rail verification: +5V (±5%), +3.3V (±5%), +12V pass-through
   - Current draw: expect ~15-50mA at idle

3. **Digital bring-up** (1 day)
   - Red Pitaya connection: SPI signals visible on scope
   - 74HCT595 clocking: SRCLK, RCLK, SER waveforms
   - BSS138 outputs: GATE0-7 switch between 0V and ~5V

**Deliverable:** Board that passes power-on and digital control tests

**Dependencies:** Phase 3 complete (PCBs + components)

---

### Phase 5: Bench Validation (Weeks 8-9)

**Goal:** All subsystems verified against specifications

**Tasks:**
1. **T/R bridge validation** (2 days)
   - Isolation test: 100V TX pulse, measure RX node leakage
   - Target: >26 dB isolation (measurable with scope/divider)
   - Insertion loss: inject small signal, measure output
   - Target: <10 dB loss (verify 1k bias resistor fix)
   - PRF test: switch at 1 kHz, 5 kHz, 10 kHz

2. **MUX + LNA validation** (2 days)
   - DG408 channel select: verify all 8 channels switch correctly
   - Crosstalk: signal on CH0, measure leakage on CH1-7
   - OPA1641 gain: inject known signal, verify gain=10
   - Bandwidth: sweep 100 kHz to 10 MHz, verify flatness
   - Noise: shorted input, measure output noise floor

3. **TX switch validation** (2 days)
   - Gate drive: TC4427 output rise/fall time (<100ns)
   - IRF830 switching: drain waveform clean, no ringing
   - TX pulse: amplitude, width, repeatability
   - Thermal: IR camera during continuous 1 kHz operation

4. **Integration test** (2 days)
   - Full TX→RX loop: pulse on CH0, switch to RX, capture echo
   - All 8 channels: sequential scan, verify timing
   - Red Pitaya ADC: capture real waveform, verify SNR

**Deliverable:** Validation report with measured specs vs. targets

**Dependencies:** Phase 4 complete (working power + digital)

---

### Phase 6: Phantom Testing Prep (Weeks 10-12)

**Goal:** System ready for ATS 539 liver phantom study

**Tasks:**
1. **FPGA integration** (3-4 days)
   - Load Red Pitaya FPGA bitstream
   - Verify DMA acquisition at 125 MSPS
   - Python API: channel select, pulse fire, data capture
   - Real-time display: B-mode + elastography maps

2. **Transducer integration** (2-3 days)
   - 3.5 MHz focused transducer (spec already defined)
   - Matching network: 6.5 µH series inductor
   - Water tank testing: pulse-echo in deionized water
   - Phantom gel coupling: verify impedance match

3. **Phantom study prep** (2-3 days)
   - ATS 539 phantom procurement (~£300-500)
   - Test protocol: axial resolution, lateral resolution, cyst detection
   - Data acquisition: 100 frames, SNR measurement
   - Correlation with known phantom stiffness values

**Deliverable:** Phantom test report + dataset for journal submission

**Dependencies:** Phase 5 complete (all subsystems validated)

---

## 3. REALISTIC TIMELINE SUMMARY

| Phase | Weeks | Calendar (from May 6) | Key Deliverable |
|-------|-------|----------------------|-----------------|
| 1. Schematic completion | 1-2 | May 6 – May 19 | ERC-clean schematic |
| 2. PCB layout | 3-4 | May 20 – June 2 | Fabrication-ready Gerbers |
| 3. Fab + procurement | 5-6 | June 3 – June 16 | 10 PCBs + components |
| 4. Assembly + power-on | 7 | June 17 – June 23 | Working board |
| 5. Bench validation | 8-9 | June 24 – July 7 | Validation report |
| 6. Phantom prep | 10-12 | July 8 – July 28 | Phantom test dataset |
| **Journal submission** | 13-14 | August | IEEE T-UFFC or PMB |
| **Series A raise** | 14-16 | August – September | With validation data |

**Total: ~12 weeks to phantom-ready prototype**
**Total: ~14 weeks to journal submission**

---

## 4. RESOURCE REQUIREMENTS

### Money

| Item | Cost | When Needed |
|------|------|-------------|
| PCB fabrication (10 qty) | £40-60 | Week 3 (May 20) |
| Components (10 boards) | £400-500 | Week 3 (May 20) |
| Red Pitaya STEMlab 125-14 | £250 | Week 4 (May 27) |
| ATS 539 liver phantom | £350-500 | Week 9 (July 7) |
| Oscilloscope (if not owned) | £200-400 | Week 7 (June 17) |
| Soldering tools/reflow | £100-150 | Week 7 (June 17) |
| **TOTAL** | **£1,340 – £1,860** | Over 12 weeks |

### Time

| Activity | Hours/Week | Who |
|----------|-----------|-----|
| Schematic + PCB | 15-20 | Lead engineer |
| Assembly + testing | 10-15 | Lead engineer |
| FPGA/software | 5-10 | Lead engineer |
| Documentation | 2-3 | Lead engineer |
| Phantom testing | 5-10 | Lead + collaborator |
| **TOTAL** | **37-58 hrs/week** | |

### People

| Role | Commitment | Source |
|------|-----------|--------|
| Lead engineer | Full-time (owner) | James |
| PCB review | 4-8 hours | Advisor or freelance (Upwork ~£200) |
| Phantom testing | 2-3 days | NHS hepatologist advisor |
| FPGA support | Ad-hoc | Red Pitaya community/open-source |

---

## 5. RISK REGISTER

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **PCB design error** | Medium | High | Design review, 10-board batch, test points everywhere |
| **Component shortage** | Medium | Medium | Order early, LCSC + DigiKey dual-source, alternates listed |
| **T/R bridge underperforms** | Low-Medium | High | Bench test before PCB order; PIN diode upgrade path (MA4P7102) |
| **LNA noise too high** | Low | Medium | Guard ring layout, shielded enclosure, filtered power |
| **IRF830 thermal issues** | Low | Medium | Copper pour + small heatsink, duty cycle limited to burst mode |
| **JLCPCB delay** | Medium | Low | Order early; PCBWay backup; standard specs (no special materials) |
| **Phantom unavailable** | Low | Low | CIRS 040 alternative; ex vivo tissue as backup |
| **Personal time crunch** | High | High | 12-week buffer built in; advisor support for testing phase |

---

## 6. GO/NO-GO DECISIONS

### Go/No-Go #1: Post-Schematic (Week 2)
**Criteria:**
- [ ] ERC clean: 0 errors, <5 warnings
- [ ] Peer review completed (advisor or Upwork freelancer)
- [ ] BOM finalized with LCSC part numbers
- [ ] £500 procurement budget secured

**If NO-GO:** Fix schematic issues, delay PCB layout by 1 week

### Go/No-Go #2: Post-Layout (Week 4)
**Criteria:**
- [ ] DRC clean: 0 errors, all JLCPCB rules satisfied
- [ ] HV clearance review: >2mm on all 100V traces
- [ ] Gerbers generated and visually inspected
- [ ] Component order placed

**If NO-GO:** Fix layout issues, re-order components, delay fab by 1 week

### Go/No-Go #3: Post-Assembly (Week 7)
**Criteria:**
- [ ] Power rails stable: +5V, +3.3V, +12V
- [ ] Digital control responding: GATE0-7 toggle correctly
- [ ] At least 1 channel: TX pulse visible, RX echo path connected
- [ ] No smoke, no excessive heat

**If NO-GO:** Debug with scope, fix solder joints, possible PCB respin

### Go/No-Go #4: Post-Validation (Week 9)
**Criteria:**
- [ ] T/R isolation >26 dB
- [ ] Insertion loss <10 dB
- [ ] LNA gain = 10 ±10%
- [ ] All 8 channels switch correctly
- [ ] PRF ≥ 1 kHz achievable

**If NO-GO:** Component substitution (PIN diodes, different LNA), layout fix for v5.1

---

## 7. WHAT "DONE" LOOKS LIKE

### Minimum Viable Prototype (Week 7)
- Board powers on, rails stable
- Digital control works via Red Pitaya
- At least 1 channel: TX pulse + RX echo captured

### Full Validation (Week 9)
- All 8 channels operational
- Specs met: isolation, loss, gain, PRF
- Integration with Red Pitaya Python API

### Phantom-Ready (Week 12)
- 3.5 MHz transducer integrated
- Real-time acquisition + display
- Phantom test protocol executed
- Dataset ready for journal submission

### Investor-Ready (Week 14)
- Working prototype in hand
- Phantom validation data
- IEEE paper draft submitted
- Series A pitch with traction

---

## 8. EXECUTIVE SUMMARY (TL;DR)

**TurboQuant V5 is 70% designed, 0% built.**

We have a validated system architecture, proven component selection, peer-review-ready physics, and investor materials. What's missing is the actual hardware: schematic wiring, PCB layout, fabrication, assembly, and testing.

**Realistic path:** 12 weeks and £1,500 to a phantom-ready prototype.

**Not 4 weeks.** Not magic. Just disciplined execution of a known path.

**Key enabler:** The physics framework is already done. The hardware is the bottleneck, but it's a *known* bottleneck with clear steps.

**Biggest risk:** Personal time availability. The 12-week timeline assumes 40-50 hours/week of focused engineering work. If that's not realistic, add 50% to the timeline.

**Decision needed now:**
1. Do we have £1,500 for the prototype build? (or £75K seed for 20 units + phantom)
2. Do we have 12 weeks of engineering time?
3. If yes to both: start schematic wiring this week.

---

*Document: Executive Summary & Prototyping Roadmap*
*Date: May 6, 2026*
*Next action: Begin analog schematic wiring in KiCad*
