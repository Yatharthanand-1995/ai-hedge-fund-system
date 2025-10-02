import React, { useState, useEffect } from 'react';
import {
  Bell,
  Clock,
  TrendingUp,
  TrendingDown,
  Target,
  AlertTriangle,
  CheckCircle,
  Calendar,
  DollarSign,
  Activity,
  Zap,
  ArrowRight
} from 'lucide-react';
import { cn, formatCurrency, formatPercentage } from '../../utils';

interface ActionItem {
  id: string;
  type: 'trade' | 'rebalance' | 'monitor' | 'alert' | 'opportunity';
  priority: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  symbol?: string;
  action: string;
  targetValue?: number;
  currentValue?: number;
  timeframe: string;
  impact: 'high' | 'medium' | 'low';
  completed: boolean;
  createdAt: Date;
}

interface UpcomingEvent {
  id: string;
  type: 'earnings' | 'dividend' | 'economic' | 'rebalancing';
  title: string;
  symbol?: string;
  date: Date;
  impact: 'high' | 'medium' | 'low';
  description: string;
}

interface Alert {
  id: string;
  type: 'price' | 'threshold' | 'risk' | 'opportunity';
  severity: 'high' | 'medium' | 'low';
  message: string;
  symbol?: string;
  timestamp: Date;
  acknowledged: boolean;
}

interface ActionableInsightsPanelProps {
  className?: string;
}

export const ActionableInsightsPanel: React.FC<ActionableInsightsPanelProps> = ({ className }) => {
  const [actionItems, setActionItems] = useState<ActionItem[]>([]);
  const [upcomingEvents, setUpcomingEvents] = useState<UpcomingEvent[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'actions' | 'events' | 'alerts'>('actions');

  useEffect(() => {
    // Fetch real actionable insights based on top picks analysis
    const fetchInsights = async () => {
      try {
        setLoading(true);

        // Fetch top picks to generate insights
        const response = await fetch('http://localhost:8010/portfolio/top-picks?limit=10');
        if (!response.ok) {
          throw new Error('Failed to fetch portfolio data');
        }

        const data = await response.json();
        const topPicks = data.top_picks || [];

        // Generate real action items based on top picks
        const realActions: ActionItem[] = [];
        const realAlerts: Alert[] = [];

        topPicks.forEach((pick: any, index: number) => {
          const { symbol, overall_score, recommendation, market_data } = pick;

          // Generate actions based on real data
          if (overall_score > 75 && recommendation.includes('BUY')) {
            realActions.push({
              id: `buy-${symbol}`,
              type: 'trade',
              priority: overall_score > 85 ? 'high' : 'medium',
              title: `Execute ${symbol} Buy Signal`,
              description: `Strong ${recommendation.toLowerCase()} signal with score ${overall_score}`,
              symbol,
              action: 'BUY',
              targetValue: market_data.current_price * 1.05,
              currentValue: market_data.current_price,
              timeframe: overall_score > 85 ? 'Today' : 'This Week',
              impact: overall_score > 85 ? 'high' : 'medium',
              completed: false,
              createdAt: new Date(Date.now() - index * 3600000)
            });

            realAlerts.push({
              id: `alert-${symbol}`,
              type: 'opportunity',
              severity: overall_score > 85 ? 'high' : 'medium',
              message: `${symbol} shows strong ${recommendation.toLowerCase()} signal (score: ${overall_score})`,
              symbol,
              timestamp: new Date(Date.now() - index * 1800000),
              acknowledged: false
            });
          }

          if (overall_score < 45 && recommendation.includes('SELL')) {
            realActions.push({
              id: `sell-${symbol}`,
              type: 'alert',
              priority: 'high',
              title: `${symbol} Risk Alert`,
              description: `Low score ${overall_score} suggests ${recommendation.toLowerCase()}`,
              symbol,
              action: 'REDUCE',
              targetValue: market_data.current_price * 0.95,
              currentValue: market_data.current_price,
              timeframe: 'Urgent',
              impact: 'high',
              completed: false,
              createdAt: new Date(Date.now() - index * 7200000)
            });
          }

          if (overall_score >= 45 && overall_score <= 65) {
            realActions.push({
              id: `monitor-${symbol}`,
              type: 'monitor',
              priority: 'low',
              title: `Monitor ${symbol} Performance`,
              description: `Moderate score ${overall_score} requires monitoring`,
              symbol,
              action: 'MONITOR',
              timeframe: 'This Month',
              impact: 'low',
              completed: false,
              createdAt: new Date(Date.now() - index * 86400000)
            });
          }
        });

        // Calculate sector allocation insights
        const sectorCounts: Record<string, number> = {};
        topPicks.forEach((pick: any) => {
          sectorCounts[pick.sector] = (sectorCounts[pick.sector] || 0) + 1;
        });

        const dominantSector = Object.entries(sectorCounts).reduce((a, b) => a[1] > b[1] ? a : b)?.[0];
        if (dominantSector && sectorCounts[dominantSector] > topPicks.length * 0.4) {
          realActions.push({
            id: 'sector-rebalance',
            type: 'rebalance',
            priority: 'medium',
            title: `Rebalance ${dominantSector} Allocation`,
            description: `${dominantSector} sector is overweight with ${sectorCounts[dominantSector]} positions`,
            action: 'REBALANCE',
            targetValue: 30,
            currentValue: (sectorCounts[dominantSector] / topPicks.length) * 100,
            timeframe: 'This Week',
            impact: 'medium',
            completed: false,
            createdAt: new Date(Date.now() - 86400000)
          });
        }

        // Generate upcoming events (simulated but realistic)
        const realEvents: UpcomingEvent[] = [
          {
            id: 'monthly-review',
            type: 'rebalancing',
            title: 'Monthly Portfolio Review',
            date: new Date(Date.now() + 86400000 * 7),
            impact: 'medium',
            description: 'Scheduled monthly rebalancing and performance review'
          },
          {
            id: 'quarterly-earnings',
            type: 'earnings',
            title: 'Quarterly Earnings Season',
            date: new Date(Date.now() + 86400000 * 14),
            impact: 'high',
            description: 'Major earnings reports may impact portfolio positions'
          }
        ];

        // Add risk alerts based on portfolio composition
        const avgScore = topPicks.reduce((sum: number, pick: any) => sum + pick.overall_score, 0) / topPicks.length;
        if (avgScore < 60) {
          realAlerts.push({
            id: 'portfolio-risk',
            type: 'risk',
            severity: 'medium',
            message: `Portfolio average score ${avgScore.toFixed(1)} below target threshold`,
            timestamp: new Date(Date.now() - 1800000),
            acknowledged: false
          });
        }

        setActionItems(realActions.slice(0, 8)); // Limit to 8 actions
        setUpcomingEvents(realEvents);
        setAlerts(realAlerts.slice(0, 5)); // Limit to 5 alerts
      } catch (error) {
        console.error('Failed to fetch insights:', error);

        // Fallback to minimal data if API fails
        setActionItems([]);
        setUpcomingEvents([]);
        setAlerts([]);
      } finally {
        setLoading(false);
      }
    };

    fetchInsights();
  }, []);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-400 bg-red-500/10';
      case 'medium': return 'text-yellow-400 bg-yellow-500/10';
      case 'low': return 'text-green-400 bg-green-500/10';
      default: return 'text-gray-400 bg-gray-500/10';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'trade': return <TrendingUp className="h-4 w-4" />;
      case 'rebalance': return <Target className="h-4 w-4" />;
      case 'monitor': return <Activity className="h-4 w-4" />;
      case 'alert': return <AlertTriangle className="h-4 w-4" />;
      case 'opportunity': return <Zap className="h-4 w-4" />;
      case 'earnings': return <DollarSign className="h-4 w-4" />;
      case 'economic': return <TrendingDown className="h-4 w-4" />;
      case 'dividend': return <CheckCircle className="h-4 w-4" />;
      default: return <Bell className="h-4 w-4" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'text-red-400';
      case 'medium': return 'text-yellow-400';
      case 'low': return 'text-blue-400';
      default: return 'text-gray-400';
    }
  };

  const formatTimeAgo = (date: Date) => {
    const diff = Date.now() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    return `${minutes}m ago`;
  };

  const formatTimeUntil = (date: Date) => {
    const diff = date.getTime() - Date.now();
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (days > 0) return `in ${days}d`;
    if (hours > 0) return `in ${hours}h`;
    return 'soon';
  };

  const pendingActions = actionItems.filter(item => !item.completed);
  const unacknowledgedAlerts = alerts.filter(alert => !alert.acknowledged);

  if (loading) {
    return (
      <div className={cn('professional-card p-6', className)}>
        <div className="flex items-center space-x-3 mb-6">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-accent"></div>
          <h2 className="text-xl font-semibold text-foreground">Loading Actionable Insights...</h2>
        </div>
      </div>
    );
  }

  return (
    <div className={cn('professional-card p-6', className)}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-foreground flex items-center space-x-2">
          <Zap className="h-6 w-6 text-accent" />
          <span>Actionable Insights</span>
        </h2>
        <div className="flex items-center space-x-4">
          <div className="text-sm text-muted-foreground">
            {pendingActions.length} pending actions
          </div>
          <div className="text-sm text-muted-foreground">
            {unacknowledgedAlerts.length} new alerts
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 mb-6 bg-muted/20 rounded-lg p-1">
        <button
          onClick={() => setActiveTab('actions')}
          className={cn('flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
            activeTab === 'actions'
              ? 'bg-accent text-accent-foreground'
              : 'text-muted-foreground hover:bg-muted/20'
          )}
        >
          Actions ({pendingActions.length})
        </button>
        <button
          onClick={() => setActiveTab('events')}
          className={cn('flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
            activeTab === 'events'
              ? 'bg-accent text-accent-foreground'
              : 'text-muted-foreground hover:bg-muted/20'
          )}
        >
          Events ({upcomingEvents.length})
        </button>
        <button
          onClick={() => setActiveTab('alerts')}
          className={cn('flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
            activeTab === 'alerts'
              ? 'bg-accent text-accent-foreground'
              : 'text-muted-foreground hover:bg-muted/20'
          )}
        >
          Alerts ({unacknowledgedAlerts.length})
        </button>
      </div>

      {/* Content */}
      <div className="space-y-4 max-h-96 overflow-y-auto">
        {activeTab === 'actions' && (
          <>
            {pendingActions.map((action) => (
              <div key={action.id} className="professional-card p-4 bg-muted/20">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <div className={cn('p-2 rounded-lg', getPriorityColor(action.priority))}>
                      {getTypeIcon(action.type)}
                    </div>
                    <div>
                      <div className="font-medium text-foreground">{action.title}</div>
                      <div className="text-sm text-muted-foreground">{action.description}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-muted-foreground">{action.timeframe}</div>
                    <div className={cn('text-xs px-2 py-1 rounded-full', getPriorityColor(action.priority))}>
                      {action.priority}
                    </div>
                  </div>
                </div>

                {action.symbol && (
                  <div className="flex items-center space-x-4 mb-3 text-sm">
                    <span className="font-medium">{action.symbol}</span>
                    {action.currentValue && action.targetValue && (
                      <span className="text-muted-foreground">
                        Current: {typeof action.currentValue === 'number' && action.currentValue > 50
                          ? formatCurrency(action.currentValue)
                          : formatPercentage(action.currentValue)}
                        → Target: {typeof action.targetValue === 'number' && action.targetValue > 50
                          ? formatCurrency(action.targetValue)
                          : formatPercentage(action.targetValue)}
                      </span>
                    )}
                  </div>
                )}

                <div className="flex justify-between items-center">
                  <div className="text-xs text-muted-foreground">
                    Created {formatTimeAgo(action.createdAt)} • Impact: {action.impact}
                  </div>
                  <div className="flex space-x-2">
                    <button className="px-3 py-1 bg-accent hover:bg-accent/80 text-accent-foreground rounded text-sm">
                      {action.action}
                    </button>
                    <button className="px-3 py-1 border border-border hover:bg-muted/20 rounded text-sm">
                      Details
                    </button>
                  </div>
                </div>
              </div>
            ))}
            {pendingActions.length === 0 && (
              <div className="text-center text-muted-foreground py-8">
                <CheckCircle className="h-12 w-12 mx-auto mb-4 text-green-400" />
                <div className="text-lg font-medium">All actions completed!</div>
                <div>Great job staying on top of your portfolio</div>
              </div>
            )}
          </>
        )}

        {activeTab === 'events' && (
          <>
            {upcomingEvents.map((event) => (
              <div key={event.id} className="professional-card p-4 bg-muted/20">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
                      {getTypeIcon(event.type)}
                    </div>
                    <div>
                      <div className="font-medium text-foreground">{event.title}</div>
                      <div className="text-sm text-muted-foreground">{event.description}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-foreground">{formatTimeUntil(event.date)}</div>
                    <div className={cn('text-xs', getSeverityColor(event.impact))}>
                      {event.impact} impact
                    </div>
                  </div>
                </div>

                <div className="flex justify-between items-center">
                  <div className="flex items-center space-x-2 text-sm">
                    <Calendar className="h-4 w-4 text-muted-foreground" />
                    <span className="text-muted-foreground">
                      {event.date.toLocaleDateString()}
                    </span>
                    {event.symbol && (
                      <span className="font-medium">{event.symbol}</span>
                    )}
                  </div>
                  <button className="text-sm text-accent hover:underline flex items-center space-x-1">
                    <span>Set Reminder</span>
                    <ArrowRight className="h-3 w-3" />
                  </button>
                </div>
              </div>
            ))}
          </>
        )}

        {activeTab === 'alerts' && (
          <>
            {alerts.map((alert) => (
              <div key={alert.id} className={cn(
                'professional-card p-4',
                alert.acknowledged ? 'bg-muted/10 opacity-60' : 'bg-muted/20'
              )}>
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <div className={cn('p-2 rounded-lg',
                      alert.acknowledged
                        ? 'bg-gray-500/10 text-gray-400'
                        : `${getSeverityColor(alert.severity).replace('text-', 'text-')} bg-${alert.severity === 'high' ? 'red' : alert.severity === 'medium' ? 'yellow' : 'blue'}-500/10`
                    )}>
                      <Bell className="h-4 w-4" />
                    </div>
                    <div>
                      <div className={cn('font-medium', alert.acknowledged ? 'text-muted-foreground' : 'text-foreground')}>
                        {alert.message}
                      </div>
                      {alert.symbol && (
                        <div className="text-sm text-muted-foreground">{alert.symbol}</div>
                      )}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-muted-foreground">{formatTimeAgo(alert.timestamp)}</div>
                    {!alert.acknowledged && (
                      <button
                        onClick={() => {
                          setAlerts(prev => prev.map(a =>
                            a.id === alert.id ? { ...a, acknowledged: true } : a
                          ));
                        }}
                        className="text-xs text-accent hover:underline"
                      >
                        Acknowledge
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </>
        )}
      </div>
    </div>
  );
};