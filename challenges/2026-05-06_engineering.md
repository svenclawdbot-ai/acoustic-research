# Engineering Challenge — May 6, 2026
## TurboQuant V5: Transmit/Receive Switching Characterisation

### Context
You just committed the investor pitch deck for TurboQuant. Now it's time to validate one of the most critical subsystems before prototype ordering: the **T/R (Transmit/Receive) switching network**.

The T/R diode bridge (MUR120 ×4 per channel) is what protects the DG408 analog MUX and OPA1641 LNA from the ±100V transmit pulse. If this doesn't work, the receive chain gets destroyed on the first pulse.

### Challenge

**Part 1: Isolation Analysis (30 min)**
- Calculate T/R isolation during TX mode:
  - MUR120 reverse recovery time: ~2 µs
  - TX pulse width: 0.5 µs (2 cycles @ 3.5 MHz)
  - TX voltage: 100V
  - Leakage through reverse-biased diodes to LNA input
- Determine if the 10:1 attenuator + BAV99 clamping is sufficient protection

**Part 2: Insertion Loss Budget (30 min)**
- Calculate two-way insertion loss through the T/R bridge in RX mode:
  - MUR120 forward voltage drop: ~0.8V @ 10mA echo current
  - 4 diodes in series (2 per arm)
  - Compare to target: <10 dB total loss acceptable

**Part 3: Timing Diagram (30 min)**
- Sketch the TX/RX timing sequence for a single channel:
  1. T/R bias switches to TX mode (D1 forward, D2 reverse)
  2. HV pulse fires (0.5 µs)
  3. Dead time (diode recovery)
  4. T/R bias switches to RX mode (D1 reverse, D2 forward)
  5. Echo acquisition window opens
- Calculate minimum PRF (pulse repetition frequency) limited by diode recovery

### Deliverables
1. Isolation calculation with margin analysis
2. Insertion loss budget table
3. Timing diagram (ASCII or drawn)
4. Go/No-Go decision: Is the MUR120-based T/R bridge adequate, or do we need PIN diodes?

### Success Criteria
- >26 dB TX-to-RX isolation (stated in design docs)
- <10 dB insertion loss in RX path
- PRF ≥ 1 kHz for real-time imaging

### References
- V5_DESIGN_VERIFICATION.md (T/R section)
- turboquant_v5/hardware/SYSTEM_BLOCK_DIAGRAM.md
- MUR120 datasheet: 200V, 1A, reverse recovery ~2 µs

---
*Time estimate: 90 minutes*
*Focus: Validate the most critical protection circuit before £2,500 prototype spend*
