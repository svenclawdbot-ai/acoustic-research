#!/usr/bin/env python3
"""
Group Velocity Extraction with Wavelet Denoising
=================================================

Enhanced validation comparing raw vs wavelet-denoised signals.
Uses tuned threshold factor (2.0x) for conservative denoising.

Integration of:
- validate_group_velocity_fixed.py (baseline)
- wavelet_denoising.py (pre-processing)

Author: Research Project
Date: March 14, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert
import sys
import os

# Add research path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'research', 'week2'))

# Import our modules
from wavelet_denoising import WaveletDenoiser

try:
    from shear_wave_2d_simple import ShearWave2D
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


def extract_group_velocity(sig1, sig2, dt, distance, denoise=False,
                           wavelet='sym6', threshold_factor=2.0):
    """
    Group velocity extraction with optional wavelet denoising.
    
    Parameters:
    -----------
    sig1, sig2 : array_like
        Time signals from two receivers
    dt : float
        Time step (seconds)
    distance : float
        Distance between receivers (meters)
    denoise : bool
        Apply wavelet denoising before extraction
    wavelet : str
        Wavelet family (default: 'sym6')
    threshold_factor : float
        Threshold multiplier (default: 2.0 = conservative)
        
    Returns:
    --------
    dict with extraction results and metadata
    """
    sig1_proc = sig1.copy()
    sig2_proc = sig2.copy()
    
    # Optional wavelet denoising
    if denoise:
        denoiser = WaveletDenoiser(
            wavelet=wavelet,
            level=5,
            threshold_factor=threshold_factor,
            mode='soft'
        )
        sig1_proc = denoiser.denoise(sig1_proc)
        sig2_proc = denoiser.denoise(sig2_proc)
    
    # Envelope extraction
    env1 = np.abs(hilbert(sig1_proc))
    env2 = np.abs(hilbert(sig2_proc))
    
    # Search window: 45-80 ms (wave arrives 50-60 ms typically)
    t = np.arange(len(env1)) * dt * 1000  # ms
    search_mask = (t >= 45) & (t <= 80)
    
    if not np.any(search_mask):
        return {
            'c_g': np.nan, 't1': np.nan, 't2': np.nan,
            'delay_ms': np.nan, 'env1': env1, 'env2': env2,
            'status': 'No search window', 'denoised': denoise
        }
    
    search_indices = np.where(search_mask)[0]
    
    peak1_rel_idx = np.argmax(env1[search_mask])
    peak2_rel_idx = np.argmax(env2[search_mask])
    
    peak1_idx = search_indices[peak1_rel_idx]
    peak2_idx = search_indices[peak2_rel_idx]
    
    t1_ms = peak1_idx * dt * 1000
    t2_ms = peak2_idx * dt * 1000
    delay_ms = t2_ms - t1_ms
    delay_s = delay_ms * 1e-3
    
    if delay_s <= 0:
        return {
            'c_g': np.nan, 't1': t1_ms, 't2': t2_ms,
            'delay_ms': delay_ms, 'env1': env1, 'env2': env2,
            'status': f'Invalid delay {delay_ms:.2f} ms',
            'denoised': denoise
        }
    
    c_g = distance / delay_s
    
    return {
        'c_g': c_g,
        't1': t1_ms,
        't2': t2_ms,
        'delay_ms': delay_ms,
        'env1': env1,
        'env2': env2,
        'status': 'OK',
        'denoised': denoise
    }


def run_comparison_validation(G_prime=2000, eta=0.5, rho=1000,
                               n_receivers=3, source_freq=100,
                               noise_level=0.0, impulse_noise=None):
    """
    Run validation comparing raw vs denoised extraction.
    
    Can add synthetic noise to test robustness.
    """
    print(f"\n{'='*70}")
    print(f"WAVELET-DENOISED GROUP VELOCITY VALIDATION")
    print(f"{'='*70}")
    print(f"Parameters: G'={G_prime} Pa, η={eta} Pa·s, ρ={rho} kg/m³")
    print(f"Noise level: {noise_level*100:.0f}%")
    if impulse_noise:
        print(f"Impulse noise: {impulse_noise['prob']*100:.1f}% @ amp={impulse_noise['amp']}")
    print(f"{'='*70}")
    
    # Setup simulation
    nx, ny = 300, 300
    dx = 0.0005
    pml_width = 20
    
    sim = ShearWave2D(nx=nx, ny=ny, dx=dx,
                      rho=rho, G_prime=G_prime, eta=eta,
                      pml_width=pml_width)
    
    c_s = np.sqrt(G_prime / rho)
    print(f"\nTheory: c_s = {c_s:.2f} m/s")
    
    # Receiver positions (5mm, 10mm, 15mm)
    source_x, source_y = nx // 2, ny // 2
    distances_m = np.array([0.005, 0.010, 0.015])[:n_receivers]
    
    receiver_positions = []
    for i, d in enumerate(distances_m):
        rx = int(source_x + d/dx)
        ry = source_y
        receiver_positions.append((rx, ry))
        print(f"  R{i+1}: {d*1000:.0f} mm from source")
    
    # Run simulation
    n_steps = 4000
    source_duration = 5
    dt = sim.dt
    
    print(f"\nRunning simulation: {n_steps} steps (dt={dt*1e6:.1f} μs)...")
    
    time_signals_clean = [[] for _ in range(n_receivers)]
    
    for n in range(n_steps):
        t = n * dt
        
        if n < int(source_duration / source_freq / dt):
            sim.add_source(t, x_pos=source_x, y_pos=source_y,
                          amplitude=1e-6, f0=source_freq, source_type='tone_burst')
        
        sim.step()
        
        for i, (rx, ry) in enumerate(receiver_positions):
            time_signals_clean[i].append(sim.u[rx, ry])
    
    time_signals_clean = [np.array(sig) for sig in time_signals_clean]
    
    # Add synthetic noise if requested
    time_signals_noisy = []
    for sig in time_signals_clean:
        sig_noisy = sig.copy()
        
        # Gaussian noise
        if noise_level > 0:
            sig_noisy += noise_level * np.std(sig) * np.random.randn(len(sig))
        
        # Impulse noise
        if impulse_noise:
            n_impulses = int(len(sig) * impulse_noise['prob'])
            idx = np.random.choice(len(sig), n_impulses, replace=False)
            sig_noisy[idx] += impulse_noise['amp'] * np.std(sig) * np.random.randn(n_impulses)
        
        time_signals_noisy.append(sig_noisy)
    
    signals = time_signals_noisy if (noise_level > 0 or impulse_noise) else time_signals_clean
    
    # Extract group velocities: RAW vs DENOISED
    print(f"\n{'='*70}")
    print("EXTRACTION RESULTS")
    print(f"{'='*70}")
    
    raw_results = []
    denoised_results = []
    
    for i in range(n_receivers - 1):
        for j in range(i + 1, n_receivers):
            distance = distances_m[j] - distances_m[i]
            pair_name = f'R{i+1}-R{j+1}'
            
            print(f"\n  {pair_name} ({distances_m[i]*1000:.0f}-{distances_m[j]*1000:.0f} mm, {distance*1000:.0f} mm baseline):")
            
            # RAW extraction
            raw = extract_group_velocity(
                signals[i], signals[j], dt, distance,
                denoise=False
            )
            raw_results.append(raw)
            
            print(f"    RAW:      c_g = {raw['c_g']:.2f} m/s" if not np.isnan(raw['c_g']) else "    RAW:      FAILED")
            
            # DENOISED extraction
            den = extract_group_velocity(
                signals[i], signals[j], dt, distance,
                denoise=True, wavelet='sym6', threshold_factor=2.0
            )
            denoised_results.append(den)
            
            print(f"    DENOISED: c_g = {den['c_g']:.2f} m/s" if not np.isnan(den['c_g']) else "    DENOISED: FAILED")
            
            if not np.isnan(raw['c_g']) and not np.isnan(den['c_g']):
                raw_err = 100 * abs(raw['c_g'] - c_s) / c_s
                den_err = 100 * abs(den['c_g'] - c_s) / c_s
                improvement = raw_err - den_err
                print(f"    Errors:   RAW {raw_err:.1f}% | DENOISED {den_err:.1f}% | Δ {improvement:+.1f}%")
    
    # Summary statistics
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    
    raw_cg = [r['c_g'] for r in raw_results if not np.isnan(r['c_g'])]
    den_cg = [r['c_g'] for r in denoised_results if not np.isnan(r['c_g'])]
    
    print(f"Theory:        {c_s:.2f} m/s")
    
    if raw_cg:
        raw_mean = np.mean(raw_cg)
        raw_std = np.std(raw_cg)
        raw_err = 100 * abs(raw_mean - c_s) / c_s
        print(f"RAW:           {raw_mean:.2f} ± {raw_std:.2f} m/s (error: {raw_err:.1f}%)")
    else:
        print("RAW:           No valid extractions")
    
    if den_cg:
        den_mean = np.mean(den_cg)
        den_std = np.std(den_cg)
        den_err = 100 * abs(den_mean - c_s) / c_s
        print(f"DENOISED:      {den_mean:.2f} ± {den_std:.2f} m/s (error: {den_err:.1f}%)")
    else:
        print("DENOISED:      No valid extractions")
    
    if raw_cg and den_cg:
        improvement = (100 * abs(np.mean(raw_cg) - c_s) / c_s) - den_err
        print(f"\nImprovement:   {improvement:+.1f}% error reduction")
    
    return {
        'G_prime': G_prime,
        'eta': eta,
        'c_s': c_s,
        'distances': distances_m,
        'signals_clean': time_signals_clean,
        'signals_noisy': signals if (noise_level > 0 or impulse_noise) else None,
        'dt': dt,
        'raw_results': raw_results,
        'denoised_results': denoised_results
    }


def plot_comparison_results(data, save_path='group_velocity_comparison.png'):
    """Plot comparison of raw vs denoised extraction."""
    
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.3)
    
    G_prime = data['G_prime']
    eta = data['eta']
    c_s = data['c_s']
    dt = data['dt']
    t_ms = np.arange(len(data['signals_clean'][0])) * dt * 1000
    
    n_pairs = len(data['raw_results'])
    
    # Row 0: Signal comparison for first receiver
    ax_signal = fig.add_subplot(gs[0, :])
    
    if data['signals_noisy'] is not None:
        ax_signal.plot(t_ms, data['signals_noisy'][0], 'b-', alpha=0.4, 
                       linewidth=0.5, label='Noisy input')
    
    ax_signal.plot(t_ms, data['signals_clean'][0], 'g-', alpha=0.7,
                   linewidth=0.8, label='Clean (simulated)')
    
    # Show denoised version
    denoiser = WaveletDenoiser(wavelet='sym6', level=5, 
                               threshold_factor=2.0, mode='soft')
    sig_denoised = denoiser.denoise(data['signals_noisy'][0].copy() 
                                     if data['signals_noisy'] is not None 
                                     else data['signals_clean'][0])
    ax_signal.plot(t_ms, sig_denoised, 'r-', alpha=0.8,
                   linewidth=0.8, label='Wavelet denoised (2.0x)')
    
    ax_signal.set_xlim([30, 80])
    ax_signal.set_xlabel('Time (ms)')
    ax_signal.set_ylabel('Displacement')
    ax_signal.set_title('R1 Signal: Input vs Denoised', fontweight='bold')
    ax_signal.legend(loc='upper right')
    ax_signal.grid(True, alpha=0.3)
    
    # Row 1: Envelope comparisons for each pair
    for i in range(min(n_pairs, 3)):
        ax = fig.add_subplot(gs[1, i])
        
        raw = data['raw_results'][i]
        den = data['denoised_results'][i]
        
        # Plot envelopes
        ax.plot(t_ms, raw['env1'], 'b-', alpha=0.5, linewidth=1, label='R env (raw)')
        ax.plot(t_ms, raw['env2'], 'b--', alpha=0.5, linewidth=1, label='R+1 env (raw)')
        ax.plot(t_ms, den['env1'], 'r-', alpha=0.8, linewidth=1, label='R env (denoised)')
        ax.plot(t_ms, den['env2'], 'r--', alpha=0.8, linewidth=1, label='R+1 env (denoised)')
        
        # Mark peaks
        if not np.isnan(raw['t1']):
            ax.axvline(raw['t1'], color='b', linestyle=':', alpha=0.5)
            ax.axvline(raw['t2'], color='b', linestyle=':', alpha=0.5)
        if not np.isnan(den['t1']):
            ax.axvline(den['t1'], color='r', linestyle=':', alpha=0.7)
            ax.axvline(den['t2'], color='r', linestyle=':', alpha=0.7)
        
        ax.set_xlim([45, 70])
        ax.set_xlabel('Time (ms)')
        ax.set_ylabel('Envelope')
        ax.set_title(f'Pair {i+1}: Envelopes', fontweight='bold')
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)
    
    # Row 2: Bar chart comparison
    ax_bar = fig.add_subplot(gs[2, :2])
    
    raw_cg = [r['c_g'] for r in data['raw_results']]
    den_cg = [r['c_g'] for r in data['denoised_results']]
    
    x = np.arange(n_pairs)
    width = 0.35
    
    bars1 = ax_bar.bar(x - width/2, raw_cg, width, label='RAW', color='blue', alpha=0.6)
    bars2 = ax_bar.bar(x + width/2, den_cg, width, label='DENOISED (2.0x)', color='red', alpha=0.6)
    
    # Theory line
    ax_bar.axhline(c_s, color='green', linestyle='--', linewidth=2, label=f'Theory: {c_s:.1f} m/s')
    
    ax_bar.set_xlabel('Receiver Pair')
    ax_bar.set_ylabel('Group Velocity (m/s)')
    ax_bar.set_title('Group Velocity: Raw vs Wavelet-Denoised', fontweight='bold')
    ax_bar.set_xticks(x)
    ax_bar.set_xticklabels([f'Pair {i+1}' for i in range(n_pairs)])
    ax_bar.legend()
    ax_bar.grid(True, alpha=0.3, axis='y')
    
    # Error table
    ax_table = fig.add_subplot(gs[2, 2])
    ax_table.axis('off')
    
    table_data = [['Pair', 'RAW Error %', 'Denoised Error %']]
    for i, (raw, den) in enumerate(zip(data['raw_results'], data['denoised_results'])):
        if not np.isnan(raw['c_g']):
            raw_err = 100 * abs(raw['c_g'] - c_s) / c_s
        else:
            raw_err = float('nan')
        
        if not np.isnan(den['c_g']):
            den_err = 100 * abs(den['c_g'] - c_s) / c_s
        else:
            den_err = float('nan')
        
        table_data.append([f'{i+1}', f'{raw_err:.1f}', f'{den_err:.1f}'])
    
    table = ax_table.table(cellText=table_data[1:], colLabels=table_data[0],
                           loc='center', cellLoc='center',
                           colColours=['#4472C4']*3)
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.5)
    ax_table.set_title('Error Comparison', fontweight='bold', pad=20)
    
    plt.suptitle(f'Wavelet Denoising Validation: G\'={G_prime} Pa, η={eta} Pa·s',
                 fontsize=14, fontweight='bold')
    
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"\nSaved: {save_path}")
    
    return fig


if __name__ == "__main__":
    import pywt
    
    print("="*70)
    print("GROUP VELOCITY WITH WAVELET DENOISING")
    print("="*70)
    
    # Test 1: Clean data (baseline)
    print("\n" + "="*70)
    print("TEST 1: Clean Signal (No Noise)")
    print("="*70)
    
    data_clean = run_comparison_validation(
        G_prime=2000, eta=0.5,
        noise_level=0.0
    )
    plot_comparison_results(data_clean, 'validation_clean.png')
    
    # Test 2: With Gaussian noise
    print("\n" + "="*70)
    print("TEST 2: 15% Gaussian Noise")
    print("="*70)
    
    np.random.seed(42)
    data_noisy = run_comparison_validation(
        G_prime=2000, eta=0.5,
        noise_level=0.15
    )
    plot_comparison_results(data_noisy, 'validation_noisy.png')
    
    # Test 3: With mixed noise (impulse + Gaussian)
    print("\n" + "="*70)
    print("TEST 3: Mixed Noise (10% Gaussian + Impulse)")
    print("="*70)
    
    np.random.seed(42)
    data_mixed = run_comparison_validation(
        G_prime=2000, eta=0.5,
        noise_level=0.10,
        impulse_noise={'prob': 0.01, 'amp': 1.0}
    )
    plot_comparison_results(data_mixed, 'validation_mixed.png')
    
    print("\n" + "="*70)
    print("VALIDATION COMPLETE")
    print("="*70)
    print("Generated files:")
    print("  - validation_clean.png")
    print("  - validation_noisy.png")
    print("  - validation_mixed.png")
