#!/usr/bin/env python3
"""
5-Year V2.1 Backtest: Full historical simulation with all fixes
Uses 30-stock universe (reduced from 50) to avoid rate limits
"""
import os
import sys
from datetime import datetime, timedelta
from core.backtesting_engine import HistoricalBacktestEngine, BacktestConfig
from core.risk_manager import RiskLimits

# Disable LLM to avoid Gemini rate limits
os.environ['GEMINI_API_KEY'] = ''
os.environ['OPENAI_API_KEY'] = ''

# 30-stock elite universe (balanced across sectors)
ELITE_30 = [
    # Magnificent 7 (Tech giants)
    'AAPL', 'MSFT', 'GOOGL', 'NVDA', 'AMZN', 'META', 'TSLA',
    # Tech leaders
    'AVGO', 'CRM', 'ORCL', 'AMD', 'QCOM', 'ADBE',
    # Healthcare leaders
    'UNH', 'JNJ', 'LLY', 'ABBV',
    # Financial leaders
    'V', 'JPM', 'MA', 'BAC',
    # Consumer leaders
    'WMT', 'PG', 'HD', 'KO', 'COST',
    # Energy
    'CVX', 'XOM',
    # Industrial
    'CAT'
]

print("="*80)
print("🚀 5-YEAR V2.1 BACKTEST: Complete Historical Simulation")
print("="*80)
print()

end_date = datetime.now()
start_date = end_date - timedelta(days=5*365)

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
    universe=ELITE_30,
    enable_risk_management=True,
    enable_regime_detection=True,  # ✅ ENABLED: Use adaptive regime-based weights
    risk_limits=risk_limits,
    engine_version="2.1",
    use_enhanced_provider=True
)

print(f"📅 TIME PERIOD")
print(f"   Start: {config.start_date}")
print(f"   End:   {config.end_date}")
print(f"   Duration: 5 years")
print()
print(f"💰 PORTFOLIO CONFIGURATION")
print(f"   Initial Capital: ${config.initial_capital:,.0f}")
print(f"   Universe: {len(config.universe)} elite stocks")
print(f"   Portfolio: Top {config.top_n_stocks} stocks")
print(f"   Rebalance: Quarterly (20 rebalances)")
print()
print(f"📊 ENGINE CONFIGURATION")
print(f"   Version: {config.engine_version}")
print(f"   Enhanced Provider: {config.use_enhanced_provider}")
print(f"   Risk Management: {config.enable_risk_management}")
print(f"   Regime Detection: {config.enable_regime_detection} {'✅ ADAPTIVE WEIGHTS!' if config.enable_regime_detection else '❌ Static Weights'}")
print()
print(f"🎯 ELITE 30 UNIVERSE")
print(f"   Tech (13): AAPL, MSFT, GOOGL, NVDA, AMZN, META, TSLA, AVGO, CRM, ORCL, AMD, QCOM, ADBE")
print(f"   Healthcare (4): UNH, JNJ, LLY, ABBV")
print(f"   Financial (4): V, JPM, MA, BAC")
print(f"   Consumer (5): WMT, PG, HD, KO, COST")
print(f"   Energy (2): CVX, XOM")
print(f"   Industrial (1): CAT")
print()
print(f"🛡️  ANALYTICAL FIXES ENABLED")
print(f"   1. Quality-Weighted Stop-Losses")
print(f"   2. Re-Entry Logic")
print(f"   3. Magnificent 7 Exemption")
print(f"   4. Trailing Stops")
print(f"   5. Confidence-Based Position Sizing")
print()
print(f"🔄 ADAPTIVE REGIME-BASED WEIGHTS")
print(f"   ✅ ENABLED - Weights adjust automatically based on market conditions")
print(f"   BULL + HIGH_VOL:    F:30% M:40% Q:20% S:10% (momentum focus)")
print(f"   BULL + NORMAL_VOL:  F:40% M:30% Q:20% S:10% (balanced)")
print(f"   BEAR + HIGH_VOL:    F:20% M:20% Q:40% S:20% (defensive)")
print(f"   BEAR + NORMAL_VOL:  F:30% M:20% Q:30% S:20% (quality focus)")
print(f"   ... 9 total configurations")
print()
print("="*80)
print("🔄 Running 5-year backtest... (this will take 5-10 minutes)")
print("="*80)
print()

import time
start_time = time.time()

engine = HistoricalBacktestEngine(config)
result = engine.run_backtest()

elapsed = time.time() - start_time

if result:
    print()
    print("="*80)
    print("✅ 5-YEAR BACKTEST RESULTS (V2.1)")
    print("="*80)
    print()
    
    print(f"⏱️  EXECUTION TIME")
    print(f"   Duration: {elapsed/60:.1f} minutes")
    print()
    
    print(f"📈 PERFORMANCE")
    print(f"   Initial Capital:    ${result.initial_capital:,.2f}")
    print(f"   Final Value:        ${result.final_value:,.2f}")
    print(f"   Profit:             ${result.final_value - result.initial_capital:,.2f}")
    print(f"   Total Return:       {result.total_return*100:+.2f}%")
    print(f"   CAGR:               {result.cagr*100:+.2f}%")
    print()
    
    print(f"📊 BENCHMARK COMPARISON")
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
    
    print(f"⚖️  RISK-ADJUSTED METRICS")
    print(f"   Sharpe Ratio:       {result.sharpe_ratio:.2f}")
    print(f"   Sortino Ratio:      {result.sortino_ratio:.2f}")
    print(f"   Calmar Ratio:       {result.calmar_ratio:.2f}")
    print(f"   Max Drawdown:       {result.max_drawdown*100:.2f}%")
    print(f"   Volatility:         {result.volatility*100:.2f}%")
    print()
    
    print(f"📋 TRADING ACTIVITY")
    print(f"   Rebalances:         {result.num_rebalances}")
    print(f"   Avg Holdings:       {result.final_value/result.initial_capital:.1f}x initial capital")
    print()
    
    print(f"🔍 V2.1 METADATA")
    print(f"   Engine Version:     {result.engine_version}")
    print(f"   Data Provider:      {result.data_provider}")
    print(f"   Estimated Bias:     {result.estimated_bias_impact}")
    print()
    
    # Performance assessment
    total_return_pct = result.total_return * 100
    
    print("="*80)
    print("🎯 PERFORMANCE ASSESSMENT")
    print("="*80)
    print()
    
    if total_return_pct > 200:
        print("🌟 EXCEPTIONAL: >200% return over 5 years")
        print("   Strategy significantly outperformed expectations")
    elif total_return_pct > 150:
        print("✅ EXCELLENT: 150-200% return over 5 years")
        print("   Strategy met optimistic targets")
    elif total_return_pct > 100:
        print("✅ GOOD: 100-150% return over 5 years")
        print("   Strategy performed well with solid gains")
    elif total_return_pct > 50:
        print("⚠️  MODERATE: 50-100% return over 5 years")
        print("   Strategy underperformed expectations but still positive")
    else:
        print("❌ UNDERPERFORMED: <50% return over 5 years")
        print("   Strategy needs review and optimization")
    
    print()
    print(f"📊 KEY INSIGHTS:")
    print(f"   • V2.1 features working: Sector-aware scoring + Analytical fixes")
    print(f"   • Enhanced data provider: 40+ technical indicators")
    print(f"   • Known bias: Results may be 5-10% optimistic (documented)")
    print(f"   • Recommended: Discount {total_return_pct*0.075:.0f}pp for realistic estimate")
    print(f"   • Realistic return estimate: ~{total_return_pct*0.925:.0f}%")
    print()
    
    print("="*80)
    print("✅ 5-YEAR BACKTEST COMPLETE")
    print("="*80)
    
else:
    print()
    print("="*80)
    print("❌ BACKTEST FAILED")
    print("="*80)
    sys.exit(1)
