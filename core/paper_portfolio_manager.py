"""
Paper Trading Portfolio Manager

Simple portfolio manager for paper trading with $10,000 initial balance.
Logs all transactions for verification and analysis.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from functools import lru_cache
from cachetools import TTLCache

from .portfolio_lock_manager import PortfolioLockManager


class PaperPortfolioManager:
    """Manages paper trading portfolio with transaction logging."""

    INITIAL_CASH = 10000.0
    PORTFOLIO_FILE = "data/paper_portfolio.json"
    TRANSACTION_LOG_FILE = "data/transaction_log.json"

    def __init__(self):
        """Initialize portfolio manager."""
        self.portfolio_file = Path(self.PORTFOLIO_FILE)
        self.transaction_log_file = Path(self.TRANSACTION_LOG_FILE)

        # Ensure data directory exists
        self.portfolio_file.parent.mkdir(parents=True, exist_ok=True)

        # Initialize lock manager for cross-process safety
        self.lock_manager = PortfolioLockManager()

        # Price cache with automatic eviction: max 500 symbols, 60s TTL
        # Prevents memory leak from unbounded dict growth
        self._price_cache = TTLCache(maxsize=500, ttl=60)

        # Load or initialize portfolio
        self._load_or_initialize_portfolio()

    def _load_or_initialize_portfolio(self):
        """Load existing portfolio or create new one."""
        if self.portfolio_file.exists():
            with open(self.portfolio_file, 'r') as f:
                data = json.load(f)
                self.cash = data.get('cash', self.INITIAL_CASH)
                self.positions = data.get('positions', {})
                self.created_at = data.get('created_at', datetime.now().isoformat())
        else:
            self.cash = self.INITIAL_CASH
            self.positions = {}
            self.created_at = datetime.now().isoformat()
            self._save_portfolio()

    def _save_portfolio(self):
        """Save portfolio to disk with atomic write."""
        data = {
            'cash': self.cash,
            'positions': self.positions,
            'created_at': self.created_at,
            'updated_at': datetime.now().isoformat()
        }

        # Write to temp file, then rename (atomic)
        temp_file = Path(str(self.portfolio_file) + '.tmp')

        try:
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2)

            # Atomic rename (overwrites existing file)
            temp_file.replace(self.portfolio_file)

        except Exception as e:
            # Clean up temp file on error
            if temp_file.exists():
                temp_file.unlink()
            raise

    def _reload_portfolio_from_disk(self):
        """
        Reload portfolio state from disk.

        CRITICAL: Must be called AFTER acquiring lock to ensure fresh data.
        This prevents race conditions where multiple processes have stale state.
        """
        if self.portfolio_file.exists():
            try:
                with open(self.portfolio_file, 'r') as f:
                    data = json.load(f)
                    self.cash = data.get('cash', self.INITIAL_CASH)
                    self.positions = data.get('positions', {})
                    # Don't update created_at - that's immutable
            except Exception as e:
                # If reload fails, keep current state but log error
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to reload portfolio from disk: {e}")
                raise

    def _log_transaction(self, action: str, symbol: str, shares: int, price: float, total: float):
        """Log transaction to transaction log file."""
        transaction = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'symbol': symbol,
            'shares': shares,
            'price': price,
            'total': total,
            'cash_after': self.cash,
            'portfolio_value': self.get_portfolio_value()
        }

        # Load existing transactions
        transactions = []
        if self.transaction_log_file.exists():
            with open(self.transaction_log_file, 'r') as f:
                transactions = json.load(f)

        # Append new transaction
        transactions.append(transaction)

        # Save back to file
        with open(self.transaction_log_file, 'w') as f:
            json.dump(transactions, f, indent=2)

    def _validate_trade_inputs(self, shares: int, price: float, action: str) -> Optional[str]:
        """
        Validate trading inputs (shares and price).

        Args:
            shares: Number of shares
            price: Price per share
            action: Trading action (for error messages)

        Returns:
            Error message if validation fails, None if valid
        """
        import math

        # Validate shares
        if not isinstance(shares, (int, float)):
            return f'Invalid shares: must be a number, got {type(shares).__name__}'

        if shares <= 0:
            return 'Shares must be positive'

        if not isinstance(shares, int) and not shares.is_integer():
            return f'Shares must be a whole number, got {shares}'

        # Validate price
        if not isinstance(price, (int, float)):
            return f'Invalid price: must be a number, got {type(price).__name__}'

        if price <= 0:
            return 'Price must be positive'

        if math.isnan(price):
            return 'Invalid price: NaN (not a number)'

        if math.isinf(price):
            return 'Invalid price: infinity'

        # Validate total cost doesn't overflow
        try:
            total = shares * price
            if math.isinf(total):
                return f'Total cost overflow: {shares} × ${price} is too large'
        except (OverflowError, ValueError) as e:
            return f'Calculation error: {str(e)}'

        return None

    def buy(self, symbol: str, shares: int, price: float) -> Dict:
        """
        Buy shares of a stock with file locking.

        Args:
            symbol: Stock symbol
            shares: Number of shares to buy
            price: Price per share

        Returns:
            Dict with status and message
        """
        # Validate inputs (before acquiring lock)
        validation_error = self._validate_trade_inputs(shares, price, 'buy')
        if validation_error:
            return {'success': False, 'message': validation_error}

        # Validate symbol
        if not symbol or not isinstance(symbol, str):
            return {'success': False, 'message': 'Invalid symbol'}

        total_cost = shares * price

        # Acquire lock for critical section
        with self.lock_manager.acquire_lock(f"buy_{symbol}"):
            # CRITICAL FIX: Reload portfolio from disk AFTER acquiring lock
            # This ensures we have fresh data, preventing race conditions
            self._reload_portfolio_from_disk()

            # Check cash with fresh data
            if total_cost > self.cash:
                return {
                    'success': False,
                    'message': f'Insufficient funds. Need ${total_cost:.2f}, have ${self.cash:.2f}'
                }

            # Store previous state for rollback
            prev_cash = self.cash
            prev_position = self.positions.get(symbol, None).copy() if symbol in self.positions else None

            try:
                # Execute buy
                self.cash -= total_cost

                if symbol in self.positions:
                    # Average cost basis calculation
                    existing_shares = self.positions[symbol]['shares']
                    existing_cost_basis = self.positions[symbol]['cost_basis']
                    total_shares = existing_shares + shares
                    new_cost_basis = ((existing_shares * existing_cost_basis) + total_cost) / total_shares

                    self.positions[symbol] = {
                        'shares': total_shares,
                        'cost_basis': new_cost_basis,
                        'first_purchase_date': self.positions[symbol].get('first_purchase_date', datetime.now().isoformat())
                    }
                else:
                    self.positions[symbol] = {
                        'shares': shares,
                        'cost_basis': price,
                        'first_purchase_date': datetime.now().isoformat()
                    }

                # Save portfolio - if this fails, rollback will trigger
                self._save_portfolio()

                # Log transaction - if this fails, transaction is still saved to portfolio
                try:
                    self._log_transaction('BUY', symbol, shares, price, total_cost)
                except Exception as log_error:
                    # Don't fail the whole transaction if logging fails
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Transaction executed but logging failed: {log_error}")

                return {
                    'success': True,
                    'message': f'Bought {shares} shares of {symbol} at ${price:.2f}',
                    'total_cost': total_cost,
                    'cash_remaining': self.cash
                }

            except Exception as e:
                # Rollback on ANY failure (including save failures)
                self.cash = prev_cash
                if prev_position is None:
                    # Remove newly added position
                    if symbol in self.positions:
                        del self.positions[symbol]
                else:
                    # Restore previous position
                    self.positions[symbol] = prev_position

                return {
                    'success': False,
                    'message': f'Buy failed: {str(e)}'
                }

    def sell(self, symbol: str, shares: int, price: float) -> Dict:
        """
        Sell shares of a stock with file locking.

        Args:
            symbol: Stock symbol
            shares: Number of shares to sell
            price: Price per share

        Returns:
            Dict with status and message
        """
        # Validate inputs (before acquiring lock)
        validation_error = self._validate_trade_inputs(shares, price, 'sell')
        if validation_error:
            return {'success': False, 'message': validation_error}

        # Validate symbol
        if not symbol or not isinstance(symbol, str):
            return {'success': False, 'message': 'Invalid symbol'}

        # Acquire lock for critical section
        with self.lock_manager.acquire_lock(f"sell_{symbol}"):
            # CRITICAL FIX: Reload portfolio from disk AFTER acquiring lock
            # This ensures we have fresh data, preventing race conditions
            self._reload_portfolio_from_disk()

            # Check ownership with fresh data
            if symbol not in self.positions:
                return {'success': False, 'message': f'You do not own {symbol}'}

            # Check if we have enough shares
            owned_shares = self.positions[symbol]['shares']
            if shares > owned_shares:
                return {
                    'success': False,
                    'message': f'Insufficient shares. Own {owned_shares}, trying to sell {shares}'
                }

            # Store previous state for rollback
            prev_cash = self.cash
            prev_position = self.positions[symbol].copy()

            try:
                # Execute sell
                total_proceeds = shares * price
                self.cash += total_proceeds

                # Calculate P&L
                cost_basis = self.positions[symbol]['cost_basis']
                pnl = (price - cost_basis) * shares
                pnl_percent = ((price - cost_basis) / cost_basis) * 100

                # Update position
                if shares == owned_shares:
                    # Sold entire position
                    del self.positions[symbol]
                else:
                    # Partial sale
                    self.positions[symbol]['shares'] -= shares

                # Save portfolio - if this fails, rollback will trigger
                self._save_portfolio()

                # Log transaction - if this fails, transaction is still saved to portfolio
                try:
                    self._log_transaction('SELL', symbol, shares, price, total_proceeds)
                except Exception as log_error:
                    # Don't fail the whole transaction if logging fails
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Transaction executed but logging failed: {log_error}")

                return {
                    'success': True,
                    'message': f'Sold {shares} shares of {symbol} at ${price:.2f}',
                    'total_proceeds': total_proceeds,
                    'pnl': pnl,
                    'pnl_percent': pnl_percent,
                    'cash_remaining': self.cash
                }

            except Exception as e:
                # Rollback on ANY failure (including save failures)
                self.cash = prev_cash
                self.positions[symbol] = prev_position

                return {
                    'success': False,
                    'message': f'Sell failed: {str(e)}'
                }

    def _get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get current market price for a symbol with caching.

        Args:
            symbol: Stock symbol

        Returns:
            Current price or None if unavailable
        """
        # Check cache (TTLCache handles expiration automatically)
        if symbol in self._price_cache:
            return self._price_cache[symbol]

        # Fetch fresh price
        try:
            from data.enhanced_provider import EnhancedYahooProvider
            provider = EnhancedYahooProvider()
            data = provider.get_comprehensive_data(symbol)

            if data and 'current_price' in data:
                price = data['current_price']
                # TTLCache will auto-expire after 60s and evict if >500 symbols
                self._price_cache[symbol] = price
                return price
        except Exception as e:
            print(f"Warning: Could not fetch price for {symbol}: {e}")

        return None

    def get_portfolio(self) -> Dict:
        """Get current portfolio state."""
        return {
            'cash': self.cash,
            'positions': self.positions,
            'created_at': self.created_at
        }

    def get_portfolio_with_prices(self) -> Dict:
        """
        Get portfolio state enriched with current market prices and P&L.

        Returns:
            Dict with cash, positions (with current prices), and created_at
        """
        enriched_positions = {}

        for symbol, pos in self.positions.items():
            current_price = self._get_current_price(symbol)
            cost_basis = pos['cost_basis']
            shares = pos['shares']

            if current_price is not None:
                market_value = shares * current_price
                unrealized_pnl = (current_price - cost_basis) * shares
                unrealized_pnl_percent = ((current_price - cost_basis) / cost_basis) * 100
            else:
                # Fallback to cost basis if price unavailable
                current_price = cost_basis
                market_value = shares * cost_basis
                unrealized_pnl = 0.0
                unrealized_pnl_percent = 0.0

            enriched_positions[symbol] = {
                'shares': shares,
                'cost_basis': cost_basis,
                'current_price': current_price,
                'market_value': market_value,
                'unrealized_pnl': unrealized_pnl,
                'unrealized_pnl_percent': unrealized_pnl_percent,
                'first_purchase_date': pos.get('first_purchase_date', '')
            }

        return {
            'cash': self.cash,
            'positions': enriched_positions,
            'created_at': self.created_at
        }

    def get_portfolio_value(self, use_market_prices: bool = True) -> float:
        """
        Calculate total portfolio value (cash + positions).

        Args:
            use_market_prices: If True, uses current market prices. If False, uses cost basis.

        Returns:
            Total portfolio value
        """
        if not use_market_prices:
            # Legacy mode: use cost basis
            positions_value = sum(
                pos['shares'] * pos['cost_basis']
                for pos in self.positions.values()
            )
        else:
            # New mode: use current market prices
            positions_value = 0.0
            for symbol, pos in self.positions.items():
                current_price = self._get_current_price(symbol)
                if current_price is not None:
                    positions_value += pos['shares'] * current_price
                else:
                    # Fallback to cost basis if price unavailable
                    positions_value += pos['shares'] * pos['cost_basis']

        return self.cash + positions_value

    def get_transactions(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get transaction history.

        Args:
            limit: Maximum number of transactions to return (most recent first)

        Returns:
            List of transactions
        """
        if not self.transaction_log_file.exists():
            return []

        with open(self.transaction_log_file, 'r') as f:
            transactions = json.load(f)

        # Return most recent first
        transactions.reverse()

        if limit:
            return transactions[:limit]
        return transactions

    def reset_portfolio(self) -> Dict:
        """Reset portfolio to initial state."""
        self.cash = self.INITIAL_CASH
        self.positions = {}
        self.created_at = datetime.now().isoformat()

        self._save_portfolio()

        # Archive old transaction log
        if self.transaction_log_file.exists():
            archive_name = f"transaction_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            archive_path = self.transaction_log_file.parent / archive_name
            self.transaction_log_file.rename(archive_path)

        return {
            'success': True,
            'message': 'Portfolio reset to initial state',
            'cash': self.cash
        }

    def get_stats(self) -> Dict:
        """Get portfolio statistics with market prices."""
        total_value = self.get_portfolio_value(use_market_prices=True)
        total_invested = self.INITIAL_CASH - self.cash
        num_positions = len(self.positions)

        # Calculate realized P&L from sells
        transactions = self.get_transactions()
        transactions_list = list(reversed(transactions))  # Chronological order

        # Track cost basis for sold positions
        position_cost_tracker = {}  # {symbol: total_cost_of_shares_sold}

        for tx in transactions_list:
            symbol = tx['symbol']
            if tx['action'] == 'SELL':
                # Get cost basis at time of sell
                shares_sold = tx['shares']
                # We need to find the cost basis - stored in positions at sell time
                # For simplicity, use the price difference from the transaction
                # Realized P&L is already calculated during sell, so sum from transaction log
                pass

        # Simpler approach: Sum P&L from successful sell transactions
        # The sell() method calculates P&L, but we need to track it in transactions
        # For now, calculate as: (total_sells - cost_of_sold_shares)
        total_buys = sum(t['total'] for t in transactions_list if t['action'] == 'BUY')
        total_sells = sum(t['total'] for t in transactions_list if t['action'] == 'SELL')

        # Current position cost
        current_position_cost = sum(
            pos['shares'] * pos['cost_basis']
            for pos in self.positions.values()
        )

        # Realized P&L = (money from sells) - (cost of shares sold)
        # Cost of shares sold = total money spent on buys - cost still in positions
        cost_of_sold_shares = total_buys - current_position_cost
        realized_pnl = total_sells - cost_of_sold_shares

        # Calculate unrealized P&L
        portfolio_with_prices = self.get_portfolio_with_prices()
        unrealized_pnl = sum(
            pos['unrealized_pnl']
            for pos in portfolio_with_prices['positions'].values()
        )

        return {
            'total_value': total_value,
            'cash': self.cash,
            'invested': total_invested,
            'num_positions': num_positions,
            'total_return': total_value - self.INITIAL_CASH,
            'total_return_percent': ((total_value - self.INITIAL_CASH) / self.INITIAL_CASH) * 100 if self.INITIAL_CASH > 0 else 0,
            'realized_pnl': realized_pnl,
            'unrealized_pnl': unrealized_pnl,
            'num_transactions': len(transactions)
        }
