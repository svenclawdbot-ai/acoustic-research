# Solana Sniper Bot Dashboard

Real-time web dashboard for monitoring the sniper bot.

## Features

- **Live Statistics** - Real-time counters for scanned pairs, filters, trades
- **Interactive Charts** - Visualize detection activity over time
- **Position Tracking** - Monitor active positions with PnL
- **Activity Log** - Color-coded event stream
- **Signal Feed** - High-confidence trading opportunities

## Quick Start

The dashboard starts automatically with the bot:

```bash
python src/main.py --dry-run
```

Then open: **http://localhost:8080**

## Screenshots

```
┌─────────────────────────────────────────────────────────────┐
│  🎯 SNIPER.BOT          [Stats Cards: Scanned/Filtered/AI]  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📈 Detection Activity Chart                                │
│  ═══════════════════════════════════════════════════════   │
│                                                             │
│                                                             │
├──────────────────┬──────────────────┬───────────────────────┤
│ Active Positions │ Recent Activity  │ Top Signals           │
│ ──────────────── │ ──────────────── │ ───────────────────── │
│ Token | Entry    │ 🟢 Buy executed  │ TOKEN 85% conf       │
│ ...   | $0.001   │ 🔴 Sell triggered│ TOKEN 78% conf       │
│                  │ 🔵 New pair      │                      │
└──────────────────┴──────────────────┴───────────────────────┘
```

## Architecture

```
Dashboard Server (aiohttp)
    ├── WebSocket (/ws) - Real-time updates
    ├── REST API (/api/*) - Stats, positions, history
    └── Static Files (/static) - CSS, JS
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/stats` | Current statistics |
| `GET /api/positions` | Active positions |
| `GET /api/activities` | Recent activity log |
| `GET /api/signals` | Trading signals |
| `GET /api/history` | Historical chart data |
| `WS /ws` | WebSocket for live updates |

## WebSocket Events

```json
// Stats update
{"type": "stats", "data": {"scanned": 100, "filtered": 10, ...}}

// New activity
{"type": "activity", "data": {"type": "buy", "message": "...", "time": "..."}}

// New signal
{"type": "signal", "data": {"token": "...", "confidence": 0.85, ...}}

// New position
{"type": "position", "data": {"token": "...", "entry": "...", ...}}
```

## Configuration

In your `.env` file:

```bash
# Enable dashboard
DASHBOARD_ENABLED=true
DASHBOARD_PORT=8080
```

## Customization

### Change Port
```bash
export DASHBOARD_PORT=3000
python src/main.py
```

### Disable Dashboard
```bash
export DASHBOARD_ENABLED=false
python src/main.py
```

### Access via Tailscale
If using Tailscale, the dashboard is accessible from any device on your tailnet:
```
http://your-hostname:8080
```

## Development

### Frontend
- Edit `templates/index.html` for structure
- Edit `static/css/style.css` for styling
- Edit `static/js/dashboard.js` for interactivity

### Backend
- Edit `server.py` to add API endpoints
- Integrate with bot via `update_stats()`, `log_activity()`, etc.

## Troubleshooting

**Dashboard not loading?**
- Check if port 8080 is available: `lsof -i :8080`
- Try a different port: `DASHBOARD_PORT=3000`

**WebSocket not connecting?**
- Check browser console for errors
- Ensure firewall allows the port

**Stats not updating?**
- Check bot logs for errors
- Verify WebSocket connection in browser dev tools
