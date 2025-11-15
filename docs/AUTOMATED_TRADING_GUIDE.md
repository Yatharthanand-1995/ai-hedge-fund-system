# Automated Paper Trading Guide

## Overview

The AI Hedge Fund System now supports **fully automated paper trading** with intelligent buy/sell automation based on the 4-agent AI analysis system. The automation monitors your portfolio 24/7 and executes trades based on configurable rules.

## Features

### Auto-Buy System
Automatically buys stocks that meet your investment criteria:

- **Score Threshold**: Only buy stocks with AI scores >= 75 (default)
- **Recommendation Filter**: Auto-buy on "STRONG BUY" signals
- **Confidence Filter**: Minimum confidence level (LOW/MEDIUM/HIGH)
- **Position Sizing**: Max 15% of portfolio per position
- **Trade Limits**: Max $2,000 per trade (configurable)
- **Max Positions**: Limit total positions (default: 10)
- **Sector Diversification**: Max 30% allocation per sector
- **Avoid Doubling**: Won't buy stocks already owned

### Auto-Sell System
Automatically sells positions that trigger exit criteria:

- **Stop-Loss**: Sell if loss exceeds -10% (configurable)
- **Take-Profit**: Sell if gain exceeds +20% (configurable)
- **AI Signal Watch**: Sell when AI downgrades to "SELL" or "WEAK SELL"
- **Position Age Limit**: Optional max holding period (disabled by default)

## Quick Start

### 1. Enable Auto-Buy

```bash
curl -X POST "http://localhost:8010/portfolio/paper/auto-buy/rules?enabled=true&min_score_threshold=75&max_positions=10"
```

**Auto-Buy Configuration:**
- `enabled`: Enable/disable auto-buy (boolean)
- `min_score_threshold`: Minimum AI score (0-100, default: 75)
- `max_position_size_percent`: Max % of portfolio per position (default: 15%)
- `max_positions`: Maximum number of positions (default: 10)
- `min_confidence_level`: Minimum confidence (LOW/MEDIUM/HIGH, default: MEDIUM)
- `max_single_trade_amount`: Max $ per trade (default: $2000)
- `require_sector_diversification`: Enable sector limits (default: true)
- `max_sector_allocation_percent`: Max % per sector (default: 30%)

### 2. Enable Auto-Sell

```bash
curl -X POST "http://localhost:8010/portfolio/paper/auto-sell/rules?enabled=true&stop_loss_percent=-10&take_profit_percent=20&watch_ai_signals=true"
```

**Auto-Sell Configuration:**
- `enabled`: Enable/disable auto-sell (boolean)
- `stop_loss_percent`: Stop-loss trigger (negative %, default: -10%)
- `take_profit_percent`: Take-profit trigger (positive %, default: 20%)
- `watch_ai_signals`: Monitor AI recommendation changes (default: true)
- `max_position_age_days`: Max holding period in days (optional, default: null)

### 3. Run Automated Trading

```bash
# Execute full trading cycle (sell then buy)
curl -X POST "http://localhost:8010/portfolio/paper/auto-trade"
```

This endpoint:
1. Scans portfolio for sell signals
2. Executes auto-sells
3. Scans market for buy opportunities
4. Executes auto-buys
5. Returns summary of all trades

## API Endpoints

### Auto-Buy Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/portfolio/paper/auto-buy/rules` | GET | Get auto-buy configuration |
| `/portfolio/paper/auto-buy/rules` | POST | Update auto-buy rules |
| `/portfolio/paper/auto-buy/scan` | GET | Scan for buy opportunities (no execution) |
| `/portfolio/paper/auto-buy/execute` | POST | Execute auto-buys |
| `/portfolio/paper/auto-buy/alerts` | GET | Get auto-buy alert history |

### Auto-Sell Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/portfolio/paper/auto-sell/rules` | GET | Get auto-sell configuration |
| `/portfolio/paper/auto-sell/rules` | POST | Update auto-sell rules |
| `/portfolio/paper/auto-sell/scan` | GET | Scan for sell signals (no execution) |
| `/portfolio/paper/auto-sell/execute` | POST | Execute auto-sells |
| `/portfolio/paper/auto-sell/alerts` | GET | Get auto-sell alert history |

### Unified Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/portfolio/paper/auto-trade` | POST | Run full trading cycle (sell + buy) |
| `/portfolio/paper/auto-trade/status` | GET | Get automation status & portfolio |

## Usage Examples

### Python Example

```python
import requests

BASE_URL = "http://localhost:8010"

# Enable automation
requests.post(
    f"{BASE_URL}/portfolio/paper/auto-buy/rules",
    params={"enabled": True, "min_score_threshold": 75}
)

requests.post(
    f"{BASE_URL}/portfolio/paper/auto-sell/rules",
    params={"enabled": True, "stop_loss_percent": -10, "take_profit_percent": 20}
)

# Check status
status = requests.get(f"{BASE_URL}/portfolio/paper/auto-trade/status").json()
print(f"Fully Automated: {status['automation_enabled']['fully_automated']}")

# Scan for opportunities (dry run)
opportunities = requests.get(f"{BASE_URL}/portfolio/paper/auto-buy/scan").json()
print(f"Found {opportunities['count']} buy opportunities")

# Execute automated trading
result = requests.post(f"{BASE_URL}/portfolio/paper/auto-trade").json()
print(f"Executed {result['summary']['total_trades']} trades")
```

### cURL Examples

```bash
# Check automation status
curl http://localhost:8010/portfolio/paper/auto-trade/status

# Scan for buy opportunities (no execution)
curl http://localhost:8010/portfolio/paper/auto-buy/scan?universe_limit=30

# Scan for sell signals (no execution)
curl http://localhost:8010/portfolio/paper/auto-sell/scan

# Execute full automated trading cycle
curl -X POST http://localhost:8010/portfolio/paper/auto-trade

# View auto-buy alerts
curl http://localhost:8010/portfolio/paper/auto-buy/alerts?limit=20

# View auto-sell alerts
curl http://localhost:8010/portfolio/paper/auto-sell/alerts?limit=20
```

## How It Works

### Auto-Buy Decision Flow

```
1. Scan top 50 stocks from universe
2. Filter out already-owned stocks
3. For each stock:
   a. Check if score >= min_score_threshold (75)
   b. Check if recommendation in ["STRONG BUY"]
   c. Check if confidence >= min_confidence_level (MEDIUM)
   d. Check if num_positions < max_positions (10)
   e. Check sector diversification limits
   f. Calculate position size (min of 15% portfolio or $2000)
   g. Execute buy if all checks pass
```

### Auto-Sell Decision Flow

```
1. Get current portfolio positions
2. Fetch current AI recommendations
3. For each position:
   a. Check unrealized P&L vs stop-loss (-10%)
   b. Check unrealized P&L vs take-profit (+20%)
   c. Check if AI recommendation changed to SELL/WEAK SELL
   d. Check position age (if configured)
   e. Execute sell if any trigger activated
```

## Best Practices

### Recommended Settings for Different Strategies

**Conservative (Low Risk)**
```bash
# Auto-Buy
min_score_threshold=80
max_positions=5
max_position_size_percent=10
min_confidence_level=HIGH
max_single_trade_amount=1000

# Auto-Sell
stop_loss_percent=-5
take_profit_percent=15
watch_ai_signals=true
```

**Balanced (Medium Risk)**
```bash
# Auto-Buy
min_score_threshold=75
max_positions=10
max_position_size_percent=15
min_confidence_level=MEDIUM
max_single_trade_amount=2000

# Auto-Sell
stop_loss_percent=-10
take_profit_percent=20
watch_ai_signals=true
```

**Aggressive (Higher Risk)**
```bash
# Auto-Buy
min_score_threshold=70
max_positions=15
max_position_size_percent=20
min_confidence_level=LOW
max_single_trade_amount=3000

# Auto-Sell
stop_loss_percent=-15
take_profit_percent=30
watch_ai_signals=true
```

## Monitoring & Alerts

### View Recent Activity

```bash
# Check last 50 auto-buy alerts
curl http://localhost:8010/portfolio/paper/auto-buy/alerts?limit=50

# Check last 50 auto-sell alerts
curl http://localhost:8010/portfolio/paper/auto-sell/alerts?limit=50

# View all transactions
curl http://localhost:8010/portfolio/paper/transactions?limit=100
```

### Alert Types

**Auto-Buy Alerts:**
- `TRIGGERED`: Buy opportunity identified
- Contains: symbol, score, recommendation, shares, price, total_cost

**Auto-Sell Alerts:**
- `TRIGGERED`: Sell signal activated
- Contains: symbol, trigger type (stop_loss/take_profit/ai_signal), unrealized P&L

## Testing

Run the automated trading test script:

```bash
python3 test_automated_trading.py
```

This will:
1. Check current automation status
2. Enable auto-buy and auto-sell
3. Scan for opportunities
4. Demonstrate full trading cycle

## Architecture

### Backend Components

- **`core/auto_buy_monitor.py`**: Auto-buy logic and opportunity scanning
- **`core/auto_sell_monitor.py`**: Auto-sell logic and signal detection
- **`core/paper_portfolio_manager.py`**: Portfolio management and trade execution
- **`api/main.py`**: API endpoints for automation control

### Data Flow

```
User → API Endpoints → Auto-Buy/Sell Monitors → 4-Agent Analysis → Portfolio Manager → Trade Execution → Transaction Log
```

## Safety Features

1. **Dry Run Mode**: Use `/scan` endpoints to preview without executing
2. **Position Limits**: Max positions, max per-position size
3. **Sector Diversification**: Prevent overconcentration
4. **Confidence Filtering**: Only trade high-confidence signals
5. **Transaction Logging**: All trades logged to `data/transaction_log.json`
6. **Alert History**: Track all triggers to `data/auto_buy_alerts.json` and `data/auto_sell_alerts.json`

## Troubleshooting

### No Opportunities Found

**Possible reasons:**
- Score threshold too high (try lowering from 75 to 70)
- Already at max positions
- Insufficient cash for trades
- All high-scoring stocks already owned
- Sector diversification limits reached

**Solutions:**
```bash
# Lower score threshold
curl -X POST "http://localhost:8010/portfolio/paper/auto-buy/rules?min_score_threshold=70"

# Increase max positions
curl -X POST "http://localhost:8010/portfolio/paper/auto-buy/rules?max_positions=15"
```

### No Sell Signals

**Possible reasons:**
- No positions held
- All positions within stop-loss/take-profit range
- AI still recommends holding
- Auto-sell disabled

**Solutions:**
```bash
# Check portfolio
curl http://localhost:8010/portfolio/paper

# Adjust thresholds
curl -X POST "http://localhost:8010/portfolio/paper/auto-sell/rules?stop_loss_percent=-8&take_profit_percent=15"
```

## Future Enhancements

Planned features:
- [ ] Scheduled automation (cron-like execution)
- [ ] Email/webhook notifications
- [ ] Backtesting automation strategies
- [ ] Advanced filters (momentum, volatility)
- [ ] Partial position sizing (dollar-cost averaging)
- [ ] Trailing stop-loss
- [ ] Risk parity position sizing

## API Documentation

Full interactive API documentation available at:
- Swagger UI: http://localhost:8010/docs
- ReDoc: http://localhost:8010/redoc

All automation endpoints are tagged under "Paper Trading - Automation".
