# Scripts Directory

This directory contains utility scripts for backtesting, analysis, monitoring, and verification of the AI Hedge Fund System.

## Directory Structure

```
scripts/
├── analysis/           # Performance analysis and deep dives
├── backtesting/        # Historical backtest runners
├── monitoring/         # System monitoring scripts
└── verification/       # Integration and system verification
```

## 📊 Analysis Scripts

**Purpose**: Deep analysis of backtest results and strategy performance

| Script | Description |
|--------|-------------|
| `deep_analysis.py` | Comprehensive performance analysis with detailed breakdowns |
| `quick_deep_analysis.py` | Fast diagnostic analysis of recent backtests |

**Usage**:
```bash
python3 scripts/analysis/deep_analysis.py
python3 scripts/analysis/quick_deep_analysis.py
```

---

## 🔄 Backtesting Scripts

**Purpose**: Run historical simulations with different configurations

| Script | Description | Duration |
|--------|-------------|----------|
| `run_quick_backtest.py` | Fast 2-year backtest for rapid verification | ~3 min |
| `run_5year_backtest.py` | Full 5-year historical simulation | ~10 min |
| `run_dashboard_backtest.py` | Backtest with dashboard-ready metrics | ~8 min |
| `run_analytical_fixes_backtest.py` | Tests with all analytical fixes enabled | ~10 min |
| `run_baseline_50stocks.py` | Baseline test on 50-stock universe | ~8 min |
| `run_adaptive_vs_static_comparison.py` | Compares adaptive vs static weights | ~15 min |
| `compare_backtest_versions.py` | V1.x vs V2.0+ engine comparison | ~12 min |

**Usage**:
```bash
# Quick 2-year test (fastest)
python3 scripts/backtesting/run_quick_backtest.py

# Full 5-year test (recommended)
python3 scripts/backtesting/run_5year_backtest.py

# Compare static vs adaptive weights
python3 scripts/backtesting/run_adaptive_vs_static_comparison.py
```

**Configuration Options**:
- Modify `ELITE_30` or universe lists in scripts
- Adjust `rebalance_frequency`: 'quarterly', 'monthly'
- Toggle `enable_regime_detection`: True/False
- Set `top_n_stocks`: Number of stocks in portfolio

---

## 🔍 Monitoring Scripts

**Purpose**: Monitor running backtests and system health

| Script | Description |
|--------|-------------|
| `monitor_backtests.sh` | Monitor multiple running backtests, display progress |

**Usage**:
```bash
# Monitor running backtests
./scripts/monitoring/monitor_backtests.sh
```

---

## ✅ Verification Scripts

**Purpose**: Verify system integrity and V2.x engine features

| Script | Description |
|--------|-------------|
| `verify_v2_integration.py` | Quick V2.1 verification test (3 months, 5 stocks) |

**Usage**:
```bash
# Quick verification (1-2 minutes)
python3 scripts/verification/verify_v2_integration.py
```

---

## Common Workflows

### 1. Quick System Check
```bash
# Fast verification that everything works
python3 scripts/verification/verify_v2_integration.py
python3 scripts/backtesting/run_quick_backtest.py
```

### 2. Full Strategy Validation
```bash
# Complete 5-year backtest
python3 scripts/backtesting/run_5year_backtest.py

# Analyze results
python3 scripts/analysis/deep_analysis.py
```

### 3. Test Configuration Changes
```bash
# Compare static vs adaptive weights
python3 scripts/backtesting/run_adaptive_vs_static_comparison.py
```

### 4. Monitor Long-Running Tests
```bash
# In one terminal
python3 scripts/backtesting/run_5year_backtest.py > logs/backtests/5year_test.log &

# In another terminal
./scripts/monitoring/monitor_backtests.sh
```

---

## Expected Results (Baseline)

Based on testing 2020-2025 period with 50-stock universe:

| Metric | Baseline (Static Weights) |
|--------|--------------------------|
| Total Return | 160-175% |
| CAGR | 17-19% |
| Sharpe Ratio | 0.75-0.85 |
| Max Drawdown | -28% to -32% |
| vs SPY Outperformance | +50-60pp |

**Note**: Adaptive weights may reduce performance by 5-10pp in certain market conditions.

---

## Tips

1. **Rate Limiting**: yfinance has rate limits. Space out backtests by 5-10 minutes if running multiple tests.

2. **Logging**: All scripts output to console. Redirect to logs/ for permanent records:
   ```bash
   python3 scripts/backtesting/run_5year_backtest.py > logs/backtests/my_test.log 2>&1
   ```

3. **Parallel Execution**: Don't run more than 2-3 backtests simultaneously to avoid API rate limits.

4. **Look-Ahead Bias**: Backtest results are optimistic by 5-10% due to current fundamental data. See `docs/DATA_LIMITATIONS.md`.

---

## Maintenance

- **Adding New Scripts**: Place in appropriate subdirectory and update this README
- **Deprecating Scripts**: Move to `archive/` directory with note in commit message
- **Performance Issues**: Check yfinance API limits and cache settings

---

Last Updated: 2025-10-30
