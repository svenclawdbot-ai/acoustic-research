from typing import List, Optional
from dataclasses import dataclass
import numpy as np

from config.settings import settings
from signal.dex_screener import TokenPair
from utils.logger import setup_logger

logger = setup_logger("filters")


@dataclass
class FilterResult:
    """Result of token filtering"""
    passed: bool
    score: float  # 0-1 confidence score
    reasons: List[str]
    risk_flags: List[str]


class TokenFilters:
    """Multi-layer token filtering using Taleb/Antifragility principles"""
    
    def __init__(self):
        self.blacklisted = set(settings.blacklisted_tokens)
    
    def evaluate(self, pair: TokenPair) -> FilterResult:
        """
        Run all filters and return composite score
        Returns FilterResult with confidence score (0-1)
        """
        reasons = []
        risk_flags = []
        
        # Layer 1: Basic eligibility (binary pass/fail)
        if not self._basic_eligibility(pair):
            return FilterResult(
                passed=False,
                score=0.0,
                reasons=["Failed basic eligibility"],
                risk_flags=["BASIC_FAIL"]
            )
        
        # Layer 2: Liquidity filters
        liq_score, liq_reasons = self._liquidity_check(pair)
        reasons.extend(liq_reasons)
        
        # Layer 3: Volume/momentum signals
        vol_score, vol_reasons, vol_flags = self._volume_analysis(pair)
        reasons.extend(vol_reasons)
        risk_flags.extend(vol_flags)
        
        # Layer 4: Age/timing (convexity = get in early)
        age_score, age_reasons = self._age_analysis(pair)
        reasons.extend(age_reasons)
        
        # Layer 5: Black swan detection (anomaly check)
        anomaly_score, anomaly_flags = self._anomaly_detection(pair)
        risk_flags.extend(anomaly_flags)
        
        # Composite score (weighted)
        composite = (
            liq_score * 0.25 +
            vol_score * 0.35 +
            age_score * 0.25 +
            anomaly_score * 0.15
        )
        
        # Apply risk penalties
        if len(risk_flags) > 2:
            composite *= 0.5
        elif len(risk_flags) > 0:
            composite *= 0.8
        
        passed = composite >= settings.confidence_threshold
        
        if passed:
            logger.info(f"✓ {pair.base_token[:8]}... score={composite:.2f} flags={risk_flags}")
        
        return FilterResult(
            passed=passed,
            score=composite,
            reasons=reasons,
            risk_flags=risk_flags
        )
    
    def _basic_eligibility(self, pair: TokenPair) -> bool:
        """Binary eligibility check"""
        # Not blacklisted
        if pair.base_token in self.blacklisted:
            return False
        
        # Minimum liquidity
        if pair.liquidity_usd < settings.min_liquidity_usd:
            return False
        
        # Has price data
        if pair.price_usd <= 0:
            return False
        
        # Not too old (we want fresh launches for convexity)
        if pair.age_seconds and pair.age_seconds > settings.max_entry_delay_seconds:
            return False
        
        return True
    
    def _liquidity_check(self, pair: TokenPair) -> tuple:
        """
        Analyze liquidity depth
        Returns: (score 0-1, reasons)
        """
        score = 0.0
        reasons = []
        
        liquidity = pair.liquidity_usd
        
        if liquidity > 50000:
            score = 1.0
            reasons.append(f"Deep liquidity: ${liquidity:,.0f}")
        elif liquidity > 10000:
            score = 0.8
            reasons.append(f"Good liquidity: ${liquidity:,.0f}")
        elif liquidity > 5000:
            score = 0.6
            reasons.append(f"Moderate liquidity: ${liquidity:,.0f}")
        elif liquidity > 1000:
            score = 0.4
            reasons.append(f"Low liquidity: ${liquidity:,.0f}")
        else:
            score = 0.2
            reasons.append(f"Thin liquidity: ${liquidity:,.0f}")
        
        return score, reasons
    
    def _volume_analysis(self, pair: TokenPair) -> tuple:
        """
        Analyze volume patterns for momentum signals
        Returns: (score 0-1, reasons, risk_flags)
        """
        score = 0.0
        reasons = []
        flags = []
        
        vol_5m = pair.volume_5m
        vol_1h = pair.volume_1h
        
        # 5-minute volume check
        if vol_5m > settings.min_volume_5m * 5:
            score += 0.4
            reasons.append(f"High 5m volume: ${vol_5m:,.0f}")
        elif vol_5m > settings.min_volume_5m:
            score += 0.25
            reasons.append(f"Good 5m volume: ${vol_5m:,.0f}")
        
        # Transaction count (organic vs bot)
        if pair.tx_count_5m > 50:
            score += 0.3
            reasons.append(f"High tx count: {pair.tx_count_5m}")
        elif pair.tx_count_5m > 20:
            score += 0.15
        elif pair.tx_count_5m < 5:
            flags.append("LOW_TX_COUNT")
        
        # Price momentum (early pump detection)
        if pair.price_change_5m > 10:
            score += 0.2
            reasons.append(f"Momentum: +{pair.price_change_5m:.1f}% (5m)")
        elif pair.price_change_5m > 50:
            # Already pumped hard - might be late
            flags.append("ALREADY_PUMPED")
            score -= 0.1
        elif pair.price_change_5m < -20:
            flags.append("DUMPING")
            score -= 0.2
        
        # Volume acceleration (5m vs 1h ratio)
        if vol_1h > 0:
            vol_ratio = (vol_5m * 12) / vol_1h  # Annualized comparison
            if vol_ratio > 2.0:
                score += 0.1
                reasons.append("Volume accelerating")
        
        return min(score, 1.0), reasons, flags
    
    def _age_analysis(self, pair: TokenPair) -> tuple:
        """
        Age = convexity opportunity
        Earlier = cheaper option premium
        Returns: (score 0-1, reasons)
        """
        score = 0.0
        reasons = []
        
        age = pair.age_seconds
        
        if age is None:
            return 0.5, ["Unknown age"]
        
        if age < 60:
            score = 1.0
            reasons.append(f"⚡ Ultra-fresh: {age:.0f}s old")
        elif age < 180:
            score = 0.9
            reasons.append(f"🚀 Very fresh: {age:.0f}s old")
        elif age < 300:
            score = 0.75
            reasons.append(f"Fresh: {age:.0f}s old")
        elif age < 600:
            score = 0.5
            reasons.append(f"Getting old: {age:.0f}s")
        else:
            score = 0.3
            reasons.append(f"Late entry: {age:.0f}s")
        
        return score, reasons
    
    def _anomaly_detection(self, pair: TokenPair) -> tuple:
        """
        Detect anomalies that might indicate:
        - Honey pots
        - Rug pulls
        - Bot manipulation
        Returns: (score 0-1, risk_flags)
        """
        score = 1.0
        flags = []
        
        # Check for extreme price action (potential honey pot)
        if abs(pair.price_change_5m) > 200:
            flags.append("EXTREME_VOLATILITY")
            score -= 0.3
        
        # Unusual volume pattern (bot wash trading)
        if pair.volume_5m > 0 and pair.tx_count_5m > 0:
            avg_tx_size = pair.volume_5m / pair.tx_count_5m
            if avg_tx_size > 10000:  # $10k+ average tx
                flags.append("LARGE_TX_PATTERN")
            elif avg_tx_size < 10:  # Very small txs
                flags.append("WASH_TRADING_SUSPECTED")
        
        # Low liquidity but high volume (dangerous)
        if pair.liquidity_usd > 0:
            vol_liq_ratio = pair.volume_5m / pair.liquidity_usd
            if vol_liq_ratio > 5:  # 5x turnover in 5 min
                flags.append("HIGH_TURNOVER")
        
        return max(score, 0.0), flags
