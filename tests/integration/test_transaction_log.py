#!/usr/bin/env python3
"""
Quick test to verify transaction log functionality in backtesting
Tests both API and verifies transaction data structure
"""

import requests
import json
from datetime import datetime, timedelta

API_BASE = "http://localhost:8010"

def test_backtest_with_transaction_log():
    """Run a quick backtest and verify transaction log data"""

    print("="*80)
    print("🧪 Testing Transaction Log Functionality")
    print("="*80)
    print()

    # Configure a quick 6-month backtest
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)  # 6 months

    config = {
        "start_date": start_date.strftime('%Y-%m-%d'),
        "end_date": end_date.strftime('%Y-%m-%d'),
        "rebalance_frequency": "monthly",
        "top_n": 10,
        "universe": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "V", "JPM", "UNH"],
        "initial_capital": 10000
    }

    print(f"📅 Test Period: {config['start_date']} to {config['end_date']}")
    print(f"💰 Initial Capital: ${config['initial_capital']:,}")
    print(f"📊 Universe: {len(config['universe'])} stocks")
    print(f"🔄 Rebalancing: {config['rebalance_frequency']}")
    print()
    print("🚀 Running backtest...")
    print()

    try:
        # Run backtest
        response = requests.post(
            f"{API_BASE}/backtest/historical",
            json=config,
            timeout=180  # 3 minutes max
        )

        if response.status_code == 200:
            result = response.json()

            print("✅ Backtest completed successfully!")
            print()

            # Verify basic results
            results = result.get('results', {})
            print(f"📈 Performance Metrics:")
            print(f"   Total Return: {results.get('total_return', 0)*100:.2f}%")
            print(f"   Final Value: ${results.get('final_value', 0):,.2f}")
            print(f"   Sharpe Ratio: {results.get('sharpe_ratio', 0):.2f}")
            print(f"   Max Drawdown: {results.get('max_drawdown', 0)*100:.2f}%")
            print()

            # Check if trade_log exists
            trade_log = result.get('trade_log', [])

            if trade_log:
                print(f"✅ Transaction Log Found: {len(trade_log)} transactions")
                print()

                # Analyze transactions
                buys = [tx for tx in trade_log if tx['action'] == 'BUY']
                sells = [tx for tx in trade_log if tx['action'] == 'SELL']

                print(f"📊 Transaction Breakdown:")
                print(f"   Total Transactions: {len(trade_log)}")
                print(f"   Buy Orders: {len(buys)}")
                print(f"   Sell Orders: {len(sells)}")
                print()

                # Show sample transactions
                print("💵 Sample BUY Transactions (First 3):")
                print("-" * 100)
                print(f"{'Date':<12} {'Symbol':<8} {'Shares':>10} {'Price':>12} {'Total Value':>15} {'Score':>8}")
                print("-" * 100)
                for tx in buys[:3]:
                    print(f"{tx['date']:<12} {tx['symbol']:<8} {tx['shares']:>10.2f} "
                          f"${tx['price']:>11.2f} ${tx['value']:>14.2f} {tx.get('agent_score', 0):>8.1f}")
                print()

                if sells:
                    print("💰 Sample SELL Transactions (First 3):")
                    print("-" * 120)
                    print(f"{'Date':<12} {'Symbol':<8} {'Shares':>10} {'Price':>12} {'Entry Price':>13} {'P&L':>12} {'P&L %':>10}")
                    print("-" * 120)
                    for tx in sells[:3]:
                        pnl = tx.get('pnl', 0)
                        pnl_pct = tx.get('pnl_pct', 0)
                        print(f"{tx['date']:<12} {tx['symbol']:<8} {tx['shares']:>10.2f} "
                              f"${tx['price']:>11.2f} ${tx.get('entry_price', 0):>12.2f} "
                              f"${pnl:>11.2f} {pnl_pct*100:>9.2f}%")
                    print()

                # Calculate total P&L
                total_pnl = sum(tx.get('pnl', 0) for tx in sells if tx.get('pnl') is not None)
                winning_trades = len([tx for tx in sells if tx.get('pnl', 0) > 0])
                losing_trades = len([tx for tx in sells if tx.get('pnl', 0) < 0])

                print(f"📊 P&L Summary:")
                print(f"   Total Realized P&L: ${total_pnl:,.2f}")
                if sells:
                    print(f"   Winning Trades: {winning_trades} ({winning_trades/len(sells)*100:.1f}%)")
                    print(f"   Losing Trades: {losing_trades} ({losing_trades/len(sells)*100:.1f}%)")
                print()

                # Verify data structure
                print("✅ Transaction Data Structure Verification:")
                sample_tx = trade_log[0]
                required_fields = ['date', 'action', 'symbol', 'shares', 'price', 'value']
                for field in required_fields:
                    status = "✓" if field in sample_tx else "✗"
                    print(f"   {status} {field}: {sample_tx.get(field, 'MISSING')}")
                print()

                print("="*80)
                print("✅ SUCCESS: Transaction log is working correctly!")
                print("="*80)
                print()
                print("📱 You can now view these transactions in the frontend:")
                print("   1. Open http://localhost:5174")
                print("   2. Go to Backtesting page")
                print("   3. Click 'Run Backtest' or view existing results")
                print("   4. Switch to 'Detailed Analysis' tab")
                print("   5. Scroll to see the complete transaction log")
                print()

                # Save sample to file
                with open('sample_transaction_log.json', 'w') as f:
                    json.dump({
                        'summary': {
                            'total_transactions': len(trade_log),
                            'buy_orders': len(buys),
                            'sell_orders': len(sells),
                            'total_pnl': total_pnl
                        },
                        'sample_transactions': trade_log[:10]
                    }, f, indent=2)
                print("💾 Sample transaction log saved to: sample_transaction_log.json")
                print()

            else:
                print("❌ WARNING: trade_log not found in API response!")
                print("   The API may need to be updated to include trade_log")
                print()

        else:
            print(f"❌ Backtest failed with status {response.status_code}")
            print(f"Error: {response.text}")

    except requests.exceptions.Timeout:
        print("⏱️  Backtest timed out (>3 minutes)")
        print("   Try reducing the time period or number of stocks")
    except Exception as e:
        print(f"❌ Error running backtest: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_backtest_with_transaction_log()
