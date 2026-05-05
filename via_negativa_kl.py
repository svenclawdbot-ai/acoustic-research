"""
Via Negativa: KL-Divergence Spectrum Fitting
=============================================

Instead of peak picking, model the full k-ω spectrum and fit parameters
by minimizing KL divergence between observed and predicted distributions.

The "negative" insight: energy AWAY from the dispersion curve is just as
informative as energy ON it. We use the ENTIRE spectrum, not just peaks.

p_obs(k,ω) = |U(k,ω)| / Z(ω)        # Observed distribution
p_pred(k,ω) = N(k_pred(ω), σ²)     # Predicted ridge from Zener model

Loss = Σ_ω D_KL(p_obs(·,ω) || p_pred(·,ω))

where k_pred(ω) = ω / c(ω; G₀, G∞, τ)

Author: April 22, 2026
"""

import numpy as np
import sys
sys.path.insert(0, '/home/james/.openclaw/workspace')
from scipy.optimize import differential_evolution, least_squares
from bayesian_inversion_calibrated import GuidedDispersionExtractor
from dispersion_inverse_problem import ShearWaveExperiment, ZenerDispersionModel


def kl_divergence_spectrum(u_xt, x, t, params, f_min=30, f_max=250, sigma_k_factor=1.0):
    """
    Compute KL divergence between observed k-distribution and predicted ridge.
    
    For each frequency, we:
    1. Extract the observed k-distribution p_obs(k) = |U(k,ω)| / Σ|U|
    2. Predict the ridge location k_pred(ω) from Zener parameters
    3. Form predicted distribution p_pred(k) = Gaussian centered at k_pred
    4. Compute D_KL = Σ p_obs log(p_obs / p_pred)
    
    Lower D_KL = better fit.
    
    Parameters:
    -----------
    u_xt : array (nx, nt)
        Spatiotemporal wavefield
    x, t : arrays
        Spatial and temporal axes
    params : (G0, G_inf, tau)
        Zener model parameters
    f_min, f_max : float
        Frequency range of interest
    sigma_k_factor : float
        Ridge width in units of dk (spatial frequency bin spacing)
    
    Returns:
    --------
    kl_total : float
        Total KL divergence (sum over frequencies)
    kl_per_freq : dict
        Per-frequency breakdown
    """
    G0, G_inf, tau = params
    
    # Hard constraints
    if G0 <= 50 or G_inf <= G0 or tau <= 1e-5:
        return 1e10, {}
    
    dx = x[1] - x[0]
    dt = t[1] - t[0]
    
    # Compute k-ω spectrum
    window = np.hanning(u_xt.shape[0]).reshape(-1, 1)
    U_kw = np.fft.fftshift(np.fft.fft2(u_xt * window))
    magnitude = np.abs(U_kw)
    
    k = np.fft.fftshift(2 * np.pi * np.fft.fftfreq(len(x), dx))
    omega = np.fft.fftshift(2 * np.pi * np.fft.fftfreq(len(t), dt))
    f = omega / (2 * np.pi)
    
    # Positive quadrant
    k_pos_idx = np.where(k > 0)[0]
    omega_pos_idx = np.where(omega > 0)[0]
    k_pos = k[k_pos_idx]
    omega_pos = omega[omega_pos_idx]
    f_pos = f[omega_pos_idx]
    mag_pos = magnitude[np.ix_(k_pos_idx, omega_pos_idx)]
    
    dk = k_pos[1] - k_pos[0]
    sigma_k = dk * sigma_k_factor
    
    model = ZenerDispersionModel(rho=1000)
    
    kl_total = 0.0
    kl_per_freq = {}
    
    for j, f_val in enumerate(f_pos):
        if f_val < f_min or f_val > f_max:
            continue
        
        omega_val = 2 * np.pi * f_val
        
        # Observed distribution (normalize to sum to 1)
        p_obs = mag_pos[:, j]
        obs_sum = np.sum(p_obs)
        if obs_sum < 1e-12:
            continue
        p_obs = p_obs / obs_sum
        
        # Predicted ridge location
        c_pred = model.phase_velocity(omega_val, G0, G_inf, tau)
        k_pred = omega_val / c_pred
        
        # Predicted distribution: Gaussian ridge
        p_pred = np.exp(-0.5 * ((k_pos - k_pred) / sigma_k) ** 2)
        p_pred = p_pred / np.sum(p_pred)
        
        # KL divergence: D_KL(p_obs || p_pred)
        # Add small epsilon to avoid log(0)
        eps = 1e-12
        kl = np.sum(p_obs * np.log((p_obs + eps) / (p_pred + eps)))
        
        kl_total += kl
        kl_per_freq[f_val] = kl
    
    return kl_total, kl_per_freq


def fit_via_negativa_kl(u_xt, x, t, calibrated, f_min=30, f_max=250):
    """
    Fit Zener parameters by minimizing KL divergence between 
    observed and predicted k-distributions.
    """
    G0_cal = calibrated['G0']
    Ginf_cal = calibrated['G_inf']
    tau_cal = calibrated['tau_sigma']
    
    bounds = [
        (G0_cal * 0.3, G0_cal * 2.5),
        (Ginf_cal * 0.3, Ginf_cal * 2.0),
        (tau_cal * 0.2, tau_cal * 4.0)
    ]
    
    print(f"  KL bounds: G0=[{bounds[0][0]:.0f}, {bounds[0][1]:.0f}], "
          f"Ginf=[{bounds[1][0]:.0f}, {bounds[1][1]:.0f}], "
          f"tau=[{bounds[2][0]*1000:.1f}, {bounds[2][1]*1000:.1f}]ms")
    
    def objective(params):
        kl, _ = kl_divergence_spectrum(u_xt, x, t, params, f_min, f_max)
        return kl
    
    result = differential_evolution(
        objective,
        bounds, maxiter=200, seed=42, workers=1, popsize=15,
        tol=1e-6, atol=1e-6
    )
    
    G0_fit, Ginf_fit, tau_fit = result.x
    kl_final, kl_per_freq = kl_divergence_spectrum(u_xt, x, t, result.x, f_min, f_max)
    
    return {
        'G0': G0_fit,
        'G_inf': Ginf_fit,
        'tau_sigma': tau_fit,
        'eta': tau_fit * Ginf_fit,
        'kl_divergence': kl_final,
        'kl_per_freq': kl_per_freq,
        'success': result.success
    }


def compare_all_methods(snr, label, calibrated):
    """Compare: guided peaks + LS, vs KL-divergence spectrum fitting."""
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
    
    # Method 1: Guided extraction + LS
    kwt = GuidedDispersionExtractor(exp.x, t)
    kwt.transform(u)
    f_data, c_data, _ = kwt.extract(
        f_min=30, f_max=250, threshold=0.05,
        true_G0=calibrated['G0_input'], true_Ginf=calibrated['G_inf_input'],
        true_tau=calibrated['tau_input']
    )
    
    model = ZenerDispersionModel(rho=1000)
    ls_G0 = np.nan
    
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
    
    # Method 2: KL divergence spectrum fitting
    print("  Running KL-divergence fitting...")
    kl_result = fit_via_negativa_kl(u, exp.x, t, calibrated)
    
    # True values
    true_G0 = calibrated['G0']
    true_Ginf = calibrated['G_inf']
    
    # Errors
    ls_err = abs(ls_G0 - true_G0) / true_G0 * 100 if np.isfinite(ls_G0) else float('nan')
    kl_err = abs(kl_result['G0'] - true_G0) / true_G0 * 100
    
    print(f"  Points: {len(f_data)}")
    if np.isfinite(ls_G0):
        print(f"  LS (peaks): G0={ls_G0:.1f} ({ls_err:.1f}% err)")
    else:
        print(f"  LS (peaks): FAILED")
    print(f"  KL (spectrum): G0={kl_result['G0']:.1f} ({kl_err:.1f}% err), "
          f"KL={kl_result['kl_divergence']:.2f}")
    print(f"  True:   G0={true_G0:.1f}")
    
    return {
        'label': label,
        'ls': {'G0': ls_G0, 'err': ls_err},
        'kl': {'G0': kl_result['G0'], 'err': kl_err, 'kl_div': kl_result['kl_divergence']}
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
        results.append(compare_all_methods(snr, label, calibrated))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"{'Condition':<12} {'LS (peaks)':<12} {'KL (spectrum)':<15}")
    for r in results:
        print(f"{r['label']:<12} {r['ls']['err']:>10.1f}%  {r['kl']['err']:>13.1f}%")
