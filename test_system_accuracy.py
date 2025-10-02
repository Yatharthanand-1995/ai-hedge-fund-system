#!/usr/bin/env python3
"""
System Accuracy Analysis Script
Tests all 4 agents and identifies potential issues
"""

import requests
import json
import pandas as pd
from typing import Dict, List
import time

BASE_URL = "http://localhost:8010"

def test_agent_consistency():
    """Test consistency across different stocks"""

    print("🔍 SYSTEM ACCURACY ANALYSIS")
    print("=" * 50)

    # Test stocks from different sectors
    test_stocks = ['AAPL', 'GOOGL', 'MSFT', 'NVDA', 'JPM', 'UNH', 'WMT']
    results = []

    for symbol in test_stocks:
        try:
            print(f"\n📊 Testing {symbol}...")

            response = requests.post(f"{BASE_URL}/analyze",
                                   json={"symbol": symbol},
                                   timeout=30)

            if response.status_code == 200:
                data = response.json()

                # Extract scores from the correct API response structure
                narrative = data.get('narrative', {})
                agent_scores = narrative.get('agent_scores', {})

                # Calculate average confidence from all agents
                agent_results = data.get('agent_results', {})
                confidences = [agent.get('confidence', 0) for agent in agent_results.values()]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0

                # Generate signals based on overall score and recommendation
                overall_score = narrative.get('overall_score', 0)
                recommendation = narrative.get('recommendation', 'HOLD')

                # Signal logic based on recommendation
                buy_signal = recommendation in ['STRONG BUY', 'BUY', 'WEAK BUY']
                hold_signal = recommendation == 'HOLD'
                sell_signal = recommendation in ['WEAK SELL', 'SELL', 'STRONG SELL']

                result = {
                    'symbol': symbol,
                    'composite_score': overall_score,
                    'confidence': avg_confidence,
                    'fundamentals': agent_scores.get('fundamentals', 0),
                    'momentum': agent_scores.get('momentum', 0),
                    'quality': agent_scores.get('quality', 0),
                    'sentiment': agent_scores.get('sentiment', 0),
                    'buy_signal': buy_signal,
                    'hold_signal': hold_signal,
                    'sell_signal': sell_signal
                }
                results.append(result)

                print(f"  Composite: {result['composite_score']:.1f}")
                print(f"  Fund: {result['fundamentals']:.1f} | Mom: {result['momentum']:.1f} | Qual: {result['quality']:.1f} | Sent: {result['sentiment']:.1f}")
                print(f"  Signals: Buy={result['buy_signal']} Hold={result['hold_signal']} Sell={result['sell_signal']}")

            else:
                print(f"  ❌ Failed to analyze {symbol}: {response.status_code}")

        except Exception as e:
            print(f"  ❌ Error analyzing {symbol}: {e}")

    return results

def test_portfolio_endpoint():
    """Test portfolio top-picks endpoint"""

    print(f"\n🎯 Testing Portfolio Endpoint...")

    try:
        # Use shorter timeout and limit to avoid long processing times
        response = requests.get(f"{BASE_URL}/portfolio/top-picks?limit=3", timeout=120)

        if response.status_code == 200:
            data = response.json()

            print(f"  ✅ Portfolio endpoint working")
            print(f"  Top picks count: {len(data.get('top_picks', []))}")
            print(f"  Total portfolio value: ${data.get('portfolio_summary', {}).get('total_value', 0):,.0f}")

            # Show top 3 picks with corrected field access
            top_picks = data.get('top_picks', [])[:3]
            for i, pick in enumerate(top_picks, 1):
                score = pick.get('overall_score', pick.get('composite_score', 0))
                weight = pick.get('weight', 0)
                print(f"  #{i}: {pick.get('symbol')} - Score: {score:.1f} - Weight: {weight:.1f}%")

            return True
        else:
            print(f"  ❌ Portfolio endpoint failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"  ❌ Portfolio endpoint error: {e}")
        return False

def analyze_scoring_issues(results: List[Dict]):
    """Analyze potential scoring issues"""

    print(f"\n🚨 POTENTIAL ISSUES IDENTIFIED:")

    issues = []

    # Check for unrealistic scores
    for result in results:
        symbol = result['symbol']

        # Check fundamentals scoring
        if result['fundamentals'] < 40 and symbol in ['AAPL', 'MSFT', 'GOOGL']:
            issues.append(f"❌ {symbol} fundamentals too low ({result['fundamentals']:.1f}) for mega-cap quality")

        # Check for zero scores
        for agent in ['fundamentals', 'momentum', 'quality', 'sentiment']:
            if result[agent] == 0:
                issues.append(f"❌ {symbol} {agent} agent returned 0 (data issue?)")

        # Check signal logic
        signals = [result['buy_signal'], result['hold_signal'], result['sell_signal']]
        if sum(signals) != 1:
            issues.append(f"❌ {symbol} invalid signal state (should have exactly 1 signal)")

        # Check confidence
        if result['confidence'] < 0.5:
            issues.append(f"⚠️  {symbol} low confidence ({result['confidence']:.2f}) - data quality issue")

    # Statistical analysis
    df = pd.DataFrame(results)

    print(f"\n📈 SCORING STATISTICS:")
    print(f"Average Composite Score: {df['composite_score'].mean():.1f}")
    print(f"Average Confidence: {df['confidence'].mean():.2f}")
    print(f"Fundamentals Range: {df['fundamentals'].min():.1f} - {df['fundamentals'].max():.1f}")
    print(f"Momentum Range: {df['momentum'].min():.1f} - {df['momentum'].max():.1f}")
    print(f"Quality Range: {df['quality'].min():.1f} - {df['quality'].max():.1f}")
    print(f"Sentiment Range: {df['sentiment'].min():.1f} - {df['sentiment'].max():.1f}")

    if issues:
        print(f"\n⚠️  ISSUES FOUND ({len(issues)}):")
        for issue in issues:
            print(f"  {issue}")
    else:
        print(f"\n✅ NO MAJOR ISSUES DETECTED")

    return issues

def suggest_improvements(issues: List[str]):
    """Suggest system improvements"""

    print(f"\n💡 IMPROVEMENT RECOMMENDATIONS:")

    if any("fundamentals too low" in issue for issue in issues):
        print(f"1. 🔧 Further optimize fundamentals thresholds for mega-caps")
        print(f"   - Current thresholds may still be too harsh")
        print(f"   - Consider Apple/Microsoft as baseline for 'good' scores")

    if any("returned 0" in issue for issue in issues):
        print(f"2. 🔧 Fix data retrieval issues")
        print(f"   - Some agents returning 0 scores (data problems)")
        print(f"   - Add better error handling and fallbacks")

    if any("low confidence" in issue for issue in issues):
        print(f"3. 🔧 Improve data quality")
        print(f"   - Low confidence indicates missing data")
        print(f"   - Add data validation and enrichment")

    if any("invalid signal" in issue for issue in issues):
        print(f"4. 🔧 Fix signal logic")
        print(f"   - Ensure exactly one signal per stock")
        print(f"   - Review signal generation thresholds")

    print(f"\n🎯 PRIORITY FIXES:")
    print(f"1. High: Data quality and zero scores")
    print(f"2. Medium: Fundamentals threshold fine-tuning")
    print(f"3. Low: Signal logic validation")

if __name__ == "__main__":
    print("Starting comprehensive system accuracy analysis...")

    # Test individual agents
    results = test_agent_consistency()

    # Test portfolio endpoint
    portfolio_works = test_portfolio_endpoint()

    # Analyze issues
    if results:
        issues = analyze_scoring_issues(results)
        suggest_improvements(issues)
    else:
        issues = ["No data collected"]

    print(f"\n🏁 ANALYSIS COMPLETE")
    print(f"System Status: {'✅ Healthy' if not issues and portfolio_works else '⚠️ Issues Found'}")