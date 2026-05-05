# Soil Impedance Spectroscopy — TurboQuant V5 Application Note

*Date: 2026-04-27*
*Status: Research & Conceptual Design*

---

## Overview

Soil impedance spectroscopy measures the electrical properties of soil across a range of frequencies (typically 1 Hz to 10 MHz). The complex impedance reveals:

- **Moisture content** — dominant factor affecting conductivity
- **Salinity / nutrient levels** — ionic concentration in pore water
- **Soil texture** — clay vs sand affects double-layer capacitance
- **Organic matter** — changes dielectric properties
- **Bulk density / compaction** — affects contact resistance and porosity

Your TurboQuant V5 hardware (8-channel MUX + LNA + FPGA) is well-suited for multi-point soil sensing with minimal modifications.

---

## Physics of Soil Impedance

### Equivalent Circuit Model

Soil can be modelled electrically as:

```
        R_bulk (ionic conduction)
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    │                             │
    │    C_double_layer           │
    │   ━━━━━━━━━━━━━━            │
    │   │            │            │
    │   │  R_polar   │            │
    │   │  (charge    │            │
    │   │   transfer)  │            │
    │   │            │            │
    ════╧════════════╧════════════
              
    Electrode 1          Electrode 2
```

Where:
- **R_bulk**: DC resistance of soil solution (~10-10,000 Ω·m depending on moisture/salinity)
- **C_double_layer**: Capacitance at electrode-soil interface (~µF/cm²)
- **R_polar**: Polarisation resistance (frequency-dependent)

### Frequency Response

| Frequency Range | Dominant Phenomenon | Information Content |
|-----------------|---------------------|---------------------|
| < 1 kHz | Electrode polarisation, double-layer charging | Electrode quality, soil texture |
| 1 kHz – 100 kHz | Bulk ionic conduction | **Moisture, salinity** (primary) |
| 100 kHz – 1 MHz | Dielectric relaxation of water | **Moisture** (secondary, less temperature sensitive) |
| 1 – 10 MHz | Maxwell-Wagner polarisation | Soil structure, porosity |

### Cole-Cole Model

The complex permittivity of soil follows:

$$
\varepsilon^*(\omega) = \varepsilon_\infty + \frac{\varepsilon_s - \varepsilon_\infty}{1 + (j\omega\tau)^{1-\alpha}}
$$

Where:
- ε_s = static permittivity (~5-80 depending on water content)
- ε_∞ = high-frequency permittivity (~3-5)
- τ = relaxation time constant (~10⁻⁶ to 10⁻³ s)
- α = distribution parameter (0 = ideal Debye, 0.1-0.5 = soil)

---

## TurboQuant V5 Adaptation

### Hardware Modifications

| Current V5 | Soil Sensing Mod | Notes |
|------------|------------------|-------|
| MUR120 diodes (T/R bridge) | **Remove / bypass** | Not needed for low-voltage soil sensing |
| DG408 MUX (8-ch) | **Keep** | Perfect for 8 soil electrodes |
| OPA1641 LNA | **Keep** | Low-noise for weak signals (µV to mV) |
| IRF830 + TC4427 (TX switch) | **Remove / disable** | No HV pulser needed |
| ±100V TX_BUS | **Replace with AC drive** | ±1V sinusoidal excitation |
| Red Pitaya DAC | **Use as signal generator** | 1-100 kHz sine sweep |
| Red Pitaya ADC | **Use as receiver** | I/Q demodulation or direct sampling |

### Proposed Soil Sensor Schematic

```
┌─────────────────────────────────────────────────────────────────┐
│              SOIL IMPEDANCE MEASUREMENT CHANNEL                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Red Pitaya DAC (±1V)                                           │
│       │                                                          │
│       ↓                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │ Current-Limit│───→│ Buffer       │───→│ Electrode    │       │
│  │ Resistor     │    │ (OPA1641)    │    │ Pair (SS)    │       │
│  │ (1kΩ)        │    │ (×1 gain)    │    │              │       │
│  └──────────────┘    └──────────────┘    └──────┬───────┘       │
│                                                   │              │
│                                                   ↓              │
│                                              ┌──────────┐       │
│                                              │   SOIL   │       │
│                                              │ (Z_soil) │       │
│                                              └────┬─────┘       │
│                                                   │              │
│       ┌───────────────────────────────────────────┘              │
│       ↓                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │ Sense        │───→│ OPA1641      │───→│ Red Pitaya   │       │
│  │ Resistor     │    │ LNA          │    │ ADC          │       │
│  │ (100Ω)       │    │ (gain=10)    │    │              │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│                                                                  │
│  Measurement: V_sense / R_sense = I_soil                         │
│  Z_soil = V_drive / I_soil                                       │
└─────────────────────────────────────────────────────────────────┘
```

### Electrode Design

**Four-electrode (Wenner) configuration** eliminates contact resistance:

```
    A ──→ I+    M ──→ V+    N ──→ V-    B ──→ I-
    │           │           │           │
    ├───────────┴───────────┴───────────┤
    │            SOIL VOLUME             │
    │                                    │
    └────────────────────────────────────┘
    
    A, B = current injection electrodes (outer)
    M, N = voltage sense electrodes (inner)
    
    Apparent resistivity: ρ_a = 2πa × (V_MN / I_AB)
    where a = electrode spacing
```

**Electrode materials:**
- Stainless steel (316L) — durable, low polarisation
- Graphite rods — excellent for long-term burial
- Ag/AgCl — reference quality but expensive

---

## Measurement Protocol

### Frequency Sweep

```python
# Pseudocode for Red Pitaya control
frequencies = np.logspace(0, 5, 50)  # 1 Hz to 100 kHz
results = []

for f in frequencies:
    # Generate sine wave on DAC
    rp.dac_generate(frequency=f, amplitude=0.5, waveform='sine')
    
    # Set MUX channel
    mux.select_channel(ch=0)
    
    # Acquire ADC samples
    adc_data = rp.adc_acquire(samples=4096, decimation=8)
    
    # Compute I/Q (lock-in detection)
    I, Q = lock_in_detect(adc_data, reference_freq=f)
    
    # Calculate impedance
    magnitude = np.sqrt(I**2 + Q**2) / drive_current
    phase = np.arctan2(Q, I)
    
    results.append((f, magnitude, phase))
```

### Lock-In Detection (FPGA Implementation)

Your FPGA can implement real-time lock-in amplification:

```verilog
// Simplified lock-in detector
module lock_in_detector (
    input clk_125mhz,
    input signed [13:0] adc_in,
    input [31:0] phase_increment,  // DDS frequency control
    output reg signed [31:0] I_out,
    output reg signed [31:0] Q_out
);

    // DDS sine/cosine generation
    dds_compiler dds (
        .clk(clk_125mhz),
        .phase_increment(phase_increment),
        .sine(ref_sin),
        .cosine(ref_cos)
    );
    
    // Multipliers (mixer)
    assign I_mix = adc_in * ref_cos;
    assign Q_mix = adc_in * ref_sin;
    
    // Low-pass filter (moving average)
    always @(posedge clk_125mhz) begin
        I_out <= I_out + (I_mix >>> 10) - (I_out >>> 10);
        Q_out <= Q_out + (Q_mix >>> 10) - (Q_out >>> 10);
    end
endmodule
```

---

## Calibration & Interpretation

### Topp Equation (Dielectric)

For moisture from dielectric permittivity:

$$
\theta_v = -5.3 \times 10^{-2} + 2.92 \times 10^{-2} \varepsilon - 5.5 \times 10^{-4} \varepsilon^2 + 4.3 \times 10^{-6} \varepsilon^3
$$

Where θ_v = volumetric water content, ε = apparent permittivity.

### Rhoades Equation (Electrical Conductivity)

For salinity from bulk electrical conductivity:

$$
EC_e \approx \frac{EC_b \cdot \rho_b}{\theta_v \cdot K_s}
$$

Where:
- EC_e = pore water electrical conductivity (dS/m)
- EC_b = bulk soil EC (measured)
- ρ_b = bulk density (g/cm³)
- θ_v = volumetric water content
- K_s = shape factor (~0.3-0.6)

---

## Multi-Channel Soil Sensor Array

### 8-Channel Configuration

```
    ┌─────────────────────────────────────────┐
    │         TURBOQUANT V5 SOIL PROBE       │
    │                                          │
    │  CH0  CH1  CH2  CH3  CH4  CH5  CH6  CH7 │
    │   ●    ●    ●    ●    ●    ●    ●    ●  │  ← Electrode pairs
    │   │    │    │    │    │    │    │    │  │    (4-electrode each)
    │   └────┴────┴────┴────┴────┴────┴────┘  │
    │              DG408 MUX (8-ch)            │
    │                   │                      │
    │              OPA1641 LNA                │
    │                   │                      │
    │            Red Pitaya ADC                │
    └─────────────────────────────────────────┘
    
    Spacing: 10-30cm between electrode pairs
    Depth: 10-50cm (adjustable insertion)
```

### Scanning Modes

1. **Parallel mode** — All 8 channels simultaneously (fast, coarse)
2. **Sequential mode** — One channel at a time (detailed, per-channel calibration)
3. **Differential mode** — Compare adjacent channels (gradient mapping)

---

## Comparison with Commercial Systems

| System | Channels | Frequency Range | Cost | Notes |
|--------|----------|-----------------|------|-------|
| **TurboQuant V5** | 8 | 1 Hz – 10 MHz | ~£300 | Customisable, FPGA real-time |
| Sentek Drill & Drop | 1 | 10 MHz (capacitance only) | £400 | Proprietary, single depth |
| Stevens HydraProbe | 1 | 50 MHz | £600 | Dielectric only, no salinity |
| Delta-T WET Sensor | 1 | 20-100 MHz | £350 | 3-parameter (moisture, EC, temp) |
| Irrometer Watermark | 1 | DC (resistance) | £50 | Granular matrix, slow response |

**Advantage of TurboQuant:** Multi-channel, wide frequency range, open-source, FPGA real-time processing.

---

## Implementation Roadmap

### Phase 1: Proof of Concept (1-2 weeks)
- [ ] Remove HV pulser from V5 (or disable in software)
- [ ] Add current-limiting resistors (1kΩ) to DAC outputs
- [ ] Build 4-electrode test cell with known soil samples
- [ ] Implement frequency sweep in Python (Red Pitaya)

### Phase 2: Calibration (2-3 weeks)
- [ ] Measure standard soils with known moisture (oven-dry method)
- [ ] Fit Cole-Cole parameters for different textures
- [ ] Validate against commercial sensors (HydraProbe, WET)
- [ ] Develop calibration equations for local soil types

### Phase 3: Field Deployment (1 month)
- [ ] Design waterproof electrode array (IP67)
- [ ] Add temperature compensation (soil temp affects EC by ~2%/°C)
- [ ] Implement wireless data logging (WiFi/LoRa)
- [ ] Solar power integration

### Phase 4: Data Platform (ongoing)
- [ ] Map moisture/salinity across field
- [ ] Irrigation scheduling algorithm
- [ ] Alert system for drought/salinity stress
- [ ] Integration with weather data

---

## Key Papers & References

1. **Topp et al. (1980)** — "Electromagnetic determination of soil water content" *Water Resources Research*
2. **Rhoades et al. (1976)** — "Effects of liquid-phase electrical conductivity, water content, and surface conductivity on bulk soil electrical conductivity" *Soil Science Society of America Journal*
3. **Hilhorst (2000)** — "A pore water conductivity sensor" *Soil Science Society of America Journal*
4. **Kelleners et al. (2005)** — "Improved method for calibrating electromagnetic induction sensors" *Soil Science Society of America Journal*

---

## Next Steps

1. **Review this concept** — does the physics match your understanding?
2. **Build test cell** — small container with 4 electrodes and known soil
3. **Modify V5 firmware** — disable pulser, add frequency sweep
4. **First measurement** — compare dry vs saturated soil impedance

Ready to adapt your V5 for soil sensing? The hardware is ~80% there already.
