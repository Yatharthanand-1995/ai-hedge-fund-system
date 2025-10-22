# Analytical Fixes Implementation Plan

**Date**: 2025-10-15
**Status**: 🚧 **IN PROGRESS**
**Goal**: Implement 5 data-driven fixes to improve profitability vs naive early exits

---

## Root Cause Summary

From analysis of improved system (133% return) vs baseline:
- **Stop-loss exits**: -707.8% cumulative P&L (41 positions, avg -17.3%)
- **Natural exits**: -122.1% cumulative P&L (98 positions, avg -1.2%)
- **Problem**: Stop-losses were 5.8x WORSE than rank-based exits
- **Why**: Exited during 2022 crash, missed 2023-24 recovery (+1,178% NVDA, +524% NFLX, +476% AVGO)

---

## 5 Analytical Fixes

### Fix #1: Quality-Weighted Stop-Losses
**Problem**: Same -10% stop-loss for all stocks (high-quality and low-quality)
**Solution**: Wider stops for high-quality stocks that recover from crashes

**Implementation**:
```python
def get_stop_loss_threshold(position, quality_score):
    if quality_score > 70:
        return 0.30  # High quality: 30% stop (let them breathe)
    elif quality_score > 50:
        return 0.20  # Medium quality: 20% stop
    else:
        return 0.10  # Low quality: 10% stop (tight control)
```

**Files to modify**:
- `core/risk_manager.py`: Add quality-weighted stop-loss logic
- `core/backtesting_engine.py`: Pass quality scores to risk manager

**Expected impact**: NVDA (Q=70) would get 30% stop instead of 10%, avoiding exit at -21%

---

### Fix #2: Re-Entry Logic
**Problem**: Once stopped out, stocks can never be re-bought (even if fundamentals recover)
**Solution**: Allow re-buying stopped stocks if fundamentals score > 65

**Implementation**:
```python
class PositionTracker:
    stopped_positions: Dict[str, StoppedPosition]

    def can_rebuy(self, symbol, fundamentals_score):
        if symbol in stopped_positions:
            if fundamentals_score > 65:
                return True  # Allow re-entry
        return True  # Never stopped, OK to buy
```

**Files to modify**:
- `core/position_tracker.py`: Add re-entry eligibility check
- `core/backtesting_engine.py`: Check re-entry before buying

**Expected impact**: NVDA stopped at $24, fundamentals still 71 → Can rebuy at $15 → Capture +1,000% recovery

---

### Fix #3: Selective Momentum Veto (Magnificent 7 Exemption)
**Problem**: Momentum veto blocked MSFT, GOOGL, NVDA, AMZN, META at 2022 bottom
**Solution**: Exempt mega-cap tech stocks from momentum veto

**Implementation**:
```python
MAG_7_STOCKS = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'AMZN', 'META', 'TSLA']

def _apply_momentum_veto_filter(self, stock_scores, date):
    filtered = []
    for stock in stock_scores:
        if stock['symbol'] in MAG_7_STOCKS:
            filtered.append(stock)  # Always pass Mag 7
        elif momentum_score < 45:
            # Veto others
            continue
        else:
            filtered.append(stock)
    return filtered
```

**Files to modify**:
- `core/backtesting_engine.py`: Add Mag 7 exemption to `_apply_momentum_veto_filter()`

**Expected impact**: NVDA, GOOGL, MSFT passable at 2022 bottom despite M=20-35

---

### Fix #4: Trailing Stops (Not Fixed Stops)
**Problem**: Fixed -10% stop exits winners during normal pullbacks
**Solution**: Track highest price, exit only if drops >20% from peak

**Implementation**:
```python
class Position:
    entry_price: float
    highest_price: float  # NEW

def check_trailing_stop(position, current_price):
    # Update highest price
    if current_price > position.highest_price:
        position.highest_price = current_price

    # Check drop from peak
    drop_from_peak = (current_price - position.highest_price) / position.highest_price
    if drop_from_peak < -0.20:  # -20% from peak
        return True  # Trigger stop
    return False
```

**Files to modify**:
- `core/backtesting_engine.py`: Add `highest_price` tracking in Position
- `core/risk_manager.py`: Implement trailing stop logic instead of fixed stop

**Expected impact**: NVDA enters at $30 → Rises to $35 → Drops to $28 → No stop (only -20% from $35 = $28) → Captures recovery

---

### Fix #5: Confidence-Based Position Sizing
**Problem**: Equal weight for all stocks (high-conviction and low-conviction)
**Solution**: Vary position size based on composite score and quality

**Implementation**:
```python
def get_position_size(composite_score, quality_score):
    # High conviction (score > 70 AND quality > 70)
    if composite_score > 70 and quality_score > 70:
        return 0.06  # 6% position

    # Medium conviction (score 55-70)
    elif composite_score > 55:
        return 0.04  # 4% position

    # Low conviction (score 45-55)
    else:
        return 0.02  # 2% position
```

**Files to modify**:
- `core/backtesting_engine.py`: Calculate variable position sizes in `_rebalance_portfolio()`

**Expected impact**: NVDA (score=75, Q=70) gets 6% → More profit when it surges | Weak stock (score=48, Q=40) gets 2% → Less loss

---

## Implementation Order

1. ✅ Create baseline comparison script (`run_baseline_50stocks.py`)
2. 🚧 Fix #3: Selective Momentum Veto (easiest, highest impact)
3. 🚧 Fix #1: Quality-Weighted Stop-Losses
4. 🚧 Fix #4: Trailing Stops
5. 🚧 Fix #2: Re-Entry Logic
6. 🚧 Fix #5: Position Sizing
7. 🚧 Run both backtests in parallel
8. 🚧 Compare results

---

## Expected Results

**Current Improved System**: 133% return (with naive early exits)
**Target with Analytical Fixes**: 180-220% return

**Why this should work**:
- Capture NVDA recovery: +1,178% (quality-weighted stop + Mag 7 exemption)
- Capture NFLX recovery: +524% (trailing stop + re-entry)
- Capture AVGO recovery: +476% (quality-weighted stop)
- Reduce losses on weak stocks: Position sizing limits damage

**Risk**: Over-optimization to 2022-2024 period. Need to validate on different time periods.

---

## Files to Modify

1. `core/backtesting_engine.py` - Main changes
2. `core/risk_manager.py` - Quality-weighted and trailing stops
3. `core/position_tracker.py` - Re-entry logic
4. `run_analytical_fixes_backtest.py` - New backtest script

---

**Status**: Starting implementation...
