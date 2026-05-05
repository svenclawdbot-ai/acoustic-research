# Alpaca Trading Client
# Handles real API calls to Alpaca (paper + live)

import os
from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderStatus
from alpaca.data.historical import StockHistoricalDataClient, CryptoHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.live import StockDataStream, CryptoDataStream


@dataclass
class AlpacaConfig:
    api_key: str
    secret_key: str
    paper: bool = True  # True = paper trading, False = live
    
    @property
    def base_url(self) -> str:
        return "https://paper-api.alpaca.markets" if self.paper else "https://api.alpaca.markets"


class AlpacaTrader:
    """Alpaca trading wrapper with paper/live support"""
    
    def __init__(self, config: AlpacaConfig):
        self.config = config
        self.trading_client = TradingClient(
            api_key=config.api_key,
            secret_key=config.secret_key,
            paper=config.paper
        )
        self.data_client = StockHistoricalDataClient(
            api_key=config.api_key,
            secret_key=config.secret_key
        )
        self.crypto_client = CryptoHistoricalDataClient(
            api_key=config.api_key,
            secret_key=config.secret_key
        )
        self._account = None
    
    def get_account(self) -> Dict:
        """Get account details (cash, equity, buying power)"""
        try:
            account = self.trading_client.get_account()
            return {
                "id": str(account.id),
                "cash": float(account.cash),
                "equity": float(account.equity),
                "buying_power": float(account.buying_power),
                "portfolio_value": float(account.portfolio_value),
                "status": account.status,
                "pattern_day_trader": account.pattern_day_trader,
                "trading_blocked": account.trading_blocked,
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_positions(self) -> List[Dict]:
        """Get all open positions"""
        try:
            positions = self.trading_client.get_all_positions()
            return [
                {
                    "symbol": p.symbol,
                    "side": "LONG" if float(p.qty) > 0 else "SHORT",
                    "qty": abs(float(p.qty)),
                    "avg_entry_price": float(p.avg_entry_price),
                    "current_price": float(p.current_price),
                    "market_value": float(p.market_value),
                    "unrealized_pl": float(p.unrealized_pl),
                    "unrealized_plpc": float(p.unrealized_plpc) * 100,
                    "change_today": float(p.change_today) * 100,
                }
                for p in positions
            ]
        except Exception as e:
            return [{"error": str(e)}]
    
    def get_orders(self, status: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Get recent orders"""
        try:
            request = GetOrdersRequest(
                status=status,
                limit=limit,
                nested=True
            )
            orders = self.trading_client.get_orders(filter=request)
            return [
                {
                    "id": str(o.id),
                    "symbol": o.symbol,
                    "side": o.side.value,
                    "qty": float(o.qty) if o.qty else 0,
                    "filled_qty": float(o.filled_qty) if o.filled_qty else 0,
                    "type": o.type.value,
                    "status": o.status.value,
                    "submitted_at": str(o.submitted_at) if o.submitted_at else None,
                    "filled_at": str(o.filled_at) if o.filled_at else None,
                    "filled_avg_price": float(o.filled_avg_price) if o.filled_avg_price else None,
                }
                for o in orders
            ]
        except Exception as e:
            return [{"error": str(e)}]
    
    def submit_market_order(self, symbol: str, qty: float, side: str) -> Dict:
        """Submit a market order"""
        try:
            order_side = OrderSide.BUY if side.upper() == "BUY" else OrderSide.SELL
            order = MarketOrderRequest(
                symbol=symbol,
                qty=abs(qty),
                side=order_side,
                time_in_force=TimeInForce.DAY
            )
            result = self.trading_client.submit_order(order)
            return {
                "id": str(result.id),
                "symbol": result.symbol,
                "side": result.side.value,
                "qty": float(result.qty),
                "status": result.status.value,
                "submitted_at": str(result.submitted_at),
            }
        except Exception as e:
            return {"error": str(e)}
    
    def submit_limit_order(self, symbol: str, qty: float, side: str, limit_price: float) -> Dict:
        """Submit a limit order"""
        try:
            order_side = OrderSide.BUY if side.upper() == "BUY" else OrderSide.SELL
            order = LimitOrderRequest(
                symbol=symbol,
                qty=abs(qty),
                side=order_side,
                time_in_force=TimeInForce.DAY,
                limit_price=limit_price
            )
            result = self.trading_client.submit_order(order)
            return {
                "id": str(result.id),
                "symbol": result.symbol,
                "side": result.side.value,
                "qty": float(result.qty),
                "limit_price": limit_price,
                "status": result.status.value,
                "submitted_at": str(result.submitted_at),
            }
        except Exception as e:
            return {"error": str(e)}
    
    def cancel_all_orders(self) -> Dict:
        """Cancel all open orders"""
        try:
            self.trading_client.cancel_orders()
            return {"success": True, "message": "All open orders cancelled"}
        except Exception as e:
            return {"error": str(e)}
    
    def close_position(self, symbol: str) -> Dict:
        """Close a specific position"""
        try:
            result = self.trading_client.close_position(symbol)
            return {
                "id": str(result.id),
                "symbol": result.symbol,
                "status": result.status.value,
            }
        except Exception as e:
            return {"error": str(e)}
    
    def close_all_positions(self) -> Dict:
        """Close all positions"""
        try:
            self.trading_client.close_all_positions(cancel_orders=True)
            return {"success": True, "message": "All positions closed"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_stock_bars(self, symbol: str, start: datetime, end: datetime, timeframe: TimeFrame = TimeFrame.Day) -> Dict:
        """Get historical stock bars"""
        try:
            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=timeframe,
                start=start,
                end=end
            )
            bars = self.data_client.get_stock_bars(request)
            df = bars.df
            return {
                "symbol": symbol,
                "bars": df.reset_index().to_dict('records') if not df.empty else []
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_crypto_bars(self, symbol: str, start: datetime, end: datetime, timeframe: TimeFrame = TimeFrame.Hour) -> Dict:
        """Get historical crypto bars"""
        try:
            request = CryptoBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=timeframe,
                start=start,
                end=end
            )
            bars = self.crypto_client.get_crypto_bars(request)
            df = bars.df
            return {
                "symbol": symbol,
                "bars": df.reset_index().to_dict('records') if not df.empty else []
            }
        except Exception as e:
            return {"error": str(e)}
    
    def is_connected(self) -> bool:
        """Check if API keys are valid"""
        try:
            self.trading_client.get_account()
            return True
        except Exception:
            return False


def create_from_env() -> Optional[AlpacaTrader]:
    """Create Alpaca trader from environment variables"""
    key = os.getenv("ALPACA_API_KEY")
    secret = os.getenv("ALPACA_SECRET_KEY")
    paper = os.getenv("ALPACA_PAPER", "true").lower() == "true"
    
    if not key or not secret:
        return None
    
    return AlpacaTrader(AlpacaConfig(api_key=key, secret_key=secret, paper=paper))
