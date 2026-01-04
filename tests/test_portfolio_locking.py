"""
Portfolio Locking Stress Tests

Tests the PortfolioLockManager under concurrent access scenarios to ensure:
1. No race conditions
2. No data corruption
3. Proper lock timeouts
4. Transaction rollback on failure
"""

import pytest
import time
import multiprocessing
from pathlib import Path
from unittest.mock import patch
import tempfile

from core.portfolio_lock_manager import PortfolioLockManager
from core.paper_portfolio_manager import PaperPortfolioManager


class TestPortfolioLockManager:
    """Unit tests for PortfolioLockManager."""

    @pytest.fixture
    def temp_lock_file(self, tmp_path):
        """Create temporary lock file."""
        lock_file = tmp_path / "test.lock"
        return str(lock_file)

    @pytest.fixture
    def lock_manager(self, temp_lock_file):
        """Create lock manager with temp file."""
        return PortfolioLockManager(lock_file=temp_lock_file)

    def test_acquire_and_release_lock(self, lock_manager):
        """Test basic lock acquisition and release."""
        # Acquire lock
        with lock_manager.acquire_lock("test_operation"):
            # Lock should be held
            assert lock_manager.is_locked() is True

        # Lock should be released
        assert lock_manager.is_locked() is False

    def test_lock_timeout(self, lock_manager):
        """Test that lock acquisition times out."""
        # Hold lock in background
        def hold_lock():
            with lock_manager.acquire_lock("hold", timeout=10.0):
                time.sleep(2.0)  # Hold for 2 seconds

        # Start background lock holder
        import threading
        thread = threading.Thread(target=hold_lock)
        thread.start()

        # Wait for lock to be acquired
        time.sleep(0.1)

        # Try to acquire with short timeout - should fail
        with pytest.raises(TimeoutError):
            with lock_manager.acquire_lock("test", timeout=0.5):
                pass

        # Wait for background thread to finish
        thread.join()

    def test_lock_released_on_exception(self, lock_manager):
        """Test that lock is released even if exception occurs."""
        # Acquire lock and raise exception
        try:
            with lock_manager.acquire_lock("test_exception"):
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Lock should still be released
        assert lock_manager.is_locked() is False

    def test_acquire_lock_with_retry(self, lock_manager):
        """Test lock acquisition with retry logic."""
        # Hold lock briefly
        def brief_hold():
            with lock_manager.acquire_lock("hold", timeout=5.0):
                time.sleep(0.5)

        # Start background lock holder
        import threading
        thread = threading.Thread(target=brief_hold)
        thread.start()

        # Wait for lock to be acquired
        time.sleep(0.1)

        # Try with retry - should succeed after first lock releases
        with lock_manager.acquire_lock_with_retry(
            "test",
            timeout=1.0,
            max_retries=3,
            retry_delay=0.3
        ):
            assert True  # Successfully acquired

        thread.join()


class TestConcurrentPortfolioAccess:
    """Stress tests for concurrent portfolio access."""

    @pytest.fixture
    def temp_portfolio_file(self, tmp_path):
        """Create temporary portfolio file."""
        return tmp_path / "test_portfolio.json"

    @pytest.fixture
    def temp_tx_log_file(self, tmp_path):
        """Create temporary transaction log file."""
        return tmp_path / "test_tx_log.json"

    def concurrent_buy_worker(self, portfolio_file, tx_log_file, symbol, shares, price, results_queue):
        """Worker function for concurrent buy operations."""
        try:
            with patch.object(PaperPortfolioManager, 'PORTFOLIO_FILE', str(portfolio_file)):
                with patch.object(PaperPortfolioManager, 'TRANSACTION_LOG_FILE', str(tx_log_file)):
                    portfolio = PaperPortfolioManager()
                    result = portfolio.buy(symbol, shares, price)
                    results_queue.put(result)
        except Exception as e:
            results_queue.put({'success': False, 'error': str(e)})

    def test_concurrent_buys_no_overspending(self, temp_portfolio_file, temp_tx_log_file):
        """
        Test that concurrent buys don't allow overspending.

        Scenario: 2 processes try to buy simultaneously,
        total cost exceeds available cash.
        Only one should succeed.
        """
        # Initialize portfolio
        with patch.object(PaperPortfolioManager, 'PORTFOLIO_FILE', str(temp_portfolio_file)):
            with patch.object(PaperPortfolioManager, 'TRANSACTION_LOG_FILE', str(temp_tx_log_file)):
                initial_portfolio = PaperPortfolioManager()
                initial_cash = initial_portfolio.cash  # $10,000

        # Create result queue
        manager = multiprocessing.Manager()
        results_queue = manager.Queue()

        # Launch 2 concurrent buys that together exceed cash
        # Each costs $6,000, total $12,000 > $10,000
        processes = []
        for i in range(2):
            p = multiprocessing.Process(
                target=self.concurrent_buy_worker,
                args=(temp_portfolio_file, temp_tx_log_file, f"STOCK{i}", 40, 150.0, results_queue)
            )
            p.start()
            processes.append(p)

        # Wait for all processes
        for p in processes:
            p.join(timeout=10)

        # Collect results
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())

        # Verify results
        successes = [r for r in results if r.get('success')]
        failures = [r for r in results if not r.get('success')]

        # Only one should succeed (whichever got the lock first)
        assert len(successes) == 1, f"Expected 1 success, got {len(successes)}"
        assert len(failures) == 1, f"Expected 1 failure, got {len(failures)}"

        # Verify final portfolio state
        with patch.object(PaperPortfolioManager, 'PORTFOLIO_FILE', str(temp_portfolio_file)):
            with patch.object(PaperPortfolioManager, 'TRANSACTION_LOG_FILE', str(temp_tx_log_file)):
                final_portfolio = PaperPortfolioManager()

                # Should have exactly one position
                assert len(final_portfolio.positions) == 1

                # Cash should be exactly initial - cost
                expected_cash = initial_cash - (40 * 150.0)
                assert final_portfolio.cash == expected_cash

    def test_concurrent_buy_and_sell_no_corruption(self, temp_portfolio_file, temp_tx_log_file):
        """
        Test that concurrent buy and sell don't corrupt portfolio.

        Scenario: Buy AAPL and sell GOOGL simultaneously.
        Both should succeed without corrupting data.
        """
        # Initialize portfolio with GOOGL position
        with patch.object(PaperPortfolioManager, 'PORTFOLIO_FILE', str(temp_portfolio_file)):
            with patch.object(PaperPortfolioManager, 'TRANSACTION_LOG_FILE', str(temp_tx_log_file)):
                initial_portfolio = PaperPortfolioManager()
                # Buy GOOGL first
                initial_portfolio.buy("GOOGL", 10, 100.0)
                initial_cash = initial_portfolio.cash

        # Result queue
        manager = multiprocessing.Manager()
        results_queue = manager.Queue()

        # Concurrent buy AAPL and sell GOOGL
        def buy_worker():
            self.concurrent_buy_worker(
                temp_portfolio_file, temp_tx_log_file,
                "AAPL", 5, 150.0, results_queue
            )

        def sell_worker():
            try:
                with patch.object(PaperPortfolioManager, 'PORTFOLIO_FILE', str(temp_portfolio_file)):
                    with patch.object(PaperPortfolioManager, 'TRANSACTION_LOG_FILE', str(temp_tx_log_file)):
                        portfolio = PaperPortfolioManager()
                        result = portfolio.sell("GOOGL", 10, 110.0)
                        results_queue.put(result)
            except Exception as e:
                results_queue.put({'success': False, 'error': str(e)})

        # Launch processes
        p1 = multiprocessing.Process(target=buy_worker)
        p2 = multiprocessing.Process(target=sell_worker)

        p1.start()
        p2.start()

        p1.join(timeout=10)
        p2.join(timeout=10)

        # Collect results
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())

        # Both should succeed
        successes = [r for r in results if r.get('success')]
        assert len(successes) == 2, "Both operations should succeed"

        # Verify final state
        with patch.object(PaperPortfolioManager, 'PORTFOLIO_FILE', str(temp_portfolio_file)):
            with patch.object(PaperPortfolioManager, 'TRANSACTION_LOG_FILE', str(temp_tx_log_file)):
                final_portfolio = PaperPortfolioManager()

                # Should have AAPL, not GOOGL
                assert "AAPL" in final_portfolio.positions
                assert "GOOGL" not in final_portfolio.positions

                # Cash calculation: initial - AAPL cost + GOOGL proceeds
                expected_cash = initial_cash - (5 * 150.0) + (10 * 110.0)
                assert final_portfolio.cash == expected_cash

    def test_many_concurrent_transactions(self, temp_portfolio_file, temp_tx_log_file):
        """
        Stress test with many concurrent transactions.

        Run 20 concurrent buy operations and verify no data loss.
        """
        # Initialize
        with patch.object(PaperPortfolioManager, 'PORTFOLIO_FILE', str(temp_portfolio_file)):
            with patch.object(PaperPortfolioManager, 'TRANSACTION_LOG_FILE', str(temp_tx_log_file)):
                PaperPortfolioManager()  # Initialize file

        # Result queue
        manager = multiprocessing.Manager()
        results_queue = manager.Queue()

        # Launch 20 concurrent small buys
        processes = []
        num_processes = 20
        shares_per_buy = 1
        price_per_share = 100.0

        for i in range(num_processes):
            p = multiprocessing.Process(
                target=self.concurrent_buy_worker,
                args=(
                    temp_portfolio_file,
                    temp_tx_log_file,
                    f"STOCK{i}",
                    shares_per_buy,
                    price_per_share,
                    results_queue
                )
            )
            p.start()
            processes.append(p)

        # Wait for all
        for p in processes:
            p.join(timeout=30)

        # Collect results
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())

        # All should succeed (enough cash for all)
        successes = [r for r in results if r.get('success')]
        assert len(successes) == num_processes, f"Expected {num_processes} successes, got {len(successes)}"

        # Verify final state
        with patch.object(PaperPortfolioManager, 'PORTFOLIO_FILE', str(temp_portfolio_file)):
            with patch.object(PaperPortfolioManager, 'TRANSACTION_LOG_FILE', str(temp_tx_log_file)):
                final_portfolio = PaperPortfolioManager()

                # Should have exactly num_processes positions
                assert len(final_portfolio.positions) == num_processes

                # Verify each position
                for i in range(num_processes):
                    symbol = f"STOCK{i}"
                    assert symbol in final_portfolio.positions
                    assert final_portfolio.positions[symbol]['shares'] == shares_per_buy

                # Verify cash
                total_spent = num_processes * shares_per_buy * price_per_share
                expected_cash = 10000.0 - total_spent
                assert final_portfolio.cash == expected_cash


class TestAtomicWrites:
    """Test atomic write operations."""

    def test_atomic_write_on_failure(self, tmp_path):
        """Test that failed writes don't corrupt portfolio file."""
        portfolio_file = tmp_path / "test_portfolio.json"
        tx_log_file = tmp_path / "test_tx.json"

        with patch.object(PaperPortfolioManager, 'PORTFOLIO_FILE', str(portfolio_file)):
            with patch.object(PaperPortfolioManager, 'TRANSACTION_LOG_FILE', str(tx_log_file)):
                portfolio = PaperPortfolioManager()

                # Make a successful buy
                result1 = portfolio.buy("AAPL", 10, 100.0)
                assert result1['success'] is True

                # Verify file is valid JSON
                import json
                with open(portfolio_file, 'r') as f:
                    data = json.load(f)
                    assert "AAPL" in data['positions']

                # Simulate write failure by making file read-only
                portfolio_file.chmod(0o444)

                try:
                    # This should fail
                    portfolio.buy("GOOGL", 5, 150.0)
                except Exception:
                    pass

                # Restore permissions
                portfolio_file.chmod(0o644)

                # File should still be valid JSON with original data
                with open(portfolio_file, 'r') as f:
                    data = json.load(f)
                    assert "AAPL" in data['positions']
                    assert "GOOGL" not in data['positions']  # Failed buy shouldn't be there


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
