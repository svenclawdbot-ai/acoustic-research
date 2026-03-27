# React Native ShearWave Acquisition App

React Native app for smartphone-based ultrasonic shear wave measurement.

## Features

- 📱 Real-time accelerometer data (up to 500 Hz)
- 🔵 Bluetooth LE connection to ESP32
- 📊 Live waveform visualization
- 💾 Local data storage with upload queue
- 🗺️ Position guidance with visual phantom diagram

## Prerequisites

- Node.js 16+
- React Native development environment
- Expo CLI (optional, for easier setup)
- Android/iOS device with accelerometer

## Installation

```bash
# Install dependencies
npm install

# For iOS (Mac only)
cd ios && pod install && cd ..

# Start Metro bundler
npm start
```

## Running on Device

```bash
# Android
npm run android

# iOS
npm run ios

# Expo
npm run expo
```

## Project Structure

```
src/
├── components/
│   ├── PositionGuide.js      # Phantom diagram with position markers
│   ├── WaveformChart.js      # Real-time waveform visualization
│   ├── ProgressCard.js       # Measurement progress indicator
│   ├── RecordButton.js       # Recording control with animation
│   └── StatsPanel.js         # SNR, peak, frequency stats
├── screens/
│   ├── MeasureScreen.js      # Main acquisition screen
│   ├── ResultsScreen.js      # Dispersion curves & analysis
│   └── SettingsScreen.js     # Sampling rate, positions, etc.
├── hooks/
│   ├── useAccelerometer.js   # Sensor data hook
│   ├── useBluetooth.js       # BLE connection management
│   └── useRecording.js       # Recording state & data buffer
├── services/
│   ├── BluetoothService.js   # BLE peripheral management
│   ├── StorageService.js     # AsyncStorage for offline data
│   └── AnalysisService.js    # Real-time SNR/quality metrics
└── utils/
    ├── constants.js          # Sampling rates, position arrays
    └── helpers.js            # Data conversion, formatting
```

## Dependencies

```json
{
  "react-native-sensors": "^7.3.0",
  "react-native-ble-plx": "^3.1.2",
  "@react-native-async-storage/async-storage": "^1.19.0",
  "react-native-svg": "^13.0.0",
  "react-native-chart-kit": "^6.12.0",
  "react-native-reanimated": "^3.5.0",
  "react-navigation": "^6.0.0"
}
```

## ESP32 BLE Protocol

### Service UUID
```
SHEARWAVE_SERVICE = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
```

### Characteristics
```
ACCEL_DATA_CHAR = "beb5483e-36e1-4688-b7f5-ea07361b26a8"  // Notify
COMMAND_CHAR = "00002a52-0000-1000-8000-00805f9b34fb"      // Write
STATUS_CHAR = "00002a3b-0000-1000-8000-00805f9b34fb"       // Read/Notify
```

### Command Format
```javascript
// Start acquisition
{
  cmd: "START_ACQUISITION",
  position: 4,           // Position index (1-12)
  duration: 100,         // ms
  sampleRate: 500        // Hz
}

// Stop acquisition
{
  cmd: "STOP"
}

// Get status
{
  cmd: "GET_STATUS"
}
```

### Data Format (from ESP32)
```javascript
{
  position: 4,
  timestamp: 1699123456789,
  samples: [
    {t: 0, x: 0.0012, y: -0.0003, z: 0.9998},
    {t: 2, x: 0.0015, y: -0.0001, z: 0.9999},
    // ... 50 samples for 100ms @ 500Hz
  ],
  stats: {
    snr: 8.2,
    peak: 0.0021,
    rms: 0.0008
  }
}
```

## Configuration

Edit `src/utils/constants.js`:

```javascript
export const SAMPLING_RATES = [100, 250, 500, 1000];
export const DEFAULT_RATE = 500;

export const POSITIONS = [
  { id: 1, cm: 2.0, x: 20 },
  { id: 2, cm: 3.1, x: 35 },
  { id: 3, cm: 4.2, x: 50 },
  // ... 12 positions
];

export const RECORD_DURATION = 100; // ms
export const TOTAL_POSITIONS = 12;

export const ESP32_CONFIG = {
  serviceUUID: "4fafc201-1fb5-459e-8fcc-c5c9c331914b",
  dataCharUUID: "beb5483e-36e1-4688-b7f5-ea07361b26a8",
  commandCharUUID: "00002a52-0000-1000-8000-00805f9b34fb",
  statusCharUUID: "00002a3b-0000-1000-8000-00805f9b34fb",
};
```

## Usage Flow

1. **Connect to ESP32**
   - App scans for BLE devices
   - Select "ShearWave-Device"
   - Automatic connection

2. **Position Phone**
   - Follow visual guide (phantom diagram)
   - Position markers show completed/current/next
   - Text instructions with distance

3. **Record**
   - Press record button
   - 100ms acquisition (50 samples @ 500Hz)
   - Real-time waveform preview
   - Stats: SNR, peak amplitude, dominant frequency

4. **Next Position**
   - Auto-advance or manual
   - Progress bar updates
   - Estimated time remaining

5. **Complete**
   - All 12 positions recorded
   - Upload to ESP32 or save locally
   - View dispersion results

## Development Notes

### Sensor Calibration
```javascript
// Zero-offset calibration before measurement
const calibrate = async () => {
  const samples = [];
  const subscription = accelerometer.subscribe(({ x, y, z }) => {
    samples.push({ x, y, z });
  });
  
  await delay(1000); // 1 second calibration
  subscription.unsubscribe();
  
  const offset = {
    x: avg(samples.map(s => s.x)),
    y: avg(samples.map(s => s.y)),
    z: avg(samples.map(s => s.z)) - 1, // Remove gravity
  };
  
  return offset;
};
```

### Offline Mode
```javascript
// Queue data when BLE unavailable
const queueMeasurement = async (data) => {
  const queue = await AsyncStorage.getItem('measurementQueue');
  const newQueue = [...JSON.parse(queue), data];
  await AsyncStorage.setItem('measurementQueue', JSON.stringify(newQueue));
};

// Upload when connected
const uploadQueue = async () => {
  const queue = JSON.parse(await AsyncStorage.getItem('measurementQueue'));
  for (const data of queue) {
    await BluetoothService.sendData(data);
  }
  await AsyncStorage.setItem('measurementQueue', '[]');
};
```

## Troubleshooting

### Sensor not working
- Check permissions: `android.permission.HIGH_SAMPLING_RATE_SENSORS`
- iOS: Add `NSMotionUsageDescription` to Info.plist

### BLE connection fails
- Ensure ESP32 is advertising
- Check UUIDs match exactly
- Try forgetting device in Bluetooth settings

### Low sampling rate
- Some Android devices limit to 200-250 Hz
- Use `react-native-sensors` with `interval: 'fastest'`
- Consider native module for >500 Hz

## License

MIT
