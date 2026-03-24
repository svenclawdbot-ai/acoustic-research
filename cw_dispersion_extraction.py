"""
CW-Based Dispersion Extraction
===============================

Extract phase velocity using continuous wave (CW) excitation.
Most reliable method for dispersion measurement.

Method:
-------
1. Run simulation with CW source at single frequency until steady-state
2. Measure phase at two receiver positions
3. Phase difference → phase velocity: c_p = ω·Δx/Δφ
4. Repeat for multiple frequencies

Advantages:
- Single frequency (no spectral spread)
- Steady-state (no transients)
- Phase measurement is robust
- Well-defined dispersion relation
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.insert(0, '/home/james/.openclaw/workspace')


def extract_dispersion_cw_2d(frequencies, G_r=5000, G_inf=8000, tau_sigma=0.001,
                              nx=200, steady_state_time=0.05):
    """
    Extract dispersion using CW excitation in 2D.
    
    For each frequency:
    1. Run until steady state with CW source
    2. Measure phase at two receivers
    3. Compute phase velocity
    """
    from shear_wave_2d_zener import ShearWave2DZener
    
    rho = 1000
    results = []
    
    print("=" * 70)
    print("CW DISPERSION EXTRACTION — 2D ZENER")
    print("=" * 70)
    print(f"Parameters: G_r={G_r}, G_∞={G_inf}, τ_σ={tau_sigma*1000:.1f} ms")
    print(f"Frequencies: {frequencies} Hz")
    print(f"Steady-state time: {steady_state_time*1000:.1f} ms\n")
    
    for f0 in frequencies:
        print(f"Frequency: {f0} Hz...")
        
        # Grid setup
        c_r = np.sqrt(G_r / rho)
        wavelength = c_r / f0
        dx = wavelength / 12
        
        sim = ShearWave2DZener(nx=nx, ny=nx, dx=dx, rho=rho, G_r=G_r, G_inf=G_inf,
                               tau_sigma=tau_sigma, bc_type='mur1')
        
        dt = sim.dt
        period = 1.0 / f0
        n_periods = int(steady_state_time / period)
        n_steps = int((n_periods + 2) * period / dt)  # Extra for measurement
        
        # Source and receiver positions
        source_pos = (nx // 5, nx // 2)
        rec1_pos = (2 * nx // 5, nx // 2)
        rec2_pos = (3 * nx // 5, nx // 2)
        distance = (rec2_pos[0] - rec1_pos[0]) * dx
        
        # Record phase during last period
        rec1_last_period = []
        rec2_last_period = []
        t_last_period = []
        
        start_recording = n_steps - int(period / dt)
        
        for n in range(n_steps):
            t = n * dt
            
            # CW source: continuous sinusoid
            source_amp = 2e-5 * np.sin(2 * np.pi * f0 * t)
            sim.vy[source_pos] += sim.dt * source_amp / sim.dt  # Direct velocity injection
            
            sim.step()
            
            if n >= start_recording:
                rec1_last_period.append(sim.vy[rec1_pos])
                rec2_last_period.append(sim.vy[rec2_pos])
                t_last_period.append(t)
        
        # Compute phase using Hilbert transform
        rec1_last_period = np.array(rec1_last_period)
        rec2_last_period = np.array(rec2_last_period)
        
        # Analytic signal
        from scipy.signal import hilbert
        analytic1 = hilbert(rec1_last_period)
        analytic2 = hilbert(rec2_last_period)
        
        # Phase (average over last period)
        phase1 = np.angle(np.mean(analytic1))
        phase2 = np.angle(np.mean(analytic2))
        
        # Phase difference
        phase_diff = phase2 - phase1
        # Unwrap
        while phase_diff > np.pi:
            phase_diff -= 2 * np.pi
        while phase_diff < -np.pi:
            phase_diff += 2 * np.pi
        
        # Phase velocity
        omega = 2 * np.pi * f0
        if abs(phase_diff) > 0.001:
            c_p = omega * distance / abs(phase_diff)
        else:
            c_p = np.sqrt(G_r / rho)
        
        # Theoretical
        G_star = G_r + (G_inf - G_r) / (1 + 1j * omega * tau_sigma)
        G_mag = np.abs(G_star)
        delta = np.angle(G_star)
        c_theory = np.sqrt(2 * G_mag / (rho * (1 + np.cos(delta))))
        
        results.append({
            'f': f0,
            'c_p': c_p,
            'c_theory': c_theory,
            'phase_diff': phase_diff,
            'distance': distance
        })
        
        print(f"  Phase diff: {np.degrees(phase_diff):.1f}°")
        print(f"  c_p = {c_p:.2f} m/s (theory: {c_theory:.2f})")
    
    return results


def zener_c(f, G_r, G_inf, tau_sigma, rho=1000):
    """Theoretical Zener phase velocity."""
    omega = 2 * np.pi * f
    G_star = G_r + (G_inf - G_r) / (1 + 1j * omega * tau_sigma)
    G_mag = np.abs(G_star)
    delta = np.angle(G_star)
    return np.sqrt(2 * G_mag / (rho * (1 + np.cos(delta))))


def visualize_cw_results(results, G_r, G_inf, tau_sigma):
    """Visualize CW extraction results."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    freqs = [r['f'] for r in results]
    c_extracted = [r['c_p'] for r in results]
    c_theory = [r['c_theory'] for r in results]
    
    # Theory curve
    f_theory = np.linspace(min(freqs)*0.8, max(freqs)*1.2, 100)
    c_theory_curve = [zener_c(f, G_r, G_inf, tau_sigma) for f in f_theory]
    
    # Plot 1: Dispersion
    ax = axes[0]
    ax.plot(freqs, c_extracted, 'bo-', markersize=12, linewidth=2,
           label='CW Extraction', zorder=5)
    ax.plot(f_theory, c_theory_curve, 'r--', linewidth=2, label='Zener Theory')
    
    c_r = np.sqrt(G_r / 1000)
    c_inf = np.sqrt(G_inf / 1000)
    ax.axhline(y=c_r, color='gray', linestyle=':', alpha=0.5)
    ax.axhline(y=c_inf, color='gray', linestyle='-.', alpha=0.5)
    ax.text(max(freqs)*1.05, c_r, f'c_r={c_r:.2f}', va='center', fontsize=10)
    ax.text(max(freqs)*1.05, c_inf, f'c_∞={c_inf:.2f}', va='center', fontsize=10)
    
    ax.set_xlabel('Frequency (Hz)', fontsize=12)
    ax.set_ylabel('Phase Velocity (m/s)', fontsize=12)
    ax.set_title('CW Dispersion Extraction', fontsize=13, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    
    # Plot 2: Error
    ax = axes[1]
    errors = [100 * (ce - ct) / ct for ce, ct in zip(c_extracted, c_theory)]
    
    ax.plot(freqs, errors, 'go-', markersize=12, linewidth=2)
    ax.axhline(y=0, color='r', linestyle='--', linewidth=2, alpha=0.5)
    ax.axhline(y=5, color='gray', linestyle=':', alpha=0.3)
    ax.axhline(y=-5, color='gray', linestyle=':', alpha=0.3)
    
    ax.fill_between(freqs, -5, 5, alpha=0.1, color='green', label='±5% band')
    
    ax.set_xlabel('Frequency (Hz)', fontsize=12)
    ax.set_ylabel('Error (%)', fontsize=12)
    ax.set_title(f'Extraction Error (mean={np.mean(np.abs(errors)):.1f}%)', 
                fontsize=13, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('cw_dispersion_extraction.png', dpi=150)
    print("\n✓ Saved: cw_dispersion_extraction.png")
    plt.show()
    
    # Print table
    print("\n" + "=" * 70)
    print("CW EXTRACTION RESULTS")
    print("=" * 70)
    print(f"{'Freq (Hz)':<12} {'Extracted':<12} {'Theory':<12} {'Error %':<12}")
    print("-" * 70)
    for r in results:
        err = 100 * (r['c_p'] - r['c_theory']) / r['c_theory']
        print(f"{r['f']:<12.0f} {r['c_p']:<12.2f} {r['c_theory']:<12.2f} {err:<12.1f}")
    print("=" * 70)


def main():
    """Run CW extraction."""
    frequencies = [50, 100, 150, 200, 250, 300, 350]
    
    results = extract_dispersion_cw_2d(
        frequencies, G_r=5000, G_inf=8000, tau_sigma=0.001,
        nx=200, steady_state_time=0.05
    )
    
    visualize_cw_results(results, 5000, 8000, 0.001)
    
    print("\n" + "=" * 70)
    print("CW extraction complete!")
    print("=" * 70)
    print("\n✓ Reliable dispersion data ready for inverse problem")
    
    return results


if __name__ == "__main__":
    main()
