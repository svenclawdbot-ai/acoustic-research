#!/usr/bin/env python3
"""
End-to-End Shear Wave Pipeline with Hybrid Fallback (Fixed)
=============================================================

Fixed version with:
1. Proper phase ambiguity resolution
2. IQR outlier rejection
3. Velocity sanity checks
4. Better quality metrics

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
from dataclasses import dataclass
from enum import Enum

sys.path.insert(0, os.path.dirname(__file__))
from subsample_gcc import gcc_phat, gcc_standard
from bayesian_dispersion import kelvin_voigt_velocity, fit_frequentist


class ExtractionMethod(Enum):
    """Methods used for delay extraction."""
    GCC_PHAT = "gcc_phat"
    ENVELOPE = "envelope"
    FAILED = "failed"


@dataclass
class DelayResult:
    """Result from a single delay estimation attempt."""
    delay: float
    correlation: float
    method: ExtractionMethod
    quality_score: float
    diagnostic_info: Dict


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


def extract_delay_two_stage(s1, s2, dt, f_center, use_phat=True):
    """
    Extract delay using two-stage approach with quality metrics.
    
    FIXED: Better phase ambiguity resolution and validation.
    """
    fs = 1.0 / fs if 'fs' in locals() else 1.0 / dt
    diagnostics = {}
    
    # Ensure equal length
    min_len = min(len(s1), len(s2))
    s1 = s1[:min_len]
    s2 = s2[:min_len]
    
    # Bandpass filter both signals
    nyq = fs / 2
    low = max(0.01, (f_center - 12) / nyq)
    high = min(0.99, (f_center + 12) / nyq)
    
    try:
        b, a = butter(2, [low, high], btype='band')
        s1_f = filtfilt(b, a, s1)
        s2_f = filtfilt(b, a, s2)
    except Exception as e:
        diagnostics['filter_error'] = str(e)
        return DelayResult(0, 0, ExtractionMethod.FAILED, 0, diagnostics)
    
    # Stage 1: Envelope-based coarse delay
    env1 = np.abs(hilbert(s1_f))
    env2 = np.abs(hilbert(s2_f))
    
    # Search window (ms) - focus on where bursts arrive
    t_ms = np.arange(len(env1)) * dt * 1000
    search_mask = (t_ms >= 15) & (t_ms <= 110)
    
    if not np.any(search_mask):
        diagnostics['error'] = 'No samples in search window'
        return DelayResult(0, 0, ExtractionMethod.FAILED, 0, diagnostics)
    
    idx = np.where(search_mask)[0]
    peak1_idx = idx[np.argmax(env1[search_mask])]
    peak2_idx = idx[np.argmax(env2[search_mask])]
    coarse_delay = (peak2_idx - peak1_idx) * dt
    
    diagnostics['coarse_delay'] = coarse_delay
    diagnostics['peak1_idx'] = peak1_idx
    diagnostics['peak2_idx'] = peak2_idx
    
    # Validate coarse delay - should be positive (signal arrives later at farther receiver)
    if coarse_delay <= 0:
        diagnostics['error'] = f'Invalid coarse delay: {coarse_delay:.4f}'
        return DelayResult(0, 0, ExtractionMethod.FAILED, 0, diagnostics)
    
    # Stage 2: GCC-PHAT for fine delay
    try:
        if use_phat:
            delay_fine, corr = gcc_phat(s1_f, s2_f, fs, freq_range=(f_center-10, f_center+10))
        else:
            delay_fine, corr = gcc_standard(s1_f, s2_f, fs)
    except Exception as e:
        diagnostics['gcc_error'] = str(e)
        # Fall back to envelope
        return DelayResult(coarse_delay, 0.5, ExtractionMethod.ENVELOPE, 0.5, diagnostics)
    
    diagnostics['gcc_delay'] = delay_fine
    diagnostics['gcc_correlation'] = corr
    
    # FIXED: Better phase ambiguity resolution
    period = 1.0 / f_center
    delay_diff = delay_fine - coarse_delay
    n_periods = round(delay_diff / period)
    delay_corrected = delay_fine - n_periods * period
    
    diagnostics['period'] = period
    diagnostics['n_periods_corrected'] = n_periods
    diagnostics['delay_before_correction'] = delay_fine
    diagnostics['delay_after_correction'] = delay_corrected
    
    # FIXED: Validate correction - corrected delay should be close to coarse estimate
    if abs(delay_corrected - coarse_delay) > period / 2:
        # Correction seems wrong - fall back to coarse
        diagnostics['fallback_reason'] = f'correction_too_large({abs(delay_corrected - coarse_delay):.4f})'
        return DelayResult(coarse_delay, abs(corr), ExtractionMethod.ENVELOPE, 0.5, diagnostics)
    
    # Quality based on correlation (normalize to 0-1)
    quality_score = min(abs(corr), 1.0)
    
    # Validate final delay
    if delay_corrected <= 1e-9:
        diagnostics['error'] = 'Invalid delay (<= 0)'
        return DelayResult(0, 0, ExtractionMethod.FAILED, 0, diagnostics)
    
    return DelayResult(delay_corrected, abs(corr), ExtractionMethod.GCC_PHAT, quality_score, diagnostics)


def extract_dispersion_hybrid(signals, dt, distances, frequencies,
                              min_quality=0.3, max_velocity=2.5, verbose=False):
    """
    Extract dispersion curve using hybrid GCC-PHAT + envelope fallback.
    
    FIXED: Added IQR outlier rejection and velocity sanity checks.
    """
    results = {
        'frequencies': [],
        'velocities': [],
        'uncertainties': [],
        'methods': [],
        'quality_scores': [],
        'diagnostics': []
    }
    
    method_counts = {method: 0 for method in ExtractionMethod}
    
    for f_center in frequencies:
        pair_velocities = []
        pair_weights = []
        pair_methods = []
        
        if verbose:
            print(f"\n  Processing {f_center:.0f} Hz:")
        
        # Compare all receiver pairs
        for i in range(len(signals) - 1):
            for j in range(i + 1, len(signals)):
                distance = distances[j] - distances[i]
                
                # Extract delay using hybrid method
                delay_result = extract_delay_two_stage(
                    signals[i], signals[j], dt, f_center, use_phat=True
                )
                
                method_counts[delay_result.method] += 1
                
                # Skip if quality too low
                if delay_result.quality_score < min_quality:
                    if verbose:
                        print(f"    Pair ({i},{j}): FAILED (quality={delay_result.quality_score:.2f})")
                    continue
                
                # Compute velocity
                velocity = distance / delay_result.delay
                
                # FIXED: Stricter velocity bounds (shear waves in soft tissue: 1-2.5 m/s)
                if 0.8 <= velocity <= max_velocity:
                    pair_velocities.append(velocity)
                    pair_weights.append(delay_result.quality_score * distance)
                    pair_methods.append(delay_result.method)
                    
                    if verbose:
                        print(f"    Pair ({i},{j}): {velocity:.2f} m/s "
                              f"({delay_result.method.value}, "
                              f"quality={delay_result.quality_score:.2f})")
                else:
                    if verbose:
                        print(f"    Pair ({i},{j}): REJECTED (velocity={velocity:.2f} m/s)")
        
        if pair_velocities:
            # FIXED: IQR outlier rejection (stricter: k=1.0)
            v_array = np.array(pair_velocities)
            w_array = np.array(pair_weights)
            
            if len(v_array) >= 3:
                q1, q3 = np.percentile(v_array, [25, 75])
                iqr = q3 - q1
                mask = (v_array >= q1 - 1.0*iqr) & (v_array <= q3 + 1.0*iqr)
                v_clean = v_array[mask]
                w_clean = w_array[mask]
                if len(v_clean) >= 2:
                    v_array = v_clean
                    w_array = w_clean
                    if verbose:
                        n_outliers = len(pair_velocities) - len(v_array)
                        if n_outliers > 0:
                            print(f"    Removed {n_outliers} outliers via IQR")
            
            # Weighted average by quality and distance
            if np.sum(w_array) > 0:
                weights = w_array / np.sum(w_array)
                v_mean = np.average(v_array, weights=weights)
            else:
                v_mean = np.median(v_array)
            
            # Uncertainty estimate
            if len(v_array) > 1:
                v_std = np.sqrt(np.average((v_array - v_mean)**2, weights=weights))
            else:
                v_std = 0.05 * v_mean
            
            # FIXED: Final sanity check on mean velocity
            if v_mean <= max_velocity:
                results['frequencies'].append(f_center)
                results['velocities'].append(v_mean)
                results['uncertainties'].append(v_std)
                results['quality_scores'].append(np.mean(w_array))
                
                # Record primary method used
                primary_method = max(set(pair_methods), key=pair_methods.count)
                results['methods'].append(primary_method)
                
                if verbose:
                    print(f"  -> Result: {v_mean:.2f} ± {v_std:.2f} m/s "
                          f"({primary_method.value})")
            else:
                if verbose:
                    print(f"  -> REJECTED (mean velocity {v_mean:.2f} m/s too high)")
        else:
            if verbose:
                print(f"  -> NO VALID MEASUREMENTS")
    
    # Convert to arrays
    results['frequencies'] = np.array(results['frequencies'])
    results['velocities'] = np.array(results['velocities'])
    results['uncertainties'] = np.array(results['uncertainties'])
    
    # Add method statistics
    results['method_stats'] = method_counts
    results['valid'] = ~np.isnan(results['velocities'])
    
    return results


def run_pipeline_with_diagnostics(true_G=2000, true_eta=0.5, rho=1000, 
                                   noise_level=0.10, verbose=True):
    """Run complete pipeline with detailed diagnostics."""
    print("="*70)
    print("HYBRID PIPELINE WITH DIAGNOSTICS (FIXED)")
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
    
    # Extract dispersion with diagnostics
    print("\n2. Extracting dispersion (hybrid method)...")
    dispersion = extract_dispersion_hybrid(
        signals, dt, distances, frequencies, 
        min_quality=0.3, max_velocity=2.5, verbose=verbose
    )
    
    print(f"\n   Extracted {len(dispersion['velocities'])} frequency points")
    print(f"   Method breakdown:")
    for method, count in dispersion['method_stats'].items():
        if count > 0:
            print(f"     {method.value}: {count} pair measurements")
    
    if len(dispersion['velocities']) == 0:
        print("\n   ERROR: No dispersion points extracted!")
        return None
    
    # Print results table
    print(f"\n   {'Freq (Hz)':<12} {'Velocity (m/s)':<18} {'Method':<15} {'Quality'}")
    print("   " + "-"*60)
    for i in range(len(dispersion['frequencies'])):
        f = dispersion['frequencies'][i]
        v = dispersion['velocities'][i]
        u = dispersion['uncertainties'][i]
        m = dispersion['methods'][i].value
        q = dispersion['quality_scores'][i]
        print(f"   {f:<12.0f} {v:.2f} ± {u:.2f}       {m:<15} {q:.2f}")
    
    # Fit parameters
    print("\n3. Fitting Kelvin-Voigt model...")
    fit = fit_frequentist(
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
    
    # Generate plots
    print("\n4. Generating diagnostic plots...")
    create_diagnostic_plots(signals, t, distances, dispersion, fit, 
                           true_G, true_eta, rho)
    
    print("\n" + "="*70)
    print("PIPELINE COMPLETE")
    print("="*70)
    
    return {
        'signals': signals,
        'dispersion': dispersion,
        'fit': fit
    }


def create_diagnostic_plots(signals, t, distances, dispersion, fit,
                           true_G, true_eta, rho):
    """Create comprehensive diagnostic plots."""
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # Plot 1: Raw signals
    ax = fig.add_subplot(gs[0, :])
    t_ms = t * 1000
    for i, sig in enumerate(signals):
        ax.plot(t_ms, sig * 1e6, alpha=0.7, label=f'R{i+1} ({distances[i]*1000:.0f}mm)')
    ax.set_xlabel('Time (ms)')
    ax.set_ylabel('Displacement (μm)')
    ax.set_title('Raw Receiver Signals')
    ax.legend(ncol=4, fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 120)
    
    # Plot 2: Dispersion curve
    ax = fig.add_subplot(gs[1, 0])
    
    # True curve
    freq_theory = np.linspace(50, 150, 200)
    omega_theory = 2 * np.pi * freq_theory
    G_mag_theory = np.sqrt(true_G**2 + (omega_theory * true_eta)**2)
    c_theory = np.sqrt(2/rho) * np.sqrt(G_mag_theory**2 / (true_G + G_mag_theory))
    ax.plot(freq_theory, c_theory, 'g--', linewidth=2, label='True', alpha=0.7)
    
    # Fitted curve
    if fit['success']:
        G_mag_fit = np.sqrt(fit['G_prime']**2 + (omega_theory * fit['eta'])**2)
        c_fit = np.sqrt(2/rho) * np.sqrt(G_mag_fit**2 / (fit['G_prime'] + G_mag_fit))
        ax.plot(freq_theory, c_fit, 'r-', linewidth=2, label='Fitted', alpha=0.7)
    
    # Measured points with method coloring
    method_colors = {
        ExtractionMethod.GCC_PHAT: 'blue',
        ExtractionMethod.ENVELOPE: 'orange',
        ExtractionMethod.FAILED: 'red'
    }
    
    for i in range(len(dispersion['frequencies'])):
        f = dispersion['frequencies'][i]
        v = dispersion['velocities'][i]
        u = dispersion['uncertainties'][i]
        m = dispersion['methods'][i]
        color = method_colors.get(m, 'grey')
        ax.errorbar(f, v, yerr=u, fmt='o', color=color, capsize=3, 
                   markersize=8, alpha=0.8)
    
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Phase Velocity (m/s)')
    ax.set_title('Dispersion Curve (Blue=GCC-PHAT, Orange=Envelope)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 6)
    
    # Plot 3: Method usage pie chart
    ax = fig.add_subplot(gs[1, 1])
    method_counts = dispersion['method_stats']
    labels = []
    sizes = []
    colors = []
    for method, count in method_counts.items():
        if count > 0:
            labels.append(method.value.replace('_', ' ').title())
            sizes.append(count)
            colors.append(method_colors.get(method, 'grey'))
    
    if sizes:
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.0f%%',
               startangle=90)
        ax.set_title('Method Usage Distribution')
    else:
        ax.text(0.5, 0.5, 'No valid\nmeasurements', 
               ha='center', va='center', transform=ax.transAxes)
        ax.set_title('Method Usage')
    
    # Plot 4: Quality scores
    ax = fig.add_subplot(gs[1, 2])
    if len(dispersion['quality_scores']) > 0:
        ax.bar(dispersion['frequencies'], dispersion['quality_scores'], 
               width=8, alpha=0.7, color='green')
        ax.axhline(0.3, color='r', linestyle='--', label='Min quality threshold')
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Quality Score')
        ax.set_title('Measurement Quality by Frequency')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    # Plot 5: Parameter results
    ax = fig.add_subplot(gs[2, 0])
    ax.axis('off')
    if fit['success']:
        G_error = 100 * abs(fit['G_prime'] - true_G) / true_G
        eta_error = 100 * abs(fit['eta'] - true_eta) / true_eta if true_eta > 0 else 0
        
        text = f"""
Parameter Estimation Results
{'='*40}
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
    
    # Plot 6: Residuals
    ax = fig.add_subplot(gs[2, 1:])
    if fit['success'] and len(dispersion['frequencies']) > 0:
        omega = 2 * np.pi * dispersion['frequencies']
        G_mag_fit = np.sqrt(fit['G_prime']**2 + (omega * fit['eta'])**2)
        c_fit = np.sqrt(2/rho) * np.sqrt(G_mag_fit**2 / (fit['G_prime'] + G_mag_fit))
        residuals = dispersion['velocities'] - c_fit
        
        colors_res = [method_colors.get(m, 'grey') for m in dispersion['methods']]
        ax.scatter(dispersion['frequencies'], residuals, c=colors_res, s=100, alpha=0.7)
        ax.axhline(0, color='r', linestyle='-', linewidth=2)
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Residual (m/s)')
        ax.set_title('Fit Residuals (Color = Method)')
        ax.grid(True, alpha=0.3)
    
    plt.suptitle('Hybrid Pipeline Diagnostics (Fixed)', fontweight='bold', fontsize=14)
    plt.savefig('hybrid_pipeline_fixed.png', dpi=150, bbox_inches='tight')
    print("   Saved: hybrid_pipeline_fixed.png")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Hybrid Pipeline with Fallback (Fixed)'
    )
    parser.add_argument('--noise', type=float, default=0.10,
                       help='Noise level (0-1)')
    parser.add_argument('--quiet', action='store_true',
                       help='Reduce output verbosity')
    
    args = parser.parse_args()
    
    run_pipeline_with_diagnostics(
        true_G=2000,
        true_eta=0.5,
        noise_level=args.noise,
        verbose=not args.quiet
    )


if __name__ == '__main__':
    main()
