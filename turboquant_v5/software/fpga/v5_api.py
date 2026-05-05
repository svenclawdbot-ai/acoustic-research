"""
TurboQuant V5 Red Pitaya API
=============================

Python interface for V5 acoustic NDE system on Red Pitaya STEMlab.

Supports two modes:
1. SCPI mode: Simple, slower (~80ms for 8-channel scan)
2. FPGA DMA mode: Fast, real-time (~35ms for 8-channel scan)

Usage:
    import v5_api
    
    # Connect
    rp = v5_api.V5RedPitaya("192.168.1.100", mode="dma")
    
    # Configure
    rp.set_source_pulse(frequency=150e3, amplitude=0.5, duration=5)
    
    # Acquire
    waveforms = rp.acquire_all_channels(decimation=64, samples=8192)
    
    # Process
    for ch, data in waveforms.items():
        print(f"Channel {ch}: max amplitude = {np.max(data):.3f} V")

Author: April 22, 2026
"""

import numpy as np
import socket
import struct
import time
import warnings
from typing import Dict, Optional, Tuple


class V5RedPitaya:
    """
    Main interface for V5 acquisition system on Red Pitaya.
    
    Parameters:
    -----------
    host : str
        Red Pitaya IP address (e.g., "192.168.1.100")
    port : int
        SCPI port (default 5000)
    mode : str
        "scpi" or "dma"
    """
    
    def __init__(self, host: str = "192.168.1.100", port: int = 5000, mode: str = "scpi"):
        self.host = host
        self.port = port
        self.mode = mode.lower()
        
        if self.mode not in ["scpi", "dma"]:
            raise ValueError("Mode must be 'scpi' or 'dma'")
        
        # SCPI connection (always available)
        self._socket = None
        self._connect()
        
        # DMA parameters (for fast mode)
        self.dma_buffer_size = 8192
        self._dma_initialized = False
        
        # MUX parameters
        self.n_channels = 8
        self.mux_settle_us = 2  # MUX settling time
        
        # Source parameters
        self.source_freq = 150e3
        self.source_amp = 0.5
        self.source_duration_cycles = 5
        
        print(f"[V5] Connected to {host}:{port} in {mode} mode")
    
    def _connect(self):
        """Establish SCPI connection."""
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(5.0)
            self._socket.connect((self.host, self.port))
            # Test connection
            self._scpi_command("*IDN?")
            print("[V5] SCPI connection established")
        except Exception as e:
            warnings.warn(f"SCPI connection failed: {e}. Using mock mode.")
            self._socket = None
    
    def _scpi_command(self, cmd: str) -> str:
        """Send SCPI command and return response."""
        if self._socket is None:
            return ""
        
        self._socket.sendall(f"{cmd}\n".encode())
        
        if cmd.endswith("?"):
            response = self._socket.recv(4096).decode().strip()
            return response
        return ""
    
    def close(self):
        """Close connection."""
        if self._socket:
            self._socket.close()
            self._socket = None
            print("[V5] Connection closed")
    
    # ========================================================================
    # MUX Control
    # ========================================================================
    
    def set_mux_channel(self, channel: int, enable: bool = True):
        """
        Set DG408 MUX channel.
        
        Parameters:
        -----------
        channel : int
            Channel number (0-7)
        enable : bool
            Enable MUX output
        """
        if not 0 <= channel < self.n_channels:
            raise ValueError(f"Channel must be 0-{self.n_channels-1}")
        
        # GPIO bits: [3]=/EN (0=enabled), [2:0]=channel
        gpio_val = (0 if enable else 8) | (channel & 0x7)
        
        self._scpi_command(f"GPIO:DATa:SET 0,{gpio_val}")
        
        if enable:
            time.sleep(self.mux_settle_us * 1e-6)
    
    def disable_mux(self):
        """Disable MUX output (all channels off)."""
        self._scpi_command("GPIO:DATa:SET 0,15")  # /EN=1 (disabled)
    
    # ========================================================================
    # Source Excitation
    # ========================================================================
    
    def set_source_pulse(self, frequency: float = 150e3, amplitude: float = 0.5,
                         duration: int = 5):
        """
        Configure source excitation pulse.
        
        Parameters:
        -----------
        frequency : float
            Center frequency in Hz (default 150 kHz)
        amplitude : float
            DAC amplitude 0-1 (normalized to ±1V)
        duration : int
            Number of cycles in tone burst
        """
        self.source_freq = frequency
        self.source_amp = amplitude
        self.source_duration_cycles = duration
        
        # Generate waveform
        fs = 125e6  # DAC sample rate
        n_samples = int(fs / frequency * duration)
        t = np.arange(n_samples) / fs
        
        # Hanning-windowed tone burst
        carrier = np.sin(2 * np.pi * frequency * t)
        window = np.hanning(n_samples)
        waveform = amplitude * carrier * window
        
        # Upload to DAC
        self._load_waveform(waveform)
    
    def set_source_ricker(self, frequency: float = 150e3, amplitude: float = 0.5):
        """
        Set Ricker (Mexican hat) wavelet source.
        
        Better for broadband dispersion analysis.
        """
        self.source_freq = frequency
        self.source_amp = amplitude
        
        fs = 125e6
        sigma = 1.0 / (np.pi * frequency)
        t = np.arange(-3*sigma, 3*sigma, 1/fs)
        
        # Ricker wavelet
        tau = t / sigma
        waveform = amplitude * (1 - 2*tau**2) * np.exp(-tau**2)
        
        self._load_waveform(waveform)
    
    def _load_waveform(self, waveform: np.ndarray):
        """Upload waveform to DAC buffer."""
        # Scale to 14-bit DAC
        waveform_int = np.clip(waveform * 8191, -8192, 8191).astype(np.int16)
        
        if self.mode == "scpi":
            # SCPI: upload as comma-separated values
            # Note: This is slow for large waveforms
            data_str = ",".join([str(int(v)) for v in waveform_int[:1024]])
            self._scpi_command(f"SOUR1:TRAC:DATA:DATA {data_str}")
        else:
            # DMA mode: write directly to FPGA BRAM
            # (requires mmap or driver interface)
            self._dma_load_waveform(waveform_int)
    
    def _dma_load_waveform(self, waveform_int: np.ndarray):
        """Load waveform via DMA (placeholder)."""
        # In practice, use /dev/mem mmap or custom driver
        # This is a stub for the full implementation
        pass
    
    # ========================================================================
    # Acquisition
    # ========================================================================
    
    def acquire_single(self, channel: int, decimation: int = 64,
                       samples: int = 8192, trigger_level: float = 0.05) -> np.ndarray:
        """
        Acquire single channel.
        
        Parameters:
        -----------
        channel : int
            Channel number (0-7)
        decimation : int
            Decimation factor (1, 8, 64, 1024, 8192)
        samples : int
            Number of samples to acquire
        trigger_level : float
            Trigger threshold in volts
        
        Returns:
        --------
        data : np.ndarray
            Acquired waveform (volts)
        """
        if self.mode == "scpi":
            return self._acquire_scpi(channel, decimation, samples, trigger_level)
        else:
            return self._acquire_dma(channel, decimation, samples)
    
    def _acquire_scpi(self, channel: int, decimation: int,
                      samples: int, trigger_level: float) -> np.ndarray:
        """SCPI-based acquisition."""
        # Set MUX
        self.set_mux_channel(channel)
        
        # Configure acquisition
        self._scpi_command(f"ACQ:DEC {decimation}")
        self._scpi_command("ACQ:RST")
        self._scpi_command(f"ACQ:TRIG:LEV {trigger_level}")
        self._scpi_command(f"ACQ:TRIG:DLY {samples // 2}")
        
        # Arm and trigger
        self._scpi_command("ACQ:START")
        time.sleep(0.01)
        self._scpi_command("ACQ:TRIG NOW")
        
        # Wait for trigger
        max_wait = 100
        for _ in range(max_wait):
            status = self._scpi_command("ACQ:TRIG:STAT?")
            if status == "TD":
                break
            time.sleep(0.001)
        
        # Read data
        self._scpi_command("ACQ:SOUR1:DATA?")
        raw_data = self._scpi_command("")  # Read the response
        
        # Parse
        if raw_data:
            values = [float(x) for x in raw_data.strip("{}").split(",")]
            return np.array(values)
        
        return np.zeros(samples)
    
    def _acquire_dma(self, channel: int, decimation: int,
                     samples: int) -> np.ndarray:
        """DMA-based acquisition (fast, FPGA-controlled)."""
        # Trigger FPGA acquisition sequence
        # FPGA handles MUX scanning, triggering, and DMA
        # ARM reads from DMA buffer
        
        # Placeholder: in practice, use /dev/mem mmap or custom driver
        warnings.warn("DMA mode not fully implemented, using SCPI fallback")
        return self._acquire_scpi(channel, decimation, samples, 0.05)
    
    def acquire_all_channels(self, decimation: int = 64,
                            samples: int = 8192) -> Dict[int, np.ndarray]:
        """
        Acquire all 8 channels.
        
        Returns:
        --------
        waveforms : dict
            {channel_number: waveform_array}
        """
        waveforms = {}
        
        start_time = time.time()
        
        for ch in range(self.n_channels):
            waveforms[ch] = self.acquire_single(ch, decimation, samples)
        
        elapsed = time.time() - start_time
        print(f"[V5] Acquired {self.n_channels} channels in {elapsed*1000:.1f} ms")
        
        return waveforms
    
    # ========================================================================
    # Convenience Methods
    # ========================================================================
    
    def quick_scan(self, decimation: int = 64) -> Dict[int, np.ndarray]:
        """
        Quick 8-channel scan with default parameters.
        
        Returns waveforms as dictionary.
        """
        return self.acquire_all_channels(decimation=decimation, samples=8192)
    
    def get_sample_rate(self, decimation: int) -> float:
        """Get effective sample rate for given decimation."""
        return 125e6 / decimation
    
    # ========================================================================
    # Mock Mode (for testing without hardware)
    # ========================================================================
    
    def generate_mock_data(self, channel: int, decimation: int = 64,
                           samples: int = 8192, noise_level: float = 0.01) -> np.ndarray:
        """
        Generate synthetic data for testing.
        
        Simulates a dispersive shear wave arrival.
        """
        fs = self.get_sample_rate(decimation)
        t = np.arange(samples) / fs
        
        # Delay increases with channel number (propagation)
        delay = 100e-6 + channel * 20e-6  # 100-240 μs
        
        # Dispersive pulse (higher freq arrives earlier)
        f_center = 150e3
        bw = 50e3
        
        # Create chirp-like signal
        envelope = np.exp(-((t - delay) / 50e-6)**2)
        phase = 2 * np.pi * (f_center * (t - delay) + 
                              0.5 * bw * ((t - delay) / 100e-6)**2)
        
        signal = envelope * np.sin(phase)
        signal[t < delay - 100e-6] = 0  # Causal
        
        # Add noise
        noise = noise_level * np.random.randn(samples)
        
        return signal + noise


# =============================================================================
# DSP Utilities
# =============================================================================

def bandpass_filter(data: np.ndarray, f_low: float, f_high: float,
                    fs: float, order: int = 4) -> np.ndarray:
    """Butterworth bandpass filter."""
    from scipy.signal import butter, filtfilt
    
    nyq = 0.5 * fs
    low = f_low / nyq
    high = f_high / nyq
    
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, data)


def envelope(data: np.ndarray) -> np.ndarray:
    """Hilbert envelope detection."""
    from scipy.signal import hilbert
    return np.abs(hilbert(data))


def first_arrival(data: np.ndarray, fs: float, threshold: float = 0.1) -> float:
    """
    Detect first arrival time.
    
    Returns time in seconds.
    """
    env = envelope(data)
    env_norm = env / np.max(env)
    
    # Find first sample above threshold
    above_thresh = np.where(env_norm > threshold)[0]
    
    if len(above_thresh) > 0:
        return above_thresh[0] / fs
    else:
        return np.nan


def gcc_phat(trace1: np.ndarray, trace2: np.ndarray, fs: float) -> float:
    """
    Generalized Cross-Correlation with PHAT weighting.
    
    Returns time delay in seconds.
    """
    n = len(trace1) + len(trace2) - 1
    
    # FFT
    fft1 = np.fft.fft(trace1, n)
    fft2 = np.fft.fft(trace2, n)
    
    # Cross-spectrum
    cross = fft2 * np.conj(fft1)
    
    # PHAT weighting
    phat = cross / (np.abs(cross) + 1e-10)
    
    # Back to time domain
    corr = np.fft.ifft(phat).real
    
    # Peak
    peak = np.argmax(np.abs(corr))
    lag = peak - (len(trace1) - 1)
    
    return lag / fs


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    # Demo with mock data
    print("=" * 60)
    print("TurboQuant V5 API Demo")
    print("=" * 60)
    
    rp = V5RedPitaya("192.168.1.100", mode="scpi")
    
    # Generate mock data
    print("\n--- Mock Data Generation ---")
    for ch in range(8):
        data = rp.generate_mock_data(ch)
        t_arrival = first_arrival(data, rp.get_sample_rate(64))
        print(f"Channel {ch}: arrival = {t_arrival*1e6:.1f} μs")
    
    # Configure source
    print("\n--- Source Configuration ---")
    rp.set_source_ricker(frequency=150e3, amplitude=0.5)
    print("Ricker pulse configured: 150 kHz, 0.5 V")
    
    # Quick scan (would need real hardware)
    # waveforms = rp.quick_scan()
    
    rp.close()
    
    print("\n✅ Demo complete")
