import React, { useState, useEffect } from 'react';
import { Clock, ShoppingCart, TrendingUp, AlertCircle, CheckCircle, Calendar } from 'lucide-react';
import { cn, formatCurrency } from '../../utils';

interface QueuedBuy {
  symbol: string;
  queued_at: string;
  signal: string;
  score: number;
  price: number | null;
  reason: string;
}

interface BuyQueueStatus {
  success: boolean;
  queued_buys: QueuedBuy[];
  count: number;
  next_execution: string;
  batch_mode_enabled: boolean;
  queue_file: string;
}

interface AutoBuyStatusPanelProps {
  className?: string;
}

export const AutoBuyStatusPanel: React.FC<AutoBuyStatusPanelProps> = ({ className }) => {
  const [queueStatus, setQueueStatus] = useState<BuyQueueStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchQueueStatus();
    // Refresh every 30 seconds
    const interval = setInterval(fetchQueueStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchQueueStatus = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('http://localhost:8010/portfolio/paper/auto-buy/queue');
      if (!response.ok) {
        throw new Error('Failed to fetch buy queue status');
      }

      const data = await response.json();
      setQueueStatus(data);
    } catch (err) {
      console.error('Failed to fetch buy queue:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const getTimeAgo = (timestamp: string): string => {
    const queued = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - queued.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins}m ago`;

    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;

    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
  };

  const getSignalColor = (signal: string): string => {
    if (signal === 'STRONG BUY') return 'text-green-600 bg-green-50';
    if (signal === 'BUY') return 'text-blue-600 bg-blue-50';
    return 'text-gray-600 bg-gray-50';
  };

  if (loading && !queueStatus) {
    return (
      <div className={cn(
        'bg-white/60 backdrop-blur-lg rounded-xl border border-gray-200/50 p-6',
        className
      )}>
        <div className="flex items-center space-x-2 mb-4">
          <ShoppingCart className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">Auto-Buy Queue</h3>
        </div>
        <div className="text-center py-8 text-gray-500">
          Loading queue status...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={cn(
        'bg-white/60 backdrop-blur-lg rounded-xl border border-gray-200/50 p-6',
        className
      )}>
        <div className="flex items-center space-x-2 mb-4">
          <ShoppingCart className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">Auto-Buy Queue</h3>
        </div>
        <div className="flex items-center space-x-2 text-red-600">
          <AlertCircle className="w-5 h-5" />
          <span>{error}</span>
        </div>
      </div>
    );
  }

  const hasQueuedBuys = queueStatus && queueStatus.count > 0;

  return (
    <div className={cn(
      'bg-white/60 backdrop-blur-lg rounded-xl border border-gray-200/50 p-6',
      className
    )}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <ShoppingCart className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">Auto-Buy Queue</h3>
        </div>

        {hasQueuedBuys && (
          <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-100 text-blue-700">
            <Clock className="w-4 h-4" />
            <span className="text-sm font-medium">{queueStatus.count} queued</span>
          </div>
        )}
      </div>

      {/* Batch Execution Info */}
      {queueStatus?.batch_mode_enabled && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center space-x-2 text-blue-900">
            <Calendar className="w-4 h-4" />
            <span className="text-sm font-medium">
              Next Execution: {queueStatus.next_execution}
            </span>
          </div>
          <p className="text-xs text-blue-700 mt-1 ml-6">
            Batch execution optimizes pricing and reduces slippage
          </p>
        </div>
      )}

      {/* Queue Status */}
      {!hasQueuedBuys ? (
        <div className="text-center py-8">
          <CheckCircle className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500 font-medium">No pending buy opportunities</p>
          <p className="text-sm text-gray-400 mt-1">
            System will queue STRONG BUY signals here for batch execution
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {queueStatus.queued_buys.map((buy, index) => (
            <div
              key={`${buy.symbol}-${index}`}
              className="p-4 bg-gradient-to-r from-blue-50 to-white border border-blue-100 rounded-lg hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  {/* Symbol and Signal */}
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="text-lg font-bold text-gray-900">{buy.symbol}</span>
                    <span className={cn(
                      'px-2 py-0.5 rounded-full text-xs font-medium',
                      getSignalColor(buy.signal)
                    )}>
                      {buy.signal}
                    </span>
                  </div>

                  {/* Score and Price */}
                  <div className="flex items-center space-x-4 mb-2">
                    <div className="flex items-center space-x-1">
                      <TrendingUp className="w-4 h-4 text-green-600" />
                      <span className="text-sm font-medium text-gray-700">
                        Score: {buy.score.toFixed(1)}
                      </span>
                    </div>
                    {buy.price && (
                      <span className="text-sm text-gray-600">
                        @ {formatCurrency(buy.price)}
                      </span>
                    )}
                  </div>

                  {/* Reason */}
                  {buy.reason && (
                    <p className="text-xs text-gray-600 mb-2">{buy.reason}</p>
                  )}

                  {/* Queued Time */}
                  <div className="flex items-center space-x-1 text-xs text-gray-500">
                    <Clock className="w-3 h-3" />
                    <span>Queued {getTimeAgo(buy.queued_at)}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}

          {/* Summary Footer */}
          <div className="pt-3 mt-3 border-t border-gray-200">
            <div className="text-sm text-gray-600 text-center">
              {queueStatus.count} {queueStatus.count === 1 ? 'opportunity' : 'opportunities'} will be executed at market close
            </div>
          </div>
        </div>
      )}

      {/* Manual Refresh Button */}
      <button
        onClick={fetchQueueStatus}
        className="mt-4 w-full px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
        disabled={loading}
      >
        {loading ? 'Refreshing...' : 'Refresh Queue'}
      </button>
    </div>
  );
};
