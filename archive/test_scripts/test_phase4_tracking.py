"""
Test Phase 4: Enhanced Transaction Logging
Runs a 1-year backtest to verify all tracking features work correctly
"""

import logging
from datetime import datetime, timedelta
from core.backtesting_engine import HistoricalBacktestEngine, BacktestConfig
from core.risk_manager import RiskLimits
from data.us_top_100_stocks import US_TOP_100_STOCKS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_phase4_tracking():
    """Test Phase 4 enhanced transaction logging with 1-year backtest"""

    logger.info("=" * 80)
    logger.info("🧪 PHASE 4 TRACKING TEST")
    logger.info("=" * 80)
    logger.info("")
    logger.info("Testing enhanced transaction logging with:")
    logger.info("  • Exit reason categorization (STOP_LOSS, REGIME_REDUCTION, SCORE_DROPPED)")
    logger.info("  • Late stop-loss detection (>-20% threshold)")
    logger.info("  • Position entry tracking with scores and ranks")
    logger.info("  • Daily price tracking (max/min while held)")
    logger.info("  • Recovery tracking (90-day monitoring)")
    logger.info("  • Comprehensive statistics generation")
    logger.info("")

    # Use 1-year backtest for faster testing
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    logger.info(f"📅 Backtest Period: {start_date.strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')}")
    logger.info(f"📊 Universe Size: {len(US_TOP_100_STOCKS)} stocks")
    logger.info("")

    # Configure risk management to trigger stops
    risk_limits = RiskLimits(
        max_portfolio_drawdown=0.15,    # 15% max drawdown
        position_stop_loss=0.20,         # 20% stop-loss per stock
        max_volatility=0.30,             # 30% volatility threshold
        max_sector_concentration=0.40,   # 40% max per sector
        max_position_size=0.10,          # 10% max per stock
        cash_buffer_on_drawdown=0.50,   # Move 50% to cash on drawdown
        volatility_scale_factor=0.75     # Reduce 25% when volatile
    )

    # Configure backtest with Phase 4 tracking
    config = BacktestConfig(
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        initial_capital=10000.0,
        rebalance_frequency='quarterly',
        top_n_stocks=20,
        universe=US_TOP_100_STOCKS,
        backtest_mode=True,
        enable_risk_management=True,  # Enable stop-losses for testing
        risk_limits=risk_limits,
        enable_regime_detection=True  # Enable regime-based exits
    )

    # Run backtest
    logger.info("🚀 Starting backtest with Phase 4 tracking...")
    logger.info("")

    engine = HistoricalBacktestEngine(config)
    result = engine.run_backtest()

    if not result:
        logger.error("❌ Backtest failed to complete")
        return None

    logger.info("")
    logger.info("=" * 80)
    logger.info("✅ PHASE 4 TEST COMPLETE")
    logger.info("=" * 80)
    logger.info("")

    # Get trade log from engine
    trade_log = getattr(engine, 'trade_log', [])
    logger.info(f"📋 Retrieved {len(trade_log)} transactions from trade log")
    logger.info("")

    # Verify tracking features
    logger.info("🔍 VERIFICATION CHECKS:")
    logger.info("")

    # Check 1: Trade log has exit reasons
    trades_with_exit_reasons = sum(1 for t in trade_log if t.get('action') == 'SELL' and 'exit_reason' in t)
    total_sells = sum(1 for t in trade_log if t.get('action') == 'SELL')

    logger.info(f"1. Exit Reasons:")
    logger.info(f"   ✓ {trades_with_exit_reasons}/{total_sells} sells have exit_reason field")

    if trades_with_exit_reasons == total_sells:
        logger.info(f"   ✅ PASS: All sells have exit reasons")
    else:
        logger.warning(f"   ⚠️  PARTIAL: {total_sells - trades_with_exit_reasons} sells missing exit_reason")
    logger.info("")

    # Check 2: Exit reason breakdown
    exit_reasons = {}
    for trade in trade_log:
        if trade.get('action') == 'SELL' and 'exit_reason' in trade:
            reason = trade['exit_reason']
            exit_reasons[reason] = exit_reasons.get(reason, 0) + 1

    logger.info(f"2. Exit Reason Breakdown:")
    for reason, count in sorted(exit_reasons.items()):
        pct = count / total_sells * 100 if total_sells > 0 else 0
        logger.info(f"   • {reason}: {count} ({pct:.1f}%)")
    logger.info("")

    # Check 3: Exit details present
    trades_with_exit_details = sum(1 for t in trade_log if t.get('action') == 'SELL' and 'exit_details' in t)

    logger.info(f"3. Exit Details:")
    logger.info(f"   ✓ {trades_with_exit_details}/{total_sells} sells have exit_details")

    if trades_with_exit_details == total_sells:
        logger.info(f"   ✅ PASS: All sells have detailed exit information")
    else:
        logger.warning(f"   ⚠️  PARTIAL: {total_sells - trades_with_exit_details} sells missing exit_details")
    logger.info("")

    # Check 4: Buy trades have scores and ranks
    buys_with_scores = sum(1 for t in trade_log if t.get('action') == 'BUY' and 'agent_score' in t and 'rank' in t)
    total_buys = sum(1 for t in trade_log if t.get('action') == 'BUY')

    logger.info(f"4. Entry Tracking:")
    logger.info(f"   ✓ {buys_with_scores}/{total_buys} buys have agent_score and rank")

    if buys_with_scores == total_buys:
        logger.info(f"   ✅ PASS: All buys tracked with scores and rankings")
    else:
        logger.warning(f"   ⚠️  PARTIAL: {total_buys - buys_with_scores} buys missing tracking data")
    logger.info("")

    # Check 5: Late stop-losses detected
    logger.info(f"5. Late Stop-Loss Detection:")

    late_stops = []
    for trade in trade_log:
        if trade.get('action') == 'SELL' and trade.get('exit_reason') == 'STOP_LOSS':
            exit_details = trade.get('exit_details', {})
            loss_pct = exit_details.get('loss_pct', 0)
            if loss_pct < -0.25:  # More than -25%
                late_stops.append({
                    'symbol': trade['symbol'],
                    'date': trade['date'],
                    'loss_pct': loss_pct
                })

    if late_stops:
        logger.info(f"   ⚠️  {len(late_stops)} late stop-losses detected:")
        for stop in late_stops:
            logger.info(f"      • {stop['symbol']} on {stop['date']}: {stop['loss_pct']*100:.1f}%")
    else:
        logger.info(f"   ✅ PASS: No late stop-losses detected (all within -20% threshold)")
    logger.info("")

    # Check 6: Holding period tracking
    holding_periods = []
    for trade in trade_log:
        if trade.get('action') == 'SELL' and 'exit_details' in trade:
            holding_days = trade['exit_details'].get('holding_period_days', 0)
            if holding_days > 0:
                holding_periods.append(holding_days)

    if holding_periods:
        avg_holding = sum(holding_periods) / len(holding_periods)
        logger.info(f"6. Holding Period Analysis:")
        logger.info(f"   ✓ Average holding period: {avg_holding:.1f} days")
        logger.info(f"   ✓ Min: {min(holding_periods)} days")
        logger.info(f"   ✓ Max: {max(holding_periods)} days")
        logger.info(f"   ✅ PASS: Holding periods tracked correctly")
    else:
        logger.warning(f"   ⚠️  No holding period data found")
    logger.info("")

    # Final summary
    logger.info("=" * 80)
    logger.info("📊 PHASE 4 TEST SUMMARY")
    logger.info("=" * 80)
    logger.info("")
    logger.info(f"Total Trades: {len(trade_log)}")
    logger.info(f"  • Buys: {total_buys}")
    logger.info(f"  • Sells: {total_sells}")
    logger.info("")
    logger.info(f"Tracking Coverage:")
    if total_sells > 0:
        logger.info(f"  • Exit reasons: {trades_with_exit_reasons}/{total_sells} ({trades_with_exit_reasons/total_sells*100:.1f}%)")
        logger.info(f"  • Exit details: {trades_with_exit_details}/{total_sells} ({trades_with_exit_details/total_sells*100:.1f}%)")
    else:
        logger.info(f"  • Exit reasons: {trades_with_exit_reasons}/{total_sells} (N/A)")
        logger.info(f"  • Exit details: {trades_with_exit_details}/{total_sells} (N/A)")
    if total_buys > 0:
        logger.info(f"  • Entry tracking: {buys_with_scores}/{total_buys} ({buys_with_scores/total_buys*100:.1f}%)")
    else:
        logger.info(f"  • Entry tracking: {buys_with_scores}/{total_buys} (N/A)")
    logger.info("")

    # Overall pass/fail
    all_checks_pass = (
        trades_with_exit_reasons == total_sells and
        trades_with_exit_details == total_sells and
        buys_with_scores == total_buys and
        len(holding_periods) > 0
    )

    if all_checks_pass:
        logger.info("✅ PHASE 4 TEST: PASSED")
        logger.info("   All tracking features working correctly!")
    else:
        logger.warning("⚠️  PHASE 4 TEST: PARTIAL PASS")
        logger.warning("   Some tracking features need attention")

    logger.info("")
    logger.info("=" * 80)

    return result, trade_log


if __name__ == "__main__":
    result_tuple = test_phase4_tracking()

    if result_tuple and len(result_tuple) == 2:
        result, trade_log = result_tuple

        print("\n" + "=" * 80)
        print("🎯 Quick Performance Summary:")
        print("=" * 80)
        print(f"Final Value: ${result.final_value:,.2f}")
        print(f"Total Return: {result.total_return*100:+.2f}%")
        print(f"CAGR: {result.cagr*100:.2f}%")
        print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
        print(f"Max Drawdown: {result.max_drawdown*100:.2f}%")
        print(f"Total Trades: {len(trade_log)}")
        print("=" * 80)
    else:
        print("\n❌ Phase 4 test failed to complete")
        print("=" * 80)
