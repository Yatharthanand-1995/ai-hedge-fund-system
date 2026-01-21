# Auto-Buy Execution Mode Guide

## Overview

The system supports two execution strategies for auto-buy opportunities:

1. **Immediate Execution** (default) - Execute immediately when STRONG BUY signals are detected
2. **Batch Execution at 4 PM** - Queue opportunities for review and batch execution at market close

## When to Use Each Mode

### ✅ Use Immediate Execution (`immediate`) when:
- **Paper trading** (virtual money, no risk)
- **Learning and testing** signal quality
- You want to **capture opportunities in real-time**
- You trust the AI scoring system
- You want **immediate feedback** on trades

**Benefits:**
- Don't miss price movements
- Real-time execution matches signal detection
- Simpler workflow (no queue management)
- Better for educational purposes

### ⏰ Use Batch Execution (`batch_4pm`) when:
- Trading with **real capital**
- You want **final human review** before execution
- You need to **aggregate multiple orders** for better fills
- You prefer **market close pricing** for predictability
- Risk management requires **manual approval**

**Benefits:**
- Final review opportunity before committing capital
- Market close prices are often more stable
- Can cancel queued trades if market conditions change
- Better for conservative, risk-managed approaches

## How to Switch Modes

### Option 1: Edit Configuration File

1. Open `data/auto_buy_config.json`
2. Change the `execution_mode` field:

```json
{
  "enabled": true,
  "execution_mode": "immediate",    // ← Change this
  ...
}
```

**Values:**
- `"immediate"` - Execute on signal detection (default)
- `"batch_4pm"` - Queue for 4 PM batch execution

3. Save the file
4. Restart the API server (if running)

### Option 2: Via API (Coming Soon)

```bash
# Update execution mode via API
curl -X POST http://localhost:8010/portfolio/paper/auto-buy/rules \
  -H "Content-Type: application/json" \
  -d '{"execution_mode": "immediate"}'
```

## Behavior by Mode

### Immediate Execution Mode

```
Signal Detected (Score ≥ 70, STRONG BUY)
           ↓
    Validate Rules
           ↓
   Execute Buy NOW  ← Instant!
           ↓
  Portfolio Updated
```

**What you'll see:**
- Auto-buy scan endpoint returns `executed_buys` list
- Trades appear immediately in portfolio
- No queue management needed

### Batch Execution Mode

```
Signal Detected (Score ≥ 70, STRONG BUY)
           ↓
    Validate Rules
           ↓
   Add to Buy Queue  ← Queued for later
           ↓
    Wait until 4 PM
           ↓
  Re-validate Signals
           ↓
   Execute Valid Buys
           ↓
  Portfolio Updated
```

**What you'll see:**
- Auto-buy scan endpoint queues opportunities
- View queue at `/portfolio/paper/auto-buy/queue`
- Trades execute at 4 PM via scheduler
- Stale signals (score dropped >10 points) are rejected

## Checking Current Mode

### Via API:
```bash
curl http://localhost:8010/portfolio/paper/auto-buy/queue | python3 -m json.tool
```

Look for:
```json
{
  "execution_mode": "immediate",
  "next_execution": "Immediate (on signal detection)",
  ...
}
```

### Via Frontend:
Navigate to **Paper Trading** page → Check the **Auto-Buy Status Panel** at the top:
- 🟢 Green badge: "Immediate Execution Mode"
- 🔵 Blue badge: "Next Execution: 4:00 PM ET"

## Recommendations

| Use Case | Recommended Mode | Rationale |
|----------|------------------|-----------|
| **Paper Trading** | `immediate` | Learn in real-time, no capital risk |
| **Backtesting** | N/A | Uses historical data, not real-time |
| **Real Trading (<$10k)** | `immediate` | Small amounts, trust the system |
| **Real Trading (>$10k)** | `batch_4pm` | Large amounts need final review |
| **Learning AI Signals** | `immediate` | Immediate feedback aids learning |
| **Conservative Approach** | `batch_4pm` | Review before committing |

## Default Configuration

**Out of the box:** `execution_mode` is set to `"immediate"` because:
- Most users start with paper trading
- Immediate execution is simpler to understand
- Provides better learning experience
- Matches hedge fund behavior (fast execution on strong signals)

You can always switch to `batch_4pm` when transitioning to real capital.

## Troubleshooting

**Q: I changed execution_mode but it's not taking effect?**
- Restart the API server: `python -m api.main`
- Check for JSON syntax errors in config file

**Q: In immediate mode, why didn't it buy a stock with score 72?**
- Check other rules: confidence level, sector diversification, position limits
- Check portfolio: may have reached max positions (default: 10)
- Check cash: may not have enough for the trade

**Q: In batch mode, trades disappeared from the queue?**
- Check if they were executed at 4 PM (check portfolio history)
- Stale trades (score dropped >10 points) are auto-rejected

**Q: How do I disable auto-buy entirely?**
- Set `"enabled": false` in `auto_buy_config.json`
- Or delete the config file
