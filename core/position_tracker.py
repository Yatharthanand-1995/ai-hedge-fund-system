"""
Position Tracker for Enhanced Transaction Logging
Tracks position entry/exit details, reasons, and recovery metrics
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class PositionEntry:
    """Detailed position entry information"""
    symbol: str
    entry_date: str
    entry_price: float
    shares: float
    entry_value: float
    agent_score: float
    rank: int  # Ranking when bought (1 = top stock)

    # Regime context at entry
    market_regime: Optional[str] = None
    portfolio_size_at_entry: Optional[int] = None

    # Tracking
    max_price_while_held: float = 0.0
    min_price_while_held: float = float('inf')
    max_gain_pct: float = 0.0
    max_loss_pct: float = 0.0


@dataclass
class ExitDetails:
    """Detailed exit reason and metrics"""
    exit_reason: str  # STOP_LOSS, REGIME_REDUCTION, SCORE_DROPPED, REBALANCE

    # Price metrics
    entry_price: float
    exit_price: float
    loss_pct: float
    holding_period_days: int
    max_price_while_held: float
    max_gain_pct: float

    # Context-specific details
    stop_loss_triggered: bool = False
    stop_loss_threshold: float = -0.20  # -20%

    # For regime-driven sells
    regime_change: Optional[str] = None
    portfolio_size_before: Optional[int] = None
    portfolio_size_after: Optional[int] = None

    # For score-driven sells
    score_when_bought: Optional[float] = None
    score_when_sold: Optional[float] = None
    score_dropped_by: Optional[float] = None
    rank_when_bought: Optional[int] = None
    rank_when_sold: Optional[int] = None

    # Recovery tracking (to be filled later)
    recovery_tracked: bool = True
    recovery_period_days: int = 90
    recovered_to_entry: bool = False
    max_price_after_exit: Optional[float] = None
    recovery_date: Optional[str] = None


@dataclass
class StoppedPosition:
    """Position that was stopped out - tracked for recovery analysis"""
    symbol: str
    exit_date: str
    entry_price: float
    exit_price: float
    exit_reason: str
    stop_loss_pct: float

    # Recovery tracking
    days_to_track: int = 90
    track_until_date: str = None
    recovered: bool = False
    recovery_date: Optional[str] = None
    max_price_after_exit: float = 0.0


class PositionTracker:
    """
    Tracks all positions with detailed entry/exit information
    """

    def __init__(self):
        self.active_positions: Dict[str, PositionEntry] = {}
        self.stopped_positions: List[StoppedPosition] = []
        self.all_exits: List[Dict] = []

        # Statistics
        self.stop_loss_count = 0
        self.regime_reduction_count = 0
        self.score_dropped_count = 0
        self.normal_rebalance_count = 0

    def add_position(
        self,
        symbol: str,
        entry_date: str,
        entry_price: float,
        shares: float,
        agent_score: float,
        rank: int,
        market_regime: Optional[str] = None,
        portfolio_size: Optional[int] = None
    ):
        """Record a new position entry"""
        position = PositionEntry(
            symbol=symbol,
            entry_date=entry_date,
            entry_price=entry_price,
            shares=shares,
            entry_value=shares * entry_price,
            agent_score=agent_score,
            rank=rank,
            market_regime=market_regime,
            portfolio_size_at_entry=portfolio_size,
            max_price_while_held=entry_price,
            min_price_while_held=entry_price
        )

        self.active_positions[symbol] = position
        logger.debug(f"Tracked position entry: {symbol} @ ${entry_price:.2f}, rank #{rank}")

    def update_price_tracking(self, symbol: str, current_price: float):
        """Update max/min prices while held"""
        if symbol not in self.active_positions:
            return

        position = self.active_positions[symbol]

        # Update max price
        if current_price > position.max_price_while_held:
            position.max_price_while_held = current_price
            gain_pct = (current_price - position.entry_price) / position.entry_price
            position.max_gain_pct = max(position.max_gain_pct, gain_pct)

        # Update min price
        if current_price < position.min_price_while_held:
            position.min_price_while_held = current_price
            loss_pct = (current_price - position.entry_price) / position.entry_price
            position.max_loss_pct = min(position.max_loss_pct, loss_pct)

    def exit_position(
        self,
        symbol: str,
        exit_date: str,
        exit_price: float,
        exit_reason: str,
        current_scores: Optional[Dict[str, float]] = None,
        regime_change: Optional[str] = None,
        portfolio_size_before: Optional[int] = None,
        portfolio_size_after: Optional[int] = None
    ) -> ExitDetails:
        """
        Record position exit with detailed reason and metrics

        Args:
            symbol: Stock symbol
            exit_date: Exit date
            exit_price: Exit price
            exit_reason: One of: STOP_LOSS, REGIME_REDUCTION, SCORE_DROPPED, REBALANCE
            current_scores: Dict of symbol -> current score (for SCORE_DROPPED)
            regime_change: e.g., "BULL -> BEAR"
            portfolio_size_before/after: For regime reductions
        """
        if symbol not in self.active_positions:
            # Position not tracked, create minimal exit details
            return ExitDetails(
                exit_reason=exit_reason,
                entry_price=exit_price,  # Unknown
                exit_price=exit_price,
                loss_pct=0.0,
                holding_period_days=0,
                max_price_while_held=exit_price,
                max_gain_pct=0.0,
                stop_loss_triggered=(exit_reason == "STOP_LOSS")
            )

        position = self.active_positions[symbol]

        # Calculate holding period
        entry_dt = datetime.strptime(position.entry_date, '%Y-%m-%d')
        exit_dt = datetime.strptime(exit_date, '%Y-%m-%d')
        holding_days = (exit_dt - entry_dt).days

        # Calculate loss
        loss_pct = (exit_price - position.entry_price) / position.entry_price

        # Build exit details
        exit_details = ExitDetails(
            exit_reason=exit_reason,
            entry_price=position.entry_price,
            exit_price=exit_price,
            loss_pct=loss_pct,
            holding_period_days=holding_days,
            max_price_while_held=position.max_price_while_held,
            max_gain_pct=position.max_gain_pct,
            stop_loss_triggered=(exit_reason == "STOP_LOSS")
        )

        # Add context-specific details
        if exit_reason == "REGIME_REDUCTION":
            exit_details.regime_change = regime_change
            exit_details.portfolio_size_before = portfolio_size_before
            exit_details.portfolio_size_after = portfolio_size_after
            self.regime_reduction_count += 1

        elif exit_reason == "SCORE_DROPPED":
            exit_details.score_when_bought = position.agent_score
            exit_details.rank_when_bought = position.rank

            if current_scores and symbol in current_scores:
                exit_details.score_when_sold = current_scores[symbol]
                exit_details.score_dropped_by = current_scores[symbol] - position.agent_score

                # Calculate current rank
                sorted_scores = sorted(current_scores.items(), key=lambda x: x[1], reverse=True)
                try:
                    rank = next(i for i, (s, _) in enumerate(sorted_scores, 1) if s == symbol)
                    exit_details.rank_when_sold = rank
                except StopIteration:
                    exit_details.rank_when_sold = len(sorted_scores) + 1

            self.score_dropped_count += 1

        elif exit_reason == "STOP_LOSS":
            self.stop_loss_count += 1

            # Track for recovery analysis
            track_until = (exit_dt + timedelta(days=90)).strftime('%Y-%m-%d')
            stopped_pos = StoppedPosition(
                symbol=symbol,
                exit_date=exit_date,
                entry_price=position.entry_price,
                exit_price=exit_price,
                exit_reason=exit_reason,
                stop_loss_pct=loss_pct,
                days_to_track=90,
                track_until_date=track_until,
                max_price_after_exit=exit_price
            )
            self.stopped_positions.append(stopped_pos)

            # Check if stop-loss executed late
            if loss_pct < -0.25:  # More than -25%
                logger.warning(
                    f"⚠️  LATE STOP-LOSS: {symbol} lost {loss_pct*100:.1f}% "
                    f"(threshold: -20%). Entry: ${position.entry_price:.2f}, "
                    f"Exit: ${exit_price:.2f}"
                )

        elif exit_reason == "REBALANCE":
            self.normal_rebalance_count += 1

        # Record exit
        self.all_exits.append({
            'symbol': symbol,
            'exit_date': exit_date,
            'exit_details': exit_details
        })

        # Remove from active positions
        del self.active_positions[symbol]

        logger.info(
            f"Tracked position exit: {symbol} - {exit_reason} | "
            f"Held {holding_days} days | P&L: {loss_pct*100:+.1f}%"
        )

        return exit_details

    def update_recovery_tracking(self, symbol: str, date: str, price: float):
        """Update recovery tracking for stopped positions"""
        for stopped in self.stopped_positions:
            if stopped.symbol != symbol:
                continue

            if stopped.recovered:
                continue  # Already recovered

            # Check if still in tracking window
            if date > stopped.track_until_date:
                continue

            # Update max price after exit
            if price > stopped.max_price_after_exit:
                stopped.max_price_after_exit = price

            # Check if recovered to entry price
            if price >= stopped.entry_price and not stopped.recovered:
                stopped.recovered = True
                stopped.recovery_date = date

                days_to_recovery = (
                    datetime.strptime(date, '%Y-%m-%d') -
                    datetime.strptime(stopped.exit_date, '%Y-%m-%d')
                ).days

                logger.info(
                    f"💚 RECOVERY: {symbol} recovered to entry price "
                    f"${stopped.entry_price:.2f} in {days_to_recovery} days "
                    f"(stopped at ${stopped.exit_price:.2f})"
                )

    def get_statistics(self) -> Dict:
        """Get comprehensive tracking statistics"""
        total_exits = len(self.all_exits)

        # Recovery analysis
        stopped_tracked = [s for s in self.stopped_positions]
        total_stopped = len(stopped_tracked)
        recovered = sum(1 for s in stopped_tracked if s.recovered)
        recovery_rate = recovered / total_stopped if total_stopped > 0 else 0

        # False positive analysis (positions that recovered quickly)
        false_positives = sum(
            1 for s in stopped_tracked
            if s.recovered and s.recovery_date and
            (datetime.strptime(s.recovery_date, '%Y-%m-%d') -
             datetime.strptime(s.exit_date, '%Y-%m-%d')).days <= 30
        )

        return {
            'total_exits': total_exits,
            'stop_loss_exits': self.stop_loss_count,
            'regime_reduction_exits': self.regime_reduction_count,
            'score_dropped_exits': self.score_dropped_count,
            'normal_rebalance_exits': self.normal_rebalance_count,
            'recovery_tracking': {
                'total_stopped_positions': total_stopped,
                'recovered_to_entry': recovered,
                'recovery_rate': recovery_rate,
                'false_positives_30days': false_positives
            }
        }

    def get_late_stop_losses(self) -> List[Dict]:
        """Get positions where stop-loss executed beyond threshold"""
        late_stops = []

        for exit_record in self.all_exits:
            details = exit_record['exit_details']
            if details.exit_reason == "STOP_LOSS" and details.loss_pct < -0.25:
                late_stops.append({
                    'symbol': exit_record['symbol'],
                    'date': exit_record['exit_date'],
                    'entry_price': details.entry_price,
                    'exit_price': details.exit_price,
                    'loss_pct': details.loss_pct,
                    'expected_threshold': -0.20,
                    'excess_loss': details.loss_pct - (-0.20)
                })

        return late_stops

    def can_rebuy_stopped_position(
        self,
        symbol: str,
        fundamentals_score: float,
        date: str
    ) -> bool:
        """
        ANALYTICAL FIX #2: Re-Entry Logic
        Check if a previously stopped position can be re-bought.

        Rules:
        - Allow re-buying if fundamentals score > 65 (strong fundamentals recovered)
        - Stock must have been stopped out previously
        - Must still be within tracking window (90 days)

        Args:
            symbol: Stock symbol to check
            fundamentals_score: Current fundamentals score (0-100)
            date: Current date

        Returns:
            True if eligible for re-entry, False otherwise
        """
        # Check if this symbol was ever stopped
        stopped_records = [s for s in self.stopped_positions if s.symbol == symbol]

        if not stopped_records:
            return True  # Never stopped, OK to buy

        # Get most recent stop
        most_recent_stop = max(stopped_records, key=lambda s: s.exit_date)

        # Check if within tracking window
        if date > most_recent_stop.track_until_date:
            # Outside tracking window, OK to rebuy
            return True

        # ANALYTICAL FIX #2: Allow re-entry if fundamentals are strong (> 65)
        if fundamentals_score > 65:
            logger.info(
                f"✅ RE-ENTRY ELIGIBLE: {symbol} (F={fundamentals_score:.0f} > 65) - "
                f"Stopped on {most_recent_stop.exit_date}, fundamentals recovered"
            )
            return True

        # Still within tracking window, fundamentals not strong enough
        logger.debug(
            f"🚫 RE-ENTRY BLOCKED: {symbol} (F={fundamentals_score:.0f} ≤ 65) - "
            f"Stopped on {most_recent_stop.exit_date}, fundamentals still weak"
        )
        return False
