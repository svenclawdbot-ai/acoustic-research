#!/usr/bin/env python3
"""
Matched Filter Deep Dive — Part 3: Dispersive Media Effects
============================================================

Models how dispersion affects matched filter performance.
Uses a simplified attenuation model appropriate for ultrasound in tissue.
"""

import numpy as np
import matplotlib.pyplot as plt

# =============================================================================
# PARAMETERS
# =============================================================================

fs = 125e6          # Red Pitaya ADC sample rate (Hz)
f0 = 5e6            # Transducer centre frequency (Hz)
tau = 1/f0          # 1-cycle pulse duration (s)
SNR_dB = 10         # Input SNR (dB)

# Material properties (realistic for soft tissue/phantom)
c0 = 1540           # Speed of sound (m/s) — soft tissue
alpha0 = 0.5        # Attenuation coefficient at 1 MHz (dB/cm)
n = 1.1             # Power law exponent (typically 1.0-1.5 for tissue)
d = 0.05            # Propagation distance (m) — 50mm

print("=" * 60)
print("MATCHED FILTER PART 3: DISPERSIVE MEDIA EFFECTS")
print("=" * 60)
print()
print("Material Properties (Soft Tissue / Phantom):")
print(f"  c₀ (speed of sound): {c0:.0f} m/s")
print(f"  α₀ (attenuation @ 1MHz): {alpha0:.1f} dB/cm")
print(f"  n (power law exponent): {n:.1f}")
print(f"  d (propagation distance): {d*1e3:.0f} mm")
print()

# =============================================================================
# 1. GENERATE TRANSMITTED PULSE
# =============================================================================

N = 4096
t = np.arange(0, N/fs, 1/fs)

# 1-cycle tone burst at 5 MHz
pulse = np.sin(2 * np.pi * f0 * t) * (t <= tau)
pulse = pulse / np.sqrt(np.sum(pulse**2))

# =============================================================================
# 2. MODEL DISPERSIVE PROPAGATION (Power Law Attenuation)
# =============================================================================

# Frequency vector
freqs_Hz = np.fft.fftfreq(N, 1/fs)
omega = 2 * np.pi * freqs_Hz

# Power law attenuation: α(f) = α₀ · (f/f₀)^n
# Convert α₀ from dB/cm to Np/m
alpha0_Np_m = alpha0 * 100 * np.log(10) / 20  # dB/cm → Np/m

# Attenuation coefficient at each frequency
f_ref = 1e6  # 1 MHz reference
alpha = alpha0_Np_m * (np.abs(freqs_Hz) / f_ref)**n
alpha[0] = 0  # DC has no attenuation

# Phase velocity dispersion (from Kramers-Kronig relations)
# For power law: c(f) = c₀ / (1 + tan(nπ/2) · α(f) · c₀ / (2πf))
# Simplified: small dispersion approximation
c_phase = c0 * np.ones_like(freqs_Hz)
# Only apply dispersion correction for non-zero frequencies
nonzero = np.abs(freqs_Hz) > 1e3
c_phase[nonzero] = c0 / (1 + np.tan(n*np.pi/2) * alpha[nonzero] * c0 / (2*np.pi*np.abs(freqs_Hz[nonzero])))

# Propagation transfer function
# H(f) = exp(-α(f)·d) · exp(-i·2πf·d/c(f))
H_prop = np.exp(-alpha * d) * np.exp(-1j * 2*np.pi*freqs_Hz * d / c_phase)

# Apply propagation
Pulse_spectrum = np.fft.fft(pulse)
Pulse_dispersed_spectrum = Pulse_spectrum * H_prop
pulse_dispersed = np.fft.ifft(Pulse_dispersed_spectrum).real

# Normalise to maintain unit energy
pulse_dispersed = pulse_dispersed / np.sqrt(np.sum(pulse_dispersed**2))

print("Dispersion Analysis:")
print(f"  Original pulse duration: {tau*1e9:.0f} ns")
threshold = 0.05 * np.max(np.abs(pulse_dispersed))
dispersed_samples = np.sum(np.abs(pulse_dispersed) > threshold)
print(f"  Dispersed pulse duration: {dispersed_samples / fs * 1e9:.0f} ns (estimated)")
print()

# =============================================================================
# 3. COMPARE PULSES
# =============================================================================

# Add noise to dispersed pulse
signal_power = np.sum(pulse_dispersed**2) / (tau * fs)
noise_power = signal_power / (10**(SNR_dB/10))
noise = np.sqrt(noise_power) * np.random.randn(N)
echo_dispersed = pulse_dispersed + noise

# Create matched filters
h_original = np.flip(pulse)
h_dispersed = np.flip(pulse_dispersed)

# Apply filters
filtered_original_mf = np.convolve(echo_dispersed, h_original, mode='same')
filtered_dispersed_mf = np.convolve(echo_dispersed, h_dispersed, mode='same')

# Measure SNR
peak_original = np.max(np.abs(filtered_original_mf))
peak_dispersed = np.max(np.abs(filtered_dispersed_mf))
noise_rms = np.sqrt(np.mean(noise[int(2*tau*fs):]**2))

SNR_original_mf = 20*np.log10(peak_original / noise_rms)
SNR_dispersed_mf = 20*np.log10(peak_dispersed / noise_rms)
SNR_loss = SNR_dispersed_mf - SNR_original_mf

print("=" * 60)
print("SNR COMPARISON")
print("=" * 60)
print(f"Matched filter designed for ORIGINAL pulse:")
print(f"  Peak output: {peak_original:.4f}")
print(f"  SNR: {SNR_original_mf:.1f} dB")
print()
print(f"Matched filter designed for DISPERSED pulse:")
print(f"  Peak output: {peak_dispersed:.4f}")
print(f"  SNR: {SNR_dispersed_mf:.1f} dB")
print()
print(f"SNR loss from mismatch: {SNR_loss:.1f} dB")
print(f"(Negative = dispersed filter performs better)")
print()

# =============================================================================
# 4. FREQUENCY-DOMAIN ANALYSIS
# =============================================================================

freqs_MHz = freqs_Hz / 1e6

# Attenuation in dB/m
alpha_dB_m = 20 * np.log10(np.e) * alpha

print("=" * 60)
print("DISPERSION CHARACTERISTICS")
print("=" * 60)
idx_5MHz = np.argmin(np.abs(freqs_MHz - 5))
print(f"At {f0/1e6:.1f} MHz:")
print(f"  Phase velocity: {c_phase[idx_5MHz]:.1f} m/s")
print(f"  Attenuation: {alpha_dB_m[idx_5MHz]:.1f} dB/m")
print(f"  Attenuation over {d*1e3:.0f}mm: {alpha_dB_m[idx_5MHz] * d:.2f} dB")
print(f"  Total attenuation (power): {20*np.log10(np.exp(-alpha[idx_5MHz]*d)):.1f} dB")
print()

# =============================================================================
# 5. PLOTS
# =============================================================================

fig = plt.figure(figsize=(14, 12))

# Plot 1: Original vs dispersed pulse
ax1 = plt.subplot(3, 2, 1)
ax1.plot(t*1e6, pulse, 'b-', linewidth=1.5, label='Original (transmitted)')
ax1.plot(t*1e6, pulse_dispersed, 'r-', linewidth=1.5, label='Dispersed (received)')
ax1.set_xlabel('Time (µs)')
ax1.set_ylabel('Amplitude')
ax1.set_title('Pulse Distortion Due to Dispersion')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.set_xlim([0, 2*tau*1e6])

# Plot 2: Spectra
ax2 = plt.subplot(3, 2, 2)
ax2.plot(freqs_MHz[:N//2], 20*np.log10(np.abs(Pulse_spectrum[:N//2]) + 1e-10), 'b-', linewidth=1.5, label='Original')
ax2.plot(freqs_MHz[:N//2], 20*np.log10(np.abs(Pulse_dispersed_spectrum[:N//2]) + 1e-10), 'r-', linewidth=1.5, label='Dispersed')
ax2.set_xlabel('Frequency (MHz)')
ax2.set_ylabel('Magnitude (dB)')
ax2.set_title('Frequency Content')
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.set_xlim([0, 20])

# Plot 3: Attenuation vs frequency
ax3 = plt.subplot(3, 2, 3)
ax3.plot(freqs_MHz[:N//2], alpha_dB_m[:N//2], 'g-', linewidth=1.5)
ax3.axvline(x=f0/1e6, color='r', linestyle='--', alpha=0.7, label=f'{f0/1e6:.1f} MHz')
ax3.set_xlabel('Frequency (MHz)')
ax3.set_ylabel('Attenuation (dB/m)')
ax3.set_title('Frequency-Dependent Attenuation')
ax3.legend()
ax3.grid(True, alpha=0.3)
ax3.set_xlim([0, 20])

# Plot 4: Phase velocity
ax4 = plt.subplot(3, 2, 4)
ax4.plot(freqs_MHz[:N//2], c_phase[:N//2], 'm-', linewidth=1.5)
ax4.axvline(x=f0/1e6, color='r', linestyle='--', alpha=0.7, label=f'{f0/1e6:.1f} MHz')
ax4.axhline(y=c0, color='k', linestyle=':', alpha=0.5, label=f'c₀ = {c0} m/s')
ax4.set_xlabel('Frequency (MHz)')
ax4.set_ylabel('Phase Velocity (m/s)')
ax4.set_title('Phase Velocity Dispersion')
ax4.legend()
ax4.grid(True, alpha=0.3)
ax4.set_xlim([0, 20])

# Plot 5: Matched filter outputs
ax5 = plt.subplot(3, 2, 5)
ax5.plot(t*1e6, filtered_original_mf, 'b-', linewidth=1.5, label='MF for original pulse')
ax5.plot(t*1e6, filtered_dispersed_mf, 'r-', linewidth=1.5, label='MF for dispersed pulse')
ax5.set_xlabel('Time (µs)')
ax5.set_ylabel('Amplitude')
ax5.set_title(f'Matched Filter Outputs (SNR loss: {SNR_loss:.1f} dB)')
ax5.legend()
ax5.grid(True, alpha=0.3)
ax5.set_xlim([0, 5*tau*1e6])

# Plot 6: Transfer function magnitude
ax6 = plt.subplot(3, 2, 6)
ax6.plot(freqs_MHz[:N//2], 20*np.log10(np.abs(H_prop[:N//2]) + 1e-10), 'c-', linewidth=1.5)
ax6.axvline(x=f0/1e6, color='r', linestyle='--', alpha=0.7)
ax6.set_xlabel('Frequency (MHz)')
ax6.set_ylabel('Magnitude (dB)')
ax6.set_title('Propagation Transfer Function')
ax6.grid(True, alpha=0.3)
ax6.set_xlim([0, 20])

plt.tight_layout()
plt.savefig('matched_filter_part3.png', dpi=150, bbox_inches='tight')
print("✓ Saved plot: matched_filter_part3.png")

# =============================================================================
# 6. PARAMETER SWEEP: ATTENUATION EFFECTS
# =============================================================================

print()
print("=" * 60)
print("PARAMETER SWEEP: ATTENUATION EFFECTS")
print("=" * 60)

alpha0_values = [0.1, 0.3, 0.5, 1.0, 2.0, 5.0]  # dB/cm @ 1MHz
print(f"{'α₀ (dB/cm)':>12} | {'Attn @5MHz (dB)':>16} | {'SNR loss (dB)':>14} | {'Pulse spread':>12}")
print("-" * 70)

for alpha0_test in alpha0_values:
    alpha0_Np = alpha0_test * 100 * np.log(10) / 20
    alpha_test = alpha0_Np * (np.abs(freqs_Hz) / f_ref)**n
    alpha_test[0] = 0
    
    H_test = np.exp(-alpha_test * d) * np.exp(-1j * 2*np.pi*freqs_Hz * d / c0)
    
    Pulse_test = Pulse_spectrum * H_test
    pulse_test = np.fft.ifft(Pulse_test).real
    pulse_test = pulse_test / np.sqrt(np.sum(pulse_test**2))
    
    # Attenuation at 5 MHz
    idx_5M = np.argmin(np.abs(freqs_MHz - 5))
    attn_dB = 20 * np.log10(np.exp(-alpha_test[idx_5M] * d))
    
    # SNR with mismatched filter
    h_test = np.flip(pulse_test)
    echo_test = pulse_test + noise
    filtered_test = np.convolve(echo_test, h_original, mode='same')
    filtered_matched = np.convolve(echo_test, h_test, mode='same')
    
    peak_test = np.max(np.abs(filtered_test))
    peak_matched = np.max(np.abs(filtered_matched))
    snr_loss_test = 20*np.log10(peak_test/peak_matched) if peak_matched > 0 else 0
    
    # Pulse spread
    threshold = 0.05 * np.max(np.abs(pulse_test))
    spread = np.sum(np.abs(pulse_test) > threshold) / fs * 1e9
    
    print(f"{alpha0_test:>12.1f} | {attn_dB:>16.1f} | {snr_loss_test:>14.1f} | {spread:>12.0f}")

# =============================================================================
# 7. KEY INSIGHTS
# =============================================================================

print()
print("=" * 60)
print("KEY INSIGHTS")
print("=" * 60)
print("1. Dispersion spreads pulse in time → broader peak after MF")
print("2. Frequency-dependent attenuation reduces high-frequency content")
print("3. Mismatched filter (designed for original pulse) loses SNR")
print("4. Higher attenuation → more pulse distortion → larger SNR loss")
print("5. Power law: α(f) = α₀·(f/f₀)^n — attenuation increases with frequency")
print()
print("Practical implications for TurboQuant V5:")
print("- Use dispersed pulse as template for matched filter")
print("- Or: pre-compensate (deconvolve) dispersion before filtering")
print("- Higher viscosity → need adaptive matched filter (track α estimate)")
print()
print("Connection to your shear wave simulations:")
print("- This models what your 2D/3D FDTD code simulates")
print("- Parameter recovery (G', η) uses this dispersion relationship")
print("- Matched filter is first step; inverse problem comes next")
