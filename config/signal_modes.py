"""
Signal Mode Configuration for A/B/C Testing
Three distinct signal generation strategies for comparative backtesting
"""

from enum import Enum
from typing import Dict, Any


class SignalMode(Enum):
    """Signal generation modes for testing"""
    BASELINE = "baseline"
    EASY_WINS = "easy_wins"
    FULL_ACADEMIC = "full_academic"


class SignalModeConfig:
    """
    Configuration manager for different signal modes
    Enables rigorous A/B/C testing across identical time periods
    """

    BASELINE = {
        'mode_name': 'BASELINE',
        'description': 'Original signal engine without enhancements',

        'technical_weight': 0.70,
        'volume_weight': 0.30,
        'microstructure_weight': 0.00,

        'enable_stochastic': False,
        'enable_adx_filter': False,
        'enable_mfi': False,
        'enable_dynamic_weighting': False,
        'enable_half_kelly': False,

        'enable_ml_regime': False,
        'enable_order_book': False,
        'enable_volatility_clustering': False,

        'confidence_threshold': 0.15,
        'base_position_size': 0.15,
        'max_position_size': 0.20,
        'min_position_size': 0.03,
    }

    EASY_WINS = {
        'mode_name': 'EASY_WINS',
        'description': 'Academic easy wins: Stochastic, ADX, MFI, Dynamic Weighting, Half-Kelly',

        'technical_weight': 0.50,
        'volume_weight': 0.30,
        'microstructure_weight': 0.20,

        'enable_stochastic': True,
        'enable_adx_filter': True,
        'enable_mfi': True,
        'enable_dynamic_weighting': True,
        'enable_half_kelly': True,

        'enable_ml_regime': False,
        'enable_order_book': False,
        'enable_volatility_clustering': False,

        'confidence_threshold': 0.15,
        'base_position_size': 0.15,
        'max_position_size': 0.20,
        'min_position_size': 0.03,
    }

    FULL_ACADEMIC = {
        'mode_name': 'FULL_ACADEMIC',
        'description': 'All 7 academic components: Easy Wins + ML Regime + Order Book + Vol Clustering',

        'technical_weight': 0.40,
        'volume_weight': 0.30,
        'microstructure_weight': 0.30,

        'enable_stochastic': True,
        'enable_adx_filter': True,
        'enable_mfi': True,
        'enable_dynamic_weighting': True,
        'enable_half_kelly': True,

        'enable_ml_regime': True,
        'enable_order_book': True,
        'enable_volatility_clustering': True,

        'confidence_threshold': 0.15,
        'base_position_size': 0.15,
        'max_position_size': 0.25,
        'min_position_size': 0.03,
    }

    @classmethod
    def get_config(cls, mode: SignalMode) -> Dict[str, Any]:
        """Get configuration for specified signal mode"""
        mode_configs = {
            SignalMode.BASELINE: cls.BASELINE,
            SignalMode.EASY_WINS: cls.EASY_WINS,
            SignalMode.FULL_ACADEMIC: cls.FULL_ACADEMIC
        }

        if isinstance(mode, str):
            mode = SignalMode(mode.lower())

        return mode_configs[mode].copy()

    @classmethod
    def get_all_modes(cls):
        """Return all available signal modes"""
        return [SignalMode.BASELINE, SignalMode.EASY_WINS, SignalMode.FULL_ACADEMIC]


def run_comparative_backtest(start_date: str, end_date: str, symbols: list = None):
    """
    Run comparative backtest across all 3 signal modes

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        symbols: List of symbols to test (optional)

    Returns:
        Dict with results for each mode
    """
    results = {}

    for mode in SignalModeConfig.get_all_modes():
        config = SignalModeConfig.get_config(mode)
        print(f"\n{'='*80}")
        print(f"Running backtest: {config['mode_name']}")
        print(f"Description: {config['description']}")
        print(f"{'='*80}")

        # Here you would run the backtest with this config
        # results[mode.value] = run_backtest(config, start_date, end_date, symbols)

    return results


if __name__ == "__main__":
    print("Signal Mode Configurations:")
    print("\n" + "="*80)

    for mode in SignalModeConfig.get_all_modes():
        config = SignalModeConfig.get_config(mode)
        print(f"\n{config['mode_name']}:")
        print(f"  Description: {config['description']}")
        print(f"  Weights: Tech={config['technical_weight']}, Vol={config['volume_weight']}")
        print(f"  Stochastic: {config['enable_stochastic']}")
        print(f"  ADX Filter: {config['enable_adx_filter']}")
        print(f"  MFI: {config['enable_mfi']}")
        print(f"  Dynamic Weighting: {config['enable_dynamic_weighting']}")
        print(f"  Half-Kelly: {config['enable_half_kelly']}")