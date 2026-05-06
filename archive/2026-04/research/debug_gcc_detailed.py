#!/usr/bin/env python3
"""Debug GCC-PHAT signal generation"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
import sys
sys.path.insert(0, '/home/james/.openclaw/workspace')
from subsample_gcc import gcc_phat

# Parameters
G_prime = 2000
eta = 0.5
rho = 1000
d1, d2 = 0.005, 0.015  # 5mm and 15mm

fs = 20000
dt = 1/fs
duration = 0.12
t = np.linspace(0, duration, int(fs * duration))

# Generate signals with single frequency each (no interference)
def make_signal(d, f_center, t_base):
    omega = 2 * np.pi * f_center
    G_mag = np.sqrt(G_prime**2 + (omega * eta)**2)
    c_f = np.sqrt(2 / rho) * np.sqrt(G_mag**2 / (G_prime + G_mag))
    
    arrival = t_base + d / c_f
    burst_width = 0.005
    envelope = np.exp(-((t - arrival)**2) / (2 * (burst_width/3)**2))
    carrier = np.sin(omega * (t - arrival))
    return envelope * carrier, arrival, c_f

# Test at 100 Hz
f_test = 100
t_base = 0.050  # 50 ms base

sig1, arrival1, c1 = make_signal(d1, f_test, t_base)
sig2, arrival2, c2 = make_signal(d2, f_test, t_base)

print(f"100 Hz:")
print(f"  Receiver 1 (d={d1*1000:.0f}mm): arrival={arrival1*1000:.2f}ms, c={c1:.3f}m/s")
print(f"  Receiver 2 (d={d2*1000:.0f}mm): arrival={arrival2*1002:.2f}ms, c={c2:.3f}m/s")
print(f"  Expected delay: {(arrival2-arrival1)*1000:.2f}ms")
print(f"  Expected velocity: {(d2-d1)/(arrival2-arrival1):.3f}m/s")

# Filter signals
nyq = fs / 2
low, high = 90/nyq, 110/nyq
b, a = butter(4, [low, high], btype='band')
sig1_f = filtfilt(b, a, sig1)
sig2_f = filtfilt(b, a, sig2)

# GCC-PHAT
delay_est, corr = gcc_phat(sig1_f, sig2_f, fs, freq_range=(90, 110))
velocity_est = (d2 - d1) / delay_est

print(f"\nGCC-PHAT results:")
print(f"  Estimated delay: {delay_est*1000:.2f}ms")
print(f"  Estimated velocity: {velocity_est:.3f}m/s")
print(f"  Correlation: {corr:.4f}")

# Plot
fig, axes = plt.subplots(4, 1, figsize=(12, 12))

# Raw signals
axes[0].plot(t*1000, sig1, 'b-', alpha=0.7, label=f'R1 d={d1*1000:.0f}mm')
axes[0].plot(t*1000, sig2, 'r-', alpha=0.7, label=f'R2 d={d2*1000:.0f}mm')
axes[0].axvline(arrival1*1000, color='b', linestyle='--', alpha=0.5)
axes[0].axvline(arrival2*1000, color='r', linestyle='--', alpha=0.5)
axes[0].set_xlabel('Time (ms)')
axes[0].set_ylabel('Amplitude')
axes[0].set_title(f'Raw Signals @ {f_test}Hz - Expected delay: {(arrival2-arrival1)*1000:.2f}ms')
axes[0].legend()
axes[0].grid(True, alpha=0.3)
axes[0].set_xlim(40, 80)

# Filtered signals
axes[1].plot(t*1000, sig1_f, 'b-', alpha=0.7, label='R1 filtered')
axes[1].plot(t*1000, sig2_f, 'r-', alpha=0.7, label='R2 filtered')
axes[1].set_xlabel('Time (ms)')
axes[1].set_ylabel('Amplitude')
axes[1].set_title(f'Filtered Signals (90-110 Hz) - GCC-PHAT delay: {delay_est*1000:.2f}ms')
axes[1].legend()
axes[1].grid(True, alpha=0.3)
axes[1].set_xlim(40, 80)

# Cross-correlation (compute manually for plotting)
from scipy import signal
ccf = signal.correlate(sig2_f, sig1_f, mode='full')
lags = np.arange(-len(sig1_f)+1, len(sig1_f))
delays_ms = lags * dt * 1000

axes[2].plot(delays_ms, np.abs(ccf), 'g-', linewidth=1)
axes[2].axvline(delay_est*1000, color='r', linestyle='--', label=f'Peak: {delay_est*1000:.2f}ms')
axes[2].set_xlabel('Delay (ms)')
axes[2].set_ylabel('Correlation')
axes[2].set_title('Cross-Correlation')
axes[2].legend()
axes[2].grid(True, alpha=0.3)
# Zoom to expected range
expected_delay_ms = (arrival2 - arrival1) * 1000
axes[2].set_xlim(expected_delay_ms - 5, expected_delay_ms + 5)

# Zoomed view of filtered signals
axes[3].plot(t*1000, sig1_f, 'b-', alpha=0.7, label='R1')
axes[3].plot(t*1000, sig2_f, 'r-', alpha=0.7, label='R2')
axes[3].set_xlabel('Time (ms)')
axes[3].set_ylabel('Amplitude')
axes[3].set_title('Zoomed: Filtered Signals')
axes[3].legend()
axes[3].grid(True, alpha=0.3)
axes[3].set_xlim(arrival1*1000 - 3, arrival2*1000 + 3)

plt.tight_layout()
plt.savefig('gcc_debug_detailed.png', dpi=150)
print(f"\nSaved: gcc_debug_detailed.png")
