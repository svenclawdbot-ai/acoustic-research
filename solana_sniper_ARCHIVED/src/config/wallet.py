from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
import base58

from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger("wallet")


class WalletManager:
    """
    Hot wallet management for sniper bot
    
    SECURITY WARNINGS:
    - This is a HOT wallet (private key in memory)
    - ONLY use with funds you can afford to lose completely
    - NEVER use your main wallet or hardware wallet
    - Recommended: Create dedicated sniper wallet with limited funds
    
    Barbell Strategy Implementation:
    - Track total balance
    - Enforce 90% cash reserve
    - Only 10% available for sniping positions
    """
    
    def __init__(self):
        self.keypair = self._load_keypair()
        self.pubkey = self.keypair.pubkey()
        self.balance_sol = 0.0
        self.reserved_sol = 0.0
        self.allocated_sol = 0.0
        
        logger.info(f"Wallet loaded: {str(self.pubkey)[:16]}...")
    
    def _load_keypair(self) -> Keypair:
        """Load keypair from environment"""
        try:
            private_key = settings.private_key
            
            # Handle different key formats
            if private_key.startswith('['):
                # JSON array format
                import json
                key_bytes = bytes(json.loads(private_key))
            elif ',' in private_key:
                # Comma-separated bytes
                key_bytes = bytes([int(x) for x in private_key.split(',')])
            else:
                # Base58 format (standard)
                key_bytes = base58.b58decode(private_key)
            
            return Keypair.from_bytes(key_bytes)
            
        except Exception as e:
            logger.error(f"Failed to load keypair: {e}")
            raise RuntimeError("Invalid private key format")
    
    async def update_balance(self, rpc_client: AsyncClient):
        """Fetch current SOL balance"""
        try:
            response = await rpc_client.get_balance(self.pubkey)
            lamports = response.value
            self.balance_sol = lamports / 1_000_000_000
            
            logger.debug(f"Balance updated: {self.balance_sol:.4f} SOL")
            
        except Exception as e:
            logger.error(f"Balance fetch error: {e}")
    
    def get_available_for_trading(self) -> float:
        """
        Calculate available balance for sniping
        
        Implements barbell strategy:
        - 90% cash reserve (never touched)
        - 10% maximum allocation for positions
        """
        max_allocation = self.balance_sol * (settings.sniper_allocation_pct / 100)
        
        # Subtract already allocated positions
        available = max_allocation - self.allocated_sol
        
        # Ensure minimum balance for fees
        fee_reserve = 0.01  # Keep 0.01 SOL for fees
        available = min(available, self.balance_sol - fee_reserve)
        
        return max(0, available)
    
    def allocate_funds(self, amount_sol: float) -> bool:
        """
        Allocate funds for a position
        
        Returns True if allocation successful
        """
        available = self.get_available_for_trading()
        
        if amount_sol > available:
            logger.warning(f"Insufficient funds: need {amount_sol:.3f}, have {available:.3f}")
            return False
        
        if amount_sol > settings.max_position_sol:
            logger.warning(f"Exceeds max position: {amount_sol:.3f} > {settings.max_position_sol:.3f}")
            return False
        
        self.allocated_sol += amount_sol
        logger.info(f"Allocated {amount_sol:.3f} SOL (total allocated: {self.allocated_sol:.3f})")
        
        return True
    
    def release_allocation(self, amount_sol: float):
        """Release allocated funds (on position close)"""
        self.allocated_sol = max(0, self.allocated_sol - amount_sol)
        logger.debug(f"Released {amount_sol:.3f} SOL (remaining allocated: {self.allocated_sol:.3f})")
    
    def get_wallet_summary(self) -> dict:
        """Get wallet status summary"""
        return {
            "pubkey": str(self.pubkey),
            "balance_sol": self.balance_sol,
            "cash_reserve_sol": self.balance_sol * (settings.cash_reserve_pct / 100),
            "max_allocation_sol": self.balance_sol * (settings.sniper_allocation_pct / 100),
            "allocated_sol": self.allocated_sol,
            "available_sol": self.get_available_for_trading(),
            "barbell_compliance": self.allocated_sol <= self.balance_sol * 0.1
        }
    
    def sign_transaction(self, transaction):
        """Sign a transaction with this wallet"""
        # This would integrate with the actual signing
        # For now, just return the keypair for external signing
        return self.keypair


# Convenience functions
def create_new_sniper_wallet() -> tuple:
    """
    Create a new wallet for sniping
    
    Returns:
        (pubkey, private_key_base58)
    
    Usage:
        pubkey, private_key = create_new_sniper_wallet()
        print(f"New wallet: {pubkey}")
        print(f"Private key (save this!): {private_key}")
    """
    keypair = Keypair()
    pubkey = str(keypair.pubkey())
    private_key = base58.b58encode(bytes(keypair)).decode('ascii')
    
    return pubkey, private_key


async def verify_wallet_setup(wallet: WalletManager, rpc_client: AsyncClient):
    """
    Verify wallet is properly configured
    
    Checks:
    - Balance > 0
    - Can fetch balance
    - Keypair is valid
    """
    logger.info("Verifying wallet setup...")
    
    await wallet.update_balance(rpc_client)
    
    if wallet.balance_sol <= 0:
        logger.error("Wallet has zero balance! Please fund the wallet.")
        return False
    
    logger.info(f"✓ Wallet verified: {wallet.balance_sol:.4f} SOL")
    logger.info(f"✓ Max position: {settings.max_position_sol} SOL")
    logger.info(f"✓ Available for sniping: {wallet.get_available_for_trading():.4f} SOL")
    
    return True
