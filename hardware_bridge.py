#!/usr/bin/env python3
"""
Hardware Bridge - ESP32 Array to Processing Pipeline
=====================================================

Connects ESP32-S3 ultrasound array controller to Python signal
processing pipeline. Handles acquisition, buffering, and dispatch
to dispersion extraction.

Usage:
    from hardware_bridge import ArrayHardwareBridge
    
    bridge = ArrayHardwareBridge('/dev/ttyUSB0')
    if bridge.connect():
        # Single acquisition
        data = bridge.acquire_single(frequency=100, depth_mm=30)
        dispersion = bridge.process_dispersion(data)
        
        # Or continuous monitoring
        for result in bridge.acquire_continuous():
            print(f"G' = {result['G_prime']:.0f} Pa")

Author: Research Project
Date: April 17, 2026
"""

import numpy as np
import time
import sys
import os
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import warnings

sys.path.insert(0, os.path.dirname(__file__))
from array_control_host import ArrayControlInterface
from e2e_from_demo import extract_dispersion_envelope, fit_kelvin_voigt


class AcquisitionMode(Enum):
    """Acquisition modes."""
    SINGLE = "single"
    CONTINUOUS = "continuous"
    SEQUENTIAL = "sequential"


@dataclass
class HardwareConfig:
    """Configuration for hardware acquisition."""
    # Serial
    port: str = '/dev/ttyUSB0'
    baud: int = 921600
    
    # Array geometry
    num_elements: int = 8
    element_pitch_mm: float = 0.5
    
    # Acquisition
    sample_rate: float = 20e6  # Hz (ESP32-S3 ADC max)
    samples_per_acq: int = 2048
    averages: int = 4
    
    # Excitation
    push_frequency_hz: float = 100
    focus_depth_mm: float = 30
    pulse_width_us: int = 10
    
    # Processing
    freq_bands: Optional[List[Tuple[float, float]]] = None
    rho: float = 1000  # kg/m³
    
    # Sequential mode
    sequential_frequencies: List[float] = None
    
    def __post_init__(self):
        if self.freq_bands is None:
            centers = [60, 80, 100, 120, 140]
            self.freq_bands = [(f-5, f+5) for f in centers]
        if self.sequential_frequencies is None:
            self.sequential_frequencies = [60, 80, 100, 120, 140]


class ArrayHardwareBridge:
    """
    Bridge between ESP32 hardware and Python processing pipeline.
    """
    
    def __init__(self, config: Optional[HardwareConfig] = None):
        self.config = config or HardwareConfig()
        self.interface: Optional[ArrayControlInterface] = None
        self.is_connected = False
        self.acquisition_count = 0
        
        # Statistics
        self.last_acquisition_time = 0.0
        
    def connect(self) -> bool:
        """Connect to ESP32 hardware."""
        print(f"Connecting to ESP32 at {self.config.port}...")
        
        self.interface = ArrayControlInterface(
            port=self.config.port,
            baud=self.config.baud
        )
        
        if not self.interface.connect():
            print("ERROR: Failed to connect")
            self.is_connected = False
            return False
        
        # Initialize array geometry
        resp = self.interface.set_geometry(
            num_elements=self.config.num_elements,
            element_pitch=self.config.element_pitch_mm
        )
        
        if resp.get('status') != 'ok':
            print(f"ERROR: Failed to set geometry: {resp}")
            self.interface.disconnect()
            self.is_connected = False
            return False
        
        print("Connected successfully!")
        self.is_connected = True
        return True
    
    def disconnect(self):
        """Disconnect from hardware."""
        if self.interface:
            self.interface.disconnect()
            self.interface = None
        self.is_connected = False
        print("Disconnected")
    
    def acquire_single(self, frequency: Optional[float] = None,
                       depth_mm: Optional[float] = None) -> Optional[np.ndarray]:
        """
        Acquire single frame from all array elements.
        
        Parameters:
            frequency: Push frequency (Hz), uses config default if None
            depth_mm: Focus depth (mm), uses config default if None
            
        Returns:
            Array of shape (num_elements, samples) or None on failure
        """
        if not self.is_connected or not self.interface:
            print("ERROR: Not connected to hardware")
            return None
        
        freq = frequency or self.config.push_frequency_hz
        depth = depth_mm or self.config.focus_depth_mm
        
        # Set focus
        resp = self.interface.set_focus(depth_mm=depth, angle_deg=0)
        if resp.get('status') != 'ok':
            print(f"WARNING: Failed to set focus: {resp}")
        
        # Fire all elements
        resp = self.interface.fire(
            element_mask=0xFF,  # All 8 elements
            pulse_width_us=self.config.pulse_width_us
        )
        if resp.get('status') != 'ok':
            print(f"WARNING: Fire command failed: {resp}")
        
        # Acquire data
        start_time = time.time()
        data = self.interface.acquire(
            samples=self.config.samples_per_acq,
            num_elements=self.config.num_elements,
            focus_depth_mm=depth,
            averages=self.config.averages
        )
        
        if data is None:
            print("ERROR: Acquisition failed")
            return None
        
        self.last_acquisition_time = time.time() - start_time
        self.acquisition_count += 1
        
        return data
    
    def process_dispersion(self, data: np.ndarray,
                           frequencies: Optional[List[float]] = None) -> Dict:
        """
        Process raw array data to extract dispersion and fit parameters.
        
        Parameters:
            data: Raw array data (num_elements, samples)
            frequencies: List of frequencies to analyze (Hz)
            
        Returns:
            Dictionary with dispersion curve and fitted parameters
        """
        if data is None or data.shape[0] == 0:
            return {'success': False, 'error': 'No data'}
        
        dt = 1.0 / self.config.sample_rate
        distances = np.arange(self.config.num_elements) * \
                   (self.config.element_pitch_mm / 1000)
        freqs = frequencies or [f[0] + (f[1]-f[0])/2 for f in self.config.freq_bands]
        
        # Extract dispersion using envelope method
        dispersion = extract_dispersion_envelope(data, dt, distances, freqs)
        
        if len(dispersion['velocities']) == 0:
            return {
                'success': False,
                'error': 'No dispersion points extracted',
                'raw_data': data
            }
        
        # Fit Kelvin-Voigt model
        fit = fit_kelvin_voigt(
            dispersion['frequencies'],
            dispersion['velocities'],
            dispersion['uncertainties'],
            self.config.rho
        )
        
        return {
            'success': fit.get('success', False),
            'dispersion': dispersion,
            'fit': fit,
            'raw_data': data,
            'G_prime': fit.get('G_prime'),
            'eta': fit.get('eta'),
            'r_squared': fit.get('r_squared')
        }
    
    def acquire_sequential(self, frequencies: Optional[List[float]] = None,
                          depth_mm: Optional[float] = None) -> Dict:
        """
        Sequential single-frequency acquisition.
        
        For each frequency:
        1. Configure excitation
        2. Fire elements
        3. Acquire data
        4. Extract velocity at that frequency
        
        Returns dispersion curve built from sequential measurements.
        """
        freqs = frequencies or self.config.sequential_frequencies
        depth = depth_mm or self.config.focus_depth_mm
        
        print(f"Sequential acquisition: {len(freqs)} frequencies")
        print(f"Focus depth: {depth} mm")
        
        freq_results = []
        velocity_results = []
        uncertainty_results = []
        
        for freq in freqs:
            print(f"\n  Acquiring at {freq} Hz...")
            
            # Single frequency acquisition
            data = self.acquire_single(frequency=freq, depth_mm=depth)
            
            if data is None:
                print(f"    FAILED - skipping")
                continue
            
            # Extract velocity at this frequency only
            # Use narrow band around the excitation frequency
            dt = 1.0 / self.config.sample_rate
            distances = np.arange(self.config.num_elements) * \
                       (self.config.element_pitch_mm / 1000)
            
            dispersion = extract_dispersion_envelope(
                data, dt, distances, [freq]
            )
            
            if len(dispersion['velocities']) > 0:
                v = dispersion['velocities'][0]
                u = dispersion['uncertainties'][0]
                freq_results.append(freq)
                velocity_results.append(v)
                uncertainty_results.append(u)
                print(f"    c = {v:.2f} ± {u:.2f} m/s")
            else:
                print(f"    No velocity extracted")
        
        # Build dispersion dict
        dispersion = {
            'frequencies': np.array(freq_results),
            'velocities': np.array(velocity_results),
            'uncertainties': np.array(uncertainty_results),
            'valid': np.ones(len(freq_results), dtype=bool)
        }
        
        # Fit if we have enough points
        fit = None
        if len(freq_results) >= 3:
            fit = fit_kelvin_voigt(
                dispersion['frequencies'],
                dispersion['velocities'],
                dispersion['uncertainties'],
                self.config.rho
            )
        
        return {
            'success': len(freq_results) >= 3 and (fit is not None and fit.get('success')),
            'dispersion': dispersion,
            'fit': fit,
            'frequencies_acquired': freq_results
        }
    
    def acquire_continuous(self, callback: Optional[Callable] = None,
                          interval_ms: int = 500) -> Dict:
        """
        Continuous acquisition loop.
        
        Parameters:
            callback: Function called with each result dict
            interval_ms: Time between acquisitions
            
        Yields:
            Result dictionaries with dispersion and fit
        """
        print(f"Starting continuous acquisition (interval: {interval_ms} ms)")
        
        try:
            while True:
                start_time = time.time()
                
                # Acquire and process
                data = self.acquire_single()
                if data is not None:
                    result = self.process_dispersion(data)
                    
                    if callback:
                        callback(result)
                    
                    yield result
                
                # Maintain interval
                elapsed = (time.time() - start_time) * 1000
                sleep_time = max(0, (interval_ms - elapsed) / 1000)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
        except KeyboardInterrupt:
            print("\nContinuous acquisition stopped")
    
    def get_status(self) -> Dict:
        """Get bridge status."""
        return {
            'connected': self.is_connected,
            'acquisitions': self.acquisition_count,
            'last_acquisition_time_ms': self.last_acquisition_time * 1000,
            'config': {
                'port': self.config.port,
                'num_elements': self.config.num_elements,
                'sample_rate': self.config.sample_rate
            }
        }


def demo_single_acquisition():
    """Demo: Single acquisition and processing."""
    print("="*70)
    print("HARDWARE BRIDGE DEMO: Single Acquisition")
    print("="*70)
    
    config = HardwareConfig(
        port='/dev/ttyUSB0',
        push_frequency_hz=100,
        focus_depth_mm=30
    )
    
    bridge = ArrayHardwareBridge(config)
    
    if not bridge.connect():
        print("\nNote: No hardware connected - this is expected if ESP32 not plugged in")
        print("The code structure is ready for hardware integration.")
        return
    
    try:
        # Acquire
        print("\nAcquiring single frame...")
        data = bridge.acquire_single()
        
        if data is not None:
            print(f"  Acquired: {data.shape}")
            print(f"  Data range: [{data.min()}, {data.max()}]")
            
            # Process
            print("\nProcessing...")
            result = bridge.process_dispersion(data)
            
            if result['success']:
                print(f"  G' = {result['G_prime']:.0f} Pa")
                print(f"  η = {result['eta']:.3f} Pa·s")
                print(f"  R² = {result['r_squared']:.4f}")
            else:
                print(f"  Processing failed: {result.get('error')}")
        
    finally:
        bridge.disconnect()


def demo_sequential_acquisition():
    """Demo: Sequential multi-frequency acquisition."""
    print("="*70)
    print("HARDWARE BRIDGE DEMO: Sequential Acquisition")
    print("="*70)
    
    config = HardwareConfig(
        port='/dev/ttyUSB0',
        sequential_frequencies=[60, 80, 100, 120, 140]
    )
    
    bridge = ArrayHardwareBridge(config)
    
    if not bridge.connect():
        print("\nNote: No hardware connected - code structure ready")
        return
    
    try:
        print("\nRunning sequential acquisition...")
        result = bridge.acquire_sequential()
        
        if result['success']:
            fit = result['fit']
            print(f"\nSequential acquisition complete!")
            print(f"  Frequencies: {result['frequencies_acquired']}")
            print(f"  G' = {fit['G_prime']:.0f} Pa")
            print(f"  η = {fit['eta']:.3f} Pa·s")
        else:
            print(f"  Failed: {result.get('error')}")
            
    finally:
        bridge.disconnect()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Hardware Bridge Demo')
    parser.add_argument('--mode', choices=['single', 'sequential', 'continuous'],
                       default='single', help='Acquisition mode')
    parser.add_argument('--port', default='/dev/ttyUSB0', help='Serial port')
    
    args = parser.parse_args()
    
    if args.mode == 'single':
        demo_single_acquisition()
    elif args.mode == 'sequential':
        demo_sequential_acquisition()
    elif args.mode == 'continuous':
        print("Continuous mode - requires hardware connection")
        print("Run with ESP32 connected to test")


if __name__ == '__main__':
    main()
