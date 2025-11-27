import React, { useState, useEffect } from 'react';
import { AlertCircle, Bell, CheckCircle, Info, XCircle, AlertTriangle, RefreshCw, CheckCheck } from 'lucide-react';

interface Alert {
  id: string;
  timestamp: string;
  level: 'error' | 'warning' | 'info' | 'success';
  category: string;
  message: string;
  details: Record<string, any>;
  source: string | null;
  read: boolean;
}

interface AlertStats {
  total_alerts: number;
  unread_count: number;
  error_count: number;
  warning_count: number;
  info_count: number;
  recent_errors_1h: number;
  levels: {
    error: number;
    warning: number;
    info: number;
    success: number;
  };
  categories: Record<string, number>;
}

const AlertsPage: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [stats, setStats] = useState<AlertStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [filterLevel, setFilterLevel] = useState<string>('');
  const [filterCategory, setFilterCategory] = useState<string>('');
  const [showUnreadOnly, setShowUnreadOnly] = useState(false);

  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8010';

  const fetchAlerts = async () => {
    try {
      const params = new URLSearchParams();
      if (filterLevel) params.append('level', filterLevel);
      if (filterCategory) params.append('category', filterCategory);
      if (showUnreadOnly) params.append('unread_only', 'true');

      const response = await fetch(`${API_BASE_URL}/alerts?${params}`);
      const data = await response.json();
      setAlerts(data.alerts);
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/alerts/stats`);
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const markAsRead = async (alertId: string) => {
    try {
      await fetch(`${API_BASE_URL}/alerts/${alertId}/read`, {
        method: 'POST',
      });
      await fetchAlerts();
      await fetchStats();
    } catch (error) {
      console.error('Failed to mark alert as read:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      await fetch(`${API_BASE_URL}/alerts/read-all`, {
        method: 'POST',
      });
      await fetchAlerts();
      await fetchStats();
    } catch (error) {
      console.error('Failed to mark all as read:', error);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchAlerts(), fetchStats()]);
      setLoading(false);
    };

    loadData();

    // Auto-refresh every 10 seconds
    const interval = setInterval(() => {
      fetchAlerts();
      fetchStats();
    }, 10000);

    return () => clearInterval(interval);
  }, [filterLevel, filterCategory, showUnreadOnly]);

  const getLevelIcon = (level: string) => {
    switch (level) {
      case 'error':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      default:
        return <Info className="w-5 h-5 text-blue-500" />;
    }
  };

  const getLevelBadge = (level: string) => {
    const colors = {
      error: 'bg-red-100 text-red-800 border-red-200',
      warning: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      info: 'bg-blue-100 text-blue-800 border-blue-200',
      success: 'bg-green-100 text-green-800 border-green-200',
    };

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium border ${colors[level as keyof typeof colors] || colors.info}`}>
        {level.toUpperCase()}
      </span>
    );
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
        <span className="ml-3 text-lg">Loading alerts...</span>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <Bell className="w-8 h-8 text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-900">System Alerts</h1>
        </div>
        <button
          onClick={() => {
            fetchAlerts();
            fetchStats();
          }}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
            <div className="text-sm font-medium text-gray-600">Total Alerts</div>
            <div className="text-2xl font-bold text-gray-900">{stats.total_alerts}</div>
          </div>

          <div className="bg-white rounded-lg shadow p-4 border-l-4 border-yellow-500">
            <div className="text-sm font-medium text-gray-600">Unread</div>
            <div className="text-2xl font-bold text-gray-900">{stats.unread_count}</div>
          </div>

          <div className="bg-white rounded-lg shadow p-4 border-l-4 border-red-500">
            <div className="text-sm font-medium text-gray-600">Errors (All Time)</div>
            <div className="text-2xl font-bold text-gray-900">{stats.levels.error}</div>
          </div>

          <div className="bg-white rounded-lg shadow p-4 border-l-4 border-orange-500">
            <div className="text-sm font-medium text-gray-600">Recent Errors (1h)</div>
            <div className="text-2xl font-bold text-gray-900">{stats.recent_errors_1h}</div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex flex-wrap items-center gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Level</label>
            <select
              value={filterLevel}
              onChange={(e) => setFilterLevel(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">All Levels</option>
              <option value="error">Error</option>
              <option value="warning">Warning</option>
              <option value="info">Info</option>
              <option value="success">Success</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">All Categories</option>
              <option value="api">API</option>
              <option value="agent">Agent</option>
              <option value="system">System</option>
              <option value="performance">Performance</option>
            </select>
          </div>

          <div className="flex items-center space-x-2 mt-6">
            <input
              type="checkbox"
              id="unreadOnly"
              checked={showUnreadOnly}
              onChange={(e) => setShowUnreadOnly(e.target.checked)}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label htmlFor="unreadOnly" className="text-sm font-medium text-gray-700">
              Show unread only
            </label>
          </div>

          {stats && stats.unread_count > 0 && (
            <button
              onClick={markAllAsRead}
              className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors mt-6"
            >
              <CheckCheck className="w-4 h-4" />
              <span>Mark All Read</span>
            </button>
          )}
        </div>
      </div>

      {/* Alerts List */}
      <div className="space-y-3">
        {alerts.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-600">No alerts to display</p>
          </div>
        ) : (
          alerts.map((alert) => (
            <div
              key={alert.id}
              className={`bg-white rounded-lg shadow p-4 border-l-4 ${
                alert.level === 'error'
                  ? 'border-red-500'
                  : alert.level === 'warning'
                  ? 'border-yellow-500'
                  : alert.level === 'success'
                  ? 'border-green-500'
                  : 'border-blue-500'
              } ${!alert.read ? 'bg-blue-50' : ''}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  <div className="mt-1">{getLevelIcon(alert.level)}</div>

                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      {getLevelBadge(alert.level)}
                      <span className="text-xs text-gray-500 font-medium uppercase">{alert.category}</span>
                      {alert.source && (
                        <span className="text-xs text-gray-400">• {alert.source}</span>
                      )}
                      {!alert.read && (
                        <span className="px-2 py-0.5 bg-blue-500 text-white text-xs rounded-full">
                          NEW
                        </span>
                      )}
                    </div>

                    <p className="text-gray-900 font-medium mb-1">{alert.message}</p>

                    {Object.keys(alert.details).length > 0 && (
                      <details className="text-sm text-gray-600 mt-2">
                        <summary className="cursor-pointer hover:text-gray-900">View details</summary>
                        <pre className="mt-2 p-2 bg-gray-100 rounded text-xs overflow-auto">
                          {JSON.stringify(alert.details, null, 2)}
                        </pre>
                      </details>
                    )}

                    <div className="text-xs text-gray-500 mt-2">{formatTimestamp(alert.timestamp)}</div>
                  </div>
                </div>

                {!alert.read && (
                  <button
                    onClick={() => markAsRead(alert.id)}
                    className="ml-4 px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors"
                  >
                    Mark Read
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default AlertsPage;
