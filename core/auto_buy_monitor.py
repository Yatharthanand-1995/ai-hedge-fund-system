"""
Auto-Buy Monitor for Paper Trading

Monitors market opportunities and automatically buys based on:
1. Strong AI buy signals (STRONG BUY recommendations)
2. Score thresholds (e.g., score > 75)
3. Portfolio allocation rules
4. Position size limits
"""

import json
import logging
import requests
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Global lock to prevent concurrent auto-buy operations
_auto_buy_lock = threading.RLock()


@dataclass
class AutoBuyRule:
    """Configuration for auto-buy rules."""
    enabled: bool = False
    execution_mode: str = "immediate"  # "immediate" or "batch_4pm"
    min_score_threshold: float = 75.0  # Only buy if score >= 75
    max_position_size_percent: float = 15.0  # Max 15% of portfolio per position
    max_positions: int = 10  # Maximum number of positions
    min_confidence_level: str = "MEDIUM"  # Minimum confidence: LOW, MEDIUM, HIGH
    auto_buy_recommendations: List[str] = None  # Auto-buy on these recommendations
    max_single_trade_amount: float = 2000.0  # Max $ amount per trade
    require_sector_diversification: bool = True  # Avoid overconcentration in one sector
    max_sector_allocation_percent: float = 30.0  # Max 30% per sector

    # Score-weighted position sizing (NEW)
    use_score_weighted_sizing: bool = False  # Enable exponential score weighting
    score_weight_exponent: float = 1.5  # Exponent for score weighting curve (1.0=linear, 1.5=exponential)
    min_score_multiplier: float = 0.5  # Minimum multiplier for lowest scores (70 → 0.5x)
    max_score_multiplier: float = 1.5  # Maximum multiplier for highest scores (100 → 1.5x)

    def __post_init__(self):
        """Set defaults for mutable fields."""
        if self.auto_buy_recommendations is None:
            self.auto_buy_recommendations = ["STRONG BUY"]


class AutoBuyMonitor:
    """Monitors market and triggers auto-buys based on rules."""

    CONFIG_FILE = "data/config/auto_buy_config.json"
    ALERTS_FILE = "data/runtime/auto_buy_alerts.json"

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
            'execution_mode': rules.execution_mode,
            'min_score_threshold': rules.min_score_threshold,
            'max_position_size_percent': rules.max_position_size_percent,
            'max_positions': rules.max_positions,
            'min_confidence_level': rules.min_confidence_level,
            'auto_buy_recommendations': rules.auto_buy_recommendations,
            'max_single_trade_amount': rules.max_single_trade_amount,
            'require_sector_diversification': rules.require_sector_diversification,
            'max_sector_allocation_percent': rules.max_sector_allocation_percent,
            # Score-weighted sizing fields
            'use_score_weighted_sizing': rules.use_score_weighted_sizing,
            'score_weight_exponent': rules.score_weight_exponent,
            'min_score_multiplier': rules.min_score_multiplier,
            'max_score_multiplier': rules.max_score_multiplier
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
                'max_sector_allocation_percent': self.rules.max_sector_allocation_percent,
                'use_score_weighted_sizing': self.rules.use_score_weighted_sizing,
                'score_weight_exponent': self.rules.score_weight_exponent,
                'min_score_multiplier': self.rules.min_score_multiplier,
                'max_score_multiplier': self.rules.max_score_multiplier
            }
        }

    def get_rules(self) -> Dict:
        """Get current auto-buy rules."""
        return {
            'enabled': self.rules.enabled,
            'execution_mode': self.rules.execution_mode,
            'min_score_threshold': self.rules.min_score_threshold,
            'max_position_size_percent': self.rules.max_position_size_percent,
            'max_positions': self.rules.max_positions,
            'min_confidence_level': self.rules.min_confidence_level,
            'auto_buy_recommendations': self.rules.auto_buy_recommendations,
            'max_single_trade_amount': self.rules.max_single_trade_amount,
            'require_sector_diversification': self.rules.require_sector_diversification,
            'max_sector_allocation_percent': self.rules.max_sector_allocation_percent,
            'use_score_weighted_sizing': self.rules.use_score_weighted_sizing,
            'score_weight_exponent': self.rules.score_weight_exponent,
            'min_score_multiplier': self.rules.min_score_multiplier,
            'max_score_multiplier': self.rules.max_score_multiplier
        }

    def _check_confidence_level(self, confidence: str) -> bool:
        """Check if confidence level meets minimum requirement."""
        levels = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
        min_level = levels.get(self.rules.min_confidence_level, 2)
        actual_level = levels.get(confidence, 1)
        return actual_level >= min_level

    def _get_regime_adjusted_threshold(self) -> tuple[float, float]:
        """
        Get threshold and position size multiplier based on market regime.

        Returns: (score_threshold, position_size_multiplier)

        Market regimes and their thresholds:
        - BULL + NORMAL_VOL: Standard (70.0, 1.0)
        - BULL + HIGH_VOL: Slightly cautious (72.0, 0.9)
        - BEAR + HIGH_VOL: Very selective (78.0, 0.6)
        - BEAR + NORMAL_VOL: Higher bar (75.0, 0.75)
        - SIDEWAYS + NORMAL_VOL: Moderate (72.0, 0.85)
        - SIDEWAYS + HIGH_VOL: Conservative (74.0, 0.8)
        """
        try:
            # Fetch current regime (cached 6 hours on server side)
            response = requests.get("http://localhost:8010/market/regime", timeout=5)
            regime_data = response.json()

            trend = regime_data.get('trend', 'SIDEWAYS')
            volatility = regime_data.get('volatility', 'NORMAL_VOL')
            regime = f"{trend}_{volatility}"

            # Threshold mapping
            thresholds = {
                # BULL market regimes
                'BULL_LOW_VOL': (70.0, 1.0),      # Ideal conditions - full allocation
                'BULL_NORMAL_VOL': (70.0, 1.0),   # Standard - aggressive buying
                'BULL_HIGH_VOL': (72.0, 0.9),     # Slight caution - volatility risk

                # BEAR market regimes
                'BEAR_LOW_VOL': (76.0, 0.8),      # Defensive but stable
                'BEAR_NORMAL_VOL': (75.0, 0.75),  # Higher bar - defensive
                'BEAR_HIGH_VOL': (78.0, 0.6),     # Very selective - dangerous market

                # SIDEWAYS market regimes
                'SIDEWAYS_LOW_VOL': (71.0, 0.9),      # Wait for direction but stable
                'SIDEWAYS_NORMAL_VOL': (72.0, 0.85),  # Moderate - wait for breakout
                'SIDEWAYS_HIGH_VOL': (74.0, 0.8),     # Conservative - uncertain direction
            }

            threshold, multiplier = thresholds.get(regime, (75.0, 0.9))  # Default: conservative

            logger.info(f"Market regime: {regime} → threshold={threshold}, multiplier={multiplier:.2f}")
            return threshold, multiplier

        except Exception as e:
            logger.warning(f"Could not fetch market regime, using default threshold: {e}")
            return (75.0, 1.0)  # Fallback to conservative default

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

    def _calculate_score_weighted_position(
        self,
        overall_score: float,
        portfolio_total_value: float,
        num_positions: int
    ) -> float:
        """
        Calculate position size using exponential score weighting.

        Higher scores get exponentially larger allocations:
        - Score 70: 0.5x multiplier → ~5% of portfolio
        - Score 80: 0.83x multiplier → ~8.3%
        - Score 90: 1.28x multiplier → ~12.8%
        - Score 95: 1.44x multiplier → ~14.4%

        Formula: position_size = base_allocation * (0.5 + normalized_score^1.5)

        Args:
            overall_score: AI overall score (0-100)
            portfolio_total_value: Total portfolio value (cash + positions)
            num_positions: Current number of positions

        Returns:
            Calculated position size in dollars
        """
        # Normalize score to 0-1 range (70-100 → 0-1)
        # Scores below 70 shouldn't trigger buys, but clamp just in case
        normalized_score = (overall_score - 70) / 30
        normalized_score = max(0, min(1, normalized_score))

        # Exponential multiplier (0.5 to 1.5x)
        # Use exponent from config (default: 1.5)
        exponent = getattr(self.rules, 'score_weight_exponent', 1.5)
        multiplier = 0.5 + (normalized_score ** exponent)

        # Base allocation: divide portfolio by target number of positions (default 10)
        # This ensures we don't over-allocate even with high scores
        target_positions = max(self.rules.max_positions, 10)
        base_allocation = portfolio_total_value / target_positions

        # Apply multiplier
        position_size = base_allocation * multiplier

        # Respect max limits from rules
        max_by_percent = portfolio_total_value * (self.rules.max_position_size_percent / 100)
        position_size = min(position_size, max_by_percent, self.rules.max_single_trade_amount)

        return position_size

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

        # Get regime-adjusted threshold and position size multiplier
        regime_threshold, regime_multiplier = self._get_regime_adjusted_threshold()

        # Check score threshold (regime-adaptive)
        if overall_score < regime_threshold:
            return {
                'should_buy': False,
                'shares': 0,
                'reason': f'Score {overall_score:.1f} below regime-adjusted threshold {regime_threshold}'
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
        # Use score-weighted sizing if enabled, otherwise use fixed sizing
        use_score_weighting = getattr(self.rules, 'use_score_weighted_sizing', False)

        if use_score_weighting:
            # Score-weighted position sizing (exponential)
            max_amount = self._calculate_score_weighted_position(
                overall_score=overall_score,
                portfolio_total_value=portfolio_total_value,
                num_positions=num_positions
            )
        else:
            # Fixed position sizing (original logic)
            # Use smaller of: max_position_size_percent or max_single_trade_amount
            max_by_percent = portfolio_total_value * (self.rules.max_position_size_percent / 100)
            max_amount = min(max_by_percent, self.rules.max_single_trade_amount)

        # Apply regime-based position size multiplier
        # In volatile/bearish markets, reduce position sizes for risk management
        max_amount = max_amount * regime_multiplier

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

        THREAD-SAFE: Uses lock to prevent concurrent execution and race conditions.

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
        # Acquire lock to prevent concurrent auto-buy operations (prevents race conditions)
        with _auto_buy_lock:
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
