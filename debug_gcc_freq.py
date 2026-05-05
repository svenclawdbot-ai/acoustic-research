#!/usr/bin/env python3
"""Debug specific frequency band"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import hilbert, butter, filtfilt
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

# Generate signals
def make_signal(d, f_center, t_base):
    omega = 2 * np.pi * f_center
    G_mag = np.sqrt(G_prime**2 + (omega * eta)**2)
    c_f = np.sqrt(2 / rho) * np.sqrt(G_mag**2 / (G_prime + G_mag))
    
    arrival = t_base + d / c_f
    burst_width = 0.005
    envelope = np.exp(-((t - arrival)**2) / (2 * (burst_width/3)**2))
    carrier = np.sin(omega * (t - arrival))
    return envelope * carrier, arrival, c_f

# Test at 60 Hz and 140 Hz
for f_test in [60, 140]:
    print(f"\n{'='*50}")
    print(f"Frequency: {f_test} Hz")
    print(f"{'='*50}")
    
    t_base = 0.030 if f_test == 60 else 0.090
    
    sig1, arrival1, c1 = make_signal(d1, f_test, t_base)
    sig2, arrival2, c2 = make_signal(d2, f_test, t_base)
    
    # Add noise
    np.random.seed(42)
    noise_level = 0.15
    sig1 += noise_level * np.std(sig1) * np.random.randn(len(sig1))
    sig2 += noise_level * np.std(sig2) * np.random.randn(len(sig2))
    
    print(f"Expected arrival 1: {arrival1*1000:.2f} ms")
    print(f"Expected arrival 2: {arrival2*1002:.2f} ms")
    print(f"Expected delay: {(arrival2-arrival1)*1000:.2f} ms")
    print(f"Expected velocity: {(d2-d1)/(arrival2-arrival1):.3f} m/s")
    
    # Envelope-based coarse delay
    env1 = np.abs(hilbert(sig1))
    env2 = np.abs(hilbert(sig2))
    
    t_ms = np.arange(len(sig1)) * dt * 1000
    search_mask = (t_ms >= 30) & (t_ms <= 110)
    
    if np.any(search_mask):
        idx = np.where(search_mask)[0]
        peak1_idx = idx[np.argmax(env1[search_mask])]
        peak2_idx = idx[np.argmax(env2[search_mask])]
        coarse_delay = (peak2_idx - peak1_idx) * dt
        print(f"\nCoarse delay (envelope): {coarse_delay*1000:.2f} ms")
    
    # Filter
    nyq = fs / 2
    low, high = (f_test-15)/nyq, (f_test+15)/nyq
    b, a = butter(2, [low, high], btype='band')
    sig1_f = filtfilt(b, a, sig1)
    sig2_f = filtfilt(b, a, sig2)
    
    # GCC-PHAT
    delay_fine, corr = gcc_phat(sig1_f, sig2_f, fs, freq_range=(f_test-10, f_test+10))
    print(f"Fine delay (GCC-PHAT): {delay_fine*1000:.2f} ms")
    
    # Phase correction
    period = 1.0 / f_test
    delay_diff = delay_fine - coarse_delay
    n_periods = round(delay_diff / period)
    corrected_delay = delay_fine - n_periods * period
    
    print(f"Period at {f_test} Hz: {period*1000:.2f} ms")
    print(f"Periods to correct: {n_periods}")
    print(f"Corrected delay: {corrected_delay*1000:.2f} ms")
    print(f"Corrected velocity: {(d2-d1)/corrected_delay:.3f} m/s")
    
    # Plot
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    # Raw
    axes[0].plot(t_ms, sig1, 'b-', alpha=0.7, label=f'R1 d={d1*1000:.0f}mm')
    axes[0].plot(t_ms, sig2, 'r-', alpha=0.7, label=f'R2 d={d2*1000:.0f}mm')
    axes[0].axvline(arrival1*1000, color='b', linestyle='--', alpha=0.5)
    axes[0].axvline(arrival2*1000, color='r', linestyle='--', alpha=0.5)
    axes[0].set_xlabel('Time (ms)')
    axes[0].set_title(f'{f_test} Hz: Raw Signals')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    axes[0].set_xlim(20, 110)
    
    # Envelope
    axes[1].plot(t_ms, env1, 'b-', alpha=0.7, label='R1 envelope')
    axes[1].plot(t_ms, env2, 'r-', alpha=0.7, label='R2 envelope')
    axes[1].axvline(peak1_idx*dt*1000, color='b', linestyle='--', alpha=0.5)
    axes[1].axvline(peak2_idx*dt*1000, color='r', linestyle='--', alpha=0.5)
    axes[1].set_xlabel('Time (ms)')
    axes[1].set_title(f'Envelopes: Coarse delay = {coarse_delay*1000:.2f} ms')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    axes[1].set_xlim(20, 110)
    
    # Filtered
    axes[2].plot(t_ms, sig1_f, 'b-', alpha=0.7, label='R1 filtered')
    axes[2].plot(t_ms, sig2_f, 'r-', alpha=0.7, label='R2 filtered')
    axes[2].set_xlabel('Time (ms)')
    axes[2].set_title(f'Filtered ({f_test-15}-{f_test+15} Hz): Fine delay = {delay_fine*1000:.2f} ms')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    axes[2].set_xlim(20, 110)
    
    plt.tight_layout()
    plt.savefig(f'gcc_debug_{f_test}hz.png', dpi=150)
    print(f"\nSaved: gcc_debug_{f_test}hz.png")

