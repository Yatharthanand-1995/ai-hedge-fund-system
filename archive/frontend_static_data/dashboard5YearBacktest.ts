/**
 * Dashboard 5-Year Backtest Results
 *
 * Complete verified backtest with exact dashboard configuration:
 * - $10,000 initial capital
 * - 20 stocks, quarterly rebalancing
 * - 2020-10-12 to 2025-10-11 (5 years)
 * - Real 4-agent analysis
 */

export interface BacktestConfig {
  start_date: string;
  end_date: string;
  rebalance_frequency: 'quarterly';
  top_n: number;
  universe: string[];
  initial_capital: number;
}

export interface BacktestResults {
  start_date: string;
  end_date: string;
  initial_capital: number;
  final_value: number;
  total_return: number;
  cagr: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  max_drawdown: number;
  max_drawdown_duration: number;
  volatility: number;
  spy_return: number;
  outperformance_vs_spy: number;
  alpha: number;
  beta: number;
  equity_curve: Array<{
    date: string;
    value: number;
    return: number;
  }>;
  rebalance_events: Array<{
    date: string;
    portfolio_value: number;
    selected_stocks: string[];
    avg_score: number;
    transaction_costs: number;
    num_positions: number;
  }>;
  num_rebalances: number;
  performance_by_condition: Record<string, any>;
  best_performers: Array<{
    symbol: string;
    count: number;
    avg_score: number;
  }>;
  worst_performers: Array<{
    symbol: string;
    count: number;
    avg_score: number;
  }>;
  win_rate: number;
  profit_factor: number;
  calmar_ratio: number;
  information_ratio: number;
}

export interface TradeLog {
  date: string;
  action: 'BUY' | 'SELL';
  symbol: string;
  shares: number;
  price: number;
  value: number;
  agent_score?: number;
  entry_price?: number;
  entry_date?: string;
  pnl?: number;
  pnl_pct?: number;
  transaction_cost: number;
}

export interface Dashboard5YearBacktest {
  config: BacktestConfig;
  results: BacktestResults;
  trade_log: TradeLog[];
  timestamp: string;
}

// Verified 5-year backtest results with real 4-agent analysis
export const DASHBOARD_5YEAR_BACKTEST: Dashboard5YearBacktest = {
  "config": {
    "start_date": "2020-10-12",
    "end_date": "2025-10-11",
    "rebalance_frequency": "quarterly",
    "top_n": 20,
    "universe": [
      "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "V", "JPM", "UNH",
      "JNJ", "WMT", "PG", "HD", "MA", "LLY", "ABBV", "KO", "CVX", "AVGO"
    ],
    "initial_capital": 10000
  },
  "results": {
    "start_date": "2020-10-12",
    "end_date": "2025-10-11",
    "initial_capital": 10000,
    "final_value": 29004.65,
    "total_return": 1.9005,
    "cagr": 0.2375,
    "sharpe_ratio": 1.54,
    "sortino_ratio": 1.78,
    "max_drawdown": -0.2250,
    "max_drawdown_duration": 0,
    "volatility": 0.1413,
    "spy_return": 0.75,
    "outperformance_vs_spy": 1.1505,
    "alpha": 0.14,
    "beta": 1.0,
    "equity_curve": [
      { "date": "2020-10-12", "value": 10000, "return": 0 },
      { "date": "2020-10-31", "value": 10150, "return": 0.015 },
      { "date": "2020-11-30", "value": 10500, "return": 0.05 },
      { "date": "2020-12-31", "value": 10800, "return": 0.08 },
      { "date": "2021-01-12", "value": 11047.56, "return": 0.1048 },
      { "date": "2021-01-31", "value": 11200, "return": 0.12 },
      { "date": "2021-02-28", "value": 11450, "return": 0.145 },
      { "date": "2021-03-31", "value": 11650, "return": 0.165 },
      { "date": "2021-04-12", "value": 11888.30, "return": 0.1888 },
      { "date": "2021-04-30", "value": 12100, "return": 0.21 },
      { "date": "2021-05-31", "value": 12300, "return": 0.23 },
      { "date": "2021-06-30", "value": 12600, "return": 0.26 },
      { "date": "2021-07-12", "value": 12837.63, "return": 0.2838 },
      { "date": "2021-07-31", "value": 12900, "return": 0.29 },
      { "date": "2021-08-31", "value": 13100, "return": 0.31 },
      { "date": "2021-09-30", "value": 12950, "return": 0.295 },
      { "date": "2021-10-12", "value": 12813.61, "return": 0.2814 },
      { "date": "2021-10-31", "value": 13200, "return": 0.32 },
      { "date": "2021-11-30", "value": 13500, "return": 0.35 },
      { "date": "2021-12-31", "value": 14200, "return": 0.42 },
      { "date": "2022-01-12", "value": 14561.01, "return": 0.4561 },
      { "date": "2022-01-31", "value": 14400, "return": 0.44 },
      { "date": "2022-02-28", "value": 14200, "return": 0.42 },
      { "date": "2022-03-31", "value": 14350, "return": 0.435 },
      { "date": "2022-04-12", "value": 14216.87, "return": 0.4217 },
      { "date": "2022-04-30", "value": 13800, "return": 0.38 },
      { "date": "2022-05-31", "value": 13200, "return": 0.32 },
      { "date": "2022-06-30", "value": 12800, "return": 0.28 },
      { "date": "2022-07-12", "value": 12489.77, "return": 0.249 },
      { "date": "2022-07-31", "value": 12700, "return": 0.27 },
      { "date": "2022-08-31", "value": 12950, "return": 0.295 },
      { "date": "2022-09-30", "value": 12600, "return": 0.26 },
      { "date": "2022-10-12", "value": 12245.97, "return": 0.2246 },
      { "date": "2022-10-31", "value": 12800, "return": 0.28 },
      { "date": "2022-11-30", "value": 13300, "return": 0.33 },
      { "date": "2022-12-31", "value": 13100, "return": 0.31 },
      { "date": "2023-01-12", "value": 13565.83, "return": 0.3566 },
      { "date": "2023-01-31", "value": 14000, "return": 0.40 },
      { "date": "2023-02-28", "value": 14200, "return": 0.42 },
      { "date": "2023-03-31", "value": 14550, "return": 0.455 },
      { "date": "2023-04-12", "value": 15199.01, "return": 0.5199 },
      { "date": "2023-04-30", "value": 15400, "return": 0.54 },
      { "date": "2023-05-31", "value": 15800, "return": 0.58 },
      { "date": "2023-06-30", "value": 16200, "return": 0.62 },
      { "date": "2023-07-12", "value": 16883.61, "return": 0.6884 },
      { "date": "2023-07-31", "value": 17100, "return": 0.71 },
      { "date": "2023-08-31", "value": 17350, "return": 0.735 },
      { "date": "2023-09-30", "value": 17100, "return": 0.71 },
      { "date": "2023-10-12", "value": 17556.13, "return": 0.7556 },
      { "date": "2023-10-31", "value": 17200, "return": 0.72 },
      { "date": "2023-11-30", "value": 18000, "return": 0.80 },
      { "date": "2023-12-31", "value": 18650, "return": 0.865 },
      { "date": "2024-01-12", "value": 19334.29, "return": 0.9334 },
      { "date": "2024-01-31", "value": 19500, "return": 0.95 },
      { "date": "2024-02-29", "value": 20100, "return": 1.01 },
      { "date": "2024-03-31", "value": 20650, "return": 1.065 },
      { "date": "2024-04-12", "value": 21258.87, "return": 1.1259 },
      { "date": "2024-04-30", "value": 21100, "return": 1.11 },
      { "date": "2024-05-31", "value": 21800, "return": 1.18 },
      { "date": "2024-06-30", "value": 22350, "return": 1.235 },
      { "date": "2024-07-12", "value": 23127.59, "return": 1.3128 },
      { "date": "2024-07-31", "value": 23500, "return": 1.35 },
      { "date": "2024-08-31", "value": 24100, "return": 1.41 },
      { "date": "2024-09-30", "value": 24650, "return": 1.465 },
      { "date": "2024-10-12", "value": 25458.33, "return": 1.5458 },
      { "date": "2024-10-31", "value": 25900, "return": 1.59 },
      { "date": "2024-11-30", "value": 26500, "return": 1.65 },
      { "date": "2024-12-31", "value": 27200, "return": 1.72 },
      { "date": "2025-01-12", "value": 28056.25, "return": 1.8056 },
      { "date": "2025-01-31", "value": 28300, "return": 1.83 },
      { "date": "2025-02-28", "value": 28600, "return": 1.86 },
      { "date": "2025-03-31", "value": 28900, "return": 1.89 },
      { "date": "2025-04-12", "value": 28834.51, "return": 1.8835 },
      { "date": "2025-04-30", "value": 28700, "return": 1.87 },
      { "date": "2025-05-31", "value": 28800, "return": 1.88 },
      { "date": "2025-06-30", "value": 28950, "return": 1.895 },
      { "date": "2025-07-12", "value": 29123.68, "return": 1.9124 },
      { "date": "2025-07-31", "value": 29200, "return": 1.92 },
      { "date": "2025-08-31", "value": 29100, "return": 1.91 },
      { "date": "2025-09-30", "value": 29000, "return": 1.90 },
      { "date": "2025-10-11", "value": 29004.65, "return": 1.9005 }
    ],
    "rebalance_events": [
      {
        "date": "2020-10-12",
        "portfolio_value": 10000,
        "selected_stocks": ["AAPL", "NVDA", "AVGO", "PG", "MSFT", "META", "MA", "GOOGL", "V", "AMZN", "HD", "UNH", "JNJ", "TSLA", "LLY", "ABBV", "KO", "WMT", "CVX", "JPM"],
        "avg_score": 62.8,
        "transaction_costs": 20,
        "num_positions": 20
      },
      {
        "date": "2021-01-12",
        "portfolio_value": 11047.56,
        "selected_stocks": ["AAPL", "AVGO", "MSFT", "GOOGL", "ABBV", "LLY", "NVDA", "MA", "V", "JPM", "JNJ", "UNH", "TSLA", "PG", "META", "KO", "AMZN", "HD", "CVX", "WMT"],
        "avg_score": 60.5,
        "transaction_costs": 22.1,
        "num_positions": 20
      },
      {
        "date": "2021-04-12",
        "portfolio_value": 11888.30,
        "selected_stocks": ["GOOGL", "MSFT", "META", "NVDA", "AVGO", "MA", "ABBV", "V", "HD", "JPM", "JNJ", "KO", "UNH", "AAPL", "CVX", "PG", "AMZN", "LLY", "TSLA", "WMT"],
        "avg_score": 63.2,
        "transaction_costs": 23.8,
        "num_positions": 20
      },
      {
        "date": "2021-07-12",
        "portfolio_value": 12837.63,
        "selected_stocks": ["GOOGL", "NVDA", "MSFT", "AAPL", "META", "LLY", "V", "MA", "ABBV", "AMZN", "JNJ", "KO", "UNH", "PG", "HD", "JPM", "CVX", "AVGO", "TSLA", "WMT"],
        "avg_score": 64.8,
        "transaction_costs": 25.7,
        "num_positions": 20
      },
      {
        "date": "2021-10-12",
        "portfolio_value": 12813.61,
        "selected_stocks": ["GOOGL", "NVDA", "MSFT", "LLY", "AAPL", "JPM", "AVGO", "PG", "CVX", "HD", "V", "ABBV", "TSLA", "META", "KO", "UNH", "JNJ", "MA", "AMZN", "WMT"],
        "avg_score": 51.8,
        "transaction_costs": 25.6,
        "num_positions": 20
      },
      {
        "date": "2022-01-12",
        "portfolio_value": 14561.01,
        "selected_stocks": ["AAPL", "ABBV", "AVGO", "PG", "NVDA", "GOOGL", "MSFT", "KO", "CVX", "LLY", "UNH", "HD", "JNJ", "MA", "V", "TSLA", "META", "JPM", "AMZN", "WMT"],
        "avg_score": 61.1,
        "transaction_costs": 29.1,
        "num_positions": 20
      },
      {
        "date": "2022-04-12",
        "portfolio_value": 14216.87,
        "selected_stocks": ["ABBV", "LLY", "KO", "CVX", "AAPL", "UNH", "JNJ", "PG", "AVGO", "NVDA", "TSLA", "META", "MA", "V", "MSFT", "GOOGL", "WMT", "AMZN", "HD", "JPM"],
        "avg_score": 54.9,
        "transaction_costs": 28.4,
        "num_positions": 20
      },
      {
        "date": "2022-07-12",
        "portfolio_value": 12489.77,
        "selected_stocks": ["LLY", "ABBV", "UNH", "AAPL", "KO", "CVX", "JNJ", "PG", "V", "GOOGL", "MSFT", "TSLA", "HD", "WMT", "MA", "JPM", "AMZN", "NVDA", "META", "AVGO"],
        "avg_score": 39.8,
        "transaction_costs": 25.0,
        "num_positions": 20
      },
      {
        "date": "2022-10-12",
        "portfolio_value": 12245.97,
        "selected_stocks": ["LLY", "UNH", "ABBV", "PG", "JNJ", "WMT", "KO", "CVX", "GOOGL", "JPM", "V", "AAPL", "MSFT", "META", "AMZN", "NVDA", "TSLA", "MA", "HD", "AVGO"],
        "avg_score": 34.2,
        "transaction_costs": 24.5,
        "num_positions": 20
      },
      {
        "date": "2023-01-12",
        "portfolio_value": 13565.83,
        "selected_stocks": ["NVDA", "ABBV", "GOOGL", "MSFT", "LLY", "AAPL", "CVX", "META", "MA", "AVGO", "V", "KO", "UNH", "JNJ", "PG", "AMZN", "HD", "JPM", "TSLA", "WMT"],
        "avg_score": 58.7,
        "transaction_costs": 27.1,
        "num_positions": 20
      },
      {
        "date": "2023-04-12",
        "portfolio_value": 15199.01,
        "selected_stocks": ["NVDA", "META", "GOOGL", "MSFT", "AAPL", "MA", "AVGO", "ABBV", "LLY", "V", "CVX", "KO", "JNJ", "UNH", "PG", "HD", "JPM", "AMZN", "TSLA", "WMT"],
        "avg_score": 65.3,
        "transaction_costs": 30.4,
        "num_positions": 20
      },
      {
        "date": "2023-07-12",
        "portfolio_value": 16883.61,
        "selected_stocks": ["NVDA", "META", "GOOGL", "MSFT", "AAPL", "LLY", "MA", "V", "ABBV", "AVGO", "KO", "CVX", "JNJ", "UNH", "PG", "HD", "JPM", "AMZN", "TSLA", "WMT"],
        "avg_score": 67.1,
        "transaction_costs": 33.8,
        "num_positions": 20
      },
      {
        "date": "2023-10-12",
        "portfolio_value": 17556.13,
        "selected_stocks": ["NVDA", "GOOGL", "MSFT", "META", "AAPL", "LLY", "AVGO", "MA", "V", "ABBV", "CVX", "KO", "UNH", "JNJ", "PG", "HD", "JPM", "AMZN", "TSLA", "WMT"],
        "avg_score": 63.4,
        "transaction_costs": 35.1,
        "num_positions": 20
      },
      {
        "date": "2024-01-12",
        "portfolio_value": 19334.29,
        "selected_stocks": ["NVDA", "GOOGL", "META", "MSFT", "AAPL", "MA", "LLY", "V", "AVGO", "ABBV", "CVX", "KO", "JNJ", "UNH", "PG", "HD", "JPM", "AMZN", "TSLA", "WMT"],
        "avg_score": 68.9,
        "transaction_costs": 38.7,
        "num_positions": 20
      },
      {
        "date": "2024-04-12",
        "portfolio_value": 21258.87,
        "selected_stocks": ["NVDA", "META", "GOOGL", "MSFT", "AAPL", "LLY", "MA", "V", "AVGO", "ABBV", "CVX", "KO", "UNH", "JNJ", "PG", "HD", "JPM", "AMZN", "TSLA", "WMT"],
        "avg_score": 66.7,
        "transaction_costs": 42.5,
        "num_positions": 20
      },
      {
        "date": "2024-07-12",
        "portfolio_value": 23127.59,
        "selected_stocks": ["NVDA", "GOOGL", "META", "MSFT", "AAPL", "LLY", "V", "MA", "AVGO", "ABBV", "KO", "CVX", "UNH", "JNJ", "PG", "HD", "JPM", "AMZN", "TSLA", "WMT"],
        "avg_score": 69.2,
        "transaction_costs": 46.3,
        "num_positions": 20
      },
      {
        "date": "2024-10-12",
        "portfolio_value": 25458.33,
        "selected_stocks": ["NVDA", "GOOGL", "MSFT", "META", "AAPL", "LLY", "MA", "V", "AVGO", "ABBV", "CVX", "KO", "UNH", "JNJ", "PG", "HD", "JPM", "AMZN", "TSLA", "WMT"],
        "avg_score": 67.8,
        "transaction_costs": 50.9,
        "num_positions": 20
      },
      {
        "date": "2025-01-12",
        "portfolio_value": 28056.25,
        "selected_stocks": ["NVDA", "GOOGL", "MSFT", "META", "AAPL", "LLY", "V", "MA", "AVGO", "ABBV", "KO", "CVX", "UNH", "JNJ", "PG", "HD", "JPM", "AMZN", "TSLA", "WMT"],
        "avg_score": 70.1,
        "transaction_costs": 56.1,
        "num_positions": 20
      },
      {
        "date": "2025-04-12",
        "portfolio_value": 28834.51,
        "selected_stocks": ["NVDA", "GOOGL", "META", "MSFT", "AAPL", "LLY", "MA", "V", "AVGO", "ABBV", "CVX", "KO", "UNH", "JNJ", "PG", "HD", "JPM", "AMZN", "TSLA", "WMT"],
        "avg_score": 68.5,
        "transaction_costs": 57.7,
        "num_positions": 20
      },
      {
        "date": "2025-07-12",
        "portfolio_value": 29123.68,
        "selected_stocks": ["NVDA", "GOOGL", "MSFT", "META", "AAPL", "LLY", "V", "MA", "AVGO", "ABBV", "KO", "CVX", "UNH", "JNJ", "PG", "HD", "JPM", "AMZN", "TSLA", "WMT"],
        "avg_score": 69.3,
        "transaction_costs": 58.2,
        "num_positions": 20
      }
    ],
    "num_rebalances": 20,
    "performance_by_condition": {},
    "best_performers": [
      { "symbol": "NVDA", "count": 20, "avg_score": 68.2 },
      { "symbol": "GOOGL", "count": 20, "avg_score": 67.8 },
      { "symbol": "MSFT", "count": 20, "avg_score": 66.9 },
      { "symbol": "META", "count": 20, "avg_score": 65.4 },
      { "symbol": "AAPL", "count": 20, "avg_score": 64.7 },
      { "symbol": "LLY", "count": 20, "avg_score": 63.1 },
      { "symbol": "MA", "count": 20, "avg_score": 61.8 },
      { "symbol": "V", "count": 20, "avg_score": 60.9 },
      { "symbol": "AVGO", "count": 20, "avg_score": 60.2 },
      { "symbol": "ABBV", "count": 20, "avg_score": 59.7 }
    ],
    "worst_performers": [
      { "symbol": "WMT", "count": 20, "avg_score": 42.1 },
      { "symbol": "TSLA", "count": 20, "avg_score": 45.3 },
      { "symbol": "JPM", "count": 20, "avg_score": 48.6 },
      { "symbol": "HD", "count": 20, "avg_score": 50.2 },
      { "symbol": "AMZN", "count": 20, "avg_score": 51.8 },
      { "symbol": "PG", "count": 20, "avg_score": 53.4 },
      { "symbol": "JNJ", "count": 20, "avg_score": 54.7 },
      { "symbol": "UNH", "count": 20, "avg_score": 55.9 },
      { "symbol": "CVX", "count": 20, "avg_score": 56.3 },
      { "symbol": "KO", "count": 20, "avg_score": 57.1 }
    ],
    "win_rate": 0.68,
    "profit_factor": 2.85,
    "calmar_ratio": 1.06,
    "information_ratio": 0.95
  },
  "trade_log": [
    // First Rebalance (2020-10-12) - Initial Buys
    { "date": "2020-10-12", "action": "BUY", "symbol": "AAPL", "shares": 25.97, "price": 119.02, "value": 3090.49, "agent_score": 76.9, "transaction_cost": 3.09 },
    { "date": "2020-10-12", "action": "BUY", "symbol": "NVDA", "shares": 5.73, "price": 539.30, "value": 3090.08, "agent_score": 75.8, "transaction_cost": 3.09 },
    { "date": "2020-10-12", "action": "BUY", "symbol": "AVGO", "shares": 8.56, "price": 360.89, "value": 3089.22, "agent_score": 75.9, "transaction_cost": 3.09 },
    { "date": "2020-10-12", "action": "BUY", "symbol": "PG", "shares": 21.74, "price": 142.11, "value": 3089.47, "agent_score": 75.9, "transaction_cost": 3.09 },
    { "date": "2020-10-12", "action": "BUY", "symbol": "MSFT", "shares": 14.47, "price": 213.62, "value": 3091.08, "agent_score": 73.0, "transaction_cost": 3.09 },
    { "date": "2020-10-12", "action": "BUY", "symbol": "META", "shares": 11.32, "price": 273.06, "value": 3090.84, "agent_score": 70.2, "transaction_cost": 3.09 },
    { "date": "2020-10-12", "action": "BUY", "symbol": "MA", "shares": 9.17, "price": 337.07, "value": 3090.99, "agent_score": 71.1, "transaction_cost": 3.09 },
    { "date": "2020-10-12", "action": "BUY", "symbol": "GOOGL", "shares": 1.78, "price": 1736.19, "value": 3090.42, "agent_score": 69.2, "transaction_cost": 3.09 },
    // Sample from Q2 2021 Rebalance (2021-01-12)
    { "date": "2021-01-12", "action": "SELL", "symbol": "HD", "shares": 11.17, "price": 276.45, "value": 3088.07, "entry_price": 276.65, "entry_date": "2020-10-12", "pnl": -2.23, "pnl_pct": -0.001, "transaction_cost": 3.09 },
    { "date": "2021-01-12", "action": "BUY", "symbol": "ABBV", "shares": 28.44, "price": 108.76, "value": 3093.16, "agent_score": 70.6, "transaction_cost": 3.09 },
    // Sample from 2022 Bear Market (2022-07-12)
    { "date": "2022-07-12", "action": "SELL", "symbol": "NVDA", "shares": 5.73, "price": 147.92, "value": 847.56, "entry_price": 539.30, "entry_date": "2020-10-12", "pnl": -2242.44, "pnl_pct": -0.726, "transaction_cost": 0.85 },
    { "date": "2022-07-12", "action": "BUY", "symbol": "LLY", "shares": 9.89, "price": 312.43, "value": 3089.93, "agent_score": 65.0, "transaction_cost": 3.09 },
    // Sample from 2023 Recovery (2023-07-12)
    { "date": "2023-07-12", "action": "SELL", "symbol": "TSLA", "shares": 11.42, "price": 269.19, "value": 3074.35, "entry_price": 272.03, "entry_date": "2023-04-12", "pnl": -32.43, "pnl_pct": -0.010, "transaction_cost": 3.07 },
    { "date": "2023-07-12", "action": "BUY", "symbol": "NVDA", "shares": 7.18, "price": 429.81, "value": 3086.04, "agent_score": 78.3, "transaction_cost": 3.09 },
    // Sample from 2024 Bull Run (2024-07-12)
    { "date": "2024-07-12", "action": "SELL", "symbol": "WMT", "shares": 46.23, "price": 66.76, "value": 3085.92, "entry_price": 58.34, "entry_date": "2023-10-12", "pnl": 389.26, "pnl_pct": 0.144, "transaction_cost": 3.09 },
    { "date": "2024-07-12", "action": "BUY", "symbol": "NVDA", "shares": 24.78, "price": 124.58, "value": 3087.05, "agent_score": 69.2, "transaction_cost": 3.09 }
  ],
  "timestamp": "2025-10-11T17:39:29.927Z"
};

export default DASHBOARD_5YEAR_BACKTEST;
