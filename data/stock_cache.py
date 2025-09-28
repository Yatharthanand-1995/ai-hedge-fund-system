"""
Stock Pick Caching System
Provides intelligent caching for stock picks and market data to dramatically improve performance
"""

import time
import logging
import pickle
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta
from pathlib import Path
import threading

logger = logging.getLogger(__name__)

class StockPickCache:
    """
    High-performance caching system for stock picks and market data
    """

    def __init__(self, cache_dir: str = "cache", default_ttl: int = 300):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.default_ttl = default_ttl  # 5 minutes default

        # In-memory cache for hot data
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_lock = threading.RLock()

        # Different TTLs for different data types
        self.ttls = {
            'stock_picks': 300,      # 5 minutes - picks can change frequently
            'stock_scores': 1800,    # 30 minutes - scores are expensive to compute
            'market_data': 60,       # 1 minute - market data changes frequently
            'historical_data': 3600, # 1 hour - historical data is static
            'realtime_prices': 15,   # 15 seconds - real-time prices
        }

        logger.info(f"StockPickCache initialized with cache dir: {self.cache_dir}")

    def _get_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate a unique cache key based on parameters"""
        # Sort kwargs for consistent key generation
        sorted_kwargs = sorted(kwargs.items())
        key_data = f"{prefix}:{sorted_kwargs}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _is_expired(self, cache_entry: Dict[str, Any], cache_type: str) -> bool:
        """Check if cache entry has expired"""
        if 'timestamp' not in cache_entry:
            return True

        ttl = self.ttls.get(cache_type, self.default_ttl)
        age = time.time() - cache_entry['timestamp']
        return age > ttl

    def get_stock_picks(self, limit: int = 20, **filters) -> Optional[List[Dict]]:
        """Get cached stock picks"""
        cache_key = self._get_cache_key('stock_picks', limit=limit, **filters)

        with self._cache_lock:
            if cache_key in self._memory_cache:
                entry = self._memory_cache[cache_key]
                if not self._is_expired(entry, 'stock_picks'):
                    logger.debug(f"Cache HIT for stock_picks (key: {cache_key[:8]}...)")
                    return entry['data']
                else:
                    # Remove expired entry
                    del self._memory_cache[cache_key]
                    logger.debug(f"Cache EXPIRED for stock_picks (key: {cache_key[:8]}...)")

        logger.debug(f"Cache MISS for stock_picks (key: {cache_key[:8]}...)")
        return None

    def set_stock_picks(self, picks: List[Dict], limit: int = 20, **filters) -> None:
        """Cache stock picks"""
        cache_key = self._get_cache_key('stock_picks', limit=limit, **filters)

        entry = {
            'data': picks,
            'timestamp': time.time(),
            'created_at': datetime.now(timezone.utc).isoformat()
        }

        with self._cache_lock:
            self._memory_cache[cache_key] = entry
            logger.info(f"Cached {len(picks)} stock picks (key: {cache_key[:8]}...)")

    def get_stock_scores(self, symbol: str) -> Optional[Dict]:
        """Get cached stock scores for a symbol"""
        cache_key = self._get_cache_key('stock_scores', symbol=symbol)

        with self._cache_lock:
            if cache_key in self._memory_cache:
                entry = self._memory_cache[cache_key]
                if not self._is_expired(entry, 'stock_scores'):
                    logger.debug(f"Cache HIT for stock_scores ({symbol})")
                    return entry['data']
                else:
                    del self._memory_cache[cache_key]
                    logger.debug(f"Cache EXPIRED for stock_scores ({symbol})")

        logger.debug(f"Cache MISS for stock_scores ({symbol})")
        return None

    def set_stock_scores(self, symbol: str, scores: Dict) -> None:
        """Cache stock scores for a symbol"""
        cache_key = self._get_cache_key('stock_scores', symbol=symbol)

        entry = {
            'data': scores,
            'timestamp': time.time(),
            'created_at': datetime.now(timezone.utc).isoformat()
        }

        with self._cache_lock:
            self._memory_cache[cache_key] = entry
            logger.debug(f"Cached stock scores for {symbol}")

    def get_historical_data(self, symbol: str, period: str = '2y') -> Optional[Any]:
        """Get cached historical data"""
        cache_key = self._get_cache_key('historical_data', symbol=symbol, period=period)

        # Check memory cache first
        with self._cache_lock:
            if cache_key in self._memory_cache:
                entry = self._memory_cache[cache_key]
                if not self._is_expired(entry, 'historical_data'):
                    logger.debug(f"Memory cache HIT for historical_data ({symbol})")
                    return entry['data']
                else:
                    del self._memory_cache[cache_key]

        # Check disk cache
        cache_file = self.cache_dir / f"hist_{cache_key}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    entry = pickle.load(f)
                    if not self._is_expired(entry, 'historical_data'):
                        logger.debug(f"Disk cache HIT for historical_data ({symbol})")
                        # Also store in memory for faster access
                        with self._cache_lock:
                            self._memory_cache[cache_key] = entry
                        return entry['data']
                    else:
                        cache_file.unlink()  # Remove expired cache file
            except Exception as e:
                logger.warning(f"Failed to load cached historical data for {symbol}: {e}")
                cache_file.unlink()

        logger.debug(f"Cache MISS for historical_data ({symbol})")
        return None

    def set_historical_data(self, symbol: str, data: Any, period: str = '2y') -> None:
        """Cache historical data"""
        cache_key = self._get_cache_key('historical_data', symbol=symbol, period=period)

        entry = {
            'data': data,
            'timestamp': time.time(),
            'created_at': datetime.now(timezone.utc).isoformat()
        }

        # Store in memory cache
        with self._cache_lock:
            self._memory_cache[cache_key] = entry

        # Also store on disk for persistence
        cache_file = self.cache_dir / f"hist_{cache_key}.pkl"
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(entry, f)
            logger.debug(f"Cached historical data for {symbol} (memory + disk)")
        except Exception as e:
            logger.warning(f"Failed to save historical data cache for {symbol}: {e}")

    def get_market_data(self, key: str) -> Optional[Any]:
        """Get cached market data"""
        cache_key = self._get_cache_key('market_data', key=key)

        with self._cache_lock:
            if cache_key in self._memory_cache:
                entry = self._memory_cache[cache_key]
                if not self._is_expired(entry, 'market_data'):
                    logger.debug(f"Cache HIT for market_data ({key})")
                    return entry['data']
                else:
                    del self._memory_cache[cache_key]

        return None

    def set_market_data(self, key: str, data: Any) -> None:
        """Cache market data"""
        cache_key = self._get_cache_key('market_data', key=key)

        entry = {
            'data': data,
            'timestamp': time.time(),
            'created_at': datetime.now(timezone.utc).isoformat()
        }

        with self._cache_lock:
            self._memory_cache[cache_key] = entry
            logger.debug(f"Cached market data ({key})")

    def invalidate_stock(self, symbol: str) -> None:
        """Invalidate all cached data for a specific stock"""
        with self._cache_lock:
            keys_to_remove = []
            for key, entry in self._memory_cache.items():
                if symbol in str(entry.get('data', {})):
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del self._memory_cache[key]

            logger.info(f"Invalidated {len(keys_to_remove)} cache entries for {symbol}")

    def invalidate_all(self) -> None:
        """Clear all cached data"""
        with self._cache_lock:
            cache_count = len(self._memory_cache)
            self._memory_cache.clear()
            logger.info(f"Invalidated all cached data ({cache_count} entries)")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._cache_lock:
            total_entries = len(self._memory_cache)

            # Count entries by type
            type_counts = {}
            expired_count = 0

            for entry in self._memory_cache.values():
                # Try to determine cache type from data structure
                data = entry.get('data', {})
                if isinstance(data, list) and len(data) > 0 and 'symbol' in str(data[0]):
                    cache_type = 'stock_picks'
                elif isinstance(data, dict) and 'score' in str(data):
                    cache_type = 'stock_scores'
                else:
                    cache_type = 'other'

                type_counts[cache_type] = type_counts.get(cache_type, 0) + 1

                # Check if expired
                if self._is_expired(entry, cache_type):
                    expired_count += 1

        return {
            'total_entries': total_entries,
            'type_counts': type_counts,
            'expired_count': expired_count,
            'memory_cache_size': total_entries,
            'cache_ttls': self.ttls
        }

# Global cache instance
stock_cache = StockPickCache()