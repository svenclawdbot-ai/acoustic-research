import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator

# =============================================================================
# SOIL IMPEDANCE SPECTROSCOPY MODEL
# =============================================================================
# Physical constants
epsilon_0 = 8.854e-12  # F/m

# =============================================================================
# SOIL STATE DEFINITIONS
# =============================================================================
# For agricultural soil impedance spectroscopy, the dominant effect at low
# frequencies is electrode polarization (modeled as a Constant Phase Element).
# At high frequencies (>100 kHz), bulk dielectric properties dominate.

soil_states = {
    "dry_clay": {
        "vwc": 0.05,           # volumetric water content
        "sigma_bulk": 0.0003,  # S/m (very low conductivity)
        "rho_bulk": 3333,      # Ohm.m
        "epsilon_r": 10,       # relative permittivity
        "cpe_Q": 1e-6,         # CPE coefficient
        "cpe_alpha": 0.65,     # CPE exponent (0.5-0.8 typical)
        "color": "#8B4513",    # saddle brown
    },
    "moderate_loam": {
        "vwc": 0.25,
        "sigma_bulk": 0.01,    # S/m
        "rho_bulk": 100,       # Ohm.m
        "epsilon_r": 20,
        "cpe_Q": 3e-6,
        "cpe_alpha": 0.70,
        "color": "#CD853F",    # peru
    },
    "saturated_loam": {
        "vwc": 0.45,
        "sigma_bulk": 0.08,    # S/m
        "rho_bulk": 12.5,      # Ohm.m
        "epsilon_r": 30,
        "cpe_Q": 8e-6,
        "cpe_alpha": 0.75,
        "color": "#4682B4",    # steel blue
    },
}

# Wenner array geometric factor
a = 0.05  # 5 cm electrode spacing
K_g = 2 * np.pi * a  # ~0.314 m

def R_from_rho(rho, K_g):
    """Convert resistivity to resistance for Wenner array."""
    return rho / K_g

def z_bulk_resistive(freq, rho, K_g):
    """Purely resistive bulk soil impedance."""
    R = rho / K_g
    return R + 0j

def z_cpe(freq, Q, alpha):
    """Constant Phase Element impedance.
    Z_CPE = 1 / (Q * (j*omega)^alpha)
    """
    omega = 2 * np.pi * freq
    # (j*omega)^alpha = omega^alpha * (cos(alpha*pi/2) + j*sin(alpha*pi/2))
    mag = omega ** alpha
    phase_factor = np.exp(1j * alpha * np.pi / 2)
    return 1 / (Q * mag * phase_factor)

def z_soil(freq, state):
    """Total soil impedance: bulk resistance in series with CPE (electrode polarization).
    
    In a 4-electrode Wenner measurement:
    - Current electrodes inject I
    - Potential electrodes measure V
    - The CPE effect appears in series with the bulk
    """
    s = soil_states[state]
    R_bulk = s["rho_bulk"] / K_g
    Z_cpe = z_cpe(freq, s["cpe_Q"], s["cpe_alpha"])
    
    # Series combination: Z_total = R_bulk + Z_CPE
    # At low freq, Z_CPE dominates (large phase)
    # At high freq, Z_CPE becomes small, R_bulk dominates
    return R_bulk + Z_cpe

# =============================================================================
# FREQUENCY SWEEP
# =============================================================================
freq = np.logspace(0, 6, 500)  # 1 Hz to 1 MHz

fig, axes = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle("Soil Impedance Spectroscopy — Wenner Array (a=5cm)\n" + 
             "Model: R_bulk + CPE (electrode polarization)", fontsize=12)

# --- Plot 1: |Z| vs frequency ---
ax1 = axes[0, 0]
for name, props in soil_states.items():
    Z = z_soil(freq, name)
    ax1.loglog(freq, np.abs(Z), color=props["color"], lw=2, 
               label=f"{name.replace('_', ' ').title()} (VWC={props['vwc']:.0%})")

ax1.set_xlabel("Frequency (Hz)")
ax1.set_ylabel("|Z| (Ω)")
ax1.set_title("Impedance Magnitude vs Frequency")
ax1.legend(loc="upper right", fontsize=8)
ax1.grid(True, which="both", ls="--", alpha=0.5)
ax1.axvline(1e3, color="gray", ls=":", alpha=0.7, label="1 kHz")
ax1.axvline(1e5, color="gray", ls="-.", alpha=0.7, label="100 kHz")

# --- Plot 2: Phase vs frequency ---
ax2 = axes[0, 1]
for name, props in soil_states.items():
    Z = z_soil(freq, name)
    phase_deg = np.angle(Z, deg=True)
    ax2.semilogx(freq, phase_deg, color=props["color"], lw=2,
                 label=f"{name.replace('_', ' ').title()}")

ax2.set_xlabel("Frequency (Hz)")
ax2.set_ylabel("Phase (degrees)")
ax2.set_title("Phase Angle vs Frequency")
ax2.set_ylim(-95, 5)
ax2.legend(loc="lower right", fontsize=8)
ax2.grid(True, which="both", ls="--", alpha=0.5)
ax2.axhline(0, color="black", ls="-", alpha=0.3)
ax2.axvline(1e3, color="gray", ls=":", alpha=0.7)
ax2.axvline(1e5, color="gray", ls="-.", alpha=0.7)

# --- Plot 3: Cole-Cole plot (Imag vs Real) ---
ax3 = axes[1, 0]
for name, props in soil_states.items():
    Z = z_soil(freq, name)
    # Plot -Im(Z) vs Re(Z) (standard electrochemistry convention)
    ax3.plot(np.real(Z), -np.imag(Z), color=props["color"], lw=2,
             label=f"{name.replace('_', ' ').title()}")
    # Mark direction: low freq → high freq
    ax3.annotate("", xy=(np.real(Z)[-1], -np.imag(Z)[-1]),
                xytext=(np.real(Z)[-50], -np.imag(Z)[-50]),
                arrowprops=dict(arrowstyle="->", color=props["color"], alpha=0.5))

ax3.set_xlabel("Re(Z) (Ω)")
ax3.set_ylabel("-Im(Z) (Ω)")
ax3.set_title("Cole-Cole Plot (Nyquist)")
ax3.legend(loc="upper right", fontsize=8)
ax3.grid(True, ls="--", alpha=0.5)

# --- Plot 4: Conductivity vs frequency ---
ax4 = axes[1, 1]
for name, props in soil_states.items():
    Z = z_soil(freq, name)
    # Apparent conductivity: sigma_a = K_g / |Z|
    sigma_a = K_g / np.abs(Z)
    ax4.loglog(freq, sigma_a, color=props["color"], lw=2,
               label=f"{name.replace('_', ' ').title()}")
    # True bulk conductivity (horizontal line)
    ax4.axhline(props["sigma_bulk"], color=props["color"], ls="--", alpha=0.5)

ax4.set_xlabel("Frequency (Hz)")
ax4.set_ylabel("σ_a (S/m)")
ax4.set_title("Apparent Conductivity vs Frequency")
ax4.legend(loc="lower right", fontsize=8)
ax4.grid(True, which="both", ls="--", alpha=0.5)

plt.tight_layout()
plt.savefig("soil_impedance_spectra.png", dpi=150, bbox_inches="tight")
print("✓ Saved: soil_impedance_spectra.png")

# =============================================================================
# NUMERICAL SUMMARY TABLE
# =============================================================================
print("\n" + "="*70)
print("IMPEDANCE VALUES AT KEY FREQUENCIES")
print("="*70)
print(f"{'State':<20} {'1 Hz':>12} {'1 kHz':>12} {'100 kHz':>12} {'1 MHz':>12}")
print("-"*70)

test_freqs = [1, 1e3, 1e5, 1e6]
for name, props in soil_states.items():
    vals = []
    for f in test_freqs:
        Z = z_soil(np.array([f]), name)[0]
        vals.append(f"|Z|={np.abs(Z):.1f} ∠{np.angle(Z, deg=True):.1f}°")
    print(f"{name.replace('_', ' '):<20} {vals[0]:>12} {vals[1]:>12} {vals[2]:>12} {vals[3]:>12}")

print("\n" + "="*70)
print("KEY INSIGHTS")
print("="*70)
print("""
1. LOW FREQ (<100 Hz):  Electrode polarization (CPE) dominates.
                        Phase → -90°, |Z| very large.
                        NOT measuring soil properties.

2. MID FREQ (1-10 kHz): Transition zone. Phase shifts rapidly.
                        |Z| reflects mixed bulk + electrode effects.
                        Used to extract CPE parameters (curve fitting).

3. HIGH FREQ (>100 kHz): Bulk soil dominates. Phase → 0°.
                         |Z| ≈ R_bulk = ρ/K_g.
                         Apparent conductivity σ_a → σ_bulk.
                         This is where you extract TRUE soil properties.

4. MOISTURE SENSITIVITY: At 1 MHz, |Z| spans ~10× (100Ω to 1000Ω)
                         across the three states.
                         → Excellent dynamic range for measurement.

5. DESIGN IMPLICATION: Your excitation sweep should prioritize:
   - 1 kHz: Extract CPE parameters (for electrode correction)
   - 100 kHz - 1 MHz: Extract bulk ρ → infer moisture
   - Phase at multiple frequencies: Separate σ_bulk from ε_r
""")
