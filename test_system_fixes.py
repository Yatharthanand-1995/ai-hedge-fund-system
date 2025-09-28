#!/usr/bin/env python3
"""
Test System Fixes
Verify that all implemented fixes are working correctly
"""

import requests
import json
import time
from typing import Dict, List

BASE_URL = "http://localhost:8010"

def test_enhanced_error_handling():
    """Test enhanced error handling with partial scoring"""
    print("🔧 Testing Enhanced Error Handling...")

    # Test with a valid stock to ensure normal operation
    try:
        response = requests.post(f"{BASE_URL}/analyze",
                               json={"symbol": "AAPL"},
                               timeout=30)

        if response.status_code == 200:
            data = response.json()
            confidence = data.get('confidence', 0)
            score = data.get('composite_score', 0)

            print(f"  ✅ AAPL analysis successful: Score={score:.1f}, Confidence={confidence:.2f}")

            # Check if we have metrics indicating data quality
            agent_scores = data.get('agent_scores', {})
            fundamentals_score = agent_scores.get('fundamentals', 0)

            if fundamentals_score > 0:
                print(f"  ✅ Fundamentals agent working: {fundamentals_score:.1f}")
            else:
                print(f"  ⚠️  Fundamentals agent returned 0 score")

        else:
            print(f"  ❌ Failed to analyze AAPL: {response.status_code}")

    except Exception as e:
        print(f"  ❌ Error testing enhanced error handling: {e}")

def test_data_quality_validation():
    """Test data quality validation layer"""
    print("\n📊 Testing Data Quality Validation...")

    try:
        # Test multiple stocks to check data quality validation
        test_symbols = ['AAPL', 'GOOGL', 'MSFT']

        for symbol in test_symbols:
            response = requests.post(f"{BASE_URL}/analyze",
                                   json={"symbol": symbol},
                                   timeout=30)

            if response.status_code == 200:
                data = response.json()
                confidence = data.get('confidence', 0)

                # Check if confidence is reasonable (not 0, not 1)
                if 0.1 <= confidence <= 1.0:
                    print(f"  ✅ {symbol}: Reasonable confidence={confidence:.2f}")
                else:
                    print(f"  ⚠️  {symbol}: Unusual confidence={confidence:.2f}")

            else:
                print(f"  ❌ Failed to analyze {symbol}")

    except Exception as e:
        print(f"  ❌ Error testing data quality validation: {e}")

def test_graceful_degradation():
    """Test graceful degradation for external dependencies"""
    print("\n🛡️ Testing Graceful Degradation...")

    try:
        # Test that system handles partial data gracefully
        response = requests.post(f"{BASE_URL}/analyze",
                               json={"symbol": "NVDA"},
                               timeout=30)

        if response.status_code == 200:
            data = response.json()
            agent_scores = data.get('agent_scores', {})

            # Check all agents returned scores
            agents = ['fundamentals', 'momentum', 'quality', 'sentiment']
            working_agents = 0

            for agent in agents:
                score = agent_scores.get(agent, 0)
                if score > 0:
                    working_agents += 1
                    print(f"  ✅ {agent} agent: {score:.1f}")
                else:
                    print(f"  ⚠️  {agent} agent: {score} (may be using fallback)")

            if working_agents >= 3:  # At least 3 out of 4 agents working
                print(f"  ✅ System degradation: {working_agents}/4 agents operational")
            else:
                print(f"  ❌ Poor degradation: Only {working_agents}/4 agents working")

        else:
            print(f"  ❌ Failed to test graceful degradation")

    except Exception as e:
        print(f"  ❌ Error testing graceful degradation: {e}")

def test_portfolio_endpoint():
    """Test that portfolio endpoint still works with fixes"""
    print("\n🎯 Testing Portfolio Endpoint...")

    try:
        response = requests.get(f"{BASE_URL}/portfolio/top-picks", timeout=60)

        if response.status_code == 200:
            data = response.json()
            top_picks = data.get('top_picks', [])

            if len(top_picks) > 0:
                print(f"  ✅ Portfolio endpoint working: {len(top_picks)} top picks")

                # Check first pick has required fields
                first_pick = top_picks[0]
                required_fields = ['symbol', 'composite_score', 'confidence', 'weight']

                for field in required_fields:
                    if field in first_pick:
                        print(f"  ✅ {field}: {first_pick[field]}")
                    else:
                        print(f"  ❌ Missing field: {field}")

            else:
                print(f"  ❌ No top picks returned")

        else:
            print(f"  ❌ Portfolio endpoint failed: {response.status_code}")

    except Exception as e:
        print(f"  ❌ Error testing portfolio endpoint: {e}")

def test_confidence_improvements():
    """Test confidence weighting improvements"""
    print("\n🎯 Testing Confidence Improvements...")

    try:
        # Test multiple stocks and check confidence distribution
        test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'JPM', 'UNH']
        confidences = []

        for symbol in test_symbols:
            response = requests.post(f"{BASE_URL}/analyze",
                                   json={"symbol": symbol},
                                   timeout=30)

            if response.status_code == 200:
                data = response.json()
                confidence = data.get('confidence', 0)
                confidences.append(confidence)
                print(f"  📊 {symbol}: confidence={confidence:.2f}")

        if confidences:
            avg_confidence = sum(confidences) / len(confidences)
            min_confidence = min(confidences)
            max_confidence = max(confidences)

            print(f"  📈 Average confidence: {avg_confidence:.2f}")
            print(f"  📉 Range: {min_confidence:.2f} - {max_confidence:.2f}")

            # Check if confidence distribution is reasonable
            if min_confidence >= 0.2 and avg_confidence >= 0.5:
                print(f"  ✅ Confidence distribution looks healthy")
            else:
                print(f"  ⚠️  Confidence distribution may need adjustment")

    except Exception as e:
        print(f"  ❌ Error testing confidence improvements: {e}")

def main():
    print("🚀 SYSTEM FIXES VALIDATION")
    print("=" * 50)

    # Run all tests
    test_enhanced_error_handling()
    test_data_quality_validation()
    test_graceful_degradation()
    test_portfolio_endpoint()
    test_confidence_improvements()

    print(f"\n🏁 VALIDATION COMPLETE")
    print("Check the results above to verify all fixes are working properly.")

if __name__ == "__main__":
    main()