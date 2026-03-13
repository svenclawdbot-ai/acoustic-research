#!/usr/bin/env python3
"""
Broadband Multi-Frequency Group Velocity Extraction
====================================================

Uses chirp (swept frequency) source to excite all frequencies simultaneously.
Then extracts dispersion via cross-correlation of narrowband-filtered envelopes.

Author: Research Project
Date: March 13, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert, chirp, butter, filtfilt
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'research', 'week2'))

try:
    from shear_wave_2d_simple import ShearWave2D
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


def extract_arrival_at_frequency(sig1, sig2, dt, distance, 
                                 freq_center, freq_bw=15):
    """
    Extract arrival time difference at a specific frequency band.
    Returns time delay (not velocity) for more robust fitting.
    """
    nyquist = 1.0 / (2 * dt)
    low = max(0.02, (freq_center - freq_bw/2) / nyquist)
    high = min(0.98, (freq_center + freq_bw/2) / nyquist)
    
    if low >= high:
        return np.nan, 0
    
    try:
        b, a = butter(2, [low, high], btype='band')
        s1_filt = filtfilt(b, a, sig1)
        s2_filt = filtfilt(b, a, sig2)
    except:
        return np.nan, 0
    
    # Envelopes
    env1 = np.abs(hilbert(s1_filt))
    env2 = np.abs(hilbert(s2_filt))
    
    # Find peaks in window 45-100 ms
    t_ms = np.arange(len(env1)) * dt * 1000
    search_mask = (t_ms >= 45) & (t_ms <= 100)
    
    if not np.any(search_mask):
        return np.nan, 0
    
    search_indices = np.where(search_mask)[0]
    
    peak1_idx = search_indices[np.argmax(env1[search_mask])]
    peak2_idx = search_indices[np.argmax(env2[search_mask])]
    
    t1_ms = peak1_idx * dt * 1000
    t2_ms = peak2_idx * dt * 1000
    
    delay_ms = t2_ms - t1_ms
    
    # Quality: correlation coefficient of envelopes
    from scipy.stats import pearsonr
    try:
        corr, _ = pearsonr(env1[search_mask], env2[search_mask])
        quality = abs(corr)
    except:
        quality = 0
    
    return delay_ms, quality


def run_broadband_extraction(G_prime=2000, eta=0.5, rho=1000):
    """Run broadband multi-frequency validation."""
    
    print(f"\n{'='*60}")
    print(f"BROADBAND DISPERSION: G'={G_prime} Pa, η={eta} Pa·s")
    print(f"{'='*60}")
    
    # Simulation
    nx, ny = 400, 400
    dx = 0.0005
    pml_width = 20
    
    sim = ShearWave2D(nx=nx, ny=ny, dx=dx, 
                      rho=rho, G_prime=G_prime, eta=eta,
                      pml_width=pml_width)
    
    c_s = np.sqrt(G_prime / rho)
    print(f"\nTheory: c_s = {c_s:.2f} m/s")
    
    # Source and receivers
    source_x, source_y = nx // 2, ny // 2
    r1_pos = int(source_x + 0.005/dx)  # 5 mm
    r2_pos = int(source_x + 0.025/dx)  # 25 mm
    distance = 0.020  # 20 mm baseline
    
    print(f"  R1: 5 mm")
    print(f"  R2: 25 mm")
    print(f"  Baseline: {distance*1000:.0f} mm")
    
    # Run simulation with chirp source
    n_steps = 8000
    dt = sim.dt
    duration = n_steps * dt
    
    print(f"\nRunning {n_steps} steps ({duration*1000:.0f} ms)...")
    
    sig1 = []
    sig2 = []
    
    for n in range(n_steps):
        t = n * dt
        
        # Chirp source: 50-200 Hz over simulation duration
        # Only excite for first 80% of simulation
        if t < duration * 0.8:
            f_inst = 50 + (200 - 50) * (t / (duration * 0.8))
            amplitude = 1e-6
            source_val = amplitude * np.sin(2 * np.pi * 50 * t + 
                                            2 * np.pi * (200-50) * t**2 / (2 * duration * 0.8))
            sim.add_source(t, x_pos=source_x, y_pos=source_y,
                          amplitude=amplitude, f0=f_inst, source_type='tone_burst')
        
        sim.step()
        
        sig1.append(sim.u[r1_pos, source_y])
        sig2.append(sim.u[r2_pos, source_y])
    
    sig1 = np.array(sig1)
    sig2 = np.array(sig2)
    t_ms = np.arange(len(sig1)) * dt * 1000
    
    print("Complete. Extracting dispersion...")
    
    # Extract at multiple frequencies
    frequencies = np.arange(60, 181, 20)  # 60, 80, 100, ..., 180 Hz
    
    results = []
    for freq in frequencies:
        delay_ms, quality = extract_arrival_at_frequency(sig1, sig2, dt, distance, freq, freq_bw=15)
        
        if not np.isnan(delay_ms) and delay_ms > 0 and quality > 0.3:
            c_g = distance / (delay_ms * 1e-3)
            results.append({
                'freq': freq,
                'delay_ms': delay_ms,
                'c_g': c_g,
                'quality': quality
            })
            print(f"  {freq:3d} Hz: delay={delay_ms:.2f} ms, c_g={c_g:.2f} m/s, q={quality:.2f}")
        else:
            print(f"  {freq:3d} Hz: Failed (delay={delay_ms:.2f}, q={quality:.2f})")
    
    return {
        'G_prime': G_prime,
        'eta': eta,
        'rho': rho,
        'c_s': c_s,
        'sig1': sig1,
        'sig2': sig2,
        't_ms': t_ms,
        'results': results,
        'distance': distance
    }


def plot_broadband(data, save_path='broadband_dispersion.png'):
    """Plot broadband extraction results."""
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    G_prime = data['G_prime']
    eta = data['eta']
    rho = data['rho']
    c_s = data['c_s']
    results = data['results']
    
    fig.suptitle(f'Broadband Dispersion: G\'={G_prime} Pa, η={eta} Pa·s',
                 fontsize=11)
    
    # Plot 1: Raw signals
    ax1 = axes[0, 0]
    ax1.plot(data['t_ms'], data['sig1'] * 1e6, 'b-', alpha=0.6, label='R1 (5mm)', linewidth=0.5)
    ax1.plot(data['t_ms'], data['sig2'] * 1e6, 'r-', alpha=0.6, label='R2 (25mm)', linewidth=0.5)
    ax1.set_xlabel('Time (ms)')
    ax1.set_ylabel('Displacement (μm)')
    ax1.set_title('Broadband Receiver Signals')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Spectrogram-style view
    ax2 = axes[0, 1]
    sig = data['sig1']
    dt_s = (data['t_ms'][1] - data['t_ms'][0]) * 1e-3
    
    # Plot filtered envelopes at different frequencies
    colors = plt.cm.viridis(np.linspace(0, 1, len(results)))
    for i, r in enumerate(results):
        freq = r['freq']
        nyquist = 1.0 / (2 * dt_s)
        low = max(0.02, (freq - 10) / nyquist)
        high = min(0.98, (freq + 10) / nyquist)
        try:
            b, a = butter(2, [low, high], btype='band')
            sig_filt = filtfilt(b, a, sig)
            env = np.abs(hilbert(sig_filt))
            ax2.plot(data['t_ms'], env * 1e6 + i * 0.5, color=colors[i], 
                    label=f'{freq} Hz', linewidth=1)
        except:
            pass
    
    ax2.set_xlabel('Time (ms)')
    ax2.set_ylabel('Envelope (μm, offset)')
    ax2.set_title('Bandpass Filtered Envelopes')
    ax2.legend(fontsize=7)
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Dispersion curve
    ax3 = axes[1, 0]
    
    # Theoretical
    if results:
        f_theory = np.linspace(50, 200, 100)
        omega = 2 * np.pi * f_theory
        G_mag = np.sqrt(G_prime**2 + (omega * eta)**2)
        c_theory = np.sqrt(2 / rho) * np.sqrt(G_mag**2 / (G_prime + G_mag))
        ax3.plot(f_theory, c_theory, 'k-', linewidth=2, label='Kelvin-Voigt theory')
    
    ax3.axhline(c_s, color='gray', linestyle='--', alpha=0.5, label=f'Elastic: {c_s:.2f} m/s')
    
    # Extracted
    if results:
        freqs = [r['freq'] for r in results]
        c_g = [r['c_g'] for r in results]
        qualities = [r['quality'] for r in results]
        sizes = [100 + 400 * q for q in qualities]
        ax3.scatter(freqs, c_g, s=sizes, c='red', alpha=0.6, label='Extracted', zorder=5)
    
    ax3.set_xlabel('Frequency (Hz)')
    ax3.set_ylabel('Group velocity (m/s)')
    ax3.set_title('Dispersion Curve')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim(1.2, 2.2)
    
    # Plot 4: Time delay vs frequency
    ax4 = axes[1, 1]
    
    if results:
        freqs = [r['freq'] for r in results]
        delays = [r['delay_ms'] for r in results]
        
        ax4.scatter(freqs, delays, s=100, c='blue', alpha=0.6)
        
        # Theoretical delay
        if results:
            f_theory = np.array([r['freq'] for r in results])
            omega = 2 * np.pi * f_theory
            G_mag = np.sqrt(G_prime**2 + (omega * eta)**2)
            c_theory = np.sqrt(2 / rho) * np.sqrt(G_mag**2 / (G_prime + G_mag))
            delay_theory = data['distance'] / c_theory * 1000  # ms
            ax4.plot(f_theory, delay_theory, 'k-', linewidth=2, label='Theory')
        
        ax4.set_xlabel('Frequency (Hz)')
        ax4.set_ylabel('Time delay (ms)')
        ax4.set_title('Arrival Time Delay vs Frequency')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Saved: {save_path}")


def main():
    """Run broadband validation."""
    
    print("BROADBAND MULTI-FREQUENCY EXTRACTION")
    print("="*60)
    
    data = run_broadband_extraction(G_prime=2000, eta=0.3, rho=1000)
    
    plot_broadband(data, save_path='broadband_G2000_eta0.3.png')
    
    print("\n" + "="*60)
    print("EXTRACTION SUMMARY")
    print("="*60)
    print(f"Extracted {len(data['results'])} frequency points")
    
    if data['results']:
        print("\nDispersion data:")
        for r in data['results']:
            print(f"  {r['freq']:3d} Hz: c_g = {r['c_g']:.2f} m/s (q={r['quality']:.2f})")
    
    print("\n" + "="*60)
    print("READY FOR INVERSE PROBLEM")
    print("="*60)
    print("Fit c(ω) to recover G' and η")


if __name__ == '__main__':
    main()
