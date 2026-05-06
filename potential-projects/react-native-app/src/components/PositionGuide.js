import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Animated,
  Dimensions,
} from 'react-native';
import Svg, { Rect, Circle, Line, Text as SvgText } from 'react-native-svg';

const { width } = Dimensions.get('window');

const PositionGuide = ({ 
  currentPosition, 
  totalPositions, 
  positions,
  completedPositions = [],
}) => {
  const phantomWidth = 300;
  const phantomHeight = 100;
  const phantomX = (width - phantomWidth) / 2;
  const phantomY = 40;

  // Animation for current position
  const [pulseAnim] = useState(new Animated.Value(1));
  
  useEffect(() => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 1.2,
          duration: 750,
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1,
          duration: 750,
          useNativeDriver: true,
        }),
      ])
    ).start();
  }, []);

  const getMarkerColor = (posId) => {
    if (completedPositions.includes(posId)) return '#27ae60'; // Green
    if (posId === currentPosition) return '#e74c3c'; // Red (current)
    return '#bdc3c7'; // Gray (upcoming)
  };

  const currentPosData = positions.find(p => p.id === currentPosition);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>📍 Position Guide</Text>
      
      {/* Phantom Diagram */}
      <View style={styles.diagramContainer}>
        <Svg width={width} height={180}>
          {/* Phantom label */}
          <SvgText
            x={width / 2}
            y={20}
            textAnchor="middle"
            fontSize="12"
            fill="#666"
          >
            Gelatin Phantom (20 cm)
          </SvgText>
          
          {/* Phantom block */}
          <Rect
            x={phantomX}
            y={phantomY + 30}
            width={phantomWidth}
            height={phantomHeight}
            fill="#4a90e2"
            rx={8}
          />
          <SvgText
            x={width / 2}
            y={phantomY + 85}
            textAnchor="middle"
            fontSize="14"
            fill="white"
            fontWeight="bold"
          >
            Tissue Phantom
          </SvgText>
          
          {/* Position markers */}
          {positions.map((pos) => {
            const markerX = phantomX + (pos.x / 100) * phantomWidth;
            const isCurrent = pos.id === currentPosition;
            const isCompleted = completedPositions.includes(pos.id);
            
            return (
              <React.Fragment key={pos.id}>
                {/* Marker line */}
                <Line
                  x1={markerX}
                  y1={phantomY + 20}
                  x2={markerX}
                  y2={phantomY + 30}
                  stroke={getMarkerColor(pos.id)}
                  strokeWidth={2}
                />
                
                {/* Position marker */}
                {isCurrent ? (
                  <AnimatedCircle
                    cx={markerX}
                    cy={phantomY}
                    r={15}
                    fill={getMarkerColor(pos.id)}
                    scale={pulseAnim}
                  />
                ) : (
                  <Circle
                    cx={markerX}
                    cy={phantomY}
                    r={isCompleted ? 12 : 10}
                    fill={getMarkerColor(pos.id)}
                  />
                )}
                
                {/* Position label */}
                <SvgText
                  x={markerX}
                  y={phantomY + 5}
                  textAnchor="middle"
                  fontSize="10"
                  fill="white"
                  fontWeight="bold"
                >
                  {isCompleted ? '✓' : pos.id}
                </SvgText>
              </React.Fragment>
            );
          })}
          
          {/* Scale markers */}
          {[0, 5, 10, 15, 20].map((cm) => (
            <SvgText
              key={cm}
              x={phantomX + (cm / 20) * phantomWidth}
              y={phantomY + 150}
              textAnchor="middle"
              fontSize="10"
              fill="#666"
            >
              {cm}cm
            </SvgText>
          ))}
        </Svg>
      </View>
      
      {/* Position Info Card */}
      <View style={styles.infoCard}>
        <Text style={styles.infoTitle}>
          Position {currentPosition} of {totalPositions}
        </Text>
        <Text style={styles.infoText}>
          Place phone at <Text style={styles.highlight}>{currentPosData?.cm} cm</Text> from left edge.{'\n'}
          Ensure good contact with silicone pad.
        </Text>
      </View>
    </View>
  );
};

// Animated circle component
const AnimatedCircle = Animated.createAnimatedComponent(Circle);

const styles = StyleSheet.create({
  container: {
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 20,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 15,
    color: '#1a1a1a',
  },
  diagramContainer: {
    backgroundColor: '#f0f0f0',
    borderRadius: 12,
    overflow: 'hidden',
  },
  infoCard: {
    backgroundColor: '#fff3cd',
    borderLeftWidth: 4,
    borderLeftColor: '#ffc107',
    padding: 15,
    borderRadius: 0,
    borderTopRightRadius: 8,
    borderBottomRightRadius: 8,
    marginTop: 15,
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#856404',
    marginBottom: 5,
  },
  infoText: {
    fontSize: 14,
    color: '#856404',
    lineHeight: 20,
  },
  highlight: {
    fontWeight: 'bold',
  },
});

export default PositionGuide;
