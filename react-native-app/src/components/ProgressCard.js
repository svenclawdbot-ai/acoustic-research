import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const ProgressCard = ({ current, total, progress, estimatedTime }) => {
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Measurement Progress</Text>
        <View style={styles.countBadge}>
          <Text style={styles.countText}>{current}/{total}</Text>
        </View>
      </View>
      
      <View style={styles.progressBar}>
        <View style={[styles.progressFill, { width: `${progress}%` }]} />
      </View>
      
      <Text style={styles.estimate}>
        Estimated time remaining: ~{estimatedTime} seconds
      </Text>
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
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1a1a1a',
  },
  countBadge: {
    backgroundColor: '#667eea',
    paddingHorizontal: 12,
    paddingVertical: 5,
    borderRadius: 20,
  },
  countText: {
    color: 'white',
    fontWeight: '600',
    fontSize: 14,
  },
  progressBar: {
    height: 8,
    backgroundColor: '#e0e0e0',
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: 10,
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#667eea',
    borderRadius: 4,
  },
  estimate: {
    fontSize: 13,
    color: '#666',
  },
});

export default ProgressCard;
