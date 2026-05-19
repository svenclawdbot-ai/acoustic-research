# Engineering Challenge — Tuesday, May 19, 2026

## Topic: Multi-Layer Soil Impedance Inversion

### Background
You've developed the transfer matrix method for a 2-layer backing structure (PVC + steel) sitting on a semi-infinite soil half-space. The resonance spectrum encodes the soil's acoustic impedance.

**Real soil is layered.** Topsoil, subsoil, clay pans, sand lenses — each layer has different impedance. A single half-space model collapses all of this into one number.

### The Challenge

Extend the transfer matrix Python code (`transfer_matrix.py`) to handle **N-layer soil profiles** and demonstrate that you can resolve layer boundaries and impedances from the resonance spectrum.

### Deliverables

1. **Code Extension**
   - Modify `transfer_matrix.py` to accept an arbitrary list of layers:
     ```python
     layers = [
         {'name': 'PVC', 'thickness': 0.005, 'density': 1400, 'velocity': 2300},
         {'name': 'Steel', 'thickness': 0.015, 'density': 7850, 'velocity': 5900},
         {'name': 'Topsoil', 'thickness': 0.100, 'density': 1600, 'velocity': 400},
         {'name': 'Clay', 'thickness': 0.200, 'density': 1900, 'velocity': 1500},
         {'name': 'Bedrock', 'thickness': np.inf, 'density': 2500, 'velocity': 3000},
     ]
     ```
   - The last layer must have `thickness=np.inf` (semi-infinite)
   - Build transfer matrices for each layer, multiply them all
   - Compute input impedance and reflection coefficient

2. **Synthetic Test Cases**
   - **Case A:** Single-layer soil (verify against current code)
   - **Case B:** Two-layer soil (topsoil + clay) — show spectrum differs from single-layer equivalent
   - **Case C:** Thin sand lens (50mm) embedded in clay — show detectability

3. **Sensitivity Analysis**
   - How thin can a layer be and still affect the spectrum?
   - Plot: minimum detectable layer thickness vs. frequency
   - Consider: wavelength in layer = λ = c/f. Layer must be ~λ/4 or thicker to create interference.

4. **Inversion Proof-of-Concept**
   - Given a synthetic spectrum from a 2-layer soil, can you fit for both layer thicknesses and impedances?
   - Use least-squares or MCMC (you've done MCMC before in the Bayesian challenge)
   - Report: parameter identifiability — which parameters are well-constrained?

### Key Physics

For an N-layer system, the total transfer matrix is:

$$T_{total} = T_{backing,1} \times T_{backing,2} \times \cdots \times T_{soil,1} \times T_{soil,2} \times \cdots$$

Each layer adds its own phase shifts and impedance transformations. The spectrum becomes richer — more peaks, more modulations — but also more ambiguous.

**The inversion problem is ill-posed:** many layer combinations can produce similar spectra. You need constraints:
- Fix backing layers (known PVC + steel)
- Assume monotonic impedance increase with depth
- Limit number of soil layers (Occam's razor)

### Success Criteria

- [ ] Code runs for 2-layer, 3-layer, and 5-layer systems
- [ ] Spectra visually distinguishable for different soil profiles
- [ ] Minimum detectable thickness estimated
- [ ] Inversion recovers layer parameters within 10% for synthetic data

### Time Estimate
4-6 hours

### Why This Matters
A single soil impedance measurement tells you "the soil is stiff." A multi-layer measurement tells you "there's a compacted pan at 15cm depth" — actionable information for precision agriculture.

---
*Generated: 2026-05-19*
