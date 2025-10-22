"""
Backtest Results Storage System
Persists backtest results to JSON files for historical tracking
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class BacktestStorage:
    """
    Simple JSON-based storage for backtest results

    Storage Structure:
    data/backtest_results/
        ├── index.json (list of all backtest IDs with metadata)
        └── results/
            ├── {backtest_id_1}.json
            ├── {backtest_id_2}.json
            └── ...
    """

    def __init__(self, storage_dir: str = None):
        """
        Initialize backtest storage

        Args:
            storage_dir: Directory to store backtest results (defaults to data/backtest_results)
        """
        if storage_dir is None:
            # Default to data/backtest_results in project root
            project_root = os.path.dirname(os.path.dirname(__file__))
            storage_dir = os.path.join(project_root, 'data', 'backtest_results')

        self.storage_dir = storage_dir
        self.results_dir = os.path.join(storage_dir, 'results')
        self.index_file = os.path.join(storage_dir, 'index.json')

        # Create directories if they don't exist
        os.makedirs(self.results_dir, exist_ok=True)

        # Initialize index if it doesn't exist
        if not os.path.exists(self.index_file):
            self._save_index([])

    def _load_index(self) -> List[Dict]:
        """Load the index of all backtest results"""
        try:
            with open(self.index_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            logger.error(f"Failed to parse index file: {self.index_file}")
            return []

    def _save_index(self, index: List[Dict]):
        """Save the index of all backtest results"""
        with open(self.index_file, 'w') as f:
            json.dump(index, f, indent=2)

    def save_result(self, backtest_id: str, config: Dict, results: Dict, timestamp: str = None) -> str:
        """
        Save a backtest result

        Args:
            backtest_id: Unique identifier for this backtest
            config: Backtest configuration
            results: Backtest results
            timestamp: ISO timestamp (defaults to now)

        Returns:
            backtest_id: The ID of the saved backtest
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        # Create full backtest record
        backtest_record = {
            'backtest_id': backtest_id,
            'config': config,
            'results': results,
            'timestamp': timestamp,
            'created_at': timestamp
        }

        # Save full result to file
        result_file = os.path.join(self.results_dir, f'{backtest_id}.json')
        with open(result_file, 'w') as f:
            json.dump(backtest_record, f, indent=2)

        # Update index
        index = self._load_index()

        # Create index entry with metadata
        index_entry = {
            'backtest_id': backtest_id,
            'timestamp': timestamp,
            'start_date': config.get('start_date'),
            'end_date': config.get('end_date'),
            'initial_capital': config.get('initial_capital'),
            'final_value': results.get('final_value'),
            'total_return': results.get('total_return'),
            'sharpe_ratio': results.get('metrics', {}).get('sharpe_ratio'),
            'max_drawdown': results.get('metrics', {}).get('max_drawdown'),
            'num_rebalances': results.get('rebalances', 0),
            'universe_size': len(config.get('universe', [])),
        }

        # Add to index (most recent first)
        index.insert(0, index_entry)

        # Keep only last 100 backtests in index
        if len(index) > 100:
            # Remove oldest entries
            removed = index[100:]
            index = index[:100]

            # Delete old result files
            for entry in removed:
                old_file = os.path.join(self.results_dir, f"{entry['backtest_id']}.json")
                try:
                    if os.path.exists(old_file):
                        os.remove(old_file)
                except Exception as e:
                    logger.warning(f"Failed to delete old backtest file {old_file}: {e}")

        self._save_index(index)

        logger.info(f"✅ Saved backtest result: {backtest_id} (Return: {results.get('total_return', 0)*100:.1f}%)")
        return backtest_id

    def get_result_by_id(self, backtest_id: str) -> Optional[Dict]:
        """
        Get a specific backtest result by ID

        Args:
            backtest_id: The backtest ID to retrieve

        Returns:
            Full backtest record or None if not found
        """
        result_file = os.path.join(self.results_dir, f'{backtest_id}.json')

        try:
            with open(result_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Backtest result not found: {backtest_id}")
            return None
        except json.JSONDecodeError:
            logger.error(f"Failed to parse backtest result: {backtest_id}")
            return None

    def get_all_results(self, limit: int = 10) -> List[Dict]:
        """
        Get all backtest results (summary only, from index)

        Args:
            limit: Maximum number of results to return (default 10)

        Returns:
            List of backtest summary records (most recent first)
        """
        index = self._load_index()
        return index[:limit]

    def get_full_results(self, limit: int = 10) -> List[Dict]:
        """
        Get full backtest results (loads complete records from files)

        Args:
            limit: Maximum number of results to return (default 10)

        Returns:
            List of full backtest records (most recent first)
        """
        index = self._load_index()
        results = []

        for entry in index[:limit]:
            backtest_id = entry['backtest_id']
            full_result = self.get_result_by_id(backtest_id)
            if full_result:
                results.append(full_result)

        return results

    def delete_result(self, backtest_id: str) -> bool:
        """
        Delete a backtest result

        Args:
            backtest_id: The backtest ID to delete

        Returns:
            True if deleted, False if not found
        """
        result_file = os.path.join(self.results_dir, f'{backtest_id}.json')

        # Remove from index
        index = self._load_index()
        original_length = len(index)
        index = [entry for entry in index if entry['backtest_id'] != backtest_id]

        if len(index) == original_length:
            # Not found in index
            return False

        self._save_index(index)

        # Remove file
        try:
            if os.path.exists(result_file):
                os.remove(result_file)
            logger.info(f"🗑️ Deleted backtest result: {backtest_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete backtest file: {e}")
            return False

    def get_storage_stats(self) -> Dict:
        """
        Get storage statistics

        Returns:
            Dictionary with storage stats
        """
        index = self._load_index()

        # Calculate total storage size
        total_size = 0
        for entry in index:
            result_file = os.path.join(self.results_dir, f"{entry['backtest_id']}.json")
            if os.path.exists(result_file):
                total_size += os.path.getsize(result_file)

        return {
            'total_backtests': len(index),
            'storage_size_bytes': total_size,
            'storage_size_mb': round(total_size / (1024 * 1024), 2),
            'oldest_backtest': index[-1]['timestamp'] if index else None,
            'newest_backtest': index[0]['timestamp'] if index else None,
        }


# Singleton instance for global access
_storage_instance = None


def get_backtest_storage() -> BacktestStorage:
    """Get the global backtest storage instance"""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = BacktestStorage()
    return _storage_instance
