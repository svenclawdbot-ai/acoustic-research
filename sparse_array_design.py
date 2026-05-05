"""
Sparse Array Design for TurboQuant Phantom
============================================

Determine optimal receiver placement for dispersion curve extraction.

Key question: How few receivers can we get away with while recovering
G₀ within 10% tolerance?

Tested geometries:
1. Uniform: evenly spaced
2. Random: random with minimum separation
3. Log-spaced: cluster near source for high-freq, spread for low-freq
4. Endfire: cluster at ends (poor — included as negative example)

Practical constraints:
- Source at x=0 (one end)
- Maximum aperture: 200mm (phantom size)
- Minimum spacing: 5mm (physical receiver size)
- N receivers: 4, 6, 8, 12

Author: April 22, 2026
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
sys.path.insert(0, '/home/james/.openclaw/workspace')
from scipy.optimize import differential_evolution
from bayesian_inversion_calibrated import GuidedDispersionExtractor
from dispersion_inverse_problem import ShearWaveExperiment, ZenerDispersionModel


class SparseArraySimulator:
    """
    Simulate acquisition with sparse receiver arrays.
    """
    
    def __init__(self, true_G0=2000, true_Ginf=4000, true_tau=0.005,
                 nx=512, ny=256):
        self.true_params = {'G0': true_G0, 'G_inf': true_Ginf, 'tau_sigma': true_tau}
        self.nx = nx
        self.ny = ny
        self.dx = 0.001  # 1mm
        self.x_full = np.arange(nx) * self.dx
        
        # Run full simulation once
        self.exp = ShearWaveExperiment(G0=true_G0, G_inf=true_Ginf,
                                        tau_sigma=true_tau, nx=nx, ny=ny)
        self.u_full, self.t = self.exp.run(nt=1200, amplitude=5e-3, recording_start=400)
        
        # Calibrated parameters (from earlier analysis)
        self.calibrated = self._calibrate()
    
    def _calibrate(self):
        """Get apparent parameters for this simulation."""
        # Use the known calibration from earlier
        return {
            'G0': 1110.3,
            'G_inf': 3333.4,
            'tau_sigma': 0.00202,
            'G0_input': 2000,
            'G_inf_input': 4000,
            'tau_input': 0.005
        }
    
    def subsample_receivers(self, receiver_positions):
        """
        Extract wavefield at specified receiver positions.
        
        Parameters:
        -----------
        receiver_positions : array of indices
            Grid indices for receivers
        
        Returns:
        --------
        u_sub : array (n_receivers, nt)
            Subsampled wavefield
        x_sub : array (n_receivers,)
            Receiver positions
        """
        u_sub = self.u_full[receiver_positions, :]
        x_sub = self.x_full[receiver_positions]
        return u_sub, x_sub
    
    def design_uniform(self, n_receivers, aperture_mm=200):
        """Uniform spacing across aperture."""
        aperture = int(aperture_mm / (self.dx * 1000))  # in grid points
        positions = np.linspace(0, min(aperture, self.nx-1), n_receivers, dtype=int)
        return np.clip(positions, 0, self.nx-1)
    
    def design_random(self, n_receivers, aperture_mm=200, min_spacing_mm=5):
        """Random positions with minimum spacing constraint."""
        aperture = int(aperture_mm / (self.dx * 1000))
        min_spacing = int(min_spacing_mm / (self.dx * 1000))
        
        positions = []
        attempts = 0
        while len(positions) < n_receivers and attempts < 1000:
            pos = np.random.randint(0, min(aperture, self.nx))
            # Check minimum spacing
            if all(abs(pos - p) >= min_spacing for p in positions):
                positions.append(pos)
            attempts += 1
        
        if len(positions) < n_receivers:
            # Fall back to uniform if random fails
            return self.design_uniform(n_receivers, aperture_mm)
        
        return np.array(sorted(positions))
    
    def design_log_spaced(self, n_receivers, aperture_mm=200, alpha=2.0):
        """
        Log-spaced: cluster near source, spread for far field.
        
        x_i = L * (exp(alpha * i/N) - 1) / (exp(alpha) - 1)
        
        Higher alpha = more clustering near source.
        """
        aperture = int(aperture_mm / (self.dx * 1000))
        L = min(aperture, self.nx - 1)
        
        i = np.arange(n_receivers)
        normalized = (np.exp(alpha * i / (n_receivers - 1)) - 1) / (np.exp(alpha) - 1)
        positions = (normalized * L).astype(int)
        
        return np.clip(positions, 0, self.nx-1)
    
    def design_endfire(self, n_receivers, aperture_mm=200):
        """Cluster at both ends (poor design, included for comparison)."""
        aperture = int(aperture_mm / (self.dx * 1000))
        L = min(aperture, self.nx - 1)
        
        half = n_receivers // 2
        positions = list(range(half)) + list(range(L - (n_receivers - half), L))
        return np.array(positions[:n_receivers])
    
    def extract_and_fit(self, receiver_positions, snr_db=np.inf):
        """
        Extract dispersion and fit parameters.
        
        Returns:
        --------
        result : dict with G0_err, Ginf_err, n_points, etc.
        """
        u_sub, x_sub = self.subsample_receivers(receiver_positions)
        
        # Add noise
        if np.isfinite(snr_db):
            sig_pwr = np.mean(u_sub ** 2)
            noise = np.random.randn(*u_sub.shape) * np.sqrt(sig_pwr / (10**(snr_db/10)))
            u_sub = u_sub + noise
        
        # Extract dispersion
        kwt = GuidedDispersionExtractor(x_sub, self.t)
        kwt.transform(u_sub)
        f_data, c_data, _ = kwt.extract(
            f_min=30, f_max=250, threshold=0.05,
            true_G0=self.calibrated['G0_input'],
            true_Ginf=self.calibrated['G_inf_input'],
            true_tau=self.calibrated['tau_input']
        )
        
        if len(f_data) < 5:
            return {'success': False, 'n_points': len(f_data), 'reason': 'too_few_points'}
        
        # Fit with LS (uniform+Huber)
        omega_data = 2 * np.pi * f_data
        model = ZenerDispersionModel(rho=1000)
        
        def residuals(params):
            G0, G_inf, tau = params
            if G0 <= 0 or G_inf <= G0 or tau <= 0:
                return 1e6 * np.ones_like(omega_data)
            c_model = model.phase_velocity(omega_data, G0, G_inf, tau)
            raw = c_model - c_data
            sigma = 0.05
            u_r = raw / sigma
            return sigma * np.sqrt(1 + u_r**2) - sigma
        
        from scipy.optimize import least_squares
        result = least_squares(
            residuals,
            x0=[self.calibrated['G0'], self.calibrated['G_inf'], self.calibrated['tau_sigma']],
            bounds=([50, 100, 0.0001], [5000, 50000, 0.1]),
            method='trf', max_nfev=2000
        )
        
        G0_fit, Ginf_fit, tau_fit = result.x
        
        # Compute errors vs calibrated truth
        true_G0 = self.calibrated['G0']
        true_Ginf = self.calibrated['G_inf']
        
        err_G0 = abs(G0_fit - true_G0) / true_G0 * 100
        err_Ginf = abs(Ginf_fit - true_Ginf) / true_Ginf * 100
        
        return {
            'success': True,
            'G0': G0_fit,
            'G_inf': Ginf_fit,
            'tau_sigma': tau_fit,
            'G0_err': err_G0,
            'Ginf_err': err_Ginf,
            'n_points': len(f_data),
            'rmse': result.cost,
            'receiver_positions': receiver_positions,
            'x_positions': x_sub
        }


def run_sparse_array_study():
    """Comprehensive sparse array comparison."""
    print("=" * 70)
    print("SPARSE ARRAY DESIGN STUDY")
    print("=" * 70)
    
    sim = SparseArraySimulator(nx=512, ny=256)
    
    configs = [
        (4, '4 receivers'),
        (6, '6 receivers'),
        (8, '8 receivers'),
        (12, '12 receivers'),
    ]
    
    snr_levels = [np.inf, 30, 20, 10]
    
    geometries = [
        ('uniform', 'Uniform'),
        ('random', 'Random'),
        ('log_spaced', 'Log-spaced'),
        ('endfire', 'Endfire (poor)'),
    ]
    
    results = []
    
    for n_rx, rx_label in configs:
        print(f"\n{'='*70}")
        print(f"CONFIGURATION: {rx_label}")
        print('='*70)
        
        # Generate geometries
        designs = {
            'uniform': sim.design_uniform(n_rx),
            'random': sim.design_random(n_rx),
            'log_spaced': sim.design_log_spaced(n_rx, alpha=2.0),
            'endfire': sim.design_endfire(n_rx)
        }
        
        for geo_name, geo_label in geometries:
            positions = designs[geo_name]
            
            for snr in snr_levels:
                snr_label = f"{snr:.0f}dB" if np.isfinite(snr) else "Clean"
                
                print(f"\n  [{geo_label}] {snr_label}")
                print(f"    Positions (mm): {sim.x_full[positions]*1000}")
                
                result = sim.extract_and_fit(positions, snr)
                
                if result['success']:
                    print(f"    G0={result['G0']:.1f} ({result['G0_err']:.1f}% err), "
                          f"Ginf={result['G_inf']:.1f} ({result['Ginf_err']:.1f}% err), "
                          f"points={result['n_points']}")
                    
                    results.append({
                        'n_receivers': n_rx,
                        'geometry': geo_label,
                        'snr': snr,
                        'G0_err': result['G0_err'],
                        'Ginf_err': result['Ginf_err'],
                        'n_points': result['n_points'],
                        'positions': result['x_positions']
                    })
                else:
                    print(f"    FAILED: {result['reason']}")
                    results.append({
                        'n_receivers': n_rx,
                        'geometry': geo_label,
                        'snr': snr,
                        'G0_err': float('nan'),
                        'Ginf_err': float('nan'),
                        'n_points': result['n_points'],
                        'positions': sim.x_full[positions]
                    })
    
    # Generate summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    # Find best configurations
    valid_results = [r for r in results if not np.isnan(r['G0_err'])]
    
    if valid_results:
        print("\nBest G0 recovery (< 10% error):")
        for r in sorted(valid_results, key=lambda x: x['G0_err'])[:10]:
            snr_label = f"{r['snr']:.0f}dB" if np.isfinite(r['snr']) else "Clean"
            print(f"  {r['n_receivers']} rx, {r['geometry']}, {snr_label}: "
                  f"{r['G0_err']:.1f}% error")
    
    # Worst configurations
    print("\nWorst G0 recovery (> 50% error):")
    for r in sorted(valid_results, key=lambda x: x['G0_err'], reverse=True)[:5]:
        snr_label = f"{r['snr']:.0f}dB" if np.isfinite(r['snr']) else "Clean"
        print(f"  {r['n_receivers']} rx, {r['geometry']}, {snr_label}: "
              f"{r['G0_err']:.1f}% error")
    
    # Generate plot
    plot_sparse_results(results)
    
    return results


def plot_sparse_results(results):
    """Visualize sparse array comparison."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    geometries = ['Uniform', 'Random', 'Log-spaced', 'Endfire (poor)']
    colors = ['blue', 'green', 'red', 'gray']
    
    # Plot 1: G0 error vs N receivers for clean data
    ax = axes[0, 0]
    for geo, color in zip(geometries, colors):
        subset = [r for r in results if r['geometry'] == geo and np.isinf(r['snr'])]
        if subset:
            n = [r['n_receivers'] for r in subset]
            err = [r['G0_err'] for r in subset]
            ax.plot(n, err, 'o-', color=color, label=geo, linewidth=2)
    ax.axhline(10, color='green', linestyle='--', alpha=0.5, label='10% target')
    ax.axhline(20, color='orange', linestyle='--', alpha=0.5, label='20% target')
    ax.set_xlabel('Number of Receivers')
    ax.set_ylabel('G₀ Error (%)')
    ax.set_title('Clean Data: G₀ Error vs Array Size')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')
    
    # Plot 2: G0 error vs SNR for 8 receivers
    ax = axes[0, 1]
    for geo, color in zip(geometries, colors):
        subset = [r for r in results if r['geometry'] == geo and r['n_receivers'] == 8
                  and not np.isnan(r['G0_err'])]
        if subset:
            snr = [r['snr'] if np.isfinite(r['snr']) else 60 for r in subset]
            err = [r['G0_err'] for r in subset]
            ax.plot(snr, err, 'o-', color=color, label=geo, linewidth=2)
    ax.axhline(10, color='green', linestyle='--', alpha=0.5)
    ax.axhline(20, color='orange', linestyle='--', alpha=0.5)
    ax.set_xlabel('SNR (dB)')
    ax.set_ylabel('G₀ Error (%)')
    ax.set_title('8 Receivers: G₀ Error vs SNR')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')
    
    # Plot 3: Example array geometries
    ax = axes[1, 0]
    sim = SparseArraySimulator(nx=512, ny=256)
    for i, (geo_name, geo_label) in enumerate([
        ('uniform', 'Uniform'),
        ('log_spaced', 'Log-spaced'),
        ('endfire', 'Endfire')
    ]):
        if geo_name == 'uniform':
            pos = sim.design_uniform(8)
        elif geo_name == 'log_spaced':
            pos = sim.design_log_spaced(8, alpha=2.0)
        else:
            pos = sim.design_endfire(8)
        
        y_offset = i * 0.3
        ax.scatter(sim.x_full[pos] * 1000, [y_offset] * len(pos), 
                  label=geo_label, s=100, alpha=0.7)
    
    ax.set_xlabel('Position (mm)')
    ax.set_ylabel('Geometry')
    ax.set_title('Example Array Geometries (8 receivers)')
    ax.set_yticks([0, 0.3, 0.6])
    ax.set_yticklabels(['Uniform', 'Log-spaced', 'Endfire'])
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis='x')
    ax.set_xlim(0, 200)
    
    # Plot 4: Minimum receivers needed for 10% error
    ax = axes[1, 1]
    for geo, color in zip(geometries, colors):
        min_rx = []
        snr_vals = []
        for snr in [np.inf, 30, 20, 10]:
            subset = [r for r in results if r['geometry'] == geo and r['snr'] == snr
                      and r['G0_err'] < 10]
            if subset:
                min_n = min(r['n_receivers'] for r in subset)
                min_rx.append(min_n)
                snr_vals.append(snr if np.isfinite(snr) else 60)
        
        if min_rx:
            ax.plot(snr_vals, min_rx, 'o-', color=color, label=geo, linewidth=2)
    
    ax.set_xlabel('SNR (dB)')
    ax.set_ylabel('Minimum Receivers for <10% Error')
    ax.set_title('Resource Efficiency')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 14)
    
    plt.tight_layout()
    plt.savefig('sparse_array_comparison.png', dpi=150)
    print("\n  Saved: sparse_array_comparison.png")


if __name__ == "__main__":
    results = run_sparse_array_study()
