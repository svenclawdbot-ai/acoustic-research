"""
Guided Wave Defect Detection - Part 2: 2D-FFT and f-k Analysis
Generate synthetic wavefield and perform frequency-wavenumber analysis
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import chirp, gausspulse
import warnings
warnings.filterwarnings('ignore')

# Sensor array configuration
n_sensors = 32
sensor_spacing = 0.01  # 10 mm
x_array = np.arange(n_sensors) * sensor_spacing  # Sensor positions (m)

# Time configuration
ts = 1e-7  # Sampling interval (10 MHz sampling)
t_duration = 2e-3  # 2 ms duration
t = np.arange(0, t_duration, ts)
n_time = len(t)

# Wave parameters
f_center = 100e3  # 100 kHz center frequency
omega = 2 * np.pi * f_center

# Material (Aluminum 3mm plate) - from Part 1
c_s = 3120  # Shear speed (m/s)
c_l = 6200  # Longitudinal speed (m/s)
c_r = 0.92 * c_s  # Rayleigh speed ~2870 m/s

# At 100 kHz, use S0 mode parameters (from dispersion curves)
c_p_s0 = 3500  # Phase velocity of S0 at 100 kHz (m/s) - from dispersion curve
c_g_s0 = 3200  # Group velocity approximation (m/s)
k_s0 = omega / c_p_s0  # Wavenumber

print(f"Simulation Parameters:")
print(f"  Center frequency: {f_center/1e3:.0f} kHz")
print(f"  Array: {n_sensors} sensors, {sensor_spacing*1000:.1f} mm spacing")
print(f"  Array length: {(n_sensors-1)*sensor_spacing*1000:.1f} mm")
print(f"  S0 mode: c_p = {c_p_s0:.0f} m/s, k = {k_s0:.2f} rad/m")

# Defect position (offset from array center)
x_defect = 0.15  # 150 mm from first sensor

# Generate incident S0 mode wavefield
def generate_incident_wavefield(x_array, t, f_center, c_p, c_g, k, amplitude=1.0):
    """Generate incident S0 Lamb wave propagating through sensor array"""
    wavefield = np.zeros((len(t), len(x_array)))
    
    # Gaussian pulse envelope
    sigma_t = 3 / (2 * np.pi * f_center)  # ~3 cycles
    
    for i, x in enumerate(x_array):
        # Wave arrives at position x with group velocity delay
        delay = x / c_g
        pulse = amplitude * np.exp(-((t - delay)**2) / (2 * sigma_t**2)) * np.cos(2*np.pi*f_center*(t - delay))
        wavefield[:, i] = pulse
    
    return wavefield

# Generate defect-scattered wavefield
def generate_scattered_wavefield(x_array, t, f_center, c_p, c_g, k, x_defect, amplitude=0.3):
    """
    Generate scattered wave from defect.
    Defect acts as secondary source at x_defect.
    """
    wavefield = np.zeros((len(t), len(x_array)))
    
    # Time for incident wave to reach defect
    t_incident = x_defect / c_g
    
    # Scattering occurs when incident wave hits defect
    sigma_t = 3 / (2 * np.pi * f_center)
    
    for i, x in enumerate(x_array):
        if x >= x_defect:
            # Forward scattered (transmission side)
            delay = t_incident + (x - x_defect) / c_g
            # Mode conversion: some energy goes to A0 (slower)
            # S0 scattered component
            pulse_s0 = amplitude * 0.5 * np.exp(-((t - delay)**2) / (2 * sigma_t**2)) * np.cos(2*np.pi*f_center*(t - delay))
            # A0 component (slower, arrives later)
            c_g_a0 = 2000  # Approximate A0 group velocity at 100 kHz
            delay_a0 = t_incident + (x - x_defect) / c_g_a0
            pulse_a0 = amplitude * 0.3 * np.exp(-((t - delay_a0)**2) / (2 * sigma_t**2)) * np.cos(2*np.pi*f_center*(t - delay_a0))
            wavefield[:, i] = pulse_s0 + pulse_a0
        else:
            # Back scattered (reflection - pulse-echo)
            delay = t_incident + (x_defect - x) / c_g
            pulse = amplitude * 0.2 * np.exp(-((t - delay)**2) / (2 * sigma_t**2)) * np.cos(2*np.pi*f_center*(t - delay))
            wavefield[:, i] = pulse
    
    return wavefield

print(f"\nGenerating wavefields...")
print(f"  Defect position: {x_defect*1000:.1f} mm from sensor 0")

# Generate wavefields
incident = generate_incident_wavefield(x_array, t, f_center, c_p_s0, c_g_s0, k_s0, amplitude=1.0)
scattered = generate_scattered_wavefield(x_array, t, f_center, c_p_s0, c_g_s0, k_s0, x_defect, amplitude=0.4)

total_wavefield = incident + scattered

# Add noise
total_wavefield += 0.05 * np.random.randn(*total_wavefield.shape)

print(f"  Wavefield shape: {total_wavefield.shape} (time × space)")

# Apply windowing to reduce spectral leakage
window_t = np.hanning(n_time)[:, np.newaxis]
window_x = np.hanning(n_sensors)[np.newaxis, :]
windowed = total_wavefield * window_t * window_x

# 2D-FFT: Time → Frequency, Space → Wavenumber
fft_2d = np.fft.fft2(windowed)
fft_2d = np.fft.fftshift(fft_2d)

# Frequency and wavenumber axes
freq = np.fft.fftfreq(n_time, ts)
freq_shifted = np.fft.fftshift(freq)
k = np.fft.fftfreq(n_sensors, sensor_spacing) * 2 * np.pi  # rad/m
k_shifted = np.fft.fftshift(k)

# Only keep positive frequencies and relevant wavenumbers
f_positive = freq_shifted[freq_shifted >= 0]
k_relevant = k_shifted[np.abs(k_shifted) <= 1000]  # Limit to ±1000 rad/m

# Extract relevant portion of spectrum
f_idx = np.where(freq_shifted >= 0)[0]
k_idx = np.where(np.abs(k_shifted) <= 1000)[0]
spectrum = np.abs(fft_2d[np.ix_(f_idx, k_idx)])

print(f"  2D-FFT complete")
print(f"  Frequency range: 0 - {f_positive[-1]/1e3:.0f} kHz")
print(f"  Wavenumber range: {k_relevant[0]:.0f} to {k_relevant[-1]:.0f} rad/m")

# Visualization
fig = plt.figure(figsize=(16, 10))

# 1. Time-space wavefield (raw data)
ax1 = fig.add_subplot(2, 3, 1)
extent = [x_array[0]*1000, x_array[-1]*1000, t[-1]*1000, t[0]*1000]
im1 = ax1.imshow(total_wavefield, aspect='auto', extent=extent, cmap='RdBu_r', vmin=-1, vmax=1)
ax1.axvline(x=x_defect*1000, color='green', linestyle='--', linewidth=2, label=f'Defect at {x_defect*1000:.0f} mm')
ax1.set_xlabel('Position (mm)', fontsize=11)
ax1.set_ylabel('Time (ms)', fontsize=11)
ax1.set_title('(a) Total Wavefield (Incident + Scattered)', fontsize=12)
ax1.legend()
plt.colorbar(im1, ax=ax1, label='Amplitude')

# 2. Incident wavefield only
ax2 = fig.add_subplot(2, 3, 2)
im2 = ax2.imshow(incident, aspect='auto', extent=extent, cmap='RdBu_r', vmin=-1, vmax=1)
ax2.set_xlabel('Position (mm)', fontsize=11)
ax2.set_ylabel('Time (ms)', fontsize=11)
ax2.set_title('(b) Incident S0 Mode Only', fontsize=12)
plt.colorbar(im2, ax=ax2, label='Amplitude')

# 3. Scattered wavefield only
ax3 = fig.add_subplot(2, 3, 3)
im3 = ax3.imshow(scattered, aspect='auto', extent=extent, cmap='RdBu_r', vmin=-0.5, vmax=0.5)
ax3.axvline(x=x_defect*1000, color='green', linestyle='--', linewidth=2, label='Defect')
ax3.set_xlabel('Position (mm)', fontsize=11)
ax3.set_ylabel('Time (ms)', fontsize=11)
ax3.set_title('(c) Scattered Field (Defect Response)', fontsize=12)
ax3.legend()
plt.colorbar(im3, ax=ax3, label='Amplitude')

# 4. f-k spectrum (full)
ax4 = fig.add_subplot(2, 3, 4)
extent_fk = [k_relevant[0], k_relevant[-1], f_positive[-1]/1e3, f_positive[0]]
im4 = ax4.imshow(spectrum/1e4, aspect='auto', extent=extent_fk, cmap='hot', vmin=0, vmax=5)

# Overlay expected dispersion curves
fd_plot = f_positive * 2 * 0.0015 / 1e3  # kHz·mm for 3mm plate
# S0 theoretical wavenumber
k_s0_theory = 2 * np.pi * f_positive / c_p_s0
# A0 theoretical (approximate - lower velocity)
c_p_a0 = np.maximum(500, 1000 * np.sqrt(f_positive/1e3))  # Rough approx
k_a0_theory = 2 * np.pi * f_positive / c_p_a0

ax4.plot(k_s0_theory, f_positive/1e3, 'c-', linewidth=2, label='S0 mode')
ax4.plot(-k_s0_theory, f_positive/1e3, 'c-', linewidth=2)
ax4.plot(k_a0_theory, f_positive/1e3, 'g--', linewidth=2, label='A0 mode (approx)')
ax4.plot(-k_a0_theory, f_positive/1e3, 'g--', linewidth=2)

ax4.set_xlabel('Wavenumber k (rad/m)', fontsize=11)
ax4.set_ylabel('Frequency (kHz)', fontsize=11)
ax4.set_title('(d) Frequency-Wavenumber Spectrum', fontsize=12)
ax4.set_xlim(-600, 600)
ax4.set_ylim(0, 300)
ax4.legend(loc='upper right')
plt.colorbar(im4, ax=ax4, label='|D(ω,k)| (×10⁴)')

# 5. Zoomed f-k at center frequency
ax5 = fig.add_subplot(2, 3, 5)
f_center_idx = np.argmin(np.abs(f_positive - f_center))
f_bandwidth = 20  # ±20 kHz around center
f_low_idx = np.argmin(np.abs(f_positive - (f_center - f_bandwidth*1e3)))
f_high_idx = np.argmin(np.abs(f_positive - (f_center + f_bandwidth*1e3)))

spectrum_slice = spectrum[f_low_idx:f_high_idx, :].mean(axis=0)
ax5.plot(k_relevant, spectrum_slice/1e4, 'b-', linewidth=2)
ax5.axvline(x=k_s0, color='r', linestyle='--', linewidth=2, label=f'S0: k={k_s0:.1f} rad/m')
ax5.axvline(x=-k_s0, color='r', linestyle='--', linewidth=2)
ax5.axvline(x=k_s0*1.5, color='g', linestyle=':', alpha=0.7, label='Scattered energy')
ax5.set_xlabel('Wavenumber k (rad/m)', fontsize=11)
ax5.set_ylabel('|D(ω,k)| (×10⁴)', fontsize=11)
ax5.set_title(f'(e) Spectrum Slice @ {f_center/1e3:.0f} kHz ±{f_bandwidth} kHz', fontsize=12)
ax5.legend()
ax5.set_xlim(-400, 400)
ax5.grid(True, alpha=0.3)

# 6. Defect detection principle illustration
ax6 = fig.add_subplot(2, 3, 6)
ax6.axis('off')
ax6.set_title('(f) Defect Detection Principle', fontsize=12)

diagram_text = """
DEFECT LOCALIZATION FROM f-k SPECTRUM

1. INCIDENT WAVE (k_incident):
   • Energy concentrated along dispersion curve
   • For S0 at 100 kHz: k ≈ 180 rad/m
   • Propagates: +x direction → k > 0

2. SCATTERED WAVE (k_scattered):
   • Defect acts as secondary source
   • Creates hyperbolic arcs in f-k domain
   • Contains mode-converted energy (A0)

3. LOCALIZATION:
   • Back-scattered: k_back = -k_incident
     → Arrives at sensors BEFORE incident
     → Use time-of-flight: x_defect = c_g × Δt/2
   
   • Forward-scattered: k_forward = +k_incident  
     → Arrives AFTER passing defect
     → Contains mode conversion (S0→A0)

4. FILTERING:
   • Mask incident mode along dispersion ridge
   • Residual energy = scattered field
   • Back-project to localize defect

Key Equation:
  x_defect = (c_g × t_arrival) / 2  (pulse-echo)
"""
ax6.text(0.05, 0.95, diagram_text, transform=ax6.transAxes, fontsize=10,
         verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig('/home/james/.openclaw/workspace/fk_analysis.png', dpi=150, bbox_inches='tight')
plt.show()

print(f"\n{'='*60}")
print(f"Part 2: 2D-FFT and f-k Analysis Complete")
print(f"{'='*60}")
print(f"Key observations:")
print(f"  • Incident S0 mode: k ≈ ±{k_s0:.0f} rad/m at {f_center/1e3:.0f} kHz")
print(f"  • Defect creates scattered energy across multiple k values")
print(f"  • Mode conversion visible: S0 → A0 (lower velocity)")
print(f"  • f-k filtering can separate incident from scattered waves")

# Save data for Part 3
np.savez('/home/james/.openclaw/workspace/wavefield_data.npz',
         total=total_wavefield,
         incident=incident,
         scattered=scattered,
         t=t, x_array=x_array,
         f_center=f_center, k_s0=k_s0, c_g_s0=c_g_s0,
         x_defect=x_defect)

print(f"\nSaved: fk_analysis.png, wavefield_data.npz")
