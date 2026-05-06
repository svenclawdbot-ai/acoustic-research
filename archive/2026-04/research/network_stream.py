#!/usr/bin/env python3
"""
network_stream.py - Network streaming for real-time remote display

Uses ZeroMQ for high-performance message passing.
Supports multiple clients, compression, and automatic reconnection.

Architecture:
    Server (ESP32 host) --PUB--▶ Network --SUB--▶ Client(s)
                              
    Or with request/response for control:
    Client --REQ--▶ Server --REP--▶ Client

Usage:
    # Server side
    python network_stream.py server --port /dev/ttyUSB0 --bind tcp://*:5555
    
    # Client side  
    python network_stream.py client --connect tcp://192.168.1.100:5555
    
    # Multiple clients can connect to same server
"""

import sys
import time
import argparse
import json
import struct
import zlib
import threading
import numpy as np
from typing import Optional, Callable, List
from dataclasses import dataclass
from datetime import datetime

import zmq

# PyQtGraph for client display
 try:
    import pyqtgraph as pg
    from pyqtgraph.Qt import QtCore, QtWidgets
    HAS_GUI = True
except ImportError:
    HAS_GUI = False


@dataclass
class StreamConfig:
    """Stream configuration"""
    bind_address: str = "tcp://*:5555"
    connect_address: str = "tcp://localhost:5555"
    sample_rate: float = 20_000_000
    num_channels: int = 8
    chunk_size: int = 1024  # Samples per message
    compression: bool = True
    compression_level: int = 3  # 0-9 (higher = smaller but slower)
    heartbeat_interval: float = 1.0  # Seconds


class StreamMessage:
    """Message format for network streaming"""
    
    MAGIC = b'TQS'  # TurboQuant Stream
    VERSION = 1
    
    # Message types
    TYPE_DATA = 0x01
    TYPE_METADATA = 0x02
    TYPE_HEARTBEAT = 0x03
    TYPE_CONTROL = 0x04
    
    @classmethod
    def pack_data(cls, 
                  timestamp: float,
                  data: np.ndarray,
                  compression: bool = True,
                  compression_level: int = 3) -> bytes:
        """
        Pack data frame into message
        
        Format:
            [3 bytes magic] [1 byte version] [1 byte type] [4 byte flags]
            [8 byte timestamp] [2 byte num_samples] [2 byte num_channels]
            [4 byte data_length] [N bytes data]
        """
        # Ensure contiguous array
        if not data.flags.c_contiguous:
            data = np.ascontiguousarray(data)
        
        # Pack data
        data_bytes = data.astype(np.uint16).tobytes()
        
        # Compress if enabled and beneficial
        flags = 0
        if compression and len(data_bytes) > 100:
            compressed = zlib.compress(data_bytes, compression_level)
            if len(compressed) < len(data_bytes):
                data_bytes = compressed
                flags |= 0x01  # Compression flag
        
        # Build message
        header = struct.pack(
            '<3s B B I d H H I',
            cls.MAGIC,
            cls.VERSION,
            cls.TYPE_DATA,
            flags,
            timestamp,
            data.shape[0],
            data.shape[1],
            len(data_bytes)
        )
        
        return header + data_bytes
    
    @classmethod
    def unpack_data(cls, message: bytes) -> Optional[dict]:
        """Unpack data message"""
        try:
            # Parse header
            magic = message[:3]
            if magic != cls.MAGIC:
                return None
            
            version = message[3]
            if version != cls.VERSION:
                return None
            
            msg_type = message[4]
            if msg_type != cls.TYPE_DATA:
                return None
            
            flags = struct.unpack('<I', message[5:9])[0]
            timestamp = struct.unpack('<d', message[9:17])[0]
            num_samples = struct.unpack('<H', message[17:19])[0]
            num_channels = struct.unpack('<H', message[19:21])[0]
            data_length = struct.unpack('<I', message[21:25])[0]
            
            data_bytes = message[25:25+data_length]
            
            # Decompress if needed
            if flags & 0x01:
                data_bytes = zlib.decompress(data_bytes)
            
            # Convert back to array
            data = np.frombuffer(data_bytes, dtype=np.uint16)
            data = data.reshape(num_samples, num_channels)
            
            return {
                'timestamp': timestamp,
                'data': data,
                'num_samples': num_samples,
                'num_channels': num_channels
            }
        except:
            return None
    
    @classmethod
    def pack_metadata(cls, metadata: dict) -> bytes:
        """Pack metadata message"""
        json_bytes = json.dumps(metadata).encode()
        
        header = struct.pack(
            '<3s B B I',
            cls.MAGIC,
            cls.VERSION,
            cls.TYPE_METADATA,
            len(json_bytes)
        )
        
        return header + json_bytes
    
    @classmethod
    def unpack_metadata(cls, message: bytes) -> Optional[dict]:
        """Unpack metadata message"""
        try:
            magic = message[:3]
            if magic != cls.MAGIC:
                return None
            
            version = message[3]
            msg_type = message[4]
            
            if msg_type != cls.TYPE_METADATA:
                return None
            
            json_length = struct.unpack('<I', message[5:9])[0]
            json_bytes = message[9:9+json_length]
            
            return json.loads(json_bytes.decode())
        except:
            return None
    
    @classmethod
    def pack_heartbeat(cls) -> bytes:
        """Pack heartbeat message"""
        return struct.pack('<3s B B', cls.MAGIC, cls.VERSION, cls.TYPE_HEARTBEAT)
    
    @classmethod
    def pack_control(cls, command: str, params: Optional[dict] = None) -> bytes:
        """Pack control message"""
        data = {'command': command, 'params': params or {}}
        json_bytes = json.dumps(data).encode()
        
        header = struct.pack(
            '<3s B B I',
            cls.MAGIC,
            cls.VERSION,
            cls.TYPE_CONTROL,
            len(json_bytes)
        )
        
        return header + json_bytes


class StreamServer:
    """Network streaming server"""
    
    def __init__(self, config: StreamConfig):
        self.config = config
        self.context = zmq.Context()
        
        # Publisher socket for data
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.setsockopt(zmq.SNDHWM, 10)  # Limit backlog
        self.publisher.bind(config.bind_address)
        
        # REP socket for control
        self.control = self.context.socket(zmq.REP)
        self.control.bind(config.bind_address.replace('5555', '5556'))
        
        self.running = False
        self.clients_connected = 0
        self.frames_sent = 0
        self.bytes_sent = 0
        
        # Statistics
        self.start_time = None
        
    def start(self):
        """Start server"""
        self.running = True
        self.start_time = time.time()
        print(f"Stream server started on {self.config.bind_address}")
        print(f"Control port on {self.config.bind_address.replace('5555', '5556')}")
        
        # Start control thread
        control_thread = threading.Thread(target=self._control_loop)
        control_thread.daemon = True
        control_thread.start()
        
        # Start heartbeat thread
        heartbeat_thread = threading.Thread(target=self._heartbeat_loop)
        heartbeat_thread.daemon = True
        heartbeat_thread.start()
    
    def stop(self):
        """Stop server"""
        self.running = False
        self.publisher.close()
        self.control.close()
        self.context.term()
    
    def send_frame(self, timestamp: float, data: np.ndarray):
        """Send data frame to all clients"""
        message = StreamMessage.pack_data(
            timestamp,
            data,
            self.config.compression,
            self.config.compression_level
        )
        
        self.publisher.send(message, flags=zmq.NOBLOCK)
        
        self.frames_sent += 1
        self.bytes_sent += len(message)
    
    def send_metadata(self, metadata: dict):
        """Send metadata to all clients"""
        message = StreamMessage.pack_metadata(metadata)
        self.publisher.send(message)
    
    def _control_loop(self):
        """Handle control requests"""
        while self.running:
            try:
                # Wait for request with timeout
                if self.control.poll(100):  # 100ms timeout
                    request = self.control.recv()
                    
                    # Parse request
                    # For now, just acknowledge
                    response = {'status': 'ok'}
                    self.control.send_json(response)
            except zmq.ZMQError:
                pass
    
    def _heartbeat_loop(self):
        """Send periodic heartbeats"""
        while self.running:
            message = StreamMessage.pack_heartbeat()
            self.publisher.send(message)
            time.sleep(self.config.heartbeat_interval)
    
    def get_stats(self) -> dict:
        """Get server statistics"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        return {
            'frames_sent': self.frames_sent,
            'bytes_sent': self.bytes_sent,
            'bytes_sent_mb': self.bytes_sent / (1024 * 1024),
            'elapsed_seconds': elapsed,
            'fps': self.frames_sent / elapsed if elapsed > 0 else 0,
            'mbps': (self.bytes_sent * 8 / 1e6) / elapsed if elapsed > 0 else 0
        }


class StreamClient:
    """Network streaming client"""
    
    def __init__(self, config: StreamConfig):
        self.config = config
        self.context = zmq.Context()
        
        # Subscriber socket
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.setsockopt(zmq.RCVHWM, 100)
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, '')  # Subscribe to all
        self.subscriber.connect(config.connect_address)
        
        # REQ socket for control
        self.control = self.context.socket(zmq.REQ)
        control_addr = config.connect_address.replace('5555', '5556')
        self.control.connect(control_addr)
        
        self.running = False
        self.frames_received = 0
        self.bytes_received = 0
        self.last_frame_time = 0
        self.latency_ms = 0
        
        # Callbacks
        self.on_data: Optional[Callable] = None
        self.on_metadata: Optional[Callable] = None
        
    def start(self):
        """Start client receive loop"""
        self.running = True
        print(f"Stream client connected to {self.config.connect_address}")
        
        receive_thread = threading.Thread(target=self._receive_loop)
        receive_thread.daemon = True
        receive_thread.start()
    
    def stop(self):
        """Stop client"""
        self.running = False
        self.subscriber.close()
        self.control.close()
        self.context.term()
    
    def _receive_loop(self):
        """Main receive loop"""
        while self.running:
            try:
                # Receive with timeout
                if self.subscriber.poll(100):
                    message = self.subscriber.recv()
                    
                    # Try to parse as data
                    data = StreamMessage.unpack_data(message)
                    if data:
                        self._handle_data(data)
                        continue
                    
                    # Try metadata
                    metadata = StreamMessage.unpack_metadata(message)
                    if metadata:
                        if self.on_metadata:
                            self.on_metadata(metadata)
                        continue
                    
                    # Heartbeat or unknown
                    # (Just ignore for now)
                    
            except zmq.ZMQError:
                pass
    
    def _handle_data(self, data: dict):
        """Handle received data"""
        self.frames_received += 1
        self.bytes_received += data['data'].nbytes
        
        # Calculate latency
        current_time = time.time()
        if self.last_frame_time > 0:
            self.latency_ms = (current_time - data['timestamp']) * 1000
        self.last_frame_time = current_time
        
        # Call callback
        if self.on_data:
            self.on_data(data['timestamp'], data['data'])
    
    def send_control(self, command: str, params: Optional[dict] = None) -> Optional[dict]:
        """Send control command to server"""
        message = StreamMessage.pack_control(command, params)
        self.control.send(message)
        
        # Wait for response
        if self.control.poll(1000):
            return self.control.recv_json()
        return None
    
    def get_stats(self) -> dict:
        """Get client statistics"""
        return {
            'frames_received': self.frames_received,
            'bytes_received': self.bytes_received,
            'bytes_received_mb': self.bytes_received / (1024 * 1024),
            'latency_ms': self.latency_ms
        }


# ==========================================================================
# GUI Client (PyQtGraph)
# ==========================================================================

if HAS_GUI:
    class StreamClientGUI(QtWidgets.QMainWindow):
        """GUI client for network stream"""
        
        def __init__(self, config: StreamConfig):
            super().__init__()
            self.config = config
            self.client = StreamClient(config)
            self.client.on_data = self.on_data_received
            
            self.init_ui()
            self.client.start()
        
        def init_ui(self):
            """Initialize GUI"""
            self.setWindowTitle(f"TurboQuant Stream Client - {self.config.connect_address}")
            self.setGeometry(100, 100, 1200, 800)
            
            central = QtWidgets.QWidget()
            self.setCentralWidget(central)
            layout = QtWidgets.QVBoxLayout(central)
            
            # Status bar
            status_layout = QtWidgets.QHBoxLayout()
            self.status_label = QtWidgets.QLabel("● Connected")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            status_layout.addWidget(self.status_label)
            
            self.fps_label = QtWidgets.QLabel("FPS: --")
            status_layout.addWidget(self.fps_label)
            
            self.latency_label = QtWidgets.QLabel("Latency: -- ms")
            status_layout.addWidget(self.latency_label)
            
            status_layout.addStretch()
            layout.addLayout(status_layout)
            
            # Plot
            self.plot_widget = pg.GraphicsLayoutWidget()
            layout.addWidget(self.plot_widget)
            
            self.plot = self.plot_widget.addPlot()
            self.plot.showGrid(x=True, y=True, alpha=0.3)
            self.plot.setLabels(left="Amplitude (mV)", bottom="Time (μs)")
            self.plot.setYRange(-500, 500)
            
            # Curves for each channel
            colors = [(255, 255, 0), (0, 255, 255), (255, 0, 255), (0, 255, 0),
                     (255, 128, 0), (128, 128, 255), (255, 192, 203), (200, 200, 200)]
            
            self.curves = []
            for i in range(self.config.num_channels):
                curve = self.plot.plot(pen=pg.mkPen(color=colors[i], width=1.5))
                self.curves.append(curve)
            
            # Update timer
            self.update_timer = QtCore.QTimer()
            self.update_timer.timeout.connect(self.update_display)
            self.update_timer.start(33)  # 30 FPS
            
            self.current_data = None
        
        def on_data_received(self, timestamp: float, data: np.ndarray):
            """Handle incoming data"""
            self.current_data = data
        
        def update_display(self):
            """Update plot"""
            if self.current_data is None:
                return
            
            data = self.current_data
            samples = data.shape[0]
            
            # Time axis
            time_us = np.arange(samples) * (1e6 / self.config.sample_rate)
            
            # Update each channel
            for ch in range(min(self.config.num_channels, data.shape[1])):
                # Convert to mV
                voltage = (data[:, ch].astype(np.float32) / 4095.0) * 3300.0 - 1650.0
                self.curves[ch].setData(time_us, voltage)
            
            # Update stats
            stats = self.client.get_stats()
            self.fps_label.setText(f"FPS: {stats['frames_received']}")
            self.latency_label.setText(f"Latency: {stats['latency_ms']:.1f} ms")
        
        def closeEvent(self, event):
            """Clean up"""
            self.client.stop()
            event.accept()


# ==========================================================================
# Command Line Interface
# ==========================================================================

def run_server(args):
    """Run streaming server"""
    from data_recorder import DataRecorder
    import serial
    
    config = StreamConfig(
        bind_address=args.bind,
        sample_rate=args.sample_rate,
        num_channels=args.channels,
        compression=not args.no_compression
    )
    
    server = StreamServer(config)
    server.start()
    
    # Connect to hardware
    if args.port:
        print(f"Connecting to hardware on {args.port}...")
        ser = serial.Serial(args.port, args.baud, timeout=0.1)
        
        # Initialize DMA (simplified - assumes firmware ready)
        print("Hardware connected")
        
        try:
            while True:
                # Read data from serial (simplified)
                # In reality, you'd parse the protocol properly
                if ser.in_waiting > 0:
                    data = ser.read(ser.in_waiting)
                    # Parse and send...
                
                time.sleep(0.001)
        except KeyboardInterrupt:
            print("\nStopping server...")
    
    # Demo mode - generate synthetic data
    elif args.demo:
        print("Running in demo mode (synthetic data)...")
        t = 0
        
        try:
            while True:
                # Generate synthetic data
                samples = 1024
                data = np.zeros((samples, args.channels), dtype=np.uint16)
                
                for ch in range(args.channels):
                    freq = 100e3 + ch * 10e3
                    phase = 2 * np.pi * freq * np.arange(samples) / args.sample_rate
                    signal = np.sin(phase + t) * 500 + 2048
                    data[:, ch] = signal.astype(np.uint16)
                
                server.send_frame(time.time(), data)
                
                t += 0.05
                time.sleep(0.05)  # 20 FPS
                
                # Print stats every 5 seconds
                if int(time.time()) % 5 == 0:
                    stats = server.get_stats()
                    print(f"\rSent: {stats['frames_sent']} frames, "
                          f"{stats['mbps']:.2f} Mbps", end='', flush=True)
                          
        except KeyboardInterrupt:
            print("\n\nStopping server...")
            stats = server.get_stats()
            print(f"\nTotal: {stats['frames_sent']} frames, "
                  f"{stats['bytes_sent_mb']:.2f} MB")
    
    server.stop()


def run_client(args):
    """Run streaming client"""
    config = StreamConfig(
        connect_address=args.connect,
        sample_rate=args.sample_rate,
        num_channels=args.channels
    )
    
    if args.gui and HAS_GUI:
        # GUI mode
        app = QtWidgets.QApplication(sys.argv)
        pg.setConfigOptions(useOpenGL=True, antialias=False)
        
        window = StreamClientGUI(config)
        window.show()
        
        sys.exit(app.exec())
    else:
        # Console mode
        client = StreamClient(config)
        
        def on_data(timestamp, data):
            print(f"\rReceived: {data.shape}", end='', flush=True)
        
        client.on_data = on_data
        client.start()
        
        try:
            while True:
                time.sleep(1)
                stats = client.get_stats()
                print(f"\rFrames: {stats['frames_received']}, "
                      f"Latency: {stats['latency_ms']:.1f} ms", end='', flush=True)
        except KeyboardInterrupt:
            print("\n\nStopping client...")
            client.stop()


# ==========================================================================
# Main Entry Point
# ==========================================================================

def main():
    parser = argparse.ArgumentParser(description='Network Streaming for DMA')
    subparsers = parser.add_subparsers(dest='mode', help='Operation mode')
    
    # Server mode
    server_parser = subparsers.add_parser('server', help='Run as server')
    server_parser.add_argument('--port', help='Serial port for hardware')
    server_parser.add_argument('--baud', type=int, default=921600)
    server_parser.add_argument('--bind', default='tcp://*:5555',
                              help='Bind address (default: tcp://*:5555)')
    server_parser.add_argument('--demo', action='store_true',
                              help='Generate synthetic data')
    server_parser.add_argument('--no-compression', action='store_true',
                              help='Disable compression')
    server_parser.add_argument('--sample-rate', type=float, default=20e6)
    server_parser.add_argument('--channels', type=int, default=8)
    
    # Client mode
    client_parser = subparsers.add_parser('client', help='Run as client')
    client_parser.add_argument('--connect', default='tcp://localhost:5555',
                              help='Server address (default: tcp://localhost:5555)')
    client_parser.add_argument('--gui', action='store_true',
                              help='Show GUI (requires PyQtGraph)')
    client_parser.add_argument('--sample-rate', type=float, default=20e6)
    client_parser.add_argument('--channels', type=int, default=8)
    
    args = parser.parse_args()
    
    if args.mode == 'server':
        run_server(args)
    elif args.mode == 'client':
        run_client(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
