"""
Stock Picker REST API with Real-time Data
FastAPI service for stock picks and scores with WebSocket support
"""

import sys
import os
# Add the root project directory to path (going up from src/api/ to project root)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import logging
from datetime import datetime
import yfinance as yf
import pandas as pd
import numpy as np
import socketio
import asyncio

from stock_picker.portfolio_manager import PortfolioManager
from stock_picker.stock_scorer import StockScorer
from stock_picker.narrative_engine import InvestmentNarrativeEngine
from src.data.us_top_100_stocks import US_TOP_100_STOCKS, SECTOR_MAPPING
from src.data.realtime_provider import realtime_provider, MarketHours
from src.cache.stock_cache import stock_cache
from src.data.enhanced_provider import enhanced_provider
from src.core.proven_signal_engine import ProvenSignalEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Socket.IO server
sio = socketio.AsyncServer(
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=True
)

app = FastAPI(
    title="Stock Picker API with Real-time Data",
    description="Multi-agent stock picking and scoring system with live prices",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Socket.IO app
socket_app = socketio.ASGIApp(sio, app)

def create_symbol_to_sector_map():
    symbol_to_sector = {}
    for sector, symbols in SECTOR_MAPPING.items():
        for symbol in symbols:
            symbol_to_sector[symbol] = sector
    return symbol_to_sector

SYMBOL_TO_SECTOR = create_symbol_to_sector_map()
pm = PortfolioManager(sector_mapping=SYMBOL_TO_SECTOR, max_sector_weight=0.30)
scorer = StockScorer(sector_mapping=SYMBOL_TO_SECTOR)
narrative_engine = InvestmentNarrativeEngine()

# Initialize the proven signal engine for better scoring
from config.clean_signal_config import CleanSignalConfig
signal_engine = ProvenSignalEngine(
    config=CleanSignalConfig.get_config('PROVEN_SIMPLE')
)

# Using sophisticated stock_cache from src.cache.stock_cache module

# Initialize real-time data provider
from src.data.realtime_provider import realtime_provider
realtime_provider.start()

def convert_numpy_types(obj: Any) -> Any:
    """Convert numpy types to native Python types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif pd.isna(obj):
        return None
    return obj

def _get_enhanced_stock_data(symbol: str) -> Dict:
    """Get comprehensive stock data using enhanced provider"""

    try:
        # Use the enhanced provider to get comprehensive data
        comprehensive_data = enhanced_provider.get_comprehensive_data(symbol)

        if not comprehensive_data or 'error' in comprehensive_data:
            logger.warning(f"Enhanced provider returned error for {symbol}: {comprehensive_data.get('error', 'Unknown error')}")
            return {}

        # Transform the enhanced provider data to match API format
        enhanced_data = {
            'company_name': comprehensive_data.get('company_name', symbol),
            'metrics': {
                'current_price': comprehensive_data.get('current_price', 0),
                'price_change_1d': comprehensive_data.get('price_change_percent', 0),
                'pe_ratio': comprehensive_data.get('pe_ratio', 25.0),
                'beta': comprehensive_data.get('beta', 1.0),
                'volatility_30d': comprehensive_data.get('volatility_30d', 20.0),
                'rsi': comprehensive_data.get('rsi'),
                'macd': comprehensive_data.get('macd'),
                'market_cap': comprehensive_data.get('market_cap', 0),
                'moving_avg_50': comprehensive_data.get('sma_20'),  # Use SMA 20 as approximation
                'moving_avg_200': comprehensive_data.get('ema_26'),  # Use EMA 26 as approximation
            },
            'live_data': {
                'price': comprehensive_data.get('current_price', 0),
                'previous_close': comprehensive_data.get('previous_close', 0),
                'change': comprehensive_data.get('price_change', 0),
                'change_pct': comprehensive_data.get('price_change_percent', 0),
                'volume': comprehensive_data.get('current_volume', 0),
                'high': comprehensive_data.get('day_high', 0),
                'low': comprehensive_data.get('day_low', 0),
                'last_updated': comprehensive_data.get('timestamp', datetime.now().isoformat())
            },
            'risk_metrics': {
                'sharpe_ratio': comprehensive_data.get('sharpe_ratio', 0.0),  # Use actual calculated Sharpe ratio
                'sortino_ratio': comprehensive_data.get('sortino_ratio', 0.0),  # Use actual calculated Sortino ratio
                'risk_score': comprehensive_data.get('volatility_30d', 20),
                'risk_level': _get_risk_level(comprehensive_data.get('volatility_30d', 20))
            },
            'targets': {
                'entry_price': comprehensive_data.get('current_price', 0) * 0.98,
                'stop_loss': comprehensive_data.get('current_price', 0) * 0.92,
                'take_profit': comprehensive_data.get('current_price', 0) * 1.15,
                'position_size_pct': comprehensive_data.get('position_size_pct', 5.0)  # Use calculated position size from signal engine
            }
        }

        # Convert numpy types for JSON serialization
        enhanced_data = convert_numpy_types(enhanced_data)

        return enhanced_data

    except Exception as e:
        logger.error(f"Error getting enhanced data for {symbol}: {e}")
        return {}

def _calculate_rsi(prices, period=14):
    """Calculate RSI (Relative Strength Index)"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs)).iloc[-1]

def _calculate_macd(prices, fast=12, slow=26, signal=9):
    """Calculate MACD"""
    ema_fast = prices.ewm(span=fast).mean()
    ema_slow = prices.ewm(span=slow).mean()
    macd = ema_fast - ema_slow
    return macd.iloc[-1]

def _calculate_beta(stock_prices, market_prices):
    """Calculate beta coefficient"""
    # Ensure timezone consistency
    if hasattr(stock_prices.index, 'tz') and stock_prices.index.tz is not None:
        stock_prices = stock_prices.tz_localize(None)
    if hasattr(market_prices.index, 'tz') and market_prices.index.tz is not None:
        market_prices = market_prices.tz_localize(None)

    stock_returns = stock_prices.pct_change().dropna()
    market_returns = market_prices.pct_change().dropna()

    # Align the data
    aligned_data = pd.concat([stock_returns, market_returns], axis=1).dropna()
    if len(aligned_data) < 20:  # Need minimum data points
        return None

    return aligned_data.cov().iloc[0, 1] / aligned_data.iloc[:, 1].var()

def _calculate_sharpe_ratio(returns, risk_free_rate=0.02):
    """Calculate Sharpe ratio"""
    if len(returns) == 0:
        return 0
    excess_returns = returns - risk_free_rate / 252  # Daily risk-free rate
    return excess_returns.mean() / excess_returns.std() * np.sqrt(252)

def _calculate_sortino_ratio(returns, risk_free_rate=0.02):
    """Calculate Sortino ratio"""
    if len(returns) == 0:
        return 0
    excess_returns = returns - risk_free_rate / 252
    downside_returns = returns[returns < 0]
    if len(downside_returns) == 0:
        return float('inf')
    downside_std = downside_returns.std()
    return excess_returns.mean() / downside_std * np.sqrt(252)

def _get_risk_level(volatility):
    """Determine risk level based on volatility"""
    if volatility < 15:
        return 'LOW'
    elif volatility < 25:
        return 'MODERATE'
    elif volatility < 40:
        return 'HIGH'
    else:
        return 'CRITICAL'

class PicksResponse(BaseModel):
    timestamp: str
    total_stocks: int
    avg_score: float
    avg_confidence: float
    sector_distribution: Dict[str, int]
    picks: List[Dict]

class ScoreResponse(BaseModel):
    symbol: str
    composite_score: float
    composite_confidence: float
    rank_category: str
    agent_scores: Dict
    reasoning: str

@app.get("/")
async def root():
    return {
        "service": "Stock Picker API",
        "version": "1.0.0",
        "endpoints": [
            "/picks",
            "/picks/top/{n}",
            "/scores/{symbol}",
            "/health"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/picks", response_model=PicksResponse)
async def get_top_picks(
    top_n: int = 20,
    min_score: float = 0,
    min_confidence: float = 0,
    sector_limit: bool = True
):
    try:
        # Check cache first
        cached_picks = stock_cache.get_stock_picks(
            limit=top_n,
            min_score=min_score,
            min_confidence=min_confidence,
            sector_limit=sector_limit
        )

        if cached_picks is not None:
            logger.info(f"Cache HIT for picks (limit={top_n}, min_score={min_score})")
            return PicksResponse(
                timestamp=datetime.now().isoformat(),
                total_stocks=len(cached_picks),
                avg_score=sum(pick['score'] for pick in cached_picks) / len(cached_picks) if cached_picks else 0,
                avg_confidence=sum(pick['confidence'] for pick in cached_picks) / len(cached_picks) if cached_picks else 0,
                sector_distribution={},  # Could be cached separately if needed
                picks=cached_picks
            )

        logger.info(f"Cache MISS for picks - generating fresh results (limit={top_n})")

        picks = []
        symbol_scores = []

        # Use signal engine to score stocks
        for symbol in US_TOP_100_STOCKS:
            try:
                # Get enhanced data first
                enhanced_data = _get_enhanced_stock_data(symbol)
                if not enhanced_data:
                    continue

                # Use signal engine to generate signal
                try:
                    # Extract historical OHLCV data for signal engine
                    historical_data = enhanced_data.get('historical_data')
                    if historical_data is not None and not historical_data.empty:
                        signal_result = signal_engine.generate_signal(symbol, historical_data)
                        score = signal_result.get('confidence', 0) * 100  # Convert to 0-100 scale
                        recommendation = signal_result.get('signal', 'NEUTRAL').upper()
                    else:
                        logger.warning(f"No historical data available for signal engine: {symbol}")
                        raise ValueError("No historical data")
                except Exception as e:
                    logger.warning(f"Signal engine error for {symbol}: {e}")
                    # Skip stocks where signal engine fails - no fallback scoring
                    continue

                if score < min_score:
                    continue

                symbol_scores.append((symbol, score, enhanced_data, recommendation))

            except Exception as e:
                logger.warning(f"Error processing {symbol}: {e}")
                continue

        # Sort by score and take top_n
        symbol_scores.sort(key=lambda x: x[1], reverse=True)
        top_symbols = symbol_scores[:top_n]

        for symbol, score, enhanced_data, recommendation in top_symbols:
            confidence = score / 100.0

            if confidence < min_confidence:
                continue

            pick = {
                'symbol': symbol,
                'company_name': enhanced_data.get('company_name', symbol),
                'score': score,
                'confidence': confidence,
                'recommendation': recommendation,
                'sector': SYMBOL_TO_SECTOR.get(symbol, 'Technology'),
                'price': enhanced_data.get('live_data', {}).get('price', 0),
                'change_pct': enhanced_data.get('live_data', {}).get('change_pct', 0),
                'volume': enhanced_data.get('live_data', {}).get('volume', 0),
                'metrics': convert_numpy_types(enhanced_data.get('metrics', {})),
                'live_data': convert_numpy_types(enhanced_data.get('live_data', {})),
                'risk_metrics': convert_numpy_types(enhanced_data.get('risk_metrics', {})),
                'targets': convert_numpy_types(enhanced_data.get('targets', {}))
            }

            picks.append(pick)

        # Cache the results for future requests
        stock_cache.set_stock_picks(
            picks,
            limit=top_n,
            min_score=min_score,
            min_confidence=min_confidence,
            sector_limit=sector_limit
        )

        avg_score = sum(pick['score'] for pick in picks) / len(picks) if picks else 0
        avg_confidence = sum(pick['confidence'] for pick in picks) / len(picks) if picks else 0

        # Calculate sector distribution
        sector_distribution = {}
        for pick in picks:
            sector = pick['sector']
            sector_distribution[sector] = sector_distribution.get(sector, 0) + 1

        response = PicksResponse(
            timestamp=datetime.now().isoformat(),
            total_stocks=len(picks),
            avg_score=avg_score,
            avg_confidence=avg_confidence,
            sector_distribution=sector_distribution,
            picks=picks
        )

        logger.info(f"Generated and cached {len(picks)} stock picks")
        return response

    except Exception as e:
        logger.error(f"Error in get_top_picks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/picks/top/{n}", response_model=PicksResponse)
async def get_top_n_picks(n: int, sector_limit: bool = True):
    if n < 1 or n > 100:
        raise HTTPException(status_code=400, detail="n must be between 1 and 100")

    return await get_top_picks(top_n=n, sector_limit=sector_limit)

@app.get("/cache/stats")
async def get_cache_stats():
    """Get cache performance statistics"""
    return stock_cache.get_cache_stats()

@app.post("/cache/invalidate")
async def invalidate_cache():
    """Manually invalidate all cache entries"""
    stock_cache.invalidate_all()
    return {"message": "Cache invalidated successfully"}

@app.get("/scores/{symbol}", response_model=ScoreResponse)
async def get_stock_score(symbol: str):
    symbol = symbol.upper()

    if symbol not in US_TOP_100_STOCKS:
        raise HTTPException(
            status_code=404,
            detail=f"Symbol {symbol} not in US Top 100 universe"
        )

    try:
        score_data = scorer.score_stock(symbol)

        return ScoreResponse(
            symbol=score_data['symbol'],
            composite_score=score_data['composite_score'],
            composite_confidence=score_data['composite_confidence'],
            rank_category=score_data['rank_category'],
            agent_scores=score_data['agent_scores'],
            reasoning=score_data['reasoning']
        )

    except Exception as e:
        logger.error(f"Error scoring {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/universe")
async def get_universe():
    return {
        "total_stocks": len(US_TOP_100_STOCKS),
        "symbols": US_TOP_100_STOCKS,
        "sectors": {sector: len(symbols) for sector, symbols in SECTOR_MAPPING.items()}
    }

@app.get("/sectors/{sector}")
async def get_sector_stocks(sector: str):
    sector_stocks = SECTOR_MAPPING.get(sector)
    if not sector_stocks:
        raise HTTPException(status_code=404, detail=f"Sector {sector} not found")

    return {
        "sector": sector,
        "count": len(sector_stocks),
        "symbols": sector_stocks
    }

@app.get("/api/risk/metrics")
async def get_risk_metrics():
    """API endpoint for risk metrics - placeholder implementation"""
    return {
        "portfolio_risk": {
            "var_95": 0.05,
            "var_99": 0.08,
            "expected_shortfall": 0.06,
            "beta": 1.0,
            "volatility": 0.15
        },
        "risk_breakdown": {
            "market_risk": 0.60,
            "sector_risk": 0.25,
            "stock_specific": 0.15
        },
        "last_updated": datetime.now().isoformat()
    }

@app.get("/risk/portfolio-risk")
async def get_portfolio_risk():
    """Portfolio risk assessment endpoint"""
    return {
        "overall_risk_score": 6.5,
        "risk_level": "MODERATE",
        "diversification_score": 8.2,
        "concentration_risk": 3.1,
        "sector_exposure": {
            "Technology": 0.35,
            "Healthcare": 0.20,
            "Financial": 0.25,
            "Consumer": 0.20
        },
        "recommendations": [
            "Consider reducing technology sector exposure",
            "Portfolio diversification is adequate"
        ]
    }

@app.get("/stocks/scores")
async def get_stock_scores(limit: int = 10):
    """Get stock scores with pagination"""
    try:
        # Get sample scores from our scoring system
        sample_symbols = US_TOP_100_STOCKS[:limit]
        scores = []

        for symbol in sample_symbols:
            score_data = scorer.score_stock(symbol)
            scores.append({
                "symbol": symbol,
                "score": score_data['composite_score'],
                "confidence": score_data['composite_confidence'],
                "recommendation": score_data['rank_category']
            })

        return {
            "scores": scores,
            "total": len(scores),
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error getting stock scores: {e}")
        # Return placeholder data if scoring fails
        return {
            "scores": [
                {"symbol": "AAPL", "score": 65.0, "confidence": 0.8, "recommendation": "Hold"},
                {"symbol": "MSFT", "score": 72.0, "confidence": 0.85, "recommendation": "Buy"}
            ],
            "total": 2,
            "limit": limit
        }

# WebSocket event handlers
@sio.event
async def connect(sid, environ):
    """Handle client connection"""
    logger.info(f"Client {sid} connected")
    await sio.emit('connection_status', {'status': 'connected', 'message': 'Welcome to real-time stock data'}, room=sid)

@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    logger.info(f"Client {sid} disconnected")

@sio.event
async def subscribe_symbols(sid, data):
    """Subscribe to real-time price updates for specific symbols"""
    try:
        symbols = data.get('symbols', [])
        logger.info(f"Client {sid} subscribing to symbols: {symbols}")

        # Join rooms for each symbol
        for symbol in symbols:
            await sio.enter_room(sid, f"prices_{symbol}")

            # Subscribe to real-time provider and get initial price
            def price_callback(price_data):
                asyncio.create_task(sio.emit('price_update', {
                    'symbol': price_data.symbol,
                    'data': price_data.to_dict()
                }, room=f"prices_{symbol}"))

            realtime_provider.subscribe(symbol, price_callback)

        await sio.emit('subscription_status', {
            'status': 'subscribed',
            'symbols': symbols,
            'message': f'Subscribed to {len(symbols)} symbols'
        }, room=sid)

    except Exception as e:
        logger.error(f"Error in subscribe_symbols: {e}")
        await sio.emit('error', {'message': str(e)}, room=sid)

@sio.event
async def unsubscribe_symbols(sid, data):
    """Unsubscribe from symbols"""
    try:
        symbols = data.get('symbols', [])
        logger.info(f"Client {sid} unsubscribing from symbols: {symbols}")

        for symbol in symbols:
            await sio.leave_room(sid, f"prices_{symbol}")
            realtime_provider.unsubscribe(symbol)

        await sio.emit('subscription_status', {
            'status': 'unsubscribed',
            'symbols': symbols,
            'message': f'Unsubscribed from {len(symbols)} symbols'
        }, room=sid)

    except Exception as e:
        logger.error(f"Error in unsubscribe_symbols: {e}")
        await sio.emit('error', {'message': str(e)}, room=sid)

@sio.event
async def get_market_status(sid):
    """Get current market status"""
    try:
        from src.data.realtime_provider import MarketHours
        status = MarketHours.get_market_status()
        is_open = MarketHours.is_market_open()

        await sio.emit('market_status', {
            'status': status,
            'is_open': is_open,
            'timestamp': datetime.now().isoformat()
        }, room=sid)

    except Exception as e:
        logger.error(f"Error getting market status: {e}")
        await sio.emit('error', {'message': str(e)}, room=sid)

# Additional API endpoints for real-time data
@app.get("/api/prices/{symbol}")
async def get_live_price(symbol: str):
    """Get current live price for a symbol"""
    try:
        price_data = realtime_provider.get_price(symbol.upper())
        return price_data.to_dict()
    except Exception as e:
        logger.error(f"Error getting live price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market-status")
async def get_market_status_api():
    """Get current market status via API"""
    try:
        from src.data.realtime_provider import MarketHours
        return {
            'status': MarketHours.get_market_status(),
            'is_open': MarketHours.is_market_open(),
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting market status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Investment Narrative Endpoints
@app.get("/narrative/{symbol}")
async def get_investment_narrative(symbol: str):
    """
    Get comprehensive investment narrative for a stock

    Returns human-readable investment thesis based on agent analysis
    """
    symbol = symbol.upper()

    try:
        logger.info(f"Generating investment narrative for {symbol}")

        # Get agent scores using existing scorer
        score_result = scorer.score_stock(symbol)

        # Get stock info for additional context
        ticker = yf.Ticker(symbol)
        stock_info = ticker.info

        # Generate comprehensive narrative
        narrative = narrative_engine.generate_comprehensive_thesis(
            symbol=symbol,
            agent_results=score_result.get('agent_scores', {}),
            stock_info=stock_info
        )

        return narrative

    except Exception as e:
        logger.error(f"Error generating narrative for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/narrative/picks/top/{n}")
async def get_top_picks_with_narratives(n: int):
    """
    Get top N picks with investment narratives

    Returns top performing stocks with detailed investment thesis
    """
    if n < 1 or n > 20:
        raise HTTPException(status_code=400, detail="n must be between 1 and 20")

    try:
        logger.info(f"Generating narratives for top {n} picks")

        # Get top picks using existing endpoint logic
        picks_response = await get_top_picks(top_n=n)

        narratives = []
        for pick in picks_response['picks'][:n]:
            symbol = pick['symbol']

            try:
                # Get agent scores
                score_result = scorer.score_stock(symbol)

                # Get stock info
                ticker = yf.Ticker(symbol)
                stock_info = ticker.info

                # Generate narrative
                narrative = narrative_engine.generate_comprehensive_thesis(
                    symbol=symbol,
                    agent_results=score_result.get('agent_scores', {}),
                    stock_info=stock_info
                )

                # Add market data from pick
                narrative['market_data'] = {
                    'price': pick['price'],
                    'change_pct': pick['change_pct'],
                    'volume': pick['volume'],
                    'sector': pick['sector']
                }

                narratives.append(narrative)

            except Exception as e:
                logger.warning(f"Failed to generate narrative for {symbol}: {e}")
                continue

        return {
            'timestamp': datetime.now().isoformat(),
            'total_narratives': len(narratives),
            'narratives': narratives
        }

    except Exception as e:
        logger.error(f"Error generating top picks narratives: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/narrative/summary/{symbol}")
async def get_investment_summary(symbol: str):
    """
    Get concise investment summary for quick analysis

    Returns key points and recommendation without full narrative
    """
    symbol = symbol.upper()

    try:
        # Get agent scores
        score_result = scorer.score_stock(symbol)

        # Generate full narrative
        narrative = narrative_engine.generate_comprehensive_thesis(
            symbol=symbol,
            agent_results=score_result.get('agent_scores', {}),
            stock_info=None
        )

        # Return condensed summary
        summary = {
            'symbol': symbol,
            'timestamp': narrative['timestamp'],
            'recommendation': narrative['recommendation'],
            'confidence_level': narrative['confidence_level'],
            'overall_score': narrative['overall_score'],
            'key_strengths': narrative['key_strengths'][:3],  # Top 3 strengths
            'key_risks': narrative['key_risks'][:3],  # Top 3 risks
            'quick_thesis': narrative['investment_thesis'][:300] + "..." if len(narrative['investment_thesis']) > 300 else narrative['investment_thesis']
        }

        return summary

    except Exception as e:
        logger.error(f"Error generating summary for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(socket_app, host="0.0.0.0", port=8001)