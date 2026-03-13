#!/usr/bin/env python3
"""
Robust Phase Extraction for Sparse Shear Wave Sampling
========================================================

Improved validation with:
1. Time-domain cross-correlation (primary method)
2. Fixed frequency-domain phase unwrapping
3. Theoretical propagation depth limits

Author: Research Project — Validation Study v2
Date: March 13, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.signal import hilbert, correlate
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'research', 'week2'))

try:
    from shear_wave_2d_simple import ShearWave2D
    from phase_velocity_extraction import PhaseVelocityExtractor
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


def theoretical_attenuation_length(G_prime, eta, rho, freq):
    """
    Calculate attenuation length for Kelvin-Voigt material.
    
    Attenuation length = 1/k'' where k'' is the imaginary part of wavenumber.
    For Kelvin-Voigt:
        k'' = ω × √(ρ/(2|G*|)) × √(1 - μ/|G*|)
    
    Returns:
        L_att: attenuation length (m) - distance over which amplitude
tegrates to 1/e (≈37%)
    """
    omega = 2 * np.pi * freq
    G_mag = np.sqrt(G_prime**2 + (omega * eta)**2)
    
    if G_mag <= G_prime:
        return np.inf  # No attenuation in elastic limit
    
    k_double = omega * np.sqrt(rho / (2 * G_mag)) * np.sqrt(1 - G_prime/G_mag)
    L_att = 1.0 / k_double if k_double > 0 else np.inf
    
    return L_att


def practical_measuring_depth(G_prime, eta, rho, freq, adc_bits=12, snr_required=20):
    """
    Calculate practical measuring depth based on ADC dynamic range.
    
    Parameters:
    -----------
    adc_bits : int
        ADC resolution (12-bit = 72 dB dynamic range)
    snr_required : float
        Required signal-to-noise ratio in dB
        
    Returns:
    --------
    depth : float
        Maximum measurable depth (m)
    """
    L_att = theoretical_attenuation_length(G_prime, eta, rho, freq)
    
    # Dynamic range in dB
    dynamic_range_db = 6.02 * adc_bits  # ~72 dB for 12-bit
    usable_dynamic_range = dynamic_range_db - snr_required  # ~52 dB
    
    # Amplitude decays as exp(-k''·x) = exp(-x/L_att)
    # In dB: 20·log10(exp(-x/L_att)) = -8.686·x/L_att
    # For usable_dynamic_range dB attenuation:
    depth = usable_dynamic_range * L_att / 8.686
    
    return depth


def extract_phase_velocity_correlation(sig1, sig2, dt, distance, 
                                        freq_range=(20, 300)):
    """
    Extract phase velocity using time-domain cross-correlation
    with bandpass filtering.
    
    More robust than frequency-domain phase for sparse sampling.
    """
    # Bandpass filter to isolate frequency band
    nyquist = 1.0 / (2 * dt)
    low = freq_range[0] / nyquist
    high = freq_range[1] / nyquist
    
    b, a = signal.butter(4, [low, high], btype='band')
    sig1_filt = signal.filtfilt(b, a, sig1)
    sig2_filt = signal.filtfilt(b, a, sig2)
    
    # Cross-correlation
    corr = correlate(sig2_filt, sig1_filt, mode='full')
    lags = np.arange(-len(sig1)+1, len(sig1))
    
    # Find peak
    peak_idx = np.argmax(np.abs(corr))
    delay_samples = lags[peak_idx]
    delay = delay_samples * dt
    
    # Phase velocity
    if abs(delay) > 1e-10:
        c_p = distance / delay
    else:
        c_p = np.nan
    
    # Also compute group velocity from envelope
    env1 = np.abs(hilbert(sig1_filt))
    env2 = np.abs(hilbert(sig2_filt))
    corr_env = correlate(env2, env1, mode='full')
    peak_env_idx = np.argmax(np.abs(corr_env))
    delay_env = lags[peak_env_idx] * dt
    
    if abs(delay_env) > 1e-10:
        c_g = distance / delay_env
    else:
        c_g = np.nan
    
    return c_p, c_g, delay


def extract_phase_velocity_freq_domain(sig1, sig2, dt, distance, 
                                        freq_range=(20, 300)):
    """
    Extract phase velocity using frequency-domain method
    with improved phase unwrapping.
    """
    # Window and FFT
    window = signal.windows.hann(len(sig1))
    sig1_win = sig1 * window
    sig2_win = sig2 * window
    
    n_fft = len(sig1)
    freqs = np.fft.fftfreq(n_fft, dt)
    
    # Only positive frequencies in range
    mask = (freqs > freq_range[0]) & (freqs < freq_range[1])
    freqs = freqs[mask]
    
    fft1 = np.fft.fft(sig1_win)[mask]
    fft2 = np.fft.fft(sig2_win)[mask]
    
    # Cross-spectrum phase (more stable than individual phases)
    cross_spectrum = fft2 * np.conj(fft1)
    phase_diff = np.angle(cross_spectrum)
    
    # Unwrap phase
    phase_diff = np.unwrap(phase_diff)
    
    # Phase velocity with sign correction
    omega = 2 * np.pi * freqs
    c_p = omega * distance / phase_diff
    
    # Filter out unreliable points
    magnitude = np.abs(cross_spectrum)
    magnitude_threshold = 0.001 * np.max(magnitude)
    reliable = magnitude > magnitude_threshold
    
    c_p[~reliable] = np.nan
    
    return freqs, c_p


def run_robust_validation(G_prime=2000, eta=0.5, rho=1000, 
                          n_receivers=3, source_freq=100):
    """Run validation with robust extraction methods."""
    
    print(f"\n{'='*60}")
    print(f"ROBUST VALIDATION: G'={G_prime} Pa, η={eta} Pa·s")
    print(f"{'='*60}")
    
    # Theoretical limits
    L_att = theoretical_attenuation_length(G_prime, eta, rho, source_freq)
    depth_12bit = practical_measuring_depth(G_prime, eta, rho, source_freq, 
                                            adc_bits=12, snr_required=20)
    depth_16bit = practical_measuring_depth(G_prime, eta, rho, source_freq,
                                            adc_bits=16, snr_required=20)
    
    print(f"\nTHEORETICAL LIMITS:")
    print(f"  Attenuation length (1/e): {L_att*1000:.1f} mm")
    print(f"  40 dB attenuation depth: {L_att*1000*40/8.686:.1f} mm")
    print(f"  Practical depth (12-bit ADC): {depth_12bit*1000:.1f} mm")
    print(f"  Practical depth (16-bit ADC): {depth_16bit*1000:.1f} mm")
    
    # Domain parameters
    nx, ny = 300, 300
    dx = 0.0005
    pml_width = 20
    
    sim = ShearWave2D(nx=nx, ny=ny, dx=dx, 
                      rho=rho, G_prime=G_prime, eta=eta,
                      pml_width=pml_width)
    
    c_s = np.sqrt(G_prime / rho)
    print(f"\nSIMULATION:")
    print(f"  Expected wave speed: {c_s:.2f} m/s")
    print(f"  Wavelength: {c_s/source_freq*1000:.1f} mm")
    
    # Source and receivers
    source_x, source_y = nx // 2, ny // 2
    
    # Receivers at various distances to test depth limits
    distances_m = np.array([0.005, 0.010, 0.015, 0.020, 0.025])[:n_receivers]
    angles = np.linspace(0, np.pi/6, n_receivers)
    
    receiver_positions = []
    for i, d in enumerate(distances_m):
        angle = angles[i] if n_receivers > 1 else 0
        rx = int(source_x + d/dx * np.cos(angle))
        ry = int(source_y + d/dx * np.sin(angle))
        receiver_positions.append((rx, ry))
        print(f"  Receiver {i+1}: {d*1000:.1f} mm from source")
    
    # Setup extractor
    extractor = PhaseVelocityExtractor(sim)
    extractor.add_receivers(receiver_positions)
    
    # Run simulation
    n_steps = 4000
    source_duration = 5
    dt = sim.dt
    
    print(f"\nRunning {n_steps} steps (dt={dt*1e6:.1f} μs)...")
    
    for n in range(n_steps):
        t = n * dt
        
        if n < int(source_duration / source_freq / dt):
            sim.add_source(t, x_pos=source_x, y_pos=source_y,
                          amplitude=1e-6, f0=source_freq, source_type='tone_burst')
        
        sim.step()
        extractor.record()
        
        if n % 1000 == 0:
            print(f"  {100*n/n_steps:.0f}%")
    
    print("Complete.")
    
    # Extract using both methods
    results = {
        'G_prime': G_prime, 'eta': eta, 'rho': rho,
        'L_att': L_att, 'depth_12bit': depth_12bit,
        'receivers': receiver_positions,
        'distances': distances_m,
        'extractor': extractor
    }
    
    # Method 1: Cross-correlation (single broadband estimate)
    print("\nCROSS-CORRELATION METHOD:")
    corr_results = []
    
    for i in range(n_receivers - 1):
        for j in range(i + 1, n_receivers):
            sig1 = np.array(extractor.time_signals[i])
            sig2 = np.array(extractor.time_signals[j])
            distance = (distances_m[j] - distances_m[i])
            
            c_p, c_g, delay = extract_phase_velocity_correlation(
                sig1, sig2, dt, distance, freq_range=(50, 150)
            )
            
            corr_results.append({
                'pair': f'R{i+1}-R{j+1}',
                'distance': distance,
                'c_p': c_p,
                'c_g': c_g,
                'delay_ms': delay * 1000
            })
            
            print(f"  {distances_m[i]*1000:.1f}-{distances_m[j]*1000:.1f} mm: "
                  f"c_p={c_p:.2f} m/s, delay={delay*1000:.2f} ms")
    
    results['correlation'] = corr_results
    
    # Method 2: Frequency domain (dispersion curve)
    print("\nFREQUENCY-DOMAIN METHOD:")
    freq_results = []
    
    for i in range(n_receivers - 1):
        for j in range(i + 1, n_receivers):
            sig1 = np.array(extractor.time_signals[i])
            sig2 = np.array(extractor.time_signals[j])
            distance = (distances_m[j] - distances_m[i])
            
            freqs, c_p = extract_phase_velocity_freq_domain(
                sig1, sig2, dt, distance, freq_range=(20, 300)
            )
            
            valid = ~np.isnan(c_p)
            n_valid = np.sum(valid)
            
            freq_results.append({
                'pair': f'R{i+1}-R{j+1}',
                'freqs': freqs,
                'c_p': c_p,
                'n_valid': n_valid
            })
            
            print(f"  R{i+1}-R{j+1}: {n_valid} valid frequency points")
    
    results['frequency'] = freq_results
    
    return results


def plot_robust_results(results, save_path='robust_validation.png'):
    """Plot validation with both extraction methods."""
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    G_prime = results['G_prime']
    eta = results['eta']
    rho = results['rho']
    
    fig.suptitle(f'Robust Sparse Sampling: G\'={G_prime} Pa, η={eta} Pa·s\n'
                 f'Attenuation length: {results["L_att"]*1000:.1f} mm, '
                 f'12-bit depth limit: {results["depth_12bit"]*1000:.1f} mm',
                 fontsize=10)
    
    extractor = results['extractor']
    
    # Plot 1: Time signals
    ax1 = axes[0, 0]
    for i, sig in enumerate(extractor.time_signals):
        t = np.arange(len(sig)) * extractor.dt * 1000
        ax1.plot(t, np.array(sig) * 1e6, 
                label=f'R{i+1} ({results["distances"][i]*1000:.0f} mm)',
                alpha=0.7)
    ax1.set_xlabel('Time (ms)')
    ax1.set_ylabel('Displacement (μm)')
    ax1.set_title('Receiver Signals')
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Cross-correlation results
    ax2 = axes[0, 1]
    
    c_elastic = np.sqrt(G_prime / rho)
    ax2.axhline(c_elastic, color='black', linestyle='--', 
               label=f'Elastic limit: {c_elastic:.2f} m/s')
    
    for r in results['correlation']:
        d_avg = r['distance'] * 1000  # mm
        ax2.scatter(d_avg, r['c_p'], s=100, alpha=0.6, label=r['pair'])
    
    ax2.set_xlabel('Separation distance (mm)')
    ax2.set_ylabel('Phase velocity (m/s)')
    ax2.set_title('Cross-Correlation Method')
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Frequency-domain dispersion
    ax3 = axes[1, 0]
    
    # Analytical reference
    f = np.linspace(20, 300, 100)
    omega = 2 * np.pi * f
    G_mag = np.sqrt(G_prime**2 + (omega * eta)**2)
    c_p_theory = np.sqrt(2 / rho) * np.sqrt(G_mag**2 / (G_prime + G_mag))
    
    ax3.plot(f, c_p_theory, 'k-', linewidth=2, label='Analytical')
    ax3.axhline(c_elastic, color='gray', linestyle='--', alpha=0.5)
    
    colors = ['blue', 'red', 'green', 'purple']
    for i, r in enumerate(results['frequency']):
        valid = ~np.isnan(r['c_p'])
        ax3.scatter(r['freqs'][valid], r['c_p'][valid], 
                   c=colors[i % len(colors)], s=20, alpha=0.5,
                   label=r['pair'])
    
    ax3.set_xlabel('Frequency (Hz)')
    ax3.set_ylabel('Phase velocity (m/s)')
    ax3.set_title('Frequency-Domain Dispersion')
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Attenuation vs theoretical
    ax4 = axes[1, 1]
    
    for i, sig_data in enumerate(extractor.time_signals):
        sig = np.array(sig_data)
        envelope = np.abs(hilbert(sig))
        t = np.arange(len(sig)) * extractor.dt * 1000
        
        # Normalize to first receiver
        if i == 0:
            ref_max = np.max(envelope)
        
        ax4.semilogy(t, envelope / ref_max + 1e-6, 
                    label=f'R{i+1}', alpha=0.7)
    
    # Theoretical attenuation curve
    d_theoretical = np.linspace(0, 25, 100)  # mm
    k_double = 1 / (results['L_att'] * 1000)  # per mm
    atten_theory = np.exp(-k_double * d_theoretical)
    
    ax4.plot(d_theoretical + 5, atten_theory, 'k--', 
            label=f'Theory (L_att={results["L_att"]*1000:.1f}mm)')
    
    ax4.axvline(results['depth_12bit']*1000, color='red', linestyle=':',
               label=f'12-bit limit: {results["depth_12bit"]*1000:.0f} mm')
    
    ax4.set_xlabel('Time (ms) → Distance (mm)')
    ax4.set_ylabel('Normalized amplitude')
    ax4.set_title('Signal Attenuation')
    ax4.legend(fontsize=8)
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"\nSaved: {save_path}")
    
    return fig


def main():
    """Run robust validation suite."""
    
    print("ROBUST SPARSE SAMPLING VALIDATION")
    print("="*60)
    
    test_cases = [
        (2000, 0.3, "Soft tissue, low η (long propagation)"),
        (2000, 0.5, "Soft tissue, medium η"),
        (2000, 1.0, "Soft tissue, higher η (shorter range)"),
    ]
    
    for G_prime, eta, desc in test_cases:
        print(f"\n\n{desc}")
        results = run_robust_validation(
            G_prime=G_prime, eta=eta, rho=1000,
            n_receivers=3, source_freq=100
        )
        
        plot_robust_results(results, 
                           save_path=f'robust_G{G_prime}_eta{eta}.png')
    
    print("\n" + "="*60)
    print("VALIDATION COMPLETE")


if __name__ == '__main__':
    main()
