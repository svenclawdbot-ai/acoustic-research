#!/usr/bin/env python3
"""
realtime_display.py - Real-time waveform visualization for DMA acquisition

High-performance display using PyQtGraph for minimal latency.
Features:
- 8-channel real-time waveform display
- Trigger synchronization indicator
- FPS and latency monitoring
- Measurement cursors
- Configurable timebase and amplitude scaling

Usage:
    python realtime_display.py --port /dev/ttyUSB0
    python realtime_display.py --port COM3 --rate 20 --window 100
"""

import sys
import time
import argparse
import numpy as np
from dataclasses import dataclass
from collections import deque
from typing import Optional, List, Callable

import serial
import json

# PyQtGraph imports
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets


@dataclass
class DisplayConfig:
    """Display configuration"""
    port: str = '/dev/ttyUSB0'
    baud: int = 921600
    sample_rate: float = 20_000_000  # Hz
    num_channels: int = 8
    samples_per_update: int = 2048
    update_rate_hz: float = 20  # Display updates per second
    time_window_us: float = 100  # Time window in microseconds
    y_range_mv: float = 500  # Y-axis range in millivolts
    trigger_channel: int = 0  # Channel to use for trigger display


class DMAInterface:
    """Serial interface to ESP32 DMA acquisition"""
    
    def __init__(self, config: DisplayConfig):
        self.config = config
        self.ser: Optional[serial.Serial] = None
        self.connected = False
        self.last_data: Optional[np.ndarray] = None
        
    def connect(self) -> bool:
        """Connect to ESP32"""
        try:
            self.ser = serial.Serial(
                port=self.config.port,
                baudrate=self.config.baud,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.1  # Short timeout for non-blocking
            )
            time.sleep(0.5)
            self.ser.reset_input_buffer()
            
            # Test connection
            if self.ping():
                self.connected = True
                return True
            return False
        except serial.SerialException as e:
            print(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect"""
        if self.ser:
            self.ser.close()
            self.ser = None
        self.connected = False
    
    def send_command(self, cmd: dict, wait_for_response: bool = True) -> Optional[dict]:
        """Send command and optionally wait for response"""
        if not self.ser:
            return None
        
        try:
            cmd_json = json.dumps(cmd)
            self.ser.write(cmd_json.encode() + b'\n')
            
            if wait_for_response:
                line = self.ser.readline().decode().strip()
                if line:
                    return json.loads(line)
            return None
        except (serial.SerialException, json.JSONDecodeError):
            return None
    
    def ping(self) -> bool:
        """Ping device"""
        response = self.send_command({"cmd": "ping"})
        return response is not None and response.get("status") == "ok"
    
    def init_dma(self) -> bool:
        """Initialize DMA for continuous acquisition"""
        response = self.send_command({
            "cmd": "dma_init",
            "num_channels": self.config.num_channels,
            "samples_per_channel": self.config.samples_per_update,
            "sample_rate": int(self.config.sample_rate),
            "trigger": "soft"
        })
        return response is not None and response.get("status") == "ok"
    
    def start_continuous(self) -> bool:
        """Start continuous acquisition"""
        response = self.send_command({"cmd": "dma_start_continuous"})
        return response is not None and response.get("status") == "ok"
    
    def stop(self):
        """Stop acquisition"""
        self.send_command({"cmd": "dma_stop"}, wait_for_response=False)
    
    def get_status(self) -> Optional[dict]:
        """Get acquisition status"""
        return self.send_command({"cmd": "dma_get_status"})
    
    def read_data(self) -> Optional[np.ndarray]:
        """Read available data"""
        # Request data info
        response = self.send_command({"cmd": "dma_read_data"})
        if not response or response.get("status") != "ok":
            return None
        
        bytes_available = response.get("bytes_available", 0)
        if bytes_available == 0:
            return None
        
        # Read binary data
        data = self.ser.read(bytes_available)
        if len(data) != bytes_available:
            return None
        
        # Convert to samples
        samples = np.frombuffer(data, dtype=np.uint16)
        return samples


class RealtimeDisplay(QtWidgets.QMainWindow):
    """Main application window"""
    
    # Color scheme for channels
    CHANNEL_COLORS = [
        (255, 255, 0),    # Yellow (Ch 0 - trigger)
        (0, 255, 255),    # Cyan
        (255, 0, 255),    # Magenta
        (0, 255, 0),      # Green
        (255, 128, 0),    # Orange
        (128, 128, 255),  # Light Blue
        (255, 192, 203),  # Pink
        (200, 200, 200),  # Gray
    ]
    
    def __init__(self, config: DisplayConfig):
        super().__init__()
        self.config = config
        self.dma = DMAInterface(config)
        
        # Performance tracking
        self.frame_times = deque(maxlen=100)
        self.last_update_time = time.perf_counter()
        self.total_frames = 0
        self.dropped_frames = 0
        
        # Data buffers
        self.channel_data: List[deque] = [
            deque(maxlen=config.samples_per_update * 2) 
            for _ in range(config.num_channels)
        ]
        
        # Trigger tracking
        self.trigger_level = 1000  # ADC counts (~800mV)
        self.last_trigger_time = 0
        
        self.init_ui()
        self.init_timers()
        
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle(f"TurboQuant Real-Time Display - {self.config.port}")
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)
        
        # === Control Panel ===
        control_panel = QtWidgets.QHBoxLayout()
        
        # Connection status
        self.status_label = QtWidgets.QLabel("● Disconnected")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        control_panel.addWidget(self.status_label)
        
        control_panel.addSpacing(20)
        
        # Run/Stop button
        self.run_button = QtWidgets.QPushButton("▶ Run")
        self.run_button.setCheckable(True)
        self.run_button.clicked.connect(self.toggle_acquisition)
        control_panel.addWidget(self.run_button)
        
        # Single button
        self.single_button = QtWidgets.QPushButton("◉ Single")
        self.single_button.clicked.connect(self.single_capture)
        control_panel.addWidget(self.single_button)
        
        control_panel.addSpacing(20)
        
        # Timebase control
        control_panel.addWidget(QtWidgets.QLabel("Timebase:"))
        self.timebase_combo = QtWidgets.QComboBox()
        self.timebase_combo.addItems(["10 μs", "50 μs", "100 μs", "200 μs", "500 μs", "1 ms"])
        self.timebase_combo.setCurrentIndex(2)  # 100 μs default
        self.timebase_combo.currentIndexChanged.connect(self.update_timebase)
        control_panel.addWidget(self.timebase_combo)
        
        control_panel.addSpacing(20)
        
        # Trigger level
        control_panel.addWidget(QtWidgets.QLabel("Trigger:"))
        self.trigger_spin = QtWidgets.QSpinBox()
        self.trigger_spin.setRange(0, 4095)
        self.trigger_spin.setValue(self.trigger_level)
        self.trigger_spin.valueChanged.connect(self.update_trigger)
        control_panel.addWidget(self.trigger_spin)
        
        control_panel.addStretch()
        
        # FPS display
        self.fps_label = QtWidgets.QLabel("FPS: --")
        control_panel.addWidget(self.fps_label)
        
        layout.addLayout(control_panel)
        
        # === Plot Area ===
        self.plot_widget = pg.GraphicsLayoutWidget()
        layout.addWidget(self.plot_widget)
        
        # Create plots for each channel
        self.plots = []
        self.curves = []
        self.trigger_lines = []
        
        for i in range(self.config.num_channels):
            if i == 0:
                plot = self.plot_widget.addPlot(row=i, col=0)
                plot.setLabels(left=f"Ch {i} (mV)")
            else:
                plot = self.plot_widget.addPlot(row=i, col=0)
                plot.setLabels(left=f"Ch {i}")
                plot.setXLink(self.plots[0])  # Link X axis to first plot
            
            plot.showGrid(x=True, y=True, alpha=0.3)
            plot.setYRange(-self.config.y_range_mv, self.config.y_range_mv)
            
            # Curve for waveform
            curve = plot.plot(pen=pg.mkPen(color=self.CHANNEL_COLORS[i], width=1.5))
            self.curves.append(curve)
            
            # Trigger level line (only on trigger channel)
            if i == self.config.trigger_channel:
                trigger_line = pg.InfiniteLine(
                    angle=0, 
                    movable=True,
                    pen=pg.mkPen(color=(255, 0, 0), style=QtCore.Qt.DashLine)
                )
                trigger_line.setValue(self.adc_to_mv(self.trigger_level))
                trigger_line.sigPositionChanged.connect(self.on_trigger_moved)
                plot.addItem(trigger_line)
                self.trigger_lines.append(trigger_line)
            
            self.plots.append(plot)
            
            # Hide X axis labels except for bottom
            if i < self.config.num_channels - 1:
                plot.getAxis('bottom').setStyle(showValues=False)
            else:
                plot.setLabels(bottom="Time (μs)")
        
        # Set initial time window
        self.update_timebase()
        
        # === Statistics Panel ===
        stats_panel = QtWidgets.QHBoxLayout()
        
        self.stats_labels = {
            'samples': QtWidgets.QLabel("Samples: 0"),
            'latency': QtWidgets.QLabel("Latency: -- ms"),
            'rate': QtWidgets.QLabel("Rate: -- MSa/s"),
            'errors': QtWidgets.QLabel("Errors: 0")
        }
        
        for label in self.stats_labels.values():
            stats_panel.addWidget(label)
        
        stats_panel.addStretch()
        layout.addLayout(stats_panel)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
    def init_timers(self):
        """Initialize update timers"""
        # Display update timer
        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(int(1000 / self.config.update_rate_hz))
        
        # Data acquisition timer (faster)
        self.data_timer = QtCore.QTimer()
        self.data_timer.timeout.connect(self.acquire_data)
        self.data_timer.start(5)  # 5ms = 200 Hz polling
        
        # Connect to device
        QtCore.QTimer.singleShot(100, self.connect_device)
        
    def connect_device(self):
        """Connect to ESP32"""
        if self.dma.connect():
            self.status_label.setText(f"● Connected ({self.config.port})")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.statusBar().showMessage("Connected to device")
        else:
            self.status_label.setText("● Connection Failed")
            self.statusBar().showMessage(f"Failed to connect to {self.config.port}")
    
    def toggle_acquisition(self):
        """Start/stop continuous acquisition"""
        if self.run_button.isChecked():
            self.run_button.setText("⏹ Stop")
            self.start_acquisition()
        else:
            self.run_button.setText("▶ Run")
            self.stop_acquisition()
    
    def start_acquisition(self):
        """Start acquisition"""
        if not self.dma.connected:
            self.statusBar().showMessage("Not connected")
            self.run_button.setChecked(False)
            return
        
        # Initialize DMA
        if not self.dma.init_dma():
            self.statusBar().showMessage("DMA init failed")
            self.run_button.setChecked(False)
            return
        
        # Start continuous mode
        if self.dma.start_continuous():
            self.statusBar().showMessage("Acquisition running")
            # Clear buffers
            for buf in self.channel_data:
                buf.clear()
        else:
            self.statusBar().showMessage("Failed to start acquisition")
            self.run_button.setChecked(False)
    
    def stop_acquisition(self):
        """Stop acquisition"""
        self.dma.stop()
        self.statusBar().showMessage("Acquisition stopped")
    
    def single_capture(self):
        """Single capture mode"""
        if not self.dma.connected:
            return
        
        self.stop_acquisition()
        self.run_button.setChecked(False)
        self.run_button.setText("▶ Run")
        
        # TODO: Implement burst mode single capture
        self.statusBar().showMessage("Single capture not implemented yet")
    
    def acquire_data(self):
        """Background data acquisition"""
        if not self.dma.connected or not self.run_button.isChecked():
            return
        
        # Read data if available
        data = self.dma.read_data()
        if data is not None and len(data) > 0:
            # Reshape to channels
            num_samples = len(data) // self.config.num_channels
            if num_samples > 0:
                reshaped = data[:num_samples * self.config.num_channels].reshape(
                    num_samples, self.config.num_channels
                )
                
                # Append to buffers
                for ch in range(self.config.num_channels):
                    self.channel_data[ch].extend(reshaped[:, ch])
                
                # Check for trigger
                self.check_trigger(reshaped)
    
    def check_trigger(self, data: np.ndarray):
        """Check for trigger condition"""
        ch_data = data[:, self.config.trigger_channel]
        
        # Simple rising edge trigger
        crossings = np.where((ch_data[:-1] < self.trigger_level) & 
                            (ch_data[1:] >= self.trigger_level))[0]
        
        if len(crossings) > 0:
            self.last_trigger_time = time.perf_counter()
    
    def update_display(self):
        """Update display (called at display frame rate)"""
        current_time = time.perf_counter()
        dt = current_time - self.last_update_time
        self.last_update_time = current_time
        
        self.frame_times.append(dt)
        self.total_frames += 1
        
        # Calculate FPS
        if len(self.frame_times) > 10:
            avg_dt = np.mean(self.frame_times)
            fps = 1.0 / avg_dt if avg_dt > 0 else 0
            self.fps_label.setText(f"FPS: {fps:.1f}")
        
        # Update plots
        samples_per_window = int(self.config.sample_rate * 
                                  self.config.time_window_us / 1e6)
        
        for ch in range(self.config.num_channels):
            buf = self.channel_data[ch]
            
            if len(buf) >= samples_per_window:
                # Get last N samples
                samples = list(buf)[-samples_per_window:]
                
                # Convert to mV (12-bit ADC, 3.3V ref)
                voltage = np.array(samples) * 3300.0 / 4095.0
                
                # Center around 1.65V (midpoint)
                voltage = voltage - 1650
                
                # Create time axis
                time_us = np.arange(len(voltage)) * (1e6 / self.config.sample_rate)
                
                # Update curve
                self.curves[ch].setData(time_us, voltage)
        
        # Update statistics
        total_samples = sum(len(buf) for buf in self.channel_data)
        self.stats_labels['samples'].setText(f"Samples: {total_samples}")
        
        # Calculate latency if we have trigger info
        if self.last_trigger_time > 0:
            latency_ms = (current_time - self.last_trigger_time) * 1000
            self.stats_labels['latency'].setText(f"Latency: {latency_ms:.1f} ms")
    
    def update_timebase(self):
        """Update timebase from combo box"""
        time_str = self.timebase_combo.currentText()
        
        # Parse time value
        if "μs" in time_str:
            self.config.time_window_us = float(time_str.replace(" μs", ""))
        elif "ms" in time_str:
            self.config.time_window_us = float(time_str.replace(" ms", "")) * 1000
        
        # Update plot ranges
        for plot in self.plots:
            plot.setXRange(0, self.config.time_window_us)
    
    def update_trigger(self, value: int):
        """Update trigger level from spin box"""
        self.trigger_level = value
        for line in self.trigger_lines:
            line.setValue(self.adc_to_mv(value))
    
    def on_trigger_moved(self, line):
        """Handle trigger line being moved"""
        mv = line.value()
        adc = self.mv_to_adc(mv)
        self.trigger_level = int(adc)
        self.trigger_spin.setValue(self.trigger_level)
    
    @staticmethod
    def adc_to_mv(adc_value: int) -> float:
        """Convert ADC counts to millivolts"""
        return (adc_value / 4095.0) * 3300.0 - 1650
    
    @staticmethod
    def mv_to_adc(mv: float) -> int:
        """Convert millivolts to ADC counts"""
        return int(((mv + 1650) / 3300.0) * 4095)
    
    def closeEvent(self, event):
        """Clean up on close"""
        self.dma.stop()
        self.dma.disconnect()
        event.accept()


def main():
    parser = argparse.ArgumentParser(description='Real-time DMA Display')
    parser.add_argument('--port', default='/dev/ttyUSB0', help='Serial port')
    parser.add_argument('--baud', type=int, default=921600, help='Baud rate')
    parser.add_argument('--rate', type=int, default=20, help='Update rate (Hz)')
    parser.add_argument('--window', type=float, default=100, help='Time window (μs)')
    parser.add_argument('--samples', type=int, default=2048, help='Samples per update')
    
    args = parser.parse_args()
    
    # Create config
    config = DisplayConfig(
        port=args.port,
        baud=args.baud,
        update_rate_hz=args.rate,
        time_window_us=args.window,
        samples_per_update=args.samples
    )
    
    # Create application
    app = QtWidgets.QApplication(sys.argv)
    
    # Set PyQtGraph options for performance
    pg.setConfigOptions(
        useOpenGL=True,
        enableExperimental=True,
        antialias=False  # Disable for speed
    )
    
    # Create window
    window = RealtimeDisplay(config)
    window.show()
    
    # Run
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
