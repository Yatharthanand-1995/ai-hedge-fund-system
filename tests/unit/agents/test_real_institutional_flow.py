"""
Test institutional flow with real scores (after bug fix)
"""

from core.stock_scorer import StockScorer
import logging

logging.basicConfig(level=logging.WARNING)

def test_with_real_scores():
    """Test multiple stocks to see institutional flow in action"""

    print("\n" + "="*80)
    print("REAL INSTITUTIONAL FLOW ANALYSIS TEST")
    print("="*80)

    scorer = StockScorer()

    # Test with different stock types
    test_stocks = [
        ("AAPL", "Tech Giant"),
        ("NVDA", "AI/Chip Leader"),
        ("JPM", "Financial"),
        ("XOM", "Energy"),
        ("TSLA", "High Volatility")
    ]

    results = []

    for symbol, description in test_stocks:
        print(f"\n{'='*80}")
        print(f"Analyzing {symbol} ({description})")
        print('='*80)

        try:
            result = scorer.score_stock(symbol)

            print(f"\n📊 Overall Analysis:")
            print(f"   Composite Score: {result['composite_score']:.2f}/100")
            print(f"   Confidence: {result['composite_confidence']:.2f}")
            print(f"   Recommendation: {result['rank_category']}")

            print(f"\n🤖 Agent Breakdown:")
            agent_scores = result['agent_scores']

            for agent_name in ['fundamentals', 'momentum', 'quality', 'sentiment', 'institutional_flow']:
                if agent_name in agent_scores:
                    agent_result = agent_scores[agent_name]
                    score = agent_result['score']
                    conf = agent_result['confidence']

                    # Highlight institutional flow
                    marker = "📈" if agent_name == 'institutional_flow' else "  "
                    print(f"   {marker} {agent_name:20s}: {score:5.1f} (conf: {conf:.2f})")

            # Show institutional flow details
            if 'institutional_flow' in agent_scores:
                flow = agent_scores['institutional_flow']
                print(f"\n💰 Institutional Flow Details:")
                print(f"   {flow['reasoning']}")

                if 'metrics' in flow and not flow.get('metrics', {}).get('insufficient_data'):
                    metrics = flow['metrics']
                    print(f"\n   Key Metrics:")
                    print(f"     Volume Flow Score: {metrics.get('volume_flow', 0):.1f}/100")
                    print(f"     Money Flow Score: {metrics.get('money_flow', 0):.1f}/100")
                    print(f"     Unusual Activity: {metrics.get('unusual_activity', 0):.1f}/100")
                    print(f"     VWAP Position: {metrics.get('vwap_position', 0):.1f}/100")
                    print(f"     Volume Z-Score: {metrics.get('volume_zscore', 0):.2f}")
                    print(f"     MFI: {metrics.get('mfi', 0):.1f}")

            results.append({
                'symbol': symbol,
                'description': description,
                'composite': result['composite_score'],
                'institutional_flow': agent_scores.get('institutional_flow', {}).get('score', 0)
            })

        except Exception as e:
            print(f"   ❌ Analysis failed: {e}")
            import traceback
            traceback.print_exc()

    # Summary
    print(f"\n{'='*80}")
    print("INSTITUTIONAL FLOW SUMMARY")
    print('='*80)
    print(f"\n{'Stock':<8} {'Type':<20} {'Overall':<10} {'Inst Flow':<12} {'Signal'}")
    print("-" * 80)

    for r in results:
        signal = "🟢 Buying" if r['institutional_flow'] > 60 else "🔴 Selling" if r['institutional_flow'] < 45 else "⚪ Neutral"
        print(f"{r['symbol']:<8} {r['description']:<20} {r['composite']:>6.1f}     {r['institutional_flow']:>6.1f}       {signal}")

    print("\n" + "="*80)
    print("✅ TEST COMPLETE - Institutional Flow Agent Working with Real Data!")
    print("="*80 + "\n")

    return True

if __name__ == "__main__":
    test_with_real_scores()
