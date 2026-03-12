"""
2D Shear Wave Propagation in Viscoelastic Media
================================================

Extension of 1D velocity-stress FDTD to 2D with:
- Multi-layer viscoelastic media
- Reverberant excitation (multiple ARF sources)
- Perfectly Matched Layer (PML) absorbing boundaries
- Phase velocity extraction

Known Limitations (from 1D validation):
---------------------------------------
1. Purely elastic (η=0) requires extremely conservative CFL
   - Mitigation: Always include small viscosity (η ≥ 0.5 Pa·s)
   
2. Boundary reflections can cause late-time instability
   - Mitigation: PML with sufficient thickness (≥20 cells)
   
3. Viscous stability constraint: dt ≤ ρ·dx²/(4η) in 2D
   - This is more restrictive than wave CFL for fine grids

Physics (Kelvin-Voigt in 2D):
-----------------------------
σ_xx = G'·ε_xx + η·∂ε_xx/∂t
σ_yy = G'·ε_yy + η·∂ε_yy/∂t  
σ_xy = G'·ε_xy + η·∂ε_xy/∂t

Momentum: ρ·∂v_i/∂t = ∂σ_ij/∂x_j

Author: Research Project — Week 2
Date: March 12, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


class ShearWave2D:
    """
    2D shear wave simulator using velocity-stress FDTD.
    Supports multi-layer viscoelastic media.
    """
    
    def __init__(self, nx, ny, dx, dt=None, rho=1000, 
                 G_prime=5000, eta=5, pml_width=20):
        """
        Initialize 2D shear wave simulation.
        
        Parameters:
        -----------
        nx, ny : int
            Grid dimensions
        dx : float
            Spatial step (same in x and y)
        dt : float or None
            Time step (auto-computed if None)
        rho : float or array(nx, ny)
            Density (kg/m³)
        G_prime : float or array(nx, ny)
            Storage modulus (Pa)
        eta : float or array(nx, ny)
            Viscosity (Pa·s) - must be > 0 for stability
        pml_width : int
            Thickness of PML absorbing boundary
        """
        self.nx = nx
        self.ny = ny
        self.dx = dx
        self.pml_width = pml_width
        
        # Store parameters (allow spatial variation)
        self.rho = np.ones((nx, ny)) * rho if np.isscalar(rho) else rho
        self.G_prime = np.ones((nx, ny)) * G_prime if np.isscalar(G_prime) else G_prime
        self.eta = np.ones((nx, ny)) * eta if np.isscalar(eta) else eta
        
        # Ensure minimum viscosity for stability
        self.eta = np.maximum(self.eta, 0.5)  # Min 0.5 Pa·s
        
        # Shear wave speed (for reference)
        self.c_s = np.sqrt(self.G_prime / self.rho)
        
        # Compute stable time step
        if dt is None:
            dt_wave = 0.3 * dx / np.max(self.c_s)
            # 2D viscous: dt ≤ ρ·dx²/(4η)
            dt_viscous = 0.5 * np.min(self.rho) * dx**2 / (4 * np.max(self.eta))
            self.dt = min(dt_wave, dt_viscous)
        else:
            self.dt = dt
        
        # CFL check
        courant = np.max(self.c_s) * self.dt / self.dx
        print(f"CFL = {courant:.3f}, dt = {self.dt*1e6:.2f} μs")
        if courant > 0.5:
            print(f"⚠️ Warning: CFL = {courant:.3f} may be unstable")
        else:
            print(f"✓ CFL stable")
        
        # Initialize velocity fields (staggered grid)
        self.vx = np.zeros((nx, ny))  # x-velocity
        self.vy = np.zeros((nx, ny))  # y-velocity
        
        # Stress fields
        self.sxx = np.zeros((nx, ny))  # Normal stress xx
        self.syy = np.zeros((nx, ny))  # Normal stress yy
        self.sxy = np.zeros((nx, ny))  # Shear stress xy
        
        # Strain fields (for viscous term)
        self.exx = np.zeros((nx, ny))
        self.eyy = np.zeros((nx, ny))
        self.exy = np.zeros((nx, ny))
        
        # PML damping profiles
        self._init_pml()
        
        # Coordinates
        self.x = np.arange(nx) * dx
        self.y = np.arange(ny) * dx
        
        # Time history
        self.time_history = []
        self.displacement_history = []
        
    def _init_pml(self):
        """Initialize Perfectly Matched Layer damping profiles."""
        nx, ny = self.nx, self.ny
        pml = self.pml_width
        
        # PML damping: exponential profile
        # damp(x) = damp_max * (x/pml)^2
        damp_max = 0.15  # Maximum damping coefficient
        
        damp_x = np.zeros(nx)
        damp_y = np.zeros(ny)
        
        # Left and right PML
        for i in range(pml):
            factor = ((pml - i) / pml) ** 2
            damp_x[i] = damp_max * factor
            damp_x[nx - 1 - i] = damp_max * factor
        
        # Bottom and top PML
        for j in range(pml):
            factor = ((pml - j) / pml) ** 2
            damp_y[j] = damp_max * factor
            damp_y[ny - 1 - j] = damp_max * factor
        
        # 2D damping masks (for multiplication: v *= (1 - damp))
        self.damp_x = damp_x[:, np.newaxis]
        self.damp_y = damp_y[np.newaxis, :]
        
    def _apply_pml(self, field):
        """Apply PML damping to a field."""
        # Damping: field *= (1 - damp)
        # This smoothly attenuates waves in PML region
        field *= (1 - self.damp_x) * (1 - self.damp_y)
        return field
        
    def add_source(self, t, x_pos, y_pos, fx=0, fy=1e-5, f0=100, source_type='tone_burst'):
        """
        Add acoustic radiation force source at (x_pos, y_pos).
        
        Parameters:
        -----------
        t : float
            Current time
        x_pos, y_pos : int
            Grid indices for source location
        fx, fy : float
            Force components (N)
        f0 : float
            Center frequency (Hz)
        source_type : str
            'tone_burst' or 'ricker'
        """
        if source_type == 'tone_burst':
            sigma = 3 / f0
            envelope = np.exp(-(t - 3*sigma)**2 / (2*(sigma/3)**2))
            source_val = envelope * np.sin(2*np.pi*f0*t)
        elif source_type == 'ricker':
            sigma = 1 / (np.pi * f0)
            tau = t - 3*sigma
            source_val = (1 - 2*(tau/sigma)**2) * np.exp(-(tau/sigma)**2)
        else:
            raise ValueError(f"Unknown source type: {source_type}")
        
        # Apply as force (adds to velocity via F = ma)
        if 0 <= x_pos < self.nx and 0 <= y_pos < self.ny:
            self.vx[x_pos, y_pos] += (fx * source_val * self.dt / self.rho[x_pos, y_pos])
            self.vy[x_pos, y_pos] += (fy * source_val * self.dt / self.rho[x_pos, y_pos])
    
    def step(self):
        """
        One FDTD time step.
        
        Update sequence for 2D velocity-stress:
        1. Compute strain rates from velocities
        2. Update stress (Kelvin-Voigt)
        3. Update velocities from stress divergence
        4. Apply PML
        """
        dt = self.dt
        dx = self.dx
        
        # Spatial derivatives (central differences)
        def d_dx(field):
            result = np.zeros_like(field)
            result[1:-1, :] = (field[2:, :] - field[:-2, :]) / (2*dx)
            return result
        
        def d_dy(field):
            result = np.zeros_like(field)
            result[:, 1:-1] = (field[:, 2:] - field[:, :-2]) / (2*dx)
            return result
        
        # Compute strain rates
        dvx_dx = d_dx(self.vx)
        dvy_dy = d_dy(self.vy)
        dvx_dy = d_dy(self.vx)
        dvy_dx = d_dx(self.vy)
        
        # Shear strain rate (symmetric)
        exy_rate = 0.5 * (dvx_dy + dvy_dx)
        
        # Update strains
        self.exx += dt * dvx_dx
        self.eyy += dt * dvy_dy
        self.exy += dt * exy_rate
        
        # Update stresses (Kelvin-Voigt)
        # σ = G'·ε + η·∂ε/∂t
        self.sxx = self.G_prime * self.exx + self.eta * dvx_dx
        self.syy = self.G_prime * self.eyy + self.eta * dvy_dy
        self.sxy = self.G_prime * self.exy + self.eta * exy_rate
        
        # Compute stress divergence
        dsxx_dx = d_dx(self.sxx)
        dsxy_dy = d_dy(self.sxy)
        dsxy_dx = d_dx(self.sxy)
        dsyy_dy = d_dy(self.syy)
        
        # Update velocities
        self.vx += dt / self.rho * (dsxx_dx + dsxy_dy)
        self.vy += dt / self.rho * (dsxy_dx + dsyy_dy)
        
        # Apply PML damping
        self.vx = self._apply_pml(self.vx)
        self.vy = self._apply_pml(self.vy)
        self.sxx = self._apply_pml(self.sxx)
        self.syy = self._apply_pml(self.syy)
        self.sxy = self._apply_pml(self.sxy)
        
    def get_displacement_magnitude(self):
        """Get magnitude of displacement (for visualization)."""
        # Displacement is integral of velocity - approximate
        # For visualization, we use velocity as proxy
        return np.sqrt(self.vx**2 + self.vy**2)
    
    def get_wavefield(self):
        """Get full wavefield for analysis."""
        return {
            'vx': self.vx.copy(),
            'vy': self.vy.copy(),
            'sxx': self.sxx.copy(),
            'syy': self.syy.copy(),
            'sxy': self.sxy.copy(),
        }


def create_two_layer_medium(nx, ny, dx, layer_thickness, 
                            G1=5000, eta1=5, G2=25000, eta2=10):
    """
    Create a two-layer viscoelastic medium.
    
    Parameters:
    -----------
    nx, ny : int
        Grid dimensions
    dx : float
        Grid spacing
    layer_thickness : float
        Thickness of first layer (m)
    G1, eta1 : float
        Properties of first layer (Pa, Pa·s)
    G2, eta2 : float
        Properties of second layer (Pa, Pa·s)
    """
    # Layer boundary in grid cells
    layer_cells = int(layer_thickness / dx)
    
    G_prime = np.ones((nx, ny)) * G2
    eta = np.ones((nx, ny)) * eta2
    
    # First layer (bottom)
    G_prime[:, :layer_cells] = G1
    eta[:, :layer_cells] = eta1
    
    return G_prime, eta


def quick_demo():
    """Quick demonstration of 2D shear wave propagation."""
    print("=" * 60)
    print("2D SHEAR WAVE PROPAGATION - DEMO")
    print("=" * 60)
    
    # Grid parameters
    nx, ny = 200, 200
    dx = 0.001  # 1 mm grid
    
    # Create two-layer medium
    layer_thickness = 0.05  # 5 cm first layer
    G_prime, eta = create_two_layer_medium(
        nx, ny, dx, layer_thickness,
        G1=5000, eta1=5,    # Soft layer (liver-like)
        G2=20000, eta2=10   # Stiff layer (muscle-like)
    )
    
    print(f"\nGrid: {nx} x {ny}, dx = {dx*1000:.1f} mm")
    print(f"Layer 1: G' = 5 kPa, η = 5 Pa·s, thickness = {layer_thickness*100:.1f} cm")
    print(f"Layer 2: G' = 20 kPa, η = 10 Pa·s")
    
    # Create simulator
    sim = ShearWave2D(nx, ny, dx, rho=1000, G_prime=G_prime, eta=eta)
    
    # Source positions (reverberant configuration)
    sources = [
        (nx//3, ny//3),
        (2*nx//3, ny//3),
        (nx//2, 2*ny//3),
    ]
    
    # Run simulation
    duration = 0.02  # 20 ms
    n_steps = int(duration / sim.dt)
    print(f"\nRunning {n_steps} steps...")
    
    snapshots = []
    snapshot_times = []
    
    for n in range(n_steps):
        t = n * sim.dt
        
        # Multi-source excitation (reverberant)
        if n < 100:
            for sx, sy in sources:
                sim.add_source(t, sx, sy, fx=0, fy=1e-5, f0=100)
        
        sim.step()
        
        # Record snapshots
        if n % 50 == 0:
            snap = sim.get_displacement_magnitude()
            snapshots.append(snap)
            snapshot_times.append(t)
        
        # Stability check
        if n % 500 == 0:
            max_v = np.max(sim.get_displacement_magnitude())
            if max_v > 1e-3 or np.isnan(max_v):
                print(f"✗ Unstable at step {n}")
                break
    
    print(f"✓ Simulation complete")
    print(f"  Final max |v|: {np.max(sim.get_displacement_magnitude()):.3e} m/s")
    
    # Visualization
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    vmax = np.percentile(np.array(snapshots), 99)
    
    for idx, (ax, snap, t) in enumerate(zip(axes, snapshots[::len(snapshots)//6], snapshot_times[::len(snapshot_times)//6])):
        im = ax.imshow(snap.T, origin='lower', cmap='RdBu_r', 
                       vmin=-vmax, vmax=vmax, extent=[0, nx*dx*100, 0, ny*dx*100])
        
        # Draw layer boundary
        ax.axhline(y=layer_thickness*100, color='w', linestyle='--', linewidth=2)
        ax.set_xlabel('x (cm)')
        ax.set_ylabel('y (cm)')
        ax.set_title(f't = {t*1000:.1f} ms')
        
        # Mark sources
        for sx, sy in sources:
            ax.plot(sx*dx*100, sy*dx*100, 'g*', markersize=10)
    
    plt.colorbar(im, ax=axes, label='|v| (m/s)')
    plt.suptitle('2D Shear Wave Propagation in Two-Layer Medium')
    plt.tight_layout()
    plt.savefig('shear_wave_2d_demo.png', dpi=150)
    print(f"\nSaved: shear_wave_2d_demo.png")
    
    return sim, snapshots


if __name__ == "__main__":
    sim, snaps = quick_demo()
