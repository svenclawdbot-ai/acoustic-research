# Acoustic Resonance Method — Physics Deep Dive

## The Core Idea

Instead of measuring a single reflected pulse, you create a **resonant cavity** between the transducer and the soil. The resonance frequencies depend on the acoustic impedance of the soil, giving you a very sensitive measurement.

## The Setup (from the NSF paper)

```
Transducer (piezo)
    ↓
Backing Plate A (PVC - low impedance ~3 MRayls)
    ↓
Backing Plate B (Steel - high impedance ~45 MRayls)
    ↓
Soil (unknown impedance Z)
```

The transducer is mounted on a **layered backing structure** (PVC + steel) that sits on top of the soil.

---

## The Physics: Standing Waves in a Layered System

### 1. What Happens When a Wave Hits an Interface

At any boundary between two materials, some energy reflects and some transmits:

- **Reflection coefficient** (pressure): 
  $$R = \frac{Z_2 - Z_1}{Z_2 + Z_1}$$
  
- **Transmission coefficient**:
  $$T = \frac{2Z_2}{Z_2 + Z_1}$$

Where $Z_1, Z_2$ are the acoustic impedances of the two materials.

### 2. The Key: Creating a Resonant Cavity

The PVC layer acts as a **quarter-wave resonator** (or more precisely, a resonant layer). Here's why:

- PVC has LOW impedance (~3 MRayls)
- Steel has HIGH impedance (~45 MRayls) 
- Soil has UNKNOWN impedance (typically 2-8 MRayls)

When the ultrasonic wave travels:
1. Through the PVC → hits steel → **strong reflection** (because steel ≫ PVC)
2. The reflected wave returns to PVC → hits soil interface → **partial reflection** (depends on Z_soil)

### 3. Standing Wave Pattern

The two reflections interfere. For certain frequencies, they interfere **constructively** → resonance.

For a layer of thickness $d$ with wave velocity $c$, the resonance condition is approximately:

$$f_n = \frac{(2n+1)c}{4d}$$

This is the **quarter-wave resonator** condition: the round-trip phase shift creates constructive interference at odd multiples of quarter-wavelength.

### 4. Why This Reveals Soil Impedance

The **quality factor** (Q) and the **exact resonance frequencies** depend on:
- The impedance mismatch at the PVC-soil boundary
- The impedance mismatch at the PVC-steel boundary

Mathematically, the input impedance looking into the layered structure is:

$$Z_{in} = Z_{PVC} \frac{Z_{soil} + j Z_{PVC} \tan(kd)}{Z_{PVC} + j Z_{soil} \tan(kd)}$$

Where $k = 2\pi f/c$ is the wavenumber in PVC.

The **peaks and valleys** in the reflected spectrum correspond to frequencies where:
- $\tan(kd)$ creates maxima/minima
- The exact positions depend on $Z_{soil}$

### 5. Reading the Resonance Spectrum

When you sweep frequency and measure reflected amplitude:

```
Amplitude
    │
    │    ╱╲        ╱╲
    │   ╱  ╲      ╱  ╲
    │──╱────╲────╱────╲───
    │ ╱      ╲  ╱      ╲
    │╱        ╲╱        ╲
    └──────────────────────→ Frequency
       f₁      f₂      f₃
```

- **Resonance peaks**: occur at frequencies where the PVC layer length = odd multiples of λ/4
- **Peak spacing** Δf = c/2d (fundamental cavity mode spacing)
- **Peak width** (Q factor): depends on energy loss — broader peaks = more energy transmitted into soil = lower reflection = closer impedance match

### 6. Extracting Z_soil

From the measured resonance spectrum:

1. **Identify resonance frequencies** $f_n$
2. **Measure Q factor** (bandwidth at -3dB)
3. **Calculate reflection coefficient** at resonance from Q
4. **Solve for Z_soil**:

$$|R| = \frac{|Z_{soil} - Z_{PVC}|}{|Z_{soil} + Z_{PVC}|}$$

The exact relationship requires full transfer matrix analysis (layered media), but the principle is:
- **High Z_soil** (stiff/dense soil): strong reflection → sharp peaks, high Q
- **Low Z_soil** (soft/loose soil): weak reflection → broad peaks, low Q

## Why This is So Sensitive

Compared to simple pulse-echo:

| Method | Signal Measured | Sensitivity |
|--------|----------------|-------------|
| Pulse-echo | Single reflection amplitude | Moderate |
| Resonance | Multiple round-trip interference | High (Q-factor amplification) |

The resonance method effectively "amplifies" the impedance contrast by letting the wave bounce many times. Small changes in Z_soil create measurable shifts in:
- Resonance frequency
- Peak amplitude  
- Peak width (Q)

## Practical Implementation

**Electronics:**
- Frequency sweep generator (chirp or stepped sine)
- Power amplifier for transducer
- Receiver amplifier
- FFT or lock-in detection for spectrum analysis

**Transducer:**
- Same piezo element for TX and RX (pulse-echo style)
- Frequency range: typically 100kHz - 1MHz
- PVC backing layer: ~5-20mm thickness
- Steel backing: ~10-20mm thickness

**Signal Processing:**
- Send swept-frequency tone burst
- Record reflected signal
- FFT to get frequency response
- Fit resonance peaks
- Extract Z_soil from peak parameters

## Extension: Multi-Layer Soil Profile

If the soil itself is layered, each layer interface creates additional reflections. The full system becomes:

```
Transducer
    ↓
PVC backing
    ↓
Steel backing
    ↓
Soil Layer 1 (Z₁)
    ↓
Soil Layer 2 (Z₂)
    ↓
Soil Layer 3 (Z₃)
```

The resonance spectrum becomes more complex, but by analyzing multiple peaks and using inversion techniques, you can potentially resolve:
- Layer boundaries
- Each layer's impedance
- Layer thicknesses

This is the realm of **acoustic impedance inversion** used in seismic exploration.

---

## Summary: The Physics in 3 Sentences

You create a resonant cavity using a known backing material (PVC). The cavity's resonance frequencies and Q-factor depend on the acoustic impedance mismatch with the soil. By precisely measuring the resonance spectrum, you invert for the soil's acoustic impedance — which encodes density and wave velocity information.
