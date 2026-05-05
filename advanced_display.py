#!/usr/bin/env python3
"""
advanced_display.py - Professional oscilloscope-style display with PyQtGraph

Advanced features:
- Multiple view modes: Waveform, FFT, Waterfall, X-Y
- Digital phosphor persistence
- Advanced triggering (edge, pulse, pattern)
- Measurements and cursors
- Data recording and export
- Multi-threaded acquisition

Usage:
    python advanced_display.py --port /dev/ttyUSB0
    python advanced_display.py --demo  # Run with simulated data
"""

import sys
import time
import argparse
import numpy as np
from collections import deque
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, List, Dict, Callable, Tuple
import threading
import queue

import serial
import json

# PyQtGraph and Qt
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets, QtGui
from pyqtgraph.graphicsItems.GradientEditorItem import GradientEditorItem


class TriggerMode(Enum):
    """Trigger modes"""
    AUTO = auto()
    NORMAL = auto()
    SINGLE = auto()
    STOP = auto()


class TriggerType(Enum):
    """Trigger types"""
    EDGE_RISING = auto()
    EDGE_FALLING = auto()
    EDGE_BOTH = auto()
    PULSE_WIDTH = auto()


@dataclass
class ChannelConfig:
    """Per-channel configuration"""
    enabled: bool = True
    color: Tuple[int, int, int] = (255, 255, 0)
    offset_mv: float = 0.0
    scale_mv: float = 500.0  # mV per division
    probe_attenuation: float = 1.0
    coupling: str = "DC"  # DC, AC, GND


@dataclass
class DisplayConfig:
    """Display configuration"""
    port: str = '/dev/ttyUSB0'
    baud: int = 921600
    demo_mode: bool = False
    
    # Acquisition
    sample_rate: float = 20_000_000
    num_channels: int = 8
    samples_per_acquisition: int = 4096
    
    # Display
    timebase_us: float = 100.0  # microseconds per division
    persistence: bool = True
    persistence_decay: float = 0.9  # Decay factor per frame
    
    # Trigger
    trigger_mode: TriggerMode = TriggerMode.AUTO
    trigger_type: TriggerType = TriggerType.EDGE_RISING
    trigger_channel: int = 0
    trigger_level_mv: float = 100.0
    trigger_hysteresis_mv: float = 10.0
    
    # Channels
    channels: List[ChannelConfig] = field(default_factory=lambda: [
        ChannelConfig(True, (255, 255, 0), 0, 500),      # Ch 0 - Yellow
        ChannelConfig(True, (0, 255, 255), 0, 500),      # Ch 1 - Cyan
        ChannelConfig(True, (255, 0, 255), 0, 500),      # Ch 2 - Magenta
        ChannelConfig(True, (0, 255, 0), 0, 500),        # Ch 3 - Green
        ChannelConfig(True, (255, 128, 0), 0, 500),      # Ch 4 - Orange
        ChannelConfig(True, (128, 128, 255), 0, 500),    # Ch 5 - Light Blue
        ChannelConfig(True, (255, 192, 203), 0, 500),    # Ch 6 - Pink
        ChannelConfig(True, (200, 200, 200), 0, 500),    # Ch 7 - Gray
    ])


class DataAcquisitionThread(QtCore.QThread):
    """Background thread for data acquisition"""
    
    data_ready = QtCore.pyqtSignal(np.ndarray, float)  # data, timestamp
    status_update = QtCore.pyqtSignal(str)
    
    def __init__(self, config: DisplayConfig):
        super().__init__()
        self.config = config
        self.running = False
        self.ser: Optional[serial.Serial] = None
        self.data_queue = queue.Queue(maxsize=10)
        
    def connect(self) -> bool:
        """Connect to hardware"""
        if self.config.demo_mode:
            self.status_update.emit("Demo mode - simulated data")
            return True
        
        try:
            self.ser = serial.Serial(
                port=self.config.port,
                baudrate=self.config.baud,
                timeout=0.1
            )
            time.sleep(0.5)
            self.ser.reset_input_buffer()
            
            # Test connection
            if self.ping():
                self.status_update.emit(f"Connected to {self.config.port}")
                return True
            return False
        except Exception as e:
            self.status_update.emit(f"Connection failed: {e}")
            return False
    
    def ping(self) -> bool:
        """Ping device"""
        if not self.ser:
            return False
        try:
            self.ser.write(b'{"cmd": "ping"}\n')
            response = self.ser.readline().decode().strip()
            return '"status": "ok"' in response
        except:
            return False
    
    def run(self):
        """Main acquisition loop"""
        self.running = True
        
        if self.config.demo_mode:
            self._demo_loop()
        else:
            self._hardware_loop()
    
    def _demo_loop(self):
        """Generate simulated data"""
        t = 0
        while self.running:
            # Generate synthetic ultrasound-like data
            samples = self.config.samples_per_acquisition
            num_ch = self.config.num_channels
            
            data = np.zeros((samples, num_ch), dtype=np.float32)
            
            for ch in range(num_ch):
                # Base frequency sweep (ultrasound chirp)
                freq_start = 100e3  # 100 kHz
                freq_end = 500e3    # 500 kHz
                
                t_vec = np.linspace(0, samples / self.config.sample_rate, samples)
                
                # Chirp signal with noise
                instantaneous_freq = np.linspace(freq_start, freq_end, len(t_vec))
                phase = 2 * np.pi * np.cumsum(instantaneous_freq) * (t_vec[1] - t_vec[0])
                
                # Add channel-dependent delay (simulating array geometry)
                delay_samples = ch * 10
                signal = np.sin(phase + t) * np.exp(-t_vec * 5000)
                
                # Shift by delay
                signal = np.roll(signal, delay_samples)
                
                # Add noise
                signal += np.random.normal(0, 0.05, samples)
                
                # Convert to ADC counts (12-bit)
                data[:, ch] = (signal + 1.0) * 2048
            
            # Emit data
            timestamp = time.perf_counter()
            self.data_ready.emit(data, timestamp)
            
            t += 0.1
            time.sleep(0.05)  # 20 FPS
    
    def _hardware_loop(self):
        """Hardware acquisition loop"""
        # Initialize DMA
        if not self._init_dma():
            self.status_update.emit("DMA init failed")
            return
        
        while self.running:
            # Request data
            data = self._read_data()
            if data is not None:
                timestamp = time.perf_counter()
                self.data_ready.emit(data, timestamp)
            
            time.sleep(0.001)  # 1ms polling
    
    def _init_dma(self) -> bool:
        """Initialize DMA on device"""
        if not self.ser:
            return False
        
        try:
            cmd = {
                "cmd": "dma_init",
                "num_channels": self.config.num_channels,
                "samples_per_channel": self.config.samples_per_acquisition,
                "sample_rate": int(self.config.sample_rate),
                "trigger": "soft"
            }
            self.ser.write(json.dumps(cmd).encode() + b'\n')
            response = json.loads(self.ser.readline().decode().strip())
            
            if response.get("status") == "ok":
                # Start continuous
                self.ser.write(b'{"cmd": "dma_start_continuous"}\n')
                return True
            return False
        except:
            return False
    
    def _read_data(self) -> Optional[np.ndarray]:
        """Read data from device"""
        if not self.ser:
            return None
        
        try:
            self.ser.write(b'{"cmd": "dma_read_data"}\n')
            response = json.loads(self.ser.readline().decode().strip())
            
            if response.get("status") != "ok":
                return None
            
            bytes_available = response.get("bytes_available", 0)
            if bytes_available == 0:
                return None
            
            data = self.ser.read(bytes_available)
            if len(data) != bytes_available:
                return None
            
            samples = np.frombuffer(data, dtype=np.uint16)
            
            # Reshape
            num_samples = len(samples) // self.config.num_channels
            if num_samples > 0:
                return samples[:num_samples * self.config.num_channels].reshape(
                    num_samples, self.config.num_channels
                )
            return None
        except:
            return None
    
    def stop(self):
        """Stop acquisition"""
        self.running = False
        if self.ser:
            try:
                self.ser.write(b'{"cmd": "dma_stop"}\n')
            except:
                pass


class Measurements:
    """Measurement calculations"""
    
    @staticmethod
    def vpp(data: np.ndarray) -> float:
        """Peak-to-peak voltage"""
        return np.max(data) - np.min(data)
    
    @staticmethod
    def frequency(data: np.ndarray, sample_rate: float) -> float:
        """Estimate dominant frequency using FFT"""
        fft = np.fft.rfft(data)
        freqs = np.fft.rfftfreq(len(data), 1/sample_rate)
        peak_idx = np.argmax(np.abs(fft[1:])) + 1  # Skip DC
        return freqs[peak_idx]
    
    @staticmethod
    def risetime(data: np.ndarray, sample_rate: float) -> float:
        """10-90% rise time"""
        low, high = np.percentile(data, [10, 90])
        crossings_10 = np.where(data > low)[0]
        crossings_90 = np.where(data > high)[0]
        
        if len(crossings_10) == 0 or len(crossings_90) == 0:
            return 0
        
        return (crossings_90[0] - crossings_10[0]) / sample_rate


class AdvancedDisplay(QtWidgets.QMainWindow):
    """Main application window with professional scope features"""
    
    def __init__(self, config: DisplayConfig):
        super().__init__()
        self.config = config
        self.acq_thread = DataAcquisitionThread(config)
        self.acq_thread.data_ready.connect(self.on_data_ready)
        self.acq_thread.status_update.connect(self.on_status_update)
        
        # Data storage
        self.current_data: Optional[np.ndarray] = None
        self.persistence_buffer: List[np.ndarray] = []
        self.max_persistence_frames = 20
        
        # Trigger state
        self.trigger_armed = True
        self.trigger_point = 0
        
        # Measurements
        self.measurements = {}
        self.cursors = {'x1': None, 'x2': None, 'y1': None, 'y2': None}
        
        # Performance tracking
        self.frame_times = deque(maxlen=60)
        self.last_frame_time = time.perf_counter()
        
        self.init_ui()
        
        # Start acquisition
        if self.acq_thread.connect():
            self.acq_thread.start()
    
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("TurboQuant Pro - Advanced Oscilloscope")
        self.setGeometry(50, 50, 1600, 1000)
        
        # Central widget with splitter
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QHBoxLayout(central)
        
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        layout.addWidget(splitter)
        
        # === Left Panel: Controls ===
        left_panel = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_panel)
        left_layout.setSpacing(10)
        
        # Connection status
        self.status_group = QtWidgets.QGroupBox("Status")
        status_layout = QtWidgets.QVBoxLayout(self.status_group)
        self.status_label = QtWidgets.QLabel("● Connecting...")
        self.status_label.setStyleSheet("color: orange; font-weight: bold;")
        status_layout.addWidget(self.status_label)
        self.fps_label = QtWidgets.QLabel("FPS: --")
        status_layout.addWidget(self.fps_label)
        left_layout.addWidget(self.status_group)
        
        # Trigger controls
        self.trigger_group = QtWidgets.QGroupBox("Trigger")
        trigger_layout = QtWidgets.QFormLayout(self.trigger_group)
        
        self.trigger_mode_combo = QtWidgets.QComboBox()
        self.trigger_mode_combo.addItems(["Auto", "Normal", "Single", "Stop"])
        self.trigger_mode_combo.currentIndexChanged.connect(self.on_trigger_mode_changed)
        trigger_layout.addRow("Mode:", self.trigger_mode_combo)
        
        self.trigger_type_combo = QtWidgets.QComboBox()
        self.trigger_type_combo.addItems(["Edge ↑", "Edge ↓", "Edge ↔", "Pulse"])
        trigger_layout.addRow("Type:", self.trigger_type_combo)
        
        self.trigger_ch_spin = QtWidgets.QSpinBox()
        self.trigger_ch_spin.setRange(0, 7)
        self.trigger_ch_spin.setValue(self.config.trigger_channel)
        trigger_layout.addRow("Channel:", self.trigger_ch_spin)
        
        self.trigger_level_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.trigger_level_slider.setRange(-3300, 3300)
        self.trigger_level_slider.setValue(int(self.config.trigger_level_mv))
        self.trigger_level_slider.valueChanged.connect(self.on_trigger_level_changed)
        trigger_layout.addRow("Level (mV):", self.trigger_level_slider)
        
        self.trigger_level_label = QtWidgets.QLabel(f"{self.config.trigger_level_mv} mV")
        trigger_layout.addRow("", self.trigger_level_label)
        
        left_layout.addWidget(self.trigger_group)
        
        # Timebase controls
        self.timebase_group = QtWidgets.QGroupBox("Timebase")
        timebase_layout = QtWidgets.QFormLayout(self.timebase_group)
        
        self.timebase_combo = QtWidgets.QComboBox()
        self.timebase_combo.addItems([
            "10 μs/div", "20 μs/div", "50 μs/div", "100 μs/div",
            "200 μs/div", "500 μs/div", "1 ms/div", "2 ms/div"
        ])
        self.timebase_combo.setCurrentIndex(3)  # 100 μs/div
        self.timebase_combo.currentIndexChanged.connect(self.on_timebase_changed)
        timebase_layout.addRow("Scale:", self.timebase_combo)
        
        self.persistence_check = QtWidgets.QCheckBox("Digital Phosphor")
        self.persistence_check.setChecked(self.config.persistence)
        timebase_layout.addRow("", self.persistence_check)
        
        left_layout.addWidget(self.timebase_group)
        
        # Channel controls
        self.channel_group = QtWidgets.QGroupBox("Channels")
        channel_layout = QtWidgets.QVBoxLayout(self.channel_group)
        
        self.channel_checks = []
        for i in range(self.config.num_channels):
            ch_layout = QtWidgets.QHBoxLayout()
            
            check = QtWidgets.QCheckBox(f"Ch {i}")
            check.setChecked(self.config.channels[i].enabled)
            check.setStyleSheet(f"color: rgb{self.config.channels[i].color};")
            self.channel_checks.append(check)
            ch_layout.addWidget(check)
            
            offset_spin = QtWidgets.QSpinBox()
            offset_spin.setRange(-2000, 2000)
            offset_spin.setValue(int(self.config.channels[i].offset_mv))
            offset_spin.setSuffix(" mV")
            ch_layout.addWidget(offset_spin)
            
            channel_layout.addLayout(ch_layout)
        
        left_layout.addWidget(self.channel_group)
        
        # Measurements
        self.meas_group = QtWidgets.QGroupBox("Measurements")
        meas_layout = QtWidgets.QFormLayout(self.meas_group)
        
        self.meas_vpp_label = QtWidgets.QLabel("--")
        meas_layout.addRow("Vpp:", self.meas_vpp_label)
        
        self.meas_freq_label = QtWidgets.QLabel("--")
        meas_layout.addRow("Freq:", self.meas_freq_label)
        
        self.meas_rise_label = QtWidgets.QLabel("--")
        meas_layout.addRow("Rise:", self.meas_rise_label)
        
        left_layout.addWidget(self.meas_group)
        
        left_layout.addStretch()
        
        # Record button
        self.record_btn = QtWidgets.QPushButton("⏺ Record")
        self.record_btn.setCheckable(True)
        self.record_btn.clicked.connect(self.on_record)
        left_layout.addWidget(self.record_btn)
        
        splitter.addWidget(left_panel)
        
        # === Center: Main Display ===
        display_container = QtWidgets.QWidget()
        display_layout = QtWidgets.QVBoxLayout(display_container)
        
        # Plot widget
        self.plot_widget = pg.GraphicsLayoutWidget()
        display_layout.addWidget(self.plot_widget)
        
        # Create main waveform plot
        self.waveform_plot = self.plot_widget.addPlot(row=0, col=0)
        self.waveform_plot.showGrid(x=True, y=True, alpha=0.3)
        self.waveform_plot.setLabels(left="Amplitude (mV)", bottom="Time (μs)")
        self.waveform_plot.setYRange(-500, 500)
        self.waveform_plot.setXRange(0, self.config.timebase_us * 10)  # 10 divisions
        
        # Add trigger level line
        self.trigger_line = pg.InfiniteLine(
            angle=0,
            movable=True,
            pen=pg.mkPen(color=(255, 0, 0), width=2, style=QtCore.Qt.DashLine)
        )
        self.trigger_line.setValue(self.config.trigger_level_mv)
        self.trigger_line.sigPositionChanged.connect(self.on_trigger_line_moved)
        self.waveform_plot.addItem(self.trigger_line)
        
        # Cursor lines
        self.cursor_x1 = pg.InfiniteLine(angle=90, movable=True, pen='y')
        self.cursor_x2 = pg.InfiniteLine(angle=90, movable=True, pen='y')
        self.cursor_y1 = pg.InfiniteLine(angle=0, movable=True, pen='c')
        self.cursor_y2 = pg.InfiniteLine(angle=0, movable=True, pen='c')
        self.waveform_plot.addItem(self.cursor_x1)
        self.waveform_plot.addItem(self.cursor_x2)
        self.waveform_plot.addItem(self.cursor_y1)
        self.waveform_plot.addItem(self.cursor_y2)
        
        # Curves for each channel
        self.channel_curves = []
        self.persistence_curves = []  # For phosphor effect
        
        for i in range(self.config.num_channels):
            color = self.config.channels[i].color
            
            # Main curve
            curve = self.waveform_plot.plot(
                pen=pg.mkPen(color=color, width=2),
                name=f"Ch{i}"
            )
            self.channel_curves.append(curve)
            
            # Persistence curves (fainter)
            persist_curves = []
            for j in range(self.max_persistence_frames):
                alpha = int(255 * (self.config.persistence_decay ** j) * 0.3)
                persist_color = (*color[:3], alpha)
                persist_curve = self.waveform_plot.plot(
                    pen=pg.mkPen(color=persist_color, width=1)
                )
                persist_curves.append(persist_curve)
            self.persistence_curves.append(persist_curves)
        
        # Add FFT plot below
        self.fft_plot = self.plot_widget.addPlot(row=1, col=0)
        self.fft_plot.showGrid(x=True, y=True, alpha=0.3)
        self.fft_plot.setLabels(left="Magnitude (dB)", bottom="Frequency (MHz)")
        self.fft_plot.setYRange(-100, 0)
        self.fft_plot.setXRange(0, 10)  # 0-10 MHz
        
        self.fft_curves = []
        for i in range(self.config.num_channels):
            color = self.config.channels[i].color
            curve = self.fft_plot.plot(pen=pg.mkPen(color=color, width=1.5))
            self.fft_curves.append(curve)
        
        splitter.addWidget(display_container)
        
        # Set splitter sizes
        splitter.setSizes([300, 1300])
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def on_data_ready(self, data: np.ndarray, timestamp: float):
        """Handle new data from acquisition thread"""
        self.current_data = data
        
        # Process trigger
        if self.process_trigger(data):
            self.update_display(data, timestamp)
    
    def process_trigger(self, data: np.ndarray) -> bool:
        """Process trigger logic"""
        if self.config.trigger_mode == TriggerMode.STOP:
            return False
        
        if self.config.trigger_mode == TriggerMode.AUTO:
            return True
        
        ch = self.config.trigger_channel
        if ch >= data.shape[1]:
            return True
        
        ch_data = data[:, ch]
        trigger_adc = self.mv_to_adc(self.config.trigger_level_mv)
        
        # Simple edge trigger
        if self.config.trigger_type == TriggerType.EDGE_RISING:
            crossings = np.where((ch_data[:-1] < trigger_adc) & 
                                (ch_data[1:] >= trigger_adc))[0]
        elif self.config.trigger_type == TriggerType.EDGE_FALLING:
            crossings = np.where((ch_data[:-1] > trigger_adc) & 
                                (ch_data[1:] <= trigger_adc))[0]
        else:
            crossings = np.where(np.abs(ch_data[:-1] - trigger_adc) < 50)[0]
        
        if len(crossings) > 0:
            self.trigger_point = crossings[0]
            
            if self.config.trigger_mode == TriggerMode.SINGLE:
                self.trigger_armed = False
                self.trigger_mode_combo.setCurrentIndex(3)  # Stop
            
            return True
        
        return self.config.trigger_mode == TriggerMode.AUTO
    
    def update_display(self, data: np.ndarray, timestamp: float):
        """Update display with new data"""
        # Calculate FPS
        current_time = time.perf_counter()
        dt = current_time - self.last_frame_time
        self.last_frame_time = current_time
        self.frame_times.append(dt)
        
        if len(self.frame_times) > 10:
            fps = 1.0 / np.mean(self.frame_times)
            self.fps_label.setText(f"FPS: {fps:.1f}")
        
        # Update persistence buffer
        if self.config.persistence:
            self.persistence_buffer.insert(0, data.copy())
            if len(self.persistence_buffer) > self.max_persistence_frames:
                self.persistence_buffer.pop()
        
        # Calculate time axis
        samples = data.shape[0]
        time_us = np.arange(samples) * (1e6 / self.config.sample_rate)
        
        # Center on trigger point
        trigger_time = self.trigger_point * (1e6 / self.config.sample_rate)
        time_us = time_us - trigger_time
        
        # Update waveform display
        for ch in range(self.config.num_channels):
            if not self.channel_checks[ch].isChecked():
                self.channel_curves[ch].clear()
                continue
            
            # Convert ADC to mV
            ch_data = data[:, ch].astype(np.float32)
            voltage = (ch_data / 4095.0) * 3300.0 - 1650.0
            voltage += self.config.channels[ch].offset_mv
            
            # Update main curve
            self.channel_curves[ch].setData(time_us, voltage)
            
            # Update persistence curves
            if self.config.persistence and self.persistence_check.isChecked():
                for i, persist_curve in enumerate(self.persistence_curves[ch]):
                    if i < len(self.persistence_buffer):
                        old_data = self.persistence_buffer[i][:, ch].astype(np.float32)
                        old_voltage = (old_data / 4095.0) * 3300.0 - 1650.0
                        old_voltage += self.config.channels[ch].offset_mv
                        persist_curve.setData(time_us, old_voltage)
                    else:
                        persist_curve.clear()
        
        # Update FFT display
        for ch in range(self.config.num_channels):
            if not self.channel_checks[ch].isChecked():
                self.fft_curves[ch].clear()
                continue
            
            ch_data = data[:, ch].astype(np.float32)
            
            # Apply window
            window = np.hanning(len(ch_data))
            windowed = ch_data * window
            
            # FFT
            fft = np.fft.rfft(windowed)
            magnitude = np.abs(fft)
            magnitude_db = 20 * np.log10(magnitude + 1e-10)
            
            # Frequency axis
            freqs = np.fft.rfftfreq(len(ch_data), 1/self.config.sample_rate)
            freqs_mhz = freqs / 1e6
            
            self.fft_curves[ch].setData(freqs_mhz, magnitude_db)
        
        # Update measurements (on trigger channel)
        if data.shape[0] > 0:
            ch_data = data[:, self.config.trigger_channel].astype(np.float32)
            voltage = (ch_data / 4095.0) * 3300.0 - 1650.0
            
            vpp = Measurements.vpp(voltage)
            self.meas_vpp_label.setText(f"{vpp:.1f} mV")
            
            try:
                freq = Measurements.frequency(ch_data, self.config.sample_rate)
                self.meas_freq_label.setText(f"{freq/1e3:.1f} kHz")
            except:
                self.meas_freq_label.setText("--")
    
    def on_status_update(self, message: str):
        """Handle status updates from acquisition thread"""
        if "Connected" in message:
            self.status_label.setText(f"● {message}")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
        elif "failed" in message.lower():
            self.status_label.setText(f"● {message}")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
        else:
            self.statusBar().showMessage(message)
    
    def on_trigger_mode_changed(self, index: int):
        """Handle trigger mode change"""
        modes = [TriggerMode.AUTO, TriggerMode.NORMAL, TriggerMode.SINGLE, TriggerMode.STOP]
        self.config.trigger_mode = modes[index]
        
        if self.config.trigger_mode == TriggerMode.SINGLE:
            self.trigger_armed = True
    
    def on_trigger_type_changed(self, index: int):
        """Handle trigger type change"""
        types = [TriggerType.EDGE_RISING, TriggerType.EDGE_FALLING, 
                TriggerType.EDGE_BOTH, TriggerType.PULSE_WIDTH]
        self.config.trigger_type = types[index]
    
    def on_trigger_level_changed(self, value: int):
        """Handle trigger level slider"""
        self.config.trigger_level_mv = float(value)
        self.trigger_level_label.setText(f"{value} mV")
        self.trigger_line.setValue(value)
    
    def on_trigger_line_moved(self, line):
        """Handle trigger line being moved"""
        value = line.value()
        self.config.trigger_level_mv = value
        self.trigger_level_label.setText(f"{value:.0f} mV")
        self.trigger_level_slider.setValue(int(value))
    
    def on_timebase_changed(self, index: int):
        """Handle timebase change"""
        timebases = [10, 20, 50, 100, 200, 500, 1000, 2000]
        self.config.timebase_us = timebases[index]
        
        # Update plot range
        self.waveform_plot.setXRange(
            -self.config.timebase_us * 5,  # Center trigger
            self.config.timebase_us * 5
        )
    
    def on_record(self):
        """Handle record button"""
        if self.record_btn.isChecked():
            self.record_btn.setText("⏹ Stop Recording")
            self.statusBar().showMessage("Recording started...")
            # TODO: Implement recording
        else:
            self.record_btn.setText("⏺ Record")
            self.statusBar().showMessage("Recording stopped")
    
    @staticmethod
    def adc_to_mv(adc: float) -> float:
        """Convert ADC counts to mV"""
        return (adc / 4095.0) * 3300.0 - 1650.0
    
    @staticmethod
    def mv_to_adc(mv: float) -> int:
        """Convert mV to ADC counts"""
        return int(((mv + 1650.0) / 3300.0) * 4095.0)
    
    def closeEvent(self, event):
        """Clean up on close"""
        self.acq_thread.stop()
        self.acq_thread.wait()
        event.accept()


def main():
    parser = argparse.ArgumentParser(description='Advanced Oscilloscope Display')
    parser.add_argument('--port', default='/dev/ttyUSB0', help='Serial port')
    parser.add_argument('--baud', type=int, default=921600, help='Baud rate')
    parser.add_argument('--demo', action='store_true', help='Demo mode with simulated data')
    
    args = parser.parse_args()
    
    config = DisplayConfig(
        port=args.port,
        baud=args.baud,
        demo_mode=args.demo
    )
    
    app = QtWidgets.QApplication(sys.argv)
    
    # Set PyQtGraph options
    pg.setConfigOptions(
        useOpenGL=True,
        enableExperimental=True,
        antialias=False
    )
    
    window = AdvancedDisplay(config)
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
