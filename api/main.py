"""
FastAPI Web Application for 4-Agent AI Hedge Fund System
Production-ready API with narrative generation and investment analysis
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, validator, Field
from typing import List, Dict, Optional
import asyncio
import json
import logging
import yfinance as yf
from datetime import datetime, timedelta
import sys
import os
import numpy as np
import math
import pandas as pd
import time
from functools import lru_cache
import concurrent.futures

# Add the root project directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Custom JSON Encoder for numpy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.DataFrame):
            return obj.to_dict('records')
        elif isinstance(obj, pd.Series):
            return obj.to_list()
        elif hasattr(obj, 'dtype'):
            try:
                if np.issubdtype(obj.dtype, np.integer):
                    return int(obj)
                elif np.issubdtype(obj.dtype, np.floating):
                    return float(obj)
                elif np.issubdtype(obj.dtype, np.bool_):
                    return bool(obj)
                else:
                    return str(obj)
            except:
                return str(obj)
        return super().default(obj)

# Import our 4-agent hedge fund components
from agents.fundamentals_agent import FundamentalsAgent
from agents.momentum_agent import MomentumAgent
from agents.quality_agent import QualityAgent
from agents.sentiment_agent import SentimentAgent
from narrative_engine.narrative_engine import InvestmentNarrativeEngine
from core.portfolio_manager import PortfolioManager
from core.stock_scorer import StockScorer
from data.enhanced_provider import EnhancedYahooProvider
from data.us_top_100_stocks import US_TOP_100_STOCKS, SECTOR_MAPPING

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# In-memory cache for analyses with TTL
analysis_cache = {}
CACHE_TTL_SECONDS = 900  # 15 minutes

# Thread pool for concurrent processing
executor = concurrent.futures.ThreadPoolExecutor(max_workers=20)

# Initialize FastAPI app
app = FastAPI(
    title="4-Agent AI Hedge Fund System",
    description="""
🏦 **AI-Powered Hedge Fund Analysis Platform** with multi-agent investment analysis and narrative generation.

## 4-Agent Analysis Framework

* **Fundamentals Agent** - Financial health, profitability, growth, and valuation analysis
* **Momentum Agent** - Technical analysis and price trend evaluation
* **Quality Agent** - Business characteristics and operational efficiency assessment
* **Sentiment Agent** - Market sentiment and analyst outlook analysis

## Investment Narrative Engine

* **Comprehensive Investment Thesis** - Human-readable analysis combining all 4 agents
* **Weighted Scoring System** - Fundamentals (40%), Momentum (30%), Quality (20%), Sentiment (10%)
* **Clear Recommendations** - STRONG BUY/BUY/WEAK BUY/HOLD/WEAK SELL/SELL ratings
* **Risk Assessment** - Detailed risk analysis and position sizing recommendations

## Features

* **Real-time Analysis** - Live stock analysis with narrative generation
* **Portfolio Management** - Multi-position portfolio optimization
* **Risk Management** - VaR calculation and correlation analysis
* **Performance Monitoring** - Comprehensive metrics and analytics
    """,
    version="4.0.0",
    contact={
        "name": "4-Agent AI Hedge Fund System",
        "url": "https://github.com/yourusername/ai-hedge-fund",
    },
    tags_metadata=[
        {
            "name": "Investment Analysis",
            "description": "4-agent investment analysis with narrative generation",
        },
        {
            "name": "Portfolio Management",
            "description": "Portfolio optimization and risk management",
        },
        {
            "name": "System",
            "description": "Health checks and system monitoring",
        },
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
fundamentals_agent = FundamentalsAgent()
momentum_agent = MomentumAgent()
quality_agent = QualityAgent()
sentiment_agent = SentimentAgent()
narrative_engine = InvestmentNarrativeEngine()
portfolio_manager = PortfolioManager()
stock_scorer = StockScorer()
data_provider = EnhancedYahooProvider()

def get_cached_analysis(symbol: str):
    """Get cached analysis if available and not expired"""
    if symbol in analysis_cache:
        cached_data, timestamp = analysis_cache[symbol]
        if time.time() - timestamp < CACHE_TTL_SECONDS:
            return cached_data
    return None

def set_cached_analysis(symbol: str, analysis_data: dict):
    """Cache analysis data with timestamp"""
    analysis_cache[symbol] = (analysis_data, time.time())

def sanitize_float(value):
    """Sanitize float values for JSON serialization"""
    if isinstance(value, (np.integer, np.int64, np.int32, np.int16, np.int8)):
        return int(value)
    if isinstance(value, (np.floating, np.float64, np.float32, np.float16)):
        val = float(value)
        if math.isinf(val) or math.isnan(val):
            return 0.0
        return val
    if isinstance(value, np.bool_):
        return bool(value)
    if hasattr(value, 'dtype'):
        try:
            if np.issubdtype(value.dtype, np.integer):
                return int(value)
            elif np.issubdtype(value.dtype, np.floating):
                val = float(value)
                if math.isinf(val) or math.isnan(val):
                    return 0.0
                return val
            elif np.issubdtype(value.dtype, np.bool_):
                return bool(value)
        except (ValueError, TypeError):
            pass
    if isinstance(value, (int, float)):
        if math.isinf(value) or math.isnan(value):
            return 0.0
        return float(value)
    return value

def sanitize_dict(data):
    """Recursively sanitize all values in a dictionary"""
    if isinstance(data, dict):
        return {k: sanitize_dict(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_dict(item) for item in data]
    elif isinstance(data, tuple):
        return tuple(sanitize_dict(item) for item in data)
    elif isinstance(data, (np.ndarray,)):
        return sanitize_dict(data.tolist())
    else:
        return sanitize_float(data)

# Pydantic models
class AnalysisRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10, description="Stock symbol (e.g., AAPL)")

    @validator('symbol')
    def validate_symbol(cls, v):
        if not v:
            raise ValueError('Symbol cannot be empty')
        v = v.strip().upper()
        if not v.replace('.', '').replace('-', '').isalpha():
            raise ValueError('Invalid symbol format')
        return v

class BatchAnalysisRequest(BaseModel):
    symbols: List[str] = Field(..., min_items=1, max_items=50, description="List of stock symbols")

    @validator('symbols')
    def validate_symbols(cls, v):
        if not v:
            raise ValueError('Symbols list cannot be empty')
        if len(v) > 50:
            raise ValueError('Maximum 50 symbols allowed per batch request')

        validated_symbols = []
        seen = set()
        for symbol in v:
            symbol = symbol.strip().upper()
            if not symbol or symbol in seen:
                continue
            if not symbol.replace('.', '').replace('-', '').isalpha():
                raise ValueError(f'Invalid symbol format: {symbol}')
            validated_symbols.append(symbol)
            seen.add(symbol)

        if not validated_symbols:
            raise ValueError('No valid symbols provided')
        return validated_symbols

class PortfolioRequest(BaseModel):
    symbols: List[str] = Field(..., min_items=2, max_items=20, description="Portfolio symbols")
    weights: Optional[List[float]] = Field(None, description="Portfolio weights (optional)")

    @validator('weights')
    def validate_weights(cls, v, values):
        if v is not None:
            if 'symbols' in values and len(v) != len(values['symbols']):
                raise ValueError('Weights length must match symbols length')
            if abs(sum(v) - 1.0) > 0.01:
                raise ValueError('Weights must sum to 1.0')
        return v

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    agents_status: Dict[str, str]

# API Routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with API documentation"""
    return """
    <html>
        <head>
            <title>4-Agent AI Hedge Fund System</title>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 40px; background: #f8f9fa; }
                .container { max-width: 1200px; margin: 0 auto; }
                .header { background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); color: white; padding: 30px; border-radius: 12px; margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
                .agent-section { background: #e8f5e8; border: 1px solid #4caf50; padding: 20px; border-radius: 8px; margin: 20px 0; }
                .endpoint-group { background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .endpoint { padding: 12px; margin: 8px 0; border-radius: 6px; border-left: 4px solid #007bff; background: #f8f9fa; }
                .method { background: #28a745; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; margin-right: 8px; font-weight: bold; }
                .method.post { background: #007bff; }
                .method.get { background: #28a745; }
                a { color: #007bff; text-decoration: none; }
                a:hover { text-decoration: underline; }
                .features { background: #fff3cd; border: 1px solid #ffc107; padding: 20px; border-radius: 8px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏦 4-Agent AI Hedge Fund System v4.0.0</h1>
                    <p>Professional-grade investment analysis with multi-agent intelligence and narrative generation</p>
                </div>

                <div class="agent-section">
                    <h3>🤖 4-Agent Analysis Framework</h3>
                    <p><strong>Fundamentals Agent (40%)</strong> - Financial health, profitability, growth, and valuation</p>
                    <p><strong>Momentum Agent (30%)</strong> - Technical analysis and price trend evaluation</p>
                    <p><strong>Quality Agent (20%)</strong> - Business characteristics and operational efficiency</p>
                    <p><strong>Sentiment Agent (10%)</strong> - Market sentiment and analyst outlook analysis</p>
                </div>

                <div class="endpoint-group">
                    <h2>📚 API Documentation</h2>
                    <div class="endpoint">
                        <a href="/docs">🔧 Interactive API Documentation (Swagger UI)</a>
                    </div>
                    <div class="endpoint">
                        <a href="/redoc">📖 Alternative Documentation (ReDoc)</a>
                    </div>
                </div>

                <div class="endpoint-group">
                    <h2>🎯 Investment Analysis Endpoints</h2>
                    <div class="endpoint">
                        <span class="method post">POST</span> <strong>/analyze</strong> - Complete 4-agent analysis with narrative<br>
                        <em>Generate comprehensive investment thesis for single stock</em>
                    </div>
                    <div class="endpoint">
                        <span class="method post">POST</span> <strong>/analyze/batch</strong> - Batch analysis for multiple stocks<br>
                        <em>Concurrent analysis with intelligent caching</em>
                    </div>
                    <div class="endpoint">
                        <span class="method get">GET</span> <strong>/analyze/{symbol}</strong> - Quick analysis for single symbol<br>
                        <em>Fast analysis with cached results</em>
                    </div>
                </div>

                <div class="endpoint-group">
                    <h2>📈 Portfolio Management</h2>
                    <div class="endpoint">
                        <span class="method post">POST</span> <strong>/portfolio/analyze</strong> - Portfolio analysis and optimization<br>
                        <em>Multi-asset portfolio risk and return analysis</em>
                    </div>
                    <div class="endpoint">
                        <span class="method get">GET</span> <strong>/portfolio/top-picks</strong> - Top investment picks<br>
                        <em>Curated stock picks based on 4-agent analysis</em>
                    </div>
                </div>

                <div class="endpoint-group">
                    <h2>🔧 System Endpoints</h2>
                    <div class="endpoint">
                        <span class="method get">GET</span> <strong>/health</strong> - System health check<br>
                        <em>Verify all agents are operational</em>
                    </div>
                </div>

                <div class="features">
                    <h2>✨ Key Features</h2>
                    <ul>
                        <li><strong>Multi-Agent Intelligence</strong> - 4 specialized agents for comprehensive analysis</li>
                        <li><strong>Investment Narratives</strong> - Human-readable investment thesis generation</li>
                        <li><strong>Weighted Scoring</strong> - Professional-grade scoring methodology</li>
                        <li><strong>Risk Management</strong> - VaR calculation and correlation analysis</li>
                        <li><strong>Portfolio Optimization</strong> - Multi-asset portfolio management</li>
                        <li><strong>Real-time Analysis</strong> - Live market data integration</li>
                        <li><strong>Intelligent Caching</strong> - 15-minute TTL for optimal performance</li>
                    </ul>
                </div>
            </div>
        </body>
    </html>
    """

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint - verify all agents are operational"""
    try:
        # Test each agent
        agents_status = {}

        # Test with AAPL data
        test_data = data_provider.get_comprehensive_data("AAPL")

        # Test Fundamentals Agent
        try:
            fund_result = fundamentals_agent.analyze("AAPL")
            agents_status["fundamentals"] = "healthy" if fund_result.get('score', 0) > 0 else "degraded"
        except Exception as e:
            agents_status["fundamentals"] = "unhealthy"

        # Test Momentum Agent
        try:
            momentum_result = momentum_agent.analyze("AAPL", test_data['historical_data'], test_data['historical_data'])
            agents_status["momentum"] = "healthy" if momentum_result.get('score', 0) >= 0 else "degraded"
        except Exception as e:
            agents_status["momentum"] = "unhealthy"

        # Test Quality Agent
        try:
            quality_result = quality_agent.analyze("AAPL", test_data)
            agents_status["quality"] = "healthy" if quality_result.get('score', 0) > 0 else "degraded"
        except Exception as e:
            agents_status["quality"] = "unhealthy"

        # Test Sentiment Agent
        try:
            sentiment_result = sentiment_agent.analyze("AAPL")
            agents_status["sentiment"] = "healthy" if sentiment_result.get('score', 0) >= 0 else "degraded"
        except Exception as e:
            agents_status["sentiment"] = "unhealthy"

        # Overall status
        healthy_agents = sum(1 for status in agents_status.values() if status == "healthy")
        overall_status = "healthy" if healthy_agents >= 3 else "degraded" if healthy_agents >= 2 else "unhealthy"

        return HealthResponse(
            status=overall_status,
            timestamp=datetime.now().isoformat(),
            version="4.0.0",
            agents_status=agents_status
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now().isoformat(),
            version="4.0.0",
            agents_status={"error": str(e)}
        )

@app.post("/analyze", tags=["Investment Analysis"])
async def analyze_stock(request: AnalysisRequest):
    """Complete 4-agent analysis with investment narrative generation"""
    try:
        symbol = request.symbol

        # Check cache first
        cached_analysis = get_cached_analysis(symbol)
        if cached_analysis:
            return cached_analysis

        logger.info(f"Starting 4-agent analysis for {symbol}")

        # Get comprehensive market data
        comprehensive_data = data_provider.get_comprehensive_data(symbol)
        if 'error' in comprehensive_data:
            raise HTTPException(status_code=404, detail=f"No data available for {symbol}")

        # Run all 4 agents
        agent_results = {}

        # Fundamentals Agent
        agent_results['fundamentals'] = fundamentals_agent.analyze(symbol)

        # Momentum Agent
        agent_results['momentum'] = momentum_agent.analyze(
            symbol,
            comprehensive_data['historical_data'],
            comprehensive_data['historical_data']  # Using same data for market comparison
        )

        # Quality Agent
        agent_results['quality'] = quality_agent.analyze(symbol, comprehensive_data)

        # Sentiment Agent
        agent_results['sentiment'] = sentiment_agent.analyze(symbol)

        # Generate comprehensive narrative
        narrative = narrative_engine.generate_comprehensive_thesis(
            symbol, agent_results, comprehensive_data
        )

        # Combine all results
        analysis_result = {
            "symbol": symbol,
            "agent_results": sanitize_dict(agent_results),
            "narrative": sanitize_dict(narrative),
            "market_data": {
                "current_price": comprehensive_data.get("current_price", 0),
                "previous_close": comprehensive_data.get("previous_close", 0),
                "price_change": comprehensive_data.get("price_change", 0),
                "price_change_percent": comprehensive_data.get("price_change_percent", 0),
                "volume": comprehensive_data.get("current_volume", 0),
                "market_cap": comprehensive_data.get("market_cap", 0),
            },
            "timestamp": datetime.now().isoformat()
        }

        # Cache the result
        set_cached_analysis(symbol, analysis_result)

        return analysis_result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyze/{symbol}", tags=["Investment Analysis"])
async def quick_analyze(symbol: str):
    """Quick analysis for single symbol with cached results"""
    request = AnalysisRequest(symbol=symbol)
    return await analyze_stock(request)

@app.post("/analyze/batch", tags=["Investment Analysis"])
async def batch_analyze(request: BatchAnalysisRequest):
    """Batch analysis for multiple stocks with concurrent processing"""
    try:
        logger.info(f"Starting batch analysis for {len(request.symbols)} symbols")

        results = []
        cached_count = 0

        # Check cache first
        symbols_needing_analysis = []
        for symbol in request.symbols:
            cached_analysis = get_cached_analysis(symbol)
            if cached_analysis:
                results.append(cached_analysis)
                cached_count += 1
            else:
                symbols_needing_analysis.append(symbol)

        logger.info(f"Using {cached_count} cached analyses, analyzing {len(symbols_needing_analysis)} new")

        # Process in batches to avoid overwhelming the system
        BATCH_SIZE = 10
        for i in range(0, len(symbols_needing_analysis), BATCH_SIZE):
            batch_symbols = symbols_needing_analysis[i:i + BATCH_SIZE]

            # Create analysis tasks
            tasks = []
            for symbol in batch_symbols:
                task = analyze_stock(AnalysisRequest(symbol=symbol))
                tasks.append(task)

            # Execute concurrently
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Batch analysis error: {result}")
                    continue
                results.append(result)

        return {
            "analyses": results,
            "total_processed": len(results),
            "total_requested": len(request.symbols),
            "cached_count": cached_count,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Batch analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/portfolio/analyze", tags=["Portfolio Management"])
async def analyze_portfolio(request: PortfolioRequest):
    """Portfolio analysis and optimization"""
    try:
        logger.info(f"Analyzing portfolio with {len(request.symbols)} positions")

        # Get individual analyses for all symbols
        batch_request = BatchAnalysisRequest(symbols=request.symbols)
        batch_result = await batch_analyze(batch_request)

        analyses = batch_result["analyses"]

        # Extract scores for portfolio optimization
        portfolio_data = []
        for analysis in analyses:
            narrative = analysis["narrative"]
            portfolio_data.append({
                "symbol": analysis["symbol"],
                "overall_score": narrative["overall_score"],
                "recommendation": narrative["recommendation"],
                "confidence_level": narrative["confidence_level"],
                "market_data": analysis["market_data"]
            })

        # Portfolio optimization using our portfolio manager
        if request.weights:
            # Use provided weights
            optimized_weights = dict(zip(request.symbols, request.weights))
        else:
            # Calculate optimal weights based on scores
            total_score = sum(item["overall_score"] for item in portfolio_data)
            if total_score > 0:
                optimized_weights = {
                    item["symbol"]: item["overall_score"] / total_score
                    for item in portfolio_data
                }
            else:
                # Equal weights if all scores are zero
                equal_weight = 1.0 / len(request.symbols)
                optimized_weights = {symbol: equal_weight for symbol in request.symbols}

        # Calculate portfolio metrics
        portfolio_score = sum(
            item["overall_score"] * optimized_weights[item["symbol"]]
            for item in portfolio_data
        )

        # Risk assessment
        high_risk_positions = [
            item for item in portfolio_data
            if item["overall_score"] < 40
        ]

        return {
            "portfolio_analysis": {
                "symbols": request.symbols,
                "weights": optimized_weights,
                "portfolio_score": round(portfolio_score, 2),
                "number_of_positions": len(request.symbols),
                "high_risk_positions": len(high_risk_positions),
                "risk_level": "High" if len(high_risk_positions) > len(request.symbols) / 2 else "Moderate" if len(high_risk_positions) > 0 else "Low"
            },
            "individual_analyses": analyses,
            "portfolio_recommendations": [
                f"Portfolio shows {'strong' if portfolio_score > 70 else 'moderate' if portfolio_score > 50 else 'weak'} investment potential",
                f"Consider rebalancing if more than {len(high_risk_positions)} positions show high risk",
                "Monitor correlation between positions for diversification"
            ],
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Portfolio analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/portfolio/top-picks", tags=["Portfolio Management"])
async def get_top_picks(limit: int = 10):
    """Get top investment picks based on 4-agent analysis"""
    try:
        logger.info(f"Generating top {limit} investment picks")

        # Analyze all Top 20 Elite Stocks
        top_symbols = US_TOP_100_STOCKS  # All 20 elite stocks for analysis
        batch_request = BatchAnalysisRequest(symbols=top_symbols)
        batch_result = await batch_analyze(batch_request)

        analyses = batch_result["analyses"]

        # Sort by overall score
        sorted_analyses = sorted(
            analyses,
            key=lambda x: x["narrative"]["overall_score"],
            reverse=True
        )

        # Get top picks
        top_picks = []
        for analysis in sorted_analyses[:limit]:
            narrative = analysis["narrative"]
            market_data = analysis["market_data"]

            # Get sector information
            sector = "Unknown"
            for sector_name, symbols in SECTOR_MAPPING.items():
                if analysis["symbol"] in symbols:
                    sector = sector_name
                    break

            pick = {
                "symbol": analysis["symbol"],
                "company_name": analysis["symbol"],  # Use symbol as name for now
                "sector": sector,
                "overall_score": narrative["overall_score"],
                "recommendation": narrative["recommendation"],
                "confidence_level": narrative["confidence_level"],
                "investment_thesis": narrative["investment_thesis"][:200] + "..." if len(narrative["investment_thesis"]) > 200 else narrative["investment_thesis"],
                "key_strengths": narrative["key_strengths"],
                "key_risks": narrative["key_risks"],
                "market_data": market_data,
                "agent_scores": narrative["agent_scores"]
            }
            top_picks.append(pick)

        return {
            "top_picks": top_picks,
            "total_analyzed": len(analyses),
            "selection_criteria": "Based on 4-agent comprehensive analysis with weighted scoring",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to generate top picks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    """Startup event"""
    logger.info("🏦 4-Agent AI Hedge Fund System starting up...")
    logger.info("✅ All 4 agents initialized")
    logger.info("✅ Narrative engine ready")
    logger.info("✅ Portfolio manager ready")
    logger.info("✅ API endpoints configured")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    logger.info("🛑 4-Agent AI Hedge Fund System shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)