#!/usr/bin/env python3
"""
Phase 1 & 2 Integration Test

Tests:
- Phase 1: Trading Scheduler (daily execution at 4 PM ET)
- Phase 2: Score-Weighted Position Sizing (exponential allocation)
"""

import requests
import json
from datetime import datetime
from core.auto_buy_monitor import AutoBuyMonitor

BASE_URL = "http://localhost:8010"

def print_section(title):
    """Print formatted section header."""
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70 + "\n")


def test_phase_1_scheduler():
    """Test Phase 1: Trading Scheduler."""
    print_section("PHASE 1: TRADING SCHEDULER TEST")

    tests_passed = 0
    tests_total = 5

    # Test 1: Scheduler Status
    print("Test 1: Scheduler Status Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/scheduler/status")
        data = response.json()

        if data.get('success') and data['scheduler']['is_running']:
            print(f"  ✅ Scheduler is running")
            print(f"  ✅ Next execution: {data['scheduler']['next_execution']}")
            tests_passed += 1
        else:
            print(f"  ❌ Scheduler not running")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    # Test 2: Next Execution Time
    print("\nTest 2: Next Execution Time Validation")
    try:
        response = requests.get(f"{BASE_URL}/scheduler/status")
        data = response.json()
        next_exec = data['scheduler']['next_execution']

        if next_exec and '16:00:00' in next_exec:
            print(f"  ✅ Scheduled for 4 PM ET: {next_exec}")
            tests_passed += 1
        else:
            print(f"  ❌ Incorrect time: {next_exec}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    # Test 3: Execution History
    print("\nTest 3: Execution History Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/scheduler/history")
        data = response.json()

        if data.get('success'):
            print(f"  ✅ History endpoint working")
            print(f"  ✅ Total executions: {data['count']}")
            tests_passed += 1
        else:
            print(f"  ❌ History endpoint failed")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    # Test 4: Scheduler Control (Start/Stop)
    print("\nTest 4: Scheduler Control Endpoints")
    try:
        # Test stop
        response = requests.post(f"{BASE_URL}/scheduler/stop")
        if response.json().get('success'):
            print(f"  ✅ Stop endpoint working")

            # Test start
            response = requests.post(f"{BASE_URL}/scheduler/start")
            if response.json().get('success'):
                print(f"  ✅ Start endpoint working")
                tests_passed += 1
            else:
                print(f"  ❌ Start endpoint failed")
        else:
            print(f"  ❌ Stop endpoint failed")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    # Test 5: Auto-Trade Endpoint Exists
    print("\nTest 5: Auto-Trade Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/portfolio/paper/auto-trade/status")
        data = response.json()

        if data.get('automation_enabled', {}).get('fully_automated'):
            print(f"  ✅ Auto-trade endpoint working")
            print(f"  ✅ System fully automated")
            tests_passed += 1
        else:
            print(f"  ⚠️  System not fully automated (check auto-buy/sell rules)")
            tests_passed += 0.5
    except Exception as e:
        print(f"  ❌ Error: {e}")

    print(f"\n📊 Phase 1 Score: {tests_passed}/{tests_total} tests passed")
    return tests_passed == tests_total


def test_phase_2_score_weighting():
    """Test Phase 2: Score-Weighted Position Sizing."""
    print_section("PHASE 2: SCORE-WEIGHTED POSITION SIZING TEST")

    tests_passed = 0
    tests_total = 5

    # Test 1: Auto-Buy Rules Include Score Weighting
    print("Test 1: Auto-Buy Config Has Score Weighting Fields")
    try:
        response = requests.get(f"{BASE_URL}/portfolio/paper/auto-buy/rules")
        rules = response.json()['rules']

        required_fields = ['use_score_weighted_sizing', 'score_weight_exponent',
                          'min_score_multiplier', 'max_score_multiplier']

        if all(field in rules for field in required_fields):
            print(f"  ✅ All score weighting fields present")
            print(f"  ✅ Score weighting enabled: {rules['use_score_weighted_sizing']}")
            print(f"  ✅ Exponent: {rules['score_weight_exponent']}")
            tests_passed += 1
        else:
            print(f"  ❌ Missing score weighting fields")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    # Test 2: Local Config File Updated
    print("\nTest 2: Local Config File Validation")
    try:
        monitor = AutoBuyMonitor()

        if monitor.rules.use_score_weighted_sizing:
            print(f"  ✅ Score weighting enabled in config")
            print(f"  ✅ Exponent: {monitor.rules.score_weight_exponent}")
            tests_passed += 1
        else:
            print(f"  ❌ Score weighting not enabled")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    # Test 3: Position Sizing Math
    print("\nTest 3: Position Sizing Calculation")
    try:
        monitor = AutoBuyMonitor()
        portfolio_value = 10000.0

        test_cases = [
            (70, 500, 5.0),    # Score 70 → ~$500 (5%)
            (85, 850, 8.5),    # Score 85 → ~$850 (8.5%)
            (95, 1250, 12.5),  # Score 95 → ~$1,250 (12.5%)
        ]

        all_correct = True
        for score, expected_amount, expected_pct in test_cases:
            position_size = monitor._calculate_score_weighted_position(
                overall_score=score,
                portfolio_total_value=portfolio_value,
                num_positions=5
            )

            # Allow 10% tolerance
            tolerance = expected_amount * 0.1
            if abs(position_size - expected_amount) <= tolerance:
                print(f"  ✅ Score {score}: ${position_size:.0f} (~{expected_pct}%)")
            else:
                print(f"  ❌ Score {score}: ${position_size:.0f} (expected ~${expected_amount})")
                all_correct = False

        if all_correct:
            tests_passed += 1
    except Exception as e:
        print(f"  ❌ Error: {e}")

    # Test 4: Exponential Curve Verification
    print("\nTest 4: Exponential Weighting Curve")
    try:
        monitor = AutoBuyMonitor()
        portfolio_value = 10000.0

        size_70 = monitor._calculate_score_weighted_position(70, portfolio_value, 5)
        size_95 = monitor._calculate_score_weighted_position(95, portfolio_value, 5)

        ratio = size_95 / size_70

        # Score 95 should get 2-3x more than score 70
        if 2.0 <= ratio <= 3.0:
            print(f"  ✅ Exponential curve correct")
            print(f"  ✅ Score 95 gets {ratio:.2f}x more than score 70")
            tests_passed += 1
        else:
            print(f"  ❌ Ratio out of range: {ratio:.2f}x (expected 2-3x)")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    # Test 5: Integration with check_opportunity
    print("\nTest 5: Integration with check_opportunity()")
    try:
        monitor = AutoBuyMonitor()

        # Test with score 85
        result = monitor.check_opportunity(
            symbol="TEST",
            overall_score=85,
            recommendation="STRONG BUY",
            confidence_level="HIGH",
            current_price=100.0,
            portfolio_cash=5000.0,
            portfolio_total_value=10000.0,
            num_positions=5,
            already_owned=False
        )

        if result['should_buy'] and result['shares'] >= 8:
            print(f"  ✅ Score 85 triggers buy")
            print(f"  ✅ Buys {result['shares']} shares (score-weighted)")
            tests_passed += 1
        else:
            print(f"  ❌ Unexpected result: {result}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    print(f"\n📊 Phase 2 Score: {tests_passed}/{tests_total} tests passed")
    return tests_passed == tests_total


def test_integration():
    """Test Phase 1 + 2 working together."""
    print_section("INTEGRATION TEST: PHASE 1 + 2")

    print("Test: Scheduler + Score Weighting Integration")
    print()
    print("Simulating automated trading cycle:")
    print("  1. Scheduler triggers at 4 PM ET")
    print("  2. System scans for STRONG BUY signals")
    print("  3. Uses score-weighted sizing for position allocation")
    print("  4. Executes trades with optimal capital allocation")
    print()

    # Verify both systems are configured
    try:
        # Check scheduler
        sched_response = requests.get(f"{BASE_URL}/scheduler/status")
        sched_running = sched_response.json()['scheduler']['is_running']

        # Check auto-buy with score weighting
        rules_response = requests.get(f"{BASE_URL}/portfolio/paper/auto-buy/rules")
        rules = rules_response.json()['rules']
        score_weighting_enabled = rules.get('use_score_weighted_sizing', False)
        auto_buy_enabled = rules.get('enabled', False)

        print(f"✅ Scheduler Running: {sched_running}")
        print(f"✅ Auto-Buy Enabled: {auto_buy_enabled}")
        print(f"✅ Score Weighting Enabled: {score_weighting_enabled}")
        print()

        if sched_running and auto_buy_enabled and score_weighting_enabled:
            print("🎯 INTEGRATION SUCCESS!")
            print()
            print("Your system is now configured for intelligent automated trading:")
            print("  • Daily execution at 4 PM ET")
            print("  • Score-weighted position sizing")
            print("  • Higher scores = larger positions")
            print()
            return True
        else:
            print("⚠️  INTEGRATION INCOMPLETE")
            print("   Some components not enabled")
            return False

    except Exception as e:
        print(f"❌ Integration test error: {e}")
        return False


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + " PHASE 1 & 2 INTEGRATION TEST SUITE ".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")

    # Check API connectivity
    print("\n🔌 Checking API connectivity...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is running\n")
        else:
            print(f"⚠️  API returned status {response.status_code}\n")
    except Exception as e:
        print(f"❌ Cannot connect to API at {BASE_URL}")
        print(f"   Error: {e}")
        print("\n   Please ensure the API server is running:")
        print("   ./start_system.sh\n")
        return

    # Run tests
    phase1_pass = test_phase_1_scheduler()
    phase2_pass = test_phase_2_score_weighting()
    integration_pass = test_integration()

    # Summary
    print_section("TEST SUMMARY")

    results = [
        ("Phase 1: Trading Scheduler", phase1_pass),
        ("Phase 2: Score-Weighted Sizing", phase2_pass),
        ("Integration Test", integration_pass)
    ]

    print("Test Results:")
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {test_name}")

    all_passed = all(passed for _, passed in results)

    print()
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print()
        print("✅ Phase 1 & 2 are working correctly")
        print("✅ Ready to proceed to Phase 3 (Regime-Adaptive Signals)")
        print()
    else:
        print("⚠️  SOME TESTS FAILED")
        print()
        print("Please review the failures above before proceeding.")
        print()

    print("="*70)
    print()


if __name__ == "__main__":
    main()
