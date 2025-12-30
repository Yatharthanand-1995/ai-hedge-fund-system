// API Response Types for AI Hedge Fund System

export interface AgentScores {
  fundamentals: number;
  momentum: number;
  quality: number;
  sentiment: number;
  institutional_flow: number;
}

export interface AgentNarratives {
  fundamentals: string;
  momentum: string;
  quality: string;
  sentiment: string;
  institutional_flow: string;
}

export interface MarketData {
  current_price: number;
  previous_close: number;
  price_change: number;
  price_change_percent: number;
  volume: number;
  market_cap: number;
}

export interface Narrative {
  symbol: string;
  timestamp: string;
  investment_thesis: string;
  key_strengths: string[];
  key_risks: string[];
  recommendation: 'STRONG BUY' | 'BUY' | 'WEAK BUY' | 'HOLD' | 'WEAK SELL' | 'SELL';
  confidence_level: 'HIGH' | 'MEDIUM' | 'LOW';
  agent_narratives: AgentNarratives;
  overall_score: number;
  agent_scores: AgentScores;
  // Additional fields that might be used by components
  executive_summary?: string;
  target_price?: number;
  upside_potential?: number;
  time_horizon?: string;
}

export interface StockAnalysis {
  symbol: string;
  agent_results: {
    fundamentals: AgentResult;
    momentum: AgentResult;
    quality: AgentResult;
    sentiment: AgentResult;
    institutional_flow: AgentResult;
  };
  narrative: Narrative;
  market_data: MarketData;
  timestamp: string;
  // Computed/convenience properties that match component expectations
  agent_scores?: AgentScores;
  company_name?: string;
  current_price?: number;
  price_change?: number;
  price_change_percent?: number;
  confidence_score?: number;
  agent_details?: Record<string, any>;
  recommendation?: RecommendationType;
  confidence_level?: ConfidenceLevel;
}

export interface AgentResult {
  score: number;
  confidence: number;
  metrics?: Record<string, any>;
  reasoning?: string;
}

export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  version: string;
  agents_status: {
    fundamentals: 'healthy' | 'degraded' | 'unhealthy';
    momentum: 'healthy' | 'degraded' | 'unhealthy';
    quality: 'healthy' | 'degraded' | 'unhealthy';
    sentiment: 'healthy' | 'degraded' | 'unhealthy';
    institutional_flow: 'healthy' | 'degraded' | 'unhealthy';
  };
}

export interface BatchAnalysisResponse {
  analyses: StockAnalysis[];
  total_processed: number;
  total_requested: number;
  cached_count: number;
  timestamp: string;
}

export interface PortfolioAnalysis {
  portfolio_analysis: {
    symbols: string[];
    weights: Record<string, number>;
    portfolio_score: number;
    number_of_positions: number;
    high_risk_positions: number;
    risk_level: 'High' | 'Moderate' | 'Low';
  };
  individual_analyses: StockAnalysis[];
  portfolio_recommendations: string[];
  timestamp: string;
}

export interface TopPick {
  symbol: string;
  company_name: string;
  sector: string;
  overall_score: number;
  weight: number;
  recommendation: string;
  confidence_level: string;
  investment_thesis: string;
  key_strengths: string[];
  key_risks: string[];
  market_data: MarketData;
  agent_scores: AgentScores;
}

export interface TopPicksResponse {
  top_picks: TopPick[];
  total_analyzed: number;
  selection_criteria: string;
  timestamp: string;
}

// Request Types
export interface AnalysisRequest {
  symbol: string;
}

export interface BatchAnalysisRequest {
  symbols: string[];
}

export interface PortfolioRequest {
  symbols: string[];
  weights?: number[];
}

// Error Types
export interface ApiError {
  detail: string;
  status_code?: number;
}

// Utility Types
export type RecommendationType = Narrative['recommendation'];
export type ConfidenceLevel = Narrative['confidence_level'];
export type AgentType = keyof AgentScores;

// Chart Data Types
export interface ChartDataPoint {
  name: string;
  value: number;
  color?: string;
}

export interface AgentScoreData {
  agent: AgentType;
  score: number;
  weight: number;
  weighted_score: number;
  confidence: number;
  color: string;
}

// UI State Types
export interface LoadingState {
  isLoading: boolean;
  error: string | null;
}

export interface SearchState {
  query: string;
  suggestions: string[];
  isSearching: boolean;
}

// Consensus Analysis Types
export interface AgentConsensusData {
  name: string;
  score: number;
  confidence: number;
  weight: number;
  accuracy: number;
  reasoning: string;
  status: 'healthy' | 'degraded' | 'unhealthy';
}

export interface ConsensusAnalysis {
  symbol: string;
  overallScore: number;
  consensus: 'strong' | 'moderate' | 'weak';
  agreement: number;
  conflictAreas: string[];
  topReason: string;
  agents: AgentConsensusData[];
}

export interface ConsensusResponse {
  consensus: ConsensusAnalysis[];
  timestamp: string;
}

// Backtest Types
export interface BacktestMetrics {
  sharpe_ratio: number;
  max_drawdown: number;
  volatility: number;
}

export interface EquityCurvePoint {
  date: string;
  value: number;
  return: number;
}

export interface RebalanceEvent {
  date: string;
  portfolio: string[];
  portfolio_value: number;
  avg_score: number;
}

export interface BacktestResult {
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
  metrics: BacktestMetrics;
  equity_curve: EquityCurvePoint[];
  rebalance_log: RebalanceEvent[];
}

export interface BacktestConfig {
  start_date: string;
  end_date: string;
  rebalance_frequency: 'monthly' | 'quarterly';
  top_n: number;
  universe: string[];
  initial_capital: number;
}

export interface BacktestResponse {
  results: BacktestResult;
  config: BacktestConfig;
  timestamp: string;
}

export interface BacktestHistoryResponse {
  results: BacktestResult[];
  total_count: number;
  timestamp: string;
}