"""
2D Shear Wave Propagation in Viscoelastic Medium
=================================================

Extension of 1D FDTD to 2D with absorbing boundary conditions.

Physics:
--------
∂²u/∂t² = (G'/ρ) ∇²u + (η/ρ) ∂∇²u/∂t

Where ∇²u = ∂²u/∂x² + ∂²u/∂y² (2D Laplacian)

Boundary Conditions:
-------------------
- Mur 2nd Order: Approximates outgoing wave equation at boundaries
- PML: Perfectly Matched Layer (absorbing layer surrounding domain)

Author: Research Project — Week 2 Extension
Date: March 16, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle


class ShearWave2D:
    """
    2D shear wave simulator using FDTD with absorbing boundary conditions.
    """
    
    def __init__(self, nx=200, ny=200, dx=0.001, dt=1e-6, 
                 rho=1000, G_prime=5000, eta=5, bc_type='mur2'):
        """
        Initialize 2D shear wave simulation.
        
        Parameters:
        -----------
        nx, ny : int
            Number of spatial grid points in x and y
        dx : float
            Spatial step size (m) - same for x and y
        dt : float
            Time step size (s)
        rho : float
            Density (kg/m³)
        G_prime : float
            Storage modulus (Pa)
        eta : float
            Viscosity (Pa·s)
        bc_type : str
            'mur1' = 1st order Mur, 'mur2' = 2nd order Mur, 'pml' = PML
        """
        self.nx = nx
        self.ny = ny
        self.dx = dx
        self.dt = dt
        self.rho = rho
        self.G_prime = G_prime
        self.eta = eta
        self.bc_type = bc_type
        
        # Derived parameters
        self.c_s = np.sqrt(G_prime / rho)
        self.tau = eta / G_prime
        
        # Stability check
        self.courant = self.c_s * dt / dx
        if self.courant > 1/np.sqrt(2):  # Stricter CFL for 2D
            print(f"⚠️ Warning: CFL = {self.courant:.3f} > 1/√2 ≈ 0.707")
            print("   Consider reducing dt or increasing dx")
        
        # Initialize fields: u(x, y, t)
        self.x = np.linspace(0, (nx-1)*dx, nx)
        self.y = np.linspace(0, (ny-1)*dx, ny)
        self.X, self.Y = np.meshgrid(self.x, self.y, indexing='ij')
        
        # Current, previous, and next displacement fields
        self.u = np.zeros((nx, ny))
        self.u_prev = np.zeros((nx, ny))
        self.u_next = np.zeros((nx, ny))
        
        # For Mur 2nd order ABC, need previous boundary values
        self.u_prev_boundary = {
            'left': np.zeros(ny),
            'right': np.zeros(ny),
            'top': np.zeros(nx),
            'bottom': np.zeros(nx)
        }
        
        # PML parameters (if using PML)
        if bc_type == 'pml':
            self._setup_pml()
        
        # Time history
        self.time_history = []
        self.displacement_history = []
        
    def _setup_pml(self, thickness=20, sigma_max=None):
        """
        Setup Perfectly Matched Layer damping profile.
        
        PML surrounds the computational domain with an absorbing layer
        where waves are attenuated exponentially.
        """
        if sigma_max is None:
            sigma_max = 3 * self.c_s / (2 * thickness * self.dx)
        
        self.pml_thickness = thickness
        
        # Create damping profile (quadratic increase from interface)
        self.sigma_x = np.zeros((self.nx, self.ny))
        self.sigma_y = np.zeros((self.nx, self.ny))
        
        # Left PML
        for i in range(thickness):
            sigma_val = sigma_max * ((thickness - i) / thickness)**2
            self.sigma_x[i, :] = sigma_val
        
        # Right PML
        for i in range(self.nx - thickness, self.nx):
            sigma_val = sigma_max * ((i - (self.nx - thickness)) / thickness)**2
            self.sigma_x[i, :] = sigma_val
        
        # Bottom PML
        for j in range(thickness):
            sigma_val = sigma_max * ((thickness - j) / thickness)**2
            self.sigma_y[:, j] = sigma_val
        
        # Top PML
        for j in range(self.ny - thickness, self.ny):
            sigma_val = sigma_max * ((j - (self.ny - thickness)) / thickness)**2
            self.sigma_y[:, j] = sigma_val
        
        print(f"✓ PML setup complete: {thickness} cells, σ_max={sigma_max:.2f}")
    
    def add_source(self, t, source_type='ricker', f0=100, 
                   location=None, amplitude=1e-6):
        """
        Add source excitation at specific location.
        
        Parameters:
        -----------
        t : float
            Current time
        source_type : str
            'ricker' or 'tone_burst'
        f0 : float
            Center frequency (Hz)
        location : tuple (ix, iy)
            Grid indices for source (default: center)
        amplitude : float
            Source amplitude (m)
        """
        if location is None:
            location = (self.nx // 2, self.ny // 2)
        
        ix, iy = location
        
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
        
        self.u[ix, iy] += source_val
    
    def _laplacian(self, field):
        """
        Compute 2D Laplacian ∇²u using 5-point stencil.
        
        Interior: ∇²u ≈ (u_{i+1,j} + u_{i-1,j} + u_{i,j+1} + u_{i,j-1} - 4u_{i,j}) / dx²
        """
        lap = np.zeros_like(field)
        
        # Interior points (5-point stencil)
        lap[1:-1, 1:-1] = (
            field[2:, 1:-1] + field[:-2, 1:-1] +
            field[1:-1, 2:] + field[1:-1, :-2] -
            4 * field[1:-1, 1:-1]
        ) / self.dx**2
        
        return lap
    
    def step(self):
        """
        Advance simulation by one time step.
        
        For standard interior: FDTD update with viscoelasticity
        For boundaries: Apply absorbing boundary condition
        """
        # Compute Laplacians for current and previous time steps
        lap_u_n = self._laplacian(self.u)
        lap_u_nm1 = self._laplacian(self.u_prev)
        
        # Elastic and viscous forces
        elastic_force = self.G_prime * lap_u_n
        viscous_force = (self.eta / self.dt) * (lap_u_n - lap_u_nm1)
        
        # Acceleration
        acceleration = (elastic_force + viscous_force) / self.rho
        
        # FDTD update for interior points
        self.u_next[1:-1, 1:-1] = (
            2 * self.u[1:-1, 1:-1] - 
            self.u_prev[1:-1, 1:-1] +
            self.dt**2 * acceleration[1:-1, 1:-1]
        )
        
        # Apply boundary conditions
        if self.bc_type == 'mur1':
            self._apply_mur1()
        elif self.bc_type == 'mur2':
            self._apply_mur2()
        elif self.bc_type == 'pml':
            self._apply_pml_update()
        else:
            # Dirichlet (fixed) boundaries - simple zero
            self.u_next[0, :] = 0
            self.u_next[-1, :] = 0
            self.u_next[:, 0] = 0
            self.u_next[:, -1] = 0
        
        # Update fields
        self.u_prev, self.u, self.u_next = self.u, self.u_next, self.u_prev
    
    def _apply_mur1(self):
        """
        1st order Mur absorbing boundary condition.
        
        Based on one-way wave equation approximation.
        """
        c = self.c_s
        dx = self.dx
        dt = self.dt
        
        # Coefficient for Mur 1st order
        # u_boundary(t+1) = u_interior(t) + (c*dt - dx)/(c*dt + dx) * (u_interior(t+1) - u_boundary(t))
        coeff = (c*dt - dx) / (c*dt + dx)
        
        # Left boundary (x = 0)
        self.u_next[0, :] = self.u_prev[1, :] + coeff * (self.u[1, :] - self.u[0, :])
        
        # Right boundary (x = nx-1)
        self.u_next[-1, :] = self.u_prev[-2, :] + coeff * (self.u[-2, :] - self.u[-1, :])
        
        # Bottom boundary (y = 0)
        self.u_next[:, 0] = self.u_prev[:, 1] + coeff * (self.u[:, 1] - self.u[:, 0])
        
        # Top boundary (y = ny-1)
        self.u_next[:, -1] = self.u_prev[:, -2] + coeff * (self.u[:, -2] - self.u[:, -1])
    
    def _apply_mur2(self):
        """
        2nd order Mur absorbing boundary condition (Engquist-Majda).
        
        Uses a simplified stable formulation based on:
        u^{n+1} = 2*u^n - u^{n-1} + (ABC terms)
        
        The ABC approximates: (d/dt - c*d/dx)(d/dt + c*d/dx)u = 0
        """
        c = self.c_s
        dx = self.dx
        dt = self.dt
        
        # Mur 2nd order coefficients (standard form)
        # These come from the discretized one-way wave equation
        a = 1.0 / (c/dx + 1.0/dt)
        
        # For stability, use a blended approach:
        # Main term: extrapolate from interior using wave equation
        # Correction: add transverse derivative term
        
        # Left boundary (x = 0): wave exits to the left
        # u_0^{n+1} = u_1^n + ((c*dt - dx)/(c*dt + dx)) * (u_1^{n+1} - u_0^n)
        #             + transverse correction
        
        coeff_main = (c*dt - dx) / (c*dt + dx + 1e-10)  # Main Mur 1st-like term
        coeff_transverse = (c * dt**2) / (2 * dx)  # 2nd order correction
        
        # Interior points should already be computed in u_next
        # Left boundary update
        for j in range(1, self.ny-1):
            # Basic Mur 1st order part
            mur1_part = (self.u[1, j] + 
                        coeff_main * (self.u_next[1, j] - self.u[0, j]))
            
            # 2nd order correction: transverse Laplacian
            transverse_curvature = (self.u[0, j+1] - 2*self.u[0, j] + self.u[0, j-1])
            prev_transverse = (self.u_prev[0, j+1] - 2*self.u_prev[0, j] + self.u_prev[0, j-1])
            
            # Apply correction (damped for stability)
            correction = 0.25 * coeff_transverse * (transverse_curvature + prev_transverse) / (dt**2)
            
            self.u_next[0, j] = mur1_part + correction
        
        # Right boundary (x = nx-1)
        for j in range(1, self.ny-1):
            mur1_part = (self.u[-2, j] + 
                        coeff_main * (self.u_next[-2, j] - self.u[-1, j]))
            
            transverse_curvature = (self.u[-1, j+1] - 2*self.u[-1, j] + self.u[-1, j-1])
            prev_transverse = (self.u_prev[-1, j+1] - 2*self.u_prev[-1, j] + self.u_prev[-1, j-1])
            correction = 0.25 * coeff_transverse * (transverse_curvature + prev_transverse) / (dt**2)
            
            self.u_next[-1, j] = mur1_part + correction
        
        # Bottom boundary (y = 0)
        for i in range(1, self.nx-1):
            mur1_part = (self.u[i, 1] + 
                        coeff_main * (self.u_next[i, 1] - self.u[i, 0]))
            
            transverse_curvature = (self.u[i+1, 0] - 2*self.u[i, 0] + self.u[i-1, 0])
            prev_transverse = (self.u_prev[i+1, 0] - 2*self.u_prev[i, 0] + self.u_prev[i-1, 0])
            correction = 0.25 * coeff_transverse * (transverse_curvature + prev_transverse) / (dt**2)
            
            self.u_next[i, 0] = mur1_part + correction
        
        # Top boundary (y = ny-1)
        for i in range(1, self.nx-1):
            mur1_part = (self.u[i, -2] + 
                        coeff_main * (self.u_next[i, -2] - self.u[i, -1]))
            
            transverse_curvature = (self.u[i+1, -1] - 2*self.u[i, -1] + self.u[i-1, -1])
            prev_transverse = (self.u_prev[i+1, -1] - 2*self.u_prev[i, -1] + self.u_prev[i-1, -1])
            correction = 0.25 * coeff_transverse * (transverse_curvature + prev_transverse) / (dt**2)
            
            self.u_next[i, -1] = mur1_part + correction
        
        # Corners: simple outgoing wave approximation
        self.u_next[0, 0] = self.u[1, 1]  # Diagonal outgoing
        self.u_next[-1, 0] = self.u[-2, 1]
        self.u_next[0, -1] = self.u[1, -2]
        self.u_next[-1, -1] = self.u[-2, -2]
    
    def _apply_pml_update(self):
        """
        Apply PML damping to boundary region.
        
        This modifies the update in PML regions to include damping terms.
        """
        # For PML, we modify the acceleration with damping
        # This is a simplified implementation
        
        # Apply damping to PML regions
        damping_factor = 1 - (self.sigma_x + self.sigma_y) * self.dt
        
        # Only apply to boundary regions
        mask = (self.sigma_x > 0) | (self.sigma_y > 0)
        self.u_next[mask] *= damping_factor[mask]
    
    def record(self, t):
        """Record time history."""
        self.time_history.append(t)
        self.displacement_history.append(self.u.copy())
    
    def extract_line_profile(self, direction='x', index=None):
        """
        Extract 1D line profile from 2D field.
        
        Useful for comparing with 1D simulation.
        """
        if index is None:
            index = self.ny // 2 if direction == 'x' else self.nx // 2
        
        if direction == 'x':
            return self.u[:, index]
        else:
            return self.u[index, :]


def run_2d_simulation(bc_type='mur2', save_animation=False):
    """
    Run a 2D shear wave simulation and visualize results.
    """
    print("=" * 60)
    print(f"2D Shear Wave Simulation: {bc_type.upper()} Boundary Conditions")
    print("=" * 60)
    
    # Physical parameters (liver-typical)
    rho = 1000  # kg/m³
    G_prime = 5000  # Pa
    eta = 5  # Pa·s
    f0 = 100  # Hz
    
    # Grid parameters
    c_s = np.sqrt(G_prime / rho)
    wavelength = c_s / f0
    
    # Spatial discretization (10 points per wavelength)
    dx = wavelength / 10
    nx = ny = 150  # Grid size
    
    # Temporal discretization (CFL < 1/√2 for 2D stability)
    dt = dx / (2 * c_s)
    
    duration = 0.025  # 25 ms simulation
    n_steps = int(duration / dt)
    
    print(f"\nParameters:")
    print(f"  Shear wave speed: {c_s:.2f} m/s")
    print(f"  Wavelength: {wavelength*100:.2f} cm")
    print(f"  Grid: {nx}×{ny}, dx={dx*1000:.2f} mm")
    print(f"  Time step: {dt*1e6:.2f} μs, steps: {n_steps}")
    print(f"  CFL: {c_s*dt/dx:.3f}")
    print(f"  BC type: {bc_type}")
    
    # Create simulator
    sim = ShearWave2D(nx=nx, ny=ny, dx=dx, dt=dt,
                      rho=rho, G_prime=G_prime, eta=eta, bc_type=bc_type)
    
    # Storage for visualization
    storage_interval = 50
    u_storage = []
    t_storage = []
    
    print(f"\nRunning simulation...")
    
    for n in range(n_steps):
        t = n * dt
        
        # Add source (Ricker wavelet at center)
        sim.add_source(t, source_type='ricker', f0=f0, amplitude=5e-6)
        
        # Step forward
        sim.step()
        
        # Record
        if n % storage_interval == 0:
            u_storage.append(sim.u.copy())
            t_storage.append(t)
        
        if n % 1000 == 0:
            print(f"  Step {n}/{n_steps} ({100*n/n_steps:.1f}%)")
    
    print("✓ Simulation complete!")
    
    # Visualization
    print("\nGenerating visualizations...")
    
    # Create figure with multiple snapshots
    fig = plt.figure(figsize=(16, 10))
    
    # Select time snapshots
    snapshot_indices = [0, len(u_storage)//4, len(u_storage)//2, 
                       3*len(u_storage)//4, -1]
    
    for idx, snap_idx in enumerate(snapshot_indices):
        ax = plt.subplot(2, 3, idx + 1)
        
        u = u_storage[snap_idx]
        t = t_storage[snap_idx]
        
        # Plot wave field
        extent = [0, (nx-1)*dx*100, 0, (ny-1)*dx*100]  # cm
        vmax = np.max(np.abs(u)) * 1e6  # μm
        
        im = ax.imshow(u.T * 1e6, origin='lower', extent=extent,
                      cmap='RdBu_r', vmin=-vmax, vmax=vmax,
                      aspect='equal')
        
        # Mark source position
        ax.plot(nx//2 * dx * 100, ny//2 * dx * 100, 'k+', markersize=10)
        
        ax.set_xlabel('x (cm)')
        ax.set_ylabel('y (cm)')
        ax.set_title(f't = {t*1000:.1f} ms')
        
        plt.colorbar(im, ax=ax, label='Displacement (μm)')
    
    # Add comparison plot: center line profile vs time
    ax = plt.subplot(2, 3, 6)
    
    # Extract center line at final time
    center_line = u_storage[-1][:, ny//2] * 1e6
    x_line = np.linspace(0, (nx-1)*dx*100, nx)
    
    ax.plot(x_line, center_line, 'b-', linewidth=1, label='2D center line')
    ax.set_xlabel('x (cm)')
    ax.set_ylabel('Displacement (μm)')
    ax.set_title('Final time: Center line profile')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    plt.suptitle(f'2D Shear Wave Propagation: {bc_type.upper()} BCs, f₀={f0} Hz', 
                fontsize=14)
    plt.tight_layout()
    
    filename = f'shear_wave_2d_{bc_type}.png'
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"✓ Saved: {filename}")
    plt.show()
    
    return sim, u_storage, t_storage


def compare_boundary_conditions():
    """
    Compare different boundary condition implementations.
    """
    print("=" * 60)
    print("Boundary Condition Comparison")
    print("=" * 60)
    
    bc_types = ['dirichlet', 'mur1', 'mur2']
    results = {}
    
    for bc_type in bc_types:
        print(f"\n--- Running {bc_type.upper()} ---")
        sim, u_storage, t_storage = run_2d_simulation(bc_type=bc_type)
        results[bc_type] = {
            'sim': sim,
            'u_storage': u_storage,
            't_storage': t_storage
        }
    
    # Create comparison figure
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    for idx, bc_type in enumerate(bc_types):
        u_final = results[bc_type]['u_storage'][-1]
        sim = results[bc_type]['sim']
        
        # 2D field
        ax = axes[0, idx]
        extent = [0, (sim.nx-1)*sim.dx*100, 0, (sim.ny-1)*sim.dx*100]
        vmax = np.max([np.max(np.abs(results[b]['u_storage'][-1])) for b in bc_types]) * 1e6
        
        im = ax.imshow(u_final.T * 1e6, origin='lower', extent=extent,
                      cmap='RdBu_r', vmin=-vmax, vmax=vmax)
        ax.set_title(f'{bc_type.upper()} BCs')
        ax.set_xlabel('x (cm)')
        ax.set_ylabel('y (cm)')
        plt.colorbar(im, ax=ax)
        
        # Center line profile
        ax = axes[1, idx]
        center_line = u_final[:, sim.ny//2] * 1e6
        x_line = np.linspace(0, (sim.nx-1)*sim.dx*100, sim.nx)
        
        ax.plot(x_line, center_line, 'b-', linewidth=1)
        ax.set_xlabel('x (cm)')
        ax.set_ylabel('Displacement (μm)')
        ax.set_title('Center line profile')
        ax.grid(True, alpha=0.3)
        
        # Quantify boundary reflection
        boundary_region = center_line[-20:]  # Last 20 points
        reflection_energy = np.sum(boundary_region**2)
        ax.text(0.05, 0.95, f'Boundary energy: {reflection_energy:.2f}',
               transform=ax.transAxes, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.suptitle('Boundary Condition Comparison', fontsize=14)
    plt.tight_layout()
    plt.savefig('bc_comparison.png', dpi=150, bbox_inches='tight')
    print("\n✓ Saved: bc_comparison.png")
    plt.show()
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    for bc_type in bc_types:
        u_final = results[bc_type]['u_storage'][-1]
        center_line = u_final[:, results[bc_type]['sim'].ny//2]
        boundary_energy = np.sum(center_line[-20:]**2)
        print(f"  {bc_type.upper():12s}: Boundary reflection energy = {boundary_energy:.4f}")
    print("\nLower is better — Mur 2nd order should show least reflection.")


def generate_dispersion_curves():
    """
    Generate dispersion curves from 2D simulation.
    
    Run multiple frequencies and extract phase velocity at receivers.
    """
    print("=" * 60)
    print("Dispersion Curve Generation")
    print("=" * 60)
    
    rho = 1000
    G_prime = 5000
    eta = 10  # Higher viscosity for clearer dispersion
    
    frequencies = np.array([50, 100, 150, 200, 250, 300])
    phase_velocities = []
    
    # Physical domain
    domain_size = 0.15  # 15 cm
    dx = 0.001  # 1 mm
    nx = int(domain_size / dx)
    dt = dx / (2 * np.sqrt(G_prime / rho))  # Stable time step
    n_steps = int(0.03 / dt)  # 30 ms
    
    print(f"Grid: {nx}×{nx}, dx={dx*1000:.1f} mm, {n_steps} steps")
    print(f"Frequencies: {frequencies} Hz\n")
    
    for f0 in frequencies:
        print(f"Running f = {f0} Hz...")
        
        sim = ShearWave2D(nx=nx, ny=nx, dx=dx, dt=dt,
                         rho=rho, G_prime=G_prime, eta=eta, bc_type='mur2')
        
        # Receiver positions (distance from source)
        source_pos = (nx // 3, nx // 2)
        receiver_pos = (2 * nx // 3, nx // 2)
        distance = (receiver_pos[0] - source_pos[0]) * dx
        
        # Time series at receiver
        receiver_signal = []
        
        for n in range(n_steps):
            t = n * dt
            sim.add_source(t, source_type='tone_burst', f0=f0, 
                          location=source_pos, amplitude=1e-6)
            sim.step()
            receiver_signal.append(sim.u[receiver_pos])
        
        # Estimate phase velocity from time-of-flight
        receiver_signal = np.array(receiver_signal)
        
        # Find peak of envelope
        envelope = np.abs(receiver_signal)
        peak_idx = np.argmax(envelope)
        peak_time = peak_idx * dt
        
        # Phase velocity = distance / time
        c_phase = distance / peak_time if peak_time > 0 else np.sqrt(G_prime / rho)
        phase_velocities.append(c_phase)
        
        print(f"  Peak arrival: {peak_time*1000:.2f} ms, c_p = {c_phase:.2f} m/s")
    
    # Plot dispersion curve
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Theoretical Kelvin-Voigt dispersion
    omega = 2 * np.pi * frequencies
    c0 = np.sqrt(G_prime / rho)
    c_theory = c0 * np.sqrt(2) * ((1 + (omega * eta / G_prime)**2)**0.25) * \
               np.cos(0.5 * np.arctan(omega * eta / G_prime))
    
    ax.plot(frequencies, phase_velocities, 'bo-', linewidth=2, 
           markersize=8, label='2D Simulation (Mur2 BC)')
    ax.plot(frequencies, c_theory, 'r--', linewidth=2, 
           label='Kelvin-Voigt Theory')
    
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Phase Velocity (m/s)')
    ax.set_title('Shear Wave Dispersion in Viscoelastic Medium')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('dispersion_curve_2d.png', dpi=150)
    print("\n✓ Saved: dispersion_curve_2d.png")
    plt.show()
    
    # Print summary
    print("\n" + "=" * 60)
    print("Dispersion Results:")
    print(f"  Storage modulus G': {G_prime} Pa")
    print(f"  Viscosity η: {eta} Pa·s")
    print(f"  Elastic wave speed c₀: {c0:.2f} m/s")
    print("\n  Frequency | Phase Velocity (sim) | Phase Velocity (theory)")
    print("  " + "-" * 55)
    for f, c_sim, c_th in zip(frequencies, phase_velocities, c_theory):
        print(f"  {f:6.0f} Hz | {c_sim:18.2f} m/s | {c_th:18.2f} m/s")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("2D SHEAR WAVE SIMULATION SUITE")
    print("Boundary Conditions: Mur 1st/2nd Order, PML, Dirichlet")
    print("=" * 60 + "\n")
    
    # Run main simulation with Mur 2nd order
    print("\n[1] Running 2D simulation with Mur 2nd order ABC...")
    sim, u_storage, t_storage = run_2d_simulation(bc_type='mur2')
    
    # Compare boundary conditions
    print("\n[2] Comparing boundary condition implementations...")
    compare_boundary_conditions()
    
    # Generate dispersion curves
    print("\n[3] Generating dispersion curves from 2D simulation...")
    generate_dispersion_curves()
    
    print("\n" + "=" * 60)
    print("All simulations complete!")
    print("\nKey achievements:")
    print("  ✓ 2D FDTD with viscoelastic Kelvin-Voigt model")
    print("  ✓ Mur 1st and 2nd order absorbing boundary conditions")
    print("  ✓ PML implementation (optional)")
    print("  ✓ Dispersion curve extraction from 2D wave fields")
    print("=" * 60)
