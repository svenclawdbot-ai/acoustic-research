# Critical PCB Issues - Action Required

**Board:** TurboQuant MUX/LNA v4  
**Status:** Schematic incomplete in KiCad (SKiDL source exists)  
**Priority:** 🔴 **BLOCKING FABRICATION**

---

## 🚨 CRITICAL: Must Fix Before Layout

### Issue 1: LM7805 Thermal Overload

**Problem:**
```
Power dissipation: P = (Vin - Vout) × Iload
                  = (12V - 5V) × 0.4A (8 channels @ 50mA)
                  = 2.8W

TO-220 thermal resistance: θJA = 54°C/W (no heatsink)
Temperature rise: ΔT = 2.8W × 54°C/W = 151°C
Ambient: 25°C → Junction: 176°C
Maximum: 125°C ❌ THERMAL RUNAWAY
```

**Solutions:**

| Option | Part | Efficiency | Cost | Effort |
|--------|------|------------|------|--------|
| A | Heatsink | N/A | $2 | 1h |
| B | LM2596 (switching) | 90% | $1 | 2h |
| C | Separate 5V supply | N/A | $5 | 4h |

**Recommendation: Option B (LM2596)**
- Drop-in replacement for LM7805
- 90% efficiency = only 0.3W dissipation
- No heatsink needed
- Pin-compatible (check pinout)

**Action:**
```python
# In turboquant_mux_lna_skidl.py, replace:
# OLD:
self.reg_5v = Part('Regulator_Linear', 'LM7805_TO220', ...)

# NEW:
self.reg_5v = Part('Regulator_Switching', 'LM2596T-5.0', 
                   footprint='Package_TO_SOT_THT:TO-220-5')
```

---

### Issue 2: 74HC595 Level Incompatibility

**Problem:**
```
ESP32 GPIO: 3.3V logic, VOH min = 2.64V (80% of 3.3V)
74HC595 VIH min: 3.5V (70% of 5V)

2.64V < 3.5V ❌ INCOMPATIBLE
```

**Symptoms:**
- Intermittent shifting
- Wrong data latched
- Unreliable operation

**Solutions:**

| Option | Approach | Cost | Effort |
|--------|----------|------|--------|
| A | Use 74HCT595 (TTL levels) | Same | 10 min |
| B | Use 74LV595 (3.3V) | Same | 10 min |
| C | Add level shifter | $0.50 | 30 min |

**Recommendation: Option A (74HCT595)**
- TTL input levels: VIH min = 2.0V ✓
- Pin-compatible with 74HC595
- Same speed, same drive strength
- Widely available

**Action:**
```python
# In turboquant_mux_lna_skidl.py, replace:
# OLD:
self.sr = Part('74xx', '74HC595', ...)

# NEW:
self.sr = Part('74xx', '74HCT595', ...)
```

---

### Issue 3: Analog MUX Voltage Range

**Problem:**
Need to verify what voltage range your ultrasound TX pulses are.

| Scenario | Voltage | MUX Required |
|----------|---------|--------------|
| Low-voltage | <15V | CD4051B OK |
| Medium | 15-30V | DG408 (30V) |
| High | 30-100V | DG408/DG409 (100V) |
| Very high | >100V | Custom HV switches |

**Action Required:**
- [ ] Check your pulser output voltage
- [ ] Update MUX selection accordingly

---

## 🟡 IMPORTANT: Should Fix

### Issue 4: Decoupling Capacitors

**Current:** 100nF on each regulator

**Recommended:**
```
LM7805/LM2596 input:  100μF electrolytic + 100nF ceramic
LM7805/LM2596 output: 10μF electrolytic + 100nF ceramic
AMS1117 input:        10μF ceramic
AMS1117 output:       10μF ceramic
Each IC VCC pin:      100nF ceramic (as close as possible)
```

---

### Issue 5: Pull-Down Resistors

**Missing:**
- [ ] MUX address lines (A/B/C) need 10kΩ pull-down to GND
- [ ] Shift register outputs should have pull-downs (optional)
- [ ] Control lines from E1 header: pull-ups or pull-downs

**Why:** Prevents floating inputs during power-up/reset

---

### Issue 6: Test Points

**Add test points for:**
- [ ] 12V rail
- [ ] 5V rail  
- [ ] 3.3V rail
- [ ] GND (multiple locations)
- [ ] MUX address lines (A/B/C)
- [ ] LNA outputs (pre- and post-)
- [ ] Shift register clock/data

**Format:** 0.1" header or TP pads (2mm diameter)

---

## 📋 Action Checklist

### Before PCB Layout (CRITICAL)
- [ ] **Fix LM7805 → LM2596** (30 min)
- [ ] **Fix 74HC595 → 74HCT595** (10 min)
- [ ] **Verify CD4051B voltage rating** (need info from you)
- [ ] **Add decoupling capacitors** (30 min)
- [ ] **Add pull-down resistors** (20 min)
- [ ] **Add test points** (30 min)

### PCB Layout Phase
- [ ] Complete schematic in KiCad
- [ ] Run ERC (Electrical Rule Check)
- [ ] Component placement
- [ ] Routing
- [ ] DRC (Design Rule Check)

### Manufacturing Prep
- [ ] Generate BOM
- [ ] Generate Gerbers
- [ ] Assembly drawings
- [ ] Design review

---

## 🎯 Priority Order

```
TODAY (Critical):
  1. Fix LM7805 → LM2596
  2. Fix 74HC595 → 74HCT595
  3. Verify MUX voltage rating

THIS WEEK:
  4. Complete schematic
  5. Add decoupling
  6. Add pull-downs
  7. Add test points

NEXT WEEK:
  8. PCB layout
  9. Design review
  10. Submit for fabrication
```

---

## 💬 Questions for You

1. **What voltage do your ultrasound pulsers output?**
   - This determines if CD4051B is sufficient or if you need HV MUX

2. **Do you have a preferred PCB manufacturer?**
   - JLCPCB (fast, cheap)
   - PCBWay (good quality)
   - Eurocircuits (European)

3. **Do you want SMT assembly service or self-assembly?**
   - JLCPCB PCBA is ~$30-50 extra but saves time
   - Self-assembly requires hot plate + microscope

4. **Any mechanical constraints?**
   - Enclosure size?
   - Mounting hole locations?
   - Connector placement (front panel vs board edge)?

---

## 📁 Files to Update

| File | Action |
|------|--------|
| `turboquant_mux_lna_skidl.py` | Fix LM7805, 74HC595, add caps/resistors |
| `kicad/turboquant_mux_lna_v4/` | Import netlist, layout PCB |
| `PCB_FINALIZATION_CHECKLIST.md` | Check off items as complete |

---

**Time to fix critical issues: ~2 hours**
**Time to complete PCB: ~1 week**

Ready to start? Let's fix those critical issues first! 🔧
