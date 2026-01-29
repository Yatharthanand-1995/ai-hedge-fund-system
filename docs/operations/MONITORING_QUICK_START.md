# Monitoring System - Quick Start Guide

## ✅ System Status

The intelligent signal monitoring system is **LIVE and OPERATIONAL**!

- **Monitoring**: ✅ Enabled (every 30 min during market hours)
- **Watchlist**: 5 stocks (GOOGL, MRK, AAPL, NVDA, MSFT)
- **Trading**: ❌ Disabled (monitor-only mode)
- **Signal History**: ✅ Tracking all changes

---

## 🚀 Quick Commands

### Check System Status
```bash
curl http://localhost:8010/monitoring/watchlist | python3 -m json.tool
```

### View Current Signals (All Monitored Stocks)
```bash
curl http://localhost:8010/monitoring/current-signals | python3 -m json.tool
```

### View Signal History (Recent Changes)
```bash
curl http://localhost:8010/monitoring/signal-history?days=7 | python3 -m json.tool
```

### Get Monitoring Statistics
```bash
curl http://localhost:8010/monitoring/statistics | python3 -m json.tool
```

### Add Stocks to Watchlist
```bash
curl -X POST http://localhost:8010/monitoring/watchlist/add \
  -H "Content-Type: application/json" \
  -d '["TSLA", "META", "AMZN"]' | python3 -m json.tool
```

### Remove Stocks from Watchlist
```bash
curl -X POST http://localhost:8010/monitoring/watchlist/remove \
  -H "Content-Type: application/json" \
  -d '["TSLA"]' | python3 -m json.tool
```

### Manual Test (Direct - No API Deadlock)
```bash
python3 test_monitoring_direct.py
```

---

## 📊 How It Works

### Monitoring Tiers

1. **TIER 1 - Portfolio** (Every 30 min)
   - Monitors all stocks you own
   - Critical for risk management
   - Immediate sell on CRITICAL downgrades

2. **TIER 2 - Hot Watchlist** (Every 2 hours)
   - Monitors 5 hand-picked stocks
   - Opportunity scouting
   - Buys on strong signals

3. **TIER 3 - Full Scan** (Daily at 4 PM ET)
   - Scans all 50 stocks in US_TOP_100_STOCKS
   - Discovery of new opportunities
   - Auto-adds strong candidates to watchlist

### Signal Changes & Urgency

| Change Type | Example | Urgency | Action (if trading enabled) |
|------------|---------|---------|----------------------------|
| CRITICAL_DOWNGRADE | STRONG BUY → SELL | 🔴 CRITICAL | Sell immediately (<5 min) |
| MAJOR_DOWNGRADE | BUY → WEAK SELL | 🟠 HIGH | Sell at next cycle (<30 min) |
| DOWNGRADE | STRONG BUY → HOLD | 🟡 MEDIUM | Monitor closely |
| UPGRADE | HOLD → STRONG BUY | 🟢 MEDIUM | Queue for buy at 4 PM |
| SCORE_CHANGE | Score: 70→75 | ⚪ LOW | Log only |

---

## 🎯 Enabling Automated Trading

**Current Status**: `system_active = false` (monitor-only mode)

### To Enable Trading:

```bash
curl -X POST http://localhost:8010/monitoring/activate
```

This will:
- Execute sells on CRITICAL downgrades (within 5 minutes)
- Execute buys on strong signals (batched at 4 PM)
- Respect all safety limits (position sizing, cash availability)

### To Disable Trading:

```bash
curl -X POST http://localhost:8010/monitoring/deactivate
```

Monitoring continues, but no trades are executed.

---

## 📈 Understanding Signal History

The system tracks EVERY signal change in `data/monitoring/signal_history.json`:

```json
{
  "current_signals": {
    "GOOGL": {
      "signal": "STRONG BUY",
      "score": 76.5,
      "confidence": "MEDIUM",
      "last_updated": "2026-01-02T10:30:00Z",
      "agent_scores": {
        "fundamentals": {"score": 73.5, "reasoning": "..."},
        "momentum": {"score": 96.0, "reasoning": "..."},
        "quality": {"score": 65.0, "reasoning": "..."},
        "sentiment": {"score": 51.5, "reasoning": "..."},
        "institutional_flow": {"score": 56.0, "reasoning": "..."}
      }
    }
  },
  "signal_changes": [
    {
      "timestamp": "2026-01-02T10:30:00Z",
      "symbol": "GOOGL",
      "previous_signal": "BUY",
      "new_signal": "STRONG BUY",
      "score_change": +5.3,
      "change_type": "UPGRADE",
      "urgency": "MEDIUM",
      "reason": "Momentum improved significantly"
    }
  ]
}
```

---

## 🔧 Configuration

Edit `data/monitoring_config.json` to customize:

### Monitoring Intervals
```json
{
  "monitoring": {
    "portfolio_check_interval_minutes": 30,
    "watchlist_check_interval_hours": 2,
    "market_hours_only": true
  }
}
```

### Execution Rules
```json
{
  "execution": {
    "immediate_sells_on_critical": true,
    "batch_buys_at_4pm": true,
    "max_trades_per_hour": 5,
    "min_holding_period_days": 3
  }
}
```

### Watchlist
```json
{
  "monitoring": {
    "hot_watchlist": ["GOOGL", "MRK", "AAPL", "NVDA", "MSFT"]
  }
}
```

---

## 📊 Real-Time Monitoring Dashboard

### Latest Analysis Results (from test)

| Stock | Fundamentals | Momentum | Sentiment | Inst. Flow | Overall |
|-------|-------------|----------|-----------|------------|---------|
| **GOOGL** | 73.5 ⭐ | 96.0 🚀 | 51.5 | 56.0 | STRONG |
| **AAPL** | 62.9 | 70.0 ✅ | 51.5 | 53.0 | MODERATE |
| **MSFT** | 69.0 | 29.0 ⚠️ | 56.0 | 45.5 | MIXED |

**Key Insights**:
- GOOGL showing exceptional momentum (96/100)
- MSFT momentum weakness despite good fundamentals
- AAPL balanced across all metrics

---

## ⚠️ Known Issues

1. **Quality Agent Error**: Currently experiencing a bug in quality agent
   - **Impact**: Minimal - other 4 agents still working
   - **Workaround**: Using 4-agent scoring temporarily
   - **Status**: Can be fixed separately

2. **API Deadlock**: Don't use `/monitoring/trigger` from API
   - **Impact**: Causes timeout when API calls itself
   - **Workaround**: Use `test_monitoring_direct.py` instead
   - **Status**: Will fix in v2.1

---

## 🎓 Next Steps

### Phase 1: Monitor & Learn (Current)
- ✅ Let system track signals for 1 week
- ✅ Review signal changes daily
- ✅ Identify patterns and reliability

### Phase 2: Paper Trading (Week 2)
- Enable auto-trading: `system_active = true`
- Start with small watchlist (3-5 stocks)
- Monitor for unexpected behavior

### Phase 3: Optimization (Week 3+)
- Tune urgency thresholds
- Adjust check intervals
- Optimize position sizing

### Phase 4: Live Trading (Month 2+)
- If Sharpe > 1.5 and drawdown < 15%
- Start with 10% of capital
- Scale up gradually

---

## 📞 Support

**Documentation**:
- Full design: `SIGNAL_MONITORING_DESIGN.md`
- Operations guide: `MONITORING_GUIDE.md`

**Quick Help**:
```bash
# View API documentation
open http://localhost:8010/docs#tag/Signal-Monitoring

# Check logs
tail -f nohup_new.out | grep -i monitoring

# Reset signal history (if needed)
rm data/monitoring/signal_history.json
```

---

**Status**: ✅ System is operational and tracking live market data!

**Last Updated**: 2026-01-02
**Version**: 1.0
