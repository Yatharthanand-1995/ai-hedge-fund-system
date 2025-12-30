import axios, { type AxiosResponse } from 'axios';
import {
  type StockAnalysis,
  type HealthStatus,
  type BatchAnalysisResponse,
  type PortfolioAnalysis,
  type TopPicksResponse,
  type AnalysisRequest,
  type BatchAnalysisRequest,
  type PortfolioRequest,
  type ApiError,
  type ConsensusResponse,
  type BacktestResponse,
  type BacktestHistoryResponse,
  type BacktestConfig,
} from '../types/api';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8010';

// Create axios instance with default config
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds for analysis requests
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const apiError: ApiError = {
      detail: error.response?.data?.detail || error.message || 'An unknown error occurred',
      status_code: error.response?.status,
    };
    return Promise.reject(apiError);
  }
);

// API Service Functions
export const apiService = {
  // Health Check
  async getHealth(): Promise<HealthStatus> {
    const response: AxiosResponse<HealthStatus> = await apiClient.get('/health');
    return response.data;
  },

  // Single Stock Analysis
  async analyzeStock(request: AnalysisRequest): Promise<StockAnalysis> {
    const response: AxiosResponse<StockAnalysis> = await apiClient.post('/analyze', request);
    return response.data;
  },

  // Quick Stock Analysis (GET)
  async getStockAnalysis(symbol: string): Promise<StockAnalysis> {
    const response: AxiosResponse<StockAnalysis> = await apiClient.get(`/analyze/${symbol}`);
    return response.data;
  },

  // Batch Stock Analysis
  async analyzeBatch(request: BatchAnalysisRequest): Promise<BatchAnalysisResponse> {
    const response: AxiosResponse<BatchAnalysisResponse> = await apiClient.post('/analyze/batch', request);
    return response.data;
  },

  // Portfolio Analysis
  async analyzePortfolio(request: PortfolioRequest): Promise<PortfolioAnalysis> {
    const response: AxiosResponse<PortfolioAnalysis> = await apiClient.post('/portfolio/analyze', request);
    return response.data;
  },

  // Top Investment Picks
  async getTopPicks(limit: number = 10): Promise<TopPicksResponse> {
    const response: AxiosResponse<TopPicksResponse> = await apiClient.get(`/portfolio/top-picks?limit=${limit}`);
    return response.data;
  },

  // Consensus Analysis
  async getConsensus(symbols: string[]): Promise<ConsensusResponse> {
    const symbolsParam = symbols.join(',');
    const response: AxiosResponse<ConsensusResponse> = await apiClient.get(`/analyze/consensus?symbols=${symbolsParam}`);
    return response.data;
  },

  // Backtest History
  async getBacktestHistory(): Promise<BacktestHistoryResponse> {
    const response: AxiosResponse<BacktestHistoryResponse> = await apiClient.get('/backtest/history');
    return response.data;
  },

  // Run Backtest
  async runBacktest(config: BacktestConfig): Promise<BacktestResponse> {
    const response: AxiosResponse<BacktestResponse> = await apiClient.post('/backtest/run', config, {
      timeout: 60000, // 60 seconds for backtests
    });
    return response.data;
  },
};

// Query Keys for React Query
export const queryKeys = {
  health: ['health'] as const,
  stockAnalysis: (symbol: string) => ['stockAnalysis', symbol] as const,
  batchAnalysis: (symbols: string[]) => ['batchAnalysis', symbols.sort().join(',')] as const,
  portfolioAnalysis: (symbols: string[], weights?: number[]) =>
    ['portfolioAnalysis', symbols.sort().join(','), weights?.join(',') || ''] as const,
  topPicks: (limit: number) => ['topPicks', limit] as const,
  consensus: (symbols: string[]) => ['consensus', symbols.sort().join(',')] as const,
  backtestHistory: ['backtestHistory'] as const,
};

// Default query options
export const defaultQueryOptions = {
  staleTime: 5 * 60 * 1000, // 5 minutes
  cacheTime: 15 * 60 * 1000, // 15 minutes (matching API cache TTL)
  retry: 2,
  retryDelay: (attemptIndex: number) => Math.min(1000 * 2 ** attemptIndex, 30000),
};

// Specific query options for different endpoints
export const queryOptions = {
  health: {
    ...defaultQueryOptions,
    staleTime: 30 * 1000, // 30 seconds for health checks
    refetchInterval: 60 * 1000, // Refetch every minute
  },
  stockAnalysis: {
    ...defaultQueryOptions,
    staleTime: 15 * 60 * 1000, // 15 minutes (matching API cache)
  },
  topPicks: {
    ...defaultQueryOptions,
    staleTime: 10 * 60 * 1000, // 10 minutes
  },
  consensus: {
    ...defaultQueryOptions,
    staleTime: 10 * 60 * 1000, // 10 minutes
  },
  backtestHistory: {
    ...defaultQueryOptions,
    staleTime: 5 * 60 * 1000, // 5 minutes
  },
};