"""
Run 5-year backtest with ENHANCED dashboard configuration
- $10,000 initial capital
- 50 stocks universe (enables real stock rotation)
- Top 20 stocks portfolio (AI-driven selection)
- Quarterly rebalancing
- Real 4-agent analysis
"""
import asyncio
import sys
from datetime import datetime, timedelta
from core.backtesting_engine import HistoricalBacktestEngine, BacktestConfig
from core.risk_manager import RiskLimits
from data.us_top_100_stocks import US_TOP_100_STOCKS
import logging
import json
import pandas as pd
import numpy as np

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def safe_float(value):
    """Safely convert value to float, handling Series/arrays"""
    if isinstance(value, (pd.Series, np.ndarray)):
        return float(value.iloc[0] if isinstance(value, pd.Series) else value[0])
    return float(value) if value is not None else 0.0


def run_backtest_sync():
    """Run 5-year backtest synchronously"""

    print("=" * 80)
    print("🚀 5-YEAR BACKTEST - ENHANCED DASHBOARD CONFIGURATION")
    print("=" * 80)
    print()

    # ENHANCED: Use full 50-stock universe for REAL stock rotation
    # - 50 stocks analyzed each quarter by 4-agent system
    # - Top 20 by AI score are selected for the portfolio
    # - Stocks with declining scores are SOLD
    # - Stocks with rising scores are BOUGHT
    # This creates realistic portfolio turnover based on AI signals
    DASHBOARD_UNIVERSE = US_TOP_100_STOCKS  # 50 elite US stocks

    # 5-year period
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5*365)

    # Configure risk management with conservative limits
    risk_limits = RiskLimits(
        max_portfolio_drawdown=0.15,    # 15% max drawdown → move to cash
        position_stop_loss=0.20,         # 20% stop-loss per stock
        max_volatility=0.30,             # 30% volatility threshold
        max_sector_concentration=0.40,   # 40% max per sector
        max_position_size=0.10,          # 10% max per stock
        cash_buffer_on_drawdown=0.50,   # Move 50% to cash on drawdown
        volatility_scale_factor=0.75     # Reduce 25% when volatile
    )

    config = BacktestConfig(
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        initial_capital=10000.0,  # EXACTLY $10,000 as dashboard shows
        rebalance_frequency='quarterly',  # Quarterly as dashboard specifies
        top_n_stocks=20,  # Top 20 stocks as dashboard shows
        universe=DASHBOARD_UNIVERSE,
        backtest_mode=True,  # Use backtest weights (M:50%, Q:40%, F:5%, S:5%)
        enable_risk_management=True,  # ENABLE RISK MANAGEMENT
        risk_limits=risk_limits,
        enable_regime_detection=True  # ENABLE MARKET REGIME DETECTION
    )

    print(f"📅 Period: {config.start_date} to {config.end_date}")
    print(f"💰 Initial Capital: ${config.initial_capital:,.0f}")
    print(f"🔄 Rebalance: {config.rebalance_frequency.upper()}")
    print(f"📊 Portfolio Size: Top {config.top_n_stocks} stocks")
    print(f"🎯 Universe: {len(config.universe)} stocks")
    print(f"🤖 Real 4-Agent Analysis: {config.backtest_mode}")
    print()
    print("🔄 STOCK ROTATION ENABLED:")
    print(f"   • Analyze {len(config.universe)} stocks each quarter")
    print(f"   • Select top {config.top_n_stocks} by AI composite score")
    print(f"   • Sell stocks that fall out of top {config.top_n_stocks}")
    print(f"   • Buy stocks that enter top {config.top_n_stocks}")
    print()
    print("⚙️  Agent Weights (Backtest Mode):")
    print("   • Momentum: 50% (most reliable for historical data)")
    print("   • Quality: 40% (stable business metrics)")
    print("   • Fundamentals: 5% (has look-ahead bias)")
    print("   • Sentiment: 5% (has look-ahead bias)")
    print()
    print("🛡️  Risk Management ENABLED:")
    print(f"   • Max Drawdown: {risk_limits.max_portfolio_drawdown*100:.0f}% (→ {risk_limits.cash_buffer_on_drawdown*100:.0f}% cash)")
    print(f"   • Position Stop-Loss: {risk_limits.position_stop_loss*100:.0f}%")
    print(f"   • Max Volatility: {risk_limits.max_volatility*100:.0f}%")
    print(f"   • Max Position Size: {risk_limits.max_position_size*100:.0f}%")
    print()
    print("📊 Market Regime Detection ENABLED:")
    print("   • Dynamically adjusts portfolio based on market conditions")
    print("   • BULL markets: 20 stocks, 0-10% cash (aggressive)")
    print("   • BEAR markets: 12-15 stocks, 25-40% cash (defensive)")
    print("   • CRISIS mode: 10 stocks, 50% cash (survival)")
    print()
    print("-" * 80)
    print("🔄 Running backtest... This will take 10-15 minutes for 50-stock universe")
    print("-" * 80)
    print()

    # Run backtest
    engine = HistoricalBacktestEngine(config)
    result = engine.run_backtest()

    if result:
        print()
        print("=" * 80)
        print("✅ 5-YEAR BACKTEST RESULTS")
        print("=" * 80)
        print()

        # Calculate additional metrics
        years = (end_date - start_date).days / 365.25
        total_return_pct = result.total_return * 100

        print(f"📈 PERFORMANCE SUMMARY")
        print(f"   Initial Capital:    ${result.initial_capital:,.2f}")
        print(f"   Final Value:        ${result.final_value:,.2f}")
        print(f"   Total Return:       {total_return_pct:+.2f}%")
        print(f"   CAGR:              {result.cagr*100:+.2f}% per year")
        print()

        print(f"📊 RISK METRICS")
        print(f"   Sharpe Ratio:       {result.sharpe_ratio:.2f}")
        print(f"   Max Drawdown:       {result.max_drawdown*100:.2f}%")
        print(f"   Volatility:         {result.volatility*100:.2f}%")
        print(f"   Sortino Ratio:      {result.sortino_ratio:.2f}")
        print(f"   Calmar Ratio:       {result.calmar_ratio:.2f}")
        print()

        print(f"📅 TRADING ACTIVITY")
        print(f"   Total Rebalances:   {int(result.num_rebalances)}")
        print(f"   Avg per Year:       {int(result.num_rebalances)/years:.1f}")
        print(f"   Equity Curve Points: {len(result.equity_curve)}")
        print()

        # Benchmark comparison (safely convert Series to float)
        spy_return = safe_float(result.spy_return)
        outperformance = safe_float(result.outperformance_vs_spy)
        alpha = safe_float(result.alpha)
        beta = safe_float(result.beta)

        print(f"🎯 VS S&P 500 (SPY)")
        print(f"   SPY Return:         {spy_return*100:+.2f}%")
        print(f"   Our Return:         {total_return_pct:+.2f}%")
        print(f"   Outperformance:     {outperformance*100:+.2f}%")
        print(f"   Alpha:              {alpha*100:+.2f}%")
        print(f"   Beta:               {beta:.2f}")
        print()

        print("=" * 80)
        print("✅ Backtest saved to: data/backtest_results/")
        print("=" * 80)
        print()

        # Summary for user
        print("🎉 BOTTOM LINE")
        print()
        if total_return_pct > 0:
            print(f"   Turning $10,000 into ${result.final_value:,.0f} over 5 years")
            print(f"   That's {result.cagr*100:.1f}% compound annual growth!")
        else:
            print(f"   Portfolio declined from $10,000 to ${result.final_value:,.0f}")
            print(f"   This period included significant market downturns")
        print()

        if result.sharpe_ratio > 1.0:
            print(f"   ✅ Strong risk-adjusted returns (Sharpe: {result.sharpe_ratio:.2f})")
        else:
            print(f"   ⚠️  Risk-adjusted returns below target (Sharpe: {result.sharpe_ratio:.2f})")
        print()

        # Save to JSON for dashboard
        print("💾 Saving results to JSON for dashboard...")

        # Extract trade log from engine
        trade_log = getattr(engine, 'trade_log', [])
        print(f"   📋 Transaction Log: {len(trade_log)} trades")

        result_dict = {
            "config": {
                "start_date": config.start_date,
                "end_date": config.end_date,
                "initial_capital": config.initial_capital,
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
                "information_ratio": result.information_ratio
            },
            "trade_log": trade_log,  # Include all buy/sell transactions with AI scores
            "timestamp": datetime.now().isoformat()
        }

        output_path = f"data/backtest_results/dashboard_5year_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.json"
        with open(output_path, 'w') as f:
            json.dump(result_dict, f, indent=2, default=str)

        print(f"✅ Saved to: {output_path}")
        print()

        return result
    else:
        print()
        print("❌ Backtest failed to complete")
        print()
        return None


if __name__ == "__main__":
    try:
        run_backtest_sync()
    except KeyboardInterrupt:
        print("\n⚠️  Backtest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Backtest failed with error: {e}")
        logger.exception("Backtest error")
        sys.exit(1)
