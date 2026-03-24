# Field-Deployable Shear Wave System: Low-Cost Design

## Project: Portable Viscoelastic Imaging for Remote/Field Use

---

## DESIGN PHILOSOPHY

**Constraints:**
- Total system cost: **< £2,000**
- Weight: **< 5 kg** (portable backpack unit)
- Power: **USB-C or 12V battery** (no mains)
- Operation: **Tablet/laptop control**, wireless data option
- Environment: **Ruggedized** for field conditions

---

## 1. WAVE GENERATION (Low-Cost Portable)

### Selected: Piezo Stack Actuator (Not Transducer)
| Item | Specification | Qty | Cost | Notes |
|------|--------------|-----|------|-------|
| Piezo stack actuator | 10×10×20 mm, 150V, 12 μm displacement | 2 | £80 | Noliac NAC2124 or similar |
| Driving circuit | HV amplifier, 150Vpp, 100 kHz | 1 | £120 | Custom PCB or PiezoDrive PDm200 |
| Microcontroller | Raspberry Pi Pico / Arduino DUE | 1 | £15 | Generates waveforms |
| HV power supply | 12V → 150V DC-DC converter | 1 | £35 | Miniature module |
| Coupling cone | 3D printed PLA + epoxy tip | 2 | £10 | Custom design |
| Mounting bracket | Aluminum, clamp-type | 1 | £25 | Holds actuator perpendicular to surface |

**Why piezo stack vs transducer?**
- Direct mechanical coupling (no fluid bath)
- Lower voltage than traditional transducers
- Simpler impedance matching
- Compact and robust

**Generation Subtotal: £285**

---

## 2. DETECTION SYSTEM (Smartphone-Based)

### Selected: Smartphone Accelerometer Array
| Item | Specification | Qty | Cost | Notes |
|------|--------------|-----|------|-------|
| MEMS accelerometers | ADXL355 (±2g, 20-bit, SPI) | 4 | £60 | Low-noise, 0.25 mg resolution |
| Microcontroller | ESP32-S3 (WiFi + Bluetooth) | 1 | £8 | Acquires 4-ch at 1 kS/s |
| PCB carrier | 4-layer, accelerometer array | 1 | £45 | 40×60 mm, 4 sensors at 2 cm spacing |
| Acrylic housing | IP65 enclosure, custom | 1 | £30 | Protects electronics |
| Magnets | Neodymium, 10mm disc | 4 | £5 | Secure coupling to steel/tissue phantom |
| Coupling gel pads | Silicone elastomer, 3 mm | 10 | £15 | Acoustic coupling to skin/phantom |

**Alternative: Single-point LDV (if budget allows)**
| Item | Specification | Qty | Cost |
|------|--------------|-----|------|
| Polytec PDV-100 | Portable laser vibrometer | 1 | £3,500 |

**Selected: MEMS array (more robust, lower cost)**

**Detection Subtotal: £163**

---

## 3. DATA ACQUISITION (USB/Wireless)

| Item | Specification | Qty | Cost | Notes |
|------|--------------|-----|------|-------|
| Tablet computer | iPad/Android, 10-inch | 1 | £350 | Field interface, data logging |
| OR: Rugged phone | Samsung XCover Pro / Cat S62 | 1 | £450 | More rugged option |
| USB-C hub | 4-port, powered | 1 | £25 | Connects ESP32 + sensors |
| Power bank | 20,000 mAh, 60W PD | 1 | £40 | 8+ hours operation |
| Solar panel | 30W foldable, USB-C out | 1 | £60 | Remote charging |
| Waterproof case | Pelican-style, custom foam | 1 | £45 | IP67 rated |

**DAQ Subtotal: £520** (with tablet) or **£620** (rugged phone)

---

## 4. PHANTOM FABRICATION (Field-Deployable)

| Item | Specification | Qty | Cost |
|------|--------------|-----|------|
| Pre-mixed phantom gel | CIRS Model 049/050 equivalent | 2 L | £120 | 
| OR: Agar powder | Bacteriological grade | 500 g | £30 | Self-mix option |
| Graphite powder | Conductive filler | 250 g | £15 | For attenuation tuning |
| Glycerin | USP grade | 500 ml | £10 | For softening |
| Silicone molds | Cylindrical, disposable | 5 | £25 | 
| Transport containers | Sealed, 1L | 3 | £20 | 

**Phantom Subtotal: £110** (pre-mixed) or **£100** (self-mix)

---

## 5. CALIBRATION & VALIDATION

| Item | Specification | Qty | Cost |
|------|--------------|-----|------|
| Reference spring | Known stiffness (k = 1000 N/m) | 1 | £25 | Mechanical calibration |
| Steel mass | 100 g, precision | 1 | £15 | Inertial reference |
| Oscilloscope (mini) | FNIRSI or similar, 1 MHz | 1 | £80 | Signal debugging |
| Digital multimeter | True RMS, temperature | 1 | £35 | Electrical checks |

**Calibration Subtotal: £155**

---

## 6. ACCESSORIES & CONSUMABLES

| Item | Specification | Qty | Cost |
|------|--------------|-----|------|
| Cables | USB-C, micro-USB, dupont | Assortment | £25 |
| Cable management | Velcro ties, cable wrap | 1 pack | £8 |
| Cleaning kit | Isopropanol, wipes, swabs | 1 | £15 |
| Spare fuses | For HV supply | 5 | £3 |
| Carry case | Pelican 1400 or similar | 1 | £85 |

**Accessories Subtotal: £136**

---

## REVISED TOTAL COST

### Field-Deployable System

| Category | Cost |
|----------|------|
| Wave generation | £285 |
| Detection (MEMS) | £163 |
| Data acquisition | £520 |
| Phantom materials | £110 |
| Calibration | £155 |
| Accessories | £136 |
| **Total** | **£1,369** |

### With Rugged Phone (Alternative)
| Category | Cost |
|----------|------|
| Wave generation | £285 |
| Detection (MEMS) | £163 |
| Data acquisition (rugged) | £620 |
| Phantom materials | £110 |
| Calibration | £155 |
| Accessories | £136 |
| **Total** | **£1,469** |

---

## SYSTEM SPECIFICATIONS

### Physical
- **Total weight**: ~4.2 kg (including case)
- **Dimensions**: 400 × 300 × 150 mm (in Pelican case)
- **Power consumption**: ~5W average, 15W peak
- **Battery life**: 8-10 hours continuous

### Performance
- **Shear wave frequency**: 50-500 Hz (tunable)
- **Displacement sensitivity**: ~10 nm (with MEMS)
- **Spatial resolution**: 2 cm (sensor spacing)
- **Measurement time**: <5 seconds per location

### Environmental
- **Operating temperature**: 5-40°C
- **Humidity**: <90% non-condensing
- **IP rating**: IP54 (splash resistant)

---

## SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────┐
│                    TABLET/PHONE                         │
│              (Python app or web interface)              │
└────────────────────┬────────────────────────────────────┘
                     │ USB-C / Bluetooth
┌────────────────────▼────────────────────────────────────┐
│              ESP32-S3 CONTROLLER                        │
│    ┌──────────────┐  ┌──────────────┐                  │
│    │  Waveform    │  │   4-ch ADC   │                  │
│    │  Generation  │  │   1 kS/s     │                  │
│    └──────┬───────┘  └──────┬───────┘                  │
└───────────┼────────────────┼────────────────────────────┘
            │                │
    ┌───────▼───────┐       │ SPI/I2C
    │  HV Amplifier │       │
    │  (150Vpp)     │       │
    └───────┬───────┘       │
            │               │
    ┌───────▼───────┐       │
    │  Piezo Stack  │       │
    │  (Actuator)   │       │
    └───────┬───────┘       │
            │               │
    ════════▼═══════════════▼═══════════════════════════════
                   PHANTOM/SUBJECT
    ═══════════════════════════════════════════════════════
            │               │
    ┌───────▼───────┐       │
    │  Coupling Gel │       │
    └───────┬───────┘       │
            │               │
    ┌───────▼───────────────▼───────┐
    │   MEMS ACCELEROMETER ARRAY    │
    │   4 sensors, 2 cm spacing     │
    └───────────────────────────────┘
```

---

## SOFTWARE STACK

### Firmware (ESP32)
- **Framework**: Arduino / ESP-IDF
- **Acquisition**: 1 kS/s per channel, DMA buffer
- **Communication**: USB serial or Bluetooth SPP
- **Local storage**: SD card backup

### Host Software (Tablet/Phone)
- **Language**: Python (Kivy/PyQt for GUI)
- **Processing**: Real-time FFT, dispersion analysis
- **Inversion**: Pre-computed lookup tables or lightweight MCMC
- **Output**: G', η maps, uncertainty quantification

### Data Format
- **Raw**: HDF5 or NumPy arrays
- **Processed**: JSON with metadata
- **Export**: CSV for Excel/MATLAB compatibility

---

## FIELD OPERATION PROTOCOL

### Setup (5 minutes)
1. Remove from case, connect power bank
2. Attach tablet, launch app
3. Position actuator and sensor array
4. Apply coupling gel
5. Initiate measurement sequence

### Measurement (per site)
1. **Calibration**: Measure on known phantom (30 s)
2. **Acquisition**: Record wave propagation (5 s)
3. **Processing**: On-tablet inversion (10 s)
4. **Validation**: Check residual, repeat if needed (optional)

### Data Upload (if connectivity available)
- Auto-sync to cloud when WiFi/cellular available
- GPS tagging for location metadata
- Timestamp and environmental conditions

---

## PROCUREMENT PRIORITY

### Immediate (Week 1)
- [ ] Piezo stack actuators (2×)
- [ ] HV amplifier kit
- [ ] ESP32-S3 dev boards
- [ ] ADXL355 accelerometers (4×)

### Short-term (Week 2-3)
- [ ] PCB fabrication (sensor array)
- [ ] Tablet/rugged phone
- [ ] Pelican case
- [ ] Phantom materials

### Testing (Week 4)
- [ ] Bench validation on steel
- [ ] Phantom characterization
- [ ] Firmware development
- [ ] App interface

---

## RISK MITIGATION

| Risk | Mitigation |
|------|-----------|
| MEMS noise too high | Add analog preamp stage (+£20) |
| Coupling inconsistent | Standardized pressure applicator (+£30) |
| Power bank insufficient | Upgrade to 30,000 mAh (+£20) |
| Tablet not rugged | Add waterproof case (+£25) |
| Piezo depolarization | Keep below 120°C, current limiting |

---

## FUTURE UPGRADES

### Phase 2 (£500 additional)
- Upgrade to linear array (8 sensors)
- Add temperature compensation
- Implement real-time tomography

### Phase 3 (£1,000 additional)
- Single-point LDV module (replace MEMS)
- GPS + IMU for position tracking
- Cellular/satellite uplink

---

## SUPPLIERS (Field-Focused)

| Component | Supplier | URL |
|-----------|----------|-----|
| Piezo actuators | Noliac / PiezoDrive | www.noliac.com |
| MEMS sensors | Digi-Key / Mouser | www.digikey.co.uk |
| ESP32 | Espressif / Adafruit | www.adafruit.com |
| Rugged phones | Cat Phones / Samsung | www.catphones.com |
| Enclosures | Pelican / Nanuk | www.peli.com |
| PCB fab | JLCPCB / PCBWay | jlcpcb.com |

---

*Field-deployable design prepared: March 16, 2026*
*Target: Sub-£2,000 portable viscoelastic imaging system*
