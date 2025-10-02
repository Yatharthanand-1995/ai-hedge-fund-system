import React from 'react';
import { TrendingUp, ShoppingCart, AlertTriangle, Target, PieChart } from 'lucide-react';
import { formatPercentage } from '../../utils';

interface Stock {
  overall_score: number;
  recommendation: string;
  market_data: {
    price_change_percent: number;
  };
  sector: string;
}

interface StockSummaryCardsProps {
  stocks: Stock[];
}

export const StockSummaryCards: React.FC<StockSummaryCardsProps> = ({ stocks }) => {
  // Calculate summary statistics
  const avgScore = stocks.reduce((sum, s) => sum + s.overall_score, 0) / stocks.length || 0;

  const strongBuys = stocks.filter(s =>
    s.recommendation === 'STRONG BUY' || s.recommendation === 'BUY'
  ).length;

  const highRisk = stocks.filter(s => s.overall_score < 50).length;

  const avgPriceChange = stocks.reduce((sum, s) =>
    sum + s.market_data.price_change_percent, 0
  ) / stocks.length || 0;

  // Calculate sector distribution
  const sectorCounts: Record<string, number> = {};
  stocks.forEach(s => {
    sectorCounts[s.sector] = (sectorCounts[s.sector] || 0) + 1;
  });
  const topSector = Object.entries(sectorCounts).sort((a, b) => b[1] - a[1])[0];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
      {/* Average AI Score */}
      <div className="professional-card p-4">
        <div className="flex items-center justify-between mb-2">
          <div className="text-sm text-muted-foreground">Avg AI Score</div>
          <TrendingUp className="h-4 w-4 text-accent" />
        </div>
        <div className="text-2xl font-bold text-foreground">
          {avgScore.toFixed(1)}
          <span className="text-sm text-muted-foreground ml-1">/ 100</span>
        </div>
        <div className="mt-1 text-xs text-muted-foreground">
          Portfolio average
        </div>
      </div>

      {/* Buy Recommendations */}
      <div className="professional-card p-4">
        <div className="flex items-center justify-between mb-2">
          <div className="text-sm text-muted-foreground">Buy Signals</div>
          <ShoppingCart className="h-4 w-4 text-green-400" />
        </div>
        <div className="text-2xl font-bold text-green-400">
          {strongBuys}
          <span className="text-sm text-muted-foreground ml-1">stocks</span>
        </div>
        <div className="mt-1 text-xs text-muted-foreground">
          Strong buy/buy rated
        </div>
      </div>

      {/* High Risk Count */}
      <div className="professional-card p-4">
        <div className="flex items-center justify-between mb-2">
          <div className="text-sm text-muted-foreground">High Risk</div>
          <AlertTriangle className="h-4 w-4 text-red-400" />
        </div>
        <div className="text-2xl font-bold text-red-400">
          {highRisk}
          <span className="text-sm text-muted-foreground ml-1">stocks</span>
        </div>
        <div className="mt-1 text-xs text-muted-foreground">
          Score below 50
        </div>
      </div>

      {/* Average Price Change */}
      <div className="professional-card p-4">
        <div className="flex items-center justify-between mb-2">
          <div className="text-sm text-muted-foreground">Avg Change</div>
          <Target className="h-4 w-4 text-accent" />
        </div>
        <div className={`text-2xl font-bold ${avgPriceChange >= 0 ? 'text-green-400' : 'text-red-400'}`}>
          {avgPriceChange >= 0 ? '+' : ''}{formatPercentage(avgPriceChange)}
        </div>
        <div className="mt-1 text-xs text-muted-foreground">
          Today's performance
        </div>
      </div>

      {/* Top Sector */}
      <div className="professional-card p-4">
        <div className="flex items-center justify-between mb-2">
          <div className="text-sm text-muted-foreground">Top Sector</div>
          <PieChart className="h-4 w-4 text-accent" />
        </div>
        <div className="text-2xl font-bold text-foreground">
          {topSector ? topSector[0] : 'N/A'}
        </div>
        <div className="mt-1 text-xs text-muted-foreground">
          {topSector ? `${topSector[1]} stocks` : 'No data'}
        </div>
      </div>
    </div>
  );
};