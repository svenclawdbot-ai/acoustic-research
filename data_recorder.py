#!/usr/bin/env python3
"""
data_recorder.py - Multi-format data recording for DMA acquisition

Supports:
- HDF5 (recommended for large datasets)
- NumPy (.npz files)
- CSV (for small exports)
- WAV (for audio-like analysis)
- TDMS (LabVIEW/NI compatible)

Usage:
    from data_recorder import DataRecorder
    
    recorder = DataRecorder('session_001.h5')
    recorder.start_recording()
    recorder.add_frame(timestamp, data)  # data: (samples, channels)
    recorder.stop_recording()
"""

import time
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, BinaryIO, Union
from dataclasses import dataclass, asdict
from enum import Enum
import json
import struct

# Optional dependencies - handle gracefully
 try:
    import h5py
    HAS_H5PY = True
except ImportError:
    HAS_H5PY = False

try:
    from nptdms import TdmsWriter, ChannelObject
    HAS_TDMS = True
except ImportError:
    HAS_TDMS = False


class RecordingFormat(Enum):
    """Supported recording formats"""
    HDF5 = "h5"
    NUMPY = "npz"
    CSV = "csv"
    WAV = "wav"
    TDMS = "tdms"
    BINARY = "bin"


@dataclass
class RecordingMetadata:
    """Recording session metadata"""
    session_id: str
    start_time: datetime
    sample_rate: float
    num_channels: int
    channel_names: List[str]
    voltage_range_mv: float = 3300.0
    adc_resolution: int = 12
    notes: str = ""
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        d = asdict(self)
        d['start_time'] = self.start_time.isoformat()
        return d


class DataRecorder:
    """Multi-format data recorder"""
    
    def __init__(self, 
                 filepath: str,
                 format: RecordingFormat = RecordingFormat.HDF5,
                 sample_rate: float = 20_000_000,
                 num_channels: int = 8,
                 compression: str = "gzip"):
        """
        Initialize recorder
        
        Args:
            filepath: Output file path (extension auto-added if missing)
            format: Recording format
            sample_rate: Sample rate in Hz
            num_channels: Number of channels
            compression: Compression algorithm (HDF5 only)
        """
        self.filepath = Path(filepath)
        self.format = format
        self.sample_rate = sample_rate
        self.num_channels = num_channels
        self.compression = compression
        
        # State
        self.is_recording = False
        self.metadata: Optional[RecordingMetadata] = None
        self.file_handle: Optional[BinaryIO] = None
        self.frame_count = 0
        self.total_samples = 0
        
        # Buffer for formats that need it
        self.buffer: List[tuple] = []  # (timestamp, data)
        self.buffer_size = 100  # Frames before write
        
        # Ensure correct extension
        if not self.filepath.suffix:
            self.filepath = self.filepath.with_suffix(f".{format.value}")
    
    def start_recording(self, 
                       session_id: Optional[str] = None,
                       channel_names: Optional[List[str]] = None,
                       notes: str = "") -> bool:
        """
        Start recording session
        
        Returns:
            True if started successfully
        """
        if self.is_recording:
            return False
        
        # Create metadata
        if channel_names is None:
            channel_names = [f"Ch{i}" for i in range(self.num_channels)]
        
        self.metadata = RecordingMetadata(
            session_id=session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            start_time=datetime.now(),
            sample_rate=self.sample_rate,
            num_channels=self.num_channels,
            channel_names=channel_names,
            notes=notes
        )
        
        # Initialize format-specific writer
        success = False
        if self.format == RecordingFormat.HDF5:
            success = self._init_hdf5()
        elif self.format == RecordingFormat.NUMPY:
            success = self._init_numpy()
        elif self.format == RecordingFormat.CSV:
            success = self._init_csv()
        elif self.format == RecordingFormat.WAV:
            success = self._init_wav()
        elif self.format == RecordingFormat.TDMS:
            success = self._init_tdms()
        elif self.format == RecordingFormat.BINARY:
            success = self._init_binary()
        
        if success:
            self.is_recording = True
            self.frame_count = 0
            self.total_samples = 0
        
        return success
    
    def stop_recording(self) -> Optional[dict]:
        """
        Stop recording and close file
        
        Returns:
            Recording statistics or None if not recording
        """
        if not self.is_recording:
            return None
        
        # Flush any remaining data
        self._flush_buffer()
        
        # Close format-specific
        if self.format == RecordingFormat.HDF5:
            self._close_hdf5()
        elif self.format == RecordingFormat.NUMPY:
            self._close_numpy()
        elif self.format == RecordingFormat.CSV:
            self._close_csv()
        elif self.format == RecordingFormat.WAV:
            self._close_wav()
        elif self.format == RecordingFormat.TDMS:
            self._close_tdms()
        elif self.format == RecordingFormat.BINARY:
            self._close_binary()
        
        self.is_recording = False
        
        # Return statistics
        duration = (datetime.now() - self.metadata.start_time).total_seconds()
        return {
            "session_id": self.metadata.session_id,
            "filepath": str(self.filepath),
            "format": self.format.value,
            "frames_recorded": self.frame_count,
            "total_samples": self.total_samples,
            "duration_seconds": duration,
            "sample_rate": self.sample_rate,
            "file_size_mb": self.filepath.stat().st_size / (1024 * 1024)
        }
    
    def add_frame(self, timestamp: float, data: np.ndarray, metadata: Optional[dict] = None):
        """
        Add a frame of data
        
        Args:
            timestamp: Frame timestamp (seconds since epoch or relative)
            data: Array of shape (samples, channels) or (samples,)
            metadata: Optional frame-specific metadata
        """
        if not self.is_recording:
            return
        
        # Ensure 2D
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        
        # Add to buffer
        self.buffer.append((timestamp, data, metadata))
        
        # Write if buffer full
        if len(self.buffer) >= self.buffer_size:
            self._flush_buffer()
    
    def _flush_buffer(self):
        """Write buffered data to file"""
        if not self.buffer:
            return
        
        if self.format == RecordingFormat.HDF5:
            self._write_hdf5_buffer()
        elif self.format == RecordingFormat.NUMPY:
            self._write_numpy_buffer()
        elif self.format == RecordingFormat.CSV:
            self._write_csv_buffer()
        elif self.format == RecordingFormat.WAV:
            self._write_wav_buffer()
        elif self.format == RecordingFormat.TDMS:
            self._write_tdms_buffer()
        elif self.format == RecordingFormat.BINARY:
            self._write_binary_buffer()
        
        self.buffer = []
    
    # ==========================================================================
    # HDF5 Format (Recommended for large datasets)
    # ==========================================================================
    
    def _init_hdf5(self) -> bool:
        """Initialize HDF5 file"""
        if not HAS_H5PY:
            print("Error: h5py not installed. Run: pip install h5py")
            return False
        
        self._h5file = h5py.File(self.filepath, 'w')
        
        # Create datasets
        self._h5_timestamp = self._h5file.create_dataset(
            'timestamps', shape=(0,), maxshape=(None,),
            dtype='float64', compression=self.compression
        )
        
        # One dataset per channel for efficiency
        self._h5_channels = []
        for i in range(self.num_channels):
            ds = self._h5file.create_dataset(
                f'channel_{i}', shape=(0,), maxshape=(None,),
                dtype='uint16', compression=self.compression,
                chunks=(8192,)
            )
            self._h5_channels.append(ds)
        
        # Metadata
        meta_group = self._h5file.create_group('metadata')
        for key, value in self.metadata.to_dict().items():
            if isinstance(value, list):
                meta_group.create_dataset(key, data=np.array(value, dtype='S'))
            else:
                meta_group.attrs[key] = value
        
        return True
    
    def _write_hdf5_buffer(self):
        """Write buffer to HDF5"""
        if not self.buffer:
            return
        
        # Extract data
        timestamps = np.array([b[0] for b in self.buffer])
        
        # Resize and write timestamps
        old_size = self._h5_timestamp.shape[0]
        new_size = old_size + len(timestamps)
        self._h5_timestamp.resize((new_size,))
        self._h5_timestamp[old_size:] = timestamps
        
        # Write each channel
        for ch in range(self.num_channels):
            data_list = [b[1][:, ch] for b in self.buffer if ch < b[1].shape[1]]
            if data_list:
                data = np.concatenate(data_list)
                old_size = self._h5_channels[ch].shape[0]
                new_size = old_size + len(data)
                self._h5_channels[ch].resize((new_size,))
                self._h5_channels[ch][old_size:] = data
        
        self.frame_count += len(self.buffer)
        self.total_samples += sum(b[1].shape[0] for b in self.buffer)
    
    def _close_hdf5(self):
        """Close HDF5 file"""
        if hasattr(self, '_h5file'):
            self._h5file.close()
    
    # ==========================================================================
    # NumPy Format (.npz)
    # ==========================================================================
    
    def _init_numpy(self) -> bool:
        """Initialize NumPy archive"""
        self._np_data = {
            'timestamps': [],
            'metadata': self.metadata.to_dict()
        }
        for i in range(self.num_channels):
            self._np_data[f'channel_{i}'] = []
        return True
    
    def _write_numpy_buffer(self):
        """Buffer for NumPy (actually just store in memory)"""
        for timestamp, data, meta in self.buffer:
            self._np_data['timestamps'].append(timestamp)
            for ch in range(min(self.num_channels, data.shape[1])):
                self._np_data[f'channel_{ch}'].append(data[:, ch])
        
        self.frame_count += len(self.buffer)
        self.total_samples += sum(b[1].shape[0] for b in self.buffer)
    
    def _close_numpy(self):
        """Save NumPy archive"""
        # Convert lists to arrays
        save_dict = {'metadata': json.dumps(self._np_data['metadata'])}
        
        for ch in range(self.num_channels):
            key = f'channel_{ch}'
            if self._np_data[key]:
                save_dict[key] = np.concatenate(self._np_data[key])
        
        if self._np_data['timestamps']:
            save_dict['timestamps'] = np.array(self._np_data['timestamps'])
        
        np.savez_compressed(self.filepath, **save_dict)
    
    # ==========================================================================
    # CSV Format (for small exports)
    # ==========================================================================
    
    def _init_csv(self) -> bool:
        """Initialize CSV file"""
        self.file_handle = open(self.filepath, 'w')
        
        # Write header
        header = ['timestamp'] + self.metadata.channel_names
        self.file_handle.write(','.join(header) + '\n')
        
        return True
    
    def _write_csv_buffer(self):
        """Write CSV buffer"""
        # CSV only supports single-value per row, so we average or take max
        for timestamp, data, meta in self.buffer:
            # Take mean of each channel for this frame
            values = [str(timestamp)]
            for ch in range(min(self.num_channels, data.shape[1])):
                values.append(str(np.mean(data[:, ch])))
            self.file_handle.write(','.join(values) + '\n')
        
        self.file_handle.flush()
        self.frame_count += len(self.buffer)
    
    def _close_csv(self):
        """Close CSV file"""
        if self.file_handle:
            self.file_handle.close()
    
    # ==========================================================================
    # WAV Format (for audio analysis tools)
    # ==========================================================================
    
    def _init_wav(self) -> bool:
        """Initialize WAV file"""
        import wave
        
        # WAV uses 16-bit samples, limit to reasonable rates
        self._wav_sample_rate = min(int(self.sample_rate), 192000)
        self._wav_resample_factor = int(self.sample_rate / self._wav_sample_rate)
        
        self._wav_file = wave.open(str(self.filepath), 'wb')
        self._wav_file.setnchannels(min(self.num_channels, 2))  # Stereo max
        self._wav_file.setsampwidth(2)  # 16-bit
        self._wav_file.setframerate(self._wav_sample_rate)
        
        self._wav_buffer = bytearray()
        
        return True
    
    def _write_wav_buffer(self):
        """Write WAV buffer"""
        import wave
        
        for timestamp, data, meta in self.buffer:
            # Resample and convert to 16-bit
            resampled = data[::self._wav_resample_factor, :min(data.shape[1], 2)]
            
            # Convert ADC (0-4095) to 16-bit signed (-32768 to 32767)
            audio = ((resampled / 4095.0) * 65535 - 32768).astype(np.int16)
            
            # Interleave channels
            if audio.shape[1] == 2:
                interleaved = audio.flatten()
            else:
                interleaved = audio[:, 0]
            
            self._wav_file.writeframes(interleaved.tobytes())
        
        self.frame_count += len(self.buffer)
    
    def _close_wav(self):
        """Close WAV file"""
        if hasattr(self, '_wav_file'):
            self._wav_file.close()
    
    # ==========================================================================
    # TDMS Format (NI LabVIEW compatible)
    # ==========================================================================
    
    def _init_tdms(self) -> bool:
        """Initialize TDMS file"""
        if not HAS_TDMS:
            print("Error: nptdms not installed. Run: pip install nptdms")
            return False
        
        self._tdms_writer = TdmsWriter(self.filepath)
        self._tdms_segments = []
        return True
    
    def _write_tdms_buffer(self):
        """Write TDMS buffer"""
        # TDMS writes segments - collect data
        for ch in range(self.num_channels):
            channel_data = []
            for timestamp, data, meta in self.buffer:
                if ch < data.shape[1]:
                    channel_data.append(data[:, ch])
            
            if channel_data:
                combined = np.concatenate(channel_data)
                channel = ChannelObject(
                    "Group", 
                    self.metadata.channel_names[ch],
                    combined
                )
                self._tdms_segments.append(channel)
        
        self.frame_count += len(self.buffer)
    
    def _close_tdms(self):
        """Close TDMS file"""
        if hasattr(self, '_tdms_writer'):
            with self._tdms_writer:
                self._tdms_writer.write_segment(self._tdms_segments)
    
    # ==========================================================================
    # Binary Format (raw, fast, minimal)
    # ==========================================================================
    
    def _init_binary(self) -> bool:
        """Initialize binary file"""
        self.file_handle = open(self.filepath, 'wb')
        
        # Write header
        header = {
            'magic': b'TQDATA\x00',
            'version': 1,
            'sample_rate': self.sample_rate,
            'num_channels': self.num_channels,
            'start_time': self.metadata.start_time.isoformat()
        }
        
        # Write as JSON followed by null terminator
        header_bytes = json.dumps(header).encode() + b'\x00'
        self.file_handle.write(header_bytes)
        
        return True
    
    def _write_binary_buffer(self):
        """Write binary buffer"""
        for timestamp, data, meta in self.buffer:
            # Write: timestamp (8 bytes double), length (4 bytes uint32), data
            self.file_handle.write(struct.pack('d', timestamp))
            self.file_handle.write(struct.pack('I', data.shape[0]))
            self.file_handle.write(struct.pack('H', data.shape[1]))
            self.file_handle.write(data.astype(np.uint16).tobytes())
        
        self.frame_count += len(self.buffer)
        self.total_samples += sum(b[1].shape[0] for b in self.buffer)
    
    def _close_binary(self):
        """Close binary file"""
        if self.file_handle:
            self.file_handle.close()
    
    # ==========================================================================
    # Static Methods for Reading
    # ==========================================================================
    
    @staticmethod
    def read_hdf5(filepath: str) -> Dict:
        """Read HDF5 file and return data dictionary"""
        if not HAS_H5PY:
            raise ImportError("h5py required")
        
        with h5py.File(filepath, 'r') as f:
            result = {
                'timestamps': f['timestamps'][:],
                'metadata': dict(f['metadata'].attrs)
            }
            
            # Read channels
            ch_idx = 0
            while f'channel_{ch_idx}' in f:
                result[f'channel_{ch_idx}'] = f[f'channel_{ch_idx}'][:]
                ch_idx += 1
            
            return result
    
    @staticmethod
    def read_numpy(filepath: str) -> Dict:
        """Read NumPy archive"""
        data = np.load(filepath)
        result = {'metadata': json.loads(str(data['metadata']))}
        
        for key in data.files:
            if key != 'metadata':
                result[key] = data[key]
        
        return result
    
    @staticmethod
    def read_binary(filepath: str) -> Dict:
        """Read binary format"""
        with open(filepath, 'rb') as f:
            # Read header (JSON until null)
            header_bytes = b''
            while True:
                byte = f.read(1)
                if byte == b'\x00':
                    break
                header_bytes += byte
            
            header = json.loads(header_bytes.decode())
            
            # Read data frames
            timestamps = []
            channel_data = [[] for _ in range(header['num_channels'])]
            
            while True:
                ts_bytes = f.read(8)
                if len(ts_bytes) < 8:
                    break
                
                timestamp = struct.unpack('d', ts_bytes)[0]
                length = struct.unpack('I', f.read(4))[0]
                num_ch = struct.unpack('H', f.read(2))[0]
                
                data = np.frombuffer(f.read(length * num_ch * 2), dtype=np.uint16)
                data = data.reshape(length, num_ch)
                
                timestamps.append(timestamp)
                for ch in range(num_ch):
                    channel_data[ch].append(data[:, ch])
            
            result = {
                'metadata': header,
                'timestamps': np.array(timestamps)
            }
            
            for ch in range(header['num_channels']):
                if channel_data[ch]:
                    result[f'channel_{ch}'] = np.concatenate(channel_data[ch])
            
            return result


# ==========================================================================
# Convenience Functions
# ==========================================================================

def record_session(filepath: str,
                  data_generator,
                  duration: float = 10.0,
                  format: RecordingFormat = RecordingFormat.HDF5,
                  **kwargs) -> dict:
    """
    Convenience function to record a session
    
    Args:
        filepath: Output file path
        data_generator: Generator yielding (timestamp, data) tuples
        duration: Recording duration in seconds
        format: Recording format
        **kwargs: Additional recorder arguments
    
    Returns:
        Recording statistics
    """
    recorder = DataRecorder(filepath, format=format, **kwargs)
    
    if not recorder.start_recording():
        raise RuntimeError("Failed to start recording")
    
    print(f"Recording to {filepath} for {duration} seconds...")
    
    start_time = time.time()
    try:
        for timestamp, data in data_generator:
            recorder.add_frame(timestamp, data)
            
            if time.time() - start_time >= duration:
                break
    except KeyboardInterrupt:
        print("Recording stopped by user")
    
    stats = recorder.stop_recording()
    print(f"Recording complete: {stats}")
    
    return stats


# ==========================================================================
# Example Usage
# ==========================================================================

if __name__ == '__main__':
    # Example: Record simulated data
    
    def simulated_data():
        """Generate simulated ultrasound data"""
        t = 0
        while True:
            # 8 channels, 1000 samples each
            data = np.random.normal(2048, 100, (1000, 8)).astype(np.uint16)
            
            # Add chirp signal to channel 0
            freq = 100e3 + t * 10e3  # Sweeping frequency
            phase = 2 * np.pi * freq * np.arange(1000) / 20e6
            data[:, 0] += (np.sin(phase) * 500).astype(np.uint16)
            
            yield t, data
            t += 0.05
            time.sleep(0.05)
    
    # Record 5 seconds to HDF5
    stats = record_session(
        'test_recording',
        simulated_data(),
        duration=5.0,
        format=RecordingFormat.HDF5,
        sample_rate=20_000_000,
        num_channels=8
    )
    
    print(f"\nRecorded {stats['frames_recorded']} frames")
    print(f"File size: {stats['file_size_mb']:.2f} MB")
