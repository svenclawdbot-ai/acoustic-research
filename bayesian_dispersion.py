#!/usr/bin/env python3
"""
Bayesian Parameter Estimation for Shear Wave Dispersion
=========================================================

Implements MCMC sampling for Kelvin-Voigt parameter estimation
from noisy dispersion curves. Provides credible intervals and
proper uncertainty quantification.

Author: Research Project
Date: April 17, 2026
"""

import numpy as np
from scipy.optimize import curve_fit
from typing import Dict, Tuple, Optional, Callable
import warnings

# Try to import emcee for MCMC
# We'll handle if it's not installed
EMCEE_AVAILABLE = False
DYNESTY_AVAILABLE = False

try:
    import emcee
    EMCEE_AVAILABLE = True
except ImportError:
    pass

try:
    import dynesty
    DYNESTY_AVAILABLE = True
except ImportError:
    pass


def kelvin_voigt_velocity(omega: np.ndarray, G_prime: float, eta: float, 
                          rho: float = 1000) -> np.ndarray:
    """
    Calculate phase velocity from Kelvin-Voigt model.
    
    Parameters:
    -----------
    omega : array
        Angular frequencies (rad/s)
    G_prime : float
        Storage modulus (Pa)
    eta : float
        Viscosity (Pa·s)
    rho : float
        Density (kg/m³)
        
    Returns:
    --------
    velocity : array
        Phase velocities (m/s)
    """
    G_mag = np.sqrt(G_prime**2 + (omega * eta)**2)
    c = np.sqrt(2 / rho) * np.sqrt(G_mag**2 / (G_prime + G_mag))
    return c


def log_likelihood(params: np.ndarray, omega: np.ndarray, 
                   velocities: np.ndarray, uncertainties: np.ndarray,
                   rho: float = 1000) -> float:
    """
    Gaussian log-likelihood for dispersion data.
    
    For each frequency point:
    log L_i = -0.5 * [(v_meas - v_model)²/σ² + log(2πσ²)]
    
    Parameters:
    -----------
    params : array [G_prime, eta]
        Parameters to evaluate
    omega : array
        Angular frequencies (rad/s)
    velocities : array
        Measured phase velocities (m/s)
    uncertainties : array
        Measurement uncertainties (m/s)
    rho : float
        Density (kg/m³)
        
    Returns:
    --------
    log_l : float
        Log-likelihood value
    """
    G_prime, eta = params
    
    # Compute model velocities
    c_model = kelvin_voigt_velocity(omega, G_prime, eta, rho)
    
    # Gaussian likelihood
    residuals = velocities - c_model
    sigma = uncertainties
    
    # Avoid division by zero
    sigma = np.where(sigma < 1e-10, 1e-10, sigma)
    
    chi2 = np.sum((residuals / sigma)**2)
    log_norm = np.sum(np.log(2 * np.pi * sigma**2))
    
    return -0.5 * (chi2 + log_norm)


def log_prior(params: np.ndarray, 
              G_min: float = 100, G_max: float = 50000,
              eta_min: float = 0.001, eta_max: float = 100) -> float:
    """
    Log-uniform prior for Kelvin-Voigt parameters.
    
    Parameters:
    -----------
    params : array [G_prime, eta]
        Parameters to evaluate
    G_min, G_max : float
        Storage modulus bounds (Pa)
    eta_min, eta_max : float
        Viscosity bounds (Pa·s)
        
    Returns:
    --------
    log_p : float
        Log-prior value (-inf if outside bounds)
    """
    G_prime, eta = params
    
    # Check bounds
    if not (G_min <= G_prime <= G_max):
        return -np.inf
    if not (eta_min <= eta <= eta_max):
        return -np.inf
    
    # Log-uniform prior: p(θ) = 1/(θ * log(θ_max/θ_min))
    log_p_G = -np.log(G_prime) - np.log(np.log(G_max / G_min))
    log_p_eta = -np.log(eta) - np.log(np.log(eta_max / eta_min))
    
    return log_p_G + log_p_eta


def log_probability(params: np.ndarray, omega: np.ndarray,
                    velocities: np.ndarray, uncertainties: np.ndarray,
                    rho: float = 1000) -> float:
    """
    Log-probability = log-prior + log-likelihood.
    """
    lp = log_prior(params)
    if not np.isfinite(lp):
        return -np.inf
    return lp + log_likelihood(params, omega, velocities, uncertainties, rho)


def fit_frequentist(freq: np.ndarray, vel: np.ndarray, unc: np.ndarray,
                    rho: float = 1000) -> Dict:
    """
    Frequentist fit using curve_fit (MLE).
    
    Returns:
    --------
    dict with G_prime, eta, errors, and R²
    """
    def kv_model(omega, Gp, et):
        Gm = np.sqrt(Gp**2 + (omega*et)**2)
        return np.sqrt(2/rho) * np.sqrt(Gm**2 / (Gp + Gm))
    
    omega = 2 * np.pi * freq
    
    c0 = np.median(vel) if len(vel) > 0 else 1.5
    G0 = max(100, min(rho * c0**2, 50000))
    eta0 = 0.5
    
    try:
        popt, pcov = curve_fit(kv_model, omega, vel, p0=[G0, eta0],
                              bounds=([10, 0.001], [100000, 100]),
                              sigma=unc, maxfev=5000)
        
        G_prime, eta = popt
        G_err, eta_err = np.sqrt(np.diag(pcov))
        
        residuals = vel - kv_model(omega, *popt)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((vel - np.mean(vel))**2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        return {
            'G_prime': G_prime, 'eta': eta,
            'G_prime_err': G_err, 'eta_err': eta_err,
            'r_squared': r2, 'success': True
        }
    except Exception as e:
        return {
            'G_prime': G0, 'eta': eta0,
            'G_prime_err': np.nan, 'eta_err': np.nan,
            'r_squared': 0, 'success': False, 'error': str(e)
        }


def fit_bayesian_emcee(freq: np.ndarray, vel: np.ndarray, unc: np.ndarray,
                       rho: float = 1000, n_walkers: int = 32,
                       n_steps: int = 5000, burn_in: int = 1000,
                       progress: bool = True) -> Dict:
    """
    Bayesian fit using emcee ensemble MCMC sampler.
    
    Parameters:
    -----------
    freq : array
        Frequencies (Hz)
    vel : array
        Phase velocities (m/s)
    unc : array
        Uncertainties (m/s)
    rho : float
        Density (kg/m³)
    n_walkers : int
        Number of MCMC walkers
    n_steps : int
        Number of steps per walker
    burn_in : int
        Number of burn-in steps to discard
    progress : bool
        Show progress bar
        
    Returns:
    --------
    dict with posterior samples and summary statistics
    """
    if not EMCEE_AVAILABLE:
        raise ImportError("emcee not installed. Install with: pip install emcee")
    
    omega = 2 * np.pi * freq
    
    # Initial guess from frequentist fit
    freq_result = fit_frequentist(freq, vel, unc, rho)
    p0_guess = np.array([freq_result['G_prime'], freq_result['eta']])
    
    # Initialize walkers around the guess
    n_dim = 2
    pos = []
    for _ in range(n_walkers):
        # Add small random perturbation
        perturbation = np.array([0.1 * p0_guess[0], 0.2 * p0_guess[1]])
        walker_pos = p0_guess + perturbation * np.random.randn(n_dim)
        walker_pos = np.abs(walker_pos)  # Ensure positive
        pos.append(walker_pos)
    
    # Create sampler
    sampler = emcee.EnsembleSampler(
        n_walkers, n_dim, log_probability,
        args=(omega, vel, unc, rho)
    )
    
    # Run MCMC
    if progress:
        from tqdm import tqdm
        for _ in tqdm(sampler.sample(pos, iterations=n_steps), total=n_steps):
            pass
    else:
        sampler.run_mcmc(pos, n_steps)
    
    # Extract samples (after burn-in)
    samples = sampler.get_chain(discard=burn_in, flat=True)
    
    # Compute statistics
    G_samples = samples[:, 0]
    eta_samples = samples[:, 1]
    
    # 16th, 50th, 84th percentiles
    G_median = np.median(G_samples)
    G_16, G_84 = np.percentile(G_samples, [16, 84])
    
    eta_median = np.median(eta_samples)
    eta_16, eta_84 = np.percentile(eta_samples, [16, 84])
    
    # Also compute mean and std for comparison
    G_mean = np.mean(G_samples)
    G_std = np.std(G_samples)
    eta_mean = np.mean(eta_samples)
    eta_std = np.std(eta_samples)
    
    return {
        'G_prime_median': G_median,
        'G_prime_mean': G_mean,
        'G_prime_std': G_std,
        'G_prime_16': G_16,
        'G_prime_84': G_84,
        'G_prime_ci': (G_16, G_84),
        'eta_median': eta_median,
        'eta_mean': eta_mean,
        'eta_std': eta_std,
        'eta_16': eta_16,
        'eta_84': eta_84,
        'eta_ci': (eta_16, eta_84),
        'samples': samples,
        'sampler': sampler,
        'acceptance_fraction': np.mean(sampler.acceptance_fraction),
        'autocorr_time': sampler.get_autocorr_time() if n_steps > 100 else None
    }


def plot_likelihood_surface(freq: np.ndarray, vel: np.ndarray, unc: np.ndarray,
                            true_G: float = None, true_eta: float = None,
                            rho: float = 1000, save_path: str = 'likelihood_surface.png'):
    """
    Plot likelihood surface over (G', η) grid.
    """
    import matplotlib.pyplot as plt
    
    omega = 2 * np.pi * freq
    
    # Create parameter grid
    G_range = np.logspace(2, 4.5, 100)  # 100 to ~30000 Pa
    eta_range = np.logspace(-2, 1, 100)  # 0.01 to 10 Pa·s
    G_grid, eta_grid = np.meshgrid(G_range, eta_range)
    
    # Compute log-likelihood at each point
    log_l = np.zeros_like(G_grid)
    for i in range(len(eta_range)):
        for j in range(len(G_range)):
            params = np.array([G_grid[i, j], eta_grid[i, j]])
            log_l[i, j] = log_likelihood(params, omega, vel, unc, rho)
    
    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Log-likelihood
    ax = axes[0]
    vmax = np.percentile(log_l, 99)
    vmin = vmax - 20  # Show 20 log-likelihood units from peak
    im = ax.pcolormesh(G_grid, eta_grid, log_l, shading='gouraud',
                       vmin=vmin, vmax=vmax, cmap='viridis')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel("G' (Pa)")
    ax.set_ylabel('η (Pa·s)')
    ax.set_title('Log-Likelihood Surface')
    plt.colorbar(im, ax=ax, label='log L')
    
    if true_G is not None and true_eta is not None:
        ax.plot(true_G, true_eta, 'r*', markersize=15, label='True')
        ax.legend()
    
    # Chi-squared (more intuitive)
    ax = axes[1]
    chi2 = -2 * (log_l - np.max(log_l))  # Delta chi2 from peak
    levels = [1, 4, 9, 16]  # 1, 2, 3, 4 sigma contours
    cs = ax.contour(G_grid, eta_grid, chi2, levels=levels, colors='black')
    ax.clabel(cs, inline=True, fontsize=8)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel("G' (Pa)")
    ax.set_ylabel('η (Pa·s)')
    ax.set_title('Δχ² Contours (1σ, 2σ, 3σ, 4σ)')
    
    if true_G is not None and true_eta is not None:
        ax.plot(true_G, true_eta, 'r*', markersize=15, label='True')
        ax.legend()
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Saved: {save_path}")
    
    return fig


def plot_corner(bayesian_result: Dict, true_G: float = None, 
                true_eta: float = None, save_path: str = 'corner_plot.png'):
    """
    Create corner plot of posterior samples.
    """
    samples = bayesian_result['samples']
    
    # Try to use corner package if available
    try:
        import corner
        fig = corner.corner(samples, labels=["G' (Pa)", 'η (Pa·s)'],
                           truths=[true_G, true_eta] if true_G else None,
                           quantiles=[0.16, 0.5, 0.84],
                           show_titles=True, title_kwargs={"fontsize": 12})
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
        return fig
    except ImportError:
        # Fallback to simple scatter plots
        import matplotlib.pyplot as plt
        
        fig, axes = plt.subplots(2, 2, figsize=(10, 10))
        
        G_samples = samples[:, 0]
        eta_samples = samples[:, 1]
        
        # G' histogram
        ax = axes[0, 0]
        ax.hist(G_samples, bins=50, alpha=0.7, color='blue', edgecolor='black')
        ax.axvline(bayesian_result['G_prime_median'], color='red', linestyle='--',
                   label=f"Median: {bayesian_result['G_prime_median']:.0f}")
        if true_G:
            ax.axvline(true_G, color='green', linestyle='--', label=f'True: {true_G:.0f}')
        ax.set_xlabel("G' (Pa)")
        ax.set_ylabel('Probability')
        ax.legend()
        ax.set_title("G' Posterior")
        
        # Scatter plot
        ax = axes[0, 1]
        ax.scatter(G_samples[::10], eta_samples[::10], alpha=0.3, s=1)
        ax.scatter(bayesian_result['G_prime_median'], bayesian_result['eta_median'],
                   color='red', marker='x', s=100, label='Median')
        if true_G and true_eta:
            ax.scatter(true_G, true_eta, color='green', marker='*', s=200, label='True')
        ax.set_xlabel("G' (Pa)")
        ax.set_ylabel('η (Pa·s)')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.legend()
        ax.set_title('Parameter Space')
        
        # η histogram
        ax = axes[1, 0]
        ax.hist(eta_samples, bins=50, alpha=0.7, color='blue', edgecolor='black')
        ax.axvline(bayesian_result['eta_median'], color='red', linestyle='--',
                   label=f"Median: {bayesian_result['eta_median']:.3f}")
        if true_eta:
            ax.axvline(true_eta, color='green', linestyle='--', label=f'True: {true_eta:.3f}')
        ax.set_xlabel('η (Pa·s)')
        ax.set_ylabel('Probability')
        ax.legend()
        ax.set_title('η Posterior')
        
        # Empty subplot
        axes[1, 1].axis('off')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
        return fig


def plot_posterior_predictive(freq: np.ndarray, vel: np.ndarray, unc: np.ndarray,
                              bayesian_result: Dict, true_G: float = None,
                              true_eta: float = None, rho: float = 1000,
                              n_curves: int = 100,
                              save_path: str = 'posterior_predictive.png'):
    """
    Plot posterior predictive distribution.
    
    Samples from posterior and plots model curves to show uncertainty.
    """
    import matplotlib.pyplot as plt
    
    samples = bayesian_result['samples']
    omega_data = 2 * np.pi * freq
    
    # Fine frequency grid for smooth curves
    freq_fine = np.linspace(freq.min(), freq.max(), 200)
    omega_fine = 2 * np.pi * freq_fine
    
    # Sample curves from posterior
    velocities_curves = []
    for i in range(n_curves):
        idx = np.random.randint(0, len(samples))
        G_s, eta_s = samples[idx]
        c_curve = kelvin_voigt_velocity(omega_fine, G_s, eta_s, rho)
        velocities_curves.append(c_curve)
    
    velocities_curves = np.array(velocities_curves)
    
    # Compute percentiles
    v_median = np.median(velocities_curves, axis=0)
    v_16 = np.percentile(velocities_curves, 16, axis=0)
    v_84 = np.percentile(velocities_curves, 84, axis=0)
    v_2_5 = np.percentile(velocities_curves, 2.5, axis=0)
    v_97_5 = np.percentile(velocities_curves, 97.5, axis=0)
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Individual samples (thin grey)
    for i in range(min(n_curves, 50)):
        ax.plot(freq_fine, velocities_curves[i], 'grey', alpha=0.2, linewidth=0.5)
    
    # Credible bands
    ax.fill_between(freq_fine, v_2_5, v_97_5, alpha=0.2, color='blue', label='95% CI')
    ax.fill_between(freq_fine, v_16, v_84, alpha=0.3, color='blue', label='68% CI')
    ax.plot(freq_fine, v_median, 'b-', linewidth=2, label='Median model')
    
    # Data with error bars
    ax.errorbar(freq, vel, yerr=unc, fmt='ro', capsize=3, markersize=6,
                label='Data', zorder=10)
    
    # True model
    if true_G and true_eta:
        c_true = kelvin_voigt_velocity(omega_fine, true_G, true_eta, rho)
        ax.plot(freq_fine, c_true, 'g--', linewidth=2, label='True')
    
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Phase Velocity (m/s)')
    ax.set_title('Posterior Predictive Distribution')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Saved: {save_path}")
    
    return fig


def compare_bayesian_frequentist(freq: np.ndarray, vel: np.ndarray, unc: np.ndarray,
                                 true_G: float, true_eta: float, rho: float = 1000,
                                 noise_label: str = ""):
    """
    Compare Bayesian and frequentist approaches on a single dataset.
    """
    print(f"\n{'='*70}")
    print(f"Comparison: {noise_label}")
    print(f"{'='*70}")
    print(f"True: G' = {true_G:.0f} Pa, η = {true_eta:.3f} Pa·s")
    print(f"Data: {len(freq)} frequency points")
    
    # Frequentist fit
    print("\n--- Frequentist (curve_fit) ---")
    freq_result = fit_frequentist(freq, vel, unc, rho)
    if freq_result['success']:
        print(f"G' = {freq_result['G_prime']:.0f} ± {freq_result['G_prime_err']:.0f} Pa")
        print(f"η = {freq_result['eta']:.3f} ± {freq_result['eta_err']:.3f} Pa·s")
        print(f"R² = {freq_result['r_squared']:.4f}")
        
        G_in_ci = abs(freq_result['G_prime'] - true_G) < freq_result['G_prime_err']
        eta_in_ci = abs(freq_result['eta'] - true_eta) < freq_result['eta_err']
        print(f"True G' in 1σ CI: {G_in_ci}")
        print(f"True η in 1σ CI: {eta_in_ci}")
    else:
        print("Fit failed!")
    
    # Bayesian fit
    if EMCEE_AVAILABLE:
        print("\n--- Bayesian (MCMC) ---")
        try:
            bayes_result = fit_bayesian_emcee(freq, vel, unc, rho, 
                                              n_walkers=32, n_steps=3000,
                                              burn_in=500, progress=False)
            
            print(f"G' = {bayes_result['G_prime_median']:.0f} "
                  f"({bayes_result['G_prime_16']:.0f}, {bayes_result['G_prime_84']:.0f}) Pa")
            print(f"η = {bayes_result['eta_median']:.3f} "
                  f"({bayes_result['eta_16']:.3f}, {bayes_result['eta_84']:.3f}) Pa·s")
            print(f"Acceptance: {bayes_result['acceptance_fraction']:.3f}")
            
            G_in_ci = (bayes_result['G_prime_16'] <= true_G <= bayes_result['G_prime_84'])
            eta_in_ci = (bayes_result['eta_16'] <= true_eta <= bayes_result['eta_84'])
            print(f"True G' in 68% CI: {G_in_ci}")
            print(f"True η in 68% CI: {eta_in_ci}")
            
            return freq_result, bayes_result
        except Exception as e:
            print(f"MCMC failed: {e}")
            return freq_result, None
    else:
        print("\nemcee not installed — skipping Bayesian analysis")
        print("Install with: pip install emcee")
        return freq_result, None


def run_comparison_suite():
    """
    Run comparison across different data quality scenarios.
    """
    from numpy.polynomial import polynomial as P
    
    print("="*70)
    print("Bayesian vs Frequentist: Shear Wave Dispersion")
    print("="*70)
    
    # True parameters
    true_G = 2000
    true_eta = 0.5
    rho = 1000
    
    # Test scenarios
    scenarios = [
        ("Well-constrained (9 freq, 5% noise)", 
         np.linspace(60, 140, 9), 0.05),
        ("Moderate (7 freq, 10% noise)", 
         np.linspace(60, 140, 7), 0.10),
        ("Poor (5 freq, 15% noise)", 
         np.linspace(60, 140, 5), 0.15),
        ("Very poor (3 freq, 25% noise)", 
         np.linspace(80, 120, 3), 0.25),
    ]
    
    np.random.seed(42)
    
    for label, freqs, noise_level in scenarios:
        omega = 2 * np.pi * freqs
        
        # Generate synthetic data
        c_true = kelvin_voigt_velocity(omega, true_G, true_eta, rho)
        noise = noise_level * c_true * np.random.randn(len(freqs))
        vel = c_true + noise
        unc = noise_level * c_true  # Assume noise level known
        
        # Run comparison
        freq_res, bayes_res = compare_bayesian_frequentist(
            freqs, vel, unc, true_G, true_eta, rho, label
        )


def main():
    """
    Main demonstration of Bayesian parameter estimation.
    """
    print("="*70)
    print("Bayesian Parameter Estimation for Shear Wave Dispersion")
    print("="*70)
    
    if not EMCEE_AVAILABLE:
        print("\nWARNING: emcee not installed. Install with: pip install emcee")
        print("Running in likelihood-only mode...\n")
    
    # Generate test data
    true_G = 2000
    true_eta = 0.5
    rho = 1000
    
    freqs = np.linspace(60, 140, 9)
    omega = 2 * np.pi * freqs
    
    # True velocities
    c_true = kelvin_voigt_velocity(omega, true_G, true_eta, rho)
    
    # Add 10% noise
    np.random.seed(42)
    noise_level = 0.10
    noise = noise_level * c_true * np.random.randn(len(freqs))
    vel = c_true + noise
    unc = noise_level * c_true
    
    print(f"\nTrue parameters: G' = {true_G} Pa, η = {true_eta} Pa·s")
    print(f"Data: {len(freqs)} frequencies, {noise_level*100:.0f}% noise")
    
    # Plot likelihood surface
    print("\n1. Computing likelihood surface...")
    plot_likelihood_surface(freqs, vel, unc, true_G, true_eta, rho)
    
    # Run comparison
    print("\n2. Running parameter estimation...")
    freq_res, bayes_res = compare_bayesian_frequentist(
        freqs, vel, unc, true_G, true_eta, rho, "Test case"
    )
    
    if bayes_res is not None:
        # Plot corner
        print("\n3. Generating corner plot...")
        plot_corner(bayes_res, true_G, true_eta)
        
        # Plot posterior predictive
        print("\n4. Generating posterior predictive...")
        plot_posterior_predictive(freqs, vel, unc, bayes_res, true_G, true_eta, rho)
    
    # Run full comparison suite
    print("\n5. Running comparison suite across scenarios...")
    run_comparison_suite()
    
    print("\n" + "="*70)
    print("Complete!")
    print("="*70)


if __name__ == '__main__':
    main()
