# 2D Polar Scanning — Software Integration Guide

Simplest 3D-adjacent visualisation: scan the room with a servo, build a 2D polar activity map.

## What You Get

```
                    N (0°)
                     │
                     │
            ┌────────┴────────┐
            │   🔴     🟡    │
            │      RADAR    │
            │   🟡     🔵    │
            └────────┴────────┘
                     │
                     │
                    S (180°)

Legend:
  🔴 Red   = Motion detected (walking)
  🟡 Yellow = Weak activity / breathing
  🔵 Blue  = Quiet / no motion
```

Two side-by-side polar plots:
- **Left:** Activity confidence per angle (bar height)
- **Right:** Power (radius) + Doppler speed (colour)

## Hardware Needed (£10 extra)

| Item | Spec | Cost | Wiring |
|------|------|------|--------|
| SG90 servo | 9g micro servo | £2 | Signal → RP DIO0_N |
| Servo bracket | Pan mount or dual-axis | £3 | Mechanical |
| External 5V | USB power bank or adapter | £5 | Servo power |
| Shared GND | Wire between RP and servo PSU | £0 | Connect grounds |

**IMPORTANT:** Power servos from external 5V, not Red Pitaya 3.3V. The RP 3.3V rail cannot supply enough current for servo movement.

### Wiring Diagram

```
External 5V Supply:
  +5V ───────┬──► Servo VCC (red wire)
             │
  GND  ──────┼──► Servo GND (brown/black wire)
             │
             └──► Red Pitaya GND (E1 pin 5/7/9)

Red Pitaya E1 Connector:
  DIO0_N (pin 1) ──► Servo signal (orange/yellow wire) — PAN
  DIO1_N (pin 2) ──► Servo signal — TILT (optional)
```

### Servo Mounting

- **Option A:** Camera tripod with phone clamp → hot-glue servo to clamp
- **Option B:** 3D printed bracket (Thingiverse: "servo pan tilt mount")
- **Option C:** Sticky tape + cardboard box (prototype only)

Antenna attaches to servo horn, points in scan direction.

---

## Software Stack

### File Inventory

| File | Purpose | Lines |
|------|---------|-------|
| `rp_sdr_client.py` | Red Pitaya TCP I/Q streaming | 170 |
| `servo_controller.py` | GPIO PWM for servos | 230 |
| `polar_scanner.py` | Main application: scan + process + render | 340 |

### Dependencies

All in `requirements.txt`:
```
numpy, scipy, matplotlib, pyqtgraph, PyQt5
```

No extra dependencies for the servo stack. Uses standard library `mmap` for GPIO.

---

## Running the Polar Scanner

### 1. Desk Test (No Red Pitaya, No Servo)

Test the polar rendering with mock data:

```bash
cd radar/cw_doppler
python polar_scanner.py --mock-servo --mock-radar --pan-step 10 --dwell 200
```

**What you see:**
- Polar plot animates as scanner sweeps 0° → 180°
- Fake motion appears at 45–75° (hardcoded for demo)
- Activity bars grow/shrink in real-time
- Console prints angle-by-angle status

### 2. Servo Test (No Red Pitaya)

Test servo movement:

```bash
python -c "
from servo_controller import ServoController
import time

servo = ServoController(pan_pin=0, tilt_pin=1)
servo.start()

for angle in [0, 45, 90, 135, 180, 90]:
    print(f'Moving to {angle}°')
    servo.set_pan_tilt(angle, 90)
    time.sleep(1.0)

servo.stop()
"
```

**Expected:** Servo smoothly moves through angles. If it chatters, the PWM timing is off — use the mock mode or switch to external PWM driver.

### 3. Full Scan (Red Pitaya + Servo)

```bash
python polar_scanner.py \
    --rp-ip 192.168.1.100 \
    --pan-start 0 --pan-end 180 --pan-step 5 \
    --tilt 90 --dwell 300 \
    --fc 30e6 --rate-idx 2 \
    --hpf 0.5 \
    --loops 3 \
    --save scan_result.png
```

**What happens:**
1. Connects to Red Pitaya, starts TX/RX
2. Servo moves to 0°
3. Dwells 300 ms, acquires I/Q samples
4. Processes: HPF → FFT → motion detection
5. Updates polar map bar at 0°
6. Steps to 5°, repeats
7. ...continues to 180°
8. Prints active sectors summary
9. Optionally loops again (3 loops total)
10. Saves final map to `scan_result.png`

---

## Output Interpretation

### Console Output

```
[SCAN] Loop 1/3
    0.0° | clear
    5.0° | clear
   10.0° | clear
   ...
   45.0° | 🚨 MOTION | power=-42.3 dB | doppler=16.5 Hz
   50.0° | 🚨 MOTION | power=-38.1 dB | doppler=18.2 Hz
   55.0° | 🚨 MOTION | power=-45.7 dB | doppler=14.8 Hz
   ...
  180.0° | clear

[PolarMap] 3 active sectors:
   45.0° | activity=85% | power=38.5 dB | walking (16.5 Hz)
   50.0° | activity=92% | power=42.1 dB | walking (18.2 Hz)
   55.0° | activity=71% | power=35.8 dB | walking (14.8 Hz)
```

### Polar Plot

- **Left plot (Activity Map):** Bar height = confidence 0–100%. Colour: blue (quiet) → yellow (weak) → red (motion).
- **Right plot (Power + Doppler):** Bar radius = signal power. Colour: blue (slow/breathing) → green (walking) → red (fast).

### Saved Image (`scan_result.png`)

Static PNG of final polar map. Good for reports, documentation, comparison over time.

---

## Tuning Parameters

| Parameter | Default | Effect | Adjust If... |
|-----------|---------|--------|--------------|
| `--pan-step` | 5° | Angular resolution | Too coarse: reduce to 2°. Too slow: increase to 10° |
| `--dwell` | 300 ms | Acquisition time per angle | Motion missed: increase to 500 ms. Scan too slow: decrease to 200 ms |
| `--hpf` | 0.5 Hz | Clutter cutoff | Static objects false-alarm: increase to 1 Hz. Breathing missed: decrease to 0.1 Hz |
| `--loops` | 1 | Number of scan cycles | Tracking over time: increase to 10+ |

**Scan speed:**
- 5° step, 300 ms dwell, 180° range = 37 positions × 0.3 s = 11.1 s per sweep
- Add servo move time (~0.1 s per step) = ~15 s per sweep
- 3 loops = ~45 seconds total

---

## From 2D Polar to 3D

### Current: 2D Polar (what we have now)
```
Data per angle: (activity, power, max_doppler)
Visual: polar bar chart
Limitation: No range — can't tell if target is 1 m or 5 m away
```

### Upgrade 1: 2.5D Sector (add range proxy)
```
Use power as proxy for range (inverse 4th power, approximate)
Data: (angle, estimated_range, power, speed)
Visual: polar scatter with radial distance = power
Limitation: Very rough range estimate
```

### Upgrade 2: 2.5D with FMCW (proper range)
```
Add FPGA chirp generator → beat frequency gives real range
Data: (angle, range_m, speed, power)
Visual: polar plot with concentric range rings
Limitation: Single elevation angle
```

### Upgrade 3: Full 3D (add elevation scan)
```
Tilt servo scans 0° → 90° at each pan angle
Data: (azimuth, elevation, range, speed, power)
Visual: spherical point cloud (Open3D)
Use: Full room 3D reconstruction
```

### Upgrade 4: Multi-radar fusion
```
Two or more radars at known positions
Triangulate target from angle-only detections
Data: (x, y, z, speed) in global coordinates
Visual: 3D trajectory tracking
```

---

## Troubleshooting

### Servo doesn't move
- Check external 5V power (not RP 3.3V)
- Check common ground between RP and servo PSU
- Verify pin numbers (DIO0 = pin 1 on E1)
- Use `--mock-servo` to test software without hardware

### Jerky / noisy servo
- Software PWM has jitter. For smooth motion, use external PWM servo driver (PCA9685 I2C module, £3)
- Or upgrade to FPGA-based PWM (custom bitstream)

### No motion detected
- Check `--mock-radar` produces fake motion at 45–75° (proves software works)
- Verify Red Pitaya I/Q streaming with `cw_doppler.py --mode baseband`
- Increase `--dwell` for longer acquisition
- Decrease `--hpf` to catch slower motion
- Check antenna alignment — is it actually pointing at the target?

### False alarms everywhere
- Increase `--hpf` to reject slow drift
- Increase motion threshold in `PolarDopplerProcessor`
- Check for vibrating objects (fans, HVAC) — move radar away from them

### Polar plot not updating
- Ensure matplotlib backend supports interactive mode (`plt.ion()`)
- On headless systems: `export MPLBACKEND=TkAgg` before running
- Or use `--save` to skip real-time plot and just save final image

---

## Security Application: Room Clear

**Scenario:** Before entering a room, scan from outside/doorway.

```bash
# Position radar at doorway, scan 180° arc into room
python polar_scanner.py \
    --rp-ip 192.168.1.100 \
    --pan-start -90 --pan-end 90 --pan-step 10 \
    --dwell 500 --loops 2
```

**Interpretation:**
- Motion at -30° → left side of room, ~3 m in
- Motion at +45° → right side, near window
- No motion at 0° → centre aisle clear

**Action:** Enter cautiously, check left first (motion detected).

---

## Next Steps

1. ✅ **Run mock test** — `polar_scanner.py --mock-servo --mock-radar`
2. ✅ **Wire servo + test movement** — `python -c "from servo_controller import *; ..."`
3. ✅ **Full scan with Red Pitaya** — `polar_scanner.py --rp-ip ...`
4. 🔄 **Tune parameters** for your room size and target type
5. 🔄 **Add FMCW** for real range → concentric range rings on polar plot
6. 🔄 **Add tilt servo** → spherical scan → 3D point cloud

The 2D polar map is the simplest upgrade that gives you genuine spatial information. From here, every hardware addition (FMCW, second antenna, tilt) unlocks a new dimension of visualisation.
