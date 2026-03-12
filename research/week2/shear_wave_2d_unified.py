"""
2D Shear Wave Simulator - Unified Interface
============================================

Supports both Kelvin-Voigt and Zener (Standard Linear Solid) models.

Model Selection:
---------------
• 'kelvin_voigt': σ = G'ε + η∂ε/∂t
  - Simple, stable
  - Excessive high-frequency damping
  - Good for inverse problem validation

• 'zener': σ + τ_σ∂σ/∂t = G₀(ε + τ_ε∂ε/∂t)  
  - More realistic
  - Moderate damping (better for phase extraction)
  - More complex implementation

Usage:
  from shear_wave_2d_unified import ShearWave2D
  
  # Kelvin-Voigt (default)
  sim = ShearWave2D(nx, ny, dx, model='kelvin_voigt', G_prime=5000, eta=5)
  
  # Zener
  sim = ShearWave2D(nx, ny, dx, model='zener', G0=5000, G_inf=8000, tau_sigma=0.01)
"""

import numpy as np
import matplotlib.pyplot as plt


class ShearWave2D:
    """
    Unified 2D shear wave simulator.
    Supports Kelvin-Voigt and Zener viscoelastic models.
    """
    
    def __init__(self, nx, ny, dx, dt=None, rho=1000, model='kelvin_voigt', 
                 pml_width=20, **model_params):
        """
        Initialize 2D simulator.
        
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
        model : str
            'kelvin_voigt' or 'zener'
        pml_width : int
            PML thickness
        **model_params:
            For KV: G_prime, eta
            For Zener: G0, G_inf, tau_sigma
        """
        self.nx = nx
        self.ny = ny
        self.dx = dx
        self.rho = rho
        self.pml_width = pml_width
        self.model_type = model
        
        # Model setup
        if model == 'kelvin_voigt':
            self._init_kelvin_voigt(**model_params)
        elif model == 'zener':
            self._init_zener(**model_params)
        else:
            raise ValueError(f"Unknown model: {model}")
        
        # Time step
        if dt is None:
            self._compute_dt()
        else:
            self.dt = dt
        
        # Initialize fields
        self._init_fields()
        self._init_pml()
        
        print(f"2D {model.replace('_', ' ').title()} Simulator initialized")
        print(f"  Grid: {nx}x{ny}, dx={dx*1000:.1f}mm, dt={self.dt*1e6:.1f}μs")
    
    def _init_kelvin_voigt(self, G_prime=5000, eta=5):
        """Initialize Kelvin-Voigt parameters."""
        self.G_prime = G_prime
        self.eta = max(eta, 0.5)  # Minimum for stability
        self.c_s = np.sqrt(G_prime / self.rho)
        print(f"  KV: G'={G_prime}Pa, η={self.eta}Pa·s, c_s={self.c_s:.2f}m/s")
    
    def _init_zener(self, G0=5000, G_inf=8000, tau_sigma=0.01):
        """Initialize Zener parameters."""
        self.G0 = G0
        self.G_inf = G_inf
        self.tau_sigma = tau_sigma
        self.G1 = G0
        self.G2 = G_inf - G0
        self.tau_epsilon = tau_sigma * G_inf / G0
        self.eta_zener = tau_sigma * G_inf
        
        self.c0 = np.sqrt(G0 / self.rho)
        self.c_inf = np.sqrt(G_inf / self.rho)
        print(f"  Zener: G₀={G0}, G_∞={G_inf}, τ_σ={tau_sigma*1000:.1f}ms")
        print(f"    c₀={self.c0:.2f}, c_∞={self.c_inf:.2f}m/s")
    
    def _compute_dt(self):
        """Compute stable time step."""
        if self.model_type == 'kelvin_voigt':
            # KV constraints
            dt_wave = 0.2 * self.dx / self.c_s
            dt_viscous = 0.5 * self.rho * self.dx**2 / (4 * self.eta)
            self.dt = min(dt_wave, dt_viscous)
        else:  # zener
            # Zener constraint (based on high-freq speed)
            self.dt = 0.25 * self.dx / self.c_inf
    
    def _init_fields(self):
        """Initialize field arrays."""
        nx, ny = self.nx, self.ny
        
        # Common fields
        self.u = np.zeros((nx, ny))       # Displacement
        self.u_prev = np.zeros((nx, ny))  # Previous displacement
        self.u_next = np.zeros((nx, ny))  # Next displacement
        
        self.v = np.zeros((nx, ny))       # Velocity (for output)
        
        # Zener-specific memory variables
        if self.model_type == 'zener':
            self.e_a = np.zeros((nx, ny))  # Anelastic strain (simplified)
    
    def _init_pml(self):
        """Initialize PML."""
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
    
    def _laplacian(self, field):
        """5-point Laplacian."""
        result = np.zeros_like(field)
        result[1:-1, 1:-1] = (
            field[2:, 1:-1] + field[:-2, 1:-1] + 
            field[1:-1, 2:] + field[1:-1, :-2] - 
            4 * field[1:-1, 1:-1]
        ) / self.dx**2
        return result
    
    def add_source(self, t, x_pos, y_pos, amplitude=1e-6, f0=100, source_type='tone_burst'):
        """Add source."""
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
        if self.model_type == 'kelvin_voigt':
            self._step_kv()
        else:
            self._step_zener()
    
    def _step_kv(self):
        """Kelvin-Voigt time step."""
        dt = self.dt
        
        # Laplacian
        lap_u = self._laplacian(self.u)
        lap_u_prev = self._laplacian(self.u_prev)
        
        # KV: ρ∂²u/∂t² = G'∇²u + η∂(∇²u)/∂t
        elastic = self.G_prime * lap_u
        viscous = self.eta * (lap_u - lap_u_prev) / dt
        accel = (elastic + viscous) / self.rho
        
        # Update
        self.u_next[1:-1, 1:-1] = (
            2*self.u[1:-1, 1:-1] - self.u_prev[1:-1, 1:-1] + 
            dt**2 * accel[1:-1, 1:-1]
        )
        
        # PML
        self.u_next = self._apply_pml(self.u_next)
        
        # Velocity
        self.v = (self.u_next - self.u_prev) / (2*dt)
        
        # Rotate
        self.u_prev, self.u, self.u_next = self.u, self.u_next, self.u_prev
    
    def _step_zener(self):
        """Zener time step - simplified implementation."""
        dt = self.dt
        
        # Laplacian
        lap_u = self._laplacian(self.u)
        
        # Effective modulus (frequency-dependent approximation)
        # Use high-frequency modulus for wave propagation
        # This is a simplification - full Zener requires memory variables
        G_eff = self.G_inf
        
        # Wave equation with effective modulus
        accel = G_eff * lap_u / self.rho
        
        # Update
        self.u_next[1:-1, 1:-1] = (
            2*self.u[1:-1, 1:-1] - self.u_prev[1:-1, 1:-1] + 
            dt**2 * accel[1:-1, 1:-1]
        )
        
        # Apply damping to simulate Zener dissipation
        # Loss proportional to velocity (simplified)
        damping = self.eta_zener / self.G_inf
        self.u_next -= damping * (self.u - self.u_prev)
        
        # PML
        self.u_next = self._apply_pml(self.u_next)
        
        # Velocity
        self.v = (self.u_next - self.u_prev) / (2*dt)
        
        # Rotate
        self.u_prev, self.u, self.u_next = self.u, self.u_next, self.u_prev
    
    def get_displacement(self):
        """Get displacement field."""
        return self.u.copy()
    
    def get_velocity(self):
        """Get velocity field."""
        return self.v.copy()


def compare_models():
    """Compare Kelvin-Voigt and Zener models."""
    print("=" * 70)
    print("MODEL COMPARISON: Kelvin-Voigt vs Zener")
    print("=" * 70)
    
    nx, ny = 120, 120
    dx = 0.001
    
    # Kelvin-Voigt
    print("\n[1] Kelvin-Voigt Model")
    sim_kv = ShearWave2D(nx, ny, dx, model='kelvin_voigt', 
                         G_prime=5000, eta=5, pml_width=10)
    
    sx, sy = nx//2, ny//4
    for n in range(800):
        t = n * sim_kv.dt
        if n < 50:
            sim_kv.add_source(t, sx, sy, amplitude=1e-5, f0=100)
        sim_kv.step()
    
    u_kv = sim_kv.get_displacement()
    max_kv = np.max(np.abs(u_kv))
    print(f"  Max displacement: {max_kv:.3e} m")
    
    # Zener
    print("\n[2] Zener Model")
    sim_z = ShearWave2D(nx, ny, dx, model='zener',
                        G0=5000, G_inf=8000, tau_sigma=0.01, pml_width=10)
    
    for n in range(800):
        t = n * sim_z.dt
        if n < 50:
            sim_z.add_source(t, sx, sy, amplitude=1e-5, f0=100)
        sim_z.step()
    
    u_z = sim_z.get_displacement()
    max_z = np.max(np.abs(u_z))
    print(f"  Max displacement: {max_z:.3e} m")
    
    # Compare
    print("\n" + "=" * 70)
    print("COMPARISON")
    print("=" * 70)
    print(f"  KV max |u|: {max_kv:.3e}")
    print(f"  Zener max |u|: {max_z:.3e}")
    print(f"  Ratio (Zener/KV): {max_z/max_kv:.2f}")
    
    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    vmax = max(np.max(np.abs(u_kv)), np.max(np.abs(u_z)))
    
    im1 = axes[0].imshow(u_kv.T, origin='lower', cmap='RdBu_r',
                          vmin=-vmax, vmax=vmax)
    axes[0].set_title('Kelvin-Voigt')
    axes[0].set_xlabel('x')
    axes[0].set_ylabel('y')
    
    im2 = axes[1].imshow(u_z.T, origin='lower', cmap='RdBu_r',
                          vmin=-vmax, vmax=vmax)
    axes[1].set_title('Zener')
    axes[1].set_xlabel('x')
    axes[1].set_ylabel('y')
    
    plt.colorbar(im2, ax=axes, label='Displacement (m)')
    plt.tight_layout()
    plt.savefig('model_comparison.png', dpi=150)
    print("\n  Saved: model_comparison.png")


if __name__ == "__main__":
    compare_models()
