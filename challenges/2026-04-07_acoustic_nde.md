# Engineering Challenge — 2026-04-07
## Acoustic NDE: Ultrasonic Signal Classification

### Background
Acoustic Non-Destructive Evaluation (NDE) uses ultrasonic waves to detect flaws in materials without causing damage. A key challenge is distinguishing between different defect types (cracks, voids, inclusions) from noisy ultrasonic signals.

### Today's Challenge
**Implement a classifier for ultrasonic A-scan signals to detect and classify material defects.**

### Requirements

1. **Signal Simulator** (Python/MATLAB)
   - Generate synthetic A-scan signals: clean reference, crack reflection, void, inclusion
   - Add realistic noise (Gaussian, white noise) and attenuation
   - Parameters: frequency (1-10 MHz), material velocity, defect depth

2. **Feature Extraction**
   - Extract features from time-domain signals:
     - Peak amplitude
     - Time-of-flight
     - Signal energy
     - Frequency content (FFT peaks)
     - Wavelet decomposition coefficients

3. **Classifier**
   - Train a simple classifier (k-NN, SVM, or Random Forest)
   - Minimum 85% accuracy on test set
   - Output: defect type + confidence score

4. **Bonus**
   - Implement pulse-echo measurement geometry
   - Add B-scan image generation from multiple A-scans
   - Visualize wave propagation (optional)

### Deliverables
- [ ] Working signal simulator
- [ ] Feature extraction pipeline
- [ ] Trained classifier with evaluation metrics
- [ ] Short report on performance

### Resources
- Start with 1D time-series data
- Use `scikit-learn` for ML, `scipy.signal` for processing
- Reference: ASME V / ASTM E1065 ultrasonic standards

### Time Estimate
2-4 hours for core implementation

---
*Generated for 2026-04-07 | Focus: Signal processing + ML for NDE*
