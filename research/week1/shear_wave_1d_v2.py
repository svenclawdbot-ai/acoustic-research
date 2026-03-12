"""
1D Shear Wave Propagation - Velocity-Stress Formulation
========================================================

Standard FDTD approach using velocity-stress formulation for Kelvin-Voigt viscoelasticity.
This is the industry-standard approach used in seismic/acoustic FDTD codes.

Physics (Kelvin-Voigt):
  Stress: σ = G'·ε + η·∂ε/∂t
  Momentum: ρ·∂v/∂t = ∂σ/∂x
  Strain rate: ∂ε/∂t = ∂v/∂x

Discretization (staggered grid):
  - Velocity v at integer time steps, half-integer space (or same grid)
  - Stress σ at half-integer time steps, integer space
  - Standard leapfrog time stepping

Stability condition (CFL):
  dt ≤ dx / c_s where c_s = √(G'/ρ)

Author: Research Project — Week 2
Date: March 12, 2026
"""

import numpy as np
import matplotlib.pyplot as plt


class ShearWave1D:
    """
    1D shear wave simulator using velocity-stress FDTD.
    Stable implementation for Kelvin-Voigt viscoelasticity.
    """
    
    def __init__(self, nx=1000, dx=0.001, dt=None, rho=1000, G_prime=5000, eta=5):
        """
        Initialize 1D shear wave simulation.
        
        Parameters:
        -----------
        nx : int
            Number of spatial grid points
        dx : float
            Spatial step size (m)
        dt : float or None
            Time step size (s). If None, computed from CFL condition.
        rho : float
            Density (kg/m³)
        G_prime : float
            Storage modulus (Pa)
        eta : float
            Viscosity (Pa·s)
        """
        self.nx = nx
        self.dx = dx
        self.rho = rho
        self.G_prime = G_prime
        self.eta = eta
        
        # Shear wave speed
        self.c_s = np.sqrt(G_prime / rho)
        
        # Relaxation time
        self.tau = eta / G_prime if G_prime > 0 else 0
        
        # Auto-compute dt if not provided
        if dt is None:
            # Wave CFL: dt <= dx / c_s
            # Use more conservative factor for stability
            dt_wave = 0.3 * dx / self.c_s
            
            # Viscous stability: dt <= rho * dx^2 / (2 * eta)
            if eta > 0:
                dt_viscous = 0.5 * rho * dx**2 / (2 * eta)
                self.dt = min(dt_wave, dt_viscous)
            else:
                self.dt = dt_wave
        else:
            self.dt = dt
        
        # CFL check
        self.courant = self.c_s * self.dt / self.dx
        if self.courant > 1.0:
            print(f"⚠️ Warning: CFL = {self.courant:.3f} > 1.0. May be unstable.")
        else:
            print(f"✓ CFL = {self.courant:.3f} (stable)")
        
        # Grid
        self.x = np.linspace(0, (nx-1)*dx, nx)
        
        # Fields (staggered in time)
        self.v = np.zeros(nx)  # Velocity v(t)
        self.v_half = np.zeros(nx)  # Velocity at t+dt/2
        
        self.sigma = np.zeros(nx)  # Stress σ(t+dt/2)
        self.sigma_half = np.zeros(nx)  # Stress at t+dt
        
        self.epsilon = np.zeros(nx)  # Strain ε(t)
        
        # For output
        self.u = np.zeros(nx)  # Displacement (computed by integrating v)
        
        # Time history
        self.time_history = []
        self.displacement_history = []
        
    def add_source(self, t, source_type='ricker', f0=100, location=None, amplitude=1e-6):
        """
        Add source as velocity injection or force.
        Using force source: adds to velocity equation.
        """
        if location is None:
            location = self.nx // 4
        
        # Source as force (adds to stress gradient)
        if source_type == 'ricker':
            sigma = 1 / (np.pi * f0)
            tau = t - 3*sigma
            source_val = amplitude * (1 - 2*(tau/sigma)**2) * np.exp(-(tau/sigma)**2)
        elif source_type == 'tone_burst':
            sigma = 3 / f0
            envelope = np.exp(-(t - 3*sigma)**2 / (2*(sigma/3)**2))
            source_val = amplitude * envelope * np.sin(2*np.pi*f0*t)
        else:
            raise ValueError(f"Unknown source type: {source_type}")
        
        # Apply as velocity source (equivalent to force/rho)
        self.v[location] += source_val * self.dt / self.rho
        
    def step(self):
        """
        One FDTD time step using velocity-stress formulation.
        
        Update sequence:
        1. Update strain from velocity gradient: ε += dt * ∂v/∂x
        2. Update stress from strain: σ = G'·ε + η·∂ε/∂t
        3. Update velocity from stress gradient: v += dt/ρ * ∂σ/∂x
        """
        dt = self.dt
        dx = self.dx
        rho = self.rho
        G = self.G_prime
        eta = self.eta
        
        # Spatial derivatives (central difference)
        def d_dx(field):
            result = np.zeros_like(field)
            result[1:-1] = (field[2:] - field[:-2]) / (2*dx)
            return result
        
        # Step 1: Update strain rate and strain
        # ∂ε/∂t = ∂v/∂x
        strain_rate = d_dx(self.v)
        
        # Step 2: Update stress (Kelvin-Voigt: σ = G'·ε + η·strain_rate)
        # Use semi-implicit: ε at n+1/2 ≈ ε + 0.5*dt*strain_rate
        epsilon_half = self.epsilon + 0.5 * dt * strain_rate
        sigma_new = G * epsilon_half + eta * strain_rate
        
        # Step 3: Update velocity from stress gradient
        # ρ·∂v/∂t = ∂σ/∂x
        d_sigma_dx = d_dx(sigma_new)
        v_new = self.v + dt / rho * d_sigma_dx
        
        # Update fields
        self.sigma = sigma_new
        self.v = v_new
        self.epsilon = self.epsilon + dt * strain_rate  # Full update for strain
        
        # Update displacement (for output)
        self.u = self.u + dt * self.v
        
        # Apply ABC
        self._apply_abc()
        
    def _apply_abc(self):
        """
        Sponge layer absorbing boundary condition.
        Gradually damps fields near boundaries to prevent reflections.
        """
        sponge_width = 60  # Increased from 40
        damping_strength = 0.25  # Increased from 0.15
        
        for i in range(sponge_width):
            # Parabolic damping profile
            damping_left = (i / sponge_width) ** 2
            damping_right = ((sponge_width - 1 - i) / sponge_width) ** 2
            
            # Apply damping to fields
            self.v[i] *= (1 - damping_strength * damping_left)
            self.sigma[i] *= (1 - damping_strength * damping_left)
            self.epsilon[i] *= (1 - damping_strength * damping_left)
            
            self.v[-(i+1)] *= (1 - damping_strength * damping_right)
            self.sigma[-(i+1)] *= (1 - damping_strength * damping_right)
            self.epsilon[-(i+1)] *= (1 - damping_strength * damping_right)
        
    def record(self, t):
        """Record time history."""
        self.time_history.append(t)
        self.displacement_history.append(self.u.copy())


def quick_test():
    """Quick validation test."""
    print("=" * 60)
    print("1D SHEAR WAVE SIMULATOR - VELOCITY-STRESS FORMULATION")
    print("=" * 60)
    
    # Test parameters
    rho = 1000
    G_prime = 5000
    eta = 0  # Start with elastic
    f0 = 100
    
    # Grid
    nx = 400
    dx = 0.001
    
    print(f"\nParameters:")
    print(f"  G' = {G_prime} Pa")
    print(f"  η = {eta} Pa·s")
    print(f"  ρ = {rho} kg/m³")
    print(f"  c_s = {np.sqrt(G_prime/rho):.2f} m/s")
    
    # Create simulator
    sim = ShearWave1D(nx=nx, dx=dx, rho=rho, G_prime=G_prime, eta=eta)
    
    # Run simulation
    duration = 0.03
    n_steps = int(duration / sim.dt)
    print(f"\nRunning {n_steps} steps...")
    
    snapshots = []
    times = []
    
    for n in range(n_steps):
        t = n * sim.dt
        
        # Source
        if n < 100:
            sim.add_source(t, f0=f0, amplitude=1e-4)
        
        sim.step()
        
        if n % 50 == 0:
            snapshots.append(sim.u.copy())
            times.append(t)
    
    print(f"✓ Simulation complete")
    print(f"  Final max |u|: {np.max(np.abs(sim.u)):.6e} m")
    
    # Check for NaN
    if np.any(np.isnan(sim.u)):
        print("  ✗ NaN detected!")
    else:
        print("  ✓ No NaN")
    
    # Plot
    fig, ax = plt.subplots(figsize=(12, 5))
    x_cm = sim.x * 100
    
    for i, (snapshot, t) in enumerate(zip(snapshots[::3], times[::3])):
        ax.plot(x_cm, snapshot * 1e6, label=f't={t*1000:.1f}ms', alpha=0.7)
    
    ax.set_xlabel('Position (cm)')
    ax.set_ylabel('Displacement (μm)')
    ax.set_title('1D Shear Wave Propagation (Elastic)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('shear_wave_test.png', dpi=150)
    print(f"\nSaved: shear_wave_test.png")
    
    # Energy check
    print("\n" + "=" * 60)
    print("ENERGY CHECK")
    print("=" * 60)
    
    for eta_test in [0, 5, 10, 20]:
        sim = ShearWave1D(nx=300, dx=0.001, rho=1000, G_prime=5000, eta=eta_test)
        
        E_history = []
        for n in range(500):
            t = n * sim.dt
            if 50 < n < 150:
                sim.add_source(t, f0=100, amplitude=5e-5)
            sim.step()
            # Kinetic + potential energy approximation
            E = np.sum(sim.v**2) * sim.rho + np.sum(sim.sigma * sim.epsilon)
            E_history.append(abs(E))
        
        E0 = E_history[200] if len(E_history) > 200 else E_history[100]
        Ef = np.mean(E_history[-50:])
        
        if E0 > 0:
            print(f"η = {eta_test:2d} Pa·s: E_final/E0 = {Ef/E0:.3f}")
        else:
            print(f"η = {eta_test:2d} Pa·s: E0 = 0 (check)")
    
    print("\nExpected: η=0 stable, η>0 shows decay")


if __name__ == "__main__":
    quick_test()
