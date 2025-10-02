import React from 'react';
import { type PortfolioAnalysis } from '../../types/api';
import { cn, formatNumber, getScoreColorClass, formatTimeAgo } from '../../utils';
import { AgentScoreCard } from '../cards/AgentScoreCard';

interface PortfolioDisplayProps {
  analysis: PortfolioAnalysis;
  className?: string;
}

export const PortfolioDisplay: React.FC<PortfolioDisplayProps> = ({
  analysis,
  className,
}) => {
  const { portfolio_analysis, individual_analyses, portfolio_recommendations } = analysis;

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'Low': return 'text-green-400';
      case 'Moderate': return 'text-yellow-400';
      case 'High': return 'text-red-400';
      default: return 'text-muted-foreground';
    }
  };

  const getRecommendationColor = (recommendation: string) => {
    if (recommendation.includes('STRONG BUY')) return 'text-green-400';
    if (recommendation.includes('BUY')) return 'text-green-300';
    if (recommendation.includes('HOLD')) return 'text-yellow-400';
    if (recommendation.includes('SELL')) return 'text-red-400';
    return 'text-muted-foreground';
  };

  return (
    <div className={cn('space-y-6', className)}>
      {/* Portfolio Overview */}
      <div className="professional-card p-6">
        <h2 className="section-header">Portfolio Analysis</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          <div>
            <div className="metric-label">Portfolio Score</div>
            <div className={cn('metric-value text-2xl', getScoreColorClass(portfolio_analysis.portfolio_score))}>
              {portfolio_analysis.portfolio_score}
            </div>
          </div>

          <div>
            <div className="metric-label">Total Positions</div>
            <div className="metric-value">{portfolio_analysis.number_of_positions}</div>
          </div>

          <div>
            <div className="metric-label">Risk Level</div>
            <div className={cn('metric-value', getRiskColor(portfolio_analysis.risk_level))}>
              {portfolio_analysis.risk_level}
            </div>
          </div>

          <div>
            <div className="metric-label">High Risk Positions</div>
            <div className="metric-value">
              {portfolio_analysis.high_risk_positions}
              <span className="text-muted-foreground text-sm ml-1">
                / {portfolio_analysis.number_of_positions}
              </span>
            </div>
          </div>
        </div>

        {/* Portfolio Weights */}
        <div>
          <h3 className="text-lg font-semibold text-foreground mb-4">Position Weights</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {Object.entries(portfolio_analysis.weights).map(([symbol, weight]) => (
              <div key={symbol} className="flex justify-between items-center p-3 bg-muted/30 rounded-lg">
                <span className="font-medium text-foreground">{symbol}</span>
                <span className="text-accent font-medium">{(weight * 100).toFixed(1)}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Portfolio Recommendations */}
      <div className="professional-card p-6">
        <h2 className="section-header">Portfolio Recommendations</h2>
        <div className="space-y-3">
          {portfolio_recommendations.map((recommendation, index) => (
            <div key={index} className="flex items-start space-x-3">
              <div className="w-6 h-6 rounded-full bg-accent/20 text-accent flex items-center justify-center text-sm font-medium mt-0.5">
                {index + 1}
              </div>
              <p className="text-muted-foreground flex-1">{recommendation}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Individual Stock Analysis */}
      <div className="professional-card p-6">
        <h2 className="section-header">Individual Stock Analysis</h2>
        <div className="space-y-6">
          {individual_analyses.map((stock) => (
            <div key={stock.symbol} className="border border-gray-600 rounded-lg p-6">
              {/* Stock Header */}
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-xl font-semibold text-foreground">{stock.symbol}</h3>
                  <p className="text-muted-foreground">
                    Last updated: {formatTimeAgo(stock.timestamp)}
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-foreground">
                    ${formatNumber(stock.market_data.current_price)}
                  </div>
                  <div className={cn(
                    'text-sm font-medium',
                    stock.market_data.price_change >= 0 ? 'text-green-400' : 'text-red-400'
                  )}>
                    {stock.market_data.price_change >= 0 ? '+' : ''}{stock.market_data.price_change_percent.toFixed(2)}%
                  </div>
                </div>
              </div>

              {/* Agent Scores */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                {Object.entries(stock.narrative.agent_scores).map(([agent, score]) => (
                  <AgentScoreCard
                    key={agent}
                    agent={agent as any}
                    score={score}
                    confidence={0.85}
                    size="sm"
                  />
                ))}
              </div>

              {/* Investment Summary */}
              <div className="bg-muted/30 p-4 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-foreground">Recommendation:</span>
                  <span className={cn('font-semibold', getRecommendationColor(stock.narrative.recommendation))}>
                    {stock.narrative.recommendation}
                  </span>
                </div>
                <div className="flex items-center justify-between mb-3">
                  <span className="font-medium text-foreground">Overall Score:</span>
                  <span className={cn('text-xl font-bold', getScoreColorClass(stock.narrative.overall_score))}>
                    {stock.narrative.overall_score}
                  </span>
                </div>
                <div className="text-sm text-muted-foreground">
                  <p className="mb-2"><strong>Investment Thesis:</strong> {stock.narrative.investment_thesis}</p>

                  {stock.narrative.key_strengths.length > 0 && (
                    <div className="mb-2">
                      <strong className="text-foreground">Key Strengths:</strong>
                      <ul className="list-disc list-inside mt-1 space-y-1">
                        {stock.narrative.key_strengths.map((strength, idx) => (
                          <li key={idx}>{strength}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {stock.narrative.key_risks.length > 0 && (
                    <div>
                      <strong className="text-foreground">Key Risks:</strong>
                      <ul className="list-disc list-inside mt-1 space-y-1">
                        {stock.narrative.key_risks.map((risk, idx) => (
                          <li key={idx}>{risk}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};