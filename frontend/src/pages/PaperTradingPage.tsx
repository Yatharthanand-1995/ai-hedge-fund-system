import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { TrendingUp, TrendingDown, RefreshCw, Trash2, Clock, Sparkles, BarChart3, Shield, AlertTriangle } from 'lucide-react';
import { cn, formatCurrency } from '../utils';
import { useToast } from '../components/common/Toast';
import { AutoSellSettings } from '../components/AutoSellSettings';

interface PaperPortfolio {
  cash: number;
  positions: Record<string, {
    shares: number;
    cost_basis: number;
    current_price?: number;
    market_value?: number;
    unrealized_pnl?: number;
    unrealized_pnl_percent?: number;
    first_purchase_date: string;
  }>;
  created_at: string;
}

interface PaperStats {
  total_value: number;
  cash: number;
  invested: number;
  num_positions: number;
  total_return: number;
  total_return_percent: number;
  realized_pnl: number;
  unrealized_pnl?: number;
  num_transactions: number;
}

interface Transaction {
  timestamp: string;
  action: 'BUY' | 'SELL';
  symbol: string;
  shares: number;
  price: number;
  total: number;
  cash_after: number;
  portfolio_value: number;
}

interface TopPick {
  symbol: string;
  overall_score: number;
  recommendation: string;
  sector: string;
  market_data: {
    current_price: number;
    change_percent: number;
  };
  agent_scores: {
    fundamentals: number;
    momentum: number;
    quality: number;
    sentiment: number;
  };
}

interface AutoSellRules {
  enabled: boolean;
  stop_loss_percent: number;
  take_profit_percent: number;
  watch_ai_signals: boolean;
  max_position_age_days: number | null;
}

const API_BASE = 'http://localhost:8010';

export const PaperTradingPage: React.FC = () => {
  const [buySymbol, setBuySymbol] = useState('');
  const [buyShares, setBuyShares] = useState('');
  const [sellSymbol, setSellSymbol] = useState('');
  const [sellShares, setSellShares] = useState('');
  const [showAutoSellSettings, setShowAutoSellSettings] = useState(false);
  const queryClient = useQueryClient();
  const toast = useToast();

  // Fetch portfolio
  const { data: portfolioData, isLoading: portfolioLoading, error: portfolioError } = useQuery({
    queryKey: ['paperPortfolio'],
    queryFn: async () => {
      const response = await fetch(`${API_BASE}/portfolio/paper`);
      if (!response.ok) throw new Error('Failed to fetch portfolio');
      return response.json();
    },
    refetchInterval: 5000, // Refresh every 5 seconds
  });

  // Fetch transactions
  const { data: transactionsData, isLoading: transactionsLoading } = useQuery({
    queryKey: ['paperTransactions'],
    queryFn: async () => {
      const response = await fetch(`${API_BASE}/portfolio/paper/transactions?limit=50`);
      if (!response.ok) throw new Error('Failed to fetch transactions');
      return response.json();
    },
    refetchInterval: 5000,
  });

  // Fetch AI recommendations (top picks from 4-agent system)
  const { data: topPicksData, isLoading: topPicksLoading } = useQuery({
    queryKey: ['aiTopPicks'],
    queryFn: async () => {
      const response = await fetch(`${API_BASE}/portfolio/top-picks?limit=10`);
      if (!response.ok) throw new Error('Failed to fetch AI recommendations');
      return response.json();
    },
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  });

  // Buy mutation
  const buyMutation = useMutation({
    mutationFn: async ({ symbol, shares }: { symbol: string; shares: number }) => {
      const response = await fetch(`${API_BASE}/portfolio/paper/buy?symbol=${symbol}&shares=${shares}`, {
        method: 'POST',
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Buy failed');
      }
      return response.json();
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['paperPortfolio'] });
      queryClient.invalidateQueries({ queryKey: ['paperTransactions'] });
      toast.success('Buy Order Executed', `Bought ${data.transaction.shares} shares`);
      setBuySymbol('');
      setBuyShares('');
    },
    onError: (error: Error) => {
      toast.error('Buy Order Failed', error.message);
    },
  });

  // Sell mutation
  const sellMutation = useMutation({
    mutationFn: async ({ symbol, shares }: { symbol: string; shares: number }) => {
      const response = await fetch(`${API_BASE}/portfolio/paper/sell?symbol=${symbol}&shares=${shares}`, {
        method: 'POST',
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Sell failed');
      }
      return response.json();
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['paperPortfolio'] });
      queryClient.invalidateQueries({ queryKey: ['paperTransactions'] });
      const pnl = data.transaction.pnl || 0;
      const pnlPercent = data.transaction.pnl_percent || 0;
      toast.success(
        'Sell Order Executed',
        `P&L: ${formatCurrency(pnl)} (${pnlPercent > 0 ? '+' : ''}${pnlPercent.toFixed(2)}%)`
      );
      setSellSymbol('');
      setSellShares('');
    },
    onError: (error: Error) => {
      toast.error('Sell Order Failed', error.message);
    },
  });

  // Reset mutation
  const resetMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch(`${API_BASE}/portfolio/paper/reset`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Reset failed');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['paperPortfolio'] });
      queryClient.invalidateQueries({ queryKey: ['paperTransactions'] });
      toast.success('Portfolio Reset', 'Portfolio reset to $10,000');
    },
    onError: (error: Error) => {
      toast.error('Reset Failed', error.message);
    },
  });

  const handleBuy = () => {
    if (!buySymbol || !buyShares) {
      toast.warning('Missing Information', 'Please enter symbol and shares');
      return;
    }
    const shares = parseInt(buyShares);
    if (shares <= 0) {
      toast.warning('Invalid Shares', 'Shares must be positive');
      return;
    }

    // Risk management checks
    const cash = portfolioData?.portfolio?.cash || 0;
    const totalValue = portfolioData?.stats?.total_value || 10000;

    // Get price from AI recommendations if available
    const topPick = topPicks.find(p => p.symbol === buySymbol.toUpperCase());
    const estimatedPrice = topPick?.market_data?.current_price || 100; // Fallback estimate
    const estimatedCost = shares * estimatedPrice;

    // Check if enough cash
    if (estimatedCost > cash) {
      toast.warning('Insufficient Cash', `Estimated cost $${estimatedCost.toFixed(2)} exceeds available cash $${cash.toFixed(2)}`);
      return;
    }

    // Warn if position > 25% of portfolio
    const positionPercent = (estimatedCost / totalValue) * 100;
    if (positionPercent > 25) {
      const proceed = confirm(
        `⚠️ Risk Warning\n\n` +
        `This trade would be ${positionPercent.toFixed(1)}% of your portfolio.\n\n` +
        `Recommended max: 25% per position.\n\n` +
        `Are you sure you want to proceed?`
      );
      if (!proceed) return;
    }

    buyMutation.mutate({ symbol: buySymbol.toUpperCase(), shares });
  };

  const handleSell = () => {
    if (!sellSymbol || !sellShares) {
      toast.warning('Missing Information', 'Please enter symbol and shares');
      return;
    }
    const shares = parseInt(sellShares);
    if (shares <= 0) {
      toast.warning('Invalid Shares', 'Shares must be positive');
      return;
    }
    sellMutation.mutate({ symbol: sellSymbol.toUpperCase(), shares });
  };

  const handleReset = () => {
    if (confirm('Are you sure you want to reset your portfolio? This will archive all transactions and start fresh with $10,000.')) {
      resetMutation.mutate();
    }
  };

  // Handle AI-recommended trade
  const handleAITrade = (pick: TopPick, action: 'buy' | 'sell') => {
    const cash = portfolioData?.portfolio?.cash || 0;
    const price = pick.market_data?.current_price || 0;

    if (!price || price <= 0) {
      toast.error('Invalid Price', `Cannot get price for ${pick.symbol}`);
      return;
    }

    if (action === 'buy') {
      // Calculate max affordable shares (leaving some buffer)
      const maxShares = Math.floor((cash * 0.2) / price); // Use 20% of cash per position
      const shares = Math.max(1, maxShares);

      if (shares * price > cash) {
        toast.warning('Insufficient Funds', `Not enough cash to buy ${pick.symbol}`);
        return;
      }

      buyMutation.mutate({ symbol: pick.symbol, shares });
    } else {
      // Check if we own this stock
      const position = portfolioData?.portfolio?.positions?.[pick.symbol];
      if (!position) {
        toast.warning('No Position', `You don't own ${pick.symbol}`);
        return;
      }

      sellMutation.mutate({ symbol: pick.symbol, shares: position.shares });
    }
  };

  const portfolio: PaperPortfolio | undefined = portfolioData?.portfolio;
  const stats: PaperStats | undefined = portfolioData?.stats;
  const transactions: Transaction[] = transactionsData?.transactions || [];
  const topPicks: TopPick[] = topPicksData?.top_picks || [];

  if (portfolioError) {
    return (
      <div className="professional-card p-8 text-center">
        <p className="text-red-400">Error loading paper trading portfolio</p>
        <p className="text-sm text-muted-foreground mt-2">Make sure the API server is running</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-foreground mb-2">
          Paper Trading
        </h1>
        <p className="text-xl text-muted-foreground">
          Practice trading with $10,000 virtual cash - All transactions logged
        </p>
      </div>

      {/* Auto-Sell Settings Modal */}
      {showAutoSellSettings && (
        <AutoSellSettings onClose={() => setShowAutoSellSettings(false)} />
      )}

      {/* Portfolio Summary */}
      <div className="professional-card p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold">Portfolio Overview</h2>
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setShowAutoSellSettings(true)}
              className="professional-button-secondary flex items-center space-x-2"
            >
              <Shield className="h-4 w-4" />
              <span>Auto-Sell</span>
            </button>
            <button
              onClick={() => queryClient.invalidateQueries({ queryKey: ['paperPortfolio', 'paperTransactions'] })}
              className="professional-button-secondary flex items-center space-x-2"
              disabled={portfolioLoading}
            >
              <RefreshCw className={cn('h-4 w-4', portfolioLoading && 'animate-spin')} />
              <span>Refresh</span>
            </button>
          </div>
        </div>

        {portfolioLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent"></div>
          </div>
        ) : stats ? (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="text-center p-4 bg-muted/20 rounded-lg">
                <div className="text-sm text-muted-foreground mb-1">Total Value</div>
                <div className="text-2xl font-bold">{formatCurrency(stats.total_value)}</div>
              </div>
              <div className="text-center p-4 bg-muted/20 rounded-lg">
                <div className="text-sm text-muted-foreground mb-1">Cash</div>
                <div className="text-2xl font-bold text-green-400">{formatCurrency(stats.cash)}</div>
              </div>
              <div className="text-center p-4 bg-muted/20 rounded-lg">
                <div className="text-sm text-muted-foreground mb-1">Invested</div>
                <div className="text-2xl font-bold text-blue-400">{formatCurrency(stats.invested)}</div>
              </div>
              <div className="text-center p-4 bg-muted/20 rounded-lg">
                <div className="text-sm text-muted-foreground mb-1">Total Return</div>
                <div className={cn(
                  'text-2xl font-bold',
                  stats.total_return >= 0 ? 'text-green-400' : 'text-red-400'
                )}>
                  {formatCurrency(stats.total_return)} ({stats.total_return_percent > 0 ? '+' : ''}{stats.total_return_percent.toFixed(2)}%)
                </div>
              </div>
            </div>

            {/* P&L Breakdown */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="border border-border rounded-lg p-4">
                <div className="text-sm text-muted-foreground mb-1">Unrealized P&L</div>
                <div className={cn(
                  'text-xl font-bold',
                  (stats.unrealized_pnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                )}>
                  {(stats.unrealized_pnl || 0) >= 0 ? '+' : ''}{formatCurrency(stats.unrealized_pnl || 0)}
                </div>
                <div className="text-xs text-muted-foreground mt-1">From open positions</div>
              </div>
              <div className="border border-border rounded-lg p-4">
                <div className="text-sm text-muted-foreground mb-1">Realized P&L</div>
                <div className={cn(
                  'text-xl font-bold',
                  (stats.realized_pnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                )}>
                  {(stats.realized_pnl || 0) >= 0 ? '+' : ''}{formatCurrency(stats.realized_pnl || 0)}
                </div>
                <div className="text-xs text-muted-foreground mt-1">From closed trades</div>
              </div>
              <div className="border border-border rounded-lg p-4">
                <div className="text-sm text-muted-foreground mb-1">Positions</div>
                <div className="text-xl font-bold">{stats.num_positions}</div>
                <div className="text-xs text-muted-foreground mt-1">{stats.num_transactions} transactions</div>
              </div>
            </div>
          </div>
        ) : null}
      </div>

      {/* AI Recommendations from 4-Agent System */}
      <div className="professional-card p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold flex items-center space-x-2">
            <Sparkles className="h-6 w-6 text-yellow-400" />
            <span>AI Recommendations</span>
          </h2>
          <button
            onClick={() => queryClient.invalidateQueries({ queryKey: ['aiTopPicks'] })}
            className="professional-button-secondary flex items-center space-x-2"
            disabled={topPicksLoading}
          >
            <RefreshCw className={cn('h-4 w-4', topPicksLoading && 'animate-spin')} />
            <span>Refresh</span>
          </button>
        </div>

        {topPicksLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent"></div>
            <span className="ml-3 text-muted-foreground">Analyzing 50 stocks with 4-agent system...</span>
          </div>
        ) : topPicks.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <BarChart3 className="h-12 w-12 mx-auto mb-2 opacity-50" />
            <p>No recommendations available</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {topPicks.slice(0, 6).map((pick) => {
              const hasPosition = !!portfolio?.positions?.[pick.symbol];
              const overallScore = pick.overall_score || 0;
              const scoreColor =
                overallScore >= 75 ? 'text-green-400' :
                overallScore >= 60 ? 'text-blue-400' :
                overallScore >= 50 ? 'text-yellow-400' : 'text-orange-400';

              return (
                <div key={pick.symbol} className="border border-border rounded-lg p-4 hover:border-accent transition-colors">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <div className="text-lg font-bold">{pick.symbol || 'N/A'}</div>
                      <div className="text-xs text-muted-foreground">{pick.sector || 'N/A'}</div>
                    </div>
                    <div className="text-right">
                      <div className={cn('text-2xl font-bold', scoreColor)}>
                        {overallScore.toFixed(0)}
                      </div>
                      <div className="text-xs text-muted-foreground">Score</div>
                    </div>
                  </div>

                  <div className="mb-3">
                    <div className="text-sm font-medium">{formatCurrency(pick.market_data?.current_price || 0)}</div>
                    <div className={cn(
                      'text-xs',
                      (pick.market_data?.change_percent || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                    )}>
                      {(pick.market_data?.change_percent || 0) >= 0 ? '+' : ''}
                      {(pick.market_data?.change_percent || 0).toFixed(2)}%
                    </div>
                  </div>

                  <div className="mb-3">
                    <div className={cn(
                      'text-xs font-medium px-2 py-1 rounded inline-block',
                      pick.recommendation === 'STRONG BUY' ? 'bg-green-400/10 text-green-400' :
                      pick.recommendation === 'BUY' ? 'bg-emerald-400/10 text-emerald-400' :
                      pick.recommendation === 'HOLD' ? 'bg-yellow-400/10 text-yellow-400' :
                      'bg-orange-400/10 text-orange-400'
                    )}>
                      {pick.recommendation || 'N/A'}
                    </div>
                  </div>

                  <div className="grid grid-cols-4 gap-1 mb-3">
                    <div className="text-center">
                      <div className="text-xs text-muted-foreground">Fund</div>
                      <div className="text-xs font-bold">{(pick.agent_scores?.fundamentals || 0).toFixed(0)}</div>
                    </div>
                    <div className="text-center">
                      <div className="text-xs text-muted-foreground">Mom</div>
                      <div className="text-xs font-bold">{(pick.agent_scores?.momentum || 0).toFixed(0)}</div>
                    </div>
                    <div className="text-center">
                      <div className="text-xs text-muted-foreground">Qual</div>
                      <div className="text-xs font-bold">{(pick.agent_scores?.quality || 0).toFixed(0)}</div>
                    </div>
                    <div className="text-center">
                      <div className="text-xs text-muted-foreground">Sent</div>
                      <div className="text-xs font-bold">{(pick.agent_scores?.sentiment || 0).toFixed(0)}</div>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    {!hasPosition ? (
                      <button
                        onClick={() => handleAITrade(pick, 'buy')}
                        disabled={buyMutation.isPending}
                        className="flex-1 bg-green-500/10 hover:bg-green-500/20 text-green-400 px-3 py-2 rounded text-sm font-medium transition-colors flex items-center justify-center space-x-1"
                      >
                        <TrendingUp className="h-4 w-4" />
                        <span>Buy</span>
                      </button>
                    ) : (
                      <button
                        onClick={() => handleAITrade(pick, 'sell')}
                        disabled={sellMutation.isPending}
                        className="flex-1 bg-red-500/10 hover:bg-red-500/20 text-red-400 px-3 py-2 rounded text-sm font-medium transition-colors flex items-center justify-center space-x-1"
                      >
                        <TrendingDown className="h-4 w-4" />
                        <span>Sell</span>
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Trading Panels */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Buy Panel */}
        <div className="professional-card p-6">
          <h3 className="text-xl font-bold mb-4 flex items-center space-x-2">
            <TrendingUp className="h-5 w-5 text-green-400" />
            <span>Buy Stock</span>
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Symbol</label>
              <input
                type="text"
                value={buySymbol}
                onChange={(e) => setBuySymbol(e.target.value.toUpperCase())}
                placeholder="AAPL"
                className="professional-input"
                disabled={buyMutation.isPending}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Shares</label>
              <input
                type="number"
                value={buyShares}
                onChange={(e) => setBuyShares(e.target.value)}
                placeholder="10"
                min="1"
                className="professional-input"
                disabled={buyMutation.isPending}
              />
            </div>
            <button
              onClick={handleBuy}
              disabled={buyMutation.isPending || !buySymbol || !buyShares}
              className="professional-button-primary w-full"
            >
              {buyMutation.isPending ? 'Processing...' : 'Buy Stock'}
            </button>
          </div>
        </div>

        {/* Sell Panel */}
        <div className="professional-card p-6">
          <h3 className="text-xl font-bold mb-4 flex items-center space-x-2">
            <TrendingDown className="h-5 w-5 text-red-400" />
            <span>Sell Stock</span>
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Symbol</label>
              <input
                type="text"
                value={sellSymbol}
                onChange={(e) => setSellSymbol(e.target.value.toUpperCase())}
                placeholder="AAPL"
                className="professional-input"
                disabled={sellMutation.isPending}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Shares</label>
              <input
                type="number"
                value={sellShares}
                onChange={(e) => setSellShares(e.target.value)}
                placeholder="10"
                min="1"
                className="professional-input"
                disabled={sellMutation.isPending}
              />
            </div>
            <button
              onClick={handleSell}
              disabled={sellMutation.isPending || !sellSymbol || !sellShares}
              className="professional-button-primary w-full"
            >
              {sellMutation.isPending ? 'Processing...' : 'Sell Stock'}
            </button>
          </div>
        </div>
      </div>

      {/* Risk Management Summary */}
      {portfolio && Object.keys(portfolio.positions).length > 0 && stats && (
        <div className="professional-card p-6 bg-gradient-to-r from-yellow-500/5 to-orange-500/5 border-yellow-500/20">
          <h3 className="text-xl font-bold mb-4 flex items-center">
            <span className="mr-2">⚠️</span>
            Risk Management
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(portfolio.positions).map(([symbol, position]) => {
              const marketValue = position.market_value || (position.shares * position.cost_basis);
              const positionPercent = (marketValue / stats.total_value) * 100;
              const isHighRisk = positionPercent > 25;
              const isMediumRisk = positionPercent > 15 && positionPercent <= 25;

              return (
                <div key={symbol} className={cn(
                  'border rounded-lg p-3',
                  isHighRisk ? 'border-red-500/50 bg-red-500/5' :
                  isMediumRisk ? 'border-yellow-500/50 bg-yellow-500/5' :
                  'border-green-500/50 bg-green-500/5'
                )}>
                  <div className="flex items-center justify-between">
                    <div className="font-bold">{symbol}</div>
                    <div className={cn(
                      'text-sm font-medium',
                      isHighRisk ? 'text-red-400' :
                      isMediumRisk ? 'text-yellow-400' :
                      'text-green-400'
                    )}>
                      {positionPercent.toFixed(1)}%
                    </div>
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {isHighRisk ? '⚠️ High concentration' :
                     isMediumRisk ? '⚡ Moderate risk' :
                     '✓ Diversified'}
                  </div>
                </div>
              );
            })}
          </div>
          <div className="mt-4 text-sm text-muted-foreground">
            <strong>Tip:</strong> Keep individual positions under 25% of portfolio value for better diversification.
          </div>
        </div>
      )}

      {/* Positions */}
      {portfolio && Object.keys(portfolio.positions).length > 0 && (
        <div className="professional-card p-6">
          <h3 className="text-xl font-bold mb-4">Current Positions</h3>
          <div className="space-y-3">
            {Object.entries(portfolio.positions).map(([symbol, position]) => {
              const currentPrice = position.current_price || position.cost_basis;
              const marketValue = position.market_value || (position.shares * position.cost_basis);
              const unrealizedPnl = position.unrealized_pnl || 0;
              const unrealizedPnlPercent = position.unrealized_pnl_percent || 0;
              const isProfitable = unrealizedPnl >= 0;

              return (
                <div key={symbol} className="border border-border rounded-lg p-4 hover:border-accent transition-colors">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <div className="text-xl font-bold">{symbol}</div>
                      <div className="text-sm text-muted-foreground">
                        {position.shares} shares
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-xl font-bold">{formatCurrency(marketValue)}</div>
                      <div className={cn(
                        'text-sm font-medium',
                        isProfitable ? 'text-green-400' : 'text-red-400'
                      )}>
                        {isProfitable ? '+' : ''}{formatCurrency(unrealizedPnl)} ({unrealizedPnlPercent >= 0 ? '+' : ''}{unrealizedPnlPercent.toFixed(2)}%)
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="text-muted-foreground">Cost Basis</div>
                      <div className="font-medium">{formatCurrency(position.cost_basis)}</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">Current Price</div>
                      <div className="font-medium flex items-center">
                        {formatCurrency(currentPrice)}
                        {currentPrice !== position.cost_basis && (
                          <span className={cn(
                            'ml-2 text-xs',
                            isProfitable ? 'text-green-400' : 'text-red-400'
                          )}>
                            {isProfitable ? '↑' : '↓'}
                          </span>
                        )}
                      </div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">Total Cost</div>
                      <div className="font-medium">{formatCurrency(position.shares * position.cost_basis)}</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">Purchase Date</div>
                      <div className="font-medium text-xs">
                        {new Date(position.first_purchase_date).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Transaction History */}
      <div className="professional-card p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold">Transaction History</h3>
          <button
            onClick={handleReset}
            disabled={resetMutation.isPending}
            className="professional-button-secondary flex items-center space-x-2 text-red-400 hover:text-red-300"
          >
            <Trash2 className="h-4 w-4" />
            <span>Reset Portfolio</span>
          </button>
        </div>

        {transactionsLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent"></div>
          </div>
        ) : transactions.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <Clock className="h-12 w-12 mx-auto mb-2 opacity-50" />
            <p>No transactions yet. Start trading!</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="border-b border-border">
                <tr className="text-left">
                  <th className="pb-2 font-medium">Date</th>
                  <th className="pb-2 font-medium">Action</th>
                  <th className="pb-2 font-medium">Symbol</th>
                  <th className="pb-2 font-medium text-right">Shares</th>
                  <th className="pb-2 font-medium text-right">Price</th>
                  <th className="pb-2 font-medium text-right">Total</th>
                  <th className="pb-2 font-medium text-right">Cash After</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {transactions.map((tx, i) => (
                  <tr key={i} className="hover:bg-muted/10">
                    <td className="py-2 text-sm text-muted-foreground">
                      {new Date(tx.timestamp).toLocaleString()}
                    </td>
                    <td className="py-2">
                      <span className={cn(
                        'px-2 py-1 rounded text-sm font-medium',
                        tx.action === 'BUY'
                          ? 'bg-green-400/10 text-green-400'
                          : 'bg-red-400/10 text-red-400'
                      )}>
                        {tx.action}
                      </span>
                    </td>
                    <td className="py-2 font-medium">{tx.symbol}</td>
                    <td className="py-2 text-right">{tx.shares}</td>
                    <td className="py-2 text-right">{formatCurrency(tx.price)}</td>
                    <td className="py-2 text-right font-medium">{formatCurrency(tx.total)}</td>
                    <td className="py-2 text-right text-muted-foreground">{formatCurrency(tx.cash_after)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
