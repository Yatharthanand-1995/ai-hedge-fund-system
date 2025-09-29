import React, { useState } from 'react';
import { useStockAnalysis, useAnalyzeStock } from '../hooks/useApi';
import { StockSearchForm } from '../components/forms/StockSearchForm';
import { StockAnalysisDisplay } from '../components/analysis/StockAnalysisDisplay';

export const StockAnalysisPage: React.FC = () => {
  const [selectedSymbol, setSelectedSymbol] = useState<string | null>(null);

  const { data: analysis, isLoading: isQueryLoading, error: queryError } = useStockAnalysis(selectedSymbol);
  const { mutate: analyzeStock, isPending: isMutationLoading, error: mutationError } = useAnalyzeStock();

  const isLoading = isQueryLoading || isMutationLoading;
  const error = queryError || mutationError;

  const handleSearch = (symbol: string) => {
    setSelectedSymbol(symbol);
    // Trigger fresh analysis
    analyzeStock({ symbol });
  };

  return (
    <div>
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-foreground mb-2">
            📊 Stock Analysis
          </h1>
          <p className="text-xl text-muted-foreground">
            Get comprehensive investment analysis powered by our 4-agent AI system
          </p>
        </div>

        {/* Search Section */}
        <div className="mb-8">
          <div className="professional-card p-6">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
              <div>
                <h2 className="text-xl font-semibold text-foreground mb-2">
                  Analyze Any Stock
                </h2>
                <p className="text-muted-foreground">
                  Enter a stock symbol to get real-time analysis from our fundamentals, momentum, quality, and sentiment agents
                </p>
              </div>
              <StockSearchForm
                onSearch={handleSearch}
                isLoading={isLoading}
                className="lg:w-auto"
              />
            </div>
          </div>
        </div>

        {/* Loading State */}
        {isLoading && selectedSymbol && (
          <div className="professional-card p-8">
            <div className="flex flex-col items-center justify-center space-y-4">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent"></div>
              <div className="text-center">
                <h3 className="text-lg font-semibold text-foreground mb-2">
                  Analyzing {selectedSymbol}
                </h3>
                <p className="text-muted-foreground">
                  Our 4-agent system is evaluating fundamentals, momentum, quality, and sentiment...
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && !isLoading && (
          <div className="professional-card p-6">
            <div className="flex items-center space-x-3">
              <div className="text-red-400 text-xl">⚠️</div>
              <div>
                <h3 className="text-lg font-semibold text-foreground mb-1">
                  Analysis Failed
                </h3>
                <p className="text-muted-foreground">
                  {error.detail || 'Unable to analyze the stock. Please try again.'}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Analysis Results */}
        {analysis && !isLoading && (
          <StockAnalysisDisplay analysis={analysis} />
        )}

        {/* Getting Started Section */}
        {!selectedSymbol && !isLoading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="professional-card p-6">
              <div className="text-3xl mb-4">🔍</div>
              <h3 className="text-lg font-semibold text-foreground mb-2">
                Fundamentals Agent
              </h3>
              <p className="text-muted-foreground text-sm">
                Analyzes financial health, profitability metrics, growth rates, and valuation ratios to assess intrinsic value
              </p>
            </div>

            <div className="professional-card p-6">
              <div className="text-3xl mb-4">📈</div>
              <h3 className="text-lg font-semibold text-foreground mb-2">
                Momentum Agent
              </h3>
              <p className="text-muted-foreground text-sm">
                Evaluates technical indicators, price trends, volume patterns, and market momentum signals
              </p>
            </div>

            <div className="professional-card p-6">
              <div className="text-3xl mb-4">⭐</div>
              <h3 className="text-lg font-semibold text-foreground mb-2">
                Quality Agent
              </h3>
              <p className="text-muted-foreground text-sm">
                Assesses business quality, competitive advantages, management effectiveness, and operational efficiency
              </p>
            </div>

            <div className="professional-card p-6">
              <div className="text-3xl mb-4">💭</div>
              <h3 className="text-lg font-semibold text-foreground mb-2">
                Sentiment Agent
              </h3>
              <p className="text-muted-foreground text-sm">
                Monitors market sentiment, analyst opinions, news coverage, and social media indicators
              </p>
            </div>

            <div className="professional-card p-6">
              <div className="text-3xl mb-4">🎯</div>
              <h3 className="text-lg font-semibold text-foreground mb-2">
                Weighted Scoring
              </h3>
              <p className="text-muted-foreground text-sm">
                Combines all agent scores using institutional-grade weighting: 40% fundamentals, 30% momentum, 20% quality, 10% sentiment
              </p>
            </div>

            <div className="professional-card p-6">
              <div className="text-3xl mb-4">📋</div>
              <h3 className="text-lg font-semibold text-foreground mb-2">
                Investment Narrative
              </h3>
              <p className="text-muted-foreground text-sm">
                Generates comprehensive investment thesis with key strengths, risks, price targets, and actionable insights
              </p>
            </div>
          </div>
        )}
    </div>
  );
};