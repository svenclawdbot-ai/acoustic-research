"""
Gaussian Splatting for Ultrasonic Wavefield Reconstruction
===========================================================

Represents wavefield as sum of anisotropic Gaussians in (x, t) space:
    u(x,t) = Σᵢ αᵢ · G(x - μᵢ; Σᵢ) · exp(j(ωᵢt - kᵢx))

Each Gaussian primitive carries:
- Position μ = (x₀, t₀): Wave packet center
- Covariance Σ: Spatiotemporal extent (beam width, pulse duration)
- Amplitude α: Wave magnitude
- Frequency ω: With dispersion k(ω) from Zener model

Optimized via gradient descent to match sparse receiver measurements.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import sys
sys.path.insert(0, '/home/james/.openclaw/workspace')
sys.path.insert(0, '/home/james/.openclaw/workspace/research/week2')

from shear_wave_2d_zener import ShearWave2DZener
from zener_model import ZenerModel


class WavefieldGaussian:
    """
    Single Gaussian wave packet primitive.
    
    Represents localized wave energy with Gaussian envelope
    and dispersive phase propagation.
    """
    
    def __init__(self, x0, t0, sigma_x, sigma_t, amplitude, omega, 
                 zener_model=None):
        """
        Initialize Gaussian wave packet.
        
        Parameters:
        -----------
        x0, t0 : float
            Center position (m) and time (s)
        sigma_x, sigma_t : float
            Spatial and temporal standard deviations
        amplitude : float
            Peak amplitude
        omega : float
            Angular frequency (rad/s)
        zener_model : ZenerModel
            For dispersion relation k(ω)
        """
        self.x0 = x0
        self.t0 = t0
        self.sigma_x = sigma_x
        self.sigma_t = sigma_t
        self.amplitude = amplitude
        self.omega = omega
        self.zm = zener_model
        
        # Compute wavenumber from dispersion relation
        if zener_model is not None and omega > 0:
            c = zener_model.phase_velocity(omega)
            self.k = omega / c
        else:
            self.k = 0
    
    def evaluate(self, x, t):
        """
        Evaluate Gaussian at points (x, t).
        
        Parameters:
        -----------
        x : array (nx,)
            Spatial positions
        t : array (nt,)
            Time points
            
        Returns:
        --------
        u : array (nx, nt)
            Complex wavefield values
        """
        X, T = np.meshgrid(x, t, indexing='ij')
        
        # Gaussian envelope
        envelope = np.exp(-0.5 * ((X - self.x0)**2 / self.sigma_x**2 + 
                                   (T - self.t0)**2 / self.sigma_t**2))
        
        # Dispersive phase
        phase = np.exp(1j * (self.omega * T - self.k * X))
        
        return self.amplitude * envelope * phase
    
    def evaluate_at_points(self, x_points, t_points):
        """Evaluate at specific (x, t) points (for sparse receivers)."""
        # Gaussian envelope
        envelope = np.exp(-0.5 * ((x_points - self.x0)**2 / self.sigma_x**2 + 
                                   (t_points - self.t0)**2 / self.sigma_t**2))
        
        # Dispersive phase
        phase = np.exp(1j * (self.omega * t_points - self.k * x_points))
        
        return self.amplitude * envelope * phase


class GaussianWavefieldSplat:
    """
    Wavefield as sum of Gaussian primitives.
    
    Optimizes Gaussian parameters to match sparse measurements.
    """
    
    def __init__(self, n_gaussians, x_bounds, t_bounds, zener_model):
        """
        Initialize Gaussian splat representation.
        
        Parameters:
        -----------
        n_gaussians : int
            Number of Gaussian primitives
        x_bounds : tuple (x_min, x_max)
            Spatial domain bounds
        t_bounds : tuple (t_min, t_max)
            Temporal domain bounds
        zener_model : ZenerModel
            Dispersion relation
        """
        self.n_gauss = n_gaussians
        self.x_min, self.x_max = x_bounds
        self.t_min, self.t_max = t_bounds
        self.zm = zener_model
        
        # Initialize Gaussian parameters
        self.gaussians = self._initialize_gaussians()
        
    def _initialize_gaussians(self):
        """Initialize Gaussian primitives near signal locations."""
        gaussians = []
        
        for i in range(self.n_gauss):
            # Cluster around center of domain where signal likely is
            x0 = np.random.uniform(self.x_min + (self.x_max-self.x_min)*0.2, 
                                   self.x_min + (self.x_max-self.x_min)*0.5)
            t0 = np.random.uniform(self.t_min + (self.t_max-self.t_min)*0.1, 
                                   self.t_min + (self.t_max-self.t_min)*0.4)
            
            # Moderate scales
            sigma_x = np.exp(np.random.uniform(np.log(0.003), np.log(0.015)))
            sigma_t = np.exp(np.random.uniform(np.log(0.002), np.log(0.008)))
            
            # Random frequency (80-250 Hz range)
            f = np.random.uniform(80, 250)
            omega = 2 * np.pi * f
            
            # Non-zero amplitude initialization
            amplitude = np.random.uniform(1e-5, 3e-5)
            
            g = WavefieldGaussian(x0, t0, sigma_x, sigma_t, 
                                 amplitude, omega, self.zm)
            gaussians.append(g)
        
        return gaussians
    
    def evaluate(self, x, t):
        """Evaluate full wavefield as sum of Gaussians."""
        u = np.zeros((len(x), len(t)), dtype=complex)
        
        for g in self.gaussians:
            u += g.evaluate(x, t)
        
        return u
    
    def evaluate_at_receivers(self, rec_idx, x_array, t_array):
        """
        Evaluate at sparse receiver positions.
        
        Parameters:
        -----------
        rec_idx : array
            Receiver spatial indices
        x_array : array
            Full spatial grid
        t_array : array
            Time array
            
        Returns:
        --------
        y : array (n_receivers, n_times)
            Wavefield at receiver positions
        """
        n_rec = len(rec_idx)
        nt = len(t_array)
        y = np.zeros((n_rec, nt), dtype=complex)
        
        for i, idx in enumerate(rec_idx):
            x_pos = x_array[idx]
            for g in self.gaussians:
                y[i, :] += g.evaluate_at_points(x_pos, t_array)
        
        return y
    
    def get_params(self):
        """Get all Gaussian parameters as flat array."""
        params = []
        for g in self.gaussians:
            params.extend([
                g.x0, g.t0, 
                g.sigma_x, g.sigma_t,
                g.amplitude,
                g.omega
            ])
        return np.array(params)
    
    def set_params(self, params):
        """Set Gaussian parameters from flat array."""
        for i, g in enumerate(self.gaussians):
            idx = i * 6
            g.x0 = params[idx]
            g.t0 = params[idx + 1]
            g.sigma_x = params[idx + 2]
            g.sigma_t = params[idx + 3]
            g.amplitude = params[idx + 4]
            g.omega = params[idx + 5]
            
            # Update wavenumber from dispersion
            if g.omega > 0:
                c = self.zm.phase_velocity(g.omega)
                g.k = g.omega / c
    
    def bounds(self):
        """Return parameter bounds for optimization."""
        bounds = []
        for _ in range(self.n_gauss):
            bounds.extend([
                (self.x_min, self.x_max),      # x0
                (self.t_min, self.t_max),      # t0
                (0.0005, 0.05),                # sigma_x
                (0.0005, 0.02),                # sigma_t
                (0, 1e-4),                     # amplitude
                (2*np.pi*20, 2*np.pi*500)      # omega
            ])
        return bounds


def optimize_gaussian_splat(y_sparse, rec_idx, x_array, t_array, 
                            zener_model, n_gaussians=20, max_iter=500):
    """
    Optimize Gaussian primitives to match sparse measurements.
    
    Parameters:
    -----------
    y_sparse : array (n_rec, nt)
        Sparse measurements
    rec_idx : array
        Receiver indices
    x_array : array
        Spatial grid
    t_array : array
        Time grid
    zener_model : ZenerModel
        Dispersion relation
    n_gaussians : int
        Number of primitives
    max_iter : int
        Optimization iterations
        
    Returns:
    --------
    splat : GaussianWavefieldSplat
        Optimized Gaussian representation
    """
    print(f"\n[3] Optimizing {n_gaussians} Gaussian primitives...")
    
    # Initialize splat
    splat = GaussianWavefieldSplat(
        n_gaussians,
        x_bounds=(x_array[0], x_array[-1]),
        t_bounds=(t_array[0], t_array[-1]),
        zener_model=zener_model
    )
    
    # Objective function
    def objective(params):
        splat.set_params(params)
        y_pred = splat.evaluate_at_receivers(rec_idx, x_array, t_array)
        
        # Data fidelity (weighted by signal presence)
        residual = y_sparse - y_pred
        data_fit = np.sum(np.abs(residual)**2)
        
        # Very weak L2 regularization on amplitudes (not L1)
        l2_penalty = 0
        for g in splat.gaussians:
            l2_penalty += g.amplitude**2
        
        # Encourage compact Gaussians
        sigma_penalty = 0
        for g in splat.gaussians:
            sigma_penalty += g.sigma_x + g.sigma_t
        
        return data_fit + 1e-10 * l2_penalty + 1e-8 * sigma_penalty
    
    # Optimize
    x0 = splat.get_params()
    bounds = splat.bounds()
    
    print(f"  Parameters: {len(x0)}")
    print(f"  Measurements: {y_sparse.size}")
    
    result = minimize(
        objective,
        x0,
        method='L-BFGS-B',
        bounds=bounds,
        options={'maxiter': max_iter, 'ftol': 1e-12, 'gtol': 1e-8}
    )
    
    splat.set_params(result.x)
    
    final_obj = objective(result.x)
    print(f"  Final objective: {final_obj:.2e}")
    print(f"  Iterations: {result.nit}")
    
    return splat


def run_gaussian_splat_demo():
    """Demonstrate Gaussian Splatting for wavefield reconstruction."""
    print("=" * 70)
    print("GAUSSIAN SPLATTING FOR ULTRASONIC WAVEFIELD RECONSTRUCTION")
    print("=" * 70)
    
    # 1. Generate synthetic wavefield
    print("\n[1] Generating wavefield...")
    nx, ny = 100, 80
    dx = 0.002
    sim = ShearWave2DZener(nx, ny, dx, rho=1000, 
                           G0=2000, G_inf=4000, tau_sigma=0.005)
    
    nt_steps = 800
    wavefield = []
    t_array = []
    
    for n in range(nt_steps):
        t = n * sim.dt
        if t < 0.015:
            f_inst = 80 + (250 - 80) * (t / 0.015)
            envelope = np.exp(-(t - 0.0075)**2 / (2 * 0.003**2))
            sim.add_source(t, nx//5, ny//2, amplitude=2e-5 * envelope,
                          f0=f_inst, source_type='ricker')
        sim.step()
        
        if n % 3 == 0:
            wavefield.append(sim.vy[:, ny//2].copy())
            t_array.append(t)
    
    u_full = np.array(wavefield).T
    dt = sim.dt * 3
    x = sim.x
    t = np.array(t_array)
    
    print(f"  Shape: {u_full.shape}")
    print(f"  Amplitude: {np.abs(u_full).max():.2e}")
    
    # 2. Sparse sampling - use MORE receivers and ensure coverage
    print("\n[2] Sparse sampling...")
    n_rec = 20  # Increased from 10
    np.random.seed(42)
    # Ensure we have receivers across the domain including where signal is
    rec_idx = np.sort(np.random.choice(nx, n_rec, replace=False))
    y_sparse = u_full[rec_idx, :]
    print(f"  {n_rec} receivers at positions: {[round(x[i]*100,1) for i in rec_idx]} cm")
    
    # 3. Optimize Gaussian splat
    zm = ZenerModel(2000, 4000, 0.005)
    splat = optimize_gaussian_splat(y_sparse, rec_idx, x, t, zm, 
                                    n_gaussians=15, max_iter=300)
    
    # 4. Reconstruct
    print("\n[4] Reconstructing wavefield...")
    u_recon = splat.evaluate(x, t)
    
    # Quality metrics
    nmse = np.mean(np.abs(u_full - u_recon)**2) / np.mean(np.abs(u_full)**2)
    corr = np.corrcoef(np.real(u_full).flatten(), np.real(u_recon).flatten())[0, 1]
    print(f"  NMSE: {nmse:.4f}")
    print(f"  Correlation: {corr:.4f}")
    
    # 5. Visualize
    print("\n[5] Generating visualization...")
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    
    extent = [t[0]*1000, t[-1]*1000, x[0]*100, x[-1]*100]
    vmax = np.percentile(np.abs(u_full), 99)
    
    # Ground truth
    im0 = axes[0, 0].imshow(np.real(u_full), aspect='auto', origin='lower',
                            extent=extent, cmap='RdBu_r', vmin=-vmax, vmax=vmax)
    axes[0, 0].set_title('Ground Truth')
    axes[0, 0].set_ylabel('Position (cm)')
    plt.colorbar(im0, ax=axes[0, 0])
    
    # Sparse samples
    u_sparse = np.zeros_like(u_full)
    u_sparse[rec_idx, :] = y_sparse
    im1 = axes[0, 1].imshow(np.real(u_sparse), aspect='auto', origin='lower',
                            extent=extent, cmap='RdBu_r', vmin=-vmax, vmax=vmax)
    axes[0, 1].set_title(f'Sparse Samples ({n_rec} rec)')
    plt.colorbar(im1, ax=axes[0, 1])
    
    # Reconstructed
    im2 = axes[0, 2].imshow(np.real(u_recon), aspect='auto', origin='lower',
                            extent=extent, cmap='RdBu_r', vmin=-vmax, vmax=vmax)
    axes[0, 2].set_title(f'Gaussian Splat (r={corr:.2f})')
    plt.colorbar(im2, ax=axes[0, 2])
    
    # Error
    error = np.abs(u_full - u_recon)
    im3 = axes[1, 0].imshow(error, aspect='auto', origin='lower',
                            extent=extent, cmap='hot')
    axes[1, 0].set_title('Absolute Error')
    axes[1, 0].set_xlabel('Time (ms)')
    axes[1, 0].set_ylabel('Position (cm)')
    plt.colorbar(im3, ax=axes[1, 0])
    
    # Gaussian primitives
    ax = axes[1, 1]
    for i, g in enumerate(splat.gaussians):
        # Draw ellipse for 2σ
        from matplotlib.patches import Ellipse
        ellipse = Ellipse(
            (g.t0*1000, g.x0*100), 
            width=4*g.sigma_t*1000, 
            height=4*g.sigma_x*100,
            angle=0,
            fill=False,
            edgecolor=f'C{i % 10}',
            linewidth=2,
            alpha=0.7,
            label=f'G{i}: f={g.omega/(2*np.pi):.0f}Hz'
        )
        ax.add_patch(ellipse)
        ax.plot(g.t0*1000, g.x0*100, 'o', color=f'C{i % 10}', markersize=5)
    
    ax.set_xlim(extent[0], extent[1])
    ax.set_ylim(extent[2], extent[3])
    ax.set_xlabel('Time (ms)')
    ax.set_ylabel('Position (cm)')
    ax.set_title('Gaussian Primitives')
    ax.grid(True, alpha=0.3)
    
    # Parameter summary
    ax = axes[1, 2]
    ax.axis('off')
    
    summary = f"""
    Gaussian Splat Results:
    ----------------------
    Receivers: {n_rec}/{nx} ({n_rec/nx*100:.1f}%)
    Gaussians: {splat.n_gauss}
    
    Quality Metrics:
    ---------------
    NMSE: {nmse:.4f}
    Correlation: {corr:.4f}
    
    Active Gaussians:
    ----------------
    """
    
    for i, g in enumerate(splat.gaussians[:8]):  # Show first 8
        summary += f"G{i}: f={g.omega/(2*np.pi):.0f}Hz, "
        summary += f"α={g.amplitude:.2e}, "
        summary += f"at ({g.x0*100:.1f},{g.t0*1000:.1f}), "
        summary += f"σ=({g.sigma_x*100:.2f},{g.sigma_t*1000:.1f})\n"
    
    ax.text(0.1, 0.5, summary, transform=ax.transAxes, fontsize=10,
           verticalalignment='center', fontfamily='monospace',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig('gaussian_splat_wavefield.png', dpi=150)
    print("  Saved: gaussian_splat_wavefield.png")
    
    print("\n" + "=" * 70)
    print("GAUSSIAN SPLAT RECONSTRUCTION COMPLETE")
    print("=" * 70)
    
    return splat, u_full, u_recon, nmse, corr


if __name__ == "__main__":
    splat, u_full, u_recon, nmse, corr = run_gaussian_splat_demo()
