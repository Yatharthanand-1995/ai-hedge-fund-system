import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { TrendingUp, TrendingDown, Activity } from 'lucide-react';
import { cn } from '../../utils';

interface MarketRegime {
  regime: string;
  trend: 'BULL' | 'BEAR' | 'SIDEWAYS';
  volatility: 'HIGH_VOL' | 'NORMAL_VOL' | 'LOW_VOL';
  adaptive_weights_enabled: boolean;
}

interface MarketRegimeBadgeProps {
  className?: string;
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const TREND_CONFIG = {
  BULL: {
    icon: TrendingUp,
    label: 'Bull',
    color: 'text-green-700',
    bgColor: 'bg-green-100',
    borderColor: 'border-green-300',
    emoji: '📈'
  },
  BEAR: {
    icon: TrendingDown,
    label: 'Bear',
    color: 'text-red-700',
    bgColor: 'bg-red-100',
    borderColor: 'border-red-300',
    emoji: '📉'
  },
  SIDEWAYS: {
    icon: Activity,
    label: 'Sideways',
    color: 'text-amber-700',
    bgColor: 'bg-amber-100',
    borderColor: 'border-amber-300',
    emoji: '↔️'
  }
};

const SIZE_CONFIG = {
  sm: {
    text: 'text-xs',
    padding: 'px-2 py-1',
    icon: 'h-3 w-3'
  },
  md: {
    text: 'text-sm',
    padding: 'px-3 py-1.5',
    icon: 'h-4 w-4'
  },
  lg: {
    text: 'text-base',
    padding: 'px-4 py-2',
    icon: 'h-5 w-5'
  }
};

export const MarketRegimeBadge: React.FC<MarketRegimeBadgeProps> = ({
  className,
  showLabel = true,
  size = 'md'
}) => {
  const { data: regime } = useQuery<MarketRegime>({
    queryKey: ['market-regime'],
    queryFn: async () => {
      const res = await fetch('http://localhost:8010/market/regime');
      if (!res.ok) throw new Error('Failed to fetch market regime');
      return res.json();
    },
    staleTime: 6 * 60 * 60 * 1000, // 6 hours
  });

  if (!regime) return null;

  const trendConfig = TREND_CONFIG[regime.trend];
  const sizeConfig = SIZE_CONFIG[size];
  const TrendIcon = trendConfig.icon;

  return (
    <div
      className={cn(
        'inline-flex items-center space-x-1.5 rounded-full border font-medium transition-all',
        trendConfig.bgColor,
        trendConfig.borderColor,
        trendConfig.color,
        sizeConfig.padding,
        sizeConfig.text,
        className
      )}
      title={`Market: ${regime.regime} ${regime.adaptive_weights_enabled ? '(Adaptive)' : ''}`}
    >
      <span className="text-sm">{trendConfig.emoji}</span>
      <TrendIcon className={sizeConfig.icon} />
      {showLabel && (
        <span className="font-semibold">{trendConfig.label}</span>
      )}
      {regime.adaptive_weights_enabled && size !== 'sm' && (
        <span className="opacity-75 text-xs ml-1">⚙️</span>
      )}
    </div>
  );
};
