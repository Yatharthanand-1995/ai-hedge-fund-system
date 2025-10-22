"""
Extract backtest data from JSON files and create TypeScript static data file for frontend
"""
import json
from pathlib import Path

# Read all backtest result files
backtest_dir = Path("data/backtest_results/results")
backtest_files = list(backtest_dir.glob("*.json"))

# Read index to get metadata
with open("data/backtest_results/index.json", "r") as f:
    index = json.load(f)

# Extract data from each backtest
static_data = []

for entry in index:
    backtest_id = entry["backtest_id"]
    result_file = backtest_dir / f"{backtest_id}.json"

    if not result_file.exists():
        print(f"Warning: {result_file} not found, skipping")
        continue

    with open(result_file, "r") as f:
        full_data = json.load(f)

    # Extract the data we need for frontend
    results = full_data["results"]

    # Extract spy_return and benchmark_return
    spy_return = results.get("spy_return", [0])[0] if isinstance(results.get("spy_return"), list) else results.get("spy_return", 0)
    benchmark_return = results.get("benchmark_return", [0])[0] if isinstance(results.get("benchmark_return"), list) else results.get("benchmark_return", spy_return)
    outperformance_vs_spy = results.get("outperformance_vs_spy", [0])[0] if isinstance(results.get("outperformance_vs_spy"), list) else results.get("outperformance_vs_spy", 0)
    outperformance_vs_benchmark = results.get("outperformance_vs_benchmark", [0])[0] if isinstance(results.get("outperformance_vs_benchmark"), list) else results.get("outperformance_vs_benchmark", outperformance_vs_spy)

    backtest_summary = {
        "backtest_id": backtest_id,
        "start_date": results["start_date"],
        "end_date": results["end_date"],
        "initial_capital": results["initial_capital"],
        "final_value": results["final_value"],
        "total_return": results["total_return"],
        "benchmark_return": benchmark_return,
        "spy_return": spy_return,
        "outperformance_vs_benchmark": outperformance_vs_benchmark,
        "outperformance_vs_spy": outperformance_vs_spy,
        "rebalances": int(results.get("rebalances", 0)),
        "metrics": {
            "sharpe_ratio": results["metrics"]["sharpe_ratio"],
            "max_drawdown": results["metrics"]["max_drawdown"],
            "volatility": results["metrics"]["volatility"]
        },
        "equity_curve": results["equity_curve"],
        "rebalance_log": full_data.get("rebalance_log", [])
    }

    static_data.append(backtest_summary)
    print(f"✅ Extracted {backtest_id}: {results['start_date']} to {results['end_date']}")

# Sort by start_date (most recent first)
static_data.sort(key=lambda x: x["start_date"], reverse=True)

# Write TypeScript file
ts_content = f"""/**
 * Static Backtest Data
 *
 * This file contains pre-loaded backtest results from the 4-agent analysis system.
 * Data is extracted from data/backtest_results/ JSON files.
 *
 * Generated: {Path(__file__).name}
 * Total backtests: {len(static_data)}
 */

export interface BacktestMetrics {{
  sharpe_ratio: number;
  max_drawdown: number;
  volatility: number;
}}

export interface EquityPoint {{
  date: string;
  value: number;
  return: number;
}}

export interface RebalanceEntry {{
  date: string;
  portfolio: string[];
  portfolio_value?: number;
  avg_score?: number;
}}

export interface BacktestResult {{
  backtest_id: string;
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
  equity_curve: EquityPoint[];
  rebalance_log: RebalanceEntry[];
}}

export const STATIC_BACKTEST_DATA: BacktestResult[] = {json.dumps(static_data, indent=2)};

export default STATIC_BACKTEST_DATA;
"""

# Write to frontend src directory
output_file = Path(__file__).parent / "frontend" / "src" / "data" / "staticBacktestData.ts"
output_file.parent.mkdir(parents=True, exist_ok=True)

with open(output_file, "w") as f:
    f.write(ts_content)

print(f"\n✅ Created {output_file}")
print(f"✅ Total backtests: {len(static_data)}")
print(f"\nBacktest Summary:")
for bt in static_data:
    print(f"  • {bt['start_date']} to {bt['end_date']}: {bt['total_return']*100:+.2f}% (Sharpe: {bt['metrics']['sharpe_ratio']:.2f})")
