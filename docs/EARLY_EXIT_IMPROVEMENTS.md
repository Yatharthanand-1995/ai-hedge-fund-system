# Early Exit Improvements for Loss Prevention

**Date**: 2025-10-15
**Status**: ✅ **IMPLEMENTED & TESTING**
**Goal**: Beat 190% baseline with better loss prevention

---

## Problem Identified

The original system (190% baseline) had:
- **No momentum early warning** - waited until M<35 (too late)
- **Loose stop-losses** - 20% per position (too much loss)
- **No score deterioration tracking** - held declining stocks too long

**Result**: Good returns (190%) but **excessive losses** on declining positions

---

## 3 Strategic Improvements Implemented

### 1. ✅ Tighter Stop-Loss (-10% instead of -20%)

**What Changed:**
- **Old**: 20% stop-loss per position (15% in some configs)
- **New**: **10% stop-loss** per position

**Why This Helps:**
- Exit losers **50% earlier** (at -10% instead of -20%)
- Save **10% per losing position**
- More capital preserved for next winners

**Files Modified:**
- `core/backtesting_engine.py` line 60: Default risk_limits
- `run_dashboard_backtest.py` line 58: Dashboard config

**Expected Impact:**
- Reduce average loss per stopped position from -15-20% to -10-12%
- Preserve ~5-8% more capital across all stopped positions

---

### 2. ✅ Momentum Early Warning (M<45 instead of M<35)

**What Changed:**
- **Old**: Momentum veto at M<35 (strong downtrend)
- **New**: **Momentum veto at M<45** (early weakness detection)

**Additional**: Also veto if M<50 AND F<45 (both agents showing weakness)

**Why This Helps:**
- **Catches decline earlier** - before stock drops 10-15%
- **Prevents buying weak stocks** - filters before portfolio entry
- **Exit existing positions faster** - if they weaken to M<45

**Files Modified:**
- `core/backtesting_engine.py` lines 609-662: `_apply_momentum_veto_filter()`

**Expected Impact:**
- Filter **2-3x more stocks** with weak momentum
- Avoid **10-15% of declines** by exiting earlier
- Reduce exposure to declining stocks by 30-40%

**Real Example from Log:**
```
🛑 2021-07-15 - Momentum veto for INTC: Momentum weakening (M=25, threshold=45)
🛑 2021-07-15 - Momentum veto for WMT: Momentum weakening (M=30, threshold=45)
```

---

### 3. ✅ Score Deterioration Tracking (>20 point drop)

**What Changed:**
- **Old**: Only sold if stock fell out of top 20 ranking
- **New**: **Force sell if score drops >20 points** from entry, even if still in top 20

**How It Works:**
1. Track entry score when buying (e.g., bought at score=72)
2. Check score at each rebalance (e.g., now score=50)
3. If drop >20 points (72→50 = 22 point drop), **force sell**

**Why This Helps:**
- **Catches fundamental deterioration** before it becomes a loss
- **Exit declining stocks proactively** rather than reactively
- **Prevents "slow bleeds"** where score declines gradually

**Files Modified:**
- `core/backtesting_engine.py` line 76: Added `entry_score` field to Position
- `core/backtesting_engine.py` line 535: Store entry_score when buying
- `core/backtesting_engine.py` lines 427-477: Score deterioration check logic

**Expected Impact:**
- Force sell **5-10 positions per year** with deteriorating scores
- Prevent **5-10% additional losses** from held declining positions
- Exit **1-2 quarters earlier** than rank-based system

**Example Scenario:**
```
Entry:  AAPL bought at score=75 (rank #5)
Q1:     AAPL score=68 (rank #8)  ← No action yet (drop=7)
Q2:     AAPL score=54 (rank #12) ← FORCE SELL! (drop=21 points)
        Old system: Would hold until rank #21+
        New system: Sell at -5% loss instead of -15% loss
```

---

## Combined Expected Impact

### Loss Reduction:
1. **Tighter stop-loss**: Save 5-8% per stopped position
2. **Momentum early warning**: Avoid 10-15% of declines
3. **Score deterioration**: Prevent 5-10% additional losses

**Total**: **20-30% reduction in losses** from declining positions

### Return Enhancement:
- If baseline had 20 losing positions with avg -15% loss = **-300% cumulative loss**
- With improvements: avg -8% loss = **-160% cumulative loss**
- **Net improvement**: +140% preserved capital → **reinvested in winners**

### Target Performance:
- **Baseline**: 190% return with -300% cumulative losses
- **Improved**: **200-220% return** with -160% cumulative losses (**Goal: beat 190%**)

---

## Implementation Details

### Position Lifecycle with Improvements

#### Entry:
1. ✅ Pass momentum veto (M≥45)
2. ✅ Pass score veto (S≥45)
3. ✅ Rank in top 20
4. **Store entry score** for tracking

#### Holding Period - Daily Checks:
1. Monitor for **-10% stop-loss** (tighter)
2. Track max price while held
3. Monitor recovery after stop-loss

#### Rebalancing - Quarterly Checks:
1. **Momentum early warning**: Sell if M<45
2. **Score deterioration**: Sell if drop >20 points
3. Rank-based exit: Sell if falls out of top 20
4. Regime-driven reduction: Reduce holdings in BEAR markets

#### Exit Reasons Tracked:
- STOP_LOSS (-10% triggered)
- MOMENTUM_VETO (M<45)
- SCORE_DETERIORATION (>20 point drop)
- SCORE_DROPPED (fell out of top 20)
- REGIME_REDUCTION (bear market defensive)

---

## Backtest Configuration

### Test Parameters:
- **Period**: 2020-10-16 to 2025-10-15 (5 years)
- **Universe**: 50 stocks (US_TOP_100_STOCKS)
- **Portfolio**: Top 20 stocks
- **Rebalancing**: Quarterly
- **Initial Capital**: $10,000
- **Benchmark**: 190% (baseline without improvements)

### Risk Management:
- Position stop-loss: **10%** (was 20%)
- Max drawdown: 15%
- Cash buffer on drawdown: 50%

### Agent Weights (Backtest Mode):
- Momentum: 50%
- Quality: 40%
- Fundamentals: 5%
- Sentiment: 5%

---

## Expected Results

### Success Metrics:

**🏆 CLEAR WIN if:**
- Return >200% (beat baseline by 10%+)
- Max drawdown <-18% (3% improvement)
- Stop-loss count 2-3x higher (more active management)
- Momentum veto events 2-3x higher (earlier exits)

**✅ SOLID WIN if:**
- Return >190% (match/beat baseline)
- Max drawdown <-20% (match baseline)
- Sharpe ratio >1.2 (better risk-adjusted returns)
- Demonstrable loss reduction from early exits

**🤔 MIXED RESULTS if:**
- Return 180-190% (slightly lower)
- BUT Max drawdown <-15% (much better)
- AND Sharpe ratio >1.3 (better risk-adjusted)
- This is still a WIN for risk-conscious investors

---

## Comparison Framework

### What We're Testing:

| Metric | Baseline (No Protection) | Improved (3 Enhancements) | Goal |
|--------|--------------------------|--------------------------|------|
| **Total Return** | 190% | ⏳ Testing | >190% |
| **Final Value** | $29,000 | ⏳ Testing | >$29,000 |
| **Max Drawdown** | -22.5% | ⏳ Testing | <-20% |
| **Sharpe Ratio** | 1.54 | ⏳ Testing | >1.5 |
| **Stop-Loss Events** | Few/None | ⏳ Testing | 40-60 (proactive) |
| **Momentum Veto** | ~100-150 | ⏳ Testing | 200-300 (2x more) |
| **Score Deterioration** | N/A | ⏳ Testing | 20-40 events |

---

## Monitoring Progress

### Check Backtest Status:
```bash
# Monitor live progress
tail -f /tmp/improved_backtest_final.log

# Check if running
ps aux | grep run_dashboard_backtest

# Count momentum veto events so far
grep "Momentum veto filtered out" /tmp/improved_backtest_final.log | wc -l

# Count stop-loss events
grep "Stop-loss triggered" /tmp/improved_backtest_final.log | wc -l

# Count score deterioration events
grep "DETERIORATION SELL" /tmp/improved_backtest_final.log | wc -l
```

### Key Log Patterns to Watch:
```
🛑 Momentum veto for SYMBOL: Momentum weakening (M=XX, threshold=45)
📉 DETERIORATION SELL: SYMBOL - Entry score XX → Current XX (drop: XX points)
🛑 RISK: Sold SYMBOL - STOP_LOSS (loss: -XX%)
```

---

## Technical Implementation

### Code Changes Summary:

**1. Tighter Stop-Loss:**
```python
# core/backtesting_engine.py:60
risk_limits = RiskLimits(
    position_stop_loss=0.10,  # Changed from 0.15/0.20
    ...
)
```

**2. Momentum Early Warning:**
```python
# core/backtesting_engine.py:643
if momentum_score < 45:  # Changed from <35
    veto_reason = "Momentum weakening"
elif momentum_score < 50 and fundamentals_score < 45:  # Added
    veto_reason = "Weak momentum + weak fundamentals"
```

**3. Score Deterioration:**
```python
# core/backtesting_engine.py:76
@dataclass
class Position:
    entry_score: float = 50.0  # NEW field

# core/backtesting_engine.py:432-474
for position in self.portfolio:
    score_drop = position.entry_score - current_score
    if score_drop > 20:  # NEW check
        # Force sell
```

---

## Next Steps

### After Backtest Completes (~15 minutes):

1. **Extract Results:**
   - Final return vs 190% baseline
   - Max drawdown comparison
   - Stop-loss statistics
   - Momentum veto statistics
   - Score deterioration statistics

2. **Calculate Impact:**
   - Loss reduction in dollars
   - Extra profit from preserved capital
   - Early exit effectiveness

3. **Create Final Report:**
   - Side-by-side comparison table
   - Win/loss analysis
   - Risk-adjusted return improvement
   - Production deployment recommendation

---

## Production Deployment

### If Results Are Positive:

These improvements should be:
- ✅ Kept in `core/backtesting_engine.py` (already integrated)
- ✅ Kept in `run_dashboard_backtest.py` (already integrated)
- ✅ Applied to live system (same risk_limits and momentum thresholds)

### Configuration for Live System:
```python
# In production code
risk_limits = RiskLimits(
    position_stop_loss=0.10,      # 10% stop-loss
    max_portfolio_drawdown=0.15,  # 15% max drawdown
)

# Momentum veto thresholds
MOMENTUM_VETO_THRESHOLD = 45  # Early warning
SCORE_DETERIORATION_THRESHOLD = 20  # Force sell
```

---

**Status**: ⏳ Backtest running (PID 13233)
**ETA**: 15 minutes
**Log**: `/tmp/improved_backtest_final.log`

**Last Updated**: 2025-10-15 23:35
**Next Update**: When backtest completes (~23:50)
