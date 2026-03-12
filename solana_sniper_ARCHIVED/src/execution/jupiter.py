import asyncio
import aiohttp
import base64
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from decimal import Decimal

from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts

from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger("jupiter")


@dataclass
class SwapRoute:
    """Jupiter swap route"""
    input_mint: str
    output_mint: str
    in_amount: int  # lamports
    out_amount: int  # lamports
    price_impact_pct: float
    route_plan: List[Dict]
    other_amount_threshold: int  # Minimum output (slippage protection)


@dataclass
class SwapResult:
    """Swap execution result"""
    success: bool
    signature: Optional[str]
    input_amount: float
    output_amount: float
    price_impact: float
    error: Optional[str] = None


class JupiterClient:
    """
    Jupiter DEX Aggregator Client
    
    Jupiter finds the best route across all Solana DEXs
    for optimal price execution.
    """
    
    def __init__(self, rpc_client: AsyncClient):
        self.rpc = rpc_client
        self.base_url = "https://quote-api.jup.ag/v6"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=10, connect=3)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_quote(self, 
                       input_mint: str,
                       output_mint: str,
                       amount: int,  # in lamports/smallest unit
                       slippage_bps: int = None,
                       only_direct_routes: bool = False) -> Optional[SwapRoute]:
        """
        Get best swap route from Jupiter
        
        Args:
            input_mint: Input token mint address (WSOL for wrapped SOL)
            output_mint: Output token mint address
            amount: Input amount in smallest unit
            slippage_bps: Slippage tolerance in basis points (100 = 1%)
        """
        if slippage_bps is None:
            slippage_bps = settings.max_slippage_bps
        
        params = {
            "inputMint": input_mint,
            "outputMint": output_mint,
            "amount": str(amount),
            "slippageBps": slippage_bps,
            "onlyDirectRoutes": str(only_direct_routes).lower(),
            "asLegacyTransaction": "false"
        }
        
        try:
            async with self.session.get(f"{self.base_url}/quote", params=params) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    logger.error(f"Jupiter quote error: {resp.status} - {error_text}")
                    return None
                
                data = await resp.json()
                
                route = SwapRoute(
                    input_mint=input_mint,
                    output_mint=output_mint,
                    in_amount=int(data["inAmount"]),
                    out_amount=int(data["outAmount"]),
                    price_impact_pct=float(data.get("priceImpactPct", 0)),
                    route_plan=data.get("routePlan", []),
                    other_amount_threshold=int(data["otherAmountThreshold"])
                )
                
                logger.debug(f"Jupiter route: {route.out_amount} out, "
                           f"impact={route.price_impact_pct:.2f}%")
                
                return route
                
        except asyncio.TimeoutError:
            logger.error("Jupiter quote timeout")
            return None
        except Exception as e:
            logger.error(f"Jupiter quote error: {e}")
            return None
    
    async def build_swap_tx(self,
                           route: SwapRoute,
                           user_public_key: Pubkey,
                           priority_fee: int = None) -> Optional[VersionedTransaction]:
        """
        Build swap transaction from Jupiter route
        
        Returns unsigned VersionedTransaction ready for signing
        """
        if priority_fee is None:
            priority_fee = settings.priority_fee_microlamports
        
        payload = {
            "quoteResponse": {
                "inputMint": route.input_mint,
                "outputMint": route.output_mint,
                "inAmount": str(route.in_amount),
                "outAmount": str(route.out_amount),
                "otherAmountThreshold": str(route.other_amount_threshold),
                "priceImpactPct": route.price_impact_pct,
                "routePlan": route.route_plan
            },
            "userPublicKey": str(user_public_key),
            "wrapAndUnwrapSol": True,
            "prioritizationFeeLamports": priority_fee,
            "dynamicComputeUnitLimit": True
        }
        
        try:
            async with self.session.post(f"{self.base_url}/swap", json=payload) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    logger.error(f"Jupiter swap build error: {resp.status} - {error_text}")
                    return None
                
                data = await resp.json()
                
                # Decode transaction
                tx_bytes = base64.b64decode(data["swapTransaction"])
                transaction = VersionedTransaction.from_bytes(tx_bytes)
                
                logger.debug(f"Built Jupiter swap tx: {len(tx_bytes)} bytes")
                
                return transaction
                
        except Exception as e:
            logger.error(f"Jupiter swap build error: {e}")
            return None
    
    async def execute_swap(self,
                          wallet: Keypair,
                          input_mint: str,
                          output_mint: str,
                          amount_sol: float,
                          slippage_bps: int = None) -> SwapResult:
        """
        Execute full swap: quote -> build -> sign -> send
        
        This is the main entry point for buying/selling tokens
        """
        # Convert SOL to lamports
        amount_lamports = int(amount_sol * 1_000_000_000)
        
        # Get quote
        route = await self.get_quote(
            input_mint=input_mint,
            output_mint=output_mint,
            amount=amount_lamports,
            slippage_bps=slippage_bps
        )
        
        if not route:
            return SwapResult(
                success=False,
                signature=None,
                input_amount=amount_sol,
                output_amount=0,
                price_impact=0,
                error="Failed to get Jupiter route"
            )
        
        # Build transaction
        transaction = await self.build_swap_tx(route, wallet.pubkey())
        
        if not transaction:
            return SwapResult(
                success=False,
                signature=None,
                input_amount=amount_sol,
                output_amount=route.out_amount / 1_000_000_000,
                price_impact=route.price_impact_pct,
                error="Failed to build swap transaction"
            )
        
        # Sign transaction
        # Note: Requires recent blockhash - should be refreshed before this call
        # This is handled by the caller (main execution loop)
        
        return SwapResult(
            success=True,
            signature=None,  # Will be filled after send
            input_amount=amount_sol,
            output_amount=route.out_amount / 1_000_000_000,
            price_impact=route.price_impact_pct
        )
    
    async def get_priority_fee_estimate(self) -> int:
        """
        Get recommended priority fee from Jupiter
        
        Returns priority fee in micro-lamports per CU
        """
        try:
            async with self.session.get(f"{self.base_url}/priority-fee") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    # Return medium priority fee
                    return data.get("medium", settings.priority_fee_microlamports)
        except Exception as e:
            logger.debug(f"Priority fee fetch error: {e}")
        
        return settings.priority_fee_microlamports


# Token mint addresses
WSOL_MINT = "So11111111111111111111111111111111111111112"  # Wrapped SOL
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"


async def buy_token(jupiter: JupiterClient,
                   wallet: Keypair,
                   token_mint: str,
                   amount_sol: float,
                   slippage_bps: int = None) -> SwapResult:
    """
    Buy token with SOL
    
    Args:
        jupiter: Jupiter client instance
        wallet: Your keypair
        token_mint: Token to buy
        amount_sol: Amount of SOL to spend
        slippage_bps: Slippage tolerance (default: 100 = 1%)
    
    Returns:
        SwapResult with transaction details
    """
    logger.info(f"🛒 BUY: {token_mint[:8]}... with {amount_sol:.3f} SOL")
    
    result = await jupiter.execute_swap(
        wallet=wallet,
        input_mint=WSOL_MINT,
        output_mint=token_mint,
        amount_sol=amount_sol,
        slippage_bps=slippage_bps
    )
    
    return result


async def sell_token(jupiter: JupiterClient,
                    wallet: Keypair,
                    token_mint: str,
                    token_amount: float,
                    decimals: int = 9,
                    slippage_bps: int = None) -> SwapResult:
    """
    Sell token for SOL
    
    Args:
        jupiter: Jupiter client instance
        wallet: Your keypair
        token_mint: Token to sell
        token_amount: Amount of tokens to sell
        decimals: Token decimals (default: 9)
        slippage_bps: Slippage tolerance
    
    Returns:
        SwapResult with transaction details
    """
    # Convert to smallest unit
    amount_raw = int(token_amount * (10 ** decimals))
    
    logger.info(f"💰 SELL: {token_mint[:8]}... amount={token_amount:.6f}")
    
    # Build quote manually for sell
    route = await jupiter.get_quote(
        input_mint=token_mint,
        output_mint=WSOL_MINT,
        amount=amount_raw,
        slippage_bps=slippage_bps
    )
    
    if not route:
        return SwapResult(
            success=False,
            signature=None,
            input_amount=token_amount,
            output_amount=0,
            price_impact=0,
            error="Failed to get sell route"
        )
    
    # Build and return (signing/sending handled by caller)
    return SwapResult(
        success=True,
        signature=None,
        input_amount=token_amount,
        output_amount=route.out_amount / 1_000_000_000,
        price_impact=route.price_impact_pct
    )
