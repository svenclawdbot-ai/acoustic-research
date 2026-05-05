#!/usr/bin/env python3
"""
Polar Scanning Radar — 2D Activity Map

Combines CW Doppler radar with pan-tilt servo scanning to produce
a 2D polar heatmap of motion activity.

Usage:
    python polar_scanner.py --rp-ip 192.168.1.100 --mock-servo
    python polar_scanner.py --rp-ip 192.168.1.100 --scan-step 5 --dwell 200

Hardware:
    - Red Pitaya with CW Doppler setup
    - Pan servo on DIO0_N
    - Tilt servo on DIO1_N (optional, fixed at 90° for 2D scan)
    - External 5V power for servos (share ground with RP)
"""

import argparse
import sys
import time
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge

from rp_sdr_client import RedPitayaSDR
from servo_controller import ServoController, MockServo


class PolarDopplerProcessor:
    """
    CW Doppler processor that stores results per angle.
    """
    
    def __init__(self, fs: float, hpf_cutoff: float = 0.5):
        self.fs = fs
        self.dt = 1.0 / fs
        self.hpf_cutoff = hpf_cutoff
        
        self.b, self.a = signal.butter(2, hpf_cutoff / (fs / 2), btype='high')
        self.zi = signal.lfilter_zi(self.b, self.a)
    
    def process_scan_block(self, iq: np.ndarray) -> dict:
        """Process I/Q block and return motion metrics."""
        if len(iq) < 256:
            return {'motion_detected': False, 'power_db': -100, 
                    'max_doppler_hz': 0, 'confidence': 0}
        
        # High-pass filter
        filtered, self.zi = signal.lfilter(self.b, self.a, iq, zi=self.zi)
        
        # Power
        power = np.mean(np.abs(filtered) ** 2)
        power_db = 10 * np.log10(power + 1e-12)
        
        # Doppler spectrum
        n_fft = min(512, len(iq))
        f_bins = np.fft.rfftfreq(n_fft, d=self.dt)
        spectrum = np.abs(np.fft.rfft(filtered[:n_fft] * signal.windows.hann(n_fft))) ** 2
        
        # Max Doppler in walking band (1-50 Hz)
        walk_mask = (f_bins >= 1.0) & (f_bins <= 50.0)
        if np.any(walk_mask):
            walk_power = np.mean(spectrum[walk_mask])
            walk_db = 10 * np.log10(walk_power + 1e-12)
            max_idx = np.argmax(spectrum[walk_mask])
            max_doppler = f_bins[walk_mask][max_idx]
        else:
            walk_db = -100
            max_doppler = 0
        
        # Motion detection threshold
        motion_detected = walk_db > -50  # Adjustable threshold
        confidence = min(100, max(0, (walk_db + 60) * 2))
        
        return {
            'motion_detected': motion_detected,
            'power_db': power_db,
            'walk_power_db': walk_db,
            'max_doppler_hz': max_doppler,
            'confidence': confidence,
            'spectrum': spectrum,
            'f_bins': f_bins
        }


class PolarMap:
    """
    2D polar activity map with sector-based storage.
    """
    
    def __init__(self, pan_start: float = 0, pan_end: float = 180, 
                 pan_step: float = 5.0, max_range_m: float = 10.0,
                 n_range_bins: int = 20):
        self.angles = np.arange(pan_start, pan_end + pan_step, pan_step)
        self.max_range = max_range_m
        self.n_range_bins = n_range_bins
        
        # Activity per angle (no range info for CW, so just angular sector)
        self.activity = np.zeros(len(self.angles))
        self.power = np.zeros(len(self.angles))
        self.confidence = np.zeros(len(self.angles))
        self.doppler = np.zeros(len(self.angles))
        
        # History for animation
        self.history = []  # list of (angle, activity, timestamp)
        
        # Figure
        self.fig, self.axes = plt.subplots(1, 2, figsize=(14, 6), 
                                          subplot_kw={'projection': 'polar'})
        self.fig.suptitle("CW Doppler Polar Scan — 2D Activity Map", fontsize=14)
        
        # Left: Activity heatmap
        self.ax_activity = self.axes[0]
        self.ax_activity.set_theta_zero_location('N')
        self.ax_activity.set_theta_direction(-1)
        self.ax_activity.set_thetamin(self.angles[0])
        self.ax_activity.set_thetamax(self.angles[-1])
        self.ax_activity.set_title("Activity Map", pad=20)
        
        # Bar plot for activity
        self.theta_rad = np.radians(self.angles)
        self.width = np.radians(pan_step * 0.8)
        self.bars = self.ax_activity.bar(
            self.theta_rad, self.activity, 
            width=self.width, bottom=0.0,
            color='blue', alpha=0.7
        )
        
        # Right: Power + Doppler
        self.ax_doppler = self.axes[1]
        self.ax_doppler.set_theta_zero_location('N')
        self.ax_doppler.set_theta_direction(-1)
        self.ax_doppler.set_thetamin(self.angles[0])
        self.ax_doppler.set_thetamax(self.angles[-1])
        self.ax_doppler.set_title("Power (radius) + Doppler (colour)", pad=20)
        
        self.bars_doppler = self.ax_doppler.bar(
            self.theta_rad, self.power,
            width=self.width, bottom=0.0,
            color='gray', alpha=0.7
        )
        
        plt.tight_layout()
        plt.show(block=False)
    
    def update(self, angle_idx: int, result: dict):
        """Update map with new scan result."""
        # Smooth update (exponential averaging)
        alpha = 0.3
        
        if result['motion_detected']:
            self.activity[angle_idx] = (1 - alpha) * self.activity[angle_idx] + alpha * result['confidence']
        else:
            self.activity[angle_idx] = (1 - alpha) * self.activity[angle_idx]
        
        self.power[angle_idx] = (1 - alpha) * self.power[angle_idx] + alpha * max(0, result['power_db'] + 80)
        self.confidence[angle_idx] = result['confidence']
        self.doppler[angle_idx] = result['max_doppler_hz']
        
        self.history.append((self.angles[angle_idx], self.activity[angle_idx], time.time()))
        
        # Update plots
        # Activity map: height = confidence, colour = activity level
        for bar, act, conf in zip(self.bars, self.activity, self.confidence):
            bar.set_height(act)
            # Colour: blue (quiet) → yellow (moderate) → red (motion)
            if act < 20:
                bar.set_color('blue')
                bar.set_alpha(0.3)
            elif act < 50:
                bar.set_color('yellow')
                bar.set_alpha(0.6)
            else:
                bar.set_color('red')
                bar.set_alpha(0.9)
        
        # Doppler map: radius = power, colour = Doppler frequency
        for bar, power, dop in zip(self.bars_doppler, self.power, self.doppler):
            bar.set_height(power)
            # Colour by Doppler speed
            if dop < 5:
                bar.set_color('blue')  # Slow / breathing
            elif dop < 20:
                bar.set_color('green')  # Walking
            else:
                bar.set_color('red')  # Fast motion
        
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()
    
    def save(self, filename: str = "polar_scan.png"):
        """Save current map to file."""
        self.fig.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"[PolarMap] Saved to {filename}")
    
    def get_active_sectors(self, threshold: float = 30.0) -> list:
        """Return list of angles with activity above threshold."""
        active = []
        for i, act in enumerate(self.activity):
            if act > threshold:
                active.append({
                    'angle_deg': self.angles[i],
                    'activity': act,
                    'power_db': self.power[i],
                    'doppler_hz': self.doppler[i]
                })
        return active
    
    def print_summary(self):
        """Print text summary of active sectors."""
        active = self.get_active_sectors(threshold=20)
        if not active:
            print("[PolarMap] No motion detected")
            return
        
        print(f"\n[PolarMap] {len(active)} active sectors:")
        for a in active:
            speed = "breathing" if a['doppler_hz'] < 5 else "walking" if a['doppler_hz'] < 20 else "fast"
            print(f"  {a['angle_deg']:5.1f}° | activity={a['activity']:.0f}% | "
                  f"power={a['power_db']:.1f} dB | {speed} ({a['doppler_hz']:.1f} Hz)")


def main():
    parser = argparse.ArgumentParser(description="Polar Scanning CW Doppler Radar")
    parser.add_argument("--rp-ip", default="192.168.1.100", help="Red Pitaya IP")
    parser.add_argument("--mock-servo", action="store_true", 
                       help="Use mock servo (software-only test)")
    parser.add_argument("--mock-radar", action="store_true",
                       help="Use mock radar data (no Red Pitaya)")
    parser.add_argument("--pan-start", type=float, default=0, help="Start angle (deg)")
    parser.add_argument("--pan-end", type=float, default=180, help="End angle (deg)")
    parser.add_argument("--pan-step", type=float, default=5, help="Step angle (deg)")
    parser.add_argument("--tilt", type=float, default=90, help="Fixed tilt angle")
    parser.add_argument("--dwell", type=float, default=300, help="Dwell time per angle (ms)")
    parser.add_argument("--rate-idx", type=int, default=2, help="I/Q rate index")
    parser.add_argument("--hpf", type=float, default=0.5, help="HPF cutoff (Hz)")
    parser.add_argument("--fc", type=float, default=30e6, help="Carrier frequency (Hz)")
    parser.add_argument("--save", type=str, default=None, help="Save final map to file")
    parser.add_argument("--loops", type=int, default=1, help="Number of scan loops")
    
    args = parser.parse_args()
    
    # Determine sample rate
    rates = {0: 20e3, 1: 50e3, 2: 100e3, 3: 250e3, 4: 500e3, 5: 1250e3}
    fs = rates.get(args.rate_idx, 100e3)
    
    print(f"\n{'='*60}")
    print(f"  Polar Scanning CW Doppler Radar")
    print(f"{'='*60}")
    print(f"  Servo:     {'MOCK' if args.mock_servo else 'Hardware'}")
    print(f"  Radar:     {'MOCK' if args.mock_radar else f'Red Pitaya @ {args.rp_ip}'}")
    print(f"  Scan:      {args.pan_start}° → {args.pan_end}° step {args.pan_step}°")
    print(f"  Tilt:      {args.tilt}°")
    print(f"  Dwell:     {args.dwell} ms")
    print(f"  Carrier:   {args.fc/1e6:.1f} MHz")
    print(f"  Rate:      {fs/1e3:.0f} kSPS")
    print(f"{'='*60}\n")
    
    # Initialise servo
    if args.mock_servo:
        servo = MockServo()
    else:
        servo = ServoController(pan_pin=0, tilt_pin=1)
    
    servo.start()
    
    # Initialise radar
    rp = None
    if not args.mock_radar:
        rp = RedPitayaSDR(args.rp_ip)
        if not rp.connect():
            print("[ERROR] Failed to connect to Red Pitaya")
            servo.stop()
            sys.exit(1)
        
        rp.set_sample_rate(args.rate_idx)
        rp.set_tx_freq(args.fc)
        rp.set_rx_freq(args.fc)
        rp.start_rx()
        rp.start_tx()
        rp.start_stream()
        time.sleep(0.5)
    
    # Initialise processor and map
    processor = PolarDopplerProcessor(fs=fs, hpf_cutoff=args.hpf)
    polar_map = PolarMap(
        pan_start=args.pan_start,
        pan_end=args.pan_end,
        pan_step=args.pan_step
    )
    
    # Scan loop
    block_size = int(fs * args.dwell / 1000.0)  # samples per dwell
    
    try:
        for loop in range(args.loops):
            print(f"\n[SCAN] Loop {loop + 1}/{args.loops}")
            
            # Scan through angles
            angles = np.arange(args.pan_start, args.pan_end + args.pan_step, args.pan_step)
            
            for i, pan_angle in enumerate(angles):
                # Move servo
                servo.set_pan_tilt(pan_angle, args.tilt)
                
                # Wait for servo to settle
                move_time = abs(pan_angle - (angles[i-1] if i > 0 else pan_angle)) / 600.0 + 0.05
                time.sleep(move_time)
                
                # Dwell and acquire
                t_start = time.time()
                samples = []
                
                while time.time() - t_start < args.dwell / 1000.0:
                    if args.mock_radar:
                        # Generate fake data with occasional motion
                        fake = np.random.randn(256) + 1j * np.random.randn(256)
                        # Add "motion" at certain angles
                        if 45 <= pan_angle <= 75:
                            fake += 0.5 * np.sin(2 * np.pi * 8 * np.arange(256) / fs)
                        samples.append(fake)
                        time.sleep(0.01)
                    else:
                        block = rp.get_samples_n(block_size // 10, timeout=1.0)
                        if len(block) > 0:
                            samples.append(block)
                
                if samples:
                    all_samples = np.concatenate(samples)
                    result = processor.process_scan_block(all_samples)
                    polar_map.update(i, result)
                    
                    # Print brief status
                    if result['motion_detected']:
                        print(f"  {pan_angle:5.1f}° | 🚨 MOTION | "
                              f"power={result['walk_power_db']:.1f} dB | "
                              f"doppler={result['max_doppler_hz']:.1f} Hz")
                    else:
                        print(f"  {pan_angle:5.1f}° | clear")
                
                # Update display every few angles
                if i % 3 == 0:
                    polar_map.print_summary()
        
        print("\n[SCAN] Complete")
        polar_map.print_summary()
        
        if args.save:
            polar_map.save(args.save)
    
    except KeyboardInterrupt:
        print("\n[STOP] Interrupted")
    
    finally:
        if rp:
            rp.stop_tx()
            rp.stop_rx()
            rp.disconnect()
        servo.stop()
        
        print("[DONE] Polar scan complete")
        plt.ioff()
        plt.show()


if __name__ == "__main__":
    main()
