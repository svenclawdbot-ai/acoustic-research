"""
Guided Wave Defect Detection - Part 3: Defect Localization Algorithm (Self-Contained)
Implements dispersion-based filtering and back-projection localization
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert
import warnings
warnings.filterwarnings('ignore')

print(f"Part 3: Defect Localization Algorithm")
print(f"{'='*60}")

# ============================================================================
# Generate synthetic data inline
# ============================================================================
n_sensors = 32
sensor_spacing = 0.01  # 10 mm
x_array = np.arange(n_sensors) * sensor_spacing
ts = 1e-7
t_duration = 2e-3
t = np.arange(0, t_duration, ts)
n_time = len(t)

f_center = 100e3
omega = 2 * np.pi * f_center
c_g_s0 = 3200  # S0 group velocity
k_s0 = omega / c_g_s0  # Approximate wavenumber
x_defect_true = 0.15  # True defect position (150 mm)

print(f"True defect position: {x_defect_true*1000:.1f} mm")
print(f"Array: {n_sensors} sensors, {sensor_spacing*1000:.1f} mm spacing")
print(f"Group velocity (S0): {c_g_s0:.0f} m/s")

# Generate incident wavefield
def generate_incident(x_array, t, f_center, c_g, k, amplitude=1.0):
    wavefield = np.zeros((len(t), len(x_array)))
    sigma_t = 3 / (2 * np.pi * f_center)
    for i, x in enumerate(x_array):
        delay = x / c_g
        pulse = amplitude * np.exp(-((t - delay)**2) / (2 * sigma_t**2)) * np.cos(2*np.pi*f_center*(t - delay))
        wavefield[:, i] = pulse
    return wavefield

# Generate scattered wavefield
def generate_scattered(x_array, t, f_center, c_g, k, x_defect, amplitude=0.3):
    wavefield = np.zeros((len(t), len(x_array)))
    t_incident = x_defect / c_g
    sigma_t = 3 / (2 * np.pi * f_center)
    for i, x in enumerate(x_array):
        if x >= x_defect:
            delay = t_incident + (x - x_defect) / c_g
            pulse = amplitude * 0.5 * np.exp(-((t - delay)**2) / (2 * sigma_t**2)) * np.cos(2*np.pi*f_center*(t - delay))
            wavefield[:, i] = pulse
        else:
            delay = t_incident + (x_defect - x) / c_g
            pulse = amplitude * 0.2 * np.exp(-((t - delay)**2) / (2 * sigma_t**2)) * np.cos(2*np.pi*f_center*(t - delay))
            wavefield[:, i] = pulse
    return wavefield

incident = generate_incident(x_array, t, f_center, c_g_s0, k_s0, amplitude=1.0)
scattered = generate_scattered(x_array, t, f_center, c_g_s0, k_s0, x_defect_true, amplitude=0.4)
total_wavefield = incident + scattered + 0.05 * np.random.randn(len(t), len(x_array))

# ============================================================================
# STEP 1: Extract incident modes (dispersion-based masking)
# ============================================================================
print(f"\n[Step 1] Extracting incident modes via f-k masking...")

window_t = np.hanning(n_time)[:, np.newaxis]
window_x = np.hanning(n_sensors)[np.newaxis, :]
windowed = total_wavefield * window_t * window_x

fft_2d = np.fft.fft2(windowed)
fft_2d = np.fft.fftshift(fft_2d)

freq = np.fft.fftfreq(n_time, ts)
freq_shifted = np.fft.fftshift(freq)
k = np.fft.fftfreq(n_sensors, sensor_spacing) * 2 * np.pi
k_shifted = np.fft.fftshift(k)

f_positive = freq_shifted[freq_shifted >= 0]
k_full = k_shifted
f_idx_pos = np.where(freq_shifted >= 0)[0]
spectrum_pos = fft_2d[f_idx_pos, :]

# Build dispersion mask
mask = np.zeros_like(spectrum_pos, dtype=bool)
for i, f in enumerate(f_positive):
    if f > 0 and f < 300e3:
        k_expected = k_s0 * (f / f_center)
        k_tolerance = 40 + 0.15 * k_expected
        k_diff = np.abs(k_full - k_expected)
        mask[i, k_diff < k_tolerance] = True
        k_diff_neg = np.abs(k_full + k_expected)
        mask[i, k_diff_neg < k_tolerance] = True

# Apply mask
incident_spectrum = spectrum_pos.copy()
incident_spectrum[~mask] = 0

full_mask = np.zeros_like(fft_2d, dtype=bool)
full_mask[f_idx_pos, :] = mask
full_mask[len(freq_shifted)-f_idx_pos-1, :] = mask

incident_filtered = np.fft.ifft2(np.fft.ifftshift(fft_2d * full_mask))
incident_filtered = np.real(incident_filtered) / (window_t * window_x + 1e-10)

print(f"  Dispersion mask applied: {np.sum(mask)/mask.size*100:.1f}% of spectrum")

# ============================================================================
# STEP 2: Identify scattered energy
# ============================================================================
print(f"\n[Step 2] Isolating scattered energy...")

full_scatter_mask = np.ones_like(fft_2d, dtype=bool)
full_scatter_mask[f_idx_pos, :] = ~mask
full_scatter_mask[len(freq_shifted)-f_idx_pos-1, :] = ~mask

scattered_filtered = np.fft.ifft2(np.fft.ifftshift(fft_2d * full_scatter_mask))
scattered_filtered = np.real(scattered_filtered) / (window_t * window_x + 1e-10)

print(f"  Scattered energy isolated")

# ============================================================================
# STEP 3: Back-project to defect location
# ============================================================================
print(f"\n[Step 3] Back-projection localization...")

def extract_arrival_times(wavefield, t):
    n_time, n_sensors = wavefield.shape
    arrival_times = np.zeros(n_sensors)
    for i in range(n_sensors):
        signal = wavefield[:, i]
        envelope = np.abs(hilbert(signal))
        threshold = 0.05 * np.max(envelope)
        above_thresh = np.where(envelope > threshold)[0]
        if len(above_thresh) > 0:
            arrival_times[i] = t[above_thresh[0]]
        else:
            arrival_times[i] = np.nan
    return arrival_times

t_arrival = extract_arrival_times(scattered_filtered, t)
valid_idx = ~np.isnan(t_arrival)
x_valid = x_array[valid_idx]
t_valid = t_arrival[valid_idx]

print(f"  Valid arrival times: {np.sum(valid_idx)}/{n_sensors}")

# Method 1: Linear TOF fit
x_defect_estimated = None
if len(x_valid) > 5:
    backscatter_candidates = t_valid < np.percentile(t_valid, 50)
    if np.sum(backscatter_candidates) > 3:
        x_back = x_valid[backscatter_candidates]
        t_back = t_valid[backscatter_candidates]
        A = np.vstack([x_back, np.ones(len(x_back))]).T
        b, a = np.linalg.lstsq(A, t_back, rcond=None)[0]
        c_g_estimated = -1 / b if b != 0 else c_g_s0
        x_defect_estimated = a * c_g_estimated / 2
        print(f"\n  Method 1: Linear TOF fit")
        print(f"    Estimated: {x_defect_estimated*1000:.1f} mm")
        print(f"    Error: {abs(x_defect_estimated - x_defect_true)*1000:.1f} mm")

# Method 2: Back-projection imaging
x_image = np.linspace(0, 0.5, 200)
defect_image = np.zeros_like(x_image)
for i, x_d in enumerate(x_image):
    t_expected = x_d / c_g_s0 + np.abs(x_array - x_d) / c_g_s0
    if len(t_valid) > 5:
        residuals = np.abs(t_valid - t_expected[valid_idx])
        coherence = np.exp(-np.mean(residuals) / 1e-4)
        defect_image[i] = coherence

peak_idx = np.argmax(defect_image)
x_defect_bp = x_image[peak_idx]
print(f"\n  Method 2: Back-projection")
print(f"    Estimated: {x_defect_bp*1000:.1f} mm")
print(f"    Error: {abs(x_defect_bp - x_defect_true)*1000:.1f} mm")

# Method 3: Energy-based
energy = np.sum(scattered_filtered**2, axis=0)
energy_center = np.sum(x_array * energy) / np.sum(energy)
print(f"\n  Method 3: Energy-weighted")
print(f"    Estimated: {energy_center*1000:.1f} mm")
print(f"    Error: {abs(energy_center - x_defect_true)*1000:.1f} mm")

# ============================================================================
# Visualization
# ============================================================================
fig = plt.figure(figsize=(16, 10))

# Plot setup
extent = [x_array[0]*1000, x_array[-1]*1000, t[-1]*1000, t[0]*1000]

ax1 = fig.add_subplot(2, 3, 1)
im1 = ax1.imshow(total_wavefield, aspect='auto', extent=extent, cmap='RdBu_r', vmin=-1, vmax=1)
ax1.axvline(x=x_defect_true*1000, color='green', linestyle='--', linewidth=2, alpha=0.7)
ax1.set_xlabel('Position (mm)', fontsize=11)
ax1.set_ylabel('Time (ms)', fontsize=11)
ax1.set_title('(a) Total Wavefield', fontsize=12)
plt.colorbar(im1, ax=ax1)

ax2 = fig.add_subplot(2, 3, 2)
im2 = ax2.imshow(incident_filtered, aspect='auto', extent=extent, cmap='RdBu_r', vmin=-1, vmax=1)
ax2.set_xlabel('Position (mm)', fontsize=11)
ax2.set_ylabel('Time (ms)', fontsize=11)
ax2.set_title('(b) Filtered Incident (S0)', fontsize=12)
plt.colorbar(im2, ax=ax2)

ax3 = fig.add_subplot(2, 3, 3)
im3 = ax3.imshow(scattered_filtered, aspect='auto', extent=extent, cmap='RdBu_r', vmin=-0.5, vmax=0.5)
ax3.axvline(x=x_defect_true*1000, color='green', linestyle='--', linewidth=2, alpha=0.7)
ax3.axvline(x=x_defect_bp*1000, color='red', linestyle=':', linewidth=2, alpha=0.7)
ax3.set_xlabel('Position (mm)', fontsize=11)
ax3.set_ylabel('Time (ms)', fontsize=11)
ax3.set_title('(c) Filtered Scattered', fontsize=12)
plt.colorbar(im3, ax=ax3)

ax4 = fig.add_subplot(2, 3, 4)
ax4.scatter(x_valid*1000, t_valid*1e6, c='blue', s=50, label='Measured arrivals', zorder=3)
if x_defect_estimated is not None and len(x_valid) > 5:
    backscatter_candidates = t_valid < np.percentile(t_valid, 50)
    if np.sum(backscatter_candidates) > 3:
        x_back = x_valid[backscatter_candidates]
        t_back = t_valid[backscatter_candidates]
        A = np.vstack([x_back, np.ones(len(x_back))]).T
        b, a = np.linalg.lstsq(A, t_back, rcond=None)[0]
        x_fit = np.linspace(x_valid.min(), x_valid.max(), 100)
        t_fit = a + b * x_fit
        ax4.plot(x_fit*1000, t_fit*1e6, 'r--', linewidth=2, label='Linear fit', zorder=2)
ax4.set_xlabel('Sensor Position (mm)', fontsize=11)
ax4.set_ylabel('Arrival Time (μs)', fontsize=11)
ax4.set_title('(d) Arrival Times', fontsize=12)
ax4.legend()
ax4.grid(True, alpha=0.3)

ax5 = fig.add_subplot(2, 3, 5)
ax5.plot(x_image*1000, defect_image, 'b-', linewidth=2)
ax5.axvline(x=x_defect_true*1000, color='green', linestyle='--', linewidth=2, label=f'True: {x_defect_true*1000:.0f} mm', alpha=0.7)
ax5.axvline(x=x_defect_bp*1000, color='red', linestyle=':', linewidth=2, label=f'Est: {x_defect_bp*1000:.0f} mm', alpha=0.7)
ax5.set_xlabel('Defect Position (mm)', fontsize=11)
ax5.set_ylabel('Coherence', fontsize=11)
ax5.set_title('(e) Back-Projection', fontsize=12)
ax5.legend()
ax5.grid(True, alpha=0.3)

ax6 = fig.add_subplot(2, 3, 6)
ax6.axis('off')
ax6.set_title('(f) Results Summary', fontsize=12)

est_str = f"{x_defect_estimated*1000:.1f} mm" if x_defect_estimated else "N/A"
err_str = f"{abs(x_defect_estimated - x_defect_true)*1000:.1f} mm" if x_defect_estimated else "N/A"

results_text = f"""DEFECT LOCALIZATION RESULTS

True position: {x_defect_true*1000:.1f} mm

Method 1: Linear TOF fit
  Estimated: {est_str}
  Error: {err_str}

Method 2: Back-projection
  Estimated: {x_defect_bp*1000:.1f} mm
  Error: {abs(x_defect_bp - x_defect_true)*1000:.1f} mm

Method 3: Energy-weighted
  Estimated: {energy_center*1000:.1f} mm
  Error: {abs(energy_center - x_defect_true)*1000:.1f} mm

PIPELINE SUMMARY:
1. ✓ Dispersion masking → extracted incident S0
2. ✓ Residual isolation → scattered field
3. ✓ Back-projection → localized defect
"""

ax6.text(0.05, 0.95, results_text, transform=ax6.transAxes, fontsize=10,
         verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))

plt.tight_layout()
plt.savefig('/home/james/.openclaw/workspace/defect_localization.png', dpi=150, bbox_inches='tight')
plt.show()

print(f"\n{'='*60}")
print(f"Part 3 Complete: Defect Localization Algorithm")
print(f"{'='*60}")
print(f"Saved: defect_localization.png")
