#!/usr/bin/env python3
"""
Setup 6-Month Automated Paper Trading

This script configures the paper trading system to:
1. Auto-buy stocks with STRONG BUY recommendations
2. Auto-sell positions after 6 months (180 days)
3. Apply standard stop-loss and take-profit rules
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8010"


def setup_auto_buy_rules():
    """Configure auto-buy rules for STRONG BUY signals."""
    print("\n" + "="*70)
    print("CONFIGURING AUTO-BUY RULES")
    print("="*70)

    params = {
        "enabled": True,
        "min_score_threshold": 75.0,  # Only buy if score >= 75
        "max_position_size_percent": 15.0,  # Max 15% per position
        "max_positions": 10,  # Max 10 positions
        "min_confidence_level": "MEDIUM",  # MEDIUM or HIGH confidence
        "max_single_trade_amount": 2000.0,  # Max $2000 per trade
        "require_sector_diversification": True,  # Avoid sector concentration
        "max_sector_allocation_percent": 30.0  # Max 30% per sector
    }

    response = requests.post(f"{BASE_URL}/portfolio/paper/auto-buy/rules", params=params)
    result = response.json()

    if result.get('success'):
        print("✅ Auto-buy rules configured successfully!")
        print("\nAuto-Buy Configuration:")
        for key, value in result['rules'].items():
            print(f"  • {key}: {value}")
    else:
        print(f"❌ Failed to configure auto-buy rules: {result}")

    return result


def setup_auto_sell_rules():
    """Configure auto-sell rules with 6-month holding period."""
    print("\n" + "="*70)
    print("CONFIGURING AUTO-SELL RULES (6-MONTH HOLD)")
    print("="*70)

    params = {
        "enabled": True,
        "stop_loss_percent": -10.0,  # Sell if loss >= -10%
        "take_profit_percent": 20.0,  # Sell if gain >= +20%
        "watch_ai_signals": True,  # Sell if AI downgrades to SELL
        "max_position_age_days": 180  # Auto-sell after 6 months (180 days)
    }

    response = requests.post(f"{BASE_URL}/portfolio/paper/auto-sell/rules", params=params)
    result = response.json()

    if result.get('success'):
        print("✅ Auto-sell rules configured successfully!")
        print("\nAuto-Sell Configuration:")
        for key, value in result['rules'].items():
            if key == 'max_position_age_days':
                print(f"  • {key}: {value} days (≈ {value // 30} months)")
            else:
                print(f"  • {key}: {value}")
    else:
        print(f"❌ Failed to configure auto-sell rules: {result}")

    return result


def check_status():
    """Check current automation status."""
    print("\n" + "="*70)
    print("AUTOMATION STATUS")
    print("="*70)

    response = requests.get(f"{BASE_URL}/portfolio/paper/auto-trade/status")
    status = response.json()

    auto_enabled = status.get('automation_enabled', {})
    portfolio = status.get('portfolio', {})

    print(f"\n📊 Portfolio Summary:")
    print(f"  • Cash: ${portfolio.get('cash', 0):,.2f}")
    print(f"  • Total Value: ${portfolio.get('total_value', 0):,.2f}")
    print(f"  • Positions: {len(portfolio.get('positions', {}))}")

    print(f"\n🤖 Automation Status:")
    print(f"  • Auto-Buy: {'✅ Enabled' if auto_enabled.get('auto_buy') else '❌ Disabled'}")
    print(f"  • Auto-Sell: {'✅ Enabled' if auto_enabled.get('auto_sell') else '❌ Disabled'}")
    print(f"  • Fully Automated: {'✅ Yes' if auto_enabled.get('fully_automated') else '❌ No'}")

    return status


def scan_opportunities():
    """Scan for current buy opportunities."""
    print("\n" + "="*70)
    print("SCANNING FOR BUY OPPORTUNITIES")
    print("="*70)

    response = requests.get(f"{BASE_URL}/portfolio/paper/auto-buy/scan", params={"universe_limit": 20})
    opportunities = response.json()

    count = opportunities.get('count', 0)
    print(f"\n🔍 Found {count} buy opportunities")

    if count > 0:
        print("\nTop Opportunities:")
        for opp in opportunities.get('opportunities', [])[:5]:
            print(f"  • {opp['symbol']}: {opp['recommendation']} "
                  f"(Score: {opp['overall_score']:.1f}, "
                  f"Shares: {opp['shares']}, "
                  f"Cost: ${opp['total_cost']:.2f})")
    else:
        print("\n  No opportunities found that meet current criteria.")
        print("  This may be due to:")
        print("    - Already at max positions")
        print("    - All high-scoring stocks already owned")
        print("    - Insufficient cash")

    return opportunities


def run_test_cycle():
    """Run a test automated trading cycle."""
    print("\n" + "="*70)
    print("TEST TRADING CYCLE")
    print("="*70)

    print("\n⚠️  This will execute real trades in paper portfolio.")
    user_input = input("Continue? (yes/no): ")

    if user_input.lower() != 'yes':
        print("Skipped test cycle.")
        return None

    print("\n🚀 Executing automated trading cycle...")
    response = requests.post(f"{BASE_URL}/portfolio/paper/auto-trade")
    result = response.json()

    summary = result.get('summary', {})

    print(f"\n✅ Trading cycle completed!")
    print(f"\n📈 Results:")
    print(f"  • Total Trades: {summary.get('total_trades', 0)}")
    print(f"  • Sells Executed: {summary.get('sells_executed', 0)}")
    print(f"  • Buys Executed: {summary.get('buys_executed', 0)}")

    # Show executed sells
    if result.get('sells', {}).get('executed'):
        print(f"\n📉 Executed Sells:")
        for sell in result['sells']['executed']:
            print(f"  • {sell['symbol']}: {sell['shares']} shares @ ${sell['price']:.2f} "
                  f"({sell['trigger']})")

    # Show executed buys
    if result.get('buys', {}).get('executed'):
        print(f"\n📈 Executed Buys:")
        for buy in result['buys']['executed']:
            print(f"  • {buy['symbol']}: {buy['shares']} shares @ ${buy['price']:.2f}")

    return result


def main():
    """Main setup function."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + " 6-MONTH AUTOMATED PAPER TRADING SETUP ".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")

    print("\nThis script will configure your paper trading system to:")
    print("  1. ✅ Auto-buy stocks with STRONG BUY recommendations")
    print("  2. ✅ Auto-sell positions after 6 months (180 days)")
    print("  3. ✅ Apply stop-loss (-10%) and take-profit (+20%) rules")
    print("  4. ✅ Monitor AI signal changes")

    try:
        # Check if API is running
        print("\n🔌 Checking API connection...")
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is running")
        else:
            print(f"⚠️  API returned status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API at {BASE_URL}")
        print(f"   Error: {e}")
        print("\n   Please start the API server first:")
        print("   ./start_system.sh")
        return

    # Configure rules
    setup_auto_buy_rules()
    setup_auto_sell_rules()

    # Check status
    check_status()

    # Scan for opportunities
    scan_opportunities()

    # Optional: Run test cycle
    print("\n")
    run_test_cycle()

    print("\n" + "="*70)
    print("SETUP COMPLETE")
    print("="*70)
    print("\n✅ Your paper trading system is now configured for automated 6-month trading!")
    print("\nNext steps:")
    print("  1. Monitor your portfolio: http://localhost:5174/paper-trading")
    print("  2. Run manual trading cycle: curl -X POST http://localhost:8010/portfolio/paper/auto-trade")
    print("  3. View alerts: curl http://localhost:8010/portfolio/paper/auto-buy/alerts")
    print("  4. View transactions: curl http://localhost:8010/portfolio/paper/transactions")
    print("\n🎯 The system will:")
    print("  • Buy stocks when they reach STRONG BUY status")
    print("  • Sell positions automatically after 180 days (6 months)")
    print("  • Apply stop-loss and take-profit rules")
    print("  • React to AI recommendation changes")
    print()


if __name__ == "__main__":
    main()
