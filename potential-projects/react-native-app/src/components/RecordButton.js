import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Animated } from 'react-native';

const RecordButton = ({ 
  onPress, 
  isRecording, 
  duration = 100,
  disabled = false,
}) => {
  const [progress, setProgress] = useState(0);
  const [pulseAnim] = useState(new Animated.Value(1));

  // Recording animation
  useEffect(() => {
    if (isRecording) {
      // Progress animation
      const interval = setInterval(() => {
        setProgress(p => {
          if (p >= 100) {
            clearInterval(interval);
            return 100;
          }
          return p + (100 / (duration / 10)); // Update every 10ms
        });
      }, 10);

      // Pulse animation
      Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 0.8,
            duration: 500,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 1,
            duration: 500,
            useNativeDriver: true,
          }),
        ])
      ).start();

      return () => {
        clearInterval(interval);
        pulseAnim.stopAnimation();
      };
    } else {
      setProgress(0);
      pulseAnim.setValue(1);
    }
  }, [isRecording, duration, pulseAnim]);

  const getButtonText = () => {
    if (isRecording) {
      return `⏹️ Recording... (${Math.ceil(duration - (progress / 100) * duration)}ms)`;
    }
    return `🔴 Start Recording (${duration}ms)`;
  };

  const getButtonStyle = () => {
    if (isRecording) {
      return [styles.button, styles.recording];
    }
    if (disabled) {
      return [styles.button, styles.disabled];
    }
    return styles.button;
  };

  return (
    <View style={styles.container}>
      <Animated.View
        style={[
          styles.buttonContainer,
          { transform: [{ scale: isRecording ? pulseAnim : 1 }] },
        ]}
      >
        <TouchableOpacity
          style={getButtonStyle()}
          onPress={onPress}
          disabled={disabled || isRecording}
          activeOpacity={0.8}
        >
          <Text style={styles.buttonText}>{getButtonText()}</Text>
        </TouchableOpacity>
      </Animated.View>

      {/* Progress bar */}
      {isRecording && (
        <View style={styles.progressContainer}>
          <View style={[styles.progressBar, { width: `${progress}%` }]} />
        </View>
      )}

      {/* Status text */}
      {isRecording && (
        <Text style={styles.statusText}>
          Keep phone steady...
        </Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: 15,
  },
  buttonContainer: {
    borderRadius: 12,
    overflow: 'hidden',
  },
  button: {
    backgroundColor: '#667eea',
    paddingVertical: 18,
    paddingHorizontal: 30,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#667eea',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 5,
  },
  recording: {
    backgroundColor: '#e74c3c',
    shadowColor: '#e74c3c',
  },
  disabled: {
    backgroundColor: '#bdc3c7',
    shadowColor: 'transparent',
  },
  buttonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: '600',
  },
  progressContainer: {
    height: 4,
    backgroundColor: '#e0e0e0',
    borderRadius: 2,
    marginTop: 10,
    overflow: 'hidden',
  },
  progressBar: {
    height: '100%',
    backgroundColor: '#e74c3c',
    borderRadius: 2,
  },
  statusText: {
    textAlign: 'center',
    color: '#666',
    fontSize: 14,
    marginTop: 8,
  },
});

export default RecordButton;
