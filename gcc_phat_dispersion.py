#!/usr/bin/env python3
"""
GCC-PHAT Integration for Shear Wave Dispersion Pipeline
=========================================================

Integrates sub-sample GCC-PHAT time delay estimation into the 
shear wave dispersion extraction pipeline.

Key improvements:
- Sub-sample precision delay estimation (< 0.1 sample error)
- PHAT whitening for sharper correlation peaks
- Band-limited PHAT for frequency-selective analysis
- Two-stage approach: envelope coarse + GCC-PHAT fine (resolves phase ambiguity)

Author: Research Project
Date: April 16, 2026
"""

import numpy as np
from scipy import signal
from scipy.signal import hilbert, butter, filtfilt
from typing import Optional, Tuple, List, Dict
import sys
import os

# Import existing GCC-PHAT implementation
sys.path.insert(0, os.path.dirname(__file__))
from subsample_gcc import gcc_phat, gcc_standard, parabolic_interp

# Import wavelet denoising
from wavelet_denoising import WaveletDenoiser


def extract_delay_two_stage(sig1: np.ndarray, 
                            sig2: np.ndarray, 
                            dt: float,
                            freq_center: float,
                            fs: Optional[float] = None,
                            denoise: bool = True,
                            use_phat: bool = True) -> Dict:
    """
    Extract time delay using two-stage approach:
    1. Envelope-based coarse delay (resolves phase ambiguity)
    2. GCC-PHAT for fine sub-sample refinement
    
    Parameters:
    -----------
    sig1, sig2 : array
        Input signals
    dt : float
        Time step (seconds)
    freq_center : float
        Center frequency of the signals (Hz) - needed for phase unwrapping
    fs : float, optional
        Sample rate in Hz
    denoise : bool
        Apply wavelet denoising
    use_phat : bool
        Use PHAT whitening
        
    Returns:
    --------
    dict with delay, correlation, method
    """
    if fs is None:
        fs = 1.0 / dt
    
    sig1 = np.asarray(sig1).flatten()
    sig2 = np.asarray(sig2).flatten()
    
    # Ensure equal length
    min_len = min(len(sig1), len(sig2))
    sig1 = sig1[:min_len]
    sig2 = sig2[:min_len]
    
    # Optional denoising
    if denoise:
        denoiser = WaveletDenoiser('sym6', level=5, threshold_factor=2.0, mode='soft')
        sig1 = denoiser.denoise(sig1)
        sig2 = denoiser.denoise(sig2)
    
    # Stage 1: Envelope-based coarse delay
    env1 = np.abs(hilbert(sig1))
    env2 = np.abs(hilbert(sig2))
    
    # Find peaks in reasonable time window
    t_ms = np.arange(len(sig1)) * dt * 1000
    search_mask = (t_ms >= 30) & (t_ms <= 110)
    
    if np.any(search_mask):
        idx = np.where(search_mask)[0]
        peak1_idx = idx[np.argmax(env1[search_mask])]
        peak2_idx = idx[np.argmax(env2[search_mask])]
        coarse_delay = (peak2_idx - peak1_idx) * dt
    else:
        coarse_delay = 0
    
    # Stage 2: GCC-PHAT for fine delay
    if use_phat:
        delay_fine, corr = gcc_phat(sig1, sig2, fs, freq_range=(freq_center-10, freq_center+10))
        method = 'gcc_phat_two_stage'
    else:
        delay_fine, corr = gcc_standard(sig1, sig2, fs)
        method = 'gcc_standard_two_stage'
    
    # Resolve phase ambiguity using coarse estimate
    # The period at freq_center
    period = 1.0 / freq_center
    
    # Adjust fine delay to be within ± period/2 of coarse estimate
    delay_diff = delay_fine - coarse_delay
    n_periods = round(delay_diff / period)
    delay = delay_fine - n_periods * period
    
    # If the result is way off from coarse, fall back to coarse
    if abs(delay - coarse_delay) > period:
        delay = coarse_delay
        method += '_coarse_fallback'
    
    return {
        'delay': delay,
        'coarse_delay': coarse_delay,
        'fine_delay': delay_fine,
        'delay_samples': delay * fs,
        'correlation': corr,
        'method': method,
        'period': period,
        'n_periods_corrected': n_periods
    }


def extract_dispersion_gcc_phat(signals: List[np.ndarray],
                                 dt: float,
                                 distances: np.ndarray,
                                 freq_bands: Optional[List[Tuple[float, float]]] = None,
                                 denoise: bool = True,
                                 use_phat: bool = True) -> Dict:
    """
    Extract dispersion curve using two-stage GCC-PHAT.
    """
    n_receivers = len(signals)
    fs = 1.0 / dt
    
    if freq_bands is None:
        freq_centers = np.arange(60, 141, 10)
        freq_bands = [(f-10, f+10) for f in freq_centers]
    else:
        freq_centers = [(b[0] + b[1]) / 2 for b in freq_bands]
    
    results = {
        'freq_centers': [],
        'velocities': [],
        'uncertainties': [],
        'correlations': [],
    }
    
    print(f"Extracting dispersion with two-stage GCC-PHAT ({n_receivers} receivers)")
    
    for band_idx, ((f_min, f_max), f_center) in enumerate(zip(freq_bands, freq_centers)):
        pair_velocities = []
        pair_weights = []
        
        for i in range(n_receivers - 1):
            for j in range(i + 1, n_receivers):
                distance = distances[j] - distances[i]
                
                # Light filtering
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
                
                # Two-stage delay estimation
                delay_result = extract_delay_two_stage(
                    s1_f, s2_f, dt, f_center,
                    denoise=denoise, use_phat=use_phat
                )
                
                delay = delay_result['delay']
                corr = delay_result['correlation']
                
                if delay <= 1e-9:
                    continue
                
                velocity = distance / delay
                
                # Reasonable velocity check for shear waves
                if 0.5 <= velocity <= 20:
                    pair_velocities.append(velocity)
                    # Weight by correlation and distance
                    pair_weights.append(abs(corr) * distance)
        
        if pair_velocities:
            weights = np.array(pair_weights)
            weights = weights / np.sum(weights)
            
            mean_velocity = np.average(pair_velocities, weights=weights)
            uncertainty = np.sqrt(np.average(
                (np.array(pair_velocities) - mean_velocity)**2,
                weights=weights
            )) if len(pair_velocities) > 1 else 0.1 * mean_velocity
            
            results['freq_centers'].append(f_center)
            results['velocities'].append(mean_velocity)
            results['uncertainties'].append(uncertainty)
            results['correlations'].append(np.mean(np.abs(pair_weights)))
            
            print(f"  {f_center:.0f} Hz: c = {mean_velocity:.2f} ± {uncertainty:.2f} m/s")
    
    results['freq_centers'] = np.array(results['freq_centers'])
    results['velocities'] = np.array(results['velocities'])
    results['uncertainties'] = np.array(results['uncertainties'])
    
    return results


def fit_kelvin_voigt(freq: np.ndarray,
                     velocity: np.ndarray,
                     uncertainty: Optional[np.ndarray] = None,
                     rho: float = 1000) -> Dict:
    """Fit Kelvin-Voigt model to dispersion curve."""
    from scipy.optimize import curve_fit
    
    def kv_model(omega, G_prime, eta):
        G_mag = np.sqrt(G_prime**2 + (omega * eta)**2)
        c = np.sqrt(2 / rho) * np.sqrt(G_mag**2 / (G_prime + G_mag))
        return c
    
    omega = 2 * np.pi * freq
    
    c0 = np.mean(velocity) if len(velocity) > 0 else 1.5
    G0 = max(100, min(rho * c0**2, 50000))
    eta0 = 0.5
    
    if uncertainty is not None and np.all(uncertainty > 0):
        sigma = uncertainty
    else:
        sigma = None
    
    try:
        popt, pcov = curve_fit(kv_model, omega, velocity,
                              p0=[G0, eta0],
                              bounds=([10, 0.001], [100000, 100]),
                              sigma=sigma,
                              maxfev=5000)
        
        G_prime, eta = popt
        G_err, eta_err = np.sqrt(np.diag(pcov))
        
        residuals = velocity - kv_model(omega, *popt)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((velocity - np.mean(velocity))**2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        return {
            'G_prime': G_prime,
            'eta': eta,
            'G_prime_err': G_err,
            'eta_err': eta_err,
            'r_squared': r_squared,
            'success': True
        }
    except Exception as e:
        return {
            'G_prime': G0,
            'eta': eta0,
            'G_prime_err': np.nan,
            'eta_err': np.nan,
            'r_squared': 0,
            'success': False,
            'error': str(e)
        }


def run_gcc_phat_pipeline(G_prime: float = 2000,
                          eta: float = 0.5,
                          rho: float = 1000,
                          noise_level: float = 0.15,
                          n_receivers: int = 4) -> Dict:
    """Run complete two-stage GCC-PHAT dispersion pipeline."""
    print("=" * 70)
    print("Two-Stage GCC-PHAT Dispersion Pipeline")
    print("=" * 70)
    print(f"True parameters: G' = {G_prime} Pa, η = {eta} Pa·s, ρ = {rho} kg/m³")
    print(f"Noise level: {noise_level*100:.0f}%")
    print("=" * 70)
    
    # Generate test signals
    fs = 20000
    dt = 1 / fs
    duration = 0.12
    t = np.linspace(0, duration, int(fs * duration))
    
    distances = np.array([0.005, 0.015, 0.025, 0.040])
    
    # Generate tone bursts at frequencies matching extraction bands
    freq_centers = np.arange(60, 141, 10)
    base_times = np.linspace(0.025, 0.105, len(freq_centers))
    
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
        
        # Add noise
        if noise_level > 0:
            noise_amp = noise_level * np.std(sig)
            sig = sig + noise_amp * np.random.randn(len(sig))
        
        signals.append(sig)
    
    # Extract dispersion
    print("\n1. Extracting dispersion with two-stage GCC-PHAT...")
    dispersion = extract_dispersion_gcc_phat(
        signals, dt, distances,
        denoise=True, use_phat=True
    )
    
    if len(dispersion['velocities']) == 0:
        print("ERROR: No dispersion points extracted!")
        return None
    
    print(f"\n   Extracted {len(dispersion['velocities'])} frequency points")
    
    # Fit model
    print("\n2. Fitting Kelvin-Voigt model...")
    fit = fit_kelvin_voigt(
        dispersion['freq_centers'],
        dispersion['velocities'],
        dispersion['uncertainties'],
        rho=rho
    )
    
    if fit['success']:
        print(f"   Fitted: G' = {fit['G_prime']:.0f} ± {fit['G_prime_err']:.0f} Pa")
        print(f"           η = {fit['eta']:.3f} ± {fit['eta_err']:.3f} Pa·s")
        print(f"   R² = {fit['r_squared']:.4f}")
        
        G_error_pct = 100 * abs(fit['G_prime'] - G_prime) / G_prime
        eta_error_pct = 100 * abs(fit['eta'] - eta) / eta if eta > 0 else 0
        print(f"\n   Errors: G' = {G_error_pct:.1f}%, η = {eta_error_pct:.1f}%")
    
    # Create plots
    create_gcc_phat_plots(dispersion, fit, G_prime, eta, rho)
    
    return {
        'dispersion': dispersion,
        'fit': fit,
        'true_G_prime': G_prime,
        'true_eta': eta,
        'rho': rho,
        'signals': signals,
        'distances': distances,
        'dt': dt
    }


def create_gcc_phat_plots(dispersion: Dict, fit: Dict, true_G_prime: float,
                          true_eta: float, rho: float,
                          filename: str = 'gcc_phat_pipeline.png'):
    """Create visualization."""
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Plot 1: Dispersion curve
    ax = axes[0, 0]
    
    f_theory = np.linspace(50, 150, 200)
    omega_theory = 2 * np.pi * f_theory
    G_mag_theory = np.sqrt(true_G_prime**2 + (omega_theory * true_eta)**2)
    c_theory = np.sqrt(2 / rho) * np.sqrt(G_mag_theory**2 / (true_G_prime + G_mag_theory))
    
    ax.plot(f_theory, c_theory, 'g--', linewidth=2, label='True')
    
    if fit['success']:
        G_mag_fit = np.sqrt(fit['G_prime']**2 + (omega_theory * fit['eta'])**2)
        c_fit = np.sqrt(2 / rho) * np.sqrt(G_mag_fit**2 / (fit['G_prime'] + G_mag_fit))
        ax.plot(f_theory, c_fit, 'r-', linewidth=2, label='Fitted')
    
    ax.errorbar(dispersion['freq_centers'], dispersion['velocities'],
                yerr=dispersion['uncertainties'],
                fmt='bo', capsize=3, markersize=6, alpha=0.7, label='Measured')
    
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Phase Velocity (m/s)')
    ax.set_title('Dispersion Curve: Two-Stage GCC-PHAT')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 10)
    
    # Plot 2: Residuals
    ax = axes[0, 1]
    if fit['success']:
        omega = 2 * np.pi * dispersion['freq_centers']
        G_mag_fit = np.sqrt(fit['G_prime']**2 + (omega * fit['eta'])**2)
        c_fit = np.sqrt(2 / rho) * np.sqrt(G_mag_fit**2 / (fit['G_prime'] + G_mag_fit))
        residuals = dispersion['velocities'] - c_fit
        
        ax.bar(dispersion['freq_centers'], residuals, width=8, alpha=0.6)
        ax.axhline(0, color='r', linestyle='-')
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Residual (m/s)')
        ax.set_title('Fit Residuals')
        ax.grid(True, alpha=0.3)
    
    # Plot 3: Parameters
    ax = axes[1, 0]
    if fit['success']:
        ax.text(0.1, 0.8, f"G' (true): {true_G_prime:.0f} Pa", fontsize=12, transform=ax.transAxes)
        ax.text(0.1, 0.7, f"G' (fitted): {fit['G_prime']:.0f} ± {fit['G_prime_err']:.0f} Pa", 
                fontsize=12, transform=ax.transAxes, color='red')
        ax.text(0.1, 0.5, f"η (true): {true_eta:.3f} Pa·s", fontsize=12, transform=ax.transAxes)
        ax.text(0.1, 0.4, f"η (fitted): {fit['eta']:.3f} ± {fit['eta_err']:.3f} Pa·s",
                fontsize=12, transform=ax.transAxes, color='red')
        ax.text(0.1, 0.2, f"R² = {fit['r_squared']:.4f}", fontsize=12, transform=ax.transAxes)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title('Fitted Parameters')
    
    # Plot 4: Uncertainty
    ax = axes[1, 1]
    ax.errorbar(dispersion['freq_centers'], dispersion['velocities'],
                yerr=dispersion['uncertainties'],
                fmt='none', ecolor='red', alpha=0.5, capsize=3)
    ax.scatter(dispersion['freq_centers'], dispersion['velocities'], c='blue', s=50)
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Phase Velocity (m/s)')
    ax.set_title('Uncertainty Visualization')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 10)
    
    plt.suptitle('Two-Stage GCC-PHAT Shear Wave Dispersion', fontweight='bold', fontsize=14)
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"\nSaved: {filename}")
    
    return fig


if __name__ == '__main__':
    np.random.seed(42)
    results = run_gcc_phat_pipeline(
        G_prime=2000,
        eta=0.5,
        rho=1000,
        noise_level=0.15
    )
    
    print("\n" + "=" * 70)
    print("Two-Stage GCC-PHAT Pipeline Complete!")
    print("=" * 70)
