"""
Machine Learning Module
ML-based optimization for trading strategy enhancement
"""

from .weight_optimizer import WeightOptimizer, BayesianWeightOptimizer
from .regime_detector import RegimeDetector
from .feature_engineering import FeatureEngineer

__all__ = [
    'WeightOptimizer',
    'BayesianWeightOptimizer',
    'RegimeDetector',
    'FeatureEngineer'
]