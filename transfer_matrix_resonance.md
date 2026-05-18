# Transfer Matrix Method — Acoustic Resonance Probe

## The Physical Setup

From transducer to soil:

```
┌─────────────────────────────────────────────────┐
│  Transducer                                    │
│  (Piezo element)                               │
│  Z_piezo                                       │
├─────────────────────────────────────────────────┤
│  PVC Layer                                     │
│  thickness = d₁, impedance = Z₁, velocity = c₁│
├─────────────────────────────────────────────────┤
│  Steel Plate                                   │
│  thickness = d₂, impedance = Z₂, velocity = c₂│
├─────────────────────────────────────────────────┤
│  SOIL (semi-infinite)                          │
│  impedance = Z₃ (unknown!)                     │
└─────────────────────────────────────────────────┘
```

**The resonance comes from the PVC layer** — it's sandwiched between high-impedance boundaries (steel on one side, piezo on the other), and the soil impedance at the far end controls how much energy leaks out of the system.

---

## Transfer Matrix for a Single Layer

For a plane acoustic wave in layer $n$:

- **Characteristic impedance:** $Z_n = \rho_n c_n$
- **Wavenumber:** $k_n = \omega / c_n = 2\pi f / c_n$
- **Layer thickness:** $d_n$

The **state vector** at any position is $\mathbf{s} = \begin{bmatrix} p \\ v \end{bmatrix}$ where $p$ = pressure and $v$ = particle velocity.

The **transfer matrix** $T_n$ relates the state at the left boundary to the right boundary:

$$\mathbf{s}_{right} = T_n \, \mathbf{s}_{left}$$

$$T_n = \begin{bmatrix} \cos(k_n d_n) & i Z_n \sin(k_n d_n) \\ \dfrac{i \sin(k_n d_n)}{Z_n} & \cos(k_n d_n) \end{bmatrix}$$

**Where does this come from?**

Inside the layer, the pressure field is a superposition of forward and backward traveling waves:

$$p(x) = A e^{-ikx} + B e^{+ikx}$$

The particle velocity is related to pressure gradient:

$$v(x) = \frac{1}{Z}\left(A e^{-ikx} - B e^{+ikx}\right)$$

At $x=0$: $p(0) = A + B$, $v(0) = (A - B)/Z$

At $x=d$: $p(d) = A e^{-ikd} + B e^{+ikd}$, $v(d) = (A e^{-ikd} - B e^{+ikd})/Z$

Solving for $p(d), v(d)$ in terms of $p(0), v(0)$ gives the transfer matrix above.

---

## Building the Total System

For multiple layers, multiply the matrices:

$$T_{total} = T_1 \times T_2 \times \cdots \times T_N$$

The total transfer matrix relates the state at the first boundary (transducer side) to the state at the last boundary (soil side):

$$\mathbf{s}_{soil} = T_{total} \, \mathbf{s}_{transducer}$$

For our 2-layer system (PVC + Steel):

$$T_{total} = T_{PVC} \times T_{steel}$$

---

## Applying Boundary Conditions

**At the soil boundary** (semi-infinite medium):

Only an outgoing wave exists — no reflection coming back from infinity. The impedance looking into soil is simply $Z_3$.

$$\frac{p_{soil}}{v_{soil}} = Z_3$$

**At the transducer boundary:**

The transducer emits a wave and measures the reflected wave. The **input impedance** looking into the backing structure determines the reflection:

$$Z_{in} = \frac{p_{transducer}}{v_{transducer}}$$

---

## Deriving Input Impedance (Step by Step)

### Step 1: Steel Layer with Soil Load

The impedance looking into steel from the PVC side:

$$Z_{steel}^{in} = Z_2 \, \frac{Z_3 + i Z_2 \tan(k_2 d_2)}{Z_2 + i Z_3 \tan(k_2 d_2)}$$

**Physical interpretation:**
- If $Z_3 = Z_2$ (matched): $Z_{steel}^{in} = Z_2$ (no reflection at steel-soil boundary)
- If $Z_3 \ll Z_2$ (soft soil): $Z_{steel}^{in} \approx i Z_2 \tan(k_2 d_2)$ (resonant behavior)
- If $Z_3 \gg Z_2$: $Z_{steel}^{in} \approx Z_2 / \tan(k_2 d_2)$ (different resonance condition)

### Step 2: PVC Layer with Steel Load

Now the steel presents impedance $Z_{steel}^{in}$ to the PVC:

$$Z_{in} = Z_1 \, \frac{Z_{steel}^{in} + i Z_1 \tan(k_1 d_1)}{Z_1 + i Z_{steel}^{in} \tan(k_1 d_1)}$$

This is the **input impedance** that the transducer "sees" when it looks into its backing.

---

## Reflection Coefficient

The reflection coefficient at the transducer-backing interface:

$$R = \frac{Z_{piezo} - Z_{in}}{Z_{piezo} + Z_{in}}$$

The reflected signal amplitude is proportional to $|R(\omega)|$.

**Key insight:** $Z_{in}$ depends on $Z_3$ (soil impedance) through the chain of transfer matrices. So $|R(\omega)|$ encodes information about the soil.

---

## Resonance Condition

For strong resonances, we need high reflectivity at internal boundaries. With $Z_{steel} \gg Z_{PVC}$ and $Z_{soil} \sim Z_{PVC}$ or less:

The PVC layer becomes a resonant cavity bounded by:
- Steel side: nearly rigid (high reflection)
- Transducer side: partial reflection
- Soil side: partial transmission (energy loss)

The **resonance frequencies** approximately satisfy:

$$k_1 d_1 \approx \frac{(2n+1)\pi}{2} \quad \Rightarrow \quad f_n \approx \frac{(2n+1)c_1}{4d_1}$$

This is the **quarter-wave resonator** condition. The PVC layer thickness equals odd multiples of $\lambda/4$.

At resonance, $\tan(k_1 d_1) \to \infty$, and the input impedance simplifies to:

$$Z_{in}^{res} \approx \frac{Z_1^2}{Z_{steel}^{in}}$$

The **quality factor** $Q$ depends on energy loss:
- Into the transducer (matched or not)
- Into the soil (depends on $Z_3$)
- Material damping in PVC

$$Q \approx \frac{\text{energy stored}}{\text{energy lost per cycle}}$$

Higher $Q$ = sharper peaks = less energy lost to soil (or more impedance mismatch with soil).

---

## What the Measurement Looks Like

### Frequency Domain Signal

When you sweep frequency and measure reflected amplitude:

```
|R(ω)|
  │
  │       ╱╲          ╱╲
  │      ╱  ╲        ╱  ╲        ← Resonance peaks
  │─────╱────╲──────╱────╲───────
  │    ╱      ╲    ╱      ╲
  │   ╱        ╲  ╱        ╲
  │──╱──────────╲╱──────────╲─────
  └────────────────────────────────→ ω (or f)
         f₁        f₂        f₃
```

### Extracting Soil Impedance

From the measured spectrum, you extract:

1. **Resonance frequencies** $f_n$ → confirm PVC thickness/velocity
2. **Peak amplitudes** $|R(f_n)|$ → related to $Z_{in}$ at resonance
3. **Peak widths** $\Delta f$ (FWHM) → related to $Q$ factor

Then solve for $Z_3$:

At resonance, $Z_{in} \approx Z_1^2 / Z_{steel}^{in}$, and:

$$|R| = \left|\frac{Z_{piezo} - Z_1^2/Z_{steel}^{in}}{Z_{piezo} + Z_1^2/Z_{steel}^{in}}\right|$$

Since $Z_{steel}^{in}$ depends on $Z_3$ (through the steel layer transfer matrix), you can invert this relationship to find $Z_3$.

**For the case where steel is thick and $k_2 d_2 \gg 1$:**

The steel layer acts like a semi-infinite medium from the PVC's perspective (at most frequencies). Then:

$$Z_{steel}^{in} \approx Z_2$$

And:

$$Z_{in}^{res} \approx \frac{Z_1^2}{Z_2}$$

This is a **constant** (doesn't depend on soil!) at resonance. 

**Wait — how does soil affect anything?**

If steel is thick, the wave doesn't "see" the soil from the PVC side. The resonance is determined by PVC + steel only.

But here's the key: the transducer measures the **total reflected signal**, which includes:
1. Immediate reflection from transducer-PVC interface
2. Reflections from PVC-steel interface
3. Reflections that travel through PVC → steel → soil → steel → PVC → transducer

The **third path** carries soil information. Its phase and amplitude depend on the steel-soil reflection coefficient:

$$R_{steel-soil} = \frac{Z_3 - Z_2}{Z_3 + Z_2}$$

This creates **interference patterns** in the total reflected signal. By analyzing the fine structure of the resonance peaks, you extract $R_{steel-soil}$ and thus $Z_3$.

**Alternative interpretation:** The steel layer + soil acts as a **frequency-dependent load** on the PVC resonator. Even if steel is thick, there are frequencies where the round-trip phase in steel creates constructive/destructive interference, modulating the effective load impedance.

---

## Simplified Analysis: Thin PVC, Thick Steel

For a practical probe, let the PVC be thin ($d_1 \sim$ few mm) and steel be thick ($d_2 \sim$ 10-20 mm).

At frequencies where the PVC resonates ($f \sim c_1/4d_1 \sim$ 100-500 kHz):

- The steel layer has $k_2 d_2 \gg 1$ (many wavelengths)
- The steel acts like a frequency-selective reflector
- The reflection at steel-soil boundary modulates the overall response

The **measured spectrum** shows:
- Broad envelope from PVC resonance
- Fine structure from steel layer interference
- Amplitude modulation from soil impedance

By fitting the full spectrum with the transfer matrix model, you invert for $Z_3$.

---

## Numerical Example

Let's plug in realistic numbers:

| Material | Density (kg/m³) | Velocity (m/s) | Impedance (MRayls) | Thickness |
|----------|----------------|----------------|-------------------|-----------|
| PVC | 1400 | 2300 | 3.2 | 5 mm |
| Steel | 7850 | 5900 | 46.3 | 15 mm |
| Dry Sand | 1600 | 400 | 0.64 | ∞ |
| Sat. Clay | 1900 | 1500 | 2.85 | ∞ |

For PVC resonance:
$$f_1 = \frac{c_1}{4d_1} = \frac{2300}{4 \times 0.005} = 115 \text{ kHz}$$

At this frequency, in steel:
$$k_2 d_2 = \frac{2\pi \times 115000 \times 0.015}{5900} \approx 1.84 \text{ rad}$$

So $\tan(k_2 d_2) \approx -3.8$ — not in the "thick" regime. The steel contributes to the resonance.

For dry sand ($Z_3 = 0.64$ MRayls):
$$R_{steel-sand} = \frac{0.64 - 46.3}{0.64 + 46.3} = -0.97$$

Nearly total reflection — sand is effectively a free surface to steel.

For saturated clay ($Z_3 = 2.85$ MRayls):
$$R_{steel-clay} = \frac{2.85 - 46.3}{2.85 + 46.3} = -0.88$$

Still strong reflection, but less than sand. The difference creates measurable changes in the resonance spectrum.

---

## Summary: Transfer Matrix Recipe

1. **Define layers** with known properties (PVC, steel) and unknown (soil)
2. **Build transfer matrices** for each layer
3. **Multiply** to get total transfer matrix
4. **Apply boundary condition** at semi-infinite soil: $p/v = Z_3$
5. **Compute input impedance** $Z_{in}$ at transducer side
6. **Calculate reflection coefficient** $R(\omega) = (Z_{piezo} - Z_{in})/(Z_{piezo} + Z_{in})$
7. **Compare** $|R(\omega)|$ to measured spectrum
8. **Fit** for $Z_3$ (and optionally $c_3$ if you have additional constraints)

The transfer matrix method gives the **exact frequency response** of the layered system, enabling precise extraction of soil properties from resonance measurements.
