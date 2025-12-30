"""
Centralized Agent Weight Configuration

This module provides a single source of truth for agent weights across the entire system.
All components should import weights from this module to ensure consistency.

The 5-Agent System uses weighted scoring where each agent contributes:
- Fundamentals Agent: 36% (Financial health, valuation, profitability)
- Momentum Agent: 27% (Technical analysis, price trends)
- Quality Agent: 18% (Business quality, operational efficiency)
- Sentiment Agent: 9% (Market sentiment, analyst ratings)
- Institutional Flow Agent: 10% (Smart money detection, volume analysis)

Total: 100% (weights must sum to 1.0)
"""

import os
import logging
from typing import Dict

logger = logging.getLogger(__name__)

# Static agent weights (default configuration)
# These weights are carefully calibrated based on historical performance
STATIC_AGENT_WEIGHTS = {
    'fundamentals': 0.36,      # 36% - Strongest predictor of long-term value
    'momentum': 0.27,          # 27% - Important for entry/exit timing
    'quality': 0.18,           # 18% - Business sustainability factor
    'sentiment': 0.09,         # 09% - Market psychology indicator
    'institutional_flow': 0.10 # 10% - Smart money tracking
}

# Validation
_weight_sum = sum(STATIC_AGENT_WEIGHTS.values())
assert abs(_weight_sum - 1.0) < 0.0001, f"Weights must sum to 1.0, got {_weight_sum}"

# Verify all required agents are present
REQUIRED_AGENTS = {'fundamentals', 'momentum', 'quality', 'sentiment', 'institutional_flow'}
_configured_agents = set(STATIC_AGENT_WEIGHTS.keys())
assert _configured_agents == REQUIRED_AGENTS, \
    f"Weight configuration must include all agents. Missing: {REQUIRED_AGENTS - _configured_agents}"


def get_agent_weights(adaptive: bool = False) -> Dict[str, float]:
    """
    Get agent weights (static or adaptive based on market regime)

    Args:
        adaptive: If True and ENABLE_ADAPTIVE_WEIGHTS environment variable is set,
                 return regime-adjusted weights based on current market conditions.
                 Otherwise, return static weights.

    Returns:
        Dictionary mapping agent names to their weights (summing to 1.0)

    Examples:
        >>> weights = get_agent_weights()
        >>> weights['fundamentals']
        0.36

        >>> # With adaptive weights enabled
        >>> os.environ['ENABLE_ADAPTIVE_WEIGHTS'] = 'true'
        >>> adaptive_weights = get_agent_weights(adaptive=True)
        >>> # Returns regime-adjusted weights
    """
    # Check if adaptive weights should be used
    if adaptive and os.getenv('ENABLE_ADAPTIVE_WEIGHTS', 'false').lower() == 'true':
        try:
            from core.market_regime_service import get_market_regime_service
            regime_service = get_market_regime_service()
            adaptive_weights = regime_service.get_adaptive_weights()

            logger.info(
                f"Using adaptive weights based on market regime: "
                f"{', '.join(f'{k}={v:.0%}' for k, v in adaptive_weights.items())}"
            )
            return adaptive_weights

        except Exception as e:
            logger.warning(
                f"Failed to get adaptive weights, falling back to static: {e}"
            )
            # Fall through to return static weights

    # Return a copy to prevent external modification
    return STATIC_AGENT_WEIGHTS.copy()


def get_weight_percentages() -> Dict[str, int]:
    """
    Get agent weights as percentages (for display purposes)

    Returns:
        Dictionary mapping agent names to their weight percentages

    Example:
        >>> percentages = get_weight_percentages()
        >>> percentages['fundamentals']
        36
    """
    return {
        agent: int(weight * 100)
        for agent, weight in STATIC_AGENT_WEIGHTS.items()
    }


def validate_custom_weights(weights: Dict[str, float]) -> bool:
    """
    Validate that custom weights are valid

    Args:
        weights: Dictionary of agent weights to validate

    Returns:
        True if weights are valid, False otherwise

    Validation checks:
    - All required agents are present
    - All weights are between 0 and 1
    - Weights sum to 1.0 (within tolerance)
    """
    # Check all agents present
    if set(weights.keys()) != REQUIRED_AGENTS:
        logger.error(
            f"Invalid agents in custom weights. "
            f"Required: {REQUIRED_AGENTS}, Got: {set(weights.keys())}"
        )
        return False

    # Check weight ranges
    for agent, weight in weights.items():
        if not 0 <= weight <= 1:
            logger.error(f"Weight for {agent} out of range [0,1]: {weight}")
            return False

    # Check sum
    weight_sum = sum(weights.values())
    if abs(weight_sum - 1.0) > 0.0001:
        logger.error(f"Weights must sum to 1.0, got {weight_sum}")
        return False

    return True


# Export for convenience
__all__ = [
    'STATIC_AGENT_WEIGHTS',
    'get_agent_weights',
    'get_weight_percentages',
    'validate_custom_weights',
    'REQUIRED_AGENTS'
]
