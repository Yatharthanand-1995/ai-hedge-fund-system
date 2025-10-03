import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, DollarSign, Briefcase, PieChart, Lightbulb, AlertCircle, CheckCircle, Target } from 'lucide-react';
import { cn, formatCurrency, formatPercentage } from '../../utils';

interface Position {
  symbol: string;
  shares: number;
  cost_basis: number;
  purchase_date: string;
  notes: string;
  current_price: number;
  market_value: number;
  total_cost: number;
  pnl: number;
  pnl_percent: number;
  company_name: string;
}

interface PortfolioSummary {
  total_value: number;
  total_market_value: number;
  total_cost_basis: number;
  total_pnl: number;
  total_pnl_percent: number;
  cash: number;
  num_positions: number;
  total_invested: number;
}

interface UserPortfolio {
  portfolio_id: string;
  cash: number;
  positions: Position[];
  summary: PortfolioSummary;
  settings: {
    risk_tolerance: string;
    investment_style: string;
    rebalance_frequency: string;
  };
  updated_at: string;
}

interface PositionAnalysis {
  symbol: string;
  action: 'HOLD' | 'CONSIDER_SELLING' | 'REVIEW';
  ai_score: number | null;
  current_value: number;
  recommendation: string;
  confidence: string;
  reasoning: string;
  rank_in_top_picks: number | null;
}

interface BuyRecommendation {
  symbol: string;
  rank: number;
  ai_score: number;
  current_price: number;
  recommendation: string;
  confidence: string;
  shares_to_buy: number;
  estimated_investment: number;
  reasoning: string;
  sector: string;
}

interface Recommendations {
  portfolio_analysis: {
    total_positions: number;
    positions_in_top_picks: number;
    actions_needed: number;
    cash_available: number;
    total_portfolio_value: number;
  };
  current_holdings_analysis: PositionAnalysis[];
  buy_recommendations: BuyRecommendation[];
  rebalancing_plan: {
    priority: string;
    suggested_actions: number;
    available_capital: number;
    diversification_score: number;
  };
}

interface UserPortfolioPanelProps {
  className?: string;
}

export const UserPortfolioPanel: React.FC<UserPortfolioPanelProps> = ({ className }) => {
  const [portfolio, setPortfolio] = useState<UserPortfolio | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendations | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingRecs, setLoadingRecs] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPortfolio = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:8010/portfolio/user');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setPortfolio(data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch user portfolio:', err);
        setError('Failed to load portfolio data');
      } finally {
        setLoading(false);
      }
    };

    const fetchRecommendations = async () => {
      try {
        setLoadingRecs(true);
        const response = await fetch('http://localhost:8010/portfolio/user/recommendations');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setRecommendations(data);
      } catch (err) {
        console.error('Failed to fetch recommendations:', err);
        // Don't set error - recommendations are optional
      } finally {
        setLoadingRecs(false);
      }
    };

    fetchPortfolio();
    fetchRecommendations();

    // Refresh every 60 seconds
    const interval = setInterval(() => {
      fetchPortfolio();
      fetchRecommendations();
    }, 60000);

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className={cn('professional-card p-6', className)}>
        <div className="flex items-center space-x-3">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-accent"></div>
          <h2 className="text-xl font-semibold text-foreground">Loading Your Portfolio...</h2>
        </div>
      </div>
    );
  }

  if (error || !portfolio) {
    return (
      <div className={cn('professional-card p-6', className)}>
        <div className="text-red-400">
          <h2 className="text-xl font-semibold mb-2">Error Loading Portfolio</h2>
          <p className="text-sm">{error || 'Unknown error'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={cn('professional-card p-6', className)}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-foreground flex items-center space-x-2">
          <Briefcase className="h-6 w-6 text-accent" />
          <span>Your Portfolio</span>
        </h2>
        <div className="text-sm text-muted-foreground">
          Last updated: {new Date(portfolio.updated_at).toLocaleString()}
        </div>
      </div>

      {/* Portfolio Summary */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Total Value */}
        <div className="text-center">
          <div className="text-sm text-muted-foreground mb-1">Total Value</div>
          <div className="text-3xl font-bold text-foreground">
            {formatCurrency(portfolio.summary.total_value)}
          </div>
          <div className="text-xs text-muted-foreground mt-1">
            {portfolio.summary.num_positions} positions + cash
          </div>
        </div>

        {/* Total P&L */}
        <div className="text-center">
          <div className="text-sm text-muted-foreground mb-1">Total P&L</div>
          <div className={cn('text-2xl font-bold flex items-center justify-center space-x-1',
            portfolio.summary.total_pnl >= 0 ? 'text-green-400' : 'text-red-400')}>
            {portfolio.summary.total_pnl >= 0 ? <TrendingUp className="h-5 w-5" /> : <TrendingDown className="h-5 w-5" />}
            <span>{formatCurrency(portfolio.summary.total_pnl)}</span>
          </div>
          <div className={cn('text-sm',
            portfolio.summary.total_pnl >= 0 ? 'text-green-400' : 'text-red-400')}>
            {portfolio.summary.total_pnl_percent >= 0 ? '+' : ''}{formatPercentage(portfolio.summary.total_pnl_percent)}
          </div>
        </div>

        {/* Cash Available */}
        <div className="text-center">
          <div className="text-sm text-muted-foreground mb-1">Cash Available</div>
          <div className="text-2xl font-bold text-foreground flex items-center justify-center space-x-1">
            <DollarSign className="h-5 w-5" />
            <span>{formatCurrency(portfolio.cash)}</span>
          </div>
          <div className="text-xs text-muted-foreground mt-1">
            {((portfolio.cash / portfolio.summary.total_value) * 100).toFixed(1)}% of portfolio
          </div>
        </div>

        {/* Invested */}
        <div className="text-center">
          <div className="text-sm text-muted-foreground mb-1">Invested</div>
          <div className="text-2xl font-bold text-foreground flex items-center justify-center space-x-1">
            <PieChart className="h-5 w-5" />
            <span>{formatCurrency(portfolio.summary.total_market_value)}</span>
          </div>
          <div className="text-xs text-muted-foreground mt-1">
            Cost: {formatCurrency(portfolio.summary.total_cost_basis)}
          </div>
        </div>
      </div>

      {/* Positions */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-foreground mb-4">Your Positions</h3>
        <div className="space-y-3">
          {portfolio.positions.map((position) => (
            <div key={position.symbol} className="professional-card p-4 bg-muted/20">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="text-lg font-bold text-foreground">{position.symbol}</span>
                    <span className="text-sm text-muted-foreground">{position.shares} shares</span>
                  </div>
                  <div className="text-sm text-muted-foreground">{position.company_name}</div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-foreground">{formatCurrency(position.market_value)}</div>
                  <div className={cn('text-sm font-medium',
                    position.pnl >= 0 ? 'text-green-400' : 'text-red-400')}>
                    {position.pnl >= 0 ? '+' : ''}{formatCurrency(position.pnl)} ({formatPercentage(position.pnl_percent)})
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-4 gap-4 text-sm">
                <div>
                  <div className="text-muted-foreground">Current Price</div>
                  <div className="font-medium">{formatCurrency(position.current_price)}</div>
                </div>
                <div>
                  <div className="text-muted-foreground">Cost Basis</div>
                  <div className="font-medium">{formatCurrency(position.cost_basis)}</div>
                </div>
                <div>
                  <div className="text-muted-foreground">Total Cost</div>
                  <div className="font-medium">{formatCurrency(position.total_cost)}</div>
                </div>
                <div>
                  <div className="text-muted-foreground">Purchase Date</div>
                  <div className="font-medium">{new Date(position.purchase_date).toLocaleDateString()}</div>
                </div>
              </div>

              {position.notes && (
                <div className="mt-2 text-xs text-muted-foreground italic">
                  {position.notes}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* AI Recommendations */}
      {!loadingRecs && recommendations && (
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-foreground flex items-center space-x-2">
              <Lightbulb className="h-5 w-5 text-accent" />
              <span>AI-Powered Recommendations</span>
            </h3>
            <div className={cn('px-3 py-1 rounded-full text-xs font-medium',
              recommendations.rebalancing_plan.priority === 'HIGH'
                ? 'bg-red-500/20 text-red-400'
                : 'bg-green-500/20 text-green-400')}>
              {recommendations.rebalancing_plan.suggested_actions} action{recommendations.rebalancing_plan.suggested_actions !== 1 ? 's' : ''} needed
            </div>
          </div>

          {/* Holdings Analysis */}
          {recommendations.current_holdings_analysis.length > 0 && (
            <div className="mb-4">
              <h4 className="text-sm font-semibold text-foreground mb-3">Current Holdings Analysis</h4>
              <div className="space-y-2">
                {recommendations.current_holdings_analysis.map((analysis) => (
                  <div key={analysis.symbol} className="professional-card p-3 bg-muted/10">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <span className="font-medium text-foreground">{analysis.symbol}</span>
                        {analysis.rank_in_top_picks && (
                          <span className="text-xs px-2 py-0.5 rounded bg-green-500/20 text-green-400">
                            #{analysis.rank_in_top_picks} in AI picks
                          </span>
                        )}
                      </div>
                      <div className="flex items-center space-x-2">
                        {analysis.ai_score && (
                          <span className="text-sm font-medium">{analysis.ai_score}/100</span>
                        )}
                        {analysis.action === 'HOLD' && <CheckCircle className="h-4 w-4 text-green-400" />}
                        {analysis.action === 'CONSIDER_SELLING' && <AlertCircle className="h-4 w-4 text-yellow-400" />}
                        {analysis.action === 'REVIEW' && <Target className="h-4 w-4 text-red-400" />}
                      </div>
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {analysis.reasoning}
                    </div>
                    <div className="mt-1 text-xs font-medium">
                      <span className={cn(
                        analysis.action === 'HOLD' ? 'text-green-400' :
                        analysis.action === 'CONSIDER_SELLING' ? 'text-yellow-400' :
                        'text-red-400'
                      )}>
                        {analysis.action === 'HOLD' ? '✓ Hold' :
                         analysis.action === 'CONSIDER_SELLING' ? '⚠ Consider Selling' :
                         '⚠ Review for Rebalancing'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Buy Recommendations */}
          {recommendations.buy_recommendations.length > 0 && (
            <div className="mb-4">
              <h4 className="text-sm font-semibold text-foreground mb-3">
                Top Buy Opportunities (You have {formatCurrency(recommendations.rebalancing_plan.available_capital)} available)
              </h4>
              <div className="space-y-2">
                {recommendations.buy_recommendations.map((rec) => (
                  <div key={rec.symbol} className="professional-card p-3 bg-accent/5 border border-accent/20">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <span className="font-medium text-foreground">{rec.symbol}</span>
                        <span className="text-xs px-2 py-0.5 rounded bg-accent/20 text-accent">
                          AI Rank #{rec.rank}
                        </span>
                        <span className="text-xs text-muted-foreground">{rec.sector}</span>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-bold text-foreground">{formatCurrency(rec.current_price)}/share</div>
                        <div className="text-xs text-muted-foreground">Score: {rec.ai_score}/100</div>
                      </div>
                    </div>
                    <div className="text-xs text-muted-foreground mb-2">{rec.reasoning}</div>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-muted-foreground">
                        Suggested: {rec.shares_to_buy} share{rec.shares_to_buy !== 1 ? 's' : ''}
                      </span>
                      <span className="font-medium text-accent">
                        Investment: {formatCurrency(rec.estimated_investment)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Rebalancing Plan Summary */}
          <div className="professional-card p-3 bg-blue-500/5 border border-blue-500/20">
            <h4 className="text-sm font-semibold text-foreground mb-2">Rebalancing Plan</h4>
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div>
                <div className="text-muted-foreground">Priority</div>
                <div className={cn('font-medium',
                  recommendations.rebalancing_plan.priority === 'HIGH' ? 'text-red-400' : 'text-green-400')}>
                  {recommendations.rebalancing_plan.priority}
                </div>
              </div>
              <div>
                <div className="text-muted-foreground">Diversification Score</div>
                <div className="font-medium">{recommendations.rebalancing_plan.diversification_score.toFixed(0)}%</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Portfolio Settings */}
      <div className="professional-card p-4 bg-muted/20">
        <h3 className="text-sm font-semibold text-foreground mb-3">Portfolio Settings</h3>
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div>
            <div className="text-muted-foreground">Risk Tolerance</div>
            <div className="font-medium capitalize">{portfolio.settings.risk_tolerance}</div>
          </div>
          <div>
            <div className="text-muted-foreground">Investment Style</div>
            <div className="font-medium capitalize">{portfolio.settings.investment_style}</div>
          </div>
          <div>
            <div className="text-muted-foreground">Rebalance Frequency</div>
            <div className="font-medium capitalize">{portfolio.settings.rebalance_frequency}</div>
          </div>
        </div>
      </div>
    </div>
  );
};
