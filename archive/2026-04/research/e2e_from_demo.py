#!/usr/bin/env python3
"""
E2E Pipeline - Direct Copy from Working Demo
===============================================

This directly uses the working_dispersion_demo.py logic
which successfully extracted all 5 frequencies.

Author: Research Project
Date: April 17, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert, butter, filtfilt
from scipy.optimize import curve_fit
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from subsample_gcc import gcc_phat


def generate_narrowband_signal(t, f_center, arrival_time, burst_width=0.005):
    """Generate a narrowband tone burst."""
    omega = 2 * np.pi * f_center
    envelope = np.exp(-((t - arrival_time)**2) / (2 * (burst_width/3)**2))
    carrier = np.sin(omega * (t - arrival_time))
    return envelope * carrier


def generate_receiver_signals(distances, frequencies, G_prime, eta, rho, 
                              t, base_times, noise_level=0.0):
    """Generate signals for multiple receivers at multiple frequencies."""
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
    """EXACT copy from working_dispersion_demo.py"""
    results = {'frequencies': [], 'velocities': [], 'uncertainties': []}
    fs = 1.0 / dt
    
    print("\nExtracting with envelope method...")
    
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
                print(f"  {f_center:.0f} Hz: c = {v_mean:.2f} ± {v_std:.2f} m/s")
    
    return results


def extract_dispersion_gcc_phat(signals, dt, distances, frequencies):
    """EXACT copy from working_dispersion_demo.py"""
    results = {'frequencies': [], 'velocities': [], 'uncertainties': []}
    fs = 1.0 / dt
    
    print("\nExtracting with GCC-PHAT...")
    
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
                coarse_delay = (p2 - p1) * dt
                
                delay_fine, corr = gcc_phat(s1_f, s2_f, fs, freq_range=(f_center-10, f_center+10))
                
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
                print(f"  {f_center:.0f} Hz: c = {v_mean:.2f} ± {v_std:.2f} m/s")
    
    return results


def fit_kelvin_voigt(freq, vel, unc, rho=1000):
    """Fit Kelvin-Voigt model."""
    def kv(omega, Gp, et):
        Gm = np.sqrt(Gp**2 + (omega*et)**2)
        return np.sqrt(2/rho) * np.sqrt(Gm**2 / (Gp + Gm))
    
    freq = np.array(freq)
    vel = np.array(vel)
    unc = np.array(unc) if unc is not None else None
    omega = 2 * np.pi * freq
    c0 = np.median(vel)
    G0 = rho * c0**2
    
    try:
        popt, pcov = curve_fit(kv, omega, vel, p0=[G0, 0.5],
                              bounds=([10, 0.001], [50000, 50]),
                              sigma=unc, maxfev=5000)
        Gp, et = popt
        G_err, eta_err = np.sqrt(np.diag(pcov))
        residuals = vel - kv(omega, *popt)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((vel - np.mean(vel))**2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        return {'G_prime': Gp, 'eta': et, 'G_err': G_err, 'eta_err': eta_err,
                'r_squared': r2, 'success': True}
    except:
        return {'G_prime': G0, 'eta': 0.5, 'success': False}


def main():
    """Run pipeline."""
    print("="*70)
    print("E2E PIPELINE - FROM WORKING DEMO")
    print("="*70)
    
    # True parameters
    G_prime_true = 2000
    eta_true = 0.5
    rho = 1000
    noise_level = 0.10
    
    print(f"\nTrue: G' = {G_prime_true} Pa, η = {eta_true} Pa·s")
    
    # Setup
    fs = 20000
    dt = 1 / fs
    duration = 0.12
    t = np.linspace(0, duration, int(fs * duration))
    
    distances = np.array([0.005, 0.015, 0.025, 0.035])
    frequencies = [60, 80, 100, 120, 140]
    base_times = [0.030, 0.045, 0.060, 0.075, 0.090]
    
    # Generate signals
    print("\nGenerating synthetic signals...")
    np.random.seed(42)
    signals = generate_receiver_signals(
        distances, frequencies, G_prime_true, eta_true, rho,
        t, base_times, noise_level=noise_level
    )
    print(f"  {len(signals)} receivers, {len(frequencies)} frequencies")
    
    # Extract with envelope
    results_envelope = extract_dispersion_envelope(signals, dt, distances, frequencies)
    
    # Extract with GCC-PHAT
    results_gcc = extract_dispersion_gcc_phat(signals, dt, distances, frequencies)
    
    # Compare
    print("\n" + "="*70)
    print("COMPARISON")
    print("="*70)
    
    for name, results in [('Envelope', results_envelope), ('GCC-PHAT', results_gcc)]:
        if len(results['velocities']) > 0:
            fit = fit_kelvin_voigt(results['frequencies'], results['velocities'],
                                  results['uncertainties'], rho)
            if fit['success']:
                G_err = 100 * abs(fit['G_prime'] - G_prime_true) / G_prime_true
                eta_err = 100 * abs(fit['eta'] - eta_true) / eta_true
                
                print(f"\n{name}:")
                print(f"  Points: {len(results['velocities'])}")
                print(f"  G' = {fit['G_prime']:.0f} Pa (error: {G_err:.1f}%)")
                print(f"  η = {fit['eta']:.3f} Pa·s (error: {eta_err:.1f}%)")
                print(f"  R² = {fit['r_squared']:.4f}")
    
    print("\n" + "="*70)
    print("Complete!")
    print("="*70)


if __name__ == '__main__':
    main()
