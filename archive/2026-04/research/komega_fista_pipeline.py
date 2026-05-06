"""
Integrated k-ω Pipeline with FISTA Reconstruction
=================================================

Complete pipeline combining:
1. Sparse wavefield sampling (simulating few receivers)
2. Weighted FISTA reconstruction with Zener prior
3. k-ω dispersion extraction
4. Comparison: full data vs sparse vs reconstructed

Author: DSP Challenge — March 25, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
import sys
sys.path.insert(0, '/home/james/.openclaw/workspace')

from fista_with_restart import WeightedFISTA, ZenerWeightedFISTA


class SparseKOmegaPipeline:
    """
    Complete pipeline: sparse sampling → FISTA reconstruction → k-ω extraction.
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
        rho : float
            Density (kg/m³)
        """
        self.x = np.array(x_array)
        self.t = np.array(t_array)
        self.nx = len(x_array)
        self.nt = len(t_array)
        self.dx = x_array[1] - x_array[0]
        self.dt = t_array[1] - t_array[0]
        
        self.G0, self.G_inf, self.tau_sigma = zener_params
        self.rho = rho
        
        # Import Zener model
        try:
            from zener_model import ZenerModel
            self.zm = ZenerModel(self.G0, self.G_inf, self.tau_sigma)
        except ImportError:
            self.zm = None
            print("Warning: ZenerModel not found, using analytical weights")
        
        # Build Fourier basis for CS
        self._build_fourier_basis()
        
        print(f"Pipeline initialized:")
        print(f"  Grid: {self.nx} × {self.nt}")
        print(f"  dx = {self.dx*1000:.2f} mm, dt = {self.dt*1000:.3f} ms")
    
    def _build_fourier_basis(self):
        """Build spatial Fourier basis matrix."""
        k = 2 * np.pi * np.fft.fftfreq(self.nx, self.dx)
        self.k = k
        X, K = np.meshgrid(self.x, k, indexing='ij')
        self.Phi = np.exp(1j * K * X) / np.sqrt(self.nx)
    
    def sample_sparse(self, u_full, n_receivers, array_type='optimized'):
        """
        Sample wavefield with sparse receiver array.
        
        Parameters:
        -----------
        u_full : ndarray (nx, nt)
            Full wavefield
        n_receivers : int
            Number of receivers
        array_type : str
            'uniform', 'random', 'endfire', 'optimized'
            
        Returns:
        --------
        y_sparse : ndarray (n_receivers, nt)
            Sparse measurements
        rec_idx : array
            Receiver indices
        """
        nx = self.nx_full = len(self.x)
        
        if array_type == 'uniform':
            rec_idx = np.linspace(0, nx-1, n_receivers, dtype=int)
        
        elif array_type == 'random':
            np.random.seed(42)
            min_spacing = nx // (2 * n_receivers)
            rec_idx = []
            while len(rec_idx) < n_receivers:
                i = np.random.randint(0, nx)
                if all(abs(i - j) >= min_spacing for j in rec_idx):
                    rec_idx.append(i)
            rec_idx = np.array(sorted(rec_idx))
        
        elif array_type == 'endfire':
            n_per_end = n_receivers // 2
            rec_idx = np.concatenate([
                np.linspace(0, nx//4, n_per_end, dtype=int),
                np.linspace(3*nx//4, nx-1, n_receivers - n_per_end, dtype=int)
            ])
        
        elif array_type == 'optimized':
            # Log-spaced for better frequency coverage
            log_pos = np.logspace(0, np.log10(nx), n_receivers)
            rec_idx = np.unique(np.round(log_pos).astype(int))
            rec_idx = np.clip(rec_idx, 0, nx-1)
            if len(rec_idx) < n_receivers:
                extra = np.random.choice(
                    [i for i in range(nx) if i not in rec_idx],
                    n_receivers - len(rec_idx),
                    replace=False
                )
                rec_idx = np.sort(np.concatenate([rec_idx, extra]))
        
        else:
            raise ValueError(f"Unknown array type: {array_type}")
        
        y_sparse = u_full[rec_idx, :]
        
        print(f"\nSparse sampling: {n_receivers} receivers ({array_type})")
        print(f"  Positions: {list(self.x[rec_idx]*100)} cm")
        print(f"  Compression: {n_receivers/nx*100:.1f}%")
        
        return y_sparse, rec_idx
    
    def compute_zener_weights(self, omega, sharpness=0.05):
        """
        Compute Zener-informed weights for given frequency.
        
        Parameters:
        -----------
        omega : float
            Angular frequency (rad/s)
        sharpness : float
            Weight curve sharpness (lower = broader)
            
        Returns:
        --------
        weights : ndarray (nx,)
            Weight vector for L1 regularization
        """
        if omega <= 0 or self.zm is None:
            return np.ones(self.nx)
        
        # Expected wavenumber from Zener model
        c_omega = self.zm.phase_velocity(omega)
        k_expected = omega / c_omega
        
        # Distance from expected k
        k_dist = np.abs(np.abs(self.k) - k_expected)
        
        # Gaussian-like weights
        weights = np.exp(-sharpness * k_dist)
        weights = np.maximum(weights, 0.1)  # Floor
        
        return weights
    
    def reconstruct_weighted_fista(self, y_sparse, rec_idx,
                                    lambda_reg=0.05, max_iter=50,
                                    use_zener_weights=True):
        """
        Reconstruct wavefield using weighted FISTA per frequency.
        
        Parameters:
        -----------
        y_sparse : ndarray (n_rec, nt)
            Sparse measurements
        rec_idx : array
            Receiver indices
        lambda_reg : float
            L1 regularization parameter
        max_iter : int
            FISTA iterations per frequency
        use_zener_weights : bool
            Use Zener-informed weights
            
        Returns:
        --------
        u_recon : ndarray (nx, nt)
            Reconstructed wavefield
        metrics : dict
            Quality metrics
        """
        n_rec = len(rec_idx)
        
        # Sensing matrix
        A = self.Phi[rec_idx, :]  # (n_rec, nx)
        
        # Transform to frequency domain
        Y_freq = np.fft.rfft(y_sparse, axis=1)  # (n_rec, n_freq)
        omega_array = 2 * np.pi * np.fft.rfftfreq(self.nt, self.dt)
        n_freq = len(omega_array)
        
        print(f"\nFrequency-domain reconstruction:")
        print(f"  Frequencies: {n_freq}")
        print(f"  FISTA iterations: {max_iter}")
        print(f"  Zener weights: {use_zener_weights}")
        
        # Storage
        X_recon = np.zeros((self.nx, n_freq), dtype=complex)
        
        # Process each frequency
        for i_freq, omega in enumerate(omega_array):
            if i_freq % 20 == 0:
                print(f"  Processing ω = {omega:.1f} rad/s ({i_freq}/{n_freq})")
            
            y_omega = Y_freq[:, i_freq]
            
            # Compute weights
            if use_zener_weights:
                weights = self.compute_zener_weights(omega, sharpness=0.05)
            else:
                weights = np.ones(self.nx)
            
            # Warm start with pseudo-inverse
            x_init = np.linalg.lstsq(A, y_omega, rcond=None)[0]
            
            # Weighted FISTA
            solver = WeightedFISTA(weights=weights)
            x_freq, _ = solver.solve(A, y_omega, lambda_reg, 
                                     max_iter=max_iter, x_init=x_init)
            
            X_recon[:, i_freq] = x_freq
        
        # Inverse FFT to time domain
        u_recon = np.fft.irfft(X_recon, n=self.nt, axis=1)
        
        return u_recon
    
    def compute_komega(self, u_xt):
        """
        Compute k-ω transform.
        
        Parameters:
        -----------
        u_xt : ndarray (nx, nt)
            Spatiotemporal wavefield
            
        Returns:
        --------
        k : array
            Wavenumber axis (rad/m)
        f : array
            Frequency axis (Hz)
        spectrum : ndarray
            Power spectrum |U(k, ω)|²
        """
        nx, nt = u_xt.shape
        
        # Tukey window
        def tukey_window(n, alpha=0.1):
            w = np.ones(n)
            taper = int(alpha * n / 2)
            for i in range(taper):
                w[i] = 0.5 * (1 - np.cos(np.pi * i / taper))
                w[n-1-i] = w[i]
            return w
        
        win_x = tukey_window(nx, 0.15)
        win_t = tukey_window(nt, 0.05)
        u_windowed = u_xt * np.outer(win_x, win_t)
        
        # 2D FFT
        U = np.fft.fftshift(np.fft.fft2(u_windowed))
        spectrum = np.abs(U)**2
        
        # Axes
        k_full = np.fft.fftshift(np.fft.fftfreq(nx, self.dx)) * 2 * np.pi
        f_full = np.fft.fftshift(np.fft.fftfreq(nt, self.dt))
        
        # Positive frequencies only
        zero_f_idx = len(f_full) // 2
        f_pos = f_full[zero_f_idx:]
        spectrum_pos = spectrum[:, zero_f_idx:]
        
        return k_full, f_pos, spectrum_pos
    
    def extract_dispersion(self, k, f, spectrum, f_range=(50, 300)):
        """
        Extract dispersion curve from k-ω spectrum.
        
        Parameters:
        -----------
        k : array
            Wavenumber axis
        f : array
            Frequency axis
        spectrum : ndarray
            Power spectrum
        f_range : tuple
            Frequency range to extract (Hz)
            
        Returns:
        --------
        f_extracted : array
            Extracted frequencies
        c_extracted : array
            Extracted phase velocities
        """
        # Smooth spectrum
        spectrum_smooth = gaussian_filter1d(spectrum, sigma=1.0, axis=0)
        
        # Frequency mask
        f_mask = (f >= f_range[0]) & (f <= f_range[1])
        f_valid = f[f_mask]
        
        c_extracted = []
        f_extracted = []
        
        for freq in f_valid:
            idx = np.where(f == freq)[0][0]
            spec_slice = spectrum_smooth[:, idx]
            
            # Find peak in positive k
            k_pos_mask = k > 0
            k_pos = k[k_pos_mask]
            spec_pos = spec_slice[k_pos_mask]
            
            if len(k_pos) == 0:
                continue
            
            # Find peak
            peak_idx = np.argmax(spec_pos)
            k_peak = k_pos[peak_idx]
            
            # Phase velocity
            omega = 2 * np.pi * freq
            c_p = omega / k_peak
            
            # Sanity check
            if 1.0 < c_p < 15.0:
                c_extracted.append(c_p)
                f_extracted.append(freq)
        
        return np.array(f_extracted), np.array(c_extracted)
    
    def evaluate_reconstruction(self, u_true, u_recon):
        """Compute reconstruction quality metrics."""
        error = u_true - u_recon
        nmse = np.mean(np.abs(error)**2) / np.mean(np.abs(u_true)**2)
        
        # Correlation
        u_true_flat = np.real(u_true.flatten())
        u_recon_flat = np.real(u_recon.flatten())
        corr = np.corrcoef(u_true_flat, u_recon_flat)[0, 1]
        
        return {'NMSE': nmse, 'correlation': corr}


def run_integrated_demo():
    """Run complete integrated pipeline demonstration."""
    print("=" * 70)
    print("INTEGRATED k-ω PIPELINE WITH FISTA RECONSTRUCTION")
    print("=" * 70)
    
    # Try to load existing wavefield or generate one
    try:
        from research.week2.shear_wave_2d_zener import ShearWave2DZener
        generate = True
    except ImportError:
        generate = False
        print("\nNote: Cannot import shear_wave_2d_zener")
        print("      Using synthetic data for demonstration")
    
    # Parameters
    G0, G_inf, tau_sigma = 2000, 4000, 0.005
    rho = 1000
    
    # Generate or load wavefield
    if generate:
        print("\n[1] Generating 2D wavefield simulation...")
        nx, ny = 100, 80
        dx = 0.002
        
        sim = ShearWave2DZener(nx, ny, dx, rho=rho, 
                               G0=G0, G_inf=G_inf, tau_sigma=tau_sigma)
        
        nt = 500
        sx, sy = nx // 4, ny // 2
        
        wavefield = []
        t_array = []
        
        for n in range(nt):
            t = n * sim.dt
            if n < 150:
                sim.add_source(t, sx, sy, amplitude=2e-5, 
                              f0=150, source_type='ricker')
            sim.step()
            
            if n % 2 == 0:
                wavefield.append(sim.vy[:, ny//2].copy())
                t_array.append(t)
        
        u_full = np.array(wavefield).T
        t_array = np.array(t_array)
        x_array = sim.x
        
    else:
        print("\n[1] Generating synthetic wavefield...")
        nx, nt = 100, 250
        dx = 0.002
        x_array = np.arange(nx) * dx
        dt = 2e-5
        t_array = np.arange(nt) * dt
        
        # Synthetic chirp wave
        u_full = np.zeros((nx, nt))
        for i, x in enumerate(x_array):
            for j, t in enumerate(t_array):
                delay = x / 2.0  # Wave propagation
                if t > delay:
                    u_full[i, j] = np.sin(2 * np.pi * 150 * (t - delay)) * \
                                   np.exp(-((t - delay) - 0.01)**2 / (2 * 0.005**2))
    
    print(f"  Wavefield shape: {u_full.shape}")
    print(f"  Spatial: {x_array[0]*100:.1f} to {x_array[-1]*100:.1f} cm")
    print(f"  Temporal: {t_array[0]*1000:.1f} to {t_array[-1]*1000:.1f} ms")
    
    # Initialize pipeline
    print("\n[2] Initializing pipeline...")
    pipeline = SparseKOmegaPipeline(x_array, t_array, 
                                    (G0, G_inf, tau_sigma), rho)
    
    # Full data k-ω
    print("\n[3] Computing k-ω from full data...")
    k, f, spectrum_full = pipeline.compute_komega(u_full)
    f_full, c_full = pipeline.extract_dispersion(k, f, spectrum_full)
    print(f"  Extracted {len(f_full)} dispersion points")
    
    # Test with different receiver counts
    results = {}
    receiver_configs = [4, 8, 16]
    
    for n_rec in receiver_configs:
        print(f"\n{'='*50}")
        print(f"[4.{n_rec//4}] Testing with {n_rec} receivers")
        print(f"{'='*50}")
        
        # Sparse sampling
        y_sparse, rec_idx = pipeline.sample_sparse(u_full, n_rec, 
                                                    array_type='optimized')
        
        # Reconstruct with weighted FISTA
        print("\n  Reconstructing with weighted FISTA...")
        u_recon = pipeline.reconstruct_weighted_fista(
            y_sparse, rec_idx, lambda_reg=0.03, max_iter=30
        )
        
        # Evaluate
        metrics = pipeline.evaluate_reconstruction(u_full, u_recon)
        print(f"  Quality: NMSE={metrics['NMSE']:.4f}, r={metrics['correlation']:.4f}")
        
        # k-ω on reconstructed
        k, f, spectrum_recon = pipeline.compute_komega(u_recon)
        f_recon, c_recon = pipeline.extract_dispersion(k, f, spectrum_recon)
        print(f"  Extracted {len(f_recon)} dispersion points from reconstruction")
        
        results[n_rec] = {
            'u_recon': u_recon,
            'y_sparse': y_sparse,
            'rec_idx': rec_idx,
            'metrics': metrics,
            'f_disp': f_recon,
            'c_disp': c_recon,
            'spectrum': spectrum_recon
        }
    
    # Visualization
    print("\n[5] Generating visualization...")
    fig = visualize_comparison(pipeline, u_full, results, G0, G_inf, tau_sigma)
    
    plt.savefig('komega_fista_integrated.png', dpi=150, bbox_inches='tight')
    print("  ✓ Saved: komega_fista_integrated.png")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Full data: {len(f_full)} dispersion points extracted")
    print("")
    print("Sparse sampling with weighted FISTA:")
    for n_rec, data in results.items():
        m = data['metrics']
        print(f"  {n_rec:2d} receivers: "
              f"NMSE={m['NMSE']:.4f}, r={m['correlation']:.3f}, "
              f"{len(data['f_disp'])} dispersion pts")
    
    print("\n✓ Pipeline complete!")
    
    return results


def visualize_comparison(pipeline, u_full, results, G0, G_inf, tau_sigma):
    """Create comprehensive visualization."""
    
    n_configs = len(results)
    fig, axes = plt.subplots(3, n_configs + 1, figsize=(16, 12))
    
    # Full data reference
    k, f, spectrum_full = pipeline.compute_komega(u_full)
    f_full, c_full = pipeline.extract_dispersion(k, f, spectrum_full)
    
    extent = [pipeline.t[0]*1000, pipeline.t[-1]*1000,
              pipeline.x[0]*100, pipeline.x[-1]*100]
    vmax = np.max(np.abs(u_full))
    
    # Row 0: Wavefields
    axes[0, 0].imshow(u_full, aspect='auto', origin='lower', extent=extent,
                      cmap='RdBu_r', vmin=-vmax, vmax=vmax)
    axes[0, 0].set_title('Full Data (Reference)')
    axes[0, 0].set_ylabel('Position (cm)')
    
    for i, (n_rec, data) in enumerate(results.items()):
        u_rec = data['u_recon']
        m = data['metrics']
        
        axes[0, i+1].imshow(u_rec, aspect='auto', origin='lower', extent=extent,
                           cmap='RdBu_r', vmin=-vmax, vmax=vmax)
        axes[0, i+1].set_title(f'{n_rec} rec: r={m["correlation"]:.2f}')
    
    # Row 1: k-ω spectra
    k_pos = k[k >= 0]
    spec_full_pos = spectrum_full[k >= 0, :]
    
    axes[1, 0].imshow(10*np.log10(spec_full_pos + 1e-10), aspect='auto',
                      origin='lower', extent=[f[0], f[-1], k_pos[0], k_pos[-1]],
                      cmap='jet', vmin=-20, vmax=30)
    axes[1, 0].set_title('k-ω Spectrum')
    axes[1, 0].set_ylabel('k (rad/m)')
    
    for i, (n_rec, data) in enumerate(results.items()):
        spec = data['spectrum']
        spec_pos = spec[k >= 0, :]
        
        axes[1, i+1].imshow(10*np.log10(spec_pos + 1e-10), aspect='auto',
                           origin='lower', extent=[f[0], f[-1], k_pos[0], k_pos[-1]],
                           cmap='jet', vmin=-20, vmax=30)
        axes[1, i+1].set_title(f'{n_rec} rec spectrum')
    
    # Row 2: Dispersion curves
    ax = axes[2, 0]
    if len(f_full) > 0:
        ax.plot(f_full, c_full, 'b-o', markersize=6, label='Full data')
    
    # Zener theory
    from research.week2.zener_model import ZenerModel
    zm = ZenerModel(G0, G_inf, tau_sigma)
    f_theory = np.linspace(50, 300, 100)
    c_theory = [zm.phase_velocity(2*np.pi*f) for f in f_theory]
    ax.plot(f_theory, c_theory, 'k--', linewidth=2, label='Zener theory')
    
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Phase Velocity (m/s)')
    ax.set_title('Dispersion Curves')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 6)
    
    for i, (n_rec, data) in enumerate(results.items()):
        ax = axes[2, i+1]
        f_r = data['f_disp']
        c_r = data['c_disp']
        m = data['metrics']
        
        if len(f_r) > 0:
            ax.plot(f_r, c_r, 'r-s', markersize=5, label=f'{n_rec} rec')
        ax.plot(f_theory, c_theory, 'k--', linewidth=2, alpha=0.5)
        
        ax.set_xlabel('Frequency (Hz)')
        ax.set_title(f'{n_rec} rec: NMSE={m["NMSE"]:.3f}')
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 6)
    
    plt.tight_layout()
    return fig


if __name__ == "__main__":
    results = run_integrated_demo()
