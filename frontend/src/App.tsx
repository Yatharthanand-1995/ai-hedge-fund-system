import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { Navigation } from './components/navigation/Navigation';
import { StockAnalysisPage } from './pages/StockAnalysisPage';
import { PortfolioPage } from './pages/PortfolioPage';
import { PortfolioSummaryPanel } from './components/dashboard/PortfolioSummaryPanel';
import { IntelligentStockCard } from './components/dashboard/IntelligentStockCard';
import { SectorAllocationPanel } from './components/dashboard/SectorAllocationPanel';
import { MultiAgentConsensusPanel } from './components/dashboard/MultiAgentConsensusPanel';
import { ActionableInsightsPanel } from './components/dashboard/ActionableInsightsPanel';
import { RiskManagementPanel } from './components/dashboard/RiskManagementPanel';
import { BacktestResultsPanel } from './components/dashboard/BacktestResultsPanel';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 15 * 60 * 1000, // 15 minutes (formerly cacheTime)
    },
  },
});

// Enhanced Professional Dashboard Component
const Dashboard: React.FC<{ onPageChange: (page: 'dashboard' | 'analysis' | 'portfolio') => void }> = ({ onPageChange }) => {
  const [topPicks, setTopPicks] = useState<any[]>([]);
  const [isLoadingPicks, setIsLoadingPicks] = useState(true);

  // Fetch real top picks data on mount
  React.useEffect(() => {
    const fetchTopPicks = async () => {
      try {
        setIsLoadingPicks(true);
        const response = await fetch('http://localhost:8010/portfolio/top-picks?limit=6');
        if (response.ok) {
          const data = await response.json();
          const enhancedPicks = data.top_picks?.map((pick: any, index: number) => ({
            ...pick,
            nextAction: {
              type: pick.overall_score > 75 ? 'buy' : pick.overall_score < 50 ? 'sell' : 'hold',
              urgency: pick.overall_score > 80 ? 'high' : pick.overall_score > 60 ? 'medium' : 'low',
              description: pick.overall_score > 75
                ? 'Strong buy signal - Consider increasing position'
                : pick.overall_score < 50
                ? 'Weak performance - Consider reducing exposure'
                : 'Monitor closely for trend changes',
              targetPrice: pick.market_data.current_price * (pick.overall_score > 75 ? 1.1 : 0.9),
              timeframe: 'This Week'
            },
            momentum: pick.agent_scores?.momentum > 70 ? 'bullish' : pick.agent_scores?.momentum < 40 ? 'bearish' : 'neutral',
            riskLevel: pick.overall_score > 70 ? 'low' : pick.overall_score > 50 ? 'medium' : 'high'
          })) || [];
          setTopPicks(enhancedPicks);
        }
      } catch (error) {
        console.error('Failed to fetch top picks:', error);
      } finally {
        setIsLoadingPicks(false);
      }
    };
    fetchTopPicks();
  }, []);

  const handleActionClick = (action: any, symbol: string) => {
    console.log(`Action ${action.type} clicked for ${symbol}`, action);
    // In a real app, this would trigger actual trading actions
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-foreground mb-2">
          🏦 AI Hedge Fund System
        </h1>
        <p className="text-xl text-muted-foreground">
          Professional-grade investment analysis with 4-agent intelligence
        </p>
      </div>

      {/* Executive Summary - Top Priority */}
      <PortfolioSummaryPanel className="mb-8" />

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        {/* Left Column - Insights and Actions */}
        <div className="xl:col-span-1 space-y-8">
          <ActionableInsightsPanel />
        </div>

        {/* Right Column - Analysis */}
        <div className="xl:col-span-2 space-y-8">
          {/* Multi-Agent Analysis */}
          <MultiAgentConsensusPanel />

          {/* Sector Allocation */}
          <SectorAllocationPanel />
        </div>
      </div>

      {/* Risk Management Section */}
      <RiskManagementPanel className="mb-8" />

      {/* Backtesting Results Section */}
      <BacktestResultsPanel className="mb-8" />

      {/* Intelligent Stock Recommendations */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-foreground">🎯 Intelligent Investment Recommendations</h2>
          <button
            onClick={() => onPageChange('portfolio')}
            className="text-accent hover:underline text-sm font-medium"
          >
            View All →
          </button>
        </div>
        {isLoadingPicks ? (
          <div className="professional-card p-8">
            <div className="flex items-center justify-center space-x-3">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent"></div>
              <span className="text-muted-foreground">Loading intelligent recommendations...</span>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {topPicks.slice(0, 6).map((pick, index) => (
              <IntelligentStockCard
                key={pick.symbol}
                stock={pick}
                rank={index + 1}
                onActionClick={handleActionClick}
              />
            ))}
          </div>
        )}
      </div>

      {/* Quick Navigation */}
      <div className="professional-card p-6">
        <h2 className="text-xl font-bold text-foreground mb-4">Professional Tools</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <button
            onClick={() => onPageChange('analysis')}
            className="text-center p-6 border border-border rounded-lg hover:border-accent hover:bg-muted/20 transition-all cursor-pointer"
          >
            <div className="text-3xl mb-2">📊</div>
            <h3 className="font-semibold mb-2">Deep Stock Analysis</h3>
            <p className="text-muted-foreground text-sm">
              Comprehensive 4-agent analysis with detailed narratives
            </p>
            <div className="mt-2 text-accent text-sm font-medium">Analyze →</div>
          </button>
          <button
            onClick={() => onPageChange('portfolio')}
            className="text-center p-6 border border-border rounded-lg hover:border-accent hover:bg-muted/20 transition-all cursor-pointer"
          >
            <div className="text-3xl mb-2">📈</div>
            <h3 className="font-semibold mb-2">Portfolio Optimizer</h3>
            <p className="text-muted-foreground text-sm">
              Advanced portfolio optimization and risk management
            </p>
            <div className="mt-2 text-accent text-sm font-medium">Optimize →</div>
          </button>
          <button
            onClick={() => window.open('http://localhost:8010/docs', '_blank')}
            className="text-center p-6 border border-border rounded-lg hover:border-accent hover:bg-muted/20 transition-all cursor-pointer"
          >
            <div className="text-3xl mb-2">📚</div>
            <h3 className="font-semibold mb-2">API Documentation</h3>
            <p className="text-muted-foreground text-sm">
              Complete API reference and integration guides
            </p>
            <div className="mt-2 text-accent text-sm font-medium">Explore →</div>
          </button>
        </div>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  const [currentPage, setCurrentPage] = useState<'dashboard' | 'analysis' | 'portfolio'>('dashboard');

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-background">
        <div className="max-w-7xl mx-auto p-6">
          <Navigation currentPage={currentPage} onPageChange={setCurrentPage} />
          {currentPage === 'dashboard' && <Dashboard onPageChange={setCurrentPage} />}
          {currentPage === 'analysis' && <StockAnalysisPage />}
          {currentPage === 'portfolio' && <PortfolioPage />}
        </div>
      </div>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

export default App;
