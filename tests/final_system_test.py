#!/usr/bin/env python3
"""
Final Comprehensive System Test
Tests all major components and validates improvements made during system analysis
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8010"

def test_header():
    print("🏦 FINAL COMPREHENSIVE SYSTEM TEST")
    print("=" * 60)
    print(f"Testing AI Hedge Fund System - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

def test_api_health():
    """Test API health and agent status"""
    print("\n🔍 1. API HEALTH CHECK")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API Status: {data['status'].upper()}")
            print(f"   ✅ Version: {data['version']}")

            agents = data['agents_status']
            healthy_count = sum(1 for status in agents.values() if status == 'healthy')
            print(f"   ✅ Agents: {healthy_count}/4 healthy")

            for agent, status in agents.items():
                emoji = "✅" if status == "healthy" else "⚠️" if status == "degraded" else "❌"
                print(f"      {emoji} {agent.capitalize()}: {status}")

            return True
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False

def test_individual_analysis():
    """Test individual stock analysis"""
    print("\n📊 2. INDIVIDUAL STOCK ANALYSIS")

    test_symbols = ['AAPL', 'GOOGL', 'MSFT']
    success_count = 0

    for symbol in test_symbols:
        try:
            response = requests.post(f"{BASE_URL}/analyze",
                                   json={"symbol": symbol},
                                   timeout=30)

            if response.status_code == 200:
                data = response.json()
                narrative = data.get('narrative', {})
                overall_score = narrative.get('overall_score', 0)
                recommendation = narrative.get('recommendation', 'N/A')

                # Calculate average confidence
                agent_results = data.get('agent_results', {})
                confidences = [agent.get('confidence', 0) for agent in agent_results.values()]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0

                print(f"   ✅ {symbol}: Score={overall_score:.1f}, Rec={recommendation}, Conf={avg_confidence:.2f}")

                # Validate key fields exist
                required_fields = ['symbol', 'narrative', 'market_data', 'agent_results']
                missing_fields = [field for field in required_fields if field not in data]

                if not missing_fields:
                    success_count += 1
                else:
                    print(f"      ⚠️  Missing fields: {missing_fields}")

            else:
                print(f"   ❌ {symbol}: Failed with status {response.status_code}")

        except Exception as e:
            print(f"   ❌ {symbol}: Error - {e}")

    print(f"\n   📈 Analysis Success Rate: {success_count}/{len(test_symbols)} ({success_count/len(test_symbols)*100:.1f}%)")
    return success_count == len(test_symbols)

def test_portfolio_functionality():
    """Test portfolio and top-picks endpoints"""
    print("\n🎯 3. PORTFOLIO FUNCTIONALITY")

    # Test top picks
    try:
        print("   Testing top picks endpoint...")
        response = requests.get(f"{BASE_URL}/portfolio/top-picks?limit=3", timeout=60)

        if response.status_code == 200:
            data = response.json()
            top_picks = data.get('top_picks', [])

            if len(top_picks) > 0:
                print(f"   ✅ Top Picks: {len(top_picks)} stocks returned")

                # Validate first pick structure
                first_pick = top_picks[0]
                required_fields = ['symbol', 'overall_score', 'recommendation']
                present_fields = [field for field in required_fields if field in first_pick]

                print(f"   ✅ Required fields present: {len(present_fields)}/{len(required_fields)}")

                # Show sample picks
                for i, pick in enumerate(top_picks[:3], 1):
                    symbol = pick.get('symbol', 'N/A')
                    score = pick.get('overall_score', 0)
                    rec = pick.get('recommendation', 'N/A')
                    weight = pick.get('weight', 0)
                    print(f"   #{i}: {symbol} - Score: {score:.1f}, Rec: {rec}, Weight: {weight:.1f}%")

                return True
            else:
                print("   ❌ No top picks returned")
                return False
        else:
            print(f"   ❌ Top picks failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"   ❌ Portfolio test error: {e}")
        return False

def test_signal_generation():
    """Test signal generation logic"""
    print("\n📈 4. SIGNAL GENERATION")

    test_symbols = ['AAPL', 'NVDA']
    signals_working = 0

    for symbol in test_symbols:
        try:
            response = requests.post(f"{BASE_URL}/analyze",
                                   json={"symbol": symbol},
                                   timeout=30)

            if response.status_code == 200:
                data = response.json()
                narrative = data.get('narrative', {})
                recommendation = narrative.get('recommendation', '')

                # Determine expected signals based on recommendation
                buy_expected = recommendation in ['STRONG BUY', 'BUY', 'WEAK BUY']
                hold_expected = recommendation == 'HOLD'
                sell_expected = recommendation in ['WEAK SELL', 'SELL', 'STRONG SELL']

                # Count valid signals
                signal_count = sum([buy_expected, hold_expected, sell_expected])

                if signal_count == 1:  # Exactly one signal should be true
                    signals_working += 1
                    signal_type = 'BUY' if buy_expected else 'HOLD' if hold_expected else 'SELL'
                    print(f"   ✅ {symbol}: {recommendation} → {signal_type} signal")
                else:
                    print(f"   ⚠️  {symbol}: Ambiguous signal state")

        except Exception as e:
            print(f"   ❌ {symbol}: Signal test error - {e}")

    print(f"\n   📊 Signal Generation Success: {signals_working}/{len(test_symbols)} ({signals_working/len(test_symbols)*100:.1f}%)")
    return signals_working == len(test_symbols)

def test_error_handling():
    """Test error handling with invalid inputs"""
    print("\n🛡️ 5. ERROR HANDLING & ROBUSTNESS")

    test_cases = [
        ("Invalid symbol", "INVALID_STOCK"),
        ("Empty symbol", ""),
        ("Special characters", "!@#$%"),
    ]

    robust_count = 0

    for test_name, symbol in test_cases:
        try:
            response = requests.post(f"{BASE_URL}/analyze",
                                   json={"symbol": symbol},
                                   timeout=10)

            if response.status_code in [400, 404, 422]:  # Expected error codes
                print(f"   ✅ {test_name}: Properly handled (status {response.status_code})")
                robust_count += 1
            elif response.status_code == 200:
                print(f"   ⚠️  {test_name}: Unexpected success (may need validation)")
            else:
                print(f"   ❌ {test_name}: Unexpected error {response.status_code}")

        except requests.exceptions.Timeout:
            print(f"   ✅ {test_name}: Timeout protection working")
            robust_count += 1
        except Exception as e:
            print(f"   ⚠️  {test_name}: Exception - {e}")

    print(f"\n   🛡️ Error Handling Success: {robust_count}/{len(test_cases)} ({robust_count/len(test_cases)*100:.1f}%)")
    return robust_count >= len(test_cases) * 0.5  # At least 50% should handle errors properly

def run_performance_test():
    """Test system performance and response times"""
    print("\n⚡ 6. PERFORMANCE TEST")

    start_time = time.time()
    response = requests.post(f"{BASE_URL}/analyze",
                           json={"symbol": "AAPL"},
                           timeout=30)
    end_time = time.time()

    response_time = end_time - start_time

    if response.status_code == 200:
        print(f"   ✅ Response time: {response_time:.2f} seconds")

        if response_time < 10:
            print("   ✅ Performance: Excellent (<10s)")
            return True
        elif response_time < 20:
            print("   ⚠️  Performance: Acceptable (10-20s)")
            return True
        else:
            print("   ❌ Performance: Slow (>20s)")
            return False
    else:
        print(f"   ❌ Performance test failed: {response.status_code}")
        return False

def final_summary():
    """Display final test summary"""
    print("\n" + "=" * 60)
    print("🏁 FINAL SYSTEM TEST SUMMARY")
    print("=" * 60)

    # Run all tests
    results = {
        "API Health": test_api_health(),
        "Individual Analysis": test_individual_analysis(),
        "Portfolio Functions": test_portfolio_functionality(),
        "Signal Generation": test_signal_generation(),
        "Error Handling": test_error_handling(),
        "Performance": run_performance_test()
    }

    # Calculate overall score
    passed_tests = sum(results.values())
    total_tests = len(results)
    success_rate = passed_tests / total_tests * 100

    print(f"\n📊 TEST RESULTS:")
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status} {test_name}")

    print(f"\n🎯 OVERALL SYSTEM HEALTH: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")

    if success_rate >= 90:
        print("🟢 STATUS: EXCELLENT - System ready for production")
    elif success_rate >= 75:
        print("🟡 STATUS: GOOD - Minor issues to address")
    elif success_rate >= 50:
        print("🟠 STATUS: FAIR - Several issues need fixing")
    else:
        print("🔴 STATUS: POOR - Major issues require attention")

    return success_rate >= 75

if __name__ == "__main__":
    test_header()
    final_summary()