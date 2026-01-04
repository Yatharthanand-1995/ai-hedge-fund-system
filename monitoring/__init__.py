"""
Intelligent Signal Monitoring System

Hybrid monitoring approach that:
1. Tracks portfolio positions every 30 minutes (critical)
2. Monitors hot watchlist every 2 hours (important)
3. Full scan daily at 4 PM (comprehensive)
4. Event-triggered on price spikes (reactive)

Reduces API calls by 80% while maintaining responsiveness.
"""

from .signal_history import SignalHistory
from .intelligent_monitor import IntelligentSignalMonitor

__all__ = ['SignalHistory', 'IntelligentSignalMonitor']
