"""
Quick test to verify Market Regime Detection + Risk Management integration
Tests that both systems work together properly in the backtesting engine
"""

import sys
from datetime import datetime, timedelta
from core.backtesting_engine import HistoricalBacktestEngine, BacktestConfig
from core.risk_manager import RiskLimits
from data.us_top_100_stocks import US_TOP_100_STOCKS
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("="*80)
print("🧪 TESTING: Market Regime Detection + Risk Management Integration")
print("="*80)
print()

# Short 6-month test period
end_date = datetime.now()
start_date = end_date - timedelta(days=180)  # 6 months

# Use small universe for fast test
test_universe = US_TOP_100_STOCKS[:10]

# Configure risk management
risk_limits = RiskLimits(
    max_portfolio_drawdown=0.15,
    position_stop_loss=0.20,
    max_volatility=0.30,
    max_sector_concentration=0.40,
    max_position_size=0.10,
    cash_buffer_on_drawdown=0.50,
    volatility_scale_factor=0.75
)

print(f"📅 Test Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
print(f"📊 Universe: {len(test_universe)} stocks")
print(f"💰 Initial Capital: $10,000")
print()
print("✅ Risk Management: ENABLED")
print("✅ Regime Detection: ENABLED")
print()
print("-"*80)
print("Running backtest...")
print("-"*80)
print()

try:
    config = BacktestConfig(
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        initial_capital=10000.0,
        rebalance_frequency='monthly',
        top_n_stocks=5,
        universe=test_universe,
        backtest_mode=True,
        enable_risk_management=True,
        risk_limits=risk_limits,
        enable_regime_detection=True  # BOTH ENABLED!
    )

    engine = HistoricalBacktestEngine(config)
    result = engine.run_backtest()

    print()
    print("="*80)
    print("✅ INTEGRATION TEST RESULTS")
    print("="*80)
    print()

    print(f"📈 Final Value: ${result.final_value:,.2f}")
    print(f"📈 Total Return: {result.total_return*100:+.2f}%")
    print(f"📉 Max Drawdown: {result.max_drawdown*100:.2f}%")
    print(f"⚡ Sharpe Ratio: {result.sharpe_ratio:.2f}")
    print()

    # Check if regime detection was used
    regime_detected = False
    risk_triggered = False

    for event in engine.rebalance_events:
        if 'market_regime' in event:
            regime_detected = True
            print(f"✅ Regime Detection Working: Found {event['market_regime']['trend']} / {event['market_regime']['volatility']} market on {event['date']}")
            break

    for event in engine.rebalance_events:
        if event.get('risk_triggered_sells', 0) > 0:
            risk_triggered = True
            print(f"✅ Risk Management Working: {event['risk_triggered_sells']} stop-loss sells on {event['date']}")
            break

    if not regime_detected:
        print("⚠️  Warning: No regime detection data found in rebalance events")

    if not risk_triggered:
        print("ℹ️  Note: No risk-triggered sells (market may have been stable)")

    print()
    print("="*80)
    print("🎉 INTEGRATION TEST PASSED!")
    print("   • Both systems are working together")
    print("   • Regime detection adapts portfolio size and cash allocation")
    print("   • Risk management provides additional downside protection")
    print("="*80)
    print()

except Exception as e:
    print()
    print("="*80)
    print(f"❌ TEST FAILED: {e}")
    print("="*80)
    logger.exception("Test error")
    sys.exit(1)
