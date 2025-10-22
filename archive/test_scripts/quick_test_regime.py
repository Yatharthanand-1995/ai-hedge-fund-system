"""
Quick Test for Market Regime Detection
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from core.market_regime_service import MarketRegimeService

# Initialize regime service
regime_service = MarketRegimeService()

# Get current market regime
print("\n🔍 Detecting current market regime...")
regime_info = regime_service.get_current_regime(force_refresh=True)

print(f"\n📊 Market Regime: {regime_info['regime']}")
print(f"   Trend: {regime_info['trend']}")
print(f"   Volatility: {regime_info['volatility']}")

print(f"\n⚙️  Adaptive Weights:")
weights = regime_info['weights']
for agent, weight in weights.items():
    print(f"   {agent.capitalize()}: {weight*100:.0f}%")

explanation = regime_service.get_regime_explanation(regime_info['regime'])
print(f"\n💡 {explanation}\n")
