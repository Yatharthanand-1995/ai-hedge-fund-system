"""
Portfolio Lock Manager - Cross-process file locking for portfolio operations.

This module provides process-safe locking mechanisms to prevent concurrent
modifications to the portfolio.json file from multiple processes.

Uses fcntl-based file locking (Unix/Mac only) for cross-process safety.
"""

import fcntl
import time
import logging
from pathlib import Path
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class PortfolioLockManager:
    """
    Cross-process file locking using fcntl.

    Prevents concurrent writes to portfolio.json from multiple processes
    (monitoring scheduler, trading scheduler, API endpoints).
    """

    def __init__(self, lock_file: str = "data/paper_portfolio.lock"):
        """
        Initialize portfolio lock manager.

        Args:
            lock_file: Path to lock file (default: data/paper_portfolio.lock)
        """
        self.lock_file = Path(lock_file)

        # Ensure directory exists
        self.lock_file.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def acquire_lock(self, operation: str, timeout: float = 10.0):
        """
        Acquire exclusive lock on portfolio file.

        Args:
            operation: Operation name (for logging)
            timeout: Max seconds to wait for lock (default: 10.0)

        Raises:
            TimeoutError: If lock cannot be acquired within timeout

        Example:
            ```python
            with lock_manager.acquire_lock("buy_AAPL"):
                # Critical section - execute portfolio modification
                self.cash -= total_cost
                self.positions[symbol] = {...}
                self._save_portfolio()
            ```
        """
        lock_fd = None
        start_time = time.time()

        try:
            # Open/create lock file
            lock_fd = open(self.lock_file, 'w')

            # Try to acquire exclusive lock with timeout
            while True:
                try:
                    # LOCK_EX = exclusive lock, LOCK_NB = non-blocking
                    fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    logger.debug(f"🔒 Lock acquired for {operation}")
                    break
                except BlockingIOError:
                    elapsed = time.time() - start_time
                    if elapsed > timeout:
                        raise TimeoutError(
                            f"Could not acquire portfolio lock for {operation} after {timeout}s. "
                            f"Another process may be holding the lock."
                        )
                    # Wait a bit before retrying
                    time.sleep(0.1)

            # Lock acquired, yield control to critical section
            yield

        except TimeoutError:
            # Re-raise timeout errors
            logger.error(
                f"❌ Lock timeout for {operation} after {timeout}s. "
                f"Check for deadlocks or long-running operations."
            )
            raise

        except Exception as e:
            # Log unexpected errors
            logger.error(f"❌ Unexpected error acquiring lock for {operation}: {e}")
            raise

        finally:
            # Always release lock, even if exception occurred
            if lock_fd:
                try:
                    fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)
                    lock_fd.close()
                    logger.debug(f"🔓 Lock released for {operation}")
                except Exception as e:
                    logger.warning(f"⚠️  Error releasing lock for {operation}: {e}")

    @contextmanager
    def acquire_lock_with_retry(self, operation: str, timeout: float = 10.0,
                                max_retries: int = 3, retry_delay: float = 1.0):
        """
        Acquire lock with automatic retry on timeout.

        Useful for non-critical operations that can be retried.

        Args:
            operation: Operation name (for logging)
            timeout: Max seconds to wait for lock per attempt
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds

        Raises:
            TimeoutError: If all retries exhausted
        """
        last_error = None

        for attempt in range(1, max_retries + 1):
            try:
                with self.acquire_lock(operation, timeout=timeout):
                    yield
                    return  # Success

            except TimeoutError as e:
                last_error = e
                if attempt < max_retries:
                    logger.warning(
                        f"⚠️  Lock timeout for {operation} (attempt {attempt}/{max_retries}), "
                        f"retrying in {retry_delay}s..."
                    )
                    time.sleep(retry_delay)
                else:
                    logger.error(
                        f"❌ Lock timeout for {operation} after {max_retries} attempts"
                    )

        # All retries exhausted
        raise last_error

    def is_locked(self) -> bool:
        """
        Check if portfolio is currently locked by another process.

        Returns:
            True if locked, False if available

        Note:
            This is a best-effort check and may have race conditions.
            Always use acquire_lock() for actual locking.
        """
        lock_fd = None

        try:
            lock_fd = open(self.lock_file, 'w')

            # Try to acquire lock without blocking
            fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

            # Lock acquired successfully - file is not locked
            fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)
            return False

        except BlockingIOError:
            # Could not acquire lock - file is locked
            return True

        except Exception as e:
            logger.warning(f"⚠️  Error checking lock status: {e}")
            return False

        finally:
            if lock_fd:
                try:
                    lock_fd.close()
                except Exception:
                    pass
