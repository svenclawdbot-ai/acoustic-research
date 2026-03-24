"""
k-ω Dispersion Extraction — Multi-Frequency Method
===================================================

More reliable approach: Run separate simulations at each frequency,
record full space-time history, and extract phase velocity via k-ω.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert
import sys
sys.path.insert(0, '/home/james/.openclaw/workspace')


def simulate_single_frequency(f0, G_r=5000, G_inf=8000, tau_sigma=0.001,
                               nx=256, duration=0.06):
    """
    Run 2D simulation at single frequency, optimized for k-ω.
    """
    from shear_wave_2d_zener import ShearWave2DZener
    
    rho = 1000
    c_r = np.sqrt(G_r / rho)
    c_inf = np.sqrt(G_inf / rho)
    
    # Grid: ensure at least 10 wavelengths
    wavelength = c_r / f0
    dx = wavelength / 12  # 12 points per wavelength
    
    sim = ShearWave2DZener(nx=nx, ny=nx, dx=dx, rho=rho, G_r=G_r, G_inf=G_inf,
                           tau_sigma=tau_sigma, bc_type='mur1')
    
    dt = sim.dt
    n_steps = int(duration / dt)
    
    source_pos = (nx // 6, nx // 2)  # Source at 1/6 point
    
    # Record full wavefield along center line
    record_interval = 2
    line_history = []
    
    # CW-like excitation: many cycles
    source_duration = int(4.0 / f0 / dt)  # 4 cycles
    
    for n in range(n_steps):
        t = n * dt
        
        # Tone burst source
        if n < source_duration:
            sim.add_source(t, source_type='tone_burst', f0=f0,
                          location=source_pos, amplitude=1e-5)
        
        sim.step()
        
        if n % record_interval == 0:
            line_history.append(sim.uy[:, nx//2].copy())
    
    data = np.array(line_history).T  # (nx, nt)
    dt_eff = dt * record_interval
    
    return data, dx, dt_eff, sim


def extract_phase_velocity_komega(data, dx, dt, f_target):
    """
    Extract phase velocity at specific frequency using k-ω peak.
    """
    nx, nt = data.shape
    
    # Tukey window
    def tukey(n, alpha=0.1):
        w = np.ones(n)
        t = int(alpha * n / 2)
        for i in range(t):
            w[i] = 0.5 * (1 - np.cos(np.pi * i / t))
            w[n-1-i] = w[i]
        return w
    
    window = np.outer(tukey(nx, 0.15), tukey(nt, 0.05))
    data_w = data * window
    
    # 2D FFT
    U = np.fft.fftshift(np.fft.fft2(data_w))
    spectrum = np.abs(U)**2
    
    # Axes
    k = np.fft.fftshift(np.fft.fftfreq(nx, dx)) * 2 * np.pi
    f = np.fft.fftshift(np.fft.fftfreq(nt, dt))
    
    # Keep positive frequencies
    f_pos_idx = len(f) // 2
    f_pos = f[f_pos_idx:]
    spectrum_pos = spectrum[:, f_pos_idx:]
    
    # Find frequency bin closest to target
    f_idx = np.argmin(np.abs(f_pos - f_target))
    actual_f = f_pos[f_idx]
    
    # Extract k-spectrum at this frequency
    k_spec = spectrum_pos[:, f_idx]
    
    # Find peak in positive k
    k_pos_mask = k > 5  # Avoid k=0
    k_pos = k[k_pos_mask]
    spec_pos = k_spec[k_pos_mask]
    
    if len(k_pos) == 0 or np.max(spec_pos) == 0:
        return None, None, None
    
    peak_idx = np.argmax(spec_pos)
    k_peak = k_pos[peak_idx]
    
    omega = 2 * np.pi * actual_f
    c_p = omega / k_peak
    
    return actual_f, c_p, k_peak


def run_multifrequency_extraction(frequencies, G_r=5000, G_inf=8000, tau_sigma=0.001):
    """
    Run extraction at multiple frequencies.
    """
    print("=" * 70)
    print("MULTI-FREQUENCY k-ω EXTRACTION")
    print("=" * 70)
    print(f"Zener: G_r={G_r}, G_∞={G_inf}, τ_σ={tau_sigma*1000:.1f} ms")
    print(f"Frequencies: {frequencies} Hz\n")
    
    results = []
    
    for f0 in frequencies:
        print(f"Running f = {f0} Hz...")
        
        data, dx, dt, sim = simulate_single_frequency(
            f0, G_r, G_inf, tau_sigma, nx=256, duration=0.06
        )
        
        f_meas, c_p, k_peak = extract_phase_velocity_komega(data, dx, dt, f0)
        
        if f_meas is not None:
            results.append({
                'f_target': f0,
                'f_meas': f_meas,
                'c_p': c_p,
                'k': k_peak
            })
            print(f"  ✓ c_p = {c_p:.2f} m/s at f = {f_meas:.1f} Hz")
        else:
            print(f"  ✗ Failed to extract")
    
    return results


def zener_c(f, G_r, G_inf, tau_sigma, rho=1000):
    """Theoretical Zener phase velocity."""
    omega = 2 * np.pi * f
    G_star = G_r + (G_inf - G_r) / (1 + 1j * omega * tau_sigma)
    G_mag = np.abs(G_star)
    delta = np.angle(G_star)
    return np.sqrt(2 * G_mag / (rho * (1 + np.cos(delta))))


def visualize_results(results, G_r, G_inf, tau_sigma):
    """Plot comparison."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Extract arrays
    freqs = [r['f_meas'] for r in results]
    c_extracted = [r['c_p'] for r in results]
    
    # Theory curve
    f_theory = np.linspace(40, 350, 100)
    c_theory = zener_c(f_theory, G_r, G_inf, tau_sigma)
    
    # Plot 1: Dispersion curve
    ax = axes[0]
    ax.plot(freqs, c_extracted, 'bo-', markersize=10, linewidth=2,
           label='k-ω Extracted')
    ax.plot(f_theory, c_theory, 'r--', linewidth=2, label='Zener Theory')
    
    c_r = np.sqrt(G_r / 1000)
    c_inf = np.sqrt(G_inf / 1000)
    ax.axhline(y=c_r, color='gray', linestyle=':', alpha=0.5, label=f'c_r={c_r:.2f}')
    ax.axhline(y=c_inf, color='gray', linestyle='-.', alpha=0.5, label=f'c_∞={c_inf:.2f}')
    
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Phase Velocity (m/s)')
    ax.set_title('Zener Dispersion: k-ω vs Theory')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 2: Error
    ax = axes[1]
    
    c_theory_at_freqs = zener_c(np.array(freqs), G_r, G_inf, tau_sigma)
    error = 100 * (np.array(c_extracted) - c_theory_at_freqs) / c_theory_at_freqs
    
    ax.plot(freqs, error, 'go-', markersize=10, linewidth=2)
    ax.axhline(y=0, color='r', linestyle='--', alpha=0.5)
    ax.axhline(y=10, color='gray', linestyle=':', alpha=0.3)
    ax.axhline(y=-10, color='gray', linestyle=':', alpha=0.3)
    
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Error (%)')
    ax.set_title(f'Extraction Error (mean={np.mean(np.abs(error)):.1f}%)')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('komega_multifreq_result.png', dpi=150)
    print("\n✓ Saved: komega_multifreq_result.png")
    plt.show()
    
    # Print table
    print("\n" + "=" * 70)
    print("RESULTS TABLE")
    print("=" * 70)
    print(f"{'Freq (Hz)':<12} {'Extracted c_p':<15} {'Theory c_p':<15} {'Error %':<10}")
    print("-" * 70)
    for r in results:
        f = r['f_meas']
        c = r['c_p']
        ct = zener_c(f, G_r, G_inf, tau_sigma)
        err = 100 * (c - ct) / ct
        print(f"{f:<12.1f} {c:<15.2f} {ct:<15.2f} {err:<10.1f}")
    print("=" * 70)


def main():
    """Run multi-frequency extraction."""
    # Test frequencies
    frequencies = [50, 100, 150, 200, 250]
    
    results = run_multifrequency_extraction(
        frequencies, G_r=5000, G_inf=8000, tau_sigma=0.001
    )
    
    if len(results) > 0:
        visualize_results(results, 5000, 8000, 0.001)
    
    print("\n" + "=" * 70)
    print("Multi-frequency k-ω extraction complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
