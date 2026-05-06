#!/usr/bin/env python3
"""
Debug version to understand why extraction fails
"""
import numpy as np
from scipy.signal import hilbert, butter, filtfilt
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from subsample_gcc import gcc_phat

# Generate a single test case
fs = 20000
dt = 1.0 / fs
t = np.linspace(0, 0.12, int(fs * 0.12))

# Two receivers at 5mm and 35mm
d1, d2 = 0.005, 0.035
distance = d2 - d1

# 100 Hz signal with expected velocity ~1.4 m/s
f_center = 100
period = 1.0 / f_center
expected_delay = distance / 1.4  # ~21.4 ms

print(f"Test: {f_center} Hz, distance = {distance*1000:.0f} mm")
print(f"Expected delay: {expected_delay*1000:.1f} ms ({expected_delay/period:.2f} periods)")

# Generate signals
omega = 2 * np.pi * f_center
arrival1 = 0.045 + d1 / 1.4
arrival2 = 0.045 + d2 / 1.4

env1 = np.exp(-((t - arrival1)**2) / (2 * (0.005/3)**2))
carrier1 = np.sin(omega * (t - arrival1))
s1 = env1 * carrier1

env2 = np.exp(-((t - arrival2)**2) / (2 * (0.005/3)**2))
carrier2 = np.sin(omega * (t - arrival2))
s2 = env2 * carrier2

# Add 10% noise
s1 = s1 / np.max(np.abs(s1))
s2 = s2 / np.max(np.abs(s2))
noise = 0.10
s1 += noise * np.std(s1) * np.random.randn(len(s1))
s2 += noise * np.std(s2) * np.random.randn(len(s2))

print(f"\nSignal 1 peak at {arrival1*1000:.1f} ms")
print(f"Signal 2 peak at {arrival2*1000:.1f} ms")

# Filter
nyq = fs / 2
low = max(0.01, (f_center - 12) / nyq)
high = min(0.99, (f_center + 12) / nyq)
b, a = butter(2, [low, high], btype='band')
s1_f = filtfilt(b, a, s1)
s2_f = filtfilt(b, a, s2)

# Envelope method
env1 = np.abs(hilbert(s1_f))
env2 = np.abs(hilbert(s2_f))
t_ms = np.arange(len(env1)) * dt * 1000
search = (t_ms > 15) & (t_ms < 110)
idx = np.where(search)[0]
p1 = idx[np.argmax(env1[search])]
p2 = idx[np.argmax(env2[search])]
coarse_delay = (p2 - p1) * dt

print(f"\nEnvelope method:")
print(f"  Peak indices: {p1}, {p2}")
print(f"  Coarse delay: {coarse_delay*1000:.1f} ms")
print(f"  Coarse velocity: {distance/coarse_delay:.2f} m/s")

# GCC-PHAT
delay_fine, corr = gcc_phat(s1_f, s2_f, fs, freq_range=(f_center-10, f_center+10))

print(f"\nGCC-PHAT:")
print(f"  Fine delay (raw): {delay_fine*1000:.1f} ms")
print(f"  Correlation: {corr:.3f}")

# Phase ambiguity resolution
n_periods = round((delay_fine - coarse_delay) / period)
delay_corrected = delay_fine - n_periods * period

print(f"\nPhase ambiguity resolution:")
print(f"  Period: {period*1000:.1f} ms")
print(f"  n_periods: {n_periods}")
print(f"  Corrected delay: {delay_corrected*1000:.1f} ms")
print(f"  Corrected velocity: {distance/delay_corrected:.2f} m/s")

# Validation
print(f"\nValidation:")
print(f"  Difference from coarse: {abs(delay_corrected - coarse_delay)*1000:.1f} ms")
print(f"  Half period: {period*1000/2:.1f} ms")
print(f"  Is valid (< half period): {abs(delay_corrected - coarse_delay) < period/2}")
print(f"  Correlation > 0.5: {abs(corr) > 0.5}")
print(f"  Velocity in range [0.8, 2.5]: {0.8 <= distance/delay_corrected <= 2.5}")
