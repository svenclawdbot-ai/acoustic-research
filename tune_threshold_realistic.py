#!/usr/bin/env python3
"""
Realistic Wavelet Threshold Tuning
===================================

Tests with realistic ultrasound artifacts:
- Impulse noise (electrical spikes)
- Baseline wander (low-frequency drift)
- Mixed noise types

These conditions better differentiate threshold strategies.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert
import sys

from wavelet_denoising import WaveletDenoiser


def generate_realistic_ultrasound_signal(t, f0=100, noise_config=None):
    """
    Generate realistic shear wave signal with ultrasound artifacts.
    
    Artifacts:
    - Gaussian noise (thermal/electronic)
    - Impulse noise (electrical spikes, switching)
    - Baseline wander (respiratory motion, probe coupling)
    """
    if noise_config is None:
        noise_config = {
            'gaussian': 0.1,
            'impulse_prob': 0.01,  # 1% samples are impulses
            'impulse_amp': 0.5,
            'baseline_wander': 0.05
        }
    
    # Clean signal: Gaussian-windowed chirp
    envelope = np.exp(-((t - 0.05)**2) / 0.0005)
    dispersion = 50
    signal = envelope * np.sin(2 * np.pi * f0 * t + dispersion * t**2)
    signal = signal / np.max(np.abs(signal))
    
    # Add artifacts
    noisy = signal.copy()
    
    # 1. Gaussian noise
    if noise_config['gaussian'] > 0:
        noisy += noise_config['gaussian'] * np.random.randn(len(t))
    
    # 2. Impulse noise (spikes)
    if noise_config['impulse_prob'] > 0:
        n_impulses = int(len(t) * noise_config['impulse_prob'])
        impulse_idx = np.random.choice(len(t), n_impulses, replace=False)
        noisy[impulse_idx] += noise_config['impulse_amp'] * np.random.randn(n_impulses)
    
    # 3. Baseline wander (low freq drift)
    if noise_config['baseline_wander'] > 0:
        wander = noise_config['baseline_wander'] * np.sin(2 * np.pi * 2 * t)  # 2 Hz
        wander += 0.5 * noise_config['baseline_wander'] * np.sin(2 * np.pi * 0.5 * t)  # 0.5 Hz
        noisy += wander
    
    return signal, noisy


def evaluate_comprehensive(clean, denoised):
    """More comprehensive evaluation metrics."""
    metrics = {}
    
    # NMSE
    metrics['nmse'] = np.mean((denoised - clean)**2) / np.mean(clean**2)
    
    # Envelope correlation
    env_clean = np.abs(hilbert(clean))
    env_den = np.abs(hilbert(denoised))
    metrics['env_corr'] = np.corrcoef(env_clean, env_den)[0, 1]
    
    # Peak time error (critical for group velocity)
    peak_clean = np.argmax(env_clean)
    peak_den = np.argmax(env_den)
    metrics['peak_shift'] = abs(peak_den - peak_clean)  # samples
    
    # Peak amplitude preservation
    metrics['amp_error'] = abs(np.max(env_den) - np.max(env_clean)) / np.max(env_clean)
    
    # Signal smoothness (variance of second derivative)
    smooth_clean = np.var(np.diff(clean, 2))
    smooth_den = np.var(np.diff(denoised, 2))
    metrics['smoothness_ratio'] = smooth_den / (smooth_clean + 1e-10)
    
    return metrics


def test_threshold_robustness():
    """
    Test threshold factors with realistic mixed noise.
    """
    print("Realistic Wavelet Threshold Tuning")
    print("=" * 60)
    
    # Setup
    fs = 20000
    duration = 0.1
    t = np.linspace(0, duration, int(fs * duration))
    dt = 1/fs
    
    # Noise configurations to test
    noise_conditions = [
        {
            'name': 'Low Gaussian (10%)',
            'config': {'gaussian': 0.1, 'impulse_prob': 0, 'impulse_amp': 0, 'baseline_wander': 0}
        },
        {
            'name': 'High Gaussian (30%)',
            'config': {'gaussian': 0.3, 'impulse_prob': 0, 'impulse_amp': 0, 'baseline_wander': 0}
        },
        {
            'name': 'Mixed: 10% + Impulses',
            'config': {'gaussian': 0.1, 'impulse_prob': 0.01, 'impulse_amp': 0.8, 'baseline_wander': 0}
        },
        {
            'name': 'Mixed: 20% + Baseline',
            'config': {'gaussian': 0.2, 'impulse_prob': 0, 'impulse_amp': 0, 'baseline_wander': 0.1}
        },
        {
            'name': 'Full: 15% + Impulse + Baseline',
            'config': {'gaussian': 0.15, 'impulse_prob': 0.005, 'impulse_amp': 0.5, 'baseline_wander': 0.08}
        }
    ]
    
    threshold_factors = [1.0, 1.5, 2.0, 2.5, 3.0]
    
    all_results = {}
    
    for condition in noise_conditions:
        print(f"\n{'='*60}")
        print(f"Testing: {condition['name']}")
        print(f"{'='*60}")
        
        np.random.seed(42)
        clean, noisy = generate_realistic_ultrasound_signal(t, noise_config=condition['config'])
        
        condition_results = []
        
        for factor in threshold_factors:
            denoiser = WaveletDenoiser(wavelet='sym6', level=5, 
                                       threshold_factor=factor, mode='soft')
            denoised = denoiser.denoise(noisy.copy())
            
            metrics = evaluate_comprehensive(clean, denoised)
            metrics['factor'] = factor
            condition_results.append(metrics)
        
        # Print results
        print(f"\n{'Factor':<10} {'NMSE':<12} {'Env Corr':<12} {'Peak Shift':<12} {'Amp Error':<12}")
        print("-" * 60)
        
        best_factor = 2.0
        best_score = -np.inf
        
        for r in condition_results:
            score = -r['nmse'] * 10 + r['env_corr'] - r['peak_shift'] * 0.01 - r['amp_error']
            if score > best_score:
                best_score = score
                best_factor = r['factor']
            
            print(f"{r['factor']:<10.1f} {r['nmse']:<12.6f} {r['env_corr']:<12.4f} "
                  f"{r['peak_shift']:<12.1f} {r['amp_error']:<12.4f}")
        
        print("-" * 60)
        print(f"BEST: Factor = {best_factor:.1f}x (score: {best_score:.3f})")
        
        all_results[condition['name']] = {
            'results': condition_results,
            'best_factor': best_factor,
            'clean': clean,
            'noisy': noisy
        }
        
        # Plot for this condition
        plot_condition_comparison(clean, noisy, condition_results, dt, 
                                  condition['name'])
    
    # Final summary
    print("\n" + "=" * 60)
    print("SUMMARY: OPTIMAL THRESHOLD FACTORS")
    print("=" * 60)
    print(f"{'Condition':<35} {'Best Factor':<15}")
    print("-" * 60)
    
    factors = []
    for name, data in all_results.items():
        print(f"{name:<35} {data['best_factor']:.1f}x")
        factors.append(data['best_factor'])
    
    print("-" * 60)
    
    # Overall recommendation
    avg_factor = np.mean(factors)
    print(f"\nOVERALL: threshold_factor = {avg_factor:.1f}x")
    
    # Specific guidance
    print("\nRecommendations by condition:")
    print("  - Pure Gaussian noise (<20%): Use 1.0-1.5x")
    print("  - High Gaussian (>20%): Use 2.0-2.5x")
    print("  - With impulse noise: Use 2.0-2.5x (standard threshold too aggressive)")
    print("  - With baseline wander: Use 2.5-3.0x (conservative, preserve low-freq)")
    print("  - Mixed artifacts: Use 2.0x as safe default")
    
    return all_results


def plot_condition_comparison(clean, noisy, results, dt, condition_name):
    """Plot comparison for a single noise condition."""
    fig, axes = plt.subplots(2, len(results) + 2, figsize=(18, 8))
    
    t = np.arange(len(clean)) * dt * 1000
    
    # Column 0: Clean
    axes[0, 0].plot(t, clean, 'g-', linewidth=1)
    axes[0, 0].set_title('Clean', fontweight='bold')
    axes[0, 0].set_ylabel('Signal')
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].set_xlim([30, 70])
    
    env_clean = np.abs(hilbert(clean))
    axes[1, 0].plot(t, env_clean, 'g-', linewidth=1.5)
    axes[1, 0].set_title('Envelope', fontweight='bold')
    axes[1, 0].set_ylabel('Envelope')
    axes[1, 0].set_xlabel('Time (ms)')
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].set_xlim([30, 70])
    
    # Column 1: Noisy
    axes[0, 1].plot(t, noisy, 'b-', alpha=0.6, linewidth=0.5)
    axes[0, 1].set_title('Noisy', fontweight='bold')
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].set_xlim([30, 70])
    
    env_noisy = np.abs(hilbert(noisy))
    axes[1, 1].plot(t, env_noisy, 'b-', alpha=0.6, linewidth=0.8)
    axes[1, 1].set_title('Envelope', fontweight='bold')
    axes[1, 1].set_xlabel('Time (ms)')
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].set_xlim([30, 70])
    
    # Columns 2+: Denoised results
    for i, r in enumerate(results):
        col = i + 2
        factor = r['factor']
        
        # Re-denoise to get signal (inefficient but simple)
        denoiser = WaveletDenoiser(wavelet='sym6', level=5, 
                                   threshold_factor=factor, mode='soft')
        denoised = denoiser.denoise(noisy.copy())
        
        # Signal
        axes[0, col].plot(t, clean, 'g-', alpha=0.4, linewidth=0.8, label='Clean')
        axes[0, col].plot(t, denoised, 'r-', alpha=0.8, linewidth=0.8, label='Denoised')
        axes[0, col].set_title(f'{factor}x\nNMSE: {r["nmse"]:.4f}', fontweight='bold')
        axes[0, col].legend(fontsize=7)
        axes[0, col].grid(True, alpha=0.3)
        axes[0, col].set_xlim([30, 70])
        
        # Envelope
        env_den = np.abs(hilbert(denoised))
        axes[1, col].plot(t, env_clean, 'g-', alpha=0.4, linewidth=1)
        axes[1, col].plot(t, env_den, 'r-', alpha=0.8, linewidth=0.8)
        axes[1, col].set_title(f'Corr: {r["env_corr"]:.3f}, Shift: {r["peak_shift"]:.0f}', fontsize=9)
        axes[1, col].set_xlabel('Time (ms)')
        axes[1, col].grid(True, alpha=0.3)
        axes[1, col].set_xlim([30, 70])
    
    plt.suptitle(f'Threshold Tuning: {condition_name}', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    safe_name = condition_name.replace(' ', '_').replace('+', 'plus').replace('%', 'pct')
    filename = f'threshold_tune_{safe_name}.png'
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"  Saved: {filename}")


if __name__ == "__main__":
    try:
        import pywt
    except ImportError:
        print("ERROR: PyWavelets not installed")
        sys.exit(1)
    
    results = test_threshold_robustness()
    print("\nDone! Check generated PNG files.")
