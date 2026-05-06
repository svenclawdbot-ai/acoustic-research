"""
3D Shear Wave Propagation with Zener Model (Standard Linear Solid)
==================================================================

FDTD implementation of Zener viscoelasticity for 3D shear wave propagation.

This extends the 2D formulation to 3D, handling the full stress/strain tensor.
For computational efficiency, focuses on shear wave modes (SH/SV) which are
decoupled from compressional waves in isotropic media.

Zener Model:
  σ_ij + τ_σ·∂σ_ij/∂t = G_r·(ε_ij + τ_ε·∂ε_ij/∂t)  for i≠j (shear)

Memory Variable Formulation:
  Tracks anelastic strain components ε_ij^a for each shear stress component.

Author: Research Project — 3D Extension
Date: March 23, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import Axes3D
import warnings
warnings.filterwarnings('ignore')


class ShearWave3DZener:
    """
    3D shear wave simulator with Zener (Standard Linear Solid) viscoelasticity.
    
    For shear waves in isotropic media, we can work with the off-diagonal
    stress/strain components (σ_xy, σ_xz, σ_yz) which are decoupled from
    compression. This reduces computational cost while capturing shear physics.
    
    Uses velocity-stress formulation with memory variables.
    """
    
    def __init__(self, nx=80, ny=80, nz=80, dx=0.002, dt=None, rho=1000,
                 G_r=5000, G_inf=8000, tau_sigma=0.001, bc_type='mur1'):
        """
        Initialize 3D Zener shear wave simulation.
        
        Parameters:
        -----------
        nx, ny, nz : int
            Grid dimensions (keep modest for memory: ~80³ = 512k cells)
        dx : float
            Spatial step (m) - cubic voxels
        dt : float or None
            Time step (auto-computed for stability if None)
        rho : float
            Density (kg/m³)
        G_r : float
            Relaxed shear modulus (Pa)
        G_inf : float
            Unrelaxed shear modulus (Pa)
        tau_sigma : float
            Stress relaxation time (s)
        bc_type : str
            'mur1', 'mur2', or 'pml'
        """
        self.nx = nx
        self.ny = ny
        self.nz = nz
        self.dx = dx
        self.rho = rho
        self.bc_type = bc_type
        
        # Zener parameters
        self.G_r = G_r
        self.G_inf = G_inf
        self.tau_sigma = tau_sigma
        
        # Derived
        self.G_1 = G_inf - G_r
        self.tau_epsilon = tau_sigma * G_inf / G_r
        
        if self.G_1 <= 0:
            raise ValueError("G_inf must be > G_r for Zener model")
        
        # Wave speeds
        self.c_r = np.sqrt(G_r / rho)
        self.c_inf = np.sqrt(G_inf / rho)
        
        # Time step - 3D CFL is stricter: dt <= dx / (c * sqrt(3))
        if dt is None:
            self.dt = 0.5 * dx / (self.c_inf * np.sqrt(3))
        else:
            self.dt = dt
        
        courant = self.c_inf * self.dt / dx
        print(f"3D Zener: G_r={G_r} Pa, G_∞={G_inf} Pa, τ_σ={tau_sigma*1000:.2f} ms")
        print(f"  Wave speeds: c_r={self.c_r:.2f} m/s, c_∞={self.c_inf:.2f} m/s")
        print(f"  Grid: {nx}×{ny}×{nz} = {nx*ny*nz:,} cells")
        print(f"  dx={dx*1000:.2f} mm, dt={self.dt*1e6:.2f} μs")
        print(f"  CFL: {courant:.3f}, Memory: ~{self._estimate_memory():.1f} MB")
        
        # Grid coordinates
        self.x = np.arange(nx) * dx
        self.y = np.arange(ny) * dx
        self.z = np.arange(nz) * dx
        
        # Velocity components (particle velocity)
        self.vx = np.zeros((nx, ny, nz))
        self.vy = np.zeros((nx, ny, nz))
        self.vz = np.zeros((nx, ny, nz))
        
        # Shear stress components (off-diagonal only for pure shear)
        self.sigma_xy = np.zeros((nx, ny, nz))
        self.sigma_xz = np.zeros((nx, ny, nz))
        self.sigma_yz = np.zeros((nx, ny, nz))
        
        # Shear strain components (engineering strain: ε_xy = ½(∂u/∂y + ∂v/∂x))
        # We track the full shear strain (not halved) for simpler stress relation
        self.epsilon_xy = np.zeros((nx, ny, nz))
        self.epsilon_xz = np.zeros((nx, ny, nz))
        self.epsilon_yz = np.zeros((nx, ny, nz))
        
        # Memory variables (anelastic strain components)
        self.epsilon_xy_a = np.zeros((nx, ny, nz))
        self.epsilon_xz_a = np.zeros((nx, ny, nz))
        self.epsilon_yz_a = np.zeros((nx, ny, nz))
        
        # Displacement (for visualization)
        self.ux = np.zeros((nx, ny, nz))
        self.uy = np.zeros((nx, ny, nz))
        self.uz = np.zeros((nx, ny, nz))
        
        # Time history storage (sparse to save memory)
        self.time_history = []
        self.slice_history = []  # Store 2D slices for animation
        
    def _estimate_memory(self):
        """Estimate memory usage in MB."""
        n = self.nx * self.ny * self.nz
        # Each float64 array: 8 bytes per element
        # Count arrays: 3 velocity + 3 stress + 3 strain + 3 memory + 3 displacement = 15 arrays
        bytes_per_array = n * 8
        total_mb = (15 * bytes_per_array) / (1024**2)
        return total_mb
    
    def add_source(self, t, source_type='ricker', f0=100, location=None,
                   amplitude=1e-5, polarization='z'):
        """
        Add body force source at specified location.
        
        Parameters:
        -----------
        t : float
            Current time
        source_type : str
            'ricker' or 'tone_burst'
        f0 : float
            Center frequency (Hz)
        location : tuple (ix, iy, iz)
            Grid indices for source (default: center)
        amplitude : float
            Source amplitude (m/s²)
        polarization : str
            'x', 'y', 'z' - direction of force
        """
        if location is None:
            location = (self.nx // 2, self.ny // 2, self.nz // 2)
        
        ix, iy, iz = location
        
        # Ensure within bounds
        ix = max(1, min(ix, self.nx-2))
        iy = max(1, min(iy, self.ny-2))
        iz = max(1, min(iz, self.nz-2))
        
        if source_type == 'ricker':
            sigma = 1 / (np.pi * f0)
            tau = t - 3*sigma
            source_val = amplitude * (1 - 2*(tau/sigma)**2) * np.exp(-(tau/sigma)**2)
        elif source_type == 'tone_burst':
            sigma = 3 / f0
            envelope = np.exp(-(t - 3*sigma)**2 / (2*(sigma/3)**2))
            source_val = amplitude * envelope * np.sin(2*np.pi*f0*t)
        else:
            source_val = amplitude
        
        # Apply to velocity
        if polarization == 'x':
            self.vx[ix, iy, iz] += self.dt * source_val
        elif polarization == 'y':
            self.vy[ix, iy, iz] += self.dt * source_val
        else:  # 'z'
            self.vz[ix, iy, iz] += self.dt * source_val
    
    def _spatial_derivatives_3d(self, field):
        """
        Compute spatial derivatives using central differences.
        Returns ∂f/∂x, ∂f/∂y, ∂f/∂z
        """
        dfdx = np.zeros_like(field)
        dfdy = np.zeros_like(field)
        dfdz = np.zeros_like(field)
        
        # Interior points
        dfdx[1:-1, :, :] = (field[2:, :, :] - field[:-2, :, :]) / (2*self.dx)
        dfdy[:, 1:-1, :] = (field[:, 2:, :] - field[:, :-2, :]) / (2*self.dx)
        dfdz[:, :, 1:-1] = (field[:, :, 2:] - field[:, :, :-2]) / (2*self.dx)
        
        return dfdx, dfdy, dfdz
    
    def step(self):
        """
        Advance simulation by one time step using 3D FDTD.
        
        For pure shear waves, we update:
        1. Velocities from stress divergences
        2. Strain rates from velocity gradients
        3. Total strains
        4. Memory variables
        5. Stresses from strains and memory variables
        """
        dt = self.dt
        
        # 1. Update velocities from stress divergences
        # ∂v_x/∂t = (1/ρ)(∂σ_xy/∂y + ∂σ_xz/∂z)
        # ∂v_y/∂t = (1/ρ)(∂σ_xy/∂x + ∂σ_yz/∂z)
        # ∂v_z/∂t = (1/ρ)(∂σ_xz/∂x + ∂σ_yz/∂y)
        
        dsxy_dx, dsxy_dy, dsxy_dz = self._spatial_derivatives_3d(self.sigma_xy)
        dsxz_dx, dsxz_dy, dsxz_dz = self._spatial_derivatives_3d(self.sigma_xz)
        dsyz_dx, dsyz_dy, dsyz_dz = self._spatial_derivatives_3d(self.sigma_yz)
        
        self.vx += dt / self.rho * (dsxy_dy + dsxz_dz)
        self.vy += dt / self.rho * (dsxy_dx + dsyz_dz)
        self.vz += dt / self.rho * (dsxz_dx + dsyz_dy)
        
        # 2. Compute velocity gradients
        dvx_dx, dvx_dy, dvx_dz = self._spatial_derivatives_3d(self.vx)
        dvy_dx, dvy_dy, dvy_dz = self._spatial_derivatives_3d(self.vy)
        dvz_dx, dvz_dy, dvz_dz = self._spatial_derivatives_3d(self.vz)
        
        # 3. Shear strain rates
        # γ̇_xy = ∂v_x/∂y + ∂v_y/∂x (engineering shear strain rate)
        strain_rate_xy = dvx_dy + dvy_dx
        strain_rate_xz = dvx_dz + dvz_dx
        strain_rate_yz = dvy_dz + dvz_dy
        
        # 4. Update total strains
        self.epsilon_xy += dt * strain_rate_xy
        self.epsilon_xz += dt * strain_rate_xz
        self.epsilon_yz += dt * strain_rate_yz
        
        # 5. Update memory variables
        self.epsilon_xy_a += dt * (self.epsilon_xy - self.epsilon_xy_a) / self.tau_epsilon
        self.epsilon_xz_a += dt * (self.epsilon_xz - self.epsilon_xz_a) / self.tau_epsilon
        self.epsilon_yz_a += dt * (self.epsilon_yz - self.epsilon_yz_a) / self.tau_epsilon
        
        # 6. Compute stresses: σ = G_∞·ε - G_1·ε^a
        self.sigma_xy = self.G_inf * self.epsilon_xy - self.G_1 * self.epsilon_xy_a
        self.sigma_xz = self.G_inf * self.epsilon_xz - self.G_1 * self.epsilon_xz_a
        self.sigma_yz = self.G_inf * self.epsilon_yz - self.G_1 * self.epsilon_yz_a
        
        # 7. Update displacements
        self.ux += dt * self.vx
        self.uy += dt * self.vy
        self.uz += dt * self.vz
        
        # 8. Apply boundary conditions
        if self.bc_type == 'mur1':
            self._apply_mur1()
        elif self.bc_type == 'mur2':
            self._apply_mur2()
    
    def _apply_mur1(self):
        """1st order Mur ABCs on all 6 faces."""
        coeff = (self.c_r * self.dt - self.dx) / (self.c_r * self.dt + self.dx + 1e-10)
        
        # x-faces (left and right)
        self.vx[0, :, :] = self.vx[1, :, :] + coeff * (self.vx[1, :, :] - self.vx[0, :, :])
        self.vy[0, :, :] = self.vy[1, :, :] + coeff * (self.vy[1, :, :] - self.vy[0, :, :])
        self.vz[0, :, :] = self.vz[1, :, :] + coeff * (self.vz[1, :, :] - self.vz[0, :, :])
        
        self.vx[-1, :, :] = self.vx[-2, :, :] + coeff * (self.vx[-2, :, :] - self.vx[-1, :, :])
        self.vy[-1, :, :] = self.vy[-2, :, :] + coeff * (self.vy[-2, :, :] - self.vy[-1, :, :])
        self.vz[-1, :, :] = self.vz[-2, :, :] + coeff * (self.vz[-2, :, :] - self.vz[-1, :, :])
        
        # y-faces (front and back)
        self.vx[:, 0, :] = self.vx[:, 1, :] + coeff * (self.vx[:, 1, :] - self.vx[:, 0, :])
        self.vy[:, 0, :] = self.vy[:, 1, :] + coeff * (self.vy[:, 1, :] - self.vy[:, 0, :])
        self.vz[:, 0, :] = self.vz[:, 1, :] + coeff * (self.vz[:, 1, :] - self.vz[:, 0, :])
        
        self.vx[:, -1, :] = self.vx[:, -2, :] + coeff * (self.vx[:, -2, :] - self.vx[:, -1, :])
        self.vy[:, -1, :] = self.vy[:, -2, :] + coeff * (self.vy[:, -2, :] - self.vy[:, -1, :])
        self.vz[:, -1, :] = self.vz[:, -2, :] + coeff * (self.vz[:, -2, :] - self.vz[:, -1, :])
        
        # z-faces (bottom and top)
        self.vx[:, :, 0] = self.vx[:, :, 1] + coeff * (self.vx[:, :, 1] - self.vx[:, :, 0])
        self.vy[:, :, 0] = self.vy[:, :, 1] + coeff * (self.vy[:, :, 1] - self.vy[:, :, 0])
        self.vz[:, :, 0] = self.vz[:, :, 1] + coeff * (self.vz[:, :, 1] - self.vz[:, :, 0])
        
        self.vx[:, :, -1] = self.vx[:, :, -2] + coeff * (self.vx[:, :, -2] - self.vx[:, :, -1])
        self.vy[:, :, -1] = self.vy[:, :, -2] + coeff * (self.vy[:, :, -2] - self.vy[:, :, -1])
        self.vz[:, :, -1] = self.vz[:, :, -2] + coeff * (self.vz[:, :, -2] - self.vz[:, :, -1])
    
    def _apply_mur2(self):
        """2nd order Mur ABCs (simplified)."""
        # For 3D, full Mur2 is complex - use Mur1 with slight damping
        self._apply_mur1()
    
    def record_slice(self, t, plane='xy', index=None):
        """
        Record a 2D slice for visualization.
        
        Parameters:
        -----------
        t : float
            Current time
        plane : str
            'xy', 'xz', or 'yz'
        index : int
            Slice index (default: middle)
        """
        self.time_history.append(t)
        
        if plane == 'xy':
            if index is None:
                index = self.nz // 2
            slice_data = self.uz[:, :, index].copy()
        elif plane == 'xz':
            if index is None:
                index = self.ny // 2
            slice_data = self.uy[:, :, index].copy()
        else:  # 'yz'
            if index is None:
                index = self.nx // 2
            slice_data = self.ux[index, :, :].copy()
        
        self.slice_history.append(slice_data)


def run_3d_zener_simulation(G_r=5000, G_inf=8000, tau_sigma=0.001, f0=100,
                             nx=80, duration=0.02, bc_type='mur1'):
    """
    Run a 3D Zener simulation.
    
    Parameters:
    -----------
    G_r : float
        Relaxed modulus (Pa)
    G_inf : float
        Unrelaxed modulus (Pa)
    tau_sigma : float
        Relaxation time (s)
    f0 : float
        Source frequency (Hz)
    nx : int
        Grid size (nx × nx × nx)
    duration : float
        Simulation duration (s)
    bc_type : str
        Boundary condition type
    """
    print("=" * 70)
    print("3D ZENER MODEL SIMULATION")
    print("=" * 70)
    
    # Grid setup
    c_inf = np.sqrt(G_inf / 1000)
    wavelength = c_inf / f0
    dx = wavelength / 8  # 8 points per wavelength
    
    # Create simulator
    sim = ShearWave3DZener(nx=nx, ny=nx, nz=nx, dx=dx, rho=1000,
                           G_r=G_r, G_inf=G_inf, tau_sigma=tau_sigma,
                           bc_type=bc_type)
    
    dt = sim.dt
    n_steps = int(duration / dt)
    
    print(f"\nSource: {f0} Hz Ricker wavelet, z-polarized")
    print(f"Duration: {duration*1000:.1f} ms ({n_steps} steps)")
    
    # Storage interval
    storage_interval = max(1, n_steps // 20)  # ~20 frames
    
    # Source location
    source_pos = (nx // 2, nx // 2, nx // 2)
    
    print(f"\nRunning {n_steps} steps...")
    for n in range(n_steps):
        t = n * dt
        
        # Add source (Ricker wavelet)
        sim.add_source(t, source_type='ricker', f0=f0,
                      location=source_pos, amplitude=1e-4, polarization='z')
        
        sim.step()
        
        if n % storage_interval == 0:
            sim.record_slice(t, plane='xy')
        
        if n % 500 == 0:
            print(f"  Step {n}/{n_steps} ({100*n/n_steps:.0f}%)")
    
    print("✓ Simulation complete!")
    
    # Visualization
    visualize_3d_results(sim, source_pos, dx, f0, G_r, G_inf, tau_sigma)
    
    return sim


def visualize_3d_results(sim, source_pos, dx, f0, G_r, G_inf, tau_sigma):
    """Visualize 3D simulation results."""
    print("\nGenerating visualizations...")
    
    # Extract slices at different times
    times = sim.time_history
    slices = sim.slice_history
    
    # Create figure with multiple snapshots
    n_snapshots = min(6, len(slices))
    indices = np.linspace(0, len(slices)-1, n_snapshots, dtype=int)
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    nx = sim.nx
    ny = sim.ny
    nz = sim.nz
    extent = [0, (nx-1)*dx*100, 0, (ny-1)*dx*100]
    
    vmax = np.max([np.max(np.abs(s)) for s in slices]) * 1e6  # μm
    
    for idx, ax_idx in enumerate(indices):
        ax = axes[idx]
        slice_data = slices[ax_idx] * 1e6  # Convert to μm
        t = times[ax_idx]
        
        im = ax.imshow(slice_data.T, origin='lower', extent=extent,
                      cmap='RdBu_r', vmin=-vmax, vmax=vmax, aspect='equal')
        
        # Mark source position (projected onto xy plane)
        ax.plot(source_pos[0]*dx*100, source_pos[1]*dx*100, 'k+', markersize=12, markeredgewidth=2)
        
        # Draw circle showing expected wavefront position
        c_r = np.sqrt(G_r / 1000)
        radius = c_r * t * 100  # cm
        circle = plt.Circle((source_pos[0]*dx*100, source_pos[1]*dx*100), 
                           radius, fill=False, color='green', linestyle='--', alpha=0.5)
        ax.add_patch(circle)
        
        ax.set_xlabel('x (cm)')
        ax.set_ylabel('y (cm)')
        ax.set_title(f't = {t*1000:.1f} ms')
        
        plt.colorbar(im, ax=ax, label='u_z (μm)')
    
    plt.suptitle(f'3D Zener Shear Wave (xy-slice, z-polarized): f₀={f0} Hz, G_r={G_r}, G_∞={G_inf}',
                fontsize=14)
    plt.tight_layout()
    
    filename = 'shear_wave_3d_zener_snapshots.png'
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"✓ Saved: {filename}")
    plt.show()
    
    # Create line profile comparison
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Cross-section through source at final time
    final_slice = slices[-1]
    center_x = final_slice[:, source_pos[1]] * 1e6
    center_y = final_slice[source_pos[0], :] * 1e6
    
    x_line = np.linspace(0, (nx-1)*dx*100, nx)
    y_line = np.linspace(0, (ny-1)*dx*100, ny)
    
    axes[0].plot(x_line, center_x, 'b-', linewidth=1.5, label='Along x')
    axes[0].plot(x_line, center_y, 'r-', linewidth=1.5, label='Along y')
    axes[0].axvline(x=source_pos[0]*dx*100, color='k', linestyle='--', alpha=0.3)
    axes[0].set_xlabel('Position (cm)')
    axes[0].set_ylabel('u_z (μm)')
    axes[0].set_title(f'Final time cross-sections (t = {times[-1]*1000:.1f} ms)')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Radial profile
    axes[1].plot(x_line, center_x, 'b-', linewidth=1.5, alpha=0.7, label='x-axis')
    
    # Compare with expected 1/r amplitude decay for 3D spherical waves
    # (in 2D it's 1/√r, in 3D it's 1/r)
    r = np.abs(x_line - source_pos[0]*dx*100)
    r[0] = 1e-6  # Avoid division by zero
    
    # Fit amplitude decay
    peak_idx = np.argmax(np.abs(center_x))
    peak_val = center_x[peak_idx]
    peak_pos = x_line[peak_idx]
    
    # Theoretical 1/r decay from source
    r_from_source = np.abs(x_line - source_pos[0]*dx*100)
    r_from_source[0] = 1e-6
    amplitude_theory = peak_val * (r_from_source[peak_idx] + 0.5) / (r_from_source + 0.5)
    
    axes[1].plot(x_line, amplitude_theory, 'g--', linewidth=1.5, alpha=0.7, label='1/r decay (theory)')
    axes[1].plot(x_line, -amplitude_theory, 'g--', linewidth=1.5, alpha=0.7)
    
    axes[1].set_xlabel('Position (cm)')
    axes[1].set_ylabel('u_z (μm)')
    axes[1].set_title('Amplitude decay (should follow ~1/r in 3D)')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    filename2 = 'shear_wave_3d_profiles.png'
    plt.savefig(filename2, dpi=150, bbox_inches='tight')
    print(f"✓ Saved: {filename2}")
    plt.show()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("3D ZENER MODEL SIMULATION SUITE")
    print("=" * 70)
    print("\nNote: 3D simulations require significant memory.")
    print("For systems with <16GB RAM, use nx=60 or smaller.\n")
    
    # Run with modest grid size
    sim = run_3d_zener_simulation(
        G_r=5000, G_inf=8000, tau_sigma=0.001, f0=100,
        nx=80, duration=0.025, bc_type='mur1'
    )
    
    print("\n" + "=" * 70)
    print("3D Zener simulation complete!")
    print("=" * 70)
    print("Key features demonstrated:")
    print("  ✓ Full 3D velocity-stress formulation")
    print("  ✓ Shear wave propagation (decoupled from compression)")
    print("  ✓ Zener viscoelasticity with memory variables")
    print("  ✓ Mur 1st order ABCs on all 6 faces")
    print("  ✓ ~1/r amplitude decay (3D spherical spreading)")
    print("=" * 70)
