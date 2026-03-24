"""
Working CS Pipeline with Physics-Informed Prior
===============================================

Clean implementation integrating:
1. Zener dispersion dictionary
2. ADMM reconstruction
3. Sparse receiver arrays

Works with 8-16 receivers for practical reconstruction.

Author: DSP Challenge — March 18, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append('/home/james/.openclaw/workspace/research/week2')
from shear_wave_2d_zener import ShearWave2DZener
from zener_model import ZenerModel


class WorkingCSPipeline:
    """
    Complete CS pipeline with physics-informed prior.
    
    Uses frequency-domain approach:
    - Transform to frequency domain
    - For each frequency: solve sparse recovery
    - Use Zener dispersion as initialization/prior
    """
    
    def __init__(self, x_array, t_array, zener_params, rho=1000):
        """
        Initialize pipeline.
        
        Parameters:
        -----------
        x_array : array
            Spatial grid (m)
        t_array : array
            Time grid (s)
        zener_params : tuple (G0, G_inf, tau_sigma)
            Zener model parameters
        """
        self.x = np.array(x_array)
        self.t = np.array(t_array)
        self.nx = len(x_array)
        self.nt = len(t_array)
        self.dx = x_array[1] - x_array[0]
        self.dt = t_array[1] - t_array[0]
        
        self.G0, self.G_inf, self.tau_sigma = zener_params
        self.rho = rho
        self.zm = ZenerModel(self.G0, self.G_inf, self.tau_sigma)
        
        # Frequency axis
        self.omega = 2 * np.pi * np.fft.rfftfreq(self.nt, self.dt)
        self.n_freq = len(self.omega)
        
        # Wavenumber axis
        self.k = 2 * np.pi * np.fft.fftfreq(self.nx, self.dx)
        
        print(f"CS Pipeline initialized:")
        print(f"  Grid: {self.nx} × {self.nt}")
        print(f"  Frequencies: {self.n_freq}")
        print(f"  Zener: G₀={self.G0}, G∞={self.G_inf}")
    
    def build_fourier_basis(self):
        """Build spatial Fourier basis matrix."""
        # Phi[i,j] = exp(i * k[j] * x[i])
        X, K = np.meshgrid(self.x, self.k, indexing='ij')
        self.Phi = np.exp(1j * K * X) / np.sqrt(self.nx)
        print(f"  Fourier basis: {self.Phi.shape}")
        return self.Phi
    
    def reconstruct_frequency_domain(self, y_sparse, rec_idx, 
                                     lambda_reg=0.1, n_iter=100):
        """
        Reconstruct using frequency-domain CS with Zener prior.
        
        For each frequency ω:
        1. Extract y_ω from measurements
        2. Solve: s_ω = argmin ||y_ω - A·s_ω||² + λ||s_ω||₁
        3. Use Zener dispersion to weight/warm-start
        
        Parameters:
        -----------
        y_sparse : ndarray (n_rec, nt)
            Sparse measurements
        rec_idx : array
            Receiver indices
        lambda_reg : float
            L1 regularization parameter
        n_iter : int
            Iterations per frequency
            
        Returns:
        --------
        u_recon : ndarray (nx, nt)
            Reconstructed wavefield
        """
        n_rec = len(rec_idx)
        
        # Build sensing matrix for receivers
        A = self.Phi[rec_idx, :]  # (n_rec, nx)
        
        # Transform measurements to frequency domain
        Y_freq = np.fft.rfft(y_sparse, axis=1)  # (n_rec, n_freq)
        
        print(f"\nFrequency-domain CS:")
        print(f"  Receivers: {n_rec}")
        print(f"  Frequencies: {self.n_freq}")
        print(f"  Sensing matrix: {A.shape}")
        
        # Storage for reconstructed spectrum
        S_recon = np.zeros((self.nx, self.n_freq), dtype=complex)
        
        # Process each frequency
        for i_freq, omega in enumerate(self.omega):
            if i_freq % 20 == 0:
                print(f"  Freq {i_freq}/{self.n_freq}: ω={omega:.1f} rad/s")
            
            y_omega = Y_freq[:, i_freq]
            
            # Get dispersion-informed prior for this frequency
            # Prior: k should be near ω/c(ω)
            if omega > 0:
                c_omega = self.zm.phase_velocity(omega)
                k_expected = omega / c_omega
                
                # Build weights (closer to expected k = lower regularization)
                k_dist = np.abs(np.abs(self.k) - k_expected)
                weights = 1 / (1 + k_dist * 0.1)  # Soft weighting
            else:
                weights = np.ones(self.nx)
            
            # Iterative soft thresholding with weighted L1
            # Use pseudo-inverse initialization
            s_init = np.linalg.lstsq(A, y_omega, rcond=None)[0]
            s = self._ista_weighted(A, y_omega, lambda_reg, weights, n_iter, s_init)
            
            # If ISTA fails, fall back to pseudo-inverse
            if np.linalg.norm(s) < 1e-10:
                s = s_init
            
            S_recon[:, i_freq] = s
        
        # Transform back to time domain
        u_recon = np.fft.irfft(S_recon, n=self.nt, axis=1)
        
        return u_recon
    
    def _ista_weighted(self, A, y, lambda_reg, weights, n_iter, s_init=None):
        """
        Weighted iterative soft thresholding.
        
        min ||y - A·s||² + λ·||w⊙s||₁
        """
        n = A.shape[1]
        
        # Lipschitz constant
        L = np.linalg.norm(A.conj().T @ A, 2)
        step = 0.5 / L  # More conservative step
        
        # Initialize
        if s_init is not None:
            s = s_init.copy()
        else:
            s = A.conj().T @ y / L
        
        for it in range(n_iter):
            # Gradient step
            residual = y - A @ s
            s_new = s + step * (A.conj().T @ residual)
            
            # Weighted soft thresholding
            s_mag = np.abs(s_new)
            s_phase = np.angle(s_new)
            threshold = step * lambda_reg / (weights + 0.01)  # Add small epsilon
            s_mag_thresh = np.maximum(s_mag - threshold, 0)
            s = s_mag_thresh * np.exp(1j * s_phase)
            
            # Early stopping if converged
            if it > 10 and np.linalg.norm(residual) < 1e-6:
                break
        
        return s
    
    def evaluate(self, u_true, u_recon):
        """Evaluate reconstruction quality."""
        error = u_true - u_recon
        nmse = np.mean(np.abs(error)**2) / np.mean(np.abs(u_true)**2)
        
        # Correlation
        u_true_flat = u_true.flatten()
        u_recon_flat = u_recon.flatten()
        corr = np.corrcoef(np.real(u_true_flat), np.real(u_recon_flat))[0, 1]
        
        return {'NMSE': nmse, 'correlation': corr}


def test_cs_pipeline():
    """Test the complete CS pipeline."""
    print("=" * 70)
    print("CS PIPELINE WITH PHYSICS-INFORMED PRIOR")
    print("=" * 70)
    
    # Generate wavefield
    print("\n[1] Generating wavefield...")
    nx, ny = 80, 40
    dx = 0.0025
    
    G0, G_inf, tau_sigma = 2000, 4000, 0.005
    sim = ShearWave2DZener(nx, ny, dx, rho=1000,
                           G0=G0, G_inf=G_inf, tau_sigma=tau_sigma)
    
    nt = 150
    sx, sy = nx//4, ny//2
    
    wavefield = []
    t_array = []
    
    for n in range(nt):
        t = n * sim.dt
        if n < 80:
            sim.add_source(t, sx, sy, amplitude=2e-5, f0=150, source_type='ricker')
        sim.step()
        wavefield.append(sim.vy[:, ny//2].copy())
        t_array.append(t)
    
    u_true = np.array(wavefield).T
    t_array = np.array(t_array)
    x_array = sim.x
    
    print(f"  Wavefield: {u_true.shape}")
    
    # Initialize pipeline
    print("\n[2] Initializing CS pipeline...")
    pipeline = WorkingCSPipeline(x_array, t_array, 
                                  (G0, G_inf, tau_sigma))
    pipeline.build_fourier_basis()
    
    # Test with different receiver counts
    print("\n[3] Testing reconstruction...")
    
    results = {}
    for n_rec in [4, 8, 16]:
        print(f"\n--- {n_rec} receivers ({n_rec/nx*100:.1f}%) ---")
        
        # Random receivers
        np.random.seed(42)
        rec_idx = np.sort(np.random.choice(nx, n_rec, replace=False))
        
        # Sample
        y_sparse = u_true[rec_idx, :]
        
        # Reconstruct
        u_recon = pipeline.reconstruct_frequency_domain(
            y_sparse, rec_idx, lambda_reg=0.05, n_iter=50
        )
        
        # Evaluate
        metrics = pipeline.evaluate(u_true, u_recon)
        
        results[n_rec] = {
            'u_recon': u_recon,
            'rec_idx': rec_idx,
            'metrics': metrics
        }
        
        print(f"  NMSE: {metrics['NMSE']:.4f}")
        print(f"  Correlation: {metrics['correlation']:.4f}")
    
    # Visualize
    print("\n[4] Visualization...")
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    
    extent = [t_array[0]*1000, t_array[-1]*1000, x_array[0]*100, x_array[-1]*100]
    vmax = np.max(np.abs(u_true))
    
    # Row 0: Reconstructions
    axes[0, 0].imshow(u_true, aspect='auto', origin='lower', extent=extent,
                      cmap='RdBu_r', vmin=-vmax, vmax=vmax)
    axes[0, 0].set_title('True')
    axes[0, 0].set_ylabel('Position (cm)')
    
    for i, n_rec in enumerate([4, 8, 16]):
        u_rec = results[n_rec]['u_recon']
        m = results[n_rec]['metrics']
        axes[0, i+1].imshow(np.real(u_rec), aspect='auto', origin='lower',
                           extent=extent, cmap='RdBu_r', vmin=-vmax, vmax=vmax)
        axes[0, i+1].set_title(f'{n_rec} rec: NMSE={m["NMSE"]:.3f}, r={m["correlation"]:.3f}')
    
    # Row 1: Errors
    axes[1, 0].axis('off')
    for i, n_rec in enumerate([4, 8, 16]):
        u_rec = results[n_rec]['u_recon']
        error = np.abs(u_true - u_rec)
        im = axes[1, i+1].imshow(error, aspect='auto', origin='lower',
                                extent=extent, cmap='hot')
        axes[1, i+1].set_title(f'Error ({n_rec} rec)')
        axes[1, i+1].set_xlabel('Time (ms)')
        if i == 0:
            axes[1, i+1].set_ylabel('Position (cm)')
        plt.colorbar(im, ax=axes[1, i+1])
    
    plt.tight_layout()
    plt.savefig('cs_working_pipeline.png', dpi=150)
    print("  Saved: cs_working_pipeline.png")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("Physics-informed CS pipeline:")
    for n_rec, data in results.items():
        m = data['metrics']
        print(f"  {n_rec:2d} receivers ({n_rec/nx*100:4.1f}%): "
              f"NMSE={m['NMSE']:.4f}, Corr={m['correlation']:.4f}")
    
    print("\nKey features:")
    print("  - Frequency-domain processing")
    print("  - Zener dispersion as weighted prior")
    print("  - Weighted ISTA for each frequency")
    print("  - Joint sparsity via independent frequencies")


if __name__ == "__main__":
    test_cs_pipeline()
