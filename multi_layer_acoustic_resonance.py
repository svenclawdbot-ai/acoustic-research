#!/usr/bin/env python3
"""
Multi-Layer Acoustic Resonance Probe — Transfer Matrix Analysis

Extends the acoustic resonance probe concept to handle N-layer soil profiles.
The probe consists of:
  - Piezo transducer (excitation + reception)
  - Backing plate A (PVC, low impedance ~3.2 MRayls)
  - Backing plate B (Steel, high impedance ~46 MRayls)
  - Multi-layer soil (unknown profile)

Physics:
--------
For acoustic waves in a layer of thickness d with:
  - Characteristic impedance: Z = ρ·c [kg/(m²·s) = MRayls]
  - Wavenumber: k = ω/c = 2πf/c

The transfer matrix T relates [pressure, particle_velocity] across the layer:

    [p_right]   [ cos(kd)      i·Z·sin(kd)  ] [p_left]
    [v_right] = [ i·sin(kd)/Z   cos(kd)     ] [v_left]

The global matrix is the product of individual layer matrices.
Boundary conditions:
  - At transducer: measures reflection coefficient R = (Z_piezo - Z_in)/(Z_piezo + Z_in)
  - At semi-infinite soil base: p/v = Z_soil (outgoing wave only)

This script implements:
  1. Multi-layer transfer matrix solver
  2. Synthetic spectra for different soil profiles
  3. Sensitivity analysis: minimum detectable layer thickness
  4. Proof-of-concept inversion for layer parameters
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
from scipy.optimize import minimize, least_squares
import warnings


@dataclass
class AcousticLayer:
    """
    Represents an acoustic layer for the resonance probe.
    
    Attributes:
        name: Layer identifier
        thickness: Layer thickness [m] (np.inf for semi-infinite half-space)
        density: Mass density [kg/m³]
        velocity: Wave velocity [m/s] (compressional, since we're in solid coupling regime)
        damping: Hysteretic damping ratio [-] (optional)
    """
    name: str
    thickness: float
    density: float
    velocity: float
    damping: float = 0.0
    
    def __post_init__(self):
        if self.thickness != np.inf and self.thickness <= 0:
            raise ValueError("Layer thickness must be positive or np.inf")
        if self.velocity <= 0:
            raise ValueError("Wave velocity must be positive")
        if self.density <= 0:
            raise ValueError("Density must be positive")
        if self.damping < 0:
            raise ValueError("Damping ratio cannot be negative")
    
    @property
    def impedance(self) -> float:
        """Characteristic acoustic impedance Z = ρ·c [kg/(m²·s)]"""
        return self.density * self.velocity
    
    @property
    def is_semi_infinite(self) -> bool:
        """True if this is a semi-infinite half-space."""
        return self.thickness == np.inf
    
    def wavenumber(self, omega: np.ndarray) -> np.ndarray:
        """Angular-frequency wavenumber k = ω/c [rad/m]."""
        k = omega / self.velocity
        if self.damping > 0:
            # Complex wavenumber for damping
            k = k / (1 + 1j * self.damping)
        return k
    
    def __repr__(self) -> str:
        if self.is_semi_infinite:
            return f"AcousticLayer('{self.name}', semi-inf, ρ={self.density:.0f}, c={self.velocity:.0f}, Z={self.impedance/1e6:.2f}MRayls)"
        return f"AcousticLayer('{self.name}', d={self.thickness*1000:.1f}mm, ρ={self.density:.0f}, c={self.velocity:.0f}, Z={self.impedance/1e6:.2f}MRayls)"


class AcousticResonanceProbe:
    """
    Multi-layer acoustic resonance probe solver.
    
    Layer stack: transducer side → backing layers → soil layers → semi-infinite base
    """
    
    # Piezo ceramic impedance (typical PZT)
    Z_PIEZO = 30e6  # 30 MRayls (PZT-5A)
    
    def __init__(self, layers: List[AcousticLayer]):
        """
        Initialize probe with layer stack.
        
        Args:
            layers: List of AcousticLayer from transducer outward.
                    Last layer should be semi-infinite (thickness=np.inf).
        """
        if not layers:
            raise ValueError("At least one layer required")
        if not layers[-1].is_semi_infinite:
            raise ValueError("Last layer must be semi-infinite (thickness=np.inf)")
        self.layers = layers
    
    def transfer_matrix(self, layer: AcousticLayer, omega: float) -> np.ndarray:
        """
        Compute 2×2 transfer matrix for a single layer.
        
        [p_out]   [T11  T12] [p_in]
        [v_out] = [T21  T22] [v_in]
        
        For semi-infinite layer: returns identity (boundary condition handled separately).
        """
        if layer.is_semi_infinite:
            return np.eye(2, dtype=complex)
        
        k = layer.wavenumber(np.array([omega]))[0]
        kd = k * layer.thickness
        Z = layer.impedance
        
        if abs(kd) < 1e-12:
            # Static limit: thin layer, T ≈ identity with small correction
            return np.array([
                [1.0, 1j * Z * kd],
                [1j * kd / Z, 1.0]
            ], dtype=complex)
        
        # Standard transfer matrix
        cos_kd = np.cos(kd)
        sin_kd = np.sin(kd)
        
        return np.array([
            [cos_kd, 1j * Z * sin_kd],
            [1j * sin_kd / Z, cos_kd]
        ], dtype=complex)
    
    def global_transfer_matrix(self, omega: float) -> np.ndarray:
        """
        Compute global transfer matrix for entire layer stack.
        
        Multiplies individual matrices: T_global = T_1 × T_2 × ... × T_{N-1}
        (semi-infinite layer is identity).
        """
        T_global = np.eye(2, dtype=complex)
        
        for layer in self.layers:
            if not layer.is_semi_infinite:
                T_layer = self.transfer_matrix(layer, omega)
                T_global = T_global @ T_layer
        
        return T_global
    
    def input_impedance(self, omega: float, z_base: Optional[float] = None) -> complex:
        """
        Compute input impedance looking into the backing structure.
        
        Args:
            omega: Angular frequency [rad/s]
            z_base: Base impedance (defaults to last layer's impedance)
        
        Returns:
            Complex input impedance [kg/(m²·s)]
        """
        if z_base is None:
            z_base = self.layers[-1].impedance
        
        T = self.global_transfer_matrix(omega)
        t11, t12 = T[0, 0], T[0, 1]
        t21, t22 = T[1, 0], T[1, 1]
        
        # With semi-infinite base: p_base / v_base = z_base
        # [p_base]   [T11  T12] [p_in]
        # [v_base] = [T21  T22] [v_in]
        # 
        # p_base = z_base * v_base
        # z_base * (t21*p_in + t22*v_in) = t11*p_in + t12*v_in
        # z_in = p_in / v_in = (z_base*t22 - t12) / (t11 - z_base*t21)
        
        denom = t11 - z_base * t21
        if abs(denom) < 1e-15:
            return np.inf
        
        z_in = (z_base * t22 - t12) / denom
        return z_in
    
    def reflection_coefficient(self, omega: float, 
                                z_piezo: float = Z_PIEZO,
                                z_base: Optional[float] = None) -> complex:
        """
        Compute reflection coefficient at transducer-backing interface.
        
        R = (Z_piezo - Z_in) / (Z_piezo + Z_in)
        
        Returns:
            Complex reflection coefficient
        """
        z_in = self.input_impedance(omega, z_base)
        
        if np.isinf(z_in):
            return -1.0  # Total reflection
        
        return (z_piezo - z_in) / (z_piezo + z_in)
    
    def reflection_spectrum(self, frequencies: np.ndarray,
                          z_piezo: float = Z_PIEZO) -> np.ndarray:
        """
        Compute reflection coefficient magnitude across frequency range.
        
        Args:
            frequencies: Frequency array [Hz]
            z_piezo: Transducer impedance [kg/(m²·s)]
        
        Returns:
            Complex reflection coefficient array
        """
        omega = 2 * np.pi * frequencies
        R = np.zeros(len(frequencies), dtype=complex)
        
        for i, w in enumerate(omega):
            R[i] = self.reflection_coefficient(w, z_piezo)
        
        return R
    
    def resonance_peaks(self, frequencies: np.ndarray, 
                         z_piezo: float = Z_PIEZO,
                         threshold: float = 0.5) -> np.ndarray:
        """
        Find resonance frequencies from reflection spectrum.
        
        Resonances appear as peaks in |R| (high reflection = standing wave).
        
        Args:
            frequencies: Frequency array [Hz]
            z_piezo: Transducer impedance
            threshold: Minimum |R| to qualify as peak
        
        Returns:
            Array of resonance frequencies [Hz]
        """
        R = self.reflection_spectrum(frequencies, z_piezo)
        mag_R = np.abs(R)
        
        peaks = []
        for i in range(1, len(mag_R) - 1):
            if mag_R[i] > mag_R[i-1] and mag_R[i] > mag_R[i+1] and mag_R[i] > threshold:
                # Parabolic interpolation
                if mag_R[i-1] != mag_R[i+1]:
                    shift = 0.5 * (mag_R[i-1] - mag_R[i+1]) / (mag_R[i-1] - 2*mag_R[i] + mag_R[i+1])
                    peak_freq = frequencies[i] + shift * (frequencies[1] - frequencies[0])
                else:
                    peak_freq = frequencies[i]
                peaks.append(peak_freq)
        
        return np.array(peaks)
    
    def q_factors(self, frequencies: np.ndarray, 
                  z_piezo: float = Z_PIEZO) -> List[Dict]:
        """
        Compute Q-factors for identified resonance peaks.
        
        Q = f_res / Δf_FWHM (full width at half maximum)
        
        Returns:
            List of dicts with 'frequency', 'amplitude', 'q_factor', 'bandwidth'
        """
        peaks = self.resonance_peaks(frequencies, z_piezo)
        R = self.reflection_spectrum(frequencies, z_piezo)
        mag_R = np.abs(R)
        
        results = []
        df = frequencies[1] - frequencies[0]
        
        for fp in peaks:
            # Find index closest to peak
            idx = np.argmin(np.abs(frequencies - fp))
            peak_amp = mag_R[idx]
            half_max = peak_amp / np.sqrt(2)  # -3dB point
            
            # Find FWHM
            left_idx = idx
            while left_idx > 0 and mag_R[left_idx] > half_max:
                left_idx -= 1
            
            right_idx = idx
            while right_idx < len(mag_R) - 1 and mag_R[right_idx] > half_max:
                right_idx += 1
            
            fwhm = (right_idx - left_idx) * df
            q = fp / fwhm if fwhm > 0 else np.inf
            
            results.append({
                'frequency': fp,
                'amplitude': peak_amp,
                'q_factor': q,
                'bandwidth': fwhm
            })
        
        return results
    
    def __repr__(self) -> str:
        return f"AcousticResonanceProbe({len(self.layers)} layers)"


def make_standard_probe(soil_layers: List[AcousticLayer]) -> AcousticResonanceProbe:
    """
    Create a standard probe with PVC + steel backing + soil profile.
    
    Args:
        soil_layers: Soil layers from top (near surface) to bottom (deepest).
                     Last layer should be semi-infinite.
    
    Returns:
        AcousticResonanceProbe instance
    """
    backing = [
        AcousticLayer("PVC", thickness=0.005, density=1400, velocity=2300),
        AcousticLayer("Steel", thickness=0.015, density=7850, velocity=5900),
    ]
    
    # Prepend backing to soil layers
    all_layers = backing + soil_layers
    
    return AcousticResonanceProbe(all_layers)


# ============================================================================
# SYNTHETIC TEST CASES
# ============================================================================

def test_case_a_single_layer_soil() -> Tuple[AcousticResonanceProbe, str]:
    """
    Case A: Single-layer soil (semi-infinite dry sand).
    Verifies against the analytical model in transfer_matrix_resonance.md.
    """
    soil = [
        AcousticLayer("Dry Sand", thickness=np.inf, density=1600, velocity=400),
    ]
    
    probe = make_standard_probe(soil)
    description = "Case A: Single-layer soil (dry sand, semi-infinite)"
    
    print(f"\n{'='*60}")
    print(description)
    print(f"{'='*60}")
    for layer in probe.layers:
        print(f"  {layer}")
    
    # Check: sand-steel reflection should be ~ -0.97
    z_steel = 46.3e6
    z_sand = 1600 * 400
    R_theory = (z_sand - z_steel) / (z_sand + z_steel)
    print(f"\n  Steel-Sand reflection coefficient: {R_theory:.3f}")
    print(f"  (Expected: ~-0.97 for strong reflection)")
    
    return probe, description


def test_case_b_two_layer_soil() -> Tuple[AcousticResonanceProbe, str]:
    """
    Case B: Two-layer soil — topsoil over clay.
    Demonstrates that spectrum differs from single-layer equivalent.
    """
    soil = [
        AcousticLayer("Topsoil", thickness=0.100, density=1500, velocity=350),
        AcousticLayer("Clay", thickness=np.inf, density=1900, velocity=1500),
    ]
    
    probe = make_standard_probe(soil)
    description = "Case B: Two-layer soil (topsoil 100mm + clay semi-inf)"
    
    print(f"\n{'='*60}")
    print(description)
    print(f"{'='*60}")
    for layer in probe.layers:
        print(f"  {layer}")
    
    # Impedance contrast
    z_top = soil[0].impedance
    z_clay = soil[1].impedance
    R_interface = (z_clay - z_top) / (z_clay + z_top)
    print(f"\n  Topsoil-Clay reflection: {R_interface:.3f}")
    print(f"  Topsoil Z = {z_top/1e6:.2f} MRayls, Clay Z = {z_clay/1e6:.2f} MRayls")
    
    return probe, description


def test_case_c_sand_lens() -> Tuple[AcousticResonanceProbe, str]:
    """
    Case C: Thin sand lens (50mm) embedded in clay.
    Tests detectability of thin layers.
    """
    soil = [
        AcousticLayer("Topsoil", thickness=0.080, density=1500, velocity=350),
        AcousticLayer("Sand Lens", thickness=0.050, density=1700, velocity=500),
        AcousticLayer("Clay", thickness=np.inf, density=1900, velocity=1500),
    ]
    
    probe = make_standard_probe(soil)
    description = "Case C: Sand lens 50mm in clay (topsoil 80mm + sand 50mm + clay)"
    
    print(f"\n{'='*60}")
    print(description)
    print(f"{'='*60}")
    for layer in probe.layers:
        print(f"  {layer}")
    
    # Wavelength in sand lens at 100 kHz
    f_test = 100e3
    lambda_sand = soil[1].velocity / f_test
    print(f"\n  Wavelength in sand at {f_test/1e3:.0f} kHz: {lambda_sand*1000:.1f} mm")
    print(f"  Sand lens thickness: {soil[1].thickness*1000:.0f} mm")
    print(f"  Thickness/λ ratio: {soil[1].thickness / lambda_sand:.3f}")
    print(f"  (Need ~λ/4 = {lambda_sand*1000/4:.1f} mm for strong interference)")
    
    return probe, description


def test_case_d_saturation_contrast() -> Tuple[AcousticResonanceProbe, str]:
    """
    Case D: Dry vs Saturated soil — shows moisture sensitivity.
    """
    # Dry profile
    soil_dry = [
        AcousticLayer("Dry Topsoil", thickness=0.100, density=1400, velocity=300),
        AcousticLayer("Dry Sand", thickness=np.inf, density=1600, velocity=400),
    ]
    
    # Saturated profile
    soil_wet = [
        AcousticLayer("Saturated Topsoil", thickness=0.100, density=1700, velocity=800),
        AcousticLayer("Saturated Sand", thickness=np.inf, density=2000, velocity=1700),
    ]
    
    probe_dry = make_standard_probe(soil_dry)
    probe_wet = make_standard_probe(soil_wet)
    
    print(f"\n{'='*60}")
    print("Case D: Dry vs Saturated soil contrast")
    print(f"{'='*60}")
    print("\n  DRY profile:")
    for layer in probe_dry.layers:
        print(f"    {layer}")
    print("\n  WET profile:")
    for layer in probe_wet.layers:
        print(f"    {layer}")
    
    return probe_dry, probe_wet, "Case D: Dry vs Saturated"


# ============================================================================
# PLOTTING AND ANALYSIS
# ============================================================================

def plot_reflection_spectrum(probe: AcousticResonanceProbe,
                              f_min: float = 10e3,
                              f_max: float = 500e3,
                              n_points: int = 5000,
                              title: str = "",
                              ax=None,
                              color: str = 'blue',
                              label: str = "",
                              z_piezo: float = AcousticResonanceProbe.Z_PIEZO) -> Tuple[plt.Figure, plt.Axes]:
    """Plot reflection coefficient magnitude spectrum."""
    
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 5))
    else:
        fig = ax.figure
    
    frequencies = np.linspace(f_min, f_max, n_points)
    R = probe.reflection_spectrum(frequencies, z_piezo)
    mag_R = np.abs(R)
    
    ax.plot(frequencies / 1e3, mag_R, color=color, linewidth=1.2, label=label or title)
    
    # Mark peaks
    peaks = probe.resonance_peaks(frequencies, z_piezo, threshold=0.3)
    for fp in peaks[:8]:  # Mark first 8 peaks
        idx = np.argmin(np.abs(frequencies - fp))
        ax.plot(fp / 1e3, mag_R[idx], 'ro', markersize=6)
    
    ax.set_xlabel('Frequency [kHz]', fontsize=11)
    ax.set_ylabel('|Reflection Coefficient|', fontsize=11)
    ax.set_title(title or 'Reflection Spectrum', fontsize=12)
    ax.set_xlim(f_min / 1e3, f_max / 1e3)
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)
    if label:
        ax.legend()
    
    plt.tight_layout()
    return fig, ax


def plot_multiple_spectra(probes: List[AcousticResonanceProbe],
                          labels: List[str],
                          f_min: float = 10e3,
                          f_max: float = 500e3,
                          n_points: int = 5000,
                          title: str = "",
                          filename: str = "") -> plt.Figure:
    """Plot multiple spectra for comparison."""
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    colors = plt.cm.tab10(np.linspace(0, 1, len(probes)))
    
    for probe, label, color in zip(probes, labels, colors):
        frequencies = np.linspace(f_min, f_max, n_points)
        R = probe.reflection_spectrum(frequencies)
        mag_R = np.abs(R)
        ax.plot(frequencies / 1e3, mag_R, color=color, linewidth=1.5, label=label, alpha=0.8)
    
    ax.set_xlabel('Frequency [kHz]', fontsize=12)
    ax.set_ylabel('|Reflection Coefficient|', fontsize=12)
    ax.set_title(title or 'Multi-Layer Reflection Spectra', fontsize=13)
    ax.set_xlim(f_min / 1e3, f_max / 1e3)
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=10)
    
    plt.tight_layout()
    if filename:
        fig.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"Plot saved: {filename}")
    
    return fig


def compare_cases():
    """Run all test cases and compare spectra."""
    print("\n" + "=" * 70)
    print("MULTI-LAYER ACOUSTIC RESONANCE PROBE — TEST SUITE")
    print("=" * 70)
    
    # Case A: Single layer
    probe_a, desc_a = test_case_a_single_layer_soil()
    
    # Case B: Two layer
    probe_b, desc_b = test_case_b_two_layer_soil()
    
    # Case C: Sand lens
    probe_c, desc_c = test_case_c_sand_lens()
    
    # Case D: Dry vs Wet
    probe_d_dry, probe_d_wet, desc_d = test_case_d_saturation_contrast()
    
    # Plot comparisons
    print("\n" + "=" * 70)
    print("GENERATING PLOTS")
    print("=" * 70)
    
    # 1. All cases on one plot
    fig1 = plot_multiple_spectra(
        [probe_a, probe_b, probe_c],
        ["A: Single sand", "B: Topsoil+Clay", "C: Sand lens"],
        f_min=10e3, f_max=300e3, n_points=8000,
        title="Soil Profile Comparison — Reflection Spectra",
        filename="multi_layer_spectra_comparison.png"
    )
    
    # 2. Dry vs Wet
    fig2 = plot_multiple_spectra(
        [probe_d_dry, probe_d_wet],
        ["Dry", "Saturated"],
        f_min=10e3, f_max=300e3, n_points=8000,
        title="Moisture Effect — Dry vs Saturated Soil",
        filename="moisture_contrast_spectra.png"
    )
    
    # 3. Detailed single case with Q-factors
    fig3, ax3 = plt.subplots(figsize=(12, 6))
    frequencies = np.linspace(10e3, 300e3, 8000)
    R = probe_b.reflection_spectrum(frequencies)
    mag_R = np.abs(R)
    ax3.plot(frequencies / 1e3, mag_R, 'b-', linewidth=1.2)
    
    # Q-factors
    q_data = probe_b.q_factors(frequencies)
    for q in q_data[:5]:
        ax3.axvline(x=q['frequency'] / 1e3, color='r', linestyle='--', alpha=0.4)
        ax3.text(q['frequency'] / 1e3, 0.95, 
                f"Q={q['q_factor']:.1f}", 
                rotation=90, va='top', ha='right', color='r', fontsize=8)
    
    ax3.set_xlabel('Frequency [kHz]')
    ax3.set_ylabel('|Reflection Coefficient|')
    ax3.set_title('Case B: Q-Factor Analysis (Topsoil + Clay)')
    ax3.set_xlim(10, 300)
    ax3.set_ylim(0, 1.05)
    ax3.grid(True, alpha=0.3)
    plt.tight_layout()
    fig3.savefig("q_factor_analysis.png", dpi=150, bbox_inches='tight')
    print("Plot saved: q_factor_analysis.png")
    
    plt.close('all')
    
    return probe_a, probe_b, probe_c, probe_d_dry, probe_d_wet


# ============================================================================
# SENSITIVITY ANALYSIS
# ============================================================================

def sensitivity_minimum_thickness():
    """
    Analyze minimum detectable layer thickness vs. frequency.
    
    A layer must be ~λ/4 thick to create detectable interference.
    λ = c/f, so minimum thickness d_min ≈ c/(4f).
    """
    print("\n" + "=" * 70)
    print("SENSITIVITY ANALYSIS: Minimum Detectable Layer Thickness")
    print("=" * 70)
    
    # Materials
    materials = {
        'Sand (c=500 m/s)': 500,
        'Clay (c=1500 m/s)': 1500,
        'Silt (c=800 m/s)': 800,
    }
    
    frequencies = np.logspace(4, 6, 100)  # 10 kHz to 1 MHz
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for name, velocity in materials.items():
        # λ/4 thickness
        lambda_quarter = velocity / (4 * frequencies)
        ax.loglog(frequencies / 1e3, lambda_quarter * 1000, linewidth=2, label=name)
    
    # Mark practical frequency range
    ax.axvspan(50, 500, alpha=0.2, color='green', label='Practical probe range')
    
    # Reference lines
    ax.axhline(y=50, color='k', linestyle='--', alpha=0.5, label='50 mm (typical feature)')
    
    ax.set_xlabel('Frequency [kHz]', fontsize=12)
    ax.set_ylabel('Minimum Detectable Thickness [mm]', fontsize=12)
    ax.set_title('Layer Detectability: λ/4 Criterion', fontsize=13)
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3, which='both')
    
    plt.tight_layout()
    fig.savefig("sensitivity_minimum_thickness.png", dpi=150, bbox_inches='tight')
    print("Plot saved: sensitivity_minimum_thickness.png")
    
    # Print table
    print("\nMinimum detectable thickness [mm] at key frequencies:")
    print(f"{'Material':<20} {'50 kHz':<12} {'100 kHz':<12} {'200 kHz':<12} {'500 kHz':<12}")
    print("-" * 70)
    for name, velocity in materials.items():
        vals = []
        for f in [50e3, 100e3, 200e3, 500e3]:
            d_min = velocity / (4 * f) * 1000
            vals.append(f"{d_min:.1f}")
        print(f"{name:<20} {vals[0]:<12} {vals[1]:<12} {vals[2]:<12} {vals[3]:<12}")
    
    plt.close('all')


def sensitivity_thin_layer_test():
    """
    Test detectability of progressively thinner sand lenses in clay.
    """
    print("\n" + "=" * 70)
    print("SENSITIVITY: Thin Sand Lens Detectability")
    print("=" * 70)
    
    thicknesses = [0.200, 0.100, 0.050, 0.020, 0.010]  # 200mm down to 10mm
    labels = [f"{t*1000:.0f} mm" for t in thicknesses]
    
    probes = []
    for t in thicknesses:
        soil = [
            AcousticLayer("Topsoil", thickness=0.080, density=1500, velocity=350),
            AcousticLayer("Sand Lens", thickness=t, density=1700, velocity=500),
            AcousticLayer("Clay", thickness=np.inf, density=1900, velocity=1500),
        ]
        probes.append(make_standard_probe(soil))
    
    # Also add reference (no sand lens)
    soil_ref = [
        AcousticLayer("Topsoil", thickness=0.080, density=1500, velocity=350),
        AcousticLayer("Clay", thickness=np.inf, density=1900, velocity=1500),
    ]
    probes.append(make_standard_probe(soil_ref))
    labels.append("No lens")
    
    # Plot
    fig, ax = plt.subplots(figsize=(12, 7))
    
    colors = plt.cm.viridis(np.linspace(0, 1, len(probes)))
    frequencies = np.linspace(10e3, 300e3, 5000)
    
    for probe, label, color in zip(probes, labels, colors):
        R = probe.reflection_spectrum(frequencies)
        mag_R = np.abs(R)
        ax.plot(frequencies / 1e3, mag_R, color=color, linewidth=1.5, label=label, alpha=0.8)
    
    ax.set_xlabel('Frequency [kHz]', fontsize=12)
    ax.set_ylabel('|Reflection Coefficient|', fontsize=12)
    ax.set_title('Sand Lens Detectability — Thickness Sweep', fontsize=13)
    ax.set_xlim(10, 300)
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=10)
    
    plt.tight_layout()
    fig.savefig("thin_lens_detectability.png", dpi=150, bbox_inches='tight')
    print("Plot saved: thin_lens_detectability.png")
    
    # Compute difference metric
    print("\nDifference from 'no lens' reference (RMS deviation in |R|):")
    R_ref = np.abs(probes[-1].reflection_spectrum(frequencies))
    for probe, label in zip(probes[:-1], labels[:-1]):
        R = np.abs(probe.reflection_spectrum(frequencies))
        rms_diff = np.sqrt(np.mean((R - R_ref)**2))
        print(f"  {label}: RMS diff = {rms_diff:.4f}")
    
    plt.close('all')


# ============================================================================
# INVERSION PROOF-OF-CONCEPT
# ============================================================================

def inversion_two_layer():
    """
    Proof-of-concept: Given a synthetic spectrum from 2-layer soil,
    recover layer thickness and impedance via least-squares fitting.
    
    Uses multi-start optimization to avoid local minima.
    """
    print("\n" + "=" * 70)
    print("INVERSION: Two-Layer Soil Parameter Recovery")
    print("=" * 70)
    
    # True model
    true_soil = [
        AcousticLayer("Topsoil", thickness=0.100, density=1500, velocity=350),  # Z = 0.525 MRayls
        AcousticLayer("Clay", thickness=np.inf, density=1900, velocity=1500),      # Z = 2.85 MRayls
    ]
    true_probe = make_standard_probe(true_soil)
    
    print("\nTRUE MODEL:")
    for layer in true_probe.layers:
        if "PVC" in layer.name or "Steel" in layer.name:
            continue
        print(f"  {layer}")
    
    # Generate synthetic data — use finer resolution for fitting
    frequencies = np.linspace(10e3, 300e3, 400)
    R_true = true_probe.reflection_spectrum(frequencies)
    mag_true = np.abs(R_true)
    
    # Add noise (0.5% amplitude noise — optimistic for lab conditions)
    np.random.seed(42)
    noise_level = 0.005
    mag_noisy = mag_true * (1 + noise_level * np.random.randn(len(mag_true)))
    
    # Fit model: optimize [thickness_topsoil, velocity_topsoil, velocity_clay]
    # We fix densities and backing layers (known)
    
    def model_spectrum(params: np.ndarray) -> np.ndarray:
        """Compute spectrum for given parameters."""
        d_top, c_top, c_clay = params
        
        soil = [
            AcousticLayer("Topsoil", thickness=max(d_top, 0.001), density=1500, velocity=max(c_top, 100)),
            AcousticLayer("Clay", thickness=np.inf, density=1900, velocity=max(c_clay, 100)),
        ]
        probe = make_standard_probe(soil)
        R = probe.reflection_spectrum(frequencies)
        return np.abs(R)
    
    def residual(params: np.ndarray) -> np.ndarray:
        """Residual vector for least squares."""
        return model_spectrum(params) - mag_noisy
    
    def objective(params: np.ndarray) -> float:
        """Scalar objective for direct minimization."""
        return np.sum(residual(params)**2)
    
    # Bounds
    bounds = ([0.010, 100.0, 500.0],    # lower
              [0.500, 800.0, 2500.0])   # upper
    
    print(f"\nTrue values:     d_top={true_soil[0].thickness*1000:.0f}mm, c_top={true_soil[0].velocity:.0f}m/s, c_clay={true_soil[1].velocity:.0f}m/s")
    
    # Multi-start optimization
    print(f"\nRunning multi-start optimization (10 random starts)...")
    
    best_result = None
    best_misfit = np.inf
    
    n_starts = 10
    for start in range(n_starts):
        if start == 0:
            # First start: reasonable guess
            p0 = np.array([0.080, 400.0, 1200.0])
        else:
            # Random start within bounds
            p0 = np.array([
                np.random.uniform(bounds[0][0], bounds[1][0]),
                np.random.uniform(bounds[0][1], bounds[1][1]),
                np.random.uniform(bounds[0][2], bounds[1][2]),
            ])
        
        try:
            result = least_squares(residual, p0, bounds=bounds, method='trf', 
                                  max_nfev=2000, ftol=1e-12, xtol=1e-12)
            misfit = result.cost
            
            if misfit < best_misfit:
                best_misfit = misfit
                best_result = result
                
            if start < 3 or start == n_starts - 1:
                print(f"  Start {start+1}: d={result.x[0]*1000:.1f}mm, c_top={result.x[1]:.0f}, c_clay={result.x[2]:.0f}, misfit={misfit:.4e}")
        except Exception as e:
            print(f"  Start {start+1}: failed ({e})")
    
    p_opt = best_result.x
    d_opt, c_top_opt, c_clay_opt = p_opt
    
    print(f"\n{'='*40}")
    print("BEST INVERSION RESULT")
    print(f"{'='*40}")
    print(f"  Recovered: d_top={d_opt*1000:.1f}mm, c_top={c_top_opt:.0f}m/s, c_clay={c_clay_opt:.0f}m/s")
    print(f"  True:      d_top={true_soil[0].thickness*1000:.0f}mm, c_top={true_soil[0].velocity:.0f}m/s, c_clay={true_soil[1].velocity:.0f}m/s")
    
    # Errors
    err_d = abs(d_opt - true_soil[0].thickness) / true_soil[0].thickness * 100
    err_c_top = abs(c_top_opt - true_soil[0].velocity) / true_soil[0].velocity * 100
    err_c_clay = abs(c_clay_opt - true_soil[1].velocity) / true_soil[1].velocity * 100
    
    print(f"\n  Relative errors:")
    print(f"    Thickness: {err_d:.1f}%")
    print(f"    Topsoil c: {err_c_top:.1f}%")
    print(f"    Clay c:    {err_c_clay:.1f}%")
    
    # Plot fit
    mag_fit = model_spectrum(p_opt)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(frequencies / 1e3, mag_true, 'b-', linewidth=2, label='True (noise-free)')
    ax.plot(frequencies / 1e3, mag_noisy, 'g.', markersize=3, alpha=0.4, label='Noisy data (0.5% noise)')
    ax.plot(frequencies / 1e3, mag_fit, 'r--', linewidth=2, label='Fitted model')
    
    ax.set_xlabel('Frequency [kHz]', fontsize=12)
    ax.set_ylabel('|Reflection Coefficient|', fontsize=12)
    ax.set_title('Inversion: Two-Layer Soil Fit (Multi-Start)', fontsize=13)
    ax.set_xlim(10, 300)
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=11)
    
    # Add text box with results
    textstr = f"Recovered:\n" \
              f"  d_top = {d_opt*1000:.1f} mm\n" \
              f"  c_top = {c_top_opt:.0f} m/s\n" \
              f"  c_clay = {c_clay_opt:.0f} m/s\n\n" \
              f"Errors:\n" \
              f"  d: {err_d:.1f}%\n" \
              f"  c_top: {err_c_top:.1f}%\n" \
              f"  c_clay: {err_c_clay:.1f}%\n\n" \
              f"Misfit: {best_misfit:.4e}"
    
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props, family='monospace')
    
    plt.tight_layout()
    fig.savefig("inversion_two_layer_fit.png", dpi=150, bbox_inches='tight')
    print("\nPlot saved: inversion_two_layer_fit.png")
    
    plt.close('all')
    
    return best_result


def inversion_identifiability():
    """
    Analyze which parameters are well-constrained by the spectrum.
    
    Test: fix one parameter, vary others, measure fit quality.
    """
    print("\n" + "=" * 70)
    print("INVERSION: Parameter Identifiability Analysis")
    print("=" * 70)
    
    # True model
    true_soil = [
        AcousticLayer("Topsoil", thickness=0.100, density=1500, velocity=350),
        AcousticLayer("Clay", thickness=np.inf, density=1900, velocity=1500),
    ]
    true_probe = make_standard_probe(true_soil)
    
    frequencies = np.linspace(10e3, 300e3, 200)
    mag_true = np.abs(true_probe.reflection_spectrum(frequencies))
    
    # Parameter sweeps
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    param_names = ['d_top [mm]', 'c_top [m/s]', 'c_clay [m/s]']
    param_ranges = [
        np.linspace(0.020, 0.300, 50),   # thickness
        np.linspace(100, 800, 50),       # topsoil velocity
        np.linspace(500, 2500, 50),      # clay velocity
    ]
    true_values = [0.100, 350, 1500]
    
    misfits = []
    
    for idx, (ax, name, p_range, true_val) in enumerate(zip(axes, param_names, param_ranges, true_values)):
        misfit = []
        for p_val in p_range:
            # Build model with swept parameter
            if idx == 0:
                soil = [
                    AcousticLayer("Topsoil", thickness=p_val, density=1500, velocity=350),
                    AcousticLayer("Clay", thickness=np.inf, density=1900, velocity=1500),
                ]
            elif idx == 1:
                soil = [
                    AcousticLayer("Topsoil", thickness=0.100, density=1500, velocity=p_val),
                    AcousticLayer("Clay", thickness=np.inf, density=1900, velocity=1500),
                ]
            else:
                soil = [
                    AcousticLayer("Topsoil", thickness=0.100, density=1500, velocity=350),
                    AcousticLayer("Clay", thickness=np.inf, density=1900, velocity=p_val),
                ]
            
            probe = make_standard_probe(soil)
            mag = np.abs(probe.reflection_spectrum(frequencies))
            
            # RMS misfit
            m = np.sqrt(np.mean((mag - mag_true)**2))
            misfit.append(m)
        
        misfits.append(misfit)
        
        # Plot
        if idx == 0:
            x_plot = p_range * 1000  # mm
            x_true = true_val * 1000
        else:
            x_plot = p_range
            x_true = true_val
        
        ax.plot(x_plot, misfit, 'b-', linewidth=2)
        ax.axvline(x=x_true, color='r', linestyle='--', linewidth=2, label='True value')
        ax.set_xlabel(name, fontsize=11)
        ax.set_ylabel('RMS Misfit', fontsize=11)
        ax.set_title(f'Parameter {idx+1} Sensitivity', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Mark minimum
        min_idx = np.argmin(misfit)
        ax.plot(x_plot[min_idx], misfit[min_idx], 'go', markersize=10, label='Minimum')
    
    plt.tight_layout()
    fig.savefig("parameter_identifiability.png", dpi=150, bbox_inches='tight')
    print("Plot saved: parameter_identifiability.png")
    
    # Summary
    print("\nIdentifiability Summary (sharpness of misfit minimum):")
    for name, misfit, p_range, true_val in zip(param_names, misfits, param_ranges, true_values):
        # Compute curvature at minimum (2nd derivative)
        min_idx = np.argmin(misfit)
        if 0 < min_idx < len(misfit) - 1:
            dx = p_range[1] - p_range[0]
            curvature = (misfit[min_idx-1] - 2*misfit[min_idx] + misfit[min_idx+1]) / dx**2
        else:
            curvature = 0
        
        identifiability = "HIGH" if curvature > 1e-4 else "LOW"
        print(f"  {name}: curvature={curvature:.2e} → {identifiability}")
    
    plt.close('all')


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run the full multi-layer resonance analysis suite."""
    print("\n" + "=" * 70)
    print("MULTI-LAYER ACOUSTIC RESONANCE PROBE ANALYSIS")
    print("=" * 70)
    
    # Run all test cases
    compare_cases()
    
    # Sensitivity
    sensitivity_minimum_thickness()
    sensitivity_thin_layer_test()
    
    # Inversion
    inversion_two_layer()
    inversion_identifiability()
    
    print("\n" + "=" * 70)
    print("COMPLETE. Generated plots:")
    print("  - multi_layer_spectra_comparison.png")
    print("  - moisture_contrast_spectra.png")
    print("  - q_factor_analysis.png")
    print("  - sensitivity_minimum_thickness.png")
    print("  - thin_lens_detectability.png")
    print("  - inversion_two_layer_fit.png")
    print("  - parameter_identifiability.png")
    print("=" * 70)


if __name__ == "__main__":
    main()
