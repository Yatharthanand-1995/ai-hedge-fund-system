"""
Drawdown Monitor
Tracks portfolio drawdowns and recovery metrics
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DrawdownMonitor:
    """
    Monitor portfolio drawdowns and recovery

    Metrics:
    1. Current drawdown from peak
    2. Maximum drawdown
    3. Drawdown duration
    4. Recovery time estimation
    5. Historical drawdown distribution
    """

    def __init__(self):
        """Initialize drawdown monitor"""
        self.alert_thresholds = {
            'warning': 0.20,  # 20% drawdown
            'moderate': 0.30,  # 30% drawdown
            'severe': 0.40,   # 40% drawdown
        }
        logger.info("DrawdownMonitor initialized")

    def calculate_drawdown_series(self, portfolio_values: pd.Series) -> pd.Series:
        """
        Calculate drawdown series (% from peak)

        Args:
            portfolio_values: Series of portfolio values over time

        Returns:
            Series of drawdown percentages (negative values)
        """
        try:
            # Calculate running maximum
            running_max = portfolio_values.expanding().max()

            # Calculate drawdown
            drawdown = (portfolio_values - running_max) / running_max

            return drawdown

        except Exception as e:
            logger.error(f"Drawdown series calculation failed: {e}")
            return pd.Series()

    def calculate_max_drawdown(self, portfolio_values: pd.Series) -> Dict:
        """
        Calculate maximum drawdown metrics

        Args:
            portfolio_values: Series of portfolio values

        Returns:
            {
                'max_drawdown': float,
                'peak_value': float,
                'trough_value': float,
                'peak_date': str,
                'trough_date': str,
                'duration_days': int,
                'recovery_date': str or None
            }
        """
        try:
            # Calculate drawdown series
            drawdown_series = self.calculate_drawdown_series(portfolio_values)

            if len(drawdown_series) == 0:
                return {'error': 'No data'}

            # Find maximum drawdown
            max_dd_idx = drawdown_series.idxmin()
            max_dd = drawdown_series.min()

            # Find peak before drawdown
            values_before_trough = portfolio_values[:max_dd_idx]
            peak_idx = values_before_trough.idxmax()

            # Get values
            peak_value = portfolio_values[peak_idx]
            trough_value = portfolio_values[max_dd_idx]

            # Calculate duration
            if isinstance(peak_idx, pd.Timestamp) and isinstance(max_dd_idx, pd.Timestamp):
                duration = (max_dd_idx - peak_idx).days
            else:
                duration = max_dd_idx - peak_idx

            # Check for recovery
            values_after_trough = portfolio_values[max_dd_idx:]
            recovered = values_after_trough >= peak_value

            if recovered.any():
                recovery_idx = values_after_trough[recovered].index[0]
                recovery_date = str(recovery_idx)
                if isinstance(recovery_idx, pd.Timestamp) and isinstance(max_dd_idx, pd.Timestamp):
                    recovery_duration = (recovery_idx - max_dd_idx).days
                else:
                    recovery_duration = recovery_idx - max_dd_idx
            else:
                recovery_date = None
                recovery_duration = None

            return {
                'max_drawdown': float(max_dd),
                'max_drawdown_pct': float(max_dd * 100),
                'peak_value': float(peak_value),
                'trough_value': float(trough_value),
                'peak_date': str(peak_idx),
                'trough_date': str(max_dd_idx),
                'duration_days': int(duration) if duration else None,
                'recovery_date': recovery_date,
                'recovery_duration_days': int(recovery_duration) if recovery_duration else None,
                'is_recovered': recovery_date is not None
            }

        except Exception as e:
            logger.error(f"Max drawdown calculation failed: {e}")
            return {'error': str(e)}

    def calculate_current_drawdown(self, portfolio_values: pd.Series) -> Dict:
        """
        Calculate current drawdown from peak

        Args:
            portfolio_values: Series of portfolio values

        Returns:
            {
                'current_drawdown': float,
                'peak_value': float,
                'current_value': float,
                'days_in_drawdown': int,
                'alert_level': str
            }
        """
        try:
            if len(portfolio_values) == 0:
                return {'error': 'No data'}

            # Current value and peak
            current_value = portfolio_values.iloc[-1]
            peak_value = portfolio_values.max()
            current_drawdown = (current_value - peak_value) / peak_value

            # Find when peak occurred
            peak_idx = portfolio_values.idxmax()
            current_idx = portfolio_values.index[-1]

            if isinstance(peak_idx, pd.Timestamp) and isinstance(current_idx, pd.Timestamp):
                days_in_drawdown = (current_idx - peak_idx).days
            else:
                days_in_drawdown = current_idx - peak_idx

            # Determine alert level
            dd_abs = abs(current_drawdown)
            if dd_abs >= self.alert_thresholds['severe']:
                alert_level = 'SEVERE'
            elif dd_abs >= self.alert_thresholds['moderate']:
                alert_level = 'MODERATE'
            elif dd_abs >= self.alert_thresholds['warning']:
                alert_level = 'WARNING'
            else:
                alert_level = 'NORMAL'

            return {
                'current_drawdown': float(current_drawdown),
                'current_drawdown_pct': float(current_drawdown * 100),
                'peak_value': float(peak_value),
                'current_value': float(current_value),
                'peak_date': str(peak_idx),
                'days_in_drawdown': int(days_in_drawdown) if days_in_drawdown else 0,
                'alert_level': alert_level
            }

        except Exception as e:
            logger.error(f"Current drawdown calculation failed: {e}")
            return {'error': str(e)}

    def analyze_drawdown_distribution(self, portfolio_values: pd.Series) -> Dict:
        """
        Analyze historical drawdown distribution

        Args:
            portfolio_values: Series of portfolio values

        Returns:
            {
                'mean_drawdown': float,
                'median_drawdown': float,
                'drawdown_percentiles': dict,
                'num_drawdowns': int,
                'avg_duration': float
            }
        """
        try:
            # Calculate drawdown series
            drawdown_series = self.calculate_drawdown_series(portfolio_values)

            if len(drawdown_series) == 0:
                return {'error': 'No data'}

            # Only consider negative drawdowns
            negative_drawdowns = drawdown_series[drawdown_series < 0]

            if len(negative_drawdowns) == 0:
                return {
                    'mean_drawdown': 0.0,
                    'median_drawdown': 0.0,
                    'num_drawdowns': 0
                }

            # Calculate statistics
            mean_dd = negative_drawdowns.mean()
            median_dd = negative_drawdowns.median()

            # Percentiles
            percentiles = {
                '10th': float(negative_drawdowns.quantile(0.10)),
                '25th': float(negative_drawdowns.quantile(0.25)),
                '50th': float(negative_drawdowns.quantile(0.50)),
                '75th': float(negative_drawdowns.quantile(0.75)),
                '90th': float(negative_drawdowns.quantile(0.90)),
                '95th': float(negative_drawdowns.quantile(0.95))
            }

            # Count distinct drawdown periods
            in_drawdown = drawdown_series < 0
            drawdown_periods = (in_drawdown != in_drawdown.shift()).cumsum()[in_drawdown]
            num_drawdowns = drawdown_periods.nunique() if len(drawdown_periods) > 0 else 0

            return {
                'mean_drawdown': float(mean_dd),
                'mean_drawdown_pct': float(mean_dd * 100),
                'median_drawdown': float(median_dd),
                'median_drawdown_pct': float(median_dd * 100),
                'drawdown_percentiles': percentiles,
                'num_drawdowns': int(num_drawdowns),
                'total_days_in_drawdown': int(len(negative_drawdowns))
            }

        except Exception as e:
            logger.error(f"Drawdown distribution analysis failed: {e}")
            return {'error': str(e)}

    def estimate_recovery_time(self, portfolio_values: pd.Series,
                              target_return: float = 0.10) -> Dict:
        """
        Estimate time to recover from current drawdown

        Args:
            portfolio_values: Series of portfolio values
            target_return: Expected annual return (default 10%)

        Returns:
            {
                'estimated_days': int,
                'estimated_value': float,
                'assumed_return': float
            }
        """
        try:
            current_dd = self.calculate_current_drawdown(portfolio_values)

            if 'error' in current_dd:
                return current_dd

            current_value = current_dd['current_value']
            peak_value = current_dd['peak_value']
            dd_pct = abs(current_dd['current_drawdown'])

            if dd_pct < 0.01:  # Less than 1% drawdown
                return {
                    'estimated_days': 0,
                    'message': 'No significant drawdown'
                }

            # Calculate daily return needed
            daily_return = (1 + target_return) ** (1/252) - 1  # 252 trading days

            # Days to recover = log(peak/current) / log(1 + daily_return)
            days_to_recover = np.log(peak_value / current_value) / np.log(1 + daily_return)

            return {
                'estimated_days': int(days_to_recover),
                'estimated_months': round(days_to_recover / 21, 1),  # ~21 trading days/month
                'estimated_value': float(peak_value),
                'current_value': float(current_value),
                'assumed_daily_return': float(daily_return * 100),
                'assumed_annual_return': float(target_return * 100)
            }

        except Exception as e:
            logger.error(f"Recovery time estimation failed: {e}")
            return {'error': str(e)}

    def get_drawdown_summary(self, portfolio_values: pd.Series) -> Dict:
        """
        Get comprehensive drawdown summary

        Args:
            portfolio_values: Series of portfolio values

        Returns:
            Complete drawdown analysis
        """
        try:
            return {
                'max_drawdown': self.calculate_max_drawdown(portfolio_values),
                'current_drawdown': self.calculate_current_drawdown(portfolio_values),
                'distribution': self.analyze_drawdown_distribution(portfolio_values),
                'recovery_estimate': self.estimate_recovery_time(portfolio_values),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Drawdown summary generation failed: {e}")
            return {'error': str(e)}