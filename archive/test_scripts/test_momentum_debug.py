#!/usr/bin/env python3
"""
Debug Momentum Agent - Test with real data
"""

import yfinance as yf
from agents.momentum_agent import MomentumAgent

def test_momentum_agent():
    """Test momentum agent with multiple stocks"""

    print("🔍 DEBUGGING MOMENTUM AGENT")
    print("=" * 60)

    agent = MomentumAgent()
    test_symbols = ['AAPL', 'GOOGL', 'NVDA', 'JPM', 'WMT']

    # Download SPY for relative strength
    spy_data = yf.download('SPY', period='2y', progress=False)
    print(f"✅ SPY data downloaded: {len(spy_data)} days\n")

    results = []

    for symbol in test_symbols:
        print(f"📊 Testing {symbol}...")

        # Download data
        data = yf.download(symbol, period='2y', progress=False)
        print(f"   Data points: {len(data)}")

        # Analyze
        result = agent.analyze(symbol, data, spy_data)

        print(f"   Score: {result['score']}")
        print(f"   Confidence: {result['confidence']}")
        print(f"   Reasoning: {result['reasoning']}")

        # Show component scores
        metrics = result.get('metrics', {})
        print(f"   Returns Score: {metrics.get('returns', 'N/A')}")
        print(f"   MA Score: {metrics.get('moving_averages', 'N/A')}")
        print(f"   RS Score: {metrics.get('relative_strength', 'N/A')}")
        print(f"   Quality Score: {metrics.get('trend_quality', 'N/A')}")
        print(f"   3M Return: {metrics.get('3m_return', 'N/A')}%")
        print(f"   6M Return: {metrics.get('6m_return', 'N/A')}%")
        print(f"   12M Return: {metrics.get('12m_return', 'N/A')}%")
        print()

        results.append({
            'symbol': symbol,
            'score': result['score'],
            'confidence': result['confidence']
        })

    print("\n📈 SUMMARY")
    print("=" * 60)
    for r in results:
        print(f"{r['symbol']:6s}: Score={r['score']:5.1f}, Confidence={r['confidence']:.2f}")

    # Check variance
    scores = [r['score'] for r in results]
    import numpy as np
    variance = np.var(scores)
    print(f"\n📊 Score Variance: {variance:.2f}")

    if variance < 10:
        print("⚠️  WARNING: Scores too similar! Momentum agent may not be working correctly.")
    else:
        print("✅ Good variance - momentum agent is differentiating stocks")

if __name__ == "__main__":
    test_momentum_agent()
