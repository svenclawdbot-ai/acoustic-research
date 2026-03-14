#!/usr/bin/env python3
"""
Spatial Coherence Filtering for 4-Transducer Array
===================================================

Exploits array geometry to reject incoherent noise.
Uses phase coherence across receivers to identify true wave arrivals.

Integrates with:
- wavelet_denoising.py (temporal pre-processing)
- analyze_4th_transducer.py (array configuration)
- dispersion_postprocessing.py (parameter estimation)

Author: Research Project
Date: March 14, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert, correlate
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'research', 'week2'))

from wavelet_denoising import WaveletDenoiser

try:
    from shear_wave_2d_simple import ShearWave2D
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


def compute_spatial_coherence(signals, dt, distances, expected_velocity_range=(0.5, 5.0)):
    """
    Compute spatial coherence for propagating wave detection.
    
    For a true propagating wave:
    - Phase difference between receivers should be consistent with distance/velocity
    - Envelope peaks should arrive with delays matching distance/velocity
    - Cross-correlation should peak at expected time delay
    
    Parameters:
    -----------
    signals : list of arrays
        Time-domain signals from each receiver
    dt : float
        Time step
    distances : array
        Receiver distances from source
    expected_velocity_range : tuple
        (min, max) expected wave velocity in m/s
        
    Returns:
    --------
    dict with coherence metrics and expected arrivals
    """
    n_receivers = len(signals)
    n_samples = len(signals[0])
    
    # Compute analytic signals
    analytic_signals = [hilbert(sig) for sig in signals]
    envelopes = [np.abs(asig) for asig in analytic_signals]
    
    # Method 1: Cross-correlation based coherence
    # For propagating waves, R(i) and R(j) should be time-delayed versions
    cc_matrix = np.zeros((n_receivers, n_receivers))
    delay_matrix = np.zeros((n_receivers, n_receivers))
    
    for i in range(n_receivers):
        for j in range(i+1, n_receivers):
            # Cross-correlation
            cc = correlate(envelopes[i], envelopes[j], mode='full')
            cc_max_idx = np.argmax(cc)
            
            # Normalize CC peak
            cc_max = cc[cc_max_idx]
            cc_norm = cc_max / np.sqrt(np.sum(envelopes[i]**2) * np.sum(envelopes[j]**2))
            
            # Time delay at peak
            delay_samples = cc_max_idx - (len(envelopes[i]) - 1)
            delay_s = delay_samples * dt
            
            cc_matrix[i, j] = cc_norm
            cc_matrix[j, i] = cc_norm
            delay_matrix[i, j] = delay_s
            delay_matrix[j, i] = -delay_s
    
    # Method 2: Velocity consistency check
    # For true wave, delay_ij / distance_ij should be consistent
    velocity_estimates = []
    for i in range(n_receivers):
        for j in range(i+1, n_receivers):
            dist = abs(distances[j] - distances[i])
            delay = abs(delay_matrix[i, j])
            if delay > 1e-9:  # Avoid division by zero
                velocity = dist / delay
                velocity_estimates.append(velocity)
    
    velocity_consistency = 1.0
    if velocity_estimates:
        v_mean = np.mean(velocity_estimates)
        v_std = np.std(velocity_estimates)
        # High consistency = low CV (coefficient of variation)
        velocity_consistency = 1.0 / (1.0 + v_std / (v_mean + 1e-10))
    
    # Method 3: Temporal coherence - wave arrival detection
    # During wave arrival, all receivers show synchronized activity increase
    temporal_coherence = np.zeros(n_samples)
    
    # Sliding window analysis
    window_ms = 3  # 3 ms window
    window_samples = int(window_ms * 1e-3 / dt)
    
    for t in range(window_samples, n_samples - window_samples):
        # Signal activity in each receiver
        activities = []
        for sig in signals:
            var = np.var(sig[t-window_samples:t+window_samples])
            activities.append(var)
        
        # High coherence = all receivers show similar activity
        if np.sum(activities) > 1e-20:
            cv = np.std(activities) / (np.mean(activities) + 1e-10)
            temporal_coherence[t] = np.exp(-cv)  # High when activity is uniform
    
    # Overall receiver coherence from CC matrix
    receiver_coherence = np.mean(cc_matrix, axis=1)
    
    return {
        'cc_matrix': cc_matrix,
        'delay_matrix': delay_matrix,
        'receiver_coherence': receiver_coherence,
        'temporal_coherence': temporal_coherence,
        'velocity_consistency': velocity_consistency,
        'velocity_estimates': velocity_estimates,
        'envelopes': envelopes
    }


def filter_by_spatial_coherence(signals, coherence_info, threshold=0.3):
    """
    Apply spatial coherence mask to signals.
    
    Uses CC-based temporal coherence - enhances signal during wave arrival.
    """
    temporal_coherence = coherence_info['temporal_coherence']
    
    # Smooth coherence
    from scipy.ndimage import gaussian_filter1d
    coherence_smooth = gaussian_filter1d(temporal_coherence, sigma=5)
    
    # Create enhancement mask: boost during high coherence (wave arrival)
    # Scale from threshold to 1.0
    mask = np.clip((coherence_smooth - threshold) / (1 - threshold), 0.1, 1.0)
    
    # Apply to signals
    filtered_signals = []
    for sig in signals:
        filtered = sig * mask
        filtered_signals.append(filtered)
    
    return filtered_signals, mask


def coherent_sum_beamforming(signals, dt, distances, steering_velocity=1.4):
    """
    Delay-and-sum beamforming for wave direction.
    
    Focuses array on waves with specific velocity, suppressing other directions.
    """
    n_receivers = len(signals)
    n_samples = len(signals[0])
    
    # Compute delays for each receiver (relative to first)
    delays_samples = []
    for d in distances:
        delay_s = d / steering_velocity
        delay_samples = int(delay_s / dt)
        delays_samples.append(delay_samples)
    
    # Align and sum
    max_delay = max(delays_samples)
    aligned_length = n_samples - max_delay
    
    aligned_signals = []
    for sig, delay in zip(signals, delays_samples):
        aligned = sig[delay:delay+aligned_length]
        aligned_signals.append(aligned)
    
    # Coherent sum
    coherent_sum = np.sum(aligned_signals, axis=0)
    
    # Also compute incoherent sum (for comparison)
    incoherent_sum = np.sqrt(np.sum([s**2 for s in aligned_signals], axis=0))
    
    # Array gain = coherent / incoherent
    array_gain = np.abs(coherent_sum) / (incoherent_sum + 1e-10)
    
    return {
        'coherent_sum': coherent_sum,
        'incoherent_sum': incoherent_sum,
        'array_gain': array_gain,
        'aligned_signals': aligned_signals
    }


def run_spatial_filtering_demo(n_receivers=4, noise_level=0.2, 
                                impulse_noise=True, rho=1000):
    """
    Demonstrate spatial filtering with 3 or 4 transducers.
    """
    print("\n" + "="*70)
    print("SPATIAL COHERENCE FILTERING DEMO")
    print("="*70)
    print(f"Array: {n_receivers} receivers")
    print(f"Noise: {noise_level*100:.0f}% Gaussian")
    if impulse_noise:
        print(f"       + Impulse noise")
    print("="*70)
    
    # Simulation parameters
    G_prime = 2000
    eta = 0.5
    nx, ny = 300, 300
    dx = 0.0005
    
    sim = ShearWave2D(nx=nx, ny=ny, dx=dx, rho=rho,
                      G_prime=G_prime, eta=eta, pml_width=20)
    
    c_s = np.sqrt(G_prime / rho)
    print(f"\nShear velocity: {c_s:.2f} m/s")
    
    # Receiver positions: linear array starting at 5mm
    source_x, source_y = nx // 2, ny // 2
    distances_m = np.array([0.005, 0.010, 0.015, 0.020])[:n_receivers]
    
    receiver_positions = []
    for d in distances_m:
        rx = int(source_x + d/dx)
        receiver_positions.append((rx, source_y))
        print(f"  R{len(receiver_positions)}: {d*1000:.0f} mm")
    
    # Run simulation
    n_steps = 4000
    source_freq = 100
    dt = sim.dt
    
    print(f"\nRunning simulation ({n_steps} steps)...")
    
    time_signals_clean = [[] for _ in range(n_receivers)]
    
    for n in range(n_steps):
        t = n * dt
        if n < int(5 / source_freq / dt):
            sim.add_source(t, x_pos=source_x, y_pos=source_y,
                          amplitude=1e-6, f0=source_freq, source_type='tone_burst')
        sim.step()
        for i, (rx, ry) in enumerate(receiver_positions):
            time_signals_clean[i].append(sim.u[rx, ry])
    
    time_signals_clean = [np.array(sig) for sig in time_signals_clean]
    
    # Add noise
    np.random.seed(42)
    time_signals_noisy = []
    
    for sig in time_signals_clean:
        sig_noisy = sig.copy()
        
        # Gaussian noise
        if noise_level > 0:
            sig_noisy += noise_level * np.std(sig) * np.random.randn(len(sig))
        
        # Impulse noise
        if impulse_noise:
            n_impulses = int(len(sig) * 0.005)  # 0.5% samples
            idx = np.random.choice(len(sig), n_impulses, replace=False)
            sig_noisy[idx] += 2.0 * np.std(sig) * np.random.randn(n_impulses)
        
        time_signals_noisy.append(sig_noisy)
    
    # Stage 1: Wavelet denoising (temporal)
    print("\nStage 1: Wavelet denoising...")
    time_signals_wavelet = []
    for sig in time_signals_noisy:
        denoiser = WaveletDenoiser(wavelet='sym6', level=5, 
                                   threshold_factor=2.0, mode='soft')
        time_signals_wavelet.append(denoiser.denoise(sig))
    
    # Stage 2: Spatial coherence filtering
    print("\nStage 2: Spatial coherence analysis...")
    coherence_info = compute_spatial_coherence(
        time_signals_wavelet, dt, distances_m,
        expected_velocity_range=(0.5, 5.0)
    )
    
    print(f"  Velocity consistency: {coherence_info['velocity_consistency']:.3f}")
    if coherence_info['velocity_estimates']:
        print(f"  Estimated velocity: {np.mean(coherence_info['velocity_estimates']):.2f} m/s "
              f"± {np.std(coherence_info['velocity_estimates']):.2f} m/s")
    print(f"  Receiver coherence scores:")
    for i, score in enumerate(coherence_info['receiver_coherence']):
        print(f"    R{i+1}: {score:.3f}")
    
    # Apply coherence mask
    time_signals_spatial, coherence_mask = filter_by_spatial_coherence(
        time_signals_wavelet, coherence_info, threshold=0.3
    )
    
    # Stage 3: Beamforming
    print("Stage 3: Coherent beamforming...")
    beamforming = coherent_sum_beamforming(
        time_signals_spatial, dt, distances_m, 
        steering_velocity=c_s
    )
    
    # Evaluate improvement
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    
    def evaluate_signal(sig_clean, sig_processed, label):
        mse = np.mean((sig_processed - sig_clean)**2)
        corr = np.corrcoef(sig_clean, sig_processed)[0, 1]
        env_clean = np.abs(hilbert(sig_clean))
        env_proc = np.abs(hilbert(sig_processed))
        env_corr = np.corrcoef(env_clean, env_proc)[0, 1]
        return mse, corr, env_corr
    
    # Evaluate R1
    mse_noisy, corr_noisy, env_corr_noisy = evaluate_signal(
        time_signals_clean[0], time_signals_noisy[0], "Noisy"
    )
    mse_wavelet, corr_wavelet, env_corr_wavelet = evaluate_signal(
        time_signals_clean[0], time_signals_wavelet[0], "Wavelet"
    )
    mse_spatial, corr_spatial, env_corr_spatial = evaluate_signal(
        time_signals_clean[0], time_signals_spatial[0], "Spatial"
    )
    
    print(f"\nR1 Signal Quality (vs clean):")
    print(f"{'Stage':<15} {'MSE':<12} {'Signal Corr':<12} {'Envelope Corr':<12}")
    print("-" * 50)
    print(f"{'Noisy':<15} {mse_noisy:<12.6f} {corr_noisy:<12.4f} {env_corr_noisy:<12.4f}")
    print(f"{'+ Wavelet':<15} {mse_wavelet:<12.6f} {corr_wavelet:<12.4f} {env_corr_wavelet:<12.4f}")
    print(f"{'+ Spatial':<15} {mse_spatial:<12.6f} {corr_spatial:<12.4f} {env_corr_spatial:<12.4f}")
    
    # Plot results
    plot_spatial_filtering_results(
        time_signals_clean, time_signals_noisy,
        time_signals_wavelet, time_signals_spatial,
        coherence_info, coherence_mask, beamforming,
        dt, distances_m
    )
    
    plt.savefig('spatial_filtering_demo.png', dpi=150, bbox_inches='tight')
    print(f"\nSaved: spatial_filtering_demo.png")
    
    return {
        'signals_clean': time_signals_clean,
        'signals_noisy': time_signals_noisy,
        'signals_wavelet': time_signals_wavelet,
        'signals_spatial': time_signals_spatial,
        'coherence': coherence_info,
        'beamforming': beamforming
    }


def plot_spatial_filtering_results(clean, noisy, wavelet, spatial,
                                    coherence, mask, beamforming,
                                    dt, distances):
    """Plot comprehensive spatial filtering results."""
    
    fig = plt.figure(figsize=(16, 14))
    gs = fig.add_gridspec(4, 3, hspace=0.35, wspace=0.3)
    
    t_ms = np.arange(len(clean[0])) * dt * 1000
    
    # Row 0: Signal progression for R1
    stages = [
        ('Clean (Ground Truth)', clean[0], 'g'),
        ('Noisy Input', noisy[0], 'b'),
        ('+ Wavelet Denoising', wavelet[0], 'orange'),
        ('+ Spatial Filtering', spatial[0], 'r')
    ]
    
    for i, (title, sig, color) in enumerate(stages):
        ax = fig.add_subplot(gs[0, i if i < 3 else 2])
        ax.plot(t_ms, sig, color=color, linewidth=0.8, alpha=0.8)
        ax.set_xlim([30, 80])
        ax.set_xlabel('Time (ms)')
        ax.set_ylabel('Amplitude')
        ax.set_title(title, fontweight='bold')
        ax.grid(True, alpha=0.3)
        if i == 0:
            ax.set_ylabel('Displacement')
    
    # Row 1: All receivers comparison
    ax_receivers = fig.add_subplot(gs[1, :])
    
    colors = plt.cm.tab10(np.linspace(0, 1, len(clean)))
    
    for i, (sig, dist) in enumerate(zip(spatial, distances)):
        ax_receivers.plot(t_ms, sig + i*0.5, color=colors[i], 
                         linewidth=0.8, label=f'R{i+1} ({dist*1000:.0f}mm)')
    
    ax_receivers.set_xlim([30, 80])
    ax_receivers.set_xlabel('Time (ms)')
    ax_receivers.set_ylabel('Displacement (offset)')
    ax_receivers.set_title('All Receivers After Spatial Filtering', fontweight='bold')
    ax_receivers.legend(loc='upper right', ncol=4)
    ax_receivers.grid(True, alpha=0.3)
    
    # Row 2: Coherence analysis
    ax_coherence = fig.add_subplot(gs[2, 0])
    im = ax_coherence.imshow(coherence['cc_matrix'], 
                             cmap='RdYlGn', vmin=0, vmax=1,
                             aspect='equal')
    plt.colorbar(im, ax=ax_coherence, label='Coherence')
    ax_coherence.set_xlabel('Receiver')
    ax_coherence.set_ylabel('Receiver')
    ax_coherence.set_title('Spatial Coherence Matrix', fontweight='bold')
    
    # Temporal coherence
    ax_temporal = fig.add_subplot(gs[2, 1])
    ax_temporal.plot(t_ms, coherence['temporal_coherence'], 'b-', linewidth=1)
    ax_temporal.plot(t_ms, mask, 'r--', linewidth=1.5, label='Applied mask')
    ax_temporal.set_xlim([30, 80])
    ax_temporal.set_xlabel('Time (ms)')
    ax_temporal.set_ylabel('Coherence')
    ax_temporal.set_title('Temporal Coherence & Mask', fontweight='bold')
    ax_temporal.legend()
    ax_temporal.grid(True, alpha=0.3)
    
    # Beamforming result
    ax_beam = fig.add_subplot(gs[2, 2])
    t_beam = np.arange(len(beamforming['coherent_sum'])) * dt * 1000
    ax_beam.plot(t_beam, beamforming['coherent_sum'], 'g-', linewidth=1, label='Coherent sum')
    ax_beam.plot(t_beam, beamforming['incoherent_sum'], 'r--', linewidth=1, alpha=0.7, label='Incoherent sum')
    ax_beam.set_xlim([30, 80])
    ax_beam.set_xlabel('Time (ms)')
    ax_beam.set_ylabel('Amplitude')
    ax_beam.set_title('Beamformed Output', fontweight='bold')
    ax_beam.legend()
    ax_beam.grid(True, alpha=0.3)
    
    # Row 3: Envelope comparison
    ax_env = fig.add_subplot(gs[3, :])
    
    env_clean = np.abs(hilbert(clean[0]))
    env_noisy = np.abs(hilbert(noisy[0]))
    env_wavelet = np.abs(hilbert(wavelet[0]))
    env_spatial = np.abs(hilbert(spatial[0]))
    
    ax_env.plot(t_ms, env_noisy, 'b-', alpha=0.3, linewidth=0.8, label='Noisy')
    ax_env.plot(t_ms, env_clean, 'g-', linewidth=2, label='Clean (truth)')
    ax_env.plot(t_ms, env_wavelet, 'orange', linewidth=1.5, label='Wavelet')
    ax_env.plot(t_ms, env_spatial, 'r-', linewidth=1.5, label='Spatial')
    
    ax_env.set_xlim([45, 65])
    ax_env.set_xlabel('Time (ms)')
    ax_env.set_ylabel('Envelope')
    ax_env.set_title('Envelope Comparison (Zoomed)', fontweight='bold')
    ax_env.legend(loc='upper right')
    ax_env.grid(True, alpha=0.3)
    
    plt.suptitle(f'Spatial Coherence Filtering: {len(clean)}-Receiver Array',
                 fontsize=14, fontweight='bold')


if __name__ == "__main__":
    import pywt
    
    # Run with 4 receivers, high noise
    result = run_spatial_filtering_demo(
        n_receivers=4,
        noise_level=0.2,
        impulse_noise=True
    )
    
    print("\nSpatial filtering demo complete!")
