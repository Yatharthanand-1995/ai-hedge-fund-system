#!/usr/bin/env python3
"""Quick test to verify momentum fix"""

import requests
import json

BASE_URL = "http://localhost:8010"

def test_momentum_variance():
    """Test that momentum scores now have variance"""
    print("🔍 TESTING MOMENTUM FIX")
    print("=" * 60)

    test_stocks = ['AAPL', 'GOOGL', 'NVDA']
    results = []

    for symbol in test_stocks:
        try:
            print(f"\n📊 Testing {symbol}...")
            response = requests.post(f"{BASE_URL}/analyze",
                                   json={"symbol": symbol},
                                   timeout=30)

            if response.status_code == 200:
                data = response.json()
                narrative = data.get('narrative', {})
                agent_scores = narrative.get('agent_scores', {})

                momentum_score = agent_scores.get('momentum', 0)
                print(f"   Momentum Score: {momentum_score:.1f}")

                results.append({
                    'symbol': symbol,
                    'momentum': momentum_score
                })
            else:
                print(f"   ❌ Failed: {response.status_code}")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    print("\n📈 MOMENTUM SCORES SUMMARY")
    print("=" * 60)
    for r in results:
        print(f"{r['symbol']:6s}: Momentum = {r['momentum']:.1f}")

    # Check variance
    if len(results) >= 2:
        scores = [r['momentum'] for r in results]
        import numpy as np
        variance = np.var(scores)
        mean = np.mean(scores)

        print(f"\n📊 Statistics:")
        print(f"   Mean: {mean:.1f}")
        print(f"   Variance: {variance:.2f}")

        if variance < 10 and mean == 50.0:
            print("   ❌ STILL BROKEN: All scores are 50.0")
        elif variance < 10:
            print("   ⚠️  WARNING: Low variance, scores too similar")
        else:
            print("   ✅ FIXED: Good variance in momentum scores!")

if __name__ == "__main__":
    test_momentum_variance()
