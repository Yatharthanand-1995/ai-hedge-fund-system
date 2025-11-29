"""
Institutional Flow Agent
Detects institutional buying/selling patterns through volume analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class InstitutionalFlowAgent:
    """
    Scores stocks based on institutional flow (smart money) indicators

    Categories:
    1. Volume Flow Trends (40%) - OBV & AD trend analysis
    2. Money Flow Strength (30%) - MFI & CMF analysis
    3. Unusual Activity Detection (20%) - Volume spike detection
    4. VWAP Analysis (10%) - Price vs institutional benchmark
    """

    def __init__(self):
        self.name = "InstitutionalFlowAgent"
        logger.info(f"{self.name} initialized")

    def analyze(self, symbol: str, data: pd.DataFrame, cached_data: Optional[Dict] = None) -> Dict:
        """
        Analyze institutional flow and return score

        Args:
            symbol: Stock ticker
            data: Price/volume DataFrame with OHLCV
            cached_data: Pre-calculated indicators from EnhancedYahooProvider

        Returns:
            {
                'score': 0-100,
                'confidence': 0-1,
                'metrics': {...},
                'reasoning': str
            }
        """

        try:
            # Use cached data if available
            if cached_data and 'technical_data' in cached_data:
                tech_data = cached_data['technical_data']
                obv = tech_data.get('obv')
                ad = tech_data.get('ad')
                mfi = tech_data.get('mfi')
                cmf = tech_data.get('cmf')
                vwap = tech_data.get('vwap')
                volume_zscore = tech_data.get('volume_zscore')
            else:
                # Fallback: calculate from data
                return self._no_signal(symbol, "No cached technical data available")

            # Flatten MultiIndex if needed
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]

            close = data['Close'].values
            if close.ndim > 1:
                close = close.flatten()

            volume = data['Volume'].values
            if volume.ndim > 1:
                volume = volume.flatten()

            # Need minimum data for meaningful analysis
            if len(close) < 60:
                return self._no_signal(symbol, "Insufficient data for institutional flow analysis")

            # Calculate component scores
            flow_score = self._score_volume_flow(obv, ad)
            money_flow_score = self._score_money_flow(mfi, cmf)
            unusual_activity_score = self._score_unusual_activity(volume_zscore, volume)
            vwap_score = self._score_vwap(close, vwap)

            # Composite score (weighted)
            composite_score = (
                0.40 * flow_score +
                0.30 * money_flow_score +
                0.20 * unusual_activity_score +
                0.10 * vwap_score
            )

            # Confidence (based on data quality and signal strength)
            confidence = self._calculate_confidence(obv, ad, mfi, volume)

            # Build reasoning
            reasoning = self._build_reasoning(
                flow_score, money_flow_score,
                unusual_activity_score, vwap_score
            )

            # Gather metrics
            current_obv = float(obv[-1]) if obv is not None and len(obv) > 0 else 0
            current_ad = float(ad[-1]) if ad is not None and len(ad) > 0 else 0
            current_mfi = float(mfi[-1]) if mfi is not None and len(mfi) > 0 else 50
            current_cmf = float(cmf[-1]) if cmf is not None and len(cmf) > 0 else 0
            current_zscore = float(volume_zscore[-1]) if volume_zscore is not None and len(volume_zscore) > 0 else 0

            return {
                'score': round(composite_score, 2),
                'confidence': round(confidence, 2),
                'metrics': {
                    'volume_flow': flow_score,
                    'money_flow': money_flow_score,
                    'unusual_activity': unusual_activity_score,
                    'vwap_position': vwap_score,
                    'obv_value': round(current_obv, 0),
                    'ad_value': round(current_ad, 0),
                    'mfi': round(current_mfi, 2),
                    'cmf': round(current_cmf, 4),
                    'volume_zscore': round(current_zscore, 2),
                },
                'reasoning': reasoning
            }

        except Exception as e:
            logger.error(f"Institutional flow analysis failed for {symbol}: {e}")
            return self._no_signal(symbol, str(e))

    def _score_volume_flow(self, obv: Optional[np.ndarray], ad: Optional[np.ndarray]) -> float:
        """
        Score based on OBV and AD trends (0-100)
        Positive trends indicate institutional accumulation
        """
        score = 0.0

        try:
            # OBV trend analysis (50 points)
            if obv is not None and len(obv) >= 60:
                obv_trend = self._calculate_trend(obv)

                if obv_trend > 0.10:  # Strong uptrend
                    score += 50
                elif obv_trend > 0.05:  # Moderate uptrend
                    score += 35
                elif obv_trend > 0:  # Slight uptrend
                    score += 20
                elif obv_trend > -0.05:  # Slight downtrend
                    score += 10
                # Strong downtrend = 0 points

            # AD trend analysis (50 points)
            if ad is not None and len(ad) >= 60:
                ad_trend = self._calculate_trend(ad)

                if ad_trend > 0.10:  # Strong accumulation
                    score += 50
                elif ad_trend > 0.05:  # Moderate accumulation
                    score += 35
                elif ad_trend > 0:  # Slight accumulation
                    score += 20
                elif ad_trend > -0.05:  # Slight distribution
                    score += 10
                # Strong distribution = 0 points

            return min(score, 100)

        except Exception as e:
            logger.warning(f"Volume flow scoring failed: {e}")
            return 50

    def _score_money_flow(self, mfi: Optional[np.ndarray], cmf: Optional[np.ndarray]) -> float:
        """
        Score based on Money Flow Index and Chaikin Money Flow (0-100)
        Identifies buying/selling pressure
        """
        score = 0.0

        try:
            # MFI analysis (50 points)
            if mfi is not None and len(mfi) > 0:
                current_mfi = float(mfi[-1])

                if 40 <= current_mfi <= 60:  # Neutral, healthy
                    score += 30
                elif 30 <= current_mfi < 40:  # Oversold territory
                    score += 40
                elif 20 <= current_mfi < 30:  # Very oversold (buying opportunity)
                    score += 50
                elif 60 < current_mfi <= 70:  # Overbought but strong
                    score += 35
                elif 70 < current_mfi <= 80:  # Overbought
                    score += 20
                else:  # Extreme levels
                    score += 10

            # CMF analysis (50 points)
            if cmf is not None and len(cmf) > 0:
                current_cmf = float(cmf[-1])

                if current_cmf > 0.15:  # Strong buying pressure
                    score += 50
                elif current_cmf > 0.05:  # Moderate buying pressure
                    score += 40
                elif current_cmf > 0:  # Slight buying pressure
                    score += 30
                elif current_cmf > -0.05:  # Slight selling pressure
                    score += 20
                elif current_cmf > -0.15:  # Moderate selling pressure
                    score += 10
                # Strong selling pressure = 0 points

            return min(score, 100)

        except Exception as e:
            logger.warning(f"Money flow scoring failed: {e}")
            return 50

    def _score_unusual_activity(self, volume_zscore: Optional[np.ndarray], volume: np.ndarray) -> float:
        """
        Score based on unusual volume spikes (0-100)
        High Z-scores indicate institutional activity
        """
        score = 0.0

        try:
            # Recent volume Z-score (70 points)
            if volume_zscore is not None and len(volume_zscore) > 0:
                current_zscore = float(volume_zscore[-1])

                if current_zscore > 3.0:  # Extreme spike
                    score += 70
                elif current_zscore > 2.0:  # Strong spike
                    score += 60
                elif current_zscore > 1.5:  # Moderate spike
                    score += 50
                elif current_zscore > 1.0:  # Slight spike
                    score += 40
                elif current_zscore > 0.5:  # Above average
                    score += 30
                else:  # Normal or below
                    score += 20

            # Volume trend (30 points)
            if len(volume) >= 20:
                volume_trend = self._calculate_trend(volume)

                if volume_trend > 0.20:  # Strong increasing volume
                    score += 30
                elif volume_trend > 0.10:  # Moderate increasing volume
                    score += 20
                elif volume_trend > 0:  # Slight increasing volume
                    score += 10
                # Decreasing volume = 0 points

            return min(score, 100)

        except Exception as e:
            logger.warning(f"Unusual activity scoring failed: {e}")
            return 50

    def _score_vwap(self, close: np.ndarray, vwap: Optional[np.ndarray]) -> float:
        """
        Score based on price position vs VWAP (0-100)
        Price above VWAP suggests institutional buying
        """
        try:
            if vwap is None or len(vwap) == 0:
                return 50  # Neutral if no VWAP data

            current_price = float(close[-1])
            current_vwap = float(vwap[-1])

            # Calculate percentage difference
            vwap_diff = (current_price / current_vwap - 1) * 100

            if vwap_diff > 5:  # Well above VWAP (strong institutional support)
                return 100
            elif vwap_diff > 2:  # Above VWAP
                return 80
            elif vwap_diff > 0:  # Slightly above VWAP
                return 60
            elif vwap_diff > -2:  # Slightly below VWAP
                return 40
            elif vwap_diff > -5:  # Below VWAP
                return 20
            else:  # Well below VWAP
                return 0

        except Exception as e:
            logger.warning(f"VWAP scoring failed: {e}")
            return 50

    def _calculate_trend(self, data: np.ndarray) -> float:
        """
        Calculate trend using linear regression slope
        Returns normalized slope (-1 to 1 range)
        """
        try:
            if len(data) < 20:
                return 0.0

            # Use last 60 days for trend
            recent_data = data[-60:]

            # Remove NaN values
            valid_indices = ~np.isnan(recent_data)
            if not np.any(valid_indices):
                return 0.0

            valid_data = recent_data[valid_indices]
            x = np.arange(len(valid_data))

            # Linear regression
            coeffs = np.polyfit(x, valid_data, 1)
            slope = coeffs[0]

            # Normalize by mean to get percentage trend
            mean_val = np.mean(valid_data)
            if mean_val != 0:
                normalized_slope = slope / abs(mean_val)
            else:
                normalized_slope = 0.0

            return normalized_slope

        except Exception as e:
            logger.warning(f"Trend calculation failed: {e}")
            return 0.0

    def _calculate_confidence(self, obv: Optional[np.ndarray], ad: Optional[np.ndarray],
                             mfi: Optional[np.ndarray], volume: np.ndarray) -> float:
        """
        Calculate confidence based on data availability and signal consistency
        """
        confidence = 0.5  # Base confidence

        # Data availability bonus
        available_indicators = 0
        if obv is not None and len(obv) >= 60:
            available_indicators += 1
        if ad is not None and len(ad) >= 60:
            available_indicators += 1
        if mfi is not None and len(mfi) > 0:
            available_indicators += 1

        confidence += available_indicators * 0.1

        # Volume consistency bonus
        if len(volume) >= 60:
            # Check if volume data is consistent (not all zeros or identical)
            volume_std = np.std(volume[-60:])
            volume_mean = np.mean(volume[-60:])

            if volume_mean > 0 and volume_std > 0:
                cv = volume_std / volume_mean  # Coefficient of variation
                if cv > 0.1:  # Healthy variation
                    confidence += 0.2

        return min(confidence, 1.0)

    def _build_reasoning(self, flow: float, money: float, activity: float, vwap: float) -> str:
        """Build human-readable reasoning"""

        reasons = []

        # Volume flow analysis
        if flow > 70:
            reasons.append("strong institutional accumulation detected (OBV/AD uptrend)")
        elif flow > 50:
            reasons.append("moderate buying pressure from volume flows")
        elif flow < 30:
            reasons.append("institutional distribution detected (OBV/AD downtrend)")

        # Money flow analysis
        if money > 70:
            reasons.append("strong money flow indicating smart money buying")
        elif money > 50:
            reasons.append("positive money flow metrics")
        elif money < 30:
            reasons.append("weak money flow suggesting selling pressure")

        # Unusual activity
        if activity > 70:
            reasons.append("unusual volume spike detected (potential institutional activity)")
        elif activity > 50:
            reasons.append("above-average trading volume")
        elif activity < 30:
            reasons.append("below-average volume (limited institutional interest)")

        # VWAP positioning
        if vwap > 70:
            reasons.append("price well above VWAP (institutional support)")
        elif vwap < 30:
            reasons.append("price below VWAP (institutional resistance)")

        return "; ".join(reasons).capitalize() if reasons else "Mixed institutional flow signals"

    def _no_signal(self, symbol: str, reason: str) -> Dict:
        """Return neutral signal when analysis cannot be performed"""
        return {
            'score': 50.0,
            'confidence': 0.2,
            'metrics': {'insufficient_data': True},
            'reasoning': f"Limited institutional flow analysis: {reason}"
        }
