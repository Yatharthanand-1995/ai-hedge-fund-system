"""
Backtest Version Comparison Tool
Compares V1.x (minimal indicators) vs V2.0 (EnhancedYahooProvider) backtests
"""
import sys
from datetime import datetime, timedelta
from core.backtesting_engine import HistoricalBacktestEngine, BacktestConfig
import logging
import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def compare_backtest_versions():
    """
    Compare V1.x vs V2.0 backtest performance

    Expected differences:
    - V2.0 should have slightly different results due to 40+ indicators vs 3 indicators
    - Both should show ~5-10% optimistic bias due to look-ahead in fundamentals/sentiment
    - Performance difference should be <5% (data quality, not strategy difference)
    """

    print("=" * 80)
    print("📊 BACKTEST VERSION COMPARISON: V1.x vs V2.0")
    print("=" * 80)
    print()

    # Test period: 6 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)

    # Small universe for quick comparison
    test_universe = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'AMZN', 'META', 'TSLA']

    print(f"📅 Test Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"🎯 Test Universe: {len(test_universe)} stocks (Magnificent 7)")
    print(f"📊 Portfolio Size: Top 5 stocks")
    print(f"🔄 Rebalance: Monthly")
    print()

    # ========================================================================
    # V1.x: Minimal indicators (RSI, SMA20, SMA50)
    # ========================================================================
    print("-" * 80)
    print("🔵 Running V1.x Backtest (Minimal Indicators)")
    print("-" * 80)
    print()

    config_v1 = BacktestConfig(
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        initial_capital=10000.0,
        rebalance_frequency='monthly',
        top_n_stocks=5,
        universe=test_universe,
        enable_risk_management=False,
        enable_regime_detection=False,
        engine_version="1.0",
        use_enhanced_provider=False  # V1.x: Minimal indicators
    )

    try:
        engine_v1 = HistoricalBacktestEngine(config_v1)
        result_v1 = engine_v1.run_backtest()
    except Exception as e:
        logger.error(f"V1.x backtest failed: {e}")
        result_v1 = None

    # ========================================================================
    # V2.0: EnhancedYahooProvider (40+ indicators)
    # ========================================================================
    print()
    print("-" * 80)
    print("🟢 Running V2.0 Backtest (EnhancedYahooProvider, 40+ Indicators)")
    print("-" * 80)
    print()

    config_v2 = BacktestConfig(
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        initial_capital=10000.0,
        rebalance_frequency='monthly',
        top_n_stocks=5,
        universe=test_universe,
        enable_risk_management=False,
        enable_regime_detection=False,
        engine_version="2.0",
        use_enhanced_provider=True  # V2.0: Full indicators
    )

    try:
        engine_v2 = HistoricalBacktestEngine(config_v2)
        result_v2 = engine_v2.run_backtest()
    except Exception as e:
        logger.error(f"V2.0 backtest failed: {e}")
        result_v2 = None

    # ========================================================================
    # Comparison
    # ========================================================================
    print()
    print("=" * 80)
    print("📊 COMPARISON RESULTS")
    print("=" * 80)
    print()

    if not result_v1 or not result_v2:
        print("❌ One or both backtests failed. Cannot compare.")
        return False

    # Create comparison table
    comparison = pd.DataFrame({
        'Metric': [
            'Engine Version',
            'Data Provider',
            'Final Value',
            'Total Return',
            'CAGR',
            'Sharpe Ratio',
            'Max Drawdown',
            'Number of Trades',
            'Win Rate'
        ],
        'V1.x (Minimal)': [
            result_v1.engine_version,
            result_v1.data_provider,
            f"${result_v1.final_value:,.2f}",
            f"{result_v1.total_return*100:+.2f}%",
            f"{result_v1.cagr*100:+.2f}%",
            f"{result_v1.sharpe_ratio:.2f}",
            f"{result_v1.max_drawdown*100:.2f}%",
            result_v1.num_trades,
            f"{result_v1.win_rate*100:.1f}%"
        ],
        'V2.0 (Enhanced)': [
            result_v2.engine_version,
            result_v2.data_provider,
            f"${result_v2.final_value:,.2f}",
            f"{result_v2.total_return*100:+.2f}%",
            f"{result_v2.cagr*100:+.2f}%",
            f"{result_v2.sharpe_ratio:.2f}",
            f"{result_v2.max_drawdown*100:.2f}%",
            result_v2.num_trades,
            f"{result_v2.win_rate*100:.1f}%"
        ]
    })

    print(comparison.to_string(index=False))
    print()

    # Calculate differences
    return_diff = (result_v2.total_return - result_v1.total_return) * 100
    sharpe_diff = result_v2.sharpe_ratio - result_v1.sharpe_ratio
    drawdown_diff = (result_v2.max_drawdown - result_v1.max_drawdown) * 100

    print("📈 PERFORMANCE DIFFERENCES (V2.0 vs V1.x):")
    print(f"   Total Return: {return_diff:+.2f} pp")
    print(f"   Sharpe Ratio: {sharpe_diff:+.2f}")
    print(f"   Max Drawdown: {drawdown_diff:+.2f} pp")
    print()

    # Analysis
    print("🔍 ANALYSIS:")
    print()

    if abs(return_diff) < 2.0:
        print("   ✅ MINOR DIFFERENCE (<2 pp): V1.x and V2.0 perform similarly")
        print("      → Data quality improvements in V2.0 don't significantly change strategy")
    elif abs(return_diff) < 5.0:
        print("   ⚠️  MODERATE DIFFERENCE (2-5 pp): V2.0 provides modest improvement")
        print("      → Enhanced indicators (40+ vs 3) provide some edge")
    else:
        print("   🚨 SIGNIFICANT DIFFERENCE (>5 pp): Large divergence between versions")
        print("      → Investigate if technical indicators are driving different stock picks")

    print()

    if sharpe_diff > 0.2:
        print("   ✅ V2.0 BETTER RISK-ADJUSTED RETURNS: Higher Sharpe ratio")
    elif sharpe_diff < -0.2:
        print("   ⚠️  V1.x BETTER RISK-ADJUSTED RETURNS: Higher Sharpe ratio")
    else:
        print("   ℹ️  SIMILAR RISK-ADJUSTED RETURNS: Sharpe ratios within 0.2")

    print()

    print("📋 DATA LIMITATIONS (Both Versions):")
    print("   Both V1.x and V2.0 have the same look-ahead bias:")
    for agent, limitation in result_v2.data_limitations.items():
        print(f"   • {agent}: {limitation}")

    print()
    print(f"⚠️  {result_v2.estimated_bias_impact}")
    print()

    print("=" * 80)
    print("✅ COMPARISON COMPLETE")
    print("=" * 80)
    print()

    print("💡 RECOMMENDATIONS:")
    print("   1. Use V2.0 for production backtests (better data quality)")
    print("   2. Adjust results down 5-10% to account for look-ahead bias")
    print("   3. Focus on relative performance vs absolute returns")
    print("   4. Consider V2.0 as the new baseline for future backtests")
    print()

    return True


if __name__ == "__main__":
    try:
        success = compare_backtest_versions()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Comparison interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Comparison failed: {e}")
        logger.exception("Comparison error")
        sys.exit(1)
