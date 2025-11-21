import React, { useState, Component } from 'react';
import type { ErrorInfo, ReactNode } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { Navigation } from './components/navigation/Navigation';
import { ToastProvider } from './components/common/Toast';
import { StockAnalysisPage } from './pages/StockAnalysisPage';
import { PortfolioPage } from './pages/PortfolioPage';
import { BacktestingPage } from './pages/BacktestingPage';
import { PaperTradingPage } from './pages/PaperTradingPage';
import SystemDetailsPage from './pages/SystemDetailsPage';
import { IntelligentStockCard } from './components/dashboard/IntelligentStockCard';
import { SectorAllocationPanel } from './components/dashboard/SectorAllocationPanel';
import { MultiAgentConsensusPanel } from './components/dashboard/MultiAgentConsensusPanel';
import { ActionableInsightsPanel } from './components/dashboard/ActionableInsightsPanel';
import { RiskManagementPanel } from './components/dashboard/RiskManagementPanel';
import { InvestmentGuidePanel } from './components/dashboard/InvestmentGuidePanel';
import { CommandCenter } from './components/dashboard/CommandCenter';
import { SmartFilterBar } from './components/dashboard/SmartFilterBar';
import { UserPortfolioPanel } from './components/dashboard/UserPortfolioPanel';
import type { FilterOptions, SortOption } from './types/filters';
import { FEATURE_FLAGS } from './config/featureFlags';

console.log('🚀 App.tsx loaded successfully');

// Error Boundary Component
interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    console.error('❌ Error Boundary caught error:', error);
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('❌ Error details:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '40px', backgroundColor: '#1a1a1a', color: '#fff', minHeight: '100vh' }}>
          <h1>⚠️ Application Error</h1>
          <p>Something went wrong. Please check the console for details.</p>
          <pre style={{ backgroundColor: '#2a2a2a', padding: '20px', borderRadius: '8px', overflow: 'auto' }}>
            {this.state.error?.toString()}
            {'\n\n'}
            {this.state.error?.stack}
          </pre>
          <button
            onClick={() => window.location.reload()}
            style={{ marginTop: '20px', padding: '10px 20px', cursor: 'pointer' }}
          >
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 15 * 60 * 1000, // 15 minutes (formerly cacheTime)
    },
  },
});

// Define interface for top picks data
interface TopPickData {
  symbol: string;
  company_name?: string;
  sector: string;
  overall_score: number;
  recommendation: string;
  confidence_level: string;
  agent_scores: {
    fundamentals: number;
    momentum: number;
    quality: number;
    sentiment: number;
  };
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
  nextAction: {
    type: 'buy' | 'sell' | 'hold' | 'monitor';
    urgency: 'high' | 'medium' | 'low';
    description: string;
    targetPrice?: number;
    timeframe?: string;
  };
  momentum: 'bullish' | 'bearish' | 'neutral';
  riskLevel: 'low' | 'medium' | 'high';
}

// Enhanced Professional Dashboard Component
const Dashboard: React.FC<{ onPageChange: (page: 'dashboard' | 'analysis' | 'portfolio' | 'backtesting' | 'paper-trading' | 'system-details') => void }> = ({ onPageChange }) => {
  const [topPicks, setTopPicks] = useState<TopPickData[]>([]);
  const [isLoadingPicks, setIsLoadingPicks] = useState(true);
  const [filters, setFilters] = useState<FilterOptions>({
    sector: [],
    scoreRange: 'all',
    riskLevel: [],
    consensus: [],
    priceRange: 'all',
    searchQuery: ''
  });
  const [sortBy, setSortBy] = useState<SortOption>('score-desc');

  // Fetch real top picks data on mount
  React.useEffect(() => {
    const fetchTopPicks = async () => {
      try {
        setIsLoadingPicks(true);
        const response = await fetch('http://localhost:8010/portfolio/top-picks?limit=12');
        if (response.ok) {
          const data = await response.json();
          const enhancedPicks: TopPickData[] = (data.top_picks || []).map((pick: any) => ({
            ...pick,
            nextAction: {
              type: pick.overall_score > 75 ? 'buy' as const : pick.overall_score < 50 ? 'sell' as const : 'hold' as const,
              urgency: pick.overall_score > 80 ? 'high' as const : pick.overall_score > 60 ? 'medium' as const : 'low' as const,
              description: pick.overall_score > 75
                ? 'Strong buy signal - Consider increasing position'
                : pick.overall_score < 50
                ? 'Weak performance - Consider reducing exposure'
                : 'Monitor closely for trend changes',
              targetPrice: pick.market_data.current_price * (pick.overall_score > 75 ? 1.1 : 0.9),
              timeframe: 'This Week'
            },
            momentum: pick.agent_scores?.momentum > 70 ? 'bullish' as const : pick.agent_scores?.momentum < 40 ? 'bearish' as const : 'neutral' as const,
            riskLevel: pick.overall_score > 70 ? 'low' as const : pick.overall_score > 50 ? 'medium' as const : 'high' as const
          }));
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

  const handleActionClick = (action: TopPickData['nextAction'], symbol: string) => {
    console.log(`Action ${action?.type} clicked for ${symbol}`, action);
    // In a real app, this would trigger actual trading actions
  };

  const handleDetailsClick = (symbol: string) => {
    console.log(`Details clicked for ${symbol}, navigating to analysis page`);
    onPageChange('analysis');
    // In a real app, we would also pre-populate the stock symbol in the analysis form
  };

  // Filter and sort picks
  const filteredAndSortedPicks = React.useMemo(() => {
    let result = [...topPicks];

    // Apply search filter
    if (filters.searchQuery) {
      const query = filters.searchQuery.toLowerCase();
      result = result.filter(pick =>
        pick.symbol.toLowerCase().includes(query) ||
        pick.recommendation?.toLowerCase().includes(query)
      );
    }

    // Apply sector filter
    if (filters.sector.length > 0) {
      result = result.filter(pick => filters.sector.includes(pick.sector));
    }

    // Apply score range filter
    if (filters.scoreRange !== 'all') {
      result = result.filter(pick => {
        const score = pick.overall_score;
        switch (filters.scoreRange) {
          case 'strong-buy': return score >= 80;
          case 'buy': return score >= 65 && score < 80;
          case 'hold': return score >= 45 && score < 65;
          case 'sell': return score < 45;
          default: return true;
        }
      });
    }

    // Apply risk level filter
    if (filters.riskLevel.length > 0) {
      result = result.filter(pick => {
        const riskLevel = pick.riskLevel || (pick.overall_score > 70 ? 'Low' : pick.overall_score > 50 ? 'Medium' : 'High');
        return filters.riskLevel.includes(riskLevel);
      });
    }

    // Apply price range filter
    if (filters.priceRange !== 'all') {
      result = result.filter(pick => {
        const price = pick.market_data?.current_price || 0;
        switch (filters.priceRange) {
          case '0-50': return price >= 0 && price <= 50;
          case '50-200': return price > 50 && price <= 200;
          case '200-500': return price > 200 && price <= 500;
          case '500+': return price > 500;
          default: return true;
        }
      });
    }

    // Apply sorting
    result.sort((a, b) => {
      switch (sortBy) {
        case 'score-desc': return b.overall_score - a.overall_score;
        case 'score-asc': return a.overall_score - b.overall_score;
        case 'price-desc': return (b.market_data?.current_price || 0) - (a.market_data?.current_price || 0);
        case 'price-asc': return (a.market_data?.current_price || 0) - (b.market_data?.current_price || 0);
        case 'momentum-desc': return (b.agent_scores?.momentum || 0) - (a.agent_scores?.momentum || 0);
        case 'alpha-asc': return a.symbol.localeCompare(b.symbol);
        case 'alpha-desc': return b.symbol.localeCompare(a.symbol);
        default: return 0;
      }
    });

    return result;
  }, [topPicks, filters, sortBy]);

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

      {/* Command Center - Action Items (NEW) */}
      {FEATURE_FLAGS.USE_COMMAND_CENTER && (
        <CommandCenter
          className="mb-8"
          onPageChange={onPageChange}
          currentPage="dashboard"
        />
      )}

      {/* Investment Guide - How to Use */}
      <InvestmentGuidePanel className="mb-8" />

      {/* Your Real Portfolio with AI Recommendations */}
      <UserPortfolioPanel className="mb-8" />

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

        {/* Smart Filter Bar */}
        <SmartFilterBar
          onFilterChange={setFilters}
          onSortChange={setSortBy}
          totalCount={topPicks.length}
          filteredCount={filteredAndSortedPicks.length}
          className="mb-6"
        />

        {isLoadingPicks ? (
          <div className="professional-card p-8">
            <div className="flex items-center justify-center space-x-3">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent"></div>
              <span className="text-muted-foreground">Loading intelligent recommendations...</span>
            </div>
          </div>
        ) : filteredAndSortedPicks.length === 0 ? (
          <div className="professional-card p-8 text-center">
            <p className="text-muted-foreground text-lg mb-2">No stocks match your filters</p>
            <p className="text-sm text-muted-foreground">Try adjusting your filter criteria</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredAndSortedPicks.map((pick, index) => (
              <IntelligentStockCard
                key={pick.symbol}
                stock={pick}
                rank={index + 1}
                onActionClick={handleActionClick}
                onDetailsClick={handleDetailsClick}
              />
            ))}
          </div>
        )}
      </div>

      {/* Quick Navigation */}
      <div className="professional-card p-6">
        <h2 className="text-xl font-bold text-foreground mb-4">Professional Tools</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
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
            onClick={() => onPageChange('backtesting')}
            className="text-center p-6 border border-border rounded-lg hover:border-accent hover:bg-muted/20 transition-all cursor-pointer"
          >
            <div className="text-3xl mb-2">📉</div>
            <h3 className="font-semibold mb-2">5-Year Backtest</h3>
            <p className="text-muted-foreground text-sm">
              Historical performance analysis with real market data
            </p>
            <div className="mt-2 text-accent text-sm font-medium">View Results →</div>
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
  console.log('🎯 App component rendering...');
  const [currentPage, setCurrentPage] = useState<'dashboard' | 'analysis' | 'portfolio' | 'backtesting' | 'paper-trading' | 'system-details'>('dashboard');
  console.log('📄 Current page:', currentPage);

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ToastProvider>
          <div className="min-h-screen bg-background flex justify-center">
            <div className="w-full max-w-[1600px] px-4 sm:px-6 lg:px-8 py-6">
              <Navigation currentPage={currentPage} onPageChange={setCurrentPage} />
              {currentPage === 'dashboard' && (
                <ErrorBoundary>
                  <Dashboard onPageChange={setCurrentPage} />
                </ErrorBoundary>
              )}
              {currentPage === 'analysis' && (
                <ErrorBoundary>
                  <StockAnalysisPage />
                </ErrorBoundary>
              )}
              {currentPage === 'portfolio' && (
                <ErrorBoundary>
                  <PortfolioPage />
                </ErrorBoundary>
              )}
              {currentPage === 'backtesting' && (
                <ErrorBoundary>
                  <BacktestingPage />
                </ErrorBoundary>
              )}
              {currentPage === 'paper-trading' && (
                <ErrorBoundary>
                  <PaperTradingPage />
                </ErrorBoundary>
              )}
              {currentPage === 'system-details' && (
                <ErrorBoundary>
                  <SystemDetailsPage />
                </ErrorBoundary>
              )}
            </div>
          </div>
          <ReactQueryDevtools initialIsOpen={false} />
        </ToastProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

console.log('✅ App component defined');

export default App;
