"""
Trading Scheduler - Automated daily execution of paper trading system.

Executes trading cycle daily at 4 PM ET (market close) on weekdays.
"""

import logging
import json
import asyncio
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from .market_calendar import is_trading_day, get_next_trading_day

logger = logging.getLogger(__name__)

# Timezone for ET (Eastern Time)
ET_TIMEZONE = pytz.timezone('America/New_York')


class TradingScheduler:
    """
    Automated trading scheduler that executes paper trading cycle daily at 4 PM ET.

    Features:
    - Runs Mon-Fri at 4:00 PM ET (market close)
    - Skips weekends and NYSE holidays
    - Error handling with retry logic
    - Execution history tracking
    """

    def __init__(self, base_url: str = "http://localhost:8010"):
        """
        Initialize trading scheduler.

        Args:
            base_url: Base URL for API endpoints
        """
        self.base_url = base_url
        self.scheduler = AsyncIOScheduler(timezone=ET_TIMEZONE)
        self.execution_log_file = Path("data/execution_log.json")
        self.is_running = False

        # Ensure data directory exists
        self.execution_log_file.parent.mkdir(parents=True, exist_ok=True)

        # Load or initialize execution log
        self.execution_log = self._load_execution_log()

    def _load_execution_log(self) -> List[Dict]:
        """Load execution history from file."""
        if self.execution_log_file.exists():
            try:
                with open(self.execution_log_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load execution log: {e}")
                return []
        return []

    def _save_execution_log(self):
        """Save execution history to file."""
        try:
            # Keep only last 100 executions
            recent_log = self.execution_log[-100:]
            with open(self.execution_log_file, 'w') as f:
                json.dump(recent_log, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save execution log: {e}")

    def _log_execution(
        self,
        status: str,
        summary: Optional[Dict] = None,
        error: Optional[str] = None
    ):
        """
        Log execution details.

        Args:
            status: Execution status (success/failure/skipped)
            summary: Execution summary dict
            error: Error message if failed
        """
        log_entry = {
            'timestamp': datetime.now(ET_TIMEZONE).isoformat(),
            'status': status,
            'summary': summary or {},
            'error': error
        }

        self.execution_log.append(log_entry)
        self._save_execution_log()

        logger.info(f"Execution logged: {status} at {log_entry['timestamp']}")

    async def _execute_daily_trading(self):
        """
        Execute daily trading cycle at 4 PM ET.

        Steps:
        1. Check if market is open (skip holidays)
        2. Execute auto-sells first
        3. Execute auto-buys with freed capital
        4. Generate performance snapshot
        5. Log execution summary
        """
        execution_time = datetime.now(ET_TIMEZONE)
        logger.info(f"Starting daily trading execution at {execution_time}")

        # Check if it's a trading day
        if not is_trading_day(execution_time):
            logger.info(f"Skipping execution - not a trading day ({execution_time.date()})")
            self._log_execution('skipped', summary={'reason': 'Not a trading day'})
            return

        try:
            # Execute auto-trade cycle
            result = await self._execute_auto_trade_cycle()

            if result.get('success'):
                logger.info(f"Daily trading execution completed successfully")
                self._log_execution('success', summary=result.get('summary', {}))
            else:
                logger.error(f"Daily trading execution failed: {result.get('error')}")
                self._log_execution('failure', error=result.get('error'))

        except Exception as e:
            logger.error(f"Daily trading execution error: {str(e)}", exc_info=True)
            self._log_execution('failure', error=str(e))

            # Retry once after 5 minutes
            logger.info("Retrying execution in 5 minutes...")
            await asyncio.sleep(300)  # 5 minutes

            try:
                result = await self._execute_auto_trade_cycle()
                if result.get('success'):
                    logger.info("Retry successful")
                    self._log_execution('success_retry', summary=result.get('summary', {}))
                else:
                    logger.error(f"Retry failed: {result.get('error')}")
                    self._log_execution('failure_retry', error=result.get('error'))
            except Exception as retry_error:
                logger.error(f"Retry error: {str(retry_error)}", exc_info=True)
                self._log_execution('failure_retry', error=str(retry_error))

    async def _execute_auto_trade_cycle(self) -> Dict:
        """
        Execute the auto-trade cycle via API.

        Returns:
            Dict with success status and summary
        """
        try:
            # Process buy queue from monitoring system (if any)
            await self._process_buy_queue()

            # Call the unified auto-trade endpoint
            response = await asyncio.to_thread(
                requests.post,
                f"{self.base_url}/portfolio/paper/auto-trade",
                timeout=300  # 5 minute timeout
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'summary': result.get('summary', {}),
                    'sells': result.get('sells', {}),
                    'buys': result.get('buys', {})
                }
            else:
                return {
                    'success': False,
                    'error': f"API returned status {response.status_code}: {response.text}"
                }

        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': "API request timed out after 5 minutes"
            }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': "Could not connect to API server"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}"
            }

    async def _process_buy_queue(self):
        """
        Process queued buy opportunities from monitoring system.

        This method:
        1. Loads all queued opportunities from buy_queue.json
        2. Re-validates each opportunity (score check, signal check)
        3. Executes still-valid buy orders
        4. Clears the queue
        """
        try:
            from core.buy_queue_manager import BuyQueueManager

            buy_queue = BuyQueueManager()
            queued_opportunities = buy_queue.dequeue_all()

            if not queued_opportunities:
                logger.info("📋 No opportunities in buy queue")
                return

            logger.info(f"📋 Processing {len(queued_opportunities)} queued buy opportunities")

            # Get fresh analysis for all queued symbols
            symbols = [opp['symbol'] for opp in queued_opportunities]
            current_analyses = await self._get_current_analyses(symbols)

            # Validate and filter opportunities
            valid_opportunities = buy_queue.validate_and_filter(
                queued_opportunities,
                current_analyses
            )

            if not valid_opportunities:
                logger.info("✅ No valid opportunities after re-validation")
                return

            logger.info(f"✅ {len(valid_opportunities)} opportunities validated, executing buys...")

            # Execute valid buys
            for opp in valid_opportunities:
                try:
                    await self._execute_queued_buy(opp, current_analyses)
                except Exception as e:
                    logger.error(f"Error executing buy for {opp['symbol']}: {e}")

        except Exception as e:
            logger.error(f"Error processing buy queue: {e}", exc_info=True)

    async def _get_current_analyses(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        Get current analysis for multiple symbols.

        Args:
            symbols: List of symbols to analyze

        Returns:
            Dict mapping symbol -> analysis result
        """
        analyses = {}

        for symbol in symbols:
            try:
                response = await asyncio.to_thread(
                    requests.get,
                    f"{self.base_url}/analyze/{symbol}",
                    timeout=30
                )

                if response.status_code == 200:
                    analyses[symbol] = response.json()
                else:
                    logger.warning(f"Could not get analysis for {symbol}: {response.status_code}")

            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")

        return analyses

    async def _execute_queued_buy(self, opportunity: Dict, current_analyses: Dict):
        """
        Execute a single queued buy opportunity.

        Args:
            opportunity: Opportunity dict from queue
            current_analyses: Current analysis results
        """
        symbol = opportunity['symbol']
        queued_signal = opportunity['signal']
        queued_score = opportunity['score']

        # Get current analysis
        analysis = current_analyses.get(symbol)
        if not analysis:
            logger.warning(f"No current analysis for {symbol}, skipping")
            return

        current_price = analysis.get('market_data', {}).get('current_price')
        current_score = analysis.get('overall_score', 0)
        current_signal = analysis.get('recommendation', 'HOLD')

        if not current_price or current_price <= 0:
            logger.error(f"Invalid price for {symbol}: {current_price}")
            return

        # Execute buy via API
        try:
            from core.paper_portfolio_manager import PaperPortfolioManager
            portfolio_manager = PaperPortfolioManager()

            # Calculate position size
            portfolio_value = portfolio_manager.get_portfolio_value()
            position_size = self._calculate_position_size(current_score, portfolio_value, current_price)

            if position_size is None or position_size <= 0:
                logger.warning(f"Invalid position size for {symbol}: ${position_size}")
                return

            shares = int(position_size / current_price)

            if shares <= 0:
                logger.warning(f"Calculated 0 shares for {symbol} - position too small")
                return

            total_cost = shares * current_price

            if total_cost > portfolio_manager.cash:
                logger.warning(
                    f"Insufficient cash for {symbol}: need ${total_cost:.2f}, have ${portfolio_manager.cash:.2f}"
                )
                return

            # Execute buy
            result = portfolio_manager.buy(symbol, shares, current_price)

            if result['success']:
                logger.info(
                    f"🟢 QUEUED BUY EXECUTED: {symbol} "
                    f"{queued_signal} (queued) → {current_signal} (current) "
                    f"| {shares} shares @ ${current_price:.2f} "
                    f"| Total: ${total_cost:.2f} | Score: {queued_score:.1f}→{current_score:.1f}"
                )
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

    def start(self):
        """
        Start the trading scheduler.

        Schedules daily execution at 4:00 PM ET on weekdays.
        """
        if self.is_running:
            logger.warning("Scheduler is already running")
            return

        # Schedule daily execution at 4:00 PM ET, Mon-Fri
        self.scheduler.add_job(
            self._execute_daily_trading,
            CronTrigger(
                day_of_week='mon-fri',
                hour=16,
                minute=0,
                timezone=ET_TIMEZONE
            ),
            id='daily_trading_cycle',
            name='Daily Trading Cycle (4 PM ET)',
            replace_existing=True
        )

        self.scheduler.start()
        self.is_running = True

        next_run = self.get_next_execution_time()
        logger.info(f"Trading scheduler started - next execution at {next_run}")

    def stop(self):
        """Stop the trading scheduler."""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return

        self.scheduler.shutdown(wait=False)
        self.is_running = False
        logger.info("Trading scheduler stopped")

    def get_status(self) -> Dict:
        """
        Get scheduler status.

        Returns:
            Dict with status information
        """
        return {
            'is_running': self.is_running,
            'next_execution': self.get_next_execution_time(),
            'last_execution': self.get_last_execution(),
            'total_executions': len(self.execution_log),
            'recent_executions': self.execution_log[-5:] if self.execution_log else []
        }

    def get_next_execution_time(self) -> Optional[str]:
        """Get next scheduled execution time."""
        if not self.is_running:
            return None

        job = self.scheduler.get_job('daily_trading_cycle')
        if job and job.next_run_time:
            return job.next_run_time.isoformat()

        # Fallback: calculate next 4 PM ET on trading day
        now = datetime.now(ET_TIMEZONE)
        next_day = get_next_trading_day(now)
        next_execution = datetime.combine(next_day, datetime.min.time()).replace(
            hour=16, minute=0, second=0, microsecond=0, tzinfo=ET_TIMEZONE
        )

        # If today is a trading day and it's before 4 PM, use today
        if is_trading_day(now) and now.hour < 16:
            next_execution = now.replace(hour=16, minute=0, second=0, microsecond=0)

        return next_execution.isoformat()

    def get_last_execution(self) -> Optional[Dict]:
        """Get last execution details."""
        if self.execution_log:
            return self.execution_log[-1]
        return None

    def get_execution_history(self, limit: int = 50) -> List[Dict]:
        """
        Get recent execution history.

        Args:
            limit: Maximum number of records to return

        Returns:
            List of execution log entries
        """
        return self.execution_log[-limit:] if self.execution_log else []

    async def trigger_manual_execution(self) -> Dict:
        """
        Manually trigger a trading execution (for testing).

        Returns:
            Execution result
        """
        logger.info("Manual trading execution triggered")
        await self._execute_daily_trading()

        # Return last execution
        last_exec = self.get_last_execution()
        return last_exec if last_exec else {'status': 'unknown', 'error': 'No execution logged'}
