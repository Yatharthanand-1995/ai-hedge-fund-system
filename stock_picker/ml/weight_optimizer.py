"""
Weight Optimizer
Machine Learning-based optimization for agent weights
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Callable
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class WeightOptimizer:
    """
    Base class for agent weight optimization

    Optimizes the weights for different agents (fundamentals, momentum, quality, sentiment)
    to maximize risk-adjusted returns
    """

    def __init__(self, target_metric: str = 'sharpe'):
        """
        Initialize weight optimizer

        Args:
            target_metric: Optimization target
                - 'sharpe': Sharpe ratio
                - 'calmar': Calmar ratio (return/max_drawdown)
                - 'sortino': Sortino ratio
                - 'return': Total return
        """
        self.target_metric = target_metric
        self.valid_metrics = ['sharpe', 'calmar', 'sortino', 'return']

        if target_metric not in self.valid_metrics:
            raise ValueError(f"target_metric must be one of {self.valid_metrics}")

        logger.info(f"WeightOptimizer initialized (target: {target_metric})")

    def calculate_objective(self, weights: Dict[str, float],
                          agent_scores: pd.DataFrame,
                          returns_data: pd.Series) -> float:
        """
        Calculate objective function value for given weights

        Args:
            weights: Agent weights dict
            agent_scores: DataFrame with agent scores over time
            returns_data: Actual returns for validation

        Returns:
            Objective function value (higher is better)
        """
        try:
            # Ensure weights sum to 1
            total_weight = sum(weights.values())
            if total_weight == 0:
                return -np.inf

            normalized_weights = {k: v/total_weight for k, v in weights.items()}

            # Calculate weighted composite scores
            composite_scores = pd.Series(0.0, index=agent_scores.index)

            for agent, weight in normalized_weights.items():
                if agent in agent_scores.columns:
                    composite_scores += weight * agent_scores[agent]

            # Align with returns data
            aligned_data = pd.DataFrame({
                'scores': composite_scores,
                'returns': returns_data
            }).dropna()

            if len(aligned_data) < 10:
                logger.warning("Insufficient aligned data for optimization")
                return -np.inf

            returns = aligned_data['returns']

            if self.target_metric == 'sharpe':
                if returns.std() == 0:
                    return 0
                sharpe = returns.mean() / returns.std() * np.sqrt(252)
                return sharpe

            elif self.target_metric == 'calmar':
                total_return = (1 + returns).prod() - 1

                # Calculate max drawdown
                cumulative = (1 + returns).cumprod()
                running_max = cumulative.expanding().max()
                drawdown = (cumulative - running_max) / running_max
                max_dd = abs(drawdown.min())

                if max_dd == 0:
                    return total_return if total_return > 0 else 0

                calmar = total_return / max_dd
                return calmar

            elif self.target_metric == 'sortino':
                downside_returns = returns[returns < 0]
                if len(downside_returns) == 0 or downside_returns.std() == 0:
                    return returns.mean() * np.sqrt(252)

                sortino = returns.mean() / downside_returns.std() * np.sqrt(252)
                return sortino

            elif self.target_metric == 'return':
                return returns.mean() * 252

        except Exception as e:
            logger.error(f"Objective calculation failed: {e}")
            return -np.inf

    def optimize_weights(self, agent_scores: pd.DataFrame,
                        returns_data: pd.Series,
                        bounds: Optional[Dict[str, Tuple[float, float]]] = None) -> Dict[str, float]:
        """
        Optimize agent weights

        Args:
            agent_scores: Historical agent scores
            returns_data: Historical returns
            bounds: Weight bounds for each agent

        Returns:
            Optimized weights dict
        """
        try:
            from scipy.optimize import minimize

            # Default bounds
            if bounds is None:
                bounds = {
                    'fundamentals': (0.2, 0.6),
                    'momentum': (0.1, 0.5),
                    'quality': (0.1, 0.4),
                    'sentiment': (0.0, 0.3)
                }

            agents = list(bounds.keys())
            n_agents = len(agents)

            # Initial weights (current strategy: 40/30/20/10)
            initial_weights = np.array([0.4, 0.3, 0.2, 0.1])

            def objective_func(weights_array):
                weights_dict = dict(zip(agents, weights_array))
                return -self.calculate_objective(weights_dict, agent_scores, returns_data)

            # Constraints
            constraints = [
                {'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}
            ]

            # Bounds array
            bounds_array = [bounds[agent] for agent in agents]

            # Optimization
            result = minimize(
                objective_func,
                initial_weights,
                method='SLSQP',
                bounds=bounds_array,
                constraints=constraints,
                options={'maxiter': 1000, 'ftol': 1e-9}
            )

            if result.success:
                optimal_weights = dict(zip(agents, result.x))

                # Normalize to ensure sum = 1
                total = sum(optimal_weights.values())
                optimal_weights = {k: v/total for k, v in optimal_weights.items()}

                logger.info(f"Optimization successful: {optimal_weights}")
                return optimal_weights
            else:
                logger.warning(f"Optimization failed: {result.message}")
                # Return equal weights as fallback
                return {agent: 1.0/n_agents for agent in agents}

        except Exception as e:
            logger.error(f"Weight optimization failed: {e}")
            # Return current strategy weights as fallback
            return {'fundamentals': 0.4, 'momentum': 0.3, 'quality': 0.2, 'sentiment': 0.1}


class BayesianWeightOptimizer(WeightOptimizer):
    """
    Bayesian optimization for agent weights
    Uses Gaussian Process regression for more efficient optimization
    """

    def __init__(self, target_metric: str = 'sharpe', n_iter: int = 50):
        """
        Initialize Bayesian optimizer

        Args:
            target_metric: Optimization target
            n_iter: Number of optimization iterations
        """
        super().__init__(target_metric)
        self.n_iter = n_iter
        logger.info(f"BayesianWeightOptimizer initialized (n_iter: {n_iter})")

    def optimize_weights(self, agent_scores: pd.DataFrame,
                        returns_data: pd.Series,
                        bounds: Optional[Dict[str, Tuple[float, float]]] = None) -> Dict[str, float]:
        """
        Bayesian optimization for agent weights

        Args:
            agent_scores: Historical agent scores
            returns_data: Historical returns
            bounds: Weight bounds for each agent

        Returns:
            Optimized weights dict
        """
        try:
            from skopt import gp_minimize
            from skopt.space import Real
            from skopt.utils import use_named_args

            # Default bounds
            if bounds is None:
                bounds = {
                    'fundamentals': (0.2, 0.6),
                    'momentum': (0.1, 0.5),
                    'quality': (0.1, 0.4),
                    'sentiment': (0.0, 0.3)
                }

            agents = list(bounds.keys())

            # Create search space
            dimensions = [Real(bounds[agent][0], bounds[agent][1], name=agent)
                         for agent in agents]

            @use_named_args(dimensions)
            def objective(**kwargs):
                # Normalize weights to sum to 1
                weights_array = np.array([kwargs[agent] for agent in agents])
                weights_sum = weights_array.sum()

                if weights_sum == 0:
                    return 1e10  # Large positive number (minimize function)

                normalized_weights = {agent: kwargs[agent] / weights_sum
                                    for agent in agents}

                # Calculate negative objective (since gp_minimize minimizes)
                return -self.calculate_objective(normalized_weights, agent_scores, returns_data)

            # Bayesian optimization
            result = gp_minimize(
                func=objective,
                dimensions=dimensions,
                n_calls=self.n_iter,
                n_initial_points=10,
                acq_func='EI',  # Expected Improvement
                random_state=42
            )

            if result.fun != 1e10:
                # Extract optimal weights
                optimal_weights_array = np.array(result.x)
                optimal_weights_sum = optimal_weights_array.sum()

                optimal_weights = {
                    agent: weight / optimal_weights_sum
                    for agent, weight in zip(agents, optimal_weights_array)
                }

                logger.info(f"Bayesian optimization successful: {optimal_weights}")
                logger.info(f"Best objective value: {-result.fun:.4f}")
                return optimal_weights
            else:
                logger.warning("Bayesian optimization failed")
                return super().optimize_weights(agent_scores, returns_data, bounds)

        except ImportError:
            logger.warning("scikit-optimize not available, falling back to scipy")
            return super().optimize_weights(agent_scores, returns_data, bounds)
        except Exception as e:
            logger.error(f"Bayesian optimization failed: {e}")
            return super().optimize_weights(agent_scores, returns_data, bounds)

    def cross_validate_weights(self, agent_scores: pd.DataFrame,
                              returns_data: pd.Series,
                              n_splits: int = 5) -> List[Dict[str, float]]:
        """
        Cross-validate weight optimization

        Args:
            agent_scores: Historical agent scores
            returns_data: Historical returns
            n_splits: Number of CV splits

        Returns:
            List of optimized weights for each split
        """
        try:
            cv_results = []

            # Time series split
            data_length = len(agent_scores)
            split_size = data_length // n_splits

            for i in range(n_splits):
                start_idx = i * split_size
                end_idx = min((i + 1) * split_size, data_length)

                if end_idx - start_idx < 50:  # Minimum data points
                    continue

                train_scores = agent_scores.iloc[start_idx:end_idx]
                train_returns = returns_data.iloc[start_idx:end_idx]

                # Align data
                aligned_data = pd.DataFrame({
                    'scores': train_scores.index,
                    'returns': train_returns
                }).dropna()

                if len(aligned_data) < 20:
                    continue

                # Optimize weights for this split
                optimal_weights = self.optimize_weights(train_scores, train_returns)
                cv_results.append(optimal_weights)

                logger.info(f"CV Split {i+1}/{n_splits}: {optimal_weights}")

            return cv_results

        except Exception as e:
            logger.error(f"Cross-validation failed: {e}")
            return []

    def ensemble_weights(self, cv_results: List[Dict[str, float]]) -> Dict[str, float]:
        """
        Create ensemble weights from cross-validation results

        Args:
            cv_results: List of weight dictionaries from CV

        Returns:
            Ensemble weights (median across splits)
        """
        try:
            if not cv_results:
                return {'fundamentals': 0.4, 'momentum': 0.3, 'quality': 0.2, 'sentiment': 0.1}

            # Extract all agents
            all_agents = set()
            for weights in cv_results:
                all_agents.update(weights.keys())

            # Calculate median weights
            ensemble_weights = {}
            for agent in all_agents:
                agent_weights = [weights.get(agent, 0) for weights in cv_results]
                ensemble_weights[agent] = np.median(agent_weights)

            # Normalize
            total = sum(ensemble_weights.values())
            ensemble_weights = {k: v/total for k, v in ensemble_weights.items()}

            logger.info(f"Ensemble weights: {ensemble_weights}")
            return ensemble_weights

        except Exception as e:
            logger.error(f"Ensemble creation failed: {e}")
            return {'fundamentals': 0.4, 'momentum': 0.3, 'quality': 0.2, 'sentiment': 0.1}