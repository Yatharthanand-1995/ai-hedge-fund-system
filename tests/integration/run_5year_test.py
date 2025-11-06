#!/usr/bin/env python3
"""
Run a 5-year backtest and save results for the frontend
"""

import requests
import json
from datetime import datetime, timedelta

API_BASE = "http://localhost:8010"

def run_5year_backtest():
    """Run full 5-year backtest"""

    print("="*80)
    print("🚀 Running 5-Year Backtest")
    print("="*80)
    print()

    # 5-year backtest config (matches frontend config)
    end_date = datetime.now()
    start_date = end_date.replace(year=end_date.year - 5)

    config = {
        "start_date": start_date.strftime('%Y-%m-%d'),
        "end_date": end_date.strftime('%Y-%m-%d'),
        "rebalance_frequency": "quarterly",
        "top_n": 20,
        "universe": ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'V', 'JPM', 'UNH',
                     'JNJ', 'WMT', 'PG', 'HD', 'MA', 'LLY', 'ABBV', 'KO', 'CVX', 'AVGO'],
        "initial_capital": 10000
    }

    print(f"📅 Test Period: {config['start_date']} to {config['end_date']}")
    print(f"💰 Initial Capital: ${config['initial_capital']:,}")
    print(f"📊 Universe: {len(config['universe'])} stocks")
    print(f"🔄 Rebalancing: {config['rebalance_frequency']}")
    print(f"🎯 Top N: {config['top_n']} stocks")
    print()
    print("⏳ Running backtest (this may take 5-10 minutes)...")
    print()

    try:
        # Run backtest
        response = requests.post(
            f"{API_BASE}/backtest/historical",
            json=config,
            timeout=600  # 10 minutes max
        )

        if response.status_code == 200:
            result = response.json()

            print("✅ Backtest completed successfully!")
            print()

            # Display results
            results = result.get('results', {})
            print("="*80)
            print("📈 PERFORMANCE METRICS")
            print("="*80)
            print(f"   Total Return:       {results.get('total_return', 0)*100:>10.2f}%")
            print(f"   CAGR:              {results.get('cagr', 0)*100:>10.2f}%")
            print(f"   Final Value:        ${results.get('final_value', 0):>10,.2f}")
            print(f"   Sharpe Ratio:      {results.get('sharpe_ratio', 0):>10.2f}")
            print(f"   Sortino Ratio:     {results.get('sortino_ratio', 0):>10.2f}")
            print(f"   Max Drawdown:      {results.get('max_drawdown', 0)*100:>10.2f}%")
            print(f"   Volatility:        {results.get('volatility', 0)*100:>10.2f}%")
            print()
            print("📊 BENCHMARK COMPARISON")
            print("="*80)
            spy_return = results.get('spy_return', {})
            if isinstance(spy_return, dict):
                spy_ret = list(spy_return.values())[0] if spy_return else 0
            else:
                spy_ret = spy_return

            outperf = results.get('outperformance_vs_spy', {})
            if isinstance(outperf, dict):
                outperf_val = list(outperf.values())[0] if outperf else 0
            else:
                outperf_val = outperf

            print(f"   SPY Return:        {spy_ret*100:>10.2f}%")
            print(f"   Outperformance:    {outperf_val*100:>+10.2f}%")
            print(f"   Alpha:             {results.get('alpha', 0):>10.2f}")
            print(f"   Beta:              {results.get('beta', 0):>10.2f}")
            print()

            # Transaction log
            trade_log = result.get('trade_log', [])
            if trade_log:
                buys = [tx for tx in trade_log if tx['action'] == 'BUY']
                sells = [tx for tx in trade_log if tx['action'] == 'SELL']

                print("📋 TRANSACTION LOG")
                print("="*80)
                print(f"   Total Transactions: {len(trade_log)}")
                print(f"   Buy Orders:         {len(buys)}")
                print(f"   Sell Orders:        {len(sells)}")

                if sells:
                    total_pnl = sum(tx.get('pnl', 0) for tx in sells if tx.get('pnl') is not None)
                    winning = len([tx for tx in sells if tx.get('pnl', 0) > 0])
                    losing = len([tx for tx in sells if tx.get('pnl', 0) < 0])

                    print(f"   Total P&L:          ${total_pnl:,.2f}")
                    print(f"   Winning Trades:     {winning} ({winning/len(sells)*100:.1f}%)")
                    print(f"   Losing Trades:      {losing} ({losing/len(sells)*100:.1f}%)")
                print()

            # Save result
            with open('backtest_5year_result.json', 'w') as f:
                json.dump(result, f, indent=2)

            print("="*80)
            print("✅ SUCCESS!")
            print("="*80)
            print()
            print("💾 Results saved to: backtest_5year_result.json")
            print()
            print("🌐 You can now view these results in the frontend:")
            print("   1. The backend should automatically serve these results")
            print("   2. Refresh your browser at http://localhost:5174")
            print("   3. Go to Backtesting page")
            print("   4. Results should now be visible!")
            print()

            return True

        else:
            print(f"❌ Backtest failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("⏱️  Backtest timed out (>10 minutes)")
        print("   Try reducing the time period or number of stocks")
        return False
    except Exception as e:
        print(f"❌ Error running backtest: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    success = run_5year_backtest()
    sys.exit(0 if success else 1)
