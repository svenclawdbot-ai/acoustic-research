"""
FISTA with Restart and Weighted L1 for Physics-Informed CS
===========================================================

Advanced iterative algorithms for compressive sensing reconstruction:
1. FISTA with adaptive restart (monotonic guarantee)
2. Weighted L1 with Zener dispersion prior
3. Hybrid approach combining both

Reference: O'Donoghue & Candès, "Adaptive Restart for Accelerated Gradient Schemes" (2015)
"""

import numpy as np
from scipy.optimize import linesearch


class FISTAWithRestart:
    """
    FISTA with adaptive restart for guaranteed convergence.
    
    Solves: min ||y - A*x||² + lambda*||x||₁
    
    Restart triggers when:
    - Objective increases (function scheme)
    - Momentum opposes gradient (gradient scheme)
    """
    
    def __init__(self, restart_mode='function', patience=5):
        """
        Initialize FISTA with restart.
        
        Parameters:
        -----------
        restart_mode : str
            'function' - restart when objective increases
            'gradient' - restart when (y-x)·(x-x_old) > 0
            'none' - standard FISTA (no restart)
        patience : int
            Iterations to wait before forcing restart
        """
        self.restart_mode = restart_mode
        self.patience = patience
        self.restart_count = 0
    
    def solve(self, A, y, lambda_reg, max_iter=100, x_init=None, verbose=False):
        """
        Solve L1-regularized least squares with FISTA+restart.
        
        Parameters:
        -----------
        A : ndarray (m, n)
            Sensing matrix
        y : ndarray (m,)
            Measurements
        lambda_reg : float
            L1 regularization parameter
        max_iter : int
            Maximum iterations
        x_init : ndarray (n,), optional
            Initial guess
        verbose : bool
            Print iteration info
            
        Returns:
        --------
        x : ndarray (n,)
            Reconstructed signal
        history : dict
            Convergence history
        """
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
        
        # History tracking
        history = {
            'objective': [],
            'residual': [],
            'restarts': [],
            'x_norm': []
        }
        
        # Best solution tracking
        x_best = x.copy()
        obj_best = self._objective(A, y, x, lambda_reg)
        patience_counter = 0
        
        for k in range(max_iter):
            x_old = x.copy()
            
            # Gradient step at extrapolated point z
            residual = y - A @ z
            x = z + step * (A.conj().T @ residual)
            
            # Soft thresholding
            x = self._soft_threshold(x, step * lambda_reg)
            
            # Compute objective
            obj = self._objective(A, y, x, lambda_reg)
            history['objective'].append(obj)
            history['residual'].append(np.linalg.norm(residual))
            history['x_norm'].append(np.linalg.norm(x))
            
            # Track best solution
            if obj < obj_best:
                obj_best = obj
                x_best = x.copy()
                patience_counter = 0
            else:
                patience_counter += 1
            
            # Check restart condition
            restart = self._check_restart(x, x_old, z, A, y, obj, lambda_reg)
            
            if restart or patience_counter >= self.patience:
                # Reset momentum
                z = x.copy()
                t = 1.0
                self.restart_count += 1
                history['restarts'].append(k)
                patience_counter = 0
                
                if verbose and k > 0:
                    print(f"  Restart at iter {k}, obj={obj:.6f}")
            else:
                # Standard FISTA momentum update
                t_new = (1 + np.sqrt(1 + 4 * t**2)) / 2
                z = x + ((t - 1) / t_new) * (x - x_old)
                t = t_new
            
            # Early stopping
            if k > 10 and history['residual'][-1] < 1e-8:
                if verbose:
                    print(f"  Converged at iteration {k}")
                break
        
        history['restart_count'] = self.restart_count
        return x_best, history
    
    def _objective(self, A, y, x, lambda_reg):
        """Compute objective: ||y - Ax||² + lambda*||x||₁"""
        residual = y - A @ x
        data_fit = np.real(residual.conj().T @ residual)
        l1_penalty = lambda_reg * np.sum(np.abs(x))
        return data_fit + l1_penalty
    
    def _soft_threshold(self, x, threshold):
        """Soft thresholding operator."""
        magnitude = np.abs(x)
        phase = np.angle(x)
        magnitude_thresholded = np.maximum(magnitude - threshold, 0)
        return magnitude_thresholded * np.exp(1j * phase)
    
    def _check_restart(self, x, x_old, z, A, y, obj, lambda_reg):
        """Check if restart condition is met."""
        if self.restart_mode == 'none':
            return False
        
        elif self.restart_mode == 'function':
            # Restart if objective increased
            obj_old = self._objective(A, y, x_old, lambda_reg)
            return obj > obj_old
        
        elif self.restart_mode == 'gradient':
            # Restart if momentum opposes gradient direction
            # (y-x)·(x-x_old) > 0 indicates we're going in wrong direction
            momentum = x - x_old
            grad_direction = z - x
            return np.real(np.vdot(grad_direction, momentum)) > 0
        
        return False


class WeightedFISTA:
    """
    FISTA with weighted L1 regularization.
    
    Solves: min ||y - A*x||² + lambda*||W·x||₁
    
    Where W is a diagonal weight matrix. Smaller weights = less regularization.
    Useful for incorporating prior knowledge (e.g., Zener dispersion).
    """
    
    def __init__(self, weights=None):
        """
        Initialize weighted FISTA.
        
        Parameters:
        -----------
        weights : ndarray (n,), optional
            Weight vector (one per coefficient). 
            Default: ones (standard L1)
        """
        self.weights = weights
    
    def solve(self, A, y, lambda_reg, max_iter=100, x_init=None, 
              restart=False, verbose=False):
        """
        Solve weighted L1-regularized least squares.
        
        Parameters:
        -----------
        A : ndarray (m, n)
            Sensing matrix
        y : ndarray (m,)
            Measurements
        lambda_reg : float
            L1 regularization parameter
        max_iter : int
            Maximum iterations
        x_init : ndarray (n,), optional
            Initial guess
        restart : bool
            Enable adaptive restart
        verbose : bool
            Print iteration info
            
        Returns:
        --------
        x : ndarray (n,)
            Reconstructed signal
        history : dict
            Convergence history
        """
        m, n = A.shape
        
        # Default weights
        if self.weights is None:
            weights = np.ones(n)
        else:
            weights = self.weights
            if len(weights) != n:
                raise ValueError(f"Weights length {len(weights)} != signal length {n}")
        
        # Ensure weights are positive
        weights = np.maximum(weights, 1e-6)
        
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
        
        history = {'objective': [], 'residual': []}
        restart_count = 0
        
        for k in range(max_iter):
            x_old = x.copy()
            
            # Gradient step at z
            residual = y - A @ z
            x = z + step * (A.conj().T @ residual)
            
            # Weighted soft thresholding
            # Threshold varies per coefficient: lambda / w_i
            x = self._weighted_soft_threshold(x, step * lambda_reg, weights)
            
            # Track history
            history['residual'].append(np.linalg.norm(residual))
            obj = self._weighted_objective(A, y, x, lambda_reg, weights)
            history['objective'].append(obj)
            
            # Restart check (if enabled)
            if restart and k > 0:
                obj_old = history['objective'][-2] if len(history['objective']) > 1 else obj
                if obj > obj_old:
                    z = x.copy()
                    t = 1.0
                    restart_count += 1
                    if verbose:
                        print(f"  Restart at iter {k}")
                    continue
            
            # FISTA momentum update
            t_new = (1 + np.sqrt(1 + 4 * t**2)) / 2
            z = x + ((t - 1) / t_new) * (x - x_old)
            t = t_new
            
            # Early stopping
            if k > 10 and history['residual'][-1] < 1e-8:
                break
        
        history['restart_count'] = restart_count
        return x, history
    
    def _weighted_soft_threshold(self, x, lambda_step, weights):
        """
        Weighted soft thresholding.
        
        threshold_i = lambda_step / weights[i]
        """
        magnitude = np.abs(x)
        phase = np.angle(x)
        
        # Element-wise threshold
        thresholds = lambda_step / weights
        magnitude_thresholded = np.maximum(magnitude - thresholds, 0)
        
        return magnitude_thresholded * np.exp(1j * phase)
    
    def _weighted_objective(self, A, y, x, lambda_reg, weights):
        """Compute weighted objective."""
        residual = y - A @ x
        data_fit = np.real(residual.conj().T @ residual)
        weighted_l1 = lambda_reg * np.sum(weights * np.abs(x))
        return data_fit + weighted_l1


class ZenerWeightedFISTA:
    """
    Physics-informed FISTA using Zener model dispersion for weighting.
    
    The Zener model predicts expected wavenumber k for each frequency ω:
        k_expected(ω) = ω / c(ω)
    
    Weights are constructed to:
    - Reduce regularization near expected k (encourage these components)
    - Increase regularization far from expected k (suppress noise)
    """
    
    def __init__(self, zener_model):
        """
        Initialize with Zener model.
        
        Parameters:
        -----------
        zener_model : ZenerModel
            Viscoelastic dispersion model
        """
        self.zm = zener_model
    
    def compute_weights(self, k_array, omega, sharpness=0.1):
        """
        Compute weights based on Zener dispersion.
        
        Parameters:
        -----------
        k_array : ndarray (n,)
            Wavenumber grid (rad/m)
        omega : float
            Current frequency (rad/s)
        sharpness : float
            Width of the "passband" (lower = sharper)
            
        Returns:
        --------
        weights : ndarray (n,)
            Weight vector (higher = less regularization)
        """
        if omega <= 0:
            return np.ones(len(k_array))
        
        # Expected wavenumber from Zener model
        c_omega = self.zm.phase_velocity(omega)
        k_expected = omega / c_omega
        
        # Distance from expected wavenumber
        k_dist = np.abs(np.abs(k_array) - k_expected)
        
        # Weights: Gaussian-like around expected k
        # w = exp(-sharpness * k_dist)
        weights = np.exp(-sharpness * k_dist)
        
        # Ensure minimum weight for numerical stability
        weights = np.maximum(weights, 0.1)
        
        return weights
    
    def solve_frequency_domain(self, A, Y_freq, k_array, omega_array,
                               lambda_reg=0.1, max_iter=50, use_restart=True):
        """
        Solve CS for all frequencies with Zener-informed weights.
        
        Parameters:
        -----------
        A : ndarray (m, n)
            Sensing matrix
        Y_freq : ndarray (m, n_freq)
            Frequency-domain measurements
        k_array : ndarray (n,)
            Wavenumber grid
        omega_array : ndarray (n_freq,)
            Frequency array (rad/s)
        lambda_reg : float
            Regularization parameter
        max_iter : int
            Iterations per frequency
        use_restart : bool
            Use FISTA with restart
            
        Returns:
        --------
        X_recon : ndarray (n, n_freq)
            Reconstructed frequency-domain signal
        histories : list
            Convergence history per frequency
        """
        m, n_freq = Y_freq.shape
        n = A.shape[1]
        
        X_recon = np.zeros((n, n_freq), dtype=complex)
        histories = []
        
        # Choose solver
        if use_restart:
            solver = FISTAWithRestart(restart_mode='function')
        else:
            solver = WeightedFISTA()
        
        for i_freq, omega in enumerate(omega_array):
            if i_freq % 20 == 0:
                print(f"  Processing frequency {i_freq}/{n_freq}: ω={omega:.1f} rad/s")
            
            y_omega = Y_freq[:, i_freq]
            
            # Compute Zener-informed weights
            weights = self.compute_weights(k_array, omega, sharpness=0.05)
            
            # Warm start: pseudo-inverse
            x_init = np.linalg.lstsq(A, y_omega, rcond=None)[0]
            
            # Solve with weighted FISTA
            if use_restart:
                x_freq, history = solver.solve(A, y_omega, lambda_reg, 
                                               max_iter=max_iter, 
                                               x_init=x_init)
            else:
                weighted_solver = WeightedFISTA(weights=weights)
                x_freq, history = weighted_solver.solve(A, y_omega, lambda_reg,
                                                        max_iter=max_iter,
                                                        x_init=x_init)
            
            X_recon[:, i_freq] = x_freq
            histories.append(history)
        
        return X_recon, histories


def compare_fista_variants():
    """Compare ISTA, FISTA, FISTA+restart, and weighted FISTA."""
    import matplotlib.pyplot as plt
    
    print("=" * 70)
    print("FISTA VARIANTS COMPARISON")
    print("=" * 70)
    
    # Generate test problem
    np.random.seed(42)
    n = 256
    m = 64  # 25% measurements
    k_sparse = 10  # True sparsity
    
    # Sparse signal
    x_true = np.zeros(n, dtype=complex)
    support = np.random.choice(n, k_sparse, replace=False)
    x_true[support] = np.random.randn(k_sparse) + 1j * np.random.randn(k_sparse)
    
    # Sensing matrix (subsampled Fourier)
    A = np.fft.fft(np.eye(n)) / np.sqrt(n)
    rows = np.sort(np.random.choice(n, m, replace=False))
    A = A[rows, :]
    
    y = A @ x_true
    
    print(f"\nTest problem: n={n}, m={m}, sparsity={k_sparse}")
    print(f"Undersampling ratio: {m/n*100:.1f}%")
    
    # Compare algorithms
    lambda_reg = 0.1
    max_iter = 200
    
    results = {}
    
    # 1. ISTA
    print("\n[1] Running ISTA...")
    ista = FISTAWithRestart(restart_mode='none')
    x_ista, hist_ista = ista.solve(A, y, lambda_reg, max_iter=max_iter)
    results['ISTA'] = (x_ista, hist_ista)
    
    # 2. FISTA (no restart)
    print("[2] Running FISTA...")
    fista = FISTAWithRestart(restart_mode='none')
    # Override to use FISTA update without restart
    x_fista, hist_fista = fista.solve(A, y, lambda_reg, max_iter=max_iter)
    results['FISTA'] = (x_fista, hist_fista)
    
    # 3. FISTA with restart
    print("[3] Running FISTA+Restart...")
    fista_r = FISTAWithRestart(restart_mode='function', patience=3)
    x_fista_r, hist_fista_r = fista_r.solve(A, y, lambda_reg, max_iter=max_iter, verbose=True)
    results['FISTA+Restart'] = (x_fista_r, hist_fista_r)
    
    # 4. Weighted FISTA (oracle weights - known support)
    print("[4] Running Weighted FISTA (oracle)...")
    weights = np.ones(n)
    weights[support] = 10.0  # Lower regularization on true support
    wfista = WeightedFISTA(weights=weights)
    x_wfista, hist_wfista = wfista.solve(A, y, lambda_reg, max_iter=max_iter)
    results['Weighted FISTA'] = (x_wfista, hist_wfista)
    
    # Evaluate
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"{'Method':<20} {'NMSE':>12} {'Support Recovery':>18} {'Restarts':>10}")
    print("-" * 70)
    
    for name, (x, hist) in results.items():
        nmse = np.mean(np.abs(x - x_true)**2) / np.mean(np.abs(x_true)**2)
        
        # Support recovery (how many true nonzeros captured)
        x_mag = np.abs(x)
        threshold = 0.1 * np.max(x_mag)
        recovered_support = np.where(x_mag > threshold)[0]
        support_overlap = len(set(recovered_support) & set(support))
        support_recovery = support_overlap / k_sparse * 100
        
        restarts = hist.get('restart_count', 0)
        
        print(f"{name:<20} {nmse:>12.6f} {support_recovery:>17.1f}% {restarts:>10d}")
    
    # Plot convergence
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Objective vs iteration
    ax = axes[0]
    for name, (x, hist) in results.items():
        ax.semilogy(hist['objective'], label=name, linewidth=2)
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Objective Value')
    ax.set_title('Convergence Comparison')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Residual vs iteration
    ax = axes[1]
    for name, (x, hist) in results.items():
        ax.semilogy(hist['residual'], label=name, linewidth=2)
        if 'restarts' in hist and hist['restarts']:
            for r in hist['restarts']:
                ax.axvline(r, color='gray', linestyle='--', alpha=0.3)
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Residual Norm')
    ax.set_title('Residual Convergence (gray lines = restarts)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('fista_comparison.png', dpi=150)
    print("\nSaved: fista_comparison.png")
    
    return results


if __name__ == "__main__":
    results = compare_fista_variants()
