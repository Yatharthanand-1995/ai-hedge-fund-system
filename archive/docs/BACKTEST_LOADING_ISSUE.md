# Backtest Loading Issue - Troubleshooting Guide

**Date**: October 10, 2025
**Issue**: Frontend shows "loading" when trying to view backtest results
**Root Cause**: API endpoint timing out or long-running backtest blocking requests

---

## Current Status

✅ **Backtest Data Exists**: 1 stored result in `data/backtest_results/`
✅ **Frontend Running**: http://localhost:5174
⚠️ **API Hanging**: `/backtest/history` endpoint timing out
⚠️ **Possible Long-Running Backtest**: May be blocking the API

---

## Quick Diagnosis

### 1. Check Stored Data
```bash
cat data/backtest_results/index.json | python3 -m json.tool
```

**Expected Output**:
```json
[
  {
    "backtest_id": "d184236a-5f11-4fe3-aa7f-c86a8712d293",
    "timestamp": "2025-10-10T18:23:50.453639",
    "total_return": 0.0851,
    "sharpe_ratio": 7.28
  }
]
```
✅ **Data exists** - 1 backtest stored

### 2. Test API Endpoint Directly
```bash
curl -m 5 http://localhost:8010/backtest/history
```

❌ **Times out** - API is hung or processing long request

### 3. Check API Logs
```bash
tail -100 /tmp/api_debug.log | grep -i backtest
```

**Findings**: API appears to be running a long backtest that's blocking other requests

---

## Root Cause Analysis

The `/backtest/history` endpoint is timing out because:

1. **FastAPI is synchronous** for this endpoint - it blocks while waiting
2. **Long-running backtest** may be in progress (downloading 277 days of data for multiple stocks)
3. **No async handling** - the endpoint waits for any in-progress backtest to complete

---

## Solution Options

### Option 1: Wait for Current Backtest to Complete
**Time**: 2-5 minutes
**Action**: Just wait - the backtest will complete and then history will load

### Option 2: Restart API Server (Recommended)
```bash
# Kill all Python processes
killall -9 python3

# Wait a moment
sleep 3

# Restart API
cd /Users/yatharthanand/ai_hedge_fund_system
python3 -m api.main > /tmp/api_fresh.log 2>&1 &

# Wait for startup
sleep 10

# Test
curl http://localhost:8010/health
curl http://localhost:8010/backtest/history
```

### Option 3: Use Cached Result
The backtest data is already stored. You can view it directly:

```bash
# View the stored backtest
cat data/backtest_results/results/d184236a-5f11-4fe3-aa7f-c86a8712d293.json | python3 -m json.tool
```

---

## Permanent Fix (For Development)

### Make `/backtest/history` Truly Async

**File**: `api/main.py` (line 1512)

**Current** (blocks):
```python
@app.get("/backtest/history", tags=["Backtesting"])
async def get_backtest_history(limit: int = 10):
    # This still blocks even though it's marked async
    storage = get_backtest_storage()
    stored_results = storage.get_all_results(limit=limit)
    return stored_results
```

**Better** (non-blocking):
```python
@app.get("/backtest/history", tags=["Backtesting"])
async def get_backtest_history(limit: int = 10):
    # Run storage access in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    stored_results = await loop.run_in_executor(
        None,
        lambda: get_backtest_storage().get_all_results(limit)
    )
    return stored_results
```

---

## Immediate Workaround

### Use the Start Script
```bash
cd /Users/yatharthanand/ai_hedge_fund_system
./start_system.sh
```

This will:
1. Kill existing processes
2. Start API on port 8010
3. Start frontend on port 5174
4. Show you the URLs

---

## Frontend Issue

The frontend is configured to call `/backtest/history` on page load. If the API is hung, the frontend will show "loading" indefinitely.

**Frontend File**: `frontend/src/components/dashboard/BacktestResultsPanel.tsx` (line 66)

```typescript
useEffect(() => {
  loadBacktestHistory();  // Called on mount - will hang if API hung
}, []);
```

**Temporary Fix**: Add a timeout to the frontend request:

```typescript
const loadBacktestHistory = async () => {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout

    const response = await fetch(`${API_BASE_URL}/backtest/history`, {
      signal: controller.signal
    });

    clearTimeout(timeoutId);
    // ... rest of code
  } catch (error) {
    if (error.name === 'AbortError') {
      console.error('Request timed out - API may be processing a backtest');
      // Show user-friendly message
    }
  }
};
```

---

## Verification Steps

After restarting:

### 1. Check API Health
```bash
curl http://localhost:8010/health
```
Expected: `{"status":"healthy",...}`

### 2. Check Backtest History
```bash
curl http://localhost:8010/backtest/history
```
Expected: JSON array with 1 backtest

### 3. Open Frontend
```
http://localhost:5174
```
Navigate to Backtesting tab - should show 1 historical backtest

---

## Expected Backtest Display

In the frontend, you should see:

- **Backtest ID**: d184236a-5f11-4fe3-aa7f-c86a8712d293
- **Date Range**: 2025-09-01 to 2025-10-10
- **Total Return**: 8.51%
- **Sharpe Ratio**: 7.28
- **Max Drawdown**: -1.92%
- **Equity Curve**: Chart showing 40 days of performance
- **Rebalance Log**: 2 rebalance events with stock selections

---

## Quick Fix Commands

```bash
# 1. Kill everything
killall -9 python3; killall -9 node

# 2. Wait
sleep 5

# 3. Start API
cd /Users/yatharthanand/ai_hedge_fund_system
python3 -m api.main > /tmp/api.log 2>&1 &

# 4. Start Frontend
cd frontend
npm run dev > /tmp/frontend.log 2>&1 &

# 5. Wait for startup
sleep 15

# 6. Test
curl http://localhost:8010/health
curl http://localhost:8010/backtest/history

# 7. Open browser
open http://localhost:5174
```

---

## Summary

**Problem**: API endpoint timing out, causing frontend loading spinner

**Why**: Long-running backtest or API synchronization issue

**Solution**: Restart API server and frontend

**Data**: Backtest results ARE stored and available (verified in storage)

**Next Steps**:
1. Restart services using commands above
2. Open http://localhost:5174
3. Navigate to Backtesting tab
4. Should see 1 historical backtest with real data

---

**Status**: Issue identified, workaround provided
**Fix Complexity**: Simple (restart) + Optional (async improvement)
**Data Loss**: None - all data is persisted in storage
