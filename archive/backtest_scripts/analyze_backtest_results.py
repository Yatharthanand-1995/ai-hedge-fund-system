"""
Comprehensive Backtest Analysis
Compares baseline (Phase 1) vs enhanced (Phases 2+3) results
"""

import json
import re
from datetime import datetime
from typing import Dict, List

def parse_log_file(log_path: str) -> Dict:
    """Extract key metrics from log file"""

    with open(log_path, 'r') as f:
        log_content = f.read()

    results = {
        'rebalance_events': [],
        'regime_transitions': [],
        'risk_events': [],
        'performance': {}
    }

    # Extract rebalance events
    rebalance_pattern = r'Rebalancing portfolio on (\d{4}-\d{2}-\d{2})'
    value_pattern = r'Rebalanced: (\d+) sells, (\d+) buys, value: \$([0-9,]+\.\d{2})'

    rebalance_dates = re.findall(rebalance_pattern, log_content)
    rebalance_values = re.findall(value_pattern, log_content)

    for i, (date, (sells, buys, value)) in enumerate(zip(rebalance_dates, rebalance_values)):
        results['rebalance_events'].append({
            'date': date,
            'sells': int(sells),
            'buys': int(buys),
            'value': float(value.replace(',', ''))
        })

    # Extract regime transitions
    regime_pattern = r'📊 Market Regime: ([A-Z]+) / ([A-Z]+) / ([A-Z]+)'
    regime_date_pattern = r'(\d{4}-\d{2}-\d{2}).*?📊 Market Regime: ([A-Z]+) / ([A-Z]+) / ([A-Z]+)'

    regime_matches = re.findall(regime_date_pattern, log_content)
    for match in regime_matches:
        date, trend, volatility, condition = match
        results['regime_transitions'].append({
            'date': date,
            'trend': trend,
            'volatility': volatility,
            'condition': condition
        })

    # Extract risk events
    stop_loss_pattern = r'🛑 Stop-loss triggered for ([A-Z]+): ([+-]?\d+\.\d+)% loss'
    stop_losses = re.findall(stop_loss_pattern, log_content)

    for symbol, loss_pct in stop_losses:
        results['risk_events'].append({
            'type': 'STOP_LOSS',
            'symbol': symbol,
            'loss_pct': float(loss_pct)
        })

    # Extract final performance
    final_value_pattern = r'Final Value:\s+\$([0-9,]+\.\d{2})'
    total_return_pattern = r'Total Return:\s+([+-]?\d+\.\d{2})%'
    cagr_pattern = r'CAGR:\s+([+-]?\d+\.\d{2})%'
    sharpe_pattern = r'Sharpe Ratio:\s+(\d+\.\d{2})'
    max_dd_pattern = r'Max Drawdown:\s+([+-]?\d+\.\d{2})%'

    final_value = re.search(final_value_pattern, log_content)
    total_return = re.search(total_return_pattern, log_content)
    cagr = re.search(cagr_pattern, log_content)
    sharpe = re.search(sharpe_pattern, log_content)
    max_dd = re.search(max_dd_pattern, log_content)

    if final_value:
        results['performance']['final_value'] = float(final_value.group(1).replace(',', ''))
    if total_return:
        results['performance']['total_return'] = float(total_return.group(1))
    if cagr:
        results['performance']['cagr'] = float(cagr.group(1))
    if sharpe:
        results['performance']['sharpe_ratio'] = float(sharpe.group(1))
    if max_dd:
        results['performance']['max_drawdown'] = float(max_dd.group(1))

    return results


def analyze_regime_transitions(regime_transitions: List[Dict]) -> Dict:
    """Analyze regime changes over time"""

    regime_stats = {
        'total_transitions': len(regime_transitions),
        'trend_counts': {},
        'volatility_counts': {},
        'condition_counts': {},
        'regime_periods': []
    }

    for transition in regime_transitions:
        trend = transition['trend']
        volatility = transition['volatility']
        condition = transition['condition']

        regime_stats['trend_counts'][trend] = regime_stats['trend_counts'].get(trend, 0) + 1
        regime_stats['volatility_counts'][volatility] = regime_stats['volatility_counts'].get(volatility, 0) + 1
        regime_stats['condition_counts'][condition] = regime_stats['condition_counts'].get(condition, 0) + 1

    # Group consecutive similar regimes
    if regime_transitions:
        current_regime = f"{regime_transitions[0]['trend']}/{regime_transitions[0]['volatility']}"
        start_date = regime_transitions[0]['date']

        for i, transition in enumerate(regime_transitions[1:], 1):
            new_regime = f"{transition['trend']}/{transition['volatility']}"
            if new_regime != current_regime or i == len(regime_transitions) - 1:
                end_date = regime_transitions[i-1]['date']
                regime_stats['regime_periods'].append({
                    'regime': current_regime,
                    'start': start_date,
                    'end': end_date,
                    'quarters': 1
                })
                current_regime = new_regime
                start_date = transition['date']

    return regime_stats


def compare_results(baseline: Dict, enhanced: Dict) -> Dict:
    """Compare baseline vs enhanced results"""

    comparison = {
        'performance': {},
        'risk_metrics': {},
        'improvements': {}
    }

    # Performance comparison
    baseline_perf = baseline.get('performance', {})
    enhanced_perf = enhanced.get('performance', {})

    for metric in ['final_value', 'total_return', 'cagr', 'sharpe_ratio', 'max_drawdown']:
        if metric in baseline_perf and metric in enhanced_perf:
            baseline_val = baseline_perf[metric]
            enhanced_val = enhanced_perf[metric]
            change = enhanced_val - baseline_val
            change_pct = (change / baseline_val * 100) if baseline_val != 0 else 0

            comparison['performance'][metric] = {
                'baseline': baseline_val,
                'enhanced': enhanced_val,
                'change': change,
                'change_pct': change_pct
            }

    # Risk improvements
    if 'max_drawdown' in comparison['performance']:
        dd_improvement = -comparison['performance']['max_drawdown']['change']  # Negative DD is good
        comparison['improvements']['drawdown_reduction'] = dd_improvement

    if 'sharpe_ratio' in comparison['performance']:
        sharpe_improvement = comparison['performance']['sharpe_ratio']['change']
        comparison['improvements']['sharpe_improvement'] = sharpe_improvement

    # Risk events count
    comparison['risk_metrics']['stop_losses'] = len(enhanced.get('risk_events', []))
    comparison['risk_metrics']['regime_adaptations'] = len(enhanced.get('regime_transitions', []))

    return comparison


def generate_report(baseline: Dict, enhanced: Dict, comparison: Dict):
    """Generate comprehensive comparison report"""

    print("=" * 100)
    print("📊 COMPREHENSIVE BACKTEST ANALYSIS")
    print("   Baseline (Phase 1) vs Enhanced (Phases 2+3)")
    print("=" * 100)
    print()

    # Performance Summary
    print("📈 PERFORMANCE COMPARISON")
    print("-" * 100)
    print(f"{'Metric':<25} {'Baseline':<20} {'Enhanced':<20} {'Change':<20} {'% Change':<15}")
    print("-" * 100)

    for metric, data in comparison['performance'].items():
        metric_name = metric.replace('_', ' ').title()
        baseline_val = data['baseline']
        enhanced_val = data['enhanced']
        change = data['change']
        change_pct = data['change_pct']

        if metric in ['final_value']:
            baseline_str = f"${baseline_val:,.2f}"
            enhanced_str = f"${enhanced_val:,.2f}"
            change_str = f"${change:+,.2f}"
        elif metric in ['sharpe_ratio']:
            baseline_str = f"{baseline_val:.2f}"
            enhanced_str = f"{enhanced_val:.2f}"
            change_str = f"{change:+.2f}"
        else:
            baseline_str = f"{baseline_val:+.2f}%"
            enhanced_str = f"{enhanced_val:+.2f}%"
            change_str = f"{change:+.2f}pp"

        print(f"{metric_name:<25} {baseline_str:<20} {enhanced_str:<20} {change_str:<20} {change_pct:+.1f}%")

    print()

    # Regime Analysis
    if enhanced.get('regime_transitions'):
        print("🌍 MARKET REGIME ANALYSIS")
        print("-" * 100)

        regime_stats = analyze_regime_transitions(enhanced['regime_transitions'])

        print(f"Total Rebalances with Regime Detection: {regime_stats['total_transitions']}")
        print()

        print("Trend Distribution:")
        for trend, count in regime_stats['trend_counts'].items():
            pct = count / regime_stats['total_transitions'] * 100
            print(f"   {trend:<12} {count:>3} rebalances ({pct:>5.1f}%)")
        print()

        print("Volatility Distribution:")
        for vol, count in regime_stats['volatility_counts'].items():
            pct = count / regime_stats['total_transitions'] * 100
            print(f"   {vol:<12} {count:>3} rebalances ({pct:>5.1f}%)")
        print()

        if regime_stats['regime_periods']:
            print("Major Regime Periods:")
            for period in regime_stats['regime_periods']:
                print(f"   {period['start']} to {period['end']}: {period['regime']}")
        print()

    # Risk Management
    if comparison['risk_metrics']:
        print("🛡️  RISK MANAGEMENT IMPACT")
        print("-" * 100)

        stop_losses = comparison['risk_metrics'].get('stop_losses', 0)
        regime_adaptations = comparison['risk_metrics'].get('regime_adaptations', 0)

        print(f"Stop-Loss Events: {stop_losses}")
        print(f"Regime Adaptations: {regime_adaptations}")

        if 'drawdown_reduction' in comparison['improvements']:
            dd_reduction = comparison['improvements']['drawdown_reduction']
            print(f"Drawdown Reduction: {dd_reduction:.2f}pp")

        if 'sharpe_improvement' in comparison['improvements']:
            sharpe_imp = comparison['improvements']['sharpe_improvement']
            print(f"Sharpe Ratio Improvement: {sharpe_imp:+.2f}")
        print()

    # Summary
    print("=" * 100)
    print("🎯 KEY FINDINGS")
    print("=" * 100)
    print()

    # Calculate overall improvement
    if 'total_return' in comparison['performance']:
        return_change = comparison['performance']['total_return']['change']
        if return_change > 0:
            print(f"✅ Returns IMPROVED by {return_change:+.2f}pp")
        elif return_change < -2:
            print(f"⚠️  Returns DECREASED by {return_change:.2f}pp (expected tradeoff for risk reduction)")
        else:
            print(f"↔️  Returns roughly FLAT ({return_change:+.2f}pp change)")

    if 'drawdown_reduction' in comparison['improvements']:
        dd_reduction = comparison['improvements']['drawdown_reduction']
        if dd_reduction > 0:
            print(f"✅ Max Drawdown REDUCED by {dd_reduction:.2f}pp (better downside protection)")

    if 'sharpe_improvement' in comparison['improvements']:
        sharpe_imp = comparison['improvements']['sharpe_improvement']
        if sharpe_imp > 0:
            print(f"✅ Sharpe Ratio IMPROVED by {sharpe_imp:+.2f} (better risk-adjusted returns)")

    print()
    print("=" * 100)


if __name__ == "__main__":
    import sys

    # Baseline results (from Phase 1)
    baseline_results = {
        'performance': {
            'final_value': 23300.0,
            'total_return': 133.0,
            'cagr': 18.5,
            'max_drawdown': -23.0,
            'sharpe_ratio': 1.2  # Estimated
        }
    }

    # Enhanced results (from current run)
    log_path = '/tmp/full_backtest_with_regime.log'

    try:
        enhanced_results = parse_log_file(log_path)

        if not enhanced_results['performance']:
            print("⏳ Backtest still running... Performance metrics not yet available.")
            print()
            print(f"Current progress: {len(enhanced_results['rebalance_events'])} rebalances completed")
            if enhanced_results['regime_transitions']:
                print(f"Regime detections: {len(enhanced_results['regime_transitions'])}")
                print(f"Latest regime: {enhanced_results['regime_transitions'][-1]}")
            if enhanced_results['risk_events']:
                print(f"Risk events: {len(enhanced_results['risk_events'])} stop-losses triggered")
        else:
            comparison = compare_results(baseline_results, enhanced_results)
            generate_report(baseline_results, enhanced_results, comparison)

    except FileNotFoundError:
        print(f"❌ Log file not found: {log_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error analyzing results: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
