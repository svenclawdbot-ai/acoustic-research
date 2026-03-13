# DIY High-Voltage Ultrasound Pulser
## Complete Build Guide for Shear Wave Elastography

**Date:** March 13, 2026  
**Cost:** ~£40-50  
**Build Time:** 2-4 hours  
**Skill Level:** Intermediate (soldering required)

---

## CIRCUIT OVERVIEW

```
Raspberry Pi/Arduino → Gate Driver → MOSFET → Pulse Transformer → Transducer
                                              ↑
                                       HV Supply (100-200V)
```

**Key Components:**
- **Gate Driver:** TC4427 (fast switching)
- **MOSFET:** IRF830 (200V, 4.5A)
- **Pulse Transformer:** Custom wound or CTX01-14611
- **HV Supply:** DC-DC boost module 100-200V

---

## COMPONENT LIST

### Active Components

| Component | Specs | Supplier | Part Number | Cost |
|-----------|-------|----------|-------------|------|
| **Gate Driver IC** | Dual, 1.5A output | RS Components | TC4427CPA | £2.50 |
| **MOSFET** | 200V, N-channel | RS Components | IRF830PBF | £3.20 |
| **HV DC-DC Module** | 12V → 100-200V | Amazon / AliExpress | "High Voltage DC-DC Boost" | £15 |
| **Arduino Nano** | ATmega328P | Amazon | Clone | £8 |
| **Voltage Regulator** | 5V, 1A | RS Components | LM7805 | £0.80 |
| **Optocoupler** | PC817 (isolation) | RS Components | PC817 | £0.50 |

### Passive Components

| Component | Value | Qty | Supplier | Cost |
|-----------|-------|-----|----------|------|
| **Pulse Transformer** | 1:1 or 1:2 ratio | 1 | Coilcraft / DIY | £10 |
| **Resistor 10Ω** | 1/4W | 2 | RS Components | £0.20 |
| **Resistor 1kΩ** | 1/4W | 4 | RS Components | £0.20 |
| **Resistor 10kΩ** | 1/4W | 2 | RS Components | £0.10 |
| **Capacitor 100nF** | Ceramic, 50V | 4 | RS Components | £0.40 |
| **Capacitor 10µF** | Electrolytic, 250V | 2 | RS Components | £1.00 |
| **Capacitor 100µF** | Electrolytic, 25V | 2 | RS Components | £0.60 |
| **Diode 1N4007** | 1kV | 2 | RS Components | £0.30 |
| **LED** | 3mm, any color | 2 | RS Components | £0.30 |

### Hardware

| Item | Qty | Supplier | Cost |
|------|-----|----------|------|
| **Prototyping PCB** | 1 | Amazon | £3 |
| **BNC Connector** | 2 | Amazon | £3 |
| **Pin Headers** | 1 set | Amazon | £2 |
| **Jumper Wires** | 1 set | Amazon | £3 |
| **Enclosure** | 1 | Amazon | £5 |
| **Heat Sink (small)** | 1 | Amazon | £2 |
| **TOTAL** | | | **~£48** |

---

## CIRCUIT SCHEMATIC

```
                              +12V
                               |
                              [10µF]
                               |
    +--------------------+     |     +--------------------+
    |   HV DC-DC Boost   |-----+     |   Pulse Circuit    |
    |   (100-200V out)   |           |                    |
    +--------------------+           |  +---------------+ |
            |                        |  |  Pulse Xfmr   | |
           [100µF]                   |  |   Primary    | |
            |                        |  |     ||       | |
           +++ 200V                 +++ |     ||       | |
           | |                       | | |  +--||--+    | |
           | |                       | | |  |      |    | |
           +++                       | | | [10µF] [D1]  | |
            |                        | | |  |      |    | |
            +------------------------+ | |  +--+---+    | |
                                       | |     |        | |
                                       | |   [IRF830]   | |
                                       | |     |        | |
                                       | |    S D G     | |
                                       | |     | | |    | |
                                       | |     | | +----+ |
                                       | |     | |   |    |
                                       | |    +++  [10Ω]  |
                                       | |    | |   |    |
                                       | |   GND  |   |   |
                                       | |          |   |
                                       | +----------+   |
                                       |      |         |
                                       |  +---+----+    |
                                       |  | TC4427 |    |
                                       |  |  OUT A |----+---> To Arduino
                                       |  +--------+    |
                                       |       |        |
                                       |      GND       |
                                       +----------------+
                                               |
                                          +----+----+
                                          |   BNC   |-----> Transducer
                                          +---------+
```

---

## PULSE TRANSFORMER OPTIONS

### Option 1: Buy Pre-made (Easiest)
**Part:** Coilcraft CTX01-14611 or similar  
**Specs:** 1:1 turns ratio, 20µH primary, >200V rating  
**Cost:** £10-15  
**Source:** Coilcraft, Digi-Key, Mouser

### Option 2: Wind Your Own (Cheapest)
**Materials:**
- Ferrite toroid: T50-2 or T68-2 (red/yellow paint)
- Magnet wire: 28 AWG, ~2m length
- Cost: £2-3

**Winding:**
1. Wind 10 turns primary (center-tapped = 2×5 turns)
2. Wind 10 turns secondary over primary
3. Use 28 AWG magnet wire
4. Keep windings tight and even

**Test:** Should measure ~20-50µH on primary

---

## ASSEMBLY INSTRUCTIONS

### Step 1: Power Supply Section

1. **Mount HV DC-DC module** on PCB
2. **Connect input:** +12V and GND
3. **Connect output:** Through 100µF capacitor to pulse circuit
4. **Add LED indicator:** With 1kΩ resistor on +12V line

### Step 2: Gate Driver Section

1. **Mount TC4427** on PCB
   - Pin 1: VDD (+5V)
   - Pin 2: Input A (from Arduino)
   - Pin 3: GND
   - Pin 4: Input B (grounded)
   - Pin 5: Output B (not used)
   - Pin 6: VDD (+5V)
   - Pin 7: Output A → MOSFET gate
   - Pin 8: VDD (+5V)

2. **Add decoupling capacitors:**
   - 100nF ceramic across VDD and GND (as close to IC as possible)

### Step 3: MOSFET Section

1. **Mount IRF830** with heat sink
   - Pin 1 (Gate): From TC4427 output through 10Ω resistor
   - Pin 2 (Drain): To pulse transformer primary
   - Pin 3 (Source): To GND

2. **Add gate protection:**
   - 10Ω resistor in series with gate
   - Optional: 12V Zener diode gate-to-source

### Step 4: Pulse Transformer Section

1. **Mount transformer:**
   - Primary: One side to +200V, other side to MOSFET drain
   - Secondary: To BNC connector (transducer output)

2. **Add damping network:**
   - 10µF capacitor across primary (HV side)
   - 1N4007 diode in parallel with primary (reverse biased)

### Step 5: Output Section

1. **Mount BNC connector:**
   - Center pin: Transformer secondary
   - Shield: GND

2. **Add protection:**
   - 1N4007 diode from center pin to GND (protects against transducer ringing)

### Step 6: Control Interface

1. **Connect Arduino:**
   - Digital pin 9 (PWM) → TC4427 input A
   - GND → Common ground

2. **Add optocoupler (optional but recommended):**
   - Isolates Arduino from high-voltage section
   - PC817: Arduino pin → LED side, transistor side → TC4427 input

---

## ARDUINO CODE

```cpp
/*
 * Ultrasound Pulser Controller
 * For shear wave elastography
 * 
 * Hardware: Arduino Nano + TC4427 + IRF830 + HV supply
 */

const int PULSE_PIN = 9;        // Output to gate driver
const int LED_PIN = 13;         // Status LED

// Pulse parameters
int pulseWidth_us = 100;        // 100 microseconds (adjust 50-500)
int prf_hz = 100;               // Pulse repetition frequency
int burstCycles = 5;            // Cycles for ARFI push

void setup() {
  pinMode(PULSE_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(PULSE_PIN, LOW);
  
  Serial.begin(115200);
  Serial.println("Ultrasound Pulser Ready");
  Serial.println("Commands:");
  Serial.println("  pXXX - Set pulse width (us)");
  Serial.println("  fXXX - Set PRF (Hz)");
  Serial.println("  bXXX - Set burst cycles");
  Serial.println("  s - Single pulse");
  Serial.println("  r - Run continuous");
  Serial.println("  x - Stop");
}

void loop() {
  if (Serial.available()) {
    char cmd = Serial.read();
    int value = Serial.parseInt();
    
    switch(cmd) {
      case 'p':
        pulseWidth_us = constrain(value, 10, 1000);
        Serial.print("Pulse width: ");
        Serial.print(pulseWidth_us);
        Serial.println(" us");
        break;
        
      case 'f':
        prf_hz = constrain(value, 1, 1000);
        Serial.print("PRF: ");
        Serial.print(prf_hz);
        Serial.println(" Hz");
        break;
        
      case 'b':
        burstCycles = constrain(value, 1, 50);
        Serial.print("Burst cycles: ");
        Serial.println(burstCycles);
        break;
        
      case 's':
        fireBurst();
        Serial.println("Single burst fired");
        break;
        
      case 'r':
        Serial.println("Running... (send 'x' to stop)");
        runContinuous();
        break;
        
      case 'x':
        Serial.println("Stopped");
        break;
    }
  }
}

void firePulse() {
  digitalWrite(PULSE_PIN, HIGH);
  delayMicroseconds(pulseWidth_us);
  digitalWrite(PULSE_PIN, LOW);
}

void fireBurst() {
  digitalWrite(LED_PIN, HIGH);
  for(int i = 0; i < burstCycles; i++) {
    firePulse();
    delayMicroseconds(10);  // Short delay between pulses
  }
  digitalWrite(LED_PIN, LOW);
}

void runContinuous() {
  unsigned long period_ms = 1000 / prf_hz;
  
  while(!Serial.available() || Serial.peek() != 'x') {
    fireBurst();
    delay(period_ms - 1);  // Approximate timing
  }
  Serial.read();  // Consume 'x'
}
```

---

## TESTING PROCEDURE

### Step 1: Power-On Test (NO HV)

1. Connect only +5V to Arduino and gate driver
2. Upload code
3. Open Serial Monitor (115200 baud)
4. Type `s` and verify:
   - Status LED flashes
   - TC4427 output toggles (use scope or DMM)

### Step 2: Low-Voltage Test (NO TRANSDUCER)

1. Connect +12V to HV module input
2. HV module output should read 100-200V (DMM)
3. Verify MOSFET gate drive signal (scope)
4. Should see ~5V pulses at gate

### Step 3: First Pulse Test

1. Connect oscilloscope to BNC output (1MΩ input)
2. Type `p100` (100 µs pulse)
3. Type `b1` (single pulse)
4. Type `s` to fire
5. Should see ~100-200V pulse on scope

### Step 4: With Transducer

1. Connect transducer to BNC
2. Place transducer in water bath
3. Fire pulse
4. Look for echo on scope (should see transmitted pulse + reflections)

---

## TROUBLESHOOTING

| Symptom | Cause | Solution |
|---------|-------|----------|
| **No output** | MOSFET not switching | Check gate drive signal |
| **Weak pulse (<50V)** | HV supply low | Adjust DC-DC potentiometer |
| **Pulse ringing** | No damping | Add capacitor across transformer |
| **MOSFET gets hot** | Too much current | Check transformer ratio |
| **Intermittent firing** | Ground loops | Use star grounding |
| **Arduino resets** | HV interference | Add optocoupler isolation |

---

## PERFORMANCE SPECIFICATIONS

| Parameter | Target | Achievable |
|-----------|--------|------------|
| **Pulse voltage** | 100-200V | 50-250V (adjustable) |
| **Pulse width** | 50-500 µs | 10-1000 µs |
| **Rise time** | <100 ns | ~50-100 ns |
| **PRF** | 1-1000 Hz | Up to 10 kHz (burst) |
| **Burst cycles** | 1-50 | Unlimited |

---

## ARFI PUSH CONFIGURATION

For shear wave elastography, configure:

```
p500      // 500 µs pulse (longer = more push)
b10       // 10 cycles in burst
f100      // 100 Hz PRF
r         // Run
```

This creates acoustic radiation force impulse (ARFI) suitable for generating shear waves in tissue phantoms.

---

## SAFETY WARNINGS

⚠️ **HIGH VOLTAGE PRESENT (100-200V)**
- Always discharge capacitors before handling
- Use insulated tools
- Keep one hand behind your back when probing
- Never connect/disconnect transducer while powered

⚠️ **TRANSDUCER DAMAGE RISK**
- Start with low voltage (50V)
- Gradually increase while monitoring
- Excessive voltage will crack crystal

⚠️ **ELECTRICAL ISOLATION**
- Keep HV section physically separated from logic
- Use optocouplers for control signals
- Double-check wiring before power-on

---

## ALTERNATIVE: SIMPLER DESIGN

If full ARFI capability not needed, use this simpler circuit for receive-only:

```
Transducer → LNA (AD8099) → Buffer → ADC
```

**LNA Circuit:**
- AD8099 op-amp (low noise, high speed)
- Gain: 20-40 dB
- Bandwidth: 1-10 MHz
- Cost: ~£10

Use external mechanical shaker for shear wave generation instead of ARFI.

---

## REFERENCES

1. **"A Pulse Generator Based on an Arduino Platform"**  
   Physics Procedia 70 (2015): 1096-1099

2. **TC4427 Datasheet** — Microchip  
   http://ww1.microchip.com/downloads/en/DeviceDoc/20001420G.pdf

3. **IRF830 Datasheet** — Vishay  
   https://www.vishay.com/docs/91038/irf830.pdf

4. **echomods Documentation** — kelu124  
   https://kelu124.gitbooks.io/echomods/

---

*Document created: March 13, 2026*  
*Build at your own risk — high voltage present*
