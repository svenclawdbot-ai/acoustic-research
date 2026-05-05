# 3D Radar Rendering & Visualisation

What can we produce from radar data, and how do we make it useful for security applications?

## Data We Have (CW vs FMCW)

### CW Doppler Output (Current Stack)
```python
# Per frame:
{
    'timestamp': 0.0,           # seconds
    'range': None,              # CW has NO range information
    'doppler_hz': 16.3,        # speed toward/away
    'doppler_band': 'walking',  # breathing / heartbeat / walking
    'power_db': -45.2,         # reflection strength
    'azimuth': None,           # no angle (single antenna)
    'elevation': None,         # no angle
}
```

**CW Doppler is 1D:** speed only. You can't render a 3D scene from this alone.  
**What you CAN do:**
- Time-series waterfall (spectrogram over time)
- Occupancy timeline (was motion detected? yes/no)
- Speed histogram
- Geolocation if you move the antenna and record GPS/position

### FMCW Output (Upgrade Path)
```python
# Per chirp:
{
    'timestamp': 0.0,
    'range_m': 3.47,           # ← range from beat frequency
    'doppler_hz': 2.1,         # ← Doppler across chirps
    'power_db': -52.0,         # reflection strength
    'azimuth': None,           # need antenna array or scanning
    'elevation': None,         # need elevation scan
}
```

**FMCW is 2D:** range + speed per target.

### MIMO / Array Output (Further Upgrade)
```python
# Per frame:
{
    'timestamp': 0.0,
    'range_m': 3.47,
    'doppler_hz': 2.1,
    'power_db': -52.0,
    'azimuth_deg': 15.3,      # ← angle from antenna array
    'elevation_deg': -5.2,    # ← angle from vertical array
}
```

**MIMO is 3D:** range, azimuth, elevation per target. Now you can render.

---

## Rendering Pipeline Overview

```
Raw I/Q ──► Signal Processing ──► Detections ──► Tracking ──► 3D Scene
    │              │                  │             │           │
    │         FFT/CFAR          (range,             Kalman     Open3D
    │         Range-Doppler      speed,            Filter      /PyVista
    │         Map                 power)           MHT          /Three.js
    │                                                   │
    └───────────────────────────────────────────────────┘
                    Point Cloud / Voxel Grid
```

---

## Technique 1: Range-Doppler Map (2D Heatmap)

Already built into `cw_doppler.py`. The spectrogram is essentially this.

**With FMCW:**
```python
import numpy as np
import matplotlib.pyplot as plt

# range_bins: 0–10 m in 0.3 m steps (for 50 MHz chirp)
# doppler_bins: -50 to +50 Hz

range_doppler_map = np.zeros((n_range_bins, n_doppler_bins))

# Fill from detections
for detection in detections:
    r_idx = int(detection['range_m'] / range_resolution)
    d_idx = int((detection['doppler_hz'] + max_doppler) / doppler_resolution)
    range_doppler_map[r_idx, d_idx] += 10**(detection['power_db']/10)

# Render
plt.figure(figsize=(10, 6))
plt.imshow(20*np.log10(range_doppler_map + 1e-12), 
           aspect='auto', origin='lower', cmap='viridis')
plt.xlabel('Doppler (Hz)')
plt.ylabel('Range (m)')
plt.title('Range-Doppler Map')
plt.colorbar(label='Power (dB)')
```

**Security use:** Identify what targets are where and how fast. Person at 3 m walking = strong peak at (3m, 16Hz).

---

## Technique 2: SAR — Synthetic Aperture Radar (2D Image from Scanning)

**Concept:** Move the antenna along a path while recording. Process coherently to synthesise a larger aperture → higher resolution image.

**For CW Doppler (limited but possible):**
- Move antenna horizontally → process as 1D SAR → range-crossrange image
- Range comes from... wait, CW has no range. You need FMCW or pulse radar for SAR.

**For FMCW (proper SAR):**
```
Move antenna along rail / manually scan room
At each position x: record FMCW chirp → range profile r
SAR processing: back-projection or range-Doppler algorithm
Output: 2D image (range vs cross-range) with cm-scale resolution
```

**Security use:**
- **Wall imaging:** Scan radar along wall exterior → image interior layout
- **Concealed object detection:** Find anomalies in wall structure (voids, compartments)
- **Through-wall SAR:** Requires wide bandwidth + coherent motion tracking

**Implementation:**
```python
def sar_backproject(range_profiles, positions, image_grid):
    """
    positions: N×2 array of (x, y) antenna positions
    range_profiles: N×M array of range bins
    image_grid: grid of pixels to reconstruct
    """
    image = np.zeros(image_grid.shape)
    
    for i, (x, y) in enumerate(positions):
        for pixel in image_grid:
            px, py = pixel
            r = np.sqrt((px - x)**2 + (py - y)**2)
            r_idx = int(r / range_resolution)
            if 0 <= r_idx < len(range_profiles[i]):
                image[pixel] += range_profiles[i, r_idx]
    
    return image
```

**With Red Pitaya:** Use Pavel Demin's Scanner project for precise raster scanning control. The scanner already has FPGA-based line/raster generation and position-synced acquisition.

---

## Technique 3: Multiple Antenna Array — Angle Estimation (2.5D)

**Concept:** Use 2–4 antennas spaced by λ/2. Phase difference between channels gives angle of arrival (AoA).

**For Red Pitaya:**
- **Dual RX:** IN1 and IN2 can receive from two antennas
- Phase difference between IN1 and IN2 → azimuth estimate

**Mathematics:**
```
Two antennas spaced d = λ/2 = 6.25 cm at 2.4 GHz
Phase difference Δφ = (2πd/λ) · sin(θ)
Therefore: θ = arcsin(Δφ · λ / (2πd))
```

**Implementation:**
```python
def estimate_azimuth(iq_ch1, iq_ch2, wavelength, spacing):
    """
    iq_ch1, iq_ch2: complex baseband samples from two antennas
    wavelength: in metres (0.125 m at 2.4 GHz)
    spacing: antenna separation in metres
    """
    # Correlation gives phase difference
    correlation = np.mean(iq_ch1 * np.conj(iq_ch2))
    phase_diff = np.angle(correlation)  # -π to +π
    
    # Unwrap if needed
    k = np.round((phase_diff * spacing / wavelength) / (2*np.pi))
    phase_diff_unwrapped = phase_diff - k * 2 * np.pi * wavelength / spacing
    
    theta = np.arcsin(phase_diff_unwrapped * wavelength / (2 * np.pi * spacing))
    return np.degrees(theta)  # -90° to +90°
```

**Limitations:**
- Only one target at a time (multiple targets have overlapping phase)
- Grating lobes if spacing > λ/2
- Accuracy: ±5–10° with SNR > 10 dB

**Security use:**
- **Directional alarm:** "Motion detected at bearing 23°"
- **Sector monitoring:** Divide space into zones, track which zone has activity
- **Two-target separation:** If targets at different angles, can distinguish

---

## Technique 4: Full 3D Point Cloud (FMCW + Scanning or Array)

**Requirements:**
1. FMCW for range
2. Multiple antennas or mechanical scan for angle
3. Optional: dual polarisation for elevation

### 4a. Mechanical Scanning (Slow but Simple)
```
Radar on pan-tilt mount
Step 1: Point at azimuth 0°, record FMCW
Step 2: Point at azimuth 5°, record FMCW
...
Step N: Point at azimuth 180°, record FMCW

Each FMCW gives range profile along that line
Combine: 2D polar → cartesian point cloud
Add elevation tilt → 3D point cloud
```

**Time per scan:**
- 37 angles × 0.1 sec per angle = 3.7 sec for 180° sweep
- Too slow for real-time tracking, fine for mapping

### 4b. Linear Array (Real-Time 2D)
```
8 antennas spaced λ/2 = 6.25 cm → total array 43.75 cm
Beamforming or MUSIC algorithm → AoA estimate for each range bin

Output per frame: (range, azimuth, power) for each target
```

### 4c. Rectangular Array (Real-Time 3D)
```
4×4 array = 16 antennas
MUSIC or ESPRIT in 2D → (range, azimuth, elevation)
```

**Red Pitaya limitation:** Only 2 ADC channels. For >2 antennas, need external ADC multiplexer or multiple Red Pitayas with synchronised clocks.

### 4d. Hybrid: FMCW + Single Antenna + Known Position (SLAM-style)
```
Move radar through space while recording
GPS/IMU tracks position and orientation
Each FMCW chirp = a 1D range measurement along current bearing
Combine like LiDAR SLAM → build 3D map
```

This is actually very practical for security: walk around a building exterior, map interior through walls.

---

## Technique 5: Volumetric Rendering (Voxel Grid)

**Concept:** Divide space into 3D voxels. Fill each voxel with probability of occupancy based on radar returns.

```python
import numpy as np

class VoxelGrid:
    def __init__(self, x_range, y_range, z_range, resolution):
        self.res = resolution
        self.x_bins = int((x_range[1] - x_range[0]) / resolution)
        self.y_bins = int((y_range[1] - y_range[0]) / resolution)
        self.z_bins = int((z_range[1] - z_range[0]) / resolution)
        
        self.occupancy = np.zeros((self.x_bins, self.y_bins, self.z_bins))
        self.hits = np.zeros((self.x_bins, self.y_bins, self.z_bins))
        self.misses = np.zeros((self.x_bins, self.y_bins, self.z_bins))
    
    def update_from_detection(self, range_m, azimuth_deg, elevation_deg, 
                              power_db, radar_position):
        """Convert polar detection to voxel update."""
        # Convert to cartesian
        az = np.radians(azimuth_deg)
        el = np.radians(elevation_deg)
        
        dx = range_m * np.cos(el) * np.cos(az)
        dy = range_m * np.cos(el) * np.sin(az)
        dz = range_m * np.sin(el)
        
        target_pos = radar_position + np.array([dx, dy, dz])
        
        # Map to voxel
        vx = int((target_pos[0] - self.x_range[0]) / self.res)
        vy = int((target_pos[1] - self.y_range[0]) / self.res)
        vz = int((target_pos[2] - self.z_range[0]) / self.res)
        
        if 0 <= vx < self.x_bins and 0 <= vy < self.y_bins and 0 <= vz < self.z_bins:
            # Update occupancy (log-odds)
            p = self._power_to_probability(power_db)
            log_odds = np.log(p / (1 - p))
            self.occupancy[vx, vy, vz] += log_odds
            self.hits[vx, vy, vz] += 1
    
    def _power_to_probability(self, power_db):
        """Map received power to occupancy probability."""
        # Sigmoid-like mapping
        # Strong return = high probability
        # Threshold at -60 dB
        return 1.0 / (1.0 + np.exp(-(power_db + 60) / 5))
    
    def get_point_cloud(self, threshold=0.5):
        """Extract occupied voxels as point cloud."""
        prob = 1.0 / (1.0 + np.exp(-self.occupancy))
        occupied = prob > threshold
        
        x, y, z = np.where(occupied)
        points = np.column_stack([
            self.x_range[0] + x * self.res,
            self.y_range[0] + y * self.res,
            self.z_range[0] + z * self.res
        ])
        return points
```

**Security use:**
- **Room mapping:** Walk radar around room → build voxel map of walls, furniture, people
- **Change detection:** Compare current voxel grid to baseline → highlight moved objects
- **Persistent surveillance:** Update grid over hours → track long-term occupancy patterns

---

## Technique 6: Real-Time 3D Visualisation

### Option A: Matplotlib 3D (Simple, Slow)
```python
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot point cloud
ax.scatter(points[:, 0], points[:, 1], points[:, 2], c=power, cmap='jet')

# Plot radar position
ax.scatter([0], [0], [0], c='red', marker='^', s=200)

# Add room bounds
ax.set_xlim(0, 10)
ax.set_ylim(-5, 5)
ax.set_zlim(0, 3)
ax.set_xlabel('X (m)')
ax.set_ylabel('Y (m)')
ax.set_zlabel('Z (m)')

plt.show()
```

**Pros:** No extra dependencies, works now  
**Cons:** Too slow for real-time (>5 fps). Fine for post-analysis.

### Option B: PyVista (Better, Still Python)
```python
import pyvista as pv

plotter = pv.Plotter()

# Point cloud
cloud = pv.PolyData(points)
cloud['power'] = power_values
plotter.add_mesh(cloud, render_points_as_spheres=True, 
                 point_size=5, cmap='jet')

# Voxel grid as volume
volume = plotter.add_volume(grid, cmap='viridis', opacity='linear')

# Radar position
plotter.add_mesh(pv.Sphere(radius=0.1, center=(0, 0, 0)), color='red')

plotter.show()
```

**Pros:** Handles large point clouds, volume rendering, interactive  
**Cons:** Heavy dependency, may not run on all systems

### Option C: Open3D (Industry Standard)
```python
import open3d as o3d

# Point cloud
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(points)
pcd.colors = o3d.utility.Vector3dVector(colors)  # colour by power

# Visualise
o3d.visualization.draw_geometries([pcd])

# Save for later
o3d.io.write_point_cloud("room_scan.ply", pcd)
```

**Pros:** Fast, modern, supports real-time update, mesh reconstruction  
**Cons:** C++ backend, large install

### Option D: Web-Based Three.js (Dashboard / Remote)
```
Backend: Python (Flask/FastAPI) serves radar data as JSON
Frontend: Three.js renders 3D scene in browser

Update rate: 1–5 Hz (limited by webSocket)
Great for: remote monitoring dashboard, multi-user view
```

**Pros:** Accessible from any device, no install  
**Cons:** More complex stack, latency

---

## Technique 7: Target Tracking & Trajectory Rendering

**Even with CW Doppler (no range), we can track over time if we move the radar or have angle.**

### Kalman Filter Tracker
```python
import numpy as np

class RadarTracker:
    def __init__(self):
        self.tracks = {}  # track_id → state
        self.next_id = 0
    
    def predict(self, dt):
        """Predict forward using constant velocity model."""
        for tid, track in self.tracks.items():
            F = np.array([
                [1, 0, dt, 0],
                [0, 1, 0, dt],
                [0, 0, 1, 0],
                [0, 0, 0, 1]
            ])  # state: [x, y, vx, vy]
            track['state'] = F @ track['state']
            track['cov'] = F @ track['cov'] @ F.T + track['Q']
    
    def update(self, detections):
        """Update with new detections using Hungarian assignment."""
        # Simplified: nearest-neighbour association
        for det in detections:
            best_track = None
            best_dist = float('inf')
            
            for tid, track in self.tracks.items():
                dist = np.linalg.norm(det['position'] - track['state'][:2])
                if dist < best_dist and dist < 2.0:  # 2 m gate
                    best_dist = dist
                    best_track = tid
            
            if best_track is not None:
                # Update existing track
                self._kalman_update(best_track, det)
            else:
                # New track
                self._init_track(det)
    
    def _init_track(self, detection):
        self.tracks[self.next_id] = {
            'state': np.array([detection['x'], detection['y'], 0, 0]),
            'cov': np.eye(4) * 10,
            'Q': np.eye(4) * 0.1,  # process noise
            'R': np.eye(2) * 1.0,   # measurement noise
            'age': 0,
            'hits': 1
        }
        self.next_id += 1
```

**Render tracks in 3D:**
```python
# Plot trajectory history
for tid, track in tracker.tracks.items():
    history = track['history']  # list of (x, y, t)
    points = np.array([(h[0], h[1], 0) for h in history])
    
    # Line for trajectory
    ax.plot(points[:, 0], points[:, 1], points[:, 2], 
            label=f'Track {tid}')
    
    # Current position marker
    ax.scatter([points[-1, 0]], [points[-1, 1]], [points[-1, 2]], 
               s=100, marker='o')
```

**Security use:**
- **Count people:** How many distinct tracks? → room occupancy count
- **Predict motion:** Where is the target heading? → intercept or intercept planning
- **Anomaly detection:** Track deviates from normal path → alert

---

## Technique 8: Building Layout Reconstruction (SAR + Mapping)

**The dream:** Walk around a building with FMCW radar → get a 3D model of interior.

**Approach:**
```
1. Walk around building exterior, radar aimed at walls
2. Record GPS/IMU position + orientation for each FMCW chirp
3. For each chirp: range profile = reflection along that line
4. SAR back-projection → 2D slice through wall
5. Multiple slices at different heights → 3D reconstruction
6. Detect anomalies: voids, different materials, hidden rooms
```

**Red Pitaya-specific:**
- Use Pavel Demin's Scanner for precise antenna positioning
- Or use smartphone IMU + manual trigger (tap to record at each position)
- FPGA handles real-time FMCW, ARM saves data to SD card

**Visualisation:**
- **Cross-section slices:** Matplotlib imshow at different depths
- **3D isosurface:** PyVista contour plot of reflection strength
- **Difference map:** Compare to expected solid wall → highlight voids

---

## What Can We Build with Current Hardware (CW Doppler Only)?

### A. Occupancy Timeline (Text/2D)
```
Time    | Motion | Speed | Confidence
--------|--------|-------|----------
10:00:00| None   | 0     | 100%
10:00:15| Walk   | 1.2   | 85%
10:00:20| Stop   | 0     | 90%
10:00:25| Breath | 0.05  | 60%
10:00:45| Walk   | 1.5   | 88%
10:00:50| Leave  | —     | 95%
```

### B. Waterfall / Spectrogram (2D Image)
Already in `cw_doppler.py`. Time on x-axis, Doppler on y-axis, colour = power.

### C. Polar Plot (2D, if scanning)
If you pan the antenna and record angle:
```python
# Polar scatter: radius = some proxy (e.g., signal strength), angle = pan angle
theta = np.radians(pan_angles)
r = 1 + np.log10(power)  # normalised

fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
ax.scatter(theta, r, c=power, cmap='jet')
ax.set_title('Radar Scan (Polar)')
```

### D. Georeferenced Track (2D Map)
If you have GPS on the radar:
```python
# Plot on satellite map background
import folium

m = folium.Map(location=[lat, lon], zoom_start=18)
for det in detections:
    folium.CircleMarker(
        location=[det['lat'], det['lon']],
        radius=5,
        color='red' if det['motion'] else 'green',
        popup=f"{det['timestamp']}: {det['doppler_hz']:.1f} Hz"
    ).add_to(m)
```

---

## Upgrade Path for 3D

| Stage | Hardware Add | Data Dimensions | 3D Capability |
|-------|-------------|-----------------|---------------|
| **1. CW** | None (now) | Speed only | Timeline + spectrogram |
| **2. FMCW** | FPGA chirp | Speed + Range | Range-Doppler map, 1D profile |
| **3. SAR** | Scanner / manual pan | Speed + Range + Position | 2D slice through wall |
| **4. Dual RX** | Second antenna | Speed + Range + Azimuth | 2.5D: polar plot, sector activity |
| **5. MIMO array** | 4–8 antennas + mux | Speed + Range + Az + El | Full 3D point cloud |
| **6. Multi-node** | 2+ radars networked | Speed + Range + Angle + Position | Triangulated 3D, wide area |

---

## Recommended Next Steps for 3D Rendering

### Immediate (CW Doppler, no new hardware)
1. **Add polar scanning:** Put radar on a pan-tilt servo, record angle
   - Servo control from Red Pitaya GPIO or external Arduino
   - At each angle: run CW Doppler for 0.5 sec → record max power
   - Render polar heatmap

2. **Add geolocation:** GPS module (USB or UART to Red Pitaya)
   - Record GPS position with each detection
   - Overlay on OpenStreetMap
   - Track radar path + detected motion zones

3. **Add IMU:** MPU6050 or similar (I2C to Red Pitaya)
   - Record radar orientation
   - Project detections into global coordinates
   - Build 2D activity map from moving radar

### Short-term (FMCW upgrade)
1. **Build FPGA chirp generator** (next major hardware step)
   - Red Pitaya generates sawtooth frequency sweep
   - Beat frequency → range
   - Now you can do SAR and wall imaging

2. **Add dual-antenna AoA**
   - Two antennas on IN1/IN2
   - Phase difference → azimuth
   - Render 2.5D: range-azimuth heatmap (like a sector LiDAR)

### Medium-term (MIMO array)
1. **External ADC multiplexer** or multiple synced Red Pitayas
2. **MUSIC/ESPRIT beamforming** for high-resolution angle
3. **Full 3D point cloud** with Open3D real-time visualisation

---

## Code: Real-Time 3D Visualisation Stub

```python
# render3d.py — PyQtGraph-based real-time 3D scatter

import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from PyQt5 import QtWidgets, QtCore

class Radar3DViewer(gl.GLViewWidget):
    def __init__(self):
        super().__init__()
        
        # Radar position (origin)
        self.radar_pos = np.array([0, 0, 0])
        
        # Point cloud storage
        self.points = []
        self.colors = []
        
        # GL scatter item
        self.scatter = gl.GLScatterPlotItem()
        self.addItem(self.scatter)
        
        # Grid
        gx = gl.GLGridItem()
        gx.scale(1, 1, 1)
        self.addItem(gx)
        
        # Radar marker
        radar_mesh = gl.MeshData.sphere(rows=10, cols=10, radius=0.1)
        self.radar_marker = gl.GLMeshItem(meshdata=radar_mesh, 
                                          color=(1, 0, 0, 1))
        self.addItem(self.radar_marker)
    
    def update_detections(self, detections):
        """
        detections: list of dicts with keys:
            range_m, azimuth_deg, elevation_deg, power_db
        """
        new_points = []
        new_colors = []
        
        for det in detections:
            az = np.radians(det['azimuth_deg'])
            el = np.radians(det['elevation_deg'])
            r = det['range_m']
            
            x = r * np.cos(el) * np.cos(az)
            y = r * np.cos(el) * np.sin(az)
            z = r * np.sin(el)
            
            new_points.append([x, y, z])
            
            # Color by power: blue (weak) to red (strong)
            p = np.clip((det['power_db'] + 80) / 40, 0, 1)
            new_colors.append([p, 0, 1-p, 0.8])
        
        self.points = np.array(new_points)
        self.colors = np.array(new_colors)
        
        if len(self.points) > 0:
            self.scatter.setData(pos=self.points, color=self.colors, size=10)
    
    def add_trajectory(self, points, color=(1, 1, 0, 1)):
        """Draw a trajectory line."""
        line = gl.GLLinePlotItem(pos=points, color=color, width=2)
        self.addItem(line)


# Usage in main loop:
viewer = Radar3DViewer()
viewer.show()

# In acquisition thread:
while running:
    detections = radar.get_detections()
    viewer.update_detections(detections)
    QtCore.QThread.msleep(100)  # 10 Hz update
```

---

## Summary: 3D Rendering Roadmap

**Week 1–2 (CW Doppler):**
- ✅ Spectrogram waterfall (already built)
- ✅ Occupancy timeline (text or simple plot)
- 🔄 Polar scan with servo (add pan mechanism)

**Week 3–4 (FMCW upgrade):**
- 🆕 Range-Doppler heatmap (2D)
- 🆕 1D range profile (like a LiDAR sweep)
- 🆕 SAR back-projection (2D wall slice)

**Month 2 (Dual antenna):**
- 🆕 Azimuth estimation (phase difference)
- 🆕 Polar heatmap with range rings
- 🆕 2.5D sector visualisation

**Month 3 (Array / MIMO):**
- 🆕 Full 3D point cloud (Open3D)
- 🆕 Voxel grid mapping
- 🆕 Real-time trajectory tracking
- 🆕 Change detection vs. baseline

**The most bang-for-buck 3D upgrade:** Add a **pan-tilt servo** to your CW Doppler. For £10 in servos + a few lines of Python, you get a scanning radar that produces a 2D polar activity map. That's genuinely useful for security (sector alarms, coverage mapping) and is a stepping stone to FMCW + SAR.
