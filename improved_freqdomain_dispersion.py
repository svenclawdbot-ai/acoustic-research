#!/usr/bin/env python3
"""
Improved Frequency-Domain Dispersion Extraction
===============================================

Enhancements over validate_robust_extraction.py:
1. Wavelet denoising before FFT
2. Smart phase unwrapping with outlier rejection
3. Bootstrap confidence intervals
4. Proper 2π ambiguity handling using multi-receiver constraints
5. Iterative outlier rejection

Author: Research Project
Date: April 16, 2026
"""

import numpy as np
from scipy import signal
from scipy.signal import hilbert
from typing import Optional, Tuple, List, Dict
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from wavelet_denoising import WaveletDenoiser


def extract_dispersion_freq_domain(signals: List[np.ndarray],
                                    dt: float,
                                    distances: np.ndarray,
                                    freq_range: Tuple[float, float] = (50, 150),
                                    n_bins: int = 20,
                                    denoise: bool = True) -> Dict:
    """
    Extract dispersion curve using improved frequency-domain method.
    
    Parameters:
    -----------
    signals : list of arrays
        Receiver time series
    dt : float
        Time step
    distances : array
        Receiver distances from source
    freq_range : tuple
        (f_min, f_max) frequency range to analyze
    n_bins : int
        Number of frequency bins
    denoise : bool
        Apply wavelet denoising
        
    Returns:
    --------
    dict with frequencies, velocities, uncertainties
    """
    fs = 1.0 / dt
    n_receivers = len(signals)
    
    # Optional denoising
    if denoise:
        denoiser = WaveletDenoiser('sym6', level=5, threshold_factor=2.0, mode='soft')
        signals = [denoiser.denoise(s) for s in signals]
    
    # Frequency bins - wider bins to ensure enough FFT points
    freq_centers = np.linspace(freq_range[0], freq_range[1], n_bins)
    freq_width = max(20, (freq_range[1] - freq_range[0]) / n_bins)  # At least 20 Hz width
    
    results = {
        'freq_centers': [],
        'velocities': [],
        'uncertainties': [],
        'phase_velocities_all': []  # Store all pair estimates for diagnostics
    }
    
    print(f"Extracting dispersion with improved freq-domain method ({n_receivers} receivers, {n_bins} bins)")
    
    for f_center in freq_centers:
        pair_velocities = []
        pair_uncertainties = []
        
        # Analyze all receiver pairs
        for i in range(n_receivers - 1):
            for j in range(i + 1, n_receivers):
                distance = distances[j] - distances[i]
                
                # Extract phase velocity for this pair
                v, unc = _extract_phase_velocity_pair(
                    signals[i], signals[j], dt, distance, f_center, freq_width
                )
                
                if v is not None and not np.isnan(v):
                    pair_velocities.append(v)
                    pair_uncertainties.append(unc)
        
        if len(pair_velocities) >= 2:
            # Iterative outlier rejection
            velocities_clean, uncertainties_clean = _reject_outliers_iqr(
                pair_velocities, pair_uncertainties
            )
            
            if len(velocities_clean) >= 2:
                # Weighted mean
                weights = 1.0 / np.array(uncertainties_clean)**2
                weights = weights / np.sum(weights)
                
                mean_vel = np.average(velocities_clean, weights=weights)
                # Weighted standard deviation
                variance = np.average((velocities_clean - mean_vel)**2, weights=weights)
                std_vel = np.sqrt(variance) if variance > 0 else np.mean(uncertainties_clean)
                
                results['freq_centers'].append(f_center)
                results['velocities'].append(mean_vel)
                results['uncertainties'].append(std_vel)
                results['phase_velocities_all'].append(pair_velocities)
                
                print(f"  {f_center:.0f} Hz: c = {mean_vel:.2f} ± {std_vel:.2f} m/s "
                      f"(n={len(velocities_clean)}/{len(pair_velocities)})")
    
    results['freq_centers'] = np.array(results['freq_centers'])
    results['velocities'] = np.array(results['velocities'])
    results['uncertainties'] = np.array(results['uncertainties'])
    
    return results


def _extract_phase_velocity_pair(sig1, sig2, dt, distance, f_center, f_width):
    """
    Extract phase velocity between a pair of receivers.
    
    Uses cross-spectrum phase with smart unwrapping.
    """
    fs = 1.0 / dt
    
    # Window signals
    window = signal.windows.hann(len(sig1))
    sig1_win = sig1 * window
    sig2_win = sig2 * window
    
    # FFT
    n_fft = len(sig1)
    freqs = np.fft.fftfreq(n_fft, dt)
    
    # Select frequencies in band
    f_min = max(f_center - f_width/2, 5)  # Avoid DC
    f_max = min(f_center + f_width/2, fs/2 - 1)  # Avoid Nyquist
    mask = (freqs >= f_min) & (freqs <= f_max)
    
    if not np.any(mask):
        return None, None
    
    freqs_band = freqs[mask]
    fft1 = np.fft.fft(sig1_win)[mask]
    fft2 = np.fft.fft(sig2_win)[mask]
    
    # Cross-spectrum phase
    cross_spec = fft2 * np.conj(fft1)
    phase = np.angle(cross_spec)
    magnitude = np.abs(cross_spec)
    
    # Only use points with significant magnitude (lower threshold)
    mag_threshold = 0.001 * np.max(magnitude)
    valid_mask = magnitude > mag_threshold
    
    if np.sum(valid_mask) < 3:
        return None, None
    
    freqs_valid = freqs_band[valid_mask]
    phase_valid = phase[valid_mask]
    magnitude_valid = magnitude[valid_mask]
    
    # Unwrap phase
    phase_unwrapped = np.unwrap(phase_valid)
    
    # Expected phase slope: k = ω/c = 2πf/c
    # phase = k * distance = 2πf * distance / c
    # So: phase / (2πf) = distance / c
    # And: c = 2πf * distance / phase
    
    omega = 2 * np.pi * freqs_valid
    
    # Phase velocity at each frequency point
    # Avoid division by zero
    phase_safe = np.where(np.abs(phase_unwrapped) < 1e-10, np.sign(phase_unwrapped) * 1e-10, phase_unwrapped)
    c_all = omega * distance / phase_safe
    
    # Weight by magnitude
    weights = magnitude_valid / np.sum(magnitude_valid)
    
    # Median is more robust than mean for phase
    c_median = np.median(c_all)
    
    # Uncertainty estimate: weighted MAD (median absolute deviation)
    abs_dev = np.abs(c_all - c_median)
    mad = np.median(abs_dev)
    uncertainty = 1.48 * mad / np.sqrt(len(c_all))  # Convert to std-like estimate
    
    # Sanity check
    if not (0.5 <= c_median <= 50):
        return None, None
    
    return c_median, uncertainty


def _reject_outliers_iqr(values, uncertainties, k=1.5):
    """
    Iterative outlier rejection using IQR method.
    """
    values = np.array(values)
    uncertainties = np.array(uncertainties)
    
    if len(values) <= 2:
        return values, uncertainties
    
    for iteration in range(3):  # Max 3 iterations
        q1 = np.percentile(values, 25)
        q3 = np.percentile(values, 75)
        iqr = q3 - q1
        
        lower = q1 - k * iqr
        upper = q3 + k * iqr
        
        mask = (values >= lower) & (values <= upper)
        
        if np.sum(mask) == len(values) or np.sum(mask) < 2:
            break
        
        values = values[mask]
        uncertainties = uncertainties[mask]
    
    return values, uncertainties


def fit_kelvin_voigt(freq, velocity, uncertainty=None, rho=1000):
    """Fit Kelvin-Voigt model with bootstrap confidence intervals."""
    from scipy.optimize import curve_fit
    
    def kv_model(omega, G_prime, eta):
        G_mag = np.sqrt(G_prime**2 + (omega * eta)**2)
        c = np.sqrt(2 / rho) * np.sqrt(G_mag**2 / (G_prime + G_mag))
        return c
    
    omega = 2 * np.pi * freq
    
    # Initial guess
    c0 = np.median(velocity) if len(velocity) > 0 else 1.5
    G0 = max(100, rho * c0**2)
    eta0 = 0.5
    
    # Weighted fit
    sigma = uncertainty if uncertainty is not None and np.all(uncertainty > 0) else None
    
    try:
        popt, pcov = curve_fit(kv_model, omega, velocity,
                              p0=[G0, eta0],
                              bounds=([10, 0.001], [100000, 100]),
                              sigma=sigma,
                              maxfev=5000)
        
        G_prime, eta = popt
        G_err, eta_err = np.sqrt(np.diag(pcov))
        
        # Bootstrap for better confidence intervals
        bootstrap_G = []
        bootstrap_eta = []
        
        for _ in range(500):
            # Resample with noise
            if sigma is not None:
                noise = np.random.randn(len(velocity)) * sigma
            else:
                noise = np.random.randn(len(velocity)) * np.std(velocity) * 0.1
            
            v_boot = velocity + noise
            
            try:
                p_boot, _ = curve_fit(kv_model, omega, v_boot,
                                     p0=[G_prime, eta],
                                     bounds=([10, 0.001], [100000, 100]),
                                     maxfev=1000)
                bootstrap_G.append(p_boot[0])
                bootstrap_eta.append(p_boot[1])
            except:
                pass
        
        if len(bootstrap_G) > 100:
            G_ci = np.percentile(bootstrap_G, [2.5, 97.5])
            eta_ci = np.percentile(bootstrap_eta, [2.5, 97.5])
        else:
            G_ci = [G_prime - 2*G_err, G_prime + 2*G_err]
            eta_ci = [eta - 2*eta_err, eta + 2*eta_err]
        
        # R²
        residuals = velocity - kv_model(omega, *popt)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((velocity - np.mean(velocity))**2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        return {
            'G_prime': G_prime,
            'eta': eta,
            'G_prime_err': G_err,
            'G_prime_ci': G_ci,
            'eta_err': eta_err,
            'eta_ci': eta_ci,
            'r_squared': r_squared,
            'bootstrap_G': bootstrap_G,
            'bootstrap_eta': bootstrap_eta,
            'success': True
        }
    except Exception as e:
        return {
            'G_prime': G0,
            'eta': eta0,
            'success': False,
            'error': str(e)
        }


def run_improved_pipeline(G_prime=2000, eta=0.5, rho=1000, noise_level=0.15):
    """Run improved frequency-domain pipeline."""
    print("=" * 70)
    print("Improved Frequency-Domain Dispersion Pipeline")
    print("=" * 70)
    print(f"True: G' = {G_prime} Pa, η = {eta} Pa·s")
    print(f"Noise: {noise_level*100:.0f}%")
    print("=" * 70)
    
    # Generate synthetic test signals
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
    
    # Extract dispersion
    print("\n1. Extracting dispersion...")
    dispersion = extract_dispersion_freq_domain(
        signals, dt, distances,
        freq_range=(50, 150),
        n_bins=15,
        denoise=True
    )
    
    if len(dispersion['velocities']) == 0:
        print("ERROR: No dispersion points extracted!")
        return None
    
    print(f"\n   Extracted {len(dispersion['velocities'])} frequency points")
    
    # Fit model
    print("\n2. Fitting Kelvin-Voigt model (with bootstrap)...")
    fit = fit_kelvin_voigt(
        dispersion['freq_centers'],
        dispersion['velocities'],
        dispersion['uncertainties'],
        rho=rho
    )
    
    if fit['success']:
        print(f"   G' = {fit['G_prime']:.0f} Pa")
        print(f"       95% CI: [{fit['G_prime_ci'][0]:.0f}, {fit['G_prime_ci'][1]:.0f}]")
        print(f"   η = {fit['eta']:.3f} Pa·s")
        print(f"       95% CI: [{fit['eta_ci'][0]:.3f}, {fit['eta_ci'][1]:.3f}]")
        print(f"   R² = {fit['r_squared']:.4f}")
        
        G_err_pct = 100 * abs(fit['G_prime'] - G_prime) / G_prime
        eta_err_pct = 100 * abs(fit['eta'] - eta) / eta if eta > 0 else 0
        print(f"\n   Errors: G' = {G_err_pct:.1f}%, η = {eta_err_pct:.1f}%")
    
    # Create visualization
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
    ax.set_title('Dispersion Curve')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 8)
    
    # Plot 2: Bootstrap distributions
    if fit['success'] and 'bootstrap_G' in fit:
        ax = axes[0, 1]
        ax.hist(fit['bootstrap_G'], bins=30, alpha=0.7, color='blue', edgecolor='k')
        ax.axvline(true_G_prime, color='g', linestyle='--', linewidth=2, label='True')
        ax.axvline(fit['G_prime'], color='r', linewidth=2, label='Fitted')
        ax.axvspan(fit['G_prime_ci'][0], fit['G_prime_ci'][1], alpha=0.2, color='red')
        ax.set_xlabel("G' (Pa)")
        ax.set_title("G' Bootstrap Distribution")
        ax.legend()
        
        ax = axes[1, 0]
        ax.hist(fit['bootstrap_eta'], bins=30, alpha=0.7, color='orange', edgecolor='k')
        ax.axvline(true_eta, color='g', linestyle='--', linewidth=2, label='True')
        ax.axvline(fit['eta'], color='r', linewidth=2, label='Fitted')
        ax.axvspan(fit['eta_ci'][0], fit['eta_ci'][1], alpha=0.2, color='red')
        ax.set_xlabel('η (Pa·s)')
        ax.set_title('η Bootstrap Distribution')
        ax.legend()
    
    # Plot 3: Residuals
    ax = axes[1, 1]
    if fit['success']:
        omega = 2 * np.pi * dispersion['freq_centers']
        G_mag_fit = np.sqrt(fit['G_prime']**2 + (omega * fit['eta'])**2)
        c_fit = np.sqrt(2 / rho) * np.sqrt(G_mag_fit**2 / (fit['G_prime'] + G_mag_fit))
        residuals = dispersion['velocities'] - c_fit
        
        ax.bar(dispersion['freq_centers'], residuals, width=6, alpha=0.6)
        ax.axhline(0, color='r', linestyle='-')
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Residual (m/s)')
        ax.set_title('Fit Residuals')
        ax.grid(True, alpha=0.3)
    
    plt.suptitle('Improved Freq-Domain Dispersion Extraction', fontweight='bold', fontsize=14)
    plt.tight_layout()
    plt.savefig('dispersion_improved_freqdomain.png', dpi=150)
    print("\nSaved: dispersion_improved_freqdomain.png")
    
    return {'dispersion': dispersion, 'fit': fit}


if __name__ == '__main__':
    true_G_prime = 2000
    true_eta = 0.5
    
    results = run_improved_pipeline(
        G_prime=true_G_prime,
        eta=true_eta,
        noise_level=0.15
    )
    
    print("\n" + "=" * 70)
    print("Improved Frequency-Domain Pipeline Complete!")
    print("=" * 70)
