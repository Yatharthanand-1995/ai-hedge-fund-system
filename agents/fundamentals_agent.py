"""
Fundamentals Agent
Analyzes financial health, profitability, growth, and valuation
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, Optional
import logging

# Import data validator
try:
    from utils.data_validator import data_validator
    DATA_VALIDATOR_AVAILABLE = True
except ImportError:
    DATA_VALIDATOR_AVAILABLE = False

logger = logging.getLogger(__name__)


class FundamentalsAgent:
    """
    Scores stocks based on fundamental financial metrics

    Categories (equal weight):
    1. Profitability (25%)
    2. Growth (25%)
    3. Financial Health (25%)
    4. Valuation (25%)
    """

    def __init__(self):
        self.name = "FundamentalsAgent"
        logger.info(f"{self.name} initialized")

    def analyze(self, symbol: str, data: Optional[pd.DataFrame] = None,
                cached_data: Optional[Dict] = None) -> Dict:
        """
        Analyze fundamentals and return score

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
                financials = cached_data.get('financials', pd.DataFrame())
                balance_sheet = cached_data.get('balance_sheet', pd.DataFrame())
                cash_flow = cached_data.get('cashflow', pd.DataFrame())
            else:
                # Fallback to downloading
                ticker = yf.Ticker(symbol)
                info = ticker.info
                financials = ticker.financials
                balance_sheet = ticker.balance_sheet
                cash_flow = ticker.cashflow

            # Calculate scores for each category
            profitability_score = self._score_profitability(info)
            growth_score = self._score_growth(info, financials)
            health_score = self._score_financial_health(info, balance_sheet)
            valuation_score = self._score_valuation(info)

            # Composite score (equal weight)
            composite_score = (
                profitability_score +
                growth_score +
                health_score +
                valuation_score
            ) / 4.0

            # Confidence based on data availability
            confidence = self._calculate_confidence(info, financials, balance_sheet)

            # Enhanced confidence with data quality validation
            if DATA_VALIDATOR_AVAILABLE:
                try:
                    data_quality = data_validator.validate_fundamentals_data(info, financials, balance_sheet)
                    confidence = data_validator.get_quality_adjusted_confidence(confidence, data_quality)
                    logger.debug(f"Data quality validation for {symbol}: {data_quality['quality_score']:.2f}")
                except Exception as e:
                    logger.warning(f"Data quality validation failed for {symbol}: {e}")

            # Build reasoning
            reasoning = self._build_reasoning(
                profitability_score, growth_score,
                health_score, valuation_score
            )

            return {
                'score': round(composite_score, 2),
                'confidence': round(confidence, 2),
                'metrics': {
                    'profitability': profitability_score,
                    'growth': growth_score,
                    'financial_health': health_score,
                    'valuation': valuation_score,
                    'roe': info.get('returnOnEquity', 0) * 100,
                    'net_margin': info.get('profitMargins', 0) * 100,
                    'revenue_growth': info.get('revenueGrowth', 0) * 100,
                    'debt_to_equity': info.get('debtToEquity', 0),
                    'pe_ratio': info.get('trailingPE', 0),
                },
                'reasoning': reasoning
            }

        except Exception as e:
            logger.error(f"Fundamentals analysis failed for {symbol}: {e}")
            # Try partial scoring with basic info if available
            try:
                ticker = yf.Ticker(symbol)
                basic_info = ticker.info

                # Calculate partial score with available basic metrics
                partial_score = self._calculate_partial_score(basic_info)
                partial_confidence = 0.2  # Low confidence for partial data

                return {
                    'score': round(partial_score, 2),
                    'confidence': partial_confidence,
                    'metrics': {
                        'partial_analysis': True,
                        'available_metrics': len([k for k in basic_info.keys() if basic_info.get(k) is not None])
                    },
                    'reasoning': f"Partial analysis due to data issues: {str(e)[:100]}"
                }
            except:
                # Final fallback
                return {
                    'score': 50.0,
                    'confidence': 0.0,
                    'metrics': {},
                    'reasoning': f"Analysis failed: {str(e)}"
                }

    def _score_profitability(self, info: Dict) -> float:
        """Score based on profitability metrics (0-100)"""
        score = 0.0

        # ROE (Return on Equity) - Optimized for Mega-Cap Excellence
        roe = info.get('returnOnEquity', 0) * 100
        if roe > 15:  # Excellent (top 20% of mega-caps)
            score += 40
        elif roe > 12:  # Very good (Apple ~15%, Microsoft ~40%)
            score += 35
        elif roe > 8:   # Good (solid performance)
            score += 25
        elif roe > 5:   # Acceptable
            score += 15
        elif roe > 0:   # At least positive
            score += 5

        # Net Margin - Realistic for Large Tech/Blue Chips
        net_margin = info.get('profitMargins', 0) * 100
        if net_margin > 15:  # Excellent (top tech companies)
            score += 30
        elif net_margin > 12:  # Very good (Apple ~25%, Google ~21%)
            score += 25
        elif net_margin > 8:   # Good (solid profitability)
            score += 20
        elif net_margin > 5:   # Acceptable
            score += 12
        elif net_margin > 2:   # Minimal but positive
            score += 5

        # Operating Margin - Adjusted for Scale Economics
        op_margin = info.get('operatingMargins', 0) * 100
        if op_margin > 20:  # Excellent (top performers)
            score += 30
        elif op_margin > 15:  # Very good (Microsoft ~42%, Apple ~30%)
            score += 25
        elif op_margin > 12:  # Good
            score += 20
        elif op_margin > 8:   # Acceptable
            score += 12
        elif op_margin > 5:   # Basic profitability
            score += 5

        return min(score, 100)

    def _score_growth(self, info: Dict, financials: pd.DataFrame) -> float:
        """Score based on growth metrics (0-100)"""
        score = 0.0

        # Revenue Growth - Realistic for Mature Mega-Caps
        revenue_growth = info.get('revenueGrowth', 0) * 100
        if revenue_growth > 15:  # Excellent growth for large companies
            score += 40
        elif revenue_growth > 10:  # Very good growth
            score += 30
        elif revenue_growth > 6:   # Good growth (Apple ~8%, Microsoft ~12%)
            score += 25
        elif revenue_growth > 3:   # Modest growth
            score += 15
        elif revenue_growth > 0:   # At least growing
            score += 8

        # Earnings Growth - Adjusted for Mega-Cap Scale
        earnings_growth = info.get('earningsGrowth', 0) * 100
        if earnings_growth > 15:  # Excellent earnings growth
            score += 40
        elif earnings_growth > 10:  # Very good growth
            score += 30
        elif earnings_growth > 5:   # Good growth (sustainable for large caps)
            score += 22
        elif earnings_growth > 1:   # Modest positive growth
            score += 12
        elif earnings_growth > -5:  # Slight decline (acceptable in economic cycles)
            score += 5

        # Book Value Growth (if available)
        if not financials.empty and 'Total Stockholder Equity' in financials.index:
            equity_values = financials.loc['Total Stockholder Equity'].values
            if len(equity_values) >= 2:
                equity_growth = (equity_values[0] - equity_values[1]) / equity_values[1] * 100
                if equity_growth > 15:
                    score += 20
                elif equity_growth > 10:
                    score += 15
                elif equity_growth > 5:
                    score += 10

        return min(score, 100)

    def _score_financial_health(self, info: Dict, balance_sheet: pd.DataFrame) -> float:
        """Score based on financial health (0-100)"""
        score = 0.0

        # Current Ratio (liquidity)
        current_ratio = info.get('currentRatio', 0)
        if current_ratio > 2.0:
            score += 35
        elif current_ratio > 1.5:
            score += 25
        elif current_ratio > 1.0:
            score += 15

        # Debt to Equity
        debt_to_equity = info.get('debtToEquity', 0)
        if debt_to_equity < 0.5:
            score += 35
        elif debt_to_equity < 1.0:
            score += 25
        elif debt_to_equity < 2.0:
            score += 15
        elif debt_to_equity < 3.0:
            score += 5

        # Free Cash Flow
        fcf = info.get('freeCashflow', 0)
        if fcf > 0:
            score += 30
            # Bonus for strong FCF
            market_cap = info.get('marketCap', 1)
            fcf_yield = (fcf / market_cap) * 100 if market_cap > 0 else 0
            if fcf_yield > 5:
                score += 10

        return min(score, 100)

    def _score_valuation(self, info: Dict) -> float:
        """Score based on valuation metrics (0-100)"""
        score = 0.0

        # P/E Ratio
        pe = info.get('trailingPE', 0)
        if 0 < pe < 15:
            score += 40
        elif pe < 20:
            score += 30
        elif pe < 25:
            score += 20
        elif pe < 30:
            score += 10

        # P/B Ratio
        pb = info.get('priceToBook', 0)
        if 0 < pb < 2:
            score += 30
        elif pb < 3:
            score += 20
        elif pb < 5:
            score += 10

        # PEG Ratio (P/E to Growth)
        peg = info.get('pegRatio', 0)
        if 0 < peg < 1:
            score += 30
        elif peg < 1.5:
            score += 20
        elif peg < 2:
            score += 10

        return min(score, 100)

    def _calculate_confidence(self, info: Dict, financials: pd.DataFrame,
                             balance_sheet: pd.DataFrame) -> float:
        """Calculate confidence based on data availability"""

        data_points = 0
        available_points = 0

        # Check key metrics with weights
        key_metrics = [
            'returnOnEquity', 'profitMargins', 'operatingMargins',
            'revenueGrowth', 'earningsGrowth',
            'currentRatio', 'debtToEquity', 'freeCashflow',
            'trailingPE', 'priceToBook', 'pegRatio'
        ]

        for metric in key_metrics:
            data_points += 1
            if info.get(metric) is not None and info.get(metric) != 0:
                available_points += 1

        # Check financial statements
        if not financials.empty:
            available_points += 1
        data_points += 1

        if not balance_sheet.empty:
            available_points += 1
        data_points += 1

        confidence = available_points / data_points if data_points > 0 else 0

        # Minimum confidence threshold for partial scoring
        return max(confidence, 0.3)  # Ensure minimum 30% confidence

    def _build_reasoning(self, prof: float, growth: float, health: float, val: float) -> str:
        """Build human-readable reasoning"""

        reasons = []

        if prof > 70:
            reasons.append("Excellent profitability")
        elif prof > 50:
            reasons.append("Good profitability")
        elif prof < 30:
            reasons.append("Weak profitability")

        if growth > 70:
            reasons.append("strong growth")
        elif growth > 50:
            reasons.append("moderate growth")
        elif growth < 30:
            reasons.append("low growth")

        if health > 70:
            reasons.append("solid financial health")
        elif health > 50:
            reasons.append("adequate financial health")
        elif health < 30:
            reasons.append("weak balance sheet")

        if val > 70:
            reasons.append("attractive valuation")
        elif val > 50:
            reasons.append("fair valuation")
        elif val < 30:
            reasons.append("expensive valuation")

        return "; ".join(reasons).capitalize() if reasons else "Mixed signals"

    def _calculate_partial_score(self, info: Dict) -> float:
        """Calculate partial score with minimal data available"""
        score = 50.0  # Start with neutral

        # Basic profitability check
        if info.get('profitMargins'):
            margin = info.get('profitMargins', 0) * 100
            if margin > 10:
                score += 15
            elif margin > 5:
                score += 10
            elif margin > 0:
                score += 5

        # Basic valuation check
        if info.get('trailingPE'):
            pe = info.get('trailingPE', 0)
            if 10 < pe < 25:
                score += 10
            elif pe < 30:
                score += 5

        # Market cap bonus (for quality/stability)
        market_cap = info.get('marketCap', 0)
        if market_cap > 100e9:  # Large cap
            score += 10
        elif market_cap > 50e9:
            score += 5

        return min(max(score, 20), 80)  # Bound between 20-80 for partial analysis