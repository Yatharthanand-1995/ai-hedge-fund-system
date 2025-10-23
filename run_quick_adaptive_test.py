#!/usr/bin/env python3
"""
Quick Adaptive Weights Test: 2-Year Comparison
Demonstrates adaptive regime-based weights work better than static
"""
import os
from datetime import datetime, timedelta
from core.backtesting_engine import HistoricalBacktestEngine, BacktestConfig
from core.risk_manager import RiskLimits

os.environ['GEMINI_API_KEY'] = ''
os.environ['OPENAI_API_KEY'] = ''

ELITE_30 = [
    'AAPL', 'MSFT', 'GOOGL', 'NVDA', 'AMZN', 'META', 'TSLA',
    'AVGO', 'CRM', 'ORCL', 'AMD', 'QCOM', 'ADBE',
    'UNH', 'JNJ', 'LLY', 'ABBV',
    'V', 'JPM', 'MA', 'BAC',
    'WMT', 'PG', 'HD', 'KO', 'COST',
    'CVX', 'XOM', 'CAT'
]

print("="*80)
print("⚡ QUICK TEST: Static vs Adaptive Weights (2 Years)")
print("="*80)
print()

end_date = datetime.now()
start_date = end_date - timedelta(days=2*365)  # 2 years for speed

risk_limits = RiskLimits(
    max_portfolio_drawdown=0.15,
    position_stop_loss=0.20,
    max_volatility=0.25,
    max_sector_concentration=0.40,
    max_position_size=0.10,
    cash_buffer_on_drawdown=0.50,
    volatility_scale_factor=0.5
)

common_params = {
    'start_date': start_date.strftime('%Y-%m-%d'),
    'end_date': end_date.strftime('%Y-%m-%d'),
    'initial_capital': 10000.0,
    'rebalance_frequency': 'quarterly',
    'top_n_stocks': 20,
    'universe': ELITE_30,
    'enable_risk_management': True,
    'risk_limits': risk_limits,
    'engine_version': "2.1",
    'use_enhanced_provider': True
}

print(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
print()

# TEST A: Static Weights
print("="*80)
print("📊 TEST A: STATIC WEIGHTS")
print("="*80)
print("   Weights: F:40% M:30% Q:20% S:10% (ALWAYS)")
print()

config_static = BacktestConfig(**common_params, enable_regime_detection=False)
engine_static = HistoricalBacktestEngine(config_static)
result_static = engine_static.run_backtest()

print(f"\n✅ STATIC: {result_static.total_return*100:+.2f}% | Sharpe: {result_static.sharpe_ratio:.2f} | Drawdown: {result_static.max_drawdown*100:.2f}%\n")

# TEST B: Adaptive Weights
print("="*80)
print("📊 TEST B: ADAPTIVE WEIGHTS")
print("="*80)
print("   Weights: DYNAMIC based on market regime")
print()

config_adaptive = BacktestConfig(**common_params, enable_regime_detection=True)
engine_adaptive = HistoricalBacktestEngine(config_adaptive)
result_adaptive = engine_adaptive.run_backtest()

print(f"\n✅ ADAPTIVE: {result_adaptive.total_return*100:+.2f}% | Sharpe: {result_adaptive.sharpe_ratio:.2f} | Drawdown: {result_adaptive.max_drawdown*100:.2f}%\n")

# Comparison
print("="*80)
print("📊 RESULTS COMPARISON")
print("="*80)
print()

return_diff = (result_adaptive.total_return - result_static.total_return) * 100
sharpe_diff = result_adaptive.sharpe_ratio - result_static.sharpe_ratio
dd_diff = (result_static.max_drawdown - result_adaptive.max_drawdown) * 100

print(f"Total Return:    Static {result_static.total_return*100:6.2f}% | Adaptive {result_adaptive.total_return*100:6.2f}% | Δ {return_diff:+.2f}pp")
print(f"Sharpe Ratio:    Static {result_static.sharpe_ratio:6.2f} | Adaptive {result_adaptive.sharpe_ratio:6.2f} | Δ {sharpe_diff:+.2f}")
print(f"Max Drawdown:    Static {result_static.max_drawdown*100:6.2f}% | Adaptive {result_adaptive.max_drawdown*100:6.2f}% | Δ {dd_diff:+.2f}pp")
print(f"Final Value:     Static ${result_static.final_value:,.2f} | Adaptive ${result_adaptive.final_value:,.2f} | Δ ${result_adaptive.final_value - result_static.final_value:+,.2f}")
print()

if return_diff > 2:
    print("✅ VERDICT: Adaptive weights SIGNIFICANTLY BETTER (+{:.1f}pp)".format(return_diff))
elif return_diff > 0:
    print("✅ VERDICT: Adaptive weights BETTER (+{:.1f}pp)".format(return_diff))
else:
    print("⚠️  VERDICT: No improvement ({:+.1f}pp)".format(return_diff))

print()
print("="*80)
print("✅ QUICK TEST COMPLETE")
print("="*80)
