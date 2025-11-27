"""
System Alerts Manager
Tracks errors, warnings, and system events for internal dashboard monitoring
"""

from datetime import datetime
from typing import List, Dict, Optional
from collections import deque
import logging

logger = logging.getLogger(__name__)


class AlertsManager:
    """
    In-memory alerts tracking for dashboard monitoring
    Keeps recent alerts (last 100) for display in frontend
    """

    def __init__(self, max_alerts: int = 100):
        """
        Initialize alerts manager

        Args:
            max_alerts: Maximum number of alerts to keep in memory
        """
        self.max_alerts = max_alerts
        self.alerts = deque(maxlen=max_alerts)
        self.error_count = 0
        self.warning_count = 0
        self.info_count = 0

    def add_alert(
        self,
        level: str,
        category: str,
        message: str,
        details: Optional[Dict] = None,
        source: Optional[str] = None
    ) -> Dict:
        """
        Add a new alert

        Args:
            level: Alert severity (error, warning, info, success)
            category: Alert category (api, agent, system, performance)
            message: Alert message
            details: Additional details dictionary
            source: Source of the alert (endpoint, agent name, etc.)

        Returns:
            The created alert dictionary
        """
        alert = {
            'id': f"{datetime.now().timestamp()}_{self.error_count + self.warning_count + self.info_count}",
            'timestamp': datetime.now().isoformat(),
            'level': level.lower(),
            'category': category,
            'message': message,
            'details': details or {},
            'source': source,
            'read': False
        }

        self.alerts.appendleft(alert)  # Add to front (most recent first)

        # Update counters
        if level.lower() == 'error':
            self.error_count += 1
        elif level.lower() == 'warning':
            self.warning_count += 1
        else:
            self.info_count += 1

        return alert

    def get_alerts(
        self,
        limit: int = 50,
        level: Optional[str] = None,
        category: Optional[str] = None,
        unread_only: bool = False
    ) -> List[Dict]:
        """
        Get recent alerts with optional filtering

        Args:
            limit: Maximum number of alerts to return
            level: Filter by alert level (error, warning, info, success)
            category: Filter by category (api, agent, system, performance)
            unread_only: Only return unread alerts

        Returns:
            List of alert dictionaries
        """
        filtered = list(self.alerts)

        if level:
            filtered = [a for a in filtered if a['level'] == level.lower()]

        if category:
            filtered = [a for a in filtered if a['category'] == category]

        if unread_only:
            filtered = [a for a in filtered if not a['read']]

        return filtered[:limit]

    def mark_read(self, alert_id: str) -> bool:
        """
        Mark an alert as read

        Args:
            alert_id: ID of the alert to mark as read

        Returns:
            True if alert was found and marked, False otherwise
        """
        for alert in self.alerts:
            if alert['id'] == alert_id:
                alert['read'] = True
                return True
        return False

    def mark_all_read(self) -> int:
        """
        Mark all alerts as read

        Returns:
            Number of alerts marked as read
        """
        count = 0
        for alert in self.alerts:
            if not alert['read']:
                alert['read'] = True
                count += 1
        return count

    def get_stats(self) -> Dict:
        """
        Get alert statistics

        Returns:
            Dictionary with alert counts and stats
        """
        unread_count = sum(1 for a in self.alerts if not a['read'])

        recent_errors = sum(
            1 for a in self.alerts
            if a['level'] == 'error'
            and (datetime.now() - datetime.fromisoformat(a['timestamp'])).seconds < 3600
        )

        return {
            'total_alerts': len(self.alerts),
            'unread_count': unread_count,
            'error_count': self.error_count,
            'warning_count': self.warning_count,
            'info_count': self.info_count,
            'recent_errors_1h': recent_errors,
            'levels': {
                'error': sum(1 for a in self.alerts if a['level'] == 'error'),
                'warning': sum(1 for a in self.alerts if a['level'] == 'warning'),
                'info': sum(1 for a in self.alerts if a['level'] == 'info'),
                'success': sum(1 for a in self.alerts if a['level'] == 'success'),
            },
            'categories': self._count_by_category()
        }

    def _count_by_category(self) -> Dict[str, int]:
        """Count alerts by category"""
        counts = {}
        for alert in self.alerts:
            category = alert['category']
            counts[category] = counts.get(category, 0) + 1
        return counts

    def clear_old_alerts(self, days: int = 7) -> int:
        """
        Clear alerts older than specified days

        Args:
            days: Number of days to keep

        Returns:
            Number of alerts cleared
        """
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        original_count = len(self.alerts)

        self.alerts = deque(
            (a for a in self.alerts if datetime.fromisoformat(a['timestamp']).timestamp() > cutoff),
            maxlen=self.max_alerts
        )

        cleared = original_count - len(self.alerts)
        if cleared > 0:
            logger.info(f"Cleared {cleared} alerts older than {days} days")
        return cleared


# Global singleton instance
_alerts_manager = None


def get_alerts_manager() -> AlertsManager:
    """Get the global alerts manager instance"""
    global _alerts_manager
    if _alerts_manager is None:
        _alerts_manager = AlertsManager(max_alerts=100)
    return _alerts_manager
