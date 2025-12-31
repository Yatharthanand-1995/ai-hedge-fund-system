"""
Momentum Agent
Analyzes price trends and relative strength
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class MomentumAgent:
    """
    Scores stocks based on momentum/trend metrics

    Categories:
    1. Multi-timeframe returns (40%)
    2. Moving average trends (30%)
    3. Relative strength (20%)
    4. Trend quality (10%)
    """

    def __init__(self):
        self.name = "MomentumAgent"
        logger.info(f"{self.name} initialized")

    def analyze(self, symbol: str, data: pd.DataFrame, spy_data: Optional[pd.DataFrame] = None) -> Dict:
        """
        Analyze momentum and return score

        Args:
            symbol: Stock ticker
            data: Price/volume DataFrame with OHLCV
            spy_data: SPY data for relative strength (optional)

        Returns:
            {
                'score': 0-100,
                'confidence': 0-1,
                'metrics': {...},
                'reasoning': str
            }
        """

        try:
            # Flatten MultiIndex if needed
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]

            close = data['Close'].values
            if close.ndim > 1:
                close = close.flatten()

            if len(close) < 252:
                return self._no_signal(symbol, "Insufficient data")

            # Calculate scores
            returns_score = self._score_returns(close)
            ma_score = self._score_moving_averages(close)
            # Enhanced relative strength with fallback
            if spy_data is not None and not spy_data.empty:
                rs_score = self._score_relative_strength(close, spy_data)
            else:
                rs_score = self._get_fallback_relative_strength(close)
                logger.debug(f"Using fallback relative strength for {symbol}: {rs_score}")
            quality_score = self._score_trend_quality(close)

            # Composite score
            composite_score = (
                0.40 * returns_score +
                0.30 * ma_score +
                0.20 * rs_score +
                0.10 * quality_score
            )

            # Confidence (higher for consistent trends)
            confidence = self._calculate_confidence(close)

            # Metrics
            ret_3m = (close[-1] - close[-63]) / close[-63] * 100 if len(close) >= 63 else 0
            ret_6m = (close[-1] - close[-126]) / close[-126] * 100 if len(close) >= 126 else 0
            ret_12m = (close[-1] - close[-252]) / close[-252] * 100 if len(close) >= 252 else 0

            ma50 = np.mean(close[-50:]) if len(close) >= 50 else close[-1]
            ma200 = np.mean(close[-200:]) if len(close) >= 200 else close[-1]

            reasoning = self._build_reasoning(returns_score, ma_score, rs_score, quality_score)

            return {
                'score': round(composite_score, 2),
                'confidence': round(confidence, 2),
                'metrics': {
                    'returns': returns_score,
                    'moving_averages': ma_score,
                    'relative_strength': rs_score,
                    'trend_quality': quality_score,
                    '3m_return': round(ret_3m, 2),
                    '6m_return': round(ret_6m, 2),
                    '12m_return': round(ret_12m, 2),
                    'price_vs_ma50': round((close[-1] / ma50 - 1) * 100, 2),
                    'price_vs_ma200': round((close[-1] / ma200 - 1) * 100, 2),
                },
                'reasoning': reasoning
            }

        except Exception as e:
            logger.error(f"Momentum analysis failed for {symbol}: {e}")
            return self._no_signal(symbol, str(e))

    def _score_returns(self, close: np.ndarray) -> float:
        """Score based on multi-timeframe returns (0-100)"""
        score = 0.0

        # 3-month return
        if len(close) >= 63:
            ret_3m = (close[-1] - close[-63]) / close[-63] * 100
            if ret_3m > 15:
                score += 25
            elif ret_3m > 10:
                score += 20
            elif ret_3m > 5:
                score += 15
            elif ret_3m > 0:
                score += 10

        # 6-month return
        if len(close) >= 126:
            ret_6m = (close[-1] - close[-126]) / close[-126] * 100
            if ret_6m > 20:
                score += 35
            elif ret_6m > 15:
                score += 25
            elif ret_6m > 10:
                score += 20
            elif ret_6m > 0:
                score += 10

        # 12-month return
        if len(close) >= 252:
            ret_12m = (close[-1] - close[-252]) / close[-252] * 100
            if ret_12m > 30:
                score += 40
            elif ret_12m > 20:
                score += 30
            elif ret_12m > 10:
                score += 20
            elif ret_12m > 0:
                score += 10

        return min(score, 100)

    def _score_moving_averages(self, close: np.ndarray) -> float:
        """Score based on price vs moving averages (0-100)"""
        score = 0.0

        # Validate input data
        if len(close) == 0:
            return 0.0

        current_price = close[-1]

        # Check if current price is valid
        if np.isnan(current_price) or current_price <= 0:
            return 0.0

        # MA50
        if len(close) >= 50:
            ma50 = np.mean(close[-50:])
            # Validate MA50 before division
            if not np.isnan(ma50) and ma50 > 0:
                diff_50 = (current_price / ma50 - 1) * 100

                if diff_50 > 10:
                    score += 40
                elif diff_50 > 5:
                    score += 30
                elif diff_50 > 0:
                    score += 20
                elif diff_50 > -5:
                    score += 10

        # MA200
        if len(close) >= 200:
            ma200 = np.mean(close[-200:])
            # Validate MA200 before division
            if not np.isnan(ma200) and ma200 > 0:
                diff_200 = (current_price / ma200 - 1) * 100

                if diff_200 > 15:
                    score += 40
                elif diff_200 > 10:
                    score += 30
                elif diff_200 > 5:
                    score += 20
                elif diff_200 > 0:
                    score += 10

        # Golden cross bonus (MA50 > MA200)
        if len(close) >= 200:
            ma50 = np.mean(close[-50:])
            ma200 = np.mean(close[-200:])
            # Validate both MAs before comparison
            if not np.isnan(ma50) and not np.isnan(ma200) and ma50 > ma200:
                score += 20

        return min(score, 100)

    def _score_relative_strength(self, close: np.ndarray, spy_data: pd.DataFrame) -> float:
        """Score based on relative strength vs SPY (0-100)"""
        try:
            # Flatten SPY data
            if isinstance(spy_data.columns, pd.MultiIndex):
                spy_data.columns = [col[0] if isinstance(col, tuple) else col for col in spy_data.columns]

            spy_close = spy_data['Close'].values
            if spy_close.ndim > 1:
                spy_close = spy_close.flatten()

            # Align lengths
            min_len = min(len(close), len(spy_close))
            close_aligned = close[-min_len:]
            spy_aligned = spy_close[-min_len:]

            # Calculate relative strength (6 months)
            if min_len >= 126:
                stock_ret = (close_aligned[-1] - close_aligned[-126]) / close_aligned[-126]
                spy_ret = (spy_aligned[-1] - spy_aligned[-126]) / spy_aligned[-126]
                rel_strength = (stock_ret - spy_ret) * 100

                if rel_strength > 20:
                    return 100
                elif rel_strength > 10:
                    return 80
                elif rel_strength > 5:
                    return 60
                elif rel_strength > 0:
                    return 50
                elif rel_strength > -5:
                    return 40
                elif rel_strength > -10:
                    return 30
                else:
                    return 20

            return 50

        except Exception as e:
            logger.warning(f"Relative strength calculation failed: {e}")
            return 50

    def _score_trend_quality(self, close: np.ndarray) -> float:
        """Score based on trend consistency (0-100)"""
        score = 0.0

        # Check if trend is consistent (not choppy)
        if len(close) >= 60:
            # Calculate rolling 20-day returns
            returns_20d = []
            for i in range(len(close) - 20, len(close)):
                ret = (close[i] - close[i-20]) / close[i-20]
                returns_20d.append(ret)

            # Count positive periods
            positive_count = sum(1 for r in returns_20d if r > 0)
            positive_ratio = positive_count / len(returns_20d)

            if positive_ratio > 0.8:
                score += 50
            elif positive_ratio > 0.6:
                score += 40
            elif positive_ratio > 0.5:
                score += 30

        # Bonus for steady uptrend (low volatility in returns)
        if len(close) >= 30:
            returns = np.diff(close[-30:]) / close[-30:-1]
            volatility = np.std(returns)

            if volatility < 0.02:
                score += 50
            elif volatility < 0.03:
                score += 30
            elif volatility < 0.04:
                score += 20

        return min(score, 100)

    def _calculate_confidence(self, close: np.ndarray) -> float:
        """Calculate confidence based on data availability and consistency"""

        if len(close) < 63:
            return 0.3
        elif len(close) < 126:
            return 0.5
        elif len(close) < 252:
            return 0.7
        else:
            # Full year of data
            # Check trend consistency
            ret_3m = (close[-1] - close[-63]) / close[-63]
            ret_6m = (close[-1] - close[-126]) / close[-126]
            ret_12m = (close[-1] - close[-252]) / close[-252]

            # If all pointing same direction = high confidence
            if (ret_3m > 0 and ret_6m > 0 and ret_12m > 0):
                return 0.95
            elif (ret_3m < 0 and ret_6m < 0 and ret_12m < 0):
                return 0.95
            else:
                return 0.75

    def _build_reasoning(self, returns: float, ma: float, rs: float, quality: float) -> str:
        """Build human-readable reasoning"""

        reasons = []

        if returns > 70:
            reasons.append("Strong returns across all timeframes")
        elif returns > 50:
            reasons.append("Positive momentum")
        elif returns < 30:
            reasons.append("Weak returns")

        if ma > 70:
            reasons.append("strong uptrend vs MAs")
        elif ma > 50:
            reasons.append("above moving averages")
        elif ma < 30:
            reasons.append("below moving averages")

        if rs > 70:
            reasons.append("outperforming market")
        elif rs < 40:
            reasons.append("underperforming market")

        if quality > 70:
            reasons.append("consistent trend")
        elif quality < 30:
            reasons.append("choppy price action")

        return "; ".join(reasons).capitalize() if reasons else "Mixed momentum signals"

    def _no_signal(self, symbol: str, reason: str) -> Dict:
        """Return neutral signal with improved confidence"""
        return {
            'score': 50.0,
            'confidence': 0.2,  # Minimum confidence instead of 0
            'metrics': {'insufficient_data': True},
            'reasoning': f"Limited analysis: {reason}"
        }

    def _get_fallback_relative_strength(self, close: np.ndarray) -> float:
        """Calculate fallback relative strength when SPY data unavailable"""
        try:
            # Use momentum indicators as proxy for relative strength
            if len(close) >= 126:
                # 6-month momentum
                momentum_6m = (close[-1] - close[-126]) / close[-126] * 100

                # Score based on absolute momentum (proxy for market outperformance)
                if momentum_6m > 25:  # Strong positive momentum
                    return 75
                elif momentum_6m > 15:
                    return 65
                elif momentum_6m > 5:
                    return 55
                elif momentum_6m > -5:
                    return 45
                elif momentum_6m > -15:
                    return 35
                else:
                    return 25

            return 50  # Neutral if insufficient data

        except Exception as e:
            logger.warning(f"Fallback relative strength calculation failed: {e}")
            return 50