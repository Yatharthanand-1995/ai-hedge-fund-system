# Test Suite Organization

This directory contains all tests for the AI Hedge Fund System, organized by test type and scope.

## Directory Structure

```
tests/
├── unit/               # Unit tests for individual components
│   ├── agents/        # Tests for individual agents (fundamentals, momentum, etc.)
│   ├── core/          # Tests for core system components (scorer, regime detection)
│   └── data/          # Tests for data providers and utilities
├── integration/       # Integration tests for multiple components
└── system/            # End-to-end system tests
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test Levels
```bash
# Unit tests only (fast)
pytest tests/unit -v

# Integration tests
pytest tests/integration -v

# System tests (slow)
pytest tests/system -v
```

### Run Tests by Marker
```bash
# Skip slow tests
pytest -m "not slow"

# Run only backtesting tests
pytest -m backtest

# Run tests that don't require API access
pytest -m "not requires_api"
```

### Run Specific Test Files
```bash
# Test institutional flow agent
pytest tests/unit/agents/test_institutional_flow_simple.py -v

# Test regime detection
pytest tests/unit/core/test_regime_adaptive.py -v

# Test automated trading
pytest tests/system/test_automated_trading.py -v
```

## Test Categories

### Unit Tests (`tests/unit/`)
Fast, isolated tests for individual components:
- **agents/**: Individual agent logic (fundamentals, momentum, quality, sentiment, institutional flow)
- **core/**: Core system components (stock scorer, regime detection, portfolio manager)
- **data/**: Data providers and utilities

### Integration Tests (`tests/integration/`)
Tests that verify multiple components work together:
- API endpoint integration
- Agent coordination
- Portfolio management workflows
- Backtesting engine integration

### System Tests (`tests/system/`)
End-to-end tests that validate the complete system:
- Full analysis pipeline (all 5 agents)
- Automated trading cycles
- Multi-month simulations
- Performance and regression tests

## Test Markers

Tests can be marked with decorators for selective execution:

```python
import pytest

@pytest.mark.unit
def test_fundamentals_scoring():
    """Unit test example"""
    pass

@pytest.mark.slow
@pytest.mark.backtest
def test_5year_backtest():
    """Slow backtest example"""
    pass

@pytest.mark.requires_api
def test_live_data_fetch():
    """Test requiring external API"""
    pass
```

## Writing Tests

### Best Practices
1. **Isolation**: Unit tests should not depend on external APIs or files
2. **Mocking**: Use pytest fixtures and mocking for external dependencies
3. **Descriptive Names**: Test names should describe what they verify
4. **Assertions**: Use clear, specific assertions with helpful messages
5. **Cleanup**: Ensure tests clean up any created files/resources

### Example Test Structure
```python
import pytest
from agents.fundamentals_agent import FundamentalsAgent

@pytest.mark.unit
class TestFundamentalsAgent:
    def test_profitability_scoring_high_margins(self):
        """Should give high profitability score for >20% margins"""
        agent = FundamentalsAgent()
        score = agent._score_profitability(roe=25.0, net_margin=22.0)
        assert score >= 80, "High margins should yield high profitability score"

    def test_handles_missing_data_gracefully(self):
        """Should return low confidence when data is missing"""
        agent = FundamentalsAgent()
        result = agent.analyze("INVALID_SYMBOL")
        assert result['confidence'] < 0.5
```

## Continuous Integration

Tests are automatically run on:
- Every commit (unit + integration tests)
- Pull requests (full test suite including system tests)
- Nightly builds (includes slow tests and backtests)

## Troubleshooting

### Import Errors
Make sure you're running tests from the project root:
```bash
cd /path/to/ai_hedge_fund_system
pytest
```

### API Rate Limits
Some tests may fail if API rate limits are exceeded. Use mocking or the `--skip-requires-api` flag:
```bash
pytest -m "not requires_api"
```

### Slow Tests
Skip slow tests during development:
```bash
pytest -m "not slow" -x  # Stop on first failure
```

## Coverage Reports

Generate test coverage reports:
```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

## Adding New Tests

When adding new tests:
1. Place in the appropriate directory (unit/integration/system)
2. Follow naming convention: `test_<component>_<scenario>.py`
3. Add appropriate markers (`@pytest.mark.unit`, etc.)
4. Update this README if adding new test categories
