"""
1D Shear Wave Propagation in Viscoelastic Medium
================================================

Starter code for simulating shear wave propagation in a 1D viscoelastic rod.
This is the simplest possible model to understand the physics before moving to 2D/3D.

Physics:
--------
∂²u/∂t² = (G'/ρ) ∂²u/∂x² + (η/ρ) ∂³u/∂x²∂t

Where:
- u(x,t) = displacement
- G' = storage modulus (elastic)
- η = viscosity (G'' = ωη for KV model)
- ρ = density

For Kelvin-Voigt model: Stress = G'·strain + η·strain_rate

Author: Research Project — Week 2
Date: March 7, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


class ShearWave1D:
    """
    1D shear wave simulator using finite difference time domain (FDTD).
    """
    
    def __init__(self, nx=1000, dx=0.001, dt=1e-6, rho=1000, G_prime=5000, eta=5):
        """
        Initialize 1D shear wave simulation.
        
        Parameters:
        -----------
        nx : int
            Number of spatial grid points
        dx : float
            Spatial step size (m)
        dt : float
            Time step size (s)
        rho : float
            Density (kg/m³) — default 1000 (soft tissue)
        G_prime : float
            Storage modulus (Pa) — default 5000 (~5 kPa, liver-typical)
        eta : float
            Viscosity (Pa·s) — default 5 Pa·s
        """
        self.nx = nx
        self.dx = dx
        self.dt = dt
        self.rho = rho
        self.G_prime = G_prime
        self.eta = eta
        
        # Derived parameters
        self.c_s = np.sqrt(G_prime / rho)  # Shear wave speed (elastic)
        self.tau = eta / G_prime  # Relaxation time
        
        # Stability check (CFL condition modified for viscoelasticity)
        self.courant = self.c_s * dt / dx
        if self.courant > 1:
            print(f"⚠️ Warning: CFL = {self.courant:.3f} > 1. Reduce dt or increase dx.")
        
        # Initialize fields
        self.x = np.linspace(0, (nx-1)*dx, nx)
        self.u = np.zeros(nx)  # Displacement
        self.u_prev = np.zeros(nx)  # Displacement at t-1
        self.u_next = np.zeros(nx)  # Displacement at t+1
        
        # Time history for dispersion analysis
        self.time_history = []
        self.displacement_history = []
        
    def add_source(self, t, source_type='ricker', f0=100, location=None, amplitude=1e-6):
        """
        Add source excitation at specific location.
        
        Parameters:
        -----------
        t : float
            Current time
        source_type : str
            'ricker' (Mexican hat wavelet) or 'tone_burst'
        f0 : float
            Center frequency (Hz)
        location : int
            Grid index for source (default: center)
        amplitude : float
            Source amplitude (m)
        """
        if location is None:
            location = self.nx // 4  # Place at 1/4 point
        
        if source_type == 'ricker':
            # Ricker wavelet (second derivative of Gaussian)
            sigma = 1 / (np.pi * f0)  # Time width
            tau = t - 3*sigma  # Shift to start at ~0
            source_val = amplitude * (1 - 2*(tau/sigma)**2) * np.exp(-(tau/sigma)**2)
        elif source_type == 'tone_burst':
            # Tone burst (sinusoid with Gaussian envelope)
            sigma = 3 / f0  # 3 cycles
            envelope = np.exp(-(t - 3*sigma)**2 / (2*(sigma/3)**2))
            source_val = amplitude * envelope * np.sin(2*np.pi*f0*t)
        else:
            raise ValueError(f"Unknown source type: {source_type}")
        
        self.u[location] += source_val
        
    def step(self):
        """
        Advance simulation by one time step using FDTD.
        
        Kelvin-Voigt model: ρ ∂²u/∂t² = G' ∂²u/∂x² + η ∂³u/∂x²∂t
        
        Discretized:
        u^{n+1} = 2u^n - u^{n-1} + (dt²/ρ)[G'·∂²u^n/∂x² + (η/dt)(∂²u^n/∂x² - ∂²u^{n-1}/∂x²)]
        """
        # Compute spatial Laplacian ∇²u for current and previous time steps
        def laplacian(field):
            result = np.zeros_like(field)
            result[1:-1] = (field[2:] - 2*field[1:-1] + field[:-2]) / self.dx**2
            return result
        
        lap_u_n = laplacian(self.u)       # ∂²u^n/∂x²
        lap_u_nm1 = laplacian(self.u_prev) # ∂²u^{n-1}/∂x²
        
        # Elastic term: G' · ∂²u^n/∂x²
        elastic_force = self.G_prime * lap_u_n
        
        # Viscous term: (η/dt) · (∂²u^n/∂x² - ∂²u^{n-1}/∂x²)
        # This represents η · ∂³u/∂x²∂t using backward Euler for time derivative
        viscous_force = (self.eta / self.dt) * (lap_u_n - lap_u_nm1)
        
        # Total acceleration
        acceleration = (elastic_force + viscous_force) / self.rho
        
        # Update: u^{n+1} = 2u^n - u^{n-1} + dt² · acceleration
        self.u_next[:] = 2*self.u - self.u_prev + self.dt**2 * acceleration
        
        # Absorbing boundary conditions (simple Mur 1st order)
        self._apply_abc()
        
        # Update fields for next iteration
        self.u_prev, self.u, self.u_next = self.u, self.u_next, self.u_prev
        
    def _apply_abc(self):
        """
        Simple absorbing boundary condition (1st order Mur).
        Reduces reflections at boundaries.
        """
        # Left boundary
        self.u[0] = self.u_prev[1] + (self.c_s*self.dt - self.dx)/(self.c_s*self.dt + self.dx) * (self.u[1] - self.u_prev[0])
        # Right boundary
        self.u[-1] = self.u_prev[-2] + (self.c_s*self.dt - self.dx)/(self.c_s*self.dt + self.dx) * (self.u[-2] - self.u_prev[-1])
        
    def record(self, t):
        """Record time history for analysis."""
        self.time_history.append(t)
        self.displacement_history.append(self.u.copy())
        
    def extract_dispersion(self, x_positions, freq_range=(50, 500), n_fft=2048):
        """
        Extract phase velocity dispersion curve from time history.
        
        Parameters:
        -----------
        x_positions : list of int
            Grid indices where displacement was recorded
        freq_range : tuple
            (min_freq, max_freq) to analyze
        n_fft : int
            FFT size for frequency resolution
            
        Returns:
        --------
        freqs : array
            Frequencies (Hz)
        phase_velocity : array
            Phase velocity at each frequency (m/s)
        """
        if len(self.displacement_history) < 10:
            raise ValueError("Not enough time steps recorded. Run simulation longer.")
        
        # Convert history to array (time, space)
        u_history = np.array(self.displacement_history)
        dt = self.time_history[1] - self.time_history[0]
        
        # FFT of displacement at each position
        freqs = np.fft.rfftfreq(n_fft, dt)
        
        # Find indices in frequency range
        freq_mask = (freqs >= freq_range[0]) & (freqs <= freq_range[1])
        freqs = freqs[freq_mask]
        
        phase_velocities = []
        
        for x_pos in x_positions:
            # FFT of displacement at this position
            u_fft = np.fft.rfft(u_history[:, x_pos], n=n_fft)
            u_fft = u_fft[freq_mask]
            
            # Phase
            phase = np.angle(u_fft)
            
            # Phase velocity: c = ωx/Δφ (for multiple positions, use phase difference)
            # Simplified: for single position, we need reference
            pass
        
        # For now, return simplified analysis
        # Full dispersion extraction needs multiple receiver positions
        # This is a placeholder for the concept
        
        return freqs, None  # TODO: implement full dispersion extraction


def simulate_single_frequency():
    """
    Run a single-frequency simulation and visualize the wave propagation.
    """
    print("=" * 60)
    print("1D Shear Wave Simulation: Single Frequency")
    print("=" * 60)
    
    # Parameters (liver-typical)
    rho = 1000  # kg/m³
    G_prime = 5000  # Pa (~5 kPa, healthy liver)
    eta = 5  # Pa·s
    f0 = 100  # Hz (typical clinical frequency)
    
    # Spatial/temporal discretization
    c_s = np.sqrt(G_prime / rho)
    wavelength = c_s / f0
    dx = wavelength / 20  # 20 points per wavelength
    dt = dx / (2*c_s)  # CFL = 0.5 for stability
    
    nx = 2000  # Grid points
    duration = 0.05  # Simulation time (s)
    n_steps = int(duration / dt)
    
    print(f"Shear wave speed: {c_s:.2f} m/s")
    print(f"Wavelength: {wavelength*100:.2f} cm")
    print(f"Grid spacing: {dx*1000:.3f} mm")
    print(f"Time step: {dt*1e6:.2f} μs")
    print(f"CFL number: {c_s*dt/dx:.3f}")
    print(f"Simulation steps: {n_steps}")
    
    # Create simulator
    sim = ShearWave1D(nx=nx, dx=dx, dt=dt, rho=rho, G_prime=G_prime, eta=eta)
    
    # Storage for animation
    storage_interval = 50
    u_storage = []
    t_storage = []
    
    # Run simulation
    for n in range(n_steps):
        t = n * dt
        
        # Add source (tone burst at 100 Hz)
        sim.add_source(t, source_type='tone_burst', f0=f0, amplitude=1e-6)
        
        # Step forward
        sim.step()
        
        # Record
        if n % storage_interval == 0:
            sim.record(t)
            u_storage.append(sim.u.copy())
            t_storage.append(t)
        
        if n % 1000 == 0:
            print(f"Step {n}/{n_steps} ({100*n/n_steps:.1f}%)")
    
    print("Simulation complete. Generating visualization...")
    
    # Plot wave propagation snapshots
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    axes = axes.flatten()
    
    x_cm = sim.x * 100  # Convert to cm
    
    snapshot_indices = [0, len(u_storage)//5, 2*len(u_storage)//5, 
                       3*len(u_storage)//5, 4*len(u_storage)//5, -1]
    
    for idx, ax in enumerate(axes):
        i = snapshot_indices[idx]
        ax.plot(x_cm, u_storage[i] * 1e6, 'b-', linewidth=0.8)  # μm
        ax.axvline(x=x_cm[nx//4], color='r', linestyle='--', alpha=0.5, label='Source')
        ax.set_xlabel('Position (cm)')
        ax.set_ylabel('Displacement (μm)')
        ax.set_title(f't = {t_storage[i]*1000:.1f} ms')
        ax.set_xlim(0, x_cm[-1])
        ax.grid(True, alpha=0.3)
        ax.legend()
    
    plt.suptitle(f'1D Shear Wave Propagation: f={f0} Hz, G\'={G_prime} Pa, η={eta} Pa·s', 
                 fontsize=14)
    plt.tight_layout()
    plt.savefig('shear_wave_snapshots.png', dpi=150)
    plt.show()
    
    print("Saved: shear_wave_snapshots.png")
    
    return sim, u_storage, t_storage


def compare_elastic_vs_viscoelastic():
    """
    Compare wave propagation in purely elastic vs viscoelastic media.
    """
    print("=" * 60)
    print("Comparison: Elastic vs Viscoelastic")
    print("=" * 60)
    
    # Common parameters
    rho = 1000
    G_prime = 5000
    f0 = 100
    
    # Elastic case (eta = 0)
    sim_elastic = ShearWave1D(nx=1500, dx=0.0005, dt=0.25e-6, 
                               rho=rho, G_prime=G_prime, eta=0)
    
    # Viscoelastic case
    eta = 10  # Pa·s
    sim_visco = ShearWave1D(nx=1500, dx=0.0005, dt=0.25e-6, 
                             rho=rho, G_prime=G_prime, eta=eta)
    
    # Run both simulations
    duration = 0.03
    n_steps = int(duration / sim_elastic.dt)
    
    u_elastic = []
    u_visco = []
    
    for n in range(n_steps):
        t = n * sim_elastic.dt
        
        sim_elastic.add_source(t, f0=f0, amplitude=1e-6)
        sim_visco.add_source(t, f0=f0, amplitude=1e-6)
        
        sim_elastic.step()
        sim_visco.step()
        
        if n % 100 == 0:
            u_elastic.append(sim_elastic.u.copy())
            u_visco.append(sim_visco.u.copy())
    
    # Plot comparison
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    x_cm = sim_elastic.x * 100
    
    # Plot at final time
    axes[0].plot(x_cm, u_elastic[-1] * 1e6, 'b-', linewidth=1, label='Elastic (η=0)')
    axes[0].plot(x_cm, u_visco[-1] * 1e6, 'r-', linewidth=1, label=f'Viscoelastic (η={eta})')
    axes[0].axvline(x=x_cm[1500//4], color='k', linestyle='--', alpha=0.5, label='Source')
    axes[0].set_xlabel('Position (cm)')
    axes[0].set_ylabel('Displacement (μm)')
    axes[0].set_title('Wave Profile Comparison')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Plot amplitude decay vs distance
    source_pos = 1500 // 4
    distances = x_cm[source_pos:] - x_cm[source_pos]
    amp_elastic = np.abs(u_elastic[-1][source_pos:])
    amp_visco = np.abs(u_visco[-1][source_pos:])
    
    axes[1].semilogy(distances, amp_elastic * 1e6 + 1e-9, 'b-', linewidth=1, label='Elastic')
    axes[1].semilogy(distances, amp_visco * 1e6 + 1e-9, 'r-', linewidth=1, label='Viscoelastic')
    axes[1].set_xlabel('Distance from source (cm)')
    axes[1].set_ylabel('Amplitude (μm, log scale)')
    axes[1].set_title('Amplitude Attenuation')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.suptitle('Elastic vs Viscoelastic Shear Wave Propagation', fontsize=14)
    plt.tight_layout()
    plt.savefig('elastic_vs_viscoelastic.png', dpi=150)
    plt.show()
    
    print("\nKey observations:")
    print("- Elastic: Wave propagates without amplitude decay")
    print("- Viscoelastic: Amplitude decays due to viscous dissipation")
    print("- Phase velocity may also differ slightly")
    
    return sim_elastic, sim_visco


def dispersion_analysis_demo():
    """
    Demonstrate frequency-dependent phase velocity (dispersion).
    """
    print("=" * 60)
    print("Dispersion Analysis Demo")
    print("=" * 60)
    
    rho = 1000
    G_prime = 5000
    eta = 10  # Significant viscosity for dispersion
    
    frequencies = [50, 100, 200, 300, 400]  # Hz
    colors = plt.cm.viridis(np.linspace(0, 1, len(frequencies)))
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    for f0, color in zip(frequencies, colors):
        c_s = np.sqrt(G_prime / rho)
        wavelength = c_s / f0
        dx = wavelength / 20
        dt = dx / (2*c_s)
        
        sim = ShearWave1D(nx=2000, dx=dx, dt=dt, rho=rho, G_prime=G_prime, eta=eta)
        
        n_steps = int(0.04 / dt)
        u_max = []
        
        for n in range(n_steps):
            t = n * dt
            sim.add_source(t, f0=f0, amplitude=1e-6)
            sim.step()
            u_max.append(np.max(np.abs(sim.u)))
        
        x_cm = sim.x * 100
        ax.plot(x_cm, sim.u * 1e6, color=color, linewidth=1, 
               label=f'f = {f0} Hz')
    
    ax.set_xlabel('Position (cm)')
    ax.set_ylabel('Displacement (μm)')
    ax.set_title('Shear Wave Dispersion: Higher Frequencies Attenuate Faster')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 20)
    
    plt.tight_layout()
    plt.savefig('dispersion_demo.png', dpi=150)
    plt.show()
    
    print("\nKey observation:")
    print("Higher frequencies attenuate more rapidly due to viscosity")
    print("This frequency-dependent attenuation is the 'dispersion'")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("1D SHEAR WAVE SIMULATION SUITE")
    print("Acoustic Research Project — Week 2 Starter Code")
    print("=" * 60 + "\n")
    
    # Run simulations
    print("\n[1] Running single frequency simulation...")
    sim1, u1, t1 = simulate_single_frequency()
    
    print("\n[2] Comparing elastic vs viscoelastic...")
    sim_elastic, sim_visco = compare_elastic_vs_viscoelastic()
    
    print("\n[3] Dispersion analysis...")
    dispersion_analysis_demo()
    
    print("\n" + "=" * 60)
    print("All simulations complete!")
    print("Next steps:")
    print("- Modify parameters (G', η, f0) to see effects")
    print("- Implement multi-frequency source for dispersion extraction")
    print("- Add inverse problem solver to recover (G', η) from data")
    print("=" * 60)
