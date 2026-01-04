# Paper Trading System - Monitoring Guide

**System Started:** 2025-12-31
**Status:** ✅ LIVE - Automated trading enabled

---

## Quick Status Check

```bash
# System health (all agents operational?)
curl http://localhost:8010/health | python3 -m json.tool

# Scheduler status (next execution time?)
curl http://localhost:8010/scheduler/status | python3 -m json.tool

# Current portfolio (positions, P&L)
curl http://localhost:8010/portfolio/paper | python3 -m json.tool

# Auto-trade configuration
curl http://localhost:8010/portfolio/paper/auto-trade/status | python3 -m json.tool
```

---

## Daily Monitoring Routine

### Morning Check (9:30 AM ET - Market Open)

```bash
# 1. Verify system is running
curl -s http://localhost:8010/health | grep -q "healthy" && echo "✅ System healthy" || echo "❌ System down"

# 2. Check today's execution schedule
curl -s http://localhost:8010/scheduler/status | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'Next trade: {data[\"scheduler\"][\"next_execution\"]}')"

# 3. View current portfolio
curl http://localhost:8010/portfolio/paper | python3 -m json.tool
```

### Evening Check (5:00 PM ET - After Auto-Trade)

```bash
# 1. Check if today's trade executed
curl -s http://localhost:8010/scheduler/status | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'Total executions: {data[\"scheduler\"][\"total_executions\"]}')"

# 2. View transaction log
cat data/paper_portfolio/transaction_log.json | python3 -m json.tool | tail -50

# 3. Check performance metrics
curl http://localhost:8010/performance/dashboard | python3 -m json.tool

# 4. View execution history
curl http://localhost:8010/scheduler/history | python3 -m json.tool
```

---

## What Happens Daily at 4 PM ET

The scheduler automatically:

1. **Executes Auto-Sell First** (frees up capital)
   - Checks all positions for sell triggers
   - Priority: Stop-loss (-10%) > AI signals (SELL/WEAK SELL) > Take-profit (+20%) > Age (180 days)
   - AI signals: If position gets downgraded to SELL/WEAK SELL, exits immediately
   - Take-profit: Deferred if AI still shows STRONG BUY or BUY (lets winners run)

2. **Executes Auto-Buy Second** (uses freed capital + existing cash)
   - Scans US_TOP_100_STOCKS for STRONG BUY signals
   - Applies regime-adaptive thresholds:
     - BULL market: Score ≥ 70 (aggressive)
     - BEAR market: Score ≥ 78 (selective)
     - SIDEWAYS: Score ≥ 72 (moderate)
   - Uses score-weighted position sizing:
     - Score 70: ~5% of portfolio
     - Score 80: ~8% of portfolio
     - Score 90: ~13% of portfolio
     - Score 95: ~14% of portfolio

3. **Records Daily Snapshot**
   - Portfolio value, cash, positions
   - SPY benchmark price
   - Market regime
   - Performance metrics

---

## Performance Tracking

### Weekly Review (Every Monday)

```bash
# 1. Weekly performance summary
curl http://localhost:8010/performance/report

# 2. Compare vs SPY benchmark
curl -s http://localhost:8010/performance/dashboard | python3 -c "import sys, json; d=json.load(sys.stdin); print(f'Portfolio: {d[\"portfolio_return\"]*100:.2f}% | SPY: {d[\"spy_return\"]*100:.2f}% | Alpha: {d[\"outperformance\"]*100:+.2f}%')"

# 3. Win rate analysis
curl -s http://localhost:8010/performance/dashboard | python3 -c "import sys, json; d=json.load(sys.stdin); print(f'Win Rate: {d[\"win_rate\"]:.1f}% | Avg Holding: {d[\"avg_holding_period\"]} days')"
```

### Monthly Review (First day of month)

```bash
# Full performance dashboard
curl http://localhost:8010/performance/dashboard | python3 -m json.tool > monthly_report_$(date +%Y-%m).json

# Calculate key metrics
python3 << 'EOF'
import json
with open('monthly_report_' + __import__('datetime').datetime.now().strftime('%Y-%m') + '.json') as f:
    data = json.load(f)
    print(f"""
📊 MONTHLY PERFORMANCE REPORT
============================
Portfolio Return:   {data['portfolio_return']*100:+.2f}%
SPY Return:         {data['spy_return']*100:+.2f}%
Outperformance:     {data['outperformance']*100:+.2f}%

Sharpe Ratio:       {data['sharpe_ratio']:.2f}
Win Rate:           {data['win_rate']:.1f}%
Total Trades:       {data['total_trades']}

Best Trade:         {data['best_trade']['symbol']} ({data['best_trade']['return_pct']:+.2f}%)
Worst Trade:        {data['worst_trade']['symbol']} ({data['worst_trade']['return_pct']:+.2f}%)
""")
EOF
```

---

## Troubleshooting

### System Not Running

```bash
# Check if API server is running
curl -s http://localhost:8010/health || echo "❌ Server not responding"

# Restart system
./start_system.sh

# Check logs
tail -f nohup.out
```

### Scheduler Not Executing

```bash
# Check scheduler status
curl http://localhost:8010/scheduler/status | python3 -m json.tool

# Manual trigger (for testing)
curl -X POST http://localhost:8010/scheduler/trigger

# Check last execution error
curl -s http://localhost:8010/scheduler/history | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['recent_executions'][-1] if data['recent_executions'] else 'No executions yet')"
```

### Trades Not Executing

```bash
# 1. Check auto-trade rules enabled
curl http://localhost:8010/portfolio/paper/auto-trade/status | grep -q '"enabled": true' && echo "✅ Auto-trade enabled" || echo "❌ Auto-trade disabled"

# 2. Check buy rules
curl http://localhost:8010/portfolio/paper/auto-buy/rules | python3 -m json.tool

# 3. Check sell rules
curl http://localhost:8010/portfolio/paper/auto-sell/rules | python3 -m json.tool

# 4. Scan for opportunities (dry run)
curl -X POST http://localhost:8010/portfolio/paper/auto-buy/scan | python3 -m json.tool
```

### High API Usage (Rate Limiting)

```bash
# Check cache stats
curl http://localhost:8010/cache/stats | python3 -m json.tool

# Clear cache if needed
curl -X DELETE http://localhost:8010/cache/clear
```

---

## Success Metrics (Evaluate After 3 Months)

### Minimum Requirements:
- ✅ **Sharpe Ratio**: > 1.5 (vs SPY ~0.8)
- ✅ **SPY Outperformance**: +5% to +10% annualized
- ✅ **Max Drawdown**: < 15%
- ✅ **Win Rate**: > 60%

### Stretch Goals:
- 🎯 **Sharpe Ratio**: > 2.0
- 🎯 **SPY Outperformance**: +10% to +15% annualized
- 🎯 **Max Drawdown**: < 10%
- 🎯 **Win Rate**: > 65%

---

## Configuration Changes

### Adjust Risk Tolerance

```bash
# More aggressive (lower threshold)
curl -X POST http://localhost:8010/portfolio/paper/auto-buy/rules \
  -H "Content-Type: application/json" \
  -d '{"enabled": true, "min_score_threshold": 70.0, "use_score_weighted_sizing": true}'

# More conservative (higher threshold)
curl -X POST http://localhost:8010/portfolio/paper/auto-buy/rules \
  -H "Content-Type: application/json" \
  -d '{"enabled": true, "min_score_threshold": 80.0, "use_score_weighted_sizing": true}'
```

### Adjust Stop-Loss/Take-Profit

```bash
# Tighter stops (more defensive)
curl -X POST http://localhost:8010/portfolio/paper/auto-sell/rules \
  -H "Content-Type: application/json" \
  -d '{"enabled": true, "stop_loss_percent": -5.0, "take_profit_percent": 15.0}'

# Wider stops (let positions breathe)
curl -X POST http://localhost:8010/portfolio/paper/auto-sell/rules \
  -H "Content-Type: application/json" \
  -d '{"enabled": true, "stop_loss_percent": -15.0, "take_profit_percent": 30.0}'
```

---

## Data Files

**Portfolio State:**
- `data/paper_portfolio/portfolio.json` - Current positions and cash
- `data/paper_portfolio/transaction_log.json` - All trades

**Scheduler:**
- `data/execution_log.json` - Daily execution history

**Performance:**
- `data/daily_snapshots.json` - Daily portfolio snapshots
- `data/trade_analysis.json` - Trade performance analytics

**Logs:**
- `nohup.out` - API server logs
- `logs/trading_scheduler.log` - Scheduler execution logs (if configured)

---

## Emergency Stop

```bash
# Stop all automated trading
curl -X POST http://localhost:8010/portfolio/paper/auto-buy/rules \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'

curl -X POST http://localhost:8010/portfolio/paper/auto-sell/rules \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'

# Stop scheduler
curl -X POST http://localhost:8010/scheduler/stop

# Shut down system
pkill -f "python -m api.main"
```

---

## Next Steps

1. **Let it run for 3 months** (90 trading days)
2. **Review weekly** to ensure system is healthy
3. **Don't panic on bad weeks** - focus on long-term results
4. **After 3 months**: Evaluate metrics and decide if strategy is viable
5. **If successful (beats SPY)**: Consider live trading with small capital
6. **If unsuccessful**: Analyze what went wrong, adjust strategy, backtest again

**Remember:** Paper trading is about proving the strategy works, not about maximizing returns. Focus on risk-adjusted performance (Sharpe ratio) and consistency.

---

**Questions?** Check logs, use API endpoints, or review the comprehensive documentation in:
- `COMPREHENSIVE_ANALYSIS_REPORT.md`
- `CRITICAL_FIXES_SUMMARY.md`
- `HIGH_PRIORITY_BUGS_FIXED.md`
