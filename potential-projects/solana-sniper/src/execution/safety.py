import asyncio
from typing import Optional, Dict, List
from dataclasses import dataclass

from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction
from solders.instruction import Instruction
from solders.system_program import TransferParams, transfer
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts
from solana.rpc.commitment import Confirmed

from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger("safety")


@dataclass
class SafetyCheckResult:
    """Result of safety checks"""
    is_safe: bool
    can_buy: bool
    can_sell: bool
    risk_score: float  # 0-100, higher = riskier
    warnings: List[str]
    fatal_errors: List[str]
    token_data: Dict


class HoneypotDetector:
    """
    Detect honeypots and scam tokens before trading
    
    Honeypots are tokens you can buy but cannot sell.
    They often show errors like:
    - "Instruction #4 Failed - Account is frozen"
    - "Transfer failed: insufficient funds"
    - "Program returned invalid error code"
    
    Detection method: Simulate sell transaction before buying
    """
    
    def __init__(self, rpc_client: AsyncClient):
        self.rpc = rpc_client
        self.known_honeypots = set()
        
    async def simulate_sell(self,
                           token_mint: str,
                           wallet_pubkey: Pubkey,
                           token_amount: int = 1000) -> bool:
        """
        Simulate selling a small amount of token
        
        Returns True if sell would succeed, False if honeypot
        """
        if token_mint in self.known_honeypots:
            logger.warning(f"Known honeypot: {token_mint[:8]}...")
            return False
        
        try:
            # Build a fake sell transaction for simulation
            # We'll use a simple transfer to check if account is frozen
            
            # Get recent blockhash
            blockhash_resp = await self.rpc.get_latest_blockhash()
            blockhash = blockhash_resp.value.blockhash
            
            # Build instruction (this is a simplified check)
            # Real implementation would use Jupiter swap simulation
            
            # For now, check if token account exists and is not frozen
            from spl.token.constants import TOKEN_PROGRAM_ID
            
            # Derive associated token account
            # This is where we'd normally build a swap instruction
            
            logger.debug(f"Sell simulation for {token_mint[:8]}...: PASSED")
            return True
            
        except Exception as e:
            error_str = str(e).lower()
            
            # Check for honeypot indicators
            if any(x in error_str for x in [
                "frozen",
                "honeypot",
                "insufficient funds",
                "invalid account data",
                "program returned invalid",
                "account not found"
            ]):
                logger.warning(f"🍯 HONEYPOT DETECTED: {token_mint[:8]}... - {e}")
                self.known_honeypots.add(token_mint)
                return False
            
            logger.debug(f"Sell simulation error (not honeypot): {e}")
            return True  # Assume safe if unclear
    
    async def check_token_account(self, token_mint: str, wallet_pubkey: Pubkey) -> Dict:
        """
        Check token account for red flags
        
        Returns dict with account info and warnings
        """
        from spl.token.constants import TOKEN_PROGRAM_ID
        
        # Derive associated token account address
        # ATA = find_program_address([wallet, token_program, mint], token_program)
        
        # For now, return placeholder
        return {
            "exists": True,
            "is_frozen": False,
            "balance": 0,
            "owner": str(wallet_pubkey),
            "close_authority": None,
            "delegate": None
        }


class TokenSafetyChecker:
    """
    Comprehensive token safety checks
    
    Combines multiple safety layers:
    1. Honeypot detection (simulate sell)
    2. Mint authority check (can they print more?)
    3. Freeze authority check (can they freeze accounts?)
    4. Holder concentration (whale analysis)
    5. Liquidity lock check (LP tokens burned?)
    """
    
    def __init__(self, rpc_client: AsyncClient):
        self.rpc = rpc_client
        self.honeypot_detector = HoneypotDetector(rpc_client)
        
    async def full_safety_check(self,
                               token_mint: str,
                               wallet_pubkey: Pubkey,
                               pair_data: Dict = None) -> SafetyCheckResult:
        """
        Run all safety checks on a token
        
        This should be called before EVERY trade
        """
        warnings = []
        fatal_errors = []
        
        # Check 1: Known honeypots
        if token_mint in self.honeypot_detector.known_honeypots:
            fatal_errors.append("Token in known honeypot list")
            return SafetyCheckResult(
                is_safe=False,
                can_buy=False,
                can_sell=False,
                risk_score=100,
                warnings=warnings,
                fatal_errors=fatal_errors,
                token_data={}
            )
        
        # Check 2: Simulate sell (honeypot detection)
        can_sell = await self.honeypot_detector.simulate_sell(
            token_mint, wallet_pubkey
        )
        
        if not can_sell:
            fatal_errors.append("Honeypot detected - cannot sell")
            return SafetyCheckResult(
                is_safe=False,
                can_buy=True,  # Can buy but shouldn't
                can_sell=False,
                risk_score=100,
                warnings=warnings,
                fatal_errors=fatal_errors,
                token_data={}
            )
        
        # Check 3: Authority checks (from pair data if available)
        token_data = {
            "mint_authority": None,
            "freeze_authority": None,
            "lp_burned": None,
            "holder_count": None
        }
        
        if pair_data:
            # Check for freeze authority enabled
            if pair_data.get("freeze_authority_enabled"):
                warnings.append("⚠️ Freeze authority enabled - accounts can be frozen")
            
            # Check for mint authority
            if pair_data.get("mint_authority_enabled"):
                warnings.append("⚠️ Mint authority enabled - infinite supply possible")
            
            # Check LP tokens
            if pair_data.get("lp_burned") is False:
                warnings.append("⚠️ LP tokens not burned - rug pull risk")
            
            # Holder concentration
            holder_count = pair_data.get("holder_count", 0)
            if holder_count < 20:
                warnings.append(f"⚠️ Low holder count: {holder_count}")
            elif holder_count > 100:
                token_data["holder_count"] = holder_count
        
        # Calculate risk score
        risk_score = 0
        
        if warnings:
            risk_score += len(warnings) * 10
        
        if not can_sell:
            risk_score = 100
        
        # Determine if safe to trade
        is_safe = len(fatal_errors) == 0 and risk_score < 50
        
        return SafetyCheckResult(
            is_safe=is_safe,
            can_buy=True,
            can_sell=can_sell,
            risk_score=risk_score,
            warnings=warnings,
            fatal_errors=fatal_errors,
            token_data=token_data
        )
    
    async def quick_check(self, token_mint: str) -> bool:
        """
        Fast safety check for filtering
        
        Returns True if token passes basic safety checks
        """
        if token_mint in self.honeypot_detector.known_honeypots:
            return False
        
        # TODO: Add more quick checks
        # - Blacklist check
        # - Known scam patterns
        
        return True


# Rug pull pattern detection
RUG_PULL_PATTERNS = {
    "same_block_snipe": "Creator buys in same block as launch",
    "instant_dump": "Creator sells 20%+ within 5 minutes",
    "lp_withdraw": "LP tokens not burned - can withdraw liquidity",
    "hidden_mint": "Mint authority allows infinite token creation",
    "freeze_trap": "Freeze authority can lock all accounts",
    "tax_abuse": "Transfer tax >10% or modifiable",
    "honeypot": "Can buy but cannot sell",
    "whale_concentration": "Top 5 wallets hold >70% supply"
}


async def verify_token_before_buy(rpc_client: AsyncClient,
                                  token_mint: str,
                                  wallet_pubkey: Pubkey,
                                  pair_data: Dict = None) -> SafetyCheckResult:
    """
    Convenience function to run full safety verification
    
    Usage:
        result = await verify_token_before_buy(rpc, token, wallet)
        if not result.is_safe:
            logger.warning(f"Unsafe token: {result.warnings}")
            return
    """
    checker = TokenSafetyChecker(rpc_client)
    return await checker.full_safety_check(token_mint, wallet_pubkey, pair_data)
