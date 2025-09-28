"""
Sentiment Agent
Analyzes market sentiment through analyst ratings and other indicators
"""

import yfinance as yf
import pandas as pd
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class SentimentAgent:
    """
    Scores stocks based on market sentiment

    Data sources (with yfinance):
    1. Analyst recommendations (80%)
    2. Target price vs current (20%)

    Note: With free data (yfinance), sentiment analysis is limited.
    Could be enhanced with:
    - News sentiment API
    - Insider trades
    - Social media sentiment
    """

    def __init__(self):
        self.name = "SentimentAgent"
        logger.info(f"{self.name} initialized")

    def analyze(self, symbol: str, data: Optional = None, cached_data: Optional[Dict] = None) -> Dict:
        """
        Analyze sentiment and return score

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
            if cached_data:
                info = cached_data.get('info', {})
                recommendations_df = cached_data.get('recommendations', pd.DataFrame())
                recommendations = self._parse_recommendations(recommendations_df)
            else:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                recommendations = self._get_recommendations(ticker)

            # Calculate scores
            analyst_score = self._score_analyst_ratings(recommendations)
            target_score = self._score_target_price(info)

            # Composite score
            composite_score = (
                0.80 * analyst_score +
                0.20 * target_score
            )

            # Confidence based on data availability
            confidence = self._calculate_confidence(recommendations, info)

            reasoning = self._build_reasoning(analyst_score, target_score, recommendations, info)

            return {
                'score': round(composite_score, 2),
                'confidence': round(confidence, 2),
                'metrics': {
                    'analyst_rating': analyst_score,
                    'target_price_upside': target_score,
                    'recommendations': recommendations,
                    'target_price': info.get('targetMeanPrice', 0),
                    'current_price': info.get('currentPrice', 0),
                },
                'reasoning': reasoning
            }

        except Exception as e:
            logger.error(f"Sentiment analysis failed for {symbol}: {e}")
            return {
                'score': 50.0,
                'confidence': 0.0,
                'metrics': {},
                'reasoning': f"Analysis failed: {str(e)}"
            }

    def _parse_recommendations(self, recs: pd.DataFrame) -> Dict:
        """Parse recommendations DataFrame into counts"""
        counts = {
            'strongBuy': 0,
            'buy': 0,
            'hold': 0,
            'sell': 0,
            'strongSell': 0
        }

        if recs is None or recs.empty:
            return counts

        try:
            # Get most recent recommendations
            recent = recs.tail(20)

            for _, row in recent.iterrows():
                action = row.get('To Grade', '').lower()
                if 'strong buy' in action or 'outperform' in action:
                    counts['strongBuy'] += 1
                elif 'buy' in action:
                    counts['buy'] += 1
                elif 'sell' in action and 'strong' not in action:
                    counts['sell'] += 1
                elif 'strong sell' in action or 'underperform' in action:
                    counts['strongSell'] += 1
                else:
                    counts['hold'] += 1

        except Exception as e:
            logger.warning(f"Failed to parse recommendations: {e}")

        return counts

    def _get_recommendations(self, ticker) -> Dict:
        """Get analyst recommendations"""
        try:
            recs = ticker.recommendations
            if recs is not None and not recs.empty:
                # Get most recent recommendations
                recent = recs.tail(20)  # Last 20 recommendations

                counts = {
                    'strongBuy': 0,
                    'buy': 0,
                    'hold': 0,
                    'sell': 0,
                    'strongSell': 0
                }

                for _, row in recent.iterrows():
                    action = row.get('To Grade', '').lower()
                    if 'strong buy' in action or 'outperform' in action:
                        counts['strongBuy'] += 1
                    elif 'buy' in action:
                        counts['buy'] += 1
                    elif 'sell' in action and 'strong' not in action:
                        counts['sell'] += 1
                    elif 'strong sell' in action or 'underperform' in action:
                        counts['strongSell'] += 1
                    else:
                        counts['hold'] += 1

                return counts

        except Exception as e:
            logger.warning(f"Failed to get recommendations: {e}")

        return {'strongBuy': 0, 'buy': 0, 'hold': 0, 'sell': 0, 'strongSell': 0}

    def _score_analyst_ratings(self, recommendations: Dict) -> float:
        """Score based on analyst recommendations (0-100)"""

        total = sum(recommendations.values())
        if total == 0:
            return 50  # Neutral if no data

        # Weight different ratings
        weighted_score = (
            recommendations['strongBuy'] * 100 +
            recommendations['buy'] * 75 +
            recommendations['hold'] * 50 +
            recommendations['sell'] * 25 +
            recommendations['strongSell'] * 0
        )

        score = weighted_score / total if total > 0 else 50

        return min(max(score, 0), 100)

    def _score_target_price(self, info: Dict) -> float:
        """Score based on target price upside (0-100)"""

        target_price = info.get('targetMeanPrice', 0)
        current_price = info.get('currentPrice', 0)

        if target_price == 0 or current_price == 0:
            return 50  # Neutral if no data

        upside = (target_price - current_price) / current_price * 100

        # Score based on upside percentage
        if upside > 30:
            return 100
        elif upside > 20:
            return 90
        elif upside > 15:
            return 80
        elif upside > 10:
            return 70
        elif upside > 5:
            return 60
        elif upside > 0:
            return 55
        elif upside > -5:
            return 45
        elif upside > -10:
            return 35
        elif upside > -15:
            return 25
        else:
            return 10

    def _calculate_confidence(self, recommendations: Dict, info: Dict) -> float:
        """Calculate confidence based on data availability"""

        confidence = 0.0

        # Check if we have recommendations
        total_recs = sum(recommendations.values())
        if total_recs > 0:
            confidence += 0.6
            # More recommendations = higher confidence
            if total_recs >= 10:
                confidence += 0.2

        # Check if we have target price
        if info.get('targetMeanPrice', 0) > 0:
            confidence += 0.2

        return min(confidence, 1.0)

    def _build_reasoning(self, analyst_score: float, target_score: float,
                        recommendations: Dict, info: Dict) -> str:
        """Build human-readable reasoning"""

        reasons = []

        # Analyst sentiment
        total_recs = sum(recommendations.values())
        if total_recs > 0:
            buy_count = recommendations['strongBuy'] + recommendations['buy']
            sell_count = recommendations['sell'] + recommendations['strongSell']

            if buy_count > sell_count * 2:
                reasons.append("Strong analyst bullish consensus")
            elif buy_count > sell_count:
                reasons.append("Analysts lean bullish")
            elif sell_count > buy_count:
                reasons.append("Analysts lean bearish")
            else:
                reasons.append("Mixed analyst views")

        # Target price
        target = info.get('targetMeanPrice', 0)
        current = info.get('currentPrice', 0)
        if target > 0 and current > 0:
            upside = (target - current) / current * 100
            if upside > 15:
                reasons.append(f"significant upside to target ({upside:.1f}%)")
            elif upside > 5:
                reasons.append(f"moderate upside to target ({upside:.1f}%)")
            elif upside < -5:
                reasons.append(f"trading above target ({upside:.1f}%)")

        return "; ".join(reasons).capitalize() if reasons else "Limited sentiment data"