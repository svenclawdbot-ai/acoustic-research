import asyncio
import aiohttp
from typing import Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime

from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger("dex_screener")


@dataclass
class TokenPair:
    """Token pair data from DEX Screener"""
    address: str
    base_token: str
    quote_token: str
    dex_id: str
    price_usd: float
    liquidity_usd: float
    volume_5m: float
    volume_1h: float
    volume_24h: float
    price_change_5m: float
    price_change_1h: float
    tx_count_5m: int
    created_at: Optional[datetime] = None
    
    @property
    def age_seconds(self) -> Optional[float]:
        if self.created_at:
            return (datetime.utcnow() - self.created_at).total_seconds()
        return None


class DEXScreenerClient:
    """Ultra-fast DEX Screener API client"""
    
    def __init__(self):
        self.base_url = settings.dex_screener_api
        self.session: Optional[aiohttp.ClientSession] = None
        self._lock = asyncio.Lock()
        
    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=5, connect=2)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_new_pairs(self, chain: str = "solana", limit: int = 50) -> List[TokenPair]:
        """Fetch newest pairs from Solana DEXs"""
        url = f"{self.base_url}/pairs/{chain}"
        
        try:
            async with self._lock:
                async with self.session.get(url) as resp:
                    if resp.status != 200:
                        logger.error(f"DEX Screener error: {resp.status}")
                        return []
                    
                    data = await resp.json()
                    pairs = []
                    
                    for pair_data in data.get("pairs", [])[:limit]:
                        try:
                            pair = self._parse_pair(pair_data)
                            if pair:
                                pairs.append(pair)
                        except Exception as e:
                            logger.debug(f"Parse error: {e}")
                            continue
                    
                    logger.info(f"Fetched {len(pairs)} pairs from DEX Screener")
                    return pairs
                    
        except asyncio.TimeoutError:
            logger.error("DEX Screener timeout")
            return []
        except Exception as e:
            logger.error(f"DEX Screener error: {e}")
            return []
    
    async def get_pair_by_token(self, token_address: str) -> Optional[TokenPair]:
        """Get specific token pair data"""
        url = f"{self.base_url}/tokens/{token_address}"
        
        try:
            async with self.session.get(url) as resp:
                if resp.status != 200:
                    return None
                
                data = await resp.json()
                pairs = data.get("pairs", [])
                
                if pairs:
                    # Return highest liquidity pair
                    best = max(pairs, key=lambda x: float(x.get("liquidity", {}).get("usd", 0) or 0))
                    return self._parse_pair(best)
                    
        except Exception as e:
            logger.error(f"Token lookup error: {e}")
        
        return None
    
    def _parse_pair(self, data: Dict) -> Optional[TokenPair]:
        """Parse DEX Screener pair data"""
        try:
            # Parse creation time
            created = data.get("pairCreatedAt")
            created_dt = None
            if created:
                created_dt = datetime.utcfromtimestamp(created / 1000)
            
            return TokenPair(
                address=data.get("pairAddress", ""),
                base_token=data.get("baseToken", {}).get("address", ""),
                quote_token=data.get("quoteToken", {}).get("address", ""),
                dex_id=data.get("dexId", ""),
                price_usd=float(data.get("priceUsd", 0) or 0),
                liquidity_usd=float(data.get("liquidity", {}).get("usd", 0) or 0),
                volume_5m=float(data.get("volume", {}).get("m5", 0) or 0),
                volume_1h=float(data.get("volume", {}).get("h1", 0) or 0),
                volume_24h=float(data.get("volume", {}).get("h24", 0) or 0),
                price_change_5m=float(data.get("priceChange", {}).get("m5", 0) or 0),
                price_change_1h=float(data.get("priceChange", {}).get("h1", 0) or 0),
                tx_count_5m=int(data.get("txns", {}).get("m5", {}).get("buys", 0) or 0) + \
                           int(data.get("txns", {}).get("m5", {}).get("sells", 0) or 0),
                created_at=created_dt
            )
        except (KeyError, ValueError, TypeError) as e:
            logger.debug(f"Parse error: {e}")
            return None
    
    async def subscribe_new_pairs(self, callback):
        """Continuously poll for new pairs"""
        seen_addresses = set()
        
        while True:
            try:
                pairs = await self.get_new_pairs()
                
                for pair in pairs:
                    if pair.address not in seen_addresses:
                        seen_addresses.add(pair.address)
                        # Only process very new pairs (< 5 min old)
                        if pair.age_seconds and pair.age_seconds < 300:
                            await callback(pair)
                
                # Cleanup old entries periodically
                if len(seen_addresses) > 10000:
                    seen_addresses = set(list(seen_addresses)[-5000:])
                
                await asyncio.sleep(settings.poll_interval_seconds)
                
            except Exception as e:
                logger.error(f"Subscription error: {e}")
                await asyncio.sleep(5)
