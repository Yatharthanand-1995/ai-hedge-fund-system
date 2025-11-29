"""
Enhanced Yahoo Finance Data Provider
Comprehensive stock data collection with technical indicators
"""

import yfinance as yf
import pandas as pd
import numpy as np
import talib
from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_extract_value(data, column, index=-1, default=0):
    """Safely extract value from pandas data, handling numpy arrays properly"""
    try:
        if data.empty:
            return default

        value = data[column].iloc[index]

        # Handle numpy arrays or Series
        if isinstance(value, (np.ndarray, pd.Series)):
            if len(value) == 1:
                value = value.iloc[0] if hasattr(value, 'iloc') else value[0]
            else:
                logger.warning(f"Unexpected array size: {len(value)}, taking first value")
                value = value.iloc[0] if hasattr(value, 'iloc') else value[0]

        # Convert to appropriate type
        if pd.isna(value):
            return default
        return float(value) if isinstance(default, float) else int(value)
    except Exception as e:
        logger.error(f"Error extracting {column} from data: {e}")
        return default

class EnhancedYahooProvider:
    """Enhanced data provider for comprehensive stock analysis using Yahoo Finance"""

    def __init__(self, rate_limit_delay: float = 0.5):
        self.rate_limit_delay = rate_limit_delay
        self.cache = {}
        self.cache_expiry = {}
        self.cache_duration = 1200  # 20 minutes cache (extended for 50-stock universe)

    def get_comprehensive_data(self, symbol: str) -> Dict:
        """Get comprehensive stock data including all technical indicators"""

        # Check cache first
        if self._is_cached_data_fresh(symbol):
            logger.info(f"Using cached data for {symbol}")
            return self.cache[symbol]

        try:
            logger.info(f"Fetching fresh data for {symbol}")

            # Get stock data
            ticker = yf.Ticker(symbol)

            # Get historical data (2 years for momentum + technical indicators)
            hist = ticker.history(period="2y", interval="1d")
            if hist.empty:
                logger.warning(f"No historical data found for {symbol}")
                return self._create_empty_data(symbol)

            # Get stock info
            info = ticker.info

            # Calculate all technical indicators
            technical_data = self._calculate_all_indicators(hist)

            # Get current price data
            current_data = self._get_current_price_data(hist, info)

            # Get financials data for Quality Agent
            financials = ticker.financials
            quarterly_financials = ticker.quarterly_financials

            # Combine all data
            comprehensive_data = {
                **current_data,
                **technical_data,
                'symbol': symbol,
                'company_name': info.get('longName', symbol),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'market_cap': info.get('marketCap', 0),
                'timestamp': datetime.now().isoformat(),
                'historical_data': hist,  # Include historical OHLCV data for signal engine
                'technical_data': technical_data,  # Also include as separate key for institutional flow agent
                'info': info,  # Full company info for Quality Agent
                'financials': financials,  # Financial statements for Quality Agent
                'quarterly_financials': quarterly_financials  # Quarterly financials for Quality Agent
            }

            # Cache the data
            self.cache[symbol] = comprehensive_data
            self.cache_expiry[symbol] = datetime.now() + timedelta(seconds=self.cache_duration)

            # Rate limiting
            time.sleep(self.rate_limit_delay)

            return comprehensive_data

        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return self._create_error_data(symbol, str(e))

    def get_batch_data(self, symbols: List[str]) -> List[Dict]:
        """Get comprehensive data for multiple symbols"""
        results = []

        for symbol in symbols:
            data = self.get_comprehensive_data(symbol)
            results.append(data)

        return results

    def _get_current_price_data(self, hist: pd.DataFrame, info: Dict) -> Dict:
        """Extract current price and volume data"""

        if hist.empty:
            return {}

        current_close = safe_extract_value(hist, 'Close', -1, 0.0)
        previous_close = safe_extract_value(hist, 'Close', -2, current_close) if len(hist) > 1 else current_close
        current_volume = safe_extract_value(hist, 'Volume', -1, 0)
        avg_volume = hist['Volume'].mean()

        price_change = current_close - previous_close
        price_change_percent = (price_change / previous_close) * 100 if previous_close != 0 else 0

        return {
            'current_price': round(current_close, 2),
            'previous_close': round(previous_close, 2),
            'price_change': round(price_change, 2),
            'price_change_percent': round(price_change_percent, 2),
            'day_high': round(safe_extract_value(hist, 'High', -1, 0.0), 2),
            'day_low': round(safe_extract_value(hist, 'Low', -1, 0.0), 2),
            'current_volume': int(current_volume),
            'avg_volume': int(avg_volume),
            'volume_ratio': round(current_volume / avg_volume, 2) if avg_volume > 0 else 0,
            'open_price': round(safe_extract_value(hist, 'Open', -1, 0.0), 2)
        }

    def _calculate_all_indicators(self, hist: pd.DataFrame) -> Dict:
        """Calculate comprehensive technical indicators"""

        if len(hist) < 14:  # Need sufficient data for indicators
            logger.warning(f"Insufficient data for indicators: {len(hist)} days")
            return self._create_empty_indicators()

        try:
            # Price data - convert to float64 for TA-Lib
            close = hist['Close'].values.astype(np.float64)
            high = hist['High'].values.astype(np.float64)
            low = hist['Low'].values.astype(np.float64)
            volume = hist['Volume'].values.astype(np.float64)
            open_prices = hist['Open'].values.astype(np.float64)

            # Momentum Indicators
            rsi = talib.RSI(close, timeperiod=14)
            stoch_k, stoch_d = talib.STOCH(high, low, close,
                                         fastk_period=14, slowk_period=3, slowd_period=3)
            williams_r = talib.WILLR(high, low, close, timeperiod=14)
            cci = talib.CCI(high, low, close, timeperiod=14)

            # Trend Indicators
            sma_20 = talib.SMA(close, timeperiod=20)
            ema_12 = talib.EMA(close, timeperiod=12)
            ema_26 = talib.EMA(close, timeperiod=26)
            adx = talib.ADX(high, low, close, timeperiod=14)

            # MACD
            macd, macd_signal, macd_histogram = talib.MACD(close,
                                                          fastperiod=12,
                                                          slowperiod=26,
                                                          signalperiod=9)

            # Bollinger Bands
            bb_upper, bb_middle, bb_lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2)

            # Volatility Indicators
            atr = talib.ATR(high, low, close, timeperiod=14)

            # Volume Indicators
            obv = talib.OBV(close, volume)
            ad = talib.AD(high, low, close, volume)
            mfi = talib.MFI(high, low, close, volume, timeperiod=14)

            # Chaikin Money Flow (CMF) - Institutional flow indicator
            cmf = talib.ADOSC(high, low, close, volume, fastperiod=3, slowperiod=10)

            # VWAP (Volume Weighted Average Price) - Custom calculation
            vwap = self._calculate_vwap(high, low, close, volume)

            # Volume Z-score - Detects unusual institutional activity
            volume_zscore = self._calculate_volume_zscore(volume)

            # Additional Momentum Indicators
            roc = talib.ROC(close, timeperiod=10)  # Rate of Change
            mom = talib.MOM(close, timeperiod=10)  # Momentum
            trix = talib.TRIX(close, timeperiod=14)  # Triple Exponential Moving Average

            # Volatility Indicators
            natr = talib.NATR(high, low, close, timeperiod=14)  # Normalized ATR
            trange = talib.TRANGE(high, low, close)  # True Range

            # Trend Indicators
            aroon_down, aroon_up = talib.AROON(high, low, timeperiod=14)
            aroonosc = talib.AROONOSC(high, low, timeperiod=14)
            ppo = talib.PPO(close)  # Percentage Price Oscillator

            # Overlap Studies
            dema = talib.DEMA(close, timeperiod=30)  # Double Exponential Moving Average
            tema = talib.TEMA(close, timeperiod=30)  # Triple Exponential Moving Average
            kama = talib.KAMA(close, timeperiod=30)  # Kaufman Adaptive Moving Average

            # Advanced Oscillators
            ultimate_osc = talib.ULTOSC(high, low, close)  # Ultimate Oscillator

            # Pattern Recognition (Extended)
            doji = talib.CDLDOJI(open_prices, high, low, close)
            hammer = talib.CDLHAMMER(open_prices, high, low, close)
            shooting_star = talib.CDLSHOOTINGSTAR(open_prices, high, low, close)
            engulfing = talib.CDLENGULFING(open_prices, high, low, close)
            harami = talib.CDLHARAMI(open_prices, high, low, close)
            morning_star = talib.CDLMORNINGSTAR(open_prices, high, low, close)
            evening_star = talib.CDLEVENINGSTAR(open_prices, high, low, close)
            spinning_top = talib.CDLSPINNINGTOP(open_prices, high, low, close)

            # Calculate derived metrics
            current_price = close[-1]
            bb_position = self._calculate_bb_position(current_price, bb_upper[-1], bb_lower[-1])
            trend_strength = self._calculate_trend_strength(sma_20[-1], ema_12[-1], ema_26[-1], current_price)
            momentum_score = self._calculate_momentum_score(rsi[-1], stoch_k[-1], williams_r[-1])

            return {
                # Momentum Indicators
                'rsi': round(rsi[-1], 2) if not np.isnan(rsi[-1]) else None,
                'stoch_k': round(stoch_k[-1], 2) if not np.isnan(stoch_k[-1]) else None,
                'stoch_d': round(stoch_d[-1], 2) if not np.isnan(stoch_d[-1]) else None,
                'williams_r': round(williams_r[-1], 2) if not np.isnan(williams_r[-1]) else None,
                'cci': round(cci[-1], 2) if not np.isnan(cci[-1]) else None,

                # Trend Indicators
                'sma_20': round(sma_20[-1], 2) if not np.isnan(sma_20[-1]) else None,
                'ema_12': round(ema_12[-1], 2) if not np.isnan(ema_12[-1]) else None,
                'ema_26': round(ema_26[-1], 2) if not np.isnan(ema_26[-1]) else None,
                'adx': round(adx[-1], 2) if not np.isnan(adx[-1]) else None,

                # MACD
                'macd': round(macd[-1], 4) if not np.isnan(macd[-1]) else None,
                'macd_signal': round(macd_signal[-1], 4) if not np.isnan(macd_signal[-1]) else None,
                'macd_histogram': round(macd_histogram[-1], 4) if not np.isnan(macd_histogram[-1]) else None,

                # Bollinger Bands
                'bb_upper': round(bb_upper[-1], 2) if not np.isnan(bb_upper[-1]) else None,
                'bb_middle': round(bb_middle[-1], 2) if not np.isnan(bb_middle[-1]) else None,
                'bb_lower': round(bb_lower[-1], 2) if not np.isnan(bb_lower[-1]) else None,
                'bb_position': bb_position,

                # Volatility
                'atr': round(atr[-1], 2) if not np.isnan(atr[-1]) else None,

                # Volume
                'obv': obv,  # Return full array for trend analysis
                'ad': ad,    # Return full array for trend analysis
                'mfi': mfi,  # Return full array for trend analysis
                'cmf': cmf,  # Chaikin Money Flow (institutional indicator)
                'vwap': vwap,  # Volume Weighted Average Price
                'volume_zscore': volume_zscore,  # Volume spike detection

                # Additional Momentum
                'roc': round(roc[-1], 2) if not np.isnan(roc[-1]) else None,
                'mom': round(mom[-1], 2) if not np.isnan(mom[-1]) else None,
                'trix': round(trix[-1], 4) if not np.isnan(trix[-1]) else None,

                # Advanced Volatility
                'natr': round(natr[-1], 2) if not np.isnan(natr[-1]) else None,
                'trange': round(trange[-1], 2) if not np.isnan(trange[-1]) else None,

                # Trend Analysis
                'aroon_up': round(aroon_up[-1], 2) if not np.isnan(aroon_up[-1]) else None,
                'aroon_down': round(aroon_down[-1], 2) if not np.isnan(aroon_down[-1]) else None,
                'aroonosc': round(aroonosc[-1], 2) if not np.isnan(aroonosc[-1]) else None,
                'ppo': round(ppo[-1], 4) if not np.isnan(ppo[-1]) else None,

                # Advanced Moving Averages
                'dema': round(dema[-1], 2) if not np.isnan(dema[-1]) else None,
                'tema': round(tema[-1], 2) if not np.isnan(tema[-1]) else None,
                'kama': round(kama[-1], 2) if not np.isnan(kama[-1]) else None,

                # Advanced Oscillators
                'ultimate_osc': round(ultimate_osc[-1], 2) if not np.isnan(ultimate_osc[-1]) else None,

                # Patterns (last 3 days)
                'doji_pattern': int(doji[-3:].sum()) if len(doji) >= 3 else 0,
                'hammer_pattern': int(hammer[-3:].sum()) if len(hammer) >= 3 else 0,
                'shooting_star_pattern': int(shooting_star[-3:].sum()) if len(shooting_star) >= 3 else 0,
                'engulfing_pattern': int(engulfing[-3:].sum()) if len(engulfing) >= 3 else 0,
                'harami_pattern': int(harami[-3:].sum()) if len(harami) >= 3 else 0,
                'morning_star_pattern': int(morning_star[-3:].sum()) if len(morning_star) >= 3 else 0,
                'evening_star_pattern': int(evening_star[-3:].sum()) if len(evening_star) >= 3 else 0,
                'spinning_top_pattern': int(spinning_top[-3:].sum()) if len(spinning_top) >= 3 else 0,

                # Derived Metrics
                'trend_strength': trend_strength,
                'momentum_score': momentum_score,
                'volatility_rank': self._calculate_volatility_rank(atr[-1], close)
            }

        except Exception as e:
            logger.error(f"Error calculating indicators: {str(e)}")
            return self._create_empty_indicators()

    def _calculate_bb_position(self, price: float, bb_upper: float, bb_lower: float) -> str:
        """Calculate Bollinger Band position"""
        if np.isnan(bb_upper) or np.isnan(bb_lower):
            return "Unknown"

        if price > bb_upper:
            return "Above Upper"
        elif price < bb_lower:
            return "Below Lower"
        else:
            position = (price - bb_lower) / (bb_upper - bb_lower) * 100
            return f"{position:.1f}%"

    def _calculate_trend_strength(self, sma_20: float, ema_12: float, ema_26: float, price: float) -> str:
        """Calculate trend strength based on moving averages"""
        if any(np.isnan(x) for x in [sma_20, ema_12, ema_26]):
            return "Unknown"

        if price > ema_12 > ema_26 > sma_20:
            return "Strong Bullish"
        elif price > ema_12 > sma_20:
            return "Bullish"
        elif price < ema_12 < ema_26 < sma_20:
            return "Strong Bearish"
        elif price < ema_12 < sma_20:
            return "Bearish"
        else:
            return "Neutral"

    def _calculate_momentum_score(self, rsi: float, stoch_k: float, williams_r: float) -> int:
        """Calculate momentum score 0-100"""
        scores = []

        # RSI score
        if not np.isnan(rsi):
            if rsi > 70:
                scores.append(20)  # Overbought
            elif rsi > 50:
                scores.append(60 + (rsi - 50) * 2)
            elif rsi < 30:
                scores.append(20)  # Oversold
            else:
                scores.append(40 - (50 - rsi) * 2)

        # Stochastic score
        if not np.isnan(stoch_k):
            if stoch_k > 80:
                scores.append(20)
            elif stoch_k > 50:
                scores.append(60 + (stoch_k - 50))
            elif stoch_k < 20:
                scores.append(20)
            else:
                scores.append(40 - (50 - stoch_k))

        # Williams %R score
        if not np.isnan(williams_r):
            williams_normalized = 100 + williams_r  # Convert from -100-0 to 0-100
            if williams_normalized > 80:
                scores.append(20)
            elif williams_normalized > 50:
                scores.append(60 + (williams_normalized - 50))
            elif williams_normalized < 20:
                scores.append(20)
            else:
                scores.append(40 - (50 - williams_normalized))

        return int(np.mean(scores)) if scores else 50

    def _calculate_volatility_rank(self, atr: float, close_prices: np.ndarray) -> str:
        """Calculate volatility rank"""
        if np.isnan(atr) or len(close_prices) == 0:
            return "Unknown"

        avg_price = np.mean(close_prices[-20:])  # Last 20 days average
        volatility_percent = (atr / avg_price) * 100

        if volatility_percent < 1:
            return "Low"
        elif volatility_percent < 2:
            return "Medium"
        elif volatility_percent < 4:
            return "High"
        else:
            return "Very High"

    def _calculate_vwap(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, volume: np.ndarray) -> np.ndarray:
        """
        Calculate Volume Weighted Average Price (VWAP)

        VWAP is the average price weighted by volume - used by institutional traders
        as a benchmark for execution quality.

        Returns:
            numpy array of VWAP values
        """
        try:
            # Typical price (average of high, low, close)
            typical_price = (high + low + close) / 3.0

            # Calculate cumulative volume-weighted price
            # Use rolling window to avoid cumulative sum getting too large
            window = min(60, len(volume))  # 60-day rolling VWAP

            vwap = np.zeros_like(close)
            for i in range(len(close)):
                start_idx = max(0, i - window + 1)
                volume_slice = volume[start_idx:i+1]
                price_slice = typical_price[start_idx:i+1]

                total_volume = np.sum(volume_slice)
                if total_volume > 0:
                    vwap[i] = np.sum(price_slice * volume_slice) / total_volume
                else:
                    vwap[i] = close[i]

            return vwap

        except Exception as e:
            logger.warning(f"VWAP calculation failed: {e}")
            # Return close prices as fallback
            return close.copy()

    def _calculate_volume_zscore(self, volume: np.ndarray, window: int = 20) -> np.ndarray:
        """
        Calculate Z-score of volume to detect unusual activity

        Z-score > 2 indicates volume spike (potential institutional activity)
        Z-score > 3 indicates extreme volume spike

        Args:
            volume: Volume array
            window: Rolling window for mean/std calculation (default 20 days)

        Returns:
            numpy array of volume Z-scores
        """
        try:
            zscore = np.zeros_like(volume, dtype=float)

            for i in range(len(volume)):
                if i < window:
                    # Not enough data for Z-score
                    zscore[i] = 0.0
                else:
                    # Calculate rolling mean and std
                    volume_window = volume[i-window:i]
                    mean_vol = np.mean(volume_window)
                    std_vol = np.std(volume_window)

                    if std_vol > 0:
                        zscore[i] = (volume[i] - mean_vol) / std_vol
                    else:
                        zscore[i] = 0.0

            return zscore

        except Exception as e:
            logger.warning(f"Volume Z-score calculation failed: {e}")
            return np.zeros_like(volume, dtype=float)

    def _is_cached_data_fresh(self, symbol: str) -> bool:
        """Check if cached data is still fresh"""
        if symbol not in self.cache or symbol not in self.cache_expiry:
            return False
        return datetime.now() < self.cache_expiry[symbol]

    def _create_empty_data(self, symbol: str) -> Dict:
        """Create empty data structure for missing data"""
        return {
            'symbol': symbol,
            'error': 'No data available',
            'timestamp': datetime.now().isoformat()
        }

    def _create_error_data(self, symbol: str, error_msg: str) -> Dict:
        """Create error data structure"""
        return {
            'symbol': symbol,
            'error': error_msg,
            'timestamp': datetime.now().isoformat()
        }

    def _create_empty_indicators(self) -> Dict:
        """Create empty indicators structure"""
        return {
            'rsi': None,
            'stoch_k': None,
            'stoch_d': None,
            'williams_r': None,
            'cci': None,
            'sma_20': None,
            'ema_12': None,
            'ema_26': None,
            'adx': None,
            'macd': None,
            'macd_signal': None,
            'macd_histogram': None,
            'bb_upper': None,
            'bb_middle': None,
            'bb_lower': None,
            'bb_position': "Unknown",
            'atr': None,
            'obv': None,
            'ad': None,
            'doji_pattern': 0,
            'hammer_pattern': 0,
            'shooting_star_pattern': 0,
            'trend_strength': "Unknown",
            'momentum_score': 50,
            'volatility_rank': "Unknown"
        }

    def get_data(self, symbol: str, period: str = '3mo') -> pd.DataFrame:
        """
        Get OHLCV data as clean DataFrame without MultiIndex

        Args:
            symbol: Stock symbol
            period: Time period (e.g., '3mo', '1y')

        Returns:
            DataFrame with OHLCV data with flat column index
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval='1d')

            if data.empty:
                logger.warning(f"No data found for {symbol}")
                return pd.DataFrame()

            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.droplevel(1)

            return data

        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return pd.DataFrame()

# Singleton instance
enhanced_provider = EnhancedYahooProvider()