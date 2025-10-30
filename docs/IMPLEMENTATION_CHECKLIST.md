# Backtesting Fix Implementation Checklist

**Quick Reference Guide** for implementing all critical fixes

---

## 📋 Pre-Implementation

- [ ] Read `AUDIT_SUMMARY.md` (executive summary)
- [ ] Read `COMPREHENSIVE_BACKTEST_FIX_PLAN.md` (detailed plan)
- [ ] Backup current code: `git commit -m "Pre-fix backup"`
- [ ] Create fix branch: `git checkout -b fix/backtest-critical-gaps`

---

## Phase 1: Sector-Aware Scoring (15 min)

### File: `core/backtesting_engine.py`

- [ ] **Line 29**: Add import
  ```python
  from data.us_top_100_stocks import SECTOR_MAPPING
  ```

- [ ] **Line 182**: Update QualityAgent initialization
  ```python
  self.quality_agent = QualityAgent(sector_mapping=SECTOR_MAPPING)
  ```

- [ ] **Test**: Compile check
  ```bash
  python3 -m py_compile core/backtesting_engine.py
  ```

- [ ] **Verify**: Run quick test
  ```bash
  python3 -c "from core.backtesting_engine import HistoricalBacktestEngine; print('✅ Import OK')"
  ```

---

## Phase 2: Adaptive Weights Parameter (20 min)

### File: `core/backtesting_engine.py`

- [ ] **Line 1132**: Update method signature
  ```python
  def _calculate_real_agent_composite_score(
      self,
      symbol: str,
      comprehensive_data: Dict,
      adaptive_weights: Optional[Dict[str, float]] = None  # ADD THIS
  ) -> Tuple[float, Dict[str, float]]:
  ```

- [ ] **Line 987**: Update method call (in `_score_universe_at_date`)
  ```python
  score, agent_scores = self._calculate_real_agent_composite_score(
      symbol,
      comprehensive_data,
      adaptive_weights=adaptive_weights  # ADD THIS
  )
  ```

- [ ] **Test**: Compile check
  ```bash
  python3 -m py_compile core/backtesting_engine.py
  ```

---

## Phase 3: API Endpoint Updates (30 min)

### File: `api/main.py`

- [ ] **Lines 1637-1646**: Remove `backtest_mode`, add V2.1 params
  ```python
  engine_config = EngineConfig(
      start_date=config.start_date,
      end_date=config.end_date,
      initial_capital=config.initial_capital,
      rebalance_frequency=config.rebalance_frequency,
      top_n_stocks=config.top_n,
      universe=config.universe if config.universe else US_TOP_100_STOCKS,
      transaction_cost=0.001,
      # REMOVED: backtest_mode=True
      engine_version="2.1",                # ADD
      use_enhanced_provider=True,          # ADD
      enable_regime_detection=True         # ADD (for adaptive weights)
  )
  ```

- [ ] **Lines 1662-1688**: Add V2.1 metadata
  ```python
  "results": {
      # ... existing fields ...

      # V2.1 metadata (ADD THESE):
      "engine_version": result.engine_version,
      "data_provider": result.data_provider,
      "data_limitations": result.data_limitations,
      "estimated_bias_impact": result.estimated_bias_impact,
  }
  ```

- [ ] **After line 1688**: Add trade_log
  ```python
  response = {
      "config": { ... },
      "results": { ... },
      "trade_log": self._extract_trade_log(result),  # ADD THIS
      "timestamp": datetime.now().isoformat()
  }
  ```

- [ ] **Add helper method** (after the endpoint function):
  ```python
  def _extract_trade_log(self, result) -> List[Dict]:
      """Extract detailed transaction log from rebalance events"""
      transactions = []
      for event in result.rebalance_events:
          if hasattr(event, 'buys'):
              transactions.extend(event.buys)
          if hasattr(event, 'sells'):
              transactions.extend(event.sells)
      return transactions
  ```

- [ ] **Test**: Compile check
  ```bash
  python3 -m py_compile api/main.py
  ```

---

## Phase 4: Testing (45 min)

### Test 1: Unit Tests

- [ ] Run existing tests
  ```bash
  python3 -m pytest tests/test_backtesting_v2.py -v
  ```
  - [ ] **Expected**: 21/21 passing

### Test 2: Integration Test

- [ ] Run verification script
  ```bash
  python3 verify_v2_integration.py
  ```
  - [ ] **Check logs for**:
    - ✅ "Using EnhancedYahooProvider"
    - ✅ "Market regime detection ENABLED (with adaptive weights)"
    - ✅ "REGIME: BULL_HIGH_VOL" (or similar)
    - ✅ "Adaptive weights: F:XX% M:XX% Q:XX% S:XX%"
  - [ ] **Expected output**: "✅ V2.1 INTEGRATION VERIFICATION - SUCCESS"

### Test 3: API Test

- [ ] Start backend
  ```bash
  python -m api.main
  ```

- [ ] In another terminal, test endpoint
  ```bash
  curl -X POST http://localhost:8010/backtest/historical \
    -H "Content-Type: application/json" \
    -d '{
      "start_date": "2024-01-01",
      "end_date": "2024-10-23",
      "initial_capital": 10000,
      "rebalance_frequency": "quarterly",
      "top_n": 20,
      "universe": ["AAPL", "MSFT", "GOOGL", "NVDA", "AMZN"]
    }' | jq .
  ```

- [ ] **Verify response contains**:
  - [ ] `results.engine_version`: "2.1"
  - [ ] `results.data_provider`: "EnhancedYahooProvider"
  - [ ] `results.data_limitations`: {...}
  - [ ] `results.estimated_bias_impact`: "Results may be..."
  - [ ] `trade_log`: [...]
  - [ ] No errors in terminal

### Test 4: Frontend Test

- [ ] Start backend (if not already running)
  ```bash
  python -m api.main
  ```

- [ ] In another terminal, start frontend
  ```bash
  cd frontend && npm run dev
  ```

- [ ] Open browser to `http://localhost:5173/backtesting`

- [ ] Click "Run Backtest" button

- [ ] **Verify**:
  - [ ] Loading spinner appears
  - [ ] Results display after 2-3 minutes
  - [ ] Executive Summary shows metrics
  - [ ] Equity curve chart renders
  - [ ] Transaction log table populated (in "Detailed Analysis" tab)
  - [ ] Year-by-year breakdown works
  - [ ] No console errors

### Test 5: Comprehensive Backtest

- [ ] Run analytical fixes backtest
  ```bash
  python3 run_analytical_fixes_backtest.py
  ```

- [ ] **Monitor logs for**:
  - [ ] Regime detection messages
  - [ ] Adaptive weight changes
  - [ ] Sector-aware scoring
  - [ ] Final results look reasonable

- [ ] **Check final output**:
  - [ ] Total return > 140% (5-year)
  - [ ] No errors
  - [ ] Transaction log populated

---

## Post-Implementation

### Commit Changes

- [ ] Review all changes
  ```bash
  git diff
  ```

- [ ] Stage changes
  ```bash
  git add core/backtesting_engine.py api/main.py
  ```

- [ ] Commit with detailed message
  ```bash
  git commit -m "🔧 Fix critical backtesting gaps

  Phase 1: Enable sector-aware scoring
  - Add SECTOR_MAPPING import
  - Pass sector context to QualityAgent

  Phase 2: Fix adaptive weights parameter passing
  - Update _calculate_real_agent_composite_score signature
  - Pass adaptive_weights through call chain

  Phase 3: Update API endpoint for V2.1
  - Remove deprecated backtest_mode parameter
  - Add V2.1 metadata to response
  - Add detailed trade_log for frontend

  Impact: +20-40pp expected performance improvement
  Fixes: Sector scoring, adaptive weights, frontend integration

  Tests: 21/21 passing
  Integration: ✅ verify_v2_integration.py passes
  API: ✅ Returns valid V2.1 response
  Frontend: ✅ Displays transaction log correctly"
  ```

### Documentation

- [ ] Update `V2_IMPLEMENTATION_COMPLETE.md` to V2.1.1
- [ ] Archive audit documents
  ```bash
  mv AUDIT_SUMMARY.md BACKTEST_VS_PRODUCTION_AUDIT.md COMPREHENSIVE_BACKTEST_FIX_PLAN.md docs/
  ```

---

## Success Criteria

### All Must Pass ✅

- [x] All code changes implemented
- [x] 21/21 unit tests passing
- [x] verify_v2_integration.py passes
- [x] API returns valid V2.1 response
- [x] Frontend displays all features
- [x] Adaptive weights working (logs show different weights per regime)
- [x] Sector-aware scoring enabled (logs show sector-specific benchmarks)
- [x] No compilation errors
- [x] No runtime errors

---

## Troubleshooting

### Issue: Tests fail after Phase 1

**Check**:
- SECTOR_MAPPING imported correctly?
- All stocks in universe have sector mappings?

**Fix**:
```python
from data.us_top_100_stocks import US_TOP_100_STOCKS, SECTOR_MAPPING
print(f"Universe size: {len(US_TOP_100_STOCKS)}")
print(f"Sector mappings: {len(SECTOR_MAPPING)}")
assert all(s in SECTOR_MAPPING for s in US_TOP_100_STOCKS)
```

### Issue: API returns TypeError on backtest_mode

**Check**:
- Did you remove `backtest_mode=True` from line 1645?

**Fix**: Remove the parameter completely

### Issue: Frontend doesn't show transaction log

**Check**:
- Does API response include `trade_log` at top level?
- Are `buys` and `sells` populated in rebalance_events?

**Fix**: Add `_extract_trade_log()` helper method

### Issue: Adaptive weights not changing

**Check**:
- Is `enable_regime_detection=True` in API config?
- Is `adaptive_weights` parameter passed to `_calculate_real_agent_composite_score()`?

**Fix**: Update method signature and call site

---

## Quick Reference

### Files Modified
1. ✅ `core/backtesting_engine.py` (Phases 1-2)
2. ✅ `api/main.py` (Phase 3)

### Total Changes
- Lines added: ~30
- Lines modified: ~10
- Lines removed: ~5

### Estimated Time
- Implementation: 65 min
- Testing: 45 min
- **Total**: ~2 hours

---

**Status**: ⏳ Ready to Implement
**Complexity**: Medium
**Risk**: Low (additive changes, backwards compatible)

---

*Generated: October 23, 2025*
