# Shear Wave Dispersion Analysis Pipeline

Complete signal processing pipeline for shear wave dispersion analysis in viscoelastic materials. Implements wavelet denoising, spatial coherence validation, and robust parameter estimation with uncertainty quantification.

## Quick Start

```bash
# Install dependencies
pip install numpy scipy matplotlib pywt

# Run demo
python3 shear_wave_pipeline.py
```

## Installation

### Requirements

- Python 3.8+
- NumPy >= 1.20
- SciPy >= 1.7
- Matplotlib >= 3.3
- PyWavelets >= 1.1

### Setup

```bash
git clone https://github.com/svenclawdbot-ai/Engineering-Learning.git
cd acoustic-nde
git submodule update --init  # If using week2 simulator
```

## Pipeline Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Raw Signals    │───▶│ Wavelet Denoise  │───▶│ Spatial Check   │
│  (3-4 receivers)│    │ (sym6, 2.0×)     │    │ (Validate wave) │
└─────────────────┘    └──────────────────┘    └────────┬────────┘
                                                        │
┌─────────────────┐    ┌──────────────────┐            │
│  Bootstrap CI   │◀───│ Savgol Smooth    │◀───────────┘
│  (G', η ± σ)    │    │ (window=5, o=3)  │
└─────────────────┘    └──────────────────┘
```

## Usage

### Basic Analysis

```python
from shear_wave_pipeline import ShearWaveAnalyzer
import numpy as np

# Your data: time-domain signals from 3 receivers
signals = [receiver_1, receiver_2, receiver_3]  # Each: np.array of shape (n_samples,)
dt = 1 / 20000  # Sampling interval (50 μs = 20 kHz)
distances = np.array([0.005, 0.010, 0.015])  # 5mm, 10mm, 15mm from source

# Initialize analyzer
analyzer = ShearWaveAnalyzer(
    wavelet='sym6',
    threshold_factor=2.0,
    enable_spatial_check=True,
    enable_smoothing=True
)

# Run analysis
results = analyzer.analyze(signals, dt, distances)

# Extract parameters
print(f"G' = {results['G_prime']:.0f} ± {results['G_prime_std']:.0f} Pa")
print(f"η  = {results['eta']:.3f} ± {results['eta_std']:.3f} Pa·s")
print(f"Quality flag: {results['quality_flag']}")

# Generate plots
analyzer.plot_results('analysis_output.png')
```

### Advanced Configuration

```python
# Customize for specific noise conditions
analyzer = ShearWaveAnalyzer(
    wavelet='sym6',              # Options: 'sym6', 'sym8', 'db6', 'coif2'
    threshold_factor=2.5,        # Higher = more conservative (2.0 default)
    enable_spatial_check=True,   # Set False to skip coherence validation
    enable_smoothing=True,       # Set False to skip Savgol smoothing
    rho=1000                     # Material density (kg/m³)
)

# Run with custom frequency range
results = analyzer.analyze(
    signals, dt, distances,
    freq_range=(40, 200),  # 40-200 Hz analysis
    freq_step=10,          # 10 Hz steps
    verbose=True
)
```

## Module Reference

### wavelet_denoising.py

Temporal signal denoising using wavelet thresholding.

```python
from wavelet_denoising import WaveletDenoiser, denoise_signal

# Method 1: Direct denoising
denoised = denoise_signal(
    signal, 
    wavelet='sym6',
    threshold_factor=2.0,
    verbose=True
)

# Method 2: Class-based for repeated use
denoiser = WaveletDenoiser(
    wavelet='sym6',
    level=5,
    threshold_factor=2.0,
    mode='soft'
)
denoised = denoiser.denoise(signal)

# Inspect decomposition
denoiser.plot_comparison(original, denoised)
denoiser.plot_decomposition()
```

**Threshold Guidelines:**

| Noise Condition | Recommended Factor |
|-----------------|-------------------|
| Clean (< 10% noise) | 1.0–1.5× |
| Moderate (10-20%) | 1.5–2.0× |
| Heavy (> 20%) or impulse noise | 2.0–2.5× |
| Baseline wander | 2.5–3.0× |

### spatial_filtering.py

Array coherence validation for multi-receiver setups.

```python
from spatial_filtering import compute_spatial_coherence

coherence = compute_spatial_coherence(
    signals,           # List of receiver signals
    dt,                # Time step
    distances,         # Receiver distances
    expected_velocity_range=(0.5, 5.0)  # Expected c_s range (m/s)
)

# Check quality
print(f"Velocity estimate: {np.mean(coherence['velocity_estimates']):.2f} m/s")
print(f"Consistency: {coherence['velocity_consistency']:.3f}")

# Flag if poor coherence
if coherence['velocity_consistency'] < 0.7:
    print("WARNING: Low spatial coherence - check data quality")
```

### dispersion_postprocessing.py

Dispersion curve smoothing and parameter estimation.

```python
from dispersion_postprocessing import (
    savgol_smooth, 
    bootstrap_fit,
    kelvin_voigt
)

# Savitzky-Golay smoothing
vel_smooth, unc_smooth = savgol_smooth(
    frequencies,
    velocities,
    uncertainties,
    window_length=5,   # Must be odd
    polyorder=3        # Polynomial order
)

# Bootstrap parameter estimation
results = bootstrap_fit(
    frequencies,
    vel_smooth,
    unc_smooth,
    n_bootstrap=1000,  # Number of resamples
    rho=1000           # Density
)

print(f"G' = {results['G_median']:.0f} Pa")
print(f"95% CI: [{results['G_ci'][0]:.0f}, {results['G_ci'][1]:.0f}]")
```

## Data Format

### Input Signals

- **Shape:** `(n_samples,)` per receiver
- **Sampling:** Typically 20-50 kHz for ultrasound
- **Duration:** 50-100 ms captures shear wave arrival
- **Amplitude:** Normalized to ±1 (unitless displacement)

### Expected Wave Characteristics

| Parameter | Typical Value | Notes |
|-----------|---------------|-------|
| Center frequency | 50-200 Hz | Tissue: 100 Hz typical |
| Shear velocity | 1-5 m/s | Soft tissue: ~1.5 m/s |
| Arrival window | 45-80 ms | After source excitation |
| Receiver spacing | 5-10 mm | Minimum for phase resolution |

## Troubleshooting

### "No dispersion points extracted"

- Check `dt` is in seconds (not milliseconds)
- Verify signals have energy in 50-150 Hz band
- Inspect arrival times are within 45-80 ms window
- Try reducing noise threshold or increasing signal amplitude

### "Low spatial coherence detected"

- Verify receiver positions are correct
- Check for clipped or saturated signals
- Ensure wave is actually propagating (not evanescent)
- Consider reducing `threshold_factor` if over-denoising

### "Bootstrap fit failed"

- Need ≥4 frequency points for reliable fit
- Check dispersion curve is monotonic (increasing with frequency)
- Verify uncertainties are not all zero
- Try wider frequency range

### Poor parameter estimates

- Increase SNR (reduce noise, increase source amplitude)
- Add more receiver pairs (4+ receivers recommended)
- Extend frequency range for better dispersion characterization
- Check material is actually viscoelastic (Kelvin-Voigt model appropriate)

## Validation

Test the pipeline with synthetic data:

```python
# Generate test signals
python3 shear_wave_pipeline.py

# Expected output:
# G' = 2074 ± 106 Pa (true: 2000 Pa, ~4% error)
# η = 0.472 ± 0.505 Pa·s (true: 0.5, ~6% error)
```

## Performance

Typical execution times (Intel i7, 3 receivers, 4000 samples):

| Stage | Time |
|-------|------|
| Wavelet denoising | ~50 ms |
| Spatial coherence | ~30 ms |
| Dispersion extraction | ~100 ms |
| Bootstrap (n=1000) | ~500 ms |
| **Total** | **~700 ms** |

## Citation

If using this pipeline in research:

```bibtex
@software{shear_wave_pipeline_2026,
  title = {Shear Wave Dispersion Analysis Pipeline},
  author = {Research Team},
  year = {2026},
  url = {https://github.com/svenclawdbot-ai/Engineering-Learning}
}
```

## License

MIT License - See LICENSE file for details.

## Contact

For questions or issues:
- GitHub Issues: github.com/svenclawdbot-ai/Engineering-Learning/issues
- Blog: svenclawdbot-ai.github.io/Engineering-Learning

---

*Last updated: March 14, 2026*
