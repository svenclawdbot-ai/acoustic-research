#!/usr/bin/env python3
"""
turboquant.py - Unified launcher for TurboQuant acquisition system

Central command-line interface for:
- Firmware flashing and configuration
- Data acquisition and recording
- Real-time visualization
- Network streaming
- Data analysis and export

Usage:
    turboquant --help
    
    # Device management
    turboquant device scan
    turboquant device flash --port /dev/ttyUSB0
    turboquant device info
    
    # Acquisition
    turboquant acquire --duration 60 --output session.h5
    turboquant acquire --stream --bind tcp://*:5555
    
    # Visualization
    turboquant display --mode basic
    turboquant display --mode advanced --port /dev/ttyUSB0
    
    # Recording
    turboquant record --duration 300 --format hdf5
    
    # Streaming
    turboquant stream server --port /dev/ttyUSB0
    turboquant stream client --connect tcp://192.168.1.100:5555
    
    # Analysis
    turboquant analyze recording.h5 --spectrogram
    turboquant analyze recording.h5 --export csv
"""

import sys
import os
import argparse
import subprocess
import json
import time
from pathlib import Path
from typing import Optional, List, Dict
from dataclasses import dataclass

# Add workspace to path for imports
sys.path.insert(0, str(Path(__file__).parent))


@dataclass
class SystemConfig:
    """System configuration"""
    workspace_dir: Path = Path(__file__).parent
    default_port: str = "/dev/ttyUSB0"
    default_baud: int = 921600
    default_sample_rate: float = 20_000_000
    default_channels: int = 8


class Colors:
    """Terminal colors"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_banner():
    """Print application banner"""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ████████╗██╗   ██╗██████╗ ███████╗ ██████╗  ██████╗ ██╗   ██╗║
║   ╚══██╔══╝██║   ██║██╔══██╗██╔════╝██╔═══██╗██╔═══██╗██║   ██║║
║      ██║   ██║   ██║██████╔╝█████╗  ██║   ██║██║   ██║██║   ██║║
║      ██║   ██║   ██║██╔══██╗██╔══╝  ██║   ██║██║   ██║██║   ██║║
║      ██║   ╚██████╔╝██║  ██║██║     ╚██████╔╝╚██████╔╝╚██████╔╝║
║      ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝      ╚═════╝  ╚═════╝  ╚═════╝ ║
║                                                               ║
║              High-Speed Ultrasound Acquisition                 ║
╚═══════════════════════════════════════════════════════════════╝{Colors.END}
"""
    print(banner)


def print_status(message: str, status: str = "info"):
    """Print status message with color"""
    colors = {
        "info": Colors.BLUE,
        "success": Colors.GREEN,
        "warning": Colors.YELLOW,
        "error": Colors.RED,
        "header": Colors.HEADER
    }
    color = colors.get(status, Colors.END)
    print(f"{color}[{status.upper()}]{Colors.END} {message}")


def run_command(cmd: List[str], description: str = "") -> bool:
    """Run shell command with error handling"""
    if description:
        print_status(description, "info")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print_status(f"Command failed: {e}", "error")
        if e.stderr:
            print(e.stderr)
        return False
    except FileNotFoundError:
        print_status(f"Command not found: {cmd[0]}", "error")
        return False


def find_serial_ports() -> List[str]:
    """Find available serial ports"""
    ports = []
    
    # Linux
    import glob
    ports.extend(glob.glob('/dev/ttyUSB*'))
    ports.extend(glob.glob('/dev/ttyACM*'))
    
    # macOS
    ports.extend(glob.glob('/dev/tty.usbserial*'))
    ports.extend(glob.glob('/dev/tty.SLAB_USB*'))
    
    return sorted(ports)


# ==========================================================================
# Device Commands
# ==========================================================================

def cmd_device_scan(args):
    """Scan for connected devices"""
    print_status("Scanning for devices...", "header")
    
    ports = find_serial_ports()
    
    if not ports:
        print_status("No serial ports found", "warning")
        print("\nTroubleshooting:")
        print("  - Check USB cable connection")
        print("  - Verify ESP32 is powered on")
        print("  - Run with sudo if permission denied")
        return 1
    
    print(f"\n{Colors.BOLD}Found {len(ports)} serial port(s):{Colors.END}")
    for i, port in enumerate(ports, 1):
        print(f"  {i}. {port}")
        
        # Try to identify device
        try:
            import serial
            ser = serial.Serial(port, 921600, timeout=0.5)
            ser.write(b'{"cmd": "ping"}\n')
            response = ser.readline().decode().strip()
            if '"status": "ok"' in response:
                print(f"     {Colors.GREEN}✓ TurboQuant device detected{Colors.END}")
            ser.close()
        except:
            pass
    
    print(f"\nUse --port to specify device (e.g., --port {ports[0]})")
    return 0


def cmd_device_flash(args):
    """Flash firmware to device"""
    print_status("Flashing firmware...", "header")
    
    port = args.port or "/dev/ttyUSB0"
    
    # Check if esptool is available
    result = subprocess.run(['which', 'esptool.py'], capture_output=True)
    if result.returncode != 0:
        print_status("esptool.py not found. Install with: pip install esptool", "error")
        return 1
    
    # Flash commands
    commands = [
        # Erase flash
        ['esptool.py', '--port', port, 'erase_flash'],
        # Flash firmware
        ['esptool.py', '--port', port, '--baud', '921600', 
         'write_flash', '-z', '0x1000', 'build/array_control_firmware.bin'],
    ]
    
    for cmd in commands:
        if not run_command(cmd):
            return 1
    
    print_status("Firmware flashed successfully!", "success")
    print(f"\nReset the device and run: turboquant device info --port {port}")
    return 0


def cmd_device_info(args):
    """Get device information"""
    import serial
    
    port = args.port or "/dev/ttyUSB0"
    
    print_status(f"Connecting to {port}...", "info")
    
    try:
        ser = serial.Serial(port, 921600, timeout=2)
        time.sleep(0.5)
        
        # Send ping
        ser.write(b'{"cmd": "ping"}\n')
        response = ser.readline().decode().strip()
        
        if '"status": "ok"' in response:
            print_status("Device responding", "success")
            
            # Get status
            ser.write(b'{"cmd": "get_status"}\n')
            status = ser.readline().decode().strip()
            print(f"\n{Colors.BOLD}Device Status:{Colors.END}")
            print(json.dumps(json.loads(status), indent=2))
            
            # Get DMA status
            ser.write(b'{"cmd": "dma_get_status"}\n')
            dma_status = ser.readline().decode().strip()
            print(f"\n{Colors.BOLD}DMA Status:{Colors.END}")
            print(json.dumps(json.loads(dma_status), indent=2))
            
        else:
            print_status("Device not responding correctly", "error")
            print(f"Response: {response}")
            
        ser.close()
        return 0
        
    except Exception as e:
        print_status(f"Connection failed: {e}", "error")
        return 1


# ==========================================================================
# Acquisition Commands
# ==========================================================================

def cmd_acquire(args):
    """Run acquisition with recording"""
    from data_recorder import DataRecorder, RecordingFormat
    import serial
    import json
    
    port = args.port or "/dev/ttyUSB0"
    duration = args.duration or 60
    output = args.output or f"acquisition_{time.strftime('%Y%m%d_%H%M%S')}.h5"
    
    print_status(f"Starting acquisition: {duration}s -> {output}", "header")
    
    # Determine format from extension
    format_map = {
        '.h5': RecordingFormat.HDF5,
        '.npz': RecordingFormat.NUMPY,
        '.csv': RecordingFormat.CSV,
        '.wav': RecordingFormat.WAV,
        '.tdms': RecordingFormat.TDMS,
        '.bin': RecordingFormat.BINARY
    }
    
    ext = Path(output).suffix.lower()
    rec_format = format_map.get(ext, RecordingFormat.HDF5)
    
    # Setup recorder
    recorder = DataRecorder(
        output,
        format=rec_format,
        sample_rate=args.sample_rate or 20_000_000,
        num_channels=args.channels or 8
    )
    
    if not recorder.start_recording():
        print_status("Failed to start recording", "error")
        return 1
    
    # Connect to hardware
    try:
        ser = serial.Serial(port, 921600, timeout=0.1)
        print_status("Hardware connected", "success")
        
        # Initialize and start DMA
        ser.write(json.dumps({
            "cmd": "dma_init",
            "num_channels": args.channels or 8,
            "samples_per_channel": 1024,
            "sample_rate": int(args.sample_rate or 20_000_000),
            "trigger": "soft"
        }).encode() + b'\n')
        
        ser.write(b'{"cmd": "dma_start_continuous"}\n')
        print_status("DMA acquisition started", "info")
        
        # Acquisition loop
        start_time = time.time()
        frames = 0
        
        print(f"\n{Colors.BOLD}Recording... Press Ctrl+C to stop early{Colors.END}\n")
        
        try:
            while time.time() - start_time < duration:
                # Request data
                ser.write(b'{"cmd": "dma_read_data"}\n')
                response_line = ser.readline().decode().strip()
                
                if response_line:
                    try:
                        response = json.loads(response_line)
                        if response.get("status") == "ok":
                            bytes_avail = response.get("bytes_available", 0)
                            if bytes_avail > 0:
                                data = ser.read(bytes_avail)
                                if len(data) == bytes_avail:
                                    samples = np.frombuffer(data, dtype=np.uint16)
                                    num_ch = args.channels or 8
                                    samples_per_ch = len(samples) // num_ch
                                    
                                    if samples_per_ch > 0:
                                        reshaped = samples[:samples_per_ch * num_ch].reshape(
                                            samples_per_ch, num_ch
                                        )
                                        recorder.add_frame(time.time(), reshaped)
                                        frames += 1
                                        
                                        # Progress update
                                        elapsed = time.time() - start_time
                                                percent = (elapsed / duration) * 100
                                        print(f"\r[{percent:5.1f}%] Frames: {frames}, "
                                              f"Time: {elapsed:.1f}s", end='', flush=True)
                    except json.JSONDecodeError:
                        pass
                        
                time.sleep(0.001)
                
        except KeyboardInterrupt:
            print("\n\nStopping...")
        
        # Cleanup
        ser.write(b'{"cmd": "dma_stop"}\n')
        ser.close()
        
        stats = recorder.stop_recording()
        
        print(f"\n{Colors.GREEN}{Colors.BOLD}Recording complete!{Colors.END}")
        print(f"  Frames: {stats['frames_recorded']}")
        print(f"  Duration: {stats['duration_seconds']:.1f}s")
        print(f"  File size: {stats['file_size_mb']:.2f} MB")
        print(f"  Output: {output}")
        
        return 0
        
    except Exception as e:
        print_status(f"Acquisition failed: {e}", "error")
        recorder.stop_recording()
        return 1


# ==========================================================================
# Display Commands
# ==========================================================================

def cmd_display(args):
    """Launch visualization"""
    mode = args.mode or "basic"
    port = args.port or "/dev/ttyUSB0"
    
    scripts = {
        'basic': 'realtime_display.py',
        'advanced': 'advanced_display.py',
        'demo': 'advanced_display.py'
    }
    
    script = scripts.get(mode)
    if not script:
        print_status(f"Unknown mode: {mode}", "error")
        print(f"Available modes: {', '.join(scripts.keys())}")
        return 1
    
    print_status(f"Launching {mode} display...", "header")
    
    cmd = [sys.executable, script]
    
    if mode == 'demo':
        cmd.append('--demo')
    else:
        cmd.extend(['--port', port])
    
    try:
        subprocess.run(cmd)
        return 0
    except KeyboardInterrupt:
        return 0


# ==========================================================================
# Stream Commands
# ==========================================================================

def cmd_stream_server(args):
    """Run streaming server"""
    print_status("Starting streaming server...", "header")
    
    cmd = [
        sys.executable, 'network_stream.py',
        'server',
        '--bind', args.bind or 'tcp://*:5555'
    ]
    
    if args.port:
        cmd.extend(['--port', args.port])
    if args.demo:
        cmd.append('--demo')
    
    try:
        subprocess.run(cmd)
        return 0
    except KeyboardInterrupt:
        return 0


def cmd_stream_client(args):
    """Run streaming client"""
    print_status("Starting streaming client...", "header")
    
    cmd = [
        sys.executable, 'network_stream.py',
        'client',
        '--connect', args.connect or 'tcp://localhost:5555'
    ]
    
    if args.gui:
        cmd.append('--gui')
    
    try:
        subprocess.run(cmd)
        return 0
    except KeyboardInterrupt:
        return 0


# ==========================================================================
# Analysis Commands
# ==========================================================================

def cmd_analyze(args):
    """Analyze recorded data"""
    from data_analysis import analyze_file, generate_spectrogram
    
    input_file = args.input
    
    if not Path(input_file).exists():
        print_status(f"File not found: {input_file}", "error")
        return 1
    
    print_status(f"Analyzing {input_file}...", "header")
    
    if args.spectrogram:
        output = args.output or input_file.replace('.h5', '_spectrogram.png')
        print_status("Generating spectrogram...", "info")
        generate_spectrogram(input_file, output, channel=args.channel or 0)
        print_status(f"Saved to {output}", "success")
    
    if args.export:
        output = args.output or input_file.replace('.h5', f'.{args.export}')
        print_status(f"Exporting to {args.export}...", "info")
        # Implementation in data_analysis.py
        print_status(f"Saved to {output}", "success")
    
    if args.info:
        print_status("File information:", "info")
        info = analyze_file(input_file)
        print(json.dumps(info, indent=2))
    
    return 0


# ==========================================================================
# Main Entry Point
# ==========================================================================

def main():
    parser = argparse.ArgumentParser(
        description='TurboQuant Unified Launcher',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    turboquant device scan
    turboquant acquire --duration 60 --output session.h5
    turboquant display --mode advanced
    turboquant stream server --demo
    turboquant analyze recording.h5 --spectrogram
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Device commands
    device_parser = subparsers.add_parser('device', help='Device management')
    device_subparsers = device_parser.add_subparsers(dest='device_cmd')
    
    device_scan = device_subparsers.add_parser('scan', help='Scan for devices')
    
    device_flash = device_subparsers.add_parser('flash', help='Flash firmware')
    device_flash.add_argument('--port', help='Serial port')
    
    device_info = device_subparsers.add_parser('info', help='Device information')
    device_info.add_argument('--port', help='Serial port')
    
    # Acquire command
    acquire_parser = subparsers.add_parser('acquire', help='Run acquisition')
    acquire_parser.add_argument('--port', help='Serial port')
    acquire_parser.add_argument('--duration', '-d', type=float, help='Duration in seconds')
    acquire_parser.add_argument('--output', '-o', help='Output file')
    acquire_parser.add_argument('--sample-rate', type=float, default=20e6)
    acquire_parser.add_argument('--channels', '-c', type=int, default=8)
    
    # Display command
    display_parser = subparsers.add_parser('display', help='Launch visualization')
    display_parser.add_argument('--mode', choices=['basic', 'advanced', 'demo'], 
                                default='basic', help='Display mode')
    display_parser.add_argument('--port', help='Serial port')
    
    # Stream command
    stream_parser = subparsers.add_parser('stream', help='Network streaming')
    stream_subparsers = stream_parser.add_subparsers(dest='stream_cmd')
    
    stream_server = stream_subparsers.add_parser('server', help='Streaming server')
    stream_server.add_argument('--port', help='Serial port (for hardware)')
    stream_server.add_argument('--bind', default='tcp://*:5555', help='Bind address')
    stream_server.add_argument('--demo', action='store_true', help='Demo mode')
    
    stream_client = stream_subparsers.add_parser('client', help='Streaming client')
    stream_client.add_argument('--connect', default='tcp://localhost:5555', 
                              help='Server address')
    stream_client.add_argument('--gui', action='store_true', help='GUI mode')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze recorded data')
    analyze_parser.add_argument('input', help='Input file')
    analyze_parser.add_argument('--spectrogram', action='store_true', 
                               help='Generate spectrogram')
    analyze_parser.add_argument('--channel', '-ch', type=int, default=0, 
                               help='Channel to analyze')
    analyze_parser.add_argument('--export', choices=['csv', 'wav', 'npz'], 
                               help='Export format')
    analyze_parser.add_argument('--output', '-o', help='Output file')
    analyze_parser.add_argument('--info', action='store_true', 
                               help='Show file information')
    
    # Global flags
    parser.add_argument('--no-banner', action='store_true', help='Skip banner')
    
    args = parser.parse_args()
    
    # Show banner unless suppressed
    if not args.no_banner:
        print_banner()
    
    # Route to command handler
    if args.command == 'device':
        if args.device_cmd == 'scan':
            return cmd_device_scan(args)
        elif args.device_cmd == 'flash':
            return cmd_device_flash(args)
        elif args.device_cmd == 'info':
            return cmd_device_info(args)
        else:
            device_parser.print_help()
            return 1
    
    elif args.command == 'acquire':
        return cmd_acquire(args)
    
    elif args.command == 'display':
        return cmd_display(args)
    
    elif args.command == 'stream':
        if args.stream_cmd == 'server':
            return cmd_stream_server(args)
        elif args.stream_cmd == 'client':
            return cmd_stream_client(args)
        else:
            stream_parser.print_help()
            return 1
    
    elif args.command == 'analyze':
        return cmd_analyze(args)
    
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
