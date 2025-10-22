"""
Run FAIR BASELINE: 50-stock universe with NO early exit protection
- Same universe as improved system (50 stocks)
- NO stop-losses
- NO momentum veto early warning
- NO score deterioration
- Only natural rank-based exits (quarterly rebalance)

This provides apples-to-apples comparison
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
        logging.FileHandler('/tmp/baseline_50stocks.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def run_baseline():
    """Run clean baseline with 50-stock universe, NO protection"""

    print("=" * 80)
    print("🎯 FAIR BASELINE: 50-Stock Universe, NO Early Exit Protection")
    print("=" * 80)
    print()

    end_date = datetime.now()
    start_date = end_date - timedelta(days=5*365)

    # DISABLE all early exit protection for fair baseline
    risk_limits = RiskLimits(
        max_portfolio_drawdown=0.99,    # Effectively disabled (99%)
        position_stop_loss=0.99,         # Effectively disabled (99%)
        max_volatility=0.99,             # Effectively disabled
        max_sector_concentration=1.0,   # No sector limits
        max_position_size=0.20,          # Allow 20% per stock
        cash_buffer_on_drawdown=0.0,   # Never move to cash
        volatility_scale_factor=1.0     # No volatility scaling
    )

    config = BacktestConfig(
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        initial_capital=10000.0,
        rebalance_frequency='quarterly',
        top_n_stocks=20,
        universe=US_TOP_100_STOCKS,  # Same 50-stock universe
        backtest_mode=True,
        enable_risk_management=False,  # DISABLE risk management (no stop-losses)
        enable_regime_detection=False  # DISABLE regime detection
    )

    print(f"📅 Period: {config.start_date} to {config.end_date}")
    print(f"💰 Initial Capital: ${config.initial_capital:,.0f}")
    print(f"🎯 Universe: {len(config.universe)} stocks (SAME as improved system)")
    print(f"📊 Portfolio: Top {config.top_n_stocks} stocks")
    print(f"🔄 Rebalance: Quarterly")
    print()
    print("⚠️  BASELINE CONFIGURATION (No Protection):")
    print("   • NO stop-losses")
    print("   • NO momentum veto")
    print("   • NO regime detection")
    print("   • NO score deterioration tracking")
    print("   • Only rank-based exits (natural quarterly rebalancing)")
    print()
    print("This is the FAIR comparison to see if protection helps or hurts.")
    print()
    print("-" * 80)
    print("🔄 Running baseline backtest...")
    print("-" * 80)
    print()

    # Run backtest
    engine = HistoricalBacktestEngine(config)
    result = engine.run_backtest()

    if result:
        print()
        print("=" * 80)
        print("✅ BASELINE RESULTS (50-Stock Universe, No Protection)")
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

        print("✅ This is the TRUE baseline for 50-stock universe.")
        print("   Compare future improvements against THIS number.")
        print()

        return result
    else:
        print("❌ Baseline backtest failed")
        return None


if __name__ == "__main__":
    try:
        run_baseline()
    except KeyboardInterrupt:
        print("\\n⚠️  Baseline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\\n❌ Baseline failed: {e}")
        logger.exception("Baseline error")
        sys.exit(1)
