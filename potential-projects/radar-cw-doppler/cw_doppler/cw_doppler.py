#!/usr/bin/env python3
"""
CW Doppler Radar — Real-Time Acquisition & Processing

Usage:
    python cw_doppler.py --rp-ip 192.168.1.100 --mode baseband
    python cw_doppler.py --rp-ip 192.168.1.100 --mode motion --duration 60

Modes:
    baseband   — 30 MHz direct, desk test (no extra hardware)
    ism24      — 2.4 GHz with external frontend (requires hardware)
    motion     — Real-time motion detection with alarm
    breathing  — Micro-motion / vital signs extraction
"""

import argparse
import sys
import time
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
from collections import deque

from rp_sdr_client import RedPitayaSDR


# ─── Configuration ──────────────────────────────────────────────────────────

DEFAULT_RP_IP = "192.168.1.100"
DEFAULT_RATE_IDX = 2          # 100 kSPS — good balance of BW vs processing
DEFAULT_BLOCK_SIZE = 4096     # Samples per read
DEFAULT_FC_BASEBAND = 30e6    # 30 MHz for direct Red Pitaya tx/rx
DEFAULT_FC_ISM24 = 2.4e9      # 2.4 GHz — external frontend shifts this

# Doppler bands (for 2.4 GHz; scale proportionally for other frequencies)
BAND_BREATHING = (0.1, 0.5)   # Hz — breathing rate
BAND_HEARTBEAT = (0.8, 2.0)   # Hz — heartbeat
BAND_WALKING = (1.0, 20.0)    # Hz — person walking


# ─── Signal Processing ───────────────────────────────────────────────────────

class DopplerProcessor:
    """
    Process I/Q baseband samples for CW Doppler detection.
    """
    
    def __init__(self, fs: float, fft_size: int = 1024, 
                 hop_size: int = 512, hpf_cutoff: float = 0.1):
        self.fs = fs
        self.dt = 1.0 / fs
        self.fft_size = fft_size
        self.hop_size = hop_size
        self.hpf_cutoff = hpf_cutoff
        
        # High-pass filter: remove DC and static clutter
        self._design_hpf()
        
        # State for streaming filter
        self.zi = signal.lfilter_zi(self.b, self.a)
        
        # Spectrogram history
        self.spec_history = deque(maxlen=500)
        
        # Phase history for micro-motion
        self.phase_history = deque(maxlen=int(fs * 30))  # 30 seconds
        
    def _design_hpf(self):
        """Design Butterworth high-pass filter."""
        nyq = self.fs / 2.0
        normalized_cutoff = self.hpf_cutoff / nyq
        
        # For very low cutoff relative to fs, need careful filter design
        if normalized_cutoff < 0.001:
            # Use IIR with low order to avoid instability
            self.b, self.a = signal.butter(2, normalized_cutoff, btype='high')
        else:
            self.b, self.a = signal.butter(4, normalized_cutoff, btype='high')
    
    def process_block(self, iq: np.ndarray) -> dict:
        """
        Process one block of I/Q samples.
        Returns dict with processed data and metrics.
        """
        if len(iq) < self.fft_size:
            return {}
        
        # 1. Remove DC / static clutter with HPF
        filtered, self.zi = signal.lfilter(self.b, self.a, iq, zi=self.zi)
        
        # 2. Compute instantaneous power
        power = np.abs(filtered) ** 2
        
        # 3. FFT for Doppler spectrum
        window = signal.windows.hann(self.fft_size)
        f_bins = np.fft.rfftfreq(self.fft_size, d=self.dt)
        
        # Use overlapping segments for smoother spectrogram
        segments = []
        for i in range(0, len(iq) - self.fft_size, self.hop_size):
            seg = filtered[i:i+self.fft_size] * window
            seg_fft = np.fft.rfft(seg)
            segments.append(np.abs(seg_fft) ** 2)
        
        if segments:
            spectrum = np.mean(segments, axis=0)
        else:
            spectrum = np.zeros(len(f_bins))
        
        # 4. Energy in Doppler bands
        def band_energy(low, high):
            mask = (f_bins >= low) & (f_bins <= high)
            return np.mean(spectrum[mask]) if np.any(mask) else 0.0
        
        result = {
            'f_bins': f_bins,
            'spectrum': spectrum,
            'power_mean': np.mean(power),
            'power_max': np.max(power),
            'energy_breathing': band_energy(*BAND_BREATHING),
            'energy_heartbeat': band_energy(*BAND_HEARTBEAT),
            'energy_walking': band_energy(*BAND_WALKING),
            'raw_iq': filtered,
        }
        
        # 5. Phase for micro-motion (breathing)
        # Unwrapped phase of complex signal
        phase = np.unwrap(np.angle(filtered))
        result['phase'] = phase
        
        # Add to history
        self.spec_history.append(spectrum)
        self.phase_history.extend(phase)
        
        return result
    
    def detect_motion(self, threshold_db: float = 10.0) -> bool:
        """
        Simple motion detector: compare current spectrum to running average.
        Returns True if motion detected.
        """
        if len(self.spec_history) < 10:
            return False
        
        current = self.spec_history[-1]
        baseline = np.mean(list(self.spec_history)[:-5], axis=0)
        
        # Energy ratio in walking band
        f_bins = np.fft.rfftfreq(self.fft_size, d=self.dt)
        walk_mask = (f_bins >= BAND_WALKING[0]) & (f_bins <= BAND_WALKING[1])
        
        current_walk = np.mean(current[walk_mask])
        baseline_walk = np.mean(baseline[walk_mask])
        
        if baseline_walk == 0:
            return current_walk > threshold_db
        
        ratio_db = 10 * np.log10(current_walk / baseline_walk + 1e-12)
        return ratio_db > threshold_db


# ─── Visualization ────────────────────────────────────────────────────────────

class RealTimePlot:
    """
    Matplotlib-based real-time spectrogram and metrics display.
    """
    
    def __init__(self, processor: DopplerProcessor, mode: str = "spectrogram"):
        self.proc = processor
        self.mode = mode
        
        plt.ion()
        self.fig, self.axes = plt.subplots(2, 2, figsize=(12, 8))
        self.fig.suptitle("CW Doppler Radar — Real-Time", fontsize=14)
        
        # Axis 0: Spectrogram
        self.ax_spec = self.axes[0, 0]
        self.im_spec = None
        
        # Axis 1: Current spectrum
        self.ax_spectrum = self.axes[0, 1]
        self.line_spectrum, = self.ax_spectrum.plot([], [], 'b-', lw=1)
        self.ax_spectrum.set_xlabel("Doppler Frequency (Hz)")
        self.ax_spectrum.set_ylabel("Power (dB)")
        self.ax_spectrum.set_xlim(0, 50)
        self.ax_spectrum.set_ylim(-20, 80)
        self.ax_spectrum.grid(True, alpha=0.3)
        
        # Axis 2: Phase (micro-motion)
        self.ax_phase = self.axes[1, 0]
        self.line_phase, = self.ax_phase.plot([], [], 'g-', lw=1)
        self.ax_phase.set_xlabel("Time (s)")
        self.ax_phase.set_ylabel("Phase (rad)")
        self.ax_phase.set_title("Micro-Motion (Breathing)")
        self.ax_phase.grid(True, alpha=0.3)
        
        # Axis 3: Energy bars
        self.ax_energy = self.axes[1, 1]
        self.bars = None
        self.ax_energy.set_ylabel("Energy (dB)")
        self.ax_energy.set_title("Doppler Band Energy")
        
        plt.tight_layout()
        plt.show(block=False)
    
    def update(self, result: dict):
        """Update plots with new processed block."""
        if not result:
            return
        
        # Update spectrogram
        if len(self.proc.spec_history) > 0:
            spec_data = np.array(list(self.proc.spec_history))
            spec_db = 10 * np.log10(spec_data.T + 1e-12)
            
            if self.im_spec is None:
                extent = [0, spec_data.shape[0], 
                         0, self.proc.fs / 2]
                self.im_spec = self.ax_spec.imshow(
                    spec_db, aspect='auto', origin='lower',
                    extent=extent, cmap='viridis', vmin=-20, vmax=60
                )
                self.ax_spec.set_xlabel("Time (frames)")
                self.ax_spec.set_ylabel("Frequency (Hz)")
                self.ax_spec.set_title("Spectrogram")
                plt.colorbar(self.im_spec, ax=self.ax_spec, label="dB")
            else:
                self.im_spec.set_data(spec_db)
                self.im_spec.set_clim(-20, 60)
        
        # Update spectrum
        f_bins = result.get('f_bins', np.array([]))
        spectrum = result.get('spectrum', np.array([]))
        if len(f_bins) > 0 and len(spectrum) > 0:
            spec_db = 10 * np.log10(spectrum + 1e-12)
            # Limit to 0-50 Hz for display
            mask = f_bins <= 50
            self.line_spectrum.set_data(f_bins[mask], spec_db[mask])
        
        # Update phase
        if 'phase' in result:
            phase = result['phase']
            t = np.arange(len(phase)) * self.proc.dt
            self.line_phase.set_data(t, phase)
            self.ax_phase.set_xlim(0, t[-1] if len(t) > 0 else 1)
            if len(phase) > 0:
                self.ax_phase.set_ylim(np.min(phase) - 0.5, np.max(phase) + 0.5)
        
        # Update energy bars
        energies = [
            10 * np.log10(result.get('energy_breathing', 1e-12) + 1e-12),
            10 * np.log10(result.get('energy_heartbeat', 1e-12) + 1e-12),
            10 * np.log10(result.get('energy_walking', 1e-12) + 1e-12),
        ]
        labels = ['Breathing\n(0.1-0.5 Hz)', 'Heartbeat\n(0.8-2 Hz)', 'Walking\n(1-20 Hz)']
        
        if self.bars is None:
            self.bars = self.ax_energy.bar(labels, energies, color=['#2ecc71', '#3498db', '#e74c3c'])
            self.ax_energy.set_ylim(-20, 60)
        else:
            for bar, val in zip(self.bars, energies):
                bar.set_height(val)
        
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="CW Doppler Radar with Red Pitaya")
    parser.add_argument("--rp-ip", default=DEFAULT_RP_IP, help="Red Pitaya IP address")
    parser.add_argument("--mode", choices=["baseband", "ism24", "motion", "breathing"],
                       default="baseband", help="Operating mode")
    parser.add_argument("--fc", type=float, default=None, 
                       help="Carrier frequency in Hz (overrides mode default)")
    parser.add_argument("--rate-idx", type=int, default=DEFAULT_RATE_IDX,
                       help="I/Q rate index: 0=20k, 1=50k, 2=100k, 3=250k, 4=500k, 5=1250k SPS")
    parser.add_argument("--duration", type=float, default=0,
                       help="Run duration in seconds (0 = indefinite)")
    parser.add_argument("--hpf", type=float, default=0.1,
                       help="High-pass filter cutoff in Hz")
    parser.add_argument("--threshold", type=float, default=10.0,
                       help="Motion detection threshold in dB above baseline")
    parser.add_argument("--no-plot", action="store_true",
                       help="Disable real-time plot (text output only)")
    parser.add_argument("--tx-gain", type=int, default=80,
                       help="TX gain (0-100)")
    parser.add_argument("--rx-gain", type=int, default=50,
                       help="RX gain (0-100)")
    
    args = parser.parse_args()
    
    # Determine carrier frequency
    if args.fc is not None:
        fc = args.fc
    elif args.mode == "ism24":
        fc = DEFAULT_FC_ISM24
    else:
        fc = DEFAULT_FC_BASEBAND
    
    # Determine sample rate
    rates = {0: 20e3, 1: 50e3, 2: 100e3, 3: 250e3, 4: 500e3, 5: 1250e3}
    fs = rates.get(args.rate_idx, 100e3)
    
    print(f"\n{'='*60}")
    print(f"  CW Doppler Radar")
    print(f"{'='*60}")
    print(f"  Mode:        {args.mode}")
    print(f"  Carrier:     {fc/1e6:.1f} MHz")
    print(f"  Sample rate: {fs/1e3:.0f} kSPS")
    print(f"  HPF cutoff:  {args.hpf} Hz")
    print(f"  Threshold:   {args.threshold} dB")
    print(f"{'='*60}\n")
    
    # Connect to Red Pitaya
    rp = RedPitayaSDR(args.rp_ip)
    if not rp.connect():
        print("[ERROR] Failed to connect. Check IP and that SDR transceiver is running.")
        sys.exit(1)
    
    try:
        # Configure
        rp.set_sample_rate(args.rate_idx)
        rp.set_tx_freq(fc)
        rp.set_rx_freq(fc)  # Homodyne: rx = tx for CW Doppler
        rp.set_tx_gain(args.tx_gain)
        rp.set_rx_gain(args.rx_gain)
        
        # Start
        rp.start_rx()
        rp.start_tx()
        rp.start_stream()
        
        # Allow PLLs to settle
        time.sleep(0.5)
        
        # Initialize processor
        processor = DopplerProcessor(fs=fs, hpf_cutoff=args.hpf)
        
        # Initialize plot (unless disabled)
        plot = None if args.no_plot else RealTimePlot(processor, mode=args.mode)
        
        # Main loop
        start_time = time.time()
        frame_count = 0
        
        print("[RUN] Acquisition running. Press Ctrl+C to stop.\n")
        
        while True:
            # Check duration
            if args.duration > 0 and (time.time() - start_time) > args.duration:
                break
            
            # Get samples
            samples = rp.get_samples_n(DEFAULT_BLOCK_SIZE, timeout=2.0)
            if len(samples) == 0:
                continue
            
            # Process
            result = processor.process_block(samples)
            frame_count += 1
            
            # Update display
            if plot:
                plot.update(result)
            
            # Motion detection (console output)
            if args.mode == "motion" and frame_count % 10 == 0:
                motion = processor.detect_motion(threshold_db=args.threshold)
                if motion:
                    e_walk = result.get('energy_walking', 0)
                    print(f"[ALERT] Motion detected! Walking band energy: {10*np.log10(e_walk+1e-12):.1f} dB")
                else:
                    print(f"[OK] No motion — baseline stable")
            
            # Breathing mode: show phase stats
            if args.mode == "breathing" and frame_count % 10 == 0:
                e_breath = result.get('energy_breathing', 0)
                e_heart = result.get('energy_heartbeat', 0)
                print(f"[VITALS] Breathing: {10*np.log10(e_breath+1e-12):.1f} dB | "
                      f"Heartbeat: {10*np.log10(e_heart+1e-12):.1f} dB")
            
            # Throttle console output in baseband mode
            if args.mode == "baseband" and frame_count % 20 == 0:
                print(f"[INFO] Frame {frame_count} | Power: {result.get('power_mean', 0):.2e} | "
                      f"Max: {result.get('power_max', 0):.2e}")
    
    except KeyboardInterrupt:
        print("\n[STOP] Interrupted by user")
    
    finally:
        rp.stop_tx()
        rp.stop_rx()
        rp.disconnect()
        
        print(f"\n[SUMMARY] Total frames: {frame_count}")
        print("[DONE] Acquisition complete")
        
        if plot:
            plt.ioff()
            plt.show()


if __name__ == "__main__":
    main()
