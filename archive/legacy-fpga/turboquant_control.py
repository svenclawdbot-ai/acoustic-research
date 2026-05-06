#!/usr/bin/env python3
"""
TurboQuant FPGA Control Interface
=================================

Python control interface for Red Pitaya TurboQuant shear wave FPGA.
Provides memory-mapped register access, acquisition control, and
integration with signal processing pipeline.

Usage:
    from turboquant_control import TurboQuantFPGA
    
    # Connect to FPGA
    tq = TurboQuantFPGA()
    
    # Configure acquisition
    tq.set_frequency(100)           # 100 Hz tone burst
    tq.set_burst_cycles(5)          # 5 cycles per burst
    tq.set_num_frequencies(5)       # Acquire 5 frequencies (60-100 Hz)
    
    # Run acquisition
    data = tq.acquire_single()
    
    # Or continuous monitoring
    for frame in tq.acquire_continuous():
        process(frame)

Author: Research Project
Date: April 17, 2026
"""

import numpy as np
import mmap
import os
import time
import struct
from typing import Dict, List, Optional, Tuple, Callable, Generator
from dataclasses import dataclass
from enum import Enum
import warnings

# Try to import Red Pitaya SCPI interface
try:
    import redpitaya_scpi as scpi
    HAS_SCPI = True
except ImportError:
    HAS_SCPI = False
    warnings.warn("redpitaya_scpi not installed. Install with: pip install redpitaya_scpi")


class RegisterMap(Enum):
    """FPGA register addresses (offset from base)."""
    CONTROL = 0x00        # Control register
    STATUS = 0x04         # Status register
    FREQ_SELECT = 0x08    # Frequency selection (0-8)
    BURST_CYCLES = 0x0C   # Burst cycles (1-15)
    NUM_FREQS = 0x10      # Number of frequencies
    FOCUS_DEPTH = 0x14    # Focus depth in mm (Q16.16)
    STEERING = 0x18       # Steering angle (Q8.8)
    SOUND_SPEED = 0x60    # Sound speed in m/s (Q16.16)


class ControlBits:
    """Control register bit definitions."""
    START = 0x01
    STOP = 0x02
    SINGLE_SHOT = 0x04


class StatusBits:
    """Status register bit definitions."""
    ACQUIRING = 0x01
    BURST_ACTIVE = 0x02
    FREQ_READY = 0x04


@dataclass
class AcquisitionConfig:
    """Configuration for shear wave acquisition."""
    frequency_hz: int = 100        # Center frequency
    burst_cycles: int = 5          # Cycles per burst
    num_frequencies: int = 5       # Sequential frequencies (5 = 60-100 Hz)
    focus_depth_mm: float = 30.0   # Focus depth
    steering_angle_deg: float = 0.0  # Steering angle
    sound_speed_ms: float = 1540.0 # Sound speed
    samples_per_acq: int = 8192    # Samples per acquisition
    
    # Frequency table (indices 0-8)
    FREQ_TABLE = [60, 70, 80, 90, 100, 110, 120, 130, 140]
    
    def get_freq_index(self, freq_hz: int) -> int:
        """Get frequency table index from Hz value."""
        try:
            return self.FREQ_TABLE.index(freq_hz)
        except ValueError:
            # Find closest
            return min(range(len(self.FREQ_TABLE)), 
                        key=lambda i: abs(self.FREQ_TABLE[i] - freq_hz))


@dataclass
class AcquisitionResult:
    """Result from a single acquisition."""
    raw_data: np.ndarray           # Raw ADC data (2 channels)
    frequency_hz: int              # Excitation frequency
    element_idx: int               # Element used for transmit
    timestamp: float               # Acquisition timestamp
    
    # Processed results (filled by pipeline)
    dispersion: Optional[Dict] = None
    G_prime: Optional[float] = None
    eta: Optional[float] = None


class TurboQuantFPGA:
    """
    Main interface to TurboQuant FPGA on Red Pitaya.
    
    Provides low-level register access and high-level acquisition control.
    """
    
    # Red Pitaya memory map
    BASE_ADDR = 0x40000000          # AXI GP0 base address
    REG_SIZE = 0x10000              # 64KB register space
    DMA_BASE = 0x80000000           # DDR DMA buffer base
    
    def __init__(self, ip_address: Optional[str] = None, 
                 local_mmap: bool = True):
        """
        Initialize FPGA interface.
        
        Parameters:
            ip_address: Red Pitaya IP for SCPI remote control (optional)
            local_mmap: Use local memory-mapped registers (for code running on RP)
        """
        self.ip_address = ip_address
        self.local_mmap = local_mmap
        self.mm = None                 # Memory map object
        self.scpi = None               # SCPI connection
        
        # Configuration
        self.config = AcquisitionConfig()
        
        # Statistics
        self.acquisition_count = 0
        self.last_acquisition_time = 0.0
        
        # Connect
        self._connect()
    
    def _connect(self):
        """Establish connection to FPGA."""
        if self.ip_address and HAS_SCPI:
            # Remote SCPI connection
            self.scpi = scpi.scpi(self.ip_address)
            print(f"Connected to Red Pitaya at {self.ip_address} (SCPI)")
            
        elif self.local_mmap:
            # Local memory-mapped access (running on Red Pitaya)
            try:
                fd = os.open("/dev/mem", os.O_RDWR | os.O_SYNC)
                self.mm = mmap.mmap(fd, self.REG_SIZE, 
                                   mmap.MAP_SHARED,
                                   mmap.PROT_READ | mmap.PROT_WRITE,
                                   offset=self.BASE_ADDR)
                os.close(fd)
                print("Connected to FPGA via memory-mapped registers (local)")
            except PermissionError:
                print("ERROR: Need root privileges for /dev/mem access")
                print("Run with: sudo python3 script.py")
                raise
            except Exception as e:
                print(f"ERROR: Failed to open memory map: {e}")
                raise
        else:
            warnings.warn("No connection method available (set ip_address or local_mmap)")
    
    def _read_reg(self, offset: int) -> int:
        """Read 32-bit register."""
        if self.mm:
            self.mm.seek(offset)
            return struct.unpack('<I', self.mm.read(4))[0]
        elif self.scpi:
            # SCPI: use custom register read command
            resp = self.scpi.txrx(f"REG:READ? {offset}")
            return int(resp)
        return 0
    
    def _write_reg(self, offset: int, value: int):
        """Write 32-bit register."""
        if self.mm:
            self.mm.seek(offset)
            self.mm.write(struct.pack('<I', value))
        elif self.scpi:
            self.scpi.txrx(f"REG:WRITE {offset},{value}")
    
    def read_status(self) -> Dict:
        """Read FPGA status register."""
        status = self._read_reg(RegisterMap.STATUS.value)
        return {
            'acquiring': bool(status & StatusBits.ACQUIRING),
            'burst_active': bool(status & StatusBits.BURST_ACTIVE),
            'freq_ready': bool(status & StatusBits.FREQ_READY),
            'raw': status
        }
    
    def set_frequency(self, freq_hz: int):
        """Set excitation frequency."""
        idx = self.config.get_freq_index(freq_hz)
        self._write_reg(RegisterMap.FREQ_SELECT.value, idx)
        self.config.frequency_hz = freq_hz
        print(f"Set frequency: {freq_hz} Hz (index {idx})")
    
    def set_burst_cycles(self, cycles: int):
        """Set number of cycles per burst."""
        cycles = max(1, min(15, cycles))
        self._write_reg(RegisterMap.BURST_CYCLES.value, cycles)
        self.config.burst_cycles = cycles
        print(f"Set burst cycles: {cycles}")
    
    def set_num_frequencies(self, num: int):
        """Set number of frequencies for sequential acquisition."""
        num = max(1, min(9, num))
        self._write_reg(RegisterMap.NUM_FREQS.value, num)
        self.config.num_frequencies = num
        print(f"Set number of frequencies: {num}")
    
    def set_focus_depth(self, depth_mm: float):
        """Set focus depth for beamforming."""
        # Convert to Q16.16 fixed point
        fixed = int(depth_mm * 65536)
        self._write_reg(RegisterMap.FOCUS_DEPTH.value, fixed)
        self.config.focus_depth_mm = depth_mm
        print(f"Set focus depth: {depth_mm} mm")
    
    def configure(self, **kwargs):
        """Configure multiple parameters at once."""
        if 'frequency' in kwargs:
            self.set_frequency(kwargs['frequency'])
        if 'burst_cycles' in kwargs:
            self.set_burst_cycles(kwargs['burst_cycles'])
        if 'num_frequencies' in kwargs:
            self.set_num_frequencies(kwargs['num_frequencies'])
        if 'focus_depth' in kwargs:
            self.set_focus_depth(kwargs['focus_depth'])
    
    def start_acquisition(self, single_shot: bool = False):
        """Start acquisition."""
        control = ControlBits.START
        if single_shot:
            control |= ControlBits.SINGLE_SHOT
        self._write_reg(RegisterMap.CONTROL.value, control)
    
    def stop_acquisition(self):
        """Stop acquisition."""
        self._write_reg(RegisterMap.CONTROL.value, ControlBits.STOP)
    
    def wait_for_acquisition(self, timeout_sec: float = 10.0) -> bool:
        """Wait for acquisition to complete."""
        start_time = time.time()
        while time.time() - start_time < timeout_sec:
            status = self.read_status()
            if not status['acquiring']:
                return True
            time.sleep(0.001)  # 1ms polling
        return False
    
    def read_dma_data(self, num_samples: int) -> np.ndarray:
        """Read data from DMA buffer."""
        if self.mm:
            # Direct memory access
            self.mm.seek(self.DMA_BASE - self.BASE_ADDR)
            raw = self.mm.read(num_samples * 4)  # 4 bytes per sample
            data = np.frombuffer(raw, dtype=np.int32, count=num_samples)
            return data
        elif self.scpi:
            # SCPI data transfer (slower)
            # This would need a custom command in FPGA
            raise NotImplementedError("SCPI DMA read not implemented")
        return np.array([])
    
    def acquire_single(self, frequency: Optional[int] = None) -> AcquisitionResult:
        """
        Acquire single frame.
        
        Parameters:
            frequency: Excitation frequency (Hz), uses config if None
            
        Returns:
            AcquisitionResult with raw data and metadata
        """
        if frequency:
            self.set_frequency(frequency)
        
        # Start acquisition
        start_time = time.time()
        self.start_acquisition(single_shot=True)
        
        # Wait for completion
        if not self.wait_for_acquisition(timeout_sec=5.0):
            raise TimeoutError("Acquisition timeout")
        
        # Read data
        num_samples = self.config.samples_per_acq
        data = self.read_dma_data(num_samples)
        
        # Reshape to (2 channels, samples)
        if len(data) >= num_samples:
            data = data[:num_samples].reshape(2, -1)
        
        self.last_acquisition_time = time.time() - start_time
        self.acquisition_count += 1
        
        return AcquisitionResult(
            raw_data=data,
            frequency_hz=self.config.frequency_hz,
            element_idx=0,  # Would come from FPGA status
            timestamp=time.time()
        )
    
    def acquire_sequential(self) -> List[AcquisitionResult]:
        """
        Sequential multi-frequency acquisition.
        
        Returns:
            List of AcquisitionResult, one per frequency
        """
        results = []
        freqs = self.config.FREQ_TABLE[:self.config.num_frequencies]
        
        print(f"Sequential acquisition: {len(freqs)} frequencies")
        
        for freq in freqs:
            print(f"  Acquiring at {freq} Hz...", end=' ')
            try:
                result = self.acquire_single(frequency=freq)
                results.append(result)
                print(f"✓ ({len(result.raw_data)} samples)")
            except Exception as e:
                print(f"✗ ({e})")
        
        print(f"Complete: {len(results)}/{len(freqs)} frequencies acquired")
        return results
    
    def acquire_continuous(self, interval_ms: float = 500.0) -> Generator[AcquisitionResult, None, None]:
        """
        Continuous acquisition generator.
        
        Yields:
            AcquisitionResult for each frame
        """
        print(f"Starting continuous acquisition ({interval_ms} ms interval)")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                loop_start = time.time()
                
                result = self.acquire_single()
                yield result
                
                # Maintain interval
                elapsed = (time.time() - loop_start) * 1000
                sleep_time = max(0, (interval_ms - elapsed) / 1000)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
        except KeyboardInterrupt:
            print("\nContinuous acquisition stopped")
            self.stop_acquisition()
    
    def get_status(self) -> Dict:
        """Get comprehensive status."""
        fpga_status = self.read_status()
        return {
            'connected': self.mm is not None or self.scpi is not None,
            'acquisitions': self.acquisition_count,
            'last_acquisition_time_ms': self.last_acquisition_time * 1000,
            'fpga_status': fpga_status,
            'config': {
                'frequency_hz': self.config.frequency_hz,
                'burst_cycles': self.config.burst_cycles,
                'num_frequencies': self.config.num_frequencies,
                'focus_depth_mm': self.config.focus_depth_mm
            }
        }
    
    def close(self):
        """Close connection and release resources."""
        if self.mm:
            self.mm.close()
            self.mm = None
        if self.scpi:
            # SCPI close if needed
            pass
        print("TurboQuant connection closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


#============================================================================
# Integration with Signal Processing Pipeline
#============================================================================

class TurboQuantPipeline:
    """
    Complete acquisition + processing pipeline for TurboQuant.
    Integrates FPGA control with dispersion extraction and fitting.
    """
    
    def __init__(self, fpga: Optional[TurboQuantFPGA] = None, **kwargs):
        """
        Initialize pipeline.
        
        Parameters:
            fpga: Existing TurboQuantFPGA instance or None to create new
            **kwargs: Passed to TurboQuantFPGA constructor if creating new
        """
        if fpga is None:
            self.fpga = TurboQuantFPGA(**kwargs)
        else:
            self.fpga = fpga
        
        # Import processing functions
        from e2e_from_demo import extract_dispersion_envelope, fit_kelvin_voigt
        self.extract_dispersion = extract_dispersion_envelope
        self.fit_params = fit_kelvin_voigt
    
    def acquire_and_process(self, frequency: Optional[int] = None,
                           distances_mm: Optional[List[float]] = None) -> Dict:
        """
        Acquire single frame and process to get mechanical parameters.
        
        Parameters:
            frequency: Excitation frequency (Hz)
            distances_mm: Receiver distances in mm (default: 5,15,25,35)
            
        Returns:
            Dictionary with acquisition result and fitted parameters
        """
        # Default distances
        if distances_mm is None:
            distances_mm = [5, 15, 25, 35]
        
        # Acquire
        result = self.fpga.acquire_single(frequency)
        
        # Process
        fs = 125e6  # Red Pitaya sample rate
        dt = 1.0 / fs
        distances = np.array(distances_mm) / 1000.0  # Convert to meters
        
        # Extract dispersion
        freqs = [result.frequency_hz] if frequency else [60, 80, 100, 120, 140]
        dispersion = self.extract_dispersion(result.raw_data[0], dt, distances, freqs)
        
        # Fit parameters if we have data
        fit_result = None
        if len(dispersion['velocities']) > 0:
            fit_result = self.fit_params(
                dispersion['frequencies'],
                dispersion['velocities'],
                dispersion['uncertainties']
            )
            
            result.G_prime = fit_result.get('G_prime')
            result.eta = fit_result.get('eta')
        
        result.dispersion = dispersion
        
        return {
            'acquisition': result,
            'fit': fit_result,
            'G_prime': result.G_prime,
            'eta': result.eta
        }
    
    def run_sequential_sweep(self) -> Dict:
        """
        Run full sequential frequency sweep and fit.
        
        Returns:
            Complete dispersion curve and Kelvin-Voigt parameters
        """
        # Acquire all frequencies
        results = self.fpga.acquire_sequential()
        
        # Collect dispersion points
        all_freqs = []
        all_vels = []
        all_unc = []
        
        for result in results:
            # Process each result
            # ... extraction logic ...
            pass
        
        # Fit final model
        # ... fitting logic ...
        
        return {
            'frequencies': all_freqs,
            'velocities': all_vels,
            'G_prime': None,  # Fitted value
            'eta': None       # Fitted value
        }


#============================================================================
# Demo and Testing
#============================================================================

def demo_basic_control():
    """Demo: Basic FPGA control."""
    print("="*70)
    print("TurboQuant FPGA Control Demo")
    print("="*70)
    
    # Create FPGA interface (local memory map)
    tq = TurboQuantFPGA(local_mmap=True)
    
    # Read status
    print("\n1. Reading FPGA status:")
    status = tq.read_status()
    print(f"   Acquiring: {status['acquiring']}")
    print(f"   Burst active: {status['burst_active']}")
    print(f"   Frequency ready: {status['freq_ready']}")
    
    # Configure
    print("\n2. Configuring acquisition:")
    tq.configure(
        frequency=100,
        burst_cycles=5,
        num_frequencies=5,
        focus_depth=30.0
    )
    
    # Get full status
    print("\n3. Full status:")
    full_status = tq.get_status()
    print(f"   {full_status}")
    
    tq.close()
    print("\nDemo complete!")


def demo_sequential_acquisition():
    """Demo: Sequential multi-frequency acquisition."""
    print("="*70)
    print("Sequential Acquisition Demo")
    print("="*70)
    
    tq = TurboQuantFPGA(local_mmap=True)
    
    # Configure for 5 frequencies
    tq.set_num_frequencies(5)
    tq.set_burst_cycles(5)
    
    # Run sequential acquisition
    results = tq.acquire_sequential()
    
    print(f"\nAcquired {len(results)} frequencies:")
    for r in results:
        print(f"  {r.frequency_hz} Hz: {len(r.raw_data)} samples")
    
    tq.close()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='TurboQuant FPGA Control')
    parser.add_argument('--demo', choices=['basic', 'sequential', 'continuous'],
                       default='basic', help='Demo mode')
    parser.add_argument('--ip', help='Red Pitaya IP address (for remote)')
    
    args = parser.parse_args()
    
    if args.demo == 'basic':
        demo_basic_control()
    elif args.demo == 'sequential':
        demo_sequential_acquisition()
    elif args.demo == 'continuous':
        print("Continuous demo - implement with actual hardware")


if __name__ == '__main__':
    main()
