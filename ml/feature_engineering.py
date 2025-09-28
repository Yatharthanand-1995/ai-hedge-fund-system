"""
Feature Engineering
Creates features for ML optimization from historical data
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """
    Feature engineering for ML weight optimization

    Extracts relevant features from:
    - Agent scores
    - Market conditions
    - Performance metrics
    - Regime indicators
    """

    def __init__(self):
        """Initialize feature engineer"""
        logger.info("FeatureEngineer initialized")

    def extract_agent_features(self, agent_scores: Dict[str, pd.Series]) -> pd.DataFrame:
        """
        Extract features from agent scores

        Args:
            agent_scores: Dict of {agent_name: score_series}

        Returns:
            DataFrame with agent-based features
        """
        try:
            features = pd.DataFrame()

            for agent_name, scores in agent_scores.items():
                if len(scores) == 0:
                    continue

                # Raw scores
                features[f'{agent_name}_score'] = scores

                # Moving averages
                features[f'{agent_name}_ma_5'] = scores.rolling(5).mean()
                features[f'{agent_name}_ma_20'] = scores.rolling(20).mean()

                # Momentum indicators
                features[f'{agent_name}_momentum_5'] = scores / scores.shift(5) - 1
                features[f'{agent_name}_momentum_20'] = scores / scores.shift(20) - 1

                # Volatility (rolling std)
                features[f'{agent_name}_vol_5'] = scores.rolling(5).std()
                features[f'{agent_name}_vol_20'] = scores.rolling(20).std()

                # Z-scores
                rolling_mean = scores.rolling(60).mean()
                rolling_std = scores.rolling(60).std()
                features[f'{agent_name}_zscore'] = (scores - rolling_mean) / rolling_std

                # Rank percentile
                features[f'{agent_name}_rank'] = scores.rolling(60).rank(pct=True)

            logger.info(f"Extracted {len(features.columns)} agent features")
            return features

        except Exception as e:
            logger.error(f"Agent feature extraction failed: {e}")
            return pd.DataFrame()

    def extract_market_features(self, market_data: pd.DataFrame) -> pd.DataFrame:
        """
        Extract market-based features

        Args:
            market_data: DataFrame with market prices/indices

        Returns:
            DataFrame with market features
        """
        try:
            features = pd.DataFrame(index=market_data.index)

            if 'SPY' in market_data.columns:
                spy_prices = market_data['SPY']

                # Returns
                features['spy_return_1d'] = spy_prices.pct_change()
                features['spy_return_5d'] = spy_prices.pct_change(5)
                features['spy_return_20d'] = spy_prices.pct_change(20)

                # Volatility (realized)
                features['spy_vol_5d'] = features['spy_return_1d'].rolling(5).std() * np.sqrt(252)
                features['spy_vol_20d'] = features['spy_return_1d'].rolling(20).std() * np.sqrt(252)

                # Moving averages
                features['spy_ma_20'] = spy_prices.rolling(20).mean()
                features['spy_ma_50'] = spy_prices.rolling(50).mean()
                features['spy_ma_200'] = spy_prices.rolling(200).mean()

                # Technical indicators
                features['spy_above_ma20'] = (spy_prices > features['spy_ma_20']).astype(int)
                features['spy_above_ma50'] = (spy_prices > features['spy_ma_50']).astype(int)
                features['spy_above_ma200'] = (spy_prices > features['spy_ma_200']).astype(int)

                # RSI-like momentum
                delta = features['spy_return_1d']
                gain = delta.where(delta > 0, 0).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                features['spy_rsi'] = 100 - (100 / (1 + gain / loss))

            if 'VIX' in market_data.columns:
                vix = market_data['VIX']

                features['vix_level'] = vix
                features['vix_change'] = vix.pct_change()
                features['vix_ma_20'] = vix.rolling(20).mean()

                # VIX regime indicators
                features['vix_low_regime'] = (vix < 20).astype(int)
                features['vix_high_regime'] = (vix > 30).astype(int)

            logger.info(f"Extracted {len(features.columns)} market features")
            return features

        except Exception as e:
            logger.error(f"Market feature extraction failed: {e}")
            return pd.DataFrame()

    def extract_performance_features(self, portfolio_returns: pd.Series) -> pd.DataFrame:
        """
        Extract performance-based features

        Args:
            portfolio_returns: Historical portfolio returns

        Returns:
            DataFrame with performance features
        """
        try:
            features = pd.DataFrame(index=portfolio_returns.index)

            # Returns
            features['portfolio_return'] = portfolio_returns

            # Cumulative returns
            cumulative = (1 + portfolio_returns).cumprod()
            features['portfolio_cumulative'] = cumulative

            # Rolling performance metrics
            for window in [5, 20, 60]:
                window_returns = portfolio_returns.rolling(window)

                features[f'sharpe_{window}d'] = (
                    window_returns.mean() / window_returns.std() * np.sqrt(252)
                )

                # Drawdown
                rolling_max = cumulative.rolling(window).max()
                drawdown = (cumulative - rolling_max) / rolling_max
                features[f'drawdown_{window}d'] = drawdown

                # Hit rate
                features[f'hit_rate_{window}d'] = (portfolio_returns.rolling(window) > 0).mean()

            # Regime indicators based on performance
            features['positive_trend'] = (portfolio_returns.rolling(10).mean() > 0).astype(int)
            features['high_vol_regime'] = (
                portfolio_returns.rolling(20).std() > portfolio_returns.rolling(60).std().median()
            ).astype(int)

            logger.info(f"Extracted {len(features.columns)} performance features")
            return features

        except Exception as e:
            logger.error(f"Performance feature extraction failed: {e}")
            return pd.DataFrame()

    def create_target_variable(self, portfolio_returns: pd.Series,
                             target_type: str = 'sharpe',
                             forward_window: int = 20) -> pd.Series:
        """
        Create target variable for supervised learning

        Args:
            portfolio_returns: Portfolio returns
            target_type: Type of target ('sharpe', 'return', 'drawdown')
            forward_window: Forward-looking window in days

        Returns:
            Target variable series
        """
        try:
            if target_type == 'sharpe':
                # Forward Sharpe ratio
                target = (
                    portfolio_returns.rolling(forward_window).mean().shift(-forward_window)
                    / portfolio_returns.rolling(forward_window).std().shift(-forward_window)
                    * np.sqrt(252)
                )

            elif target_type == 'return':
                # Forward cumulative return
                target = (
                    (1 + portfolio_returns).rolling(forward_window).apply(lambda x: x.prod() - 1)
                    .shift(-forward_window)
                )

            elif target_type == 'drawdown':
                # Forward maximum drawdown (negative target)
                cumulative = (1 + portfolio_returns).cumprod()
                rolling_max = cumulative.rolling(forward_window).max().shift(-forward_window)
                rolling_min = cumulative.rolling(forward_window).min().shift(-forward_window)
                target = -(rolling_min - rolling_max) / rolling_max

            else:
                raise ValueError(f"Unknown target_type: {target_type}")

            logger.info(f"Created {target_type} target with {forward_window}d window")
            return target

        except Exception as e:
            logger.error(f"Target creation failed: {e}")
            return pd.Series()

    def build_dataset(self, agent_scores: Dict[str, pd.Series],
                     portfolio_returns: pd.Series,
                     market_data: Optional[pd.DataFrame] = None,
                     target_type: str = 'sharpe',
                     forward_window: int = 20) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Build complete dataset for ML optimization

        Args:
            agent_scores: Agent scores over time
            portfolio_returns: Portfolio returns
            market_data: Market data (optional)
            target_type: Target variable type
            forward_window: Forward-looking window

        Returns:
            Tuple of (features_df, target_series)
        """
        try:
            # Extract all features
            agent_features = self.extract_agent_features(agent_scores)
            performance_features = self.extract_performance_features(portfolio_returns)

            # Combine features
            all_features = pd.concat([agent_features, performance_features], axis=1)

            # Add market features if available
            if market_data is not None and not market_data.empty:
                market_features = self.extract_market_features(market_data)
                all_features = pd.concat([all_features, market_features], axis=1)

            # Create target
            target = self.create_target_variable(portfolio_returns, target_type, forward_window)

            # Align features and target
            aligned = pd.concat([all_features, target.rename('target')], axis=1).dropna()

            if len(aligned) == 0:
                logger.warning("No aligned data after feature creation")
                return pd.DataFrame(), pd.Series()

            features_df = aligned.drop('target', axis=1)
            target_series = aligned['target']

            logger.info(f"Dataset built: {len(features_df)} samples, {len(features_df.columns)} features")
            return features_df, target_series

        except Exception as e:
            logger.error(f"Dataset building failed: {e}")
            return pd.DataFrame(), pd.Series()

    def select_features(self, features_df: pd.DataFrame,
                       target_series: pd.Series,
                       method: str = 'correlation',
                       n_features: int = 20) -> List[str]:
        """
        Select most relevant features

        Args:
            features_df: Feature matrix
            target_series: Target variable
            method: Selection method ('correlation', 'mutual_info', 'variance')
            n_features: Number of features to select

        Returns:
            List of selected feature names
        """
        try:
            if method == 'correlation':
                # Select features with highest absolute correlation to target
                correlations = features_df.corrwith(target_series).abs()
                selected_features = correlations.nlargest(n_features).index.tolist()

            elif method == 'variance':
                # Select features with highest variance
                variances = features_df.var()
                selected_features = variances.nlargest(n_features).index.tolist()

            elif method == 'mutual_info':
                try:
                    from sklearn.feature_selection import mutual_info_regression
                    mi_scores = mutual_info_regression(features_df, target_series)
                    feature_importance = pd.Series(mi_scores, index=features_df.columns)
                    selected_features = feature_importance.nlargest(n_features).index.tolist()
                except ImportError:
                    logger.warning("sklearn not available, using correlation method")
                    correlations = features_df.corrwith(target_series).abs()
                    selected_features = correlations.nlargest(n_features).index.tolist()

            else:
                raise ValueError(f"Unknown selection method: {method}")

            logger.info(f"Selected {len(selected_features)} features using {method}")
            return selected_features

        except Exception as e:
            logger.error(f"Feature selection failed: {e}")
            return features_df.columns.tolist()[:n_features]