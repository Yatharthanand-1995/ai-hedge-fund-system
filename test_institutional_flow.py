"""
Quick integration test for Institutional Flow Agent
Tests the complete 5-agent analysis pipeline
"""

import yfinance as yf
from core.stock_scorer import StockScorer
from data.enhanced_provider import EnhancedYahooProvider
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_institutional_flow_agent():
    """Test the institutional flow agent with real stock data"""

    print("\n" + "="*80)
    print("INSTITUTIONAL FLOW AGENT INTEGRATION TEST")
    print("="*80)

    # Test stock
    symbol = "AAPL"

    print(f"\n1. Testing with {symbol}...")

    # Initialize data provider
    print("\n2. Fetching comprehensive market data...")
    provider = EnhancedYahooProvider()
    comprehensive_data = provider.get_comprehensive_data(symbol)

    if comprehensive_data is None or 'historical_data' not in comprehensive_data:
        print(f"❌ Failed to fetch data for {symbol}")
        return False

    data = comprehensive_data['historical_data']

    if data is None or data.empty:
        print(f"❌ No historical data for {symbol}")
        return False
    print(f"   ✅ Data fetched: {len(data)} days")

    # Check if institutional flow indicators are present
    print("\n3. Checking institutional flow indicators...")
    tech_data = comprehensive_data.get('technical_data', {})
    required_indicators = ['obv', 'ad', 'mfi', 'cmf', 'vwap', 'volume_zscore']

    for indicator in required_indicators:
        if indicator in tech_data and tech_data[indicator] is not None:
            if hasattr(tech_data[indicator], '__len__'):
                print(f"   ✅ {indicator.upper()}: {len(tech_data[indicator])} values")
            else:
                print(f"   ✅ {indicator.upper()}: {tech_data[indicator]}")
        else:
            print(f"   ❌ {indicator.upper()}: Missing")
            return False

    # Test StockScorer with 5 agents
    print("\n4. Running 5-agent analysis...")
    scorer = StockScorer()

    print(f"   Agent weights: {scorer.default_weights}")
    print(f"   Weights sum: {sum(scorer.default_weights.values()):.2f}")

    # Run analysis
    result = scorer.score_stock(symbol, price_data=data, cached_data=comprehensive_data)

    print(f"\n5. Analysis Results for {symbol}:")
    print(f"   Composite Score: {result['composite_score']:.2f}/100")
    print(f"   Composite Confidence: {result['composite_confidence']:.2f}")
    print(f"   Recommendation: {result['rank_category']}")

    print(f"\n6. Agent Scores:")
    for agent_name, agent_result in result['agent_scores'].items():
        score = agent_result['score']
        confidence = agent_result['confidence']
        print(f"   {agent_name.capitalize():20s}: {score:5.1f} (confidence: {confidence:.2f})")

    # Verify institutional flow agent is present
    if 'institutional_flow' not in result['agent_scores']:
        print("\n   ❌ Institutional Flow Agent missing from results!")
        return False

    flow_result = result['agent_scores']['institutional_flow']
    print(f"\n7. Institutional Flow Details:")
    print(f"   Score: {flow_result['score']:.2f}")
    print(f"   Confidence: {flow_result['confidence']:.2f}")
    print(f"   Reasoning: {flow_result['reasoning']}")

    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED - 5-Agent System Working!")
    print("="*80 + "\n")

    return True


if __name__ == "__main__":
    try:
        success = test_institutional_flow_agent()
        exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Test failed with error: {e}", exc_info=True)
        exit(1)
