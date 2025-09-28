"""
News Sentiment Module
Real-time news analysis for enhanced sentiment scoring
"""

from .news_fetcher import NewsFetcher
from .sentiment_analyzer import SentimentAnalyzer
from .news_cache import NewsCache

__all__ = [
    'NewsFetcher',
    'SentimentAnalyzer',
    'NewsCache'
]