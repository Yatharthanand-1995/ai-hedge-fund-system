# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a professional-grade AI-powered hedge fund analysis system that employs **4 specialized agents** to provide comprehensive investment analysis with human-readable narratives. The system combines quantitative analysis with qualitative reasoning to generate professional investment theses.

### 4-Agent Architecture

The system's core intelligence is distributed across 4 specialized agents with weighted scoring:

1. **Fundamentals Agent (40% weight)** - `agents/fundamentals_agent.py`
   - Analyzes financial health, profitability, growth, and valuation
   - Evaluates ROE, P/E ratios, revenue growth, debt-to-equity
   - Uses yfinance to fetch financial statements and balance sheets

2. **Momentum Agent (30% weight)** - `agents/momentum_agent.py`
   - Technical analysis and price trend evaluation
   - RSI, moving averages, price momentum calculations
   - Uses TA-Lib for technical indicators

3. **Quality Agent (20% weight)** - `agents/quality_agent.py`
   - Business quality and operational efficiency assessment
   - Analyzes business model characteristics and operational metrics

4. **Sentiment Agent (10% weight)** - `agents/sentiment_agent.py`
   - Market sentiment and analyst outlook analysis
   - Optional LLM integration for enhanced sentiment analysis

**Critical Design Principle**: The weighted scoring system (40/30/20/10) must be maintained across all components. These weights are hardcoded in multiple locations: `api/main.py`, `core/stock_scorer.py`, and `narrative_engine/narrative_engine.py`.

## Key Commands

### Running the System

```bash
# Start both API and frontend servers
./start_system.sh

# Or manually:
# Backend API server
python -m api.main

# Frontend (in separate terminal)
cd frontend && npm run dev
```

### Testing

```bash
# Test all 4 agents and narrative generation
python test_system.py

# Test system accuracy and fixes
python test_system_accuracy.py
python test_system_fixes.py

# Final comprehensive system test
python final_system_test.py
```

### Development

```bash
# Code formatting
black .

# Import organization
isort .

# Linting
flake8 .

# Frontend build
cd frontend && npm run build

# Frontend linting
cd frontend && npm run lint
```

## Architecture & Data Flow

### Analysis Pipeline

1. **Data Collection** (`data/enhanced_provider.py`)
   - `EnhancedYahooProvider` fetches comprehensive market data
   - Implements 15-minute caching (`CACHE_TTL_SECONDS = 900`)
   - Calculates technical indicators using TA-Lib
   - Handles numpy array serialization issues with `sanitize_float()` and `sanitize_dict()`

2. **Agent Orchestration** (`core/stock_scorer.py`)
   - `StockScorer` coordinates all 4 agents
   - Combines weighted scores into composite score
   - Returns confidence-weighted recommendations

3. **Narrative Generation** (`narrative_engine/narrative_engine.py`)
   - `InvestmentNarrativeEngine` converts quantitative scores to human-readable thesis
   - Optional LLM integration (OpenAI/Anthropic) for sophisticated reasoning
   - Generates key strengths, risks, and recommendations

4. **API Layer** (`api/main.py`)
   - FastAPI application with comprehensive endpoints
   - Concurrent batch processing (max 10 symbols per batch)
   - In-memory caching with TTL
   - Custom `NumpyEncoder` for JSON serialization

### Data Flow Patterns

- All agents accept optional `cached_data` parameter to avoid redundant API calls
- The `EnhancedYahooProvider` maintains its own cache with 15-minute TTL
- The API layer has a separate `analysis_cache` for full analysis results
- Agents return standardized dictionaries: `{'score': 0-100, 'confidence': 0-1, 'metrics': {...}, 'reasoning': str}`

## API Endpoints

The system exposes a FastAPI server on port 8010:

- **POST /analyze** - Complete 4-agent analysis with narrative for single stock
- **GET /analyze/{symbol}** - Quick analysis with cached results
- **POST /analyze/batch** - Batch analysis (max 50 symbols, processed in batches of 10)
- **POST /portfolio/analyze** - Portfolio optimization and risk analysis
- **GET /portfolio/top-picks** - Top investment picks from US_TOP_100_STOCKS
- **GET /health** - System health check (tests all 4 agents)
- **GET /docs** - Swagger UI documentation
- **GET /redoc** - ReDoc alternative documentation

## Frontend Architecture

The frontend is a React + TypeScript + Vite application:

- **Stack**: React 19, TypeScript, Vite, TanStack Query, Tailwind CSS
- **State Management**: Zustand (`src/stores/`)
- **API Client**: Axios with React Query (`src/services/`, `src/hooks/`)
- **UI Components**: Radix UI + custom components (`src/components/`)
- **Routing**: React Router (`src/pages/`)
- **Dev Server**: Vite on port 5174 (or 5173)

## Critical Implementation Details

### Numpy Serialization

The system extensively uses numpy and pandas, which require special JSON serialization handling:

- Use `sanitize_float()` and `sanitize_dict()` in `api/main.py` before returning JSON
- Custom `NumpyEncoder` class handles all numpy types (int64, float64, ndarray, etc.)
- Check for `inf` and `nan` values and convert to `0.0`

### Confidence Scoring

Agent confidence is crucial for overall system reliability:

- Each agent returns a `confidence` score (0-1) based on data availability
- Optional data validator in `utils/data_validator.py` enhances confidence scoring
- Composite confidence is weighted average across all agents
- Confidence affects recommendation strength (HIGH/MEDIUM/LOW)

### Recommendation Mapping

Scores map to recommendations in `narrative_engine/narrative_engine.py`:

- 80-100: STRONG BUY
- 65-79: BUY
- 55-64: WEAK BUY
- 45-54: HOLD
- 35-44: WEAK SELL
- 0-34: SELL

### Stock Universe

The system operates on a curated universe defined in `data/us_top_100_stocks.py`:

- `US_TOP_100_STOCKS`: List of 20 elite stocks (not actually 100)
- `SECTOR_MAPPING`: Dictionary mapping stocks to sectors
- Used by `/portfolio/top-picks` endpoint

## Environment Configuration

Optional environment variables for enhanced features:

```bash
OPENAI_API_KEY=your_key        # For GPT-based sentiment analysis
ANTHROPIC_API_KEY=your_key     # For Claude-based sentiment analysis
NEWS_API_KEY=your_key           # For news sentiment analysis
```

LLM integration is optional and gracefully degrades if keys are not provided.

## Common Development Tasks

### Adding a New Agent

1. Create agent class in `agents/` inheriting common patterns
2. Implement `analyze()` method returning `{'score': float, 'confidence': float, 'metrics': dict, 'reasoning': str}`
3. Add agent to `StockScorer` in `core/stock_scorer.py`
4. Update agent weights (ensure they sum to 1.0)
5. Update `InvestmentNarrativeEngine` to incorporate new agent's narrative
6. Update API documentation and tests

### Modifying Agent Weights

Agent weights are defined in multiple locations and must be updated consistently:

1. `core/stock_scorer.py` - Default weights dictionary
2. `narrative_engine/narrative_engine.py` - Weighted score calculation
3. `api/main.py` - Documentation strings
4. Update README.md documentation

### Adding New Technical Indicators

1. Add calculation in `data/enhanced_provider.py` → `_calculate_all_indicators()`
2. Use TA-Lib functions for standard indicators
3. Update the returned technical_data dictionary
4. Agents can then access via `cached_data['technical_data']`

## Troubleshooting

### Port Already in Use

The startup script kills existing processes on ports 8010 and 5174. If issues persist:

```bash
lsof -ti :8010 | xargs kill -9
lsof -ti :5174 | xargs kill -9
```

### Agent Failures

Check `/health` endpoint to diagnose which agent is failing. Healthy system requires at least 3/4 agents operational.

### Cache Issues

To clear analysis cache, restart the API server. The in-memory cache is not persisted.

### Missing Dependencies

Ensure all dependencies are installed:

```bash
pip install -r requirements.txt
cd frontend && npm install
```

Note: `talib-binary` is required for technical indicators. If installation fails, install TA-Lib system library first.