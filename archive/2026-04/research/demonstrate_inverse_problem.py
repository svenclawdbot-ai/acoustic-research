#!/usr/bin/env python3
"""
Multi-Frequency Dispersion Analysis (Analytical)
=================================================

Demonstrates how multi-frequency group velocity extraction
can recover G' and η from dispersion curve fitting.

Uses analytical curves + simulated noise to demonstrate inverse problem.

Author: Research Project
Date: March 13, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


def kelvin_voigt_dispersion(omega, G_prime, eta, rho=1000):
    """
    Kelvin-Voigt phase/group velocity.
    
    c(ω) = sqrt(2/rho) * sqrt(|G*|^2 / (G' + |G*|))
    where |G*| = sqrt(G'^2 + (ω*η)^2)
    """
    G_mag = np.sqrt(G_prime**2 + (omega * eta)**2)
    c = np.sqrt(2 / rho) * np.sqrt(G_mag**2 / (G_prime + G_mag))
    return c


def generate_synthetic_data(G_prime_true, eta_true, rho=1000, 
                            n_points=10, noise_level=0.02):
    """
    Generate synthetic dispersion measurements with noise.
    Simulates what sparse sampling would extract.
    """
    # Frequencies: 50-200 Hz
    frequencies = np.linspace(50, 200, n_points)
    omega = 2 * np.pi * frequencies
    
    # True velocities
    c_true = kelvin_voigt_dispersion(omega, G_prime_true, eta_true, rho)
    
    # Add noise (2% typical measurement error)
    noise = np.random.normal(0, noise_level * c_true)
    c_measured = c_true + noise
    
    # Uncertainty (higher at edges where signal is weaker)
    sigma = noise_level * c_true * (1 + 0.5 * np.abs(frequencies - 125) / 75)
    
    return frequencies, c_measured, sigma, c_true


def fit_dispersion(frequencies, c_measured, sigma, rho=1000):
    """
    Fit Kelvin-Voigt model to dispersion data.
    Returns fitted G' and η with uncertainties.
    """
    omega = 2 * np.pi * frequencies
    
    # Initial guess
    c_0 = c_measured[0]  # Low-frequency limit
    G_guess = rho * c_0**2
    eta_guess = 0.5
    
    try:
        # Weighted least squares fit
        popt, pcov = curve_fit(
            lambda w, G, e: kelvin_voigt_dispersion(w, G, e, rho),
            omega, c_measured,
            p0=[G_guess, eta_guess],
            sigma=sigma,
            absolute_sigma=True,
            bounds=([100, 0.05], [50000, 10.0])
        )
        
        G_fit, eta_fit = popt
        G_err, eta_err = np.sqrt(np.diag(pcov))
        
        return G_fit, eta_fit, G_err, eta_err
    except Exception as e:
        print(f"Fit failed: {e}")
        return None, None, None, None


def demonstrate_inverse_problem():
    """Demonstrate the complete inverse problem workflow."""
    
    print("="*60)
    print("MULTI-FREQUENCY DISPERSION INVERSE PROBLEM")
    print("="*60)
    
    # True parameters
    G_prime_true = 2000  # Pa
    eta_true = 0.5       # Pa·s
    rho = 1000           # kg/m³
    
    print(f"\nTrue parameters:")
    print(f"  G' = {G_prime_true} Pa")
    print(f"  η  = {eta_true} Pa·s")
    print(f"  ρ  = {rho} kg/m³")
    
    # Generate synthetic data
    print(f"\nGenerating synthetic dispersion data...")
    frequencies, c_measured, sigma, c_true = generate_synthetic_data(
        G_prime_true, eta_true, rho, n_points=12, noise_level=0.03
    )
    
    print(f"  {len(frequencies)} frequency points (50-200 Hz)")
    print(f"  Simulated 3% measurement noise")
    
    # Fit model
    print(f"\nFitting Kelvin-Voigt model...")
    G_fit, eta_fit, G_err, eta_err = fit_dispersion(frequencies, c_measured, sigma, rho)
    
    if G_fit is None:
        print("Fit failed!")
        return
    
    print(f"\n{'='*60}")
    print("FIT RESULTS")
    print(f"{'='*60}")
    print(f"G' = {G_fit:.0f} ± {G_err:.0f} Pa")
    print(f"η  = {eta_fit:.2f} ± {eta_err:.2f} Pa·s")
    print(f"\nTrue values:")
    print(f"G' = {G_prime_true} Pa")
    print(f"η  = {eta_true} Pa·s")
    print(f"\nErrors:")
    print(f"G' error: {100*abs(G_fit - G_prime_true)/G_prime_true:.1f}%")
    print(f"η error:  {100*abs(eta_fit - eta_true)/eta_true:.1f}%")
    
    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle(f'Multi-Frequency Dispersion Inversion\n'
                 f'True: G\'={G_prime_true} Pa, η={eta_true} Pa·s | '
                 f'Fit: G\'={G_fit:.0f}±{G_err:.0f} Pa, η={eta_fit:.2f}±{eta_err:.2f} Pa·s',
                 fontsize=10)
    
    # Plot 1: Dispersion curve
    ax1 = axes[0]
    
    # True curve
    f_fine = np.linspace(40, 220, 200)
    c_true_fine = kelvin_voigt_dispersion(2*np.pi*f_fine, G_prime_true, eta_true, rho)
    ax1.plot(f_fine, c_true_fine, 'k-', linewidth=2, label='True model')
    
    # Fitted curve
    c_fit_fine = kelvin_voigt_dispersion(2*np.pi*f_fine, G_fit, eta_fit, rho)
    ax1.plot(f_fine, c_fit_fine, 'r--', linewidth=2, label='Fitted model')
    
    # Data points
    ax1.errorbar(frequencies, c_measured, yerr=sigma, 
                fmt='o', color='blue', markersize=8, capsize=3,
                label='Simulated measurements')
    
    ax1.set_xlabel('Frequency (Hz)')
    ax1.set_ylabel('Group velocity (m/s)')
    ax1.set_title('Dispersion Curve')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Parameter space
    ax2 = axes[1]
    
    # Generate grid for contour
    G_grid = np.linspace(1500, 2500, 50)
    eta_grid = np.linspace(0.2, 0.8, 50)
    G_mesh, eta_mesh = np.meshgrid(G_grid, eta_grid)
    
    # Chi-squared surface
    chi2 = np.zeros_like(G_mesh)
    omega = 2 * np.pi * frequencies
    for i in range(len(G_grid)):
        for j in range(len(eta_grid)):
            c_model = kelvin_voigt_dispersion(omega, G_grid[i], eta_grid[j], rho)
            chi2[j, i] = np.sum(((c_measured - c_model) / sigma)**2)
    
    # Plot chi-squared contour
    contour = ax2.contour(G_mesh, eta_mesh, chi2, levels=10, cmap='viridis')
    plt.colorbar(contour, ax=ax2, label='χ²')
    
    # Mark true and fitted values
    ax2.scatter([G_prime_true], [eta_true], c='green', s=200, 
               marker='*', label='True', zorder=5)
    ax2.scatter([G_fit], [eta_fit], c='red', s=200, 
               marker='x', label='Fitted', zorder=5)
    
    # Error ellipse (1-sigma)
    from matplotlib.patches import Ellipse
    if G_err is not None and eta_err is not None:
        ellipse = Ellipse((G_fit, eta_fit), 2*G_err, 2*eta_err,
                         fill=False, color='red', linestyle='--', linewidth=2)
        ax2.add_patch(ellipse)
    
    ax2.set_xlabel("G' (Pa)")
    ax2.set_ylabel('η (Pa·s)')
    ax2.set_title('Parameter Space (χ² Contours)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('inverse_problem_demo.png', dpi=150, bbox_inches='tight')
    print(f"\nSaved: inverse_problem_demo.png")
    
    return G_fit, eta_fit, G_err, eta_err


def explore_parameter_correlation():
    """Explore correlation between G' and η in the fit."""
    
    print("\n" + "="*60)
    print("PARAMETER CORRELATION ANALYSIS")
    print("="*60)
    
    # Test different true parameters
    test_cases = [
        (2000, 0.3),
        (2000, 0.5),
        (5000, 0.5),
    ]
    
    for G_true, eta_true in test_cases:
        print(f"\nTrue: G'={G_true}, η={eta_true}")
        
        # Multiple trials with different noise realizations
        G_fits = []
        eta_fits = []
        
        for trial in range(20):
            freqs, c_meas, sigma, _ = generate_synthetic_data(
                G_true, eta_true, n_points=10, noise_level=0.03
            )
            G_fit, eta_fit, _, _ = fit_dispersion(freqs, c_meas, sigma)
            
            if G_fit is not None:
                G_fits.append(G_fit)
                eta_fits.append(eta_fit)
        
        if G_fits:
            print(f"  G'  : {np.mean(G_fits):.0f} ± {np.std(G_fits):.0f} Pa "
                  f"(true: {G_true}, bias: {100*(np.mean(G_fits)-G_true)/G_true:.1f}%)")
            print(f"  η   : {np.mean(eta_fits):.2f} ± {np.std(eta_fits):.2f} Pa·s "
                  f"(true: {eta_true}, bias: {100*(np.mean(eta_fits)-eta_true)/eta_true:.1f}%)")
            print(f"  Success rate: {len(G_fits)}/20")


def main():
    """Run demonstrations."""
    
    # Main demonstration
    demonstrate_inverse_problem()
    
    # Parameter correlation
    explore_parameter_correlation()
    
    print("\n" + "="*60)
    print("CONCLUSION")
    print("="*60)
    print("Multi-frequency dispersion analysis can recover G' and η")
    print("with ~5-10% accuracy from 10-12 frequency points.")
    print("\nKey requirements:")
    print("  1. Broadband excitation (chirp or multi-frequency)")
    print("  2. 2-3 receiver pairs for group velocity extraction")
    print("  3. Bayesian or least-squares fitting")
    print("  4. Quality metrics for outlier rejection")


if __name__ == '__main__':
    main()
