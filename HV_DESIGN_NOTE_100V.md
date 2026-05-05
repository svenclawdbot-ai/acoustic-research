# HV Design Note — 100-200V Ultrasound Excitation

**Date:** 2026-04-21
**Issue:** DG408 cannot handle 100-200V pulser output
**Severity:** Critical — will destroy MUX and LNA if TX pulse reaches them

---

## The Problem

| Component | Max Voltage | Your Requirement | Result |
|-----------|-------------|------------------|--------|
| DG408 MUX | 40V single supply | 100-200V TX pulse | ❌ **Instant destruction** |
| OPA1641 LNA | ±18V (36V span) | 100-200V TX pulse | ❌ **Instant destruction** |
| IRF830 MOSFET | 500V | 100-200V TX pulse | ✅ OK |

**Current V5 schematic bug:** TX switch outputs connect directly to MUX inputs. During TX pulse, 100-200V goes straight into the DG408 and OPA1641.

---

## The Root Cause

In pulse-echo ultrasound (medical imaging style):
```
1. TX pulse (100-200V) → transducer
2. Same transducer → receives echo (<1mV to 100mV)
3. Echo → LNA → ADC
```

The **same element** is used for both TX and RX. During the TX pulse, the LNA must be protected. A **Transmit/Receive (T/R) switch** is required.

---

## Solution Options

### Option A: Add Passive T/R Switch (Recommended)

Use a **diode bridge T/R switch** — the medical ultrasound standard.

```
Transducer (SMA)
     │
     ├──┬──┐
     │  │  │
    D1 D2 D3 D4  ← 4× fast recovery diodes (e.g., MUR120, 200V, 50ns)
     │  │  │  │
     └──┼──┘  │
        │     │
   TX_PATH  RX_PATH
   (HV)      (DG408 MUX)
```

**How it works:**
- During TX: high current forward-biases diodes → pulse reaches transducer
- During RX: diodes are reverse-biased by a small DC bias current → echo passes to RX, TX path is isolated
- The "clamp" voltage at the RX port stays within ±0.6V of the bias point

**Components needed per channel:**
- 4× fast recovery diodes, 200V, 50ns (MUR120 or similar) — ~£0.30 each
- Bias resistor network (10kΩ + 100kΩ to ±5V or ±12V)

**Pros:**
- ✅ Proven in millions of medical ultrasound systems
- ✅ Passive — no control signals needed
- ✅ Protects RX path to <1V during TX
- ✅ Works to 200V+
- ✅ Fast recovery (<100ns)

**Cons:**
- ❌ Small insertion loss on RX (~1-2dB)
- ❌ Requires ± bias supply (can use 5V with resistive divider)
- ❌ Adds 4 diodes per channel = 32 diodes total

**Cost:** ~£12 for all 8 channels

---

### Option B: Active T/R Switch (Relay-Based)

Use small **signal relays** to physically connect transducer to TX or RX bus.

```
Transducer ── Relay ──┬─ TX bus (HV)
                      └─ RX bus (DG408 MUX)
```

**Relay options:**
- Panasonic TQ2-L2-5V — 2-pole, 5V coil, 250V switching, £2 each
- Coto 9011 reed relay — 200V, £1.50 each

**Control:** Extra 74HCT595 shift register (or use QH' cascade from existing one) to drive relay coils.

**Pros:**
- ✅ Perfect isolation (galvanic)
- ✅ Handles any voltage
- ✅ No insertion loss in RX

**Cons:**
- ❌ Slow: 5-10ms switching time
- ❌ Only suitable for sequential firing (not phased array)
- ❌ 8 relays = adds cost and board space
- ❌ Coil current: ~50mA per relay × 8 = 400mA extra load

**Cost:** ~£20-30 for 8 relays + driver circuit

---

### Option C: Hybrid — Separate TX and RX Elements

Don't share elements. Use:
- 4 elements dedicated TX only
- 4 elements dedicated RX only (or 8 RX elements for beamforming)

**Architecture:**
```
TX elements (4) ── IRF830 switches ── TX_IN
RX elements (4-8) ── DG408 MUX ── LNA ── RX_OUT
```

**No T/R switch needed!**

**Pros:**
- ✅ Simplest electronics
- ✅ No HV protection needed on RX
- ✅ Can do true beamforming on RX

**Cons:**
- ❌ Need 2× transducers (or 2× elements in one housing)
- ❌ Can't do pulse-echo on same element (some NDE techniques need this)
- ❌ Larger probe head

---

### Option D: Reduce Voltage to 40V (Accept Shorter Depth)

Keep V5 as-is but limit pulser to 40V max.

**Trade-off:**
- 40V into tissue: ~4-6 cm imaging depth (acceptable for superficial)
- 100V into tissue: ~10-15 cm imaging depth (full abdominal)

**Pros:**
- ✅ No design changes
- ✅ Safer
- ✅ Lower power

**Cons:**
- ❌ Reduced depth penetration

---

## Recommended Architecture for 100-200V

```
TX_IN (SMA, from RP DAC + HV pulser)
    │
    ├── IRF830 TX Switch (×8) ← 74HCT595 Q0-Q7
    │
    └──┬──┬──┬──┬──┬──┬──┬──┬── TX buses (100-200V)
       │  │  │  │  │  │  │  │
      T/R Switch (×8) ← diode bridge, 200V
       │  │  │  │  │  │  │  │
    TX/RX elements (×8 transducers)
       │  │  │  │  │  │  │  │
      T/R Switch (×8)
       │  │  │  │  │  │  │  │
       └──┴──┴──┴──┴──┴──┴──┴── RX buses (low voltage echoes)
                                  │
                            DG408 MUX (×2)
                                  │
                            OPA1641 LNA (×2)
                                  │
                            RX0/RX1 SMA outputs
```

**Key additions to V5 BOM:**

| Item | Qty | Unit | Line | Notes |
|------|-----|------|------|-------|
| MUR120 fast recovery diode | 32 | £0.30 | £9.60 | T/R bridge, 200V, 50ns |
| 10kΩ resistor | 16 | £0.01 | £0.16 | Bias network |
| 100kΩ resistor | 16 | £0.01 | £0.16 | Bias network |
| 1N4148 small signal diode | 8 | £0.02 | £0.16 | Bias clamp |
| BZX84C5V1 Zener | 8 | £0.05 | £0.40 | Bias regulation |

**T/R switch subtotal:** ~£11

---

## Updated V5 Schematic Changes

### Required:
1. [ ] Remove direct connection between TX switch output and MUX input
2. [ ] Add T/R switch block between each transducer and the TX/RX buses
3. [ ] MUX inputs connect to RX bus only (post-T/R switch)
4. [ ] Add bias supply for T/R switches (can derive from 5V rail with resistive divider)

### Analog Sheet Topology:
```
TX_IN (HV) ── IRF830 ── TX_BUS
                          │
                    T/R Switch (diode bridge)
                          │
                    TX/RX Element (SMA)
                          │
                    T/R Switch (diode bridge)
                          │
                    RX_BUS ── DG408 MUX ── LNA
```

---

## HV Pulser Note

The Red Pitaya DAC outputs ±1V max. To get 100-200V, you need an external **HV pulser**:

**Options:**
1. **DIY MOSFET pulser** — 2× IRF830 in totem-pole + gate driver (MD1210 or similar) — £15-20
2. **Off-the-shelf** — MD1210 + TC6320 evaluation board — £80-120
3. **Custom transformer** — Step-up transformer 1:100 from RP DAC — £5-10 but complex

The pulser is a separate subsystem from the MUX/LNA board. It connects to:
- TX_IN on the TurboQuant board
- Trigger input from RP DIO (pin 14 on E1)

---

## Decision Required

| Option | Depth | Complexity | Cost | Speed |
|--------|-------|------------|------|-------|
| A: Passive T/R + 100-200V | 10-15 cm | Medium | +£11 | Standard |
| B: Relay T/R + 100-200V | 10-15 cm | High | +£25 | 5-10ms switching |
| C: Separate TX/RX elements | 10-15 cm | Medium | +4 transducers | Standard |
| D: Limit to 40V | 4-6 cm | Low | £0 | Standard |

**My recommendation:** Option A — diode bridge T/R switch. It's the medical ultrasound industry standard, passive (no extra control logic), and adds only £11 to the BOM.

---

*Flagged: April 21, 2026*
*Action required: Confirm T/R switch approach before PCB layout*
