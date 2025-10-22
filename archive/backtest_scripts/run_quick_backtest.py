"""
Run Ultra-Fast 3-Month Backtest
This creates one quick backtest result for immediate frontend display
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Ultra-fast: Only 5 most liquid stocks
ULTRA_FAST_UNIVERSE = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']

def run_quick_backtest():
    """Run single 3-month backtest"""

    # Last 3 months
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

    config = {
        "start_date": start_date,
        "end_date": end_date,
        "rebalance_frequency": "monthly",
        "top_n": 3,
        "universe": ULTRA_FAST_UNIVERSE,
        "initial_capital": 100000
    }

    print(f"\n{'='*70}")
    print(f"🏦 AI HEDGE FUND - ULTRA-FAST BACKTEST")
    print(f"{'='*70}")
    print(f"\n🚀 Running 3-month backtest")
    print(f"   Period: {start_date} to {end_date}")
    print(f"   Universe: {len(ULTRA_FAST_UNIVERSE)} stocks (FAANG)")
    print(f"   Top N: 3")
    print(f"   Initial Capital: $100,000")
    print(f"\n   This should complete in ~2 minutes...\n")

    try:
        response = requests.post(
            'http://localhost:8010/backtest/run',
            json=config,
            timeout=300  # 5 minute timeout
        )

        if response.status_code == 200:
            result = response.json()
            results = result.get('results', {})

            total_return = results.get('total_return', 0) * 100
            cagr = results.get('metrics', {}).get('cagr', 0) * 100
            sharpe = results.get('metrics', {}).get('sharpe_ratio', 0)
            max_dd = results.get('metrics', {}).get('max_drawdown', 0) * 100

            print(f"✅ COMPLETED SUCCESSFULLY!\n")
            print(f"📊 Performance Metrics:")
            print(f"   Total Return:     {total_return:>8.2f}%")
            print(f"   CAGR:            {cagr:>8.2f}%")
            print(f"   Sharpe Ratio:    {sharpe:>8.2f}")
            print(f"   Max Drawdown:    {max_dd:>8.2f}%")
            print(f"\n💾 Backtest ID: {result.get('backtest_id', 'N/A')}")

            # Check history
            print(f"\n{'='*70}")
            print("📚 Checking Backtest History...")
            print(f"{'='*70}\n")

            history_response = requests.get('http://localhost:8010/backtest/history?limit=10', timeout=30)
            if history_response.status_code == 200:
                history = history_response.json()
                print(f"✅ Total Stored Backtests: {len(history)}\n")

                for i, bt in enumerate(history[:5], 1):
                    ret = bt.get('total_return', 0) * 100
                    period = f"{bt['start_date']} to {bt['end_date']}"
                    print(f"   {i}. {period:35s} {ret:>7.2f}%")

            print(f"\n{'='*70}")
            print("🎉 COMPLETE!")
            print(f"{'='*70}")
            print("\n✨ Frontend should now show backtest results!")
            print("   URL: http://localhost:5173")
            print("   Tab: Backtesting\n")

            return result
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"   Error: {response.text[:500]}")
            return None

    except requests.exceptions.Timeout:
        print(f"⏱️ TIMEOUT after 5 minutes")
        return None
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None

if __name__ == "__main__":
    run_quick_backtest()
