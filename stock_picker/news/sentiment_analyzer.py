"""
Sentiment Analyzer
Analyzes sentiment of financial news articles
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Union
import logging
import re

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Analyze sentiment of financial news

    Methods:
    1. TextBlob (basic sentiment)
    2. Financial keyword matching
    3. VADER sentiment (if available)
    4. Mock/demo mode for testing
    """

    def __init__(self, method: str = 'financial_keywords'):
        """
        Initialize sentiment analyzer

        Args:
            method: Analysis method
                - 'textblob': TextBlob library
                - 'vader': VADER sentiment
                - 'financial_keywords': Custom financial keyword matching
                - 'demo': Mock sentiment for testing
        """
        self.method = method
        self.available_methods = ['textblob', 'vader', 'financial_keywords', 'demo']

        if method not in self.available_methods:
            logger.warning(f"Unknown method {method}, using 'financial_keywords'")
            self.method = 'financial_keywords'

        # Financial sentiment keywords
        self.positive_keywords = {
            'earnings': ['beat', 'exceeded', 'strong', 'growth', 'profit', 'revenue', 'outperform'],
            'business': ['expansion', 'acquisition', 'partnership', 'innovation', 'launch', 'success'],
            'market': ['bullish', 'rally', 'surge', 'gain', 'rise', 'boost', 'upgrade'],
            'general': ['positive', 'optimistic', 'confident', 'promising', 'excellent', 'outstanding']
        }

        self.negative_keywords = {
            'earnings': ['missed', 'disappointing', 'decline', 'loss', 'weak', 'shortfall'],
            'business': ['layoffs', 'closure', 'bankruptcy', 'scandal', 'investigation', 'lawsuit'],
            'market': ['bearish', 'crash', 'plunge', 'fall', 'drop', 'downgrade', 'correction'],
            'general': ['negative', 'pessimistic', 'concerned', 'worried', 'challenging', 'difficult']
        }

        # Initialize chosen method
        self._initialize_method()

        logger.info(f"SentimentAnalyzer initialized (method: {self.method})")

    def _initialize_method(self):
        """Initialize the chosen sentiment analysis method"""
        try:
            if self.method == 'textblob':
                try:
                    from textblob import TextBlob
                    self.textblob = TextBlob
                    logger.info("TextBlob sentiment analyzer ready")
                except ImportError:
                    logger.warning("TextBlob not available, falling back to financial_keywords")
                    self.method = 'financial_keywords'

            elif self.method == 'vader':
                try:
                    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
                    self.vader = SentimentIntensityAnalyzer()
                    logger.info("VADER sentiment analyzer ready")
                except ImportError:
                    logger.warning("VADER not available, falling back to financial_keywords")
                    self.method = 'financial_keywords'

        except Exception as e:
            logger.error(f"Method initialization failed: {e}")
            self.method = 'financial_keywords'

    def analyze_text(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of a single text

        Args:
            text: Text to analyze

        Returns:
            Dict with sentiment scores
        """
        try:
            if self.method == 'demo':
                return self._analyze_demo(text)
            elif self.method == 'textblob':
                return self._analyze_textblob(text)
            elif self.method == 'vader':
                return self._analyze_vader(text)
            elif self.method == 'financial_keywords':
                return self._analyze_financial_keywords(text)
            else:
                return self._analyze_financial_keywords(text)

        except Exception as e:
            logger.error(f"Text sentiment analysis failed: {e}")
            return {'sentiment': 0.0, 'confidence': 0.0}

    def _analyze_demo(self, text: str) -> Dict[str, float]:
        """Generate demo sentiment based on text content"""
        text_lower = text.lower()

        # Simple keyword-based demo sentiment
        positive_words = ['strong', 'growth', 'beat', 'exceed', 'positive', 'gain']
        negative_words = ['weak', 'decline', 'miss', 'fall', 'negative', 'loss']

        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)

        if pos_count > neg_count:
            sentiment = 0.5 + min(0.4, pos_count * 0.1)
        elif neg_count > pos_count:
            sentiment = -0.5 - min(0.4, neg_count * 0.1)
        else:
            sentiment = np.random.normal(0, 0.1)  # Slight random variation

        confidence = min(1.0, (abs(pos_count - neg_count) + 1) * 0.2)

        return {
            'sentiment': float(np.clip(sentiment, -1.0, 1.0)),
            'confidence': float(confidence),
            'method': 'demo'
        }

    def _analyze_textblob(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using TextBlob"""
        try:
            blob = self.textblob(text)
            polarity = blob.sentiment.polarity  # -1 to 1
            subjectivity = blob.sentiment.subjectivity  # 0 to 1

            # Convert subjectivity to confidence (more objective = higher confidence)
            confidence = 1.0 - subjectivity

            return {
                'sentiment': float(polarity),
                'confidence': float(confidence),
                'subjectivity': float(subjectivity),
                'method': 'textblob'
            }

        except Exception as e:
            logger.error(f"TextBlob analysis failed: {e}")
            return {'sentiment': 0.0, 'confidence': 0.0}

    def _analyze_vader(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using VADER"""
        try:
            scores = self.vader.polarity_scores(text)

            # VADER returns pos, neu, neg, compound
            sentiment = scores['compound']  # -1 to 1
            confidence = max(scores['pos'], scores['neg'])  # Confidence based on strongest sentiment

            return {
                'sentiment': float(sentiment),
                'confidence': float(confidence),
                'positive': float(scores['pos']),
                'negative': float(scores['neg']),
                'neutral': float(scores['neu']),
                'method': 'vader'
            }

        except Exception as e:
            logger.error(f"VADER analysis failed: {e}")
            return {'sentiment': 0.0, 'confidence': 0.0}

    def _analyze_financial_keywords(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using financial keyword matching"""
        try:
            text_lower = text.lower()

            # Count keyword matches
            positive_matches = 0
            negative_matches = 0

            for category, keywords in self.positive_keywords.items():
                for keyword in keywords:
                    matches = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text_lower))
                    positive_matches += matches

            for category, keywords in self.negative_keywords.items():
                for keyword in keywords:
                    matches = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text_lower))
                    negative_matches += matches

            # Calculate sentiment score
            total_matches = positive_matches + negative_matches

            if total_matches == 0:
                sentiment = 0.0
                confidence = 0.0
            else:
                # Sentiment ranges from -1 to 1
                sentiment = (positive_matches - negative_matches) / total_matches
                # Confidence based on total matches (more matches = higher confidence)
                confidence = min(1.0, total_matches * 0.1)

            return {
                'sentiment': float(sentiment),
                'confidence': float(confidence),
                'positive_matches': positive_matches,
                'negative_matches': negative_matches,
                'total_matches': total_matches,
                'method': 'financial_keywords'
            }

        except Exception as e:
            logger.error(f"Financial keyword analysis failed: {e}")
            return {'sentiment': 0.0, 'confidence': 0.0}

    def analyze_articles(self, articles: List[Dict]) -> Dict:
        """
        Analyze sentiment for multiple articles

        Args:
            articles: List of article dictionaries

        Returns:
            Aggregated sentiment analysis
        """
        try:
            if not articles:
                return {
                    'overall_sentiment': 0.0,
                    'confidence': 0.0,
                    'article_count': 0,
                    'positive_articles': 0,
                    'negative_articles': 0,
                    'neutral_articles': 0
                }

            sentiments = []
            confidences = []
            article_sentiments = []

            for article in articles:
                # Analyze title and description together
                text = article.get('title', '') + ' ' + article.get('description', '')

                if text.strip():
                    analysis = self.analyze_text(text)
                    sentiment_score = analysis.get('sentiment', 0.0)
                    confidence = analysis.get('confidence', 0.0)

                    sentiments.append(sentiment_score)
                    confidences.append(confidence)

                    article_sentiments.append({
                        'title': article.get('title', ''),
                        'sentiment': sentiment_score,
                        'confidence': confidence,
                        'published_at': article.get('published_at', ''),
                        'source': article.get('source', '')
                    })

            if not sentiments:
                return {
                    'overall_sentiment': 0.0,
                    'confidence': 0.0,
                    'article_count': 0
                }

            # Calculate weighted average (weight by confidence)
            weights = np.array(confidences)
            weights = weights / weights.sum() if weights.sum() > 0 else np.ones_like(weights) / len(weights)

            overall_sentiment = np.average(sentiments, weights=weights)
            overall_confidence = np.mean(confidences)

            # Count sentiment categories
            positive_articles = sum(1 for s in sentiments if s > 0.1)
            negative_articles = sum(1 for s in sentiments if s < -0.1)
            neutral_articles = len(sentiments) - positive_articles - negative_articles

            return {
                'overall_sentiment': float(overall_sentiment),
                'confidence': float(overall_confidence),
                'article_count': len(articles),
                'analyzed_count': len(sentiments),
                'positive_articles': positive_articles,
                'negative_articles': negative_articles,
                'neutral_articles': neutral_articles,
                'sentiment_distribution': {
                    'mean': float(np.mean(sentiments)),
                    'std': float(np.std(sentiments)),
                    'min': float(np.min(sentiments)),
                    'max': float(np.max(sentiments))
                },
                'article_details': article_sentiments[:10]  # Top 10 articles
            }

        except Exception as e:
            logger.error(f"Multi-article analysis failed: {e}")
            return {'error': str(e), 'article_count': len(articles) if articles else 0}

    def get_sentiment_signal(self, overall_sentiment: float,
                           confidence: float,
                           article_count: int) -> Dict:
        """
        Convert sentiment analysis to trading signal

        Args:
            overall_sentiment: Overall sentiment score (-1 to 1)
            confidence: Confidence in sentiment (0 to 1)
            article_count: Number of articles analyzed

        Returns:
            Trading signal interpretation
        """
        try:
            # Base signal strength on sentiment, confidence, and article count
            signal_strength = abs(overall_sentiment) * confidence

            # Adjust for article count (more articles = more reliable)
            article_factor = min(1.0, article_count / 10.0)  # Full weight at 10+ articles
            adjusted_strength = signal_strength * article_factor

            # Determine signal direction and strength
            if overall_sentiment > 0.2 and adjusted_strength > 0.3:
                signal = 'STRONG_BUY'
                signal_score = min(1.0, adjusted_strength * 2)
            elif overall_sentiment > 0.05 and adjusted_strength > 0.15:
                signal = 'BUY'
                signal_score = adjusted_strength
            elif overall_sentiment < -0.2 and adjusted_strength > 0.3:
                signal = 'STRONG_SELL'
                signal_score = -min(1.0, adjusted_strength * 2)
            elif overall_sentiment < -0.05 and adjusted_strength > 0.15:
                signal = 'SELL'
                signal_score = -adjusted_strength
            else:
                signal = 'NEUTRAL'
                signal_score = 0.0

            return {
                'signal': signal,
                'signal_score': float(signal_score),
                'strength': float(adjusted_strength),
                'direction': 'POSITIVE' if overall_sentiment > 0 else 'NEGATIVE' if overall_sentiment < 0 else 'NEUTRAL',
                'confidence': float(confidence),
                'article_count': article_count,
                'reliability': 'HIGH' if article_count >= 5 and confidence > 0.5 else 'MEDIUM' if article_count >= 3 else 'LOW'
            }

        except Exception as e:
            logger.error(f"Signal generation failed: {e}")
            return {
                'signal': 'NEUTRAL',
                'signal_score': 0.0,
                'error': str(e)
            }