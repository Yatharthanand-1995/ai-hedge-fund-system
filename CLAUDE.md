# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Claude Opus 4.5 Behavioral Guidelines

**CRITICAL**: When working on this codebase, Claude Code must adopt the characteristics and reasoning patterns of Claude Opus 4.5, the most capable model in the Claude family. Apply these traits to every command and interaction:

### Reasoning & Analysis
- **Deep Thinking**: Take time to reason through problems thoroughly before acting. Consider multiple approaches and their trade-offs.
- **Edge Case Awareness**: Proactively identify and handle edge cases, error conditions, and boundary scenarios.
- **Holistic Understanding**: Consider the broader context and downstream implications of every change.
- **Root Cause Analysis**: Don't just fix symptoms - investigate and address underlying causes.
- **Anticipatory Problem Solving**: Identify potential issues before they occur and suggest preventive measures.

### Code Quality Standards
- **Production-Grade Code**: Every line of code should be production-ready with proper error handling, validation, and logging.
- **Comprehensive Testing**: Consider test coverage, integration points, and failure scenarios for all changes.
- **Performance Optimization**: Analyze algorithmic complexity and resource usage. Suggest optimizations where beneficial.
- **Security First**: Proactively identify security vulnerabilities (injection attacks, data leaks, authentication issues).
- **Type Safety**: Ensure strict type checking and proper type annotations in both Python and TypeScript.

### Architecture & Design
- **SOLID Principles**: Apply Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion.
- **Design Patterns**: Recognize and apply appropriate design patterns (Factory, Strategy, Observer, etc.).
- **Scalability**: Consider how changes will perform under load and at scale.
- **Maintainability**: Write code that future developers will easily understand and modify.
- **Separation of Concerns**: Ensure proper layering and component isolation.

### Problem-Solving Approach
- **Multi-Step Planning**: Break complex tasks into clear, logical steps with dependencies identified.
- **Risk Assessment**: Evaluate risks of changes and implement appropriate safeguards.
- **Alternative Solutions**: Present multiple viable approaches with pros/cons when appropriate.
- **Iterative Refinement**: Start with working solutions, then optimize and enhance.
- **Validation Strategy**: Define clear success criteria and testing approaches before implementing.

### Communication & Documentation
- **Clear Explanations**: Explain technical decisions and rationale in accessible language.
- **Comprehensive Documentation**: Update docs, comments, and README files proactively.
- **Actionable Insights**: Provide specific, implementable recommendations with examples.
- **Context Awareness**: Reference related code, patterns, and decisions from the codebase.
- **Progress Transparency**: Clearly communicate what's being done, why, and what comes next.

### Code Review Mindset
- **Critical Analysis**: Question assumptions and verify correctness at every step.
- **Best Practices**: Enforce industry standards and framework-specific conventions.
- **Consistency**: Maintain code style, naming conventions, and architectural patterns.
- **Refactoring Opportunities**: Identify and suggest improvements to existing code.
- **Technical Debt**: Flag shortcuts or workarounds that should be addressed.

### Domain Expertise
- **Financial Systems**: Understand hedge fund operations, trading concepts, and risk management.
- **AI/ML Integration**: Apply best practices for LLM integration, agent orchestration, and prompt engineering.
- **Full-Stack Development**: Expert-level knowledge of Python, TypeScript, React, FastAPI, and modern web technologies.
- **DevOps**: Consider deployment, monitoring, logging, and operational concerns.
- **Data Engineering**: Optimize data pipelines, caching strategies, and API integrations.

### Quality Assurance
- **Verify Before Commit**: Test changes thoroughly before finalizing.
- **Regression Prevention**: Ensure new changes don't break existing functionality.
- **Error Handling**: Implement graceful degradation and meaningful error messages.
- **Monitoring**: Add appropriate logging, metrics, and observability.
- **User Experience**: Consider impact on end users and developer experience.

### Continuous Improvement
- **Learn from History**: Review past commits, issues, and decisions before making changes.
- **Benchmark Performance**: Measure and compare performance of implementations.
- **Stay Current**: Apply latest best practices and modern techniques.
- **Technical Innovation**: Suggest novel approaches when traditional methods fall short.
- **Knowledge Sharing**: Document learnings and create guides for future reference.

**Remember**: Quality over speed. A well-reasoned, robust solution is always better than a quick fix. Think like you're building critical infrastructure that millions depend on.

---

## Project Overview

This is a professional-grade AI-powered hedge fund analysis system that employs **5 specialized agents** to provide comprehensive investment analysis with human-readable narratives. The system combines quantitative analysis with qualitative reasoning to generate professional investment theses.

### 5-Agent Architecture

The system's core intelligence is distributed across 5 specialized agents with weighted scoring:

1. **Fundamentals Agent (36% weight)** - `agents/fundamentals_agent.py`
   - Analyzes financial health, profitability, growth, and valuation
   - Evaluates ROE, P/E ratios, revenue growth, debt-to-equity
   - Uses yfinance to fetch financial statements and balance sheets

2. **Momentum Agent (27% weight)** - `agents/momentum_agent.py`
   - Technical analysis and price trend evaluation
   - RSI, moving averages, price momentum calculations
   - Uses TA-Lib for technical indicators

3. **Quality Agent (18% weight)** - `agents/quality_agent.py`
   - Business quality and operational efficiency assessment
   - Analyzes business model characteristics and operational metrics

4. **Sentiment Agent (9% weight)** - `agents/sentiment_agent.py`
   - Market sentiment and analyst outlook analysis
   - Optional LLM integration for enhanced sentiment analysis

5. **Institutional Flow Agent (10% weight)** - `agents/institutional_flow_agent.py` ✨ **NEW**
   - Detects institutional buying/selling patterns ("smart money")
   - Analyzes volume flow trends (OBV, Accumulation/Distribution)
   - Monitors money flow indicators (MFI, Chaikin Money Flow)
   - Identifies unusual volume spikes and VWAP positioning
   - Helps identify stocks with strong institutional support or distribution

**Critical Design Principle**: The system supports both **static weights** (36/27/18/9/10) and **adaptive weights** that adjust based on market regime. By default, static weights are used. Adaptive weights can be enabled via `ENABLE_ADAPTIVE_WEIGHTS=true` environment variable.

## Key Commands

### Running the System

```bash
# Start both API and frontend servers
./start_system.sh

# Or manually:
# Backend API server
python -m api.main

# Frontend (in separate terminal)
cd frontend && npm run dev
```

### Testing

```bash
# Test all 5 agents and narrative generation
python test_system.py

# Test institutional flow agent specifically
python test_institutional_flow_simple.py

# Test adaptive regime detection & weights
python quick_test_regime.py
python test_regime_detection.py

# Test system accuracy and fixes
python test_system_accuracy.py
python test_system_fixes.py

# Final comprehensive system test
python final_system_test.py
```

### Development

```bash
# Code formatting
black .

# Import organization
isort .

# Linting
flake8 .

# Frontend build
cd frontend && npm run build

# Frontend linting
cd frontend && npm run lint
```

## Architecture & Data Flow

### Analysis Pipeline

1. **Data Collection** (`data/enhanced_provider.py`)
   - `EnhancedYahooProvider` fetches comprehensive market data
   - Implements 20-minute caching (`cache_duration = 1200`) for 50-stock universe
   - Calculates technical indicators using TA-Lib
   - **Institutional flow indicators**: OBV, Accumulation/Distribution, MFI, CMF, VWAP, Volume Z-score
   - Handles numpy array serialization issues with `sanitize_float()` and `sanitize_dict()`

2. **Agent Orchestration** (`core/stock_scorer.py`)
   - `StockScorer` coordinates all 5 agents
   - Combines weighted scores into composite score
   - Returns confidence-weighted recommendations

3. **Narrative Generation** (`narrative_engine/narrative_engine.py`)
   - `InvestmentNarrativeEngine` converts quantitative scores to human-readable thesis
   - Optional LLM integration (OpenAI/Anthropic) for sophisticated reasoning
   - Generates key strengths, risks, and recommendations

4. **API Layer** (`api/main.py`)
   - FastAPI application with comprehensive endpoints
   - Concurrent batch processing (max 10 symbols per batch)
   - In-memory caching with TTL
   - Custom `NumpyEncoder` for JSON serialization

### Data Flow Patterns

- All agents accept optional `cached_data` parameter to avoid redundant API calls
- The `EnhancedYahooProvider` maintains its own cache with 15-minute TTL
- The API layer has a separate `analysis_cache` for full analysis results
- Agents return standardized dictionaries: `{'score': 0-100, 'confidence': 0-1, 'metrics': {...}, 'reasoning': str}`

## API Endpoints

The system exposes a FastAPI server on port 8010:

### Core Analysis
- **POST /analyze** - Complete 5-agent analysis with narrative for single stock
- **GET /analyze/{symbol}** - Quick analysis with cached results
- **POST /analyze/batch** - Batch analysis (max 50 symbols, processed in batches of 10)

### Portfolio Management
- **POST /portfolio/analyze** - Portfolio optimization and risk analysis
- **GET /portfolio/top-picks** - Top investment picks from US_TOP_100_STOCKS
- **GET /portfolio/user** - Get user's portfolio with P&L
- **POST /portfolio/user/position** - Add/update position in user portfolio

### Market Regime (NEW ✨)
- **GET /market/regime** - Get current market regime and adaptive weights
  - Returns trend (BULL/BEAR/SIDEWAYS) and volatility (HIGH/NORMAL/LOW)
  - Provides regime-adjusted agent weights
  - Cached for 6 hours, auto-refreshes

### Paper Trading & Auto-Buy (NEW ✨)
- **GET /portfolio/paper** - Get paper trading portfolio with live prices
- **POST /portfolio/paper/buy** - Execute manual buy in paper portfolio
- **POST /portfolio/paper/sell** - Execute manual sell in paper portfolio
- **GET /portfolio/paper/auto-buy/queue** - Get queued buy opportunities
  - Shows opportunities awaiting batch execution at 4 PM ET
  - Includes symbol, score, signal, queue time, and reason
  - Real-time status updates every 30 seconds in frontend
- **POST /portfolio/paper/auto-buy/scan** - Scan market for auto-buy opportunities
- **POST /portfolio/paper/auto-buy/execute** - Execute queued auto-buys

**Execution Modes:**
The system supports two execution strategies (configured via `execution_mode` in `data/auto_buy_config.json`):

1. **Immediate Execution** (default - recommended for paper trading):
   - Executes buys immediately when STRONG BUY signals are detected
   - Captures opportunities in real-time without delay
   - Provides immediate feedback on signal quality
   - Best for paper trading and educational purposes

2. **Batch Execution at 4 PM** (optional - for real capital):
   - Queues STRONG BUY signals during market hours
   - Executes all queued trades at 4 PM ET (market close)
   - Allows final human review before committing real capital
   - Optimizes pricing through market close execution
   - Re-validates signals before trading to prevent stale trades

**Buy Queue Manager** (`core/buy_queue_manager.py`):
- Thread-safe and process-safe with fcntl file locking
- Atomic writes using temp file + rename pattern
- Auto-cleanup of stale entries (>24 hours old)
- Validation before execution (rejects if score drops >10 points or signal downgrades)

### System
- **GET /health** - System health check (tests all 5 agents)
- **GET /docs** - Swagger UI documentation
- **GET /redoc** - ReDoc alternative documentation

## Frontend Architecture

The frontend is a React + TypeScript + Vite application:

- **Stack**: React 19, TypeScript, Vite, TanStack Query, Tailwind CSS
- **State Management**: Zustand (`src/stores/`)
- **API Client**: Axios with React Query (`src/services/`, `src/hooks/`)
- **UI Components**: Radix UI + custom components (`src/components/`)
- **Routing**: React Router (`src/pages/`)
- **Dev Server**: Vite on port 5174 (or 5173)

## Critical Implementation Details

### Numpy Serialization

The system extensively uses numpy and pandas, which require special JSON serialization handling:

- Use `sanitize_float()` and `sanitize_dict()` in `api/main.py` before returning JSON
- Custom `NumpyEncoder` class handles all numpy types (int64, float64, ndarray, etc.)
- Check for `inf` and `nan` values and convert to `0.0`

### Confidence Scoring

Agent confidence is crucial for overall system reliability:

- Each agent returns a `confidence` score (0-1) based on data availability
- Optional data validator in `utils/data_validator.py` enhances confidence scoring
- Composite confidence is weighted average across all agents
- Confidence affects recommendation strength (HIGH/MEDIUM/LOW)

### Recommendation Mapping

Scores map to recommendations in `narrative_engine/narrative_engine.py`:

- 80-100: STRONG BUY
- 65-79: BUY
- 55-64: WEAK BUY
- 45-54: HOLD
- 35-44: WEAK SELL
- 0-34: SELL

### Stock Universe

The system operates on a curated universe defined in `data/us_top_100_stocks.py`:

- `US_TOP_100_STOCKS`: List of 50 elite stocks from S&P 100 (balanced across 7 sectors)
- `SECTOR_MAPPING`: Dictionary mapping stocks to sectors
- Used by `/portfolio/top-picks` endpoint

## Environment Configuration

Optional environment variables for enhanced features:

```bash
# LLM Provider Selection (default: gemini)
LLM_PROVIDER=gemini            # Options: openai, anthropic, gemini

# API Keys (only one required based on LLM_PROVIDER)
OPENAI_API_KEY=your_key        # For GPT-based sentiment analysis
ANTHROPIC_API_KEY=your_key     # For Claude-based sentiment analysis
GEMINI_API_KEY=your_key        # For Gemini-based sentiment analysis (recommended)
NEWS_API_KEY=your_key           # For news sentiment analysis
```

**LLM Provider Details:**
- **Gemini** (default): Google's Gemini 1.5 Flash - Fast, cost-effective, free tier available
- **OpenAI**: GPT-3.5-turbo - High quality, requires paid API key
- **Anthropic**: Claude 3 Haiku/Sonnet - Excellent reasoning, requires paid API key

LLM integration is optional and gracefully degrades if keys are not provided. The system uses LLMs for:
1. News sentiment analysis in the Sentiment Agent (25% weight)
2. Sophisticated investment thesis generation in the Narrative Engine

To get a Gemini API key (free): https://makersuite.google.com/app/apikey

### 🚀 Adaptive Agent Weights (NEW Feature)

The system now supports **ML-based adaptive agent weights** that automatically adjust based on market conditions:

#### How It Works:
1. **Market Regime Detection**: Uses SPY data to classify current market regime
   - **Trend Analysis**: BULL, BEAR, or SIDEWAYS market
   - **Volatility Analysis**: HIGH_VOL, NORMAL_VOL, or LOW_VOL

2. **Adaptive Weight Adjustment**: Agent weights dynamically change based on regime
   - **Bull + Normal Vol**: F:36% M:27% Q:18% S:9% IF:10% (balanced)
   - **Bull + High Vol**: F:27% M:36% Q:18% S:9% IF:10% (momentum-focused)
   - **Bear + High Vol**: F:18% M:18% Q:36% S:18% IF:10% (quality & safety-focused)
   - **Bear + Normal Vol**: F:27% M:18% Q:27% S:18% IF:10% (fundamentals & quality)

3. **Caching**: Regime is detected once and cached for 6 hours, then auto-refreshes

#### Enabling Adaptive Weights:

```bash
# In .env file
ENABLE_ADAPTIVE_WEIGHTS=true
```

#### Testing Adaptive Weights:

```bash
# Quick regime check
python quick_test_regime.py

# Full comparison (static vs adaptive)
python test_regime_detection.py

# Via API
curl http://localhost:8010/market/regime
```

#### Key Benefits:
- **5-10% performance improvement** in different market cycles
- **Automatic adaptation** to changing market conditions
- **No manual intervention** required
- **Zero additional cost** (uses existing code)

#### Technical Implementation:
- `core/market_regime_service.py`: Market regime detection service
- `ml/regime_detector.py`: ML-based regime classification
- `core/stock_scorer.py`: Integrated adaptive weights support
- `api/main.py`: `/market/regime` endpoint for regime monitoring

## Common Development Tasks

### Adding a New Agent

1. Create agent class in `agents/` inheriting common patterns
2. Implement `analyze()` method returning `{'score': float, 'confidence': float, 'metrics': dict, 'reasoning': str}`
3. Add agent to `StockScorer` in `core/stock_scorer.py`
4. Update agent weights (ensure they sum to 1.0)
5. Update `InvestmentNarrativeEngine` to incorporate new agent's narrative
6. Update API documentation and tests

### Modifying Agent Weights

Agent weights are defined in multiple locations and must be updated consistently:

1. `core/stock_scorer.py` - Default weights dictionary
2. `narrative_engine/narrative_engine.py` - Weighted score calculation
3. `api/main.py` - Documentation strings
4. Update README.md documentation

### Adding New Technical Indicators

1. Add calculation in `data/enhanced_provider.py` → `_calculate_all_indicators()`
2. Use TA-Lib functions for standard indicators
3. Update the returned technical_data dictionary
4. Agents can then access via `cached_data['technical_data']`

## Backtesting Engine V2.0

The system includes a sophisticated historical backtesting engine in `core/backtesting_engine.py` for validating the 5-agent strategy on historical data.

### Key Features (V2.0)

**Version 2.0 Improvements:**
- ✅ **EnhancedYahooProvider Integration**: Uses same data provider as live system (40+ technical indicators vs 3 in v1.x)
- ✅ **Live System Weight Alignment**: Always uses production weights (36/27/18/9/10) - removed `backtest_mode` override
- ✅ **Transparent Bias Documentation**: Clear warnings about look-ahead bias in fundamentals/sentiment data
- ✅ **Backward Compatibility**: Can run in v1.x mode via `use_enhanced_provider=False`
- ✅ **Comprehensive Testing**: 21 unit tests covering versioning, data accuracy, and weight consistency

**Backtesting Capabilities:**
- Historical simulation from 2019-present
- Quarterly/monthly rebalancing
- SPY benchmark comparison
- Risk-adjusted metrics (Sharpe, Sortino, Calmar, Information Ratio)
- Market regime detection integration
- Position tracking and transaction logging
- Stop-loss and risk management testing

### Running Backtests

```bash
# Quick verification test (3 months, 5 stocks)
python3 verify_v2_integration.py

# Compare V1.x vs V2.0 (6 months, Magnificent 7)
python3 compare_backtest_versions.py

# Full 5-year backtest with risk management
python3 run_analytical_fixes_backtest.py

# Unit tests
python3 -m pytest tests/test_backtesting_v2.py -v
```

### Using the Backtesting Engine

```python
from datetime import datetime, timedelta
from core.backtesting_engine import HistoricalBacktestEngine, BacktestConfig

# V2.0 Configuration
config = BacktestConfig(
    start_date='2020-01-01',
    end_date='2024-12-31',
    initial_capital=10000.0,
    rebalance_frequency='quarterly',  # or 'monthly'
    top_n_stocks=20,
    universe=['AAPL', 'MSFT', ...],  # Your stock universe

    # V2.0 features
    engine_version="2.0",              # Default
    use_enhanced_provider=True,        # Use 40+ indicators (default)

    # Optional: Risk management
    enable_risk_management=True,       # Stop-losses, drawdown protection
    enable_regime_detection=True,      # Adaptive weights based on market regime
)

# Run backtest
engine = HistoricalBacktestEngine(config)
result = engine.run_backtest()

# Access results
print(f"Total Return: {result.total_return*100:.2f}%")
print(f"CAGR: {result.cagr*100:.2f}%")
print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
print(f"Max Drawdown: {result.max_drawdown*100:.2f}%")
print(f"vs SPY: {result.outperformance_vs_spy*100:+.2f}%")

# V2.0 metadata
print(f"Engine Version: {result.engine_version}")
print(f"Data Provider: {result.data_provider}")
print(f"Estimated Bias: {result.estimated_bias_impact}")
```

### Data Limitations (IMPORTANT)

**Look-Ahead Bias Warning:**

The backtesting engine has **known look-ahead bias** in two agents:

1. **Fundamentals Agent**: Uses CURRENT financial statements (not historical)
   - Real-world: Q4 2023 financials available in Feb 2024
   - Backtest: Uses 2024 financials for all of 2023 decisions

2. **Sentiment Agent**: Uses CURRENT analyst ratings (not historical)
   - Real-world: Analyst ratings change over time
   - Backtest: Uses current ratings for historical decisions

**Impact**: Results may be **optimistic by 5-10%** due to this bias.

**Mitigation**:
- Use backtests for **relative performance** comparison (strategy A vs B)
- Discount absolute returns by 5-10% for realistic estimates
- Focus on **risk-adjusted metrics** (Sharpe, Sortino) which are less biased
- V2.0 clearly documents limitations in `result.data_limitations`

**Accurate Data** (No Look-Ahead Bias):
- Momentum Agent: Uses historical prices only ✅
- Quality Agent: Partial bias (uses historical prices + current fundamentals)
- Point-in-time filtering for all technical indicators ✅

### V1.x Compatibility Mode

For comparison with legacy backtests:

```python
config = BacktestConfig(
    # ... other params ...
    engine_version="1.0",
    use_enhanced_provider=False  # Only RSI, SMA20, SMA50
)
```

### Migration from V1.x

See `docs/BACKTEST_V2_MIGRATION.md` for detailed migration guide.

**Key Changes:**
- Removed `backtest_mode` parameter (weights always match live system)
- Added `use_enhanced_provider` flag (default: True)
- Added version metadata to results
- Enhanced provider gives 40+ indicators vs 3 in v1.x

**Breaking Changes:**
- None - V1.x configs still work via `use_enhanced_provider=False`

## Troubleshooting

### Port Already in Use

The startup script kills existing processes on ports 8010 and 5174. If issues persist:

```bash
lsof -ti :8010 | xargs kill -9
lsof -ti :5174 | xargs kill -9
```

### Agent Failures

Check `/health` endpoint to diagnose which agent is failing. Healthy system requires at least 4/5 agents operational.

### Cache Issues

To clear analysis cache, restart the API server. The in-memory cache is not persisted.

### Missing Dependencies

Ensure all dependencies are installed:

```bash
pip install -r requirements.txt
cd frontend && npm install
```

Note: `talib-binary` is required for technical indicators. If installation fails, install TA-Lib system library first.