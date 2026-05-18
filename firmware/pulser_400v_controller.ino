// =============================================================================
// External 400V Pulser Controller — TurboQuant NDE Module
// Arduino Nano / Pro Mini (5V, 16 MHz)
// Interfaces: Serial (USB), Trigger input (BNC or DIO), HV monitor (ADC)
// =============================================================================

#include <SoftwareSerial.h>

// ─────────────────────────────────────────────────────────────────────────────
// PIN DEFINITIONS
// ─────────────────────────────────────────────────────────────────────────────
#define PIN_TRIGGER_OUT     9   // PWM-capable pin to TC4427 gate driver
#define PIN_STATUS_LED      13  // Built-in LED
#define PIN_HV_MONITOR      A0  // HV rail voltage (via 1000:1 divider)
#define PIN_POT_VOLTAGE     A1  // Optional: analog pot for voltage adjustment
#define PIN_MODE_SWITCH     2   // Optional: toggle Medical/NDE mode (interrupt)

// ─────────────────────────────────────────────────────────────────────────────
// DEFAULT PARAMETERS
// ─────────────────────────────────────────────────────────────────────────────
struct PulseParams {
    uint16_t pulseWidth_us = 100;      // 50–1000 µs
    uint16_t prf_hz = 100;             // 1–1000 Hz
    uint8_t  burstCycles = 5;          // 1–50 pulses per burst
    uint16_t hv_setpoint = 200;        // 50–400V target (if digital pot fitted)
    bool     externalMode = true;      // true = use this pulser, false = bypass
};

PulseParams params;

// ─────────────────────────────────────────────────────────────────────────────
// STATE
// ─────────────────────────────────────────────────────────────────────────────
volatile bool running = false;
volatile bool fireSingle = false;
uint32_t pulseCount = 0;
unsigned long lastReportMs = 0;

// ─────────────────────────────────────────────────────────────────────────────
// SETUP
// ─────────────────────────────────────────────────────────────────────────────
void setup() {
    Serial.begin(115200);
    while (!Serial && millis() < 3000);  // Wait for Serial or timeout
    delay(500);

    pinMode(PIN_TRIGGER_OUT, OUTPUT);
    pinMode(PIN_STATUS_LED, OUTPUT);
    pinMode(PIN_MODE_SWITCH, INPUT_PULLUP);

    digitalWrite(PIN_TRIGGER_OUT, LOW);
    digitalWrite(PIN_STATUS_LED, LOW);

    // Attach mode switch interrupt
    attachInterrupt(digitalPinToInterrupt(PIN_MODE_SWITCH), onModeSwitch, CHANGE);

    printBanner();
    printHelp();
}

// ─────────────────────────────────────────────────────────────────────────────
// MAIN LOOP
// ─────────────────────────────────────────────────────────────────────────────
void loop() {
    handleSerialCommands();

    if (fireSingle) {
        fireSingle = false;
        fireBurst();
        Serial.println("[OK] Single burst fired");
    }

    if (running) {
        fireBurst();
        pulseCount += params.burstCycles;

        // PRF delay
        unsigned long period_ms = 1000UL / params.prf_hz;
        unsigned long elapsed = millis() - lastReportMs;

        // Report every ~2 seconds
        if (elapsed >= 2000) {
            reportStatus();
            lastReportMs = millis();
        }

        // Non-blocking delay approximation
        unsigned long delayNeeded = period_ms;
        if (delayNeeded > 50) delayNeeded = 50;  // Check serial frequently
        delay(delayNeeded);
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// PULSE GENERATION
// ─────────────────────────────────────────────────────────────────────────────
void firePulse() {
    digitalWrite(PIN_TRIGGER_OUT, HIGH);
    delayMicroseconds(params.pulseWidth_us);
    digitalWrite(PIN_TRIGGER_OUT, LOW);
}

void fireBurst() {
    digitalWrite(PIN_STATUS_LED, HIGH);
    for (uint8_t i = 0; i < params.burstCycles; i++) {
        firePulse();
        // Short inter-pulse delay (10 µs) for burst coherence
        delayMicroseconds(10);
    }
    digitalWrite(PIN_STATUS_LED, LOW);
}

// ─────────────────────────────────────────────────────────────────────────────
// HV MONITOR
// ─────────────────────────────────────────────────────────────────────────────
float readHVVoltage() {
    // ADC: 10-bit, 5V reference = 5V/1024 = 4.88 mV per count
    // Divider: 10MΩ + 10kΩ = 1000:1 ratio
    // So: ADC_voltage = HV / 1000
    // HV = ADC_reading × 4.88 mV × 1000 = ADC_reading × 4.88 V
    int raw = analogRead(PIN_HV_MONITOR);
    float hv = raw * 4.88;  // volts
    return hv;
}

// ─────────────────────────────────────────────────────────────────────────────
// SERIAL COMMANDS
// ─────────────────────────────────────────────────────────────────────────────
void handleSerialCommands() {
    if (!Serial.available()) return;

    char cmd = Serial.read();
    int value = Serial.parseInt();

    switch (cmd) {
        case 'p':  // Pulse width
            params.pulseWidth_us = constrain(value, 10, 1000);
            Serial.print("[SET] Pulse width = ");
            Serial.print(params.pulseWidth_us);
            Serial.println(" µs");
            break;

        case 'f':  // PRF
            params.prf_hz = constrain(value, 1, 1000);
            Serial.print("[SET] PRF = ");
            Serial.print(params.prf_hz);
            Serial.println(" Hz");
            break;

        case 'b':  // Burst cycles
            params.burstCycles = constrain(value, 1, 50);
            Serial.print("[SET] Burst cycles = ");
            Serial.println(params.burstCycles);
            break;

        case 'v':  // HV setpoint (if digital pot fitted)
            params.hv_setpoint = constrain(value, 50, 400);
            Serial.print("[SET] HV target = ");
            Serial.print(params.hv_setpoint);
            Serial.println(" V");
            // TODO: Adjust digital potentiometer via I2C/SPI
            break;

        case 's':  // Single burst
            fireSingle = true;
            break;

        case 'r':  // Run continuous
            if (!running) {
                running = true;
                pulseCount = 0;
                lastReportMs = millis();
                Serial.println("[RUN] Continuous mode started (send 'x' to stop)");
            }
            break;

        case 'x':  // Stop
            if (running) {
                running = false;
                Serial.println("[STOP] Continuous mode stopped");
                reportStatus();
            }
            break;

        case 'h':  // Read HV
            reportHV();
            break;

        case 'm':  // Mode
            params.externalMode = !params.externalMode;
            Serial.print("[SET] Mode = ");
            Serial.println(params.externalMode ? "EXTERNAL PULSER (NDE)" : "BYPASS (V5 internal)");
            break;

        case 'i':  // Info / status
            reportStatus();
            break;

        case '?':  // Help
        case 'H':
            printHelp();
            break;

        default:
            // Ignore unknown characters (likely whitespace)
            break;
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// REPORTING
// ─────────────────────────────────────────────────────────────────────────────
void reportHV() {
    float hv = readHVVoltage();
    Serial.print("[HV] Rail voltage = ");
    Serial.print(hv, 1);
    Serial.println(" V");

    // Safety warning
    if (hv > 50) {
        Serial.println("[WARN] HV capacitor charged — discharge before handling!");
    }
}

void reportStatus() {
    Serial.println("\n─── STATUS ───");
    Serial.print("  Mode:       ");
    Serial.println(params.externalMode ? "External pulser (NDE)" : "Bypass (V5 internal)");
    Serial.print("  Pulse:      ");
    Serial.print(params.pulseWidth_us);
    Serial.println(" µs");
    Serial.print("  PRF:        ");
    Serial.print(params.prf_hz);
    Serial.println(" Hz");
    Serial.print("  Burst:      ");
    Serial.print(params.burstCycles);
    Serial.println(" cycles");
    Serial.print("  HV target:  ");
    Serial.print(params.hv_setpoint);
    Serial.println(" V");
    Serial.print("  HV actual:  ");
    Serial.print(readHVVoltage(), 1);
    Serial.println(" V");
    Serial.print("  Pulses:     ");
    Serial.println(pulseCount);
    Serial.print("  Running:    ");
    Serial.println(running ? "YES" : "NO");
    Serial.println("───────────────\n");
}

// ─────────────────────────────────────────────────────────────────────────────
// INTERRUPT HANDLER
// ─────────────────────────────────────────────────────────────────────────────
void onModeSwitch() {
    // Debounce in software if needed
    static unsigned long lastInterrupt = 0;
    unsigned long now = millis();
    if (now - lastInterrupt < 200) return;
    lastInterrupt = now;

    params.externalMode = digitalRead(PIN_MODE_SWITCH) == LOW;
    // In real hardware, this would also switch a relay to route TX_IN
}

// ─────────────────────────────────────────────────────────────────────────────
// UI
// ─────────────────────────────────────────────────────────────────────────────
void printBanner() {
    Serial.println("\n╔═══════════════════════════════════════╗");
    Serial.println("║   TurboQuant NDE — 400V Pulser      ║");
    Serial.println("║   External HV Module Controller       ║");
    Serial.println("╚═══════════════════════════════════════╝");
    Serial.println("Version: 0.1 | 2026-05-07\n");
}

void printHelp() {
    Serial.println("Serial Commands (115200 baud):");
    Serial.println("  pXXX  → Pulse width in µs     (p100 = 100 µs)");
    Serial.println("  fXXX  → PRF in Hz             (f100 = 100 Hz)");
    Serial.println("  bXXX  → Burst cycles          (b10 = 10 pulses)");
    Serial.println("  vXXX  → HV target in V        (v200 = 200V)");
    Serial.println("  s     → Fire single burst");
    Serial.println("  r     → Run continuous");
    Serial.println("  x     → Stop");
    Serial.println("  h     → Read HV rail voltage");
    Serial.println("  m     → Toggle external/bypass mode");
    Serial.println("  i     → Full status report");
    Serial.println("  ?/H   → This help\n");
    Serial.println("Safety: 'h' to check HV before handling. Wait for LED off.\n");
}

// =============================================================================
// END OF SKETCH
// =============================================================================
