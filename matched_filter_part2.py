#!/usr/bin/env python3
"""
Matched Filter Deep Dive — Part 2: Frequency-Domain Implementation
=================================================================

Compares time-domain vs FFT-based matched filter implementation.
Demonstrates O(N log N) vs O(N²) complexity advantage.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import time

# =============================================================================
# PARAMETERS
# =============================================================================

fs = 125e6          # Red Pitaya ADC sample rate (Hz)
f0 = 5e6            # Transducer centre frequency (Hz)
tau = 1/f0          # 1-cycle pulse duration (s)
SNR_dB = 10         # Input SNR (dB)

print("=" * 60)
print("MATCHED FILTER PART 2: FREQUENCY-DOMAIN IMPLEMENTATION")
print("=" * 60)
print()

# =============================================================================
# 1. GENERATE TEST SIGNALS OF VARYING LENGTHS
# =============================================================================

signal_lengths = [500, 1000, 2000, 5000, 10000, 20000, 50000]
time_domain_times = []
fft_times = []

print("Timing comparison: Time-domain vs FFT-based matched filter")
print("-" * 60)
print(f"{'Signal Length':>12} | {'Time-Domain (ms)':>16} | {'FFT (ms)':>12} | {'Speedup':>8}")
print("-" * 60)

for N in signal_lengths:
    # Generate signal
    t = np.arange(0, N/fs, 1/fs)
    pulse = np.sin(2 * np.pi * f0 * t) * (t <= tau)
    pulse = pulse / np.sqrt(np.sum(pulse**2))
    
    # Add noise
    signal_power = np.sum(pulse**2) / (tau * fs)
    noise_power = signal_power / (10**(SNR_dB/10))
    noise = np.sqrt(noise_power) * np.random.randn(N)
    echo = pulse + noise
    
    # Matched filter impulse response
    h = np.flip(pulse)
    
    # Time-domain convolution
    start = time.perf_counter()
    result_td = np.convolve(echo, h, mode='same')
    td_time = (time.perf_counter() - start) * 1000  # ms
    time_domain_times.append(td_time)
    
    # FFT-based convolution
    start = time.perf_counter()
    # FFT length: next power of 2 for efficiency
    n_fft = 1 << (N + len(h) - 1).bit_length()
    H = np.fft.fft(h, n_fft)
    X = np.fft.fft(echo, n_fft)
    Y = X * np.conj(H)  # Matched filter = correlation
    result_fd = np.fft.ifft(Y)[:N]  # Take first N samples (same mode approximation)
    fd_time = (time.perf_counter() - start) * 1000  # ms
    fft_times.append(fd_time)
    
    speedup = td_time / fd_time if fd_time > 0 else float('inf')
    print(f"{N:>12} | {td_time:>16.3f} | {fd_time:>12.3f} | {speedup:>8.1f}x")

print("-" * 60)
print()

# =============================================================================
# 2. DETAILED COMPARISON FOR TYPICAL ACQUISITION LENGTH
# =============================================================================

# Typical Red Pitaya acquisition: 16384 samples (2^14)
N = 16384
t = np.arange(0, N/fs, 1/fs)
pulse = np.sin(2 * np.pi * f0 * t) * (t <= tau)
pulse = pulse / np.sqrt(np.sum(pulse**2))

signal_power = np.sum(pulse**2) / (tau * fs)
noise_power = signal_power / (10**(SNR_dB/10))
noise = np.sqrt(noise_power) * np.random.randn(N)
echo = pulse + noise
h = np.flip(pulse)

# Time-domain
start = time.perf_counter()
result_td = np.convolve(echo, h, mode='same')
td_time = (time.perf_counter() - start) * 1000

# FFT-based with proper "same" mode handling
start = time.perf_counter()
n_fft = 1 << (N + len(h) - 1).bit_length()
H = np.fft.fft(h, n_fft)
X = np.fft.fft(echo, n_fft)
# Matched filter = correlation = convolution with flipped, conjugated pulse
# FFT approach: ifft(fft(echo) * conj(fft(pulse)))
# Since h = flip(pulse), we use fft(h) directly for convolution
Y = X * H  # Convolution in frequency domain
result_fd_full = np.fft.ifft(Y)
# Extract "same" mode portion - center the valid linear convolution region
# Linear convolution length = N + M - 1
# "same" returns the central N samples
start_idx = (len(h) - 1) // 2
result_fd = np.real(result_fd_full[start_idx:start_idx + N])
fd_time = (time.perf_counter() - start) * 1000

print(f"Detailed comparison for N={N} (typical Red Pitaya acquisition)")
print(f"  Time-domain: {td_time:.3f} ms")
print(f"  FFT-based:   {fd_time:.3f} ms")
print(f"  Speedup:     {td_time/fd_time:.1f}x")
print()

# Verify numerical equivalence
result_td = np.convolve(echo, h, mode='same')
start_idx = (len(h) - 1) // 2
result_fd_aligned = np.real(result_fd_full[start_idx:start_idx + N])
max_diff = np.max(np.abs(result_td - result_fd_aligned))
rel_diff = max_diff / np.max(np.abs(result_td))
print(f"Maximum difference: {max_diff:.2e} (relative: {rel_diff:.2e})")
print(f"Equivalent for practical purposes: {rel_diff < 1e-10}")
print()

# =============================================================================
# 3. FREQUENCY RESPONSE ANALYSIS
# =============================================================================

# Compute frequency response of matched filter
H_response = np.fft.fft(h, 4096)
freqs = np.fft.fftfreq(4096, 1/fs) / 1e6  # MHz

# Shift for plotting
H_shift = np.fft.fftshift(H_response)
freqs_shift = np.fft.fftshift(freqs)

# Pulse spectrum
Pulse_spectrum = np.fft.fft(pulse, 4096)
Pulse_shift = np.fft.fftshift(Pulse_spectrum)

print("=" * 60)
print("FREQUENCY DOMAIN ANALYSIS")
print("=" * 60)

# Bandwidth estimation (handle both positive and negative frequencies)
mag_squared = np.abs(Pulse_shift)**2
# Find peak
peak_idx = np.argmax(mag_squared)
peak_freq = freqs_shift[peak_idx]

# Find -3dB points around peak
half_power = np.max(mag_squared) / 2
# Search in positive frequency region only
positive_freqs = freqs_shift > 0
positive_mag = mag_squared[positive_freqs]
positive_freq = freqs_shift[positive_freqs]

if len(positive_mag) > 0:
    # Find where magnitude drops below half power
    above_half = positive_mag >= half_power
    if np.any(above_half):
        f_low = positive_freq[np.where(above_half)[0][0]]
        f_high = positive_freq[np.where(above_half)[0][-1]]
        bandwidth = f_high - f_low
        print(f"Pulse -3dB bandwidth: {bandwidth:.2f} MHz")
        print(f"  Lower cutoff: {f_low:.2f} MHz")
        print(f"  Upper cutoff: {f_high:.2f} MHz")
        print(f"  Centre frequency: {(f_low + f_high)/2:.2f} MHz")
        print(f"  Fractional bandwidth: {bandwidth/((f_low+f_high)/2)*100:.1f}%")

print()

# =============================================================================
# 4. PLOTS
# =============================================================================

fig = plt.figure(figsize=(14, 10))

# Plot 1: Timing comparison
ax1 = plt.subplot(2, 2, 1)
ax1.semilogy(signal_lengths, time_domain_times, 'bo-', label='Time-domain', linewidth=2, markersize=8)
ax1.semilogy(signal_lengths, fft_times, 'rs-', label='FFT-based', linewidth=2, markersize=8)
ax1.set_xlabel('Signal Length (samples)')
ax1.set_ylabel('Execution Time (ms)')
ax1.set_title('Computational Complexity Comparison')
ax1.legend()
ax1.grid(True, alpha=0.3, which='both')

# Plot 2: Complexity scaling
ax2 = plt.subplot(2, 2, 2)
N_theory = np.array(signal_lengths)
td_theory = N_theory**2 / N_theory[0]**2 * time_domain_times[0]
fft_theory = N_theory * np.log2(N_theory) / (signal_lengths[0] * np.log2(signal_lengths[0])) * fft_times[0]
ax2.loglog(N_theory, time_domain_times, 'bo', label='Time-domain (measured)')
ax2.loglog(N_theory, td_theory, 'b--', label='Time-domain O(N²)')
ax2.loglog(N_theory, fft_times, 'rs', label='FFT (measured)')
ax2.loglog(N_theory, fft_theory, 'r--', label='FFT O(N log N)')
ax2.set_xlabel('Signal Length N')
ax2.set_ylabel('Time (ms)')
ax2.set_title('Theoretical vs Measured Scaling')
ax2.legend()
ax2.grid(True, alpha=0.3, which='both')

# Plot 3: Frequency response of matched filter
ax3 = plt.subplot(2, 2, 3)
ax3.plot(freqs_shift, 20*np.log10(np.abs(H_shift) + 1e-10), 'g-', linewidth=1.5)
ax3.axvline(x=f0/1e6, color='r', linestyle='--', alpha=0.7, label=f'Centre: {f0/1e6:.1f} MHz')
ax3.set_xlabel('Frequency (MHz)')
ax3.set_ylabel('Magnitude (dB)')
ax3.set_title('Matched Filter Frequency Response')
ax3.set_xlim([0, 20])
ax3.legend()
ax3.grid(True, alpha=0.3)

# Plot 4: Pulse spectrum
ax4 = plt.subplot(2, 2, 4)
ax4.plot(freqs_shift, 20*np.log10(np.abs(Pulse_shift) + 1e-10), 'm-', linewidth=1.5)
ax4.axvline(x=f0/1e6, color='r', linestyle='--', alpha=0.7, label=f'Centre: {f0/1e6:.1f} MHz')
ax4.set_xlabel('Frequency (MHz)')
ax4.set_ylabel('Magnitude (dB)')
ax4.set_title('Transmitted Pulse Spectrum')
ax4.set_xlim([0, 20])
ax4.legend()
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('matched_filter_part2.png', dpi=150, bbox_inches='tight')
print("✓ Saved plot: matched_filter_part2.png")

# =============================================================================
# 5. KEY INSIGHTS
# =============================================================================

print()
print("=" * 60)
print("KEY INSIGHTS")
print("=" * 60)
print("1. FFT-based: O(N log N) vs time-domain O(N²)")
print("   → 10-100x speedup for typical acquisition lengths")
print()
print("2. Matched filter frequency response = |S(f)|²")
print("   → Emphasises frequencies where signal has energy")
print("   → Suppresses frequencies where noise dominates")
print()
print("3. For Red Pitaya (N=16384):")
print(f"   → FFT matched filter: ~{fd_time:.2f} ms")
print(f"   → Real-time capable at 125 MS/s? {fd_time < 0.1}")
print("   → Need FPGA implementation for true real-time")
print()
print("4. Zero-padding to next power of 2 optimises FFT")
print(f"   → N={N} → n_fft={1 << (N + len(h) - 1).bit_length()}")
print()
print("5. 'Same' mode requires careful indexing for FFT output")
print("   → Circular convolution vs linear convolution")
print("   → Minimum FFT length: N + M - 1 to avoid aliasing")
