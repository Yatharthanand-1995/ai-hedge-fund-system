"""
Run Fast Comprehensive Backtests - Multiple Short Periods
This creates comprehensive backtest history without long-running requests
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Top 10 most liquid stocks for faster backtesting
FAST_UNIVERSE = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA',
    'META', 'TSLA', 'V', 'JPM', 'UNH'
]

def run_backtest(start_date, end_date, name, top_n=8, initial_capital=100000):
    """Run backtest via API with proper timeout"""

    config = {
        "start_date": start_date,
        "end_date": end_date,
        "rebalance_frequency": "monthly",
        "top_n": top_n,
        "universe": FAST_UNIVERSE,
        "initial_capital": initial_capital
    }

    print(f"\n{'='*70}")
    print(f"🚀 {name}")
    print(f"{'='*70}")
    print(f"   Period: {start_date} to {end_date}")
    print(f"   Universe: {len(FAST_UNIVERSE)} stocks")
    print(f"   Top N: {top_n}")
    print(f"   Running...")

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

            print(f"\n✅ COMPLETED!")
            print(f"   Return:     {total_return:>7.2f}%")
            print(f"   CAGR:       {cagr:>7.2f}%")
            print(f"   Sharpe:     {sharpe:>7.2f}")
            print(f"   Max DD:     {max_dd:>7.2f}%")
            print(f"   Saved ID:   {result.get('backtest_id', 'N/A')[:8]}...")

            return result
        else:
            print(f"\n❌ FAILED: HTTP {response.status_code}")
            return None

    except requests.exceptions.Timeout:
        print(f"\n⏱️ TIMEOUT after 5 minutes")
        return None
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return None

def check_history():
    """Check backtest history"""
    try:
        response = requests.get('http://localhost:8010/backtest/history?limit=20', timeout=30)
        if response.status_code == 200:
            history = response.json()
            print(f"\n📚 Total Stored Backtests: {len(history)}")
            return history
        return []
    except:
        return []

def main():
    """Run multiple short-period backtests"""
    print("\n" + "="*70)
    print("🏦 AI HEDGE FUND - FAST BACKTEST RUNNER")
    print("="*70)
    print("\nStrategy: Run multiple shorter backtests for comprehensive history")
    print("This is faster and more reliable than one long 5-year backtest.\n")

    # Current date
    end_date = datetime.now()

    # Define multiple backtest periods
    periods = [
        {
            "name": "Last 6 Months",
            "months": 6,
            "top_n": 8,
            "capital": 100000
        },
        {
            "name": "Last 9 Months",
            "months": 9,
            "top_n": 8,
            "capital": 100000
        },
        {
            "name": "Last 12 Months (1 Year)",
            "months": 12,
            "top_n": 8,
            "capital": 100000
        },
        {
            "name": "Last 18 Months",
            "months": 18,
            "top_n": 8,
            "capital": 100000
        },
        {
            "name": "Last 24 Months (2 Years)",
            "months": 24,
            "top_n": 8,
            "capital": 100000
        }
    ]

    results = []

    for i, period in enumerate(periods, 1):
        start_date = (end_date - timedelta(days=period['months'] * 30)).strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')

        result = run_backtest(
            start_date=start_date,
            end_date=end_str,
            name=f"{period['name']} ({i}/{len(periods)})",
            top_n=period['top_n'],
            initial_capital=period['capital']
        )

        if result:
            results.append(result)

        # Brief pause between backtests
        if i < len(periods):
            print("\n⏸️  Waiting 3 seconds...")
            time.sleep(3)

    # Final summary
    print(f"\n{'='*70}")
    print("📊 FINAL SUMMARY")
    print(f"{'='*70}")
    print(f"\n✅ Completed: {len(results)}/{len(periods)} backtests")

    history = check_history()

    if history:
        print(f"\n📚 Recent Backtest History:")
        for i, bt in enumerate(history[:10], 1):
            ret = bt.get('total_return', 0) * 100
            period = f"{bt['start_date']} to {bt['end_date']}"
            print(f"   {i:2d}. {period:30s} {ret:>7.2f}%")

    print(f"\n{'='*70}")
    print("🎉 COMPLETE!")
    print(f"{'='*70}")
    print("\n✨ Frontend should now show backtest results!")
    print("   URL: http://localhost:5173")
    print("   Tab: Backtesting\n")

if __name__ == "__main__":
    main()
