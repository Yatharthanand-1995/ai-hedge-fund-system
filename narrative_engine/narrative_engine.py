"""
Investment Narrative Engine
Generates human-readable investment thesis and reasoning based on agent analysis
Enhanced with LLM-powered sophisticated reasoning
"""

import yfinance as yf
from typing import Dict, List, Optional
import logging
from datetime import datetime
import os
import json

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


class InvestmentNarrativeEngine:
    """
    Converts quantitative agent analysis into human-readable investment narratives
    Enhanced with LLM-powered sophisticated reasoning
    """

    def __init__(self, llm_provider='openai', enable_llm=True):
        self.name = "InvestmentNarrativeEngine"
        self.llm_provider = llm_provider
        self.enable_llm = enable_llm

        # Initialize LLM clients
        self.openai_client = None
        self.anthropic_client = None
        self.gemini_client = None

        # Check if adaptive weights are enabled
        self.use_adaptive_weights = os.getenv('ENABLE_ADAPTIVE_WEIGHTS', 'false').lower() == 'true'
        self.market_regime_service = None

        if self.use_adaptive_weights:
            try:
                from core.market_regime_service import get_market_regime_service
                self.market_regime_service = get_market_regime_service()
                logger.info("✅ Adaptive agent weights ENABLED in narrative engine")
            except Exception as e:
                logger.warning(f"Failed to initialize market regime service: {e}")
                self.use_adaptive_weights = False

        if enable_llm:
            self._initialize_llm_clients()

        logger.info(f"{self.name} initialized with LLM={enable_llm}, provider={llm_provider}, adaptive_weights={self.use_adaptive_weights}")

    def _initialize_llm_clients(self):
        """Initialize LLM clients with API keys"""
        try:
            # OpenAI setup
            if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
                self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                logger.info("OpenAI client initialized")

            # Anthropic setup
            if ANTHROPIC_AVAILABLE and os.getenv('ANTHROPIC_API_KEY'):
                self.anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
                logger.info("Anthropic client initialized")

            # Gemini setup
            if GEMINI_AVAILABLE and os.getenv('GEMINI_API_KEY'):
                genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
                self.gemini_client = genai.GenerativeModel('gemini-2.0-flash')
                logger.info("Gemini client initialized")

        except Exception as e:
            logger.warning(f"Failed to initialize LLM clients: {e}")
            self.enable_llm = False

    def _get_current_weights(self) -> Dict[str, float]:
        """Get current agent weights (adaptive or static)"""
        if self.use_adaptive_weights and self.market_regime_service:
            try:
                return self.market_regime_service.get_adaptive_weights()
            except Exception as e:
                logger.warning(f"Failed to get adaptive weights, using static: {e}")
                # Fallback to static weights
                return {
                    'fundamentals': 0.4,
                    'momentum': 0.3,
                    'quality': 0.2,
                    'sentiment': 0.1
                }
        else:
            # Static weights (default)
            return {
                'fundamentals': 0.4,
                'momentum': 0.3,
                'quality': 0.2,
                'sentiment': 0.1
            }

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

            # Get adaptive or static weights
            weights = self._get_current_weights()
            market_regime_info = None

            overall_score = (
                fundamentals.get('score', 0) * weights['fundamentals'] +
                momentum.get('score', 0) * weights['momentum'] +
                quality.get('score', 0) * weights['quality'] +
                sentiment.get('score', 0) * weights['sentiment']
            )

            # Generate individual agent narratives (rule-based backup)
            agent_narratives = {
                'fundamentals': self._generate_fundamentals_narrative(fundamentals, symbol),
                'momentum': self._generate_momentum_narrative(momentum, symbol),
                'quality': self._generate_quality_narrative(quality, symbol),
                'sentiment': self._generate_sentiment_narrative(sentiment, symbol)
            }

            # Generate overall investment thesis - LLM enhanced if available
            if self.enable_llm and (self.openai_client or self.anthropic_client):
                investment_thesis = self._generate_llm_thesis(
                    symbol, overall_score, agent_results, agent_narratives, stock_info
                )
            else:
                investment_thesis = self._generate_overall_thesis(
                    symbol, overall_score, agent_narratives, stock_info
                )

            # Extract key strengths and risks
            strengths, risks = self._extract_strengths_and_risks(agent_results)

            # Determine recommendation
            recommendation = self._get_recommendation(overall_score)
            confidence_level = self._get_confidence_level(agent_results)

            # Get market regime info if adaptive weights are enabled
            if self.use_adaptive_weights and self.market_regime_service:
                try:
                    market_regime_info = self.market_regime_service.get_current_regime()
                except Exception as e:
                    logger.warning(f"Failed to get market regime: {e}")
                    market_regime_info = None

            result = {
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
                },
                'weights_used': weights
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
            logger.error(f"Error generating narrative for {symbol}: {e}")
            return self._generate_error_narrative(symbol, str(e))

    def _generate_llm_thesis(self, symbol: str, overall_score: float,
                           agent_results: Dict, agent_narratives: Dict,
                           stock_info: Optional[Dict]) -> str:
        """Generate sophisticated investment thesis using LLM"""
        try:
            # Prepare data for LLM
            company_name = symbol
            if stock_info:
                company_name = stock_info.get('shortName', symbol)

            # Create comprehensive data summary for LLM
            data_summary = self._prepare_llm_data(symbol, company_name, overall_score, agent_results, stock_info)

            # Generate thesis using preferred LLM
            if self.llm_provider == 'gemini' and self.gemini_client:
                return self._generate_gemini_thesis(data_summary)
            elif self.llm_provider == 'anthropic' and self.anthropic_client:
                return self._generate_anthropic_thesis(data_summary)
            elif self.llm_provider == 'openai' and self.openai_client:
                return self._generate_openai_thesis(data_summary)
            elif self.gemini_client:  # Fallback to Gemini
                return self._generate_gemini_thesis(data_summary)
            elif self.openai_client:  # Fallback to OpenAI
                return self._generate_openai_thesis(data_summary)
            elif self.anthropic_client:  # Fallback to Anthropic
                return self._generate_anthropic_thesis(data_summary)
            else:
                logger.warning("No LLM client available, falling back to rule-based")
                return self._generate_overall_thesis(symbol, overall_score, agent_narratives, stock_info)

        except Exception as e:
            logger.error(f"LLM thesis generation failed: {e}")
            return self._generate_overall_thesis(symbol, overall_score, agent_narratives, stock_info)

    def _prepare_llm_data(self, symbol: str, company_name: str, overall_score: float,
                         agent_results: Dict, stock_info: Optional[Dict]) -> Dict:
        """Prepare comprehensive data summary for LLM analysis"""

        # Extract key metrics from each agent
        fundamentals = agent_results.get('fundamentals', {})
        momentum = agent_results.get('momentum', {})
        quality = agent_results.get('quality', {})
        sentiment = agent_results.get('sentiment', {})

        data_summary = {
            'symbol': symbol,
            'company_name': company_name,
            'overall_score': overall_score,
            'agent_scores': {
                'fundamentals': fundamentals.get('score', 0),
                'momentum': momentum.get('score', 0),
                'quality': quality.get('score', 0),
                'sentiment': sentiment.get('score', 0)
            },
            'fundamentals_metrics': fundamentals.get('metrics', {}),
            'momentum_metrics': momentum.get('metrics', {}),
            'quality_metrics': quality.get('metrics', {}),
            'sentiment_metrics': sentiment.get('metrics', {}),
            'stock_info': stock_info or {}
        }

        return data_summary

    def _generate_openai_thesis(self, data_summary: Dict) -> str:
        """Generate investment thesis using OpenAI GPT"""
        try:
            prompt = self._create_investment_prompt(data_summary)

            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional hedge fund analyst with 15+ years of experience. Generate sophisticated, institutional-quality investment theses."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"OpenAI thesis generation failed: {e}")
            raise

    def _generate_anthropic_thesis(self, data_summary: Dict) -> str:
        """Generate investment thesis using Anthropic Claude"""
        try:
            prompt = self._create_investment_prompt(data_summary)

            response = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=800,
                temperature=0.7,
                system="You are a professional hedge fund analyst with 15+ years of experience. Generate sophisticated, institutional-quality investment theses.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return response.content[0].text.strip()

        except Exception as e:
            logger.error(f"Anthropic thesis generation failed: {e}")
            raise

    def _generate_gemini_thesis(self, data_summary: Dict) -> str:
        """Generate investment thesis using Google Gemini"""
        try:
            prompt = self._create_investment_prompt(data_summary)

            response = self.gemini_client.generate_content(
                f"You are a professional hedge fund analyst with 15+ years of experience. Generate sophisticated, institutional-quality investment theses.\n\n{prompt}",
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=800,
                )
            )

            return response.text.strip()

        except Exception as e:
            logger.error(f"Gemini thesis generation failed: {e}")
            raise

    def _create_investment_prompt(self, data: Dict) -> str:
        """Create detailed prompt for LLM investment thesis generation"""

        symbol = data['symbol']
        company_name = data['company_name']
        overall_score = data['overall_score']
        agent_scores = data['agent_scores']

        # Build detailed prompt with all available data
        prompt = f"""
Generate a comprehensive investment thesis for {company_name} ({symbol}) based on our 4-agent quantitative analysis.

OVERALL SCORE: {overall_score:.1f}/100

AGENT ANALYSIS BREAKDOWN:
• Fundamentals Agent (40% weight): {agent_scores['fundamentals']}/100
• Momentum Agent (30% weight): {agent_scores['momentum']}/100
• Quality Agent (20% weight): {agent_scores['quality']}/100
• Sentiment Agent (10% weight): {agent_scores['sentiment']}/100

DETAILED METRICS:
Fundamentals: {json.dumps(data['fundamentals_metrics'], indent=2)}
Momentum: {json.dumps(data['momentum_metrics'], indent=2)}
Quality: {json.dumps(data['quality_metrics'], indent=2)}
Sentiment: {json.dumps(data['sentiment_metrics'], indent=2)}

COMPANY DATA: {json.dumps(data['stock_info'], indent=2)}

Please provide a sophisticated investment thesis that includes:

1. EXECUTIVE SUMMARY (2-3 sentences): Key investment thesis and recommendation

2. QUANTITATIVE ASSESSMENT:
   - Analysis of the 4-agent scores and what they reveal
   - Key strengths and weaknesses identified by our models
   - Risk-adjusted return expectations

3. FUNDAMENTAL ANALYSIS:
   - Financial health and business model assessment
   - Competitive positioning and moats
   - Growth prospects and valuation

4. TECHNICAL & MOMENTUM FACTORS:
   - Price action and trend analysis
   - Market timing considerations
   - Entry/exit strategy implications

5. RISK ASSESSMENT:
   - Key downside risks and mitigation strategies
   - Market/sector/company-specific risks
   - Position sizing considerations

6. INVESTMENT RECOMMENDATION:
   - Clear BUY/HOLD/SELL recommendation
   - Target allocation and time horizon
   - Key catalysts to monitor

Write in a professional, analytical tone suitable for institutional investors. Use specific data points from the analysis to support your conclusions.
"""

        return prompt

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