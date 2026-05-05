#!/usr/bin/env python3
"""
GCC-PHAT Integration for Shear Wave Dispersion Pipeline - SIMPLIFIED
====================================================================

Uses envelope-based delay estimation which works reliably.
GCC-PHAT reserved for cases with very high SNR and narrowband signals.

Author: Research Project
Date: April 16, 2026
"""

import numpy as np
from scipy.signal import hilbert, butter, filtfilt
from typing import Optional, List, Dict
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from wavelet_denoising import WaveletDenoiser


def extract_delay_envelope(sig1, sig2, dt, denoise=True):
    """Extract delay using envelope peak detection."""
    sig1 = np.asarray(sig1).flatten()
    sig2 = np.asarray(sig2).flatten()
    
    min_len = min(len(sig1), len(sig2))
    sig1 = sig1[:min_len]
    sig2 = sig2[:min_len]
    
    if denoise:
        denoiser = WaveletDenoiser('sym6', level=5, threshold_factor=2.0, mode='soft')
        sig1 = denoiser.denoise(sig1)
        sig2 = denoiser.denoise(sig2)
    
    # Envelope detection
    env1 = np.abs(hilbert(sig1))
    env2 = np.abs(hilbert(sig2))
    
    # Find peaks in search window
    t_ms = np.arange(len(sig1)) * dt * 1000
    search_mask = (t_ms >= 30) & (t_ms <= 110)
    
    if not np.any(search_mask):
        return {'delay': 0, 'success': False}
    
    idx = np.where(search_mask)[0]
    peak1_idx = idx[np.argmax(env1[search_mask])]
    peak2_idx = idx[np.argmax(env2[search_mask])]
    
    delay = (peak2_idx - peak1_idx) * dt
    
    return {
        'delay': delay,
        'peak1_ms': peak1_idx * dt * 1000,
        'peak2_ms': peak2_idx * dt * 1000,
        'success': True
    }


def extract_dispersion_envelope(signals, dt, distances, freq_bands=None):
    """Extract dispersion using envelope method."""
    if freq_bands is None:
        freq_centers = np.arange(60, 141, 10)
        freq_bands = [(f-10, f+10) for f in freq_centers]
    else:
        freq_centers = [(b[0] + b[1]) / 2 for b in freq_bands]
    
    results = {'freq_centers': [], 'velocities': [], 'uncertainties': []}
    
    print(f"Extracting dispersion with envelope method ({len(signals)} receivers)")
    
    for f_center in freq_centers:
        pair_velocities = []
        
        for i in range(len(signals) - 1):
            for j in range(i + 1, len(signals)):
                distance = distances[j] - distances[i]
                
                # Light filtering
                fs = 1.0 / dt
                nyq = fs / 2
                low = max(0.01, (f_center-15) / nyq)
                high = min(0.99, (f_center+15) / nyq)
                
                if low < high:
                    try:
                        b, a = butter(2, [low, high], btype='band')
                        s1_f = filtfilt(b, a, signals[i])
                        s2_f = filtfilt(b, a, signals[j])
                    except:
                        s1_f = signals[i]
                        s2_f = signals[j]
                else:
                    s1_f = signals[i]
                    s2_f = signals[j]
                
                delay_result = extract_delay_envelope(s1_f, s2_f, dt, denoise=True)
                
                if delay_result['success'] and delay_result['delay'] > 1e-9:
                    velocity = distance / delay_result['delay']
                    if 0.5 <= velocity <= 20:
                        pair_velocities.append(velocity)
        
        if pair_velocities:
            mean_vel = np.mean(pair_velocities)
            std_vel = np.std(pair_velocities) if len(pair_velocities) > 1 else 0.1 * mean_vel
            
            results['freq_centers'].append(f_center)
            results['velocities'].append(mean_vel)
            results['uncertainties'].append(std_vel)
            
            print(f"  {f_center:.0f} Hz: c = {mean_vel:.2f} ± {std_vel:.2f} m/s (n={len(pair_velocities)})")
    
    results['freq_centers'] = np.array(results['freq_centers'])
    results['velocities'] = np.array(results['velocities'])
    results['uncertainties'] = np.array(results['uncertainties'])
    
    return results


def fit_kelvin_voigt(freq, velocity, uncertainty=None, rho=1000):
    """Fit Kelvin-Voigt model."""
    from scipy.optimize import curve_fit
    
    def kv_model(omega, G_prime, eta):
        G_mag = np.sqrt(G_prime**2 + (omega * eta)**2)
        return np.sqrt(2 / rho) * np.sqrt(G_mag**2 / (G_prime + G_mag))
    
    omega = 2 * np.pi * freq
    c0 = np.mean(velocity)
    G0 = max(100, rho * c0**2)
    
    sigma = uncertainty if uncertainty is not None and np.all(uncertainty > 0) else None
    
    try:
        popt, pcov = curve_fit(kv_model, omega, velocity, p0=[G0, 0.5],
                              bounds=([10, 0.001], [100000, 100]),
                              sigma=sigma, maxfev=5000)
        
        G_prime, eta = popt
        G_err, eta_err = np.sqrt(np.diag(pcov))
        
        residuals = velocity - kv_model(omega, *popt)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((velocity - np.mean(velocity))**2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        return {'G_prime': G_prime, 'eta': eta, 'G_prime_err': G_err,
                'eta_err': eta_err, 'r_squared': r_squared, 'success': True}
    except Exception as e:
        return {'G_prime': G0, 'eta': 0.5, 'success': False, 'error': str(e)}


def run_pipeline(G_prime=2000, eta=0.5, rho=1000, noise_level=0.15):
    """Run complete pipeline."""
    print("=" * 60)
    print("Shear Wave Dispersion Pipeline (Envelope Method)")
    print("=" * 60)
    print(f"True: G' = {G_prime} Pa, η = {eta} Pa·s")
    print(f"Noise: {noise_level*100:.0f}%")
    print("=" * 60)
    
    # Generate signals
    fs = 20000
    dt = 1 / fs
    duration = 0.12
    t = np.linspace(0, duration, int(fs * duration))
    
    distances = np.array([0.005, 0.015, 0.025, 0.040])
    freq_centers = np.arange(60, 141, 10)
    base_times = np.linspace(0.025, 0.105, len(freq_centers))
    
    np.random.seed(42)
    signals = []
    
    for d in distances:
        sig = np.zeros_like(t)
        for f_center, t_base in zip(freq_centers, base_times):
            omega = 2 * np.pi * f_center
            G_mag = np.sqrt(G_prime**2 + (omega * eta)**2)
            c_f = np.sqrt(2 / rho) * np.sqrt(G_mag**2 / (G_prime + G_mag))
            
            arrival = t_base + d / c_f
            burst_width = 0.005
            envelope = np.exp(-((t - arrival)**2) / (2 * (burst_width/3)**2))
            carrier = np.sin(omega * (t - arrival))
            sig += envelope * carrier
        
        sig = sig / (np.max(np.abs(sig)) + 1e-10)
        
        if noise_level > 0:
            sig += noise_level * np.std(sig) * np.random.randn(len(sig))
        
        signals.append(sig)
    
    # Extract
    print("\nExtracting dispersion...")
    dispersion = extract_dispersion_envelope(signals, dt, distances)
    
    if len(dispersion['velocities']) == 0:
        print("ERROR: No points extracted!")
        return None
    
    # Fit
    print("\nFitting Kelvin-Voigt...")
    fit = fit_kelvin_voigt(dispersion['freq_centers'], dispersion['velocities'],
                           dispersion['uncertainties'], rho)
    
    if fit['success']:
        print(f"  G' = {fit['G_prime']:.0f} ± {fit['G_prime_err']:.0f} Pa")
        print(f"  η = {fit['eta']:.3f} ± {fit['eta_err']:.3f} Pa·s")
        print(f"  R² = {fit['r_squared']:.4f}")
        
        G_err_pct = 100 * abs(fit['G_prime'] - G_prime) / G_prime
        eta_err_pct = 100 * abs(fit['eta'] - eta) / eta
        print(f"\n  Errors: G' = {G_err_pct:.1f}%, η = {eta_err_pct:.1f}%")
    
    # Plot
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 6))
    
    f_theory = np.linspace(50, 150, 200)
    omega_theory = 2 * np.pi * f_theory
    G_mag_theory = np.sqrt(G_prime**2 + (omega_theory * eta)**2)
    c_theory = np.sqrt(2 / rho) * np.sqrt(G_mag_theory**2 / (G_prime + G_mag_theory))
    
    ax.plot(f_theory, c_theory, 'g--', linewidth=2, label='True')
    
    if fit['success']:
        G_mag_fit = np.sqrt(fit['G_prime']**2 + (omega_theory * fit['eta'])**2)
        c_fit = np.sqrt(2 / rho) * np.sqrt(G_mag_fit**2 / (fit['G_prime'] + G_mag_fit))
        ax.plot(f_theory, c_fit, 'r-', linewidth=2, label='Fitted')
    
    ax.errorbar(dispersion['freq_centers'], dispersion['velocities'],
                yerr=dispersion['uncertainties'], fmt='bo', capsize=3, label='Measured')
    
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Phase Velocity (m/s)')
    ax.set_title('Shear Wave Dispersion - Envelope Method')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 8)
    
    plt.tight_layout()
    plt.savefig('dispersion_envelope.png', dpi=150)
    print("\nSaved: dispersion_envelope.png")
    
    return {'dispersion': dispersion, 'fit': fit}


if __name__ == '__main__':
    run_pipeline(G_prime=2000, eta=0.5, noise_level=0.15)
