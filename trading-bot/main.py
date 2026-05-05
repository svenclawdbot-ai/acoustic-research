"""
Trading Bot Dashboard with Alpaca Integration
FastAPI backend with WebSocket live updates
"""
import asyncio
import json
import random
import os
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

# Alpaca integration
from alpaca_client import AlpacaTrader, AlpacaConfig, create_from_env

# ── Data Models ──────────────────────────────────────────────────────────────

@dataclass
class Position:
    symbol: str
    side: str
    entry_price: float
    current_price: float
    size: float
    pnl: float
    pnl_pct: float
    opened_at: str
    strategy: str

@dataclass
class TradeSignal:
    symbol: str
    action: str
    price: float
    timestamp: str
    strategy: str
    confidence: float

@dataclass
class BotStatus:
    running: bool
    mode: str           # PAPER / LIVE / MOCK
    connected: bool     # Alpaca API connected
    uptime_seconds: int
    total_trades: int
    win_rate: float
    total_pnl: float
    active_strategies: List[str]
    account_value: float
    buying_power: float
    cash: float

# ── Mock Engine (Fallback when no Alpaca keys) ─────────────────────────────

class MockEngine:
    SYMBOLS = ["BTC-USD", "ETH-USD", "SOL-USD", "AAPL", "TSLA", "NVDA"]
    STRATEGIES = ["Momentum", "MeanReversion", "Breakout", "Grid"]
    
    def __init__(self):
        self.positions: Dict[str, Position] = {}
        self.signals: List[TradeSignal] = []
        self.status = BotStatus(
            running=False,
            mode="MOCK",
            connected=False,
            uptime_seconds=0,
            total_trades=0,
            win_rate=0.0,
            total_pnl=0.0,
            active_strategies=["Momentum", "MeanReversion"],
            account_value=100000.0,
            buying_power=100000.0,
            cash=100000.0,
        )
        self.price_feed = {
            "BTC-USD": random.uniform(25000, 65000),
            "ETH-USD": random.uniform(1500, 4000),
            "SOL-USD": random.uniform(80, 250),
            "AAPL": random.uniform(150, 220),
            "TSLA": random.uniform(150, 300),
            "NVDA": random.uniform(400, 900),
        }
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        if self._running:
            return
        self._running = True
        self.status.running = True
        self._task = asyncio.create_task(self._loop())

    async def stop(self):
        self._running = False
        self.status.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _loop(self):
        tick = 0
        while self._running:
            await asyncio.sleep(2)
            tick += 1
            self.status.uptime_seconds = tick * 2
            
            for sym in self.SYMBOLS:
                change = random.uniform(-0.02, 0.02)
                self.price_feed[sym] *= (1 + change)
            
            for sym, pos in list(self.positions.items()):
                new_price = self.price_feed.get(sym, pos.current_price)
                if pos.side == "LONG":
                    pnl = (new_price - pos.entry_price) * pos.size
                else:
                    pnl = (pos.entry_price - new_price) * pos.size
                pct = (pnl / (pos.entry_price * pos.size)) * 100 if pos.entry_price else 0
                
                self.positions[sym] = Position(
                    symbol=sym, side=pos.side, entry_price=pos.entry_price,
                    current_price=round(new_price, 2), size=pos.size,
                    pnl=round(pnl, 2), pnl_pct=round(pct, 2),
                    opened_at=pos.opened_at, strategy=pos.strategy,
                )

            if random.random() < 0.3:
                await self._generate_signal()
            self._recalc_stats()

    async def _generate_signal(self):
        sym = random.choice(self.SYMBOLS)
        strat = random.choice(self.STRATEGIES)
        price = self.price_feed[sym]
        has_position = sym in self.positions
        
        if has_position and random.random() < 0.4:
            action = "CLOSE"
        elif has_position:
            return
        else:
            action = random.choice(["BUY", "SELL"])
        
        signal = TradeSignal(
            symbol=sym, action=action, price=round(price, 2),
            timestamp=datetime.now().strftime("%H:%M:%S"),
            strategy=strat, confidence=round(random.uniform(0.6, 0.99), 2)
        )
        self.signals.insert(0, signal)
        self.signals = self.signals[:50]
        
        if action == "BUY" and sym not in self.positions:
            self.positions[sym] = Position(
                symbol=sym, side="LONG", entry_price=round(price, 2),
                current_price=round(price, 2), size=round(random.uniform(0.1, 2.0), 3),
                pnl=0.0, pnl_pct=0.0,
                opened_at=datetime.now().strftime("%H:%M:%S"),
                strategy=strat
            )
            self.status.total_trades += 1
        elif action == "SELL" and sym not in self.positions:
            self.positions[sym] = Position(
                symbol=sym, side="SHORT", entry_price=round(price, 2),
                current_price=round(price, 2), size=round(random.uniform(0.1, 2.0), 3),
                pnl=0.0, pnl_pct=0.0,
                opened_at=datetime.now().strftime("%H:%M:%S"),
                strategy=strat
            )
            self.status.total_trades += 1
        elif action == "CLOSE" and sym in self.positions:
            del self.positions[sym]

    def _recalc_stats(self):
        self.status.total_pnl = round(sum(p.pnl for p in self.positions.values()), 2)
        if self.status.total_trades > 0:
            self.status.win_rate = round(50 + random.uniform(-10, 15), 1)

    def get_state(self):
        return {
            "status": asdict(self.status),
            "positions": [asdict(p) for p in self.positions.values()],
            "signals": [asdict(s) for s in self.signals[:20]],
            "prices": {k: round(v, 2) for k, v in self.price_feed.items()},
            "orders": [],
        }

# ── Alpaca Engine (Real trading) ─────────────────────────────────────────────

class AlpacaEngine:
    def __init__(self):
        self.trader: Optional[AlpacaTrader] = create_from_env()
        self.signals: List[TradeSignal] = []
        self.price_cache: Dict[str, float] = {}
        self._running = False
        self._task: Optional[asyncio.Task] = None
        
        if self.trader:
            account = self.trader.get_account()
            is_paper = self.trader.config.paper
            self.status = BotStatus(
                running=False,
                mode="PAPER" if is_paper else "LIVE",
                connected=True,
                uptime_seconds=0,
                total_trades=0,
                win_rate=0.0,
                total_pnl=0.0,
                active_strategies=["Alpaca Real"],
                account_value=account.get("equity", 0),
                buying_power=account.get("buying_power", 0),
                cash=account.get("cash", 0),
            )
        else:
            self.status = BotStatus(
                running=False, mode="NO_KEYS", connected=False,
                uptime_seconds=0, total_trades=0, win_rate=0.0,
                total_pnl=0.0, active_strategies=[],
                account_value=0, buying_power=0, cash=0,
            )

    async def start(self):
        if not self.trader or self._running:
            return
        self._running = True
        self.status.running = True
        self._task = asyncio.create_task(self._loop())

    async def stop(self):
        self._running = False
        self.status.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _loop(self):
        tick = 0
        while self._running:
            await asyncio.sleep(3)
            tick += 1
            self.status.uptime_seconds = tick * 3
            
            # Refresh account data
            if self.trader:
                account = self.trader.get_account()
                if "error" not in account:
                    self.status.account_value = account.get("equity", 0)
                    self.status.buying_power = account.get("buying_power", 0)
                    self.status.cash = account.get("cash", 0)
                
                positions = self.trader.get_positions()
                if positions and "error" not in positions[0]:
                    self.status.total_pnl = round(sum(p.get("unrealized_pl", 0) for p in positions), 2)

    def get_state(self):
        positions = []
        orders = []
        
        if self.trader:
            raw_positions = self.trader.get_positions()
            if raw_positions and "error" not in raw_positions[0]:
                for p in raw_positions:
                    positions.append({
                        "symbol": p["symbol"],
                        "side": p["side"],
                        "entry_price": p["avg_entry_price"],
                        "current_price": p["current_price"],
                        "size": p["qty"],
                        "pnl": p["unrealized_pl"],
                        "pnl_pct": p["unrealized_plpc"],
                        "opened_at": "N/A",
                        "strategy": "Alpaca",
                    })
            
            raw_orders = self.trader.get_orders(limit=20)
            if raw_orders and "error" not in raw_orders[0]:
                orders = raw_orders

        return {
            "status": asdict(self.status),
            "positions": positions,
            "signals": [asdict(s) for s in self.signals[:20]],
            "prices": self.price_cache,
            "orders": orders,
        }

# ── Unified Engine ─────────────────────────────────────────────────────────

class TradingEngine:
    def __init__(self):
        self.alpaca = AlpacaEngine()
        self.mock = MockEngine()
        self.active = self.alpaca if self.alpaca.trader else self.mock
        
    async def start(self):
        await self.active.start()
        
    async def stop(self):
        await self.active.stop()
        
    def get_state(self):
        return self.active.get_state()
    
    def submit_order(self, symbol: str, qty: float, side: str, order_type: str = "market", limit_price: Optional[float] = None):
        if isinstance(self.active, AlpacaEngine) and self.active.trader:
            if order_type == "market":
                return self.active.trader.submit_market_order(symbol, qty, side)
            else:
                return self.active.trader.submit_limit_order(symbol, qty, side, limit_price or 0)
        return {"error": "No real broker connected"}

# ── FastAPI App ──────────────────────────────────────────────────────────────

engine = TradingEngine()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await engine.start()
    yield
    await engine.stop()

app = FastAPI(title="Trading Bot Dashboard", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

clients: List[WebSocket] = []

async def broadcast():
    if not clients:
        return
    state = engine.get_state()
    dead = []
    for ws in clients:
        try:
            await ws.send_json(state)
        except Exception:
            dead.append(ws)
    for ws in dead:
        if ws in clients:
            clients.remove(ws)

@app.on_event("startup")
async def _starter():
    asyncio.create_task(_broadcaster())

async def _broadcaster():
    while True:
        await asyncio.sleep(1)
        await broadcast()

@app.get("/", response_class=HTMLResponse)
def index():
    with open("templates/index.html") as f:
        return HTMLResponse(f.read())

@app.get("/api/state")
def api_state():
    return engine.get_state()

@app.post("/api/start")
async def api_start():
    await engine.start()
    return {"status": "started"}

@app.post("/api/stop")
async def api_stop():
    await engine.stop()
    return {"status": "stopped"}

@app.post("/api/order")
async def api_order(symbol: str, qty: float, side: str, order_type: str = "market", limit_price: Optional[float] = None):
    result = engine.submit_order(symbol, qty, side, order_type, limit_price)
    return result

@app.websocket("/ws")
async def websocket(ws: WebSocket):
    await ws.accept()
    clients.append(ws)
    await ws.send_json(engine.get_state())
    try:
        while True:
            msg = await ws.receive_text()
            data = json.loads(msg)
            cmd = data.get("cmd")
            if cmd == "start":
                await engine.start()
            elif cmd == "stop":
                await engine.stop()
            elif cmd == "ping":
                await ws.send_json({"pong": True})
    except WebSocketDisconnect:
        if ws in clients:
            clients.remove(ws)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
