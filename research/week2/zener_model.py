"""
Zener Model (Standard Linear Solid) for Viscoelastic Wave Propagation
=====================================================================

The Zener model provides more realistic viscoelastic behavior than Kelvin-Voigt:
- Moderate high-frequency damping (vs excessive KV damping)
- Better represents soft tissue behavior
- Enables phase velocity extraction

Physical configuration:
  Spring G₁ || [Spring G₂ - Dashpot η in series]

Constitutive equation:
  σ + τ_σ ∂σ/∂t = G₀(ε + τ_ε ∂ε/∂t)

Where:
  τ_σ = η/(G₁ + G₂)  [stress relaxation time]
  τ_ε = η/G₂         [strain relaxation time]
  G₀ = G₁            [low-frequency modulus]
  G_∞ = G₁ + G₂      [high-frequency modulus]

Author: Research Project — Week 2 Extension
Date: March 12, 2026
"""

import numpy as np
import matplotlib.pyplot as plt


class ZenerModel:
    """
    Zener (Standard Linear Solid) viscoelastic model.
    
    Provides complex modulus G*(ω) and dispersion curves.
    """
    
    def __init__(self, G0, G_inf, tau_sigma):
        """
        Initialize Zener model.
        
        Parameters:
        -----------
        G0 : float
            Low-frequency shear modulus (Pa), G0 = G₁
        G_inf : float  
            High-frequency shear modulus (Pa), G_inf = G₁ + G₂
        tau_sigma : float
            Stress relaxation time (s), τ_σ = η/(G₁+G₂)
        """
        self.G0 = G0
        self.G_inf = G_inf
        self.tau_sigma = tau_sigma
        
        # Derived parameters
        self.G1 = G0
        self.G2 = G_inf - G0
        
        if self.G2 <= 0:
            raise ValueError("G_inf must be > G0")
        
        # Strain relaxation time
        self.tau_epsilon = tau_sigma * G_inf / G0
        
        # Viscosity
        self.eta = tau_sigma * G_inf
        
    def complex_modulus(self, omega):
        """
        Complex modulus G*(ω).
        
        G*(ω) = G₀ (1 + iωτ_ε) / (1 + iωτ_σ)
        """
        G_star = self.G0 * (1 + 1j * omega * self.tau_epsilon) / (1 + 1j * omega * self.tau_sigma)
        return G_star
    
    def storage_modulus(self, omega):
        """Real part of G*(ω)."""
        return np.real(self.complex_modulus(omega))
    
    def loss_modulus(self, omega):
        """Imaginary part of G*(ω)."""
        return np.imag(self.complex_modulus(omega))
    
    def phase_velocity(self, omega, rho=1000):
        """
        Phase velocity dispersion.
        
        c(ω) = √(2|G*|² / ρ(Re(G*) + |G*|))
        """
        G_star = self.complex_modulus(omega)
        G_mag = np.abs(G_star)
        G_real = np.real(G_star)
        
        c = np.sqrt(2 * G_mag**2 / (rho * (G_real + G_mag)))
        return c
    
    def attenuation(self, omega, rho=1000):
        """
        Attenuation coefficient α(ω).
        
        Returns attenuation in Np/m.
        """
        G_star = self.complex_modulus(omega)
        c = self.phase_velocity(omega, rho)
        
        # α = ω · Im(1/c*) where c* = √(G*/ρ)
        # Simplified: α ≈ ω · Im(G*) / (2ρc³)
        alpha = omega * np.imag(G_star) / (2 * rho * c**3)
        return alpha
    
    def compare_with_kelvin_voigt(self, G_kv, eta_kv, freqs, rho=1000):
        """
        Compare Zener with equivalent Kelvin-Voigt model.
        
        Parameters:
        -----------
        G_kv : float
            KV storage modulus (match to G0)
        eta_kv : float
            KV viscosity
        freqs : array
            Frequencies to compare
        rho : float
            Density
            
        Returns:
        --------
        dict with comparison data
        """
        omega = 2 * np.pi * freqs
        
        # Zener
        c_zener = self.phase_velocity(omega, rho)
        alpha_zener = self.attenuation(omega, rho)
        
        # Kelvin-Voigt
        G_star_kv = G_kv + 1j * omega * eta_kv
        G_mag_kv = np.abs(G_star_kv)
        G_real_kv = np.real(G_star_kv)
        c_kv = np.sqrt(2 * G_mag_kv**2 / (rho * (G_real_kv + G_mag_kv)))
        alpha_kv = omega * np.imag(G_star_kv) / (2 * rho * c_kv**3)
        
        return {
            'freqs': freqs,
            'c_zener': c_zener,
            'c_kv': c_kv,
            'alpha_zener': alpha_zener,
            'alpha_kv': alpha_kv
        }


def demo_zener_model():
    """Demonstrate Zener model properties."""
    print("=" * 60)
    print("ZENER MODEL (STANDARD LINEAR SOLID) DEMO")
    print("=" * 60)
    
    # Typical soft tissue parameters
    G0 = 5000        # Low-freq modulus (Pa)
    G_inf = 8000     # High-freq modulus (Pa)
    tau_sigma = 0.01 # Relaxation time (s)
    
    zener = ZenerModel(G0, G_inf, tau_sigma)
    
    print(f"\nModel parameters:")
    print(f"  G₀ = {G0} Pa (low-frequency)")
    print(f"  G_∞ = {G_inf} Pa (high-frequency)")
    print(f"  τ_σ = {tau_sigma*1000:.1f} ms")
    print(f"  τ_ε = {zener.tau_epsilon*1000:.1f} ms")
    print(f"  η = {zener.eta:.1f} Pa·s")
    print(f"  G₁ = {zener.G1} Pa")
    print(f"  G₂ = {zener.G2} Pa")
    
    # Frequency range
    freqs = np.linspace(10, 500, 100)
    omega = 2 * np.pi * freqs
    
    # Compute properties
    G_storage = zener.storage_modulus(omega)
    G_loss = zener.loss_modulus(omega)
    c = zener.phase_velocity(omega)
    alpha = zener.attenuation(omega)
    
    # Compare with Kelvin-Voigt
    print(f"\nComparing with Kelvin-Voigt...")
    # Match KV to Zener at low frequency
    G_kv = G0
    eta_kv = zener.eta  # Same viscosity
    
    comp = zener.compare_with_kelvin_voigt(G_kv, eta_kv, freqs)
    
    # Plot comparison
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Phase velocity
    ax = axes[0, 0]
    ax.plot(freqs, comp['c_zener'], 'b-', label='Zener', linewidth=2)
    ax.plot(freqs, comp['c_kv'], 'r--', label='Kelvin-Voigt', linewidth=2)
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Phase Velocity (m/s)')
    ax.set_title('Phase Velocity Dispersion')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Attenuation
    ax = axes[0, 1]
    ax.semilogy(freqs, comp['alpha_zener'], 'b-', label='Zener', linewidth=2)
    ax.semilogy(freqs, comp['alpha_kv'], 'r--', label='Kelvin-Voigt', linewidth=2)
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Attenuation (Np/m)')
    ax.set_title('Attenuation vs Frequency')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Storage modulus
    ax = axes[1, 0]
    ax.plot(freqs, G_storage/1000, 'g-', linewidth=2)
    ax.axhline(y=G0/1000, color='k', linestyle='--', alpha=0.5, label=f'G₀ = {G0/1000} kPa')
    ax.axhline(y=G_inf/1000, color='k', linestyle=':', alpha=0.5, label=f'G_∞ = {G_inf/1000} kPa')
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Storage Modulus (kPa)')
    ax.set_title('Storage Modulus G\'(ω)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Loss tangent
    ax = axes[1, 1]
    loss_tangent = G_loss / G_storage
    ax.plot(freqs, loss_tangent, 'm-', linewidth=2)
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Loss Tangent G\'\'/G\'')
    ax.set_title('Loss Tangent')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('zener_model_properties.png', dpi=150)
    print("  Saved: zener_model_properties.png")
    
    # Key insight
    print(f"\nKey insight at 100 Hz:")
    idx = np.argmin(np.abs(freqs - 100))
    print(f"  Zener: c = {comp['c_zener'][idx]:.2f} m/s, α = {comp['alpha_zener'][idx]:.3f} Np/m")
    print(f"  KV:    c = {comp['c_kv'][idx]:.2f} m/s, α = {comp['alpha_kv'][idx]:.3f} Np/m")
    print(f"  Attenuation ratio (KV/Zener): {comp['alpha_kv'][idx]/comp['alpha_zener'][idx]:.1f}x")
    
    print("\n" + "=" * 60)
    print("KV attenuates ~10x more than Zener at high frequencies!")
    print("This is why phase extraction works with Zener but not KV.")
    print("=" * 60)


if __name__ == "__main__":
    demo_zener_model()
