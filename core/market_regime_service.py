"""
Market Regime Service
Simplified service for detecting market regimes and providing adaptive agent weights
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, Optional
import logging
from datetime import datetime, timedelta
from ml.regime_detector import RegimeDetector

logger = logging.getLogger(__name__)


class MarketRegimeService:
    """
    Simplified market regime detection service

    Detects current market regime and returns appropriate agent weights
    Uses SPY as the market benchmark
    """

    def __init__(self, cache_duration_hours: int = 6):
        """
        Initialize market regime service

        Args:
            cache_duration_hours: How long to cache regime detection (default: 6 hours)
        """
        self.regime_detector = RegimeDetector()
        self.cache_duration = timedelta(hours=cache_duration_hours)
        self._cached_regime = None
        self._cached_weights = None
        self._cache_timestamp = None

        logger.info(f"MarketRegimeService initialized (cache: {cache_duration_hours}h)")

    def get_current_regime(self, force_refresh: bool = False) -> Dict:
        """
        Get current market regime

        Args:
            force_refresh: Force refresh even if cache is valid

        Returns:
            {
                'regime': str (e.g., 'BULL_NORMAL_VOL'),
                'trend': str ('BULL', 'BEAR', 'SIDEWAYS'),
                'volatility': str ('HIGH_VOL', 'NORMAL_VOL', 'LOW_VOL'),
                'weights': Dict[str, float] (adaptive agent weights),
                'timestamp': str,
                'cache_hit': bool
            }
        """
        try:
            # Check cache
            if not force_refresh and self._is_cache_valid():
                logger.info("Using cached regime data")
                return {
                    'regime': self._cached_regime,
                    'trend': self._cached_regime.split('_')[0] if self._cached_regime else 'UNKNOWN',
                    'volatility': '_'.join(self._cached_regime.split('_')[1:]) if self._cached_regime else 'UNKNOWN',
                    'weights': self._cached_weights,
                    'timestamp': self._cache_timestamp.isoformat(),
                    'cache_hit': True
                }

            # Fetch SPY data (last 3 months for regime detection)
            logger.info("Fetching SPY data for regime detection...")
            spy = yf.Ticker('SPY')
            hist = spy.history(period='3mo', interval='1d')

            if hist.empty or len(hist) < 30:
                logger.warning("Insufficient SPY data, using default regime")
                return self._get_default_regime()

            # Prepare data for regime detection
            hist['returns'] = hist['Close'].pct_change()
            market_data = pd.DataFrame({
                'price': hist['Close'],
                'returns': hist['returns']
            })

            # Detect regimes
            trend_regime = self.regime_detector.detect_trend_regime(market_data['price'])
            volatility_regime = self.regime_detector.detect_volatility_regime(market_data['returns'])

            # Get most recent regime
            current_trend = trend_regime.iloc[-1] if not trend_regime.empty else 'SIDEWAYS'
            current_volatility = volatility_regime.iloc[-1] if not volatility_regime.empty else 'NORMAL_VOL'

            # Composite regime
            composite_regime = f"{current_trend}_{current_volatility}"

            # Get adaptive weights
            adaptive_weights = self.regime_detector.get_regime_weights(composite_regime)

            # Update cache
            self._cached_regime = composite_regime
            self._cached_weights = adaptive_weights
            self._cache_timestamp = datetime.now()

            logger.info(f"Current market regime: {composite_regime}")
            logger.info(f"Adaptive weights: {adaptive_weights}")

            return {
                'regime': composite_regime,
                'trend': current_trend,
                'volatility': current_volatility,
                'weights': adaptive_weights,
                'timestamp': self._cache_timestamp.isoformat(),
                'cache_hit': False
            }

        except Exception as e:
            logger.error(f"Regime detection failed: {e}")
            return self._get_default_regime()

    def get_adaptive_weights(self, force_refresh: bool = False) -> Dict[str, float]:
        """
        Get adaptive agent weights based on current market regime

        Args:
            force_refresh: Force refresh even if cache is valid

        Returns:
            Dict with agent weights (fundamentals, momentum, quality, sentiment)
        """
        regime_info = self.get_current_regime(force_refresh=force_refresh)
        return regime_info['weights']

    def _is_cache_valid(self) -> bool:
        """Check if cached regime data is still valid"""
        if self._cache_timestamp is None:
            return False

        age = datetime.now() - self._cache_timestamp
        return age < self.cache_duration

    def _get_default_regime(self) -> Dict:
        """
        Return default regime when detection fails

        Returns default regime as SIDEWAYS_NORMAL_VOL with standard weights
        """
        default_weights = {
            'fundamentals': 0.4,
            'momentum': 0.3,
            'quality': 0.2,
            'sentiment': 0.1
        }

        return {
            'regime': 'SIDEWAYS_NORMAL_VOL',
            'trend': 'SIDEWAYS',
            'volatility': 'NORMAL_VOL',
            'weights': default_weights,
            'timestamp': datetime.now().isoformat(),
            'cache_hit': False,
            'error': 'Using default regime due to detection failure'
        }

    def get_regime_explanation(self, regime: Optional[str] = None) -> str:
        """
        Get human-readable explanation of the regime

        Args:
            regime: Regime string (if None, uses cached regime)

        Returns:
            Human-readable explanation
        """
        if regime is None:
            regime = self._cached_regime or 'SIDEWAYS_NORMAL_VOL'

        explanations = {
            'BULL_HIGH_VOL': "📈 Bull market with high volatility - Strong uptrend but choppy. Momentum matters more.",
            'BULL_NORMAL_VOL': "📈 Bull market with normal volatility - Steady uptrend. Balanced approach.",
            'BULL_LOW_VOL': "📈 Bull market with low volatility - Calm uptrend. Fundamentals lead.",

            'BEAR_HIGH_VOL': "📉 Bear market with high volatility - Panic selling. Quality and safety first.",
            'BEAR_NORMAL_VOL': "📉 Bear market with normal volatility - Downtrend. Focus on quality and fundamentals.",
            'BEAR_LOW_VOL': "📉 Bear market with low volatility - Slow decline. Fundamentals critical.",

            'SIDEWAYS_HIGH_VOL': "↔️ Sideways market with high volatility - Range-bound but choppy. Balance quality and momentum.",
            'SIDEWAYS_NORMAL_VOL': "↔️ Sideways market with normal volatility - Neutral trend. Standard balanced approach.",
            'SIDEWAYS_LOW_VOL': "↔️ Sideways market with low volatility - Calm consolidation. Fundamentals matter most.",
        }

        return explanations.get(regime, "Unknown market regime")


# Global singleton instance
_market_regime_service = None


def get_market_regime_service() -> MarketRegimeService:
    """
    Get or create the global MarketRegimeService instance

    Returns:
        MarketRegimeService singleton
    """
    global _market_regime_service

    if _market_regime_service is None:
        _market_regime_service = MarketRegimeService(cache_duration_hours=6)

    return _market_regime_service
