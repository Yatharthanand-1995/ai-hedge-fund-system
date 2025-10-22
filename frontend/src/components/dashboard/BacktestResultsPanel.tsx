import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, TrendingDown, Calendar, DollarSign, Target, Activity, Play, Pause, Download } from 'lucide-react';
import { cn, formatCurrency, formatPercentage } from '../../utils';

interface BacktestResult {
  start_date: string;
  end_date: string;
  initial_capital: number;
  final_value: number;
  total_return: number;
  benchmark_return: number;
  spy_return: number;
  outperformance_vs_benchmark: number;
  outperformance_vs_spy: number;
  rebalances: number;
  metrics: {
    sharpe_ratio: number;
    max_drawdown: number;
    volatility: number;
  };
  equity_curve: Array<{
    date: string;
    value: number;
    return: number;
  }>;
  rebalance_log: Array<{
    date: string;
    portfolio: string[];
    portfolio_value: number;
    avg_score: number;
  }>;
}

interface BacktestConfig {
  start_date: string;
  end_date: string;
  rebalance_frequency: 'monthly' | 'quarterly';
  top_n: number;
  universe: string[];
}

interface BacktestResultsPanelProps {
  className?: string;
}

export const BacktestResultsPanel: React.FC<BacktestResultsPanelProps> = ({ className }) => {
  const [backtestResults, setBacktestResults] = useState<BacktestResult[]>([]);
  const [selectedResult, setSelectedResult] = useState<BacktestResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [config, setConfig] = useState<BacktestConfig>({
    start_date: '2023-01-01',
    end_date: '2024-01-01',
    rebalance_frequency: 'monthly',
    top_n: 10,
    universe: []  // Empty array uses all 50 stocks from US_TOP_100_STOCKS by default
  });

  useEffect(() => {
    // Load backtest history from API
    loadBacktestHistory();
  }, []);

  const loadBacktestHistory = async () => {
    try {
      // Fetch backtest history from API
      const response = await fetch('http://localhost:8010/backtest/history');
      if (response.ok) {
        const data = await response.json();
        console.log(`✅ Loaded ${data.length} backtest results from API`);

        if (data.length > 0) {
          setBacktestResults(data);
          setSelectedResult(data[0]);
        } else {
          console.log('ℹ️ No backtest history found yet. Run a backtest to see results.');
          setBacktestResults([]);
          setSelectedResult(null);
        }
      } else {
        console.log('No backtest history available');
        setBacktestResults([]);
        setSelectedResult(null);
      }
    } catch (error) {
      console.error('Failed to load backtest history:', error);
      setBacktestResults([]);
      setSelectedResult(null);
    }
  };

  const generateEnhancedMockData = async (useBasicFallback = false): Promise<BacktestResult[]> => {
    try {
      if (!useBasicFallback) {
        // Try to fetch real portfolio data to enhance mock results
        const portfolioResponse = await fetch('http://localhost:8010/portfolio/top-picks?limit=10');
        if (portfolioResponse.ok) {
          const portfolioData = await portfolioResponse.json();
          const topPicks = portfolioData.top_picks || [];

          if (topPicks.length > 0) {
            return generateRealisticBacktestData(topPicks);
          }
        }
      }
    } catch (error) {
      console.log('Using basic fallback data for backtest');
    }

    // Return basic mock data
    return [mockBacktestResult];
  };

  const generateRealisticBacktestData = (topPicks: any[]): BacktestResult[] => {
    const avgScore = topPicks.reduce((sum, pick) => sum + pick.overall_score, 0) / topPicks.length;
    const scoreStd = Math.sqrt(topPicks.reduce((sum, pick) => sum + Math.pow(pick.overall_score - avgScore, 2), 0) / topPicks.length);

    // Generate multiple backtest scenarios
    const scenarios = [
      { period: '1 Year', start: '2023-01-01', end: '2024-01-01', multiplier: 1.0 },
      { period: '6 Months', start: '2023-07-01', end: '2024-01-01', multiplier: 0.6 },
      { period: '3 Months', start: '2023-10-01', end: '2024-01-01', multiplier: 0.3 }
    ];

    return scenarios.map((scenario, index) => {
      const baseReturn = (avgScore - 50) * 0.004 * scenario.multiplier; // Base return from AI score
      const volatility = Math.max(0.08, scoreStd * 0.015);

      // Add some randomness but keep it realistic
      const randomFactor = (Math.random() - 0.5) * 0.1;
      const totalReturn = Math.max(-0.25, Math.min(0.4, baseReturn + randomFactor));

      const initialCapital = 100000;
      const finalValue = initialCapital * (1 + totalReturn);
      const benchmarkReturn = totalReturn * 0.85;
      const spyReturn = totalReturn * 0.8;

      // Generate equity curve
      const periods = Math.max(3, Math.floor(scenario.multiplier * 12));
      const equityCurve = [];

      for (let i = 0; i <= periods; i++) {
        const progress = i / periods;
        const currentReturn = totalReturn * progress + (Math.random() - 0.5) * volatility * 0.5;
        const currentValue = initialCapital * (1 + currentReturn);

        const date = new Date(scenario.start);
        date.setDate(date.getDate() + (progress * (new Date(scenario.end).getTime() - new Date(scenario.start).getTime()) / (1000 * 60 * 60 * 24)));

        equityCurve.push({
          date: date.toISOString().split('T')[0],
          value: Math.round(currentValue),
          return: Math.round(currentReturn * 10000) / 10000
        });
      }

      // Generate rebalance log with real symbols
      const rebalanceLog = [];
      const symbols = topPicks.slice(0, 10).map(pick => pick.symbol);

      for (let i = 0; i < Math.min(3, periods); i++) {
        const date = new Date(scenario.start);
        date.setMonth(date.getMonth() + i * 3);

        rebalanceLog.push({
          date: date.toISOString().split('T')[0],
          portfolio: symbols.slice(0, 8),
          portfolio_value: Math.round(initialCapital * (1 + totalReturn * (i / 3))),
          avg_score: Math.round((avgScore + (Math.random() - 0.5) * 5) * 10) / 10
        });
      }

      return {
        start_date: scenario.start,
        end_date: scenario.end,
        initial_capital: initialCapital,
        final_value: Math.round(finalValue),
        total_return: Math.round(totalReturn * 10000) / 10000,
        benchmark_return: Math.round(benchmarkReturn * 10000) / 10000,
        spy_return: Math.round(spyReturn * 10000) / 10000,
        outperformance_vs_benchmark: Math.round((totalReturn - benchmarkReturn) * 10000) / 10000,
        outperformance_vs_spy: Math.round((totalReturn - spyReturn) * 10000) / 10000,
        rebalances: rebalanceLog.length,
        metrics: {
          sharpe_ratio: Math.round(Math.max(0.5, totalReturn / volatility) * 100) / 100,
          max_drawdown: Math.round(Math.min(0.15, volatility * 1.2) * 1000) / 1000,
          volatility: Math.round(volatility * 1000) / 1000
        },
        equity_curve: equityCurve,
        rebalance_log: rebalanceLog
      };
    });
  };

  const runBacktest = async () => {
    try {
      setIsRunning(true);

      console.log('🚀 Running backtest with config:', config);

      // Call the real backtest API with 60s timeout (backtests can take time)
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000);

      const response = await fetch('http://localhost:8010/backtest/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      if (response.ok) {
        const apiResult = await response.json();
        console.log('✅ Backtest completed successfully:', apiResult);

        if (apiResult && apiResult.results) {
          // Backtest was saved to storage backend, now reload history to get updated list
          await loadBacktestHistory();
          console.log('✅ Backtest history reloaded from storage');
          return;
        }
      } else {
        const errorText = await response.text();
        console.error('❌ Backtest API failed:', response.status, errorText);
        throw new Error(`Backtest failed: ${response.status}`);
      }

      throw new Error('No results returned from backtest API');

    } catch (error) {
      console.error('❌ Backtest failed with error:', error);

      if (error instanceof Error && error.name === 'AbortError') {
        alert('Backtest timed out after 60 seconds.\n\nThis usually happens for long time periods (multi-year backtests).\n\nTry:\n• Shorter date range (1-6 months)\n• Smaller stock universe\n• Monthly instead of quarterly rebalancing');
      } else {
        alert(`Backtest failed: ${error instanceof Error ? error.message : 'Unknown error'}\n\nPlease ensure the API server is running on localhost:8010`);
      }
    } finally {
      setIsRunning(false);
    }
  };

  const generateConfigBasedBacktest = async (config: BacktestConfig): Promise<BacktestResult> => {
    try {
      // Get real portfolio data for the backtest
      const portfolioResponse = await fetch('http://localhost:8010/portfolio/top-picks?limit=config.top_n');
      if (portfolioResponse.ok) {
        const portfolioData = await portfolioResponse.json();
        const topPicks = portfolioData.top_picks || [];

        if (topPicks.length > 0) {
          return generateRealisticBacktestFromConfig(config, topPicks);
        }
      }
    } catch (error) {
      console.log('Using basic backtest generation');
    }

    return generateBasicBacktestResult(config);
  };

  const generateRealisticBacktestFromConfig = (config: BacktestConfig, topPicks: any[]): BacktestResult => {
    const avgScore = topPicks.slice(0, config.top_n).reduce((sum, pick) => sum + pick.overall_score, 0) / Math.min(config.top_n, topPicks.length);
    const scoreStd = Math.sqrt(topPicks.slice(0, config.top_n).reduce((sum, pick) => sum + Math.pow(pick.overall_score - avgScore, 2), 0) / Math.min(config.top_n, topPicks.length));

    // Calculate time span
    const startDate = new Date(config.start_date);
    const endDate = new Date(config.end_date);
    const years = (endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24 * 365.25);

    // Generate performance based on AI scores and time period
    const baseAnnualReturn = (avgScore - 50) * 0.004; // Base return from AI score
    const volatility = Math.max(0.08, scoreStd * 0.015);
    const totalReturn = Math.max(-0.3, Math.min(0.5, baseAnnualReturn * years + (Math.random() - 0.5) * volatility * Math.sqrt(years)));

    const finalValue = config.initial_capital * (1 + totalReturn);
    const benchmarkReturn = totalReturn * 0.85;
    const spyReturn = totalReturn * 0.8;

    // Generate monthly periods for equity curve
    const months = Math.max(1, Math.round(years * 12));
    const equityCurve = [];
    const rebalanceLog = [];

    const rebalanceMonths = config.rebalance_frequency === 'quarterly' ? 3 : 1;

    for (let i = 0; i <= months; i++) {
      const date = new Date(startDate);
      date.setMonth(date.getMonth() + i);

      const progress = i / months;
      const currentReturn = totalReturn * progress + (Math.random() - 0.5) * volatility * 0.3;
      const currentValue = config.initial_capital * (1 + currentReturn);

      equityCurve.push({
        date: date.toISOString().split('T')[0],
        value: Math.round(currentValue),
        return: Math.round(currentReturn * 10000) / 10000
      });

      // Add rebalance events
      if (i % rebalanceMonths === 0 && i < months) {
        const symbols = topPicks.slice(0, config.top_n).map(pick => pick.symbol);
        rebalanceLog.push({
          date: date.toISOString().split('T')[0],
          portfolio: symbols,
          portfolio_value: Math.round(currentValue),
          avg_score: Math.round((avgScore + (Math.random() - 0.5) * 5) * 10) / 10
        });
      }
    }

    return {
      start_date: config.start_date,
      end_date: config.end_date,
      initial_capital: config.initial_capital,
      final_value: Math.round(finalValue),
      total_return: Math.round(totalReturn * 10000) / 10000,
      benchmark_return: Math.round(benchmarkReturn * 10000) / 10000,
      spy_return: Math.round(spyReturn * 10000) / 10000,
      outperformance_vs_benchmark: Math.round((totalReturn - benchmarkReturn) * 10000) / 10000,
      outperformance_vs_spy: Math.round((totalReturn - spyReturn) * 10000) / 10000,
      rebalances: rebalanceLog.length,
      metrics: {
        sharpe_ratio: Math.round(Math.max(0.5, totalReturn / volatility) * 100) / 100,
        max_drawdown: Math.round(Math.min(0.2, volatility * 1.3) * 1000) / 1000,
        volatility: Math.round(volatility * 1000) / 1000
      },
      equity_curve: equityCurve,
      rebalance_log: rebalanceLog
    };
  };

  const generateBasicBacktestResult = (config: BacktestConfig): BacktestResult => {
    // Simple fallback for when portfolio data isn't available
    const years = (new Date(config.end_date).getTime() - new Date(config.start_date).getTime()) / (1000 * 60 * 60 * 24 * 365.25);
    const totalReturn = Math.max(-0.15, Math.min(0.25, (Math.random() - 0.3) * 0.4 * years));
    const finalValue = config.initial_capital * (1 + totalReturn);

    return {
      start_date: config.start_date,
      end_date: config.end_date,
      initial_capital: config.initial_capital,
      final_value: Math.round(finalValue),
      total_return: Math.round(totalReturn * 10000) / 10000,
      benchmark_return: Math.round(totalReturn * 0.8 * 10000) / 10000,
      spy_return: Math.round(totalReturn * 0.75 * 10000) / 10000,
      outperformance_vs_benchmark: Math.round(totalReturn * 0.2 * 10000) / 10000,
      outperformance_vs_spy: Math.round(totalReturn * 0.25 * 10000) / 10000,
      rebalances: Math.max(1, Math.round(years * 4)), // Quarterly rebalances
      metrics: {
        sharpe_ratio: Math.round(Math.max(0.8, Math.random() * 1.5) * 100) / 100,
        max_drawdown: Math.round(Math.max(0.05, Math.random() * 0.15) * 1000) / 1000,
        volatility: Math.round(Math.max(0.1, Math.random() * 0.2) * 1000) / 1000
      },
      equity_curve: [
        { date: config.start_date, value: config.initial_capital, return: 0.0 },
        { date: config.end_date, value: Math.round(finalValue), return: Math.round(totalReturn * 10000) / 10000 }
      ],
      rebalance_log: [
        {
          date: config.end_date,
          portfolio: config.universe.slice(0, config.top_n),
          portfolio_value: Math.round(finalValue),
          avg_score: 65.0
        }
      ]
    };
  };

  const getPerformanceColor = (value: number) => {
    return value >= 0 ? 'text-green-400' : 'text-red-400';
  };

  const getSharpeColor = (sharpe: number) => {
    if (sharpe >= 1.5) return 'text-green-400';
    if (sharpe >= 1.0) return 'text-yellow-400';
    return 'text-red-400';
  };

  const handleExportResults = () => {
    if (!selectedResult) return;

    const dataStr = JSON.stringify(selectedResult, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `backtest-results-${selectedResult.start_date}-${selectedResult.end_date}.json`;
    link.click();
    URL.revokeObjectURL(url);
    console.log('Exported backtest results:', selectedResult);
  };

  const handleCompareStrategies = () => {
    console.log('Compare Strategies clicked');
    alert('Compare Strategies\n\nIn a real app, this would:\n• Show side-by-side strategy comparison\n• Compare different rebalancing frequencies\n• Analyze different portfolio sizes\n• Compare vs benchmarks (S&P 500, etc.)');
  };

  const handleViewFullReport = () => {
    console.log('View Full Report clicked');
    alert('View Full Report\n\nIn a real app, this would:\n• Open detailed PDF/HTML report\n• Show all metrics and analysis\n• Include trade-by-trade breakdown\n• Provide risk analysis charts');
  };

  if (loading) {
    return (
      <div className={cn('professional-card p-6', className)}>
        <div className="flex items-center space-x-3 mb-6">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-accent"></div>
          <h2 className="text-xl font-semibold text-foreground">Loading Backtest Results...</h2>
        </div>
      </div>
    );
  }

  return (
    <div className={cn('professional-card p-6', className)}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-foreground flex items-center space-x-2">
          <Activity className="h-6 w-6 text-accent" />
          <span>Strategy Backtesting</span>
        </h2>
        <div className="flex space-x-2">
          <button
            onClick={runBacktest}
            disabled={isRunning}
            className="bg-accent hover:bg-accent/80 text-accent-foreground px-4 py-2 rounded-lg font-medium text-sm transition-colors flex items-center space-x-2"
          >
            {isRunning ? (
              <>
                <Pause className="h-4 w-4" />
                <span>Running...</span>
              </>
            ) : (
              <>
                <Play className="h-4 w-4" />
                <span>Run Backtest</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Configuration Panel */}
      <div className="bg-muted/20 rounded-lg p-4 mb-6">
        <h3 className="text-lg font-semibold text-foreground mb-3">Backtest Configuration</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="text-sm text-muted-foreground">Start Date</label>
            <input
              type="date"
              value={config.start_date}
              onChange={(e) => setConfig(prev => ({ ...prev, start_date: e.target.value }))}
              className="w-full bg-muted border border-border rounded px-3 py-2 text-sm text-foreground"
            />
          </div>
          <div>
            <label className="text-sm text-muted-foreground">End Date</label>
            <input
              type="date"
              value={config.end_date}
              onChange={(e) => setConfig(prev => ({ ...prev, end_date: e.target.value }))}
              className="w-full bg-muted border border-border rounded px-3 py-2 text-sm text-foreground"
            />
          </div>
          <div>
            <label className="text-sm text-muted-foreground">Frequency</label>
            <select
              value={config.rebalance_frequency}
              onChange={(e) => setConfig(prev => ({ ...prev, rebalance_frequency: e.target.value as 'monthly' | 'quarterly' }))}
              className="w-full bg-muted border border-border rounded px-3 py-2 text-sm text-foreground"
            >
              <option value="monthly">Monthly</option>
              <option value="quarterly">Quarterly</option>
            </select>
          </div>
          <div>
            <label className="text-sm text-muted-foreground">Top N Stocks</label>
            <input
              type="number"
              value={config.top_n}
              onChange={(e) => setConfig(prev => ({ ...prev, top_n: parseInt(e.target.value) }))}
              className="w-full bg-muted border border-border rounded px-3 py-2 text-sm text-foreground"
              min="5"
              max="20"
            />
          </div>
        </div>
      </div>

      {/* Empty State */}
      {!selectedResult && backtestResults.length === 0 && (
        <div className="text-center py-12">
          <Activity className="h-16 w-16 text-muted-foreground mx-auto mb-4 opacity-50" />
          <h3 className="text-xl font-semibold text-foreground mb-2">No Backtest History</h3>
          <p className="text-muted-foreground mb-6">
            Run your first backtest to see results here. All backtest runs will be saved and tracked.
          </p>
          <button
            onClick={runBacktest}
            disabled={isRunning}
            className="bg-accent hover:bg-accent/80 text-accent-foreground px-6 py-3 rounded-lg font-medium transition-colors inline-flex items-center space-x-2"
          >
            <Play className="h-5 w-5" />
            <span>Run Your First Backtest</span>
          </button>
        </div>
      )}

      {/* Backtest History List */}
      {backtestResults.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-foreground mb-3">Backtest History ({backtestResults.length} results)</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {backtestResults.map((result, index) => {
              const isSelected = selectedResult?.start_date === result.start_date &&
                                selectedResult?.end_date === result.end_date;
              return (
                <button
                  key={index}
                  onClick={() => setSelectedResult(result)}
                  className={cn(
                    'professional-card p-4 text-left transition-all hover:scale-[1.02]',
                    isSelected ? 'ring-2 ring-accent bg-accent/10' : 'bg-muted/20 hover:bg-muted/30'
                  )}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <Calendar className="h-4 w-4 text-accent" />
                      <span className="font-medium text-foreground">
                        {result.start_date} → {result.end_date}
                      </span>
                    </div>
                    <span className={cn(
                      'text-sm font-semibold',
                      getPerformanceColor(result.total_return)
                    )}>
                      {formatPercentage(result.total_return * 100)}
                    </span>
                  </div>
                  <div className="grid grid-cols-3 gap-2 text-xs">
                    <div>
                      <div className="text-muted-foreground">Sharpe</div>
                      <div className={cn('font-semibold', getSharpeColor(result.metrics.sharpe_ratio))}>
                        {result.metrics.sharpe_ratio.toFixed(2)}
                      </div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">Max DD</div>
                      <div className="font-semibold text-red-400">
                        {formatPercentage(result.metrics.max_drawdown * 100)}
                      </div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">Rebalances</div>
                      <div className="font-semibold text-foreground">
                        {result.rebalances}
                      </div>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {selectedResult && (
        <>
          {/* Selected Backtest Header */}
          <div className="mb-4 p-4 bg-accent/10 border border-accent/20 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-foreground mb-1">
                  {selectedResult.start_date} to {selectedResult.end_date}
                </h3>
                <p className="text-sm text-muted-foreground">
                  Real 4-Agent Analysis • {selectedResult.rebalances} Rebalances •
                  {(() => {
                    const startDate = new Date(selectedResult.start_date);
                    const endDate = new Date(selectedResult.end_date);
                    const years = (endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24 * 365.25);
                    const cagr = Math.pow(selectedResult.final_value / selectedResult.initial_capital, 1 / years) - 1;
                    return ` CAGR: ${formatPercentage(cagr * 100)}`;
                  })()}
                </p>
              </div>
              <div className="text-right">
                <div className="text-sm text-muted-foreground">Agent Weights (Backtest Mode)</div>
                <div className="text-xs text-muted-foreground mt-1">
                  M:50% • Q:40% • F:5% • S:5%
                </div>
              </div>
            </div>
          </div>

          {/* Performance Summary */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="professional-card p-4 bg-muted/20">
              <div className="flex items-center space-x-2 mb-2">
                <TrendingUp className="h-4 w-4 text-accent" />
                <span className="text-sm text-muted-foreground">Total Return</span>
              </div>
              <div className={cn('text-2xl font-bold', getPerformanceColor(selectedResult.total_return))}>
                {formatPercentage(selectedResult.total_return * 100)}
              </div>
              <div className="text-xs text-muted-foreground">
                vs SPY: {formatPercentage(selectedResult.outperformance_vs_spy * 100)}
              </div>
            </div>

            <div className="professional-card p-4 bg-muted/20">
              <div className="flex items-center space-x-2 mb-2">
                <Target className="h-4 w-4 text-accent" />
                <span className="text-sm text-muted-foreground">Sharpe Ratio</span>
              </div>
              <div className={cn('text-2xl font-bold', getSharpeColor(selectedResult.metrics.sharpe_ratio))}>
                {selectedResult.metrics.sharpe_ratio.toFixed(2)}
              </div>
              <div className="text-xs text-muted-foreground">
                Risk-adjusted return
              </div>
            </div>

            <div className="professional-card p-4 bg-muted/20">
              <div className="flex items-center space-x-2 mb-2">
                <TrendingDown className="h-4 w-4 text-red-400" />
                <span className="text-sm text-muted-foreground">Max Drawdown</span>
              </div>
              <div className="text-2xl font-bold text-red-400">
                {formatPercentage(selectedResult.metrics.max_drawdown * 100)}
              </div>
              <div className="text-xs text-muted-foreground">
                Largest peak-to-trough decline
              </div>
            </div>

            <div className="professional-card p-4 bg-muted/20">
              <div className="flex items-center space-x-2 mb-2">
                <DollarSign className="h-4 w-4 text-accent" />
                <span className="text-sm text-muted-foreground">Final Value</span>
              </div>
              <div className="text-2xl font-bold text-foreground">
                {formatCurrency(selectedResult.final_value)}
              </div>
              <div className="text-xs text-muted-foreground">
                From {formatCurrency(selectedResult.initial_capital)}
              </div>
            </div>
          </div>

          {/* Equity Curve Chart */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-foreground mb-4">Equity Curve</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={selectedResult.equity_curve}>
                  <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip
                    formatter={(value, name) => [
                      formatCurrency(value as number),
                      'Portfolio Value'
                    ]}
                    labelFormatter={(label) => `Date: ${label}`}
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

          {/* Recent Rebalances */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-foreground mb-4">Recent Rebalances</h3>
            <div className="space-y-3">
              {selectedResult.rebalance_log.slice(0, 5).map((rebalance, index) => (
                <div key={index} className="professional-card p-4 bg-muted/20">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <Calendar className="h-4 w-4 text-accent" />
                      <span className="font-medium text-foreground">{rebalance.date}</span>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      Avg Score: {rebalance.avg_score.toFixed(1)}
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {rebalance.portfolio.slice(0, 8).map((symbol) => (
                      <span key={symbol} className="bg-accent/20 text-accent px-2 py-1 rounded text-xs">
                        {symbol}
                      </span>
                    ))}
                    {rebalance.portfolio.length > 8 && (
                      <span className="text-xs text-muted-foreground">
                        +{rebalance.portfolio.length - 8} more
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-2">
            <button
              onClick={handleExportResults}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium text-sm transition-colors flex items-center space-x-2"
            >
              <Download className="h-4 w-4" />
              <span>Export Results</span>
            </button>
            <button
              onClick={handleCompareStrategies}
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium text-sm transition-colors"
            >
              Compare Strategies
            </button>
            <button
              onClick={handleViewFullReport}
              className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg font-medium text-sm transition-colors"
            >
              View Full Report
            </button>
          </div>
        </>
      )}
    </div>
  );
};

// Mock data for demo purposes
const mockBacktestResult: BacktestResult = {
  start_date: '2023-01-01',
  end_date: '2024-01-01',
  initial_capital: 100000,
  final_value: 118500,
  total_return: 0.185,
  benchmark_return: 0.142,
  spy_return: 0.134,
  outperformance_vs_benchmark: 0.043,
  outperformance_vs_spy: 0.051,
  rebalances: 12,
  metrics: {
    sharpe_ratio: 1.45,
    max_drawdown: 0.083,
    volatility: 0.156
  },
  equity_curve: [
    { date: '2023-01-01', value: 100000, return: 0.0 },
    { date: '2023-02-01', value: 102500, return: 0.025 },
    { date: '2023-03-01', value: 105200, return: 0.052 },
    { date: '2023-04-01', value: 103800, return: 0.038 },
    { date: '2023-05-01', value: 108400, return: 0.084 },
    { date: '2023-06-01', value: 111200, return: 0.112 },
    { date: '2023-07-01', value: 109800, return: 0.098 },
    { date: '2023-08-01', value: 113600, return: 0.136 },
    { date: '2023-09-01', value: 116200, return: 0.162 },
    { date: '2023-10-01', value: 114800, return: 0.148 },
    { date: '2023-11-01', value: 117500, return: 0.175 },
    { date: '2023-12-01', value: 118500, return: 0.185 }
  ],
  rebalance_log: [
    {
      date: '2023-12-01',
      portfolio: ['NVDA', 'MSFT', 'AAPL', 'GOOGL', 'META', 'V', 'MA', 'UNH', 'JNJ', 'AVGO'],
      portfolio_value: 118500,
      avg_score: 73.2
    },
    {
      date: '2023-11-01',
      portfolio: ['MSFT', 'NVDA', 'AAPL', 'GOOGL', 'V', 'META', 'UNH', 'MA', 'JNJ', 'LLY'],
      portfolio_value: 117500,
      avg_score: 71.8
    },
    {
      date: '2023-10-01',
      portfolio: ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'V', 'UNH', 'META', 'JNJ', 'MA', 'AVGO'],
      portfolio_value: 114800,
      avg_score: 70.5
    }
  ]
};