#!/usr/bin/env python3
"""
End-to-End Shear Wave Pipeline with Hybrid Fallback
====================================================

Improved extraction reliability using:
1. Two-stage GCC-PHAT (primary method)
2. Envelope detection (fallback when GCC-PHAT fails)
3. Quality metrics and diagnostics

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
    quality_score: float  # 0-1, higher is better
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
    
    Stage 1: Envelope peak for coarse delay (resolves phase ambiguity)
    Stage 2: GCC-PHAT for fine delay (sub-sample precision)
    
    Returns DelayResult with quality score and diagnostics.
    """
    fs = 1.0 / dt
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
    
    # Search window (ms)
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
    
    # Stage 2: GCC-PHAT for fine delay
    if use_phat:
        delay_fine, corr = gcc_phat(s1_f, s2_f, fs, freq_range=(f_center-10, f_center+10))
        method_used = ExtractionMethod.GCC_PHAT
    else:
        delay_fine, corr = gcc_standard(s1_f, s2_f, fs)
        method_used = ExtractionMethod.GCC_PHAT
    
    diagnostics['gcc_delay'] = delay_fine
    diagnostics['gcc_correlation'] = corr
    
    # Resolve phase ambiguity using coarse estimate
    period = 1.0 / f_center
    delay_diff = delay_fine - coarse_delay
    n_periods = round(delay_diff / period)
    delay = delay_fine - n_periods * period
    
    diagnostics['period'] = period
    diagnostics['n_periods_corrected'] = n_periods
    diagnostics['final_delay'] = delay
    
    # Quality assessment for GCC-PHAT
    quality_score = abs(corr)
    
    # If quality is poor, fall back to coarse estimate
    if quality_score < 0.3 or abs(delay - coarse_delay) > period:
        delay = coarse_delay
        method_used = ExtractionMethod.ENVELOPE
        quality_score = 0.3  # Baseline quality for envelope
        diagnostics['fallback_reason'] = f'low_correlation({corr:.2f})' if abs(corr) < 0.3 else 'phase_ambiguity'
    
    # Sanity check on final delay
    if delay <= 1e-9:
        diagnostics['error'] = 'Invalid delay (<= 0)'
        return DelayResult(0, 0, ExtractionMethod.FAILED, 0, diagnostics)
    
    return DelayResult(delay, corr, method_used, quality_score, diagnostics)


def extract_dispersion_hybrid(signals, dt, distances, frequencies,
                              min_quality=0.2, verbose=False):
    """
    Extract dispersion curve using hybrid GCC-PHAT + envelope fallback.
    
    Parameters:
    -----------
    signals : array (n_receivers, n_samples)
        Receiver time series
    dt : float
        Time step
    distances : array
        Receiver distances (m)
    frequencies : list
        Frequencies to analyze (Hz)
    min_quality : float
        Minimum quality score to accept a measurement
    verbose : bool
        Print diagnostic information
        
    Returns:
    --------
    dict with frequencies, velocities, uncertainties, and method statistics
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
                
                # Reasonable velocity check for shear waves
                if 0.5 <= velocity <= 10:
                    pair_velocities.append(velocity)
                    pair_weights.append(delay_result.quality_score * distance)
                    pair_methods.append(delay_result.method)
                    
                    if verbose:
                        print(f"    Pair ({i},{j}): {velocity:.2f} m/s "
                              f"({delay_result.method.value}, "
                              f"quality={delay_result.quality_score:.2f})")
        
        if pair_velocities:
            # Weighted average by quality and distance
            weights = np.array(pair_weights)
            weights = weights / np.sum(weights)
            velocities = np.array(pair_velocities)
            
            v_mean = np.average(velocities, weights=weights)
            
            # Uncertainty estimate
            if len(velocities) > 1:
                v_std = np.sqrt(np.average((velocities - v_mean)**2, weights=weights))
            else:
                v_std = 0.1 * v_mean
            
            results['frequencies'].append(f_center)
            results['velocities'].append(v_mean)
            results['uncertainties'].append(v_std)
            results['quality_scores'].append(np.mean(pair_weights))
            
            # Record primary method used
            primary_method = max(set(pair_methods), key=pair_methods.count)
            results['methods'].append(primary_method)
            
            if verbose:
                print(f"  -> Result: {v_mean:.2f} ± {v_std:.2f} m/s "
                      f"({primary_method.value})")
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
    print("HYBRID PIPELINE WITH DIAGNOSTICS")
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
        min_quality=0.2, verbose=verbose
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
    
    plt.suptitle('Hybrid Pipeline Diagnostics', fontweight='bold', fontsize=14)
    plt.savefig('hybrid_pipeline_diagnostics.png', dpi=150, bbox_inches='tight')
    print("   Saved: hybrid_pipeline_diagnostics.png")


def benchmark_hybrid_vs_gcc_only(n_trials=20):
    """Benchmark hybrid method against GCC-PHAT only."""
    print("="*70)
    print("BENCHMARK: Hybrid vs GCC-PHAT Only")
    print("="*70)
    
    true_G = 2000
    true_eta = 0.5
    rho = 1000
    distances = np.array([0.005, 0.015, 0.025, 0.035])
    frequencies = [60, 80, 100, 120, 140]
    
    noise_levels = [0.05, 0.10, 0.15, 0.20]
    
    for noise in noise_levels:
        print(f"\n{'='*70}")
        print(f"Noise Level: {noise*100:.0f}%")
        print(f"{'='*70}")
        
        hybrid_results = []
        gcc_only_results = []
        
        for trial in range(n_trials):
            signals, t = generate_synthetic_data(
                distances, frequencies, true_G, true_eta, rho,
                noise_level=noise, seed=1000 + trial
            )
            
            dt = 1.0 / 20000
            
            # Hybrid method
            disp_hybrid = extract_dispersion_hybrid(
                signals, dt, distances, frequencies, 
                min_quality=0.2, verbose=False
            )
            
            if len(disp_hybrid['velocities']) >= 3:
                fit_hybrid = fit_frequentist(
                    disp_hybrid['frequencies'],
                    disp_hybrid['velocities'],
                    disp_hybrid['uncertainties'],
                    rho
                )
                if fit_hybrid['success']:
                    hybrid_results.append(fit_hybrid['G_prime'])
            
            # GCC-PHAT only (emulated by setting min_quality very high)
            disp_gcc = extract_dispersion_hybrid(
                signals, dt, distances, frequencies,
                min_quality=0.8, verbose=False  # Only high-quality GCC-PHAT
            )
            
            if len(disp_gcc['velocities']) >= 3:
                fit_gcc = fit_frequentist(
                    disp_gcc['frequencies'],
                    disp_gcc['velocities'],
                    disp_gcc['uncertainties'],
                    rho
                )
                if fit_gcc['success']:
                    gcc_only_results.append(fit_gcc['G_prime'])
        
        # Statistics
        print(f"\n  Hybrid method:")
        print(f"    Success rate: {len(hybrid_results)}/{n_trials}")
        if hybrid_results:
            h_arr = np.array(hybrid_results)
            print(f"    G' = {np.mean(h_arr):.0f} ± {np.std(h_arr):.0f} Pa")
            print(f"    RMSE: {np.sqrt(np.mean((h_arr - true_G)**2)):.0f} Pa")
        
        print(f"\n  GCC-PHAT only (corr > 0.8):")
        print(f"    Success rate: {len(gcc_only_results)}/{n_trials}")
        if gcc_only_results:
            g_arr = np.array(gcc_only_results)
            print(f"    G' = {np.mean(g_arr):.0f} ± {np.std(g_arr):.0f} Pa")
            print(f"    RMSE: {np.sqrt(np.mean((g_arr - true_G)**2)):.0f} Pa")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Hybrid Pipeline with Fallback'
    )
    parser.add_argument('--mode', choices=['single', 'benchmark', 'sweep'],
                       default='single',
                       help='Operation mode')
    parser.add_argument('--noise', type=float, default=0.10,
                       help='Noise level (0-1)')
    parser.add_argument('--quiet', action='store_true',
                       help='Reduce output verbosity')
    
    args = parser.parse_args()
    
    if args.mode == 'single':
        run_pipeline_with_diagnostics(
            true_G=2000,
            true_eta=0.5,
            noise_level=args.noise,
            verbose=not args.quiet
        )
        
    elif args.mode == 'benchmark':
        benchmark_hybrid_vs_gcc_only(n_trials=20)
        
    elif args.mode == 'sweep':
        print("Running noise sweep...")
        for noise in [0.05, 0.10, 0.15, 0.20, 0.25]:
            print(f"\n{'='*70}")
            print(f"NOISE LEVEL: {noise*100:.0f}%")
            print(f"{'='*70}")
            run_pipeline_with_diagnostics(
                true_G=2000,
                true_eta=0.5,
                noise_level=noise,
                verbose=False
            )


if __name__ == '__main__':
    main()
