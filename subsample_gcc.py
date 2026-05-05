"""
subsample_gcc.py - Sub-sample Cross-Correlation
Part 1 of April 14 Engineering Challenge

Provides both standard GCC and GCC-PHAT with sub-sample precision
via parabolic interpolation.
"""

import numpy as np
from scipy import signal
from scipy.signal import chirp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def parabolic_interp(y, idx):
    """
    Sub-sample peak location via parabolic fit around idx.
    
    Returns interpolated peak position with sub-sample precision.
    """
    if idx <= 0 or idx >= len(y) - 1:
        return float(idx)
    
    alpha, beta, gamma = y[idx-1], y[idx], y[idx+1]
    denom = alpha - 2*beta + gamma
    
    if abs(denom) < 1e-12:
        return float(idx)
    
    p = 0.5 * (alpha - gamma) / denom
    return idx + p


def gcc_standard(sig1, sig2, fs):
    """
    Standard cross-correlation with sub-sample parabolic interpolation.
    
    Parameters:
    -----------
    sig1, sig2 : array
        Input signals
    fs : float
        Sample rate in Hz
        
    Returns:
    --------
    delay : float
        Estimated delay in seconds (positive = sig2 delayed relative to sig1)
    corr : float
        Peak correlation coefficient
    """
    # Linear cross-correlation (full mode gives lags from -(N-1) to +(N-1))
    ccf = signal.correlate(sig2, sig1, mode='full', method='auto')
    
    # Find peak
    peak_idx = np.argmax(np.abs(ccf))
    peak_fine = parabolic_interp(np.abs(ccf), peak_idx)
    
    # Convert to lag (0 lag is at index len(sig1)-1)
    n = len(sig1)
    lag = peak_fine - (n - 1)
    delay = lag / fs
    
    # Normalized correlation
    corr_max = ccf[peak_idx] / (np.std(sig1) * np.std(sig2) * n + 1e-12)
    
    return delay, corr_max


def gcc_phat(sig1, sig2, fs, freq_range=None):
    """
    GCC-PHAT with optional frequency band limiting.
    
    PHAT whitening can amplify noise. This implementation allows
    restricting to a frequency band where signal energy is present.
    
    Parameters:
    -----------
    sig1, sig2 : array
        Input signals
    fs : float
        Sample rate in Hz
    freq_range : tuple (f_min, f_max), optional
        Frequency band to use (Hz). If None, uses full bandwidth
        with regularization to prevent noise amplification.
        
    Returns:
    --------
    delay : float
        Estimated delay in seconds
    corr : float
        Peak correlation value
    """
    n = len(sig1)
    n_fft = 2 ** int(np.ceil(np.log2(2 * n)))
    
    X1 = np.fft.fft(sig1, n=n_fft)
    X2 = np.fft.fft(sig2, n=n_fft)
    freqs = np.fft.fftfreq(n_fft, 1/fs)
    
    # Cross-power spectrum
    R = X2 * np.conj(X1)
    
    # PHAT whitening with regularization to prevent noise amplification
    if freq_range is not None:
        # Band-limited PHAT
        f_min, f_max = freq_range
        band_mask = (np.abs(freqs) >= f_min) & (np.abs(freqs) <= f_max)
        
        # Within band: apply PHAT
        R_phased = R.copy()
        R_phased[band_mask] /= (np.abs(R[band_mask]) + 1e-12)
        # Outside band: zero out (don't use)
        R_phased[~band_mask] = 0
    else:
        # Full bandwidth with soft regularization
        eps = 1e-6 * np.max(np.abs(R))
        R_phased = R / (np.abs(R) + eps)
    
    # Transform to time domain
    ccf = np.fft.ifft(R_phased).real
    
    # Reconstruct full correlation (similar to 'full' mode)
    # ccf[0] = 0 lag, ccf[1:n] = +ve lags, ccf[-n+1:] = -ve lags
    ccf_full = np.concatenate([ccf[-(n-1):], ccf[:n]])
    
    # Find peak
    peak_idx = np.argmax(np.abs(ccf_full))
    peak_fine = parabolic_interp(np.abs(ccf_full), peak_idx)
    
    # Convert to lag
    lag = peak_fine - (n - 1)
    delay = lag / fs
    
    corr_max = np.abs(ccf_full[peak_idx]) / (np.max(np.abs(ccf_full)) + 1e-12)
    
    return delay, corr_max


def generate_test_signal(fs=10000, duration=0.1, f0=50, f1=200, 
                         delay_samples=0.0, noise_std=0.0):
    """
    Generate synthetic chirp signal with known sub-sample delay.
    
    Uses proper fractional delay filtering.
    """
    t = np.arange(0, duration, 1/fs)
    
    # Linear chirp (sweep from f0 to f1)
    sig1 = chirp(t, f0, duration, f1, method='linear')
    
    # Apply fractional delay using sinc interpolation
    if delay_samples != 0:
        # Design fractional delay filter using sinc
        filter_len = 21  # Must be odd
        center = filter_len // 2
        n = np.arange(filter_len)
        
        # Sinc function centered at fractional position
        h = np.sinc(n - center - delay_samples)
        
        # Apply Blackman window to reduce artifacts
        window = np.blackman(filter_len)
        h = h * window
        
        # Normalize
        h = h / np.sum(h)
        
        # Convolve
        sig2 = signal.convolve(sig1, h, mode='same')
    else:
        sig2 = sig1.copy()
    
    # Add noise
    if noise_std > 0:
        sig1 = sig1 + noise_std * np.random.randn(len(sig1))
        sig2 = sig2 + noise_std * np.random.randn(len(sig2))
    
    return sig1, sig2, t


def validate_subsample_gcc():
    """
    Run validation tests for sub-sample delay estimation.
    
    Tests:
    1. Sub-sample precision (target: < 0.1 sample error)
    2. Robustness to noise
    3. Comparison of standard vs PHAT
    """
    print("=" * 70)
    print("Sub-sample GCC Validation (April 14 Challenge)")
    print("=" * 70)
    
    fs = 10000  # 10 kHz sample rate
    f0, f1 = 50, 200  # Chirp frequency range (shear wave frequencies)
    
    # Test 1: Sub-sample precision (no noise)
    print("\n--- Test 1: Sub-sample Precision (No Noise) ---")
    print("Target: < 0.1 sample error for all delays")
    
    test_delays = [0.0, 0.5, 1.0, 2.3, 5.7, 10.0]
    max_error_std = 0
    max_error_phat = 0
    
    for true_delay in test_delays:
        sig1, sig2, _ = generate_test_signal(
            fs=fs, f0=f0, f1=f1, delay_samples=true_delay, noise_std=0.0
        )
        
        # Standard GCC
        est_std, _ = gcc_standard(sig1, sig2, fs)
        err_std = abs(est_std * fs - true_delay)
        max_error_std = max(max_error_std, err_std)
        
        # GCC-PHAT (band-limited)
        est_phat, _ = gcc_phat(sig1, sig2, fs, freq_range=(f0, f1))
        err_phat = abs(est_phat * fs - true_delay)
        max_error_phat = max(max_error_phat, err_phat)
        
        status = "✓" if err_std < 0.1 else "✗"
        print(f"  Delay: {true_delay:5.2f} samples | "
              f"Standard: {est_std*fs:8.4f} (err={err_std:.4f}) {status} | "
              f"PHAT: {est_phat*fs:8.4f} (err={err_phat:.4f})")
    
    print(f"\n  Max error (Standard GCC): {max_error_std:.4f} samples")
    print(f"  Max error (GCC-PHAT):   {max_error_phat:.4f} samples")
    print(f"  Sub-sample target (<0.1): {'PASS ✓' if max(max_error_std, max_error_phat) < 0.1 else 'FAIL ✗'}")
    
    # Test 2: Noise robustness
    print("\n--- Test 2: Noise Robustness (delay = 2.3 samples) ---")
    true_delay = 2.3
    snr_levels = [20, 10, 5, 0, -5]
    noise_results = []
    
    for snr_db in snr_levels:
        # Calculate noise level for desired SNR
        sig_clean, _, _ = generate_test_signal(
            fs=fs, delay_samples=true_delay, noise_std=0.0
        )
        signal_power = np.mean(sig_clean**2)
        noise_var = signal_power / (10**(snr_db/10))
        noise_std = np.sqrt(noise_var)
        
        errors_std = []
        errors_phat = []
        
        # Monte Carlo trials
        for _ in range(20):
            sig1, sig2, _ = generate_test_signal(
                fs=fs, delay_samples=true_delay, noise_std=noise_std
            )
            
            est_std, _ = gcc_standard(sig1, sig2, fs)
            est_phat, _ = gcc_phat(sig1, sig2, fs, freq_range=(f0, f1))
            
            errors_std.append(abs(est_std * fs - true_delay))
            errors_phat.append(abs(est_phat * fs - true_delay))
        
        noise_results.append({
            'snr': snr_db,
            'mean_std': np.mean(errors_std),
            'max_std': np.max(errors_std),
            'mean_phat': np.mean(errors_phat),
            'max_phat': np.max(errors_phat)
        })
        
        print(f"  SNR = {snr_db:3d} dB:")
        print(f"    Standard GCC: mean={np.mean(errors_std):.4f}, max={np.max(errors_std):.4f}")
        print(f"    GCC-PHAT:     mean={np.mean(errors_phat):.4f}, max={np.max(errors_phat):.4f}")
    
    return noise_results


def plot_results(noise_results, filename='gcc_accuracy.png'):
    """Generate accuracy vs SNR plot."""
    snr = [r['snr'] for r in noise_results]
    max_std = [r['max_std'] for r in noise_results]
    max_phat = [r['max_phat'] for r in noise_results]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.semilogy(snr, max_std, 'o-', linewidth=2, markersize=8, label='Standard GCC (max error)')
    ax.semilogy(snr, max_phat, 's--', linewidth=2, markersize=6, label='GCC-PHAT (max error)', alpha=0.7)
    ax.axhline(y=0.1, color='green', linestyle=':', linewidth=2, label='Target: 0.1 samples')
    
    ax.set_xlabel('SNR (dB)', fontsize=12)
    ax.set_ylabel('Sample-Delay Error', fontsize=12)
    ax.set_title('Sub-sample GCC: Accuracy vs SNR', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"\nPlot saved: {filename}")


if __name__ == '__main__':
    results = validate_subsample_gcc()
    plot_results(results)
    print("\n" + "=" * 70)
    print("Validation complete! Module ready for integration.")
    print("=" * 70)
