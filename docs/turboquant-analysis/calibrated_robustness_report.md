# Calibrated Bayesian Robustness Report

**Date:** 2026-04-22
**Input parameters:** G₀=2000 Pa, G∞=4000 Pa, τ=5.0ms
**Calibrated parameters:** G₀=1110 Pa, G∞=3333 Pa, τ=2.0ms
**Calibration RMSE:** 0.0589 m/s

## Results Summary

| Test | Points | LS G₀ Err | LS G∞ Err | Bayes G₀ Err | Bayes G∞ Err | Bayes CI Width |
|------|--------|-----------|-----------|--------------|--------------|----------------|
| Clean | 17 | 19.4% | 8.2% | 2.6% | 0.7% | 279.7 |
| SNR_30dB | 17 | 16.7% | 8.0% | 3.7% | 0.4% | 315.6 |
| SNR_20dB | 17 | 12.2% | 7.8% | 9.8% | 0.6% | 411.5 |
| SNR_10dB | 17 | 95.5% | 5.6% | 54.7% | 4.3% | 601.8 |
| SNR_5dB | 17 | 95.5% | 15.7% | 62.5% | 9.0% | 600.2 |

## Key Findings

- **Best G₀ recovery:** Clean — 2.6% error
- **Worst G₀ recovery:** SNR_5dB — 62.5% error

## Method

1. **Forward model calibration:** FDTD simulation (512×256 grid) run with input parameters;
   apparent Zener parameters fitted to match numerical dispersion.
2. **Dispersion extraction:** Guided k-ω peak tracking with Hann window + parabolic interpolation.
3. **Bayesian inference:** Metropolis-Hastings MCMC with broad log-normal priors around calibrated values.
4. **Noise robustness:** AWGN added at specified SNR; same extraction + inference pipeline applied.
