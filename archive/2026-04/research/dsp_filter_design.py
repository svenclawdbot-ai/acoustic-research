"""
Digital Filter Design for Ultrasonic NDE
TurboQuant V5 - DSP Chain

ADC: 125 MS/s, ultrasound band-limited ~1-10MHz
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.fft import fft, fftshift, ifft

# =============================================================================
# CONFIGURATION
# =============================================================================
FS = 125e6          # ADC sampling rate (Hz)
NYQUIST = FS / 2    # 62.5 MHz
FC = 5e6            # Centre frequency (Hz)
PULSE_CYCLES = 1    # Tone burst cycles
NOISE_SNR_DB = 20   # Signal-to-noise ratio (dB)

# Time vector for one acquisition window
ACQ_TIME = 100e-6   # 100 microseconds
N_SAMPLES = int(FS * ACQ_TIME)
t = np.arange(N_SAMPLES) / FS

# =============================================================================
# 1. ANTI-ALIASING LOW-PASS FILTER DESIGN
# =============================================================================

def design_anti_aliasing_filter(method='fir'):
    """
    Design anti-aliasing filter for 125 MS/s ADC.
    
    Specifications:
    - Passband: 0 - 10 MHz (ripple < 0.5 dB)
    - Stopband: > 62.5 MHz (attenuation > 60 dB)
    
    Parameters:
        method: 'fir' or 'iir'
    
    Returns:
        b, a: filter coefficients
        filter_info: dict with metadata
    """
    fp = 10e6      # Passband edge
    fs = 62.5e6    # Stopband edge (Nyquist)
    
    # Normalised frequencies (0 to 1, where 1 = Nyquist)
    wp = fp / NYQUIST
    ws = fs / NYQUIST
    
    filter_info = {
        'type': 'anti-aliasing',
        'method': method,
        'fp': fp,
        'fs': fs,
        'wp': wp,
        'ws': ws
    }
    
    if method == 'fir':
        # FIR design using Kaiser window
        # Estimate filter order using firwin2 or remez
        # For 60 dB attenuation, need ~0.22 * FS / transition_width taps
        transition_width = (fs - fp) / NYQUIST
        
        # Kaiser window parameter for 60 dB attenuation
        beta = signal.kaiser_beta(60)  # ~5.65
        
        # Estimate order: N ≈ (A - 8) / (2.285 * Δω) where Δω is normalised transition width
        # More practical: use firwin with width specification
        width = (fs - fp) / NYQUIST
        N, beta = signal.kaiserord(ripple=60, width=width)
        
        # Ensure odd length for linear phase Type I FIR
        if N % 2 == 0:
            N += 1
        
        b = signal.firwin(
            numtaps=N,
            cutoff=fp,
            window=('kaiser', beta),
            fs=FS,
            pass_zero=True  # Lowpass
        )
        a = 1.0
        
        filter_info.update({
            'order': N,
            'beta': beta,
            'group_delay': (N - 1) / 2 / FS * 1e6,  # microseconds
            'linear_phase': True
        })
        
    elif method == 'iir':
        # IIR Butterworth design
        # Much lower order but non-linear phase
        wp_norm = fp / NYQUIST  # Normalised to Nyquist
        ws_norm = 0.99          # Close to Nyquist for stopband
        
        # Design Butterworth filter
        N_butt, Wn = signal.buttord(
            wp=wp_norm,
            ws=ws_norm,
            gpass=0.5,   # Passband ripple (dB)
            gstop=60,    # Stopband attenuation (dB)
            fs=FS
        )
        
        b, a = signal.butter(
            N=N_butt,
            Wn=Wn,
            btype='low',
            fs=FS
        )
        
        filter_info.update({
            'order': N_butt,
            'group_delay': 'frequency-dependent (non-linear phase)',
            'linear_phase': False
        })
    
    return b, a, filter_info


def plot_filter_response(b, a, fs, title, filter_info):
    """Plot magnitude response, phase, and group delay."""
    fig, axes = plt.subplots(3, 1, figsize=(10, 8))
    
    # Frequency response
    w, h = signal.freqz(b, a, worN=8192, fs=fs)
    
    # Magnitude (dB)
    ax1 = axes[0]
    ax1.plot(w / 1e6, 20 * np.log10(np.abs(h) + 1e-10))
    ax1.axvline(x=10, color='g', linestyle='--', label='Passband edge (10 MHz)')
    ax1.axvline(x=62.5, color='r', linestyle='--', label='Nyquist (62.5 MHz)')
    ax1.axhline(y=-0.5, color='g', linestyle=':', alpha=0.7)
    ax1.axhline(y=-60, color='r', linestyle=':', alpha=0.7)
    ax1.set_ylabel('Magnitude (dB)')
    ax1.set_title(f'{title}\n{filter_info}')
    ax1.set_ylim([-100, 5])
    ax1.legend()
    ax1.grid(True)
    
    # Phase
    ax2 = axes[1]
    phase = np.unwrap(np.angle(h))
    ax2.plot(w / 1e6, phase)
    ax2.set_ylabel('Phase (rad)')
    ax2.set_title('Phase Response')
    ax2.grid(True)
    
    # Group delay
    ax3 = axes[2]
    if filter_info.get('linear_phase', False):
        # Constant group delay for linear phase FIR
        gd = np.full_like(w, filter_info['group_delay'])
        ax3.plot(w / 1e6, gd)
        ax3.set_ylabel('Group Delay (µs)')
    else:
        # Compute group delay for IIR
        w_gd, gd = signal.group_delay((b, a), fs=fs)
        ax3.plot(w_gd / 1e6, gd / fs * 1e6)
        ax3.set_ylabel('Group Delay (µs)')
    
    ax3.set_xlabel('Frequency (MHz)')
    ax3.set_title('Group Delay')
    ax3.grid(True)
    
    plt.tight_layout()
    return fig


# =============================================================================
# 2. BANDPASS FILTER FOR ECHO EXTRACTION
# =============================================================================

def design_bandpass_filter(method='fir'):
    """
    Design bandpass filter for NDE echo extraction.
    
    Specifications:
    - Passband: 3 - 7 MHz
    - Transition bands: 2-3 MHz and 7-8 MHz
    - Attenuation: > 40 dB in stopbands
    
    Parameters:
        method: 'fir' (window/Kaiser), 'iir' (Butterworth/Chebyshev), 'pm' (Parks-McClellan)
    
    Returns:
        b, a: filter coefficients
        filter_info: dict with metadata
    """
    f_low = 3e6      # Lower passband edge
    f_high = 7e6     # Upper passband edge
    f_stop_low = 2e6   # Lower stopband edge
    f_stop_high = 8e6  # Upper stopband edge
    
    filter_info = {
        'type': 'bandpass',
        'method': method,
        'passband': (f_low, f_high),
        'stopband': (f_stop_low, f_stop_high)
    }
    
    if method == 'fir':
        # FIR using Kaiser window
        # Transition widths
        width_low = (f_low - f_stop_low) / NYQUIST
        width_high = (f_stop_high - f_high) / NYQUIST
        width = min(width_low, width_high)
        
        N, beta = signal.kaiserord(ripple=40, width=width)
        if N % 2 == 0:
            N += 1
        
        b = signal.firwin(
            numtaps=N,
            cutoff=[f_stop_low, f_stop_high],
            window=('kaiser', beta),
            fs=FS,
            pass_zero=False  # Bandpass
        )
        a = 1.0
        
        filter_info.update({
            'order': N,
            'beta': beta,
            'group_delay': (N - 1) / 2 / FS * 1e6,
            'linear_phase': True
        })
        
    elif method == 'iir':
        # IIR Butterworth bandpass
        wp = [f_low / NYQUIST, f_high / NYQUIST]
        ws = [f_stop_low / NYQUIST, f_stop_high / NYQUIST]
        
        N_butt, Wn = signal.buttord(
            wp=wp,
            ws=ws,
            gpass=1.0,   # Slightly more ripple allowed for bandpass
            gstop=40,
            fs=FS
        )
        
        b, a = signal.butter(
            N=N_butt,
            Wn=Wn,
            btype='band',
            fs=FS
        )
        
        filter_info.update({
            'order': N_butt,
            'linear_phase': False
        })
        
    elif method == 'pm':
        # Parks-McClellan (equiripple) - optimal FIR
        # Define bands: [0, f_stop_low], [f_low, f_high], [f_stop_high, NYQUIST]
        bands = [0, f_stop_low, f_low, f_high, f_stop_high, NYQUIST]
        
        # Desired response: 0 in stopbands, 1 in passband
        # Weight: higher in stopbands for better attenuation
        desired = [0, 1, 0]
        
        # Estimate order (trial and error, or use remezord)
        # For 40 dB attenuation and ~1 MHz transition:
        N_est = int(3.3 * FS / min(f_low - f_stop_low, f_stop_high - f_high))
        
        # Parks-McClellan design
        b = signal.remez(
            numtaps=N_est,
            bands=bands,
            desired=desired,
            fs=FS,
            maxiter=100
        )
        a = 1.0
        
        filter_info.update({
            'order': N_est,
            'group_delay': (N_est - 1) / 2 / FS * 1e6,
            'linear_phase': True
        })
    
    return b, a, filter_info


# =============================================================================
# 3. MATCHED FILTER FOR PULSE COMPRESSION
# =============================================================================

def generate_tone_burst(fc, cycles, fs, amplitude=1.0):
    """
    Generate a tone burst pulse.
    
    Parameters:
        fc: Centre frequency (Hz)
        cycles: Number of cycles
        fs: Sampling rate (Hz)
        amplitude: Peak amplitude
    
    Returns:
        pulse: tone burst signal
        t_pulse: time vector for pulse
    """
    duration = cycles / fc
    n_samples = int(fs * duration)
    t_pulse = np.arange(n_samples) / fs
    
    # Gaussian envelope for smooth start/stop
    sigma = duration / 4
    envelope = np.exp(-0.5 * ((t_pulse - duration/2) / sigma) ** 2)
    
    pulse = amplitude * envelope * np.sin(2 * np.pi * fc * t_pulse)
    
    return pulse, t_pulse


def design_matched_filter(transmitted_pulse):
    """
    Design matched filter for pulse compression.
    
    The matched filter maximises SNR for a known signal in white noise.
    Impulse response = time-reversed, conjugated transmitted pulse.
    
    Parameters:
        transmitted_pulse: The known transmitted pulse
    
    Returns:
        matched_filter: filter coefficients
        filter_info: dict with metadata
    """
    # Time-reverse and conjugate
    matched_filter = np.conj(transmitted_pulse[::-1])
    
    # Normalise for unity gain at peak
    matched_filter = matched_filter / np.sum(np.abs(matched_filter) ** 2)
    
    filter_info = {
        'type': 'matched',
        'pulse_length': len(transmitted_pulse),
        'compression_ratio': len(transmitted_pulse),  # Approximate
        'theoretical_snr_gain_db': 10 * np.log10(len(transmitted_pulse))
    }
    
    return matched_filter, filter_info


def apply_matched_filter(signal_in, matched_filter):
    """
    Apply matched filter using convolution.
    
    Parameters:
        signal_in: Input signal containing echoes
        matched_filter: Matched filter coefficients
    
    Returns:
        output: Filtered signal (correlation output)
    """
    output = np.convolve(signal_in, matched_filter, mode='same')
    return output


# =============================================================================
# 4. SYNTHETIC ECHO GENERATION
# =============================================================================

def generate_synthetic_echoes(pulse, t, delays, amplitudes, noise_snr_db=20):
    """
    Generate synthetic ultrasonic signal with echoes and noise.
    
    Parameters:
        pulse: Transmitted pulse waveform
        t: Time vector
        delays: List of echo delays (seconds)
        amplitudes: List of echo amplitudes (relative to transmit)
        noise_snr_db: Signal-to-noise ratio (dB)
    
    Returns:
        signal_with_echoes: Signal with echoes and noise
        clean_echoes: Echoes without noise (for comparison)
    """
    n_samples = len(t)
    clean_echoes = np.zeros(n_samples)
    
    # Add echoes at specified delays
    for delay, amp in zip(delays, amplitudes):
        delay_samples = int(delay * FS)
        if delay_samples + len(pulse) < n_samples:
            clean_echoes[delay_samples:delay_samples + len(pulse)] += amp * pulse
    
    # Calculate signal power for SNR
    signal_power = np.mean(clean_echoes ** 2)
    noise_power = signal_power / (10 ** (noise_snr_db / 10))
    
    # Generate white noise
    noise = np.sqrt(noise_power) * np.random.randn(n_samples)
    
    signal_with_echoes = clean_echoes + noise
    
    return signal_with_echoes, clean_echoes, noise


def measure_snr(signal_in, signal_clean, noise_only=None):
    """
    Measure SNR in dB.
    
    Parameters:
        signal_in: Signal with or without noise
        signal_clean: Clean signal (reference)
        noise_only: Noise component (optional)
    
    Returns:
        snr_db: Signal-to-noise ratio in dB
    """
    if noise_only is not None:
        signal_power = np.mean(signal_clean ** 2)
        noise_power = np.mean(noise_only ** 2)
    else:
        noise = signal_in - signal_clean
        signal_power = np.mean(signal_clean ** 2)
        noise_power = np.mean(noise ** 2)
    
    snr_db = 10 * np.log10(signal_power / noise_power)
    return snr_db


# =============================================================================
# 5. MAIN PROCESSING CHAIN
# =============================================================================

def run_dsp_chain():
    """
    Run the complete DSP chain demonstration.
    """
    print("=" * 60)
    print("TurboQuant V5 - Digital Signal Processing Chain")
    print("=" * 60)
    
    # -------------------------------------------------------------------------
    # Generate transmitted pulse
    # -------------------------------------------------------------------------
    print("\n[1] Generating 5 MHz tone burst...")
    pulse, t_pulse = generate_tone_burst(FC, PULSE_CYCLES, FS)
    print(f"    Pulse duration: {len(pulse) / FS * 1e6:.1f} µs")
    print(f"    Samples per pulse: {len(pulse)}")
    
    # -------------------------------------------------------------------------
    # Generate synthetic echoes
    # -------------------------------------------------------------------------
    print("\n[2] Generating synthetic echoes...")
    delays = [10e-6, 25e-6, 45e-6]      # Echo delays (µs)
    amplitudes = [1.0, 0.5, 0.3]         # Echo amplitudes
    
    signal_noisy, clean_echoes, noise = generate_synthetic_echoes(
        pulse, t, delays, amplitudes, NOISE_SNR_DB
    )
    
    snr_input = measure_snr(signal_noisy, clean_echoes, noise)
    print(f"    Echo delays: {[d*1e6 for d in delays]} µs")
    print(f"    Input SNR: {snr_input:.1f} dB")
    
    # -------------------------------------------------------------------------
    # Design and apply anti-aliasing filter
    # -------------------------------------------------------------------------
    print("\n[3] Designing anti-aliasing filters...")
    
    # FIR version
    b_aa_fir, a_aa_fir, info_aa_fir = design_anti_aliasing_filter(method='fir')
    print(f"    FIR: Order={info_aa_fir['order']}, "
          f"Group Delay={info_aa_fir['group_delay']:.2f} µs")
    
    # IIR version
    b_aa_iir, a_aa_iir, info_aa_iir = design_anti_aliasing_filter(method='iir')
    print(f"    IIR: Order={info_aa_iir['order']}, "
          f"Non-linear phase")
    
    # Apply FIR anti-aliasing filter
    signal_aa = signal.lfilter(b_aa_fir, a_aa_fir, signal_noisy)
    
    # -------------------------------------------------------------------------
    # Design and apply bandpass filter
    # -------------------------------------------------------------------------
    print("\n[4] Designing bandpass filters...")
    
    # FIR Kaiser window
    b_bp_fir, a_bp_fir, info_bp_fir = design_bandpass_filter(method='fir')
    print(f"    FIR (Kaiser): Order={info_bp_fir['order']}, "
          f"Group Delay={info_bp_fir['group_delay']:.2f} µs")
    
    # IIR Butterworth
    b_bp_iir, a_bp_iir, info_bp_iir = design_bandpass_filter(method='iir')
    print(f"    IIR (Butterworth): Order={info_bp_iir['order']}")
    
    # Apply FIR bandpass
    signal_bp = signal.lfilter(b_bp_fir, a_bp_fir, signal_aa)
    
    # -------------------------------------------------------------------------
    # Design and apply matched filter
    # -------------------------------------------------------------------------
    print("\n[5] Designing matched filter...")
    matched_filt, info_matched = design_matched_filter(pulse)
    print(f"    Pulse length: {info_matched['pulse_length']} samples")
    print(f"    Theoretical SNR gain: {info_matched['theoretical_snr_gain_db']:.1f} dB")
    
    # Apply matched filter
    signal_matched = apply_matched_filter(signal_bp, matched_filt)
    
    # Measure output SNR
    # For matched filter, we need to compare against expected output
    snr_output = measure_snr(signal_matched, clean_echoes)
    snr_improvement = snr_output - snr_input
    print(f"    Output SNR: {snr_output:.1f} dB")
    print(f"    SNR improvement: {snr_improvement:.1f} dB")
    
    # -------------------------------------------------------------------------
    # Plotting
    # -------------------------------------------------------------------------
    print("\n[6] Generating plots...")
    
    # Plot 1: Time domain signals
    fig1, axes = plt.subplots(4, 1, figsize=(12, 10))
    
    # Zoom to first 60 µs for visibility
    zoom_samples = int(60e-6 * FS)
    t_zoom = t[:zoom_samples] * 1e6  # Convert to µs
    
    axes[0].plot(t_zoom, signal_noisy[:zoom_samples])
    axes[0].set_title('Input Signal (with noise)')
    axes[0].set_ylabel('Amplitude')
    axes[0].grid(True)
    
    axes[1].plot(t_zoom, signal_aa[:zoom_samples])
    axes[1].set_title('After Anti-Aliasing Filter')
    axes[1].set_ylabel('Amplitude')
    axes[1].grid(True)
    
    axes[2].plot(t_zoom, signal_bp[:zoom_samples])
    axes[2].set_title('After Bandpass Filter')
    axes[2].set_ylabel('Amplitude')
    axes[2].grid(True)
    
    axes[3].plot(t_zoom, signal_matched[:zoom_samples])
    axes[3].set_title('After Matched Filter')
    axes[3].set_ylabel('Amplitude')
    axes[3].set_xlabel('Time (µs)')
    axes[3].grid(True)
    
    plt.tight_layout()
    plt.savefig('dsp_chain_time_domain.png', dpi=150)
    print("    Saved: dsp_chain_time_domain.png")
    
    # Plot 2: Filter responses
    fig2 = plot_filter_response(b_aa_fir, a_aa_fir, FS, 
                                'Anti-Aliasing Filter (FIR)', info_aa_fir)
    plt.savefig('filter_anti_aliasing.png', dpi=150)
    print("    Saved: filter_anti_aliasing.png")
    
    fig3 = plot_filter_response(b_bp_fir, a_bp_fir, FS,
                                'Bandpass Filter (FIR Kaiser)', info_bp_fir)
    plt.savefig('filter_bandpass.png', dpi=150)
    print("    Saved: filter_bandpass.png")
    
    # Plot 3: Spectra comparison
    fig4, axes = plt.subplots(2, 2, figsize=(12, 8))
    
    # Compute spectra
    f = np.fft.rfftfreq(len(t), 1/FS) / 1e6  # MHz
    
    spec_input = 20 * np.log10(np.abs(np.fft.rfft(signal_noisy)) + 1e-10)
    spec_bp = 20 * np.log10(np.abs(np.fft.rfft(signal_bp)) + 1e-10)
    spec_matched = 20 * np.log10(np.abs(np.fft.rfft(signal_matched)) + 1e-10)
    
    axes[0, 0].plot(f, spec_input)
    axes[0, 0].set_title('Input Spectrum')
    axes[0, 0].set_xlim([0, 20])
    axes[0, 0].set_ylim([-100, 0])
    axes[0, 0].grid(True)
    
    axes[0, 1].plot(f, spec_bp)
    axes[0, 1].set_title('After Bandpass Filter')
    axes[0, 1].set_xlim([0, 20])
    axes[0, 1].set_ylim([-100, 0])
    axes[0, 1].grid(True)
    
    axes[1, 0].plot(f, spec_matched)
    axes[1, 0].set_title('After Matched Filter')
    axes[1, 0].set_xlim([0, 20])
    axes[1, 0].set_ylim([-100, 0])
    axes[1, 0].set_xlabel('Frequency (MHz)')
    axes[1, 0].grid(True)
    
    # Pulse spectrum
    spec_pulse = 20 * np.log10(np.abs(np.fft.rfft(pulse, n=8192)) + 1e-10)
    f_pulse = np.fft.rfftfreq(8192, 1/FS) / 1e6
    axes[1, 1].plot(f_pulse, spec_pulse)
    axes[1, 1].set_title('Transmitted Pulse Spectrum')
    axes[1, 1].set_xlim([0, 20])
    axes[1, 1].set_ylim([-60, 0])
    axes[1, 1].set_xlabel('Frequency (MHz)')
    axes[1, 1].grid(True)
    
    plt.tight_layout()
    plt.savefig('dsp_spectra.png', dpi=150)
    print("    Saved: dsp_spectra.png")
    
    # Plot 4: Matched filter demonstration
    fig5, axes = plt.subplots(2, 1, figsize=(10, 6))
    
    # Pulse compression comparison
    axes[0].plot(t_pulse * 1e6, pulse)
    axes[0].set_title('Original Pulse')
    axes[0].set_xlabel('Time (µs)')
    axes[0].set_ylabel('Amplitude')
    axes[0].grid(True)
    
    # Show compressed pulse (autocorrelation)
    compressed = np.convolve(pulse, matched_filt, mode='same')
    t_compressed = np.arange(len(compressed)) / FS * 1e6
    axes[1].plot(t_compressed, compressed)
    axes[1].set_title('Matched Filter Output (Pulse Compression)')
    axes[1].set_xlabel('Time (µs)')
    axes[1].set_ylabel('Amplitude')
    axes[1].grid(True)
    
    plt.tight_layout()
    plt.savefig('matched_filter_compression.png', dpi=150)
    print("    Saved: matched_filter_compression.png")
    
    print("\n" + "=" * 60)
    print("DSP Chain Complete!")
    print("=" * 60)
    
    return {
        'pulse': pulse,
        'signal_noisy': signal_noisy,
        'signal_aa': signal_aa,
        'signal_bp': signal_bp,
        'signal_matched': signal_matched,
        'snr_input': snr_input,
        'snr_output': snr_output,
        'snr_improvement': snr_improvement,
        'filters': {
            'anti_aliasing': (b_aa_fir, a_aa_fir, info_aa_fir),
            'bandpass': (b_bp_fir, a_bp_fir, info_bp_fir),
            'matched': (matched_filt, 1.0, info_matched)
        }
    }


# =============================================================================
# COMPARISON: FIR vs IIR
# =============================================================================

def compare_fir_iir():
    """
    Compare FIR and IIR filter implementations for the DSP chain.
    """
    print("\n" + "=" * 60)
    print("FIR vs IIR Comparison")
    print("=" * 60)
    
    # Generate test signal
    pulse, _ = generate_tone_burst(FC, PULSE_CYCLES, FS)
    delays = [20e-6]
    amplitudes = [1.0]
    signal_noisy, clean_echoes, noise = generate_synthetic_echoes(
        pulse, t, delays, amplitudes, NOISE_SNR_DB
    )
    
    results = {}
    
    for filter_type in ['anti_aliasing', 'bandpass']:
        print(f"\n{filter_type.upper()}:")
        
        for method in ['fir', 'iir']:
            if filter_type == 'anti_aliasing':
                b, a, info = design_anti_aliasing_filter(method=method)
            else:
                b, a, info = design_bandpass_filter(method=method)
            
            filtered = signal.lfilter(b, a, signal_noisy)
            snr = measure_snr(filtered, clean_echoes, noise)
            
            results[f"{filter_type}_{method}"] = {
                'snr': snr,
                'info': info
            }
            
            print(f"  {method.upper()}: Order={info['order']}, SNR={snr:.1f} dB")
    
    return results


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # Run main DSP chain
    results = run_dsp_chain()
    
    # Run FIR vs IIR comparison
    comparison = compare_fir_iir()
    
    plt.show()
