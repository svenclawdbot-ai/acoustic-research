# Required Arduino Libraries

Install these via Arduino IDE Library Manager (Sketch → Include Library → Manage Libraries):

| Library | Version | Author | Search Term |
|---------|---------|--------|-------------|
| **WiFiManager** | ^2.0.17 | tzapu | "WiFiManager" |
| **PubSubClient** | ^2.8 | Nick O'Leary | "PubSubClient" |
| **ArduinoJson** | ^6.21 | Benoît Blanchon | "ArduinoJson" |
| **DallasTemperature** | ^3.11 | Miles Burton | "DallasTemperature" |
| **OneWire** | ^2.3 | Paul Stoffregen | "OneWire" |

### ESP32 Board Package
Add to Arduino IDE Preferences → Additional Board Manager URLs:
```
https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
```

Then install **"ESP32 by Espressif Systems"** version **>= 3.0.0** via Boards Manager.

### Board Selection
- **Board:** "ESP32S3 Dev Module"
- **Port:** Your USB-C COM port
- **Upload Speed:** 921600
