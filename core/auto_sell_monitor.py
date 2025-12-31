"""
Auto-Sell Monitor for Paper Trading

Monitors positions and automatically sells based on:
1. Stop-loss thresholds (e.g., -10% loss)
2. Take-profit targets (e.g., +20% gain)
3. AI recommendation changes (STRONG BUY -> SELL)
4. Risk score increases
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class AutoSellRule:
    """Configuration for auto-sell rules."""
    enabled: bool = False
    stop_loss_percent: float = -10.0  # Sell if loss exceeds -10%
    take_profit_percent: float = 20.0  # Sell if gain exceeds +20%
    watch_ai_signals: bool = True  # Monitor AI recommendation changes
    max_position_age_days: Optional[int] = None  # Sell positions older than X days

    # AI-first sell logic (Phase 4)
    prioritize_ai_signals: bool = True  # AI signals override take-profit
    defer_take_profit_on_strong_signals: bool = True  # Don't sell on take-profit if AI still bullish
    ai_signal_sell_threshold: float = 50.0  # Sell if AI score drops below this (WEAK SELL territory)


class AutoSellMonitor:
    """Monitors positions and triggers auto-sells based on rules."""

    CONFIG_FILE = "data/auto_sell_config.json"
    ALERTS_FILE = "data/auto_sell_alerts.json"

    def __init__(self):
        """Initialize auto-sell monitor."""
        self.config_file = Path(self.CONFIG_FILE)
        self.alerts_file = Path(self.ALERTS_FILE)

        # Ensure data directory exists
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        # Load or initialize config
        self.rules = self._load_config()

    def _load_config(self) -> AutoSellRule:
        """Load auto-sell configuration."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                return AutoSellRule(**data)
        else:
            # Default rules
            rules = AutoSellRule()
            self._save_config(rules)
            return rules

    def _save_config(self, rules: AutoSellRule):
        """Save auto-sell configuration."""
        data = {
            'enabled': rules.enabled,
            'stop_loss_percent': rules.stop_loss_percent,
            'take_profit_percent': rules.take_profit_percent,
            'watch_ai_signals': rules.watch_ai_signals,
            'max_position_age_days': rules.max_position_age_days,
            'prioritize_ai_signals': rules.prioritize_ai_signals,
            'defer_take_profit_on_strong_signals': rules.defer_take_profit_on_strong_signals,
            'ai_signal_sell_threshold': rules.ai_signal_sell_threshold
        }
        with open(self.config_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _log_alert(self, symbol: str, reason: str, action: str, details: Dict):
        """Log auto-sell alert."""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'reason': reason,
            'action': action,
            'details': details
        }

        # Load existing alerts
        alerts = []
        if self.alerts_file.exists():
            with open(self.alerts_file, 'r') as f:
                alerts = json.load(f)

        # Append new alert
        alerts.append(alert)

        # Keep only last 100 alerts
        alerts = alerts[-100:]

        # Save back to file
        with open(self.alerts_file, 'w') as f:
            json.dump(alerts, f, indent=2)

    def update_rules(self, **kwargs) -> Dict:
        """Update auto-sell rules."""
        # Update rules
        for key, value in kwargs.items():
            if hasattr(self.rules, key):
                setattr(self.rules, key, value)

        # Save updated config
        self._save_config(self.rules)

        return {
            'success': True,
            'message': 'Auto-sell rules updated',
            'rules': {
                'enabled': self.rules.enabled,
                'stop_loss_percent': self.rules.stop_loss_percent,
                'take_profit_percent': self.rules.take_profit_percent,
                'watch_ai_signals': self.rules.watch_ai_signals,
                'max_position_age_days': self.rules.max_position_age_days
            }
        }

    def get_rules(self) -> Dict:
        """Get current auto-sell rules."""
        return {
            'enabled': self.rules.enabled,
            'stop_loss_percent': self.rules.stop_loss_percent,
            'take_profit_percent': self.rules.take_profit_percent,
            'watch_ai_signals': self.rules.watch_ai_signals,
            'max_position_age_days': self.rules.max_position_age_days,
            'prioritize_ai_signals': self.rules.prioritize_ai_signals,
            'defer_take_profit_on_strong_signals': self.rules.defer_take_profit_on_strong_signals,
            'ai_signal_sell_threshold': self.rules.ai_signal_sell_threshold
        }

    def check_position(
        self,
        symbol: str,
        cost_basis: float,
        current_price: float,
        unrealized_pnl_percent: float,
        ai_recommendation: Optional[str] = None,
        ai_score: Optional[float] = None,
        position_age_days: Optional[int] = None
    ) -> Dict:
        """
        Check if position should be auto-sold using PRIORITIZED trigger hierarchy.

        PRIORITY ORDER (Phase 4 - AI-First Logic):
        1. CRITICAL: Stop-loss (-10%) - Emergency exit, always honored
        2. PRIMARY: AI downgrades (SELL/WEAK SELL) - Main exit driver
        3. SECONDARY: Take-profit (+20%) - DEFERRED if AI still bullish
        4. TERTIARY: Position age (180 days) - Portfolio cleanup

        Args:
            symbol: Stock symbol
            cost_basis: Original purchase price
            current_price: Current market price
            unrealized_pnl_percent: Current P&L percentage
            ai_recommendation: Current AI recommendation (e.g., 'SELL', 'HOLD', 'BUY')
            ai_score: Current AI overall score (0-100)
            position_age_days: Days since position was opened

        Returns:
            Dict with should_sell flag, reason, trigger, and urgency
        """
        if not self.rules.enabled:
            return {'should_sell': False, 'reason': None}

        # ==========================================
        # PRIORITY 1 (CRITICAL): Stop-Loss
        # ==========================================
        if unrealized_pnl_percent <= self.rules.stop_loss_percent:
            reason = f"Stop-loss triggered: {unrealized_pnl_percent:.2f}% loss (threshold: {self.rules.stop_loss_percent}%)"
            self._log_alert(symbol, reason, 'TRIGGERED', {
                'unrealized_pnl_percent': unrealized_pnl_percent,
                'threshold': self.rules.stop_loss_percent,
                'urgency': 'CRITICAL'
            })
            return {
                'should_sell': True,
                'reason': reason,
                'trigger': 'stop_loss',
                'urgency': 'CRITICAL'
            }

        # ==========================================
        # PRIORITY 2 (PRIMARY): AI Signal Downgrades
        # ==========================================
        if self.rules.watch_ai_signals and self.rules.prioritize_ai_signals and ai_recommendation:
            # Immediate sell on SELL recommendation
            if ai_recommendation == 'SELL':
                score_info = f" (score: {ai_score:.1f})" if ai_score is not None else ""
                reason = f"AI downgraded to SELL{score_info}"
                self._log_alert(symbol, reason, 'TRIGGERED', {
                    'ai_recommendation': ai_recommendation,
                    'ai_score': ai_score,
                    'urgency': 'IMMEDIATE'
                })
                return {
                    'should_sell': True,
                    'reason': reason,
                    'trigger': 'ai_signal',
                    'urgency': 'IMMEDIATE'
                }

            # Sell on WEAK SELL (less urgent but still prioritized)
            if ai_recommendation == 'WEAK SELL':
                score_info = f" (score: {ai_score:.1f})" if ai_score is not None else ""
                reason = f"AI downgraded to WEAK SELL{score_info}"
                self._log_alert(symbol, reason, 'TRIGGERED', {
                    'ai_recommendation': ai_recommendation,
                    'ai_score': ai_score,
                    'urgency': 'HIGH'
                })
                return {
                    'should_sell': True,
                    'reason': reason,
                    'trigger': 'ai_signal',
                    'urgency': 'HIGH'
                }

        # ==========================================
        # PRIORITY 3 (SECONDARY): Take-Profit
        # ==========================================
        if unrealized_pnl_percent >= self.rules.take_profit_percent:
            # Check if AI is still bullish - if so, DEFER take-profit
            if (self.rules.defer_take_profit_on_strong_signals and
                ai_recommendation in ['STRONG BUY', 'BUY']):
                # DON'T sell - let winners run
                return {
                    'should_sell': False,
                    'reason': f"Take-profit reached ({unrealized_pnl_percent:.2f}%) but AI still {ai_recommendation} - holding"
                }
            else:
                # AI is neutral/bearish - take profits
                ai_info = f" (AI: {ai_recommendation})" if ai_recommendation else ""
                reason = f"Take-profit triggered: {unrealized_pnl_percent:.2f}% gain{ai_info}"
                self._log_alert(symbol, reason, 'TRIGGERED', {
                    'unrealized_pnl_percent': unrealized_pnl_percent,
                    'threshold': self.rules.take_profit_percent,
                    'ai_recommendation': ai_recommendation,
                    'urgency': 'MEDIUM'
                })
                return {
                    'should_sell': True,
                    'reason': reason,
                    'trigger': 'take_profit',
                    'urgency': 'MEDIUM'
                }

        # ==========================================
        # PRIORITY 4 (TERTIARY): Position Age
        # ==========================================
        if self.rules.max_position_age_days and position_age_days:
            if position_age_days >= self.rules.max_position_age_days:
                reason = f"Position age exceeded: {position_age_days} days (max: {self.rules.max_position_age_days})"
                self._log_alert(symbol, reason, 'TRIGGERED', {
                    'position_age_days': position_age_days,
                    'max_days': self.rules.max_position_age_days,
                    'urgency': 'LOW'
                })
                return {
                    'should_sell': True,
                    'reason': reason,
                    'trigger': 'position_age',
                    'urgency': 'LOW'
                }

        return {'should_sell': False, 'reason': None}

    def scan_portfolio(self, portfolio_with_prices: Dict, ai_recommendations: Optional[Dict[str, str]] = None) -> List[Dict]:
        """
        Scan entire portfolio for auto-sell triggers.

        Args:
            portfolio_with_prices: Portfolio dict with current prices and P&L
            ai_recommendations: Dict mapping symbol -> recommendation

        Returns:
            List of positions that should be auto-sold
        """
        if not self.rules.enabled:
            return []

        positions_to_sell = []

        for symbol, position in portfolio_with_prices.get('positions', {}).items():
            unrealized_pnl_percent = position.get('unrealized_pnl_percent', 0)
            cost_basis = position.get('cost_basis', 0)
            current_price = position.get('current_price', 0)

            # Get AI recommendation if available
            ai_rec = None
            if ai_recommendations:
                ai_rec = ai_recommendations.get(symbol)

            # Calculate position age
            position_age_days = None
            if 'first_purchase_date' in position:
                try:
                    first_purchase = datetime.fromisoformat(position['first_purchase_date'])
                    position_age_days = (datetime.now() - first_purchase).days
                except:
                    pass

            # Check if should sell
            result = self.check_position(
                symbol=symbol,
                cost_basis=cost_basis,
                current_price=current_price,
                unrealized_pnl_percent=unrealized_pnl_percent,
                ai_recommendation=ai_rec,
                position_age_days=position_age_days
            )

            if result['should_sell']:
                positions_to_sell.append({
                    'symbol': symbol,
                    'shares': position.get('shares', 0),
                    'reason': result['reason'],
                    'trigger': result['trigger'],
                    'unrealized_pnl_percent': unrealized_pnl_percent,
                    'current_price': current_price
                })

        return positions_to_sell

    def get_alerts(self, limit: int = 50) -> List[Dict]:
        """Get recent auto-sell alerts."""
        if not self.alerts_file.exists():
            return []

        with open(self.alerts_file, 'r') as f:
            alerts = json.load(f)

        # Return most recent first
        alerts.reverse()

        if limit:
            return alerts[:limit]
        return alerts
