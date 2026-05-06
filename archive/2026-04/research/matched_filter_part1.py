#!/usr/bin/env python3
"""
Matched Filter Deep Dive — Part 1: Basic Implementation
========================================================

Demonstrates matched filter for ultrasonic NDE pulse compression.
Red Pitaya ADC: 125 MS/s, 14-bit
Transducer: 5 MHz centre frequency
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# =============================================================================
# PARAMETERS
# =============================================================================

fs = 125e6          # Red Pitaya ADC sample rate (Hz)
f0 = 5e6            # Transducer centre frequency (Hz)
tau = 1/f0          # 1-cycle pulse duration (s)
SNR_dB = 10         # Input SNR (dB)

# Time vector: enough samples to see pulse + some tail
t = np.arange(0, 20*tau, 1/fs)
N = len(t)

print(f"Sample rate: {fs/1e6:.1f} MS/s")
print(f"Centre frequency: {f0/1e6:.1f} MHz")
print(f"Pulse duration: {tau*1e9:.1f} ns ({tau*1e6:.2f} µs)")
print(f"Samples per pulse: {int(tau * fs)}")
print(f"Total samples: {N}")
print()

# =============================================================================
# 1. GENERATE TRANSMITTED PULSE (1-cycle tone burst)
# =============================================================================

# Window the sine wave to exactly 1 cycle
pulse = np.sin(2 * np.pi * f0 * t) * (t <= tau)

# Normalise to unit energy (convenient for SNR calculations)
pulse = pulse / np.sqrt(np.sum(pulse**2))

print(f"Pulse energy: {np.sum(pulse**2):.6f} (should be 1.0)")

# =============================================================================
# 2. CREATE MATCHED FILTER
# =============================================================================

# Matched filter impulse response: h(t) = s*(T - t)
# For real signals: time-reversed, conjugated (conjugate does nothing for real)
h = np.flip(pulse)

# Verify matched filter property: convolution with itself should peak at correct location
auto_corr = np.convolve(pulse, h, mode='full')
peak_idx = np.argmax(np.abs(auto_corr))
print(f"Autocorrelation peak at sample {peak_idx} (expected: {len(pulse)-1})")

# =============================================================================
# 3. GENERATE SYNTHETIC ECHO WITH NOISE
# =============================================================================

# Signal power (unit energy pulse, so power = energy / duration)
signal_power = np.sum(pulse**2) / (tau * fs)  # Power in samples where pulse exists

# Noise power from SNR
noise_power = signal_power / (10**(SNR_dB/10))
noise = np.sqrt(noise_power) * np.random.randn(N)

# Echo = pulse + noise (pulse at t=0)
echo = pulse + noise

print(f"\nSignal power: {signal_power:.6f}")
print(f"Noise power: {noise_power:.6f}")
print(f"Input SNR: {SNR_dB} dB (set)")

# =============================================================================
# 4. APPLY MATCHED FILTER
# =============================================================================

# Time-domain convolution
filtered = np.convolve(echo, h, mode='same')

# =============================================================================
# 5. MEASURE SNR IMPROVEMENT
# =============================================================================

# Method 1: Peak-to-RMS ratio (standard for pulse detection)
# Raw signal
peak_raw = np.max(np.abs(echo))
# Noise RMS in region after pulse dies out
noise_region = echo[int(2*tau*fs):]  # Samples after pulse + some margin
noise_rms_raw = np.sqrt(np.mean(noise_region**2))
SNR_raw_measured = 20*np.log10(peak_raw / noise_rms_raw)

# Filtered signal
peak_filtered = np.max(np.abs(filtered))
# Noise RMS after filtering (need to be careful about correlation effects)
# For proper measurement, apply filter to noise-only segment
noise_only = noise[int(2*tau*fs):]
filtered_noise = np.convolve(noise, h, mode='same')
noise_rms_filtered = np.sqrt(np.mean(filtered_noise[int(2*tau*fs):]**2))
SNR_filtered_measured = 20*np.log10(peak_filtered / noise_rms_filtered)

SNR_gain = SNR_filtered_measured - SNR_raw_measured

print(f"\n{'='*50}")
print("SNR ANALYSIS")
print(f"{'='*50}")
print(f"Raw signal:")
print(f"  Peak amplitude: {peak_raw:.4f}")
print(f"  Noise RMS: {noise_rms_raw:.4f}")
print(f"  Measured SNR: {SNR_raw_measured:.1f} dB")
print(f"\nFiltered signal:")
print(f"  Peak amplitude: {peak_filtered:.4f}")
print(f"  Noise RMS: {noise_rms_filtered:.4f}")
print(f"  Measured SNR: {SNR_filtered_measured:.1f} dB")
print(f"\nSNR Improvement: {SNR_gain:.1f} dB")
print(f"Theoretical gain: {10*np.log10(N):.1f} dB (processing gain ≈ 10·log₁₀(N))")
print(f"Actual processing gain: {10*np.log10(len(pulse)):.1f} dB (10·log₁₀(samples per pulse))")

# =============================================================================
# 6. PLOTS
# =============================================================================

fig, axes = plt.subplots(4, 1, figsize=(12, 10))

# Plot 1: Transmitted pulse
ax = axes[0]
ax.plot(t*1e6, pulse, 'b-', linewidth=1.5)
ax.set_xlabel('Time (µs)')
ax.set_ylabel('Amplitude')
ax.set_title(f'Transmitted Pulse: {f0/1e6:.1f} MHz, 1 cycle ({tau*1e9:.0f} ns)')
ax.grid(True, alpha=0.3)
ax.set_xlim([0, 2*tau*1e6])

# Plot 2: Noisy echo (zoomed)
ax = axes[1]
ax.plot(t*1e6, echo, 'r-', alpha=0.7, linewidth=0.8, label='Noisy echo')
ax.plot(t*1e6, pulse, 'b--', linewidth=2, label='True pulse')
ax.set_xlabel('Time (µs)')
ax.set_ylabel('Amplitude')
ax.set_title(f'Received Echo (SNR = {SNR_dB} dB) — Pulse barely visible in noise')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_xlim([0, 2*tau*1e6])

# Plot 3: Matched filter output
ax = axes[2]
ax.plot(t*1e6, filtered, 'g-', linewidth=1.5)
ax.axvline(x=tau*1e6, color='r', linestyle='--', alpha=0.7, label='Expected peak location')
ax.set_xlabel('Time (µs)')
ax.set_ylabel('Amplitude')
ax.set_title(f'Matched Filter Output — SNR = {SNR_filtered_measured:.1f} dB (gain: {SNR_gain:.1f} dB)')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_xlim([0, 5*tau*1e6])

# Plot 4: Autocorrelation shape (pulse compression visualisation)
ax = axes[3]
t_corr = np.arange(-len(pulse)+1, len(pulse)) / fs * 1e6  # µs
ax.plot(t_corr, auto_corr, 'm-', linewidth=1.5)
ax.set_xlabel('Lag (µs)')
ax.set_ylabel('Correlation')
ax.set_title('Pulse Autocorrelation — Shows compression effect')
ax.grid(True, alpha=0.3)
ax.set_xlim([-2*tau*1e6, 2*tau*1e6])

plt.tight_layout()
plt.savefig('matched_filter_part1.png', dpi=150, bbox_inches='tight')
print(f"\n✓ Saved plot: matched_filter_part1.png")

# =============================================================================
# 7. ADDITIONAL ANALYSIS
# =============================================================================

print(f"\n{'='*50}")
print("PULSE COMPRESSION ANALYSIS")
print(f"{'='*50}")

# Measure pulse width before and after filtering
# Before: duration = tau
# After: measure FWHM of autocorrelation peak
half_max = np.max(auto_corr) / 2
# Find where autocorrelation drops below half max
above_half = np.abs(auto_corr) > half_max
# Count continuous region around peak
peak_region = np.where(above_half)[0]
if len(peak_region) > 0:
    fwhm_samples = peak_region[-1] - peak_region[0] + 1
    fwhm_time = fwhm_samples / fs * 1e9  # ns
    compression_ratio = tau * 1e9 / fwhm_time
    print(f"Input pulse FWHM: {tau*1e9:.0f} ns")
    print(f"Output pulse FWHM: {fwhm_time:.1f} ns")
    print(f"Compression ratio: {compression_ratio:.1f}x")
    print(f"Range resolution: {fwhm_time/1e3 * 5900/2:.2f} mm in steel (c=5900 m/s)")

# Sidelobe analysis
main_lobe_width = int(2 * tau * fs)  # Approximate main lobe
sidelobes = np.abs(auto_corr)
# Zero out main lobe region
left_cutoff = max(0, peak_idx - main_lobe_width//2)
right_cutoff = min(len(sidelobes), peak_idx + main_lobe_width//2)
sidelobe_region = np.concatenate([sidelobes[:left_cutoff], 
                                   sidelobes[right_cutoff:]])
if len(sidelobe_region) > 0 and np.max(sidelobe_region) > 0:
    peak_sidelobe = np.max(sidelobe_region)
    pslr = 20*np.log10(peak_sidelobe / np.max(auto_corr))  # Peak sidelobe ratio
    print(f"\nPeak sidelobe level: {pslr:.1f} dB")
    print(f"(Lower is better — ideal sinc has -13.2 dB first sidelobe)")
else:
    print(f"\nNo significant sidelobes detected (pure tone burst)")
    print(f"Windowing (e.g., Hamming) would reduce sidelobes further")

print(f"\n{'='*50}")
print("KEY INSIGHTS")
print(f"{'='*50}")
print("1. Matched filter maximises SNR at the sampling instant")
print("2. Output peak occurs at t = τ (pulse duration delay)")
print("3. SNR gain ≈ 10·log₁₀(N) where N = samples in pulse")
print("4. Pulse is 'compressed' — narrower peak = better range resolution")
print("5. Sidelobes can cause false detections — windowing helps")

# Don't show plot in non-interactive environment
# plt.show()
