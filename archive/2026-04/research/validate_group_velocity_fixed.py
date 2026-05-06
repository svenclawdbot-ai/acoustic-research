#!/usr/bin/env python3
"""
Fixed Group Velocity Extraction
================================

Corrected envelope peak tracking for sparse shear wave sampling.
Key fixes:
1. Proper absolute index tracking
2. Distinct peak finding for each receiver
3. Validated time window (45-80 ms)

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


def extract_group_velocity_fixed(sig1, sig2, dt, distance, 
                                 freq_range=None):
    """
    Fixed group velocity extraction with proper peak finding.
    
    Uses raw envelope (no filtering) to avoid signal attenuation.
    """
    # Use raw signal envelope (filtering can attenuate too much)
    env1 = np.abs(hilbert(sig1))
    env2 = np.abs(hilbert(sig2))
    
    # Search window: 45-80 ms (wave arrives 50-60 ms)
    t = np.arange(len(env1)) * dt * 1000  # Time in ms
    search_mask = (t >= 45) & (t <= 80)
    
    if not np.any(search_mask):
        return np.nan, np.nan, np.nan, env1, env2, "No search window"
    
    # Find peaks in search window (absolute indices)
    search_indices = np.where(search_mask)[0]
    
    peak1_rel_idx = np.argmax(env1[search_mask])
    peak2_rel_idx = np.argmax(env2[search_mask])
    
    peak1_idx = search_indices[peak1_rel_idx]
    peak2_idx = search_indices[peak2_rel_idx]
    
    # Arrival times in ms
    t1_ms = peak1_idx * dt * 1000
    t2_ms = peak2_idx * dt * 1000
    
    # Delay in seconds
    delay_s = (t2_ms - t1_ms) * 1e-3
    
    if delay_s <= 0:
        return np.nan, t1_ms, t2_ms, env1, env2, f"Invalid delay {delay_s*1000:.2f} ms"
    
    c_g = distance / delay_s
    
    return c_g, t1_ms, t2_ms, env1, env2, "OK"


def run_fixed_validation(G_prime=2000, eta=0.5, rho=1000, 
                         n_receivers=3, source_freq=100):
    """Run validation with fixed extraction."""
    
    print(f"\n{'='*60}")
    print(f"FIXED GROUP VELOCITY: G'={G_prime} Pa, η={eta} Pa·s")
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
    print(f"Expected delay for 5mm at {c_s:.2f} m/s: {0.005/c_s*1000:.1f} ms")
    
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
    
    print(f"\nRunning {n_steps} steps (dt={dt*1e6:.1f} μs)...")
    for n in range(n_steps):
        t = n * dt
        
        if n < int(source_duration / source_freq / dt):
            sim.add_source(t, x_pos=source_x, y_pos=source_y,
                          amplitude=1e-6, f0=source_freq, source_type='tone_burst')
        
        sim.step()
        
        for i, (rx, ry) in enumerate(receiver_positions):
            time_signals[i].append(sim.u[rx, ry])
    
    time_signals = [np.array(sig) for sig in time_signals]
    t_ms = np.arange(len(time_signals[0])) * dt * 1000
    
    # Extract group velocity
    print(f"\nEXTRACTION RESULTS:")
    print(f"{'='*60}")
    
    results = []
    valid_cg = []
    
    for i in range(n_receivers - 1):
        for j in range(i + 1, n_receivers):
            sig1 = time_signals[i]
            sig2 = time_signals[j]
            distance = distances_m[j] - distances_m[i]
            
            c_g, t1, t2, env1, env2, status = extract_group_velocity_fixed(
                sig1, sig2, dt, distance, freq_range=(50, 150)
            )
            
            results.append({
                'pair': f'R{i+1}-R{j+1}',
                'distance_mm': distance * 1000,
                'c_g': c_g,
                't1': t1,
                't2': t2,
                'status': status,
                'env1': env1,
                'env2': env2
            })
            
            print(f"\n  {results[-1]['pair']} ({distances_m[i]*1000:.0f}-{distances_m[j]*1000:.0f} mm):")
            print(f"    Status: {status}")
            print(f"    Arrivals: t1={t1:.1f} ms, t2={t2:.1f} ms")
            print(f"    Delay: {(t2-t1):.2f} ms")
            
            if not np.isnan(c_g):
                error = 100 * abs(c_g - c_s) / c_s
                valid_cg.append(c_g)
                print(f"    c_g = {c_g:.2f} m/s (error: {error:.1f}%)")
            else:
                print(f"    FAILED")
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    if valid_cg:
        c_g_mean = np.mean(valid_cg)
        c_g_std = np.std(valid_cg)
        print(f"Mean c_g: {c_g_mean:.2f} ± {c_g_std:.2f} m/s")
        print(f"Theory:   {c_s:.2f} m/s")
        print(f"Mean error: {100*abs(c_g_mean - c_s)/c_s:.1f}%")
        print(f"Success rate: {len(valid_cg)}/{len(results)} pairs")
    else:
        print("No valid extractions")
    
    return {
        'G_prime': G_prime,
        'eta': eta,
        'c_s': c_s,
        'distances': distances_m,
        'time_signals': time_signals,
        't_ms': t_ms,
        'results': results,
        'valid_cg': valid_cg
    }


def plot_fixed_results(data, save_path='fixed_group_velocity.png'):
    """Plot fixed extraction results."""
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    G_prime = data['G_prime']
    eta = data['eta']
    c_s = data['c_s']
    
    fig.suptitle(f'Fixed Group Velocity: G\'={G_prime} Pa, η={eta} Pa·s\n'
                 f'Theory: c_s = {c_s:.2f} m/s',
                 fontsize=11)
    
    time_signals = data['time_signals']
    t_ms = data['t_ms']
    results = data['results']
    
    colors = ['blue', 'red', 'green']
    
    # Plot 1: Raw signals
    ax1 = axes[0, 0]
    for i, sig in enumerate(time_signals):
        ax1.plot(t_ms, sig * 1e6, color=colors[i], alpha=0.5, 
                label=f'R{i+1}', linewidth=0.5)
    ax1.axvspan(45, 80, alpha=0.2, color='gray', label='Search window')
    ax1.set_xlabel('Time (ms)')
    ax1.set_ylabel('Displacement (μm)')
    ax1.set_title('Raw Signals')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Envelopes with arrival markers
    ax2 = axes[0, 1]
    for i, sig in enumerate(time_signals):
        env = np.abs(hilbert(sig))
        ax2.plot(t_ms, env * 1e6, color=colors[i], 
                label=f'R{i+1}', linewidth=2)
    
    # Mark detected arrivals
    for r in results:
        if not np.isnan(r['c_g']):
            parts = r['pair'].split('-')
            i1 = int(parts[0][1]) - 1
            i2 = int(parts[1][1]) - 1
            ax2.axvline(r['t1'], color=colors[i1], linestyle='--', alpha=0.5)
            ax2.axvline(r['t2'], color=colors[i2], linestyle='--', alpha=0.5)
            ax2.scatter([r['t1']], [r['env1'][int(r['t1']/data['t_ms'][1])]*1e6], 
                       color=colors[i1], s=100, marker='o', zorder=5)
            ax2.scatter([r['t2']], [r['env2'][int(r['t2']/data['t_ms'][1])]*1e6],
                       color=colors[i2], s=100, marker='s', zorder=5)
    
    ax2.axvspan(45, 80, alpha=0.2, color='gray')
    ax2.set_xlabel('Time (ms)')
    ax2.set_ylabel('Envelope (μm)')
    ax2.set_title('Envelopes with Detected Arrivals')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Group velocity results
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
    ax3.set_ylim(0, 3)
    
    # Plot 4: Error bar chart
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
        ax4.set_ylim(-50, 50)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Saved: {save_path}")


def main():
    """Run fixed validation."""
    
    print("FIXED GROUP VELOCITY EXTRACTION")
    print("="*60)
    
    test_cases = [
        (2000, 0.3, "Low viscosity"),
        (2000, 0.5, "Medium viscosity"),
        (5000, 0.5, "Stiffer tissue"),
    ]
    
    for G_prime, eta, desc in test_cases:
        print(f"\n\n{'='*60}")
        print(f"TEST: {desc}")
        print(f"{'='*60}")
        
        data = run_fixed_validation(
            G_prime=G_prime, eta=eta, rho=1000,
            n_receivers=3, source_freq=100
        )
        
        plot_fixed_results(data, 
                          save_path=f'fixed_G{G_prime}_eta{eta}.png')
    
    print("\n" + "="*60)
    print("FIXED VALIDATION COMPLETE")


if __name__ == '__main__':
    main()
