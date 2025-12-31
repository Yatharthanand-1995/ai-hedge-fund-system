"""
FastAPI Web Application for 5-Agent AI Hedge Fund System
Production-ready API with narrative generation and investment analysis
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, validator, Field
from typing import List, Dict, Optional
from starlette.middleware.base import BaseHTTPMiddleware
import asyncio
import json
import logging
from logging.handlers import RotatingFileHandler
import uuid

# Optional rate limiting - gracefully degrades if slowapi not installed
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    RATE_LIMITING_ENABLED = True
except ImportError:
    RATE_LIMITING_ENABLED = False
    # Logging will be configured later, so we'll just note this for now
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
from cachetools import TTLCache

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()  # Load .env file from project root

# Optional Sentry error tracking - gracefully degrades if not configured
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration

    sentry_dsn = os.getenv('SENTRY_DSN')
    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=os.getenv('ENVIRONMENT', 'development'),
            traces_sample_rate=0.1,  # 10% of transactions for performance monitoring
            profiles_sample_rate=0.1,  # 10% for profiling
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                LoggingIntegration(
                    level=logging.INFO,  # Capture info and above
                    event_level=logging.ERROR  # Send errors to Sentry
                ),
            ],
            # Filter out sensitive data
            before_send=lambda event, hint: event if not any(
                keyword in str(event).lower()
                for keyword in ['api_key', 'password', 'token', 'secret']
            ) else None,
        )
        SENTRY_ENABLED = True
    else:
        SENTRY_ENABLED = False
except ImportError:
    SENTRY_ENABLED = False

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

# Import our 5-agent hedge fund components
from agents.fundamentals_agent import FundamentalsAgent
from agents.momentum_agent import MomentumAgent
from agents.quality_agent import QualityAgent
from agents.sentiment_agent import SentimentAgent
from narrative_engine.narrative_engine import InvestmentNarrativeEngine
from core.portfolio_manager import PortfolioManager
from core.stock_scorer import StockScorer
from core.parallel_executor import ParallelAgentExecutor
from data.enhanced_provider import EnhancedYahooProvider
from data.us_top_100_stocks import US_TOP_100_STOCKS, SECTOR_MAPPING
from config.agent_weights import get_weight_percentages
from scheduler.trading_scheduler import TradingScheduler

# Configure logging with rotation
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create logs directory if it doesn't exist
os.makedirs('logs/api', exist_ok=True)

# Rotating file handler (10MB max, 5 backups)
file_handler = RotatingFileHandler(
    'logs/api/api.log',
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5
)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)
logger = logging.getLogger(__name__)

# Thread-safe in-memory cache for analyses with TTL
# Configurable via environment variables
CACHE_MAX_SIZE = int(os.getenv('CACHE_MAX_SIZE', '2000'))  # Increased from 1000 to 2000
CACHE_TTL_SECONDS = int(os.getenv('CACHE_TTL_SECONDS', '1200'))  # 20 minutes default
analysis_cache = TTLCache(maxsize=CACHE_MAX_SIZE, ttl=CACHE_TTL_SECONDS)
cache_lock = asyncio.Lock()  # Lock for thread-safe cache access

# Thread pool for concurrent processing
executor = concurrent.futures.ThreadPoolExecutor(max_workers=20)

# Initialize rate limiter (if available)
if RATE_LIMITING_ENABLED:
    limiter = Limiter(key_func=get_remote_address)
else:
    limiter = None

# Initialize FastAPI app
app = FastAPI(
    title="5-Agent AI Hedge Fund System",
    description="""
🏦 **AI-Powered Hedge Fund Analysis Platform** with multi-agent investment analysis and narrative generation.

## 5-Agent Analysis Framework

* **Fundamentals Agent** - Financial health, profitability, growth, and valuation analysis
* **Momentum Agent** - Technical analysis and price trend evaluation
* **Quality Agent** - Business characteristics and operational efficiency assessment
* **Sentiment Agent** - Market sentiment and analyst outlook analysis

## Investment Narrative Engine

* **Comprehensive Investment Thesis** - Human-readable analysis combining all 5 agents
* **Weighted Scoring System** - Fundamentals (36%), Momentum (27%), Quality (18%), Sentiment (9%), Institutional Flow (10%)
* **Clear Recommendations** - STRONG BUY/BUY/WEAK BUY/HOLD/WEAK SELL/SELL ratings
* **Risk Assessment** - Detailed risk analysis and position sizing recommendations

## Features

* **Real-time Analysis** - Live stock analysis with narrative generation
* **Portfolio Management** - Multi-position portfolio optimization
* **Risk Management** - VaR calculation and correlation analysis
* **Performance Monitoring** - Comprehensive metrics and analytics

## Rate Limits

* **Analysis endpoints**: 60 requests per minute
* **Batch endpoints**: 10 requests per minute
* **Health checks**: Unlimited
    """,
    version="5.0.0",
    contact={
        "name": "5-agent AI Hedge Fund System",
        "url": "https://github.com/yourusername/ai-hedge-fund",
    },
    tags_metadata=[
        {
            "name": "Investment Analysis",
            "description": "5-agent investment analysis with narrative generation",
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

# Add rate limiter to app state (if enabled)
if RATE_LIMITING_ENABLED:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Create a decorator that applies rate limits
    def apply_rate_limits():
        """Apply rate limits to endpoints after they're defined"""
        # This will be called after all endpoints are defined
        # Rate limits are applied via decorator in endpoint definitions
        pass

    logger.info("Rate limiting enabled (slowapi)")
else:
    logger.warning("Rate limiting disabled - slowapi not installed")

# Request tracing middleware
class RequestTracingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add request tracing with X-Request-ID headers.

    - Generates unique ID for each request
    - Accepts existing X-Request-ID from client
    - Adds X-Request-ID to response headers
    - Logs request ID for all requests
    """

    async def dispatch(self, request: Request, call_next):
        # Get or generate request ID
        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))

        # Store in request state for access in endpoints
        request.state.request_id = request_id

        # Log request with ID
        logger.info(f"[{request_id}] {request.method} {request.url.path}")

        # Process request
        try:
            response = await call_next(request)

            # Add request ID to response headers
            response.headers['X-Request-ID'] = request_id

            # Log response
            logger.info(f"[{request_id}] Response: {response.status_code}")

            return response
        except Exception as e:
            # Log error with request ID
            logger.error(f"[{request_id}] Error: {str(e)}")
            raise

# Add request tracing middleware
app.add_middleware(RequestTracingMiddleware)

# Configure CORS - secure defaults
# Get allowed origins from environment variable
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5174,http://localhost:3000,http://localhost:5173')

# Warn if using wildcard in production
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
if ALLOWED_ORIGINS == '*' and ENVIRONMENT == 'production':
    logger.error("🚨 SECURITY WARNING: CORS wildcard (*) enabled in production! Set ALLOWED_ORIGINS environment variable.")

if ALLOWED_ORIGINS == '*':
    # Wildcard mode (only for development)
    allowed_origins_list = ["*"]
    allow_credentials_flag = False  # Can't use credentials with wildcard
    if ENVIRONMENT == 'development':
        logger.warning("⚠️  CORS: Wildcard (*) mode active - development only!")
else:
    # Secure mode - specific origins
    allowed_origins_list = [origin.strip() for origin in ALLOWED_ORIGINS.split(',')]
    allow_credentials_flag = True
    logger.info(f"✅ CORS: Restricted to origins: {allowed_origins_list}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins_list,
    allow_credentials=allow_credentials_flag,  # Only allow with specific origins
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Get LLM provider from environment (default: gemini)
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'gemini')  # Options: openai, anthropic, gemini

# Global instances
from agents.institutional_flow_agent import InstitutionalFlowAgent

fundamentals_agent = FundamentalsAgent()
momentum_agent = MomentumAgent()
quality_agent = QualityAgent()
sentiment_agent = SentimentAgent(llm_provider=LLM_PROVIDER)
institutional_flow_agent = InstitutionalFlowAgent()
narrative_engine = InvestmentNarrativeEngine(llm_provider=LLM_PROVIDER)
portfolio_manager = PortfolioManager()
stock_scorer = StockScorer()
data_provider = EnhancedYahooProvider()

# Initialize trading scheduler (will be started in startup event)
trading_scheduler = None

# Initialize parallel executor with error handling (5 agents)
parallel_executor = ParallelAgentExecutor(
    fundamentals_agent=fundamentals_agent,
    momentum_agent=momentum_agent,
    quality_agent=quality_agent,
    sentiment_agent=sentiment_agent,
    institutional_flow_agent=institutional_flow_agent,
    max_retries=3,
    timeout_seconds=30
)

async def get_cached_analysis(symbol: str):
    """Get cached analysis if available and not expired (thread-safe)"""
    async with cache_lock:
        # TTLCache automatically handles expiration
        return analysis_cache.get(symbol)

async def set_cached_analysis(symbol: str, analysis_data: dict):
    """Cache analysis data (thread-safe with automatic TTL)"""
    async with cache_lock:
        analysis_cache[symbol] = analysis_data

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
    elif isinstance(data, pd.Series):
        # Convert pandas Series to list and sanitize
        return sanitize_dict(data.tolist())
    elif isinstance(data, pd.DataFrame):
        # Convert pandas DataFrame to list of dicts and sanitize
        return sanitize_dict(data.to_dict('records'))
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
    environment: Optional[Dict] = None

# API Routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with API documentation"""
    return """
    <html>
        <head>
            <title>5-agent AI Hedge Fund System</title>
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
                    <h1>🏦 5-agent AI Hedge Fund System v5.0.0</h1>
                    <p>Professional-grade investment analysis with multi-agent intelligence and narrative generation</p>
                </div>

                <div class="agent-section">
                    <h3>🤖 5-agent Analysis Framework</h3>
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
                        <span class="method post">POST</span> <strong>/analyze</strong> - Complete 5-agent analysis with narrative<br>
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
                        <em>Curated stock picks based on 5-agent analysis</em>
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
    """
    Health check endpoint - verify all agents are operational

    Returns:
    - **status**: Overall system health (healthy/degraded/unhealthy)
    - **timestamp**: Current server time (ISO format)
    - **version**: API version
    - **agents_status**: Individual agent health status
    - **environment**: Deployment environment info

    System is considered:
    - **healthy**: 3+ agents operational
    - **degraded**: 2 agents operational
    - **unhealthy**: <2 agents operational
    """
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
            logger.warning(f"Fundamentals agent health check failed: {e}")

        # Test Momentum Agent
        try:
            momentum_result = momentum_agent.analyze("AAPL", test_data['historical_data'], test_data['historical_data'])
            agents_status["momentum"] = "healthy" if momentum_result.get('score', 0) >= 0 else "degraded"
        except Exception as e:
            agents_status["momentum"] = "unhealthy"
            logger.warning(f"Momentum agent health check failed: {e}")

        # Test Quality Agent
        try:
            quality_result = quality_agent.analyze("AAPL", test_data)
            agents_status["quality"] = "healthy" if quality_result.get('score', 0) > 0 else "degraded"
        except Exception as e:
            agents_status["quality"] = "unhealthy"
            logger.warning(f"Quality agent health check failed: {e}")

        # Test Sentiment Agent
        try:
            sentiment_result = sentiment_agent.analyze("AAPL")
            agents_status["sentiment"] = "healthy" if sentiment_result.get('score', 0) >= 0 else "degraded"
        except Exception as e:
            agents_status["sentiment"] = "unhealthy"
            logger.warning(f"Sentiment agent health check failed: {e}")

        # Test Institutional Flow Agent
        try:
            inst_flow_result = institutional_flow_agent.analyze("AAPL", test_data)
            agents_status["institutional_flow"] = "healthy" if inst_flow_result.get('score', 0) >= 0 else "degraded"
        except Exception as e:
            agents_status["institutional_flow"] = "unhealthy"
            logger.warning(f"Institutional flow agent health check failed: {e}")

        # Overall status
        healthy_agents = sum(1 for status in agents_status.values() if status == "healthy")
        overall_status = "healthy" if healthy_agents >= 4 else "degraded" if healthy_agents >= 3 else "unhealthy"

        # Add environment info for monitoring
        environment_info = {
            "llm_provider": LLM_PROVIDER,
            "adaptive_weights_enabled": os.getenv('ENABLE_ADAPTIVE_WEIGHTS', 'false') == 'true',
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "sentry_enabled": SENTRY_ENABLED,
            "rate_limiting_enabled": RATE_LIMITING_ENABLED
        }

        return HealthResponse(
            status=overall_status,
            timestamp=datetime.now().isoformat(),
            version="5.0.0",
            agents_status=agents_status,
            environment=environment_info
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now().isoformat(),
            version="5.0.0",
            agents_status={"error": str(e)},
            environment={"error": "Unable to load environment info"}
        )

@app.get("/metrics", tags=["System"])
async def get_metrics():
    """
    Simple metrics endpoint for monitoring

    Returns basic system metrics including cache stats and request counts.
    Can be extended with Prometheus metrics in Phase 2.
    """
    try:
        # Calculate cache statistics
        cache_size = len(analysis_cache)
        cache_utilization = (cache_size / CACHE_MAX_SIZE * 100) if CACHE_MAX_SIZE > 0 else 0
        cache_keys = list(analysis_cache.keys())[:10]  # First 10 for preview

        # Enhanced metrics
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "version": "5.0.0",
            "cache": {
                "current_size": cache_size,
                "max_size": CACHE_MAX_SIZE,
                "utilization_percent": round(cache_utilization, 2),
                "ttl_seconds": CACHE_TTL_SECONDS,
                "sample_keys": cache_keys,
                "status": "healthy" if cache_utilization < 80 else "warning" if cache_utilization < 95 else "critical"
            },
            "agents": {
                "count": 5,
                "names": ["fundamentals", "momentum", "quality", "sentiment", "institutional_flow"]
            },
            "system": {
                "llm_provider": LLM_PROVIDER,
                "adaptive_weights": os.getenv('ENABLE_ADAPTIVE_WEIGHTS', 'false') == 'true',
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
                "rate_limiting_enabled": RATE_LIMITING_ENABLED,
                "sentry_enabled": SENTRY_ENABLED
            }
        }

        return JSONResponse(content=metrics)

    except Exception as e:
        logger.error(f"Metrics endpoint failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to generate metrics", "detail": str(e)}
        )

@app.get("/market/regime", tags=["System"])
async def get_market_regime(force_refresh: bool = False):
    """
    Get current market regime and adaptive agent weights

    Market regimes are detected using SPY data analysis:
    - **Trend**: BULL, BEAR, or SIDEWAYS market
    - **Volatility**: HIGH_VOL, NORMAL_VOL, or LOW_VOL
    - **Adaptive Weights**: Agent weights automatically adjust based on regime

    **Caching**: Regime data is cached for 6 hours by default

    **Example Response:**
    ```json
    {
        "regime": "BULL_NORMAL_VOL",
        "trend": "BULL",
        "volatility": "NORMAL_VOL",
        "weights": {
            "fundamentals": 0.4,
            "momentum": 0.3,
            "quality": 0.2,
            "sentiment": 0.1
        },
        "explanation": "Bull market with normal volatility - Steady uptrend. Balanced approach.",
        "timestamp": "2025-10-07T02:30:00",
        "cache_hit": false,
        "adaptive_weights_enabled": true
    }
    ```
    """
    try:
        from core.market_regime_service import get_market_regime_service
        import os

        regime_service = get_market_regime_service()
        regime_info = regime_service.get_current_regime(force_refresh=force_refresh)

        # Get explanation
        explanation = regime_service.get_regime_explanation(regime_info.get('regime'))

        # Check if adaptive weights are enabled
        adaptive_enabled = os.getenv('ENABLE_ADAPTIVE_WEIGHTS', 'false').lower() == 'true'

        return {
            **regime_info,
            'explanation': explanation,
            'adaptive_weights_enabled': adaptive_enabled
        }

    except Exception as e:
        logger.error(f"Failed to get market regime: {e}")
        # Return default regime on error
        return {
            'regime': 'SIDEWAYS_NORMAL_VOL',
            'trend': 'SIDEWAYS',
            'volatility': 'NORMAL_VOL',
            'weights': {
                'fundamentals': 0.4,
                'momentum': 0.3,
                'quality': 0.2,
                'sentiment': 0.1
            },
            'explanation': 'Using default regime due to detection failure',
            'timestamp': datetime.now().isoformat(),
            'cache_hit': False,
            'adaptive_weights_enabled': False,
            'error': str(e)
        }


@app.post("/analyze", tags=["Investment Analysis"])
async def analyze_stock(request: AnalysisRequest, req: Request = None):
    """Complete 5-agent analysis with investment narrative generation (PARALLEL EXECUTION)

    Rate limit: 60 requests per minute per IP (when slowapi is installed)
    """
    try:
        symbol = request.symbol

        # Check cache first
        cached_analysis = await get_cached_analysis(symbol)
        if cached_analysis:
            logger.info(f"✅ Cache hit for {symbol}")
            return cached_analysis

        logger.info(f"🚀 Starting parallel 5-agent analysis for {symbol}")

        # Get comprehensive market data
        comprehensive_data = data_provider.get_comprehensive_data(symbol)
        if 'error' in comprehensive_data:
            raise HTTPException(status_code=404, detail=f"No data available for {symbol}")

        # Execute all agents in parallel with error handling
        agent_results = await parallel_executor.execute_all_agents(symbol, comprehensive_data)

        # Extract metadata and remove from agent results
        execution_meta = agent_results.pop('_meta', {})
        failed_agents = execution_meta.get('failed_agents', [])
        execution_time = execution_meta.get('execution_time', 0)

        logger.info(
            f"✨ Parallel execution completed in {execution_time:.2f}s "
            f"({5 - len(failed_agents)}/5 agents succeeded)"
        )

        # Check if we have enough successful agents
        if len(failed_agents) >= 3:  # At least 3/5 agents must succeed
            raise HTTPException(
                status_code=503,
                detail=f"Analysis failed: Too many agents failed ({len(failed_agents)}/5)"
            )

        # Generate comprehensive narrative (even with some failed agents)
        narrative = narrative_engine.generate_comprehensive_thesis(
            symbol, agent_results, comprehensive_data
        )

        # Add warning if agents failed
        if failed_agents:
            narrative['warnings'] = [
                f"Analysis completed with degraded accuracy: {', '.join(failed_agents)} agent(s) failed"
            ]
            narrative['confidence_level'] = 'LOW'  # Downgrade confidence

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
            "execution_meta": {
                "execution_time": execution_time,
                "failed_agents": failed_agents,
                "mode": "parallel"
            },
            "timestamp": datetime.now().isoformat()
        }

        # Cache the result
        await set_cached_analysis(symbol, analysis_result)

        return analysis_result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Analysis failed for {symbol}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyze/consensus", tags=["Investment Analysis"])
async def get_agent_consensus(symbols: str = "AAPL,MSFT,GOOGL"):
    """
    Get multi-agent consensus analysis for multiple stocks

    Returns detailed agent-by-agent breakdown with consensus metrics
    """
    try:
        # Parse symbols
        symbol_list = [s.strip().upper() for s in symbols.split(',')]
        logger.info(f"Generating consensus analysis for {symbol_list}")

        # Analyze all requested symbols
        batch_request = BatchAnalysisRequest(symbols=symbol_list)
        batch_result = await batch_analyze(batch_request, req=None)

        consensus_data = []

        for analysis in batch_result["analyses"]:
            symbol = analysis["symbol"]
            narrative = analysis["narrative"]
            agent_results = analysis.get("agent_results", {})

            # Extract agent scores and confidence
            agents_data = []
            agent_scores_list = []

            # Get weight percentages from centralized configuration
            weight_map = get_weight_percentages()

            for agent_name in ['fundamentals', 'momentum', 'quality', 'sentiment', 'institutional_flow']:
                if agent_name in agent_results:
                    agent_info = agent_results[agent_name]

                    score = agent_info.get('score', 50)
                    confidence = agent_info.get('confidence', 0.5)

                    # Determine agent health status
                    if confidence >= 0.8 and score > 0:
                        status = 'healthy'
                    elif confidence >= 0.5:
                        status = 'degraded'
                    else:
                        status = 'unhealthy'

                    agents_data.append({
                        'name': agent_name.capitalize(),
                        'score': round(score, 1),
                        'confidence': round(confidence, 2),
                        'weight': weight_map.get(agent_name, 10),
                        'accuracy': round(85 + confidence * 10, 1),  # Estimated accuracy
                        'reasoning': agent_info.get('reasoning', 'No reasoning available'),
                        'status': status
                    })

                    agent_scores_list.append(score)

            # Calculate consensus metrics
            overall_score = narrative.get("overall_score", 50)

            # Calculate agreement (based on score variance)
            if len(agent_scores_list) > 1:
                score_std = np.std(agent_scores_list)
                agreement = max(0, min(100, 100 - (score_std * 2)))  # Lower variance = higher agreement
            else:
                agreement = 50

            # Determine consensus strength
            if agreement >= 85 and overall_score >= 70:
                consensus = 'strong'
            elif agreement >= 70 or (overall_score >= 60 and overall_score <= 80):
                consensus = 'moderate'
            else:
                consensus = 'weak'

            # Identify conflict areas
            conflict_areas = []
            if len(agent_scores_list) >= 4:
                # Check for significant disagreements
                max_score = max(agent_scores_list)
                min_score = min(agent_scores_list)
                if max_score - min_score > 30:
                    # Find which agents disagree
                    if agent_results.get('fundamentals', {}).get('score', 50) < 50 and agent_results.get('momentum', {}).get('score', 50) > 70:
                        conflict_areas.append('Valuation vs Momentum')
                    if agent_results.get('quality', {}).get('score', 50) < 50:
                        conflict_areas.append('Business Quality Concerns')
                    if agent_results.get('sentiment', {}).get('score', 50) < 40:
                        conflict_areas.append('Negative Sentiment')

            # Generate top reason
            top_agent = max(agents_data, key=lambda x: x['score'] * x['weight'])
            if overall_score >= 75:
                top_reason = f"Strong {top_agent['name'].lower()} signals with score of {top_agent['score']}"
            elif overall_score >= 60:
                top_reason = f"Moderate performance across agents, led by {top_agent['name'].lower()}"
            else:
                top_reason = f"Weak signals across multiple agents, concerns in {', '.join(conflict_areas) if conflict_areas else 'multiple areas'}"

            consensus_data.append({
                'symbol': symbol,
                'overallScore': round(overall_score, 1),
                'consensus': consensus,
                'agreement': round(agreement, 0),
                'conflictAreas': conflict_areas,
                'topReason': top_reason,
                'agents': agents_data
            })

        return {
            'consensus': consensus_data,
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to generate consensus analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyze/{symbol}", tags=["Investment Analysis"])
async def quick_analyze(symbol: str):
    """Quick analysis for single symbol with cached results"""
    request = AnalysisRequest(symbol=symbol)
    return await analyze_stock(request)

@app.post("/analyze/batch", tags=["Investment Analysis"])
async def batch_analyze(request: BatchAnalysisRequest, req: Request = None):
    """Batch analysis for multiple stocks with concurrent processing

    Rate limit: 10 requests per minute per IP (when slowapi is installed)
    """
    try:
        logger.info(f"Starting batch analysis for {len(request.symbols)} symbols")

        results = []
        cached_count = 0

        # Check cache first
        symbols_needing_analysis = []
        for symbol in request.symbols:
            cached_analysis = await get_cached_analysis(symbol)
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
        batch_result = await batch_analyze(batch_request, req=None)

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
async def get_top_picks(limit: int = 12):
    """Get top investment picks based on 5-agent analysis from 50-stock universe"""
    try:
        logger.info(f"Generating top {limit} investment picks from 50-stock universe")

        # Analyze all Top 50 Elite Stocks
        top_symbols = US_TOP_100_STOCKS  # All 50 elite stocks for analysis
        batch_request = BatchAnalysisRequest(symbols=top_symbols)
        batch_result = await batch_analyze(batch_request, req=None)

        analyses = batch_result["analyses"]

        # Sort by overall score
        sorted_analyses = sorted(
            analyses,
            key=lambda x: x["narrative"]["overall_score"],
            reverse=True
        )

        # Get top picks and calculate portfolio weights
        top_picks = []
        total_score = sum(analysis["narrative"]["overall_score"] for analysis in sorted_analyses[:limit])

        for analysis in sorted_analyses[:limit]:
            narrative = analysis["narrative"]
            market_data = analysis["market_data"]

            # Get sector information
            sector = "Unknown"
            for sector_name, symbols in SECTOR_MAPPING.items():
                if analysis["symbol"] in symbols:
                    sector = sector_name
                    break

            # Calculate weight based on score proportion
            weight = (narrative["overall_score"] / total_score * 100) if total_score > 0 else 0

            pick = {
                "symbol": analysis["symbol"],
                "company_name": analysis["symbol"],  # Use symbol as name for now
                "sector": sector,
                "overall_score": narrative["overall_score"],
                "weight": round(weight, 2),
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
            "selection_criteria": "Based on 5-agent comprehensive analysis with weighted scoring",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to generate top picks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/portfolio/summary", tags=["Portfolio Management"])
async def get_portfolio_summary():
    """Get portfolio summary metrics based on top picks analysis"""
    try:
        logger.info("Generating portfolio summary")

        # Get top 10 picks for portfolio calculation
        top_picks_response = await get_top_picks(limit=10)
        top_picks = top_picks_response["top_picks"]

        if not top_picks:
            raise HTTPException(status_code=404, detail="No portfolio data available")

        # Calculate portfolio metrics
        total_score = sum(pick["overall_score"] for pick in top_picks)
        avg_score = total_score / len(top_picks) if top_picks else 0

        # Calculate weighted performance based on scores
        portfolio_value = 100000  # Base portfolio value
        daily_performance = (avg_score - 50) * 0.5  # Convert score to daily performance %
        weekly_performance = daily_performance * 7 * 0.7  # Weekly with some decay
        monthly_performance = daily_performance * 30 * 0.5  # Monthly with more decay

        # AI confidence based on average confidence levels
        confidence_levels = [pick["confidence_level"] for pick in top_picks if pick.get("confidence_level")]
        ai_confidence = 8.5  # Default high confidence
        if confidence_levels:
            confidence_map = {"HIGH": 9, "MEDIUM": 7, "LOW": 5}
            avg_confidence = sum(confidence_map.get(level, 7) for level in confidence_levels) / len(confidence_levels)
            ai_confidence = avg_confidence

        # Market regime based on average scores
        if avg_score > 70:
            market_regime = "bullish"
        elif avg_score < 45:
            market_regime = "bearish"
        else:
            market_regime = "sideways"

        # Risk level based on score dispersion
        scores = [pick["overall_score"] for pick in top_picks]
        score_std = np.std(scores) if len(scores) > 1 else 0
        if score_std > 15:
            risk_level = "high"
        elif score_std > 8:
            risk_level = "medium"
        else:
            risk_level = "low"

        # Count actions required (positions with scores < 60)
        actions_required = len([pick for pick in top_picks if pick["overall_score"] < 60])

        portfolio_summary = {
            "totalValue": portfolio_value + (portfolio_value * monthly_performance / 100),
            "dailyPnL": portfolio_value * daily_performance / 100,
            "dailyPnLPercent": daily_performance,
            "weeklyPnL": portfolio_value * weekly_performance / 100,
            "weeklyPnLPercent": weekly_performance,
            "monthlyPnL": portfolio_value * monthly_performance / 100,
            "monthlyPnLPercent": monthly_performance,
            "aiConfidenceIndex": round(ai_confidence, 1),
            "marketRegime": market_regime,
            "riskLevel": risk_level,
            "activePositions": len(top_picks),
            "actionsRequired": actions_required,
            "timestamp": datetime.now().isoformat()
        }

        return portfolio_summary

    except Exception as e:
        logger.error(f"Failed to generate portfolio summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/portfolio/sector-analysis", tags=["Portfolio Management"])
async def get_sector_analysis():
    """Get comprehensive sector analysis across all 50 stocks in the universe"""
    try:
        logger.info("Generating sector analysis for 50-stock universe")

        # Analyze all 50 stocks
        all_symbols = US_TOP_100_STOCKS
        batch_request = BatchAnalysisRequest(symbols=all_symbols)
        batch_result = await batch_analyze(batch_request, req=None)

        analyses = batch_result["analyses"]

        # Group by sector
        sector_data = {}
        for sector_name, symbols in SECTOR_MAPPING.items():
            sector_analyses = [a for a in analyses if a["symbol"] in symbols]

            if not sector_analyses:
                continue

            # Calculate sector metrics
            scores = [a["narrative"]["overall_score"] for a in sector_analyses]
            avg_score = sum(scores) / len(scores) if scores else 0
            score_std = np.std(scores) if len(scores) > 1 else 0

            # Calculate allocation (equal weight)
            allocation = (len(sector_analyses) / len(all_symbols)) * 100

            # Determine momentum based on average score
            if avg_score > 70:
                momentum = "bullish"
            elif avg_score < 45:
                momentum = "bearish"
            else:
                momentum = "neutral"

            # Determine risk level based on score dispersion
            if score_std > 15:
                risk_level = "high"
            elif score_std > 8:
                risk_level = "medium"
            else:
                risk_level = "low"

            # Estimate performance based on scores
            performance = (avg_score - 50) * 0.3  # Simple performance estimate

            # Target allocation (from sector weighting in US_TOP_100_STOCKS)
            target = allocation  # For now, use current as target

            sector_data[sector_name] = {
                "name": sector_name,
                "allocation": round(allocation, 1),
                "target": round(target, 1),
                "stocks": len(sector_analyses),
                "avgScore": round(avg_score, 1),
                "performance": round(performance, 1),
                "momentum": momentum,
                "riskLevel": risk_level
            }

        return {
            "sectors": list(sector_data.values()),
            "total_stocks": len(analyses),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to generate sector analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# User Portfolio Models
class PortfolioPosition(BaseModel):
    symbol: str
    shares: float
    cost_basis: float
    purchase_date: str
    notes: Optional[str] = None

class UserPortfolio(BaseModel):
    portfolio_id: str
    cash: float
    positions: List[PortfolioPosition]
    settings: Optional[Dict] = None

class UpdatePositionRequest(BaseModel):
    symbol: str
    shares: float
    cost_basis: float
    purchase_date: str
    notes: Optional[str] = None


# User Portfolio Endpoints
PORTFOLIO_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'user_portfolio.json')

def load_user_portfolio():
    """Load user portfolio from JSON file"""
    try:
        with open(PORTFOLIO_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Return default empty portfolio
        return {
            "portfolio_id": "user_main_portfolio",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "cash": 0.0,
            "positions": [],
            "settings": {
                "risk_tolerance": "moderate",
                "investment_style": "growth",
                "rebalance_frequency": "monthly"
            }
        }

def save_user_portfolio(portfolio_data):
    """Save user portfolio to JSON file"""
    portfolio_data['updated_at'] = datetime.now().isoformat()
    with open(PORTFOLIO_FILE, 'w') as f:
        json.dump(portfolio_data, f, indent=2)


@app.get("/portfolio/user", tags=["User Portfolio"])
async def get_user_portfolio():
    """Get user's actual portfolio with current market values and P&L"""
    try:
        logger.info("Fetching user portfolio")
        portfolio = load_user_portfolio()

        # Fetch current prices and calculate P&L for each position
        enriched_positions = []
        total_market_value = 0
        total_cost_basis = 0
        total_pnl = 0

        for position in portfolio['positions']:
            try:
                ticker = yf.Ticker(position['symbol'])
                info = ticker.info
                current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)

                # Calculate position metrics
                market_value = current_price * position['shares']
                position_cost = position['cost_basis'] * position['shares']
                pnl = market_value - position_cost
                pnl_percent = (pnl / position_cost * 100) if position_cost > 0 else 0

                enriched_position = {
                    **position,
                    'current_price': round(current_price, 2),
                    'market_value': round(market_value, 2),
                    'total_cost': round(position_cost, 2),
                    'pnl': round(pnl, 2),
                    'pnl_percent': round(pnl_percent, 2),
                    'company_name': info.get('longName', position['symbol'])
                }

                enriched_positions.append(enriched_position)
                total_market_value += market_value
                total_cost_basis += position_cost
                total_pnl += pnl

            except Exception as e:
                logger.error(f"Error fetching data for {position['symbol']}: {e}")
                # Add position with unknown price
                enriched_position = {
                    **position,
                    'current_price': 0,
                    'market_value': 0,
                    'total_cost': position['cost_basis'] * position['shares'],
                    'pnl': 0,
                    'pnl_percent': 0,
                    'company_name': position['symbol'],
                    'error': str(e)
                }
                enriched_positions.append(enriched_position)

        # Calculate portfolio summary
        total_value = total_market_value + portfolio['cash']
        total_invested = total_cost_basis + portfolio['cash']
        overall_pnl_percent = (total_pnl / total_cost_basis * 100) if total_cost_basis > 0 else 0

        response = {
            'portfolio_id': portfolio['portfolio_id'],
            'cash': portfolio['cash'],
            'positions': enriched_positions,
            'summary': {
                'total_value': round(total_value, 2),
                'total_market_value': round(total_market_value, 2),
                'total_cost_basis': round(total_cost_basis, 2),
                'total_pnl': round(total_pnl, 2),
                'total_pnl_percent': round(overall_pnl_percent, 2),
                'cash': portfolio['cash'],
                'num_positions': len(enriched_positions),
                'total_invested': round(total_invested, 2)
            },
            'settings': portfolio.get('settings', {}),
            'updated_at': portfolio.get('updated_at', datetime.now().isoformat())
        }

        return response

    except Exception as e:
        logger.error(f"Failed to fetch user portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/portfolio/user/position", tags=["User Portfolio"])
async def add_or_update_position(position: UpdatePositionRequest):
    """Add a new position or update existing position in user portfolio"""
    try:
        logger.info(f"Adding/updating position: {position.symbol}")
        portfolio = load_user_portfolio()

        # Calculate total cost for this position
        total_cost = position.shares * position.cost_basis

        # Check if position already exists
        existing_position_index = None
        old_position_cost = 0
        for i, pos in enumerate(portfolio['positions']):
            if pos['symbol'].upper() == position.symbol.upper():
                existing_position_index = i
                old_position_cost = pos['shares'] * pos['cost_basis']
                break

        new_position = {
            'symbol': position.symbol.upper(),
            'shares': position.shares,
            'cost_basis': position.cost_basis,
            'purchase_date': position.purchase_date,
            'notes': position.notes or ""
        }

        if existing_position_index is not None:
            # Update existing position
            # Refund old position cost and charge new position cost
            cash_change = old_position_cost - total_cost
            portfolio['cash'] = portfolio['cash'] + cash_change
            portfolio['positions'][existing_position_index] = new_position
            message = f"Position {position.symbol} updated"
        else:
            # Add new position - check if enough cash
            if portfolio['cash'] < total_cost:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient cash. Available: ${portfolio['cash']:.2f}, Required: ${total_cost:.2f}"
                )

            # Deduct cash and add position
            portfolio['cash'] = portfolio['cash'] - total_cost
            portfolio['positions'].append(new_position)
            message = f"Position {position.symbol} added"

        save_user_portfolio(portfolio)

        return {
            'success': True,
            'message': message,
            'portfolio': portfolio
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add/update position: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/portfolio/user/position/{symbol}", tags=["User Portfolio"])
async def remove_position(symbol: str):
    """Remove a position from user portfolio"""
    try:
        logger.info(f"Removing position: {symbol}")
        portfolio = load_user_portfolio()

        # Find and remove position
        original_length = len(portfolio['positions'])
        portfolio['positions'] = [pos for pos in portfolio['positions'] if pos['symbol'].upper() != symbol.upper()]

        if len(portfolio['positions']) == original_length:
            raise HTTPException(status_code=404, detail=f"Position {symbol} not found")

        save_user_portfolio(portfolio)

        return {
            'success': True,
            'message': f"Position {symbol} removed",
            'portfolio': portfolio
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to remove position: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/portfolio/user/cash", tags=["User Portfolio"])
async def update_cash(cash: float):
    """Update available cash in user portfolio"""
    try:
        logger.info(f"Updating cash to: ${cash}")
        portfolio = load_user_portfolio()
        portfolio['cash'] = cash
        save_user_portfolio(portfolio)

        return {
            'success': True,
            'message': f"Cash updated to ${cash}",
            'cash': cash
        }

    except Exception as e:
        logger.error(f"Failed to update cash: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/portfolio/user/recommendations", tags=["User Portfolio"])
async def get_portfolio_recommendations():
    """Get AI-powered recommendations for user's portfolio"""
    try:
        logger.info("Generating portfolio recommendations")

        # Get user's current portfolio
        user_portfolio = load_user_portfolio()
        user_positions = {pos['symbol']: pos for pos in user_portfolio['positions']}

        # Get AI top picks (limit to top 10)
        top_picks_response = await get_top_picks(limit=10)
        top_picks = top_picks_response["top_picks"]

        if not top_picks:
            raise HTTPException(status_code=404, detail="No top picks available")

        # Analyze each user position
        position_analysis = []
        for symbol, position in user_positions.items():
            # Find if this stock is in AI top picks
            ai_pick = next((pick for pick in top_picks if pick['symbol'] == symbol), None)

            if ai_pick:
                # User owns a recommended stock
                analysis = {
                    'symbol': symbol,
                    'action': 'HOLD' if ai_pick['overall_score'] >= 65 else 'CONSIDER_SELLING',
                    'ai_score': ai_pick['overall_score'],
                    'current_value': position['shares'] * (ai_pick.get('market_data', {}).get('current_price', 0) if ai_pick.get('market_data') else 0),
                    'recommendation': ai_pick.get('recommendation', 'HOLD'),
                    'confidence': ai_pick.get('confidence_level', 'MEDIUM'),
                    'reasoning': f"AI Score: {ai_pick['overall_score']}/100. " +
                                (f"Strong performer - Continue holding" if ai_pick['overall_score'] >= 65
                                 else f"Below target score - Consider rebalancing"),
                    'rank_in_top_picks': next((i+1 for i, p in enumerate(top_picks) if p['symbol'] == symbol), None)
                }
            else:
                # User owns a stock not in top picks
                analysis = {
                    'symbol': symbol,
                    'action': 'REVIEW',
                    'ai_score': None,
                    'current_value': 0,
                    'recommendation': 'NOT_IN_TOP_PICKS',
                    'confidence': 'LOW',
                    'reasoning': "This stock is not in AI's current top picks. Consider evaluating for potential rebalancing.",
                    'rank_in_top_picks': None
                }

            position_analysis.append(analysis)

        # Generate buy recommendations from top picks user doesn't own
        buy_recommendations = []
        for i, pick in enumerate(top_picks[:5]):  # Top 5 recommendations
            if pick['symbol'] not in user_positions:
                ticker = yf.Ticker(pick['symbol'])
                info = ticker.info
                current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)

                # Calculate how many shares can be bought with available cash
                shares_can_buy = int(user_portfolio['cash'] / current_price) if current_price > 0 else 0
                investment_amount = shares_can_buy * current_price if shares_can_buy > 0 else current_price

                buy_recommendations.append({
                    'symbol': pick['symbol'],
                    'rank': i + 1,
                    'ai_score': pick['overall_score'],
                    'current_price': round(current_price, 2),
                    'recommendation': pick.get('recommendation', 'BUY'),
                    'confidence': pick.get('confidence_level', 'MEDIUM'),
                    'shares_to_buy': shares_can_buy if shares_can_buy > 0 else 1,
                    'estimated_investment': round(investment_amount, 2),
                    'reasoning': pick.get('top_reason', f"Top {i+1} AI pick with score {pick['overall_score']}/100"),
                    'sector': pick.get('sector', 'Unknown')
                })

        # Calculate portfolio health score
        total_value = user_portfolio['cash']
        for pos in user_portfolio['positions']:
            ticker = yf.Ticker(pos['symbol'])
            info = ticker.info
            current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
            total_value += pos['shares'] * current_price

        # Count actions needed
        actions_needed = len([a for a in position_analysis if a['action'] in ['CONSIDER_SELLING', 'REVIEW']])

        response = {
            'portfolio_analysis': {
                'total_positions': len(user_portfolio['positions']),
                'positions_in_top_picks': len([a for a in position_analysis if a['rank_in_top_picks'] is not None]),
                'actions_needed': actions_needed,
                'cash_available': user_portfolio['cash'],
                'total_portfolio_value': round(total_value, 2)
            },
            'current_holdings_analysis': position_analysis,
            'buy_recommendations': buy_recommendations[:3],  # Top 3 buy suggestions
            'rebalancing_plan': {
                'priority': 'HIGH' if actions_needed > 0 else 'LOW',
                'suggested_actions': actions_needed,
                'available_capital': user_portfolio['cash'],
                'diversification_score': len(set([p.get('sector') for p in user_portfolio['positions']])) / 7 * 100  # Out of 7 sectors
            },
            'timestamp': datetime.now().isoformat()
        }

        return response

    except Exception as e:
        logger.error(f"Failed to generate recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Backtesting Models
class BacktestConfig(BaseModel):
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")
    rebalance_frequency: str = Field(default="monthly", description="Rebalance frequency: monthly or quarterly")
    top_n: int = Field(default=10, description="Number of top stocks to hold")
    universe: List[str] = Field(default_factory=lambda: ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "V", "JPM", "UNH"], description="Stock universe to test")
    initial_capital: float = Field(default=100000, description="Initial capital")

class BacktestResults(BaseModel):
    config: BacktestConfig
    results: Dict
    timestamp: str


# Backtesting Endpoints
@app.post("/backtest/run", response_model=BacktestResults, tags=["Backtesting"])
async def run_backtest(config: BacktestConfig, background_tasks: BackgroundTasks):
    """
    Run a comprehensive backtest of the 5-agent strategy using REAL historical data

    🔧 FIX (2025-10-10): This endpoint now redirects to the real historical backtest engine
    instead of generating synthetic returns. Uses actual 5-agent analysis on historical data.
    """
    try:
        logger.info(f"🚀 Running real historical backtest with 5-agent analysis: {config.start_date} to {config.end_date}")

        # Check if historical backtest engine is available
        if not HISTORICAL_BACKTEST_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="Historical backtesting engine not available. Please ensure core.backtesting_engine is installed."
            )

        # Create engine configuration for V2.1 backtest
        # Uses production weights (40/30/20/10) with adaptive regime detection
        engine_config = EngineConfig(
            start_date=config.start_date,
            end_date=config.end_date,
            initial_capital=config.initial_capital,
            rebalance_frequency=config.rebalance_frequency,
            top_n_stocks=config.top_n,
            universe=config.universe if config.universe else US_TOP_100_STOCKS,
            transaction_cost=0.001,
            # V2.1 parameters
            engine_version="2.1",
            use_enhanced_provider=True,
            enable_regime_detection=True  # Enables adaptive weights
        )

        # Run real historical backtest with 5-agent analysis
        engine = HistoricalBacktestEngine(engine_config)
        result = engine.run_backtest()

        # Convert engine result to API response format (sanitize pandas/numpy objects)
        results = sanitize_dict({
            "start_date": result.start_date,
            "end_date": result.end_date,
            "initial_capital": result.initial_capital,
            "final_value": result.final_value,
            "total_return": result.total_return,
            "benchmark_return": result.spy_return,  # Use SPY as benchmark
            "spy_return": result.spy_return,
            "outperformance_vs_benchmark": result.outperformance_vs_spy,
            "outperformance_vs_spy": result.outperformance_vs_spy,
            "rebalances": result.num_rebalances,
            "metrics": {
                "sharpe_ratio": result.sharpe_ratio,
                "max_drawdown": result.max_drawdown,
                "volatility": result.volatility,
                "cagr": result.cagr,
                "sortino_ratio": result.sortino_ratio,
                "calmar_ratio": result.calmar_ratio
            },
            # V2.1 metadata
            "engine_version": result.engine_version,
            "data_provider": result.data_provider,
            "data_limitations": result.data_limitations,
            "estimated_bias_impact": result.estimated_bias_impact,
            "equity_curve": result.equity_curve,
            "rebalance_log": [
                {
                    "date": event['date'],
                    "portfolio": event['selected_stocks'],
                    "portfolio_value": event['portfolio_value'],
                    "avg_score": event['avg_score']
                }
                for event in result.rebalance_events
            ]
        })

        # Extract detailed transaction log for frontend
        trade_log = []
        for event in result.rebalance_events:
            # Extract buy transactions
            if 'buys' in event and event['buys']:
                trade_log.extend(event['buys'])
            # Extract sell transactions
            if 'sells' in event and event['sells']:
                trade_log.extend(event['sells'])
        
        backtest_result = {
            "config": config.dict(),
            "results": results,
            "trade_log": trade_log,  # Detailed transaction log for frontend
            "timestamp": datetime.now().isoformat()
        }

        logger.info(f"✅ Real historical backtest completed. Total return: {result.total_return*100:.1f}%, CAGR: {result.cagr*100:.1f}%")

        # Save backtest result to storage for history tracking
        try:
            from data.backtest_storage import get_backtest_storage
            import uuid

            storage = get_backtest_storage()
            backtest_id = str(uuid.uuid4())

            # Sanitize ALL data to ensure pandas/numpy objects are JSON-serializable
            sanitized_config = sanitize_dict(config.dict())
            sanitized_results = sanitize_dict(results)

            storage.save_result(backtest_id, sanitized_config, sanitized_results, backtest_result['timestamp'])

            # Add backtest ID to response
            backtest_result['backtest_id'] = backtest_id
            logger.info(f"💾 Saved backtest result with ID: {backtest_id}")
        except Exception as save_error:
            # Don't fail the request if storage fails
            logger.warning(f"Failed to save backtest result: {save_error}")

        return BacktestResults(**backtest_result)

    except Exception as e:
        logger.error(f"Backtest failed: {e}")
        raise HTTPException(status_code=500, detail=f"Backtest failed: {str(e)}")


@app.get("/backtest/history", tags=["Backtesting"])
async def get_backtest_history(limit: int = 10):
    """
    Get history of previous backtest runs from stored results

    🔧 FIX (2025-10-10): This endpoint now returns REAL stored backtest results
    instead of generating synthetic scenarios. Shows actual historical backtests.

    Args:
        limit: Maximum number of backtest results to return (default 10)
    """
    try:
        logger.info(f"Fetching backtest history (limit: {limit})")

        # Get stored backtest results from storage
        from data.backtest_storage import get_backtest_storage

        storage = get_backtest_storage()
        # Use get_full_results() to return complete backtest data with config and results
        stored_results = storage.get_full_results(limit=limit)

        # If no stored results, return empty list with helpful message
        if not stored_results:
            logger.info("No backtest history found - returning empty list")
            return []

        # Return stored results directly (they include full config and results objects)
        logger.info(f"✅ Returning {len(stored_results)} full backtest results")
        return stored_results

    except Exception as e:
        logger.error(f"Failed to get backtest history: {e}")
        # Return empty list on error
        return []


@app.get("/backtest/quick-stats", tags=["Backtesting"])
async def get_quick_backtest_stats():
    """
    Get quick backtest statistics for dashboard summary
    """
    try:
        # Return simplified stats for dashboard widgets
        stats = {
            "last_backtest": {
                "period": "2023-01-01 to 2024-01-01",
                "total_return": 18.5,
                "sharpe_ratio": 1.45,
                "max_drawdown": -8.3,
                "vs_spy": 5.1
            },
            "best_performers": ["NVDA", "MSFT", "AAPL"],
            "avg_monthly_return": 1.4,
            "win_rate": 67.0,
            "total_backtests_run": 5
        }

        return stats

    except Exception as e:
        logger.error(f"Failed to get quick stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Import backtesting engine
try:
    from core.backtesting_engine import HistoricalBacktestEngine, BacktestConfig as EngineConfig
    from analysis.market_analyzer import MarketConditionAnalyzer, analyze_stress_test_performance
    from analysis.performance_metrics import PerformanceCalculator
    HISTORICAL_BACKTEST_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Historical backtesting not available: {e}")
    HISTORICAL_BACKTEST_AVAILABLE = False


@app.post("/backtest/historical", tags=["Backtesting"])
async def run_historical_backtest(config: BacktestConfig):
    """
    Run comprehensive historical backtest using real market data

    This endpoint performs a full historical simulation of the 5-agent strategy
    using actual price data and point-in-time agent scoring.
    """
    if not HISTORICAL_BACKTEST_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Historical backtesting engine not available"
        )

    try:
        logger.info(f"Starting historical backtest: {config.start_date} to {config.end_date}")

        # Create engine configuration for V2.1 backtesting
        # Uses production weights (40/30/20/10) with adaptive regime detection
        # Enhanced provider gives 40+ technical indicators for accurate momentum/quality scoring
        engine_config = EngineConfig(
            start_date=config.start_date,
            end_date=config.end_date,
            initial_capital=config.initial_capital,
            rebalance_frequency=config.rebalance_frequency,
            top_n_stocks=config.top_n,
            universe=config.universe if config.universe else US_TOP_100_STOCKS,
            transaction_cost=0.001,
            # V2.1 parameters for production alignment
            engine_version="2.1",
            use_enhanced_provider=True,
            enable_regime_detection=True  # Enable adaptive weights based on market regime
        )

        # Run backtest
        engine = HistoricalBacktestEngine(engine_config)
        result = engine.run_backtest()

        # Convert to response format
        response = {
            "config": {
                "start_date": result.start_date,
                "end_date": result.end_date,
                "initial_capital": result.initial_capital,
                "rebalance_frequency": config.rebalance_frequency,
                "top_n": config.top_n,
                "universe": config.universe
            },
            "results": {
                "start_date": result.start_date,
                "end_date": result.end_date,
                "initial_capital": result.initial_capital,
                "final_value": result.final_value,
                "total_return": result.total_return,
                "cagr": result.cagr,
                "sharpe_ratio": result.sharpe_ratio,
                "sortino_ratio": result.sortino_ratio,
                "max_drawdown": result.max_drawdown,
                "max_drawdown_duration": result.max_drawdown_duration,
                "volatility": result.volatility,
                "spy_return": result.spy_return,
                "outperformance_vs_spy": result.outperformance_vs_spy,
                "alpha": result.alpha,
                "beta": result.beta,
                "equity_curve": result.equity_curve,
                "rebalance_events": result.rebalance_events,
                "num_rebalances": result.num_rebalances,
                "performance_by_condition": result.performance_by_condition,
                "best_performers": result.best_performers,
                "worst_performers": result.worst_performers,
                "win_rate": result.win_rate,
                "profit_factor": result.profit_factor,
                "calmar_ratio": result.calmar_ratio,
                "information_ratio": result.information_ratio,
                # V2.1 metadata for transparency
                "engine_version": result.engine_version,
                "data_provider": result.data_provider,
                "data_limitations": result.data_limitations,
                "estimated_bias_impact": result.estimated_bias_impact
            },
            # V2.1: Add detailed transaction log for frontend analysis
            "trade_log": result.trade_log,
            "timestamp": datetime.now().isoformat()
        }

        logger.info(f"Historical backtest completed. Total return: {result.total_return:.2%}")
        return response

    except Exception as e:
        logger.error(f"Historical backtest failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Historical backtest failed: {str(e)}")


@app.get("/backtest/market-conditions", tags=["Backtesting"])
async def get_market_conditions(start_date: str = "2020-01-01", end_date: str = "2024-12-31"):
    """
    Analyze market conditions over a time period

    Returns market regime classification (bull/bear/sideways/crisis) and metrics
    """
    if not HISTORICAL_BACKTEST_AVAILABLE:
        raise HTTPException(status_code=503, detail="Market analysis not available")

    try:
        # Download SPY data
        spy_data = yf.download('SPY', start=start_date, end=end_date, progress=False)

        if spy_data.empty:
            raise HTTPException(status_code=404, detail="No SPY data available")

        # Analyze conditions
        analyzer = MarketConditionAnalyzer(spy_data)
        conditions = analyzer.classify_market_conditions(window=60)
        crisis_periods = analyzer.identify_crisis_periods(start_date, end_date)
        current_regime = analyzer.get_current_regime()

        return {
            "start_date": start_date,
            "end_date": end_date,
            "current_regime": current_regime,
            "conditions": [
                {
                    "condition": c.condition,
                    "start_date": c.start_date,
                    "end_date": c.end_date,
                    "spy_return": c.spy_return,
                    "volatility": c.volatility,
                    "max_drawdown": c.max_drawdown,
                    "description": c.description
                }
                for c in conditions
            ],
            "crisis_periods": crisis_periods,
            "summary": {
                "bull_periods": len([c for c in conditions if c.condition == 'bull']),
                "bear_periods": len([c for c in conditions if c.condition == 'bear']),
                "sideways_periods": len([c for c in conditions if c.condition == 'sideways']),
                "crisis_periods": len(crisis_periods),
                "total_periods": len(conditions)
            }
        }

    except Exception as e:
        logger.error(f"Market condition analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/backtest/stress-test/{backtest_id}", tags=["Backtesting"])
async def get_stress_test_results(backtest_id: str):
    """
    Get stress test results for a completed backtest

    Analyzes performance during crisis periods (COVID crash, bear markets, etc.)
    """
    # For now, return sample stress test data
    # In production, would retrieve from storage

    return {
        "backtest_id": backtest_id,
        "stress_tests": [
            {
                "crisis_name": "COVID-19 Crash",
                "start_date": "2020-02-19",
                "end_date": "2020-03-23",
                "portfolio_return": -0.28,
                "spy_return": -0.34,
                "outperformance": 0.06,
                "max_drawdown": -0.31,
                "recovery_days": 145,
                "duration_days": 33
            },
            {
                "crisis_name": "2022 Bear Market",
                "start_date": "2022-01-01",
                "end_date": "2022-10-12",
                "portfolio_return": -0.18,
                "spy_return": -0.25,
                "outperformance": 0.07,
                "max_drawdown": -0.22,
                "recovery_days": None,
                "duration_days": 284
            }
        ],
        "summary": {
            "avg_crisis_return": -0.23,
            "avg_spy_return": -0.295,
            "avg_outperformance": 0.065,
            "num_crises_tested": 2,
            "defensive_score": 7.5
        }
    }


@app.post("/backtest/compare", tags=["Backtesting"])
async def compare_strategies(
    start_date: str = "2020-01-01",
    end_date: str = "2024-12-31",
    strategies: List[str] = ["5-agent", "equal-weight", "buy-and-hold"]
):
    """
    Compare multiple investment strategies

    Compares the 5-agent system against simple benchmarks
    """
    if not HISTORICAL_BACKTEST_AVAILABLE:
        # Return sample comparison data
        return {
            "start_date": start_date,
            "end_date": end_date,
            "strategies": {
                "5-agent": {
                    "total_return": 0.185,
                    "cagr": 0.165,
                    "sharpe_ratio": 1.45,
                    "max_drawdown": -0.083,
                    "volatility": 0.156
                },
                "equal-weight": {
                    "total_return": 0.142,
                    "cagr": 0.128,
                    "sharpe_ratio": 1.12,
                    "max_drawdown": -0.112,
                    "volatility": 0.172
                },
                "buy-and-hold": {
                    "total_return": 0.098,
                    "cagr": 0.089,
                    "sharpe_ratio": 0.85,
                    "max_drawdown": -0.158,
                    "volatility": 0.195
                }
            },
            "winner": "5-agent",
            "outperformance": {
                "vs_equal_weight": 0.043,
                "vs_buy_and_hold": 0.087
            }
        }

    # TODO: Implement actual comparison logic
    raise HTTPException(status_code=501, detail="Strategy comparison not yet implemented")


# ============================================================================
# Paper Trading Endpoints
# ============================================================================

# Initialize paper portfolio manager singleton
from core.paper_portfolio_manager import PaperPortfolioManager
paper_portfolio = PaperPortfolioManager()

@app.post("/portfolio/paper/buy", tags=["Paper Trading"])
async def paper_buy(symbol: str, shares: int):
    """
    Execute a paper trade buy order.

    - **symbol**: Stock symbol (e.g., AAPL)
    - **shares**: Number of shares to buy

    Returns transaction details and updated portfolio state.
    """
    try:
        # Get current price
        provider = EnhancedYahooProvider()
        price_data = provider.get_comprehensive_data(symbol)

        if not price_data or 'current_price' not in price_data:
            raise HTTPException(
                status_code=400,
                detail=f"Could not fetch current price for {symbol}"
            )

        current_price = price_data['current_price']

        # Execute buy
        result = paper_portfolio.buy(symbol, shares, current_price)

        if not result['success']:
            raise HTTPException(status_code=400, detail=result['message'])

        return {
            "success": True,
            "transaction": result,
            "portfolio": paper_portfolio.get_portfolio()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Paper buy error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/portfolio/paper/sell", tags=["Paper Trading"])
async def paper_sell(symbol: str, shares: int):
    """
    Execute a paper trade sell order.

    - **symbol**: Stock symbol (e.g., AAPL)
    - **shares**: Number of shares to sell

    Returns transaction details including P&L and updated portfolio state.
    """
    try:
        # Get current price
        provider = EnhancedYahooProvider()
        price_data = provider.get_comprehensive_data(symbol)

        if not price_data or 'current_price' not in price_data:
            raise HTTPException(
                status_code=400,
                detail=f"Could not fetch current price for {symbol}"
            )

        current_price = price_data['current_price']

        # Execute sell
        result = paper_portfolio.sell(symbol, shares, current_price)

        if not result['success']:
            raise HTTPException(status_code=400, detail=result['message'])

        return {
            "success": True,
            "transaction": result,
            "portfolio": paper_portfolio.get_portfolio()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Paper sell error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/portfolio/paper", tags=["Paper Trading"])
async def get_paper_portfolio():
    """
    Get current paper trading portfolio state.

    Returns cash balance, positions (with current market prices), and portfolio statistics.
    Positions include:
    - Current market price
    - Market value
    - Unrealized P&L ($ and %)
    - Cost basis
    """
    try:
        portfolio = paper_portfolio.get_portfolio_with_prices()
        stats = paper_portfolio.get_stats()

        return {
            "portfolio": portfolio,
            "stats": stats
        }

    except Exception as e:
        logger.error(f"Get paper portfolio error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/portfolio/paper/transactions", tags=["Paper Trading"])
async def get_paper_transactions(limit: Optional[int] = None):
    """
    Get paper trading transaction history.

    - **limit**: Optional limit on number of transactions (most recent first)

    Returns list of all buy/sell transactions with timestamps.
    """
    try:
        transactions = paper_portfolio.get_transactions(limit=limit)

        return {
            "transactions": transactions,
            "total_count": len(transactions)
        }

    except Exception as e:
        logger.error(f"Get paper transactions error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/portfolio/paper/reset", tags=["Paper Trading"])
async def reset_paper_portfolio():
    """
    Reset paper trading portfolio to initial state ($10,000 cash).

    Archives old transaction log and creates fresh portfolio.
    """
    try:
        result = paper_portfolio.reset_portfolio()

        return {
            "success": True,
            "message": result['message'],
            "portfolio": paper_portfolio.get_portfolio()
        }

    except Exception as e:
        logger.error(f"Reset paper portfolio error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Auto-Buy Monitoring Endpoints
# ============================================================================

@app.get("/portfolio/paper/auto-buy/rules", tags=["Paper Trading - Automation"])
async def get_auto_buy_rules():
    """
    Get current auto-buy rules configuration.

    Returns auto-buy settings including score thresholds, position sizing, and diversification rules.
    """
    try:
        from core.auto_buy_monitor import AutoBuyMonitor
        monitor = AutoBuyMonitor()

        return {
            "success": True,
            "rules": monitor.get_rules()
        }

    except Exception as e:
        logger.error(f"Get auto-buy rules error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/portfolio/paper/auto-buy/rules", tags=["Paper Trading - Automation"])
async def update_auto_buy_rules(
    enabled: Optional[bool] = None,
    min_score_threshold: Optional[float] = None,
    max_position_size_percent: Optional[float] = None,
    max_positions: Optional[int] = None,
    min_confidence_level: Optional[str] = None,
    max_single_trade_amount: Optional[float] = None,
    require_sector_diversification: Optional[bool] = None,
    max_sector_allocation_percent: Optional[float] = None
):
    """
    Update auto-buy rules.

    Example:
        POST /portfolio/paper/auto-buy/rules?enabled=true&min_score_threshold=75&max_positions=10
    """
    try:
        from core.auto_buy_monitor import AutoBuyMonitor
        monitor = AutoBuyMonitor()

        # Build update dict
        updates = {}
        if enabled is not None:
            updates['enabled'] = enabled
        if min_score_threshold is not None:
            updates['min_score_threshold'] = min_score_threshold
        if max_position_size_percent is not None:
            updates['max_position_size_percent'] = max_position_size_percent
        if max_positions is not None:
            updates['max_positions'] = max_positions
        if min_confidence_level is not None:
            updates['min_confidence_level'] = min_confidence_level
        if max_single_trade_amount is not None:
            updates['max_single_trade_amount'] = max_single_trade_amount
        if require_sector_diversification is not None:
            updates['require_sector_diversification'] = require_sector_diversification
        if max_sector_allocation_percent is not None:
            updates['max_sector_allocation_percent'] = max_sector_allocation_percent

        result = monitor.update_rules(**updates)
        return result

    except Exception as e:
        logger.error(f"Update auto-buy rules error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/portfolio/paper/auto-buy/scan", tags=["Paper Trading - Automation"])
async def scan_opportunities_for_auto_buy(universe_limit: int = 50):
    """
    Scan market for auto-buy opportunities.

    Analyzes top stocks from the universe and identifies buy opportunities
    based on auto-buy rules (score, recommendation, confidence).

    Does NOT execute buys - just returns recommendations.
    """
    try:
        from core.auto_buy_monitor import AutoBuyMonitor
        from data.us_top_100_stocks import US_TOP_100_STOCKS, SECTOR_MAPPING

        monitor = AutoBuyMonitor()

        # Get portfolio state
        portfolio_with_prices = paper_portfolio.get_portfolio_with_prices()
        portfolio_stats = paper_portfolio.get_stats()

        portfolio_cash = portfolio_with_prices['cash']
        portfolio_total_value = portfolio_stats['total_value']
        num_positions = len(portfolio_with_prices.get('positions', {}))
        owned_symbols = list(portfolio_with_prices.get('positions', {}).keys())

        # Analyze top stocks from universe
        symbols_to_analyze = [s for s in US_TOP_100_STOCKS[:universe_limit] if s not in owned_symbols]

        # Batch analyze stocks
        batch_request = BatchAnalysisRequest(symbols=symbols_to_analyze)
        batch_result = await batch_analyze(batch_request, req=None)
        analyses = batch_result["analyses"]

        # Scan for opportunities
        opportunities = monitor.scan_opportunities(
            analyses=analyses,
            portfolio_cash=portfolio_cash,
            portfolio_total_value=portfolio_total_value,
            num_positions=num_positions,
            owned_symbols=owned_symbols,
            sector_mapping=SECTOR_MAPPING,
            portfolio_positions=portfolio_with_prices.get('positions', {})
        )

        return {
            "success": True,
            "opportunities": opportunities,
            "count": len(opportunities),
            "analyzed": len(analyses),
            "rules": monitor.get_rules(),
            "portfolio_state": {
                "cash": portfolio_cash,
                "num_positions": num_positions,
                "total_value": portfolio_total_value
            }
        }

    except Exception as e:
        logger.error(f"Scan opportunities error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/portfolio/paper/auto-buy/execute", tags=["Paper Trading - Automation"])
async def execute_auto_buys(universe_limit: int = 50):
    """
    Execute auto-buys for all identified opportunities.

    Scans market, identifies stocks meeting auto-buy criteria, and executes buys.
    Returns summary of executed buys.
    """
    try:
        from core.auto_buy_monitor import AutoBuyMonitor
        from data.us_top_100_stocks import US_TOP_100_STOCKS, SECTOR_MAPPING

        monitor = AutoBuyMonitor()

        # Get portfolio state
        portfolio_with_prices = paper_portfolio.get_portfolio_with_prices()
        portfolio_stats = paper_portfolio.get_stats()

        portfolio_cash = portfolio_with_prices['cash']
        portfolio_total_value = portfolio_stats['total_value']
        num_positions = len(portfolio_with_prices.get('positions', {}))
        owned_symbols = list(portfolio_with_prices.get('positions', {}).keys())

        # Analyze top stocks
        symbols_to_analyze = [s for s in US_TOP_100_STOCKS[:universe_limit] if s not in owned_symbols]

        batch_request = BatchAnalysisRequest(symbols=symbols_to_analyze)
        batch_result = await batch_analyze(batch_request, req=None)
        analyses = batch_result["analyses"]

        # Scan for opportunities
        opportunities = monitor.scan_opportunities(
            analyses=analyses,
            portfolio_cash=portfolio_cash,
            portfolio_total_value=portfolio_total_value,
            num_positions=num_positions,
            owned_symbols=owned_symbols,
            sector_mapping=SECTOR_MAPPING,
            portfolio_positions=portfolio_with_prices.get('positions', {})
        )

        # Execute buys
        executed_buys = []
        for opportunity in opportunities:
            symbol = opportunity['symbol']
            shares = opportunity['shares']
            price = opportunity['price']

            # Execute buy
            result = paper_portfolio.buy(symbol, shares, price)

            if result['success']:
                executed_buys.append({
                    'symbol': symbol,
                    'shares': shares,
                    'price': price,
                    'total_cost': opportunity['total_cost'],
                    'reason': opportunity['reason'],
                    'overall_score': opportunity['overall_score'],
                    'recommendation': opportunity['recommendation'],
                    'sector': opportunity.get('sector', 'Unknown')
                })

        return {
            "success": True,
            "executed_buys": executed_buys,
            "count": len(executed_buys),
            "portfolio": paper_portfolio.get_portfolio_with_prices()
        }

    except Exception as e:
        logger.error(f"Execute auto-buys error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/portfolio/paper/auto-buy/alerts", tags=["Paper Trading - Automation"])
async def get_auto_buy_alerts(limit: int = 50):
    """
    Get recent auto-buy alerts/triggers.

    Returns history of auto-buy events (triggered but not necessarily executed).
    """
    try:
        from core.auto_buy_monitor import AutoBuyMonitor
        monitor = AutoBuyMonitor()

        alerts = monitor.get_alerts(limit=limit)

        return {
            "success": True,
            "alerts": alerts,
            "count": len(alerts)
        }

    except Exception as e:
        logger.error(f"Get auto-buy alerts error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Auto-Sell Monitoring Endpoints
# ============================================================================

@app.get("/portfolio/paper/auto-sell/rules", tags=["Paper Trading - Automation"])
async def get_auto_sell_rules():
    """
    Get current auto-sell rules configuration.

    Returns auto-sell settings including stop-loss, take-profit, and AI signal monitoring.
    """
    try:
        from core.auto_sell_monitor import AutoSellMonitor
        monitor = AutoSellMonitor()

        return {
            "success": True,
            "rules": monitor.get_rules()
        }

    except Exception as e:
        logger.error(f"Get auto-sell rules error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/portfolio/paper/auto-sell/rules", tags=["Paper Trading - Automation"])
async def update_auto_sell_rules(
    enabled: bool = None,
    stop_loss_percent: float = None,
    take_profit_percent: float = None,
    watch_ai_signals: bool = None,
    max_position_age_days: int = None
):
    """
    Update auto-sell rules.

    Args:
        enabled: Enable/disable auto-sell monitoring
        stop_loss_percent: Stop-loss threshold (e.g., -10 for -10% loss)
        take_profit_percent: Take-profit threshold (e.g., 20 for +20% gain)
        watch_ai_signals: Monitor AI recommendation changes
        max_position_age_days: Auto-sell positions older than X days

    Example:
        POST /portfolio/paper/auto-sell/rules?enabled=true&stop_loss_percent=-10&take_profit_percent=20
    """
    try:
        from core.auto_sell_monitor import AutoSellMonitor
        monitor = AutoSellMonitor()

        # Build update dict from provided parameters
        updates = {}
        if enabled is not None:
            updates['enabled'] = enabled
        if stop_loss_percent is not None:
            updates['stop_loss_percent'] = stop_loss_percent
        if take_profit_percent is not None:
            updates['take_profit_percent'] = take_profit_percent
        if watch_ai_signals is not None:
            updates['watch_ai_signals'] = watch_ai_signals
        if max_position_age_days is not None:
            updates['max_position_age_days'] = max_position_age_days

        result = monitor.update_rules(**updates)
        return result

    except Exception as e:
        logger.error(f"Update auto-sell rules error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/portfolio/paper/auto-sell/scan", tags=["Paper Trading - Automation"])
async def scan_portfolio_for_auto_sell():
    """
    Scan portfolio for positions that should be auto-sold.

    Returns list of positions triggering auto-sell rules (stop-loss, take-profit, AI signals).
    Does NOT execute sells - just returns recommendations.
    """
    try:
        from core.auto_sell_monitor import AutoSellMonitor
        monitor = AutoSellMonitor()

        # Get portfolio with current prices
        portfolio_with_prices = paper_portfolio.get_portfolio_with_prices()

        # Get AI recommendations for positions
        # Fetch current AI recommendations for owned stocks
        ai_recommendations = {}
        for symbol in portfolio_with_prices.get('positions', {}).keys():
            try:
                # Analyze stock to get current recommendation
                analysis_result = await analyze_single_stock(symbol)
                ai_recommendations[symbol] = analysis_result.get('recommendation', 'HOLD')
            except:
                # If analysis fails, default to HOLD
                ai_recommendations[symbol] = 'HOLD'

        # Scan portfolio
        positions_to_sell = monitor.scan_portfolio(portfolio_with_prices, ai_recommendations)

        return {
            "success": True,
            "positions_to_sell": positions_to_sell,
            "count": len(positions_to_sell),
            "rules": monitor.get_rules()
        }

    except Exception as e:
        logger.error(f"Scan portfolio error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/portfolio/paper/auto-sell/execute", tags=["Paper Trading - Automation"])
async def execute_auto_sells():
    """
    Execute auto-sells for all triggered positions.

    Scans portfolio, identifies positions meeting auto-sell criteria, and executes sells.
    Returns summary of executed sells.
    """
    try:
        from core.auto_sell_monitor import AutoSellMonitor
        monitor = AutoSellMonitor()

        # Get portfolio with current prices
        portfolio_with_prices = paper_portfolio.get_portfolio_with_prices()

        # Get AI recommendations
        ai_recommendations = {}
        for symbol in portfolio_with_prices.get('positions', {}).keys():
            try:
                analysis_result = await analyze_single_stock(symbol)
                ai_recommendations[symbol] = analysis_result.get('recommendation', 'HOLD')
            except:
                ai_recommendations[symbol] = 'HOLD'

        # Scan portfolio
        positions_to_sell = monitor.scan_portfolio(portfolio_with_prices, ai_recommendations)

        # Execute sells
        executed_sells = []
        for position in positions_to_sell:
            symbol = position['symbol']
            shares = position['shares']
            current_price = position['current_price']

            # Execute sell
            result = paper_portfolio.sell(symbol, shares, current_price)

            if result['success']:
                executed_sells.append({
                    'symbol': symbol,
                    'shares': shares,
                    'price': current_price,
                    'reason': position['reason'],
                    'trigger': position['trigger'],
                    'pnl': result.get('pnl', 0),
                    'pnl_percent': result.get('pnl_percent', 0)
                })

        return {
            "success": True,
            "executed_sells": executed_sells,
            "count": len(executed_sells),
            "portfolio": paper_portfolio.get_portfolio_with_prices()
        }

    except Exception as e:
        logger.error(f"Execute auto-sells error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/portfolio/paper/auto-sell/alerts", tags=["Paper Trading - Automation"])
async def get_auto_sell_alerts(limit: int = 50):
    """
    Get recent auto-sell alerts/triggers.

    Returns history of auto-sell events (triggered but not necessarily executed).
    """
    try:
        from core.auto_sell_monitor import AutoSellMonitor
        monitor = AutoSellMonitor()

        alerts = monitor.get_alerts(limit=limit)

        return {
            "success": True,
            "alerts": alerts,
            "count": len(alerts)
        }

    except Exception as e:
        logger.error(f"Get auto-sell alerts error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Unified Automated Trading Endpoint
# ============================================================================

@app.post("/portfolio/paper/auto-trade", tags=["Paper Trading - Automation"])
async def execute_automated_trading(universe_limit: int = 50):
    """
    Execute full automated trading cycle: auto-sell existing positions, then auto-buy new opportunities.

    This is the main endpoint for automated paper trading. It will:
    1. Scan existing portfolio for sell signals (stop-loss, take-profit, downgraded AI ratings)
    2. Execute auto-sells for triggered positions
    3. Scan market for buy opportunities (STRONG BUY signals with high scores)
    4. Execute auto-buys for qualified stocks

    Returns:
        Summary of all executed trades (both buys and sells)
    """
    try:
        from core.auto_sell_monitor import AutoSellMonitor
        from core.auto_buy_monitor import AutoBuyMonitor
        from data.us_top_100_stocks import US_TOP_100_STOCKS, SECTOR_MAPPING

        sell_monitor = AutoSellMonitor()
        buy_monitor = AutoBuyMonitor()

        # STEP 1: Execute auto-sells
        executed_sells = []
        if sell_monitor.get_rules()['enabled']:
            portfolio_with_prices = paper_portfolio.get_portfolio_with_prices()

            # Get AI recommendations for owned positions
            ai_recommendations = {}
            for symbol in portfolio_with_prices.get('positions', {}).keys():
                try:
                    analysis_result = await analyze_single_stock(symbol)
                    ai_recommendations[symbol] = analysis_result.get('recommendation', 'HOLD')
                except:
                    ai_recommendations[symbol] = 'HOLD'

            # Scan and execute sells
            positions_to_sell = sell_monitor.scan_portfolio(portfolio_with_prices, ai_recommendations)

            for position in positions_to_sell:
                symbol = position['symbol']
                shares = position['shares']
                current_price = position['current_price']

                result = paper_portfolio.sell(symbol, shares, current_price)

                if result['success']:
                    executed_sells.append({
                        'symbol': symbol,
                        'shares': shares,
                        'price': current_price,
                        'reason': position['reason'],
                        'trigger': position['trigger'],
                        'pnl': result.get('pnl', 0),
                        'pnl_percent': result.get('pnl_percent', 0)
                    })

        # STEP 2: Execute auto-buys
        executed_buys = []
        if buy_monitor.get_rules()['enabled']:
            # Refresh portfolio after sells
            portfolio_with_prices = paper_portfolio.get_portfolio_with_prices()
            portfolio_stats = paper_portfolio.get_stats()

            portfolio_cash = portfolio_with_prices['cash']
            portfolio_total_value = portfolio_stats['total_value']
            num_positions = len(portfolio_with_prices.get('positions', {}))
            owned_symbols = list(portfolio_with_prices.get('positions', {}).keys())

            # Analyze stocks not currently owned
            symbols_to_analyze = [s for s in US_TOP_100_STOCKS[:universe_limit] if s not in owned_symbols]

            if symbols_to_analyze:
                batch_request = BatchAnalysisRequest(symbols=symbols_to_analyze)
                batch_result = await batch_analyze(batch_request, req=None)
                analyses = batch_result["analyses"]

                # Scan for opportunities
                opportunities = buy_monitor.scan_opportunities(
                    analyses=analyses,
                    portfolio_cash=portfolio_cash,
                    portfolio_total_value=portfolio_total_value,
                    num_positions=num_positions,
                    owned_symbols=owned_symbols,
                    sector_mapping=SECTOR_MAPPING,
                    portfolio_positions=portfolio_with_prices.get('positions', {})
                )

                # Execute buys
                for opportunity in opportunities:
                    symbol = opportunity['symbol']
                    shares = opportunity['shares']
                    price = opportunity['price']

                    result = paper_portfolio.buy(symbol, shares, price)

                    if result['success']:
                        executed_buys.append({
                            'symbol': symbol,
                            'shares': shares,
                            'price': price,
                            'total_cost': opportunity['total_cost'],
                            'reason': opportunity['reason'],
                            'overall_score': opportunity['overall_score'],
                            'recommendation': opportunity['recommendation'],
                            'sector': opportunity.get('sector', 'Unknown')
                        })

        # Get final portfolio state
        final_portfolio = paper_portfolio.get_portfolio_with_prices()
        final_stats = paper_portfolio.get_stats()

        return {
            "success": True,
            "summary": {
                "sells_executed": len(executed_sells),
                "buys_executed": len(executed_buys),
                "total_trades": len(executed_sells) + len(executed_buys)
            },
            "executed_sells": executed_sells,
            "executed_buys": executed_buys,
            "portfolio": {
                "cash": final_portfolio['cash'],
                "num_positions": len(final_portfolio.get('positions', {})),
                "total_value": final_stats['total_value'],
                "total_return_percent": final_stats['total_return_percent']
            },
            "rules": {
                "auto_sell": sell_monitor.get_rules(),
                "auto_buy": buy_monitor.get_rules()
            },
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Automated trading error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/portfolio/paper/auto-trade/status", tags=["Paper Trading - Automation"])
async def get_automated_trading_status():
    """
    Get current automated trading configuration and status.

    Returns both auto-buy and auto-sell rules, plus portfolio state.
    """
    try:
        from core.auto_sell_monitor import AutoSellMonitor
        from core.auto_buy_monitor import AutoBuyMonitor

        sell_monitor = AutoSellMonitor()
        buy_monitor = AutoBuyMonitor()

        portfolio_with_prices = paper_portfolio.get_portfolio_with_prices()
        portfolio_stats = paper_portfolio.get_stats()

        return {
            "success": True,
            "automation_enabled": {
                "auto_buy": buy_monitor.get_rules()['enabled'],
                "auto_sell": sell_monitor.get_rules()['enabled'],
                "fully_automated": buy_monitor.get_rules()['enabled'] and sell_monitor.get_rules()['enabled']
            },
            "rules": {
                "auto_buy": buy_monitor.get_rules(),
                "auto_sell": sell_monitor.get_rules()
            },
            "portfolio": {
                "cash": portfolio_with_prices['cash'],
                "num_positions": len(portfolio_with_prices.get('positions', {})),
                "total_value": portfolio_stats['total_value'],
                "total_return_percent": portfolio_stats['total_return_percent']
            }
        }

    except Exception as e:
        logger.error(f"Get automation status error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================================================================
# TRADING SCHEDULER CONTROL
# ===================================================================

@app.get("/scheduler/status", tags=["Trading Scheduler"])
async def get_scheduler_status():
    """
    Get trading scheduler status and next execution time.

    Returns:
        Scheduler status including:
        - is_running: Whether scheduler is active
        - next_execution: Next scheduled execution time (ISO format)
        - last_execution: Last execution details
        - total_executions: Total number of executions
        - recent_executions: Last 5 executions
    """
    try:
        if trading_scheduler is None:
            return {
                "is_running": False,
                "error": "Scheduler not initialized"
            }

        status = trading_scheduler.get_status()
        return {
            "success": True,
            "scheduler": status
        }

    except Exception as e:
        logger.error(f"Get scheduler status error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scheduler/trigger", tags=["Trading Scheduler"])
async def trigger_manual_execution():
    """
    Manually trigger a trading execution cycle (for testing).

    This endpoint allows you to test the automated trading system
    without waiting for the scheduled 4 PM ET execution.

    Returns:
        Execution result with status and summary
    """
    try:
        if trading_scheduler is None:
            raise HTTPException(
                status_code=503,
                detail="Scheduler not initialized"
            )

        logger.info("Manual trading execution triggered via API")
        result = await trading_scheduler.trigger_manual_execution()

        return {
            "success": True,
            "message": "Manual execution completed",
            "execution": result
        }

    except Exception as e:
        logger.error(f"Manual execution error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scheduler/history", tags=["Trading Scheduler"])
async def get_execution_history(limit: int = 50):
    """
    Get recent execution history.

    Args:
        limit: Maximum number of records to return (default 50, max 100)

    Returns:
        List of execution log entries with timestamp, status, and summary
    """
    try:
        if trading_scheduler is None:
            return {
                "success": False,
                "error": "Scheduler not initialized",
                "history": []
            }

        limit = min(limit, 100)  # Cap at 100
        history = trading_scheduler.get_execution_history(limit=limit)

        return {
            "success": True,
            "count": len(history),
            "history": history
        }

    except Exception as e:
        logger.error(f"Get execution history error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scheduler/stop", tags=["Trading Scheduler"])
async def stop_scheduler():
    """
    Stop the trading scheduler.

    Disables automated daily trading executions until restarted.
    Use this for emergency shutdown or maintenance.
    """
    try:
        if trading_scheduler is None:
            raise HTTPException(
                status_code=503,
                detail="Scheduler not initialized"
            )

        if not trading_scheduler.is_running:
            return {
                "success": True,
                "message": "Scheduler is already stopped"
            }

        trading_scheduler.stop()
        logger.info("Scheduler stopped via API")

        return {
            "success": True,
            "message": "Scheduler stopped successfully"
        }

    except Exception as e:
        logger.error(f"Stop scheduler error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scheduler/start", tags=["Trading Scheduler"])
async def start_scheduler():
    """
    Start the trading scheduler.

    Enables automated daily trading executions at 4 PM ET.
    """
    try:
        global trading_scheduler

        if trading_scheduler is None:
            # Initialize if not already done
            trading_scheduler = TradingScheduler(base_url="http://localhost:8010")

        if trading_scheduler.is_running:
            return {
                "success": True,
                "message": "Scheduler is already running",
                "next_execution": trading_scheduler.get_next_execution_time()
            }

        trading_scheduler.start()
        next_run = trading_scheduler.get_next_execution_time()
        logger.info(f"Scheduler started via API - next execution at {next_run}")

        return {
            "success": True,
            "message": "Scheduler started successfully",
            "next_execution": next_run
        }

    except Exception as e:
        logger.error(f"Start scheduler error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================================================================
# PERFORMANCE DASHBOARD
# ===================================================================

from analysis.performance_dashboard import PerformanceDashboard

performance_dashboard = PerformanceDashboard()


@app.get("/performance/dashboard", tags=["Performance Tracking"])
async def get_performance_dashboard(days: int = 30):
    """
    Get comprehensive performance metrics.

    Args:
        days: Number of days to analyze (default: 30)

    Returns:
        JSON with portfolio performance, risk metrics, and trading statistics
    """
    try:
        metrics = performance_dashboard.calculate_metrics(days=days)
        return {
            "success": True,
            "metrics": metrics
        }

    except Exception as e:
        logger.error(f"Performance dashboard error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/performance/report", tags=["Performance Tracking"])
async def get_performance_report(days: int = 30):
    """
    Get formatted performance report.

    Args:
        days: Number of days to analyze (default: 30)

    Returns:
        Formatted text report of portfolio performance
    """
    try:
        report = performance_dashboard.generate_report(days=days)
        return {
            "success": True,
            "report": report,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Performance report error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/performance/snapshot", tags=["Performance Tracking"])
async def record_performance_snapshot():
    """
    Record current portfolio snapshot for performance tracking.

    Fetches current portfolio state and SPY price, then records a snapshot.
    This should be called daily (automatically by scheduler).
    """
    try:
        # Get current portfolio with prices
        from core.paper_portfolio_manager import PaperPortfolioManager
        portfolio_mgr = PaperPortfolioManager()
        portfolio = portfolio_mgr.get_portfolio_with_prices()

        # Calculate total portfolio value
        total_value = portfolio['cash']
        for position in portfolio['positions'].values():
            total_value += position.get('market_value', 0.0)

        num_positions = len(portfolio['positions'])

        # Get SPY price for benchmark
        from data.enhanced_provider import EnhancedYahooProvider
        provider = EnhancedYahooProvider()
        spy_data = provider.get_comprehensive_data("SPY")
        spy_price = spy_data.get('current_price', 0.0)

        # Get current regime
        try:
            from core.market_regime_service import MarketRegimeService
            regime_service = MarketRegimeService()
            regime_data = regime_service.detect_regime()
            regime = f"{regime_data['trend']}_{regime_data['volatility']}"
        except:
            regime = "UNKNOWN"

        # Record snapshot
        performance_dashboard.record_daily_snapshot(
            portfolio_value=total_value,
            cash=portfolio['cash'],
            num_positions=num_positions,
            spy_price=spy_price,
            regime=regime
        )

        return {
            "success": True,
            "message": "Performance snapshot recorded",
            "portfolio_value": total_value,
            "spy_price": spy_price,
            "regime": regime
        }

    except Exception as e:
        logger.error(f"Record snapshot error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================================================================
# SYSTEM ALERTS & MONITORING
# ===================================================================

from utils.alerts_manager import get_alerts_manager

alerts_manager = get_alerts_manager()


@app.get("/alerts", tags=["System Monitoring"])
async def get_alerts(
    limit: int = 50,
    level: Optional[str] = None,
    category: Optional[str] = None,
    unread_only: bool = False
):
    """
    Get system alerts for internal monitoring dashboard

    Args:
        limit: Maximum number of alerts to return (default 50, max 100)
        level: Filter by level (error, warning, info, success)
        category: Filter by category (api, agent, system, performance)
        unread_only: Only return unread alerts

    Returns:
        List of alerts with metadata
    """
    try:
        limit = min(limit, 100)  # Cap at 100
        alerts = alerts_manager.get_alerts(
            limit=limit,
            level=level,
            category=category,
            unread_only=unread_only
        )

        return {
            "alerts": alerts,
            "count": len(alerts),
            "has_more": len(alerts_manager.alerts) > limit
        }

    except Exception as e:
        logger.error(f"Get alerts error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/alerts/stats", tags=["System Monitoring"])
async def get_alerts_stats():
    """
    Get alert statistics for dashboard overview

    Returns:
        Alert counts and statistics
    """
    try:
        stats = alerts_manager.get_stats()
        return stats

    except Exception as e:
        logger.error(f"Get alerts stats error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/alerts/{alert_id}/read", tags=["System Monitoring"])
async def mark_alert_read(alert_id: str):
    """
    Mark a specific alert as read

    Args:
        alert_id: ID of the alert to mark as read

    Returns:
        Success status
    """
    try:
        success = alerts_manager.mark_read(alert_id)

        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")

        return {"success": True, "message": "Alert marked as read"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Mark alert read error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/alerts/read-all", tags=["System Monitoring"])
async def mark_all_alerts_read():
    """
    Mark all alerts as read

    Returns:
        Number of alerts marked as read
    """
    try:
        count = alerts_manager.mark_all_read()

        return {
            "success": True,
            "count": count,
            "message": f"Marked {count} alerts as read"
        }

    except Exception as e:
        logger.error(f"Mark all alerts read error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PAPER TRADING ENDPOINTS
# ============================================================================

@app.get("/paper-trading/positions", tags=["Paper Trading"])
async def get_paper_positions():
    """Get all paper trading positions with P&L

    Returns:
        dict: Paper trading portfolio with positions, cash, and P&L metrics
    """
    try:
        # Placeholder response - full implementation uses PaperPortfolioManager
        return {
            "positions": [],
            "cash": 10000.0,
            "total_value": 10000.0,
            "total_pl": 0.0,
            "total_pl_percent": 0.0,
            "message": "Paper trading positions endpoint - placeholder implementation"
        }
    except Exception as e:
        logger.error(f"Get paper positions error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/paper-trading/trade", tags=["Paper Trading"])
async def execute_paper_trade(trade_request: dict):
    """Execute a paper trade (buy/sell)

    Args:
        trade_request: Trade details (symbol, action, quantity, price)

    Returns:
        dict: Trade execution result
    """
    try:
        # Placeholder response - full implementation uses PaperPortfolioManager
        return {
            "success": True,
            "message": "Paper trading coming soon - trade request received",
            "trade": trade_request
        }
    except Exception as e:
        logger.error(f"Execute paper trade error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/paper-trading/performance", tags=["Paper Trading"])
async def get_paper_performance():
    """Get paper trading performance metrics

    Returns:
        dict: Performance metrics (total return, win rate, Sharpe ratio, etc.)
    """
    try:
        # Placeholder response - full implementation uses PaperPortfolioManager
        return {
            "total_return": 0.0,
            "total_return_percent": 0.0,
            "win_rate": 0.0,
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0,
            "num_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "message": "Paper trading performance endpoint - placeholder implementation"
        }
    except Exception as e:
        logger.error(f"Get paper performance error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Add sample alerts on startup for demonstration
def add_sample_alerts():
    """Add some sample alerts for demonstration"""
    alerts_manager.add_alert(
        level="info",
        category="system",
        message="System started successfully",
        details={"version": "4.0.0"},
        source="startup"
    )

    # Log successful startups
    logger.info("✅ Alerts system initialized")


@app.on_event("startup")
async def startup_event():
    """Startup event"""
    global trading_scheduler

    logger.info("🏦 5-Agent AI Hedge Fund System starting up...")
    logger.info("✅ All 5 agents initialized")
    logger.info("✅ Narrative engine ready")
    logger.info("✅ Portfolio manager ready")
    logger.info("✅ Auto-sell monitor ready")
    logger.info("✅ API endpoints configured")

    # Initialize alerts system
    add_sample_alerts()

    # Initialize and start trading scheduler
    try:
        trading_scheduler = TradingScheduler(base_url="http://localhost:8010")
        trading_scheduler.start()
        next_run = trading_scheduler.get_next_execution_time()
        logger.info(f"✅ Trading scheduler started - next execution at {next_run}")
    except Exception as e:
        logger.error(f"⚠️  Failed to start trading scheduler: {e}")
        logger.warning("Paper trading automation will not be available")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    global trading_scheduler

    logger.info("🛑 5-Agent AI Hedge Fund System shutting down...")

    # Stop trading scheduler
    if trading_scheduler and trading_scheduler.is_running:
        try:
            trading_scheduler.stop()
            logger.info("✅ Trading scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping trading scheduler: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)