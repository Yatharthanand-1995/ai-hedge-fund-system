"""
Correlation Tracker
Monitors portfolio correlation and concentration risk
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class CorrelationTracker:
    """
    Track correlation metrics for portfolio risk management

    Metrics:
    1. Portfolio correlation matrix
    2. Correlation to market (SPY)
    3. Average pairwise correlation
    4. Concentration risk indicators
    """

    def __init__(self):
        """Initialize correlation tracker"""
        logger.info("CorrelationTracker initialized")

    def calculate_correlation_matrix(self, returns_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate correlation matrix for all assets

        Args:
            returns_data: DataFrame with returns for each asset

        Returns:
            Correlation matrix DataFrame
        """
        try:
            # Remove any NaN values
            returns_clean = returns_data.dropna()

            if len(returns_clean) < 20:
                logger.warning("Insufficient data for correlation calculation")
                return pd.DataFrame()

            # Calculate correlation matrix
            corr_matrix = returns_clean.corr()

            return corr_matrix

        except Exception as e:
            logger.error(f"Correlation matrix calculation failed: {e}")
            return pd.DataFrame()

    def calculate_portfolio_correlation(self, positions: Dict[str, float],
                                       returns_data: pd.DataFrame) -> Dict:
        """
        Calculate portfolio-level correlation metrics

        Args:
            positions: Dict of {symbol: weight}
            returns_data: DataFrame with returns for each symbol

        Returns:
            {
                'avg_correlation': float,
                'max_correlation': float,
                'min_correlation': float,
                'concentration_risk': str,
                'corr_matrix': pd.DataFrame
            }
        """
        try:
            # Filter returns for portfolio positions
            portfolio_symbols = list(positions.keys())
            portfolio_returns = returns_data[portfolio_symbols].dropna()

            if len(portfolio_returns) < 20:
                logger.warning("Insufficient data for portfolio correlation")
                return {
                    'error': 'Insufficient data',
                    'symbols': portfolio_symbols
                }

            # Calculate correlation matrix
            corr_matrix = portfolio_returns.corr()

            # Extract upper triangle (avoid double counting)
            upper_tri = corr_matrix.where(
                np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
            )

            # Calculate statistics
            correlations = upper_tri.stack().values
            avg_corr = float(np.mean(correlations))
            max_corr = float(np.max(correlations))
            min_corr = float(np.min(correlations))

            # Concentration risk assessment
            if avg_corr > 0.8:
                concentration_risk = "HIGH - Very similar movements"
            elif avg_corr > 0.6:
                concentration_risk = "MEDIUM - Moderately correlated"
            elif avg_corr > 0.3:
                concentration_risk = "LOW - Well diversified"
            else:
                concentration_risk = "VERY LOW - Highly diversified"

            return {
                'avg_correlation': avg_corr,
                'max_correlation': max_corr,
                'min_correlation': min_corr,
                'concentration_risk': concentration_risk,
                'corr_matrix': corr_matrix.to_dict(),
                'symbols': portfolio_symbols,
                'observations': len(portfolio_returns)
            }

        except Exception as e:
            logger.error(f"Portfolio correlation calculation failed: {e}")
            return {
                'error': str(e),
                'symbols': list(positions.keys())
            }

    def calculate_market_correlation(self, portfolio_returns: pd.Series,
                                    market_returns: pd.Series) -> Dict:
        """
        Calculate portfolio correlation to market (SPY)

        Args:
            portfolio_returns: Portfolio return series
            market_returns: Market (SPY) return series

        Returns:
            {
                'correlation': float,
                'beta': float,
                'alpha': float,
                'r_squared': float
            }
        """
        try:
            # Align and clean data
            aligned = pd.DataFrame({
                'portfolio': portfolio_returns,
                'market': market_returns
            }).dropna()

            if len(aligned) < 20:
                logger.warning("Insufficient data for market correlation")
                return {
                    'correlation': np.nan,
                    'beta': np.nan
                }

            # Calculate correlation
            correlation = aligned['portfolio'].corr(aligned['market'])

            # Calculate beta (covariance / market variance)
            covariance = aligned['portfolio'].cov(aligned['market'])
            market_var = aligned['market'].var()
            beta = covariance / market_var if market_var != 0 else 0

            # Calculate alpha (excess return vs market)
            portfolio_mean = aligned['portfolio'].mean()
            market_mean = aligned['market'].mean()
            alpha = portfolio_mean - (beta * market_mean)

            # R-squared
            r_squared = correlation ** 2

            return {
                'correlation': float(correlation),
                'beta': float(beta),
                'alpha': float(alpha),
                'r_squared': float(r_squared),
                'observations': len(aligned)
            }

        except Exception as e:
            logger.error(f"Market correlation calculation failed: {e}")
            return {
                'error': str(e),
                'correlation': np.nan
            }

    def identify_high_correlations(self, corr_matrix: pd.DataFrame,
                                   threshold: float = 0.8) -> List[Dict]:
        """
        Identify pairs of assets with correlation above threshold

        Args:
            corr_matrix: Correlation matrix
            threshold: Correlation threshold (default 0.8)

        Returns:
            List of {asset1, asset2, correlation}
        """
        try:
            high_corr_pairs = []

            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    asset1 = corr_matrix.columns[i]
                    asset2 = corr_matrix.columns[j]
                    corr_value = corr_matrix.iloc[i, j]

                    if abs(corr_value) >= threshold:
                        high_corr_pairs.append({
                            'asset1': asset1,
                            'asset2': asset2,
                            'correlation': float(corr_value),
                            'type': 'positive' if corr_value > 0 else 'negative'
                        })

            # Sort by absolute correlation
            high_corr_pairs.sort(key=lambda x: abs(x['correlation']), reverse=True)

            return high_corr_pairs

        except Exception as e:
            logger.error(f"High correlation identification failed: {e}")
            return []

    def calculate_diversification_ratio(self, positions: Dict[str, float],
                                       returns_data: pd.DataFrame) -> Dict:
        """
        Calculate portfolio diversification ratio
        DR = (Weighted average of volatilities) / (Portfolio volatility)

        Args:
            positions: Dict of {symbol: weight}
            returns_data: DataFrame with returns

        Returns:
            {
                'diversification_ratio': float,
                'interpretation': str
            }
        """
        try:
            # Filter returns for portfolio
            portfolio_symbols = list(positions.keys())
            portfolio_returns = returns_data[portfolio_symbols].dropna()

            if len(portfolio_returns) < 20:
                logger.warning("Insufficient data for diversification ratio")
                return {
                    'diversification_ratio': np.nan,
                    'error': 'Insufficient data'
                }

            # Calculate individual volatilities
            individual_vols = portfolio_returns.std()

            # Weighted average volatility
            weighted_avg_vol = sum(positions[sym] * individual_vols[sym]
                                  for sym in portfolio_symbols)

            # Portfolio volatility
            portfolio_total_returns = sum(positions[sym] * portfolio_returns[sym]
                                         for sym in portfolio_symbols)
            portfolio_vol = portfolio_total_returns.std()

            # Diversification ratio
            div_ratio = weighted_avg_vol / portfolio_vol if portfolio_vol != 0 else 1.0

            # Interpretation
            if div_ratio > 1.5:
                interpretation = "EXCELLENT - Strong diversification"
            elif div_ratio > 1.2:
                interpretation = "GOOD - Moderate diversification"
            elif div_ratio > 1.0:
                interpretation = "FAIR - Some diversification"
            else:
                interpretation = "POOR - Little diversification benefit"

            return {
                'diversification_ratio': float(div_ratio),
                'weighted_avg_vol': float(weighted_avg_vol),
                'portfolio_vol': float(portfolio_vol),
                'interpretation': interpretation,
                'observations': len(portfolio_returns)
            }

        except Exception as e:
            logger.error(f"Diversification ratio calculation failed: {e}")
            return {
                'diversification_ratio': np.nan,
                'error': str(e)
            }