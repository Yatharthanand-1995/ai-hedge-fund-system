# 5-Year Backtest Comparison Setup

**Date**: 2025-10-14
**Status**: ⏳ RUNNING
**ETA**: 10-15 minutes

---

## Comparison Goal

**Test if improved sell discipline can beat 190% baseline return with lower losses**

---

## Test Configuration - IDENTICAL for Fair Comparison

### Baseline (Original System)
- **Return**: 190% over 5 years (2.9x money)
- **Period**: ~2020-2025 (5 years)
- **Universe**: 10 stocks (AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA, V, JPM, UNH)
- **Portfolio**: Top 8 stocks, monthly rebalance
- **Initial Capital**: $100,000
- **Risk Management**: ❌ DISABLED by default
- **Momentum Veto**: ❌ NONE
- **Stop-Losses**: ❌ NONE

### Improved System (Current Test)
- **Return**: ⏳ TESTING NOW
- **Period**: 2020-10-15 to 2025-10-14 (5 years) ✅ SAME
- **Universe**: 10 stocks (AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA, V, JPM, UNH) ✅ SAME
- **Portfolio**: Top 8 stocks, monthly rebalance ✅ SAME
- **Initial Capital**: $100,000 ✅ SAME
- **Risk Management**: ✅ ENABLED (15% stop-loss, 12% drawdown)
- **Momentum Veto**: ✅ ACTIVE (filter M<35 or M<40+F<45)
- **Stop-Losses**: ✅ ACTIVE (15% per position)

---

## Expected Improvements

### 1. Higher Returns (Target: >190%)
**Why**: Momentum veto prevents holding declining stocks
- **Baseline**: Held all stocks regardless of momentum
- **Improved**: Filters weak momentum stocks before buying

**Early Evidence (Oct 2020)**:
```
JPM: Score=40.8, M=33 → 🛑 FILTERED (momentum veto)
Result: Avoided holding JPM during downtrend
```

### 2. Lower Maximum Drawdown (Target: <-20%)
**Why**: Stop-losses limit downside to -15% per position
- **Baseline**: No stop-losses → positions could drop -20% to -30%
- **Improved**: 15% stop-loss → max -15% per position (plus some slippage)

**Expected Impact**: -3% to -5% drawdown reduction

### 3. Lower Volatility
**Why**: Momentum veto reduces exposure to volatile declining stocks
- **Baseline**: Full exposure to all stocks
- **Improved**: Reduced exposure during downtrends

**Expected Impact**: -2% to -4% volatility reduction

### 4. Higher Sharpe Ratio (Target: >1.5)
**Why**: Same/higher returns + lower drawdown + lower volatility = better risk-adjusted returns
- **Baseline Sharpe**: Unknown (likely 1.0-1.3)
- **Improved Sharpe**: Targeting 1.5+

---

## Key Metrics to Compare

| Metric | Baseline | Improved (Testing) | Goal |
|--------|----------|-------------------|------|
| **Total Return** | 190% | ⏳ | >190% (+0-10%) |
| **Final Value** | $290,000 | ⏳ | >$290,000 |
| **Max Drawdown** | ~-20%? | ⏳ | <-17% (-3-5%) |
| **Sharpe Ratio** | ~1.2? | ⏳ | >1.5 (+0.3+) |
| **Volatility** | ~22%? | ⏳ | <20% (-2-4%) |
| **CAGR** | ~24% | ⏳ | >24% |
| **Losses Avoided** | 0 | ⏳ | $20,000+ |

---

## What We're Testing

### Hypothesis 1: Returns Should Match or Exceed 190%
**Logic**:
- Momentum veto prevents buying declining stocks
- Stop-losses limit downside on existing positions
- Combined effect: fewer large losses = higher returns

**Counter-risk**:
- Momentum veto might filter out stocks that later recover
- Stop-losses might exit positions that later bounce back
- Net effect could be slightly lower returns BUT with much better risk metrics

### Hypothesis 2: Risk Metrics Should Improve Significantly
**Logic**:
- 15% stop-losses cap downside → lower drawdown
- Momentum veto reduces volatile holdings → lower volatility
- Combined: much better Sharpe ratio even if returns are similar

**Success Criteria**:
- If returns = 190% but Sharpe improves from 1.2 → 1.5: **WIN**
- If returns = 180% but Sharpe improves from 1.2 → 1.8: **STILL WIN**
- Only fail if both returns AND Sharpe drop significantly

### Hypothesis 3: Loss Avoidance Should Be Significant
**Logic**:
- Count stocks filtered by momentum veto over 60 rebalances
- Estimate avoided losses from NOT holding those stocks
- Should be $20,000+ in total avoided losses

---

## Progress Tracking

### Backtest Status: ⏳ RUNNING

**Current Progress**:
- ✅ Downloaded data for 11 symbols (10 stocks + SPY)
- ✅ Generated 60 monthly rebalance dates
- ✅ Started simulation (Oct 2020)
- ⏳ Processing 5 years of monthly rebalances
- ⏳ Calculating final metrics

**Early Observations**:
1. **First rebalance (Oct 2020)**: JPM filtered (M=33) ✅
2. **Momentum veto already working**: System avoiding weak stocks ✅
3. **Risk management active**: Stop-losses enabled ✅

**Monitor Progress**:
```bash
tail -f /tmp/5year_improved_output.log
```

---

## Why This Comparison Matters

### For Production Deployment:
1. **Validates improvements** on exact same data as baseline
2. **Proves ROI** of momentum veto + stop-losses
3. **Shows risk reduction** even if returns are similar
4. **Demonstrates capital preservation** during bear markets

### For User Confidence:
1. **Apples-to-apples comparison** (same stocks, same period)
2. **Clear before/after** metrics
3. **Quantified improvement** in dollars and percentages
4. **Battle-tested** on 5 years including COVID crash and 2022 bear

---

## Expected Timeline

- **Start**: 2025-10-14 22:08 (just started)
- **Duration**: 10-15 minutes for 60 monthly rebalances
- **ETA**: 2025-10-14 22:20-22:25
- **Log**: `/tmp/5year_improved_output.log`

---

## Next Steps After Completion

1. **Extract Results**:
   - Total return vs 190% baseline
   - Max drawdown comparison
   - Sharpe ratio improvement
   - Momentum veto statistics

2. **Calculate Impact**:
   - Extra profit in dollars
   - Avoided losses from momentum veto
   - Risk-adjusted return improvement

3. **Create Final Report**:
   - Side-by-side comparison table
   - Momentum veto effectiveness
   - Loss reduction analysis
   - Production deployment recommendation

4. **Update Documentation**:
   - Add 5-year results to SELL_DISCIPLINE_IMPROVEMENTS.md
   - Update BACKTEST_RESULTS with comparison
   - Create executive summary for stakeholders

---

## Success Metrics

### 🏆 CLEAR WIN if:
- Return >200% (beat baseline by 10%+)
- Sharpe >1.5 (excellent risk-adjusted returns)
- Max drawdown <-15% (significant improvement)

### ✅ SOLID WIN if:
- Return >190% (match/beat baseline)
- Sharpe >1.3 (good improvement)
- Max drawdown <-18% (moderate improvement)

### 🤔 MIXED RESULTS if:
- Return 180-190% (slight underperformance)
- BUT Sharpe >1.5 (much better risk-adjusted)
- AND Max drawdown <-15% (much lower risk)
→ Still a win for risk-conscious investors!

### ❌ NEEDS REVIEW if:
- Return <180% (significant underperformance)
- AND Sharpe <1.2 (no risk improvement)
- This would suggest momentum veto is too aggressive

---

## Current Status

⏳ **Backtest is running now...**

Check progress with:
```bash
# See live progress
tail -f /tmp/5year_improved_output.log

# Check if still running
ps aux | grep run_5year_improved

# Count momentum veto events so far
grep "Momentum veto filtered out" /tmp/5year_improved_output.log | wc -l
```

---

**Last Updated**: 2025-10-14 22:10
**Next Update**: When backtest completes (~22:20-22:25)
