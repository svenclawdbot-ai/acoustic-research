#!/usr/bin/env python3
"""
TurboQuant Controller - Python Interface for Red Pitaya

Controls the FPGA-based 74HC595 driver for 8-element ultrasound scanning.
Runs on Red Pitaya STEMlab 125-14 (Linux).

Usage:
    from turboquant import TurboQuantController
    
    tq = TurboQuantController()
    tq.select_element(0)  # Activate element 0
    data = tq.read_adc()  # Read ADC
"""

import os
import time
import struct
import mmap
import numpy as np
from enum import IntEnum
from typing import Optional, Tuple

# Red Pitaya memory-mapped FPGA register addresses
# These are relative to the AXI GP0 base address (0x40000000)
class RegisterOffset(IntEnum):
    """FPGA register offsets from base address"""
    ELEMENT_SELECT = 0x00    # 3-bit element select (0-7)
    ELEMENT_VALID = 0x04     # Trigger pulse (write 1 to update)
    BUSY_STATUS = 0x08       # Controller busy flag
    CURRENT_PATTERN = 0x0C   # Current 8-bit gate pattern (read-only)
    CONTROL = 0x10          # Global control register

class ControlBits(IntEnum):
    """Control register bit definitions"""
    RESET = 0x01           # Reset controller
    ENABLE = 0x02          # Enable outputs

class TurboQuantController:
    """
    Interface to TurboQuant FPGA controller on Red Pitaya.
    
    Handles:
    - Element selection (0-7) via 74HC595 shift register
    - ADC data capture from Red Pitaya fast inputs
    - Sequential scanning with software beamforming
    """
    
    # Red Pitaya AXI GP0 base address
    BASE_ADDR = 0x40000000
    REG_SIZE = 0x10000  # 64KB register space
    
    # ADC parameters
    ADC_CHANNELS = 2
    ADC_SAMPLE_RATE = 125_000_000  # 125 MSa/s
    ADC_BITS = 14
    ADC_VREF = 1.0  # Volts (±1V range)
    
    def __init__(self, base_addr: int = None, adc_buffer_size: int = 16384):
        """
        Initialize TurboQuant controller.
        
        Args:
            base_addr: FPGA register base address (default: 0x40000000)
            adc_buffer_size: Number of samples to capture per read
        """
        self.base_addr = base_addr or self.BASE_ADDR
        self.adc_buffer_size = adc_buffer_size
        self._fd = None
        self._mem = None
        self._current_element = 0
        
        # Initialize memory-mapped register access
        self._init_registers()
        
        # Initialize ADC interface
        self._init_adc()
        
        print(f"TurboQuant Controller initialized")
        print(f"  Base address: 0x{self.base_addr:08X}")
        print(f"  ADC buffer: {self.adc_buffer_size} samples")
        
    def _init_registers(self):
        """Initialize memory-mapped register access via /dev/mem"""
        try:
            self._fd = os.open('/dev/mem', os.O_RDWR | os.O_SYNC)
            self._mem = mmap.mmap(
                self._fd,
                self.REG_SIZE,
                mmap.MAP_SHARED,
                mmap.PROT_READ | mmap.PROT_WRITE,
                offset=self.base_addr
            )
        except (OSError, PermissionError) as e:
            raise RuntimeError(
                f"Cannot access /dev/mem: {e}\n"
                "Run as root or use 'sudo'"
            )
    
    def _init_adc(self):
        """Initialize Red Pitaya ADC interface"""
        # Check if ADC is available via standard interface
        self.adc_path = '/dev/rpadc'  # Standard Red Pitaya ADC device
        if not os.path.exists(self.adc_path):
            # Fall back to memory-mapped ADC
            self.adc_path = None
            self._adc_base = 0x40100000  # ADC DMA buffer address
    
    def _write_reg(self, offset: int, value: int):
        """Write 32-bit value to FPGA register"""
        self._mem[offset:offset+4] = struct.pack('<I', value)
    
    def _read_reg(self, offset: int) -> int:
        """Read 32-bit value from FPGA register"""
        return struct.unpack('<I', self._mem[offset:offset+4])[0]
    
    def select_element(self, element: int, wait: bool = True) -> bool:
        """
        Select active ultrasound element (0-7).
        
        Args:
            element: Element number (0-7)
            wait: If True, wait for shift operation to complete
            
        Returns:
            True if successful, False if busy
            
        Raises:
            ValueError: If element not in range 0-7
        """
        if not 0 <= element <= 7:
            raise ValueError(f"Element must be 0-7, got {element}")
        
        # Check if controller is busy
        if self._read_reg(RegisterOffset.BUSY_STATUS):
            if wait:
                # Wait up to 100ms for busy to clear
                timeout = time.time() + 0.1
                while self._read_reg(RegisterOffset.BUSY_STATUS):
                    if time.time() > timeout:
                        return False
                    time.sleep(0.001)
            else:
                return False
        
        # Write element select and trigger
        self._write_reg(RegisterOffset.ELEMENT_SELECT, element)
        self._write_reg(RegisterOffset.ELEMENT_VALID, 1)
        self._write_reg(RegisterOffset.ELEMENT_VALID, 0)  # Clear trigger
        
        self._current_element = element
        
        if wait:
            # Wait for shift operation (~10us)
            time.sleep(0.00002)  # 20us to be safe
        
        return True
    
    def get_current_pattern(self) -> int:
        """
        Read current 8-bit gate pattern from FPGA.
        
        Returns:
            8-bit pattern (one-hot encoding of active element)
        """
        return self._read_reg(RegisterOffset.CURRENT_PATTERN) & 0xFF
    
    def is_busy(self) -> bool:
        """Check if controller is busy shifting"""
        return bool(self._read_reg(RegisterOffset.BUSY_STATUS))
    
    def reset(self):
        """Reset the FPGA controller"""
        self._write_reg(RegisterOffset.CONTROL, ControlBits.RESET)
        time.sleep(0.001)
        self._write_reg(RegisterOffset.CONTROL, 0)
        time.sleep(0.001)
    
    def read_adc(self, channel: int = 0, n_samples: int = None) -> np.ndarray:
        """
        Read ADC data from Red Pitaya fast inputs.
        
        Args:
            channel: ADC channel (0 or 1)
            n_samples: Number of samples to read (default: buffer_size)
            
        Returns:
            NumPy array of voltage values (float32)
        """
        if n_samples is None:
            n_samples = self.adc_buffer_size
            
        if channel not in [0, 1]:
            raise ValueError(f"Channel must be 0 or 1, got {channel}")
        
        # For now, return simulated data if ADC not available
        # In real implementation, this reads from Red Pitaya ADC DMA
        if self.adc_path is None:
            # Simulated ADC read - replace with actual implementation
            return self._read_adc_mmap(channel, n_samples)
        else:
            return self._read_adc_device(channel, n_samples)
    
    def _read_adc_mmap(self, channel: int, n_samples: int) -> np.ndarray:
        """Read ADC via memory-mapped DMA buffer"""
        # This is a placeholder - implement based on Red Pitaya ADC driver
        # In real hardware, this reads from 0x40100000 + offset
        
        # Return simulated sine wave for testing
        t = np.arange(n_samples) / self.ADC_SAMPLE_RATE
        freq = 5e6  # 5 MHz ultrasound
        amplitude = 0.5  # 0.5V
        
        # Add element-specific phase shift for testing
        phase = self._current_element * np.pi / 4
        
        data = amplitude * np.sin(2 * np.pi * freq * t + phase)
        
        # Add some noise
        data += np.random.normal(0, 0.01, n_samples)
        
        return data.astype(np.float32)
    
    def _read_adc_device(self, channel: int, n_samples: int) -> np.ndarray:
        """Read ADC via device driver"""
        # Implement actual ADC read from /dev/rpadc or similar
        # This is hardware-specific
        raise NotImplementedError("ADC device driver not implemented")
    
    def scan_all_elements(self, n_samples: int = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Sequential scan through all 8 elements.
        
        Args:
            n_samples: Samples per element (default: buffer_size)
            
        Returns:
            Tuple of (element_data, metadata)
            element_data: Shape (8, n_samples) array
            metadata: Timing and pattern info
        """
        if n_samples is None:
            n_samples = self.adc_buffer_size
        
        data = np.zeros((8, n_samples), dtype=np.float32)
        patterns = []
        timestamps = []
        
        for element in range(8):
            # Select element
            t0 = time.time()
            self.select_element(element, wait=True)
            
            # Small delay for signal settling
            time.sleep(0.0001)  # 100us
            
            # Read ADC
            data[element, :] = self.read_adc(channel=0, n_samples=n_samples)
            
            patterns.append(self.get_current_pattern())
            timestamps.append(time.time() - t0)
        
        metadata = {
            'patterns': patterns,
            'timestamps': timestamps,
            'sample_rate': self.ADC_SAMPLE_RATE,
            'n_samples': n_samples
        }
        
        return data, metadata
    
    def close(self):
        """Clean up resources"""
        if self._mem:
            self._mem.close()
        if self._fd:
            os.close(self._fd)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def demo_scan():
    """Demonstration: scan all elements and display results"""
    print("=" * 60)
    print("TurboQuant Controller Demo")
    print("=" * 60)
    
    with TurboQuantController() as tq:
        print("\n1. Testing element selection...")
        for element in range(8):
            tq.select_element(element)
            pattern = tq.get_current_pattern()
            expected = 1 << element
            status = "✓" if pattern == expected else "✗"
            print(f"  Element {element}: pattern=0b{pattern:08b} {status}")
        
        print("\n2. Sequential scan with ADC read...")
        data, meta = tq.scan_all_elements(n_samples=1024)
        
        print(f"  Captured: {data.shape[0]} elements × {data.shape[1]} samples")
        print(f"  Sample rate: {meta['sample_rate']/1e6:.1f} MSa/s")
        print(f"  Total scan time: {sum(meta['timestamps'])*1000:.2f} ms")
        
        # Simple statistics
        print("\n3. Signal statistics:")
        for i in range(8):
            rms = np.sqrt(np.mean(data[i]**2))
            peak = np.max(np.abs(data[i]))
            print(f"  Element {i}: RMS={rms:.3f}V, Peak={peak:.3f}V")
        
        print("\n4. Save to file...")
        np.savez('scan_data.npz', 
                 data=data, 
                 metadata=meta,
                 timestamp=time.time())
        print("  Saved to scan_data.npz")
    
    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)


if __name__ == '__main__':
    demo_scan()
