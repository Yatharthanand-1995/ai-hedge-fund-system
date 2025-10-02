/**
 * Feature Flags Configuration
 *
 * Toggle experimental features on/off without breaking production
 * All flags default to false for safety
 */

export interface FeatureFlags {
  // Dashboard Versions
  USE_ENHANCED_DASHBOARD: boolean;

  // Component Enhancements
  USE_COMMAND_CENTER: boolean;
  USE_ADVANCED_CHARTS: boolean;
  USE_REAL_TIME_UPDATES: boolean;
  USE_ENHANCED_PORTFOLIO_VIEW: boolean;

  // Experimental Features
  USE_AI_CHAT_ASSISTANT: boolean;
  USE_CUSTOM_ALERTS: boolean;
  USE_DARK_MODE_TOGGLE: boolean;

  // Performance Features
  USE_INFINITE_SCROLL: boolean;
  USE_VIRTUAL_SCROLLING: boolean;

  // Debug Mode
  DEBUG_MODE: boolean;
}

// Default feature flags - all experimental features OFF
export const defaultFeatureFlags: FeatureFlags = {
  // Dashboard Versions
  USE_ENHANCED_DASHBOARD: false,

  // Component Enhancements
  USE_COMMAND_CENTER: true, // NEW - ON by default (ready for production)
  USE_ADVANCED_CHARTS: false,
  USE_REAL_TIME_UPDATES: false,
  USE_ENHANCED_PORTFOLIO_VIEW: false,

  // Experimental Features
  USE_AI_CHAT_ASSISTANT: false,
  USE_CUSTOM_ALERTS: false,
  USE_DARK_MODE_TOGGLE: false,

  // Performance Features
  USE_INFINITE_SCROLL: false,
  USE_VIRTUAL_SCROLLING: false,

  // Debug Mode
  DEBUG_MODE: false,
};

// Load flags from localStorage (persists across sessions)
const loadFeatureFlags = (): FeatureFlags => {
  // Check if we're in a browser environment
  if (typeof window === 'undefined' || typeof localStorage === 'undefined') {
    return defaultFeatureFlags;
  }

  try {
    const saved = localStorage.getItem('featureFlags');
    if (saved) {
      return { ...defaultFeatureFlags, ...JSON.parse(saved) };
    }
  } catch (error) {
    console.warn('Failed to load feature flags from localStorage:', error);
  }
  return defaultFeatureFlags;
};

// Save flags to localStorage
export const saveFeatureFlags = (flags: FeatureFlags): void => {
  if (typeof window === 'undefined' || typeof localStorage === 'undefined') {
    return;
  }

  try {
    localStorage.setItem('featureFlags', JSON.stringify(flags));
  } catch (error) {
    console.error('Failed to save feature flags to localStorage:', error);
  }
};

// Internal cache for feature flags (lazy loaded)
let _featureFlags: FeatureFlags | null = null;

// Get feature flags (lazy loaded on first access)
function getFeatureFlags(): FeatureFlags {
  if (_featureFlags === null) {
    _featureFlags = loadFeatureFlags();
  }
  return _featureFlags;
}

// Export current feature flags using Proxy for lazy loading
export const FEATURE_FLAGS = new Proxy({} as FeatureFlags, {
  get(_target, prop: string) {
    const flags = getFeatureFlags();
    return flags[prop as keyof FeatureFlags];
  }
});

// Update feature flags (used by settings UI)
export const updateFeatureFlags = (updates: Partial<FeatureFlags>): void => {
  const currentFlags = getFeatureFlags();
  _featureFlags = { ...currentFlags, ...updates };
  saveFeatureFlags(_featureFlags);

  // Trigger page reload to apply changes
  if (typeof window !== 'undefined') {
    window.location.reload();
  }
};

// Reset to defaults
export const resetFeatureFlags = (): void => {
  _featureFlags = { ...defaultFeatureFlags };
  saveFeatureFlags(_featureFlags);

  if (typeof window !== 'undefined') {
    window.location.reload();
  }
};

// Development mode detection
export const isDevelopment = import.meta.env.DEV;
export const isProduction = import.meta.env.PROD;

// Helper to check if any experimental features are enabled
export const hasExperimentalFeatures = (): boolean => {
  return Object.entries(FEATURE_FLAGS).some(
    ([key, value]) => key !== 'DEBUG_MODE' && value === true
  );
};
