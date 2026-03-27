"""
Integrated k-ω Pipeline with FISTA+Restart
===========================================

Complete pipeline:
1. 2D wavefield simulation (Zener viscoelastic)
2. Sparse random sampling
3. FISTA with adaptive restart reconstruction
4. Weighted L1 with Zener prior
5. k-ω dispersion extraction
6. Comparison: full vs sparse vs reconstructed

Author: DSP Challenge — March 25, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
import sys
sys.path.insert(0, '/home/james/.openclaw/workspace')
sys.path.insert(0, '/home/james/.openclaw/workspace/research/week2')

from shear_wave_2d_zener import ShearWave2DZener
from zener_model import ZenerModel


class FISTAWithRestart:
    """FISTA with adaptive restart for guaranteed convergence."""
    
    def __init__(self, restart_mode='function', patience=10):
        self.restart_mode = restart_mode
        self.patience = patience
        self.restart_count = 0
    
    def solve(self, A, y, lambda_reg, max_iter=100, x_init=None, 
              weights=None, verbose=False):
        m, n = A.shape
        
        # Lipschitz constant
        L = np.linalg.norm(A @ A.conj().T, 2)
        step = 1.0 / L
        
        # Initialize
        if x_init is not None:
            x = x_init.copy()
        else:
            x = np.zeros(n, dtype=complex)
        
        z = x.copy()
        t = 1.0
        
        # Default weights
        if weights is None:
            weights = np.ones(n)
        weights = np.maximum(weights, 0.05)
        
        history = {'objective': [], 'residual': [], 'restarts': []}
        obj_best = self._objective(A, y, x, lambda_reg)
        patience_counter = 0
        
        for k in range(max_iter):
            x_old = x.copy()
            
            # Gradient step at z
            residual = y - A @ z
            x = z + step * (A.conj().T @ residual)
            
            # Weighted soft thresholding
            thresholds = step * lambda_reg / weights
            x = self._soft_threshold(x, thresholds)
            
            # Compute objective
            obj = self._objective(A, y, x, lambda_reg)
            history['objective'].append(obj)
            history['residual'].append(np.linalg.norm(residual))
            
            # Track best and check restart
            if obj < obj_best:
                obj_best = obj
                patience_counter = 0
            else:
                patience_counter += 1
            
            restart = self._check_restart(x, x_old, z, A, y, obj, lambda_reg)
            
            if restart or patience_counter >= self.patience:
                z = x.copy()
                t = 1.0
                self.restart_count += 1
                history['restarts'].append(k)
                patience_counter = 0
                if verbose and k > 0:
                    print(f"    Restart at iter {k}, obj={obj:.6e}")
            else:
                t_new = (1 + np.sqrt(1 + 4 * t**2)) / 2
                z = x + ((t - 1) / t_new) * (x - x_old)
                t = t_new
            
            # Early stopping
            if k > 20 and history['residual'][-1] < 1e-12:
                break
        
        history['restart_count'] = self.restart_count
        return x, history
    
    def _objective(self, A, y, x, lambda_reg):
        residual = y - A @ x
        data_fit = np.real(residual.conj().T @ residual)
        l1_penalty = lambda_reg * np.sum(np.abs(x))
        return data_fit + l1_penalty
    
    def _soft_threshold(self, x, thresholds):
        mag = np.abs(x)
        phase = np.angle(x)
        mag_thresh = np.maximum(mag - thresholds, 0)
        return mag_thresh * np.exp(1j * phase)
    
    def _check_restart(self, x, x_old, z, A, y, obj, lambda_reg):
        if self.restart_mode == 'none':
            return False
        elif self.restart_mode == 'function':
            obj_old = self._objective(A, y, x_old, lambda_reg)
            return obj > obj_old
        elif self.restart_mode == 'gradient':
            momentum = x - x_old
            grad_direction = z - x
            return np.real(np.vdot(grad_direction, momentum)) > 0
        return False


def generate_wavefield(nx=120, ny=100, dx=0.0015, duration=0.06):
    """Generate 2D shear wave wavefield."""
    print("[1] Generating wavefield...")
    
    sim = ShearWave2DZener(nx, ny, dx, rho=1000, 
                           G0=2000, G_inf=4000, tau_sigma=0.005)
    
    nt_steps = int(duration / sim.dt)
    wavefield = []
    t_array = []
    
    # Multi-frequency chirp source
    for n in range(nt_steps):
        t = n * sim.dt
        if t < 0.012:  # 12 ms chirp
            f_inst = 50 + (300 - 50) * (t / 0.012)
            envelope = np.exp(-(t - 0.006)**2 / (2 * 0.002**2))
            sim.add_source(t, nx//6, ny//2, amplitude=2e-5 * envelope,
                          f0=f_inst, source_type='ricker')
        
        sim.step()
        
        if n % 2 == 0:
            wavefield.append(sim.vy[:, ny//2].copy())
            t_array.append(t)
    
    u_full = np.array(wavefield).T
    dt = sim.dt * 2
    x = sim.x
    
    print(f"  Shape: {u_full.shape}")
    print(f"  Amplitude: {np.abs(u_full).max():.2e}")
    print(f"  Duration: {t_array[-1]*1000:.1f} ms")
    
    return u_full, x, dt, t_array


def sparse_sample(u_full, x, n_receivers, array_type='random'):
    """Sparse sampling with random or optimized array."""
    print(f"\n[2] Sparse sampling ({n_receivers} receivers, {array_type})...")
    
    nx = len(x)
    
    if array_type == 'random':
        np.random.seed(42)
        rec_idx = np.sort(np.random.choice(nx, n_receivers, replace=False))
    elif array_type == 'uniform':
        rec_idx = np.linspace(0, nx-1, n_receivers, dtype=int)
    else:  # optimized
        log_pos = np.logspace(0, np.log10(nx), n_receivers)
        rec_idx = np.unique(np.round(log_pos).astype(int))
        rec_idx = np.clip(rec_idx, 0, nx-1)
    
    y_sparse = u_full[rec_idx, :]
    
    print(f"  Positions: {[round(x[i]*100,1) for i in rec_idx]} cm")
    print(f"  Compression: {n_receivers/nx*100:.1f}%")
    
    return y_sparse, rec_idx


def build_sensing_matrix(x, rec_idx):
    """Build Fourier sensing matrix."""
    nx = len(x)
    dx = x[1] - x[0]
    k = 2 * np.pi * np.fft.fftfreq(nx, dx)
    
    # A[i,j] = exp(1j * k[j] * x[rec_idx[i]]) / sqrt(nx)
    A = np.exp(1j * np.outer(x[rec_idx], k)) / np.sqrt(nx)
    
    print(f"\n[3] Sensing matrix: {A.shape}")
    print(f"  Condition number: {np.linalg.cond(A):.2e}")
    
    return A, k


def reconstruct_fista(y_sparse, A, k, omega, zm, lambda_base=1e-7, 
                      max_iter=100, use_restart=True):
    """Reconstruct wavefield using FISTA with Zener weights."""
    print(f"\n[4] Reconstructing with FISTA...")
    print(f"  Max iterations: {max_iter}")
    print(f"  Restart mode: {'function' if use_restart else 'none'}")
    
    Y_freq = np.fft.rfft(y_sparse, axis=1)
    nx, n_freq = A.shape[1], len(omega)
    
    X_recon = np.zeros((nx, n_freq), dtype=complex)
    total_restarts = 0
    
    solver = FISTAWithRestart(restart_mode='function' if use_restart else 'none',
                               patience=10)
    
    for i, w in enumerate(omega):
        if i % 30 == 0:
            print(f"  Processing {i}/{n_freq} (ω={w:.0f})")
        
        y_w = Y_freq[:, i]
        
        if np.linalg.norm(y_w) < 1e-20:
            continue
        
        # Zener-informed weights
        if w > 0 and zm is not None:
            c_w = zm.phase_velocity(w)
            k_expected = w / c_w
            weights = np.exp(-0.03 * np.abs(np.abs(k) - k_expected))
            weights = np.maximum(weights, 0.1)
        else:
            weights = np.ones(nx)
        
        # Adaptive regularization
        lambda_reg = lambda_base * np.linalg.norm(y_w)
        
        # Warm start
        x_init = np.linalg.lstsq(A, y_w, rcond=None)[0]
        
        # FISTA reconstruction
        x_recon, hist = solver.solve(A, y_w, lambda_reg, max_iter=max_iter,
                                      x_init=x_init, weights=weights)
        
        X_recon[:, i] = x_recon
        total_restarts += hist.get('restart_count', 0)
    
    print(f"  Total restarts: {total_restarts}")
    
    u_recon = np.fft.irfft(X_recon, n=y_sparse.shape[1], axis=1)
    return u_recon


def komega_transform(u, dx, dt):
    """Compute k-ω spectrum."""
    nx, nt = u.shape
    
    # Windowing
    win = np.outer(np.hanning(nx), np.hanning(nt))
    u_w = u * win
    
    # 2D FFT
    U = np.fft.fftshift(np.fft.fft2(u_w))
    spectrum = np.abs(U)**2
    
    # Axes
    k = np.fft.fftshift(np.fft.fftfreq(nx, dx)) * 2 * np.pi
    f = np.fft.fftshift(np.fft.fftfreq(nt, dt))
    
    # Positive frequencies
    f0 = len(f) // 2
    return k, f[f0:], spectrum[:, f0:]


def extract_dispersion(k, f, spectrum, f_range=(50, 300)):
    """Extract dispersion curve."""
    spectrum = gaussian_filter1d(spectrum, sigma=1, axis=0)
    
    f_valid = f[(f >= f_range[0]) & (f <= f_range[1])]
    c_extracted = []
    
    for freq in f_valid:
        idx = np.argmin(np.abs(f - freq))
        spec = spectrum[:, idx]
        
        k_pos = k[k > 0]
        spec_pos = spec[k > 0]
        
        if len(k_pos) == 0:
            c_extracted.append(np.nan)
            continue
        
        k_peak = k_pos[np.argmax(spec_pos)]
        c_p = 2 * np.pi * freq / k_peak
        
        if 1 < c_p < 10:
            c_extracted.append(c_p)
        else:
            c_extracted.append(np.nan)
    
    return f_valid, np.array(c_extracted)


def evaluate_quality(u_true, u_recon):
    """Compute reconstruction metrics."""
    mask = np.abs(u_true) > 1e-15
    if np.any(mask):
        error = u_true - u_recon
        nmse = np.mean(error[mask]**2) / np.mean(u_true[mask]**2)
        corr = np.corrcoef(u_true[mask].flatten(), u_recon[mask].flatten())[0, 1]
    else:
        nmse = np.nan
        corr = np.nan
    return nmse, corr


def visualize_results(u_full, u_recon, y_sparse, rec_idx, k_full, f_full, 
                      spec_full, spec_recon, f_full_disp, c_full_disp,
                      f_rec_disp, c_rec_disp, zm, dt, x):
    """Create comprehensive visualization."""
    print("\n[6] Generating visualization...")
    
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    
    # Wavefields
    nx, nt = u_full.shape
    dx = x[1] - x[0]
    extent = [0, nt*dt*1000, 0, nx*dx*100]
    
    u_nonzero = u_full[np.abs(u_full) > 1e-15]
    vmax = np.percentile(np.abs(u_nonzero), 99) if len(u_nonzero) > 0 else 1e-6
    
    im0 = axes[0, 0].imshow(u_full, aspect='auto', origin='lower', 
                            extent=extent, cmap='RdBu_r', vmin=-vmax, vmax=vmax)
    axes[0, 0].set_title('Full Wavefield')
    axes[0, 0].set_ylabel('Position (cm)')
    plt.colorbar(im0, ax=axes[0, 0])
    
    u_sparse = np.zeros_like(u_full)
    u_sparse[rec_idx, :] = y_sparse
    im1 = axes[0, 1].imshow(u_sparse, aspect='auto', origin='lower',
                            extent=extent, cmap='RdBu_r', vmin=-vmax, vmax=vmax)
    axes[0, 1].set_title(f'Sparse ({len(rec_idx)} rec)')
    plt.colorbar(im1, ax=axes[0, 1])
    
    nmse, corr = evaluate_quality(u_full, u_recon)
    im2 = axes[0, 2].imshow(u_recon, aspect='auto', origin='lower',
                            extent=extent, cmap='RdBu_r', vmin=-vmax, vmax=vmax)
    axes[0, 2].set_title(f'Reconstructed (r={corr:.3f})')
    plt.colorbar(im2, ax=axes[0, 2])
    
    # k-ω spectra
    k_pos = k_full[k_full >= 0]
    spec_f = spec_full[k_full >= 0, :]
    spec_r = spec_recon[k_full >= 0, :]
    
    spec_f_log = 10 * np.log10(spec_f + 1e-20)
    spec_r_log = 10 * np.log10(spec_r + 1e-20)
    vmax_s = np.percentile(spec_f_log, 99)
    vmin_s = vmax_s - 50
    
    im3 = axes[1, 0].imshow(spec_f_log, aspect='auto', origin='lower',
                            extent=[f_full[0], f_full[-1], k_pos[0], k_pos[-1]],
                            cmap='jet', vmin=vmin_s, vmax=vmax_s)
    axes[1, 0].set_title('k-ω: Full')
    axes[1, 0].set_xlabel('Frequency (Hz)')
    axes[1, 0].set_ylabel('k (rad/m)')
    plt.colorbar(im3, ax=axes[1, 0])
    
    im4 = axes[1, 1].imshow(spec_r_log, aspect='auto', origin='lower',
                            extent=[f_full[0], f_full[-1], k_pos[0], k_pos[-1]],
                            cmap='jet', vmin=vmin_s, vmax=vmax_s)
    axes[1, 1].set_title('k-ω: Reconstructed')
    axes[1, 1].set_xlabel('Frequency (Hz)')
    plt.colorbar(im4, ax=axes[1, 1])
    
    # Dispersion curves
    ax = axes[1, 2]
    f_theory = np.linspace(50, 300, 100)
    c_theory = [zm.phase_velocity(2*np.pi*f) for f in f_theory]
    
    ax.plot(f_theory, c_theory, 'k--', linewidth=2, label='Zener theory')
    
    valid_f = ~np.isnan(c_full_disp)
    valid_r = ~np.isnan(c_rec_disp)
    
    if np.any(valid_f):
        ax.plot(f_full_disp[valid_f], c_full_disp[valid_f], 'bo',
                markersize=6, label='Full data', alpha=0.7)
    if np.any(valid_r):
        ax.plot(f_rec_disp[valid_r], c_rec_disp[valid_r], 'rs',
                markersize=5, label='Reconstructed', alpha=0.7)
    
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Phase Velocity (m/s)')
    ax.set_title('Dispersion')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim(1.5, 3.5)
    
    plt.tight_layout()
    plt.savefig('komega_fista_final.png', dpi=150, bbox_inches='tight')
    print("  Saved: komega_fista_final.png")
    
    return fig


def main():
    """Run complete integrated pipeline."""
    print("=" * 70)
    print("INTEGRATED k-ω PIPELINE WITH FISTA+RESTART")
    print("=" * 70)
    
    # Parameters
    nx, ny = 120, 100
    dx = 0.0015
    duration = 0.06
    n_receivers = 12
    
    # 1. Generate wavefield
    u_full, x, dt, t_array = generate_wavefield(nx, ny, dx, duration)
    
    # 2. Sparse sampling (RANDOM for CS)
    y_sparse, rec_idx = sparse_sample(u_full, x, n_receivers, array_type='random')
    
    # 3. Build sensing matrix
    A, k = build_sensing_matrix(x, rec_idx)
    
    # 4. Reconstruct with FISTA+Restart
    omega = 2 * np.pi * np.fft.rfftfreq(u_full.shape[1], dt)
    zm = ZenerModel(2000, 4000, 0.005)
    
    u_recon = reconstruct_fista(y_sparse, A, k, omega, zm, 
                                 lambda_base=5e-8, max_iter=80,
                                 use_restart=True)
    
    # 5. k-ω analysis
    print("\n[5] k-ω analysis...")
    k_full, f_full, spec_full = komega_transform(u_full, dx, dt)
    k_rec, f_rec, spec_rec = komega_transform(u_recon, dx, dt)
    
    f_full_disp, c_full_disp = extract_dispersion(k_full, f_full, spec_full)
    f_rec_disp, c_rec_disp = extract_dispersion(k_rec, f_rec, spec_rec)
    
    n_full = np.sum(~np.isnan(c_full_disp))
    n_rec = np.sum(~np.isnan(c_rec_disp))
    print(f"  Full data: {n_full} valid points")
    print(f"  Reconstructed: {n_rec} valid points")
    
    # Quality metrics
    nmse, corr = evaluate_quality(u_full, u_recon)
    print(f"\n  Quality: NMSE={nmse:.4f}, correlation={corr:.4f}")
    
    # 6. Visualize
    visualize_results(u_full, u_recon, y_sparse, rec_idx, k_full, f_full,
                      spec_full, spec_rec, f_full_disp, c_full_disp,
                      f_rec_disp, c_rec_disp, zm, dt, x)
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Receivers: {n_receivers}/{nx} ({n_receivers/nx*100:.1f}%)")
    print(f"Reconstruction: NMSE={nmse:.4f}, r={corr:.4f}")
    print(f"Dispersion points: {n_full} (full) vs {n_rec} (recon)")
    print("=" * 70)
    
    return u_full, u_recon, nmse, corr


if __name__ == "__main__":
    u_full, u_recon, nmse, corr = main()
