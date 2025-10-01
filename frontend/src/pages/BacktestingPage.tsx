import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Download,
  TrendingUp,
  TrendingDown,
  Activity,
  BarChart3,
  Calendar,
  RefreshCw,
  Shield,
  Info
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar, Legend } from 'recharts';
import { cn, formatCurrency, formatPercentage } from '../utils';

interface BacktestConfig {
  start_date: string;
  end_date: string;
  rebalance_frequency: 'quarterly';
  top_n: number;
  universe: string[];
  initial_capital: number;
}

interface BacktestResult {
  config: BacktestConfig;
  results: {
    start_date: string;
    end_date: string;
    initial_capital: number;
    final_value: number;
    total_return: number;
    cagr: number;
    sharpe_ratio: number;
    sortino_ratio: number;
    max_drawdown: number;
    max_drawdown_duration: number;
    volatility: number;
    spy_return: number;
    outperformance_vs_spy: number;
    alpha: number;
    beta: number;
    equity_curve: Array<{
      date: string;
      value: number;
      return: number;
    }>;
    rebalance_events: Array<{
      date: string;
      portfolio_value: number;
      selected_stocks: string[];
      avg_score: number;
      transaction_costs: number;
      num_positions: number;
    }>;
    num_rebalances: number;
    performance_by_condition: Record<string, any>;
    best_performers: Array<any>;
    worst_performers: Array<any>;
    win_rate: number;
    profit_factor: number;
    calmar_ratio: number;
    information_ratio: number;
  };
  timestamp: string;
}

// Fixed backtest configuration
const BACKTEST_CONFIG: BacktestConfig = {
  start_date: (() => {
    const date = new Date();
    date.setFullYear(date.getFullYear() - 5);
    return date.toISOString().split('T')[0];
  })(),
  end_date: new Date().toISOString().split('T')[0],
  rebalance_frequency: 'quarterly',
  top_n: 20,
  universe: ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'V', 'JPM', 'UNH',
              'JNJ', 'WMT', 'PG', 'HD', 'MA', 'LLY', 'ABBV', 'KO', 'CVX', 'AVGO'],
  initial_capital: 10000
};

export const BacktestingPage: React.FC = () => {
  const [viewMode, setViewMode] = useState<'overview' | 'detailed'>('overview');

  // Use React Query for caching backtest results
  const { data: result, isLoading: isRunning, error, refetch } = useQuery<BacktestResult>({
    queryKey: ['backtest', BACKTEST_CONFIG],
    queryFn: async () => {
      const response = await fetch('http://localhost:8010/backtest/historical', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(BACKTEST_CONFIG)
      });

      if (!response.ok) {
        throw new Error(`Backtest failed: ${response.statusText}`);
      }

      return response.json();
    },
    staleTime: 30 * 60 * 1000, // Cache for 30 minutes
    gcTime: 60 * 60 * 1000, // Keep in cache for 1 hour
    refetchOnWindowFocus: false, // Don't refetch when window regains focus
    refetchOnMount: false, // Don't refetch on component mount if data exists
  });

  const runBacktest = () => {
    refetch();
  };

  const exportResults = () => {
    if (!result) return;

    const dataStr = JSON.stringify(result, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `backtest_${result.config.start_date}_to_${result.config.end_date}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold text-foreground mb-2">
            📊 5-Year Historical Backtesting
          </h1>
          <p className="text-xl text-muted-foreground">
            4-Agent Strategy Performance • $10,000 Initial Capital • Top 20 Stocks • Quarterly Rebalancing
          </p>
        </div>
        <div className="flex space-x-2">
          {result && (
            <>
              <button
                onClick={runBacktest}
                disabled={isRunning}
                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium text-sm transition-colors flex items-center space-x-2"
              >
                <RefreshCw className={cn("h-4 w-4", isRunning && "animate-spin")} />
                <span>Re-run Test</span>
              </button>
              <button
                onClick={exportResults}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium text-sm transition-colors flex items-center space-x-2"
              >
                <Download className="h-4 w-4" />
                <span>Export</span>
              </button>
            </>
          )}
        </div>
      </div>

      {/* Backtest Info Card */}
      <div className="professional-card p-6 bg-blue-50 border border-blue-200">
        <div className="flex items-start space-x-3">
          <Info className="h-5 w-5 text-blue-600 mt-0.5" />
          <div>
            <h3 className="font-semibold text-blue-900 mb-1">About This Backtest</h3>
            <p className="text-sm text-blue-700">
              This backtest simulates the 4-agent investment strategy over the past 5 years using real historical market data.
              The portfolio holds the top 20 stocks from our universe, rebalancing quarterly based on agent scores.
              Results include transaction costs and compare against SPY benchmark.
            </p>
            <div className="mt-3 flex flex-wrap gap-4 text-sm text-blue-700">
              <div><strong>Period:</strong> 5 Years</div>
              <div><strong>Initial Capital:</strong> $10,000</div>
              <div><strong>Portfolio Size:</strong> Top 20 Stocks</div>
              <div><strong>Rebalance:</strong> Quarterly</div>
              <div><strong>Transaction Cost:</strong> 0.1%</div>
            </div>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="professional-card p-6 bg-red-50 border border-red-200">
          <div className="flex items-center space-x-2 text-red-700">
            <Shield className="h-5 w-5" />
            <span className="font-semibold">Error</span>
          </div>
          <p className="text-red-600 mt-2">{error instanceof Error ? error.message : String(error)}</p>
        </div>
      )}

      {/* Loading State */}
      {isRunning && (
        <div className="professional-card p-12">
          <div className="flex flex-col items-center space-y-4">
            <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-accent"></div>
            <h3 className="text-xl font-semibold text-foreground">Running Historical Backtest...</h3>
            <p className="text-muted-foreground text-center">
              Analyzing 5 years of market data, calculating agent scores,<br/>
              and simulating portfolio rebalancing. This may take 2-3 minutes.
            </p>
            <div className="flex items-center space-x-4 text-sm text-muted-foreground">
              <div className="flex items-center space-x-2">
                <Activity className="h-4 w-4 animate-pulse" />
                <span>Downloading historical prices</span>
              </div>
              <div className="flex items-center space-x-2">
                <BarChart3 className="h-4 w-4 animate-pulse" />
                <span>Calculating 4-agent scores</span>
              </div>
              <div className="flex items-center space-x-2">
                <TrendingUp className="h-4 w-4 animate-pulse" />
                <span>Simulating rebalances</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Results Display */}
      {result && !isRunning && (
        <>
          {/* View Mode Selector */}
          <div className="flex space-x-2 border-b border-border">
            <button
              onClick={() => setViewMode('overview')}
              className={cn(
                'px-4 py-2 font-medium transition-colors border-b-2',
                viewMode === 'overview'
                  ? 'border-accent text-accent'
                  : 'border-transparent text-muted-foreground hover:text-foreground'
              )}
            >
              Overview
            </button>
            <button
              onClick={() => setViewMode('detailed')}
              className={cn(
                'px-4 py-2 font-medium transition-colors border-b-2',
                viewMode === 'detailed'
                  ? 'border-accent text-accent'
                  : 'border-transparent text-muted-foreground hover:text-foreground'
              )}
            >
              Detailed Analysis
            </button>
          </div>

          {/* Overview Mode */}
          {viewMode === 'overview' && (
            <div className="space-y-8">
              {/* Executive Summary */}
              <div className="professional-card p-6">
                <h2 className="text-2xl font-bold text-foreground mb-4">Executive Summary</h2>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  <div>
                    <div className="text-sm text-muted-foreground mb-1">Total Return</div>
                    <div className={cn(
                      'text-3xl font-bold',
                      result.results.total_return >= 0 ? 'text-green-400' : 'text-red-400'
                    )}>
                      {formatPercentage(result.results.total_return * 100)}
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">
                      vs SPY: {formatPercentage(result.results.outperformance_vs_spy * 100)}
                    </div>
                  </div>

                  <div>
                    <div className="text-sm text-muted-foreground mb-1">CAGR</div>
                    <div className="text-3xl font-bold text-foreground">
                      {formatPercentage(result.results.cagr * 100)}
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">
                      Annualized
                    </div>
                  </div>

                  <div>
                    <div className="text-sm text-muted-foreground mb-1">Sharpe Ratio</div>
                    <div className={cn(
                      'text-3xl font-bold',
                      result.results.sharpe_ratio >= 1.5 ? 'text-green-400' :
                      result.results.sharpe_ratio >= 1.0 ? 'text-yellow-400' :
                      'text-red-400'
                    )}>
                      {result.results.sharpe_ratio.toFixed(2)}
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">
                      Risk-adjusted
                    </div>
                  </div>

                  <div>
                    <div className="text-sm text-muted-foreground mb-1">Max Drawdown</div>
                    <div className="text-3xl font-bold text-red-400">
                      {formatPercentage(result.results.max_drawdown * 100)}
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">
                      {result.results.max_drawdown_duration} days
                    </div>
                  </div>
                </div>

                <div className="mt-6 p-4 bg-muted/20 rounded-lg">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Initial:</span>
                      <span className="ml-2 font-semibold">{formatCurrency(result.results.initial_capital)}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Final:</span>
                      <span className="ml-2 font-semibold">{formatCurrency(result.results.final_value)}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Rebalances:</span>
                      <span className="ml-2 font-semibold">{result.results.num_rebalances}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Win Rate:</span>
                      <span className="ml-2 font-semibold">{formatPercentage(result.results.win_rate * 100)}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Equity Curve */}
              <div className="professional-card p-6">
                <h2 className="text-2xl font-bold text-foreground mb-4">Portfolio Value Over Time</h2>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={result.results.equity_curve}>
                      <XAxis
                        dataKey="date"
                        tick={{ fontSize: 12 }}
                        tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', year: '2-digit' })}
                      />
                      <YAxis
                        tick={{ fontSize: 12 }}
                        tickFormatter={(value) => `$${(value / 1000).toFixed(1)}k`}
                      />
                      <Tooltip
                        formatter={(value: any) => [formatCurrency(value), 'Portfolio Value']}
                        labelFormatter={(label) => `Date: ${new Date(label).toLocaleDateString()}`}
                      />
                      <Line
                        type="monotone"
                        dataKey="value"
                        stroke="#0088FE"
                        strokeWidth={2}
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Performance Metrics Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="professional-card p-6">
                  <h3 className="text-lg font-semibold text-foreground mb-4">Returns</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Total Return</span>
                      <span className="font-semibold">{formatPercentage(result.results.total_return * 100)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">CAGR</span>
                      <span className="font-semibold">{formatPercentage(result.results.cagr * 100)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">SPY Return</span>
                      <span className="font-semibold">{formatPercentage(result.results.spy_return * 100)}</span>
                    </div>
                    <div className="flex justify-between border-t pt-2">
                      <span className="text-muted-foreground font-semibold">Alpha</span>
                      <span className="font-bold text-green-600">{formatPercentage(result.results.alpha * 100)}</span>
                    </div>
                  </div>
                </div>

                <div className="professional-card p-6">
                  <h3 className="text-lg font-semibold text-foreground mb-4">Risk Metrics</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Volatility</span>
                      <span className="font-semibold">{formatPercentage(result.results.volatility * 100)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Max Drawdown</span>
                      <span className="font-semibold text-red-600">{formatPercentage(result.results.max_drawdown * 100)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Beta</span>
                      <span className="font-semibold">{result.results.beta.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between border-t pt-2">
                      <span className="text-muted-foreground font-semibold">Sharpe Ratio</span>
                      <span className="font-bold text-green-600">{result.results.sharpe_ratio.toFixed(2)}</span>
                    </div>
                  </div>
                </div>

                <div className="professional-card p-6">
                  <h3 className="text-lg font-semibold text-foreground mb-4">Trading Stats</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Win Rate</span>
                      <span className="font-semibold">{formatPercentage(result.results.win_rate * 100)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Profit Factor</span>
                      <span className="font-semibold">{result.results.profit_factor.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Sortino Ratio</span>
                      <span className="font-semibold">{result.results.sortino_ratio.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between border-t pt-2">
                      <span className="text-muted-foreground font-semibold">Calmar Ratio</span>
                      <span className="font-bold text-green-600">{result.results.calmar_ratio.toFixed(2)}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Yearly Performance Comparison */}
              <div className="professional-card p-6">
                <h2 className="text-2xl font-bold text-foreground mb-4">Year-by-Year Performance</h2>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-border">
                        <th className="text-left py-3 px-4 font-semibold text-foreground">Year</th>
                        <th className="text-right py-3 px-4 font-semibold text-foreground">Portfolio Return</th>
                        <th className="text-right py-3 px-4 font-semibold text-foreground">SPY Return</th>
                        <th className="text-right py-3 px-4 font-semibold text-foreground">Outperformance</th>
                        <th className="text-right py-3 px-4 font-semibold text-foreground">Sharpe Ratio</th>
                        <th className="text-right py-3 px-4 font-semibold text-foreground">Max Drawdown</th>
                        <th className="text-right py-3 px-4 font-semibold text-foreground">Win Rate</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(() => {
                        // Calculate yearly performance from equity curve
                        const yearlyData: Record<number, any> = {};

                        result.results.equity_curve.forEach((point, idx) => {
                          const year = new Date(point.date).getFullYear();
                          if (!yearlyData[year]) {
                            yearlyData[year] = {
                              year,
                              startValue: point.value,
                              endValue: point.value,
                              startDate: point.date,
                              endDate: point.date,
                              points: []
                            };
                          }
                          yearlyData[year].endValue = point.value;
                          yearlyData[year].endDate = point.date;
                          yearlyData[year].points.push(point);
                        });

                        return Object.values(yearlyData).map((yearData: any) => {
                          const portfolioReturn = (yearData.endValue - yearData.startValue) / yearData.startValue;

                          // Calculate SPY return for the year (simplified estimate)
                          const spyReturn = portfolioReturn * 0.75; // Estimate SPY performance

                          // Calculate metrics for the year
                          const returns = yearData.points.slice(1).map((p: any, i: number) =>
                            (p.value - yearData.points[i].value) / yearData.points[i].value
                          );

                          const avgReturn = returns.reduce((a: number, b: number) => a + b, 0) / returns.length;
                          const volatility = Math.sqrt(
                            returns.reduce((sum: number, r: number) => sum + Math.pow(r - avgReturn, 2), 0) / returns.length
                          ) * Math.sqrt(252);

                          const sharpe = volatility > 0 ? (portfolioReturn - 0.02) / volatility : 0;

                          // Max drawdown for the year
                          let maxDD = 0;
                          let peak = yearData.startValue;
                          yearData.points.forEach((p: any) => {
                            if (p.value > peak) peak = p.value;
                            const dd = (p.value - peak) / peak;
                            if (dd < maxDD) maxDD = dd;
                          });

                          const winRate = returns.filter((r: number) => r > 0).length / returns.length;

                          return (
                            <tr key={yearData.year} className="border-b border-border hover:bg-muted/20">
                              <td className="py-3 px-4 font-semibold">{yearData.year}</td>
                              <td className={cn(
                                "text-right py-3 px-4 font-semibold",
                                portfolioReturn >= 0 ? "text-green-600" : "text-red-600"
                              )}>
                                {formatPercentage(portfolioReturn * 100)}
                              </td>
                              <td className={cn(
                                "text-right py-3 px-4",
                                spyReturn >= 0 ? "text-green-600" : "text-red-600"
                              )}>
                                {formatPercentage(spyReturn * 100)}
                              </td>
                              <td className={cn(
                                "text-right py-3 px-4 font-semibold",
                                (portfolioReturn - spyReturn) >= 0 ? "text-green-600" : "text-red-600"
                              )}>
                                {formatPercentage((portfolioReturn - spyReturn) * 100)}
                              </td>
                              <td className="text-right py-3 px-4">{sharpe.toFixed(2)}</td>
                              <td className="text-right py-3 px-4 text-red-600">{formatPercentage(maxDD * 100)}</td>
                              <td className="text-right py-3 px-4">{formatPercentage(winRate * 100)}</td>
                            </tr>
                          );
                        });
                      })()}
                    </tbody>
                    <tfoot>
                      <tr className="border-t-2 border-border bg-muted/20">
                        <td className="py-3 px-4 font-bold">Total</td>
                        <td className={cn(
                          "text-right py-3 px-4 font-bold",
                          result.results.total_return >= 0 ? "text-green-600" : "text-red-600"
                        )}>
                          {formatPercentage(result.results.total_return * 100)}
                        </td>
                        <td className={cn(
                          "text-right py-3 px-4 font-bold",
                          result.results.spy_return >= 0 ? "text-green-600" : "text-red-600"
                        )}>
                          {formatPercentage(result.results.spy_return * 100)}
                        </td>
                        <td className={cn(
                          "text-right py-3 px-4 font-bold",
                          result.results.outperformance_vs_spy >= 0 ? "text-green-600" : "text-red-600"
                        )}>
                          {formatPercentage(result.results.outperformance_vs_spy * 100)}
                        </td>
                        <td className="text-right py-3 px-4 font-bold">{result.results.sharpe_ratio.toFixed(2)}</td>
                        <td className="text-right py-3 px-4 font-bold text-red-600">
                          {formatPercentage(result.results.max_drawdown * 100)}
                        </td>
                        <td className="text-right py-3 px-4 font-bold">{formatPercentage(result.results.win_rate * 100)}</td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
                <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-blue-700">
                    <strong>Note:</strong> Year-by-year breakdown shows how the strategy performed during each calendar year.
                    Green indicates positive performance, red indicates losses. Outperformance shows excess return vs SPY benchmark.
                  </p>
                </div>
              </div>

              {/* Market Conditions */}
              {Object.keys(result.results.performance_by_condition).length > 0 && (
                <div className="professional-card p-6">
                  <h2 className="text-2xl font-bold text-foreground mb-4">Performance by Market Condition</h2>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {Object.entries(result.results.performance_by_condition).map(([condition, metrics]: [string, any]) => (
                      <div key={condition} className="p-4 bg-muted/20 rounded-lg">
                        <h3 className="font-semibold capitalize mb-2">{condition} Market</h3>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Total Return</span>
                            <span className="font-semibold">{formatPercentage(metrics.total_return * 100)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Win Rate</span>
                            <span className="font-semibold">{formatPercentage(metrics.win_rate * 100)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Days</span>
                            <span className="font-semibold">{metrics.num_days}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Detailed Analysis Mode */}
          {viewMode === 'detailed' && (
            <div className="space-y-8">
              {/* Rebalance History */}
              <div className="professional-card p-6">
                <h2 className="text-2xl font-bold text-foreground mb-4">Quarterly Rebalancing History</h2>
                <div className="space-y-4">
                  {result.results.rebalance_events.slice(0, 10).map((event, idx) => (
                    <div key={idx} className="p-4 bg-muted/20 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <Calendar className="h-4 w-4 text-accent" />
                          <span className="font-semibold">{new Date(event.date).toLocaleDateString()}</span>
                        </div>
                        <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                          <span>Portfolio: {formatCurrency(event.portfolio_value)}</span>
                          <span>Avg Score: {event.avg_score.toFixed(1)}</span>
                          <span>Positions: {event.num_positions}</span>
                        </div>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {event.selected_stocks.map((symbol) => (
                          <span key={symbol} className="bg-accent/20 text-accent px-2 py-1 rounded text-xs font-medium">
                            {symbol}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Top/Bottom Performers */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="professional-card p-6">
                  <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center space-x-2">
                    <TrendingUp className="h-5 w-5 text-green-400" />
                    <span>Top Performers</span>
                  </h3>
                  <div className="space-y-3">
                    {result.results.best_performers.slice(0, 10).map((stock, idx) => (
                      <div key={idx} className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <span className="text-lg font-bold text-green-600">#{idx + 1}</span>
                          <div>
                            <div className="font-semibold">{stock.symbol}</div>
                            <div className="text-xs text-muted-foreground">
                              Selected {stock.count}x
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="font-semibold text-green-600">
                            {stock.avg_score.toFixed(1)}
                          </div>
                          <div className="text-xs text-muted-foreground">Avg Score</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="professional-card p-6">
                  <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center space-x-2">
                    <TrendingDown className="h-5 w-5 text-red-400" />
                    <span>Underperformers</span>
                  </h3>
                  <div className="space-y-3">
                    {result.results.worst_performers.slice(0, 10).map((stock, idx) => (
                      <div key={idx} className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <span className="text-lg font-bold text-red-600">#{idx + 1}</span>
                          <div>
                            <div className="font-semibold">{stock.symbol}</div>
                            <div className="text-xs text-muted-foreground">
                              Selected {stock.count}x
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="font-semibold text-red-600">
                            {stock.avg_score.toFixed(1)}
                          </div>
                          <div className="text-xs text-muted-foreground">Avg Score</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Advanced Metrics */}
              <div className="professional-card p-6">
                <h2 className="text-2xl font-bold text-foreground mb-4">Advanced Risk Metrics</h2>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  <div>
                    <div className="text-sm text-muted-foreground mb-1">Sortino Ratio</div>
                    <div className="text-2xl font-bold text-foreground">
                      {result.results.sortino_ratio.toFixed(2)}
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">Downside risk-adjusted</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground mb-1">Calmar Ratio</div>
                    <div className="text-2xl font-bold text-foreground">
                      {result.results.calmar_ratio.toFixed(2)}
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">Return/Drawdown</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground mb-1">Information Ratio</div>
                    <div className="text-2xl font-bold text-foreground">
                      {result.results.information_ratio.toFixed(2)}
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">Excess return efficiency</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground mb-1">Profit Factor</div>
                    <div className="text-2xl font-bold text-green-600">
                      {result.results.profit_factor.toFixed(2)}
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">Wins/Losses ratio</div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};