#!/usr/bin/env python3
"""
Solana Sniper Bot - Main Entry Point

Ultra-fast token sniper using:
- Taleb/Antifragility principles (convexity, barbell, via negativa)
- Active Inference (Bayesian surprise minimization, precision weighting)
- DEX Screener for signal detection
- Jupiter + Jito for execution
- Safety checks (honeypot detection)
"""

import asyncio
import argparse
import signal
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from solana.rpc.async_api import AsyncClient

from config.settings import settings
from config.wallet import WalletManager, verify_wallet_setup
from signal.dex_screener import DEXScreenerClient
from signal.filters import TokenFilters
from inference.bayesian import BayesianInference
from execution.position import PositionManager
from execution.jupiter import JupiterClient, buy_token, sell_token
from execution.jito import JitoClient, execute_sniper_bundle
from execution.safety import verify_token_before_buy, TokenSafetyChecker
from dashboard.server import init_dashboard, close_dashboard, update_stats, log_activity
from utils.logger import setup_logger

logger = setup_logger("main")


class SniperBot:
    """Main sniper bot orchestrator"""
    
    def __init__(self):
        self.filters = TokenFilters()
        self.inference = BayesianInference()
        self.safety = None  # Initialized in run()
        self.wallet = None  # Initialized in run()
        self.rpc_client = None
        self.jupiter = None
        self.jito = None
        self.positions = None
        self.running = False
        self.stats = {
            "scanned": 0,
            "filtered": 0,
            "inferred": 0,
            "safety_checked": 0,
            "safety_failed": 0,
            "attempted": 0,
            "successful": 0,
            "positions": []
        }
    
    async def handle_new_pair(self, pair):
        """Process new token pair"""
        self.stats["scanned"] += 1
        
        logger.debug(f"New pair: {pair.base_token[:8]}... age={pair.age_seconds}s "
                    f"liq=${pair.liquidity_usd:,.0f}")
        
        # Update dashboard
        await log_activity("scan", f"New pair detected: {pair.base_token[:8]}...")
        
        # Layer 1: Filters (fast rejection)
        filter_result = self.filters.evaluate(pair)
        
        if not filter_result.passed:
            logger.debug(f"Filtered: {pair.base_token[:8]}... score={filter_result.score:.2f}")
            return
        
        self.stats["filtered"] += 1
        await log_activity("filter", f"Passed filters: {pair.base_token[:8]}... score={filter_result.score:.2f}")
        
        # Layer 2: Bayesian Inference
        inference = self.inference.infer(pair, filter_result.score)
        
        if inference.recommendation != "BUY":
            logger.debug(f"Inference skip: {pair.base_token[:8]}... "
                        f"conf={inference.confidence:.2f}")
            return
        
        self.stats["inferred"] += 1
        
        # Add to dashboard signals
        await add_signal({
            "token": pair.base_token,
            "confidence": inference.confidence,
            "score": filter_result.score,
            "age": pair.age_seconds or 0,
            "liquidity": pair.liquidity_usd,
            "volume_5m": pair.volume_5m
        })
        
        # Layer 3: Safety Checks (critical!)
        if not settings.dry_run:
            safety = await verify_token_before_buy(
                self.rpc_client,
                pair.base_token,
                self.wallet.pubkey,
                {"liquidity_usd": pair.liquidity_usd}
            )
            
            self.stats["safety_checked"] += 1
            
            if not safety.is_safe:
                self.stats["safety_failed"] += 1
                logger.warning(f"🚫 UNSAFE: {pair.base_token[:8]}... "
                             f"risk={safety.risk_score} warnings={safety.warnings}")
                await log_activity("warning", f"Safety blocked: {pair.base_token[:8]}...")
                return
        
        # Execute trade
        await self.execute_trade(pair, inference)
    
    async def execute_trade(self, pair, inference):
        """Execute buy order with full stack"""
        self.stats["attempted"] += 1
        
        # Calculate position size based on confidence
        available = self.wallet.get_available_for_trading()
        position_size = min(
            settings.max_position_sol * inference.confidence,
            available
        )
        
        if position_size < 0.01:
            logger.warning(f"Position too small: {position_size:.4f} SOL")
            return
        
        logger.info(f"🎯 EXECUTING: {pair.base_token[:8]}... "
                   f"size={position_size:.3f}SOL conf={inference.confidence:.2f}")
        
        if settings.dry_run:
            logger.info(f"💰 DRY RUN: Would buy {pair.base_token[:8]}... "
                       f"for {position_size:.3f}SOL")
            self.stats["successful"] += 1
            
            # Log to dashboard
            await log_activity("buy", f"DRY RUN: Simulated buy {pair.base_token[:8]}... for {position_size:.3f} SOL")
            
            # Add to positions
            await add_position({
                "token": pair.base_token,
                "entry": pair.price_usd,
                "size": position_size,
                "pnl": 0,
                "status": "OPEN"
            })
            
            return
        
        # Allocate funds
        if not self.wallet.allocate_funds(position_size):
            return
        
        try:
            # Execute via Jupiter + Jito
            result = await execute_sniper_bundle(
                jito=self.jito,
                jupiter=self.jupiter,
                wallet=self.wallet.keypair,
                token_mint=pair.base_token,
                amount_sol=position_size,
                slippage_bps=settings.max_slippage_bps
            )
            
            if result.success:
                self.stats["successful"] += 1
                logger.info(f"✅ SUCCESS: {pair.base_token[:8]}... "
                           f"bundle={result.bundle_id[:16] if result.bundle_id else 'N/A'}")
                
                # Log to dashboard
                await log_activity("success", f"Trade executed: {pair.base_token[:8]}...")
                
                # Add to positions
                await add_position({
                    "token": pair.base_token,
                    "entry": pair.price_usd,
                    "size": position_size,
                    "pnl": 0,
                    "status": "OPEN"
                })
                
                # Track position
                await self.positions.open_position(
                    pair.base_token,
                    inference.confidence
                )
            else:
                logger.error(f"❌ FAILED: {pair.base_token[:8]}... error={result.error}")
                await log_activity("error", f"Trade failed: {pair.base_token[:8]}... - {result.error}")
                self.wallet.release_allocation(position_size)
                
        except Exception as e:
            logger.error(f"Execution error: {e}")
            await log_activity("error", f"Execution error: {str(e)}")
            self.wallet.release_allocation(position_size)
    
    async def update_dashboard_loop(self):
        """Periodically update dashboard with stats"""
        while self.running:
            try:
                if hasattr(self, 'dashboard') and self.dashboard:
                    from dashboard.server import DashboardStats
                    
                    await self.dashboard.update_stats(DashboardStats(
                        scanned=self.stats['scanned'],
                        filtered=self.stats['filtered'],
                        inferred=self.stats['inferred'],
                        safety_checked=self.stats['safety_checked'],
                        safety_failed=self.stats['safety_failed'],
                        trades_attempted=self.stats['attempted'],
                        trades_successful=self.stats['successful'],
                        balance_sol=self.wallet.balance_sol if self.wallet else 0,
                        available_sol=self.wallet.get_available_for_trading() if self.wallet else 0
                    ))
                
                await asyncio.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"Dashboard update error: {e}")
                await asyncio.sleep(10)
    
    async def monitor_positions(self):
        """Background task to check position exits"""
        while self.running:
            try:
                for token_address, position in list(self.positions.positions.items()):
                    if position.status != "OPEN":
                        continue
                    
                    # Get current price (from Jupiter or DEX Screener)
                    # TODO: Implement price fetching
                    current_price = position.entry_price  # Placeholder
                    
                    exit_reason = await self.positions.check_exits(
                        token_address, current_price
                    )
                    
                    if exit_reason:
                        logger.info(f"Exit triggered: {token_address[:8]}... reason={exit_reason}")
                        await log_activity("sell", f"Position closed: {token_address[:8]}... ({exit_reason})")
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Position monitor error: {e}")
                await asyncio.sleep(10)
    
    async def run(self):
        """Main bot loop"""
        self.running = True
        
        # Initialize dashboard server
        dashboard_enabled = getattr(settings, 'dashboard_enabled', True)
        dashboard_port = getattr(settings, 'dashboard_port', 8080)
        
        if dashboard_enabled:
            from dashboard.server import DashboardServer
            self.dashboard = DashboardServer(port=dashboard_port)
            await self.dashboard.start()
        
        # Initialize RPC client
        self.rpc_client = AsyncClient(settings.rpc_url)
        
        # Initialize wallet
        self.wallet = WalletManager()
        await verify_wallet_setup(self.wallet, self.rpc_client)
        
        # Initialize safety checker
        self.safety = TokenSafetyChecker(self.rpc_client)
        
        # Initialize execution clients
        async with JupiterClient(self.rpc_client) as jupiter, \
                   JitoClient(self.rpc_client, self.wallet.pubkey) as jito:
            
            self.jupiter = jupiter
            self.jito = jito
            self.positions = PositionManager(self.rpc_client, self.wallet.keypair)
            
            logger.info("=" * 60)
            logger.info("🚀 Solana Sniper Bot Starting")
            logger.info("=" * 60)
            logger.info(f"Mode: {'DRY RUN ✓' if settings.dry_run else 'LIVE ⚠️'}")
            logger.info(f"Wallet: {str(self.wallet.pubkey)[:20]}...")
            logger.info(f"Balance: {self.wallet.balance_sol:.4f} SOL")
            logger.info(f"Max Position: {settings.max_position_sol} SOL")
            logger.info(f"Available: {self.wallet.get_available_for_trading():.4f} SOL")
            logger.info(f"Stop Loss: {settings.stop_loss_pct}%")
            logger.info(f"Take Profits: {settings.take_profit_1}x / {settings.take_profit_2}x")
            logger.info(f"Safety Checks: {'ENABLED' if not settings.dry_run else 'SKIPPED (dry run)'}")
            logger.info(f"Jito MEV Protection: {'ENABLED' if settings.use_jito else 'DISABLED'}")
            if dashboard_enabled:
                logger.info(f"Dashboard: http://localhost:{dashboard_port}")
            logger.info("=" * 60)
            
            if not settings.dry_run:
                logger.warning("⚠️  LIVE TRADING MODE - REAL FUNDS AT RISK")
                logger.warning("⚠️  98.6% of tokens fail - expect total loss on most trades")
                logger.info("=" * 60)
            
            # Start position monitor and dashboard updater
            monitor_task = asyncio.create_task(self.monitor_positions())
            dashboard_task = asyncio.create_task(self.update_dashboard_loop())
            
            try:
                async with DEXScreenerClient() as dex:
                    await dex.subscribe_new_pairs(self.handle_new_pair)
            except asyncio.CancelledError:
                logger.info("Bot stopped")
            except Exception as e:
                logger.error(f"Bot error: {e}")
            finally:
                monitor_task.cancel()
                dashboard_task.cancel()
                try:
                    await monitor_task
                    await dashboard_task
                except asyncio.CancelledError:
                    pass
        
        # Cleanup
        await self.rpc_client.close()
        
        if dashboard_enabled and hasattr(self, 'dashboard'):
            await self.dashboard.stop()
        
        self.print_stats()
        
        # Initialize wallet
        self.wallet = WalletManager()
        await verify_wallet_setup(self.wallet, self.rpc_client)
        
        # Initialize safety checker
        self.safety = TokenSafetyChecker(self.rpc_client)
        
        # Initialize execution clients
        async with JupiterClient(self.rpc_client) as jupiter, \
                   JitoClient(self.rpc_client, self.wallet.pubkey) as jito:
            
            self.jupiter = jupiter
            self.jito = jito
            self.positions = PositionManager(self.rpc_client, self.wallet.keypair)
            
            logger.info("=" * 60)
            logger.info("🚀 Solana Sniper Bot Starting")
            logger.info("=" * 60)
            logger.info(f"Mode: {'DRY RUN ✓' if settings.dry_run else 'LIVE ⚠️'}")
            logger.info(f"Wallet: {str(self.wallet.pubkey)[:20]}...")
            logger.info(f"Balance: {self.wallet.balance_sol:.4f} SOL")
            logger.info(f"Max Position: {settings.max_position_sol} SOL")
            logger.info(f"Available: {self.wallet.get_available_for_trading():.4f} SOL")
            logger.info(f"Stop Loss: {settings.stop_loss_pct}%")
            logger.info(f"Take Profits: {settings.take_profit_1}x / {settings.take_profit_2}x")
            logger.info(f"Safety Checks: {'ENABLED' if not settings.dry_run else 'SKIPPED (dry run)'}")
            logger.info(f"Jito MEV Protection: {'ENABLED' if settings.use_jito else 'DISABLED'}")
            logger.info("=" * 60)
            
            if not settings.dry_run:
                logger.warning("⚠️  LIVE TRADING MODE - REAL FUNDS AT RISK")
                logger.warning("⚠️  98.6% of tokens fail - expect total loss on most trades")
                logger.info("=" * 60)
            
            # Start position monitor and dashboard updater
            monitor_task = asyncio.create_task(self.monitor_positions())
            dashboard_task = asyncio.create_task(self.update_dashboard_loop())
            
            try:
                async with DEXScreenerClient() as dex:
                    await dex.subscribe_new_pairs(self.handle_new_pair)
            except asyncio.CancelledError:
                logger.info("Bot stopped")
            except Exception as e:
                logger.error(f"Bot error: {e}")
            finally:
                monitor_task.cancel()
                try:
                    await monitor_task
                except asyncio.CancelledError:
                    pass
        
        await self.rpc_client.close()
        self.print_stats()
    
    def print_stats(self):
        """Print session statistics"""
        logger.info("=" * 60)
        logger.info("📊 SESSION STATISTICS")
        logger.info("=" * 60)
        logger.info(f"Pairs Scanned: {self.stats['scanned']}")
        logger.info(f"Passed Filters: {self.stats['filtered']}")
        logger.info(f"Passed Inference: {self.stats['inferred']}")
        logger.info(f"Safety Checks: {self.stats['safety_checked']}")
        logger.info(f"Safety Failed: {self.stats['safety_failed']}")
        logger.info(f"Trades Attempted: {self.stats['attempted']}")
        logger.info(f"Trades Successful: {self.stats['successful']}")
        if self.stats['attempted'] > 0:
            success_rate = self.stats['successful'] / self.stats['attempted'] * 100
            logger.info(f"Success Rate: {success_rate:.1f}%")
        logger.info("=" * 60)
    
    def stop(self):
        """Graceful shutdown"""
        logger.info("Stopping bot...")
        self.running = False


def main():
    parser = argparse.ArgumentParser(description="Solana Sniper Bot")
    parser.add_argument("--live", action="store_true", help="Live trading mode")
    parser.add_argument("--dry-run", action="store_true", help="Simulation mode (default)")
    parser.add_argument("--max-position", type=float, default=0.1, help="Max position size in SOL")
    
    args = parser.parse_args()
    
    # Override settings if needed
    if args.live:
        settings.dry_run = False
        settings.max_position_sol = args.max_position
    
    bot = SniperBot()
    
    # Signal handlers
    def signal_handler(signum, frame):
        bot.stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        bot.print_stats()


if __name__ == "__main__":
    main()
