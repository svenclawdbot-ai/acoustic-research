"""
k-ω Transform for Dispersion Extraction
========================================

Extract phase velocity dispersion curves from space-time wavefield data
using the k-ω (wavenumber-frequency) transform.

Method:
-------
1. Record wavefield u(x, t) at multiple spatial positions
2. Apply 2D FFT: U(k, ω) = ∫∫ u(x,t) exp(-i(kx - ωt)) dx dt
3. The dispersion relation appears as ridges in |U(k, ω)|²
4. Extract c(ω) = ω/k from peak locations

Advantages over two-receiver methods:
- Uses all spatial information (better SNR)
- Handles dispersive pulse spreading naturally
- No need for cross-correlation peak picking
- Separates forward/backward propagating waves

Author: Research Project — DSP Pipeline
Date: March 23, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d, maximum_filter
from scipy.signal import find_peaks
import warnings
warnings.filterwarnings('ignore')


class KOmegaExtractor:
    """
    k-ω transform for dispersion curve extraction from wavefield data.
    """
    
    def __init__(self, dx, dt):
        """
        Initialize k-ω extractor.
        
        Parameters:
        -----------
        dx : float
            Spatial sampling interval (m)
        dt : float
            Temporal sampling interval (s)
        """
        self.dx = dx
        self.dt = dt
        
    def apply_window(self, data, window_type='tukey'):
        """
        Apply 2D window to reduce spectral leakage.
        
        Parameters:
        -----------
        data : array (nx, nt)
            Space-time wavefield
        window_type : str
            'tukey', 'hann', or 'none'
        """
        nx, nt = data.shape
        
        if window_type == 'tukey':
            # Manual Tukey window implementation
            alpha = 0.2
            win_x = np.ones(nx)
            win_t = np.ones(nt)
            
            # Taper edges for x window
            taper_len_x = int(alpha * nx / 2)
            for i in range(taper_len_x):
                win_x[i] = 0.5 * (1 - np.cos(np.pi * i / taper_len_x))
                win_x[nx - 1 - i] = win_x[i]
            
            # Taper edges for t window
            taper_len_t = int(alpha * nt / 2)
            for i in range(taper_len_t):
                win_t[i] = 0.5 * (1 - np.cos(np.pi * i / taper_len_t))
                win_t[nt - 1 - i] = win_t[i]
                
        elif window_type == 'hann':
            win_x = np.hanning(nx)
            win_t = np.hanning(nt)
        elif window_type == 'none':
            return data
        else:
            raise ValueError(f"Unknown window: {window_type}")
        
        # 2D window (outer product)
        window_2d = np.outer(win_x, win_t)
        return data * window_2d
    
    def transform(self, data, window='tukey'):
        """
        Compute k-ω transform of wavefield data.
        
        Parameters:
        -----------
        data : array (nx, nt)
            Space-time wavefield u(x,t)
        window : str
            Window type for tapering
            
        Returns:
        --------
        k : array
            Wavenumbers (rad/m)
        omega : array
            Angular frequencies (rad/s)
        spectrum : array (nk, nomega)
            |U(k, ω)|² power spectrum
        """
        # Apply window
        data_windowed = self.apply_window(data, window)
        
        # 2D FFT (numpy uses opposite convention: fft2 does sum over last axis first)
        # We want: U(k, ω) = ∫∫ u(x,t) exp(-i(kx - ωt)) dx dt
        U = np.fft.fftshift(np.fft.fft2(data_windowed))
        
        # Power spectrum
        spectrum = np.abs(U)**2
        
        # Frequency and wavenumber axes
        nx, nt = data.shape
        k = np.fft.fftshift(np.fft.fftfreq(nx, self.dx)) * 2 * np.pi  # rad/m
        f = np.fft.fftshift(np.fft.fftfreq(nt, self.dt))  # Hz
        omega = 2 * np.pi * f  # rad/s
        
        # Only keep positive frequencies (causal)
        zero_freq_idx = len(omega) // 2
        spectrum = spectrum[:, zero_freq_idx:]
        k = k
        omega = omega[zero_freq_idx:]
        
        return k, omega, spectrum
    
    def extract_dispersion(self, data, freq_range=None, window='tukey',
                          smoothing_sigma=1.0, min_peak_height=0.1):
        """
        Extract dispersion curve from k-ω spectrum.
        
        Parameters:
        -----------
        data : array (nx, nt)
            Space-time wavefield
        freq_range : tuple (f_min, f_max)
            Frequency range to analyze (Hz)
        window : str
            Window type
        smoothing_sigma : float
            Gaussian smoothing sigma (in frequency bins)
        min_peak_height : float
            Minimum peak height relative to max
            
        Returns:
        --------
        freqs : array
            Frequencies (Hz)
        phase_velocities : array
            Phase velocities (m/s)
        k_axis : array
            Wavenumber axis
        omega_axis : array
            Frequency axis (rad/s)
        spectrum : array
            k-ω spectrum
        """
        k, omega, spectrum = self.transform(data, window)
        freqs = omega / (2 * np.pi)
        
        # Frequency range mask
        if freq_range is not None:
            f_min, f_max = freq_range
            mask = (freqs >= f_min) & (freqs <= f_max)
            freqs = freqs[mask]
            omega = omega[mask]
            spectrum = spectrum[:, mask]
        
        # Smooth spectrum along k for each frequency
        spectrum_smooth = np.zeros_like(spectrum)
        for i in range(spectrum.shape[1]):
            spectrum_smooth[:, i] = gaussian_filter1d(spectrum[:, i], smoothing_sigma)
        
        # Find peaks in k for each frequency
        phase_velocities = []
        valid_freqs = []
        
        for i, (f, om) in enumerate(zip(freqs, omega)):
            if om <= 0:  # Skip zero frequency
                continue
                
            k_slice = spectrum_smooth[:, i]
            
            # Only look at positive k (forward propagating)
            k_pos_mask = k > 0.1  # Avoid k=0
            if not np.any(k_pos_mask):
                continue
                
            k_pos = k[k_pos_mask]
            k_slice_pos = k_slice[k_pos_mask]
            
            if len(k_slice_pos) == 0 or np.max(k_slice_pos) == 0:
                continue
            
            # Normalize
            k_slice_norm = k_slice_pos / np.max(k_slice_pos)
            
            # Find peaks with minimum separation
            peaks, properties = find_peaks(k_slice_norm, height=min_peak_height, 
                                          distance=5, prominence=0.05)
            
            if len(peaks) > 0:
                # Select strongest peak
                peak_idx = peaks[np.argmax(properties['peak_heights'])]
                k_peak = k_pos[peak_idx]
                
                # Compute phase velocity
                c_p = om / k_peak
                
                # Sanity check: should be between 0.5 and 50 m/s for soft tissue
                if 0.5 <= c_p <= 50:
                    phase_velocities.append(c_p)
                    valid_freqs.append(f)
        
        return (np.array(valid_freqs), np.array(phase_velocities), 
                k, omega, spectrum_smooth)
    
    def plot_spectrum(self, k, omega, spectrum, extracted_freqs=None, 
                     extracted_c=None, theory_c=None, title='k-ω Spectrum'):
        """
        Visualize k-ω spectrum with extracted dispersion.
        
        Parameters:
        -----------
        k : array
            Wavenumbers (rad/m)
        omega : array
            Angular frequencies (rad/s)
        spectrum : array
            Power spectrum
        extracted_freqs, extracted_c : arrays
            Extracted dispersion curve
        theory_c : callable
            Function c(ω) for theoretical comparison
        title : str
            Plot title
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Plot 1: k-ω spectrum
        ax = axes[0]
        
        # Log scale for better dynamic range
        spectrum_log = 10 * np.log10(spectrum + 1e-10)
        
        # Limit k range for visualization (positive k, reasonable range)
        k_pos_mask = k >= 0
        k_pos = k[k_pos_mask]
        spectrum_pos = spectrum_log[k_pos_mask, :]
        
        # Also limit to reasonable k values
        k_max_vis = 150  # rad/m (adjust as needed)
        k_vis_mask = k_pos <= k_max_vis
        k_vis = k_pos[k_vis_mask]
        spectrum_vis = spectrum_pos[k_vis_mask, :]
        
        extent = [0, omega[-1]/(2*np.pi), k_vis[0], k_vis[-1]]
        im = ax.imshow(spectrum_vis, aspect='auto', origin='lower', extent=extent,
                      cmap='viridis', vmin=np.percentile(spectrum_vis, 5),
                      vmax=np.percentile(spectrum_vis, 95))
        
        # Overlay extracted dispersion
        if extracted_freqs is not None and extracted_c is not None:
            # Convert c to k: k = ω/c
            omega_ext = 2 * np.pi * extracted_freqs
            k_ext = omega_ext / extracted_c
            k_ext_mask = (k_ext >= k_vis[0]) & (k_ext <= k_vis[-1])
            ax.plot(extracted_freqs[k_ext_mask], k_ext[k_ext_mask], 
                   'ro', markersize=6, label='Extracted')
        
        # Overlay theoretical dispersion
        if theory_c is not None:
            omega_theory = np.linspace(omega[1], omega[-1], 200)
            f_theory = omega_theory / (2 * np.pi)
            c_theory = theory_c(f_theory)
            k_theory = omega_theory / c_theory
            k_theory_mask = (k_theory >= k_vis[0]) & (k_theory <= k_vis[-1])
            ax.plot(f_theory[k_theory_mask], k_theory[k_theory_mask],
                   'w--', linewidth=2, label='Theory')
        
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Wavenumber k (rad/m)')
        ax.set_title(title)
        ax.legend(loc='upper left')
        plt.colorbar(im, ax=ax, label='Power (dB)')
        
        # Plot 2: Phase velocity dispersion
        ax = axes[1]
        
        if extracted_freqs is not None and extracted_c is not None:
            ax.plot(extracted_freqs, extracted_c, 'bo-', markersize=8,
                   linewidth=1.5, label='k-ω Extracted')
        
        if theory_c is not None:
            f_theory = np.linspace(omega[1]/(2*np.pi), omega[-1]/(2*np.pi), 200)
            ax.plot(f_theory, theory_c(f_theory), 'r--', linewidth=2,
                   label='Zener Theory')
        
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Phase Velocity (m/s)')
        ax.set_title('Dispersion Curve')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig


def extract_dispersion_from_simulation(simulator_output, dx, dt, 
                                       freq_range=(50, 400), **kwargs):
    """
    Convenience function to extract dispersion from simulation output.
    
    Parameters:
    -----------
    simulator_output : list of arrays
        Time history of wavefield [u(x,t0), u(x,t1), ...]
    dx : float
        Spatial step
    dt : float
        Time step between stored frames
    freq_range : tuple
        (f_min, f_max) in Hz
    
    Returns:
    --------
    dict with freqs, phase_velocities, k, omega, spectrum, extractor
    """
    # Convert list of 1D arrays to 2D array (nx, nt)
    data = np.array(simulator_output).T
    
    extractor = KOmegaExtractor(dx, dt)
    
    freqs, c_p, k, omega, spectrum = extractor.extract_dispersion(
        data, freq_range=freq_range, **kwargs
    )
    
    return {
        'freqs': freqs,
        'phase_velocities': c_p,
        'k': k,
        'omega': omega,
        'spectrum': spectrum,
        'extractor': extractor,
        'data': data
    }


def test_komega_extraction():
    """
    Test k-ω extraction on synthetic data and 2D simulation.
    """
    print("=" * 70)
    print("k-ω TRANSFORM TEST")
    print("=" * 70)
    
    # Test 1: Synthetic non-dispersive wave
    print("\n[Test 1] Synthetic non-dispersive wave")
    print("-" * 50)
    
    nx, nt = 256, 512
    dx, dt = 0.002, 0.0005
    c = 3.0  # Wave speed
    f0 = 100
    
    x = np.arange(nx) * dx
    t = np.arange(nt) * dt
    
    # Create a simple propagating pulse with narrow bandwidth
    # Use several frequency components that travel at same speed
    data = np.zeros((nx, nt))
    freqs_signal = [80, 100, 120]
    
    for f in freqs_signal:
        omega = 2 * np.pi * f
        k = omega / c  # Non-dispersive: k = omega/c
        
        # Create plane wave
        for i, xi in enumerate(x):
            for j, tj in enumerate(t):
                # Gaussian envelope traveling wave
                envelope = np.exp(-((xi - c*tj - 0.1)**2) / (2*0.05**2))
                data[i, j] += envelope * np.cos(k*xi - omega*tj)
    
    extractor = KOmegaExtractor(dx, dt)
    freqs, c_p, _, _, _ = extractor.extract_dispersion(
        data, freq_range=(50, 200), min_peak_height=0.05
    )
    
    print(f"  Expected: c = {c:.2f} m/s")
    if len(c_p) > 0:
        print(f"  Extracted: c = {np.mean(c_p):.2f} ± {np.std(c_p):.2f} m/s")
        print(f"  Error: {100*abs(np.mean(c_p)-c)/c:.1f}%")
    
    # Test 2: 2D Zener simulation
    print("\n[Test 2] 2D Zener simulation")
    print("-" * 50)
    
    import sys
    sys.path.insert(0, '/home/james/.openclaw/workspace')
    from shear_wave_2d_zener import ShearWave2DZener
    
    # Parameters
    G_r = 5000
    G_inf = 8000
    tau_sigma = 0.001
    rho = 1000
    f0 = 100
    
    # Setup
    c_inf = np.sqrt(G_inf / rho)
    wavelength = c_inf / f0
    dx = wavelength / 12
    nx = 120
    
    sim = ShearWave2DZener(nx=nx, ny=nx, dx=dx, rho=rho, G_r=G_r, G_inf=G_inf,
                           tau_sigma=tau_sigma, bc_type='mur1')
    
    dt = sim.dt
    n_steps = int(0.04 / dt)
    
    # Source position
    source_pos = (nx // 4, nx // 2)
    
    # Record line through source (x-direction)
    line_history = []
    
    print(f"  Running 2D simulation: {n_steps} steps...")
    for n in range(n_steps):
        t = n * dt
        if n * dt < 3.0 / f0:
            sim.add_source(t, source_type='tone_burst', f0=f0,
                          location=source_pos, amplitude=2e-5)
        sim.step()
        
        if n % 5 == 0:  # Subsample for storage
            line_history.append(sim.uy[:, nx//2].copy())
    
    print(f"  Recorded {len(line_history)} frames")
    
    # Extract dispersion
    data = np.array(line_history).T
    dt_record = dt * 5
    
    extractor = KOmegaExtractor(dx, dt_record)
    freqs, c_p, k, omega, spectrum = extractor.extract_dispersion(
        data, freq_range=(50, 300), smoothing_sigma=2.0
    )
    
    # Theoretical
    def zener_c(f):
        omega = 2 * np.pi * f
        G_star = G_r + (G_inf - G_r) / (1 + 1j * omega * tau_sigma)
        G_mag = np.abs(G_star)
        delta = np.angle(G_star)
        return np.sqrt(2 * G_mag / (rho * (1 + np.cos(delta))))
    
    print(f"\n  Extracted {len(c_p)} frequency points")
    if len(c_p) > 0:
        print(f"  Phase velocity range: {c_p.min():.2f} - {c_p.max():.2f} m/s")
        print(f"  Theory range: {zener_c(50):.2f} - {zener_c(300):.2f} m/s")
    
    # Plot
    fig = extractor.plot_spectrum(k, omega, spectrum, freqs, c_p, zener_c,
                                  title='2D Zener: k-ω Spectrum')
    plt.savefig('komega_2d_zener_test.png', dpi=150, bbox_inches='tight')
    print("\n  ✓ Saved: komega_2d_zener_test.png")
    plt.show()
    
    return freqs, c_p


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("k-ω TRANSFORM FOR DISPERSION EXTRACTION")
    print("=" * 70)
    
    test_komega_extraction()
    
    print("\n" + "=" * 70)
    print("k-ω extraction complete!")
    print("=" * 70)
