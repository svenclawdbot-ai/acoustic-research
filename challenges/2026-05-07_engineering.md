# Thursday Engineering Challenge — May 7, 2026
## Topic: Signal Processing for Soil Impedance Spectroscopy

### Context
Yesterday you reviewed the agricultural sensing roadmap. Soil impedance spectroscopy is Phase 1 — a proof-of-concept to measure soil moisture and nutrient content via electrical impedance across 1 Hz–10 MHz. Before building hardware, you need to validate the signal processing chain.

### The Challenge

**Part 1: Impedance Measurement Theory (45 min)**
- Derive the relationship between soil impedance magnitude/phase and:
  - Volumetric water content (using Archie's law simplified form)
  - Bulk electrical conductivity (salinity proxy)
- For a four-electrode Wenner array with spacing *a* = 5 cm, calculate the geometric factor K_g
- Estimate expected impedance range: dry clay (~10 kΩ) vs saturated loam (~100 Ω) at 1 kHz

**Part 2: Frequency Sweep DSP (45 min)**
Design the DSP pipeline for an impedance spectroscopy measurement:
1. **Excitation signal:** Sinusoid at frequency f, amplitude 100 mV ( galvanostatic / potentiostatic)
2. **Current sensing:** Transimpedance amplifier converts I_soil to voltage
3. **Lock-in amplification:** Multiply measured signal by reference sin/cos at f, LPF at 10 Hz
4. **Extract:** |Z| = V_exc / I_meas, phase = atan2(Q, I)
- Write pseudocode or Python for the lock-in amplifier DSP
- Calculate minimum measurement time per frequency point for 1% amplitude accuracy
- How many frequency points across 1 Hz–1 MHz can you measure in 60 seconds?

**Part 3: Noise & Error Budget (30 min)**
- Thermal noise in electrodes: 4kTR across 100 Ω–10 kΩ
- Calculate SNR at the TIA output for 1 Hz and 1 MHz BW
- Quantization noise: 16-bit ADC at 3.3V range — effective bits at different gain settings
- Identify the dominant error source at low vs high frequencies

### Deliverables
1. Impedance vs moisture curve sketch (hand calculation or Python plot)
2. Lock-in amplifier Python implementation (synthetic data test)
3. Measurement time budget table
4. Go/No-Go: Is a Red Pitaya (125 MSPS, 14-bit) overkill? Would a cheap STM32 + AD9833 DDS suffice for Phase 1?

### References
- rhoades1996_soil_electrical_conductivity.pdf (agricultural standard)
- kelleners2004_frequency_domain_analysis.pdf (soil dielectric)
- AD5933 datasheet (integrated impedance analyzer, 1 kHz–100 kHz)

---
*Time estimate: 2–2.5 hours*
*Focus: Validate DSP approach before £219 BOM spend*
