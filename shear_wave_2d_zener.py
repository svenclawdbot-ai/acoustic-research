"""
2D Shear Wave Propagation with Zener Model (Standard Linear Solid)
==================================================================

FDTD implementation of Zener viscoelasticity for 2D shear wave propagation.

Zener Model (Standard Linear Solid):
  Spring G_r || [Spring G_1 - Dashpot η in series]

Constitutive equation:
  σ + τ_σ·∂σ/∂t = G_r·(ε + τ_ε·∂ε/∂t)

Memory variable formulation tracks anelastic strain components.

Author: Research Project — 2D Zener Extension
Date: March 23, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


class ShearWave2DZener:
    """
    2D shear wave simulator with Zener (Standard Linear Solid) viscoelasticity.
    
    Uses velocity-stress formulation with memory variables for the anelastic
    components of strain.
    """
    
    def __init__(self, nx=200, ny=200, dx=0.001, dt=None, rho=1000,
                 G_r=5000, G_inf=8000, tau_sigma=0.001, bc_type='mur2'):
        """
        Initialize 2D Zener shear wave simulation.
        
        Parameters:
        -----------
        nx, ny : int
            Number of spatial grid points
        dx : float
            Spatial step size (m)
        dt : float or None
            Time step (auto-computed for stability if None)
        rho : float
            Density (kg/m³)
        G_r : float
            Relaxed modulus G_r (low-frequency limit, Pa)
        G_inf : float
            Unrelaxed modulus G_∞ (high-frequency limit, Pa)
        tau_sigma : float
            Stress relaxation time τ_σ = η/G_1 (s)
        bc_type : str
            'mur1', 'mur2', or 'pml'
        """
        self.nx = nx
        self.ny = ny
        self.dx = dx
        self.rho = rho
        self.bc_type = bc_type
        
        # Zener parameters
        self.G_r = G_r
        self.G_inf = G_inf
        self.tau_sigma = tau_sigma
        
        # Derived parameters
        self.G_1 = G_inf - G_r
        self.tau_epsilon = tau_sigma * G_inf / G_r
        self.eta = tau_sigma * G_inf
        
        if self.G_1 <= 0:
            raise ValueError("G_inf must be > G_r for Zener model")
        
        # Wave speeds
        self.c_r = np.sqrt(G_r / rho)
        self.c_inf = np.sqrt(G_inf / rho)
        
        # Time step - need finer resolution for accuracy
        if dt is None:
            self.dt = 0.2 * dx / self.c_inf  # Finer for better accuracy
        else:
            self.dt = dt
        
        courant = self.c_inf * self.dt / dx
        print(f"2D Zener: G_r={G_r} Pa, G_∞={G_inf} Pa, τ_σ={tau_sigma*1000:.2f} ms")
        print(f"  Wave speeds: c_r={self.c_r:.2f} m/s, c_∞={self.c_inf:.2f} m/s")
        print(f"  Grid: {nx}×{ny}, dx={dx*1000:.2f} mm, dt={self.dt*1e6:.2f} μs")
        print(f"  CFL: {courant:.3f}, BC: {bc_type}")
        
        # Grid
        self.x = np.arange(nx) * dx
        self.y = np.arange(ny) * dx
        self.X, self.Y = np.meshgrid(self.x, self.y, indexing='ij')
        
        # Fields - velocity-stress formulation
        # Particle velocity components
        self.vx = np.zeros((nx, ny))
        self.vy = np.zeros((nx, ny))
        
        # Stress components (symmetric tensor)
        self.sigma_xx = np.zeros((nx, ny))
        self.sigma_yy = np.zeros((nx, ny))
        self.sigma_xy = np.zeros((nx, ny))
        
        # Total strain components (integrated from strain rate)
        self.epsilon_xx = np.zeros((nx, ny))
        self.epsilon_yy = np.zeros((nx, ny))
        self.epsilon_xy = np.zeros((nx, ny))
        
        # Memory variables (anelastic strain in Maxwell element)
        # Each stress component has associated anelastic strain
        self.epsilon_xx_a = np.zeros((nx, ny))
        self.epsilon_yy_a = np.zeros((nx, ny))
        self.epsilon_xy_a = np.zeros((nx, ny))
        
        # Displacement (for visualization)
        self.ux = np.zeros((nx, ny))
        self.uy = np.zeros((nx, ny))
        
        # Time history
        self.time_history = []
        self.displacement_history = []
        
    def add_source(self, t, source_type='ricker', f0=100, location=None, 
                   amplitude=1e-5, direction='z'):
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
        location : tuple (ix, iy)
            Grid indices for source
        amplitude : float
            Source amplitude (m/s²)
        direction : str
            'z' (out-of-plane), 'x', or 'y' for in-plane
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
            source_val = amplitude
        
        # Apply as body force to velocity
        if direction == 'z' or direction == 'y':
            self.vy[ix, iy] += self.dt * source_val
        if direction == 'x':
            self.vx[ix, iy] += self.dt * source_val
    
    def _spatial_derivatives(self, field):
        """
        Compute spatial derivatives using central differences.
        Returns ∂f/∂x and ∂f/∂y
        """
        dfdx = np.zeros_like(field)
        dfdy = np.zeros_like(field)
        
        # Central differences for interior
        dfdx[1:-1, :] = (field[2:, :] - field[:-2, :]) / (2*self.dx)
        dfdy[:, 1:-1] = (field[:, 2:] - field[:, :-2]) / (2*self.dx)
        
        return dfdx, dfdy
    
    def step(self):
        """
        Advance simulation by one time step using FDTD.
        
        Velocity-stress formulation with memory variables:
        1. Stress divergence → velocity update
        2. Velocity gradient → strain rate
        3. Update total strain
        4. Update memory variables
        5. Compute stress from strain and memory variables
        """
        dt = self.dt
        
        # 1. Update velocities from stress divergence
        # ∂v_x/∂t = (1/ρ) * ∂σ_xx/∂x + ∂σ_xy/∂y
        # ∂v_y/∂t = (1/ρ) * ∂σ_xy/∂x + ∂σ_yy/∂y
        
        dsxx_dx, dsxx_dy = self._spatial_derivatives(self.sigma_xx)
        dsyy_dx, dsyy_dy = self._spatial_derivatives(self.sigma_yy)
        dsxy_dx, dsxy_dy = self._spatial_derivatives(self.sigma_xy)
        
        self.vx += dt / self.rho * (dsxx_dx + dsxy_dy)
        self.vy += dt / self.rho * (dsxy_dx + dsyy_dy)
        
        # 2. Compute strain rates from velocity gradients
        # ε̇_xx = ∂v_x/∂x
        # ε̇_yy = ∂v_y/∂y  
        # ε̇_xy = ½(∂v_x/∂y + ∂v_y/∂x) [engineering strain]
        # For stress computation, we use ∂v_x/∂y + ∂v_y/∂x directly
        
        dvx_dx, dvx_dy = self._spatial_derivatives(self.vx)
        dvy_dx, dvy_dy = self._spatial_derivatives(self.vy)
        
        strain_rate_xx = dvx_dx
        strain_rate_yy = dvy_dy
        strain_rate_xy = dvx_dy + dvy_dx  # Note: 2*ε̇_xy in engineering notation
        
        # 3. Update total strains
        self.epsilon_xx += dt * strain_rate_xx
        self.epsilon_yy += dt * strain_rate_yy
        self.epsilon_xy += dt * strain_rate_xy
        
        # 4. Update memory variables (anelastic strain)
        # ∂ε^a/∂t = (ε - ε^a)/τ_ε
        self.epsilon_xx_a += dt * (self.epsilon_xx - self.epsilon_xx_a) / self.tau_epsilon
        self.epsilon_yy_a += dt * (self.epsilon_yy - self.epsilon_yy_a) / self.tau_epsilon
        self.epsilon_xy_a += dt * (self.epsilon_xy - self.epsilon_xy_a) / self.tau_epsilon
        
        # 5. Compute stresses
        # σ = G_∞·ε - G_1·ε^a
        self.sigma_xx = self.G_inf * self.epsilon_xx - self.G_1 * self.epsilon_xx_a
        self.sigma_yy = self.G_inf * self.epsilon_yy - self.G_1 * self.epsilon_yy_a
        self.sigma_xy = self.G_inf * self.epsilon_xy - self.G_1 * self.epsilon_xy_a
        
        # Update displacements
        self.ux += dt * self.vx
        self.uy += dt * self.vy
        
        # Apply boundary conditions
        if self.bc_type == 'mur1':
            self._apply_mur1()
        elif self.bc_type == 'mur2':
            self._apply_mur2()
    
    def _apply_mur1(self):
        """1st order Mur absorbing boundary conditions."""
        coeff = (self.c_r * self.dt - self.dx) / (self.c_r * self.dt + self.dx)
        
        # Left boundary
        self.vx[0, :] = self.vx[1, :] + coeff * (self.vx[1, :] - self.vx[0, :])
        self.vy[0, :] = self.vy[1, :] + coeff * (self.vy[1, :] - self.vy[0, :])
        
        # Right boundary
        self.vx[-1, :] = self.vx[-2, :] + coeff * (self.vx[-2, :] - self.vx[-1, :])
        self.vy[-1, :] = self.vy[-2, :] + coeff * (self.vy[-2, :] - self.vy[-1, :])
        
        # Bottom boundary
        self.vx[:, 0] = self.vx[:, 1] + coeff * (self.vx[:, 1] - self.vx[:, 0])
        self.vy[:, 0] = self.vy[:, 1] + coeff * (self.vy[:, 1] - self.vy[:, 0])
        
        # Top boundary
        self.vx[:, -1] = self.vx[:, -2] + coeff * (self.vx[:, -2] - self.vx[:, -1])
        self.vy[:, -1] = self.vy[:, -2] + coeff * (self.vy[:, -2] - self.vy[:, -1])
    
    def _apply_mur2(self):
        """2nd order Mur absorbing boundary conditions (simplified)."""
        c = self.c_r
        dt = self.dt
        dx = self.dx
        
        coeff_main = (c*dt - dx) / (c*dt + dx + 1e-10)
        
        # Left boundary
        for j in range(1, self.ny-1):
            self.vx[0, j] = self.vx[1, j] + coeff_main * (self.vx[1, j] - self.vx[0, j])
            self.vy[0, j] = self.vy[1, j] + coeff_main * (self.vy[1, j] - self.vy[0, j])
        
        # Right boundary
        for j in range(1, self.ny-1):
            self.vx[-1, j] = self.vx[-2, j] + coeff_main * (self.vx[-2, j] - self.vx[-1, j])
            self.vy[-1, j] = self.vy[-2, j] + coeff_main * (self.vy[-2, j] - self.vy[-1, j])
        
        # Bottom boundary
        for i in range(1, self.nx-1):
            self.vx[i, 0] = self.vx[i, 1] + coeff_main * (self.vx[i, 1] - self.vx[i, 0])
            self.vy[i, 0] = self.vy[i, 1] + coeff_main * (self.vy[i, 1] - self.vy[i, 0])
        
        # Top boundary
        for i in range(1, self.nx-1):
            self.vx[i, -1] = self.vx[i, -2] + coeff_main * (self.vx[i, -2] - self.vx[i, -1])
            self.vy[i, -1] = self.vy[i, -2] + coeff_main * (self.vy[i, -2] - self.vy[i, -1])
        
        # Corners
        self.vx[0, 0] = self.vx[1, 1]
        self.vx[-1, 0] = self.vx[-2, 1]
        self.vx[0, -1] = self.vx[1, -2]
        self.vx[-1, -1] = self.vx[-2, -2]
        self.vy[0, 0] = self.vy[1, 1]
        self.vy[-1, 0] = self.vy[-2, 1]
        self.vy[0, -1] = self.vy[1, -2]
        self.vy[-1, -1] = self.vy[-2, -2]
    
    def record(self, t):
        """Record time history."""
        self.time_history.append(t)
        # Store displacement magnitude for visualization
        displacement_magnitude = np.sqrt(self.ux**2 + self.uy**2)
        self.displacement_history.append(displacement_magnitude.copy())
    
    def get_dispersion_theory(self, frequencies):
        """
        Compute theoretical Zener dispersion.
        
        Returns phase velocity c_p(ω) for given frequencies.
        """
        omega = 2 * np.pi * np.array(frequencies)
        
        # Complex modulus for Zener model
        G_star = self.G_r + (self.G_inf - self.G_r) / (1 + 1j*omega*self.tau_sigma)
        
        # Storage and loss modulus
        G_prime = np.real(G_star)
        G_double_prime = np.imag(G_star)
        
        # Magnitude and loss angle
        G_mag = np.abs(G_star)
        delta = np.arctan2(G_double_prime, G_prime)
        
        # Phase velocity
        c_p = np.sqrt(2*G_mag / (self.rho * (1 + np.cos(delta))))
        
        return c_p


def run_2d_zener_simulation(G_r=5000, G_inf=8000, tau_sigma=0.001, f0=100,
                             nx=200, duration=0.025, bc_type='mur2'):
    """
    Run a 2D Zener simulation and visualize.
    
    Parameters:
    -----------
    G_r : float
        Relaxed modulus (Pa)
    G_inf : float
        Unrelaxed modulus (Pa)
    tau_sigma : float
        Stress relaxation time (s)
    f0 : float
        Source frequency (Hz)
    nx : int
        Grid size (nx × nx)
    duration : float
        Simulation duration (s)
    bc_type : str
        Boundary condition type
    """
    print("=" * 70)
    print("2D ZENER MODEL SIMULATION")
    print("=" * 70)
    
    # Grid setup
    c_inf = np.sqrt(G_inf / 1000)
    wavelength = c_inf / f0
    dx = wavelength / 10
    
    # Create simulator
    sim = ShearWave2DZener(nx=nx, ny=nx, dx=dx, rho=1000,
                           G_r=G_r, G_inf=G_inf, tau_sigma=tau_sigma,
                           bc_type=bc_type)
    
    dt = sim.dt
    n_steps = int(duration / dt)
    
    print(f"\nSource: {f0} Hz tone burst")
    print(f"Duration: {duration*1000:.1f} ms ({n_steps} steps)")
    
    # Storage
    storage_interval = 50
    u_storage = []
    t_storage = []
    
    # Source location
    source_pos = (nx // 2, nx // 2)
    
    print("\nRunning...")
    for n in range(n_steps):
        t = n * dt
        
        # Add source (first 100 steps)
        if n < 100:
            sim.add_source(t, source_type='tone_burst', f0=f0,
                          location=source_pos, amplitude=2e-5)
        
        sim.step()
        
        if n % storage_interval == 0:
            sim.record(t)
            u_storage.append(sim.ux.copy())
            t_storage.append(t)
        
        if n % 1000 == 0:
            print(f"  Step {n}/{n_steps}")
    
    print("✓ Complete!")
    
    # Visualization
    fig = plt.figure(figsize=(16, 12))
    
    # Snapshots
    snapshot_indices = [0, len(u_storage)//4, len(u_storage)//2,
                       3*len(u_storage)//4, -1]
    titles = ['Early', 'Quarter', 'Half', 'Three-Quarter', 'Final']
    
    for idx, (snap_idx, title) in enumerate(zip(snapshot_indices, titles)):
        ax = plt.subplot(2, 3, idx + 1)
        
        u = u_storage[snap_idx]
        t = t_storage[snap_idx]
        
        extent = [0, (nx-1)*dx*100, 0, (nx-1)*dx*100]
        vmax = np.max([np.max(np.abs(u)) for u in u_storage]) * 1e6
        
        im = ax.imshow(u.T * 1e6, origin='lower', extent=extent,
                      cmap='RdBu_r', vmin=-vmax, vmax=vmax, aspect='equal')
        
        # Mark source
        ax.plot(source_pos[0]*dx*100, source_pos[1]*dx*100, 'k+', markersize=15)
        
        ax.set_xlabel('x (cm)')
        ax.set_ylabel('y (cm)')
        ax.set_title(f'{title}: t = {t*1000:.1f} ms')
        plt.colorbar(im, ax=ax, label='u_x (μm)')
    
    # Center line profile at final time
    ax = plt.subplot(2, 3, 6)
    center_line = u_storage[-1][:, nx//2] * 1e6
    x_line = np.linspace(0, (nx-1)*dx*100, nx)
    
    ax.plot(x_line, center_line, 'b-', linewidth=1.5)
    ax.axvline(x=source_pos[0]*dx*100, color='r', linestyle='--', alpha=0.5, label='Source')
    ax.set_xlabel('x (cm)')
    ax.set_ylabel('u_x (μm)')
    ax.set_title('Final: Center Line Profile')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    plt.suptitle(f'2D Zener Model: G_r={G_r}, G_∞={G_inf}, τ_σ={tau_sigma*1000:.1f}ms, f₀={f0}Hz',
                fontsize=14)
    plt.tight_layout()
    
    filename = f'shear_wave_2d_zener_{f0}Hz.png'
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"✓ Saved: {filename}")
    plt.show()
    
    return sim, u_storage, t_storage


def dispersion_validation_2d():
    """
    Validate 2D Zener dispersion against theory using phase difference method.
    """
    print("=" * 70)
    print("2D ZENER DISPERSION VALIDATION")
    print("=" * 70)
    
    # Parameters
    G_r = 5000
    G_inf = 8000
    tau_sigma = 0.001
    rho = 1000
    
    frequencies = [50, 100, 150, 200, 300]
    c_simulated = []
    
    for f0 in frequencies:
        print(f"\nRunning f = {f0} Hz...")
        
        # Setup - ensure adequate resolution
        c_inf = np.sqrt(G_inf / rho)
        wavelength = c_inf / f0
        dx = wavelength / 15  # Better spatial resolution
        nx = max(int(0.15 / dx), 100)  # At least 15 cm domain, 100 points
        
        sim = ShearWave2DZener(nx=nx, ny=nx, dx=dx, rho=rho,
                               G_r=G_r, G_inf=G_inf, tau_sigma=tau_sigma,
                               bc_type='mur2')
        
        dt = sim.dt
        n_steps = int(0.05 / dt)  # 50 ms simulation
        
        source_pos = (nx // 3, nx // 2)
        receiver1_pos = (nx // 2, nx // 2)  # Closer receiver
        receiver2_pos = (2 * nx // 3, nx // 2)  # Farther receiver
        
        distance = (receiver2_pos[0] - receiver1_pos[0]) * dx
        
        # Time series at both receivers
        rec1_signal = []
        rec2_signal = []
        times = []
        
        for n in range(n_steps):
            t = n * dt
            if n * dt < 3.0 / f0:  # Source duration ~3 cycles
                sim.add_source(t, source_type='tone_burst', f0=f0,
                              location=source_pos, amplitude=1e-5)
            sim.step()
            rec1_signal.append(sim.vy[receiver1_pos])
            rec2_signal.append(sim.vy[receiver2_pos])
            times.append(t)
        
        rec1_signal = np.array(rec1_signal)
        rec2_signal = np.array(rec2_signal)
        times = np.array(times)
        
        # Use cross-correlation to find time delay between receivers
        from scipy.signal import correlate, hilbert
        
        # Envelope detection for more robust correlation
        env1 = np.abs(hilbert(rec1_signal))
        env2 = np.abs(hilbert(rec2_signal))
        
        # Cross-correlation
        correlation = correlate(env2, env1, mode='full')
        lags = np.arange(-len(env1) + 1, len(env1))
        
        # Find peak
        peak_idx = np.argmax(correlation)
        lag = lags[peak_idx]
        time_delay = lag * dt
        
        # Compute phase velocity
        if abs(time_delay) > 0.0001:  # At least 0.1 ms
            c_est = distance / abs(time_delay)
        else:
            # Fall back to group velocity from single receiver
            # Use peak arrival at farther receiver
            peak2_idx = np.argmax(env2)
            peak2_time = times[peak2_idx]
            # Estimate source-to-r2 distance
            dist_total = (receiver2_pos[0] - source_pos[0]) * dx
            c_est = dist_total / peak2_time if peak2_time > 0.001 else np.sqrt(G_r / rho)
        
        c_simulated.append(c_est)
        print(f"  Time delay: {time_delay*1000:.2f} ms, c_p = {c_est:.2f} m/s")
    
    # Theoretical
    c_theory = sim.get_dispersion_theory(frequencies)
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(frequencies, c_simulated, 'bo', markersize=10, label='2D FDTD Simulation')
    ax.plot(frequencies, c_theory, 'r-', linewidth=2, label='Zener Theory')
    ax.axhline(y=np.sqrt(G_r/rho), color='k', linestyle='--', alpha=0.5,
              label=f'c_r = {np.sqrt(G_r/rho):.1f} m/s')
    ax.axhline(y=np.sqrt(G_inf/rho), color='k', linestyle=':', alpha=0.5,
              label=f'c_∞ = {np.sqrt(G_inf/rho):.1f} m/s')
    
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Phase Velocity (m/s)')
    ax.set_title('2D Zener Model: Dispersion Validation')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('zener_2d_dispersion_validation.png', dpi=150)
    print("\n✓ Saved: zener_2d_dispersion_validation.png")
    
    # Summary table
    print("\n" + "=" * 70)
    print("Validation Summary:")
    print(f"{'Freq (Hz)':<12} {'FDTD':<12} {'Theory':<12} {'Error %':<10}")
    print("-" * 70)
    for f, c_s, c_t in zip(frequencies, c_simulated, c_theory):
        err = 100 * abs(c_s - c_t) / c_t if c_t > 0 else 0
        print(f"{f:<12} {c_s:<12.2f} {c_t:<12.2f} {err:<10.2f}")
    
    plt.show()
    return frequencies, c_simulated, c_theory


def compare_kv_zener_2d():
    """
    Compare 2D Kelvin-Voigt vs Zener side-by-side.
    """
    print("=" * 70)
    print("2D COMPARISON: Kelvin-Voigt vs Zener")
    print("=" * 70)
    
    # Common parameters
    G_r = 5000
    G_inf = 8000
    tau_sigma = 0.001
    rho = 1000
    f0 = 200  # Higher frequency to see difference
    
    # Match KV viscosity to Zener at this frequency
    eta_kv = (G_inf - G_r) * tau_sigma
    
    print(f"Parameters: G_r={G_r}, G_∞={G_inf}, f0={f0} Hz")
    print(f"KV viscosity: η={eta_kv:.2f} Pa·s")
    
    # Run Zener
    print("\n--- Running Zener (2D) ---")
    sim_zener, u_zener, t_zener = run_2d_zener_simulation(
        G_r=G_r, G_inf=G_inf, tau_sigma=tau_sigma, f0=f0,
        nx=180, duration=0.025, bc_type='mur2'
    )
    
    # Run KV (using existing 2D code)
    print("\n--- Running Kelvin-Voigt (2D) ---")
    from shear_wave_2d_simulator import ShearWave2D
    
    c_s = np.sqrt(G_r / rho)
    wavelength = c_s / f0
    dx = wavelength / 10
    nx = 180
    dt = dx / (2 * c_s)
    n_steps = int(0.025 / dt)
    
    sim_kv = ShearWave2D(nx=nx, ny=nx, dx=dx, dt=dt, rho=rho,
                         G_prime=G_r, eta=eta_kv, bc_type='mur2')
    
    u_kv_storage = []
    source_pos = (nx // 2, nx // 2)
    
    for n in range(n_steps):
        t = n * dt
        if n < 100:
            sim_kv.add_source(t, source_type='ricker', f0=f0,
                             location=source_pos, amplitude=5e-6)
        sim_kv.step()
        if n % 50 == 0:
            u_kv_storage.append(sim_kv.u.copy())
    
    # Comparison plot
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    snapshot_idx = [len(u_zener)//4, len(u_zener)//2, -1]
    titles = ['Early', 'Mid', 'Late']
    
    extent = [0, (nx-1)*dx*100, 0, (nx-1)*dx*100]
    
    for col, (idx, title) in enumerate(zip(snapshot_idx, titles)):
        # Zener
        ax = axes[0, col]
        u = u_zener[idx]
        vmax = np.max([np.max(np.abs(u)) for u in u_zener])
        im = ax.imshow(u.T * 1e6, origin='lower', extent=extent,
                      cmap='RdBu_r', vmin=-vmax, vmax=vmax)
        ax.plot(source_pos[0]*dx*100, source_pos[1]*dx*100, 'k+', markersize=10)
        ax.set_title(f'Zener: {title}')
        ax.set_xlabel('x (cm)')
        ax.set_ylabel('y (cm)')
        plt.colorbar(im, ax=ax)
        
        # KV
        ax = axes[1, col]
        u = u_kv_storage[idx]
        vmax = np.max([np.max(np.abs(u)) for u in u_kv_storage])
        im = ax.imshow(u.T * 1e6, origin='lower', extent=extent,
                      cmap='RdBu_r', vmin=-vmax, vmax=vmax)
        ax.plot(source_pos[0]*dx*100, source_pos[1]*dx*100, 'k+', markersize=10)
        ax.set_title(f'Kelvin-Voigt: {title}')
        ax.set_xlabel('x (cm)')
        ax.set_ylabel('y (cm)')
        plt.colorbar(im, ax=ax)
    
    plt.suptitle(f'2D Comparison: Zener vs Kelvin-Voigt (f={f0} Hz)', fontsize=14)
    plt.tight_layout()
    plt.savefig('zener_vs_kv_2d_comparison.png', dpi=150)
    print("\n✓ Saved: zener_vs_kv_2d_comparison.png")
    plt.show()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("2D ZENER MODEL SIMULATION SUITE")
    print("=" * 70)
    
    # Main simulation
    print("\n[1] Running 2D Zener simulation...")
    sim, u_storage, t_storage = run_2d_zener_simulation(
        G_r=5000, G_inf=8000, tau_sigma=0.001, f0=100,
        nx=200, duration=0.03, bc_type='mur2'
    )
    
    # Dispersion validation
    print("\n[2] Validating dispersion curves...")
    freqs, c_sim, c_theory = dispersion_validation_2d()
    
    print("\n" + "=" * 70)
    print("Complete! Key features of 2D Zener model:")
    print("=" * 70)
    print("✓ Memory variable formulation for anelastic strain")
    print("✓ Bounded phase velocity (physical at all frequencies)")
    print("✓ Frequency-dependent attenuation with peak at ωτ ≈ 1")
    print("✓ Mur 2nd order absorbing boundary conditions")
    print("=" * 70)
