# Signal-Based Continuous Monitoring System - Design Document

**Status:** 🎯 PLANNING
**Priority:** HIGH
**Estimated Implementation:** 7-10 days
**Complexity:** Medium-High

---

## Executive Summary

Transform the current "daily check at 4 PM" system into an **intelligent, continuous signal monitoring system** that:
- Tracks market signals every 15-30 minutes during market hours
- Logs all signal changes to database for analysis
- Triggers immediate trades on critical signal changes (when system is active)
- Provides complete signal history and analytics

---

## 🎯 Problem Statement

### Current Limitations:
1. **Timing Risk:** Only checks once daily at 4 PM ET
   - Misses: STRONG BUY at 10 AM → SELL at 2 PM (would hold losing position overnight)
   - Misses: New STRONG BUY appears at 11 AM (waits until next day to buy)

2. **No Signal Visibility:** No record of signal changes over time
   - Can't answer: "How long was GOOGL a STRONG BUY before it dropped?"
   - Can't analyze: "Which signal changes led to best returns?"

3. **Binary Operation:** System is always "on" or requires manual intervention
   - No "monitor-only" mode
   - Can't pause trading while keeping track of signals

4. **Reactive vs. Proactive:** Waits for scheduled time instead of responding to market

---

## 🏗️ Proposed Architecture

### Core Components

#### 1. **Signal Monitor Service** (`monitoring/signal_monitor.py`)

**Purpose:** Continuously track signals for portfolio + watchlist

**Functionality:**
```python
class SignalMonitor:
    """
    Monitors market signals and detects changes.

    Runs every 15-30 minutes during market hours (9:30 AM - 4 PM ET).
    """

    def __init__(self,
                 check_interval_minutes: int = 30,
                 watchlist: List[str] = None):
        self.interval = check_interval_minutes
        self.watchlist = watchlist or []
        self.signal_history = SignalHistory()
        self.change_detector = ChangeDetector()

    async def monitor_cycle(self):
        """Execute one monitoring cycle."""
        # 1. Get current portfolio positions
        # 2. Combine with watchlist
        # 3. Analyze all symbols
        # 4. Detect signal changes
        # 5. Log changes to history
        # 6. Trigger trades if system is active
```

**Features:**
- Monitors portfolio positions (what we own)
- Monitors watchlist (potential buys)
- Runs only during market hours (9:30 AM - 4 PM ET)
- Skips weekends and holidays
- Rate limiting: Max 1 check per stock per 15 minutes

---

#### 2. **Signal History Database** (`monitoring/signal_history.py`)

**Purpose:** Store all signal changes over time

**Schema:**
```json
{
  "signal_changes": [
    {
      "timestamp": "2026-01-01T10:30:00-05:00",
      "symbol": "GOOGL",
      "previous_signal": "BUY",
      "new_signal": "STRONG BUY",
      "previous_score": 68.5,
      "new_score": 73.8,
      "change_type": "UPGRADE",
      "urgency": "MEDIUM",
      "action_taken": null,
      "reason": "Momentum improved from 75 to 84"
    },
    {
      "timestamp": "2026-01-01T14:15:00-05:00",
      "symbol": "NVDA",
      "previous_signal": "STRONG BUY",
      "new_signal": "SELL",
      "previous_score": 75.2,
      "new_score": 42.3,
      "change_type": "CRITICAL_DOWNGRADE",
      "urgency": "CRITICAL",
      "action_taken": "SOLD 8 shares at $187.50",
      "reason": "Fundamentals collapsed, sentiment turned negative"
    }
  ],
  "current_signals": {
    "GOOGL": {
      "signal": "STRONG BUY",
      "score": 73.8,
      "last_updated": "2026-01-01T10:30:00-05:00",
      "confidence": "MEDIUM"
    }
  }
}
```

**Features:**
- Tracks every signal change (not just current state)
- Enables historical analysis
- Identifies patterns (e.g., "STRONG BUY lasted 3 days before dropping")

---

#### 3. **Change Detector** (`monitoring/change_detector.py`)

**Purpose:** Identify meaningful signal changes and assign urgency

**Signal Change Types:**

| Previous → New | Change Type | Urgency | Action |
|---------------|-------------|---------|--------|
| STRONG BUY → SELL | CRITICAL_DOWNGRADE | 🔴 CRITICAL | Sell immediately |
| STRONG BUY → WEAK SELL | CRITICAL_DOWNGRADE | 🔴 CRITICAL | Sell immediately |
| BUY → SELL | MAJOR_DOWNGRADE | 🟠 HIGH | Sell at next cycle |
| STRONG BUY → HOLD | DOWNGRADE | 🟡 MEDIUM | Monitor closely |
| HOLD → STRONG BUY | UPGRADE | 🟢 MEDIUM | Queue for buy |
| BUY → STRONG BUY | UPGRADE | 🟢 LOW | Queue for buy |
| STRONG BUY → STRONG BUY | NO_CHANGE | ⚪ NONE | Log score change |

**Urgency Levels:**
```python
class SignalUrgency:
    CRITICAL = "CRITICAL"      # Sell immediately (< 5 min)
    HIGH = "HIGH"              # Sell at next cycle (< 30 min)
    MEDIUM = "MEDIUM"          # Queue for execution (4 PM)
    LOW = "LOW"                # Monitor only
    NONE = "NONE"              # No action needed
```

---

#### 4. **Trade Trigger System** (`monitoring/trade_trigger.py`)

**Purpose:** Execute trades based on signal changes (only when active)

**Execution Logic:**
```python
class TradeTrigger:
    """
    Triggers trades based on signal changes.

    CRITICAL: Only executes if system_active = true
    """

    def process_signal_change(self, change: SignalChange):
        # Check if system is active
        if not self.is_system_active():
            logger.info(f"System inactive - logging change only: {change}")
            return

        # Execute based on urgency
        if change.urgency == "CRITICAL":
            self.execute_sell_immediately(change.symbol)
        elif change.urgency == "HIGH":
            self.queue_sell(change.symbol, priority="high")
        elif change.urgency == "MEDIUM":
            self.queue_buy(change.symbol)
```

**Safety Features:**
- Respects position limits
- Checks cash availability
- Only trades during market hours
- Rate limiting (max trades per hour)
- Circuit breaker (pause if > 10 signals change in 1 hour = market crash)

---

#### 5. **Active/Inactive Control** (`data/monitoring_config.json`)

**Purpose:** Master switch for automated trading

**Configuration:**
```json
{
  "system_active": false,
  "monitoring": {
    "enabled": true,
    "check_interval_minutes": 30,
    "market_hours_only": true,
    "watchlist": ["AAPL", "MSFT", "NVDA", "TSLA", "GOOGL"]
  },
  "execution": {
    "enabled_when_active": true,
    "immediate_sells_on_downgrade": true,
    "batch_buys_at_4pm": true,
    "max_trades_per_hour": 5
  },
  "notifications": {
    "log_all_changes": true,
    "alert_on_critical": false,
    "daily_summary": true
  }
}
```

**System States:**
1. **Active + Monitoring:** Monitors signals AND executes trades
2. **Inactive + Monitoring:** Monitors signals ONLY (no trades)
3. **Inactive + No Monitoring:** System paused (manual mode)

---

## 📊 Data Flow

### Monitoring Cycle (Every 30 Minutes)

```
1. TRIGGER (APScheduler)
   │
   ▼
2. CHECK: Is market open? (9:30 AM - 4 PM ET)
   │
   ├─ NO → Skip cycle
   │
   ▼
3. ANALYZE: Portfolio positions + Watchlist
   │
   ▼
4. COMPARE: Current signals vs. Last recorded signals
   │
   ▼
5. DETECT: Signal changes (upgrade/downgrade)
   │
   ▼
6. LOG: All changes to signal_history.json
   │
   ▼
7. EVALUATE: Urgency level (CRITICAL/HIGH/MEDIUM/LOW)
   │
   ▼
8. CHECK: Is system_active = true?
   │
   ├─ NO → Log only, skip execution
   │
   ▼
9. EXECUTE:
   ├─ CRITICAL → Sell immediately
   ├─ HIGH → Queue for next cycle
   └─ MEDIUM → Queue for 4 PM batch
```

---

## 🚀 Implementation Roadmap

### Phase 1: Foundation (Days 1-2)

**Files to Create:**
- `monitoring/__init__.py`
- `monitoring/signal_history.py`
- `monitoring/change_detector.py`
- `data/signal_history.json`
- `data/monitoring_config.json`

**Tasks:**
1. Create `SignalHistory` class
   - Load/save signal history from JSON
   - Track current signals for all monitored stocks
   - Log signal changes with timestamps

2. Create `ChangeDetector` class
   - Compare previous vs. current signals
   - Assign urgency levels
   - Generate change descriptions

3. Add tests
   - Test signal change detection
   - Test urgency assignment
   - Test history logging

---

### Phase 2: Monitoring Service (Days 3-4)

**Files to Create:**
- `monitoring/signal_monitor.py`
- `monitoring/monitoring_scheduler.py`

**Tasks:**
1. Create `SignalMonitor` class
   - Fetch portfolio positions
   - Analyze all symbols (portfolio + watchlist)
   - Detect signal changes
   - Log to history

2. Create monitoring scheduler
   - Run every 30 minutes (configurable)
   - Only during market hours (9:30 AM - 4 PM ET)
   - Skip weekends and holidays

3. Integrate with API startup
   - Start monitoring scheduler on API startup
   - Add graceful shutdown

---

### Phase 3: Trade Execution (Days 5-6)

**Files to Create:**
- `monitoring/trade_trigger.py`

**Tasks:**
1. Create `TradeTrigger` class
   - Check if system is active
   - Execute immediate sells on CRITICAL downgrades
   - Queue sells for HIGH urgency
   - Queue buys for MEDIUM urgency

2. Add safety features
   - Position limits
   - Cash availability check
   - Rate limiting
   - Circuit breaker

3. Integrate with paper portfolio
   - Use existing buy/sell functions
   - Log all automated trades

---

### Phase 4: API & Control (Days 7-8)

**API Endpoints:**
```
GET  /monitoring/status           # Get monitoring status
GET  /monitoring/signal-history   # Get signal change history
GET  /monitoring/current-signals  # Get current signals for all stocks
POST /monitoring/activate         # Activate trading (system_active = true)
POST /monitoring/deactivate       # Deactivate trading (monitor only)
POST /monitoring/watchlist        # Update watchlist
GET  /monitoring/statistics       # Signal change stats
```

**Tasks:**
1. Add monitoring endpoints to `api/main.py`
2. Create monitoring dashboard data
3. Add signal analytics

---

### Phase 5: Testing & Refinement (Days 9-10)

**Tasks:**
1. Run monitoring for 1 week in "inactive" mode
   - Verify signal changes are detected correctly
   - Check false positives/negatives
   - Tune urgency thresholds

2. Test with real portfolio
   - Activate trading for 1 stock only
   - Verify trades execute correctly
   - Check safety features

3. Full system test
   - Activate for full portfolio
   - Monitor for 1 trading day
   - Verify performance

---

## 📈 Expected Benefits

### 1. **Faster Reaction Time**
- **Before:** Holds losing position until 4 PM next day
- **After:** Sells within 5 minutes of downgrade

**Example:**
```
10:00 AM: NVDA downgrades from STRONG BUY (75) → SELL (42)
10:05 AM: System sells NVDA at $187 (saves $15/share vs 4 PM price of $172)
```

### 2. **Better Entry Points**
- **Before:** Buys at 4 PM price (often after day's move)
- **After:** Detects upgrade and queues for execution

**Example:**
```
11:00 AM: LLY upgrades to STRONG BUY (score 72)
04:00 PM: System buys LLY at $1,079 (vs $1,095 if checked next day)
```

### 3. **Signal Intelligence**
- Track how long signals persist
- Identify most reliable signals
- Optimize entry/exit timing

**Example Insights:**
```
- "STRONG BUY signals last average 8 days before reverting"
- "Downgrades from STRONG BUY → HOLD lead to -12% avg loss if held"
- "Upgrades to STRONG BUY return +18% over next month"
```

### 4. **Risk Management**
- Immediate exits on critical downgrades
- Prevents holding through crashes
- Preserves capital

---

## ⚠️ Risks & Mitigations

### Risk 1: Over-Trading
**Problem:** Signal changes frequently → too many trades → high costs

**Mitigation:**
- Rate limit: Max 5 trades/hour
- Minimum holding period: 3 days (don't sell if bought < 3 days ago)
- Only execute on >= 2 urgency levels change

### Risk 2: False Signals
**Problem:** Temporary signal change → bad trade

**Mitigation:**
- Require signal to persist for 2 consecutive checks (30 min)
- Only act on score changes >= 5 points
- Confidence level filter (ignore LOW confidence signals)

### Risk 3: API Rate Limiting
**Problem:** Analyzing 50 stocks every 30 min = 96 API calls/hour

**Mitigation:**
- Cache analysis results (15 min TTL)
- Prioritize portfolio positions > watchlist
- Use batch analysis where possible

### Risk 4: Market Volatility
**Problem:** All signals downgrade simultaneously (market crash)

**Mitigation:**
- Circuit breaker: Pause if > 50% portfolio downgrades in 1 hour
- Require manual confirmation for mass sells
- Alert user before executing

---

## 🎛️ Configuration Examples

### Conservative (Recommended for Start)
```json
{
  "system_active": false,
  "monitoring": {
    "check_interval_minutes": 60,
    "watchlist": ["GOOGL", "MRK"]
  },
  "execution": {
    "immediate_sells_on_downgrade": true,
    "batch_buys_at_4pm": true,
    "min_holding_period_days": 7
  }
}
```

### Aggressive (Active Trader)
```json
{
  "system_active": true,
  "monitoring": {
    "check_interval_minutes": 15,
    "watchlist": ["AAPL", "GOOGL", "MSFT", "NVDA", "TSLA", "META", "AMZN"]
  },
  "execution": {
    "immediate_sells_on_downgrade": true,
    "immediate_buys_on_strong_signals": true,
    "min_holding_period_days": 1
  }
}
```

### Monitor-Only (Evaluation Mode)
```json
{
  "system_active": false,
  "monitoring": {
    "enabled": true,
    "check_interval_minutes": 30
  },
  "execution": {
    "enabled_when_active": false
  },
  "notifications": {
    "daily_summary": true
  }
}
```

---

## 📊 Success Metrics

After 1 month of monitoring:

### Signal Tracking
- ✅ All signal changes logged to database
- ✅ 0 missed critical downgrades
- ✅ Signal history available for analysis

### Performance (if active)
- ✅ Reduced drawdown by 30% (faster exits)
- ✅ Improved entry timing by 15% (earlier buys)
- ✅ Sharpe ratio increase by 0.3+

### Reliability
- ✅ 99%+ monitoring uptime during market hours
- ✅ < 5 min response time on critical signals
- ✅ 0 false positive trades

---

## 🔧 API Usage Examples

### Check Monitoring Status
```bash
curl http://localhost:8010/monitoring/status
```

**Response:**
```json
{
  "monitoring_enabled": true,
  "system_active": false,
  "last_check": "2026-01-01T14:30:00-05:00",
  "next_check": "2026-01-01T15:00:00-05:00",
  "stocks_monitored": 12,
  "signal_changes_today": 3
}
```

### Activate Trading System
```bash
curl -X POST http://localhost:8010/monitoring/activate
```

**Response:**
```json
{
  "success": true,
  "system_active": true,
  "message": "Trading system activated. Will execute trades on signal changes."
}
```

### View Signal History
```bash
curl "http://localhost:8010/monitoring/signal-history?symbol=GOOGL&days=7"
```

**Response:**
```json
{
  "symbol": "GOOGL",
  "changes": [
    {
      "timestamp": "2026-01-01T10:30:00-05:00",
      "from": "BUY",
      "to": "STRONG BUY",
      "score_change": "+5.3",
      "action": null
    }
  ],
  "current_signal": "STRONG BUY",
  "days_at_current": 0.2
}
```

---

## 🚦 Next Steps

### For User Review:

1. **Review this design document**
   - Does the architecture make sense?
   - Any missing features or concerns?
   - Preferred monitoring interval (15 min / 30 min / 60 min)?

2. **Decide on initial configuration**
   - Start in "monitor-only" mode (recommended)
   - Or activate trading immediately?
   - Which stocks to include in watchlist?

3. **Approve implementation timeline**
   - Full implementation: 7-10 days
   - MVP (monitoring only): 3-4 days
   - Which approach?

### Questions for Clarification:

1. **Monitoring Frequency:** Every 15 min (aggressive) or 30 min (balanced) or 60 min (conservative)?

2. **Watchlist Size:** How many stocks to monitor beyond portfolio? (5 / 10 / 20?)

3. **Execution Speed:**
   - Immediate sells on downgrades? (recommended: YES)
   - Immediate buys on upgrades? (recommended: NO, batch at 4 PM)

4. **Storage:** JSON files (simple) or SQLite database (scalable)?

5. **Starting Mode:** Monitor-only first (safe) or active trading (aggressive)?

---

**Ready to proceed?** Let me know your preferences and I'll start implementation!
