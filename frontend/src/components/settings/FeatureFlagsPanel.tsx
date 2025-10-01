import React, { useState } from 'react';
import { Settings, ToggleLeft, ToggleRight, AlertTriangle, RefreshCw } from 'lucide-react';
import { FEATURE_FLAGS, updateFeatureFlags, resetFeatureFlags, hasExperimentalFeatures, type FeatureFlags } from '../../config/featureFlags';
import { cn } from '../../utils';

interface FeatureFlagsPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export const FeatureFlagsPanel: React.FC<FeatureFlagsPanelProps> = ({ isOpen, onClose }) => {
  const [flags, setFlags] = useState<FeatureFlags>(FEATURE_FLAGS);

  const toggleFlag = (key: keyof FeatureFlags) => {
    const newFlags = { ...flags, [key]: !flags[key] };
    setFlags(newFlags);
  };

  const handleApply = () => {
    updateFeatureFlags(flags);
    // Page will reload automatically
  };

  const handleReset = () => {
    if (confirm('Reset all feature flags to defaults? This will reload the page.')) {
      resetFeatureFlags();
    }
  };

  if (!isOpen) return null;

  const featureCategories = {
    'Dashboard Versions': [
      { key: 'USE_ENHANCED_DASHBOARD', label: 'Enhanced Dashboard', description: 'New improved dashboard layout' },
    ],
    'Component Enhancements': [
      { key: 'USE_ADVANCED_CHARTS', label: 'Advanced Charts', description: 'Enhanced chart visualizations' },
      { key: 'USE_REAL_TIME_UPDATES', label: 'Real-Time Updates', description: 'Live data streaming' },
      { key: 'USE_ENHANCED_PORTFOLIO_VIEW', label: 'Enhanced Portfolio', description: 'Improved portfolio display' },
    ],
    'Experimental Features': [
      { key: 'USE_AI_CHAT_ASSISTANT', label: 'AI Chat Assistant', description: 'Interactive AI helper' },
      { key: 'USE_CUSTOM_ALERTS', label: 'Custom Alerts', description: 'Personalized notifications' },
      { key: 'USE_DARK_MODE_TOGGLE', label: 'Dark Mode Toggle', description: 'Manual theme switching' },
    ],
    'Performance': [
      { key: 'USE_INFINITE_SCROLL', label: 'Infinite Scroll', description: 'Automatic content loading' },
      { key: 'USE_VIRTUAL_SCROLLING', label: 'Virtual Scrolling', description: 'Optimized list rendering' },
    ],
    'Debug': [
      { key: 'DEBUG_MODE', label: 'Debug Mode', description: 'Show debug information' },
    ],
  };

  const hasChanges = JSON.stringify(flags) !== JSON.stringify(FEATURE_FLAGS);
  const hasExperimental = hasExperimentalFeatures();

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="professional-card max-w-4xl max-h-[90vh] overflow-y-auto m-4 p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <Settings className="h-6 w-6 text-accent" />
            <div>
              <h2 className="text-2xl font-bold text-foreground">Feature Flags</h2>
              <p className="text-sm text-muted-foreground">
                Toggle experimental features on/off
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Warning Banner */}
        {hasExperimental && (
          <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4 mb-6 flex items-start space-x-3">
            <AlertTriangle className="h-5 w-5 text-yellow-500 mt-0.5 flex-shrink-0" />
            <div className="text-sm">
              <div className="font-semibold text-yellow-500 mb-1">Experimental Features Enabled</div>
              <div className="text-muted-foreground">
                Some features are experimental and may be unstable. Switch back to the stable version anytime.
              </div>
            </div>
          </div>
        )}

        {/* Feature Categories */}
        <div className="space-y-6">
          {Object.entries(featureCategories).map(([category, features]) => (
            <div key={category}>
              <h3 className="text-lg font-semibold text-foreground mb-3">{category}</h3>
              <div className="space-y-2">
                {features.map(({ key, label, description }) => {
                  const isEnabled = flags[key as keyof FeatureFlags];
                  return (
                    <div
                      key={key}
                      className="professional-card bg-muted/20 p-4 flex items-center justify-between"
                    >
                      <div className="flex-1">
                        <div className="font-medium text-foreground">{label}</div>
                        <div className="text-sm text-muted-foreground">{description}</div>
                      </div>
                      <button
                        onClick={() => toggleFlag(key as keyof FeatureFlags)}
                        className={cn(
                          'ml-4 p-2 rounded-lg transition-all',
                          isEnabled
                            ? 'bg-accent text-accent-foreground hover:bg-accent/80'
                            : 'bg-muted text-muted-foreground hover:bg-muted/80'
                        )}
                      >
                        {isEnabled ? (
                          <ToggleRight className="h-6 w-6" />
                        ) : (
                          <ToggleLeft className="h-6 w-6" />
                        )}
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-between mt-8 pt-6 border-t border-border">
          <button
            onClick={handleReset}
            className="flex items-center space-x-2 px-4 py-2 rounded-lg border border-border hover:bg-muted/20 transition-colors text-muted-foreground"
          >
            <RefreshCw className="h-4 w-4" />
            <span>Reset to Defaults</span>
          </button>

          <div className="flex items-center space-x-3">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-lg border border-border hover:bg-muted/20 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleApply}
              disabled={!hasChanges}
              className={cn(
                'px-6 py-2 rounded-lg font-medium transition-all',
                hasChanges
                  ? 'bg-accent text-accent-foreground hover:bg-accent/80'
                  : 'bg-muted text-muted-foreground cursor-not-allowed'
              )}
            >
              {hasChanges ? 'Apply & Reload' : 'No Changes'}
            </button>
          </div>
        </div>

        {/* Info Footer */}
        <div className="mt-4 pt-4 border-t border-border text-xs text-muted-foreground">
          <p>
            💡 <strong>Tip:</strong> Changes are saved in your browser and persist across sessions.
            You can always reset to defaults or switch back to the previous branch.
          </p>
        </div>
      </div>
    </div>
  );
};
