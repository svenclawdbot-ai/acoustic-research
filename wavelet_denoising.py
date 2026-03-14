#!/usr/bin/env python3
"""
Wavelet Denoising Module for Shear Wave Ultrasound
===================================================

Conservative wavelet denoising for dispersion curve extraction.
Designed to avoid overfitting while improving SNR.

Key features:
- Symlet wavelets (phase-preserving)
- Loose thresholding (conservative denoising)
- Soft thresholding (smooth results)
- Level-adaptive thresholds

Author: Research Project
Date: March 14, 2026
"""

import numpy as np
import pywt
from scipy.signal import hilbert
import matplotlib.pyplot as plt


class WaveletDenoiser:
    """
    Conservative wavelet denoising for ultrasound signals.
    
    Uses loose thresholds to avoid overfitting while still
    improving SNR for dispersion curve extraction.
    """
    
    def __init__(self, wavelet='sym6', level=5, threshold_factor=2.0, 
                 mode='soft', threshold_method='universal'):
        """
        Initialize wavelet denoiser with conservative settings.
        
        Parameters:
        -----------
        wavelet : str
            Wavelet family. Default 'sym6' (good phase preservation)
            Options: 'sym4', 'sym6', 'sym8', 'db4', 'db6', 'coif2'
        level : int
            Decomposition level. Default 5 (conservative for ~1000-5000 samples)
        threshold_factor : float
            Multiplier for threshold (higher = looser/more conservative).
            Default 2.0 (2x the calculated threshold = very conservative)
        mode : str
            Thresholding mode: 'soft' (default), 'hard', 'garotte'
        threshold_method : str
            'universal' (default), 'minimax', 'sure'
        """
        self.wavelet = wavelet
        self.level = level
        self.threshold_factor = threshold_factor
        self.mode = mode
        self.threshold_method = threshold_method
        
        # Store decomposition for inspection
        self.coeffs_original = None
        self.coeffs_denoised = None
        self.thresholds = None
        
    def estimate_noise(self, detail_coeffs):
        """
        Estimate noise standard deviation from finest detail coefficients.
        Uses MAD (Median Absolute Deviation) - robust to outliers.
        """
        mad = np.median(np.abs(detail_coeffs))
        sigma = mad / 0.6745  # Convert MAD to std for Gaussian
        return sigma
    
    def compute_threshold(self, detail_coeffs, n_samples):
        """
        Compute threshold with conservative factor applied.
        """
        sigma = self.estimate_noise(detail_coeffs)
        
        if self.threshold_method == 'universal':
            # Universal threshold with conservative multiplier
            thresh = sigma * np.sqrt(2 * np.log(n_samples))
        elif self.threshold_method == 'minimax':
            # Simplified minimax approximation
            thresh = sigma * (0.3936 + 0.1829 * np.log2(n_samples))
        elif self.threshold_method == 'sure':
            # SURE threshold (adaptive)
            thresh = self._sure_threshold(detail_coeffs)
        else:
            thresh = sigma * np.sqrt(2 * np.log(n_samples))
        
        # Apply conservative factor (higher = looser thresholding)
        return thresh * self.threshold_factor
    
    def _sure_threshold(self, coeffs):
        """Stein's Unbiased Risk Estimate threshold."""
        n = len(coeffs)
        sorted_coeffs = np.sort(np.abs(coeffs))**2
        risks = np.zeros(n)
        
        for k in range(n):
            risks[k] = (n - 2 * (k + 1) + np.sum(sorted_coeffs[:k+1]) + 
                       (n - k - 1) * sorted_coeffs[k]) / n
        
        min_risk_idx = np.argmin(risks)
        return np.sqrt(sorted_coeffs[min_risk_idx])
    
    def denoise(self, signal):
        """
        Apply conservative wavelet denoising to signal.
        
        Parameters:
        -----------
        signal : array_like
            Input noisy signal
            
        Returns:
        --------
        denoised : ndarray
            Denoised signal
        """
        # Ensure 1D array
        signal = np.asarray(signal).flatten()
        n_samples = len(signal)
        
        # Adjust level if signal is too short
        max_level = pywt.dwt_max_level(n_samples, pywt.Wavelet(self.wavelet).dec_len)
        self.level = min(self.level, max_level)
        
        # Wavelet decomposition
        self.coeffs_original = pywt.wavedec(signal, self.wavelet, level=self.level)
        
        # Compute threshold from finest detail coefficients
        finest_detail = self.coeffs_original[-1]
        threshold = self.compute_threshold(finest_detail, n_samples)
        
        # Apply threshold to detail coefficients only (keep approximation)
        self.coeffs_denoised = [self.coeffs_original[0]]  # Keep approximation as-is
        self.thresholds = [0]  # No threshold on approximation
        
        for i, detail in enumerate(self.coeffs_original[1:], 1):
            # Level-dependent threshold (coarser levels get higher thresholds)
            level_threshold = threshold * np.sqrt(i)  # Increase for lower frequencies
            denoised_detail = pywt.threshold(detail, level_threshold, mode=self.mode)
            self.coeffs_denoised.append(denoised_detail)
            self.thresholds.append(level_threshold)
        
        # Reconstruct signal
        denoised = pywt.waverec(self.coeffs_denoised, self.wavelet)
        
        # Trim to original length (wavelet transform may add padding)
        return denoised[:n_samples]
    
    def compute_snr(self, original, denoised):
        """
        Estimate SNR improvement.
        Returns (input_snr_db, output_snr_db, improvement_db).
        """
        # Estimate noise as residual (conservative: assumes denoised is closer to true signal)
        noise_in = denoised - original  # Actually signal - denoised, but flipped for simplicity
        
        # Better estimate: assume signal power >> noise power
        signal_power = np.var(denoised)
        noise_power_in = np.var(original - denoised)
        
        input_snr = 10 * np.log10(signal_power / (noise_power_in + 1e-10))
        
        # Output SNR: if we had ground truth, but we don't
        # Use smoothness as proxy - lower high-frequency energy = better denoising
        original_hf = np.sum(np.abs(np.diff(original, 2)))
        denoised_hf = np.sum(np.abs(np.diff(denoised, 2)))
        
        return {
            'signal_power': signal_power,
            'noise_power_estimate': noise_power_in,
            'snr_db': input_snr,
            'hf_reduction': (original_hf - denoised_hf) / original_hf * 100
        }
    
    def plot_decomposition(self, figsize=(14, 10)):
        """Plot wavelet decomposition coefficients before/after thresholding."""
        if self.coeffs_original is None:
            raise ValueError("Must call denoise() first")
        
        n_levels = len(self.coeffs_original)
        fig, axes = plt.subplots(n_levels, 2, figsize=figsize)
        
        for i in range(n_levels):
            # Original coefficients
            ax_left = axes[i, 0] if n_levels > 1 else axes[0]
            ax_left.plot(self.coeffs_original[i], 'b-', alpha=0.7, linewidth=0.5)
            if i > 0 and self.thresholds:
                ax_left.axhline(self.thresholds[i], color='r', linestyle='--', alpha=0.5)
                ax_left.axhline(-self.thresholds[i], color='r', linestyle='--', alpha=0.5)
            ax_left.set_title(f'Level {i} - Original' if i > 0 else 'Approximation (Original)')
            ax_left.set_ylabel('Amplitude')
            
            # Denoised coefficients
            ax_right = axes[i, 1] if n_levels > 1 else axes[1]
            ax_right.plot(self.coeffs_denoised[i], 'g-', alpha=0.7, linewidth=0.5)
            ax_right.set_title(f'Level {i} - Denoised' if i > 0 else 'Approximation (Kept)')
            
            if i == 0:
                ax_left.set_ylabel('Approximation\nCoefficients')
                ax_right.set_ylabel('Approximation\nCoefficients')
        
        plt.tight_layout()
        return fig
    
    def plot_comparison(self, original, denoised, dt=None, title=None, figsize=(14, 8)):
        """Plot signal comparison: original, denoised, and residuals."""
        fig, axes = plt.subplots(3, 1, figsize=figsize)
        
        if dt is None:
            t = np.arange(len(original))
            xlabel = 'Sample'
        else:
            t = np.arange(len(original)) * dt * 1000  # ms
            xlabel = 'Time (ms)'
        
        # Original
        axes[0].plot(t, original, 'b-', alpha=0.7, linewidth=0.8, label='Original')
        axes[0].set_ylabel('Amplitude')
        axes[0].set_title('Original Signal' if title is None else title)
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Denoised
        axes[1].plot(t, denoised, 'g-', alpha=0.9, linewidth=0.8, label='Denoised')
        axes[1].set_ylabel('Amplitude')
        axes[1].set_title(f'Denoised (threshold_factor={self.threshold_factor}, wavelet={self.wavelet})')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        # Residual (noise removed)
        residual = original - denoised
        axes[2].plot(t, residual, 'r-', alpha=0.7, linewidth=0.5, label='Removed (noise)')
        axes[2].set_ylabel('Amplitude')
        axes[2].set_xlabel(xlabel)
        axes[2].set_title('Residual (Removed Component)')
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig


def denoise_signal(signal, wavelet='sym6', level=5, threshold_factor=2.0, 
                   mode='soft', verbose=True):
    """
    Convenience function for one-shot denoising.
    
    Uses conservative defaults to avoid overfitting.
    """
    denoiser = WaveletDenoiser(
        wavelet=wavelet,
        level=level,
        threshold_factor=threshold_factor,
        mode=mode
    )
    
    denoised = denoiser.denoise(signal)
    
    if verbose:
        metrics = denoiser.compute_snr(signal, denoised)
        print(f"Wavelet Denoising ({wavelet}, level={denoiser.level})")
        print(f"  Threshold factor: {threshold_factor}x (conservative)")
        print(f"  Mode: {mode}")
        print(f"  SNR estimate: {metrics['snr_db']:.1f} dB")
        print(f"  High-freq reduction: {metrics['hf_reduction']:.1f}%")
    
    return denoised, denoiser


# =============================================================================
# Integration with existing group velocity extraction
# =============================================================================

def extract_group_velocity_denoised(sig1, sig2, dt, distance,
                                    denoise_before=True,
                                    wavelet='sym6', threshold_factor=2.0,
                                    freq_range=None):
    """
    Group velocity extraction with optional wavelet denoising.
    
    Drop-in replacement for extract_group_velocity_fixed() with
    conservative wavelet pre-processing.
    """
    from scipy.signal import hilbert
    
    # Optional denoising (conservative)
    if denoise_before:
        sig1, _ = denoise_signal(sig1, wavelet=wavelet, 
                                 threshold_factor=threshold_factor, verbose=False)
        sig2, _ = denoise_signal(sig2, wavelet=wavelet, 
                                 threshold_factor=threshold_factor, verbose=False)
    
    # Standard envelope extraction
    env1 = np.abs(hilbert(sig1))
    env2 = np.abs(hilbert(sig2))
    
    # Search window: 45-80 ms
    t = np.arange(len(env1)) * dt * 1000
    search_mask = (t >= 45) & (t <= 80)
    
    if not np.any(search_mask):
        return np.nan, np.nan, np.nan, env1, env2, "No search window"
    
    search_indices = np.where(search_mask)[0]
    
    peak1_rel_idx = np.argmax(env1[search_mask])
    peak2_rel_idx = np.argmax(env2[search_mask])
    
    peak1_idx = search_indices[peak1_rel_idx]
    peak2_idx = search_indices[peak2_rel_idx]
    
    t1_ms = peak1_idx * dt * 1000
    t2_ms = peak2_idx * dt * 1000
    
    delay_s = (t2_ms - t1_ms) * 1e-3
    
    if delay_s <= 0:
        return np.nan, t1_ms, t2_ms, env1, env2, f"Invalid delay {delay_s*1000:.2f} ms"
    
    c_g = distance / delay_s
    
    return c_g, t1_ms, t2_ms, env1, env2, "OK"


if __name__ == "__main__":
    # Quick test with synthetic signal
    print("Wavelet Denoising Module Test")
    print("=" * 50)
    
    # Create synthetic ultrasound-like signal
    t = np.linspace(0, 0.1, 2000)  # 100 ms, 20 kHz sampling
    f0 = 100  # 100 Hz shear wave
    
    # Chirp signal (dispersive)
    signal = np.sin(2 * np.pi * f0 * t + 50 * t**2) * np.exp(-((t - 0.05)**2) / 0.001)
    
    # Add noise
    noise_level = 0.3
    noisy = signal + noise_level * np.std(signal) * np.random.randn(len(signal))
    
    print(f"\nSignal: {len(signal)} samples")
    print(f"Noise level: {noise_level * 100:.0f}% of signal std")
    
    # Denoise with conservative settings
    print("\n--- Conservative Denoising ---")
    denoised, denoiser = denoise_signal(noisy, threshold_factor=2.0, verbose=True)
    
    # Compare
    mse_noisy = np.mean((noisy - signal)**2)
    mse_denoised = np.mean((denoised - signal)**2)
    
    print(f"\nMSE (noisy vs true):   {mse_noisy:.6f}")
    print(f"MSE (denoised vs true): {mse_denoised:.6f}")
    print(f"Improvement: {mse_noisy/mse_denoised:.1f}x")
    
    # Plot
    fig = denoiser.plot_comparison(noisy, denoised, dt=t[1]-t[0])
    plt.savefig('wavelet_denoise_test.png', dpi=150, bbox_inches='tight')
    print("\nSaved: wavelet_denoise_test.png")
    plt.close(fig)
    print("Test complete!")
