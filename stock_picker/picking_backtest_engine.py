"""
Stock Picking Backtest Engine
Tests portfolio selection strategy over historical data
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import logging

from .portfolio_manager import PortfolioManager
from .data_cache import DataCache, load_or_create_cache

logger = logging.getLogger(__name__)


class PickingBacktestEngine:
    """
    Backtest stock picking strategy with monthly/quarterly rebalancing
    """

    def __init__(self, initial_capital: float = 100000, sector_mapping: Dict = None):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.portfolio_manager = PortfolioManager(sector_mapping=sector_mapping)
        logger.info(f"PickingBacktestEngine initialized with ${initial_capital:,}")

    def run_backtest(self, universe: List[str], start_date: str, end_date: str,
                    rebalance_frequency: str = 'monthly', top_n: int = 20,
                    use_cache: bool = True) -> Dict:
        """
        Run backtest with periodic rebalancing

        Args:
            universe: List of stock symbols
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            rebalance_frequency: 'monthly' or 'quarterly'
            top_n: Number of stocks to hold
            use_cache: Use cached data (much faster)

        Returns:
            Backtest results dictionary
        """

        logger.info(f"Running backtest: {start_date} to {end_date}")
        logger.info(f"Universe: {len(universe)} stocks, Top {top_n}, Rebalance: {rebalance_frequency}")

        # Load or create cache
        cache = None
        if use_cache:
            print("\n📦 Loading/creating data cache...")
            cache = load_or_create_cache(universe, start_date, end_date)
            print()

        # Get price data (from cache or download)
        print(f"Loading price data for {len(universe)} stocks...")
        all_data = {}
        if cache:
            for symbol in universe:
                price_data = cache.get_price_data(symbol)
                if not price_data.empty:
                    all_data[symbol] = price_data
        else:
            for symbol in universe:
                try:
                    data = yf.download(symbol, start=start_date, end=end_date, progress=False)
                    if not data.empty:
                        all_data[symbol] = data
                except Exception as e:
                    logger.warning(f"Failed to download {symbol}: {e}")

        # Get SPY data
        if cache:
            spy_data = cache.get_price_data('SPY')
            if spy_data.empty:
                spy_data = yf.download('SPY', start=start_date, end=end_date, progress=False)
        else:
            spy_data = yf.download('SPY', start=start_date, end=end_date, progress=False)

        # Generate rebalance dates
        rebalance_dates = self._generate_rebalance_dates(
            start_date, end_date, rebalance_frequency
        )

        print(f"Rebalancing {len(rebalance_dates)} times ({rebalance_frequency})")

        # Run backtest
        portfolio = []
        portfolio_value = self.initial_capital
        equity_curve = []
        rebalance_log = []

        for i, rebalance_date in enumerate(rebalance_dates):
            print(f"\n[{i+1}/{len(rebalance_dates)}] Rebalance on {rebalance_date.date()}...")

            # Score all stocks based on data up to this date
            scores = self._score_universe_at_date(
                universe, all_data, spy_data, rebalance_date, cache
            )

            # Debug: show score distribution
            if scores:
                top_score = scores[0]['composite_score']
                bottom_score = scores[-1]['composite_score']
                print(f"  Scored {len(scores)} stocks (top: {top_score:.1f}, bottom: {bottom_score:.1f})")
            else:
                print(f"  WARNING: No stocks scored!")

            # Select top N stocks
            top_stocks = scores[:top_n]
            new_portfolio = [s['symbol'] for s in top_stocks]

            # Skip if no stocks selected
            if not new_portfolio:
                print(f"  WARNING: No stocks selected, skipping rebalance")
                continue

            # Calculate portfolio value before rebalance
            if portfolio:
                portfolio_value = self._calculate_portfolio_value(
                    portfolio, all_data, rebalance_date
                )

            # Equal weight allocation
            position_value = portfolio_value / len(new_portfolio)

            # Log rebalance
            rebalance_log.append({
                'date': str(rebalance_date.date()),
                'portfolio': new_portfolio,
                'portfolio_value': portfolio_value,
                'avg_score': np.mean([s['composite_score'] for s in top_stocks]),
                'holdings': [
                    {
                        'symbol': s['symbol'],
                        'score': s['composite_score'],
                        'category': s['rank_category']
                    }
                    for s in top_stocks
                ]
            })

            # Update portfolio
            portfolio = [
                {
                    'symbol': stock['symbol'],
                    'entry_price': self._get_price_at_date(all_data[stock['symbol']], rebalance_date),
                    'shares': position_value / self._get_price_at_date(all_data[stock['symbol']], rebalance_date),
                    'entry_date': rebalance_date
                }
                for stock in top_stocks
                if stock['symbol'] in all_data
            ]

            # Track equity curve daily until next rebalance
            if i < len(rebalance_dates) - 1:
                next_rebalance = rebalance_dates[i + 1]
            else:
                next_rebalance = pd.Timestamp(end_date)

            current_date = rebalance_date
            while current_date <= next_rebalance:
                pv = self._calculate_portfolio_value(portfolio, all_data, current_date)
                equity_curve.append({
                    'date': str(current_date.date()),
                    'value': pv,
                    'return': (pv - self.initial_capital) / self.initial_capital
                })
                current_date += timedelta(days=1)

            print(f"  Portfolio value: ${portfolio_value:,.0f} ({(portfolio_value/self.initial_capital - 1)*100:+.1f}%)")
            print(f"  Top holdings: {', '.join(new_portfolio[:5])}")

        # Final value
        final_value = equity_curve[-1]['value'] if equity_curve else self.initial_capital
        total_return = (final_value - self.initial_capital) / self.initial_capital

        # Calculate benchmark (equal weight buy-hold)
        benchmark_return = self._calculate_benchmark(universe, all_data, start_date, end_date)

        # Calculate SPY return
        spy_return = self._calculate_spy_return(spy_data)

        # Calculate metrics
        metrics = self._calculate_metrics(equity_curve)

        results = {
            'start_date': start_date,
            'end_date': end_date,
            'initial_capital': self.initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'benchmark_return': benchmark_return,
            'spy_return': spy_return,
            'outperformance_vs_benchmark': total_return - benchmark_return,
            'outperformance_vs_spy': total_return - spy_return,
            'rebalances': len(rebalance_dates),
            'metrics': metrics,
            'equity_curve': equity_curve,
            'rebalance_log': rebalance_log
        }

        print(f"\n" + "="*80)
        print(f"BACKTEST RESULTS")
        print(f"="*80)
        print(f"Strategy Return:       {total_return*100:>6.1f}%")
        print(f"Equal Weight Buy-Hold: {benchmark_return*100:>6.1f}%")
        print(f"SPY:                   {spy_return*100:>6.1f}%")
        print(f"\nvs Benchmark:  {(total_return - benchmark_return)*100:>+6.1f}% {'✅' if total_return > benchmark_return else '❌'}")
        print(f"vs SPY:        {(total_return - spy_return)*100:>+6.1f}% {'✅' if total_return > spy_return else '❌'}")
        print(f"\nSharpe Ratio:  {metrics['sharpe_ratio']:.2f}")
        print(f"Max Drawdown:  {metrics['max_drawdown']*100:.1f}%")
        print(f"Rebalances:    {len(rebalance_dates)}")

        return results

    def _generate_rebalance_dates(self, start: str, end: str, frequency: str) -> List[pd.Timestamp]:
        """Generate rebalance dates"""
        if frequency == 'monthly':
            # First day of each month
            dates = pd.date_range(start=start, end=end, freq='MS')  # Month Start
        elif frequency == 'quarterly':
            # First day of each quarter
            dates = pd.date_range(start=start, end=end, freq='QS')  # Quarter Start
        else:
            dates = pd.date_range(start=start, end=end, freq='MS')

        return list(dates)

    def _score_universe_at_date(self, universe: List[str], all_data: Dict,
                                spy_data: pd.DataFrame, date: pd.Timestamp,
                                cache: Optional[DataCache] = None) -> List[Dict]:
        """Score stocks using data up to date"""
        scores = []

        # Get data up to this date
        spy_window = spy_data.loc[:date]

        for symbol in universe:
            if symbol not in all_data:
                continue

            data_window = all_data[symbol].loc[:date]

            if len(data_window) < 50:  # Need minimum data
                continue

            try:
                # Get cached fundamental data
                cached_data = None
                if cache:
                    cached_data = {
                        'info': cache.get_info(symbol),
                        'financials': cache.get_financials(symbol),
                        'balance_sheet': cache.get_balance_sheet(symbol),
                        'cashflow': cache.get_cashflow(symbol),
                        'recommendations': cache.get_recommendations(symbol)
                    }

                score = self.portfolio_manager.scorer.score_stock(
                    symbol, data_window, spy_window, cached_data=cached_data
                )
                scores.append(score)
            except Exception as e:
                logger.warning(f"Failed to score {symbol} at {date}: {e}")

        # Sort by composite score
        scores.sort(key=lambda x: x['composite_score'], reverse=True)
        return scores

    def _get_price_at_date(self, data: pd.DataFrame, date: pd.Timestamp) -> float:
        """Get closing price at date"""
        try:
            if isinstance(data.columns, pd.MultiIndex):
                close = data['Close'].loc[:date].iloc[-1]
            else:
                close = data.loc[:date, 'Close'].iloc[-1]

            if isinstance(close, pd.Series):
                close = close.iloc[0]

            return float(close)
        except:
            return 0.0

    def _calculate_portfolio_value(self, portfolio: List[Dict], all_data: Dict,
                                   date: pd.Timestamp) -> float:
        """Calculate total portfolio value"""
        total_value = 0.0

        for holding in portfolio:
            symbol = holding['symbol']
            shares = holding['shares']

            if symbol in all_data:
                current_price = self._get_price_at_date(all_data[symbol], date)
                total_value += shares * current_price

        return total_value

    def _calculate_benchmark(self, universe: List[str], all_data: Dict,
                            start: str, end: str) -> float:
        """Calculate equal-weight buy-and-hold return"""
        returns = []

        for symbol in universe:
            if symbol not in all_data or all_data[symbol].empty:
                continue

            data = all_data[symbol]
            if len(data) < 2:
                continue

            first_price = self._get_price_at_date(data, pd.Timestamp(start))
            last_price = self._get_price_at_date(data, pd.Timestamp(end))

            if first_price > 0:
                ret = (last_price - first_price) / first_price
                returns.append(ret)

        return np.mean(returns) if returns else 0.0

    def _calculate_spy_return(self, spy_data: pd.DataFrame) -> float:
        """Calculate SPY return"""
        if spy_data.empty:
            return 0.0

        if isinstance(spy_data.columns, pd.MultiIndex):
            close = spy_data['Close'].values.flatten()
        else:
            close = spy_data['Close'].values

        return (close[-1] - close[0]) / close[0]

    def _calculate_metrics(self, equity_curve: List[Dict]) -> Dict:
        """Calculate performance metrics"""
        if not equity_curve:
            return {'sharpe_ratio': 0, 'max_drawdown': 0, 'volatility': 0}

        values = [point['value'] for point in equity_curve]
        returns = [point['return'] for point in equity_curve]

        # Daily returns
        daily_rets = np.diff(values) / values[:-1]

        # Sharpe ratio (annualized)
        if len(daily_rets) > 0 and np.std(daily_rets) > 0:
            sharpe = np.mean(daily_rets) / np.std(daily_rets) * np.sqrt(252)
        else:
            sharpe = 0

        # Max drawdown
        peak = values[0]
        max_dd = 0
        for value in values:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            if dd > max_dd:
                max_dd = dd

        # Volatility (annualized)
        volatility = np.std(daily_rets) * np.sqrt(252) if len(daily_rets) > 0 else 0

        return {
            'sharpe_ratio': sharpe,
            'max_drawdown': max_dd,
            'volatility': volatility
        }