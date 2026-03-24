"""
Robust k-ω Dispersion Extraction
=================================

Production-ready dispersion extraction from FDTD simulations.
Optimized for 2D Zener viscoelastic shear waves.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert, find_peaks
import sys
sys.path.insert(0, '/home/james/.openclaw/workspace')


def run_2d_simulation_for_komega(G_r=5000, G_inf=8000, tau_sigma=0.001,
                                  f_center=150, nx=200, duration=0.05):
    """
    Run 2D simulation optimized for k-ω analysis.
    
    Key: Use larger domain, longer duration, multi-frequency excitation.
    """
    from shear_wave_2d_zener import ShearWave2DZener
    
    rho = 1000
    c_inf = np.sqrt(G_inf / rho)
    c_r = np.sqrt(G_r / rho)
    
    # Grid: at least 10 wavelengths at lowest frequency
    f_min = 50
    wavelength_max = c_r / f_min
    dx = wavelength_max / 15
    
    sim = ShearWave2DZener(nx=nx, ny=nx, dx=dx, rho=rho, G_r=G_r, G_inf=G_inf,
                           tau_sigma=tau_sigma, bc_type='mur1')
    
    dt = sim.dt
    n_steps = int(duration / dt)
    
    print(f"k-ω optimized 2D sim:")
    print(f"  Grid: {nx}×{nx}, dx={dx*1000:.2f} mm")
    print(f"  Duration: {duration*1000:.1f} ms, {n_steps} steps")
    print(f"  Wavelengths across domain: {nx*dx/wavelength_max:.1f}")
    
    # Multi-frequency chirp source
    source_pos = (nx // 4, nx // 2)
    
    # Record center line
    line_history = []
    record_interval = 3  # Save every 3 steps
    
    for n in range(n_steps):
        t = n * dt
        
        # Chirp source: frequency sweeps from 50 to 300 Hz
        # This excites all frequencies for clean k-ω spectrum
        if t < 0.015:  # 15 ms chirp
            f_inst = 50 + (300 - 50) * (t / 0.015)
            envelope = np.exp(-(t - 0.0075)**2 / (2*0.003**2))
            amplitude = 2e-5 * envelope
            sim.add_source(t, source_type='tone_burst', f0=f_inst,
                          location=source_pos, amplitude=amplitude)
        
        sim.step()
        
        if n % record_interval == 0:
            line_history.append(sim.uy[:, nx//2].copy())
    
    data = np.array(line_history).T
    dt_eff = dt * record_interval
    
    print(f"  Recorded {data.shape[1]} time frames")
    print(f"  Data shape: {data.shape}")
    
    return data, dx, dt_eff, sim


def komega_transform(data, dx, dt):
    """
    Compute k-ω transform with proper normalization.
    
    Returns power spectrum |U(k, ω)|²
    """
    nx, nt = data.shape
    
    # Tukey window in space and time
    def tukey_window(n, alpha=0.1):
        w = np.ones(n)
        taper = int(alpha * n / 2)
        for i in range(taper):
            w[i] = 0.5 * (1 - np.cos(np.pi * i / taper))
            w[n-1-i] = w[i]
        return w
    
    win_x = tukey_window(nx, 0.15)
    win_t = tukey_window(nt, 0.05)
    window = np.outer(win_x, win_t)
    data_w = data * window
    
    # 2D FFT with proper shift
    U = np.fft.fftshift(np.fft.fft2(data_w))
    spectrum = np.abs(U)**2
    
    # Frequency/wavenumber axes (only positive frequencies)
    k_full = np.fft.fftshift(np.fft.fftfreq(nx, dx)) * 2 * np.pi
    f_full = np.fft.fftshift(np.fft.fftfreq(nt, dt))
    
    # Keep only positive frequencies
    zero_f_idx = len(f_full) // 2
    f_pos = f_full[zero_f_idx:]
    spectrum_pos = spectrum[:, zero_f_idx:]
    
    return k_full, f_pos, spectrum_pos


def extract_dispersion_ridge(k, f, spectrum, f_range=(50, 300), 
                              k_min=5, k_max=150):
    """
    Extract dispersion curve by finding ridge in k-ω spectrum.
    
    Uses maximum search along k for each frequency.
    """
    # Smooth spectrum slightly
    from scipy.ndimage import gaussian_filter1d
    spectrum_smooth = gaussian_filter1d(spectrum, sigma=1.0, axis=0)
    
    # Frequency mask
    f_mask = (f >= f_range[0]) & (f <= f_range[1])
    f_valid = f[f_mask]
    
    c_extracted = []
    f_extracted = []
    
    for i, freq in enumerate(f_valid):
        idx = np.where(f == freq)[0][0]
        spec_slice = spectrum_smooth[:, idx]
        
        # Only look in valid k range
        k_mask = (k > k_min) & (k < k_max)
        if not np.any(k_mask):
            continue
        
        k_valid = k[k_mask]
        spec_valid = spec_slice[k_mask]
        
        # Find peak
        peak_idx = np.argmax(spec_valid)
        k_peak = k_valid[peak_idx]
        
        # Compute phase velocity
        omega = 2 * np.pi * freq
        c_p = omega / k_peak
        
        # Sanity check
        if 1.0 < c_p < 10.0:
            c_extracted.append(c_p)
            f_extracted.append(freq)
    
    return np.array(f_extracted), np.array(c_extracted)


def zener_theory_c(f, G_r, G_inf, tau_sigma, rho=1000):
    """Theoretical Zener phase velocity."""
    omega = 2 * np.pi * f
    G_star = G_r + (G_inf - G_r) / (1 + 1j * omega * tau_sigma)
    G_mag = np.abs(G_star)
    delta = np.angle(G_star)
    return np.sqrt(2 * G_mag / (rho * (1 + np.cos(delta))))


def visualize_komega(k, f, spectrum, f_extracted, c_extracted, 
                     G_r, G_inf, tau_sigma, title="k-ω Analysis"):
    """Create comprehensive k-ω visualization."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 1. k-ω spectrum
    ax = axes[0, 0]
    
    # Log scale and limit k range
    spectrum_log = 10 * np.log10(spectrum + 1e-10)
    k_mask = k >= 0
    k_pos = k[k_mask]
    spec_pos = spectrum_log[k_mask, :]
    
    # Limit k for visualization
    k_vis_max = 100
    k_vis_mask = k_pos <= k_vis_max
    k_vis = k_pos[k_vis_mask]
    spec_vis = spec_pos[k_vis_mask, :]
    
    vmax = np.percentile(spec_vis, 99)
    vmin = np.percentile(spec_vis, 10)
    
    extent = [f[0], f[-1], k_vis[0], k_vis[-1]]
    im = ax.imshow(spec_vis, aspect='auto', origin='lower', extent=extent,
                  cmap='jet', vmin=vmin, vmax=vmax)
    
    # Overlay extracted dispersion
    if len(f_extracted) > 0:
        omega_ext = 2 * np.pi * f_extracted
        k_ext = omega_ext / c_extracted
        ax.plot(f_extracted, k_ext, 'wo', markersize=6, markerfacecolor='none',
               markeredgewidth=2, label='Extracted')
    
    # Overlay theory
    f_theory = np.linspace(50, 300, 100)
    c_theory = zener_theory_c(f_theory, G_r, G_inf, tau_sigma)
    k_theory = 2 * np.pi * f_theory / c_theory
    k_theory_mask = k_theory <= k_vis_max
    ax.plot(f_theory[k_theory_mask], k_theory[k_theory_mask], 
           'w--', linewidth=2, label='Theory')
    
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Wavenumber k (rad/m)')
    ax.set_title('k-ω Spectrum')
    ax.legend(loc='upper left')
    plt.colorbar(im, ax=ax, label='Power (dB)')
    
    # 2. Dispersion curve
    ax = axes[0, 1]
    
    if len(f_extracted) > 0:
        ax.plot(f_extracted, c_extracted, 'bo-', markersize=8, 
               linewidth=2, label='k-ω Extracted')
    
    ax.plot(f_theory, c_theory, 'r--', linewidth=2, label='Zener Theory')
    
    # Reference lines
    c_r = np.sqrt(G_r / 1000)
    c_inf = np.sqrt(G_inf / 1000)
    ax.axhline(y=c_r, color='gray', linestyle=':', alpha=0.5, label=f'c_r={c_r:.1f}')
    ax.axhline(y=c_inf, color='gray', linestyle='-.', alpha=0.5, label=f'c_∞={c_inf:.1f}')
    
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Phase Velocity (m/s)')
    ax.set_title('Dispersion Curve')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(50, 300)
    
    # 3. Error analysis
    ax = axes[1, 0]
    
    if len(f_extracted) > 0:
        c_theory_extracted = zener_theory_c(f_extracted, G_r, G_inf, tau_sigma)
        error = 100 * (c_extracted - c_theory_extracted) / c_theory_extracted
        
        ax.plot(f_extracted, error, 'go-', markersize=8)
        ax.axhline(y=0, color='r', linestyle='--')
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Error (%)')
        ax.set_title('Extraction Error')
        ax.grid(True, alpha=0.3)
    else:
        ax.text(0.5, 0.5, 'No data extracted', ha='center', va='center',
               transform=ax.transAxes)
    
    # 4. Parameters
    ax = axes[1, 1]
    ax.axis('off')
    
    param_text = f"""
    Zener Model Parameters:
    ----------------------
    G_r (relaxed) = {G_r} Pa
    G_∞ (unrelaxed) = {G_inf} Pa
    τ_σ = {tau_sigma*1000:.2f} ms
    
    Wave Speeds:
    -----------
    c_r = {c_r:.2f} m/s
    c_∞ = {c_inf:.2f} m/s
    
    Extraction:
    ----------
    Points extracted: {len(f_extracted)}
    Mean error: {np.mean(np.abs(error)):.1f}% (if extracted)
    """
    ax.text(0.1, 0.5, param_text, transform=ax.transAxes, fontsize=11,
           verticalalignment='center', fontfamily='monospace',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.suptitle(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    return fig


def main():
    """Run complete k-ω extraction pipeline."""
    print("=" * 70)
    print("k-ω DISPERSION EXTRACTION PIPELINE")
    print("=" * 70)
    
    # Parameters
    G_r = 5000
    G_inf = 8000
    tau_sigma = 0.001
    
    print(f"\nZener: G_r={G_r}, G_∞={G_inf}, τ_σ={tau_sigma*1000:.1f} ms")
    print(f"Theory: c_r={np.sqrt(G_r/1000):.2f}, c_∞={np.sqrt(G_inf/1000):.2f} m/s")
    
    # Run simulation
    print("\n[1] Running 2D simulation...")
    data, dx, dt, sim = run_2d_simulation_for_komega(
        G_r=G_r, G_inf=G_inf, tau_sigma=tau_sigma,
        f_center=150, nx=200, duration=0.05
    )
    
    # k-ω transform
    print("\n[2] Computing k-ω transform...")
    k, f, spectrum = komega_transform(data, dx, dt)
    print(f"  k range: {k.min():.1f} to {k.max():.1f} rad/m")
    print(f"  f range: {f.min():.1f} to {f.max():.1f} Hz")
    
    # Extract dispersion
    print("\n[3] Extracting dispersion ridge...")
    f_extracted, c_extracted = extract_dispersion_ridge(
        k, f, spectrum, f_range=(60, 280)
    )
    print(f"  Extracted {len(f_extracted)} frequency points")
    
    if len(f_extracted) > 0:
        print(f"  Phase velocity range: {c_extracted.min():.2f} - {c_extracted.max():.2f} m/s")
        
        # Compute error
        c_theory_extracted = zener_theory_c(f_extracted, G_r, G_inf, tau_sigma)
        mean_error = np.mean(np.abs(100 * (c_extracted - c_theory_extracted) / c_theory_extracted))
        print(f"  Mean error: {mean_error:.1f}%")
    
    # Visualize
    print("\n[4] Generating plots...")
    fig = visualize_komega(k, f, spectrum, f_extracted, c_extracted,
                          G_r, G_inf, tau_sigma)
    
    plt.savefig('komega_production_result.png', dpi=150, bbox_inches='tight')
    print("  ✓ Saved: komega_production_result.png")
    plt.show()
    
    print("\n" + "=" * 70)
    print("k-ω extraction complete!")
    print("=" * 70)
    
    return f_extracted, c_extracted


if __name__ == "__main__":
    main()
