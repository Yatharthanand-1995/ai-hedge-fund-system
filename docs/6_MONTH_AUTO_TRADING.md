# 6-Month Automated Paper Trading

## Overview

The AI Hedge Fund System now includes a **6-month automated trading strategy** that automatically buys stocks on STRONG BUY signals and sells them after exactly 6 months (180 days), while also applying intelligent risk management rules.

This feature leverages the existing auto-buy and auto-sell infrastructure with a time-based exit strategy designed for testing the 5-agent AI system over medium-term holding periods.

## Quick Start

### 1. Setup (One-Time Configuration)

```bash
python3 setup_6month_auto_trading.py
```

This script configures:
- ✅ Auto-buy on STRONG BUY recommendations (score ≥ 75)
- ✅ Auto-sell after 180 days (6 months)
- ✅ Stop-loss at -10%
- ✅ Take-profit at +20%
- ✅ AI signal monitoring

### 2. Test the System

```bash
python3 test_6month_auto_trading.py
```

This verifies:
- Configuration is correct
- Auto-buy and auto-sell are enabled
- Position age calculations work
- Scanning and execution logic is functional

### 3. Monitor Trading

```bash
# Check automation status
curl http://localhost:8010/portfolio/paper/auto-trade/status

# Execute trading cycle (manual trigger)
curl -X POST http://localhost:8010/portfolio/paper/auto-trade
```

## How It Works

### Auto-Buy Logic

The system continuously scans the stock universe and **automatically buys** when:

1. **Score Threshold**: Stock score ≥ 75 (out of 100)
2. **Recommendation**: Stock has "STRONG BUY" recommendation
3. **Confidence**: Analysis confidence ≥ MEDIUM
4. **Portfolio Limits**:
   - Not already owned (no doubling down)
   - Total positions < 10
   - Position size ≤ 15% of portfolio value
   - Trade amount ≤ $2,000
5. **Sector Diversification**:
   - Sector allocation ≤ 30%
   - Prevents overconcentration

### Auto-Sell Logic

The system **automatically sells** positions when ANY of these triggers:

1. **6-Month Age Limit**: Position held for ≥ 180 days ⭐ **NEW**
2. **Stop-Loss**: Unrealized loss ≤ -10%
3. **Take-Profit**: Unrealized gain ≥ +20%
4. **AI Signal Change**: Recommendation downgrades to SELL or WEAK SELL

### Timeline Example

```
Day 0    → Stock reaches STRONG BUY (score 80)
           ✅ AUTO-BUY: 10 shares @ $150 = $1,500

Day 30   → Stock +10% (score 75, still BUY)
           🟢 HOLD: Position worth $1,650 (+$150 gain)

Day 60   → Stock -5% (score 72, HOLD)
           🟢 HOLD: Position worth $1,425 (-$75 loss)

Day 90   → Stock +15% (score 78, BUY)
           🟢 HOLD: Position worth $1,725 (+$225 gain)

Day 150  → Stock +25% (score 80, STRONG BUY)
           ⚠️  TAKE-PROFIT TRIGGER: Sell at $1,875 (+$375 gain)
           OR continue holding until Day 180

Day 180  → 6 months elapsed
           🔴 AUTO-SELL (age limit): Sell at current price
           Realize gains/losses
```

## Configuration Details

### Current Settings

Auto-buy rules are stored in `data/auto_buy_config.json`:

```json
{
  "enabled": true,
  "min_score_threshold": 75.0,
  "max_position_size_percent": 15.0,
  "max_positions": 10,
  "min_confidence_level": "MEDIUM",
  "auto_buy_recommendations": ["STRONG BUY"],
  "max_single_trade_amount": 2000.0,
  "require_sector_diversification": true,
  "max_sector_allocation_percent": 30.0
}
```

Auto-sell rules are stored in `data/auto_sell_config.json`:

```json
{
  "enabled": true,
  "stop_loss_percent": -10.0,
  "take_profit_percent": 20.0,
  "watch_ai_signals": true,
  "max_position_age_days": 180
}
```

### Modifying Settings

```bash
# Change 6-month period to 3 months (90 days)
curl -X POST "http://localhost:8010/portfolio/paper/auto-sell/rules?max_position_age_days=90"

# Change to 1 year (365 days)
curl -X POST "http://localhost:8010/portfolio/paper/auto-sell/rules?max_position_age_days=365"

# Disable age-based selling (keep other rules)
curl -X POST "http://localhost:8010/portfolio/paper/auto-sell/rules?max_position_age_days=null"

# Adjust stop-loss to -5%
curl -X POST "http://localhost:8010/portfolio/paper/auto-sell/rules?stop_loss_percent=-5"

# Increase max positions to 15
curl -X POST "http://localhost:8010/portfolio/paper/auto-buy/rules?max_positions=15"
```

## API Endpoints

### Status & Monitoring

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/portfolio/paper/auto-trade/status` | GET | Overall automation status |
| `/portfolio/paper/auto-buy/rules` | GET | Current auto-buy configuration |
| `/portfolio/paper/auto-sell/rules` | GET | Current auto-sell configuration |
| `/portfolio/paper/auto-buy/alerts` | GET | Auto-buy trigger history |
| `/portfolio/paper/auto-sell/alerts` | GET | Auto-sell trigger history |
| `/portfolio/paper/transactions` | GET | All executed trades |

### Scanning (Dry Run)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/portfolio/paper/auto-buy/scan` | GET | Preview buy opportunities (no execution) |
| `/portfolio/paper/auto-sell/scan` | GET | Preview sell signals (no execution) |

### Execution

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/portfolio/paper/auto-buy/execute` | POST | Execute auto-buys only |
| `/portfolio/paper/auto-sell/execute` | POST | Execute auto-sells only |
| `/portfolio/paper/auto-trade` | POST | Execute full cycle (sell then buy) |

## Testing Strategy

### Why 6 Months?

1. **Medium-Term Validation**: Tests AI predictions over a realistic investment horizon
2. **Earnings Cycles**: Captures 2-3 quarterly earnings reports
3. **Trend Confirmation**: Enough time for fundamental trends to play out
4. **Risk Management**: Prevents indefinite holding of declining positions

### Expected Outcomes

**Successful Scenarios:**
- Stock reaches +20% gain → Take-profit triggered before 6 months
- Stock maintains STRONG BUY → Held for full 6 months, sold at profit
- Stock drops to SELL recommendation → AI signal triggers early exit

**Risk Mitigation:**
- Stock drops -10% → Stop-loss triggers, limits downside
- Stock trades sideways for 6 months → Age limit forces exit, frees capital
- Stock deteriorates slowly → AI downgrade or age limit prevents further loss

## Monitoring & Alerts

### View Recent Activity

```bash
# Last 50 auto-buy alerts
curl http://localhost:8010/portfolio/paper/auto-buy/alerts?limit=50 | python3 -m json.tool

# Last 50 auto-sell alerts
curl http://localhost:8010/portfolio/paper/auto-sell/alerts?limit=50 | python3 -m json.tool

# Recent transactions
curl http://localhost:8010/portfolio/paper/transactions?limit=100 | python3 -m json.tool
```

### Alert Format

**Auto-Buy Alert:**
```json
{
  "timestamp": "2025-12-30T10:30:00",
  "symbol": "AAPL",
  "reason": "Auto-buy triggered: STRONG BUY (score: 82.5, confidence: HIGH)",
  "action": "TRIGGERED",
  "details": {
    "overall_score": 82.5,
    "recommendation": "STRONG BUY",
    "confidence_level": "HIGH",
    "shares": 12,
    "price": 165.50,
    "total_cost": 1986.00
  }
}
```

**Auto-Sell Alert (Age-Based):**
```json
{
  "timestamp": "2025-12-30T15:45:00",
  "symbol": "MSFT",
  "reason": "Position age exceeded: 182 days (max: 180)",
  "action": "TRIGGERED",
  "details": {
    "position_age_days": 182,
    "max_days": 180
  }
}
```

## Architecture

### Components

1. **`core/auto_buy_monitor.py`**:
   - Scans for STRONG BUY opportunities
   - Validates portfolio constraints
   - Calculates position sizing

2. **`core/auto_sell_monitor.py`**:
   - Monitors position age (NEW: 6-month logic)
   - Checks stop-loss / take-profit
   - Watches AI recommendation changes

3. **`core/paper_portfolio_manager.py`**:
   - Executes buy/sell orders
   - Updates portfolio state
   - Logs all transactions

4. **`api/main.py`**:
   - Exposes automation endpoints
   - Coordinates buy/sell cycles
   - Returns trade summaries

### Data Flow

```
User Portfolio
      ↓
Auto-Sell Monitor → Check positions → Sell triggers?
      ↓                                      ↓
      No                                    Yes
      ↓                                      ↓
Auto-Buy Monitor                     Execute Sells
      ↓                                      ↓
Scan Universe → STRONG BUY?           Update Portfolio
      ↓              ↓                       ↓
      No            Yes                 Free up cash
      ↓              ↓                       ↓
   HOLD       Execute Buys ←─────────────────┘
                    ↓
            Update Portfolio
                    ↓
            Log Transaction
```

## Position Age Calculation

The age-based auto-sell uses the `first_purchase_date` field:

```python
from datetime import datetime

# In paper_portfolio_manager.py
position = {
    'symbol': 'AAPL',
    'shares': 10,
    'cost_basis': 150.0,
    'first_purchase_date': '2025-06-30T10:00:00',  # Initial purchase
    'last_purchase_date': '2025-06-30T10:00:00'
}

# In auto_sell_monitor.py
first_purchase = datetime.fromisoformat(position['first_purchase_date'])
age_days = (datetime.now() - first_purchase).days

if age_days >= 180:  # 6 months
    trigger_sell(position)
```

**Important**: Age is calculated from the **first purchase**, not subsequent adds.

## Best Practices

### 1. Regular Execution

Set up a cron job or scheduled task to execute trading cycles:

```bash
# Run every day at 4 PM (after market close)
0 16 * * 1-5 curl -X POST http://localhost:8010/portfolio/paper/auto-trade
```

### 2. Monitor Performance

Track key metrics weekly:
- Number of positions bought
- Number of positions sold (by trigger type)
- Average holding period
- Win rate (profitable exits)
- Total P&L

### 3. Review Alerts

Regularly review alerts to understand:
- Why stocks were bought (score, confidence)
- Why stocks were sold (trigger type)
- Timing of exits (age vs. stop-loss vs. take-profit)

### 4. Adjust Parameters

Based on results, tune:
- `min_score_threshold`: 70-80 range
- `stop_loss_percent`: -5% to -15%
- `take_profit_percent`: 15% to 30%
- `max_position_age_days`: 90-365 days

## Troubleshooting

### No Buy Opportunities Found

**Symptoms:**
- Scan returns 0 opportunities
- No new positions added

**Possible Causes:**
1. No stocks have STRONG BUY rating
2. Already at max positions (10)
3. Insufficient cash
4. Sector limits reached

**Solutions:**
```bash
# Lower score threshold
curl -X POST "http://localhost:8010/portfolio/paper/auto-buy/rules?min_score_threshold=70"

# Increase max positions
curl -X POST "http://localhost:8010/portfolio/paper/auto-buy/rules?max_positions=15"

# Add more cash to portfolio
curl -X POST "http://localhost:8010/portfolio/paper/add-cash" -d '{"amount": 5000}'
```

### No Sell Signals Triggered

**Symptoms:**
- Positions held longer than 6 months
- No auto-sells executed

**Possible Causes:**
1. Auto-sell disabled
2. Position age not being calculated
3. `first_purchase_date` field missing

**Solutions:**
```bash
# Verify auto-sell is enabled
curl http://localhost:8010/portfolio/paper/auto-sell/rules

# Check position data
curl http://localhost:8010/portfolio/paper | python3 -m json.tool

# Re-enable auto-sell with 6-month rule
python3 setup_6month_auto_trading.py
```

### Position Age Not Calculated

**Symptoms:**
- `first_purchase_date` is null or missing
- Age-based sells not triggering

**Solutions:**
- This is only an issue for positions created before this feature
- New positions automatically get `first_purchase_date`
- Old positions will be sold by other triggers (stop-loss, take-profit, AI signal)

## Future Enhancements

Planned improvements:

- [ ] Email/webhook notifications when trades execute
- [ ] Backtesting mode to test 6-month strategy on historical data
- [ ] Performance dashboard showing age-based exit analytics
- [ ] Configurable age limits per sector (e.g., 90 days for tech, 180 for value)
- [ ] Partial exits (sell 50% at 6 months, hold remainder)
- [ ] Trailing age-based exit (extend if stock is still STRONG BUY)

## Related Documentation

- [Automated Trading Guide](./AUTOMATED_TRADING_GUIDE.md) - Full automation documentation
- [Paper Trading](./PAPER_TRADING.md) - General paper trading overview
- [5-Agent System](./FIVE_AGENT_SYSTEM.md) - Understanding the AI scoring

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. View logs: Check API console output
3. Test configuration: Run `test_6month_auto_trading.py`
4. Review alerts: Check `data/auto_buy_alerts.json` and `data/auto_sell_alerts.json`

---

**Last Updated**: 2025-12-30
**Feature Version**: 1.0
**Compatible With**: AI Hedge Fund System v5.0+
