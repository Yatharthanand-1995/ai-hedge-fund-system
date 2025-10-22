"""
Run ANALYTICAL FIXES backtest: 5 data-driven improvements to stop-loss strategy

This backtest includes ALL 5 analytical fixes:
1. Quality-Weighted Stop-Losses: NVDA (Q=70) gets 30% stop vs junk (Q=30) gets 10%
2. Re-Entry Logic: Allow re-buying stopped stocks if Fundamentals > 65
3. Magnificent 7 Exemption: MSFT, GOOGL, NVDA exempt from momentum veto
4. Trailing Stops: Exit on -20% from PEAK, not entry (protects profits, lets winners run)
5. Confidence-Based Position Sizing: High-conviction (score>70, Q>70) gets 6%, weak gets 2%

Expected Result: 180-220% return (vs 133% with naive exits)
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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/analytical_fixes_backtest.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def run_analytical_fixes_backtest():
    """Run backtest with ALL 5 analytical fixes"""

    print("=" * 80)
    print("🎯 ANALYTICAL FIXES BACKTEST: 5 Data-Driven Improvements")
    print("=" * 80)
    print()

    end_date = datetime.now()
    start_date = end_date - timedelta(days=5*365)

    # ANALYTICAL FIX #1 & #4: Quality-weighted and trailing stop-losses
    risk_limits = RiskLimits(
        max_portfolio_drawdown=0.15,    # 15% max drawdown
        position_stop_loss=0.20,         # Base stop-loss (will be adjusted by quality)
        max_volatility=0.25,             # 25% volatility threshold
        max_sector_concentration=0.40,   # 40% max per sector
        max_position_size=0.10,          # 10% max per position
        cash_buffer_on_drawdown=0.50,   # Move 50% to cash on drawdown
        volatility_scale_factor=0.5      # Reduce 50% when vol > threshold
    )

    config = BacktestConfig(
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        initial_capital=10000.0,
        rebalance_frequency='quarterly',
        top_n_stocks=20,
        universe=US_TOP_100_STOCKS,  # 50-stock universe
        backtest_mode=True,
        enable_risk_management=True,   # Enable analytical stop-losses
        enable_regime_detection=False,  # Disable for clean comparison
        risk_limits=risk_limits
    )

    print(f"📅 Period: {config.start_date} to {config.end_date}")
    print(f"💰 Initial Capital: ${config.initial_capital:,.0f}")
    print(f"🎯 Universe: {len(config.universe)} stocks")
    print(f"📊 Portfolio: Top {config.top_n_stocks} stocks")
    print(f"🔄 Rebalance: Quarterly")
    print()
    print("✅ ANALYTICAL FIXES ENABLED:")
    print("   1. Quality-Weighted Stop-Losses")
    print("      • High quality (Q>70): 30% stop (let them recover)")
    print("      • Medium quality (Q 50-70): 20% stop")
    print("      • Low quality (Q<50): 10% stop (tight control)")
    print()
    print("   2. Re-Entry Logic")
    print("      • Allow re-buying stopped stocks if Fundamentals > 65")
    print("      • Captures recovery opportunities (e.g., NVDA after 2022 crash)")
    print()
    print("   3. Magnificent 7 Exemption")
    print("      • AAPL, MSFT, GOOGL, NVDA, AMZN, META, TSLA")
    print("      • Exempt from momentum veto during crashes")
    print("      • Low momentum = BUYING OPPORTUNITY, not sell signal")
    print()
    print("   4. Trailing Stops (Not Fixed Stops)")
    print("      • Track highest price while held")
    print("      • Exit only if drops >20% from PEAK, not entry")
    print("      • Protects profits, lets winners run")
    print()
    print("   5. Confidence-Based Position Sizing")
    print("      • High conviction (score>70, Q>70): 6% position")
    print("      • Medium conviction (score 55-70): 4% position")
    print("      • Low conviction (score 45-55): 2% position")
    print()
    print("📈 EXPECTED RESULT: 180-220% return (vs 133% with naive exits)")
    print()
    print("-" * 80)
    print("🔄 Running analytical fixes backtest...")
    print("-" * 80)
    print()

    # Run backtest
    engine = HistoricalBacktestEngine(config)
    result = engine.run_backtest()

    if result:
        print()
        print("=" * 80)
        print("✅ ANALYTICAL FIXES RESULTS")
        print("=" * 80)
        print()

        total_return_pct = result.total_return * 100

        print(f"📈 PERFORMANCE")
        print(f"   Final Value:        ${result.final_value:,.2f}")
        print(f"   Total Return:       {total_return_pct:+.2f}%")
        print(f"   CAGR:              {result.cagr*100:+.2f}%")
        print(f"   Sharpe Ratio:       {result.sharpe_ratio:.2f}")
        print(f"   Max Drawdown:       {result.max_drawdown*100:.2f}%")
        print()

        print("🎯 ANALYTICAL FIXES IMPACT:")
        print(f"   • Baseline (no protection):     190% (expected)")
        print(f"   • Naive exits (old system):     133%")
        print(f"   • Analytical fixes (THIS run):  {total_return_pct:.1f}%")
        print()

        if total_return_pct > 180:
            print("✅ SUCCESS: Analytical fixes beat baseline!")
            print("   Data-driven approach > naive rules")
        elif total_return_pct > 133:
            print("✅ IMPROVEMENT: Beat naive exits")
            print(f"   Gained {total_return_pct - 133:.1f} pp vs naive system")
        else:
            print("⚠️  UNDERPERFORMED: Need more analysis")
            print("   Check if 2022-24 period is not representative")

        print()
        return result
    else:
        print("❌ Analytical fixes backtest failed")
        return None


if __name__ == "__main__":
    try:
        run_analytical_fixes_backtest()
    except KeyboardInterrupt:
        print("\n⚠️  Backtest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Backtest failed: {e}")
        logger.exception("Backtest error")
        sys.exit(1)
