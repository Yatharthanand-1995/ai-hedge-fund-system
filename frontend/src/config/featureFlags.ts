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
  try {
    localStorage.setItem('featureFlags', JSON.stringify(flags));
  } catch (error) {
    console.error('Failed to save feature flags to localStorage:', error);
  }
};

// Export current feature flags
export let FEATURE_FLAGS = loadFeatureFlags();

// Update feature flags (used by settings UI)
export const updateFeatureFlags = (updates: Partial<FeatureFlags>): void => {
  FEATURE_FLAGS = { ...FEATURE_FLAGS, ...updates };
  saveFeatureFlags(FEATURE_FLAGS);

  // Trigger page reload to apply changes
  if (typeof window !== 'undefined') {
    window.location.reload();
  }
};

// Reset to defaults
export const resetFeatureFlags = (): void => {
  FEATURE_FLAGS = { ...defaultFeatureFlags };
  saveFeatureFlags(FEATURE_FLAGS);

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
