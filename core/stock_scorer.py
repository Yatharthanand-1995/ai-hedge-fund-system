"""
Stock Scorer
Orchestrates all agents and combines their scores
"""

import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional
import logging

from agents import FundamentalsAgent, MomentumAgent, QualityAgent, SentimentAgent

logger = logging.getLogger(__name__)


class StockScorer:
    """
    Combines all agent scores to rank stocks

    Agent Weights:
    - Fundamentals: 40%
    - Momentum: 30%
    - Quality: 20%
    - Sentiment: 10%
    """

    def __init__(self, sector_mapping: Optional[Dict] = None, agent_weights: Optional[Dict] = None):
        self.fundamentals_agent = FundamentalsAgent()
        self.momentum_agent = MomentumAgent()
        self.quality_agent = QualityAgent(sector_mapping=sector_mapping)
        self.sentiment_agent = SentimentAgent()

        # Weights (use custom if provided, otherwise use defaults)
        self.weights = agent_weights or {
            'fundamentals': 0.40,
            'momentum': 0.30,
            'quality': 0.20,
            'sentiment': 0.10
        }

        logger.info(f"StockScorer initialized with 4 agents (weights: {self.weights})")

    def score_stock(self, symbol: str, price_data: Optional[pd.DataFrame] = None,
                   spy_data: Optional[pd.DataFrame] = None,
                   cached_data: Optional[Dict] = None) -> Dict:
        """
        Score a single stock using all agents

        Args:
            symbol: Stock ticker
            price_data: Historical price data (optional, will download if None)
            spy_data: SPY data for relative strength (optional)

        Returns:
            {
                'symbol': str,
                'composite_score': 0-100,
                'composite_confidence': 0-1,
                'agent_scores': {...},
                'reasoning': str,
                'rank_category': str  # 'Strong Buy', 'Buy', 'Hold', 'Sell'
            }
        """

        try:
            # Download price data if not provided
            if price_data is None:
                price_data = yf.download(symbol, period='2y', progress=False)

            # Download SPY if not provided
            if spy_data is None:
                spy_data = yf.download('SPY', period='2y', progress=False)

            # Get scores from each agent (pass cached data if available)
            fund_result = self.fundamentals_agent.analyze(symbol, cached_data=cached_data)
            mom_result = self.momentum_agent.analyze(symbol, price_data, spy_data)
            qual_result = self.quality_agent.analyze(symbol, price_data)
            sent_result = self.sentiment_agent.analyze(symbol, cached_data=cached_data)

            # Calculate weighted composite score
            composite_score = (
                self.weights['fundamentals'] * fund_result['score'] +
                self.weights['momentum'] * mom_result['score'] +
                self.weights['quality'] * qual_result['score'] +
                self.weights['sentiment'] * sent_result['score']
            )

            # Composite confidence (weighted average of confidences)
            composite_confidence = (
                self.weights['fundamentals'] * fund_result['confidence'] +
                self.weights['momentum'] * mom_result['confidence'] +
                self.weights['quality'] * qual_result['confidence'] +
                self.weights['sentiment'] * sent_result['confidence']
            )

            # Determine rank category
            rank_category = self._get_rank_category(composite_score, composite_confidence)

            # Combined reasoning
            reasoning = self._combine_reasoning(
                fund_result, mom_result, qual_result, sent_result
            )

            return {
                'symbol': symbol,
                'composite_score': round(composite_score, 2),
                'composite_confidence': round(composite_confidence, 2),
                'agent_scores': {
                    'fundamentals': {
                        'score': fund_result['score'],
                        'confidence': fund_result['confidence'],
                        'reasoning': fund_result['reasoning']
                    },
                    'momentum': {
                        'score': mom_result['score'],
                        'confidence': mom_result['confidence'],
                        'reasoning': mom_result['reasoning']
                    },
                    'quality': {
                        'score': qual_result['score'],
                        'confidence': qual_result['confidence'],
                        'reasoning': qual_result['reasoning']
                    },
                    'sentiment': {
                        'score': sent_result['score'],
                        'confidence': sent_result['confidence'],
                        'reasoning': sent_result['reasoning']
                    }
                },
                'metrics': {
                    **fund_result.get('metrics', {}),
                    **mom_result.get('metrics', {}),
                },
                'reasoning': reasoning,
                'rank_category': rank_category
            }

        except Exception as e:
            logger.error(f"Failed to score {symbol}: {e}")
            return {
                'symbol': symbol,
                'composite_score': 50.0,
                'composite_confidence': 0.0,
                'agent_scores': {},
                'metrics': {},
                'reasoning': f"Scoring failed: {str(e)}",
                'rank_category': 'Error'
            }

    def score_universe(self, symbols: List[str], verbose: bool = True) -> List[Dict]:
        """
        Score all stocks in a universe

        Args:
            symbols: List of stock tickers
            verbose: Print progress

        Returns:
            List of score dictionaries, sorted by composite_score descending
        """

        results = []

        # Download SPY once for all stocks
        spy_data = yf.download('SPY', period='2y', progress=False)

        for i, symbol in enumerate(symbols, 1):
            if verbose:
                print(f"[{i}/{len(symbols)}] Scoring {symbol}...", end=" ")

            result = self.score_stock(symbol, spy_data=spy_data)
            results.append(result)

            if verbose:
                print(f"{result['composite_score']:.1f} ({result['rank_category']})")

        # Sort by composite score descending
        results.sort(key=lambda x: x['composite_score'], reverse=True)

        return results

    def _get_rank_category(self, score: float, confidence: float) -> str:
        """Categorize stock based on score and confidence"""

        # Adjust score by confidence
        adjusted_score = score * (0.5 + 0.5 * confidence)  # Min 50% weight, max 100%

        if adjusted_score >= 75:
            return "Strong Buy"
        elif adjusted_score >= 65:
            return "Buy"
        elif adjusted_score >= 50:
            return "Hold"
        elif adjusted_score >= 35:
            return "Underweight"
        else:
            return "Sell"

    def _combine_reasoning(self, fund: Dict, mom: Dict, qual: Dict, sent: Dict) -> str:
        """Combine reasoning from all agents"""

        reasons = []

        # Fundamentals (highest weight)
        if fund['score'] > 70:
            reasons.append(f"Strong fundamentals: {fund['reasoning']}")
        elif fund['score'] < 40:
            reasons.append(f"Weak fundamentals: {fund['reasoning']}")

        # Momentum
        if mom['score'] > 70:
            reasons.append(f"Momentum: {mom['reasoning']}")
        elif mom['score'] < 40:
            reasons.append(f"Momentum: {mom['reasoning']}")

        # Quality
        if qual['score'] > 70:
            reasons.append(f"Quality: {qual['reasoning']}")
        elif qual['score'] < 40:
            reasons.append(f"Quality: {qual['reasoning']}")

        # Sentiment (if meaningful)
        if sent['confidence'] > 0.5:
            if sent['score'] > 65:
                reasons.append(f"Sentiment: {sent['reasoning']}")
            elif sent['score'] < 45:
                reasons.append(f"Sentiment: {sent['reasoning']}")

        return " | ".join(reasons) if reasons else "Mixed signals across all factors"