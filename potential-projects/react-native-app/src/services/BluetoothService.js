import { BleManager } from 'react-native-ble-plx';
import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

// BLE UUIDs (must match ESP32 firmware)
const SHEARWAVE_SERVICE_UUID = '4fafc201-1fb5-459e-8fcc-c5c9c331914b';
const ACCEL_DATA_CHAR_UUID = 'beb5483e-36e1-4688-b7f5-ea07361b26a8';
const COMMAND_CHAR_UUID = '00002a52-0000-1000-8000-00805f9b34fb';
const STATUS_CHAR_UUID = '00002a3b-0000-1000-8000-00805f9b34fb';

class BluetoothService {
  constructor() {
    this.manager = new BleManager();
    this.device = null;
    this.isConnected = false;
    this.dataSubscription = null;
    this.statusSubscription = null;
    this.offlineQueue = [];
  }

  // Initialize and check Bluetooth state
  async initialize() {
    const state = await this.manager.state();
    
    if (state === 'PoweredOff') {
      await this.manager.enable();
    }
    
    // Load offline queue
    const queue = await AsyncStorage.getItem('bleQueue');
    if (queue) {
      this.offlineQueue = JSON.parse(queue);
    }

    return state === 'PoweredOn';
  }

  // Scan for ESP32 device
  async scanForDevice(timeout = 10000) {
    return new Promise((resolve, reject) => {
      const devices = new Map();
      
      const subscription = this.manager.onStateChange((state) => {
        if (state === 'PoweredOn') {
          this.manager.startDeviceScan(
            null,  // Scan all services
            null,  // Default scan options
            (error, device) => {
              if (error) {
                reject(error);
                return;
              }

              // Look for ESP32 by name or service UUID
              if (device && (
                device.name?.includes('ShearWave') ||
                device.name?.includes('ESP32')
              )) {
                devices.set(device.id, device);
              }

              // Check service UUID (requires connection, so we filter by name first)
            }
          );

          // Stop scan after timeout
          setTimeout(() => {
            this.manager.stopDeviceScan();
            subscription.remove();
            resolve(Array.from(devices.values()));
          }, timeout);
        }
      }, true);
    });
  }

  // Connect to device
  async connectToDevice(deviceId) {
    try {
      const device = await this.manager.connectToDevice(deviceId, {
        autoConnect: false,
        timeout: 5000,
      });

      await device.discoverAllServicesAndCharacteristics();

      this.device = device;
      this.isConnected = true;

      // Monitor disconnection
      device.onDisconnected((error) => {
        console.log('Disconnected:', error);
        this.isConnected = false;
        this.device = null;
      });

      return device;
    } catch (error) {
      console.error('Connection error:', error);
      throw error;
    }
  }

  // Send command to ESP32
  async sendCommand(command) {
    if (!this.isConnected || !this.device) {
      // Queue for later if offline
      this.offlineQueue.push({
        type: 'command',
        data: command,
        timestamp: Date.now(),
      });
      await this.saveQueue();
      return false;
    }

    try {
      const jsonCommand = JSON.stringify(command);
      const base64Command = btoa(jsonCommand);

      await this.device.writeCharacteristicWithResponseForService(
        SHEARWAVE_SERVICE_UUID,
        COMMAND_CHAR_UUID,
        base64Command
      );

      return true;
    } catch (error) {
      console.error('Command error:', error);
      // Queue on failure
      this.offlineQueue.push({
        type: 'command',
        data: command,
        timestamp: Date.now(),
      });
      await this.saveQueue();
      return false;
    }
  }

  // Start acquisition on ESP32
  async startAcquisition(position, duration = 100, sampleRate = 500) {
    return this.sendCommand({
      cmd: 'START_ACQUISITION',
      position,
      duration,
      sampleRate,
    });
  }

  // Stop acquisition
  async stopAcquisition() {
    return this.sendCommand({
      cmd: 'STOP',
    });
  }

  // Subscribe to accelerometer data
  async subscribeToData(onDataReceived) {
    if (!this.isConnected || !this.device) {
      throw new Error('Not connected');
    }

    this.dataSubscription = this.device.monitorCharacteristicForService(
      SHEARWAVE_SERVICE_UUID,
      ACCEL_DATA_CHAR_UUID,
      (error, characteristic) => {
        if (error) {
          console.error('Data subscription error:', error);
          return;
        }

        if (characteristic?.value) {
          try {
            const jsonString = atob(characteristic.value);
            const data = JSON.parse(jsonString);
            onDataReceived(data);
          } catch (e) {
            console.error('Parse error:', e);
          }
        }
      }
    );

    return this.dataSubscription;
  }

  // Subscribe to status updates
  async subscribeToStatus(onStatusUpdate) {
    if (!this.isConnected || !this.device) {
      throw new Error('Not connected');
    }

    this.statusSubscription = this.device.monitorCharacteristicForService(
      SHEARWAVE_SERVICE_UUID,
      STATUS_CHAR_UUID,
      (error, characteristic) => {
        if (error) {
          console.error('Status subscription error:', error);
          return;
        }

        if (characteristic?.value) {
          try {
            const jsonString = atob(characteristic.value);
            const status = JSON.parse(jsonString);
            onStatusUpdate(status);
          } catch (e) {
            console.error('Parse error:', e);
          }
        }
      }
    );

    return this.statusSubscription;
  }

  // Unsubscribe from data
  unsubscribeFromData() {
    if (this.dataSubscription) {
      this.dataSubscription.remove();
      this.dataSubscription = null;
    }
  }

  // Unsubscribe from status
  unsubscribeFromStatus() {
    if (this.statusSubscription) {
      this.statusSubscription.remove();
      this.statusSubscription = null;
    }
  }

  // Disconnect
  async disconnect() {
    if (this.device) {
      await this.device.cancelConnection();
      this.device = null;
      this.isConnected = false;
    }
  }

  // Save offline queue
  async saveQueue() {
    await AsyncStorage.setItem('bleQueue', JSON.stringify(this.offlineQueue));
  }

  // Process offline queue
  async processQueue() {
    if (!this.isConnected || this.offlineQueue.length === 0) {
      return;
    }

    const queue = [...this.offlineQueue];
    this.offlineQueue = [];

    for (const item of queue) {
      if (item.type === 'command') {
        await this.sendCommand(item.data);
      }
    }

    await this.saveQueue();
  }

  // Get connection status
  getStatus() {
    return {
      isConnected: this.isConnected,
      deviceName: this.device?.name,
      deviceId: this.device?.id,
      queueLength: this.offlineQueue.length,
    };
  }

  // Destroy manager
  destroy() {
    this.unsubscribeFromData();
    this.unsubscribeFromStatus();
    this.disconnect();
    this.manager.destroy();
  }
}

// Export singleton instance
export default new BluetoothService();
