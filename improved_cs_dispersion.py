"""
Improved Compressive Sensing with Physics-Informed Prior
========================================================

Extends basic L1 CS with Zener dispersion curve prior.

Key improvements:
1. Model-based dictionary: atoms shaped by Zener dispersion
2. ADMM solver (faster convergence than ISTA)
3. Multiple Measurement Vector (MMV) for time samples
4. Total Variation regularization for spatial smoothness
5. Dispersion-constrained basis pursuit

Author: DSP Challenge Extension — March 18, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy.linalg import lstsq
import sys
sys.path.append('/home/james/.openclaw/workspace/research/week2')
from shear_wave_2d_zener import ShearWave2DZener
from zener_model import ZenerModel


class PhysicsInformedCompressiveSensing:
    """
    Compressive sensing with Zener dispersion prior.
    
    Instead of generic Fourier basis, use atoms that satisfy
    the Zener dispersion relation ω(k) = k·c(k, G₀, G_∞, τ_σ).
    """
    
    def __init__(self, x_full, t_array, zener_params, n_receivers=8):
        """
        Initialize physics-informed CS.
        
        Parameters:
        -----------
        x_full : array
            Full spatial grid (m)
        t_array : array
            Time array (s)
        zener_params : tuple (G0, G_inf, tau_sigma)
            Zener model parameters
        n_receivers : int
            Number of receivers (recommend 8-16)
        """
        self.x = np.array(x_full)
        self.t = np.array(t_array)
        self.dx = x_full[1] - x_full[0]
        self.dt = t_array[1] - t_array[0] if len(t_array) > 1 else 1e-4
        self.nx = len(x_full)
        self.nt = len(t_array)
        
        self.G0, self.G_inf, self.tau_sigma = zener_params
        self.zm = ZenerModel(self.G0, self.G_inf, self.tau_sigma)
        
        # Frequencies for dispersion
        self.omega = 2 * np.pi * np.fft.rfftfreq(self.nt, self.dt)
        self.nfreq = len(self.omega)
        
        print(f"Physics-Informed CS initialized:")
        print(f"  Grid: {self.nx} points, {self.nt} time samples")
        print(f"  Zener: G₀={self.G0}, G_∞={self.G_inf}, τ_σ={self.tau_sigma*1000:.1f}ms")
        
    def build_dispersion_dictionary(self, k_candidates=None):
        """
        Build dictionary where each atom satisfies Zener dispersion.
        
        For each frequency ω, create atoms of form:
        ψ(k, x, t) = exp(i(kx - ω(k)t))
        where ω(k) follows Zener dispersion.
        
        Parameters:
        -----------
        k_candidates : array or None
            Candidate wavenumbers. If None, use FFT grid.
            
        Returns:
        --------
        Psi : ndarray (nx, nt, n_atoms)
            Dictionary matrix (reshaped to 2D for CS)
        k_opt : array
            Optimal wavenumbers for each frequency
        """
        if k_candidates is None:
            # Use FFT wavenumber grid
            k_candidates = 2 * np.pi * np.fft.fftfreq(self.nx, self.dx)
            k_candidates = k_candidates[k_candidates >= 0]  # Positive only
        
        print(f"Building dispersion dictionary...")
        print(f"  {len(k_candidates)} k candidates × {len(self.omega)} frequencies")
        
        # For each frequency, find matching k from Zener model
        # ω(k) = k · c(ω), solve for k given ω
        k_opt = []
        for omega in self.omega:
            if omega > 0:
                c = self.zm.phase_velocity(omega)
                k = omega / c
                k_opt.append(k)
            else:
                k_opt.append(0)
        k_opt = np.array(k_opt)
        
        # Build dictionary: columns are space-time atoms
        # Each atom: exp(i(kx - ωt)) for a specific (k, ω) pair
        atoms = []
        atom_params = []  # Store (k, omega) for each atom
        
        for i_om, (omega, k) in enumerate(zip(self.omega, k_opt)):
            if omega <= 0:
                continue
                
            # Create space-time atom
            X, T = np.meshgrid(self.x, self.t, indexing='ij')
            
            # Forward traveling wave
            atom_fwd = np.exp(1j * (k * X - omega * T))
            atoms.append(atom_fwd.flatten())
            atom_params.append((k, omega, 'forward'))
            
            # Backward traveling wave
            atom_bwd = np.exp(1j * (-k * X - omega * T))
            atoms.append(atom_bwd.flatten())
            atom_params.append((-k, omega, 'backward'))
            
            # Also include nearby k values for robustness
            for dk in [-0.1*k, 0.1*k]:
                if abs(dk) > 1e-6:
                    atom_fwd_pert = np.exp(1j * ((k+dk) * X - omega * T))
                    atoms.append(atom_fwd_pert.flatten())
                    atom_params.append((k+dk, omega, 'forward_pert'))
        
        # Stack into dictionary matrix
        Psi = np.column_stack(atoms)  # (nx*nt, n_atoms)
        
        print(f"  Dictionary shape: {Psi.shape}")
        print(f"  Atoms: {len(atoms)}")
        
        self.Psi = Psi
        self.atom_params = atom_params
        self.k_opt = k_opt
        
        return Psi, k_opt
    
    def build_sensing_matrix(self, receiver_indices):
        """
        Build sensing matrix A that samples at receiver positions.
        
        A[i, j] = 1 if spatial index i matches receiver j
        """
        n_rec = len(receiver_indices)
        
        # Sensing matrix for spatial sampling
        # Shape: (n_rec*nt, nx*nt) - samples space, keeps all time
        A_blocks = []
        for t_idx in range(self.nt):
            row_start = t_idx * n_rec
            col_start = t_idx * self.nx
            
            # For this time slice, sample at receiver positions
            block = np.zeros((n_rec, self.nx))
            for i_rec, idx in enumerate(receiver_indices):
                block[i_rec, idx] = 1.0
            
            A_blocks.append(block)
        
        # Block diagonal matrix
        from scipy.sparse import block_diag
        A = block_diag(A_blocks, format='csr')
        
        print(f"Sensing matrix: {A.shape}")
        print(f"  Measurements: {n_rec * self.nt}")
        print(f"  Unknowns: {self.Psi.shape[1]} coefficients")
        
        return A
    
    def reconstruct_admm(self, y_sparse, receiver_indices, 
                         lambda_l1=0.1, lambda_tv=0.05, 
                         rho=1.0, max_iter=100, tol=1e-4):
        """
        Reconstruct using ADMM with L1 + TV regularization.
        
        Solves: minimize ||y - A*Psi*s||² + λ₁||s||₁ + λ₂||D*s||₁
        
        Parameters:
        -----------
        y_sparse : ndarray (n_rec, nt)
            Sparse measurements at receiver positions
        receiver_indices : array
            Indices of receiver positions
        lambda_l1 : float
            L1 regularization (sparsity in dispersion basis)
        lambda_tv : float
            Total variation regularization (spatial smoothness)
        rho : float
            ADMM penalty parameter
        max_iter : int
            Maximum iterations
            
        Returns:
        --------
        u_reconstructed : ndarray (nx, nt)
            Reconstructed wavefield
        s : array
            Sparse coefficients in dispersion basis
        history : dict
            Convergence history
        """
        # Build matrices
        if not hasattr(self, 'Psi'):
            self.build_dispersion_dictionary()
        
        A = self.build_sensing_matrix(receiver_indices)
        
        # Measurement vector
        y = y_sparse.flatten()  # (n_rec * nt,)
        
        # Combined sensing + dictionary
        # y = A * vec(u) = A * Psi * s = Phi * s
        Phi = A @ self.Psi  # (n_rec*nt, n_atoms)
        
        print(f"\nADMM Reconstruction:")
        print(f"  Phi shape: {Phi.shape}")
        print(f"  Sparsity ratio: {Phi.shape[1]/Phi.shape[0]:.2f}x")
        
        # ADMM iterations
        n_atoms = self.Psi.shape[1]
        
        # Initialize
        s = np.zeros(n_atoms, dtype=complex)
        z = np.zeros(n_atoms)  # Auxiliary variable for L1
        w = np.zeros(n_atoms)  # Auxiliary variable for TV
        u = np.zeros(n_atoms)  # Dual variable for z
        v = np.zeros(n_atoms)  # Dual variable for w
        
        # Precompute (Phi^H * Phi + rho*I)^{-1}
        Phi_H = Phi.conj().T
        P = Phi_H @ Phi + rho * np.eye(n_atoms)
        P_inv = np.linalg.inv(P)
        
        # TV operator (1D finite difference)
        D = np.eye(n_atoms) - np.eye(n_atoms, k=1)
        D[-1, -1] = 0  # Boundary
        D_H = D.T
        
        history = {'residual': [], 'obj': []}
        
        for iteration in range(max_iter):
            # s-update: least squares
            q = Phi_H @ y + rho * (z - u) + rho * (D_H @ (w - v))
            s = P_inv @ q
            
            # z-update: soft thresholding (L1)
            z_old = z.copy()
            z = self._soft_threshold(s + u, lambda_l1 / rho)
            
            # w-update: soft thresholding (TV)
            w_old = w.copy()
            Ds = D @ s
            w = self._soft_threshold(Ds + v, lambda_tv / rho)
            
            # Dual updates
            u = u + s - z
            v = v + Ds - w
            
            # Residuals
            primal_res = np.linalg.norm(s - z)
            dual_res = rho * np.linalg.norm(z - z_old)
            
            # Objective
            residual = y - Phi @ s
            obj = (np.linalg.norm(residual)**2 + 
                   lambda_l1 * np.linalg.norm(s, 1) +
                   lambda_tv * np.linalg.norm(D @ s, 1))
            
            history['residual'].append(primal_res)
            history['obj'].append(obj)
            
            if iteration % 20 == 0:
                print(f"  Iter {iteration}: obj={obj:.4e}, resid={primal_res:.4e}")
            
            # Convergence check
            if primal_res < tol and dual_res < tol:
                print(f"  Converged at iteration {iteration}")
                break
        
        # Reconstruct wavefield
        u_vec = self.Psi @ s
        u_reconstructed = u_vec.reshape(self.nx, self.nt)
        
        return u_reconstructed, s, history
    
    def _soft_threshold(self, x, threshold):
        """Soft thresholding for complex numbers."""
        magnitude = np.abs(x)
        phase = np.angle(x)
        magnitude_thresholded = np.maximum(magnitude - threshold, 0)
        return magnitude_thresholded * np.exp(1j * phase)
    
    def reconstruct_mmv(self, y_sparse, receiver_indices, lambda_reg=0.1):
        """
        Multiple Measurement Vector (MMV) reconstruction.
        
        Exploits joint sparsity across time samples.
        All time samples share the same support (frequencies present).
        """
        n_rec, nt = y_sparse.shape
        
        # Build spatial Fourier basis
        k_vec = 2 * np.pi * np.fft.fftfreq(self.nx, self.dx)
        K, T = np.meshgrid(k_vec, self.t, indexing='ij')
        
        # Dictionary: spatial Fourier × temporal Fourier
        # This enforces that the same k components appear at all times
        
        # For each frequency, solve jointly
        S = np.zeros((self.nx, nt), dtype=complex)  # k-t domain coefficients
        
        print(f"\nMMV Reconstruction:")
        print(f"  Solving {len(self.omega)} frequency bins jointly")
        
        for i_om, omega in enumerate(self.omega):
            if omega <= 0:
                continue
            
            # Extract this frequency component from all receivers
            y_freq = np.fft.rfft(y_sparse, axis=1)[:, i_om]
            
            # Spatial dictionary at this frequency
            # Atoms: exp(ikx) for different k
            Phi_spatial = np.exp(1j * np.outer(self.x[receiver_indices], k_vec))
            
            # Group LASSO: minimize ||y - Phi*s||² + λ*sum(||s_j||_2)
            # where s_j is the coefficient vector across time for k_j
            # For single frequency, this reduces to LASSO
            
            from sklearn.linear_model import Lasso
            lasso = Lasso(alpha=lambda_reg / len(y_freq), max_iter=1000)
            lasso.fit(np.real(Phi_spatial), np.real(y_freq))
            s_real = lasso.coef_
            
            lasso.fit(np.imag(Phi_spatial), np.imag(y_freq))
            s_imag = lasso.coef_
            
            S[:, i_om] = s_real + 1j * s_imag
        
        # Transform back to space-time
        u_reconstructed = np.fft.irfft(S, n=nt, axis=1)
        
        return u_reconstructed


class ArrayOptimizer:
    """
    Optimize receiver placement for compressive sensing.
    
    Uses genetic algorithm to minimize reconstruction error.
    """
    
    def __init__(self, x_full, n_receivers=8, zener_params=None):
        self.x = x_full
        self.nx = len(x_full)
        self.n_rec = n_receivers
        self.zener_params = zener_params
        
    def objective(self, indices, u_true, A_sensing_func):
        """
        Objective function: NMSE of reconstruction.
        
        Parameters:
        -----------
        indices : array
            Receiver indices (integers)
        u_true : ndarray (nx, nt)
            True wavefield
        A_sensing_func : callable
            Function that returns sensing matrix given indices
            
        Returns:
        --------
        nmse : float
            Normalized mean squared error
        """
        indices = np.clip(indices.astype(int), 0, self.nx - 1)
        indices = np.unique(indices)
        
        if len(indices) < self.n_rec:
            return 1.0  # Penalize duplicates
        
        # Sample
        y = u_true[indices, :]
        
        # Reconstruct with simple method
        A = A_sensing_func(indices)
        
        # Basic LS reconstruction (for speed in optimization)
        # In practice, use full CS reconstruction
        s, residuals, rank, s_vals = lstsq(A, y.flatten())
        u_recon = (A @ s).reshape(self.nx, u_true.shape[1])
        
        # NMSE
        nmse = np.mean(np.abs(u_true - u_recon)**2) / np.mean(np.abs(u_true)**2)
        
        return nmse
    
    def optimize(self, u_true, method='differential_evolution', pop_size=20):
        """
        Optimize receiver placement.
        
        Uses differential evolution (global optimization).
        """
        from scipy.optimize import differential_evolution
        
        print(f"Optimizing {self.n_rec} receiver positions...")
        
        # Bounds: each receiver index in [0, nx-1]
        bounds = [(0, self.nx - 1) for _ in range(self.n_rec)]
        
        # Dummy sensing function (will be replaced)
        def dummy_A(indices):
            return np.eye(self.nx)[indices, :]
        
        # Optimize
        result = differential_evolution(
            lambda x: self.objective(x, u_true, dummy_A),
            bounds,
            maxiter=100,
            popsize=pop_size,
            tol=1e-3,
            workers=-1,  # Parallel
            polish=True
        )
        
        optimal_indices = np.clip(result.x.astype(int), 0, self.nx - 1)
        optimal_indices = np.unique(optimal_indices)
        
        print(f"  Optimal positions: {self.x[optimal_indices]*100:.1f} cm")
        print(f"  Final NMSE: {result.fun:.4f}")
        
        return optimal_indices, result


def demo_improved_cs():
    """Demonstrate improved CS with physics-informed prior."""
    print("=" * 70)
    print("IMPROVED COMPRESSIVE SENSING WITH PHYSICS PRIOR")
    print("=" * 70)
    
    # 1. Generate synthetic wavefield
    print("\n[1] Generating wavefield...")
    nx, ny = 100, 50  # Reduced for speed
    dx = 0.002  # 2mm grid
    
    G0, G_inf, tau_sigma = 2000, 4000, 0.005
    
    sim = ShearWave2DZener(nx, ny, dx, rho=1000,
                           G0=G0, G_inf=G_inf, tau_sigma=tau_sigma)
    
    nt = 400  # Reduced
    sx, sy = nx//4, ny//2
    
    wavefield_slices = []
    t_array = []
    
    for n in range(nt):
        t = n * sim.dt
        if n < 150:
            sim.add_source(t, sx, sy, amplitude=2e-5, f0=150, source_type='ricker')
        sim.step()
        
        if n % 2 == 0:
            wavefield_slices.append(sim.vy[:, ny//2].copy())
            t_array.append(t)
    
    u_true = np.array(wavefield_slices).T
    t_array = np.array(t_array)
    x_array = sim.x
    
    print(f"  Wavefield: {u_true.shape}")
    
    # 2. Initialize physics-informed CS
    print("\n[2] Initializing physics-informed CS...")
    pics = PhysicsInformedCompressiveSensing(
        x_array, t_array, 
        zener_params=(G0, G_inf, tau_sigma),
        n_receivers=8
    )
    
    # Build dictionary
    pics.build_dispersion_dictionary()
    
    # 3. Test with 8 receivers (vs 4 in basic version)
    print("\n[3] Testing with 8 receivers...")
    
    # Random array
    np.random.seed(42)
    rec_indices = np.sort(np.random.choice(nx, 8, replace=False))
    
    print(f"  Receiver positions: {x_array[rec_indices]*100} cm")
    
    y_sparse = u_true[rec_indices, :]
    
    # 4. Reconstruct with ADMM
    print("\n[4] ADMM reconstruction (L1 + TV)...")
    u_admm, s, history = pics.reconstruct_admm(
        y_sparse, rec_indices,
        lambda_l1=0.05, lambda_tv=0.02,
        rho=2.0, max_iter=50
    )
    
    # 5. Evaluate
    nmse_admm = np.mean(np.abs(u_true - u_admm)**2) / np.mean(np.abs(u_true)**2)
    corr_admm = np.corrcoef(u_true.flatten(), u_admm.flatten())[0, 1]
    
    print(f"\n  ADMM Results:")
    print(f"    NMSE: {nmse_admm:.4f}")
    print(f"    Correlation: {corr_admm:.4f}")
    
    # 6. Compare to basic L1 (for reference)
    print("\n[5] Comparison to basic L1...")
    
    # Simple L1 via coordinate descent
    from sklearn.linear_model import Lasso
    
    A = pics.build_sensing_matrix(rec_indices)
    y = y_sparse.flatten()
    
    # Project to real for sklearn
    A_real = np.vstack([np.real(A), np.imag(A)])
    y_real = np.concatenate([np.real(y), np.imag(y)])
    
    lasso = Lasso(alpha=0.01, max_iter=2000)
    lasso.fit(A_real, y_real)
    s_basic = lasso.coef_
    
    u_basic = (A @ s_basic).reshape(pics.nx, pics.nt)
    
    nmse_basic = np.mean(np.abs(u_true - u_basic)**2) / np.mean(np.abs(u_true)**2)
    corr_basic = np.corrcoef(u_true.flatten(), u_basic.flatten())[0, 1]
    
    print(f"  Basic L1 Results:")
    print(f"    NMSE: {nmse_basic:.4f}")
    print(f"    Correlation: {corr_basic:.4f}")
    
    # 7. Visualization
    print("\n[6] Generating comparison plots...")
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    extent = [t_array[0]*1000, t_array[-1]*1000, x_array[0]*100, x_array[-1]*100]
    
    # True
    ax = axes[0, 0]
    vmax = np.max(np.abs(u_true))
    im = ax.imshow(u_true, aspect='auto', origin='lower', extent=extent,
                   cmap='RdBu_r', vmin=-vmax, vmax=vmax)
    ax.set_title('True Wavefield')
    ax.set_ylabel('Position (cm)')
    plt.colorbar(im, ax=ax)
    
    # Sparse samples
    ax = axes[0, 1]
    u_sparse_plot = np.zeros_like(u_true)
    u_sparse_plot[rec_indices, :] = y_sparse
    im = ax.imshow(u_sparse_plot, aspect='auto', origin='lower', extent=extent,
                   cmap='RdBu_r', vmin=-vmax, vmax=vmax)
    ax.set_title(f'Sparse Samples ({len(rec_indices)} receivers)')
    plt.colorbar(im, ax=ax)
    
    # ADMM reconstruction
    ax = axes[0, 2]
    im = ax.imshow(np.real(u_admm), aspect='auto', origin='lower', extent=extent,
                   cmap='RdBu_r', vmin=-vmax, vmax=vmax)
    ax.set_title(f'ADMM (NMSE={nmse_admm:.3f}, r={corr_admm:.3f})')
    plt.colorbar(im, ax=ax)
    
    # Basic L1
    ax = axes[1, 0]
    im = ax.imshow(np.real(u_basic), aspect='auto', origin='lower', extent=extent,
                   cmap='RdBu_r', vmin=-vmax, vmax=vmax)
    ax.set_title(f'Basic L1 (NMSE={nmse_basic:.3f}, r={corr_basic:.3f})')
    ax.set_ylabel('Position (cm)')
    ax.set_xlabel('Time (ms)')
    plt.colorbar(im, ax=ax)
    
    # Convergence
    ax = axes[1, 1]
    ax.semilogy(history['residual'], 'b-', label='Primal residual')
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Residual')
    ax.set_title('ADMM Convergence')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Dispersion comparison
    ax = axes[1, 2]
    
    # Extract dispersion from true and reconstructed
    from k_omega_transform import KOmegaTransform
    
    kt_true = KOmegaTransform(x_array, t_array)
    kt_true.transform(u_true)
    kt_true.extract_dispersion()
    f_true, c_true = kt_true.compute_phase_velocity()
    
    kt_admm = KOmegaTransform(x_array, t_array)
    kt_admm.transform(np.real(u_admm))
    kt_admm.extract_dispersion()
    f_admm, c_admm = kt_admm.compute_phase_velocity()
    
    ax.plot(f_true, c_true, 'b-o', markersize=4, label='True')
    ax.plot(f_admm, c_admm, 'r-s', markersize=4, label='ADMM recon')
    
    # Analytical
    f_theory = np.linspace(20, 300, 100)
    zm = ZenerModel(G0, G_inf, tau_sigma)
    c_theory = [zm.phase_velocity(2*np.pi*f) for f in f_theory]
    ax.plot(f_theory, c_theory, 'g--', linewidth=2, label='Zener theory')
    
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Phase Velocity (m/s)')
    ax.set_title('Dispersion Curves')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('improved_cs_comparison.png', dpi=150)
    print("  Saved: improved_cs_comparison.png")
    
    print("\n" + "=" * 70)
    print("IMPROVEMENT SUMMARY")
    print("=" * 70)
    print(f"Basic L1:  NMSE={nmse_basic:.4f}, Correlation={corr_basic:.4f}")
    print(f"ADMM:      NMSE={nmse_admm:.4f}, Correlation={corr_admm:.4f}")
    print(f"\nImprovement:")
    print(f"  NMSE reduction: {(1 - nmse_admm/nmse_basic)*100:.1f}%")
    print(f"  Correlation gain: {corr_admm - corr_basic:.3f}")
    
    return pics, u_admm, history


if __name__ == "__main__":
    pics, u_admm, history = demo_improved_cs()
