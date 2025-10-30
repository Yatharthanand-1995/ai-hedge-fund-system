#!/bin/bash

# Monitor both baseline and analytical fixes backtests

echo "🔄 Monitoring Both Backtests..."
echo "================================"
echo ""

while true; do
    clear
    echo "🔄 BACKTEST PROGRESS MONITOR"
    echo "================================"
    echo ""

    # Check baseline backtest
    echo "📊 BASELINE (No Protection):"
    if ps aux | grep -q "[r]un_baseline_50stocks.py"; then
        echo "   Status: ✅ RUNNING"
        # Get last few lines
        tail -5 /tmp/baseline_50stocks.log 2>/dev/null | grep -E "(Rebalancing|RESULTS|Total Return)" || echo "   Initializing..."
    else
        echo "   Status: ✅ COMPLETE or ❌ FAILED"
        if grep -q "Total Return" /tmp/baseline_50stocks.log 2>/dev/null; then
            echo "   ✅ COMPLETE!"
            grep "Total Return" /tmp/baseline_50stocks.log | tail -1
        fi
    fi

    echo ""
    echo "🎯 ANALYTICAL FIXES:"
    if ps aux | grep -q "[r]un_analytical_fixes_backtest.py"; then
        echo "   Status: ✅ RUNNING"
        tail -5 /tmp/analytical_fixes.log 2>/dev/null | grep -E "(Rebalancing|RESULTS|Total Return)" || echo "   Initializing..."
    else
        echo "   Status: ✅ COMPLETE or ❌ FAILED"
        if grep -q "Total Return" /tmp/analytical_fixes.log 2>/dev/null; then
            echo "   ✅ COMPLETE!"
            grep "Total Return" /tmp/analytical_fixes.log | tail -1
        fi
    fi

    echo ""
    echo "================================"
    echo "Press Ctrl+C to stop monitoring"
    echo ""

    # Check if both are done
    if ! ps aux | grep -q "[r]un_baseline_50stocks.py" && ! ps aux | grep -q "[r]un_analytical_fixes_backtest.py"; then
        echo "✅ Both backtests complete!"
        echo ""
        echo "📊 RESULTS SUMMARY:"
        echo ""
        echo "Baseline (No Protection):"
        grep "Total Return" /tmp/baseline_50stocks.log 2>/dev/null || echo "   ❌ Failed or incomplete"
        echo ""
        echo "Analytical Fixes (All 5 improvements):"
        grep "Total Return" /tmp/analytical_fixes.log 2>/dev/null || echo "   ❌ Failed or incomplete"
        echo ""
        break
    fi

    sleep 30
done
