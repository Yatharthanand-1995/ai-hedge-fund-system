#!/bin/bash
# Monitor backtest completion and show results

LOG_FILE="/tmp/full_backtest_with_regime.log"

echo "🔍 Monitoring backtest progress..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Show current progress
LAST_REBALANCE=$(tail -200 "$LOG_FILE" | grep "Rebalancing portfolio on" | tail -1 | sed 's/.*portfolio on //')
LAST_REGIME=$(tail -100 "$LOG_FILE" | grep "Market Regime:" | tail -1 | sed 's/.*Market Regime: //')
LAST_VALUE=$(tail -100 "$LOG_FILE" | grep "Rebalanced:" | tail -1 | sed 's/.*value: //')

if [ -n "$LAST_REBALANCE" ]; then
    echo "📅 Latest Rebalance: $LAST_REBALANCE"
    echo "📊 Market Regime: $LAST_REGIME"
    echo "💰 Portfolio Value: $LAST_VALUE"
    echo ""
fi

# Check if completed
if grep -q "BOTTOM LINE" "$LOG_FILE"; then
    echo "✅ BACKTEST COMPLETE!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    tail -50 "$LOG_FILE" | grep -A 30 "BOTTOM LINE"
    exit 0
elif grep -q "5-YEAR BACKTEST RESULTS" "$LOG_FILE"; then
    echo "✅ BACKTEST COMPLETE!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    tail -80 "$LOG_FILE" | grep -A 40 "5-YEAR BACKTEST RESULTS"
    exit 0
else
    echo "⏳ Backtest still running..."
    echo ""
    echo "Progress estimate based on rebalance dates:"
    TOTAL_REBALANCES=$(tail -500 "$LOG_FILE" | grep "Rebalancing portfolio on" | wc -l | tr -d ' ')
    echo "   Completed: $TOTAL_REBALANCES / 20 quarters"
    echo "   Estimated: $(echo "scale=1; $TOTAL_REBALANCES * 5" | bc)% complete"
    echo ""
    echo "Last 5 regime detections:"
    tail -500 "$LOG_FILE" | grep "📊 Market Regime:" | tail -5
    exit 1
fi
