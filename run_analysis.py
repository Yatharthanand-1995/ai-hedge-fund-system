#!/usr/bin/env python3
"""
Direct System Analysis - Run from current directory
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from test_system_accuracy import *

if __name__ == "__main__":
    print("Starting comprehensive system accuracy analysis...")

    # Test individual agents
    results = test_agent_consistency()

    # Test portfolio endpoint
    portfolio_works = test_portfolio_endpoint()

    # Analyze issues
    if results:
        issues = analyze_scoring_issues(results)
        suggest_improvements(issues)

    print(f"\n🏁 ANALYSIS COMPLETE")
    print(f"System Status: {'✅ Healthy' if not issues and portfolio_works else '⚠️ Issues Found'}")