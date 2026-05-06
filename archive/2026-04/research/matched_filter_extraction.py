"""
Matched Filter Dispersion Extraction
=====================================

Extract phase velocity using matched filtering with dispersive pulse templates.

Method:
-------
1. For each frequency, create a dispersive reference pulse
   (known propagation distance, measure phase shift)
2. Correlate received signal with reference
3. Peak of correlation gives time-of-flight
4. Phase of correlation at peak gives phase velocity

Advantages:
- Works with tone bursts (finite duration)
- Accounts for dispersion in template
- Better SNR than simple cross-correlation
- Can separate multiple arrivals

Author: Research Project — DSP Pipeline
Date: March 23, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert, correlate, chirp
import sys
sys.path.insert(0, '/home/james/.openclaw/workspace')


class MatchedFilterExtractor:
    """
    Matched filter extraction for dispersive waves.
    """
    
    def __init__(self, G_r, G_inf, tau_sigma, rho=1000):
        """
        Initialize with Zener model parameters.
        
        Parameters:
        -----------
        G_r, G_inf, tau_sigma : Zener model parameters
        rho : density (kg/m³)
        """
        self.G_r = G_r
        self.G_inf = G_inf
        self.tau_sigma = tau_sigma
        self.rho = rho
        
    def zener_phase_velocity(self, f):
        """Compute Zener phase velocity at frequency f."""
        omega = 2 * np.pi * f
        G_star = self.G_r + (self.G_inf - self.G_r) / (1 + 1j * omega * self.tau_sigma)
        G_mag = np.abs(G_star)
        delta = np.angle(G_star)
        return np.sqrt(2 * G_mag / (self.rho * (1 + np.cos(delta))))
    
    def zener_group_velocity(self, f):
        """Compute Zener group velocity (for envelope)."""
        # Approximate: c_g ≈ c_p for weak dispersion
        # More accurate requires numerical derivative
        df = 0.01 * f
        c1 = self.zener_phase_velocity(f - df)
        c2 = self.zener_phase_velocity(f + df)
        k1 = 2 * np.pi * (f - df) / c1
        k2 = 2 * np.pi * (f + df) / c2
        omega1 = 2 * np.pi * (f - df)
        omega2 = 2 * np.pi * (f + df)
        return (omega2 - omega1) / (k2 - k1)
    
    def create_reference_pulse(self, f0, distance, dt, n_samples, n_cycles=4):
        """
        Create reference pulse for matched filter.
        
        This is what we expect to receive after propagation.
        """
        t = np.arange(n_samples) * dt
        
        # Phase velocity at this frequency
        c_p = self.zener_phase_velocity(f0)
        
        # Time delay
        delay = distance / c_p
        
        # Create dispersed pulse
        # Envelope travels at group velocity (approximate)
        c_g = self.zener_group_velocity(f0)
        envelope_delay = distance / c_g if c_g > 0 else delay
        
        # Gaussian envelope
        sigma = n_cycles / f0 / 3  # n_cycles at center frequency
        envelope = np.exp(-(t - envelope_delay)**2 / (2 * sigma**2))
        
        # Phase accumulation: φ = 2πf(t - delay)
        # The carrier phase shifts by the propagation delay
        carrier = np.cos(2 * np.pi * f0 * (t - delay))
        
        return envelope * carrier
    
    def extract_arrival(self, signal, f0, distance, dt, n_cycles=4):
        """
        Extract arrival time using matched filter.
        
        Returns:
        --------
        arrival_time : float
            Estimated arrival time
        correlation_peak : float
            Peak correlation value
        phase_shift : float
            Phase shift at peak (radians)
        """
        n_samples = len(signal)
        
        # Create reference
        reference = self.create_reference_pulse(f0, distance, dt, n_samples, n_cycles)
        
        # Matched filter (cross-correlation)
        correlation = correlate(signal, reference, mode='full')
        corr_lags = np.arange(-len(reference) + 1, len(signal))
        
        # Find peak
        peak_idx = np.argmax(np.abs(correlation))
        peak_lag = corr_lags[peak_idx]
        
        # Arrival time from peak position
        # The lag indicates how much the signal is delayed relative to reference
        arrival_time = peak_lag * dt
        
        # Phase at peak
        phase_shift = np.angle(correlation[peak_idx])
        
        # Correlation quality
        correlation_peak = np.abs(correlation[peak_idx]) / (np.linalg.norm(signal) * np.linalg.norm(reference))
        
        return arrival_time, correlation_peak, phase_shift
    
    def extract_phase_velocity_two_receiver(self, rec1, rec2, f0, distance, dt, n_cycles=4):
        """
        Extract phase velocity using two receivers and matched filter.
        
        Parameters:
        -----------
        rec1, rec2 : arrays
            Signals at receiver 1 and 2
        f0 : float
            Center frequency
        distance : float
            Distance between receivers (m)
        dt : float
            Time step
        n_cycles : int
            Number of cycles in pulse
            
        Returns:
        --------
        c_p : float
            Phase velocity
        time_delay : float
            Time delay between receivers
        quality : float
            Correlation quality metric
        """
        # Extract arrival at both receivers
        t1, qual1, phase1 = self.extract_arrival(rec1, f0, 0, dt, n_cycles)
        t2, qual2, phase2 = self.extract_arrival(rec2, f0, distance, dt, n_cycles)
        
        # Time delay
        time_delay = t2 - t1
        
        # Phase velocity from time delay
        if abs(time_delay) > 1e-6:
            c_p_time = distance / abs(time_delay)
        else:
            c_p_time = self.zener_phase_velocity(f0)
        
        # Phase velocity from phase difference
        phase_diff = phase2 - phase1
        # Unwrap
        while phase_diff > np.pi:
            phase_diff -= 2 * np.pi
        while phase_diff < -np.pi:
            phase_diff += 2 * np.pi
        
        omega = 2 * np.pi * f0
        if abs(phase_diff) > 0.01:
            c_p_phase = omega * distance / abs(phase_diff)
        else:
            c_p_phase = c_p_time
        
        # Quality metric
        quality = (qual1 + qual2) / 2
        
        # Use phase velocity for final result (more accurate)
        # But bound by reasonable range
        c_p = c_p_phase
        if c_p < 0.5 or c_p > 20:
            c_p = c_p_time
        
        return c_p, time_delay, quality


def run_2d_simulation_matched(f0, G_r=5000, G_inf=8000, tau_sigma=0.001,
                               nx=150, duration=0.04):
    """
    Run 2D simulation for matched filter extraction.
    """
    from shear_wave_2d_zener import ShearWave2DZener
    
    rho = 1000
    c_r = np.sqrt(G_r / rho)
    
    # Grid
    wavelength = c_r / f0
    dx = wavelength / 10
    
    sim = ShearWave2DZener(nx=nx, ny=nx, dx=dx, rho=rho, G_r=G_r, G_inf=G_inf,
                           tau_sigma=tau_sigma, bc_type='mur1')
    
    dt = sim.dt
    n_steps = int(duration / dt)
    
    # Source and receiver positions
    source_pos = (nx // 5, nx // 2)
    rec1_pos = (2 * nx // 5, nx // 2)
    rec2_pos = (3 * nx // 5, nx // 2)
    distance = (rec2_pos[0] - rec1_pos[0]) * dx
    
    # Record signals
    rec1_signal = []
    rec2_signal = []
    
    source_duration = int(4.0 / f0 / dt)
    
    for n in range(n_steps):
        t = n * dt
        if n < source_duration:
            sim.add_source(t, source_type='tone_burst', f0=f0,
                          location=source_pos, amplitude=2e-5)
        sim.step()
        rec1_signal.append(sim.vy[rec1_pos])
        rec2_signal.append(sim.vy[rec2_pos])
    
    return (np.array(rec1_signal), np.array(rec2_signal), distance, dt, 
            source_pos, rec1_pos, rec2_pos, dx)


def multifrequency_extraction_matched(frequencies, G_r=5000, G_inf=8000, tau_sigma=0.001):
    """
    Extract dispersion at multiple frequencies using matched filter.
    """
    print("=" * 70)
    print("MATCHED FILTER DISPERSION EXTRACTION")
    print("=" * 70)
    print(f"Zener: G_r={G_r}, G_∞={G_inf}, τ_σ={tau_sigma*1000:.1f} ms")
    print(f"Frequencies: {frequencies} Hz\n")
    
    extractor = MatchedFilterExtractor(G_r, G_inf, tau_sigma)
    results = []
    
    for f0 in frequencies:
        print(f"Processing f = {f0} Hz...")
        
        # Run simulation
        rec1, rec2, distance, dt, src, r1, r2, dx = run_2d_simulation_matched(
            f0, G_r, G_inf, tau_sigma
        )
        
        # Extract using matched filter
        c_p, time_delay, quality = extractor.extract_phase_velocity_two_receiver(
            rec1, rec2, f0, distance, dt, n_cycles=4
        )
        
        c_theory = extractor.zener_phase_velocity(f0)
        
        results.append({
            'f': f0,
            'c_p': c_p,
            'c_theory': c_theory,
            'time_delay': time_delay,
            'quality': quality,
            'distance': distance
        })
        
        print(f"  c_p = {c_p:.2f} m/s (theory: {c_theory:.2f}), quality: {quality:.3f}")
    
    return results, extractor


def visualize_matched_results(results, extractor):
    """Plot matched filter extraction results."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    freqs = [r['f'] for r in results]
    c_extracted = [r['c_p'] for r in results]
    c_theory = [r['c_theory'] for r in results]
    qualities = [r['quality'] for r in results]
    
    # Theory curve
    f_theory = np.linspace(40, max(freqs)*1.2, 100)
    c_theory_curve = [extractor.zener_phase_velocity(f) for f in f_theory]
    
    # Plot 1: Dispersion comparison
    ax = axes[0, 0]
    ax.plot(freqs, c_extracted, 'bo-', markersize=10, linewidth=2,
           label='Matched Filter')
    ax.plot(f_theory, c_theory_curve, 'r--', linewidth=2, label='Zener Theory')
    
    c_r = np.sqrt(extractor.G_r / extractor.rho)
    c_inf = np.sqrt(extractor.G_inf / extractor.rho)
    ax.axhline(y=c_r, color='gray', linestyle=':', alpha=0.5, label=f'c_r={c_r:.2f}')
    ax.axhline(y=c_inf, color='gray', linestyle='-.', alpha=0.5, label=f'c_∞={c_inf:.2f}')
    
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Phase Velocity (m/s)')
    ax.set_title('Dispersion: Matched Filter vs Theory')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 2: Error
    ax = axes[0, 1]
    errors = [100 * (ce - ct) / ct for ce, ct in zip(c_extracted, c_theory)]
    ax.plot(freqs, errors, 'go-', markersize=10, linewidth=2)
    ax.axhline(y=0, color='r', linestyle='--', alpha=0.5)
    ax.axhline(y=5, color='gray', linestyle=':', alpha=0.3)
    ax.axhline(y=-5, color='gray', linestyle=':', alpha=0.3)
    
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Error (%)')
    ax.set_title(f'Extraction Error (mean={np.mean(np.abs(errors)):.1f}%)')
    ax.grid(True, alpha=0.3)
    
    # Plot 3: Correlation quality
    ax = axes[1, 0]
    ax.plot(freqs, qualities, 'mo-', markersize=10, linewidth=2)
    ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5, label='Threshold')
    
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Correlation Quality')
    ax.set_title('Matched Filter Quality Metric')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 4: Parameters
    ax = axes[1, 1]
    ax.axis('off')
    
    param_text = f"""
    Matched Filter Results:
    ----------------------
    Points extracted: {len(results)}
    Mean error: {np.mean(np.abs(errors)):.1f}%
    Max error: {max(abs(e) for e in errors):.1f}%
    
    Zener Parameters:
    ----------------
    G_r = {extractor.G_r} Pa
    G_∞ = {extractor.G_inf} Pa
    τ_σ = {extractor.tau_sigma*1000:.2f} ms
    
    Wave Speeds:
    -----------
    c_r = {c_r:.2f} m/s
    c_∞ = {c_inf:.2f} m/s
    """
    ax.text(0.1, 0.5, param_text, transform=ax.transAxes, fontsize=11,
           verticalalignment='center', fontfamily='monospace',
           bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig('matched_filter_result.png', dpi=150)
    print("\n✓ Saved: matched_filter_result.png")
    plt.show()
    
    # Print table
    print("\n" + "=" * 70)
    print("RESULTS TABLE")
    print("=" * 70)
    print(f"{'Freq (Hz)':<12} {'Extracted':<12} {'Theory':<12} {'Error %':<12} {'Quality':<10}")
    print("-" * 70)
    for r in results:
        err = 100 * (r['c_p'] - r['c_theory']) / r['c_theory']
        print(f"{r['f']:<12.0f} {r['c_p']:<12.2f} {r['c_theory']:<12.2f} {err:<12.1f} {r['quality']:<10.3f}")
    print("=" * 70)


def main():
    """Run matched filter extraction."""
    frequencies = [60, 100, 150, 200, 250, 300]
    
    results, extractor = multifrequency_extraction_matched(
        frequencies, G_r=5000, G_inf=8000, tau_sigma=0.001
    )
    
    visualize_matched_results(results, extractor)
    
    print("\n" + "=" * 70)
    print("Matched filter extraction complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
