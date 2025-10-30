#!/usr/bin/env python3
"""
Quick Deep Analysis: Extract insights from most recent backtest results
Analyzes the position tracker data directly from the engine
"""
import os
import sys
from datetime import datetime, timedelta
from collections import defaultdict
from core.backtesting_engine import HistoricalBacktestEngine, BacktestConfig
from core.risk_manager import RiskLimits

# Disable LLM to avoid rate limits
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
print("🔍 QUICK DEEP ANALYSIS: Strategy Performance Insights")
print("="*80)
print()

# Run backtest
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
    enable_regime_detection=False,
    risk_limits=risk_limits,
    engine_version="2.1",
    use_enhanced_provider=True
)

print("Running backtest...")
engine = HistoricalBacktestEngine(config)
result = engine.run_backtest()

if not result:
    print("❌ Backtest failed")
    sys.exit(1)

print()
print("="*80)
print("📊 ANALYZING RESULTS")
print("="*80)
print()

# Access position tracker if available
if hasattr(engine, 'position_tracker') and engine.position_tracker:
    tracker = engine.position_tracker
    all_exits = tracker.get_all_exits()
    
    print(f"Total Position Exits Tracked: {len(all_exits)}")
    print()
    
    # Separate by exit reason
    stop_losses = [e for e in all_exits if e['exit_reason'] == 'STOP_LOSS']
    score_drops = [e for e in all_exits if e['exit_reason'] == 'SCORE_DROPPED']
    regime_exits = [e for e in all_exits if e['exit_reason'] == 'REGIME_REDUCTION']
    normal_exits = [e for e in all_exits if e['exit_reason'] == 'NORMAL_REBALANCE']
    
    print("📊 Exit Breakdown:")
    print(f"   • Stop-Loss Exits:      {len(stop_losses):3d} ({len(stop_losses)/len(all_exits)*100:.1f}%)")
    print(f"   • Score Dropped Exits:  {len(score_drops):3d} ({len(score_drops)/len(all_exits)*100:.1f}%)")
    print(f"   • Regime Exits:         {len(regime_exits):3d} ({len(regime_exits)/len(all_exits)*100:.1f}%)")
    print(f"   • Normal Rebalance:     {len(normal_exits):3d} ({len(normal_exits)/len(all_exits)*100:.1f}%)")
    print()
    
    # Analyze stop-losses
    if stop_losses:
        print("="*80)
        print("🛑 STOP-LOSS ANALYSIS")
        print("="*80)
        print()
        
        late_stops = [e for e in stop_losses if e['pnl_pct'] < -20]
        on_time_stops = [e for e in stop_losses if e['pnl_pct'] >= -20]
        
        print(f"On-time stops (>-20%):  {len(on_time_stops)}")
        print(f"Late stops (<-20%):     {len(late_stops)}")
        print()
        
        if late_stops:
            print("🔴 LATE STOP-LOSSES (Exceeded -20%):")
            print()
            late_stops_sorted = sorted(late_stops, key=lambda x: x['pnl_pct'])
            for exit in late_stops_sorted:
                print(f"   {exit['symbol']:6s}: {exit['pnl_pct']:6.1f}% loss | Held {exit['hold_days']:3d} days | Entry: {exit['entry_date']} | Exit: {exit['exit_date']}")
            print()
            
            avg_late_loss = sum(e['pnl_pct'] for e in late_stops) / len(late_stops)
            print(f"Average late stop loss: {avg_late_loss:.1f}%")
            print(f"Excess loss beyond -20%: {avg_late_loss + 20:.1f}pp")
            print()
        
        # Recovery analysis
        recoveries = tracker.get_recoveries()
        if recoveries:
            print("🔄 RECOVERY ANALYSIS:")
            print(f"   Stopped positions that recovered: {len(recoveries)}/{len(stop_losses)} ({len(recoveries)/len(stop_losses)*100:.1f}%)")
            print()
            
            recovery_time = [r['days_to_recovery'] for r in recoveries if 'days_to_recovery' in r]
            if recovery_time:
                avg_recovery = sum(recovery_time) / len(recovery_time)
                print(f"   Average recovery time: {avg_recovery:.0f} days")
            print()
    
    # Analyze winners vs losers
    winners = [e for e in all_exits if e['pnl_pct'] > 0]
    losers = [e for e in all_exits if e['pnl_pct'] <= 0]
    
    print("="*80)
    print("📊 WIN/LOSS ANALYSIS")
    print("="*80)
    print()
    
    print(f"Winners: {len(winners)} ({len(winners)/len(all_exits)*100:.1f}%)")
    print(f"Losers:  {len(losers)} ({len(losers)/len(all_exits)*100:.1f}%)")
    print()
    
    if winners:
        avg_win = sum(e['pnl_pct'] for e in winners) / len(winners)
        best_win = max(winners, key=lambda x: x['pnl_pct'])
        print(f"Average Winner: +{avg_win:.1f}%")
        print(f"Best Trade: {best_win['symbol']} +{best_win['pnl_pct']:.1f}% (held {best_win['hold_days']} days)")
        print()
    
    if losers:
        avg_loss = sum(e['pnl_pct'] for e in losers) / len(losers)
        worst_loss = min(losers, key=lambda x: x['pnl_pct'])
        print(f"Average Loser: {avg_loss:.1f}%")
        print(f"Worst Trade: {worst_loss['symbol']} {worst_loss['pnl_pct']:.1f}% (held {worst_loss['hold_days']} days)")
        print()
    
    # Win rate by symbol
    symbol_stats = defaultdict(lambda: {'wins': 0, 'losses': 0, 'total_pnl': 0})
    for exit in all_exits:
        symbol = exit['symbol']
        if exit['pnl_pct'] > 0:
            symbol_stats[symbol]['wins'] += 1
        else:
            symbol_stats[symbol]['losses'] += 1
        symbol_stats[symbol]['total_pnl'] += exit['pnl_pct']
    
    print("="*80)
    print("📊 BEST & WORST PERFORMERS")
    print("="*80)
    print()
    
    # Sort by total P&L
    sorted_symbols = sorted(symbol_stats.items(), key=lambda x: x[1]['total_pnl'], reverse=True)
    
    print("Top 10 Best Performing Stocks:")
    for i, (symbol, stats) in enumerate(sorted_symbols[:10], 1):
        total_trades = stats['wins'] + stats['losses']
        win_rate = stats['wins'] / total_trades * 100
        print(f"   {i:2d}. {symbol:6s}: {stats['total_pnl']:+7.1f}% total | {total_trades:2d} trades | {win_rate:5.1f}% win rate")
    print()
    
    print("Top 10 Worst Performing Stocks:")
    for i, (symbol, stats) in enumerate(sorted_symbols[-10:], 1):
        total_trades = stats['wins'] + stats['losses']
        win_rate = stats['wins'] / total_trades * 100
        print(f"   {i:2d}. {symbol:6s}: {stats['total_pnl']:+7.1f}% total | {total_trades:2d} trades | {win_rate:5.1f}% win rate")
    print()

else:
    print("⚠️  Position tracker not available in engine")
    print()

# Overall performance
print("="*80)
print("📊 OVERALL PERFORMANCE SUMMARY")
print("="*80)
print()

print(f"Initial Capital:   ${result.initial_capital:,.2f}")
print(f"Final Value:       ${result.final_value:,.2f}")
print(f"Total Return:      {result.total_return*100:+.2f}%")
print(f"CAGR:              {result.cagr*100:+.2f}%")
print(f"Sharpe Ratio:      {result.sharpe_ratio:.2f}")
print(f"Max Drawdown:      {result.max_drawdown*100:.2f}%")
print()

# Handle pandas Series for spy_return and outperformance_vs_spy
spy_ret = result.spy_return
if hasattr(spy_ret, 'iloc'):
    spy_ret = spy_ret.iloc[0] if len(spy_ret) > 0 else 0
outperf = result.outperformance_vs_spy
if hasattr(outperf, 'iloc'):
    outperf = outperf.iloc[0] if len(outperf) > 0 else 0
print(f"SPY Return:        {spy_ret*100:+.2f}%")
print(f"Outperformance:    {outperf*100:+.2f}%")
print()

print("="*80)
print("🎯 KEY RECOMMENDATIONS")
print("="*80)
print()

print("1. STOP-LOSS OPTIMIZATION")
if hasattr(engine, 'position_tracker') and engine.position_tracker:
    late_stops = [e for e in engine.position_tracker.get_all_exits() 
                  if e['exit_reason'] == 'STOP_LOSS' and e['pnl_pct'] < -20]
    if late_stops:
        print(f"   ❌ {len(late_stops)} trades exceeded -20% stop-loss")
        print("   💡 Implement tighter stops for low-quality stocks (Q<50: 10% stop)")
        print("   💡 Add weekly monitoring to exit deteriorating positions faster")
    else:
        print("   ✅ All stop-losses executed within threshold")
else:
    print("   ⚠️  Data not available")
print()

print("2. CONVICTION-BASED SIZING")
win_rate = len(winners)/len(all_exits)*100 if all_exits else 0
if win_rate > 60:
    print(f"   ✅ Win rate is strong ({win_rate:.1f}%)")
    print("   💡 Consider increasing position size for HIGH conviction trades")
elif win_rate < 50:
    print(f"   ❌ Win rate needs improvement ({win_rate:.1f}%)")
    print("   💡 Reduce position size for LOW conviction trades")
    print("   💡 Consider skipping trades with score <55")
print()

print("3. AGENT WEIGHT OPTIMIZATION")
print("   💡 Current: F:40% M:30% Q:20% S:10%")
print("   💡 Test increasing Momentum to 35-40% (strong technical signals)")
print("   💡 Test increasing Quality to 25% (helps avoid disasters)")
print()

print("4. EARLY EXIT SIGNALS")
print("   💡 Implement mid-quarter score checks (weekly monitoring)")
print("   💡 Exit if score drops >15 points in 2 weeks")
print("   💡 Exit if momentum drops below 30 (rapid deterioration)")
print()

print("="*80)
print("✅ ANALYSIS COMPLETE")
print("="*80)
