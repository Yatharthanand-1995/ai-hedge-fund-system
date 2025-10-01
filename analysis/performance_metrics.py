"""
Performance Metrics Calculator
Comprehensive performance analysis utilities
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Complete set of performance metrics"""
    # Return metrics
    total_return: float
    cagr: float
    annualized_return: float
    avg_monthly_return: float
    avg_daily_return: float

    # Risk metrics
    volatility: float
    downside_deviation: float
    max_drawdown: float
    max_drawdown_duration: int
    current_drawdown: float

    # Risk-adjusted returns
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    information_ratio: float

    # Benchmark comparison
    beta: float
    alpha: float
    tracking_error: float
    correlation: float

    # Trading statistics
    win_rate: float
    profit_factor: float
    avg_win: float
    avg_loss: float
    best_day: float
    worst_day: float

    # Advanced metrics
    var_95: float  # Value at Risk (95%)
    cvar_95: float  # Conditional VaR
    ulcer_index: float
    kurtosis: float
    skewness: float


class PerformanceCalculator:
    """
    Calculate comprehensive performance metrics
    """

    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize calculator

        Args:
            risk_free_rate: Annual risk-free rate (default 2%)
        """
        self.risk_free_rate = risk_free_rate

    def calculate_all_metrics(self,
                             returns: pd.Series,
                             benchmark_returns: pd.Series,
                             equity_curve: Optional[pd.Series] = None) -> PerformanceMetrics:
        """
        Calculate all performance metrics

        Args:
            returns: Portfolio returns series
            benchmark_returns: Benchmark returns series
            equity_curve: Optional equity curve

        Returns:
            PerformanceMetrics object with all metrics
        """
        # Align returns
        min_len = min(len(returns), len(benchmark_returns))
        returns = returns.iloc[:min_len]
        benchmark_returns = benchmark_returns.iloc[:min_len]

        # Return metrics
        total_return = (1 + returns).prod() - 1
        years = len(returns) / 252  # Assuming daily returns
        cagr = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        annualized_return = returns.mean() * 252
        avg_monthly_return = returns.mean() * 21
        avg_daily_return = returns.mean()

        # Risk metrics
        volatility = returns.std() * np.sqrt(252)
        downside_returns = returns[returns < 0]
        downside_deviation = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0

        # Drawdown analysis
        if equity_curve is not None:
            dd_metrics = self._calculate_drawdown_metrics(equity_curve)
        else:
            cumulative = (1 + returns).cumprod()
            dd_metrics = self._calculate_drawdown_metrics(cumulative)

        max_drawdown = dd_metrics['max_drawdown']
        max_dd_duration = dd_metrics['max_duration']
        current_drawdown = dd_metrics['current_drawdown']

        # Risk-adjusted returns
        sharpe_ratio = (annualized_return - self.risk_free_rate) / volatility if volatility > 0 else 0

        sortino_ratio = (annualized_return - self.risk_free_rate) / downside_deviation if downside_deviation > 0 else 0

        calmar_ratio = cagr / abs(max_drawdown) if max_drawdown != 0 else 0

        # Information ratio
        excess_returns = returns - benchmark_returns
        tracking_error = excess_returns.std() * np.sqrt(252)
        information_ratio = excess_returns.mean() * 252 / tracking_error if tracking_error > 0 else 0

        # Benchmark comparison
        beta, alpha = self._calculate_beta_alpha(returns, benchmark_returns)
        correlation = returns.corr(benchmark_returns)

        # Trading statistics
        winning_returns = returns[returns > 0]
        losing_returns = returns[returns < 0]

        win_rate = len(winning_returns) / len(returns) if len(returns) > 0 else 0

        avg_win = winning_returns.mean() if len(winning_returns) > 0 else 0
        avg_loss = losing_returns.mean() if len(losing_returns) > 0 else 0

        total_wins = winning_returns.sum()
        total_losses = abs(losing_returns.sum())
        profit_factor = total_wins / total_losses if total_losses > 0 else 0

        best_day = returns.max()
        worst_day = returns.min()

        # Advanced risk metrics
        var_95 = self._calculate_var(returns, 0.95)
        cvar_95 = self._calculate_cvar(returns, 0.95)

        ulcer_index = self._calculate_ulcer_index(equity_curve if equity_curve is not None else (1 + returns).cumprod())

        kurtosis = returns.kurtosis()
        skewness = returns.skew()

        return PerformanceMetrics(
            total_return=float(total_return),
            cagr=float(cagr),
            annualized_return=float(annualized_return),
            avg_monthly_return=float(avg_monthly_return),
            avg_daily_return=float(avg_daily_return),
            volatility=float(volatility),
            downside_deviation=float(downside_deviation),
            max_drawdown=float(max_drawdown),
            max_drawdown_duration=int(max_dd_duration),
            current_drawdown=float(current_drawdown),
            sharpe_ratio=float(sharpe_ratio),
            sortino_ratio=float(sortino_ratio),
            calmar_ratio=float(calmar_ratio),
            information_ratio=float(information_ratio),
            beta=float(beta),
            alpha=float(alpha),
            tracking_error=float(tracking_error),
            correlation=float(correlation),
            win_rate=float(win_rate),
            profit_factor=float(profit_factor),
            avg_win=float(avg_win),
            avg_loss=float(avg_loss),
            best_day=float(best_day),
            worst_day=float(worst_day),
            var_95=float(var_95),
            cvar_95=float(cvar_95),
            ulcer_index=float(ulcer_index),
            kurtosis=float(kurtosis),
            skewness=float(skewness)
        )

    def _calculate_drawdown_metrics(self, cumulative_returns: pd.Series) -> Dict:
        """Calculate drawdown metrics"""
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max

        max_drawdown = drawdown.min()
        current_drawdown = drawdown.iloc[-1] if len(drawdown) > 0 else 0

        # Calculate max drawdown duration
        is_in_drawdown = drawdown < 0
        max_duration = 0
        current_duration = 0

        for in_dd in is_in_drawdown:
            if in_dd:
                current_duration += 1
                max_duration = max(max_duration, current_duration)
            else:
                current_duration = 0

        return {
            'max_drawdown': max_drawdown,
            'current_drawdown': current_drawdown,
            'max_duration': max_duration
        }

    def _calculate_beta_alpha(self, returns: pd.Series, benchmark_returns: pd.Series) -> tuple:
        """Calculate beta and alpha"""
        try:
            covariance = np.cov(returns, benchmark_returns)[0, 1]
            benchmark_variance = np.var(benchmark_returns)
            beta = covariance / benchmark_variance if benchmark_variance > 0 else 1.0

            # Alpha = Portfolio Return - (Risk Free + Beta * (Benchmark Return - Risk Free))
            portfolio_return = returns.mean() * 252
            benchmark_return = benchmark_returns.mean() * 252
            alpha = portfolio_return - (self.risk_free_rate + beta * (benchmark_return - self.risk_free_rate))

            return beta, alpha
        except:
            return 1.0, 0.0

    def _calculate_var(self, returns: pd.Series, confidence: float) -> float:
        """Calculate Value at Risk"""
        return returns.quantile(1 - confidence)

    def _calculate_cvar(self, returns: pd.Series, confidence: float) -> float:
        """Calculate Conditional Value at Risk (Expected Shortfall)"""
        var = self._calculate_var(returns, confidence)
        return returns[returns <= var].mean()

    def _calculate_ulcer_index(self, cumulative_returns: pd.Series) -> float:
        """Calculate Ulcer Index (Peter Martin 1987)"""
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max * 100  # Convert to percentage

        # Ulcer Index is RMS of drawdown
        ulcer = np.sqrt(np.mean(drawdown ** 2))
        return ulcer

    def calculate_rolling_metrics(self,
                                  returns: pd.Series,
                                  window: int = 252) -> Dict[str, pd.Series]:
        """
        Calculate rolling performance metrics

        Args:
            returns: Return series
            window: Rolling window size (default 252 days = 1 year)

        Returns:
            Dict of rolling metric series
        """
        rolling_metrics = {}

        # Rolling returns
        rolling_metrics['rolling_return'] = (1 + returns).rolling(window).apply(lambda x: x.prod() - 1, raw=True)

        # Rolling volatility
        rolling_metrics['rolling_volatility'] = returns.rolling(window).std() * np.sqrt(252)

        # Rolling Sharpe
        rolling_mean = returns.rolling(window).mean() * 252
        rolling_std = returns.rolling(window).std() * np.sqrt(252)
        rolling_metrics['rolling_sharpe'] = (rolling_mean - self.risk_free_rate) / rolling_std

        # Rolling max drawdown
        cumulative = (1 + returns).cumprod()
        rolling_metrics['rolling_max_dd'] = cumulative.rolling(window).apply(
            lambda x: ((x - x.expanding().max()) / x.expanding().max()).min(),
            raw=True
        )

        return rolling_metrics

    def compare_strategies(self,
                          strategy_returns: Dict[str, pd.Series],
                          benchmark_returns: pd.Series) -> pd.DataFrame:
        """
        Compare multiple strategies

        Args:
            strategy_returns: Dict of strategy name -> returns series
            benchmark_returns: Benchmark returns

        Returns:
            DataFrame comparing all strategies
        """
        comparison = []

        for name, returns in strategy_returns.items():
            metrics = self.calculate_all_metrics(returns, benchmark_returns)

            comparison.append({
                'Strategy': name,
                'Total Return': metrics.total_return,
                'CAGR': metrics.cagr,
                'Sharpe Ratio': metrics.sharpe_ratio,
                'Sortino Ratio': metrics.sortino_ratio,
                'Max Drawdown': metrics.max_drawdown,
                'Volatility': metrics.volatility,
                'Win Rate': metrics.win_rate,
                'Beta': metrics.beta,
                'Alpha': metrics.alpha
            })

        return pd.DataFrame(comparison)


def format_metrics_for_display(metrics: PerformanceMetrics) -> Dict:
    """Format metrics for human-readable display"""
    return {
        'Returns': {
            'Total Return': f"{metrics.total_return:.2%}",
            'CAGR': f"{metrics.cagr:.2%}",
            'Annualized Return': f"{metrics.annualized_return:.2%}",
            'Avg Monthly Return': f"{metrics.avg_monthly_return:.2%}",
            'Avg Daily Return': f"{metrics.avg_daily_return:.4%}",
        },
        'Risk': {
            'Volatility (Annual)': f"{metrics.volatility:.2%}",
            'Downside Deviation': f"{metrics.downside_deviation:.2%}",
            'Max Drawdown': f"{metrics.max_drawdown:.2%}",
            'Max DD Duration': f"{metrics.max_drawdown_duration} days",
            'Current Drawdown': f"{metrics.current_drawdown:.2%}",
            'Value at Risk (95%)': f"{metrics.var_95:.2%}",
            'CVaR (95%)': f"{metrics.cvar_95:.2%}",
            'Ulcer Index': f"{metrics.ulcer_index:.2f}",
        },
        'Risk-Adjusted Returns': {
            'Sharpe Ratio': f"{metrics.sharpe_ratio:.2f}",
            'Sortino Ratio': f"{metrics.sortino_ratio:.2f}",
            'Calmar Ratio': f"{metrics.calmar_ratio:.2f}",
            'Information Ratio': f"{metrics.information_ratio:.2f}",
        },
        'Benchmark Comparison': {
            'Beta': f"{metrics.beta:.2f}",
            'Alpha': f"{metrics.alpha:.2%}",
            'Tracking Error': f"{metrics.tracking_error:.2%}",
            'Correlation': f"{metrics.correlation:.2f}",
        },
        'Trading Statistics': {
            'Win Rate': f"{metrics.win_rate:.2%}",
            'Profit Factor': f"{metrics.profit_factor:.2f}",
            'Average Win': f"{metrics.avg_win:.2%}",
            'Average Loss': f"{metrics.avg_loss:.2%}",
            'Best Day': f"{metrics.best_day:.2%}",
            'Worst Day': f"{metrics.worst_day:.2%}",
        },
        'Distribution': {
            'Skewness': f"{metrics.skewness:.2f}",
            'Kurtosis': f"{metrics.kurtosis:.2f}",
        }
    }