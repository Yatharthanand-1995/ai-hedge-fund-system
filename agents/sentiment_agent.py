"""
Sentiment Agent
Analyzes market sentiment through analyst ratings and other indicators
Enhanced with LLM-powered news sentiment analysis
"""

import yfinance as yf
import pandas as pd
from typing import Dict, Optional, List
import logging
import os
import requests
from datetime import datetime, timedelta

# LLM imports
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

logger = logging.getLogger(__name__)


class SentimentAgent:
    """
    Scores stocks based on market sentiment

    Enhanced Data sources:
    1. Analyst recommendations (60%)
    2. Target price vs current (15%)
    3. LLM-powered news sentiment (25%)

    Features:
    - News sentiment analysis using GPT/Claude
    - Advanced reasoning about market impact
    - Real-time news processing
    """

    def __init__(self, llm_provider='openai', enable_llm=True):
        self.name = "SentimentAgent"
        self.llm_provider = llm_provider
        self.enable_llm = enable_llm

        # Initialize LLM clients
        self.openai_client = None
        self.anthropic_client = None
        self.gemini_client = None

        if enable_llm:
            self._initialize_llm_clients()

        logger.info(f"{self.name} initialized with LLM={enable_llm}, provider={llm_provider}")

    def _initialize_llm_clients(self):
        """Initialize LLM clients with API keys"""
        try:
            # OpenAI setup
            if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
                self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                logger.info("OpenAI client initialized for sentiment analysis")

            # Anthropic setup
            if ANTHROPIC_AVAILABLE and os.getenv('ANTHROPIC_API_KEY'):
                self.anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
                logger.info("Anthropic client initialized for sentiment analysis")

            # Gemini setup
            if GEMINI_AVAILABLE and os.getenv('GEMINI_API_KEY'):
                genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
                self.gemini_client = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("Gemini client initialized for sentiment analysis")

        except Exception as e:
            logger.warning(f"Failed to initialize LLM clients: {e}")
            self.enable_llm = False

    def analyze(self, symbol: str, data: Optional = None, cached_data: Optional[Dict] = None) -> Dict:
        """
        Analyze sentiment and return score

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
                recommendations_df = cached_data.get('recommendations', pd.DataFrame())
                recommendations = self._parse_recommendations(recommendations_df)
            else:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                recommendations = self._get_recommendations(ticker)

            # Calculate scores
            analyst_score = self._score_analyst_ratings(recommendations)
            target_score = self._score_target_price(info)

            # Get LLM-powered news sentiment if available
            news_sentiment_score = 50.0  # Default neutral
            if self.enable_llm and (self.openai_client or self.anthropic_client or self.gemini_client):
                try:
                    news_sentiment_score = self._analyze_news_sentiment(symbol, info)
                except Exception as e:
                    logger.warning(f"News sentiment analysis failed for {symbol}: {e}")
                    news_sentiment_score = 50.0

            # Enhanced composite score with news sentiment
            if self.enable_llm:
                composite_score = (
                    0.60 * analyst_score +
                    0.15 * target_score +
                    0.25 * news_sentiment_score
                )
            else:
                # Fallback to original weighting
                composite_score = (
                    0.80 * analyst_score +
                    0.20 * target_score
                )

            # Confidence based on data availability
            confidence = self._calculate_confidence(recommendations, info)

            reasoning = self._build_reasoning(analyst_score, target_score, recommendations, info)

            return {
                'score': round(composite_score, 2),
                'confidence': round(confidence, 2),
                'metrics': {
                    'analyst_rating': analyst_score,
                    'target_price_upside': target_score,
                    'news_sentiment': news_sentiment_score if self.enable_llm else None,
                    'recommendations': recommendations,
                    'target_price': info.get('targetMeanPrice', 0),
                    'current_price': info.get('currentPrice', 0),
                },
                'reasoning': reasoning
            }

        except Exception as e:
            logger.error(f"Sentiment analysis failed for {symbol}: {e}")
            # Try basic sentiment analysis without LLM
            try:
                basic_info = yf.Ticker(symbol).info
                basic_recommendations = self._get_recommendations(yf.Ticker(symbol))

                # Calculate basic scores
                basic_analyst_score = self._score_analyst_ratings(basic_recommendations)
                basic_target_score = self._score_target_price(basic_info)

                # Simple weighted average without LLM
                basic_composite = (0.8 * basic_analyst_score + 0.2 * basic_target_score)
                basic_confidence = 0.3  # Low confidence for basic analysis

                return {
                    'score': round(basic_composite, 2),
                    'confidence': basic_confidence,
                    'metrics': {
                        'analyst_rating': basic_analyst_score,
                        'target_price_upside': basic_target_score,
                        'fallback_mode': True
                    },
                    'reasoning': f"Basic sentiment analysis (error: {str(e)[:50]})"
                }
            except:
                # Final fallback
                return {
                    'score': 50.0,
                    'confidence': 0.1,
                    'metrics': {'analysis_failed': True},
                    'reasoning': f"Sentiment analysis failed: {str(e)}"
                }

    def _parse_recommendations(self, recs: pd.DataFrame) -> Dict:
        """Parse recommendations DataFrame into counts"""
        counts = {
            'strongBuy': 0,
            'buy': 0,
            'hold': 0,
            'sell': 0,
            'strongSell': 0
        }

        if recs is None or recs.empty:
            return counts

        try:
            # Get most recent recommendations
            recent = recs.tail(20)

            for _, row in recent.iterrows():
                action = row.get('To Grade', '').lower()
                if 'strong buy' in action or 'outperform' in action:
                    counts['strongBuy'] += 1
                elif 'buy' in action:
                    counts['buy'] += 1
                elif 'sell' in action and 'strong' not in action:
                    counts['sell'] += 1
                elif 'strong sell' in action or 'underperform' in action:
                    counts['strongSell'] += 1
                else:
                    counts['hold'] += 1

        except Exception as e:
            logger.warning(f"Failed to parse recommendations: {e}")

        return counts

    def _get_recommendations(self, ticker) -> Dict:
        """Get analyst recommendations"""
        try:
            recs = ticker.recommendations
            if recs is not None and not recs.empty:
                # Get most recent recommendations
                recent = recs.tail(20)  # Last 20 recommendations

                counts = {
                    'strongBuy': 0,
                    'buy': 0,
                    'hold': 0,
                    'sell': 0,
                    'strongSell': 0
                }

                for _, row in recent.iterrows():
                    action = row.get('To Grade', '').lower()
                    if 'strong buy' in action or 'outperform' in action:
                        counts['strongBuy'] += 1
                    elif 'buy' in action:
                        counts['buy'] += 1
                    elif 'sell' in action and 'strong' not in action:
                        counts['sell'] += 1
                    elif 'strong sell' in action or 'underperform' in action:
                        counts['strongSell'] += 1
                    else:
                        counts['hold'] += 1

                return counts

        except Exception as e:
            logger.warning(f"Failed to get recommendations: {e}")

        return {'strongBuy': 0, 'buy': 0, 'hold': 0, 'sell': 0, 'strongSell': 0}

    def _score_analyst_ratings(self, recommendations: Dict) -> float:
        """Score based on analyst recommendations (0-100)"""

        total = sum(recommendations.values())
        if total == 0:
            return 50  # Neutral if no data

        # Weight different ratings
        weighted_score = (
            recommendations['strongBuy'] * 100 +
            recommendations['buy'] * 75 +
            recommendations['hold'] * 50 +
            recommendations['sell'] * 25 +
            recommendations['strongSell'] * 0
        )

        score = weighted_score / total if total > 0 else 50

        return min(max(score, 0), 100)

    def _score_target_price(self, info: Dict) -> float:
        """Score based on target price upside (0-100)"""

        target_price = info.get('targetMeanPrice', 0)
        current_price = info.get('currentPrice', 0)

        if target_price == 0 or current_price == 0:
            return 50  # Neutral if no data

        upside = (target_price - current_price) / current_price * 100

        # Score based on upside percentage
        if upside > 30:
            return 100
        elif upside > 20:
            return 90
        elif upside > 15:
            return 80
        elif upside > 10:
            return 70
        elif upside > 5:
            return 60
        elif upside > 0:
            return 55
        elif upside > -5:
            return 45
        elif upside > -10:
            return 35
        elif upside > -15:
            return 25
        else:
            return 10

    def _calculate_confidence(self, recommendations: Dict, info: Dict) -> float:
        """Calculate confidence based on data availability"""

        confidence = 0.0

        # Check if we have recommendations
        total_recs = sum(recommendations.values())
        if total_recs > 0:
            confidence += 0.6
            # More recommendations = higher confidence
            if total_recs >= 10:
                confidence += 0.2

        # Check if we have target price
        if info.get('targetMeanPrice', 0) > 0:
            confidence += 0.2

        return min(confidence, 1.0)

    def _build_reasoning(self, analyst_score: float, target_score: float,
                        recommendations: Dict, info: Dict) -> str:
        """Build human-readable reasoning"""

        reasons = []

        # Analyst sentiment
        total_recs = sum(recommendations.values())
        if total_recs > 0:
            buy_count = recommendations['strongBuy'] + recommendations['buy']
            sell_count = recommendations['sell'] + recommendations['strongSell']

            if buy_count > sell_count * 2:
                reasons.append("Strong analyst bullish consensus")
            elif buy_count > sell_count:
                reasons.append("Analysts lean bullish")
            elif sell_count > buy_count:
                reasons.append("Analysts lean bearish")
            else:
                reasons.append("Mixed analyst views")

        # Target price
        target = info.get('targetMeanPrice', 0)
        current = info.get('currentPrice', 0)
        if target > 0 and current > 0:
            upside = (target - current) / current * 100
            if upside > 15:
                reasons.append(f"significant upside to target ({upside:.1f}%)")
            elif upside > 5:
                reasons.append(f"moderate upside to target ({upside:.1f}%)")
            elif upside < -5:
                reasons.append(f"trading above target ({upside:.1f}%)")

        return "; ".join(reasons).capitalize() if reasons else "Limited sentiment data"

    def _analyze_news_sentiment(self, symbol: str, stock_info: Dict) -> float:
        """Analyze news sentiment using LLM"""
        try:
            # Get recent news from yfinance
            ticker = yf.Ticker(symbol)
            news = []

            try:
                news_data = ticker.news
                if news_data:
                    # Get last 5 recent news items
                    news = news_data[:5]
            except:
                logger.warning(f"Could not fetch news for {symbol}")

            # If no news available, fetch from basic search
            if not news:
                news = self._search_basic_news(symbol)

            if not news:
                logger.info(f"No news found for {symbol}, returning neutral sentiment")
                return 50.0

            # Analyze sentiment using LLM
            return self._llm_sentiment_analysis(symbol, news, stock_info)

        except Exception as e:
            logger.error(f"News sentiment analysis failed for {symbol}: {e}")
            return 50.0

    def _search_basic_news(self, symbol: str) -> List[Dict]:
        """Basic news search as fallback"""
        # This is a placeholder - in production you'd use a real news API
        # For now, we'll return empty to avoid external dependencies
        return []

    def _llm_sentiment_analysis(self, symbol: str, news: List[Dict], stock_info: Dict) -> float:
        """Use LLM to analyze news sentiment"""
        try:
            # Prepare news data for LLM
            news_summary = self._prepare_news_summary(symbol, news, stock_info)

            # Generate sentiment using preferred LLM
            if self.llm_provider == 'gemini' and self.gemini_client:
                return self._analyze_sentiment_gemini(news_summary)
            elif self.llm_provider == 'anthropic' and self.anthropic_client:
                return self._analyze_sentiment_anthropic(news_summary)
            elif self.llm_provider == 'openai' and self.openai_client:
                return self._analyze_sentiment_openai(news_summary)
            elif self.gemini_client:  # Fallback to Gemini
                return self._analyze_sentiment_gemini(news_summary)
            elif self.openai_client:  # Fallback to OpenAI
                return self._analyze_sentiment_openai(news_summary)
            elif self.anthropic_client:  # Fallback to Anthropic
                return self._analyze_sentiment_anthropic(news_summary)
            else:
                return 50.0

        except Exception as e:
            logger.error(f"LLM sentiment analysis failed: {e}")
            return 50.0

    def _prepare_news_summary(self, symbol: str, news: List[Dict], stock_info: Dict) -> str:
        """Prepare news summary for LLM analysis"""
        company_name = stock_info.get('shortName', symbol)

        news_text = f"Recent news analysis for {company_name} ({symbol}):\n\n"

        for i, article in enumerate(news[:5], 1):
            title = article.get('title', 'No title')
            summary = article.get('summary', article.get('description', 'No summary'))

            news_text += f"{i}. {title}\n"
            if summary:
                news_text += f"   Summary: {summary[:200]}...\n"
            news_text += "\n"

        return news_text

    def _analyze_sentiment_openai(self, news_summary: str) -> float:
        """Analyze sentiment using OpenAI"""
        try:
            prompt = f"""
Analyze the sentiment of the following news for investment purposes. Return a score from 0-100:
- 0-20: Very Bearish (strong negative impact on stock price)
- 21-40: Bearish (negative impact)
- 41-60: Neutral (minimal impact)
- 61-80: Bullish (positive impact)
- 81-100: Very Bullish (strong positive impact)

Consider:
1. Impact on company fundamentals
2. Market reaction potential
3. Short-term vs long-term implications
4. Industry/sector context

{news_summary}

Respond with just the numeric score (0-100) and a brief 1-sentence explanation.
"""

            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a financial analyst specializing in news sentiment analysis for stock investments."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.3
            )

            response_text = response.choices[0].message.content.strip()

            # Extract numeric score
            import re
            score_match = re.search(r'\b(\d{1,3})\b', response_text)
            if score_match:
                score = float(score_match.group(1))
                return max(0, min(100, score))

            return 50.0

        except Exception as e:
            logger.error(f"OpenAI sentiment analysis failed: {e}")
            return 50.0

    def _analyze_sentiment_anthropic(self, news_summary: str) -> float:
        """Analyze sentiment using Anthropic Claude"""
        try:
            prompt = f"""
Analyze the sentiment of the following news for investment purposes. Return a score from 0-100:
- 0-20: Very Bearish (strong negative impact on stock price)
- 21-40: Bearish (negative impact)
- 41-60: Neutral (minimal impact)
- 61-80: Bullish (positive impact)
- 81-100: Very Bullish (strong positive impact)

Consider:
1. Impact on company fundamentals
2. Market reaction potential
3. Short-term vs long-term implications
4. Industry/sector context

{news_summary}

Respond with just the numeric score (0-100) and a brief 1-sentence explanation.
"""

            response = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=100,
                temperature=0.3,
                system="You are a financial analyst specializing in news sentiment analysis for stock investments.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = response.content[0].text.strip()

            # Extract numeric score
            import re
            score_match = re.search(r'\b(\d{1,3})\b', response_text)
            if score_match:
                score = float(score_match.group(1))
                return max(0, min(100, score))

            return 50.0

        except Exception as e:
            logger.error(f"Anthropic sentiment analysis failed: {e}")
            return 50.0

    def _analyze_sentiment_gemini(self, news_summary: str) -> float:
        """Analyze sentiment using Google Gemini"""
        try:
            prompt = f"""
Analyze the sentiment of the following news for investment purposes. Return a score from 0-100:
- 0-20: Very Bearish (strong negative impact on stock price)
- 21-40: Bearish (negative impact)
- 41-60: Neutral (minimal impact)
- 61-80: Bullish (positive impact)
- 81-100: Very Bullish (strong positive impact)

Consider:
1. Impact on company fundamentals
2. Market reaction potential
3. Short-term vs long-term implications
4. Industry/sector context

{news_summary}

Respond with just the numeric score (0-100) and a brief 1-sentence explanation.
"""

            response = self.gemini_client.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=100,
                )
            )

            response_text = response.text.strip()

            # Extract numeric score
            import re
            score_match = re.search(r'\b(\d{1,3})\b', response_text)
            if score_match:
                score = float(score_match.group(1))
                return max(0, min(100, score))

            return 50.0

        except Exception as e:
            logger.error(f"Gemini sentiment analysis failed: {e}")
            return 50.0