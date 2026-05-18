/**
 * GlassHouse Tomatoes — Mobile App
 * ================================
 * React Native (Expo) app for monitoring glasshouse soil conditions.
 */

import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { StatusBar } from 'expo-status-bar';
import { Text, View, StyleSheet } from 'react-native';

// Placeholder screens — replace with real implementations
function DashboardScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>GlassHouse Dashboard</Text>
      <Text style={styles.subtitle}>Connect to your backend to see live data</Text>
    </View>
  );
}

function HistoryScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>History</Text>
      <Text style={styles.subtitle}>Charts will appear here</Text>
    </View>
  );
}

function NodesScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Nodes</Text>
      <Text style={styles.subtitle}>Manage your sensor nodes</Text>
    </View>
  );
}

function AlertsScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Alerts</Text>
      <Text style={styles.subtitle}>Configure notification rules</Text>
    </View>
  );
}

const Tab = createBottomTabNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <StatusBar style="auto" />
      <Tab.Navigator
        screenOptions={{
          headerStyle: { backgroundColor: '#2E7D32' },
          headerTintColor: '#fff',
          tabBarActiveTintColor: '#2E7D32',
        }}
      >
        <Tab.Screen name="Dashboard" component={DashboardScreen} />
        <Tab.Screen name="History" component={HistoryScreen} />
        <Tab.Screen name="Nodes" component={NodesScreen} />
        <Tab.Screen name="Alerts" component={AlertsScreen} />
      </Tab.Navigator>
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f5f5f5',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#1b5e20',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
});
