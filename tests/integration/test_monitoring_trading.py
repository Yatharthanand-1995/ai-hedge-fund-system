"""
Integration Tests for Monitoring → Trading Buy Queue Flow

Tests the complete end-to-end flow:
1. Monitoring detects signal at 2 PM
2. Signal queued for 4 PM execution
3. Trading scheduler processes queue at 4 PM
4. Trade executes
5. Portfolio updated
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock

from core.buy_queue_manager import BuyQueueManager
from core.paper_portfolio_manager import PaperPortfolioManager


class TestBuyQueueIntegration:
    """Integration tests for buy queue system."""

    @pytest.fixture
    def temp_queue_file(self, tmp_path):
        """Create temporary queue file."""
        queue_file = tmp_path / "test_buy_queue.json"
        return str(queue_file)

    @pytest.fixture
    def queue_manager(self, temp_queue_file):
        """Create queue manager with temp file."""
        return BuyQueueManager(queue_file=temp_queue_file)

    @pytest.fixture
    def temp_portfolio_file(self, tmp_path):
        """Create temporary portfolio file."""
        portfolio_file = tmp_path / "test_portfolio.json"
        return str(portfolio_file)

    def test_enqueue_and_dequeue_single_opportunity(self, queue_manager):
        """Test enqueueing and dequeueing a single opportunity."""
        # Enqueue an opportunity
        success = queue_manager.enqueue(
            symbol="AAPL",
            score=85.5,
            signal="STRONG BUY",
            price=150.0,
            reason="Major upgrade: HOLD → STRONG BUY"
        )

        assert success is True

        # Dequeue all opportunities
        opportunities = queue_manager.dequeue_all()

        assert len(opportunities) == 1
        assert opportunities[0]['symbol'] == "AAPL"
        assert opportunities[0]['score'] == 85.5
        assert opportunities[0]['signal'] == "STRONG BUY"
        assert opportunities[0]['price'] == 150.0

        # Queue should be empty after dequeue
        opportunities2 = queue_manager.dequeue_all()
        assert len(opportunities2) == 0

    def test_enqueue_multiple_opportunities(self, queue_manager):
        """Test enqueueing multiple opportunities."""
        symbols = [("AAPL", 85.5), ("GOOGL", 88.0), ("MSFT", 82.3)]

        for symbol, score in symbols:
            queue_manager.enqueue(
                symbol=symbol,
                score=score,
                signal="STRONG BUY",
                reason="Test"
            )

        opportunities = queue_manager.dequeue_all()
        assert len(opportunities) == 3

        queued_symbols = {opp['symbol'] for opp in opportunities}
        assert queued_symbols == {"AAPL", "GOOGL", "MSFT"}

    def test_prevent_duplicate_symbols(self, queue_manager):
        """Test that duplicate symbols are prevented."""
        # Enqueue AAPL
        success1 = queue_manager.enqueue(
            symbol="AAPL",
            score=85.5,
            signal="STRONG BUY",
            reason="Test"
        )
        assert success1 is True

        # Try to enqueue AAPL again
        success2 = queue_manager.enqueue(
            symbol="AAPL",
            score=90.0,
            signal="STRONG BUY",
            reason="Test 2"
        )
        assert success2 is False  # Should reject duplicate

        # Only one AAPL should be in queue
        opportunities = queue_manager.dequeue_all()
        assert len(opportunities) == 1
        assert opportunities[0]['score'] == 85.5  # Original score

    def test_stale_entries_cleanup(self, queue_manager, temp_queue_file):
        """Test that stale entries (>24 hours old) are removed."""
        # Manually create queue with stale entry
        stale_time = "2026-01-01T10:00:00Z"  # 2 days ago
        recent_time = datetime.now(timezone.utc).isoformat() + "Z"

        data = {
            "queued_opportunities": [
                {
                    "symbol": "OLD",
                    "queued_at": stale_time,
                    "signal": "BUY",
                    "score": 75.0,
                    "reason": "Stale"
                },
                {
                    "symbol": "NEW",
                    "queued_at": recent_time,
                    "signal": "STRONG BUY",
                    "score": 85.0,
                    "reason": "Recent"
                }
            ],
            "metadata": {
                "last_modified": recent_time
            }
        }

        with open(temp_queue_file, 'w') as f:
            json.dump(data, f)

        # Dequeue should only return recent entry
        opportunities = queue_manager.dequeue_all()

        assert len(opportunities) == 1
        assert opportunities[0]['symbol'] == "NEW"

    def test_validate_and_filter_score_drop(self, queue_manager):
        """Test that opportunities with significant score drops are rejected."""
        # Queue an opportunity with high score
        queue_manager.enqueue(
            symbol="AAPL",
            score=85.0,
            signal="STRONG BUY",
            reason="Test"
        )

        opportunities = queue_manager.peek()

        # Mock current analyses with dropped score
        current_analyses = {
            "AAPL": {
                "composite_score": 70.0,  # Dropped 15 points
                "recommendation": "BUY"
            }
        }

        # Validate and filter
        valid = queue_manager.validate_and_filter(opportunities, current_analyses)

        # Should be rejected due to score drop >10 points
        assert len(valid) == 0

    def test_validate_and_filter_signal_downgrade(self, queue_manager):
        """Test that downgraded signals are rejected."""
        queue_manager.enqueue(
            symbol="AAPL",
            score=85.0,
            signal="STRONG BUY",
            reason="Test"
        )

        opportunities = queue_manager.peek()

        # Mock current analyses with downgraded signal
        current_analyses = {
            "AAPL": {
                "composite_score": 84.0,  # Small score change
                "recommendation": "HOLD"  # Downgraded
            }
        }

        valid = queue_manager.validate_and_filter(opportunities, current_analyses)

        # Should be rejected due to signal downgrade
        assert len(valid) == 0

    def test_validate_and_filter_still_valid(self, queue_manager):
        """Test that still-valid opportunities pass validation."""
        queue_manager.enqueue(
            symbol="AAPL",
            score=85.0,
            signal="STRONG BUY",
            reason="Test"
        )

        opportunities = queue_manager.peek()

        # Mock current analyses with maintained signal
        current_analyses = {
            "AAPL": {
                "composite_score": 87.0,  # Score improved
                "recommendation": "STRONG BUY"  # Still strong buy
            }
        }

        valid = queue_manager.validate_and_filter(opportunities, current_analyses)

        # Should pass validation
        assert len(valid) == 1
        assert valid[0]['symbol'] == "AAPL"

    def test_peek_does_not_clear_queue(self, queue_manager):
        """Test that peek() doesn't remove opportunities."""
        queue_manager.enqueue(
            symbol="AAPL",
            score=85.0,
            signal="STRONG BUY",
            reason="Test"
        )

        # Peek should not clear queue
        opportunities1 = queue_manager.peek()
        assert len(opportunities1) == 1

        # Second peek should still show the opportunity
        opportunities2 = queue_manager.peek()
        assert len(opportunities2) == 1

        # Dequeue should clear it
        opportunities3 = queue_manager.dequeue_all()
        assert len(opportunities3) == 1

        # Now it should be empty
        opportunities4 = queue_manager.peek()
        assert len(opportunities4) == 0

    def test_clear_queue(self, queue_manager):
        """Test clearing the queue."""
        # Add multiple opportunities
        for symbol in ["AAPL", "GOOGL", "MSFT"]:
            queue_manager.enqueue(
                symbol=symbol,
                score=85.0,
                signal="STRONG BUY",
                reason="Test"
            )

        # Verify queue has 3 items
        assert len(queue_manager.peek()) == 3

        # Clear queue
        success = queue_manager.clear()
        assert success is True

        # Queue should be empty
        assert len(queue_manager.peek()) == 0


class TestEndToEndBuyFlow:
    """Test complete end-to-end buy queue flow."""

    @pytest.fixture
    def mock_portfolio_manager(self, tmp_path):
        """Create portfolio manager with temp file."""
        portfolio_file = tmp_path / "test_portfolio.json"
        with patch.object(PaperPortfolioManager, 'PORTFOLIO_FILE', str(portfolio_file)):
            with patch.object(PaperPortfolioManager, 'TRANSACTION_LOG_FILE', str(tmp_path / "test_tx_log.json")):
                manager = PaperPortfolioManager()
                return manager

    def test_end_to_end_queue_to_execution(self, tmp_path):
        """
        Test complete flow:
        1. Queue opportunity
        2. Validate at execution time
        3. Execute buy
        4. Portfolio updated
        """
        # Setup
        queue_file = tmp_path / "test_queue.json"
        queue_manager = BuyQueueManager(queue_file=str(queue_file))

        portfolio_file = tmp_path / "test_portfolio.json"

        # Step 1: Queue opportunity (simulating 2 PM detection)
        queue_manager.enqueue(
            symbol="AAPL",
            score=85.5,
            signal="STRONG BUY",
            price=None,  # Will fetch at execution
            reason="Major upgrade detected"
        )

        # Step 2: At 4 PM, dequeue and validate
        opportunities = queue_manager.dequeue_all()
        assert len(opportunities) == 1

        # Mock current analysis (still valid)
        current_analyses = {
            "AAPL": {
                "composite_score": 86.0,  # Improved
                "recommendation": "STRONG BUY",
                "market_data": {
                    "current_price": 150.0
                }
            }
        }

        # Validate
        temp_queue = BuyQueueManager(queue_file=str(tmp_path / "temp.json"))
        valid = temp_queue.validate_and_filter(opportunities, current_analyses)
        assert len(valid) == 1

        # Step 3: Execute buy
        with patch.object(PaperPortfolioManager, 'PORTFOLIO_FILE', str(portfolio_file)):
            with patch.object(PaperPortfolioManager, 'TRANSACTION_LOG_FILE', str(tmp_path / "tx.json")):
                portfolio = PaperPortfolioManager()

                # Execute buy
                result = portfolio.buy(
                    symbol="AAPL",
                    shares=10,
                    price=150.0
                )

                assert result['success'] is True

                # Step 4: Verify portfolio updated
                assert "AAPL" in portfolio.positions
                assert portfolio.positions["AAPL"]['shares'] == 10
                assert portfolio.positions["AAPL"]['cost_basis'] == 150.0
                assert portfolio.cash == 10000.0 - (10 * 150.0)  # Initial cash - cost


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
