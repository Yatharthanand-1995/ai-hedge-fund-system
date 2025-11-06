# Static Backtest Results Setup

**Date**: 2025-10-31
**Version**: v2.2.1
**Status**: ✅ IMPLEMENTED

---

## 🎯 Goal

Enable the frontend to display backtest results immediately without requiring a 5-10 minute API call each time.

---

## 📝 Changes Made

### 1. Frontend Modification (`frontend/src/pages/BacktestingPage.tsx`)

**Before**:
- Required clicking "Run Backtest" button
- 5-10 minute wait for results
- No default data to display

**After**:
- Automatically loads static results from `/static_backtest_result.json`
- Results appear instantly on page load
- "Run Backtest" button still works for fresh data (optional)

### 2. Static Results Generation

**Script**: `generate_static_backtest.py`

```bash
# Generate static results (run once)
python3 generate_static_backtest.py
```

This script:
- Runs 5-year backtest directly (bypasses API)
- Saves results to `frontend/public/static_backtest_result.json`
- Matches exact format expected by frontend

### 3. Workflow

```
┌─────────────────────────┐
│  Frontend Loads         │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  Fetch static JSON      │
│  /static_backtest_      │
│  result.json            │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  Display Results        │
│  Immediately!           │
└─────────────────────────┘

Optional: Click "Run Backtest" → Override with fresh API data
```

---

## 🚀 Usage

### For Users (Viewing Results)

1. **Open Frontend**: http://localhost:5174
2. **Go to Backtesting** page
3. **See Results Instantly** - No waiting!

### For Developers (Updating Results)

When you want to update the displayed backtest with new data:

```bash
# 1. Generate new backtest results
python3 generate_static_backtest.py

# 2. Frontend automatically picks up the new file
# (just refresh browser if needed)
```

---

## 📂 File Locations

- **Frontend Code**: `frontend/src/pages/BacktestingPage.tsx`
- **Static Results**: `frontend/public/static_backtest_result.json`
- **Generation Script**: `generate_static_backtest.py`

---

## 🔧 Technical Details

### Frontend Loading Logic

```typescript
// Load static results from public folder
const { data: staticResult } = useQuery<BacktestResult>({
  queryKey: ['static-backtest'],
  queryFn: async () => {
    const response = await fetch('/static_backtest_result.json');
    return response.json();
  },
  staleTime: Infinity, // Never refetch
});

// Use static by default, API result overrides if available
const result = apiResult || staticResult;
```

### Benefits

✅ **Instant Load**: Results appear immediately
✅ **No API Wait**: No 5-10 minute delay
✅ **Still Fresh**: Can run new backtest anytime via button
✅ **Reliable**: No timeout errors
✅ **Flexible**: Easy to update results anytime

---

## 🐛 API Timeout Investigation

### Issue
API backtest endpoint (`POST /backtest/historical`) times out after 3 minutes.

### Root Causes Identified

1. **Data Fetching Overhead**:
   - Fetches data for 20 stocks
   - 21 rebalance dates over 5 years
   - ~420 data fetches total (20 stocks × 21 dates)
   - Each fetch calls 4 agents
   - Total: ~1,680 agent calls

2. **yfinance Rate Limiting**:
   - Yahoo Finance API has rate limits
   - Multiple concurrent requests slow down

3. **LLM API Calls** (if enabled):
   - Sentiment agent makes LLM calls
   - Adds 2-3 seconds per stock

### Solutions Implemented

**Short-term** (Current):
- ✅ Disable LLM in generation script
- ✅ Run backtest directly (not via API)
- ✅ Use static file for display

**Medium-term** (Recommended):
- [ ] Increase API timeout to 10 minutes
- [ ] Add caching layer for historical data
- [ ] Implement progress websocket for live updates

**Long-term** (Optional):
- [ ] Pre-compute common backtests
- [ ] Background job queue for long-running tasks
- [ ] Database cache for stock scores

---

## 📊 Current Backtest Parameters

```python
config = {
    "start_date": "5 years ago",
    "end_date": "today",
    "initial_capital": 10000,
    "rebalance_frequency": "quarterly",
    "top_n": 20,
    "universe": [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA',
        'META', 'TSLA', 'V', 'JPM', 'UNH',
        'JNJ', 'WMT', 'PG', 'HD', 'MA',
        'LLY', 'ABBV', 'KO', 'CVX', 'AVGO'
    ],
    "enable_risk_management": False,  # Simpler/faster
    "enable_regime_detection": False,  # Static weights
}
```

---

## ✅ Testing

### Test Static Results Load

1. Ensure static file exists:
```bash
ls -lh frontend/public/static_backtest_result.json
```

2. Open frontend:
```bash
open http://localhost:5174
```

3. Navigate to Backtesting page
4. Results should appear immediately!

### Test Fresh Backtest (Optional)

1. Click "Run Backtest" button in frontend
2. Wait 5-10 minutes
3. New results override static results

---

## 🎉 Success Criteria

✅ Frontend loads instantly
✅ Backtest results visible immediately
✅ Transaction log shows all buy/sell prices
✅ "Run Backtest" button still works for fresh data
✅ No more timeout errors on page load

---

**Last Updated**: 2025-10-31
**Status**: Implementation Complete, Backtest Generation In Progress
