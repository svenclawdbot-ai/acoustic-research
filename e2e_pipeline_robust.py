#!/usr/bin/env python3
"""
End-to-End Shear Wave Pipeline - Working Version
================================================

This version is based on the proven working_dispersion_demo.py
with the reliable two-stage approach and IQR outlier rejection.

Key fixes:
1. Proper envelope-based delay as primary method
2. GCC-PHAT only for sub-sample refinement (when correlation is high)
3. IQR outlier rejection on velocities (not delays)
4. Velocity sanity checks

Author: Research Project
Date: April 17, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert, butter, filtfilt
from scipy.optimize import curve_fit
from typing import Dict, List, Tuple, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from subsample_gcc import gcc_phat


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
    
    # Well-separated base arrival times for each frequency
    base_times = np.linspace(0.030, 0.090, len(frequencies))
    
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


def extract_dispersion_robust(signals, dt, distances, frequencies, 
                                use_gcc_refinement=True, verbose=False):
    """
    Extract dispersion using robust two-stage method.
    
    Stage 1: Envelope peak detection (primary, robust)
    Stage 2: GCC-PHAT for sub-sample refinement (optional)
    
    Includes IQR outlier rejection on velocities.
    """
    results = {'frequencies': [], 'velocities': [], 'uncertainties': [], 'methods': []}
    fs = 1.0 / dt
    n_receivers = len(signals)
    
    if verbose:
        print(f"\nExtracting dispersion from {n_receivers} receivers...")
    
    for f_center in frequencies:
        pair_velocities = []
        pair_info = []  # Store (i, j, delay, method) for diagnostics
        
        for i in range(n_receivers - 1):
            for j in range(i + 1, n_receivers):
                distance = distances[j] - distances[i]
                
                # Bandpass filter to isolate frequency
                nyq = fs / 2
                low = max(0.01, (f_center - 12) / nyq)
                high = min(0.99, (f_center + 12) / nyq)
                
                try:
                    b, a = butter(2, [low, high], btype='band')
                    s1_f = filtfilt(b, a, signals[i])
                    s2_f = filtfilt(b, a, signals[j])
                except:
                    continue
                
                # Stage 1: Envelope-based delay (primary method)
                env1 = np.abs(hilbert(s1_f))
                env2 = np.abs(hilbert(s2_f))
                
                # Search window where bursts arrive
                t_ms = np.arange(len(env1)) * dt * 1000
                search = (t_ms > 15) & (t_ms < 110)
                
                if not np.any(search):
                    continue
                
                idx = np.where(search)[0]
                p1 = idx[np.argmax(env1[search])]
                p2 = idx[np.argmax(env2[search])]
                coarse_delay = (p2 - p1) * dt
                delay = coarse_delay
                method = 'envelope'
                
                # Stage 2: GCC-PHAT refinement (only if correlation is good)
                if use_gcc_refinement:
                    try:
                        delay_fine, corr = gcc_phat(s1_f, s2_f, fs, 
                                                    freq_range=(f_center-10, f_center+10))
                        
                        # Only use GCC-PHAT if correlation is significant
                        # and the refined delay is reasonable
                        if abs(corr) > 0.5:  # Threshold for good correlation
                            period = 1.0 / f_center
                            n_periods = round((delay_fine - coarse_delay) / period)
                            delay_refined = delay_fine - n_periods * period
                            
                            # Validate refinement: should be close to coarse estimate
                            if abs(delay_refined - coarse_delay) < period / 2:
                                delay = delay_refined
                                method = 'gcc_phat'
                    except:
                        pass  # Fall back to envelope
                
                # Compute velocity
                if delay > 1e-9:
                    velocity = distance / delay
                    
                    # Strict velocity bounds for shear waves in tissue
                    if 0.8 <= velocity <= 2.5:
                        pair_velocities.append(velocity)
                        pair_info.append((i, j, delay, method))
        
        if pair_velocities:
            # Convert to array for outlier rejection
            v_array = np.array(pair_velocities)
            
            # IQR outlier rejection (stricter: k=1.0)
            if len(v_array) >= 3:
                q1, q3 = np.percentile(v_array, [25, 75])
                iqr = q3 - q1
                mask = (v_array >= q1 - 1.0*iqr) & (v_array <= q3 + 1.0*iqr)
                v_clean = v_array[mask]
                
                if len(v_clean) >= 2:
                    v_array = v_clean
                    n_outliers = len(pair_velocities) - len(v_array)
                    if verbose and n_outliers > 0:
                        print(f"  {f_center:.0f} Hz: removed {n_outliers} outliers")
            
            # Use median for robustness
            v_mean = np.median(v_array)
            v_std = np.std(v_array) if len(v_array) > 1 else 0.05 * v_mean
            
            # Final sanity check
            if v_mean <= 2.5:
                results['frequencies'].append(f_center)
                results['velocities'].append(v_mean)
                results['uncertainties'].append(v_std)
                
                # Determine primary method used
                methods_used = [info[3] for info in pair_info]
                primary_method = max(set(methods_used), key=methods_used.count)
                results['methods'].append(primary_method)
                
                if verbose:
                    print(f"  {f_center:.0f} Hz: c = {v_mean:.2f} ± {v_std:.2f} m/s ({primary_method})")
            elif verbose:
                print(f"  {f_center:.0f} Hz: REJECTED (outlier: {v_mean:.2f} m/s)")
    
    # Convert to arrays
    results['frequencies'] = np.array(results['frequencies'])
    results['velocities'] = np.array(results['velocities'])
    results['uncertainties'] = np.array(results['uncertainties'])
    results['valid'] = ~np.isnan(results['velocities'])
    
    return results


def fit_kelvin_voigt(freq, vel, unc, rho=1000):
    """Fit Kelvin-Voigt model to dispersion data."""
    def kv(omega, Gp, et):
        Gm = np.sqrt(Gp**2 + (omega*et)**2)
        return np.sqrt(2/rho) * np.sqrt(Gm**2 / (Gp + Gm))
    
    freq = np.array(freq)
    vel = np.array(vel)
    omega = 2 * np.pi * freq
    
    c0 = np.median(vel) if len(vel) > 0 else 1.5
    G0 = max(100, min(rho * c0**2, 50000))
    eta0 = 0.5
    
    try:
        popt, pcov = curve_fit(kv, omega, vel, p0=[G0, eta0],
                              bounds=([10, 0.001], [50000, 50]),
                              sigma=unc if unc is not None else None,
                              maxfev=5000)
        Gp, et = popt
        G_err, eta_err = np.sqrt(np.diag(pcov))
        
        residuals = vel - kv(omega, *popt)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((vel - np.mean(vel))**2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        return {'G_prime': Gp, 'eta': et, 'G_prime_err': G_err, 
                'eta_err': eta_err, 'r_squared': r2, 'success': True}
    except Exception as e:
        return {'G_prime': G0, 'eta': eta0, 'success': False, 'error': str(e)}


def run_pipeline(true_G=2000, true_eta=0.5, rho=1000, noise_level=0.10):
    """Run complete end-to-end pipeline."""
    print("="*70)
    print("END-TO-END PIPELINE - ROBUST VERSION")
    print("="*70)
    print(f"True: G' = {true_G} Pa, η = {true_eta} Pa·s")
    print(f"Noise: {noise_level*100:.0f}%")
    print("="*70)
    
    # Setup
    fs = 20000
    dt = 1.0 / fs
    distances = np.array([0.005, 0.015, 0.025, 0.035])
    frequencies = [60, 80, 100, 120, 140]
    
    # Generate data
    print("\n1. Generating synthetic data...")
    signals, t = generate_synthetic_data(
        distances, frequencies, true_G, true_eta, rho,
        fs=fs, noise_level=noise_level, seed=42
    )
    print(f"   {signals.shape[0]} channels, {signals.shape[1]} samples")
    
    # Extract dispersion
    print("\n2. Extracting dispersion (robust method)...")
    dispersion = extract_dispersion_robust(
        signals, dt, distances, frequencies, 
        use_gcc_refinement=True, verbose=True
    )
    
    print(f"\n   Extracted {len(dispersion['velocities'])} frequency points")
    
    if len(dispersion['velocities']) == 0:
        print("   ERROR: No dispersion points extracted!")
        return None
    
    # Print results
    print(f"\n   {'Freq (Hz)':<12} {'Velocity (m/s)':<18} {'Method':<15}")
    print("   " + "-"*45)
    for i in range(len(dispersion['frequencies'])):
        f = dispersion['frequencies'][i]
        v = dispersion['velocities'][i]
        u = dispersion['uncertainties'][i]
        m = dispersion['methods'][i]
        print(f"   {f:<12.0f} {v:.2f} ± {u:.2f}       {m:<15}")
    
    # Fit parameters
    print("\n3. Fitting Kelvin-Voigt model...")
    fit = fit_kelvin_voigt(
        dispersion['frequencies'],
        dispersion['velocities'],
        dispersion['uncertainties'],
        rho
    )
    
    if fit['success']:
        print(f"   G' = {fit['G_prime']:.0f} ± {fit['G_prime_err']:.0f} Pa")
        print(f"   η = {fit['eta']:.3f} ± {fit['eta_err']:.3f} Pa·s")
        print(f"   R² = {fit['r_squared']:.4f}")
        
        G_error = 100 * abs(fit['G_prime'] - true_G) / true_G
        eta_error = 100 * abs(fit['eta'] - true_eta) / true_eta if true_eta > 0 else 0
        print(f"\n   Relative errors: G' = {G_error:.1f}%, η = {eta_error:.1f}%")
    else:
        print(f"   Fit failed: {fit.get('error', 'Unknown')}")
    
    # Generate plot
    print("\n4. Generating plot...")
    create_plot(signals, t, distances, dispersion, fit, true_G, true_eta, rho)
    
    print("\n" + "="*70)
    print("PIPELINE COMPLETE")
    print("="*70)
    
    return {'signals': signals, 'dispersion': dispersion, 'fit': fit}


def create_plot(signals, t, distances, dispersion, fit, true_G, true_eta, rho):
    """Create diagnostic plot."""
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
    
    # True curve
    freq_theory = np.linspace(50, 150, 200)
    omega_theory = 2 * np.pi * freq_theory
    G_mag_theory = np.sqrt(true_G**2 + (omega_theory * true_eta)**2)
    c_theory = np.sqrt(2/rho) * np.sqrt(G_mag_theory**2 / (true_G + G_mag_theory))
    ax.plot(freq_theory, c_theory, 'g--', linewidth=2, label='True')
    
    # Fitted curve
    if fit['success']:
        G_mag_fit = np.sqrt(fit['G_prime']**2 + (omega_theory * fit['eta'])**2)
        c_fit = np.sqrt(2/rho) * np.sqrt(G_mag_fit**2 / (fit['G_prime'] + G_mag_fit))
        ax.plot(freq_theory, c_fit, 'r-', linewidth=2, label='Fitted')
    
    # Measured points
    method_colors = {'gcc_phat': 'blue', 'envelope': 'orange'}
    for i in range(len(dispersion['frequencies'])):
        f = dispersion['frequencies'][i]
        v = dispersion['velocities'][i]
        u = dispersion['uncertainties'][i]
        m = dispersion['methods'][i]
        color = method_colors.get(m, 'grey')
        ax.errorbar(f, v, yerr=u, fmt='o', color=color, capsize=3, markersize=8)
    
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Phase Velocity (m/s)')
    ax.set_title('Dispersion Curve (Blue=GCC-PHAT, Orange=Envelope)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 6)
    
    # Plot 3: Parameter results
    ax = axes[1, 0]
    ax.axis('off')
    if fit['success']:
        G_error = 100 * abs(fit['G_prime'] - true_G) / true_G
        eta_error = 100 * abs(fit['eta'] - true_eta) / true_eta if true_eta > 0 else 0
        text = f"""
Parameter Estimation Results
{'='*35}
True values:
  G' = {true_G:.0f} Pa
  η = {true_eta:.3f} Pa·s

Fitted values:
  G' = {fit['G_prime']:.0f} ± {fit['G_prime_err']:.0f} Pa
  η = {fit['eta']:.3f} ± {fit['eta_err']:.3f} Pa·s

Relative errors:
  G' error: {G_error:.1f}%
  η error: {eta_error:.1f}%

Goodness of fit:
  R² = {fit['r_squared']:.4f}
        """.strip()
        ax.text(0.1, 0.5, text, fontsize=10, verticalalignment='center',
               fontfamily='monospace', transform=ax.transAxes)
    
    # Plot 4: Residuals
    ax = axes[1, 1]
    if fit['success'] and len(dispersion['frequencies']) > 0:
        omega = 2 * np.pi * dispersion['frequencies']
        G_mag_fit = np.sqrt(fit['G_prime']**2 + (omega * fit['eta'])**2)
        c_fit = np.sqrt(2/rho) * np.sqrt(G_mag_fit**2 / (fit['G_prime'] + G_mag_fit))
        residuals = dispersion['velocities'] - c_fit
        
        colors = [method_colors.get(m, 'grey') for m in dispersion['methods']]
        ax.scatter(dispersion['frequencies'], residuals, c=colors, s=100, alpha=0.7)
        ax.axhline(0, color='r', linestyle='-', linewidth=2)
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Residual (m/s)')
        ax.set_title('Fit Residuals')
        ax.grid(True, alpha=0.3)
    
    plt.suptitle('End-to-End Pipeline (Robust)', fontweight='bold', fontsize=14)
    plt.tight_layout()
    plt.savefig('e2e_pipeline_robust.png', dpi=150, bbox_inches='tight')
    print("   Saved: e2e_pipeline_robust.png")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='End-to-End Pipeline (Robust)')
    parser.add_argument('--noise', type=float, default=0.10, help='Noise level (0-1)')
    args = parser.parse_args()
    
    run_pipeline(noise_level=args.noise)


if __name__ == '__main__':
    main()
