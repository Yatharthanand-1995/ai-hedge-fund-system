"""
Run Comprehensive 5-Year Backtest with Real 4-Agent Analysis
This script runs a full backtest with real historical data and stores results
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Top 20 stocks from the elite universe - diversified across sectors
TOP_20_STOCKS = [
    # Mega Cap Tech (8 stocks)
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AVGO',
    # Healthcare (4 stocks)
    'UNH', 'JNJ', 'LLY', 'ABBV',
    # Financial (4 stocks)
    'V', 'JPM', 'MA', 'BAC',
    # Consumer (2 stocks)
    'WMT', 'HD',
    # Energy (2 stocks)
    'CVX', 'XOM'
]

def run_backtest(start_date, end_date, top_n=10, initial_capital=100000):
    """Run backtest via API"""

    config = {
        "start_date": start_date,
        "end_date": end_date,
        "rebalance_frequency": "monthly",
        "top_n": top_n,
        "universe": TOP_20_STOCKS,
        "initial_capital": initial_capital
    }

    print(f"\n🚀 Running backtest: {start_date} to {end_date}")
    print(f"   Universe: {len(TOP_20_STOCKS)} stocks")
    print(f"   Top N: {top_n}")
    print(f"   Initial Capital: ${initial_capital:,}")
    print(f"   Rebalance: Monthly")
    print("\n   This may take 2-5 minutes for 5 years of data...\n")

    try:
        response = requests.post(
            'http://localhost:8010/backtest/run',
            json=config,
            timeout=600  # 10 minute timeout for long backtest
        )

        if response.status_code == 200:
            result = response.json()

            # Extract key metrics
            results = result.get('results', {})
            total_return = results.get('total_return', 0) * 100
            cagr = results.get('metrics', {}).get('cagr', 0) * 100
            sharpe = results.get('metrics', {}).get('sharpe_ratio', 0)
            max_dd = results.get('metrics', {}).get('max_drawdown', 0) * 100
            spy_return = results.get('spy_return', 0) * 100
            outperformance = results.get('outperformance_vs_spy', 0) * 100

            print("✅ BACKTEST COMPLETED SUCCESSFULLY!\n")
            print(f"📊 Performance Metrics:")
            print(f"   Total Return:     {total_return:>8.2f}%")
            print(f"   CAGR:            {cagr:>8.2f}%")
            print(f"   Sharpe Ratio:    {sharpe:>8.2f}")
            print(f"   Max Drawdown:    {max_dd:>8.2f}%")
            print(f"   SPY Return:      {spy_return:>8.2f}%")
            print(f"   Outperformance:  {outperformance:>8.2f}%")
            print(f"\n💾 Backtest ID: {result.get('backtest_id', 'N/A')}")

            return result
        else:
            print(f"❌ Backtest failed: HTTP {response.status_code}")
            print(f"   Error: {response.text[:500]}")
            return None

    except requests.exceptions.Timeout:
        print("⏱️ Backtest timed out (>10 minutes)")
        print("   This can happen with very long backtests.")
        print("   Try a shorter time period or fewer stocks.")
        return None
    except Exception as e:
        print(f"❌ Backtest failed with error: {e}")
        return None

def check_backtest_history():
    """Check stored backtest history"""
    try:
        response = requests.get('http://localhost:8010/backtest/history', timeout=10)
        if response.status_code == 200:
            history = response.json()
            print(f"\n📚 Backtest History: {len(history)} results stored")

            for i, backtest in enumerate(history[:5], 1):
                total_return = backtest.get('total_return', 0) * 100
                print(f"   {i}. {backtest['start_date']} to {backtest['end_date']}: "
                      f"{total_return:.2f}% return")

            return history
        else:
            print(f"⚠️ Could not fetch history: HTTP {response.status_code}")
            return []
    except Exception as e:
        print(f"⚠️ Failed to fetch history: {e}")
        return []

def main():
    """Run comprehensive backtests"""
    print("="*70)
    print("🏦 AI HEDGE FUND - COMPREHENSIVE BACKTEST RUNNER")
    print("="*70)

    # Calculate date ranges
    end_date = datetime.now().strftime('%Y-%m-%d')

    # Run multiple backtests with different time periods
    backtests_to_run = [
        {
            "name": "5-Year Full Period",
            "start": (datetime.now() - timedelta(days=365*5)).strftime('%Y-%m-%d'),
            "end": end_date,
            "top_n": 10,
            "capital": 100000
        },
        {
            "name": "3-Year Recent",
            "start": (datetime.now() - timedelta(days=365*3)).strftime('%Y-%m-%d'),
            "end": end_date,
            "top_n": 10,
            "capital": 100000
        },
        {
            "name": "1-Year Last Year",
            "start": (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'),
            "end": end_date,
            "top_n": 10,
            "capital": 100000
        }
    ]

    results = []

    for i, config in enumerate(backtests_to_run, 1):
        print(f"\n{'='*70}")
        print(f"BACKTEST {i}/{len(backtests_to_run)}: {config['name']}")
        print(f"{'='*70}")

        result = run_backtest(
            start_date=config['start'],
            end_date=config['end'],
            top_n=config['top_n'],
            initial_capital=config['capital']
        )

        if result:
            results.append(result)
            print(f"\n✅ Backtest {i} completed and saved!")
        else:
            print(f"\n❌ Backtest {i} failed!")

        # Wait a bit between backtests to avoid overwhelming the system
        if i < len(backtests_to_run):
            print("\n⏸️  Waiting 5 seconds before next backtest...")
            time.sleep(5)

    # Check final history
    print(f"\n{'='*70}")
    print("📊 FINAL RESULTS")
    print(f"{'='*70}")
    print(f"\n✅ Completed {len(results)}/{len(backtests_to_run)} backtests")

    check_backtest_history()

    print(f"\n{'='*70}")
    print("🎉 ALL BACKTESTS COMPLETE!")
    print(f"{'='*70}")
    print("\n✨ You can now view results in the frontend at http://localhost:5173")
    print("   Navigate to the Backtesting tab to see detailed results.\n")

if __name__ == "__main__":
    main()
