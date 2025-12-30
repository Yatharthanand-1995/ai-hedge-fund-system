import React, { useState } from 'react';
import {
  BookOpen,
  ChevronDown,
  ChevronUp,
  TrendingUp,
  Shield,
  Target,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Info,
  DollarSign,
  BarChart3
} from 'lucide-react';
import { cn } from '../../utils';

interface InvestmentGuidePanelProps {
  className?: string;
}

export const InvestmentGuidePanel: React.FC<InvestmentGuidePanelProps> = ({ className }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [activeTab, setActiveTab] = useState<'quick' | 'scores' | 'strategy' | 'rules'>('quick');

  return (
    <div className={cn('professional-card', className)}>
      {/* Header - Always Visible */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-6 flex items-center justify-between hover:bg-muted/20 transition-colors"
      >
        <div className="flex items-center space-x-3">
          <BookOpen className="h-6 w-6 text-accent" />
          <div className="text-left">
            <h2 className="text-2xl font-bold text-foreground">📚 Investment Guide: How to Use This Dashboard</h2>
            <p className="text-sm text-muted-foreground mt-1">
              Learn how to read signals, interpret scores, and make informed investment decisions
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-accent font-medium">
            {isExpanded ? 'Hide Guide' : 'Show Guide'}
          </span>
          {isExpanded ? (
            <ChevronUp className="h-5 w-5 text-accent" />
          ) : (
            <ChevronDown className="h-5 w-5 text-accent" />
          )}
        </div>
      </button>

      {/* Expandable Content */}
      {isExpanded && (
        <div className="border-t border-border">
          {/* Tab Navigation */}
          <div className="flex space-x-1 p-4 bg-muted/10 overflow-x-auto">
            <button
              onClick={() => setActiveTab('quick')}
              className={cn(
                'px-4 py-2 rounded-lg font-medium text-sm whitespace-nowrap transition-colors',
                activeTab === 'quick'
                  ? 'bg-accent text-accent-foreground'
                  : 'text-muted-foreground hover:text-foreground hover:bg-muted/20'
              )}
            >
              🎯 Quick Start
            </button>
            <button
              onClick={() => setActiveTab('scores')}
              className={cn(
                'px-4 py-2 rounded-lg font-medium text-sm whitespace-nowrap transition-colors',
                activeTab === 'scores'
                  ? 'bg-accent text-accent-foreground'
                  : 'text-muted-foreground hover:text-foreground hover:bg-muted/20'
              )}
            >
              📊 Reading Scores
            </button>
            <button
              onClick={() => setActiveTab('strategy')}
              className={cn(
                'px-4 py-2 rounded-lg font-medium text-sm whitespace-nowrap transition-colors',
                activeTab === 'strategy'
                  ? 'bg-accent text-accent-foreground'
                  : 'text-muted-foreground hover:text-foreground hover:bg-muted/20'
              )}
            >
              💰 Portfolio Strategies
            </button>
            <button
              onClick={() => setActiveTab('rules')}
              className={cn(
                'px-4 py-2 rounded-lg font-medium text-sm whitespace-nowrap transition-colors',
                activeTab === 'rules'
                  ? 'bg-accent text-accent-foreground'
                  : 'text-muted-foreground hover:text-foreground hover:bg-muted/20'
              )}
            >
              🚨 Rules & Warnings
            </button>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {/* Quick Start Tab */}
            {activeTab === 'quick' && (
              <div className="space-y-6">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-start space-x-3">
                    <Info className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <h3 className="font-semibold text-blue-900 mb-2">Before You Start</h3>
                      <p className="text-sm text-blue-800">
                        This system provides data-driven insights for educational purposes only. It is NOT professional financial advice.
                        Always do your own research, never invest more than you can afford to lose, and consider consulting a licensed financial advisor.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Step 1 */}
                  <div className="professional-card p-4 bg-green-50 border-green-200">
                    <div className="flex items-center space-x-2 mb-3">
                      <div className="bg-green-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold">1</div>
                      <h4 className="font-semibold text-foreground">Check System Health</h4>
                    </div>
                    <ul className="text-sm text-muted-foreground space-y-2">
                      <li className="flex items-start space-x-2">
                        <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                        <span><strong>AI Confidence ≥ 7.0/10</strong> - System is reliable</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                        <span><strong>Market Regime = Bullish</strong> - Good conditions</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                        <span><strong>Risk Level = Low/Medium</strong> - Acceptable risk</span>
                      </li>
                    </ul>
                  </div>

                  {/* Step 2 */}
                  <div className="professional-card p-4 bg-blue-50 border-blue-200">
                    <div className="flex items-center space-x-2 mb-3">
                      <div className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold">2</div>
                      <h4 className="font-semibold text-foreground">Find Top Stocks</h4>
                    </div>
                    <ul className="text-sm text-muted-foreground space-y-2">
                      <li className="flex items-start space-x-2">
                        <Target className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                        <span>Go to <strong>Stock Analysis</strong> tab</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <Target className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                        <span>Filter: <strong>Score ≥ 75</strong></span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <Target className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                        <span>Filter: <strong>BUY or STRONG BUY</strong></span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <Target className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                        <span>Look for <strong>HIGH confidence</strong></span>
                      </li>
                    </ul>
                  </div>

                  {/* Step 3 */}
                  <div className="professional-card p-4 bg-purple-50 border-purple-200">
                    <div className="flex items-center space-x-2 mb-3">
                      <div className="bg-purple-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold">3</div>
                      <h4 className="font-semibold text-foreground">Analyze Details</h4>
                    </div>
                    <ul className="text-sm text-muted-foreground space-y-2">
                      <li className="flex items-start space-x-2">
                        <BarChart3 className="h-4 w-4 text-purple-600 mt-0.5 flex-shrink-0" />
                        <span>Click stock to <strong>expand details</strong></span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <BarChart3 className="h-4 w-4 text-purple-600 mt-0.5 flex-shrink-0" />
                        <span>Read <strong>Investment Thesis</strong></span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <BarChart3 className="h-4 w-4 text-purple-600 mt-0.5 flex-shrink-0" />
                        <span>Check <strong>Key Strengths vs Risks</strong></span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <BarChart3 className="h-4 w-4 text-purple-600 mt-0.5 flex-shrink-0" />
                        <span>Verify <strong>all 5 agents ≥ 70</strong></span>
                      </li>
                    </ul>
                  </div>

                  {/* Step 4 */}
                  <div className="professional-card p-4 bg-yellow-50 border-yellow-200">
                    <div className="flex items-center space-x-2 mb-3">
                      <div className="bg-yellow-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold">4</div>
                      <h4 className="font-semibold text-foreground">Build Portfolio</h4>
                    </div>
                    <ul className="text-sm text-muted-foreground space-y-2">
                      <li className="flex items-start space-x-2">
                        <DollarSign className="h-4 w-4 text-yellow-600 mt-0.5 flex-shrink-0" />
                        <span>Select <strong>3-5 stocks</strong> from different sectors</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <DollarSign className="h-4 w-4 text-yellow-600 mt-0.5 flex-shrink-0" />
                        <span>Allocate based on <strong>scores</strong></span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <DollarSign className="h-4 w-4 text-yellow-600 mt-0.5 flex-shrink-0" />
                        <span>No single stock <strong>&gt; 35%</strong></span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <DollarSign className="h-4 w-4 text-yellow-600 mt-0.5 flex-shrink-0" />
                        <span>Diversify across <strong>sectors</strong></span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {/* Reading Scores Tab */}
            {activeTab === 'scores' && (
              <div className="space-y-6">
                {/* Overall Score Guide */}
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center space-x-2">
                    <TrendingUp className="h-5 w-5 text-accent" />
                    <span>Overall AI Score Interpretation</span>
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <div className="professional-card p-4 bg-green-50 border-green-200">
                      <div className="text-2xl font-bold text-green-600 mb-1">85-100</div>
                      <div className="font-semibold text-green-900 mb-2">STRONG BUY</div>
                      <p className="text-sm text-green-700">Exceptional opportunity. Top priority for allocation.</p>
                    </div>
                    <div className="professional-card p-4 bg-emerald-50 border-emerald-200">
                      <div className="text-2xl font-bold text-emerald-600 mb-1">75-84</div>
                      <div className="font-semibold text-emerald-900 mb-2">BUY</div>
                      <p className="text-sm text-emerald-700">Very good candidate. Include in portfolio.</p>
                    </div>
                    <div className="professional-card p-4 bg-lime-50 border-lime-200">
                      <div className="text-2xl font-bold text-lime-600 mb-1">65-74</div>
                      <div className="font-semibold text-lime-900 mb-2">WEAK BUY</div>
                      <p className="text-sm text-lime-700">Acceptable. Consider carefully or pass.</p>
                    </div>
                    <div className="professional-card p-4 bg-yellow-50 border-yellow-200">
                      <div className="text-2xl font-bold text-yellow-600 mb-1">55-64</div>
                      <div className="font-semibold text-yellow-900 mb-2">HOLD</div>
                      <p className="text-sm text-yellow-700">Neutral. Don't buy new positions.</p>
                    </div>
                    <div className="professional-card p-4 bg-orange-50 border-orange-200">
                      <div className="text-2xl font-bold text-orange-600 mb-1">45-54</div>
                      <div className="font-semibold text-orange-900 mb-2">WEAK SELL</div>
                      <p className="text-sm text-orange-700">Concerning. Avoid or exit positions.</p>
                    </div>
                    <div className="professional-card p-4 bg-red-50 border-red-200">
                      <div className="text-2xl font-bold text-red-600 mb-1">0-44</div>
                      <div className="font-semibold text-red-900 mb-2">SELL</div>
                      <p className="text-sm text-red-700">Poor quality. Strong sell signal.</p>
                    </div>
                  </div>
                </div>

                {/* 5-Agent System */}
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-4">Understanding the 5-Agent System</h3>
                  <div className="space-y-3">
                    <div className="professional-card p-4 bg-blue-50 border-blue-200">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <div className="text-2xl">📊</div>
                          <div>
                            <h4 className="font-semibold text-blue-900">Fundamentals Agent</h4>
                            <p className="text-sm text-blue-600">36% Weight - MOST IMPORTANT</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm text-blue-700 font-medium">Never buy if &lt; 70</div>
                        </div>
                      </div>
                      <p className="text-sm text-blue-800">
                        Analyzes financial health, profitability (ROE, ROA), revenue growth, debt levels, and valuation (P/E ratio).
                        This is your financial safety check.
                      </p>
                    </div>

                    <div className="professional-card p-4 bg-green-50 border-green-200">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <div className="text-2xl">📈</div>
                          <div>
                            <h4 className="font-semibold text-green-900">Momentum Agent</h4>
                            <p className="text-sm text-green-600">27% Weight</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm text-green-700 font-medium">Buy when ≥ 70</div>
                        </div>
                      </div>
                      <p className="text-sm text-green-800">
                        Tracks price trends, technical indicators (RSI, moving averages), volume patterns.
                        Confirms the market agrees with fundamentals.
                      </p>
                    </div>

                    <div className="professional-card p-4 bg-purple-50 border-purple-200">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <div className="text-2xl">⭐</div>
                          <div>
                            <h4 className="font-semibold text-purple-900">Quality Agent</h4>
                            <p className="text-sm text-purple-600">18% Weight</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm text-purple-700 font-medium">Higher = better hold</div>
                        </div>
                      </div>
                      <p className="text-sm text-purple-800">
                        Evaluates business model strength, competitive advantages (moat), management quality, and operational efficiency.
                      </p>
                    </div>

                    <div className="professional-card p-4 bg-amber-50 border-amber-200">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <div className="text-2xl">💭</div>
                          <div>
                            <h4 className="font-semibold text-amber-900">Sentiment Agent</h4>
                            <p className="text-sm text-amber-600">9% Weight</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm text-amber-700 font-medium">Don't chase alone</div>
                        </div>
                      </div>
                      <p className="text-sm text-amber-800">
                        Analyzes analyst ratings, target prices, and market sentiment. Useful but shouldn't drive decisions alone.
                      </p>
                    </div>

                    <div className="professional-card p-4 bg-pink-50 border-pink-200">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <div className="text-2xl">💰</div>
                          <div>
                            <h4 className="font-semibold text-pink-900">Institutional Flow Agent</h4>
                            <p className="text-sm text-pink-600">10% Weight</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm text-pink-700 font-medium">Follow smart money</div>
                        </div>
                      </div>
                      <p className="text-sm text-pink-800">
                        Detects institutional buying and selling patterns through volume analysis (OBV, MFI, CMF). Tracks where smart money is flowing.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Portfolio Strategies Tab */}
            {activeTab === 'strategy' && (
              <div className="space-y-6">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h3 className="font-semibold text-blue-900 mb-2">Choose Based on Your Risk Tolerance</h3>
                  <p className="text-sm text-blue-800">
                    These strategies assume you have capital to invest. If current market scores are below 75, consider waiting for better opportunities.
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {/* Conservative */}
                  <div className="professional-card p-5 bg-green-50 border-green-200">
                    <div className="flex items-center space-x-2 mb-3">
                      <Shield className="h-6 w-6 text-green-600" />
                      <h4 className="text-lg font-semibold text-green-900">Conservative</h4>
                    </div>
                    <div className="text-sm text-green-800 space-y-3">
                      <div>
                        <div className="font-semibold mb-1">Goal: Lower Risk, Steady Returns</div>
                        <div className="text-xs">Recommended for beginners</div>
                      </div>
                      <div>
                        <div className="font-semibold mb-1">Portfolio:</div>
                        <ul className="space-y-1 text-xs">
                          <li>• 3 stocks only</li>
                          <li>• All scores ≥ 80</li>
                          <li>• All Fundamentals ≥ 75</li>
                          <li>• Different sectors</li>
                        </ul>
                      </div>
                      <div>
                        <div className="font-semibold mb-1">Allocation:</div>
                        <ul className="space-y-1 text-xs">
                          <li>• Stock 1: 35% ($350)</li>
                          <li>• Stock 2: 35% ($350)</li>
                          <li>• Stock 3: 30% ($300)</li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  {/* Moderate */}
                  <div className="professional-card p-5 bg-blue-50 border-blue-200">
                    <div className="flex items-center space-x-2 mb-3">
                      <Target className="h-6 w-6 text-blue-600" />
                      <h4 className="text-lg font-semibold text-blue-900">Moderate</h4>
                    </div>
                    <div className="text-sm text-blue-800 space-y-3">
                      <div>
                        <div className="font-semibold mb-1">Goal: Balanced Risk/Reward</div>
                        <div className="text-xs">Most popular strategy</div>
                      </div>
                      <div>
                        <div className="font-semibold mb-1">Portfolio:</div>
                        <ul className="space-y-1 text-xs">
                          <li>• 4-5 stocks</li>
                          <li>• Scores 75-95</li>
                          <li>• Mix momentum + fundamentals</li>
                          <li>• 3+ different sectors</li>
                        </ul>
                      </div>
                      <div>
                        <div className="font-semibold mb-1">Allocation:</div>
                        <ul className="space-y-1 text-xs">
                          <li>• Stock 1: 25% ($250)</li>
                          <li>• Stock 2: 22.5% ($225)</li>
                          <li>• Stock 3: 20% ($200)</li>
                          <li>• Stock 4: 17.5% ($175)</li>
                          <li>• Stock 5: 15% ($150)</li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  {/* Aggressive */}
                  <div className="professional-card p-5 bg-red-50 border-red-200">
                    <div className="flex items-center space-x-2 mb-3">
                      <TrendingUp className="h-6 w-6 text-red-600" />
                      <h4 className="text-lg font-semibold text-red-900">Aggressive</h4>
                    </div>
                    <div className="text-sm text-red-800 space-y-3">
                      <div>
                        <div className="font-semibold mb-1">Goal: Maximum Returns, Higher Risk</div>
                        <div className="text-xs">For experienced investors</div>
                      </div>
                      <div>
                        <div className="font-semibold mb-1">Portfolio:</div>
                        <ul className="space-y-1 text-xs">
                          <li>• 2-3 stocks only</li>
                          <li>• Scores ≥ 85</li>
                          <li>• High momentum (≥ 80)</li>
                          <li>• Can concentrate sectors</li>
                        </ul>
                      </div>
                      <div>
                        <div className="font-semibold mb-1">Allocation:</div>
                        <ul className="space-y-1 text-xs">
                          <li>• Stock 1: 50% ($500)</li>
                          <li>• Stock 2: 30% ($300)</li>
                          <li>• Stock 3: 20% ($200)</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Rules & Warnings Tab */}
            {activeTab === 'rules' && (
              <div className="space-y-6">
                {/* When to Buy */}
                <div>
                  <h3 className="text-lg font-semibold text-green-600 mb-3 flex items-center space-x-2">
                    <CheckCircle className="h-5 w-5" />
                    <span>✅ When to BUY</span>
                  </h3>
                  <div className="professional-card p-4 bg-green-50 border-green-200">
                    <ul className="space-y-2 text-sm text-green-800">
                      <li className="flex items-start space-x-2">
                        <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                        <span><strong>AI Confidence ≥ 7.0/10</strong> - System is reliable</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                        <span><strong>Overall Score ≥ 75</strong> - Strong buy signal</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                        <span><strong>Fundamentals ≥ 70</strong> - Financial health confirmed</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                        <span><strong>At least 3 of 5 agents ≥ 70</strong> - Consensus signal</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                        <span><strong>Confidence: HIGH or MEDIUM</strong> - Data quality good</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                        <span><strong>Read and understood Investment Thesis</strong> - Know what you're buying</span>
                      </li>
                    </ul>
                  </div>
                </div>

                {/* When to WAIT */}
                <div>
                  <h3 className="text-lg font-semibold text-yellow-600 mb-3 flex items-center space-x-2">
                    <AlertTriangle className="h-5 w-5" />
                    <span>⏸️ When to WAIT (Stay in Cash)</span>
                  </h3>
                  <div className="professional-card p-4 bg-yellow-50 border-yellow-200">
                    <ul className="space-y-2 text-sm text-yellow-800">
                      <li className="flex items-start space-x-2">
                        <AlertTriangle className="h-4 w-4 text-yellow-600 mt-0.5 flex-shrink-0" />
                        <span><strong>AI Confidence &lt; 6.0</strong> - Unreliable signals</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <AlertTriangle className="h-4 w-4 text-yellow-600 mt-0.5 flex-shrink-0" />
                        <span><strong>No stocks scoring ≥ 75</strong> - No strong opportunities</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <AlertTriangle className="h-4 w-4 text-yellow-600 mt-0.5 flex-shrink-0" />
                        <span><strong>Market Regime = Bearish</strong> - Market declining</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <AlertTriangle className="h-4 w-4 text-yellow-600 mt-0.5 flex-shrink-0" />
                        <span><strong>Risk Level = High</strong> - Elevated uncertainty</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <AlertTriangle className="h-4 w-4 text-yellow-600 mt-0.5 flex-shrink-0" />
                        <span><strong>You don't understand the companies</strong> - Do more research</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <AlertTriangle className="h-4 w-4 text-yellow-600 mt-0.5 flex-shrink-0" />
                        <span><strong>Cash is a position</strong> - Waiting for opportunities is valid</span>
                      </li>
                    </ul>
                  </div>
                </div>

                {/* When to SELL */}
                <div>
                  <h3 className="text-lg font-semibold text-red-600 mb-3 flex items-center space-x-2">
                    <XCircle className="h-5 w-5" />
                    <span>❌ When to SELL or AVOID</span>
                  </h3>
                  <div className="professional-card p-4 bg-red-50 border-red-200">
                    <ul className="space-y-2 text-sm text-red-800">
                      <li className="flex items-start space-x-2">
                        <XCircle className="h-4 w-4 text-red-600 mt-0.5 flex-shrink-0" />
                        <span><strong>Score drops below 60</strong> - Quality deteriorating</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <XCircle className="h-4 w-4 text-red-600 mt-0.5 flex-shrink-0" />
                        <span><strong>Fundamentals &lt; 65</strong> - Financial health declining</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <XCircle className="h-4 w-4 text-red-600 mt-0.5 flex-shrink-0" />
                        <span><strong>Confidence = LOW</strong> - Data quality poor</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <XCircle className="h-4 w-4 text-red-600 mt-0.5 flex-shrink-0" />
                        <span><strong>Stock loses 15% from your buy price</strong> - Stop-loss triggered</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <XCircle className="h-4 w-4 text-red-600 mt-0.5 flex-shrink-0" />
                        <span><strong>Recommendation changes to SELL</strong> - System says exit</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <XCircle className="h-4 w-4 text-red-600 mt-0.5 flex-shrink-0" />
                        <span><strong>Investment thesis no longer holds</strong> - Fundamentals changed</span>
                      </li>
                    </ul>
                  </div>
                </div>

                {/* Risk Management */}
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-3 flex items-center space-x-2">
                    <Shield className="h-5 w-5 text-accent" />
                    <span>🛡️ Risk Management Rules</span>
                  </h3>
                  <div className="professional-card p-4 bg-muted/20">
                    <ul className="space-y-2 text-sm text-muted-foreground">
                      <li className="flex items-start space-x-2">
                        <Shield className="h-4 w-4 text-accent mt-0.5 flex-shrink-0" />
                        <span><strong>Position Sizing:</strong> No single stock &gt; 35% of portfolio</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <Shield className="h-4 w-4 text-accent mt-0.5 flex-shrink-0" />
                        <span><strong>Sector Limits:</strong> No single sector &gt; 50% of portfolio</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <Shield className="h-4 w-4 text-accent mt-0.5 flex-shrink-0" />
                        <span><strong>Stop-Loss:</strong> Exit if position loses 15% from entry</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <Shield className="h-4 w-4 text-accent mt-0.5 flex-shrink-0" />
                        <span><strong>Rebalancing:</strong> Review quarterly, like the backtest</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <Shield className="h-4 w-4 text-accent mt-0.5 flex-shrink-0" />
                        <span><strong>Cash Reserve:</strong> Keep 5-10% in cash for opportunities</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <Shield className="h-4 w-4 text-accent mt-0.5 flex-shrink-0" />
                        <span><strong>Never Average Down:</strong> Don't add to losing positions</span>
                      </li>
                    </ul>
                  </div>
                </div>

                {/* Final Warning */}
                <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4">
                  <div className="flex items-start space-x-3">
                    <AlertTriangle className="h-6 w-6 text-red-600 flex-shrink-0" />
                    <div>
                      <h4 className="font-bold text-red-900 mb-2">⚠️ Critical Reminder</h4>
                      <p className="text-sm text-red-800 mb-2">
                        This system is for <strong>educational and research purposes ONLY</strong>. It is NOT professional financial advice.
                      </p>
                      <ul className="text-xs text-red-700 space-y-1">
                        <li>• Markets are unpredictable - you can lose money</li>
                        <li>• Past performance does NOT guarantee future results</li>
                        <li>• Only invest what you can afford to lose</li>
                        <li>• Always do your own research</li>
                        <li>• Consider consulting a licensed financial advisor</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
