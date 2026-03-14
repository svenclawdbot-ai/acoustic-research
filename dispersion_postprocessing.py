#!/usr/bin/env python3
"""
Dispersion Post-Processing Demo
================================

Demonstrates Savitzky-Golay smoothing + Bootstrap
on noisy dispersion curve data.

Input: Raw dispersion measurements c(ω) with uncertainties
Output: Smoothed curve + Kelvin-Voigt fit with confidence intervals

Author: Research Project
Date: March 14, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter


def kelvin_voigt(omega, G, eta, rho=1000):
    """Kelvin-Voigt dispersion."""
    Gm = np.sqrt(G**2 + (omega * eta)**2)
    return np.sqrt(2 / rho) * np.sqrt(Gm**2 / (G + Gm))


def savgol_smooth(x, y, dy, wl=5, po=3):
    """Savitzky-Golay smoothing."""
    if len(y) < wl:
        return y, dy
    wl = wl if wl % 2 else wl + 1
    wl = min(wl, len(y) - 1)
    if wl < po + 1:
        return y, dy
    ys = savgol_filter(y, wl, po)
    dys = savgol_filter(dy, wl + 2, 1) if dy is not None else dy
    if dys is not None:
        dys = np.maximum(dys, dy * 0.5)
    return ys, dys


def bootstrap_fit(freq, vel, unc, n=1000, rho=1000):
    """Bootstrap parameter estimation."""
    w = 2 * np.pi * freq
    try:
        p0, _ = curve_fit(lambda wv, G, e: kelvin_voigt(wv, G, e, rho), w, vel, 
                         sigma=unc, p0=[2000, 0.5], bounds=([100, 0.01], [50000, 50]))
    except:
        return None
    
    Gs, es = [], []
    for _ in range(n):
        idx = np.random.choice(len(freq), len(freq), True)
        vf = vel[idx] + np.random.randn(len(idx)) * (unc[idx] if unc is not None else 0.1)
        try:
            p, _ = curve_fit(lambda wv, G, e: kelvin_voigt(wv, G, e, rho), w[idx], vf,
                            p0=p0, bounds=([100, 0.01], [50000, 50]), maxfev=500)
            Gs.append(p[0])
            es.append(p[1])
        except:
            pass
    
    if not Gs:
        return None
    
    return {
        'G_median': np.median(Gs), 'G_ci': np.percentile(Gs, [2.5, 97.5]),
        'eta_median': np.median(es), 'eta_ci': np.percentile(es, [2.5, 97.5]),
        'G_std': np.std(Gs), 'eta_std': np.std(es),
        'G_samples': Gs, 'eta_samples': es
    }


def main():
    print("=" * 60)
    print("DISPERSION CURVE POST-PROCESSING")
    print("Savitzky-Golay + Bootstrap")
    print("=" * 60)
    
    # True parameters
    G_true, eta_true = 2000, 0.5
    print(f"\nTrue: G' = {G_true} Pa, η = {eta_true} Pa·s")
    
    # Generate synthetic dispersion data
    np.random.seed(42)
    freq = np.array([60, 70, 80, 90, 100, 110, 120, 130, 140])
    omega = 2 * np.pi * freq
    
    # True velocities
    v_true = kelvin_voigt(omega, G_true, eta_true)
    
    # Add measurement noise
    v_noisy = v_true * (1 + 0.05 * np.random.randn(len(freq)))  # 5% noise
    unc = 0.03 * v_noisy  # 3% uncertainty
    
    print(f"\nGenerated {len(freq)} frequency points")
    print(f"Noise level: 5%")
    
    # Stage 1: Savitzky-Golay smoothing
    print("\n1. Savitzky-Golay smoothing (window=5, order=3)...")
    v_smooth, unc_smooth = savgol_smooth(freq, v_noisy, unc, 5, 3)
    
    # Stage 2: Bootstrap fitting
    print("2. Bootstrap parameter estimation (n=1000)...")
    
    # Fit to raw data
    b_raw = bootstrap_fit(freq, v_noisy, unc)
    
    # Fit to smoothed data
    b_smooth = bootstrap_fit(freq, v_smooth, unc_smooth)
    
    # Results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Theory:  G' = {G_true:6.0f} Pa, η = {eta_true:.3f} Pa·s")
    
    if b_raw:
        G, e = b_raw['G_median'], b_raw['eta_median']
        print(f"Raw:     G' = {G:6.0f} ± {b_raw['G_std']:4.0f} Pa, "
              f"η = {e:.3f} ± {b_raw['eta_std']:.3f} Pa·s")
        print(f"         Error: G' = {100*abs(G-G_true)/G_true:.1f}%, "
              f"η = {100*abs(e-eta_true)/eta_true:.1f}%")
    
    if b_smooth:
        G, e = b_smooth['G_median'], b_smooth['eta_median']
        print(f"Smoothed: G' = {G:6.0f} ± {b_smooth['G_std']:4.0f} Pa, "
              f"η = {e:.3f} ± {b_smooth['eta_std']:.3f} Pa·s")
        print(f"          Error: G' = {100*abs(G-G_true)/G_true:.1f}%, "
              f"η = {100*abs(e-eta_true)/eta_true:.1f}%")
        
        if b_raw:
            print(f"\nUncertainty reduction:")
            print(f"  G': {(1 - b_smooth['G_std']/b_raw['G_std'])*100:.1f}% smaller")
            print(f"  η:  {(1 - b_smooth['eta_std']/b_raw['eta_std'])*100:.1f}% smaller")
    
    # Plot
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Dispersion curves
    ax = axes[0, 0]
    wf = np.linspace(omega.min(), omega.max(), 200)
    ff = wf / (2 * np.pi)
    
    ax.errorbar(freq, v_noisy, yerr=unc, fmt='bo', capsize=3, alpha=0.5, label='Raw')
    ax.errorbar(freq, v_smooth, yerr=unc_smooth, fmt='rs', capsize=3, alpha=0.7, label='Smoothed')
    ax.plot(ff, kelvin_voigt(wf, G_true, eta_true), 'g--', linewidth=2, label='True')
    
    if b_smooth:
        ax.plot(ff, kelvin_voigt(wf, b_smooth['G_median'], b_smooth['eta_median']), 
                'r-', linewidth=2, label='Fit')
    
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Velocity (m/s)')
    ax.set_title('Dispersion Curve')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # G' distributions
    if b_raw and b_smooth:
        ax = axes[0, 1]
        ax.hist(b_raw['G_samples'], 50, alpha=0.5, color='blue', label='Raw', edgecolor='k')
        ax.hist(b_smooth['G_samples'], 50, alpha=0.5, color='red', label='Smoothed', edgecolor='k')
        ax.axvline(G_true, color='green', linestyle='--', linewidth=2, label='True')
        ax.set_xlabel("G' (Pa)")
        ax.set_title("G' Bootstrap Distributions")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # η distributions
        ax = axes[1, 0]
        ax.hist(b_raw['eta_samples'], 50, alpha=0.5, color='blue', label='Raw', edgecolor='k')
        ax.hist(b_smooth['eta_samples'], 50, alpha=0.5, color='red', label='Smoothed', edgecolor='k')
        ax.axvline(eta_true, color='green', linestyle='--', linewidth=2, label='True')
        ax.set_xlabel('η (Pa·s)')
        ax.set_title('η Bootstrap Distributions')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Joint distribution
        ax = axes[1, 1]
        H, xe, ye = np.histogram2d(b_smooth['G_samples'], b_smooth['eta_samples'], 50)
        ax.imshow(H.T, origin='lower', extent=[xe[0], xe[-1], ye[0], ye[-1]], 
                 aspect='auto', cmap='Blues')
        ax.plot(G_true, eta_true, 'g*', markersize=15, markeredgecolor='w', label='True')
        ax.plot(b_smooth['G_median'], b_smooth['eta_median'], 'r+', markersize=12, mew=2, label='Fit')
        ax.set_xlabel("G' (Pa)")
        ax.set_ylabel('η (Pa·s)')
        ax.set_title('Joint Distribution (Smoothed)')
        ax.legend()
    
    plt.suptitle('Savitzky-Golay Smoothing + Bootstrap Confidence Intervals', 
                 fontweight='bold')
    plt.tight_layout()
    plt.savefig('savgol_bootstrap.png', dpi=150)
    print("\nSaved: savgol_bootstrap.png")


if __name__ == "__main__":
    main()
    print("\nDone!")
