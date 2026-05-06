#!/usr/bin/env python3
"""
Low-Viscosity Validation for Sparse Shear Wave Sampling
========================================================

Validates phase velocity extraction with realistic tissue parameters
(eta = 0.1-0.5 Pa.s) where wave propagation is observable.

Tests the core hypothesis: Can we recover G' and eta from 2-3 receivers?

Author: Research Project — Validation Study
Date: March 13, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import sys
import os

# Add week2 to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'research', 'week2'))

try:
    from shear_wave_2d_simple import ShearWave2D
    from phase_velocity_extraction import PhaseVelocityExtractor
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure week2/ contains the simulator files")
    sys.exit(1)


def analytical_phase_velocity(omega, mu, eta, rho):
    """
    Analytical Kelvin-Voigt phase velocity for validation.
    
    c_p(omega) = sqrt(2/rho) * sqrt(|G*|^2 / (G' + |G*|))
    
    where |G*| = sqrt(G'^2 + (omega*eta)^2)
    """
    G_mag = np.sqrt(mu**2 + (omega * eta)**2)
    c_p = np.sqrt(2 / rho) * np.sqrt(G_mag**2 / (mu + G_mag))
    return c_p


def run_sparse_validation(G_prime=2000, eta=0.5, rho=1000, 
                          n_receivers=3, source_freq=100):
    """
    Run validation with sparse receiver configuration.
    
    Parameters:
    -----------
    G_prime : float
        Shear modulus (Pa)
    eta : float  
        Viscosity (Pa.s) - LOW value for propagation
    rho : float
        Density (kg/m³)
    n_receivers : int
        Number of receivers (2 or 3)
    source_freq : float
        Center frequency of source excitation (Hz)
        
    Returns:
    --------
    results : dict
        Contains simulated and analytical dispersion curves
    """
    
    print(f"\n{'='*60}")
    print(f"SPARSE VALIDATION: G'={G_prime} Pa, eta={eta} Pa.s")
    print(f"{'='*60}")
    
    # Domain parameters
    nx, ny = 300, 300
    dx = 0.0005  # 0.5 mm grid
    pml_width = 20
    
    # Create simulator
    sim = ShearWave2D(nx=nx, ny=ny, dx=dx, 
                      rho=rho, G_prime=G_prime, eta=eta,
                      pml_width=pml_width)
    
    # Expected shear wave speed (elastic limit)
    c_s = np.sqrt(G_prime / rho)
    print(f"Expected wave speed: {c_s:.2f} m/s")
    print(f"Grid resolution: {dx*1000:.1f} mm")
    print(f"Wavelength at {source_freq} Hz: {c_s/source_freq*1000:.1f} mm")
    print(f"Points per wavelength: {c_s/source_freq/dx:.1f}")
    
    # Place source in center
    source_x, source_y = nx // 2, ny // 2
    
    # Place receivers radially from source (sparse configuration)
    # Distances: 5mm, 10mm, 15mm from source
    distances_m = np.array([0.005, 0.010, 0.015])[:n_receivers]
    angles = np.linspace(0, np.pi/4, n_receivers)  # Spread angles
    
    receiver_positions = []
    for i, d in enumerate(distances_m):
        angle = angles[i] if n_receivers > 1 else 0
        rx = int(source_x + d/dx * np.cos(angle))
        ry = int(source_y + d/dx * np.sin(angle))
        receiver_positions.append((rx, ry))
        print(f"  Receiver {i+1}: ({rx}, {ry}), distance = {d*1000:.1f} mm")
    
    # Setup extractor
    extractor = PhaseVelocityExtractor(sim)
    extractor.add_receivers(receiver_positions)
    
    # Simulation parameters
    n_steps = 4000
    source_duration = 5  # cycles
    dt = sim.dt
    
    print(f"\nRunning simulation for {n_steps} steps...")
    print(f"  Time step: {dt*1e6:.2f} us")
    print(f"  Total time: {n_steps*dt*1000:.1f} ms")
    
    # Run simulation
    for n in range(n_steps):
        t = n * dt
        
        # Add source (tone burst)
        if n < int(source_duration / source_freq / dt):
            sim.add_source(t, x_pos=source_x, y_pos=source_y,
                          amplitude=1e-6, f0=source_freq, source_type='tone_burst')
        
        # Step simulation
        sim.step()
        
        # Record at receivers
        extractor.record()
        
        if n % 500 == 0:
            print(f"  Step {n}/{n_steps} ({100*n/n_steps:.0f}%)")
    
    print("Simulation complete.")
    
    # Extract dispersion using two-point methods
    results = {
        'G_prime': G_prime,
        'eta': eta,
        'rho': rho,
        'receivers': receiver_positions,
        'distances': distances_m,
        'extractor': extractor
    }
    
    # Method 1: Receiver pairs (1-2, 2-3, 1-3)
    print("\nExtracting phase velocity...")
    
    freqs_list = []
    c_p_list = []
    labels = []
    
    for i in range(n_receivers - 1):
        for j in range(i + 1, n_receivers):
            try:
                freqs, c_p = extractor.two_point_method(i, j, freq_range=(20, 300))
                freqs_list.append(freqs)
                c_p_list.append(c_p)
                d_mm = (distances_m[j] - distances_m[i]) * 1000
                labels.append(f'R{i+1}-R{j+1} ({d_mm:.1f} mm)')
                print(f"  Pair R{i+1}-R{j+1}: extracted {np.sum(~np.isnan(c_p))} valid points")
            except Exception as e:
                print(f"  Pair R{i+1}-R{j+1}: failed - {e}")
    
    results['freqs'] = freqs_list
    results['phase_velocity'] = c_p_list
    results['labels'] = labels
    
    # Analytical reference
    omega_analytical = 2 * np.pi * np.linspace(20, 300, 100)
    c_p_analytical = analytical_phase_velocity(omega_analytical, G_prime, eta, rho)
    
    results['omega_analytical'] = omega_analytical
    results['c_p_analytical'] = c_p_analytical
    
    return results


def plot_validation_results(results, save_path='low_eta_validation.png'):
    """Plot validation comparison."""
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(f'Low-Viscosity Validation: G\'={results["G_prime"]} Pa, '
                 f'η={results["eta"]} Pa·s', fontsize=12)
    
    G_prime = results['G_prime']
    eta = results['eta']
    rho = results['rho']
    
    # Plot 1: Phase velocity dispersion
    ax1 = axes[0, 0]
    
    # Analytical curve
    f_analytical = results['omega_analytical'] / (2 * np.pi)
    ax1.plot(f_analytical, results['c_p_analytical'], 'k-', 
             linewidth=2, label='Analytical (Kelvin-Voigt)')
    
    # Simulated extraction
    colors = ['blue', 'red', 'green', 'purple']
    for i, (freqs, c_p, label) in enumerate(zip(results['freqs'], 
                                                 results['phase_velocity'],
                                                 results['labels'])):
        valid = ~np.isnan(c_p)
        ax1.scatter(freqs[valid], c_p[valid], c=colors[i % len(colors)], 
                   s=20, alpha=0.6, label=f'Simulated: {label}')
    
    # Elastic limit
    c_elastic = np.sqrt(G_prime / rho)
    ax1.axhline(c_elastic, color='gray', linestyle='--', 
                label=f'Elastic limit = {c_elastic:.2f} m/s')
    
    ax1.set_xlabel('Frequency (Hz)')
    ax1.set_ylabel('Phase velocity (m/s)')
    ax1.set_title('Phase Velocity Dispersion')
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Time signals at receivers
    ax2 = axes[0, 1]
    extractor = results['extractor']
    
    for i, signal in enumerate(extractor.time_signals):
        t = np.arange(len(signal)) * extractor.dt * 1000  # ms
        ax2.plot(t, np.array(signal) * 1e6, 
                label=f'Receiver {i+1} ({results["distances"][i]*1000:.1f} mm)',
                alpha=0.7)
    
    ax2.set_xlabel('Time (ms)')
    ax2.set_ylabel('Displacement (μm)')
    ax2.set_title('Receiver Signals')
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Error analysis
    ax3 = axes[1, 0]
    
    all_errors = []
    for freqs, c_p in zip(results['freqs'], results['phase_velocity']):
        valid = ~np.isnan(c_p)
        if np.sum(valid) > 0:
            # Interpolate analytical to match
            c_p_theory = analytical_phase_velocity(2*np.pi*freqs[valid], 
                                                   G_prime, eta, rho)
            error_pct = 100 * (c_p[valid] - c_p_theory) / c_p_theory
            all_errors.extend(error_pct)
            ax3.scatter(freqs[valid], error_pct, alpha=0.5, s=10)
    
    if all_errors:
        ax3.axhline(0, color='black', linestyle='-', linewidth=1)
        ax3.axhline(np.mean(all_errors), color='red', linestyle='--',
                   label=f'Mean error: {np.mean(all_errors):.1f}%')
        ax3.set_ylim(-50, 50)
    
    ax3.set_xlabel('Frequency (Hz)')
    ax3.set_ylabel('Error (%)')
    ax3.set_title('Extraction Error vs Analytical')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Attenuation analysis
    ax4 = axes[1, 1]
    
    # Extract amplitude envelope
    from scipy.signal import hilbert
    for i, sig_data in enumerate(extractor.time_signals):
        sig = np.array(sig_data)
        envelope = np.abs(hilbert(sig))
        t = np.arange(len(sig)) * extractor.dt * 1000
        ax4.semilogy(t, envelope * 1e6 + 1e-3, 
                    label=f'R{i+1}', alpha=0.7)
    
    # Expected attenuation
    f_center = 100  # Hz
    omega = 2 * np.pi * f_center
    G_mag = np.sqrt(G_prime**2 + (omega * eta)**2)
    k_double = omega * np.sqrt(rho / (2 * G_mag)) * np.sqrt(1 - G_prime/G_mag)
    attenuation_length = 1 / k_double if k_double > 0 else np.inf
    
    ax4.axvline(x=attenuation_length*1000, color='red', linestyle='--',
               label=f'Atten. length = {attenuation_length*1000:.1f} mm')
    
    ax4.set_xlabel('Time (ms)')
    ax4.set_ylabel('Envelope (μm)')
    ax4.set_title('Signal Attenuation')
    ax4.legend(fontsize=8)
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"\nSaved plot: {save_path}")
    
    return fig


def main():
    """Run validation suite."""
    
    print("LOW-VISCOSITY SPARSE SAMPLING VALIDATION")
    print("="*60)
    
    # Test case: Realistic tissue parameters
    test_cases = [
        # (G', eta, description)
        (2000, 0.5, "Soft tissue (low viscosity)"),
        (2000, 1.0, "Soft tissue (medium viscosity)"),
        (5000, 0.5, "Stiff tissue (low viscosity)"),
    ]
    
    all_results = []
    
    for G_prime, eta, desc in test_cases:
        print(f"\n\nTest case: {desc}")
        
        results = run_sparse_validation(
            G_prime=G_prime,
            eta=eta,
            rho=1000,
            n_receivers=3,
            source_freq=100
        )
        
        all_results.append(results)
        
        # Plot individual result
        plot_validation_results(results, 
                               save_path=f'validation_G{G_prime}_eta{eta}.png')
    
    print("\n" + "="*60)
    print("VALIDATION COMPLETE")
    print("="*60)
    
    # Summary
    print("\nSummary:")
    for i, (G_prime, eta, desc) in enumerate(test_cases):
        results = all_results[i]
        print(f"\n{desc}:")
        print(f"  Simulated vs analytical phase velocity comparison")
        print(f"  See: validation_G{G_prime}_eta{eta}.png")


if __name__ == '__main__':
    main()
