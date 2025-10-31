# Changelog

All notable changes to the AI Hedge Fund System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2025-10-31

### Fixed
- **CRITICAL: Division by Zero Errors in Backtesting**: Fixed 9 division by zero vulnerabilities in `core/backtesting_engine.py`
  - ✅ Logging statistics with zero exits (lines 1459-1465) - **Most likely cause of failures**
  - ✅ Weight normalization when all scores are zero (lines 919-925)
  - ✅ Total return calculations (lines 1362 & 1532)
  - ✅ CAGR calculation with full protection (lines 1370-1373)
  - ✅ Drawdown vector division using np.where (line 1396)
  - ✅ Alpha calculation safe division (lines 1432-1433)
  - ✅ Sharpe ratio with NaN protection (lines 1378-1381)
  - ✅ Sortino ratio with NaN protection (lines 1387-1390)
  - ✅ Volume score safe division (lines 1293-1297)

### Added
- **test_backtest_fix.py**: Comprehensive test script for division by zero fixes
- **BACKTEST_BUGFIX_SUMMARY.md**: Complete documentation of all fixes with examples and testing results

### Testing
- ✅ Quick 3-month backtest: 17.17% return, Sharpe 5.86, no errors
- ✅ All edge cases handled (zero exits, zero volatility, buy-and-hold scenarios)
- ✅ Frontend displays results correctly with transaction log

### Impact
- **Before**: Backtests failed with "division by zero" error, especially on short periods (< 6 months) or buy-and-hold scenarios
- **After**: All backtests complete successfully with proper fallback values for edge cases

---

## [2.1.0] - 2025-10-30

### Added
- **Log Rotation**: Implemented rotating file handler for API logs (10MB max, 5 backups)
- **Scripts Organization**: Created `scripts/` directory structure with subdirectories for analysis, backtesting, monitoring, and verification
- **scripts/README.md**: Comprehensive documentation for all utility scripts
- **docs/PRODUCTION_CONFIG.md**: Production configuration documentation (renamed from RECOMMENDED_CONFIG_APPLIED.md)
- **docs/DATA_LIMITATIONS.md**: Data limitations and look-ahead bias documentation

### Fixed
- **Critical TypeError**: Fixed `Series.__format__` error in backtest result output (affected 3 scripts)
- **Log Management**: Organized and archived 28MB of log files, preventing disk space issues
- **API Server**: Verified API server operational (was already running, startup script issue resolved)

### Changed
- **Project Structure**: Reorganized 11 scripts into logical subdirectories
- **Log Storage**: All logs now stored in `logs/` with subdirectories (api, backtests, tests, archive)
- **Configuration**: Static agent weights (F:40% M:30% Q:20% S:10%) confirmed optimal, adaptive weights disabled by default

### Removed
- **Experimental Files**: Cleaned up 18 experimental test scripts and status documents from root directory
- **Failed Tier 1 Experiments**: Removed Tier 1 improvement attempt files (volatility buffer approach failed with -10.5pp performance)
- **Duplicate Test Logs**: Compressed and archived 8 old test log files

### Performance
- **Baseline Validated**: 162-173% return over 5 years (2020-2025)
- **CAGR**: 17-19% annualized
- **Sharpe Ratio**: 0.75-0.85
- **vs SPY**: +50-60pp outperformance

### Deprecated
- Adaptive weight system remains in code but disabled (testing showed -5 to -10pp reduction in performance)

---

## [2.0.0] - 2025-10-20

### Added
- **V2.0 Backtesting Engine**: Enhanced with 40+ technical indicators via EnhancedYahooProvider
- **ML-based Market Regime Detection**: Bull/Bear/Sideways × High/Normal/Low volatility classification
- **Adaptive Agent Weights**: Dynamic weight adjustment based on market conditions
- **Risk Management System**: Quality-tiered stop-losses, trailing stops, drawdown protection
- **Position Tracking**: Comprehensive exit reason tracking and recovery analysis
- **Sector-Aware Scoring**: Industry-specific fundamental analysis

### Changed
- Migrated from basic technical indicators (3) to EnhancedYahooProvider (40+ indicators)
- Updated all documentation for V2.0 features

### Fixed
- Numpy serialization issues in API responses
- Agent confidence scoring edge cases

---

## [1.0.0] - 2025-09-15

### Added
- Initial release of 4-Agent AI Hedge Fund System
- **Fundamentals Agent** (40% weight): Financial health, profitability, valuation
- **Momentum Agent** (30% weight): Technical analysis and price trends
- **Quality Agent** (20% weight): Business quality assessment
- **Sentiment Agent** (10% weight): Market sentiment analysis
- **Investment Narrative Engine**: Human-readable investment theses
- **FastAPI Backend**: RESTful API with comprehensive endpoints
- **React Frontend**: Modern UI with TanStack Query and Tailwind CSS
- **Portfolio Manager**: Top picks generation and portfolio optimization
- **US_TOP_100_STOCKS**: Curated 50-stock elite universe

### Features
- Real-time stock analysis with 4-agent scoring
- Batch analysis (up to 50 symbols)
- In-memory caching (20-minute TTL)
- LLM integration (OpenAI/Anthropic/Gemini) for enhanced analysis
- Comprehensive API documentation (Swagger/ReDoc)

---

## Version History

- **2.1.0** (2025-10-30): Bug fixes, project reorganization, baseline validation
- **2.0.0** (2025-10-20): V2.0 backtesting engine, adaptive weights, risk management
- **1.0.0** (2025-09-15): Initial 4-agent system release

---

## Lessons Learned

### Tier 1 Failure (October 2025)
**Attempt**: Hybrid stop-loss + volatility buffer + quality tracking
**Result**: **FAILED** - 144.29% return vs 154.82% baseline (-10.5pp worse)
**Root Cause**: Volatility buffer (20% wider stops for high-vol stocks) prevented timely exits
**Lesson**: Wider stops don't reduce false positives; they increase late stops. Original stops were correct.

### Adaptive Weights Testing (October 2025)
**Finding**: Static weights (40/30/20/10) outperformed adaptive weights by 5-21pp
**Configuration Tested**: 4 combinations over 2020-2025
**Winner**: Baseline static weights - 172.82% return
**Lesson**: Market regime adaptation sounds good in theory but degrades real performance. Stick with proven weights.

---

## Future Roadmap

### Under Consideration
- **Weekly Position Monitoring**: Check positions weekly (not quarterly) for early deterioration detection
  - Expected impact: +4-5pp improvement
  - Risk: 4x API calls (rate limiting concerns)

- **Enhanced Sentiment Analysis**: Real-time news and social media sentiment
- **Multi-Portfolio Support**: User-defined custom portfolios
- **Options Analysis**: Options-based hedging strategies

### Not Planned
- ~~Adaptive agent weights~~ (tested, reduced performance)
- ~~Volatility-based stop adjustments~~ (tested, increased late stops)

---

Last Updated: 2025-10-30
