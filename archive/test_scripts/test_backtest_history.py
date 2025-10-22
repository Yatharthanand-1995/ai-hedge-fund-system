"""
Test script to verify /backtest/history endpoint uses real stored results
Tests the fix for Issue #3: Synthetic scenario generation replaced with real storage
"""

import requests
import json
from datetime import datetime, timedelta

# API base URL
BASE_URL = "http://localhost:8010"

def test_backtest_history_endpoint():
    """Test that /backtest/history returns real stored results"""

    print("\n" + "="*80)
    print("🧪 TEST: /backtest/history Endpoint - Real Storage vs Synthetic Data")
    print("="*80 + "\n")

    # First, run a backtest to create stored results
    print("📝 Step 1: Running a backtest to create stored results...")
    print("-"*80 + "\n")

    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

    backtest_config = {
        "start_date": start_date,
        "end_date": end_date,
        "rebalance_frequency": "monthly",
        "top_n": 5,
        "universe": ["AAPL", "MSFT", "GOOGL"],
        "initial_capital": 10000.0
    }

    print(f"📅 Backtest Period: {start_date} to {end_date}")
    print(f"💰 Initial Capital: ${backtest_config['initial_capital']:,.2f}")
    print(f"📊 Universe: {', '.join(backtest_config['universe'])}")

    try:
        # Run backtest
        print("\n🚀 Running backtest...")
        response = requests.post(
            f"{BASE_URL}/backtest/run",
            json=backtest_config,
            timeout=300
        )

        if response.status_code != 200:
            print(f"\n❌ Backtest failed with status code: {response.status_code}")
            print(f"Error: {response.text}")
            return False

        backtest_result = response.json()
        backtest_id = backtest_result.get('backtest_id')

        print(f"✅ Backtest completed successfully!")
        if backtest_id:
            print(f"💾 Backtest ID: {backtest_id}")
        print(f"📈 Total Return: {backtest_result['results']['total_return']*100:.2f}%")

        # Now test the history endpoint
        print("\n" + "="*80)
        print("📝 Step 2: Testing /backtest/history endpoint...")
        print("-"*80 + "\n")

        print("🚀 Fetching backtest history...")
        history_response = requests.get(f"{BASE_URL}/backtest/history?limit=5", timeout=30)

        if history_response.status_code != 200:
            print(f"\n❌ History request failed with status code: {history_response.status_code}")
            print(f"Error: {history_response.text}")
            return False

        history = history_response.json()

        print("\n" + "="*80)
        print("📊 BACKTEST HISTORY RESULTS")
        print("="*80 + "\n")

        if not history:
            print("⚠️ No backtest history found (empty list returned)")
            print("\nThis could mean:")
            print("  • Storage is working but no results saved yet")
            print("  • Backtest ID was not saved properly")
            return False

        print(f"✅ Found {len(history)} backtest result(s) in history")
        print("\n" + "-"*80 + "\n")

        # Validate history structure
        validations = []

        # Check 1: History is a list
        if isinstance(history, list):
            validations.append("✓ History is a list (not synthetic scenarios)")
        else:
            validations.append("✗ History is not a list")

        # Check 2: Results have backtest_id
        if history and 'backtest_id' in history[0]:
            validations.append("✓ Results contain backtest_id (real storage)")
        else:
            validations.append("✗ Results missing backtest_id")

        # Check 3: Results have timestamp
        if history and 'timestamp' in history[0]:
            validations.append("✓ Results contain timestamp")
        else:
            validations.append("✗ Results missing timestamp")

        # Check 4: Results have real metrics (not hardcoded values)
        if history:
            first_result = history[0]
            # Check if this matches our just-run backtest
            if backtest_id and first_result.get('backtest_id') == backtest_id:
                validations.append("✓ Most recent result matches just-run backtest")
            else:
                validations.append("✗ Recent result doesn't match just-run backtest")

        # Check 5: No synthetic scenario markers
        synthetic_markers = ["base_scenarios", "multiplier", "fallback"]
        has_synthetic_markers = any(
            marker in str(history).lower() for marker in synthetic_markers
        )
        if not has_synthetic_markers:
            validations.append("✓ No synthetic scenario generation markers found")
        else:
            validations.append("✗ Contains synthetic scenario markers")

        # Display sample results
        print("📋 Sample Backtest History Entries:\n")
        for i, result in enumerate(history[:3], 1):
            print(f"   Entry {i}:")
            print(f"      • Backtest ID: {result.get('backtest_id', 'N/A')}")
            print(f"      • Period: {result.get('start_date')} to {result.get('end_date')}")
            print(f"      • Total Return: {result.get('total_return', 0)*100:.2f}%")
            print(f"      • Sharpe Ratio: {result.get('sharpe_ratio', 0):.2f}")
            print(f"      • Max Drawdown: {result.get('max_drawdown', 0)*100:.2f}%")
            print(f"      • Rebalances: {result.get('num_rebalances', 0)}")
            print(f"      • Timestamp: {result.get('timestamp', 'N/A')}")
            print()

        # Validation summary
        print("="*80)
        print("✅ VALIDATION CHECKS")
        print("="*80 + "\n")

        for validation in validations:
            print(validation)

        passed = all('✓' in v for v in validations)

        if passed:
            print("\n" + "="*80)
            print("✅ TEST PASSED: /backtest/history uses REAL storage!")
            print("="*80)
            print("\nEvidence:")
            print("✓ Returns stored backtest results (not synthetic scenarios)")
            print("✓ Results contain backtest_id and timestamp")
            print("✓ Most recent result matches just-run backtest")
            print("✓ No synthetic generation markers found")
            print("✓ Issue #3 is FIXED")
            return True
        else:
            print("\n" + "="*80)
            print("⚠️ TEST WARNING: Some validations failed")
            print("="*80)
            return False

    except requests.exceptions.Timeout:
        print("\n❌ Request timed out")
        return False
    except Exception as e:
        print("\n" + "="*80)
        print("❌ TEST FAILED")
        print("="*80)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is running and healthy")
            return True
        else:
            print(f"⚠️ API returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API is not accessible: {e}")
        print(f"\nPlease start the API server:")
        print(f"  cd /Users/yatharthanand/ai_hedge_fund_system")
        print(f"  python -m api.main")
        return False


if __name__ == "__main__":
    print("\n" + "🔬 " + "="*76 + " 🔬")
    print("   /BACKTEST/HISTORY ENDPOINT VALIDATION")
    print("   Testing Real Storage vs Synthetic Data Generation")
    print("🔬 " + "="*76 + " 🔬\n")

    # Check API health first
    print("📡 Checking API status...")
    if not check_api_health():
        print("\n❌ Cannot run test - API not available")
        exit(1)

    print("\n" + "-"*80 + "\n")

    # Run test
    success = test_backtest_history_endpoint()

    # Final summary
    print("\n" + "="*80)
    print("📋 TEST SUMMARY")
    print("="*80)

    if success:
        print("\n🎉 SUCCESS!")
        print("\n✅ The /backtest/history endpoint now uses REAL storage")
        print("✅ Synthetic scenario generation has been replaced")
        print("✅ Issue #3 is FIXED")
        exit(0)
    else:
        print("\n❌ TEST FAILED - Review output above")
        exit(1)
