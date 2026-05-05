"""
Red Pitaya SDR Transceiver TCP Client
Compatible with Pavel Demin's SDR transceiver bitstream.
"""

import socket
import struct
import numpy as np
import threading
import queue


class RedPitayaSDR:
    """
    TCP client for Red Pitaya SDR transceiver.
    
    Supports both control commands and I/Q streaming.
    Default ports may vary by bitstream version — check Red Pitaya docs.
    """
    
    def __init__(self, ip: str, ctrl_port: int = 1001, data_port: int = 1002):
        self.ip = ip
        self.ctrl_port = ctrl_port
        self.data_port = data_port
        
        self.ctrl_sock = None
        self.data_sock = None
        self._streaming = False
        self._stream_thread = None
        self._iq_queue = queue.Queue(maxsize=1000)
        
    def connect(self) -> bool:
        """Open control and data connections."""
        try:
            self.ctrl_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ctrl_sock.settimeout(5.0)
            self.ctrl_sock.connect((self.ip, self.ctrl_port))
            
            self.data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.data_sock.settimeout(5.0)
            self.data_sock.connect((self.ip, self.data_port))
            
            print(f"[RP-SDR] Connected to {self.ip}:{self.ctrl_port} (ctrl) / {self.data_port} (data)")
            return True
        except Exception as e:
            print(f"[RP-SDR] Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close all connections."""
        self.stop_stream()
        if self.ctrl_sock:
            self.ctrl_sock.close()
        if self.data_sock:
            self.data_sock.close()
        print("[RP-SDR] Disconnected")
    
    def set_tx_freq(self, freq_hz: float):
        """Set TX frequency in Hz."""
        cmd = f"SET_TX_FREQ_HZ {int(freq_hz)}\n".encode()
        self.ctrl_sock.sendall(cmd)
        resp = self.ctrl_sock.recv(1024)
        print(f"[RP-SDR] TX freq: {freq_hz/1e6:.3f} MHz — {resp.decode().strip()}")
    
    def set_rx_freq(self, freq_hz: float):
        """Set RX frequency in Hz."""
        cmd = f"SET_RX_FREQ_HZ {int(freq_hz)}\n".encode()
        self.ctrl_sock.sendall(cmd)
        resp = self.ctrl_sock.recv(1024)
        print(f"[RP-SDR] RX freq: {freq_hz/1e6:.3f} MHz — {resp.decode().strip()}")
    
    def set_sample_rate(self, rate_idx: int):
        """
        Set I/Q sample rate.
        rate_idx mapping (Pavel Demin SDR transceiver):
        0 = 20 kSPS, 1 = 50 kSPS, 2 = 100 kSPS, 
        3 = 250 kSPS, 4 = 500 kSPS, 5 = 1250 kSPS
        """
        rates = {0: 20e3, 1: 50e3, 2: 100e3, 3: 250e3, 4: 500e3, 5: 1250e3}
        cmd = f"SET_RATE {rate_idx}\n".encode()
        self.ctrl_sock.sendall(cmd)
        resp = self.ctrl_sock.recv(1024)
        print(f"[RP-SDR] Rate: {rates.get(rate_idx, 'unknown')/1e3:.0f} kSPS — {resp.decode().strip()}")
    
    def set_tx_gain(self, gain: int):
        """Set TX gain (0-100 or as supported by bitstream)."""
        cmd = f"SET_TX_GAIN {gain}\n".encode()
        self.ctrl_sock.sendall(cmd)
        resp = self.ctrl_sock.recv(1024)
    
    def set_rx_gain(self, gain: int):
        """Set RX gain (0-100 or as supported by bitstream)."""
        cmd = f"SET_RX_GAIN {gain}\n".encode()
        self.ctrl_sock.sendall(cmd)
        resp = self.ctrl_sock.recv(1024)
    
    def start_tx(self):
        """Enable TX."""
        self.ctrl_sock.sendall(b"START_TX\n")
        resp = self.ctrl_sock.recv(1024)
        print(f"[RP-SDR] TX start — {resp.decode().strip()}")
    
    def stop_tx(self):
        """Disable TX."""
        self.ctrl_sock.sendall(b"STOP_TX\n")
        resp = self.ctrl_sock.recv(1024)
    
    def start_rx(self):
        """Enable RX streaming."""
        self.ctrl_sock.sendall(b"START_RX\n")
        resp = self.ctrl_sock.recv(1024)
        print(f"[RP-SDR] RX start — {resp.decode().strip()}")
    
    def stop_rx(self):
        """Disable RX streaming."""
        self.ctrl_sock.sendall(b"STOP_RX\n")
        resp = self.ctrl_sock.recv(1024)
    
    def _read_stream(self, buffer_size: int = 4096):
        """Background thread: read I/Q samples from data socket."""
        # I/Q interleaved int16 = 4 bytes per complex sample
        sample_bytes = 4
        
        while self._streaming:
            try:
                chunk = self.data_sock.recv(buffer_size)
                if not chunk:
                    break
                    
                # Parse interleaved int16 I/Q
                n_samples = len(chunk) // sample_bytes
                if n_samples == 0:
                    continue
                    
                fmt = f"<{n_samples * 2}h"  # little-endian int16
                flat = struct.unpack(fmt, chunk[:n_samples * sample_bytes])
                iq = np.array(flat[0::2]) + 1j * np.array(flat[1::2])
                
                # Non-blocking queue put
                try:
                    self._iq_queue.put_nowait(iq)
                except queue.Full:
                    # Drop oldest if queue full
                    try:
                        self._iq_queue.get_nowait()
                        self._iq_queue.put_nowait(iq)
                    except queue.Empty:
                        pass
                        
            except socket.timeout:
                continue
            except Exception as e:
                print(f"[RP-SDR] Stream error: {e}")
                break
    
    def start_stream(self, buffer_size: int = 4096):
        """Start background I/Q streaming thread."""
        self._streaming = True
        self._stream_thread = threading.Thread(target=self._read_stream, args=(buffer_size,))
        self._stream_thread.daemon = True
        self._stream_thread.start()
        print("[RP-SDR] Stream thread started")
    
    def stop_stream(self):
        """Stop background streaming."""
        self._streaming = False
        if self._stream_thread:
            self._stream_thread.join(timeout=1.0)
        print("[RP-SDR] Stream thread stopped")
    
    def get_samples(self, timeout: float = 1.0) -> np.ndarray:
        """Get a block of I/Q samples from the queue."""
        try:
            return self._iq_queue.get(timeout=timeout)
        except queue.Empty:
            return np.array([], dtype=complex)
    
    def get_samples_n(self, n: int, timeout: float = 5.0) -> np.ndarray:
        """Get exactly N samples (blocks until available)."""
        samples = []
        collected = 0
        while collected < n:
            block = self.get_samples(timeout=timeout)
            if len(block) == 0:
                break
            samples.append(block)
            collected += len(block)
        
        if not samples:
            return np.array([], dtype=complex)
        
        all_samples = np.concatenate(samples)
        return all_samples[:n]
