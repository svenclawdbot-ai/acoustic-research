# Single Transducer Shear Wave Elastography Setup
## Complete System Specification

**Date:** 2026-03-18  
**Configuration:** 1× Transmit/Receive Transducer + Support Hardware  
**Application:** ARFI Shear Wave Elastography + Phantom Imaging

---

## SYSTEM OVERVIEW

```
[PC/USB] ←→ [Digitizer/Scope] ←→ [Pulser/Receiver] ←→ [Matching Network] ←→ [Transducer]
                                                              ↓
                                                         [Phantom/Tissue]
```

**Signal Flow:**
1. PC triggers pulse generation
2. Pulser sends HV spike to transducer
3. Transducer transmits + receives echoes
4. Receiver amplifies returned signal
5. Digitizer captures waveform
6. PC processes for imaging/dispersion

---

## COMPONENT 1: TRANSDUCER

### Primary Recommendation: Ceramtec (Germany)

| Specification | Value |
|--------------|-------|
| **Material** | PIC 181 (PZT-5H equivalent) |
| **Frequency** | 3.5 MHz ±5% |
| **Aperture** | 19 mm diameter |
| **Focal Depth** | 40 mm (f/2.1) |
| **Housing** | Brass or stainless |
| **Connector** | BNC (preferred) or SMA |
| **Expected Price** | £200–250 |
| **Lead Time** | 3–4 weeks |

**Email:** medical@ceramtec.de

**Alternative:** Ultran (Poland) — £150–200, 2–3 weeks

---

## COMPONENT 2: PULSER/RECEIVER

### Option A: Echomods / Un0rick (Recommended)

| Spec | Value |
|------|-------|
| **Source** | kelu124 on Tindie/Hackaday |
| **HV Pulse** | ±100V, <50ns rise time |
| **PRF** | Up to 10 kHz |
| **Receiver** | LNA + protection switches |
| **ADC** | 20 MSPS, 12-bit |
| **Interface** | Raspberry Pi or USB |
| **Price** | £80–120 |
| **Lead Time** | 2–3 weeks (PCB + assembly) |

**Why recommended:**
- ✅ Open source, community support
- ✅ Python software included
- ✅ Modular (upgrade ADC later)
- ✅ Designed for exactly this application

**Where to buy:**
- Tindie: Search "un0rick" or "echomods"
- GitHub: github.com/kelu124/echomods

### Option B: DIY Arduino Pulser (Budget)

| Spec | Value |
|------|-------|
| **HV** | 100–200V |
| **Circuit** | Arduino + MOSFET + pulse transformer |
| **Components** | £40–50 |
| **Build Time** | 1 day |

**Reference:** "A Pulse Generator Based on an Arduino Platform for Ultrasonic Applications" — Physics Procedia 70 (2015): 1096-1099

### Option C: Commercial Pulser/Receiver

| Product | Specs | Price |
|---------|-------|-------|
| Olympus 5072PR | HV pulser + LNA | £1,500+ |
| JSR Ultrasonics DPR300 | Research grade | £2,000+ |
| Interspec/Novatron | Various | £800–1,500 |

**Not recommended for budget builds.**

---

## COMPONENT 3: DIGITIZER / OSCILLOSCOPE

### Option A: USB Oscilloscope (Recommended)

| Product | Specs | Price |
|---------|-------|-------|
| **Hantek 6022BE** | 20 MHz, 48 MSPS | £60–80 |
| **PicoScope 2204A** | 10 MHz, 50 MSPS | £100–120 |
| **PicoScope 3403D** | 50 MHz, 100 MSPS | £300–400 |

**Why USB scope:**
- ✅ Direct computer interface
- ✅ Python control (pico-sdk, libusb)
- ✅ Sufficient for 3.5 MHz (Nyquist = 7 MHz minimum)
- ✅ Affordable

### Option B: Raspberry Pi + ADC HAT

| Component | Specs | Price |
|-----------|-------|-------|
| **Raspberry Pi 4** | 4GB RAM | £55 |
| **ADC HAT (HiFiBerry)** | 24-bit audio | £30 |
| **Custom ADC** | AD9200 20 MSPS | £20 |

**Already have from previous equipment list?**

### Option C: Used Bench Scope

| Product | Specs | Price | Source |
|---------|-------|-------|--------|
| **Tektronix TDS 1002** | 60 MHz, 2-ch | £100–150 | eBay |
| **Keysight DSOX1102G** | 70 MHz, 2-ch | £200–250 | eBay |
| **Rigol DS1054Z** | 50 MHz, 4-ch | £200 | Amazon |

**Better for visual debugging, less convenient for automation.**

---

## COMPONENT 4: MATCHING NETWORK

### Series Inductor Tuning

For your 3.5 MHz transducer (~25Ω) to 50Ω system:

| Component | Value | Purpose |
|-----------|-------|---------|
| **L_series** | 6.5 μH | Cancel capacitive reactance |
| **C_parallel** | 10–50 pF trimmer | Fine tuning |

**Implementation:**
- Fixed inductor: Coilcraft 0603HP or similar (£2)
- OR wind your own: 20 turns on T37-2 toroid
- Mount in small enclosure near transducer connector

### Simple T-Network (Optional)

For better bandwidth:
```
Transducer --[L]--+-- 50Ω cable
                  [C]
                  |
                 GND
```

**Calculate values:** Use Smith chart or online matching calculator

---

## COMPONENT 5: PHANTOM MATERIALS

### Gelatin Phantom (Start Here)

| Component | Amount | Cost | Source |
|-----------|--------|------|--------|
| **Gelatin 300 bloom** | 500g | £12 | Amazon/Special Ingredients |
| **Graphite powder** | 100g | £8 | Amazon (art supply) |
| **Glycerin** | 500ml | £5 | Pharmacy |
| **Mold (Tupperware)** | 2L | £5 | Supermarket |
| **Total** | | **£30** | |

**Recipe (soft tissue, ~5 kPa):**
- 100g gelatin + 900ml water + 10g graphite
- Microwave to dissolve, pour, refrigerate 4h

### CIRS Phantom (Professional)

| Product | Specs | Price |
|---------|-------|-------|
| **CIRS 040GSE** | Multi-purpose | £800–1,200 |
| **CIRS 050** | Cardiac | £600–900 |

**Consider for final validation, not for development.**

---

## COMPONENT 6: MECHANICAL SETUP

### Positioning Stage (Optional but Recommended)

| Option | Specs | Price |
|--------|-------|-------|
| **Manual XYZ stage** | Thorlabs PT1/M | £200 |
| **DIY stepper stage** | 3D printed + NEMA17 | £50 |
| **Simple fixture** | Clamp + ruler | £0 |

**For:** Beam profiling, repeatable positioning

### Water Tank

| Option | Specs | Price |
|--------|-------|-------|
| **Plastic container** | 20L, clear | £10 |
| **Acoustic tank** | Custom | £50–100 |

**Requirements:**
- Clear sides for visual alignment
- Large enough for focal depth (40mm) + clearance
- Flat bottom for reflector

---

## COMPLETE SHOPPING LIST

### Essential (£400–500)

| Priority | Item | Cost | Source |
|----------|------|------|--------|
| 🔴 | **Transducer (Ceramtec)** | £200–250 | Email tonight |
| 🔴 | **Echomods pulser/ADC** | £90 | Tindie |
| 🔴 | **USB Scope (PicoScope)** | £100–120 | Amazon/Pico |
| 🟡 | **Matching components** | £10 | RS/Farnell |
| 🟡 | **Gelatin phantom** | £30 | Supermarket/Amazon |
| 🟡 | **Cables (BNC, coax)** | £20 | Amazon |
| 🟢 | **Water tank** | £10 | Supermarket |
| **Total** | | **£460–530** | |

### Optional Upgrades (£200–300)

| Item | Cost | When |
|------|------|------|
| XYZ positioning stage | £200 | For beam profiling |
| Better scope (50 MHz) | £150 | If bandwidth issues |
| CIRS phantom | £800 | Final validation |
| Impedance analyzer | £500 | Characterization |

---

## SETUP VERIFICATION CHECKLIST

### Before First Pulse

- [ ] All connections correct (pulser → transducer → receiver → scope)
- [ ] Transducer immersed in water (degassed)
- [ ] Flat reflector at known distance (e.g., 40mm)
- [ ] Scope triggered on pulse
- [ ] Gain set appropriately (start low!)

### First Pulse

- [ ] Transmit pulse visible on scope
- [ ] Echo returns at expected time
  - Time = 2×distance / speed_of_sound
  - 40mm → ~52 μs in water
- [ ] No ringing artifacts (backing working)
- [ ] Signal saturates? → Reduce gain or move reflector

### Imaging Check

- [ ] Move reflector, echo time changes correctly
- [ ] Add phantom, see speckle pattern
- [ ] Anechoic cyst visible (if phantom has one)

### Shear Wave Check

- [ ] Push pulse generates displacement
- [ ] Shear wave arrival detected
- [ ] Speed measurement reasonable (~1–5 m/s in soft tissue)

---

## SOFTWARE PIPELINE

### Data Acquisition

**Python with PicoSDK:**
```python
import picoscope

# Configure scope
scope = picoscope.PicoScope()
scope.set_channel('A', range='100mV')
scope.set_trigger('A', threshold=0.1)

# Capture
data = scope.capture_block(samples=10000)
```

**Or with Echomods:**
```python
import un0rick

# Initialize
dev = un0rick.UN0RICK()
dev.set_period(100)  # PRF
data = dev.capture()  # Single acquisition
```

### Processing (Your Existing Code)

1. **Signal conditioning** — Bandpass, denoise
2. **Displacement estimation** — Loupas or Kasai algorithm
3. **Shear wave tracking** — Peak detection, time-of-flight
4. **Dispersion extraction** — k-ω or phase gradient
5. **Inversion** — Recover G', η

---

## TIMELINE TO FIRST IMAGE

| Week | Activity | Deliverable |
|------|----------|-------------|
| **1** | Order transducer + hardware | Quotes sent, orders placed |
| **2** | Receive echomods/scope | Hardware in hand |
| **3** | Build matching network, set up tank | Mechanical ready |
| **4** | First pulse, debug | Echo visible |
| **5** | Phantom imaging | B-mode images |
| **6** | Shear wave detection | Displacement curves |
| **7+** | Optimize, characterize | Publication data |

**Assuming 3–4 week lead time on transducer.**

---

## NEXT STEPS (TONIGHT)

1. **Email Ceramtec** — Request quote for transducer
2. **Order echomods pulser** — From Tindie (search "un0rick")
3. **Order PicoScope 2204A** — Amazon or Pico directly
4. **Order matching components** — RS/Farnell (inductors, capacitors)
5. **Order gelatin materials** — Amazon

**Total order tonight:** ~£400

---

**Document created:** 2026-03-18  
**Next:** After system working, plan hybrid array expansion
