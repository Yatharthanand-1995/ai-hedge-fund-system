"""
Auto-Buy Monitor for Paper Trading

Monitors market opportunities and automatically buys based on:
1. Strong AI buy signals (STRONG BUY recommendations)
2. Score thresholds (e.g., score > 75)
3. Portfolio allocation rules
4. Position size limits
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class AutoBuyRule:
    """Configuration for auto-buy rules."""
    enabled: bool = False
    min_score_threshold: float = 75.0  # Only buy if score >= 75
    max_position_size_percent: float = 15.0  # Max 15% of portfolio per position
    max_positions: int = 10  # Maximum number of positions
    min_confidence_level: str = "MEDIUM"  # Minimum confidence: LOW, MEDIUM, HIGH
    auto_buy_recommendations: List[str] = None  # Auto-buy on these recommendations
    max_single_trade_amount: float = 2000.0  # Max $ amount per trade
    require_sector_diversification: bool = True  # Avoid overconcentration in one sector
    max_sector_allocation_percent: float = 30.0  # Max 30% per sector

    def __post_init__(self):
        """Set defaults for mutable fields."""
        if self.auto_buy_recommendations is None:
            self.auto_buy_recommendations = ["STRONG BUY"]


class AutoBuyMonitor:
    """Monitors market and triggers auto-buys based on rules."""

    CONFIG_FILE = "data/auto_buy_config.json"
    ALERTS_FILE = "data/auto_buy_alerts.json"

    def __init__(self):
        """Initialize auto-buy monitor."""
        self.config_file = Path(self.CONFIG_FILE)
        self.alerts_file = Path(self.ALERTS_FILE)

        # Ensure data directory exists
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        # Load or initialize config
        self.rules = self._load_config()

    def _load_config(self) -> AutoBuyRule:
        """Load auto-buy configuration."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                return AutoBuyRule(**data)
        else:
            # Default rules
            rules = AutoBuyRule()
            self._save_config(rules)
            return rules

    def _save_config(self, rules: AutoBuyRule):
        """Save auto-buy configuration."""
        data = {
            'enabled': rules.enabled,
            'min_score_threshold': rules.min_score_threshold,
            'max_position_size_percent': rules.max_position_size_percent,
            'max_positions': rules.max_positions,
            'min_confidence_level': rules.min_confidence_level,
            'auto_buy_recommendations': rules.auto_buy_recommendations,
            'max_single_trade_amount': rules.max_single_trade_amount,
            'require_sector_diversification': rules.require_sector_diversification,
            'max_sector_allocation_percent': rules.max_sector_allocation_percent
        }
        with open(self.config_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _log_alert(self, symbol: str, reason: str, action: str, details: Dict):
        """Log auto-buy alert."""
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
        """Update auto-buy rules."""
        # Update rules
        for key, value in kwargs.items():
            if hasattr(self.rules, key):
                setattr(self.rules, key, value)

        # Save updated config
        self._save_config(self.rules)

        return {
            'success': True,
            'message': 'Auto-buy rules updated',
            'rules': {
                'enabled': self.rules.enabled,
                'min_score_threshold': self.rules.min_score_threshold,
                'max_position_size_percent': self.rules.max_position_size_percent,
                'max_positions': self.rules.max_positions,
                'min_confidence_level': self.rules.min_confidence_level,
                'auto_buy_recommendations': self.rules.auto_buy_recommendations,
                'max_single_trade_amount': self.rules.max_single_trade_amount,
                'require_sector_diversification': self.rules.require_sector_diversification,
                'max_sector_allocation_percent': self.rules.max_sector_allocation_percent
            }
        }

    def get_rules(self) -> Dict:
        """Get current auto-buy rules."""
        return {
            'enabled': self.rules.enabled,
            'min_score_threshold': self.rules.min_score_threshold,
            'max_position_size_percent': self.rules.max_position_size_percent,
            'max_positions': self.rules.max_positions,
            'min_confidence_level': self.rules.min_confidence_level,
            'auto_buy_recommendations': self.rules.auto_buy_recommendations,
            'max_single_trade_amount': self.rules.max_single_trade_amount,
            'require_sector_diversification': self.rules.require_sector_diversification,
            'max_sector_allocation_percent': self.rules.max_sector_allocation_percent
        }

    def _check_confidence_level(self, confidence: str) -> bool:
        """Check if confidence level meets minimum requirement."""
        levels = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
        min_level = levels.get(self.rules.min_confidence_level, 2)
        actual_level = levels.get(confidence, 1)
        return actual_level >= min_level

    def _get_sector_allocation(self, portfolio: Dict, sector_mapping: Dict[str, List[str]]) -> Dict[str, float]:
        """Calculate current sector allocation percentages."""
        sector_values = {}
        total_value = 0.0

        positions = portfolio.get('positions', {})

        for symbol, position in positions.items():
            market_value = position.get('market_value', 0)
            total_value += market_value

            # Find sector for this symbol
            sector = 'Unknown'
            for sector_name, symbols in sector_mapping.items():
                if symbol in symbols:
                    sector = sector_name
                    break

            if sector not in sector_values:
                sector_values[sector] = 0.0
            sector_values[sector] += market_value

        # Convert to percentages
        if total_value > 0:
            sector_percentages = {
                sector: (value / total_value) * 100
                for sector, value in sector_values.items()
            }
        else:
            sector_percentages = {}

        return sector_percentages

    def check_opportunity(
        self,
        symbol: str,
        overall_score: float,
        recommendation: str,
        confidence_level: str,
        current_price: float,
        portfolio_cash: float,
        portfolio_total_value: float,
        num_positions: int,
        sector: Optional[str] = None,
        sector_allocation: Optional[Dict[str, float]] = None,
        already_owned: bool = False
    ) -> Dict:
        """
        Check if stock should be auto-bought.

        Args:
            symbol: Stock symbol
            overall_score: AI overall score (0-100)
            recommendation: AI recommendation (e.g., 'STRONG BUY', 'BUY')
            confidence_level: Confidence level ('LOW', 'MEDIUM', 'HIGH')
            current_price: Current stock price
            portfolio_cash: Available cash
            portfolio_total_value: Total portfolio value
            num_positions: Number of current positions
            sector: Stock sector (for diversification)
            sector_allocation: Current sector allocation percentages
            already_owned: Whether stock is already owned

        Returns:
            Dict with should_buy flag, shares to buy, and reason
        """
        if not self.rules.enabled:
            return {'should_buy': False, 'shares': 0, 'reason': None}

        # Skip if already owned (avoid doubling down)
        if already_owned:
            return {
                'should_buy': False,
                'shares': 0,
                'reason': 'Already own this position'
            }

        # Check max positions
        if num_positions >= self.rules.max_positions:
            return {
                'should_buy': False,
                'shares': 0,
                'reason': f'Maximum positions reached ({self.rules.max_positions})'
            }

        # Check score threshold
        if overall_score < self.rules.min_score_threshold:
            return {
                'should_buy': False,
                'shares': 0,
                'reason': f'Score {overall_score:.1f} below threshold {self.rules.min_score_threshold}'
            }

        # Check recommendation
        if recommendation not in self.rules.auto_buy_recommendations:
            return {
                'should_buy': False,
                'shares': 0,
                'reason': f'Recommendation "{recommendation}" not in auto-buy list'
            }

        # Check confidence level
        if not self._check_confidence_level(confidence_level):
            return {
                'should_buy': False,
                'shares': 0,
                'reason': f'Confidence {confidence_level} below minimum {self.rules.min_confidence_level}'
            }

        # Check sector diversification
        if self.rules.require_sector_diversification and sector and sector_allocation:
            current_sector_pct = sector_allocation.get(sector, 0.0)
            if current_sector_pct >= self.rules.max_sector_allocation_percent:
                return {
                    'should_buy': False,
                    'shares': 0,
                    'reason': f'Sector {sector} at {current_sector_pct:.1f}% (max: {self.rules.max_sector_allocation_percent}%)'
                }

        # Calculate position size
        # Use smaller of: max_position_size_percent or max_single_trade_amount
        max_by_percent = portfolio_total_value * (self.rules.max_position_size_percent / 100)
        max_amount = min(max_by_percent, self.rules.max_single_trade_amount)

        # Check if we have enough cash
        if portfolio_cash < current_price:
            return {
                'should_buy': False,
                'shares': 0,
                'reason': f'Insufficient cash (${portfolio_cash:.2f}) for 1 share (${current_price:.2f})'
            }

        # Calculate shares to buy
        available_for_trade = min(max_amount, portfolio_cash)
        shares_to_buy = int(available_for_trade / current_price)

        if shares_to_buy < 1:
            return {
                'should_buy': False,
                'shares': 0,
                'reason': f'Insufficient cash for 1 share at ${current_price:.2f}'
            }

        # Calculate actual cost
        total_cost = shares_to_buy * current_price

        reason = f"Auto-buy triggered: {recommendation} (score: {overall_score:.1f}, confidence: {confidence_level})"

        self._log_alert(symbol, reason, 'TRIGGERED', {
            'overall_score': overall_score,
            'recommendation': recommendation,
            'confidence_level': confidence_level,
            'shares': shares_to_buy,
            'price': current_price,
            'total_cost': total_cost
        })

        return {
            'should_buy': True,
            'shares': shares_to_buy,
            'total_cost': total_cost,
            'reason': reason,
            'trigger': 'ai_signal'
        }

    def scan_opportunities(
        self,
        analyses: List[Dict],
        portfolio_cash: float,
        portfolio_total_value: float,
        num_positions: int,
        owned_symbols: List[str],
        sector_mapping: Optional[Dict[str, List[str]]] = None,
        portfolio_positions: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Scan multiple stock analyses for auto-buy opportunities.

        Args:
            analyses: List of stock analysis results
            portfolio_cash: Available cash
            portfolio_total_value: Total portfolio value
            num_positions: Number of current positions
            owned_symbols: List of currently owned symbols
            sector_mapping: Mapping of sectors to symbols
            portfolio_positions: Current portfolio positions (for sector allocation)

        Returns:
            List of stocks that should be auto-bought
        """
        if not self.rules.enabled:
            return []

        # Calculate sector allocation
        sector_allocation = {}
        if sector_mapping and portfolio_positions:
            sector_allocation = self._get_sector_allocation(
                {'positions': portfolio_positions},
                sector_mapping
            )

        opportunities = []

        for analysis in analyses:
            symbol = analysis.get('symbol')
            narrative = analysis.get('narrative', {})
            market_data = analysis.get('market_data', {})

            overall_score = narrative.get('overall_score', 0)
            recommendation = narrative.get('recommendation', 'HOLD')
            confidence_level = narrative.get('confidence_level', 'LOW')
            current_price = market_data.get('current_price', 0)

            # Find sector
            sector = None
            if sector_mapping:
                for sector_name, symbols in sector_mapping.items():
                    if symbol in symbols:
                        sector = sector_name
                        break

            # Check if should buy
            result = self.check_opportunity(
                symbol=symbol,
                overall_score=overall_score,
                recommendation=recommendation,
                confidence_level=confidence_level,
                current_price=current_price,
                portfolio_cash=portfolio_cash,
                portfolio_total_value=portfolio_total_value,
                num_positions=num_positions,
                sector=sector,
                sector_allocation=sector_allocation,
                already_owned=symbol in owned_symbols
            )

            if result['should_buy']:
                opportunities.append({
                    'symbol': symbol,
                    'shares': result['shares'],
                    'price': current_price,
                    'total_cost': result['total_cost'],
                    'reason': result['reason'],
                    'trigger': result['trigger'],
                    'overall_score': overall_score,
                    'recommendation': recommendation,
                    'sector': sector
                })

                # Update tracking for next iteration
                num_positions += 1
                portfolio_cash -= result['total_cost']

                # Update sector allocation
                if sector and sector_allocation is not None:
                    current_sector_value = (sector_allocation.get(sector, 0) / 100) * portfolio_total_value
                    new_sector_value = current_sector_value + result['total_cost']
                    new_total_value = portfolio_total_value  # Simplified (cash moved to stock)
                    sector_allocation[sector] = (new_sector_value / new_total_value) * 100

        return opportunities

    def get_alerts(self, limit: int = 50) -> List[Dict]:
        """Get recent auto-buy alerts."""
        if not self.alerts_file.exists():
            return []

        with open(self.alerts_file, 'r') as f:
            alerts = json.load(f)

        # Return most recent first
        alerts.reverse()

        if limit:
            return alerts[:limit]
        return alerts
