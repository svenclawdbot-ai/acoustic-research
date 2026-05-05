# Engineering Challenge — 2026-04-14 (Tuesday)
## Acoustic NDE: Shear Wave Dispersion Pipeline & Real-Data Validation

### Background

Week 2 of your acoustic NDE research established a **production-ready signal processing pipeline** for shear wave dispersion analysis, achieving a **4× accuracy improvement** (7.4% → 1.8% error) through classical signal processing alone. The pipeline stages are:

1. **Wavelet denoising** (Symlet-6, 2.0× conservative threshold)
2. **Spatial coherence validation** (4-transducer array cross-check)
3. **Multi-frequency dispersion extraction** (bandpass + group velocity)
4. **Savitzky-Golay smoothing + bootstrap confidence intervals**

Today’s challenge pushes this from synthetic validation toward **real-data readiness** by implementing sub-sample precision, adaptive thresholding, and a quality-gated analysis workflow.

---

## Part 1: Sub-Sample Cross-Correlation Arrival-Time Estimation (45 min)

### Problem
The current pipeline uses peak-detection within a search window. For dispersion extraction, you need **sub-sample precision** on arrival times to compute accurate group velocities across frequencies.

### Tasks

1. **Implement parabolic peak interpolation**
   ```python
   def parabolic_interp(y, idx):
       """Sub-sample peak location via parabolic fit around idx."""
       if idx <= 0 or idx >= len(y) - 1:
           return float(idx)
       alpha = y[idx - 1]
       beta = y[idx]
       gamma = y[idx + 1]
       p = 0.5 * (alpha - gamma) / (alpha - 2*beta + gamma)
       return idx + p
   ```

2. **Implement generalized cross-correlation with phase transform (GCC-PHAT)**
   ```python
   from numpy.fft import fft, ifft

   def gcc_phat(sig1, sig2, fs, interp_factor=16):
       """
       Compute time delay between sig1 and sig2 using GCC-PHAT.
       Returns: delay (seconds), peak correlation value
       """
       n = len(sig1) + len(sig2) - 1
       X1 = fft(sig1, n=n)
       X2 = fft(sig2, n=n)
       R = X1 * np.conj(X2)
       R /= np.abs(R) + 1e-12  # PHAT whitening
       ccf = ifft(R)
       ccf = np.fft.fftshift(ccf.real)
       
       peak_idx = np.argmax(ccf)
       peak_fine = parabolic_interp(ccf, peak_idx)
       
       lags = np.arange(n) - (n - 1) / 2
       delay = lags[peak_idx] / fs  # coarse
       # For sub-sample, use interpolated position:
       delay_fine = (lags[peak_idx] + (peak_fine - peak_idx)) / fs
       return delay_fine, ccf[peak_idx] / np.max(np.abs(ccf))
   ```

3. **Validate on synthetic chirp signals**
   - Create a chirp with known time delay (e.g., 2.3 samples)
   - Verify GCC-PHAT recovers delay to <0.1 sample accuracy
   - Test robustness at SNR = 5 dB, 0 dB, -5 dB

### Deliverable
- `subsample_gcc.py` module
- Accuracy plot: sample-delay error vs SNR

---

## Part 2: Adaptive Wavelet Thresholding (60 min)

### Problem
Your Week 2 pipeline used a **fixed 2.0× threshold factor**, which works well for mixed noise but is suboptimal when noise conditions change. Implement **SNR-aware adaptive thresholding**.

### Tasks

1. **Estimate signal vs noise power**
   ```python
   def estimate_snr(signal, fs, noise_band=(150, 250)):
       """
       Estimate SNR using a high-frequency noise reference band.
       Returns: SNR_dB
       """
       from scipy.signal import welch
       f, Pxx = welch(signal, fs, nperseg=256)
       sig_mask = (f >= 10) & (f <= 100)
       noise_mask = (f >= noise_band[0]) & (f <= noise_band[1])
       sig_power = np.trapezoid(Pxx[sig_mask], f[sig_mask])
       noise_power = np.trapezoid(Pxx[noise_mask], f[noise_band])
       return 10 * np.log10(sig_power / (noise_power + 1e-12))
   ```

2. **Adaptive threshold map**
   | Estimated SNR | Threshold Factor | Rationale |
   |---------------|------------------|-----------|
   | > 20 dB | 1.0× | Clean data, minimal denoising needed |
   | 10–20 dB | 1.5× | Moderate noise |
   | 0–10 dB | 2.0× | Significant noise (current default) |
   | < 0 dB | 2.5× | Heavy noise, aggressive denoising |

3. **Integrate into WaveletDenoiser**
   ```python
   class AdaptiveWaveletDenoiser:
       def __init__(self, wavelet='sym6', level=5, mode='soft'):
           self.wavelet = wavelet
           self.level = level
           self.mode = mode
       
       def denoise(self, signal, fs):
           snr = estimate_snr(signal, fs)
           factor = self._select_factor(snr)
           # ... apply wavelet denoising with computed factor
           return denoised_signal, {'snr': snr, 'factor': factor}
   ```

4. **Benchmark on synthetic ultrasound signals**
   - Generate signals with 5%, 15%, 30% noise
   - Compare fixed 2.0× vs adaptive thresholding
   - Measure: G′ estimation error, η estimation error

### Deliverable
- `adaptive_wavelet.py` module
- Comparison table: fixed vs adaptive across noise levels

---

## Part 3: Quality-Gated Analysis Pipeline (45 min)

### Problem
Real experimental data will have bad acquisitions (poor coupling, motion artifacts, weak excitation). Build a **quality gate** that flags unreliable data *before* it enters the dispersion fit.

### Tasks

1. **Implement quality metrics**
   ```python
   def compute_quality_metrics(signals, dt, distances):
       """
       Returns dict of quality flags and scores.
       """
       metrics = {}
       
       # 1. Spatial coherence (from Week 2)
       from spatial_filtering import compute_spatial_coherence
       coherence = compute_spatial_coherence(signals, dt, distances)
       metrics['spatial_coherence'] = coherence['consistency']
       
       # 2. Signal-to-noise ratio (average across receivers)
       fs = 1.0 / dt
       snrs = [estimate_snr(s, fs) for s in signals]
       metrics['mean_snr'] = np.mean(snrs)
       metrics['min_snr'] = np.min(snors)
       
       # 3. Amplitude consistency (coefficient of variation)
       peaks = [np.max(np.abs(s)) for s in signals]
       metrics['amp_cv'] = np.std(peaks) / (np.mean(peaks) + 1e-12)
       
       # 4. Arrival-time monotonicity
       # For uniformly spaced receivers, delays should increase monotonically
       delays = [gcc_phat(signals[0], s, fs)[0] for s in signals[1:]]
       metrics['delay_monotonicity'] = np.sum(np.diff(delays) > -1e-6) / len(delays)
       
       return metrics
   ```

2. **Define pass/fail criteria**
   ```python
   def quality_gate(metrics):
       """
       Returns ('pass', 'warn', or 'fail') and reason string.
       """
       if metrics['spatial_coherence'] < 0.85:
           return 'fail', 'Low spatial coherence (poor wave propagation)'
       if metrics['mean_snr'] < 0:
           return 'fail', 'SNR too low for reliable dispersion'
       if metrics['amp_cv'] > 0.5:
           return 'warn', 'High amplitude variation (check coupling)'
       if metrics['delay_monotonicity'] < 0.8:
           return 'warn', 'Non-monotonic delays (possible artifact)'
       return 'pass', 'All quality checks passed'
   ```

3. **Integrate into ShearWaveAnalyzer**
   - Run quality gate *before* dispersion extraction
   - If `fail`: skip analysis, return error flag
   - If `warn`: proceed but flag larger uncertainties in bootstrap
   - If `pass`: normal processing

### Deliverable
- `quality_gate.py` module
- Test cases: clean data → pass, noisy data → warn/fail

---

## Part 4: End-to-End Real-Data Simulation (60 min)

### Problem
Simulate "realistic" ultrasound acquisition conditions to validate your improved pipeline.

### Tasks

1. **Realistic signal generator**
   ```python
   def generate_realistic_signals(
       G_prime=2000, eta=0.5, rho=1000,
       n_receivers=4, receiver_spacing=0.005,
       fs=10000, duration=0.1,
       noise_type='mixed',  # 'gaussian', 'impulse', 'baseline', 'mixed'
       coupling_variation=0.1  # amplitude variation between receivers
   ):
       """
       Generate signals with realistic artifacts.
       """
       # ... generate theoretical dispersion
       # ... add specified noise type
       # ... apply per-receiver amplitude scaling
       # ... add random baseline wander
       return signals, dt, distances, (G_prime, eta)
   ```

2. **Run full adaptive pipeline**
   ```python
   from shear_wave_pipeline import ShearWaveAnalyzer
   from adaptive_wavelet import AdaptiveWaveletDenoiser
   from quality_gate import compute_quality_metrics, quality_gate
   
   analyzer = ShearWaveAnalyzer(
       wavelet='sym6',
       threshold_factor='adaptive',  # Use adaptive
       enable_spatial_check=True,
       enable_smoothing=True
   )
   
   results = analyzer.analyze(signals, dt, distances)
   ```

3. **Compare Week 2 baseline vs today’s improvements**
   | Condition | Baseline (fixed 2.0×) | Adaptive + GCC-PHAT + Quality Gate |
   |-----------|----------------------|-----------------------------------|
   | Clean (5% noise) | 2.1% G′ error | ~1.5% G′ error |
   | Mixed (15% noise) | 1.8% G′ error | ~1.2% G′ error |
   | Heavy (30% noise) | 4.1% G′ error | ~2.5% G′ error |
   | Poor coupling | 7.0%+ error | **rejected by gate** |

### Deliverable
- `validate_realistic.py` test harness
- Error comparison plot across conditions
- ROC-like curve: gate rejection rate vs actual bad data

---

## Extension Challenges (Optional)

### A) Bayesian Dispersion Fitting (90 min)
Replace bootstrap with a Bayesian posterior using `emcee` or `PyMC`. Compare credible intervals to bootstrap confidence intervals.

### B) Real-Time Streaming Adaptation (60 min)
Modify the pipeline to process a sliding window of incoming data (simulated streaming) and update the dispersion estimate every N frames.

### C) Hardware Integration Plan (30 min)
Draft a protocol for capturing real data with the echomods kit: pulser settings, expected SNR, phantom specifications, and gate thresholds.

---

## Key Equations Reference

| Parameter | Formula |
|-----------|---------|
| Kelvin-Voigt dispersion | `c(ω) = √(2/ρ) · √(|G*|² / (G′ + |G*|))` |
| GCC-PHAT delay estimate | `argmax_t ℱ⁻¹{X₁·X₂* / |X₁·X₂*|}` |
| Adaptive threshold | `factor = f(SNR_estimated)` |
| Quality gate | `pass` if coherence > 0.85 and SNR > 0 dB |

---

## Connections to Your Existing Work

| Previous Work | This Challenge |
|--------------|----------------|
| Week 2 wavelet denoising | → Adaptive thresholding |
| Peak-detection arrival times | → Sub-sample GCC-PHAT |
| Spatial coherence validation | → Quality-gated pipeline |
| Bootstrap uncertainty | → Realistic data validation |

---

## Deliverables Summary

1. **Sub-sample GCC-PHAT** — precise arrival-time estimation
2. **Adaptive wavelet denoiser** — SNR-aware thresholding
3. **Quality gate** — automatic pass/warn/fail for acquisitions
4. **Realistic validation** — end-to-end benchmark on simulated real data

---

**Difficulty:** Intermediate–Advanced (builds directly on Week 2 code)
**Est. Time:** 3.5 hours (core) + 2.5 hours (extensions)
**Topic:** Acoustic NDE / Signal Processing / Real-Data Validation

## Status: 🆕 NOT STARTED

*Generated: 2026-04-14 07:00 UTC*
