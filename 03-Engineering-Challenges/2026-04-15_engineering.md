# Engineering Challenge — 2026-04-15 (Wednesday)
## Acoustic NDE: DMA Streaming + Real-Time Beamforming Integration

### Background

Your acoustic NDE research has made significant strides on two parallel fronts:

**Week 1-2: Signal Processing Pipeline**
- Shear wave dispersion analysis with 4× accuracy improvement (7.4% → 1.8%)
- Adaptive wavelet denoising with SNR-aware thresholding
- GCC-PHAT sub-sample arrival time estimation
- Quality-gated acquisition pipeline

**Hardware Progress (Recent)**
- DMA acquisition system for ESP32-S3 with PSRAM buffering (4MB ring buffer)
- Flexural beam mechanical design for shear wave generation (200 Hz target)
- Array control firmware with beamforming delay calculation
- End-to-end pipeline: Array firing → DMA capture → Host verification

**Today's Challenge** bridges these streams: integrate real-time beamforming with DMA streaming, enabling live elastography data acquisition from the flexural-beam-coupled transducer array.

---

## Part 1: Beamforming Weight Calculation for Shear Wave Mode (45 min)

### Problem
Your existing array firmware calculates delays for longitudinal waves. For shear wave elastography via flexural beam coupling, you need steering weights that account for:
1. The transverse wave generated at the beam tip
2. Variable angle propagation into tissue
3. Frequency-dependent phase shifts from the mechanical resonator

### Tasks

1. **Flexural beam transfer function**
   ```python
   def flexural_transfer_function(f, beam_params):
       """
       Compute complex transfer function of flexural beam.
       
       Parameters:
       -----------
       f : array
           Frequencies in Hz
       beam_params : dict
           - L: beam length (m)
           - b: width (m)
           - h: thickness (m)
           - E: Young's modulus (Pa)
           - rho: density (kg/m³)
           - m_tip: tip mass (kg)
       
       Returns:
       --------
       H(f) : complex transfer function
       """
       # Euler-Bernoulli cantilever with tip mass
       # H(f) = tip_displacement / base_excitation
       
       E = beam_params['E']
       rho = beam_params['rho']
       L = beam_params['L']
       b = beam_params['b']
       h = beam_params['h']
       m_tip = beam_params.get('m_tip', 0)
       
       I = b * h**3 / 12
       A = b * h
       
       # Effective stiffness and mass
       k_eff = 3 * E * I / L**3
       m_eff = 0.23 * rho * A * L + m_tip
       
       # Natural frequency
       f_n = (1 / (2*np.pi)) * np.sqrt(k_eff / m_eff)
       
       # Damping (assume 5% for aluminum)
       zeta = 0.05
       
       # Transfer function: second-order resonator
       s = 1j * 2 * np.pi * f
       omega_n = 2 * np.pi * f_n
       
       H = 1 / (m_eff * (s**2 + 2*zeta*omega_n*s + omega_n**2))
       
       # Normalize to unity at resonance
       H = H / np.abs(H[np.argmin(np.abs(f - f_n))])
       
       return H
   ```

2. **Shear wave steering vector**
   ```python
   def shear_wave_steering_vector(x_array, y_array, theta_steering, c_shear, f,
                                   beam_params=None):
       """
       Generate steering vector for shear wave beamforming.
       
       Parameters:
       -----------
       x_array, y_array : arrays
           Element positions (m)
       theta_steering : float
           Steering angle (degrees)
       c_shear : float
           Shear wave speed in tissue (m/s, typically 1-5 m/s)
       f : float
           Frequency (Hz)
       beam_params : dict (optional)
           Flexural beam parameters for phase correction
       
       Returns:
       --------
       w : complex array (N_elements,)
           Steering weights
       """
       theta_rad = np.deg2rad(theta_steering)
       
       # Time delays for plane wave at angle theta
       k = 2 * np.pi * f / c_shear
       delays = (x_array * np.sin(theta_rad) + y_array * np.cos(theta_rad)) / c_shear
       
       # Phase weights
       phase_weights = np.exp(-1j * 2 * np.pi * f * delays)
       
       # Apply flexural beam transfer function correction
       if beam_params:
           H = flexural_transfer_function(np.array([f]), beam_params)[0]
           # Compensate for mechanical resonator phase
           phase_weights *= np.exp(-1j * np.angle(H))
       
       # Normalize
       w = phase_weights / np.sum(np.abs(phase_weights))
       
       return w
   ```

3. **Validate on simulated array data**
   - Generate 4-element array with 5mm spacing
   - Simulate plane shear wave at 30° from 100 Hz source
   - Compare: (a) no beamforming, (b) conventional delay-sum, (c) flexural-corrected
   - Measure SNR improvement and arrival time accuracy

### Deliverable
- `beamforming_shear.py` module with steering functions
- Plot: array gain vs steering angle for different methods

---

## Part 2: DMA Trigger Synchronization Protocol (60 min)

### Problem
Your DMA acquisition needs to capture data synchronized with the array firing sequence. The current system has separate "array control" and "DMA acquisition" subsystems that need tight coordination.

### Tasks

1. **Define trigger protocol**
   ```c
   // In array_dma_integration.c
   
   typedef enum {
       TRIGGER_NONE = 0,
       TRIGGER_IMMEDIATE,
       TRIGGER_EXTERNAL_GPIO,
       TRIGGER_ARRAY_SYNC  // New: sync with array firing
   } TriggerMode;
   
   typedef struct {
       TriggerMode mode;
       uint32_t pre_trigger_samples;  // Capture before trigger
       uint32_t post_trigger_samples; // Capture after trigger
       uint32_t delay_us;             // Delay after array trigger
   } SyncConfig;
   ```

2. **Implement array-sync trigger**
   ```c
   void dma_set_array_sync_trigger(uint32_t element_mask, uint32_t delay_us) {
       // Configure DMA to trigger after array elements fire
       // 1. Enable external trigger on GPIO (connected to array done signal)
       // 2. Set delay timer for post-firing capture
       // 3. Pre-fill buffer with pre-trigger samples if needed
       
       sync_config.mode = TRIGGER_ARRAY_SYNC;
       sync_config.delay_us = delay_us;
       
       // Configure ADC timer for pre-trigger sampling
       if (sync_config.pre_trigger_samples > 0) {
           // Start continuous sampling into circular buffer
           dma_start_pretrigger_buffer(sync_config.pre_trigger_samples);
       }
       
       // Wait for array trigger GPIO
       gpio_enable_interrupt(TRIGGER_GPIO_PIN);
   }
   ```

3. **Host-side sync command**
   ```python
   def capture_synced_acquisition(ser, array_config, delay_us=100, 
                                   pre_trigger_ms=5, post_trigger_ms=50):
       """
       Fire array and capture synchronized DMA data.
       
       Parameters:
       -----------
       ser : Serial
           USB serial connection to ESP32
       array_config : dict
           Element delays and weights
       delay_us : int
           Microseconds between array fire and DMA start
       pre_trigger_ms : float
           Capture time before trigger (ms)
       post_trigger_ms : float
           Capture time after trigger (ms)
       
       Returns:
       --------
       data : ndarray (n_channels, n_samples)
           Synchronized capture
       timestamp : float
           Acquisition timestamp
       """
       import struct
       import json
       
       # Calculate sample counts
       fs = 1e6  # 1 MHz (conservative for 8ch)
       pre_samples = int(pre_trigger_ms * 1e-3 * fs)
       post_samples = int(post_trigger_ms * 1e-3 * fs)
       
       # Configure sync trigger
       cmd = {
           "cmd": "dma_sync_config",
           "mode": "array_sync",
           "pre_trigger": pre_samples,
           "post_trigger": post_samples,
           "delay_us": delay_us
       }
       ser.write(json.dumps(cmd).encode() + b'\n')
       
       # Configure array firing
       array_cmd = {
           "cmd": "fire_array",
           "delays": array_config['delays'],
           "elements": array_config['elements'],
           "wait_for_sync": True  # Don't fire until DMA ready
       }
       ser.write(json.dumps(array_cmd).encode() + b'\n')
       
       # Wait for data
       response = ser.readline().decode()
       result = json.loads(response)
       
       # Read binary data
       n_bytes = result['total_bytes']
       data_bytes = ser.read(n_bytes)
       
       # Parse into array
       n_channels = result['channels']
       n_samples = result['samples_per_channel']
       data = np.frombuffer(data_bytes, dtype=np.uint16)
       data = data.reshape(n_samples, n_channels).T
       
       return data, result['timestamp']
   ```

4. **Validate timing precision**
   - Connect GPIO pulse generator as mock "array done" signal
   - Measure actual delay between trigger and first sample
   - Verify jitter < 10 µs for elastography requirements

### Deliverable
- Updated `array_dma_integration.c` with sync protocol
- Python `sync_capture.py` module
- Timing validation report (oscilloscope or logic analyzer output)

---

## Part 3: Real-Time Shear Wave Beamformer (60 min)

### Problem
Combine the beamforming weights with DMA-captured data to implement a real-time shear wave beamformer that processes incoming data in near real-time.

### Tasks

1. **Streaming beamformer class**
   ```python
   class ShearWaveBeamformer:
       """
       Real-time beamformer for shear wave elastography.
       """
       
       def __init__(self, element_positions, c_shear=3.0, 
                    beam_params=None, n_avg=10):
           """
           Parameters:
           -----------
           element_positions : array (N, 2)
               (x, y) positions of array elements in meters
           c_shear : float
               Assumed shear wave speed (m/s)
           beam_params : dict
               Flexural beam parameters
           n_avg : int
           Number of acquisitions to average
           """
           self.positions = np.array(element_positions)
           self.c_shear = c_shear
           self.beam_params = beam_params
           self.n_avg = n_avg
           self.buffer = []
           
       def compute_weights(self, theta, f_center):
           """Compute steering weights for given angle and frequency."""
           x = self.positions[:, 0]
           y = self.positions[:, 1]
           
           return shear_wave_steering_vector(
               x, y, theta, self.c_shear, f_center,
               self.beam_params
           )
       
       def process_frame(self, raw_data, fs, theta=0, f_center=100):
           """
           Beamform a single acquisition frame.
           
           Parameters:
           -----------
           raw_data : array (n_channels, n_samples)
               Raw DMA-captured data
           fs : float
               Sample rate (Hz)
           theta : float
               Steering angle (degrees)
           f_center : float
           Center frequency for beamforming (Hz)
           
           Returns:
           --------
           beamformed : array (n_samples,)
               Beamformed output
           """
           n_channels, n_samples = raw_data.shape
           
           # Get steering weights
           w = self.compute_weights(theta, f_center)
           
           # Optional: time-domain delays for wideband
           # For narrowband, just complex weight and sum
           
           # Simple delay-sum (for now)
           beamformed = np.zeros(n_samples)
           for i, (delay, weight) in enumerate(zip(
               np.angle(w) / (2*np.pi*f_center), np.abs(w))):
               delay_samples = int(delay * fs)
               shifted = np.roll(raw_data[i], delay_samples)
               beamformed += weight * shifted
           
           return beamformed
       
       def update_estimate(self, raw_data, fs):
           """
           Update running estimate with new acquisition.
           """
           # Beamform at multiple angles
           angles = np.linspace(-45, 45, 11)
           
           results = {}
           for theta in angles:
               bf = self.process_frame(raw_data, fs, theta)
               
               # Extract metrics: peak amplitude, arrival time
               peak_idx = np.argmax(np.abs(bf))
               arrival_time = peak_idx / fs
               peak_amp = np.max(np.abs(bf))
               
               results[theta] = {
                   'signal': bf,
                   'arrival_time': arrival_time,
                   'peak_amplitude': peak_amp
               }
           
           self.buffer.append(results)
           if len(self.buffer) > self.n_avg:
               self.buffer.pop(0)
           
           return results
       
       def get_average_dispersion(self):
           """
           Compute average dispersion curve from buffer.
           """
           # Aggregate arrival times across angles
           # Fit to Kelvin-Voigt model
           # Return G', eta estimates
           pass
   ```

2. **Live display integration**
   ```python
   def run_live_beamformer(port='/dev/ttyUSB0', duration=30):
       """
       Run real-time beamformer with live display.
       """
       import pyqtgraph as pg
       from pyqtgraph.Qt import QtCore, QtWidgets
       
       # Initialize hardware
       ser = serial.Serial(port, 921600, timeout=1)
       
       # Configure beamformer
       positions = np.array([[0, 0], [0.005, 0], [0.01, 0], [0.015, 0]])
       beam_params = {
           'L': 0.060, 'b': 0.015, 'h': 0.002,
           'E': 69e9, 'rho': 2700, 'm_tip': 0.005
       }
       
       bf = ShearWaveBeamformer(positions, c_shear=2.5, 
                                 beam_params=beam_params)
       
       # Setup PyQtGraph display
       app = QtWidgets.QApplication([])
       win = pg.GraphicsLayoutWidget(show=True, title="Live Shear Wave Beamformer")
       
       # Waveform plot
       waveform_plot = win.addPlot(title="Beamformed Signal")
       waveform_curve = waveform_plot.plot(pen='y')
       
       # Angle scan plot
       win.nextRow()
       angle_plot = win.addPlot(title="Signal vs Steering Angle")
       angle_curve = angle_plot.plot(pen=None, symbol='o')
       
       # Dispersion curve
       win.nextRow()
       dispersion_plot = win.addPlot(title="Dispersion Estimate")
       
       def update():
           # Trigger acquisition
           data, _ = capture_synced_acquisition(ser, 
               array_config={'delays': [0, 0, 0, 0], 'elements': [0,1,2,3]},
               delay_us=50, pre_trigger_ms=2, post_trigger_ms=20)
           
           # Process
           fs = 1e6
           results = bf.update_estimate(data, fs)
           
           # Update plots
           center_angle = 0
           wf = results[center_angle]['signal']
           waveform_curve.setData(wf)
           
           angles = list(results.keys())
           amps = [results[a]['peak_amplitude'] for a in angles]
           angle_curve.setData(angles, amps)
       
       timer = QtCore.QTimer()
       timer.timeout.connect(update)
       timer.start(100)  # 10 Hz update rate
       
       QtWidgets.QApplication.instance().exec_()
   ```

3. **Performance benchmarks**
   - Processing latency per frame (target: < 50 ms for real-time)
   - Beamforming gain vs single element (target: > 6 dB)
   - Angle resolution with 4-element array

### Deliverable
- `shear_wave_beamformer.py` module
- Live display script
- Performance benchmark results

---

## Part 4: End-to-End Validation Test (45 min)

### Problem
Validate the complete chain: flexural beam → array firing → DMA capture → beamforming → dispersion estimate.

### Tasks

1. **Synthetic end-to-end test**
   ```python
   def generate_realistic_shear_wave_acquisition(
       G_prime=2000, eta=0.5, rho=1000,
       element_positions=None,
       beam_params=None,
       theta_source=30,
       noise_level=0.05,
       coupling_variation=0.1
   ):
       """
       Generate realistic synthetic acquisition through full chain.
       """
       # 1. Compute theoretical dispersion
       from shear_wave_pipeline import kelvin_voigt_dispersion
       
       frequencies = np.linspace(50, 200, 20)
       c_t = kelvin_voigt_dispersion(frequencies, G_prime, eta, rho)
       
       # 2. Generate source signal (200 Hz tone burst)
       fs = 1e6
       duration = 0.05
       t = np.arange(0, duration, 1/fs)
       
       f_center = 100
       n_cycles = 5
       tone_burst = np.sin(2*np.pi*f_center*t) * \
                    (t < n_cycles/f_center)
       
       # 3. Propagate to each array element
       if element_positions is None:
           element_positions = np.array([[0, 0], [0.005, 0], 
                                          [0.01, 0], [0.015, 0]])
       
       # Distance and time delay from source at angle
       source_dist = 0.1  # 10 cm away
       source_x = source_dist * np.sin(np.deg2rad(theta_source))
       source_y = source_dist * np.cos(np.deg2rad(theta_source))
       
       distances = np.sqrt((element_positions[:,0] - source_x)**2 + 
                           (element_positions[:,1] - source_y)**2)
       arrival_times = distances / c_t[np.argmin(np.abs(frequencies - f_center))]
       
       # 4. Apply flexural beam transfer function
       if beam_params:
           H = flexural_transfer_function(f_center, beam_params)
           amplitude_scale = np.abs(H)
           phase_shift = np.angle(H)
       else:
           amplitude_scale = 1.0
           phase_shift = 0
       
       # 5. Generate element signals
       signals = []
       for i, (dist, t_arr) in enumerate(zip(distances, arrival_times)):
           # Attenuation with distance (geometric spreading)
           amp = amplitude_scale * (0.05 / dist)  # Reference at 5cm
           
           # Add per-element coupling variation
           amp *= (1 + coupling_variation * np.random.randn())
           
           # Delay and add noise
           delay_samples = int(t_arr * fs)
           sig = np.zeros_like(t)
           if delay_samples < len(sig):
               sig[delay_samples:] = amp * tone_burst[:len(sig)-delay_samples]
           
           # Add phase shift from beam
           sig = np.real(np.fft.ifft(
               np.fft.fft(sig) * np.exp(1j * phase_shift)
           ))
           
           # Add noise
           noise = noise_level * np.std(sig) * np.random.randn(len(sig))
           signals.append(sig + noise)
       
       return np.array(signals), fs, element_positions, (G_prime, eta)
   ```

2. **Run full pipeline validation**
   ```python
   def validate_full_pipeline():
       """Test complete acquisition and processing chain."""
       
       # Generate synthetic ground truth
       true_G = 2500
       true_eta = 0.8
       
       raw_data, fs, positions, truth = generate_realistic_shear_wave_acquisition(
           G_prime=true_G, eta=true_eta
       )
       
       # Process through beamformer
       beam_params = {
           'L': 0.060, 'b': 0.015, 'h': 0.002,
           'E': 69e9, 'rho': 2700, 'm_tip': 0.005
       }
       
       bf = ShearWaveBeamformer(positions, c_shear=2.5, 
                                 beam_params=beam_params)
       
       results = bf.update_estimate(raw_data, fs)
       
       # Extract arrival times across angles
       # ... fit to dispersion model
       # ... estimate G', eta
       
       estimated_G = 2450  # Placeholder
       estimated_eta = 0.75
       
       # Report accuracy
       G_error = abs(estimated_G - true_G) / true_G * 100
       eta_error = abs(estimated_eta - true_eta) / true_eta * 100
       
       print(f"Ground truth: G' = {true_G} Pa, η = {true_eta} Pa·s")
       print(f"Estimated: G' = {estimated_G} Pa, η = {estimated_eta} Pa·s")
       print(f"Error: G' = {G_error:.1f}%, η = {eta_error:.1f}%")
       
       return G_error, eta_error
   ```

3. **Performance targets**
   | Metric | Target | Achieved |
   |--------|--------|----------|
   | G′ estimation error | < 5% | ? |
   | η estimation error | < 10% | ? |
   | Processing latency | < 100 ms | ? |
   | Beamforming gain | > 6 dB | ? |

### Deliverable
- `validate_e2e.py` test harness
- Accuracy report comparing ground truth to estimates
- Performance metrics table

---

## Extension Challenges (Optional)

### A) Adaptive Beamforming (90 min)
Implement MVDR (Minimum Variance Distortionless Response) beamformer that adapts weights based on measured noise covariance. Compare to fixed steering weights.

### B) Multi-Frequency Processing (60 min)
Extend beamformer to process multiple frequencies simultaneously using filter banks, enabling real-time dispersion curve extraction.

### C) Hardware-in-the-Loop Test (120 min)
With actual flexural beam and Red Pitaya/ESP32 system: capture real ultrasound data, run through beamformer, validate against phantom with known stiffness.

---

## Key Equations Reference

| Component | Equation |
|-----------|----------|
| Flexural beam resonance | f₁ = (1/2π) √(k_eff / m_eff) |
| Shear wave steering | τᵢ = (xᵢ sin θ + yᵢ cos θ) / c |
| Kelvin-Voigt dispersion | c(ω) = √(2/ρ) · √(|G*|² / (G′ + \|G*\|)) |
| Array gain | G = 20 log₁₀(N · |w·a| / √E[\|w·n\|²]) |

---

## Connections to Your Existing Work

| Previous Work | This Challenge |
|---------------|----------------|
| Week 2 signal processing | → Real-time beamforming |
| DMA acquisition firmware | → Synced capture integration |
| Flexural beam design | → Transfer function modeling |
| Quality gate pipeline | → Live validation metrics |

---

## Deliverables Summary

1. **Shear wave beamforming** — angle-dependent steering with flexural correction
2. **DMA sync protocol** — hardware-software trigger coordination
3. **Real-time processor** — live beamforming with display
4. **End-to-end validation** — synthetic test of complete chain

---

**Difficulty:** Intermediate–Advanced (hardware integration focus)
**Est. Time:** 3.5 hours (core) + 2.5 hours (extensions)
**Topic:** Acoustic NDE / Real-Time Signal Processing / Hardware Integration

## Status: 🆕 NOT STARTED

*Generated: 2026-04-15 07:00 UTC*
