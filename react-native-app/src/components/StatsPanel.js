import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const StatsPanel = ({ snr, peak, frequency, quality }) => {
  const getQualityColor = () => {
    if (quality === 'Good') return '#27ae60';
    if (quality === 'Fair') return '#f39c12';
    return '#e74c3c';
  };

  return (
    <View style={styles.container}>
      <View style={styles.grid}>
        <View style={styles.statBox}>
          <Text style={styles.statValue}>{snr.toFixed(1)}</Text>
          <Text style={styles.statLabel}>SNR (dB)</Text>
        </View>
        
        <View style={styles.statBox}>
          <Text style={styles.statValue}>{(peak * 1000).toFixed(1)}</Text>
          <Text style={styles.statLabel}>Peak (mg)</Text>
        </View>
        
        <View style={styles.statBox}>
          <Text style={styles.statValue}>{Math.round(frequency)}</Text>
          <Text style={styles.statLabel}>Freq (Hz)</Text>
        </View>
        
        <View style={[styles.statBox, { borderColor: getQualityColor() }]}>
          <Text style={[styles.statValue, { color: getQualityColor() }]}>
            {quality === 'Good' ? '✓' : quality === 'Fair' ? '~' : '✗'}
          </Text>
          <Text style={styles.statLabel}>Quality</Text>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 15,
    margin: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  grid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  statBox: {
    backgroundColor: '#f8f9fa',
    borderRadius: 12,
    padding: 15,
    alignItems: 'center',
    minWidth: 70,
    borderWidth: 2,
    borderColor: 'transparent',
  },
  statValue: {
    fontSize: 20,
    fontWeight: '700',
    color: '#667eea',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 11,
    color: '#666',
  },
});

export default StatsPanel;
