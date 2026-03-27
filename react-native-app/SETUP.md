# React Native ShearWave App - Setup Guide

## Prerequisites

### Development Environment
- Node.js 16+ (LTS recommended)
- npm or yarn
- React Native CLI
- Android Studio (for Android) or Xcode (for iOS)

### Mobile Device
- Android 8.0+ or iOS 13+
- Accelerometer sensor
- Bluetooth Low Energy (for ESP32 connection)

## Installation

### 1. Install React Native CLI
```bash
npm install -g react-native-cli
```

### 2. Clone/Copy Project
```bash
cd /home/james/.openclaw/workspace/react-native-app
```

### 3. Install Dependencies
```bash
npm install
```

### 4. iOS Specific Setup (Mac only)
```bash
cd ios
pod install
cd ..
```

### 5. Android Permissions

Add to `android/app/src/main/AndroidManifest.xml`:
```xml
<!-- Bluetooth permissions -->
<uses-permission android:name="android.permission.BLUETOOTH" />
<uses-permission android:name="android.permission.BLUETOOTH_ADMIN" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
<uses-permission android:name="android.permission.BLUETOOTH_SCAN" />
<uses-permission android:name="android.permission.BLUETOOTH_CONNECT" />

<!-- Sensor permission -->
<uses-permission android:name="android.permission.HIGH_SAMPLING_RATE_SENSORS" />

<!-- For Android 12+ -->
<uses-permission android:name="android.permission.BLUETOOTH_ADVERTISE" />
```

### 6. iOS Permissions (Mac only)

Add to `ios/YourApp/Info.plist`:
```xml
<key>NSBluetoothAlwaysUsageDescription</key>
<string>This app uses Bluetooth to connect to ESP32 for data acquisition.</string>

<key>NSBluetoothPeripheralUsageDescription</key>
<string>This app needs Bluetooth to communicate with the measurement device.</string>

<key>NSMotionUsageDescription</key>
<string>This app uses the accelerometer to measure ultrasonic shear waves.</string>

<key>NSLocationWhenInUseUsageDescription</key>
<string>Location is used for tagging measurement sites.</string>
```

## Running the App

### Development Mode

#### Android
```bash
# Start Metro bundler
npm start

# In another terminal, run on device/emulator
npm run android
```

#### iOS
```bash
# Start Metro bundler
npm start

# In another terminal, run on simulator/device
npm run ios
```

### Building Release APK (Android)
```bash
cd android
./gradlew assembleRelease
```
Output: `android/app/build/outputs/apk/release/app-release.apk`

### Building Release IPA (iOS)
Use Xcode:
1. Open `ios/YourApp.xcworkspace`
2. Select device/simulator
3. Product → Archive
4. Distribute App

## Troubleshooting

### Metro bundler issues
```bash
# Clear cache
npm start -- --reset-cache

# Or
npx react-native start --reset-cache
```

### Android build fails
```bash
cd android
./gradlew clean
cd ..
npm run android
```

### iOS pod install fails
```bash
cd ios
rm -rf Pods Podfile.lock
pod install --repo-update
cd ..
```

### Sensor not working (Android)
- Check `AndroidManifest.xml` has `HIGH_SAMPLING_RATE_SENSORS` permission
- Some devices limit sampling rate to 200 Hz (hardware limitation)

### Sensor not working (iOS)
- Add `NSMotionUsageDescription` to Info.plist
- User must grant permission on first launch
- iOS typically limits to 60 Hz (use Core Motion directly for higher rates)

### Bluetooth not connecting
- Ensure ESP32 is powered and advertising
- Check UUIDs match exactly (case-sensitive)
- Try forgetting device in Bluetooth settings
- Android: Grant location permission (required for BLE scan)

## File Structure

```
react-native-app/
├── android/              # Android native code
├── ios/                  # iOS native code
├── src/
│   ├── components/       # Reusable UI components
│   │   ├── PositionGuide.js
│   │   ├── RecordButton.js
│   │   ├── ProgressCard.js
│   │   ├── WaveformChart.js
│   │   └── StatsPanel.js
│   ├── screens/          # Screen components
│   │   └── MeasureScreen.js
│   ├── hooks/            # Custom React hooks
│   │   └── useAccelerometer.js
│   ├── services/         # Business logic
│   │   └── BluetoothService.js
│   └── utils/            # Utilities & constants
│       └── constants.js
├── App.js                # App entry with navigation
├── index.js              # Root registration
├── package.json          # Dependencies
└── README.md             # This file
```

## Key Dependencies Explained

| Package | Purpose |
|---------|---------|
| `react-native-sensors` | Access device accelerometer |
| `react-native-ble-plx` | Bluetooth Low Energy communication |
| `@react-navigation/native` | Screen navigation |
| `react-native-svg` | Drawing phantom diagram |
| `react-native-reanimated` | Smooth animations |
| `@react-native-async-storage` | Local data storage |

## Next Steps

1. **Test with phone sensor only**
   - Comment out Bluetooth code in MeasureScreen
   - Verify accelerometer data flows
   - Test recording and waveform display

2. **Add ESP32 connection**
   - Flash ESP32 with firmware
   - Verify BLE advertising
   - Test command sending and data reception

3. **Customize**
   - Adjust `TOTAL_POSITIONS` in constants.js
   - Change `RECORD_DURATION` if needed
   - Modify phantom diagram dimensions

4. **Build release version**
   - Generate signed APK/IPA
   - Distribute to field team

## Support

- React Native docs: https://reactnative.dev
- BLE library: https://github.com/dotintent/react-native-ble-plx
- Sensors library: https://github.com/react-native-sensors/react-native-sensors
