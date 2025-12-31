"""
News Cache
Caches news articles to reduce API calls and improve performance
"""

import json
import os
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import hashlib
import logging

logger = logging.getLogger(__name__)


class NewsCache:
    """
    Cache system for news articles

    Features:
    1. Disk-based caching with expiration
    2. Memory caching for recent requests
    3. Automatic cleanup of expired entries
    4. Configurable cache duration
    """

    def __init__(self,
                 cache_dir: str = 'cache/news',
                 default_expiry_hours: int = 6,
                 memory_cache_size: int = 100):
        """
        Initialize news cache

        Args:
            cache_dir: Directory for cache files
            default_expiry_hours: Default cache expiry in hours
            memory_cache_size: Maximum items in memory cache
        """
        self.cache_dir = cache_dir
        self.default_expiry_hours = default_expiry_hours
        self.memory_cache_size = memory_cache_size

        # Create cache directory
        os.makedirs(cache_dir, exist_ok=True)

        # Memory cache for frequent requests
        self.memory_cache = {}
        self.memory_access_times = {}

        logger.info(f"NewsCache initialized (dir: {cache_dir}, expiry: {default_expiry_hours}h)")

    def _generate_cache_key(self, symbol: str, days: int, source: str = '') -> str:
        """Generate unique cache key for request"""
        key_data = f"{symbol}_{days}_{source}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _get_cache_filepath(self, cache_key: str) -> str:
        """Get file path for cache key"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")

    def get(self, symbol: str, days: int, source: str = '') -> Optional[List[Dict]]:
        """
        Retrieve cached news articles

        Args:
            symbol: Stock symbol
            days: Days to look back
            source: News source

        Returns:
            Cached articles or None if not found/expired
        """
        try:
            cache_key = self._generate_cache_key(symbol, days, source)

            # Check memory cache first
            if cache_key in self.memory_cache:
                cached_data = self.memory_cache[cache_key]
                if self._is_cache_valid(cached_data['timestamp']):
                    self.memory_access_times[cache_key] = datetime.now()
                    logger.debug(f"Memory cache hit: {symbol}")
                    return cached_data['articles']
                else:
                    # Remove expired memory cache
                    del self.memory_cache[cache_key]
                    del self.memory_access_times[cache_key]

            # Check disk cache
            cache_file = self._get_cache_filepath(cache_key)
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                    # Convert timestamp string back to datetime
                    cached_data['timestamp'] = datetime.fromisoformat(cached_data['timestamp'])

                if self._is_cache_valid(cached_data['timestamp']):
                    # Load into memory cache
                    self._add_to_memory_cache(cache_key, cached_data)
                    logger.debug(f"Disk cache hit: {symbol}")
                    return cached_data['articles']
                else:
                    # Remove expired disk cache
                    os.remove(cache_file)
                    logger.debug(f"Removed expired cache: {symbol}")

            return None

        except Exception as e:
            logger.error(f"Cache retrieval failed for {symbol}: {e}")
            return None

    def set(self, symbol: str, days: int, articles: List[Dict],
            source: str = '', expiry_hours: Optional[int] = None) -> bool:
        """
        Cache news articles

        Args:
            symbol: Stock symbol
            days: Days looked back
            articles: News articles to cache
            source: News source
            expiry_hours: Custom expiry time (uses default if None)

        Returns:
            True if cached successfully
        """
        try:
            cache_key = self._generate_cache_key(symbol, days, source)
            timestamp = datetime.now()

            # Memory cache data (with datetime object)
            memory_data = {
                'symbol': symbol,
                'days': days,
                'source': source,
                'articles': articles,
                'timestamp': timestamp,
                'expiry_hours': expiry_hours or self.default_expiry_hours
            }

            # Disk cache data (with ISO string timestamp)
            disk_data = {
                'symbol': symbol,
                'days': days,
                'source': source,
                'articles': articles,
                'timestamp': timestamp.isoformat(),
                'expiry_hours': expiry_hours or self.default_expiry_hours
            }

            # Save to disk
            cache_file = self._get_cache_filepath(cache_key)
            with open(cache_file, 'w') as f:
                json.dump(disk_data, f, indent=2)

            # Add to memory cache
            self._add_to_memory_cache(cache_key, memory_data)

            logger.debug(f"Cached {len(articles)} articles for {symbol}")
            return True

        except Exception as e:
            logger.error(f"Cache save failed for {symbol}: {e}")
            return False

    def _is_cache_valid(self, timestamp: datetime, expiry_hours: int = None) -> bool:
        """Check if cache entry is still valid"""
        expiry_hours = expiry_hours or self.default_expiry_hours
        expiry_time = timestamp + timedelta(hours=expiry_hours)
        return datetime.now() < expiry_time

    def _add_to_memory_cache(self, cache_key: str, cached_data: Dict):
        """Add entry to memory cache with size management"""
        try:
            # Remove oldest entries if cache is full
            while len(self.memory_cache) >= self.memory_cache_size:
                oldest_key = min(self.memory_access_times,
                               key=self.memory_access_times.get)
                del self.memory_cache[oldest_key]
                del self.memory_access_times[oldest_key]

            # Add new entry
            self.memory_cache[cache_key] = cached_data
            self.memory_access_times[cache_key] = datetime.now()

        except Exception as e:
            logger.error(f"Memory cache update failed: {e}")

    def cleanup_expired(self) -> int:
        """
        Remove expired cache entries

        Returns:
            Number of entries removed
        """
        try:
            removed_count = 0

            # Clean disk cache
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.cache_dir, filename)
                    try:
                        with open(filepath, 'r') as f:
                            cached_data = json.load(f)
                            # Convert timestamp string to datetime
                            cached_data['timestamp'] = datetime.fromisoformat(cached_data['timestamp'])

                        if not self._is_cache_valid(cached_data['timestamp'],
                                                   cached_data.get('expiry_hours')):
                            os.remove(filepath)
                            removed_count += 1

                    except Exception as e:
                        # Remove corrupted cache files
                        os.remove(filepath)
                        removed_count += 1
                        logger.warning(f"Removed corrupted cache file: {filename}")

            # Clean memory cache
            expired_keys = []
            for cache_key, cached_data in self.memory_cache.items():
                if not self._is_cache_valid(cached_data['timestamp'],
                                          cached_data.get('expiry_hours')):
                    expired_keys.append(cache_key)

            for key in expired_keys:
                del self.memory_cache[key]
                del self.memory_access_times[key]
                removed_count += 1

            if removed_count > 0:
                logger.info(f"Cleaned up {removed_count} expired cache entries")

            return removed_count

        except Exception as e:
            logger.error(f"Cache cleanup failed: {e}")
            return 0

    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        try:
            # Count disk cache files
            disk_files = 0
            total_disk_size = 0

            if os.path.exists(self.cache_dir):
                for filename in os.listdir(self.cache_dir):
                    if filename.endswith('.json'):
                        filepath = os.path.join(self.cache_dir, filename)
                        disk_files += 1
                        total_disk_size += os.path.getsize(filepath)

            return {
                'memory_cache_size': len(self.memory_cache),
                'memory_cache_limit': self.memory_cache_size,
                'disk_cache_files': disk_files,
                'disk_cache_size_mb': total_disk_size / (1024 * 1024),
                'cache_directory': self.cache_dir,
                'default_expiry_hours': self.default_expiry_hours
            }

        except Exception as e:
            logger.error(f"Cache stats failed: {e}")
            return {'error': str(e)}

    def clear_cache(self, symbol: Optional[str] = None) -> int:
        """
        Clear cache entries

        Args:
            symbol: If provided, only clear cache for this symbol

        Returns:
            Number of entries removed
        """
        try:
            removed_count = 0

            if symbol:
                # Clear specific symbol cache
                keys_to_remove = []
                for cache_key, cached_data in self.memory_cache.items():
                    if cached_data.get('symbol') == symbol:
                        keys_to_remove.append(cache_key)

                for key in keys_to_remove:
                    del self.memory_cache[key]
                    del self.memory_access_times[key]
                    removed_count += 1

                # Clear disk cache for symbol
                for filename in os.listdir(self.cache_dir):
                    if filename.endswith('.json'):
                        filepath = os.path.join(self.cache_dir, filename)
                        try:
                            with open(filepath, 'r') as f:
                                cached_data = json.load(f)

                            if cached_data.get('symbol') == symbol:
                                os.remove(filepath)
                                removed_count += 1

                        except Exception:
                            pass

            else:
                # Clear all cache
                self.memory_cache.clear()
                self.memory_access_times.clear()

                for filename in os.listdir(self.cache_dir):
                    if filename.endswith('.json'):
                        filepath = os.path.join(self.cache_dir, filename)
                        os.remove(filepath)
                        removed_count += 1

            logger.info(f"Cleared {removed_count} cache entries" +
                       (f" for {symbol}" if symbol else ""))

            return removed_count

        except Exception as e:
            logger.error(f"Cache clearing failed: {e}")
            return 0