"""
Run a comprehensive 5-year backtest (2020-2025) to show system performance
"""
import asyncio
from datetime import datetime, timedelta
from core.backtesting_engine import BacktestingEngine, BacktestConfig

async def run_5year_backtest():
    """Run 5-year backtest with real 4-agent analysis"""

    print("=" * 80)
    print("🚀 5-YEAR BACKTEST (2020-2025)")
    print("=" * 80)
    print()

    # Define 10-stock universe (top performers across sectors)
    BACKTEST_UNIVERSE = [
        'AAPL',   # Technology
        'MSFT',   # Technology
        'GOOGL',  # Technology
        'AMZN',   # Consumer Cyclical
        'NVDA',   # Technology
        'META',   # Technology
        'TSLA',   # Consumer Cyclical
        'V',      # Financial Services
        'JPM',    # Financial Services
        'UNH'     # Healthcare
    ]

    # Configure 5-year backtest
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5*365)

    config = BacktestConfig(
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        initial_capital=100000.0,
        rebalance_frequency='monthly',
        top_n=8,
        universe=BACKTEST_UNIVERSE,
        use_real_agents=True
    )

    print(f"📅 Period: {config.start_date} to {config.end_date}")
    print(f"💰 Initial Capital: ${config.initial_capital:,.0f}")
    print(f"🔄 Rebalance: {config.rebalance_frequency}")
    print(f"📊 Portfolio Size: Top {config.top_n} stocks")
    print(f"🎯 Universe: {len(config.universe)} stocks")
    print(f"🤖 Real 4-Agent Analysis: {config.use_real_agents}")
    print()
    print("⚙️  Agent Weights (Backtest Mode):")
    print("   • Momentum: 50% (most reliable for historical data)")
    print("   • Quality: 40% (stable business metrics)")
    print("   • Fundamentals: 5% (has look-ahead bias)")
    print("   • Sentiment: 5% (has look-ahead bias)")
    print()
    print("-" * 80)
    print("🔄 Running backtest... This will take 5-10 minutes for 5 years of data")
    print("-" * 80)
    print()

    # Run backtest
    engine = BacktestingEngine(config)
    results = await engine.run_backtest()

    if results:
        print()
        print("=" * 80)
        print("✅ 5-YEAR BACKTEST RESULTS")
        print("=" * 80)
        print()

        # Calculate additional metrics
        years = (end_date - start_date).days / 365.25
        cagr = (results['final_value'] / results['initial_capital']) ** (1/years) - 1
        total_return_pct = results['total_return'] * 100

        print(f"📈 PERFORMANCE SUMMARY")
        print(f"   Initial Capital:    ${results['initial_capital']:,.2f}")
        print(f"   Final Value:        ${results['final_value']:,.2f}")
        print(f"   Total Return:       {total_return_pct:+.2f}%")
        print(f"   CAGR:              {cagr*100:+.2f}% per year")
        print()

        print(f"📊 RISK METRICS")
        print(f"   Sharpe Ratio:       {results['metrics']['sharpe_ratio']:.2f}")
        print(f"   Max Drawdown:       {results['metrics']['max_drawdown']*100:.2f}%")
        print(f"   Volatility:         {results['metrics']['volatility']*100:.2f}%")
        print(f"   Sortino Ratio:      {results['metrics'].get('sortino_ratio', 0):.2f}")
        print(f"   Calmar Ratio:       {results['metrics'].get('calmar_ratio', 0):.2f}")
        print()

        print(f"📅 TRADING ACTIVITY")
        print(f"   Total Rebalances:   {int(results['rebalances'])}")
        print(f"   Avg per Year:       {int(results['rebalances'])/years:.1f}")
        print(f"   Equity Curve Points: {len(results['equity_curve'])}")
        print()

        # Benchmark comparison
        if 'spy_return' in results and results['spy_return']:
            spy_return = results['spy_return'][0] if isinstance(results['spy_return'], list) else results['spy_return']
            outperformance = results['outperformance_vs_spy'][0] if isinstance(results['outperformance_vs_spy'], list) else results['outperformance_vs_spy']

            print(f"🎯 VS S&P 500 (SPY)")
            print(f"   SPY Return:         {spy_return*100:+.2f}%")
            print(f"   Our Return:         {total_return_pct:+.2f}%")
            print(f"   Outperformance:     {outperformance*100:+.2f}%")
            print()

        # Recent rebalances
        print(f"📋 RECENT REBALANCES (Last 5)")
        print()
        for i, rebalance in enumerate(results['rebalance_log'][:5], 1):
            print(f"   {i}. {rebalance['date']}")
            print(f"      Portfolio: {', '.join(rebalance['portfolio'][:8])}")
            if 'avg_score' in rebalance:
                print(f"      Avg Score: {rebalance['avg_score']:.1f}")
            print()

        print("=" * 80)
        print("✅ Backtest saved to: data/backtest_results/")
        print("=" * 80)
        print()

        # Summary for user
        print("🎉 BOTTOM LINE")
        print()
        if total_return_pct > 0:
            print(f"   Turning $100,000 into ${results['final_value']:,.0f} over 5 years")
            print(f"   That's {cagr*100:.1f}% compound annual growth!")
        else:
            print(f"   Portfolio declined from $100,000 to ${results['final_value']:,.0f}")
            print(f"   This period included significant market downturns")
        print()

        if results['metrics']['sharpe_ratio'] > 1.0:
            print(f"   ✅ Strong risk-adjusted returns (Sharpe: {results['metrics']['sharpe_ratio']:.2f})")
        else:
            print(f"   ⚠️  Risk-adjusted returns below target (Sharpe: {results['metrics']['sharpe_ratio']:.2f})")
        print()

        return results
    else:
        print()
        print("❌ Backtest failed to complete")
        print()
        return None

if __name__ == "__main__":
    asyncio.run(run_5year_backtest())
