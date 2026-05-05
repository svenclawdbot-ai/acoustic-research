#!/usr/bin/env python3
"""
Compare Dispersion Extraction Methods
======================================

Systematic comparison of three dispersion extraction methods:
1. Envelope peak detection (baseline)
2. Standard GCC (without PHAT whitening)
3. GCC-PHAT (with PHAT whitening)

Tests at multiple noise levels to determine when GCC-PHAT
provides meaningful improvements.

Author: Research Project
Date: April 17, 2026
"""

import numpy as np
from scipy.signal import hilbert, butter, filtfilt
from typing import Dict, List, Tuple
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from subsample_gcc import gcc_phat, gcc_standard
from wavelet_denoising import WaveletDenoiser


def generate_narrowband_signal(t, f_center, arrival_time, burst_width=0.005):
    """Generate a narrowband tone burst with proper phase delay."""
    omega = 2 * np.pi * f_center
    envelope = np.exp(-((t - arrival_time)**2) / (2 * (burst_width/3)**2))
    carrier = np.sin(omega * (t - arrival_time))
    return envelope * carrier


def generate_test_signals(distances, frequencies, G_prime, eta, rho,
                          t, base_times, noise_level=0.0, seed=None):
    """Generate synthetic dispersive signals for multiple receivers."""
    if seed is not None:
        np.random.seed(seed)
    
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
            noise_amp = noise_level * np.std(sig)
            sig += noise_amp * np.random.randn(len(sig))
        
        signals.append(sig)
    
    return signals


def extract_dispersion_envelope(signals, dt, distances, frequencies):
    """Extract dispersion using envelope peak detection."""
    results = {'frequencies': [], 'velocities': [], 'uncertainties': []}
    fs = 1.0 / dt
    
    for f_center in frequencies:
        pair_velocities = []
        
        for i in range(len(signals) - 1):
            for j in range(i + 1, len(signals)):
                nyq = fs / 2
                low = max(0.01, (f_center - 12) / nyq)
                high = min(0.99, (f_center + 12) / nyq)
                
                try:
                    b, a = butter(2, [low, high], btype='band')
                    s1_f = filtfilt(b, a, signals[i])
                    s2_f = filtfilt(b, a, signals[j])
                except:
                    continue
                
                env1 = np.abs(hilbert(s1_f))
                env2 = np.abs(hilbert(s2_f))
                
                t_ms = np.arange(len(env1)) * dt * 1000
                search = (t_ms > 15) & (t_ms < 110)
                
                if not np.any(search):
                    continue
                
                idx = np.where(search)[0]
                p1 = idx[np.argmax(env1[search])]
                p2 = idx[np.argmax(env2[search])]
                delay = (p2 - p1) * dt
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


def extract_dispersion_gcc(signals, dt, distances, frequencies, use_phat=True):
    """Extract dispersion using GCC (optionally with PHAT)."""
    results = {'frequencies': [], 'velocities': [], 'uncertainties': []}
    fs = 1.0 / dt
    
    for f_center in frequencies:
        pair_velocities = []
        pair_correlations = []
        
        for i in range(len(signals) - 1):
            for j in range(i + 1, len(signals)):
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
                t_ms = np.arange(len(env1)) * dt * 1000
                search = (t_ms > 15) & (t_ms < 110)
                
                if not np.any(search):
                    continue
                
                idx = np.where(search)[0]
                p1 = idx[np.argmax(env1[search])]
                p2 = idx[np.argmax(env2[search])]
                coarse_delay = (p2 - p1) * dt
                
                # Fine delay from GCC
                if use_phat:
                    delay_fine, corr = gcc_phat(s1_f, s2_f, fs, 
                                                freq_range=(f_center-10, f_center+10))
                else:
                    delay_fine, corr = gcc_standard(s1_f, s2_f, fs)
                
                # Resolve phase ambiguity
                period = 1.0 / f_center
                n_periods = round((delay_fine - coarse_delay) / period)
                delay = delay_fine - n_periods * period
                
                distance = distances[j] - distances[i]
                
                if delay > 1e-9:
                    velocity = distance / delay
                    if 0.5 <= velocity <= 10:
                        pair_velocities.append(velocity)
                        pair_correlations.append(abs(corr))
        
        if pair_velocities:
            v_array = np.array(pair_velocities)
            weights = np.array(pair_correlations)
            
            if len(v_array) >= 3:
                q1, q3 = np.percentile(v_array, [25, 75])
                iqr = q3 - q1
                mask = (v_array >= q1 - 1.0*iqr) & (v_array <= q3 + 1.0*iqr)
                if np.sum(mask) >= 2:
                    v_array = v_array[mask]
                    weights = weights[mask]
            
            if len(weights) > 0 and np.sum(weights) > 0:
                weights = weights / np.sum(weights)
                v_mean = np.average(v_array, weights=weights)
            else:
                v_mean = np.median(v_array)
            
            v_std = np.std(v_array) if len(v_array) > 1 else 0.05 * v_mean
            
            if v_mean <= 2.5:
                results['frequencies'].append(f_center)
                results['velocities'].append(v_mean)
                results['uncertainties'].append(v_std)
    
    return results


def fit_kelvin_voigt(freq, vel, unc, rho=1000):
    """Fit Kelvin-Voigt model to dispersion data."""
    from scipy.optimize import curve_fit
    
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
                              bounds=([10, 0.001], [100000, 100]),
                              sigma=unc if unc is not None else None,
                              maxfev=5000)
        Gp, et = popt
        G_err, eta_err = np.sqrt(np.diag(pcov))
        
        residuals = vel - kv(omega, *popt)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((vel - np.mean(vel))**2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        return {
            'G_prime': Gp, 'eta': et,
            'G_prime_err': G_err, 'eta_err': eta_err,
            'r_squared': r2, 'success': True
        }
    except Exception as e:
        return {
            'G_prime': G0, 'eta': eta0,
            'G_prime_err': np.nan, 'eta_err': np.nan,
            'r_squared': 0, 'success': False, 'error': str(e)
        }


def run_comparison(noise_levels, G_prime_true=2000, eta_true=0.5, rho=1000,
                   n_repeats=5):
    """Run systematic comparison across noise levels."""
    
    # Setup
    fs = 20000
    dt = 1 / fs
    duration = 0.12
    t = np.linspace(0, duration, int(fs * duration))
    
    distances = np.array([0.005, 0.015, 0.025, 0.040])
    frequencies = [60, 80, 100, 120, 140]
    base_times = [0.030, 0.045, 0.060, 0.075, 0.090]
    
    results_table = []
    
    print("=" * 80)
    print("Method Comparison: Shear Wave Dispersion Extraction")
    print("=" * 80)
    print(f"True: G' = {G_prime_true} Pa, η = {eta_true} Pa·s")
    print(f"Receivers: {len(distances)}, Frequencies: {len(frequencies)}")
    print(f"Repeats per condition: {n_repeats}")
    print("=" * 80)
    
    for noise in noise_levels:
        print(f"\n{'='*80}")
        print(f"Noise Level: {noise*100:.0f}%")
        print(f"{'='*80}")
        
        envelope_errors = {'G': [], 'eta': []}
        gcc_errors = {'G': [], 'eta': []}
        gcc_phat_errors = {'G': [], 'eta': []}
        
        for repeat in range(n_repeats):
            seed = 42 + repeat
            
            signals = generate_test_signals(
                distances, frequencies, G_prime_true, eta_true, rho,
                t, base_times, noise_level=noise, seed=seed
            )
            
            # Method 1: Envelope
            res_env = extract_dispersion_envelope(signals, dt, distances, frequencies)
            if len(res_env['velocities']) > 0:
                fit_env = fit_kelvin_voigt(res_env['frequencies'], 
                                           res_env['velocities'],
                                           res_env['uncertainties'], rho)
                if fit_env['success']:
                    envelope_errors['G'].append(
                        100 * abs(fit_env['G_prime'] - G_prime_true) / G_prime_true
                    )
                    envelope_errors['eta'].append(
                        100 * abs(fit_env['eta'] - eta_true) / eta_true if eta_true > 0 else 0
                    )
            
            # Method 2: Standard GCC
            res_gcc = extract_dispersion_gcc(signals, dt, distances, frequencies, use_phat=False)
            if len(res_gcc['velocities']) > 0:
                fit_gcc = fit_kelvin_voigt(res_gcc['frequencies'],
                                          res_gcc['velocities'],
                                          res_gcc['uncertainties'], rho)
                if fit_gcc['success']:
                    gcc_errors['G'].append(
                        100 * abs(fit_gcc['G_prime'] - G_prime_true) / G_prime_true
                    )
                    gcc_errors['eta'].append(
                        100 * abs(fit_gcc['eta'] - eta_true) / eta_true if eta_true > 0 else 0
                    )
            
            # Method 3: GCC-PHAT
            res_phat = extract_dispersion_gcc(signals, dt, distances, frequencies, use_phat=True)
            if len(res_phat['velocities']) > 0:
                fit_phat = fit_kelvin_voigt(res_phat['frequencies'],
                                           res_phat['velocities'],
                                           res_phat['uncertainties'], rho)
                if fit_phat['success']:
                    gcc_phat_errors['G'].append(
                        100 * abs(fit_phat['G_prime'] - G_prime_true) / G_prime_true
                    )
                    gcc_phat_errors['eta'].append(
                        100 * abs(fit_phat['eta'] - eta_true) / eta_true if eta_true > 0 else 0
                    )
        
        # Compute statistics
        def stats(arr):
            if len(arr) == 0:
                return (np.nan, np.nan)
            return (np.mean(arr), np.std(arr))
        
        env_G_mean, env_G_std = stats(envelope_errors['G'])
        env_eta_mean, env_eta_std = stats(envelope_errors['eta'])
        gcc_G_mean, gcc_G_std = stats(gcc_errors['G'])
        gcc_eta_mean, gcc_eta_std = stats(gcc_errors['eta'])
        phat_G_mean, phat_G_std = stats(gcc_phat_errors['G'])
        phat_eta_mean, phat_eta_std = stats(gcc_phat_errors['eta'])
        
        # Store results
        results_table.append({
            'noise': noise,
            'envelope': {'G_mean': env_G_mean, 'G_std': env_G_std,
                        'eta_mean': env_eta_mean, 'eta_std': env_eta_std},
            'gcc': {'G_mean': gcc_G_mean, 'G_std': gcc_G_std,
                   'eta_mean': gcc_eta_mean, 'eta_std': gcc_eta_std},
            'gcc_phat': {'G_mean': phat_G_mean, 'G_std': phat_G_std,
                        'eta_mean': phat_eta_mean, 'eta_std': phat_eta_std}
        })
        
        # Print results for this noise level
        print(f"\nResults (mean ± std over {n_repeats} runs):")
        print("-" * 60)
        print(f"{'Method':<15} {'G\' Error %':<20} {'η Error %':<20}")
        print("-" * 60)
        print(f"{'Envelope':<15} {env_G_mean:6.1f}±{env_G_std:5.1f}      {env_eta_mean:6.1f}±{env_eta_std:5.1f}")
        print(f"{'Standard GCC':<15} {gcc_G_mean:6.1f}±{gcc_G_std:5.1f}      {gcc_eta_mean:6.1f}±{gcc_eta_std:5.1f}")
        print(f"{'GCC-PHAT':<15} {phat_G_mean:6.1f}±{phat_G_std:5.1f}      {phat_eta_mean:6.1f}±{phat_eta_std:5.1f}")
    
    return results_table


def print_summary_table(results_table):
    """Print formatted comparison table."""
    print("\n" + "=" * 80)
    print("SUMMARY: Method Comparison Across Noise Levels")
    print("=" * 80)
    print(f"{'Noise':<8} {'Method':<15} {'G\' Error %':<15} {'η Error %':<15} {'Notes'}")
    print("-" * 80)
    
    for res in results_table:
        noise_pct = f"{res['noise']*100:.0f}%"
        
        # Envelope
        print(f"{noise_pct:<8} {'Envelope':<15} "
              f"{res['envelope']['G_mean']:6.1f}±{res['envelope']['G_std']:4.1f}       "
              f"{res['envelope']['eta_mean']:6.1f}±{res['envelope']['eta_std']:4.1f}       "
              f"Baseline")
        
        # Standard GCC
        print(f"{'':8} {'Standard GCC':<15} "
              f"{res['gcc']['G_mean']:6.1f}±{res['gcc']['G_std']:4.1f}       "
              f"{res['gcc']['eta_mean']:6.1f}±{res['gcc']['eta_std']:4.1f}       "
              f"{'Better' if res['gcc']['G_mean'] < res['envelope']['G_mean'] else 'Similar'}")
        
        # GCC-PHAT
        improvement = "Best" if (res['gcc_phat']['G_mean'] < res['gcc']['G_mean'] and 
                                  res['gcc_phat']['G_mean'] < res['envelope']['G_mean']) else \
                      "Good" if res['gcc_phat']['G_mean'] < res['envelope']['G_mean'] else "Similar"
        print(f"{'':8} {'GCC-PHAT':<15} "
              f"{res['gcc_phat']['G_mean']:6.1f}±{res['gcc_phat']['G_std']:4.1f}       "
              f"{res['gcc_phat']['eta_mean']:6.1f}±{res['gcc_phat']['eta_std']:4.1f}       "
              f"{improvement}")
        
        if res != results_table[-1]:
            print("-" * 80)
    
    print("=" * 80)
    
    # Analysis
    print("\nANALYSIS:")
    print("-" * 40)
    
    # Find where GCC-PHAT shows clear advantage
    advantages = []
    for res in results_table:
        if res['gcc_phat']['G_mean'] < res['envelope']['G_mean'] - 2:
            advantages.append(f"  • At {res['noise']*100:.0f}% noise: GCC-PHAT reduces G' error by "
                              f"{res['envelope']['G_mean'] - res['gcc_phat']['G_mean']:.1f}%")
    
    if advantages:
        print("GCC-PHAT advantages:")
        for adv in advantages:
            print(adv)
    else:
        print("• GCC-PHAT shows similar performance to simpler methods on clean data")
        print("• Benefits may appear at higher noise or with real experimental data")
    
    # Check noise robustness
    high_noise = [r for r in results_table if r['noise'] >= 0.15]
    if high_noise:
        avg_env = np.mean([r['envelope']['G_mean'] for r in high_noise])
        avg_phat = np.mean([r['gcc_phat']['G_mean'] for r in high_noise])
        if avg_phat < avg_env:
            print(f"\n• At high noise (≥15%), GCC-PHAT averages {avg_env - avg_phat:.1f}% better on G'")


def main():
    """Run full comparison."""
    noise_levels = [0.05, 0.10, 0.15, 0.20, 0.25]
    
    results = run_comparison(
        noise_levels=noise_levels,
        G_prime_true=2000,
        eta_true=0.5,
        rho=1000,
        n_repeats=5
    )
    
    print_summary_table(results)
    
    print("\n" + "=" * 80)
    print("Comparison Complete!")
    print("=" * 80)


if __name__ == '__main__':
    main()
