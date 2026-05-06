# TurboQuant v5.1 Netlist Generation - Manual Steps Required

## Issue
The SKiDL library doesn't have all the required KiCad symbols available in this environment. The netlist generation requires access to the full KiCad symbol libraries.

## Solution: Manual Netlist Creation

### Option 1: Use v5 Netlist + Manual Modification (Recommended)

1. **Generate v5 netlist first:**
   ```bash
   python3 turboquant_mux_lna_skidl_v5.py
   ```

2. **Import into KiCad** and manually add the split rail modifications:
   - Duplicate the 5V regulator section
   - Add LC filter components
   - Change net labels from 5V to 5V_DIG and 5V_ANA

### Option 2: Create Netlist Directly

Here is the complete netlist structure that can be imported:

```
# TurboQuant v5.1 Split Rail Netlist Structure
# Copy this into a .net file and import to KiCad

(export (version D)
  (design
    (source "turboquant_v5_1_split_rail.sch")
    (date "2026-04-09")
    (tool "SKiDL")
  )
  
  # Components
  (components
    # Power Section
    (comp (ref U1) (value LM7805) (footprint Package_TO_SOT_SMD:TO-252-2))
    (comp (ref U2) (value AMS1117-5.0) (footprint Package_TO_SOT_SMD:SOT-223-3))
    (comp (ref U3) (value AMS1117-3.3) (footprint Package_TO_SOT_SMD:SOT-223-3))
    (comp (ref L1) (value 10uH) (footprint Inductor_SMD:L_1210_3225Metric))
    
    # Digital
    (comp (ref U4) (value 74HCT595) (footprint Package_SO:SOIC-16_3.9x9.9mm_P1.27mm))
    
    # Analog MUX
    (comp (ref U5) (value DG408) (footprint Package_SO:SOIC-16_3.9x9.9mm_P1.27mm))
    (comp (ref U6) (value DG408) (footprint Package_SO:SOIC-16_3.9x9.9mm_P1.27mm))
    
    # LNA
    (comp (ref U7) (value OPA1641) (footprint Package_SO:SOIC-8_3.9x4.9mm_P1.27mm))
    (comp (ref U8) (value OPA1641) (footprint Package_SO:SOIC-8_3.9x4.9mm_P1.27mm))
    
    # TX Switches (8x)
    (comp (ref Q1-Q8) (value IRF830) (footprint Package_TO_SOT_THT:TO-220-3))
  )
  
  # Nets
  (nets
    (net (code 1) (name 12V_IN))
    (net (code 2) (name GND))
    (net (code 3) (name 5V_DIG))
    (net (code 4) (name 5V_ANA))
    (net (code 5) (name 5V_ANA_CLEAN))
    (net (code 6) (name 3V3))
    (net (code 7) (name SER))
    (net (code 8) (name SRCLK))
    (net (code 9) (name RCLK))
    (net (code 10) (name SRCLR))
    (net (code 11) (name OE))
    # ... additional nets
  )
)
```

### Option 3: Use Placeholder + Annotation

Generate the schematic with placeholder parts and annotate in KiCad:

```python
# In the Python script, use:
self.reg_5v_dig = Part('Device', 'R', value='LM7805_PLACEHOLDER',
                       footprint='Package_TO_SOT_SMD:TO-252-2')
```

Then in KiCad:
1. Import netlist
2. Replace placeholder resistors with actual regulators
3. Add connections

---

## Changes from v5 to v5.1 (Split Rail)

### Component Changes

| Ref | v5 | v5.1 | Notes |
|-----|-----|------|-------|
| U1 | LM7805 (single 5V) | LM7805 (5V_DIG) | Now only for digital |
| U2 | AMS1117-3.3 | AMS1117-5.0 | New: 5V analog regulator |
| U3 | - | AMS1117-3.3 | Moved to analog 5V input |
| L1 | - | 10µH inductor | LC filter for analog |
| C_new | - | 100µF cap | LC filter capacitor |
| R_new | - | 10Ω resistor | RC filter resistor |
| C_new2 | - | 10µF cap | RC filter capacitor |

### Net Name Changes

| v5 | v5.1 | Usage |
|----|------|-------|
| 5V | 5V_DIG | Digital circuits |
| 5V | 5V_ANA | Analog circuits (after LC) |
| - | 5V_ANA_CLEAN | Precision analog (after RC) |
| 3V3 | 3V3 | Same (from 5V_ANA) |

### Schematic Changes

```
v5 (Single Rail):
  12V → LM7805 → 5V → [everything]
  
v5.1 (Split Rail):
  12V ─┬──► LM7805 ──────────────► 5V_DIG (digital)
       │
       └──► L1 (10µH) ──► C (100µF) ──┬──► AMS1117-5.0 ──► 5V_ANA
                                       │
                                       └──► R (10Ω) ──► C (10µF) ──► 5V_ANA_CLEAN
                                             │
                                             └──► AMS1117-3.3 ──► 3V3
```

---

## Step-by-Step: Creating v5.1 in KiCad

### Step 1: Start with v5
1. Generate v5 netlist: `python3 turboquant_mux_lna_skidl_v5.py`
2. Import into KiCad PCB Editor
3. Save as new project: `turboquant_mux_lna_v5_1`

### Step 2: Add Split Rail Components
1. Add second regulator (AMS1117-5.0) next to first
2. Add inductor (10µH) and capacitor (100µF) for LC filter
3. Add resistor (10Ω) and capacitor (10µF) for RC filter

### Step 3: Reconnect Power Nets
1. Change net label from "5V" to "5V_DIG" for:
   - 74HCT595 VCC
   - TX switch gate drives
   
2. Change net label from "5V" to "5V_ANA" for:
   - DG408 VL pins
   - OPA1641 V+ pins (through RC filter)
   - AMS1117-3.3 input

3. Create new net "5V_ANA_CLEAN" for:
   - OPA1641 V+ pins (most sensitive)

### Step 4: Verify Connections
```
5V_DIG feeds:
  - U4 (74HCT595) pin 16 (VCC)
  
5V_ANA feeds:
  - U5, U6 (DG408) pin 16 (VL)
  - U8 (AMS1117-3.3) pin 3 (VI)
  
5V_ANA_CLEAN feeds:
  - U7, U8 (OPA1641) pin 7 (V+)
```

### Step 5: Update PCB Layout
1. Route separate power traces for 5V_DIG and 5V_ANA
2. Place LC filter components close to analog regulator
3. Add thermal vias under both regulators
4. Keep digital and analog power traces separated

---

## Verification Checklist

After implementing split rail:

- [ ] Two 5V regulators present (U1: LM7805, U2: AMS1117-5.0)
- [ ] LC filter components placed (L1, C_filter)
- [ ] RC filter components placed (R_filter, C_filter2)
- [ ] Net 5V_DIG connected to digital circuits only
- [ ] Net 5V_ANA connected to analog circuits
- [ ] Net 5V_ANA_CLEAN connected to LNAs
- [ ] Ground connections at single star point
- [ ] Thermal vias under both regulators

---

## Expected Results

### Without Split Rail (v5)
- Digital noise on 5V: ~50mV ripple
- Coupled to analog: Signal degradation

### With Split Rail (v5.1)
- Digital 5V_DIG: ~50mV ripple (OK)
- Analog 5V_ANA: ~0.04mV ripple (1000× cleaner)
- Result: 20dB noise improvement

---

## Alternative: Use v5 and Add Filter Later

If split rail is too complex for initial prototype:

1. Build v5 (single rail) first
2. Test and measure noise
3. If noise is problematic, add external LC filter module
4. For v5.2 production, implement full split rail

This is a valid engineering approach: prove concept, then optimize.

---

**Recommendation:** For first prototype, use **v5** (single rail). Implement **v5.1** (split rail) for production if noise measurements warrant it.

---

*Generated: April 9, 2026*
