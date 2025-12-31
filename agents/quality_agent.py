"""
Quality Agent
Analyzes business quality, market position, and stability
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class QualityAgent:
    """
    Scores stocks based on business quality

    Categories:
    1. Market position (30%) - size, sector leadership
    2. Stability (30%) - revenue/profit consistency
    3. Competitive moat (20%) - margins, market share
    4. Quality metrics (20%) - ROE stability, cash generation
    """

    def __init__(self, sector_mapping: Optional[Dict] = None):
        self.name = "QualityAgent"
        self.sector_mapping = sector_mapping or {}
        logger.info(f"{self.name} initialized")

    def analyze(self, symbol: str, data: Optional[pd.DataFrame] = None,
                cached_data: Optional[Dict] = None) -> Dict:
        """
        Analyze quality and return score

        Args:
            symbol: Stock symbol
            data: Optional price data (deprecated, use cached_data)
            cached_data: Optional cached data from EnhancedYahooProvider

        Returns:
            {
                'score': 0-100,
                'confidence': 0-1,
                'metrics': {...},
                'reasoning': str
            }
        """

        try:
            # Use cached data if available (faster, reduces API calls)
            if cached_data:
                info = cached_data.get('info', {})
                financials = cached_data.get('financials', pd.DataFrame())
                quarterly_financials = cached_data.get('quarterly_financials', pd.DataFrame())
            else:
                # Fallback to fetching fresh data
                ticker = yf.Ticker(symbol)
                info = ticker.info
                financials = ticker.financials
                quarterly_financials = ticker.quarterly_financials

            # Calculate scores
            market_position_score = self._score_market_position(info, symbol)
            stability_score = self._score_stability(info, financials, quarterly_financials)
            moat_score = self._score_competitive_moat(info)
            quality_metrics_score = self._score_quality_metrics(info, financials)

            # Composite score
            composite_score = (
                0.30 * market_position_score +
                0.30 * stability_score +
                0.20 * moat_score +
                0.20 * quality_metrics_score
            )

            # Confidence
            confidence = self._calculate_confidence(info, financials)

            reasoning = self._build_reasoning(
                market_position_score, stability_score,
                moat_score, quality_metrics_score
            )

            return {
                'score': round(composite_score, 2),
                'confidence': round(confidence, 2),
                'metrics': {
                    'market_position': market_position_score,
                    'stability': stability_score,
                    'competitive_moat': moat_score,
                    'quality_metrics': quality_metrics_score,
                    'market_cap': info.get('marketCap', 0),
                    'sector': self._get_sector(symbol),
                    'profit_margin': info.get('profitMargins', 0) * 100,
                },
                'reasoning': reasoning
            }

        except Exception as e:
            logger.error(f"Quality analysis failed for {symbol}: {e}")
            return {
                'score': 50.0,
                'confidence': 0.0,
                'metrics': {},
                'reasoning': f"Analysis failed: {str(e)}"
            }

    def _score_market_position(self, info: Dict, symbol: str) -> float:
        """Score based on market cap and sector position (0-100)"""
        score = 0.0

        # Market Cap tier
        market_cap = info.get('marketCap', 0)

        if market_cap > 500e9:  # Mega cap (>$500B)
            score += 50
        elif market_cap > 200e9:  # Large cap+ (>$200B)
            score += 40
        elif market_cap > 100e9:  # Large cap (>$100B)
            score += 30
        elif market_cap > 50e9:  # Mid-large cap
            score += 20
        else:
            score += 10

        # Sector leadership (heuristic: top market cap in sector)
        sector = self._get_sector(symbol)
        if sector in ['Technology', 'Healthcare', 'Financial']:
            score += 20  # Bonus for being in strong sectors

        # Exchange (NYSE/NASDAQ = quality)
        exchange = info.get('exchange', '')
        if exchange in ['NMS', 'NYQ']:
            score += 20

        # Company age/establishment (if available)
        # Older companies = more established
        if 'longBusinessSummary' in info:
            score += 10

        return min(score, 100)

    def _score_stability(self, info: Dict, financials: pd.DataFrame, quarterly: pd.DataFrame) -> float:
        """Score based on revenue/profit stability (0-100)"""
        score = 0.0

        # Revenue consistency
        if not financials.empty and 'Total Revenue' in financials.index:
            revenues = financials.loc['Total Revenue'].values
            if len(revenues) >= 3:
                # Check if revenues are growing consistently (not volatile)
                # Validate data before calculation to prevent division by zero and NaN issues
                if not np.any(np.isnan(revenues)) and not np.any(revenues[1:] == 0):
                    revenue_changes = np.diff(revenues) / revenues[1:]

                    # Check if revenue_changes contains valid data
                    if not np.any(np.isnan(revenue_changes)) and len(revenue_changes) > 0:
                        volatility = np.std(revenue_changes)

                        if volatility < 0.1:  # Low volatility
                            score += 40
                        elif volatility < 0.2:
                            score += 30
                        elif volatility < 0.3:
                            score += 20

                        # All positive growth
                        if all(change > 0 for change in revenue_changes):
                            score += 20

        # Profit margin stability
        profit_margin = info.get('profitMargins', 0)
        if profit_margin > 0.15:  # Consistent high margins
            score += 40
        elif profit_margin > 0.10:
            score += 30
        elif profit_margin > 0.05:
            score += 20

        return min(score, 100)

    def _score_competitive_moat(self, info: Dict) -> float:
        """Score based on indicators of competitive advantage (0-100)"""
        score = 0.0

        # High margins = pricing power
        gross_margin = info.get('grossMargins', 0)
        if gross_margin > 0.50:
            score += 40
        elif gross_margin > 0.40:
            score += 30
        elif gross_margin > 0.30:
            score += 20

        # Operating margin
        operating_margin = info.get('operatingMargins', 0)
        if operating_margin > 0.25:
            score += 30
        elif operating_margin > 0.20:
            score += 20
        elif operating_margin > 0.15:
            score += 10

        # Return on Assets (efficiency)
        roa = info.get('returnOnAssets', 0)
        if roa > 0.15:
            score += 30
        elif roa > 0.10:
            score += 20
        elif roa > 0.05:
            score += 10

        return min(score, 100)

    def _score_quality_metrics(self, info: Dict, financials: pd.DataFrame) -> float:
        """Score based on high-quality business indicators (0-100)"""
        score = 0.0

        # ROE consistency
        roe = info.get('returnOnEquity', 0)
        if roe > 0.20:
            score += 40
        elif roe > 0.15:
            score += 30
        elif roe > 0.10:
            score += 20

        # Free cash flow generation
        fcf = info.get('freeCashflow', 0)
        operating_cf = info.get('operatingCashflow', 0)

        if fcf > 0 and operating_cf > 0:
            fcf_ratio = fcf / operating_cf if operating_cf > 0 else 0
            if fcf_ratio > 0.7:  # Strong FCF conversion
                score += 40
            elif fcf_ratio > 0.5:
                score += 30
            elif fcf_ratio > 0.3:
                score += 20

        # Share buybacks (returning value to shareholders)
        shares_outstanding_change = info.get('sharesPercentSharesOut', 0)
        if shares_outstanding_change < 0:  # Reducing shares
            score += 20

        return min(score, 100)

    def _calculate_confidence(self, info: Dict, financials: pd.DataFrame) -> float:
        """Calculate confidence based on data availability"""

        data_points = 0
        available_points = 0

        # Key metrics
        key_metrics = [
            'marketCap', 'profitMargins', 'grossMargins', 'operatingMargins',
            'returnOnEquity', 'returnOnAssets', 'freeCashflow', 'operatingCashflow'
        ]

        for metric in key_metrics:
            data_points += 1
            if info.get(metric) is not None:
                available_points += 1

        if not financials.empty:
            available_points += 1
        data_points += 1

        return available_points / data_points if data_points > 0 else 0.5

    def _get_sector(self, symbol: str) -> str:
        """Get sector for symbol from mapping"""
        for sector, symbols in self.sector_mapping.items():
            if symbol in symbols:
                return sector
        return 'Unknown'

    def _build_reasoning(self, market: float, stability: float, moat: float, quality: float) -> str:
        """Build human-readable reasoning"""

        reasons = []

        if market > 70:
            reasons.append("Strong market position")
        elif market < 40:
            reasons.append("Smaller market presence")

        if stability > 70:
            reasons.append("highly stable business")
        elif stability > 50:
            reasons.append("stable operations")
        elif stability < 30:
            reasons.append("volatile business")

        if moat > 70:
            reasons.append("strong competitive moat")
        elif moat > 50:
            reasons.append("good competitive position")
        elif moat < 30:
            reasons.append("weak competitive advantages")

        if quality > 70:
            reasons.append("excellent quality metrics")
        elif quality < 40:
            reasons.append("mixed quality signals")

        return "; ".join(reasons).capitalize() if reasons else "Average quality business"