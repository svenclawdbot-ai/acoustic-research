#!/usr/bin/env python3
"""
Zener (Standard Linear Solid) Viscoelastic Model
================================================

The Zener model bridges Kelvin-Voigt and Maxwell behavior:
- Spring (G∞) in parallel with
- Spring (ΔG = G0 - G∞) and dashpot (η) in series

Complex modulus: G*(ω) = G∞ + ΔG/(1 + iωτ)
where τ = η/ΔG is the relaxation time

This captures:
- High-frequency elastic limit: G∞
- Low-frequency elastic limit: G0 = G∞ + ΔG
- Peak loss at ω = 1/τ

Author: Research Project — Publication-ready extension
Date: March 16, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Tuple
from scipy.optimize import minimize
import warnings


@dataclass
class ZenerModel:
    """
    Zener (Standard Linear Solid) viscoelastic model.
    
    Parameters:
    -----------
    G_inf : High-frequency modulus (Pa)
    G_0 : Low-frequency modulus (Pa)  
    tau : Relaxation time (s)
    
    Derived: delta_G = G_0 - G_inf, eta = tau * delta_G
    """
    
    def compute_waveform(self, t: np.ndarray, r: float,
                        G_inf: float, G_0: float, tau: float,
                        f0: float = 100.0, amplitude: float = 1e-6,
                        rho: float = 1000.0) -> np.ndarray:
        """
        Compute waveform for Zener viscoelastic material.
        
        Uses quasi-static approximation for wave propagation.
        """
        omega = 2 * np.pi * f0
        delta_G = G_0 - G_inf
        
        # Frequency-dependent modulus at source frequency
        denom = 1 + (omega * tau)**2
        G_prime = G_inf + delta_G / denom
        G_double_prime = delta_G * omega * tau / denom
        
        # Phase velocity
        c_s_inf = np.sqrt(G_inf / rho)
        c_phase = np.sqrt(2 * G_prime / (rho * (1 + np.sqrt(1 + (G_double_prime/G_prime)**2))))
        
        # Attenuation
        attenuation = omega * G_double_prime / (2 * G_prime * c_phase)
        
        # Ricker wavelet
        sigma = 1 / (np.pi * f0)
        tau_wave = t - r / c_phase - 3 * sigma
        ricker = (1 - 2 * (tau_wave / sigma)**2) * np.exp(-(tau_wave / sigma)**2)
        
        u = amplitude * np.exp(-attenuation * r) * ricker
        
        arrival_time = r / c_phase - 3 * sigma
        u[t < arrival_time] = 0
        
        return u
    
    def dispersion_curve(self, frequencies: np.ndarray, G_inf: float, G_0: float, tau: float,
                         rho: float = 1000.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute dispersion curve for Zener model.
        
        Returns:
            phase_velocity, attenuation_coefficient
        """
        omega = 2 * np.pi * frequencies
        delta_G = G_0 - G_inf
        
        # Storage and loss modulus
        denom = 1 + (omega * tau)**2
        G_prime = G_inf + delta_G / denom
        G_double_prime = delta_G * omega * tau / denom
        
        # Phase velocity
        c_phase = np.sqrt(2 * G_prime / (rho * (1 + np.sqrt(1 + (G_double_prime/G_prime)**2))))
        
        # Attenuation
        attenuation = omega * G_double_prime / (2 * G_prime * c_phase)
        
        return c_phase, attenuation
    
    def loss_tangent(self, frequencies: np.ndarray, G_inf: float, G_0: float, tau: float) -> np.ndarray:
        """
        Compute loss tangent: tan(δ) = G''/G'
        """
        omega = 2 * np.pi * frequencies
        delta_G = G_0 - G_inf
        
        denom = 1 + (omega * tau)**2
        G_prime = G_inf + delta_G / denom
        G_double_prime = delta_G * omega * tau / denom
        
        return G_double_prime / G_prime


@dataclass
class KelvinVoigtModel:
    """Kelvin-Voigt model for comparison."""
    
    def compute_waveform(self, t: np.ndarray, r: float,
                        G_prime: float, eta: float, f0: float = 100.0,
                        amplitude: float = 1e-6, rho: float = 1000.0) -> np.ndarray:
        """Compute waveform for Kelvin-Voigt material."""
        c_s = np.sqrt(G_prime / rho)
        omega = 2 * np.pi * f0
        tau = eta / G_prime
        
        # Dispersed wave speed
        omega_tau = omega * tau
        c_phase = c_s * np.sqrt(2) * ((1 + omega_tau**2)**0.25) * np.cos(0.5 * np.arctan(omega_tau))
        
        # Attenuation
        alpha_att = (omega**2 * eta) / (2 * G_prime * c_s)
        
        # Ricker wavelet
        sigma = 1 / (np.pi * f0)
        tau_wave = t - r / c_phase - 3 * sigma
        ricker = (1 - 2 * (tau_wave / sigma)**2) * np.exp(-(tau_wave / sigma)**2)
        
        u = amplitude * np.exp(-alpha_att * r) * ricker
        
        arrival_time = r / c_phase - 3 * sigma
        u[t < arrival_time] = 0
        
        return u
    
    def dispersion_curve(self, frequencies: np.ndarray, G_prime: float, eta: float,
                         rho: float = 1000.0) -> Tuple[np.ndarray, np.ndarray]:
        """Compute dispersion curve."""
        omega = 2 * np.pi * frequencies
        c_s = np.sqrt(G_prime / rho)
        tau = eta / G_prime
        
        omega_tau = omega * tau
        c_phase = c_s * np.sqrt(2) * ((1 + omega_tau**2)**0.25) * np.cos(0.5 * np.arctan(omega_tau))
        attenuation = (omega**2 * eta) / (2 * G_prime * c_phase)
        
        return c_phase, attenuation


@dataclass
class PowerLawModel:
    """Power-Law model for comparison."""
    
    def compute_waveform(self, t: np.ndarray, r: float,
                        G0: float, alpha: float, f0: float = 100.0,
                        amplitude: float = 1e-6, rho: float = 1000.0) -> np.ndarray:
        """Compute waveform for Power-Law material."""
        omega = 2 * np.pi * f0
        omega_ref = omega
        
        G_prime = G0 * (omega / omega_ref)**alpha * np.cos(alpha * np.pi / 2)
        G_double_prime = G0 * (omega / omega_ref)**alpha * np.sin(alpha * np.pi / 2)
        
        c_s = np.sqrt(G_prime / rho)
        tan_factor = np.tan(alpha * np.pi / 2) if alpha < 0.99 else 10.0
        alpha_att = omega * tan_factor / (2 * c_s)
        
        sigma = 1 / (np.pi * f0)
        tau_wave = t - r / c_s - 3 * sigma
        ricker = (1 - 2 * (tau_wave / sigma)**2) * np.exp(-(tau_wave / sigma)**2)
        
        u = amplitude * np.exp(-alpha_att * r) * ricker
        
        arrival_time = r / c_s - 3 * sigma
        u[t < arrival_time] = 0
        
        return u
    
    def dispersion_curve(self, frequencies: np.ndarray, G0: float, alpha: float,
                         rho: float = 1000.0, f_ref: float = 100.0) -> Tuple[np.ndarray, np.ndarray]:
        """Compute dispersion curve."""
        omega = 2 * np.pi * frequencies
        omega_ref = 2 * np.pi * f_ref
        
        G_prime = G0 * (omega / omega_ref)**alpha * np.cos(alpha * np.pi / 2)
        G_double_prime = G0 * (omega / omega_ref)**alpha * np.sin(alpha * np.pi / 2)
        
        c_phase = np.sqrt(2 * G_prime / (rho * (1 + np.sqrt(1 + (G_double_prime/G_prime)**2))))
        attenuation = omega * G_double_prime / (2 * G_prime * c_phase)
        
        return c_phase, attenuation


class ThreeModelComparison:
    """Compare Kelvin-Voigt, Zener, and Power-Law models."""
    
    def __init__(self, duration: float = 0.04, dt: float = 2e-5):
        self.duration = duration
        self.dt = dt
        self.time = np.arange(0, duration, dt)
        self.receiver_distances = [0.02, 0.04, 0.06]
        self.kv_model = KelvinVoigtModel()
        self.zener_model = ZenerModel()
        self.pl_model = PowerLawModel()
    
    def generate_data(self, model_type: str, params: dict, noise_std: float = 0.01e-6) -> np.ndarray:
        """Generate synthetic data from specified model."""
        data = []
        for r in self.receiver_distances:
            if model_type == 'kv':
                waveform = self.kv_model.compute_waveform(self.time, r, params['G_prime'], params['eta'])
            elif model_type == 'zener':
                waveform = self.zener_model.compute_waveform(self.time, r, params['G_inf'], params['G_0'], params['tau'])
            elif model_type == 'pl':
                waveform = self.pl_model.compute_waveform(self.time, r, params['G0'], params['alpha'])
            else:
                raise ValueError(f"Unknown model: {model_type}")
            data.append(waveform)
        
        data = np.array(data)
        noise = np.random.normal(0, noise_std, data.shape)
        return data + noise
    
    def fit_model(self, model_type: str, data: np.ndarray, noise_std: float = 0.01e-6) -> dict:
        """Fit specified model to data."""
        
        def residuals(params):
            if model_type == 'kv':
                G_prime, eta = params
                if not (1000 <= G_prime <= 20000 and 0.1 <= eta <= 100):
                    return 1e10
                pred = np.array([self.kv_model.compute_waveform(self.time, r, G_prime, eta) 
                                for r in self.receiver_distances])
            
            elif model_type == 'zener':
                G_inf, G_0, tau = params
                if not (100 <= G_inf <= 15000 and G_inf < G_0 <= 20000 and 1e-4 <= tau <= 0.1):
                    return 1e10
                pred = np.array([self.zener_model.compute_waveform(self.time, r, G_inf, G_0, tau)
                                for r in self.receiver_distances])
            
            elif model_type == 'pl':
                G0, alpha = params
                if not (1000 <= G0 <= 20000 and 0.01 <= alpha <= 0.99):
                    return 1e10
                pred = np.array([self.pl_model.compute_waveform(self.time, r, G0, alpha)
                                for r in self.receiver_distances])
            
            else:
                return 1e10
            
            return np.sum((data - pred)**2) / noise_std**2
        
        # Initial guesses and bounds
        if model_type == 'kv':
            x0 = [4500, 5]
            bounds = [(1000, 20000), (0.1, 100)]
            result = minimize(residuals, x0=x0, bounds=bounds, method='L-BFGS-B')
            return {'G_prime': result.x[0], 'eta': result.x[1], 'rss': result.fun * noise_std**2, 
                   'n_params': 2, 'success': result.success}
        
        elif model_type == 'zener':
            x0 = [2000, 6000, 0.005]
            bounds = [(100, 15000), (1000, 20000), (1e-4, 0.1)]
            result = minimize(residuals, x0=x0, bounds=bounds, method='L-BFGS-B')
            return {'G_inf': result.x[0], 'G_0': result.x[1], 'tau': result.x[2],
                   'rss': result.fun * noise_std**2, 'n_params': 3, 'success': result.success}
        
        elif model_type == 'pl':
            x0 = [4500, 0.3]
            bounds = [(1000, 20000), (0.01, 0.99)]
            result = minimize(residuals, x0=x0, bounds=bounds, method='L-BFGS-B')
            return {'G0': result.x[0], 'alpha': result.x[1], 'rss': result.fun * noise_std**2,
                   'n_params': 2, 'success': result.success}
    
    def compute_ic(self, rss: float, n_data: int, n_params: int) -> dict:
        """Compute information criteria."""
        aic = n_data * np.log(rss / n_data) + 2 * n_params
        bic = n_data * np.log(rss / n_data) + n_params * np.log(n_data)
        aicc = aic + 2 * n_params * (n_params + 1) / (n_data - n_params - 1) if n_data > n_params + 1 else np.inf
        return {'aic': aic, 'bic': bic, 'aicc': aicc}
    
    def run_zener_focused_comparison(self):
        """Comparison focused on Zener model capabilities."""
        print("=" * 70)
        print("ZENER MODEL ANALYSIS: Bridging KV and Power-Law Behavior")
        print("=" * 70)
        
        # Generate data from Zener model
        zener_params = {'G_inf': 3000, 'G_0': 7000, 'tau': 0.003}  # 3 ms relaxation
        print(f"\nTrue Zener parameters:")
        print(f"  G∞ = {zener_params['G_inf']} Pa (high-freq limit)")
        print(f"  G₀ = {zener_params['G_0']} Pa (low-freq limit)")
        print(f"  τ = {zener_params['tau']*1000:.1f} ms (relaxation time)")
        print(f"  ΔG = {zener_params['G_0'] - zener_params['G_inf']} Pa")
        
        data = self.generate_data('zener', zener_params, noise_std=0.01e-6)
        n_data = data.size
        
        # Fit all three models
        print("\n" + "-" * 70)
        print("Fitting models...")
        
        kv_fit = self.fit_model('kv', data)
        print(f"\nKelvin-Voigt:")
        print(f"  G' = {kv_fit['G_prime']:.1f} Pa, η = {kv_fit['eta']:.3f} Pa·s")
        
        zener_fit = self.fit_model('zener', data)
        print(f"\nZener:")
        print(f"  G∞ = {zener_fit['G_inf']:.1f} Pa, G₀ = {zener_fit['G_0']:.1f} Pa, τ = {zener_fit['tau']*1000:.2f} ms")
        
        pl_fit = self.fit_model('pl', data)
        print(f"\nPower-Law:")
        print(f"  G₀ = {pl_fit['G0']:.1f} Pa, α = {pl_fit['alpha']:.3f}")
        
        # Information criteria
        kv_ic = self.compute_ic(kv_fit['rss'], n_data, kv_fit['n_params'])
        zener_ic = self.compute_ic(zener_fit['rss'], n_data, zener_fit['n_params'])
        pl_ic = self.compute_ic(pl_fit['rss'], n_data, pl_fit['n_params'])
        
        print("\n" + "=" * 70)
        print("MODEL COMPARISON")
        print("=" * 70)
        print(f"{'Criterion':<12} {'KV (2p)':<18} {'Zener (3p)':<18} {'PL (2p)':<18} {'Winner':<10}")
        print("-" * 70)
        
        models = [('KV', kv_ic), ('Zener', zener_ic), ('PL', pl_ic)]
        for criterion in ['aic', 'bic', 'aicc']:
            values = [ic[criterion] for _, ic in models]
            winner_idx = np.argmin(values)
            winner = models[winner_idx][0]
            print(f"{criterion.upper():<12} {kv_ic[criterion]:<18.2f} {zener_ic[criterion]:<18.2f} "
                  f"{pl_ic[criterion]:<18.2f} {winner:<10}")
        
        # Visualization
        self._plot_zener_analysis(data, zener_params, kv_fit, zener_fit, pl_fit)
        
        return {'kv': kv_fit, 'zener': zener_fit, 'pl': pl_fit}
    
    def _plot_zener_analysis(self, data, true_params, kv_fit, zener_fit, pl_fit):
        """Visualize Zener model analysis."""
        fig, axes = plt.subplots(2, 3, figsize=(16, 10))
        
        # Generate predictions
        kv_pred = np.array([self.kv_model.compute_waveform(self.time, r, kv_fit['G_prime'], kv_fit['eta'])
                           for r in self.receiver_distances])
        zener_pred = np.array([self.zener_model.compute_waveform(self.time, r, zener_fit['G_inf'], 
                                                                  zener_fit['G_0'], zener_fit['tau'])
                              for r in self.receiver_distances])
        pl_pred = np.array([self.pl_model.compute_waveform(self.time, r, pl_fit['G0'], pl_fit['alpha'])
                           for r in self.receiver_distances])
        true_pred = np.array([self.zener_model.compute_waveform(self.time, r, true_params['G_inf'],
                                                                 true_params['G_0'], true_params['tau'])
                             for r in self.receiver_distances])
        
        # Row 1: Waveforms
        for i, ax in enumerate(axes[0]):
            dist = self.receiver_distances[i] * 100
            ax.plot(self.time * 1000, data[i] * 1e6, 'k-', alpha=0.5, linewidth=0.8, label='Data')
            ax.plot(self.time * 1000, kv_pred[i] * 1e6, 'b--', linewidth=1.5, label='KV')
            ax.plot(self.time * 1000, zener_pred[i] * 1e6, 'g-', linewidth=1.5, label='Zener')
            ax.plot(self.time * 1000, pl_pred[i] * 1e6, 'r:', linewidth=1.5, label='PL')
            ax.set_xlabel('Time (ms)')
            ax.set_ylabel('Displacement (μm)')
            ax.set_title(f'{dist:.0f} cm receiver')
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)
        
        # Row 2: Model characteristics
        
        # Dispersion curves
        ax = axes[1, 0]
        freqs = np.linspace(20, 500, 100)
        
        c_kv, _ = self.kv_model.dispersion_curve(freqs, kv_fit['G_prime'], kv_fit['eta'])
        c_zener, _ = self.zener_model.dispersion_curve(freqs, zener_fit['G_inf'], zener_fit['G_0'], zener_fit['tau'])
        c_pl, _ = self.pl_model.dispersion_curve(freqs, pl_fit['G0'], pl_fit['alpha'])
        c_true, _ = self.zener_model.dispersion_curve(freqs, true_params['G_inf'], true_params['G_0'], true_params['tau'])
        
        ax.plot(freqs, c_kv, 'b--', linewidth=2, label='KV')
        ax.plot(freqs, c_zener, 'g-', linewidth=2, label='Zener')
        ax.plot(freqs, c_pl, 'r:', linewidth=2, label='PL')
        ax.plot(freqs, c_true, 'k-', alpha=0.5, linewidth=2, label='True')
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Phase velocity (m/s)')
        ax.set_title('Dispersion curves')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Loss tangent
        ax = axes[1, 1]
        tan_kv = freqs * kv_fit['eta'] / kv_fit['G_prime']  # Approximate for KV
        tan_zener = self.zener_model.loss_tangent(freqs, zener_fit['G_inf'], zener_fit['G_0'], zener_fit['tau'])
        tan_pl = np.tan(pl_fit['alpha'] * np.pi / 2) * np.ones_like(freqs)  # Constant for PL
        tan_true = self.zener_model.loss_tangent(freqs, true_params['G_inf'], true_params['G_0'], true_params['tau'])
        
        ax.semilogy(freqs, tan_kv, 'b--', linewidth=2, label='KV')
        ax.semilogy(freqs, tan_zener, 'g-', linewidth=2, label='Zener')
        ax.semilogy(freqs, tan_pl, 'r:', linewidth=2, label='PL')
        ax.semilogy(freqs, tan_true, 'k-', alpha=0.5, linewidth=2, label='True')
        ax.axvline(x=1/(2*np.pi*true_params['tau']), color='k', linestyle='--', alpha=0.3, label='f = 1/(2πτ)')
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Loss tangent tan(δ)')
        ax.set_title('Loss tangent spectra')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Complex modulus plane
        ax = axes[1, 2]
        omega = 2 * np.pi * freqs
        
        # Zener
        delta_G_z = zener_fit['G_0'] - zener_fit['G_inf']
        denom_z = 1 + (omega * zener_fit['tau'])**2
        G_prime_z = zener_fit['G_inf'] + delta_G_z / denom_z
        G_dp_z = delta_G_z * omega * zener_fit['tau'] / denom_z
        
        # True
        delta_G_t = true_params['G_0'] - true_params['G_inf']
        denom_t = 1 + (omega * true_params['tau'])**2
        G_prime_t = true_params['G_inf'] + delta_G_t / denom_t
        G_dp_t = delta_G_t * omega * true_params['tau'] / denom_t
        
        ax.plot(G_prime_z/1000, G_dp_z/1000, 'g-', linewidth=2, label='Zener fit')
        ax.plot(G_prime_t/1000, G_dp_t/1000, 'k--', linewidth=2, label='True')
        ax.set_xlabel("G' (kPa)")
        ax.set_ylabel("G'' (kPa)")
        ax.set_title('Cole-Cole plot')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.axis('equal')
        
        plt.tight_layout()
        plt.savefig('zener_analysis.png', dpi=150, bbox_inches='tight')
        plt.show()
        print("\n✓ Saved: zener_analysis.png")


def main():
    """Run Zener-focused analysis."""
    comparison = ThreeModelComparison()
    results = comparison.run_zener_focused_comparison()
    
    print("\n" + "=" * 70)
    print("KEY FINDINGS")
    print("=" * 70)
    print("""
The Zener model captures both elastic limits:
  • G∞ = high-frequency modulus (instantaneous response)
  • G₀ = low-frequency modulus (equilibrium response)
  • Peak loss at ω = 1/τ

Advantages over KV:
  ✓ Bounded storage modulus (physically realistic)
  ✓ Frequency-independent limits
  ✓ Single relaxation time interpretable

Advantages over Power-Law:
  ✓ Finite parameter count
  ✓ Clear physical interpretation
  ✓ Easier to fit (3 vs 2 parameters but well-constrained)

Recommendation for publication:
  - Compare all three models on experimental data
  - Use BIC for model selection
  - Report Zener parameters when selected (most interpretable)
    """)


if __name__ == "__main__":
    main()
