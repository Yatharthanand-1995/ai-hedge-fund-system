# Dashboard 5-Year Backtest - In Progress

**Status**: 🔄 RUNNING
**Started**: October 11, 2025
**Expected Duration**: 5-10 minutes

---

## Configuration (Matches Dashboard Exactly)

- **Initial Capital**: $10,000 ✅
- **Portfolio Size**: Top 20 stocks ✅
- **Rebalance Frequency**: Quarterly (4 times per year) ✅
- **Universe**: 20 stocks (AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA, V, JPM, UNH, JNJ, WMT, PG, HD, MA, LLY, ABBV, KO, CVX, AVGO) ✅
- **Period**: 2020-10-12 to 2025-10-11 (5 years) ✅
- **Real 4-Agent Analysis**: YES ✅

---

## Agent Weights (Backtest Mode)

- **Momentum**: 50% (most reliable for historical data)
- **Quality**: 40% (stable business metrics)
- **Fundamentals**: 5% (reduced due to look-ahead bias)
- **Sentiment**: 5% (reduced due to look-ahead bias)

---

## Progress

### Data Download: ✅ COMPLETE
- Downloaded 1,507 days of historical price data for each of 20 stocks
- Downloaded SPY benchmark data
- Total: 21 symbols loaded

### Rebalance Schedule: ✅ GENERATED
- Generated 20 quarterly rebalance dates (Oct 2020 - Oct 2025)
- First rebalance: 2020-10-12
- Last rebalance: 2025-10-12 (projected)

### Simulation: 🔄 RUNNING
- Currently on: 2020-10-12 (first rebalance)
- Scoring all 20 stocks using real 4-agent analysis
- For each stock: F, M, Q, S agents analyze point-in-time data
- Portfolio simulation will run through 1,826 days (5 years)

---

## Why Dashboard Was Showing Loading

### Root Causes Identified:

1. **Wrong Initial Capital**: Previous backtests used $100,000, dashboard expects $10,000
2. **Wrong Portfolio Size**: Previous backtests used 8-10 stocks, dashboard expects top 20
3. **Wrong Rebalance Frequency**: Previous backtests used monthly, dashboard expects quarterly
4. **No 5-Year Backtest**: Only had 2-year periods, not full 5 years
5. **Mixed Data**: Backtest storage had inconsistent configurations

---

## What This Backtest Will Provide

Once complete, you will see:

### Performance Metrics
- **Total Return**: How much $10,000 grew to
- **CAGR**: Compound annual growth rate over 5 years
- **Sharpe Ratio**: Risk-adjusted return quality
- **Max Drawdown**: Worst peak-to-trough decline
- **Volatility**: Annualized standard deviation

### Comparison vs SPY
- SPY 5-year return
- Outperformance (alpha)
- Beta (market correlation)

### Trading Activity
- 20 quarterly rebalances
- Transaction costs accounted for
- Equity curve with 1,826 daily data points

### Portfolio Analysis
- Best performing stocks over 5 years
- Worst performing stocks
- Win rate, profit factor
- Year-by-year breakdown

---

## Next Steps (After Backtest Completes)

1. **Extract Results**: Run `python extract_backtest_data.py` to update static data
2. **Regenerate Frontend Data**: Create new staticBacktestData.ts with 5-year results
3. **Restart Frontend Dev Server**: Ensure new data is loaded
4. **Verify Dashboard**: Check that results display instantly without loading

---

## Log File

Monitor progress: `/tmp/dashboard_backtest.log`

```bash
# Watch progress in real-time
tail -f /tmp/dashboard_backtest.log

# Check last 50 lines
tail -50 /tmp/dashboard_backtest.log

# Check if complete
grep "Backtest complete" /tmp/dashboard_backtest.log
```

---

## Expected Timeline

- **Data Download**: ✅ Complete (took ~30 seconds)
- **First Rebalance**: 🔄 In progress (scoring 20 stocks × 4 agents = 80 analyses)
- **Remaining Rebalances**: 19 more to go (each takes ~15-30 seconds)
- **Results Calculation**: Final metrics and analysis (~30 seconds)

**Total Estimated Time**: 5-10 minutes

---

## Technical Details

### Script Location
`/Users/yatharthanand/ai_hedge_fund_system/run_dashboard_backtest.py`

### Output Location
`data/backtest_results/dashboard_5year_20201012_20251011.json`

### Backtest Engine
- Class: `HistoricalBacktestEngine`
- Module: `core.backtesting_engine`
- Real agents: `FundamentalsAgent`, `MomentumAgent`, `QualityAgent`, `SentimentAgent`

---

**Last Updated**: October 11, 2025 (backtest in progress)
