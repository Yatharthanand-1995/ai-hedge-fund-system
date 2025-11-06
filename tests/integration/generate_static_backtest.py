#!/usr/bin/env python3
"""
Generate static backtest results for frontend display
Runs backtest directly (bypasses API) and saves in frontend-compatible format
"""
import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from core.backtesting_engine import HistoricalBacktestEngine, BacktestConfig
from dataclasses import asdict

# Disable LLM to avoid rate limits
os.environ['GEMINI_API_KEY'] = ''
os.environ['OPENAI_API_KEY'] = ''

def sanitize_for_json(obj):
    """Convert pandas/numpy types to JSON-serializable Python types"""
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, pd.Series):
        return sanitize_for_json(obj.to_dict())
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        if np.isnan(obj) or np.isinf(obj):
            return 0.0
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return sanitize_for_json(obj.tolist())
    elif pd.isna(obj):
        return None
    else:
        return obj

print("="*80)
print("🎯 Generating Static Backtest Results for Frontend")
print("="*80)
print()

# Match frontend config exactly
end_date = datetime.now()
start_date = end_date.replace(year=end_date.year - 5)

config = BacktestConfig(
    start_date=start_date.strftime('%Y-%m-%d'),
    end_date=end_date.strftime('%Y-%m-%d'),
    initial_capital=10000.0,
    rebalance_frequency='quarterly',
    top_n_stocks=20,
    universe=['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'V', 'JPM', 'UNH',
              'JNJ', 'WMT', 'PG', 'HD', 'MA', 'LLY', 'ABBV', 'KO', 'CVX', 'AVGO'],
    enable_risk_management=False,  # Keep simple for reliability
    enable_regime_detection=False,  # Static weights
    use_enhanced_provider=True,
    engine_version="2.2",
)

print(f"📅 Period: {config.start_date} to {config.end_date}")
print(f"💰 Capital: ${config.initial_capital:,}")
print(f"📊 Universe: {len(config.universe)} stocks")
print(f"🎯 Top N: {config.top_n_stocks}")
print()
print("⏳ Running backtest (may take 5-10 minutes)...")
print()

try:
    # Run backtest
    engine = HistoricalBacktestEngine(config)
    result = engine.run_backtest()

    print("✅ Backtest completed!")
    print()

    # Convert to frontend format (matching API response structure)
    frontend_result = {
        "config": {
            "start_date": result.start_date,
            "end_date": result.end_date,
            "initial_capital": result.initial_capital,
            "rebalance_frequency": config.rebalance_frequency,
            "top_n": config.top_n_stocks,
            "universe": config.universe
        },
        "results": {
            "start_date": result.start_date,
            "end_date": result.end_date,
            "initial_capital": result.initial_capital,
            "final_value": result.final_value,
            "total_return": result.total_return,
            "cagr": result.cagr,
            "sharpe_ratio": result.sharpe_ratio,
            "sortino_ratio": result.sortino_ratio,
            "max_drawdown": result.max_drawdown,
            "max_drawdown_duration": result.max_drawdown_duration,
            "volatility": result.volatility,
            "spy_return": result.spy_return,
            "outperformance_vs_spy": result.outperformance_vs_spy,
            "alpha": result.alpha,
            "beta": result.beta,
            "equity_curve": result.equity_curve,
            "rebalance_events": result.rebalance_events,
            "num_rebalances": result.num_rebalances,
            "performance_by_condition": result.performance_by_condition,
            "best_performers": result.best_performers,
            "worst_performers": result.worst_performers,
            "win_rate": result.win_rate,
            "profit_factor": result.profit_factor,
            "calmar_ratio": result.calmar_ratio,
            "information_ratio": result.information_ratio,
            "engine_version": result.engine_version,
            "data_provider": result.data_provider,
            "data_limitations": result.data_limitations,
            "estimated_bias_impact": result.estimated_bias_impact
        },
        "trade_log": result.trade_log,
        "timestamp": datetime.now().isoformat()
    }

    # Sanitize data for JSON serialization
    frontend_result = sanitize_for_json(frontend_result)

    # Save to frontend public folder
    output_path = 'frontend/public/static_backtest_result.json'
    with open(output_path, 'w') as f:
        json.dump(frontend_result, f, indent=2)

    # Display results
    print("="*80)
    print("📈 PERFORMANCE METRICS")
    print("="*80)
    print(f"   Total Return:       {result.total_return*100:>10.2f}%")
    print(f"   CAGR:              {result.cagr*100:>10.2f}%")
    print(f"   Final Value:        ${result.final_value:>10,.2f}")
    print(f"   Sharpe Ratio:      {result.sharpe_ratio:>10.2f}")
    print(f"   Sortino Ratio:     {result.sortino_ratio:>10.2f}")
    print(f"   Max Drawdown:      {result.max_drawdown*100:>10.2f}%")
    print()

    # Handle spy_return which might be dict or float
    spy_ret = result.spy_return
    if isinstance(spy_ret, dict):
        spy_ret = list(spy_ret.values())[0] if spy_ret else 0

    outperf = result.outperformance_vs_spy
    if isinstance(outperf, dict):
        outperf = list(outperf.values())[0] if outperf else 0

    print("📊 BENCHMARK")
    print("="*80)
    print(f"   SPY Return:        {spy_ret*100:>10.2f}%")
    print(f"   Outperformance:    {outperf*100:>+10.2f}%")
    print()

    print("📋 TRANSACTIONS")
    print("="*80)
    buys = [t for t in result.trade_log if t['action'] == 'BUY']
    sells = [t for t in result.trade_log if t['action'] == 'SELL']
    print(f"   Total Trades:      {len(result.trade_log)}")
    print(f"   Buys:              {len(buys)}")
    print(f"   Sells:             {len(sells)}")
    print()

    print("="*80)
    print("✅ SUCCESS!")
    print("="*80)
    print()
    print(f"💾 Results saved to: {output_path}")
    print()
    print("📝 Next Steps:")
    print("   1. Frontend will automatically load this file")
    print("   2. Refresh your browser")
    print("   3. Results should appear immediately!")
    print()

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
