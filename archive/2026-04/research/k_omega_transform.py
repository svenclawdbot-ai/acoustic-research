"""
k-ω Transform for Shear Wave Dispersion Extraction
===================================================

Implementation of wavenumber-frequency domain analysis for 
viscoelastic shear wave dispersion characterization.

Features:
- 2D FFT-based k-ω transform
- Dispersion curve extraction via peak tracking
- Sparse sampling simulation (2-4 receivers)
- Compressive sensing reconstruction (L1 minimization)
- Comparison to analytical Zener model

Uses: research/week2/shear_wave_2d_zener.py (Zener simulator)

Author: DSP Challenge — March 18, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy.interpolate import interp1d
import sys
sys.path.append('/home/james/.openclaw/workspace/research/week2')
from shear_wave_2d_zener import ShearWave2DZener


class KOmegaTransform:
    """
    k-ω (wavenumber-frequency) transform for dispersion extraction.
    
    Transforms spatiotemporal wavefield u(x,t) to k-ω domain U(k,ω)
    via 2D FFT. Dispersion relation ω(k) appears as peaks in |U(k,ω)|.
    """
    
    def __init__(self, x, t):
        """
        Initialize k-ω transform.
        
        Parameters:
        -----------
        x : array_like
            Spatial coordinates (m)
        t : array_like  
            Time coordinates (s)
        """
        self.x = np.array(x)
        self.t = np.array(t)
        self.dx = x[1] - x[0]
        self.dt = t[1] - t[0]
        self.nx = len(x)
        self.nt = len(t)
        
        # Frequency and wavenumber axes
        self.omega = 2 * np.pi * np.fft.fftfreq(self.nt, self.dt)
        self.k = 2 * np.pi * np.fft.fftfreq(self.nx, self.dx)
        
        # Shift for visualization
        self.omega_shift = np.fft.fftshift(self.omega)
        self.k_shift = np.fft.fftshift(self.k)
        
    def transform(self, u_xt):
        """
        Compute k-ω transform.
        
        Parameters:
        -----------
        u_xt : ndarray (nx, nt)
            Spatiotemporal wavefield u(x,t)
            
        Returns:
        --------
        U_kw : ndarray (nx, nt)
            k-ω spectrum U(k,ω)
        """
        # 2D FFT: transform both dimensions
        U_kw = np.fft.fft2(u_xt)
        
        # Shift zero frequency to center
        self.U_kw = np.fft.fftshift(U_kw)
        self.magnitude = np.abs(self.U_kw)
        
        return self.U_kw
    
    def extract_dispersion(self, k_range=None, omega_range=None, 
                          threshold=0.1, smoothing=True):
        """
        Extract dispersion curve ω(k) from k-ω spectrum.
        
        Parameters:
        -----------
        k_range : tuple (k_min, k_max)
            Wavenumber range to analyze (rad/m)
        omega_range : tuple (omega_min, omega_max)
            Frequency range to analyze (rad/s)
        threshold : float
            Peak detection threshold (fraction of max)
        smoothing : bool
            Apply Savitzky-Golay smoothing to curve
            
        Returns:
        --------
        k_disp : array
            Wavenumbers where dispersion curve extracted
        omega_disp : array
            Corresponding frequencies (dispersion curve)
        """
        # Select relevant region
        if k_range is None:
            k_min, k_max = -np.max(np.abs(self.k)), np.max(np.abs(self.k))
        else:
            k_min, k_max = k_range
            
        if omega_range is None:
            omega_min, omega_max = 0, np.max(self.omega)
        else:
            omega_min, omega_max = omega_range
        
        # Find indices
        k_idx = (self.k_shift >= k_min) & (self.k_shift <= k_max)
        omega_idx = (self.omega_shift >= omega_min) & (self.omega_shift <= omega_max)
        
        k_sel = self.k_shift[k_idx]
        omega_sel = self.omega_shift[omega_idx]
        mag_sel = self.magnitude[np.ix_(k_idx, omega_idx)]
        
        # Normalize
        mag_norm = mag_sel / np.max(mag_sel)
        
        # Extract peak for each k (dispersion branch)
        omega_disp = []
        k_disp = []
        
        for i, k_val in enumerate(k_sel):
            # Find peaks above threshold
            profile = mag_norm[i, :]
            peak_idx = np.where(profile > threshold * np.max(profile))[0]
            
            if len(peak_idx) > 0:
                # Take highest peak
                max_peak_idx = peak_idx[np.argmax(profile[peak_idx])]
                omega_disp.append(omega_sel[max_peak_idx])
                k_disp.append(k_val)
        
        k_disp = np.array(k_disp)
        omega_disp = np.array(omega_disp)
        
        # Sort by k
        sort_idx = np.argsort(k_disp)
        k_disp = k_disp[sort_idx]
        omega_disp = omega_disp[sort_idx]
        
        # Smoothing
        if smoothing and len(k_disp) > 5:
            from scipy.signal import savgol_filter
            window = min(5, len(k_disp) // 2 * 2 + 1)
            if window >= 3:
                omega_disp = savgol_filter(omega_disp, window, 2)
        
        self.k_disp = k_disp
        self.omega_disp = omega_disp
        
        return k_disp, omega_disp
    
    def compute_phase_velocity(self):
        """Compute phase velocity c_p = ω/k from dispersion curve."""
        if not hasattr(self, 'k_disp'):
            raise ValueError("Run extract_dispersion() first")
        
        # Avoid division by zero
        mask = np.abs(self.k_disp) > 1e-6
        k_valid = self.k_disp[mask]
        omega_valid = self.omega_disp[mask]
        
        c_p = omega_valid / k_valid
        f_valid = omega_valid / (2 * np.pi)
        
        return f_valid, np.abs(c_p)
    
    def plot_spectrum(self, figsize=(12, 10), save_path=None):
        """Visualize k-ω spectrum with extracted dispersion."""
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        
        # Full spectrum
        ax = axes[0, 0]
        extent = [self.omega_shift[0]/(2*np.pi), self.omega_shift[-1]/(2*np.pi),
                  self.k_shift[0], self.k_shift[-1]]
        im = ax.imshow(self.magnitude, aspect='auto', origin='lower',
                       extent=extent, cmap='hot')
        ax.set_xlabel('Frequency f (Hz)')
        ax.set_ylabel('Wavenumber k (rad/m)')
        ax.set_title('k-ω Spectrum |U(k,ω)|')
        plt.colorbar(im, ax=ax, label='Magnitude')
        
        # Zoom on positive quadrant
        ax = axes[0, 1]
        # Select positive k and omega
        k_pos = self.k_shift > 0
        omega_pos = self.omega_shift > 0
        mag_pos = self.magnitude[np.ix_(k_pos, omega_pos)]
        extent_pos = [0, self.omega_shift[-1]/(2*np.pi),
                      0, self.k_shift[-1]]
        im = ax.imshow(mag_pos, aspect='auto', origin='lower',
                       extent=extent_pos, cmap='hot')
        
        # Overlay dispersion curve if available
        if hasattr(self, 'k_disp'):
            ax.plot(self.omega_disp/(2*np.pi), np.abs(self.k_disp), 'c--', 
                   linewidth=2, label='Extracted dispersion')
            ax.legend()
        
        ax.set_xlabel('Frequency f (Hz)')
        ax.set_ylabel('|k| (rad/m)')
        ax.set_title('Positive Quadrant with Dispersion')
        plt.colorbar(im, ax=ax, label='Magnitude')
        
        # Dispersion curve ω(k)
        ax = axes[1, 0]
        if hasattr(self, 'k_disp'):
            ax.plot(self.k_disp, self.omega_disp/(2*np.pi), 'b-o', markersize=4)
            ax.set_xlabel('Wavenumber k (rad/m)')
            ax.set_ylabel('Frequency f (Hz)')
            ax.set_title('Dispersion Curve f(k)')
            ax.grid(True, alpha=0.3)
        
        # Phase velocity
        ax = axes[1, 1]
        f, c_p = self.compute_phase_velocity()
        ax.plot(f, c_p, 'r-s', markersize=4, label='Extracted')
        ax.set_xlabel('Frequency f (Hz)')
        ax.set_ylabel('Phase Velocity c_p (m/s)')
        ax.set_title('Phase Velocity Dispersion')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved: {save_path}")
        
        return fig


class SparseSamplingArray:
    """
    Sparse receiver array for wavefield sampling.
    
    Simulates N receivers at arbitrary positions for compressed sensing.
    """
    
    def __init__(self, x_full, n_receivers=4, array_type='random'):
        """
        Initialize sparse array.
        
        Parameters:
        -----------
        x_full : array
            Full spatial grid (m)
        n_receivers : int
            Number of receivers (2, 3, or 4)
        array_type : str
            'uniform', 'random', 'optimized', 'endfire'
        """
        self.x_full = x_full
        self.nx_full = len(x_full)
        self.n_receivers = n_receivers
        self.array_type = array_type
        
        # Select receiver positions
        self.receiver_indices = self._select_positions(array_type)
        self.x_sparse = x_full[self.receiver_indices]
        
        print(f"Sparse array: {n_receivers} receivers ({array_type})")
        print(f"  Positions: {self.x_sparse*100} cm")
        print(f"  Compression: {n_receivers}/{len(x_full)} = {n_receivers/len(x_full)*100:.1f}%")
    
    def _select_positions(self, array_type):
        """Select receiver positions based on array type."""
        nx = self.nx_full
        
        if array_type == 'uniform':
            # Evenly spaced
            idx = np.linspace(0, nx-1, self.n_receivers, dtype=int)
        
        elif array_type == 'random':
            # Random positions with minimum spacing
            np.random.seed(42)  # Reproducible
            min_spacing = nx // (2 * self.n_receivers)
            idx = []
            while len(idx) < self.n_receivers:
                i = np.random.randint(0, nx)
                if all(abs(i - j) >= min_spacing for j in idx):
                    idx.append(i)
            idx = np.array(sorted(idx))
        
        elif array_type == 'endfire':
            # Clustered at ends for maximum baseline
            n_per_end = self.n_receivers // 2
            idx = np.concatenate([
                np.linspace(0, nx//4, n_per_end, dtype=int),
                np.linspace(3*nx//4, nx-1, self.n_receivers - n_per_end, dtype=int)
            ])
        
        elif array_type == 'optimized':
            # Log-spaced for better frequency coverage
            log_pos = np.logspace(0, np.log10(nx), self.n_receivers)
            idx = np.unique(np.round(log_pos).astype(int))
            idx = np.clip(idx, 0, nx-1)
            if len(idx) < self.n_receivers:
                # Fill in with random
                extra = np.random.choice(
                    [i for i in range(nx) if i not in idx],
                    self.n_receivers - len(idx),
                    replace=False
                )
                idx = np.sort(np.concatenate([idx, extra]))
        
        else:
            raise ValueError(f"Unknown array type: {array_type}")
        
        return idx
    
    def sample(self, u_full):
        """
        Sample full wavefield at receiver positions.
        
        Parameters:
        -----------
        u_full : ndarray (nx, nt)
            Full wavefield
            
        Returns:
        --------
        u_sparse : ndarray (n_receivers, nt)
            Sampled wavefield
        """
        return u_full[self.receiver_indices, :]
    
    def plot_array_geometry(self, ax=None):
        """Plot receiver positions."""
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 2))
        
        ax.scatter(self.x_full, np.zeros_like(self.x_full), 
                  c='lightgray', s=10, label='Full grid')
        ax.scatter(self.x_sparse, np.zeros_like(self.x_sparse),
                  c='red', s=100, marker='v', label='Receivers', zorder=5)
        ax.set_xlabel('Position x (m)')
        ax.set_title(f'Sparse Array Geometry ({self.array_type})')
        ax.legend()
        ax.set_yticks([])
        ax.grid(True, alpha=0.3)
        
        return ax


class CompressiveSensingReconstruction:
    """
    Compressive sensing for wavefield reconstruction from sparse samples.
    
    Uses L1 minimization with dispersion curve prior.
    """
    
    def __init__(self, sparse_array, k_omega_transform):
        """
        Initialize CS reconstruction.
        
        Parameters:
        -----------
        sparse_array : SparseSamplingArray
            Sparse receiver configuration
        k_omega_transform : KOmegaTransform
            k-ω transform object (for basis)
        """
        self.sparse_array = sparse_array
        self.kt = k_omega_transform
        
    def build_sensing_matrix(self):
        """
        Build sensing matrix A for y = A*x.
        
        y: sparse measurements (n_receivers, nt)
        x: full wavefield (nx, nt)
        A: subsampled Fourier matrix
        """
        nx = self.sparse_array.nx_full
        n_rec = self.sparse_array.n_receivers
        
        # Fourier basis matrix (IDFT)
        k = self.kt.k
        x = self.kt.x
        
        # Sensing matrix: subsampled IDFT
        # A[i,j] = exp(1j * k[j] * x[receiver_i]) / nx
        self.A = np.zeros((n_rec, nx), dtype=complex)
        for i, idx in enumerate(self.sparse_array.receiver_indices):
            self.A[i, :] = np.exp(1j * k * x[idx]) / nx
        
        return self.A
    
    def reconstruct_l1(self, y_sparse, lambda_reg=0.1, max_iter=100):
        """
        Reconstruct wavefield via L1 minimization.
        
        minimize: ||y - A*x||_2^2 + lambda * ||x||_1
        
        Parameters:
        -----------
        y_sparse : ndarray (n_receivers, nt)
            Sparse measurements
        lambda_reg : float
            L1 regularization parameter
        max_iter : int
            Maximum iterations
            
        Returns:
        --------
        u_reconstructed : ndarray (nx, nt)
            Reconstructed wavefield
        """
        n_rec, nt = y_sparse.shape
        nx = self.sparse_array.nx_full
        
        # Build sensing matrix
        A = self.build_sensing_matrix()
        
        # Reconstruct each time slice (or use full 2D)
        # For efficiency, work in frequency domain
        u_reconstructed = np.zeros((nx, nt), dtype=complex)
        
        print(f"Running L1 reconstruction ({n_rec} measurements, {nx} unknowns)...")
        
        # Process each frequency component
        for it in range(nt):
            y = y_sparse[:, it]
            
            # L1 minimization using ISTA (Iterative Soft Thresholding)
            x_est = self._ista(A, y, lambda_reg, max_iter)
            
            u_reconstructed[:, it] = x_est
            
            if it % 50 == 0:
                print(f"  Time step {it}/{nt}")
        
        return np.real(u_reconstructed)
    
    def _ista(self, A, y, lambda_reg, max_iter):
        """
        Iterative Soft Thresholding Algorithm for L1 minimization.
        
        Solves: min ||y - A*x||^2 + lambda*||x||_1
        """
        # Step size (Lipschitz constant)
        L = np.linalg.norm(A @ A.conj().T, 2)
        step = 1.0 / L
        
        # Initialize
        x = np.zeros(A.shape[1], dtype=complex)
        
        for _ in range(max_iter):
            # Gradient step
            residual = y - A @ x
            x = x + step * (A.conj().T @ residual)
            
            # Soft thresholding (proximal operator for L1)
            x = self._soft_threshold(x, step * lambda_reg)
        
        return x
    
    def _soft_threshold(self, x, threshold):
        """Soft thresholding operator."""
        magnitude = np.abs(x)
        phase = np.angle(x)
        magnitude_thresholded = np.maximum(magnitude - threshold, 0)
        return magnitude_thresholded * np.exp(1j * phase)
    
    def evaluate_quality(self, u_true, u_reconstructed):
        """
        Evaluate reconstruction quality.
        
        Returns:
        --------
        metrics : dict
            NMSE, correlation, etc.
        """
        error = u_true - u_reconstructed
        mse = np.mean(np.abs(error)**2)
        nmse = mse / np.mean(np.abs(u_true)**2)
        
        # Correlation
        corr = np.corrcoef(u_true.flatten(), u_reconstructed.flatten())[0, 1]
        
        return {
            'NMSE': nmse,
            'correlation': corr,
            'RMSE': np.sqrt(mse)
        }


def demo_k_omega_transform():
    """Demonstrate full k-ω pipeline."""
    print("=" * 70)
    print("k-ω TRANSFORM FOR SHEAR WAVE DISPERSION EXTRACTION")
    print("=" * 70)
    
    # 1. Generate wavefield with Zener simulator
    print("\n[1] Generating synthetic wavefield...")
    nx, ny = 200, 100  # 2D slice for line receivers
    dx = 0.001  # 1 mm grid
    
    # Zener parameters
    G0 = 2000  # Pa (soft tissue)
    G_inf = 4000  # Pa
    tau_sigma = 0.005  # s
    
    sim = ShearWave2DZener(nx, ny, dx, rho=1000,
                           G0=G0, G_inf=G_inf, tau_sigma=tau_sigma)
    
    # Run simulation and extract line profile
    nt = 1000
    sx, sy = nx//4, ny//2
    
    wavefield_slices = []
    t_array = []
    
    for n in range(nt):
        t = n * sim.dt
        # Multi-frequency source
        if n < 150:
            sim.add_source(t, sx, sy, amplitude=2e-5, f0=150, source_type='ricker')
        sim.step()
        
        # Extract center line (y = ny//2)
        if n % 2 == 0:  # Subsample time for efficiency
            wavefield_slices.append(sim.vy[:, ny//2].copy())
            t_array.append(t)
    
    u_xt = np.array(wavefield_slices).T  # (nx, nt)
    t_array = np.array(t_array)
    x_array = sim.x
    
    print(f"  Wavefield shape: {u_xt.shape}")
    print(f"  Spatial extent: {x_array[0]*100:.1f} to {x_array[-1]*100:.1f} cm")
    print(f"  Time extent: {t_array[0]*1000:.1f} to {t_array[-1]*1000:.1f} ms")
    
    # 2. Full k-ω transform
    print("\n[2] Computing k-ω transform...")
    kt = KOmegaTransform(x_array, t_array)
    kt.transform(u_xt)
    
    # 3. Extract dispersion
    print("\n[3] Extracting dispersion curve...")
    k_range = (10, 300)  # rad/m
    omega_range = (2*np.pi*20, 2*np.pi*300)  # 20-300 Hz
    kt.extract_dispersion(k_range=k_range, omega_range=omega_range)
    
    f_disp, c_disp = kt.compute_phase_velocity()
    print(f"  Extracted {len(f_disp)} dispersion points")
    print(f"  Phase velocity range: {c_disp.min():.2f} to {c_disp.max():.2f} m/s")
    
    # 4. Sparse sampling comparison
    print("\n[4] Testing sparse sampling arrays...")
    array_types = ['uniform', 'random', 'endfire', 'optimized']
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    axes = axes.flatten()
    
    results = {}
    
    for idx, array_type in enumerate(array_types):
        print(f"\n  Array type: {array_type}")
        
        # Create sparse array
        sparse = SparseSamplingArray(x_array, n_receivers=4, array_type=array_type)
        
        # Sample
        u_sparse = sparse.sample(u_xt)
        
        # k-ω on sparse data (interpolated)
        # For fair comparison, use same k-ω transform but with zero-filled data
        u_zero_filled = np.zeros_like(u_xt)
        u_zero_filled[sparse.receiver_indices, :] = u_sparse
        
        kt_sparse = KOmegaTransform(x_array, t_array)
        kt_sparse.transform(u_zero_filled)
        
        # Plot geometry
        ax = axes[idx]
        sparse.plot_array_geometry(ax=ax)
        ax.set_title(f'{array_type.capitalize()}: {sparse.n_receivers} receivers')
        
        results[array_type] = {
            'sparse': sparse,
            'u_sparse': u_sparse,
            'kt': kt_sparse
        }
    
    plt.tight_layout()
    plt.savefig('sparse_array_comparison.png', dpi=150)
    print("\n  Saved: sparse_array_comparison.png")
    
    # 5. Compressive sensing reconstruction (one example)
    print("\n[5] Compressive sensing reconstruction...")
    sparse = SparseSamplingArray(x_array, n_receivers=4, array_type='random')
    u_sparse = sparse.sample(u_xt)
    
    cs = CompressiveSensingReconstruction(sparse, kt)
    
    # Reconstruct (using subset for speed)
    print("  Reconstructing from sparse samples...")
    u_recon = cs.reconstruct_l1(u_sparse[:, ::2], lambda_reg=0.05, max_iter=50)
    
    # Evaluate
    metrics = cs.evaluate_quality(u_xt[:, ::2], u_recon)
    print(f"  Reconstruction quality:")
    print(f"    NMSE: {metrics['NMSE']:.4f}")
    print(f"    Correlation: {metrics['correlation']:.4f}")
    
    # 6. Plot full results
    print("\n[6] Generating visualization...")
    fig = kt.plot_spectrum(save_path='k_omega_spectrum.png')
    
    # Additional comparison plot
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    # Original wavefield
    ax = axes[0, 0]
    extent = [t_array[0]*1000, t_array[-1]*1000, x_array[0]*100, x_array[-1]*100]
    im = ax.imshow(u_xt, aspect='auto', origin='lower', extent=extent, cmap='RdBu_r')
    ax.set_xlabel('Time (ms)')
    ax.set_ylabel('Position (cm)')
    ax.set_title('Original Wavefield u(x,t)')
    plt.colorbar(im, ax=ax)
    
    # Sparse samples
    ax = axes[0, 1]
    u_sparse_plot = np.zeros_like(u_xt)
    u_sparse_plot[sparse.receiver_indices, :] = u_sparse
    im = ax.imshow(u_sparse_plot, aspect='auto', origin='lower', extent=extent, 
                   cmap='RdBu_r')
    ax.set_xlabel('Time (ms)')
    ax.set_ylabel('Position (cm)')
    ax.set_title('Sparse Samples (4 receivers)')
    plt.colorbar(im, ax=ax)
    
    # Reconstructed
    ax = axes[0, 2]
    im = ax.imshow(u_recon, aspect='auto', origin='lower', 
                   extent=[t_array[0]*1000, t_array[-1]*1000, x_array[0]*100, x_array[-1]*100],
                   cmap='RdBu_r')
    ax.set_xlabel('Time (ms)')
    ax.set_ylabel('Position (cm)')
    ax.set_title(f'CS Reconstructed (corr={metrics["correlation"]:.3f})')
    plt.colorbar(im, ax=ax)
    
    # Dispersion comparison
    ax = axes[1, 0]
    ax.plot(f_disp, c_disp, 'b-o', markersize=4, label='Full data')
    
    # Analytical Zener
    from zener_model import ZenerModel
    zm = ZenerModel(G0, G_inf, tau_sigma)
    f_theory = np.linspace(20, 300, 100)
    c_theory = [zm.phase_velocity(2*np.pi*f) for f in f_theory]
    ax.plot(f_theory, c_theory, 'g--', linewidth=2, label='Zener theory')
    
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Phase Velocity (m/s)')
    ax.set_title('Dispersion Curve Validation')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Array geometry
    ax = axes[1, 1]
    sparse.plot_array_geometry(ax=ax)
    
    # Quality metrics
    ax = axes[1, 2]
    ax.axis('off')
    metrics_text = f"""
    Reconstruction Metrics:
    
    NMSE: {metrics['NMSE']:.4f}
    Correlation: {metrics['correlation']:.4f}
    RMSE: {metrics['RMSE']:.2e}
    
    Array Configuration:
    Receivers: {sparse.n_receivers}
    Type: {sparse.array_type}
    Compression: {sparse.n_receivers/len(x_array)*100:.1f}%
    
    Zener Parameters:
    G₀ = {G0} Pa
    G_∞ = {G_inf} Pa
    τ_σ = {tau_sigma*1000:.1f} ms
    """
    ax.text(0.1, 0.5, metrics_text, fontsize=10, family='monospace',
           verticalalignment='center')
    
    plt.tight_layout()
    plt.savefig('k_omega_full_analysis.png', dpi=150, bbox_inches='tight')
    print("  Saved: k_omega_full_analysis.png")
    
    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    
    return kt, sparse, cs, metrics


if __name__ == "__main__":
    kt, sparse, cs, metrics = demo_k_omega_transform()
