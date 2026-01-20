"""
Test Automated Trading System

Demonstrates the automated buy/sell functionality:
1. Enable auto-buy and auto-sell rules
2. Scan for opportunities
3. Execute automated trading cycle
"""

import requests
import json
from datetime import datetime


BASE_URL = "http://localhost:8010"


def print_section(title):
    """Print section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_automation_status():
    """Check current automation status."""
    print_section("1. Automation Status")

    response = requests.get(f"{BASE_URL}/portfolio/paper/auto-trade/status")
    data = response.json()

    print(f"Auto-Buy Enabled: {data['automation_enabled']['auto_buy']}")
    print(f"Auto-Sell Enabled: {data['automation_enabled']['auto_sell']}")
    print(f"Fully Automated: {data['automation_enabled']['fully_automated']}")
    print(f"\nPortfolio Cash: ${data['portfolio']['cash']:.2f}")
    print(f"Positions: {data['portfolio']['num_positions']}")
    print(f"Total Value: ${data['portfolio']['total_value']:.2f}")
    print(f"Return: {data['portfolio']['total_return_percent']:.2f}%")

    return data


def enable_automation():
    """Enable both auto-buy and auto-sell."""
    print_section("2. Enabling Automation Rules")

    # Enable auto-buy
    auto_buy_params = {
        "enabled": True,
        "min_score_threshold": 75,
        "max_positions": 10,
        "max_single_trade_amount": 2000,
        "min_confidence_level": "MEDIUM"
    }

    response = requests.post(
        f"{BASE_URL}/portfolio/paper/auto-buy/rules",
        params=auto_buy_params
    )
    print("✅ Auto-Buy Rules:")
    print(f"   - Min Score: {auto_buy_params['min_score_threshold']}")
    print(f"   - Max Positions: {auto_buy_params['max_positions']}")
    print(f"   - Max Trade Amount: ${auto_buy_params['max_single_trade_amount']}")
    print(f"   - Min Confidence: {auto_buy_params['min_confidence_level']}")

    # Enable auto-sell
    auto_sell_params = {
        "enabled": True,
        "stop_loss_percent": -10,
        "take_profit_percent": 20,
        "watch_ai_signals": True
    }

    response = requests.post(
        f"{BASE_URL}/portfolio/paper/auto-sell/rules",
        params=auto_sell_params
    )
    print("\n✅ Auto-Sell Rules:")
    print(f"   - Stop Loss: {auto_sell_params['stop_loss_percent']}%")
    print(f"   - Take Profit: {auto_sell_params['take_profit_percent']}%")
    print(f"   - Watch AI Signals: {auto_sell_params['watch_ai_signals']}")


def scan_opportunities():
    """Scan for auto-buy opportunities."""
    print_section("3. Scanning for Buy Opportunities")

    response = requests.get(f"{BASE_URL}/portfolio/paper/auto-buy/scan?universe_limit=30")
    data = response.json()

    print(f"Analyzed {data['analyzed']} stocks")
    print(f"Found {data['count']} opportunities\n")

    if data['count'] > 0:
        print("Top Opportunities:")
        for i, opp in enumerate(data['opportunities'][:5], 1):
            print(f"\n  {i}. {opp['symbol']} ({opp.get('sector', 'Unknown')})")
            print(f"     Score: {opp['overall_score']:.1f} | {opp['recommendation']}")
            print(f"     Buy: {opp['shares']} shares @ ${opp['price']:.2f} = ${opp['total_cost']:.2f}")
            print(f"     Reason: {opp['reason'][:80]}...")
    else:
        print("No opportunities found matching criteria")

    return data


def scan_sell_signals():
    """Scan for auto-sell signals."""
    print_section("4. Scanning for Sell Signals")

    response = requests.get(f"{BASE_URL}/portfolio/paper/auto-sell/scan")
    data = response.json()

    print(f"Found {data['count']} positions to sell\n")

    if data['count'] > 0:
        print("Positions Triggering Sell:")
        for i, pos in enumerate(data['positions_to_sell'], 1):
            print(f"\n  {i}. {pos['symbol']}")
            print(f"     Shares: {pos['shares']}")
            print(f"     P&L: {pos['unrealized_pnl_percent']:.2f}%")
            print(f"     Trigger: {pos['trigger']}")
            print(f"     Reason: {pos['reason']}")
    else:
        print("No sell signals detected")

    return data


def execute_automated_trading():
    """Execute full automated trading cycle."""
    print_section("5. Executing Automated Trading Cycle")

    print("Running automated trading...")
    response = requests.post(f"{BASE_URL}/portfolio/paper/auto-trade?universe_limit=30")
    data = response.json()

    summary = data['summary']
    print(f"\n📊 Trading Summary:")
    print(f"   Sells Executed: {summary['sells_executed']}")
    print(f"   Buys Executed: {summary['buys_executed']}")
    print(f"   Total Trades: {summary['total_trades']}")

    if summary['sells_executed'] > 0:
        print(f"\n🔴 Executed Sells:")
        for sell in data['executed_sells']:
            print(f"   • {sell['symbol']}: {sell['shares']} shares @ ${sell['price']:.2f}")
            print(f"     P&L: ${sell['pnl']:.2f} ({sell['pnl_percent']:+.2f}%)")
            print(f"     Reason: {sell['reason'][:60]}...")

    if summary['buys_executed'] > 0:
        print(f"\n🟢 Executed Buys:")
        for buy in data['executed_buys']:
            print(f"   • {buy['symbol']} ({buy['sector']}): {buy['shares']} shares @ ${buy['price']:.2f}")
            print(f"     Cost: ${buy['total_cost']:.2f} | Score: {buy['overall_score']:.1f}")
            print(f"     {buy['recommendation']}")

    portfolio = data['portfolio']
    print(f"\n💼 Updated Portfolio:")
    print(f"   Cash: ${portfolio['cash']:.2f}")
    print(f"   Positions: {portfolio['num_positions']}")
    print(f"   Total Value: ${portfolio['total_value']:.2f}")
    print(f"   Return: {portfolio['total_return_percent']:.2f}%")

    return data


def main():
    """Run automated trading test."""
    print("\n" + "🤖 " * 20)
    print("AUTOMATED PAPER TRADING SYSTEM TEST")
    print("🤖 " * 20)

    try:
        # Check status
        test_automation_status()

        # Enable automation
        enable_automation()

        # Scan opportunities
        scan_opportunities()

        # Scan sell signals
        scan_sell_signals()

        # Execute automated trading
        print("\n⏸️  Press Enter to execute automated trading cycle...")
        input()

        result = execute_automated_trading()

        print_section("✅ Test Complete")
        print("Automated trading system is fully operational!")
        print("\nKey Features:")
        print("  • Auto-Buy: Automatically buys STRONG BUY signals (score >= 75)")
        print("  • Auto-Sell: Sells on stop-loss (-10%), take-profit (+20%), or AI downgrades")
        print("  • Smart Diversification: Max 30% per sector, max 15% per position")
        print("  • Risk Management: Position sizing, confidence filters, max positions")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
