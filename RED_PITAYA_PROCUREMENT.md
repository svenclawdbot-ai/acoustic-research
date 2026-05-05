# Red Pitaya Procurement — Ultrasound Mux Board Project

**Date:** March 27, 2026
**Target:** 8-element ultrasound array with Red Pitaya STEMlab

---

## ORDER 1 — Red Pitaya (Core Platform)

| # | Item | Spec | Supplier | Cost | Lead |
|---|------|------|----------|------|------|
| 1 | **STEMlab 125-14 Gen 2** | 2×ADC/DAC 125 MSa/s 14-bit, Zynq 7010 | redpitaya.com | **£250** | 3-5 days |

**Model:** STEMlab 125-14 Gen 2 (standard) — **CONFIRMED**

**Direct link:** https://redpitaya.com/product/stemlab-125-14/

**What it gives you:**
- 2× RF inputs (ADC): 125 MSa/s, 14-bit, ±1V / ±20V (selectable), **-75 dB noise floor**
- 2× RF outputs (DAC): 125 MSa/s, 14-bit, **±2V @ Hi-Z** (Gen 2 improvement)
- USB-C connector (3A power delivery)
- 16× DIO (3.3V) on extension connectors E1/E2
- Xilinx Zynq 7010 FPGA (dual ARM Cortex-A9 + FPGA fabric)
- Ethernet + USB for host connection
- Runs Linux (can SSH in, run Python directly on-board)

**Gen 2 advantages for this project:**
- ±2V output swing = stronger drive, no pre-amp stage needed
- Lower noise floor = relaxed LNA requirements
- USB-C = simpler power, modern interface
- 16× DIO (3.3V) on extension connectors E1/E2
- Xilinx Zynq 7010 FPGA (dual ARM Cortex-A9 + FPGA fabric)
- Ethernet + USB for host connection
- Runs Linux (can SSH in, run Python directly on-board)

---

## ORDER 2 — Mux Board Components (DIGI-KEY ORDER PLACED 28/03/2026)

**Status:** ✅ ORDERED — Digi-Key UK, standard shipping
**Order Total:** £68.26 (inc VAT & shipping)
**Expected Delivery:** March 31 — April 2, 2026

### Active ICs — ORDERED

| # | Item | Spec | Part # | Qty | Cost | Status |
|---|------|------|--------|-----|------|--------|
| 2 | **74HC595** | 8-bit shift register, DIP-16 | 296-1600-5-ND | 2 | £1.04 | ✅ Ordered |
| 3 | **CD4051BE** | 8:1 analog mux, DIP-16 | 296-2057-5-ND | 3 | £1.74 | ✅ Ordered |
| 4 | **AD8332** | Dual LNA/VGA (0-48 dB), ultrasound-specific | AD8332ARUZ-ND | 1 | £11.85 | ✅ Ordered |
| 5 | **BSS138** | N-channel MOSFET, SOT-23, 50V | BSS138-7-FCT-ND | 10 | £1.30 | ✅ Ordered |
| 6 | **LM7805** | 5V regulator, TO-220 | LM7805CT-ND | 2 | £1.56 | ✅ Ordered |
| 7 | **AMS1117-3.3** | 3.3V LDO, SOT-223 | AMS1117-3.3CT-ND | 2 | £1.04 | ✅ Ordered |

### Protection & Passives — ORDERED

| # | Item | Spec | Part # | Qty | Cost | Status |
|---|------|------|--------|-----|------|--------|
| 8 | **BAV99** | Dual series diode, SOT-23 | BAV99-7-F-ND | 10 | £1.10 | ✅ Ordered |
| 9 | **10kΩ resistor** | 1/4W, 1%, 0805 | 311-10.0KFRCT-ND | 50 | £1.00 | ✅ Ordered |
| 10 | **100Ω resistor** | 1/4W, 1%, 0805 | 311-100FRCT-ND | 50 | £1.00 | ✅ Ordered |
| 11 | **1kΩ resistor** | 1/4W, 1%, 0805 | 311-1.00KFRCT-ND | 50 | £1.00 | ✅ Ordered |
| 12 | **100nF ceramic** | 50V, 0805 | 311-100nFCT-ND | 50 | £1.50 | ✅ Ordered |
| 13 | **10µF electrolytic** | 25V | Various | 5 | £0.75 | ✅ Ordered |
| 14 | **1µF ceramic** | 16V, 0805 | 311-1.0uFCT-ND | 20 | £1.60 | ✅ Ordered |

### Connectors & Mechanical — ORDERED

| # | Item | Spec | Part # | Qty | Cost | Status |
|---|------|------|--------|-----|------|--------|
| 15 | **SMA edge-mount** | 50Ω, PCB | 732-5318-ND | 4 | £7.40 | ✅ Ordered |
| 16 | **2×20 pin header** | 2.54mm, for RP GPIO | S1011EC-40-ND | 2 | £2.40 | ✅ Ordered |
| 17 | **2-pin screw terminal** | 5.08mm, power input | ED10561-ND | 2 | £0.90 | ✅ Ordered |
| 18 | **Prototype PCB** | 100×70mm, double-sided | 377-2095-ND | 2 | £7.70 | ✅ Ordered |

---

## COST SUMMARY

| Category | Amount |
|----------|--------|
| Red Pitaya STEMlab 125-14 Gen 2 | £250.00 |
| Active ICs | £17.80 |
| Passives & Protection | £4.80 |
| Connectors & Mechanical | £28.80 |
| **TOTAL** | **£301.40** |
| Contingency (+10%) | £30.14 |
| **GRAND TOTAL** | **£331.54** |

---

## GPIO PIN MAPPING (Red Pitaya E1/E2 Connectors)

```
Red Pitaya E1 Connector (active analog/digital):
─────────────────────────────────────────────────
Pin  7 → DIO0_P → 74HC595 SER   (shift register data)
Pin  8 → DIO0_N → 74HC595 SRCLK (shift register clock)
Pin  9 → DIO1_P → 74HC595 RCLK  (storage register latch)
Pin 10 → DIO1_N → CD4051 A      (RX mux address bit 0)
Pin 11 → DIO2_P → CD4051 B      (RX mux address bit 1)
Pin 12 → DIO2_N → CD4051 C      (RX mux address bit 2)
Pin 13 → DIO3_P → RX_CH_SEL     (which CD4051 is active)
Pin 14 → DIO3_N → TRIGGER       (emission sync)

Power:
Pin 1  → 3V3 (from Red Pitaya)
Pin 2  → 3V3 (from Red Pitaya)
Pin 25 → GND
Pin 26 → GND
```

---

## NOTES

1. **BSS138 vs IRF830:** Using BSS138 (50V, SOT-23) for Rev 1 — sufficient for low-voltage testing. Swap to IRF830 (500V) if using HV pulser directly.

2. **AD8332 soldering:** It's TSSOP-20 — needs fine soldering. Alternative: use 2× OPA657 in DIP-8 for easier prototyping.

3. **SMA count:** 12 SMA connectors is expensive (£18). Alternative: use pin headers for element connections and only SMA for TX/RX to Red Pitaya. Saves ~£12.

4. **Rev 1 is low-voltage:** Test with Red Pitaya DAC output (±1V) directly into elements. Add HV pulser later as separate module.

5. **PCB vs stripboard:** For Rev 1 prototype, stripboard works. For Rev 2 (with HV), get a proper PCB from JLCPCB (~£5 for 5 boards).

---

## ORDERING CHECKLIST

- [ ] Order Red Pitaya STEMlab 125-14 from redpitaya.com
- [x] Place Digi-Key order (mux board components) — ORDERED 28/03/2026
- [ ] Download Red Pitaya OS image and flash SD card
- [ ] Test Red Pitaya basic I/O before building mux board
