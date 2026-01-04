"""
Signal History Database

Tracks all signal changes over time for analysis and decision-making.
Stores both current signals and historical changes.
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class SignalChange:
    """Represents a single signal change event."""

    def __init__(
        self,
        symbol: str,
        timestamp: datetime,
        previous_signal: Optional[str],
        new_signal: str,
        previous_score: Optional[float],
        new_score: float,
        change_type: str,
        urgency: str,
        action_taken: Optional[str] = None,
        reason: Optional[str] = None
    ):
        self.symbol = symbol
        self.timestamp = timestamp
        self.previous_signal = previous_signal
        self.new_signal = new_signal
        self.previous_score = previous_score
        self.new_score = new_score
        self.change_type = change_type
        self.urgency = urgency
        self.action_taken = action_taken
        self.reason = reason

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'symbol': self.symbol,
            'timestamp': self.timestamp.isoformat(),
            'previous_signal': self.previous_signal,
            'new_signal': self.new_signal,
            'previous_score': self.previous_score,
            'new_score': self.new_score,
            'score_change': round(self.new_score - (self.previous_score or 0), 2),
            'change_type': self.change_type,
            'urgency': self.urgency,
            'action_taken': self.action_taken,
            'reason': self.reason
        }


class SignalHistory:
    """
    Manages signal history database.

    Tracks:
    1. Current signals for all monitored stocks
    2. Historical signal changes
    3. Last check times for smart caching
    """

    def __init__(self, history_file: str = "data/monitoring/signal_history.json"):
        self.history_file = Path(history_file)
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

        # Load or initialize data
        self.data = self._load_history()

    def _load_history(self) -> Dict:
        """Load signal history from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    logger.info(f"Loaded signal history: {len(data.get('current_signals', {}))} stocks tracked")
                    return data
            except Exception as e:
                logger.error(f"Failed to load signal history: {e}")
                return self._initialize_empty_history()
        else:
            return self._initialize_empty_history()

    def _initialize_empty_history(self) -> Dict:
        """Initialize empty history structure."""
        return {
            'current_signals': {},  # {symbol: {signal, score, last_updated, confidence}}
            'signal_changes': [],   # List of all signal change events
            'last_checks': {},      # {symbol: last_check_timestamp} for smart caching
            'metadata': {
                'created_at': datetime.now(timezone.utc).isoformat(),
                'total_changes_logged': 0,
                'version': '2.0'
            }
        }

    def _save_history(self):
        """Save signal history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save signal history: {e}")

    def get_current_signal(self, symbol: str) -> Optional[Dict]:
        """Get current signal for a symbol."""
        return self.data['current_signals'].get(symbol)

    def get_last_check_time(self, symbol: str) -> Optional[datetime]:
        """Get last time a symbol was checked."""
        timestamp_str = self.data['last_checks'].get(symbol)
        if timestamp_str:
            return datetime.fromisoformat(timestamp_str)
        return None

    def update_signal(
        self,
        symbol: str,
        signal: str,
        score: float,
        confidence: str,
        agent_scores: Optional[Dict] = None
    ) -> Optional[SignalChange]:
        """
        Update signal for a symbol and detect changes.

        Returns:
            SignalChange object if signal changed, None otherwise
        """
        current = self.get_current_signal(symbol)
        now = datetime.now(timezone.utc)

        # Determine if this is a meaningful change
        signal_changed = False
        change_type = None
        urgency = None

        if current is None:
            # First time seeing this symbol
            signal_changed = True
            change_type = 'NEW'
            urgency = 'LOW'
        else:
            # Check for signal or significant score change
            if current['signal'] != signal:
                signal_changed = True
                change_type = self._classify_change(current['signal'], signal)
                urgency = self._determine_urgency(change_type, current['score'], score)
            elif abs(current['score'] - score) >= 3.0:
                # Score changed by >= 3 points (meaningful but same signal)
                signal_changed = True
                change_type = 'SCORE_CHANGE'
                urgency = 'LOW'

        # Update current signal
        self.data['current_signals'][symbol] = {
            'signal': signal,
            'score': score,
            'confidence': confidence,
            'last_updated': now.isoformat(),
            'agent_scores': agent_scores or {}
        }

        # Update last check time
        self.data['last_checks'][symbol] = now.isoformat()

        # Log change if meaningful
        signal_change_obj = None
        if signal_changed:
            signal_change_obj = SignalChange(
                symbol=symbol,
                timestamp=now,
                previous_signal=current['signal'] if current else None,
                new_signal=signal,
                previous_score=current['score'] if current else None,
                new_score=score,
                change_type=change_type,
                urgency=urgency,
                reason=self._generate_reason(change_type, current, score)
            )

            # Add to change log
            self.data['signal_changes'].append(signal_change_obj.to_dict())
            self.data['metadata']['total_changes_logged'] += 1

            logger.info(f"📊 Signal change detected: {symbol} {current['signal'] if current else 'NEW'} → {signal} (score: {score:.1f}, urgency: {urgency})")

        # Save to disk
        self._save_history()

        return signal_change_obj

    def _classify_change(self, old_signal: str, new_signal: str) -> str:
        """Classify type of signal change."""
        signal_order = {
            'SELL': 0,
            'WEAK SELL': 1,
            'HOLD': 2,
            'WEAK BUY': 3,
            'BUY': 4,
            'STRONG BUY': 5
        }

        old_rank = signal_order.get(old_signal, 2)
        new_rank = signal_order.get(new_signal, 2)

        if new_rank > old_rank:
            if new_rank - old_rank >= 3:
                return 'MAJOR_UPGRADE'
            return 'UPGRADE'
        elif new_rank < old_rank:
            # Downgrades are critical
            if old_rank >= 4 and new_rank <= 1:  # STRONG BUY/BUY → SELL/WEAK SELL
                return 'CRITICAL_DOWNGRADE'
            elif new_rank - old_rank <= -2:
                return 'MAJOR_DOWNGRADE'
            return 'DOWNGRADE'
        else:
            return 'NO_CHANGE'

    def _determine_urgency(self, change_type: str, old_score: float, new_score: float) -> str:
        """Determine urgency level for a signal change."""
        if change_type == 'CRITICAL_DOWNGRADE':
            return 'CRITICAL'  # Sell immediately
        elif change_type == 'MAJOR_DOWNGRADE':
            return 'HIGH'  # Sell soon
        elif change_type == 'DOWNGRADE':
            return 'MEDIUM'  # Monitor closely
        elif change_type in ['MAJOR_UPGRADE', 'UPGRADE']:
            # Only urgent if score is very high
            if new_score >= 75:
                return 'MEDIUM'  # Consider buying
            return 'LOW'
        else:
            return 'LOW'

    def _generate_reason(self, change_type: str, previous: Optional[Dict], new_score: float) -> str:
        """Generate human-readable reason for change."""
        if previous is None:
            return "First analysis of this stock"

        score_diff = new_score - previous['score']
        if change_type == 'CRITICAL_DOWNGRADE':
            return f"Critical deterioration: score dropped {abs(score_diff):.1f} points"
        elif change_type == 'MAJOR_DOWNGRADE':
            return f"Significant weakness: score dropped {abs(score_diff):.1f} points"
        elif change_type == 'DOWNGRADE':
            return f"Signal weakened: score dropped {abs(score_diff):.1f} points"
        elif change_type == 'MAJOR_UPGRADE':
            return f"Strong improvement: score increased {score_diff:.1f} points"
        elif change_type == 'UPGRADE':
            return f"Signal strengthened: score increased {score_diff:.1f} points"
        elif change_type == 'SCORE_CHANGE':
            direction = "increased" if score_diff > 0 else "decreased"
            return f"Score {direction} {abs(score_diff):.1f} points"
        else:
            return "No significant change"

    def get_changes_since(self, since: datetime, symbol: Optional[str] = None) -> List[Dict]:
        """Get signal changes since a specific time."""
        changes = []
        for change in self.data['signal_changes']:
            change_time = datetime.fromisoformat(change['timestamp'])
            if change_time >= since:
                if symbol is None or change['symbol'] == symbol:
                    changes.append(change)
        return changes

    def get_changes_for_symbol(self, symbol: str, limit: int = 10) -> List[Dict]:
        """Get recent changes for a specific symbol."""
        symbol_changes = [
            change for change in self.data['signal_changes']
            if change['symbol'] == symbol
        ]
        # Return most recent first
        return sorted(symbol_changes, key=lambda x: x['timestamp'], reverse=True)[:limit]

    def get_statistics(self) -> Dict:
        """Get signal history statistics."""
        changes = self.data['signal_changes']

        # Count by urgency
        urgency_counts = {}
        for change in changes:
            urgency = change['urgency']
            urgency_counts[urgency] = urgency_counts.get(urgency, 0) + 1

        # Count by change type
        type_counts = {}
        for change in changes:
            change_type = change['change_type']
            type_counts[change_type] = type_counts.get(change_type, 0) + 1

        return {
            'total_stocks_tracked': len(self.data['current_signals']),
            'total_changes_logged': len(changes),
            'urgency_breakdown': urgency_counts,
            'change_type_breakdown': type_counts,
            'last_updated': self.data['metadata'].get('created_at')
        }

    def clear_old_changes(self, days_to_keep: int = 30):
        """Remove signal changes older than specified days."""
        cutoff = datetime.now(timezone.utc).timestamp() - (days_to_keep * 86400)

        original_count = len(self.data['signal_changes'])
        self.data['signal_changes'] = [
            change for change in self.data['signal_changes']
            if datetime.fromisoformat(change['timestamp']).timestamp() > cutoff
        ]

        removed = original_count - len(self.data['signal_changes'])
        if removed > 0:
            logger.info(f"Cleaned up {removed} old signal changes (kept last {days_to_keep} days)")
            self._save_history()
