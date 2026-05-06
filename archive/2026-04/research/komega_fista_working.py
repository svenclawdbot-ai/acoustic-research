"""
Working k-ω + FISTA Integration
================================

Simplified, robust pipeline that actually works.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
import sys
sys.path.insert(0, '/home/james/.openclaw/workspace')
sys.path.insert(0, '/home/james/.openclaw/workspace/research/week2')

from shear_wave_2d_zener import ShearWave2DZener
from zener_model import ZenerModel


def soft_threshold(x, threshold):
    """Soft thresholding operator."""
    mag = np.abs(x)
    phase = np.angle(x)
    mag_thresh = np.maximum(mag - threshold, 0)
    return mag_thresh * np.exp(1j * phase)


def fista_reconstruct(A, y, lambda_reg, max_iter=50, weights=None):
    """
    FISTA for L1 minimization: min ||y - Ax||^2 + lambda*||Wx||_1
    
    Parameters:
    -----------
    A : ndarray (m, n) - sensing matrix
    y : ndarray (m,) - measurements  
    lambda_reg : float - regularization
    max_iter : int - iterations
    weights : ndarray (n,) - weights (higher = less penalty)
    
    Returns:
    --------
    x : ndarray (n,) - reconstructed signal
    """
    m, n = A.shape
    
    # Lipschitz constant
    L = np.linalg.norm(A @ A.conj().T, 2)
    step = 1.0 / L
    
    # Initialize
    x = np.zeros(n, dtype=complex)
    z = x.copy()
    t = 1.0
    
    # Default weights
    if weights is None:
        weights = np.ones(n)
    weights = np.maximum(weights, 0.1)
    
    for _ in range(max_iter):
        x_old = x.copy()
        
        # Gradient step at z
        residual = y - A @ z
        x = z + step * (A.conj().T @ residual)
        
        # Weighted soft thresholding
        thresholds = step * lambda_reg / weights
        x = soft_threshold(x, thresholds)
        
        # FISTA momentum
        t_new = (1 + np.sqrt(1 + 4 * t**2)) / 2
        z = x + ((t - 1) / t_new) * (x - x_old)
        t = t_new
    
    return x


def komega_transform(u, dx, dt):
    """Compute k-ω spectrum."""
    nx, nt = u.shape
    
    # Window
    win_x = np.hanning(nx)
    win_t = np.hanning(nt)
    u_w = u * np.outer(win_x, win_t)
    
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
        
        # Peak in positive k
        k_pos = k[k > 0]
        spec_pos = spec[k > 0]
        if len(k_pos) == 0:
            continue
        
        k_peak = k_pos[np.argmax(spec_pos)]
        c_p = 2 * np.pi * freq / k_peak
        
        if 1 < c_p < 10:
            c_extracted.append(c_p)
        else:
            c_extracted.append(np.nan)
    
    return f_valid, np.array(c_extracted)


def run_pipeline():
    """Run complete pipeline."""
    print("=" * 60)
    print("k-ω + FISTA RECONSTRUCTION PIPELINE")
    print("=" * 60)
    
    # 1. Generate wavefield
    print("\n[1] Generating wavefield...")
    nx, ny = 100, 80
    dx = 0.002
    sim = ShearWave2DZener(nx, ny, dx, rho=1000, G0=2000, G_inf=4000, tau_sigma=0.005)
    
    nt = 1500  # Longer simulation for wave propagation
    wavefield = []
    for n in range(nt):
        t = n * sim.dt
        if n < 100:  # Shorter source for cleaner wave
            sim.add_source(t, nx//8, ny//2, amplitude=2e-5, f0=150, source_type='ricker')
        sim.step()
        if n % 3 == 0:  # Record every 3 steps
            wavefield.append(sim.vy[:, ny//2].copy())
    
    u_full = np.array(wavefield).T
    dt = sim.dt * 3
    x = sim.x
    
    print(f"  Shape: {u_full.shape}")
    print(f"  Amplitude: {np.abs(u_full).max():.2e}")
    print(f"  Nonzero: {np.count_nonzero(np.abs(u_full) > 1e-15)} / {u_full.size}")
    
    # 2. Sparse sampling
    print("\n[2] Sparse sampling...")
    n_rec = 8
    rec_idx = np.linspace(0, nx-1, n_rec, dtype=int)
    y_sparse = u_full[rec_idx, :]
    print(f"  Receivers: {n_rec} at positions {[round(x[i]*100,1) for i in rec_idx]} cm")
    
    # 3. Build sensing matrix
    print("\n[3] Building Fourier basis...")
    k = 2 * np.pi * np.fft.fftfreq(nx, dx)
    Phi = np.exp(1j * np.outer(x, k)) / np.sqrt(nx)  # (nx, nx) Fourier basis
    A = Phi[rec_idx, :]  # (n_rec, nx) sensing matrix
    print(f"  A shape: {A.shape}")
    
    # 4. Reconstruct with weighted FISTA
    print("\n[4] Reconstructing with FISTA...")
    zm = ZenerModel(2000, 4000, 0.005)
    
    # Transform to frequency domain
    Y_freq = np.fft.rfft(y_sparse, axis=1)  # (n_rec, n_freq)
    omega = 2 * np.pi * np.fft.rfftfreq(u_full.shape[1], dt)
    
    X_recon = np.zeros((nx, len(omega)), dtype=complex)
    
    # Find frequency with maximum energy for debugging
    energy = np.sum(np.abs(Y_freq)**2, axis=0)
    peak_freq = np.argmax(energy)
    print(f"  Peak energy at frequency index {peak_freq}")
    
    # Scale factor for regularization
    y_scale = np.sqrt(np.mean(np.abs(Y_freq)**2))
    print(f"  Measurement scale: {y_scale:.2e}")
    
    for i, w in enumerate(omega):
        if i % 30 == 0:
            print(f"  Freq {i}/{len(omega)}: ω={w:.1f}")
        
        # Zener-informed weights
        if w > 0:
            c_w = zm.phase_velocity(w)
            k_expected = w / c_w
            weights = np.exp(-0.02 * np.abs(np.abs(k) - k_expected))
            weights = np.maximum(weights, 0.05)
        else:
            weights = np.ones(nx)
        
        # Reconstruct
        y_w = Y_freq[:, i]
        
        # Skip if no energy
        if np.linalg.norm(y_w) < 1e-20:
            continue
        
        # Adaptive regularization based on signal strength
        signal_norm = np.linalg.norm(y_w)
        lambda_reg = 1e-7 * signal_norm  # Very small regularization
        
        x_init = np.linalg.lstsq(A, y_w, rcond=None)[0]
        x_recon = fista_reconstruct(A, y_w, lambda_reg=lambda_reg, max_iter=50, 
                                     weights=weights)
        X_recon[:, i] = x_recon
    
    # Back to time domain
    u_recon = np.fft.irfft(X_recon, n=u_full.shape[1], axis=1)
    
    # Quality metrics
    nmse = np.mean((u_full - u_recon)**2) / np.mean(u_full**2)
    corr = np.corrcoef(u_full.flatten(), u_recon.flatten())[0, 1]
    print(f"\n  Reconstruction: NMSE={nmse:.4f}, correlation={corr:.4f}")
    
    # 5. k-ω analysis
    print("\n[5] k-ω analysis...")
    k_full, f_full, spec_full = komega_transform(u_full, dx, dt)
    k_rec, f_rec, spec_rec = komega_transform(u_recon, dx, dt)
    
    f_disp_full, c_disp_full = extract_dispersion(k_full, f_full, spec_full)
    f_disp_rec, c_disp_rec = extract_dispersion(k_rec, f_rec, spec_rec)
    
    print(f"  Full data: {np.sum(~np.isnan(c_disp_full))} valid dispersion points")
    print(f"  Reconstructed: {np.sum(~np.isnan(c_disp_rec))} valid dispersion points")
    
    # 6. Plot
    print("\n[6] Plotting...")
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    # Wavefields - use actual data range for scaling
    extent = [0, u_full.shape[1]*dt*1000, 0, nx*dx*100]
    
    # Find actual signal range (ignore zeros)
    u_nonzero = u_full[np.abs(u_full) > 1e-15]
    if len(u_nonzero) > 0:
        vmax = np.percentile(np.abs(u_nonzero), 99)
    else:
        vmax = np.abs(u_full).max()
    
    print(f"  Plot vmax: {vmax:.2e}")
    
    im0 = axes[0, 0].imshow(u_full, aspect='auto', origin='lower', extent=extent,
                            cmap='RdBu_r', vmin=-vmax, vmax=vmax)
    axes[0, 0].set_title('Full Wavefield')
    axes[0, 0].set_ylabel('Position (cm)')
    plt.colorbar(im0, ax=axes[0, 0])
    
    # Sparse samples
    u_sparse = np.zeros_like(u_full)
    u_sparse[rec_idx, :] = y_sparse
    im1 = axes[0, 1].imshow(u_sparse, aspect='auto', origin='lower', extent=extent,
                            cmap='RdBu_r', vmin=-vmax, vmax=vmax)
    axes[0, 1].set_title(f'Sparse Samples ({n_rec} rec)')
    plt.colorbar(im1, ax=axes[0, 1])
    
    # Reconstructed
    im2 = axes[0, 2].imshow(u_recon, aspect='auto', origin='lower', extent=extent,
                            cmap='RdBu_r', vmin=-vmax, vmax=vmax)
    axes[0, 2].set_title(f'Reconstructed (r={corr:.2f})')
    plt.colorbar(im2, ax=axes[0, 2])
    
    # k-ω spectra - use log scale with proper vmin/vmax
    k_pos = k_full[k_full >= 0]
    spec_f = spec_full[k_full >= 0, :]
    spec_r = spec_rec[k_rec >= 0, :]
    
    # Log transform with clipping
    spec_f_log = 10*np.log10(spec_f + 1e-20)
    spec_r_log = 10*np.log10(spec_r + 1e-20)
    
    # Dynamic range
    vmax_spec = np.percentile(spec_f_log, 99)
    vmin_spec = vmax_spec - 60  # 60 dB dynamic range
    
    im3 = axes[1, 0].imshow(spec_f_log, aspect='auto', origin='lower',
                            extent=[f_full[0], f_full[-1], k_pos[0], k_pos[-1]],
                            cmap='jet', vmin=vmin_spec, vmax=vmax_spec)
    axes[1, 0].set_title('k-ω: Full Data')
    axes[1, 0].set_xlabel('Frequency (Hz)')
    axes[1, 0].set_ylabel('k (rad/m)')
    plt.colorbar(im3, ax=axes[1, 0])
    
    im4 = axes[1, 1].imshow(spec_r_log, aspect='auto', origin='lower',
                            extent=[f_rec[0], f_rec[-1], k_pos[0], k_pos[-1]],
                            cmap='jet', vmin=vmin_spec, vmax=vmax_spec)
    axes[1, 1].set_title('k-ω: Reconstructed')
    axes[1, 1].set_xlabel('Frequency (Hz)')
    plt.colorbar(im4, ax=axes[1, 1])
    
    # Dispersion curves
    ax = axes[1, 2]
    f_theory = np.linspace(50, 300, 100)
    c_theory = [zm.phase_velocity(2*np.pi*f) for f in f_theory]
    
    ax.plot(f_theory, c_theory, 'k--', linewidth=2, label='Zener theory')
    
    # Only plot valid (non-nan) points
    valid_full = ~np.isnan(c_disp_full)
    valid_rec = ~np.isnan(c_disp_rec)
    
    if np.any(valid_full):
        ax.plot(f_disp_full[valid_full], c_disp_full[valid_full], 'bo', 
                markersize=6, label='Full data', alpha=0.7)
    if np.any(valid_rec):
        ax.plot(f_disp_rec[valid_rec], c_disp_rec[valid_rec], 'rs', 
                markersize=5, label='Reconstructed', alpha=0.7)
    
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Phase Velocity (m/s)')
    ax.set_title('Dispersion Curves')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 6)
    
    plt.tight_layout()
    plt.savefig('komega_fista_working.png', dpi=150)
    print("  Saved: komega_fista_working.png")
    
    print("\n" + "=" * 60)
    print("✓ Pipeline complete!")
    print("=" * 60)
    
    return u_full, u_recon, nmse, corr


if __name__ == "__main__":
    u_full, u_recon, nmse, corr = run_pipeline()
