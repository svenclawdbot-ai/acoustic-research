# Transducer Fabrication Guide
## 3.5 MHz Focused Transducer — Step-by-Step Build

**Design:** TR-3.5-PHANTOM-001  
**Aperture:** 19 mm | **Focal Depth:** 40 mm (f/2.1)  
**Estimated Time:** 6–8 hours (spread over 2–3 days for curing)

---

## PRE-BUILD CHECKLIST

### Workspace Setup
- [ ] Clean, dust-free area (kitchen table covered with newspaper works)
- [ ] Good lighting
- [ ] Ventilation for epoxy work
- [ ] Access to oven or hot plate for curing
- [ ] All tools laid out and clean

### Tools Required
| Tool | Purpose | Alternative |
|------|---------|-------------|
| Digital scale (0.01g) | Weigh powders | None — essential |
| Digital calipers (0.01mm) | Measure thickness | None — essential |
| Vacuum chamber + pump | Degas epoxy | None — essential |
| Soldering station | Electrical connections | 25W iron minimum |
| Helping hands | Hold parts while soldering | Stack of books |
| Tweezers (fine tip) | Handle PZT | Needle-nose pliers (careful) |
| Mixing cups (30ml) | Epoxy mixing | Disposable plastic cups |
| Wooden stirrers | Mix epoxy | Popsicle sticks |
| Syringes (10ml) | Epoxy application | Pipettes |
| Kimwipes/lint-free wipes | Cleaning | Coffee filters |
| Isopropyl alcohol (99%) | Degreasing | Acetone (hardware store) |
| Masking tape | Protect surfaces | — |

### Materials Check
- [ ] PZT-5H disc (19mm × 0.64mm) ×3
- [ ] Tungsten powder (5–10 μm)
- [ ] Epo-Tek 301 epoxy
- [ ] Alumina powder (Al₂O₃, 1–5 μm)
- [ ] Brass tube (20mm ID × 25mm OD)
- [ ] Concave PMMA lens (R=40mm)
- [ ] RG174/U coax cable
- [ ] SMA connectors
- [ ] Copper tape (conductive adhesive)
- [ ] Solder, flux
- [ ] Kapton tape

---

## PHASE 1: PZT PREPARATION (Day 1, Morning — 30 min)

### Step 1.1: Inspect PZT Crystal
**What:** Verify crystal quality before proceeding

1. **Visual inspection:**
   - Check for cracks, chips, or surface defects
   - Gold electrodes should be intact (shiny, no bare spots)
   - Thickness should be ~0.64mm (measure with calipers)

2. **Clean surface:**
   - Wipe with isopropyl alcohol on Kimwipe
   - Air dry (don't touch surface with fingers)

**Decision point:** If crystal is damaged, use spare. That's why you ordered 3.

### Step 1.2: Electrode Test (Optional but Recommended)
**What:** Verify electrical continuity

1. Set multimeter to resistance (Ω) mode
2. Touch probes to top and bottom electrodes
3. Should read: **50–100 Ω** (typical for thin PZT)
4. If open circuit (∞) or very high (>1kΩ): crystal may be cracked internally

**If test fails:** Try another crystal

---

## PHASE 2: BACKING MATERIAL (Day 1, Morning — 1 hour + 24h cure)

### Step 2.1: Prepare Workspace
1. Lay down disposable covering
2. Set up vacuum chamber nearby (but not running yet)
3. Have scale, mixing cup, stirrer ready
4. **Wear nitrile gloves** — tungsten powder is not toxic but avoid inhalation

### Step 2.2: Mix Tungsten-Epoxy
**Ratio:** 3:1 by mass (tungsten:epoxy)

**For one transducer:**
| Component | Mass | Volume (approx) |
|-----------|------|-----------------|
| Tungsten powder | 9g | ~2.5 ml |
| Epo-Tek 301 Part A | 2g | ~2 ml |
| Epo-Tek 301 Part B | 1g | ~1 ml |
| **Total** | **12g** | **~5.5 ml** |

**Process:**
1. Weigh tungsten powder into mixing cup (record: ___ g)
2. Add Part A, mix thoroughly (2 minutes)
3. Add Part B, mix thoroughly (3 minutes)
   - Scrape sides and bottom
   - Mix until uniform gray paste

### Step 2.3: Vacuum Degas
**Critical step — do not skip**

1. Place mixing cup in vacuum chamber
2. Seal chamber, start pump
3. Watch for bubbling (air escaping)
4. Hold at full vacuum (~-0.08 MPa) for **5 minutes**
5. Release vacuum slowly

**What to watch for:**
- ✓ Mixture bubbles vigorously then settles
- ✗ If it boils over: too much air mixed in, remake batch

### Step 2.4: Apply Backing to PZT
**Target thickness:** 3–5 mm (not critical, just needs to be thick enough)

1. Place PZT disc on flat surface (clean glass or metal)
2. Use syringe or spatula to apply tungsten-epoxy to back surface
3. Spread evenly with spatula or card
4. Target thickness: ~3mm
5. **Check for voids:** Look for bubbles or bare spots

### Step 2.5: Cure Backing
**Option A:** Room temperature cure
- 24 hours at 20–25°C
- Cover to prevent dust

**Option B:** Accelerated cure
- 2 hours at 60°C (oven or hot plate)
- Then 12 hours at room temperature

**Do not disturb during cure** — vibrations cause voids

---

## PHASE 3: MATCHING LAYER (Day 2, Morning — 1 hour + 12h cure)

### Step 3.1: Check Backing Cure
**Before proceeding:**
- Backing should be hard (not tacky)
- No visible voids on surface
- Should not indent with fingernail

### Step 3.2: Prepare PZT with Backing
1. Clean front surface (PZT side) with isopropyl alcohol
2. Mask edges with tape if needed to control matching layer spread
3. Place on level surface, PZT side up

### Step 3.3: Mix Alumina-Epoxy Matching Layer
**Target impedance:** 3.0–3.5 MRayl  
**Target thickness:** 0.11 mm (λ/4 at 3.5 MHz)

**Ratio:** ~40% alumina by mass in Epo-Tek 301

**For one transducer:**
| Component | Mass |
|-----------|------|
| Alumina powder | 2g |
| Epo-Tek Part A | 2g |
| Epo-Tek Part B | 1g |

**Process:**
1. Mix alumina into Part A first (forms paste)
2. Add Part B, mix thoroughly (3 minutes)
3. **Vacuum degas** for 3 minutes

### Step 3.4: Apply Matching Layer
**Critical:** Thickness control to ±0.02 mm

**Method A: Spin Coating (if available)**
1. Mount PZT on spin coater chuck
2. Deposit matching layer at center (~0.2 ml)
3. Spin: 1000 RPM for 30 seconds
4. Measure thickness with calipers
5. Adjust RPM for target 0.11 mm

**Method B: Blade/Doctor Blade**
1. Apply small amount of mixture to PZT center
2. Use flat blade (razor blade, feeler gauge) at 45°
3. Drag across surface to spread to ~0.11 mm
4. Measure with calipers
5. If too thick: scrape excess; if too thin: add more

**Method C: Trial and Error (No tools)**
1. Apply thin layer by hand
2. Measure: calipers on edge
3. Target: 0.11 mm = thickness of 2–3 sheets of paper
4. Accept ±0.02 mm tolerance → frequency shift ±3%

### Step 3.5: Cure Matching Layer
- **12 hours** at room temperature
- Or **2 hours** at 60°C
- Keep level!

---

## PHASE 4: HOUSING FABRICATION (Day 2, Afternoon — 1 hour)

### Step 4.1: Prepare Brass Housing
**Dimensions:** 20mm ID × 25mm OD × 30mm L

1. Clean brass tube with alcohol
2. Deburr edges (file or sandpaper)
3. Cut to 30mm length if not pre-cut

### Step 4.2: Prepare Lens
**Concave PMMA lens:** R=40mm, 19mm clear aperture

1. Clean with alcohol
2. Check concave surface (should be smooth, no scratches)
3. Test fit: Should seat against brass tube end

### Step 4.3: Prepare PZT Stack
Now you have: PZT + backing (3mm) + matching layer (0.11mm)

1. Measure total thickness: should be ~3.75 mm
2. Clean all surfaces with alcohol
3. Handle by edges only

---

## PHASE 5: ASSEMBLY (Day 3 — 2 hours + 24h cure)

### Step 5.1: Bond PZT to Housing
1. Apply thin layer of epoxy to inside bottom of brass tube
2. Insert PZT stack (matching layer facing outward)
3. Center the PZT (should have ~0.5mm clearance all around)
4. Press gently to seat
5. **Check:** Matching layer should be flush with housing edge

### Step 5.2: Bond Lens to Housing
1. Apply thin epoxy bead to housing rim
2. Place concave lens (concave side facing OUT)
3. Center the lens
4. Press gently to spread epoxy
5. Wipe excess immediately

**Alignment check:**
- Lens center should align with PZT center
- Concave surface facing outward (toward tissue/phantom)

### Step 5.3: Cure Assembly
- 24 hours at room temperature
- Keep vertical (lens up) to prevent sag
- Or 4 hours at 60°C

### Step 5.4: Electrical Connections
**After housing is cured**

1. **Ground connection:**
   - Scrape small area of gold electrode on side of PZT
   - Solder wire to ground electrode (bottom/back)
   - Use flux, minimal heat (PZT is heat-sensitive)

2. **Signal connection:**
   - Solder coax center conductor to top electrode
   - Keep solder joint small

3. **Shield connection:**
   - Solder coax braid to brass housing
   - This grounds the housing for EMI shielding

4. **Strain relief:**
   - Use Kapton tape to secure cable to housing
   - Leave slack inside housing

### Step 5.5: Potting (Optional but Recommended)
1. Mix small amount of potting epoxy
2. Fill housing cavity around solder joints
3. Cover to top of housing
4. Cure 24 hours

---

## PHASE 6: IMPEDANCE MATCHING (Day 4 — 30 min)

### Step 6.1: Add Series Inductor
**For tuning to 50Ω at 3.5 MHz**

Calculated: **6.5 μH**

1. Use fixed inductor (Digi-Key, Mouser)
2. Or wind your own: ~20 turns on T37-2 toroid
3. Solder in series with coax center conductor
4. Keep leads short (<5mm)

### Step 6.2: Optional Tuning Capacitor
For fine-tuning:
- Parallel 10–50 pF trimmer capacitor
- Adjust for minimum VSWR at 3.5 MHz

---

## PHASE 7: TESTING (Day 4 — 1 hour)

### Step 7.1: Visual Inspection
- [ ] No visible voids in backing
- [ ] Lens centered and secure
- [ ] No solder bridges
- [ ] Cable strain relief in place

### Step 7.2: Impedance Check
With impedance analyzer or simple setup:

1. **Expected:** 20–30 Ω (real part) at 3.5 MHz
2. **Acceptable range:** 15–50 Ω
3. **If too high (>100Ω):** Check solder joints, matching layer
4. **If too low (<10Ω):** Possible short — check for solder bridges

**Without analyzer:**
- Connect to signal generator + oscilloscope
- Apply 3.5 MHz, 10Vpp
- Should draw ~200–400 mA (check with current probe or series resistor)

### Step 7.3: Pulse-Echo Test
**Simple test in water:**

1. Fill container with water
2. Place flat reflector (metal plate) at ~40mm distance
3. Connect transducer to pulser/receiver
4. Send pulse, look for echo

**What to look for:**
- ✓ Clear echo at ~52 μs round-trip (40mm × 2 / 1540 m/s)
- ✓ Echo amplitude >10× noise
- ✗ No echo: Check connections, try different distance
- ✗ Double echoes: Backing insufficient (ring-down)

### Step 7.4: Bandwidth Check
With signal generator:

1. Sweep frequency: 1–6 MHz
2. Measure received amplitude at each frequency
3. Plot response
4. **Target:** -6dB points at ~1.5 and ~5.5 MHz (114% bandwidth)

**Without equipment:**
- Note qualitative: Does it work at 2 MHz? 5 MHz?

---

## TROUBLESHOOTING GUIDE

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| No echo | Open circuit | Check solder joints |
| Weak echo | Poor matching layer | Rebuild |
| Double echoes | Insufficient backing | Heavier backing next time |
| Ring-down artifacts | Backing voids | Vacuum degas better |
| Frequency off | Wrong matching thickness | Accept or rebuild |
| High impedance | Open connection | Check electrodes |
| Low impedance | Short circuit | Check for solder bridges |

---

## SUCCESS CRITERIA

Your transducer is successful if:
- [ ] Impedance: 15–50 Ω @ 3.5 MHz
- [ ] Echo visible from flat reflector at 40mm
- [ ] Bandwidth >80% (-6dB)
- [ ] No visible artifacts in pulse

**First build expectations:**
- 70% of specs met = Good learning experience
- 85% of specs met = Excellent first attempt
- 100% of specs met = You're a natural

---

## TIMELINE SUMMARY

| Phase | Activity | Time | Calendar |
|-------|----------|------|----------|
| 1 | PZT prep | 30 min | Day 1 AM |
| 2 | Backing | 1h + 24h cure | Day 1 AM → Day 2 AM |
| 3 | Matching layer | 1h + 12h cure | Day 2 AM → Day 2 PM |
| 4 | Housing prep | 1h | Day 2 PM |
| 5 | Assembly | 2h + 24h cure | Day 3 |
| 6 | Impedance match | 30 min | Day 4 |
| 7 | Testing | 1h | Day 4 |
| **Total** | | **~7h active** | **4 days** |

---

**Document created:** 2026-03-18  
**Next:** Procurement list (Phase 1 items for tonight)
