"""
Smartphone IMU for Ultrasonic Wavefield Measurement
====================================================

Uses phone's built-in accelerometer/gyroscope as a single-channel receiver
for shear wave dispersion measurement.

Key advantages:
- Zero additional hardware cost
- High sampling rates (100-500 Hz typical, up to 2000 Hz on some phones)
- Built-in timestamping and data logging
- Wireless data transfer
- Everyone already has one

Challenges:
- Lower sensitivity than dedicated MEMS (ADXL355: 0.25 mg vs phone: ~1-5 mg)
- Must couple phone to phantom effectively
- Sequential sampling required (move phone to multiple positions)
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, hilbert, spectrogram
import sys
sys.path.insert(0, '/home/james/.openclaw/workspace')
sys.path.insert(0, '/home/james/.openclaw/workspace/research/week2')

from shear_wave_2d_zener import ShearWave2DZener
from zener_model import ZenerModel


class PhoneIMUReceiver:
    """
    Simulates smartphone IMU acquisition for ultrasonic measurement.
    
    Typical phone IMU specs:
    - Accelerometer: ±2g/±4g/±8g/±16g selectable
    - Resolution: ~0.06-0.5 mg (varies by phone)
    - Sampling: 100-500 Hz typical, up to 2000 Hz on gaming phones
    - Noise: 100-500 µg/√Hz
    """
    
    def __init__(self, sampling_rate=500, noise_floor=2e-4, resolution=1e-5):
        """
        Initialize phone IMU simulator.
        
        Parameters:
        -----------
        sampling_rate : int
            Hz (100-2000 Hz typical)
        noise_floor : float
            Acceleration noise in g (1e-4 g = ~1 mg)
        resolution : float
            ADC resolution in g
        """
        self.fs = sampling_rate
        self.noise_floor = noise_floor
        self.resolution = resolution
        
        # Realistic phone constraints
        self.max_g = 2.0  # ±2g typical
        self.coupling_efficiency = 0.3  # Phone-to-phantom coupling loss
        
    def acquire(self, true_signal, duration, coupling_quality='good'):
        """
        Simulate phone IMU acquisition.
        
        Parameters:
        -----------
        true_signal : callable(t)
            Ground truth acceleration function
        duration : float
            Acquisition duration (seconds)
        coupling_quality : str
            'good', 'fair', 'poor' affects signal transmission
            
        Returns:
        --------
        t : array
            Time stamps
        y : array
            Measured acceleration (with noise)
        """
        # Coupling efficiency
        coupling = {'good': 0.5, 'fair': 0.3, 'poor': 0.1}[coupling_quality]
        
        # Time vector
        n_samples = int(duration * self.fs)
        t = np.arange(n_samples) / self.fs
        
        # True signal (interpolate to phone sampling)
        signal_true = true_signal(t) * coupling
        
        # Add noise
        noise = np.random.normal(0, self.noise_floor, n_samples)
        
        # Quantize (ADC resolution)
        signal_noisy = signal_true + noise
        signal_quantized = np.round(signal_noisy / self.resolution) * self.resolution
        
        # Clip to ±2g
        signal_clipped = np.clip(signal_quantized, -self.max_g, self.max_g)
        
        return t, signal_clipped
    
    def bandpass_filter(self, y, f_low=50, f_high=250):
        """Apply bandpass filter for shear wave frequencies."""
        nyquist = self.fs / 2
        
        # Ensure cutoff frequencies are valid
        f_low = max(f_low, 10)  # Minimum 10 Hz
        f_high = min(f_high, nyquist - 10)  # Below Nyquist
        
        low = f_low / nyquist
        high = f_high / nyquist
        
        # Ensure 0 < Wn < 1
        low = max(0.01, min(0.99, low))
        high = max(0.01, min(0.99, high))
        
        if low >= high:
            # Invalid band, return original
            return y
        
        b, a = butter(4, [low, high], btype='band')
        y_filtered = filtfilt(b, a, y)
        
        return y_filtered


class SequentialSamplingProtocol:
    """
    Protocol for sequential sampling with single sensor.
    
    Move phone to N positions, record at each, build virtual array.
    """
    
    def __init__(self, phone_imu, positions, settling_time=0.5):
        """
        Initialize sequential sampling.
        
        Parameters:
        -----------
        phone_imu : PhoneIMUReceiver
            Phone IMU instance
        positions : array (n_positions,)
            Spatial positions (m) to sample
        settling_time : float
            Seconds to wait after moving (for vibrations to settle)
        """
        self.imu = phone_imu
        self.positions = positions
        self.settling_time = settling_time
        
    def run_sequence(self, source_position, wavefield_sim, duration=0.05):
        """
        Run sequential sampling at all positions.
        
        Parameters:
        -----------
        source_position : float
            Source location (m)
        wavefield_sim : ShearWave2DZener
            Wavefield simulator
        duration : float
            Record duration per position
            
        Returns:
        --------
        data : dict
            Dictionary with position keys and time series values
        metadata : dict
            Sampling info
        """
        data = {}
        
        print(f"Sequential sampling: {len(self.positions)} positions")
        print(f"  Sampling rate: {self.imu.fs} Hz")
        print(f"  Duration per position: {duration*1000:.0f} ms")
        print(f"  Estimated total time: {len(self.positions) * (duration + self.settling_time):.1f} s")
        
        for i, pos in enumerate(self.positions):
            print(f"\n  Position {i+1}/{len(self.positions)}: x={pos*100:.1f} cm")
            
            # Simulate moving phone
            print(f"    Moving sensor...")
            # In real implementation: wait for user to reposition
            
            # Extract signal at this position from simulation
            def signal_at_position(t):
                # Interpolate from wavefield simulation
                idx_x = np.argmin(np.abs(sim.x - pos))
                
                # Get time index closest to t
                dt_sim = sim.dt * 2  # We subsampled by 2
                idx_t = np.clip((t / dt_sim).astype(int), 0, 
                               vy_history.shape[1] - 1)
                
                return vy_history[idx_x, idx_t]
            
            # Acquire with phone IMU
            t, y = self.imu.acquire(signal_at_position, duration, 
                                    coupling_quality='good')
            
            # Filter
            y_filt = self.imu.bandpass_filter(y)
            
            data[pos] = {
                't': t,
                'y_raw': y,
                'y_filt': y_filt
            }
            
            print(f"    Acquired {len(t)} samples, SNR={self._estimate_snr(y, y_filt):.1f} dB")
        
        metadata = {
            'positions': self.positions,
            'sampling_rate': self.imu.fs,
            'duration': duration,
            'n_positions': len(self.positions)
        }
        
        return data, metadata
    
    def _estimate_snr(self, y_raw, y_filt):
        """Estimate SNR in dB."""
        noise = y_raw - y_filt
        signal_power = np.var(y_filt)
        noise_power = np.var(noise)
        if noise_power > 0:
            snr = 10 * np.log10(signal_power / noise_power)
        else:
            snr = 60  # Cap at 60 dB
        return snr


def single_channel_dispersion_extraction(data, zm, f_range=(50, 300)):
    """
    Extract dispersion from single-channel sequential measurements.
    
    Uses time-of-flight approach rather than k-ω (need spatial array for k-ω).
    
    Parameters:
    -----------
    data : dict
        Sequential sampling data {position: {t, y_filt}}
    zm : ZenerModel
        Zener dispersion model
    f_range : tuple
        Frequency range to analyze
        
    Returns:
    --------
    frequencies : array
        Frequencies analyzed
    phase_velocities : array
        Extracted phase velocities
    """
    print("\n[Processing] Single-channel dispersion extraction...")
    
    positions = np.array(sorted(data.keys()))
    
    # Stack all measurements into virtual array
    # Align by time (assume synchronized triggering)
    t_common = data[positions[0]]['t']
    virtual_array = np.zeros((len(positions), len(t_common)))
    
    for i, pos in enumerate(positions):
        virtual_array[i, :] = data[pos]['y_filt']
    
    # Now we have a virtual spatial array → can use k-ω!
    print(f"  Virtual array: {virtual_array.shape}")
    
    # 2D FFT for k-ω transform
    U = np.fft.fftshift(np.fft.fft2(virtual_array))
    spectrum = np.abs(U)**2
    
    # Axes
    nx, nt = virtual_array.shape
    dx = np.mean(np.diff(positions))
    dt = t_common[1] - t_common[0]
    
    k = np.fft.fftshift(np.fft.fftfreq(nx, dx)) * 2 * np.pi
    f = np.fft.fftshift(np.fft.fftfreq(nt, dt))
    
    # Keep positive frequencies
    f0 = len(f) // 2
    f_pos = f[f0:]
    spectrum_pos = spectrum[:, f0:]
    
    # Extract dispersion ridge
    from scipy.ndimage import gaussian_filter1d
    spectrum_smooth = gaussian_filter1d(spectrum_pos, sigma=1, axis=0)
    
    f_valid = f_pos[(f_pos >= f_range[0]) & (f_pos <= f_range[1])]
    c_extracted = []
    
    for freq in f_valid:
        idx = np.argmin(np.abs(f_pos - freq))
        spec_slice = spectrum_smooth[:, idx]
        
        # Find peak in positive k
        k_pos = k[k > 0]
        spec_pos = spec_slice[k > 0]
        
        if len(k_pos) == 0:
            c_extracted.append(np.nan)
            continue
        
        k_peak = k_pos[np.argmax(spec_pos)]
        c_p = 2 * np.pi * freq / k_peak
        
        if 1 < c_p < 10:
            c_extracted.append(c_p)
        else:
            c_extracted.append(np.nan)
    
    valid_mask = ~np.isnan(c_extracted)
    return f_valid[valid_mask], np.array(c_extracted)[valid_mask]


def alternative_time_frequency_method(data, positions, zm):
    """
    Alternative: Time-frequency analysis at each position.
    
    For phones with limited sampling, use instantaneous frequency tracking.
    """
    print("\n[Processing] Time-frequency dispersion extraction...")
    
    results = []
    
    for pos in sorted(data.keys()):
        y = data[pos]['y_filt']
        t = data[pos]['t']
        
        # Spectrogram
        f, t_spec, Sxx = spectrogram(y, fs=1/(t[1]-t[0]), 
                                     nperseg=256, noverlap=128)
        
        # Find peak frequency vs time
        peak_freq = []
        for i in range(Sxx.shape[1]):
            idx = np.argmax(Sxx[:, i])
            peak_freq.append(f[idx])
        
        # Arrival time for each frequency
        arrival_times = []
        frequencies = []
        
        for target_f in np.linspace(50, 300, 20):
            # Find when this frequency arrives
            close_idx = np.where(np.abs(np.array(peak_freq) - target_f) < 10)[0]
            if len(close_idx) > 0:
                arrival_t = t_spec[close_idx[0]]
                arrival_times.append(arrival_t)
                frequencies.append(target_f)
        
        results.append({
            'position': pos,
            'arrival_times': np.array(arrival_times),
            'frequencies': np.array(frequencies)
        })
    
    # Phase velocity from arrival time differences
    # c = Δx / Δt for each frequency
    # (Simplified - real implementation needs source time)
    
    return results


def run_phone_imu_demo():
    """Demonstrate phone IMU-based measurement."""
    print("=" * 70)
    print("SMARTPHONE IMU FOR ULTRASONIC MEASUREMENT")
    print("=" * 70)
    
    # 1. Simulate wavefield
    print("\n[1] Simulating shear wave propagation...")
    nx, ny = 100, 80
    dx = 0.002
    sim = ShearWave2DZener(nx, ny, dx, rho=1000,
                           G0=2000, G_inf=4000, tau_sigma=0.005)
    
    nt_steps = 600
    vy_history = []
    
    for n in range(nt_steps):
        t = n * sim.dt
        if t < 0.012:
            f_inst = 80 + (250 - 80) * (t / 0.012)
            envelope = np.exp(-(t - 0.006)**2 / (2 * 0.003**2))
            sim.add_source(t, nx//5, ny//2, amplitude=2e-5 * envelope,
                          f0=f_inst, source_type='ricker')
        sim.step()
        if n % 2 == 0:
            vy_history.append(sim.vy[:, ny//2].copy())
    
    vy_history = np.array(vy_history).T
    
    print(f"  Wavefield shape: {vy_history.shape}")
    print(f"  Peak amplitude: {np.abs(vy_history).max():.2e} g")
    
    # 2. Phone IMU acquisition
    print("\n[2] Phone IMU acquisition...")
    
    # Typical phone specs
    phone = PhoneIMUReceiver(
        sampling_rate=500,      # 500 Hz typical
        noise_floor=5e-4,       # 0.5 mg noise (pessimistic)
        resolution=1e-5         # 0.01 mg resolution
    )
    
    # Sequential sampling positions
    positions = np.linspace(0.02, 0.14, 12)  # 12 positions, 1 cm spacing
    
    protocol = SequentialSamplingProtocol(phone, positions, settling_time=0.3)
    
    # Run sequence
    # Create interpolation function for each position
    data = {}
    metadata = {
        'positions': positions,
        'sampling_rate': phone.fs,
        'duration': 0.1,
        'n_positions': len(positions)
    }
    
    duration = 0.1  # 100 ms for more samples
    
    print(f"Sequential sampling: {len(positions)} positions")
    print(f"  Sampling rate: {phone.fs} Hz")
    print(f"  Duration per position: {duration*1000:.0f} ms")
    print(f"  Estimated total time: {len(positions) * (duration + 0.3):.1f} s")
    
    for i, pos in enumerate(positions):
        print(f"\n  Position {i+1}/{len(positions)}: x={pos*100:.1f} cm")
        print(f"    Moving sensor...")
        
        # Create signal function for this position
        idx_x = np.argmin(np.abs(sim.x - pos))
        dt_sim = sim.dt * 2
        
        def make_signal(idx):
            def signal_fn(t):
                idx_t = np.clip((t / dt_sim).astype(int), 0, vy_history.shape[1] - 1)
                return vy_history[idx, idx_t]
            return signal_fn
        
        signal_fn = make_signal(idx_x)
        
        # Acquire with phone IMU
        t, y = phone.acquire(signal_fn, duration, coupling_quality='good')
        
        # Filter
        y_filt = phone.bandpass_filter(y)
        
        data[pos] = {
            't': t,
            'y_raw': y,
            'y_filt': y_filt
        }
        
        # Estimate SNR
        noise = y - y_filt
        signal_power = np.var(y_filt)
        noise_power = np.var(noise) if np.var(noise) > 0 else 1e-10
        snr = 10 * np.log10(signal_power / noise_power)
        print(f"    Acquired {len(t)} samples, SNR={snr:.1f} dB")
    
    # 3. Dispersion extraction
    print("\n[3] Dispersion extraction...")
    zm = ZenerModel(2000, 4000, 0.005)
    
    f_extracted, c_extracted = single_channel_dispersion_extraction(
        data, zm, f_range=(60, 280)
    )
    
    print(f"  Extracted {len(f_extracted)} dispersion points")
    
    # 4. Visualization
    print("\n[4] Generating visualization...")
    fig = visualize_phone_imu_results(data, positions, f_extracted, c_extracted, zm, vy_history, sim.x, sim.dt*2)
    
    plt.savefig('phone_imu_measurement.png', dpi=150)
    print("  Saved: phone_imu_measurement.png")
    
    # Summary
    print("\n" + "=" * 70)
    print("PHONE IMU MEASUREMENT SUMMARY")
    print("=" * 70)
    print(f"Hardware cost: £0 (phone already owned)")
    print(f"Sampling rate: {phone.fs} Hz")
    print(f"Positions measured: {len(positions)}")
    print(f"Total measurement time: ~{len(positions) * 0.4:.0f} seconds")
    print(f"Dispersion points extracted: {len(f_extracted)}")
    print(f"Comparison: 12 virtual receivers from 1 phone IMU")
    print("=" * 70)
    
    return data, f_extracted, c_extracted


def visualize_phone_imu_results(data, positions, f_extracted, c_extracted, zm, vy_history, x, dt):
    """Visualize phone IMU measurement results."""
    
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # Virtual array heatmap
    ax1 = fig.add_subplot(gs[0, :2])
    t = data[positions[0]]['t']
    virtual_array = np.array([data[p]['y_filt'] for p in positions])
    
    extent = [t[0]*1000, t[-1]*1000, 
              positions[0]*100, positions[-1]*100]
    
    im = ax1.imshow(virtual_array, aspect='auto', origin='lower',
                    extent=extent, cmap='RdBu_r')
    ax1.set_xlabel('Time (ms)')
    ax1.set_ylabel('Position (cm)')
    ax1.set_title('Virtual Array (12 positions, 1 phone IMU)')
    plt.colorbar(im, ax=ax1, label='Acceleration (g)')
    
    # Sample waveforms
    ax2 = fig.add_subplot(gs[0, 2])
    for i in [0, 4, 8, 11]:
        pos = positions[i]
        y = data[pos]['y_filt']
        ax2.plot(t*1000, y*1e3 + i*2, label=f'{pos*100:.0f} cm', alpha=0.7)
    ax2.set_xlabel('Time (ms)')
    ax2.set_ylabel('Position offset')
    ax2.set_title('Sample Waveforms')
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)
    
    # k-ω spectrum
    ax3 = fig.add_subplot(gs[1, :2])
    
    # Compute k-ω
    U = np.fft.fftshift(np.fft.fft2(virtual_array))
    spectrum = np.abs(U)**2
    
    dx = np.mean(np.diff(positions))
    nt = len(t)
    k = np.fft.fftshift(np.fft.fftfreq(len(positions), dx)) * 2 * np.pi
    f = np.fft.fftshift(np.fft.fftfreq(nt, dt))
    
    f0 = len(f) // 2
    k_pos = k[k >= 0]
    spec_pos = spectrum[k >= 0, f0:]
    
    spec_log = 10 * np.log10(spec_pos + 1e-10)
    vmax = np.percentile(spec_log, 99)
    vmin = vmax - 50
    
    extent_kw = [f[f0:].min(), f[f0:].max(), k_pos.min(), k_pos.max()]
    im = ax3.imshow(spec_log, aspect='auto', origin='lower',
                    extent=extent_kw, cmap='jet', vmin=vmin, vmax=vmax)
    ax3.set_xlabel('Frequency (Hz)')
    ax3.set_ylabel('k (rad/m)')
    ax3.set_title('k-ω Spectrum (from virtual array)')
    plt.colorbar(im, ax=ax3)
    
    # Dispersion comparison
    ax4 = fig.add_subplot(gs[1, 2])
    
    f_theory = np.linspace(50, 300, 100)
    c_theory = [zm.phase_velocity(2*np.pi*f) for f in f_theory]
    
    ax4.plot(f_theory, c_theory, 'k--', linewidth=2, label='Zener theory')
    ax4.plot(f_extracted, c_extracted, 'ro', markersize=6, 
            label=f'Phone IMU ({len(f_extracted)} pts)')
    
    ax4.set_xlabel('Frequency (Hz)')
    ax4.set_ylabel('Phase Velocity (m/s)')
    ax4.set_title('Dispersion Curve')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.set_ylim(1.5, 3.0)
    
    # Phone setup diagram
    ax5 = fig.add_subplot(gs[2, :])
    ax5.axis('off')
    
    setup_text = """
    SMARTPHONE IMU MEASUREMENT SETUP
    =================================
    
    Hardware:
    ---------
    • Smartphone (any modern phone with accelerometer)
    • 3D-printed coupling stand (holds phone perpendicular to surface)
    • Silicone coupling pad (acoustic impedance matching)
    • Piezo actuator (shear wave generation)
    • Optional: Magnetic base for phone positioning
    
    Procedure:
    ----------
    1. Place phone on coupling stand at position 1
    2. Trigger actuator, record 50-100 ms acceleration
    3. Move phone to position 2 (1 cm spacing)
    4. Repeat for 10-15 positions
    5. Process: Build virtual array → k-ω transform → dispersion
    
    Performance:
    ------------
    • Sampling rate: 100-500 Hz (phone dependent)
    • Sensitivity: ~0.5 mg (adequate for shear waves > 1 mg)
    • Spatial resolution: 1-2 cm (limited by positioning)
    • Total time: ~30 seconds (12 positions × 2.5s each)
    
    Advantages:
    -----------
    • Zero additional hardware cost
    • Wireless data logging
    • GPS tagging for spatial reference
    • Built-in display for real-time monitoring
    • Easy data sharing (cloud, email, etc.)
    
    Limitations:
    ------------
    • Sequential sampling (time penalty)
    • Requires good coupling (silicone pad critical)
    • Lower sensitivity than dedicated MEMS
    • Limited to < 250 Hz (Nyquist at 500 Hz sampling)
    """
    
    ax5.text(0.05, 0.5, setup_text, transform=ax5.transAxes, fontsize=10,
            verticalalignment='center', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
    
    return fig


if __name__ == "__main__":
    data, f_extracted, c_extracted = run_phone_imu_demo()
