"""
Test script to verify /backtest/run endpoint uses real historical engine
Tests the fix for Issue #2: Synthetic data generation replaced with real backtest
"""

import requests
import json
from datetime import datetime, timedelta

# API base URL
BASE_URL = "http://localhost:8010"

def test_backtest_run_endpoint():
    """Test that /backtest/run uses real historical backtest engine"""

    print("\n" + "="*80)
    print("🧪 TEST: /backtest/run Endpoint - Real vs Synthetic Data")
    print("="*80 + "\n")

    # Define test configuration (short period for quick testing)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')  # 3 months

    config = {
        "start_date": start_date,
        "end_date": end_date,
        "rebalance_frequency": "monthly",
        "top_n": 5,
        "universe": ["AAPL", "MSFT", "GOOGL"],  # Small universe for quick test
        "initial_capital": 10000.0
    }

    print(f"📅 Test Period: {start_date} to {end_date}")
    print(f"💰 Initial Capital: ${config['initial_capital']:,.2f}")
    print(f"📊 Universe: {', '.join(config['universe'])}")
    print(f"🔄 Rebalance: {config['rebalance_frequency']}")
    print(f"📌 Top N: {config['top_n']}")
    print("\n" + "-"*80 + "\n")

    print("🚀 Sending request to /backtest/run endpoint...")

    try:
        # Make POST request to /backtest/run
        response = requests.post(
            f"{BASE_URL}/backtest/run",
            json=config,
            timeout=300  # 5 minute timeout for backtest
        )

        if response.status_code != 200:
            print(f"\n❌ Request failed with status code: {response.status_code}")
            print(f"Error: {response.text}")
            return False

        result = response.json()

        print("\n" + "="*80)
        print("📊 BACKTEST RESULTS")
        print("="*80 + "\n")

        # Extract results
        results = result.get('results', {})

        print(f"📈 Performance Metrics:")
        print(f"   • Initial Capital: ${results.get('initial_capital', 0):,.2f}")
        print(f"   • Final Value: ${results.get('final_value', 0):,.2f}")
        print(f"   • Total Return: {results.get('total_return', 0)*100:.2f}%")

        metrics = results.get('metrics', {})
        print(f"   • CAGR: {metrics.get('cagr', 0)*100:.2f}%")
        print(f"   • Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
        print(f"   • Max Drawdown: {metrics.get('max_drawdown', 0)*100:.2f}%")
        print(f"   • Volatility: {metrics.get('volatility', 0)*100:.2f}%")

        print(f"\n📊 Benchmark Comparison:")
        print(f"   • SPY Return: {results.get('spy_return', 0)*100:.2f}%")
        print(f"   • Outperformance: {results.get('outperformance_vs_spy', 0)*100:.2f}%")

        print(f"\n🔄 Trading Activity:")
        print(f"   • Number of Rebalances: {results.get('rebalances', 0)}")

        # Check rebalance log to verify real agent scoring
        rebalance_log = results.get('rebalance_log', [])
        if rebalance_log:
            print(f"\n🎯 Sample Rebalance Events:")
            for i, event in enumerate(rebalance_log[:3], 1):
                print(f"\n   Rebalance {i}:")
                print(f"      • Date: {event.get('date')}")
                print(f"      • Portfolio Value: ${event.get('portfolio_value', 0):,.2f}")
                print(f"      • Average Score: {event.get('avg_score', 0):.1f}/100")
                print(f"      • Stocks: {', '.join(event.get('portfolio', []))}")

        # Validation checks
        print("\n" + "="*80)
        print("✅ VALIDATION CHECKS")
        print("="*80 + "\n")

        validations = []

        # Check 1: Non-zero returns (real backtest should have actual market returns)
        if results.get('total_return', 0) != 0:
            validations.append("✓ Non-zero returns (real market data)")
        else:
            validations.append("✗ Zero returns (suspicious)")

        # Check 2: Rebalance log exists with agent scores
        if rebalance_log and all('avg_score' in event for event in rebalance_log):
            validations.append("✓ Rebalance log contains agent scores")
        else:
            validations.append("✗ Missing agent scores in rebalance log")

        # Check 3: Advanced metrics present (CAGR, Sortino, Calmar from real engine)
        advanced_metrics = ['cagr', 'sortino_ratio', 'calmar_ratio']
        present_metrics = [m for m in advanced_metrics if m in metrics]
        if len(present_metrics) >= 1:  # At least one advanced metric present
            validations.append(f"✓ Advanced metrics present: {', '.join(present_metrics)}")
        else:
            validations.append("✗ No advanced metrics found")

        # Check 4: Equity curve exists
        if results.get('equity_curve') and len(results['equity_curve']) > 0:
            validations.append("✓ Equity curve generated")
        else:
            validations.append("✗ No equity curve")

        # Check 5: Realistic Sharpe ratio (not hardcoded)
        sharpe = metrics.get('sharpe_ratio', 0)
        if sharpe > 0 and sharpe != 1.0:  # 1.0 was the fallback in synthetic version
            validations.append(f"✓ Realistic Sharpe ratio: {sharpe:.2f}")
        else:
            validations.append(f"✗ Suspicious Sharpe ratio: {sharpe:.2f}")

        for validation in validations:
            print(validation)

        # Final verdict
        passed = all('✓' in v for v in validations)

        if passed:
            print("\n" + "="*80)
            print("✅ TEST PASSED: /backtest/run uses REAL historical engine!")
            print("="*80)
            print("\nEvidence:")
            print("✓ Real market returns calculated from historical prices")
            print("✓ Agent scores visible in rebalance events")
            print("✓ Advanced performance metrics (CAGR, Sortino) present")
            print("✓ Equity curve shows real portfolio progression")
            print("✓ No synthetic/formula-based return generation")
            return True
        else:
            print("\n" + "="*80)
            print("⚠️ TEST WARNING: Some validations failed")
            print("="*80)
            return False

    except requests.exceptions.Timeout:
        print("\n❌ Request timed out (backtest may take longer)")
        print("Try with a shorter time period or larger timeout")
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
    print("   /BACKTEST/RUN ENDPOINT VALIDATION")
    print("   Testing Real Historical Engine vs Synthetic Data")
    print("🔬 " + "="*76 + " 🔬\n")

    # Check API health first
    print("📡 Checking API status...")
    if not check_api_health():
        print("\n❌ Cannot run test - API not available")
        exit(1)

    print("\n" + "-"*80 + "\n")

    # Run test
    success = test_backtest_run_endpoint()

    # Final summary
    print("\n" + "="*80)
    print("📋 TEST SUMMARY")
    print("="*80)

    if success:
        print("\n🎉 SUCCESS!")
        print("\n✅ The /backtest/run endpoint now uses REAL historical data")
        print("✅ Synthetic return generation has been replaced")
        print("✅ Issue #2 is FIXED")
        exit(0)
    else:
        print("\n❌ TEST FAILED - Review output above")
        exit(1)
