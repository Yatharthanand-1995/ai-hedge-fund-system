import React from 'react';
import { cn, formatCurrency, formatPercentage, formatTimeAgo, getRecommendationColorClass, getConfidenceColorClass } from '../../utils';
import { type StockAnalysis } from '../../types/api';
import { AgentScoreCard } from '../cards/AgentScoreCard';

interface StockAnalysisDisplayProps {
  analysis: StockAnalysis;
  className?: string;
}

export const StockAnalysisDisplay: React.FC<StockAnalysisDisplayProps> = ({
  analysis,
  className,
}) => {
  const { narrative, agent_results, market_data, symbol, timestamp } = analysis;

  return (
    <div className={cn('space-y-8', className)}>
      {/* Stock Header */}
      <div className="professional-card p-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6 mb-6">
          <div>
            <div className="flex items-center space-x-4 mb-2">
              <h1 className="text-3xl font-bold text-foreground">{symbol}</h1>
              <div className={cn('px-3 py-1 rounded-full text-sm font-medium', getRecommendationColorClass(narrative.recommendation))}>
                {narrative.recommendation}
              </div>
            </div>
            <div className="flex items-center space-x-4 text-muted-foreground text-sm">
              <span>Analysis completed {formatTimeAgo(timestamp)}</span>
              <span className={cn('font-medium', getConfidenceColorClass(narrative.confidence_level))}>
                {narrative.confidence_level} Confidence
              </span>
            </div>
          </div>

          {/* Price Info */}
          <div className="text-right">
            <div className="text-3xl font-bold text-foreground">
              {formatCurrency(market_data.current_price)}
            </div>
            <div className={cn('text-lg', market_data.price_change >= 0 ? 'text-green-400' : 'text-red-400')}>
              {market_data.price_change >= 0 ? '+' : ''}{formatCurrency(market_data.price_change)}
              ({formatPercentage(market_data.price_change_percent)})
            </div>
            <div className="text-sm text-muted-foreground">
              Previous close: {formatCurrency(market_data.previous_close)}
            </div>
          </div>
        </div>

        {/* Overall Score Display */}
        <div className="text-center py-6">
          <div className="text-6xl font-bold text-accent mb-2">
            {narrative.overall_score.toFixed(1)}
          </div>
          <div className="text-lg text-muted-foreground">Overall Score (out of 100)</div>
        </div>
      </div>

      {/* Agent Scores */}
      <div>
        <h2 className="section-header">4-Agent Analysis Breakdown</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <AgentScoreCard
            agent="fundamentals"
            score={agent_results.fundamentals.score}
            confidence={agent_results.fundamentals.confidence}
            reasoning={agent_results.fundamentals.reasoning}
          />
          <AgentScoreCard
            agent="momentum"
            score={agent_results.momentum.score}
            confidence={agent_results.momentum.confidence}
            reasoning={agent_results.momentum.reasoning}
          />
          <AgentScoreCard
            agent="quality"
            score={agent_results.quality.score}
            confidence={agent_results.quality.confidence}
            reasoning={agent_results.quality.reasoning}
          />
          <AgentScoreCard
            agent="sentiment"
            score={agent_results.sentiment.score}
            confidence={agent_results.sentiment.confidence}
            reasoning={agent_results.sentiment.reasoning}
          />
        </div>
      </div>

      {/* Investment Thesis */}
      <div className="professional-card p-6">
        <h2 className="section-header">Investment Thesis</h2>
        <div className="prose prose-invert max-w-none">
          <p className="text-foreground leading-relaxed">
            {narrative.investment_thesis}
          </p>
        </div>
      </div>

      {/* Strengths and Risks */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Key Strengths */}
        <div className="professional-card p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center">
            <span className="text-green-400 mr-2">✓</span>
            Key Strengths
          </h3>
          <ul className="space-y-2">
            {narrative.key_strengths.map((strength, index) => (
              <li key={index} className="flex items-start space-x-2">
                <span className="text-green-400 mt-1">•</span>
                <span className="text-muted-foreground">{strength}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Key Risks */}
        <div className="professional-card p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center">
            <span className="text-red-400 mr-2">⚠</span>
            Key Risks
          </h3>
          <ul className="space-y-2">
            {narrative.key_risks.map((risk, index) => (
              <li key={index} className="flex items-start space-x-2">
                <span className="text-red-400 mt-1">•</span>
                <span className="text-muted-foreground">{risk}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Market Data */}
      <div className="professional-card p-6">
        <h2 className="section-header">Market Data</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <div className="metric-label">Current Price</div>
            <div className="metric-value">{formatCurrency(market_data.current_price)}</div>
          </div>
          <div>
            <div className="metric-label">Volume</div>
            <div className="metric-value">{market_data.volume.toLocaleString()}</div>
          </div>
          <div>
            <div className="metric-label">Market Cap</div>
            <div className="metric-value">{formatCurrency(market_data.market_cap / 1e9)}B</div>
          </div>
          <div>
            <div className="metric-label">Previous Close</div>
            <div className="metric-value">{formatCurrency(market_data.previous_close)}</div>
          </div>
        </div>
      </div>

      {/* Agent Narratives */}
      <div className="space-y-6">
        <h2 className="section-header">Detailed Agent Analysis</h2>
        {Object.entries(narrative.agent_narratives).map(([agentType, agentNarrative]) => (
          <div key={agentType} className="professional-card p-6">
            <h3 className="text-lg font-semibold text-foreground mb-3 capitalize">
              {agentType} Agent Analysis
            </h3>
            <p className="text-muted-foreground leading-relaxed">
              {agentNarrative}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};