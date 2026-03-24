# ESP32 Firmware Specification
## Shear Wave Elastography Controller

**Platform:** ESP32-S3 (dual-core, WiFi/BT, 512KB SRAM)  
**Framework:** Arduino / ESP-IDF  
**Version:** 1.0  
**Date:** March 16, 2026

---

## SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                      ESP32-S3                                   │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   CORE 0    │    │   CORE 1    │    │   SHARED    │         │
│  │  (PRO_CPU)  │    │  (APP_CPU)  │    │   MEMORY    │         │
│  │             │    │             │    │             │         │
│  │ Waveform    │    │ Sensor      │    │ Ring Buffer │         │
│  │ Generation  │    │ Acquisition │    │ (DMA)       │         │
│  │ - DAC/PWM   │    │ - SPI/I2C   │    │ - 32KB      │         │
│  │ - Timing    │    │ - Filtering │    │             │         │
│  │ - Trigger   │    │ - Decimate  │    │ Command     │         │
│  │             │    │             │    │ Queue       │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  GPIO 25    │    │  SPI (HSPI) │    │  USB CDC    │         │
│  │  (DAC_1)    │    │  SCK: 14    │    │  Serial     │         │
│  │             │    │  MOSI: 13   │    │  921600     │         │
│  │  HV Amp     │    │  MISO: 12   │    │             │         │
│  │  (150V)     │    │  CS: 15     │    │  Bluetooth  │         │
│  │             │    │             │    │  SPP/BLE    │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   PIEZO     │    │  4× ADXL355 │    │  HOST PC    │         │
│  │   STACK     │    │  (SPI)      │    │  / TABLET   │         │
│  │             │    │  SENSORS    │    │             │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

---

## PIN ASSIGNMENT

### Power
| Pin | Function | Notes |
|-----|----------|-------|
| 3V3 | Digital supply | 500 mA max |
| 5V | USB input | Or external 5V |
| GND | Common ground | Multiple pins |

### Waveform Output
| Pin | GPIO | Function | Drive |
|-----|------|----------|-------|
| 25 | DAC_1 | Analog waveform | Direct to amp |
| 26 | DAC_2 | Spare / Sync | - |
| 27 | GPIO | HV enable | 3.3V logic |

### Sensor SPI (HSPI)
| Pin | GPIO | Function | ADXL355 Pin |
|-----|------|----------|-------------|
| 14 | HSCK | SPI Clock | SCLK |
| 13 | HMOSI | SPI MOSI | MOSI |
| 12 | HMISO | SPI MISO | MISO |
| 15 | HCS | SPI CS (Master) | CS |
| 4 | GPIO | CS Sensor 1 | CS1 |
| 16 | GPIO | CS Sensor 2 | CS2 |
| 17 | GPIO | CS Sensor 3 | CS3 |
| 18 | GPIO | CS Sensor 4 | CS4 |
| 19 | GPIO | DRDY (interrupt) | DRDY |

### Status LEDs
| Pin | GPIO | Function |
|-----|------|----------|
| 2 | GPIO | System ready (green) |
| 5 | GPIO | Acquiring (yellow) |
| 21 | GPIO | Error (red) |

### Communication
| Pin | Function | Speed |
|-----|----------|-------|
| USB | CDC Serial | 921600 baud |
| - | Bluetooth SPP | 115200 baud |

---

## WAVEFORM GENERATION MODULE

### Requirements
- **Frequency range:** 50-500 Hz
- **Waveform types:** Sine, Ricker (Mexican hat), Chirp, Burst
- **Amplitude:** 0-3.3V (DAC full scale)
- **Update rate:** 100 kHz (10 μs sample period)
- **Buffer size:** 1000 samples (10 ms @ 100 kHz)

### Implementation

```cpp
// Waveform types
enum WaveformType {
    WAVE_SINE,
    WAVE_RICKER,
    WAVE_CHIRP,
    WAVE_BURST
};

// Waveform parameters
struct WaveformConfig {
    WaveformType type;
    float frequency;        // Hz (for sine/burst)
    float startFreq;        // Hz (for chirp)
    float endFreq;          // Hz (for chirp)
    uint16_t amplitude;     // 0-4095 (12-bit DAC)
    uint16_t duration;      // ms
    uint16_t cycles;        // For burst
    bool enabled;
};

// ISR: DAC update (100 kHz)
void IRAM_ATTR onDacTimer() {
    static uint16_t sampleIndex = 0;
    
    if (!waveform.enabled) {
        dac_output_voltage(DAC_CHANNEL_1, 0);
        return;
    }
    
    // Lookup waveform from pre-computed buffer
    uint8_t value = waveformBuffer[sampleIndex];
    dac_output_voltage(DAC_CHANNEL_1, value);
    
    sampleIndex++;
    if (sampleIndex >= waveformLength) {
        sampleIndex = 0;
        waveformCycleCount++;
        
        // Stop after specified duration
        if (waveformCycleCount >= targetCycles) {
            waveform.enabled = false;
            digitalWrite(PIN_HV_ENABLE, LOW);  // Disable HV
        }
    }
}
```

### Waveform Pre-computation

```cpp
void computeWaveform(WaveformConfig& cfg) {
    float dt = 1.0 / DAC_SAMPLE_RATE;  // 10 μs
    float T = 1.0 / cfg.frequency;
    uint16_t samplesPerPeriod = (uint16_t)(T / dt);
    
    switch(cfg.type) {
        case WAVE_SINE:
            for (int i = 0; i < samplesPerPeriod; i++) {
                float t = i * dt;
                float value = sin(2 * PI * cfg.frequency * t);
                waveformBuffer[i] = (uint8_t)(2047 + value * cfg.amplitude);
            }
            break;
            
        case WAVE_RICKER:
            // Mexican hat wavelet: second derivative of Gaussian
            float sigma = 1.0 / (PI * cfg.frequency);
            for (int i = 0; i < samplesPerPeriod * 6; i++) {  // 6 sigma duration
                float t = i * dt - 3*sigma;
                float value = (1 - 2*pow(t/sigma, 2)) * exp(-pow(t/sigma, 2));
                waveformBuffer[i] = (uint8_t)(2047 + value * cfg.amplitude);
            }
            break;
            
        case WAVE_CHIRP:
            // Linear frequency sweep
            float chirpDuration = 0.01;  // 10 ms
            uint16_t chirpSamples = chirpDuration / dt;
            for (int i = 0; i < chirpSamples; i++) {
                float t = i * dt;
                float frac = t / chirpDuration;
                float freq = cfg.startFreq + (cfg.endFreq - cfg.startFreq) * frac;
                float phase = 2 * PI * (cfg.startFreq * t + 
                                       (cfg.endFreq - cfg.startFreq) * t * t / (2 * chirpDuration));
                waveformBuffer[i] = (uint8_t)(2047 + sin(phase) * cfg.amplitude);
            }
            break;
    }
}
```

---

## SENSOR ACQUISITION MODULE

### ADXL355 Configuration
- **Interface:** SPI, 4-wire
- **Data rate:** 1 kHz (configurable: 125-4000 Hz)
- **Range:** ±2g (0.25 mg resolution)
- **Filter:** Low-pass, configurable corner

### Timing Synchronization

```cpp
// Sensor sampling ISR (1 kHz)
void IRAM_ATTR onSensorTimer() {
    // Trigger SPI reads for all 4 sensors
    for (int i = 0; i < NUM_SENSORS; i++) {
        // Select sensor
        digitalWrite(sensorCS[i], LOW);
        
        // Read 3 axes (X, Y, Z) - 6 bytes total
        // ADXL355 auto-increments register address
        SPI.transfer(0x08 | 0x80);  // Read from XDATA3
        int32_t x = (SPI.transfer(0) << 16) | (SPI.transfer(0) << 8) | SPI.transfer(0);
        int32_t y = (SPI.transfer(0) << 16) | (SPI.transfer(0) << 8) | SPI.transfer(0);
        int32_t z = (SPI.transfer(0) << 16) | (SPI.transfer(0) << 8) | SPI.transfer(0);
        
        digitalWrite(sensorCS[i], HIGH);
        
        // Sign extend 20-bit to 32-bit
        x = (x << 12) >> 12;
        y = (y << 12) >> 12;
        z = (z << 12) >> 12;
        
        // Store in ring buffer
        sensorData[sensorIndex][i].x = x;
        sensorData[sensorIndex][i].y = y;
        sensorData[sensorIndex][i].z = z;
        sensorData[sensorIndex][i].timestamp = micros();
    }
    
    sensorIndex = (sensorIndex + 1) % BUFFER_SIZE;
    sampleCount++;
    
    // Signal main loop if buffer half full
    if (sampleCount % (BUFFER_SIZE/2) == 0) {
        BaseType_t xHigherPriorityTaskWoken = pdFALSE;
        vTaskNotifyGiveFromISR(dataTaskHandle, &xHigherPriorityTaskWoken);
        portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    }
}
```

### Sensor Data Structure

```cpp
struct SensorSample {
    int32_t x;          // 20-bit, sign-extended
    int32_t y;
    int32_t z;
    uint32_t timestamp; // microseconds
};

// Ring buffer
#define BUFFER_SIZE 4096  // ~4 seconds at 1 kHz
SensorSample sensorData[BUFFER_SIZE][NUM_SENSORS];
volatile uint16_t sensorIndex = 0;
volatile uint32_t sampleCount = 0;
```

---

## COMMUNICATION PROTOCOL

### Command Format (Host → ESP32)

```
[HEADER][COMMAND][PAYLOAD_LEN][PAYLOAD][CHECKSUM]

HEADER:     0xAA 0x55 (2 bytes)
COMMAND:    1 byte (see below)
PAYLOAD_LEN: 1 byte (0-255)
PAYLOAD:    0-255 bytes
CHECKSUM:   XOR of COMMAND, PAYLOAD_LEN, and all PAYLOAD bytes
```

### Command Set

| Command | Code | Payload | Description |
|---------|------|---------|-------------|
| CMD_PING | 0x01 | - | Check connectivity |
| CMD_GET_STATUS | 0x02 | - | Return system status |
| CMD_SET_WAVEFORM | 0x10 | WaveformConfig | Configure output |
| CMD_START_ACQ | 0x11 | Duration (ms) | Begin acquisition |
| CMD_STOP_ACQ | 0x12 | - | Stop immediately |
| CMD_GET_DATA | 0x20 | Offset, Count | Request data chunk |
| CMD_SET_PARAMS | 0x30 | Config struct | Update parameters |
| CMD_CALIBRATE | 0x40 | - | Run calibration |
| CMD_RESET | 0xFF | - | System reset |

### Response Format (ESP32 → Host)

```
[HEADER][STATUS][DATA_LEN][DATA][CHECKSUM]

HEADER:     0xAA 0x55
STATUS:     0x00=OK, 0x01=Error, 0x02=Data ready
DATA_LEN:   2 bytes (little-endian, 0-65535)
DATA:       Variable
CHECKSUM:   XOR checksum
```

### Data Streaming

```cpp
// Background task: stream data to host
void dataStreamingTask(void *pvParameters) {
    while (1) {
        // Wait for notification from ISR
        ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
        
        if (!acquisitionActive) continue;
        
        // Send half buffer
        uint16_t startIdx = (sensorIndex < BUFFER_SIZE/2) ? 0 : BUFFER_SIZE/2;
        uint16_t endIdx = startIdx + BUFFER_SIZE/2;
        
        // Header
        Serial.write(0xAA);
        Serial.write(0x55);
        Serial.write(0x02);  // Data ready
        
        // Data length (4 sensors × 3 axes × 4 bytes + timestamp × 4 bytes)
        uint16_t dataLen = (BUFFER_SIZE/2) * NUM_SENSORS * (3*4 + 4);
        Serial.write(dataLen & 0xFF);
        Serial.write((dataLen >> 8) & 0xFF);
        
        // Stream data
        for (uint16_t i = startIdx; i < endIdx; i++) {
            for (int s = 0; s < NUM_SENSORS; s++) {
                Serial.write((uint8_t*)&sensorData[i][s], sizeof(SensorSample));
            }
        }
        
        // Checksum
        uint8_t checksum = 0;
        // ... compute checksum
        Serial.write(checksum);
    }
}
```

---

## CONFIGURATION PARAMETERS

### Default Settings

```cpp
struct SystemConfig {
    // Acquisition
    uint16_t sampleRate = 1000;         // Hz
    uint16_t acquisitionDuration = 50;  // ms
    uint8_t numAverages = 1;
    
    // Waveform
    WaveformConfig waveform = {
        .type = WAVE_RICKER,
        .frequency = 200.0,
        .amplitude = 3000,  // ~2.4V
        .duration = 10,     // ms
        .cycles = 1,
        .enabled = false
    };
    
    // Sensors
    uint8_t sensorRange = 2;            // ±2g
    uint8_t filterCorner = 4;           // 125 Hz (see ADXL355 datasheet)
    
    // Trigger
    bool externalTrigger = false;
    uint16_t preTriggerSamples = 100;   // ms
    
    // Communication
    uint32_t baudRate = 921600;
    bool bluetoothEnabled = false;
};

SystemConfig config;
```

---

## CALIBRATION PROCEDURE

### Step 1: Sensor Zero Offset
```
1. Place probe on stable surface
2. Send CMD_CALIBRATE
3. ESP32 averages 1000 samples per sensor
4. Stores offsets in NVS (non-volatile storage)
5. Applies offsets to all future samples
```

### Step 2: Timing Calibration
```
1. Connect scope to sync output
2. Send CMD_START_ACQ with known delay
3. Measure actual delay
4. Compensate in software
```

### Step 3: Amplitude Calibration
```
1. Place on known stiffness phantom
2. Measure response at different amplitudes
3. Store amplitude-to-force relationship
```

---

## ERROR HANDLING

| Error Code | Cause | Action |
|------------|-------|--------|
| ERR_SPI (0x01) | Sensor communication failure | Retry 3x, then report |
| ERR_DAC (0x02) | Waveform buffer underrun | Reduce sample rate |
| ERR_BUFFER (0x03) | Ring buffer overflow | Increase USB baud |
| ERR_TIMEOUT (0x04) | Acquisition timeout | Check sensor status |
| ERR_CHECKSUM (0x05) | Command corruption | Request retransmit |

---

## POWER MANAGEMENT

### Operating Modes

| Mode | Current | Use Case |
|------|---------|----------|
| Active | 200 mA | Acquisition running |
| Idle | 50 mA | Connected, waiting |
| Sleep | 10 mA | Battery conservation |
| Deep Sleep | 100 μA | Long-term storage |

### Battery Estimation
- **2000 mAh LiPo:** ~10 hours active, ~40 hours idle
- **Power bank (20000 mAh):** ~100 hours active

---

## FIRMWARE STRUCTURE

```
shear_wave_probe/
├── src/
│   ├── main.cpp              # Entry point, setup
│   ├── waveform_generator.cpp
│   ├── waveform_generator.h
│   ├── sensor_acquisition.cpp
│   ├── sensor_acquisition.h
│   ├── communication.cpp     # Serial/Bluetooth
│   ├── communication.h
│   ├── calibration.cpp
│   ├── calibration.h
│   └── config.h              # Pin definitions
├── lib/
│   └── (Arduino libraries)
├── data/
│   └── index.html            # Web interface (optional)
└── platformio.ini            # Build config
```

---

## BUILD CONFIGURATION

### platformio.ini
```ini
[env:esp32-s3]
platform = espressif32
board = esp32-s3-devkitc-1
framework = arduino
monitor_speed = 921600
upload_speed = 921600

lib_deps =
    SPI
    Wire
    ArduinoJson

build_flags =
    -D CORE_DEBUG_LEVEL=3
    -D CONFIG_ARDUHAL_LOG_COLORS=1
    -D DAC_SAMPLE_RATE=100000
    -D SENSOR_SAMPLE_RATE=1000

board_build.partitions = partitions.csv
```

### partitions.csv (8MB Flash)
```
# Name,   Type, SubType, Offset,  Size,    Flags
nvs,      data, nvs,     0x9000,  0x6000,
phy_init, data, phy,     0xf000,  0x1000,
factory,  app,  factory, 0x10000, 0x200000,
storage,  data, spiffs,  0x210000,0x5F0000,
```

---

## TESTING CHECKLIST

### Unit Tests
- [ ] DAC outputs expected waveform (scope)
- [ ] SPI reads correct ADXL355 ID
- [ ] All 4 sensors sample at 1 kHz
- [ ] Ring buffer operates without overflow
- [ ] Serial communication at 921600 baud
- [ ] Bluetooth SPP pairs and connects

### Integration Tests
- [ ] Waveform syncs with sensor acquisition
- [ ] Data streams continuously for 10 seconds
- [ ] Command parser handles all commands
- [ ] Calibration stores and applies offsets
- [ ] Error recovery after sensor disconnect

### System Tests
- [ ] Full acquisition cycle (generate + acquire)
- [ ] Host Python script receives clean data
- [ ] Real-time display updates smoothly
- [ ] Battery life meets specification

---

## HOST SOFTWARE INTERFACE

### Python Example

```python
import serial
import struct
import numpy as np

class ShearWaveProbe:
    def __init__(self, port='/dev/ttyUSB0', baud=921600):
        self.ser = serial.Serial(port, baud, timeout=1)
        
    def set_waveform(self, freq=200, amp=3000, duration=10):
        """Configure Ricker wavelet."""
        payload = struct.pack('<fH', freq, amp) + bytes([duration])
        self._send_command(0x10, payload)
        
    def acquire(self, duration_ms=50):
        """Start acquisition, return data."""
        self._send_command(0x11, bytes([duration_ms]))
        
        # Read data
        data = self._read_data()
        
        # Parse into arrays
        num_samples = len(data) // (4 * 16)  # 4 sensors × 16 bytes
        samples = np.frombuffer(data, dtype=np.int32).reshape(num_samples, 4, 4)
        
        return samples  # [sample, sensor, axis+timestamp]
        
    def _send_command(self, cmd, payload):
        """Send command with checksum."""
        header = bytes([0xAA, 0x55])
        checksum = cmd ^ len(payload)
        for b in payload:
            checksum ^= b
        
        self.ser.write(header + bytes([cmd, len(payload)]) + payload + bytes([checksum]))
        
    def _read_data(self):
        """Read data packet."""
        # Wait for header
        while self.ser.read(1) != b'\xAA':
            pass
        if self.ser.read(1) != b'\x55':
            raise IOError("Invalid header")
            
        status = self.ser.read(1)[0]
        data_len = struct.unpack('<H', self.ser.read(2))[0]
        data = self.ser.read(data_len)
        checksum = self.ser.read(1)[0]
        
        return data

# Usage
probe = ShearWaveProbe()
probe.set_waveform(freq=200, amp=3000)
data = probe.acquire(duration_ms=50)

# Plot
import matplotlib.pyplot as plt
plt.plot(data[:, 0, 0])  # Sensor 0, X-axis
plt.show()
```

---

## REVISION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-16 | Initial specification |

---

*Firmware specification for ESP32-S3 based shear wave probe*  
*Compatible with hardware design in BOM_flexural_beam_probe.md*
