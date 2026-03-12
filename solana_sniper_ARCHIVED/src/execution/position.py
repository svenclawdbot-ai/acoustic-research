import asyncio
from typing import Optional, Dict
from dataclasses import dataclass
from decimal import Decimal

from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction

from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger("position")


@dataclass
class Position:
    """Active trading position"""
    token_address: str
    entry_price: float
    entry_time: float
    size_sol: float
    size_tokens: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    tx_signature: Optional[str] = None
    
    # State tracking
    highest_price: float = 0.0
    partial_exits: int = 0
    status: str = "OPEN"  # OPEN, CLOSED


class PositionManager:
    """
    Position manager using Taleb's barbell strategy
    
    Key principles:
    - Limited position size (convexity through small bets)
    - Asymmetric payoff (big upside, capped downside)
    - No averaging down (never add to losers)
    - Trailing stops after 2x
    """
    
    def __init__(self, client: AsyncClient, wallet: Keypair):
        self.client = client
        self.wallet = wallet
        self.positions: Dict[str, Position] = {}
        self.daily_losses = 0
        self.last_reset_day = None
        
    async def open_position(self, token_address: str, 
                           confidence: float) -> Optional[Position]:
        """
        Open new position with size based on confidence
        Uses Kelly Criterion-inspired sizing
        """
        # Check daily loss limit
        if self.daily_losses >= settings.daily_loss_limit:
            logger.warning("Daily loss limit reached. No new positions.")
            return None
        
        # Calculate position size based on confidence
        # Higher confidence = larger position (still within limits)
        base_size = settings.max_position_sol
        position_size = base_size * confidence
        
        # Ensure minimum viable position
        if position_size < 0.01:
            logger.info("Position size too small")
            return None
        
        # Get current price
        price = await self._get_token_price(token_address)
        if not price:
            return None
        
        # Calculate exit levels
        stop_loss = price * (1 - settings.stop_loss_pct / 100)
        tp1 = price * settings.take_profit_1
        tp2 = price * settings.take_profit_2
        
        position = Position(
            token_address=token_address,
            entry_price=price,
            entry_time=asyncio.get_event_loop().time(),
            size_sol=position_size,
            size_tokens=position_size / price,
            stop_loss=stop_loss,
            take_profit_1=tp1,
            take_profit_2=tp2,
            highest_price=price
        )
        
        self.positions[token_address] = position
        logger.info(f"Opened position: {token_address[:8]}... "
                   f"size={position_size:.3f}SOL "
                   f"SL={stop_loss:.6f} TP1={tp1:.6f}")
        
        return position
    
    async def check_exits(self, token_address: str, current_price: float) -> Optional[str]:
        """
        Check if position should be exited
        Returns: 'STOP_LOSS', 'TP1', 'TP2', 'TRAILING', or None
        """
        if token_address not in self.positions:
            return None
        
        pos = self.positions[token_address]
        
        if pos.status != "OPEN":
            return None
        
        # Update highest price for trailing stop
        if current_price > pos.highest_price:
            pos.highest_price = current_price
        
        # Check stop loss (hard rule - never move this)
        if current_price <= pos.stop_loss:
            await self._close_position(token_address, current_price, "STOP_LOSS")
            return "STOP_LOSS"
        
        # Check take profit levels
        pnl_pct = (current_price - pos.entry_price) / pos.entry_price * 100
        
        if pnl_pct >= 200 and pos.partial_exits == 0:
            # 2x+ - move stop to breakeven (free roll)
            pos.stop_loss = pos.entry_price * 1.05  # 5% profit lock
            logger.info(f"Trailing stop activated for {token_address[:8]}...")
        
        if current_price >= pos.take_profit_2 and pos.partial_exits < 2:
            # Hit 5x - take another 1/3
            await self._partial_exit(token_address, current_price, 1/3)
            pos.partial_exits += 1
            return "TP2"
        
        if current_price >= pos.take_profit_1 and pos.partial_exits < 1:
            # Hit 3x - take 1/3 profit
            await self._partial_exit(token_address, current_price, 1/3)
            pos.partial_exits += 1
            return "TP1"
        
        # Trailing stop after 3x (20% pullback from highs)
        if pos.partial_exits >= 1:
            trailing_stop = pos.highest_price * 0.8
            if current_price <= trailing_stop:
                await self._close_position(token_address, current_price, "TRAILING")
                return "TRAILING"
        
        return None
    
    async def _partial_exit(self, token_address: str, price: float, fraction: float):
        """Execute partial position exit"""
        pos = self.positions[token_address]
        exit_amount = pos.size_tokens * fraction
        
        logger.info(f"Partial exit: {token_address[:8]}... "
                   f"fraction={fraction:.0%} price={price:.6f}")
        
        # TODO: Execute swap via Jupiter
        # For now, just log
        pos.size_tokens -= exit_amount
    
    async def _close_position(self, token_address: str, price: float, reason: str):
        """Close entire position"""
        pos = self.positions[token_address]
        
        pnl_pct = (price - pos.entry_price) / pos.entry_price * 100
        pnl_sol = pos.size_sol * (pnl_pct / 100)
        
        logger.info(f"Close position: {token_address[:8]}... "
                   f"reason={reason} pnl={pnl_pct:+.1f}% ({pnl_sol:+.3f} SOL)")
        
        # TODO: Execute remaining swap via Jupiter
        
        pos.status = "CLOSED"
        
        # Track losses for daily limit
        if pnl_pct < 0:
            self.daily_losses += 1
    
    async def _get_token_price(self, token_address: str) -> Optional[float]:
        """Get current token price from Jupiter or DEX Screener"""
        # TODO: Implement price fetch
        return None
    
    def get_position_summary(self) -> dict:
        """Get summary of all positions"""
        open_pos = [p for p in self.positions.values() if p.status == "OPEN"]
        
        return {
            "open_positions": len(open_pos),
            "daily_losses": self.daily_losses,
            "daily_loss_limit": settings.daily_loss_limit,
            "positions": [
                {
                    "token": p.token_address[:8] + "...",
                    "entry": p.entry_price,
                    "size_sol": p.size_sol,
                    "pnl_pct": None  # Would need current price
                }
                for p in open_pos
            ]
        }
