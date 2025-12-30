import { useQuery, useMutation, useQueryClient, type UseQueryOptions, type UseMutationOptions } from '@tanstack/react-query';
import {
  apiService,
  queryKeys,
  queryOptions,
} from '../services/api';
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
  type BacktestHistoryResponse,
  type BacktestResponse,
  type BacktestConfig,
} from '../types/api';

// Health Check Hook
export const useHealthStatus = (options?: Partial<UseQueryOptions<HealthStatus, ApiError>>) => {
  return useQuery({
    queryKey: queryKeys.health,
    queryFn: apiService.getHealth,
    ...queryOptions.health,
    ...options,
  });
};

// Stock Analysis Hook
export const useStockAnalysis = (
  symbol: string | null,
  options?: Partial<UseQueryOptions<StockAnalysis, ApiError>>
) => {
  return useQuery({
    queryKey: symbol ? queryKeys.stockAnalysis(symbol) : [],
    queryFn: () => apiService.getStockAnalysis(symbol!),
    enabled: !!symbol,
    ...queryOptions.stockAnalysis,
    ...options,
  });
};

// Stock Analysis Mutation Hook
export const useAnalyzeStock = (
  options?: UseMutationOptions<StockAnalysis, ApiError, AnalysisRequest>
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: apiService.analyzeStock,
    onSuccess: (data, variables) => {
      // Update the cache with the new analysis
      queryClient.setQueryData(queryKeys.stockAnalysis(variables.symbol), data);

      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ['topPicks'] });
    },
    ...options,
  });
};

// Batch Analysis Mutation Hook
export const useBatchAnalysis = (
  options?: UseMutationOptions<BatchAnalysisResponse, ApiError, BatchAnalysisRequest>
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: apiService.analyzeBatch,
    onSuccess: (data, variables) => {
      // Cache individual stock analyses
      data.analyses.forEach((analysis) => {
        queryClient.setQueryData(queryKeys.stockAnalysis(analysis.symbol), analysis);
      });

      // Cache the batch result
      queryClient.setQueryData(queryKeys.batchAnalysis(variables.symbols), data);
    },
    ...options,
  });
};

// Portfolio Analysis Mutation Hook
export const usePortfolioAnalysis = (
  options?: UseMutationOptions<PortfolioAnalysis, ApiError, PortfolioRequest>
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: apiService.analyzePortfolio,
    onSuccess: (data, variables) => {
      // Cache individual analyses
      data.individual_analyses.forEach((analysis) => {
        queryClient.setQueryData(queryKeys.stockAnalysis(analysis.symbol), analysis);
      });

      // Cache the portfolio result
      queryClient.setQueryData(
        queryKeys.portfolioAnalysis(variables.symbols, variables.weights),
        data
      );
    },
    ...options,
  });
};

// Top Picks Hook
export const useTopPicks = (
  limit: number = 10,
  options?: Partial<UseQueryOptions<TopPicksResponse, ApiError>>
) => {
  return useQuery({
    queryKey: queryKeys.topPicks(limit),
    queryFn: () => apiService.getTopPicks(limit),
    ...queryOptions.topPicks,
    ...options,
  });
};

// Prefetch Hooks for Performance
export const usePrefetchStockAnalysis = () => {
  const queryClient = useQueryClient();

  return (symbol: string) => {
    queryClient.prefetchQuery({
      queryKey: queryKeys.stockAnalysis(symbol),
      queryFn: () => apiService.getStockAnalysis(symbol),
      ...queryOptions.stockAnalysis,
    });
  };
};

// Consensus Analysis Hook
export const useConsensus = (
  symbols: string[],
  options?: Partial<UseQueryOptions<ConsensusResponse, ApiError>>
) => {
  return useQuery({
    queryKey: queryKeys.consensus(symbols),
    queryFn: () => apiService.getConsensus(symbols),
    enabled: symbols.length > 0,
    ...queryOptions.consensus,
    ...options,
  });
};

// Backtest History Hook
export const useBacktestHistory = (
  options?: Partial<UseQueryOptions<BacktestHistoryResponse, ApiError>>
) => {
  return useQuery({
    queryKey: queryKeys.backtestHistory,
    queryFn: apiService.getBacktestHistory,
    ...queryOptions.backtestHistory,
    ...options,
  });
};

// Run Backtest Mutation Hook
export const useRunBacktest = (
  options?: UseMutationOptions<BacktestResponse, ApiError, BacktestConfig>
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: apiService.runBacktest,
    onSuccess: () => {
      // Invalidate backtest history to refetch updated list
      queryClient.invalidateQueries({ queryKey: queryKeys.backtestHistory });
    },
    ...options,
  });
};

// Cache Management Hooks
export const useInvalidateQueries = () => {
  const queryClient = useQueryClient();

  return {
    invalidateHealth: () => queryClient.invalidateQueries({ queryKey: queryKeys.health }),
    invalidateStockAnalysis: (symbol?: string) =>
      symbol
        ? queryClient.invalidateQueries({ queryKey: queryKeys.stockAnalysis(symbol) })
        : queryClient.invalidateQueries({ queryKey: ['stockAnalysis'] }),
    invalidateTopPicks: () => queryClient.invalidateQueries({ queryKey: ['topPicks'] }),
    invalidateConsensus: () => queryClient.invalidateQueries({ queryKey: ['consensus'] }),
    invalidateBacktestHistory: () => queryClient.invalidateQueries({ queryKey: queryKeys.backtestHistory }),
    invalidateAll: () => queryClient.invalidateQueries(),
    clearCache: () => queryClient.clear(),
  };
};

// Error Handling Hook
export const useApiError = () => {
  const formatError = (error: ApiError): string => {
    if (error.status_code === 404) {
      return 'Stock data not found. Please check the symbol and try again.';
    }
    if (error.status_code === 500) {
      return 'Analysis service temporarily unavailable. Please try again in a few moments.';
    }
    if (error.status_code === 429) {
      return 'Too many requests. Please wait a moment before trying again.';
    }
    return error.detail || 'An unexpected error occurred. Please try again.';
  };

  const isNetworkError = (error: ApiError): boolean => {
    return !error.status_code || error.detail.includes('Network Error');
  };

  return { formatError, isNetworkError };
};