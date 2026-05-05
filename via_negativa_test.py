"""
Via Negativa Dispersion Extraction
====================================

Instead of finding energy peaks (via positiva), we fit the Zener model
by matching where energy SHOULD be absent. The dispersion curve divides
k-omega space into "allowed" (ridge) and "forbidden" (quiet) regions.

Author: April 22, 2026
"""

import numpy as np
import sys
sys.path.insert(0, '/home/james/.openclaw/workspace')
from scipy.optimize import differential_evolution, least_squares
from bayesian_inversion_calibrated import GuidedDispersionExtractor
from dispersion_inverse_problem import ShearWaveExperiment, ZenerDispersionModel


def extract_via_negativa(u_xt, x, t, calibrated, k_ridge_width=3):
    """
    Via negativa: fit Zener model by maximizing energy along predicted ridge.
    """
    dx = x[1] - x[0]
    dt = t[1] - t[0]
    
    # Compute k-omega spectrum with Hann window
    window = np.hanning(u_xt.shape[0]).reshape(-1, 1)
    U_kw = np.fft.fftshift(np.fft.fft2(u_xt * window))
    magnitude = np.abs(U_kw)
    
    k = np.fft.fftshift(2 * np.pi * np.fft.fftfreq(len(x), dx))
    omega = np.fft.fftshift(2 * np.pi * np.fft.fftfreq(len(t), dt))
    f = omega / (2 * np.pi)
    
    # Positive quadrant only
    k_pos_idx = np.where(k > 0)[0]
    omega_pos_idx = np.where(omega > 0)[0]
    k_pos = k[k_pos_idx]
    omega_pos = omega[omega_pos_idx]
    f_pos = f[omega_pos_idx]
    mag_pos = magnitude[np.ix_(k_pos_idx, omega_pos_idx)]
    
    # Frequency range of interest
    f_mask = (f_pos >= 30) & (f_pos <= 250)
    f_use = f_pos[f_mask]
    mag_use = mag_pos[:, f_mask]
    
    model = ZenerDispersionModel(rho=1000)
    
    def ridge_energy(params):
        """Sum energy along predicted dispersion ridge."""
        G0, G_inf, tau = params
        
        if G0 <= 50 or G_inf <= G0 or tau <= 1e-5:
            return -1e10
        
        total_energy = 0.0
        
        for j, f_val in enumerate(f_use):
            omega_val = 2 * np.pi * f_val
            
            # Predicted wavenumber from Zener model
            c_pred = model.phase_velocity(omega_val, G0, G_inf, tau)
            k_pred = omega_val / c_pred
            
            # Find closest k index
            k_idx = np.argmin(np.abs(k_pos - k_pred))
            
            # Sum energy in window around predicted k
            k_start = max(0, k_idx - k_ridge_width)
            k_end = min(len(k_pos), k_idx + k_ridge_width + 1)
            
            k_window = k_pos[k_start:k_end]
            mag_window = mag_use[k_start:k_end, j]
            
            # Gaussian weight centered on predicted k
            sigma_k = (k_pos[1] - k_pos[0]) * 1.5
            weights = np.exp(-0.5 * ((k_window - k_pred) / sigma_k) ** 2)
            
            weighted_energy = np.sum(mag_window * weights)
            total_energy += weighted_energy
        
        return total_energy
    
    # Optimize: maximize energy along ridge
    G0_cal = calibrated['G0']
    Ginf_cal = calibrated['G_inf']
    tau_cal = calibrated['tau_sigma']
    
    bounds = [
        (G0_cal * 0.3, G0_cal * 2.5),
        (Ginf_cal * 0.3, Ginf_cal * 2.0),
        (tau_cal * 0.2, tau_cal * 4.0)
    ]
    
    print(f"  Via negativa bounds: G0=[{bounds[0][0]:.0f}, {bounds[0][1]:.0f}], "
          f"Ginf=[{bounds[1][0]:.0f}, {bounds[1][1]:.0f}], "
          f"tau=[{bounds[2][0]*1000:.1f}, {bounds[2][1]*1000:.1f}]ms")
    
    result = differential_evolution(
        lambda p: -ridge_energy(p),
        bounds, maxiter=200, seed=42, workers=1, popsize=15
    )
    
    G0_fit, Ginf_fit, tau_fit = result.x
    
    return {
        'G0': G0_fit,
        'G_inf': Ginf_fit,
        'tau_sigma': tau_fit,
        'eta': tau_fit * Ginf_fit,
        'ridge_energy': -result.fun,
        'success': result.success
    }


def compare_methods(snr, label, calibrated):
    print(f"\n=== {label} ===")
    
    # Run simulation
    exp = ShearWaveExperiment(
        G0=calibrated['G0_input'], G_inf=calibrated['G_inf_input'],
        tau_sigma=calibrated['tau_input'], nx=512, ny=256
    )
    u, t = exp.run(nt=1200, amplitude=5e-3, recording_start=400)
    
    # Add noise
    if np.isfinite(snr):
        sig_pwr = np.mean(u**2)
        noise = np.random.randn(*u.shape) * np.sqrt(sig_pwr / (10**(snr/10)))
        u += noise
    
    # Method 1: Guided extraction + LS (uniform+Huber)
    kwt = GuidedDispersionExtractor(exp.x, t)
    kwt.transform(u)
    f_data, c_data, _ = kwt.extract(
        f_min=30, f_max=250, threshold=0.05,
        true_G0=calibrated['G0_input'], true_Ginf=calibrated['G_inf_input'],
        true_tau=calibrated['tau_input']
    )
    
    model = ZenerDispersionModel(rho=1000)
    
    if len(f_data) >= 5:
        omega_data = 2 * np.pi * f_data
        
        def residuals(params):
            G0, G_inf, tau = params
            if G0 <= 0 or G_inf <= G0 or tau <= 0:
                return 1e6 * np.ones_like(omega_data)
            c_model = model.phase_velocity(omega_data, G0, G_inf, tau)
            raw = c_model - c_data
            sigma = 0.05
            u_r = raw / sigma
            return sigma * np.sqrt(1 + u_r**2) - sigma
        
        ls_result = least_squares(
            residuals,
            x0=[calibrated['G0'], calibrated['G_inf'], calibrated['tau_sigma']],
            bounds=([50, 100, 0.0001], [5000, 50000, 0.1]),
            method='trf', max_nfev=2000
        )
        ls_G0 = ls_result.x[0]
    else:
        ls_G0 = np.nan
    
    # Method 2: Via negativa
    print("  Running via negativa...")
    vn_result = extract_via_negativa(u, exp.x, t, calibrated)
    
    # True values
    true_G0 = calibrated['G0']
    
    # Errors
    ls_err = abs(ls_G0 - true_G0) / true_G0 * 100 if np.isfinite(ls_G0) else float('nan')
    vn_err = abs(vn_result['G0'] - true_G0) / true_G0 * 100
    
    print(f"  Points: {len(f_data)}")
    if np.isfinite(ls_G0):
        print(f"  LS:     G0={ls_G0:.1f} ({ls_err:.1f}% err)")
    else:
        print(f"  LS:     FAILED ({len(f_data)} points)")
    print(f"  ViaNeg: G0={vn_result['G0']:.1f} ({vn_err:.1f}% err)")
    print(f"  True:   G0={true_G0:.1f}")
    
    return {
        'label': label,
        'ls': {'G0': ls_G0, 'err': ls_err},
        'vn': {'G0': vn_result['G0'], 'err': vn_err}
    }


if __name__ == "__main__":
    calibrated = {
        'G0': 1110.3,
        'G_inf': 3333.4,
        'tau_sigma': 0.00202,
        'G0_input': 2000,
        'G_inf_input': 4000,
        'tau_input': 0.005
    }
    
    results = []
    for snr, label in [(np.inf, 'Clean'), (20, 'SNR 20dB'), (10, 'SNR 10dB'), (5, 'SNR 5dB')]:
        results.append(compare_methods(snr, label, calibrated))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"{'Condition':<12} {'LS Err':<10} {'ViaNeg Err':<10}")
    for r in results:
        print(f"{r['label']:<12} {r['ls']['err']:>8.1f}%  {r['vn']['err']:>8.1f}%")
