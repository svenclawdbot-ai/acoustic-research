# 2.4 GHz CW Doppler Frontend — Complete Hardware Stack

Homodyne radar at 2.4 GHz using Red Pitaya as the baseband digitiser.

## Architecture Overview

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   ADF4351   │      │  Resistive  │      │   TX Patch  │
│   PLL @     │──────►│  Splitter   │──────►│   Antenna   │
│   2.4 GHz   │      │  (-6 dB)    │      │   (+5 dBi)  │
│   (0 dBm)   │      └──────┬──────┘      └─────────────┘
└─────────────┘             │
                            │
                            ├──► [10 dB attenuator] ──► LO port
                            │                         (to mixer)
                            │
                            └──► [Optional PA] ──► High-power TX
                            │    (for through-wall)
                            │
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Red Pitaya│      │  Baseband   │      │   LT5560    │
│   IN1 (I)   │◄─────│  Buffer Amp │◄─────│   I output  │
│   IN2 (Q)   │◄─────│  (G=10)     │◄─────│   Q output  │
└─────────────┘      └─────────────┘      │   IQ Demod  │
                                          │   RF input  │◄──┐
                                          └─────────────┘   │
                                                            │
                                          ┌─────────────┐   │
                                          │    LNA      │   │
                                          │  SPF5189Z   │───┘
                                          │  (+20 dB)   │
                                          └──────┬──────┘
                                                 │
                                          ┌──────▼──────┐
                                          │   RX Patch  │
                                          │   Antenna   │
                                          │   (+5 dBi)  │
                                          └─────────────┘
```

**How it works:**
1. ADF4351 generates a stable 2.4 GHz CW tone
2. Splitter feeds TX antenna (for illumination) and mixer LO port (for downconversion)
3. RX antenna picks up reflected signal
4. LNA boosts weak reflection (~-80 to -60 dBm typical)
5. LT5560 IQ demodulator mixes RF with LO → baseband I/Q Doppler signal
6. Buffer amps match level to Red Pitaya ADC (±1V)
7. Red Pitaya captures I/Q at 100 kSPS → software extracts Doppler spectrum

**Key advantage:** Single LO, perfectly phase-coherent tx/rx. Doppler shift appears directly at baseband.

---

## Block-by-Block Design

### 1. LO Source — ADF4351 PLL Module

**Why:** Red Pitaya can't generate 2.4 GHz. We need a stable, tunable LO.

**Module specs (typical AliExpress/Ebay board):**
- Frequency: 35 MHz – 4.4 GHz
- Output: ~0 to +5 dBm (varies with frequency)
- Control: SPI (3.3V logic)
- Power: 3.3V, ~100 mA
- Reference: onboard 25 MHz TCXO (±0.5 ppm)
- Cost: £8-15

**SPI wiring to Red Pitaya:**
```
RP DIO0_N (pin 1 on E1) ──► ADF4351 LE  (latch enable)
RP DIO1_N (pin 2 on E1) ──► ADF4351 CLK (SPI clock)
RP DIO2_N (pin 3 on E1) ──► ADF4351 DATA (SPI MOSI)
RP GND ───────────────────► ADF4351 GND
RP 3.3V ──────────────────► ADF4351 VCC
```

Red Pitaya E1 connector has 3.3V GPIOs perfect for this.

**Programming:**
- Use the Python `spidev` library or bit-bang SPI from Red Pitaya
- Set registers for 2.400 GHz output
- Many GitHub repos have pre-calculated register values: search "ADF4351 python"

**Example register set (2.400 GHz, 25 MHz ref):**
```python
# Simplified — real values depend on your module's TCXO and filter settings
REGISTERS = [
    0x00580000,  # Register 5
    0x008C802C,  # Register 4
    0x000004B3,  # Register 3
    0x00004E42,  # Register 2
    0x08008011,  # Register 1
    0x00420000,  # Register 0 (INT=96, FRAC=0 → 96 × 25 MHz = 2.400 GHz)
]
```
*Note: Check your specific ADF4351 module documentation. Values vary by board layout and TCXO frequency.*

---

### 2. Power Splitter / Distribution

**Options:**

| Type | Cost | Pros | Cons |
|------|------|------|------|
| Resistive 2-way | £3 | Ultra-wideband, cheap | 6 dB loss + 3 dB split = -9 dB total |
| Wilkinson 2-way | £8 | Lower loss (~3.5 dB), better isolation | Narrowband, needs 2.4 GHz optimisation |
| Mini-Circuits ZX10R-2-42+ | £35 | Lab quality, -3.2 dB, high isolation | Expensive |

**Recommendation:** Start with resistive. At 2.4 GHz, a Wilkinson is worth it if you can source one cheaply.

**With resistive splitter:**
- ADF4351 output: 0 dBm
- After splitter: -9 dBm each port
- TX path: -9 dBm → antenna (weak, but enough for desk tests)
- LO path: -9 dBm → LT5560 needs -10 to +5 dBm ✓ (works!)

---

### 3. TX Path — Antenna + Optional PA

**For desk testing (0.5–2 m range):**
- Direct from splitter to antenna: -9 dBm EIRP
- Add 10 dB attenuator if too strong (prevents mixer overload from leakage)

**For through-wall (3–10 m range):**
Need more power. Add PA.

**PA Options at 2.4 GHz:**

| Part | Gain | Pout | Cost | Source |
|------|------|------|------|--------|
| SPF2243 module | +20 dB | +20 dBm (100 mW) | £3-5 | AliExpress |
| SKY65135-11 eval | +28 dB | +28 dBm (630 mW) | £8 | AliExpress |
| RA07M4047 | +40 dB | +40 dBm (10 W) | £15 | AliExpress |

**Recommendation:** SPF2243 for £3. +20 dBm (100 mW) is the legal ISM limit in most countries. Good for 5-10 m through drywall.

**PA placement:**
```
Splitter ──► [SPF2243 PA] ──► [BPF 2.4 GHz] ──► [10 dB pad] ──► TX Antenna
```
The 10 dB pad improves PA stability (reduces VSWR effects). BPF suppresses harmonics.

---

### 4. RX Path — LNA

**Required:** Reflections from a person at 2.4 GHz are incredibly weak.

**Link budget example (2 m line-of-sight):**
```
TX power:        +20 dBm (with PA)
TX antenna gain: +5 dBi
Path loss (2m):  -40 dB  (FSPL = 20·log10(4π·2/0.125) ≈ 36 dB, add margin)
Target RCS:      -10 dBsm (human at 2.4 GHz)
RX antenna gain: +5 dBi
RX signal:       +20 + 5 - 40 - 10 + 5 = -20 dBm

Without PA (0 dBm TX):
RX signal:       0 + 5 - 40 - 10 + 5 = -40 dBm
```

At 10 m through a wall:
```
Path loss (10m):      -60 dB
Wall loss (drywall):  -6 dB (2 layers)
RX signal (with PA):  +20 + 5 - 60 - 6 - 10 + 5 = -46 dBm
```

The LT5560 mixer needs ~-20 dBm RF for good SNR (its NF is ~10 dB). So we need LNA gain of +20-30 dB before the mixer.

**LNA: SPF5189Z Module**
- Frequency: 50 MHz – 4 GHz
- Gain: +18-20 dB typical at 2.4 GHz
- NF: ~0.6 dB
- Cost: £3-5
- Power: 3.3-5V, ~100 mA

**Cascaded RX chain:**
```
RX Antenna ──► SPF5189Z (+20 dB) ──► LT5560 mixer
Noise figure ≈ 0.6 dB + (10 dB - 20 dB)/linear ... ≈ 1.5 dB total NF
```

Excellent. This is a quiet front-end.

---

### 5. IQ Demodulator — LT5560

**Why LT5560:**
- True I/Q demodulator (internal 90° LO splitter)
- Wideband: 40 MHz – 4 GHz RF
- Low LO drive: -10 to +5 dBm (works with our -9 dBm from resistive splitter)
- 3.3V supply
- SSOP-16 package (solderable by skilled hobbyist)
- Cost: £8-10

**Alternative if LT5560 unavailable:**
- **ADL5380:** Similar IQ demodulator, 400 MHz – 6 GHz, £10-15
- **Two ZAD-1+ mixers + 90° hybrid:** More complex, £30+ total
- **Tayloe detector / quadrature sampler:** DIY, very cheap but narrowband and needs precise timing

**LT5560 key pins:**
```
Pin 1 (RF+):  RX signal from LNA (AC coupled, 50Ω)
Pin 2 (RF-):  Ground reference (bias to Vcm)
Pin 7 (LO+):  LO from splitter (AC coupled, 50Ω)
Pin 8 (LO-):  Ground reference
Pin 13 (I+):  I output, DC coupled, ~0.5V common mode
Pin 14 (I-):  I output complement
Pin 15 (Q+):  Q output, DC coupled
Pin 16 (Q-):  Q output complement
Pin 3 (EN):   Enable (tie high)
Pin 5, 6 (V+): 3.3V supply
```

**Output levels:**
- Differential I/Q, ~0.5V common mode
- With -20 dBm RF input and 0 dBm LO, output is ~50 mVpp per channel
- Need amplification to reach Red Pitaya's ±1V range

---

### 6. Baseband Buffer Amplifier

**Requirements:**
- Gain: 10-20× (to bring 50 mVpp to ~500 mV – 1V pp)
- Bandwidth: DC to 10 kHz (Doppler is 0.1-100 Hz, but we want margin)
- Low offset: don't rail the ADC
- 3.3V capable (single supply)

**Option A: Precision Op-Amp (Recommended)**
```
OPA2197 dual op-amp:
- Low offset: ±250 µV max
- GBW: 10 MHz
- Rail-to-rail output
- 3.3V supply
- Cost: £3

Circuit: Non-inverting, G = 1 + R2/R1 = 11 (for G=10)
        R1 = 1kΩ, R2 = 10kΩ
        C1 (parallel R2) = 10 nF → low-pass at ~1.6 kHz (anti-alias)
```

**Option B: Cheap and Cheerful**
```
LMV358 dual op-amp:
- Offset: ±3 mV (may need trim pot)
- GBW: 1 MHz
- Cost: £0.50
- Works fine if you AC-couple or digitally subtract DC
```

**Recommended circuit (one channel shown):**
```
                    VCC 3.3V
                      │
                      │
LT5560 I+ ──[10µF]──┬──► (+) OPA2197 ──[100Ω]──► Red Pitaya IN1
         DC block   │    │  (non-inv)    │
                    └─[1k]┘               │
                      │                   │
                     GND               [10k]
                                        │
                                       GND
                                        
Feedback capacitor 10nF across 10kΩ gives 1.6 kHz LPF — fine for our 100 Hz max signal.
```

**DC coupling vs AC coupling debate:**
- **DC couple:** Keeps absolute phase information. But op-amp offset + mixer LO leakage DC can shift the baseline. Red Pitaya software HPF handles this.
- **AC couple (10µF + 100kΩ → 0.16 Hz HPF):** Removes DC offsets. Loses absolute phase but Doppler is relative anyway. Simpler, more robust.

**Recommendation:** AC couple with 10µF/100kΩ (0.16 Hz HPF). The software also has a digital HPF for redundancy.

---

### 7. Antennas

**TX and RX: 2.4 GHz Patch Antennas**

**Buy:** £5 each on AliExpress, 5 dBi, SMA connector, ~30° beamwidth.

**DIY (if you want):**
- Substrate: 1.6 mm FR4 (εr ≈ 4.4)
- Patch: 30.5 mm × 37.5 mm (rectangular for single polarisation)
- Ground plane: 60 mm × 60 mm
- Probe feed: 10 mm from patch edge
- SMA connector through ground plane
- **Gain:** ~5-7 dBi
- **Beamwidth:** ~60° E-plane, 70° H-plane

**Polarisation:**
- Use **same polarisation** on TX and RX for max reflection from flat surfaces
- Use **cross-polarisation** to reject direct path leakage (if tx/rx are close)
- For through-wall: vertical polarisation often penetrates better (less coupling to horizontal rebar)

**Placement for through-wall:**
```
TX antenna ──[0.5–2 m]──► Wall ──[1–5 m]──► Target
RX antenna ──[0.5–2 m]──► Wall ──[1–5 m]──► (same side as TX, looking at reflection)
```

TX and RX should be **side by side** (monostatic-like) or **separated by >1 m** (bistatic, reduces direct-path leakage).

---

## Complete BOM (Through-Wall Capable)

| Item | Spec / Part | Qty | Est. Cost | Source |
|------|-------------|-----|-----------|--------|
| **Red Pitaya** | STEMlab 125-14 | 1 | £250 | Red Pitaya store |
| **LO Source** | ADF4351 module, 2.4 GHz | 1 | £10 | AliExpress |
| **Splitter** | Resistive 2-way SMA | 1 | £3 | AliExpress |
| **TX PA** | SPF2243 2.4 GHz module | 1 | £4 | AliExpress |
| **RX LNA** | SPF5189Z module | 1 | £5 | AliExpress |
| **IQ Demod** | LT5560 SSOP-16 | 1 | £8 | LCSC / Digi-Key |
| **Baseband Amp** | OPA2197 dual SOIC-8 | 1 | £3 | Digi-Key |
| **Antennas** | 2.4 GHz patch, SMA, 5 dBi | 2 | £10 | AliExpress |
| **SMA cables** | 10 cm, 20 cm, 50 cm | 6 | £12 | AliExpress |
| **Attenuators** | 10 dB SMA | 2 | £4 | AliExpress |
| **DC Block** | SMA in-line (optional) | 1 | £3 | AliExpress |
| **3.3V reg** | AMS1117-3.3 (if needed) | 1 | £1 | AliExpress |
| **Passives** | Caps, resistors, PCBs | — | £5 | Local |
| **Enclosure** | ABS project box | 1 | £5 | AliExpress |
| | | | | |
| **TOTAL** | | | **£323** | |
| *(without Red Pitaya)* | | | **£73** | |

**Notes:**
- Prices are AliExpress estimates. Digi-Key/Mouser will be 2-3× for same parts.
- If you already have the Red Pitaya (for TurboQuant), total additional cost is ~£73.
- You can drop the PA for desk testing and save £4.

---

## Power Budget

| Block | Voltage | Current | Power |
|-------|---------|---------|-------|
| ADF4351 | 3.3V | 100 mA | 330 mW |
| SPF2243 PA | 3.3V | 150 mA | 500 mW |
| SPF5189Z LNA | 5V | 80 mA | 400 mW |
| LT5560 | 3.3V | 60 mA | 200 mW |
| OPA2197 | 3.3V | 5 mA | 17 mW |
| Red Pitaya | 5V | 800 mA | 4000 mW |
| **Total** | | | **~5.5 W** |

A single 5V/2A USB supply can power everything if you regulate down to 3.3V for the RF blocks. Or use separate 5V (RP + LNA) and 3.3V (LO + PA + mixer + amp) supplies.

---

## Build Order — Recommended Sequence

### Stage 1: Validate LO (1 hour)
1. Power up ADF4351 module
2. Program 2.400 GHz via SPI (use Arduino or RP GPIO)
3. Verify with cheap RTL-SDR or WiFi analyser app — look for peak at 2.4 GHz
4. Debug SPI timing if needed

### Stage 2: Validate RX Chain (2 hours)
1. Connect ADF4351 → splitter → LO port of LT5560
2. TX side: connect to antenna, place 2 m away
3. RX side: antenna → LNA → LT5560 RF
4. LT5560 I/Q outputs → Red Pitaya IN1/IN2 (direct, no amp first)
5. Flash standard Red Pitaya OS, use web oscilloscope
6. Wave hand in front of antennas — look for tiny AC signal on scope
7. Add baseband amp if signal too small

### Stage 3: Baseband Amp (1 hour)
1. Build op-amp circuit on breadboard or perfboard
2. Verify gain with function generator or just the mixer output
3. Check for oscillation (add supply decoupling caps 100nF + 10µF)

### Stage 4: CW Doppler Software (30 min)
1. Flash Pavel Demin's SDR transceiver SD card
2. Run `cw_doppler.py --mode baseband` (captures raw I/Q)
3. Verify spectrogram shows motion

### Stage 5: Through-Wall Test
1. Add PA to TX path
2. Aim at drywall from 2 m away
3. Walk behind wall — look for Doppler peak at 1-5 Hz
4. Tune PA gain and RX LNA gain for best SNR without overload

---

## Alternative: Simpler/Cheaper Options

### Option A: No IQ Demodulator (Single-Channel Real)
Replace LT5560 with a single passive mixer (Mini-Circuits ZAD-1+ or ZX05-43MH-S+).

**Pros:** Cheaper (£15 vs £8), simpler wiring  
**Cons:** Loses Q channel — can't distinguish approaching vs receding. Doppler magnitude only.

For motion detection ("is someone there?"), this is sufficient. Add the Q channel later if you need direction.

### Option B: No External LO (Use WiFi Router)
Place a WiFi router in continuous test mode (or just use beacon frames) as the illuminator. Red Pitaya with downconverter captures.

**Pros:** Free LO source  
**Cons:** Not pure CW (has modulation), harder to control power, not portable

### Option C: HB100 / CDM324 Module (£3)
Buy a ready-made Doppler radar module and just tap the IF output.

**HB100:** 10.525 GHz, built-in TX/RX/mixer, IF output  
**CDM324:** 24 GHz, better performance, longer range  
**RCWL-0516:** 5.8 GHz, some boards have baseband output

**Pros:** £3, works immediately, proven  
**Cons:** Fixed frequency, no I/Q, lower performance than custom build  
**Use:** Validate your Python processing chain while you build the 2.4 GHz stack

---

## Expected Performance

| Scenario | Range | Detection | Notes |
|----------|-------|-----------|-------|
| Desk test (LOS, no PA) | 0.5–2 m | Hand waving, breathing | Easy — proves chain |
| Room test (LOS, +20 dBm PA) | 5–10 m | Walking, breathing | Reliable detection |
| Through 1 drywall | 3–5 m | Walking | Breathing marginal, walking clear |
| Through 2 drywalls | 2–3 m | Walking only | Higher false alarm rate |
| Corner/oblique | 2–3 m | Walking | Reflection angle matters |

**Doppler frequencies at 2.4 GHz:**
- Breathing (chest movement 4-12 mm/s): 0.06 – 0.2 Hz
- Heartbeat (surface motion ~0.5 mm/s): 0.008 – 0.04 Hz (very hard)
- Walking (1-2 m/s): 16 – 32 Hz
- Arm waving (3-5 m/s): 48 – 80 Hz

At 2.4 GHz, λ = 12.5 cm. fd = 2v/λ.

---

## Safety & Legal

- **2.4 GHz ISM band:** Generally licence-free for low power
- **+20 dBm EIRP:** Legal limit in EU, US, most of world for ISM
- **Indoor use only:** Some jurisdictions restrict outdoor 2.4 GHz tx
- **Wall penetration:** Microwave radiation at 100 mW poses no health risk at these distances
- **Privacy:** Only test in your own property or with explicit written consent

---

## References

- LT5560 datasheet: https://www.analog.com/media/en/technical-documentation/data-sheets/5560f.pdf
- ADF4351 datasheet: https://www.analog.com/media/en/technical-documentation/data-sheets/ADF4351.pdf
- SPF5189Z datasheet: https://www.datasheetspdf.com/pdf/1399565/RFMD/SPF5189Z/1
- Red Pitaya E1 connector pinout: https://redpitaya.readthedocs.io/en/latest/developerGuide/hardware/125-14/extent.html
- HB100 teardown: https://www.ladyada.net/library/hb100/
