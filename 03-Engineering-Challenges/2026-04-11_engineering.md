# Engineering Challenge — 2026-04-11 (Saturday)
## Acoustic NDE: Full Matrix Capture (FMC) & Total Focusing Method (TFM)

### Background

You've mastered phased array beamforming with sequential sector scanning. Today you advance to **Full Matrix Capture (FMC)** — the "record everything, focus later" paradigm that enables the **Total Focusing Method (TFM)**. FMC/TFM provides:
- **Optimal resolution** at every point in the image (not just focal zone)
- **Arbitrary focal laws** applied in post-processing
- **Multiple view combinations** (TT, TT-T, TTT-T for welds)
- **Superior defect characterization** for critical applications

This is the state-of-the-art in industrial ultrasonic imaging.

---

## Part 1: FMC Data Acquisition (60 min)

### Problem
Capture the full time-domain signals from every transmit-receive pair.

**FMC Matrix:**
For an N-element array, you acquire N×N A-scans:
- Transmit on element i
- Receive on ALL elements j = 1...N simultaneously
- Store full time history

### Tasks

1. **FMC acquisition sequence**
   ```
   For tx = 1 to N:
       Fire element tx
       Record on all N receivers simultaneously
       Store: data[tx][rx][time]
   ```
   
   Calculate data size for your system:
   ```
   N = 64 elements
   Samples = 2048 @ 20 MSa/s (100μs window)
   12-bit ADC (2 bytes stored)
   
   FMC size = 64 × 64 × 2048 × 2 = 16.8 MB per frame
   ```

2. **Modify firmware for FMC mode**
   Extend your DMA acquisition to support:
   ```c
   typedef struct {
       uint16_t tx_element;        // Current transmitter
       uint16_t rx_mask;           // Which elements receive (0xFFFF = all)
       uint32_t samples_per_acq;   // Samples to capture
       uint16_t *data_buffer;      // Pointer to N×N×samples buffer
   } FMC_Config;
   
   void acquire_fmc_frame(FMC_Config *config) {
       for (int tx = 0; tx < N_ELEMENTS; tx++) {
           // Fire element tx
           pulse_element(tx);
           
           // DMA all channels simultaneously
           start_multi_channel_dma(config->rx_mask);
           
           // Wait for completion
           wait_for_dma_complete();
           
           // Store to PSRAM at offset
           save_to_psram(tx, dma_buffer);
       }
   }
   ```

3. **Optimize acquisition speed**
   Current bottleneck: sequential TX firing
   - At 100μs pulse-receive + 10μs setup = 110μs per TX
   - 64 elements = 7ms per FMC frame
   - Target: <100ms total (10 FPS FMC imaging)

   **Optimization:** Parallel receive is already done. Can you pipeline?

### Deliverable
- `fmc_acquisition.c` firmware module
- Calculation: memory requirements for 1 second of FMC data
- Acquisition timing budget (elements vs frame rate tradeoff)

---

## Part 2: TFM Image Reconstruction (75 min)

### Problem
Implement the Total Focusing Method to achieve diffraction-limited resolution everywhere.

**TFM Principle:**
For each pixel in the image, sum contributions from all TX-RX pairs with correct time-of-flight:

```
I(x,z) = | Σ Σ sᵢⱼ(τᵢ(x,z) + τⱼ(x,z)) |
          i j
```

where:
- `sᵢⱼ(t)` = signal from transmit i, receive j
- `τᵢ(x,z)` = time from element i to point (x,z)
- Sum coherently for focusing, incoherently for robustness

### Tasks

1. **Calculate time-of-flight maps**
   ```python
   import numpy as np
   
   def compute_tof_map(element_pos, x_grid, z_grid, c):
       """
       Compute time-of-flight from each element to each image point.
       
       Returns: tof[element_idx, x_idx, z_idx]
       """
       n_elements = len(element_pos)
       nx, nz = len(x_grid), len(z_grid)
       tof = np.zeros((n_elements, nx, nz))
       
       for i, x_el in enumerate(element_pos):
           for ix, x in enumerate(x_grid):
               for iz, z in enumerate(z_grid):
                   distance = np.sqrt((x - x_el)**2 + z**2)
                   tof[i, ix, iz] = distance / c
       
       return tof
   ```

2. **Implement TFM reconstruction**
   ```python
   class TFMReconstructor:
       def __init__(self, element_positions, c, sample_rate):
           self.x_elements = element_positions
           self.c = c
           self.fs = sample_rate
           self.n_elements = len(element_positions)
       
       def reconstruct(self, fmc_data, x_grid, z_grid, mode='total'):
           """
           fmc_data: shape (n_elements, n_elements, n_samples)
           mode: 'total' (sum all paths), 'direct', 'skip'
           Returns: image[nz, nx]
           """
           image = np.zeros((len(z_grid), len(x_grid)))
           
           for iz, z in enumerate(z_grid):
               for ix, x in enumerate(x_grid):
                   # Compute TOF from each element to this point
                   distances = np.sqrt((x - self.x_elements)**2 + z**2)
                   tof_tx = distances / self.c
                   tof_rx = tof_tx  # Same for RX (reciprocity)
                   
                   # Sum over all TX-RX pairs
                   amplitude = 0
                   for i in range(self.n_elements):
                       for j in range(self.n_elements):
                           total_time = tof_tx[i] + tof_rx[j]
                           sample_idx = int(total_time * self.fs)
                           
                           if 0 <= sample_idx < fmc_data.shape[2]:
                               amplitude += fmc_data[i, j, sample_idx]
                   
                   image[iz, ix] = amplitude
           
           return image
   ```

3. **Optimize with vectorization**
   The nested loops are slow. Vectorize:
   ```python
   def reconstruct_vectorized(self, fmc_data, x_grid, z_grid):
       """Vectorized TFM for speed."""
       nz, nx = len(z_grid), len(x_grid)
       image = np.zeros((nz, nx))
       
       # Precompute all distances: shape (n_elements, nz, nx)
       X, Z = np.meshgrid(x_grid, z_grid)
       distances = np.sqrt(
           (X[None, :, :] - self.x_elements[:, None, None])**2 + 
           Z[None, :, :]**2
       )
       tof = distances / self.c
       
       # For each TX-RX pair, add contribution
       for i in range(self.n_elements):
           for j in range(self.n_elements):
               total_tof = tof[i] + tof[j]  # Shape (nz, nx)
               sample_indices = (total_tof * self.fs).astype(int)
               
               # Valid indices mask
               valid = (sample_indices >= 0) & (sample_indices < fmc_data.shape[2])
               
               # Add contributions where valid
               image[valid] += fmc_data[i, j, sample_indices[valid]]
       
       return np.abs(image)
   ```

4. **Implement TFM modes for weld inspection**
   Different wave paths reveal different defect orientations:
   
   | Mode | Path | Use Case |
   |------|------|----------|
   | TT | Transmit longitudinal → Receive longitudinal | General imaging |
   | TT-T | T-transmit → mode conversion at defect → T-receive | Tilted cracks |
   | TTT-T | Triple skip (backward wall echo) | Complex geometry |
   
   ```python
   def tfm_mode(self, fmc_data, mode='TT'):
       """
       mode: 'TT', 'TT-T', 'T-TT', etc.
       Handles mode conversion at interfaces.
       """
       # Mode velocities
       v_long = 5900  # Steel longitudinal
       v_shear = 3200  # Steel shear
       
       if mode == 'TT':
           return self.reconstruct(fmc_data, v_long, v_long)
       elif mode == 'TT-T':
           # Mode conversion at defect
           return self.reconstruct_mode_conversion(fmc_data, v_long, v_long, v_shear)
       # ... etc
   ```

### Deliverable
- `tfm_reconstructor.py` with vectorized implementation
- Reconstruction time benchmark (target: <5s for 64×64×2048 FMC → 512×256 image)
- TFM image comparison: PAUT sector scan vs TFM on same defect

---

## Part 3: Resolution & Sensitivity Analysis (45 min)

### Problem
Quantify TFM's resolution advantage over conventional PAUT.

### Tasks

1. **Theoretical resolution limit**
   TFM achieves half the pulse width (round-trip focusing):
   ```
   δx_TFM ≈ λ / 2  (lateral at any depth)
   δz_TFM ≈ c / (2 × bandwidth)  (axial)
   ```
   
   Compare to PAUT:
   ```
   δx_PAUT ≈ λ × z / D  (depth-dependent, D = aperture)
   ```

2. **Point spread function simulation**
   Simulate a point scatterer, reconstruct with TFM:
   ```python
   def simulate_point_scatterer(x_scatter, z_scatter):
       """Generate synthetic FMC data for point target."""
       fmc = np.zeros((N, N, n_samples))
       
       for i in range(N):
           for j in range(N):
               # Time of flight to scatterer and back
               d_tx = np.sqrt((x_scatter - x_elements[i])**2 + z_scatter**2)
               d_rx = np.sqrt((x_scatter - x_elements[j])**2 + z_scatter**2)
               t_total = (d_tx + d_rx) / c
               
               sample = int(t_total * fs)
               if 0 <= sample < n_samples:
                   fmc[i, j, sample] = 1.0  # Impulse response
       
       return fmc
   ```
   
   Extract and plot:
   - Lateral resolution (cross-range profile)
   - Axial resolution (range profile)
   - Side lobe levels

3. **Signal-to-noise analysis**
   TFM improves SNR by √(N²) = N (coherent summation of N² signals).
   
   For 64 elements:
   ```
   SNR_improvement = 10 × log₁₀(64²) ≈ 36 dB
   ```
   
   Verify with simulation adding Gaussian noise.

### Deliverable
- Resolution comparison plot: PAUT vs TFM
- Point spread function analysis
- SNR improvement calculation

---

## Part 4: GPU-Accelerated Real-Time TFM (60 min)

### Problem
TFM is computationally heavy. Achieve real-time reconstruction using GPU.

### Tasks

1. **CUDA TFM kernel**
   ```cuda
   __global__ void tfm_kernel(float *fmc_data, float *image, 
                              float *tof_tx, float *tof_rx,
                              int n_elements, int n_samples,
                              int nx, int nz) {
       int ix = blockIdx.x * blockDim.x + threadIdx.x;
       int iz = blockIdx.y * blockDim.y + threadIdx.y;
       
       if (ix >= nx || iz >= nz) return;
       
       float amplitude = 0.0f;
       
       for (int i = 0; i < n_elements; i++) {
           for (int j = 0; j < n_elements; j++) {
               float t = tof_tx[i * nz * nx + iz * nx + ix] + 
                        tof_rx[j * nz * nx + iz * nx + ix];
               int sample = (int)(t * fs);
               
               if (sample >= 0 && sample < n_samples) {
                   amplitude += fmc_data[(i * n_elements + j) * n_samples + sample];
               }
           }
       }
       
       image[iz * nx + ix] = fabsf(amplitude);
   }
   ```

2. **PyTorch implementation (simpler)**
   ```python
   import torch
   
   class TFMGPU:
       def __init__(self, n_elements, device='cuda'):
           self.device = device
           self.n_elements = n_elements
       
       def reconstruct(self, fmc_torch, tof_maps):
           """
           fmc_torch: (n_elements, n_elements, n_samples) on GPU
           tof_maps: (n_elements, nz, nx) on GPU
           """
           nz, nx = tof_maps.shape[1], tof_maps.shape[2]
           image = torch.zeros((nz, nx), device=self.device)
           
           # Vectorized reconstruction
           for i in range(self.n_elements):
               for j in range(self.n_elements):
                   total_tof = tof_maps[i] + tof_maps[j]
                   sample_indices = (total_tof * fs).long()
                   
                   valid = (sample_indices >= 0) & (sample_indices < fmc_torch.shape[2])
                   samples = fmc_torch[i, j, sample_indices[valid]]
                   image[valid] += samples
           
           return torch.abs(image)
   ```

3. **Benchmark comparison**
   | Method | Time (64×64×2048 → 512×256) | Speedup |
   |--------|---------------------------|---------|
   | Python loops | ~300s | 1× |
   | NumPy vectorized | ~5s | 60× |
   | GPU (PyTorch) | ~0.1s | 3000× |
   | GPU (CUDA) | ~0.05s | 6000× |

### Deliverable
- `tfm_gpu.py` with PyTorch CUDA implementation
- Benchmark results showing real-time capability (>10 FPS)
- Memory usage analysis

---

## Part 5: Advanced TFM — Multi-Mode Imaging (45 min)

### Problem
Combine multiple TFM modes for complete defect characterization.

### Tasks

1. **Weld inspection simulation**
   Create a test case with:
   - V-weld geometry
   - Side-drilled holes (SDH) at different depths
   - Angled notches (representing cracks)
   
2. **Multi-mode fusion**
   ```python
   def multi_mode_tfm(fmc_data, modes=['TT', 'TT-T', 'T-TT']):
       """
       Combine multiple TFM modes for complete coverage.
       """
       images = {}
       
       for mode in modes:
           images[mode] = tfm_reconstruct(fmc_data, mode)
       
       # Fuse: maximum amplitude projection
       fused = np.max([np.abs(img) for img in images.values()], axis=0)
       
       return images, fused
   ```

3. **Defect characterization**
   From multi-mode response, estimate:
   - Defect location (x, z)
   - Defect size (from -6dB drop)
   - Defect orientation (from which modes see it)
   - Defect type (planar vs volumetric)

### Deliverable
- Multi-mode TFM implementation
- Defect characterization algorithm
- Comparison: single-mode vs multi-mode detection probability

---

## Extension Challenges (Optional)

### A) Plane Wave Imaging (PWI) — Fast Alternative (60 min)
Instead of element-by-element, transmit plane waves at different angles. Reconstruct with similar focusing. Trade-off: faster acquisition, slightly lower SNR.

### B) Adaptive TFM (90 min)
Iteratively weight TX-RX pairs based on image coherence. Suppress noise and grating lobes.

### C) 3D TFM Matrix Array (120 min)
Extend to 2D matrix arrays for full volumetric imaging. Data size: N⁴ (for N×N elements) — requires serious computation!

---

## Key Equations Reference

| Parameter | Formula |
|-----------|---------|
| FMC data size | N² × samples × bytes/sample |
| TFM pixel amplitude | I(x,z) = Σᵢ Σⱼ sᵢⱼ(τᵢ + τⱼ) |
| TFM lateral resolution | δx ≈ λ/2 |
| SNR gain | 20 log₁₀(N) dB |
| Frame rate | 1 / (N × t_acq_per_element) |

---

## Connections to Your Existing Work

| Previous Work | This Challenge |
|--------------|----------------|
| Phased array beamforming | → Full matrix capture (record everything) |
| Sector scan imaging | → TFM (focus everywhere) |
| GPU acceleration for display | → GPU TFM reconstruction |
| Delay law calculation | → TOF maps for all pixels |

---

## Deliverables Summary

1. **FMC acquisition firmware** — sequential or optimized
2. **TFM reconstructor** — CPU vectorized version
3. **Resolution analysis** — PSF and SNR comparison
4. **GPU-accelerated TFM** — real-time reconstruction
5. **Multi-mode imaging** — weld inspection simulation

---

## Resources

- **Paper:** *Theoretical comparison of conventional and TAFT-ITFM imaging* — Holmes et al.
- **Standard:** BS EN 16018:2011 — TFM for weld inspection
- **Tutorial:** "Introduction to TFM" — Olympus NDT
- **Code:** Open-source `pyTFM` or `ULTRAPY`

---

**Difficulty:** Expert (heavy computation, GPU programming)
**Est. Time:** 4.5 hours (core) + 3 hours (extensions)
**Topic:** Acoustic NDE / Advanced Imaging / GPU Computing

## Status: 🆕 NOT STARTED

*Generated: 2026-04-11 07:05 UTC*
