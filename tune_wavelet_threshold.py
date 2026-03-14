#!/usr/bin/env python3
"""
Threshold Tuning for Wavelet Denoising
=======================================

Systematic comparison of threshold factors for shear wave signals.
Tests: 1.0x (standard), 1.5x, 2.0x, 2.5x, 3.0x (very conservative)

Metrics:
- MSE vs ground truth (simulated data)
- Dispersion curve accuracy
- Group velocity extraction error
- Visual inspection

Author: Research Project
Date: March 14, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert
import sys

from wavelet_denoising import WaveletDenoiser, denoise_signal


def generate_test_signal(t, f0=100, G_prime=2000, eta=0.5, noise_level=0.1):
    """
    Generate realistic shear wave signal with Kelvin-Voigt dispersion.
    
    For simplicity, use a Gaussian-windowed chirp that approximates
    dispersive shear wave propagation in soft tissue.
    """
    # Group velocity at center frequency (approximate)
    omega0 = 2 * np.pi * f0
    G_star = np.sqrt(G_prime**2 + (omega0 * eta)**2)
    c_g = np.sqrt(2 / 1000) * np.sqrt(G_star**2 / (G_prime + G_star))
    
    # Dispersive chirp (simplified model)
    # Phase: phi(t) = 2*pi*f0*t + dispersion_term
    dispersion = 50 * (eta / 0.5)  # Scales with viscosity
    
    # Gaussian envelope centered at 50 ms
    envelope = np.exp(-((t - 0.05)**2) / 0.0005)
    
    # Chirped signal
    signal = envelope * np.sin(2 * np.pi * f0 * t + dispersion * t**2)
    
    # Normalize
    signal = signal / np.max(np.abs(signal))
    
    # Add noise
    noise = noise_level * np.random.randn(len(t))
    noisy_signal = signal + noise
    
    return signal, noisy_signal, c_g


def evaluate_denoising(clean_signal, noisy_signal, denoised_signal, true_c_g=None):
    """
    Comprehensive evaluation metrics.
    """
    metrics = {}
    
    # 1. MSE vs clean signal
    metrics['mse'] = np.mean((denoised_signal - clean_signal)**2)
    metrics['nmse'] = metrics['mse'] / np.mean(clean_signal**2)  # Normalized
    
    # 2. Max amplitude preservation
    metrics['amplitude_error'] = abs(np.max(np.abs(denoised_signal)) - np.max(np.abs(clean_signal)))
    
    # 3. Envelope correlation
    env_clean = np.abs(hilbert(clean_signal))
    env_denoised = np.abs(hilbert(denoised_signal))
    metrics['envelope_corr'] = np.corrcoef(env_clean, env_denoised)[0, 1]
    
    # 4. Group velocity estimation (if applicable)
    if true_c_g is not None:
        # Simple peak detection for arrival time
        env = np.abs(hilbert(denoised_signal))
        peak_idx = np.argmax(env)
        # This is a simplified metric - in practice would use 2-receiver method
        metrics['peak_time_ms'] = peak_idx / len(denoised_signal) * 100  # Assuming 100ms
    
    # 5. High-frequency content (smoothness)
    hf_clean = np.sum(np.abs(np.diff(clean_signal, 2)))
    hf_denoised = np.sum(np.abs(np.diff(denoised_signal, 2)))
    metrics['hf_ratio'] = hf_denoised / (hf_clean + 1e-10)
    
    return metrics


def tune_threshold_single_signal(clean_signal, noisy_signal, threshold_factors, 
                                  wavelet='sym6', level=5, true_c_g=None):
    """
    Test multiple threshold factors on a single signal.
    """
    results = []
    
    for factor in threshold_factors:
        denoiser = WaveletDenoiser(
            wavelet=wavelet,
            level=level,
            threshold_factor=factor,
            mode='soft'
        )
        
        denoised = denoiser.denoise(noisy_signal.copy())
        metrics = evaluate_denoising(clean_signal, noisy_signal, denoised, true_c_g)
        metrics['threshold_factor'] = factor
        
        results.append({
            'factor': factor,
            'denoised': denoised,
            'denoiser': denoiser,
            'metrics': metrics
        })
    
    return results


def plot_threshold_comparison(clean_signal, noisy_signal, results, dt, 
                               noise_level, save_path='threshold_tuning.png'):
    """
    Create comprehensive comparison plot.
    """
    n_factors = len(results)
    fig = plt.figure(figsize=(16, 12))
    
    # Time vector in ms
    t = np.arange(len(clean_signal)) * dt * 1000
    
    # Create grid
    gs = fig.add_gridspec(3, n_factors + 1, hspace=0.4, wspace=0.3)
    
    # Column 0: Original signals
    ax_clean = fig.add_subplot(gs[0, 0])
    ax_noisy = fig.add_subplot(gs[1, 0])
    ax_metrics = fig.add_subplot(gs[2, :])
    
    # Plot clean signal
    ax_clean.plot(t, clean_signal, 'g-', linewidth=1)
    ax_clean.set_title('Clean Signal (Ground Truth)', fontweight='bold')
    ax_clean.set_ylabel('Amplitude')
    ax_clean.grid(True, alpha=0.3)
    ax_clean.set_xlim([30, 70])
    
    # Plot noisy signal
    ax_noisy.plot(t, noisy_signal, 'b-', alpha=0.7, linewidth=0.5)
    ax_noisy.set_title(f'Noisy Signal ({noise_level*100:.0f}% noise)', fontweight='bold')
    ax_noisy.set_ylabel('Amplitude')
    ax_noisy.grid(True, alpha=0.3)
    ax_noisy.set_xlim([30, 70])
    
    # Columns 1+: Denoised results
    for i, result in enumerate(results):
        factor = result['factor']
        denoised = result['denoised']
        metrics = result['metrics']
        
        # Row 0: Signal comparison
        ax_sig = fig.add_subplot(gs[0, i + 1])
        ax_sig.plot(t, clean_signal, 'g-', alpha=0.5, linewidth=1, label='Clean')
        ax_sig.plot(t, denoised, 'r-', alpha=0.8, linewidth=0.8, label='Denoised')
        ax_sig.set_title(f'Factor = {factor}x\nNMSE: {metrics["nmse"]:.4f}', 
                        fontweight='bold')
        ax_sig.legend(fontsize=7)
        ax_sig.grid(True, alpha=0.3)
        ax_sig.set_xlim([30, 70])
        if i == 0:
            ax_sig.set_ylabel('Amplitude')
        
        # Row 1: Envelope comparison
        ax_env = fig.add_subplot(gs[1, i + 1])
        env_clean = np.abs(hilbert(clean_signal))
        env_denoised = np.abs(hilbert(denoised))
        
        ax_env.plot(t, env_clean, 'g-', alpha=0.5, linewidth=1.5, label='Clean env')
        ax_env.plot(t, env_denoised, 'r-', alpha=0.8, linewidth=1, label='Denoised env')
        ax_env.set_title(f'Envelope corr: {metrics["envelope_corr"]:.3f}', fontsize=9)
        ax_env.legend(fontsize=7)
        ax_env.grid(True, alpha=0.3)
        ax_env.set_xlim([30, 70])
        if i == 0:
            ax_env.set_ylabel('Envelope')
        
    # Row 2: Metrics summary
    factors = [r['factor'] for r in results]
    nmses = [r['metrics']['nmse'] for r in results]
    corrs = [r['metrics']['envelope_corr'] for r in results]
    hfratios = [r['metrics']['hf_ratio'] for r in results]
    
    ax_metrics_twin = ax_metrics.twinx()
    
    l1 = ax_metrics.plot(factors, nmses, 'b-o', label='NMSE (lower=better)', linewidth=2, markersize=8)
    l2 = ax_metrics.plot(factors, corrs, 'g-s', label='Envelope Corr (higher=better)', linewidth=2, markersize=8)
    l3 = ax_metrics_twin.plot(factors, hfratios, 'r-^', label='HF Ratio (≈1 ideal)', linewidth=2, markersize=8)
    
    ax_metrics.set_xlabel('Threshold Factor', fontsize=12)
    ax_metrics.set_ylabel('NMSE / Correlation', fontsize=12)
    ax_metrics_twin.set_ylabel('HF Ratio', fontsize=12, color='r')
    ax_metrics_twin.tick_params(axis='y', labelcolor='r')
    ax_metrics.grid(True, alpha=0.3)
    ax_metrics.set_title('Performance Metrics vs Threshold Factor', fontweight='bold', fontsize=12)
    
    # Combined legend
    lines = l1 + l2 + l3
    labels = [l.get_label() for l in lines]
    ax_metrics.legend(lines, labels, loc='upper right')
    
    plt.suptitle(f'Wavelet Denoising Threshold Tuning ({results[0]["denoiser"].wavelet} wavelet, '
                 f'{noise_level*100:.0f}% noise)', 
                 fontsize=14, fontweight='bold', y=1.02)
    
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Saved: {save_path}")
    
    return fig


def print_summary_table(results, noise_level):
    """
    Print formatted comparison table.
    """
    print("\n" + "="*80)
    print(f"THRESHOLD TUNING RESULTS ({noise_level*100:.0f}% noise)")
    print("="*80)
    print(f"{'Factor':<10} {'NMSE':<12} {'Envelope Corr':<15} {'HF Ratio':<12} {'Verdict':<15}")
    print("-"*80)
    
    best_factor = None
    best_score = -np.inf
    
    for r in results:
        factor = r['factor']
        m = r['metrics']
        
        # Composite score (higher is better)
        # Balance: low NMSE, high correlation, HF ratio close to 1
        score = -m['nmse'] * 10 + m['envelope_corr'] - abs(m['hf_ratio'] - 1)
        
        if score > best_score:
            best_score = score
            best_factor = factor
        
        # Verdict
        if factor == 1.0:
            verdict = "Standard (may overfit)"
        elif factor == 1.5:
            verdict = "Slightly conservative"
        elif factor == 2.0:
            verdict = "Balanced"
        elif factor == 2.5:
            verdict = "Conservative"
        elif factor >= 3.0:
            verdict = "Very conservative"
        else:
            verdict = ""
        
        print(f"{factor:<10.1f} {m['nmse']:<12.6f} {m['envelope_corr']:<15.4f} "
              f"{m['hf_ratio']:<12.3f} {verdict:<15}")
    
    print("-"*80)
    print(f"RECOMMENDED: Factor = {best_factor}x (composite score: {best_score:.3f})")
    print("="*80)
    
    return best_factor


def test_multiple_noise_levels():
    """
    Run threshold tuning across different noise levels.
    """
    print("\n" + "="*80)
    print("THRESHOLD TUNING ACROSS NOISE LEVELS")
    print("="*80)
    
    # Test parameters
    fs = 20000  # 20 kHz sampling
    duration = 0.1  # 100 ms
    t = np.linspace(0, duration, int(fs * duration))
    dt = 1/fs
    
    noise_levels = [0.05, 0.10, 0.20, 0.30]
    threshold_factors = [1.0, 1.5, 2.0, 2.5, 3.0]
    
    summary = {}
    
    for noise_level in noise_levels:
        print(f"\n--- Testing {noise_level*100:.0f}% noise level ---")
        
        # Generate signals (same random seed for consistency)
        np.random.seed(42)
        clean, noisy, true_cg = generate_test_signal(t, noise_level=noise_level)
        
        # Tune thresholds
        results = tune_threshold_single_signal(
            clean, noisy, threshold_factors, 
            wavelet='sym6', level=5, true_c_g=true_cg
        )
        
        # Find best
        best_factor = print_summary_table(results, noise_level)
        summary[noise_level] = best_factor
        
        # Plot for this noise level
        plot_threshold_comparison(
            clean, noisy, results, dt, noise_level,
            save_path=f'threshold_tuning_{int(noise_level*100):02d}pct.png'
        )
    
    # Final recommendation
    print("\n" + "="*80)
    print("SUMMARY: RECOMMENDED THRESHOLD FACTORS")
    print("="*80)
    print(f"{'Noise Level':<15} {'Recommended Factor':<20}")
    print("-"*80)
    for nl, factor in summary.items():
        print(f"{nl*100:.0f}%{'':<10} {factor:.1f}x")
    print("-"*80)
    
    # Overall recommendation
    factors = list(summary.values())
    avg_factor = np.mean(factors)
    print(f"\nOVERALL RECOMMENDATION: threshold_factor = {avg_factor:.1f}x")
    print("  For varying noise conditions, use 2.0x as a safe default")
    print("  Increase to 2.5x for high noise (>20%)")
    print("  Decrease to 1.5x for low noise (<10%)")
    print("="*80)
    
    return summary


if __name__ == "__main__":
    import os
    
    print("Wavelet Threshold Tuning")
    print("=" * 50)
    
    # Check if PyWavelets is available
    try:
        import pywt
    except ImportError:
        print("ERROR: PyWavelets not installed")
        print("Run: pip install PyWavelets")
        sys.exit(1)
    
    # Run comprehensive tuning
    summary = test_multiple_noise_levels()
    
    print("\nDone! Check generated PNG files for visualizations.")
