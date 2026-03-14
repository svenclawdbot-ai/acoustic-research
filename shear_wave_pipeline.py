#!/usr/bin/env python3
"""
Shear Wave Analysis Pipeline
============================

Unified end-to-end processing for shear wave dispersion analysis.

Pipeline stages:
1. Pre-processing (wavelet denoising)
2. Spatial validation (coherence check)
3. Group velocity extraction (multi-frequency)
4. Post-processing (Savgol smoothing + Bootstrap)

Usage:
    from shear_wave_pipeline import ShearWaveAnalyzer
    
    analyzer = ShearWaveAnalyzer()
    results = analyzer.analyze(time_signals, dt, distances)
    
    print(f"G' = {results['G_prime']:.0f} ± {results['G_prime_std']:.0f} Pa")

Author: Research Project
Date: March 14, 2026
"""

import numpy as np
from scipy.signal import hilbert, butter, filtfilt
from scipy.optimize import curve_fit
import warnings

# Import our modules
from wavelet_denoising import WaveletDenoiser
from spatial_filtering import compute_spatial_coherence
from dispersion_postprocessing import savgol_smooth, bootstrap_fit, kelvin_voigt


class ShearWaveAnalyzer:
    """
    Complete shear wave analysis pipeline.
    """
    
    def __init__(self, wavelet='sym6', threshold_factor=2.0, 
                 enable_spatial_check=True, enable_smoothing=True,
                 rho=1000):
        """
        Initialize analyzer with processing options.
        
        Parameters:
        -----------
        wavelet : str
            Wavelet family for denoising ('sym6' recommended)
        threshold_factor : float
            Denoising threshold multiplier (2.0 = conservative)
        enable_spatial_check : bool
            Validate wave propagation using array coherence
        enable_smoothing : bool
            Apply Savitzky-Golay smoothing to dispersion curve
        rho : float
            Material density (kg/m³)
        """
        self.wavelet = wavelet
        self.threshold_factor = threshold_factor
        self.enable_spatial_check = enable_spatial_check
        self.enable_smoothing = enable_smoothing
        self.rho = rho
        
        self.denoiser = WaveletDenoiser(
            wavelet=wavelet,
            level=5,
            threshold_factor=threshold_factor,
            mode='soft'
        )
        
        self.results = {}
    
    def analyze(self, signals, dt, distances, freq_range=(50, 150), 
                freq_step=10, verbose=True):
        """
        Run complete analysis pipeline.
        
        Parameters:
        -----------
        signals : list of arrays
            Time-domain signals from each receiver
        dt : float
            Time step (seconds)
        distances : array
            Receiver distances from source (meters)
        freq_range : tuple
            (min, max) frequency range (Hz)
        freq_step : int
            Frequency step size (Hz)
        verbose : bool
            Print progress
            
        Returns:
        --------
        dict with complete analysis results
        """
        self.results = {
            'signals_raw': signals,
            'dt': dt,
            'distances': distances,
            'config': {
                'wavelet': self.wavelet,
                'threshold_factor': self.threshold_factor,
                'spatial_check': self.enable_spatial_check,
                'smoothing': self.enable_smoothing
            }
        }
        
        if verbose:
            print("=" * 60)
            print("SHEAR WAVE ANALYSIS PIPELINE")
            print("=" * 60)
            print(f"Receivers: {len(signals)}")
            print(f"Distances: {[f'{d*1000:.1f} mm' for d in distances]}")
            print(f"Sampling: {1/dt/1000:.1f} kHz")
            print(f"Frequency range: {freq_range[0]}-{freq_range[1]} Hz")
        
        # Stage 1: Wavelet denoising
        if verbose:
            print("\n[1/4] Wavelet denoising...")
        signals_denoised = self._denoise_signals(signals)
        self.results['signals_denoised'] = signals_denoised
        
        # Stage 2: Spatial coherence check
        if self.enable_spatial_check:
            if verbose:
                print("[2/4] Spatial coherence validation...")
            coherence = self._check_spatial_coherence(
                signals_denoised, dt, distances
            )
            self.results['spatial_coherence'] = coherence
            
            if verbose:
                print(f"       Velocity estimate: {coherence['velocity_mean']:.2f} m/s")
                print(f"       Consistency: {coherence['consistency']:.3f}")
                
            # Flag if coherence is poor
            if coherence['consistency'] < 0.7:
                self.results['quality_flag'] = 'LOW_COHERENCE'
                if verbose:
                    print("       WARNING: Low spatial coherence detected")
            else:
                self.results['quality_flag'] = 'OK'
        else:
            self.results['quality_flag'] = 'NOT_CHECKED'
        
        # Stage 3: Extract dispersion curve
        if verbose:
            print("[3/4] Extracting dispersion curve...")
        
        freqs, vels, uncs = self._extract_dispersion(
            signals_denoised, dt, distances,
            freq_range, freq_step
        )
        
        self.results['dispersion_raw'] = {
            'frequencies': freqs,
            'velocities': vels,
            'uncertainties': uncs
        }
        
        if verbose:
            print(f"       Extracted {len(freqs)} frequency points")
        
        if len(freqs) < 4:
            if verbose:
                print("       ERROR: Insufficient dispersion points")
            self.results['success'] = False
            return self.results
        
        # Stage 4: Post-processing
        if verbose:
            print("[4/4] Post-processing...")
        
        # Savitzky-Golay smoothing
        if self.enable_smoothing:
            vels_smooth, uncs_smooth = savgol_smooth(
                freqs, vels, uncs, window_length=5, polyorder=3
            )
            self.results['dispersion_smooth'] = {
                'frequencies': freqs,
                'velocities': vels_smooth,
                'uncertainties': uncs_smooth
            }
            vels_fit = vels_smooth
            uncs_fit = uncs_smooth
        else:
            vels_fit = vels
            uncs_fit = uncs
        
        # Bootstrap fit
        bootstrap = bootstrap_fit(freqs, vels_fit, uncs_fit, n=1000, rho=self.rho)
        
        if bootstrap is None:
            if verbose:
                print("       ERROR: Bootstrap fit failed")
            self.results['success'] = False
            return self.results
        
        self.results['bootstrap'] = bootstrap
        self.results['success'] = True
        
        # Extract key parameters
        self.results['G_prime'] = bootstrap['G_median']
        self.results['G_prime_std'] = bootstrap['G_std']
        self.results['G_prime_ci'] = bootstrap['G_ci']
        self.results['eta'] = bootstrap['eta_median']
        self.results['eta_std'] = bootstrap['eta_std']
        self.results['eta_ci'] = bootstrap['eta_ci']
        
        if verbose:
            print("\n" + "=" * 60)
            print("RESULTS")
            print("=" * 60)
            print(f"G' = {self.results['G_prime']:.0f} ± {self.results['G_prime_std']:.0f} Pa")
            print(f"     95% CI: [{self.results['G_prime_ci'][0]:.0f}, {self.results['G_prime_ci'][1]:.0f}]")
            print(f"η  = {self.results['eta']:.3f} ± {self.results['eta_std']:.3f} Pa·s")
            print(f"     95% CI: [{self.results['eta_ci'][0]:.3f}, {self.results['eta_ci'][1]:.3f}]")
            print(f"Quality: {self.results['quality_flag']}")
            print("=" * 60)
        
        return self.results
    
    def _denoise_signals(self, signals):
        """Apply wavelet denoising to all signals."""
        return [self.denoiser.denoise(sig.copy()) for sig in signals]
    
    def _check_spatial_coherence(self, signals, dt, distances):
        """Check spatial coherence of wave propagation."""
        coherence = compute_spatial_coherence(signals, dt, distances)
        
        return {
            'coherence_matrix': coherence['cc_matrix'],
            'velocity_estimates': coherence['velocity_estimates'],
            'velocity_mean': np.mean(coherence['velocity_estimates']) if coherence['velocity_estimates'] else 0,
            'velocity_std': np.std(coherence['velocity_estimates']) if coherence['velocity_estimates'] else 0,
            'consistency': coherence['velocity_consistency'],
            'receiver_coherence': coherence['receiver_coherence']
        }
    
    def _extract_dispersion(self, signals, dt, distances, 
                            freq_range, freq_step):
        """Extract dispersion curve c(ω)."""
        freq_centers = np.arange(freq_range[0], freq_range[1] + 1, freq_step)
        n_receivers = len(signals)
        
        freqs, vels, uncs = [], [], []
        
        for f_center in freq_centers:
            pair_vels, pair_dists = [], []
            
            for i in range(n_receivers - 1):
                for j in range(i + 1, n_receivers):
                    s1, s2 = signals[i].copy(), signals[j].copy()
                    dist = distances[j] - distances[i]
                    
                    # Bandpass filter
                    nyq = 1.0 / (2 * dt)
                    low = max(0.01, (f_center - freq_step/2) / nyq)
                    high = min(0.99, (f_center + freq_step/2) / nyq)
                    
                    if low >= high:
                        continue
                    
                    try:
                        b, a = butter(4, [low, high], btype='band')
                        s1f = filtfilt(b, a, s1)
                        s2f = filtfilt(b, a, s2)
                    except:
                        continue
                    
                    # Envelope peak detection
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
                    if delay > 1e-9:
                        pair_vels.append(dist / delay)
                        pair_dists.append(dist)
            
            if pair_vels:
                weights = np.array(pair_dists) / sum(pair_dists)
                v = np.average(pair_vels, weights=weights)
                freqs.append(f_center)
                vels.append(v)
                uncs.append(np.std(pair_vels))
        
        return np.array(freqs), np.array(vels), np.array(uncs)
    
    def plot_results(self, save_path=None):
        """
        Plot complete analysis results.
        """
        import matplotlib.pyplot as plt
        
        if not self.results.get('success'):
            print("No successful results to plot")
            return None
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Plot 1: Signals
        ax = axes[0, 0]
        t = np.arange(len(self.results['signals_raw'][0])) * self.results['dt'] * 1000
        for i, (raw, den) in enumerate(zip(self.results['signals_raw'], 
                                           self.results['signals_denoised'])):
            ax.plot(t, raw + i*2, 'b-', alpha=0.3, linewidth=0.5)
            ax.plot(t, den + i*2, 'r-', alpha=0.8, linewidth=0.8, 
                   label=f'R{i+1}' if i == 0 else '')
        ax.set_xlim([30, 80])
        ax.set_xlabel('Time (ms)')
        ax.set_ylabel('Displacement (offset)')
        ax.set_title('Raw vs Denoised Signals')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Plot 2: Dispersion curve
        ax = axes[0, 1]
        dr = self.results['dispersion_raw']
        ax.errorbar(dr['frequencies'], dr['velocities'], 
                   yerr=dr['uncertainties'], fmt='bo', capsize=3, 
                   alpha=0.5, label='Raw')
        
        if self.enable_smoothing and 'dispersion_smooth' in self.results:
            ds = self.results['dispersion_smooth']
            ax.errorbar(ds['frequencies'], ds['velocities'],
                       yerr=ds['uncertainties'], fmt='rs', capsize=3,
                       alpha=0.7, label='Smoothed')
        
        # Theory and fit
        if 'bootstrap' in self.results:
            b = self.results['bootstrap']
            wf = np.linspace(2*np.pi*dr['frequencies'].min(), 
                            2*np.pi*dr['frequencies'].max(), 200)
            ff = wf / (2*np.pi)
            ax.plot(ff, kelvin_voigt(wf, b['G_median'], b['eta_median'], self.rho),
                   'r-', linewidth=2, label='Fit')
        
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Velocity (m/s)')
        ax.set_title('Dispersion Curve')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Plot 3: Bootstrap distributions
        if 'bootstrap' in self.results:
            b = self.results['bootstrap']
            
            ax = axes[1, 0]
            ax.hist(b['G_samples'], 50, alpha=0.7, color='blue', edgecolor='k')
            ax.axvline(b['G_median'], color='red', linestyle='-', linewidth=2,
                      label=f"G' = {b['G_median']:.0f} Pa")
            ax.set_xlabel("G' (Pa)")
            ax.set_ylabel('Count')
            ax.set_title("G' Bootstrap Distribution")
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            ax = axes[1, 1]
            ax.hist(b['eta_samples'], 50, alpha=0.7, color='orange', edgecolor='k')
            ax.axvline(b['eta_median'], color='red', linestyle='-', linewidth=2,
                      label=f"η = {b['eta_median']:.3f} Pa·s")
            ax.set_xlabel('η (Pa·s)')
            ax.set_ylabel('Count')
            ax.set_title('η Bootstrap Distribution')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        plt.suptitle('Shear Wave Analysis Results', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved: {save_path}")
        
        return fig


# Demo/test function
def demo():
    """
    Demonstrate the complete pipeline with synthetic data.
    """
    print("\nRunning pipeline demo with synthetic data...\n")
    
    # Generate synthetic dispersion curve directly
    np.random.seed(42)
    
    G_true, eta_true = 2000, 0.5
    rho = 1000
    
    # Create frequency points
    freq = np.array([60, 70, 80, 90, 100, 110, 120, 130, 140])
    omega = 2 * np.pi * freq
    
    # True velocities
    v_true = kelvin_voigt(omega, G_true, eta_true, rho)
    
    # Add measurement noise
    v_noisy = v_true * (1 + 0.05 * np.random.randn(len(freq)))
    unc = 0.03 * v_noisy
    
    print("Generated synthetic dispersion data:")
    print(f"  Frequencies: {freq}")
    print(f"  True G': {G_true} Pa, True η: {eta_true} Pa·s")
    
    # Create dummy signals (not used for fitting, but for pipeline compatibility)
    fs = 20000
    dt = 1/fs
    t = np.linspace(0, 0.1, int(fs * 0.1))
    signals = [np.sin(2*np.pi*100*t) + 0.1*np.random.randn(len(t)) for _ in range(3)]
    distances = np.array([0.005, 0.010, 0.015])
    
    # Run analysis with pre-computed dispersion
    print("\n" + "=" * 60)
    print("DIRECT DISPERSION FIT (Skipping extraction)")
    print("=" * 60)
    
    from dispersion_postprocessing import savgol_smooth, bootstrap_fit
    
    # Apply smoothing
    v_smooth, unc_smooth = savgol_smooth(freq, v_noisy, unc, 5, 3)
    
    # Bootstrap fit
    bootstrap = bootstrap_fit(freq, v_smooth, unc_smooth, n=1000, rho=rho)
    
    if bootstrap:
        print(f"\nResults:")
        print(f"G' = {bootstrap['G_median']:.0f} ± {bootstrap['G_std']:.0f} Pa")
        print(f"     95% CI: [{bootstrap['G_ci'][0]:.0f}, {bootstrap['G_ci'][1]:.0f}]")
        print(f"η  = {bootstrap['eta_median']:.3f} ± {bootstrap['eta_std']:.3f} Pa·s")
        print(f"     95% CI: [{bootstrap['eta_ci'][0]:.3f}, {bootstrap['eta_ci'][1]:.3f}]")
        
        G_err = 100 * abs(bootstrap['G_median'] - G_true) / G_true
        eta_err = 100 * abs(bootstrap['eta_median'] - eta_true) / eta_true
        print(f"\nValidation:")
        print(f"True: G' = {G_true}, η = {eta_true}")
        print(f"Errors: G' = {G_err:.1f}%, η = {eta_err:.1f}%")
        
        # Plot
        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        # Dispersion curve
        ax = axes[0]
        ax.errorbar(freq, v_noisy, yerr=unc, fmt='bo', capsize=3, alpha=0.5, label='Raw')
        ax.errorbar(freq, v_smooth, yerr=unc_smooth, fmt='rs', capsize=3, alpha=0.7, label='Smoothed')
        
        wf = np.linspace(omega.min(), omega.max(), 200)
        ff = wf / (2*np.pi)
        ax.plot(ff, kelvin_voigt(wf, G_true, eta_true, rho), 'g--', linewidth=2, label='True')
        ax.plot(ff, kelvin_voigt(wf, bootstrap['G_median'], bootstrap['eta_median'], rho), 
                'r-', linewidth=2, label='Fit')
        
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Velocity (m/s)')
        ax.set_title('Dispersion Curve')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Bootstrap distributions
        ax = axes[1]
        ax.hist(bootstrap['G_samples'], 50, alpha=0.7, color='blue', edgecolor='k', label="G'")
        ax.axvline(G_true, color='green', linestyle='--', label='True')
        ax.axvline(bootstrap['G_median'], color='red', label='Fit')
        ax.set_xlabel("G' (Pa)")
        ax.set_ylabel('Count')
        ax.set_title("G' Bootstrap Distribution")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.suptitle('Shear Wave Pipeline Demo', fontweight='bold')
        plt.tight_layout()
        plt.savefig('pipeline_demo.png', dpi=150)
        print("\nSaved: pipeline_demo.png")
    
    return bootstrap


if __name__ == "__main__":
    demo()
