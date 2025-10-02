import React, { useState } from 'react';
import { ChevronDown, ChevronRight, TrendingUp, TrendingDown } from 'lucide-react';
import { cn, formatCurrency, formatPercentage } from '../../utils';
import { ExpandedStockRow } from './ExpandedStockRow';

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

interface Stock {
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

interface StockScreenerTableProps {
  stocks: Stock[];
  onRowClick?: (stock: Stock) => void;
}

export const StockScreenerTable: React.FC<StockScreenerTableProps> = ({ stocks, onRowClick }) => {
  const [expandedRow, setExpandedRow] = useState<string | null>(null);

  const toggleRow = (symbol: string) => {
    setExpandedRow(expandedRow === symbol ? null : symbol);
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    if (score >= 40) return 'text-orange-400';
    return 'text-red-400';
  };

  const getScoreBg = (score: number) => {
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

  const getRiskLevel = (score: number) => {
    if (score >= 70) return { label: 'LOW', color: 'text-green-400' };
    if (score >= 50) return { label: 'MED', color: 'text-yellow-400' };
    return { label: 'HIGH', color: 'text-red-400' };
  };

  // Calculate target price and upside
  const calculateTargets = (stock: Stock) => {
    const targetPrice = stock.market_data.current_price * (1 + (stock.overall_score - 50) / 100);
    const upside = ((targetPrice - stock.market_data.current_price) / stock.market_data.current_price) * 100;
    return { targetPrice, upside };
  };

  return (
    <div className="professional-card overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b-2 border-border bg-muted/20">
              <th className="px-4 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider w-10">

              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Rank
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Symbol
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Price
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Change
              </th>
              <th className="px-4 py-3 text-center text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                AI Score
              </th>
              <th className="px-4 py-3 text-center text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Rec
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Target
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Upside
              </th>
              <th className="px-4 py-3 text-center text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Fund
              </th>
              <th className="px-4 py-3 text-center text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Mom
              </th>
              <th className="px-4 py-3 text-center text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Qual
              </th>
              <th className="px-4 py-3 text-center text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Sent
              </th>
              <th className="px-4 py-3 text-center text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Risk
              </th>
              <th className="px-4 py-3 text-center text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Conf
              </th>
            </tr>
          </thead>
          <tbody>
            {stocks.map((stock, index) => {
              const { targetPrice, upside } = calculateTargets(stock);
              const risk = getRiskLevel(stock.overall_score);
              const isExpanded = expandedRow === stock.symbol;

              return (
                <React.Fragment key={stock.symbol}>
                  <tr
                    className={cn(
                      'border-b border-border hover:bg-muted/10 transition-colors cursor-pointer',
                      isExpanded && 'bg-muted/20'
                    )}
                    onClick={() => toggleRow(stock.symbol)}
                  >
                    {/* Expand Button */}
                    <td className="px-4 py-3">
                      {isExpanded ? (
                        <ChevronDown className="h-4 w-4 text-accent" />
                      ) : (
                        <ChevronRight className="h-4 w-4 text-muted-foreground" />
                      )}
                    </td>

                    {/* Rank */}
                    <td className="px-4 py-3">
                      <div className="text-sm font-bold text-foreground">#{index + 1}</div>
                    </td>

                    {/* Symbol & Sector */}
                    <td className="px-4 py-3">
                      <div className="font-semibold text-foreground">{stock.symbol}</div>
                      <div className="text-xs text-muted-foreground">{stock.sector}</div>
                    </td>

                    {/* Price */}
                    <td className="px-4 py-3 text-right">
                      <div className="font-semibold text-foreground">
                        {formatCurrency(stock.market_data.current_price)}
                      </div>
                    </td>

                    {/* Change */}
                    <td className="px-4 py-3 text-right">
                      <div className={cn(
                        'flex items-center justify-end space-x-1',
                        stock.market_data.price_change >= 0 ? 'text-green-400' : 'text-red-400'
                      )}>
                        {stock.market_data.price_change >= 0 ? (
                          <TrendingUp className="h-3 w-3" />
                        ) : (
                          <TrendingDown className="h-3 w-3" />
                        )}
                        <span className="text-sm font-semibold">
                          {formatPercentage(stock.market_data.price_change_percent)}
                        </span>
                      </div>
                    </td>

                    {/* AI Score */}
                    <td className="px-4 py-3">
                      <div className="flex justify-center">
                        <div className={cn(
                          'px-3 py-1 rounded-lg text-center min-w-[60px]',
                          getScoreBg(stock.overall_score)
                        )}>
                          <div className={cn('text-lg font-bold', getScoreColor(stock.overall_score))}>
                            {stock.overall_score.toFixed(0)}
                          </div>
                        </div>
                      </div>
                    </td>

                    {/* Recommendation */}
                    <td className="px-4 py-3">
                      <div className="flex justify-center">
                        <span className={cn(
                          'px-2 py-1 rounded text-xs font-medium whitespace-nowrap',
                          getRecommendationColor(stock.recommendation)
                        )}>
                          {stock.recommendation}
                        </span>
                      </div>
                    </td>

                    {/* Target Price */}
                    <td className="px-4 py-3 text-right">
                      <div className="text-sm font-semibold text-accent">
                        {formatCurrency(targetPrice)}
                      </div>
                    </td>

                    {/* Upside */}
                    <td className="px-4 py-3 text-right">
                      <div className={cn(
                        'text-sm font-semibold',
                        upside >= 0 ? 'text-green-400' : 'text-red-400'
                      )}>
                        {upside >= 0 ? '+' : ''}{formatPercentage(upside)}
                      </div>
                    </td>

                    {/* Fundamentals */}
                    <td className="px-4 py-3 text-center">
                      <div className={cn('text-sm font-semibold', getScoreColor(stock.agent_scores.fundamentals))}>
                        {stock.agent_scores.fundamentals.toFixed(0)}
                      </div>
                    </td>

                    {/* Momentum */}
                    <td className="px-4 py-3 text-center">
                      <div className={cn('text-sm font-semibold', getScoreColor(stock.agent_scores.momentum))}>
                        {stock.agent_scores.momentum.toFixed(0)}
                      </div>
                    </td>

                    {/* Quality */}
                    <td className="px-4 py-3 text-center">
                      <div className={cn('text-sm font-semibold', getScoreColor(stock.agent_scores.quality))}>
                        {stock.agent_scores.quality.toFixed(0)}
                      </div>
                    </td>

                    {/* Sentiment */}
                    <td className="px-4 py-3 text-center">
                      <div className={cn('text-sm font-semibold', getScoreColor(stock.agent_scores.sentiment))}>
                        {stock.agent_scores.sentiment.toFixed(0)}
                      </div>
                    </td>

                    {/* Risk */}
                    <td className="px-4 py-3 text-center">
                      <div className={cn('text-xs font-bold', risk.color)}>
                        {risk.label}
                      </div>
                    </td>

                    {/* Confidence */}
                    <td className="px-4 py-3 text-center">
                      <div className="text-xs font-medium text-muted-foreground">
                        {stock.confidence_level}
                      </div>
                    </td>
                  </tr>

                  {/* Expanded Row */}
                  {isExpanded && (
                    <ExpandedStockRow stock={stock} onClose={() => setExpandedRow(null)} />
                  )}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
      </div>

      {stocks.length === 0 && (
        <div className="p-12 text-center">
          <div className="text-muted-foreground">No stocks match your filters</div>
        </div>
      )}
    </div>
  );
};