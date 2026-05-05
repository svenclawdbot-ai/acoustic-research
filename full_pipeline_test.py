#!/usr/bin/env python3
"""
full_pipeline_test.py - End-to-end array + DMA pipeline test

Tests complete signal chain:
1. Set focus depth
2. Fire array element
3. Trigger DMA acquisition
4. Transfer data
5. Plot waveforms with time axis

Usage:
    python full_pipeline_test.py --port /dev/ttyUSB0 --focus 50
    python full_pipeline_test.py --port COM3 --focus 30 --samples 2048 --plot output.png
"""

import serial
import struct
import json
import time
import argparse
import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, Dict, List
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AcquisitionConfig:
    """Acquisition configuration"""
    focus_depth_mm: float
    focus_angle_deg: float = 0.0
    samples_per_channel: int = 2048
    num_channels: int = 8
    sample_rate: int = 20000000  # 20 MHz
    element_pitch_mm: float = 0.5


class PipelineTester:
    """End-to-end pipeline test tool"""
    
    # Speed of sound in tissue (m/s)
    C_TISSUE = 1540.0
    
    def __init__(self, port: str = '/dev/ttyUSB0', baud: int = 921600, timeout: float = 10.0):
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.ser: Optional[serial.Serial] = None
        self.last_data: Optional[np.ndarray] = None
        
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
            time.sleep(0.5)
            self.ser.reset_input_buffer()
            print(f"✓ Connected to {self.port}")
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
    
    def ping(self) -> bool:
        """Ping device"""
        response = self.send_command({"cmd": "ping"})
        return response.get("status") == "ok"
    
    def set_geometry(self, num_elements: int, element_pitch_mm: float) -> bool:
        """Configure array geometry"""
        cmd = {
            "cmd": "set_geometry",
            "num_elements": num_elements,
            "element_pitch_mm": element_pitch_mm
        }
        response = self.send_command(cmd)
        success = response.get("status") == "ok"
        if success:
            print(f"✓ Geometry: {num_elements} elements @ {element_pitch_mm}mm pitch")
        return success
    
    def set_focus(self, depth_mm: float, angle_deg: float = 0.0) -> bool:
        """Set beamforming focus"""
        cmd = {
            "cmd": "set_focus",
            "depth_mm": depth_mm,
            "angle_deg": angle_deg
        }
        response = self.send_command(cmd)
        success = response.get("status") == "ok"
        if success:
            print(f"✓ Focus: {depth_mm}mm depth, {angle_deg}° angle")
        return success
    
    def fire_element(self, element: int, pulse_width_us: float = 1.0, 
                     voltage: int = 100) -> bool:
        """Fire single array element"""
        cmd = {
            "cmd": "fire_element",
            "element": element,
            "pulse_width_us": pulse_width_us,
            "voltage": voltage
        }
        response = self.send_command(cmd)
        success = response.get("status") == "ok"
        if success:
            print(f"✓ Fired element {element}")
        return success
    
    def fire_focused(self) -> bool:
        """Fire with beamforming delays"""
        cmd = {"cmd": "fire_focused"}
        response = self.send_command(cmd)
        success = response.get("status") == "ok"
        if success:
            print("✓ Fired focused beam")
        return success
    
    def init_dma(self, config: AcquisitionConfig) -> bool:
        """Initialize DMA acquisition"""
        cmd = {
            "cmd": "dma_init",
            "num_channels": config.num_channels,
            "samples_per_channel": config.samples_per_channel,
            "sample_rate": config.sample_rate,
            "trigger": "ext",  # External trigger from array firing
            "trigger_gpio": 15
        }
        
        response = self.send_command(cmd)
        if response.get("status") == "ok":
            print(f"✓ DMA: {config.num_channels}ch × {config.samples_per_channel} @ {config.sample_rate/1e6:.1f} MSa/s")
            return True
        else:
            print(f"✗ DMA init failed: {response.get('error', 'unknown')}")
            return False
    
    def arm_acquisition(self) -> bool:
        """Arm DMA for trigger"""
        response = self.send_command({"cmd": "dma_start_burst"})
        if response.get("status") == "ok":
            print("✓ DMA armed")
            return True
        else:
            print(f"✗ Arm failed: {response.get('error', 'unknown')}")
            return False
    
    def wait_for_data(self, timeout: float = 5.0) -> Optional[np.ndarray]:
        """Wait for acquisition and read data"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.send_command({"cmd": "dma_get_status"})
            
            if status.get("state") == "transfer":
                return self._read_data()
            elif status.get("state") == "error":
                print("✗ Acquisition error")
                return None
            
            time.sleep(0.01)
        
        print("✗ Acquisition timeout")
        return None
    
    def _read_data(self) -> Optional[np.ndarray]:
        """Read acquired data"""
        cmd = {"cmd": "dma_read_data"}
        response = self.send_command(cmd)
        
        if response.get("status") != "ok":
            return None
        
        num_bytes = response.get("bytes_available", 0)
        if num_bytes == 0:
            return None
        
        data = self.ser.read(num_bytes)
        if len(data) != num_bytes:
            print(f"✗ Short read: {len(data)} / {num_bytes} bytes")
            return None
        
        samples = np.frombuffer(data, dtype=np.uint16)
        return samples
    
    def run_full_test(self, config: AcquisitionConfig, 
                      plot_file: Optional[str] = None) -> bool:
        """Run complete end-to-end test"""
        
        print(f"\n{'='*60}")
        print("FULL PIPELINE TEST")
        print(f"{'='*60}")
        
        # Step 1: Configure geometry
        if not self.set_geometry(config.num_channels, config.element_pitch_mm):
            return False
        
        # Step 2: Set focus
        if not self.set_focus(config.focus_depth_mm, config.focus_angle_deg):
            return False
        
        # Step 3: Initialize DMA
        if not self.init_dma(config):
            return False
        
        # Step 4: Arm acquisition
        if not self.arm_acquisition():
            return False
        
        # Step 5: Fire array
        time.sleep(0.01)  # Small delay to ensure armed
        
        if not self.fire_focused():
            return False
        
        # Step 6: Wait for and read data
        print("\nWaiting for data...")
        data = self.wait_for_data()
        
        if data is None:
            return False
        
        print(f"✓ Received {len(data)} samples")
        self.last_data = data
        
        # Step 7: Reshape and analyze
        samples_per_ch = config.samples_per_channel
        num_ch = config.num_channels
        
        # Reshape: interleaved channel samples -> [samples, channels]
        if len(data) >= samples_per_ch * num_ch:
            data_reshaped = data[:samples_per_ch * num_ch].reshape(-1, num_ch)
        else:
            print(f"✗ Insufficient data: {len(data)} < {samples_per_ch * num_ch}")
            return False
        
        # Calculate time axis
        dt = 1.0 / config.sample_rate  # seconds
        time_axis = np.arange(samples_per_ch) * dt * 1e6  # microseconds
        
        # Find wavefront arrival times
        arrival_times = self._estimate_arrivals(data_reshaped, time_axis)
        
        # Plot results
        if plot_file:
            self._plot_results(data_reshaped, time_axis, arrival_times, 
                               config, plot_file)
        
        # Validate: Check progressive delays
        self._validate_delays(arrival_times, config)
        
        return True
    
    def _estimate_arrivals(self, data: np.ndarray, 
                           time_axis: np.ndarray) -> List[float]:
        """Estimate wavefront arrival time per channel"""
        arrivals = []
        
        for ch in range(data.shape[1]):
            channel_data = data[:, ch]
            
            # Find first threshold crossing
            threshold = np.max(channel_data) * 0.3  # 30% of max
            crossings = np.where(np.abs(channel_data) > threshold)[0]
            
            if len(crossings) > 0:
                arrivals.append(time_axis[crossings[0]])
            else:
                arrivals.append(np.nan)
        
        return arrivals
    
    def _validate_delays(self, arrival_times: List[float], 
                         config: AcquisitionConfig):
        """Validate that delays are progressive across elements"""
        print(f"\n{'='*60}")
        print("DELAY VALIDATION")
        print(f"{'='*60}")
        
        valid_arrivals = [a for a in arrival_times if not np.isnan(a)]
        
        if len(valid_arrivals) < 2:
            print("✗ Not enough valid arrivals")
            return
        
        # Calculate element positions
        element_positions = np.arange(config.num_channels) * config.element_pitch_mm
        
        # Focus point
        focus_x = config.focus_depth_mm * np.sin(np.radians(config.focus_angle_deg))
        focus_z = config.focus_depth_mm * np.cos(np.radians(config.focus_angle_deg))
        
        print(f"\nFocus point: ({focus_x:.1f}, {focus_z:.1f}) mm")
        print(f"Element pitch: {config.element_pitch_mm} mm")
        print(f"Speed of sound: {self.C_TISSUE} m/s")
        
        print(f"\nChannel arrival times:")
        for i, (pos, arr) in enumerate(zip(element_positions, arrival_times)):
            if not np.isnan(arr):
                # Expected delay from focus
                dist = np.sqrt((pos - focus_x)**2 + focus_z**2)
                time_of_flight = dist * 1e-3 / self.C_TISSUE * 1e6  # us
                print(f"  Ch {i}: pos={pos:.1f}mm, arrival={arr:.2f}us, TOF={time_of_flight:.2f}us")
            else:
                print(f"  Ch {i}: pos={pos:.1f}mm, NO SIGNAL")
        
        # Check if progressive
        diffs = np.diff(valid_arrivals)
        if np.all(diffs > 0):
            print(f"\n✓ Progressive delays confirmed (all positive)")
        elif np.all(diffs < 0):
            print(f"\n✓ Progressive delays confirmed (all negative)")
        else:
            print(f"\n⚠ Non-monotonic delays detected")
        
        print(f"{'='*60}")
    
    def _plot_results(self, data: np.ndarray, time_axis: np.ndarray,
                      arrival_times: List[float],
                      config: AcquisitionConfig,
                      filename: str):
        """Plot waveforms"""
        
        fig, axes = plt.subplots(config.num_channels, 1, 
                                  figsize=(12, 2*config.num_channels),
                                  sharex=True)
        
        if config.num_channels == 1:
            axes = [axes]
        
        colors = plt.cm.tab10(np.linspace(0, 1, config.num_channels))
        
        for ch, ax in enumerate(axes):
            # Plot waveform
            channel_data = data[:, ch].astype(np.float32)
            # Normalize to mV (assuming 3.3V ref, 12-bit ADC)
            voltage = (channel_data / 4095.0) * 3300.0
            
            ax.plot(time_axis, voltage, color=colors[ch], linewidth=0.8)
            
            # Mark arrival time
            if not np.isnan(arrival_times[ch]):
                ax.axvline(arrival_times[ch], color='r', linestyle='--', 
                           alpha=0.5, label=f"Arrival: {arrival_times[ch]:.1f}μs")
            
            ax.set_ylabel(f"Ch {ch}\n(mV)", fontsize=9)
            ax.grid(True, alpha=0.3)
            ax.legend(loc='upper right', fontsize=7)
            
            # Offset y-axis for clarity
            y_offset = ch * 500  # 500mV offset per channel
            ax.set_ylim(-100 + y_offset, 400 + y_offset)
        
        axes[-1].set_xlabel("Time (μs)", fontsize=10)
        fig.suptitle(f"Array Acquisition - Focus {config.focus_depth_mm}mm, "
                     f"{config.focus_angle_deg}°\n"
                     f"Sample rate: {config.sample_rate/1e6:.1f} MSa/s", 
                     fontsize=12)
        
        plt.tight_layout()
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"\n✓ Plot saved to {filename}")
        plt.close()
    
    def measure_latency(self, iterations: int = 10) -> Dict:
        """Measure fire-to-display latency"""
        print(f"\n{'='*60}")
        print("LATENCY MEASUREMENT")
        print(f"{'='*60}")
        
        latencies = []
        
        for i in range(iterations):
            start = time.perf_counter()
            
            # Quick fire + acquire cycle
            self.arm_acquisition()
            self.fire_element(0)
            self.wait_for_data(timeout=1.0)
            
            end = time.perf_counter()
            latencies.append((end - start) * 1000)  # ms
            
            print(f"  Iteration {i+1}: {latencies[-1]:.1f} ms")
            time.sleep(0.05)
        
        result = {
            "mean_ms": np.mean(latencies),
            "std_ms": np.std(latencies),
            "min_ms": np.min(latencies),
            "max_ms": np.max(latencies)
        }
        
        print(f"\nLatency Statistics:")
        print(f"  Mean: {result['mean_ms']:.1f} ms")
        print(f"  Std:  {result['std_ms']:.1f} ms")
        print(f"  Min:  {result['min_ms']:.1f} ms")
        print(f"  Max:  {result['max_ms']:.1f} ms")
        print(f"{'='*60}")
        
        return result


def main():
    parser = argparse.ArgumentParser(description='Full Pipeline Test')
    parser.add_argument('--port', default='/dev/ttyUSB0', help='Serial port')
    parser.add_argument('--baud', type=int, default=921600, help='Baud rate')
    parser.add_argument('--focus', type=float, default=50.0, help='Focus depth (mm)')
    parser.add_argument('--angle', type=float, default=0.0, help='Focus angle (deg)')
    parser.add_argument('--samples', type=int, default=2048, help='Samples per channel')
    parser.add_argument('--channels', type=int, default=8, help='Number of channels')
    parser.add_argument('--rate', type=int, default=20000000, help='Sample rate (Hz)')
    parser.add_argument('--pitch', type=float, default=0.5, help='Element pitch (mm)')
    parser.add_argument('--plot', default='pipeline_test.png', help='Plot output file')
    parser.add_argument('--latency', action='store_true', help='Measure latency')
    
    args = parser.parse_args()
    
    tester = PipelineTester(port=args.port, baud=args.baud)
    
    if not tester.connect():
        return 1
    
    # Check connection
    if not tester.ping():
        print("✗ Device not responding")
        return 1
    print("✓ Device responding")
    
    try:
        # Run full test
        config = AcquisitionConfig(
            focus_depth_mm=args.focus,
            focus_angle_deg=args.angle,
            samples_per_channel=args.samples,
            num_channels=args.channels,
            sample_rate=args.rate,
            element_pitch_mm=args.pitch
        )
        
        success = tester.run_full_test(config, plot_file=args.plot)
        
        if success and args.latency:
            tester.measure_latency()
        
        return 0 if success else 1
        
    finally:
        tester.disconnect()


if __name__ == '__main__':
    exit(main())
