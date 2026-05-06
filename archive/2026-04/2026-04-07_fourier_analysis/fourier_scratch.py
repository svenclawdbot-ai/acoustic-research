"""
Fourier Analysis: From Scratch Implementation
Part 3.1 of 2026-04-07 Learning Challenge
"""

import numpy as np
import matplotlib.pyplot as plt


def dft_naive(x):
    """
    Compute the Discrete Fourier Transform from scratch.
    O(n²) complexity — for learning, not production!
    
    DFT formula: X[k] = Σₙ x[n]·e^(-i·2π·k·n/N)
    
    Parameters:
        x: Input signal (1D numpy array or list)
    
    Returns:
        X: Complex frequency domain representation
    """
    x = np.array(x, dtype=complex)
    N = len(x)
    X = np.zeros(N, dtype=complex)
    
    # YOUR IMPLEMENTATION HERE
    # Hint: Use nested loops over k and n
    # np.exp() with complex argument for the twiddle factor
    
    return X


def idft_naive(X):
    """
    Compute the Inverse DFT.
    
    IDFT formula: x[n] = (1/N)·Σₖ X[k]·e^(i·2π·k·n/N)
    """
    X = np.array(X, dtype=complex)
    N = len(X)
    x = np.zeros(N, dtype=complex)
    
    # YOUR IMPLEMENTATION HERE
    
    return x


def test_dft():
    """Verify your DFT against numpy's FFT"""
    # Test with simple signals
    N = 64
    n = np.arange(N)
    
    # Test 1: Delta function (impulse at n=0)
    delta = np.zeros(N)
    delta[0] = 1
    
    # Test 2: Single cosine: cos(2π·5·n/N)
    cos_signal = np.cos(2*np.pi*5*n/N)
    
    # Test 3: Sum of two sines
    mixed = np.sin(2*np.pi*3*n/N) + 0.5*np.sin(2*np.pi*10*n/N)
    
    # Compare your implementation to numpy
    print("Testing DFT implementation...")
    
    for name, signal in [("Delta", delta), ("Cosine", cos_signal), ("Mixed", mixed)]:
        yours = dft_naive(signal)
        reference = np.fft.fft(signal)
        error = np.max(np.abs(yours - reference))
        print(f"  {name}: max error = {error:.2e}")


def plot_spectrum(x, sample_rate=1.0, title="Signal Spectrum"):
    """Plot time domain signal and its frequency spectrum"""
    N = len(x)
    freqs = np.fft.fftfreq(N, d=1/sample_rate)
    X = np.fft.fft(x)  # Use numpy for plotting (your DFT for learning)
    
    fig, axes = plt.subplots(2, 1, figsize=(10, 6))
    
    # Time domain
    t = np.arange(N)/sample_rate
    axes[0].plot(t, x)
    axes[0].set_xlabel("Time")
    axes[0].set_ylabel("Amplitude")
    axes[0].set_title(f"{title} — Time Domain")
    
    # Frequency domain (magnitude)
    magnitude = np.abs(X)
    axes[1].stem(freqs[:N//2], magnitude[:N//2], basefmt=' ')
    axes[1].set_xlabel("Frequency (Hz)")
    axes[1].set_ylabel("Magnitude")
    axes[1].set_title("Frequency Domain")
    
    plt.tight_layout()
    return fig


def demonstrate_gibbs_phenomenon():
    """
    Demonstrate Gibbs phenomenon: overshoot at discontinuities
    when approximating with finite Fourier series
    """
    x = np.linspace(-np.pi, np.pi, 1000)
    
    # Square wave approximation with increasing harmonics
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    axes = axes.flatten()
    
    N_values = [5, 10, 50, 100]
    
    for ax, N in zip(axes, N_values):
        # Fourier series for square wave
        y = np.zeros_like(x)
        for n in range(1, N+1, 2):  # Odd harmonics only
            y += (4/np.pi)*(1/n)*np.sin(n*x)
        
        ax.plot(x, y, label=f'{N} harmonics')
        ax.axhline(y=1, color='r', linestyle='--', alpha=0.5, label='Target')
        ax.axhline(y=-1, color='r', linestyle='--', alpha=0.5)
        ax.set_title(f'N = {N}')
        ax.set_ylim(-1.5, 1.5)
        ax.legend()
    
    plt.suptitle("Gibbs Phenomenon: Square Wave Approximation")
    plt.tight_layout()
    return fig


if __name__ == "__main__":
    print("=" * 60)
    print("Fourier Analysis: DFT From Scratch")
    print("=" * 60)
    
    # Step 1: Implement and test your DFT
    # test_dft()  # Uncomment after implementing dft_naive()
    
    # Step 2: Analyze different signals
    N = 256
    t = np.linspace(0, 1, N, endpoint=False)
    
    signals = {
        "Square Wave": np.sign(np.sin(2*np.pi*5*t)),
        "Sawtooth": 2*(t*5 - np.floor(t*5 + 0.5)),
        "Gaussian Pulse": np.exp(-((t-0.5)**2)/1e-2),
    }
    
    for name, sig in signals.items():
        print(f"\nAnalyzing: {name}")
        fig = plot_spectrum(sig, sample_rate=N, title=name)
        fname = name.lower().replace(' ', '_')
        fig.savefig(f"/home/james/.openclaw/workspace/work/2026-04-07_fourier_analysis/spectrum_{fname}.png")
        print(f"  Saved spectrum plot")
    
    # Step 3: Gibbs phenomenon
    print("\nDemonstrating Gibbs phenomenon...")
    fig = demonstrate_gibbs_phenomenon()
    fig.savefig("/home/james/.openclaw/workspace/work/2026-04-07_fourier_analysis/gibbs_phenomenon.png")
    print("  Saved Gibbs phenomenon plot")
    
    print("\nDone! Check the output directory for plots.")
