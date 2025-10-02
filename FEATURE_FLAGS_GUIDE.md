# Feature Flags System - Developer Guide

## Overview

The feature flags system allows you to safely experiment with dashboard improvements without breaking the production version. All experimental features are OFF by default and can be toggled via the UI.

## Quick Start

### 1. Accessing Feature Flags

Click the **⚙️ Settings** icon in the navigation bar to open the Feature Flags panel.

### 2. Toggling Features

- Toggle any feature on/off by clicking the switch button
- Click **"Apply & Reload"** to activate changes
- The page will automatically reload with new settings

### 3. Branch Strategy

```bash
# Current branch (for experimental work)
dashboard-v2-improvements

# Stable branch (fallback if needed)
git checkout dashboard-real-data-integration
```

## Feature Categories

### 🎨 Dashboard Versions
- **Enhanced Dashboard** - New improved dashboard layout with better UX

### 🎯 Component Enhancements
- **Advanced Charts** - Enhanced chart visualizations with more data
- **Real-Time Updates** - Live data streaming (requires WebSocket)
- **Enhanced Portfolio View** - Improved portfolio display with better metrics

### 🧪 Experimental Features
- **AI Chat Assistant** - Interactive AI helper for investment questions
- **Custom Alerts** - Personalized price/event notifications
- **Dark Mode Toggle** - Manual theme switching

### ⚡ Performance Features
- **Infinite Scroll** - Automatic content loading as you scroll
- **Virtual Scrolling** - Optimized rendering for large lists

### 🐛 Debug
- **Debug Mode** - Show debug information in console

## How to Add a New Experimental Feature

### Step 1: Add Feature Flag

Edit `frontend/src/config/featureFlags.ts`:

```typescript
export const defaultFeatureFlags: FeatureFlags = {
  // ... existing flags
  USE_MY_NEW_FEATURE: false, // Add your flag
};
```

### Step 2: Update Feature Flags Panel

Edit `frontend/src/components/settings/FeatureFlagsPanel.tsx`:

```typescript
const featureCategories = {
  'Your Category': [
    {
      key: 'USE_MY_NEW_FEATURE',
      label: 'My New Feature',
      description: 'Description of what it does'
    },
  ],
  // ... existing categories
};
```

### Step 3: Use in Components

```typescript
import { FEATURE_FLAGS } from '../../config/featureFlags';

function MyComponent() {
  return (
    <div>
      {FEATURE_FLAGS.USE_MY_NEW_FEATURE ? (
        <NewFeatureComponent />
      ) : (
        <OldStableComponent />
      )}
    </div>
  );
}
```

## Best Practices

### ✅ DO

1. **Default to OFF** - All new flags should be `false` by default
2. **Test Thoroughly** - Test both ON and OFF states
3. **Document Features** - Add clear descriptions in the settings panel
4. **Keep Stable Fallback** - Always maintain working fallback code
5. **Clean Up** - Remove flags once features are stable and merged

### ❌ DON'T

1. **Don't Break Stable** - Never push breaking changes to stable flags
2. **Don't Nest Too Deep** - Avoid complex nested flag logic
3. **Don't Forget Fallback** - Always provide a working alternative
4. **Don't Leave Dead Flags** - Clean up unused flags regularly

## Workflow Examples

### Scenario 1: Working on New Dashboard Layout

```bash
# You're on dashboard-v2-improvements branch
# Feature flag: USE_ENHANCED_DASHBOARD = false (default)

1. Make changes to dashboard components
2. Test with flag OFF (should work normally)
3. Toggle flag ON via settings
4. Test new dashboard
5. If broken, toggle OFF to continue working
6. When stable, set default to true and merge
```

### Scenario 2: Something Broke!

```bash
# Quick rollback options:

Option A: Toggle Feature Flag OFF
1. Click Settings icon
2. Turn off problematic feature
3. Apply & Reload
4. System restored to stable state

Option B: Switch Branch
git checkout dashboard-real-data-integration
# Reload browser - back to 100% stable version

Option C: Reset All Flags
1. Click Settings icon
2. Click "Reset to Defaults"
3. Confirm reload
4. All experimental features disabled
```

### Scenario 3: Ready to Merge

```bash
# Feature is stable and tested
1. Update defaultFeatureFlags to true
2. Test thoroughly with flag ON
3. Merge branch to main
4. Deploy
5. Remove flag after 1-2 weeks of stability
```

## Storage & Persistence

- **Storage**: Browser localStorage
- **Key**: `featureFlags`
- **Persistence**: Survives browser refresh, not shared between devices
- **Reset**: Settings panel → "Reset to Defaults"

## Debugging

### Check Current Flags

Open browser console:

```javascript
// View current flags
console.log(localStorage.getItem('featureFlags'));

// Manually set a flag
localStorage.setItem('featureFlags', JSON.stringify({
  USE_ENHANCED_DASHBOARD: true
}));
location.reload();

// Clear all flags
localStorage.removeItem('featureFlags');
location.reload();
```

### Debug Mode

Enable **Debug Mode** flag to see:
- Feature flag states in console
- Component render counts
- API call logging
- Performance metrics

## Safety Checklist

Before enabling experimental features:

- [ ] Stable version is working
- [ ] You know how to toggle flags OFF
- [ ] You know how to switch branches
- [ ] Backend API is running
- [ ] You've saved any important work

## Support

If you encounter issues:

1. **Toggle flag OFF** in settings
2. **Switch to stable branch**: `git checkout dashboard-real-data-integration`
3. **Reset flags** via settings panel
4. **Clear browser cache** if settings don't persist

## Future Enhancements

Planned improvements to the feature flag system:

- [ ] A/B testing support
- [ ] Per-user flag overrides
- [ ] Remote flag management
- [ ] Analytics integration
- [ ] Gradual rollout (10% → 50% → 100%)
- [ ] Scheduled flag activation

---

**Remember**: The goal is to move fast without breaking things. Feature flags let you experiment confidently while keeping a stable fallback always available.
