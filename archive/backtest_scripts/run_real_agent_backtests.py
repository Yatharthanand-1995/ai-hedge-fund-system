"""
Run Real 4-Agent Backtests - Multiple Periods
This creates comprehensive backtest history with REAL 4-agent analysis (not simplified proxy)
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Top 10 most liquid stocks for reliable backtesting
BACKTEST_UNIVERSE = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA',
    'META', 'TSLA', 'V', 'JPM', 'UNH'
]

def run_backtest(start_date, end_date, name, top_n=8, initial_capital=100000):
    """Run backtest via API with real 4-agent analysis"""

    config = {
        "start_date": start_date,
        "end_date": end_date,
        "rebalance_frequency": "monthly",
        "top_n": top_n,
        "universe": BACKTEST_UNIVERSE,
        "initial_capital": initial_capital
    }

    print(f"\n{'='*70}")
    print(f"🚀 {name}")
    print(f"{'='*70}")
    print(f"   Period: {start_date} to {end_date}")
    print(f"   Universe: {len(BACKTEST_UNIVERSE)} stocks")
    print(f"   Top N: {top_n}")
    print(f"   Running with REAL 4-agent analysis...")
    print(f"   Expected: 2-5 minutes\n")

    try:
        response = requests.post(
            'http://localhost:8010/backtest/run',
            json=config,
            timeout=600  # 10 minute timeout for safety
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

            # Verify real agent analysis by checking rebalance log
            rebalances = results.get('rebalance_log', [])
            if rebalances and len(rebalances) > 0:
                first_rebalance = rebalances[0]
                if 'scores' in first_rebalance and first_rebalance['scores']:
                    print(f"   ✅ Real agent scores VERIFIED!")
                else:
                    print(f"   ⚠️  Agent scores not found in rebalance log")

            return result
        else:
            print(f"\n❌ FAILED: HTTP {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            return None

    except requests.exceptions.Timeout:
        print(f"\n⏱️ TIMEOUT after 10 minutes")
        print(f"   Try a shorter period or fewer stocks")
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
    """Run multiple period backtests with real 4-agent analysis"""
    print("\n" + "="*70)
    print("🏦 AI HEDGE FUND - REAL 4-AGENT BACKTEST RUNNER")
    print("="*70)
    print("\nUsing REAL 4-agent analysis:")
    print("  - FundamentalsAgent (5% weight in backtest mode)")
    print("  - MomentumAgent (50% weight - real historical data)")
    print("  - QualityAgent (40% weight - real historical data)")
    print("  - SentimentAgent (5% weight)\n")

    # Current date
    end_date = datetime.now()

    # Define multiple backtest periods (shorter to avoid timeout)
    periods = [
        {
            "name": "Last 2 Years (2023-2025)",
            "start": (end_date - timedelta(days=730)).strftime('%Y-%m-%d'),
            "end": end_date.strftime('%Y-%m-%d'),
            "top_n": 8,
            "capital": 100000
        },
        {
            "name": "2021-2022 Period",
            "start": "2021-01-01",
            "end": "2022-12-31",
            "top_n": 8,
            "capital": 100000
        },
        {
            "name": "2020-2021 Period",
            "start": "2020-01-01",
            "end": "2020-12-31",
            "top_n": 8,
            "capital": 100000
        }
    ]

    results = []

    for i, period in enumerate(periods, 1):
        result = run_backtest(
            start_date=period['start'],
            end_date=period['end'],
            name=f"{period['name']} ({i}/{len(periods)})",
            top_n=period['top_n'],
            initial_capital=period['capital']
        )

        if result:
            results.append(result)

        # Brief pause between backtests
        if i < len(periods):
            print(f"\n⏸️  Waiting 3 seconds...")
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
    print("\n✨ Frontend should now show backtest results with REAL 4-agent analysis!")
    print("   URL: http://localhost:5173")
    print("   Tab: Backtesting\n")

if __name__ == "__main__":
    main()
