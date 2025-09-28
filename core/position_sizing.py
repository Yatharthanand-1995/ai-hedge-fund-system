"""
Position Sizing Module
Volatility-based position sizing for risk-adjusted portfolios
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class PositionSizer:
    """
    Volatility-based position sizing

    Methods:
    1. Equal weight (baseline)
    2. Inverse volatility (risk parity)
    3. Risk parity with correlation
    4. Kelly criterion
    5. Maximum Sharpe
    """

    def __init__(self, method: str = 'inverse_volatility'):
        """
        Initialize position sizer

        Args:
            method: Sizing method
                - 'equal_weight': 1/N for each position
                - 'inverse_volatility': Weight inversely to volatility
                - 'risk_parity': Equal risk contribution
                - 'kelly': Kelly criterion
                - 'max_sharpe': Maximum Sharpe ratio
        """
        self.method = method
        self.valid_methods = [
            'equal_weight', 'inverse_volatility', 'risk_parity',
            'kelly', 'max_sharpe'
        ]

        if method not in self.valid_methods:
            raise ValueError(f"Method must be one of {self.valid_methods}")

        logger.info(f"PositionSizer initialized (method: {method})")

    def calculate_weights(self, symbols: List[str],
                         returns_data: pd.DataFrame,
                         scores: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """
        Calculate position weights for symbols

        Args:
            symbols: List of stock symbols
            returns_data: DataFrame with historical returns
            scores: Optional quality scores for symbols

        Returns:
            Dict of {symbol: weight}
        """
        try:
            if self.method == 'equal_weight':
                return self._equal_weight(symbols)

            elif self.method == 'inverse_volatility':
                return self._inverse_volatility(symbols, returns_data)

            elif self.method == 'risk_parity':
                return self._risk_parity(symbols, returns_data)

            elif self.method == 'kelly':
                return self._kelly_criterion(symbols, returns_data, scores)

            elif self.method == 'max_sharpe':
                return self._max_sharpe(symbols, returns_data)

        except Exception as e:
            logger.error(f"Weight calculation failed: {e}")
            return self._equal_weight(symbols)

    def _equal_weight(self, symbols: List[str]) -> Dict[str, float]:
        """Equal weight allocation (1/N)"""
        n = len(symbols)
        weight = 1.0 / n
        return {sym: weight for sym in symbols}

    def _inverse_volatility(self, symbols: List[str],
                           returns_data: pd.DataFrame) -> Dict[str, float]:
        """
        Inverse volatility weighting
        Weight = (1/volatility) / sum(1/volatility)

        Lower volatility stocks get higher weights
        """
        try:
            portfolio_returns = returns_data[symbols].dropna()

            if len(portfolio_returns) < 20:
                logger.warning("Insufficient data for volatility calculation")
                return self._equal_weight(symbols)

            volatilities = portfolio_returns.std()

            inv_vols = 1.0 / volatilities
            total_inv_vol = inv_vols.sum()

            weights = {}
            for sym in symbols:
                weights[sym] = float(inv_vols[sym] / total_inv_vol)

            weights = self._normalize_weights(weights)

            logger.info(f"Inverse volatility weights: {weights}")
            return weights

        except Exception as e:
            logger.error(f"Inverse volatility calculation failed: {e}")
            return self._equal_weight(symbols)

    def _risk_parity(self, symbols: List[str],
                     returns_data: pd.DataFrame) -> Dict[str, float]:
        """
        Risk parity: Equal risk contribution from each asset
        Accounts for correlations
        """
        try:
            portfolio_returns = returns_data[symbols].dropna()

            if len(portfolio_returns) < 60:
                logger.warning("Insufficient data for risk parity")
                return self._inverse_volatility(symbols, returns_data)

            cov_matrix = portfolio_returns.cov()
            volatilities = portfolio_returns.std()

            corr_matrix = portfolio_returns.corr()
            avg_corr = corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].mean()

            if avg_corr > 0.8:
                logger.warning(f"High correlation ({avg_corr:.2f}), using inverse volatility")
                return self._inverse_volatility(symbols, returns_data)

            inv_vols = 1.0 / volatilities

            corr_adj_weights = {}
            for sym in symbols:
                corr_penalty = 1.0
                for other_sym in symbols:
                    if sym != other_sym:
                        corr_val = abs(corr_matrix.loc[sym, other_sym])
                        corr_penalty *= (1.0 - 0.3 * corr_val)

                corr_adj_weights[sym] = inv_vols[sym] * corr_penalty

            total_weight = sum(corr_adj_weights.values())
            weights = {sym: w / total_weight for sym, w in corr_adj_weights.items()}

            weights = self._normalize_weights(weights)

            logger.info(f"Risk parity weights: {weights}")
            return weights

        except Exception as e:
            logger.error(f"Risk parity calculation failed: {e}")
            return self._inverse_volatility(symbols, returns_data)

    def _kelly_criterion(self, symbols: List[str],
                        returns_data: pd.DataFrame,
                        scores: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """
        Kelly criterion: f* = (p*b - q) / b
        where p = win probability, q = 1-p, b = win/loss ratio

        Uses historical returns and quality scores
        """
        try:
            portfolio_returns = returns_data[symbols].dropna()

            if len(portfolio_returns) < 60:
                logger.warning("Insufficient data for Kelly criterion")
                return self._inverse_volatility(symbols, returns_data)

            kelly_fractions = {}

            for sym in symbols:
                sym_returns = portfolio_returns[sym]

                positive_returns = sym_returns[sym_returns > 0]
                negative_returns = sym_returns[sym_returns < 0]

                if len(positive_returns) == 0 or len(negative_returns) == 0:
                    kelly_fractions[sym] = 1.0 / len(symbols)
                    continue

                win_prob = len(positive_returns) / len(sym_returns)
                loss_prob = 1 - win_prob

                avg_win = positive_returns.mean()
                avg_loss = abs(negative_returns.mean())

                win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 1.0

                kelly_f = (win_prob * win_loss_ratio - loss_prob) / win_loss_ratio

                kelly_f = max(0.0, min(kelly_f, 0.5))

                if scores and sym in scores:
                    score_adj = scores[sym] / 100.0
                    kelly_f *= score_adj

                kelly_fractions[sym] = kelly_f

            total_kelly = sum(kelly_fractions.values())

            if total_kelly == 0:
                return self._equal_weight(symbols)

            weights = {sym: k / total_kelly for sym, k in kelly_fractions.items()}

            weights = self._normalize_weights(weights)

            logger.info(f"Kelly criterion weights: {weights}")
            return weights

        except Exception as e:
            logger.error(f"Kelly criterion calculation failed: {e}")
            return self._inverse_volatility(symbols, returns_data)

    def _max_sharpe(self, symbols: List[str],
                    returns_data: pd.DataFrame) -> Dict[str, float]:
        """
        Maximum Sharpe ratio optimization
        Uses mean-variance optimization
        """
        try:
            portfolio_returns = returns_data[symbols].dropna()

            if len(portfolio_returns) < 60:
                logger.warning("Insufficient data for Sharpe optimization")
                return self._inverse_volatility(symbols, returns_data)

            mean_returns = portfolio_returns.mean()
            cov_matrix = portfolio_returns.cov()

            n_assets = len(symbols)

            initial_weights = np.array([1.0/n_assets] * n_assets)

            from scipy.optimize import minimize

            def neg_sharpe(weights):
                portfolio_return = np.dot(weights, mean_returns)
                portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

                if portfolio_vol == 0:
                    return 0

                sharpe = portfolio_return / portfolio_vol
                return -sharpe

            constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0})

            bounds = tuple((0.05, 0.50) for _ in range(n_assets))

            result = minimize(
                neg_sharpe,
                initial_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                options={'maxiter': 1000}
            )

            if result.success:
                optimal_weights = result.x
                weights = {sym: float(w) for sym, w in zip(symbols, optimal_weights)}

                weights = self._normalize_weights(weights)

                logger.info(f"Max Sharpe weights: {weights}")
                return weights
            else:
                logger.warning("Sharpe optimization failed, using inverse volatility")
                return self._inverse_volatility(symbols, returns_data)

        except Exception as e:
            logger.error(f"Max Sharpe calculation failed: {e}")
            return self._inverse_volatility(symbols, returns_data)

    def _normalize_weights(self, weights: Dict[str, float]) -> Dict[str, float]:
        """Ensure weights sum to 1.0"""
        total = sum(weights.values())
        if total == 0:
            return weights
        return {sym: w / total for sym, w in weights.items()}

    def calculate_position_volatility(self, weights: Dict[str, float],
                                      returns_data: pd.DataFrame) -> float:
        """
        Calculate portfolio volatility given weights

        Args:
            weights: Position weights
            returns_data: Historical returns

        Returns:
            Portfolio volatility (annualized)
        """
        try:
            symbols = list(weights.keys())
            portfolio_returns = returns_data[symbols].dropna()

            if len(portfolio_returns) < 20:
                return np.nan

            weight_array = np.array([weights[sym] for sym in symbols])

            portfolio_return = (portfolio_returns * weight_array).sum(axis=1)

            daily_vol = portfolio_return.std()
            annual_vol = daily_vol * np.sqrt(252)

            return float(annual_vol)

        except Exception as e:
            logger.error(f"Portfolio volatility calculation failed: {e}")
            return np.nan

    def compare_methods(self, symbols: List[str],
                       returns_data: pd.DataFrame,
                       scores: Optional[Dict[str, float]] = None) -> pd.DataFrame:
        """
        Compare all position sizing methods

        Returns:
            DataFrame with weights and metrics for each method
        """
        try:
            results = []

            for method in self.valid_methods:
                sizer = PositionSizer(method=method)
                weights = sizer.calculate_weights(symbols, returns_data, scores)

                portfolio_vol = self.calculate_position_volatility(weights, returns_data)

                portfolio_returns = returns_data[symbols].dropna()
                weight_array = np.array([weights[sym] for sym in symbols])
                portfolio_return = (portfolio_returns * weight_array).sum(axis=1)

                sharpe = portfolio_return.mean() / portfolio_return.std() * np.sqrt(252)

                max_weight = max(weights.values())
                min_weight = min(weights.values())

                results.append({
                    'method': method,
                    'portfolio_volatility': portfolio_vol,
                    'sharpe_ratio': sharpe,
                    'max_weight': max_weight,
                    'min_weight': min_weight,
                    'concentration': max_weight / min_weight,
                    'weights': weights
                })

            return pd.DataFrame(results)

        except Exception as e:
            logger.error(f"Method comparison failed: {e}")
            return pd.DataFrame()


class DynamicPositionSizer:
    """
    Dynamic position sizing based on market conditions

    Adjusts position sizes based on:
    - Market volatility regime
    - Portfolio drawdown
    - Individual stock volatility
    """

    def __init__(self, base_method: str = 'inverse_volatility'):
        """
        Initialize dynamic position sizer

        Args:
            base_method: Base sizing method to use
        """
        self.base_sizer = PositionSizer(method=base_method)
        self.volatility_threshold_low = 0.15
        self.volatility_threshold_high = 0.30

        logger.info(f"DynamicPositionSizer initialized (base: {base_method})")

    def calculate_weights(self, symbols: List[str],
                         returns_data: pd.DataFrame,
                         scores: Optional[Dict[str, float]] = None,
                         current_drawdown: float = 0.0,
                         market_volatility: Optional[float] = None) -> Dict[str, float]:
        """
        Calculate dynamic position weights

        Args:
            symbols: Stock symbols
            returns_data: Historical returns
            scores: Quality scores
            current_drawdown: Current portfolio drawdown (0 to -1)
            market_volatility: Current market volatility (optional)

        Returns:
            Dict of {symbol: weight}
        """
        try:
            base_weights = self.base_sizer.calculate_weights(
                symbols, returns_data, scores
            )

            if market_volatility is None:
                market_returns = returns_data.mean(axis=1)
                market_volatility = market_returns.std() * np.sqrt(252)

            vol_regime = self._determine_volatility_regime(market_volatility)

            dd_factor = self._drawdown_adjustment(current_drawdown)

            vol_factor = self._volatility_adjustment(vol_regime)

            adjusted_weights = {}
            for sym, weight in base_weights.items():
                adjusted_weight = weight * dd_factor * vol_factor
                adjusted_weights[sym] = adjusted_weight

            total_weight = sum(adjusted_weights.values())
            if total_weight > 0:
                adjusted_weights = {
                    sym: w / total_weight
                    for sym, w in adjusted_weights.items()
                }

            logger.info(f"Dynamic weights (DD: {current_drawdown:.1%}, Vol: {vol_regime}): {adjusted_weights}")
            return adjusted_weights

        except Exception as e:
            logger.error(f"Dynamic weight calculation failed: {e}")
            return self.base_sizer.calculate_weights(symbols, returns_data, scores)

    def _determine_volatility_regime(self, market_volatility: float) -> str:
        """Determine current volatility regime"""
        if market_volatility < self.volatility_threshold_low:
            return 'LOW'
        elif market_volatility < self.volatility_threshold_high:
            return 'NORMAL'
        else:
            return 'HIGH'

    def _drawdown_adjustment(self, current_drawdown: float) -> float:
        """
        Adjust position sizes based on current drawdown
        Reduce exposure during drawdowns
        """
        dd_abs = abs(current_drawdown)

        if dd_abs < 0.10:
            return 1.0
        elif dd_abs < 0.20:
            return 0.90
        elif dd_abs < 0.30:
            return 0.75
        else:
            return 0.60

    def _volatility_adjustment(self, vol_regime: str) -> float:
        """
        Adjust position sizes based on volatility regime
        Reduce exposure in high volatility
        """
        if vol_regime == 'LOW':
            return 1.1
        elif vol_regime == 'NORMAL':
            return 1.0
        else:
            return 0.80