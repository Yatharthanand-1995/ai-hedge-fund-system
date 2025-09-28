"""
Data Cache for Stock Picker
Pre-downloads and caches fundamental data to speed up backtesting
"""

import yfinance as yf
import pandas as pd
import pickle
import os
import time
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataCache:
    """
    Caches stock fundamental and price data for fast backtesting

    Structure:
    {
        'AAPL': {
            'info': {...},  # ticker.info
            'financials': DataFrame,
            'balance_sheet': DataFrame,
            'cashflow': DataFrame,
            'recommendations': DataFrame,
            'price_data': DataFrame,
            'last_updated': timestamp
        },
        ...
    }
    """

    def __init__(self, cache_dir: str = './cache'):
        self.cache_dir = cache_dir
        self.cache = {}

        # Create cache directory
        os.makedirs(cache_dir, exist_ok=True)

        logger.info(f"DataCache initialized at {cache_dir}")

    def download_all_data(self, symbols: List[str], start_date: str, end_date: str,
                         force_refresh: bool = False) -> None:
        """
        Download all data for symbols and cache it

        Args:
            symbols: List of stock symbols
            start_date: Start date for price data
            end_date: End date for price data
            force_refresh: Force re-download even if cached
        """

        print(f"\n{'='*80}")
        print(f"DOWNLOADING DATA FOR {len(symbols)} STOCKS")
        print(f"{'='*80}")

        for i, symbol in enumerate(symbols, 1):
            print(f"[{i}/{len(symbols)}] Downloading {symbol}...", end=" ")

            # Check if cached and recent
            if not force_refresh and self._is_cached_and_recent(symbol):
                print("✓ (cached)")
                continue

            try:
                # Download with retry logic
                success = False
                max_retries = 3

                for retry in range(max_retries):
                    try:
                        # Download all data
                        ticker = yf.Ticker(symbol)

                        # Get fundamental data
                        info = ticker.info
                        financials = ticker.financials
                        balance_sheet = ticker.balance_sheet
                        cashflow = ticker.cashflow
                        recommendations = ticker.recommendations

                        # Get price data with auto_adjust to suppress warning
                        price_data = yf.download(symbol, start=start_date, end=end_date,
                                                progress=False, auto_adjust=False)

                        # Cache it
                        self.cache[symbol] = {
                            'info': info,
                            'financials': financials,
                            'balance_sheet': balance_sheet,
                            'cashflow': cashflow,
                            'recommendations': recommendations,
                            'price_data': price_data,
                            'last_updated': datetime.now()
                        }

                        print("✓")
                        success = True
                        break

                    except Exception as e:
                        if retry < max_retries - 1:
                            wait_time = 2 ** retry
                            logger.warning(f"Download failed for {symbol} (attempt {retry+1}/{max_retries}), "
                                         f"retrying in {wait_time}s: {e}")
                            time.sleep(wait_time)
                        else:
                            raise e

                if not success:
                    raise Exception(f"Failed after {max_retries} retries")

            except Exception as e:
                logger.error(f"Failed to download {symbol}: {e}")
                print(f"✗ ({str(e)[:50]})")
                continue

        print(f"\n✅ Downloaded {len(self.cache)} stocks")

    def save_to_disk(self, filename: str = 'stock_data_cache.pkl') -> None:
        """Save cache to disk"""
        filepath = os.path.join(self.cache_dir, filename)

        with open(filepath, 'wb') as f:
            pickle.dump(self.cache, f)

        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        logger.info(f"Cache saved to {filepath} ({size_mb:.1f} MB)")
        print(f"💾 Cache saved to {filepath} ({size_mb:.1f} MB)")

    def load_from_disk(self, filename: str = 'stock_data_cache.pkl') -> bool:
        """Load cache from disk"""
        filepath = os.path.join(self.cache_dir, filename)

        if not os.path.exists(filepath):
            logger.warning(f"Cache file not found: {filepath}")
            return False

        try:
            with open(filepath, 'rb') as f:
                self.cache = pickle.load(f)

            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            logger.info(f"Cache loaded from {filepath} ({size_mb:.1f} MB, {len(self.cache)} stocks)")
            print(f"📂 Loaded cache: {len(self.cache)} stocks ({size_mb:.1f} MB)")
            return True

        except Exception as e:
            logger.error(f"Failed to load cache: {e}")
            return False

    def get_info(self, symbol: str) -> Dict:
        """Get ticker.info for symbol"""
        if symbol in self.cache:
            return self.cache[symbol].get('info', {})
        return {}

    def get_financials(self, symbol: str) -> pd.DataFrame:
        """Get financials for symbol"""
        if symbol in self.cache:
            return self.cache[symbol].get('financials', pd.DataFrame())
        return pd.DataFrame()

    def get_balance_sheet(self, symbol: str) -> pd.DataFrame:
        """Get balance sheet for symbol"""
        if symbol in self.cache:
            return self.cache[symbol].get('balance_sheet', pd.DataFrame())
        return pd.DataFrame()

    def get_cashflow(self, symbol: str) -> pd.DataFrame:
        """Get cash flow for symbol"""
        if symbol in self.cache:
            return self.cache[symbol].get('cashflow', pd.DataFrame())
        return pd.DataFrame()

    def get_recommendations(self, symbol: str) -> pd.DataFrame:
        """Get recommendations for symbol"""
        if symbol in self.cache:
            return self.cache[symbol].get('recommendations', pd.DataFrame())
        return pd.DataFrame()

    def get_price_data(self, symbol: str, end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Get price data for symbol up to end_date

        Args:
            symbol: Stock ticker
            end_date: End date (if None, returns all data)
        """
        if symbol not in self.cache:
            return pd.DataFrame()

        price_data = self.cache[symbol].get('price_data', pd.DataFrame())

        if price_data.empty:
            return price_data

        if end_date:
            # Filter up to end_date
            return price_data.loc[:end_date]

        return price_data

    def _is_cached_and_recent(self, symbol: str, max_age_hours: int = 24) -> bool:
        """Check if symbol is cached and data is recent"""
        if symbol not in self.cache:
            return False

        last_updated = self.cache[symbol].get('last_updated')
        if not last_updated:
            return False

        age_hours = (datetime.now() - last_updated).total_seconds() / 3600
        return age_hours < max_age_hours

    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        if not self.cache:
            return {
                'total_symbols': 0,
                'symbols_with_info': 0,
                'symbols_with_financials': 0,
                'symbols_with_price_data': 0
            }

        return {
            'total_symbols': len(self.cache),
            'symbols_with_info': len([s for s in self.cache if self.cache[s].get('info')]),
            'symbols_with_financials': len([s for s in self.cache if not self.cache[s].get('financials', pd.DataFrame()).empty]),
            'symbols_with_price_data': len([s for s in self.cache if not self.cache[s].get('price_data', pd.DataFrame()).empty]),
            'oldest_update': min([self.cache[s].get('last_updated', datetime.now()) for s in self.cache]),
            'newest_update': max([self.cache[s].get('last_updated', datetime.now()) for s in self.cache])
        }

    def clear_cache(self) -> None:
        """Clear all cached data"""
        self.cache = {}
        logger.info("Cache cleared")


# Convenience functions
_global_cache = None

def get_global_cache(cache_dir: str = './cache') -> DataCache:
    """Get or create global cache instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = DataCache(cache_dir=cache_dir)
    return _global_cache

def load_or_create_cache(symbols: List[str], start_date: str, end_date: str,
                         cache_file: str = 'stock_data_cache.pkl',
                         force_refresh: bool = False) -> DataCache:
    """
    Load cache from disk or create new one

    Args:
        symbols: List of symbols to cache
        start_date: Start date for price data
        end_date: End date for price data
        cache_file: Cache filename
        force_refresh: Force re-download
    """

    cache = get_global_cache()

    # Try to load from disk
    if not force_refresh and cache.load_from_disk(cache_file):
        # Check if we have all symbols
        cached_symbols = set(cache.cache.keys())
        missing_symbols = set(symbols) - cached_symbols

        if missing_symbols:
            print(f"⚠️  Missing {len(missing_symbols)} symbols, downloading...")
            cache.download_all_data(list(missing_symbols), start_date, end_date)
            cache.save_to_disk(cache_file)

        return cache

    # Download all data
    print("📥 No cache found, downloading all data...")
    cache.download_all_data(symbols, start_date, end_date, force_refresh=force_refresh)
    cache.save_to_disk(cache_file)

    return cache