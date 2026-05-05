"""
Sparse Array Extraction: GCC-PHAT + Model-Based Fitting
=========================================================

Two approaches for 8-receiver sparse arrays where k-ω FFT fails:

1. GCC-PHAT: Cross-correlation time-delay estimation between pairs
   → Measures group velocity vs frequency (bandpass filtering)
   
2. Model-based: Fit Zener parameters directly to time-domain waveforms
   → Forward model: simulate wavefield with candidate (G0, Ginf, tau)
   → Misfit: compare simulated to observed waveforms
   → Optimize: differential evolution on parameter space

Author: April 22, 2026
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
sys.path.insert(0, '/home/james/.openclaw/workspace')
from scipy.optimize import differential_evolution
from scipy.signal import correlate, butter, filtfilt
from dispersion_inverse_problem import ShearWaveExperiment, ZenerDispersionModel


class SparseArrayExtractor:
    """Extract dispersion from sparse receiver arrays."""
    
    def __init__(self, true_G0=2000, true_Ginf=4000, true_tau=0.005,
                 nx=512, ny=256):
        self.true_params = {'G0': true_G0, 'G_inf': true_Ginf, 'tau_sigma': true_tau}
        self.nx = nx
        self.ny = ny
        
        # Run simulation once
        self.exp = ShearWaveExperiment(G0=true_G0, G_inf=true_Ginf,
                                        tau_sigma=true_tau, nx=nx, ny=ny)
        self.u_full, self.t = self.exp.run(nt=1200, amplitude=5e-3, recording_start=400)
        self.dt = self.t[1] - self.t[0]
        self.dx = self.exp.dx
        
        # Calibrated parameters (known from earlier)
        self.calibrated = {
            'G0': 1110.3, 'G_inf': 3333.4, 'tau_sigma': 0.00202,
            'G0_input': 2000, 'G_inf_input': 4000, 'tau_input': 0.005
        }
    
    def get_8rx_wavefield(self, noise_snr=np.inf):
        """Extract 8-receiver subset with optional noise."""
        # 8 receivers at 25mm spacing over 175mm
        receiver_indices = np.array([0, 25, 50, 75, 100, 125, 150, 175])
        u_8rx = self.u_full[receiver_indices, :].copy()
        x_8rx = self.exp.x[receiver_indices]
        
        # Add noise
        if np.isfinite(noise_snr):
            sig_pwr = np.mean(u_8rx ** 2)
            noise = np.random.randn(*u_8rx.shape) * np.sqrt(sig_pwr / (10**(noise_snr/10)))
            u_8rx += noise
        
        return u_8rx, x_8rx, receiver_indices
    
    # =====================================================================
    # METHOD 1: GCC-PHAT for group velocity
    # =====================================================================
    def gcc_phat_group_velocity(self, u_rx, x_rx, f_center, bw=20):
        """
        Estimate group velocity at specific frequency using GCC-PHAT.
        
        Steps:
        1. Bandpass filter traces around f_center
        2. Compute GCC-PHAT between adjacent pairs
        3. Find peak delay → time difference
        4. Group velocity cg = Δx / Δt
        
        Parameters:
        -----------
        u_rx : array (n_receivers, nt)
            Receiver waveforms
        x_rx : array (n_receivers,)
            Receiver positions
        f_center : float
            Center frequency (Hz)
        bw : float
            Bandwidth (Hz)
        
        Returns:
        --------
        cg : float
            Group velocity (m/s)
        delays : array
            Time delays for each pair (s)
        """
        nyq = 0.5 / self.dt
        low = max(1, (f_center - bw/2)) / nyq
        high = (f_center + bw/2) / nyq
        
        # Butterworth bandpass
        b, a = butter(4, [low, high], btype='band')
        
        # Filter all traces
        u_filt = np.array([filtfilt(b, a, trace) for trace in u_rx])
        
        # Compute GCC-PHAT for adjacent pairs
        n_pairs = len(x_rx) - 1
        delays = []
        cgs = []
        
        for i in range(n_pairs):
            trace1 = u_filt[i]
            trace2 = u_filt[i + 1]
            dx = x_rx[i + 1] - x_rx[i]
            
            # Cross-correlation
            corr = correlate(trace2, trace1, mode='full')
            lag = np.arange(-len(trace1) + 1, len(trace1))
            
            # PHAT weighting (whitening)
            # Compute FFT for whitening
            n_fft = len(trace1) + len(trace2) - 1
            fft1 = np.fft.fft(trace1, n_fft)
            fft2 = np.fft.fft(trace2, n_fft)
            cross_spectrum = fft2 * np.conj(fft1)
            
            # PHAT: divide by magnitude
            eps = 1e-10
            phat_weight = 1.0 / (np.abs(cross_spectrum) + eps)
            cross_phat = cross_spectrum * phat_weight
            
            # Back to time domain
            corr_phat = np.fft.ifft(cross_phat).real
            
            # Find peak
            peak_idx = np.argmax(corr_phat)
            delay = lag[peak_idx] * self.dt
            
            if abs(delay) > 1e-9:  # Valid delay
                cg = dx / abs(delay)
                delays.append(delay)
                cgs.append(cg)
        
        # Median group velocity across pairs (robust to outliers)
        if len(cgs) > 0:
            cg_median = np.median(cgs)
            cg_std = np.std(cgs)
            return cg_median, delays, cgs, cg_std
        else:
            return np.nan, [], [], np.nan
    
    def extract_gcc_phat_dispersion(self, u_rx, x_rx, f_bands):
        """
        Extract group velocity dispersion curve using GCC-PHAT.
        
        Parameters:
        -----------
        f_bands : list of (f_center, bw) tuples
            Frequency bands to analyze
        
        Returns:
        --------
        f_disp : array
            Center frequencies
        cg_disp : array
            Group velocities
        """
        f_disp = []
        cg_disp = []
        cg_err = []
        
        for f_center, bw in f_bands:
            cg, delays, cgs, cg_std = self.gcc_phat_group_velocity(
                u_rx, x_rx, f_center, bw
            )
            
            if np.isfinite(cg) and 0.5 < cg < 5.0:
                f_disp.append(f_center)
                cg_disp.append(cg)
                cg_err.append(cg_std if np.isfinite(cg_std) else 0.1)
                print(f"  f={f_center:.0f}Hz: cg={cg:.3f}m/s, delays={[f'{d*1000:.2f}ms' for d in delays]}")
        
        return np.array(f_disp), np.array(cg_disp), np.array(cg_err)
    
    # =====================================================================
    # METHOD 2: Model-based direct fitting
    # =====================================================================
    def forward_model_wavefield(self, params, x_rx, source_pos=0.0, nt=400):
        """
        Generate predicted wavefield at receiver positions.
        
        Uses analytical Green's function for 1D propagation:
        - Each receiver sees a delayed, attenuated version of source
        - Delay: t = x / c(ω; G0, Ginf, tau)
        - Frequency-dependent velocity from Zener model
        
        Simplified: sum of frequency components with phase delays
        """
        G0, Ginf, tau = params
        
        if G0 <= 0 or Ginf <= G0 or tau <= 0:
            return None
        
        model = ZenerDispersionModel(rho=1000)
        
        # Time axis
        t = np.arange(nt) * self.dt
        
        # Source spectrum (Ricker-like)
        f0 = 150  # Hz
        sigma_t = 1 / (np.pi * f0)
        
        # Frequency components
        freqs = np.fft.rfftfreq(nt, self.dt)
        omega = 2 * np.pi * freqs
        
        # Predict wavefield at each receiver
        u_pred = np.zeros((len(x_rx), nt))
        
        for i, x in enumerate(x_rx):
            if x <= source_pos:
                continue  # No wave at or before source
            
            # Compute phase delay for each frequency
            # Delay: t_delay = x / c(ω)
            c_omega = model.phase_velocity(omega[1:], G0, Ginf, tau)
            k_omega = omega[1:] / c_omega
            
            # Build source spectrum
            source_fft = np.fft.rfft(np.exp(-((t - 3*sigma_t)/sigma_t)**2) * 
                                     (1 - 2*((t - 3*sigma_t)/sigma_t)**2))
            
            # Propagate: multiply by exp(-j * k * x)
            propagated = source_fft.copy()
            propagated[1:] *= np.exp(-1j * k_omega * (x - source_pos))
            
            # Back to time domain
            u_pred[i] = np.fft.irfft(propagated, n=nt)
        
        return u_pred
    
    def misfit_wavefield(self, params, u_obs, x_rx):
        """
        Compute misfit between observed and predicted wavefields.
        
        Uses correlation-based misfit (robust to amplitude scaling)
        """
        u_pred = self.forward_model_wavefield(params, x_rx)
        
        if u_pred is None:
            return 1e10
        
        # Normalize both
        u_obs_norm = u_obs / (np.std(u_obs) + 1e-10)
        u_pred_norm = u_pred / (np.std(u_pred) + 1e-10)
        
        # Misfit: negative sum of correlations (we want to maximize correlation)
        total_corr = 0
        for i in range(len(x_rx)):
            # Cross-correlation at zero lag
            corr = np.correlate(u_obs_norm[i], u_pred_norm[i], mode='valid')[0]
            total_corr += corr / len(u_obs_norm[i])
        
        # Return negative correlation (minimize = maximize correlation)
        return -total_corr
    
    def fit_model_based(self, u_rx, x_rx):
        """
        Fit Zener parameters by matching predicted wavefield to observed.
        """
        G0_cal = self.calibrated['G0']
        Ginf_cal = self.calibrated['G_inf']
        tau_cal = self.calibrated['tau_sigma']
        
        bounds = [
            (G0_cal * 0.2, G0_cal * 3.0),
            (Ginf_cal * 0.2, Ginf_cal * 2.5),
            (tau_cal * 0.1, tau_cal * 5.0)
        ]
        
        print(f"  Model-based bounds: G0=[{bounds[0][0]:.0f}, {bounds[0][1]:.0f}], "
              f"Ginf=[{bounds[1][0]:.0f}, {bounds[1][1]:.0f}], "
              f"tau=[{bounds[2][0]*1000:.1f}, {bounds[2][1]*1000:.1f}]ms")
        
        result = differential_evolution(
            lambda p: self.misfit_wavefield(p, u_rx, x_rx),
            bounds, maxiter=100, seed=42, workers=1, popsize=10
        )
        
        G0_fit, Ginf_fit, tau_fit = result.x
        
        return {
            'G0': G0_fit,
            'G_inf': Ginf_fit,
            'tau_sigma': tau_fit,
            'eta': tau_fit * Ginf_fit,
            'misfit': result.fun,
            'success': result.success
        }
    
    # =====================================================================
    # COMPARISON TEST
    # =====================================================================
    def compare_methods(self, noise_snr=np.inf):
        """Compare GCC-PHAT vs model-based with 8 receivers."""
        label = f"SNR_{noise_snr:.0f}dB" if np.isfinite(noise_snr) else "Clean"
        print(f"\n{'='*60}")
        print(f"8-RECEIVER TEST: {label}")
        print('='*60)
        
        # Get wavefield
        u_rx, x_rx, indices = self.get_8rx_wavefield(noise_snr)
        print(f"Receivers at (mm): {x_rx*1000}")
        
        # Method 1: GCC-PHAT
        print("\n--- GCC-PHAT ---")
        f_bands = [
            (50, 20), (75, 20), (100, 20), (125, 20),
            (150, 20), (175, 20), (200, 20)
        ]
        f_gcc, cg_gcc, err_gcc = self.extract_gcc_phat_dispersion(u_rx, x_rx, f_bands)
        
        # Fit Zener to group velocity (approximate: cg ≈ cp for low dispersion)
        # For more accuracy, we'd need the full group velocity formula
        if len(f_gcc) >= 3:
            # Convert group velocity to approximate phase velocity
            # For weak dispersion: cg ≈ cp
            # This is a rough approximation
            omega_data = 2 * np.pi * f_gcc
            model = ZenerDispersionModel(rho=1000)
            
            def residuals(params):
                G0, Ginf, tau = params
                if G0 <= 0 or Ginf <= G0 or tau <= 0:
                    return 1e6 * np.ones_like(omega_data)
                c_model = model.phase_velocity(omega_data, G0, Ginf, tau)
                return c_model - cg_gcc  # Treat cg as cp (approximation)
            
            result = least_squares(
                residuals,
                x0=[self.calibrated['G0'], self.calibrated['G_inf'], self.calibrated['tau_sigma']],
                bounds=([50, 100, 0.0001], [5000, 50000, 0.1]),
                method='trf', max_nfev=1000
            )
            gcc_G0 = result.x[0]
            gcc_err = abs(gcc_G0 - self.calibrated['G0']) / self.calibrated['G0'] * 100
            print(f"  GCC-PHAT fit: G0={gcc_G0:.1f} ({gcc_err:.1f}% err)")
        else:
            gcc_G0 = np.nan
            gcc_err = float('nan')
            print("  GCC-PHAT: FAILED (too few points)")
        
        # Method 2: Model-based
        print("\n--- Model-Based Direct Fitting ---")
        mb_result = self.fit_model_based(u_rx, x_rx)
        mb_G0 = mb_result['G0']
        mb_err = abs(mb_G0 - self.calibrated['G0']) / self.calibrated['G0'] * 100
        print(f"  Model-based: G0={mb_G0:.1f} ({mb_err:.1f}% err)")
        
        # True value
        true_G0 = self.calibrated['G0']
        print(f"\n  True: G0={true_G0:.1f}")
        
        return {
            'label': label,
            'gcc': {'G0': gcc_G0, 'err': gcc_err, 'f': f_gcc, 'cg': cg_gcc},
            'model_based': {'G0': mb_G0, 'err': mb_err, 'misfit': mb_result['misfit']}
        }


if __name__ == "__main__":
    extractor = SparseArrayExtractor()
    
    results = []
    for snr in [np.inf, 30, 20, 10]:
        results.append(extractor.compare_methods(snr))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"{'Condition':<12} {'GCC-PHAT':<12} {'Model-Based':<12}")
    for r in results:
        gcc_str = f"{r['gcc']['err']:.1f}%" if np.isfinite(r['gcc']['err']) else "FAIL"
        mb_str = f"{r['model_based']['err']:.1f}%"
        print(f"{r['label']:<12} {gcc_str:>10}  {mb_str:>10}")
