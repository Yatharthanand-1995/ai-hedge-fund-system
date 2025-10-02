import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Loader2, RefreshCw } from 'lucide-react';
import { StockFilterBar } from '../components/screener/StockFilterBar';
import type { FilterState, SortConfig } from '../components/screener/StockFilterBar';
import { StockSummaryCards } from '../components/screener/StockSummaryCards';
import { StockScreenerTable } from '../components/screener/StockScreenerTable';

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

export const StockAnalysisPage: React.FC = () => {
  const [filters, setFilters] = useState<FilterState>({
    searchTerm: '',
    recommendation: '',
    sector: '',
    riskLevel: '',
    scoreRange: ''
  });

  const [sortConfig, setSortConfig] = useState<SortConfig>({
    field: 'overall_score',
    direction: 'desc'
  });

  // Fetch top 50 stocks from the API
  const { data: response, isLoading, error, refetch } = useQuery({
    queryKey: ['top-picks', 50],
    queryFn: async () => {
      const res = await fetch('http://localhost:8010/portfolio/top-picks?limit=50');
      if (!res.ok) throw new Error('Failed to fetch stocks');
      return res.json();
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 15 * 60 * 1000, // Auto-refresh every 15 minutes
  });

  const stocks: Stock[] = response?.top_picks || [];

  // Filter stocks
  const filteredStocks = useMemo(() => {
    return stocks.filter(stock => {
      // Search filter
      if (filters.searchTerm) {
        const term = filters.searchTerm.toLowerCase();
        if (!stock.symbol.toLowerCase().includes(term) &&
            !(stock.company_name || '').toLowerCase().includes(term)) {
          return false;
        }
      }

      // Recommendation filter
      if (filters.recommendation && stock.recommendation !== filters.recommendation) {
        return false;
      }

      // Sector filter
      if (filters.sector && stock.sector !== filters.sector) {
        return false;
      }

      // Risk level filter
      if (filters.riskLevel) {
        const score = stock.overall_score;
        if (filters.riskLevel === 'low' && score < 70) return false;
        if (filters.riskLevel === 'medium' && (score < 50 || score >= 70)) return false;
        if (filters.riskLevel === 'high' && score >= 50) return false;
      }

      // Score range filter
      if (filters.scoreRange) {
        const [min, max] = filters.scoreRange.split('-').map(Number);
        if (stock.overall_score < min || stock.overall_score > max) {
          return false;
        }
      }

      return true;
    });
  }, [stocks, filters]);

  // Sort stocks
  const sortedStocks = useMemo(() => {
    return [...filteredStocks].sort((a, b) => {
      const field = sortConfig.field;
      let aValue: any;
      let bValue: any;

      // Handle nested fields like market_data.price
      if (field.includes('.')) {
        const [parent, child] = field.split('.');
        aValue = (a as any)[parent]?.[child];
        bValue = (b as any)[parent]?.[child];
      } else {
        aValue = (a as any)[field];
        bValue = (b as any)[field];
      }

      // Handle string comparison
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sortConfig.direction === 'asc'
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      }

      // Handle numeric comparison
      return sortConfig.direction === 'asc' ? aValue - bValue : bValue - aValue;
    });
  }, [filteredStocks, sortConfig]);

  // Export to CSV
  const handleExport = () => {
    const headers = [
      'Rank',
      'Symbol',
      'Sector',
      'Price',
      'Change %',
      'AI Score',
      'Recommendation',
      'Fund Score',
      'Mom Score',
      'Qual Score',
      'Sent Score',
      'Confidence',
      'Weight %'
    ];

    const rows = sortedStocks.map((stock, index) => [
      index + 1,
      stock.symbol,
      stock.sector,
      stock.market_data.current_price.toFixed(2),
      stock.market_data.price_change_percent.toFixed(2),
      stock.overall_score.toFixed(1),
      stock.recommendation,
      stock.agent_scores.fundamentals.toFixed(0),
      stock.agent_scores.momentum.toFixed(0),
      stock.agent_scores.quality.toFixed(0),
      stock.agent_scores.sentiment.toFixed(0),
      stock.confidence_level,
      stock.weight.toFixed(2)
    ]);

    const csv = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `stock-analysis-${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold text-foreground mb-2">
            📊 AI Stock Screener
          </h1>
          <p className="text-xl text-muted-foreground">
            Real-time analysis of 50 elite stocks powered by 4-agent AI system
          </p>
        </div>

        <button
          onClick={() => refetch()}
          disabled={isLoading}
          className="flex items-center space-x-2 px-4 py-2 border border-border rounded-lg hover:bg-muted/20 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="professional-card p-12">
          <div className="flex flex-col items-center space-y-4">
            <Loader2 className="h-12 w-12 animate-spin text-accent" />
            <div className="text-center">
              <h3 className="text-lg font-semibold text-foreground mb-2">
                Loading Stock Data...
              </h3>
              <p className="text-muted-foreground">
                Fetching real-time analysis from our 4-agent system
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && !isLoading && (
        <div className="professional-card p-6 bg-red-50 border border-red-200">
          <div className="flex items-center space-x-3">
            <div className="text-red-400 text-xl">⚠️</div>
            <div>
              <h3 className="text-lg font-semibold text-red-900 mb-1">
                Failed to Load Data
              </h3>
              <p className="text-red-700">
                {error instanceof Error ? error.message : 'Unable to fetch stock data. Please try again.'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      {!isLoading && !error && stocks.length > 0 && (
        <>
          {/* Summary Cards */}
          <StockSummaryCards stocks={stocks} />

          {/* Filter Bar */}
          <StockFilterBar
            filters={filters}
            sortConfig={sortConfig}
            onFilterChange={setFilters}
            onSortChange={setSortConfig}
            onExport={handleExport}
            stockCount={sortedStocks.length}
          />

          {/* Stock Table */}
          <StockScreenerTable stocks={sortedStocks} />

          {/* Info Footer */}
          <div className="professional-card p-4 bg-blue-50 border border-blue-200">
            <div className="flex items-start space-x-3">
              <div className="text-blue-600 text-xl">💡</div>
              <div>
                <h4 className="font-semibold text-blue-900 mb-1">How to Use</h4>
                <ul className="text-sm text-blue-700 space-y-1">
                  <li>• <strong>Click any row</strong> to expand and see detailed analysis, investment thesis, strengths, and risks</li>
                  <li>• <strong>Use filters</strong> to narrow down stocks by recommendation, sector, risk level, or score range</li>
                  <li>• <strong>Sort columns</strong> to find top performers by score, price change, or other metrics</li>
                  <li>• <strong>Export data</strong> to CSV for further analysis in Excel or other tools</li>
                  <li>• <strong>Auto-refresh</strong> every 15 minutes for real-time market data</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Agent Info */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="professional-card p-4">
              <div className="text-2xl mb-2">📊</div>
              <h4 className="font-semibold text-foreground mb-1">Fundamentals (40%)</h4>
              <p className="text-sm text-muted-foreground">
                Financial health, profitability, growth rates, and valuation metrics
              </p>
            </div>

            <div className="professional-card p-4">
              <div className="text-2xl mb-2">📈</div>
              <h4 className="font-semibold text-foreground mb-1">Momentum (30%)</h4>
              <p className="text-sm text-muted-foreground">
                Technical indicators, price trends, and volume patterns
              </p>
            </div>

            <div className="professional-card p-4">
              <div className="text-2xl mb-2">⭐</div>
              <h4 className="font-semibold text-foreground mb-1">Quality (20%)</h4>
              <p className="text-sm text-muted-foreground">
                Business quality, competitive advantages, and operational efficiency
              </p>
            </div>

            <div className="professional-card p-4">
              <div className="text-2xl mb-2">💭</div>
              <h4 className="font-semibold text-foreground mb-1">Sentiment (10%)</h4>
              <p className="text-sm text-muted-foreground">
                Analyst ratings, target prices, and market sentiment
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  );
};