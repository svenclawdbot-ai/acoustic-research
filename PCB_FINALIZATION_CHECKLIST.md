# PCB Finalization Checklist - TurboQuant Prototype

**Board:** TurboQuant MUX/LNA v4  
**Status:** In Progress  
**Target:** Production-ready prototype for fabrication  
**Priority:** Critical path for hardware bring-up

---

## Current Status

| Component | Version | Status | Notes |
|-----------|---------|--------|-------|
| Schematic | v4 | 🟡 In Progress | SKiDL source exists |
| PCB Layout | v4 | 🔴 Not Started | Autosave only |
| BOM | - | 🔴 Not Generated | Needs export |
| Gerbers | - | 🔴 Not Generated | Post-layout |
| Documentation | - | 🔴 Not Started | Assembly guide needed |

---

## Phase 1: Schematic Finalization

### 1.1 Review Circuit Blocks

#### Power Supply Section
- [ ] **12V Input Protection**
  - [ ] Polyfuse rating (2A suitable?)
  - [ ] Reverse polarity diode (1N4007 → SS34 for lower drop?)
  - [ ] TVS diode for transients?

- [ ] **LM7805 Regulator**
  - [ ] Thermal calculations: P = (12V - 5V) × I_load
  - [ ] With 8 channels @ 50mA each: I_load ≈ 400mA
  - [ ] Power dissipation: 7V × 0.4A = 2.8W
  - [ ] **⚠️ TO-220 requires heatsink at >1W**
  - [ ] Consider: LM2596 switching regulator instead

- [ ] **AMS1117-3.3 Regulator**
  - [ ] Input: 5V, Output: 3.3V
  - [ ] Dropout: 1.3V max → 5V - 3.3V = 1.7V margin ✓
  - [ ] Decoupling: 100nF + 10μF ✓

#### Digital Control Section
- [ ] **74HC595 Shift Register**
  - [ ] VCC = 5V (compatible with 3.3V logic?)
  - [ ] **⚠️ 74HC595 VIH min = 3.5V, ESP32 outputs 3.3V**
  - [ ] Solution: Use 74HCT595 (TTL levels) or 74LV595 (3.3V)
  - [ ] Clock rate: <25MHz for 74HC series ✓
  - [ ] Q0-Q7 drive strength: 6mA per pin

- [ ] **Control Interface (E1 Header)**
  - [ ] Pinout matches Red Pitaya E1 GPIO
  - [ ] Level shifting needed for 3.3V ↔ 5V?
  - [ ] Pull-up/pull-down resistors on control lines

#### Analog MUX Section
- [ ] **CD4051B Multiplexers**
  - [ ] VDD = 12V? 5V? Check analog signal range
  - [ ] For ±100V signals, need HV MUX (e.g., DG408)
  - [ ] ON resistance: ~125Ω @ 5V, ~80Ω @ 10V
  - [ ] Transition time: ~500ns
  - [ ] Break-before-make guaranteed ✓

- [ ] **Address Lines (A/B/C)**
  - [ ] Connected to 74HC595 outputs
  - [ ] Pull-down resistors to prevent floating
  - [ ] RC filters for glitch suppression?

#### LNA Section
- [ ] **OPA1641 Op-Amps**
  - [ ] Gain: 10 (Rf = 10k, Rg = 1k)
  - [ ] Bandwidth: 11MHz at G=10 ✓
  - [ ] Input bias current: 20pA (low for high-Z sources)
  - [ ] **⚠️ Power supply: ±2.25V to ±18V**
  - [ ] Current: 1.8mA per amp × 2 = 3.6mA

- [ ] **AC Coupling**
  - [ ] High-pass filter: fc = 1/(2πRC)
  - [ ] For ultrasound (100kHz+): C ≥ 10nF with R=100Ω

#### TX Switching Section
- [ ] **TX Switches (MD1210/TC6320 or discrete)**
  - [ ] HV capability: 100V+ for ultrasound pulsers
  - [ ] Switching speed: <100ns rise/fall
  - [ ] Current handling: 2A+ pulsed
  - [ ] Isolation when off: >60dB

### 1.2 Design Rule Check (DRC) - Schematic

- [ ] All nets labeled clearly
- [ ] No unconnected pins (intentional NC marked)
- [ ] Reference designators unique
- [ ] Footprints assigned and verified
- [ ] Power pins connected
- [ ] Decoupling capacitors on all ICs
- [ ] Test points added for critical signals

### 1.3 Annotation & Documentation

- [ ] Reference designators: sequential, logical
- [ ] Component values: include tolerance where critical
- [ ] Notes for assembly (heatsinks, orientation, etc.)
- [ ] Version and date on schematic
- [ ] Revision history block

---

## Phase 2: PCB Layout

### 2.1 Board Specifications

| Parameter | Value | Notes |
|-----------|-------|-------|
| Layers | 4 | Signal/GND/Power/Signal |
| Board size | 100mm × 80mm | TBD based on connectors |
| Thickness | 1.6mm | Standard |
| Copper weight | 1oz outer, 0.5oz inner | Standard |
| Min trace width | 0.15mm (6mil) | For signals |
| Min via size | 0.3mm drill, 0.6mm pad | Standard |

### 2.2 Component Placement

#### Mechanical Considerations
- [ ] **Connectors on one edge** (front panel)
  - [ ] 8× SMA connectors for TX
  - [ ] 2× SMA connectors for RX (I/Q)
  - [ ] 12V power input (barrel jack or terminal block)
  - [ ] E1 GPIO header (2×13 pin)

- [ ] **Mounting holes**
  - [ ] 4× M3 holes, 3.2mm drill (3.5mm pad)
  - [ ] Corner placement, 5mm from edges
  - [ ] Ground connection to mounting holes

- [ ] **Height constraints**
  - [ ] TO-220 regulators: heatsink clearance
  - [ ] Electrolytic caps: vertical height
  - [ ] Test points: probe access

#### Electrical Considerations
- [ ] **Partitioning**
  ```
  ┌─────────────────────────────────────┐
  │  Power Section    │  Digital Ctrl   │
  │  (12V, 5V, 3.3V)  │  (74HC595)      │
  ├───────────────────┴─────────────────┤
  │                                     │
  │        Analog Section               │
  │  (LNA, MUX, TX switches)            │
  │                                     │
  ├─────────────────────────────────────┤
  │  TX0 TX1 TX2 TX3 TX4 TX5 TX6 TX7   │
  │  [SMA] [SMA] [SMA] ...              │
  └─────────────────────────────────────┘
  ```

- [ ] **High-voltage TX section**
  - [ ] Keep away from sensitive analog
  - [ ] Wide clearances (>1mm for 100V)
  - [ ] Guard rings around HV traces

- [ ] **Low-noise analog section**
  - [ ] Shielded from digital switching
  - [ ] Short traces to minimize noise pickup
  - [ ] Ground plane under op-amps
  - [ ] Guard rings around high-impedance inputs

### 2.3 Routing Strategy

#### Power Rails
- [ ] **12V**: Thick trace (≥1mm for 2A)
- [ ] **5V**: Moderate trace (≥0.5mm for 1A)
- [ ] **3.3V**: Moderate trace (≥0.5mm for 500mA)
- [ ] **GND**: Solid ground plane on layer 2

#### Critical Signals
- [ ] **Analog inputs (RX)**: differential routing, matched lengths
- [ ] **TX switches**: keep short, minimize inductance
- [ ] **Control signals**: no issue, but avoid analog section
- [ ] **Clock (SRCLK)**: keep away from analog, short traces

#### High-Speed Considerations
- [ ] 20MHz signals: not really high-speed, standard routing OK
- [ ] Watch for crosstalk between channels
- [ ] Keep clock away from analog inputs

### 2.4 Design Rule Check (DRC) - Layout

- [ ] Clearances: trace-trace, trace-pad, pad-pad
- [ ] Annular ring: sufficient copper around vias
- [ ] Silkscreen: doesn't overlap pads
- [ ] Solder mask: correct openings
- [ ] Drill sizes: standard sizes preferred
- [ ] Copper balance: even distribution

### 2.5 Copper Pour

- [ ] **Layer 2 (GND)**: Solid ground plane
- [ ] **Layer 3 (PWR)**: Split planes for 12V, 5V, 3.3V
- [ ] **Top/Bottom**: Pour GND, stitch with vias

---

## Phase 3: Manufacturing Preparation

### 3.1 Bill of Materials (BOM)

**Generate BOM with:**
- [ ] Reference designator
- [ ] Manufacturer part number
- [ ] Description
- [ ] Package/footprint
- [ ] Quantity
- [ ] Distributor part numbers (DigiKey, Mouser, LCSC)
- [ ] Alternate parts (if applicable)
- [ ] Critical specifications noted

**Example Format:**
```csv
Ref,MPN,Description,Package,Qty,DigiKey,Mouser,Critical
U1,74HC595D,Shift Register,SOIC-16,1,296-1462-5-ND,595-SN74HC595DR,
U2,LM7805CT,5V Regulator,TO-220,1,LM7805CT-ND,511-LM7805CT,Heatsink req
...
```

### 3.2 Assembly Drawings

- [ ] Component placement drawing (top view)
- [ ] Component placement drawing (bottom view)
- [ ] Board outline with dimensions
- [ ] Hole locations and sizes
- [ ] Stackup specification
- [ ] Special notes for assembly

### 3.3 Gerber Files

**Required layers:**
- [ ] Top copper (GTL)
- [ ] Bottom copper (GBL)
- [ ] Top solder mask (GTS)
- [ ] Bottom solder mask (GBS)
- [ ] Top silkscreen (GTO)
- [ ] Bottom silkscreen (GBO)
- [ ] Drill file (DRL)
- [ ] Drill map/rack (optional but helpful)
- [ ] Board outline (GKO/GM1)
- [ ] Layer stackup info

**Verify:**
- [ ] Gerber viewer check (KiCad GerbView, online viewer)
- [ ] All layers align correctly
- [ ] No missing features
- [ ] Text is readable
- [ ] Drill hits are centered on pads

### 3.4 Pick-and-Place File

- [ ] Component X,Y coordinates
- [ ] Rotation angle
- [ ] Reference designator
- [ ] Layer (top/bottom)
- [ ] Part number

### 3.5 Fabrication Drawing

- [ ] Board dimensions
- [ ] Layer stackup
- [ ] Controlled impedance requirements (if any)
- [ ] Surface finish (HASL, ENIG, etc.)
- [ ] Silkscreen color
- [ ] Solder mask color
- [ ] Special requirements (beveling, slots, etc.)

---

## Phase 4: Design Review

### 4.1 Self-Review Checklist

- [ ] Power calculations verified
- [ ] Thermal analysis complete
- [ ] Signal integrity considered
- [ ] EMC/EMI mitigations in place
- [ ] Manufacturability checked (DFM)
- [ ] Testability considered (DFT)
- [ ] Assembly considerations (DFA)

### 4.2 Peer Review

**Reviewers needed:**
- [ ] Analog engineer (LNA, MUX section)
- [ ] Digital engineer (shift register, control)
- [ ] Power engineer (regulators, thermal)
- [ ] Manufacturing/PCB expert

**Review focus:**
- [ ] Schematic correctness
- [ ] Component selection
- [ ] Layout optimization
- [ ] Cost reduction opportunities

### 4.3 Simulation/Verification

- [ ] **Power integrity**: Voltage drop analysis
- [ ] **Thermal**: Hotspot identification
- [ ] **Signal integrity**: Not critical at 20MHz, but check analog
- [ ] **EMI**: Review switching noise coupling

---

## Phase 5: Prototype Fabrication

### 5.1 PCB Fabrication

**Recommended manufacturers:**
| Manufacturer | Lead Time | Cost (4-layer) | Notes |
|--------------|-----------|----------------|-------|
| JLCPCB | 5-7 days | $30-50 | Good quality, low cost |
| PCBWay | 5-7 days | $40-60 | Good for prototypes |
| OSH Park | 12-15 days | $100+ | US-based, purple PCBs |
| Eurocircuits | 5-10 days | €80+ | European, good quality |

**Order specifications:**
- [ ] Quantity: 5-10 boards (for bring-up and spares)
- [ ] Lead time: Standard (expedite only if critical)
- [ ] Panelization: Single boards (not panelized for prototype)
- [ ] Testing: Electrical test recommended

### 5.2 Component Procurement

**Procurement strategy:**
- [ ] Order all components before PCB arrival
- [ ] Check stock levels at distributors
- [ ] Order 20% extra for prototypes (mistakes, debugging)
- [ ] Identify long-lead items early

**Tools:**
- [ ] DigiKey BOM Manager
- [ ] Mouser BOM Tool
- [ ] Octopart (for price/stock comparison)

### 5.3 Assembly Options

**Option A: Self-Assembly**
- [ ] Solder paste + stencil (JLCPCB offers)
- [ ] Hot plate or reflow oven for SMD
- [ ] Hand soldering for THT components
- [ ] Microscope for fine-pitch inspection

**Option B: PCBA Service**
- [ ] JLCPCB SMT assembly (economical)
- [ ] PCBWay PCBA
- [ ] MacroFab (US-based)
- [ ] Screaming Circuits (quick turn)

**For v4 prototype:**
- Recommend: JLCPCB PCBA for SMD + self-assembly for THT
- Reason: Cost-effective, good quality

---

## Phase 6: Bring-Up Plan

### 6.1 Visual Inspection
- [ ] Solder joints quality
- [ ] Component orientation
- [ ] Missing components
- [ ] Shorts between adjacent pins

### 6.2 Power-On Sequence
1. [ ] Check 12V input (no load)
2. [ ] Check 5V regulator output
3. [ ] Check 3.3V regulator output
4. [ ] Check current consumption (should be <100mA idle)

### 6.3 Functional Tests
1. [ ] Digital control (shift register)
2. [ ] Analog MUX switching
3. [ ] LNA gain and bandwidth
4. [ ] TX switch operation
5. [ ] Full system integration

### 6.4 Documentation
- [ ] Record power consumption
- [ ] Note any issues or modifications
- [ ] Update BOM if substitutions made
- [ ] Document calibration procedure

---

## Timeline Estimate

| Phase | Duration | Prerequisites |
|-------|----------|---------------|
| Schematic finalization | 1-2 days | Design review |
| PCB layout | 3-5 days | Schematic complete |
| Design review | 1 day | Layout complete |
| Manufacturing prep | 1 day | Review complete |
| PCB fabrication | 5-7 days | Gerbers submitted |
| Component procurement | 3-5 days | BOM finalized |
| Assembly | 1-2 days | PCB + components |
| Bring-up | 2-3 days | Assembly complete |
| **Total** | **~3 weeks** | |

---

## Critical Issues to Resolve

### ⚠️ HIGH PRIORITY

1. **LM7805 Thermal Issue**
   - 2.8W dissipation requires heatsink
   - **Recommendation:** Switch to LM2596 switching regulator
   - **Effort:** 1 day schematic update

2. **74HC595 Level Compatibility**
   - 3.3V ESP32 driving 5V CMOS
   - **Recommendation:** Use 74HCT595 or add level shifter
   - **Effort:** 2 hours

3. **CD4051 Signal Range**
   - Verify analog signal voltage range
   - If >15V, need HV MUX (DG408/DG409)
   - **Effort:** Depends on finding

### ⚠️ MEDIUM PRIORITY

4. **Connector Selection**
   - Finalize SMA vs BNC vs MCX
   - Determine if panel mount needed

5. **Test Points**
   - Add test points for debugging
   - Consider 0.1" headers or loops

6. **Shielding**
   - Evaluate need for shield can over analog section

---

## Next Actions

1. **Today:**
   - [ ] Review and fix LM7805 thermal issue
   - [ ] Fix 74HC595 level compatibility

2. **This Week:**
   - [ ] Complete schematic finalization
   - [ ] Start PCB layout
   - [ ] Generate preliminary BOM

3. **Next Week:**
   - [ ] Complete PCB layout
   - [ ] Design review
   - [ ] Submit for fabrication

4. **Week 3:**
   - [ ] Receive PCBs
   - [ ] Assemble prototypes
   - [ ] Begin bring-up

---

**Let's get this PCB to fabrication!** 🎯
