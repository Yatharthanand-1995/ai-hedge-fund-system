"""
Test Script for Market Regime Detection & Adaptive Weights
"""

import os
import sys

# Add the root project directory to path
sys.path.insert(0, os.path.dirname(__file__))

from core.market_regime_service import MarketRegimeService
from core.stock_scorer import StockScorer
from data.us_top_100_stocks import SECTOR_MAPPING
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_regime_detection():
    """Test market regime detection"""
    print("\n" + "="*60)
    print("🧪 TESTING MARKET REGIME DETECTION")
    print("="*60 + "\n")

    # Initialize regime service
    regime_service = MarketRegimeService(cache_duration_hours=0)  # No cache for testing

    # Get current market regime
    print("1. Detecting current market regime (analyzing SPY)...")
    regime_info = regime_service.get_current_regime(force_refresh=True)

    print(f"\n📊 MARKET REGIME DETECTED:")
    print(f"   Composite Regime: {regime_info['regime']}")
    print(f"   Trend: {regime_info['trend']}")
    print(f"   Volatility: {regime_info['volatility']}")
    print(f"   Timestamp: {regime_info['timestamp']}")

    # Get adaptive weights
    print(f"\n⚙️  ADAPTIVE AGENT WEIGHTS:")
    weights = regime_info['weights']
    for agent, weight in weights.items():
        print(f"   {agent.capitalize()}: {weight*100:.0f}%")

    # Get explanation
    explanation = regime_service.get_regime_explanation(regime_info['regime'])
    print(f"\n💡 EXPLANATION:")
    print(f"   {explanation}")

    return regime_info


def test_static_vs_adaptive():
    """Compare static vs adaptive weight scoring"""
    print("\n" + "="*60)
    print("🔬 COMPARING STATIC VS ADAPTIVE WEIGHTS")
    print("="*60 + "\n")

    test_symbols = ['AAPL', 'MSFT', 'GOOGL']

    # Test with static weights
    print("1. Testing with STATIC weights (40/30/20/10)...")
    static_scorer = StockScorer(
        sector_mapping=SECTOR_MAPPING,
        use_adaptive_weights=False
    )

    static_results = {}
    for symbol in test_symbols:
        try:
            result = static_scorer.score_stock(symbol)
            static_results[symbol] = result['composite_score']
            print(f"   {symbol}: {result['composite_score']:.1f}")
        except Exception as e:
            print(f"   {symbol}: Error - {e}")
            static_results[symbol] = None

    # Test with adaptive weights
    print(f"\n2. Testing with ADAPTIVE weights (regime-based)...")

    # Enable adaptive weights
    os.environ['ENABLE_ADAPTIVE_WEIGHTS'] = 'true'

    adaptive_scorer = StockScorer(
        sector_mapping=SECTOR_MAPPING,
        use_adaptive_weights=True
    )

    adaptive_results = {}
    for symbol in test_symbols:
        try:
            result = adaptive_scorer.score_stock(symbol)
            adaptive_results[symbol] = result['composite_score']
            weights_used = result.get('weights_used', {})
            regime = result.get('market_regime', {})

            print(f"   {symbol}: {result['composite_score']:.1f} (regime: {regime.get('regime', 'N/A')})")
            print(f"      Weights: F:{weights_used.get('fundamentals', 0)*100:.0f}% "
                  f"M:{weights_used.get('momentum', 0)*100:.0f}% "
                  f"Q:{weights_used.get('quality', 0)*100:.0f}% "
                  f"S:{weights_used.get('sentiment', 0)*100:.0f}%")
        except Exception as e:
            print(f"   {symbol}: Error - {e}")
            adaptive_results[symbol] = None

    # Compare results
    print(f"\n📈 COMPARISON:")
    print(f"{'Symbol':<10} {'Static':<10} {'Adaptive':<10} {'Difference':<10}")
    print("-" * 45)

    for symbol in test_symbols:
        static_score = static_results.get(symbol)
        adaptive_score = adaptive_results.get(symbol)

        if static_score is not None and adaptive_score is not None:
            diff = adaptive_score - static_score
            diff_str = f"{diff:+.1f}"
            print(f"{symbol:<10} {static_score:<10.1f} {adaptive_score:<10.1f} {diff_str:<10}")
        else:
            print(f"{symbol:<10} {'N/A':<10} {'N/A':<10} {'N/A':<10}")

    # Reset environment variable
    os.environ['ENABLE_ADAPTIVE_WEIGHTS'] = 'false'


def main():
    """Run all tests"""
    try:
        # Test 1: Regime Detection
        regime_info = test_regime_detection()

        # Test 2: Static vs Adaptive Comparison
        test_static_vs_adaptive()

        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*60 + "\n")

        print("🎯 NEXT STEPS:")
        print("   1. To enable adaptive weights in production:")
        print("      - Set ENABLE_ADAPTIVE_WEIGHTS=true in .env")
        print("   2. Check current regime anytime:")
        print("      - GET http://localhost:8010/market/regime")
        print("   3. Regime is cached for 6 hours (refreshes automatically)")
        print()

    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        print(f"\n❌ ERROR: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
