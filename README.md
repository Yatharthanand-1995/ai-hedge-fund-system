# 🏦 4-Agent AI Hedge Fund System

**Professional-grade investment analysis platform with multi-agent intelligence and narrative generation**

## 🎯 System Overview

This is a sophisticated AI-powered hedge fund analysis system that employs **5 specialized agents** to provide comprehensive investment analysis with human-readable narratives. The system combines quantitative analysis with qualitative reasoning to generate professional investment theses.

### 🤖 4-Agent Analysis Framework

| Agent | Weight | Focus Area | Key Metrics |
|-------|--------|------------|-------------|
| **Fundamentals Agent** | 40% | Financial health, profitability, growth, valuation | ROE, P/E, Revenue Growth, Debt-to-Equity |
| **Momentum Agent** | 30% | Technical analysis and price trends | RSI, Moving Averages, Price Momentum |
| **Quality Agent** | 20% | Business characteristics and operational efficiency | Business Model Quality, Operational Metrics |
| **Sentiment Agent** | 10% | Market sentiment and analyst outlook | News Sentiment, Analyst Ratings |

### 💡 Investment Narrative Engine

The system generates comprehensive investment narratives that include:
- **Investment Thesis**: Detailed human-readable analysis
- **Key Strengths & Risks**: Bullet-pointed insights
- **Recommendation**: STRONG BUY/BUY/WEAK BUY/HOLD/WEAK SELL/SELL
- **Confidence Level**: HIGH/MEDIUM/LOW based on agent consensus
- **Position Sizing**: Recommended portfolio allocation

## 🌐 Live Demo

A live demonstration of the **Stock Analysis** feature is deployed on Vercel:

**[View Live Demo](https://ai-hedge-fund-stock-analysis-demo-iz5povweo.vercel.app)** 🚀

### Demo Features
- 📊 Real-time analysis of 50 elite S&P 100 stocks
- 🤖 5-agent AI scoring system in action
- 📈 Professional investment recommendations
- 🔍 Advanced filtering and sorting capabilities
- 💡 Detailed investment theses with strengths and risks

### Important Note
The demo requires the backend API to be running locally for live data. For the **full experience** with all features (Portfolio Manager, Backtesting, Paper Trading, etc.), follow the local installation guide below.

See [VERCEL_DEMO_README.md](./VERCEL_DEMO_README.md) for demo-specific documentation.

## 🚀 Quick Start

### Prerequisites

- Python 3.9+ (tested with Python 3.13)
- pip or conda for package management

### Installation

1. **Clone and navigate to the directory:**
```bash
cd /Users/yatharthanand/ai_hedge_fund_system
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the system test:**
```bash
python test_system.py
```

4. **Start the API server:**
```bash
python -m api.main
```

5. **Access the web interface:**
- **API Documentation**: http://localhost:8010/docs
- **Alternative Docs**: http://localhost:8010/redoc
- **Main Interface**: http://localhost:8010

## 📊 API Endpoints

### Investment Analysis
- `POST /analyze` - Complete 5-agent analysis with narrative
- `GET /analyze/{symbol}` - Quick analysis for single symbol
- `POST /analyze/batch` - Batch analysis for multiple stocks

### Portfolio Management
- `POST /portfolio/analyze` - Portfolio analysis and optimization
- `GET /portfolio/top-picks` - Top investment picks based on 5-agent analysis

### System Health
- `GET /health` - System health check and agent status

## 🏗️ System Architecture

```
ai_hedge_fund_system/
├── agents/                    # 4 Specialized Agents
│   ├── fundamentals_agent.py  # Financial analysis (40% weight)
│   ├── momentum_agent.py      # Technical analysis (30% weight)
│   ├── quality_agent.py       # Business quality (20% weight)
│   └── sentiment_agent.py     # Market sentiment (10% weight)
├── narrative_engine/          # Investment Thesis Generation
│   └── narrative_engine.py    # Converts analysis to human narrative
├── api/                       # Web API Interface
│   ├── main.py               # FastAPI application (NEW)
│   └── stock_picker_api.py   # Original stock picker API
├── core/                     # Core Business Logic
│   ├── portfolio_manager.py  # Portfolio optimization
│   ├── stock_scorer.py       # Multi-agent scoring
│   └── proven_signal_engine.py # Signal generation
├── data/                     # Data Providers
│   ├── enhanced_provider.py  # Enhanced Yahoo Finance provider
│   ├── realtime_provider.py  # Real-time data feeds
│   └── us_top_100_stocks.py  # US Top 50 Elite Stocks universe
├── risk/                     # Risk Management
│   ├── var_calculator.py     # Value at Risk calculation
│   ├── correlation.py        # Correlation analysis
│   └── drawdown_monitor.py   # Drawdown monitoring
├── ml/                       # Machine Learning
│   ├── regime_detector.py    # Market regime detection
│   ├── feature_engineering.py # Feature extraction
│   └── weight_optimizer.py   # Portfolio weight optimization
├── news/                     # News & Sentiment
│   ├── sentiment_analyzer.py # News sentiment analysis
│   ├── news_fetcher.py       # News data collection
│   └── news_cache.py         # News caching
└── config/                   # Configuration
    ├── signal_modes.py       # Signal configuration
    └── clean_signal_config.py # Clean signal settings
```

## 🧪 Example Usage

### Python API

```python
import requests

# Analyze a single stock
response = requests.post("http://localhost:8010/analyze",
                        json={"symbol": "AAPL"})
analysis = response.json()

print(f"Overall Score: {analysis['narrative']['overall_score']}/100")
print(f"Recommendation: {analysis['narrative']['recommendation']}")
print(f"Investment Thesis:\n{analysis['narrative']['investment_thesis']}")
```

### Test Results Example (AAPL)

```
Testing 4-Agent AI Hedge Fund System
==================================================

0. Fetching market data for AAPL...
   Market data fetched successfully

1. Testing Fundamentals Agent...
   Fundamentals Score: 45.0/100
   Confidence: 0.92

2. Testing Momentum Agent...
   Momentum Score: 50.0/100
   Confidence: 0.0

3. Testing Quality Agent...
   Quality Score: 70.0/100
   Confidence: 1.0

4. Testing Sentiment Agent...
   Sentiment Score: 49.0/100
   Confidence: 0.8

5. Testing Narrative Engine...

6. COMPLETE ANALYSIS RESULTS FOR AAPL:
============================================================
Overall Score: 51.9/100
Recommendation: HOLD
Confidence Level: MEDIUM

Agent Scores:
  Fundamentals: 45.0/100
  Momentum: 50.0/100
  Quality: 70.0/100
  Sentiment: 49.0/100

Key Strengths:
  • High-quality business characteristics

Key Risks:
  • Weak fundamental financial performance
  • Negative technical momentum
  • Negative market sentiment
```

## 🛡️ Risk Management Features

- **Value at Risk (VaR)** calculation
- **Correlation analysis** for portfolio diversification
- **Drawdown monitoring** for risk control
- **Position sizing** recommendations based on confidence levels
- **Portfolio optimization** with risk constraints

## 🔧 Configuration

### Environment Variables

```bash
# Optional API keys for enhanced features
export OPENAI_API_KEY="your_openai_key"        # For GPT-based sentiment
export ANTHROPIC_API_KEY="your_anthropic_key"  # For Claude-based sentiment
export NEWS_API_KEY="your_news_api_key"        # For news sentiment analysis
```

### Signal Modes

The system supports multiple configuration modes:
- `DEFAULT` - Balanced analysis
- `CONSERVATIVE` - Risk-averse approach
- `AGGRESSIVE` - Growth-focused analysis

## 📈 Performance Metrics

The system tracks comprehensive performance metrics:
- **Sharpe Ratio** optimization
- **Information Ratio** for active management
- **Maximum Drawdown** monitoring
- **Win Rate** analysis
- **Risk-Adjusted Returns**

## 🚀 Advanced Features

### Real-time Capabilities
- Live market data integration
- WebSocket support for streaming updates
- Intelligent caching (15-minute TTL)

### Machine Learning Integration
- Market regime detection using Hidden Markov Models
- Feature engineering for enhanced signals
- Portfolio weight optimization

### News & Sentiment Analysis
- Real-time news fetching and analysis
- Social media sentiment integration
- Analyst rating aggregation

## 📝 Development

### Running Tests

```bash
python test_system.py  # Test all 4 agents and narrative generation
python -m pytest tests/  # Run unit tests (if available)
```

### Code Quality

```bash
black .  # Code formatting
isort .  # Import organization
flake8 . # Linting
```

## 📦 Dependencies

Key dependencies include:
- **FastAPI** - Web API framework
- **yfinance** - Financial data provider
- **pandas/numpy** - Data processing
- **scikit-learn** - Machine learning
- **talib** - Technical analysis indicators

See `requirements.txt` for complete dependency list.

## 🤝 Contributing

1. Ensure all 4 agents are working correctly
2. Test narrative generation thoroughly
3. Maintain the weighted scoring system (40/30/20/10)
4. Follow the existing code structure and patterns

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Run the health check at `/health`
3. Review the test results from `test_system.py`

---

**Built with 🤖 AI-powered multi-agent intelligence for professional investment analysis**