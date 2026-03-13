#!/usr/bin/env python3
"""
Refined Group Velocity Extraction
=================================

Improved methods for robust group velocity measurement:
1. Adaptive windowing based on expected arrival
2. First-peak detection (not global maximum)
3. Multi-frequency broadband extraction
4. Quality metrics for measurement validation

Author: Research Project — Refined Validation
Date: March 13, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert, butter, filtfilt, find_peaks
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'research', 'week2'))

try:
    from shear_wave_2d_simple import ShearWave2D
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


def find_first_peak(envelope, threshold_percent=10, min_distance_samples=10):
    """
    Find the first significant peak in the envelope.
    
    More robust than global maximum for wave arrival detection.
    """
    threshold = threshold_percent / 100.0 * np.max(envelope)
    
    # Find all peaks above threshold
    peaks, properties = find_peaks(envelope, height=threshold, 
                                   distance=min_distance_samples)
    
    if len(peaks) == 0:
        return np.argmax(envelope)  # Fallback to global max
    
    return peaks[0]  # Return first peak


def extract_arrival_time(signal, dt, freq_range, 
                         expected_arrival=None, window_margin=2.0,
                         method='first_peak'):
    """
    Extract wave arrival time using envelope analysis.
    
    Parameters:
    -----------
    signal : array
        Time signal
    dt : float
        Time step (s)
    freq_range : tuple
        Bandpass filter range (Hz)
    expected_arrival : float or None
        Expected arrival time (s) for windowing. None = use full signal
    window_margin : float
        Window margin around expected arrival (multiplier)
    method : str
        'first_peak', 'centroid', or 'max'
        
    Returns:
    --------
    arrival_time : float
        Arrival time (s)
    envelope : array
        Signal envelope
    quality : float
        Quality metric (0-1, higher is better)
    """
    # Bandpass filter
    nyquist = 1.0 / (2 * dt)
    low = freq_range[0] / nyquist
    high = freq_range[1] / nyquist
    b, a = butter(4, [low, high], btype='band')
    sig_filt = filtfilt(b, a, signal)
    
    # Compute envelope
    envelope = np.abs(hilbert(sig_filt))
    
    # Apply time window if expected arrival given
    if expected_arrival is not None:
        margin = expected_arrival * (window_margin - 1)
        start_time = max(0, expected_arrival - margin)
        end_time = expected_arrival + margin * 3  # Allow later arrivals
        
        start_idx = int(start_time / dt)
        end_idx = int(end_time / dt)
        start_idx = max(0, start_idx)
        end_idx = min(len(envelope), end_idx)
        
        # Create windowed version
        windowed_env = np.zeros_like(envelope)
        windowed_env[start_idx:end_idx] = envelope[start_idx:end_idx]
    else:
        windowed_env = envelope
        start_idx = 0
    
    # Find arrival based on method
    if method == 'first_peak':
        arrival_idx = find_first_peak(windowed_env, threshold_percent=5)
    elif method == 'max':
        arrival_idx = np.argmax(windowed_env)
    elif method == 'centroid':
        # Center of mass of envelope
        t = np.arange(len(envelope)) * dt
        arrival_idx = int(np.sum(t * windowed_env) / np.sum(windowed_env) / dt)
    else:
        raise ValueError(f"Unknown method: {method}")
    
    arrival_time = arrival_idx * dt
    
    # Quality metric: SNR of peak vs background
    peak_val = envelope[arrival_idx]
    background = np.mean(envelope[envelope < np.percentile(envelope, 50)])
    quality = peak_val / (background + 1e-10)
    quality = min(quality / 10.0, 1.0)  # Normalize to 0-1
    
    return arrival_time, envelope, quality


def extract_group_velocity_refined(sig1, sig2, dt, distance, c_expected=1.5,
                                   freq_range=(50, 150), verbose=False):
    """
    Refined group velocity extraction with quality control.
    
    Parameters:
    -----------
    c_expected : float
        Expected wave speed for initial window (m/s)
        
    Returns:
    --------
    c_g : float
        Group velocity (m/s)
    quality : float
        Quality metric (0-1)
    details : dict
        Detailed extraction information
    """
    # Estimate expected arrival at receiver 2
    expected_arrival = distance / c_expected
    
    # Extract arrival times
    t1, env1, q1 = extract_arrival_time(sig1, dt, freq_range, 
                                        method='first_peak')
    t2, env2, q2 = extract_arrival_time(sig2, dt, freq_range,
                                        expected_arrival=expected_arrival,
                                        window_margin=2.0,
                                        method='first_peak')
    
    # Time difference
    delay = t2 - t1
    
    if delay <= 0:
        if verbose:
            print(f"    Invalid delay: {delay*1000:.2f} ms")
        return np.nan, 0.0, {}
    
    c_g = distance / delay
    quality = min(q1, q2)
    
    details = {
        't1_ms': t1 * 1000,
        't2_ms': t2 * 1000,
        'delay_ms': delay * 1000,
        'quality': quality,
        'env1': env1,
        'env2': env2
    }
    
    return c_g, quality, details


def run_refined_validation(G_prime=2000, eta=0.5, rho=1000, 
                           n_receivers=3, source_freq=100):
    """Run validation with refined extraction."""
    
    print(f"\n{'='*70}")
    print(f"REFINED GROUP VELOCITY: G'={G_prime} Pa, η={eta} Pa·s")
    print(f"{'='*70}")
    
    # Simulation
    nx, ny = 300, 300
    dx = 0.0005
    pml_width = 20
    
    sim = ShearWave2D(nx=nx, ny=ny, dx=dx, 
                      rho=rho, G_prime=G_prime, eta=eta,
                      pml_width=pml_width)
    
    c_s = np.sqrt(G_prime / rho)
    
    print(f"\nExpected: c_s = {c_s:.2f} m/s (elastic limit)")
    
    # Source and receivers
    source_x, source_y = nx // 2, ny // 2
    distances_m = np.array([0.005, 0.010, 0.015, 0.020, 0.025])[:n_receivers]
    
    receiver_positions = []
    for i, d in enumerate(distances_m):
        rx = int(source_x + d/dx)
        ry = source_y
        receiver_positions.append((rx, ry))
    
    print(f"Receivers: {[f'{d*1000:.0f}mm' for d in distances_m]}")
    
    # Run simulation
    n_steps = 4000
    source_duration = 5
    dt = sim.dt
    
    time_signals = [[] for _ in range(n_receivers)]
    
    print(f"Running {n_steps} steps...")
    for n in range(n_steps):
        t = n * dt
        
        if n < int(source_duration / source_freq / dt):
            sim.add_source(t, x_pos=source_x, y_pos=source_y,
                          amplitude=1e-6, f0=source_freq, source_type='tone_burst')
        
        sim.step()
        
        for i, (rx, ry) in enumerate(receiver_positions):
            time_signals[i].append(sim.u[rx, ry])
        
        if n % 1000 == 0:
            print(f"  {100*n/n_steps:.0f}%")
    
    time_signals = [np.array(sig) for sig in time_signals]
    t = np.arange(len(time_signals[0])) * dt
    
    # Refined extraction
    print(f"\n{'='*70}")
    print("REFINED EXTRACTION RESULTS")
    print(f"{'='*70}")
    
    all_results = []
    
    for i in range(n_receivers - 1):
        for j in range(i + 1, n_receivers):
            sig1 = time_signals[i]
            sig2 = time_signals[j]
            distance = distances_m[j] - distances_m[i]
            
            print(f"\nPair R{i+1}-R{j+1} ({distances_m[i]*1000:.0f}-{distances_m[j]*1000:.0f} mm):")
            
            # Single frequency band
            c_g, quality, details = extract_group_velocity_refined(
                sig1, sig2, dt, distance, 
                c_expected=c_s,
                freq_range=(50, 150),
                verbose=True
            )
            
            if not np.isnan(c_g):
                error = 100 * abs(c_g - c_s) / c_s
                print(f"  50-150 Hz:  c_g = {c_g:.2f} m/s, quality = {quality:.2f}, error = {error:.1f}%")
            else:
                print(f"  50-150 Hz:  Failed (invalid delay)")
            
            # Try narrower band
            c_g_narrow, quality_narrow, details_narrow = extract_group_velocity_refined(
                sig1, sig2, dt, distance,
                c_expected=c_s,
                freq_range=(80, 120),
                verbose=False
            )
            
            if not np.isnan(c_g_narrow):
                error_narrow = 100 * abs(c_g_narrow - c_s) / c_s
                print(f"  80-120 Hz:  c_g = {c_g_narrow:.2f} m/s, quality = {quality_narrow:.2f}, error = {error_narrow:.1f}%")
            
            all_results.append({
                'pair': f'R{i+1}-R{j+1}',
                'distance': distance,
                'c_g': c_g if not np.isnan(c_g) else c_g_narrow,
                'quality': quality,
                'sig1': sig1,
                'sig2': sig2,
                't': t,
                'details': details if not np.isnan(c_g) else details_narrow
            })
    
    # Summary statistics
    valid_results = [r for r in all_results if not np.isnan(r['c_g'])]
    if valid_results:
        c_g_values = [r['c_g'] for r in valid_results]
        c_g_mean = np.mean(c_g_values)
        c_g_std = np.std(c_g_values)
        
        print(f"\n{'='*70}")
        print("SUMMARY")
        print(f"{'='*70}")
        print(f"Mean c_g: {c_g_mean:.2f} ± {c_g_std:.2f} m/s")
        print(f"Theory:   {c_s:.2f} m/s")
        print(f"Mean error: {100*abs(c_g_mean - c_s)/c_s:.1f}%")
    
    return {
        'G_prime': G_prime,
        'eta': eta,
        'c_s': c_s,
        'distances': distances_m,
        'time_signals': time_signals,
        't': t,
        'results': all_results
    }


def plot_refined_results(data, save_path='refined_group_velocity.png'):
    """Plot refined extraction results."""
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    G_prime = data['G_prime']
    eta = data['eta']
    c_s = data['c_s']
    
    fig.suptitle(f'Refined Group Velocity: G\'={G_prime} Pa, η={eta} Pa·s\n'
                 f'Expected: c_s = {c_s:.2f} m/s',
                 fontsize=10)
    
    time_signals = data['time_signals']
    t = data['t'] * 1000  # ms
    results = data['results']
    
    colors = ['blue', 'red', 'green', 'purple', 'orange']
    
    # Plot 1: Raw signals
    ax1 = axes[0, 0]
    for i, sig in enumerate(time_signals):
        ax1.plot(t, sig * 1e6, color=colors[i], alpha=0.5, linewidth=0.5)
    ax1.set_xlabel('Time (ms)')
    ax1.set_ylabel('Displacement (μm)')
    ax1.set_title('Raw Signals')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Envelopes with arrival markers
    ax2 = axes[0, 1]
    for i, sig in enumerate(time_signals):
        env = np.abs(hilbert(sig))
        ax2.plot(t, env * 1e6, color=colors[i], 
                label=f'R{i+1}', linewidth=2, alpha=0.7)
    
    # Mark arrival times
    for r in results:
        if 'details' in r and r['details']:
            d = r['details']
            # Parse pair string like 'R1-R2'
            pair = r['pair']
            parts = pair.split('-')
            idx1 = int(parts[0][1]) - 1  # Extract number from 'R1'
            idx2 = int(parts[1][1]) - 1  # Extract number from 'R2'
            ax2.axvline(d['t1_ms'], color=colors[idx1], linestyle='--', alpha=0.5)
            ax2.axvline(d['t2_ms'], color=colors[idx2], linestyle='--', alpha=0.5)
    
    ax2.set_xlabel('Time (ms)')
    ax2.set_ylabel('Envelope (μm)')
    ax2.set_title('Envelopes with Arrival Times')
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Group velocity results
    ax3 = axes[1, 0]
    ax3.axhline(c_s, color='black', linestyle='--', linewidth=2,
               label=f'Theory: {c_s:.2f} m/s')
    
    for r in results:
        if not np.isnan(r['c_g']):
            d = r['distance'] * 1000
            q = r['quality']
            ax3.scatter(d, r['c_g'], s=100 + 200*q, alpha=0.6,
                       label=f"{r['pair']} (q={q:.2f})")
    
    ax3.set_xlabel('Separation distance (mm)')
    ax3.set_ylabel('Group velocity (m/s)')
    ax3.set_title('Extracted Group Velocity (size = quality)')
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Error distribution
    ax4 = axes[1, 1]
    
    errors = []
    labels = []
    for r in results:
        if not np.isnan(r['c_g']):
            err = 100 * (r['c_g'] - c_s) / c_s
            errors.append(err)
            labels.append(r['pair'])
    
    if errors:
        x_pos = np.arange(len(errors))
        bars = ax4.bar(x_pos, errors, color=colors[:len(errors)], alpha=0.6)
        ax4.axhline(0, color='black', linestyle='-', linewidth=1)
        ax4.set_xticks(x_pos)
        ax4.set_xticklabels(labels, rotation=45)
        ax4.set_ylabel('Error (%)')
        ax4.set_title('Group Velocity Error by Pair')
        ax4.grid(True, alpha=0.3, axis='y')
        
        # Add mean line
        mean_err = np.mean(errors)
        ax4.axhline(mean_err, color='red', linestyle='--', 
                   label=f'Mean: {mean_err:.1f}%')
        ax4.legend()
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"\nSaved: {save_path}")
    
    return fig


def main():
    """Run refined validation suite."""
    
    print("REFINED GROUP VELOCITY EXTRACTION")
    print("="*70)
    
    test_cases = [
        (2000, 0.3, "Low viscosity"),
        (2000, 0.5, "Medium viscosity"),
        (5000, 0.5, "Stiffer tissue"),
    ]
    
    for G_prime, eta, desc in test_cases:
        print(f"\n\n{'='*70}")
        print(f"TEST: {desc}")
        print(f"{'='*70}")
        
        data = run_refined_validation(
            G_prime=G_prime, eta=eta, rho=1000,
            n_receivers=3, source_freq=100
        )
        
        plot_refined_results(data,
            save_path=f'refined_G{G_prime}_eta{eta}.png')
    
    print("\n" + "="*70)
    print("REFINED VALIDATION COMPLETE")


if __name__ == '__main__':
    main()
