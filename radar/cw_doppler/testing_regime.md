# CW Doppler Radar — Testing Regime & Security Applications

## Philosophy

Build confidence in three stages:
1. **Signal chain validation** — Does the hardware produce meaningful baseband?
2. **Controlled environment** — Can we detect known targets at known ranges?
3. **Real-world deployment** — Does it work in actual security scenarios?

Each stage has pass/fail criteria, metrics, and decision gates.

---

## Stage 1: Signal Chain Validation

### 1.1 LO Verification
**Goal:** Confirm 2.400 GHz output from ADF4351.

**Test:**
```
Power up ADF4351 → program 2.400 GHz → verify with:
  A. RTL-SDR dongle + SDR# / GQRX (look for peak at 2.400 GHz)
  B. Cheap WiFi spectrum analyser app on phone (indirect)
  C. Red Pitaya spectrum analyser app (if covering 2.4 GHz with downconverter)
```

**Pass criteria:**
- Peak within ±1 MHz of 2.400 GHz
- Output power > -5 dBm
- Clean spectrum (no large spurs within ±50 MHz)
- Stable over 10 minutes (no drift > 100 kHz)

**Fail actions:**
- Check SPI register values (different board variants need different configs)
- Verify 25 MHz reference oscillator is running
- Check supply voltage (3.3V ± 5%)
- Add heatsink if PA is loading the ADF4351 output

---

### 1.2 Mixer Functionality
**Goal:** Confirm LT5560 produces baseband output when RF is applied.

**Test (without antennas):**
```
ADF4351 ──► splitter ──► LO port (LT5560 pin 7)
                         │
Signal generator ──► RF port (LT5560 pin 1) @ 2.400001 GHz (+1 kHz offset)
                         │
                    LT5560 I/Q output ──► Red Pitaya IN1/IN2 (or scope)
```

**What you should see:**
- I output: 1 kHz sine wave (~50 mVpp)
- Q output: 1 kHz cosine wave (~50 mVpp)
- 90° phase relationship between I and Q

**Pass criteria:**
- Baseband tone visible at expected offset frequency
- I and Q amplitudes within ±3 dB of each other
- Phase quadrature within ±10°
- No excessive DC offset (> 100 mV suggests LO leakage or imbalance)

**Fail actions:**
- Check LO power at mixer port (need -10 to +5 dBm)
- Verify RF input level (start with -30 dBm, adjust)
- Check LT5560 supply and enable pin
- Swap I and Q outputs to confirm both channels work

---

### 1.3 LNA Verification
**Goal:** Confirm SPF5189Z provides +20 dB gain at 2.4 GHz.

**Test:**
```
Signal generator ──► [known attenuator] ──► LNA ──► spectrum analyser / RTL-SDR
                                      (measure input power)
                                      (measure output power)
```

**Pass criteria:**
- Gain = 18–22 dB at 2.4 GHz
- Noise figure < 2 dB (hard to measure without proper NF analyser, but check SNR improvement)
- Supply current 60–100 mA at 5V

**Fail actions:**
- Check bias voltage (many modules need 5V, some 3.3V)
- Verify input/output aren't swapped
- Add input protection (series resistor or attenuator) if self-oscillating

---

### 1.4 Baseband Amplifier Verification
**Goal:** Confirm op-amp stage amplifies without oscillation or clipping.

**Test:**
```
Function generator ──► [10µF DC block] ──► op-amp input ──► scope / Red Pitaya
                (100 mVpp sine @ 1 Hz, 10 Hz, 100 Hz, 1 kHz)
```

**Pass criteria:**
- Gain = 9–11 (for G=10 config)
- Flat response 0.1 Hz – 1 kHz (±1 dB)
- No oscillation (check with scope — should be clean sine)
- Output offset < 50 mV (with inputs grounded)
- Output swings to ±1.5V without clipping (on ±3.3V supply)

**Fail actions:**
- Add supply decoupling (100 nF + 10 µF right at op-amp pins)
- Check feedback capacitor isn't open (stops oscillation)
- Verify input DC block capacitor polarity

---

### 1.5 End-to-End Loopback (No Antennas)
**Goal:** Confirm the full chain from LO generation to Red Pitaya capture.

**Test:**
```
ADF4351 ──► splitter ──┬──► [10 dB atten] ──► TX side (just a cable)
                       │
                       └──► LO port (LT5560)
                                            
TX cable ──[couple to RX cable]──► [LNA] ──► [LT5560 RF] ──► [op-amp] ──► [RP IN1/IN2]
```

Put TX and RX cables near each other (coupled, not connected). Use attenuators to simulate path loss.

**Procedure:**
1. Set up chain, power on
2. Flash SDR transceiver image on Red Pitaya
3. Run `cw_doppler.py --mode baseband --no-plot`
4. Wiggle the cables (change coupling) — look for power change
5. Introduce a small frequency offset (change ADF4351 by 1 kHz) — look for beat note

**Pass criteria:**
- Red Pitaya receives baseband signal
- Signal changes when cable coupling changes
- No clipping (ADC readings within ±0.9V)
- Noise floor is stable

**Decision gate:**
- ✅ Pass → Move to Stage 2 (antenna testing)
- ❌ Fail → Debug individual blocks (1.1–1.4)

---

## Stage 2: Controlled Environment Testing

### 2.1 Antenna Validation
**Goal:** Confirm antennas radiate and receive at 2.4 GHz.

**Test:**
```
Setup: TX antenna ──[2 m]──► RX antenna (line-of-sight)
       ADF4351 + optional PA → TX
       RX → LNA → LT5560 → RP
```

**Procedure:**
1. Place antennas 2 m apart, facing each other
2. Run CW Doppler software
3. Record baseline power for 30 seconds
4. Place a large metal object (baking tray, aluminium foil) between antennas
5. Record power change
6. Remove object — power should return to baseline

**Pass criteria:**
- Baseline power stable (±1 dB over 30 s)
- Metal object causes > 6 dB power drop (reflection/absorption)
- Power recovers when object removed

**Metrics:**
- Baseline level (arbitrary units, log for consistency)
- Change with obstruction (dB)
- Recovery time (should be instant for CW)

---

### 2.2 Doppler Detection — Hand Motion
**Goal:** Detect motion and extract Doppler frequency.

**Test:**
```
Setup: TX/RX side by side, 1 m from desk
       Person waves hand at 0.5 m/s, 1 m/s, 2 m/s
```

**Expected Doppler (2.4 GHz):**
- 0.5 m/s → 8 Hz
- 1.0 m/s → 16 Hz
- 2.0 m/s → 32 Hz

**Procedure:**
1. Start acquisition, record 60 seconds
2. Person waves hand at known speed (use metronome: 1 Hz = ~0.5 m/s amplitude)
3. Save spectrogram data
4. Post-process: find peak frequency in walking band (1–50 Hz)

**Pass criteria:**
- Spectrogram shows clear peak at expected frequency (±20%)
- Peak SNR > 10 dB above noise floor
- Peak duration matches motion duration

**Metrics:**
- Measured Doppler frequency vs. expected
- SNR (dB)
- Detection latency (time from motion start to peak detection)

---

### 2.3 Micro-Motion Detection — Breathing
**Goal:** Detect chest displacement from breathing.

**Test:**
```
Setup: TX/RX 1 m from seated person
       Person breathes normally (12 breaths/min = 0.2 Hz)
       Then holds breath for 10 seconds
       Then breathes again
```

**Expected:**
- Breathing: 0.1–0.3 Hz Doppler
- Chest displacement: 4–12 mm peak-to-peak
- Doppler amplitude: proportional to displacement × frequency

**Procedure:**
1. Start acquisition, 2 minutes
2. Person breathes normally for 60 seconds
3. Person holds breath for 10 seconds
4. Person breathes normally again

**Pass criteria:**
- Spectrogram shows 0.2 Hz peak during breathing
- Peak disappears during breath-hold
- Peak returns when breathing resumes
- Phase trace shows sinusoidal variation matching breath rate

**Metrics:**
- Breathing rate accuracy (compare to manual count)
- Detection range (how far can the person be?)
- False negative rate (missed breath cycles)

**Decision gate:**
- ✅ Pass → Move to Stage 3 (through-wall and security scenarios)
- ❌ Fail → Check: LNA gain sufficient? Antenna alignment? Person too far? Add PA?

---

### 2.4 Range Calibration
**Goal:** Understand how detection quality varies with distance.

**Test:**
```
Setup: Person walks toward radar from 10 m, 5 m, 3 m, 2 m, 1 m
       Record SNR at each distance
```

**Metrics table:**

| Distance | Walking SNR (dB) | Breathing SNR (dB) | Notes |
|----------|-----------------|-------------------|-------|
| 10 m | | | LOS only |
| 5 m | | | |
| 3 m | | | |
| 2 m | | | |
| 1 m | | | |

**Expected trend:** SNR falls as 1/R⁴ (radar range equation for monostatic).

---

### 2.5 Clutter Rejection
**Goal:** Confirm the system ignores static clutter (walls, furniture).

**Test:**
```
Setup: Radar in room with furniture, walls, ceiling
       Person hidden behind furniture vs. visible
```

**Procedure:**
1. Start acquisition, 60 seconds, no person
2. Verify spectrogram is flat (only noise)
3. Person walks behind desk (still in room, blocked by furniture)
4. Verify detection still works (Doppler from person reaches radar)
5. Person stops behind desk, holds still
6. Verify no false alarm (static target rejected by HPF)

**Pass criteria:**
- No false motion alarms from stationary furniture
- Person detected even when partially occluded
- Static person (holding breath, not moving) not detected

---

## Stage 3: Security Application Testing

### 3.1 Through-Wall Detection
**Goal:** Detect human presence through drywall.

**Test matrix:**

| Scenario | Wall Type | Distance Behind Wall | Expected Result | KPI |
|----------|-----------|---------------------|-----------------|-----|
| Single drywall | 12.5 mm gypsum | 1 m | Walking clear, breathing marginal | Walking detection rate > 90% |
| Single drywall | 12.5 mm gypsum | 3 m | Walking clear | Detection rate > 80% |
| Double drywall | 25 mm total | 1 m | Walking clear | Detection rate > 80% |
| Double drywall | 25 mm total | 3 m | Walking weak | Detection rate > 50% |
| Wood door | 40 mm solid | 1 m | Walking clear | Detection rate > 90% |
| Concrete block | 100 mm | 1 m | Walking marginal | Detection rate > 30% |
| Glass window | 6 mm | 3 m | Walking clear | Detection rate > 95% |

**Procedure:**
1. Place radar on one side of wall, antennas aimed perpendicular to wall
2. Person walks behind wall at specified distance
3. Record 30 seconds per test
4. Post-process: count detection events vs. actual motion events

**Metrics:**
- True positive rate (walking detected when person walks)
- False positive rate (alarm when no one is there)
- Detection latency (seconds from motion start to alarm)
- Maximum reliable range per wall type

**Environmental variables to record:**
- Wall material and thickness
- Presence of metal studs / rebar / foil insulation
- Furniture on either side
- Other RF sources (WiFi routers, microwaves)

---

### 3.2 Covert Room Surveillance
**Goal:** Detect occupancy without alerting occupants.

**Test scenario:**
```
Office / hotel room simulation
- Radar placed outside door or adjacent room
- One person enters, sits, works, leaves
- Two people enter, talk, leave
- Person enters, sleeps (breathing only)
```

**Metrics:**

| Event | Expected Detection | Confidence |
|-------|-------------------|------------|
| Person enters room | Walking spike | High |
| Person sits down | Brief spike then breathing | Medium |
| Person working at desk | Micro-motions (typing, shifting) | Low-Medium |
| Person sleeping | Breathing only | Medium |
| Second person enters | Multiple motion events | High |
| Both leave | Motion spike then silence | High |
| Empty room, HVAC on | False alarm risk | — |

**Procedure:**
1. Deploy radar outside target room (through wall or door)
2. Log continuous data for 1 hour
3. Ground truth: manual log of actual room events
4. Compare detected events to ground truth

**Key challenge:** HVAC, fans, and vibration can produce Doppler-like signals.
**Mitigation:**
- High-pass filter at 0.5 Hz (removes slow drift)
- Spectral analysis: HVAC is usually narrowband and constant
- Machine learning classifier on Doppler signatures

---

### 3.3 Perimeter Breach Detection
**Goal:** Detect motion crossing a boundary (doorway, corridor, window).

**Test scenario:**
```
Corridor or doorway
- Radar aimed across opening
- Person walks through beam
- Person crawls through beam (slow, low RCS)
- Animal-sized object (cat/dog) through beam
```

**Expected:**
- Crossing produces a characteristic Doppler "blip" — positive then negative (approaching then receding)
- Speed can be estimated from Doppler peak
- Direction determined by I/Q phase rotation

**Metrics:**
- Crossing detection rate
- Speed estimation accuracy (±20%?)
- Direction discrimination (approaching vs. receding)
- False alarm rate from ambient motion (curtains, plants)

---

### 3.4 Multiple Target Discrimination
**Goal:** Detect and count multiple people.

**Test:**
```
Room with 2-3 people
- All stationary (breathing)
- One walks while others stationary
- Two walk simultaneously
```

**Expected:**
- Breathing signatures may overlap (same frequency band)
- Walking signatures are distinct if people move at different speeds/directions
- I/Q processing can separate approaching vs receding

**Limitation:** CW Doppler has **no range resolution**. All targets superimposed in Doppler spectrum. Cannot count stationary people by breathing alone.

**Upgrade path:** Add FMCW capability for range resolution → count targets at different ranges.

---

### 3.5 Bistatic / Covert Mode (Phase 4)
**Goal:** Detect targets without emitting any RF.

**Test:**
```
Illuminator: Local FM radio tower or strong WiFi AP
Receiver: Red Pitaya with LNA + directional antenna aimed at surveillance area
Reference: Second antenna aimed at illuminator (or same antenna, null-steered)
```

**Procedure:**
1. Set up reference channel monitoring broadcast signal
2. Set up surveillance channel looking at area
3. Cross-correlate to find delayed/Doppler-shifted reflections
4. Person walks in surveillance area — look for peak in ambiguity function

**Metrics:**
- Target detection rate
- Maximum range (dependent on illuminator power and geometry)
- False alarm rate
- Covertness (can a receiver detect our operation? No — we're only receiving)

**Challenge:** Requires precise time/frequency synchronisation between reference and surveillance. GPSDO or common-clock distribution needed.

---

## Test Environment Setup

### Recommended Test Spaces

| Space | Size | Wall Type | Tests Supported |
|-------|------|-----------|-----------------|
| Garage / workshop | 6×4 m | Single drywall or brick | Stage 1–2, limited 3 |
| Living room | 5×4 m | Double drywall | Stage 2–3, through-wall |
| Office / hotel room | 4×3 m | Single drywall | Stage 3, covert surveillance |
| Corridor | 10×2 m | Open | Stage 3, perimeter |
| Outdoor garden | 10×10 m | None | Stage 2, max range |

### Test Fixture Ideas

**Antenna positioning jig:**
- Camera tripod with phone mount → clamp antennas
- Allows precise aiming and repeatability
- Mark angles on tripod head for consistent pointing

**Target simulator:**
- Computer fan with aluminium blade → controlled speed, known Doppler
- Servo-controlled swinging pendulum → predictable motion
- Rotating corner reflector → strong, consistent reflection

**Wall simulator:**
- 1.2×2.4 m drywall sheet on stand → portable, adjustable angle
- Stack 2 sheets for double-wall test
- Add metal foil layer for worst-case test

---

## Data Logging & Analysis Pipeline

### Raw Data Capture
```python
# Save I/Q samples + metadata to file
import h5py

with h5py.File('test_2026-04-23_throughwall_3m.h5', 'w') as f:
    f.create_dataset('iq', data=iq_samples, compression='gzip')
    f.attrs['test_type'] = 'through_wall'
    f.attrs['wall_material'] = 'drywall'
    f.attrs['wall_thickness_mm'] = 12.5
    f.attrs['target_distance_m'] = 3.0
    f.attrs['target_activity'] = 'walking'
    f.attrs['tx_power_dbm'] = 20
    f.attrs['carrier_hz'] = 2.4e9
    f.attrs['sample_rate_hz'] = 100e3
    f.attrs['timestamp'] = '2026-04-23T10:00:00Z'
```

### Automated Analysis Script
```python
# batch_analyse.py
# Loads HDF5 files, runs detection algorithms, produces report

results = {
    'true_positives': 0,
    'false_positives': 0,
    'false_negatives': 0,
    'latency_ms': [],
    'snr_db': []
}

for test_file in glob('test_*.h5'):
    iq = load_h5(test_file)
    detected_events = run_detector(iq, threshold=10)
    ground_truth = load_ground_truth(test_file)
    
    results['true_positives'] += count_matches(detected_events, ground_truth)
    results['false_positives'] += count_falses(detected_events, ground_truth)
    results['false_negatives'] += count_misses(detected_events, ground_truth)
```

### Report Template
```
Test Report: CW Doppler Radar
Date: _______  Operator: _______  Location: _______

Hardware Config:
  LO: ADF4351 @ ___ GHz, power ___ dBm
  TX: PA ___ , antenna ___ , pointing ___
  RX: LNA ___ , antenna ___ , pointing ___
  Baseband: gain ___ , HPF ___ Hz

Test Conditions:
  Environment: ___  Temperature: ___  Humidity: ___
  RF interference: WiFi ___ / Bluetooth ___ / Other ___

Results:
  [ ] Signal chain validated
  [ ] Antennas validated
  [ ] Hand motion detected (SNR: ___ dB)
  [ ] Breathing detected (SNR: ___ dB)
  [ ] Through-wall walking (distance: ___ m, rate: ___ %)
  [ ] Through-wall breathing (distance: ___ m, rate: ___ %)
  [ ] False alarm rate (___ per hour)

Notes:
  ___________________________________________
  ___________________________________________
```

---

## Decision Gates & Iteration

### Gate 1: Hardware Works (Stage 1 complete)
**Criteria:** All blocks validated individually and end-to-end.
**If fail:** Debug and replace faulty components.

### Gate 2: Motion Detected in LOS (Stage 2 complete)
**Criteria:** Hand motion and breathing detected at 1-3 m with SNR > 10 dB.
**If fail:**
- Add PA to TX (if not already)
- Increase LNA gain (check for oscillation)
- Improve antenna alignment
- Reduce HPF cutoff (if breathing not seen)

### Gate 3: Through-Wall Works (Stage 3 partial)
**Criteria:** Walking detected through single drywall at 3 m > 80% of time.
**If fail:**
- Add PA (if not already)
- Use directional antennas with higher gain
- Reduce range expectation
- Consider 433 MHz or lower frequency for better penetration

### Gate 4: Security-Ready (Stage 3 full)
**Criteria:**
- False alarm rate < 1 per hour in empty environment
- Detection latency < 5 seconds
- Multiple target capability (at least "one vs many")
- Portable deployment (< 5 minutes setup)
**If fail:**
- Add machine learning classifier
- Implement adaptive thresholding
- Upgrade to FMCW for range resolution
- Add second channel for diversity

---

## Upgrade Path

| Capability | Current (CW) | Upgrade (FMCW) | Upgrade (MIMO) |
|------------|-------------|----------------|----------------|
| Range info | No | Yes (1–10 m bins) | Yes + angle |
| Speed info | Yes (Doppler) | Yes (Doppler) | Yes |
| Target count | No (1D only) | Yes (by range) | Yes (by range + angle) |
| Through-wall | Moderate | Better (SNR integration) | Better |
| Hardware add | — | FPGA chirp generator | Second Red Pitaya |
| Cost add | — | £0 (software) | £250 |

---

## Summary: What You Can Prove with This Stack

**Week 1 (desk test):**
- ✅ CW Doppler signal chain works
- ✅ Hand motion detected at 1 m

**Week 2 (room test):**
- ✅ Breathing detected at 1-2 m
- ✅ Walking detected at 3-5 m LOS

**Week 3 (through-wall):**
- ✅ Walking through single drywall at 2-3 m
- ❌ Breathing through wall (marginal)

**Week 4 (security scenarios):**
- ✅ Room occupancy detection (motion-based)
- ⚠️ Breathing-only detection (needs quiet environment)
- ❌ Multiple target counting (needs FMCW upgrade)

**Month 2-3 (advanced):**
- FMCW upgrade → range resolution + target counting
- Bistatic mode → covert surveillance
- ML classifier → reduce false alarms
