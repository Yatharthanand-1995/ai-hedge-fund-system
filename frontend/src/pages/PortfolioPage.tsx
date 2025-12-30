import React, { useState } from 'react';
import { usePortfolioAnalysis, useTopPicks } from '../hooks/useApi';
import { PortfolioForm } from '../components/forms/PortfolioForm';
import { PortfolioDisplay } from '../components/portfolio/PortfolioDisplay';
import { TopPicksDisplay } from '../components/portfolio/TopPicksDisplay';

export const PortfolioPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'analyzer' | 'top-picks'>('analyzer');

  // Portfolio analysis
  const { mutate: analyzePortfolio, isPending: isAnalyzing, data: portfolioAnalysis, error: portfolioError } = usePortfolioAnalysis();

  // Top picks
  const { data: topPicks, isLoading: isLoadingPicks, error: picksError } = useTopPicks(10);

  const handleAnalyzePortfolio = (symbols: string[], weights?: number[]) => {
    analyzePortfolio({
      symbols,
      weights,
    });
  };

  const handleAddToPortfolio = (_symbol: string) => {
    // For now, just switch to analyzer tab
    // In a real app, this could pre-populate the form
    setActiveTab('analyzer');
  };

  const tabButtonClass = (isActive: boolean) => `
    px-6 py-3 font-medium text-sm rounded-lg transition-all
    ${isActive
      ? 'bg-accent text-accent-foreground'
      : 'text-muted-foreground hover:text-foreground hover:bg-muted'
    }
  `;

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-foreground mb-2">
          📈 Portfolio Manager
        </h1>
        <p className="text-xl text-muted-foreground">
          Analyze and optimize your investment portfolio with 5-agent intelligence
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="professional-card p-4 mb-8">
        <div className="flex space-x-2">
          <button
            onClick={() => setActiveTab('analyzer')}
            className={tabButtonClass(activeTab === 'analyzer')}
          >
            Portfolio Analyzer
          </button>
          <button
            onClick={() => setActiveTab('top-picks')}
            className={tabButtonClass(activeTab === 'top-picks')}
          >
            Top Investment Picks
          </button>
        </div>
      </div>

      {/* Portfolio Analyzer Tab */}
      {activeTab === 'analyzer' && (
        <div className="space-y-8">
          {/* Portfolio Form */}
          <div className="professional-card p-6">
            <PortfolioForm
              onAnalyze={handleAnalyzePortfolio}
              isLoading={isAnalyzing}
            />
          </div>

          {/* Loading State */}
          {isAnalyzing && (
            <div className="professional-card p-8">
              <div className="flex flex-col items-center justify-center space-y-4">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent"></div>
                <div className="text-center">
                  <h3 className="text-lg font-semibold text-foreground mb-2">
                    Analyzing Portfolio
                  </h3>
                  <p className="text-muted-foreground">
                    Our 5-agent system is evaluating your portfolio positions...
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Error State */}
          {portfolioError && !isAnalyzing && (
            <div className="professional-card p-6">
              <div className="flex items-center space-x-3">
                <div className="text-red-400 text-xl">⚠️</div>
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-1">
                    Portfolio Analysis Failed
                  </h3>
                  <p className="text-muted-foreground">
                    {portfolioError.detail || 'Unable to analyze the portfolio. Please try again.'}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Portfolio Analysis Results */}
          {portfolioAnalysis && !isAnalyzing && (
            <PortfolioDisplay analysis={portfolioAnalysis} />
          )}

          {/* Getting Started Section */}
          {!portfolioAnalysis && !isAnalyzing && !portfolioError && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="professional-card p-6">
                <div className="text-3xl mb-4">🎯</div>
                <h3 className="text-lg font-semibold text-foreground mb-2">
                  Portfolio Optimization
                </h3>
                <p className="text-muted-foreground text-sm">
                  Get optimal weights for your portfolio based on our 5-agent scoring system and risk assessment
                </p>
              </div>

              <div className="professional-card p-6">
                <div className="text-3xl mb-4">⚖️</div>
                <h3 className="text-lg font-semibold text-foreground mb-2">
                  Risk Assessment
                </h3>
                <p className="text-muted-foreground text-sm">
                  Comprehensive risk analysis identifying high-risk positions and portfolio balance recommendations
                </p>
              </div>

              <div className="professional-card p-6">
                <div className="text-3xl mb-4">📊</div>
                <h3 className="text-lg font-semibold text-foreground mb-2">
                  Individual Analysis
                </h3>
                <p className="text-muted-foreground text-sm">
                  Detailed breakdown of each stock with agent scores, recommendations, and investment thesis
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Top Picks Tab */}
      {activeTab === 'top-picks' && (
        <div className="space-y-8">
          {/* Loading State */}
          {isLoadingPicks && (
            <div className="professional-card p-8">
              <div className="flex flex-col items-center justify-center space-y-4">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent"></div>
                <div className="text-center">
                  <h3 className="text-lg font-semibold text-foreground mb-2">
                    Loading Top Picks
                  </h3>
                  <p className="text-muted-foreground">
                    Fetching our highest-rated investment opportunities...
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Error State */}
          {picksError && !isLoadingPicks && (
            <div className="professional-card p-6">
              <div className="flex items-center space-x-3">
                <div className="text-red-400 text-xl">⚠️</div>
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-1">
                    Failed to Load Top Picks
                  </h3>
                  <p className="text-muted-foreground">
                    {picksError.detail || 'Unable to load investment picks. Please try again.'}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Top Picks Results */}
          {topPicks && !isLoadingPicks && (
            <TopPicksDisplay
              topPicks={topPicks}
              onAddToPortfolio={handleAddToPortfolio}
            />
          )}
        </div>
      )}
    </div>
  );
};