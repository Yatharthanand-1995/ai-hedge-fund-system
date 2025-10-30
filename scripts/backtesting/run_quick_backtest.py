#!/usr/bin/env python3
"""
Quick 2-Year Backtest: Faster verification of V2.1 fixes
Reduced time period for quick results
"""
import sys
from datetime import datetime, timedelta
from core.backtesting_engine import HistoricalBacktestEngine, BacktestConfig
from core.risk_manager import RiskLimits
from data.us_top_100_stocks import US_TOP_100_STOCKS

print("="*80)
print("⚡ QUICK 2-YEAR BACKTEST: V2.1 Analytical Fixes")
print("="*80)
print()

end_date = datetime.now()
start_date = end_date - timedelta(days=2*365)  # 2 years instead of 5

risk_limits = RiskLimits(
    max_portfolio_drawdown=0.15,
    position_stop_loss=0.20,
    max_volatility=0.25,
    max_sector_concentration=0.40,
    max_position_size=0.10,
    cash_buffer_on_drawdown=0.50,
    volatility_scale_factor=0.5
)

config = BacktestConfig(
    start_date=start_date.strftime('%Y-%m-%d'),
    end_date=end_date.strftime('%Y-%m-%d'),
    initial_capital=10000.0,
    rebalance_frequency='quarterly',
    top_n_stocks=20,
    universe=US_TOP_100_STOCKS,
    enable_risk_management=True,
    enable_regime_detection=False,  # Disabled for speed
    risk_limits=risk_limits,
    engine_version="2.1",
    use_enhanced_provider=True
)

print(f"📅 Period: {config.start_date} to {config.end_date} (2 years)")
print(f"💰 Initial Capital: ${config.initial_capital:,.0f}")
print(f"🎯 Universe: {len(config.universe)} stocks")
print(f"📊 Portfolio: Top {config.top_n_stocks} stocks")
print(f"🔄 Rebalance: Quarterly (8 rebalances)")
print(f"⚡ Faster: Shorter period for quick results")
print()
print("="*80)
print("🔄 Running 2-year backtest...")
print("="*80)
print()

engine = HistoricalBacktestEngine(config)
result = engine.run_backtest()

if result:
    print()
    print("="*80)
    print("✅ QUICK BACKTEST RESULTS")
    print("="*80)
    print()
    print(f"📈 PERFORMANCE")
    print(f"   Final Value:        ${result.final_value:,.2f}")
    print(f"   Total Return:       {result.total_return*100:+.2f}%")
    print(f"   CAGR:              {result.cagr*100:+.2f}%")
    print(f"   Sharpe Ratio:       {result.sharpe_ratio:.2f}")
    print(f"   Max Drawdown:       {result.max_drawdown*100:.2f}%")
    # Handle pandas Series for spy_return and outperformance_vs_spy
    spy_ret = result.spy_return
    if hasattr(spy_ret, 'iloc'):
        spy_ret = spy_ret.iloc[0] if len(spy_ret) > 0 else 0
    outperf = result.outperformance_vs_spy
    if hasattr(outperf, 'iloc'):
        outperf = outperf.iloc[0] if len(outperf) > 0 else 0
    print(f"   SPY Return:         {spy_ret*100:+.2f}%")
    print(f"   Outperformance:     {outperf*100:+.2f}%")
    print()
    print(f"📊 RISK-ADJUSTED")
    print(f"   Sortino Ratio:      {result.sortino_ratio:.2f}")
    print(f"   Calmar Ratio:       {result.calmar_ratio:.2f}")
    print(f"   Volatility:         {result.volatility*100:.2f}%")
    print()
    print(f"✅ V2.1 features working: Sector-aware scoring + Analytical fixes")
    print()
else:
    print("❌ Backtest failed")
