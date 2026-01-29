# 🏦 5-Agent AI Hedge Fund System

**Professional-grade investment analysis platform with multi-agent intelligence and narrative generation**

## 🎯 System Overview

This is a sophisticated AI-powered hedge fund analysis system that employs **5 specialized agents** to provide comprehensive investment analysis with human-readable narratives. The system combines quantitative analysis with qualitative reasoning to generate professional investment theses.

### 🤖 5-Agent Analysis Framework

| Agent | Weight | Focus Area | Key Metrics |
|-------|--------|------------|-------------|
| **Fundamentals Agent** | 36% | Financial health, profitability, growth, valuation | ROE, P/E, Revenue Growth, Debt-to-Equity |
| **Momentum Agent** | 27% | Technical analysis and price trends | RSI, Moving Averages, Price Momentum |
| **Quality Agent** | 18% | Business characteristics and operational efficiency | Business Model Quality, Operational Metrics |
| **Sentiment Agent** | 9% | Market sentiment and analyst outlook | News Sentiment, Analyst Ratings |
| **Institutional Flow Agent** | 10% | "Smart money" tracking and institutional activity | OBV, MFI, Volume Trends, VWAP Position |

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
├── agents/                    # 5 Specialized Agents
│   ├── fundamentals_agent.py  # Financial analysis (36% weight)
│   ├── momentum_agent.py      # Technical analysis (27% weight)
│   ├── quality_agent.py       # Business quality (18% weight)
│   ├── sentiment_agent.py     # Market sentiment (9% weight)
│   └── institutional_flow_agent.py  # Smart money tracking (10% weight)
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

### Automated Trading System
- **Immediate Execution (Default)**: Auto-buy executes immediately when STRONG BUY signals are detected
- **Batch Execution (Optional)**: Queue opportunities for 4 PM ET market close execution (for real capital)
- **Smart Validation**: Opportunities are validated before execution to ensure signal quality
- **Risk Management**: Automatic sector diversification and position sizing based on scores
- **Visibility**: Real-time status available via API endpoint `/portfolio/paper/auto-buy/queue`

**Execution Modes** (configurable in `data/auto_buy_config.json`):
- **`immediate`** (default): Execute immediately on signal detection
  - Best for paper trading and learning
  - Captures opportunities in real-time
  - No missed gains from waiting
- **`batch_4pm`**: Queue for 4 PM batch execution
  - Best for real capital with final human review
  - Market close pricing for predictable fills
  - Aggregate order optimization

## 📝 Development

### Running Tests

```bash
python test_system.py  # Test all 5 agents and narrative generation
python -m pytest tests/  # Run organized test suite
pytest tests/unit -v  # Run unit tests only
pytest tests/integration -v  # Run integration tests
pytest tests/system -v  # Run system tests
```

### Code Quality

```bash
black .  # Code formatting
isort .  # Import organization
flake8 . # Linting
```

## 📦 Dependencies

### Core Dependencies (requirements.txt)
- **FastAPI** - Web API framework
- **yfinance** - Financial data provider
- **pandas/numpy** - Data processing
- **scikit-learn** - Machine learning
- **talib** - Technical analysis indicators
- **LLM providers** - OpenAI, Anthropic, or Google Gemini (optional)

### Optional Dependencies (requirements-optional.txt)
Heavy dependencies for advanced features (~1GB):
- **PyTorch** - Advanced ML models
- **Redis** - Distributed caching
- **PostgreSQL** - Database support
- **MLflow/TensorBoard** - ML experiment tracking

**Installation:**
```bash
# Core system (required)
pip install -r requirements.txt

# Optional features (as needed)
pip install -r requirements-optional.txt
```

## 📁 Project Organization (Updated January 2026)

The codebase has been professionally organized into a clean, maintainable structure:

### Documentation Structure
```
docs/
├── README.md              # Comprehensive navigation index
├── architecture/          # System design (4 files)
├── development/           # Implementation & fixes (10 files)
├── operations/            # Deployment & monitoring (5 files)
├── features/              # Feature documentation (3 files)
├── archive_docs/          # Historical docs (3 files)
└── reports/               # Phase completion reports (6 files)
```

### Data Organization
```
data/
├── config/                # Configuration files (tracked by git)
│   ├── auto_buy_config.json
│   ├── auto_sell_config.json
│   └── monitoring_config.json
└── runtime/               # Runtime data (gitignored)
    ├── paper_portfolio.json
    ├── buy_queue.json
    └── execution logs
```

**Benefits**:
- ✅ Clear separation of configuration vs runtime data
- ✅ Configuration files version-controlled
- ✅ Documentation organized by category
- ✅ Professional root directory (only essential files)
- ✅ Easy to navigate and maintain

See [docs/README.md](docs/README.md) for complete documentation navigation.

## 🤝 Contributing

1. Ensure all 5 agents are working correctly
2. Test narrative generation thoroughly
3. Maintain the weighted scoring system (36/27/18/9/10)
4. Follow the organized test structure in `/tests/`
5. Update documentation for any new features
6. Follow the existing code structure and patterns
7. Configuration files go in `data/config/` (tracked by git)
8. Runtime data goes in `data/runtime/` (gitignored)

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Run the health check at `/health`
3. Review the test results from `test_system.py`

---

**Built with 🤖 AI-powered multi-agent intelligence for professional investment analysis**