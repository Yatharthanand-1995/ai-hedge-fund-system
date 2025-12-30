"""
Standardized Agent Response Utilities
Provides consistent response formats across all agents
"""

from typing import Dict, Optional


def create_success_response(
    score: float,
    confidence: float,
    metrics: Dict,
    reasoning: str
) -> Dict:
    """
    Create a standardized success response for all agents

    Args:
        score: Agent score (0-100)
        confidence: Confidence level (0-1)
        metrics: Dictionary of agent-specific metrics
        reasoning: Human-readable explanation of the score

    Returns:
        Standardized response dictionary
    """
    return {
        'score': score,
        'confidence': confidence,
        'metrics': metrics,
        'reasoning': reasoning,
        'error': False
    }


def create_error_response(
    error_type: str,
    error_message: str,
    partial_metrics: Optional[Dict] = None
) -> Dict:
    """
    Create a standardized error response for all agents

    Args:
        error_type: Type of error ('NO_DATA', 'TIMEOUT', 'CALCULATION_ERROR', 'INVALID_SYMBOL')
        error_message: Human-readable error message
        partial_metrics: Optional partial metrics if some data was available

    Returns:
        Standardized error response dictionary
    """
    return {
        'score': None,  # Explicitly None for errors
        'confidence': 0.0,
        'metrics': partial_metrics or {},
        'reasoning': error_message,
        'error': True,
        'error_type': error_type
    }


def create_neutral_response(
    reasoning: str,
    partial_metrics: Optional[Dict] = None,
    confidence: float = 0.5
) -> Dict:
    """
    Create a neutral/no-signal response for ambiguous situations

    Args:
        reasoning: Explanation of why the signal is neutral
        partial_metrics: Optional partial metrics
        confidence: Confidence in the neutral assessment (default 0.5)

    Returns:
        Standardized neutral response dictionary
    """
    return {
        'score': 50.0,  # Neutral score
        'confidence': confidence,
        'metrics': partial_metrics or {},
        'reasoning': reasoning,
        'error': False
    }


# Error type constants
class ErrorType:
    """Standard error types for all agents"""
    NO_DATA = 'NO_DATA'
    TIMEOUT = 'TIMEOUT'
    CALCULATION_ERROR = 'CALCULATION_ERROR'
    INVALID_SYMBOL = 'INVALID_SYMBOL'
    API_ERROR = 'API_ERROR'
    INSUFFICIENT_DATA = 'INSUFFICIENT_DATA'
