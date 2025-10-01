import React, { useState, useEffect } from 'react';
import { AlertTriangle, TrendingUp, TrendingDown, CheckCircle, Clock, X, Bell, Target, Activity } from 'lucide-react';
import { cn } from '../../utils';

interface ActionItem {
  id: string;
  type: 'urgent' | 'important' | 'normal';
  category: 'price_alert' | 'buy_signal' | 'sell_signal' | 'rebalance' | 'review' | 'risk_alert';
  symbol?: string;
  title: string;
  description: string;
  action: {
    label: string;
    type: 'buy' | 'sell' | 'review' | 'dismiss';
    data?: any;
  };
  timestamp: string;
  dismissed?: boolean;
}

interface CommandCenterProps {
  className?: string;
  onPageChange?: (page: 'dashboard' | 'analysis' | 'portfolio' | 'backtesting') => void;
}

export const CommandCenter: React.FC<CommandCenterProps> = ({ className, onPageChange }) => {
  const [actionItems, setActionItems] = useState<ActionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [dismissedItems, setDismissedItems] = useState<Set<string>>(new Set());

  useEffect(() => {
    fetchActionItems();
    // Refresh every 5 minutes
    const interval = setInterval(fetchActionItems, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const fetchActionItems = async () => {
    try {
      setLoading(true);

      // Fetch top picks and portfolio summary
      const [picksResponse, summaryResponse] = await Promise.all([
        fetch('http://localhost:8010/portfolio/top-picks?limit=10'),
        fetch('http://localhost:8010/portfolio/summary')
      ]);

      if (!picksResponse.ok || !summaryResponse.ok) {
        throw new Error('Failed to fetch data');
      }

      const picks = await picksResponse.json();
      const summary = await summaryResponse.json();

      // Generate action items from data
      const items = generateActionItems(picks.top_picks || [], summary);
      setActionItems(items);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch action items:', error);
      setLoading(false);
    }
  };

  const generateActionItems = (topPicks: any[], summary: any): ActionItem[] => {
    const items: ActionItem[] = [];
    const now = new Date().toISOString();

    // Risk alerts (URGENT)
    if (summary.riskLevel === 'high') {
      items.push({
        id: 'risk-alert-1',
        type: 'urgent',
        category: 'risk_alert',
        title: '⚠️ High Portfolio Risk Detected',
        description: 'Your portfolio risk level is HIGH. Consider rebalancing or reducing exposure.',
        action: {
          label: 'Review Risk',
          type: 'review',
          data: { page: 'portfolio' }
        },
        timestamp: now
      });
    }

    // Strong buy signals (IMPORTANT)
    const strongBuys = topPicks.filter(pick => pick.overall_score >= 75).slice(0, 2);
    strongBuys.forEach((pick, index) => {
      items.push({
        id: `buy-signal-${pick.symbol}`,
        type: 'important',
        category: 'buy_signal',
        symbol: pick.symbol,
        title: `🟢 Strong Buy Signal: ${pick.symbol}`,
        description: `Score: ${pick.overall_score.toFixed(1)} | Price: $${pick.market_data.current_price.toFixed(2)} | High confidence opportunity`,
        action: {
          label: 'View Analysis',
          type: 'review',
          data: { symbol: pick.symbol, page: 'analysis' }
        },
        timestamp: now
      });
    });

    // Price alerts - stocks near key levels (URGENT)
    topPicks.slice(0, 5).forEach(pick => {
      const priceChange = pick.market_data.price_change_percent || 0;

      // Large price movement
      if (Math.abs(priceChange) >= 5) {
        items.push({
          id: `price-alert-${pick.symbol}`,
          type: 'urgent',
          category: 'price_alert',
          symbol: pick.symbol,
          title: `📊 ${pick.symbol} Major Move: ${priceChange > 0 ? '↑' : '↓'}${Math.abs(priceChange).toFixed(1)}%`,
          description: `${pick.symbol} moved significantly. Current: $${pick.market_data.current_price.toFixed(2)}. Review position.`,
          action: {
            label: 'Check Details',
            type: 'review',
            data: { symbol: pick.symbol }
          },
          timestamp: now
        });
      }
    });

    // Weak performers (sell signals)
    const weakPerformers = topPicks.filter(pick => pick.overall_score < 50).slice(0, 2);
    weakPerformers.forEach(pick => {
      items.push({
        id: `sell-signal-${pick.symbol}`,
        type: 'important',
        category: 'sell_signal',
        symbol: pick.symbol,
        title: `🔴 Weak Performance: ${pick.symbol}`,
        description: `Score: ${pick.overall_score.toFixed(1)} | Consider reducing exposure or exiting position`,
        action: {
          label: 'Review Position',
          type: 'review',
          data: { symbol: pick.symbol }
        },
        timestamp: now
      });
    });

    // Portfolio rebalance needed (IMPORTANT)
    if (summary.actionsRequired > 0) {
      items.push({
        id: 'rebalance-1',
        type: 'important',
        category: 'rebalance',
        title: `⚖️ Portfolio Rebalance Recommended`,
        description: `${summary.actionsRequired} actions required. Sector allocation may need adjustment.`,
        action: {
          label: 'Review Portfolio',
          type: 'review',
          data: { page: 'portfolio' }
        },
        timestamp: now
      });
    }

    // Daily market regime info (NORMAL)
    items.push({
      id: 'market-regime-1',
      type: 'normal',
      category: 'review',
      title: `📈 Market Status: ${summary.marketRegime?.toUpperCase() || 'NORMAL'}`,
      description: `AI Confidence: ${summary.aiConfidenceIndex}/10 | Active positions: ${summary.activePositions}`,
      action: {
        label: 'View Dashboard',
        type: 'review',
        data: { page: 'dashboard' }
      },
      timestamp: now
    });

    // Sort by priority: urgent → important → normal
    return items.sort((a, b) => {
      const priority = { urgent: 0, important: 1, normal: 2 };
      return priority[a.type] - priority[b.type];
    });
  };

  const handleAction = (item: ActionItem) => {
    console.log('Action clicked:', item);

    // Navigate to specific pages
    if (item.action.data?.page && onPageChange) {
      const page = item.action.data.page as 'dashboard' | 'analysis' | 'portfolio' | 'backtesting';
      onPageChange(page);
      return;
    }

    // Navigate to analysis page for stock symbols
    if (item.action.data?.symbol && onPageChange) {
      // For now, navigate to analysis page
      // In the future, could open a modal with the specific stock
      onPageChange('analysis');
      return;
    }

    // Trading actions (future implementation)
    if (item.action.type === 'buy' || item.action.type === 'sell') {
      alert(`${item.action.type.toUpperCase()} action for ${item.symbol} - Trading integration coming soon!`);
    }
  };

  const handleDismiss = (itemId: string) => {
    setDismissedItems(prev => new Set([...prev, itemId]));
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'urgent': return <AlertTriangle className="h-5 w-5 text-red-500" />;
      case 'important': return <Bell className="h-5 w-5 text-yellow-500" />;
      default: return <Activity className="h-5 w-5 text-blue-500" />;
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'buy_signal': return <TrendingUp className="h-4 w-4 text-green-500" />;
      case 'sell_signal': return <TrendingDown className="h-4 w-4 text-red-500" />;
      case 'price_alert': return <Target className="h-4 w-4 text-orange-500" />;
      case 'risk_alert': return <AlertTriangle className="h-4 w-4 text-red-500" />;
      case 'rebalance': return <Activity className="h-4 w-4 text-blue-500" />;
      default: return <CheckCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'urgent': return 'border-l-red-500 bg-red-500/5';
      case 'important': return 'border-l-yellow-500 bg-yellow-500/5';
      default: return 'border-l-blue-500 bg-blue-500/5';
    }
  };

  const visibleItems = actionItems.filter(item => !dismissedItems.has(item.id));
  const urgentCount = visibleItems.filter(i => i.type === 'urgent').length;
  const importantCount = visibleItems.filter(i => i.type === 'important').length;

  if (loading) {
    return (
      <div className={cn('professional-card p-6', className)}>
        <div className="flex items-center space-x-3">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-accent"></div>
          <span className="text-muted-foreground">Loading action items...</span>
        </div>
      </div>
    );
  }

  if (visibleItems.length === 0) {
    return (
      <div className={cn('professional-card p-6', className)}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-foreground flex items-center space-x-2">
            <CheckCircle className="h-6 w-6 text-green-500" />
            <span>Command Center</span>
          </h2>
        </div>
        <div className="text-center py-8 text-muted-foreground">
          <CheckCircle className="h-12 w-12 mx-auto mb-3 text-green-500" />
          <p className="text-lg font-medium">All Clear! 🎉</p>
          <p className="text-sm">No urgent actions required at this time.</p>
        </div>
      </div>
    );
  }

  return (
    <div className={cn('professional-card p-6', className)}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-foreground flex items-center space-x-3">
          <Target className="h-6 w-6 text-accent" />
          <span>Command Center</span>
          {(urgentCount > 0 || importantCount > 0) && (
            <div className="flex items-center space-x-2 text-sm font-normal">
              {urgentCount > 0 && (
                <span className="bg-red-500/20 text-red-500 px-2 py-1 rounded">
                  {urgentCount} Urgent
                </span>
              )}
              {importantCount > 0 && (
                <span className="bg-yellow-500/20 text-yellow-500 px-2 py-1 rounded">
                  {importantCount} Important
                </span>
              )}
            </div>
          )}
        </h2>
        <button
          onClick={fetchActionItems}
          className="text-sm text-muted-foreground hover:text-foreground transition-colors flex items-center space-x-1"
        >
          <Clock className="h-4 w-4" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Action Items */}
      <div className="space-y-3">
        {visibleItems.slice(0, 5).map((item) => (
          <div
            key={item.id}
            className={cn(
              'professional-card p-4 border-l-4 transition-all hover:shadow-md',
              getTypeColor(item.type)
            )}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-3 flex-1">
                {/* Icon */}
                <div className="mt-0.5">
                  {getTypeIcon(item.type)}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    {getCategoryIcon(item.category)}
                    <h3 className="font-semibold text-foreground text-sm">
                      {item.title}
                    </h3>
                  </div>
                  <p className="text-sm text-muted-foreground mb-3">
                    {item.description}
                  </p>

                  {/* Actions */}
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleAction(item)}
                      className={cn(
                        'px-4 py-1.5 rounded-lg text-sm font-medium transition-all',
                        item.type === 'urgent'
                          ? 'bg-red-500 text-white hover:bg-red-600'
                          : item.type === 'important'
                          ? 'bg-accent text-accent-foreground hover:bg-accent/80'
                          : 'bg-muted text-foreground hover:bg-muted/80'
                      )}
                    >
                      {item.action.label}
                    </button>
                    {item.symbol && (
                      <span className="text-xs text-muted-foreground font-mono">
                        {item.symbol}
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Dismiss Button */}
              <button
                onClick={() => handleDismiss(item.id)}
                className="text-muted-foreground hover:text-foreground transition-colors ml-2"
                title="Dismiss"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* View All Link */}
      {visibleItems.length > 5 && (
        <div className="mt-4 text-center">
          <button className="text-sm text-accent hover:underline">
            View all {visibleItems.length} action items →
          </button>
        </div>
      )}
    </div>
  );
};
