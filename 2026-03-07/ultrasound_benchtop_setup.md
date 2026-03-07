# Ultrasound Benchtop Experimental Setup
## Options for Validating Computational Shear Wave Elastography Models

**Project:** Multi-Frequency Shear Wave Elastography Research  
**Goal:** Desktop bench setup for experimental data to validate computational models  
**Target Budget:** £200-500 for complete system

---

## 🎯 EXPERIMENTAL REQUIREMENTS

### For Shear Wave Elastography, You Need:

1. **Ultrasound Transducer** — Transmit/receive pulses
   - Frequency: 1-5 MHz typical for tissue-like phantoms
   - Can use single-element for simplicity
   - Medical imaging probes work but expensive

2. **Pulse Generator / Pulser** — Create high-voltage excitation pulses
   - Needs ~50-200V pulses (ultrasound transducers are high-impedance)
   - Short pulse duration (50-200 ns typical)
   - Repetition rate: 1-10 kHz for imaging, lower for elastography

3. **Signal Acquisition** — Receive echoes
   - High-speed ADC: 10-40 MSPS (MegaSamples Per Second)
   - 8-12 bit resolution
   - Raspberry Pi-compatible preferred

4. **Phantom/Tissue Mimic** — Test medium
   - Gelatin or agar phantoms with known stiffness
   - Commercial tissue-mimicking materials

---

## 🔧 OPTION 1: Open-Source "Murgen" / "echomods" Kit (Recommended)

**Project:** kelu124's echomods  
**Website:** https://kelu124.gitbooks.io/echomods/  
**GitHub:** https://github.com/kelu124/echomods  
**Cost:** ~$300-500 (£250-400)

### What's Included:
- **High-voltage pulser board** (~$40)
- **20 MSPS ADC Raspberry Pi HAT** (~$50-80)
- **Analog front-end** (filtering, amplification)
- **Single-element transducer** (3.5-5 MHz, ~$30-50)
- **Open-source Python software**

### Advantages:
✅ Proven design, actively maintained  
✅ Compatible with Raspberry Pi  
✅ Full documentation and community support  
✅ Modular — can upgrade components  
✅ Can achieve B-mode imaging  

### For Shear Wave Elastography:
- Use pulser to generate acoustic radiation force impulses
- Track displacement with correlation techniques
- Extract shear wave propagation from echo data

### Components to Buy:
| Item | Supplier | Est. Price |
|------|----------|------------|
| Raspberry Pi 4 (4GB) | Raspberry Pi Direct | £55 |
| echomods Pulser Board | OSH Park/Tindie | £35 |
| 20MSPS ADC HAT | Hackaday Store | £45 |
| 3.5 MHz Transducer | Piezo Hannas (China) | £25 |
| Coaxial Cables | Amazon/eBay | £15 |
| **Total** | | **~£175** |

---

## 🔧 OPTION 2: Arduino-Based DIY Pulser (Budget)

**Paper:** "A Pulse Generator Based on an Arduino Platform for Ultrasonic Applications"  
**Source:** Physics Procedia, 2015  
**Cost:** ~£50-100

### Approach:
Use Arduino to generate logic pulses → gate driver → MOSFET → transformer → high voltage pulse

### Circuit Overview:
```
Arduino → Gate Driver (TC4427) → MOSFET (IRF830) → Pulse Transformer → Transducer
                                        ↑
                                   HV Supply (100-200V)
```

### Components:
| Component | Specs | Est. Price |
|-----------|-------|------------|
| Arduino Nano/UNO | Any | £10 |
| Gate Driver IC | TC4427, MCP1407 | £2 |
| MOSFET | IRF830, IRFP260 | £3 |
| Pulse Transformer | Custom or salvage | £5-15 |
| HV Supply Module | 100-200V DC-DC | £15-25 |
| Transducer | 1-5 MHz single element | £20-40 |
| ADC (optional) | MCP3002 (1MSPS) or AD9200 (20MSPS) | £5-30 |

### Advantages:
✅ Very low cost  
✅ Fully customizable  
✅ Learn analog electronics  

### Disadvantages:
❌ Requires electronics knowledge  
❌ May need debugging/tuning  
❌ Lower performance than dedicated kits  

### Your Existing Equipment:
- **Oscilloscope** (from your workshop list) — essential for debugging
- **Bench power supply** — for HV supply and biasing
- **Soldering station** — for assembly

---

## 🔧 OPTION 3: Commercial Ultrasonic Thickness Gauge (Hack)

**Product:** Commercial thickness gauges with analog output  
**Examples:** CNYST, Dakota, Olympus  
**Cost:** £150-300 (used/new)

### Approach:
- Buy affordable thickness gauge
- Tap into the transducer connector
- Use GPIO trigger + external ADC for acquisition

### Advantages:
✅ Reliable, proven hardware  
✅ Comes with transducer  
✅ Immediate working system  

### Disadvantages:
❌ Less flexible  
❌ May need reverse engineering  
❌ Limited control over pulse parameters  

### Where to Buy:
- Amazon: "Ultrasonic Thickness Gauge 5MHz" (~£150-200)
- eBay: Used industrial units (~£100-150)
- AliExpress: Chinese brands (~£80-120)

---

## 🔧 OPTION 4: USB Ultrasound Modules (Plug & Play)

**Product:** USB ultrasound OEM modules  
**Examples:** USB-UT, various OEM modules  
**Cost:** £300-600

### Approach:
- USB module handles pulser + ADC
- Control via Python/C++ library
- Connect your own transducer

### Advantages:
✅ Plug and play  
✅ No hardware development  
✅ Good documentation  

### Disadvantages:
❌ More expensive  
❌ Less educational value  
❌ May need Windows drivers  

### Vendors:
- **NDT Systems** (USA) — OEM modules
- **TecScan** (Canada) — USB-UT series
- **Krautkrämer** (Germany) — contact for OEM

---

## 🧪 PHANTOM / TISSUE MIMIC MATERIALS

For experimental validation, you need materials with known mechanical properties:

### DIY Gelatin Phantoms
**Recipe (from literature):**
- 300 bloom gelatin: 10-20% by weight
- Graphite powder: 1-2% (for scatterers, to get echoes)
- Water: remainder
- Refrigerate to set

**Properties:**
- Young's modulus: 5-50 kPa (adjust with concentration)
- Can embed stiff inclusions (rubber, harder gelatin)
- Low cost: ~£5 per phantom

### Commercial Phantoms
| Product | Supplier | Price | Notes |
|---------|----------|-------|-------|
| Multi-Purpose Ultrasound Phantom | CIRS / Gammex | £500-1500 | Professional grade |
| Elasticity QA Phantoms | CIRS | £800-2000 | Includes stiffness standards |
| Custom silicone phantoms | PhantomX | £200-500 | Made to order |

### DIY Polyacrylamide (Better Stability)
**Recipe:**
- Acrylamide/bis-acrylamide solution
- Ammonium persulfate (initiator)
- TEMED (catalyst)
- Silica particles (scatterers)

**Properties:**
- Tunable stiffness: 5-100+ kPa
- Long-term stable (unlike gelatin)
- Requires care (acrylamide is neurotoxic)

---

## 🧩 INTEGRATION WITH YOUR SETUP

### Existing Home Lab Equipment (From Your Notes):
- ✅ **Oscilloscope** — Debugging, signal verification
- ✅ **Bench power supply** — Powering circuits
- ✅ **Soldering station** — Assembly
- ✅ **Multimeter** — Circuit testing

### Additional Needed:
- Raspberry Pi 4 (if not already have)
- High-speed ADC board (for Option 1 or 2)
- Transducer(s)
- Phantom materials
- BNC cables, connectors

### Software Stack:
- **Python** — Main control + processing
- **NumPy/SciPy** — Signal processing
- **Matplotlib/Plotly** — Visualization
- **GPIO library** — Pi hardware control

---

## 💡 RECOMMENDED PATH FOR YOUR PROJECT

### Phase 1: Quick Start (Week 1)
**Goal:** Get something working fast

1. **Order:** echomods kit or components (~£200)
2. **Build:** Simple gelatin phantom (5 kPa = healthy liver, 20 kPa = fibrotic)
3. **Test:** Basic pulse-echo, verify signal chain works

### Phase 2: Shear Wave Setup (Week 2-3)
**Goal:** Generate and detect shear waves

1. **Modify pulser:** Add push-pulse capability (longer pulse for ARFI)
2. **Implement:** Speckle tracking algorithm (displacement estimation)
3. **Measure:** Shear wave speed in phantoms of different stiffness

### Phase 3: Validation (Week 4)
**Goal:** Compare experiment to simulation

1. **Match:** Phantom properties to simulation parameters
2. **Compare:** Measured vs simulated shear wave speed
3. **Analyze:** Sources of discrepancy (noise, artifacts, model limitations)

---

## 📋 SHOPPING LIST (Prioritized)

### Essential (Get First):
| Item | Purpose | Est. Price | Where |
|------|---------|------------|-------|
| 3.5 MHz ultrasound transducer | Transmit/receive | £25 | Piezo Hannas / Alibaba |
| High-voltage pulser board | Excite transducer | £35 | echomods / DIY |
| Raspberry Pi 4 + ADC HAT | Acquisition + control | £100 | Pi shop / HAT vendor |
| Gelatin + graphite | Make phantoms | £10 | Supermarket / Amazon |
| BNC cables + connectors | Signal routing | £20 | Amazon / RS |
| **Essential Subtotal** | | **~£190** | |

### Nice to Have:
| Item | Purpose | Est. Price |
|------|---------|------------|
| Second transducer (5 MHz) | Different frequency tests | £30 |
| Variable stiffness phantom set | Calibration standards | £100-200 |
| Mechanical shaker (50-500 Hz) | External vibration source | £50 |
| Temperature control chamber | Stable phantom properties | £50 |

---

## 📚 KEY REFERENCES

### Papers on DIY Ultrasound:
1. **kelu124 (echomods)** — Comprehensive open-source guide  
   https://github.com/kelu124/echomods

2. **"A Pulse Generator Based on an Arduino Platform"** — Budget pulser design  
   Physics Procedia 70 (2015): 1096-1099

3. **"Hacking ultrasound with a DIY dev kit"** — Murgen project documentation  
   https://kelu124.gitbooks.io/echomods/

### Phantom Recipes:
4. **"Tissue-mimicking materials for ultrasound elastography"** — Gelatin/silicone recipes  
   IEEE Trans. Ultrason. Ferroelectr. Freq. Control

5. **"Polyacrylamide gel as an elastography phantom"** — Stable phantom material  
   J. Acoust. Soc. Am.

---

## 🎯 IMMEDIATE NEXT STEPS

1. **Decide on approach:**
   - Fastest: echomods kit (Option 1)
   - Cheapest: Arduino DIY (Option 2)
   - Easiest: Commercial thickness gauge (Option 3)

2. **Order transducer:**
   - Source: Piezo Hannas (China) or Alibaba
   - Spec: 3.5 MHz, single element, unfocused or weakly focused
   - Cost: £20-40

3. **Make first phantom:**
   - Try 10% gelatin + 1% graphite
   - Pour into plastic container (tupperware)
   - Test stiffness by feel (should jiggle like firm Jell-O)

4. **Set up GitHub repo:**
   - Upload your computational model
   - Track experimental progress
   - Document findings

---

## 💬 QUESTIONS TO CONSIDER

1. **Budget preference?** £100 DIY vs £300 kit vs £500 commercial?
2. **Time available?** Weekend project vs ongoing research?
3. **Phantom access?** Happy to DIY gelatin or want to buy commercial?
4. **Frequency needs?** Medical imaging (3-5 MHz) or deeper penetration (1-2 MHz)?
5. **Shear wave source?** ARFI (acoustic push) or external mechanical shaker?

---

*Document created: March 7, 2026*  
*For: Acoustic NDE Research Project — Experimental Validation Phase*
