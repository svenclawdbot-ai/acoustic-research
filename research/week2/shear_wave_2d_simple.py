"""
2D Shear Wave Simulator - Simplified Version
=============================================

Streamlined implementation focusing on correct physics.
Uses direct displacement formulation with proper Kelvin-Voigt damping.

Physics:
  ρ ∂²u/∂t² = G'∇²u + η∂(∇²u)/∂t

Discretization:
  u^{n+1} = 2u^n - u^{n-1} + (dt²/ρ)[G'∇²u^n + η(∇²u^n - ∇²u^{n-1})/dt]

Author: Research Project — Week 2
"""

import numpy as np
import matplotlib.pyplot as plt


class ShearWave2D:
    """Simplified 2D shear wave simulator."""
    
    def __init__(self, nx, ny, dx, dt=None, rho=1000, G_prime=5000, eta=5, pml_width=20):
        self.nx = nx
        self.ny = ny
        self.dx = dx
        self.pml_width = pml_width
        
        # Material properties (can be arrays)
        self.rho = np.ones((nx, ny)) * rho if np.isscalar(rho) else rho
        self.G_prime = np.ones((nx, ny)) * G_prime if np.isscalar(G_prime) else G_prime
        self.eta = np.ones((nx, ny)) * max(eta, 0.5) if np.isscalar(eta) else np.maximum(eta, 0.5)
        
        # Wave speed
        self.c_s = np.sqrt(self.G_prime / self.rho)
        
        # Time step
        if dt is None:
            # Conservative CFL
            dt_wave = 0.2 * dx / np.max(self.c_s)
            dt_viscous = 0.25 * np.min(self.rho) * dx**2 / (4 * np.max(self.eta))
            self.dt = min(dt_wave, dt_viscous)
        else:
            self.dt = dt
        
        courant = np.max(self.c_s) * self.dt / self.dx
        print(f"dt = {self.dt*1e6:.2f} μs, CFL = {courant:.3f}")
        
        # Displacement fields (two time levels)
        self.u = np.zeros((nx, ny))      # Current
        self.u_prev = np.zeros((nx, ny)) # Previous
        self.u_next = np.zeros((nx, ny)) # Next
        
        # Velocity (for output)
        self.v = np.zeros((nx, ny))
        
        # PML damping
        self._init_pml()
        
        # Grid
        self.x = np.arange(nx) * dx
        self.y = np.arange(ny) * dx
        
    def _init_pml(self):
        """Initialize PML damping."""
        nx, ny = self.nx, self.ny
        pml = self.pml_width
        
        # Damping coefficient (0 in interior, increases to max in PML)
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
    
    def laplacian(self, field):
        """5-point Laplacian."""
        result = np.zeros_like(field)
        result[1:-1, 1:-1] = (
            field[2:, 1:-1] + field[:-2, 1:-1] + 
            field[1:-1, 2:] + field[1:-1, :-2] - 
            4 * field[1:-1, 1:-1]
        ) / self.dx**2
        return result
    
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
            self.u[x_pos, y_pos] += source_val
    
    def step(self):
        """One time step."""
        dt = self.dt
        
        # Laplacian at current and previous time
        lap_u = self.laplacian(self.u)
        lap_u_prev = self.laplacian(self.u_prev)
        
        # Kelvin-Voigt: ρ∂²u/∂t² = G'∇²u + η∂(∇²u)/∂t
        # Discretized:
        elastic_term = self.G_prime * lap_u
        viscous_term = self.eta * (lap_u - lap_u_prev) / dt
        
        acceleration = (elastic_term + viscous_term) / self.rho
        
        # Update
        self.u_next[1:-1, 1:-1] = (
            2 * self.u[1:-1, 1:-1] - 
            self.u_prev[1:-1, 1:-1] + 
            dt**2 * acceleration[1:-1, 1:-1]
        )
        
        # PML damping (apply to the new field)
        damp_factor = (1 - self.damp_x) * (1 - self.damp_y)
        self.u_next *= damp_factor
        
        # Update velocity
        self.v = (self.u_next - self.u_prev) / (2 * dt)
        
        # Rotate fields
        self.u_prev, self.u, self.u_next = self.u, self.u_next, self.u_prev
    
    def get_displacement(self):
        """Get current displacement field."""
        return self.u.copy()
    
    def get_velocity(self):
        """Get current velocity field."""
        return self.v.copy()


def demo():
    """Demonstrate 2D wave propagation."""
    print("=" * 60)
    print("2D SHEAR WAVE - SIMPLIFIED FORMULATION")
    print("=" * 60)
    
    nx, ny = 150, 150
    dx = 0.001
    
    sim = ShearWave2D(nx, ny, dx, rho=1000, G_prime=5000, eta=5)
    
    print(f"\nGrid: {nx} x {ny}, dx = {dx*1000:.0f} mm")
    print(f"Shear wave speed: {np.sqrt(5000/1000):.1f} m/s")
    
    # Source at center
    sx, sy = nx//2, ny//4
    
    print(f"\nRunning simulation...")
    snapshots = []
    times = []
    
    for n in range(2000):
        t = n * sim.dt
        if n < 100:
            sim.add_source(t, sx, sy, amplitude=1e-7, f0=100)
        sim.step()
        
        if n % 100 == 0:
            snapshots.append(sim.get_displacement())
            times.append(t)
            max_u = np.max(np.abs(sim.u))
            print(f"  Step {n:4d}: max|u| = {max_u:.3e} m")
            
            if max_u > 1e-3 or np.isnan(max_u):
                print(f"  ✗ Unstable!")
                break
    
    print(f"\n✓ Simulation complete")
    
    # Plot
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    vmax = np.percentile(np.abs(np.array(snapshots)), 95)
    
    for ax, snap, t in zip(axes, snapshots[::len(snapshots)//6], times[::len(times)//6]):
        im = ax.imshow(snap.T, origin='lower', cmap='RdBu_r', 
                       vmin=-vmax, vmax=vmax, extent=[0, nx*dx*100, 0, ny*dx*100])
        ax.plot(sx*dx*100, sy*dx*100, 'g*', markersize=15)
        ax.set_xlabel('x (cm)')
        ax.set_ylabel('y (cm)')
        ax.set_title(f't = {t*1000:.1f} ms')
    
    plt.colorbar(im, ax=axes, label='Displacement (m)')
    plt.suptitle('2D Shear Wave Propagation')
    plt.tight_layout()
    plt.savefig('shear_wave_2d_simple.png', dpi=150)
    print(f"\nSaved: shear_wave_2d_simple.png")


if __name__ == "__main__":
    demo()
