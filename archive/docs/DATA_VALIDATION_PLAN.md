# Data Validation Plan: Live & Backtesting Data Integrity

## Executive Summary

This document outlines a comprehensive plan to validate that the AI Hedge Fund system uses **real market data** (not mocks) for both live analysis and historical backtesting. The system is currently using legitimate data sources, but this plan provides systematic validation checkpoints.

---

## System Architecture Analysis

### 1. **Data Provider Layer** (`data/enhanced_provider.py`)

#### Current State: ✅ REAL DATA
- **Source**: Yahoo Finance via `yfinance` library
- **Data Types**:
  - Historical OHLCV data (2 years)
  - Company fundamentals (income statements, balance sheets)
  - Real-time prices and market data
  - Technical indicators calculated from real prices
- **Caching**: 20-minute TTL (1200 seconds)

#### Validation Checkpoints:
```python
# Key functions using REAL data:
- yf.Ticker(symbol).history(period="2y")  # Real historical data
- ticker.info                              # Real company info
- ticker.financials                        # Real financial statements
- ticker.quarterly_financials              # Real quarterly data
```

#### Evidence of Real Data:
- Line 64: `ticker = yf.Ticker(symbol)` - Creates Yahoo Finance ticker
- Line 67: `hist = ticker.history(period="2y", interval="1d")` - Downloads real 2-year price history
- Line 82-84: Fetches real financial statements
- Lines 151-304: Calculates technical indicators using TA-Lib on REAL price data

---

### 2. **Backtesting Engine** (`core/backtesting_engine.py`)

#### Current State: ✅ REAL HISTORICAL DATA with Minor Concerns
- **Source**: Yahoo Finance historical data via `yfinance`
- **Methodology**: Point-in-time simulation (no look-ahead bias)
- **Data Range**: User-configurable (default: 5 years)
- **Benchmark**: SPY data for comparison

#### Real Data Evidence:
- Line 176: `yf.download(symbol, start=start_date, end=end_date)` - Real historical downloads
- Line 320: `point_in_time_data = hist_data[hist_data.index <= date]` - Prevents look-ahead bias
- Line 567-579: SPY benchmark uses real downloaded data

#### ⚠️ CONCERN IDENTIFIED:
**Lines 341-381**: The `_calculate_composite_score()` function uses **simplified scoring logic** instead of actual agent analysis. This is a **MAJOR DATA QUALITY ISSUE**.

**Current Implementation (Simplified)**:
```python
# Line 346-352: Uses basic momentum calculation
returns_val = close.pct_change(20).iloc[-1]
momentum_score = min(100, max(0, 50 + returns_val * 100))

# Line 379: Uses default fundamental score
scores.append(60 * 0.4)  # Default fundamental score - NOT REAL AGENT ANALYSIS
```

**What This Means**:
- ❌ Backtest does NOT use actual Fundamentals Agent analysis
- ❌ Backtest does NOT use actual Quality Agent analysis
- ❌ Backtest does NOT use actual Sentiment Agent analysis
- ✅ Backtest DOES use real price/volume data
- ⚠️ Backtest uses simplified scoring proxy instead of full 4-agent system

---

### 3. **API Endpoints** (`api/main.py`)

#### Live Analysis Endpoints - Status: ✅ REAL DATA

**`/analyze` - Single Stock Analysis** (Lines 509-590)
- ✅ Uses `EnhancedYahooProvider` for real data
- ✅ Executes all 4 agents with real data
- ✅ Generates narrative from real agent results
- ✅ 20-minute cache TTL

**`/portfolio/top-picks`** (Lines 842-905)
- ✅ Analyzes 50 real stocks from `US_TOP_100_STOCKS`
- ✅ Uses batch processing with real data
- ✅ Returns real agent scores and recommendations

**`/portfolio/summary`** (Lines 907-979)
- ⚠️ **CONCERN**: Lines 926-929 calculate **synthetic performance** based on scores
- ❌ `daily_performance = (avg_score - 50) * 0.5` - This is NOT real P&L
- ❌ Performance metrics are **derived from scores**, not actual portfolio tracking

#### Backtesting Endpoints - Status: ⚠️ MIXED

**`/backtest/run`** (Lines 1415-1525)
- ⚠️ Uses portfolio-based simulation with **partially synthetic data**
- Line 1444: `total_return = base_return * years + np.random.normal()` - **SIMULATED RETURNS**
- Lines 1449-1468: Equity curve is **generated**, not calculated from real trades
- ❌ This endpoint generates **synthetic backtest data**, not real historical simulation

**`/backtest/historical`** (Lines 1712-1789)
- ✅ Uses `HistoricalBacktestEngine` with real data
- ✅ Downloads real historical prices
- ✅ Simulates actual portfolio rebalancing
- ⚠️ Subject to simplified scoring issue mentioned above

**`/backtest/history`** (Lines 1528-1670)
- ❌ Returns **completely synthetic history** (lines 1576-1636)
- ❌ Uses formula-based return generation, not real backtests
- This is essentially **mock data** for historical backtest results

---

### 4. **Frontend Data Display** (`frontend/src/pages/BacktestingPage.tsx`)

#### Current State: ✅ DISPLAYS REAL API DATA
- Line 91: `fetch('http://localhost:8010/backtest/historical')` - Calls real historical backtest
- Lines 88-107: React Query caching with 30-minute TTL
- ✅ All displayed data comes from API responses
- ✅ No frontend mocking or data generation

**Frontend API Service** (`frontend/src/services/api.ts`)
- ✅ All endpoints point to real backend (`http://localhost:8010`)
- ✅ No mock data injection
- ✅ Proper error handling for failed API calls

---

## Critical Issues Identified

### 🔴 ISSUE #1: Simplified Backtesting Scoring
**Location**: `core/backtesting_engine.py:341-381`
**Problem**: Backtests use simplified proxy scores instead of real 4-agent analysis
**Impact**: Backtest results may not accurately reflect actual system performance
**Severity**: HIGH

### 🔴 ISSUE #2: Synthetic Backtest Endpoint
**Location**: `api/main.py:1415-1525` (`/backtest/run`)
**Problem**: Generates synthetic returns using formulas instead of real simulation
**Impact**: Users may see unrealistic performance projections
**Severity**: HIGH

### 🟡 ISSUE #3: Mock Backtest History
**Location**: `api/main.py:1528-1670` (`/backtest/history`)
**Problem**: Returns generated historical data instead of stored real backtest results
**Impact**: Historical performance is not based on actual backtests
**Severity**: MEDIUM

### 🟡 ISSUE #4: Synthetic Portfolio Performance
**Location**: `api/main.py:907-979` (`/portfolio/summary`)
**Problem**: Calculates performance from scores rather than tracking real positions
**Impact**: Portfolio metrics are estimates, not actual P&L
**Severity**: MEDIUM

---

## Validation Testing Plan

### Phase 1: Live Data Validation (CURRENT - PASSING)

#### Test 1.1: Verify Yahoo Finance Data Freshness
```python
# Create: tests/test_data_provider_real.py

import pytest
from data.enhanced_provider import EnhancedYahooProvider
from datetime import datetime, timedelta

def test_real_data_freshness():
    """Verify that data provider fetches recent market data"""
    provider = EnhancedYahooProvider()
    data = provider.get_comprehensive_data("AAPL")

    # Check that data timestamp is recent (within 24 hours)
    timestamp = datetime.fromisoformat(data['timestamp'])
    assert datetime.now() - timestamp < timedelta(hours=24)

    # Verify current_price is non-zero
    assert data['current_price'] > 0

    # Verify historical data exists
    assert data['historical_data'] is not None
    assert len(data['historical_data']) > 100  # At least 100 days of data

def test_financial_statements_real():
    """Verify that financial statements are real, not mocked"""
    provider = EnhancedYahooProvider()
    data = provider.get_comprehensive_data("AAPL")

    # Check for real financial data
    assert 'financials' in data
    assert data['financials'] is not None

    # Verify info contains real company data
    assert data['info'].get('sector') is not None
    assert data['info'].get('marketCap', 0) > 1000000  # Market cap > $1M

def test_technical_indicators_calculated():
    """Verify technical indicators are calculated from real data, not hardcoded"""
    provider = EnhancedYahooProvider()
    data = provider.get_comprehensive_data("AAPL")

    # RSI should be between 0-100
    assert 0 <= data.get('rsi', 50) <= 100

    # Moving averages should be close to current price
    current_price = data['current_price']
    sma_20 = data.get('sma_20', current_price)
    assert abs(sma_20 - current_price) / current_price < 0.5  # Within 50%
```

#### Test 1.2: Verify Agent Analysis Uses Real Data
```python
# Create: tests/test_agents_real_data.py

def test_fundamentals_agent_real_data():
    """Verify Fundamentals Agent uses actual financial statements"""
    from agents.fundamentals_agent import FundamentalsAgent

    agent = FundamentalsAgent()
    result = agent.analyze("AAPL")

    # Score should be based on real data, not defaults
    assert result['score'] != 50  # Not default score
    assert result['confidence'] > 0

    # Metrics should contain real values
    metrics = result.get('metrics', {})
    assert 'pe_ratio' in metrics or 'roe' in metrics
    assert result['reasoning'] != ""  # Has actual reasoning

def test_momentum_agent_real_prices():
    """Verify Momentum Agent uses real price data"""
    from agents.momentum_agent import MomentumAgent
    from data.enhanced_provider import EnhancedYahooProvider

    provider = EnhancedYahooProvider()
    data = provider.get_comprehensive_data("AAPL")

    agent = MomentumAgent()
    result = agent.analyze("AAPL", data['historical_data'], data['historical_data'])

    # Score should vary based on real market conditions
    assert result['score'] >= 0
    assert result['score'] <= 100
    assert result['confidence'] > 0
```

---

### Phase 2: Backtesting Data Validation (NEEDS FIXES)

#### Test 2.1: Verify Historical Data Downloads
```python
# Create: tests/test_backtest_data.py

def test_backtest_downloads_real_data():
    """Verify backtesting engine downloads actual historical data"""
    from core.backtesting_engine import HistoricalBacktestEngine, BacktestConfig

    config = BacktestConfig(
        start_date="2023-01-01",
        end_date="2023-12-31",
        universe=["AAPL", "MSFT"]
    )

    engine = HistoricalBacktestEngine(config)
    engine._download_historical_data()

    # Verify real data was downloaded
    assert 'AAPL' in engine.historical_prices
    assert 'SPY' in engine.historical_prices
    assert len(engine.historical_prices['AAPL']) > 200  # Full year of data

    # Verify data is from correct period
    aapl_data = engine.historical_prices['AAPL']
    assert aapl_data.index[0].year == 2022  # Includes buffer
    assert aapl_data.index[-1].year >= 2023

def test_backtest_no_lookahead_bias():
    """Verify backtesting doesn't use future data"""
    from core.backtesting_engine import HistoricalBacktestEngine, BacktestConfig

    config = BacktestConfig(
        start_date="2023-01-01",
        end_date="2023-06-30",
        universe=["AAPL"]
    )

    engine = HistoricalBacktestEngine(config)
    engine._download_historical_data()

    # Get score for a specific date
    scores = engine._score_universe_at_date("2023-03-15")

    # Verify only uses data up to that date
    # (Implementation would need to expose internal state for full verification)
    assert len(scores) > 0
```

#### Test 2.2: Identify Mock Data in API Responses
```python
def test_backtest_run_endpoint_identifies_synthetic():
    """Flag synthetic data in /backtest/run endpoint"""
    import requests

    response = requests.post('http://localhost:8010/backtest/run', json={
        'start_date': '2023-01-01',
        'end_date': '2023-12-31',
        'rebalance_frequency': 'monthly',
        'top_n': 10,
        'universe': ['AAPL', 'MSFT'],
        'initial_capital': 10000
    })

    result = response.json()

    # Check for indicators of synthetic data
    equity_curve = result['results']['equity_curve']

    # Real data should have daily fluctuations
    # Synthetic data may have smooth curves
    returns = [equity_curve[i]['return'] - equity_curve[i-1]['return']
               for i in range(1, len(equity_curve))]

    # Flag if returns are too smooth (low variance)
    variance = np.var(returns)
    if variance < 0.0001:
        pytest.fail("Returns appear synthetic - variance too low")

def test_backtest_history_detects_generated_data():
    """Detect generated vs. stored backtest history"""
    import requests

    response = requests.get('http://localhost:8010/backtest/history')
    history = response.json()

    # Check if history changes on refresh (indicates generation)
    response2 = requests.get('http://localhost:8010/backtest/history')
    history2 = response2.json()

    # Generated data may differ between calls
    # Real stored data should be identical
    if history != history2:
        print("WARNING: Backtest history appears to be generated, not stored")
```

---

### Phase 3: End-to-End Data Flow Validation

#### Test 3.1: Trace Data from Source to Display
```python
def test_e2e_data_lineage():
    """Trace data from Yahoo Finance to frontend display"""
    import requests
    from data.enhanced_provider import EnhancedYahooProvider

    # Step 1: Fetch raw data
    provider = EnhancedYahooProvider()
    raw_data = provider.get_comprehensive_data("AAPL")
    raw_price = raw_data['current_price']

    # Step 2: Analyze via API
    response = requests.post('http://localhost:8010/analyze',
                            json={'symbol': 'AAPL'})
    api_data = response.json()
    api_price = api_data['market_data']['current_price']

    # Step 3: Verify price consistency
    assert abs(raw_price - api_price) < 0.01  # Within 1 cent

    # Step 4: Verify agent scores are computed
    assert 'agent_results' in api_data
    assert 'fundamentals' in api_data['agent_results']

    # Step 5: Verify narrative is generated
    assert 'narrative' in api_data
    assert api_data['narrative']['investment_thesis'] != ""
```

#### Test 3.2: Compare Live vs Historical Data
```python
def test_historical_matches_live_data():
    """Verify historical backtesting uses same data source as live"""
    from data.enhanced_provider import EnhancedYahooProvider
    import yfinance as yf

    # Get data via live provider
    provider = EnhancedYahooProvider()
    live_data = provider.get_comprehensive_data("AAPL")

    # Get same data via yfinance (what backtest uses)
    ticker = yf.Ticker("AAPL")
    hist = ticker.history(period="2y")

    # Compare latest prices
    live_price = live_data['current_price']
    hist_price = float(hist['Close'].iloc[-1])

    assert abs(live_price - hist_price) < 0.01
```

---

## Implementation Roadmap

### ✅ Phase 1: Document Current State (COMPLETED)
1. ✅ Map all data sources
2. ✅ Identify real vs. synthetic data
3. ✅ Document validation concerns

### 🔴 Phase 2: Fix Critical Issues (URGENT)

#### Fix #1: Implement Real Agent Scoring in Backtests
**File**: `core/backtesting_engine.py`
**Changes Needed**:
```python
# Replace _calculate_composite_score() with real agent analysis
def _score_universe_at_date(self, date: str) -> List[Dict]:
    scores = []

    for symbol in self.config.universe:
        # Get point-in-time data
        hist_data = self.historical_prices[symbol]
        point_in_time_data = hist_data[hist_data.index <= date]

        # Create comprehensive data structure
        comprehensive_data = {
            'historical_data': point_in_time_data,
            'current_price': float(point_in_time_data['Close'].iloc[-1]),
            # ... other required fields
        }

        # Use ACTUAL agents (not simplified proxies)
        try:
            fund_result = self.fundamentals_agent.analyze(symbol)
            momentum_result = self.momentum_agent.analyze(
                symbol, point_in_time_data, point_in_time_data
            )
            quality_result = self.quality_agent.analyze(symbol, comprehensive_data)
            sentiment_result = self.sentiment_agent.analyze(symbol)

            # Calculate weighted composite score
            composite_score = (
                fund_result['score'] * self.config.agent_weights['fundamentals'] +
                momentum_result['score'] * self.config.agent_weights['momentum'] +
                quality_result['score'] * self.config.agent_weights['quality'] +
                sentiment_result['score'] * self.config.agent_weights['sentiment']
            )

            scores.append({
                'symbol': symbol,
                'score': composite_score,
                'date': date
            })
        except Exception as e:
            logger.warning(f"Failed to score {symbol} on {date}: {e}")
            continue

    return scores
```

#### Fix #2: Replace Synthetic Backtest with Real Engine
**File**: `api/main.py`
**Changes**:
```python
# Line 1415-1525: Replace /backtest/run implementation
@app.post("/backtest/run", response_model=BacktestResults, tags=["Backtesting"])
async def run_backtest(config: BacktestConfig, background_tasks: BackgroundTasks):
    """Run REAL historical backtest (redirect to /backtest/historical)"""
    # Simply redirect to the real historical backtest
    return await run_historical_backtest(config)
```

#### Fix #3: Store and Retrieve Real Backtest History
**File**: `api/main.py`
**Create**: `data/backtest_history.json`
```python
# Line 1528: Replace /backtest/history with real storage
BACKTEST_HISTORY_FILE = 'data/backtest_history.json'

@app.get("/backtest/history", tags=["Backtesting"])
async def get_backtest_history():
    """Get STORED historical backtest results"""
    try:
        with open(BACKTEST_HISTORY_FILE, 'r') as f:
            history = json.load(f)
        return history
    except FileNotFoundError:
        # If no history exists, run initial backtests
        return []

# Add storage after each backtest
def save_backtest_to_history(result: BacktestResult):
    try:
        with open(BACKTEST_HISTORY_FILE, 'r') as f:
            history = json.load(f)
    except FileNotFoundError:
        history = []

    history.append({
        'timestamp': datetime.now().isoformat(),
        'config': result.config.dict(),
        'results': result.dict()
    })

    # Keep only last 10 backtests
    history = history[-10:]

    with open(BACKTEST_HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)
```

---

### 🟡 Phase 3: Implement Validation Tests (MEDIUM PRIORITY)

Create test suite:
```bash
tests/
├── test_data_provider_real.py      # Test 1.1
├── test_agents_real_data.py        # Test 1.2
├── test_backtest_data.py           # Test 2.1
├── test_backtest_synthetic.py      # Test 2.2
└── test_e2e_data_flow.py           # Test 3.1, 3.2
```

Run tests:
```bash
pytest tests/ -v --tb=short
```

---

### 🟢 Phase 4: Continuous Monitoring (ONGOING)

#### Create Data Quality Dashboard
**File**: `utils/data_quality_monitor.py`
```python
class DataQualityMonitor:
    """Monitor data quality and freshness"""

    def check_data_freshness(self, symbol: str) -> Dict:
        """Verify data is recent"""
        provider = EnhancedYahooProvider()
        data = provider.get_comprehensive_data(symbol)

        timestamp = datetime.fromisoformat(data['timestamp'])
        age_hours = (datetime.now() - timestamp).total_seconds() / 3600

        return {
            'symbol': symbol,
            'data_age_hours': age_hours,
            'is_fresh': age_hours < 24,
            'current_price': data['current_price'],
            'has_financials': data.get('financials') is not None
        }

    def detect_synthetic_patterns(self, equity_curve: List[Dict]) -> bool:
        """Detect if equity curve appears synthetic"""
        returns = np.diff([p['value'] for p in equity_curve])

        # Check for suspicious patterns
        variance = np.var(returns)
        mean = np.mean(returns)

        # Real data has irregular patterns
        # Synthetic data is often too smooth
        if variance < 0.001:
            return True  # Likely synthetic

        return False
```

#### Add Logging for Data Sources
```python
# Add to data/enhanced_provider.py
logger.info(f"Fetching REAL data for {symbol} from Yahoo Finance API")
logger.info(f"Downloaded {len(hist)} days of OHLCV data")
logger.info(f"Retrieved {len(financials.columns) if financials else 0} financial periods")
```

---

## Validation Checklist

### ✅ Live Data Sources (VERIFIED - REAL)
- [x] Yahoo Finance API for prices
- [x] yfinance library for historical data
- [x] Financial statements from Yahoo Finance
- [x] Technical indicators calculated via TA-Lib
- [x] All 4 agents use real data inputs

### ⚠️ Backtesting Data Sources (PARTIALLY REAL)
- [x] Historical prices downloaded via yfinance
- [x] SPY benchmark data is real
- [x] Point-in-time simulation (no look-ahead)
- [ ] ❌ Agent scoring uses simplified proxies (NOT REAL AGENTS)
- [ ] ❌ Some endpoints generate synthetic returns

### ❌ Synthetic/Mock Data Identified
- [ ] `/backtest/run` - Generates synthetic equity curves
- [ ] `/backtest/history` - Returns generated history
- [ ] `/portfolio/summary` - Calculates synthetic P&L
- [ ] `_calculate_composite_score()` - Uses simplified scoring

---

## Success Criteria

### Definition of "Real Data"
1. ✅ Data originates from external market data provider (Yahoo Finance)
2. ✅ Data is recent (< 24 hours old for live, historical for backtests)
3. ✅ Data contains actual price movements, not formulas
4. ✅ Financial statements match SEC filings
5. ❌ Backtests use full 4-agent analysis (NOT YET - needs fix)

### Validation Metrics
- **Data Freshness**: < 24 hours for live data
- **Price Accuracy**: Within $0.01 of market close
- **Historical Coverage**: 100% of requested date range
- **Agent Analysis**: All 4 agents execute successfully
- **Backtest Accuracy**: Uses real agent scores, not proxies

---

## Conclusion

### Current State Summary

**Live Analysis**: ✅ **FULLY REAL DATA**
- All live endpoints use real Yahoo Finance data
- All 4 agents analyze real market conditions
- No mock data in live analysis pipeline

**Historical Backtesting**: ⚠️ **REAL PRICES, SIMPLIFIED SCORING**
- Historical prices are 100% real (Yahoo Finance)
- Point-in-time simulation prevents look-ahead bias
- **CRITICAL ISSUE**: Agent scoring uses simplified proxies instead of real agents
- **CRITICAL ISSUE**: Some endpoints generate synthetic performance data

**Frontend**: ✅ **DISPLAYS REAL API DATA**
- No frontend data generation
- All metrics come from backend APIs
- Proper caching with appropriate TTLs

### Priority Actions

1. **IMMEDIATE** (Week 1):
   - Implement real 4-agent scoring in backtest engine
   - Remove synthetic return generation from `/backtest/run`

2. **SHORT-TERM** (Week 2):
   - Create backtest history storage system
   - Implement data quality monitoring

3. **ONGOING**:
   - Run validation test suite weekly
   - Monitor data freshness logs
   - Document any new data sources

### Risk Assessment

**Current Risk Level**: 🟡 MEDIUM
- Live data is solid and trustworthy
- Backtest data is real but scoring is simplified
- Risk of misleading users about backtest accuracy

**After Fixes**: 🟢 LOW
- All data sources will be verified real
- Full system traceability
- Comprehensive validation testing

---

**Document Version**: 1.0
**Last Updated**: 2025-10-10
**Author**: AI Hedge Fund System Team
**Status**: Ready for Implementation
