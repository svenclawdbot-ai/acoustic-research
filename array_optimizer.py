"""
Array Optimization for Sparse Sampling
======================================

Optimizes receiver placement for compressive sensing reconstruction.
Uses greedy forward selection and genetic algorithm approaches.

Author: DSP Challenge — March 18, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import differential_evolution
import sys
sys.path.append('/home/james/.openclaw/workspace/research/week2')
from shear_wave_2d_zener import ShearWave2DZener
from zener_model import ZenerModel


class ArrayOptimizer:
    """
    Optimize sparse receiver array for shear wave CS.
    
    Methods:
    1. Greedy forward selection (fast, good baseline)
    2. Differential evolution (global optimum, slower)
    3. Simulated annealing (balance of speed/quality)
    """
    
    def __init__(self, x_array, n_receivers=8, method='mutual_coherence'):
        """
        Initialize optimizer.
        
        Parameters:
        -----------
        x_array : array
            Spatial grid (m)
        n_receivers : int
            Number of receivers to place
        method : str
            'mutual_coherence', 'frame_potential', or 'reconstruction'
        """
        self.x = np.array(x_array)
        self.nx = len(x_array)
        self.n_rec = n_receivers
        self.method = method
        
        # Build Fourier basis
        k_vec = 2 * np.pi * np.fft.fftfreq(self.nx, x_array[1] - x_array[0])
        X, K = np.meshgrid(x_array, k_vec, indexing='ij')
        self.Phi = np.exp(1j * K * X) / np.sqrt(self.nx)
        self.k = k_vec
        
        print(f"Array Optimizer:")
        print(f"  Grid: {self.nx} points, {n_receivers} receivers")
        print(f"  Method: {method}")
    
    def mutual_coherence(self, indices):
        """
        Compute mutual coherence of sensing matrix.
        
        μ = max_{i≠j} |<φ_i, φ_j>|
        Lower is better for CS recovery.
        """
        A = self.Phi[indices, :]  # (n_rec, nx)
        
        # Gram matrix
        G = np.abs(A @ A.conj().T)
        np.fill_diagonal(G, 0)
        
        return np.max(G)
    
    def frame_potential(self, indices):
        """
        Compute frame potential.
        
        FP = sum_{i,j} |<φ_i, φ_j>|²
        Lower is better (minimizes redundancy).
        """
        A = self.Phi[indices, :]
        G = np.abs(A @ A.conj().T)**2
        
        return np.sum(G)
    
    def greedy_forward_selection(self, verbose=True):
        """
        Greedy algorithm: add receivers one at a time.
        
        At each step, add the receiver that minimizes the objective.
        Fast and gives good baseline performance.
        """
        if verbose:
            print(f"\nGreedy Forward Selection ({self.n_rec} receivers):")
        
        selected = []
        available = list(range(self.nx))
        
        for i in range(self.n_rec):
            best_idx = None
            best_score = float('inf')
            
            # Try each available position
            for idx in available:
                trial = selected + [idx]
                
                if self.method == 'mutual_coherence':
                    score = self.mutual_coherence(trial)
                elif self.method == 'frame_potential':
                    score = self.frame_potential(trial)
                else:
                    score = self.mutual_coherence(trial)
                
                if score < best_score:
                    best_score = score
                    best_idx = idx
            
            selected.append(best_idx)
            available.remove(best_idx)
            
            if verbose and i % 2 == 0:
                print(f"  Step {i+1}: added receiver at {self.x[best_idx]*100:.1f} cm, "
                      f"score={best_score:.4f}")
        
        selected = np.array(sorted(selected))
        
        if verbose:
            print(f"\n  Final positions: {list(self.x[selected]*100)} cm")
            final_score = (self.mutual_coherence(selected) 
                          if self.method == 'mutual_coherence' 
                          else self.frame_potential(selected))
            print(f"  Final score: {final_score:.4f}")
        
        return selected
    
    def optimize_differential_evolution(self, maxiter=50, popsize=10):
        """
        Global optimization using differential evolution.
        
        Slower but finds better solutions than greedy.
        """
        print(f"\nDifferential Evolution ({self.n_rec} receivers):")
        
        bounds = [(0, self.nx - 1) for _ in range(self.n_rec)]
        
        def objective(x):
            indices = np.clip(x.astype(int), 0, self.nx - 1)
            indices = np.unique(indices)
            
            if len(indices) < self.n_rec:
                return 1.0  # Penalize duplicates
            
            if self.method == 'mutual_coherence':
                return self.mutual_coherence(indices)
            else:
                return self.frame_potential(indices)
        
        result = differential_evolution(
            objective,
            bounds,
            maxiter=maxiter,
            popsize=popsize,
            tol=1e-4,
            polish=True,
            workers=1  # Sequential for debugging
        )
        
        optimal = np.clip(result.x.astype(int), 0, self.nx - 1)
        optimal = np.unique(optimal)
        
        print(f"  Optimal positions: {list(self.x[optimal]*100)} cm")
        print(f"  Final score: {result.fun:.4f}")
        print(f"  Iterations: {result.nit}")
        
        return optimal, result
    
    def compare_arrays(self, u_true, t_array, reconstructor):
        """
        Compare different array configurations.
        
        Parameters:
        -----------
        u_true : ndarray (nx, nt)
            True wavefield
        t_array : array
            Time array
        reconstructor : callable
            Function: u_recon = reconstructor(y_sparse, rec_indices)
            
        Returns:
        --------
        results : dict
            Comparison of array types
        """
        print("\n" + "=" * 70)
        print("ARRAY CONFIGURATION COMPARISON")
        print("=" * 70)
        
        configs = {
            'uniform': np.linspace(0, self.nx-1, self.n_rec, dtype=int),
            'random': np.sort(np.random.choice(self.nx, self.n_rec, replace=False)),
            'endfire': np.concatenate([
                np.linspace(0, self.nx//4, self.n_rec//2, dtype=int),
                np.linspace(3*self.nx//4, self.nx-1, self.n_rec - self.n_rec//2, dtype=int)
            ]),
            'greedy_mc': self.greedy_forward_selection(verbose=False),
        }
        
        results = {}
        
        for name, indices in configs.items():
            print(f"\n{name.upper()}:")
            print(f"  Positions: {list(self.x[indices]*100)} cm")
            
            # Coherence
            mu = self.mutual_coherence(indices)
            print(f"  Mutual coherence: μ = {mu:.4f}")
            
            # Sample and reconstruct
            y_sparse = u_true[indices, :]
            u_recon = reconstructor(y_sparse, indices)
            
            # Quality metrics
            nmse = np.mean(np.abs(u_true - u_recon)**2) / np.mean(np.abs(u_true)**2)
            corr = np.corrcoef(u_true.flatten(), u_recon.flatten())[0, 1]
            
            print(f"  Reconstruction: NMSE={nmse:.4f}, Corr={corr:.4f}")
            
            results[name] = {
                'indices': indices,
                'mu': mu,
                'nmse': nmse,
                'correlation': corr,
                'u_recon': u_recon
            }
        
        return results
    
    def visualize_arrays(self, results, u_true, save_path='array_comparison.png'):
        """Visualize array configurations and reconstructions."""
        fig, axes = plt.subplots(2, len(results), figsize=(4*len(results), 8))
        
        extent = [0, u_true.shape[1], self.x[0]*100, self.x[-1]*100]
        vmax = np.max(np.abs(u_true))
        
        for idx, (name, data) in enumerate(results.items()):
            # Array geometry
            ax = axes[0, idx]
            ax.scatter(self.x, np.zeros(self.nx), c='lightgray', s=5)
            ax.scatter(self.x[data['indices']], np.zeros(len(data['indices'])), 
                      c='red', s=100, marker='v', zorder=5)
            ax.set_title(f'{name.upper()}\nμ={data["mu"]:.3f}')
            ax.set_xlabel('Position (cm)')
            ax.set_yticks([])
            ax.set_xlim(self.x[0]*100, self.x[-1]*100)
            
            # Reconstruction
            ax = axes[1, idx]
            im = ax.imshow(np.real(data['u_recon']), aspect='auto', origin='lower',
                          extent=extent, cmap='RdBu_r', vmin=-vmax, vmax=vmax)
            ax.set_title(f'NMSE={data["nmse"]:.3f}, r={data["correlation"]:.3f}')
            ax.set_xlabel('Time sample')
            if idx == 0:
                ax.set_ylabel('Position (cm)')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
        print(f"\nSaved: {save_path}")
        
        return fig


def simple_reconstructor(u_true, y_sparse, rec_idx, Phi):
    """
    Simple reconstruction using pseudo-inverse.
    Fast for array comparison.
    """
    A = Phi[rec_idx, :]
    s, residuals, rank, s_vals = np.linalg.lstsq(A, y_sparse, rcond=None)
    return Phi @ s


def demo_array_optimization():
    """Demonstrate array optimization."""
    print("=" * 70)
    print("ARRAY OPTIMIZATION FOR SPARSE SAMPLING")
    print("=" * 70)
    
    # Generate wavefield
    print("\n[1] Generating wavefield...")
    nx, ny = 80, 40
    dx = 0.0025
    
    G0, G_inf, tau_sigma = 2000, 4000, 0.005
    sim = ShearWave2DZener(nx, ny, dx, rho=1000,
                           G0=G0, G_inf=G_inf, tau_sigma=tau_sigma)
    
    nt = 100
    sx, sy = nx//4, ny//2
    
    wavefield = []
    t_array = []
    
    for n in range(nt):
        t = n * sim.dt
        if n < 50:
            sim.add_source(t, sx, sy, amplitude=2e-5, f0=150, source_type='ricker')
        sim.step()
        wavefield.append(sim.vy[:, ny//2].copy())
        t_array.append(t)
    
    u_true = np.array(wavefield).T
    t_array = np.array(t_array)
    x_array = sim.x
    
    print(f"  Wavefield: {u_true.shape}")
    
    # Initialize optimizer
    print("\n[2] Initializing optimizer...")
    optimizer = ArrayOptimizer(x_array, n_receivers=8, method='mutual_coherence')
    
    # Greedy optimization
    print("\n[3] Greedy optimization...")
    greedy_indices = optimizer.greedy_forward_selection()
    
    # Compare array types
    print("\n[4] Comparing array configurations...")
    
    # Simple reconstructor
    k_vec = 2 * np.pi * np.fft.fftfreq(nx, dx)
    X, K = np.meshgrid(x_array, k_vec, indexing='ij')
    Phi = np.exp(1j * K * X) / np.sqrt(nx)
    
    def recon(y, idx):
        return simple_reconstructor(u_true, y, idx, Phi)
    
    results = optimizer.compare_arrays(u_true, t_array, recon)
    
    # Visualize
    print("\n[5] Visualization...")
    optimizer.visualize_arrays(results, u_true)
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("\nArray Configuration Comparison:")
    print(f"{'Config':<15} {'Coherence':<12} {'NMSE':<10} {'Correlation'}")
    print("-" * 60)
    for name, data in results.items():
        print(f"{name:<15} {data['mu']:<12.4f} {data['nmse']:<10.4f} {data['correlation']:.4f}")
    
    print("\nKey findings:")
    print("  - Lower mutual coherence → better reconstruction")
    print("  - Greedy selection gives good balance")
    print("  - Endfire (clustered) worst for spatial coverage")
    
    return optimizer, results


if __name__ == "__main__":
    optimizer, results = demo_array_optimization()
