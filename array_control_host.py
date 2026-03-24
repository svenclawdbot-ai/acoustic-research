#!/usr/bin/env python3
"""
array_control_host.py - Host interface for ESP32 array control firmware

Usage:
    python array_control_host.py --port /dev/ttyUSB0 ping
    python array_control_host.py --port COM3 acquire --samples 1024 --focus 50
    python array_control_host.py --port /dev/ttyUSB0 set-focus --depth 30 --angle 15
"""

import serial
import struct
import json
import argparse
import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, Dict, Any
import sys


class ArrayControlInterface:
    """Python interface to ESP32 array control firmware"""
    
    def __init__(self, port: str = '/dev/ttyUSB0', baud: int = 921600, timeout: float = 5.0):
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.ser: Optional[serial.Serial] = None
        
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
            # Wait for ESP32 to boot
            import time
            time.sleep(0.5)
            self.ser.reset_input_buffer()
            return True
        except serial.SerialException as e:
            print(f"Failed to open {self.port}: {e}")
            return False
    
    def disconnect(self):
        """Close serial connection"""
        if self.ser:
            self.ser.close()
            self.ser = None
    
    def _send_command(self, cmd: Dict[str, Any]) -> Dict[str, Any]:
        """Send JSON command and receive response"""
        if not self.ser:
            raise RuntimeError("Not connected")
        
        # Send command
        cmd_json = json.dumps(cmd)
        self.ser.write(cmd_json.encode() + b'\n')
        
        # Read response
        response_line = self.ser.readline().decode().strip()
        if not response_line:
            raise TimeoutError("No response from device")
        
        return json.loads(response_line)
    
    def ping(self) -> Dict[str, Any]:
        """Ping the device"""
        return self._send_command({"cmd": "ping"})
    
    def get_status(self) -> Dict[str, Any]:
        """Get device status"""
        return self._send_command({"cmd": "get_status"})
    
    def set_geometry(self, num_elements: int = 8, element_pitch: float = 0.5,
                     element_width: float = 0.4, frequency_mhz: float = 1.5,
                     sound_speed_ms: float = 1540.0) -> Dict[str, Any]:
        """Configure array geometry"""
        return self._send_command({
            "cmd": "set_geometry",
            "num_elements": num_elements,
            "element_pitch": element_pitch,
            "element_width": element_width,
            "center_frequency_mhz": frequency_mhz,
            "sound_speed_ms": sound_speed_ms
        })
    
    def set_focus(self, depth_mm: float, angle_deg: float = 0.0) -> Dict[str, Any]:
        """Set beam focus and steering"""
        return self._send_command({
            "cmd": "set_focus",
            "depth_mm": depth_mm,
            "angle_deg": angle_deg
        })
    
    def fire(self, element_mask: int = 0xFF, pulse_width_us: int = 10) -> Dict[str, Any]:
        """Fire specified elements"""
        return self._send_command({
            "cmd": "fire",
            "element_mask": element_mask,
            "pulse_width_us": pulse_width_us
        })
    
    def acquire(self, samples: int = 1024, num_elements: int = 8,
                focus_depth_mm: float = 0.0, steering_angle_deg: float = 0.0,
                pri_us: int = 1000, averages: int = 1) -> Optional[np.ndarray]:
        """
        Single acquisition with all elements
        
        Returns:
            Array of shape (num_elements, samples) as uint16
        """
        cmd = {
            "cmd": "acquire",
            "samples": samples,
            "num_elements": num_elements,
            "focus_depth_mm": focus_depth_mm,
            "steering_angle_deg": steering_angle_deg,
            "pri_us": pri_us,
            "averages": averages
        }
        
        # Send command
        cmd_json = json.dumps(cmd)
        self.ser.write(cmd_json.encode() + b'\n')
        
        # Read response header
        response_line = self.ser.readline().decode().strip()
        response = json.loads(response_line)
        
        if response.get("status") != "ok":
            print(f"Acquisition failed: {response}")
            return None
        
        # Read binary data
        data_size = response["data_size_bytes"]
        raw_data = self.ser.read(data_size)
        
        if len(raw_data) != data_size:
            print(f"Warning: Expected {data_size} bytes, got {len(raw_data)}")
        
        # Parse as uint16
        num_samples_total = data_size // 2
        data = np.frombuffer(raw_data, dtype=np.uint16)
        
        # Reshape to (num_elements, samples)
        return data.reshape(num_elements, samples)
    
    def start_continuous(self, samples: int = 1024, **kwargs) -> Dict[str, Any]:
        """Start continuous acquisition mode"""
        cmd = {
            "cmd": "start_acquisition",
            "samples": samples,
            **kwargs
        }
        return self._send_command(cmd)
    
    def stop_continuous(self) -> Dict[str, Any]:
        """Stop continuous acquisition"""
        return self._send_command({"cmd": "stop_acquisition"})
    
    def calibrate(self) -> Dict[str, Any]:
        """Run calibration sequence"""
        return self._send_command({"cmd": "calibrate"})
    
    def reset(self) -> Dict[str, Any]:
        """Reset the device"""
        return self._send_command({"cmd": "reset"})


def cmd_ping(args):
    """Ping command handler"""
    iface = ArrayControlInterface(args.port, args.baud)
    if not iface.connect():
        return 1
    
    try:
        resp = iface.ping()
        print(json.dumps(resp, indent=2))
    finally:
        iface.disconnect()
    return 0


def cmd_status(args):
    """Status command handler"""
    iface = ArrayControlInterface(args.port, args.baud)
    if not iface.connect():
        return 1
    
    try:
        resp = iface.get_status()
        print(json.dumps(resp, indent=2))
    finally:
        iface.disconnect()
    return 0


def cmd_geometry(args):
    """Set geometry command handler"""
    iface = ArrayControlInterface(args.port, args.baud)
    if not iface.connect():
        return 1
    
    try:
        resp = iface.set_geometry(
            num_elements=args.elements,
            element_pitch=args.pitch,
            frequency_mhz=args.frequency,
            sound_speed_ms=args.sound_speed
        )
        print(json.dumps(resp, indent=2))
    finally:
        iface.disconnect()
    return 0


def cmd_focus(args):
    """Set focus command handler"""
    iface = ArrayControlInterface(args.port, args.baud)
    if not iface.connect():
        return 1
    
    try:
        resp = iface.set_focus(depth_mm=args.depth, angle_deg=args.angle)
        print(json.dumps(resp, indent=2))
    finally:
        iface.disconnect()
    return 0


def cmd_fire(args):
    """Fire command handler"""
    iface = ArrayControlInterface(args.port, args.baud)
    if not iface.connect():
        return 1
    
    try:
        resp = iface.fire(element_mask=args.mask, pulse_width_us=args.pulse)
        print(json.dumps(resp, indent=2))
    finally:
        iface.disconnect()
    return 0


def cmd_acquire(args):
    """Acquire command handler"""
    iface = ArrayControlInterface(args.port, args.baud)
    if not iface.connect():
        return 1
    
    try:
        data = iface.acquire(
            samples=args.samples,
            num_elements=args.elements,
            focus_depth_mm=args.focus,
            steering_angle_deg=args.angle,
            averages=args.averages
        )
        
        if data is None:
            print("Acquisition failed")
            return 1
        
        print(f"Acquired data shape: {data.shape}")
        print(f"Data range: [{data.min()}, {data.max()}]")
        
        # Save to file if requested
        if args.output:
            np.save(args.output, data)
            print(f"Saved to {args.output}")
        
        # Plot if requested
        if args.plot:
            fig, axes = plt.subplots(args.elements, 1, figsize=(12, 2*args.elements))
            if args.elements == 1:
                axes = [axes]
            
            for i, ax in enumerate(axes):
                ax.plot(data[i])
                ax.set_ylabel(f'Ch{i}')
                ax.grid(True)
            
            plt.xlabel('Sample')
            plt.tight_layout()
            plt.savefig(args.plot)
            print(f"Plot saved to {args.plot}")
            plt.show()
        
    finally:
        iface.disconnect()
    return 0


def cmd_test_sequence(args):
    """Run a test sequence"""
    iface = ArrayControlInterface(args.port, args.baud)
    if not iface.connect():
        return 1
    
    try:
        print("=== Array Control Test Sequence ===\n")
        
        # 1. Ping
        print("1. Pinging device...")
        resp = iface.ping()
        print(f"   Response: {resp}\n")
        
        # 2. Get status
        print("2. Getting status...")
        resp = iface.get_status()
        print(f"   Status: {resp}\n")
        
        # 3. Set geometry
        print("3. Setting geometry (8 elements, 0.5mm pitch)...")
        resp = iface.set_geometry(num_elements=8)
        print(f"   Response: {resp}\n")
        
        # 4. Set focus
        print("4. Setting focus (50mm depth)...")
        resp = iface.set_focus(depth_mm=50, angle_deg=0)
        print(f"   Response: {resp}\n")
        
        # 5. Fire elements
        print("5. Firing all elements...")
        resp = iface.fire(element_mask=0xFF, pulse_width_us=10)
        print(f"   Response: {resp}\n")
        
        # 6. Single acquisition
        print("6. Running single acquisition...")
        data = iface.acquire(samples=512, num_elements=8)
        if data is not None:
            print(f"   Acquired shape: {data.shape}")
            print(f"   Data range: [{data.min()}, {data.max()}]")
        
        print("\n=== Test Complete ===")
        
    finally:
        iface.disconnect()
    return 0


def main():
    parser = argparse.ArgumentParser(
        description='ESP32 Array Control Firmware Host Interface'
    )
    parser.add_argument('--port', default='/dev/ttyUSB0', 
                        help='Serial port (default: /dev/ttyUSB0)')
    parser.add_argument('--baud', type=int, default=921600,
                        help='Baud rate (default: 921600)')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Ping
    ping_parser = subparsers.add_parser('ping', help='Ping device')
    ping_parser.set_defaults(func=cmd_ping)
    
    # Status
    status_parser = subparsers.add_parser('status', help='Get device status')
    status_parser.set_defaults(func=cmd_status)
    
    # Geometry
    geom_parser = subparsers.add_parser('set-geometry', help='Set array geometry')
    geom_parser.add_argument('--elements', type=int, default=8, help='Number of elements')
    geom_parser.add_argument('--pitch', type=float, default=0.5, help='Element pitch (mm)')
    geom_parser.add_argument('--frequency', type=float, default=1.5, help='Center frequency (MHz)')
    geom_parser.add_argument('--sound-speed', type=float, default=1540, help='Sound speed (m/s)')
    geom_parser.set_defaults(func=cmd_geometry)
    
    # Focus
    focus_parser = subparsers.add_parser('set-focus', help='Set beam focus')
    focus_parser.add_argument('--depth', type=float, required=True, help='Focus depth (mm)')
    focus_parser.add_argument('--angle', type=float, default=0.0, help='Steering angle (deg)')
    focus_parser.set_defaults(func=cmd_focus)
    
    # Fire
    fire_parser = subparsers.add_parser('fire', help='Fire elements')
    fire_parser.add_argument('--mask', type=lambda x: int(x, 0), default=0xFF, 
                             help='Element bitmask (default: 0xFF)')
    fire_parser.add_argument('--pulse', type=int, default=10, help='Pulse width (us)')
    fire_parser.set_defaults(func=cmd_fire)
    
    # Acquire
    acq_parser = subparsers.add_parser('acquire', help='Acquire data')
    acq_parser.add_argument('--samples', type=int, default=1024, help='Samples per channel')
    acq_parser.add_argument('--elements', type=int, default=8, help='Number of elements')
    acq_parser.add_argument('--focus', type=float, default=0.0, help='Focus depth (mm)')
    acq_parser.add_argument('--angle', type=float, default=0.0, help='Steering angle (deg)')
    acq_parser.add_argument('--averages', type=int, default=1, help='Number of averages')
    acq_parser.add_argument('-o', '--output', help='Output file (.npy)')
    acq_parser.add_argument('-p', '--plot', help='Plot output file')
    acq_parser.set_defaults(func=cmd_acquire)
    
    # Test sequence
    test_parser = subparsers.add_parser('test', help='Run test sequence')
    test_parser.set_defaults(func=cmd_test_sequence)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
