# Engineering Challenge — Sunday, May 17, 2026

## Topic: Open Research — Acoustic NDE / Soil Properties

Following yesterday's deep dive into acoustic impedance measurement methods for soil characterization, today's challenge is a continuation and consolidation exercise.

### Context

Yesterday we explored:
1. **Bender elements** — Piezoelectric bimorphs for shear wave generation/detection
2. **Acoustic impedance probes** — Ultrasonic reflection for density/compaction measurement  
3. **Resonance method** — Quarter-wave resonator with transfer matrix analysis
4. **Transfer matrix physics** — Full derivation for layered media impedance extraction

### Today's Challenge

**Build a simulation model** that demonstrates the resonance method physics numerically.

**Deliverable:** Python script that:
1. Implements the transfer matrix method for the PVC-steel-soil layered system
2. Sweeps frequency (10 kHz → 1 MHz)
3. Computes |R(ω)| for 3 different soil impedances:
   - Dry sand: Z = 0.64 MRayls
   - Saturated clay: Z = 2.85 MRayls  
   - Dense rock: Z = 8.0 MRayls
4. Plots the three spectra on one graph
5. Annotates resonance peaks and Q-factors

**Key parameters:**
- PVC: ρ=1400 kg/m³, c=2300 m/s, d=5mm
- Steel: ρ=7850 kg/m³, c=5900 m/s, d=15mm
- Transducer: Z_piezo = 30 MRayls (typical PZT)

**Extension (optional):**
- Add damping to PVC (complex wave speed: c = c_real + i·α)
- Show how Q-factor changes with soil impedance
- Implement inverse problem: given measured spectrum, estimate Z_soil

### Time Budget
2-3 hours focused work

### Output
- `resonance_soil_simulation.py` with plots
- Brief summary of what the plots reveal about soil impedance sensitivity

---

*Sunday = Open Research — adjust scope based on interest and energy*
