"""
4-Agent system for the AI hedge fund
"""

from .fundamentals_agent import FundamentalsAgent
from .momentum_agent import MomentumAgent
from .quality_agent import QualityAgent
from .sentiment_agent import SentimentAgent

__all__ = [
    'FundamentalsAgent',
    'MomentumAgent',
    'QualityAgent',
    'SentimentAgent'
]