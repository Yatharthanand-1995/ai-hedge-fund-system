import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { TrendingUp, TrendingDown, Activity, Loader2, RefreshCw, AlertCircle, ChevronRight } from 'lucide-react';
import { cn } from '../../utils';

interface MarketRegime {
  regime: string;
  trend: 'BULL' | 'BEAR' | 'SIDEWAYS';
  volatility: 'HIGH_VOL' | 'NORMAL_VOL' | 'LOW_VOL';
  weights: {
    fundamentals: number;
    momentum: number;
    quality: number;
    sentiment: number;
  };
  explanation: string;
  timestamp: string;
  cache_hit: boolean;
  adaptive_weights_enabled: boolean;
}

interface MarketRegimePanelProps {
  className?: string;
}

const TREND_CONFIG = {
  BULL: {
    icon: TrendingUp,
    color: 'text-green-600',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
    label: 'Bull Market',
    emoji: '📈'
  },
  BEAR: {
    icon: TrendingDown,
    color: 'text-red-600',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    label: 'Bear Market',
    emoji: '📉'
  },
  SIDEWAYS: {
    icon: Activity,
    color: 'text-amber-600',
    bgColor: 'bg-amber-50',
    borderColor: 'border-amber-200',
    label: 'Sideways Market',
    emoji: '↔️'
  }
};

const VOLATILITY_CONFIG = {
  HIGH_VOL: {
    label: 'High Volatility',
    color: 'text-red-600',
    bgColor: 'bg-red-100',
    emoji: '⚡'
  },
  NORMAL_VOL: {
    label: 'Normal Volatility',
    color: 'text-blue-600',
    bgColor: 'bg-blue-100',
    emoji: '🌊'
  },
  LOW_VOL: {
    label: 'Low Volatility',
    color: 'text-green-600',
    bgColor: 'bg-green-100',
    emoji: '🌤️'
  }
};

export const MarketRegimePanel: React.FC<MarketRegimePanelProps> = ({ className }) => {
  const { data: regime, isLoading, error, refetch, isRefetching } = useQuery<MarketRegime>({
    queryKey: ['market-regime'],
    queryFn: async () => {
      const res = await fetch('http://localhost:8010/market/regime');
      if (!res.ok) throw new Error('Failed to fetch market regime');
      return res.json();
    },
    staleTime: 6 * 60 * 60 * 1000, // 6 hours (matches backend cache)
    refetchInterval: 6 * 60 * 60 * 1000, // Auto-refresh every 6 hours
  });

  if (isLoading) {
    return (
      <div className={cn('bg-white border border-slate-200 rounded-lg p-6', className)}>
        <div className="flex items-center justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
          <span className="ml-2 text-slate-600">Loading market regime...</span>
        </div>
      </div>
    );
  }

  if (error || !regime) {
    return (
      <div className={cn('bg-white border border-slate-200 rounded-lg p-6', className)}>
        <div className="flex items-center text-red-600">
          <AlertCircle className="h-5 w-5 mr-2" />
          <span>Failed to load market regime</span>
        </div>
      </div>
    );
  }

  const trendConfig = TREND_CONFIG[regime.trend];
  const volConfig = VOLATILITY_CONFIG[regime.volatility];
  const TrendIcon = trendConfig.icon;

  // Calculate max weight for visualization
  const maxWeight = Math.max(...Object.values(regime.weights));

  return (
    <div className={cn('bg-white border border-slate-200 rounded-lg p-6 shadow-sm', className)}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Activity className="h-5 w-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-slate-900">Market Regime</h3>
          {regime.adaptive_weights_enabled && (
            <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-700 rounded-full">
              Adaptive
            </span>
          )}
        </div>
        <button
          onClick={() => refetch()}
          disabled={isRefetching}
          className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
          title="Refresh regime"
        >
          <RefreshCw className={cn('h-4 w-4 text-slate-600', isRefetching && 'animate-spin')} />
        </button>
      </div>

      {/* Current Regime Display */}
      <div className={cn('border rounded-lg p-4 mb-4', trendConfig.borderColor, trendConfig.bgColor)}>
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-3">
            <div className={cn('p-3 rounded-lg', trendConfig.bgColor)}>
              <TrendIcon className={cn('h-6 w-6', trendConfig.color)} />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-2xl">{trendConfig.emoji}</span>
                <h4 className={cn('text-lg font-bold', trendConfig.color)}>
                  {trendConfig.label}
                </h4>
              </div>
              <div className="flex items-center space-x-2 mt-1">
                <span className={cn('px-2 py-1 text-xs font-medium rounded', volConfig.bgColor, volConfig.color)}>
                  {volConfig.emoji} {volConfig.label}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Explanation */}
        <p className="mt-3 text-sm text-slate-700 leading-relaxed">
          {regime.explanation}
        </p>
      </div>

      {/* Adaptive Agent Weights */}
      <div>
        <h4 className="text-sm font-semibold text-slate-700 mb-3 flex items-center">
          <ChevronRight className="h-4 w-4 mr-1" />
          {regime.adaptive_weights_enabled ? 'Adaptive Agent Weights' : 'Static Agent Weights'}
        </h4>

        <div className="space-y-3">
          {/* Fundamentals */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm text-slate-600">Fundamentals</span>
              <span className="text-sm font-semibold text-slate-900">
                {(regime.weights.fundamentals * 100).toFixed(0)}%
              </span>
            </div>
            <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
              <div
                className={cn(
                  'h-full rounded-full transition-all duration-500',
                  regime.weights.fundamentals === maxWeight ? 'bg-blue-600' : 'bg-blue-400'
                )}
                style={{ width: `${regime.weights.fundamentals * 100}%` }}
              />
            </div>
          </div>

          {/* Momentum */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm text-slate-600">Momentum</span>
              <span className="text-sm font-semibold text-slate-900">
                {(regime.weights.momentum * 100).toFixed(0)}%
              </span>
            </div>
            <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
              <div
                className={cn(
                  'h-full rounded-full transition-all duration-500',
                  regime.weights.momentum === maxWeight ? 'bg-purple-600' : 'bg-purple-400'
                )}
                style={{ width: `${regime.weights.momentum * 100}%` }}
              />
            </div>
          </div>

          {/* Quality */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm text-slate-600">Quality</span>
              <span className="text-sm font-semibold text-slate-900">
                {(regime.weights.quality * 100).toFixed(0)}%
              </span>
            </div>
            <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
              <div
                className={cn(
                  'h-full rounded-full transition-all duration-500',
                  regime.weights.quality === maxWeight ? 'bg-green-600' : 'bg-green-400'
                )}
                style={{ width: `${regime.weights.quality * 100}%` }}
              />
            </div>
          </div>

          {/* Sentiment */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm text-slate-600">Sentiment</span>
              <span className="text-sm font-semibold text-slate-900">
                {(regime.weights.sentiment * 100).toFixed(0)}%
              </span>
            </div>
            <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
              <div
                className={cn(
                  'h-full rounded-full transition-all duration-500',
                  regime.weights.sentiment === maxWeight ? 'bg-amber-600' : 'bg-amber-400'
                )}
                style={{ width: `${regime.weights.sentiment * 100}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Cache Info */}
      <div className="mt-4 pt-4 border-t border-slate-200">
        <div className="flex items-center justify-between text-xs text-slate-500">
          <span>
            {regime.cache_hit ? '✓ Cached' : '⟳ Fresh'} • Updated {new Date(regime.timestamp).toLocaleTimeString()}
          </span>
          <span className="text-slate-400">Refreshes every 6h</span>
        </div>
      </div>
    </div>
  );
};
