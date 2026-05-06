"""
Servo Controller for Red Pitaya GPIO

Controls pan-tilt servos via Red Pitaya DIO pins.
Compatible with SG90 / MG90S / standard RC servos.

Pinout (Red Pitaya STEMlab 125-14 E1 connector):
  DIO0_N (pin 1)  → Pan servo PWM
  DIO1_N (pin 2)  → Tilt servo PWM
  DIO2_N (pin 3)  → Trigger / sync output
  GND   (pin 5,7,9) → Servo ground
  3.3V  (pin 4,6,8) → Servo power (NOT ENOUGH for MG90S — use external 5V)

WARNING: Red Pitaya 3.3V can supply ~100 mA total.
One SG90 draws ~100 mA when moving. Use external 5V supply for servos,
with common ground to Red Pitaya.
"""

import time
import threading
import numpy as np


class ServoController:
    """
    Software PWM servo controller using Red Pitaya DIO pins.
    
    Uses memory-mapped GPIO for precise timing (better than sysfs).
    Falls back to Python bit-banging if mmap unavailable.
    """
    
    # Servo timing: 50 Hz PWM, 0.5–2.5 ms pulse
    PWM_FREQ = 50.0  # Hz
    PERIOD_US = 20000.0  # 20 ms = 50 Hz
    MIN_PULSE_US = 500.0   # 0°
    MAX_PULSE_US = 2500.0  # 180°
    
    def __init__(self, pan_pin: int = 0, tilt_pin: int = 1, 
                 use_mmap: bool = True):
        """
        Args:
            pan_pin: DIO pin number for pan servo (0-7)
            tilt_pin: DIO pin number for tilt servo (0-7)
            use_mmap: Use memory-mapped GPIO (Linux only)
        """
        self.pan_pin = pan_pin
        self.tilt_pin = tilt_pin
        self.use_mmap = use_mmap
        
        self._pan_angle = 90.0  # degrees
        self._tilt_angle = 90.0
        
        self._pan_target = 90.0
        self._tilt_target = 90.0
        
        self._running = False
        self._thread = None
        self._lock = threading.Lock()
        
        # Try memory-mapped GPIO
        self._mm = None
        if use_mmap:
            try:
                import mmap
                import os
                # Red Pitaya GPIO base address
                GPIO_BASE = 0x41200000
                PAGE_SIZE = 4096
                with open("/dev/mem", "r+b") as f:
                    self._mm = mmap.mmap(f.fileno(), PAGE_SIZE, 
                                         offset=GPIO_BASE)
            except Exception as e:
                print(f"[Servo] Memory-mapped GPIO failed: {e}")
                print("[Servo] Falling back to sysfs GPIO (less precise)")
                self._init_sysfs_gpio()
        else:
            self._init_sysfs_gpio()
    
    def _init_sysfs_gpio(self):
        """Initialize sysfs GPIO exports."""
        import os
        for pin in [self.pan_pin, self.tilt_pin]:
            gpio_num = 960 + pin  # Red Pitaya GPIO offset
            try:
                with open(f"/sys/class/gpio/export", "w") as f:
                    f.write(str(gpio_num))
            except:
                pass  # Already exported
            
            with open(f"/sys/class/gpio/gpio{gpio_num}/direction", "w") as f:
                f.write("out")
    
    def _set_pin_mmap(self, pin: int, value: int):
        """Set GPIO pin via memory map."""
        if self._mm is None:
            return
        
        # Read current state
        self._mm.seek(0)
        state = int.from_bytes(self._mm.read(4), 'little')
        
        if value:
            state |= (1 << pin)
        else:
            state &= ~(1 << pin)
        
        self._mm.seek(0)
        self._mm.write(state.to_bytes(4, 'little'))
    
    def _set_pin_sysfs(self, pin: int, value: int):
        """Set GPIO pin via sysfs."""
        gpio_num = 960 + pin
        with open(f"/sys/class/gpio/gpio{gpio_num}/value", "w") as f:
            f.write(str(value))
    
    def _set_pin(self, pin: int, value: int):
        """Set GPIO pin (auto-select method)."""
        if self._mm is not None:
            self._set_pin_mmap(pin, value)
        else:
            self._set_pin_sysfs(pin, value)
    
    def _angle_to_pulse_us(self, angle: float) -> float:
        """Map 0-180° to pulse width in microseconds."""
        angle = np.clip(angle, 0, 180)
        return self.MIN_PULSE_US + (angle / 180.0) * (self.MAX_PULSE_US - self.MIN_PULSE_US)
    
    def _pwm_thread(self):
        """Background PWM generation thread."""
        while self._running:
            with self._lock:
                pan_pulse = self._angle_to_pulse_us(self._pan_target)
                tilt_pulse = self._angle_to_pulse_us(self._tilt_target)
            
            # Generate PWM for both servos
            # This is simplified — real implementation needs careful timing
            # For precise control, use FPGA PWM instead (see note below)
            
            t_start = time.perf_counter()
            
            # Pan servo pulse
            self._set_pin(self.pan_pin, 1)
            time.sleep(pan_pulse / 1e6)
            self._set_pin(self.pan_pin, 0)
            
            # Tilt servo pulse (offset by half period to avoid overlap)
            time.sleep(self.PERIOD_US / 2 / 1e6)
            self._set_pin(self.tilt_pin, 1)
            time.sleep(tilt_pulse / 1e6)
            self._set_pin(self.tilt_pin, 0)
            
            # Sleep remainder of period
            elapsed = (time.perf_counter() - t_start) * 1e6
            remaining = self.PERIOD_US - elapsed
            if remaining > 0:
                time.sleep(remaining / 1e6)
    
    def start(self):
        """Start PWM generation thread."""
        self._running = True
        self._thread = threading.Thread(target=self._pwm_thread, daemon=True)
        self._thread.start()
        print(f"[Servo] PWM started on pins {self.pan_pin}, {self.tilt_pin}")
    
    def stop(self):
        """Stop PWM and center servos."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
        
        # Center and release
        self.set_pan_tilt(90, 90)
        time.sleep(0.5)
        
        # Set pins low
        self._set_pin(self.pan_pin, 0)
        self._set_pin(self.tilt_pin, 0)
        
        if self._mm:
            self._mm.close()
        print("[Servo] Stopped")
    
    def set_pan_tilt(self, pan_deg: float, tilt_deg: float):
        """Set target angles (0-180°)."""
        with self._lock:
            self._pan_target = np.clip(pan_deg, 0, 180)
            self._tilt_target = np.clip(tilt_deg, 0, 180)
    
    def get_pan_tilt(self) -> tuple:
        """Get current target angles."""
        with self._lock:
            return self._pan_target, self._tilt_target
    
    def scan_angles(self, pan_start: float = 0, pan_end: float = 180,
                    pan_step: float = 5.0, tilt: float = 90.0,
                    dwell_ms: float = 500.0):
        """
        Generator that yields scan angles with dwell time.
        
        Yields: (pan_angle, tilt_angle, is_new_position)
        
        Usage:
            for angle in servo.scan_angles():
                pan, tilt, is_new = angle
                # Trigger radar acquisition
                # Wait for dwell time
        """
        angles = np.arange(pan_start, pan_end + pan_step, pan_step)
        
        for pan in angles:
            self.set_pan_tilt(pan, tilt)
            
            # Wait for servo to move (approximate)
            # SG90: ~60°/0.1s = 600°/s
            move_time = abs(pan - self._pan_target) / 600.0 + 0.05
            time.sleep(move_time)
            
            # Dwell at position
            t_dwell = time.time()
            while time.time() - t_dwell < dwell_ms / 1000.0:
                yield (pan, tilt, True)
            
            # Between steps, yield False to indicate transition
            yield (pan, tilt, False)


class FPGA_PWM_Controller:
    """
    Alternative: Use Red Pitaya FPGA for hardware PWM.
    
    Much more precise than software PWM. Requires custom FPGA bitstream
    with PWM IP cores, or using Pavel Demin's GPIO/PWM example.
    
    This is recommended for production use. Software PWM has jitter
    that can cause servo chatter.
    """
    
    def __init__(self):
        print("[FPGA-PWM] Placeholder — requires custom FPGA bitstream")
        print("[FPGA-PWM] See hardware_setup.md for Vivado instructions")
    
    def set_angles(self, pan: float, tilt: float):
        raise NotImplementedError("Requires FPGA PWM bitstream")


class MockServo:
    """
    Software-only mock for testing without hardware.
    Logs angles to console.
    """
    
    def __init__(self, pan_pin=0, tilt_pin=1):
        self.pan = 90.0
        self.tilt = 90.0
        print("[MockServo] Initialised (no hardware)")
    
    def start(self):
        print("[MockServo] Started")
    
    def stop(self):
        print("[MockServo] Stopped")
    
    def set_pan_tilt(self, pan: float, tilt: float):
        self.pan = pan
        self.tilt = tilt
    
    def get_pan_tilt(self):
        return self.pan, self.tilt
    
    def scan_angles(self, pan_start=0, pan_end=180, pan_step=5, 
                    tilt=90, dwell_ms=500):
        angles = np.arange(pan_start, pan_end + pan_step, pan_step)
        for pan in angles:
            self.set_pan_tilt(pan, tilt)
            print(f"[MockServo] Scanning pan={pan:.1f}°, tilt={tilt:.1f}°")
            time.sleep(dwell_ms / 1000.0)
            yield (pan, tilt, True)
            yield (pan, tilt, False)
