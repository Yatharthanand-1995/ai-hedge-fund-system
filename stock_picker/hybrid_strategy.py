"""
Hybrid Strategy Implementation
Combines ML optimization, position sizing, and risk management
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime, timedelta

from .position_sizing import PositionSizer
from .ml import BayesianWeightOptimizer, RegimeDetector
from .risk import RiskMetrics, DrawdownMonitor

logger = logging.getLogger(__name__)


class HybridStrategy:
    """
    Hybrid strategy combining multiple optimization approaches

    Features:
    1. ML-optimized agent weights
    2. Constrained position sizing
    3. Regime-based adaptation
    4. Dynamic risk management
    """

    def __init__(self,
                 target_metric: str = 'return',
                 max_position_size: float = 0.35,
                 min_position_size: float = 0.10,
                 rebalance_threshold: float = 0.05):
        """
        Initialize hybrid strategy

        Args:
            target_metric: ML optimization target ('return', 'sharpe', 'calmar')
            max_position_size: Maximum weight per position (35%)
            min_position_size: Minimum weight per position (10%)
            rebalance_threshold: Threshold for triggering rebalancing (5%)
        """
        self.target_metric = target_metric
        self.max_position_size = max_position_size
        self.min_position_size = min_position_size
        self.rebalance_threshold = rebalance_threshold

        # Initialize components
        self.ml_optimizer = BayesianWeightOptimizer(target_metric=target_metric, n_iter=30)
        self.position_sizer = PositionSizer(method='max_sharpe')
        self.regime_detector = RegimeDetector()
        self.risk_monitor = RiskMetrics(confidence_level=0.95)
        self.drawdown_monitor = DrawdownMonitor()

        # Strategy state
        self.current_agent_weights = {'fundamentals': 0.4, 'momentum': 0.3, 'quality': 0.2, 'sentiment': 0.1}
        self.current_position_weights = {}
        self.last_rebalance_date = None
        self.optimization_history = []

        logger.info(f"HybridStrategy initialized (target: {target_metric}, max_pos: {max_position_size:.1%})")

    def optimize_agent_weights(self,
                              agent_scores: pd.DataFrame,
                              portfolio_returns: pd.Series,
                              market_data: Optional[pd.DataFrame] = None) -> Dict[str, float]:
        """
        Optimize agent weights using ML

        Args:
            agent_scores: Historical agent scores
            portfolio_returns: Historical portfolio returns
            market_data: Optional market data for regime detection

        Returns:
            Optimized agent weights
        """
        try:
            # Detect current market regime
            current_regime = 'NORMAL'
            if market_data is not None and len(market_data) > 0:
                regimes = self.regime_detector.detect_all_regimes(market_data)
                if len(regimes) > 0 and 'composite_regime' in regimes.columns:
                    current_regime = regimes['composite_regime'].iloc[-1]

            logger.info(f"Current market regime: {current_regime}")

            # Get regime-based starting weights
            regime_weights = self.regime_detector.get_regime_weights(current_regime)

            # ML optimization with regime-aware bounds
            bounds = self._get_regime_bounds(current_regime)

            optimized_weights = self.ml_optimizer.optimize_weights(
                agent_scores, portfolio_returns, bounds=bounds
            )

            # Store optimization result
            self.optimization_history.append({
                'date': datetime.now(),
                'regime': current_regime,
                'weights': optimized_weights,
                'target_metric': self.target_metric
            })

            self.current_agent_weights = optimized_weights
            logger.info(f"Agent weights optimized: {optimized_weights}")

            return optimized_weights

        except Exception as e:
            logger.error(f"Agent weight optimization failed: {e}")
            return self.current_agent_weights

    def calculate_position_weights(self,
                                 symbols: List[str],
                                 returns_data: pd.DataFrame,
                                 agent_scores: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """
        Calculate position weights with constraints

        Args:
            symbols: Stock symbols
            returns_data: Historical returns data
            agent_scores: Optional current agent scores for symbols

        Returns:
            Position weights dictionary
        """
        try:
            # Use constrained Max Sharpe optimization
            base_weights = self.position_sizer.calculate_weights(symbols, returns_data)

            # Apply position size constraints
            constrained_weights = self._apply_position_constraints(base_weights)

            # Apply risk-based adjustments
            risk_adjusted_weights = self._apply_risk_adjustments(
                constrained_weights, symbols, returns_data
            )

            self.current_position_weights = risk_adjusted_weights
            logger.info(f"Position weights calculated: {risk_adjusted_weights}")

            return risk_adjusted_weights

        except Exception as e:
            logger.error(f"Position weight calculation failed: {e}")
            # Fallback to equal weights with constraints
            n = len(symbols)
            equal_weights = {sym: 1.0/n for sym in symbols}
            return self._apply_position_constraints(equal_weights)

    def _apply_position_constraints(self, weights: Dict[str, float]) -> Dict[str, float]:
        """Apply position size constraints"""
        try:
            constrained_weights = {}

            for symbol, weight in weights.items():
                # Apply min/max constraints
                constrained_weight = max(self.min_position_size,
                                       min(self.max_position_size, weight))
                constrained_weights[symbol] = constrained_weight

            # Renormalize to sum to 1
            total_weight = sum(constrained_weights.values())
            if total_weight > 0:
                constrained_weights = {
                    sym: w / total_weight
                    for sym, w in constrained_weights.items()
                }

            logger.info(f"Applied position constraints: min={self.min_position_size:.1%}, max={self.max_position_size:.1%}")
            return constrained_weights

        except Exception as e:
            logger.error(f"Position constraint application failed: {e}")
            return weights

    def _apply_risk_adjustments(self,
                               weights: Dict[str, float],
                               symbols: List[str],
                               returns_data: pd.DataFrame) -> Dict[str, float]:
        """Apply risk-based weight adjustments"""
        try:
            # Calculate portfolio risk metrics
            portfolio_returns = pd.Series(0.0, index=returns_data.index)
            for symbol, weight in weights.items():
                if symbol in returns_data.columns:
                    portfolio_returns += weight * returns_data[symbol]

            # Calculate portfolio values for drawdown analysis
            portfolio_values = (1 + portfolio_returns).cumprod() * 100

            # Get current drawdown
            current_dd = self.drawdown_monitor.calculate_current_drawdown(portfolio_values)

            if 'current_drawdown' in current_dd:
                dd_pct = abs(current_dd['current_drawdown'])
                alert_level = current_dd.get('alert_level', 'NORMAL')

                # Risk-based position scaling
                if alert_level == 'SEVERE':
                    # Severe drawdown: reduce position concentration
                    risk_factor = 0.70
                    logger.warning(f"SEVERE drawdown detected: {dd_pct:.1%}, reducing positions")
                elif alert_level == 'MODERATE':
                    # Moderate drawdown: slight position reduction
                    risk_factor = 0.85
                    logger.info(f"MODERATE drawdown detected: {dd_pct:.1%}, scaling positions")
                elif alert_level == 'WARNING':
                    # Warning level: minimal adjustment
                    risk_factor = 0.95
                    logger.info(f"WARNING drawdown detected: {dd_pct:.1%}")
                else:
                    risk_factor = 1.0

                if risk_factor < 1.0:
                    # Scale down positions and move toward equal weight
                    equal_weight = 1.0 / len(symbols)
                    adjusted_weights = {}

                    for symbol, weight in weights.items():
                        # Blend toward equal weight based on risk factor
                        blend_factor = 1.0 - risk_factor
                        adjusted_weight = (weight * risk_factor +
                                         equal_weight * blend_factor)
                        adjusted_weights[symbol] = adjusted_weight

                    # Renormalize
                    total = sum(adjusted_weights.values())
                    adjusted_weights = {sym: w/total for sym, w in adjusted_weights.items()}

                    logger.info(f"Applied risk adjustment factor: {risk_factor:.2f}")
                    return adjusted_weights

            return weights

        except Exception as e:
            logger.error(f"Risk adjustment failed: {e}")
            return weights

    def _get_regime_bounds(self, regime: str) -> Dict[str, Tuple[float, float]]:
        """Get optimization bounds based on market regime"""
        # Base bounds
        base_bounds = {
            'fundamentals': (0.2, 0.6),
            'momentum': (0.1, 0.5),
            'quality': (0.1, 0.4),
            'sentiment': (0.0, 0.3)
        }

        # Regime-specific adjustments
        if 'BULL' in regime:
            # Bull market: favor momentum and growth
            base_bounds['momentum'] = (0.2, 0.6)
            base_bounds['fundamentals'] = (0.1, 0.5)
        elif 'BEAR' in regime:
            # Bear market: favor quality and fundamentals
            base_bounds['quality'] = (0.2, 0.5)
            base_bounds['fundamentals'] = (0.3, 0.7)
            base_bounds['momentum'] = (0.0, 0.3)
        elif 'HIGH_VOL' in regime:
            # High volatility: favor quality and reduce sentiment
            base_bounds['quality'] = (0.2, 0.5)
            base_bounds['sentiment'] = (0.0, 0.2)

        return base_bounds

    def should_rebalance(self,
                        current_weights: Dict[str, float],
                        current_prices: pd.Series,
                        days_since_rebalance: int = 0) -> bool:
        """
        Determine if rebalancing is needed

        Args:
            current_weights: Current position weights
            current_prices: Latest prices
            days_since_rebalance: Days since last rebalance

        Returns:
            True if rebalancing is recommended
        """
        try:
            # Time-based rebalancing (quarterly)
            if days_since_rebalance >= 90:
                logger.info("Time-based rebalancing triggered (90+ days)")
                return True

            # Drift-based rebalancing
            if self.current_position_weights:
                max_drift = 0
                for symbol in current_weights:
                    if symbol in self.current_position_weights:
                        target_weight = self.current_position_weights[symbol]
                        current_weight = current_weights[symbol]
                        drift = abs(current_weight - target_weight)
                        max_drift = max(max_drift, drift)

                if max_drift > self.rebalance_threshold:
                    logger.info(f"Drift-based rebalancing triggered (max drift: {max_drift:.1%})")
                    return True

            # Risk-based rebalancing
            # Calculate portfolio returns from prices
            returns = current_prices.pct_change().dropna()
            if len(returns) > 20:
                portfolio_values = (1 + returns).cumprod() * 100
                current_dd = self.drawdown_monitor.calculate_current_drawdown(portfolio_values)

                if 'alert_level' in current_dd and current_dd['alert_level'] in ['MODERATE', 'SEVERE']:
                    logger.info(f"Risk-based rebalancing triggered ({current_dd['alert_level']} drawdown)")
                    return True

            return False

        except Exception as e:
            logger.error(f"Rebalancing check failed: {e}")
            return days_since_rebalance >= 90  # Default to quarterly

    def generate_strategy_report(self,
                               portfolio_values: pd.Series,
                               positions: Dict[str, float]) -> str:
        """Generate comprehensive strategy report"""
        try:
            report = []
            report.append("=" * 60)
            report.append("HYBRID STRATEGY REPORT")
            report.append("=" * 60)
            report.append("")

            # Strategy configuration
            report.append("Strategy Configuration:")
            report.append(f"  Target Metric: {self.target_metric}")
            report.append(f"  Max Position Size: {self.max_position_size:.1%}")
            report.append(f"  Min Position Size: {self.min_position_size:.1%}")
            report.append(f"  Rebalance Threshold: {self.rebalance_threshold:.1%}")
            report.append("")

            # Current agent weights
            report.append("Current Agent Weights:")
            for agent, weight in self.current_agent_weights.items():
                report.append(f"  {agent}: {weight:.1%}")
            report.append("")

            # Current position weights
            report.append("Current Position Weights:")
            for symbol, weight in positions.items():
                report.append(f"  {symbol}: {weight:.1%}")
            report.append("")

            # Portfolio metrics
            returns = portfolio_values.pct_change().dropna()
            if len(returns) > 0:
                total_return = (portfolio_values.iloc[-1] / portfolio_values.iloc[0] - 1) * 100
                sharpe = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0

                # Drawdown
                running_max = portfolio_values.expanding().max()
                drawdown = (portfolio_values - running_max) / running_max
                max_drawdown = drawdown.min() * 100
                current_drawdown = (portfolio_values.iloc[-1] - portfolio_values.max()) / portfolio_values.max() * 100

                report.append("Performance Metrics:")
                report.append(f"  Total Return: {total_return:.1f}%")
                report.append(f"  Sharpe Ratio: {sharpe:.2f}")
                report.append(f"  Max Drawdown: {max_drawdown:.1f}%")
                report.append(f"  Current Drawdown: {current_drawdown:.1f}%")
                report.append("")

            # Optimization history
            if self.optimization_history:
                report.append("Recent Optimizations:")
                for opt in self.optimization_history[-3:]:  # Last 3
                    report.append(f"  {opt['date'].strftime('%Y-%m-%d')}: {opt['regime']} regime")
                report.append("")

            report.append("=" * 60)

            return "\n".join(report)

        except Exception as e:
            logger.error(f"Strategy report generation failed: {e}")
            return f"Error generating strategy report: {e}"

    def get_strategy_summary(self) -> Dict:
        """Get strategy summary for API/monitoring"""
        try:
            return {
                'strategy_type': 'hybrid',
                'target_metric': self.target_metric,
                'position_constraints': {
                    'max_size': self.max_position_size,
                    'min_size': self.min_position_size
                },
                'current_agent_weights': self.current_agent_weights,
                'current_position_weights': self.current_position_weights,
                'last_rebalance': self.last_rebalance_date,
                'optimization_count': len(self.optimization_history)
            }
        except Exception as e:
            logger.error(f"Strategy summary failed: {e}")
            return {'error': str(e)}