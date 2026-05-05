#!/usr/bin/env python3
"""
Real-Time Shear Wave Elastography Pipeline
===========================================

End-to-end integration of hardware control, signal acquisition,
and parameter estimation for shear wave elastography.

Hardware → Acquisition → Dispersion Extraction → Parameter Fitting

Author: Research Project
Date: April 17, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from typing import Optional, Dict, List, Tuple, Callable
import sys
import os
import time
import json
from dataclasses import dataclass
from enum import Enum

# Import existing modules
sys.path.insert(0, os.path.dirname(__file__))
from array_control_host import ArrayControlInterface
from subsample_gcc import gcc_phat
from bayesian_dispersion import (
    kelvin_voigt_velocity, fit_frequentist, fit_bayesian_emcee,
    log_likelihood, log_prior
)


class PipelineState(Enum):
    """Pipeline execution states."""
    IDLE = "idle"
    CONNECTING = "connecting"
    ACQUIRING = "acquiring"
    PROCESSING = "processing"
    ERROR = "error"


@dataclass
class PipelineConfig:
    """Configuration for the real-time pipeline."""
    # Hardware
    port: str = '/dev/ttyUSB0'
    baud: int = 921600
    num_elements: int = 8
    element_pitch_mm: float = 0.5
    
    # Acquisition
    sample_rate: float = 20e6  # Hz (ESP32-S3 ADC max)
    samples_per_acq: int = 2048
    averages: int = 4
    
    # Excitation
    push_frequency_hz: float = 100  # Shear wave push frequency
    focus_depth_mm: float = 30
    
    # Signal processing
    freq_bands: Optional[List[Tuple[float, float]]] = None
    use_gcc_phat: bool = True
    noise_threshold: float = 0.05
    
    # Parameter estimation
    use_bayesian: bool = False  # True for MCMC (slower), False for frequentist (faster)
    rho: float = 1000  # kg/m³
    
    # Display
    update_interval_ms: int = 500
    history_length: int = 50
    
    def __post_init__(self):
        if self.freq_bands is None:
            # Default: 60-140 Hz in 10 Hz steps
            centers = np.arange(60, 141, 10)
            self.freq_bands = [(f-5, f+5) for f in centers]


class ShearWavePipeline:
    """
    Real-time shear wave elastography pipeline.
    
    Integrates hardware control, acquisition, and parameter estimation.
    """
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.state = PipelineState.IDLE
        self.interface: Optional[ArrayControlInterface] = None
        
        # Data buffers
        self.raw_data: Optional[np.ndarray] = None
        self.dispersion_history: List[Dict] = []
        self.parameter_history: List[Dict] = []
        
        # Current results
        self.current_dispersion: Optional[Dict] = None
        self.current_parameters: Optional[Dict] = None
        
        # Statistics
        self.acquisition_count = 0
        self.last_acquisition_time = 0
        
    def connect(self) -> bool:
        """Connect to ESP32 hardware."""
        self.state = PipelineState.CONNECTING
        print(f"Connecting to {self.config.port} @ {self.config.baud} baud...")
        
        self.interface = ArrayControlInterface(
            port=self.config.port,
            baud=self.config.baud
        )
        
        if not self.interface.connect():
            self.state = PipelineState.ERROR
            print("ERROR: Failed to connect to hardware")
            return False
        
        # Initialize hardware
        print("Initializing array geometry...")
        resp = self.interface.set_geometry(
            num_elements=self.config.num_elements,
            element_pitch=self.config.element_pitch_mm
        )
        
        if resp.get('status') != 'ok':
            self.state = PipelineState.ERROR
            print(f"ERROR: Failed to set geometry: {resp}")
            return False
        
        print("Connected successfully!")
        self.state = PipelineState.IDLE
        return True
    
    def disconnect(self):
        """Disconnect from hardware."""
        if self.interface:
            self.interface.disconnect()
            self.interface = None
        self.state = PipelineState.IDLE
        print("Disconnected")
    
    def acquire_frame(self) -> Optional[np.ndarray]:
        """
        Acquire a single frame from all array elements.
        
        Returns:
            Array of shape (num_elements, samples) or None on failure
        """
        if not self.interface or self.state == PipelineState.ERROR:
            return None
        
        self.state = PipelineState.ACQUIRING
        start_time = time.time()
        
        # Run acquisition with averaging
        data = self.interface.acquire(
            samples=self.config.samples_per_acq,
            num_elements=self.config.num_elements,
            focus_depth_mm=self.config.focus_depth_mm,
            averages=self.config.averages
        )
        
        if data is None:
            self.state = PipelineState.ERROR
            print("ERROR: Acquisition failed")
            return None
        
        self.raw_data = data
        self.last_acquisition_time = time.time() - start_time
        self.acquisition_count += 1
        
        self.state = PipelineState.PROCESSING
        return data
    
    def extract_dispersion(self, data: np.ndarray) -> Dict:
        """
        Extract dispersion curve from multi-channel data.
        
        Uses GCC-PHAT between receiver pairs to estimate time delays
        and compute phase velocities.
        """
        fs = self.config.sample_rate
        dt = 1.0 / fs
        
        # Compute receiver positions
        pitch_m = self.config.element_pitch_mm / 1000
        positions = np.arange(self.config.num_elements) * pitch_m
        
        freq_centers = [(b[0] + b[1]) / 2 for b in self.config.freq_bands]
        velocities = []
        uncertainties = []
        
        for f_center in freq_centers:
            pair_velocities = []
            pair_weights = []
            
            # Compare all receiver pairs
            for i in range(self.config.num_elements - 1):
                for j in range(i + 1, self.config.num_elements):
                    # Extract signals
                    s1 = data[i]
                    s2 = data[j]
                    
                    # Bandpass filter
                    from scipy.signal import butter, filtfilt, hilbert
                    nyq = fs / 2
                    low = max(0.01, (f_center - 10) / nyq)
                    high = min(0.99, (f_center + 10) / nyq)
                    
                    try:
                        b, a = butter(2, [low, high], btype='band')
                        s1_f = filtfilt(b, a, s1)
                        s2_f = filtfilt(b, a, s2)
                    except:
                        continue
                    
                    # Coarse delay from envelope
                    env1 = np.abs(hilbert(s1_f))
                    env2 = np.abs(hilbert(s2_f))
                    
                    # Find peaks
                    peak1 = np.argmax(env1)
                    peak2 = np.argmax(env2)
                    coarse_delay = (peak2 - peak1) * dt
                    
                    # Fine delay with GCC-PHAT
                    if self.config.use_gcc_phat:
                        delay_fine, corr = gcc_phat(s1_f, s2_f, fs, 
                                                    freq_range=(f_center-8, f_center+8))
                    else:
                        from subsample_gcc import gcc_standard
                        delay_fine, corr = gcc_standard(s1_f, s2_f, fs)
                    
                    # Resolve phase ambiguity
                    period = 1.0 / f_center
                    n_periods = round((delay_fine - coarse_delay) / period)
                    delay = delay_fine - n_periods * period
                    
                    distance = positions[j] - positions[i]
                    
                    if delay > 1e-9:
                        velocity = distance / delay
                        if 0.5 <= velocity <= 10:  # Reasonable shear wave range
                            pair_velocities.append(velocity)
                            pair_weights.append(abs(corr) * distance)
            
            if pair_velocities:
                # Weighted average
                weights = np.array(pair_weights)
                weights = weights / np.sum(weights)
                v_mean = np.average(pair_velocities, weights=weights)
                v_std = np.sqrt(np.average((np.array(pair_velocities) - v_mean)**2, 
                                           weights=weights))
                
                velocities.append(v_mean)
                uncertainties.append(v_std)
            else:
                velocities.append(np.nan)
                uncertainties.append(np.nan)
        
        result = {
            'frequencies': np.array(freq_centers),
            'velocities': np.array(velocities),
            'uncertainties': np.array(uncertainties),
            'valid': ~np.isnan(velocities)
        }
        
        self.current_dispersion = result
        return result
    
    def fit_parameters(self, dispersion: Dict) -> Dict:
        """
        Fit Kelvin-Voigt model to dispersion curve.
        """
        # Filter valid points
        valid = dispersion['valid']
        if np.sum(valid) < 3:
            print("WARNING: Too few valid dispersion points")
            return {'success': False, 'error': 'Insufficient data'}
        
        freq = dispersion['frequencies'][valid]
        vel = dispersion['velocities'][valid]
        unc = dispersion['uncertainties'][valid]
        
        if self.config.use_bayesian and EMCEE_AVAILABLE:
            # Bayesian fit (slower but more robust)
            try:
                result = fit_bayesian_emcee(freq, vel, unc, self.config.rho,
                                           n_walkers=16, n_steps=2000,
                                           burn_in=500, progress=False)
                result['method'] = 'bayesian'
            except Exception as e:
                print(f"Bayesian fit failed: {e}, falling back to frequentist")
                result = fit_frequentist(freq, vel, unc, self.config.rho)
                result['method'] = 'frequentist_fallback'
        else:
            # Frequentist fit (faster)
            result = fit_frequentist(freq, vel, unc, self.config.rho)
            result['method'] = 'frequentist'
        
        self.current_parameters = result
        return result
    
    def process_frame(self) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        Acquire and process a single frame.
        
        Returns:
            (dispersion_dict, parameters_dict) or (None, None) on failure
        """
        # Acquire
        data = self.acquire_frame()
        if data is None:
            return None, None
        
        # Extract dispersion
        dispersion = self.extract_dispersion(data)
        
        # Fit parameters
        parameters = self.fit_parameters(dispersion)
        
        # Store history
        self.dispersion_history.append(dispersion)
        self.parameter_history.append(parameters)
        
        if len(self.dispersion_history) > self.config.history_length:
            self.dispersion_history.pop(0)
            self.parameter_history.pop(0)
        
        self.state = PipelineState.IDLE
        return dispersion, parameters
    
    def get_statistics(self) -> Dict:
        """Get pipeline statistics."""
        if not self.parameter_history:
            return {}
        
        # Compute running statistics
        G_values = [p['G_prime'] for p in self.parameter_history if p.get('success')]
        
        return {
            'acquisition_count': self.acquisition_count,
            'last_acquisition_time_ms': self.last_acquisition_time * 1000,
            'buffer_fill': len(self.dispersion_history) / self.config.history_length,
            'G_mean': np.mean(G_values) if G_values else None,
            'G_std': np.std(G_values) if len(G_values) > 1 else None,
        }


class RealtimeVisualizer:
    """
    Real-time visualization of shear wave elastography data.
    """
    
    def __init__(self, pipeline: ShearWavePipeline):
        self.pipeline = pipeline
        self.fig = None
        self.axes = None
        self.animation = None
        
    def setup_plots(self):
        """Initialize matplotlib figures."""
        self.fig, self.axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Plot 1: Raw data (last acquisition)
        ax = self.axes[0, 0]
        ax.set_title('Raw Channel Data')
        ax.set_xlabel('Sample')
        ax.set_ylabel('Amplitude')
        ax.grid(True, alpha=0.3)
        self.raw_lines = []
        
        # Plot 2: Dispersion curve
        ax = self.axes[0, 1]
        ax.set_title('Dispersion Curve')
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Phase Velocity (m/s)')
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 6)
        self.dispersion_line, = ax.plot([], [], 'bo', markersize=6)
        self.dispersion_error = ax.errorbar([], [], yerr=[], fmt='none', 
                                           ecolor='blue', alpha=0.5)
        
        # Plot 3: Parameter history
        ax = self.axes[1, 0]
        ax.set_title('G\' History')
        ax.set_xlabel('Frame')
        ax.set_ylabel("G' (Pa)")
        ax.grid(True, alpha=0.3)
        self.G_line, = ax.plot([], [], 'g-', linewidth=2)
        
        # Plot 4: Statistics
        ax = self.axes[1, 1]
        ax.set_title('Current Estimate')
        ax.axis('off')
        self.stats_text = ax.text(0.1, 0.5, '', fontsize=12, 
                                  verticalalignment='center',
                                  transform=ax.transAxes)
        
        plt.tight_layout()
        
    def update(self, frame):
        """Update plots with new data."""
        # Process new frame
        dispersion, params = self.pipeline.process_frame()
        
        if dispersion is None or params is None:
            return []
        
        # Update raw data plot
        ax = self.axes[0, 0]
        ax.clear()
        ax.set_title('Raw Channel Data')
        ax.set_xlabel('Sample')
        ax.set_ylabel('Amplitude')
        ax.grid(True, alpha=0.3)
        if self.pipeline.raw_data is not None:
            for i, ch_data in enumerate(self.pipeline.raw_data):
                ax.plot(ch_data[:500], alpha=0.7, label=f'Ch{i}')
        
        # Update dispersion plot
        valid = dispersion['valid']
        self.dispersion_line.set_data(
            dispersion['frequencies'][valid],
            dispersion['velocities'][valid]
        )
        
        # Update G' history
        G_history = [p['G_prime'] for p in self.pipeline.parameter_history 
                     if p.get('success')]
        if G_history:
            self.G_line.set_data(range(len(G_history)), G_history)
            self.axes[1, 0].set_xlim(0, max(len(G_history), 10))
            self.axes[1, 0].set_ylim(
                min(G_history) * 0.8,
                max(G_history) * 1.2
            )
        
        # Update statistics
        stats = self.pipeline.get_statistics()
        if params.get('success'):
            text = f"""
Current Frame: {stats['acquisition_count']}
Acquisition Time: {stats['last_acquisition_time_ms']:.0f} ms

G' = {params['G_prime']:.0f} ± {params.get('G_prime_err', 0):.0f} Pa
η = {params['eta']:.3f} ± {params.get('eta_err', 0):.3f} Pa·s
R² = {params['r_squared']:.4f}

Running G' = {stats.get('G_mean', 0):.0f} ± {stats.get('G_std', 0):.0f} Pa
            """.strip()
        else:
            text = f"Fit failed: {params.get('error', 'Unknown error')}"
        
        self.stats_text.set_text(text)
        
        return [self.dispersion_line, self.G_line, self.stats_text]
    
    def run(self, duration_seconds: Optional[float] = None):
        """
        Run real-time visualization.
        
        Parameters:
            duration_seconds: Run for this many seconds (None = indefinite)
        """
        self.setup_plots()
        
        # Calculate interval in milliseconds
        interval_ms = self.pipeline.config.update_interval_ms
        
        # Create animation
        self.animation = FuncAnimation(
            self.fig, self.update,
            interval=interval_ms,
            blit=False,
            cache_frame_data=False
        )
        
        print("Starting real-time display...")
        print("Close the plot window to stop")
        
        if duration_seconds:
            plt.show(block=False)
            time.sleep(duration_seconds)
            plt.close()
        else:
            plt.show()


def run_simulation_mode(config: PipelineConfig, n_frames: int = 50):
    """
    Run pipeline in simulation mode (no hardware required).
    
    Generates synthetic shear wave data for testing.
    """
    print("="*70)
    print("SHEAR WAVE PIPELINE - SIMULATION MODE")
    print("="*70)
    print(f"True: G' = 2000 Pa, η = 0.5 Pa·s")
    print(f"Simulating {n_frames} frames...")
    print("="*70)
    
    # True parameters
    true_G = 2000
    true_eta = 0.5
    rho = 1000
    
    # Storage
    G_estimates = []
    
    for frame in range(n_frames):
        # Generate synthetic frame
        fs = config.sample_rate
        dt = 1.0 / fs
        t = np.arange(config.samples_per_acq) * dt
        
        # Create synthetic dispersive signals
        pitch_m = config.element_pitch_mm / 1000
        positions = np.arange(config.num_elements) * pitch_m
        
        freq_centers = [(b[0] + b[1]) / 2 for b in config.freq_bands]
        base_times = np.linspace(0.02, 0.08, len(freq_centers))
        
        data = []
        for d in positions:
            sig = np.zeros_like(t)
            for f_center, t_base in zip(freq_centers, base_times):
                omega = 2 * np.pi * f_center
                G_mag = np.sqrt(true_G**2 + (omega * true_eta)**2)
                c_f = np.sqrt(2 / rho) * np.sqrt(G_mag**2 / (true_G + G_mag))
                
                arrival = t_base + d / c_f
                burst_width = 0.005
                envelope = np.exp(-((t - arrival)**2) / (2 * (burst_width/3)**2))
                carrier = np.sin(omega * (t - arrival))
                sig += envelope * carrier
            
            sig = sig / (np.max(np.abs(sig)) + 1e-10)
            
            # Add 10% noise
            noise = 0.10 * np.std(sig) * np.random.randn(len(sig))
            data.append(sig + noise)
        
        data = np.array(data)
        
        # Process frame
        pipeline = ShearWavePipeline(config)
        pipeline.raw_data = data
        
        dispersion = pipeline.extract_dispersion(data)
        params = pipeline.fit_parameters(dispersion)
        
        if params.get('success'):
            G_estimates.append(params['G_prime'])
            G_err = params.get('G_prime_err', 0)
            
            if frame % 10 == 0:
                print(f"Frame {frame:3d}: G' = {params['G_prime']:.0f} ± {G_err:.0f} Pa, "
                      f"η = {params['eta']:.3f}, R² = {params['r_squared']:.3f}")
    
    # Summary
    print("\n" + "="*70)
    print("SIMULATION COMPLETE")
    print("="*70)
    
    if G_estimates:
        G_array = np.array(G_estimates)
        print(f"True G': {true_G} Pa")
        print(f"Estimated G': {np.mean(G_array):.0f} ± {np.std(G_array):.0f} Pa")
        print(f"Bias: {np.mean(G_array) - true_G:.0f} Pa")
        print(f"Error range: [{np.min(G_array):.0f}, {np.max(G_array):.0f}] Pa")
    
    return G_estimates


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Real-Time Shear Wave Elastography Pipeline'
    )
    parser.add_argument('--mode', choices=['hardware', 'simulation', 'visualization'],
                       default='simulation',
                       help='Operation mode (default: simulation)')
    parser.add_argument('--port', default='/dev/ttyUSB0',
                       help='Serial port for hardware mode')
    parser.add_argument('--frames', type=int, default=50,
                       help='Number of frames to process')
    parser.add_argument('--bayesian', action='store_true',
                       help='Use Bayesian parameter estimation (slower)')
    
    args = parser.parse_args()
    
    # Create configuration
    config = PipelineConfig(
        port=args.port,
        use_bayesian=args.bayesian
    )
    
    if args.mode == 'simulation':
        # Run simulation
        run_simulation_mode(config, args.frames)
        
    elif args.mode == 'hardware':
        # Run with real hardware
        print("Hardware mode selected")
        print("NOTE: Requires ESP32 array controller connected")
        
        pipeline = ShearWavePipeline(config)
        
        if not pipeline.connect():
            print("Failed to connect to hardware. Exiting.")
            return 1
        
        try:
            print(f"Acquiring {args.frames} frames...")
            for i in range(args.frames):
                dispersion, params = pipeline.process_frame()
                
                if params and params.get('success'):
                    print(f"Frame {i+1}/{args.frames}: "
                          f"G' = {params['G_prime']:.0f} Pa, "
                          f"R² = {params['r_squared']:.3f}")
                else:
                    print(f"Frame {i+1}/{args.frames}: Failed")
                
                time.sleep(0.1)  # Small delay between acquisitions
        finally:
            pipeline.disconnect()
            
    elif args.mode == 'visualization':
        # Run with real-time visualization
        print("Visualization mode")
        print("NOTE: Requires ESP32 array controller connected")
        
        pipeline = ShearWavePipeline(config)
        
        if not pipeline.connect():
            print("Failed to connect. Running in simulation mode instead.")
            # Fall back to simulation
            run_simulation_mode(config, args.frames)
            return 0
        
        try:
            visualizer = RealtimeVisualizer(pipeline)
            visualizer.run(duration_seconds=None)  # Run until closed
        finally:
            pipeline.disconnect()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
