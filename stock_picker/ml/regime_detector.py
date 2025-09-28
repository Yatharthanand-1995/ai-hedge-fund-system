"""
Regime Detector
Identifies market regimes for adaptive weight optimization
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RegimeDetector:
    """
    Market regime detection for adaptive strategy

    Identifies different market regimes:
    - Bull/Bear markets
    - High/Low volatility
    - Risk-on/Risk-off
    - Growth/Value rotation
    """

    def __init__(self):
        """Initialize regime detector"""
        self.regimes = {}
        logger.info("RegimeDetector initialized")

    def detect_volatility_regime(self, returns: pd.Series,
                                short_window: int = 20,
                                long_window: int = 60) -> pd.Series:
        """
        Detect volatility regime (high/normal/low)

        Args:
            returns: Return series
            short_window: Short volatility window
            long_window: Long volatility window

        Returns:
            Series with regime labels
        """
        try:
            # Calculate rolling volatilities
            short_vol = returns.rolling(short_window).std() * np.sqrt(252)
            long_vol = returns.rolling(long_window).std() * np.sqrt(252)

            # Volatility percentiles
            vol_75 = long_vol.quantile(0.75)
            vol_25 = long_vol.quantile(0.25)

            # Regime classification
            regime = pd.Series(index=returns.index, dtype=str)
            regime[short_vol > vol_75] = 'HIGH_VOL'
            regime[short_vol < vol_25] = 'LOW_VOL'
            regime[(short_vol >= vol_25) & (short_vol <= vol_75)] = 'NORMAL_VOL'

            logger.info(f"Volatility regimes: {regime.value_counts().to_dict()}")
            return regime

        except Exception as e:
            logger.error(f"Volatility regime detection failed: {e}")
            return pd.Series(index=returns.index, dtype=str).fillna('NORMAL_VOL')

    def detect_trend_regime(self, prices: pd.Series,
                           short_ma: int = 20,
                           long_ma: int = 50) -> pd.Series:
        """
        Detect trend regime (bull/bear/sideways)

        Args:
            prices: Price series
            short_ma: Short moving average period
            long_ma: Long moving average period

        Returns:
            Series with trend regime labels
        """
        try:
            # Moving averages
            ma_short = prices.rolling(short_ma).mean()
            ma_long = prices.rolling(long_ma).mean()

            # Price relative to moving averages
            price_above_short = prices > ma_short
            price_above_long = prices > ma_long
            ma_short_above_long = ma_short > ma_long

            # Regime classification
            regime = pd.Series(index=prices.index, dtype=str)

            # Bull market: price above both MAs, short MA above long MA
            bull_conditions = price_above_short & price_above_long & ma_short_above_long
            regime[bull_conditions] = 'BULL'

            # Bear market: price below both MAs, short MA below long MA
            bear_conditions = (~price_above_short) & (~price_above_long) & (~ma_short_above_long)
            regime[bear_conditions] = 'BEAR'

            # Sideways: mixed conditions
            regime[~(bull_conditions | bear_conditions)] = 'SIDEWAYS'

            logger.info(f"Trend regimes: {regime.value_counts().to_dict()}")
            return regime

        except Exception as e:
            logger.error(f"Trend regime detection failed: {e}")
            return pd.Series(index=prices.index, dtype=str).fillna('SIDEWAYS')

    def detect_momentum_regime(self, returns: pd.Series,
                              lookback: int = 60) -> pd.Series:
        """
        Detect momentum regime (momentum/mean_reversion)

        Args:
            returns: Return series
            lookback: Lookback period for momentum calculation

        Returns:
            Series with momentum regime labels
        """
        try:
            # Calculate momentum metrics
            cumulative_returns = (1 + returns).rolling(lookback).apply(lambda x: x.prod() - 1)

            # Momentum vs mean reversion indicators
            # High momentum: consistent directional moves
            momentum_strength = abs(cumulative_returns)

            # Mean reversion: high volatility with low cumulative returns
            volatility = returns.rolling(lookback).std()
            vol_normalized_return = abs(cumulative_returns) / volatility

            # Regime thresholds
            momentum_threshold = momentum_strength.quantile(0.7)
            reversion_threshold = vol_normalized_return.quantile(0.3)

            regime = pd.Series(index=returns.index, dtype=str)
            regime[momentum_strength > momentum_threshold] = 'MOMENTUM'
            regime[vol_normalized_return < reversion_threshold] = 'MEAN_REVERSION'
            regime[~regime.isin(['MOMENTUM', 'MEAN_REVERSION'])] = 'NEUTRAL'

            logger.info(f"Momentum regimes: {regime.value_counts().to_dict()}")
            return regime

        except Exception as e:
            logger.error(f"Momentum regime detection failed: {e}")
            return pd.Series(index=returns.index, dtype=str).fillna('NEUTRAL')

    def detect_correlation_regime(self, asset_returns: pd.DataFrame,
                                 window: int = 60) -> pd.Series:
        """
        Detect correlation regime (high/low correlation periods)

        Args:
            asset_returns: DataFrame with asset returns
            window: Rolling window for correlation

        Returns:
            Series with correlation regime labels
        """
        try:
            # Calculate rolling average correlation
            rolling_corr = asset_returns.rolling(window).corr()

            # Extract average correlation for each date
            avg_correlations = []
            for date in asset_returns.index:
                try:
                    corr_matrix = rolling_corr.loc[date]
                    if isinstance(corr_matrix, pd.DataFrame):
                        # Get upper triangle (excluding diagonal)
                        upper_tri = corr_matrix.where(
                            np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
                        )
                        avg_corr = upper_tri.stack().mean()
                    else:
                        avg_corr = np.nan
                    avg_correlations.append(avg_corr)
                except:
                    avg_correlations.append(np.nan)

            avg_corr_series = pd.Series(avg_correlations, index=asset_returns.index)

            # Regime classification based on correlation levels
            corr_high = avg_corr_series.quantile(0.75)
            corr_low = avg_corr_series.quantile(0.25)

            regime = pd.Series(index=asset_returns.index, dtype=str)
            regime[avg_corr_series > corr_high] = 'HIGH_CORR'
            regime[avg_corr_series < corr_low] = 'LOW_CORR'
            regime[~regime.isin(['HIGH_CORR', 'LOW_CORR'])] = 'NORMAL_CORR'

            logger.info(f"Correlation regimes: {regime.value_counts().to_dict()}")
            return regime

        except Exception as e:
            logger.error(f"Correlation regime detection failed: {e}")
            return pd.Series(index=asset_returns.index, dtype=str).fillna('NORMAL_CORR')

    def detect_all_regimes(self, market_data: pd.DataFrame) -> pd.DataFrame:
        """
        Detect all regime types

        Args:
            market_data: DataFrame with market data (prices, returns)

        Returns:
            DataFrame with all regime classifications
        """
        try:
            regimes_df = pd.DataFrame(index=market_data.index)

            # Volatility regime from returns
            if 'returns' in market_data.columns:
                regimes_df['volatility_regime'] = self.detect_volatility_regime(
                    market_data['returns']
                )
                regimes_df['momentum_regime'] = self.detect_momentum_regime(
                    market_data['returns']
                )

            # Trend regime from prices
            if 'price' in market_data.columns:
                regimes_df['trend_regime'] = self.detect_trend_regime(
                    market_data['price']
                )

            # Correlation regime if multiple assets
            return_columns = [col for col in market_data.columns if col.endswith('_return')]
            if len(return_columns) > 1:
                regimes_df['correlation_regime'] = self.detect_correlation_regime(
                    market_data[return_columns]
                )

            # Composite regime
            regimes_df['composite_regime'] = self._create_composite_regime(regimes_df)

            logger.info(f"Detected {len(regimes_df.columns)} regime types")
            return regimes_df

        except Exception as e:
            logger.error(f"Multi-regime detection failed: {e}")
            return pd.DataFrame(index=market_data.index)

    def _create_composite_regime(self, regimes_df: pd.DataFrame) -> pd.Series:
        """
        Create composite regime from individual regimes

        Args:
            regimes_df: DataFrame with individual regimes

        Returns:
            Composite regime series
        """
        try:
            composite = pd.Series(index=regimes_df.index, dtype=str)

            for idx in regimes_df.index:
                regime_components = []

                if 'trend_regime' in regimes_df.columns:
                    trend = regimes_df.loc[idx, 'trend_regime']
                    if pd.notna(trend):
                        regime_components.append(trend)

                if 'volatility_regime' in regimes_df.columns:
                    vol = regimes_df.loc[idx, 'volatility_regime']
                    if pd.notna(vol):
                        regime_components.append(vol)

                # Create composite label
                if regime_components:
                    composite.loc[idx] = '_'.join(regime_components)
                else:
                    composite.loc[idx] = 'UNKNOWN'

            return composite

        except Exception as e:
            logger.error(f"Composite regime creation failed: {e}")
            return pd.Series(index=regimes_df.index, dtype=str).fillna('UNKNOWN')

    def get_regime_weights(self, current_regime: str,
                          regime_weight_map: Optional[Dict[str, Dict[str, float]]] = None
                          ) -> Dict[str, float]:
        """
        Get optimal weights for current regime

        Args:
            current_regime: Current market regime
            regime_weight_map: Optional custom weight mapping

        Returns:
            Optimal weights for current regime
        """
        try:
            # Default regime-based weights
            if regime_weight_map is None:
                regime_weight_map = {
                    'BULL_HIGH_VOL': {'fundamentals': 0.3, 'momentum': 0.4, 'quality': 0.2, 'sentiment': 0.1},
                    'BULL_NORMAL_VOL': {'fundamentals': 0.4, 'momentum': 0.3, 'quality': 0.2, 'sentiment': 0.1},
                    'BULL_LOW_VOL': {'fundamentals': 0.5, 'momentum': 0.2, 'quality': 0.2, 'sentiment': 0.1},

                    'BEAR_HIGH_VOL': {'fundamentals': 0.2, 'momentum': 0.2, 'quality': 0.4, 'sentiment': 0.2},
                    'BEAR_NORMAL_VOL': {'fundamentals': 0.3, 'momentum': 0.2, 'quality': 0.3, 'sentiment': 0.2},
                    'BEAR_LOW_VOL': {'fundamentals': 0.4, 'momentum': 0.2, 'quality': 0.3, 'sentiment': 0.1},

                    'SIDEWAYS_HIGH_VOL': {'fundamentals': 0.2, 'momentum': 0.3, 'quality': 0.3, 'sentiment': 0.2},
                    'SIDEWAYS_NORMAL_VOL': {'fundamentals': 0.4, 'momentum': 0.3, 'quality': 0.2, 'sentiment': 0.1},
                    'SIDEWAYS_LOW_VOL': {'fundamentals': 0.5, 'momentum': 0.2, 'quality': 0.2, 'sentiment': 0.1},

                    # Default fallback
                    'DEFAULT': {'fundamentals': 0.4, 'momentum': 0.3, 'quality': 0.2, 'sentiment': 0.1}
                }

            # Get weights for current regime or use default
            if current_regime in regime_weight_map:
                weights = regime_weight_map[current_regime]
            else:
                logger.warning(f"Unknown regime {current_regime}, using default weights")
                weights = regime_weight_map['DEFAULT']

            logger.info(f"Regime weights for {current_regime}: {weights}")
            return weights

        except Exception as e:
            logger.error(f"Regime weight lookup failed: {e}")
            return {'fundamentals': 0.4, 'momentum': 0.3, 'quality': 0.2, 'sentiment': 0.1}

    def analyze_regime_performance(self, regimes: pd.Series,
                                  returns: pd.Series,
                                  weights_history: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze performance across different regimes

        Args:
            regimes: Series with regime labels
            returns: Portfolio returns
            weights_history: Historical agent weights

        Returns:
            DataFrame with performance by regime
        """
        try:
            performance_data = []

            for regime in regimes.unique():
                if pd.isna(regime):
                    continue

                regime_mask = regimes == regime
                regime_returns = returns[regime_mask]

                if len(regime_returns) == 0:
                    continue

                # Performance metrics
                total_return = (1 + regime_returns).prod() - 1
                sharpe = regime_returns.mean() / regime_returns.std() * np.sqrt(252) if regime_returns.std() > 0 else 0
                volatility = regime_returns.std() * np.sqrt(252)

                # Drawdown
                cumulative = (1 + regime_returns).cumprod()
                running_max = cumulative.expanding().max()
                drawdown = (cumulative - running_max) / running_max
                max_drawdown = drawdown.min()

                performance_data.append({
                    'regime': regime,
                    'observations': len(regime_returns),
                    'total_return': total_return,
                    'sharpe_ratio': sharpe,
                    'volatility': volatility,
                    'max_drawdown': max_drawdown,
                    'hit_rate': (regime_returns > 0).mean()
                })

            performance_df = pd.DataFrame(performance_data)

            logger.info(f"Analyzed performance across {len(performance_df)} regimes")
            return performance_df

        except Exception as e:
            logger.error(f"Regime performance analysis failed: {e}")
            return pd.DataFrame()