"""
Real-time Market Data Provider
Provides live stock prices and market data with multiple data sources
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timezone, timedelta
import yfinance as yf
import pandas as pd
import numpy as np
import requests
from concurrent.futures import ThreadPoolExecutor
import threading

logger = logging.getLogger(__name__)

class MarketHours:
    """Handles market hours and trading status"""

    @staticmethod
    def is_market_open() -> bool:
        """Check if US stock market is currently open"""
        now = datetime.now(timezone.utc)
        # Convert to Eastern Time
        eastern = now - timedelta(hours=5)  # Assuming EST (adjust for EDT)

        # Market is closed on weekends
        if eastern.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False

        # Regular market hours: 9:30 AM - 4:00 PM ET
        market_open = eastern.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = eastern.replace(hour=16, minute=0, second=0, microsecond=0)

        return market_open <= eastern <= market_close

    @staticmethod
    def get_market_status() -> str:
        """Get detailed market status"""
        now = datetime.now(timezone.utc)
        eastern = now - timedelta(hours=5)

        if eastern.weekday() >= 5:
            return "Weekend - Market Closed"

        hour_minute = eastern.hour * 60 + eastern.minute

        if 570 <= hour_minute <= 960:  # 9:30 AM - 4:00 PM
            return "Market Open"
        elif hour_minute < 570:
            return "Pre-Market"
        else:
            return "After-Hours"

class PriceData:
    """Container for price data"""

    def __init__(self, symbol: str, price: float, change: float, change_percent: float,
                 volume: int = 0, bid: float = None, ask: float = None,
                 high: float = None, low: float = None, previous_close: float = None):
        self.symbol = symbol
        self.price = price
        self.change = change
        self.change_percent = change_percent
        self.volume = volume
        self.bid = bid or price - 0.01
        self.ask = ask or price + 0.01
        self.high = high or price
        self.low = low or price
        self.previous_close = previous_close or (price - change)
        self.timestamp = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'price': round(self.price, 2),
            'change': round(self.change, 2),
            'change_percent': round(self.change_percent, 2),
            'volume': self.volume,
            'bid': round(self.bid, 2),
            'ask': round(self.ask, 2),
            'high': round(self.high, 2),
            'low': round(self.low, 2),
            'previous_close': round(self.previous_close, 2),
            'timestamp': int(self.timestamp.timestamp() * 1000),
            'last_updated': self.timestamp.isoformat()
        }

class RealTimeDataProvider:
    """
    Real-time market data provider with multiple data sources and caching
    """

    def __init__(self, cache_duration: int = 15):
        self.cache_duration = cache_duration  # seconds
        self.price_cache: Dict[str, PriceData] = {}
        self.cache_timestamps: Dict[str, float] = {}
        self.subscribers: Dict[str, List[Callable]] = {}
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.running = False
        self.update_thread = None

    def start(self):
        """Start the real-time data provider"""
        self.running = True
        self.update_thread = threading.Thread(target=self._run_updates, daemon=True)
        self.update_thread.start()
        logger.info("Real-time data provider started")

    def stop(self):
        """Stop the real-time data provider"""
        self.running = False
        if self.update_thread:
            self.update_thread.join()
        logger.info("Real-time data provider stopped")

    def _run_updates(self):
        """Background thread for updating prices"""
        while self.running:
            try:
                if self.subscribers and MarketHours.is_market_open():
                    symbols = list(self.subscribers.keys())
                    self._update_prices_batch(symbols)
                time.sleep(5)  # Update every 5 seconds during market hours
            except Exception as e:
                logger.error(f"Error in price update loop: {e}")
                time.sleep(10)  # Wait longer on error

    def subscribe(self, symbol: str, callback: Callable[[PriceData], None]):
        """Subscribe to price updates for a symbol"""
        if symbol not in self.subscribers:
            self.subscribers[symbol] = []
        self.subscribers[symbol].append(callback)

        # Get initial price
        try:
            price_data = self.get_price(symbol)
            callback(price_data)
        except Exception as e:
            logger.error(f"Error getting initial price for {symbol}: {e}")

    def unsubscribe(self, symbol: str, callback: Callable = None):
        """Unsubscribe from price updates"""
        if symbol in self.subscribers:
            if callback:
                try:
                    self.subscribers[symbol].remove(callback)
                except ValueError:
                    pass
            else:
                self.subscribers[symbol] = []

            if not self.subscribers[symbol]:
                del self.subscribers[symbol]

    def get_price(self, symbol: str, force_refresh: bool = False) -> PriceData:
        """Get current price for a symbol"""
        # Check cache first
        if not force_refresh and symbol in self.cache_timestamps:
            cache_age = time.time() - self.cache_timestamps[symbol]
            if cache_age < self.cache_duration:
                return self.price_cache[symbol]

        # Fetch fresh data
        try:
            price_data = self._fetch_yahoo_finance_price(symbol)
            self._cache_price(symbol, price_data)
            return price_data
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            # Return cached data if available, otherwise create mock data
            if symbol in self.price_cache:
                return self.price_cache[symbol]
            else:
                return self._create_mock_price(symbol)

    def get_prices_batch(self, symbols: List[str]) -> Dict[str, PriceData]:
        """Get prices for multiple symbols efficiently"""
        results = {}
        symbols_to_fetch = []

        # Check cache for each symbol
        for symbol in symbols:
            if symbol in self.cache_timestamps:
                cache_age = time.time() - self.cache_timestamps[symbol]
                if cache_age < self.cache_duration:
                    results[symbol] = self.price_cache[symbol]
                    continue
            symbols_to_fetch.append(symbol)

        # Fetch missing symbols
        if symbols_to_fetch:
            fresh_data = self._fetch_yahoo_finance_batch(symbols_to_fetch)
            for symbol, price_data in fresh_data.items():
                self._cache_price(symbol, price_data)
                results[symbol] = price_data

        return results

    def _update_prices_batch(self, symbols: List[str]):
        """Update prices for subscribed symbols and notify callbacks"""
        try:
            fresh_prices = self._fetch_yahoo_finance_batch(symbols)

            for symbol, price_data in fresh_prices.items():
                self._cache_price(symbol, price_data)

                # Notify subscribers
                if symbol in self.subscribers:
                    for callback in self.subscribers[symbol]:
                        try:
                            callback(price_data)
                        except Exception as e:
                            logger.error(f"Error in callback for {symbol}: {e}")

        except Exception as e:
            logger.error(f"Error updating prices batch: {e}")

    def _fetch_yahoo_finance_price(self, symbol: str) -> PriceData:
        """Fetch price from Yahoo Finance for single symbol"""
        try:
            ticker = yf.Ticker(symbol)

            # Get real-time data
            info = ticker.info
            hist = ticker.history(period="2d", interval="1m")

            if hist.empty:
                raise ValueError(f"No data available for {symbol}")

            # Get latest price and previous close
            current_price = float(hist['Close'].iloc[-1])
            previous_close = float(info.get('previousClose', hist['Close'].iloc[-2] if len(hist) > 1 else current_price))

            # Validate price data
            if not self._validate_price_data(current_price, previous_close):
                raise ValueError(f"Invalid price data for {symbol}: current={current_price}, previous={previous_close}")

            # Calculate change
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100 if previous_close != 0 else 0

            # Get additional data with validation
            volume = int(hist['Volume'].iloc[-1]) if not pd.isna(hist['Volume'].iloc[-1]) else 0
            high = float(hist['High'].iloc[-1])
            low = float(hist['Low'].iloc[-1])

            # Validate high/low consistency
            if high < current_price or low > current_price:
                logger.warning(f"Inconsistent high/low data for {symbol}, adjusting")
                high = max(high, current_price)
                low = min(low, current_price)

            return PriceData(
                symbol=symbol,
                price=current_price,
                change=change,
                change_percent=change_percent,
                volume=volume,
                high=high,
                low=low,
                previous_close=previous_close
            )

        except Exception as e:
            logger.error(f"Yahoo Finance error for {symbol}: {e}")
            raise

    def _fetch_yahoo_finance_batch(self, symbols: List[str]) -> Dict[str, PriceData]:
        """Fetch prices from Yahoo Finance for multiple symbols"""
        results = {}

        try:
            # Create a space-separated string of symbols
            symbols_str = " ".join(symbols)
            tickers = yf.Tickers(symbols_str)

            for symbol in symbols:
                try:
                    ticker = tickers.tickers[symbol]

                    # Get info and history
                    info = ticker.info
                    hist = ticker.history(period="2d", interval="1m")

                    if hist.empty:
                        logger.warning(f"No data for {symbol}, using mock data")
                        results[symbol] = self._create_mock_price(symbol)
                        continue

                    # Get latest price and previous close
                    current_price = float(hist['Close'].iloc[-1])
                    previous_close = float(info.get('previousClose', hist['Close'].iloc[-2] if len(hist) > 1 else current_price))

                    # Validate price data
                    if not self._validate_price_data(current_price, previous_close):
                        logger.warning(f"Invalid price data for {symbol}, using mock data")
                        results[symbol] = self._create_mock_price(symbol)
                        continue

                    # Calculate change
                    change = current_price - previous_close
                    change_percent = (change / previous_close) * 100 if previous_close != 0 else 0

                    # Get additional data with validation
                    volume = int(hist['Volume'].iloc[-1]) if not pd.isna(hist['Volume'].iloc[-1]) else 0
                    high = float(hist['High'].iloc[-1])
                    low = float(hist['Low'].iloc[-1])

                    # Validate high/low consistency
                    if high < current_price or low > current_price:
                        logger.warning(f"Inconsistent high/low data for {symbol}, adjusting")
                        high = max(high, current_price)
                        low = min(low, current_price)

                    results[symbol] = PriceData(
                        symbol=symbol,
                        price=current_price,
                        change=change,
                        change_percent=change_percent,
                        volume=volume,
                        high=high,
                        low=low,
                        previous_close=previous_close
                    )

                except Exception as e:
                    logger.error(f"Error fetching {symbol}: {e}")
                    results[symbol] = self._create_mock_price(symbol)

        except Exception as e:
            logger.error(f"Batch fetch error: {e}")
            # Fallback to individual fetches
            for symbol in symbols:
                try:
                    results[symbol] = self._fetch_yahoo_finance_price(symbol)
                except:
                    results[symbol] = self._create_mock_price(symbol)

        return results

    def _create_mock_price(self, symbol: str) -> PriceData:
        """Create mock price data for testing/fallback"""
        # Use symbol hash to create consistent mock prices
        base_price = abs(hash(symbol) % 1000) + 50  # Price between 50-1050

        # Add some random variation
        variation = (np.random.random() - 0.5) * 0.1  # ±5% variation
        current_price = base_price * (1 + variation)

        previous_close = base_price
        change = current_price - previous_close
        change_percent = (change / previous_close) * 100

        return PriceData(
            symbol=symbol,
            price=current_price,
            change=change,
            change_percent=change_percent,
            volume=np.random.randint(100000, 10000000),
            previous_close=previous_close
        )

    def _validate_price_data(self, current_price: float, previous_close: float) -> bool:
        """Validate price data for reasonableness"""
        try:
            # Check for valid positive prices
            if current_price <= 0 or previous_close <= 0:
                return False

            # Check for reasonable price ranges (not too extreme)
            if current_price > 1000000 or previous_close > 1000000:
                return False

            # Check for reasonable daily change (not more than 50% in a day)
            change_percent = abs((current_price - previous_close) / previous_close) * 100
            if change_percent > 50:
                logger.warning(f"Large price change detected: {change_percent:.2f}%")
                # Allow but log - some stocks can have extreme moves

            return True
        except (ZeroDivisionError, TypeError, ValueError):
            return False

    def _cache_price(self, symbol: str, price_data: PriceData):
        """Cache price data"""
        self.price_cache[symbol] = price_data
        self.cache_timestamps[symbol] = time.time()

# Global instance
realtime_provider = RealTimeDataProvider()