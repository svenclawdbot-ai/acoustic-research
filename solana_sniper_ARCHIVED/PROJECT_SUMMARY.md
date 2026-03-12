# Solana Sniper Bot - Project Summary

## Status: ✅ EXECUTION LAYER + DASHBOARD COMPLETE

## Overview
Ultra-fast Solana token sniper using Taleb/Antifragility principles + Active Inference.

## Quick Start

```bash
cd solana_sniper
./start.sh
```

Or manually:
```bash
pip install -r requirements.txt
cp .env.example .env  # Edit with your wallet key
python src/main.py --dry-run
```

Then open dashboard: http://localhost:8080

## Architecture (Complete)

```
solana_sniper/
├── src/
│   ├── main.py                 # Full orchestrator with dashboard
│   ├── config/
│   │   ├── settings.py         # Configuration management
│   │   └── wallet.py           # Hot wallet + barbell allocation
│   ├── signal/
│   │   ├── dex_screener.py     # DEX Screener API (5s polling)
│   │   └── filters.py          # 5-layer filtering system
│   ├── inference/
│   │   └── bayesian.py         # Active Inference engine
│   ├── execution/
│   │   ├── jupiter.py          # ✅ Jupiter DEX aggregation
│   │   ├── jito.py             # ✅ Jito MEV bundles
│   │   ├── position.py         # Taleb-style position manager
│   │   └── safety.py           # ✅ Honeypot + safety checks
│   └── utils/
│       └── logger.py           # Logging setup
├── dashboard/                  # ✅ NEW: Web Dashboard
│   ├── server.py               # aiohttp server with WebSocket
│   ├── templates/
│   │   └── index.html          # Dark crypto-themed UI
│   └── static/
│       ├── css/style.css       # Styling
│       └── js/dashboard.js     # Real-time updates
├── tests/
├── data/
├── logs/
├── requirements.txt
├── .env.example
├── start.sh                    # ✅ NEW: Easy startup script
├── README.md
├── PROJECT_SUMMARY.md
└── solana_sniper_research_report.md
```

## ✅ Dashboard Features (NEW!)

### Web Interface
- **Dark crypto-themed UI** - Professional trading dashboard aesthetic
- **Real-time updates** - WebSocket connection for live data
- **Responsive design** - Works on desktop, tablet, mobile

### Stats Cards
- Pairs Scanned (with live counter)
- Passed Filters (with rate %)
- AI Signals (inference count)
- Safety Checks (blocked count)
- Trades Executed (with success rate)
- Wallet Balance (with available funds)

### Charts
- **Activity Chart** - Line graph showing scanned/filtered/trades over time
- Time range selector (1H / 24H / 7D)
- Smooth animations and tooltips

### Panels
- **Active Positions** - Table with entry, size, PnL, status
- **Recent Activity** - Live log of bot actions
- **Top Signals** - High-confidence opportunities detected

### Notifications
- Toast notifications for important events
- Color-coded by type (success, warning, error, info)

## ✅ Implemented Components

### 1. Signal Detection (DEX Screener)
- Ultra-fast polling: 5-second intervals
- New pair subscription with automatic detection
- Age tracking: Entry within 30 seconds of launch
- Duplicate filtering

### 2. Multi-Layer Filtering
| Layer | Purpose | Status |
|-------|---------|--------|
| Basic Eligibility | Liquidity, age, blacklist | ✅ |
| Liquidity Analysis | Depth scoring ($1K-$50K+) | ✅ |
| Volume/Momentum | 5-min volume, tx count, price | ✅ |
| Age Scoring | Convexity bonus for early entry | ✅ |
| Anomaly Detection | Honey pot, rug pull, wash trading | ✅ |

### 3. Bayesian Inference (Active Inference)
- Prior: 1.4% success rate (from research)
- Likelihood: Price, volume, age signals
- Posterior: Updated success probability
- Surprise: KL divergence metric
- Expected Return: 3-6x based on confidence
- Risk-Adjusted Score: Precision-weighted

### 4. Safety Layer (Critical!)
- ✅ Honeypot detection (simulate sell before buy)
- ✅ Token account verification
- ✅ Authority checks (freeze/mint)
- ✅ Known scam pattern detection
- ✅ Risk scoring (0-100)

### 5. Execution Layer

#### Jupiter Integration
- Quote fetching across all Solana DEXs
- Route optimization for best price
- Slippage protection
- Priority fee estimation
- Swap transaction building

#### Jito Integration
- MEV protection (sandwich attack prevention)
- Bundle submission for atomic execution
- Direct validator connections
- Fallback to RPC if Jito fails

#### Wallet Management
- Hot wallet with keypair loading
- Balance tracking
- Barbell allocation enforcement (90/10 rule)
- Position size limits

### 6. Position Management (Taleb Principles)
- ✅ Convexity: Small bets, 3-5x targets
- ✅ Barbell: 90% cash reserve, 10% allocation
- ✅ Via Negativa: 30% hard stop loss
- ✅ Partial exits: 1/3 at 3x, 1/3 at 5x, runner
- ✅ Trailing stops after 2x
- ✅ Daily loss limit (3 losses = pause)

### 7. Dashboard (NEW!)
- ✅ Real-time WebSocket updates
- ✅ Dark crypto-themed UI
- ✅ Live charts and stats
- ✅ Activity logging
- ✅ Position tracking
- ✅ Signal display

## Research Key Findings (Documented)

### Token Success Rates
- **98.6%** of Pump.fun tokens fail/rug pull
- **1.4%** graduation rate ($69K market cap)
- **1.7%** of wallets make >$500/month

### Optimal Timing
- **0-30 seconds**: Ultra-early snipe window
- **10-50%**: Ideal 5-min momentum range
- **$10K+ volume**: Success predictor in first 5 min

### Execution Requirements
- Block time: ~400ms
- Latency target: Sub-100ms
- Jito bundles for MEV protection
- Priority fees: 10K-2M micro-lamports/CU

See `solana_sniper_research_report.md` for full analysis.

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Required
SNIPER_PRIVATE_KEY=your_base58_private_key
SNIPER_RPC_URL=https://api.mainnet-beta.solana.com

# Risk Management
SNIPER_MAX_POSITION=0.1              # SOL per trade
SNIPER_STOP_LOSS=30.0                # 30% stop loss
SNIPER_DAILY_LOSS_LIMIT=3            # Pause after 3 losses

# Execution Speed
SNIPER_USE_JITO=true                 # MEV protection
SNIPER_JITO_TIP=10000                # Lamports tip
SNIPER_MAX_SLIPPAGE=100              # 1% = 100 bps
SNIPER_PRIORITY_FEE=10000            # Micro-lamports/CU

# Dashboard
DASHBOARD_ENABLED=true               # Enable web UI
DASHBOARD_PORT=8080                  # Dashboard port

# Testing
SNIPER_DRY_RUN=true                  # Start with simulation!
SNIPER_LOG_LEVEL=DEBUG
```

## Execution Flow

```
New Token Detected
        ↓
[1] Basic Filters (liquidity, age, blacklist)
        ↓
[2] Multi-layer Scoring (volume, momentum, age)
        ↓
[3] Bayesian Inference (confidence, surprise, expected return)
        ↓
[4] Safety Checks (honeypot sim, authorities, risk score)
        ↓
[5] Position Sizing (barbell allocation, confidence-weighted)
        ↓
[6] Jupiter Quote (best route, slippage check)
        ↓
[7] Transaction Build (compute budget, priority fee)
        ↓
[8] Jito Bundle (MEV protection, tip, submit)
        ↓
[9] Position Tracking (stop loss, take profits, trailing)
        ↓
[10] Dashboard Update (WebSocket broadcast)
```

## Safety Warnings

⚠️ **98.6% of tokens fail** - This is high-risk gambling  
⚠️ **Only trade funds you can lose** - Expect total loss  
⚠️ **Start with dry-run** - Test for weeks before live  
⚠️ **Use dedicated hot wallet** - Never main/hardware wallet  
⚠️ **Honeypots are real** - Safety checks catch most but not all  

## Taleb Principles in Code

| Principle | Implementation |
|-----------|---------------|
| **Convexity** | Position sizes 0.01-0.1 SOL, 3-5x upside targets |
| **Barbell** | 90% cash reserve enforced, 10% max allocation |
| **Via Negativa** | 30% hard stop, daily loss limit, position tracking |
| **Optionality** | Enter <30s old (cheap option premium) |
| **Never predict** | Scan for setup quality, not token hype |

## Active Inference in Code

| Concept | Implementation |
|---------|---------------|
| **Minimize surprise** | Bayesian updating on price vs expectation |
| **Epistemic value** | Information gathering (volume, holders, age) |
| **Precision weighting** | Confidence scores determine entry/size |
| **Policy selection** | Multi-factor go/no-go decision |

## Dashboard Usage

### Access
- Local: http://localhost:8080
- Tailscale: http://your-hostname:8080
- Mobile-friendly responsive design

### Features
- **Real-time updates** every 5 seconds
- **Live charts** showing 60-minute history
- **Activity log** with color-coded events
- **Position tracking** with PnL
- **Signal feed** with confidence scores

### Time Range Selector
- 1H: Last hour (default)
- 24H: Last 24 hours
- 7D: Last 7 days

## Next Steps / Testing

### Phase 1: Dry Run (2 days as requested)
```bash
./start.sh
# Select option 1: Dry Run
```

**What to observe:**
- How many tokens are scanned?
- What's the filter pass rate?
- How many signals trigger?
- Are there false positives?
- Dashboard UI responsiveness

**Check the dashboard at:** http://localhost:8080

### Phase 2: Paper Trading
- Track what would be bought/sold
- Compare to actual price action
- Validate stop loss / take profit logic

### Phase 3: Micro Live Test
```bash
./start.sh
# Select option 2: Live Trading
# Confirm with "yes"
```

- Tiny positions ($0.01 SOL) to test execution
- Verify Jupiter swaps work
- Confirm Jito bundles land
- Check wallet balance tracking

### Phase 4: Gradual Scale
- Increase position size slowly
- Only after proven edge
- Continuous monitoring and adjustment

## File Overview

| File | Purpose | Lines |
|------|---------|-------|
| `main.py` | Orchestrator, main loop | ~350 |
| `dex_screener.py` | Signal detection | ~200 |
| `filters.py` | Token filtering | ~250 |
| `bayesian.py` | Inference engine | ~200 |
| `jupiter.py` | DEX aggregation | ~300 |
| `jito.py` | MEV bundles | ~350 |
| `safety.py` | Honeypot detection | ~250 |
| `position.py` | Position management | ~200 |
| `wallet.py` | Wallet operations | ~150 |
| `settings.py` | Configuration | ~80 |
| `server.py` | Dashboard backend | ~300 |
| `index.html` | Dashboard UI | ~400 |
| `style.css` | Dashboard styling | ~600 |
| `dashboard.js` | Dashboard frontend | ~500 |

**Total Code: ~4,300 lines**

## Potential Improvements

### High Priority
- [ ] Pre-signed transactions (refresh blockhash every 30s)
- [ ] Multiple keypairs for parallel submission
- [ ] Jito ShredStream integration (ultra-low latency)
- [ ] Custom RPC node (Helius/QuickNode)
- [ ] WebSocket price feeds for position monitoring

### Medium Priority
- [ ] Social signal integration (Twitter/Telegram)
- [ ] Wallet clustering analysis (detect coordinated sniping)
- [ ] Advanced honeypot detection (more simulation types)
- [ ] Machine learning for signal scoring
- [ ] PnL dashboard and analytics

### Low Priority
- [ ] Multi-wallet rotation
- [ ] Advanced position sizing (Kelly Criterion)
- [ ] Cross-chain sniping (Ethereum, BSC)
- [ ] Arbitrage between DEXs
- [ ] Automated strategy backtesting

## Disclaimer

This is experimental software for educational purposes. The 98.6% failure rate of Solana tokens means you will likely lose money. Use at your own risk. Not financial advice.

---

**Built by:** Sven 🦊  
**Framework:** OpenClaw + Solana  
**Philosophy:** Taleb + Active Inference  
**Status:** Ready for dry-run testing
