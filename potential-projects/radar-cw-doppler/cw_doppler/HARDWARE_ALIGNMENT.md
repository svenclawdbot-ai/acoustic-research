# Hardware Alignment — Radar + TurboQuant Ultrasound

What parts serve both projects? What skills transfer? Where do the designs diverge?

---

## The Shared Heart: Red Pitaya STEMlab 125-14

| Spec | Value | Ultrasound Use | Radar Use |
|------|-------|---------------|-----------|
| Zynq-7010 SoC | ARM + Artix-7 FPGA | Acquisition + control | SDR + chirp gen + de-chirp |
| 125 MSps ADC | 14-bit, 2 channels | 8-ch MUXed ultrasound | I/Q baseband capture |
| 125 MSps DAC | 14-bit, 2 channels | TX pulser trigger | FMCW chirp output |
| Network | 1 GbE | Remote control + streaming | Remote monitoring |
| GPIO | 16 DIO | MUX control (DG408) | Servo control |
| Cost | £250 | Core platform | Core platform |

**Key insight:** One Red Pitaya does **both** projects, just with different FPGA bitstreams. Swap SD cards to switch modes.

---

## Shared Hardware Inventory

### Already Ordered / Used for TurboQuant V5

| Item | TurboQuant Role | Radar Role | Dual-Use? |
|------|----------------|-----------|-----------|
| **Red Pitaya 125-14** | ADC for 8 ultrasound channels | SDR + digitiser | ✅ Core shared platform |
| **PicoScope 2206B** | Bring-up debug, verify signals | Verify baseband I/Q | ✅ Same use case |
| **Bench PSU (5V/3A)** | Power RP + PCB | Power RP + servos + amps | ✅ Same rail |
| **Soldering iron** | Assemble PCB | Build RF frontend | ✅ Same tool |
| **Multimeter** | Continuity, voltage | Voltage, bias checks | ✅ Same tool |
| **Breadboard** | Prototype circuits | Test filters, amps | ✅ Same |
| **Dupont jumpers** | Prototyping | RP GPIO connections | ✅ Same |
| **Anti-static mat** | Handle ICs | Handle LT5560, LNA | ✅ Same |
| **Tweezers** | Place SMD | Place SSOP-16 LT5560 | ✅ Same |
| **Flux + solder** | PCB assembly | RF module soldering | ✅ Same |
| **Wire stripper** | Cable prep | SMA cable prep | ✅ Same |
| **Side cutters** | Trim leads | Trim SMA connectors | ✅ Same |
| **Helping hands** | Hold PCB | Hold RF modules | ✅ Same |

**Shared tools value:** ~£125 (the Phase 0 workbench investment)

### Shared from Digi-Key PCB Order (TurboQuant V5)

| Component | TurboQuant Role | Radar Role | Dual-Use? |
|-----------|----------------|-----------|-----------|
| **74HCT595** | MUX control | Servo shift-register (alternative to GPIO PWM) | ⚠️ Different use |
| **DG408** | 8-ch ultrasound MUX | — | ❌ Ultrasound only |
| **LM7805 (DPAK)** | 5V regulation | Power LNA / PA | ✅ Same regulator |
| **Op-amps (various)** | LNA, buffer | Baseband buffer | ✅ Same family |
| **Passives (resistors/caps)** | Decoupling, feedback | Decoupling, feedback | ✅ Same stock |
| **SMA connectors** | Ultrasound transducer | RF frontend | ✅ Same connectors |
| **MUR120 diodes** | T/R switch | — | ❌ Ultrasound only |
| **IRF830** | TX switch | — | ❌ Ultrasound only |
| **BAV99** | Clamping | — | ❌ Ultrasound only |

**Op-amp crossover:** If you bought OPAx189 or similar precision op-amps for TurboQuant's analog chain, some can sub for the OPA2197 baseband buffer. Check specs (bandwidth, offset).

### Shared Skills & Knowledge

| Skill | TurboQuant | Radar | Transfer Value |
|-------|-----------|-------|-----------------|
| **Vivado FPGA design** | Block design, AXI, DMA | Chirp generator, de-chirp, CIC | 🔥 Direct reuse |
| **Verilog HDL** | MUX controller | DDS, complex multiplier | 🔥 Same language |
| **Python + NumPy** | Post-processing, k-ω | Doppler extraction, CFAR | 🔥 Same stack |
| **Red Pitaya ecosystem** | SCPI, DMA, web apps | SDR transceiver, custom server | 🔥 Same platform |
| **Signal processing** | Dispersion curves, FFT | Spectrogram, beat frequency | 🔥 Same math |
| **PCB layout** | 4-layer mixed-signal | Simple 2-layer RF | ⚠️ Different rules |
| **Analog frontend design** | Ultrasound T/R, LNA, HV | RF LNA, mixer, PA | ⚠️ Different frequencies |
| **Mechanical** | Transducer array mounting | Servo pan-tilt bracket | ⚠️ Different scale |

**The FPGA work is the biggest win.** The `v5_red_pitaya_bd.tcl` you built yesterday — AXI interconnect, DMA, GPIO, HP0 — is the **exact same skeleton** the FMCW chirp generator needs. You're not starting from scratch.

---

## Hardware Unique to Radar

Items the radar needs that TurboQuant doesn't:

| Item | Cost | Why Radar Needs It | Why Ultrasound Doesn't |
|------|------|-------------------|----------------------|
| **ADF4351 PLL** | £10 | Generate 2.4 GHz LO | Ultrasound is baseband (kHz–MHz) |
| **LT5560 IQ demod** | £8 | Mix 2.4 GHz to baseband | Ultrasound is already baseband |
| **SPF5189Z LNA** | £5 | Boost weak 2.4 GHz reflections | Ultrasound LNA is narrowband, different spec |
| **SPF2243 PA** | £4 | 2.4 GHz TX power | Ultrasound uses HV pulser (MD1210), completely different |
| **2.4 GHz antennas (×2)** | £10 | Radiate/capture RF | Ultrasound uses piezo transducers |
| **SMA splitter** | £3 | Divide LO | Not needed |
| **SMA attenuators** | £4 | Pad signals | Attenuators exist but different values |
| **SMA DC block** | £3 | Isolate DC | Not needed |
| **Servo + bracket** | £7 | Scan antenna | Ultrasound array is fixed |
| **External 5V for servos** | £5 | Servo power | Not needed |
| **RTL-SDR debug** | £22 | Verify 2.4 GHz | Ultrasound scope/PicoScope covers this |
| **Logic analyser** | £10 | Debug ADF4351 SPI | Useful for TurboQuant too but not essential |

**Radar-unique total: ~£93** (assuming Red Pitaya + tools already owned)

---

## Hardware Unique to TurboQuant

Items TurboQuant needs that radar doesn't:

| Item | Cost | Why Ultrasound Needs It | Why Radar Doesn't |
|------|------|------------------------|-------------------|
| **DG408 MUX** | £3 | Switch 8 ultrasound channels | Radar uses 2 fixed channels |
| **74HCT595** | £1 | MUX control | Radar uses fewer GPIOs |
| **MUR120 (×32)** | £8 | T/R diode bridge (200V) | Radar uses PA + circulator |
| **IRF830** | £2 | TX switch | Different architecture |
| **LM7805 DPAK** | £1 | 5V reg | Shared |
| **BAV99** | £1 | Clamping | Not needed |
| **Custom PCB (JLCPCB)** | £43 | 4-layer mixed-signal | Radar uses modules + perfboard |
| **Transducers (eBay)** | £151 | Piezo probes | Completely different physics |
| **HV pulser (MD1210)** | £50 | 100–200V TX pulse | Radar PA is low voltage |
| **PicoScope 2206B** | £350 | 12-bit 4-ch scope | Shared debug tool |

**TurboQuant-unique total: ~£610** (including scope + transducers)

---

## Crossover Opportunities

### 1. FPGA Bitstream Reuse

The Zynq block design from TurboQuant:
```
PS7 ──► AXI Interconnect ──► AXI GPIO ──► DG408 MUX control
                         ──► AXI DMA ──► DDR
                         ──► AXI Stream ──► Custom IP
```

For radar FMCW:
```
PS7 ──► AXI Interconnect ──► AXI GPIO ──► ADF4351 SPI control
                         ──► AXI DMA ──► DDR
                         ──► AXI Stream ──► Chirp Gen ──► DAC
                         ──► AXI Stream ──► De-Chirp ──► CIC ──► ADC
```

**Reuse:**
- AXI Interconnect (same)
- AXI DMA (same S2MM path)
- AXI GPIO (different pins, same IP)
- HP0 AXI (same)
- Clocking (125 MHz ADC/DAC clock same)

**New:**
- Chirp generator (replaces MUX controller)
- Complex multiplier (new)
- CIC decimator (new)

**~60% of the Vivado project is reusable.**

### 2. Python API Reuse

TurboQuant Python (`v5_api.py`):
```python
class TurboQuantAPI:
    def set_mux_channel(self, ch): ...
    def acquire_waveform(self): ...
    def set_pulse_voltage(self, v): ...
```

Radar Python (`rp_sdr_client.py`):
```python
class RedPitayaSDR:
    def set_tx_freq(self, hz): ...
    def get_samples(self, n): ...
```

**Shared patterns:**
- TCP socket communication
- SCPI-like command protocol
- I/Q data parsing
- Threading for streaming
- NumPy processing pipeline

**Could unify into one `RedPitayaAPI` class** with mode switching:
```python
class RedPitayaAPI:
    MODE_ULTRASOUND = 'ultrasound'
    MODE_RADAR_CW = 'radar_cw'
    MODE_RADAR_FMCW = 'radar_fmcw'
    
    def set_mode(self, mode): ...
    
    # Ultrasound methods
    def set_mux_channel(self, ch): ...
    
    # Radar methods
    def set_chirp_params(self, bw, duration): ...
    def get_radar_samples(self, n): ...
```

### 3. Analog Component Substitution

| TurboQuant Part | Radar Part | Can Substitute? |
|----------------|-----------|-----------------|
| Precision op-amp (e.g., OPAx189) | OPA2197 | ✅ Check GBW > 10 MHz |
| 5V regulator (LM7805) | AMS1117-3.3 | ⚠️ Different voltage, same package |
| 100 nF decoupling caps | Same | ✅ Identical |
| 10 kΩ resistors | Same | ✅ Identical |
| SMA connectors | Same | ✅ Identical |

### 4. Test Equipment Crossover

| Tool | Ultrasound Use | Radar Use | Priority |
|------|---------------|-----------|----------|
| **PicoScope 2206B** | Verify ultrasound pulses | Verify baseband I/Q | 🔥 Shared essential |
| **RTL-SDR** | Not used | Verify 2.4 GHz LO | Radar-only but cheap |
| **Multimeter** | Continuity, bias | Bias, supply | 🔥 Shared |
| **Bench PSU** | Power V5 board | Power RP + frontend | 🔥 Shared |
| **Function generator** | Not used | Test baseband amp | Optional for both |

### 5. Physical Workspace

| Resource | Ultrasound | Radar | Notes |
|----------|-----------|-------|-------|
| **Bench space** | Large (transducer array) | Medium (servo + antennas) | Same bench, different setups |
| **Water tank** | Needed for immersion testing | Not needed | Ultrasound-specific |
| **RF-shielded area** | Not needed | Helpful for 2.4 GHz | Radar-specific |
| **Dark room** | Not needed | Helpful for motion testing | Optional |

---

## Procurement Strategy: Combined Order

### If Ordering for Both Projects Together

**Phase 1 — Shared Foundation (£400)**
| Item | £ | Project |
|------|---|---------|
| Red Pitaya 125-14 | 250 | Both |
| PicoScope 2206B | 350 | Both (essential) |
| Bench PSU 5V/3A | 8 | Both |
| Soldering station | 25 | Both |
| Multimeter | 12 | Both |
| Breadboard + jumpers | 15 | Both |
| Anti-static gear | 11 | Both |
| Tweezers + flux + solder | 12 | Both |
| **Subtotal** | **~683** | |

**Phase 2 — TurboQuant PCB (£150)**
| Item | £ |
|------|---|
| Digi-Key components | 84 |
| JLCPCB fabrication | 43 |
| Transducers | 151 |
| HV pulser parts | 50 |
| Enclosure | 15 |
| **Subtotal** | **~343** | |

**Phase 3 — Radar Frontend (£100)**
| Item | £ |
|------|---|
| ADF4351 | 10 |
| LT5560 | 8 |
| LNA | 5 |
| PA | 4 |
| Antennas (×2) | 10 |
| SMA cables + adapters | 25 |
| Servo + bracket | 7 |
| External 5V | 5 |
| RTL-SDR | 22 |
| Attenuators | 4 |
| **Subtotal** | **~100** | |

**Grand total for both projects: ~£1,126**

Compare to buying separately:
- TurboQuant alone: £1,223–1,363
- Radar alone: £513 (with RP) or £263 (without RP)
- **Combined: £1,126** (saves ~£100–200 on shared tools + RP)

---

## Build Timeline with Shared Resources

| Week | TurboQuant | Radar | Shared Activity |
|------|-----------|-------|-----------------|
| 1 | Order Digi-Key + JLCPCB | Order AliExpress RF parts | Shared bench setup |
| 2 | Wait for PCB | Flash RP SDR image, test baseband | Soldering practice |
| 3 | Assemble V5 PCB | Build RF frontend on breadboard | Shared scope debug |
| 4 | V5 bring-up | Test LO + mixer with RTL-SDR | |
| 5 | Transducer tests | CW Doppler desk test | |
| 6 | Integration | Add servo, polar scan | |
| 7 | Calibrate | Through-wall test | |
| 8 | Validate | FMCW FPGA upgrade | Vivado work |

**Key insight:** While waiting for TurboQuant PCB (2–3 weeks), you can build and test the radar frontend. The Red Pitaya serves both — swap SD cards to switch modes.

---

## The Red Pitaya as Universal Instrument

What you've built:

| Mode | Bitstream | Use |
|------|-----------|-----|
| **TurboQuant** | Custom (MUX + DMA) | 8-ch ultrasound acquisition |
| **Radar CW** | Pavel Demin SDR | CW Doppler streaming |
| **Radar FMCW** | Custom (chirp + de-chirp) | Range profile extraction |
| **VNA** | Pavel Demin VNA | Antenna tuning |
| **Scope** | Standard RP OS | Quick analog checks |

**One board, five instruments.** That's the value of an open FPGA platform.

---

## Bottom Line

| Question | Answer |
|----------|--------|
| Can one Red Pitaya do both? | ✅ Yes — swap SD cards |
| Do tools transfer? | ✅ Yes — all bench tools shared |
| Does FPGA knowledge transfer? | ✅ Yes — 60% block design reusable |
| Does Python code transfer? | ✅ Yes — patterns shared, could unify API |
| Do analog parts transfer? | ⚠️ Partial — passives yes, RF-specific no |
| Do transducers transfer? | ❌ No — completely different physics |
| Do antennas transfer? | ❌ No — ultrasound uses piezo |
| Total unique cost for radar (tools+RP already owned) | **~£93** |
| Combined cost (from nothing) | **~£1,126** |
| Savings from shared purchase | **~£100–200** |

**The radar is a cheap side project** if you're already building TurboQuant. The Red Pitaya and bench are the expensive parts — and you already need those.
