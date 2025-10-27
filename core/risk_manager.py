"""
Risk Management System for AI Hedge Fund
Implements:
- Drawdown protection (move to cash during severe drawdowns)
- Position-level stop-losses
- Volatility-based position sizing
- Sector concentration limits
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class RiskLimits:
    """Configuration for risk management parameters"""
    max_portfolio_drawdown: float = 0.15  # 15% max drawdown before defensive action
    position_stop_loss: float = 0.20      # 20% stop-loss per position
    max_volatility: float = 0.25          # 25% annualized volatility threshold
    max_sector_concentration: float = 0.40  # 40% max allocation per sector
    max_position_size: float = 0.10       # 10% max per position
    cash_buffer_on_drawdown: float = 0.50  # Move 50% to cash on drawdown trigger
    volatility_scale_factor: float = 0.5   # Reduce positions 50% when vol > threshold


class RiskManager:
    """
    Risk management system that monitors portfolio health and enforces risk limits.

    Key Features:
    1. Drawdown Protection: Moves to cash when portfolio declines exceed threshold
    2. Stop-Loss Management: Sells positions that decline beyond loss limits
    3. Volatility Control: Reduces exposure during high-volatility periods
    4. Sector Limits: Enforces diversification across sectors
    """

    def __init__(self, limits: Optional[RiskLimits] = None):
        self.limits = limits or RiskLimits()
        self.peak_value = 0.0
        self.is_defensive_mode = False

        logger.info("🛡️  RiskManager initialized:")
        logger.info(f"   • Max Drawdown: {self.limits.max_portfolio_drawdown*100:.1f}%")
        logger.info(f"   • Position Stop-Loss: {self.limits.position_stop_loss*100:.1f}%")
        logger.info(f"   • Max Volatility: {self.limits.max_volatility*100:.1f}%")
        logger.info(f"   • Max Sector Concentration: {self.limits.max_sector_concentration*100:.1f}%")

    def check_portfolio_drawdown(self, current_value: float, peak_value: float) -> Dict:
        """
        Check if portfolio drawdown exceeds limits.

        Returns:
            dict with:
                - is_drawdown_exceeded: bool
                - current_drawdown: float
                - recommended_cash_allocation: float
                - action: str (description of recommended action)
        """
        # Update peak
        if current_value > peak_value:
            peak_value = current_value
            self.peak_value = peak_value
            self.is_defensive_mode = False

        # Calculate current drawdown
        if peak_value > 0:
            drawdown = (current_value - peak_value) / peak_value
        else:
            drawdown = 0.0

        # Check if drawdown limit exceeded
        is_exceeded = drawdown < -self.limits.max_portfolio_drawdown

        result = {
            'is_drawdown_exceeded': is_exceeded,
            'current_drawdown': drawdown,
            'peak_value': peak_value,
            'recommended_cash_allocation': 0.0,
            'action': 'NONE'
        }

        if is_exceeded and not self.is_defensive_mode:
            # Enter defensive mode
            self.is_defensive_mode = True
            result['recommended_cash_allocation'] = self.limits.cash_buffer_on_drawdown
            result['action'] = f'DRAWDOWN_PROTECTION: Move {self.limits.cash_buffer_on_drawdown*100:.0f}% to cash'
            logger.warning(f"⚠️  Drawdown limit exceeded: {drawdown*100:.1f}% (limit: {self.limits.max_portfolio_drawdown*100:.1f}%)")
            logger.warning(f"🛡️  Entering defensive mode: Moving {self.limits.cash_buffer_on_drawdown*100:.0f}% to cash")
        elif not is_exceeded and self.is_defensive_mode:
            # Exit defensive mode (drawdown recovered)
            self.is_defensive_mode = False
            result['action'] = 'RECOVERY: Exit defensive mode, resume normal allocation'
            logger.info(f"✅ Portfolio recovered. Drawdown: {drawdown*100:.1f}%. Exiting defensive mode.")

        return result

    def check_position_stop_loss(self, positions: List[Dict], historical_volatility: Dict[str, float] = None) -> List[Dict]:
        """
        Check which positions exceed stop-loss limits.

        ANALYTICAL FIX #1: Quality-Weighted Stop-Losses
        - High quality (Q>70): 30% stop (let them recover from crashes)
        - Medium quality (Q 50-70): 20% stop
        - Low quality (Q<50): 10% stop (tight control)

        TIER 1 FIX: Hybrid Stop-Loss (Fixed + Trailing)
        - Fixed stop from entry: Protects from large losses
        - Trailing stop from peak: Protects profits on winners
        - Uses whichever triggers first (more protective)

        TIER 1 FIX: Volatility Buffer
        - High volatility stocks (60-day vol > 35%) get wider stops
        - Reduces false positives from normal volatility spikes
        - Prevents premature exits that recover quickly

        Args:
            positions: List of dicts with keys: symbol, entry_price, current_price, shares,
                      quality_score (optional), highest_price (optional), historical_data (optional)
            historical_volatility: Optional dict of {symbol: 60day_volatility} for volatility buffer

        Returns:
            List of positions to close due to stop-loss
        """
        positions_to_close = []

        for position in positions:
            symbol = position['symbol']
            entry_price = position['entry_price']
            current_price = position['current_price']
            quality_score = position.get('quality_score', 50.0)  # ANALYTICAL FIX #1
            highest_price = position.get('highest_price', entry_price)  # ANALYTICAL FIX #4

            if entry_price > 0:
                # ANALYTICAL FIX #1: Determine base stop-loss from quality
                if quality_score > 70:
                    base_stop_threshold = 0.30  # High quality: 30% stop
                    quality_tier = "HIGH"
                elif quality_score >= 50:  # ✅ FIXED: Now includes 50.0 defaults
                    base_stop_threshold = 0.20  # Medium quality: 20% stop
                    quality_tier = "MED"
                else:
                    base_stop_threshold = 0.10  # Low quality: 10% stop
                    quality_tier = "LOW"
                
                # TIER 1 FIX: Volatility buffer for high-volatility stocks
                # Reduces false positives (30.8% of stops recover within 30 days)
                volatility = None
                volatility_adjustment = 1.0
                
                if historical_volatility and symbol in historical_volatility:
                    volatility = historical_volatility[symbol]
                    
                    if volatility > 0.35:  # High volatility (>35% annualized)
                        # Widen stops by 20% to account for normal volatility
                        volatility_adjustment = 1.2
                        logger.info(f"📊 VOLATILITY BUFFER: {symbol} vol={volatility*100:.1f}% → stop widened to {base_stop_threshold*volatility_adjustment*100:.0f}%")
                
                # Apply volatility adjustment
                stop_threshold = base_stop_threshold * volatility_adjustment

                # TIER 1 FIX: Hybrid stop-loss (fixed + trailing)
                # Use TIGHTER of fixed stop (from entry) or trailing stop (from peak)
                # This prevents late exits while still letting winners run
                
                # Update highest price if current is higher
                if current_price > highest_price:
                    highest_price = current_price

                # Calculate both stop types
                drop_from_peak = (current_price - highest_price) / highest_price
                drop_from_entry = (current_price - entry_price) / entry_price

                # HYBRID LOGIC: Use whichever triggers first (more protective)
                # Fixed stop: Protects from large losses from entry
                # Trailing stop: Protects profits once position runs up
                stop_triggered = False
                stop_reason = ""
                
                if drop_from_entry < -stop_threshold:
                    # Fixed stop from entry hit (downside protection)
                    stop_triggered = True
                    stop_reason = "FIXED_STOP"
                elif drop_from_peak < -(stop_threshold + 0.05):
                    # Trailing stop from peak hit (let winners run a bit more)
                    # Use wider threshold (+5%) to avoid premature exits on winners
                    stop_triggered = True
                    stop_reason = "TRAILING_STOP"
                
                if stop_triggered:
                    positions_to_close.append({
                        'symbol': symbol,
                        'entry_price': entry_price,
                        'current_price': current_price,
                        'highest_price': highest_price,
                        'quality_score': quality_score,
                        'quality_tier': quality_tier,
                        'stop_threshold': stop_threshold,
                        'loss_pct': drop_from_entry,  # Total P&L from entry
                        'drop_from_peak': drop_from_peak,  # Peak drawdown
                        'stop_type': stop_reason,  # Which stop triggered
                        'reason': f'{stop_reason} (Q={quality_tier}, -{stop_threshold*100:.0f}% stop, entry→current: {drop_from_entry*100:.1f}%, peak→current: {drop_from_peak*100:.1f}%)'
                    })
                    
                    # Debug logging for quality score tracking
                    logger.info(f"🔍 STOP DEBUG: {symbol} Q={quality_score:.1f} → tier={quality_tier} → stop={stop_threshold*100:.0f}%")
                    
                    logger.warning(
                        f"🛑 {stop_reason} triggered for {symbol} (Quality={quality_tier}, Q={quality_score:.1f}): "
                        f"Entry ${entry_price:.2f} → Peak ${highest_price:.2f} → Current ${current_price:.2f} | "
                        f"Entry loss: {drop_from_entry*100:.1f}%, Peak drop: {drop_from_peak*100:.1f}%, "
                        f"Threshold: -{stop_threshold*100:.0f}%"
                    )

        return positions_to_close

    def calculate_volatility_adjustment(self, current_volatility: float) -> float:
        """
        Calculate position sizing adjustment based on volatility.

        Args:
            current_volatility: Current annualized volatility

        Returns:
            Adjustment factor (1.0 = normal, 0.5 = reduce positions 50%)
        """
        if current_volatility > self.limits.max_volatility:
            adjustment = self.limits.volatility_scale_factor
            logger.warning(f"⚠️  High volatility detected: {current_volatility*100:.1f}% "
                         f"(threshold: {self.limits.max_volatility*100:.1f}%)")
            logger.warning(f"📉 Reducing position sizes by {(1-adjustment)*100:.0f}%")
            return adjustment

        return 1.0  # No adjustment

    def enforce_sector_limits(self, proposed_allocations: Dict[str, float],
                             sector_mapping: Dict[str, str]) -> Dict[str, float]:
        """
        Enforce sector concentration limits.

        Args:
            proposed_allocations: Dict of {symbol: allocation_pct}
            sector_mapping: Dict of {symbol: sector}

        Returns:
            Adjusted allocations that respect sector limits
        """
        # Calculate sector exposures
        sector_exposure = {}
        for symbol, allocation in proposed_allocations.items():
            sector = sector_mapping.get(symbol, 'Unknown')
            sector_exposure[sector] = sector_exposure.get(sector, 0.0) + allocation

        # Check for violations
        violations = {sector: exposure for sector, exposure in sector_exposure.items()
                     if exposure > self.limits.max_sector_concentration}

        if violations:
            logger.warning(f"⚠️  Sector concentration limits exceeded:")
            for sector, exposure in violations.items():
                logger.warning(f"   • {sector}: {exposure*100:.1f}% "
                             f"(limit: {self.limits.max_sector_concentration*100:.1f}%)")

            # Adjust allocations proportionally within each violating sector
            adjusted_allocations = proposed_allocations.copy()

            for sector, exposure in violations.items():
                # Find all symbols in this sector
                sector_symbols = [s for s, sec in sector_mapping.items()
                                if sec == sector and s in proposed_allocations]

                # Calculate scale-down factor
                scale_factor = self.limits.max_sector_concentration / exposure

                # Reduce allocations proportionally
                for symbol in sector_symbols:
                    adjusted_allocations[symbol] *= scale_factor

                logger.info(f"   → Scaled down {sector} positions by {(1-scale_factor)*100:.1f}%")

            return adjusted_allocations

        return proposed_allocations

    def enforce_position_size_limit(self, proposed_allocations: Dict[str, float]) -> Dict[str, float]:
        """
        Enforce maximum position size limit.

        Args:
            proposed_allocations: Dict of {symbol: allocation_pct}

        Returns:
            Adjusted allocations with position size limits enforced
        """
        violations = {symbol: alloc for symbol, alloc in proposed_allocations.items()
                     if alloc > self.limits.max_position_size}

        if violations:
            logger.warning(f"⚠️  Position size limits exceeded:")
            adjusted_allocations = proposed_allocations.copy()

            for symbol, allocation in violations.items():
                logger.warning(f"   • {symbol}: {allocation*100:.1f}% "
                             f"(limit: {self.limits.max_position_size*100:.1f}%)")
                adjusted_allocations[symbol] = self.limits.max_position_size

            # Normalize remaining allocations
            total = sum(adjusted_allocations.values())
            if total > 0:
                adjusted_allocations = {s: a/total for s, a in adjusted_allocations.items()}

            return adjusted_allocations

        return proposed_allocations

    def get_risk_report(self, portfolio_value: float, peak_value: float,
                       positions: List[Dict], volatility: float) -> Dict:
        """
        Generate comprehensive risk report.

        Returns:
            Dict with risk metrics and status
        """
        drawdown_check = self.check_portfolio_drawdown(portfolio_value, peak_value)
        stop_losses = self.check_position_stop_loss(positions)
        vol_adjustment = self.calculate_volatility_adjustment(volatility)

        return {
            'portfolio_value': portfolio_value,
            'peak_value': drawdown_check['peak_value'],
            'current_drawdown': drawdown_check['current_drawdown'],
            'is_defensive_mode': self.is_defensive_mode,
            'drawdown_exceeded': drawdown_check['is_drawdown_exceeded'],
            'stop_loss_count': len(stop_losses),
            'stop_loss_positions': stop_losses,
            'volatility': volatility,
            'volatility_adjustment': vol_adjustment,
            'risk_action': drawdown_check['action']
        }
