#!/usr/bin/env python3
"""
Test AI-First Sell Logic (Phase 4)

Verifies prioritized sell trigger hierarchy:
1. CRITICAL: Stop-loss
2. PRIMARY: AI signal downgrades
3. SECONDARY: Take-profit (deferred if AI bullish)
4. TERTIARY: Position age
"""

from core.auto_sell_monitor import AutoSellMonitor

def test_ai_first_sell_logic():
    """Test AI-first sell logic with prioritized triggers."""

    print("="*70)
    print(" PHASE 4: AI-FIRST SELL LOGIC TEST")
    print("="*70)
    print()

    monitor = AutoSellMonitor()

    # Verify config loaded with new fields
    print("Test 1: Configuration Validation")
    try:
        rules = monitor.get_rules()

        required_fields = [
            'enabled',
            'prioritize_ai_signals',
            'defer_take_profit_on_strong_signals',
            'ai_signal_sell_threshold'
        ]

        if all(field in rules for field in required_fields):
            print(f"  ✅ All AI-first config fields present")
            print(f"  ✅ Prioritize AI signals: {rules['prioritize_ai_signals']}")
            print(f"  ✅ Defer take-profit on STRONG BUY: {rules['defer_take_profit_on_strong_signals']}")
            print()
        else:
            print(f"  ❌ Missing config fields")
            return False

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

    # Test 2: Priority 1 - Stop-loss (always triggers)
    print("Test 2: PRIORITY 1 - Stop-Loss (CRITICAL)")
    try:
        result = monitor.check_position(
            symbol="TEST",
            cost_basis=100.0,
            current_price=88.0,
            unrealized_pnl_percent=-12.0,  # Below -10% threshold
            ai_recommendation="STRONG BUY",  # Even with STRONG BUY, should sell
            ai_score=95.0
        )

        if result['should_sell'] and result['trigger'] == 'stop_loss':
            print(f"  ✅ Stop-loss triggers even with STRONG BUY signal")
            print(f"  ✅ Urgency: {result['urgency']}")
            print(f"  ✅ Reason: {result['reason']}")
        else:
            print(f"  ❌ Stop-loss failed: {result}")
            return False

        print()

    except Exception as e:
        print(f"  ❌ Error: {e}")
        print()
        return False

    # Test 3: Priority 2 - AI Signal (SELL)
    print("Test 3: PRIORITY 2 - AI Signal SELL (IMMEDIATE)")
    try:
        result = monitor.check_position(
            symbol="TEST",
            cost_basis=100.0,
            current_price=115.0,
            unrealized_pnl_percent=15.0,  # Profitable position
            ai_recommendation="SELL",  # AI says sell
            ai_score=35.0
        )

        if result['should_sell'] and result['trigger'] == 'ai_signal':
            print(f"  ✅ AI SELL triggers immediately")
            print(f"  ✅ Urgency: {result['urgency']}")
            print(f"  ✅ Reason: {result['reason']}")
        else:
            print(f"  ❌ AI SELL failed: {result}")
            return False

        print()

    except Exception as e:
        print(f"  ❌ Error: {e}")
        print()
        return False

    # Test 4: Priority 2 - AI Signal (WEAK SELL)
    print("Test 4: PRIORITY 2 - AI Signal WEAK SELL (HIGH)")
    try:
        result = monitor.check_position(
            symbol="TEST",
            cost_basis=100.0,
            current_price=110.0,
            unrealized_pnl_percent=10.0,
            ai_recommendation="WEAK SELL",
            ai_score=42.0
        )

        if result['should_sell'] and result['trigger'] == 'ai_signal':
            print(f"  ✅ AI WEAK SELL triggers")
            print(f"  ✅ Urgency: {result['urgency']}")
            print(f"  ✅ Reason: {result['reason']}")
        else:
            print(f"  ❌ AI WEAK SELL failed: {result}")
            return False

        print()

    except Exception as e:
        print(f"  ❌ Error: {e}")
        print()
        return False

    # Test 5: Priority 3 - Take-profit DEFERRED (AI still bullish)
    print("Test 5: PRIORITY 3 - Take-Profit DEFERRED (AI STRONG BUY)")
    try:
        result = monitor.check_position(
            symbol="TEST",
            cost_basis=100.0,
            current_price=125.0,
            unrealized_pnl_percent=25.0,  # Above 20% threshold
            ai_recommendation="STRONG BUY",  # AI still bullish
            ai_score=88.0
        )

        if not result['should_sell']:
            print(f"  ✅ Take-profit deferred - letting winner run")
            print(f"  ✅ Reason: {result['reason']}")
        else:
            print(f"  ❌ Should NOT sell on take-profit when AI is STRONG BUY")
            print(f"  ❌ Result: {result}")
            return False

        print()

    except Exception as e:
        print(f"  ❌ Error: {e}")
        print()
        return False

    # Test 6: Priority 3 - Take-profit TRIGGERED (AI neutral/bearish)
    print("Test 6: PRIORITY 3 - Take-Profit TRIGGERED (AI HOLD)")
    try:
        result = monitor.check_position(
            symbol="TEST",
            cost_basis=100.0,
            current_price=122.0,
            unrealized_pnl_percent=22.0,  # Above 20% threshold
            ai_recommendation="HOLD",  # AI neutral
            ai_score=55.0
        )

        if result['should_sell'] and result['trigger'] == 'take_profit':
            print(f"  ✅ Take-profit triggers when AI is neutral/bearish")
            print(f"  ✅ Urgency: {result['urgency']}")
            print(f"  ✅ Reason: {result['reason']}")
        else:
            print(f"  ❌ Take-profit failed: {result}")
            return False

        print()

    except Exception as e:
        print(f"  ❌ Error: {e}")
        print()
        return False

    # Test 7: Priority 4 - Position age
    print("Test 7: PRIORITY 4 - Position Age (LOW)")
    try:
        result = monitor.check_position(
            symbol="TEST",
            cost_basis=100.0,
            current_price=105.0,
            unrealized_pnl_percent=5.0,
            ai_recommendation="HOLD",
            ai_score=60.0,
            position_age_days=185  # Over 180 days
        )

        if result['should_sell'] and result['trigger'] == 'position_age':
            print(f"  ✅ Position age triggers cleanup")
            print(f"  ✅ Urgency: {result['urgency']}")
            print(f"  ✅ Reason: {result['reason']}")
        else:
            print(f"  ❌ Position age failed: {result}")
            return False

        print()

    except Exception as e:
        print(f"  ❌ Error: {e}")
        print()
        return False

    # Test 8: Complex scenario - Take-profit + STRONG BUY
    print("Test 8: Complex Scenario - +30% Gain with STRONG BUY")
    try:
        result = monitor.check_position(
            symbol="WINNER",
            cost_basis=100.0,
            current_price=130.0,
            unrealized_pnl_percent=30.0,  # Big gain
            ai_recommendation="STRONG BUY",  # Still very bullish
            ai_score=92.0
        )

        if not result['should_sell']:
            print(f"  ✅ Holds +30% position when AI score is 92 (STRONG BUY)")
            print(f"  ✅ Strategy: Let winners run with AI confirmation")
        else:
            print(f"  ❌ Should hold winners when AI is still bullish")
            return False

        print()

    except Exception as e:
        print(f"  ❌ Error: {e}")
        print()
        return False

    # Summary
    print("="*70)
    print(" TEST SUMMARY")
    print("="*70)
    print()
    print("✅ All AI-first sell logic tests passed!")
    print()
    print("Validated Priority Hierarchy:")
    print("  1. CRITICAL: Stop-loss (-10%) - Always honored")
    print("  2. PRIMARY: AI downgrades (SELL/WEAK SELL) - Main exit driver")
    print("  3. SECONDARY: Take-profit (+20%) - Deferred if AI bullish")
    print("  4. TERTIARY: Position age (180 days) - Portfolio cleanup")
    print()
    print("Key Behaviors:")
    print("  • Stop-loss triggers even with STRONG BUY (risk management)")
    print("  • AI SELL/WEAK SELL triggers immediate exit")
    print("  • Take-profit deferred when AI still bullish (let winners run)")
    print("  • Take-profit executes when AI neutral/bearish (lock in gains)")
    print()
    print("="*70)
    print()

    return True


if __name__ == "__main__":
    test_ai_first_sell_logic()
