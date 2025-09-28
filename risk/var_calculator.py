"""
Value at Risk (VaR) Calculator
Calculates portfolio risk using multiple methods
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class VaRCalculator:
    """
    Calculate Value at Risk using multiple methodologies

    Methods:
    1. Historical VaR - Based on historical returns distribution
    2. Parametric VaR - Assumes normal distribution
    3. CVaR (Conditional VaR) - Expected loss beyond VaR
    """

    def __init__(self, confidence_level: float = 0.95):
        """
        Initialize VaR calculator

        Args:
            confidence_level: Confidence level for VaR (default 95%)
        """
        self.confidence_level = confidence_level
        logger.info(f"VaRCalculator initialized (confidence: {confidence_level})")

    def calculate_historical_var(self, returns: pd.Series) -> Dict:
        """
        Calculate Historical VaR based on actual return distribution

        Args:
            returns: Series of portfolio returns

        Returns:
            {
                'var': float,  # VaR value
                'percentile': float,  # Percentile used
                'worst_loss': float,  # Worst historical loss
                'method': str
            }
        """
        try:
            # Remove NaN values
            returns = returns.dropna()

            if len(returns) < 20:
                logger.warning("Insufficient data for VaR calculation")
                return {
                    'var': np.nan,
                    'percentile': (1 - self.confidence_level) * 100,
                    'worst_loss': np.nan,
                    'method': 'historical'
                }

            # Calculate percentile (lower tail)
            percentile = (1 - self.confidence_level) * 100
            var_value = np.percentile(returns, percentile)

            # Worst historical loss
            worst_loss = returns.min()

            return {
                'var': float(var_value),
                'percentile': percentile,
                'worst_loss': float(worst_loss),
                'method': 'historical',
                'observations': len(returns)
            }

        except Exception as e:
            logger.error(f"Historical VaR calculation failed: {e}")
            return {
                'var': np.nan,
                'error': str(e),
                'method': 'historical'
            }

    def calculate_parametric_var(self, returns: pd.Series) -> Dict:
        """
        Calculate Parametric VaR assuming normal distribution

        Args:
            returns: Series of portfolio returns

        Returns:
            {
                'var': float,
                'mean': float,
                'std': float,
                'z_score': float,
                'method': str
            }
        """
        try:
            # Remove NaN values
            returns = returns.dropna()

            if len(returns) < 20:
                logger.warning("Insufficient data for parametric VaR")
                return {
                    'var': np.nan,
                    'method': 'parametric'
                }

            # Calculate mean and std
            mean_return = returns.mean()
            std_return = returns.std()

            # Z-score for confidence level
            z_score = stats.norm.ppf(1 - self.confidence_level)

            # VaR = mean + z_score * std (z_score is negative for losses)
            var_value = mean_return + z_score * std_return

            return {
                'var': float(var_value),
                'mean': float(mean_return),
                'std': float(std_return),
                'z_score': float(z_score),
                'method': 'parametric',
                'observations': len(returns)
            }

        except Exception as e:
            logger.error(f"Parametric VaR calculation failed: {e}")
            return {
                'var': np.nan,
                'error': str(e),
                'method': 'parametric'
            }

    def calculate_cvar(self, returns: pd.Series) -> Dict:
        """
        Calculate Conditional VaR (CVaR) / Expected Shortfall
        Expected loss given that loss exceeds VaR

        Args:
            returns: Series of portfolio returns

        Returns:
            {
                'cvar': float,
                'var': float,
                'tail_losses': int,  # Number of observations in tail
                'method': str
            }
        """
        try:
            # Remove NaN values
            returns = returns.dropna()

            if len(returns) < 20:
                logger.warning("Insufficient data for CVaR calculation")
                return {
                    'cvar': np.nan,
                    'method': 'cvar'
                }

            # First calculate VaR
            var_result = self.calculate_historical_var(returns)
            var_value = var_result['var']

            # CVaR is the mean of returns beyond VaR threshold
            tail_losses = returns[returns <= var_value]
            cvar_value = tail_losses.mean() if len(tail_losses) > 0 else var_value

            return {
                'cvar': float(cvar_value),
                'var': float(var_value),
                'tail_losses': len(tail_losses),
                'tail_mean': float(cvar_value),
                'method': 'cvar',
                'observations': len(returns)
            }

        except Exception as e:
            logger.error(f"CVaR calculation failed: {e}")
            return {
                'cvar': np.nan,
                'error': str(e),
                'method': 'cvar'
            }

    def calculate_all_metrics(self, returns: pd.Series) -> Dict:
        """
        Calculate all VaR metrics at once

        Args:
            returns: Series of portfolio returns

        Returns:
            {
                'historical_var': dict,
                'parametric_var': dict,
                'cvar': dict,
                'summary': dict
            }
        """
        try:
            # Calculate all methods
            hist_var = self.calculate_historical_var(returns)
            param_var = self.calculate_parametric_var(returns)
            cvar = self.calculate_cvar(returns)

            # Summary statistics
            returns_clean = returns.dropna()
            summary = {
                'mean_return': float(returns_clean.mean()),
                'std_return': float(returns_clean.std()),
                'min_return': float(returns_clean.min()),
                'max_return': float(returns_clean.max()),
                'skewness': float(returns_clean.skew()),
                'kurtosis': float(returns_clean.kurtosis()),
                'observations': len(returns_clean)
            }

            return {
                'historical_var': hist_var,
                'parametric_var': param_var,
                'cvar': cvar,
                'summary': summary,
                'confidence_level': self.confidence_level
            }

        except Exception as e:
            logger.error(f"All VaR metrics calculation failed: {e}")
            return {
                'error': str(e),
                'confidence_level': self.confidence_level
            }

    def calculate_portfolio_var(self, positions: Dict[str, float],
                                returns_data: pd.DataFrame) -> Dict:
        """
        Calculate portfolio VaR given positions and returns

        Args:
            positions: Dict of {symbol: weight}
            returns_data: DataFrame with returns for each symbol

        Returns:
            Portfolio VaR metrics
        """
        try:
            # Calculate portfolio returns
            portfolio_returns = pd.Series(0.0, index=returns_data.index)

            for symbol, weight in positions.items():
                if symbol in returns_data.columns:
                    portfolio_returns += weight * returns_data[symbol]

            # Calculate VaR on portfolio returns
            return self.calculate_all_metrics(portfolio_returns)

        except Exception as e:
            logger.error(f"Portfolio VaR calculation failed: {e}")
            return {
                'error': str(e),
                'positions': positions
            }