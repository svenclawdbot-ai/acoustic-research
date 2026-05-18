#!/usr/bin/env python3
"""
Transfer Matrix Method for Seismic/Acoustic Wave Propagation in Layered Soils

This script implements the transfer matrix (propagator matrix) method for analyzing
wave propagation through horizontally layered soil systems. Used for:
- Bender element testing analysis
- Acoustic impedance probe interpretation
- Resonance column test data processing
- Site response analysis

Physics:
--------
The transfer matrix relates wave amplitudes at one boundary to those at another.
For a single layer of thickness H with wave number k = ω/V:
    [u(0)]   [ cos(kH)    sin(kH)/k ] [u(H)]
    [τ(0)] = [-k·sin(kH)   cos(kH)  ] [τ(H)]

Where:
    u = displacement
    τ = stress
    ω = angular frequency
    V = wave velocity (Vs or Vp)
    H = layer thickness
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Tuple, Optional, Union
from enum import Enum
import warnings


class WaveType(Enum):
    """Wave propagation type."""
    P_WAVE = "p"      # Compressional / Primary
    S_WAVE = "s"      # Shear / Secondary


@dataclass
class SoilLayer:
    """
    Represents a soil layer with its physical properties.
    
    Attributes:
        thickness: Layer thickness [m]
        vs: Shear wave velocity [m/s]
        vp: Compressional wave velocity [m/s] (optional, computed if density/G given)
        density: Mass density [kg/m³]
        damping: Hysteretic damping ratio [-] (optional)
        name: Layer identifier (optional)
    """
    thickness: float
    vs: float
    density: float
    vp: Optional[float] = None
    damping: float = 0.0
    name: str = ""
    
    def __post_init__(self):
        if self.thickness <= 0:
            raise ValueError("Layer thickness must be positive")
        if self.vs <= 0:
            raise ValueError("Wave velocity must be positive")
        if self.density <= 0:
            raise ValueError("Density must be positive")
        if self.damping < 0:
            raise ValueError("Damping ratio cannot be negative")
        
        # Estimate vp from vs if not provided (assuming Poisson's ratio ~0.3 for soils)
        if self.vp is None:
            # vp ≈ vs * sqrt((2-2ν)/(1-2ν)), for ν=0.3: vp ≈ 1.87 * vs
            self.vp = self.vs * 1.87
    
    @property
    def shear_modulus(self) -> float:
        """Shear modulus G = ρ * Vs² [Pa]"""
        return self.density * self.vs**2
    
    @property
    def bulk_modulus(self) -> float:
        """Bulk modulus K = ρ * (Vp² - 4/3·Vs²) [Pa]"""
        return self.density * (self.vp**2 - (4/3) * self.vs**2)
    
    @property
    def youngs_modulus(self) -> float:
        """Young's modulus E [Pa]"""
        g = self.shear_modulus
        k = self.bulk_modulus
        return 9 * k * g / (3 * k + g)
    
    @property
    def poisson_ratio(self) -> float:
        """Poisson's ratio ν [-]"""
        return (self.vp**2 - 2*self.vs**2) / (2*(self.vp**2 - self.vs**2))
    
    @property
    def impedance_s(self) -> float:
        """Shear wave impedance Zs = ρ·Vs [kg/(m²·s)]"""
        return self.density * self.vs
    
    @property
    def impedance_p(self) -> float:
        """P-wave impedance Zp = ρ·Vp [kg/(m²·s)]"""
        return self.density * self.vp
    
    def __repr__(self) -> str:
        name_str = f"'{self.name}' " if self.name else ""
        return f"SoilLayer {name_str}(H={self.thickness:.3f}m, Vs={self.vs:.1f}m/s, ρ={self.density:.1f}kg/m³)"


class TransferMatrix:
    """
    Transfer matrix for wave propagation in a single layer.
    
    The transfer matrix T relates the state vector [displacement, stress] at the
    bottom of a layer to the state vector at the top.
    
    For S-waves in a layer of thickness H:
        T = [[ cos(kH),      sin(kH)/(G·k) ],
             [-G·k·sin(kH),  cos(kH)       ]]
    
    where k = ω/Vs is the wave number and G is the shear modulus.
    """
    
    def __init__(self, layer: SoilLayer, wave_type: WaveType = WaveType.S_WAVE):
        self.layer = layer
        self.wave_type = wave_type
    
    def compute(self, omega: Union[float, np.ndarray]) -> Union[np.ndarray, List[np.ndarray]]:
        """
        Compute the transfer matrix for given angular frequency/frequencies.
        
        Args:
            omega: Angular frequency ω = 2πf [rad/s]
        
        Returns:
            Transfer matrix(es) as 2×2 numpy arrays
        """
        omega = np.atleast_1d(omega)
        
        if self.wave_type == WaveType.S_WAVE:
            velocity = self.layer.vs
            modulus = self.layer.shear_modulus
        else:
            velocity = self.layer.vp
            # For P-waves, use constrained modulus M = λ + 2G = ρ·Vp²
            modulus = self.layer.density * self.layer.vp**2
        
        # Handle damping (complex modulus approach)
        if self.layer.damping > 0:
            modulus = modulus * (1 + 2j * self.layer.damping)
        
        # Wave number
        k = omega / velocity
        
        # Handle k=0 (static case)
        kH = k * self.layer.thickness
        
        matrices = []
        for i, kh in enumerate(kH):
            if abs(kh) < 1e-10:
                # Static limit: T = [[1, H/modulus], [0, 1]]
                t11 = 1.0
                t12 = self.layer.thickness / modulus if not np.iscomplex(modulus) else self.layer.thickness / modulus
                t21 = 0.0
                t22 = 1.0
            else:
                t11 = np.cos(kh)
                t12 = np.sin(kh) / (modulus * k[i]) if not np.isscalar(modulus) else np.sin(kh) / (modulus * k[i])
                t21 = -modulus * k[i] * np.sin(kh)
                t22 = np.cos(kh)
            
            matrices.append(np.array([[t11, t12], [t21, t22]], dtype=complex))
        
        if len(omega) == 1:
            return matrices[0]
        return matrices
    
    def compute_simple(self, f: float) -> np.ndarray:
        """Simple interface: compute transfer matrix at frequency f [Hz]."""
        omega = 2 * np.pi * f
        return self.compute(omega)


class LayeredSystem:
    """
    Multi-layer system analyzed using the global transfer matrix method.
    
    The global transfer matrix is the product of individual layer matrices:
        T_global = T₁ × T₂ × ... × Tₙ
    
    Boundary conditions:
    - Free surface: stress = 0
    - Rigid base: displacement = 0  
    - Elastic base: impedance matching
    """
    
    def __init__(self, layers: List[SoilLayer]):
        if not layers:
            raise ValueError("At least one layer required")
        self.layers = layers
    
    def global_transfer_matrix(self, omega: Union[float, np.ndarray], 
                              wave_type: WaveType = WaveType.S_WAVE) -> Union[np.ndarray, List[np.ndarray]]:
        """
        Compute the global transfer matrix for the entire layer stack.
        
        Args:
            omega: Angular frequency [rad/s]
            wave_type: S_WAVE or P_WAVE
        
        Returns:
            Global 2×2 transfer matrix(ces)
        """
        omega = np.atleast_1d(omega)
        
        global_matrices = []
        for w in omega:
            # Start with identity
            T_global = np.eye(2, dtype=complex)
            
            # Multiply layer matrices from top to bottom
            for layer in self.layers:
                t_matrix = TransferMatrix(layer, wave_type).compute(w)
                T_global = T_global @ t_matrix
            
            global_matrices.append(T_global)
        
        if len(omega) == 1:
            return global_matrices[0]
        return global_matrices
    
    def amplification_function(self, frequencies: np.ndarray,
                               wave_type: WaveType = WaveType.S_WAVE,
                               boundary: str = "free_rigid") -> np.ndarray:
        """
        Compute the amplification function (transfer function) for the layer stack.
        
        Args:
            frequencies: Array of frequencies [Hz]
            wave_type: S_WAVE or P_WAVE
            boundary: "free_rigid", "free_elastic", or "rigid_rigid"
        
        Returns:
            Complex amplification values (surface/bedrock motion)
        """
        omega = 2 * np.pi * frequencies
        
        amplifications = np.zeros(len(frequencies), dtype=complex)
        
        for i, w in enumerate(omega):
            T = self.global_transfer_matrix(w, wave_type)
            
            # Extract components
            t11, t12 = T[0, 0], T[0, 1]
            t21, t22 = T[1, 0], T[1, 1]
            
            if boundary == "free_rigid":
                # Free surface (τ=0 at top), rigid base (u=0 at bottom)
                # Amplification = 1 / t11 (when stress is zero at surface)
                if abs(t11) > 1e-10:
                    amplifications[i] = 1.0 / t11
                else:
                    amplifications[i] = np.inf
            
            elif boundary == "free_elastic":
                # Free surface, elastic half-space base
                # Need impedance of half-space (last layer extends to infinity)
                base_impedance = self.layers[-1].impedance_s if wave_type == WaveType.S_WAVE else self.layers[-1].impedance_p
                if abs(t11 * base_impedance + t12) > 1e-10:
                    amplifications[i] = base_impedance / (t11 * base_impedance + t12)
                else:
                    amplifications[i] = np.inf
            
            elif boundary == "rigid_rigid":
                # Both boundaries rigid
                amplifications[i] = 1.0 / t11 if abs(t11) > 1e-10 else np.inf
            
            else:
                raise ValueError(f"Unknown boundary condition: {boundary}")
        
        return amplifications
    
    def natural_frequencies(self, wave_type: WaveType = WaveType.S_WAVE,
                           f_max: float = 100.0, n_points: int = 10000) -> np.ndarray:
        """
        Estimate natural frequencies by finding peaks in amplification.
        
        Args:
            wave_type: S_WAVE or P_WAVE
            f_max: Maximum frequency to search [Hz]
            n_points: Number of frequency points
        
        Returns:
            Array of natural frequencies [Hz]
        """
        freqs = np.linspace(0.1, f_max, n_points)
        amp = np.abs(self.amplification_function(freqs, wave_type))
        
        # Find peaks
        peaks = []
        for i in range(1, len(amp) - 1):
            if amp[i] > amp[i-1] and amp[i] > amp[i+1] and amp[i] > 2.0:
                # Interpolate for better accuracy
                if amp[i-1] != amp[i+1]:
                    shift = 0.5 * (amp[i-1] - amp[i+1]) / (amp[i-1] - 2*amp[i] + amp[i+1])
                    peak_freq = freqs[i] + shift * (freqs[1] - freqs[0])
                else:
                    peak_freq = freqs[i]
                peaks.append(peak_freq)
        
        return np.array(peaks)
    
    def resonance_modes(self, wave_type: WaveType = WaveType.S_WAVE) -> List[dict]:
        """
        Compute theoretical resonance frequencies for simple cases.
        
        For a single layer on rigid base:
            f_n = (2n - 1) * Vs / (4H)  for S-waves (odd modes)
            f_n = n * Vs / (2H)          for all modes
        
        Returns:
            List of mode dictionaries with frequency and description
        """
        modes = []
        
        if len(self.layers) == 1:
            layer = self.layers[0]
            H = layer.thickness
            V = layer.vs if wave_type == WaveType.S_WAVE else layer.vp
            
            # Fundamental and first few harmonics
            for n in range(1, 6):
                if wave_type == WaveType.S_WAVE:
                    # Free surface, rigid base: odd quarter-wavelength modes
                    f_n = (2 * n - 1) * V / (4 * H)
                    desc = f"Mode {n}: λ = {4*H/(2*n-1):.3f}m (quarter-wave)"
                else:
                    f_n = n * V / (2 * H)
                    desc = f"Mode {n}: λ = {2*H/n:.3f}m (half-wave)"
                
                modes.append({
                    'mode_number': n,
                    'frequency': f_n,
                    'wavelength': V / f_n,
                    'description': desc
                })
        
        return modes
    
    def displacement_profile(self, frequency: float, 
                            wave_type: WaveType = WaveType.S_WAVE,
                            base_amplitude: float = 1.0,
                            n_points_per_layer: int = 20) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute displacement profile through the layer stack at a given frequency.
        
        Args:
            frequency: Frequency [Hz]
            wave_type: S_WAVE or P_WAVE
            base_amplitude: Displacement amplitude at base [m]
            n_points_per_layer: Resolution per layer
        
        Returns:
            depths: Depth array from surface (0) downward [m]
            displacements: Complex displacement array [m]
        """
        omega = 2 * np.pi * frequency
        
        # Determine boundary condition at surface
        # Free surface: stress = 0
        T_global = self.global_transfer_matrix(omega, wave_type)
        
        # For free surface, τ_surface = 0, u_surface = ?
        # [u_surface]   [t11 t12] [u_base]
        # [0      ]   = [t21 t22] [τ_base]
        # 
        # From bottom: u_base = base_amplitude, find τ_base
        # 0 = t21 * u_base + t22 * τ_base
        # τ_base = -t21/t22 * u_base
        
        t21, t22 = T_global[1, 0], T_global[1, 1]
        if abs(t22) < 1e-10:
            tau_base = 0
        else:
            tau_base = -t21 / t22 * base_amplitude
        
        # State vector at base
        state_base = np.array([base_amplitude, tau_base], dtype=complex)
        
        # Propagate upward through layers
        depths = []
        displacements = []
        
        current_depth = sum(l.thickness for l in self.layers)
        
        for layer in reversed(self.layers):
            # Points within this layer (from bottom to top)
            z_local = np.linspace(layer.thickness, 0, n_points_per_layer)
            
            for z in z_local:
                # Transfer matrix from depth z to bottom of layer
                k = omega / (layer.vs if wave_type == WaveType.S_WAVE else layer.vp)
                if layer.damping > 0:
                    k = k / (1 + 1j * layer.damping)
                
                kh = k * z
                if abs(kh) < 1e-10:
                    T_local = np.eye(2, dtype=complex)
                else:
                    modulus = layer.shear_modulus if wave_type == WaveType.S_WAVE else layer.density * layer.vp**2
                    if layer.damping > 0:
                        modulus = modulus * (1 + 2j * layer.damping)
                    
                    T_local = np.array([
                        [np.cos(kh), np.sin(kh)/(modulus*k)],
                        [-modulus*k*np.sin(kh), np.cos(kh)]
                    ], dtype=complex)
                
                state = T_local @ state_base
                depths.append(current_depth - (layer.thickness - z))
                displacements.append(state[0])
            
            # Update state_base for next layer (now at top of current layer)
            T_full = TransferMatrix(layer, wave_type).compute(omega)
            state_base = T_full @ state_base
            current_depth -= layer.thickness
        
        return np.array(depths), np.array(displacements)
    
    @property
    def total_thickness(self) -> float:
        """Total thickness of layer stack [m]."""
        return sum(l.thickness for l in self.layers)
    
    def __repr__(self) -> str:
        return f"LayeredSystem({len(self.layers)} layers, total thickness={self.total_thickness:.3f}m)"


def plot_amplification(system: LayeredSystem, 
                      f_min: float = 0.1, 
                      f_max: float = 100.0,
                      wave_type: WaveType = WaveType.S_WAVE,
                      boundary: str = "free_rigid",
                      n_points: int = 2000,
                      ax=None):
    """
    Plot the amplification function for a layered system.
    
    Args:
        system: LayeredSystem instance
        f_min, f_max: Frequency range [Hz]
        wave_type: S_WAVE or P_WAVE
        boundary: Boundary condition string
        n_points: Number of frequency points
        ax: Optional matplotlib axis
    
    Returns:
        matplotlib figure and axis
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    else:
        fig = ax.figure
    
    frequencies = np.linspace(f_min, f_max, n_points)
    amplification = system.amplification_function(frequencies, wave_type, boundary)
    
    # Plot amplitude
    ax.plot(frequencies, np.abs(amplification), 'b-', linewidth=1.5, label='|Amplification|')
    
    # Mark natural frequencies
    try:
        nat_freqs = system.natural_frequencies(wave_type, f_max, n_points)
        for f in nat_freqs:
            if f_min <= f <= f_max:
                ax.axvline(x=f, color='r', linestyle='--', alpha=0.5)
                ax.text(f, ax.get_ylim()[1]*0.9, f'{f:.1f} Hz', 
                       rotation=90, va='top', ha='right', color='r', fontsize=8)
    except:
        pass
    
    ax.set_xlabel('Frequency [Hz]', fontsize=12)
    ax.set_ylabel('Amplification Factor', fontsize=12)
    ax.set_title(f'Transfer Function - {wave_type.value.upper()}-Wave\n{boundary.replace("_", " ").title()} Boundary', 
                fontsize=12)
    ax.set_xlim(f_min, f_max)
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    plt.tight_layout()
    return fig, ax


def plot_displacement_profile(system: LayeredSystem,
                              frequencies: List[float],
                              wave_type: WaveType = WaveType.S_WAVE,
                              figsize: Tuple[float, float] = (10, 8)):
    """
    Plot displacement profiles at multiple frequencies.
    
    Args:
        system: LayeredSystem instance
        frequencies: List of frequencies to plot [Hz]
        wave_type: S_WAVE or P_WAVE
        figsize: Figure size
    
    Returns:
        matplotlib figure and axes
    """
    n_freqs = len(frequencies)
    fig, axes = plt.subplots(1, n_freqs, figsize=figsize, sharey=True)
    
    if n_freqs == 1:
        axes = [axes]
    
    colors = plt.cm.viridis(np.linspace(0, 1, n_freqs))
    
    for i, (freq, color) in enumerate(zip(frequencies, colors)):
        depths, disp = system.displacement_profile(freq, wave_type)
        
        # Plot real part
        axes[i].plot(np.real(disp), depths, color=color, linewidth=2, label=f'{freq:.1f} Hz')
        axes[i].fill_betweenx(depths, 0, np.real(disp), alpha=0.3, color=color)
        
        axes[i].set_xlabel('Displacement [m]', fontsize=10)
        axes[i].set_title(f'{freq:.1f} Hz', fontsize=11)
        axes[i].grid(True, alpha=0.3)
        axes[i].axvline(x=0, color='k', linewidth=0.5)
    
    axes[0].set_ylabel('Depth [m]', fontsize=12)
    axes[0].invert_yaxis()  # Depth increases downward
    
    plt.tight_layout()
    return fig, axes


def plot_layer_properties(system: LayeredSystem, figsize: Tuple[float, float] = (10, 6)):
    """
    Plot layer properties (Vs, density, impedance) as a function of depth.
    
    Args:
        system: LayeredSystem instance
        figsize: Figure size
    
    Returns:
        matplotlib figure and axes
    """
    fig, axes = plt.subplots(1, 3, figsize=figsize, sharey=True)
    
    # Build depth arrays
    depths_top = [0]
    depths_bottom = []
    vs_values = []
    rho_values = []
    imp_values = []
    
    for layer in system.layers:
        depths_bottom.append(depths_top[-1] + layer.thickness)
        vs_values.append(layer.vs)
        rho_values.append(layer.density)
        imp_values.append(layer.impedance_s)
        depths_top.append(depths_top[-1] + layer.thickness)
    
    depths_top = depths_top[:-1]  # Remove the extra
    
    # Plot as step functions
    for ax, values, label, color in zip(axes, 
                                        [vs_values, rho_values, imp_values],
                                        ['Vs [m/s]', 'Density [kg/m³]', 'Impedance [kg/(m²·s)]'],
                                        ['blue', 'green', 'red']):
        for i, (z_top, z_bot, val) in enumerate(zip(depths_top, depths_bottom, values)):
            ax.plot([val, val], [z_top, z_bot], color=color, linewidth=2)
            if i < len(values) - 1:
                ax.plot([val, values[i+1]], [z_bot, z_bot], color=color, linewidth=1, linestyle='--')
        
        ax.set_xlabel(label, fontsize=11)
        ax.grid(True, alpha=0.3)
    
    axes[0].set_ylabel('Depth [m]', fontsize=12)
    axes[0].invert_yaxis()
    
    plt.tight_layout()
    return fig, axes


def demo_single_layer():
    """Demonstration: Single soil layer on rigid base."""
    print("=" * 60)
    print("DEMO: Single Layer on Rigid Base")
    print("=" * 60)
    
    # Typical soft clay layer
    clay = SoilLayer(
        thickness=10.0,      # 10 m thick
        vs=150.0,           # 150 m/s shear wave velocity
        density=1800.0,     # 1.8 g/cm³
        damping=0.05,       # 5% damping
        name="Soft Clay"
    )
    
    print(f"\nLayer properties:")
    print(f"  {clay}")
    print(f"  Shear modulus G = {clay.shear_modulus/1e6:.2f} MPa")
    print(f"  Poisson's ratio ν = {clay.poisson_ratio:.3f}")
    
    system = LayeredSystem([clay])
    print(f"\n{system}")
    
    # Theoretical resonance
    modes = system.resonance_modes(WaveType.S_WAVE)
    print(f"\nTheoretical resonance frequencies (S-wave):")
    for mode in modes:
        print(f"  {mode['description']}: f = {mode['frequency']:.2f} Hz")
    
    # Compute amplification
    freqs = np.linspace(0.1, 50, 1000)
    amp = system.amplification_function(freqs, WaveType.S_WAVE, "free_rigid")
    
    print(f"\nMaximum amplification: {np.max(np.abs(amp)):.1f} at {freqs[np.argmax(np.abs(amp))]:.2f} Hz")
    
    # Plot
    fig, ax = plot_amplification(system, 0.1, 50, WaveType.S_WAVE, "free_rigid")
    fig.savefig('single_layer_amplification.png', dpi=150, bbox_inches='tight')
    print("\nPlot saved: single_layer_amplification.png")
    
    # Displacement profile at resonance
    f_res = modes[0]['frequency']
    depths, disp = system.displacement_profile(f_res, WaveType.S_WAVE)
    
    fig2, ax2 = plt.subplots(figsize=(6, 8))
    ax2.plot(np.real(disp), depths, 'b-', linewidth=2, label=f'{f_res:.2f} Hz (1st mode)')
    ax2.fill_betweenx(depths, 0, np.real(disp), alpha=0.3)
    ax2.set_xlabel('Displacement [m]')
    ax2.set_ylabel('Depth [m]')
    ax2.set_title('Displacement Profile at Fundamental Resonance')
    ax2.invert_yaxis()
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    fig2.savefig('single_layer_profile.png', dpi=150, bbox_inches='tight')
    print("Plot saved: single_layer_profile.png")
    
    return system


def demo_two_layer():
    """Demonstration: Two-layer system (soil over bedrock)."""
    print("\n" + "=" * 60)
    print("DEMO: Two-Layer System (Soil over Bedrock)")
    print("=" * 60)
    
    # Layer 1: Sand
    sand = SoilLayer(
        thickness=15.0,
        vs=200.0,
        density=1900.0,
        damping=0.03,
        name="Sand"
    )
    
    # Layer 2: Stiff clay / weathered rock
    clay = SoilLayer(
        thickness=20.0,
        vs=350.0,
        density=2000.0,
        damping=0.02,
        name="Stiff Clay"
    )
    
    system = LayeredSystem([sand, clay])
    print(f"\n{system}")
    
    for layer in system.layers:
        print(f"\n  {layer}")
        print(f"    G = {layer.shear_modulus/1e6:.1f} MPa, Z = {layer.impedance_s:.0f} kg/(m²·s)")
    
    # Impedance contrast
    z1, z2 = sand.impedance_s, clay.impedance_s
    print(f"\nImpedance contrast: Z₂/Z₁ = {z2/z1:.2f}")
    print(f"Reflection coefficient: {(z2 - z1)/(z2 + z1):.3f}")
    
    # Plot amplification
    fig, ax = plot_amplification(system, 0.1, 50, WaveType.S_WAVE, "free_rigid")
    fig.savefig('two_layer_amplification.png', dpi=150, bbox_inches='tight')
    print("\nPlot saved: two_layer_amplification.png")
    
    # Plot properties
    fig2, _ = plot_layer_properties(system)
    fig2.savefig('two_layer_properties.png', dpi=150, bbox_inches='tight')
    print("Plot saved: two_layer_properties.png")
    
    # Displacement profiles at multiple frequencies
    freqs_to_plot = [2.0, 5.0, 10.0]
    fig3, _ = plot_displacement_profile(system, freqs_to_plot)
    fig3.savefig('two_layer_profiles.png', dpi=150, bbox_inches='tight')
    print("Plot saved: two_layer_profiles.png")
    
    return system


def demo_bender_element():
    """Demonstration: Bender element test analysis."""
    print("\n" + "=" * 60)
    print("DEMO: Bender Element Test Analysis")
    print("=" * 60)
    
    # Typical bender element setup
    # Sample length ~100mm, measuring S-wave velocity
    sample = SoilLayer(
        thickness=0.100,    # 100 mm
        vs=100.0,           # Unknown - to be determined
        density=1700.0,     # Loose sand
        damping=0.01,
        name="Sample"
    )
    
    system = LayeredSystem([sample])
    
    # Simulate travel time measurement
    # Frequency range typical for bender elements: 1-20 kHz
    freqs = np.linspace(1000, 20000, 1000)  # 1-20 kHz
    
    # Theoretical arrival time
    travel_time = sample.thickness / sample.vs
    print(f"\nSample: {sample.thickness*1000:.0f} mm long")
    print(f"Assumed Vs = {sample.vs:.1f} m/s")
    print(f"Travel time = {travel_time*1e6:.1f} μs")
    print(f"Travel distance = {sample.thickness*1000:.0f} mm")
    
    # Compute phase velocity from phase of transfer function
    omega = 2 * np.pi * freqs
    T = system.global_transfer_matrix(omega, WaveType.S_WAVE)
    
    # Extract phase
    if isinstance(T, list):
        phases = np.array([np.angle(t[0,0]) for t in T])
    else:
        phases = np.angle(T[0,0])
    
    # Group delay ≈ -dφ/dω
    group_delay = -np.diff(phases) / np.diff(omega)
    
    fig, axes = plt.subplots(2, 1, figsize=(10, 8))
    
    # Amplitude transfer
    axes[0].plot(freqs/1000, np.abs([t[0,0] for t in T] if isinstance(T, list) else T[0,0]), 'b-')
    axes[0].set_xlabel('Frequency [kHz]')
    axes[0].set_ylabel('|T₁₁|')
    axes[0].set_title('Transfer Function - Bender Element')
    axes[0].grid(True, alpha=0.3)
    
    # Group delay
    axes[1].plot(freqs[:-1]/1000, group_delay*1e6, 'r-', label='Measured')
    axes[1].axhline(y=travel_time*1e6, color='k', linestyle='--', label=f'Theoretical ({travel_time*1e6:.1f} μs)')
    axes[1].set_xlabel('Frequency [kHz]')
    axes[1].set_ylabel('Group Delay [μs]')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    fig.savefig('bender_element_analysis.png', dpi=150, bbox_inches='tight')
    print("\nPlot saved: bender_element_analysis.png")
    
    return system


def demo_resonance_column():
    """Demonstration: Resonance column test."""
    print("\n" + "=" * 60)
    print("DEMO: Resonance Column Test")
    print("=" * 60)
    
    # Typical resonance column sample
    # Cylindrical sample, fixed base, free top with mass
    sample = SoilLayer(
        thickness=0.200,    # 200 mm
        vs=120.0,           # Typical for loose sand
        density=1650.0,
        damping=0.02,
        name="Resonance Sample"
    )
    
    system = LayeredSystem([sample])
    
    print(f"\nSample properties:")
    print(f"  Height: {sample.thickness*1000:.0f} mm")
    print(f"  Vs: {sample.vs:.1f} m/s")
    print(f"  Density: {sample.density:.1f} kg/m³")
    print(f"  Shear modulus: {sample.shear_modulus/1e6:.2f} MPa")
    
    # Natural frequencies
    modes = system.resonance_modes(WaveType.S_WAVE)
    print(f"\nResonance frequencies:")
    for mode in modes[:3]:
        print(f"  Mode {mode['mode_number']}: {mode['frequency']:.2f} Hz")
    
    # Amplification with very fine frequency resolution
    freqs = np.linspace(0.1, 500, 5000)
    amp = system.amplification_function(freqs, WaveType.S_WAVE, "free_rigid")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(freqs, np.abs(amp), 'b-', linewidth=1)
    
    # Mark resonances
    for mode in modes[:3]:
        if mode['frequency'] <= 500:
            ax.axvline(x=mode['frequency'], color='r', linestyle='--', alpha=0.5)
            ax.text(mode['frequency'], np.max(np.abs(amp))*0.9, 
                   f"f₁ = {mode['frequency']:.1f} Hz", 
                   rotation=90, va='top', ha='right', color='r')
    
    ax.set_xlabel('Frequency [Hz]')
    ax.set_ylabel('Amplification Factor')
    ax.set_title('Resonance Column - Transfer Function')
    ax.set_xlim(0, 500)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    fig.savefig('resonance_column.png', dpi=150, bbox_inches='tight')
    print("\nPlot saved: resonance_column.png")
    
    return system


if __name__ == "__main__":
    print("Transfer Matrix Method for Wave Propagation in Soils")
    print("=" * 60)
    
    # Run demonstrations
    demo_single_layer()
    demo_two_layer()
    demo_bender_element()
    demo_resonance_column()
    
    print("\n" + "=" * 60)
    print("All demonstrations complete!")
    print("Generated plots:")
    print("  - single_layer_amplification.png")
    print("  - single_layer_profile.png")
    print("  - two_layer_amplification.png")
    print("  - two_layer_properties.png")
    print("  - two_layer_profiles.png")
    print("  - bender_element_analysis.png")
    print("  - resonance_column.png")
    print("=" * 60)
    
    plt.show()
