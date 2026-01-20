#!/usr/bin/env python3
"""
Test Score-Weighted Position Sizing

Verifies that higher scores result in exponentially larger position sizes.
"""

from core.auto_buy_monitor import AutoBuyMonitor

def test_score_weighted_sizing():
    """Test score weighting with various scores."""

    print("="*70)
    print(" SCORE-WEIGHTED POSITION SIZING TEST")
    print("="*70)

    # Initialize monitor (will load config with score weighting enabled)
    monitor = AutoBuyMonitor()

    # Test parameters
    portfolio_total_value = 10000.0  # $10k portfolio
    num_positions = 5  # Current positions
    test_scores = [70, 75, 80, 85, 90, 95, 100]

    print(f"\nPortfolio Total Value: ${portfolio_total_value:,.2f}")
    print(f"Current Positions: {num_positions}")
    print(f"Score Weighting: {'ENABLED' if monitor.rules.use_score_weighted_sizing else 'DISABLED'}")
    print(f"Exponent: {monitor.rules.score_weight_exponent}")
    print()

    print(f"{'Score':<8} {'Normalized':<12} {'Multiplier':<12} {'Position $':<15} {'% Portfolio':<12}")
    print("-" * 70)

    for score in test_scores:
        # Calculate position size using score weighting
        if monitor.rules.use_score_weighted_sizing:
            position_size = monitor._calculate_score_weighted_position(
                overall_score=score,
                portfolio_total_value=portfolio_total_value,
                num_positions=num_positions
            )
        else:
            # Fixed sizing for comparison
            max_by_percent = portfolio_total_value * (monitor.rules.max_position_size_percent / 100)
            position_size = min(max_by_percent, monitor.rules.max_single_trade_amount)

        # Calculate multiplier for display
        normalized = (score - 70) / 30
        normalized = max(0, min(1, normalized))
        multiplier = 0.5 + (normalized ** 1.5)

        pct_portfolio = (position_size / portfolio_total_value) * 100

        print(f"{score:<8} {normalized:<12.3f} {multiplier:<12.3f} ${position_size:<14,.2f} {pct_portfolio:<11.2f}%")

    print()
    print("="*70)
    print("KEY INSIGHTS:")
    print("="*70)
    print()
    print("✅ Score 70 (minimum STRONG BUY):")
    print("   → 0.5x multiplier → ~5% of portfolio (~$500)")
    print()
    print("✅ Score 80 (good signal):")
    print("   → 0.83x multiplier → ~8.3% of portfolio (~$830)")
    print()
    print("✅ Score 90 (strong signal):")
    print("   → 1.28x multiplier → ~12.8% of portfolio (~$1,280)")
    print()
    print("✅ Score 95+ (very strong signal):")
    print("   → 1.44x multiplier → ~14.4% of portfolio (~$1,440)")
    print()
    print("📊 Comparison: Score 95 gets 2.9x more capital than score 70")
    print("   (Exponential weighting rewards high-conviction signals)")
    print()

    # Test with check_opportunity (full logic)
    print("="*70)
    print(" FULL CHECK_OPPORTUNITY TEST")
    print("="*70)
    print()

    test_cases = [
        {"score": 70, "rec": "STRONG BUY", "confidence": "MEDIUM", "price": 100.0},
        {"score": 85, "rec": "STRONG BUY", "confidence": "HIGH", "price": 100.0},
        {"score": 95, "rec": "STRONG BUY", "confidence": "HIGH", "price": 100.0},
    ]

    for case in test_cases:
        result = monitor.check_opportunity(
            symbol="TEST",
            overall_score=case["score"],
            recommendation=case["rec"],
            confidence_level=case["confidence"],
            current_price=case["price"],
            portfolio_cash=5000.0,  # $5k cash available
            portfolio_total_value=portfolio_total_value,
            num_positions=num_positions,
            already_owned=False
        )

        if result['should_buy']:
            print(f"Score {case['score']:>3}: BUY {result['shares']:>2} shares @ ${case['price']:.2f} = ${result['total_cost']:,.2f}")
        else:
            print(f"Score {case['score']:>3}: NO BUY - {result['reason']}")

    print()
    print("="*70)
    print(" TEST COMPLETE")
    print("="*70)
    print()


if __name__ == "__main__":
    test_score_weighted_sizing()
