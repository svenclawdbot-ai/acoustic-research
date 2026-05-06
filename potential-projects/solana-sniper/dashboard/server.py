"""
Dashboard Server for Solana Sniper Bot
Serves real-time web dashboard
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

import aiohttp
from aiohttp import web
import aiohttp_cors

from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger("dashboard")


@dataclass
class DashboardStats:
    """Dashboard statistics"""
    scanned: int = 0
    filtered: int = 0
    inferred: int = 0
    safety_checked: int = 0
    safety_failed: int = 0
    trades_attempted: int = 0
    trades_successful: int = 0
    balance_sol: float = 0.0
    available_sol: float = 0.0
    timestamp: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DashboardServer:
    """Web dashboard server"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8080):
        self.host = host
        self.port = port
        self.app = web.Application()
        self.runner: Optional[web.AppRunner] = None
        self.site: Optional[web.TCPSite] = None
        
        # Current stats
        self.stats = DashboardStats()
        self.positions = []
        self.activities = []
        self.signals = []
        
        # WebSocket connections
        self.ws_connections = []
        
        # Setup routes
        self._setup_routes()
        
    def _setup_routes(self):
        """Setup HTTP routes"""
        # Static files
        self.app.router.add_static('/static/', 
                                   path=Path(__file__).parent / 'static',
                                   name='static')
        
        # HTML routes
        self.app.router.add_get('/', self.index)
        self.app.router.add_get('/dashboard', self.index)
        
        # API routes
        self.app.router.add_get('/api/stats', self.get_stats)
        self.app.router.add_get('/api/positions', self.get_positions)
        self.app.router.add_get('/api/activities', self.get_activities)
        self.app.router.add_get('/api/signals', self.get_signals)
        self.app.router.add_get('/api/history', self.get_history)
        
        # WebSocket for real-time updates
        self.app.router.add_get('/ws', self.websocket_handler)
        
        # Setup CORS
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*"
            )
        })
        
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    async def index(self, request: web.Request) -> web.Response:
        """Serve main dashboard HTML"""
        html_path = Path(__file__).parent / 'templates' / 'index.html'
        
        if not html_path.exists():
            return web.Response(
                text="Dashboard not found",
                status=404
            )
        
        return web.FileResponse(html_path)
    
    async def get_stats(self, request: web.Request) -> web.Response:
        """Get current statistics"""
        self.stats.timestamp = datetime.now().isoformat()
        
        return web.json_response({
            "success": True,
            "data": self.stats.to_dict()
        })
    
    async def get_positions(self, request: web.Request) -> web.Response:
        """Get active positions"""
        return web.json_response({
            "success": True,
            "data": self.positions
        })
    
    async def get_activities(self, request: web.Request) -> web.Response:
        """Get recent activities"""
        return web.json_response({
            "success": True,
            "data": self.activities[-50:]  # Last 50
        })
    
    async def get_signals(self, request: web.Request) -> web.Response:
        """Get recent signals"""
        return web.json_response({
            "success": True,
            "data": self.signals[-20:]  # Last 20
        })
    
    async def get_history(self, request: web.Request) -> web.Response:
        """Get historical data for charts"""
        # In production, fetch from database
        return web.json_response({
            "success": True,
            "data": {
                "labels": [],
                "scanned": [],
                "filtered": [],
                "trades": []
            }
        })
    
    async def websocket_handler(self, request: web.Request) -> web.WebSocketResponse:
        """Handle WebSocket connections for real-time updates"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.ws_connections.append(ws)
        logger.info(f"WebSocket client connected. Total: {len(self.ws_connections)}")
        
        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    # Handle client messages if needed
                    data = json.loads(msg.data)
                    logger.debug(f"WS received: {data}")
                    
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {ws.exception()}")
                    
        finally:
            self.ws_connections.remove(ws)
            logger.info(f"WebSocket client disconnected. Total: {len(self.ws_connections)}")
        
        return ws
    
    async def broadcast_update(self, data: Dict[str, Any]):
        """Broadcast update to all WebSocket clients"""
        if not self.ws_connections:
            return
        
        message = json.dumps(data)
        
        # Send to all connected clients
        for ws in self.ws_connections[:]:
            try:
                await ws.send_str(message)
            except Exception as e:
                logger.debug(f"Failed to send WS message: {e}")
                # Remove dead connections
                if ws in self.ws_connections:
                    self.ws_connections.remove(ws)
    
    # Update methods called by the bot
    
    async def update_stats(self, stats: DashboardStats):
        """Update dashboard statistics"""
        self.stats = stats
        await self.broadcast_update({
            "type": "stats",
            "data": stats.to_dict()
        })
    
    async def add_position(self, position: Dict[str, Any]):
        """Add new position"""
        position['timestamp'] = datetime.now().isoformat()
        self.positions.insert(0, position)
        
        # Keep only last 50
        if len(self.positions) > 50:
            self.positions = self.positions[:50]
        
        await self.broadcast_update({
            "type": "position",
            "data": position
        })
    
    async def add_activity(self, activity_type: str, message: str):
        """Add activity log"""
        activity = {
            "type": activity_type,
            "message": message,
            "time": datetime.now().isoformat()
        }
        
        self.activities.append(activity)
        
        # Keep only last 100
        if len(self.activities) > 100:
            self.activities = self.activities[-100:]
        
        await self.broadcast_update({
            "type": "activity",
            "data": activity
        })
    
    async def add_signal(self, signal: Dict[str, Any]):
        """Add trading signal"""
        signal['timestamp'] = datetime.now().isoformat()
        self.signals.insert(0, signal)
        
        # Keep only last 50
        if len(self.signals) > 50:
            self.signals = self.signals[:50]
        
        await self.broadcast_update({
            "type": "signal",
            "data": signal
        })
    
    async def start(self):
        """Start the dashboard server"""
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()
        
        logger.info(f"🌐 Dashboard running at http://{self.host}:{self.port}")
        logger.info(f"   Local: http://localhost:{self.port}")
        
        # If using Tailscale, show that URL too
        try:
            import socket
            hostname = socket.gethostname()
            logger.info(f"   Tailscale: http://{hostname}:{self.port}")
        except:
            pass
    
    async def stop(self):
        """Stop the dashboard server"""
        # Close all WebSocket connections
        for ws in self.ws_connections[:]:
            await ws.close()
        
        if self.site:
            await self.site.stop()
        
        if self.runner:
            await self.runner.cleanup()
        
        logger.info("Dashboard server stopped")


# Global dashboard instance
dashboard: Optional[DashboardServer] = None


async def init_dashboard(host: str = "127.0.0.1", port: int = None) -> DashboardServer:
    """Initialize dashboard server"""
    global dashboard
    
    if port is None:
        port = int(getattr(settings, 'dashboard_port', 8080))
    
    dashboard = DashboardServer(host, port)
    await dashboard.start()
    
    return dashboard


async def close_dashboard():
    """Close dashboard server"""
    global dashboard
    
    if dashboard:
        await dashboard.stop()
        dashboard = None


# Convenience functions for bot to call

async def update_stats(**kwargs):
    """Update dashboard stats from bot"""
    global dashboard
    if dashboard:
        stats = DashboardStats(**kwargs)
        await dashboard.update_stats(stats)


async def log_activity(activity_type: str, message: str):
    """Log activity to dashboard"""
    global dashboard
    if dashboard:
        await dashboard.add_activity(activity_type, message)


async def add_signal(signal_data: Dict[str, Any]):
    """Add signal to dashboard"""
    global dashboard
    if dashboard:
        await dashboard.add_signal(signal_data)


async def add_position(position_data: Dict[str, Any]):
    """Add position to dashboard"""
    global dashboard
    if dashboard:
        await dashboard.add_position(position_data)


# Run standalone
if __name__ == "__main__":
    async def main():
        server = await init_dashboard()
        
        try:
            # Keep running
            while True:
                await asyncio.sleep(1)
                
                # Simulate some data for testing
                await server.update_stats(DashboardStats(
                    scanned=server.stats.scanned + 1,
                    filtered=server.stats.filtered,
                    timestamp=datetime.now().isoformat()
                ))
                
        except KeyboardInterrupt:
            await server.stop()
    
    asyncio.run(main())
