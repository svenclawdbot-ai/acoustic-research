# One-Page Quick Schematic

## 2.4 GHz CW Doppler — Homodyne Architecture

```text
                                    VCC 3.3V
                                       │
    ┌──────────────────────────────────┼──────────────────────────────┐
    │                                  │                              │
    │  ┌──────────┐  RF_OUT  ┌───────┐│┌──────┐   LO    ┌─────────┐  │
    │  │  ADF4351 │──────────│ 2-way │├┤ 10dB ├────┬────│ LT5560  │  │
    │  │  2.4GHz  │          │split  │││ atten │    │    │  LO_IN  │  │
    │  │  (0dBm)  │          │(-6dB) ││└──────┘    │    └─────────┘  │
    │  └────┬─────┘          └───┬───┘│            │         │        │
    │       │SPI                 │    │            │    ┌────▼────┐   │
    │       │                   │    │            │    │  I OUT  │   │
    │  ┌────▼─────┐             │    │            │    │  Q OUT  │   │
    │  │ RP GPIO  │             │    │            │    └────┬────┘   │
    │  │ DIO0-2   │             │    │            │         │        │
    │  └──────────┘             │    │            │    ┌────▼────┐   │
    │                           │    │            │    │OPA2197  │   │
    │                           │    │            │    │I/Q Amps │   │
    │                           │    │            │    │G=10     │   │
    │                           │    │            │    └────┬────┘   │
    │                           │    │            │         │        │
    │                           │    │            │    ┌────▼────┐   │
    │                           │    │            │    │ RP IN1  │   │
    │                           │    │            │    │ RP IN2  │   │
    │                           │    │            │    └─────────┘   │
    │                           │    │            │                  │
    │                           │    │       ┌────▼────┐             │
    │                           │    │       │10dB att │             │
    │                           │    │       └───┬────┘             │
    │                           │    │           │                   │
    │                           │    │      ┌──▼───┐   ┌──────┐     │
    │                           │    │      │ PA   │   │ BPF  │     │
    │                           │    │      │+20dBm│   │2.4GHz│     │
    │                           │    │      └──┬───┘   └──┬───┘     │
    │                           │    │         │          │         │
    │                           │    │      ┌──▼───┐   ┌─▼────┐     │
    │                           │    └──────►│ TX   │   │ TX   │     │
    │                           │            │Patch │   │Ant   │     │
    │                           │            │Ant   │   │      │     │
    │                           │            └─────┘   └──────┘     │
    │                           │                                    │
    │                           │                                    │
    │                      ┌────▼────┐                              │
    │                      │  RX     │                              │
    │                      │  Patch  │                              │
    │                      │  Ant    │                              │
    │                      └────┬────┘                              │
    │                           │                                   │
    │                      ┌────▼────┐                              │
    │                      │ LNA   │                              │
    │                      │SPF5189│                              │
    │                      │+20dB  │                              │
    │                      └────┬────┘                              │
    │                           │                                   │
    │                      ┌────▼────┐                              │
    │                      │ LT5560 │                              │
    │                      │ RF_IN  │                              │
    │                      └─────────┘                              │
    │                                                               │
    └───────────────────────────────────────────────────────────────┘
```

## Signal Flow

1. **ADF4351** generates 2.400 GHz CW
2. **Splitter** divides LO to TX and mixer paths
3. **TX path:** Optional PA → antenna → illuminates target
4. **RX path:** Antenna → LNA → LT5560 RF input
5. **LT5560** mixes RF with LO → baseband I/Q Doppler
6. **Op-amps** buffer and amplify I/Q to ±1V for Red Pitaya
7. **Red Pitaya** digitises I/Q → software extracts motion

## Key Parameters

| Parameter | Value |
|-----------|-------|
| RF frequency | 2.400 GHz |
| TX power (with PA) | +20 dBm (100 mW) |
| Antenna gain | +5 dBi each |
| LNA gain | +20 dB |
| Mixer LO drive | -9 dBm (from resistive splitter) |
| Baseband gain | +20 dB (op-amp) |
| ADC full scale | ±1V (Red Pitaya) |
| Max Doppler (walking) | ~32 Hz |
| Min Doppler (breathing) | ~0.1 Hz |

## Power Rails

| Rail | Devices | Current | Source |
|------|---------|---------|--------|
| 5V | Red Pitaya + LNA | ~1A | 5V/2A adapter |
| 3.3V | ADF4351 + PA + LT5560 + Op-amp | ~350mA | AMS1117-3.3 from 5V |

## Build Checklist

- [ ] ADF4351 outputs 2.4 GHz (verify with RTL-SDR or spectrum analyser)
- [ ] Splitter divides power evenly
- [ ] LNA powered and amplifying (check with signal generator)
- [ ] LT5560 I/Q outputs present with LO only (leakage/offset)
- [ ] Add RF input — signal increases (mixer working)
- [ ] Op-amp outputs swing ±0.5V with motion
- [ ] Red Pitaya captures I/Q without clipping
- [ ] Software shows Doppler peak when waving hand
- [ ] Through-wall test: walk behind drywall, see 1-5 Hz peak
