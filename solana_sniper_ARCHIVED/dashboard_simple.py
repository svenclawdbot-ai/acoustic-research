#!/usr/bin/env python3
"""
Simplified Sniper Dashboard - Standalone
Runs dashboard without full bot for testing
"""

import asyncio
import json
import random
from datetime import datetime
from pathlib import Path

import aiohttp
from aiohttp import web

# Dashboard state
stats = {
    "scanned": 0,
    "filtered": 0,
    "inferred": 0,
    "safety_checked": 0,
    "safety_failed": 0,
    "trades": 0,
    "successful": 0,
    "balance": 5.0,
    "available": 0.5
}

positions = []
activities = []
signals = []
ws_connections = []

async def index(request):
    html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Solana Sniper Bot | Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #0a0e1a; 
            color: #f9fafb;
            padding: 2rem;
        }
        .header { 
            display: flex; 
            justify-content: space-between; 
            align-items: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #2d3748;
        }
        .logo { font-size: 1.5rem; font-weight: 800; }
        .logo span { color: #3b82f6; }
        .status { 
            background: #10b981; 
            color: white; 
            padding: 0.5rem 1rem; 
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 600;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        .card {
            background: #1a1f2e;
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid #2d3748;
        }
        .card h3 {
            font-size: 0.875rem;
            color: #9ca3af;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .card .value {
            font-size: 2rem;
            font-weight: 700;
            color: #3b82f6;
        }
        .card .sub {
            font-size: 0.75rem;
            color: #6b7280;
            margin-top: 0.25rem;
        }
        .activity {
            background: #1a1f2e;
            border-radius: 12px;
            padding: 1rem;
            border: 1px solid #2d3748;
            max-height: 300px;
            overflow-y: auto;
        }
        .activity h3 {
            margin-bottom: 1rem;
            color: #9ca3af;
            font-size: 0.875rem;
            text-transform: uppercase;
        }
        .activity-item {
            padding: 0.75rem;
            border-bottom: 1px solid #2d3748;
            font-size: 0.875rem;
        }
        .activity-item:last-child { border-bottom: none; }
        .time { color: #6b7280; font-size: 0.75rem; }
        .mode-dry { color: #f59e0b; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">🎯 SNIPER<span>.BOT</span></div>
        <div>
            <span class="mode-dry">● DRY RUN</span>
            <span class="status">ONLINE</span>
        </div>
    </div>
    
    <div class="grid">
        <div class="card">
            <h3>Scanned</h3>
            <div class="value" id="scanned">0</div>
            <div class="sub">tokens checked</div>
        </div>
        <div class="card">
            <h3>Filtered</h3>
            <div class="value" id="filtered">0</div>
            <div class="sub">passed filters</div>
        </div>
        <div class="card">
            <h3>Signals</h3>
            <div class="value" id="signals">0</div>
            <div class="sub">AI detections</div>
        </div>
        <div class="card">
            <h3>Trades</h3>
            <div class="value" id="trades">0</div>
            <div class="sub">simulated buys</div>
        </div>
        <div class="card">
            <h3>Balance</h3>
            <div class="value" id="balance">5.00</div>
            <div class="sub">SOL available</div>
        </div>
        <div class="card">
            <h3>Uptime</h3>
            <div class="value" id="uptime">0m</div>
            <div class="sub">running time</div>
        </div>
    </div>
    
    <div class="activity">
        <h3>📋 Recent Activity</h3>
        <div id="activity-list">
            <div class="activity-item">
                <div>🚀 Dashboard started</div>
                <div class="time">Just now</div>
            </div>
        </div>
    </div>
    
    <script>
        const ws = new WebSocket(`ws://${window.location.host}/ws`);
        const startTime = Date.now();
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === "stats") {
                document.getElementById("scanned").textContent = data.data.scanned;
                document.getElementById("filtered").textContent = data.data.filtered;
                document.getElementById("signals").textContent = data.data.inferred;
                document.getElementById("trades").textContent = data.data.trades;
                document.getElementById("balance").textContent = data.data.balance.toFixed(2);
            }
            if (data.type === "activity") {
                const list = document.getElementById("activity-list");
                const item = document.createElement("div");
                item.className = "activity-item";
                item.innerHTML = `<div>${data.data.message}</div><div class="time">${data.data.time}</div>`;
                list.insertBefore(item, list.firstChild);
                if (list.children.length > 20) list.removeChild(list.lastChild);
            }
        };
        
        setInterval(() => {
            const mins = Math.floor((Date.now() - startTime) / 60000);
            document.getElementById("uptime").textContent = mins + "m";
        }, 60000);
    </script>
</body>
</html>'''
    return web.Response(text=html, content_type='text/html')

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    ws_connections.append(ws)
    
    try:
        async for msg in ws:
            pass
    finally:
        ws_connections.remove(ws)
    
    return ws

async def broadcast(data):
    message = json.dumps(data)
    for ws in ws_connections[:]:
        try:
            await ws.send_str(message)
        except:
            pass

async def simulate_bot():
    """Simulate bot activity for dry-run testing"""
    while True:
        await asyncio.sleep(5)
        
        # Random increments
        stats["scanned"] += random.randint(1, 5)
        
        if random.random() > 0.7:
            stats["filtered"] += 1
            await broadcast({
                "type": "activity",
                "data": {
                    "message": f"🔍 Token passed filters",
                    "time": datetime.now().strftime("%H:%M:%S")
                }
            })
        
        if random.random() > 0.9:
            stats["inferred"] += 1
            await broadcast({
                "type": "activity", 
                "data": {
                    "message": f"🤖 AI signal: High confidence detected",
                    "time": datetime.now().strftime("%H:%M:%S")
                }
            })
        
        if random.random() > 0.95:
            stats["trades"] += 1
            stats["successful"] += 1
            await broadcast({
                "type": "activity",
                "data": {
                    "message": f"💰 DRY RUN: Simulated buy executed",
                    "time": datetime.now().strftime("%H:%M:%S")
                }
            })
        
        await broadcast({"type": "stats", "data": stats})

async def stats_updater():
    """Send stats every 5 seconds"""
    while True:
        await asyncio.sleep(5)
        await broadcast({"type": "stats", "data": stats})

async def init_app():
    app = web.Application()
    app.router.add_get("/", index)
    app.router.add_get("/ws", websocket_handler)
    return app

async def main():
    print("🚀 Starting Sniper Bot Dashboard")
    print("=" * 40)
    print("Mode: DRY RUN (Simulation)")
    print("Dashboard: http://localhost:8080")
    print("=" * 40)
    
    app = await init_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    
    # Start simulation tasks
    asyncio.create_task(simulate_bot())
    asyncio.create_task(stats_updater())
    
    print("\n✅ Dashboard running!")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        print("\n\nStopping...")
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
