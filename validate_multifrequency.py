#!/usr/bin/env python3
"""
Multi-Frequency Group Velocity Extraction
==========================================

Extract dispersion curves from broadband shear wave data.
Uses multiple bandpass filters to get c_g at different frequencies.

This enables recovery of G' and η from dispersion: c(ω)

Author: Research Project
Date: March 13, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert, butter, filtfilt
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'research', 'week2'))

try:
    from shear_wave_2d_simple import ShearWave2D
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


def extract_group_velocity_at_frequency(sig1, sig2, dt, distance, 
                                        freq_center, freq_bw=20):
    """
    Extract group velocity at a specific frequency band.
    
    Parameters:
    -----------
    freq_center : float
        Center frequency (Hz)
    freq_bw : float
        Bandwidth (Hz) — total width is ±freq_bw/2
    
    Returns:
    --------
    c_g : float
        Group velocity at this frequency (m/s)
    quality : float
        Quality metric (peak envelope value)
    """
    # Bandpass filter for this frequency band
    nyquist = 1.0 / (2 * dt)
    low = (freq_center - freq_bw/2) / nyquist
    high = (freq_center + freq_bw/2) / nyquist
    
    # Ensure valid range
    low = max(0.01, min(low, 0.99))
    high = max(0.01, min(high, 0.99))
    
    if low >= high:
        return np.nan, 0.0
    
    try:
        b, a = butter(2, [low, high], btype='band')
        s1_filt = filtfilt(b, a, sig1)
        s2_filt = filtfilt(b, a, sig2)
    except:
        return np.nan, 0.0
    
    # Envelopes
    env1 = np.abs(hilbert(s1_filt))
    env2 = np.abs(hilbert(s2_filt))
    
    # Quality: peak value in search window
    t = np.arange(len(env1)) * dt * 1000
    search_mask = (t >= 45) & (t <= 80)
    
    if not np.any(search_mask):
        return np.nan, 0.0
    
    quality = np.max(env1[search_mask]) + np.max(env2[search_mask])
    
    # Find peaks
    search_indices = np.where(search_mask)[0]
    peak1_idx = search_indices[np.argmax(env1[search_mask])]
    peak2_idx = search_indices[np.argmax(env2[search_mask])]
    
    t1_ms = peak1_idx * dt * 1000
    t2_ms = peak2_idx * dt * 1000
    delay_s = (t2_ms - t1_ms) * 1e-3
    
    if delay_s <= 0:
        return np.nan, quality
    
    c_g = distance / delay_s
    
    return c_g, quality


def extract_dispersion_curve(sig1, sig2, dt, distance, 
                             freq_bands=None):
    """
    Extract group velocity dispersion curve.
    
    Returns c_g at multiple frequencies.
    """
    if freq_bands is None:
        # Default: 50-250 Hz in 20 Hz steps
        freq_bands = [(f, 20) for f in range(50, 251, 20)]
    
    results = []
    for freq_center, freq_bw in freq_bands:
        c_g, quality = extract_group_velocity_at_frequency(
            sig1, sig2, dt, distance, freq_center, freq_bw
        )
        
        results.append({
            'freq': freq_center,
            'c_g': c_g,
            'quality': quality
        })
    
    return results


def theoretical_dispersion(G_prime, eta, rho, frequencies):
    """
    Theoretical Kelvin-Voigt dispersion curve.
    
    c_p(ω) = sqrt(2/rho) * sqrt(|G*|^2 / (G' + |G*|))
    
    For low viscosity: c_p ≈ sqrt(G'/rho) * (1 + small correction)
    """
    omega = 2 * np.pi * np.array(frequencies)
    G_mag = np.sqrt(G_prime**2 + (omega * eta)**2)
    c_p = np.sqrt(2 / rho) * np.sqrt(G_mag**2 / (G_prime + G_mag))
    return c_p


def run_multifrequency_extraction(G_prime=2000, eta=0.5, rho=1000, 
                                  n_receivers=3, source_freq=100):
    """Run multi-frequency validation."""
    
    print(f"\n{'='*60}")
    print(f"MULTI-FREQUENCY EXTRACTION: G'={G_prime} Pa, η={eta} Pa·s")
    print(f"{'='*60}")
    
    # Simulation
    nx, ny = 400, 400  # Larger domain for longer propagation
    dx = 0.0005
    pml_width = 20
    
    sim = ShearWave2D(nx=nx, ny=ny, dx=dx, 
                      rho=rho, G_prime=G_prime, eta=eta,
                      pml_width=pml_width)
    
    c_s = np.sqrt(G_prime / rho)
    print(f"\nTheory: c_s = {c_s:.2f} m/s")
    
    # Source and receivers (longer baseline for better frequency resolution)
    source_x, source_y = nx // 2, ny // 2
    distances_m = np.array([0.005, 0.015, 0.025])[:n_receivers]  # 5, 15, 25 mm
    
    receiver_positions = []
    for i, d in enumerate(distances_m):
        rx = int(source_x + d/dx)
        ry = source_y
        receiver_positions.append((rx, ry))
        print(f"  R{i+1}: {d*1000:.0f} mm")
    
    # Run simulation with longer duration for lower frequencies
    n_steps = 6000  # Longer for 50 Hz waves
    source_duration = 10  # More cycles for narrower bandwidth
    dt = sim.dt
    
    time_signals = [[] for _ in range(n_receivers)]
    
    print(f"\nRunning {n_steps} steps (dt={dt*1e6:.1f} μs)...")
    for n in range(n_steps):
        t = n * dt
        
        # Broadband source: swept tone or multiple frequencies
        if n < int(source_duration / source_freq / dt):
            sim.add_source(t, x_pos=source_x, y_pos=source_y,
                          amplitude=1e-6, f0=source_freq, source_type='tone_burst')
        
        sim.step()
        
        for i, (rx, ry) in enumerate(receiver_positions):
            time_signals[i].append(sim.u[rx, ry])
    
    time_signals = [np.array(sig) for sig in time_signals]
    t_ms = np.arange(len(time_signals[0])) * dt * 1000
    
    # Extract dispersion curves
    print(f"\nEXTRACTING DISPERSION CURVES:")
    print(f"{'='*60}")
    
    # Use R1-R3 pair (20mm baseline) for best frequency resolution
    sig1 = time_signals[0]
    sig3 = time_signals[2]
    distance = distances_m[2] - distances_m[0]  # 20 mm
    
    # Frequency bands
    freq_bands = [(f, 20) for f in range(50, 201, 25)]  # 50, 75, 100, ..., 200 Hz
    
    dispersion = extract_dispersion_curve(sig1, sig3, dt, distance, freq_bands)
    
    # Filter valid results
    valid_results = [r for r in dispersion if not np.isnan(r['c_g'])]
    
    print(f"\nExtracted {len(valid_results)}/{len(dispersion)} frequency points:")
    for r in valid_results:
        c_theory = theoretical_dispersion(G_prime, eta, rho, [r['freq']])[0]
        error = 100 * abs(r['c_g'] - c_theory) / c_theory
        print(f"  {r['freq']:3d} Hz: c_g = {r['c_g']:.2f} m/s "
              f"(theory: {c_theory:.2f}, error: {error:+.1f}%, q={r['quality']:.2e})")
    
    return {
        'G_prime': G_prime,
        'eta': eta,
        'rho': rho,
        'c_s': c_s,
        'distances': distances_m,
        'time_signals': time_signals,
        't_ms': t_ms,
        'dispersion': valid_results,
        'distance_baseline': distance
    }


def plot_multifrequency(data, save_path='multifrequency_dispersion.png'):
    """Plot multi-frequency extraction results."""
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    G_prime = data['G_prime']
    eta = data['eta']
    rho = data['rho']
    c_s = data['c_s']
    
    fig.suptitle(f'Multi-Frequency Dispersion: G\'={G_prime} Pa, η={eta} Pa·s',
                 fontsize=11)
    
    time_signals = data['time_signals']
    t_ms = data['t_ms']
    dispersion = data['dispersion']
    
    colors = ['blue', 'red', 'green']
    
    # Plot 1: Raw signals
    ax1 = axes[0, 0]
    for i, sig in enumerate(time_signals):
        ax1.plot(t_ms, sig * 1e6, color=colors[i], alpha=0.5, 
                label=f'R{i+1} ({data["distances"][i]*1000:.0f}mm)', linewidth=0.5)
    ax1.set_xlabel('Time (ms)')
    ax1.set_ylabel('Displacement (μm)')
    ax1.set_title('Receiver Signals')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Filtered signals at different frequencies
    ax2 = axes[0, 1]
    sig1 = time_signals[0]
    dt = t_ms[1] - t_ms[0]
    dt_s = dt * 1e-3
    
    # Show filtered versions
    freq_examples = [50, 100, 150]
    for freq in freq_examples:
        nyquist = 1.0 / (2 * dt_s)
        low = (freq - 10) / nyquist
        high = (freq + 10) / nyquist
        try:
            b, a = butter(2, [max(0.01, low), min(0.99, high)], btype='band')
            sig_filt = filtfilt(b, a, sig1)
            ax2.plot(t_ms, sig_filt * 1e6, alpha=0.6, label=f'{freq} Hz')
        except:
            pass
    
    ax2.set_xlabel('Time (ms)')
    ax2.set_ylabel('Displacement (μm)')
    ax2.set_title('Bandpass Filtered Signals (R1)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Dispersion curve
    ax3 = axes[1, 0]
    
    # Theoretical curve
    f_theory = np.linspace(40, 220, 100)
    c_theory = theoretical_dispersion(G_prime, eta, rho, f_theory)
    ax3.plot(f_theory, c_theory, 'k-', linewidth=2, label='Theory (Kelvin-Voigt)')
    ax3.axhline(c_s, color='gray', linestyle='--', alpha=0.5, 
               label=f'Elastic limit: {c_s:.2f} m/s')
    
    # Extracted points
    if dispersion:
        freqs = [r['freq'] for r in dispersion]
        c_g = [r['c_g'] for r in dispersion]
        qualities = [r['quality'] for r in dispersion]
        
        # Size proportional to quality
        sizes = [50 + 500 * q / max(qualities) for q in qualities]
        
        ax3.scatter(freqs, c_g, s=sizes, c='red', alpha=0.6, 
                   label='Extracted c_g', zorder=5)
    
    ax3.set_xlabel('Frequency (Hz)')
    ax3.set_ylabel('Group velocity (m/s)')
    ax3.set_title('Dispersion Curve')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim(1.0, 2.5)
    
    # Plot 4: Error vs frequency
    ax4 = axes[1, 1]
    
    if dispersion:
        errors = []
        for r in dispersion:
            c_th = theoretical_dispersion(G_prime, eta, rho, [r['freq']])[0]
            err = 100 * (r['c_g'] - c_th) / c_th
            errors.append(err)
        
        freqs = [r['freq'] for r in dispersion]
        
        ax4.scatter(freqs, errors, s=100, c='blue', alpha=0.6)
        ax4.axhline(0, color='black', linewidth=1)
        ax4.axhline(np.mean(errors), color='red', linestyle='--',
                   label=f'Mean: {np.mean(errors):.1f}%')
        
        ax4.set_xlabel('Frequency (Hz)')
        ax4.set_ylabel('Error (%)')
        ax4.set_title('Extraction Error vs Frequency')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.set_ylim(-30, 30)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"\nSaved: {save_path}")


def main():
    """Run multi-frequency validation."""
    
    print("MULTI-FREQUENCY GROUP VELOCITY EXTRACTION")
    print("="*60)
    
    test_cases = [
        (2000, 0.3, "Low viscosity (long propagation)"),
        (2000, 0.5, "Medium viscosity"),
    ]
    
    for G_prime, eta, desc in test_cases:
        print(f"\n\n{'='*60}")
        print(f"TEST: {desc}")
        print(f"{'='*60}")
        
        data = run_multifrequency_extraction(
            G_prime=G_prime, eta=eta, rho=1000,
            n_receivers=3, source_freq=100
        )
        
        plot_multifrequency(data,
            save_path=f'multifreq_G{G_prime}_eta{eta}.png')
    
    print("\n" + "="*60)
    print("MULTI-FREQUENCY EXTRACTION COMPLETE")
    
    print("\n" + "="*60)
    print("NEXT STEP: INVERSE PROBLEM")
    print("="*60)
    print("Fit extracted c(ω) to Kelvin-Voigt model to recover G' and η")
    print("Approach: Bayesian inference or least-squares optimization")


if __name__ == '__main__':
    main()
