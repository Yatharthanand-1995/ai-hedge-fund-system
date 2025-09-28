"""
Portfolio Manager
Selects top stocks and manages portfolio rebalancing
"""

import pandas as pd
from typing import Dict, List, Optional
import logging

from .stock_scorer import StockScorer

logger = logging.getLogger(__name__)


class PortfolioManager:
    """
    Manages portfolio selection and rebalancing based on stock scores
    """

    def __init__(self, sector_mapping: Optional[Dict] = None, max_sector_weight: float = 0.30):
        self.scorer = StockScorer(sector_mapping=sector_mapping)
        self.sector_mapping = sector_mapping or {}
        self.max_sector_weight = max_sector_weight
        logger.info(f"PortfolioManager initialized (max sector weight: {max_sector_weight*100}%)")

    def select_portfolio(self, universe: List[str], top_n: int = 20,
                        min_score: float = 60, min_confidence: float = 0.4) -> Dict:
        """
        Select top N stocks from universe with sector diversification

        Args:
            universe: List of stock symbols to choose from
            top_n: Number of stocks to select
            min_score: Minimum composite score (0-100)
            min_confidence: Minimum confidence (0-1)

        Returns:
            {
                'selected_stocks': List[str],
                'scores': Dict[str, Dict],
                'summary': Dict
            }
        """

        logger.info(f"Selecting portfolio from {len(universe)} stocks (top {top_n})")

        # Score all stocks
        all_scores = self.scorer.score_universe(universe, verbose=True)

        # Filter by minimum thresholds
        qualified = [
            score for score in all_scores
            if score['composite_score'] >= min_score
            and score['composite_confidence'] >= min_confidence
        ]

        logger.info(f"Qualified stocks: {len(qualified)}/{len(universe)}")

        # Select top N with sector constraints
        selected = []
        sector_counts = {}
        max_per_sector = int(top_n * self.max_sector_weight)

        for score in qualified:
            if len(selected) >= top_n:
                break

            symbol = score['symbol']
            sector = self.sector_mapping.get(symbol, 'Unknown')

            # Check sector limit
            current_count = sector_counts.get(sector, 0)
            if current_count >= max_per_sector:
                logger.debug(f"Skipping {symbol} - sector {sector} at limit ({max_per_sector})")
                continue

            selected.append(score)
            sector_counts[sector] = current_count + 1

        selected_symbols = [s['symbol'] for s in selected]

        # Create scores dict
        scores_dict = {s['symbol']: s for s in selected}

        # Summary stats
        if selected:
            avg_score = sum(s['composite_score'] for s in selected) / len(selected)
            avg_confidence = sum(s['composite_confidence'] for s in selected) / len(selected)

            # Count by category
            categories = {}
            for s in selected:
                cat = s['rank_category']
                categories[cat] = categories.get(cat, 0) + 1

            summary = {
                'total_selected': len(selected),
                'avg_score': round(avg_score, 2),
                'avg_confidence': round(avg_confidence, 2),
                'score_range': [
                    round(selected[-1]['composite_score'], 2),
                    round(selected[0]['composite_score'], 2)
                ],
                'categories': categories,
                'sector_distribution': sector_counts,
                'max_per_sector': max_per_sector,
                'min_score_threshold': min_score,
                'min_confidence_threshold': min_confidence
            }
        else:
            summary = {
                'total_selected': 0,
                'avg_score': 0,
                'avg_confidence': 0,
                'score_range': [0, 0],
                'categories': {},
                'sector_distribution': {},
                'max_per_sector': max_per_sector,
                'min_score_threshold': min_score,
                'min_confidence_threshold': min_confidence
            }

        return {
            'selected_stocks': selected_symbols,
            'scores': scores_dict,
            'all_scores': all_scores,  # Include all for analysis
            'summary': summary
        }

    def rebalance(self, current_portfolio: List[str], universe: List[str],
                 top_n: int = 20, min_score: float = 60) -> Dict:
        """
        Rebalance portfolio based on new scores

        Args:
            current_portfolio: Currently held stocks
            universe: Full universe to select from
            top_n: Target portfolio size
            min_score: Minimum score threshold

        Returns:
            {
                'hold': List[str],  # Keep these
                'sell': List[str],  # Sell these
                'buy': List[str],   # Buy these
                'new_portfolio': List[str],
                'summary': Dict
            }
        """

        logger.info(f"Rebalancing portfolio ({len(current_portfolio)} → {top_n} stocks)")

        # Get new top picks
        new_selection = self.select_portfolio(universe, top_n=top_n, min_score=min_score)
        new_portfolio = new_selection['selected_stocks']

        # Determine actions
        hold = [s for s in current_portfolio if s in new_portfolio]
        sell = [s for s in current_portfolio if s not in new_portfolio]
        buy = [s for s in new_portfolio if s not in current_portfolio]

        summary = {
            'hold_count': len(hold),
            'sell_count': len(sell),
            'buy_count': len(buy),
            'turnover_rate': len(sell) / len(current_portfolio) if current_portfolio else 0,
            'portfolio_size': len(new_portfolio)
        }

        logger.info(f"Rebalance: Hold {len(hold)}, Sell {len(sell)}, Buy {len(buy)}")

        return {
            'hold': hold,
            'sell': sell,
            'buy': buy,
            'new_portfolio': new_portfolio,
            'scores': new_selection['scores'],
            'summary': summary
        }

    def get_top_picks(self, universe: List[str], n: int = 10) -> pd.DataFrame:
        """
        Get top N stock picks as a DataFrame

        Args:
            universe: Stock symbols
            n: Number of top picks

        Returns:
            DataFrame with top picks and their scores
        """

        selection = self.select_portfolio(universe, top_n=n, min_score=0, min_confidence=0)

        data = []
        for symbol in selection['selected_stocks']:
            score_data = selection['scores'][symbol]
            data.append({
                'Symbol': symbol,
                'Score': score_data['composite_score'],
                'Confidence': score_data['composite_confidence'],
                'Category': score_data['rank_category'],
                'Fundamentals': score_data['agent_scores']['fundamentals']['score'],
                'Momentum': score_data['agent_scores']['momentum']['score'],
                'Quality': score_data['agent_scores']['quality']['score'],
                'Sentiment': score_data['agent_scores']['sentiment']['score'],
                'Reasoning': score_data['reasoning']
            })

        df = pd.DataFrame(data)
        return df