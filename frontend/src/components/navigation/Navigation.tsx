import React, { useState } from 'react';
import { Settings } from 'lucide-react';
import { cn } from '../../utils';
import { FeatureFlagsPanel } from '../settings/FeatureFlagsPanel';
import { hasExperimentalFeatures } from '../../config/featureFlags';

interface NavigationProps {
  currentPage: 'dashboard' | 'analysis' | 'portfolio' | 'backtesting';
  onPageChange: (page: 'dashboard' | 'analysis' | 'portfolio' | 'backtesting') => void;
}

export const Navigation: React.FC<NavigationProps> = ({
  currentPage,
  onPageChange,
}) => {
  const [showSettings, setShowSettings] = useState(false);
  const hasExperimental = hasExperimentalFeatures();

  const navItems = [
    { id: 'dashboard' as const, label: 'System Overview', icon: '🏦' },
    { id: 'analysis' as const, label: 'Stock Analysis', icon: '📊' },
    { id: 'portfolio' as const, label: 'Portfolio Manager', icon: '📈' },
    { id: 'backtesting' as const, label: '5-Year Backtest', icon: '📉' },
  ];

  return (
    <>
      <nav className="professional-card p-4 mb-8">
        <div className="flex items-center justify-between">
          <div className="flex flex-wrap gap-2">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => onPageChange(item.id)}
                className={cn(
                  'flex items-center space-x-2 px-4 py-2 rounded-lg transition-all',
                  'font-medium text-sm',
                  currentPage === item.id
                    ? 'bg-accent text-accent-foreground'
                    : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                )}
              >
                <span>{item.icon}</span>
                <span>{item.label}</span>
              </button>
            ))}
          </div>

          {/* Settings Button */}
          <div className="flex items-center space-x-2">
            {hasExperimental && (
              <span className="text-xs bg-yellow-500/20 text-yellow-500 px-2 py-1 rounded">
                Beta Mode
              </span>
            )}
            <button
              onClick={() => setShowSettings(true)}
              className={cn(
                'flex items-center space-x-2 px-3 py-2 rounded-lg transition-all',
                'text-muted-foreground hover:text-foreground hover:bg-muted',
                hasExperimental && 'ring-2 ring-yellow-500/30'
              )}
              title="Feature Flags & Settings"
            >
              <Settings className="h-5 w-5" />
            </button>
          </div>
        </div>
      </nav>

      {/* Settings Panel */}
      <FeatureFlagsPanel isOpen={showSettings} onClose={() => setShowSettings(false)} />
    </>
  );
};