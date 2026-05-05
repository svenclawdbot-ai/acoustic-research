#!/usr/bin/env python3
"""
verify_dma_integrity.py - DMA data integrity verification for ESP32-S3

Tests:
1. Ramp pattern continuity (no dropped samples)
2. Sample rate accuracy
3. Trigger latency
4. Buffer integrity

Usage:
    python verify_dma_integrity.py --port /dev/ttyUSB0
    python verify_dma_integrity.py --port COM3 --samples 4096 --bursts 10
"""

import serial
import struct
import json
import time
import argparse
import numpy as np
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TestResult:
    """Results from a single acquisition test"""
    burst_id: int
    samples_expected: int
    samples_received: int
    sample_rate_expected: float
    sample_rate_actual: float
    sample_rate_error_pct: float
    continuity_errors: int
    trigger_latency_ms: float
    passed: bool


class DMAVerifier:
    """DMA acquisition verification tool"""
    
    def __init__(self, port: str = '/dev/ttyUSB0', baud: int = 921600, timeout: float = 10.0):
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.ser: Optional[serial.Serial] = None
        self.results: List[TestResult] = []
        
    def connect(self) -> bool:
        """Open serial connection to ESP32"""
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baud,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout
            )
            # Wait for ESP32 boot
            time.sleep(0.5)
            self.ser.reset_input_buffer()
            print(f"✓ Connected to {self.port} @ {self.baud} baud")
            return True
        except serial.SerialException as e:
            print(f"✗ Failed to open {self.port}: {e}")
            return False
    
    def disconnect(self):
        """Close serial connection"""
        if self.ser:
            self.ser.close()
            self.ser = None
    
    def send_command(self, cmd: Dict) -> Dict:
        """Send JSON command and receive response"""
        if not self.ser:
            raise RuntimeError("Not connected")
        
        cmd_json = json.dumps(cmd)
        self.ser.write(cmd_json.encode() + b'\n')
        
        response_line = self.ser.readline().decode().strip()
        if not response_line:
            raise TimeoutError("No response from device")
        
        return json.loads(response_line)
    
    def init_dma(self, num_channels: int, samples_per_channel: int, 
                 sample_rate: int = 20000000, trigger: str = "soft") -> bool:
        """Initialize DMA acquisition"""
        cmd = {
            "cmd": "dma_init",
            "num_channels": num_channels,
            "samples_per_channel": samples_per_channel,
            "sample_rate": sample_rate,
            "trigger": trigger
        }
        
        response = self.send_command(cmd)
        if response.get("status") == "ok":
            print(f"✓ DMA initialized: {num_channels}ch × {samples_per_channel} samples @ {sample_rate/1e6:.1f} MSa/s")
            return True
        else:
            print(f"✗ DMA init failed: {response.get('error', 'unknown')}")
            return False
    
    def acquire_burst(self, timeout: float = 5.0) -> Optional[np.ndarray]:
        """Acquire single burst and return data"""
        # Start acquisition
        cmd = {"cmd": "dma_start_burst"}
        response = self.send_command(cmd)
        
        if response.get("status") != "ok":
            print(f"✗ Start failed: {response.get('error', 'unknown')}")
            return None
        
        # Wait for completion
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = self.send_command({"cmd": "dma_get_status"})
            
            if status.get("state") == "transfer":
                # Read data
                return self._read_data()
            elif status.get("state") == "error":
                print("✗ Acquisition error")
                return None
            
            time.sleep(0.01)
        
        print("✗ Acquisition timeout")
        return None
    
    def _read_data(self) -> Optional[np.ndarray]:
        """Read acquired data from device"""
        cmd = {"cmd": "dma_read_data"}
        response = self.send_command(cmd)
        
        if response.get("status") != "ok":
            return None
        
        # Read binary data
        num_bytes = response.get("bytes_available", 0)
        if num_bytes == 0:
            return None
        
        data = self.ser.read(num_bytes)
        if len(data) != num_bytes:
            print(f"✗ Short read: {len(data)} / {num_bytes} bytes")
            return None
        
        # Convert to numpy array (12-bit ADC in 16-bit container)
        samples = np.frombuffer(data, dtype=np.uint16)
        return samples
    
    def verify_ramp_pattern(self, data: np.ndarray, threshold: int = 10) -> Tuple[int, bool]:
        """
        Verify ramp pattern continuity
        
        Args:
            data: ADC samples
            threshold: Maximum allowed discontinuity
            
        Returns:
            (error_count, passed)
        """
        if len(data) < 2:
            return 0, False
        
        # Calculate differences
        diffs = np.diff(data.astype(np.int32))
        
        # Count discontinuities (allowing for 12-bit wrap-around)
        errors = 0
        for d in diffs:
            if abs(d) > threshold and abs(d) < (4096 - threshold):
                errors += 1
        
        passed = errors == 0
        return errors, passed
    
    def run_burst_test(self, num_bursts: int = 10, samples_per_channel: int = 4096,
                       num_channels: int = 8, sample_rate: int = 20000000) -> bool:
        """Run complete burst acquisition test"""
        
        print(f"\n{'='*60}")
        print(f"DMA Integrity Test")
        print(f"{'='*60}")
        print(f"Bursts: {num_bursts}")
        print(f"Channels: {num_channels}")
        print(f"Samples/ch: {samples_per_channel}")
        print(f"Sample rate: {sample_rate/1e6:.1f} MSa/s")
        print(f"{'='*60}\n")
        
        # Initialize DMA
        if not self.init_dma(num_channels, samples_per_channel, sample_rate):
            return False
        
        self.results = []
        
        for burst_id in range(num_bursts):
            print(f"\nBurst {burst_id + 1}/{num_bursts}...", end=" ")
            
            # Acquire data
            data = self.acquire_burst()
            if data is None:
                print("FAILED")
                continue
            
            # Get status
            status = self.send_command({"cmd": "dma_get_status"})
            
            samples_expected = samples_per_channel * num_channels
            samples_received = len(data)
            
            # Verify ramp pattern
            errors, passed = self.verify_ramp_pattern(data)
            
            # Calculate actual sample rate
            samples_acquired = status.get("samples_acquired", 0)
            elapsed_us = status.get("elapsed_us", 1)
            sample_rate_actual = (samples_acquired * 1e6) / elapsed_us if elapsed_us > 0 else 0
            sample_rate_error = abs(sample_rate_actual - sample_rate) / sample_rate * 100
            
            # Trigger latency
            trigger_latency_ms = status.get("trigger_latency_us", 0) / 1000.0
            
            result = TestResult(
                burst_id=burst_id,
                samples_expected=samples_expected,
                samples_received=samples_received,
                sample_rate_expected=sample_rate,
                sample_rate_actual=sample_rate_actual,
                sample_rate_error_pct=sample_rate_error,
                continuity_errors=errors,
                trigger_latency_ms=trigger_latency_ms,
                passed=passed and samples_received == samples_expected and sample_rate_error < 0.1
            )
            
            self.results.append(result)
            
            status_str = "PASS" if result.passed else "FAIL"
            print(f"{status_str} (SR: {sample_rate_actual/1e6:.2f} MSa/s, Errors: {errors})")
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        if not self.results:
            print("No results to display")
            return
        
        print(f"\n{'='*60}")
        print("TEST SUMMARY")
        print(f"{'='*60}")
        
        passed = sum(1 for r in self.results if r.passed)
        failed = len(self.results) - passed
        
        print(f"Total tests: {len(self.results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        
        if self.results:
            sample_rates = [r.sample_rate_actual for r in self.results]
            latencies = [r.trigger_latency_ms for r in self.results]
            errors = [r.continuity_errors for r in self.results]
            
            print(f"\nSample Rate Statistics:")
            print(f"  Mean: {np.mean(sample_rates)/1e6:.3f} MSa/s")
            print(f"  Std:  {np.std(sample_rates)/1e6:.3f} MSa/s")
            print(f"  Min:  {np.min(sample_rates)/1e6:.3f} MSa/s")
            print(f"  Max:  {np.max(sample_rates)/1e6:.3f} MSa/s")
            
            print(f"\nTrigger Latency Statistics:")
            print(f"  Mean: {np.mean(latencies):.3f} ms")
            print(f"  Std:  {np.std(latencies):.3f} ms")
            
            print(f"\nContinuity Errors:")
            print(f"  Total: {sum(errors)}")
            print(f"  Max per burst: {max(errors)}")
        
        print(f"{'='*60}")
        
        return passed == len(self.results)
    
    def save_results(self, filename: str = "dma_test_results.json"):
        """Save results to JSON file"""
        data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "port": self.port,
            "baud": self.baud,
            "results": [
                {
                    "burst_id": r.burst_id,
                    "samples_expected": r.samples_expected,
                    "samples_received": r.samples_received,
                    "sample_rate_expected_hz": r.sample_rate_expected,
                    "sample_rate_actual_hz": r.sample_rate_actual,
                    "sample_rate_error_pct": r.sample_rate_error_pct,
                    "continuity_errors": r.continuity_errors,
                    "trigger_latency_ms": r.trigger_latency_ms,
                    "passed": r.passed
                }
                for r in self.results
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\nResults saved to {filename}")


def main():
    parser = argparse.ArgumentParser(description='DMA Acquisition Verification')
    parser.add_argument('--port', default='/dev/ttyUSB0', help='Serial port')
    parser.add_argument('--baud', type=int, default=921600, help='Baud rate')
    parser.add_argument('--bursts', type=int, default=10, help='Number of bursts')
    parser.add_argument('--samples', type=int, default=4096, help='Samples per channel')
    parser.add_argument('--channels', type=int, default=8, help='Number of channels')
    parser.add_argument('--rate', type=int, default=20000000, help='Sample rate (Hz)')
    parser.add_argument('--output', default='dma_test_results.json', help='Output file')
    
    args = parser.parse_args()
    
    verifier = DMAVerifier(port=args.port, baud=args.baud)
    
    if not verifier.connect():
        return 1
    
    try:
        success = verifier.run_burst_test(
            num_bursts=args.bursts,
            samples_per_channel=args.samples,
            num_channels=args.channels,
            sample_rate=args.rate
        )
        
        if success:
            all_passed = verifier.print_summary()
            verifier.save_results(args.output)
            return 0 if all_passed else 1
        else:
            return 1
    finally:
        verifier.disconnect()


if __name__ == '__main__':
    exit(main())
