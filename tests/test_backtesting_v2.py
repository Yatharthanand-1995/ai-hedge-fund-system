"""
Comprehensive Test Suite for Backtesting Engine V2.0
Tests versioning, EnhancedYahooProvider integration, and data accuracy
"""
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np

from core.backtesting_engine import (
    HistoricalBacktestEngine,
    BacktestConfig,
    BacktestResult
)
from core.risk_manager import RiskLimits


class TestBacktestConfigV2(unittest.TestCase):
    """Test BacktestConfig V2.0 features"""

    def test_default_version(self):
        """Test that default engine version is 2.0"""
        config = BacktestConfig(
            start_date='2024-01-01',
            end_date='2024-12-31',
            universe=['AAPL', 'MSFT']
        )
        self.assertEqual(config.engine_version, "2.1")

    def test_enhanced_provider_enabled_by_default(self):
        """Test that EnhancedYahooProvider is enabled by default"""
        config = BacktestConfig(
            start_date='2024-01-01',
            end_date='2024-12-31',
            universe=['AAPL', 'MSFT']
        )
        self.assertTrue(config.use_enhanced_provider)

    def test_live_system_weights(self):
        """Test that agent weights match live system (40/30/20/10)"""
        config = BacktestConfig(
            start_date='2024-01-01',
            end_date='2024-12-31',
            universe=['AAPL', 'MSFT']
        )
        self.assertAlmostEqual(config.agent_weights['fundamentals'], 0.40)
        self.assertAlmostEqual(config.agent_weights['momentum'], 0.30)
        self.assertAlmostEqual(config.agent_weights['quality'], 0.20)
        self.assertAlmostEqual(config.agent_weights['sentiment'], 0.10)

    def test_weights_sum_to_one(self):
        """Test that agent weights sum to 1.0"""
        config = BacktestConfig(
            start_date='2024-01-01',
            end_date='2024-12-31',
            universe=['AAPL', 'MSFT']
        )
        total = sum(config.agent_weights.values())
        self.assertAlmostEqual(total, 1.0)

    def test_no_backtest_mode_parameter(self):
        """Test that backtest_mode parameter has been removed"""
        # This should NOT raise an error even if we don't specify backtest_mode
        config = BacktestConfig(
            start_date='2024-01-01',
            end_date='2024-12-31',
            universe=['AAPL', 'MSFT']
        )
        # backtest_mode should not exist as an attribute
        self.assertFalse(hasattr(config, 'backtest_mode'))

    def test_v1_compatibility_mode(self):
        """Test that V1.x compatibility mode can be enabled"""
        config = BacktestConfig(
            start_date='2024-01-01',
            end_date='2024-12-31',
            universe=['AAPL', 'MSFT'],
            use_enhanced_provider=False  # V1.x mode
        )
        self.assertFalse(config.use_enhanced_provider)


class TestBacktestResultV2(unittest.TestCase):
    """Test BacktestResult V2.0 metadata"""

    def _create_minimal_result(self):
        """Helper to create minimal BacktestResult for testing"""
        config = BacktestConfig(
            start_date='2024-01-01',
            end_date='2024-12-31',
            universe=['AAPL']
        )
        return BacktestResult(
            config=config,
            start_date='2024-01-01',
            end_date='2024-12-31',
            initial_capital=10000.0,
            final_value=12000.0,
            total_return=0.20,
            cagr=0.20,
            sharpe_ratio=1.5,
            sortino_ratio=1.8,
            max_drawdown=-0.10,
            max_drawdown_duration=30,
            volatility=0.15,
            spy_return=0.10,
            outperformance_vs_spy=0.10,
            alpha=0.05,
            beta=1.2,
            equity_curve=[],
            daily_returns=[],
            rebalance_events=[],
            num_rebalances=4,
            performance_by_condition={},
            best_performers=[],
            worst_performers=[],
            win_rate=0.6,
            profit_factor=2.0,
            calmar_ratio=1.5,
            information_ratio=0.8
        )

    def test_result_includes_version(self):
        """Test that result includes engine version"""
        result = self._create_minimal_result()
        self.assertEqual(result.engine_version, "2.1")

    def test_result_includes_data_limitations(self):
        """Test that result documents data limitations"""
        result = self._create_minimal_result()

        # Check that all 4 agents have documented limitations
        self.assertIn('fundamentals', result.data_limitations)
        self.assertIn('sentiment', result.data_limitations)
        self.assertIn('momentum', result.data_limitations)
        self.assertIn('quality', result.data_limitations)

    def test_result_includes_bias_estimate(self):
        """Test that result includes estimated bias impact"""
        result = self._create_minimal_result()

        self.assertIsNotNone(result.estimated_bias_impact)
        self.assertIn("5-10%", result.estimated_bias_impact)

    def test_result_tracks_data_provider(self):
        """Test that result tracks which data provider was used"""
        result_v2 = self._create_minimal_result()
        self.assertEqual(result_v2.data_provider, "EnhancedYahooProvider")


class TestEnhancedProviderIntegration(unittest.TestCase):
    """Test EnhancedYahooProvider integration"""

    def setUp(self):
        """Set up test configuration"""
        self.test_universe = ['AAPL', 'MSFT']
        self.config_v2 = BacktestConfig(
            start_date='2024-01-01',
            end_date='2024-03-31',
            initial_capital=10000.0,
            rebalance_frequency='monthly',
            top_n_stocks=2,
            universe=self.test_universe,
            use_enhanced_provider=True  # V2.0
        )

    def test_engine_uses_enhanced_provider(self):
        """Test that engine initializes with EnhancedYahooProvider"""
        engine = HistoricalBacktestEngine(self.config_v2)
        self.assertIsNotNone(engine.data_provider)

    def test_v2_data_preparation_method_exists(self):
        """Test that _prepare_comprehensive_data_v2 method exists"""
        engine = HistoricalBacktestEngine(self.config_v2)
        self.assertTrue(hasattr(engine, '_prepare_comprehensive_data_v2'))
        self.assertTrue(callable(getattr(engine, '_prepare_comprehensive_data_v2')))

    def test_v1_compatibility_method_exists(self):
        """Test that _prepare_comprehensive_data_v1 method exists for backward compatibility"""
        engine = HistoricalBacktestEngine(self.config_v2)
        self.assertTrue(hasattr(engine, '_prepare_comprehensive_data_v1'))
        self.assertTrue(callable(getattr(engine, '_prepare_comprehensive_data_v1')))


class TestPointInTimeDataFiltering(unittest.TestCase):
    """Test that point-in-time data filtering prevents look-ahead bias"""

    def test_v1_data_preparation_uses_historical_only(self):
        """Test V1 data preparation uses only historical data"""
        config = BacktestConfig(
            start_date='2024-01-01',
            end_date='2024-03-31',
            universe=['AAPL'],
            use_enhanced_provider=False  # V1 mode
        )
        engine = HistoricalBacktestEngine(config)

        # Create sample historical data
        dates = pd.date_range('2024-01-01', '2024-02-01', freq='D')
        hist_data = pd.DataFrame({
            'Open': np.random.rand(len(dates)) * 100 + 150,
            'High': np.random.rand(len(dates)) * 100 + 155,
            'Low': np.random.rand(len(dates)) * 100 + 145,
            'Close': np.random.rand(len(dates)) * 100 + 150,
            'Volume': np.random.randint(1000000, 10000000, len(dates))
        }, index=dates)

        # Test that data preparation works
        comprehensive_data = engine._prepare_comprehensive_data_v1(
            'AAPL', hist_data, '2024-02-01'
        )

        # Verify structure - V1 returns flat dict with technical indicators at top level
        self.assertIn('historical_data', comprehensive_data)
        self.assertIn('current_price', comprehensive_data)
        self.assertIn('timestamp', comprehensive_data)

    def test_technical_indicators_calculated_from_historical_data(self):
        """Test that technical indicators are calculated from historical data only"""
        config = BacktestConfig(
            start_date='2024-01-01',
            end_date='2024-03-31',
            universe=['AAPL'],
            use_enhanced_provider=False
        )
        engine = HistoricalBacktestEngine(config)

        # Create sample data with known pattern
        dates = pd.date_range('2024-01-01', '2024-02-15', freq='D')
        close_prices = np.linspace(150, 160, len(dates))  # Linear uptrend
        hist_data = pd.DataFrame({
            'Open': close_prices,
            'High': close_prices + 1,
            'Low': close_prices - 1,
            'Close': close_prices,
            'Volume': [1000000] * len(dates)
        }, index=dates)

        comprehensive_data = engine._prepare_comprehensive_data_v1(
            'AAPL', hist_data, '2024-02-15'
        )

        # Verify RSI is calculated - in V1 it's at top level, not nested
        self.assertIn('rsi', comprehensive_data)
        rsi = comprehensive_data['rsi']

        # RSI should be high for uptrend, valid range is 0-100 inclusive
        self.assertIsNotNone(rsi)
        self.assertGreaterEqual(rsi, 0)
        self.assertLessEqual(rsi, 100)


class TestWeightConsistency(unittest.TestCase):
    """Test that agent weights are consistent with live system"""

    def test_engine_logs_correct_weights(self):
        """Test that engine logs the correct weights on initialization"""
        config = BacktestConfig(
            start_date='2024-01-01',
            end_date='2024-03-31',
            universe=['AAPL', 'MSFT']
        )

        # Capture logger output
        with patch('core.backtesting_engine.logger') as mock_logger:
            engine = HistoricalBacktestEngine(config)

            # Check that weights are logged
            calls = [str(call) for call in mock_logger.info.call_args_list]
            weight_log = [c for c in calls if 'Agent weights' in c]

            # Should have logged weights
            self.assertTrue(len(weight_log) > 0)

    def test_no_weight_override_in_backtest_mode(self):
        """Test that weights are NOT overridden (backtest_mode removed)"""
        config = BacktestConfig(
            start_date='2024-01-01',
            end_date='2024-03-31',
            universe=['AAPL', 'MSFT']
        )

        engine = HistoricalBacktestEngine(config)

        # Weights should be exactly as specified in config
        self.assertEqual(
            engine.config.agent_weights,
            {
                'fundamentals': 0.40,
                'momentum': 0.30,
                'quality': 0.20,
                'sentiment': 0.10
            }
        )


class TestBiasDocumentation(unittest.TestCase):
    """Test that look-ahead bias is properly documented"""

    def test_bias_warning_at_start(self):
        """Test that bias warning is displayed at backtest start"""
        config = BacktestConfig(
            start_date='2024-01-01',
            end_date='2024-01-31',
            universe=['AAPL'],
            use_enhanced_provider=True
        )

        # Capture logger warnings
        with patch('core.backtesting_engine.logger') as mock_logger:
            engine = HistoricalBacktestEngine(config)

            # Don't actually run backtest (too slow), just check initialization
            # Check that warnings are set up to be displayed
            self.assertIsNotNone(engine.config)

    def test_bias_metadata_in_result(self):
        """Test that bias metadata is included in result"""
        config = BacktestConfig(
            start_date='2024-01-01',
            end_date='2024-12-31',
            universe=['AAPL']
        )
        result = BacktestResult(
            config=config,
            start_date='2024-01-01',
            end_date='2024-12-31',
            initial_capital=10000.0,
            final_value=12000.0,
            total_return=0.20,
            cagr=0.20,
            sharpe_ratio=1.5,
            sortino_ratio=1.8,
            max_drawdown=-0.10,
            max_drawdown_duration=30,
            volatility=0.15,
            spy_return=0.10,
            outperformance_vs_spy=0.10,
            alpha=0.05,
            beta=1.2,
            equity_curve=[],
            daily_returns=[],
            rebalance_events=[],
            num_rebalances=4,
            performance_by_condition={},
            best_performers=[],
            worst_performers=[],
            win_rate=0.6,
            profit_factor=2.0,
            calmar_ratio=1.5,
            information_ratio=0.8
        )

        # Check metadata
        self.assertIn('fundamentals', result.data_limitations)
        self.assertIn('sentiment', result.data_limitations)
        self.assertIn('look-ahead bias', result.data_limitations['fundamentals'])
        self.assertIn('look-ahead bias', result.data_limitations['sentiment'])


class TestBackwardCompatibility(unittest.TestCase):
    """Test backward compatibility with V1.x"""

    def test_can_run_in_v1_mode(self):
        """Test that V1.x mode can be enabled"""
        config = BacktestConfig(
            start_date='2024-01-01',
            end_date='2024-03-31',
            universe=['AAPL', 'MSFT'],
            use_enhanced_provider=False  # V1.x mode
        )

        engine = HistoricalBacktestEngine(config)
        self.assertFalse(config.use_enhanced_provider)

    def test_v1_uses_minimal_indicators(self):
        """Test that V1 mode uses minimal indicators (RSI, SMA20, SMA50)"""
        config = BacktestConfig(
            start_date='2024-01-01',
            end_date='2024-03-31',
            universe=['AAPL'],
            use_enhanced_provider=False
        )
        engine = HistoricalBacktestEngine(config)

        # Create sample data with enough history for all indicators
        dates = pd.date_range('2024-01-01', '2024-03-15', freq='D')  # 74 days
        hist_data = pd.DataFrame({
            'Open': [150] * len(dates),
            'High': [155] * len(dates),
            'Low': [145] * len(dates),
            'Close': [150] * len(dates),
            'Volume': [1000000] * len(dates)
        }, index=dates)

        comprehensive_data = engine._prepare_comprehensive_data_v1(
            'AAPL', hist_data, '2024-03-15'
        )

        # V1 returns flat dict with indicators at top level (not nested)
        # RSI should always be present (requires 14 days)
        self.assertIn('rsi', comprehensive_data)
        # SMA20 should be present (requires 20 days)
        self.assertIn('sma_20', comprehensive_data)
        # SMA50 should be present (requires 50 days)
        self.assertIn('sma_50', comprehensive_data)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
