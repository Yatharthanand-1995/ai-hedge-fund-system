import React, { useState, useEffect } from 'react';
import { Settings } from 'lucide-react';
import { cn } from '../../utils';
import { FeatureFlagsPanel } from '../settings/FeatureFlagsPanel';
import { hasExperimentalFeatures } from '../../config/featureFlags';

interface NavigationProps {
  currentPage: 'dashboard' | 'analysis' | 'portfolio' | 'backtesting' | 'paper-trading' | 'system-details' | 'alerts';
  onPageChange: (page: 'dashboard' | 'analysis' | 'portfolio' | 'backtesting' | 'paper-trading' | 'system-details' | 'alerts') => void;
}

export const Navigation: React.FC<NavigationProps> = ({
  currentPage,
  onPageChange,
}) => {
  const [showSettings, setShowSettings] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const hasExperimental = hasExperimentalFeatures();

  const navItems = [
    { id: 'dashboard' as const, label: 'System Overview', icon: '🏦', shortcut: '1' },
    { id: 'analysis' as const, label: 'Stock Analysis', icon: '📊', shortcut: '2' },
    { id: 'portfolio' as const, label: 'Portfolio Manager', icon: '📈', shortcut: '3' },
    { id: 'backtesting' as const, label: '5-Year Backtest', icon: '📉', shortcut: '4' },
    { id: 'paper-trading' as const, label: 'Paper Trading', icon: '💵', shortcut: '5' },
    { id: 'alerts' as const, label: 'System Alerts', icon: '🔔', shortcut: '6' },
    { id: 'system-details' as const, label: 'System Details', icon: '📚', shortcut: '7' },
  ];

  // Keyboard navigation support
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      // Only trigger if Alt/Option key is pressed with number
      if (e.altKey && !e.ctrlKey && !e.metaKey) {
        const item = navItems.find(item => item.shortcut === e.key);
        if (item && item.id !== currentPage) {
          e.preventDefault();
          handlePageChange(item.id);
        }
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentPage]);

  const handlePageChange = (page: typeof currentPage) => {
    if (page === currentPage || isTransitioning) return;

    setIsTransitioning(true);
    onPageChange(page);

    // Reset transition state after animation
    setTimeout(() => setIsTransitioning(false), 300);
  };

  return (
    <>
      <nav className="professional-card p-4 mb-8">
        <div className="flex items-center justify-between">
          <div className="flex flex-wrap gap-2">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => handlePageChange(item.id)}
                disabled={isTransitioning}
                className={cn(
                  'flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200',
                  'font-medium text-sm relative group',
                  currentPage === item.id
                    ? 'bg-accent text-accent-foreground shadow-md scale-105'
                    : 'text-muted-foreground hover:text-foreground hover:bg-muted hover:scale-102',
                  isTransitioning && 'opacity-50 cursor-not-allowed'
                )}
                title={`${item.label} (Alt+${item.shortcut})`}
              >
                <span className="text-base">{item.icon}</span>
                <span>{item.label}</span>

                {/* Active indicator */}
                {currentPage === item.id && (
                  <span className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-1/2 h-0.5 bg-accent rounded-full" />
                )}

                {/* Keyboard shortcut hint */}
                <span className="hidden group-hover:inline-block text-xs opacity-50 ml-1">
                  ⌥{item.shortcut}
                </span>
              </button>
            ))}
          </div>

          {/* Settings Button */}
          <div className="flex items-center space-x-2">
            {hasExperimental && (
              <span className="text-xs bg-yellow-500/20 text-yellow-500 px-2 py-1 rounded animate-pulse">
                Beta Mode
              </span>
            )}
            <button
              onClick={() => setShowSettings(true)}
              className={cn(
                'flex items-center space-x-2 px-3 py-2 rounded-lg transition-all duration-200',
                'text-muted-foreground hover:text-foreground hover:bg-muted hover:scale-105',
                hasExperimental && 'ring-2 ring-yellow-500/30'
              )}
              title="Feature Flags & Settings (Alt+S)"
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