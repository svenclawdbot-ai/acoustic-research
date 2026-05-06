#!/usr/bin/env python3
"""
Validate Zener Model Derivation
===============================

Compares analytically derived dispersion relations against 2D FDTD simulation data.

Run this after completing the derivation worksheet to verify your formulas.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# Simulation parameters (match your 2D simulation)
# Zener model: G_r (parallel spring) || [G_1 (series spring) - η (dashpot)]
# At low freq: G_0 = G_r (dashpot flows, series spring inactive)
# At high freq: G_inf = G_r + G_1 (dashpot frozen, both springs active)
G_r = 5000.0         # Pa (relaxed modulus, parallel spring)
G_inf = 8000.0       # Pa (unrelaxed modulus, G_r + G_1)
tau_sigma = 0.001    # s (stress relaxation time)
rho = 1000.0         # kg/m³

# Derived parameters
G_1 = G_inf - G_r    # Series spring in Maxwell branch
G_0 = G_r            # Relaxed modulus (low frequency limit)
tau_epsilon = tau_sigma * G_inf / G_r  # Strain relaxation time
eta = tau_sigma * G_1  # Dashpot viscosity

print("=" * 60)
print("Zener Model Validation: Theory vs Simulation")
print("=" * 60)
print(f"\nParameters:")
print(f"  G_r (parallel spring) = {G_r} Pa")
print(f"  G_1 (series spring) = {G_1} Pa")
print(f"  G_inf = G_r + G_1 = {G_inf} Pa (unrelaxed, high freq)")
print(f"  G_0 = G_r = {G_r} Pa (relaxed, low freq)")
print(f"  η = {eta:.3f} Pa·s")
print(f"  τσ = {tau_sigma*1000:.2f} ms")
print(f"  τε = {tau_epsilon*1000:.2f} ms")
print(f"  τε = {tau_epsilon*1000:.2f} ms")
print(f"  ρ = {rho} kg/m³")

# Frequency range
f = np.linspace(10, 500, 200)  # Hz
omega = 2 * np.pi * f

# ============================================================================
# YOUR DERIVED FORMULAS — implement these based on your worksheet
# ============================================================================

def zener_complex_modulus(omega, G_r, G_1, tau_sigma):
    """
    Compute complex modulus G*(ω) = G' + iG''
    
    Zener model: G_r || [G_1 - η] (Maxwell branch)
    
    G* = G_r + G_1*(iωτσ)/(1 + iωτσ)
    
    After rationalizing:
    G' = [G_r + (G_r + G_1)*(ωτσ)²] / [1 + (ωτσ)²]
    G'' = [G_1*ωτσ] / [1 + (ωτσ)²]
    """
    omega_tau = omega * tau_sigma
    omega_tau_sq = omega_tau ** 2
    
    G_prime = (G_r + (G_r + G_1) * omega_tau_sq) / (1 + omega_tau_sq)
    G_double_prime = (G_1 * omega_tau) / (1 + omega_tau_sq)
    
    return G_prime, G_double_prime


def zener_phase_velocity(omega, G_prime, G_double_prime, rho):
    """
    Compute phase velocity cₚ(ω)
    
    TODO: Implement your derived formula:
    
    |G*| = √(G'² + G''²)
    cₚ(ω) = √[2|G*|² / (ρ(|G*| + G'))]
    """
    G_mag = np.sqrt(G_prime**2 + G_double_prime**2)
    
    # YOUR CODE HERE
    c_p = np.sqrt(2 * G_mag**2 / (rho * (G_mag + G_prime)))
    
    return c_p


def zener_attenuation(omega, G_prime, G_double_prime, rho):
    """
    Compute attenuation α(ω) in Np/m
    
    TODO: Implement your derived formula:
    
    α(ω) = ω·√[ρ(|G*| - G') / (2|G*|²)]
    """
    G_mag = np.sqrt(G_prime**2 + G_double_prime**2)
    
    # YOUR CODE HERE
    alpha = omega * np.sqrt(rho * (G_mag - G_prime) / (2 * G_mag**2))
    
    return alpha


# ============================================================================
# Compute theoretical curves
# ============================================================================

G_prime, G_double_prime = zener_complex_modulus(omega, G_r, G_1, tau_sigma)
c_p_theory = zener_phase_velocity(omega, G_prime, G_double_prime, rho)
alpha_theory = zener_attenuation(omega, G_prime, G_double_prime, rho)

# Convert attenuation to dB/m for easier interpretation
alpha_dB_theory = alpha_theory * 20 * np.log10(np.e)  # ≈ 8.686 * alpha_Np

# ============================================================================
# Expected limiting values
# ============================================================================

c_0 = np.sqrt(G_0 / rho)      # Low-frequency limit
c_inf = np.sqrt(G_inf / rho)  # High-frequency limit

print(f"\nLimiting velocities:")
print(f"  c₀ = √(G₀/ρ) = {c_0:.3f} m/s (low frequency)")
print(f"  c∞ = √(G∞/ρ) = {c_inf:.3f} m/s (high frequency)")
print(f"  Velocity ratio: c∞/c₀ = {c_inf/c_0:.3f}")

# Peak attenuation frequency
f_peak = 1 / (2 * np.pi * tau_sigma)
print(f"\nPeak attenuation at f = 1/(2πτσ) = {f_peak:.1f} Hz")

# ============================================================================
# Load simulation data (if available)
# ============================================================================

simulation_data_available = False
c_p_sim = None
alpha_sim = None

# Try to load from existing simulation output
try:
    # Look for saved dispersion data from k-ω analysis
    import os
    sim_files = [f for f in os.listdir('.') if 'dispersion' in f and f.endswith('.npz')]
    if sim_files:
        data = np.load(sim_files[0])
        f_sim = data['frequencies']
        c_p_sim = data['phase_velocity']
        alpha_sim = data.get('attenuation', None)
        simulation_data_available = True
        print(f"\n✓ Loaded simulation data from {sim_files[0]}")
except Exception as e:
    print(f"\n⚠ No simulation data found: {e}")
    print("  Run shear_wave_2d_zener.py with dispersion extraction to generate data.")

# ============================================================================
# Plotting
# ============================================================================

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Storage and Loss Modulus
ax = axes[0, 0]
ax.semilogy(f, G_prime, 'b-', linewidth=2, label="G' (storage)")
ax.semilogy(f, G_double_prime, 'r-', linewidth=2, label="G'' (loss)")
ax.axhline(G_inf, color='b', linestyle='--', alpha=0.5, label=f'G∞ = {G_inf}')
ax.axhline(G_0, color='b', linestyle=':', alpha=0.5, label=f'G₀ = {G_0}')
ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Modulus (Pa)')
ax.set_title('Complex Modulus')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 2: Phase Velocity
ax = axes[0, 1]
ax.plot(f, c_p_theory, 'b-', linewidth=2, label='Theory')
ax.axhline(c_0, color='g', linestyle='--', alpha=0.5, label=f'c₀ = {c_0:.2f} m/s')
ax.axhline(c_inf, color='r', linestyle='--', alpha=0.5, label=f'c∞ = {c_inf:.2f} m/s')
if simulation_data_available and c_p_sim is not None:
    ax.plot(f_sim, c_p_sim, 'ro', markersize=4, label='Simulation')
ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Phase Velocity (m/s)')
ax.set_title('Phase Velocity vs Frequency')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 3: Attenuation
ax = axes[1, 0]
ax.semilogy(f, alpha_dB_theory, 'b-', linewidth=2, label='Theory')
ax.axvline(f_peak, color='r', linestyle='--', alpha=0.5, label=f'Peak at {f_peak:.0f} Hz')
if simulation_data_available and alpha_sim is not None:
    ax.semilogy(f_sim, alpha_sim * 8.686, 'ro', markersize=4, label='Simulation')
ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Attenuation (dB/m)')
ax.set_title('Attenuation vs Frequency')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 4: Loss Tangent
ax = axes[1, 1]
loss_tangent = G_double_prime / G_prime
ax.plot(f, loss_tangent, 'b-', linewidth=2)
ax.axvline(f_peak, color='r', linestyle='--', alpha=0.5, label=f'Peak at {f_peak:.0f} Hz')
ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('tan(δ) = G''/G\'')
ax.set_title('Loss Tangent')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('zener_derivation_validation.png', dpi=150, bbox_inches='tight')
print(f"\n✓ Saved validation plot to: zener_derivation_validation.png")

# ============================================================================
# Summary table
# ============================================================================

print("\n" + "=" * 60)
print("Validation Summary")
print("=" * 60)

test_frequencies = [50, 100, 159, 200, 300]  # Hz including peak
print(f"\n{'f (Hz)':<10} {'cₚ (m/s)':<12} {'α (dB/m)':<12} {'|G*| (Pa)':<12}")
print("-" * 50)

for f_test in test_frequencies:
    idx = np.argmin(np.abs(f - f_test))
    print(f"{f[idx]:<10.0f} {c_p_theory[idx]:<12.3f} {alpha_dB_theory[idx]:<12.2f} {np.sqrt(G_prime[idx]**2 + G_double_prime[idx]**2):<12.1f}")

# Check limiting behavior
print(f"\nLimit Check:")
print(f"  At f=10 Hz:  cₚ = {c_p_theory[0]:.3f} m/s (expected c₀ = {c_0:.3f})")
print(f"  At f=500 Hz: cₚ = {c_p_theory[-1]:.3f} m/s (expected c∞ = {c_inf:.3f})")

print("\n" + "=" * 60)
print("Your task: Verify these numbers match your derived formulas!")
print("=" * 60)

plt.show()
