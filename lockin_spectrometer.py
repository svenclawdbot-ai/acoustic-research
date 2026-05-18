import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Tuple, Optional
import warnings

# =============================================================================
# COMPLETE LOCK-IN AMPLIFIER FOR SOIL IMPEDANCE SPECTROSCOPY
# =============================================================================
# Simulates full measurement chain: excitation → soil → TIA → ADC → lock-in DSP

@dataclass
class SoilState:
    """Soil physical properties."""
    name: str
    vwc: float                  # volumetric water content
    sigma_bulk: float           # S/m
    rho_bulk: float             # Ohm.m
    epsilon_r: float
    cpe_Q: float                # CPE coefficient
    cpe_alpha: float            # CPE exponent

# =============================================================================
# SOIL STATE DEFINITIONS
# =============================================================================
SOIL_STATES = {
    "dry_clay": SoilState(
        name="Dry Clay", vwc=0.05, sigma_bulk=0.0003, rho_bulk=3333,
        epsilon_r=10, cpe_Q=1e-6, cpe_alpha=0.65
    ),
    "moderate_loam": SoilState(
        name="Moderate Loam", vwc=0.25, sigma_bulk=0.01, rho_bulk=100,
        epsilon_r=20, cpe_Q=3e-6, cpe_alpha=0.70
    ),
    "saturated_loam": SoilState(
        name="Saturated Loam", vwc=0.45, sigma_bulk=0.08, rho_bulk=12.5,
        epsilon_r=30, cpe_Q=8e-6, cpe_alpha=0.75
    ),
}

# Physical constants
epsilon_0 = 8.854e-12  # F/m
k_B = 1.381e-23        # Boltzmann constant
T_abs = 300            # K (27°C)

# Wenner array
a = 0.05               # 5 cm spacing
K_g = 2 * np.pi * a    # geometric factor

# =============================================================================
# SOIL IMPEDANCE MODEL (from Part 1)
# =============================================================================

def z_cpe(freq: float, Q: float, alpha: float) -> complex:
    """Constant Phase Element impedance."""
    omega = 2 * np.pi * freq
    mag = omega ** alpha
    phase_factor = np.exp(1j * alpha * np.pi / 2)
    return 1 / (Q * mag * phase_factor)

def z_soil(freq: float, soil: SoilState) -> complex:
    """Total soil impedance: bulk resistance + CPE in series."""
    R_bulk = soil.rho_bulk / K_g
    Z_cpe = z_cpe(freq, soil.cpe_Q, soil.cpe_alpha)
    return R_bulk + Z_cpe

# =============================================================================
# TRANSIIMPEDANCE AMPLIFIER (TIA) MODEL
# =============================================================================

class TIAModel:
    """
    Transimpedance amplifier for current sensing.
    Converts soil current I_soil to voltage for ADC.
    """
    def __init__(self, R_gain: float = 1000.0, bandwidth: float = 10e6,
                 input_noise: float = 2e-12, enbw_factor: float = 1.57):
        """
        Parameters:
        -----------
        R_gain : float
            Feedback resistor (Ω) — sets transimpedance gain
        bandwidth : float
            TIA bandwidth (Hz) — limits noise bandwidth
        input_noise : float
            TIA input current noise density (A/√Hz)
        enbw_factor : float
            Equivalent noise bandwidth factor (1.57 for single-pole)
        """
        self.R_gain = R_gain
        self.bandwidth = bandwidth
        self.input_noise = input_noise
        self.enbw = bandwidth * enbw_factor  # equivalent noise bandwidth
        
    def thermal_noise(self, T: float = T_abs) -> float:
        """Thermal noise voltage at output (V_rms)."""
        # 4kTR * enbw
        return np.sqrt(4 * k_B * T * self.R_gain * self.enbw)
    
    def current_noise(self) -> float:
        """TIA input current noise referred to output (V_rms)."""
        return self.input_noise * np.sqrt(self.enbw) * self.R_gain
    
    def convert(self, I_soil: np.ndarray) -> np.ndarray:
        """Convert current to voltage."""
        return I_soil * self.R_gain

# =============================================================================
# ADC MODEL
# =============================================================================

class ADCModel:
    """
    Analog-to-Digital Converter with quantization noise.
    """
    def __init__(self, fs: float, bits: int = 14, vref: float = 3.3,
                 input_range: float = 2.0):
        """
        Parameters:
        -----------
        fs : float
            Sampling rate (Hz)
        bits : int
            ADC resolution
        vref : float
            ADC reference voltage
        input_range : float
            Programmable input range (Vpp)
        """
        self.fs = fs
        self.bits = bits
        self.vref = vref
        self.input_range = input_range
        self.lsb = input_range / (2 ** bits)
        
    def quantize(self, voltage: np.ndarray, add_noise: bool = True) -> np.ndarray:
        """Quantize analog voltage to digital codes."""
        # Clip to range
        v_clipped = np.clip(voltage, -self.input_range/2, self.input_range/2)
        
        # Quantize
        codes = np.round(v_clipped / self.lsb)
        
        # Add quantization noise (uniform distribution, ±0.5 LSB)
        if add_noise:
            codes += np.random.uniform(-0.5, 0.5, size=codes.shape)
            
        return codes * self.lsb  # Return quantized voltage
    
    def quantization_noise_power(self) -> float:
        """Quantization noise power (V²)."""
        # LSB² / 12
        return (self.lsb ** 2) / 12
    
    def sqnr(self, signal_power: float) -> float:
        """Signal-to-Quantization-Noise Ratio (dB)."""
        q_noise = self.quantization_noise_power()
        return 10 * np.log10(signal_power / q_noise)

# =============================================================================
# DDS (DIRECT DIGITAL SYNTHESIS) MODEL
# =============================================================================

class DDSModel:
    """
    Direct Digital Synthesizer for excitation signal generation.
    """
    def __init__(self, fs: float, phase_bits: int = 32, amp_bits: int = 12):
        self.fs = fs
        self.phase_bits = phase_bits
        self.amp_bits = amp_bits
        self.phase_acc = 0
        
    def frequency_word(self, f_out: float) -> int:
        """Calculate phase increment for target frequency."""
        return int((f_out / self.fs) * (2 ** self.phase_bits))
    
    def frequency_resolution(self) -> float:
        """DDS frequency resolution (Hz)."""
        return self.fs / (2 ** self.phase_bits)
    
    def generate(self, f_out: float, N_samples: int,
                 amplitude: float = 1.0) -> np.ndarray:
        """Generate sinusoid using DDS."""
        ftw = self.frequency_word(f_out)
        n = np.arange(N_samples)
        phase = (ftw * n) % (2 ** self.phase_bits)
        
        # Quantized sine lookup (simulated)
        theta = 2 * np.pi * phase / (2 ** self.phase_bits)
        sine = np.sin(theta)
        
        # Amplitude quantization
        quant_levels = 2 ** self.amp_bits
        sine_quant = np.round(sine * quant_levels / 2) * 2 / quant_levels
        
        return amplitude * sine_quant

# =============================================================================
# LOCK-IN AMPLIFIER DSP
# =============================================================================

class LockInAmplifier:
    """
    Digital lock-in amplifier for coherent detection.
    
    Measures amplitude and phase of a signal at a known reference frequency
    by mixing with in-phase (I) and quadrature (Q) reference signals,
    then low-pass filtering.
    """
    def __init__(self, fs: float, f_ref: float, T_meas: float,
                 fir_taps: int = 64, window: str = 'hamming'):
        """
        Parameters:
        -----------
        fs : float
            Sampling rate (Hz)
        f_ref : float
            Reference frequency (Hz) — must be coherent with signal
        T_meas : float
            Measurement/integration time (s)
        fir_taps : int
            Number of FIR filter taps for LPF
        window : str
            Window function for FIR design
        """
        self.fs = fs
        self.f_ref = f_ref
        self.T_meas = T_meas
        self.N_meas = int(fs * T_meas)
        self.fir_taps = fir_taps
        
        # Design FIR low-pass filter
        # Cutoff: slightly above 1/T_meas for good rejection
        self.cutoff = 2.0 / T_meas
        self.fir_coeff = self._design_fir(fir_taps, self.cutoff, fs, window)
        
    def _design_fir(self, taps: int, cutoff: float, fs: float,
                    window: str) -> np.ndarray:
        """Design symmetric FIR low-pass filter using window method."""
        # Ideal sinc filter
        n = np.arange(taps)
        center = (taps - 1) / 2
        
        # Avoid division by zero at center
        h = np.sinc(2 * cutoff / fs * (n - center))
        
        # Apply window
        if window == 'hamming':
            w = 0.54 - 0.46 * np.cos(2 * np.pi * n / (taps - 1))
        elif window == 'hann':
            w = 0.5 * (1 - np.cos(2 * np.pi * n / (taps - 1)))
        elif window == 'blackman':
            w = 0.42 - 0.5 * np.cos(2 * np.pi * n / (taps - 1)) + \
                0.08 * np.cos(4 * np.pi * n / (taps - 1))
        else:
            w = np.ones(taps)
            
        h = h * w
        return h / np.sum(h)  # Normalize DC gain to 1
    
    def _fir_filter(self, x: np.ndarray) -> float:
        """Apply FIR filter and return final output (steady-state)."""
        if len(x) < self.fir_taps:
            # Not enough samples — use simple averaging
            return np.mean(x)
        
        # Use last 'taps' samples (steady-state output)
        segment = x[-self.fir_taps:]
        return np.dot(segment, self.fir_coeff)
    
    def measure(self, signal: np.ndarray, ref_phase: float = 0.0,
                method: str = 'fir') -> Tuple[float, float]:
        """
        Measure amplitude and phase using lock-in detection.
        
        Parameters:
        -----------
        signal : np.ndarray
            Measured signal
        ref_phase : float
            Phase offset of reference (rad)
        method : str
            'fir' for FIR LPF, 'avg' for simple averaging
        
        Returns:
        --------
        amplitude, phase : (float, float)
            Signal amplitude (V) and phase (rad)
        """
        N = min(len(signal), self.N_meas)
        t = np.arange(N) / self.fs
        sig = signal[:N]
        
        # Generate reference signals
        ref_I = np.cos(2 * np.pi * self.f_ref * t + ref_phase)
        ref_Q = np.sin(2 * np.pi * self.f_ref * t + ref_phase)
        
        # Mix
        mixed_I = sig * ref_I
        mixed_Q = sig * ref_Q
        
        # Low-pass filter
        if method == 'fir':
            I_out = self._fir_filter(mixed_I)
            Q_out = self._fir_filter(mixed_Q)
        else:
            I_out = np.mean(mixed_I)
            Q_out = np.mean(mixed_Q)
        
        # Extract amplitude and phase
        # For a sinusoid of amplitude A: mixed_I → A/2 * cos(φ), mixed_Q → A/2 * sin(φ)
        amplitude = 2 * np.sqrt(I_out**2 + Q_out**2)
        phase = np.arctan2(Q_out, I_out)
        
        return amplitude, phase
    
    def snr_estimate(self, signal_amp: float, noise_rms: float) -> float:
        """Estimate output SNR after lock-in filtering."""
        # Signal power after mixing: (A/2)²
        signal_power = (signal_amp / 2) ** 2
        
        # Noise power after LPF: reduced by factor ≈ fs * T_meas
        noise_bandwidth = 1 / self.T_meas  # equivalent noise bandwidth
        noise_power = noise_rms**2 * (noise_bandwidth / (self.fs / 2))
        
        if noise_power == 0:
            return np.inf
        return 10 * np.log10(signal_power / noise_power)

# =============================================================================
# COMPLETE MEASUREMENT CHAIN
# =============================================================================

class ImpedanceSpectrometer:
    """
    Complete soil impedance spectroscopy system.
    Simulates excitation → soil → TIA → ADC → lock-in → impedance calculation.
    """
    def __init__(self, fs: float = 1e6, adc_bits: int = 12,
                 tia_gain: float = 1000.0, v_exc: float = 0.1,
                 fir_taps: int = 64):
        """
        Parameters:
        -----------
        fs : float
            System sampling rate (Hz). For 1 MHz excitation, need ≥10×.
        adc_bits : int
            ADC resolution (12-bit for STM32, 14-bit for Red Pitaya)
        tia_gain : float
            Transimpedance gain (Ω)
        v_exc : float
            Excitation amplitude (V)
        fir_taps : int
            Lock-in FIR filter length
        """
        self.fs = fs
        self.v_exc = v_exc
        self.tia = TIAModel(R_gain=tia_gain, bandwidth=fs/2)
        self.adc = ADCModel(fs=fs, bits=adc_bits)
        self.dds = DDSModel(fs=fs)
        
    def measure_at_frequency(self, f_exc: float, soil: SoilState,
                           T_meas: float = None, add_noise: bool = True,
                           verbose: bool = False) -> Tuple[complex, dict]:
        """
        Measure impedance at a single frequency.
        
        Parameters:
        -----------
        f_exc : float
            Excitation frequency (Hz)
        soil : SoilState
            Soil properties
        T_meas : float
            Measurement time. If None, auto-calculated for 1% accuracy.
        add_noise : bool
            Include thermal and quantization noise
        verbose : bool
            Print debug info
        
        Returns:
        --------
        Z_measured : complex
            Measured impedance
        info : dict
            Debug information
        """
        # --- AUTO-CALCULATE MEASUREMENT TIME ---
        if T_meas is None:
            # Minimum: 10 cycles + time for 1% accuracy
            T_min_cycles = 10 / f_exc
            T_min_snr = 0.1  # 100 ms baseline for SNR
            T_meas = max(T_min_cycles, T_min_snr)
            
        N_samples = int(self.fs * T_meas)
        t = np.arange(N_samples) / self.fs
        
        # --- TRUE SOIL IMPEDANCE ---
        Z_true = z_soil(f_exc, soil)
        
        # --- EXCITATION ---
        excitation = self.v_exc * np.sin(2 * np.pi * f_exc * t)
        
        # --- SOIL RESPONSE ---
        # I = V_exc / Z, with phase shift
        I_amp = self.v_exc / np.abs(Z_true)
        I_phase = -np.angle(Z_true)  # current phase = -impedance phase
        I_soil = I_amp * np.sin(2 * np.pi * f_exc * t + I_phase)
        
        # --- TRANSIMPEDANCE AMPLIFIER ---
        v_tia = self.tia.convert(I_soil)
        
        # Add thermal noise
        noise_rms = 0
        if add_noise:
            v_thermal = self.tia.thermal_noise()
            v_current = self.tia.current_noise()
            noise_total = np.sqrt(v_thermal**2 + v_current**2)
            noise_rms = noise_total / np.sqrt(N_samples)  # per-sample
            v_tia += np.random.normal(0, noise_rms, N_samples)
        
        # --- ADC ---
        v_adc = self.adc.quantize(v_tia, add_noise=add_noise)
        
        # --- LOCK-IN AMPLIFIER ---
        lockin = LockInAmplifier(fs=self.fs, f_ref=f_exc, T_meas=T_meas,
                                 fir_taps=64)
        v_meas_amp, v_meas_phase = lockin.measure(v_adc, method='avg')
        
        # --- COMPUTE IMPEDANCE ---
        # V_meas = I_soil * R_gain
        # I_meas = V_meas / R_gain
        # Z = V_exc / I_meas = V_exc * R_gain / V_meas
        
        if v_meas_amp > 1e-12:  # avoid div by zero
            I_meas_amp = v_meas_amp / self.tia.R_gain
            Z_mag = self.v_exc / I_meas_amp
            Z_phase = -v_meas_phase  # Z phase = -I phase
            Z_measured = Z_mag * np.exp(1j * Z_phase)
        else:
            Z_measured = np.inf + 0j
            
        # --- ERROR ANALYSIS ---
        error_mag = abs(abs(Z_measured) - abs(Z_true)) / abs(Z_true) * 100
        error_phase = abs(np.angle(Z_measured, deg=True) - np.angle(Z_true, deg=True))
        
        info = {
            'Z_true': Z_true,
            'T_meas': T_meas,
            'N_samples': N_samples,
            'noise_rms': noise_rms,
            'v_tia_pp': np.ptp(v_tia),
            'v_adc_pp': np.ptp(v_adc),
            'snr_lockin': lockin.snr_estimate(v_tia.std(), noise_rms),
            'error_mag_percent': error_mag,
            'error_phase_deg': error_phase,
        }
        
        if verbose:
            print(f"  f={f_exc:.1f} Hz | Z_true={abs(Z_true):.2f}∠{np.degrees(np.angle(Z_true)):.1f}°")
            print(f"  T_meas={T_meas*1000:.1f} ms | N={N_samples}")
            print(f"  Z_meas={abs(Z_measured):.2f}∠{np.degrees(np.angle(Z_measured)):.1f}°")
            print(f"  Error: |Z|={error_mag:.2f}%, phase={error_phase:.2f}°")
            
        return Z_measured, info
    
    def sweep(self, soil: SoilState, freq_points: np.ndarray,
              T_meas_per_point: float = None,
              add_noise: bool = True) -> Tuple[np.ndarray, np.ndarray, list]:
        """
        Frequency sweep measurement.
        
        Returns:
        --------
        freqs, Z_measured, info_list
        """
        Z_meas = np.zeros(len(freq_points), dtype=complex)
        info_list = []
        
        print(f"\nSweeping {len(freq_points)} frequencies for {soil.name}...")
        for i, f in enumerate(freq_points):
            Z_meas[i], info = self.measure_at_frequency(
                f, soil, T_meas=T_meas_per_point, add_noise=add_noise
            )
            info_list.append(info)
            
        total_time = sum(info['T_meas'] for info in info_list)
        print(f"Total sweep time: {total_time:.2f} s")
        
        return freq_points, Z_meas, info_list

# =============================================================================
# DEMONSTRATION
# =============================================================================

def run_demo():
    """Run complete simulation and plot results."""
    
    print("="*70)
    print("SOIL IMPEDANCE SPECTROMETER — LOCK-IN AMPLIFIER DEMO")
    print("="*70)
    
    # --- CONFIGURATION ---
    # Option A: STM32 + AD9833 (budget, low power)
    stm32_config = {
        'fs': 1_000_000,      # 1 MSPS (STM32 H7)
        'adc_bits': 12,
        'tia_gain': 1000.0,    # 1 kΩ feedback
        'v_exc': 0.1,         # 100 mV excitation
        'fir_taps': 32,
    }
    
    # Option B: Red Pitaya (high performance, overkill)
    redpitaya_config = {
        'fs': 125_000_000,    # 125 MSPS
        'adc_bits': 14,
        'tia_gain': 1000.0,
        'v_exc': 0.1,
        'fir_taps': 64,
    }
    
    # Use STM32 config for demo (practical for Phase 1)
    config = stm32_config
    
    spec = ImpedanceSpectrometer(**config)
    
    print(f"\nHardware Configuration:")
    print(f"  Sampling rate: {config['fs']/1e6:.1f} MSPS")
    print(f"  ADC resolution: {config['adc_bits']}-bit")
    print(f"  TIA gain: {config['tia_gain']:.0f} Ω")
    print(f"  Excitation: {config['v_exc']*1000:.0f} mV")
    
    # --- SINGLE FREQUENCY DETAIL (1 kHz) ---
    print(f"\n{'─'*70}")
    print("SINGLE FREQUENCY MEASUREMENT (1 kHz, Moderate Loam)")
    print(f"{'─'*70}")
    
    soil = SOIL_STATES["moderate_loam"]
    Z_meas, info = spec.measure_at_frequency(
        f_exc=1000.0, soil=soil, T_meas=0.5, add_noise=True, verbose=True
    )
    
    # --- FREQUENCY SWEEP ---
    freq_points = np.logspace(0, 6, 50)  # 1 Hz to 1 MHz, 50 points
    
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    fig.suptitle(f"Lock-in Impedance Spectroscopy | {config['fs']/1e6:.1f} MSPS, "
                 f"{config['adc_bits']}-bit ADC", fontsize=11)
    
    colors = ["#8B4513", "#CD853F", "#4682B4"]
    
    for idx, (name, soil) in enumerate(SOIL_STATES.items()):
        freqs, Z_meas, info_list = spec.sweep(soil, freq_points, add_noise=True)
        Z_true = np.array([z_soil(f, soil) for f in freqs])
        
        # Plot 1: |Z| comparison
        ax = axes[0, 0]
        ax.loglog(freqs, np.abs(Z_true), '--', color=colors[idx], alpha=0.7, lw=1)
        ax.loglog(freqs, np.abs(Z_meas), 'o-', color=colors[idx], 
                  markersize=3, label=soil.name, lw=1.5)
        
        # Plot 2: Phase comparison
        ax = axes[0, 1]
        ax.semilogx(freqs, np.angle(Z_true, deg=True), '--', 
                    color=colors[idx], alpha=0.7, lw=1)
        ax.semilogx(freqs, np.angle(Z_meas, deg=True), 'o-',
                    color=colors[idx], markersize=3, lw=1.5)
        
        # Plot 3: Cole-Cole
        ax = axes[0, 2]
        ax.plot(np.real(Z_true), -np.imag(Z_true), '--', 
                color=colors[idx], alpha=0.7, lw=1)
        ax.plot(np.real(Z_meas), -np.imag(Z_meas), 'o-',
                color=colors[idx], markersize=3, lw=1.5, label=soil.name)
        
        # Plot 4: Relative error |Z|
        ax = axes[1, 0]
        errors_mag = [info['error_mag_percent'] for info in info_list]
        ax.semilogx(freqs, errors_mag, 'o-', color=colors[idx], 
                    markersize=3, lw=1.5, label=soil.name)
        
        # Plot 5: Phase error
        ax = axes[1, 1]
        errors_phase = [info['error_phase_deg'] for info in info_list]
        ax.semilogx(freqs, errors_phase, 'o-', color=colors[idx],
                    markersize=3, lw=1.5)
        
        # Plot 6: Measurement time per point
        ax = axes[1, 2]
        times = [info['T_meas'] * 1000 for info in info_list]  # ms
        ax.semilogx(freqs, times, 'o-', color=colors[idx],
                    markersize=3, lw=1.5)
    
    # Formatting
    axes[0, 0].set_xlabel("Frequency (Hz)")
    axes[0, 0].set_ylabel("|Z| (Ω)")
    axes[0, 0].set_title("Impedance Magnitude")
    axes[0, 0].legend(fontsize=8)
    axes[0, 0].grid(True, which='both', ls='--', alpha=0.5)
    
    axes[0, 1].set_xlabel("Frequency (Hz)")
    axes[0, 1].set_ylabel("Phase (degrees)")
    axes[0, 1].set_title("Phase Angle")
    axes[0, 1].set_ylim(-95, 5)
    axes[0, 1].grid(True, which='both', ls='--', alpha=0.5)
    
    axes[0, 2].set_xlabel("Re(Z) (Ω)")
    axes[0, 2].set_ylabel("-Im(Z) (Ω)")
    axes[0, 2].set_title("Cole-Cole Plot")
    axes[0, 2].legend(fontsize=8)
    axes[0, 2].grid(True, ls='--', alpha=0.5)
    
    axes[1, 0].set_xlabel("Frequency (Hz)")
    axes[1, 0].set_ylabel("Error (%)")
    axes[1, 0].set_title("|Z| Relative Error")
    axes[1, 0].legend(fontsize=8)
    axes[1, 0].grid(True, which='both', ls='--', alpha=0.5)
    axes[1, 0].axhline(1.0, color='green', ls='--', alpha=0.5, label='1% target')
    
    axes[1, 1].set_xlabel("Frequency (Hz)")
    axes[1, 1].set_ylabel("Error (degrees)")
    axes[1, 1].set_title("Phase Error")
    axes[1, 1].grid(True, which='both', ls='--', alpha=0.5)
    
    axes[1, 2].set_xlabel("Frequency (Hz)")
    axes[1, 2].set_ylabel("Time (ms)")
    axes[1, 2].set_title("Measurement Time per Point")
    axes[1, 2].grid(True, which='both', ls='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig("lockin_impedance_sweep.png", dpi=150, bbox_inches="tight")
    print(f"\n✓ Saved: lockin_impedance_sweep.png")
    
    # --- SUMMARY TABLE ---
    print(f"\n{'='*70}")
    print("SWEEP SUMMARY: MODERATE LOAM")
    print(f"{'='*70}")
    soil = SOIL_STATES["moderate_loam"]
    freqs, Z_meas, info_list = spec.sweep(soil, freq_points, add_noise=True)
    Z_true = [z_soil(f, soil) for f in freqs]
    
    print(f"{'Freq (Hz)':<12} {'|Z_true|':<10} {'|Z_meas|':<10} {'Err%':<8} {'Phase°':<8} {'T(ms)':<8}")
    print("-"*70)
    for i in [0, 10, 20, 30, 40, 49]:  # sample points
        f = freqs[i]
        print(f"{f:<12.1f} {abs(Z_true[i]):<10.1f} {abs(Z_meas[i]):<10.1f} "
              f"{info_list[i]['error_mag_percent']:<8.2f} "
              f"{np.angle(Z_meas[i], deg=True):<8.1f} "
              f"{info_list[i]['T_meas']*1000:<8.1f}")
    
    # --- NOISE BUDGET (Part 3 teaser) ---
    print(f"\n{'='*70}")
    print("NOISE BUDGET AT 1 kHz (Moderate Loam)")
    print(f"{'='*70}")
    
    f_test = 1000
    Z_test = z_soil(f_test, soil)
    I_test = spec.v_exc / abs(Z_test)
    V_tia = I_test * spec.tia.R_gain
    
    v_thermal = spec.tia.thermal_noise()
    v_current = spec.tia.current_noise()
    v_quant = np.sqrt(spec.adc.quantization_noise_power())
    
    print(f"Signal at TIA output:     {V_tia*1000:.3f} mV")
    print(f"TIA thermal noise (rms):  {v_thermal*1e6:.2f} µV")
    print(f"TIA current noise (rms):  {v_current*1e6:.2f} µV")
    print(f"ADC quantization (rms):     {v_quant*1e6:.2f} µV")
    print(f"Total noise (rss):          {np.sqrt(v_thermal**2 + v_current**2 + v_quant**2)*1e6:.2f} µV")
    print(f"SNR (signal/noise):         {20*np.log10(V_tia/np.sqrt(v_thermal**2 + v_current**2 + v_quant**2)):.1f} dB")
    
    # Dynamic range check
    print(f"\nADC dynamic range check:")
    print(f"  Signal: {V_tia*1000:.2f} mV pp")
    print(f"  ADC range: ±{spec.adc.input_range/2*1000:.0f} mV")
    print(f"  Utilization: {V_tia/(spec.adc.input_range/2)*100:.1f}%")
    
    # Is 12-bit sufficient?
    sqnr = spec.adc.sqnr(V_tia**2 / 2)
    print(f"\nADC SQNR (theoretical): {sqnr:.1f} dB")
    print(f"Required for 1% accuracy: ~40 dB")
    print(f"Verdict: {'✓ Sufficient' if sqnr > 40 else '✗ Insufficient'}")
    
    return spec

if __name__ == "__main__":
    spec = run_demo()
    plt.show()
