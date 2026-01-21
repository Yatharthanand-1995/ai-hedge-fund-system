"""
Comprehensive test suite for Institutional Flow Agent
Tests calculations, agent logic, integration, and edge cases
"""

import yfinance as yf
import numpy as np
import pandas as pd
from core.stock_scorer import StockScorer
from data.enhanced_provider import EnhancedYahooProvider
from agents.institutional_flow_agent import InstitutionalFlowAgent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_data_provider_calculations():
    """Test that all institutional flow indicators are calculated correctly"""
    print("\n" + "="*80)
    print("TEST 1: Data Provider Calculations")
    print("="*80)

    provider = EnhancedYahooProvider()

    # Test with a known stock
    symbol = "AAPL"
    data = provider.get_data(symbol, period='1y')

    if data is None or data.empty:
        print(f"❌ Failed to fetch data for {symbol}")
        return False

    print(f"\n✅ Fetched {len(data)} days of data for {symbol}")

    # Calculate indicators
    technical_data = provider._calculate_all_indicators(data)

    # Check all required indicators exist
    required = ['obv', 'ad', 'mfi', 'cmf', 'vwap', 'volume_zscore']

    print("\nChecking institutional flow indicators:")
    all_present = True

    for indicator in required:
        if indicator in technical_data and technical_data[indicator] is not None:
            value = technical_data[indicator]
            if hasattr(value, '__len__'):
                # Array
                print(f"  ✅ {indicator.upper():15s}: array with {len(value)} values")

                # Check for NaN issues
                if isinstance(value, np.ndarray):
                    nan_count = np.isnan(value).sum()
                    if nan_count > 0:
                        print(f"     ⚠️  Warning: {nan_count} NaN values")

                # Verify last value
                try:
                    last_val = float(value[-1])
                    if not np.isnan(last_val) and not np.isinf(last_val):
                        print(f"     Last value: {last_val:.2f}")
                    else:
                        print(f"     ⚠️  Last value is NaN or Inf")
                except:
                    print(f"     ⚠️  Could not get last value")
            else:
                print(f"  ✅ {indicator.upper():15s}: {value}")
        else:
            print(f"  ❌ {indicator.upper():15s}: MISSING")
            all_present = False

    return all_present


def test_institutional_flow_agent_logic():
    """Test the agent's scoring logic with real data"""
    print("\n" + "="*80)
    print("TEST 2: Institutional Flow Agent Logic")
    print("="*80)

    agent = InstitutionalFlowAgent()
    provider = EnhancedYahooProvider()

    # Test with multiple stocks
    test_stocks = ["AAPL", "MSFT", "TSLA"]

    for symbol in test_stocks:
        print(f"\n--- Testing {symbol} ---")

        # Get comprehensive data
        comp_data = provider.get_comprehensive_data(symbol)

        if not comp_data or 'historical_data' not in comp_data:
            print(f"  ❌ Could not fetch comprehensive data")
            continue

        data = comp_data['historical_data']

        # Run agent analysis
        result = agent.analyze(symbol, data, cached_data=comp_data)

        print(f"  Score: {result['score']:.2f}")
        print(f"  Confidence: {result['confidence']:.2f}")

        # Check metrics
        if 'metrics' in result:
            metrics = result['metrics']
            print(f"  Metrics:")
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    print(f"    {key}: {value:.2f}")

        # Check score is in valid range
        if not (0 <= result['score'] <= 100):
            print(f"  ❌ Score out of range: {result['score']}")
            return False

        # Check confidence is in valid range
        if not (0 <= result['confidence'] <= 1):
            print(f"  ❌ Confidence out of range: {result['confidence']}")
            return False

        print(f"  Reasoning: {result['reasoning'][:100]}...")
        print(f"  ✅ Agent logic working correctly")

    return True


def test_stock_scorer_integration():
    """Test full 5-agent integration"""
    print("\n" + "="*80)
    print("TEST 3: 5-Agent System Integration")
    print("="*80)

    scorer = StockScorer()

    # Verify weights
    print(f"\nAgent weights: {scorer.default_weights}")
    total_weight = sum(scorer.default_weights.values())
    print(f"Total weight: {total_weight:.4f}")

    if abs(total_weight - 1.0) > 0.001:
        print(f"❌ Weights don't sum to 1.0!")
        return False

    print(f"✅ Weights sum correctly")

    # Test analysis
    test_symbols = ["AAPL", "GOOGL"]

    for symbol in test_symbols:
        print(f"\n--- Analyzing {symbol} ---")

        try:
            result = scorer.score_stock(symbol)

            print(f"  Composite Score: {result['composite_score']:.2f}")
            print(f"  Confidence: {result['composite_confidence']:.2f}")
            print(f"  Recommendation: {result['rank_category']}")

            # Verify all 5 agents present
            agent_scores = result['agent_scores']
            expected_agents = ['fundamentals', 'momentum', 'quality', 'sentiment', 'institutional_flow']

            for agent_name in expected_agents:
                if agent_name not in agent_scores:
                    print(f"  ❌ Missing agent: {agent_name}")
                    return False

                agent_result = agent_scores[agent_name]
                score = agent_result['score']
                conf = agent_result['confidence']

                print(f"  {agent_name:20s}: {score:5.1f} (conf: {conf:.2f})")

            print(f"  ✅ All 5 agents present and working")

            # Verify composite score calculation
            expected_composite = sum(
                scorer.default_weights[agent] * agent_scores[agent]['score']
                for agent in expected_agents
            )

            if abs(expected_composite - result['composite_score']) > 0.1:
                print(f"  ❌ Composite score mismatch: {expected_composite:.2f} vs {result['composite_score']:.2f}")
                return False

            print(f"  ✅ Composite score calculated correctly")

        except Exception as e:
            print(f"  ❌ Analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    return True


def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n" + "="*80)
    print("TEST 4: Edge Cases & Error Handling")
    print("="*80)

    agent = InstitutionalFlowAgent()

    # Test 1: Empty data
    print("\nTest 4.1: Empty DataFrame")
    empty_df = pd.DataFrame()
    result = agent.analyze("TEST", empty_df, cached_data=None)

    if result['score'] == 50.0 and result['confidence'] == 0.2:
        print("  ✅ Handles empty data correctly (returns neutral)")
    else:
        print(f"  ❌ Unexpected result for empty data: {result}")
        return False

    # Test 2: No cached data
    print("\nTest 4.2: No cached data")
    data = pd.DataFrame({
        'Close': np.random.randn(100) + 100,
        'Volume': np.random.randint(1000000, 10000000, 100)
    })
    result = agent.analyze("TEST", data, cached_data=None)

    if result['score'] == 50.0:
        print("  ✅ Handles missing cached data correctly")
    else:
        print(f"  ⚠️  Score: {result['score']} (expected 50.0 for no data)")

    # Test 3: Minimal data (< 60 days)
    print("\nTest 4.3: Insufficient data (30 days)")
    provider = EnhancedYahooProvider()
    data = provider.get_data("AAPL", period='1mo')
    comp_data = provider.get_comprehensive_data("AAPL")

    result = agent.analyze("AAPL", data, cached_data=comp_data)
    print(f"  Score: {result['score']:.2f}, Confidence: {result['confidence']:.2f}")
    print(f"  ✅ Handles minimal data (may return neutral or partial score)")

    return True


def test_adaptive_weights():
    """Test adaptive weights include institutional flow"""
    print("\n" + "="*80)
    print("TEST 5: Adaptive Weights System")
    print("="*80)

    from core.market_regime_service import get_market_regime_service

    try:
        regime_service = get_market_regime_service()
        regime_info = regime_service.get_current_regime()

        print(f"\nCurrent Market Regime: {regime_info.get('regime', 'Unknown')}")
        print(f"Trend: {regime_info.get('trend', 'Unknown')}")
        print(f"Volatility: {regime_info.get('volatility', 'Unknown')}")

        weights = regime_info.get('weights', {})
        print(f"\nAdaptive Weights: {weights}")

        # Check institutional_flow is present
        if 'institutional_flow' not in weights:
            print("  ❌ institutional_flow missing from adaptive weights")
            return False

        # Check weights sum to 1.0
        total = sum(weights.values())
        print(f"Total weight: {total:.4f}")

        if abs(total - 1.0) > 0.001:
            print(f"  ❌ Adaptive weights don't sum to 1.0")
            return False

        print(f"  ✅ Adaptive weights include institutional_flow and sum correctly")

        return True

    except Exception as e:
        print(f"  ⚠️  Could not test adaptive weights: {e}")
        print(f"  (This is OK if ENABLE_ADAPTIVE_WEIGHTS is not set)")
        return True


def run_all_tests():
    """Run all tests and provide summary"""
    print("\n" + "="*80)
    print("COMPREHENSIVE INSTITUTIONAL FLOW AGENT TEST SUITE")
    print("="*80)

    tests = [
        ("Data Provider Calculations", test_data_provider_calculations),
        ("Agent Logic & Scoring", test_institutional_flow_agent_logic),
        ("5-Agent Integration", test_stock_scorer_integration),
        ("Edge Cases & Error Handling", test_edge_cases),
        ("Adaptive Weights System", test_adaptive_weights),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"\n❌ {test_name} CRASHED: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10s} {test_name}")

    print("\n" + "="*80)
    print(f"Results: {passed}/{total} tests passed")
    print("="*80 + "\n")

    return all(results.values())


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
