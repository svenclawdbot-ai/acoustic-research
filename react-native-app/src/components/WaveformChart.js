import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const WaveformChart = ({ data, title }) => {
  // Simple waveform visualization
  // In production, use react-native-chart-kit or react-native-svg
  
  const maxVal = Math.max(...data.map(d => Math.abs(d.x || 0))) || 1;
  
  return (
    <View style={styles.container}>
      <Text style={styles.title}>{title}</Text>
      
      <View style={styles.chartContainer}>
        <View style={styles.waveformLine}>
          {data.slice(0, 50).map((point, i) => {
            const height = ((point.x || 0) / maxVal) * 40 + 40;
            return (
              <View
                key={i}
                style={[
                  styles.bar,
                  {
                    height: Math.abs(height - 40),
                    backgroundColor: height > 40 ? '#667eea' : '#764ba2',
                    bottom: height > 40 ? 40 : height,
                  },
                ]}
              />
            );
          })}
        </View>
        <View style={styles.centerLine} />
      </View>
      
      <Text style={styles.samples}>{data.length} samples</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
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
  title: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 10,
    color: '#1a1a1a',
  },
  chartContainer: {
    height: 100,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    position: 'relative',
    overflow: 'hidden',
  },
  waveformLine: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    height: '100%',
    paddingHorizontal: 5,
  },
  bar: {
    width: 4,
    marginHorizontal: 1,
    borderRadius: 2,
  },
  centerLine: {
    position: 'absolute',
    left: 0,
    right: 0,
    top: '50%',
    height: 1,
    backgroundColor: '#ddd',
  },
  samples: {
    fontSize: 12,
    color: '#666',
    marginTop: 8,
    textAlign: 'center',
  },
});

export default WaveformChart;
