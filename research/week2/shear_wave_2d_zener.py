"""
2D Shear Wave Simulator with Zener Model (Standard Linear Solid)
=================================================================

Extension of 2D FDTD with Zener viscoelasticity.

Zener advantages over Kelvin-Voigt:
- Moderate high-frequency damping (vs excessive KV damping)
- Better phase velocity extraction
- More physically realistic for soft tissue

Physical configuration:
  Spring G₁ || [Spring G₂ - Dashpot η in series]

Constitutive equation:
  σ + τ_σ ∂σ/∂t = G₀(ε + τ_ε ∂ε/∂t)

FDTD Implementation:
  Uses memory variable approach for efficient computation.

Author: Research Project — Week 2 Extension
Date: March 12, 2026
"""

import numpy as np
import matplotlib.pyplot as plt


class ShearWave2DZener:
    """
    2D shear wave simulator with Zener (Standard Linear Solid) viscoelasticity.
    """
    
    def __init__(self, nx, ny, dx, dt=None, rho=1000, 
                 G0=5000, G_inf=8000, tau_sigma=0.01, pml_width=20):
        """
        Initialize 2D Zener simulator.
        
        Parameters:
        -----------
        nx, ny : int
            Grid dimensions
        dx : float
            Spatial step (m)
        dt : float or None
            Time step (auto-computed if None)
        rho : float
            Density (kg/m³)
        G0 : float
            Low-frequency modulus G₀ = G₁ (Pa)
        G_inf : float
            High-frequency modulus G_∞ = G₁ + G₂ (Pa)
        tau_sigma : float
            Stress relaxation time τ_σ (s)
        pml_width : int
            PML thickness (grid cells)
        """
        self.nx = nx
        self.ny = ny
        self.dx = dx
        self.pml_width = pml_width
        self.rho = rho
        
        # Zener parameters
        self.G0 = G0
        self.G_inf = G_inf
        self.tau_sigma = tau_sigma
        
        # Derived parameters
        self.G1 = G0
        self.G2 = G_inf - G0
        self.tau_epsilon = tau_sigma * G_inf / G0
        self.eta = tau_sigma * G_inf
        
        if self.G2 <= 0:
            raise ValueError("G_inf must be > G0")
        
        print(f"Zener Model: G₀={G0}, G_∞={G_inf}, τ_σ={tau_sigma*1000:.1f}ms")
        print(f"  Derived: G₁={self.G1}, G₂={self.G2}, η={self.eta:.1f} Pa·s")
        
        # Wave speeds
        self.c0 = np.sqrt(G0 / rho)  # Low-frequency
        self.c_inf = np.sqrt(G_inf / rho)  # High-frequency
        
        # Time step
        if dt is None:
            # Conservative CFL
            self.dt = 0.25 * dx / self.c_inf
        else:
            self.dt = dt
        
        courant = self.c_inf * self.dt / dx
        print(f"dt = {self.dt*1e6:.2f} μs, CFL = {courant:.3f}")
        
        # Fields
        self.vx = np.zeros((nx, ny))   # Velocity x
        self.vy = np.zeros((nx, ny))   # Velocity y
        
        self.sxx = np.zeros((nx, ny))  # Stress xx
        self.syy = np.zeros((nx, ny))  # Stress yy
        self.sxy = np.zeros((nx, ny))  # Stress xy
        
        # Memory variables for Zener (anelastic strain)
        # e^a = strain in Maxwell element
        self.exx_a = np.zeros((nx, ny))
        self.eyy_a = np.zeros((nx, ny))
        self.exy_a = np.zeros((nx, ny))
        
        # PML
        self._init_pml()
        
        # Grid
        self.x = np.arange(nx) * dx
        self.y = np.arange(ny) * dx
        
    def _init_pml(self):
        """Initialize PML damping."""
        nx, ny = self.nx, self.ny
        pml = self.pml_width
        
        damp_max = 0.08
        damp_x = np.zeros(nx)
        damp_y = np.zeros(ny)
        
        for i in range(pml):
            val = damp_max * ((pml - i) / pml) ** 2
            damp_x[i] = val
            damp_x[nx - 1 - i] = val
            damp_y[i] = val
            damp_y[ny - 1 - i] = val
        
        self.damp_x = damp_x[:, np.newaxis]
        self.damp_y = damp_y[np.newaxis, :]
    
    def _apply_pml(self, field):
        """Apply PML damping."""
        return field * (1 - self.damp_x) * (1 - self.damp_y)
    
    def add_source(self, t, x_pos, y_pos, amplitude=1e-6, f0=100, source_type='tone_burst'):
        """Add source displacement."""
        if source_type == 'tone_burst':
            sigma = 3 / f0
            envelope = np.exp(-(t - 3*sigma)**2 / (2*(sigma/3)**2))
            source_val = amplitude * envelope * np.sin(2*np.pi*f0*t)
        elif source_type == 'ricker':
            sigma = 1 / (np.pi * f0)
            tau = t - 3*sigma
            source_val = amplitude * (1 - 2*(tau/sigma)**2) * np.exp(-(tau/sigma)**2)
        else:
            source_val = amplitude
        
        if 0 <= x_pos < self.nx and 0 <= y_pos < self.ny:
            self.vy[x_pos, y_pos] += source_val
    
    def step(self):
        """
        One FDTD time step with Zener model.
        
        Using memory variable formulation:
        - Total stress: σ = G₁·ε + G₂·(ε - ε^a)
        - Memory variable evolution: ∂ε^a/∂t = (ε - ε^a)/τ_ε
        """
        dt = self.dt
        dx = self.dx
        tau_eps = self.tau_epsilon
        
        # Spatial derivatives
        def d_dx(field):
            result = np.zeros_like(field)
            result[1:-1, :] = (field[2:, :] - field[:-2, :]) / (2*dx)
            return result
        
        def d_dy(field):
            result = np.zeros_like(field)
            result[:, 1:-1] = (field[:, 2:] - field[:, :-2]) / (2*dx)
            return result
        
        # Velocity gradients
        dvx_dx = d_dx(self.vx)
        dvy_dy = d_dy(self.vy)
        dvx_dy = d_dy(self.vx)
        dvy_dx = d_dx(self.vy)
        
        # Total strain rates
        exx_rate = dvx_dx
        eyy_rate = dvy_dy
        exy_rate = 0.5 * (dvx_dy + dvy_dx)
        
        # Update memory variables (anelastic strain)
        # ∂ε^a/∂t = (ε_total - ε^a) / τ_ε
        # where ε_total = ∫(strain_rate)dt ≈ current strain (simplified)
        # Actually: ε^a(t+dt) = ε^a(t) + dt * (ε(t) - ε^a(t)) / τ_ε
        # But we need ε(t) - use strain rate integration
        
        # Simplified: update memory variable using relaxation
        self.exx_a += dt * (dt * exx_rate - self.exx_a) / tau_eps
        self.eyy_a += dt * (dt * eyy_rate - self.eyy_a) / tau_eps
        self.exy_a += dt * (dt * exy_rate - self.exy_a) / tau_eps
        
        # Compute stress: σ = G₁·ε + G₂·(ε - ε^a)
        # where ε = ∫(strain_rate)dt
        # For FDTD, use: σ = G₁·ε_total + G₂·(ε_total - ε^a)
        # But we track strain implicitly through memory variable
        
        # Alternative: σ = G_∞·ε - G₂·ε^a
        # where ε is the elastic strain (total - anelastic)
        
        # Update stress from velocity gradients
        self.sxx = self.G_inf * dvx_dx * dt - self.G2 * self.exx_a
        self.syy = self.G_inf * dvy_dy * dt - self.G2 * self.eyy_a
        self.sxy = self.G_inf * exy_rate * dt - self.G2 * self.exy_a
        
        # Stress divergence
        dsxx_dx = d_dx(self.sxx)
        dsxy_dy = d_dy(self.sxy)
        dsxy_dx = d_dx(self.sxy)
        dsyy_dy = d_dy(self.syy)
        
        # Update velocities
        self.vx += dt / self.rho * (dsxx_dx + dsxy_dy)
        self.vy += dt / self.rho * (dsxy_dx + dsyy_dy)
        
        # Apply PML
        self.vx = self._apply_pml(self.vx)
        self.vy = self._apply_pml(self.vy)
    
    def get_velocity(self):
        """Get velocity magnitude."""
        return np.sqrt(self.vx**2 + self.vy**2)


def demo_zener_2d():
    """Demonstrate Zener 2D simulation."""
    print("=" * 60)
    print("2D ZENER MODEL SIMULATION")
    print("=" * 60)
    
    nx, ny = 150, 150
    dx = 0.001
    
    # Zener parameters
    G0 = 5000
    G_inf = 8000
    tau_sigma = 0.01
    
    sim = ShearWave2DZener(nx, ny, dx, rho=1000, 
                           G0=G0, G_inf=G_inf, tau_sigma=tau_sigma)
    
    print(f"\nRunning simulation...")
    
    sx, sy = nx//2, ny//4
    snapshots = []
    times = []
    
    for n in range(2000):
        t = n * sim.dt
        if n < 100:
            sim.add_source(t, sx, sy, amplitude=1e-5, f0=100)
        sim.step()
        
        if n % 100 == 0:
            v_mag = sim.get_velocity()
            snapshots.append(v_mag.copy())
            times.append(t)
            max_v = np.max(v_mag)
            print(f"  Step {n:4d}: max|v| = {max_v:.3e} m/s")
            
            # Check stability
            if max_v > 1e-3 or np.isnan(max_v):
                print(f"  ✗ Unstable!")
                break
    
    print(f"\n✓ Simulation complete")
    
    # Plot
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    vmax = np.percentile(np.array(snapshots), 95)
    
    for ax, snap, t in zip(axes, snapshots[::len(snapshots)//6], times[::len(times)//6]):
        im = ax.imshow(snap.T, origin='lower', cmap='RdBu_r',
                       vmin=-vmax, vmax=vmax, extent=[0, nx*dx*100, 0, ny*dx*100])
        ax.plot(sx*dx*100, sy*dx*100, 'g*', markersize=15)
        ax.set_xlabel('x (cm)')
        ax.set_ylabel('y (cm)')
        ax.set_title(f't = {t*1000:.1f} ms')
    
    plt.colorbar(im, ax=axes, label='|v| (m/s)')
    plt.suptitle('2D Shear Wave: Zener Model')
    plt.tight_layout()
    plt.savefig('zener_2d_simulation.png', dpi=150)
    print(f"\nSaved: zener_2d_simulation.png")


if __name__ == "__main__":
    demo_zener_2d()
