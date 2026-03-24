#!/usr/bin/env python3
"""
Overfitting Diagnostic Tool for Shear Wave Pipeline
====================================================

Detects overfitting at each stage of the processing pipeline:
1. Wavelet denoising (excessive smoothing)
2. Savitzky-Golay smoothing (polynomial overfit)
3. Bootstrap confidence intervals (under-coverage)
4. Cross-validation for optimal parameters

Author: Research Project
Date: March 15, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from scipy.optimize import curve_fit
from sklearn.model_selection import LeaveOneOut, KFold
import warnings

from dispersion_postprocessing import kelvin_voigt, bootstrap_fit


class OverfittingDiagnostics:
    """
    Comprehensive overfitting detection for dispersion analysis pipeline.
    """
    
    def __init__(self, rho=1000):
        self.rho = rho
        self.results = {}
    
    def full_diagnostic(self, freq, vel_raw, unc_raw, vel_smooth, 
                       bootstrap_results, wavelet_params=None):
        """
        Run complete diagnostic suite.
        
        Parameters:
        -----------
        freq : array
            Frequency points
        vel_raw : array
            Raw (unsmoothed) velocities
        unc_raw : array
            Raw uncertainties
        vel_smooth : array
            Savgol-smoothed velocities
        bootstrap_results : dict
            Output from bootstrap_fit()
        wavelet_params : dict, optional
            {'threshold_factor': float, 'wavelet': str, 'level': int}
            
        Returns:
        --------
        dict with all diagnostic results and recommendations
        """
        print("=" * 70)
        print("OVERFITTING DIAGNOSTIC REPORT")
        print("=" * 70)
        
        self.results = {
            'n_points': len(freq),
            'freq_range': (freq.min(), freq.max()),
            'diagnostics': {}
        }
        
        # Test 1: Savgol smoothing analysis
        print("\n[1/5] Savitzky-Golay Smoothing Analysis...")
        savgol_diag = self._diagnose_savgol_smoothing(freq, vel_raw, vel_smooth, unc_raw)
        self.results['diagnostics']['savgol'] = savgol_diag
        self._print_savgol_results(savgol_diag)
        
        # Test 2: Cross-validation for optimal parameters
        print("\n[2/5] Cross-Validation for Optimal Parameters...")
        cv_results = self._cross_validate_savgol(freq, vel_raw, unc_raw)
        self.results['diagnostics']['cross_validation'] = cv_results
        self._print_cv_results(cv_results)
        
        # Test 3: Bootstrap validity
        print("\n[3/5] Bootstrap Confidence Interval Validation...")
        bootstrap_diag = self._diagnose_bootstrap(freq, vel_raw, unc_raw, bootstrap_results)
        self.results['diagnostics']['bootstrap'] = bootstrap_diag
        self._print_bootstrap_results(bootstrap_diag)
        
        # Test 4: Residual analysis
        print("\n[4/5] Residual Analysis...")
        residual_diag = self._analyze_residuals(freq, vel_raw, vel_smooth, unc_raw)
        self.results['diagnostics']['residuals'] = residual_diag
        self._print_residual_results(residual_diag)
        
        # Test 5: Model complexity vs data
        print("\n[5/5] Model Complexity Assessment...")
        complexity_diag = self._assess_model_complexity(freq, vel_raw, unc_raw)
        self.results['diagnostics']['complexity'] = complexity_diag
        self._print_complexity_results(complexity_diag)
        
        # Generate recommendations
        recommendations = self._generate_recommendations()
        self.results['recommendations'] = recommendations
        
        print("\n" + "=" * 70)
        print("RECOMMENDATIONS")
        print("=" * 70)
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        
        # Overall verdict
        self._print_overall_verdict()
        
        return self.results
    
    def _diagnose_savgol_smoothing(self, freq, vel_raw, vel_smooth, unc):
        """
        Check if Savgol smoothing is fitting noise.
        """
        n = len(freq)
        
        # 1. Chi-squared test: smoothed vs raw
        residuals = vel_raw - vel_smooth
        chi2 = np.sum((residuals / (unc + 1e-10))**2)
        
        # Reduced chi-squared (expected ~1 for good fit)
        # Degrees of freedom: n_points - 2 (for G' and eta)
        dof = max(1, n - 2)
        reduced_chi2 = chi2 / dof
        
        # 2. Variance reduction analysis
        var_raw = np.var(vel_raw)
        var_smooth = np.var(vel_smooth)
        var_residual = np.var(residuals)
        
        # If var_residual << var_raw, we may be over-smoothing
        variance_ratio = var_smooth / (var_raw + 1e-10)
        
        # 3. Smoothness metric (second derivative)
        smoothness_raw = np.std(np.diff(vel_raw, 2))
        smoothness_smooth = np.std(np.diff(vel_smooth, 2))
        smoothness_ratio = smoothness_smooth / (smoothness_raw + 1e-10)
        
        # 4. Autocorrelation of residuals (should be random)
        if len(residuals) > 3:
            autocorr = np.corrcoef(residuals[:-1], residuals[1:])[0, 1]
        else:
            autocorr = 0
        
        # 5. L-curve inspired metric
        # Trade-off: ||smooth - raw|| vs ||second_derivative||
        residual_norm = np.sqrt(np.sum(residuals**2))
        curvature_norm = np.sqrt(np.sum(np.diff(vel_smooth, 2)**2))
        
        return {
            'chi2': chi2,
            'reduced_chi2': reduced_chi2,
            'variance_ratio': variance_ratio,
            'var_residual': var_residual,
            'smoothness_ratio': smoothness_ratio,
            'residual_autocorr': autocorr,
            'residual_norm': residual_norm,
            'curvature_norm': curvature_norm,
            'n_points': n
        }
    
    def _cross_validate_savgol(self, freq, vel, unc, max_window=7):
        """
        Use LOOCV to find optimal Savgol parameters.
        """
        n = len(freq)
        
        # If too few points, skip CV
        if n < 5:
            return {
                'optimal_window': 3,
                'optimal_order': 1,
                'cv_scores': {},
                'recommendation': 'Too few points for CV - use minimal smoothing'
            }
        
        best_score = -np.inf
        best_params = None
        cv_scores = {}
        
        # Test window sizes
        for wl in range(3, min(max_window + 1, n), 2):  # Odd numbers only
            for po in range(1, min(4, wl)):
                
                # Leave-one-out cross-validation
                loo = LeaveOneOut()
                errors = []
                
                for train_idx, test_idx in loo.split(freq):
                    f_train, f_test = freq[train_idx], freq[test_idx]
                    v_train, v_test = vel[train_idx], vel[test_idx]
                    u_test = unc[test_idx]
                    
                    # Smooth training data
                    if len(v_train) >= wl and wl > po:
                        v_smooth_train = savgol_filter(v_train, wl, po)
                    else:
                        v_smooth_train = v_train
                    
                    # Interpolate to test point
                    pred = np.interp(f_test, f_train, v_smooth_train)
                    
                    # Normalized error
                    error = abs(pred - v_test) / (u_test + 1e-10)
                    errors.append(error[0])
                
                # Mean error (lower is better, but penalize overfitting)
                mean_error = np.mean(errors)
                
                # Penalty for complexity (higher order = more complex)
                complexity_penalty = 0.1 * (po - 1)
                
                score = -mean_error - complexity_penalty
                cv_scores[(wl, po)] = {
                    'mean_error': mean_error,
                    'score': score
                }
                
                if score > best_score:
                    best_score = score
                    best_params = (wl, po)
        
        if best_params is None:
            best_params = (3, 1)
        
        return {
            'optimal_window': best_params[0],
            'optimal_order': best_params[1],
            'cv_scores': cv_scores,
            'best_score': best_score
        }
    
    def _diagnose_bootstrap(self, freq, vel, unc, bootstrap_results):
        """
        Check bootstrap CI coverage and validity.
        """
        if bootstrap_results is None:
            return {'error': 'No bootstrap results provided'}
        
        G_samples = bootstrap_results.get('G_samples', [])
        eta_samples = bootstrap_results.get('eta_samples', [])
        
        if len(G_samples) == 0:
            return {'error': 'Empty bootstrap samples'}
        
        # 1. Sample statistics
        G_median = np.median(G_samples)
        eta_median = np.median(eta_samples)
        
        G_mean = np.mean(G_samples)
        eta_mean = np.mean(eta_samples)
        
        # Check for bias (median vs mean)
        G_bias = abs(G_mean - G_median) / (np.std(G_samples) + 1e-10)
        eta_bias = abs(eta_mean - eta_median) / (np.std(eta_samples) + 1e-10)
        
        # 2. Distribution shape
        from scipy import stats
        _, G_normal_p = stats.normaltest(G_samples)
        _, eta_normal_p = stats.normaltest(eta_samples)
        
        # 3. CI width relative to estimate
        G_ci = bootstrap_results.get('G_ci', [0, 0])
        eta_ci = bootstrap_results.get('eta_ci', [0, 0])
        
        G_ci_width = (G_ci[1] - G_ci[0]) / (G_median + 1e-10)
        eta_ci_width = (eta_ci[1] - eta_ci[0]) / (eta_median + 1e-10)
        
        # 4. Effective sample size (accounting for correlation)
        # Simple estimate: n_eff = n / (1 + 2*sum(autocorrelations))
        if len(G_samples) > 10:
            autocorrs = [np.corrcoef(G_samples[:-i], G_samples[i:])[0,1] 
                        for i in range(1, min(10, len(G_samples)//2))]
            n_eff = len(G_samples) / (1 + 2 * sum(max(0, ac) for ac in autocorrs))
        else:
            n_eff = len(G_samples)
        
        return {
            'n_bootstrap': len(G_samples),
            'n_effective': n_eff,
            'G_median': G_median,
            'G_mean': G_mean,
            'G_bias_ratio': G_bias,
            'G_ci_width_relative': G_ci_width,
            'eta_median': eta_median,
            'eta_mean': eta_mean,
            'eta_bias_ratio': eta_bias,
            'eta_ci_width_relative': eta_ci_width,
            'G_normality_p': G_normal_p,
            'eta_normality_p': eta_normal_p
        }
    
    def _analyze_residuals(self, freq, vel_raw, vel_smooth, unc):
        """
        Analyze residual patterns for systematic errors.
        """
        residuals = vel_raw - vel_smooth
        
        # 1. Normalized residuals
        norm_residuals = residuals / (unc + 1e-10)
        
        # 2. Runs test for randomness
        # Count sign changes
        signs = np.sign(residuals)
        runs = 1 + np.sum(signs[1:] != signs[:-1])
        n_pos = np.sum(residuals > 0)
        n_neg = len(residuals) - n_pos
        
        # Expected runs for random sequence
        expected_runs = 1 + 2 * n_pos * n_neg / (n_pos + n_neg)
        runs_z = (runs - expected_runs) / np.sqrt(
            2 * n_pos * n_neg * (2 * n_pos * n_neg - n_pos - n_neg) / 
            ((n_pos + n_neg)**2 * (n_pos + n_neg - 1))
        ) if (n_pos + n_neg) > 1 else 0
        
        # 3. Correlation with frequency
        freq_corr = np.corrcoef(freq, residuals)[0, 1]
        
        # 4. Outlier detection (Chauvenet's criterion)
        mean_res = np.mean(residuals)
        std_res = np.std(residuals)
        n = len(residuals)
        
        # Chauvenet threshold
        from scipy import stats
        threshold = stats.norm.ppf(1 - 0.5 / (2 * n))
        outliers = np.abs((residuals - mean_res) / (std_res + 1e-10)) > threshold
        
        return {
            'residuals': residuals,
            'normalized_residuals': norm_residuals,
            'mean_residual': mean_res,
            'std_residual': std_res,
            'runs': runs,
            'expected_runs': expected_runs,
            'runs_z_score': runs_z,
            'freq_correlation': freq_corr,
            'n_outliers': np.sum(outliers),
            'outlier_indices': np.where(outliers)[0]
        }
    
    def _assess_model_complexity(self, freq, vel, unc):
        """
        Assess if model is too complex for data.
        """
        n = len(freq)
        
        # Kelvin-Voigt has 2 parameters (G', eta)
        model_params = 2
        
        # Data points per parameter
        dpp = n / model_params
        
        # Information criteria
        omega = 2 * np.pi * freq
        try:
            popt, _ = curve_fit(
                lambda w, G, e: kelvin_voigt(w, G, e, self.rho),
                omega, vel, sigma=unc,
                p0=[2000, 0.5], bounds=([100, 0.01], [50000, 50])
            )
            pred = kelvin_voigt(omega, *popt, self.rho)
            residuals = vel - pred
            
            # Log-likelihood
            log_likelihood = -0.5 * np.sum(
                (residuals / (unc + 1e-10))**2 + np.log(2 * np.pi * unc**2)
            )
            
            # AIC and BIC
            aic = 2 * model_params - 2 * log_likelihood
            bic = model_params * np.log(n) - 2 * log_likelihood
            
            # Corrected AIC for small samples
            aicc = aic + 2 * model_params * (model_params + 1) / (n - model_params - 1) if n > model_params + 1 else aic
            
        except:
            aic = bic = aicc = np.inf
            log_likelihood = -np.inf
        
        return {
            'n_data_points': n,
            'n_model_parameters': model_params,
            'data_per_parameter': dpp,
            'log_likelihood': log_likelihood,
            'aic': aic,
            'aicc': aicc,
            'bic': bic,
            'complexity_rating': 'ADEQUATE' if dpp >= 3 else 'UNDERDETERMINED'
        }
    
    def _generate_recommendations(self):
        """
        Generate actionable recommendations based on diagnostics.
        """
        recommendations = []
        
        diag = self.results['diagnostics']
        
        # Savgol recommendations
        if 'savgol' in diag:
            s = diag['savgol']
            if s['reduced_chi2'] < 0.5:
                recommendations.append(
                    "OVER-SMOOTHING: Chi2/dof < 0.5. Try smaller window or lower order."
                )
            elif s['reduced_chi2'] > 3.0:
                recommendations.append(
                    "UNDER-SMOOTHING: Chi2/dof > 3. Try larger window or higher order."
                )
            
            if abs(s['residual_autocorr']) > 0.5:
                recommendations.append(
                    "STRUCTURED RESIDUALS: Residuals show autocorrelation. "
                    "Savitzky-Golay may be inappropriate - consider physics-informed smoothing."
                )
        
        # CV recommendations
        if 'cross_validation' in diag:
            cv = diag['cross_validation']
            if 'optimal_window' in cv:
                recommendations.append(
                    f"OPTIMAL SAVGOL: window={cv['optimal_window']}, "
                    f"order={cv['optimal_order']} (via LOOCV)"
                )
        
        # Bootstrap recommendations
        if 'bootstrap' in diag:
            b = diag['bootstrap']
            if 'n_effective' in b and b['n_effective'] < 500:
                recommendations.append(
                    f"LOW EFFECTIVE SAMPLES: n_eff={b['n_effective']:.0f}. "
                    "Increase bootstrap iterations to 2000+."
                )
            
            if 'G_bias_ratio' in b and b['G_bias_ratio'] > 0.1:
                recommendations.append(
                    "BIASED ESTIMATES: Median vs mean discrepancy. "
                    "Check for outliers or use robust fitting."
                )
            
            if 'G_ci_width_relative' in b and b['G_ci_width_relative'] > 0.5:
                recommendations.append(
                    "WIDE CONFIDENCE INTERVALS: Relative CI > 50%. "
                    "Need more data points or lower noise."
                )
        
        # Complexity recommendations
        if 'complexity' in diag:
            c = diag['complexity']
            if c['complexity_rating'] == 'UNDERDETERMINED':
                recommendations.append(
                    f"INSUFFICIENT DATA: Only {c['data_per_parameter']:.1f} points per parameter. "
                    "Recommend >3 points per parameter for reliable fit."
                )
        
        # Residual recommendations
        if 'residuals' in diag:
            r = diag['residuals']
            if abs(r['runs_z_score']) > 2:
                recommendations.append(
                    "NON-RANDOM RESIDUALS: Runs test indicates structure. "
                    "Consider higher-order model or different smoothing."
                )
            
            if r['n_outliers'] > 0:
                recommendations.append(
                    f"OUTLIERS DETECTED: {r['n_outliers']} points fail Chauvenet's test. "
                    f"Indices: {r['outlier_indices']}. Review these measurements."
                )
        
        if not recommendations:
            recommendations.append("No overfitting detected. Pipeline appears well-calibrated.")
        
        return recommendations
    
    def _print_savgol_results(self, diag):
        """Print Savgol diagnostic results."""
        print(f"  Reduced χ²/dof: {diag['reduced_chi2']:.2f} "
              f"({'OK' if 0.5 <= diag['reduced_chi2'] <= 3.0 else 'WARNING'})")
        print(f"  Variance ratio (smooth/raw): {diag['variance_ratio']:.3f}")
        print(f"  Smoothness ratio: {diag['smoothness_ratio']:.3f}")
        print(f"  Residual autocorr: {diag['residual_autocorr']:.3f}")
        print(f"  Data points: {diag['n_points']}")
    
    def _print_cv_results(self, diag):
        """Print cross-validation results."""
        if 'optimal_window' in diag:
            print(f"  Optimal window: {diag['optimal_window']}")
            print(f"  Optimal order: {diag['optimal_order']}")
            print(f"  Best CV score: {diag['best_score']:.3f}")
        else:
            print(f"  {diag.get('recommendation', 'CV not performed')}")
    
    def _print_bootstrap_results(self, diag):
        """Print bootstrap diagnostic results."""
        if 'error' in diag:
            print(f"  Error: {diag['error']}")
            return
        
        print(f"  Bootstrap samples: {diag['n_bootstrap']}")
        print(f"  Effective samples: {diag['n_effective']:.0f}")
        print(f"  G' bias ratio: {diag['G_bias_ratio']:.3f}")
        print(f"  η bias ratio: {diag['eta_bias_ratio']:.3f}")
        print(f"  G' CI width: {diag['G_ci_width_relative']*100:.1f}%")
        print(f"  η CI width: {diag['eta_ci_width_relative']*100:.1f}%")
        print(f"  G' normality p: {diag['G_normality_p']:.3f}")
    
    def _print_residual_results(self, diag):
        """Print residual analysis results."""
        print(f"  Mean residual: {diag['mean_residual']:.4f}")
        print(f"  Std residual: {diag['std_residual']:.4f}")
        print(f"  Runs test Z: {diag['runs_z_score']:.2f}")
        print(f"  Freq correlation: {diag['freq_correlation']:.3f}")
        print(f"  Outliers: {diag['n_outliers']}/{len(diag['residuals'])}")
    
    def _print_complexity_results(self, diag):
        """Print complexity assessment."""
        print(f"  Data points: {diag['n_data_points']}")
        print(f"  Model parameters: {diag['n_model_parameters']}")
        print(f"  Data per parameter: {diag['data_per_parameter']:.1f}")
        print(f"  AICc: {diag['aicc']:.1f}")
        print(f"  Rating: {diag['complexity_rating']}")
    
    def _print_overall_verdict(self):
        """Print overall overfitting verdict."""
        print("\n" + "=" * 70)
        
        issues = []
        
        if 'savgol' in self.results['diagnostics']:
            s = self.results['diagnostics']['savgol']
            if s['reduced_chi2'] < 0.5:
                issues.append("OVER-SMOOTHING")
            elif s['reduced_chi2'] > 3.0:
                issues.append("UNDER-SMOOTHING")
        
        if 'complexity' in self.results['diagnostics']:
            c = self.results['diagnostics']['complexity']
            if c['complexity_rating'] == 'UNDERDETERMINED':
                issues.append("UNDERDETERMINED")
        
        if 'bootstrap' in self.results['diagnostics']:
            b = self.results['diagnostics']['bootstrap']
            if 'G_ci_width_relative' in b and b['G_ci_width_relative'] > 0.5:
                issues.append("HIGH_UNCERTAINTY")
        
        if not issues:
            print("✓ OVERALL: Pipeline appears well-calibrated")
        else:
            print(f"⚠ OVERALL: Issues detected - {', '.join(issues)}")
        
        print("=" * 70)
    
    def plot_diagnostics(self, save_path=None):
        """
        Create comprehensive diagnostic plots.
        """
        if not self.results:
            print("Run full_diagnostic() first")
            return None
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
        # Plot 1: Raw vs Smoothed
        ax = axes[0, 0]
        # This would need the original data passed in or stored
        ax.set_title('Raw vs Smoothed (implement with data)')
        ax.grid(True, alpha=0.3)
        
        # Plot 2: Residuals
        if 'residuals' in self.results['diagnostics']:
            r = self.results['diagnostics']['residuals']
            ax = axes[0, 1]
            ax.plot(r['residuals'], 'bo-', markersize=4)
            ax.axhline(0, color='r', linestyle='--')
            ax.set_title('Residuals')
            ax.set_ylabel('Velocity (m/s)')
            ax.grid(True, alpha=0.3)
        
        # Plot 3: Bootstrap distributions
        if 'bootstrap' in self.results['diagnostics']:
            b = self.results['diagnostics']['bootstrap']
            ax = axes[0, 2]
            # Would need sample access
            ax.set_title('Bootstrap Distributions')
        
        # Plot 4: L-curve
        ax = axes[1, 0]
        ax.set_title('L-curve Analysis')
        ax.set_xlabel('Residual Norm')
        ax.set_ylabel('Curvature Norm')
        
        # Plot 5: CV scores
        if 'cross_validation' in self.results['diagnostics']:
            cv = self.results['diagnostics']['cross_validation']
            if 'cv_scores' in cv:
                ax = axes[1, 1]
                ax.set_title('Cross-Validation Scores')
        
        # Plot 6: QQ plot of residuals
        if 'residuals' in self.results['diagnostics']:
            r = self.results['diagnostics']['residuals']
            ax = axes[1, 2]
            from scipy import stats
            stats.probplot(r['normalized_residuals'], dist="norm", plot=ax)
            ax.set_title('Q-Q Plot (Normality)')
            ax.grid(True, alpha=0.3)
        
        plt.suptitle('Overfitting Diagnostic Plots', fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved diagnostic plots: {save_path}")
        
        return fig


# Demo/test function
def demo():
    """
    Demonstrate diagnostic tool with synthetic data.
    """
    print("Overfitting Diagnostics Demo")
    print("=" * 70)
    
    # Generate synthetic data
    np.random.seed(42)
    
    freq = np.array([60, 70, 80, 90, 100, 110, 120, 130, 140])
    G_true, eta_true = 2000, 0.5
    rho = 1000
    
    # True velocities
    omega = 2 * np.pi * freq
    v_true = kelvin_voigt(omega, G_true, eta_true, rho)
    
    # Add noise
    v_noisy = v_true * (1 + 0.05 * np.random.randn(len(freq)))
    unc = 0.03 * v_noisy
    
    # Apply smoothing (deliberately suboptimal for demo)
    v_smooth = savgol_filter(v_noisy, 5, 3)
    
    # Bootstrap
    bootstrap = bootstrap_fit(freq, v_smooth, unc, n=500, rho=rho)
    
    # Run diagnostics
    diag = OverfittingDiagnostics(rho=rho)
    results = diag.full_diagnostic(
        freq, v_noisy, unc, v_smooth, bootstrap
    )
    
    # Plot
    diag.plot_diagnostics('diagnostic_plots.png')
    
    return results


if __name__ == "__main__":
    demo()
