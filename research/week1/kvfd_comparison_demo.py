"""
Kelvin-Voigt vs Kelvin-Voigt Fractional Derivative (KVFD) Comparison

This script demonstrates why KVFD is needed for broad-frequency
shear wave elastography in biological tissues.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize


def kv_complex_modulus(G_prime, eta, omega):
    """
    Kelvin-Voigt complex modulus.
    
    G*(ω) = G' + i·ω·η
    """
    G_star = G_prime + 1j * omega * eta
    return G_star


def kvfd_complex_modulus(E0, tau, alpha, omega):
    """
    Kelvin-Voigt Fractional Derivative complex modulus.
    
    G*(ω) = E₀ · (1 + (i·ω·τ)^α)
    """
    G_star = E0 * (1 + (1j * omega * tau) ** alpha)
    return G_star


def phase_velocity(G_star, rho=1000):
    """
    Calculate phase velocity from complex modulus.
    
    c_s(ω) = √[2|G*| / (ρ(G'/|G*| + 1))]
    """
    G_mag = np.abs(G_star)
    G_real = np.real(G_star)
    c_s = np.sqrt(2 * G_mag / (rho * (G_real / G_mag + 1)))
    return c_s


def attenuation_coefficient(G_star, omega, rho=1000):
    """
    Calculate attenuation coefficient.
    
    α = ω·G'' / (2·ρ·c³)
    """
    c_s = phase_velocity(G_star, rho)
    G_imag = np.imag(G_star)
    alpha_att = omega * G_imag / (2 * rho * c_s**3)
    return alpha_att


def generate_synthetic_tissue_data(frequencies, E0=5000, tau=0.01, alpha=0.25, noise_level=0.02):
    """
    Generate synthetic dispersion data using KVFD model (simulating real tissue).
    """
    omega = 2 * np.pi * frequencies
    
    # True KVFD response
    G_star = kvfd_complex_modulus(E0, tau, alpha, omega)
    c_true = phase_velocity(G_star)
    alpha_true = attenuation_coefficient(G_star, omega)
    
    # Add measurement noise
    c_noisy = c_true * (1 + noise_level * np.random.randn(len(frequencies)))
    alpha_noisy = alpha_true * (1 + noise_level * np.random.randn(len(frequencies)))
    
    return c_noisy, alpha_noisy, c_true, alpha_true


def fit_kv_model(frequencies, c_measured):
    """
    Fit Kelvin-Voigt model to phase velocity data.
    Returns (G', η)
    """
    omega = 2 * np.pi * frequencies
    
    def cost_function(params):
        G_prime, eta = params
        G_star = kv_complex_modulus(G_prime, eta, omega)
        c_calc = phase_velocity(G_star)
        return np.sum((c_calc - c_measured)**2)
    
    result = minimize(cost_function, x0=[5000, 5], 
                     bounds=[(100, 50000), (0.1, 100)])
    return result.x


def fit_kvfd_model(frequencies, c_measured):
    """
    Fit KVFD model to phase velocity data.
    Returns (E₀, τ, α)
    """
    omega = 2 * np.pi * frequencies
    
    def cost_function(params):
        E0, tau, alpha = params
        G_star = kvfd_complex_modulus(E0, tau, alpha, omega)
        c_calc = phase_velocity(G_star)
        return np.sum((c_calc - c_measured)**2)
    
    result = minimize(cost_function, x0=[5000, 0.01, 0.2],
                     bounds=[(100, 50000), (1e-4, 1), (0.05, 0.95)])
    return result.x


def plot_comparison(frequencies, c_data, alpha_data, kv_params, kvfd_params):
    """
    Visual comparison of KV vs KVFD fits.
    """
    omega = 2 * np.pi * frequencies
    omega_fine = 2 * np.pi * np.linspace(frequencies[0], frequencies[-1], 200)
    
    # Calculate model predictions
    G_star_kv = kv_complex_modulus(kv_params[0], kv_params[1], omega_fine)
    c_kv = phase_velocity(G_star_kv)
    alpha_kv = attenuation_coefficient(G_star_kv, omega_fine)
    
    G_star_kvfd = kvfd_complex_modulus(kvfd_params[0], kvfd_params[1], 
                                        kvfd_params[2], omega_fine)
    c_kvfd = phase_velocity(G_star_kvfd)
    alpha_kvfd = attenuation_coefficient(G_star_kvfd, omega_fine)
    
    # Calculate misfits
    G_star_kv_data = kv_complex_modulus(kv_params[0], kv_params[1], omega)
    c_kv_data = phase_velocity(G_star_kv_data)
    misfit_kv = np.sqrt(np.mean((c_kv_data - c_data)**2))
    
    G_star_kvfd_data = kvfd_complex_modulus(kvfd_params[0], kvfd_params[1],
                                             kvfd_params[2], omega)
    c_kvfd_data = phase_velocity(G_star_kvfd_data)
    misfit_kvfd = np.sqrt(np.mean((c_kvfd_data - c_data)**2))
    
    # Create figure
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Phase velocity
    ax = axes[0, 0]
    ax.semilogx(frequencies, c_data, 'ko', markersize=6, label='Synthetic data')
    ax.semilogx(omega_fine/(2*np.pi), c_kv, 'r--', linewidth=2, 
                label=f'KV fit (RMS={misfit_kv:.2f} m/s)')
    ax.semilogx(omega_fine/(2*np.pi), c_kvfd, 'b-', linewidth=2,
                label=f'KVFD fit (RMS={misfit_kvfd:.2f} m/s)')
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Phase Velocity (m/s)')
    ax.set_title('Phase Velocity Dispersion')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Attenuation
    ax = axes[0, 1]
    ax.loglog(frequencies, alpha_data, 'ko', markersize=6, label='Synthetic data')
    ax.loglog(omega_fine/(2*np.pi), alpha_kv, 'r--', linewidth=2, label='KV')
    ax.loglog(omega_fine/(2*np.pi), alpha_kvfd, 'b-', linewidth=2, label='KVFD')
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Attenuation (Np/m)')
    ax.set_title('Attenuation vs Frequency')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Storage modulus
    ax = axes[1, 0]
    ax.loglog(omega_fine/(2*np.pi), np.real(G_star_kv)/1000, 'r--', 
              linewidth=2, label='KV')
    ax.loglog(omega_fine/(2*np.pi), np.real(G_star_kvfd)/1000, 'b-',
              linewidth=2, label='KVFD')
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel("G' (kPa)")
    ax.set_title('Storage Modulus')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Loss modulus
    ax = axes[1, 1]
    ax.loglog(omega_fine/(2*np.pi), np.imag(G_star_kv)/1000, 'r--',
              linewidth=2, label='KV')
    ax.loglog(omega_fine/(2*np.pi), np.imag(G_star_kvfd)/1000, 'b-',
              linewidth=2, label='KVFD')
    ax.set_xlabel('Frequency (Hz)')
    ax.setylabel('G" (kPa)')
    ax.set_title('Loss Modulus')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('kv_vs_kvfd_comparison.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    return misfit_kv, misfit_kvfd


def print_results(kv_params, kvfd_params, misfit_kv, misfit_kvfd):
    """
    Print comparison of fitted parameters.
    """
    print("\n" + "="*70)
    print("MODEL COMPARISON RESULTS")
    print("="*70)
    
    print("\n📊 KELVIN-VOIGT (2 parameters):")
    print(f"   G' (storage modulus) = {kv_params[0]:.1f} Pa")
    print(f"   η (viscosity)        = {kv_params[1]:.2f} Pa·s")
    print(f"   RMS misfit           = {misfit_kv:.2f} m/s")
    
    print("\n📊 KVFD (3 parameters):")
    print(f"   E₀ (quasi-static modulus) = {kvfd_params[0]:.1f} Pa")
    print(f"   τ (characteristic time)   = {kvfd_params[1]*1000:.2f} ms")
    print(f"   α (fractional order)      = {kvfd_params[2]:.3f}")
    print(f"   RMS misfit                = {misfit_kvfd:.2f} m/s")
    
    print("\n" + "="*70)
    print(f"✓ KVFD reduces misfit by {misfit_kv/misfit_kvfd:.1f}×")
    print("="*70)
    
    print("\n💡 KEY INSIGHTS:")
    print("   1. KV assumes linear frequency dependence")
    print("   2. KVFD captures power-law behavior (α ≈ 0.2-0.4)")
    print("   3. For broad bandwidth (>5× freq span), KVFD is essential")
    print("   4. For narrow bandwidth, KV is sufficient")


def main():
    """
    Main demonstration.
    """
    print("="*70)
    print("KELVIN-VOIGT vs KVFD MODEL COMPARISON")
    print("Shear Wave Dispersion in Soft Tissue")
    print("="*70)
    
    # Generate synthetic tissue data (using KVFD as ground truth)
    frequencies = np.array([20, 30, 50, 75, 100, 150, 200, 300, 400, 500])
    c_data, alpha_data, c_true, alpha_true = generate_synthetic_tissue_data(
        frequencies, E0=5000, tau=0.008, alpha=0.28, noise_level=0.02
    )
    
    print(f"\n📈 Generated synthetic data:")
    print(f"   Frequency range: {frequencies[0]}-{frequencies[-1]} Hz")
    print(f"   Bandwidth span: {frequencies[-1]/frequencies[0]:.1f}×")
    print(f"   Phase velocity range: {c_data.min():.2f}-{c_data.max():.2f} m/s")
    
    # Fit both models
    print("\n🔧 Fitting Kelvin-Voigt model...")
    kv_params = fit_kv_model(frequencies, c_data)
    
    print("🔧 Fitting KVFD model...")
    kvfd_params = fit_kvfd_model(frequencies, c_data)
    
    # Plot comparison
    misfit_kv, misfit_kvfd = plot_comparison(
        frequencies, c_data, alpha_data, kv_params, kvfd_params
    )
    
    # Print results
    print_results(kv_params, kvfd_params, misfit_kv, misfit_kvfd)
    
    return kv_params, kvfd_params


if __name__ == "__main__":
    kv_params, kvfd_params = main()
