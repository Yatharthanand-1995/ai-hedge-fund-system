"""
Simplified integration test for 5-agent system
"""

import yfinance as yf
from core.stock_scorer import StockScorer
import logging

logging.basicConfig(level=logging.WARNING)

def test_five_agent_system():
    """Test the 5-agent scoring system"""

    print("\n" + "="*80)
    print("5-AGENT SYSTEM INTEGRATION TEST")
    print("="*80)

    symbol = "AAPL"
    print(f"\n1. Testing {symbol} with 5-agent system...")

    # Initialize scorer
    scorer = StockScorer()

    print(f"\n2. Agent Configuration:")
    print(f"   Agents: {list(scorer.default_weights.keys())}")
    print(f"   Weights: {scorer.default_weights}")
    print(f"   Sum: {sum(scorer.default_weights.values()):.2f}")

    # Check we have 5 agents
    if len(scorer.default_weights) != 5:
        print(f"\n   ❌ Expected 5 agents, got {len(scorer.default_weights)}")
        return False

    # Check weights sum to 1.0
    if abs(sum(scorer.default_weights.values()) - 1.0) > 0.01:
        print(f"\n   ❌ Weights don't sum to 1.0")
        return False

    # Check institutional_flow is present
    if 'institutional_flow' not in scorer.default_weights:
        print(f"\n   ❌ institutional_flow agent missing")
        return False

    print(f"   ✅ All 5 agents configured correctly")

    # Run analysis
    print(f"\n3. Running analysis on {symbol}...")
    try:
        result = scorer.score_stock(symbol)

        print(f"\n4. Results:")
        print(f"   Composite Score: {result['composite_score']:.2f}/100")
        print(f"   Confidence: {result['composite_confidence']:.2f}")
        print(f"   Recommendation: {result['rank_category']}")

        print(f"\n5. Agent Breakdown:")
        for agent_name in sorted(result['agent_scores'].keys()):
            agent_result = result['agent_scores'][agent_name]
            score = agent_result['score']
            conf = agent_result['confidence']
            print(f"   {agent_name:20s}: {score:5.1f} (conf: {conf:.2f})")

        # Verify institutional_flow is in results
        if 'institutional_flow' not in result['agent_scores']:
            print(f"\n   ❌ institutional_flow missing from results")
            return False

        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED - 5-Agent System Working!")
        print("="*80 + "\n")
        return True

    except Exception as e:
        print(f"\n   ❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_five_agent_system()
    exit(0 if success else 1)
