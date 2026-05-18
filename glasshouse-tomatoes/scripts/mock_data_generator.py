#!/usr/bin/env python3
"""
Mock Data Generator for GlassHouse Backend Demo
================================================
Generates realistic soil sensor data without needing Docker or hardware.
Saves to JSON for the HTML dashboard preview.
"""

import json
import random
import math
from datetime import datetime, timedelta
from pathlib import Path

# Config
NODE_ID = "gh-n01"
START_DAYS_AGO = 7
INTERVAL_MINUTES = 15
OUTPUT_DIR = Path(__file__).parent.parent / "demo_data"

# Tomato growth simulation parameters
# Dry point: VWC ~8%, Wet point: VWC ~45%
# Daily watering event: VWC jumps up, then decays

OUTPUT_DIR.mkdir(exist_ok=True)

def generate_vwc_series(days=7, interval_mins=15):
    """Generate realistic VWC data with watering events and daily cycles."""
    points = []
    now = datetime.utcnow()
    start = now - timedelta(days=days)
    
    # Watering schedule: every 2-3 days around 7 AM
    watering_days = set()
    current = start
    while current < now:
        if random.random() < 0.4:  # 40% chance to water on any given day
            watering_days.add(current.date())
        current += timedelta(days=1)
    
    t = start
    vwc = 25.0  # Start moderately moist
    
    while t < now:
        hour = t.hour + t.minute / 60.0
        
        # Daily evaporation pattern: faster during day, slower at night
        if 6 <= hour <= 20:
            evap_rate = 0.08 + 0.05 * math.sin((hour - 6) * math.pi / 14)
        else:
            evap_rate = 0.02
        
        # Transpiration (plants drinking) — higher on sunny afternoons
        if 10 <= hour <= 16 and vwc > 15:
            transpiration = 0.03
        else:
            transpiration = 0.01
        
        vwc -= (evap_rate + transpiration)
        
        # Watering event: 7 AM on watering days
        if t.date() in watering_days and 7 <= hour < 7.25:
            vwc += random.uniform(12, 18)
        
        # Clamp realistic range
        vwc = max(5.0, min(50.0, vwc))
        
        # Add sensor noise
        vwc_noisy = vwc + random.gauss(0, 0.5)
        
        # Temperature follows daily cycle + some lag from soil thermal mass
        temp_base = 18.0
        temp_amplitude = 4.0
        temp_phase = (hour - 8) * math.pi / 12  # Peak at ~2 PM
        temp = temp_base + temp_amplitude * math.sin(temp_phase)
        temp += random.gauss(0, 0.3)
        
        # Battery drains slowly
        elapsed_hours = (t - start).total_seconds() / 3600
        battery_mv = 4200 - elapsed_hours * 0.05  # ~1% per week
        battery_mv += random.gauss(0, 10)
        
        # WiFi signal varies slightly
        rssi = -65 + random.gauss(0, 3)
        
        points.append({
            "node_id": NODE_ID,
            "timestamp": t.isoformat() + "Z",
            "vwc_percent": round(vwc_noisy, 1),
            "temp_c": round(temp, 1),
            "battery_mv": int(battery_mv),
            "rssi_dbm": int(rssi),
            "seq": len(points) + 1
        })
        
        t += timedelta(minutes=interval_mins)
    
    return points

def generate_dashboard_json(data):
    """Generate a standalone HTML dashboard with embedded data."""
    
    latest = data[-1]
    
    vwc_values = [d["vwc_percent"] for d in data]
    temp_values = [d["temp_c"] for d in data]
    battery_values = [d["battery_mv"] / 1000.0 for d in data]
    time_labels = [d["timestamp"][11:16] for d in data]  # HH:MM format
    
    # Recommendation based on latest VWC
    vwc = latest["vwc_percent"]
    if vwc < 15:
        rec = "WATER NOW — Risk of blossom end rot"
        rec_color = "#d44a3a"
    elif vwc < 25:
        rec = "Water soon — within 24h"
        rec_color = "#e0b400"
    elif vwc < 40:
        rec = "OK — No action needed"
        rec_color = "#299c46"
    elif vwc < 50:
        rec = "Too wet — Stop watering, check drainage"
        rec_color = "#73c0fc"
    else:
        rec = "SATURATED — Root rot risk!"
        rec_color = "#d44a3a"
    
    # VWC status color
    if 15 <= vwc <= 35:
        vwc_bg = "#299c46"
    elif 35 < vwc <= 45:
        vwc_bg = "#e0b400"
    else:
        vwc_bg = "#d44a3a"
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GlassHouse Tomatoes — Soil Monitor</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; padding: 20px; color: #333; }}
    .header {{ background: linear-gradient(135deg, #2E7D32, #1b5e20); color: white; padding: 24px; border-radius: 12px; margin-bottom: 20px; }}
    .header h1 {{ font-size: 24px; margin-bottom: 4px; }}
    .header p {{ opacity: 0.9; font-size: 14px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 20px; }}
    .stat-card {{ background: white; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
    .stat-value {{ font-size: 36px; font-weight: 700; margin: 8px 0; }}
    .stat-label {{ font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; color: #888; }}
    .chart-container {{ background: white; border-radius: 12px; padding: 20px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
    .chart-container h3 {{ font-size: 16px; margin-bottom: 12px; color: #555; }}
    .rec-banner {{ background: {rec_color}; color: white; padding: 16px 20px; border-radius: 12px; margin-bottom: 20px; font-weight: 600; text-align: center; }}
    .info-panel {{ background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
    .info-panel h2 {{ font-size: 18px; margin-bottom: 16px; color: #2E7D32; }}
    .info-panel table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    .info-panel th, .info-panel td {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid #eee; }}
    .info-panel th {{ color: #888; font-weight: 500; }}
    .footer {{ text-align: center; margin-top: 30px; color: #aaa; font-size: 12px; }}
    .badge {{ display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; }}
    .badge-green {{ background: #e8f5e9; color: #2E7D32; }}
    .badge-yellow {{ background: #fff8e1; color: #e0b400; }}
    .badge-red {{ background: #ffebee; color: #d44a3a; }}
    .badge-blue {{ background: #e3f2fd; color: #1976d2; }}
</style>
</head>
<body>
<div class="header">
    <h1>🍅 GlassHouse Tomatoes</h1>
    <p>Soil Monitor — Node {latest['node_id']} • Last update: {latest['timestamp'][:16].replace('T', ' ')}</p>
</div>

<div class="rec-banner">
    💧 {rec}
</div>

<div class="grid">
    <div class="stat-card">
        <div class="stat-label">Soil Moisture</div>
        <div class="stat-value" style="color: {vwc_bg}">{latest['vwc_percent']}%</div>
        <div class="badge {'badge-green' if 15 <= vwc <= 35 else 'badge-yellow' if vwc <= 45 else 'badge-red'}">
            {'OK' if 15 <= vwc <= 35 else 'WATCH' if vwc <= 45 else 'ALERT'}
        </div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Temperature</div>
        <div class="stat-value" style="color: {'#299c46' if 18 <= latest['temp_c'] <= 26 else '#e0b400'}">{latest['temp_c']}°C</div>
        <div class="badge {'badge-green' if 18 <= latest['temp_c'] <= 26 else 'badge-yellow'}">
            {'Optimal' if 20 <= latest['temp_c'] <= 24 else 'Acceptable' if 18 <= latest['temp_c'] <= 26 else 'Warning'}
        </div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Battery</div>
        <div class="stat-value" style="color: {'#299c46' if latest['battery_mv'] >= 3700 else '#e0b400' if latest['battery_mv'] >= 3300 else '#d44a3a'}">{latest['battery_mv']/1000:.2f}V</div>
        <div class="badge {'badge-green' if latest['battery_mv'] >= 3700 else 'badge-yellow' if latest['battery_mv'] >= 3300 else 'badge-red'}">
            {'Good' if latest['battery_mv'] >= 3700 else 'Low' if latest['battery_mv'] >= 3300 else 'Critical'}
        </div>
    </div>
    <div class="stat-card">
        <div class="stat-label">WiFi Signal</div>
        <div class="stat-value" style="color: {'#299c46' if latest['rssi_dbm'] >= -70 else '#e0b400' if latest['rssi_dbm'] >= -80 else '#d44a3a'}">{latest['rssi_dbm']} dBm</div>
        <div class="badge {'badge-green' if latest['rssi_dbm'] >= -70 else 'badge-yellow' if latest['rssi_dbm'] >= -80 else 'badge-red'}">
            {'Strong' if latest['rssi_dbm'] >= -65 else 'Good' if latest['rssi_dbm'] >= -70 else 'Fair' if latest['rssi_dbm'] >= -80 else 'Weak'}
        </div>
    </div>
</div>

<div class="chart-container">
    <h3>💧 Soil Moisture History (7 days)</h3>
    <canvas id="vwcChart" height="100"></canvas>
</div>

<div class="chart-container">
    <h3>🌡️ Temperature History</h3>
    <canvas id="tempChart" height="80"></canvas>
</div>

<div class="chart-container">
    <h3>🔋 Battery & Signal</h3>
    <canvas id="sysChart" height="80"></canvas>
</div>

<div class="info-panel">
    <h2>🍅 Tomato Care Guide</h2>
    <table>
        <tr><th>Stage</th><th>Target VWC</th><th>Water When Below</th></tr>
        <tr><td>Seedling</td><td>25–35%</td><td>20%</td></tr>
        <tr><td>Vegetative</td><td>20–30%</td><td>15%</td></tr>
        <tr><td>Flowering</td><td>25–35%</td><td>20%</td></tr>
        <tr><td>Fruiting</td><td>25–40%</td><td>20%</td></tr>
        <tr><td>Ripening</td><td>15–25%</td><td>12%</td></tr>
    </table>
    <br>
    <p style="font-size: 13px; color: #666; line-height: 1.6;">
        <strong>Best practices:</strong> Water in the morning (6–9 AM). Water at the base, not overhead. 
        Deep & infrequent beats shallow & frequent. Mulch with straw or wood chips to reduce evaporation by 50%.
        In a glasshouse, VWC drops 2× faster than outside — check daily in summer.
    </p>
</div>

<div class="footer">
    GlassHouse Tomatoes v1.0 • Demo data generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC
</div>

<script>
const vwcCtx = document.getElementById('vwcChart').getContext('2d');
const tempCtx = document.getElementById('tempChart').getContext('2d');
const sysCtx = document.getElementById('sysChart').getContext('2d');

const labels = {json.dumps(time_labels)};
const vwcData = {json.dumps(vwc_values)};
const tempData = {json.dumps(temp_values)};
const batData = {json.dumps(battery_values)};
const rssiData = {json.dumps([d['rssi_dbm'] for d in data])};

// Downsample labels for readability
const step = Math.max(1, Math.floor(labels.length / 48));
const sampledLabels = labels.filter((_, i) => i % step === 0);
const sample = (arr) => arr.filter((_, i) => i % step === 0);

new Chart(vwcCtx, {{
    type: 'line',
    data: {{
        labels: sampledLabels,
        datasets: [{{
            label: 'VWC %',
            data: sample(vwcData),
            borderColor: '#2E7D32',
            backgroundColor: 'rgba(46, 125, 50, 0.1)',
            fill: true,
            tension: 0.3,
            pointRadius: 1
        }}]
    }},
    options: {{
        responsive: true,
        plugins: {{ legend: {{ display: false }} }},
        scales: {{
            y: {{ min: 0, max: 60, grid: {{ color: '#eee' }} }},
            x: {{ grid: {{ display: false }} }}
        }},
        annotation: {{
            annotations: {{
                low: {{ type: 'box', yMin: 0, yMax: 15, backgroundColor: 'rgba(212, 74, 58, 0.08)' }},
                good: {{ type: 'box', yMin: 15, yMax: 35, backgroundColor: 'rgba(41, 156, 70, 0.06)' }},
                high: {{ type: 'box', yMin: 35, yMax: 60, backgroundColor: 'rgba(224, 180, 0, 0.08)' }}
            }}
        }}
    }}
}});

new Chart(tempCtx, {{
    type: 'line',
    data: {{
        labels: sampledLabels,
        datasets: [{{
            label: '°C',
            data: sample(tempData),
            borderColor: '#1976d2',
            backgroundColor: 'rgba(25, 118, 210, 0.1)',
            fill: true,
            tension: 0.3,
            pointRadius: 1
        }}]
    }},
    options: {{
        responsive: true,
        plugins: {{ legend: {{ display: false }} }},
        scales: {{
            y: {{ min: 5, max: 35, grid: {{ color: '#eee' }} }},
            x: {{ grid: {{ display: false }} }}
        }}
    }}
}});

new Chart(sysCtx, {{
    type: 'line',
    data: {{
        labels: sampledLabels,
        datasets: [
            {{
                label: 'Battery (V)',
                data: sample(batData),
                borderColor: '#e0b400',
                yAxisID: 'y',
                tension: 0.3,
                pointRadius: 1
            }},
            {{
                label: 'RSSI (dBm)',
                data: sample(rssiData),
                borderColor: '#9c27b0',
                yAxisID: 'y1',
                tension: 0.3,
                pointRadius: 1
            }}
        ]
    }},
    options: {{
        responsive: true,
        scales: {{
            y: {{ type: 'linear', display: true, position: 'left', min: 3.0, max: 4.5 }},
            y1: {{ type: 'linear', display: true, position: 'right', min: -100, max: -30 }},
            x: {{ grid: {{ display: false }} }}
        }}
    }}
}});
</script>
</body>
</html>'''
    
    output_path = OUTPUT_DIR / "dashboard.html"
    output_path.write_text(html)
    return output_path

def generate_json_api(data):
    """Generate JSON files matching the API endpoints."""
    
    # Latest measurement
    latest = data[-1]
    (OUTPUT_DIR / "latest.json").write_text(json.dumps(latest, indent=2))
    
    # History
    (OUTPUT_DIR / "history.json").write_text(json.dumps(data, indent=2))
    
    # Nodes list
    nodes = [{
        "node_id": NODE_ID,
        "latest_vwc": latest["vwc_percent"],
        "latest_temp": latest["temp_c"],
        "latest_battery_mv": latest["battery_mv"],
        "last_seen": latest["timestamp"]
    }]
    (OUTPUT_DIR / "nodes.json").write_text(json.dumps(nodes, indent=2))

def main():
    print("=" * 50)
    print("  GlassHouse Mock Data Generator")
    print("=" * 50)
    print()
    
    print(f"Generating {START_DAYS_AGO} days of sensor data...")
    data = generate_vwc_series(days=START_DAYS_AGO, interval_mins=INTERVAL_MINUTES)
    print(f"  Generated {len(data)} data points")
    print(f"  Time range: {data[0]['timestamp'][:16]} → {data[-1]['timestamp'][:16]}")
    print()
    
    print("Saving JSON API responses...")
    generate_json_api(data)
    print(f"  ✓ {OUTPUT_DIR}/latest.json")
    print(f"  ✓ {OUTPUT_DIR}/history.json")
    print(f"  ✓ {OUTPUT_DIR}/nodes.json")
    print()
    
    print("Building HTML dashboard...")
    dashboard_path = generate_dashboard_json(data)
    print(f"  ✓ {dashboard_path}")
    print()
    
    print("=" * 50)
    print("  DEMO READY")
    print("=" * 50)
    print()
    print(f"Open this file in your browser:")
    print(f"  file://{dashboard_path}")
    print()
    print("Or serve it locally:")
    print(f"  cd {OUTPUT_DIR} && python3 -m http.server 8080")
    print(f"  Then open http://localhost:8080/dashboard.html")
    print()
    print("Latest readings:")
    print(f"  VWC:    {data[-1]['vwc_percent']}%")
    print(f"  Temp:   {data[-1]['temp_c']}°C")
    print(f"  Battery:{data[-1]['battery_mv']/1000:.2f}V")
    print(f"  RSSI:   {data[-1]['rssi_dbm']} dBm")
    print()

if __name__ == "__main__":
    main()
