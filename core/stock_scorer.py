"""
Stock Scorer
Orchestrates all agents and combines their scores
"""

import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional
import logging
import os

from agents import FundamentalsAgent, MomentumAgent, QualityAgent, SentimentAgent
from agents.institutional_flow_agent import InstitutionalFlowAgent
from data.enhanced_provider import EnhancedYahooProvider

logger = logging.getLogger(__name__)


class StockScorer:
    """
    Combines all agent scores to rank stocks

    Agent Weights (Default - Static):
    - Fundamentals: 36%
    - Momentum: 27%
    - Quality: 18%
    - Sentiment: 9%
    - Institutional Flow: 10%

    With Adaptive Weights (ENABLE_ADAPTIVE_WEIGHTS=true):
    - Weights automatically adjust based on market regime
    - Bull markets: Higher momentum weight
    - Bear markets: Higher fundamentals/quality weight
    - High volatility: Higher quality weight
    """

    def __init__(self, sector_mapping: Optional[Dict] = None, agent_weights: Optional[Dict] = None,
                 use_adaptive_weights: Optional[bool] = None):
        self.fundamentals_agent = FundamentalsAgent()
        self.momentum_agent = MomentumAgent()
        self.quality_agent = QualityAgent(sector_mapping=sector_mapping)
        self.sentiment_agent = SentimentAgent()
        self.institutional_flow_agent = InstitutionalFlowAgent()
        self.data_provider = EnhancedYahooProvider()  # For comprehensive data including institutional indicators

        # Default static weights (5-agent system)
        self.default_weights = {
            'fundamentals': 0.36,
            'momentum': 0.27,
            'quality': 0.18,
            'sentiment': 0.09,
            'institutional_flow': 0.10
        }

        # Determine if adaptive weights should be used
        if use_adaptive_weights is None:
            # Check environment variable
            use_adaptive_weights = os.getenv('ENABLE_ADAPTIVE_WEIGHTS', 'false').lower() == 'true'

        self.use_adaptive_weights = use_adaptive_weights

        # Weights (use custom if provided, otherwise use defaults or adaptive)
        if agent_weights:
            self.weights = agent_weights
            self.use_adaptive_weights = False  # Custom weights override adaptive
        else:
            self.weights = self.default_weights.copy()

        # Initialize market regime service if adaptive weights enabled
        self.market_regime_service = None
        if self.use_adaptive_weights:
            try:
                from core.market_regime_service import get_market_regime_service
                self.market_regime_service = get_market_regime_service()
                logger.info("✅ Adaptive agent weights ENABLED (will adjust based on market regime)")
            except Exception as e:
                logger.warning(f"Failed to initialize adaptive weights: {e}. Using static weights.")
                self.use_adaptive_weights = False
        else:
            logger.info("Using static agent weights (36/27/18/9/10)")

        logger.info(f"StockScorer initialized with 5 agents (weights: {self.weights})")

    def score_stock(self, symbol: str, price_data: Optional[pd.DataFrame] = None,
                   spy_data: Optional[pd.DataFrame] = None,
                   cached_data: Optional[Dict] = None) -> Dict:
        """
        Score a single stock using all agents

        Args:
            symbol: Stock ticker
            price_data: Historical price data (optional, will download if None)
            spy_data: SPY data for relative strength (optional)
            cached_data: Optional cached data to avoid redundant API calls

        Returns:
            {
                'symbol': str,
                'composite_score': 0-100,
                'composite_confidence': 0-1,
                'agent_scores': {...},
                'reasoning': str,
                'rank_category': str,  # 'Strong Buy', 'Buy', 'Hold', 'Sell'
                'market_regime': str (if adaptive weights enabled),
                'weights_used': Dict[str, float]
            }
        """

        try:
            # Get current weights (adaptive or static)
            current_weights = self._get_current_weights()
            market_regime_info = None

            # If no cached_data, fetch comprehensive data for institutional flow agent
            if cached_data is None:
                cached_data = self.data_provider.get_comprehensive_data(symbol)

            # Download price data if not provided
            if price_data is None:
                price_data = cached_data.get('historical_data')
                if price_data is None or price_data.empty:
                    price_data = yf.download(symbol, period='2y', progress=False)

            # Download SPY if not provided
            if spy_data is None:
                spy_data = yf.download('SPY', period='2y', progress=False)

            # Get scores from each agent (pass cached data if available)
            fund_result = self.fundamentals_agent.analyze(symbol, cached_data=cached_data)
            mom_result = self.momentum_agent.analyze(symbol, price_data, spy_data)
            qual_result = self.quality_agent.analyze(symbol, price_data)
            sent_result = self.sentiment_agent.analyze(symbol, cached_data=cached_data)
            flow_result = self.institutional_flow_agent.analyze(symbol, price_data, cached_data=cached_data)

            # Calculate weighted composite score using current weights
            composite_score = (
                current_weights['fundamentals'] * fund_result['score'] +
                current_weights['momentum'] * mom_result['score'] +
                current_weights['quality'] * qual_result['score'] +
                current_weights['sentiment'] * sent_result['score'] +
                current_weights['institutional_flow'] * flow_result['score']
            )

            # Composite confidence (weighted average of confidences)
            composite_confidence = (
                current_weights['fundamentals'] * fund_result['confidence'] +
                current_weights['momentum'] * mom_result['confidence'] +
                current_weights['quality'] * qual_result['confidence'] +
                current_weights['sentiment'] * sent_result['confidence'] +
                current_weights['institutional_flow'] * flow_result['confidence']
            )

            # Get market regime info if adaptive weights are enabled
            if self.use_adaptive_weights and self.market_regime_service:
                try:
                    market_regime_info = self.market_regime_service.get_current_regime()
                except Exception as e:
                    logger.warning(f"Failed to get market regime: {e}")
                    market_regime_info = None

            # Determine rank category
            rank_category = self._get_rank_category(composite_score, composite_confidence)

            # Combined reasoning
            reasoning = self._combine_reasoning(
                fund_result, mom_result, qual_result, sent_result, flow_result
            )

            result = {
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
                    },
                    'institutional_flow': {
                        'score': flow_result['score'],
                        'confidence': flow_result['confidence'],
                        'reasoning': flow_result['reasoning']
                    }
                },
                'metrics': {
                    **fund_result.get('metrics', {}),
                    **mom_result.get('metrics', {}),
                },
                'reasoning': reasoning,
                'rank_category': rank_category,
                'weights_used': current_weights
            }

            # Add market regime info if available
            if market_regime_info:
                result['market_regime'] = {
                    'regime': market_regime_info.get('regime'),
                    'trend': market_regime_info.get('trend'),
                    'volatility': market_regime_info.get('volatility')
                }

            return result

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

    def _get_current_weights(self) -> Dict[str, float]:
        """
        Get current agent weights (adaptive or static)

        Returns:
            Dict with agent weights
        """
        if self.use_adaptive_weights and self.market_regime_service:
            try:
                adaptive_weights = self.market_regime_service.get_adaptive_weights()
                logger.debug(f"Using adaptive weights: {adaptive_weights}")
                return adaptive_weights
            except Exception as e:
                logger.warning(f"Failed to get adaptive weights: {e}. Using static weights.")
                return self.default_weights.copy()
        else:
            return self.weights.copy()

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

    def _combine_reasoning(self, fund: Dict, mom: Dict, qual: Dict, sent: Dict, flow: Dict) -> str:
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

        # Institutional Flow (new!)
        if flow['confidence'] > 0.5:
            if flow['score'] > 65:
                reasons.append(f"Institutional Flow: {flow['reasoning']}")
            elif flow['score'] < 45:
                reasons.append(f"Institutional Flow: {flow['reasoning']}")

        # Sentiment (if meaningful)
        if sent['confidence'] > 0.5:
            if sent['score'] > 65:
                reasons.append(f"Sentiment: {sent['reasoning']}")
            elif sent['score'] < 45:
                reasons.append(f"Sentiment: {sent['reasoning']}")

        return " | ".join(reasons) if reasons else "Mixed signals across all factors"