# TurboQuant V5 FPGA

Red Pitaya STEMlab 125-14 integration for the V5 8-channel acoustic NDE system.

## Files

| File | Description |
|------|-------------|
| `v5_red_pitaya_bd.tcl` | Vivado block design script |
| `v5_mux_controller.v` | Verilog MUX controller (AXI-Lite) |
| `v5_red_pitaya.xdc` | Pin constraints (XDC) |
| `v5_api.py` | Python API for acquisition |

## Quick Start

### 1. Build FPGA Bitstream

```bash
# In Vivado Tcl console
source v5_red_pitaya_bd.tcl

# Or command line
vivado -mode batch -source v5_red_pitaya_bd.tcl
```

### 2. Generate Bitstream

```bash
cd v5_acquisition/
launch_runs impl_1 -to_step write_bitstream
wait_on_run impl_1
```

### 3. Copy to Red Pitaya

```bash
scp v5_acquisition.runs/impl_1/v5_acquisition_wrapper.bit root@192.168.1.100:/root/v5.bit
cat v5_acquisition.runs/impl_1/v5_acquisition_wrapper.bin > /dev/xdevcfg
```

### 4. Run Python API

```python
from fpga.v5_api import V5RedPitaya

rp = V5RedPitaya("192.168.1.100", mode="scpi")
rp.set_source_ricker(frequency=150e3, amplitude=0.5)
waveforms = rp.acquire_all_channels(decimation=64)
```

## Architecture

```
[Red Pitaya Zynq 7010]
    │
    ├── DAC0 ──► Power Amp ──► Source Piezo
    │
    ├── ADC0 ──► Preamp ◄──┬── DG408 MUX ──► 8x Receiver Piezos
    │                      │
    ├── GPIO ──────────────┘ (MUX control)
    │
    └── AXI DMA ──► ARM DDR ──► Python API
```

## Performance

| Mode | 8-ch Scan Time | Frame Rate |
|------|---------------|------------|
| SCPI | ~80 ms | 12 Hz |
| DMA (target) | ~35 ms | 28 Hz |

## Next Steps

1. Complete DMA driver (`_dma_load_waveform`, `_acquire_dma`)
2. Add AXI Stream BRAM reader for DAC waveform
3. Test with real hardware
4. Optimize for real-time processing
