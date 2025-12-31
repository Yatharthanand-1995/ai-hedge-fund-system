"""
Performance Dashboard for Automated Trading System

Tracks and evaluates system performance:
- Daily portfolio snapshots
- Return metrics (total, CAGR, vs SPY)
- Risk metrics (Sharpe, Sortino, max drawdown)
- Trading statistics (win rate, avg holding period)
- Best/worst trades analysis
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np

logger = logging.getLogger(__name__)


class PerformanceDashboard:
    """Track and evaluate automated trading system performance."""

    SNAPSHOTS_FILE = "data/daily_snapshots.json"
    TRADE_ANALYSIS_FILE = "data/trade_analysis.json"

    def __init__(self):
        """Initialize performance dashboard."""
        self.snapshots_file = Path(self.SNAPSHOTS_FILE)
        self.trade_analysis_file = Path(self.TRADE_ANALYSIS_FILE)

        # Ensure data directory exists
        self.snapshots_file.parent.mkdir(parents=True, exist_ok=True)

    def record_daily_snapshot(
        self,
        portfolio_value: float,
        cash: float,
        num_positions: int,
        spy_price: float,
        regime: Optional[str] = None
    ) -> None:
        """
        Record daily portfolio state for tracking.

        Args:
            portfolio_value: Total portfolio value
            cash: Available cash
            num_positions: Number of open positions
            spy_price: SPY ETF price for benchmark comparison
            regime: Current market regime (e.g., 'BULL_NORMAL_VOL')
        """
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'portfolio_value': portfolio_value,
            'cash': cash,
            'num_positions': num_positions,
            'spy_price': spy_price,
            'regime': regime or 'UNKNOWN'
        }

        # Load existing snapshots
        snapshots = self._load_snapshots()

        # Append new snapshot
        snapshots.append(snapshot)

        # Keep only last 365 days
        snapshots = snapshots[-365:]

        # Save back to file
        with open(self.snapshots_file, 'w') as f:
            json.dump(snapshots, f, indent=2)

        logger.info(f"Recorded daily snapshot: ${portfolio_value:,.2f} ({num_positions} positions)")

    def _load_snapshots(self) -> List[Dict]:
        """Load daily snapshots from file."""
        if self.snapshots_file.exists():
            with open(self.snapshots_file, 'r') as f:
                return json.load(f)
        return []

    def calculate_metrics(self, days: int = 30) -> Dict:
        """
        Calculate performance metrics over specified period.

        Args:
            days: Number of days to analyze (default: 30)

        Returns:
            Dict with comprehensive performance metrics
        """
        snapshots = self._load_snapshots()

        if len(snapshots) < 2:
            return {
                'error': 'Insufficient data',
                'message': 'Need at least 2 daily snapshots to calculate metrics'
            }

        # Get recent snapshots
        recent_snapshots = snapshots[-days:] if len(snapshots) >= days else snapshots

        # Calculate returns
        portfolio_return = self._calculate_portfolio_return(recent_snapshots)
        spy_return = self._calculate_spy_return(recent_snapshots)
        outperformance = portfolio_return - spy_return

        # Calculate risk metrics
        sharpe_ratio = self._calculate_sharpe(recent_snapshots)
        max_drawdown = self._calculate_max_drawdown(recent_snapshots)

        # Get trading statistics
        trade_stats = self._get_trade_statistics()

        # Current values
        latest = recent_snapshots[-1]

        return {
            'period_days': len(recent_snapshots),
            'start_date': recent_snapshots[0]['date'],
            'end_date': recent_snapshots[-1]['date'],

            # Portfolio metrics
            'current_value': latest['portfolio_value'],
            'current_cash': latest['cash'],
            'num_positions': latest['num_positions'],
            'current_regime': latest.get('regime', 'UNKNOWN'),

            # Return metrics
            'portfolio_return': portfolio_return,
            'spy_return': spy_return,
            'outperformance': outperformance,

            # Risk metrics
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,

            # Trading metrics
            'total_trades': trade_stats.get('total_trades', 0),
            'win_rate': trade_stats.get('win_rate', 0.0),
            'avg_holding_period': trade_stats.get('avg_holding_period', 0),
            'best_trade': trade_stats.get('best_trade', {}),
            'worst_trade': trade_stats.get('worst_trade', {})
        }

    def _calculate_portfolio_return(self, snapshots: List[Dict]) -> float:
        """Calculate portfolio return percentage."""
        if len(snapshots) < 2:
            return 0.0

        start_value = snapshots[0]['portfolio_value']
        end_value = snapshots[-1]['portfolio_value']

        if start_value == 0:
            return 0.0

        return ((end_value - start_value) / start_value) * 100

    def _calculate_spy_return(self, snapshots: List[Dict]) -> float:
        """Calculate SPY benchmark return percentage."""
        if len(snapshots) < 2:
            return 0.0

        start_spy = snapshots[0]['spy_price']
        end_spy = snapshots[-1]['spy_price']

        if start_spy == 0:
            return 0.0

        return ((end_spy - start_spy) / start_spy) * 100

    def _calculate_sharpe(self, snapshots: List[Dict]) -> float:
        """Calculate Sharpe ratio (annualized)."""
        if len(snapshots) < 2:
            return 0.0

        # Calculate daily returns
        daily_returns = []
        for i in range(1, len(snapshots)):
            prev_value = snapshots[i-1]['portfolio_value']
            curr_value = snapshots[i]['portfolio_value']

            if prev_value > 0:
                daily_return = (curr_value - prev_value) / prev_value
                daily_returns.append(daily_return)

        if len(daily_returns) == 0:
            return 0.0

        # Calculate mean and std
        mean_return = np.mean(daily_returns)
        std_return = np.std(daily_returns)

        if std_return == 0:
            return 0.0

        # Annualize (252 trading days)
        sharpe = (mean_return / std_return) * np.sqrt(252)

        return float(sharpe)

    def _calculate_max_drawdown(self, snapshots: List[Dict]) -> float:
        """Calculate maximum drawdown percentage."""
        if len(snapshots) < 2:
            return 0.0

        values = [s['portfolio_value'] for s in snapshots]
        peak = values[0]
        max_dd = 0.0

        for value in values:
            if value > peak:
                peak = value

            drawdown = ((value - peak) / peak) * 100 if peak > 0 else 0.0

            if drawdown < max_dd:
                max_dd = drawdown

        return float(max_dd)

    def _get_trade_statistics(self) -> Dict:
        """Get trading statistics from transaction log."""
        # Load transaction log
        transaction_file = Path("data/transaction_log.json")

        if not transaction_file.exists():
            return {
                'total_trades': 0,
                'win_rate': 0.0,
                'avg_holding_period': 0,
                'best_trade': {},
                'worst_trade': {}
            }

        with open(transaction_file, 'r') as f:
            transactions = json.load(f)

        # Find completed trades (buy + sell pairs)
        completed_trades = self._find_completed_trades(transactions)

        if len(completed_trades) == 0:
            return {
                'total_trades': 0,
                'win_rate': 0.0,
                'avg_holding_period': 0,
                'best_trade': {},
                'worst_trade': {}
            }

        # Calculate statistics
        winning_trades = [t for t in completed_trades if t['pnl_percent'] > 0]
        win_rate = (len(winning_trades) / len(completed_trades)) * 100

        # Average holding period
        holding_periods = [t['holding_days'] for t in completed_trades if 'holding_days' in t]
        avg_holding = int(np.mean(holding_periods)) if holding_periods else 0

        # Best and worst trades
        best_trade = max(completed_trades, key=lambda t: t['pnl_percent'])
        worst_trade = min(completed_trades, key=lambda t: t['pnl_percent'])

        return {
            'total_trades': len(completed_trades),
            'win_rate': round(win_rate, 1),
            'avg_holding_period': avg_holding,
            'best_trade': {
                'symbol': best_trade['symbol'],
                'pnl_percent': round(best_trade['pnl_percent'], 2),
                'holding_days': best_trade.get('holding_days', 0)
            },
            'worst_trade': {
                'symbol': worst_trade['symbol'],
                'pnl_percent': round(worst_trade['pnl_percent'], 2),
                'holding_days': worst_trade.get('holding_days', 0)
            }
        }

    def _find_completed_trades(self, transactions: List[Dict]) -> List[Dict]:
        """Find completed buy/sell pairs from transaction log."""
        # Group transactions by symbol
        by_symbol = {}
        for txn in transactions:
            symbol = txn.get('symbol')
            if symbol:
                if symbol not in by_symbol:
                    by_symbol[symbol] = []
                by_symbol[symbol].append(txn)

        completed_trades = []

        for symbol, txns in by_symbol.items():
            # Sort by timestamp
            txns.sort(key=lambda t: t.get('timestamp', ''))

            # Find buy/sell pairs
            buys = [t for t in txns if t.get('action') == 'buy']
            sells = [t for t in txns if t.get('action') == 'sell']

            # Match buys with sells (FIFO)
            for buy in buys:
                if len(sells) == 0:
                    break

                sell = sells.pop(0)

                # Calculate P&L
                buy_price = buy.get('price', 0)
                sell_price = sell.get('price', 0)

                if buy_price > 0:
                    pnl_percent = ((sell_price - buy_price) / buy_price) * 100

                    # Calculate holding period
                    try:
                        buy_time = datetime.fromisoformat(buy['timestamp'])
                        sell_time = datetime.fromisoformat(sell['timestamp'])
                        holding_days = (sell_time - buy_time).days
                    except:
                        holding_days = 0

                    completed_trades.append({
                        'symbol': symbol,
                        'buy_price': buy_price,
                        'sell_price': sell_price,
                        'pnl_percent': pnl_percent,
                        'holding_days': holding_days
                    })

        return completed_trades

    def generate_report(self, days: int = 30) -> str:
        """
        Generate formatted daily performance report.

        Args:
            days: Number of days to analyze (default: 30)

        Returns:
            Formatted string report
        """
        metrics = self.calculate_metrics(days=days)

        if 'error' in metrics:
            return f"""
╔════════════════════════════════════════════════════════╗
║      AUTOMATED TRADING DAILY REPORT                    ║
║      {datetime.now().strftime('%Y-%m-%d %H:%M %Z')}                         ║
╚════════════════════════════════════════════════════════╝

⚠️  INSUFFICIENT DATA

{metrics['message']}

Record daily snapshots to enable performance tracking.
"""

        report = f"""
╔════════════════════════════════════════════════════════╗
║      AUTOMATED TRADING DAILY REPORT                    ║
║      {datetime.now().strftime('%Y-%m-%d %H:%M %Z')}                         ║
╚════════════════════════════════════════════════════════╝

PORTFOLIO OVERVIEW
Total Value:        ${metrics['current_value']:,.2f}
Cash Available:     ${metrics['current_cash']:,.2f}
Open Positions:     {metrics['num_positions']}
Market Regime:      {metrics['current_regime']}

PERFORMANCE ({metrics['period_days']} Days: {metrics['start_date']} to {metrics['end_date']})
Portfolio Return:   {metrics['portfolio_return']:+.2f}%
SPY Return:         {metrics['spy_return']:+.2f}%
Outperformance:     {metrics['outperformance']:+.2f}%

RISK METRICS
Sharpe Ratio:       {metrics['sharpe_ratio']:.2f}
Max Drawdown:       {metrics['max_drawdown']:.2f}%

TRADING STATISTICS
Total Trades:       {metrics['total_trades']}
Win Rate:           {metrics['win_rate']:.1f}%
Avg Holding:        {metrics['avg_holding_period']} days
"""

        if metrics['best_trade']:
            report += f"""
Best Trade:         {metrics['best_trade']['symbol']} ({metrics['best_trade']['pnl_percent']:+.2f}%, {metrics['best_trade']['holding_days']} days)
Worst Trade:        {metrics['worst_trade']['symbol']} ({metrics['worst_trade']['pnl_percent']:+.2f}%, {metrics['worst_trade']['holding_days']} days)
"""

        report += """
════════════════════════════════════════════════════════
"""

        return report
