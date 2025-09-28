"""
Fundamentals Agent
Analyzes financial health, profitability, growth, and valuation
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, Optional
import logging

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
            return {
                'score': 50.0,
                'confidence': 0.0,
                'metrics': {},
                'reasoning': f"Analysis failed: {str(e)}"
            }

    def _score_profitability(self, info: Dict) -> float:
        """Score based on profitability metrics (0-100)"""
        score = 0.0

        # ROE (Return on Equity)
        roe = info.get('returnOnEquity', 0) * 100
        if roe > 20:
            score += 40
        elif roe > 15:
            score += 30
        elif roe > 10:
            score += 20
        elif roe > 5:
            score += 10

        # Net Margin
        net_margin = info.get('profitMargins', 0) * 100
        if net_margin > 20:
            score += 30
        elif net_margin > 15:
            score += 20
        elif net_margin > 10:
            score += 15
        elif net_margin > 5:
            score += 10

        # Operating Margin
        op_margin = info.get('operatingMargins', 0) * 100
        if op_margin > 25:
            score += 30
        elif op_margin > 20:
            score += 20
        elif op_margin > 15:
            score += 15
        elif op_margin > 10:
            score += 10

        return min(score, 100)

    def _score_growth(self, info: Dict, financials: pd.DataFrame) -> float:
        """Score based on growth metrics (0-100)"""
        score = 0.0

        # Revenue Growth
        revenue_growth = info.get('revenueGrowth', 0) * 100
        if revenue_growth > 20:
            score += 40
        elif revenue_growth > 15:
            score += 30
        elif revenue_growth > 10:
            score += 20
        elif revenue_growth > 5:
            score += 10

        # Earnings Growth
        earnings_growth = info.get('earningsGrowth', 0) * 100
        if earnings_growth > 20:
            score += 40
        elif earnings_growth > 15:
            score += 30
        elif earnings_growth > 10:
            score += 20
        elif earnings_growth > 5:
            score += 10

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

        # Check key metrics
        key_metrics = [
            'returnOnEquity', 'profitMargins', 'operatingMargins',
            'revenueGrowth', 'earningsGrowth',
            'currentRatio', 'debtToEquity', 'freeCashflow',
            'trailingPE', 'priceToBook', 'pegRatio'
        ]

        for metric in key_metrics:
            data_points += 1
            if info.get(metric) is not None:
                available_points += 1

        # Check financial statements
        if not financials.empty:
            available_points += 1
        data_points += 1

        if not balance_sheet.empty:
            available_points += 1
        data_points += 1

        confidence = available_points / data_points if data_points > 0 else 0
        return confidence

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