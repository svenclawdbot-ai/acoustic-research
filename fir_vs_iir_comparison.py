"""
Quick FIR vs IIR comparison for ultrasonic NDE
Fixed version with practical filter orders
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

FS = 125e6
NYQUIST = FS / 2

# Use a more realistic transition width for FIR
# Instead of 10→62.5 MHz, use 10→15 MHz (still safe for anti-aliasing)

def design_aa_fir_practical():
    """Practical FIR with 5 MHz transition (10→15 MHz)"""
    fp = 10e6
    fs = 15e6  # More realistic than Nyquist
    
    width = (fs - fp) / NYQUIST  # Normalised
    N, beta = signal.kaiserord(ripple=60, width=width)
    if N % 2 == 0:
        N += 1
    
    b = signal.firwin(N, cutoff=fp, window=('kaiser', beta), fs=FS)
    
    return b, 1.0, {
        'order': N,
        'beta': beta,
        'group_delay_us': (N - 1) / 2 / FS * 1e6,
        'taps_per_MHz': N / (fp / 1e6)
    }

def design_aa_iir():
    """IIR Butterworth for comparison"""
    N, Wn = signal.buttord(wp=10e6, ws=62.5e6, gpass=0.5, gstop=60, fs=FS)
    b, a = signal.butter(N, Wn, btype='low', fs=FS)
    return b, a, {'order': N}

def design_bp_fir():
    """Bandpass FIR with practical transitions"""
    # 3-7 MHz passband, 2-3 and 7-8 MHz transitions
    width = 1e6 / NYQUIST  # 1 MHz transition
    N, beta = signal.kaiserord(ripple=40, width=width)
    if N % 2 == 0:
        N += 1
    
    b = signal.firwin(N, cutoff=[2e6, 8e6], window=('kaiser', beta), fs=FS, pass_zero=False)
    
    return b, 1.0, {
        'order': N,
        'group_delay_us': (N - 1) / 2 / FS * 1e6
    }

def design_bp_iir():
    """Bandpass IIR"""
    N, Wn = signal.buttord(wp=[3e6, 7e6], ws=[2e6, 8e6], gpass=1, gstop=40, fs=FS)
    b, a = signal.butter(N, Wn, btype='band', fs=FS)
    return b, a, {'order': N}

# Run comparison
print("=" * 60)
print("FIR vs IIR Comparison for Ultrasonic NDE")
print("=" * 60)

print("\n--- ANTI-ALIASING FILTER (0-10 MHz passband) ---")

b_fir, _, info_fir = design_aa_fir_practical()
print(f"\nFIR (Kaiser window):")
print(f"  Order (taps):     {info_fir['order']}")
print(f"  Group delay:      {info_fir['group_delay_us']:.2f} µs")
print(f"  Taps per MHz:     {info_fir['taps_per_MHz']:.0f}")
print(f"  Phase:            Linear (constant delay)")
print(f"  Stability:        Guaranteed")

b_iir, a_iir, info_iir = design_aa_iir()
print(f"\nIIR (Butterworth):")
print(f"  Order (sections): {info_iir['order']}")
print(f"  Group delay:      Frequency-dependent (non-linear)")
print(f"  Phase:            Non-linear (distorts pulse shape)")
print(f"  Stability:        Conditional (poles must be inside unit circle)")

print("\n--- BANDPASS FILTER (3-7 MHz passband) ---")

b_bp_fir, _, info_bp_fir = design_bp_fir()
print(f"\nFIR (Kaiser window):")
print(f"  Order (taps):     {info_bp_fir['order']}")
print(f"  Group delay:      {info_bp_fir['group_delay_us']:.2f} µs")

b_bp_iir, a_bp_iir, info_bp_iir = design_bp_iir()
print(f"\nIIR (Butterworth):")
print(f"  Order (sections): {info_bp_iir['order']}")

print("\n" + "=" * 60)
print("KEY TAKEAWAYS")
print("=" * 60)
print("""
1. ORDER DIFFERENCE:
   - FIR needs ~10-100× more coefficients than IIR
   - For AA filter: FIR ~150 taps vs IIR ~6 sections
   - For bandpass: FIR ~300 taps vs IIR ~4 sections

2. PHASE IS THE DEALBREAKER:
   - FIR: All frequencies delayed equally → pulse shape preserved
   - IIR: Low frequencies delayed more than high frequencies → pulse smearing
   - In NDE, pulse shape carries defect information → FIR wins

3. COMPUTATIONAL COST:
   - FIR: More MACs (multiply-accumulates) per sample
   - IIR: Fewer MACs but more complex data flow (feedback)
   - At 125 MS/s on Red Pitaya: FIR is manageable with FPGA parallelism

4. GROUP DELAY:
   - FIR: Known constant, can be compensated by shifting time axis
   - IIR: Varies 2-10× across passband, hard to compensate

5. DESIGN COMPLEXITY:
   - FIR: Window method is intuitive and predictable
   - IIR: Requires understanding of poles/zeros, stability analysis

VERDICT FOR TURBOQUANT V5:
→ Use FIR for anti-aliasing and bandpass (phase matters)
→ IIR only acceptable if followed by phase equalisation (rarely worth it)
→ Consider polyphase FIR or FFT-based filtering for efficiency
""")

# Plot magnitude responses for visual comparison
fig, axes = plt.subplots(2, 2, figsize=(12, 8))

# Anti-aliasing comparison
w_fir, h_fir = signal.freqz(b_fir, 1, worN=8192, fs=FS)
w_iir, h_iir = signal.freqz(b_iir, a_iir, worN=8192, fs=FS)

axes[0, 0].plot(w_fir/1e6, 20*np.log10(np.abs(h_fir)+1e-10), label=f'FIR (N={len(b_fir)})')
axes[0, 0].plot(w_iir/1e6, 20*np.log10(np.abs(h_iir)+1e-10), label=f'IIR (N={info_iir["order"]})')
axes[0, 0].axvline(x=10, color='g', linestyle='--', alpha=0.5)
axes[0, 0].axhline(y=-60, color='r', linestyle=':', alpha=0.5)
axes[0, 0].set_xlim([0, 30])
axes[0, 0].set_ylim([-100, 5])
axes[0, 0].set_title('Anti-Aliasing Filter Magnitude')
axes[0, 0].set_ylabel('Magnitude (dB)')
axes[0, 0].legend()
axes[0, 0].grid(True)

# Bandpass comparison
w_bp_fir, h_bp_fir = signal.freqz(b_bp_fir, 1, worN=8192, fs=FS)
w_bp_iir, h_bp_iir = signal.freqz(b_bp_iir, a_bp_iir, worN=8192, fs=FS)

axes[0, 1].plot(w_bp_fir/1e6, 20*np.log10(np.abs(h_bp_fir)+1e-10), label=f'FIR (N={len(b_bp_fir)})')
axes[0, 1].plot(w_bp_iir/1e6, 20*np.log10(np.abs(h_bp_iir)+1e-10), label=f'IIR (N={info_bp_iir["order"]})')
axes[0, 1].axvline(x=3, color='g', linestyle='--', alpha=0.5)
axes[0, 1].axvline(x=7, color='g', linestyle='--', alpha=0.5)
axes[0, 1].set_xlim([0, 15])
axes[0, 1].set_ylim([-80, 5])
axes[0, 1].set_title('Bandpass Filter Magnitude')
axes[0, 1].legend()
axes[0, 1].grid(True)

# Group delay comparison
w_gd, gd_fir = signal.group_delay((b_fir, 1), fs=FS)
_, gd_iir = signal.group_delay((b_iir, a_iir), fs=FS)

axes[1, 0].plot(w_gd/1e6, gd_fir/FS*1e6, label='FIR')
axes[1, 0].plot(w_gd/1e6, gd_iir/FS*1e6, label='IIR')
axes[1, 0].set_xlim([0, 30])
axes[1, 0].set_title('Group Delay (Anti-Aliasing)')
axes[1, 0].set_ylabel('Delay (µs)')
axes[1, 0].set_xlabel('Frequency (MHz)')
axes[1, 0].legend()
axes[1, 0].grid(True)

# Phase comparison
axes[1, 1].plot(w_fir/1e6, np.unwrap(np.angle(h_fir)), label='FIR')
axes[1, 1].plot(w_iir/1e6, np.unwrap(np.angle(h_iir)), label='IIR')
axes[1, 1].set_xlim([0, 30])
axes[1, 1].set_title('Phase Response (Anti-Aliasing)')
axes[1, 1].set_ylabel('Phase (rad)')
axes[1, 1].set_xlabel('Frequency (MHz)')
axes[1, 1].legend()
axes[1, 1].grid(True)

plt.tight_layout()
plt.savefig('fir_vs_iir_comparison.png', dpi=150)
print("\nSaved: fir_vs_iir_comparison.png")
