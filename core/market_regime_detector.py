"""
Market Regime Detection System
Identifies current market conditions to enable adaptive strategy:
- Trend: BULL, BEAR, SIDEWAYS
- Volatility: HIGH, NORMAL, LOW
- Crisis detection: NORMAL, CRISIS

Uses SPY (S&P 500) as market proxy for regime classification.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class MarketTrend(Enum):
    """Market trend classification"""
    BULL = "BULL"
    BEAR = "BEAR"
    SIDEWAYS = "SIDEWAYS"


class VolatilityRegime(Enum):
    """Volatility level classification"""
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"


class MarketCondition(Enum):
    """Overall market condition"""
    NORMAL = "NORMAL"
    CRISIS = "CRISIS"


@dataclass
class MarketRegime:
    """Complete market regime classification"""
    trend: MarketTrend
    volatility: VolatilityRegime
    condition: MarketCondition

    # Metrics
    returns_20d: float          # 20-day returns
    returns_60d: float          # 60-day returns
    volatility_20d: float       # 20-day annualized volatility
    drawdown: float             # Current drawdown from peak

    # Adaptive parameters
    recommended_stock_count: int      # How many stocks to hold
    recommended_cash_allocation: float  # % to hold in cash
    recommended_rebalance_frequency: str  # 'monthly' or 'quarterly'

    # Description
    description: str


class MarketRegimeDetector:
    """
    Detects market regime using SPY price data

    Classification Logic:
    1. Trend Detection (moving averages + returns):
       - BULL: Price > MA50, MA50 > MA200, 60d returns > 0
       - BEAR: Price < MA50, MA50 < MA200, 60d returns < 0
       - SIDEWAYS: Mixed signals

    2. Volatility Detection (realized volatility):
       - HIGH: 20d vol > 25%
       - NORMAL: 15% < 20d vol < 25%
       - LOW: 20d vol < 15%

    3. Crisis Detection (extreme moves):
       - CRISIS: Drawdown > 15% OR volatility > 30% OR 20d returns < -10%
       - NORMAL: Otherwise
    """

    def __init__(self):
        self.lookback_short = 20   # Short-term window
        self.lookback_medium = 50  # Medium-term window
        self.lookback_long = 200   # Long-term window

        # Thresholds
        self.vol_high_threshold = 0.25
        self.vol_normal_threshold = 0.15
        self.crisis_drawdown_threshold = 0.15
        self.crisis_vol_threshold = 0.30
        self.crisis_returns_threshold = -0.10

        logger.info("📊 MarketRegimeDetector initialized")

    def detect_regime(self, spy_data: pd.DataFrame, current_date: Optional[str] = None) -> MarketRegime:
        """
        Detect market regime from SPY price data

        Args:
            spy_data: DataFrame with SPY price history (columns: Open, High, Low, Close, Volume)
            current_date: Optional date to analyze (uses last date if None)

        Returns:
            MarketRegime object with complete classification
        """
        try:
            # Get point-in-time data
            if current_date:
                data = spy_data[spy_data.index <= current_date].copy()
            else:
                data = spy_data.copy()

            if len(data) < self.lookback_long:
                logger.warning(f"Insufficient data for regime detection (need {self.lookback_long} days)")
                return self._default_regime()

            # Calculate technical indicators
            close = data['Close']

            # Moving averages
            ma20 = close.rolling(self.lookback_short).mean()
            ma50 = close.rolling(self.lookback_medium).mean()
            ma200 = close.rolling(self.lookback_long).mean()

            current_price = float(close.iloc[-1])
            current_ma20 = float(ma20.iloc[-1])
            current_ma50 = float(ma50.iloc[-1])
            current_ma200 = float(ma200.iloc[-1])

            # Returns
            returns_20d = float((close.iloc[-1] / close.iloc[-self.lookback_short] - 1))
            returns_60d = float((close.iloc[-1] / close.iloc[-60] - 1)) if len(close) >= 60 else returns_20d

            # Volatility (annualized)
            returns_series = close.pct_change().dropna()
            volatility_20d = float(returns_series.tail(self.lookback_short).std() * np.sqrt(252))

            # Drawdown
            rolling_max = close.expanding().max()
            drawdown = float((close.iloc[-1] - rolling_max.iloc[-1]) / rolling_max.iloc[-1])

            # === 1. DETECT TREND ===
            trend = self._detect_trend(
                current_price, current_ma50, current_ma200,
                returns_20d, returns_60d
            )

            # === 2. DETECT VOLATILITY ===
            volatility = self._detect_volatility(volatility_20d)

            # === 3. DETECT CRISIS ===
            condition = self._detect_crisis(
                drawdown, volatility_20d, returns_20d
            )

            # === 4. GENERATE ADAPTIVE PARAMETERS ===
            adaptive_params = self._generate_adaptive_parameters(
                trend, volatility, condition
            )

            regime = MarketRegime(
                trend=trend,
                volatility=volatility,
                condition=condition,
                returns_20d=returns_20d,
                returns_60d=returns_60d,
                volatility_20d=volatility_20d,
                drawdown=drawdown,
                recommended_stock_count=adaptive_params['stock_count'],
                recommended_cash_allocation=adaptive_params['cash_allocation'],
                recommended_rebalance_frequency=adaptive_params['rebalance_frequency'],
                description=adaptive_params['description']
            )

            logger.info(f"📊 Market Regime: {regime.trend.value} / {regime.volatility.value} / {regime.condition.value}")
            logger.info(f"   Returns: 20d={returns_20d*100:.1f}%, 60d={returns_60d*100:.1f}%")
            logger.info(f"   Volatility: {volatility_20d*100:.1f}%, Drawdown: {drawdown*100:.1f}%")
            logger.info(f"   → Strategy: {adaptive_params['stock_count']} stocks, {adaptive_params['cash_allocation']*100:.0f}% cash")

            return regime

        except Exception as e:
            logger.error(f"Failed to detect regime: {e}", exc_info=True)
            return self._default_regime()

    def _detect_trend(self, price: float, ma50: float, ma200: float,
                     returns_20d: float, returns_60d: float) -> MarketTrend:
        """Detect market trend"""

        # Bull market indicators
        bull_signals = 0
        if price > ma50:
            bull_signals += 1
        if ma50 > ma200:
            bull_signals += 1
        if returns_60d > 0:
            bull_signals += 1
        if returns_20d > 0.05:  # Strong recent momentum
            bull_signals += 1

        # Bear market indicators
        bear_signals = 0
        if price < ma50:
            bear_signals += 1
        if ma50 < ma200:
            bear_signals += 1
        if returns_60d < 0:
            bear_signals += 1
        if returns_20d < -0.05:  # Strong recent decline
            bear_signals += 1

        # Classification
        if bull_signals >= 3:
            return MarketTrend.BULL
        elif bear_signals >= 3:
            return MarketTrend.BEAR
        else:
            return MarketTrend.SIDEWAYS

    def _detect_volatility(self, volatility_20d: float) -> VolatilityRegime:
        """Detect volatility regime"""

        if volatility_20d > self.vol_high_threshold:
            return VolatilityRegime.HIGH
        elif volatility_20d < self.vol_normal_threshold:
            return VolatilityRegime.LOW
        else:
            return VolatilityRegime.NORMAL

    def _detect_crisis(self, drawdown: float, volatility: float,
                      returns_20d: float) -> MarketCondition:
        """Detect crisis conditions"""

        crisis_signals = 0

        # Large drawdown
        if drawdown < -self.crisis_drawdown_threshold:
            crisis_signals += 1

        # Extreme volatility
        if volatility > self.crisis_vol_threshold:
            crisis_signals += 1

        # Sharp decline
        if returns_20d < self.crisis_returns_threshold:
            crisis_signals += 1

        # Classify
        if crisis_signals >= 2:
            return MarketCondition.CRISIS
        else:
            return MarketCondition.NORMAL

    def _generate_adaptive_parameters(self, trend: MarketTrend,
                                     volatility: VolatilityRegime,
                                     condition: MarketCondition) -> Dict:
        """
        Generate adaptive strategy parameters based on regime

        Strategy Matrix:

        BULL + NORMAL VOL + NORMAL:
            - Aggressive: 20 stocks, 0% cash, quarterly rebalance

        BULL + HIGH VOL + NORMAL:
            - Moderate: 15 stocks, 10% cash, quarterly rebalance

        BEAR + NORMAL VOL + NORMAL:
            - Defensive: 15 stocks, 25% cash, monthly rebalance

        BEAR + HIGH VOL + NORMAL:
            - Conservative: 12 stocks, 40% cash, monthly rebalance

        ANY + ANY + CRISIS:
            - Survival: 10 quality stocks, 50% cash, monthly rebalance
        """

        # Crisis mode overrides everything
        if condition == MarketCondition.CRISIS:
            return {
                'stock_count': 10,
                'cash_allocation': 0.50,
                'rebalance_frequency': 'monthly',
                'description': 'CRISIS MODE: Defensive positioning with 50% cash'
            }

        # Bull market strategies
        if trend == MarketTrend.BULL:
            if volatility == VolatilityRegime.LOW:
                return {
                    'stock_count': 20,
                    'cash_allocation': 0.0,
                    'rebalance_frequency': 'quarterly',
                    'description': 'AGGRESSIVE: Strong bull market with low volatility'
                }
            elif volatility == VolatilityRegime.NORMAL:
                return {
                    'stock_count': 20,
                    'cash_allocation': 0.0,
                    'rebalance_frequency': 'quarterly',
                    'description': 'GROWTH: Bull market with normal volatility'
                }
            else:  # HIGH volatility
                return {
                    'stock_count': 15,
                    'cash_allocation': 0.10,
                    'rebalance_frequency': 'quarterly',
                    'description': 'MODERATE: Bull market but high volatility - slight caution'
                }

        # Bear market strategies
        elif trend == MarketTrend.BEAR:
            if volatility == VolatilityRegime.HIGH:
                return {
                    'stock_count': 12,
                    'cash_allocation': 0.40,
                    'rebalance_frequency': 'monthly',
                    'description': 'CONSERVATIVE: Bear market with high volatility - heavy cash'
                }
            else:  # NORMAL or LOW volatility
                return {
                    'stock_count': 15,
                    'cash_allocation': 0.25,
                    'rebalance_frequency': 'monthly',
                    'description': 'DEFENSIVE: Bear market - reduced exposure'
                }

        # Sideways market strategies
        else:  # SIDEWAYS
            if volatility == VolatilityRegime.HIGH:
                return {
                    'stock_count': 15,
                    'cash_allocation': 0.15,
                    'rebalance_frequency': 'monthly',
                    'description': 'CAUTIOUS: Sideways market with high volatility'
                }
            else:
                return {
                    'stock_count': 18,
                    'cash_allocation': 0.05,
                    'rebalance_frequency': 'quarterly',
                    'description': 'BALANCED: Sideways market - steady approach'
                }

    def _default_regime(self) -> MarketRegime:
        """Return default regime when detection fails"""
        return MarketRegime(
            trend=MarketTrend.SIDEWAYS,
            volatility=VolatilityRegime.NORMAL,
            condition=MarketCondition.NORMAL,
            returns_20d=0.0,
            returns_60d=0.0,
            volatility_20d=0.15,
            drawdown=0.0,
            recommended_stock_count=15,
            recommended_cash_allocation=0.10,
            recommended_rebalance_frequency='quarterly',
            description='DEFAULT: Insufficient data for regime detection'
        )
