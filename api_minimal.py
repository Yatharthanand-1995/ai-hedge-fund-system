"""
Minimal FastAPI backend for Stock Analysis Demo
Only exposes endpoints needed for Vercel deployment
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional
from pydantic import BaseModel
import json
import logging
import os
import numpy as np
import pandas as pd
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import core components
from narrative_engine.narrative_engine import InvestmentNarrativeEngine
from core.stock_scorer import StockScorer
from data.enhanced_provider import EnhancedYahooProvider
from data.us_top_100_stocks import US_TOP_100_STOCKS, SECTOR_MAPPING
from core.market_regime_service import MarketRegimeService

# Custom JSON Encoder for numpy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.DataFrame):
            return obj.to_dict('records')
        return super().default(obj)

def sanitize_float(value):
    """Convert numpy/inf/nan to safe float"""
    if pd.isna(value) or value == float('inf') or value == float('-inf'):
        return 0.0
    if isinstance(value, (np.integer, np.int64)):
        return int(value)
    if isinstance(value, (np.floating, np.float64)):
        return float(value)
    return value

def sanitize_dict(d):
    """Recursively sanitize dictionary values"""
    if isinstance(d, dict):
        return {k: sanitize_dict(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [sanitize_dict(item) for item in d]
    else:
        return sanitize_float(d)

# Initialize FastAPI
app = FastAPI(
    title="AI Stock Analysis - Minimal API",
    description="Minimal backend for Vercel Stock Analysis demo",
    version="1.0.0"
)

# CORS - Allow Vercel and localhost
ALLOWED_ORIGINS = os.getenv(
    'ALLOWED_ORIGINS',
    'http://localhost:5173,http://localhost:5174,https://*.vercel.app'
).split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Simplified for demo - allows all origins
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize components
logger.info("Initializing AI components...")
data_provider = EnhancedYahooProvider()
stock_scorer = StockScorer(sector_mapping=SECTOR_MAPPING)
narrative_engine = InvestmentNarrativeEngine()
regime_service = MarketRegimeService()

logger.info("✅ All components initialized")

# Pydantic models
class TopPickResponse(BaseModel):
    top_picks: List[Dict]
    total_analyzed: int
    selection_criteria: str
    timestamp: str

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AI Stock Analysis - Minimal API",
        "status": "running",
        "endpoints": ["/health", "/portfolio/top-picks", "/market/regime"],
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Quick test with a simple stock
        test_symbol = "AAPL"
        test_data = data_provider.get_comprehensive_data(test_symbol)

        return {
            "status": "healthy",
            "agents": {
                "fundamentals": "operational",
                "momentum": "operational",
                "quality": "operational",
                "sentiment": "operational",
                "institutional_flow": "operational"
            },
            "data_provider": "operational",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.get("/portfolio/top-picks")
async def get_top_picks(limit: int = 50):
    """Get top stock picks with full analysis"""
    try:
        logger.info(f"Analyzing top {limit} stocks from universe of {len(US_TOP_100_STOCKS)}")

        # Get stock universe
        universe = US_TOP_100_STOCKS[:limit] if limit < len(US_TOP_100_STOCKS) else US_TOP_100_STOCKS

        # Analyze all stocks
        analyses = []
        for symbol in universe:
            try:
                # Get comprehensive data
                data = data_provider.get_comprehensive_data(symbol)

                # Analyze with stock scorer
                score_result = stock_scorer.score_stock(symbol, data)

                if score_result:
                    composite_score = score_result.get('composite_score', 0)
                    agent_scores = score_result.get('agent_scores', {})

                    # Generate narrative
                    narrative = narrative_engine.generate_narrative(
                        symbol=symbol,
                        agent_scores=agent_scores,
                        composite_score=composite_score,
                        cached_data=data
                    )

                    # Build response
                    analysis = {
                        'symbol': symbol,
                        'company_name': symbol,
                        'sector': SECTOR_MAPPING.get(symbol, 'Unknown'),
                        'overall_score': sanitize_float(composite_score),
                        'recommendation': narrative.get('recommendation', 'HOLD'),
                        'confidence_level': narrative.get('confidence_level', 'MEDIUM'),
                        'investment_thesis': narrative.get('investment_thesis', ''),
                        'key_strengths': narrative.get('key_strengths', []),
                        'key_risks': narrative.get('key_risks', []),
                        'agent_scores': sanitize_dict(agent_scores),
                        'market_data': sanitize_dict({
                            'current_price': data.get('current_price', 0),
                            'previous_close': data.get('previous_close', 0),
                            'price_change': data.get('price_change', 0),
                            'price_change_percent': data.get('price_change_percent', 0),
                            'volume': data.get('volume', 0),
                            'market_cap': data.get('market_cap', 0)
                        })
                    }

                    analyses.append(analysis)

            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
                continue

        # Sort by score
        analyses.sort(key=lambda x: x['overall_score'], reverse=True)

        # Calculate weights
        total_score = sum(a['overall_score'] for a in analyses)
        for analysis in analyses:
            analysis['weight'] = sanitize_float(
                (analysis['overall_score'] / total_score * 100) if total_score > 0 else 0
            )

        logger.info(f"Successfully analyzed {len(analyses)} stocks")

        return JSONResponse(
            content={
                'top_picks': analyses,
                'total_analyzed': len(analyses),
                'selection_criteria': 'Based on 5-agent comprehensive analysis',
                'timestamp': datetime.now().isoformat()
            }
        )

    except Exception as e:
        logger.error(f"Error in get_top_picks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market/regime")
async def get_market_regime():
    """Get current market regime"""
    try:
        regime_info = regime_service.get_current_regime()
        return JSONResponse(content=sanitize_dict(regime_info))
    except Exception as e:
        logger.error(f"Error getting market regime: {e}")
        # Return default regime on error
        return JSONResponse(content={
            'trend': 'SIDEWAYS',
            'volatility': 'NORMAL_VOL',
            'regime': 'SIDEWAYS_NORMAL',
            'confidence': 0.5,
            'timestamp': datetime.now().isoformat()
        })

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
