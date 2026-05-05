📅 2026-04-21 - Acoustic NDE Challenge

🎯 Today's Challenge: Material Parameter Inversion from Dispersion Curves

The 2D FDTD simulator generates wave fields. Now let's extract usable information from them.

Tasks:
1. Implement 2D FFT on simulated wave fields to obtain frequency-wavenumber (f-k) spectra
2. Extract dispersion curves (frequency vs. phase velocity) from peaks in f-k domain
3. Implement least-squares fitting to invert for (G', η) given a target dispersion curve
4. Validate: recover known parameters from synthetic data

Stretch Goal:
- Add Gaussian noise to synthetic data and quantify inversion robustness (SNR vs. parameter error)

Deliverable: Working inversion pipeline + plot showing true vs. recovered dispersion curves

⏱️  Time Budget: 2-3 hours focused work
📝 Log progress in: /home/james/.openclaw/workspace/memory/2026-04-21.md
