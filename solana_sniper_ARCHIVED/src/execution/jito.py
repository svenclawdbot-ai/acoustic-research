import asyncio
import aiohttp
import base64
from typing import Optional, List, Dict
from dataclasses import dataclass

from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction
from solders.signature import Signature
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts

from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger("jito")


@dataclass
class JitoBundleResult:
    """Result of Jito bundle submission"""
    success: bool
    bundle_id: Optional[str]
    signatures: List[str]
    landed_slot: Optional[int]
    error: Optional[str] = None


class JitoClient:
    """
    Jito Block Engine Client
    
    Jito provides:
    - MEV protection (sandwich attack prevention)
    - Bundle submission (guaranteed transaction ordering)
    - Faster landing through direct validator connections
    
    Critical for sniper bots to land transactions before others.
    """
    
    # Jito block engine endpoints
    BLOCK_ENGINES = [
        "https://mainnet.block-engine.jito.wtf",
        "https://amsterdam.mainnet.block-engine.jito.wtf",
        "https://frankfurt.mainnet.block-engine.jito.wtf",
        "https://ny.mainnet.block-engine.jito.wtf",
        "https://tokyo.mainnet.block-engine.jito.wtf",
    ]
    
    def __init__(self, rpc_client: AsyncClient, wallet_pubkey: Pubkey):
        self.rpc = rpc_client
        self.wallet_pubkey = wallet_pubkey
        self.block_engine = self.BLOCK_ENGINES[0]  # Primary
        self.session: Optional[aiohttp.ClientSession] = None
        self.tip_accounts: List[str] = []
        
    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=15, connect=3)
        self.session = aiohttp.ClientSession(timeout=timeout)
        await self._get_tip_accounts()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _get_tip_accounts(self):
        """Fetch Jito tip accounts from block engine"""
        try:
            async with self.session.get(
                f"{self.block_engine}/api/v1/bundles/tip_accounts"
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.tip_accounts = [acc["pubkey"] for acc in data]
                    logger.debug(f"Jito tip accounts: {len(self.tip_accounts)}")
                else:
                    # Fallback tip accounts
                    self.tip_accounts = [
                        "96gYZGLnJYVFmbjzopPSU6QiEV5fGqZNyN9nmNhvrZU5",
                        "HFqU5x63VTqvQss8hp11i4wVV8bD44PvwucfZ2bU7gRe",
                        "Cw8CFyM9FkoMi7K7Crf6HNvqfdrjMahgGo98LJNFpX2x",
                        "ADaUMid9yfUytqMBgopwjb2DTLSoknczSH3oQ7N4Qn8G",
                        "ADuUkR4vqLUMWXxW9gh6D6L8pMSawimyGs12gvnyTEAp"
                    ]
        except Exception as e:
            logger.warning(f"Failed to get Jito tip accounts: {e}")
            # Use fallback
            self.tip_accounts = [
                "96gYZGLnJYVFmbjzopPSU6QiEV5fGqZNyN9nmNhvrZU5"
            ]
    
    def create_tip_transaction(self, 
                              tip_amount_lamports: int = None) -> Dict:
        """
        Create a tip transfer instruction for Jito
        
        This is a separate transaction that pays the Jito validator
        for including your bundle.
        """
        if tip_amount_lamports is None:
            tip_amount_lamports = settings.jito_tip_lamports
        
        if not self.tip_accounts:
            raise RuntimeError("No Jito tip accounts available")
        
        tip_account = self.tip_accounts[0]
        
        return {
            "type": "transfer",
            "amount": tip_amount_lamports,
            "to": tip_account,
            "from": str(self.wallet_pubkey)
        }
    
    async def submit_bundle(self,
                           transactions: List[VersionedTransaction],
                           use_jito_tip: bool = True,
                           tip_amount: int = None) -> JitoBundleResult:
        """
        Submit transaction bundle to Jito block engine
        
        Bundle ensures atomic inclusion - all txs land or none do.
        This prevents partial execution (e.g., buy lands but sell doesn't).
        
        Args:
            transactions: List of signed transactions to bundle
            use_jito_tip: Whether to include tip transaction
            tip_amount: Tip amount in lamports
        
        Returns:
            JitoBundleResult with bundle ID and status
        """
        if not settings.use_jito:
            logger.warning("Jito disabled, using regular RPC send")
            return await self._fallback_send(transactions)
        
        if tip_amount is None:
            tip_amount = settings.jito_tip_lamports
        
        # Serialize transactions
        encoded_txs = []
        signatures = []
        
        for tx in transactions:
            # Serialize with signatures
            serialized = base64.b64encode(bytes(tx)).decode('utf-8')
            encoded_txs.append(serialized)
            signatures.append(str(tx.signatures[0]))
        
        # Build bundle payload
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "sendBundle",
            "params": [
                encoded_txs,
                {
                    "tipAccount": self.tip_accounts[0] if self.tip_accounts else None,
                    "tipLamports": tip_amount if use_jito_tip else 0
                }
            ]
        }
        
        try:
            async with self.session.post(
                f"{self.block_engine}/api/v1/bundles",
                json=payload
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    bundle_id = data.get("result")
                    
                    logger.info(f"🎯 Jito bundle submitted: {bundle_id[:16]}...")
                    
                    return JitoBundleResult(
                        success=True,
                        bundle_id=bundle_id,
                        signatures=signatures,
                        landed_slot=None  # Would need to poll for this
                    )
                else:
                    error_text = await resp.text()
                    logger.error(f"Jito bundle error: {resp.status} - {error_text}")
                    
                    # Fallback to regular send
                    return await self._fallback_send(transactions)
                    
        except asyncio.TimeoutError:
            logger.error("Jito bundle submission timeout")
            return await self._fallback_send(transactions)
        except Exception as e:
            logger.error(f"Jito bundle error: {e}")
            return await self._fallback_send(transactions)
    
    async def _fallback_send(self, transactions: List[VersionedTransaction]) -> JitoBundleResult:
        """Fallback to regular RPC send if Jito fails"""
        signatures = []
        
        try:
            for tx in transactions:
                result = await self.rpc.send_transaction(
                    tx,
                    opts=TxOpts(
                        skip_preflight=False,
                        preflight_commitment="confirmed"
                    )
                )
                sig = result.value
                signatures.append(str(sig))
                logger.debug(f"Sent via RPC: {str(sig)[:16]}...")
            
            return JitoBundleResult(
                success=True,
                bundle_id=None,
                signatures=signatures,
                landed_slot=None
            )
        except Exception as e:
            logger.error(f"Fallback send failed: {e}")
            return JitoBundleResult(
                success=False,
                bundle_id=None,
                signatures=[],
                error=str(e)
            )
    
    async def get_bundle_status(self, bundle_id: str) -> Optional[Dict]:
        """
        Check status of submitted bundle
        
        Returns bundle landing status and slot number
        """
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBundleStatuses",
            "params": [[bundle_id]]
        }
        
        try:
            async with self.session.post(
                f"{self.block_engine}/api/v1/bundles",
                json=payload
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("result", {}).get("value", [{}])[0]
        except Exception as e:
            logger.debug(f"Bundle status check error: {e}")
        
        return None
    
    async def get_inflight_bundle_statuses(self) -> List[Dict]:
        """Get all inflight bundles for this validator"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getInflightBundleStatuses",
            "params": [[]]
        }
        
        try:
            async with self.session.post(
                f"{self.block_engine}/api/v1/bundles",
                json=payload
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("result", {}).get("value", [])
        except Exception as e:
            logger.debug(f"Inflight status error: {e}")
        
        return []
    
    async def simulate_bundle(self, transactions: List[VersionedTransaction]) -> Optional[Dict]:
        """
        Simulate bundle execution before submission
        
        Returns simulation result with compute units consumed
        """
        encoded_txs = [
            base64.b64encode(bytes(tx)).decode('utf-8')
            for tx in transactions
        ]
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "simulateBundle",
            "params": [encoded_txs]
        }
        
        try:
            async with self.session.post(
                f"{self.block_engine}/api/v1/bundles",
                json=payload
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
        except Exception as e:
            logger.debug(f"Bundle simulation error: {e}")
        
        return None


class TransactionBuilder:
    """
    Helper class to build optimized transactions for sniping
    """
    
    def __init__(self, rpc_client: AsyncClient):
        self.rpc = rpc_client
        self.recent_blockhash = None
        self.last_blockhash_update = 0
        
    async def get_fresh_blockhash(self, max_age_seconds: int = 30) -> str:
        """
        Get recent blockhash for transaction
        
        Blockhash must be recent (max 90-120 slots old)
        Refresh every 30 seconds for sniper timing
        """
        import time
        current_time = time.time()
        
        if (self.recent_blockhash is None or 
            current_time - self.last_blockhash_update > max_age_seconds):
            
            result = await self.rpc.get_latest_blockhash()
            self.recent_blockhash = result.value.blockhash
            self.last_blockhash_update = current_time
            
            logger.debug(f"Refreshed blockhash: {self.recent_blockhash}")
        
        return self.recent_blockhash
    
    async def build_optimized_transaction(self,
                                         instructions: List,
                                         payer: Pubkey,
                                         priority_fee: int = None,
                                         compute_unit_limit: int = None) -> Optional[VersionedTransaction]:
        """
        Build transaction with optimal compute and fees
        
        Args:
            instructions: List of transaction instructions
            payer: Fee payer public key
            priority_fee: Priority fee in micro-lamports
            compute_unit_limit: Max compute units
        """
        # Get fresh blockhash
        blockhash = await self.get_fresh_blockhash()
        
        # Add priority fee instruction
        if priority_fee is None:
            priority_fee = settings.priority_fee_microlamports
        
        # Add compute budget instructions
        # These go at the start of the transaction
        from solders.system_program import set_compute_unit_limit, set_compute_unit_price
        
        if compute_unit_limit:
            cu_limit_ix = set_compute_unit_limit(compute_unit_limit)
            instructions.insert(0, cu_limit_ix)
        
        cu_price_ix = set_compute_unit_price(priority_fee)
        instructions.insert(0, cu_price_ix)
        
        # Build message
        from solders.message import MessageV0
        
        message = MessageV0.try_compile(
            payer,
            instructions,
            [],  # Address lookup tables
            blockhash
        )
        
        # Return unsigned transaction (signing done by caller)
        return VersionedTransaction(message, [])


# Convenience function for sniper execution
async def execute_sniper_bundle(jito: JitoClient,
                                jupiter: JupiterClient,
                                wallet: Keypair,
                                token_mint: str,
                                amount_sol: float,
                                slippage_bps: int = None) -> JitoBundleResult:
    """
    Execute full sniper buy with Jito MEV protection
    
    This is the main entry point for sniping new tokens
    """
    from execution.jupiter import buy_token, WSOL_MINT
    
    # Build swap transaction
    result = await buy_token(
        jupiter=jupiter,
        wallet=wallet,
        token_mint=token_mint,
        amount_sol=amount_sol,
        slippage_bps=slippage_bps
    )
    
    if not result.success:
        return JitoBundleResult(
            success=False,
            bundle_id=None,
            signatures=[],
            error=result.error
        )
    
    # TODO: Sign transaction with wallet
    # TODO: Submit via Jito bundle
    # For now, return the result structure
    
    logger.info(f"🚀 Sniper bundle ready for {token_mint[:8]}...")
    
    return JitoBundleResult(
        success=True,
        bundle_id=None,
        signatures=[],
        landed_slot=None
    )
