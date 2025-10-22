# Archive Directory

This directory contains temporary files and artifacts from the backtesting development phase that are no longer needed for production operation but are preserved for reference.

## Archive Date
October 14, 2025

## Contents Summary

- **56 files archived** in total
- Organized into 5 subdirectories

## Directory Structure

### `backtest_scripts/` (9 files)
Temporary Python scripts used for running various backtest configurations:
- `run_comprehensive_backtest.py`
- `run_fast_backtests.py`
- `run_quick_backtest.py`
- `run_real_agent_backtests.py`
- `run_5year_backtest.py`
- `run_dashboard_backtest.py`
- `analyze_backtest_results.py`
- `extract_backtest_data.py`
- `generate_complete_trade_log.py`

**Purpose**: These were ad-hoc scripts created during backtesting iterations. The production backtest functionality is now available via the API endpoint `/backtest/run`.

### `test_scripts/` (11 files)
Debug and test scripts used during development:
- `test_backtest_real_agents.py`
- `test_backtest_endpoint.py`
- `test_backtest_history.py`
- `test_backtest_mode.py`
- `test_momentum_debug.py`
- `quick_test_momentum_fix.py`
- `test_regime_integration.py`
- `test_phase4_tracking.py`
- `test_risk_management.py`
- `quick_test_regime.py`
- `test_regime_detection.py`

**Purpose**: These were temporary testing scripts for debugging specific features. The official test suite is in `tests/` directory.

### `shell_scripts/` (2 files)
Monitoring shell scripts:
- `monitor_backtest.sh`
- `continuous_monitor.sh`

**Purpose**: These were used to monitor long-running backtest processes. No longer needed as backtests are now managed via the API.

### `docs/` (30 files)
Markdown documentation from development sessions:
- Status reports (e.g., `ISSUE_3_STATUS_REPORT.md`)
- Fix summaries (e.g., `BACKTEST_FIX_SUMMARY.md`)
- Phase completion notes (e.g., `PHASE_4_COMPLETE.md`)
- Verification logs (e.g., `BACKTEST_VERIFICATION_SUMMARY.md`)

**Purpose**: These documented the iterative development and debugging process. Key information has been consolidated into the main README.md and CLAUDE.md files.

### `frontend_static_data/` (4 files)
Hardcoded static backtest data files:
- `staticBacktestData.ts`
- `dashboard5YearBacktest.ts`
- `complete_trade_log.json`
- `dashboard5YearBacktest.json`

**Purpose**: These contained hardcoded backtest results. The system now fetches backtest data dynamically from the API.

## Why These Files Were Archived

1. **Redundancy**: Functionality duplicated by production code
2. **Temporary Nature**: Created for specific debugging/testing sessions
3. **Documentation Bloat**: Status reports that are now outdated
4. **Static Data**: Replaced with dynamic API-based data fetching

## Production System Location

The active, production-ready system remains in:
- `/api/` - FastAPI backend
- `/agents/` - 4 specialized agents
- `/core/` - Core business logic
- `/frontend/` - React frontend application
- `/tests/` - Official test suite

## Restoration

If you need to restore any of these files, simply move them from this archive directory back to the project root:

```bash
# Example: Restore a specific backtest script
cp archive/backtest_scripts/run_5year_backtest.py ./
```

## Verification

After archiving, the following tests were run successfully:
- ✅ All Python imports working correctly
- ✅ All 4 agents initializing successfully
- ✅ System tests passing (tests/test_system.py)
- ✅ Frontend build completing (with minor linting warnings)
- ✅ API server starting correctly

## Notes

- These files are kept for historical reference
- They do not affect the production system
- Safe to delete if disk space is needed
- No active code references these archived files
