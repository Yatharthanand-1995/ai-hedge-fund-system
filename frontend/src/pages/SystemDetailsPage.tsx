import React, { useState } from 'react';
import {
  BookOpen,
  Bot,
  Target,
  BarChart3,
  Plug,
  TrendingUp,
  AlertTriangle,
  ChevronDown,
  ChevronRight,
  Activity,
  Brain,
  Sparkles,
  MessageSquare,
  Database,
  Zap,
  Shield,
  Calendar,
  DollarSign,
  Settings,
  Code,
  Info,
  Users,
} from 'lucide-react';

interface TechnicalDeepDiveProps {
  title: string;
  children: React.ReactNode;
}

const TechnicalDeepDive: React.FC<TechnicalDeepDiveProps> = ({ title, children }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="mt-4 border border-blue-500/30 rounded-lg overflow-hidden bg-blue-950/20">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 flex items-center justify-between bg-blue-900/30 hover:bg-blue-900/50 transition-colors"
      >
        <span className="text-sm font-semibold text-blue-300 flex items-center gap-2">
          <Code className="w-4 h-4" />
          {title}
        </span>
        {isExpanded ? <ChevronDown className="w-4 h-4 text-blue-400" /> : <ChevronRight className="w-4 h-4 text-blue-400" />}
      </button>
      {isExpanded && (
        <div className="p-4 text-sm text-gray-300 space-y-3">
          {children}
        </div>
      )}
    </div>
  );
};

interface InfoBoxProps {
  type: 'info' | 'warning' | 'success';
  children: React.ReactNode;
}

const InfoBox: React.FC<InfoBoxProps> = ({ type, children }) => {
  const styles = {
    info: 'bg-blue-950/30 border-blue-500/40 text-blue-200',
    warning: 'bg-yellow-950/30 border-yellow-500/40 text-yellow-200',
    success: 'bg-emerald-950/30 border-emerald-500/40 text-emerald-200',
  };

  return (
    <div className={`p-3 rounded-lg border ${styles[type]} text-sm`}>
      {children}
    </div>
  );
};

interface CodeBlockProps {
  language: string;
  code: string;
}

const CodeBlock: React.FC<CodeBlockProps> = ({ language, code }) => {
  return (
    <div className="bg-gray-900/80 border border-gray-700 rounded-lg p-4 overflow-x-auto">
      <div className="text-xs text-gray-500 mb-2 uppercase">{language}</div>
      <pre className="text-sm text-gray-200 font-mono">
        <code>{code}</code>
      </pre>
    </div>
  );
};

const SystemDetailsPage: React.FC = () => {
  const [activeSection, setActiveSection] = useState('architecture');

  const scrollToSection = (sectionId: string) => {
    setActiveSection(sectionId);
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  const sidebarItems = [
    { id: 'architecture', label: 'System Architecture', icon: BookOpen },
    { id: 'agents', label: '5-Agent Analysis System', icon: Bot },
    { id: 'adaptive-weights', label: 'Adaptive Weights & Market Regime', icon: Target },
    { id: 'backtesting', label: 'Backtesting Engine v2.0', icon: BarChart3 },
    { id: 'api', label: 'API & Integration Guide', icon: Plug },
    { id: 'data-sources', label: 'Data Sources & Calculations', icon: Database },
    { id: 'limitations', label: 'Limitations & Disclaimers', icon: AlertTriangle },
  ];

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Left Sidebar Navigation */}
      <div className="w-64 bg-card border-r border-border/50 overflow-y-auto sticky top-0 h-screen">
        <div className="p-6 border-b border-border/50">
          <h2 className="text-lg font-bold text-foreground flex items-center gap-2">
            <BookOpen className="w-5 h-5" />
            System Details
          </h2>
          <p className="text-xs text-muted-foreground mt-1">
            Comprehensive technical documentation
          </p>
        </div>

        <nav className="p-3">
          {sidebarItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => scrollToSection(item.id)}
                className={`w-full text-left px-3 py-2.5 rounded-lg mb-1 flex items-center gap-2 text-sm transition-all ${
                  activeSection === item.id
                    ? 'bg-accent text-accent-foreground font-medium'
                    : 'text-muted-foreground hover:bg-accent/50 hover:text-foreground'
                }`}
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                <span className="text-xs">{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Right Content Area */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto px-8 py-8 space-y-12">
          {/* System Architecture Section */}
          <section id="architecture" className="professional-card">
            <div className="flex items-start gap-3 mb-6">
              <BookOpen className="w-6 h-6 text-blue-400 flex-shrink-0 mt-1" />
              <div className="flex-1">
                <h2 className="text-2xl font-bold text-foreground mb-2">System Architecture Overview</h2>
                <p className="text-muted-foreground">
                  The AI Hedge Fund System is a professional-grade investment analysis platform that combines quantitative
                  analysis with qualitative reasoning to generate actionable investment recommendations.
                </p>
              </div>
            </div>

            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-foreground mb-3 flex items-center gap-2">
                  <Activity className="w-5 h-5 text-blue-400" />
                  Data Flow Pipeline
                </h3>
                <div className="bg-gray-900/50 border border-gray-700 rounded-lg p-6">
                  <div className="font-mono text-xs text-gray-300 space-y-2">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                      <span className="text-blue-400 font-semibold">Yahoo Finance API</span>
                      <span className="text-gray-500">→</span>
                      <span>Real-time market data</span>
                    </div>
                    <div className="pl-5 flex items-center gap-2">
                      <span className="text-gray-500">↓</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-emerald-500"></div>
                      <span className="text-emerald-400 font-semibold">EnhancedYahooProvider</span>
                      <span className="text-gray-500">(20-min cache)</span>
                    </div>
                    <div className="pl-5 text-gray-400 text-xs">
                      • Fetches comprehensive market data<br />
                      • Calculates 40+ technical indicators (TA-Lib)<br />
                      • Handles numpy serialization issues
                    </div>
                    <div className="pl-5 flex items-center gap-2">
                      <span className="text-gray-500">↓</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-purple-500"></div>
                      <span className="text-purple-400 font-semibold">5 Specialized Agents</span>
                      <span className="text-gray-500">(parallel processing)</span>
                    </div>
                    <div className="pl-5 grid grid-cols-2 gap-2 text-xs mt-2">
                  <div className="text-orange-400">• Fundamentals (36%)</div>
                  <div className="text-blue-400">• Momentum (27%)</div>
                  <div className="text-emerald-400">• Quality (18%)</div>
                  <div className="text-yellow-400">• Sentiment (9%)</div>
                  <div className="text-pink-400">• Institutional Flow (10%)</div>
                </div>
                    <div className="pl-5 flex items-center gap-2">
                      <span className="text-gray-500">↓</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                      <span className="text-yellow-400 font-semibold">StockScorer</span>
                      <span className="text-gray-500">→</span>
                      <span>Weighted composite score (0-100)</span>
                    </div>
                    <div className="pl-5 flex items-center gap-2">
                      <span className="text-gray-500">↓</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-pink-500"></div>
                      <span className="text-pink-400 font-semibold">Narrative Engine</span>
                      <span className="text-gray-500">→</span>
                      <span>Human-readable investment thesis</span>
                    </div>
                    <div className="pl-5 flex items-center gap-2">
                      <span className="text-gray-500">↓</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-green-500"></div>
                      <span className="text-green-400 font-semibold">FastAPI Endpoints</span>
                      <span className="text-gray-500">→</span>
                      <span>JSON response to frontend</span>
                    </div>
                  </div>
                </div>
              </div>

              <InfoBox type="info">
                <strong>Caching Strategy:</strong> The system implements multi-layer caching:
                <ul className="list-disc list-inside mt-2 ml-2 space-y-1">
                  <li><strong>EnhancedYahooProvider:</strong> 20-minute TTL for market data</li>
                  <li><strong>API Layer:</strong> 15-minute TTL for complete analysis results</li>
                  <li><strong>Market Regime:</strong> 6-hour TTL for regime detection</li>
                </ul>
              </InfoBox>

              <TechnicalDeepDive title="Core Components & File Locations">
                <div className="space-y-3">
                  <div>
                    <strong className="text-blue-300">Data Provider:</strong>
                    <code className="block mt-1 text-xs bg-gray-800 p-2 rounded">
                      data/enhanced_provider.py:EnhancedYahooProvider
                    </code>
                    <p className="text-xs text-gray-400 mt-1">
                      Fetches data from Yahoo Finance, calculates 40+ technical indicators using TA-Lib,
                      implements 20-minute caching for 50-stock universe.
                    </p>
                  </div>
                  <div>
                    <strong className="text-blue-300">Stock Scorer:</strong>
                    <code className="block mt-1 text-xs bg-gray-800 p-2 rounded">
                      core/stock_scorer.py:StockScorer
                    </code>
                    <p className="text-xs text-gray-400 mt-1">
                      Coordinates all 5 agents, combines weighted scores, returns confidence-weighted recommendations.
                    </p>
                  </div>
                  <div>
                    <strong className="text-blue-300">Narrative Engine:</strong>
                    <code className="block mt-1 text-xs bg-gray-800 p-2 rounded">
                      narrative_engine/narrative_engine.py:InvestmentNarrativeEngine
                    </code>
                    <p className="text-xs text-gray-400 mt-1">
                      Converts quantitative scores to human-readable investment thesis with optional LLM integration.
                    </p>
                  </div>
                </div>
              </TechnicalDeepDive>
            </div>
          </section>

          {/* 5-Agent Analysis System */}
          <section id="agents" className="professional-card">
            <div className="flex items-start gap-3 mb-6">
              <Bot className="w-6 h-6 text-purple-400 flex-shrink-0 mt-1" />
              <div className="flex-1">
                <h2 className="text-2xl font-bold text-foreground mb-2">5-Agent Analysis System</h2>
                <p className="text-muted-foreground">
                  Each agent is a specialized analyzer that evaluates different aspects of a stock's investment potential.
                  Agents run in parallel and return standardized outputs with confidence scores.
                </p>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              {/* Fundamentals Agent */}
              <div className="border border-orange-500/30 rounded-lg p-5 bg-orange-950/20">
                <div className="flex items-center gap-2 mb-3">
                  <Brain className="w-5 h-5 text-orange-400" />
                  <h3 className="text-lg font-bold text-orange-300">Fundamentals Agent</h3>
                  <span className="ml-auto text-orange-400 font-bold text-lg">36%</span>
                </div>
                <p className="text-sm text-gray-300 mb-3">
                  Analyzes financial health, profitability, growth, and valuation metrics.
                </p>
                <div className="space-y-2 text-sm">
                  <div className="flex items-start gap-2">
                    <DollarSign className="w-4 h-4 text-orange-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <strong className="text-orange-200">Key Metrics:</strong>
                      <div className="text-gray-400 text-xs mt-1">
                        ROE, P/E ratio, revenue growth, debt-to-equity, profit margins, EPS growth
                      </div>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <Database className="w-4 h-4 text-orange-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <strong className="text-orange-200">Data Sources:</strong>
                      <div className="text-gray-400 text-xs mt-1">
                        Financial statements, balance sheets, income statements (yfinance)
                      </div>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <Code className="w-4 h-4 text-orange-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <strong className="text-orange-200">File Location:</strong>
                      <div className="text-gray-400 text-xs mt-1 font-mono">
                        agents/fundamentals_agent.py
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Momentum Agent */}
              <div className="border border-blue-500/30 rounded-lg p-5 bg-blue-950/20">
                <div className="flex items-center gap-2 mb-3">
                  <TrendingUp className="w-5 h-5 text-blue-400" />
                  <h3 className="text-lg font-bold text-blue-300">Momentum Agent</h3>
                  <span className="ml-auto text-blue-400 font-bold text-lg">27%</span>
                </div>
                <p className="text-sm text-gray-300 mb-3">
                  Technical analysis and price trend evaluation using advanced indicators.
                </p>
                <div className="space-y-2 text-sm">
                  <div className="flex items-start gap-2">
                    <Activity className="w-4 h-4 text-blue-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <strong className="text-blue-200">Key Metrics:</strong>
                      <div className="text-gray-400 text-xs mt-1">
                        RSI, moving averages (SMA/EMA), MACD, Bollinger Bands, price momentum
                      </div>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <Zap className="w-4 h-4 text-blue-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <strong className="text-blue-200">Technology:</strong>
                      <div className="text-gray-400 text-xs mt-1">
                        TA-Lib for technical indicator calculations
                      </div>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <Code className="w-4 h-4 text-blue-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <strong className="text-blue-200">File Location:</strong>
                      <div className="text-gray-400 text-xs mt-1 font-mono">
                        agents/momentum_agent.py
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Quality Agent */}
              <div className="border border-emerald-500/30 rounded-lg p-5 bg-emerald-950/20">
                <div className="flex items-center gap-2 mb-3">
                  <Shield className="w-5 h-5 text-emerald-400" />
                  <h3 className="text-lg font-bold text-emerald-300">Quality Agent</h3>
                  <span className="ml-auto text-emerald-400 font-bold text-lg">18%</span>
                </div>
                <p className="text-sm text-gray-300 mb-3">
                  Business quality and operational efficiency assessment.
                </p>
                <div className="space-y-2 text-sm">
                  <div className="flex items-start gap-2">
                    <Sparkles className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <strong className="text-emerald-200">Key Metrics:</strong>
                      <div className="text-gray-400 text-xs mt-1">
                        Business model characteristics, operational efficiency, competitive moat
                      </div>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <Settings className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <strong className="text-emerald-200">Analysis Focus:</strong>
                      <div className="text-gray-400 text-xs mt-1">
                        Long-term sustainability, competitive advantages, management quality
                      </div>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <Code className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <strong className="text-emerald-200">File Location:</strong>
                      <div className="text-gray-400 text-xs mt-1 font-mono">
                        agents/quality_agent.py
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Sentiment Agent */}
              <div className="border border-yellow-500/30 rounded-lg p-5 bg-yellow-950/20">
                <div className="flex items-center gap-2 mb-3">
                  <MessageSquare className="w-5 h-5 text-yellow-400" />
                  <h3 className="text-lg font-bold text-yellow-300">Sentiment Agent</h3>
                  <span className="ml-auto text-yellow-400 font-bold text-lg">9%</span>
                </div>
                <p className="text-sm text-gray-300 mb-3">
                  Market sentiment and analyst outlook analysis with optional AI integration.
                </p>
                <div className="space-y-2 text-sm">
                  <div className="flex items-start gap-2">
                    <Brain className="w-4 h-4 text-yellow-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <strong className="text-yellow-200">Key Metrics:</strong>
                      <div className="text-gray-400 text-xs mt-1">
                        Analyst ratings, news sentiment, social media trends (when available)
                      </div>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <Sparkles className="w-4 h-4 text-yellow-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <strong className="text-yellow-200">LLM Integration:</strong>
                      <div className="text-gray-400 text-xs mt-1">
                        Optional: OpenAI GPT, Anthropic Claude, or Google Gemini (default)
                      </div>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <Code className="w-4 h-4 text-yellow-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <strong className="text-yellow-200">File Location:</strong>
                      <div className="text-gray-400 text-xs mt-1 font-mono">
                        agents/sentiment_agent.py
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Institutional Flow Agent */}
              <div className="border border-pink-500/30 rounded-lg p-5 bg-pink-950/20">
                <div className="flex items-center gap-2 mb-3">
                  <Users className="w-5 h-5 text-pink-400" />
                  <h3 className="text-lg font-bold text-pink-300">Institutional Flow Agent</h3>
                  <span className="ml-auto text-pink-400 font-bold text-lg">10%</span>
                </div>
                <p className="text-sm text-gray-300 mb-3">
                  Detects institutional buying/selling patterns ("smart money") using volume flow analysis.
                </p>
                <div className="space-y-2 text-sm">
                  <div className="flex items-start gap-2">
                    <TrendingUp className="w-4 h-4 text-pink-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <strong className="text-pink-200">Key Metrics:</strong>
                      <div className="text-gray-400 text-xs mt-1">
                        OBV, Accumulation/Distribution, MFI, Chaikin Money Flow, VWAP, Volume Z-score
                      </div>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <Activity className="w-4 h-4 text-pink-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <strong className="text-pink-200">Analysis Focus:</strong>
                      <div className="text-gray-400 text-xs mt-1">
                        Volume flow trends, unusual institutional activity, smart money positioning
                      </div>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <Code className="w-4 h-4 text-pink-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <strong className="text-pink-200">File Location:</strong>
                      <div className="text-gray-400 text-xs mt-1 font-mono">
                        agents/institutional_flow_agent.py
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <TechnicalDeepDive title="Agent Scoring Formula & Confidence Calculation">
              <div className="space-y-4">
                <div>
                  <strong className="text-blue-300">Standard Agent Output Format:</strong>
                  <CodeBlock
                    language="Python"
                    code={`{
  "score": 75.5,           # 0-100 scale
  "confidence": 0.85,      # 0-1 scale (data availability)
  "metrics": {             # Agent-specific metrics
    "rsi": 65.3,
    "sma_20": 145.67,
    # ... more metrics
  },
  "reasoning": "Stock shows strong momentum with RSI at 65..."
}`}
                  />
                </div>
                <div>
                  <strong className="text-blue-300">Composite Score Calculation:</strong>
                  <CodeBlock
                    language="Python"
                    code={`composite_score = (
  fundamentals_score * 0.36 +
  momentum_score * 0.27 +
  quality_score * 0.18 +
  sentiment_score * 0.09 +
  institutional_flow_score * 0.10
)

composite_confidence = (
  fundamentals_confidence * 0.36 +
  momentum_confidence * 0.27 +
  quality_confidence * 0.18 +
  sentiment_confidence * 0.09 +
  institutional_flow_confidence * 0.10
)`}
                  />
                </div>
                <div>
                  <strong className="text-blue-300">Recommendation Mapping:</strong>
                  <div className="grid grid-cols-2 gap-2 mt-2 text-xs">
                    <div className="bg-green-900/30 p-2 rounded">80-100: <strong>STRONG BUY</strong></div>
                    <div className="bg-emerald-900/30 p-2 rounded">65-79: <strong>BUY</strong></div>
                    <div className="bg-blue-900/30 p-2 rounded">55-64: <strong>WEAK BUY</strong></div>
                    <div className="bg-yellow-900/30 p-2 rounded">45-54: <strong>HOLD</strong></div>
                    <div className="bg-orange-900/30 p-2 rounded">35-44: <strong>WEAK SELL</strong></div>
                    <div className="bg-red-900/30 p-2 rounded">0-34: <strong>SELL</strong></div>
                  </div>
                </div>
              </div>
            </TechnicalDeepDive>
          </section>

          {/* Adaptive Weights & Market Regime */}
          <section id="adaptive-weights" className="professional-card">
            <div className="flex items-start gap-3 mb-6">
              <Target className="w-6 h-6 text-purple-400 flex-shrink-0 mt-1" />
              <div className="flex-1">
                <h2 className="text-2xl font-bold text-foreground mb-2">Adaptive Weights & Market Regime Detection</h2>
                <p className="text-muted-foreground">
                  The system can automatically adjust agent weights based on current market conditions using ML-based regime detection.
                </p>
              </div>
            </div>

            <div className="space-y-6">
              <InfoBox type="success">
                <strong>Performance Boost:</strong> Adaptive weights provide 5-10% performance improvement in different market cycles
                by emphasizing the most relevant analysis factors for current conditions.
              </InfoBox>

              <div>
                <h3 className="text-lg font-semibold text-foreground mb-3 flex items-center gap-2">
                  <Activity className="w-5 h-5 text-purple-400" />
                  How Market Regime Detection Works
                </h3>
                <div className="space-y-3">
                  <div className="bg-gray-900/50 border border-gray-700 rounded-lg p-4">
                    <div className="font-semibold text-blue-300 mb-2">Step 1: Trend Analysis (SPY-based)</div>
                    <ul className="list-disc list-inside text-sm text-gray-300 space-y-1 ml-2">
                      <li><strong>BULL:</strong> 50-day SMA &gt; 200-day SMA and price trending upward</li>
                      <li><strong>BEAR:</strong> 50-day SMA &lt; 200-day SMA and price trending downward</li>
                      <li><strong>SIDEWAYS:</strong> Consolidation with no clear directional trend</li>
                    </ul>
                  </div>
                  <div className="bg-gray-900/50 border border-gray-700 rounded-lg p-4">
                    <div className="font-semibold text-emerald-300 mb-2">Step 2: Volatility Analysis</div>
                    <ul className="list-disc list-inside text-sm text-gray-300 space-y-1 ml-2">
                      <li><strong>HIGH_VOL:</strong> 30-day volatility &gt; 75th percentile</li>
                      <li><strong>NORMAL_VOL:</strong> 30-day volatility in normal range</li>
                      <li><strong>LOW_VOL:</strong> 30-day volatility &lt; 25th percentile</li>
                    </ul>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-foreground mb-3">Adaptive Weight Matrix</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm border-collapse">
                    <thead>
                      <tr className="bg-gray-800 border-b border-gray-700">
                        <th className="px-4 py-2 text-left">Market Regime</th>
                        <th className="px-4 py-2 text-center text-orange-400">Fundamentals</th>
                        <th className="px-4 py-2 text-center text-blue-400">Momentum</th>
                        <th className="px-4 py-2 text-center text-emerald-400">Quality</th>
                        <th className="px-4 py-2 text-center text-yellow-400">Sentiment</th>
                        <th className="px-4 py-2 text-center text-pink-400">Inst Flow</th>
                      </tr>
                    </thead>
                    <tbody className="text-gray-300">
                      <tr className="border-b border-gray-800 bg-green-950/20">
                        <td className="px-4 py-2 font-semibold">Bull + Normal Vol</td>
                        <td className="px-4 py-2 text-center">36%</td>
                        <td className="px-4 py-2 text-center">27%</td>
                        <td className="px-4 py-2 text-center">18%</td>
                        <td className="px-4 py-2 text-center">9%</td>
                        <td className="px-4 py-2 text-center">10%</td>
                      </tr>
                      <tr className="border-b border-gray-800 bg-blue-950/20">
                        <td className="px-4 py-2 font-semibold">Bull + High Vol</td>
                        <td className="px-4 py-2 text-center">27%</td>
                        <td className="px-4 py-2 text-center font-bold">36%</td>
                        <td className="px-4 py-2 text-center">18%</td>
                        <td className="px-4 py-2 text-center">9%</td>
                        <td className="px-4 py-2 text-center">10%</td>
                      </tr>
                      <tr className="border-b border-gray-800 bg-red-950/20">
                        <td className="px-4 py-2 font-semibold">Bear + High Vol</td>
                        <td className="px-4 py-2 text-center">18%</td>
                        <td className="px-4 py-2 text-center">18%</td>
                        <td className="px-4 py-2 text-center font-bold">36%</td>
                        <td className="px-4 py-2 text-center">18%</td>
                        <td className="px-4 py-2 text-center">10%</td>
                      </tr>
                      <tr className="border-b border-gray-800 bg-orange-950/20">
                        <td className="px-4 py-2 font-semibold">Bear + Normal Vol</td>
                        <td className="px-4 py-2 text-center">27%</td>
                        <td className="px-4 py-2 text-center">18%</td>
                        <td className="px-4 py-2 text-center">27%</td>
                        <td className="px-4 py-2 text-center">18%</td>
                        <td className="px-4 py-2 text-center">10%</td>
                      </tr>
                      <tr className="bg-gray-900/30">
                        <td className="px-4 py-2 font-semibold">Sideways (Any Vol)</td>
                        <td className="px-4 py-2 text-center">31%</td>
                        <td className="px-4 py-2 text-center">22%</td>
                        <td className="px-4 py-2 text-center">22%</td>
                        <td className="px-4 py-2 text-center">15%</td>
                        <td className="px-4 py-2 text-center">10%</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <TechnicalDeepDive title="Enabling Adaptive Weights">
                <div className="space-y-3">
                  <p className="text-sm">
                    By default, the system uses <strong>static weights (36/27/18/9/10)</strong>. To enable adaptive weights:
                  </p>
                  <CodeBlock
                    language="bash"
                    code={`# In .env file
ENABLE_ADAPTIVE_WEIGHTS=true`}
                  />
                  <p className="text-sm text-gray-400">
                    The system will then automatically detect the market regime every 6 hours and adjust weights accordingly.
                  </p>
                  <div className="mt-3">
                    <strong className="text-blue-300">API Endpoint to Check Current Regime:</strong>
                    <CodeBlock
                      language="bash"
                      code={`curl http://localhost:8010/market/regime`}
                    />
                  </div>
                  <div className="mt-3">
                    <strong className="text-blue-300">Implementation Files:</strong>
                    <ul className="list-disc list-inside text-xs text-gray-400 space-y-1 ml-2 mt-2">
                      <li><code>core/market_regime_service.py</code> - Market regime detection service</li>
                      <li><code>ml/regime_detector.py</code> - ML-based regime classification</li>
                      <li><code>core/stock_scorer.py</code> - Integrated adaptive weights support</li>
                    </ul>
                  </div>
                </div>
              </TechnicalDeepDive>
            </div>
          </section>

          {/* Backtesting Engine v2.0 */}
          <section id="backtesting" className="professional-card">
            <div className="flex items-start gap-3 mb-6">
              <BarChart3 className="w-6 h-6 text-emerald-400 flex-shrink-0 mt-1" />
              <div className="flex-1">
                <h2 className="text-2xl font-bold text-foreground mb-2">Backtesting Engine v2.0</h2>
                <p className="text-muted-foreground">
                  Historical simulation engine for validating the 5-agent strategy on past market data with comprehensive
                  risk-adjusted metrics.
                </p>
              </div>
            </div>

            <div className="space-y-6">
              <InfoBox type="warning">
                <strong>Data Limitations:</strong> The backtesting engine has known look-ahead bias in Fundamentals (current
                financial statements) and Sentiment (current analyst ratings) agents. Results may be optimistic by 5-10%.
                Use for relative performance comparison rather than absolute returns.
              </InfoBox>

              <div>
                <h3 className="text-lg font-semibold text-foreground mb-3 flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-emerald-400" />
                  V2.0 Improvements
                </h3>
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="bg-emerald-950/20 border border-emerald-500/30 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Database className="w-4 h-4 text-emerald-400" />
                      <strong className="text-emerald-300">EnhancedYahooProvider Integration</strong>
                    </div>
                    <p className="text-xs text-gray-400">
                      Uses same data provider as live system with 40+ technical indicators (vs 3 in v1.x)
                    </p>
                  </div>
                  <div className="bg-blue-950/20 border border-blue-500/30 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Settings className="w-4 h-4 text-blue-400" />
                      <strong className="text-blue-300">Live System Weight Alignment</strong>
                    </div>
                    <p className="text-xs text-gray-400">
                      Always uses production weights (36/27/18/9/10) - removed backtest_mode override
                    </p>
                  </div>
                  <div className="bg-yellow-950/20 border border-yellow-500/30 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <AlertTriangle className="w-4 h-4 text-yellow-400" />
                      <strong className="text-yellow-300">Transparent Bias Documentation</strong>
                    </div>
                    <p className="text-xs text-gray-400">
                      Clear warnings about look-ahead bias in fundamentals/sentiment data
                    </p>
                  </div>
                  <div className="bg-purple-950/20 border border-purple-500/30 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Shield className="w-4 h-4 text-purple-400" />
                      <strong className="text-purple-300">Comprehensive Testing</strong>
                    </div>
                    <p className="text-xs text-gray-400">
                      21 unit tests covering versioning, data accuracy, and weight consistency
                    </p>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-foreground mb-3">Risk-Adjusted Metrics</h3>
                <div className="grid md:grid-cols-2 gap-3">
                  <div className="bg-gray-900/50 border border-gray-700 rounded p-3">
                    <strong className="text-blue-300 text-sm">Sharpe Ratio</strong>
                    <p className="text-xs text-gray-400 mt-1">
                      Risk-adjusted return: (Return - Risk-free rate) / Volatility. Higher is better (&gt;1.0 is excellent).
                    </p>
                  </div>
                  <div className="bg-gray-900/50 border border-gray-700 rounded p-3">
                    <strong className="text-emerald-300 text-sm">Sortino Ratio</strong>
                    <p className="text-xs text-gray-400 mt-1">
                      Downside risk-adjusted return. Similar to Sharpe but only penalizes downside volatility.
                    </p>
                  </div>
                  <div className="bg-gray-900/50 border border-gray-700 rounded p-3">
                    <strong className="text-yellow-300 text-sm">Calmar Ratio</strong>
                    <p className="text-xs text-gray-400 mt-1">
                      CAGR / Max Drawdown. Measures return relative to worst loss period.
                    </p>
                  </div>
                  <div className="bg-gray-900/50 border border-gray-700 rounded p-3">
                    <strong className="text-purple-300 text-sm">Information Ratio</strong>
                    <p className="text-xs text-gray-400 mt-1">
                      (Portfolio Return - Benchmark Return) / Tracking Error. Measures consistency of outperformance.
                    </p>
                  </div>
                </div>
              </div>

              <TechnicalDeepDive title="Running a Backtest (Python)">
                <CodeBlock
                  language="Python"
                  code={`from datetime import datetime
from core.backtesting_engine import HistoricalBacktestEngine, BacktestConfig

# V2.0 Configuration
config = BacktestConfig(
    start_date='2020-01-01',
    end_date='2024-12-31',
    initial_capital=10000.0,
    rebalance_frequency='quarterly',  # or 'monthly'
    top_n_stocks=20,
    universe=['AAPL', 'MSFT', 'GOOGL', ...],  # Stock universe

    # V2.0 features
    engine_version="2.0",              # Default
    use_enhanced_provider=True,        # Use 40+ indicators (default)

    # Optional: Risk management
    enable_risk_management=True,       # Stop-losses, drawdown protection
    enable_regime_detection=True,      # Adaptive weights based on market
)

# Run backtest
engine = HistoricalBacktestEngine(config)
result = engine.run_backtest()

# Access results
print(f"Total Return: {result.total_return*100:.2f}%")
print(f"CAGR: {result.cagr*100:.2f}%")
print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
print(f"Max Drawdown: {result.max_drawdown*100:.2f}%")
print(f"vs SPY: {result.outperformance_vs_spy*100:+.2f}%")

# V2.0 metadata
print(f"Engine Version: {result.engine_version}")
print(f"Data Provider: {result.data_provider}")
print(f"Estimated Bias: {result.estimated_bias_impact}")`}
                />
                <div className="mt-3">
                  <strong className="text-blue-300">File Location:</strong>
                  <code className="block mt-1 text-xs bg-gray-800 p-2 rounded">
                    core/backtesting_engine.py
                  </code>
                </div>
              </TechnicalDeepDive>
            </div>
          </section>

          {/* API & Integration Guide */}
          <section id="api" className="professional-card">
            <div className="flex items-start gap-3 mb-6">
              <Plug className="w-6 h-6 text-blue-400 flex-shrink-0 mt-1" />
              <div className="flex-1">
                <h2 className="text-2xl font-bold text-foreground mb-2">API & Integration Guide</h2>
                <p className="text-muted-foreground">
                  FastAPI server on port 8010 with comprehensive endpoints for stock analysis, portfolio management,
                  and market regime detection.
                </p>
              </div>
            </div>

            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-foreground mb-3">Core Analysis Endpoints</h3>
                <div className="space-y-3">
                  <div className="bg-gray-900/50 border border-blue-500/30 rounded-lg p-4">
                    <div className="flex items-start gap-3 mb-2">
                      <code className="text-sm font-mono bg-blue-900/40 text-blue-300 px-2 py-1 rounded">POST</code>
                      <div className="flex-1">
                        <code className="text-sm text-blue-300">/analyze</code>
                        <p className="text-xs text-gray-400 mt-1">
                          Complete 5-agent analysis with narrative for single stock
                        </p>
                      </div>
                    </div>
                    <CodeBlock
                      language="bash"
                      code={`curl -X POST http://localhost:8010/analyze \\
  -H "Content-Type: application/json" \\
  -d '{"symbol": "AAPL"}'`}
                    />
                  </div>

                  <div className="bg-gray-900/50 border border-emerald-500/30 rounded-lg p-4">
                    <div className="flex items-start gap-3 mb-2">
                      <code className="text-sm font-mono bg-emerald-900/40 text-emerald-300 px-2 py-1 rounded">POST</code>
                      <div className="flex-1">
                        <code className="text-sm text-emerald-300">/analyze/batch</code>
                        <p className="text-xs text-gray-400 mt-1">
                          Batch analysis (max 50 symbols, processed in batches of 10)
                        </p>
                      </div>
                    </div>
                    <CodeBlock
                      language="bash"
                      code={`curl -X POST http://localhost:8010/analyze/batch \\
  -H "Content-Type: application/json" \\
  -d '{"symbols": ["AAPL", "MSFT", "GOOGL"]}'`}
                    />
                  </div>

                  <div className="bg-gray-900/50 border border-purple-500/30 rounded-lg p-4">
                    <div className="flex items-start gap-3 mb-2">
                      <code className="text-sm font-mono bg-purple-900/40 text-purple-300 px-2 py-1 rounded">GET</code>
                      <div className="flex-1">
                        <code className="text-sm text-purple-300">/market/regime</code>
                        <p className="text-xs text-gray-400 mt-1">
                          Get current market regime and adaptive weights (cached 6 hours)
                        </p>
                      </div>
                    </div>
                    <CodeBlock
                      language="bash"
                      code={`curl http://localhost:8010/market/regime`}
                    />
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-foreground mb-3">Portfolio Management Endpoints</h3>
                <div className="grid md:grid-cols-2 gap-3">
                  <div className="bg-gray-900/50 border border-gray-700 rounded p-3">
                    <code className="text-xs text-blue-300">POST /portfolio/analyze</code>
                    <p className="text-xs text-gray-400 mt-1">Portfolio optimization and risk analysis</p>
                  </div>
                  <div className="bg-gray-900/50 border border-gray-700 rounded p-3">
                    <code className="text-xs text-emerald-300">GET /portfolio/top-picks</code>
                    <p className="text-xs text-gray-400 mt-1">Top investment picks from US_TOP_100_STOCKS</p>
                  </div>
                  <div className="bg-gray-900/50 border border-gray-700 rounded p-3">
                    <code className="text-xs text-yellow-300">GET /portfolio/user</code>
                    <p className="text-xs text-gray-400 mt-1">Get user's portfolio with P&L</p>
                  </div>
                  <div className="bg-gray-900/50 border border-gray-700 rounded p-3">
                    <code className="text-xs text-purple-300">POST /portfolio/user/position</code>
                    <p className="text-xs text-gray-400 mt-1">Add/update position in user portfolio</p>
                  </div>
                </div>
              </div>

              <TechnicalDeepDive title="API Implementation Details">
                <div className="space-y-3">
                  <div>
                    <strong className="text-blue-300">Concurrent Processing:</strong>
                    <p className="text-xs text-gray-400 mt-1">
                      Batch endpoints process max 10 symbols concurrently to balance performance and API rate limits.
                    </p>
                  </div>
                  <div>
                    <strong className="text-blue-300">Caching Strategy:</strong>
                    <p className="text-xs text-gray-400 mt-1">
                      In-memory cache with TTL (15 minutes for analysis, 6 hours for market regime). Not persisted between restarts.
                    </p>
                  </div>
                  <div>
                    <strong className="text-blue-300">JSON Serialization:</strong>
                    <p className="text-xs text-gray-400 mt-1">
                      Custom NumpyEncoder handles numpy types (int64, float64, ndarray), checks for inf/nan values.
                    </p>
                  </div>
                  <div>
                    <strong className="text-blue-300">Documentation:</strong>
                    <p className="text-xs text-gray-400 mt-1">
                      Auto-generated Swagger UI at <code className="bg-gray-800 px-1 rounded">/docs</code> and ReDoc at <code className="bg-gray-800 px-1 rounded">/redoc</code>
                    </p>
                  </div>
                  <div>
                    <strong className="text-blue-300">File Location:</strong>
                    <code className="block mt-1 text-xs bg-gray-800 p-2 rounded">
                      api/main.py:FastAPIApplication
                    </code>
                  </div>
                </div>
              </TechnicalDeepDive>
            </div>
          </section>

          {/* Data Sources & Calculations */}
          <section id="data-sources" className="professional-card">
            <div className="flex items-start gap-3 mb-6">
              <Database className="w-6 h-6 text-yellow-400 flex-shrink-0 mt-1" />
              <div className="flex-1">
                <h2 className="text-2xl font-bold text-foreground mb-2">Data Sources & Calculations</h2>
                <p className="text-muted-foreground">
                  All market data is sourced from Yahoo Finance via yfinance library with extensive technical indicator
                  calculations using TA-Lib.
                </p>
              </div>
            </div>

            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-foreground mb-3 flex items-center gap-2">
                  <Database className="w-5 h-5 text-yellow-400" />
                  Stock Universe
                </h3>
                <InfoBox type="info">
                  The system operates on <strong>US_TOP_100_STOCKS</strong>: A curated list of 50 elite stocks from S&P 100,
                  balanced across 7 sectors (Technology, Healthcare, Finance, Consumer, Energy, Industrials, Communications).
                  Defined in <code>data/us_top_100_stocks.py</code>.
                </InfoBox>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-foreground mb-3">Technical Indicators (40+)</h3>
                <div className="grid md:grid-cols-3 gap-3">
                  <div className="bg-gray-900/50 border border-gray-700 rounded p-3">
                    <strong className="text-blue-300 text-sm">Momentum</strong>
                    <ul className="text-xs text-gray-400 mt-2 space-y-1">
                      <li>• RSI (14-day)</li>
                      <li>• MACD (12, 26, 9)</li>
                      <li>• Stochastic Oscillator</li>
                      <li>• ROC (Rate of Change)</li>
                    </ul>
                  </div>
                  <div className="bg-gray-900/50 border border-gray-700 rounded p-3">
                    <strong className="text-emerald-300 text-sm">Trend</strong>
                    <ul className="text-xs text-gray-400 mt-2 space-y-1">
                      <li>• SMA (20, 50, 200)</li>
                      <li>• EMA (12, 26)</li>
                      <li>• ADX (Trend Strength)</li>
                      <li>• Parabolic SAR</li>
                    </ul>
                  </div>
                  <div className="bg-gray-900/50 border border-gray-700 rounded p-3">
                    <strong className="text-purple-300 text-sm">Volatility</strong>
                    <ul className="text-xs text-gray-400 mt-2 space-y-1">
                      <li>• Bollinger Bands</li>
                      <li>• ATR (14-day)</li>
                      <li>• Historical Volatility</li>
                      <li>• Standard Deviation</li>
                    </ul>
                  </div>
                </div>
              </div>

              <TechnicalDeepDive title="EnhancedYahooProvider Implementation">
                <div className="space-y-3">
                  <p className="text-sm">
                    The <code>EnhancedYahooProvider</code> is the central data provider with intelligent caching and
                    comprehensive indicator calculations:
                  </p>
                  <div>
                    <strong className="text-blue-300">Key Features:</strong>
                    <ul className="list-disc list-inside text-xs text-gray-400 space-y-1 ml-2 mt-2">
                      <li>20-minute cache duration for 50-stock universe</li>
                      <li>Calculates 40+ technical indicators using TA-Lib</li>
                      <li>Handles numpy array serialization issues with sanitize_float() and sanitize_dict()</li>
                      <li>Provides comprehensive error handling and data validation</li>
                      <li>Supports both live and historical data fetching</li>
                    </ul>
                  </div>
                  <div className="mt-3">
                    <strong className="text-blue-300">File Location:</strong>
                    <code className="block mt-1 text-xs bg-gray-800 p-2 rounded">
                      data/enhanced_provider.py:EnhancedYahooProvider
                    </code>
                  </div>
                </div>
              </TechnicalDeepDive>
            </div>
          </section>

          {/* Limitations & Disclaimers */}
          <section id="limitations" className="professional-card">
            <div className="flex items-start gap-3 mb-6">
              <AlertTriangle className="w-6 h-6 text-red-400 flex-shrink-0 mt-1" />
              <div className="flex-1">
                <h2 className="text-2xl font-bold text-foreground mb-2">Limitations & Disclaimers</h2>
                <p className="text-muted-foreground">
                  Important limitations and considerations when using this system for investment decisions.
                </p>
              </div>
            </div>

            <div className="space-y-4">
              <InfoBox type="warning">
                <strong>🚨 NOT FINANCIAL ADVICE:</strong> This system is for educational and research purposes only.
                Always consult with a qualified financial advisor before making investment decisions.
              </InfoBox>

              <div className="bg-red-950/20 border border-red-500/30 rounded-lg p-4">
                <h3 className="text-red-300 font-semibold mb-2 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4" />
                  Backtesting Look-Ahead Bias
                </h3>
                <p className="text-sm text-gray-300 mb-2">
                  The backtesting engine has <strong>known look-ahead bias</strong> in two agents:
                </p>
                <ul className="list-disc list-inside text-sm text-gray-400 space-y-1 ml-2">
                  <li><strong>Fundamentals Agent:</strong> Uses CURRENT financial statements (not historical point-in-time data)</li>
                  <li><strong>Sentiment Agent:</strong> Uses CURRENT analyst ratings (not historical sentiment)</li>
                </ul>
                <p className="text-sm text-yellow-300 mt-2">
                  <strong>Impact:</strong> Results may be optimistic by 5-10%. Use for relative performance comparison, not absolute return predictions.
                </p>
              </div>

              <div className="bg-yellow-950/20 border border-yellow-500/30 rounded-lg p-4">
                <h3 className="text-yellow-300 font-semibold mb-2 flex items-center gap-2">
                  <Info className="w-4 h-4" />
                  Data Availability & Quality
                </h3>
                <ul className="list-disc list-inside text-sm text-gray-400 space-y-1">
                  <li>Market data from Yahoo Finance may have delays or inaccuracies</li>
                  <li>Some stocks may have incomplete financial statement data</li>
                  <li>Agent confidence scores reflect data quality and availability</li>
                  <li>Technical indicators require sufficient historical price data</li>
                </ul>
              </div>

              <div className="bg-blue-950/20 border border-blue-500/30 rounded-lg p-4">
                <h3 className="text-blue-300 font-semibold mb-2 flex items-center gap-2">
                  <Settings className="w-4 h-4" />
                  System Limitations
                </h3>
                <ul className="list-disc list-inside text-sm text-gray-400 space-y-1">
                  <li>Analysis limited to US stocks in the predefined universe (50 stocks)</li>
                  <li>LLM sentiment analysis requires API keys (optional, gracefully degrades)</li>
                  <li>Adaptive weights require enabling via environment variable</li>
                  <li>Cache is in-memory only (not persisted between server restarts)</li>
                  <li>Concurrent batch processing limited to 10 symbols to avoid rate limits</li>
                </ul>
              </div>

              <div className="bg-gray-900/50 border border-gray-700 rounded-lg p-4">
                <h3 className="text-gray-300 font-semibold mb-2">Recommended Best Practices</h3>
                <ul className="list-disc list-inside text-sm text-gray-400 space-y-1">
                  <li>✓ Use recommendations as one input among many in your decision-making process</li>
                  <li>✓ Pay attention to confidence scores - low confidence = less reliable recommendation</li>
                  <li>✓ Review the reasoning and metrics, not just the final score</li>
                  <li>✓ Compare current recommendations with historical backtests for validation</li>
                  <li>✓ Monitor market regime to understand which agents are most influential</li>
                  <li>✓ Diversify across multiple recommendations and risk levels</li>
                  <li>✗ Do not blindly follow STRONG BUY/SELL recommendations without your own research</li>
                  <li>✗ Do not use backtested returns as guaranteed future performance predictions</li>
                </ul>
              </div>
            </div>
          </section>

          {/* Footer */}
          <div className="text-center text-sm text-muted-foreground border-t border-border/50 pt-8">
            <p>
              AI Hedge Fund System v2.0 - Professional-grade investment analysis platform
            </p>
            <p className="mt-2">
              For API documentation, visit <code className="bg-gray-800 px-2 py-1 rounded">http://localhost:8010/docs</code>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemDetailsPage;
