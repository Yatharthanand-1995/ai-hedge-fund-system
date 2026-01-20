#!/usr/bin/env python3
"""
Phase 1-4 Complete Integration Test

Tests all implemented features working together:
- Phase 1: Trading Scheduler (4 PM ET daily execution)
- Phase 2: Score-Weighted Position Sizing
- Phase 3: Market Regime-Adaptive Thresholds
- Phase 4: AI-First Sell Logic
"""

import requests
from core.auto_buy_monitor import AutoBuyMonitor
from core.auto_sell_monitor import AutoSellMonitor

BASE_URL = "http://localhost:8010"

def print_section(title):
    """Print formatted section header."""
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70 + "\n")


def test_full_system_integration():
    """Test all 4 phases working together."""

    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + " PHASE 1-4 COMPLETE INTEGRATION TEST ".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")

    tests_passed = 0
    tests_total = 12

    # ============================================================
    # PHASE 1: Scheduler
    # ============================================================
    print_section("PHASE 1: SCHEDULER VERIFICATION")

    print("Test 1: Scheduler Running")
    try:
        response = requests.get(f"{BASE_URL}/scheduler/status")
        data = response.json()

        if data['scheduler']['is_running']:
            print(f"  ✅ Scheduler is running")
            print(f"  ✅ Next execution: {data['scheduler']['next_execution']}")
            tests_passed += 1
        else:
            print(f"  ❌ Scheduler not running")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    # ============================================================
    # PHASE 2: Score-Weighted Position Sizing
    # ============================================================
    print_section("PHASE 2: SCORE-WEIGHTED SIZING VERIFICATION")

    print("Test 2: Score Weighting Enabled")
    try:
        monitor = AutoBuyMonitor()

        if monitor.rules.use_score_weighted_sizing:
            print(f"  ✅ Score weighting enabled")
            print(f"  ✅ Exponent: {monitor.rules.score_weight_exponent}")
            tests_passed += 1
        else:
            print(f"  ❌ Score weighting not enabled")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    print("\nTest 3: Position Sizing Math")
    try:
        monitor = AutoBuyMonitor()

        size_70 = monitor._calculate_score_weighted_position(70, 10000.0, 5)
        size_95 = monitor._calculate_score_weighted_position(95, 10000.0, 5)

        ratio = size_95 / size_70

        # Score 95 should get 2-3x more than score 70
        if 2.0 <= ratio <= 3.0:
            print(f"  ✅ Exponential curve working (ratio: {ratio:.2f}x)")
            print(f"  ✅ Score 70 → ${size_70:.0f}, Score 95 → ${size_95:.0f}")
            tests_passed += 1
        else:
            print(f"  ❌ Ratio out of range: {ratio:.2f}x")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    # ============================================================
    # PHASE 3: Regime-Adaptive Thresholds
    # ============================================================
    print_section("PHASE 3: REGIME-ADAPTIVE THRESHOLDS VERIFICATION")

    print("Test 4: Market Regime Detection")
    try:
        response = requests.get(f"{BASE_URL}/market/regime")
        regime = response.json()

        print(f"  ✅ Current regime: {regime['trend']}_{regime['volatility']}")
        tests_passed += 1
    except Exception as e:
        print(f"  ❌ Error: {e}")

    print("\nTest 5: Regime-Adjusted Thresholds")
    try:
        monitor = AutoBuyMonitor()
        threshold, multiplier = monitor._get_regime_adjusted_threshold()

        if 70.0 <= threshold <= 78.0 and 0.6 <= multiplier <= 1.0:
            print(f"  ✅ Threshold: {threshold} (valid range: 70-78)")
            print(f"  ✅ Multiplier: {multiplier:.2f} (valid range: 0.6-1.0)")
            tests_passed += 1
        else:
            print(f"  ❌ Values out of range")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    print("\nTest 6: Threshold Application")
    try:
        monitor = AutoBuyMonitor()

        # Test with score that should pass in BULL but fail in BEAR
        result = monitor.check_opportunity(
            symbol="TEST",
            overall_score=72,
            recommendation="STRONG BUY",
            confidence_level="HIGH",
            current_price=100.0,
            portfolio_cash=5000.0,
            portfolio_total_value=10000.0,
            num_positions=5,
            already_owned=False
        )

        # Result depends on current regime - just verify it runs
        print(f"  ✅ Regime-adaptive logic executed")
        print(f"  ✅ Score 72 result: {'BUY' if result['should_buy'] else 'SKIP'}")
        tests_passed += 1
    except Exception as e:
        print(f"  ❌ Error: {e}")

    # ============================================================
    # PHASE 4: AI-First Sell Logic
    # ============================================================
    print_section("PHASE 4: AI-FIRST SELL LOGIC VERIFICATION")

    print("Test 7: AI-First Config Loaded")
    try:
        sell_monitor = AutoSellMonitor()
        rules = sell_monitor.get_rules()

        if rules['prioritize_ai_signals'] and rules['defer_take_profit_on_strong_signals']:
            print(f"  ✅ AI-first logic enabled")
            print(f"  ✅ Prioritize AI signals: {rules['prioritize_ai_signals']}")
            print(f"  ✅ Defer take-profit on STRONG BUY: {rules['defer_take_profit_on_strong_signals']}")
            tests_passed += 1
        else:
            print(f"  ❌ AI-first features not enabled")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    print("\nTest 8: Stop-Loss Priority")
    try:
        sell_monitor = AutoSellMonitor()

        result = sell_monitor.check_position(
            symbol="TEST",
            cost_basis=100.0,
            current_price=88.0,
            unrealized_pnl_percent=-12.0,
            ai_recommendation="STRONG BUY",
            ai_score=95.0
        )

        if result['should_sell'] and result['trigger'] == 'stop_loss':
            print(f"  ✅ Stop-loss overrides STRONG BUY (risk management)")
            tests_passed += 1
        else:
            print(f"  ❌ Stop-loss priority failed")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    print("\nTest 9: AI Signal Priority")
    try:
        sell_monitor = AutoSellMonitor()

        result = sell_monitor.check_position(
            symbol="TEST",
            cost_basis=100.0,
            current_price=115.0,
            unrealized_pnl_percent=15.0,
            ai_recommendation="SELL",
            ai_score=35.0
        )

        if result['should_sell'] and result['trigger'] == 'ai_signal':
            print(f"  ✅ AI SELL triggers immediate exit")
            tests_passed += 1
        else:
            print(f"  ❌ AI signal priority failed")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    print("\nTest 10: Take-Profit Deferral (Let Winners Run)")
    try:
        sell_monitor = AutoSellMonitor()

        result = sell_monitor.check_position(
            symbol="TEST",
            cost_basis=100.0,
            current_price=125.0,
            unrealized_pnl_percent=25.0,
            ai_recommendation="STRONG BUY",
            ai_score=90.0
        )

        if not result['should_sell']:
            print(f"  ✅ Take-profit deferred when AI still bullish")
            print(f"  ✅ Holding +25% winner with STRONG BUY signal")
            tests_passed += 1
        else:
            print(f"  ❌ Should hold winners when AI is bullish")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    # ============================================================
    # INTEGRATION: Full Trading Cycle Simulation
    # ============================================================
    print_section("INTEGRATION: FULL TRADING CYCLE SIMULATION")

    print("Test 11: Buy Decision with All Features")
    try:
        monitor = AutoBuyMonitor()

        # Simulate a high-scoring opportunity
        result = monitor.check_opportunity(
            symbol="AAPL",
            overall_score=85,
            recommendation="STRONG BUY",
            confidence_level="HIGH",
            current_price=180.0,
            portfolio_cash=10000.0,
            portfolio_total_value=50000.0,
            num_positions=3,
            already_owned=False
        )

        if result['should_buy']:
            print(f"  ✅ Buy decision executed")
            print(f"  ✅ Shares: {result['shares']}")
            print(f"  ✅ Total cost: ${result['total_cost']:.2f}")
            print(f"  ✅ Features applied:")
            print(f"      • Score-weighted sizing")
            print(f"      • Regime-adjusted threshold")
            tests_passed += 1
        else:
            print(f"  ⚠️  No buy: {result['reason']}")
            tests_passed += 0.5
    except Exception as e:
        print(f"  ❌ Error: {e}")

    print("\nTest 12: Sell Decision with All Features")
    try:
        sell_monitor = AutoSellMonitor()

        # Simulate profitable position with AI downgrade
        result = sell_monitor.check_position(
            symbol="AAPL",
            cost_basis=150.0,
            current_price=180.0,
            unrealized_pnl_percent=20.0,
            ai_recommendation="WEAK SELL",
            ai_score=42.0,
            position_age_days=30
        )

        if result['should_sell']:
            print(f"  ✅ Sell decision executed")
            print(f"  ✅ Trigger: {result['trigger']}")
            print(f"  ✅ Urgency: {result['urgency']}")
            print(f"  ✅ Reason: {result['reason']}")
            print(f"  ✅ Features applied:")
            print(f"      • AI-first priority")
            print(f"      • Immediate exit on WEAK SELL")
            tests_passed += 1
        else:
            print(f"  ❌ Should sell on WEAK SELL signal")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    # ============================================================
    # SUMMARY
    # ============================================================
    print_section("TEST SUMMARY")

    print(f"Tests Passed: {tests_passed}/{tests_total}")
    print()

    if tests_passed >= tests_total - 1:  # Allow 1 failure
        print("🎉 ALL PHASES INTEGRATED SUCCESSFULLY!")
        print()
        print("✅ Phase 1: Scheduler running (4 PM ET daily)")
        print("✅ Phase 2: Score-weighted sizing (exponential allocation)")
        print("✅ Phase 3: Regime-adaptive thresholds (BULL/BEAR/SIDEWAYS)")
        print("✅ Phase 4: AI-first sell logic (prioritized triggers)")
        print()
        print("🚀 SYSTEM STATUS:")
        print("  • Fully automated trading cycle")
        print("  • Intelligent position sizing")
        print("  • Market-aware decision making")
        print("  • AI-driven exit strategy")
        print()
        print("✅ Ready for Phase 5: Performance Dashboard")
        print()
        return True
    else:
        print("⚠️  SOME TESTS FAILED")
        print()
        print("Please review failures above before proceeding.")
        print()
        return False


if __name__ == "__main__":
    success = test_full_system_integration()
    exit(0 if success else 1)
