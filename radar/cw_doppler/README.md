# CW Doppler Radar — Development Stack

Fastest path to proving Red Pitaya radar for security applications.

## Architecture

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Red Pitaya │──────│    Target   │──────│   Red Pitaya │
│   DAC OUT1   │  RF  │  (person,   │ refl │   ADC IN1    │
│   (tx tone)  │─────►│   object)   │─────►│   (rx + DDC) │
└─────────────┘      └─────────────┘      └──────┬──────┘
                                                  │
                                          I/Q baseband
                                                  │
┌─────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│  Python Processing (Linux/Windows/Mac)                       │
│  - High-pass filter (remove DC/static clutter)              │
│  - Spectrogram / FFT (detect Doppler shifts)                 │
│  - Phase unwrap (detect micro-motion: breathing)             │
│  - Energy detector (alarm on motion)                         │
└─────────────────────────────────────────────────────────────┘
```

## Two Modes

| Mode | Frequency | Hardware Needed | Use Case |
|------|-----------|-----------------|----------|
| **Baseband** | 10–50 MHz direct | Just Red Pitaya + wires | Prove signal chain, large object detection |
| **2.4 GHz ISM** | 2.4 GHz external | LNA + mixer/PLL frontend | Through-wall, person detection, breathing |

## Quick Start (Baseband Mode — No Extra Hardware)

### 1. Flash Red Pitaya

Download Pavel Demin's SDR transceiver SD card image:
```bash
wget https://github.com/pavel-demin/red-pitaya-notes/releases/download/20251012/red-pitaya-alpine-3.22-armv7-20251012-sdr-transceiver.zip
# Or copy to SD card via BalenaEtcher
```

### 2. Connect

```
Red Pitaya DAC OUT1 ──[SMA cable]──► (tx antenna or wire)
Red Pitaya ADC IN1  ──[SMA cable]──► (rx antenna or wire)
```

For desk testing without antennas:
```
OUT1 ──[30 dB attenuator]──► IN1
```
Move a metal object near the cable to create coupling changes.

### 3. Run Software

```bash
pip install -r requirements.txt
python cw_doppler.py --rp-ip 192.168.1.100 --mode baseband
```

## File Overview

| File | Purpose |
|------|---------|
| `rp_sdr_client.py` | TCP client for Red Pitaya SDR transceiver I/Q streaming |
| `cw_doppler.py` | Acquisition + real-time Doppler processing |
| `requirements.txt` | Python dependencies |
| `hardware_setup.md` | Frontend options and schematics |

## What You'll See

**Motion detection:** A peak appears in the spectrogram when you wave your hand.

**Breathing:** Low-frequency drift (< 0.5 Hz) in the phase trace when you sit near the antenna.

**Static environment:** Clean noise floor when nothing moves.

## Next Steps

1. Prove baseband motion detection (this stack)
2. Build 2.4 GHz frontend (`hardware_setup.md`)
3. Add FMCW chirp generator (custom FPGA bitstream)
4. Through-wall testing with 2.4 GHz + directional antennas

---

## References

- Pavel Demin SDR transceiver: https://pavel-demin.github.io/red-pitaya-notes/sdr-transceiver/
- OpenSourceRadar: https://github.com/OpenSourceRadar
- CW radar basics: https://www.radartutorial.eu/01.basics/Continuous%20Wave%20Radar.en.html
