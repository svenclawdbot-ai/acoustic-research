// Measurement configuration
export const SAMPLING_RATES = [100, 250, 500, 1000];
export const DEFAULT_RATE = 500;

export const RECORD_DURATION = 100; // ms
export const TOTAL_POSITIONS = 12;

// Position definitions (cm from left edge, percentage for visualization)
export const POSITIONS = [
  { id: 1, cm: 2.0, x: 10 },
  { id: 2, cm: 3.1, x: 20 },
  { id: 3, cm: 4.2, x: 30 },
  { id: 4, cm: 5.3, x: 40 },
  { id: 5, cm: 6.4, x: 50 },
  { id: 6, cm: 7.5, x: 60 },
  { id: 7, cm: 8.5, x: 70 },
  { id: 8, cm: 9.6, x: 80 },
  { id: 9, cm: 10.7, x: 85 },
  { id: 10, cm: 11.8, x: 90 },
  { id: 11, cm: 12.9, x: 95 },
  { id: 12, cm: 14.0, x: 98 },
];

// BLE Configuration (must match ESP32 firmware)
export const BLE_CONFIG = {
  serviceUUID: '4fafc201-1fb5-459e-8fcc-c5c9c331914b',
  dataCharUUID: 'beb5483e-36e1-4688-b7f5-ea07361b26a8',
  commandCharUUID: '00002a52-0000-1000-8000-00805f9b34fb',
  statusCharUUID: '00002a3b-0000-1000-8000-00805f9b34fb',
};

// Quality thresholds
export const QUALITY_THRESHOLDS = {
  excellent: 10, // dB SNR
  good: 5,
  fair: 3,
  poor: 0,
};

// Phantom dimensions (for visualization)
export const PHANTOM = {
  widthCm: 20,
  heightCm: 10,
  depthCm: 5,
};

// Colors
export const COLORS = {
  primary: '#667eea',
  primaryDark: '#764ba2',
  success: '#27ae60',
  warning: '#f39c12',
  danger: '#e74c3c',
  info: '#3498db',
  gray: '#95a5a6',
  lightGray: '#ecf0f1',
  darkGray: '#2c3e50',
  white: '#ffffff',
  black: '#000000',
};
