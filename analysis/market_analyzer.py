"""
Market Condition Analyzer
Detects market regimes and analyzes performance by condition
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class MarketCondition:
    """Market condition classification"""
    condition: str  # 'bull', 'bear', 'sideways', 'volatile', 'crisis'
    start_date: str
    end_date: str
    spy_return: float
    volatility: float
    max_drawdown: float
    description: str


class MarketConditionAnalyzer:
    """
    Analyzes market conditions and classifies regimes
    """

    # Known crisis periods
    CRISIS_PERIODS = {
        'COVID-19 Crash': ('2020-02-19', '2020-03-23'),
        'COVID-19 Recovery': ('2020-03-24', '2020-08-31'),
        '2022 Bear Market': ('2022-01-01', '2022-10-12'),
        'Banking Crisis': ('2023-03-01', '2023-03-31'),
    }

    def __init__(self, spy_data: pd.DataFrame):
        """
        Initialize with SPY benchmark data

        Args:
            spy_data: DataFrame with SPY OHLCV data
        """
        self.spy_data = spy_data
        self.spy_returns = spy_data['Close'].pct_change()

        logger.info(f"Initialized market analyzer with {len(spy_data)} days of SPY data")

    def classify_market_conditions(self, window: int = 60) -> List[MarketCondition]:
        """
        Classify market into different regimes

        Args:
            window: Rolling window for classification (days)

        Returns:
            List of market conditions
        """
        conditions = []

        # Calculate rolling metrics
        rolling_return = self.spy_data['Close'].pct_change(window)
        rolling_volatility = self.spy_returns.rolling(window).std() * np.sqrt(252)

        # Calculate drawdowns
        cumulative = (1 + self.spy_returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max

        # Classify each period
        dates = self.spy_data.index

        for i in range(window, len(dates), window // 2):  # Overlapping windows
            start_idx = max(0, i - window)
            end_idx = min(len(dates), i)

            if end_idx - start_idx < window // 2:
                continue

            period_return = rolling_return.iloc[end_idx - 1]
            period_vol = rolling_volatility.iloc[end_idx - 1]
            period_dd = drawdown.iloc[start_idx:end_idx].min()

            # Classification logic
            if period_dd < -0.15:  # Severe drawdown
                condition_type = 'crisis'
                description = f"Market crisis with {period_dd:.1%} drawdown"
            elif period_return > 0.10 and period_vol < 0.20:  # Strong uptrend, low vol
                condition_type = 'bull'
                description = f"Bull market: {period_return:.1%} return"
            elif period_return < -0.10:  # Significant decline
                condition_type = 'bear'
                description = f"Bear market: {period_return:.1%} return"
            elif period_vol > 0.30:  # High volatility
                condition_type = 'volatile'
                description = f"High volatility: {period_vol:.1%} annualized"
            else:  # Flat/choppy market
                condition_type = 'sideways'
                description = f"Sideways market: {period_return:.1%} return"

            condition = MarketCondition(
                condition=condition_type,
                start_date=dates[start_idx].strftime('%Y-%m-%d'),
                end_date=dates[end_idx - 1].strftime('%Y-%m-%d'),
                spy_return=float(period_return),
                volatility=float(period_vol),
                max_drawdown=float(period_dd),
                description=description
            )
            conditions.append(condition)

        return conditions

    def identify_crisis_periods(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Identify which crisis periods overlap with the backtest period

        Args:
            start_date: Backtest start date
            end_date: Backtest end date

        Returns:
            List of crisis periods that occurred during backtest
        """
        backtest_start = pd.to_datetime(start_date)
        backtest_end = pd.to_datetime(end_date)

        relevant_crises = []

        for crisis_name, (crisis_start, crisis_end) in self.CRISIS_PERIODS.items():
            crisis_start_dt = pd.to_datetime(crisis_start)
            crisis_end_dt = pd.to_datetime(crisis_end)

            # Check if crisis overlaps with backtest period
            if (crisis_start_dt <= backtest_end and crisis_end_dt >= backtest_start):
                # Calculate SPY performance during crisis
                crisis_data = self.spy_data[
                    (self.spy_data.index >= crisis_start_dt) &
                    (self.spy_data.index <= crisis_end_dt)
                ]

                if len(crisis_data) > 0:
                    crisis_return = (crisis_data['Close'].iloc[-1] / crisis_data['Close'].iloc[0]) - 1
                    crisis_vol = crisis_data['Close'].pct_change().std() * np.sqrt(252)

                    # Max drawdown during crisis
                    crisis_cumulative = (1 + crisis_data['Close'].pct_change()).cumprod()
                    crisis_running_max = crisis_cumulative.expanding().max()
                    crisis_dd = ((crisis_cumulative - crisis_running_max) / crisis_running_max).min()

                    relevant_crises.append({
                        'name': crisis_name,
                        'start_date': crisis_start,
                        'end_date': crisis_end,
                        'spy_return': float(crisis_return),
                        'volatility': float(crisis_vol),
                        'max_drawdown': float(crisis_dd),
                        'duration_days': len(crisis_data)
                    })

        return relevant_crises

    def analyze_yearly_performance(self, portfolio_returns: pd.Series, spy_returns: pd.Series) -> List[Dict]:
        """
        Analyze performance year by year

        Args:
            portfolio_returns: Portfolio daily returns
            spy_returns: SPY daily returns

        Returns:
            List of yearly performance metrics
        """
        yearly_stats = []

        # Align returns
        min_len = min(len(portfolio_returns), len(spy_returns))
        port_ret = portfolio_returns.iloc[:min_len]
        spy_ret = spy_returns.iloc[:min_len]

        # Group by year
        port_ret.index = pd.to_datetime(port_ret.index) if not isinstance(port_ret.index, pd.DatetimeIndex) else port_ret.index
        spy_ret.index = pd.to_datetime(spy_ret.index) if not isinstance(spy_ret.index, pd.DatetimeIndex) else spy_ret.index

        years = port_ret.index.year.unique()

        for year in sorted(years):
            year_port_ret = port_ret[port_ret.index.year == year]
            year_spy_ret = spy_ret[spy_ret.index.year == year]

            if len(year_port_ret) == 0:
                continue

            # Calculate metrics
            total_return_port = (1 + year_port_ret).prod() - 1
            total_return_spy = (1 + year_spy_ret).prod() - 1

            volatility_port = year_port_ret.std() * np.sqrt(252)
            volatility_spy = year_spy_ret.std() * np.sqrt(252)

            sharpe_port = (total_return_port - 0.02) / volatility_port if volatility_port > 0 else 0
            sharpe_spy = (total_return_spy - 0.02) / volatility_spy if volatility_spy > 0 else 0

            # Drawdown
            cum_ret = (1 + year_port_ret).cumprod()
            running_max = cum_ret.expanding().max()
            drawdown = ((cum_ret - running_max) / running_max).min()

            # Win rate
            win_rate = (year_port_ret > 0).sum() / len(year_port_ret)

            yearly_stats.append({
                'year': int(year),
                'portfolio_return': float(total_return_port),
                'spy_return': float(total_return_spy),
                'outperformance': float(total_return_port - total_return_spy),
                'portfolio_volatility': float(volatility_port),
                'spy_volatility': float(volatility_spy),
                'portfolio_sharpe': float(sharpe_port),
                'spy_sharpe': float(sharpe_spy),
                'max_drawdown': float(drawdown),
                'win_rate': float(win_rate),
                'trading_days': int(len(year_port_ret))
            })

        return yearly_stats

    def analyze_performance_by_regime(self,
                                     portfolio_returns: pd.Series,
                                     conditions: List[MarketCondition]) -> Dict[str, Dict]:
        """
        Analyze portfolio performance by market regime

        Args:
            portfolio_returns: Portfolio daily returns
            conditions: List of market conditions

        Returns:
            Dict of performance metrics by condition type
        """
        performance_by_regime = {}

        # Ensure portfolio returns has datetime index
        if not isinstance(portfolio_returns.index, pd.DatetimeIndex):
            portfolio_returns.index = pd.to_datetime(portfolio_returns.index)

        # Group conditions by type
        condition_types = {}
        for condition in conditions:
            if condition.condition not in condition_types:
                condition_types[condition.condition] = []
            condition_types[condition.condition].append(condition)

        # Calculate performance in each regime
        for regime, regime_conditions in condition_types.items():
            regime_returns = []

            for condition in regime_conditions:
                start = pd.to_datetime(condition.start_date)
                end = pd.to_datetime(condition.end_date)

                # Get returns in this period
                period_returns = portfolio_returns[
                    (portfolio_returns.index >= start) &
                    (portfolio_returns.index <= end)
                ]

                regime_returns.extend(period_returns.tolist())

            if len(regime_returns) > 0:
                regime_series = pd.Series(regime_returns)

                total_return = (1 + regime_series).prod() - 1
                avg_return = regime_series.mean()
                volatility = regime_series.std() * np.sqrt(252)
                sharpe = (avg_return * 252 - 0.02) / volatility if volatility > 0 else 0
                win_rate = (regime_series > 0).sum() / len(regime_series)

                performance_by_regime[regime] = {
                    'total_return': float(total_return),
                    'avg_daily_return': float(avg_return),
                    'annualized_return': float(avg_return * 252),
                    'volatility': float(volatility),
                    'sharpe_ratio': float(sharpe),
                    'win_rate': float(win_rate),
                    'num_days': int(len(regime_series)),
                    'num_periods': len(regime_conditions)
                }

        return performance_by_regime

    def get_current_regime(self, window: int = 60) -> Dict:
        """
        Determine current market regime

        Args:
            window: Lookback window in days

        Returns:
            Current market condition
        """
        if len(self.spy_data) < window:
            return {
                'regime': 'unknown',
                'description': 'Insufficient data',
                'confidence': 0.0
            }

        # Get recent data
        recent_data = self.spy_data.iloc[-window:]
        recent_return = (recent_data['Close'].iloc[-1] / recent_data['Close'].iloc[0]) - 1
        recent_vol = recent_data['Close'].pct_change().std() * np.sqrt(252)

        # Calculate drawdown
        cumulative = (1 + recent_data['Close'].pct_change()).cumprod()
        running_max = cumulative.expanding().max()
        current_dd = (cumulative.iloc[-1] - running_max.iloc[-1]) / running_max.iloc[-1]

        # Classify
        if current_dd < -0.15:
            regime = 'crisis'
            confidence = 0.9
            description = f"Crisis conditions: {current_dd:.1%} from peak"
        elif recent_return > 0.10 and recent_vol < 0.20:
            regime = 'bull'
            confidence = 0.8
            description = f"Bull market: +{recent_return:.1%} with low volatility"
        elif recent_return < -0.10:
            regime = 'bear'
            confidence = 0.8
            description = f"Bear market: {recent_return:.1%}"
        elif recent_vol > 0.30:
            regime = 'volatile'
            confidence = 0.7
            description = f"High volatility: {recent_vol:.1%}"
        else:
            regime = 'sideways'
            confidence = 0.6
            description = f"Range-bound: {recent_return:.1%}"

        return {
            'regime': regime,
            'description': description,
            'confidence': confidence,
            'return': float(recent_return),
            'volatility': float(recent_vol),
            'drawdown': float(current_dd),
            'window_days': window
        }


def analyze_stress_test_performance(portfolio_equity_curve: List[Dict],
                                   spy_data: pd.DataFrame,
                                   crisis_periods: List[Dict]) -> Dict:
    """
    Analyze portfolio performance during stress/crisis periods

    Args:
        portfolio_equity_curve: Portfolio values over time
        spy_data: SPY benchmark data
        crisis_periods: List of identified crisis periods

    Returns:
        Stress test results
    """
    stress_results = []

    # Convert equity curve to DataFrame
    equity_df = pd.DataFrame(portfolio_equity_curve)
    equity_df['date'] = pd.to_datetime(equity_df['date'])
    equity_df.set_index('date', inplace=True)

    for crisis in crisis_periods:
        crisis_start = pd.to_datetime(crisis['start_date'])
        crisis_end = pd.to_datetime(crisis['end_date'])

        # Get portfolio performance during crisis
        crisis_equity = equity_df[
            (equity_df.index >= crisis_start) &
            (equity_df.index <= crisis_end)
        ]

        if len(crisis_equity) > 1:
            crisis_return_port = (crisis_equity['value'].iloc[-1] / crisis_equity['value'].iloc[0]) - 1

            # Calculate max drawdown during crisis
            crisis_values = crisis_equity['value']
            running_max = crisis_values.expanding().max()
            drawdown = ((crisis_values - running_max) / running_max).min()

            # Recovery time
            bottom_date = crisis_equity['value'].idxmin()
            post_crisis = equity_df[equity_df.index > bottom_date]

            recovery_date = None
            pre_crisis_peak = crisis_equity['value'].iloc[0]

            for date, row in post_crisis.iterrows():
                if row['value'] >= pre_crisis_peak:
                    recovery_date = date
                    break

            recovery_days = (recovery_date - bottom_date).days if recovery_date else None

            stress_results.append({
                'crisis_name': crisis['name'],
                'start_date': crisis['start_date'],
                'end_date': crisis['end_date'],
                'portfolio_return': float(crisis_return_port),
                'spy_return': crisis['spy_return'],
                'outperformance': float(crisis_return_port - crisis['spy_return']),
                'max_drawdown': float(drawdown),
                'recovery_days': recovery_days,
                'duration_days': crisis['duration_days']
            })

    return {
        'stress_tests': stress_results,
        'avg_crisis_return': float(np.mean([s['portfolio_return'] for s in stress_results])) if stress_results else 0,
        'avg_outperformance': float(np.mean([s['outperformance'] for s in stress_results])) if stress_results else 0,
        'num_crises_tested': len(stress_results)
    }