#!/usr/bin/env python3
"""
Kelvin-Voigt Viscoelastic Dispersion Analysis
Plots phase velocity and attenuation vs frequency
"""

import numpy as np
import matplotlib.pyplot as plt

# Tissue-like parameters (realistic values from literature)
mu = 2000.0        # Shear modulus (Pa)
eta = 0.5          # Viscosity (Pa·s) - realistic tissue value
rho = 1000.0       # Density (kg/m³)

# Frequency range
f = np.linspace(10, 500, 1000)     # Hz
omega = 2 * np.pi * f              # rad/s

# Complex modulus
G_star = mu + 1j * omega * eta
G_mag = np.abs(G_star)
phi = np.arctan2(omega * eta, mu)  # phase angle

# Complex wave number components
k_mag = omega * np.sqrt(rho / G_mag)
k_prime = k_mag * np.cos(phi / 2)   # propagation (real part)
k_double = k_mag * np.sin(phi / 2)  # attenuation (imag part)

# Phase velocity
phase_velocity = omega / k_prime

# Attenuation coefficient (Nepers/m)
attenuation = k_double

# Elastic limit (for reference)
c_elastic = np.sqrt(mu / rho)

# Create figure
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle('Kelvin-Voigt Viscoelastic Dispersion\n' + 
             f'μ = {mu:.0f} Pa, η = {eta:.1f} Pa·s, ρ = {rho:.0f} kg/m³', 
             fontsize=12)

# Plot 1: Phase velocity vs frequency
ax1 = axes[0, 0]
ax1.semilogy(f, phase_velocity, 'b-', linewidth=2, label='Phase velocity c_p(ω)')
ax1.axhline(c_elastic, color='r', linestyle='--', label=f'Elastic limit √(μ/ρ) = {c_elastic:.1f} m/s')
ax1.set_xlabel('Frequency (Hz)')
ax1.set_ylabel('Phase velocity (m/s)')
ax1.set_title('Phase Velocity Dispersion')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Attenuation vs frequency
ax2 = axes[0, 1]
ax2.loglog(f, attenuation, 'g-', linewidth=2)
ax2.set_xlabel('Frequency (Hz)')
ax2.set_ylabel('Attenuation α (Nepers/m)')
ax2.set_title('Frequency-Dependent Attenuation')
ax2.grid(True, alpha=0.3)

# Add α ∝ ω² line for comparison at low frequencies
f_low = f[f < 100]
alpha_ref = attenuation[f < 100][0] * (f_low / f_low[0])**2
ax2.loglog(f_low, alpha_ref, 'r--', alpha=0.5, label='α ∝ ω² (low freq)')
ax2.legend()

# Plot 3: Complex modulus magnitude
ax3 = axes[1, 0]
ax3.semilogy(f, G_mag, 'purple', linewidth=2, label='|G*|')
ax3.axhline(mu, color='r', linestyle='--', label=f'Storage modulus μ = {mu:.0f} Pa')
ax3.set_xlabel('Frequency (Hz)')
ax3.set_ylabel('|G*| (Pa)')
ax3.set_title('Complex Modulus Magnitude')
ax3.legend()
ax3.grid(True, alpha=0.3)

# Plot 4: Wavenumber components
ax4 = axes[1, 1]
ax4.semilogy(f, k_prime, 'b-', linewidth=2, label="k' (propagation)")
ax4.semilogy(f, k_double, 'r-', linewidth=2, label='k" (attenuation)')
ax4.set_xlabel('Frequency (Hz)')
ax4.set_ylabel('Wavenumber (rad/m)')
ax4.set_title('Complex Wavenumber Components')
ax4.legend()
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('kelvin_voigt_dispersion.png', dpi=150, bbox_inches='tight')
print("Saved: kelvin_voigt_dispersion.png")

# Print key values at specific frequencies
print("\n--- Key Values ---")
for freq in [50, 100, 200]:
    idx = np.argmin(np.abs(f - freq))
    print(f"\nf = {freq} Hz:")
    print(f"  Phase velocity: {phase_velocity[idx]:.2f} m/s")
    print(f"  Attenuation:    {attenuation[idx]:.4f} Np/m ({attenuation[idx]*8.686:.2f} dB/m)")
    print(f"  Wavelength:     {2*np.pi/k_prime[idx]:.2f} mm")

# Compare with elastic limit
print(f"\nElastic limit (low freq): c = {c_elastic:.2f} m/s")

# Show dispersion strength
print(f"\n--- Dispersion Effect ---")
print(f"Velocity at 50 Hz:  {phase_velocity[np.argmin(np.abs(f-50))]:.2f} m/s")
print(f"Velocity at 200 Hz: {phase_velocity[np.argmin(np.abs(f-200))]:.2f} m/s")
print(f"Ratio: {phase_velocity[np.argmin(np.abs(f-200))]/phase_velocity[np.argmin(np.abs(f-50))]:.2f}x")

plt.show()
