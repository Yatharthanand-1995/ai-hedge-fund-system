import React from 'react';
import { cn } from '../../utils';

interface SkeletonLoaderProps {
  className?: string;
  variant?: 'card' | 'text' | 'circle' | 'button' | 'chart';
  lines?: number;
  height?: string;
}

/**
 * SkeletonLoader Component
 *
 * Provides placeholder UI while content is loading
 *
 * Usage:
 * <SkeletonLoader variant="card" />
 * <SkeletonLoader variant="text" lines={3} />
 */
export const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({
  className,
  variant = 'card',
  lines = 1,
  height
}) => {
  const baseClass = 'animate-pulse bg-gradient-to-r from-muted via-muted/50 to-muted bg-[length:200%_100%]';

  if (variant === 'text') {
    return (
      <div className={cn('space-y-2', className)}>
        {Array.from({ length: lines }).map((_, i) => (
          <div
            key={i}
            className={cn(
              baseClass,
              'h-4 rounded',
              i === lines - 1 && lines > 1 ? 'w-3/4' : 'w-full'
            )}
            style={{ height: height }}
          />
        ))}
      </div>
    );
  }

  if (variant === 'circle') {
    return (
      <div
        className={cn(baseClass, 'rounded-full', className)}
        style={{ width: height || '40px', height: height || '40px' }}
      />
    );
  }

  if (variant === 'button') {
    return (
      <div
        className={cn(baseClass, 'rounded-lg', className)}
        style={{ height: height || '40px', width: '120px' }}
      />
    );
  }

  if (variant === 'chart') {
    return (
      <div className={cn('space-y-4', className)}>
        <div className="flex items-end space-x-2 h-48">
          {Array.from({ length: 12 }).map((_, i) => (
            <div
              key={i}
              className={cn(baseClass, 'flex-1 rounded-t')}
              style={{ height: `${Math.random() * 80 + 20}%` }}
            />
          ))}
        </div>
      </div>
    );
  }

  // Default: card variant
  return (
    <div className={cn('professional-card p-6 space-y-4', className)}>
      <div className="flex items-center space-x-4">
        <div className={cn(baseClass, 'h-12 w-12 rounded-full')} />
        <div className="flex-1 space-y-2">
          <div className={cn(baseClass, 'h-4 w-3/4 rounded')} />
          <div className={cn(baseClass, 'h-3 w-1/2 rounded')} />
        </div>
      </div>
      <div className="space-y-2">
        <div className={cn(baseClass, 'h-3 w-full rounded')} />
        <div className={cn(baseClass, 'h-3 w-5/6 rounded')} />
        <div className={cn(baseClass, 'h-3 w-4/6 rounded')} />
      </div>
    </div>
  );
};

/**
 * Dashboard Skeleton - Specific skeleton for dashboard panels
 */
export const DashboardSkeleton: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <div className={cn('professional-card p-6', className)}>
      <div className="flex items-center justify-between mb-6">
        <SkeletonLoader variant="text" lines={1} height="24px" className="w-48" />
        <SkeletonLoader variant="button" height="32px" />
      </div>
      <div className="space-y-4">
        <SkeletonLoader variant="text" lines={3} />
        <SkeletonLoader variant="chart" />
        <div className="grid grid-cols-3 gap-4">
          <SkeletonLoader variant="text" lines={2} />
          <SkeletonLoader variant="text" lines={2} />
          <SkeletonLoader variant="text" lines={2} />
        </div>
      </div>
    </div>
  );
};

/**
 * Table Skeleton - Specific skeleton for data tables
 */
export const TableSkeleton: React.FC<{ rows?: number; columns?: number; className?: string }> = ({
  rows = 5,
  columns = 4,
  className
}) => {
  const baseClass = 'animate-pulse bg-gradient-to-r from-muted via-muted/50 to-muted bg-[length:200%_100%]';

  return (
    <div className={cn('space-y-2', className)}>
      {/* Header */}
      <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
        {Array.from({ length: columns }).map((_, i) => (
          <div key={`header-${i}`} className={cn(baseClass, 'h-8 rounded')} />
        ))}
      </div>
      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div
          key={`row-${rowIndex}`}
          className="grid gap-4"
          style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}
        >
          {Array.from({ length: columns }).map((_, colIndex) => (
            <div key={`cell-${rowIndex}-${colIndex}`} className={cn(baseClass, 'h-6 rounded')} />
          ))}
        </div>
      ))}
    </div>
  );
};
