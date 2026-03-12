#!/usr/bin/env python3
"""
Sniper Dashboard with REAL DEX Screener Data
Fetches actual Solana token data for realistic simulation
"""

import asyncio
import json
import random
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

import aiohttp
from aiohttp import web

# Import Grass tracker
try:
    from grass_tracker import grass_tracker
    GRASS_ENABLED = True
except:
    GRASS_ENABLED = False
    grass_tracker = None

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
    "available": 0.5,
    "avg_volatility": 0.0,
    "avg_volume": 0.0,
    "best_signal": 0.0
}

positions = []
activities = []
signals = []
ws_connections = []

# Data storage for 48h analysis
price_history = []
volume_history = []
signal_history = []

# DEX Screener config
DEXSCREENER_API = "https://api.dexscreener.com/latest/dex"
MIN_LIQUIDITY = 1000
MIN_VOLUME_5M = 5000
MAX_ENTRY_DELAY = 120

class TokenPair:
    def __init__(self, data: dict):
        self.address = data.get("pairAddress", "")
        self.base_token = data.get("baseToken", {}).get("address", "")
        self.quote_token = data.get("quoteToken", {}).get("address", "")
        self.dex_id = data.get("dexId", "")
        self.price_usd = float(data.get("priceUsd", 0) or 0)
        self.liquidity_usd = float(data.get("liquidity", {}).get("usd", 0) or 0)
        self.volume_5m = float(data.get("volume", {}).get("m5", 0) or 0)
        self.volume_1h = float(data.get("volume", {}).get("h1", 0) or 0)
        self.price_change_5m = float(data.get("priceChange", {}).get("m5", 0) or 0)
        self.price_change_1h = float(data.get("priceChange", {}).get("h1", 0) or 0)
        self.tx_count_5m = int(data.get("txns", {}).get("m5", {}).get("buys", 0) or 0) + int(data.get("txns", {}).get("m5", {}).get("sells", 0) or 0)
        created = data.get("pairCreatedAt")
        self.age_seconds = (datetime.utcnow().timestamp() - created / 1000) if created else None

    def calculate_volatility(self) -> float:
        """Calculate volatility score from price changes"""
        if abs(self.price_change_5m) > 100:
            return 1.0  # Extreme
        elif abs(self.price_change_5m) > 50:
            return 0.8  # High
        elif abs(self.price_change_5m) > 20:
            return 0.6  # Medium
        elif abs(self.price_change_5m) > 10:
            return 0.4  # Low-Med
        else:
            return 0.2  # Low

    def to_dict(self) -> dict:
        return {
            "token": self.base_token[:8] + "...",
            "price": self.price_usd,
            "liquidity": self.liquidity_usd,
            "volume_5m": self.volume_5m,
            "change_5m": self.price_change_5m,
            "age": self.age_seconds,
            "tx_count": self.tx_count_5m,
            "volatility": self.calculate_volatility()
        }

async def fetch_dex_data() -> List[TokenPair]:
    """Fetch real Solana pairs from DEX Screener with better error handling"""
    errors = []
    
    try:
        async with aiohttp.ClientSession() as session:
            # Try multiple endpoints for reliability
            endpoints = [
                ("https://api.dexscreener.com/latest/dex/search?q=solana", "search"),
                ("https://api.dexscreener.com/latest/dex/pairs/solana", "pairs"),
                ("https://api.dexscreener.com/token-pairs/v1/solana", "token-pairs"),
            ]
            
            for url, endpoint_type in endpoints:
                try:
                    print(f"[DEX] Trying {endpoint_type}: {url[:50]}...")
                    async with session.get(url, timeout=15) as resp:
                        print(f"[DEX] {endpoint_type} status: {resp.status}")
                        
                        if resp.status == 200:
                            data = await resp.json()
                            pairs = []
                            
                            # Handle different response formats
                            pair_list = data.get("pairs", [])
                            if not pair_list and "data" in data:
                                pair_list = data["data"].get("pairs", [])
                            
                            print(f"[DEX] {endpoint_type} returned {len(pair_list)} pairs")
                            
                            for pair_data in pair_list[:50]:
                                try:
                                    # Filter for Solana chain
                                    chain_id = pair_data.get("chainId", "")
                                    if chain_id and chain_id != "solana":
                                        continue
                                    
                                    # Also check if quoteToken mentions SOL
                                    base_token = pair_data.get("baseToken", {})
                                    quote_token = pair_data.get("quoteToken", {})
                                    
                                    # Accept pairs where quote is SOL or USDC (common on Solana)
                                    quote_symbol = quote_token.get("symbol", "")
                                    if quote_symbol not in ["SOL", "WSOL", "USDC", "USDT"]:
                                        continue
                                    
                                    pair = TokenPair(pair_data)
                                    pairs.append(pair)
                                except Exception as e:
                                    continue
                            
                            if pairs:
                                print(f"[DEX] Success! Got {len(pairs)} valid Solana pairs")
                                return pairs
                            else:
                                errors.append(f"{endpoint_type}: No valid pairs")
                        else:
                            errors.append(f"{endpoint_type}: HTTP {resp.status}")
                            
                except asyncio.TimeoutError:
                    errors.append(f"{endpoint_type}: Timeout")
                    continue
                except Exception as e:
                    errors.append(f"{endpoint_type}: {str(e)[:50]}")
                    continue
                    
    except Exception as e:
        errors.append(f"Session error: {e}")
    
    print(f"[DEX] All endpoints failed: {' | '.join(errors)}")
    return []

def evaluate_token(pair: TokenPair) -> tuple:
    """
    Apply real filtering logic to token
    Returns: (passed: bool, score: float, confidence: float, reasons: list)
    """
    score = 0.0
    reasons = []
    
    # Basic eligibility
    if pair.liquidity_usd < MIN_LIQUIDITY:
        return False, 0, 0, ["Low liquidity"]
    
    if pair.age_seconds and pair.age_seconds > MAX_ENTRY_DELAY:
        return False, 0, 0, ["Too old"]
    
    # Liquidity score
    if pair.liquidity_usd > 50000:
        score += 0.25
        reasons.append("Deep liquidity")
    elif pair.liquidity_usd > 10000:
        score += 0.20
        reasons.append("Good liquidity")
    elif pair.liquidity_usd > 5000:
        score += 0.15
    else:
        score += 0.10
    
    # Volume score
    if pair.volume_5m > 50000:
        score += 0.35
        reasons.append("High volume")
    elif pair.volume_5m > 20000:
        score += 0.25
        reasons.append("Good volume")
    elif pair.volume_5m > MIN_VOLUME_5M:
        score += 0.15
    
    # Transaction count (organic activity)
    if pair.tx_count_5m > 50:
        score += 0.20
        reasons.append("High tx count")
    elif pair.tx_count_5m > 20:
        score += 0.10
    
    # Price momentum (but not extreme)
    if 10 <= pair.price_change_5m <= 50:
        score += 0.15
        reasons.append(f"Momentum: +{pair.price_change_5m:.1f}%")
    elif 5 <= pair.price_change_5m < 10:
        score += 0.10
    
    # Age bonus (convexity)
    if pair.age_seconds and pair.age_seconds < 60:
        score += 0.10
        reasons.append("Very fresh")
    elif pair.age_seconds and pair.age_seconds < 180:
        score += 0.05
    
    # Volatility check
    volatility = pair.calculate_volatility()
    if volatility > 0.7:
        score -= 0.05  # Penalty for extreme volatility
        reasons.append("High volatility")
    
    passed = score >= 0.35
    confidence = min(score * 1.2, 0.95)  # Scale to confidence
    
    return passed, score, confidence, reasons

async def process_real_data():
    """Process real DEX data through the sniper logic"""
    global stats
    
    pairs = await fetch_dex_data()
    
    if not pairs:
        print("No data from DEX Screener, using fallback...")
        return
    
    for pair in pairs:
        stats["scanned"] += 1
        
        # Store for analysis
        price_history.append({
            "time": datetime.now().isoformat(),
            "token": pair.base_token[:8],
            "price": pair.price_usd,
            "change_5m": pair.price_change_5m,
            "volatility": pair.calculate_volatility()
        })
        
        volume_history.append({
            "time": datetime.now().isoformat(),
            "volume": pair.volume_5m
        })
        
        # Apply filters
        passed, score, confidence, reasons = evaluate_token(pair)
        
        if passed:
            stats["filtered"] += 1
            
            # Bayesian inference simulation
            if confidence >= 0.7:
                stats["inferred"] += 1
                
                signal_data = {
                    "token": pair.base_token[:8] + "...",
                    "confidence": round(confidence, 2),
                    "score": round(score, 2),
                    "age": round(pair.age_seconds) if pair.age_seconds else 0,
                    "liquidity": pair.liquidity_usd,
                    "volume_5m": pair.volume_5m,
                    "change_5m": pair.price_change_5m,
                    "volatility": pair.calculate_volatility(),
                    "reasons": reasons
                }
                
                signals.insert(0, signal_data)
                signal_history.append(signal_data)
                
                await broadcast({
                    "type": "signal",
                    "data": signal_data
                })
                
                await broadcast({
                    "type": "activity",
                    "data": {
                        "message": f"🤖 SIGNAL: {pair.base_token[:8]}... conf={confidence:.0%} | " + " | ".join(reasons[:2]),
                        "time": datetime.now().strftime("%H:%M:%S")
                    }
                })
                
                # Simulate trade
                if confidence >= 0.65:
                    stats["trades"] += 1
                    stats["successful"] += 1
                    stats["best_signal"] = max(stats["best_signal"], confidence)
                    
                    await broadcast({
                        "type": "activity",
                        "data": {
                            "message": f"💰 DRY RUN: Buy {pair.base_token[:8]}... @ ${pair.price_usd:.6f}",
                            "time": datetime.now().strftime("%H:%M:%S")
                        }
                    })
                    
                    positions.insert(0, {
                        "token": pair.base_token[:8] + "...",
                        "entry": pair.price_usd,
                        "size": 0.05,
                        "pnl": 0,
                        "status": "OPEN"
                    })
        
        # Update averages
        if price_history:
            recent = price_history[-50:]
            stats["avg_volatility"] = sum(p["volatility"] for p in recent) / len(recent)
        
        if volume_history:
            recent = volume_history[-50:]
            stats["avg_volume"] = sum(v["volume"] for v in recent) / len(recent)
        
        # Update Grass stats if enabled
        if GRASS_ENABLED and grass_tracker:
            grass_stats = grass_tracker.get_stats()
            stats["grass"] = grass_stats

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
        .data-source {
            color: #f59e0b;
            font-size: 0.75rem;
            margin-top: 0.25rem;
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
        .card.highlight {
            border-color: #fbbf24;
            background: linear-gradient(135deg, #1a1f2e 0%, rgba(251, 191, 36, 0.1) 100%);
        }
        .volatility-high { color: #ef4444 !important; }
        .volatility-med { color: #f59e0b !important; }
        .volatility-low { color: #10b981 !important; }
        .two-col {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }
        .panel {
            background: #1a1f2e;
            border-radius: 12px;
            padding: 1rem;
            border: 1px solid #2d3748;
        }
        .panel h3 {
            color: #9ca3af;
            font-size: 0.875rem;
            margin-bottom: 1rem;
            text-transform: uppercase;
        }
        .activity-list {
            max-height: 300px;
            overflow-y: auto;
        }
        .activity-item {
            padding: 0.75rem;
            border-bottom: 1px solid #2d3748;
            font-size: 0.875rem;
        }
        .activity-item:last-child { border-bottom: none; }
        .time { color: #6b7280; font-size: 0.75rem; }
        .signal-item {
            display: flex;
            justify-content: space-between;
            padding: 0.75rem;
            border-bottom: 1px solid #2d3748;
            font-size: 0.875rem;
        }
        .signal-confidence {
            color: #10b981;
            font-weight: 700;
        }
        .mode-dry { color: #f59e0b; }
        .metric-row {
            display: flex;
            justify-content: space-between;
            padding: 0.5rem 0;
            border-bottom: 1px solid #2d3748;
        }
        .metric-label { color: #9ca3af; }
        .metric-value { font-weight: 600; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <div class="logo">🎯 SNIPER<span>.BOT</span></div>
            <div class="data-source">● Using REAL DEX Screener Data</div>
        </div>
        <div>
            <span class="mode-dry">● DRY RUN</span>
            <span class="status">ONLINE</span>
        </div>
    </div>
    
    <div class="grid">
        <div class="card">
            <h3>Scanned</h3>
            <div class="value" id="scanned">0</div>
            <div class="sub">real tokens from DEX</div>
        </div>
        <div class="card">
            <h3>Filtered</h3>
            <div class="value" id="filtered">0</div>
            <div class="sub">passed criteria</div>
        </div>
        <div class="card">
            <h3>Signals</h3>
            <div class="value" id="signals">0</div>
            <div class="sub">AI detections</div>
        </div>
        <div class="card highlight">
            <h3>Trades</h3>
            <div class="value" id="trades">0</div>
            <div class="sub">simulated buys</div>
        </div>
        <div class="card">
            <h3>Avg Volatility</h3>
            <div class="value" id="volatility">0%</div>
            <div class="sub">market volatility</div>
        </div>
        <div class="card">
            <h3>Best Signal</h3>
            <div class="value" id="best-signal">0%</div>
            <div class="sub">highest confidence</div>
        </div>
        
        <div class="card" style="border-color: #10b981; background: linear-gradient(135deg, #1a1f2e 0%, rgba(16, 185, 129, 0.15) 100%);">
            <h3 style="color: #10b981;">🌱 Grass.io</h3>
            <div class="value" id="grass-gbp" style="color: #10b981;">£0</div>
            <div class="sub" id="grass-points">100,000 points</div>
        </div>
    </div>
    
    <div class="two-col">
        <div class="panel">
            <h3>📋 Activity Log</h3>
            <div class="activity-list" id="activity-list">
                <div class="activity-item">
                    <div>🚀 Dashboard started with REAL data</div>
                    <div class="time">Just now</div>
                </div>
            </div>
        </div>
        
        <div class="panel">
            <h3>🔥 Recent Signals</h3>
            <div class="activity-list" id="signal-list">
                <div class="activity-item">Waiting for signals...</div>
            </div>
        </div>
    </div>
    
    <div class="panel" style="margin-top: 1rem;">
        <h3>📊 Market Metrics (Real Data)</h3>
        <div class="metric-row">
            <span class="metric-label">Average Volume (5m)</span>
            <span class="metric-value" id="avg-volume">$0</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Average Token Age</span>
            <span class="metric-value" id="avg-age">0s</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Filter Pass Rate</span>
            <span class="metric-value" id="pass-rate">0%</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Signal Rate</span>
            <span class="metric-value" id="signal-rate">0%</span>
        </div>
    </div>
    
    <script>
        const ws = new WebSocket(`ws://${window.location.host}/ws`);
        const startTime = Date.now();
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === "stats") {
                document.getElementById("scanned").textContent = data.data.scanned.toLocaleString();
                document.getElementById("filtered").textContent = data.data.filtered.toLocaleString();
                document.getElementById("signals").textContent = data.data.inferred.toLocaleString();
                document.getElementById("trades").textContent = data.data.trades.toLocaleString();
                
                const vol = (data.data.avg_volatility * 100).toFixed(0);
                const volEl = document.getElementById("volatility");
                volEl.textContent = vol + "%";
                volEl.className = "value " + (vol > 50 ? "volatility-high" : vol > 30 ? "volatility-med" : "volatility-low");
                
                document.getElementById("best-signal").textContent = (data.data.best_signal * 100).toFixed(0) + "%";
                document.getElementById("avg-volume").textContent = "$" + (data.data.avg_volume / 1000).toFixed(1) + "K";
                
                const passRate = data.data.scanned > 0 ? ((data.data.filtered / data.data.scanned) * 100).toFixed(1) : 0;
                document.getElementById("pass-rate").textContent = passRate + "%";
                
                const sigRate = data.data.filtered > 0 ? ((data.data.inferred / data.data.filtered) * 100).toFixed(1) : 0;
                document.getElementById("signal-rate").textContent = sigRate + "%";
                
                // Update Grass stats
                if (data.data.grass) {
                    document.getElementById("grass-gbp").textContent = "£" + data.data.grass.gbp_value;
                    document.getElementById("grass-points").textContent = data.data.grass.points.toLocaleString() + " points";
                }
            }
            if (data.type === "activity") {
                const list = document.getElementById("activity-list");
                const item = document.createElement("div");
                item.className = "activity-item";
                item.innerHTML = `<div>${data.data.message}</div><div class="time">${data.data.time}</div>`;
                list.insertBefore(item, list.firstChild);
                if (list.children.length > 20) list.removeChild(list.lastChild);
            }
            if (data.type === "signal") {
                const list = document.getElementById("signal-list");
                const item = document.createElement("div");
                item.className = "signal-item";
                item.innerHTML = `
                    <span>${data.data.token}</span>
                    <span class="signal-confidence">${(data.data.confidence * 100).toFixed(0)}%</span>
                `;
                list.insertBefore(item, list.firstChild);
                if (list.children.length > 10) list.removeChild(list.lastChild);
            }
        };
        
        ws.onerror = (e) => console.error("WebSocket error:", e);
        ws.onclose = () => console.log("WebSocket closed");
    </script>
</body>
</html>'''
    return web.Response(text=html, content_type='text/html')

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    ws_connections.append(ws)
    
    # Send current stats immediately
    await ws.send_str(json.dumps({"type": "stats", "data": stats}))
    
    try:
        async for msg in ws:
            pass
    finally:
        if ws in ws_connections:
            ws_connections.remove(ws)
    
    return ws

async def broadcast(data):
    message = json.dumps(data)
    dead_connections = []
    for ws in ws_connections:
        try:
            await ws.send_str(message)
        except:
            dead_connections.append(ws)
    
    for ws in dead_connections:
        if ws in ws_connections:
            ws_connections.remove(ws)

async def save_data():
    """Save historical data for 48h analysis"""
    while True:
        await asyncio.sleep(300)  # Save every 5 minutes
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "stats": stats,
            "price_history": price_history[-1000:],  # Last 1000 entries
            "volume_history": volume_history[-1000:],
            "signal_history": signal_history[-500:]
        }
        
        try:
            with open("/home/james/.openclaw/workspace/solana_sniper/data/history.json", "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Save error: {e}")

async def main_loop():
    """Main processing loop with real data"""
    while True:
        try:
            await process_real_data()
            await broadcast({"type": "stats", "data": stats})
            await asyncio.sleep(10)  # Poll every 10 seconds
        except Exception as e:
            print(f"Main loop error: {e}")
            await asyncio.sleep(30)

async def api_stats(request):
    """REST API for stats"""
    return web.json_response(stats)

async def api_activities(request):
    """REST API for recent activities"""
    return web.json_response(activities[-50:])

async def api_positions(request):
    """REST API for positions"""
    return web.json_response(positions)

async def api_signals(request):
    """REST API for signals"""
    return web.json_response(signals[-50:])

async def api_grass(request):
    """REST API for Grass rewards"""
    if GRASS_ENABLED and grass_tracker:
        return web.json_response(grass_tracker.get_stats())
    return web.json_response({"error": "Grass not enabled"})

async def api_health(request):
    """Health check endpoint"""
    return web.json_response({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "data_source": "DEX Screener",
        "mode": "dry_run"
    })

async def init_app():
    app = web.Application()
    app.router.add_get("/", index)
    app.router.add_get("/ws", websocket_handler)
    app.router.add_get("/api/stats", api_stats)
    app.router.add_get("/api/activities", api_activities)
    app.router.add_get("/api/positions", api_positions)
    app.router.add_get("/api/signals", api_signals)
    app.router.add_get("/api/grass", api_grass)
    app.router.add_get("/health", api_health)
    return app

async def main():
    print("🚀 Starting Sniper Bot Dashboard")
    print("=" * 50)
    print("Mode: DRY RUN with REAL DEX Screener Data")
    print("Data Source: DEX Screener API (Solana)")
    print("Dashboard: http://localhost:8080")
    print("=" * 50)
    
    # Create data directory
    Path("/home/james/.openclaw/workspace/solana_sniper/data").mkdir(exist_ok=True)
    
    app = await init_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    
    # Start tasks
    asyncio.create_task(main_loop())
    asyncio.create_task(save_data())
    
    print("\n✅ Dashboard running with REAL market data!")
    print("Fetching actual Solana token data every 10s...")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        print("\n\nStopping...")
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
