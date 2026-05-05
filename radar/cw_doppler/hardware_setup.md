# CW Doppler Radar — Hardware Setup Guide

## Development Path: Start Simple, Scale Up

| Phase | Hardware | Cost | Goal |
|-------|----------|------|------|
| **1. Baseband** | Red Pitaya + cables | £0 extra | Prove signal chain |
| **2. Desk 2.4 GHz** | + LNA + patch antennas | +£40 | Detect hand motion |
| **3. Through-wall** | + PA + directional antennas | +£80 | Detect people through drywall |
| **4. Bistatic** | Second Red Pitaya | +£250 | Covert surveillance |

---

## Phase 1: Baseband Mode (Immediate — No Extra Hardware)

### Setup

```
Red Pitaya DAC OUT1 ──[SMA cable]──► IN1  (loopback with 30 dB attenuator)
```

Or for spatial separation:
```
Red Pitaya DAC OUT1 ──[SMA cable + wire dipole ~2.5m]──► (tx antenna)
Red Pitaya ADC IN1  ──[SMA cable + wire dipole ~2.5m]──► (rx antenna)
```

At 30 MHz, wavelength λ = 10 m. A quarter-wave monopole = 2.5 m. That's a long wire — drape it across your desk or use a shorter loaded antenna.

### Expected Results
- **No target:** Clean noise floor, spectrum flat
- **Hand waving between antennas:** Small Doppler peak at ~0.2 Hz (30 MHz, 1 m/s hand motion)
- **Person walking nearby:** Very low frequency shifts, hard to see at 30 MHz

### Limitations
- Doppler shift is tiny: fd = 2·v·f/c = 0.2 Hz per m/s at 30 MHz
- Antennas are large
- But it **proves the software works** without buying anything

---

## Phase 2: 2.4 GHz ISM (Recommended Next Step)

### Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Red Pitaya  │     │  2.4 GHz     │     │   TX Patch   │
│  DAC OUT1    │────►│  Upconverter │────►│   Antenna    │
│  (30 MHz IF) │     │  (mixer+PLL) │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
                                                │
                                                │ RF path
                                                │
┌──────────────┐     ┌──────────────┐     ┌────▼─────────┐
│  Red Pitaya  │     │  2.4 GHz     │     │   RX Patch   │
│  ADC IN1     │◄────│  Downconverter│◄────│   Antenna    │
│  (30 MHz IF) │     │  (mixer+PLL) │     │   + LNA      │
└──────────────┘     └──────────────┘     └──────────────┘
```

Red Pitaya generates a 30 MHz IF tone. External mixer with 2.37 GHz LO shifts it to 2.4 GHz RF.

### Simplified Single-Mixer Architecture

Actually, a simpler approach for CW Doppler:

```
                          ┌─────────────┐
┌──────────┐   LO        │   Power     │        ┌──────────┐
│  ADF4351 │─────────────►│   Splitter  │───────►│  TX Ant  │
│  2.4 GHz │              │             │        └────┬─────┘
│  PLL     │              └─────────────┘             │
└────┬─────┘                   │                      │
     │                        │ RF reflection        │
     │                        │                      │
     │                   ┌────▼─────┐           ┌─────▼─────┐
     │                   │  LNA     │           │  Target   │
     │                   │  SPF5189Z│           │  (person) │
     │                   └────┬─────┘           └───────────┘
     │                        │
     │                   ┌────▼─────┐
     └──────────────────►│  Mixer   │
                        │  (I/Q)   │
                        └────┬─────┘
                             │ IF = Doppler shift
                        ┌────▼─────┐
                        │ Red Pitaya│
                        │ ADC IN1  │
                        │ (baseband)│
                        └───────────┘
```

Wait — if we use the same LO for tx and rx (homodyne), and the LO is at 2.4 GHz, the Doppler shift gets mixed down to baseband directly. The Red Pitaya ADC captures the baseband I/Q signal.

But Red Pitaya can't generate 2.4 GHz directly. We need an external LO source.

### Option A: External LO + Passive Mixer (Recommended for learning)

**Components:**

| Item | Spec | Cost | Source |
|------|------|------|--------|
| ADF4351 PLL module | 35 MHz – 4.4 GHz, SPI control | £8-15 | AliExpress |
| Mini-Circuits ZAD-1+ | 2.4 GHz mixer | £15 | Digi-Key/Mouser |
| SPF5189Z LNA | 50–4000 MHz, 0.6 dB NF | £5-10 | AliExpress |
| 2.4 GHz patch antenna | 5 dBi directional | £5 each | AliExpress |
| 10 dB attenuator | SMA, 2W | £3 | AliExpress |
| SMA cables + splitter | 2-way resistive | £10 | AliExpress |
| **Total** | | **~£50-60** | |

**Connections:**
1. ADF4351 generates 2.4 GHz CW
2. Splitter sends LO to:
   - TX path: direct to TX antenna (via attenuator for impedance)
   - RX path: LO port of mixer
3. RX antenna → LNA → RF port of mixer
4. Mixer IF output → Red Pitaya ADC IN1 (via DC block if needed)
5. Red Pitaya runs as baseband digitizer (no TX needed from Red Pitaya in this config!)

Actually, if Red Pitaya isn't generating the LO, we just use it as a fast dual-channel ADC. The SDR transceiver bitstream may not be needed — we can use the standard oscilloscope/acquisition bitstream and capture raw ADC samples.

But the SDR transceiver gives us nice I/Q processing. Alternatively, we can use the standard Red Pitaya OS and write a custom server, or just use the ADC directly with Pavel Demin's playground/scope apps.

### Option B: Red Pitaya Generates IF, External Up/Down Converter

**Components:** Same as above +:

| Item | Spec | Cost |
|------|------|------|
| Second mixer | For upconversion from IF | £15 |
| IF filter | 30 MHz BPF | £5 |

Red Pitaya generates 30 MHz tone → upconverter → 2.4 GHz → tx antenna
Reflected signal → downconverter → 30 MHz IF → Red Pitaya ADC

This keeps the phase coherence between tx and rx because they share the same LO. This is the **classic homodyne radar**.

### Option C: Use Existing 2.4 GHz Source (Hack/Cheat Mode)

Use a cheap ESP8266 or nRF24L01+ module set to continuous wave mode as the tx source. Use Red Pitaya with a downconverter/mixer as rx.

- ESP8266 in test mode: free carrier at channel frequency
- nRF24L01+: can be configured to output continuous tone
- **Cost:** £2 for the module

Not elegant, but works for desk testing.

---

## Phase 3: Through-Wall with PA + Directional Antennas

To get through drywall (2-3 layers) with useful range (5-10 m):

### Additions

| Item | Spec | Cost |
|------|------|------|
| 2.4 GHz PA | +20 dBm output (e.g., SKY65366) | £15 |
| Directional patch or Yagi | 8-12 dBi | £10-20 |
| LNA with higher IP3 | Mini-Circuits ZX60-8008E | £40 |
| Variable attenuator | 0-30 dB, for loopback testing | £10 |

**Expected performance:**
- Tx power: +20 dBm (100 mW)
- Antenna gain: +10 dBi each = +20 dBi total
- Wall loss (drywall): ~3-6 dB per layer
- Human RCS at 2.4 GHz: ~0.1-1 m²
- **Range through 1 wall:** 5-10 m realistic

---

## Phase 4: Bistatic / Covert Mode

Two Red Pitayas or one Red Pitaya + RTL-SDR:

```
FM Radio Tower (100 MHz)
    │ broadcast signal
    ├───────► Reference antenna ──► Red Pitaya #1 (RX only)
    │
    └───────► Surveillance area target ──► Red Pitaya #2 (RX surveillance)
```

Cross-correlate the two signals. Target reflections show up as Doppler-shifted copies of the broadcast.

**Requires:**
- Two Red Pitayas or one + RTL-SDR
- Directional antennas aimed at tower and coverage area
- GPSDO or rubidium reference for coherence (or use same clock distribution)
- Processing: ambiguity function computation (computationally heavy)

---

## Antenna Notes

### 2.4 GHz Patch Antenna (DIY or Buy)

**Bought:** £5-10 on AliExpress, 5 dBi, 30° beamwidth

**DIY:** Copper tape on FR4:
- Patch: 30.5 mm × 37.5 mm
- Ground plane: 60 mm × 60 mm
- Substrate: 1.6 mm FR4 (εr ≈ 4.4)
- Probe feed: 10 mm from edge
- **Gain:** ~5-7 dBi

### Vivaldi (Tapered Slot) for UWB

If you upgrade to FMCW with wide bandwidth (e.g., 200 MHz), a Vivaldi gives wideband directional pattern.
- Frequency: 1-10 GHz
- Gain: 5-10 dBi
- Beamwidth: 40-60°
- **DIY:** PCB etch or copper foil on cardboard

---

## Red Pitaya SD Card Images

| Application | Image | Notes |
|------------|-------|-------|
| **SDR transceiver** | `red-pitaya-alpine-*-sdr-transceiver.zip` | Full SDR, TCP server, 0-60 MHz |
| **VNA** | `red-pitaya-alpine-*-vna.zip` | For antenna tuning/characterisation |
| **Playground** | `red-pitaya-alpine-*-playground.zip` | ADC/DAC raw access, good for custom dev |
| **Standard OS** | Red Pitaya 2.00 OS | Web oscilloscope, SCPI, Pavel's apps installable |

Download: https://github.com/pavel-demin/red-pitaya-notes/releases

---

## Testing Without Antennas (Desk Validation)

Before you build antennas, validate the chain with cable:

```
Red Pitaya OUT1 ──[30 dB attenuator]──► IN1
```

Or for the 2.4 GHz frontend:
```
ADF4351 LO ──[splitter]──┬──► TX port (with 20 dB attenuator)
                         └──► Mixer LO port
                         
Mixer IF output ──[DC block]──► Red Pitaya IN1
```

No antenna needed — you're testing mixer conversion gain, LO leakage, and that Red Pitaya sees the IF signal.

### Validation Steps
1. Flash SDR transceiver SD card
2. Connect loopback (OUT1 → IN1 via attenuator)
3. Run `python cw_doppler.py --mode baseband --no-plot`
4. You should see:
   - Stable power reading
   - Flat spectrum
   - No motion alarms
5. Now wave a hand near the cables — capacitive coupling change should trigger a small disturbance

---

## Safety Notes

- **2.4 GHz ISM:** 100 mW EIRP is legal in most jurisdictions without license. Stay under +20 dBm.
- **5.8 GHz:** Similar, but some countries restrict outdoor use.
- **Higher power:** Check local regulations. Through-wall radar is not explicitly regulated in most places, but high-power RF can interfere with WiFi/BT.
- **Privacy:** Only test in your own space or with explicit permission. Through-wall detection of neighbours without consent is illegal in most jurisdictions.

---

## Shopping List (Phase 2 — £50 Budget)

| Priority | Item | Est. Cost | Link Search |
|----------|------|-----------|-------------|
| 1 | ADF4351 PLL eval board | £10 | "ADF4351 module AliExpress" |
| 1 | SPF5189Z LNA module | £5 | "SPF5189Z LNA AliExpress" |
| 1 | 2.4 GHz patch antenna (2x) | £10 | "2.4GHz patch antenna SMA" |
| 1 | SMA cables (6x) | £10 | "SMA male cable 10cm" |
| 2 | Mini-Circuits ZAD-1+ mixer | £15 | "ZAD-1+ Digi-Key" |
| 2 | 10 dB SMA attenuator | £3 | "SMA attenuator 10dB" |
| 2 | Resistive splitter | £5 | "SMA resistive splitter 2-way" |

**Total Phase 2: ~£50-60**

Add Phase 3 (PA + directional): +£50
Add Phase 4 (second Red Pitaya): +£250
