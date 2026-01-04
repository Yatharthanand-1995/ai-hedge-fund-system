"""
Buy Queue Manager - Thread-safe and process-safe buy opportunity queue.

This module provides persistent queue management for buy opportunities detected
during market hours, to be executed at 4 PM batch execution.

Features:
- Atomic writes using temp files
- fcntl-based file locking for cross-process safety
- Re-validation at execution time
- Automatic cleanup of stale entries (>24 hours)
"""

import fcntl
import json
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class BuyQueueManager:
    """
    Thread-safe and process-safe buy queue with file locking.

    Manages a persistent queue of buy opportunities that are detected
    during market hours and executed at 4 PM batch execution.
    """

    def __init__(self, queue_file: str = "data/buy_queue.json"):
        """
        Initialize buy queue manager.

        Args:
            queue_file: Path to queue file (default: data/buy_queue.json)
        """
        self.queue_file = Path(queue_file)
        self.lock_file = Path(str(queue_file) + ".lock")

        # Ensure directory exists
        self.queue_file.parent.mkdir(parents=True, exist_ok=True)

        # Initialize queue file if it doesn't exist
        if not self.queue_file.exists():
            self._initialize_queue_file()

    def _initialize_queue_file(self):
        """Initialize empty queue file."""
        data = {
            "queued_opportunities": [],
            "metadata": {
                "created_at": datetime.utcnow().isoformat() + "Z",
                "last_modified": datetime.utcnow().isoformat() + "Z"
            }
        }
        self._atomic_write(data)
        logger.info(f"✅ Initialized buy queue file: {self.queue_file}")

    @contextmanager
    def _acquire_lock(self, operation: str, timeout: float = 10.0):
        """
        Acquire exclusive lock on queue file.

        Args:
            operation: Operation name (for logging)
            timeout: Max seconds to wait for lock

        Raises:
            TimeoutError: If lock cannot be acquired within timeout
        """
        lock_fd = None
        start_time = time.time()

        try:
            # Open/create lock file
            lock_fd = open(self.lock_file, 'w')

            # Try to acquire exclusive lock with timeout
            while True:
                try:
                    fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    logger.debug(f"🔒 Lock acquired for {operation}")
                    break
                except BlockingIOError:
                    if time.time() - start_time > timeout:
                        raise TimeoutError(
                            f"Could not acquire lock for {operation} after {timeout}s"
                        )
                    time.sleep(0.1)

            yield  # Execute critical section

        finally:
            if lock_fd:
                try:
                    fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)
                    lock_fd.close()
                    logger.debug(f"🔓 Lock released for {operation}")
                except Exception as e:
                    logger.warning(f"Error releasing lock: {e}")

    def _atomic_write(self, data: Dict):
        """
        Write data to queue file atomically using temp file + rename.

        Args:
            data: Data to write to queue file
        """
        temp_file = Path(str(self.queue_file) + '.tmp')

        try:
            # Write to temp file
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2)

            # Atomic rename (overwrites existing file)
            temp_file.replace(self.queue_file)

        except Exception as e:
            # Clean up temp file on error
            if temp_file.exists():
                temp_file.unlink()
            raise

    def _load_queue(self) -> Dict:
        """
        Load queue data from file.

        Returns:
            Queue data dictionary
        """
        try:
            with open(self.queue_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Error loading queue file: {e}, reinitializing")
            self._initialize_queue_file()
            return {
                "queued_opportunities": [],
                "metadata": {
                    "created_at": datetime.utcnow().isoformat() + "Z",
                    "last_modified": datetime.utcnow().isoformat() + "Z"
                }
            }

    def _cleanup_stale_entries(self, opportunities: List[Dict], max_age_hours: int = 24) -> List[Dict]:
        """
        Remove stale entries older than max_age_hours.

        Args:
            opportunities: List of opportunity dictionaries
            max_age_hours: Maximum age in hours (default: 24)

        Returns:
            Filtered list without stale entries
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        filtered = []
        stale_count = 0

        for opp in opportunities:
            try:
                queued_at = datetime.fromisoformat(opp['queued_at'].replace('Z', '+00:00'))
                if queued_at.replace(tzinfo=None) > cutoff_time:
                    filtered.append(opp)
                else:
                    stale_count += 1
            except (KeyError, ValueError) as e:
                logger.warning(f"Invalid opportunity entry: {e}, skipping")
                stale_count += 1

        if stale_count > 0:
            logger.info(f"🧹 Removed {stale_count} stale entries (>{max_age_hours}h old)")

        return filtered

    def enqueue(self, symbol: str, score: float, signal: str,
                price: Optional[float] = None, reason: str = "") -> bool:
        """
        Add buy opportunity to queue with file locking.

        Args:
            symbol: Stock symbol (e.g., "AAPL")
            score: Composite score (0-100)
            signal: Signal type (e.g., "STRONG BUY")
            price: Current price (optional, will be fetched at execution)
            reason: Reason for buy signal

        Returns:
            True if successfully enqueued, False otherwise
        """
        try:
            with self._acquire_lock(f"enqueue_{symbol}"):
                # Load current queue
                data = self._load_queue()
                opportunities = data.get('queued_opportunities', [])

                # Clean up stale entries
                opportunities = self._cleanup_stale_entries(opportunities)

                # Check if symbol already queued
                existing_symbols = {opp['symbol'] for opp in opportunities}
                if symbol in existing_symbols:
                    logger.info(f"⏭️  {symbol} already queued, skipping duplicate")
                    return False

                # Add new opportunity
                opportunity = {
                    'symbol': symbol,
                    'queued_at': datetime.utcnow().isoformat() + 'Z',
                    'signal': signal,
                    'score': score,
                    'price': price,
                    'reason': reason
                }
                opportunities.append(opportunity)

                # Update metadata
                data['queued_opportunities'] = opportunities
                data['metadata']['last_modified'] = datetime.utcnow().isoformat() + 'Z'

                # Atomic write
                self._atomic_write(data)

                logger.info(f"✅ Queued {symbol} for 4 PM execution (score: {score:.1f}, signal: {signal})")
                return True

        except Exception as e:
            logger.error(f"❌ Error enqueueing {symbol}: {e}")
            return False

    def dequeue_all(self) -> List[Dict]:
        """
        Get all queued opportunities and clear queue atomically.

        Returns:
            List of opportunity dictionaries
        """
        try:
            with self._acquire_lock("dequeue_all"):
                # Load current queue
                data = self._load_queue()
                opportunities = data.get('queued_opportunities', [])

                # Clean up stale entries before returning
                opportunities = self._cleanup_stale_entries(opportunities)

                if not opportunities:
                    logger.info("📋 Buy queue is empty")
                    return []

                logger.info(f"📋 Dequeuing {len(opportunities)} opportunities")

                # Clear queue
                data['queued_opportunities'] = []
                data['metadata']['last_modified'] = datetime.utcnow().isoformat() + 'Z'

                # Atomic write
                self._atomic_write(data)

                return opportunities

        except Exception as e:
            logger.error(f"❌ Error dequeuing opportunities: {e}")
            return []

    def peek(self) -> List[Dict]:
        """
        View queued opportunities without removing them.

        Returns:
            List of opportunity dictionaries
        """
        try:
            with self._acquire_lock("peek"):
                data = self._load_queue()
                opportunities = data.get('queued_opportunities', [])
                opportunities = self._cleanup_stale_entries(opportunities)
                return opportunities

        except Exception as e:
            logger.error(f"❌ Error peeking queue: {e}")
            return []

    def validate_and_filter(self, opportunities: List[Dict],
                           current_analyses: Dict[str, Dict]) -> List[Dict]:
        """
        Re-validate queued opportunities before execution.

        Filters out opportunities where:
        - Score has dropped significantly (>10 points)
        - Signal has downgraded
        - Stock is no longer a strong buy

        Args:
            opportunities: List of queued opportunities
            current_analyses: Dict mapping symbol -> current analysis result

        Returns:
            Filtered list of still-valid opportunities
        """
        valid = []
        rejected = []

        for opp in opportunities:
            symbol = opp['symbol']
            queued_score = opp['score']
            queued_signal = opp['signal']

            # Check if we have current analysis
            if symbol not in current_analyses:
                logger.warning(f"⚠️  No current analysis for {symbol}, rejecting")
                rejected.append(f"{symbol} (no data)")
                continue

            current = current_analyses[symbol]
            current_score = current.get('composite_score', 0)
            current_signal = current.get('recommendation', 'HOLD')

            # Validate score hasn't dropped significantly
            score_drop = queued_score - current_score
            if score_drop > 10:
                logger.warning(
                    f"⚠️  {symbol} score dropped {score_drop:.1f} points "
                    f"({queued_score:.1f} → {current_score:.1f}), rejecting"
                )
                rejected.append(f"{symbol} (score drop)")
                continue

            # Validate signal hasn't downgraded
            if current_signal not in ['STRONG BUY', 'BUY']:
                logger.warning(
                    f"⚠️  {symbol} signal downgraded to {current_signal}, rejecting"
                )
                rejected.append(f"{symbol} (downgrade)")
                continue

            # Opportunity is still valid
            valid.append(opp)
            logger.info(
                f"✅ {symbol} validated (score: {queued_score:.1f} → {current_score:.1f}, "
                f"signal: {queued_signal} → {current_signal})"
            )

        if rejected:
            logger.info(f"❌ Rejected {len(rejected)} stale opportunities: {', '.join(rejected)}")

        return valid

    def clear(self) -> bool:
        """
        Clear all queued opportunities.

        Returns:
            True if successfully cleared, False otherwise
        """
        try:
            with self._acquire_lock("clear"):
                data = self._load_queue()
                count = len(data.get('queued_opportunities', []))

                data['queued_opportunities'] = []
                data['metadata']['last_modified'] = datetime.utcnow().isoformat() + 'Z'

                self._atomic_write(data)

                logger.info(f"🧹 Cleared {count} opportunities from queue")
                return True

        except Exception as e:
            logger.error(f"❌ Error clearing queue: {e}")
            return False
