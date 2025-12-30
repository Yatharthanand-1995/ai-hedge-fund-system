import React from 'react';
import { type TopPicksResponse } from '../../types/api';
import { cn, formatNumber, getScoreColorClass, formatTimeAgo } from '../../utils';
import { AgentScoreCard } from '../cards/AgentScoreCard';

interface TopPicksDisplayProps {
  topPicks: TopPicksResponse;
  onAddToPortfolio?: (symbol: string) => void;
  className?: string;
}

export const TopPicksDisplay: React.FC<TopPicksDisplayProps> = ({
  topPicks,
  onAddToPortfolio,
  className,
}) => {
  const getRecommendationColor = (recommendation: string) => {
    if (recommendation.includes('STRONG BUY')) return 'text-green-400';
    if (recommendation.includes('BUY')) return 'text-green-300';
    if (recommendation.includes('HOLD')) return 'text-yellow-400';
    if (recommendation.includes('SELL')) return 'text-red-400';
    return 'text-muted-foreground';
  };

  const getConfidenceColor = (confidence: string) => {
    switch (confidence) {
      case 'HIGH': return 'text-green-400';
      case 'MEDIUM': return 'text-yellow-400';
      case 'LOW': return 'text-red-400';
      default: return 'text-muted-foreground';
    }
  };

  return (
    <div className={cn('space-y-6', className)}>
      {/* Header */}
      <div className="professional-card p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="section-header">Top Investment Picks</h2>
            <p className="text-muted-foreground">
              {topPicks.selection_criteria}
            </p>
          </div>
          <div className="text-right">
            <div className="metric-label">Stocks Analyzed</div>
            <div className="metric-value">{topPicks.total_analyzed}</div>
          </div>
        </div>
        <div className="text-sm text-muted-foreground">
          Last updated: {formatTimeAgo(topPicks.timestamp)}
        </div>
      </div>

      {/* Top Picks Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {topPicks.top_picks.map((pick, index) => (
          <div key={pick.symbol} className="professional-card p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 rounded-full bg-accent text-accent-foreground flex items-center justify-center font-bold">
                  {index + 1}
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-foreground">{pick.symbol}</h3>
                  <p className="text-sm text-muted-foreground">{pick.company_name}</p>
                  <p className="text-xs text-muted-foreground">{pick.sector}</p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-foreground">
                  ${formatNumber(pick.market_data.current_price)}
                </div>
                <div className={cn(
                  'text-sm font-medium',
                  pick.market_data.price_change >= 0 ? 'text-green-400' : 'text-red-400'
                )}>
                  {pick.market_data.price_change >= 0 ? '+' : ''}{pick.market_data.price_change_percent.toFixed(2)}%
                </div>
              </div>
            </div>

            {/* Scores */}
            <div className="flex items-center justify-between mb-4">
              <div>
                <div className="metric-label">Overall Score</div>
                <div className={cn('text-3xl font-bold', getScoreColorClass(pick.overall_score))}>
                  {pick.overall_score}
                </div>
              </div>
              <div className="text-right">
                <div className={cn('font-semibold', getRecommendationColor(pick.recommendation))}>
                  {pick.recommendation}
                </div>
                <div className={cn('text-sm', getConfidenceColor(pick.confidence_level))}>
                  {pick.confidence_level} Confidence
                </div>
              </div>
            </div>

            {/* Agent Scores */}
            <div className="grid grid-cols-2 gap-3 mb-4">
              {Object.entries(pick.agent_scores).map(([agent, score]) => (
                <AgentScoreCard
                  key={agent}
                  agent={agent as any}
                  score={score}
                  confidence={0.85}
                  size="sm"
                />
              ))}
            </div>

            {/* Investment Thesis */}
            <div className="bg-muted/30 p-4 rounded-lg mb-4">
              <h4 className="font-semibold text-foreground mb-2">Investment Thesis</h4>
              <p className="text-sm text-muted-foreground mb-3">{pick.investment_thesis}</p>

              {pick.key_strengths.length > 0 && (
                <div className="mb-3">
                  <h5 className="text-sm font-medium text-foreground mb-1">Key Strengths:</h5>
                  <ul className="text-xs text-muted-foreground space-y-1">
                    {pick.key_strengths.slice(0, 2).map((strength, idx) => (
                      <li key={idx} className="flex items-start">
                        <span className="text-green-400 mr-2">✓</span>
                        <span className="flex-1">{strength}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {pick.key_risks.length > 0 && (
                <div>
                  <h5 className="text-sm font-medium text-foreground mb-1">Key Risks:</h5>
                  <ul className="text-xs text-muted-foreground space-y-1">
                    {pick.key_risks.slice(0, 2).map((risk, idx) => (
                      <li key={idx} className="flex items-start">
                        <span className="text-yellow-400 mr-2">⚠</span>
                        <span className="flex-1">{risk}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Market Data */}
            <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
              <div>
                <div className="text-muted-foreground">Volume</div>
                <div className="font-medium text-foreground">
                  {formatNumber(pick.market_data.volume)}
                </div>
              </div>
              <div>
                <div className="text-muted-foreground">Market Cap</div>
                <div className="font-medium text-foreground">
                  ${formatNumber(pick.market_data.market_cap / 1e9, 1)}B
                </div>
              </div>
            </div>

            {/* Action Button */}
            {onAddToPortfolio && (
              <button
                onClick={() => onAddToPortfolio(pick.symbol)}
                className={cn(
                  'w-full py-2 px-4 rounded-lg text-sm font-medium transition-colors',
                  'bg-accent/20 text-accent hover:bg-accent/30',
                  'border border-accent/30 hover:border-accent/50'
                )}
              >
                Add to Portfolio
              </button>
            )}
          </div>
        ))}
      </div>

      {/* Performance Note */}
      <div className="professional-card p-4">
        <div className="flex items-center space-x-2 text-sm text-muted-foreground">
          <span>💡</span>
          <span>
            Rankings based on our 5-agent analysis framework: 36% fundamentals, 27% momentum, 18% quality, 9% sentiment, 10% institutional flow
          </span>
        </div>
      </div>
    </div>
  );
};