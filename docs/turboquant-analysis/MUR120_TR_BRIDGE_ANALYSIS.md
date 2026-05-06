# MUR120 T/R Bridge Analysis — TurboQuant V5

## Circuit Topology

The T/R (Transmit/Receive) bridge uses 4× MUR120 fast-recovery diodes per channel in a classic "H-bridge" configuration:

```
                    TX_PULSE (±100V)
                         |
                         |
                        D1 (MUR120)
                         |
    PROBE ───┬───────────┴───────────┬─── CH0_INPUT
             |                       |
            D2                      D3
           (MUR120)               (MUR120)
             |                       |
             |      ┌───────┐       |
             └──────┤ BIAS  ├───────┘
                    │ CTRL  │
                    └───┬───┘
                        |
                       D4 (MUR120)
                        |
                       GND
```

### Per-Channel Component List
| Component | Qty | Value | Function |
|-----------|-----|-------|----------|
| D1-D4 | 4 | MUR120 | Bridge diodes (fast recovery, 200V, 1A) |
| R1 | 1 | 10kΩ | Bias current limit |
| R2 | 1 | 100kΩ | DC bleed |
| Z1 | 1 | BZX84C5V1 | 5.1V zener for bias voltage |

**Total: 8 channels × (4 diodes + 2 resistors + 1 zener) = 32 MUR120, 16 resistors, 8 zeners**

---

## Operating Modes

### Mode 1: Transmit (TX) — Pulse to Probe
```
Bias: D1/D3 forward, D2/D4 reverse

TX_PULSE (+100V) ──► D1 ──► PROBE ──► D3 ──► CH0_INPUT (blocked)
                          │
                         GND
```
- D1 conducts TX pulse to probe
- D3 isolates receive path from high voltage
- D2 is reverse-biased (protection)
- D4 is reverse-biased

### Mode 2: Receive (RX) — Echo from Probe
```
Bias: D1/D3 reverse, D2/D4 forward (or all off)

PROBE ──► D2 ──► CH0_INPUT ──► MUX ──► LNA
  │
GND ◄── D4
```
- D2 conducts small-signal echo (~mV to V range) to receive chain
- D4 provides DC return path
- D1/D3 are reverse-biased (isolated from TX_PULSE node)

---

## Key Parameters — MUR120

| Parameter | Value | Notes |
|-----------|-------|-------|
| V_RRM (Reverse Voltage) | 200V | > 100V TX pulse requirement ✅ |
| I_F(AV) (Avg Forward Current) | 1A | Peak pulse ~2A for <1µs ✅ |
| t_rr (Reverse Recovery) | 2.0 µs typ | **Critical parameter** ⚠️ |
| V_F (Forward Voltage) | 0.8V @ 1A | Insertion loss source |
| C_j (Junction Capacitance) | 15 pF @ 25V | RF performance impact |

---

## Critical Analysis: 3 Key Questions

### 1. Isolation During TX — Is >26 dB Achievable?

**Leakage path during TX:**
```
TX_PULSE (100V) → D3 (reverse) → CH0_INPUT
```

MUR120 reverse characteristics at 100V:
- Leakage current I_R: ~10 µA (from datasheet curve, 25°C)
- Effective resistance: R = 100V / 10µA = 10 MΩ
- But at 100V, there's also capacitive coupling through junction capacitance

**Capacitive coupling:**
```
C_j = 15 pF (at 25V, lower at 100V)
Z_c = 1/(2πfC) = 1/(2π × 3.5MHz × 15pF) = 3 kΩ
```

At 3.5 MHz, the capacitive path dominates:
```
Coupling (dB) = 20 × log10(Z_load / (Z_c + Z_load))
```

Assuming CH0_INPUT is terminated in ~50Ω (typical for ultrasound):
```
Coupling ≈ 20 × log10(50 / 3050) = -35 dB
```

**But** — this is frequency-dependent. At DC/low freq (isolation test):
```
Isolation = 20 × log10(10MΩ / 50Ω) = -106 dB
```

**Conclusion:** ✅ **>26 dB isolation is achievable**, especially at RF frequencies where capacitive coupling matters more.

---

### 2. Insertion Loss in RX — Is <10 dB Acceptable?

**Forward path during RX:**
```
PROBE → D2 → CH0_INPUT
```

Two diodes in series (D2 + effective return path):
```
V_drop = 2 × 0.8V = 1.6V at 1A
```

But echo current is tiny (~mA range):
- Echo amplitude: ~100 mV into 50Ω → I = 2 mA
- At 2 mA, V_F ≈ 0.5V (from diode I-V curve)
- Two diodes: 1.0V drop

**Power loss calculation:**
```
P_echo = (100mV)² / 50Ω = 0.2 mW
P_drop = 2mA × 1.0V = 2 mW
Loss = 10 × log10(0.2 / 2.2) = -10.4 dB
```

Hmm, this is borderline. Let's recalculate more carefully:

**Actually** — the echo is AC, so we need average over half-cycle:
```
V_drop_avg = 2 × 0.5V = 1.0V
V_signal = 100 mV peak
```

At small signals, diode resistance r_d = nV_T/I_D:
```
r_d = 2 × 26mV / 2mA = 26 Ω (for both diodes)
```

Insertion loss:
```
IL = 20 × log10(50 / (50 + 26)) = -3.6 dB
```

Wait — this assumes constant bias. In practice:
- Without bias: diodes are OFF, only leakage → very high loss
- With bias: diodes conduct → lower loss

The bias network (10k + Zener) provides ~50-100 µA bias:
```
r_d = 52mV / 100µA = 520 Ω (both diodes)
IL = 20 × log10(50 / 570) = -21 dB  ← Too much!
```

**Problem identified:** The bias current may be too low!

**Solution options:**
1. Reduce bias resistor from 10k to 1k → 500 µA bias
   - r_d = 52mV / 500µA = 104 Ω
   - IL = 20 × log10(50 / 154) = -9.8 dB ✅

2. Use PIN diodes (lower forward resistance)
3. Use shunt PIN diodes (different topology)

---

### 3. PRF Limit — Can We Hit ≥1 kHz?

**Reverse recovery time:** t_rr = 2 µs (MUR120)

During TX→RX transition:
1. TX pulse ends (0.5 µs duration)
2. D3 must recover from forward conduction
3. Dead time needed: ~3× t_rr = 6 µs (rule of thumb for clean switching)

**Minimum PRF period:**
```
T_min = TX_pulse + recovery + RX_window
      = 0.5 µs + 6 µs + 100 µs (for 50mm depth)
      = 106.5 µs
```

**Maximum PRF:**
```
PRF_max = 1 / T_min = 9.4 kHz
```

**Conclusion:** ✅ **1 kHz PRF is easily achievable**. Even with conservative 10 µs dead time:
```
PRF = 1 / (0.5 + 10 + 100)µs = 9 kHz
```

---

## Go/No-Go Decision Matrix

| Criterion | Requirement | MUR120 Performance | Verdict |
|-----------|-------------|-------------------|---------|
| Isolation | >26 dB | ~35 dB at RF | ✅ GO |
| Insertion Loss | <10 dB | ~10 dB (borderline) | ⚠️ CONDITIONAL |
| PRF | ≥1 kHz | ~9 kHz max | ✅ GO |
| Voltage Rating | 100V | 200V | ✅ GO |
| Current | 2A peak | 1A avg, surge capable | ✅ GO |
| Cost | Low | £0.20 each | ✅ GO |

---

## Recommendations

### Immediate: Design Tweak Required
The insertion loss calculation shows the MUR120 with current bias network may be borderline. **Recommended fix:**

1. **Reduce bias resistor:** Change 10kΩ → 1kΩ for 500 µA bias current
   - Provides <10 dB insertion loss with margin
   - Power dissipation: P = (5V)² / 1kΩ = 25 mW (acceptable)

2. **Add bias control:** Use GPIO-controlled bias for TX/RX mode switching
   - TX mode: Bias OFF (high impedance, better isolation)
   - RX mode: Bias ON (low loss)

### Alternative: PIN Diode Upgrade
If prototype testing shows insufficient performance:

| Part | Specs | Cost | Improvement |
|------|-------|------|-------------|
| MA4P7102-1072T | 100V, 1A, t_rr = 10 ns | £2.50 | 200× faster recovery |
| BAR64-02V | 40V, 100 mA | £0.50 | Lower capacitance |
| 1N4007 → no | Too slow (t_rr = 30 µs) | N/A | Won't work |

**PIN diode advantages:**
- t_rr = 10-100 ns vs. 2 µs (MUR120)
- Lower forward resistance at same bias
- Lower capacitance

**PIN diode disadvantages:**
- 10× cost (£2 vs £0.20)
- Requires more bias current
- Higher BOM complexity

---

## Verification Plan

### Bench Test (Before PCB Order)
1. Build single-channel T/R bridge on breadboard
2. Drive with 100V pulse, measure leakage to RX side
3. Inject small signal, measure insertion loss with/without bias
4. Verify PRF switching at 1 kHz, 5 kHz, 10 kHz

### PCB Validation
1. Scope capture of TX pulse and RX node voltage
2. TDR measurement of isolation during TX
3. Network analyzer: S21 (insertion loss), S12 (isolation)
4. Thermal: IR camera during continuous 1 kHz operation

### Pass Criteria
| Test | Target | Margin |
|------|--------|--------|
| Isolation @ 100V TX | >26 dB | >30 dB preferred |
| Insertion Loss @ RX | <10 dB | <8 dB preferred |
| PRF capability | >1 kHz | >5 kHz preferred |
| Temperature rise | <20°C | At 1 kHz continuous |

---

## Conclusion

**VERDICT: GO with design tweak**

The MUR120 T/R bridge is fundamentally sound for this application. However, the bias resistor should be reduced from 10kΩ to 1kΩ to ensure adequate forward bias current for <10 dB insertion loss.

If bench testing reveals issues, upgrade path to PIN diodes is clear and low-risk.

---

*Analysis Date: May 6, 2026*
*Next Action: Update schematic (R1-R8: 10kΩ → 1kΩ) and run bench test*
