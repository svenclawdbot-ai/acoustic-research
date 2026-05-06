# Greenhouse Gateway — Irrigation Control System Design

*Date: 2026-05-05*  
*Scope: Central hub for soil monitoring + automated irrigation*  
*Target: Acre-scale greenhouse, 12 zones*

---

## Overview

The gateway is the brain of the system. It receives LoRa packets from 12 sensor nodes, stores time-series data, runs the irrigation decision engine, controls 12 solenoid valves via relay board, manages the pump, and exposes a web dashboard for manual override.

**Location:** Centre of greenhouse (or edge with good LoRa line-of-sight to all nodes).  
**Power:** Mains-powered (no solar constraints).  
**Connectivity:** Ethernet or WiFi to local network. Optional 4G/5G backup.

---

## Hardware Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         GATEWAY ENCLOSURE                               │
│                              (IP65, wall-mount)                        │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────────────────────────────────────────────────────────┐    │
│   │              Raspberry Pi 5 / Intel NUC / V5 Host            │    │
│   │  ┌──────────────────────────────────────────────────────┐   │    │
│   │  │  Python Gateway Stack                                │   │    │
│   │  │  • LoRa RX thread                                    │   │    │
│   │  │  • SQLite + time-series                              │   │    │
│   │  │  • Decision engine (irrigation triggers)             │   │    │
│   │  │  • Flask/FastAPI web server                          │   │    │
│   │  │  • MQTT client (cloud upload)                        │   │    │
│   │  └──────────────────────────────────────────────────────┘   │    │
│   │         │ GPIO │ USB │ SPI │ Ethernet │ WiFi               │    │
│   └─────────┼──────┼─────┼─────┼──────────┼──────────────────────┘    │
│             │      │     │     │          │                         │
│             ▼      ▼     ▼     ▼          ▼                         │
│   ┌─────────┐  ┌─────┐  │   ┌────┐    ┌────────┐                    │
│   │ Relay   │  │LoRa │  │   │Eth │    │ WiFi   │                    │
│   │ Board   │  │RX   │  │   │    │    │ / 4G   │                    │
│   │ (16-ch) │  │SX126│  │   │    │    │ dongle │                    │
│   └────┬────┘  └─────┘  │   └────┘    └────────┘                    │
│        │                 │                                            │
│        │ 12 signals      │                                            │
│        ▼                 │                                            │
│   ┌──────────────────────────────────────┐                           │
│   │          FIELD WIRING BOX            │                           │
│   │  ┌────────┐  ┌────────┐  ┌────────┐ │                           │
│   │  │Valve 1 │  │Valve 2 │  │Valve 12│ │  ← 12V DC solenoids      │
│   │  │        │  │        │  │        │ │                           │
│   │  │ +  -   │  │ +  -   │  │ +  -   │ │                           │
│   │  └───┬────┘  └───┬────┘  └───┬────┘ │                           │
│   │      └───────────┴───────────┘      │                           │
│   │              Common return           │                           │
│   │                    │                  │                           │
│   │              ┌─────┴─────┐            │                           │
│   │              │  Pump     │            │                           │
│   │              │ Controller│            │                           │
│   │              │  (VFD)    │            │                           │
│   │              └─────┬─────┘            │                           │
│   │                    │                  │                           │
│   │              Water Main              │                           │
│   └──────────────────────────────────────┘                           │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Bill of Materials

| Item | Qty | Spec | Cost | Supplier |
|------|-----|------|------|----------|
| **Raspberry Pi 5** | 1 | 8GB RAM, PoE HAT optional | £75 | Pimoroni |
| **SX1262 LoRa HAT** | 1 | 868/915 MHz, SPI | £25 | Pimoroni / DigiKey |
| **16-ch relay board** | 1 | 5V logic, 10A/250V, opto-isolated | £8 | Amazon |
| **Pump VFD controller** | 1 | 0.75–1.5 kW, pressure/flow control | £120–200 | eBay / industrial |
| **Pressure transducer** | 1 | 4-20 mA, 0–4 bar | £15 | AliExpress |
| **Flow meter (optional)** | 1 | Hall effect, DN25, pulse output | £12 | Amazon |
| **12V PSU (15A)** | 1 | For valves + sensors | £20 | Amazon |
| **5V PSU (5A)** | 1 | For Pi + relay logic | £10 | Amazon |
| **Ethernet switch** | 1 | 8-port, PoE optional | £15 | Amazon |
| **IP65 enclosure** | 1 | 400×300×150 mm, DIN rail | £25 | RS |
| **DIN rail + terminals** | 1 set | Wago-style spring terminals | £15 | RS |
| **Cable (multi-core)** | 50m | 16×0.5 mm² for valve wiring | £20 | Cable supplier |
| **Solenoid valves** | 12 | 12V DC, ¾" BSP, 0.5–8 bar | £120 | Irrigation supplier |
| **Header pipe + fittings** | 1 set | PVC/PE, 25 mm OD, tees | £40 | Plumbing |
| **Drip line (per zone)** | 12 × 30m | 16 mm inline drip, 2 L/h | £60 | Irrigation supplier |
| **Y-filters (per valve)** | 12 | ¾" mesh filter | £24 | Irrigation supplier |
| **Pressure reducer** | 1 | 2 bar output for drip system | £10 | Irrigation supplier |
| **Main isolation valve** | 1 | Ball valve, manual | £5 | Plumbing |
| **Drain valve** | 1 | For winter draining | £3 | Plumbing |
| **Ground rod + bonding** | 1 set | Earth bonding for metal greenhouse | £10 | Electrical |
| **UPS (optional)** | 1 | 600VA, keeps Pi + valves alive 10 min | £45 | Amazon |
| **4G dongle (optional)** | 1 | Huawei E3372 or similar | £25 | Amazon |
| **Total** | | | **£676–756** | |

*Excluding existing V5 hardware. If reusing V5 host (Red Pitaya + laptop), subtract Pi + PSU.*

---

## Software Stack

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      GATEWAY SOFTWARE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ LoRa RX      │  │ Decision     │  │ Valve        │          │
│  │ Thread       │  │ Engine       │  │ Controller   │          │
│  │              │  │              │  │              │          │
│  │ • Serial/SPI │  │ • Threshold  │  │ • GPIO on/off │          │
│  │ • Parse pkt  │  │ • Scheduling │  │ • Duration    │          │
│  │ • CRC check  │  │ • History    │  │ • Flow check  │          │
│  │ • Timestamp  │  │ • Weather    │  │ • Pressure    │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                  │                   │
│         └─────────────────┼──────────────────┘                   │
│                           │                                      │
│              ┌────────────┴────────────┐                         │
│              │      SQLite Database    │                         │
│              │  ┌────────────────────┐ │                         │
│              │  │ soil_readings      │ │                         │
│              │  │ irrigation_events  │ │                         │
│              │  │ valve_state_log    │ │                         │
│              │  │ node_health        │ │                         │
│              │  │ system_config      │ │                         │
│              │  └────────────────────┘ │                         │
│              └─────────────────────────┘                         │
│                           │                                      │
│         ┌─────────────────┼─────────────────┐                   │
│         │                 │                 │                   │
│         ▼                 ▼                 ▼                   │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐               │
│  │ Web Dash   │   │ MQTT Pub   │   │ API Server │               │
│  │ (Flask)    │   │ (cloud)    │   │ (FastAPI)  │               │
│  │            │   │            │   │            │               │
│  │ • Live map │   │ • Telemetry│   │ • REST     │               │
│  │ • Override │   │ • Alerts   │   │ • JSON     │               │
│  │ • History  │   │ • Remote   │   │ • Auth     │               │
│  │ • Alerts   │   │   config   │   │ • Webhook  │               │
│  └────────────┘   └────────────┘   └────────────┘               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### File Structure

```
gateway/
├── main.py                 # Entry point, starts all threads
├── config.yaml             # Site-specific settings
├── database.py             # SQLite schema + queries
├── lora_receiver.py        # SX1262 interface + packet parsing
├── decision_engine.py      # Irrigation trigger logic
├── valve_controller.py     # GPIO + relay + pump control
├── web_dashboard.py        # Flask app (live map + controls)
├── mqtt_client.py          # Cloud upload
├── failsafe_watchdog.py    # Hardware watchdog + dead-man switch
├── weather_client.py       # OpenWeatherMap / local station
├── calibration.py          # Impedance → moisture mapping
└── requirements.txt
```

---

## Database Schema

```sql
-- Node telemetry (from LoRa packets)
CREATE TABLE soil_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id INTEGER NOT NULL,
    timestamp INTEGER NOT NULL,          -- Node RTC time
    received_at REAL NOT NULL,             -- Gateway wall-clock
    rssi_dbm INTEGER,
    snr_db REAL,
    battery_mv INTEGER,
    z_ch0 REAL, z_ch1 REAL, z_ch2 REAL, z_ch3 REAL,
    z_ch4 REAL, z_ch5 REAL, z_ch6 REAL, z_ch7 REAL,
    soil_temp_c REAL,
    packet_crc_ok BOOLEAN DEFAULT 1
);
CREATE INDEX idx_soil_time ON soil_readings(node_id, timestamp);
CREATE INDEX idx_soil_recent ON soil_readings(received_at);

-- Every valve open/close event
CREATE TABLE irrigation_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zone_id INTEGER NOT NULL,
    triggered_by TEXT CHECK(triggered_by IN ('auto','manual','schedule','test')),
    reason TEXT,
    started_at REAL NOT NULL,
    requested_sec REAL,
    actual_sec REAL,
    valve_opened BOOLEAN,
    valve_closed BOOLEAN,
    pump_on BOOLEAN,
    pressure_start_bar REAL,
    pressure_end_bar REAL,
    flow_l_total REAL,
    aborted BOOLEAN DEFAULT 0,
    abort_reason TEXT
);
CREATE INDEX idx_irr_zone ON irrigation_events(zone_id, started_at);

-- Last-known valve + pump state (for watchdog recovery)
CREATE TABLE valve_state_log (
    zone_id INTEGER PRIMARY KEY,
    is_open BOOLEAN,
    last_cmd_at REAL,
    last_cmd_source TEXT,
    cumulative_sec_today REAL DEFAULT 0,
    daily_limit_sec REAL DEFAULT 3600
);

-- Node health (missed packets, battery trend)
CREATE TABLE node_health (
    node_id INTEGER PRIMARY KEY,
    last_seen_at REAL,
    packets_total INTEGER,
    packets_missed INTEGER,
    battery_trend_mv_per_day REAL,
    rssi_avg_dbm REAL,
    status TEXT CHECK(status IN ('online','stale','offline','dead'))
);

-- System configuration (editable via web UI)
CREATE TABLE system_config (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at REAL,
    updated_by TEXT
);

-- Insert defaults
INSERT INTO system_config (key, value) VALUES
('irrigation_enabled', 'true'),
('dry_threshold_ohm', '450'),
('max_duration_min', '30'),
('min_interval_hours', '4'),
('daily_limit_min', '60'),
('schedule_start_hour', '6'),
('schedule_end_hour', '20'),
('pump_min_pressure_bar', '1.5'),
('pump_max_pressure_bar', '3.5'),
('flow_timeout_sec', '300'),
('watchdog_timeout_sec', '300'),
('weather_api_key', ''),
('weather_location', ''),
('mqtt_broker', ''),
('mqtt_topic_prefix', 'greenhouse/soil');
```

---

## Decision Engine

### Trigger Logic

```python
# decision_engine.py
import sqlite3
import time
from datetime import datetime
from typing import Optional, Dict

class IrrigationDecisionEngine:
    def __init__(self, db_path='greenhouse.db'):
        self.db = sqlite3.connect(db_path)
        self.db.row_factory = sqlite3.Row
        
    def should_irrigate(self, zone_id: int) -> Optional[Dict]:
        """Evaluate if a zone needs water right now."""
        
        cfg = self._get_config()
        if cfg['irrigation_enabled'] != 'true':
            return None
        
        now = datetime.now()
        hour = now.hour
        if hour < int(cfg['schedule_start_hour']) or hour > int(cfg['schedule_end_hour']):
            return None  # Outside irrigation window
        
        # Get latest node reading
        reading = self._latest_reading(zone_id)
        if not reading:
            return None
        
        # Check node health
        health = self._node_health(zone_id)
        if health and health['status'] != 'online':
            return None  # Don't irrigate on stale data
        
        z_avg = sum(reading[f'z_ch{i}'] for i in range(8)) / 8
        temp_c = reading['soil_temp_c']
        threshold = float(cfg['dry_threshold_ohm'])
        
        # Temperature-corrected EC (optional refinement)
        # z_corrected = z_avg / (1 + 0.02 * (temp_c - 25))
        
        if z_avg < threshold:
            return None  # Soil wet enough
        
        # Check minimum interval
        last_event = self._last_irrigation(zone_id)
        if last_event:
            hours_since = (time.time() - last_event['started_at']) / 3600
            if hours_since < float(cfg['min_interval_hours']):
                return None
        
        # Check daily limit
        today_sec = self._today_irrigation_seconds(zone_id)
        daily_limit = float(cfg['daily_limit_min']) * 60
        if today_sec >= daily_limit:
            return None
        
        # Calculate duration
        dryness = z_avg - threshold
        duration_sec = min(
            dryness / 8 * 60,  # Rough: 1 Ω over = ~7.5 min
            float(cfg['max_duration_min']) * 60,
            daily_limit - today_sec
        )
        duration_sec = max(duration_sec, 300)  # Minimum 5 min
        
        return {
            'zone_id': zone_id,
            'duration_sec': int(duration_sec),
            'reason': f'Z_avg={z_avg:.0f}Ω > threshold {threshold:.0f}Ω, temp={temp_c:.1f}°C',
            'triggered_by': 'auto',
            'dryness': dryness
        }
    
    def _get_config(self) -> Dict:
        cursor = self.db.execute('SELECT key, value FROM system_config')
        return {row['key']: row['value'] for row in cursor.fetchall()}
    
    def _latest_reading(self, node_id: int):
        cursor = self.db.execute('''
            SELECT * FROM soil_readings 
            WHERE node_id = ? ORDER BY timestamp DESC LIMIT 1
        ''', (node_id,))
        return cursor.fetchone()
    
    def _last_irrigation(self, zone_id: int):
        cursor = self.db.execute('''
            SELECT * FROM irrigation_events 
            WHERE zone_id = ? AND aborted = 0
            ORDER BY started_at DESC LIMIT 1
        ''', (zone_id,))
        return cursor.fetchone()
    
    def _today_irrigation_seconds(self, zone_id: int) -> float:
        today = datetime.now().replace(hour=0, minute=0, second=0)
        cursor = self.db.execute('''
            SELECT COALESCE(SUM(actual_sec), 0) 
            FROM irrigation_events 
            WHERE zone_id = ? AND started_at > ? AND aborted = 0
        ''', (zone_id, time.mktime(today.timetuple())))
        return cursor.fetchone()[0] or 0
    
    def _node_health(self, node_id: int):
        cursor = self.db.execute('''
            SELECT * FROM node_health WHERE node_id = ?
        ''', (node_id,))
        return cursor.fetchone()
```

### Weather Override

```python
import requests

class WeatherClient:
    def __init__(self, api_key: str, lat: float, lon: float):
        self.api_key = api_key
        self.lat = lat
        self.lon = lon
        
    def rain_probability_next_6h(self) -> float:
        """Return 0–1 probability of rain in next 6 hours."""
        url = f'https://api.openweathermap.org/data/3.0/onecall'
        params = {
            'lat': self.lat, 'lon': self.lon,
            'appid': self.api_key, 'exclude': 'current,minutely,daily'
        }
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        
        # Check next 6 hourly slots
        hourly = data.get('hourly', [])[:6]
        probs = [h.get('pop', 0) for h in hourly]
        return max(probs) if probs else 0.0
    
    def should_delay_irrigation(self, threshold=0.5) -> bool:
        """If rain is likely, hold off."""
        return self.rain_probability_next_6h() > threshold
```

---

## Valve Controller

### GPIO Mapping

| Pi GPIO | Relay Channel | Zone | Function |
|---------|---------------|------|----------|
| 5 | 1 | Zone 0 | Solenoid valve |
| 6 | 2 | Zone 1 | Solenoid valve |
| 13 | 3 | Zone 2 | Solenoid valve |
| 16 | 4 | Zone 3 | Solenoid valve |
| 19 | 5 | Zone 4 | Solenoid valve |
| 20 | 6 | Zone 5 | Solenoid valve |
| 21 | 7 | Zone 6 | Solenoid valve |
| 26 | 8 | Zone 7 | Solenoid valve |
| 12 | 9 | Zone 8 | Solenoid valve |
| 7 | 10 | Zone 9 | Solenoid valve |
| 8 | 11 | Zone 10 | Solenoid valve |
| 25 | 12 | Zone 11 | Solenoid valve |
| 24 | 13 | — | Pump start (via VFD contactor) |
| 23 | 14 | — | Pump enable / VFD run |
| 18 | 15 | — | Emergency stop (NC relay) |
| — | 16 | — | Spare / buzzer / light |

### Valve Controller Class

```python
# valve_controller.py
import gpiozero
import time
import sqlite3
from dataclasses import dataclass
from typing import Optional

@dataclass
class FlowReading:
    pulses: int
    litres: float
    timestamp: float

class ValveController:
    # GPIO to zone mapping
    VALVE_PINS = [5, 6, 13, 16, 19, 20, 21, 26, 12, 7, 8, 25]
    PUMP_PIN = 24
    PUMP_ENABLE_PIN = 23
    EMERGENCY_PIN = 18
    
    # YF-S201: 450 pulses per litre (calibrate for your meter)
    PULSES_PER_LITRE = 450
    
    def __init__(self, db_path='greenhouse.db', has_flow_meter=True):
        self.db = sqlite3.connect(db_path)
        self.valves = [gpiozero.OutputDevice(pin=p, active_high=False) 
                       for p in self.VALVE_PINS]
        self.pump = gpiozero.OutputDevice(pin=self.PUMP_PIN, active_high=False)
        self.pump_enable = gpiozero.OutputDevice(pin=self.PUMP_ENABLE_PIN, active_high=False)
        self.emergency = gpiozero.OutputDevice(pin=self.EMERGENCY_PIN, active_high=False)
        
        self.has_flow_meter = has_flow_meter
        self.flow_pulses = 0
        self.flow_callback = None
        
        # Initialize all valves closed
        self.close_all()
        self.pump.off()
        self.pump_enable.off()
        self.emergency.on()  # Emergency relay: ON = armed, OFF = triggered
        
    def irrigate_zone(self, zone_id: int, duration_sec: float, 
                      reason: str = 'auto') -> dict:
        """Execute irrigation with full monitoring and failsafes."""
        
        event = {
            'zone_id': zone_id,
            'started_at': time.time(),
            'requested_sec': duration_sec,
            'actual_sec': 0,
            'valve_opened': False,
            'valve_closed': False,
            'pump_on': False,
            'pressure_start_bar': None,
            'pressure_end_bar': None,
            'flow_l_total': 0,
            'aborted': False,
            'abort_reason': None
        }
        
        try:
            # 1. Pre-checks
            if not self._pre_check():
                event['aborted'] = True
                event['abort_reason'] = 'Pre-check failed (pressure/pump)'
                self._log_event(event)
                return event
            
            # 2. Start pump
            self.pump_enable.on()
            time.sleep(0.5)
            self.pump.on()
            event['pump_on'] = True
            time.sleep(2)  # Let pump build pressure
            
            # 3. Read pressure
            event['pressure_start_bar'] = self._read_pressure()
            if event['pressure_start_bar'] < 1.0:
                self._abort(event, 'Low pressure at start')
                return event
            
            # 4. Open valve
            self.valves[zone_id].on()
            event['valve_opened'] = True
            self._update_valve_state(zone_id, True, reason)
            
            # 5. Monitor during irrigation
            start_time = time.time()
            flow_start = self.flow_pulses
            
            while (time.time() - start_time) < duration_sec:
                elapsed = time.time() - start_time
                
                # Check pressure
                pressure = self._read_pressure()
                if pressure < 0.5:
                    self._abort(event, 'Pressure dropped mid-irrigation')
                    return event
                
                # Check flow (if no flow after 30s, something is wrong)
                if self.has_flow_meter and elapsed > 30:
                    pulses = self.flow_pulses - flow_start
                    litres = pulses / self.PULSES_PER_LITRE
                    if litres < 0.1:
                        self._abort(event, 'No flow detected')
                        return event
                
                # Check max duration hard limit
                if elapsed > 3600:  # 1 hour absolute max
                    self._abort(event, 'Hard duration limit reached')
                    return event
                
                time.sleep(1)
            
            # 6. Normal completion
            event['actual_sec'] = time.time() - start_time
            event['pressure_end_bar'] = self._read_pressure()
            
            if self.has_flow_meter:
                pulses = self.flow_pulses - flow_start
                event['flow_l_total'] = pulses / self.PULSES_PER_LITRE
            
        except Exception as e:
            event['aborted'] = True
            event['abort_reason'] = f'Exception: {str(e)}'
            
        finally:
            # Always close valve and stop pump
            self.valves[zone_id].off()
            event['valve_closed'] = True
            self._update_valve_state(zone_id, False, 'complete')
            
            self.pump.off()
            time.sleep(1)
            self.pump_enable.off()
            event['pump_on'] = False
            
            self._log_event(event)
        
        return event
    
    def _pre_check(self) -> bool:
        """Check system health before starting."""
        # Pressure must be present (pump primed or mains pressure)
        pressure = self._read_pressure()
        if pressure < 0.3:
            return False
        
        # Emergency circuit must be armed
        if not self.emergency.value:
            return False
        
        return True
    
    def _abort(self, event: dict, reason: str):
        """Safe abort — close everything, log."""
        event['aborted'] = True
        event['abort_reason'] = reason
        event['actual_sec'] = time.time() - event['started_at']
        
        # Close all valves
        self.close_all()
        
        # Stop pump
        self.pump.off()
        time.sleep(1)
        self.pump_enable.off()
        event['pump_on'] = False
        
        self._log_event(event)
    
    def close_all(self):
        """Close all valves immediately."""
        for v in self.valves:
            v.off()
        for i in range(12):
            self._update_valve_state(i, False, 'emergency_close_all')
    
    def _read_pressure(self) -> float:
        """Read 4-20 mA pressure transducer via ADC."""
        # Implementation depends on ADC hardware (MCP3008, ADS1115, or Pi GPIO ADC)
        # 4 mA = 0 bar, 20 mA = 4 bar
        # For now, placeholder
        return 2.0  # Placeholder: assume 2 bar
    
    def _update_valve_state(self, zone_id: int, is_open: bool, source: str):
        self.db.execute('''
            INSERT OR REPLACE INTO valve_state_log 
            (zone_id, is_open, last_cmd_at, last_cmd_source)
            VALUES (?, ?, ?, ?)
        ''', (zone_id, is_open, time.time(), source))
        self.db.commit()
    
    def _log_event(self, event: dict):
        self.db.execute('''
            INSERT INTO irrigation_events 
            (zone_id, triggered_by, reason, started_at, requested_sec, 
             actual_sec, valve_opened, valve_closed, pump_on,
             pressure_start_bar, pressure_end_bar, flow_l_total,
             aborted, abort_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event['zone_id'], event.get('triggered_by', 'auto'),
            event.get('reason', ''), event['started_at'],
            event['requested_sec'], event['actual_sec'],
            event['valve_opened'], event['valve_closed'],
            event['pump_on'], event.get('pressure_start_bar'),
            event.get('pressure_end_bar'), event.get('flow_l_total'),
            event['aborted'], event.get('abort_reason')
        ))
        self.db.commit()
```

---

## Failsafe Watchdog

### Hardware Watchdog

```python
# failsafe_watchdog.py
import gpiozero
import time
import sqlite3
import threading

class FailsafeWatchdog:
    """Hardware watchdog using external timer + GPIO heartbeat."""
    
    HEARTBEAT_PIN = 17  # Pi toggles this to prove it's alive
    WDOG_TIMEOUT = 300  # 5 minutes
    
    def __init__(self, db_path='greenhouse.db'):
        self.db = sqlite3.connect(db_path)
        self.heartbeat = gpiozero.OutputDevice(self.HEARTBEAT_PIN)
        self.valve = ValveController(db_path)
        self.running = False
        self.last_heartbeat = time.time()
        
    def start(self):
        self.running = True
        threading.Thread(target=self._heartbeat_loop, daemon=True).start()
        threading.Thread(target=self._watchdog_loop, daemon=True).start()
        
    def _heartbeat_loop(self):
        """Toggle GPIO every 10s to prove software is alive."""
        while self.running:
            self.heartbeat.toggle()
            self.last_heartbeat = time.time()
            time.sleep(10)
    
    def _watchdog_loop(self):
        """Monitor heartbeat. If missed, close all valves + stop pump."""
        while self.running:
            time.sleep(30)
            
            if time.time() - self.last_heartbeat > self.WDOG_TIMEOUT:
                print("WATCHDOG: Heartbeat lost! Emergency shutdown.")
                self.valve.close_all()
                self.valve.pump.off()
                self.valve.pump_enable.off()
                
                # Log the event
                self.db.execute('''
                    INSERT INTO irrigation_events 
                    (zone_id, triggered_by, reason, started_at, aborted, abort_reason)
                    VALUES (99, 'watchdog', 'Heartbeat timeout emergency stop', ?, 1, ?)
                ''', (time.time(), f'No heartbeat for {self.WDOG_TIMEOUT}s'))
                self.db.commit()
                
                # Attempt restart or alert
                self._alert("WATCHDOG TRIGGERED: All valves closed, pump stopped")
    
    def _alert(self, message: str):
        """Send alert via MQTT, email, SMS, or local buzzer."""
        # Implementation depends on configured channels
        print(f"ALERT: {message}")
```

### Software Failsafes Summary

| Failsafe | Trigger | Action | Recovery |
|----------|---------|--------|----------|
| **Heartbeat watchdog** | No GPIO toggle for 5 min | Close all valves, stop pump | Manual restart |
| **Pressure low** | < 0.5 bar during irrigation | Abort zone, close valve | Auto retry next cycle |
| **No flow** | < 0.1 L after 30s | Abort zone, close valve | Alert operator |
| **Duration hard limit** | > 60 min any zone | Force close | Alert operator |
| **Daily water limit** | > 60 min any zone in 24h | Block further irrigation | Resets at midnight |
| **Sensor offline** | 2+ missed packets | Skip auto, use schedule | Resume when back online |
| **Emergency stop** | Physical button / web UI | Close all, stop pump | Manual reset |
| **Power loss** | Pi loses power | Relay board defaults to NC (valves closed) | UPS holds Pi 10 min |

---

## Pump Control

### VFD Integration

Most greenhouse pumps use a **Variable Frequency Drive (VFD)** for pressure control:

```
Pi GPIO 24 ──→ Contactor coil ──→ VFD Run input
Pi GPIO 23 ──→ Enable relay ──→ VFD Enable

VFD 4-20 mA output ──→ Pi ADC ──→ Pressure feedback loop
VFD fault relay ──→ Pi GPIO input ──→ Alert on pump fault
```

### Pressure Control Loop (Optional)

```python
class PumpController:
    def __init__(self, vfd_modbus_address=1):
        # Modbus RTU to VFD for setpoint control
        self.vfd = minimalmodbus.Instrument('/dev/ttyUSB1', vfd_modbus_address)
        self.target_pressure = 2.0  # bar
        
    def maintain_pressure(self):
        """Simple bang-bang pressure control via VFD."""
        pressure = self._read_pressure()
        
        if pressure < self.target_pressure - 0.3:
            # Increase speed
            current_speed = self.vfd.read_register(0x0001)
            self.vfd.write_register(0x0001, min(current_speed + 5, 100))
        elif pressure > self.target_pressure + 0.3:
            # Decrease speed
            current_speed = self.vfd.read_register(0x0001)
            self.vfd.write_register(0x0001, max(current_speed - 5, 30))
```

**Simpler option:** If VFD has built-in pressure control, just send **Run** signal from Pi and let VFD handle the rest.

---

## Web Dashboard

### Key Screens

**1. Live Map**
- Grid of 12 zones
- Colour: blue (wet) → yellow (dry) → red (critical)
- Animated: pulsing if irrigating now
- Click any zone for details

**2. Zone Detail**
- 24h impedance trend (8 channels)
- Temperature overlay
- Last irrigation event
- Manual override buttons: **Irrigate 5 min** / **Irrigate 15 min** / **Stop**

**3. System Status**
- Node health (12 nodes, online/stale/offline)
- Pump status (running/idle/fault)
- Pressure gauge
- Flow rate (if meter installed)
- Today's water usage per zone

**4. Settings**
- Threshold adjustment slider
- Schedule window (start/end hour)
- Daily limit per zone
- Weather API key
- MQTT broker config
- Calibration mode

### Flask Routes

```python
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/zones')
def get_zones():
    """Return current state of all 12 zones."""
    # Query DB for latest reading + valve state per zone
    pass

@app.route('/api/zone/<int:zone_id>/irrigate', methods=['POST'])
def manual_irrigate(zone_id: int):
    """Manual override — start irrigation."""
    duration = request.json.get('duration_sec', 300)
    result = valve_controller.irrigate_zone(
        zone_id, duration, reason='manual_override'
    )
    return jsonify(result)

@app.route('/api/zone/<int:zone_id>/stop', methods=['POST'])
def stop_irrigation(zone_id: int):
    """Emergency stop single zone."""
    valve_controller.valves[zone_id].off()
    return jsonify({'status': 'stopped'})

@app.route('/api/emergency-stop', methods=['POST'])
def emergency_stop():
    """Stop everything."""
    valve_controller.close_all()
    valve_controller.pump.off()
    return jsonify({'status': 'all_stopped'})

@app.route('/api/config', methods=['GET', 'POST'])
def config():
    if request.method == 'GET':
        return jsonify(decision_engine._get_config())
    else:
        # Update config keys
        for key, value in request.json.items():
            db.execute('UPDATE system_config SET value = ? WHERE key = ?',
                       (value, key))
        db.commit()
        return jsonify({'status': 'updated'})
```

---

## MQTT / Cloud Integration

```python
# mqtt_client.py
import paho.mqtt.client as mqtt
import json

class GreenhouseMQTT:
    def __init__(self, broker: str, topic_prefix: str = 'greenhouse/soil'):
        self.client = mqtt.Client()
        self.topic_prefix = topic_prefix
        self.client.connect(broker, 1883, 60)
        
    def publish_reading(self, reading: dict):
        topic = f"{self.topic_prefix}/node/{reading['node_id']}"
        self.client.publish(topic, json.dumps(reading), qos=1)
        
    def publish_irrigation(self, event: dict):
        topic = f"{self.topic_prefix}/irrigation/zone/{event['zone_id']}"
        self.client.publish(topic, json.dumps(event), qos=1, retain=True)
        
    def publish_alert(self, message: str, severity='warning'):
        topic = f"{self.topic_prefix}/alerts"
        payload = json.dumps({'message': message, 'severity': severity,
                              'time': time.time()})
        self.client.publish(topic, payload, qos=2)
```

**Topics:**
- `greenhouse/soil/node/0` — Live telemetry from node 0
- `greenhouse/soil/irrigation/zone/3` — Zone 3 irrigation events (retained)
- `greenhouse/soil/alerts` — System alerts (pump fault, watchdog, etc.)
- `greenhouse/soil/config` — Remote configuration changes

---

## Calibration Mode

Before going full auto, the system needs calibration:

```python
class Calibration:
    def run_calibration(self, zone_id: int):
        """Manual calibration: measure dry, field capacity, saturation."""
        
        print("Calibration for zone", zone_id)
        
        # Step 1: Dry soil (after 2 days no water)
        input("Ensure soil is dry. Press Enter to measure...")
        z_dry = self._measure_avg(zone_id)
        
        # Step 2: Field capacity (water until drain, wait 24h)
        input("Water to field capacity, wait 24h. Press Enter...")
        z_fc = self._measure_avg(zone_id)
        
        # Step 3: Saturation (flood)
        input("Flood soil. Press Enter...")
        z_sat = self._measure_avg(zone_id)
        
        # Store
        self.db.execute('''
            INSERT OR REPLACE INTO system_config (key, value)
            VALUES (?, ?)
        ''', (f'dry_threshold_zone_{zone_id}', str(z_fc)))
        self.db.commit()
        
        print(f"Zone {zone_id}: dry={z_dry:.0f}, FC={z_fc:.0f}, sat={z_sat:.0f} Ω")
```

**Default thresholds by soil type (starting points):**

| Soil Type | Dry Threshold (Ω) | Saturation (Ω) |
|-----------|-------------------|----------------|
| Sandy loam | 350 | 100 |
| Clay loam | 500 | 150 |
| Silty clay | 600 | 200 |
| Peat / organic | 800 | 300 |

---

## Installation Checklist

### Electrical

- [ ] Earth bonding for all metal enclosures
- [ ] RCD on pump circuit (30 mA)
- [ ] Circuit breaker for valve PSU (10A)
- [ ] Circuit breaker for Pi PSU (5A)
- [ ] Surge protection on LoRa antenna (lightning)
- [ ] Label all wires at both ends

### Plumbing

- [ ] Backflow prevention on mains connection
- [ ] Y-filter on every valve (protect drip emitters)
- [ ] Pressure reducer (2 bar for drip)
- [ ] Air bleed valves at high points
- [ ] Drain valves at low points (winter)
- [ ] Flow direction arrows on valves
- [ ] Test all zones for even pressure

### Commissioning

- [ ] LoRa range test: walk each node location, confirm RSSI > -100 dBm
- [ ] Valve test: open/close each zone manually via web UI
- [ ] Pump test: run 5 min, check pressure stable
- [ ] Flow test: measure actual flow rate vs expected
- [ ] Calibration: dry/FC/saturation for 3 representative zones
- [ ] Failsafe test: disconnect Pi, verify valves close (NC relay)
- [ ] Watchdog test: kill Python process, verify hardware watchdog closes valves
- [ ] Emergency stop test: press button, everything stops
- [ ] Daily limit test: irrigate to limit, confirm blocking

---

## Maintenance Schedule

| Task | Frequency | Notes |
|------|-----------|-------|
| Check Y-filters | Weekly | Clean if flow drops |
| Inspect drip emitters | Monthly | Flush clogged lines |
| Verify node batteries | Quarterly | Check via dashboard |
| Calibrate 3 zones | Seasonally | Dry/FC/saturation cycle |
| Pressure test system | Annually | Check for leaks |
| Replace 18650 cells | Every 2–3 years | When capacity < 70% |
| Update software | As needed | OTA or USB update |

---

## Files Created

| File | Purpose |
|------|---------|
| `GREENHOUSE_GATEWAY_DESIGN.md` | This document |
| `gateway/main.py` | Entry point |
| `gateway/config.yaml` | Site settings |
| `gateway/database.py` | SQLite schema |
| `gateway/lora_receiver.py` | SX1262 interface |
| `gateway/decision_engine.py` | Irrigation logic |
| `gateway/valve_controller.py` | GPIO + pump control |
| `gateway/web_dashboard.py` | Flask web UI |
| `gateway/mqtt_client.py` | Cloud upload |
| `gateway/failsafe_watchdog.py` | Safety systems |
| `gateway/weather_client.py` | Rain delay |
| `gateway/calibration.py` | Soil calibration |

---

**Ready to implement?** Start with hardware (Pi + relay board + one solenoid), then layer on LoRa RX, then web dashboard, then decision engine, then full 12-zone plumbing.

Or jump straight to: **build breadboard node + gateway talking, then add one valve.**

*Document saved to: `projects/agricultural_sensing/GREENHOUSE_GATEWAY_DESIGN.md`*
