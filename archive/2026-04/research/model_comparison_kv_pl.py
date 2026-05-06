#!/usr/bin/env python3
"""
Model Comparison: Kelvin-Voigt vs Power-Law Viscoelasticity
===========================================================

Compare two constitutive models for soft tissue characterization:
1. Kelvin-Voigt: G*(ω) = G' + iωη (single relaxation time)
2. Power-Law: G*(ω) = G₀(iω/ω₀)^α (broadband relaxation)

Author: Research Project — Week 2 Extension
Date: March 16, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Tuple, Literal
from scipy.optimize import minimize
import warnings


@dataclass  
class PowerLawModel:
    """
    Power-law viscoelastic model.
    
    Complex modulus: G*(ω) = G₀ · (iω/ω₀)^α
    
    where:
    - G₀ = modulus at reference frequency ω₀
    - α = power-law exponent (0 < α < 1)
    - ω₀ = reference angular frequency
    
    Storage modulus: G'(ω) = G₀ · (ω/ω₀)^α · cos(απ/2)
    Loss modulus:   G''(ω) = G₀ · (ω/ω₀)^α · sin(απ/2)
    """
    
    def compute_waveform(self, t: np.ndarray, r: float, 
                        G0: float, alpha: float, f0: float = 100.0,
                        amplitude: float = 1e-6, rho: float = 1000.0) -> np.ndarray:
        """
        Compute waveform for power-law viscoelastic material.
        
        Parameters:
        -----------
        t : time array
        r : distance from source
        G0 : modulus at reference frequency (Pa)
        alpha : power-law exponent (0-1)
        f0 : source frequency (Hz)
        amplitude : source amplitude
        rho : density
        """
        omega = 2 * np.pi * f0
        omega_ref = omega  # Use source frequency as reference
        
        # Frequency-dependent modulus at source frequency
        G_prime = G0 * (omega / omega_ref)**alpha * np.cos(alpha * np.pi / 2)
        G_double_prime = G0 * (omega / omega_ref)**alpha * np.sin(alpha * np.pi / 2)
        
        # Effective wave speed and attenuation
        c_s = np.sqrt(G_prime / rho)
        
        # Attenuation coefficient for power-law
        # α_att = ω · tan(απ/2) / (2c_s) for small losses
        tan_factor = np.tan(alpha * np.pi / 2) if alpha < 0.99 else 10.0
        alpha_att = omega * tan_factor / (2 * c_s)
        
        # Ricker wavelet
        sigma = 1 / (np.pi * f0)
        tau_wave = t - r / c_s - 3 * sigma
        ricker = (1 - 2 * (tau_wave / sigma)**2) * np.exp(-(tau_wave / sigma)**2)
        
        # Apply attenuation
        u = amplitude * np.exp(-alpha_att * r) * ricker
        
        # Causality
        arrival_time = r / c_s - 3 * sigma
        u[t < arrival_time] = 0
        
        return u
    
    def dispersion_curve(self, frequencies: np.ndarray, G0: float, alpha: float,
                         rho: float = 1000.0, f_ref: float = 100.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute dispersion curve for power-law model.
        
        Returns:
            phase_velocity, attenuation_coefficient
        """
        omega = 2 * np.pi * frequencies
        omega_ref = 2 * np.pi * f_ref
        
        G_prime = G0 * (omega / omega_ref)**alpha * np.cos(alpha * np.pi / 2)
        G_double_prime = G0 * (omega / omega_ref)**alpha * np.sin(alpha * np.pi / 2)
        
        # Phase velocity
        c_phase = np.sqrt(2 * G_prime / (rho * (1 + np.sqrt(1 + (G_double_prime/G_prime)**2))))
        
        # Attenuation coefficient (Np/m)
        attenuation = omega * G_double_prime / (2 * G_prime * c_phase)
        
        return c_phase, attenuation


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
        c_dispersed = c_s * np.sqrt(2) * ((1 + omega_tau**2)**0.25) * np.cos(0.5 * np.arctan(omega_tau))
        
        # Attenuation
        alpha_att = (omega**2 * eta) / (2 * G_prime * c_s)
        
        # Ricker wavelet
        sigma = 1 / (np.pi * f0)
        tau_wave = t - r / c_dispersed - 3 * sigma
        ricker = (1 - 2 * (tau_wave / sigma)**2) * np.exp(-(tau_wave / sigma)**2)
        
        u = amplitude * np.exp(-alpha_att * r) * ricker
        
        arrival_time = r / c_dispersed - 3 * sigma
        u[t < arrival_time] = 0
        
        return u
    
    def dispersion_curve(self, frequencies: np.ndarray, G_prime: float, eta: float,
                         rho: float = 1000.0) -> Tuple[np.ndarray, np.ndarray]:
        """Compute dispersion curve for Kelvin-Voigt model."""
        omega = 2 * np.pi * frequencies
        c_s = np.sqrt(G_prime / rho)
        tau = eta / G_prime
        
        # Phase velocity
        omega_tau = omega * tau
        c_phase = c_s * np.sqrt(2) * ((1 + omega_tau**2)**0.25) * np.cos(0.5 * np.arctan(omega_tau))
        
        # Attenuation
        attenuation = (omega**2 * eta) / (2 * G_prime * c_phase)
        
        return c_phase, attenuation


class ModelComparison:
    """Compare Kelvin-Voigt and Power-Law models."""
    
    def __init__(self, duration: float = 0.04, dt: float = 2e-5):
        self.duration = duration
        self.dt = dt
        self.time = np.arange(0, duration, dt)
        self.receiver_distances = [0.02, 0.04, 0.06]  # 2, 4, 6 cm
        self.kv_model = KelvinVoigtModel()
        self.pl_model = PowerLawModel()
    
    def generate_kv_data(self, G_prime: float = 5000, eta: float = 5,
                         noise_std: float = 0.01e-6) -> np.ndarray:
        """Generate synthetic data from Kelvin-Voigt model."""
        data = []
        for r in self.receiver_distances:
            waveform = self.kv_model.compute_waveform(self.time, r, G_prime, eta)
            data.append(waveform)
        data = np.array(data)
        noise = np.random.normal(0, noise_std, data.shape)
        return data + noise
    
    def generate_pl_data(self, G0: float = 5000, alpha: float = 0.3,
                         noise_std: float = 0.01e-6) -> np.ndarray:
        """Generate synthetic data from Power-Law model."""
        data = []
        for r in self.receiver_distances:
            waveform = self.pl_model.compute_waveform(self.time, r, G0, alpha)
            data.append(waveform)
        data = np.array(data)
        noise = np.random.normal(0, noise_std, data.shape)
        return data + noise
    
    def fit_kv_model(self, data: np.ndarray, noise_std: float = 0.01e-6) -> dict:
        """Fit Kelvin-Voigt model to data."""
        def residuals(params):
            G_prime, eta = params
            if G_prime < 1000 or G_prime > 20000 or eta < 0.1 or eta > 50:
                return 1e10
            
            pred = np.array([
                self.kv_model.compute_waveform(self.time, r, G_prime, eta)
                for r in self.receiver_distances
            ])
            return np.sum((data - pred)**2) / noise_std**2
        
        result = minimize(residuals, x0=[4500, 4.5], bounds=[(1000, 20000), (0.1, 50)])
        
        return {
            'G_prime': result.x[0],
            'eta': result.x[1],
            'rss': result.fun * noise_std**2,
            'n_params': 2,
            'success': result.success
        }
    
    def fit_pl_model(self, data: np.ndarray, noise_std: float = 0.01e-6) -> dict:
        """Fit Power-Law model to data."""
        def residuals(params):
            G0, alpha = params
            if G0 < 1000 or G0 > 20000 or alpha < 0.01 or alpha > 0.99:
                return 1e10
            
            pred = np.array([
                self.pl_model.compute_waveform(self.time, r, G0, alpha)
                for r in self.receiver_distances
            ])
            return np.sum((data - pred)**2) / noise_std**2
        
        result = minimize(residuals, x0=[4500, 0.25], bounds=[(1000, 20000), (0.01, 0.99)])
        
        return {
            'G0': result.x[0],
            'alpha': result.x[1],
            'rss': result.fun * noise_std**2,
            'n_params': 2,
            'success': result.success
        }
    
    def compute_information_criteria(self, rss: float, n_data: int, n_params: int) -> dict:
        """Compute AIC and BIC for model comparison."""
        # AIC = n·ln(RSS/n) + 2k
        aic = n_data * np.log(rss / n_data) + 2 * n_params
        
        # BIC = n·ln(RSS/n) + k·ln(n)
        bic = n_data * np.log(rss / n_data) + n_params * np.log(n_data)
        
        # AICc (corrected for small samples)
        aicc = aic + 2 * n_params * (n_params + 1) / (n_data - n_params - 1)
        
        return {'aic': aic, 'bic': bic, 'aicc': aicc}
    
    def run_comparison(self, true_model: Literal['kv', 'pl'] = 'kv'):
        """Run full model comparison."""
        print("=" * 70)
        print("MODEL COMPARISON: Kelvin-Voigt vs Power-Law Viscoelasticity")
        print("=" * 70)
        
        # Generate synthetic data
        print(f"\nGenerating data from {true_model.upper()} model...")
        if true_model == 'kv':
            true_params = {'G_prime': 5000, 'eta': 5}
            data = self.generate_kv_data(G_prime=5000, eta=5, noise_std=0.01e-6)
            print(f"  True: G' = {true_params['G_prime']} Pa, η = {true_params['eta']} Pa·s")
        else:
            true_params = {'G0': 5000, 'alpha': 0.3}
            data = self.generate_pl_data(G0=5000, alpha=0.3, noise_std=0.01e-6)
            print(f"  True: G₀ = {true_params['G0']} Pa, α = {true_params['alpha']}")
        
        n_data = data.size
        
        # Fit both models
        print("\n" + "-" * 70)
        print("Fitting Kelvin-Voigt model...")
        kv_fit = self.fit_kv_model(data)
        kv_ic = self.compute_information_criteria(kv_fit['rss'], n_data, kv_fit['n_params'])
        print(f"  Fitted: G' = {kv_fit['G_prime']:.1f} Pa, η = {kv_fit['eta']:.3f} Pa·s")
        print(f"  RSS = {kv_fit['rss']:.6e}")
        
        print("\nFitting Power-Law model...")
        pl_fit = self.fit_pl_model(data)
        pl_ic = self.compute_information_criteria(pl_fit['rss'], n_data, pl_fit['n_params'])
        print(f"  Fitted: G₀ = {pl_fit['G0']:.1f} Pa, α = {pl_fit['alpha']:.3f}")
        print(f"  RSS = {pl_fit['rss']:.6e}")
        
        # Model comparison
        print("\n" + "=" * 70)
        print("MODEL COMPARISON")
        print("=" * 70)
        print(f"{'Criterion':<15} {'Kelvin-Voigt':<20} {'Power-Law':<20} {'Preferred':<15}")
        print("-" * 70)
        
        for criterion in ['aic', 'bic', 'aicc']:
            kv_val = kv_ic[criterion]
            pl_val = pl_ic[criterion]
            winner = 'KV' if kv_val < pl_val else 'PL'
            delta = abs(kv_val - pl_val)
            print(f"{criterion.upper():<15} {kv_val:<20.2f} {pl_val:<20.2f} {winner + f' (Δ={delta:.1f})':<15}")
        
        # Evidence ratio (BIC-based)
        delta_bic = kv_ic['bic'] - pl_ic['bic']
        evidence_ratio = np.exp(-0.5 * delta_bic)
        print(f"\nEvidence ratio (KV/PL): {evidence_ratio:.3f}")
        if evidence_ratio > 10:
            print("→ Strong evidence for Kelvin-Voigt")
        elif evidence_ratio < 0.1:
            print("→ Strong evidence for Power-Law")
        else:
            print("→ Inconclusive preference")
        
        # Visualization
        self._plot_comparison(data, kv_fit, pl_fit, true_model, true_params)
        
        return {
            'kv_fit': kv_fit,
            'pl_fit': pl_fit,
            'kv_ic': kv_ic,
            'pl_ic': pl_ic,
            'winner': 'kv' if kv_ic['bic'] < pl_ic['bic'] else 'pl'
        }
    
    def _plot_comparison(self, data: np.ndarray, kv_fit: dict, pl_fit: dict,
                        true_model: str, true_params: dict):
        """Visualize model comparison."""
        fig, axes = plt.subplots(2, 3, figsize=(16, 10))
        
        # Generate predictions
        kv_pred = np.array([
            self.kv_model.compute_waveform(self.time, r, kv_fit['G_prime'], kv_fit['eta'])
            for r in self.receiver_distances
        ])
        
        pl_pred = np.array([
            self.pl_model.compute_waveform(self.time, r, pl_fit['G0'], pl_fit['alpha'])
            for r in self.receiver_distances
        ])
        
        # True model predictions
        if true_model == 'kv':
            true_pred = np.array([
                self.kv_model.compute_waveform(self.time, r, true_params['G_prime'], true_params['eta'])
                for r in self.receiver_distances
            ])
        else:
            true_pred = np.array([
                self.pl_model.compute_waveform(self.time, r, true_params['G0'], true_params['alpha'])
                for r in self.receiver_distances
            ])
        
        # Row 1: Waveforms at each receiver
        for i, (ax, r) in enumerate(zip(axes[0], self.receiver_distances)):
            ax.plot(self.time * 1000, data[i] * 1e6, 'k-', alpha=0.5, linewidth=0.8, label='Data')
            ax.plot(self.time * 1000, kv_pred[i] * 1e6, 'b--', linewidth=1.5, label=f"KV fit")
            ax.plot(self.time * 1000, pl_pred[i] * 1e6, 'r:', linewidth=1.5, label=f"PL fit")
            ax.set_xlabel('Time (ms)')
            ax.set_ylabel('Displacement (μm)')
            ax.set_title(f'Receiver at {r*100:.0f} cm')
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)
        
        # Row 2: Residuals, dispersion, and parameter comparison
        
        # Residuals (middle receiver)
        ax = axes[1, 0]
        kv_resid = (data[1] - kv_pred[1]) * 1e9  # nm
        pl_resid = (data[1] - pl_pred[1]) * 1e9
        ax.plot(self.time * 1000, kv_resid, 'b-', alpha=0.5, linewidth=0.8, label='KV residuals')
        ax.plot(self.time * 1000, pl_resid, 'r-', alpha=0.5, linewidth=0.8, label='PL residuals')
        ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        ax.set_xlabel('Time (ms)')
        ax.set_ylabel('Residual (nm)')
        ax.set_title('Residuals (middle receiver)')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        
        # Dispersion curves
        ax = axes[1, 1]
        freqs = np.linspace(20, 500, 100)
        
        # KV dispersion
        c_kv, att_kv = self.kv_model.dispersion_curve(freqs, kv_fit['G_prime'], kv_fit['eta'])
        
        # PL dispersion
        c_pl, att_pl = self.pl_model.dispersion_curve(freqs, pl_fit['G0'], pl_fit['alpha'])
        
        # True dispersion
        if true_model == 'kv':
            c_true, att_true = self.kv_model.dispersion_curve(freqs, true_params['G_prime'], true_params['eta'])
        else:
            c_true, att_true = self.pl_model.dispersion_curve(freqs, true_params['G0'], true_params['alpha'])
        
        ax.plot(freqs, c_kv, 'b--', linewidth=2, label='KV fit')
        ax.plot(freqs, c_pl, 'r:', linewidth=2, label='PL fit')
        ax.plot(freqs, c_true, 'g-', linewidth=2, alpha=0.7, label='True')
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Phase velocity (m/s)')
        ax.set_title('Dispersion curves')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        
        # Parameter comparison table
        ax = axes[1, 2]
        ax.axis('off')
        
        table_data = [
            ['Model', 'Parameter 1', 'Parameter 2', 'RSS'],
            ['True', f"G'={true_params.get('G_prime', '—')}" + f"/G₀={true_params.get('G0', '—')}",
             f"η={true_params.get('eta', '—')}" + f"/α={true_params.get('alpha', '—')}", '—'],
            ['KV fit', f"G'={kv_fit['G_prime']:.0f}", f"η={kv_fit['eta']:.2f}", f"{kv_fit['rss']:.2e}"],
            ['PL fit', f"G₀={pl_fit['G0']:.0f}", f"α={pl_fit['alpha']:.3f}", f"{pl_fit['rss']:.2e}"],
        ]
        
        table = ax.table(cellText=table_data, loc='center', cellLoc='center',
                        colWidths=[0.2, 0.25, 0.25, 0.25])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        
        # Highlight header
        for i in range(4):
            table[(0, i)].set_facecolor('#40466e')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        ax.set_title('Parameter Comparison', fontsize=12, fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig('model_comparison.png', dpi=150, bbox_inches='tight')
        plt.show()
        
        print("\n✓ Saved: model_comparison.png")


def main():
    """Run both cross-validation tests."""
    comparison = ModelComparison()
    
    # Test 1: KV data, fit both
    print("\n" + "=" * 70)
    print("TEST 1: Data from Kelvin-Voigt model")
    print("=" * 70)
    result_kv = comparison.run_comparison(true_model='kv')
    
    # Test 2: PL data, fit both
    print("\n\n" + "=" * 70)
    print("TEST 2: Data from Power-Law model")
    print("=" * 70)
    result_pl = comparison.run_comparison(true_model='pl')
    
    # Summary
    print("\n\n" + "=" * 70)
    print("OVERALL SUMMARY")
    print("=" * 70)
    print("\nTest 1 (KV data):")
    print(f"  Winner by BIC: {result_kv['winner'].upper()}")
    print(f"  KV RSS: {result_kv['kv_fit']['rss']:.4e}")
    print(f"  PL RSS: {result_kv['pl_fit']['rss']:.4e}")
    
    print("\nTest 2 (PL data):")
    print(f"  Winner by BIC: {result_pl['winner'].upper()}")
    print(f"  KV RSS: {result_pl['kv_fit']['rss']:.4e}")
    print(f"  PL RSS: {result_pl['pl_fit']['rss']:.4e}")


if __name__ == "__main__":
    main()
