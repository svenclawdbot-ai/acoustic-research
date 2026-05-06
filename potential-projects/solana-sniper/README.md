# Solana Sniper Bot

Ultra-fast Solana token sniper using Taleb/Antifragility principles + Active Inference.

## Philosophy
- **Barbell Strategy**: 90% cash, 10% high-conviction snipes
- **Convexity**: Small bets, massive asymmetric upside (3-5x targets)
- **Via Negativa**: 30% hard stop loss, survive to trade again
- **Never Predict, Position**: Scan for setup quality, not token hype

## Architecture

```
src/
├── main.py                 # Entry point
├── config/
│   ├── settings.py         # Configuration
│   └── wallet.py           # Hot wallet management
├── signal/
│   ├── dex_screener.py     # DEX Screener API integration
│   ├── filters.py          # Token filtering criteria
│   └── monitor.py          # New launch detection
├── inference/
│   ├── bayesian.py         # Bayesian surprise calculator
│   ├── precision.py        # Confidence scoring
│   └── black_swan.py       # Anomaly detection
├── execution/
│   ├── jupiter.py          # Jupiter DEX aggregation
│   ├── jito.py             # MEV protection bundles
│   ├── position.py         # Position manager
│   └── risk.py             # Stop loss / take profit
├── utils/
│   ├── logger.py           # Logging
│   └── helpers.py          # Utilities
└── tests/                  # Test suite
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure wallet
export SNIPER_PRIVATE_KEY="your_private_key"
export SNIPER_RPC_URL="https://api.mainnet-beta.solana.com"

# Run in dry-run mode first
python src/main.py --dry-run

# Live trading (limited funds only!)
python src/main.py --live --max-position 0.1
```

## Risk Management

- **Max Position Size**: Configurable (default 0.1 SOL)
- **Stop Loss**: 30% hard stop
- **Take Profit**: 3x (1/3), 5x (1/3), runner (1/3)
- **Daily Loss Limit**: Pause after 3 consecutive losses
- **Circuit Breaker**: Auto-stop on unusual RPC errors

## Disclaimer

This is experimental software. Only trade funds you can afford to lose.
