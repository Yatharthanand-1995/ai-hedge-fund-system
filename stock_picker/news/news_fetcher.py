"""
News Fetcher
Retrieves financial news from various sources
"""

import requests
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
import time

logger = logging.getLogger(__name__)


class NewsFetcher:
    """
    Fetch financial news from multiple sources

    Supported sources:
    1. Alpha Vantage (free tier)
    2. Finnhub (free tier)
    3. Yahoo Finance (free)
    4. Mock/demo mode for testing
    """

    def __init__(self, api_key: Optional[str] = None, source: str = 'demo'):
        """
        Initialize news fetcher

        Args:
            api_key: API key for news service
            source: News source ('alpha_vantage', 'finnhub', 'yahoo', 'demo')
        """
        self.api_key = api_key
        self.source = source
        self.rate_limit = 1.0  # Seconds between requests
        self.last_request_time = 0

        self.base_urls = {
            'alpha_vantage': 'https://www.alphavantage.co/query',
            'finnhub': 'https://finnhub.io/api/v1',
            'yahoo': 'https://query1.finance.yahoo.com/v1/finance'
        }

        logger.info(f"NewsFetcher initialized (source: {source})")

    def _rate_limit_check(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.rate_limit:
            sleep_time = self.rate_limit - time_since_last
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def fetch_stock_news(self, symbol: str, days: int = 7) -> List[Dict]:
        """
        Fetch news for a specific stock

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            days: Number of days to look back

        Returns:
            List of news articles with metadata
        """
        try:
            if self.source == 'demo':
                return self._fetch_demo_news(symbol, days)
            elif self.source == 'alpha_vantage':
                return self._fetch_alpha_vantage_news(symbol, days)
            elif self.source == 'finnhub':
                return self._fetch_finnhub_news(symbol, days)
            elif self.source == 'yahoo':
                return self._fetch_yahoo_news(symbol, days)
            else:
                logger.error(f"Unknown news source: {self.source}")
                return []

        except Exception as e:
            logger.error(f"News fetching failed for {symbol}: {e}")
            return []

    def _fetch_demo_news(self, symbol: str, days: int) -> List[Dict]:
        """Generate demo news for testing"""
        demo_articles = [
            {
                'title': f'{symbol} Reports Strong Q3 Earnings',
                'description': f'{symbol} exceeded earnings expectations with strong revenue growth',
                'published_at': (datetime.now() - timedelta(days=1)).isoformat(),
                'source': 'Demo News',
                'url': 'https://example.com/news1',
                'sentiment_hint': 'positive'
            },
            {
                'title': f'{symbol} Faces Regulatory Challenges',
                'description': f'New regulations may impact {symbol} business model',
                'published_at': (datetime.now() - timedelta(days=3)).isoformat(),
                'source': 'Demo News',
                'url': 'https://example.com/news2',
                'sentiment_hint': 'negative'
            },
            {
                'title': f'{symbol} Announces New Product Launch',
                'description': f'{symbol} unveils innovative product for growing market',
                'published_at': (datetime.now() - timedelta(days=5)).isoformat(),
                'source': 'Demo News',
                'url': 'https://example.com/news3',
                'sentiment_hint': 'positive'
            }
        ]

        logger.info(f"Generated {len(demo_articles)} demo articles for {symbol}")
        return demo_articles

    def _fetch_alpha_vantage_news(self, symbol: str, days: int) -> List[Dict]:
        """Fetch news from Alpha Vantage"""
        if not self.api_key:
            logger.error("Alpha Vantage API key required")
            return []

        self._rate_limit_check()

        params = {
            'function': 'NEWS_SENTIMENT',
            'tickers': symbol,
            'apikey': self.api_key,
            'limit': 50
        }

        try:
            response = requests.get(self.base_urls['alpha_vantage'], params=params)
            response.raise_for_status()
            data = response.json()

            if 'feed' not in data:
                logger.warning(f"No news feed in Alpha Vantage response for {symbol}")
                return []

            articles = []
            cutoff_date = datetime.now() - timedelta(days=days)

            for item in data['feed']:
                pub_date = datetime.strptime(item['time_published'], '%Y%m%dT%H%M%S')

                if pub_date >= cutoff_date:
                    articles.append({
                        'title': item['title'],
                        'description': item['summary'],
                        'published_at': pub_date.isoformat(),
                        'source': item['source'],
                        'url': item['url'],
                        'sentiment_score': float(item.get('overall_sentiment_score', 0))
                    })

            logger.info(f"Fetched {len(articles)} Alpha Vantage articles for {symbol}")
            return articles

        except Exception as e:
            logger.error(f"Alpha Vantage news fetch failed: {e}")
            return []

    def _fetch_finnhub_news(self, symbol: str, days: int) -> List[Dict]:
        """Fetch news from Finnhub"""
        if not self.api_key:
            logger.error("Finnhub API key required")
            return []

        self._rate_limit_check()

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        params = {
            'symbol': symbol,
            'from': start_date.strftime('%Y-%m-%d'),
            'to': end_date.strftime('%Y-%m-%d'),
            'token': self.api_key
        }

        try:
            url = f"{self.base_urls['finnhub']}/company-news"
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            articles = []
            for item in data:
                articles.append({
                    'title': item['headline'],
                    'description': item['summary'],
                    'published_at': datetime.fromtimestamp(item['datetime']).isoformat(),
                    'source': item['source'],
                    'url': item['url'],
                    'image_url': item.get('image', '')
                })

            logger.info(f"Fetched {len(articles)} Finnhub articles for {symbol}")
            return articles

        except Exception as e:
            logger.error(f"Finnhub news fetch failed: {e}")
            return []

    def _fetch_yahoo_news(self, symbol: str, days: int) -> List[Dict]:
        """Fetch news from Yahoo Finance (free but limited)"""
        self._rate_limit_check()

        try:
            # Yahoo Finance doesn't have a direct news API, so we simulate
            # In practice, you'd use libraries like yfinance or scraping
            import yfinance as yf

            ticker = yf.Ticker(symbol)
            news = ticker.news

            articles = []
            cutoff_date = datetime.now() - timedelta(days=days)

            for item in news[:10]:  # Limit to 10 articles
                pub_date = datetime.fromtimestamp(item['providerPublishTime'])

                if pub_date >= cutoff_date:
                    articles.append({
                        'title': item['title'],
                        'description': item.get('summary', item['title']),
                        'published_at': pub_date.isoformat(),
                        'source': item['publisher'],
                        'url': item['link']
                    })

            logger.info(f"Fetched {len(articles)} Yahoo Finance articles for {symbol}")
            return articles

        except Exception as e:
            logger.error(f"Yahoo Finance news fetch failed: {e}")
            # Fallback to demo mode
            return self._fetch_demo_news(symbol, days)

    def fetch_market_news(self, days: int = 7) -> List[Dict]:
        """Fetch general market news"""
        try:
            # For market news, use broad market symbols/terms
            market_symbols = ['SPY', 'QQQ', 'market', 'economy']

            all_articles = []
            for symbol in market_symbols:
                articles = self.fetch_stock_news(symbol, days)
                all_articles.extend(articles)

            # Remove duplicates based on title
            unique_articles = []
            seen_titles = set()

            for article in all_articles:
                if article['title'] not in seen_titles:
                    unique_articles.append(article)
                    seen_titles.add(article['title'])

            logger.info(f"Fetched {len(unique_articles)} unique market news articles")
            return unique_articles

        except Exception as e:
            logger.error(f"Market news fetch failed: {e}")
            return []

    def get_news_summary(self, symbol: str, days: int = 7) -> Dict:
        """Get news summary with basic statistics"""
        try:
            articles = self.fetch_stock_news(symbol, days)

            if not articles:
                return {
                    'symbol': symbol,
                    'article_count': 0,
                    'days_covered': days,
                    'sources': [],
                    'latest_article': None
                }

            # Basic statistics
            sources = list(set(article['source'] for article in articles))
            latest_article = max(articles, key=lambda x: x['published_at'])

            # Sentiment statistics (if available)
            sentiment_scores = [
                article.get('sentiment_score', 0)
                for article in articles
                if 'sentiment_score' in article
            ]

            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else None

            return {
                'symbol': symbol,
                'article_count': len(articles),
                'days_covered': days,
                'sources': sources,
                'latest_article': {
                    'title': latest_article['title'],
                    'published_at': latest_article['published_at'],
                    'source': latest_article['source']
                },
                'avg_sentiment': avg_sentiment,
                'articles': articles[:5]  # Return top 5 articles
            }

        except Exception as e:
            logger.error(f"News summary generation failed: {e}")
            return {'error': str(e), 'symbol': symbol}