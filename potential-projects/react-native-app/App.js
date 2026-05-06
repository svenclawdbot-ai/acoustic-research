import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Text, View } from 'react-native';

import MeasureScreen from './src/screens/MeasureScreen';

// Placeholder screens
const ResultsScreen = () => (
  <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
    <Text>Results Screen</Text>
    <Text>Dispersion curves and analysis</Text>
  </View>
);

const SettingsScreen = () => (
  <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
    <Text>Settings Screen</Text>
    <Text>Configuration options</Text>
  </View>
);

const Tab = createBottomTabNavigator();

const App = () => {
  return (
    <NavigationContainer>
      <Tab.Navigator
        screenOptions={({ route }) => ({
          tabBarIcon: ({ focused, color, size }) => {
            let icon;
            
            if (route.name === 'Measure') {
              icon = '📊';
            } else if (route.name === 'Results') {
              icon = '📈';
            } else if (route.name === 'Settings') {
              icon = '⚙️';
            }
            
            return <Text style={{ fontSize: size }}>{icon}</Text>;
          },
          tabBarActiveTintColor: '#667eea',
          tabBarInactiveTintColor: 'gray',
          headerShown: false,
        })}
      >
        <Tab.Screen name="Measure" component={MeasureScreen} />
        <Tab.Screen name="Results" component={ResultsScreen} />
        <Tab.Screen name="Settings" component={SettingsScreen} />
      </Tab.Navigator>
    </NavigationContainer>
  );
};

export default App;
