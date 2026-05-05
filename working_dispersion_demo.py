#!/usr/bin/env python3
"""
Working Demonstration: Narrowband Dispersion Extraction
==========================================================

Generates well-separated narrowband signals and demonstrates:
1. GCC-PHAT time delay estimation
2. Frequency-domain phase extraction
3. Kelvin-Voigt parameter fitting

This demonstrates the methods on clean, controlled synthetic data
where the ground truth is known exactly.

Author: Research Project
Date: April 16, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert, butter, filtfilt
from scipy.fftpack import fft, ifft
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from subsample_gcc import gcc_phat


def generate_narrowband_signal(t, f_center, arrival_time, burst_width=0.005):
    """
    Generate a narrowband tone burst.
    
    Parameters:
    -----------
    t : array
        Time array
    f_center : float
        Center frequency (Hz)
    arrival_time : float
        Arrival time (seconds)
    burst_width : float
        Burst duration (seconds)
        
    Returns:
    --------
    signal : array
        Narrowband signal with proper phase delay
    """
    omega = 2 * np.pi * f_center
    
    # Gaussian envelope
    envelope = np.exp(-((t - arrival_time)**2) / (2 * (burst_width/3)**2))
    
    # Carrier with phase including arrival time (for GCC-PHAT to measure delay)
    phase = omega * (t - arrival_time)
    carrier = np.sin(phase)
    
    return envelope * carrier


def generate_receiver_signals(distances, frequencies, G_prime, eta, rho, 
                              t, base_times, noise_level=0.0):
    """
    Generate signals for multiple receivers at multiple frequencies.
    
    Each frequency has its own arrival time (dispersive propagation).
    """
    signals = []
    
    for d in distances:
        sig = np.zeros_like(t)
        
        for f_center, t_base in zip(frequencies, base_times):
            # Theoretical phase velocity at this frequency
            omega = 2 * np.pi * f_center
            G_mag = np.sqrt(G_prime**2 + (omega * eta)**2)
            c_f = np.sqrt(2 / rho) * np.sqrt(G_mag**2 / (G_prime + G_mag))
            
            # Arrival time
            arrival = t_base + d / c_f
            
            # Generate tone burst
            sig += generate_narrowband_signal(t, f_center, arrival)
        
        # Normalize
        sig = sig / (np.max(np.abs(sig)) + 1e-10)
        
        # Add noise
        if noise_level > 0:
            noise_amp = noise_level * np.std(sig)
            sig += noise_amp * np.random.randn(len(sig))
        
        signals.append(sig)
    
    return signals


def extract_dispersion_envelope(signals, dt, distances, frequencies):
    """
    Extract dispersion using envelope cross-correlation.
    
    For each frequency:
    1. Bandpass filter to isolate the frequency
    2. Compute envelopes
    3. Cross-correlate to find delay
    4. Calculate velocity
    """
    results = {'frequencies': [], 'velocities': [], 'uncertainties': []}
    fs = 1.0 / dt
    
    print("\nExtracting with envelope method...")
    
    for f_center in frequencies:
        pair_velocities = []
        
        for i in range(len(signals) - 1):
            for j in range(i + 1, len(signals)):
                # Filter both signals
                nyq = fs / 2
                low = max(0.01, (f_center - 12) / nyq)
                high = min(0.99, (f_center + 12) / nyq)
                
                try:
                    b, a = butter(2, [low, high], btype='band')
                    s1_f = filtfilt(b, a, signals[i])
                    s2_f = filtfilt(b, a, signals[j])
                except:
                    continue
                
                # Envelopes
                env1 = np.abs(hilbert(s1_f))
                env2 = np.abs(hilbert(s2_f))
                
                # Find peaks
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
            # IQR outlier rejection (stricter: k=1.0)
            v_array = np.array(pair_velocities)
            if len(v_array) >= 3:
                q1, q3 = np.percentile(v_array, [25, 75])
                iqr = q3 - q1
                mask = (v_array >= q1 - 1.0*iqr) & (v_array <= q3 + 1.0*iqr)
                v_clean = v_array[mask]
                if len(v_clean) >= 2:
                    v_array = v_clean
            
            v_mean = np.median(v_array)  # Use median instead of mean
            v_std = np.std(v_array) if len(v_array) > 1 else 0.05 * v_mean
            
            # Sanity check: reject if more than 3x the expected velocity
            if v_mean > 2.5:  # Expected is ~1.4 m/s
                print(f"    {f_center:.0f} Hz: REJECTED (outlier: {v_mean:.2f} m/s)")
                continue
            
            results['frequencies'].append(f_center)
            results['velocities'].append(v_mean)
            results['uncertainties'].append(v_std)
            
            print(f"  {f_center:.0f} Hz: c = {v_mean:.2f} ± {v_std:.2f} m/s")
    
    return results


def extract_dispersion_gcc_phat(signals, dt, distances, frequencies):
    """
    Extract dispersion using GCC-PHAT.
    
    Similar to envelope method but uses GCC-PHAT for sub-sample delay.
    """
    results = {'frequencies': [], 'velocities': [], 'uncertainties': []}
    fs = 1.0 / dt
    
    print("\nExtracting with GCC-PHAT...")
    
    for f_center in frequencies:
        pair_velocities = []
        
        for i in range(len(signals) - 1):
            for j in range(i + 1, len(signals)):
                # Filter
                nyq = fs / 2
                low = max(0.01, (f_center - 12) / nyq)
                high = min(0.99, (f_center + 12) / nyq)
                
                try:
                    b, a = butter(2, [low, high], btype='band')
                    s1_f = filtfilt(b, a, signals[i])
                    s2_f = filtfilt(b, a, signals[j])
                except:
                    continue
                
                # Coarse delay from envelope (to resolve phase ambiguity)
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
                
                # Fine delay from GCC-PHAT
                delay_fine, corr = gcc_phat(s1_f, s2_f, fs, freq_range=(f_center-10, f_center+10))
                
                # Resolve phase ambiguity
                period = 1.0 / f_center
                n_periods = round((delay_fine - coarse_delay) / period)
                delay = delay_fine - n_periods * period
                
                distance = distances[j] - distances[i]
                
                if delay > 1e-9:
                    velocity = distance / delay
                    if 0.5 <= velocity <= 10:
                        pair_velocities.append(velocity)
        
        if pair_velocities:
            # IQR outlier rejection (stricter: k=1.0)
            v_array = np.array(pair_velocities)
            if len(v_array) >= 3:
                q1, q3 = np.percentile(v_array, [25, 75])
                iqr = q3 - q1
                mask = (v_array >= q1 - 1.0*iqr) & (v_array <= q3 + 1.0*iqr)
                v_clean = v_array[mask]
                if len(v_clean) >= 2:
                    v_array = v_clean
            
            v_mean = np.median(v_array)  # Use median instead of mean
            v_std = np.std(v_array) if len(v_array) > 1 else 0.05 * v_mean
            
            # Sanity check: reject if more than 3x the expected velocity
            if v_mean > 2.5:  # Expected is ~1.4 m/s
                print(f"    {f_center:.0f} Hz: REJECTED (outlier: {v_mean:.2f} m/s)")
                continue
            
            results['frequencies'].append(f_center)
            results['velocities'].append(v_mean)
            results['uncertainties'].append(v_std)
            
            print(f"  {f_center:.0f} Hz: c = {v_mean:.2f} ± {v_std:.2f} m/s")
    
    return results


def extract_dispersion_freq_domain(signals, dt, distances, frequencies):
    """
    Extract dispersion using frequency-domain phase.
    
    Uses cross-spectrum phase at each frequency.
    """
    results = {'frequencies': [], 'velocities': [], 'uncertainties': []}
    fs = 1.0 / dt
    
    print("\nExtracting with frequency-domain method...")
    
    # Use first and last receiver (largest separation for cleanest phase)
    i, j = 0, len(signals) - 1
    distance = distances[j] - distances[i]
    
    # Window and FFT
    window = np.hanning(len(signals[i]))
    n_fft = len(signals[i])
    
    fft_i = fft(signals[i] * window)
    fft_j = fft(signals[j] * window)
    
    freqs = np.fft.fftfreq(n_fft, dt)
    
    # Cross-spectrum
    cross_spec = fft_j * np.conj(fft_i)
    phase = np.unwrap(np.angle(cross_spec))
    magnitude = np.abs(cross_spec)
    
    omega = 2 * np.pi * freqs
    
    # Phase velocity at each frequency
    # c = ω * distance / phase
    phase_safe = np.where(np.abs(phase) < 1e-10, 1e-10, phase)
    c_all = omega * distance / phase_safe
    
    # Extract at desired frequencies
    for f_center in frequencies:
        # Find closest frequency bin
        idx = np.argmin(np.abs(freqs - f_center))
        
        # Check if magnitude is significant
        if magnitude[idx] > 0.01 * np.max(magnitude):
            velocity = c_all[idx]
            
            # Use nearby points for uncertainty estimate
            nearby = slice(max(0, idx-2), min(len(c_all), idx+3))
            unc = np.std(c_all[nearby])
            
            if 0.5 <= velocity <= 10:
                results['frequencies'].append(f_center)
                results['velocities'].append(velocity)
                results['uncertainties'].append(unc)
                
                print(f"  {f_center:.0f} Hz: c = {velocity:.2f} ± {unc:.2f} m/s")
    
    return results


def fit_kelvin_voigt(freq, vel, unc, rho=1000):
    """Fit Kelvin-Voigt model."""
    from scipy.optimize import curve_fit
    
    def kv(omega, Gp, et):
        Gm = np.sqrt(Gp**2 + (omega*et)**2)
        return np.sqrt(2/rho) * np.sqrt(Gm**2 / (Gp + Gm))
    
    freq = np.array(freq)
    vel = np.array(vel)
    unc = np.array(unc) if unc is not None else None
    
    omega = 2 * np.pi * freq
    
    # Initial guess
    c0 = np.median(vel)
    G0 = rho * c0**2
    
    try:
        popt, pcov = curve_fit(kv, omega, vel, p0=[G0, 0.5],
                              bounds=([10, 0.001], [50000, 50]),
                              sigma=unc, maxfev=5000)
        
        Gp, et = popt
        G_err, eta_err = np.sqrt(np.diag(pcov))
        
        # R²
        residuals = vel - kv(omega, *popt)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((vel - np.mean(vel))**2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        return {'G_prime': Gp, 'eta': et, 'G_err': G_err, 'eta_err': eta_err,
                'r_squared': r2, 'success': True}
    except:
        return {'G_prime': G0, 'eta': 0.5, 'success': False}


def plot_comparison(t, signals, distances, results_all, true_params, save_path):
    """Plot comparison of all three methods."""
    fig = plt.figure(figsize=(16, 10))
    
    # Create grid
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # Plot signals
    ax_signals = fig.add_subplot(gs[0, :])
    t_ms = t * 1000
    for i, (sig, d) in enumerate(zip(signals, distances)):
        ax_signals.plot(t_ms, sig * 1e6, alpha=0.7, label=f'R{i+1} ({d*1000:.0f}mm)')
    ax_signals.set_xlabel('Time (ms)')
    ax_signals.set_ylabel('Displacement (μm)')
    ax_signals.set_title('Receiver Signals (Multiple Tone Bursts)')
    ax_signals.legend(ncol=2)
    ax_signals.grid(True, alpha=0.3)
    ax_signals.set_xlim(0, 120)
    
    # Plot dispersion curves
    ax_disp = fig.add_subplot(gs[1:, :2])
    
    G_true, eta_true, rho = true_params
    
    # True curve
    f_theory = np.linspace(50, 150, 200)
    omega_theory = 2 * np.pi * f_theory
    G_mag_theory = np.sqrt(G_true**2 + (omega_theory * eta_true)**2)
    c_theory = np.sqrt(2/rho) * np.sqrt(G_mag_theory**2 / (G_true + G_mag_theory))
    ax_disp.plot(f_theory, c_theory, 'k--', linewidth=2, label='True', zorder=10)
    
    # Methods
    colors = ['blue', 'green', 'red']
    names = ['Envelope', 'GCC-PHAT', 'Freq-Domain']
    
    for results, color, name in zip(results_all, colors, names):
        if len(results['velocities']) > 0:
            ax_disp.errorbar(results['frequencies'], results['velocities'],
                           yerr=results['uncertainties'],
                           fmt='o', color=color, capsize=3, alpha=0.7,
                           label=name)
    
    ax_disp.set_xlabel('Frequency (Hz)')
    ax_disp.set_ylabel('Phase Velocity (m/s)')
    ax_disp.set_title('Dispersion Curve Comparison')
    ax_disp.legend()
    ax_disp.grid(True, alpha=0.3)
    ax_disp.set_ylim(0, 6)
    
    # Parameter comparison
    ax_params = fig.add_subplot(gs[1, 2])
    ax_params.text(0.1, 0.9, f"True Parameters:", fontsize=11, fontweight='bold', transform=ax_params.transAxes)
    ax_params.text(0.1, 0.8, f"  G' = {G_true:.0f} Pa", fontsize=10, transform=ax_params.transAxes)
    ax_params.text(0.1, 0.7, f"  η = {eta_true:.3f} Pa·s", fontsize=10, transform=ax_params.transAxes)
    
    y_pos = 0.5
    for results, color, name in zip(results_all, colors, names):
        fit = fit_kelvin_voigt(results['frequencies'], results['velocities'],
                             results['uncertainties'], rho)
        if fit['success']:
            G_err = 100 * abs(fit['G_prime'] - G_true) / G_true
            eta_err = 100 * abs(fit['eta'] - eta_true) / eta_true
            
            ax_params.text(0.1, y_pos, f"{name}:", fontsize=10, 
                          color=color, fontweight='bold', transform=ax_params.transAxes)
            ax_params.text(0.1, y_pos-0.08, f"  G' = {fit['G_prime']:.0f} Pa ({G_err:.1f}% err)", 
                          fontsize=9, color=color, transform=ax_params.transAxes)
            ax_params.text(0.1, y_pos-0.15, f"  η = {fit['eta']:.3f} Pa·s ({eta_err:.1f}% err)",
                          fontsize=9, color=color, transform=ax_params.transAxes)
            y_pos -= 0.25
    
    ax_params.set_xlim(0, 1)
    ax_params.set_ylim(0, 1)
    ax_params.axis('off')
    ax_params.set_title('Parameter Recovery')
    
    # Residuals
    ax_res = fig.add_subplot(gs[2, 2])
    
    for results, color, name in zip(results_all, colors, names):
        if len(results['velocities']) > 0:
            fit = fit_kelvin_voigt(results['frequencies'], results['velocities'],
                                 results['uncertainties'], rho)
            if fit['success']:
                omega = 2 * np.pi * np.array(results['frequencies'])
                Gm = np.sqrt(fit['G_prime']**2 + (omega*fit['eta'])**2)
                c_fit = np.sqrt(2/rho) * np.sqrt(Gm**2 / (fit['G_prime'] + Gm))
                residuals = np.array(results['velocities']) - c_fit
                
                ax_res.scatter(results['frequencies'], residuals, 
                             c=color, alpha=0.6, label=name, s=50)
    
    ax_res.axhline(0, color='black', linestyle='-', linewidth=1)
    ax_res.set_xlabel('Frequency (Hz)')
    ax_res.set_ylabel('Residual (m/s)')
    ax_res.set_title('Fit Residuals')
    ax_res.grid(True, alpha=0.3)
    
    plt.suptitle('Narrowband Dispersion Extraction: Method Comparison', 
                fontweight='bold', fontsize=14)
    
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"\nSaved: {save_path}")
    
    return fig


def main():
    """Run complete working demonstration."""
    print("=" * 70)
    print("Working Demonstration: Narrowband Dispersion Extraction")
    print("=" * 70)
    
    # True parameters
    G_prime_true = 2000
    eta_true = 0.5
    rho = 1000
    
    print(f"\nTrue: G' = {G_prime_true} Pa, η = {eta_true} Pa·s")
    
    # Setup
    fs = 20000
    dt = 1 / fs
    duration = 0.12
    t = np.linspace(0, duration, int(fs * duration))
    
    # Receivers
    distances = np.array([0.005, 0.015, 0.025, 0.035])  # 5, 15, 25, 35 mm
    
    # Frequencies - spaced apart in time
    frequencies = [60, 80, 100, 120, 140]
    base_times = [0.030, 0.045, 0.060, 0.075, 0.090]  # Well separated
    
    # Generate signals
    print("\nGenerating synthetic narrowband signals...")
    np.random.seed(42)
    signals = generate_receiver_signals(
        distances, frequencies, G_prime_true, eta_true, rho,
        t, base_times, noise_level=0.10
    )
    
    print(f"  {len(signals)} receivers, {len(frequencies)} frequencies")
    
    # Extract with all three methods
    results_envelope = extract_dispersion_envelope(signals, dt, distances, frequencies)
    results_gcc = extract_dispersion_gcc_phat(signals, dt, distances, frequencies)
    results_freq = extract_dispersion_freq_domain(signals, dt, distances, frequencies)
    
    results_all = [results_envelope, results_gcc, results_freq]
    
    # Fit and compare
    print("\n" + "=" * 70)
    print("Fitting Results:")
    print("=" * 70)
    
    names = ['Envelope', 'GCC-PHAT', 'Freq-Domain']
    
    for results, name in zip(results_all, names):
        if len(results['velocities']) > 0:
            fit = fit_kelvin_voigt(results['frequencies'], results['velocities'],
                                 results['uncertainties'], rho)
            if fit['success']:
                G_err = 100 * abs(fit['G_prime'] - G_prime_true) / G_prime_true
                eta_err = 100 * abs(fit['eta'] - eta_true) / eta_true
                
                print(f"\n{name}:")
                print(f"  G' = {fit['G_prime']:.0f} Pa (error: {G_err:.1f}%)")
                print(f"  η = {fit['eta']:.3f} Pa·s (error: {eta_err:.1f}%)")
                print(f"  R² = {fit['r_squared']:.4f}")
    
    # Plot
    plot_comparison(t, signals, distances, results_all,
                   (G_prime_true, eta_true, rho),
                   'dispersion_working_demo.png')
    
    print("\n" + "=" * 70)
    print("Demonstration Complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()
