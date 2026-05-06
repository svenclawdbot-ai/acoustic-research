#!/usr/bin/env python3
"""
Sequential Narrowband Shear Wave Simulation for Dispersion Extraction
======================================================================

Runs 2D shear wave simulation sequentially for each frequency.
Each simulation uses a narrowband tone burst at a single frequency,
producing clean signals for reliable phase velocity extraction.

Author: Research Project
Date: April 16, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from shear_wave_2d_simulator import ShearWave2D
from improved_freqdomain_dispersion import fit_kelvin_voigt


class SequentialDispersionExtractor:
    """
    Extract dispersion curve by running sequential narrowband simulations.
    """
    
    def __init__(self, 
                 G_prime: float = 2000,
                 eta: float = 0.5,
                 rho: float = 1000,
                 domain_size: float = 0.15,  # 15 cm domain
                 nx: int = 300,
                 pml_width: int = 20):
        """
        Initialize sequential dispersion extractor.
        
        Parameters:
        -----------
        G_prime : float
            Storage modulus (Pa)
        eta : float
            Viscosity (Pa·s)
        rho : float
            Density (kg/m³)
        domain_size : float
            Domain size in meters
        nx : int
            Grid points (ny = nx)
        pml_width : int
            PML thickness in grid points
        """
        self.G_prime = G_prime
        self.eta = eta
        self.rho = rho
        self.domain_size = domain_size
        self.nx = nx
        self.ny = nx
        self.pml_width = pml_width
        
        # Grid setup
        self.dx = domain_size / nx
        
        # Time step (CFL stability) - more conservative for 2D
        c_max = np.sqrt(G_prime / rho) * 2.0  # Account for dispersion
        self.dt = self.dx / (4 * c_max)  # More conservative: divide by 4 instead of 2
        
        print(f"Sequential Dispersion Extractor")
        print(f"  Domain: {domain_size*100:.1f} cm x {domain_size*100:.1f} cm")
        print(f"  Grid: {nx} x {nx}, dx={self.dx*1000:.2f} mm")
        print(f"  dt={self.dt*1e6:.2f} μs")
        print(f"  G'={G_prime} Pa, η={eta} Pa·s, ρ={rho} kg/m³")
        
    def theoretical_velocity(self, freq: float) -> float:
        """Calculate theoretical phase velocity at given frequency."""
        omega = 2 * np.pi * freq
        G_mag = np.sqrt(self.G_prime**2 + (omega * self.eta)**2)
        c = np.sqrt(2 / self.rho) * np.sqrt(G_mag**2 / (self.G_prime + G_mag))
        return c
    
    def run_single_frequency(self, 
                             freq: float,
                             receiver_distances: List[float],
                             duration: float = 0.05,
                             source_position: Tuple[float, float] = None) -> Dict:
        """
        Run simulation for a single frequency.
        
        Parameters:
        -----------
        freq : float
            Frequency in Hz
        receiver_distances : list
            Distances from source in meters
        duration : float
            Simulation duration in seconds
        source_position : tuple
            (x, y) source position in meters (default: center)
            
        Returns:
        --------
        dict with receiver signals, time array, and metadata
        """
        print(f"\n  Running f = {freq:.0f} Hz...")
        
        # Create simulator
        sim = ShearWave2D(
            nx=self.nx, ny=self.ny, dx=self.dx, dt=self.dt,
            rho=self.rho, G_prime=self.G_prime, eta=self.eta,
            bc_type='mur2'
        )
        
        # Source position
        if source_position is None:
            source_x, source_y = self.nx // 2, self.ny // 2
        else:
            source_x = int(source_position[0] / self.dx)
            source_y = int(source_position[1] / self.dx)
        
        # Receiver positions (along x-axis from source)
        receiver_positions = []
        for d in receiver_distances:
            rx = min(source_x + int(d / self.dx), self.nx - self.pml_width - 1)
            ry = source_y
            receiver_positions.append((rx, ry))
        
        # Number of steps
        n_steps = int(duration / self.dt)
        
        # Storage for receiver signals
        receiver_signals = [[] for _ in receiver_positions]
        time_array = []
        
        # Calculate source duration (5 cycles)
        source_duration = 5.0 / freq
        
        # Run simulation
        for n in range(n_steps):
            t = n * self.dt
            time_array.append(t)
            
            # Add source (tone burst)
            if t < source_duration:
                sim.add_source(
                    t, 
                    source_type='tone_burst',
                    f0=freq,
                    amplitude=1e-8,  # Smaller amplitude to avoid overflow
                    location=(source_x, source_y)
                )
            
            # Step
            sim.step()
            
            # Record receiver signals
            for i, (rx, ry) in enumerate(receiver_positions):
                receiver_signals[i].append(sim.u[rx, ry])
            
            # Progress
            if n % (n_steps // 10) == 0:
                print(f"    {100*n/n_steps:.0f}%", end='', flush=True)
        
        print(" ✓")
        
        # Convert to arrays
        receiver_signals = [np.array(sig) for sig in receiver_signals]
        time_array = np.array(time_array)
        
        # Theoretical velocity
        c_theory = self.theoretical_velocity(freq)
        
        return {
            'freq': freq,
            'time': time_array,
            'receiver_signals': receiver_signals,
            'receiver_distances': np.array(receiver_distances),
            'receiver_positions': receiver_positions,
            'source_position': (source_x, source_y),
            'c_theory': c_theory
        }
    
    def extract_velocity_from_simulation(self, sim_result: Dict) -> float:
        """
        Extract phase velocity from a single-frequency simulation.
        
        Uses envelope cross-correlation for robust delay estimation.
        """
        from scipy.signal import hilbert, correlate
        
        signals = sim_result['receiver_signals']
        distances = sim_result['receiver_distances']
        dt = self.dt
        
        pair_velocities = []
        
        for i in range(len(signals) - 1):
            for j in range(i + 1, len(signals)):
                # Envelopes
                env1 = np.abs(hilbert(signals[i]))
                env2 = np.abs(hilbert(signals[j]))
                
                # Cross-correlation
                corr = correlate(env2, env1, mode='full')
                lags = np.arange(-len(env1) + 1, len(env1))
                
                # Find peak
                peak_idx = np.argmax(np.abs(corr))
                delay = lags[peak_idx] * dt
                
                distance = distances[j] - distances[i]
                
                if delay > 1e-9:
                    velocity = distance / delay
                    if 0.5 <= velocity <= 20:  # Reasonable shear wave range
                        pair_velocities.append(velocity)
        
        if pair_velocities:
            return np.median(pair_velocities)
        return np.nan
    
    def run_dispersion_extraction(self,
                                   frequencies: List[float],
                                   receiver_distances: List[float],
                                   duration: float = 0.05) -> Dict:
        """
        Run sequential simulations and extract full dispersion curve.
        
        Parameters:
        -----------
        frequencies : list
            Frequencies to simulate (Hz)
        receiver_distances : list
            Receiver distances from source (m)
        duration : float
            Simulation duration per frequency (s)
            
        Returns:
        --------
        dict with dispersion curve and simulation results
        """
        print("=" * 70)
        print("Sequential Narrowband Dispersion Extraction")
        print("=" * 70)
        print(f"Frequencies: {frequencies}")
        print(f"Receivers at: {[f'{d*1000:.0f}mm' for d in receiver_distances]}")
        print(f"Duration per sim: {duration*1000:.0f} ms")
        print("=" * 70)
        
        results = {
            'frequencies': [],
            'velocities_measured': [],
            'velocities_theory': [],
            'simulations': []
        }
        
        for freq in frequencies:
            # Run simulation
            sim_result = self.run_single_frequency(
                freq, receiver_distances, duration
            )
            
            # Extract velocity
            v_measured = self.extract_velocity_from_simulation(sim_result)
            v_theory = sim_result['c_theory']
            
            results['frequencies'].append(freq)
            results['velocities_measured'].append(v_measured)
            results['velocities_theory'].append(v_theory)
            results['simulations'].append(sim_result)
            
            error_pct = 100 * abs(v_measured - v_theory) / v_theory if v_theory > 0 else 0
            print(f"  Result: c = {v_measured:.3f} m/s (theory: {v_theory:.3f}, error: {error_pct:.1f}%)")
        
        results['frequencies'] = np.array(results['frequencies'])
        results['velocities_measured'] = np.array(results['velocities_measured'])
        results['velocities_theory'] = np.array(results['velocities_theory'])
        
        return results
    
    def fit_parameters(self, results: Dict) -> Dict:
        """Fit Kelvin-Voigt model to measured dispersion."""
        valid_mask = ~np.isnan(results['velocities_measured'])
        
        if np.sum(valid_mask) < 3:
            print("ERROR: Not enough valid points for fitting")
            return None
        
        fit = fit_kelvin_voigt(
            results['frequencies'][valid_mask],
            results['velocities_measured'][valid_mask],
            uncertainty=None,
            rho=self.rho
        )
        
        return fit
    
    def plot_results(self, results: Dict, fit: Dict = None, save_path: str = None):
        """Create visualization of results."""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Plot 1: Dispersion curve
        ax = axes[0, 0]
        
        # Theoretical curve
        f_theory = np.linspace(50, 150, 200)
        c_theory = [self.theoretical_velocity(f) for f in f_theory]
        ax.plot(f_theory, c_theory, 'g--', linewidth=2, label='True (input)')
        
        if fit and fit['success']:
            c_fit = [np.sqrt(2/self.rho) * np.sqrt(
                (fit['G_prime']**2 + (2*np.pi*f*fit['eta'])**2)**2 / 
                (fit['G_prime'] + np.sqrt(fit['G_prime']**2 + (2*np.pi*f*fit['eta'])**2))
            ) for f in f_theory]
            ax.plot(f_theory, c_fit, 'r-', linewidth=2, 
                   label=f"Fitted: G'={fit['G_prime']:.0f}, η={fit['eta']:.3f}")
        
        ax.scatter(results['frequencies'], results['velocities_measured'],
                  c='blue', s=80, zorder=5, label='Measured')
        
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Phase Velocity (m/s)')
        ax.set_title('Dispersion Curve from Sequential Simulation')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 5)
        
        # Plot 2: Error analysis
        ax = axes[0, 1]
        errors = 100 * (results['velocities_measured'] - results['velocities_theory']) / results['velocities_theory']
        ax.bar(results['frequencies'], errors, width=6, alpha=0.7, color='steelblue')
        ax.axhline(0, color='red', linestyle='-')
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Error (%)')
        ax.set_title('Measurement Error')
        ax.grid(True, alpha=0.3)
        
        # Plot 3: Example waveforms (first frequency)
        ax = axes[1, 0]
        if len(results['simulations']) > 0:
            sim = results['simulations'][len(results['simulations'])//2]  # Middle frequency
            t_ms = sim['time'] * 1000
            for i, sig in enumerate(sim['receiver_signals']):
                ax.plot(t_ms, sig * 1e6, alpha=0.7, 
                       label=f"R{i+1} ({sim['receiver_distances'][i]*1000:.0f}mm)")
            ax.set_xlabel('Time (ms)')
            ax.set_ylabel('Displacement (μm)')
            ax.set_title(f"Example Waveforms @ {sim['freq']:.0f} Hz")
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)
        
        # Plot 4: Parameters comparison
        ax = axes[1, 1]
        ax.text(0.1, 0.7, f"True G': {self.G_prime:.0f} Pa", fontsize=12, transform=ax.transAxes)
        ax.text(0.1, 0.6, f"True η: {self.eta:.3f} Pa·s", fontsize=12, transform=ax.transAxes)
        
        if fit and fit['success']:
            G_error = 100 * abs(fit['G_prime'] - self.G_prime) / self.G_prime
            eta_error = 100 * abs(fit['eta'] - self.eta) / self.eta if self.eta > 0 else 0
            
            ax.text(0.1, 0.4, f"Fitted G': {fit['G_prime']:.0f} Pa ({G_error:.1f}% error)", 
                   fontsize=12, transform=ax.transAxes, color='red')
            ax.text(0.1, 0.3, f"Fitted η: {fit['eta']:.3f} Pa·s ({eta_error:.1f}% error)",
                   fontsize=12, transform=ax.transAxes, color='red')
            ax.text(0.1, 0.15, f"R² = {fit['r_squared']:.4f}", fontsize=12, transform=ax.transAxes)
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        ax.set_title('Parameter Recovery')
        
        plt.suptitle('Sequential Narrowband Simulation Results', fontweight='bold', fontsize=14)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150)
            print(f"\nSaved: {save_path}")
        
        return fig


def main():
    """Run example sequential dispersion extraction."""
    # True parameters
    G_prime_true = 2000
    eta_true = 0.5
    rho = 1000
    
    # Create extractor
    extractor = SequentialDispersionExtractor(
        G_prime=G_prime_true,
        eta=eta_true,
        rho=rho,
        domain_size=0.08,  # Smaller domain: 8 cm
        nx=200             # Finer grid
    )
    
    # Frequencies to simulate
    frequencies = [60, 80, 100, 120, 140]
    
    # Receiver distances
    receiver_distances = [0.015, 0.030, 0.045]  # 15, 30, 45 mm
    
    # Run extraction
    results = extractor.run_dispersion_extraction(
        frequencies=frequencies,
        receiver_distances=receiver_distances,
        duration=0.04  # 40 ms per simulation
    )
    
    # Fit model
    print("\n" + "=" * 70)
    print("Fitting Kelvin-Voigt model...")
    fit = extractor.fit_parameters(results)
    
    if fit and fit['success']:
        print(f"  G' = {fit['G_prime']:.0f} Pa (true: {G_prime_true:.0f})")
        print(f"  η = {fit['eta']:.3f} Pa·s (true: {eta_true:.3f})")
        
        G_err = 100 * abs(fit['G_prime'] - G_prime_true) / G_prime_true
        eta_err = 100 * abs(fit['eta'] - eta_true) / eta_true
        print(f"\n  Errors: G' = {G_err:.1f}%, η = {eta_err:.1f}%")
    
    # Plot
    extractor.plot_results(results, fit, save_path='sequential_dispersion.png')
    
    print("\n" + "=" * 70)
    print("Sequential simulation complete!")
    print("=" * 70)
    
    return results, fit


if __name__ == '__main__':
    results, fit = main()
