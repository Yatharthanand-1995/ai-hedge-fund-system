"""
Monitoring Scheduler

Runs IntelligentSignalMonitor every 30 minutes during market hours.
Integrates with the main API scheduler for coordinated execution.
"""

import logging
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from .intelligent_monitor import IntelligentSignalMonitor
from scheduler.market_calendar import is_trading_day
from core.buy_queue_manager import BuyQueueManager

logger = logging.getLogger(__name__)

# Timezone for ET (Eastern Time)
ET_TIMEZONE = pytz.timezone('America/New_York')


class MonitoringScheduler:
    """
    Scheduler for intelligent signal monitoring.

    Runs every 30 minutes during market hours (9:30 AM - 4:00 PM ET).
    """

    def __init__(self, base_url: str = "http://localhost:8010"):
        self.base_url = base_url
        self.scheduler = AsyncIOScheduler(timezone=ET_TIMEZONE)
        self.monitor = IntelligentSignalMonitor(base_url=base_url)
        self.is_running = False

        # Load configuration
        self.config = self._load_config()
        self.config_mtime = self._get_config_mtime()

        # Initialize buy queue
        self.buy_queue = BuyQueueManager()

        # Load initial watchlist from config
        self._load_initial_watchlist()

        logger.info("MonitoringScheduler initialized")

    def _load_config(self) -> dict:
        """Load monitoring configuration."""
        config_file = Path("data/monitoring_config.json")
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load monitoring config: {e}")
                return self._default_config()
        return self._default_config()

    def _default_config(self) -> dict:
        """Return default configuration."""
        return {
            "monitoring": {
                "enabled": True,
                "market_hours_only": True
            }
        }

    def _get_config_mtime(self) -> float:
        """Get config file modification time."""
        config_file = Path("data/monitoring_config.json")
        try:
            return config_file.stat().st_mtime if config_file.exists() else 0
        except Exception as e:
            logger.warning(f"Error getting config mtime: {e}")
            return 0

    def _reload_config_if_changed(self):
        """Reload config if file was modified."""
        try:
            current_mtime = self._get_config_mtime()

            if current_mtime > self.config_mtime:
                old_active = self.config.get('system_active', False)
                self.config = self._load_config()
                self.config_mtime = current_mtime
                new_active = self.config.get('system_active', False)

                if old_active != new_active:
                    status = "ACTIVATED" if new_active else "DEACTIVATED"
                    logger.warning(f"🔄 Config reloaded - Trading {status}")
                else:
                    logger.info("🔄 Config reloaded - no trading status change")

        except Exception as e:
            logger.error(f"Error reloading config: {e}")

    def _load_initial_watchlist(self):
        """Load initial watchlist from configuration."""
        try:
            hot_watchlist = self.config.get('monitoring', {}).get('hot_watchlist', [])
            if hot_watchlist:
                for symbol in hot_watchlist:
                    self.monitor.add_to_watchlist(symbol)
                logger.info(f"Loaded {len(hot_watchlist)} symbols into hot watchlist from config: {', '.join(hot_watchlist)}")
            else:
                logger.info("No initial watchlist found in configuration")
        except Exception as e:
            logger.error(f"Failed to load initial watchlist: {e}")

    def start(self):
        """Start the monitoring scheduler."""
        if self.is_running:
            logger.warning("Monitoring scheduler is already running")
            return

        if not self.config.get('monitoring', {}).get('enabled', True):
            logger.info("Monitoring is disabled in configuration")
            return

        try:
            # Run every 30 minutes during market hours (9:30 AM - 4:00 PM ET)
            # Cron: minute=*/30 means every 30 minutes
            # We want to run at: 9:30, 10:00, 10:30, 11:00, 11:30, 12:00, 12:30, 1:00, 1:30, 2:00, 2:30, 3:00, 3:30, 4:00

            # Add job for 30-minute intervals
            self.scheduler.add_job(
                self._execute_monitoring_cycle,
                CronTrigger(
                    day_of_week='mon-fri',
                    hour='9-16',  # 9 AM to 4 PM
                    minute='0,30'  # On the hour and half-hour
                ),
                id='monitoring_cycle',
                name='Signal Monitoring Cycle'
            )

            self.scheduler.start()
            self.is_running = True

            next_run = self.get_next_execution_time()
            logger.info(f"✅ Monitoring scheduler started - next execution at {next_run}")

        except Exception as e:
            logger.error(f"Failed to start monitoring scheduler: {e}", exc_info=True)

    def stop(self):
        """Stop the monitoring scheduler."""
        if self.is_running and self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            self.is_running = False
            logger.info("Monitoring scheduler stopped")

    async def _execute_monitoring_cycle(self):
        """Execute one monitoring cycle."""
        execution_time = datetime.now(ET_TIMEZONE)

        # Reload config if changed
        self._reload_config_if_changed()

        logger.info(f"🔍 Starting monitoring cycle at {execution_time.strftime('%I:%M %p %Z')}")

        # Check if it's a trading day
        if not is_trading_day(execution_time):
            logger.info(f"Skipping monitoring - not a trading day ({execution_time.date()})")
            return

        # Check if within market hours (if configured)
        if self.config.get('monitoring', {}).get('market_hours_only', True):
            hour = execution_time.hour
            minute = execution_time.minute

            # Market hours: 9:30 AM - 4:00 PM ET
            if hour < 9 or (hour == 9 and minute < 30) or hour > 16:
                logger.debug(f"Skipping monitoring - outside market hours")
                return

        try:
            # Execute monitoring cycle
            stats = await self.monitor.monitor_cycle()

            logger.info(
                f"✅ Monitoring cycle complete: "
                f"{stats.get('portfolio_checks', 0)} portfolio checks, "
                f"{stats.get('watchlist_checks', 0)} watchlist checks, "
                f"{stats.get('signal_changes', 0)} changes detected"
            )

            # Handle signal changes if system is active
            if self.config.get('system_active', False):
                await self._handle_signal_changes()
            elif stats.get('signal_changes', 0) > 0:
                logger.info("📊 Signal changes detected but system is INACTIVE - monitoring only")

        except Exception as e:
            logger.error(f"Monitoring cycle error: {e}", exc_info=True)

    async def _handle_signal_changes(self):
        """Handle all signal changes based on urgency and configuration."""
        # Check if execution is enabled
        exec_enabled = self.config.get('execution', {}).get('enabled_when_active', True)

        if not exec_enabled:
            logger.info("🛑 Signal changes detected but execution is disabled")
            return

        # Get recent changes (last 5 minutes)
        from datetime import timedelta
        since = datetime.now() - timedelta(minutes=5)
        recent_changes = self.monitor.signal_history.get_changes_since(since)

        # Separate changes by action type
        critical_sells = [
            change for change in recent_changes
            if change['urgency'] == 'CRITICAL'
            and change['action_taken'] is None
            and change['change_type'] in ['CRITICAL_DOWNGRADE', 'MAJOR_DOWNGRADE']
        ]

        high_priority_sells = [
            change for change in recent_changes
            if change['urgency'] == 'HIGH'
            and change['action_taken'] is None
            and change['change_type'] in ['DOWNGRADE']
        ]

        strong_buy_signals = [
            change for change in recent_changes
            if change['urgency'] in ['MEDIUM', 'HIGH']
            and change['action_taken'] is None
            and change['change_type'] in ['MAJOR_UPGRADE', 'UPGRADE']
            and change['new_signal'] in ['STRONG BUY', 'BUY']
        ]

        # Execute sells first (critical, then high priority)
        immediate_sells = self.config.get('execution', {}).get('immediate_sells_on_critical', True)
        if immediate_sells and critical_sells:
            logger.warning(f"⚠️ {len(critical_sells)} critical sell signals detected!")
            await self._execute_critical_sells(critical_sells)

        if immediate_sells and high_priority_sells:
            logger.warning(f"⚠️ {len(high_priority_sells)} high-priority sell signals detected!")
            await self._execute_critical_sells(high_priority_sells)

        # Handle buy signals
        if strong_buy_signals:
            logger.info(f"📈 {len(strong_buy_signals)} strong buy signals detected!")
            await self._execute_opportunity_buys(strong_buy_signals)

    async def _execute_critical_sells(self, critical_changes: List[Dict]):
        """Execute immediate sells for critical signal downgrades."""
        from core.paper_portfolio_manager import PaperPortfolioManager
        import requests

        portfolio_manager = PaperPortfolioManager()
        max_trades = self.config.get('execution', {}).get('max_trades_per_hour', 5)
        trades_executed = 0

        for change in critical_changes:
            # Rate limiting
            if trades_executed >= max_trades:
                logger.warning(f"⚠️ Max trades per hour ({max_trades}) reached - deferring remaining sells")
                break

            symbol = change['symbol']

            # Check if we own this position
            if symbol not in portfolio_manager.positions:
                logger.debug(f"{symbol} not in portfolio - skipping sell")
                continue

            try:
                # Get current price
                response = requests.get(f"{self.base_url}/analyze/{symbol}", timeout=10)
                if response.status_code != 200:
                    logger.error(f"Failed to get price for {symbol}: {response.status_code}")
                    continue

                data = response.json()
                current_price = data.get('market_data', {}).get('current_price')

                if current_price is None or current_price <= 0:
                    logger.error(f"Invalid price for {symbol}: {current_price}")
                    continue

                # Get position details
                position = portfolio_manager.positions[symbol]
                shares = position['shares']
                cost_basis = position['cost_basis']

                # Execute sell
                result = portfolio_manager.sell(symbol, shares, current_price)

                if result['success']:
                    pnl = (current_price - cost_basis) * shares
                    pnl_percent = ((current_price - cost_basis) / cost_basis) * 100

                    logger.warning(
                        f"🔴 CRITICAL SELL EXECUTED: {symbol} "
                        f"{change['previous_signal']} → {change['new_signal']} "
                        f"| {shares} shares @ ${current_price:.2f} "
                        f"| P&L: ${pnl:+.2f} ({pnl_percent:+.1f}%)"
                    )

                    # Mark action taken in signal history
                    change['action_taken'] = 'SELL'
                    change['execution_time'] = datetime.now().isoformat()
                    change['execution_price'] = current_price
                    change['pnl'] = pnl
                    change['pnl_percent'] = pnl_percent

                    trades_executed += 1
                else:
                    logger.error(f"Failed to sell {symbol}: {result['message']}")

            except Exception as e:
                logger.error(f"Error executing sell for {symbol}: {e}", exc_info=True)

    async def _execute_opportunity_buys(self, upgrade_changes: List[Dict]):
        """Execute buy opportunities for strong upgrade signals."""
        from core.paper_portfolio_manager import PaperPortfolioManager
        import requests

        portfolio_manager = PaperPortfolioManager()
        max_trades = self.config.get('execution', {}).get('max_trades_per_hour', 5)
        batch_buys_at_4pm = self.config.get('execution', {}).get('batch_buys_at_4pm', True)

        # If batch buys enabled, queue for 4 PM execution
        if batch_buys_at_4pm:
            logger.info(f"📋 Queuing {len(upgrade_changes)} buy opportunities for 4 PM batch execution")

            # Enqueue opportunities for 4 PM batch execution
            for change in upgrade_changes:
                self.buy_queue.enqueue(
                    symbol=change['symbol'],
                    score=change.get('new_score', 0),
                    signal=change.get('new_signal', 'HOLD'),
                    price=None,  # Will fetch at execution time
                    reason=change.get('reason', 'Signal upgrade detected')
                )

            logger.info(f"✅ Queued {len(upgrade_changes)} buy opportunities for 4 PM execution")
            return

        # Immediate execution mode
        trades_executed = 0

        for change in upgrade_changes:
            # Rate limiting
            if trades_executed >= max_trades:
                logger.warning(f"⚠️ Max trades per hour ({max_trades}) reached - deferring remaining buys")
                break

            symbol = change['symbol']

            # Skip if we already own this stock
            if symbol in portfolio_manager.positions:
                logger.debug(f"{symbol} already in portfolio - skipping buy")
                continue

            try:
                # Get current analysis
                response = requests.get(f"{self.base_url}/analyze/{symbol}", timeout=30)
                if response.status_code != 200:
                    logger.error(f"Failed to analyze {symbol}: {response.status_code}")
                    continue

                data = response.json()
                current_price = data.get('market_data', {}).get('current_price')
                current_score = data.get('overall_score', 0)
                recommendation = data.get('recommendation', 'HOLD')

                # Validate still meets buy criteria
                if recommendation not in ['STRONG BUY', 'BUY']:
                    logger.info(f"{symbol} no longer {recommendation} - skipping buy")
                    continue

                if current_score < 70.0:
                    logger.info(f"{symbol} score {current_score:.1f} below threshold - skipping buy")
                    continue

                if current_price is None or current_price <= 0:
                    logger.error(f"Invalid price for {symbol}: {current_price}")
                    continue

                # Calculate position size (score-weighted)
                portfolio_value = portfolio_manager.get_portfolio_value()
                position_size = self._calculate_position_size(
                    current_score,
                    portfolio_value,
                    current_price
                )

                if position_size is None or position_size <= 0:
                    logger.warning(f"Invalid position size for {symbol}: ${position_size}")
                    continue

                # Calculate shares to buy
                shares = int(position_size / current_price)

                if shares <= 0:
                    logger.warning(f"Calculated 0 shares for {symbol} - position too small")
                    continue

                # Check available cash
                total_cost = shares * current_price
                if total_cost > portfolio_manager.cash:
                    logger.warning(
                        f"Insufficient cash for {symbol}: need ${total_cost:.2f}, have ${portfolio_manager.cash:.2f}"
                    )
                    continue

                # Execute buy
                result = portfolio_manager.buy(symbol, shares, current_price)

                if result['success']:
                    logger.info(
                        f"🟢 BUY EXECUTED: {symbol} "
                        f"{change['previous_signal']} → {change['new_signal']} "
                        f"| {shares} shares @ ${current_price:.2f} "
                        f"| Total: ${total_cost:.2f} | Score: {current_score:.1f}"
                    )

                    # Mark action taken
                    change['action_taken'] = 'BUY'
                    change['execution_time'] = datetime.now().isoformat()
                    change['execution_price'] = current_price
                    change['shares_bought'] = shares

                    trades_executed += 1
                else:
                    logger.error(f"Failed to buy {symbol}: {result['message']}")

            except Exception as e:
                logger.error(f"Error executing buy for {symbol}: {e}", exc_info=True)

    def _calculate_position_size(self, score: float, portfolio_value: float, price: float) -> Optional[float]:
        """
        Calculate position size using score-weighted allocation.

        Higher scores get larger allocations:
        - Score 70: ~5% of portfolio
        - Score 80: ~8% of portfolio
        - Score 90: ~13% of portfolio
        """
        try:
            # Normalize score to 0-1 range (70-100 → 0-1)
            normalized_score = (score - 70) / 30
            normalized_score = max(0, min(1, normalized_score))

            # Exponential multiplier (0.5x to 1.5x)
            multiplier = 0.5 + (normalized_score ** 1.5)

            # Base allocation (10% of portfolio / 10 positions = 1% base)
            base_allocation = portfolio_value * 0.05

            # Apply multiplier
            position_size = base_allocation * multiplier

            # Respect max limits (15% of portfolio)
            max_position = portfolio_value * 0.15
            position_size = min(position_size, max_position)

            return position_size

        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return None

    def get_next_execution_time(self) -> Optional[str]:
        """Get next scheduled execution time."""
        if self.scheduler and self.is_running:
            job = self.scheduler.get_job('monitoring_cycle')
            if job and job.next_run_time:
                return job.next_run_time.isoformat()
        return None

    def get_status(self) -> dict:
        """Get monitoring scheduler status."""
        return {
            'is_running': self.is_running,
            'monitoring_enabled': self.config.get('monitoring', {}).get('enabled', True),
            'system_active': self.config.get('system_active', False),
            'next_execution': self.get_next_execution_time(),
            'configuration': {
                'portfolio_check_interval': f"{self.config.get('monitoring', {}).get('portfolio_check_interval_minutes', 30)} minutes",
                'watchlist_check_interval': f"{self.config.get('monitoring', {}).get('watchlist_check_interval_hours', 2)} hours",
                'market_hours_only': self.config.get('monitoring', {}).get('market_hours_only', True)
            }
        }

    async def trigger_manual_cycle(self) -> dict:
        """Manually trigger a monitoring cycle (for testing)."""
        logger.info("🔧 Manual monitoring cycle triggered")
        return await self.monitor.monitor_cycle()
