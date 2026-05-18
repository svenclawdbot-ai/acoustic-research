// soil_spectrometer_esp32s3.ino
// Single-board soil impedance spectrometer on ESP32-S3
// AD9833 DDS sweep + software lock-in amplifier + impedance calculation

#include <SPI.h>

// === AD9833 DDS Pinout ===
#define AD9833_FSYNC  10   // GPIO 10 (chip select)
#define SPI_SCK       12   // GPIO 12 (SCK)
#define SPI_MOSI      11   // GPIO 11 (MOSI)

// AD9833 register control bits
#define AD9833_B28      0x2000  // 28-bit freq load in two writes
#define AD9833_HLB      0x1000  // high/low byte select
#define AD9833_FSELECT  0x0800  // freq register select
#define AD9833_PSELECT  0x0400  // phase register select
#define AD9833_RESET    0x0100  // reset internal registers
#define AD9833_SLEEP1   0x0080  // DAC power down
#define AD9833_SLEEP12  0x0040  // internal clock disable
#define AD9833_OPBITEN  0x0020  // digital output enable
#define AD9833_DIV2     0x0008  // digital divide by 2
#define AD9833_MODE     0x0002  // triangle wave select

// AD9833 register addresses
#define AD9833_FREQ0    0x4000
#define AD9833_FREQ1    0x8000
#define AD9833_PHASE0   0xC000
#define AD9833_PHASE1   0xE000

// === Measurement Configuration ===
const float  MCLK_HZ          = 25000000.0;   // AD9833 onboard crystal
const float  EXCITATION_V     = 0.5;          // Vpp from AD9833 into soil (nominal)
const float  TIA_GAIN_OHMS     = 1000.0;       // 1 kΩ feedback = 1 V / 1 mA
const int    ADC_PIN           = 1;            // GPIO 1 = ADC1_CH0 on ESP32-S3
const int    ADC_RESOLUTION    = 12;           // 0-4095
const float  ADC_VREF          = 3.3;          // ESP32-S3 reference

// === Sweep Parameters ===
const int    NUM_FREQ_POINTS   = 50;
const float  FREQ_START_HZ     = 1000.0;       // 1 kHz
const float  FREQ_STOP_HZ      = 500000.0;     // 500 kHz (ESP32-S3 ADC practical limit)
const int    SAMPLES_PER_CYCLE = 8;            // coherent sampling
const int    CYCLES_TO_AVERAGE = 50;           // boxcar LPF length

float freqs_Hz[NUM_FREQ_POINTS];
float Z_mag[NUM_FREQ_POINTS];
float Z_phase[NUM_FREQ_POINTS];

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n=================================");
  Serial.println("Soil Spectrometer v0.2 — ESP32-S3");
  Serial.println("Single-board: DDS + ADC + Lock-in");
  Serial.println("=================================");

  // Init ADC
  analogReadResolution(ADC_RESOLUTION);
  analogSetAttenuation(ADC_11db);   // 0-3.3 V full scale
  pinMode(ADC_PIN, INPUT);

  // Init SPI for AD9833
  SPI.begin(SPI_SCK, -1, SPI_MOSI, AD9833_FSYNC);  // No MISO needed
  pinMode(AD9833_FSYNC, OUTPUT);
  digitalWrite(AD9833_FSYNC, HIGH);

  // Reset DDS
  ad9833_write(AD9833_RESET);
  delay(10);
  ad9833_write(0x0000);  // clear reset, no output yet

  // Build frequency log-spaced array
  float log_step = (log10(FREQ_STOP_HZ) - log10(FREQ_START_HZ)) / (NUM_FREQ_POINTS - 1);
  for (int i = 0; i < NUM_FREQ_POINTS; i++) {
    freqs_Hz[i] = pow(10.0, log10(FREQ_START_HZ) + i * log_step);
  }

  Serial.println("\nFreq (Hz)\t|Z| (Ω)\tPhase (deg)");
  Serial.println("-----------------------------------");
}

void loop() {
  // Run one complete sweep
  for (int i = 0; i < NUM_FREQ_POINTS; i++) {
    float f = freqs_Hz[i];

    // Set DDS frequency
    set_ad9833_frequency(f, 0);
    delay(5);  // settle DDS + analog front-end

    // Lock-in measurement
    float I, Q;
    measure_lockin(f, &I, &Q);

    // Convert I/Q to impedance
    float v_tia = 2.0 * sqrt(I*I + Q*Q);           // measured TIA output voltage (Vpp)
    float i_soil = v_tia / TIA_GAIN_OHMS;           // current through soil
    float z_mag_val = EXCITATION_V / i_soil;        // |Z| = V_exc / I_soil

    // Phase: measured phase at TIA output (inverted by op-amp)
    float z_phase_val = atan2(Q, I) * 180.0 / PI;

    // Store
    Z_mag[i]   = z_mag_val;
    Z_phase[i] = z_phase_val;

    // Print CSV row
    Serial.printf("%.1f\t%.3f\t%.2f\n", f, z_mag_val, z_phase_val);

    delay(10);
  }

  // End of sweep marker
  Serial.println("\n--- SWEEP COMPLETE ---");
  Serial.println("Copy CSV above into Python for Cole-Cole fitting.");
  Serial.println("Next sweep in 10 seconds...\n");
  delay(10000);
}

// === AD9833 SPI Helpers ===

void ad9833_write(uint16_t data) {
  digitalWrite(AD9833_FSYNC, LOW);
  SPI.beginTransaction(SPISettings(10000000, MSBFIRST, SPI_MODE2));
  SPI.transfer((uint8_t)(data >> 8));
  SPI.transfer((uint8_t)(data & 0xFF));
  SPI.endTransaction();
  digitalWrite(AD9833_FSYNC, HIGH);
}

void set_ad9833_frequency(float freq, uint8_t freqReg) {
  // freq_word = freq * 2^28 / MCLK
  uint32_t freqWord = (uint32_t)((freq * 268435456.0) / MCLK_HZ);

  uint16_t reg = (freqReg == 0) ? AD9833_FREQ0 : AD9833_FREQ1;

  uint16_t lsb = (freqWord & 0x3FFF) | reg;
  uint16_t msb = ((freqWord >> 14) & 0x3FFF) | reg;

  // Enter reset, enable B28 mode, write both halves, exit reset
  ad9833_write(AD9833_B28 | AD9833_RESET);
  ad9833_write(lsb);
  ad9833_write(msb);
  ad9833_write(AD9833_B28);  // sine output, exit reset
}

// === Lock-in Amplifier (Software) ===

void measure_lockin(float freq_hz, float* I_out, float* Q_out) {
  // Coherent sampling: capture N samples per cycle, locked to software reference
  int samples_per_cycle = SAMPLES_PER_CYCLE;
  int total_samples     = samples_per_cycle * CYCLES_TO_AVERAGE;
  float sample_period_us = 1000000.0 / (freq_hz * samples_per_cycle);

  float sum_I = 0.0;
  float sum_Q = 0.0;
  float dc_sum = 0.0;

  unsigned long t0 = micros();

  for (int n = 0; n < total_samples; n++) {
    // Wait for exact sample time
    unsigned long target_us = t0 + (unsigned long)(n * sample_period_us);
    while (micros() < target_us) { /* busy-wait for timing */ }

    // Read ADC (raw 0-4095)
    int raw = analogRead(ADC_PIN);
    float voltage = (raw * ADC_VREF) / ((1 << ADC_RESOLUTION) - 1);

    // Software reference phase at this instant
    float t_now = (float)(micros() - t0) / 1000000.0;
    float phase = 2.0 * PI * freq_hz * t_now;

    // Quadrature mixing
    sum_I += voltage * cos(phase);
    sum_Q += voltage * sin(phase);
    dc_sum += voltage;
  }

  // Remove DC bias from I/Q (critical for accuracy)
  float dc_offset = dc_sum / total_samples;
  sum_I -= dc_offset * total_samples * 0.0;  // cos averages to ~0 over full cycles
  sum_Q -= dc_offset * total_samples * 0.0;  // sin averages to ~0 over full cycles

  // Boxcar average (LPF)
  *I_out = sum_I / total_samples;
  *Q_out = sum_Q / total_samples;
}
