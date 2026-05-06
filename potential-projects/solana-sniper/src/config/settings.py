import os
from typing import List, Optional


class Settings:
    """Sniper bot configuration"""
    
    def __init__(self):
        # Wallet
        self.private_key = os.getenv("SNIPER_PRIVATE_KEY", "")
        self.rpc_url = os.getenv("SNIPER_RPC_URL", "https://api.mainnet-beta.solana.com")
        self.wss_url = os.getenv("SNIPER_WSS_URL", None)
        
        # Risk Management
        self.max_position_sol = float(os.getenv("SNIPER_MAX_POSITION", "0.1"))
        self.stop_loss_pct = float(os.getenv("SNIPER_STOP_LOSS", "30.0"))
        self.take_profit_1 = float(os.getenv("SNIPER_TP1", "3.0"))
        self.take_profit_2 = float(os.getenv("SNIPER_TP2", "5.0"))
        self.daily_loss_limit = int(os.getenv("SNIPER_DAILY_LOSS_LIMIT", "3"))
        
        # Barbell Allocation
        self.cash_reserve_pct = float(os.getenv("SNIPER_CASH_RESERVE", "80.0"))
        self.sniper_allocation_pct = float(os.getenv("SNIPER_ALLOCATION", "20.0"))
        
        # Execution
        self.use_jito = os.getenv("SNIPER_USE_JITO", "true").lower() == "true"
        self.jito_tip_lamports = int(os.getenv("SNIPER_JITO_TIP", "10000"))
        self.max_slippage_bps = int(os.getenv("SNIPER_MAX_SLIPPAGE", "100"))
        self.priority_fee_microlamports = int(os.getenv("SNIPER_PRIORITY_FEE", "10000"))
        
        # Signal Detection
        self.min_liquidity_usd = float(os.getenv("SNIPER_MIN_LIQUIDITY", "1000.0"))
        self.min_volume_5m = float(os.getenv("SNIPER_MIN_VOLUME_5M", "5000.0"))
        self.max_entry_delay_seconds = int(os.getenv("SNIPER_MAX_ENTRY_DELAY", "120"))
        
        # Bayesian Inference
        self.confidence_threshold = float(os.getenv("SNIPER_CONFIDENCE", "0.7"))
        self.surprise_threshold = float(os.getenv("SNIPER_SURPRISE_THRESHOLD", "2.0"))
        
        # DEX Screener
        self.dex_screener_api = os.getenv("DEXSCREENER_API", "https://api.dexscreener.com/latest/dex")
        self.poll_interval_seconds = int(os.getenv("SNIPER_POLL_INTERVAL", "5"))
        
        # Filters
        self.blacklisted_tokens = []
        self.require_verified = os.getenv("SNIPER_REQUIRE_VERIFIED", "false").lower() == "true"
        self.max_holder_concentration = float(os.getenv("SNIPER_MAX_HOLDER_CONC", "50.0"))
        
        # Dashboard
        self.dashboard_enabled = os.getenv("DASHBOARD_ENABLED", "true").lower() == "true"
        self.dashboard_port = int(os.getenv("DASHBOARD_PORT", "8080"))
        
        # Testing
        self.dry_run = os.getenv("SNIPER_DRY_RUN", "true").lower() == "true"
        self.log_level = os.getenv("SNIPER_LOG_LEVEL", "INFO")


settings = Settings()
