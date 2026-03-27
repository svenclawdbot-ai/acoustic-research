import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Alert,
  ActivityIndicator,
} from 'react-native';
import PositionGuide from '../components/PositionGuide';
import RecordButton from '../components/RecordButton';
import ProgressCard from '../components/ProgressCard';
import WaveformChart from '../components/WaveformChart';
import StatsPanel from '../components/StatsPanel';
import useAccelerometer from '../hooks/useAccelerometer';
import BluetoothService from '../services/BluetoothService';
import { POSITIONS, TOTAL_POSITIONS, RECORD_DURATION } from '../utils/constants';

const MeasureScreen = () => {
  const [currentPosition, setCurrentPosition] = useState(1);
  const [completedPositions, setCompletedPositions] = useState([]);
  const [isRecording, setIsRecording] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [lastMeasurement, setLastMeasurement] = useState(null);
  const [usePhoneSensor, setUsePhoneSensor] = useState(true);

  const {
    data: liveData,
    buffer,
    isAvailable: sensorAvailable,
    startRecording,
    stopRecording,
    clearBuffer,
    getStats,
    calibrate,
  } = useAccelerometer({
    samplingRate: 500,
    enabled: true,
  });

  // Initialize Bluetooth
  useEffect(() => {
    const initBluetooth = async () => {
      const available = await BluetoothService.initialize();
      if (available) {
        // Auto-scan for ESP32
        scanAndConnect();
      }
    };

    initBluetooth();

    return () => {
      BluetoothService.disconnect();
    };
  }, []);

  // Scan and connect to ESP32
  const scanAndConnect = async () => {
    setIsConnecting(true);
    try {
      const devices = await BluetoothService.scanForDevice(5000);
      
      if (devices.length > 0) {
        // Connect to first found device
        await BluetoothService.connectToDevice(devices[0].id);
        setIsConnected(true);
        
        // Subscribe to data
        await BluetoothService.subscribeToData((data) => {
          console.log('Received:', data);
          setLastMeasurement(data);
        });

        Alert.alert('Connected', `Connected to ${devices[0].name}`);
      } else {
        // Fall back to phone sensor
        setUsePhoneSensor(true);
        Alert.alert(
          'ESP32 Not Found',
          'Using phone accelerometer instead.',
          [{ text: 'OK' }]
        );
      }
    } catch (error) {
      console.error('Scan error:', error);
      setUsePhoneSensor(true);
    } finally {
      setIsConnecting(false);
    }
  };

  // Handle record button press
  const handleRecord = useCallback(async () => {
    if (isRecording) return;

    setIsRecording(true);
    clearBuffer();

    try {
      if (usePhoneSensor || !isConnected) {
        // Use phone's accelerometer
        startRecording(RECORD_DURATION);
        
        // Wait for recording to complete
        setTimeout(() => {
          const recordedData = stopRecording();
          const stats = getStats();
          
          setLastMeasurement({
            position: currentPosition,
            samples: recordedData,
            stats,
          });
          
          finishRecording();
        }, RECORD_DURATION + 50);
      } else {
        // Use ESP32
        await BluetoothService.startAcquisition(
          currentPosition,
          RECORD_DURATION,
          500
        );
        
        // Wait for data via BLE notification
        setTimeout(() => {
          finishRecording();
        }, RECORD_DURATION + 100);
      }
    } catch (error) {
      console.error('Recording error:', error);
      Alert.alert('Error', 'Failed to record. Please try again.');
      setIsRecording(false);
    }
  }, [
    isRecording,
    usePhoneSensor,
    isConnected,
    currentPosition,
    startRecording,
    stopRecording,
    clearBuffer,
    getStats,
  ]);

  // Finish recording and advance
  const finishRecording = () => {
    setIsRecording(false);
    
    // Mark position as complete
    setCompletedPositions((prev) => [...prev, currentPosition]);
    
    // Advance to next position
    if (currentPosition < TOTAL_POSITIONS) {
      setCurrentPosition((prev) => prev + 1);
    } else {
      // All positions complete
      Alert.alert(
        'Measurement Complete',
        'All positions recorded. View results?',
        [
          { text: 'Later', style: 'cancel' },
          { text: 'View Results', onPress: () => {/* Navigate to results */} },
        ]
      );
    }
  };

  // Calibrate before first measurement
  useEffect(() => {
    if (usePhoneSensor && sensorAvailable && completedPositions.length === 0) {
      Alert.alert(
        'Calibration',
        'Place phone on stable surface and keep still for 1 second.',
        [
          {
            text: 'Calibrate',
            onPress: async () => {
              await calibrate();
              Alert.alert('Calibrated', 'Ready to measure.');
            },
          },
        ]
      );
    }
  }, [usePhoneSensor, sensorAvailable, completedPositions.length, calibrate]);

  // Calculate progress
  const progress = (completedPositions.length / TOTAL_POSITIONS) * 100;

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>ShearWave Pro</Text>
        <Text style={styles.headerSubtitle}>
          {isConnected && !usePhoneSensor
            ? '🔵 Connected to ESP32'
            : '📱 Using phone sensor'}
        </Text>
        
        {isConnecting && (
          <ActivityIndicator color="white" style={styles.loader} />
        )}
      </View>

      <ProgressCard
        current={completedPositions.length}
        total={TOTAL_POSITIONS}
        progress={progress}
        estimatedTime={(TOTAL_POSITIONS - completedPositions.length) * 5}
      />

      <PositionGuide
        currentPosition={currentPosition}
        totalPositions={TOTAL_POSITIONS}
        positions={POSITIONS}
        completedPositions={completedPositions}
      />

      <RecordButton
        onPress={handleRecord}
        isRecording={isRecording}
        duration={RECORD_DURATION}
        disabled={!sensorAvailable && !isConnected}
      />

      {lastMeasurement && (
        <>
          <WaveformChart
            data={lastMeasurement.samples || buffer}
            title={`Position ${currentPosition - 1} Preview`}
          />

          <StatsPanel
            snr={lastMeasurement.stats?.snr || 0}
            peak={lastMeasurement.stats?.peak || 0}
            frequency={150} // Estimate from FFT
            quality={lastMeasurement.stats?.snr > 5 ? 'Good' : 'Fair'}
          />
        </>
      )}

      {!sensorAvailable && !isConnected && (
        <View style={styles.warningCard}>
          <Text style={styles.warningText}>
            ⚠️ No sensor available.{'\n'}
            Check Bluetooth connection or phone permissions.
          </Text>
        </View>
      )}

      <View style={styles.settingsPanel}>
        <Text style={styles.settingsTitle}>Settings</Text>
        <View style={styles.settingRow}>
          <Text>Sampling Rate</Text>
          <Text style={styles.settingValue}>500 Hz</Text>
        </View>
        <View style={styles.settingRow}>
          <Text>Record Duration</Text>
          <Text style={styles.settingValue}>{RECORD_DURATION} ms</Text>
        </View>
        <View style={styles.settingRow}>
          <Text>Positions</Text>
          <Text style={styles.settingValue}>{TOTAL_POSITIONS} (1 cm spacing)</Text>
        </View>
      </View>

      <View style={styles.bottomPadding} />
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f7',
  },
  header: {
    backgroundColor: '#667eea',
    padding: 20,
    paddingTop: 50,
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
  },
  headerSubtitle: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.8)',
    marginTop: 5,
  },
  loader: {
    marginTop: 10,
  },
  warningCard: {
    backgroundColor: '#fff3cd',
    borderLeftWidth: 4,
    borderLeftColor: '#ffc107',
    padding: 15,
    margin: 15,
    borderRadius: 8,
  },
  warningText: {
    color: '#856404',
    textAlign: 'center',
  },
  settingsPanel: {
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 20,
    margin: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  settingsTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 15,
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  settingValue: {
    color: '#667eea',
    fontWeight: '600',
  },
  bottomPadding: {
    height: 30,
  },
});

export default MeasureScreen;
