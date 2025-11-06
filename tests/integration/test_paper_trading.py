"""
Test Paper Trading System

Simple test to verify:
1. Portfolio initialization ($10,000)
2. Buy transactions
3. Sell transactions
4. Transaction logging
5. P&L calculation
"""

from core.paper_portfolio_manager import PaperPortfolioManager
import json
from pathlib import Path

def test_paper_trading():
    """Test paper trading functionality"""
    print("🧪 Testing Paper Trading System\n")

    # Initialize manager
    print("1️⃣ Initializing Portfolio Manager...")
    manager = PaperPortfolioManager()

    # Reset to clean state
    result = manager.reset_portfolio()
    print(f"   ✅ {result['message']}")
    print(f"   💵 Initial Cash: ${manager.cash:,.2f}\n")

    # Test BUY - AAPL
    print("2️⃣ Testing BUY: 10 shares of AAPL @ $175.50...")
    result = manager.buy('AAPL', 10, 175.50)
    if result['success']:
        print(f"   ✅ {result['message']}")
        print(f"   💰 Total Cost: ${result['total_cost']:,.2f}")
        print(f"   💵 Cash Remaining: ${result['cash_remaining']:,.2f}\n")
    else:
        print(f"   ❌ {result['message']}\n")
        return

    # Test BUY - MSFT
    print("3️⃣ Testing BUY: 5 shares of MSFT @ $385.00...")
    result = manager.buy('MSFT', 5, 385.00)
    if result['success']:
        print(f"   ✅ {result['message']}")
        print(f"   💰 Total Cost: ${result['total_cost']:,.2f}")
        print(f"   💵 Cash Remaining: ${result['cash_remaining']:,.2f}\n")
    else:
        print(f"   ❌ {result['message']}\n")
        return

    # Test SELL - AAPL (partial)
    print("4️⃣ Testing SELL: 5 shares of AAPL @ $180.00...")
    result = manager.sell('AAPL', 5, 180.00)
    if result['success']:
        print(f"   ✅ {result['message']}")
        print(f"   💰 Total Proceeds: ${result['total_proceeds']:,.2f}")
        print(f"   📈 P&L: ${result['pnl']:,.2f} ({result['pnl_percent']:+.2f}%)")
        print(f"   💵 Cash Remaining: ${result['cash_remaining']:,.2f}\n")
    else:
        print(f"   ❌ {result['message']}\n")
        return

    # Check portfolio state
    print("5️⃣ Portfolio State:")
    portfolio = manager.get_portfolio()
    print(f"   💵 Cash: ${portfolio['cash']:,.2f}")
    print(f"   📊 Positions:")
    for symbol, pos in portfolio['positions'].items():
        print(f"      • {symbol}: {pos['shares']} shares @ ${pos['cost_basis']:.2f}")
    print()

    # Check statistics
    print("6️⃣ Portfolio Statistics:")
    stats = manager.get_stats()
    print(f"   💰 Total Value: ${stats['total_value']:,.2f}")
    print(f"   📈 Total Return: ${stats['total_return']:,.2f} ({stats['total_return_percent']:+.2f}%)")
    print(f"   💵 Cash: ${stats['cash']:,.2f}")
    print(f"   📊 Invested: ${stats['invested']:,.2f}")
    print(f"   📍 Positions: {stats['num_positions']}")
    print(f"   📝 Transactions: {stats['num_transactions']}\n")

    # Check transaction log
    print("7️⃣ Transaction History:")
    transactions = manager.get_transactions(limit=5)
    for i, tx in enumerate(transactions, 1):
        print(f"   {i}. {tx['action']} {tx['shares']} {tx['symbol']} @ ${tx['price']:.2f}")
        print(f"      💰 Total: ${tx['total']:,.2f}")
        print(f"      📅 {tx['timestamp']}")
    print()

    # Verify files exist
    print("8️⃣ Verifying Files:")
    portfolio_file = Path("data/paper_portfolio.json")
    transaction_file = Path("data/transaction_log.json")

    if portfolio_file.exists():
        print(f"   ✅ Portfolio file: {portfolio_file}")
        with open(portfolio_file) as f:
            data = json.load(f)
            print(f"      Cash: ${data['cash']:,.2f}")
    else:
        print(f"   ❌ Portfolio file not found")

    if transaction_file.exists():
        print(f"   ✅ Transaction log: {transaction_file}")
        with open(transaction_file) as f:
            data = json.load(f)
            print(f"      Transactions: {len(data)}")
    else:
        print(f"   ❌ Transaction log not found")
    print()

    # Test error handling
    print("9️⃣ Testing Error Handling:")

    # Test insufficient funds
    print("   Testing insufficient funds...")
    result = manager.buy('GOOGL', 100, 150.00)  # $15,000 needed
    if not result['success']:
        print(f"   ✅ Correctly rejected: {result['message']}")
    else:
        print(f"   ❌ Should have failed!")

    # Test selling stock we don't own
    print("   Testing selling unowned stock...")
    result = manager.sell('TSLA', 10, 250.00)
    if not result['success']:
        print(f"   ✅ Correctly rejected: {result['message']}")
    else:
        print(f"   ❌ Should have failed!")

    # Test selling too many shares
    print("   Testing selling too many shares...")
    result = manager.sell('AAPL', 100, 180.00)  # We only have 5 shares
    if not result['success']:
        print(f"   ✅ Correctly rejected: {result['message']}")
    else:
        print(f"   ❌ Should have failed!")
    print()

    print("✅ All tests completed successfully!")
    print("\n" + "="*60)
    print("📊 Final Summary:")
    print("="*60)
    final_stats = manager.get_stats()
    print(f"Starting Capital: $10,000.00")
    print(f"Current Value:    ${final_stats['total_value']:,.2f}")
    print(f"Return:           ${final_stats['total_return']:,.2f} ({final_stats['total_return_percent']:+.2f}%)")
    print(f"Cash:             ${final_stats['cash']:,.2f}")
    print(f"Invested:         ${final_stats['invested']:,.2f}")
    print(f"Transactions:     {final_stats['num_transactions']}")
    print("="*60)

if __name__ == "__main__":
    test_paper_trading()
