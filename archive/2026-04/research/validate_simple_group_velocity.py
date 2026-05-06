#!/usr/bin/env python3
"""
Simplified Robust Group Velocity Extraction
============================================

Direct envelope peak tracking with simple constraints.
The key insight: Look for the MAIN envelope peak (not first transient).

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


def extract_group_velocity_simple(sig1, sig2, dt, distance, 
                                  freq_range=(50, 150),
                                  search_start_ms=30.0):
    """
    Simple group velocity extraction.
    
    1. Bandpass filter both signals
    2. Compute envelopes
    3. Find peak in search window (after source transient)
    4. Calculate velocity from time difference
    """
    # Bandpass filter
    nyquist = 1.0 / (2 * dt)
    low = freq_range[0] / nyquist
    high = freq_range[1] / nyquist
    b, a = butter(4, [low, high], btype='band')
    
    s1_filt = filtfilt(b, a, sig1)
    s2_filt = filtfilt(b, a, sig2)
    
    # Envelopes
    env1 = np.abs(hilbert(s1_filt))
    env2 = np.abs(hilbert(s2_filt))
    
    # Search window (after source transient, before end effects)
    # Wave arrives ~50-70 ms, search 45-80 ms
    start_idx = int(45 * 1e-3 / dt)
    end_idx = int(80 * 1e-3 / dt)
    start_idx = max(0, min(start_idx, len(env1) - 10))
    end_idx = max(start_idx + 50, min(end_idx, len(env1) - 20))  # Avoid PML at end
    
    # Find peaks in search window
    peak1_idx = start_idx + np.argmax(env1[start_idx:end_idx])
    peak2_idx = start_idx + np.argmax(env2[start_idx:end_idx])
    
    t1 = peak1_idx * dt * 1000  # Convert to ms immediately
    t2 = peak2_idx * dt * 1000
    delay = (t2 - t1) * 1e-3  # Convert back to seconds for velocity calc
    
    if delay <= 0:
        return np.nan, t1, t2, env1, env2
    
    c_g = distance / delay
    
    return c_g, t1, t2, env1, env2


def validate_simple(G_prime=2000, eta=0.5, rho=1000, 
                    n_receivers=3, source_freq=100,
                    search_start_ms=30.0):
    """Run simplified validation."""
    
    print(f"\n{'='*60}")
    print(f"SIMPLE GROUP VELOCITY: G'={G_prime} Pa, η={eta} Pa·s")
    print(f"Search window: {search_start_ms} ms onwards")
    print(f"{'='*60}")
    
    # Simulation
    nx, ny = 300, 300
    dx = 0.0005
    pml_width = 20
    
    sim = ShearWave2D(nx=nx, ny=ny, dx=dx, 
                      rho=rho, G_prime=G_prime, eta=eta,
                      pml_width=pml_width)
    
    c_s = np.sqrt(G_prime / rho)
    print(f"\nTheory: c_s = {c_s:.2f} m/s")
    
    # Source and receivers
    source_x, source_y = nx // 2, ny // 2
    distances_m = np.array([0.005, 0.010, 0.015])[:n_receivers]
    
    receiver_positions = []
    for i, d in enumerate(distances_m):
        rx = int(source_x + d/dx)
        ry = source_y
        receiver_positions.append((rx, ry))
        print(f"  R{i+1}: {d*1000:.0f} mm")
    
    # Run simulation
    n_steps = 4000
    source_duration = 5
    dt = sim.dt
    
    time_signals = [[] for _ in range(n_receivers)]
    
    print(f"\nRunning...")
    for n in range(n_steps):
        t = n * dt
        
        if n < int(source_duration / source_freq / dt):
            sim.add_source(t, x_pos=source_x, y_pos=source_y,
                          amplitude=1e-6, f0=source_freq, source_type='tone_burst')
        
        sim.step()
        
        for i, (rx, ry) in enumerate(receiver_positions):
            time_signals[i].append(sim.u[rx, ry])
    
    time_signals = [np.array(sig) for sig in time_signals]
    t = np.arange(len(time_signals[0])) * dt * 1000  # ms
    
    # Extract group velocity
    print(f"\nEXTRACTION RESULTS:")
    
    results = []
    for i in range(n_receivers - 1):
        for j in range(i + 1, n_receivers):
            sig1 = time_signals[i]
            sig2 = time_signals[j]
            distance = distances_m[j] - distances_m[i]
            
            c_g, t1, t2, env1, env2 = extract_group_velocity_simple(
                sig1, sig2, dt, distance,
                freq_range=(50, 150),
                search_start_ms=search_start_ms
            )
            
            results.append({
                'pair': f'R{i+1}-R{j+1}',
                'distance_mm': distance * 1000,
                'c_g': c_g,
                't1': t1,
                't2': t2,
                'env1': env1,
                'env2': env2
            })
            
            if not np.isnan(c_g):
                error = 100 * abs(c_g - c_s) / c_s
                print(f"\n  {results[-1]['pair']} ({distances_m[i]*1000:.0f}-{distances_m[j]*1000:.0f} mm):")
                print(f"    Arrivals: t1={t1:.1f} ms, t2={t2:.1f} ms")
                print(f"    Delay: {(t2-t1):.2f} ms")
                print(f"    c_g = {c_g:.2f} m/s (error: {error:.1f}%)")
            else:
                print(f"\n  {results[-1]['pair']}: Failed")
                print(f"    (t1={t1:.1f}ms, t2={t2:.1f}ms, delay={(t2-t1):.2f}ms)")
    
    # Summary
    valid_cg = [r['c_g'] for r in results if not np.isnan(r['c_g'])]
    if valid_cg:
        print(f"\n{'='*60}")
        print(f"SUMMARY: {np.mean(valid_cg):.2f} ± {np.std(valid_cg):.2f} m/s")
        print(f"THEORY:  {c_s:.2f} m/s")
        print(f"MEAN ERROR: {100*abs(np.mean(valid_cg) - c_s)/c_s:.1f}%")
    
    return {
        'G_prime': G_prime,
        'eta': eta,
        'c_s': c_s,
        'distances': distances_m,
        'time_signals': time_signals,
        't': t,
        'results': results
    }


def plot_simple(data, save_path='simple_group_velocity.png'):
    """Plot simple extraction results."""
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    G_prime = data['G_prime']
    eta = data['eta']
    c_s = data['c_s']
    
    fig.suptitle(f'Simple Group Velocity: G\'={G_prime} Pa, η={eta} Pa·s',
                 fontsize=11)
    
    time_signals = data['time_signals']
    t = data['t']
    results = data['results']
    
    colors = ['blue', 'red', 'green']
    
    # Plot 1: Raw signals
    ax1 = axes[0, 0]
    for i, sig in enumerate(time_signals):
        ax1.plot(t, sig * 1e6, color=colors[i], alpha=0.5, 
                label=f'R{i+1}', linewidth=0.5)
    ax1.set_xlabel('Time (ms)')
    ax1.set_ylabel('Displacement (μm)')
    ax1.set_title('Raw Signals')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Envelopes with arrival markers
    ax2 = axes[0, 1]
    for i, sig in enumerate(time_signals):
        env = np.abs(hilbert(sig))
        ax2.plot(t, env * 1e6, color=colors[i], 
                label=f'R{i+1}', linewidth=2)
    
    # Mark arrivals
    for r in results:
        if not np.isnan(r['c_g']):
            parts = r['pair'].split('-')
            i1 = int(parts[0][1]) - 1
            i2 = int(parts[1][1]) - 1
            ax2.axvline(r['t1'], color=colors[i1], linestyle='--', alpha=0.5)
            ax2.axvline(r['t2'], color=colors[i2], linestyle='--', alpha=0.5)
            ax2.scatter([r['t1'], r['t2']], 
                       [np.max(r['env1'])*1e6, np.max(r['env2'])*1e6],
                       color=[colors[i1], colors[i2]], s=50, zorder=5)
    
    ax2.set_xlabel('Time (ms)')
    ax2.set_ylabel('Envelope (μm)')
    ax2.set_title('Envelopes with Detected Arrivals')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Group velocity
    ax3 = axes[1, 0]
    ax3.axhline(c_s, color='black', linestyle='--', linewidth=2,
               label=f'Theory: {c_s:.2f} m/s')
    
    for r in results:
        if not np.isnan(r['c_g']):
            ax3.scatter(r['distance_mm'], r['c_g'], s=150, alpha=0.7,
                       label=r['pair'])
    
    ax3.set_xlabel('Separation (mm)')
    ax3.set_ylabel('Group velocity (m/s)')
    ax3.set_title('Extracted Group Velocity')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Error
    ax4 = axes[1, 1]
    errors = []
    labels = []
    for r in results:
        if not np.isnan(r['c_g']):
            err = 100 * (r['c_g'] - c_s) / c_s
            errors.append(err)
            labels.append(r['pair'])
    
    if errors:
        x = np.arange(len(errors))
        bars = ax4.bar(x, errors, color=colors[:len(errors)], alpha=0.6)
        ax4.axhline(0, color='black', linewidth=1)
        ax4.axhline(np.mean(errors), color='red', linestyle='--',
                   label=f'Mean: {np.mean(errors):.1f}%')
        ax4.set_xticks(x)
        ax4.set_xticklabels(labels)
        ax4.set_ylabel('Error (%)')
        ax4.set_title('Velocity Error')
        ax4.legend()
        ax4.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"\nSaved: {save_path}")


def main():
    """Run simple validation."""
    
    print("SIMPLE GROUP VELOCITY EXTRACTION")
    print("="*60)
    
    # Test different search start times
    for start_ms in [30, 40, 50]:
        print(f"\n\n{'='*60}")
        print(f"SEARCH START: {start_ms} ms")
        print(f"{'='*60}")
        
        data = validate_simple(
            G_prime=2000, eta=0.3, rho=1000,
            n_receivers=3, source_freq=100,
            search_start_ms=start_ms
        )
        
        plot_simple(data, save_path=f'simple_start{start_ms}.png')


if __name__ == '__main__':
    main()
