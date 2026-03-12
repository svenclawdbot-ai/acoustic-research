"""
Phase Velocity Extraction for 2D Shear Wave Simulations
========================================================

Methods for extracting dispersion curves from 2D wavefield simulations:
1. Two-point phase difference method
2. Multi-receiver k-ω analysis  
3. Cross-correlation time delay

Author: Research Project — Week 2
Date: March 12, 2026
"""

import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq, ifft


class PhaseVelocityExtractor:
    """
    Extract phase velocity dispersion curves from 2D wavefield data.
    """
    
    def __init__(self, sim):
        """
        Initialize extractor with simulator instance.
        
        Parameters:
        -----------
        sim : ShearWave2D
            The 2D simulator instance
        """
        self.sim = sim
        self.receivers = []  # List of (x_idx, y_idx) receiver positions
        self.time_signals = []  # Time history at each receiver
        self.dt = sim.dt
        
    def add_receivers(self, positions):
        """
        Add receiver positions.
        
        Parameters:
        -----------
        positions : list of (x, y) tuples
            Receiver positions in grid indices
        """
        self.receivers.extend(positions)
        # Initialize signal storage
        for _ in positions:
            self.time_signals.append([])
    
    def record(self):
        """Record current wavefield at all receiver positions."""
        for i, (rx, ry) in enumerate(self.receivers):
            if 0 <= rx < self.sim.nx and 0 <= ry < self.sim.ny:
                # Record displacement (or velocity if available)
                if hasattr(self.sim, 'u'):
                    self.time_signals[i].append(self.sim.u[rx, ry])
                elif hasattr(self.sim, 'vy'):
                    self.time_signals[i].append(self.sim.vy[rx, ry])
                else:
                    self.time_signals[i].append(0.0)
            else:
                self.time_signals[i].append(0.0)
    
    def two_point_method(self, rec1_idx, rec2_idx, freq_range=(50, 500)):
        """
        Extract phase velocity using two-point phase difference method.
        
        Parameters:
        -----------
        rec1_idx, rec2_idx : int
            Indices of the two receivers to use
        freq_range : tuple
            (min_freq, max_freq) to analyze
            
        Returns:
        --------
        freqs : array
            Frequencies (Hz)
        phase_velocity : array
            Phase velocity at each frequency (m/s)
        """
        if len(self.time_signals[rec1_idx]) == 0 or len(self.time_signals[rec2_idx]) == 0:
            raise ValueError("No recorded data. Run simulation with record() calls.")
        
        # Get signals
        sig1 = np.array(self.time_signals[rec1_idx])
        sig2 = np.array(self.time_signals[rec2_idx])
        
        # Window to reduce spectral leakage
        window = signal.windows.hann(len(sig1))
        sig1_win = sig1 * window
        sig2_win = sig2 * window
        
        # FFT
        n_fft = len(sig1)
        freqs = fftfreq(n_fft, self.dt)
        
        # Only positive frequencies in range
        mask = (freqs > freq_range[0]) & (freqs < freq_range[1])
        freqs = freqs[mask]
        
        fft1 = fft(sig1_win)[mask]
        fft2 = fft(sig2_win)[mask]
        
        # Compute phase difference
        # phase = angle(fft2) - angle(fft1)
        phase_diff = np.angle(fft2) - np.angle(fft1)
        
        # Unwrap phase to avoid jumps
        phase_diff = np.unwrap(phase_diff)
        
        # Distance between receivers
        r1 = np.array(self.receivers[rec1_idx])
        r2 = np.array(self.receivers[rec2_idx])
        distance = np.linalg.norm(r2 - r1) * self.sim.dx
        
        # Phase velocity: c_p = ω · distance / phase_diff
        omega = 2 * np.pi * freqs
        
        # Avoid division by zero
        phase_velocity = np.zeros_like(freqs)
        valid = np.abs(phase_diff) > 1e-10
        phase_velocity[valid] = omega[valid] * distance / phase_diff[valid]
        
        # Filter out unreliable points (where signal is weak)
        magnitude_threshold = 0.01 * np.max(np.abs(fft1))
        reliable = np.abs(fft1) > magnitude_threshold
        phase_velocity[~reliable] = np.nan
        
        return freqs, phase_velocity
    
    def multi_receiver_dispersion(self, receiver_indices=None, freq_range=(50, 500)):
        """
        Extract dispersion using multiple receivers and linear fit.
        
        Uses phase slope across multiple spatial points.
        More robust than two-point method.
        
        Parameters:
        -----------
        receiver_indices : list or None
            Which receivers to use (None = all)
        freq_range : tuple
            Frequency range to analyze
            
        Returns:
        --------
        freqs : array
            Frequencies (Hz)
        phase_velocity : array
            Phase velocity (m/s)
        """
        if receiver_indices is None:
            receiver_indices = range(len(self.receivers))
        
        if len(receiver_indices) < 2:
            raise ValueError("Need at least 2 receivers for multi-receiver method")
        
        # Collect all signals
        signals = []
        positions = []
        for idx in receiver_indices:
            if len(self.time_signals[idx]) == 0:
                continue
            sig = np.array(self.time_signals[idx])
            signals.append(sig)
            
            r = np.array(self.receivers[idx])
            # Distance from origin
            pos = np.linalg.norm(r) * self.sim.dx
            positions.append(pos)
        
        if len(signals) < 2:
            raise ValueError("Not enough valid receiver data")
        
        signals = np.array(signals)
        positions = np.array(positions)
        
        # FFT of all signals
        n_fft = signals.shape[1]
        freqs_all = fftfreq(n_fft, self.dt)
        mask = (freqs_all > freq_range[0]) & (freqs_all < freq_range[1])
        freqs = freqs_all[mask]
        
        # FFT along time axis
        ffts = fft(signals, axis=1)[:, mask]
        
        # For each frequency, fit phase vs position
        phase_velocity = np.zeros(len(freqs))
        omega = 2 * np.pi * freqs
        
        for i, f in enumerate(freqs):
            phases = np.angle(ffts[:, i])
            phases = np.unwrap(phases)
            
            # Linear fit: phase = k * x
            # Only use if we have sufficient variation
            if np.max(phases) - np.min(phases) > 0.1:
                # Fit through origin (plane wave assumption)
                k, _, _, _ = np.linalg.lstsq(
                    positions[:, np.newaxis], 
                    phases, 
                    rcond=None
                )
                k = k[0]
                
                if abs(k) > 1e-10:
                    phase_velocity[i] = omega[i] / k
                else:
                    phase_velocity[i] = np.nan
            else:
                phase_velocity[i] = np.nan
        
        return freqs, phase_velocity
    
    def theoretical_kelvin_voigt(self, freqs, G_prime, eta, rho=1000):
        """
        Compute theoretical Kelvin-Voigt dispersion.
        
        c(ω) = √[2(G'² + ω²η²) / ρ(G' + √(G'² + ω²η²))]
        
        Parameters:
        -----------
        freqs : array
            Frequencies (Hz)
        G_prime : float
            Storage modulus (Pa)
        eta : float
            Viscosity (Pa·s)
        rho : float
            Density (kg/m³)
            
        Returns:
        --------
        phase_velocity : array
            Theoretical phase velocity (m/s)
        """
        omega = 2 * np.pi * freqs
        G_star_sq = G_prime**2 + (omega * eta)**2
        c = np.sqrt(2 * G_star_sq / (rho * (G_prime + np.sqrt(G_star_sq))))
        return c
    
    def compare_with_theory(self, layer=1, freq_range=(50, 500)):
        """
        Compare extracted dispersion with Kelvin-Voigt theory.
        
        Parameters:
        -----------
        layer : int
            Which layer to compare (1 or 2)
        freq_range : tuple
            Frequency range
            
        Returns:
        --------
        comparison : dict
            Contains freqs, measured, theoretical velocities
        """
        # Get material properties from simulator
        if layer == 1:
            # Average properties in bottom half
            G_avg = np.mean(self.sim.G_prime[:, :self.sim.ny//2])
            eta_avg = np.mean(self.sim.eta[:, :self.sim.ny//2])
        else:
            # Average properties in top half
            G_avg = np.mean(self.sim.G_prime[:, self.sim.ny//2:])
            eta_avg = np.mean(self.sim.eta[:, self.sim.ny//2:])
        
        # Extract dispersion
        freqs, c_meas = self.multi_receiver_dispersion(freq_range=freq_range)
        
        # Theoretical
        c_theory = self.theoretical_kelvin_voigt(freqs, G_avg, eta_avg)
        
        return {
            'freqs': freqs,
            'measured': c_meas,
            'theoretical': c_theory,
            'G_prime': G_avg,
            'eta': eta_avg
        }


def demo_phase_extraction():
    """Demonstrate phase velocity extraction."""
    from shear_wave_2d_simple import ShearWave2D
    import matplotlib.pyplot as plt
    
    print("=" * 60)
    print("PHASE VELOCITY EXTRACTION DEMO")
    print("=" * 60)
    
    # Setup
    nx, ny = 200, 200
    dx = 0.001
    
    # Single layer for validation
    print("\n[Test 1] Single layer - compare with theory")
    G_true = 5000
    eta_true = 5
    
    sim = ShearWave2D(nx, ny, dx, rho=1000, G_prime=G_true, eta=eta_true, pml_width=15)
    extractor = PhaseVelocityExtractor(sim)
    
    # Add receivers closer to source (stronger signal)
    receivers = [(80 + i*3, 80) for i in range(15)]
    extractor.add_receivers(receivers)
    
    print(f"  Added {len(receivers)} receivers")
    print(f"  Receiver spacing: {3*dx*100:.1f} cm")
    
    # Run simulation with stronger source
    print("  Running simulation...")
    for n in range(2000):
        t = n * sim.dt
        if n < 300:
            # Multi-frequency source with MUCH stronger amplitude
            sim.add_source(t, nx//2, 50, amplitude=1e-3, f0=100)
        sim.step()
        
        # Record every step
        extractor.record()
        
        if n % 400 == 0:
            max_u = np.max(np.abs(sim.u))
            print(f"    Step {n}/2000, max|u|={max_u:.3e}")
    
    print("  ✓ Simulation complete")
    
    # Check signal strength at receivers
    sig = np.array(extractor.time_signals[7])  # Middle receiver
    print(f"\n  Signal at receiver 7: max={np.max(np.abs(sig)):.3e}, energy={np.sum(sig**2):.3e}")
    
    # Extract dispersion
    print("\n  Extracting phase velocity...")
    freqs, c_meas = extractor.multi_receiver_dispersion(freq_range=(50, 300))
    c_theory = extractor.theoretical_kelvin_voigt(freqs, G_true, eta_true)
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    valid = ~np.isnan(c_meas)
    print(f"  Valid measurements: {np.sum(valid)}/{len(freqs)} frequencies")
    
    if np.sum(valid) > 0:
        ax.plot(freqs[valid], c_meas[valid], 'bo', label='Measured', markersize=6)
    ax.plot(freqs, c_theory, 'r-', label='Kelvin-Voigt Theory', linewidth=2)
    
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Phase Velocity (m/s)')
    ax.set_title(f'Dispersion Curve: G\'={G_true} Pa, η={eta_true} Pa·s')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 5)
    
    plt.tight_layout()
    plt.savefig('dispersion_single_layer.png', dpi=150)
    print("  Saved: dispersion_single_layer.png")
    
    # Compute error
    valid_both = valid & ~np.isnan(c_theory)
    if np.sum(valid_both) > 5:
        error_pct = np.mean(np.abs(c_meas[valid_both] - c_theory[valid_both]) / c_theory[valid_both]) * 100
        print(f"\n  Mean error vs theory: {error_pct:.1f}%")
        if error_pct < 15:
            print("  ✓ Good agreement with theory")
        else:
            print("  ⚠ Significant deviation from theory")
    else:
        print("\n  ⚠ Not enough valid measurements")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    demo_phase_extraction()
