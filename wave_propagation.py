#!/usr/bin/env python3
"""
1D Shear Wave Propagation in Viscoelastic Medium
================================================

Solves the Kelvin-Voigt viscoelastic wave equation:
    ρ ∂²u/∂t² = G' ∂²u/∂x² + η ∂³u/∂x²∂t

Where:
    u(x,t) = displacement field
    G' = storage modulus (elastic component) [Pa]
    η = viscosity [Pa·s]
    ρ = density [kg/m³]

Usage:
    python wave_propagation.py

Output:
    - Wave propagation visualization
    - Dispersion curve: c_s(ω) vs frequency
    - Parameter sweep plots

Author: Acoustic NDE Research
Date: March 8, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize


class ViscoelasticWave1D:
    """
    1D shear wave simulator using Finite Difference Time Domain (FDTD).
    
    Implements Kelvin-Voigt viscoelastic model where stress is:
        σ = G'·ε + η·(dε/dt)
    """
    
    def __init__(self, nx=500, dx=0.001, dt=None, rho=1000, G_prime=5000, eta=5):
        """
        Initialize 1D viscoelastic wave simulation.
        
        Parameters:
        -----------
        nx : int
            Number of spatial grid points (default: 500)
        dx : float  
            Spatial step size in meters (default: 1 mm)
        dt : float or None
            Time step in seconds. If None, auto-computed from CFL condition
        rho : float
            Density in kg/m³ (default: 1000, soft tissue)
        G_prime : float
            Storage modulus in Pa (default: 5000 = 5 kPa, liver-typical)
        eta : float
            Viscosity in Pa·s (default: 5)
        """
        self.nx = nx
        self.dx = dx
        self.rho = rho
        self.G_prime = G_prime
        self.eta = eta
        
        # Compute theoretical wave speeds
        self.c_s_elastic = np.sqrt(G_prime / rho)
        
        # CFL condition for stability: c·dt/dx ≤ 1
        # Use 0.5 for safety margin
        if dt is None:
            self.dt = 0.5 * dx / self.c_s_elastic
        else:
            self.dt = dt
            
        # Verify stability
        courant = self.c_s_elastic * self.dt / self.dx
        if courant > 0.9:
            print(f"⚠️ Warning: CFL = {courant:.2f} may be unstable. Reduce dt.")
        
        # Spatial grid
        self.x = np.linspace(0, (nx-1)*dx, nx)
        
        # Initialize displacement fields
        self.u = np.zeros(nx)          # Current displacement
        self.u_prev = np.zeros(nx)     # Previous time step
        self.u_next = np.zeros(nx)     # Next time step
        
        # Storage for time history
        self.time_history = []
        self.displacement_history = []
        
    def add_source(self, t, source_type='tone_burst', f0=100, location=None, amplitude=1e-6):
        """
        Add source excitation at specific location.
        
        Parameters:
        -----------
        t : float
            Current time in seconds
        source_type : str
            'tone_burst' (sinusoid with Gaussian envelope) or 'ricker'
        f0 : float
            Center frequency in Hz (default: 100)
        location : int or None
            Grid index for source. None = nx//4 (quarter point)
        amplitude : float
            Source amplitude in meters (default: 1 micron)
        """
        if location is None:
            location = self.nx // 4
        
        if source_type == 'tone_burst':
            # Tone burst: sinusoid with Gaussian envelope
            n_cycles = 3
            sigma = n_cycles / f0
            envelope = np.exp(-(t - 3*sigma)**2 / (2*(sigma/3)**2))
            source_val = amplitude * envelope * np.sin(2*np.pi*f0*t)
            
        elif source_type == 'ricker':
            # Ricker (Mexican hat) wavelet
            sigma = 1 / (np.pi * f0)
            tau = t - 3*sigma
            source_val = amplitude * (1 - 2*(tau/sigma)**2) * np.exp(-(tau/sigma)**2)
        else:
            raise ValueError(f"Unknown source type: {source_type}")
        
        self.u[location] += source_val
    
    def step(self):
        """
        Advance simulation by one time step using FDTD.
        
        Updates self.u to next time step using Kelvin-Voigt wave equation.
        """
        # Spatial second derivative (central difference)
        d2u_dx2 = np.zeros(self.nx)
        d2u_dx2[1:-1] = (self.u[2:] - 2*self.u[1:-1] + self.u[:-2]) / self.dx**2
        
        # Velocity for viscous term
        velocity = (self.u - self.u_prev) / self.dt
        d2v_dx2 = np.zeros(self.nx)
        d2v_dx2[1:-1] = (velocity[2:] - 2*velocity[1:-1] + velocity[:-2]) / self.dx**2
        
        # Update equation: ρ·ü = G'·u'' + η·v''
        elastic_term = (self.dt**2 * self.G_prime / self.rho) * d2u_dx2
        viscous_term = (self.dt**3 * self.eta / self.rho) * d2v_dx2
        
        self.u_next[1:-1] = (2*self.u[1:-1] - self.u_prev[1:-1] 
                             + elastic_term[1:-1] + viscous_term[1:-1])
        
        # Absorbing boundary conditions (Mur 1st order)
        self._apply_abc()
        
        # Update fields
        self.u_prev[:] = self.u[:]
        self.u[:] = self.u_next[:]
    
    def _apply_abc(self):
        """Apply absorbing boundary conditions to reduce reflections."""
        # Left boundary
        if self.c_s_elastic * self.dt < self.dx:
            coeff = (self.c_s_elastic*self.dt - self.dx) / (self.c_s_elastic*self.dt + self.dx)
            self.u[0] = self.u_prev[1] + coeff * (self.u[1] - self.u_prev[0])
            # Right boundary
            self.u[-1] = self.u_prev[-2] + coeff * (self.u[-2] - self.u_prev[-1])
    
    def record(self, t):
        """Record current state for analysis."""
        self.time_history.append(t)
        self.displacement_history.append(self.u.copy())
    
    def phase_velocity_at_point(self, x_position, freq, dx_dt_threshold=1e-7):
        """
        Compute phase velocity at a specific point from time history.
        
        Parameters:
        -----------
        x_position : int
            Grid index where to measure
        freq : float
            Expected frequency in Hz
        dx_dt_threshold : float
            Threshold for detecting zero crossings
            
        Returns:
        --------
        c_s : float
            Phase velocity in m/s
        """
        if len(self.displacement_history) < 10:
            return None
        
        # Extract time series at this position
        u_series = np.array([d[x_position] for d in self.displacement_history])
        t_series = np.array(self.time_history)
        
        # Find zero crossings to measure period
        zero_crossings = []
        for i in range(1, len(u_series)):
            if u_series[i-1] < 0 and u_series[i] >= 0:
                # Linear interpolation for better accuracy
                t_cross = t_series[i-1] + (t_series[i] - t_series[i-1]) * \
                         (-u_series[i-1]) / (u_series[i] - u_series[i-1])
                zero_crossings.append(t_cross)
        
        if len(zero_crossings) < 2:
            return None
        
        # Calculate period and wavelength
        periods = np.diff(zero_crossings)
        T = np.mean(periods) * 2  # Full period (zero crossings are half period)
        f_measured = 1 / T
        
        # Distance from source
        source_pos = self.nx // 4
        distance = abs(x_position - source_pos) * self.dx
        
        # Time of flight
        if len(zero_crossings) > 0:
            time_of_flight = zero_crossings[0] - self.time_history[0]
            c_s = distance / time_of_flight if time_of_flight > 0 else None
            return c_s
        
        return None


def analytical_phase_velocity(omega, G_prime, eta, rho=1000):
    """
    Analytical dispersion relation for Kelvin-Voigt model.
    
    c_s(ω) = sqrt(sqrt(G'^2 + (ω*η)^2) / ρ)
    
    Parameters:
    -----------
    omega : float or array
        Angular frequency(ies) in rad/s
    G_prime : float
        Storage modulus in Pa
    eta : float
        Viscosity in Pa·s
    rho : float
        Density in kg/m³
        
    Returns:
    --------
    c_s : float or array
        Phase velocity(ies) in m/s
    """
    G_complex_mag = np.sqrt(G_prime**2 + (omega * eta)**2)
    c_s = np.sqrt(G_complex_mag / rho)
    return c_s


def run_single_simulation():
    """Run a single simulation and visualize wave propagation."""
    print("=" * 60)
    print("1D SHEAR WAVE PROPAGATION SIMULATION")
    print("=" * 60)
    
    # Parameters (healthy liver)
    rho = 1000          # kg/m³
    G_prime = 5000      # Pa (5 kPa)
    eta = 5             # Pa·s
    f0 = 100            # Hz
    
    # Setup
    sim = ViscoelasticWave1D(nx=500, dx=0.001, rho=rho, G_prime=G_prime, eta=eta)
    
    print(f"\nParameters:")
    print(f"  G' = {G_prime} Pa ({G_prime/1000} kPa)")
    print(f"  η = {eta} Pa·s")
    print(f"  ρ = {rho} kg/m³")
    print(f"  f = {f0} Hz")
    print(f"  Elastic wave speed: {sim.c_s_elastic:.2f} m/s")
    print(f"  Grid: {sim.nx} points, dx = {sim.dx*1000:.2f} mm")
    print(f"  Time step: {sim.dt*1e6:.2f} μs")
    
    # Run simulation
    duration = 0.03  # 30 ms
    n_steps = int(duration / sim.dt)
    save_every = 50
    
    print(f"\nRunning {n_steps} time steps...")
    
    u_snapshots = []
    t_snapshots = []
    
    for n in range(n_steps):
        t = n * sim.dt
        sim.add_source(t, source_type='tone_burst', f0=f0, amplitude=1e-6)
        sim.step()
        
        if n % save_every == 0:
            sim.record(t)
            u_snapshots.append(sim.u.copy())
            t_snapshots.append(t)
        
        if n % 1000 == 0:
            print(f"  Step {n}/{n_steps}")
    
    print("Simulation complete!")
    
    # Plot results
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Plot 1: Wave propagation snapshots
    ax = axes[0, 0]
    x_cm = sim.x * 100
    times_to_plot = [0, len(u_snapshots)//3, 2*len(u_snapshots)//3, -1]
    colors = plt.cm.viridis(np.linspace(0, 1, len(times_to_plot)))
    
    for idx, color in zip(times_to_plot, colors):
        ax.plot(x_cm, u_snapshots[idx] * 1e6, color=color, 
               label=f't = {t_snapshots[idx]*1000:.1f} ms')
    
    ax.axvline(x=x_cm[sim.nx//4], color='red', linestyle='--', alpha=0.5, label='Source')
    ax.set_xlabel('Position (cm)')
    ax.set_ylabel('Displacement (μm)')
    ax.set_title(f'Wave Propagation: f={f0} Hz, G\'={G_prime/1000}kPa, η={eta}Pa·s')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 2: Space-time diagram
    ax = axes[0, 1]
    u_array = np.array(u_snapshots)
    extent = [x_cm[0], x_cm[-1], t_snapshots[-1]*1000, t_snapshots[0]*1000]
    im = ax.imshow(u_array * 1e6, aspect='auto', extent=extent, cmap='RdBu_r')
    ax.set_xlabel('Position (cm)')
    ax.set_ylabel('Time (ms)')
    ax.set_title('Space-Time Diagram')
    plt.colorbar(im, ax=ax, label='Displacement (μm)')
    
    # Plot 3: Dispersion curve (analytical)
    ax = axes[1, 0]
    frequencies = np.linspace(10, 500, 100)
    omega = 2 * np.pi * frequencies
    c_s = analytical_phase_velocity(omega, G_prime, eta, rho)
    
    ax.plot(frequencies, c_s, 'b-', linewidth=2, label='Viscoelastic (KV)')
    ax.axhline(y=sim.c_s_elastic, color='r', linestyle='--', 
              label=f'Elastic limit (√(G\'/ρ))')
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Phase Velocity (m/s)')
    ax.set_title('Dispersion Curve: c_s(ω)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 4: Velocity vs viscosity
    ax = axes[1, 1]
    etas = [0, 1, 5, 10, 20]
    colors = plt.cm.viridis(np.linspace(0, 1, len(etas)))
    
    for eta_val, color in zip(etas, colors):
        c_s = analytical_phase_velocity(omega, G_prime, eta_val, rho)
        ax.plot(frequencies, c_s, color=color, label=f'η = {eta_val} Pa·s')
    
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Phase Velocity (m/s)')
    ax.set_title('Effect of Viscosity on Dispersion')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('wave_propagation_results.png', dpi=150)
    print("\nSaved: wave_propagation_results.png")
    # plt.show()  # Commented out for non-interactive environments
    
    return sim


def parameter_sweep_demo():
    """Demonstrate parameter sweep for different tissue conditions."""
    print("\n" + "=" * 60)
    print("PARAMETER SWEEP: LIVER CONDITIONS")
    print("=" * 60)
    
    # Define tissue conditions
    conditions = [
        ('Healthy', 4000, 2),      # G'=4kPa, η=2
        ('Mild Fibrosis', 8000, 3), # G'=8kPa, η=3
        ('Inflammation', 6000, 10), # G'=6kPa, η=10
        ('Severe Fibrosis', 20000, 5) # G'=20kPa, η=5
    ]
    
    frequencies = np.linspace(10, 500, 100)
    omega = 2 * np.pi * frequencies
    rho = 1000
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    for name, Gp, eta in conditions:
        c_s = analytical_phase_velocity(omega, Gp, eta, rho)
        
        # Plot 1: Dispersion curves
        ax1.plot(frequencies, c_s, linewidth=2, label=f'{name} (G\'={Gp/1000}kPa, η={eta})')
        
        # Plot 2: Normalized to elastic limit
        c_elastic = np.sqrt(Gp / rho)
        ax2.plot(frequencies, c_s / c_elastic, linewidth=2, 
                label=f'{name} (dispersion strength)')
    
    ax1.set_xlabel('Frequency (Hz)')
    ax1.set_ylabel('Phase Velocity (m/s)')
    ax1.set_title('Dispersion Curves for Liver Conditions')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    ax2.set_xlabel('Frequency (Hz)')
    ax2.set_ylabel('c_s(ω) / c_s(elastic)')
    ax2.set_title('Dispersion Strength (Ratio)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('parameter_sweep.png', dpi=150)
    print("\nSaved: parameter_sweep.png")
    # plt.show()  # Commented out for non-interactive environments
    
    # Print table
    print("\nPhase Velocity at 100 Hz and 400 Hz:")
    print("-" * 60)
    print(f"{'Condition':<20} {'G\' (kPa)':<12} {'η (Pa·s)':<12} {'c@100Hz':<12} {'c@400Hz':<12}")
    print("-" * 60)
    for name, Gp, eta in conditions:
        c_100 = analytical_phase_velocity(2*np.pi*100, Gp, eta, rho)
        c_400 = analytical_phase_velocity(2*np.pi*400, Gp, eta, rho)
        print(f"{name:<20} {Gp/1000:<12.1f} {eta:<12.1f} {c_100:<12.2f} {c_400:<12.2f}")


if __name__ == "__main__":
    # Run main simulation
    sim = run_single_simulation()
    
    # Run parameter sweep
    parameter_sweep_demo()
    
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("1. Modify G_prime and eta to see different behaviors")
    print("2. Try different frequencies (f0)")
    print("3. Add noise to simulate measurement uncertainty")
    print("4. Implement inverse problem to recover G' and η")
    print("=" * 60)
