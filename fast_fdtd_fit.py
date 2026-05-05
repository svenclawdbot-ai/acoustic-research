"""
Fast FDTD-Based Fitting (Coarse Grid)
======================================

Uses 256x128 grid (4x faster) with 20 iterations, 5 population.
Quick proof-of-concept that accurate forward model fixes the bias.

Author: April 22, 2026
"""

import numpy as np
import sys
sys.path.insert(0, '/home/james/.openclaw/workspace')
from scipy.optimize import differential_evolution
from dispersion_inverse_problem import ShearWaveExperiment


calibrated = {
    'G0': 1110.3, 'G_inf': 3333.4, 'tau_sigma': 0.00202,
    'G0_input': 2000, 'G_inf_input': 4000, 'tau_input': 0.005
}

receiver_indices = np.array([0, 25, 50, 75, 100, 125, 150, 175])

print("=" * 60)
print("FAST FDTD FITTING (256x128 grid, 8 receivers)")
print("=" * 60)

# Generate observed data
print("\n[1] Generating observed data (256x128)...")
exp_obs = ShearWaveExperiment(
    G0=calibrated['G0_input'], G_inf=calibrated['G_inf_input'],
    tau_sigma=calibrated['tau_input'], nx=256, ny=128
)
u_full, t = exp_obs.run(nt=1200, amplitude=5e-3, recording_start=400)
u_obs = u_full[receiver_indices, :]
print(f"  Observed: {u_obs.shape}, True G0={calibrated['G0']:.1f}")

_cache = {}

def forward(params):
    """Fast forward model with caching."""
    G0, Ginf, tau = params
    key = (round(G0, 1), round(Ginf, 1), round(tau, 6))
    if key in _cache:
        return _cache[key][receiver_indices, :]
    
    exp = ShearWaveExperiment(G0=G0, G_inf=Ginf, tau_sigma=tau, nx=256, ny=128)
    u, _ = exp.run(nt=1200, amplitude=5e-3, recording_start=400)
    _cache[key] = u
    return u[receiver_indices, :]

def misfit(params):
    """Correlation-based misfit."""
    G0, Ginf, tau = params
    if G0 <= 50 or Ginf <= G0 or tau <= 1e-5:
        return 1e10
    
    try:
        u_pred = forward(params)
    except:
        return 1e10
    
    total = 0.0
    for i in range(u_obs.shape[0]):
        obs = u_obs[i] / (np.std(u_obs[i]) + 1e-10)
        pred = u_pred[i] / (np.std(u_pred[i]) + 1e-10)
        corr = np.sum(obs * pred) / len(obs)
        total -= corr
    
    return total

# Fit
print("\n[2] Fitting with coarse FDTD (maxiter=20, popsize=5)...")
G0c, Gic, tc = calibrated['G0'], calibrated['G_inf'], calibrated['tau_sigma']

bounds = [
    (G0c * 0.5, G0c * 2.0),
    (Gic * 0.5, Gic * 2.0),
    (tc * 0.3, tc * 3.0)
]

result = differential_evolution(
    misfit, bounds, maxiter=20, seed=42, workers=1, popsize=5,
    tol=1e-4, atol=1e-4
)

G0_fit, Ginf_fit, tau_fit = result.x
err_G0 = abs(G0_fit - calibrated['G0']) / calibrated['G0'] * 100

print(f"\n[3] RESULTS:")
print(f"  Fitted: G0={G0_fit:.1f}, Ginf={Ginf_fit:.1f}, tau={tau_fit*1000:.2f}ms")
print(f"  True:   G0={calibrated['G0']:.1f}, Ginf={calibrated['G_inf']:.1f}, tau={calibrated['tau_sigma']*1000:.2f}ms")
print(f"  Error:  {err_G0:.1f}%")
print(f"  Cache size: {len(_cache)} simulations")

if err_G0 < 10:
    print(f"\n  ✅ SUCCESS: {err_G0:.1f}% error is within 10% target!")
elif err_G0 < 20:
    print(f"\n  ⚠️  PARTIAL: {err_G0:.1f}% error — better but not quite there.")
else:
    print(f"\n  ❌ STILL HIGH: {err_G0:.1f}% error.")
