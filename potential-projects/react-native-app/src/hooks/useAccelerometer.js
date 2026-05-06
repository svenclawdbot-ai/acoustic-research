import { useState, useEffect, useRef, useCallback } from 'react';
import { accelerometer, SensorTypes, setUpdateIntervalForType } from 'react-native-sensors';
import { Platform } from 'react-native';

// Enable high sampling rate on Android
if (Platform.OS === 'android') {
  setUpdateIntervalForType(SensorTypes.accelerometer, 2); // 2ms = 500Hz
} else {
  setUpdateIntervalForType(SensorTypes.accelerometer, 16); // 16ms = ~60Hz (iOS limit)
}

const useAccelerometer = (options = {}) => {
  const {
    samplingRate = 500, // Hz
    enabled = true,
    calibrationDuration = 1000, // ms
  } = options;

  const [data, setData] = useState({ x: 0, y: 0, z: 0, timestamp: 0 });
  const [buffer, setBuffer] = useState([]);
  const [isAvailable, setIsAvailable] = useState(false);
  const [isCalibrating, setIsCalibrating] = useState(false);
  const [calibrationOffset, setCalibrationOffset] = useState({ x: 0, y: 0, z: 0 });
  const [error, setError] = useState(null);

  const bufferRef = useRef([]);
  const subscriptionRef = useRef(null);

  // Check sensor availability
  useEffect(() => {
    const checkAvailability = async () => {
      try {
        // Try to subscribe briefly to check
        const testSub = accelerometer.subscribe(() => {});
        setIsAvailable(true);
        testSub.unsubscribe();
      } catch (err) {
        setIsAvailable(false);
        setError('Accelerometer not available');
      }
    };

    checkAvailability();
  }, []);

  // Calibration function
  const calibrate = useCallback(async () => {
    if (!isAvailable) return;

    setIsCalibrating(true);
    const calibrationSamples = [];

    return new Promise((resolve) => {
      const calSub = accelerometer.subscribe(({ x, y, z }) => {
        calibrationSamples.push({ x, y, z });
      });

      setTimeout(() => {
        calSub.unsubscribe();

        // Calculate averages
        const avg = (arr) => arr.reduce((a, b) => a + b, 0) / arr.length;
        
        const offset = {
          x: avg(calibrationSamples.map(s => s.x)),
          y: avg(calibrationSamples.map(s => s.y)),
          z: avg(calibrationSamples.map(s => s.z)) - 1, // Remove gravity
        };

        setCalibrationOffset(offset);
        setIsCalibrating(false);
        resolve(offset);
      }, calibrationDuration);
    });
  }, [isAvailable, calibrationDuration]);

  // Start recording to buffer
  const startRecording = useCallback((durationMs) => {
    if (!isAvailable) return;

    bufferRef.current = [];
    const startTime = Date.now();

    subscriptionRef.current = accelerometer.subscribe(({ x, y, z, timestamp }) => {
      // Apply calibration
      const calibrated = {
        x: x - calibrationOffset.x,
        y: y - calibrationOffset.y,
        z: z - calibrationOffset.z,
        t: Date.now() - startTime,
        timestamp,
      };

      bufferRef.current.push(calibrated);

      // Update live data
      setData(calibrated);

      // Auto-stop after duration
      if (calibrated.t >= durationMs) {
        stopRecording();
      }
    });
  }, [isAvailable, calibrationOffset]);

  // Stop recording
  const stopRecording = useCallback(() => {
    if (subscriptionRef.current) {
      subscriptionRef.current.unsubscribe();
      subscriptionRef.current = null;
    }
    
    setBuffer([...bufferRef.current]);
    return bufferRef.current;
  }, []);

  // Clear buffer
  const clearBuffer = useCallback(() => {
    bufferRef.current = [];
    setBuffer([]);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (subscriptionRef.current) {
        subscriptionRef.current.unsubscribe();
      }
    };
  }, []);

  // Calculate statistics from buffer
  const getStats = useCallback(() => {
    if (buffer.length === 0) return null;

    const samples = buffer;
    
    // RMS calculation
    const rms = Math.sqrt(
      samples.reduce((sum, s) => sum + s.x * s.x + s.y * s.y + s.z * s.z, 0) / 
      samples.length
    );

    // Peak detection
    const peak = Math.max(
      ...samples.map(s => Math.sqrt(s.x * s.x + s.y * s.y + s.z * s.z))
    );

    // Simple SNR estimate (signal vs first 10 samples as noise)
    const noiseSamples = samples.slice(0, 10);
    const signalSamples = samples.slice(10);
    
    const noisePower = noiseSamples.reduce((sum, s) => sum + s.x * s.x, 0) / noiseSamples.length;
    const signalPower = signalSamples.reduce((sum, s) => sum + s.x * s.x, 0) / signalSamples.length;
    
    const snr = noisePower > 0 ? 10 * Math.log10(signalPower / noisePower) : 0;

    return {
      sampleCount: samples.length,
      rms,
      peak,
      snr,
      duration: samples[samples.length - 1]?.t || 0,
    };
  }, [buffer]);

  return {
    data,
    buffer,
    isAvailable,
    isCalibrating,
    error,
    calibrate,
    startRecording,
    stopRecording,
    clearBuffer,
    getStats,
  };
};

export default useAccelerometer;
