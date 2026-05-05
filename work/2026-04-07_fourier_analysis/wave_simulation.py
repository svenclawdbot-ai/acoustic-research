"""
Wave Equation Simulation: Finite Difference Method
Part 3.2 of 2026-04-07 Learning Challenge
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def solve_wave_equation_1d(L, T, c, nx, nt, init_func, 
                           boundary='fixed', snap_times=None):
    """
    Solve 1D wave equation using finite difference method.
    
    Wave equation: u_tt = c²·u_xx
    
    Parameters:
        L: String length
        T: Total simulation time
        c: Wave speed
        nx: Number of spatial grid points
        nt: Number of time steps
        init_func: Function u(x,0) for initial displacement
        boundary: 'fixed' (u=0) or 'free' (u_x=0)
        snap_times: List of times to save snapshots
    
    Returns:
        x: Spatial coordinates
        t: Time coordinates
        u: Solution array (nt x nx)
        snapshots: Dict of {time: displacement}
    """
    # Grid setup
    dx = L/(nx - 1)
    dt = T/nt
    
    # CFL condition for stability: c·dt/dx <= 1
    r = c*dt/dx
    if r > 1:
        print(f"Warning: CFL condition violated (r={r:.2f}). May be unstable.")
    
    x = np.linspace(0, L, nx)
    t = np.linspace(0, T, nt)
    
    # Solution array
    u = np.zeros((nt, nx))
    
    # Initial condition
    u[0, :] = init_func(x)
    
    # Initial velocity = 0 (released from rest)
    # For zero initial velocity, use special first time step
    u[1, :] = u[0, :]  # Approximation: u(x,dt) ≈ u(x,0)
    
    # Finite difference scheme
    # u[i,n+1] = 2·u[i,n] - u[i,n-1] + r²·(u[i+1,n] - 2·u[i,n] + u[i-1,n])
    
    snapshots = {}
    
    for n in range(1, nt - 1):
        for i in range(1, nx - 1):
            u[n+1, i] = (2*u[n, i] - u[n-1, i] + 
                        r**2*(u[n, i+1] - 2*u[n, i] + u[n, i-1]))
        
        # Boundary conditions
        if boundary == 'fixed':
            u[n+1, 0] = 0
            u[n+1, -1] = 0
        elif boundary == 'free':
            u[n+1, 0] = u[n+1, 1]  # du/dx = 0
            u[n+1, -1] = u[n+1, -2]
        
        # Save snapshots
        if snap_times and any(abs(t[n+1] - st) < dt/2 for st in snap_times):
            snapshots[t[n+1]] = u[n+1, :].copy()
    
    return x, t, u, snapshots


def plucked_string(x, L, pluck_pos=0.3):
    """Triangular initial displacement (plucked string)"""
    y = np.zeros_like(x)
    left = x < pluck_pos*L
    y[left] = x[left]/(pluck_pos*L)
    y[~left] = (L - x[~left])/(L*(1 - pluck_pos))
    return y


def gaussian_pulse(x, L, center=0.5, width=0.05):
    """Gaussian pulse initial condition"""
    return np.exp(-((x - center*L)**2)/(2*(width*L)**2))


def plot_wave_evolution(x, t, u, title="Wave Propagation", n_snapshots=4):
    """Plot wave at different time snapshots"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    snapshot_indices = np.linspace(0, len(t)-1, n_snapshots, dtype=int)
    colors = plt.cm.viridis(np.linspace(0, 1, n_snapshots))
    
    for idx, color in zip(snapshot_indices, colors):
        ax.plot(x, u[idx, :], color=color, label=f't = {t[idx]:.3f}')
    
    ax.set_xlabel('Position x')
    ax.set_ylabel('Displacement u')
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    return fig


def verify_energy_conservation(x, t, u, c):
    """
    Verify energy conservation numerically.
    
    Total energy = Kinetic + Potential
    KE = ½·ρ·∫(u_t)² dx
    PE = ½·T·∫(u_x)² dx  (where c² = T/ρ)
    """
    dx = x[1] - x[0]
    dt = t[1] - t[0]
    
    kinetic = []
    potential = []
    
    for n in range(1, len(t)-1):
        # u_t ≈ (u[n+1] - u[n-1])/(2·dt)
        u_t = (u[n+1, :] - u[n-1, :])/(2*dt)
        ke = 0.5*np.sum(u_t**2)*dx
        
        # u_x ≈ (u[n, 1:] - u[n, :-1])/dx
        u_x = (u[n, 1:] - u[n, :-1])/dx
        pe = 0.5*c**2*np.sum(u_x**2)*dx
        
        kinetic.append(ke)
        potential.append(pe)
    
    total = np.array(kinetic) + np.array(potential)
    
    # Plot
    fig, axes = plt.subplots(2, 1, figsize=(10, 8))
    
    axes[0].plot(t[1:-1], kinetic, label='Kinetic')
    axes[0].plot(t[1:-1], potential, label='Potential')
    axes[0].plot(t[1:-1], total, 'k--', label='Total', linewidth=2)
    axes[0].set_xlabel('Time')
    axes[0].set_ylabel('Energy')
    axes[0].set_title('Energy Conservation')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Relative energy change
    rel_change = (total - total[0])/total[0]
    axes[1].plot(t[1:-1], rel_change)
    axes[1].set_xlabel('Time')
    axes[1].set_ylabel('Relative Energy Change')
    axes[1].set_title(f'Max Energy Drift: {np.max(np.abs(rel_change)):.2e}')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig, total


if __name__ == "__main__":
    print("=" * 60)
    print("Wave Equation Simulation")
    print("=" * 60)
    
    # Parameters
    L = 1.0     # String length
    c = 1.0     # Wave speed
    T = 2.0     # Simulation time
    nx = 201    # Spatial grid points
    nt = 500    # Time steps
    
    output_dir = "/home/james/.openclaw/workspace/work/2026-04-07_fourier_analysis"
    
    # Simulation 1: Plucked string
    print("\n1. Plucked string simulation...")
    x, t, u, _ = solve_wave_equation_1d(
        L, T, c, nx, nt,
        init_func=lambda x: plucked_string(x, L, pluck_pos=0.3),
        boundary='fixed'
    )
    
    fig = plot_wave_evolution(x, t, u, title="Plucked String (Fixed Ends)")
    fig.savefig(f"{output_dir}/plucked_string.png")
    print("   Saved: plucked_string.png")
    
    fig, E = verify_energy_conservation(x, t, u, c)
    fig.savefig(f"{output_dir}/energy_plucked.png")
    print("   Saved: energy_plucked.png")
    
    # Simulation 2: Gaussian pulse
    print("\n2. Gaussian pulse propagation...")
    x2, t2, u2, _ = solve_wave_equation_1d(
        L, T, c, nx, nt,
        init_func=lambda x: gaussian_pulse(x, L, center=0.5, width=0.05),
        boundary='fixed'
    )
    
    fig = plot_wave_evolution(x2, t2, u2, title="Gaussian Pulse Propagation")
    fig.savefig(f"{output_dir}/gaussian_pulse.png")
    print("   Saved: gaussian_pulse.png")
    
    # Simulation 3: Free boundary
    print("\n3. String with free boundaries...")
    x3, t3, u3, _ = solve_wave_equation_1d(
        L, T, c, nx, nt,
        init_func=lambda x: gaussian_pulse(x, L, center=0.5, width=0.1),
        boundary='free'
    )
    
    fig = plot_wave_evolution(x3, t3, u3, title="Pulse with Free Boundaries")
    fig.savefig(f"{output_dir}/free_boundary.png")
    print("   Saved: free_boundary.png")
    
    print("\n" + "=" * 60)
    print("All simulations complete!")
    print(f"Output directory: {output_dir}")
    print("=" * 60)
