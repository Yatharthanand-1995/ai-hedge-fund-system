import React from 'react';
import {
  TrendingUp,
  TrendingDown,
  Brain,
  AlertTriangle,
  Target,
  Clock,
  DollarSign,
  Activity,
  Star,
  ArrowUp,
  ArrowDown,
  Minus
} from 'lucide-react';
import { cn, formatCurrency, formatPercentage } from '../../utils';

interface AgentScore {
  fundamentals: number;
  momentum: number;
  quality: number;
  sentiment: number;
}

interface ActionItem {
  type: 'buy' | 'sell' | 'hold' | 'monitor';
  urgency: 'high' | 'medium' | 'low';
  description: string;
  targetPrice?: number;
  timeframe?: string;
}

interface IntelligentStockData {
  symbol: string;
  companyName?: string;
  sector: string;
  overall_score: number;
  recommendation: string;
  confidence_level: string;
  agent_scores: AgentScore;
  market_data: {
    current_price: number;
    price_change: number;
    price_change_percent: number;
    volume?: number;
    market_cap?: number;
  };
  weight: number;
  investment_thesis: string;
  key_strengths: string[];
  key_risks: string[];
  nextAction: ActionItem;
  momentum: 'bullish' | 'bearish' | 'neutral';
  riskLevel: 'low' | 'medium' | 'high';
}

interface IntelligentStockCardProps {
  stock: IntelligentStockData;
  rank: number;
  className?: string;
  onActionClick?: (action: ActionItem, symbol: string) => void;
  onDetailsClick?: (symbol: string) => void;
}

export const IntelligentStockCard: React.FC<IntelligentStockCardProps> = ({
  stock,
  rank,
  className,
  onActionClick,
  onDetailsClick
}) => {
  const getRecommendationColor = (recommendation: string) => {
    switch (recommendation.toUpperCase()) {
      case 'STRONG BUY': return 'bg-green-600 text-green-100';
      case 'BUY':
      case 'WEAK BUY': return 'bg-green-500 text-green-100';
      case 'HOLD': return 'bg-yellow-500 text-yellow-100';
      case 'WEAK SELL':
      case 'SELL': return 'bg-red-500 text-red-100';
      default: return 'bg-gray-500 text-gray-100';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getConfidenceColor = (confidence: string) => {
    switch (confidence.toUpperCase()) {
      case 'HIGH': return 'text-green-400';
      case 'MEDIUM': return 'text-yellow-400';
      case 'LOW': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low': return 'text-green-400';
      case 'medium': return 'text-yellow-400';
      case 'high': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getMomentumIcon = (momentum: string) => {
    switch (momentum) {
      case 'bullish': return <ArrowUp className="h-4 w-4 text-green-400" />;
      case 'bearish': return <ArrowDown className="h-4 w-4 text-red-400" />;
      case 'neutral': return <Minus className="h-4 w-4 text-yellow-400" />;
      default: return <Minus className="h-4 w-4 text-gray-400" />;
    }
  };

  const getActionButtonColor = (actionType: string) => {
    switch (actionType) {
      case 'buy': return 'bg-green-600 hover:bg-green-700';
      case 'sell': return 'bg-red-600 hover:bg-red-700';
      case 'hold': return 'bg-yellow-600 hover:bg-yellow-700';
      case 'monitor': return 'bg-blue-600 hover:bg-blue-700';
      default: return 'bg-gray-600 hover:bg-gray-700';
    }
  };

  const getUrgencyIndicator = (urgency: string) => {
    switch (urgency) {
      case 'high': return '🔴';
      case 'medium': return '🟡';
      case 'low': return '🟢';
      default: return '⚪';
    }
  };

  return (
    <div className={cn('professional-card p-6 hover:shadow-lg transition-all duration-300', className)}>
      {/* Header with Rank and Basic Info */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="text-2xl font-bold text-foreground">#{rank}</div>
          <div>
            <div className="text-xl font-bold text-foreground">{stock.symbol}</div>
            <div className="text-sm text-muted-foreground">{stock.sector}</div>
          </div>
        </div>

        <div className="text-right">
          <div className={cn('px-3 py-1 rounded-full text-xs font-medium mb-2',
            getRecommendationColor(stock.recommendation))}>
            {stock.recommendation}
          </div>
          <div className="flex items-center space-x-1">
            <Star className="h-3 w-3 text-yellow-400" />
            <span className="text-sm font-medium">{stock.weight.toFixed(1)}%</span>
          </div>
        </div>
      </div>

      {/* Price and Score Row */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <div className="text-2xl font-bold text-foreground">
            {formatCurrency(stock.market_data.current_price)}
          </div>
          <div className={cn('text-sm flex items-center space-x-1',
            stock.market_data.price_change >= 0 ? 'text-green-400' : 'text-red-400')}>
            {stock.market_data.price_change >= 0 ?
              <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
            <span>
              {stock.market_data.price_change >= 0 ? '+' : ''}
              {formatCurrency(stock.market_data.price_change)}
              ({stock.market_data.price_change_percent >= 0 ? '+' : ''}
              {formatPercentage(stock.market_data.price_change_percent)})
            </span>
          </div>
        </div>

        <div className="text-center">
          <div className={cn('text-3xl font-bold', getScoreColor(stock.overall_score))}>
            {stock.overall_score.toFixed(1)}
          </div>
          <div className="text-xs text-muted-foreground">AI Score</div>
        </div>
      </div>

      {/* Agent Scores Mini Chart */}
      <div className="mb-4">
        <div className="text-sm text-muted-foreground mb-2">Agent Analysis</div>
        <div className="grid grid-cols-4 gap-1">
          <div className="text-center">
            <div className={cn('text-lg font-bold', getScoreColor(stock.agent_scores.fundamentals))}>
              {stock.agent_scores.fundamentals}
            </div>
            <div className="text-xs text-muted-foreground">Fund</div>
          </div>
          <div className="text-center">
            <div className={cn('text-lg font-bold', getScoreColor(stock.agent_scores.momentum))}>
              {stock.agent_scores.momentum}
            </div>
            <div className="text-xs text-muted-foreground">Mom</div>
          </div>
          <div className="text-center">
            <div className={cn('text-lg font-bold', getScoreColor(stock.agent_scores.quality))}>
              {stock.agent_scores.quality}
            </div>
            <div className="text-xs text-muted-foreground">Qual</div>
          </div>
          <div className="text-center">
            <div className={cn('text-lg font-bold', getScoreColor(stock.agent_scores.sentiment))}>
              {stock.agent_scores.sentiment}
            </div>
            <div className="text-xs text-muted-foreground">Sent</div>
          </div>
        </div>
      </div>

      {/* Status Indicators */}
      <div className="grid grid-cols-3 gap-2 mb-4">
        <div className="flex items-center space-x-1">
          <Brain className="h-4 w-4 text-muted-foreground" />
          <span className={cn('text-sm font-medium', getConfidenceColor(stock.confidence_level))}>
            {stock.confidence_level}
          </span>
        </div>
        <div className="flex items-center space-x-1">
          <Activity className="h-4 w-4 text-muted-foreground" />
          {getMomentumIcon(stock.momentum)}
          <span className="text-sm text-muted-foreground">{stock.momentum}</span>
        </div>
        <div className="flex items-center space-x-1">
          <AlertTriangle className={cn('h-4 w-4', getRiskColor(stock.riskLevel))} />
          <span className={cn('text-sm', getRiskColor(stock.riskLevel))}>
            {stock.riskLevel} risk
          </span>
        </div>
      </div>

      {/* Investment Thesis Preview */}
      <div className="mb-4">
        <div className="text-sm text-muted-foreground mb-1">Investment Thesis</div>
        <div className="text-sm text-foreground line-clamp-2">
          {stock.investment_thesis}
        </div>
      </div>

      {/* Key Points */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div>
          <div className="text-xs text-green-400 mb-1">Strengths</div>
          <div className="text-xs text-muted-foreground">
            • {stock.key_strengths[0] || 'Strong fundamentals'}
          </div>
        </div>
        <div>
          <div className="text-xs text-red-400 mb-1">Risks</div>
          <div className="text-xs text-muted-foreground">
            • {stock.key_risks[0] || 'Market volatility'}
          </div>
        </div>
      </div>

      {/* Next Action Section */}
      <div className="bg-muted/20 rounded-lg p-3 mb-4">
        <div className="flex items-center justify-between mb-2">
          <div className="text-sm font-medium text-foreground">Next Action</div>
          <div className="text-xs">
            {getUrgencyIndicator(stock.nextAction.urgency)} {stock.nextAction.urgency}
          </div>
        </div>
        <div className="text-sm text-muted-foreground mb-2">
          {stock.nextAction.description}
        </div>
        {stock.nextAction.targetPrice && (
          <div className="text-xs text-muted-foreground">
            Target: {formatCurrency(stock.nextAction.targetPrice)}
            {stock.nextAction.timeframe && ` by ${stock.nextAction.timeframe}`}
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex space-x-2">
        <button
          onClick={() => onActionClick?.(stock.nextAction, stock.symbol)}
          className={cn(
            'flex-1 text-white px-3 py-2 rounded-lg font-medium text-sm transition-colors',
            getActionButtonColor(stock.nextAction.type)
          )}
        >
          {stock.nextAction.type.toUpperCase()}
        </button>
        <button
          onClick={() => onDetailsClick?.(stock.symbol)}
          className="px-3 py-2 border border-border rounded-lg text-sm text-muted-foreground hover:bg-muted/20 transition-colors"
        >
          Details
        </button>
      </div>
    </div>
  );
};