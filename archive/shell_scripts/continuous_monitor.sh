#!/bin/bash
# Continuous monitoring with auto-analysis when complete

LOG_FILE="/tmp/full_backtest_with_regime.log"
ANALYSIS_SCRIPT="/Users/yatharthanand/ai_hedge_fund_system/analyze_backtest_results.py"

echo "🔄 Starting continuous monitor..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

while true; do
    # Check if backtest completed
    if grep -q "5-YEAR BACKTEST RESULTS" "$LOG_FILE" 2>/dev/null || grep -q "BOTTOM LINE" "$LOG_FILE" 2>/dev/null; then
        echo "✅ BACKTEST COMPLETE! Running full analysis..."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""

        # Run comprehensive analysis
        python3 "$ANALYSIS_SCRIPT"

        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📄 Full results saved to: $LOG_FILE"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

        break
    fi

    # Show current progress every 30 seconds
    LAST_REBALANCE=$(tail -200 "$LOG_FILE" 2>/dev/null | grep "Rebalancing portfolio on" | tail -1 | sed 's/.*portfolio on //')
    LAST_REGIME=$(tail -100 "$LOG_FILE" 2>/dev/null | grep "Market Regime:" | tail -1 | sed 's/.*Market Regime: //')

    TOTAL_REBALANCES=$(tail -500 "$LOG_FILE" 2>/dev/null | grep "Rebalancing portfolio on" | wc -l | tr -d ' ')
    PROGRESS=$(echo "scale=0; $TOTAL_REBALANCES * 5" | bc 2>/dev/null)

    clear
    echo "🔄 Backtest Progress Monitor"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📅 Latest Quarter: $LAST_REBALANCE"
    echo "📊 Market Regime: $LAST_REGIME"
    echo ""
    echo "Progress: [$TOTAL_REBALANCES/20 quarters] ~${PROGRESS}% complete"
    echo ""
    echo "⏳ Estimated time remaining: $(echo "scale=0; (20 - $TOTAL_REBALANCES) * 0.5" | bc) minutes"
    echo ""
    echo "Last 3 regime detections:"
    tail -300 "$LOG_FILE" 2>/dev/null | grep "📊 Market Regime:" | tail -3
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Checking again in 30 seconds... (Ctrl+C to stop monitoring)"

    sleep 30
done
