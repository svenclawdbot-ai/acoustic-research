import asyncio
from typing import Optional, Tuple
from dataclasses import dataclass
import numpy as np
from scipy import stats

from config.settings import settings
from signal.dex_screener import TokenPair
from utils.logger import setup_logger

logger = setup_logger("bayesian")


@dataclass
class InferenceResult:
    """Bayesian inference result for token opportunity"""
    confidence: float  # 0-1
    surprise_score: float  # KL divergence
    expected_return: float  # Estimated ROI
    risk_adjusted_score: float  # Sharpe-like metric
    recommendation: str  # BUY, HOLD, PASS


class BayesianInference:
    """
    Active Inference / Free Energy Principle applied to trading
    
    Key concepts:
    - Minimize surprise: Update beliefs based on price action vs expectation
    - Epistemic value: Information gathering (volume, holder count) reduces uncertainty
    - Precision weighting: Confidence in signals determines position size
    """
    
    def __init__(self):
        # Prior beliefs (from research: 98.6% fail)
        self.prior_success_rate = 0.014  # 1.4% base success
        self.price_volatility_prior = 0.5  # Expected volatility
        
    def infer(self, pair: TokenPair, filter_score: float) -> InferenceResult:
        """
        Run Bayesian inference on token opportunity
        
        Returns confidence score, surprise metric, and recommendation
        """
        # Calculate likelihood components
        price_likelihood = self._price_likelihood(pair)
        volume_likelihood = self._volume_likelihood(pair)
        age_likelihood = self._age_likelihood(pair)
        
        # Combined likelihood (independent factors)
        likelihood = price_likelihood * volume_likelihood * age_likelihood
        
        # Bayesian update: posterior ∝ likelihood × prior
        posterior_odds = (likelihood * self.prior_success_rate) / (1 - self.prior_success_rate)
        posterior_prob = posterior_odds / (1 + posterior_odds)
        
        # Calculate surprise (KL divergence from prior)
        surprise = self._calculate_surprise(posterior_prob)
        
        # Expected return estimation (convex payoff)
        expected_return = self._estimate_return(pair, posterior_prob)
        
        # Risk-adjusted score (precision-weighted)
        risk_adj_score = self._risk_adjusted_score(
            posterior_prob, expected_return, pair, filter_score
        )
        
        # Recommendation
        if risk_adj_score >= 0.75 and surprise <= settings.surprise_threshold:
            recommendation = "BUY"
        elif risk_adj_score >= 0.5:
            recommendation = "HOLD"
        else:
            recommendation = "PASS"
        
        logger.info(f"Inference: {pair.base_token[:8]}... "
                   f"conf={posterior_prob:.2f} surprise={surprise:.2f} "
                   f"rec={recommendation}")
        
        return InferenceResult(
            confidence=posterior_prob,
            surprise_score=surprise,
            expected_return=expected_return,
            risk_adjusted_score=risk_adj_score,
            recommendation=recommendation
        )
    
    def _price_likelihood(self, pair: TokenPair) -> float:
        """
        Likelihood based on price action
        Early momentum = higher likelihood of success
        """
        change_5m = pair.price_change_5m
        
        # Favorable: moderate positive momentum (10-50%)
        # Too high (>100%) = likely already pumped or manipulation
        if 10 <= change_5m <= 50:
            return 0.8
        elif 5 <= change_5m < 10:
            return 0.6
        elif 50 <= change_5m <= 100:
            return 0.5
        elif change_5m > 100:
            return 0.3  # Already pumped
        elif change_5m < 0:
            return 0.2  # Negative momentum
        else:
            return 0.4
    
    def _volume_likelihood(self, pair: TokenPair) -> float:
        """
        Likelihood based on volume patterns
        High volume + organic distribution = good
        """
        vol_5m = pair.volume_5m
        tx_count = pair.tx_count_5m
        
        if vol_5m == 0 or tx_count == 0:
            return 0.1
        
        # Average transaction size
        avg_tx = vol_5m / tx_count
        
        # Ideal: high volume, distributed transactions
        if vol_5m > 50000 and 10 < avg_tx < 5000:
            return 0.9  # High volume, organic distribution
        elif vol_5m > 20000 and avg_tx < 10000:
            return 0.7
        elif vol_5m > 5000:
            return 0.5
        else:
            return 0.3
    
    def _age_likelihood(self, pair: TokenPair) -> float:
        """
        Likelihood based on token age
        Earlier = more convexity, but less information
        """
        age = pair.age_seconds
        
        if age is None:
            return 0.5
        
        # Optimal: very fresh but not first second (avoid honey pots)
        if 5 <= age <= 60:
            return 1.0  # Sweet spot
        elif age < 5:
            return 0.7  # Too fresh, limited info
        elif 60 < age <= 180:
            return 0.8
        elif 180 < age <= 300:
            return 0.6
        else:
            return 0.4  # Getting stale
    
    def _calculate_surprise(self, posterior: float) -> float:
        """
        Calculate surprise (KL divergence) from prior
        Lower surprise = more expected outcome = higher confidence
        """
        prior = self.prior_success_rate
        
        # KL divergence: D_KL(Posterior || Prior)
        # Approximate for binary case
        if posterior == 0 or posterior == 1:
            return 0.0
        
        kl = posterior * np.log(posterior / prior) + \
             (1 - posterior) * np.log((1 - posterior) / (1 - prior))
        
        return float(kl)
    
    def _estimate_return(self, pair: TokenPair, prob: float) -> float:
        """
        Estimate expected return based on success probability
        Uses research data: successful tokens avg 3-10x
        """
        if prob < 0.3:
            return -0.5  # Likely loss
        elif prob < 0.5:
            return 1.0  # 2x expected
        elif prob < 0.7:
            return 3.0  # 4x expected
        else:
            return 5.0  # 6x expected
    
    def _risk_adjusted_score(self, prob: float, expected_return: float, 
                             pair: TokenPair, filter_score: float) -> float:
        """
        Calculate precision-weighted risk-adjusted score
        Combines inference confidence with filter signals
        """
        # Sharpe-like ratio: E[R] / volatility
        # Estimate volatility from price change
        volatility = max(abs(pair.price_change_5m) / 100, 0.1)
        sharpe_like = expected_return / volatility
        
        # Combine with filter score and probability
        combined = (
            prob * 0.3 +
            filter_score * 0.3 +
            min(sharpe_like / 10, 1.0) * 0.4  # Normalize to 0-1
        )
        
        return min(combined, 1.0)
