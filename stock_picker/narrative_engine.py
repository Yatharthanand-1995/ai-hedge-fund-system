"""
Investment Narrative Engine
Generates human-readable investment thesis and reasoning based on agent analysis
"""

import yfinance as yf
from typing import Dict, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class InvestmentNarrativeEngine:
    """
    Converts quantitative agent analysis into human-readable investment narratives
    """

    def __init__(self):
        self.name = "InvestmentNarrativeEngine"
        logger.info(f"{self.name} initialized")

    def generate_comprehensive_thesis(self, symbol: str, agent_results: Dict,
                                    stock_info: Optional[Dict] = None) -> Dict:
        """
        Generate comprehensive investment thesis from all agent results

        Args:
            symbol: Stock symbol
            agent_results: Results from all 4 agents
            stock_info: Basic stock information

        Returns:
            {
                'symbol': str,
                'investment_thesis': str,
                'key_strengths': List[str],
                'key_risks': List[str],
                'recommendation': str,
                'confidence_level': str,
                'agent_narratives': Dict,
                'overall_score': float
            }
        """

        try:
            # Extract composite score and recommendation
            fundamentals = agent_results.get('fundamentals', {})
            momentum = agent_results.get('momentum', {})
            quality = agent_results.get('quality', {})
            sentiment = agent_results.get('sentiment', {})

            overall_score = (
                fundamentals.get('score', 0) * 0.4 +
                momentum.get('score', 0) * 0.3 +
                quality.get('score', 0) * 0.2 +
                sentiment.get('score', 0) * 0.1
            )

            # Generate individual agent narratives
            agent_narratives = {
                'fundamentals': self._generate_fundamentals_narrative(fundamentals, symbol),
                'momentum': self._generate_momentum_narrative(momentum, symbol),
                'quality': self._generate_quality_narrative(quality, symbol),
                'sentiment': self._generate_sentiment_narrative(sentiment, symbol)
            }

            # Generate overall investment thesis
            investment_thesis = self._generate_overall_thesis(
                symbol, overall_score, agent_narratives, stock_info
            )

            # Extract key strengths and risks
            strengths, risks = self._extract_strengths_and_risks(agent_results)

            # Determine recommendation
            recommendation = self._get_recommendation(overall_score)
            confidence_level = self._get_confidence_level(agent_results)

            return {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'investment_thesis': investment_thesis,
                'key_strengths': strengths,
                'key_risks': risks,
                'recommendation': recommendation,
                'confidence_level': confidence_level,
                'agent_narratives': agent_narratives,
                'overall_score': round(overall_score, 2),
                'agent_scores': {
                    'fundamentals': fundamentals.get('score', 0),
                    'momentum': momentum.get('score', 0),
                    'quality': quality.get('score', 0),
                    'sentiment': sentiment.get('score', 0)
                }
            }

        except Exception as e:
            logger.error(f"Error generating narrative for {symbol}: {e}")
            return self._generate_error_narrative(symbol, str(e))

    def _generate_fundamentals_narrative(self, fundamentals: Dict, symbol: str) -> str:
        """Generate narrative for fundamentals analysis"""
        if not fundamentals:
            return f"Fundamental analysis for {symbol} is not available."

        score = fundamentals.get('score', 0)
        metrics = fundamentals.get('metrics', {})

        if score >= 70:
            strength = "excellent"
        elif score >= 60:
            strength = "strong"
        elif score >= 40:
            strength = "moderate"
        else:
            strength = "weak"

        narrative = f"Our fundamental analysis reveals {strength} financial health for {symbol} (Score: {score}/100). "

        # Add specific metrics commentary
        if metrics.get('roe', 0) > 15:
            narrative += f"The company demonstrates exceptional profitability with ROE of {metrics.get('roe', 0):.1f}%. "
        elif metrics.get('roe', 0) > 10:
            narrative += f"The company shows solid profitability with ROE of {metrics.get('roe', 0):.1f}%. "

        if metrics.get('pe_ratio', 0) > 0:
            pe = metrics.get('pe_ratio', 0)
            if pe < 15:
                narrative += f"Trading at an attractive valuation with P/E of {pe:.1f}. "
            elif pe < 25:
                narrative += f"Reasonably valued with P/E of {pe:.1f}. "
            else:
                narrative += f"Trading at a premium valuation with P/E of {pe:.1f}. "

        return narrative.strip()

    def _generate_momentum_narrative(self, momentum: Dict, symbol: str) -> str:
        """Generate narrative for momentum analysis"""
        if not momentum:
            return f"Momentum analysis for {symbol} is not available."

        score = momentum.get('score', 0)
        metrics = momentum.get('metrics', {})

        if score >= 70:
            trend = "strong bullish momentum"
        elif score >= 60:
            trend = "positive momentum"
        elif score >= 40:
            trend = "neutral momentum"
        else:
            trend = "bearish momentum"

        narrative = f"Technical analysis indicates {trend} for {symbol} (Score: {score}/100). "

        # Add performance metrics
        three_month = metrics.get('3m_return', 0)
        six_month = metrics.get('6m_return', 0)

        if three_month > 10:
            narrative += f"The stock has shown strong short-term performance with {three_month:.1f}% gains over 3 months. "
        elif three_month > 0:
            narrative += f"Modest short-term gains of {three_month:.1f}% over 3 months. "
        else:
            narrative += f"Recent weakness with {three_month:.1f}% decline over 3 months. "

        return narrative.strip()

    def _generate_quality_narrative(self, quality: Dict, symbol: str) -> str:
        """Generate narrative for quality analysis"""
        if not quality:
            return f"Quality analysis for {symbol} is not available."

        score = quality.get('score', 0)

        if score >= 70:
            quality_level = "high-quality"
        elif score >= 60:
            quality_level = "good quality"
        elif score >= 40:
            quality_level = "average quality"
        else:
            quality_level = "below-average quality"

        narrative = f"Our quality assessment classifies {symbol} as a {quality_level} company (Score: {score}/100). "

        # Add quality-specific insights
        if score >= 60:
            narrative += "The company demonstrates consistent business fundamentals and operational efficiency. "
        else:
            narrative += "Some concerns exist regarding business consistency and operational metrics. "

        return narrative.strip()

    def _generate_sentiment_narrative(self, sentiment: Dict, symbol: str) -> str:
        """Generate narrative for sentiment analysis"""
        if not sentiment:
            return f"Sentiment analysis for {symbol} is not available."

        score = sentiment.get('score', 0)

        if score >= 70:
            market_sentiment = "very positive"
        elif score >= 60:
            market_sentiment = "positive"
        elif score >= 40:
            market_sentiment = "neutral"
        else:
            market_sentiment = "negative"

        narrative = f"Market sentiment analysis shows {market_sentiment} outlook for {symbol} (Score: {score}/100). "

        # Add sentiment context
        if score >= 60:
            narrative += "Analyst expectations and market indicators suggest favorable near-term prospects. "
        else:
            narrative += "Mixed signals from market participants and analyst sentiment. "

        return narrative.strip()

    def _generate_overall_thesis(self, symbol: str, overall_score: float,
                               agent_narratives: Dict, stock_info: Optional[Dict]) -> str:
        """Generate comprehensive investment thesis"""

        company_name = symbol
        if stock_info:
            company_name = stock_info.get('shortName', symbol)

        if overall_score >= 70:
            thesis_tone = "compelling investment opportunity"
            outlook = "strong potential for value creation"
        elif overall_score >= 60:
            thesis_tone = "attractive investment consideration"
            outlook = "reasonable upside potential"
        elif overall_score >= 40:
            thesis_tone = "neutral investment proposition"
            outlook = "balanced risk-reward profile"
        else:
            thesis_tone = "challenging investment case"
            outlook = "significant risks outweigh potential rewards"

        thesis = f"""
Investment Thesis for {company_name} ({symbol}):

Our comprehensive multi-agent analysis identifies {company_name} as a {thesis_tone} with an overall score of {overall_score:.1f}/100.

{agent_narratives.get('fundamentals', '')}

{agent_narratives.get('momentum', '')}

{agent_narratives.get('quality', '')}

{agent_narratives.get('sentiment', '')}

Overall Assessment: Based on our quantitative analysis across fundamental, technical, quality, and sentiment factors, {company_name} presents {outlook}. The convergence of our analytical frameworks suggests this assessment reflects current market conditions and company-specific factors.
        """.strip()

        return thesis

    def _extract_strengths_and_risks(self, agent_results: Dict) -> tuple:
        """Extract key strengths and risks from agent analysis"""
        strengths = []
        risks = []

        # Fundamentals strengths/risks
        fund_score = agent_results.get('fundamentals', {}).get('score', 0)
        if fund_score >= 60:
            strengths.append("Strong fundamental financial metrics")
        else:
            risks.append("Weak fundamental financial performance")

        # Momentum strengths/risks
        momentum_score = agent_results.get('momentum', {}).get('score', 0)
        if momentum_score >= 60:
            strengths.append("Positive technical momentum and price trends")
        else:
            risks.append("Negative technical momentum")

        # Quality strengths/risks
        quality_score = agent_results.get('quality', {}).get('score', 0)
        if quality_score >= 60:
            strengths.append("High-quality business characteristics")
        else:
            risks.append("Business quality concerns")

        # Sentiment strengths/risks
        sentiment_score = agent_results.get('sentiment', {}).get('score', 0)
        if sentiment_score >= 60:
            strengths.append("Positive market sentiment and analyst outlook")
        else:
            risks.append("Negative market sentiment")

        return strengths, risks

    def _get_recommendation(self, overall_score: float) -> str:
        """Get investment recommendation based on overall score"""
        if overall_score >= 75:
            return "STRONG BUY"
        elif overall_score >= 65:
            return "BUY"
        elif overall_score >= 55:
            return "WEAK BUY"
        elif overall_score >= 45:
            return "HOLD"
        elif overall_score >= 35:
            return "WEAK SELL"
        else:
            return "SELL"

    def _get_confidence_level(self, agent_results: Dict) -> str:
        """Calculate confidence level based on agent consensus"""
        scores = [
            agent_results.get('fundamentals', {}).get('score', 0),
            agent_results.get('momentum', {}).get('score', 0),
            agent_results.get('quality', {}).get('score', 0),
            agent_results.get('sentiment', {}).get('score', 0)
        ]

        if not scores:
            return "LOW"

        # Calculate standard deviation to measure consensus
        import statistics
        std_dev = statistics.stdev(scores) if len(scores) > 1 else 0

        if std_dev < 10:
            return "HIGH"
        elif std_dev < 20:
            return "MEDIUM"
        else:
            return "LOW"

    def _generate_error_narrative(self, symbol: str, error: str) -> Dict:
        """Generate error narrative when analysis fails"""
        return {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'investment_thesis': f"Unable to generate investment thesis for {symbol} due to analysis error: {error}",
            'key_strengths': [],
            'key_risks': ["Insufficient data for analysis"],
            'recommendation': "NO RATING",
            'confidence_level': "LOW",
            'agent_narratives': {},
            'overall_score': 0,
            'error': error
        }