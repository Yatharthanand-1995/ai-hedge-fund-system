#!/usr/bin/env python3
"""
Test Reproducibility of Backtest Results
Runs the backtest again and compares with original 239% result
"""
import json
import os
from datetime import datetime

print("="*80)
print("REPRODUCIBILITY TEST")
print("="*80)
print()
print("📊 Testing if we get the same 239.01% return on a fresh backtest run...")
print()

# Load original result
with open('frontend/public/static_backtest_result_original.json', 'r') as f:
    original = json.load(f)

original_return = original['results']['total_return']
original_cagr = original['results']['cagr']
original_final = original['results']['final_value']
original_trades = len(original['trade_log'])

print("Original Backtest (Run 1):")
print(f"  Total Return: {original_return*100:.2f}%")
print(f"  CAGR: {original_cagr*100:.2f}%")
print(f"  Final Value: ${original_final:,.2f}")
print(f"  Total Trades: {original_trades}")
print()

print("⏳ Running fresh backtest (Run 2)...")
print("   This will take 5-10 minutes...")
print()

# Run fresh backtest
os.system('python3 generate_static_backtest.py > logs/reproducibility_test.log 2>&1')

# Load new result
with open('frontend/public/static_backtest_result.json', 'r') as f:
    new = json.load(f)

new_return = new['results']['total_return']
new_cagr = new['results']['cagr']
new_final = new['results']['final_value']
new_trades = len(new['trade_log'])

print()
print("="*80)
print("COMPARISON RESULTS")
print("="*80)
print()

print(f"{'Metric':<20} {'Run 1 (Original)':<20} {'Run 2 (New)':<20} {'Difference':<15}")
print("-"*80)
print(f"{'Total Return':<20} {original_return*100:>18.2f}% {new_return*100:>18.2f}% {(new_return-original_return)*100:>+13.2f}%")
print(f"{'CAGR':<20} {original_cagr*100:>18.2f}% {new_cagr*100:>18.2f}% {(new_cagr-original_cagr)*100:>+13.2f}%")
print(f"{'Final Value':<20} ${original_final:>17,.2f} ${new_final:>17,.2f} ${new_final-original_final:>+12,.2f}")
print(f"{'Total Trades':<20} {original_trades:>18} {new_trades:>18} {new_trades-original_trades:>+13}")
print()

# Calculate variance
return_variance = abs((new_return - original_return) / original_return * 100)
cagr_variance = abs((new_cagr - original_cagr) / original_cagr * 100)
value_variance = abs((new_final - original_final) / original_final * 100)

print("Variance Analysis:")
print(f"  Return Variance: {return_variance:.4f}%")
print(f"  CAGR Variance: {cagr_variance:.4f}%")
print(f"  Final Value Variance: {value_variance:.4f}%")
print()

# Determine status
if return_variance < 0.1 and cagr_variance < 0.1:
    print("✅ EXCELLENT: Results are nearly identical (<0.1% variance)")
    print("   System is highly reproducible!")
elif return_variance < 1.0 and cagr_variance < 1.0:
    print("✅ GOOD: Results are very similar (<1% variance)")
    print("   Minor differences likely due to data updates")
elif return_variance < 5.0 and cagr_variance < 5.0:
    print("⚠️  MODERATE: Results show some variance (<5%)")
    print("   Data snapshot functionality recommended")
else:
    print("❌ HIGH VARIANCE: Results differ significantly (>5%)")
    print("   Data snapshot functionality REQUIRED")

print()
print("="*80)
print("RECOMMENDATION")
print("="*80)
print()

if return_variance < 1.0:
    print("✅ Current reproducibility is acceptable for development")
    print("   Can proceed to Phase 2 (Live System Implementation)")
    print()
    print("Optional improvements:")
    print("  - Add data snapshot for deterministic testing")
    print("  - Cache historical data for faster reruns")
else:
    print("⚠️  Data snapshot functionality is needed for reliable testing")
    print()
    print("Next steps:")
    print("  1. Implement data caching/snapshot system")
    print("  2. Freeze historical data for reproducibility")
    print("  3. Rerun this test with frozen data")
    print("  4. Aim for <0.1% variance before proceeding")

print()
print(f"📝 Detailed logs saved to: logs/reproducibility_test.log")
print()
