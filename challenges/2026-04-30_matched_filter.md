# Matched Filter Deep Dive — Option B (from Apr 29 DSP Challenge)
## Engineering: Signal Processing

**Date:** 2026-04-30  
**Focus:** Matched filter theory, implementation, and performance analysis for ultrasonic NDE

---

## 🎯 Learning Objectives

1. **Understand matched filter theory** — Why it maximises SNR for known signals in noise
2. **Implement pulse compression** — Time-domain and frequency-domain approaches
3. **Quantify SNR improvement** — Compare matched filter vs raw reception
4. **Apply to ultrasonic NDE** — 5MHz tone burst echoes in dispersive media

---

## 📚 Theory Background

### What is a Matched Filter?

For a known transmitted signal $s(t)$ corrupted by additive white Gaussian noise (AWGN) $n(t)$, the **matched filter** has impulse response:

$$h(t) = s^*(T - t)$$

Where:
- $s^*(t)$ is the complex conjugate of the transmitted pulse
- $T$ is a time delay (usually the pulse duration)
- The filter is "matched" to the specific pulse shape

### Why It Maximises SNR

The matched filter maximises the **peak signal-to-noise ratio** at the sampling instant:

$$\text{SNR}_{\text{out}} = \frac{2E}{N_0}$$

Where:
- $E$ = energy of the signal $s(t)$
- $N_0$ = noise power spectral density

This is the **maximum achievable SNR** for any linear filter in AWGN.

### Pulse Compression

For a pulse of duration $\tau$, the matched filter output:
- Has peak amplitude proportional to pulse energy (not amplitude)
- Has compressed duration $\approx 1/B$ where $B$ is bandwidth
- For a 5MHz tone burst: compression factor = $\tau \times B$

---

## 🔬 Practical Exercise

### Part 1: Basic Matched Filter (1 hour)

**Task:** Implement matched filter for 5MHz tone burst

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# Parameters
fs = 125e6  # Red Pitaya ADC sample rate
f0 = 5e6    # Transducer centre frequency
tau = 1/f0  # 1-cycle pulse duration
t = np.arange(0, 10*tau, 1/fs)

# 1. Generate transmitted pulse (1-cycle tone burst)
pulse = np.sin(2*np.pi*f0*t) * (t <= tau)

# 2. Create matched filter (time-reversed, conjugated)
# For real signals: h(t) = s(T-t)
h = np.flip(pulse)

# 3. Generate synthetic echo with noise
SNR_dB = 10  # Input SNR
signal_power = np.sum(pulse**2)
noise_power = signal_power / (10**(SNR_dB/10))
noise = np.sqrt(noise_power) * np.random.randn(len(t))
echo = pulse + noise

# 4. Apply matched filter
filtered = np.convolve(echo, h, mode='same')

# 5. Compute SNR improvement
peak_raw = np.max(np.abs(echo))
peak_filtered = np.max(np.abs(filtered))
noise_raw = np.std(echo[len(pulse):])  # Noise after pulse
noise_filtered = np.std(filtered[len(pulse):])

SNR_raw = 20*np.log10(peak_raw/noise_raw)
SNR_filtered = 20*np.log10(peak_filtered/noise_filtered)
SNR_gain = SNR_filtered - SNR_raw

print(f"Raw SNR: {SNR_raw:.1f} dB")
print(f"Filtered SNR: {SNR_filtered:.1f} dB")
print(f"SNR Improvement: {SNR_gain:.1f} dB")
```

**Deliverable:**
- Plot: transmitted pulse, noisy echo, matched filter output
- Measure: SNR improvement (theoretical vs actual)
- Verify: output peak occurs at pulse arrival time

---

### Part 2: Frequency-Domain Implementation (1 hour)

**Task:** Implement matched filter via FFT for computational efficiency

```python
# Frequency-domain matched filter
N = len(echo)
H = np.fft.fft(h, N)
X = np.fft.fft(echo, N)
Y = X * np.conj(H)  # Correlation in frequency domain
filtered_fd = np.fft.ifft(Y)

# Compare with time-domain
print(f"Max difference (TD vs FD): {np.max(np.abs(filtered - filtered_fd)):.2e}")
```

**Key insight:** For long signals, FFT-based implementation is $O(N \log N)$ vs $O(N^2)$ for direct convolution.

**Deliverable:**
- Compare execution time for different signal lengths
- Verify numerical equivalence (within machine precision)
- Plot frequency response of matched filter

---

### Part 3: Dispersive Media Effects (1 hour)

**Task:** Model how dispersion affects matched filter performance

In viscoelastic media (Kelvin-Voigt model):
- Phase velocity varies with frequency: $c_p(\omega) = \sqrt{\frac{G' + i\omega\eta}{\rho}}$
- Group velocity differs from phase velocity
- Pulse shape distorts during propagation

```python
# Model dispersive propagation
# Simplified: apply frequency-dependent attenuation and phase shift
omega = 2*np.pi*np.fft.fftfreq(len(t), 1/fs)

# Kelvin-Voigt dispersion (simplified)
G_prime = 50e3  # Storage modulus (Pa)
eta = 0.5       # Viscosity (Pa·s)
rho = 1000      # Density (kg/m³)
d = 0.05        # Propagation distance (m)

c = np.sqrt((G_prime + 1j*omega*eta)/rho)
k = omega / c

# Apply propagation
S = np.fft.fft(pulse)
S_prop = S * np.exp(-1j * k * d)
pulse_dispersed = np.fft.ifft(S_prop).real

# Now design matched filter for dispersed pulse
h_dispersed = np.flip(pulse_dispersed)
filtered_dispersed = np.convolve(echo, h_dispersed, mode='same')
```

**Deliverable:**
- Plot: original pulse vs dispersed pulse
- Compare: matched filter designed for original vs dispersed pulse
- Measure: SNR loss due to dispersion mismatch

---

### Part 4: Real-World Considerations (30 min)

**Topics to investigate:**

1. **Doppler shift** — If target is moving, pulse frequency shifts
   - Matched filter becomes mismatched
   - Solution: Doppler-tolerant waveforms (e.g., chirp)

2. **Multiple targets** — Range resolution
   - Two targets resolvable if separated by $\Delta t \approx 1/B$
   - For 5MHz pulse: $\Delta t \approx 200$ ns → $\Delta d \approx 0.3$ mm in steel

3. **Clutter** — Reverberation from grain structure
   - Matched filter doesn't suppress correlated clutter
   - Solution: Wiener filter or adaptive filtering

4. **Quantisation** — ADC effects (Red Pitaya 14-bit)
   - Quantisation noise floor ~ -84 dBFS
   - Matched filter gain helps but can't recover lost bits

---

## 📊 Success Criteria

| Task | Deliverable | Time |
|------|-------------|------|
| Part 1 | Python script + SNR plots | 1 hr |
| Part 2 | FFT implementation + timing | 1 hr |
| Part 3 | Dispersion model + comparison | 1 hr |
| Part 4 | Notes on real-world issues | 30 min |

**Total:** ~3.5 hours focused work

**Connection to prior learning:**
- Links to Apr 28 Fourier analysis challenge
- Builds on Apr 29 filter design (FIR/IIR)
- Applies to TurboQuant V5 signal processing chain

---

## 🔗 References

- Turin, G.L. (1960). "An introduction to matched filters." *IRE Trans. Info Theory*
- Levanon, N. (1988). *Radar Principles*. Wiley-Interscience.
- Oppenheim & Schafer (2010). *Discrete-Time Signal Processing*, Ch. 6.

---

*Generated: 2026-04-30 | Option B from Apr 29 DSP Challenge | Matched Filter Deep Dive*
