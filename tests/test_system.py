#!/usr/bin/env python3
"""
Test script for the 5-agent hedge fund system
"""

import sys
import os
# Add parent directory to path so tests can import project modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_agents():
    """Test all 5 agents with AAPL"""
    print("Testing 5-Agent AI Hedge Fund System")
    print("="*50)

    try:
        # Initialize data provider
        print("\n0. Fetching market data for AAPL...")
        from data.enhanced_provider import EnhancedYahooProvider
        data_provider = EnhancedYahooProvider()

        # Fetch comprehensive data for AAPL
        aapl_data = data_provider.get_comprehensive_data("AAPL")
        spy_data = data_provider.get_comprehensive_data("SPY")

        print("   Market data fetched successfully")

        # Test Fundamentals Agent
        print("\n1. Testing Fundamentals Agent...")
        from agents.fundamentals_agent import FundamentalsAgent
        fund_agent = FundamentalsAgent()
        fund_result = fund_agent.analyze("AAPL")
        print(f"   Fundamentals Score: {fund_result['score']}/100")
        print(f"   Confidence: {fund_result['confidence']}")

        # Test Momentum Agent
        print("\n2. Testing Momentum Agent...")
        from agents.momentum_agent import MomentumAgent
        momentum_agent = MomentumAgent()
        momentum_result = momentum_agent.analyze("AAPL", aapl_data['historical_data'], spy_data['historical_data'])
        print(f"   Momentum Score: {momentum_result['score']}/100")
        print(f"   Confidence: {momentum_result['confidence']}")

        # Test Quality Agent
        print("\n3. Testing Quality Agent...")
        from agents.quality_agent import QualityAgent
        quality_agent = QualityAgent()
        quality_result = quality_agent.analyze("AAPL", aapl_data)
        print(f"   Quality Score: {quality_result['score']}/100")
        print(f"   Confidence: {quality_result['confidence']}")

        # Test Sentiment Agent
        print("\n4. Testing Sentiment Agent...")
        from agents.sentiment_agent import SentimentAgent
        sentiment_agent = SentimentAgent()
        sentiment_result = sentiment_agent.analyze("AAPL")
        print(f"   Sentiment Score: {sentiment_result['score']}/100")
        print(f"   Confidence: {sentiment_result['confidence']}")

        # Test Institutional Flow Agent
        print("\n5. Testing Institutional Flow Agent...")
        from agents.institutional_flow_agent import InstitutionalFlowAgent
        inst_flow_agent = InstitutionalFlowAgent()
        inst_flow_result = inst_flow_agent.analyze("AAPL", aapl_data['historical_data'], aapl_data)
        print(f"   Institutional Flow Score: {inst_flow_result['score']}/100")
        print(f"   Confidence: {inst_flow_result['confidence']}")

        # Test Narrative Engine
        print("\n6. Testing Narrative Engine...")
        from narrative_engine.narrative_engine import InvestmentNarrativeEngine
        narrative_engine = InvestmentNarrativeEngine()

        agent_results = {
            'fundamentals': fund_result,
            'momentum': momentum_result,
            'quality': quality_result,
            'sentiment': sentiment_result,
            'institutional_flow': inst_flow_result
        }

        narrative = narrative_engine.generate_comprehensive_thesis("AAPL", agent_results)

        print(f"\n7. COMPLETE ANALYSIS RESULTS FOR AAPL:")
        print("="*60)
        print(f"Overall Score: {narrative['overall_score']}/100")
        print(f"Recommendation: {narrative['recommendation']}")
        print(f"Confidence Level: {narrative['confidence_level']}")
        print(f"\nAgent Scores:")
        for agent, score in narrative['agent_scores'].items():
            print(f"  {agent.capitalize()}: {score}/100")

        print(f"\nKey Strengths:")
        for strength in narrative['key_strengths']:
            print(f"  • {strength}")

        print(f"\nKey Risks:")
        for risk in narrative['key_risks']:
            print(f"  • {risk}")

        print(f"\nInvestment Thesis:")
        print("-" * 40)
        print(narrative['investment_thesis'])

        return True

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_agents()