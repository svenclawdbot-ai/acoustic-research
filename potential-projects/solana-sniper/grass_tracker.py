import asyncio
import json
from datetime import datetime
from typing import Optional, Dict

class GrassTracker:
    """
    Track Grass.io earnings and conversion
    
    Grass.io converts bandwidth usage to GRASS tokens
    Current token price: ~$0.30 USD (varies)
    """
    
    def __init__(self):
        self.points = 100000  # User's current balance
        self.token_price_usd = 0.30  # Approximate current price
        self.conversion_rate = 1000  # Estimated points per token (varies by epoch)
        self.tokens_earned = self.points / self.conversion_rate
        self.usd_value = self.tokens_earned * self.token_price_usd
        
    def get_stats(self) -> Dict:
        """Get current Grass stats"""
        return {
            "points": self.points,
            "estimated_tokens": round(self.tokens_earned, 2),
            "token_price_usd": self.token_price_usd,
            "usd_value": round(self.usd_value, 2),
            "gbp_value": round(self.usd_value * 0.79, 2),  # ~£0.79 per $1
            "monthly_estimate_gbp": 15,  # Estimated based on typical earnings
            "status": "Earning",
            "last_update": datetime.now().isoformat()
        }
    
    def update_price(self, new_price: float):
        """Update token price"""
        self.token_price_usd = new_price
        self.usd_value = self.tokens_earned * new_price

# Global instance
grass_tracker = GrassTracker()
