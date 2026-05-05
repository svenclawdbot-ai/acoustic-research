# Engineering Challenge — 2026-04-09 (Thursday)

## Real-Time Visualization Performance Optimization

### Problem Context

Your DMA acquisition firmware and PyQtGraph real-time display are now functional. Today's challenge focuses on **performance optimization** to achieve sub-50ms end-to-end latency from ultrasound pulse to screen update. This is critical for interactive beamforming adjustment.

### Challenge

Optimize the real-time visualization pipeline to achieve **<50ms latency** at 20 FPS with 8 channels @ 20 MSa/s.

---

### Part 1: USB Protocol Optimization (45 min)

**Current bottleneck:** USB CDC at 921600 baud limits throughput to ~90 kB/s, but you're trying to transfer 8ch × 20 MSa/s = 40 MB/s raw data.

**Realization:** You already solved this with PSRAM buffering. Now optimize the protocol.

**Task:**

1. **Implement compressed data transfer**
   - Add delta encoding to firmware (`dma_acquisition.c`)
   - 12-bit ADC values typically change slowly — delta fits in 8 bits
   - Expected compression: 2-4×

2. **Add bulk transfer mode**
   - Transfer only active display window (not full buffer)
   - For 100μs window at 20 MSa/s: 2000 samples × 8ch × 2 bytes = 32 KB
   - At 90 kB/s: ~360ms transfer time — still too slow!

3. **Implement selective channel transfer**
   - Only transfer channels currently visible/selected
   - Reduce to 4 channels → 16 KB → 180ms — better but not realtime

**Deliverable:**
- Updated `dma_acquisition.c` with delta encoding
- Python decoder in `realtime_display.py`
- Calculate actual compression ratio achieved

**Stretch:** Implement run-length encoding (RLE) for zeros (pre-trigger silence)

---

### Part 2: Zero-Copy Display Architecture (50 min)

**Current flow:** DMA → PSRAM → USB → Python buffer → PyQtGraph → GPU

**Problem:** Multiple copies = latency

**Task:**

1. **Implement shared memory approach**
   - Use Python `mmap` to share buffer between acquisition thread and display
   - Display thread reads directly from acquisition buffer
   - Eliminates one copy

2. **Double-buffering for display**
   - While displaying frame N, prepare frame N+1 in background
   - Swap pointers atomically (no copy)

3. **Profile current latency**
   ```python
   import time
   
   timestamps = {
       'acquisition': [],
       'usb_transfer': [],
       'processing': [],
       'render': []
   }
   
   # Measure each stage
   ```

**Deliverable:**
- Modified `realtime_display.py` with zero-copy architecture
- Latency breakdown showing time per stage
- Before/after comparison

---

### Part 3: GPU-Accelerated Processing (40 min)

**Current:** NumPy array operations on CPU

**Task:**

1. **Move processing to GPU**
   - Use CuPy or PyTorch for ADC-to-mV conversion
   - GPU can process 8 channels in parallel
   - Keep data on GPU (avoid CPU↔GPU transfer)

2. **Shader-based trigger detection**
   - Implement trigger detection in vertex shader
   - Avoids CPU readback

3. **Benchmark comparison**
   - CPU processing time vs GPU processing time
   - Memory bandwidth utilization

**Deliverable:**
- Optional GPU acceleration in `realtime_display.py`
- Fallback to CPU if no GPU
- Performance comparison table

---

### Part 4: End-to-End Latency Optimization (45 min)

**Target:** <50ms from trigger to display

**Task:**

1. **Measure current baseline**
   - Add timing markers throughout pipeline
   - Use oscilloscope: trigger GPIO pulse → measure time to USB ACK

2. **Identify biggest contributor**
   - Is it: USB transfer? Processing? Display render?
   - Focus optimization effort there

3. **Implement optimizations**
   - If USB: Increase baud rate or compress more
   - If processing: Use numba JIT or vectorize
   - If render: Reduce plot complexity, disable anti-aliasing

4. **Verify achievement**
   - Oscilloscope measurement of actual latency
   - Software timestamp correlation

**Deliverable:**
- Documented latency breakdown (pie chart)
- Optimized configuration achieving <50ms
- Oscilloscope screenshot showing measurement

---

### Key Equations

**Latency budget:**
```
total = t_acquisition + t_transfer + t_process + t_render

Target: 50ms
Acquisition: ~5ms (DMA to PSRAM)
Transfer: ~20ms (compressed 4×)
Process: ~5ms (GPU)
Render: ~16ms (60 FPS)
Margin: ~4ms
```

**USB transfer time:**
```
t_transfer = (samples × channels × bytes_per_sample × compression_ratio) / baud_rate
```

**Frame rate vs latency:**
```
latency_render = 1 / fps = 16.7ms @ 60 FPS
```

---

### Hints

- Use `pyinstrument` or `cProfile` for Python profiling
- Monitor USB buffer levels with `cat /sys/kernel/debug/usb/usbmon/x`
- PyQtGraph has built-in FPS counter: `pg.ptime`
- Consider using `asyncio` for non-blocking USB I/O

---

### Validation Checklist

- [ ] Delta encoding achieves >2× compression
- [ ] Zero-copy reduces memory bandwidth by >30%
- [ ] GPU processing >10× faster than CPU for large arrays
- [ ] Total latency <50ms verified by oscilloscope
- [ ] Display maintains 20 FPS under load
- [ ] No dropped frames at maximum data rate

---

### Connections to Current Work

| This Challenge | Your Existing Work |
|----------------|-------------------|
| Delta encoding | Extends DMA firmware from yesterday |
| Zero-copy display | Optimizes `realtime_display.py` |
| GPU acceleration | Prepares for CUDA-based beamforming |
| Latency measurement | Validates end-to-end pipeline |

---

### Deliverables Summary

1. **Delta-encoded data transfer** (firmware + Python)
2. **Zero-copy display architecture** with profiling
3. **GPU acceleration module** (optional/fallback)
4. **Latency measurement report** with oscilloscope proof
5. **Optimized configuration** achieving <50ms

---

**Difficulty:** Advanced (performance optimization, profiling)  
**Est. Time:** 3 hours  
**Topic:** Software Optimization / Real-time Systems

## Status: 🆕 NOT STARTED

*Generated: 2026-04-09 07:05 UTC*
