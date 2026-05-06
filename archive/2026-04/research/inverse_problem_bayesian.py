#!/usr/bin/env python3
"""
Inverse Problem: Recover Viscoelastic Parameters from Wave Data
===============================================================

Bayesian inference for (G', η) using analytical forward model.

Forward model: Analytical viscoelastic Green's function
Parameters: G' (storage modulus), η (viscosity)
Data: Displacement time series at receiver positions

Author: Research Project — Week 2 Extension
Date: March 16, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy.special import erfc
from dataclasses import dataclass
from typing import Tuple
import warnings


@dataclass
class ViscoelasticWaveModel:
    """
    Analytical viscoelastic wave propagation model.
    
    Uses Kelvin-Voigt model with analytical solution for 1D point source.
    """
    rho: float = 1000.0  # kg/m³
    
    def compute_waveform(self, t: np.ndarray, r: float, G_prime: float, eta: float, 
                        f0: float = 100.0, amplitude: float = 1e-6) -> np.ndarray:
        """
        Compute viscoelastic waveform at distance r from source.
        
        Uses analytical approximation valid for r > wavelength.
        
        Parameters:
        -----------
        t : time array (s)
        r : distance from source (m)
        G_prime : storage modulus (Pa)
        eta : viscosity (Pa·s)
        f0 : source frequency (Hz)
        amplitude : source amplitude (m)
        
        Returns:
        --------
        u : displacement waveform (m)
        """
        # Wave parameters
        c_s = np.sqrt(G_prime / self.rho)  # Elastic wave speed
        tau = eta / G_prime  # Relaxation time
        
        # Ricker wavelet (second derivative of Gaussian)
        sigma = 1 / (np.pi * f0)
        tau_wave = t - r / c_s - 3 * sigma  # Time shift for propagation
        
        # Geometric spreading (1D)
        spread = 1.0  # No geometric spreading in 1D
        
        # Attenuation from viscosity (exponential decay with distance)
        # For Kelvin-Voigt: attenuation ∝ exp(-α·r) where α ∝ ω²·η/(2·G')
        omega = 2 * np.pi * f0
        alpha = (omega**2 * eta) / (2 * G_prime * c_s)  # Attenuation coefficient
        attenuation = np.exp(-alpha * r)
        
        # Ricker wavelet
        ricker = (1 - 2 * (tau_wave / sigma)**2) * np.exp(-(tau_wave / sigma)**2)
        
        # Dispersion: frequency-dependent phase velocity
        # For Kelvin-Voigt: c(ω) = c_s * sqrt(2) * [(1 + (ωτ)²)^(1/4)] * cos(½ arctan(ωτ))
        omega_tau = omega * tau
        c_dispersed = c_s * np.sqrt(2) * ((1 + omega_tau**2)**0.25) * np.cos(0.5 * np.arctan(omega_tau))
        
        # Correct time delay with dispersion
        tau_corrected = t - r / c_dispersed - 3 * sigma
        ricker_corrected = (1 - 2 * (tau_corrected / sigma)**2) * np.exp(-(tau_corrected / sigma)**2)
        
        u = amplitude * spread * attenuation * ricker_corrected
        
        # Zero out before wave arrives (causality)
        arrival_time = r / c_dispersed - 3 * sigma
        u[t < arrival_time] = 0
        
        return u


@dataclass
class InverseProblem:
    """
    Bayesian inverse problem for (G', η) estimation.
    """
    true_G_prime: float = 5000.0  # Pa
    true_eta: float = 5.0         # Pa·s
    
    # Measurement setup
    receiver_distances: list = None  # meters
    duration: float = 0.04  # 40 ms
    dt: float = 2e-5  # 20 μs sampling
    f0: float = 100.0  # Source frequency
    noise_std: float = 0.01e-6  # 10 nm noise
    
    def __post_init__(self):
        if self.receiver_distances is None:
            # Receivers at 2, 4, 6 cm
            self.receiver_distances = [0.02, 0.04, 0.06]
        
        self.model = ViscoelasticWaveModel()
        self.time = np.arange(0, self.duration, self.dt)
    
    def generate_synthetic_data(self, plot: bool = True) -> Tuple[np.ndarray, np.ndarray, dict]:
        """Generate synthetic measurement data."""
        print("=" * 60)
        print("Generating Synthetic Data")
        print("=" * 60)
        print(f"True parameters:")
        print(f"  G' = {self.true_G_prime} Pa")
        print(f"  η = {self.true_eta} Pa·s")
        print(f"  c_s = {np.sqrt(self.true_G_prime/1000):.2f} m/s")
        
        data = []
        for r in self.receiver_distances:
            waveform = self.model.compute_waveform(
                self.time, r, self.true_G_prime, self.true_eta, self.f0
            )
            data.append(waveform)
        
        data = np.array(data)
        
        # Add measurement noise
        noise = np.random.normal(0, self.noise_std, data.shape)
        data_noisy = data + noise
        
        print(f"\nReceivers at: {[f'{r*100:.0f} cm' for r in self.receiver_distances]}")
        print(f"Time samples: {len(self.time)}")
        print(f"Noise level: {self.noise_std*1e9:.1f} nm")
        
        if plot:
            self._plot_data(data_noisy, data)
        
        metadata = {
            'true_G_prime': self.true_G_prime,
            'true_eta': self.true_eta,
            'receivers': self.receiver_distances
        }
        
        return self.time, data_noisy, metadata
    
    def _plot_data(self, data_noisy: np.ndarray, data_clean: np.ndarray):
        """Plot synthetic data."""
        fig, axes = plt.subplots(len(self.receiver_distances), 1, figsize=(12, 8))
        
        for i, ax in enumerate(axes):
            dist = self.receiver_distances[i] * 100
            ax.plot(self.time * 1000, data_clean[i] * 1e6, 'b-', alpha=0.5, label='Clean')
            ax.plot(self.time * 1000, data_noisy[i] * 1e6, 'r-', alpha=0.5, linewidth=0.5, label='Noisy')
            ax.set_ylabel(f'{dist:.0f} cm (μm)')
            ax.grid(True, alpha=0.3)
            if i == 0:
                ax.legend()
        
        axes[-1].set_xlabel('Time (ms)')
        plt.suptitle('Synthetic Data: True Parameters')
        plt.tight_layout()
        plt.savefig('synthetic_data.png', dpi=150)
        plt.show()
    
    def forward_model(self, G_prime: float, eta: float) -> np.ndarray:
        """Run forward simulation with given parameters."""
        predictions = []
        for r in self.receiver_distances:
            waveform = self.model.compute_waveform(
                self.time, r, G_prime, eta, self.f0
            )
            predictions.append(waveform)
        return np.array(predictions)
    
    def log_likelihood(self, G_prime: float, eta: float, data: np.ndarray) -> float:
        """Gaussian log-likelihood."""
        predictions = self.forward_model(G_prime, eta)
        residuals = data - predictions
        rss = np.sum(residuals**2)
        n = data.size
        logL = -0.5 * n * np.log(2 * np.pi * self.noise_std**2) - rss / (2 * self.noise_std**2)
        return logL
    
    def log_prior(self, G_prime: float, eta: float) -> float:
        """Prior distribution."""
        if not (1000 <= G_prime <= 20000):
            return -np.inf
        if not (0.1 <= eta <= 50):
            return -np.inf
        # Log-uniform prior
        return -np.log(G_prime) - np.log(eta)
    
    def log_posterior(self, params: np.ndarray, data: np.ndarray) -> float:
        """Log posterior."""
        G_prime, eta = params
        log_prior = self.log_prior(G_prime, eta)
        if log_prior == -np.inf:
            return -np.inf
        return self.log_likelihood(G_prime, eta, data) + log_prior
    
    def map_estimate(self, data: np.ndarray, initial_guess: Tuple[float, float] = None) -> dict:
        """Find Maximum A Posteriori estimate."""
        print("\n" + "=" * 60)
        print("Finding MAP Estimate")
        print("=" * 60)
        
        if initial_guess is None:
            initial_guess = (self.true_G_prime * 0.8, self.true_eta * 0.8)
        
        def neg_log_posterior(params):
            return -self.log_posterior(params, data)
        
        bounds = [(1000, 20000), (0.1, 50)]
        
        result = minimize(
            neg_log_posterior,
            x0=initial_guess,
            bounds=bounds,
            method='L-BFGS-B',
            options={'maxiter': 100}
        )
        
        G_map, eta_map = result.x
        
        print(f"Initial guess: G' = {initial_guess[0]:.0f}, η = {initial_guess[1]:.2f}")
        print(f"MAP Estimate:")
        print(f"  G' = {G_map:.1f} Pa (true: {self.true_G_prime} Pa)")
        print(f"  η = {eta_map:.3f} Pa·s (true: {self.true_eta} Pa·s)")
        
        G_error = abs(G_map - self.true_G_prime) / self.true_G_prime * 100
        eta_error = abs(eta_map - self.true_eta) / self.true_eta * 100
        
        print(f"Relative error: G' = {G_error:.1f}%, η = {eta_error:.1f}%")
        
        return {
            'G_prime': G_map,
            'eta': eta_map,
            'log_posterior': -result.fun,
            'errors': {'G_prime': G_error, 'eta': eta_error}
        }
    
    def grid_posterior(self, data: np.ndarray,
                       G_range: Tuple[float, float] = (3000, 7000),
                       eta_range: Tuple[float, float] = (2, 10),
                       n_points: int = 25) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Compute posterior on a grid for visualization."""
        print("\n" + "=" * 60)
        print(f"Grid Search: {n_points}×{n_points} points")
        print("=" * 60)
        
        G_values = np.linspace(G_range[0], G_range[1], n_points)
        eta_values = np.linspace(eta_range[0], eta_range[1], n_points)
        
        log_posterior_grid = np.zeros((n_points, n_points))
        
        for i, G in enumerate(G_values):
            for j, eta in enumerate(eta_values):
                log_posterior_grid[i, j] = self.log_posterior([G, eta], data)
            
            if (i + 1) % 5 == 0:
                print(f"  Progress: {i+1}/{n_points}")
        
        return G_values, eta_values, log_posterior_grid
    
    def plot_posterior(self, G_values: np.ndarray, eta_values: np.ndarray,
                       log_posterior: np.ndarray, map_estimate: dict = None):
        """Visualize posterior distribution."""
        fig, axes = plt.subplots(1, 3, figsize=(16, 5))
        
        # Convert to probability
        logP_max = np.max(log_posterior)
        posterior = np.exp(log_posterior - logP_max)
        posterior /= np.sum(posterior)
        
        G_grid, eta_grid = np.meshgrid(G_values, eta_values, indexing='ij')
        
        # 2D heatmap
        ax = axes[0]
        im = ax.pcolormesh(G_grid, eta_grid, posterior, shading='auto', cmap='viridis')
        ax.plot(self.true_G_prime, self.true_eta, 'r*', markersize=20, label='True', zorder=5)
        if map_estimate:
            ax.plot(map_estimate['G_prime'], map_estimate['eta'], 'w+',
                   markersize=15, mew=2, label='MAP', zorder=5)
        ax.set_xlabel("G' (Pa)")
        ax.set_ylabel('η (Pa·s)')
        ax.set_title('Posterior P(G\', η | data)')
        ax.legend()
        plt.colorbar(im, ax=ax, label='Probability')
        
        # Marginal for G'
        ax = axes[1]
        G_marginal = np.sum(posterior, axis=1)
        G_marginal /= np.sum(G_marginal) * (G_values[1] - G_values[0])
        ax.plot(G_values, G_marginal, 'b-', linewidth=2)
        ax.fill_between(G_values, G_marginal, alpha=0.3)
        ax.axvline(x=self.true_G_prime, color='r', linestyle='--', label=f'True: {self.true_G_prime}')
        if map_estimate:
            ax.axvline(x=map_estimate['G_prime'], color='b', linestyle=':', 
                      label=f"MAP: {map_estimate['G_prime']:.0f}")
        ax.set_xlabel("G' (Pa)")
        ax.set_ylabel('Marginal probability')
        ax.set_title("P(G' | data)")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Marginal for η
        ax = axes[2]
        eta_marginal = np.sum(posterior, axis=0)
        eta_marginal /= np.sum(eta_marginal) * (eta_values[1] - eta_values[0])
        ax.plot(eta_values, eta_marginal, 'r-', linewidth=2)
        ax.fill_between(eta_values, eta_marginal, alpha=0.3, color='red')
        ax.axvline(x=self.true_eta, color='r', linestyle='--', label=f'True: {self.true_eta}')
        if map_estimate:
            ax.axvline(x=map_estimate['eta'], color='darkred', linestyle=':',
                      label=f"MAP: {map_estimate['eta']:.2f}")
        ax.set_xlabel('η (Pa·s)')
        ax.set_ylabel('Marginal probability')
        ax.set_title('P(η | data)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('posterior_distribution.png', dpi=150)
        plt.show()
    
    def mcmc_sample(self, data: np.ndarray, n_samples: int = 5000,
                    proposal_std: Tuple[float, float] = (50, 0.1),
                    burn_in: int = 1000,
                    initial_state: Tuple[float, float] = None) -> dict:
        """
        Metropolis-Hastings MCMC sampling for full posterior exploration.
        
        Parameters:
        -----------
        data : measurement data
        n_samples : total number of MCMC iterations
        proposal_std : standard deviation of Gaussian proposals (dG', deta)
        burn_in : number of initial samples to discard
        initial_state : starting point (G', η), defaults to MAP estimate
        
        Returns:
        --------
        Dictionary with samples, acceptance rate, and statistics
        """
        print("\n" + "=" * 60)
        print(f"MCMC Sampling: {n_samples} iterations")
        print("=" * 60)
        
        # Initialize from MAP or provided state
        if initial_state is None:
            map_result = self.map_estimate(data)
            current = np.array([map_result['G_prime'], map_result['eta']])
        else:
            current = np.array(initial_state)
        
        print(f"Initial state: G'={current[0]:.1f}, η={current[1]:.3f}")
        print(f"Proposal σ: dG'={proposal_std[0]:.1f}, dη={proposal_std[1]:.3f}")
        
        # Storage
        samples = []
        log_posteriors = []
        n_accepted = 0
        
        current_logP = self.log_posterior(current, data)
        
        for i in range(n_samples):
            # Propose new state
            proposal = current + np.random.normal(0, proposal_std, 2)
            
            # Compute log posterior for proposal
            proposal_logP = self.log_posterior(proposal, data)
            
            # Accept/reject
            if proposal_logP == -np.inf:
                # Reject (out of bounds)
                accept = False
            else:
                # Metropolis criterion
                log_alpha = proposal_logP - current_logP
                accept = np.log(np.random.uniform()) < log_alpha
            
            if accept:
                current = proposal
                current_logP = proposal_logP
                n_accepted += 1
            
            # Store sample
            samples.append(current.copy())
            log_posteriors.append(current_logP)
            
            # Progress report
            if (i + 1) % 1000 == 0:
                acceptance_rate = n_accepted / (i + 1)
                print(f"  Iteration {i+1}/{n_samples}: acceptance={acceptance_rate:.2%}")
        
        # Process results
        samples = np.array(samples)
        acceptance_rate = n_accepted / n_samples
        
        # Discard burn-in
        samples_post = samples[burn_in:]
        
        print(f"\nMCMC complete:")
        print(f"  Acceptance rate: {acceptance_rate:.2%}")
        print(f"  Burn-in: {burn_in} samples")
        print(f"  Usable samples: {len(samples_post)}")
        
        # Compute statistics
        G_mean = np.mean(samples_post[:, 0])
        G_std = np.std(samples_post[:, 0])
        G_ci = np.percentile(samples_post[:, 0], [2.5, 97.5])
        
        eta_mean = np.mean(samples_post[:, 1])
        eta_std = np.std(samples_post[:, 1])
        eta_ci = np.percentile(samples_post[:, 1], [2.5, 97.5])
        
        print(f"\nPosterior statistics:")
        print(f"  G':  mean={G_mean:.1f}±{G_std:.1f}, 95% CI=[{G_ci[0]:.1f}, {G_ci[1]:.1f}]")
        print(f"  η:   mean={eta_mean:.3f}±{eta_std:.3f}, 95% CI=[{eta_ci[0]:.3f}, {eta_ci[1]:.3f}]")
        
        return {
            'samples': samples,
            'samples_posterior': samples_post,
            'log_posteriors': log_posteriors,
            'acceptance_rate': acceptance_rate,
            'statistics': {
                'G_prime': {'mean': G_mean, 'std': G_std, 'ci_95': G_ci},
                'eta': {'mean': eta_mean, 'std': eta_std, 'ci_95': eta_ci}
            }
        }
    
    def plot_mcmc_results(self, mcmc_results: dict, data: np.ndarray):
        """Visualize MCMC sampling results."""
        samples = mcmc_results['samples_posterior']
        
        fig, axes = plt.subplots(2, 3, figsize=(16, 10))
        
        # Trace plots
        ax = axes[0, 0]
        ax.plot(samples[:, 0], 'b-', alpha=0.5, linewidth=0.5)
        ax.axhline(y=self.true_G_prime, color='r', linestyle='--', label='True')
        ax.set_ylabel("G' (Pa)")
        ax.set_xlabel('Iteration')
        ax.set_title('MCMC Trace: G\'')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        ax = axes[0, 1]
        ax.plot(samples[:, 1], 'r-', alpha=0.5, linewidth=0.5)
        ax.axhline(y=self.true_eta, color='r', linestyle='--', label='True')
        ax.set_ylabel('η (Pa·s)')
        ax.set_xlabel('Iteration')
        ax.set_title('MCMC Trace: η')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Joint posterior scatter
        ax = axes[0, 2]
        ax.scatter(samples[:, 0], samples[:, 1], c=np.arange(len(samples)), 
                  cmap='viridis', alpha=0.3, s=5)
        ax.plot(self.true_G_prime, self.true_eta, 'r*', markersize=20, label='True')
        
        # Plot mean
        G_mean = mcmc_results['statistics']['G_prime']['mean']
        eta_mean = mcmc_results['statistics']['eta']['mean']
        ax.plot(G_mean, eta_mean, 'w+', markersize=15, mew=2, label='Posterior mean')
        
        ax.set_xlabel("G' (Pa)")
        ax.set_ylabel('η (Pa·s)')
        ax.set_title('Joint Posterior (color = iteration)')
        ax.legend()
        
        # Histograms with priors overlaid
        ax = axes[1, 0]
        ax.hist(samples[:, 0], bins=50, density=True, alpha=0.7, color='blue', label='Posterior')
        ax.axvline(x=self.true_G_prime, color='r', linestyle='--', linewidth=2, label='True')
        ax.axvline(x=G_mean, color='b', linestyle='-', linewidth=2, label=f'Mean: {G_mean:.0f}')
        ax.set_xlabel("G' (Pa)")
        ax.set_ylabel('Density')
        ax.set_title("P(G' | data)")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        ax = axes[1, 1]
        ax.hist(samples[:, 1], bins=50, density=True, alpha=0.7, color='red', label='Posterior')
        ax.axvline(x=self.true_eta, color='r', linestyle='--', linewidth=2, label='True')
        ax.axvline(x=eta_mean, color='darkred', linestyle='-', linewidth=2, label=f'Mean: {eta_mean:.2f}')
        ax.set_xlabel('η (Pa·s)')
        ax.set_ylabel('Density')
        ax.set_title('P(η | data)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Model fit check
        ax = axes[1, 2]
        
        # Sample 50 parameter sets and plot predictions
        sample_indices = np.random.choice(len(samples), min(50, len(samples)), replace=False)
        
        for idx in sample_indices:
            G_s, eta_s = samples[idx]
            pred = self.forward_model(G_s, eta_s)
            ax.plot(self.time * 1000, pred[1] * 1e6, 'b-', alpha=0.05)  # Middle receiver
        
        # Plot data and true model
        ax.plot(self.time * 1000, data[1] * 1e6, 'r-', linewidth=1, alpha=0.7, label='Data')
        true_pred = self.forward_model(self.true_G_prime, self.true_eta)
        ax.plot(self.time * 1000, true_pred[1] * 1e6, 'g--', linewidth=2, label='True model')
        
        ax.set_xlabel('Time (ms)')
        ax.set_ylabel('Displacement (μm)')
        ax.set_title('Posterior predictive (middle receiver)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('mcmc_results.png', dpi=150)
        plt.show()
        
        print("\n✓ MCMC visualization saved: mcmc_results.png")


def run_inversion_demo():
    """Full Bayesian inversion demonstration."""
    print("\n" + "=" * 60)
    print("Bayesian Inverse Problem: (G', η) from Wave Data")
    print("=" * 60)
    
    # Setup problem
    problem = InverseProblem(
        true_G_prime=5000,
        true_eta=5,
        noise_std=0.01e-6
    )
    
    # Generate synthetic data
    time, data, metadata = problem.generate_synthetic_data(plot=True)
    
    # Find MAP estimate
    map_result = problem.map_estimate(data)
    
    # MCMC sampling for uncertainty quantification
    mcmc_results = problem.mcmc_sample(
        data,
        n_samples=3000,
        proposal_std=(30, 0.08),
        burn_in=500,
        initial_state=(map_result['G_prime'], map_result['eta'])
    )
    
    # Visualize MCMC
    problem.plot_mcmc_results(mcmc_results, data)
    
    # Grid search for posterior surface (optional, for comparison)
    G_vals, eta_vals, logP_grid = problem.grid_posterior(
        data,
        G_range=(4500, 5500),
        eta_range=(4, 6),
        n_points=15
    )
    problem.plot_posterior(G_vals, eta_vals, logP_grid, map_result)
    
    # Summary
    print("\n" + "=" * 60)
    print("INVERSION SUMMARY")
    print("=" * 60)
    print(f"{'Parameter':<15} {'True':<15} {'MAP':<15} {'MCMC Mean':<15}")
    print("-" * 60)
    G_mcmc = mcmc_results['statistics']['G_prime']['mean']
    eta_mcmc = mcmc_results['statistics']['eta']['mean']
    print(f"{'G\' (Pa)':<15} {problem.true_G_prime:<15.0f} "
          f"{map_result['G_prime']:<15.0f} {G_mcmc:<15.0f}")
    print(f"{'η (Pa·s)':<15} {problem.true_eta:<15.1f} "
          f"{map_result['eta']:<15.2f} {eta_mcmc:<15.2f}")
    
    print("\n95% Credible Intervals:")
    G_ci = mcmc_results['statistics']['G_prime']['ci_95']
    eta_ci = mcmc_results['statistics']['eta']['ci_95']
    print(f"  G':  [{G_ci[0]:.0f}, {G_ci[1]:.0f}] Pa")
    print(f"  η:   [{eta_ci[0]:.2f}, {eta_ci[1]:.2f}] Pa·s")
    
    print("\n" + "=" * 60)
    print("Files saved:")
    print("  - synthetic_data.png")
    print("  - mcmc_results.png")
    print("  - posterior_distribution.png")
    print("=" * 60)


if __name__ == "__main__":
    run_inversion_demo()
