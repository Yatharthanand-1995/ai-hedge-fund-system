# Backtesting Engine V2.0 Migration Guide

## Overview

This guide helps you migrate from Backtesting Engine V1.x to V2.0, which includes significant improvements in data quality, weight alignment, and transparency.

## What's New in V2.0

### 1. EnhancedYahooProvider Integration (🔥 Major Improvement)

**Before (V1.x)**: Minimal technical indicators
- RSI (14-period)
- SMA 20
- SMA 50

**After (V2.0)**: Full technical indicator suite (40+ indicators)
- All indicators from live system
- MACD, Bollinger Bands, ATR, Stochastic, Volume indicators
- 20+ momentum, volatility, and trend indicators
- Same data provider as production system

**Impact**: More accurate simulation of live system behavior, better momentum/technical analysis.

### 2. Live System Weight Alignment (⚠️ Breaking Behavior Change)

**Before (V1.x)**: Backtest used different weights
```python
# V1.x with backtest_mode=True
config = BacktestConfig(
    backtest_mode=True,  # Used 50/40/5/5 weights
    # ...
)
```

Weights in V1.x backtest mode:
- Fundamentals: 50%
- Momentum: 40%
- Quality: 5%
- Sentiment: 5%

**After (V2.0)**: Always uses live system weights
```python
# V2.0 - backtest_mode parameter removed
config = BacktestConfig(
    # No backtest_mode parameter
    # Always uses 40/30/20/10 weights
    # ...
)
```

Weights in V2.0:
- Fundamentals: 40%
- Momentum: 30%
- Quality: 20%
- Sentiment: 10%

**Impact**: Backtest results now accurately reflect production performance.

### 3. Transparent Bias Documentation (✅ Transparency Improvement)

**Before (V1.x)**: No documentation of data limitations

**After (V2.0)**: Clear warnings and metadata
- Prominent warnings at backtest start and end
- `result.data_limitations` dictionary documents each agent's bias
- `result.estimated_bias_impact` provides 5-10% optimism estimate
- Look-ahead bias in fundamentals/sentiment clearly disclosed

**Impact**: Better understanding of backtest reliability, realistic expectations.

### 4. Version Metadata (📊 Observability Improvement)

**Before (V1.x)**: No version tracking

**After (V2.0)**: Full version metadata
```python
result.engine_version        # "2.0"
result.data_provider         # "EnhancedYahooProvider" or "RawYFinance"
result.data_limitations      # Dict of agent limitations
result.estimated_bias_impact # "Results may be optimistic by 5-10%..."
```

**Impact**: Can compare V1.x vs V2.0 results, track improvements over time.

## Migration Steps

### Step 1: Update Your Backtest Scripts

#### Before (V1.x):
```python
from core.backtesting_engine import HistoricalBacktestEngine, BacktestConfig

config = BacktestConfig(
    start_date='2020-01-01',
    end_date='2024-12-31',
    initial_capital=10000.0,
    rebalance_frequency='quarterly',
    top_n_stocks=20,
    universe=['AAPL', 'MSFT', 'GOOGL'],
    backtest_mode=True  # ❌ REMOVED IN V2.0
)

engine = HistoricalBacktestEngine(config)
result = engine.run_backtest()

print(f"Total Return: {result.total_return*100:.2f}%")
```

#### After (V2.0):
```python
from core.backtesting_engine import HistoricalBacktestEngine, BacktestConfig

config = BacktestConfig(
    start_date='2020-01-01',
    end_date='2024-12-31',
    initial_capital=10000.0,
    rebalance_frequency='quarterly',
    top_n_stocks=20,
    universe=['AAPL', 'MSFT', 'GOOGL'],
    # ✅ No backtest_mode parameter needed
    # ✅ New V2.0 features (optional):
    engine_version="2.0",              # Default
    use_enhanced_provider=True,        # Default - use 40+ indicators
)

engine = HistoricalBacktestEngine(config)
result = engine.run_backtest()

# ✅ Access V2.0 metadata
print(f"Total Return: {result.total_return*100:.2f}%")
print(f"Engine Version: {result.engine_version}")
print(f"Data Provider: {result.data_provider}")
print(f"Estimated Bias: {result.estimated_bias_impact}")

# ✅ Review data limitations
for agent, limitation in result.data_limitations.items():
    print(f"{agent}: {limitation}")
```

### Step 2: Remove `backtest_mode` Parameter

Simply delete the `backtest_mode` parameter from your BacktestConfig:

```diff
config = BacktestConfig(
    start_date='2020-01-01',
    end_date='2024-12-31',
-   backtest_mode=True,
    # ... other params ...
)
```

That's it! V2.0 will automatically use live system weights (40/30/20/10).

### Step 3: Interpret Results with Bias Awareness

V2.0 clearly documents look-ahead bias. Adjust your interpretation:

**Before (V1.x)**: No guidance on bias
```python
result = engine.run_backtest()
print(f"Total Return: {result.total_return*100:.2f}%")
# ❌ No information about optimistic bias
```

**After (V2.0)**: Clear bias documentation
```python
result = engine.run_backtest()
print(f"Total Return: {result.total_return*100:.2f}%")
print(f"⚠️  {result.estimated_bias_impact}")

# ✅ Adjust expectations for realistic estimate
optimistic_return = result.total_return
realistic_return = optimistic_return * 0.95  # Discount by 5% for look-ahead bias
print(f"Realistic Estimate: {realistic_return*100:.2f}%")
```

### Step 4: Run V1.x vs V2.0 Comparison

Use the comparison script to see differences:

```bash
python3 compare_backtest_versions.py
```

This will:
- Run same backtest in V1.x mode (minimal indicators)
- Run same backtest in V2.0 mode (full indicators)
- Show performance differences
- Highlight risk-adjusted metrics

Expected differences:
- Total return: <5% difference (data quality, not strategy)
- Sharpe ratio: May improve in V2.0 (better momentum signals)
- Max drawdown: Similar (depends on risk management settings)

## Backward Compatibility

### Running V1.x Mode in V2.0

If you need to reproduce V1.x results exactly:

```python
config = BacktestConfig(
    start_date='2020-01-01',
    end_date='2024-12-31',
    # ... other params ...

    # V1.x compatibility mode
    engine_version="1.0",
    use_enhanced_provider=False  # Only RSI, SMA20, SMA50
)
```

This will:
- Use minimal indicators (RSI, SMA20, SMA50) like V1.x
- Still use live system weights (40/30/20/10) - NOT backtest_mode weights
- Mark result as `data_provider="RawYFinance"`

**Note**: There is NO way to reproduce old backtest_mode weights (50/40/5/5) in V2.0. This was intentionally removed for consistency with production.

## Breaking Changes

### 1. Removed: `backtest_mode` Parameter

**Impact**: HIGH
**Action**: Remove parameter from all BacktestConfig instantiations

```diff
config = BacktestConfig(
-   backtest_mode=True,
    # ... other params ...
)
```

**Rationale**: Backtest should always match live system weights for accurate simulation.

### 2. Changed: Default Agent Weights

**Impact**: HIGH
**Action**: Expect different results due to weight changes

V1.x backtest mode:
- F:50%, M:40%, Q:5%, S:5%

V2.0 (always):
- F:40%, M:30%, Q:20%, S:10%

**Rationale**: V2.0 weights match production system. Old backtest weights were never used in production.

### 3. Added: Version Metadata Fields

**Impact**: LOW (additive change)
**Action**: Optionally access new fields

New fields in BacktestResult:
- `engine_version`
- `data_provider`
- `data_limitations`
- `estimated_bias_impact`

These fields have defaults, so old code accessing only standard fields will continue to work.

## Non-Breaking Changes

### 1. Added: `use_enhanced_provider` Flag

Default: `True` (use EnhancedYahooProvider)

Set to `False` for V1.x compatibility mode.

### 2. Added: Bias Warnings

During backtest execution, you'll see new warnings:

```
================================================================================
⚠️  DATA LIMITATIONS WARNING (v2.0)
================================================================================
Fundamentals Agent: Uses CURRENT financial statements (look-ahead bias)
Sentiment Agent: Uses CURRENT analyst ratings (look-ahead bias)
Momentum Agent: Uses historical prices (accurate)
Quality Agent: Uses historical prices + current fundamentals (partial bias)

Expected Impact: Results may be optimistic by 5-10% due to look-ahead bias
================================================================================
```

These warnings are informational and don't affect execution.

## Example: Full Migration

### Before (V1.x):
```python
#!/usr/bin/env python3
"""
Legacy backtest script (V1.x)
"""
from core.backtesting_engine import HistoricalBacktestEngine, BacktestConfig
from data.us_top_100_stocks import US_TOP_100_STOCKS

config = BacktestConfig(
    start_date='2020-01-01',
    end_date='2024-12-31',
    initial_capital=10000.0,
    rebalance_frequency='quarterly',
    top_n_stocks=20,
    universe=US_TOP_100_STOCKS,
    backtest_mode=True,  # ❌ REMOVED
)

engine = HistoricalBacktestEngine(config)
result = engine.run_backtest()

print(f"Final Value: ${result.final_value:,.2f}")
print(f"Total Return: {result.total_return*100:.2f}%")
print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
```

### After (V2.0):
```python
#!/usr/bin/env python3
"""
Updated backtest script (V2.0)
"""
from core.backtesting_engine import HistoricalBacktestEngine, BacktestConfig
from data.us_top_100_stocks import US_TOP_100_STOCKS

config = BacktestConfig(
    start_date='2020-01-01',
    end_date='2024-12-31',
    initial_capital=10000.0,
    rebalance_frequency='quarterly',
    top_n_stocks=20,
    universe=US_TOP_100_STOCKS,
    # ✅ No backtest_mode needed
    # ✅ V2.0 defaults to enhanced provider and live weights
)

engine = HistoricalBacktestEngine(config)
result = engine.run_backtest()

# ✅ Original metrics still work
print(f"Final Value: ${result.final_value:,.2f}")
print(f"Total Return: {result.total_return*100:.2f}%")
print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")

# ✅ New V2.0 metadata
print(f"\nEngine Version: {result.engine_version}")
print(f"Data Provider: {result.data_provider}")
print(f"⚠️  {result.estimated_bias_impact}")

# ✅ Realistic estimate accounting for bias
realistic_return = result.total_return * 0.95  # Discount 5%
print(f"\nRealistic Estimate: {realistic_return*100:.2f}%")
```

## Testing Your Migration

1. **Run verification test**:
```bash
python3 verify_v2_integration.py
```

Expected output:
```
✅ V2.0 INTEGRATION VERIFICATION - SUCCESS
   • EnhancedYahooProvider successfully integrated
   • Point-in-time filtering working
   • Version metadata correctly set
   • Agent weights aligned with live system
```

2. **Run comparison test**:
```bash
python3 compare_backtest_versions.py
```

Expected output:
```
📊 COMPARISON RESULTS
   Total Return: V1.x: +XX.XX%  V2.0: +YY.YY%
   Difference: <5% (data quality improvement)
```

3. **Run unit tests**:
```bash
python3 -m pytest tests/test_backtesting_v2.py -v
```

Expected output:
```
21 passed in 2.30s
```

## FAQs

### Q: Will my backtest results change in V2.0?

**A**: Yes, for two reasons:
1. **Weight change**: V1.x backtest_mode used 50/40/5/5, V2.0 uses 40/30/20/10 (live weights)
2. **Data improvement**: V2.0 has 40+ indicators vs 3 in V1.x (better momentum signals)

Expected impact: 5-15% total return difference depending on market conditions.

### Q: Can I reproduce V1.x backtest_mode results in V2.0?

**A**: No. The backtest_mode weights (50/40/5/5) are not available in V2.0. This was intentional - those weights were never used in production, so simulating them provides no value.

You CAN reproduce V1.x data provider (minimal indicators) via `use_enhanced_provider=False`, but weights will be 40/30/20/10 (live system).

### Q: Why does V2.0 warn about look-ahead bias?

**A**: V2.0 is more transparent about data limitations:
- Fundamentals Agent uses current financial statements (not point-in-time)
- Sentiment Agent uses current analyst ratings (not historical)

These limitations existed in V1.x too, but weren't documented. V2.0 makes them explicit so you can interpret results appropriately.

### Q: Should I discount backtest results by 5-10%?

**A**: For absolute return estimates, yes. The look-ahead bias in fundamentals/sentiment can make results optimistic.

However, for **relative comparisons** (Strategy A vs Strategy B), you don't need to discount - both are affected equally.

Also, **risk-adjusted metrics** (Sharpe, Sortino, Information Ratio) are less affected by bias and more reliable.

### Q: What's the recommended approach for backtesting?

**A**:

1. **Use V2.0 defaults** for most accurate simulation of live system
2. **Compare strategies relatively**, not absolute returns
3. **Focus on risk-adjusted metrics** (Sharpe, Sortino, Calmar)
4. **Discount absolute returns** by 5-10% for realistic estimates
5. **Test on multiple time periods** and market regimes
6. **Combine with forward testing** before deployment

## Support

For issues or questions about migration:
1. Check `tests/test_backtesting_v2.py` for example usage
2. Run `python3 verify_v2_integration.py` to validate setup
3. Review `CLAUDE.md` section "Backtesting Engine V2.0"
4. Open an issue if problems persist

## Version History

- **V2.0** (2025-10-23): EnhancedYahooProvider integration, live weight alignment, bias documentation
- **V1.x** (2024-2025): Original implementation with minimal indicators and backtest_mode weights
