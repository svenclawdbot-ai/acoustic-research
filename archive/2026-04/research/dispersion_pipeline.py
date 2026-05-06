#!/usr/bin/env python3
"""
Complete Dispersion Pipeline
============================

Integrated processing:
1. Wavelet denoising (temporal)
2. Dispersion extraction
3. Savitzky-Golay smoothing
4. Bootstrap confidence intervals

Author: Research Project
Date: March 14, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter, hilbert, butter, filtfilt
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'research', 'week2'))

from wavelet_denoising import WaveletDenoiser

try:
    from shear_wave_2d_simple import ShearWave2D
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


def kelvin_voigt_dispersion(omega, G_prime, eta, rho=1000):
    """Kelvin-Voigt dispersion."""
    G_mag = np.sqrt(G_prime**2 + (omega * eta)**2)
    c = np.sqrt(2 / rho) * np.sqrt(G_mag**2 / (G_prime + G_mag))
    return c


def extract_dispersion_curve(signals, dt, distances, denoise=True):
    """Extract c(ω) from multi-receiver data."""
    freq_centers = np.arange(60, 141, 10)  # 60-140 Hz in 10 Hz steps
    n_receivers = len(signals)
    
    freqs, vels, uncs = [], [], []
    
    print(f"   Processing {len(freq_centers)} frequency bands...")
    
    for f_center in freq_centers:
        pair_vels, pair_dists = [], []
        
        for i in range(n_receivers - 1):
            for j in range(i + 1, n_receivers):
                s1, s2 = signals[i].copy(), signals[j].copy()
                dist = distances[j] - distances[i]
                
                # Wavelet denoising
                if denoise:
                    denoiser = WaveletDenoiser('sym6', 5, 2.0, 'soft')
                    s1 = denoiser.denoise(s1)
                    s2 = denoiser.denoise(s2)
                
                # Bandpass filter
                nyq = 1.0 / (2 * dt)
                low, high = (f_center-10)/nyq, (f_center+10)/nyq
                low, high = max(0.01, low), min(0.99, high)
                if low >= high: 
                    continue
                
                try:
                    b, a = butter(4, [low, high], btype='band')
                    s1f = filtfilt(b, a, s1)
                    s2f = filtfilt(b, a, s2)
                except:
                    continue
                
                # Peak detection
                e1 = np.abs(hilbert(s1f))
                e2 = np.abs(hilbert(s2f))
                t = np.arange(len(e1)) * dt * 1000
                mask = (t >= 45) & (t <= 80)
                
                if not np.any(mask): 
                    continue
                
                idx = np.where(mask)[0]
                if len(idx) == 0:
                    continue
                    
                p1 = idx[np.argmax(e1[mask])]
                p2 = idx[np.argmax(e2[mask])]
                
                delay = (p2 - p1) * dt
                if delay > 1e-9:  # Valid delay
                    pair_vels.append(dist / delay)
                    pair_dists.append(dist)
        
        if pair_vels:
            w = np.array(pair_dists) / sum(pair_dists)
            v = np.average(pair_vels, weights=w)
            freqs.append(f_center)
            vels.append(v)
            uncs.append(np.std(pair_vels))
            print(f"     {f_center} Hz: c = {v:.2f} m/s")
    
    return np.array(freqs), np.array(vels), np.array(uncs)


def savgol_smooth(f, v, u, wl=5, po=3):
    """Savitzky-Golay smooth with uncertainty propagation."""
    if len(v) < wl:
        return v, u
    wl = wl if wl % 2 else wl + 1
    wl = min(wl, len(v) - 1)
    if wl % 2 == 0: wl -= 1
    if wl < po + 1:
        return v, u
    
    vs = savgol_filter(v, wl, po)
    us = savgol_filter(u, wl + 2, 1) if u is not None else u
    if us is not None:
        us = np.maximum(us, u * 0.5)
    return vs, us


def bootstrap_fit(freq, vel, unc, n=1000, rho=1000):
    """Bootstrap fit with confidence intervals."""
    w = 2 * np.pi * freq
    
    try:
        p0, _ = curve_fit(lambda wv, G, e: kelvin_voigt_dispersion(wv, G, e, rho),
                         w, vel, sigma=unc, p0=[2000, 0.5], bounds=([100, 0.01], [50000, 50]))
    except:
        return None
    
    Gs, es = [], []
    for _ in range(n):
        idx = np.random.choice(len(freq), len(freq), True)
        vf = vel[idx] + (np.random.randn(len(idx)) * unc[idx] if unc is not None else 0)
        try:
            p, _ = curve_fit(lambda wv, G, e: kelvin_voigt_dispersion(wv, G, e, rho),
                            w[idx], vf, p0=p0, bounds=([100, 0.01], [50000, 50]), maxfev=500)
            Gs.append(p[0])
            es.append(p[1])
        except:
            pass
    
    if not Gs:
        return None
    
    return {
        'G_median': np.median(Gs), 'G_ci': np.percentile(Gs, [2.5, 97.5]),
        'eta_median': np.median(es), 'eta_ci': np.percentile(es, [2.5, 97.5]),
        'G_samples': Gs, 'eta_samples': es
    }


def run_pipeline(Gt=2000, et=0.5, noise=0.15):
    """Run complete pipeline with synthetic data."""
    print("=" * 60)
    print("COMPLETE DISPERSION PIPELINE")
    print("Wavelet → Savgol → Bootstrap")
    print("=" * 60)
    print(f"True: G'={Gt} Pa, η={et} Pa·s, noise={noise*100:.0f}%")
    print("=" * 60)
    
    # Generate synthetic shear wave signals
    fs = 20000  # 20 kHz sampling
    dt = 1/fs
    duration = 0.1  # 100 ms
    t = np.linspace(0, duration, int(fs * duration))
    
    dists = np.array([0.005, 0.010, 0.015])  # 5, 10, 15 mm
    
    # Theoretical velocity
    c_s = np.sqrt(Gt / 1000)
    print(f"\nShear velocity: {c_s:.2f} m/s")
    
    # Generate dispersive chirp signals
    # Use a swept-sine (chirp) with dispersion - higher frequencies arrive later
    sigs = []
    
    for d in dists:
        # Create chirp that models dispersive propagation
        # Start with low freq, sweep to high, with delay based on dispersion
        sig = np.zeros_like(t)
        
        # For each frequency component, add it with appropriate delay
        for f in np.linspace(50, 150, 50):
            omega = 2 * np.pi * f
            G_mag = np.sqrt(Gt**2 + (omega * et)**2)
            c_f = np.sqrt(2 / 1000) * np.sqrt(G_mag**2 / (Gt + G_mag))
            
            # Delay = 50ms base + propagation time
            delay_s = 0.050 + d / c_f
            
            # Add this frequency component
            envelope = np.exp(-((t - delay_s)**2) / 0.0005)
            sig += envelope * np.sin(omega * t)
        
        # Normalize
        sig = sig / np.max(np.abs(sig) + 1e-10)
        sigs.append(sig)
    
    print(f"Signal lengths: {[len(s) for s in sigs]}")
    
    # Add noise
    np.random.seed(42)
    for i in range(3):
        noise_amp = noise * np.std(sigs[i])
        sigs[i] = sigs[i] + noise_amp * np.random.randn(len(sigs[i]))
    
    # Extract
    print("\n1. Extracting dispersion...")
    f, v, u = extract_dispersion_curve(sigs, dt, dists)
    print(f"   {len(f)} points extracted")
    
    if len(f) == 0:
        print("   ERROR: No dispersion points extracted!")
        return None
    
    # Smooth
    if len(f) == 0:
        print("   ERROR: No dispersion points!")
        return None
        
    print("2. Savitzky-Golay smoothing...")
    vs, us = savgol_smooth(f, v, u, 5, 3)
    
    # Bootstrap
    print("3. Bootstrap (n=1000)...")
    b = bootstrap_fit(f, vs, us)
    
    # Results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Theory:    G' = {Gt} Pa,     η = {et} Pa·s")
    if b:
        Ge = b['G_median']
        ee = b['eta_median']
        print(f"Estimated: G' = {Ge:.0f} Pa [{b['G_ci'][0]:.0f}, {b['G_ci'][1]:.0f}]")
        print(f"           η  = {ee:.3f} Pa·s [{b['eta_ci'][0]:.3f}, {b['eta_ci'][1]:.3f}]")
        print(f"Errors:    G' = {100*abs(Ge-Gt)/Gt:.1f}%, η = {100*abs(ee-et)/et:.1f}%")
    
    # Plot
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Dispersion curve
    ax = axes[0, 0]
    ax.errorbar(f, v, yerr=u, fmt='bo', alpha=0.4, capsize=3, label='Raw')
    ax.errorbar(f, vs, yerr=us, fmt='rs', alpha=0.7, capsize=3, label='Smoothed')
    wf = np.linspace(2*np.pi*f.min(), 2*np.pi*f.max(), 200)
    ff = wf / (2*np.pi)
    ax.plot(ff, kelvin_voigt_dispersion(wf, Gt, et), 'g--', label='True')
    if b:
        ax.plot(ff, kelvin_voigt_dispersion(wf, Ge, ee), 'r-', label='Fit')
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Velocity (m/s)')
    ax.set_title('Dispersion Curve')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Distributions
    if b:
        axes[0, 1].hist(b['G_samples'], 50, alpha=0.7, color='blue', edgecolor='k')
        axes[0, 1].axvline(Gt, color='g', linestyle='--', label='True')
        axes[0, 1].axvline(Ge, color='r', label='Estimate')
        axes[0, 1].set_xlabel("G' (Pa)")
        axes[0, 1].set_title("G' Distribution")
        axes[0, 1].legend()
        
        axes[1, 0].hist(b['eta_samples'], 50, alpha=0.7, color='orange', edgecolor='k')
        axes[1, 0].axvline(et, color='g', linestyle='--', label='True')
        axes[1, 0].axvline(ee, color='r', label='Estimate')
        axes[1, 0].set_xlabel('η (Pa·s)')
        axes[1, 0].set_title('η Distribution')
        axes[1, 0].legend()
        
        # Joint
        ax = axes[1, 1]
        H, xe, ye = np.histogram2d(b['G_samples'], b['eta_samples'], 50)
        ax.imshow(H.T, origin='lower', extent=[xe[0], xe[-1], ye[0], ye[-1]],
                 aspect='auto', cmap='Blues')
        ax.plot(Gt, et, 'g*', markersize=15, markeredgecolor='w', label='True')
        ax.plot(Ge, ee, 'r+', markersize=12, mew=2, label='Estimate')
        ax.set_xlabel("G' (Pa)")
        ax.set_ylabel('η (Pa·s)')
        ax.set_title('Joint Distribution')
        ax.legend()
    
    plt.suptitle('Complete Pipeline: Wavelet → Savgol → Bootstrap', fontweight='bold')
    plt.tight_layout()
    plt.savefig('dispersion_pipeline.png', dpi=150)
    print("\nSaved: dispersion_pipeline.png")
    
    return b


if __name__ == "__main__":
    import pywt
    run_pipeline(2000, 0.5, 0.15)
    print("\nDone!")
