import React from 'react';
import {
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  Target,
  DollarSign,
  Activity,
  BarChart3,
  Brain,
  MessageSquare
} from 'lucide-react';
import { cn, formatCurrency, formatPercentage, formatNumber } from '../../utils';

interface AgentScores {
  fundamentals: number;
  momentum: number;
  quality: number;
  sentiment: number;
}

interface MarketData {
  current_price: number;
  previous_close: number;
  price_change: number;
  price_change_percent: number;
  volume?: number;
  market_cap?: number;
}

interface ExpandedStock {
  symbol: string;
  company_name?: string;
  sector: string;
  overall_score: number;
  recommendation: string;
  confidence_level: string;
  investment_thesis: string;
  key_strengths: string[];
  key_risks: string[];
  agent_scores: AgentScores;
  market_data: MarketData;
  weight: number;
}

interface ExpandedStockRowProps {
  stock: ExpandedStock;
  onClose: () => void;
}

export const ExpandedStockRow: React.FC<ExpandedStockRowProps> = ({ stock, onClose }) => {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    if (score >= 40) return 'text-orange-400';
    return 'text-red-400';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-green-500/20';
    if (score >= 60) return 'bg-yellow-500/20';
    if (score >= 40) return 'bg-orange-500/20';
    return 'bg-red-500/20';
  };

  const getRecommendationColor = (rec: string) => {
    switch (rec.toUpperCase()) {
      case 'STRONG BUY': return 'bg-green-600 text-green-100';
      case 'BUY': return 'bg-green-500 text-green-100';
      case 'WEAK BUY': return 'bg-green-400 text-green-900';
      case 'HOLD': return 'bg-yellow-500 text-yellow-100';
      case 'WEAK SELL': return 'bg-orange-500 text-orange-100';
      case 'SELL': return 'bg-red-500 text-red-100';
      default: return 'bg-gray-500 text-gray-100';
    }
  };

  // Calculate target price (simplified - would come from API in production)
  const targetPrice = stock.market_data.current_price * (1 + (stock.overall_score - 50) / 100);
  const upside = ((targetPrice - stock.market_data.current_price) / stock.market_data.current_price) * 100;

  return (
    <tr>
      <td colSpan={100} className="p-0">
        <div className="bg-muted/10 p-6 space-y-6 border-t-2 border-accent/50">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center space-x-3 mb-2">
              <h3 className="text-2xl font-bold text-foreground">{stock.symbol}</h3>
              <span className={cn('px-3 py-1 rounded-full text-sm font-medium', getRecommendationColor(stock.recommendation))}>
                {stock.recommendation}
              </span>
            </div>
            <p className="text-muted-foreground">{stock.company_name || stock.symbol} • {stock.sector}</p>
          </div>
          <button
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground transition-colors text-2xl"
          >
            ×
          </button>
        </div>

        {/* Price and Score Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="professional-card p-4">
            <div className="text-sm text-muted-foreground mb-1">Current Price</div>
            <div className="text-2xl font-bold text-foreground">{formatCurrency(stock.market_data.current_price)}</div>
            <div className={cn('text-sm flex items-center space-x-1 mt-1',
              stock.market_data.price_change >= 0 ? 'text-green-400' : 'text-red-400')}>
              {stock.market_data.price_change >= 0 ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
              <span>
                {stock.market_data.price_change >= 0 ? '+' : ''}
                {formatCurrency(stock.market_data.price_change)} ({formatPercentage(stock.market_data.price_change_percent)})
              </span>
            </div>
          </div>

          <div className="professional-card p-4">
            <div className="text-sm text-muted-foreground mb-1">AI Score</div>
            <div className={cn('text-3xl font-bold', getScoreColor(stock.overall_score))}>
              {stock.overall_score.toFixed(1)}
            </div>
            <div className="text-xs text-muted-foreground mt-1">Confidence: {stock.confidence_level}</div>
          </div>

          <div className="professional-card p-4">
            <div className="text-sm text-muted-foreground mb-1">Target Price</div>
            <div className="text-2xl font-bold text-accent">{formatCurrency(targetPrice)}</div>
            <div className={cn('text-sm mt-1', upside >= 0 ? 'text-green-400' : 'text-red-400')}>
              {upside >= 0 ? '+' : ''}{formatPercentage(upside)} upside
            </div>
          </div>

          <div className="professional-card p-4">
            <div className="text-sm text-muted-foreground mb-1">Portfolio Weight</div>
            <div className="text-2xl font-bold text-foreground">{stock.weight.toFixed(1)}%</div>
            <div className="text-xs text-muted-foreground mt-1">Suggested allocation</div>
          </div>
        </div>

        {/* Agent Scores Detailed */}
        <div>
          <h4 className="text-lg font-semibold text-foreground mb-3 flex items-center space-x-2">
            <Brain className="h-5 w-5 text-accent" />
            <span>4-Agent Analysis Breakdown</span>
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            {/* Fundamentals */}
            <div className={cn('p-4 rounded-lg', getScoreBgColor(stock.agent_scores.fundamentals))}>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <BarChart3 className="h-4 w-4" />
                  <span className="text-sm font-semibold">Fundamentals</span>
                </div>
                <span className={cn('text-xl font-bold', getScoreColor(stock.agent_scores.fundamentals))}>
                  {stock.agent_scores.fundamentals.toFixed(0)}
                </span>
              </div>
              <div className="text-xs text-muted-foreground">
                Financial health, profitability, growth, valuation metrics
              </div>
              <div className="mt-2 text-xs">
                <div className="font-medium">Weight: 40%</div>
              </div>
            </div>

            {/* Momentum */}
            <div className={cn('p-4 rounded-lg', getScoreBgColor(stock.agent_scores.momentum))}>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <Activity className="h-4 w-4" />
                  <span className="text-sm font-semibold">Momentum</span>
                </div>
                <span className={cn('text-xl font-bold', getScoreColor(stock.agent_scores.momentum))}>
                  {stock.agent_scores.momentum.toFixed(0)}
                </span>
              </div>
              <div className="text-xs text-muted-foreground">
                Technical indicators, price trends, volume patterns
              </div>
              <div className="mt-2 text-xs">
                <div className="font-medium">Weight: 30%</div>
              </div>
            </div>

            {/* Quality */}
            <div className={cn('p-4 rounded-lg', getScoreBgColor(stock.agent_scores.quality))}>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4" />
                  <span className="text-sm font-semibold">Quality</span>
                </div>
                <span className={cn('text-xl font-bold', getScoreColor(stock.agent_scores.quality))}>
                  {stock.agent_scores.quality.toFixed(0)}
                </span>
              </div>
              <div className="text-xs text-muted-foreground">
                Business quality, competitive moat, management
              </div>
              <div className="mt-2 text-xs">
                <div className="font-medium">Weight: 20%</div>
              </div>
            </div>

            {/* Sentiment */}
            <div className={cn('p-4 rounded-lg', getScoreBgColor(stock.agent_scores.sentiment))}>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <MessageSquare className="h-4 w-4" />
                  <span className="text-sm font-semibold">Sentiment</span>
                </div>
                <span className={cn('text-xl font-bold', getScoreColor(stock.agent_scores.sentiment))}>
                  {stock.agent_scores.sentiment.toFixed(0)}
                </span>
              </div>
              <div className="text-xs text-muted-foreground">
                Market sentiment, analyst ratings, news coverage
              </div>
              <div className="mt-2 text-xs">
                <div className="font-medium">Weight: 10%</div>
              </div>
            </div>
          </div>
        </div>

        {/* Investment Thesis */}
        <div>
          <h4 className="text-lg font-semibold text-foreground mb-3">Investment Thesis</h4>
          <div className="professional-card p-4">
            <p className="text-muted-foreground text-sm leading-relaxed whitespace-pre-line">
              {stock.investment_thesis}
            </p>
          </div>
        </div>

        {/* Key Points */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Strengths */}
          <div>
            <h4 className="text-lg font-semibold text-foreground mb-3 flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-green-400" />
              <span>Key Strengths</span>
            </h4>
            <div className="professional-card p-4 space-y-2">
              {stock.key_strengths.map((strength, idx) => (
                <div key={idx} className="flex items-start space-x-2">
                  <div className="text-green-400 mt-0.5">✓</div>
                  <div className="text-sm text-foreground">{strength}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Risks */}
          <div>
            <h4 className="text-lg font-semibold text-foreground mb-3 flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5 text-red-400" />
              <span>Key Risks</span>
            </h4>
            <div className="professional-card p-4 space-y-2">
              {stock.key_risks.map((risk, idx) => (
                <div key={idx} className="flex items-start space-x-2">
                  <div className="text-red-400 mt-0.5">⚠</div>
                  <div className="text-sm text-foreground">{risk}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Trading Metrics */}
        {stock.market_data.volume && stock.market_data.market_cap && (
          <div>
            <h4 className="text-lg font-semibold text-foreground mb-3">Market Metrics</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="professional-card p-3">
                <div className="text-xs text-muted-foreground mb-1">Volume</div>
                <div className="text-lg font-semibold text-foreground">
                  {formatNumber(stock.market_data.volume)}
                </div>
              </div>
              <div className="professional-card p-3">
                <div className="text-xs text-muted-foreground mb-1">Market Cap</div>
                <div className="text-lg font-semibold text-foreground">
                  ${(stock.market_data.market_cap / 1e9).toFixed(1)}B
                </div>
              </div>
              <div className="professional-card p-3">
                <div className="text-xs text-muted-foreground mb-1">Previous Close</div>
                <div className="text-lg font-semibold text-foreground">
                  {formatCurrency(stock.market_data.previous_close)}
                </div>
              </div>
              <div className="professional-card p-3">
                <div className="text-xs text-muted-foreground mb-1">Sector</div>
                <div className="text-lg font-semibold text-foreground">
                  {stock.sector}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex items-center space-x-3 pt-4 border-t border-border">
          <button className="flex-1 bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center justify-center space-x-2">
            <DollarSign className="h-5 w-5" />
            <span>Add to Portfolio</span>
          </button>
          <button className="flex-1 bg-accent hover:bg-accent/80 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center justify-center space-x-2">
            <Target className="h-5 w-5" />
            <span>Set Alert</span>
          </button>
          <button
            onClick={onClose}
            className="px-6 py-3 border border-border rounded-lg font-medium hover:bg-muted/20 transition-colors"
          >
            Close
          </button>
        </div>
        </div>
      </td>
    </tr>
  );
};