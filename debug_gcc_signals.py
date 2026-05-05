#!/usr/bin/env python3
"""
Debug script for GCC-PHAT integration
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

# Parameters
G_prime = 2000
eta = 0.5
rho = 1000
d = 0.0067  # 6.7 mm separation

fs = 20000
dt = 1/fs
duration = 0.1
t = np.linspace(0, duration, int(fs * duration))

# Generate signals for two receivers at different distances using narrowband bursts
d1 = 0.005  # 5 mm
d2 = d1 + d  # 5 mm + 6.7 mm

sig1 = np.zeros_like(t)
sig2 = np.zeros_like(t)

# Use narrowband tone bursts at different frequencies
freq_bands = [(60, 70), (80, 90), (100, 110), (120, 130), (140, 150)]

for f_low, f_high in freq_bands:
    f_center = (f_low + f_high) / 2
    omega_center = 2 * np.pi * f_center
    
    # Compute velocity at this frequency
    G_mag = np.sqrt(G_prime**2 + (omega_center * eta)**2)
    c_f = np.sqrt(2 / rho) * np.sqrt(G_mag**2 / (G_prime + G_mag))
    
    # Propagation delay
    delay1 = 0.050 + d1 / c_f
    delay2 = 0.050 + d2 / c_f
    
    # Generate tone burst
    burst_duration = 0.015
    envelope1 = np.exp(-((t - delay1)**2) / (2 * (burst_duration/3)**2))
    envelope2 = np.exp(-((t - delay2)**2) / (2 * (burst_duration/3)**2))
    
    phase1 = 2 * np.pi * f_center * (t - delay1)
    phase2 = 2 * np.pi * f_center * (t - delay2)
    
    sig1 += envelope1 * np.sin(phase1)
    sig2 += envelope2 * np.sin(phase2)

# Normalize
sig1 = sig1 / np.max(np.abs(sig1))
sig2 = sig2 / np.max(np.abs(sig2))

# Bandpass filter at 100 Hz
f_center = 100
nyq = fs / 2
low = max(0.01, (f_center-10) / nyq)
high = min(0.99, (f_center+10) / nyq)
b, a = butter(4, [low, high], btype='band')
sig1_f = filtfilt(b, a, sig1)
sig2_f = filtfilt(b, a, sig2)

# Expected delay
c_expected = np.sqrt(G_prime / rho)  # ~1.41 m/s
delay_expected = d / c_expected * 1000  # in ms
print(f"Expected delay for d={d*1000:.1f}mm at c={c_expected:.2f}m/s: {delay_expected:.2f} ms")

# Plot
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

# Raw signals
axes[0].plot(t*1000, sig1, 'b-', alpha=0.7, label=f'Receiver 1 (d={d1*1000:.0f}mm)')
axes[0].plot(t*1000, sig2, 'r-', alpha=0.7, label=f'Receiver 2 (d={d2*1000:.0f}mm)')
axes[0].set_xlabel('Time (ms)')
axes[0].set_ylabel('Amplitude')
axes[0].set_title('Raw Signals (Full Bandwidth)')
axes[0].legend()
axes[0].grid(True, alpha=0.3)
axes[0].set_xlim(40, 80)

# Filtered signals
axes[1].plot(t*1000, sig1_f, 'b-', alpha=0.7, label='Receiver 1 (100 Hz band)')
axes[1].plot(t*1000, sig2_f, 'r-', alpha=0.7, label='Receiver 2 (100 Hz band)')
axes[1].set_xlabel('Time (ms)')
axes[1].set_ylabel('Amplitude')
axes[1].set_title(f'Filtered Signals ({f_center-10}-{f_center+10} Hz)')
axes[1].legend()
axes[1].grid(True, alpha=0.3)
axes[1].set_xlim(40, 80)

# Zoomed view
axes[2].plot(t*1000, sig1_f, 'b-', alpha=0.7, label='Receiver 1')
axes[2].plot(t*1000, sig2_f, 'r-', alpha=0.7, label='Receiver 2')
axes[2].set_xlabel('Time (ms)')
axes[2].set_ylabel('Amplitude')
axes[2].set_title(f'Zoomed View - Expected delay: {delay_expected:.2f} ms')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

# Find peaks
from scipy.signal import find_peaks
peaks1, _ = find_peaks(np.abs(sig1_f), height=np.max(np.abs(sig1_f))*0.5)
peaks2, _ = find_peaks(np.abs(sig2_f), height=np.max(np.abs(sig2_f))*0.5)

if len(peaks1) > 0 and len(peaks2) > 0:
    t1 = peaks1[0] * dt * 1000
    t2 = peaks2[0] * dt * 1000
    measured_delay = t2 - t1
    axes[2].axvline(t1, color='b', linestyle='--', alpha=0.5)
    axes[2].axvline(t2, color='r', linestyle='--', alpha=0.5)
    axes[2].set_xlim(t1 - 5, t2 + 5)
    print(f"Measured delay (peak detection): {measured_delay:.2f} ms")

plt.tight_layout()
plt.savefig('gcc_debug_signals.png', dpi=150)
print("\nSaved: gcc_debug_signals.png")

# Now run GCC-PHAT
import sys
sys.path.insert(0, '/home/james/.openclaw/workspace')
from subsample_gcc import gcc_phat, gcc_standard

delay_phat, corr_phat = gcc_phat(sig1_f, sig2_f, fs, freq_range=(90, 110))
delay_std, corr_std = gcc_standard(sig1_f, sig2_f, fs)

print(f"\nGCC-PHAT: delay={delay_phat*1000:.3f} ms, corr={corr_phat:.4f}")
print(f"Standard GCC: delay={delay_std*1000:.3f} ms, corr={corr_std:.4f}")
print(f"Expected: delay={delay_expected:.3f} ms")
