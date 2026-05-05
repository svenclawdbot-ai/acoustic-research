#!/usr/bin/env python3
"""
End-to-End Shear Wave Pipeline (Working Version)
=================================================

Simplified but functional integration of:
1. Signal generation (synthetic or hardware)
2. GCC-PHAT dispersion extraction
3. Kelvin-Voigt parameter fitting

Author: Research Project
Date: April 17, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert, butter, filtfilt
from typing import Dict, List, Tuple, Optional
import sys
import os
import warnings

sys.path.insert(0, os.path.dirname(__file__))
from subsample_gcc import gcc_phat
from bayesian_dispersion import kelvin_voigt_velocity, fit_frequentist


def generate_narrowband_signal(t, f_center, arrival_time, burst_width=0.005):
    """Generate a narrowband tone burst with proper phase delay."""
    omega = 2 * np.pi * f_center
    envelope = np.exp(-((t - arrival_time)**2) / (2 * (burst_width/3)**2))
    carrier = np.sin(omega * (t - arrival_time))
    return envelope * carrier


def generate_synthetic_data(distances, frequencies, G_prime, eta, rho,
                            fs=20000, duration=0.12, noise_level=0.1, seed=None):
    """Generate synthetic dispersive signals for multiple receivers."""
    if seed is not None:
        np.random.seed(seed)
    
    dt = 1.0 / fs
    t = np.linspace(0, duration, int(fs * duration))
    
    # Base arrival times (well-separated frequencies)
    base_times = np.linspace(0.025, 0.095, len(frequencies))
    
    signals = []
    for d in distances:
        sig = np.zeros_like(t)
        for f_center, t_base in zip(frequencies, base_times):
            omega = 2 * np.pi * f_center
            G_mag = np.sqrt(G_prime**2 + (omega * eta)**2)
            c_f = np.sqrt(2 / rho) * np.sqrt(G_mag**2 / (G_prime + G_mag))
            
            arrival = t_base + d / c_f
            sig += generate_narrowband_signal(t, f_center, arrival)
        
        sig = sig / (np.max(np.abs(sig)) + 1e-10)
        
        if noise_level > 0:
            noise = noise_level * np.std(sig) * np.random.randn(len(sig))
            sig = sig + noise
        
        signals.append(sig)
    
    return np.array(signals), t


def extract_dispersion_gcc_phat(signals, dt, distances, frequencies):
    """Extract dispersion using GCC-PHAT."""
    results = {'frequencies': [], 'velocities': [], 'uncertainties': []}
    fs = 1.0 / dt
    
    for f_center in frequencies:
        pair_velocities = []
        
        for i in range(len(signals) - 1):
            for j in range(i + 1, len(signals)):
                # Filter
                nyq = fs / 2
                low = max(0.01, (f_center - 12) / nyq)
                high = min(0.99, (f_center + 12) / nyq)
                
                try:
                    b, a = butter(2, [low, high], btype='band')
                    s1_f = filtfilt(b, a, signals[i])
                    s2_f = filtfilt(b, a, signals[j])
                except:
                    continue
                
                # Coarse delay from envelope
                env1 = np.abs(hilbert(s1_f))
                env2 = np.abs(hilbert(s2_f))
                
                # Search window for peaks
                t_ms = np.arange(len(env1)) * dt * 1000
                search = (t_ms > 15) & (t_ms < 110)
                
                if not np.any(search):
                    continue
                
                idx = np.where(search)[0]
                p1 = idx[np.argmax(env1[search])]
                p2 = idx[np.argmax(env2[search])]
                coarse_delay = (p2 - p1) * dt
                
                # Fine delay from GCC-PHAT
                delay_fine, corr = gcc_phat(s1_f, s2_f, fs, 
                                           freq_range=(f_center-10, f_center+10))
                
                # Resolve phase ambiguity
                period = 1.0 / f_center
                n_periods = round((delay_fine - coarse_delay) / period)
                delay = delay_fine - n_periods * period
                
                distance = distances[j] - distances[i]
                
                if delay > 1e-9:
                    velocity = distance / delay
                    if 0.5 <= velocity <= 10:
                        pair_velocities.append(velocity)
        
        if pair_velocities:
            v_array = np.array(pair_velocities)
            if len(v_array) >= 3:
                q1, q3 = np.percentile(v_array, [25, 75])
                iqr = q3 - q1
                mask = (v_array >= q1 - 1.0*iqr) & (v_array <= q3 + 1.0*iqr)
                v_clean = v_array[mask]
                if len(v_clean) >= 2:
                    v_array = v_clean
            
            v_mean = np.median(v_array)
            v_std = np.std(v_array) if len(v_array) > 1 else 0.05 * v_mean
            
            if v_mean <= 2.5:
                results['frequencies'].append(f_center)
                results['velocities'].append(v_mean)
                results['uncertainties'].append(v_std)
    
    return results


def run_pipeline_single_frame(true_G=2000, true_eta=0.5, rho=1000, 
                               noise_level=0.10, make_plots=True):
    """Run complete pipeline on a single synthetic frame."""
    print("="*70)
    print("END-TO-END PIPELINE - SINGLE FRAME")
    print("="*70)
    print(f"True: G' = {true_G} Pa, η = {true_eta} Pa·s, noise = {noise_level*100:.0f}%")
    
    # Setup
    fs = 20000
    distances = np.array([0.005, 0.015, 0.025, 0.035])
    frequencies = [60, 80, 100, 120, 140]
    
    # Generate data
    print("\n1. Generating synthetic data...")
    signals, t = generate_synthetic_data(
        distances, frequencies, true_G, true_eta, rho,
        fs=fs, noise_level=noise_level, seed=42
    )
    print(f"   Generated {signals.shape[0]} channels, {signals.shape[1]} samples")
    
    # Extract dispersion
    print("\n2. Extracting dispersion curve...")
    dt = 1.0 / fs
    dispersion = extract_dispersion_gcc_phat(signals, dt, distances, frequencies)
    print(f"   Extracted {len(dispersion['velocities'])} frequency points")
    
    if len(dispersion['velocities']) == 0:
        print("   ERROR: No dispersion points extracted!")
        return None
    
    for f, v, u in zip(dispersion['frequencies'], 
                       dispersion['velocities'], 
                       dispersion['uncertainties']):
        print(f"   {f:.0f} Hz: c = {v:.2f} ± {u:.2f} m/s")
    
    # Fit parameters
    print("\n3. Fitting Kelvin-Voigt model...")
    fit = fit_frequentist(
        np.array(dispersion['frequencies']),
        np.array(dispersion['velocities']),
        np.array(dispersion['uncertainties']),
        rho
    )
    
    if fit['success']:
        print(f"   G' = {fit['G_prime']:.0f} ± {fit['G_prime_err']:.0f} Pa")
        print(f"   η = {fit['eta']:.3f} ± {fit['eta_err']:.3f} Pa·s")
        print(f"   R² = {fit['r_squared']:.4f}")
        
        G_error = 100 * abs(fit['G_prime'] - true_G) / true_G
        eta_error = 100 * abs(fit['eta'] - true_eta) / true_eta if true_eta > 0 else 0
        print(f"\n   Errors: G' = {G_error:.1f}%, η = {eta_error:.1f}%")
    else:
        print(f"   Fit failed: {fit.get('error', 'Unknown')}")
    
    # Plots
    if make_plots:
        print("\n4. Generating plots...")
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Plot 1: Raw signals
        ax = axes[0, 0]
        t_ms = t * 1000
        for i, sig in enumerate(signals):
            ax.plot(t_ms, sig * 1e6, alpha=0.7, label=f'R{i+1} ({distances[i]*1000:.0f}mm)')
        ax.set_xlabel('Time (ms)')
        ax.set_ylabel('Displacement (μm)')
        ax.set_title('Receiver Signals')
        ax.legend(ncol=2, fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 120)
        
        # Plot 2: Dispersion curve
        ax = axes[0, 1]
        freq_theory = np.linspace(50, 150, 200)
        omega_theory = 2 * np.pi * freq_theory
        G_mag_theory = np.sqrt(true_G**2 + (omega_theory * true_eta)**2)
        c_theory = np.sqrt(2/rho) * np.sqrt(G_mag_theory**2 / (true_G + G_mag_theory))
        ax.plot(freq_theory, c_theory, 'g--', linewidth=2, label='True')
        
        if fit['success']:
            G_mag_fit = np.sqrt(fit['G_prime']**2 + (omega_theory * fit['eta'])**2)
            c_fit = np.sqrt(2/rho) * np.sqrt(G_mag_fit**2 / (fit['G_prime'] + G_mag_fit))
            ax.plot(freq_theory, c_fit, 'r-', linewidth=2, label='Fitted')
        
        ax.errorbar(dispersion['frequencies'], dispersion['velocities'],
                   yerr=dispersion['uncertainties'],
                   fmt='bo', capsize=3, markersize=6, alpha=0.7, label='Measured')
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Phase Velocity (m/s)')
        ax.set_title('Dispersion Curve')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 6)
        
        # Plot 3: Parameter summary
        ax = axes[1, 0]
        ax.axis('off')
        if fit['success']:
            text = f"""
Parameter Estimation Results
{'='*40}
True values:
  G' = {true_G:.0f} Pa
  η = {true_eta:.3f} Pa·s

Fitted values:
  G' = {fit['G_prime']:.0f} ± {fit['G_prime_err']:.0f} Pa
  η = {fit['eta']:.3f} ± {fit['eta_err']:.3f} Pa·s
  
Goodness of fit:
  R² = {fit['r_squared']:.4f}
  
Relative errors:
  G' error: {G_error:.1f}%
  η error: {eta_error:.1f}%
            """.strip()
            ax.text(0.1, 0.5, text, fontsize=10, verticalalignment='center',
                   fontfamily='monospace', transform=ax.transAxes)
        
        # Plot 4: Residuals
        ax = axes[1, 1]
        if fit['success']:
            omega = 2 * np.pi * np.array(dispersion['frequencies'])
            G_mag_fit = np.sqrt(fit['G_prime']**2 + (omega * fit['eta'])**2)
            c_fit = np.sqrt(2/rho) * np.sqrt(G_mag_fit**2 / (fit['G_prime'] + G_mag_fit))
            residuals = np.array(dispersion['velocities']) - c_fit
            
            ax.bar(dispersion['frequencies'], residuals, width=8, alpha=0.6, color='blue')
            ax.axhline(0, color='r', linestyle='-', linewidth=2)
            ax.set_xlabel('Frequency (Hz)')
            ax.set_ylabel('Residual (m/s)')
            ax.set_title('Fit Residuals')
            ax.grid(True, alpha=0.3)
        
        plt.suptitle('End-to-End Shear Wave Elastography Pipeline', 
                    fontweight='bold', fontsize=14)
        plt.tight_layout()
        plt.savefig('e2e_pipeline_result.png', dpi=150, bbox_inches='tight')
        print("   Saved: e2e_pipeline_result.png")
    
    print("\n" + "="*70)
    print("PIPELINE COMPLETE")
    print("="*70)
    
    return {
        'signals': signals,
        'dispersion': dispersion,
        'fit': fit,
        'true_G': true_G,
        'true_eta': true_eta
    }


def run_multiple_frames(n_frames=20, noise_levels=[0.05, 0.10, 0.15]):
    """Run pipeline on multiple frames at different noise levels."""
    print("="*70)
    print("END-TO-END PIPELINE - MULTIPLE FRAMES")
    print("="*70)
    
    true_G = 2000
    true_eta = 0.5
    rho = 1000
    
    distances = np.array([0.005, 0.015, 0.025, 0.035])
    frequencies = [60, 80, 100, 120, 140]
    
    results_table = []
    
    for noise in noise_levels:
        print(f"\n{'='*70}")
        print(f"Noise Level: {noise*100:.0f}%")
        print(f"{'='*70}")
        
        G_estimates = []
        
        for frame in range(n_frames):
            signals, t = generate_synthetic_data(
                distances, frequencies, true_G, true_eta, rho,
                noise_level=noise, seed=100 + frame
            )
            
            dt = 1.0 / 20000
            dispersion = extract_dispersion_gcc_phat(signals, dt, distances, frequencies)
            
            if len(dispersion['velocities']) > 0:
                fit = fit_frequentist(
                    np.array(dispersion['frequencies']),
                    np.array(dispersion['velocities']),
                    np.array(dispersion['uncertainties']),
                    rho
                )
                
                if fit['success']:
                    G_estimates.append(fit['G_prime'])
        
        if G_estimates:
            G_array = np.array(G_estimates)
            mean_G = np.mean(G_array)
            std_G = np.std(G_array)
            bias = mean_G - true_G
            
            results_table.append({
                'noise': noise,
                'n_success': len(G_estimates),
                'mean_G': mean_G,
                'std_G': std_G,
                'bias': bias,
                'rmse': np.sqrt(np.mean((G_array - true_G)**2))
            })
            
            print(f"Successful fits: {len(G_estimates)}/{n_frames}")
            print(f"G' = {mean_G:.0f} ± {std_G:.0f} Pa (bias: {bias:.0f} Pa)")
            print(f"RMSE: {np.sqrt(np.mean((G_array - true_G)**2)):.0f} Pa")
    
    # Summary table
    print("\n" + "="*70)
    print("SUMMARY TABLE")
    print("="*70)
    print(f"{'Noise':<10} {'Success':<10} {'Mean G\'':<15} {'Std G\'':<12} {'Bias':<10} {'RMSE':<10}")
    print("-"*70)
    for r in results_table:
        print(f"{r['noise']*100:.0f}%       {r['n_success']:<10} "
              f"{r['mean_G']:<15.0f} {r['std_G']:<12.0f} "
              f"{r['bias']:<10.0f} {r['rmse']:<10.0f}")
    
    return results_table


def hardware_integration_stub():
    """
    Stub showing how to integrate with real hardware.
    
    This would replace generate_synthetic_data() with actual
    ESP32 array controller acquisition.
    """
    print("""
HARDWARE INTEGRATION NOTES
==========================

To use with real ESP32 array controller:

1. Replace synthetic data generation with:

    from array_control_host import ArrayControlInterface
    
    iface = ArrayControlInterface('/dev/ttyUSB0', 921600)
    iface.connect()
    
    # Configure array
    iface.set_geometry(num_elements=8, element_pitch=0.5)
    iface.set_focus(depth_mm=30)
    
    # Acquire
    data = iface.acquire(samples=2048, num_elements=8, averages=4)
    # Returns: (num_elements, samples) array

2. Signal preprocessing:
    - Downsample from 20 MHz to ~20 kHz for shear waves
    - Apply bandpass filters
    - Handle channel-to-channel gain variations

3. Remaining pipeline is identical:
    - extract_dispersion_gcc_phat()
    - fit_frequentist() or bayesian version

4. Real-time considerations:
    - Acquisition: ~10-50 ms (depending on samples)
    - Processing: ~100-500 ms (depending on frequency bands)
    - Target: 1-2 Hz update rate for real-time display
    """)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='End-to-End Shear Wave Elastography Pipeline'
    )
    parser.add_argument('--mode', choices=['single', 'multi', 'hardware'],
                       default='single',
                       help='Operation mode')
    parser.add_argument('--frames', type=int, default=20,
                       help='Number of frames for multi mode')
    parser.add_argument('--noise', type=float, default=0.10,
                       help='Noise level (0-1)')
    
    args = parser.parse_args()
    
    if args.mode == 'single':
        # Single frame with plots
        run_pipeline_single_frame(
            true_G=2000,
            true_eta=0.5,
            noise_level=args.noise,
            make_plots=True
        )
        
    elif args.mode == 'multi':
        # Multiple frames, statistics
        run_multiple_frames(
            n_frames=args.frames,
            noise_levels=[0.05, 0.10, 0.15, 0.20]
        )
        
    elif args.mode == 'hardware':
        hardware_integration_stub()


if __name__ == '__main__':
    main()
