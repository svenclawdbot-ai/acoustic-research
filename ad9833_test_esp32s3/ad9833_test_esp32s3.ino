// AD9833 DDS Test for ESP32-S3
// Generates 1 kHz sine wave

#include <SPI.h>

#define AD9833_FSYNC  10  // GPIO 10
#define SPI_SCK       12  // GPIO 12 (SCK)
#define SPI_MOSI      11  // GPIO 11 (MOSI)

// AD9833 register bits
#define AD9833_B28      0x2000  // Allows a complete word to be loaded into a frequency register in two consecutive writes
#define AD9833_HLB      0x1000  // Control which 14 bits of the frequency word are loaded
#define AD9833_FSELECT  0x0800  // Select frequency register
#define AD9833_PSELECT  0x0400  // Select phase register
#define AD9833_RESET    0x0100  // Reset internal registers to 0
#define AD9833_SLEEP1   0x0080  // DAC powered down
#define AD9833_SLEEP12  0x0040  // Internal clock disabled
#define AD9833_OPBITEN  0x0020  // Enable digital output
#define AD9833_DIV2     0x0008  // Enable digital divide by 2
#define AD9833_MODE     0x0002  // Select triangle wave output

// Frequency register addresses
#define AD9833_FREQ0    0x4000
#define AD9833_FREQ1    0x8000
#define AD9833_PHASE0   0xC000
#define AD9833_PHASE1   0xE000

// MCLK frequency of AD9833 module (typically 25 MHz)
const float MCLK = 25000000.0;

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("AD9833 Test - ESP32-S3");
  
  // Initialize SPI
  SPI.begin(SPI_SCK, -1, SPI_MOSI, AD9833_FSYNC);  // SCK, MISO (not used), MOSI, SS
  pinMode(AD9833_FSYNC, OUTPUT);
  digitalWrite(AD9833_FSYNC, HIGH);
  
  // Reset AD9833
  ad9833_write(AD9833_RESET);
  delay(10);
  
  // Set frequency: 1 kHz
  setFrequency(1000.0, 0);
  
  // Enable sine output, exit reset
  ad9833_write(AD9833_B28);  // Enable B28 mode for complete word loading
  
  Serial.println("1 kHz sine wave active on AD9833 OUT");
  Serial.println("Check with multimeter AC mode - expect ~0.5V");
}

void loop() {
  // Just keep running
  delay(1000);
}

void ad9833_write(uint16_t data) {
  digitalWrite(AD9833_FSYNC, LOW);
  SPI.beginTransaction(SPISettings(10000000, MSBFIRST, SPI_MODE2));
  
  // AD9833 expects 16-bit transfers
  SPI.transfer((uint8_t)(data >> 8));
  SPI.transfer((uint8_t)(data & 0xFF));
  
  SPI.endTransaction();
  digitalWrite(AD9833_FSYNC, HIGH);
}

void setFrequency(float freq, uint8_t freqReg) {
  // Calculate frequency word
  // freq_word = freq * 2^28 / MCLK
  uint32_t freqWord = (uint32_t)((freq * 268435456.0) / MCLK);
  
  uint16_t reg = (freqReg == 0) ? AD9833_FREQ0 : AD9833_FREQ1;
  
  // Split into two 14-bit words
  uint16_t lsb = freqWord & 0x3FFF;
  uint16_t msb = (freqWord >> 14) & 0x3FFF;
  
  // Set control bits
  lsb |= reg;
  msb |= reg;
  
  // Write both parts
  ad9833_write(AD9833_B28 | AD9833_RESET);  // Enter reset, enable B28
  ad9833_write(lsb);
  ad9833_write(msb);
  ad9833_write(AD9833_B28);  // Exit reset, keep B28
}
