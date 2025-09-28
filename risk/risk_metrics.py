"""
Risk Metrics - Comprehensive Risk Analysis
Combines all risk calculations into unified interface
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

from .var_calculator import VaRCalculator
from .correlation import CorrelationTracker
from .drawdown_monitor import DrawdownMonitor

logger = logging.getLogger(__name__)


class RiskMetrics:
    """
    Comprehensive risk metrics calculator

    Combines:
    - Value at Risk (VaR) analysis
    - Correlation tracking
    - Drawdown monitoring
    """

    def __init__(self, confidence_level: float = 0.95):
        """
        Initialize risk metrics calculator

        Args:
            confidence_level: Confidence level for VaR (default 95%)
        """
        self.var_calc = VaRCalculator(confidence_level=confidence_level)
        self.corr_tracker = CorrelationTracker()
        self.dd_monitor = DrawdownMonitor()

        logger.info(f"RiskMetrics initialized (confidence: {confidence_level})")

    def calculate_all_metrics(self, portfolio_values: pd.Series,
                              positions: Dict[str, float],
                              returns_data: pd.DataFrame,
                              market_returns: Optional[pd.Series] = None) -> Dict:
        """
        Calculate all risk metrics for portfolio

        Args:
            portfolio_values: Series of portfolio values over time
            positions: Dict of {symbol: weight}
            returns_data: DataFrame with returns for each symbol
            market_returns: Optional market (SPY) returns for correlation

        Returns:
            Comprehensive risk metrics dictionary
        """
        try:
            # Calculate portfolio returns
            portfolio_returns = portfolio_values.pct_change().dropna()

            # VaR metrics
            var_metrics = self.var_calc.calculate_all_metrics(portfolio_returns)

            # Correlation metrics
            corr_metrics = self.corr_tracker.calculate_portfolio_correlation(
                positions, returns_data
            )

            # Market correlation (if provided)
            market_corr = None
            if market_returns is not None:
                market_corr = self.corr_tracker.calculate_market_correlation(
                    portfolio_returns, market_returns
                )

            # Diversification ratio
            div_ratio = self.corr_tracker.calculate_diversification_ratio(
                positions, returns_data
            )

            # Drawdown metrics
            dd_metrics = self.dd_monitor.get_drawdown_summary(portfolio_values)

            # Risk score (0-100, lower is better)
            risk_score = self._calculate_risk_score(
                var_metrics, corr_metrics, dd_metrics
            )

            return {
                'risk_score': risk_score,
                'var_metrics': var_metrics,
                'correlation_metrics': corr_metrics,
                'market_correlation': market_corr,
                'diversification': div_ratio,
                'drawdown_metrics': dd_metrics,
                'positions': positions,
                'timestamp': pd.Timestamp.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Risk metrics calculation failed: {e}")
            return {
                'error': str(e),
                'positions': positions
            }

    def _calculate_risk_score(self, var_metrics: Dict, corr_metrics: Dict,
                             dd_metrics: Dict) -> Dict:
        """
        Calculate overall risk score (0-100, lower is better)

        Components:
        - VaR contribution: 30%
        - Correlation contribution: 30%
        - Drawdown contribution: 40%
        """
        try:
            score = 0
            components = {}

            # VaR component (30 points)
            # Higher VaR = higher score (worse)
            if 'historical_var' in var_metrics and 'var' in var_metrics['historical_var']:
                var_value = abs(var_metrics['historical_var']['var'])
                # Scale: 5% VaR = 30 points, 1% VaR = 6 points
                var_score = min(var_value * 600, 30)
                score += var_score
                components['var_score'] = round(var_score, 1)

            # Correlation component (30 points)
            # Higher correlation = higher score (worse)
            if 'avg_correlation' in corr_metrics:
                avg_corr = corr_metrics['avg_correlation']
                # Scale: 0.9 corr = 30 points, 0.3 corr = 10 points
                corr_score = min((avg_corr - 0.3) / 0.6 * 30, 30)
                corr_score = max(corr_score, 0)
                score += corr_score
                components['correlation_score'] = round(corr_score, 1)

            # Drawdown component (40 points)
            # Higher drawdown = higher score (worse)
            if 'max_drawdown' in dd_metrics and 'max_drawdown' in dd_metrics['max_drawdown']:
                max_dd = abs(dd_metrics['max_drawdown']['max_drawdown'])
                # Scale: 50% DD = 40 points, 10% DD = 8 points
                dd_score = min(max_dd * 80, 40)
                score += dd_score
                components['drawdown_score'] = round(dd_score, 1)

            # Risk level interpretation
            if score < 30:
                risk_level = 'LOW'
                interpretation = 'Well-controlled risk profile'
            elif score < 50:
                risk_level = 'MODERATE'
                interpretation = 'Acceptable risk levels'
            elif score < 70:
                risk_level = 'ELEVATED'
                interpretation = 'Higher than optimal risk'
            else:
                risk_level = 'HIGH'
                interpretation = 'Risk reduction recommended'

            return {
                'total_score': round(score, 1),
                'risk_level': risk_level,
                'interpretation': interpretation,
                'components': components,
                'scale': '0-100 (lower is better)'
            }

        except Exception as e:
            logger.error(f"Risk score calculation failed: {e}")
            return {
                'total_score': np.nan,
                'error': str(e)
            }

    def get_risk_alerts(self, portfolio_values: pd.Series,
                       positions: Dict[str, float],
                       returns_data: pd.DataFrame) -> List[Dict]:
        """
        Generate risk alerts based on thresholds

        Returns:
            List of alert dictionaries
        """
        try:
            alerts = []

            # Calculate current drawdown
            current_dd = self.dd_monitor.calculate_current_drawdown(portfolio_values)

            # Drawdown alerts
            if 'alert_level' in current_dd and current_dd['alert_level'] != 'NORMAL':
                alerts.append({
                    'type': 'DRAWDOWN',
                    'severity': current_dd['alert_level'],
                    'message': f"Portfolio in {current_dd['alert_level']} drawdown: {current_dd['current_drawdown_pct']:.1f}%",
                    'value': current_dd['current_drawdown_pct']
                })

            # Correlation alerts
            corr_metrics = self.corr_tracker.calculate_portfolio_correlation(
                positions, returns_data
            )

            if 'avg_correlation' in corr_metrics and corr_metrics['avg_correlation'] > 0.8:
                alerts.append({
                    'type': 'CORRELATION',
                    'severity': 'WARNING',
                    'message': f"High portfolio correlation: {corr_metrics['avg_correlation']:.2f}",
                    'value': corr_metrics['avg_correlation']
                })

            # VaR alerts
            portfolio_returns = portfolio_values.pct_change().dropna()
            var_metrics = self.var_calc.calculate_historical_var(portfolio_returns)

            if 'var' in var_metrics:
                var_pct = abs(var_metrics['var'] * 100)
                if var_pct > 5:
                    alerts.append({
                        'type': 'VAR',
                        'severity': 'WARNING' if var_pct < 7 else 'MODERATE',
                        'message': f"High Value at Risk: {var_pct:.1f}% daily VaR",
                        'value': var_pct
                    })

            # Sort by severity
            severity_order = {'SEVERE': 0, 'MODERATE': 1, 'WARNING': 2}
            alerts.sort(key=lambda x: severity_order.get(x['severity'], 3))

            return alerts

        except Exception as e:
            logger.error(f"Risk alert generation failed: {e}")
            return []

    def generate_risk_report(self, portfolio_values: pd.Series,
                            positions: Dict[str, float],
                            returns_data: pd.DataFrame,
                            market_returns: Optional[pd.Series] = None) -> str:
        """
        Generate human-readable risk report

        Returns:
            Formatted risk report string
        """
        try:
            metrics = self.calculate_all_metrics(
                portfolio_values, positions, returns_data, market_returns
            )

            report = []
            report.append("=" * 60)
            report.append("PORTFOLIO RISK REPORT")
            report.append("=" * 60)
            report.append("")

            # Risk Score
            if 'risk_score' in metrics:
                rs = metrics['risk_score']
                report.append(f"Overall Risk Score: {rs['total_score']}/100")
                report.append(f"Risk Level: {rs['risk_level']}")
                report.append(f"Assessment: {rs['interpretation']}")
                report.append("")

            # VaR Metrics
            if 'var_metrics' in metrics and 'historical_var' in metrics['var_metrics']:
                var = metrics['var_metrics']['historical_var']
                report.append("Value at Risk (95% confidence):")
                report.append(f"  Daily VaR: {abs(var['var']*100):.2f}%")
                if 'cvar' in metrics['var_metrics']:
                    cvar = metrics['var_metrics']['cvar']
                    report.append(f"  CVaR (Expected Shortfall): {abs(cvar['cvar']*100):.2f}%")
                report.append("")

            # Correlation
            if 'correlation_metrics' in metrics:
                corr = metrics['correlation_metrics']
                if 'avg_correlation' in corr:
                    report.append("Correlation Analysis:")
                    report.append(f"  Avg Pairwise Correlation: {corr['avg_correlation']:.2f}")
                    report.append(f"  Concentration Risk: {corr['concentration_risk']}")
                    report.append("")

            # Drawdown
            if 'drawdown_metrics' in metrics:
                dd = metrics['drawdown_metrics']
                if 'max_drawdown' in dd:
                    max_dd = dd['max_drawdown']
                    report.append("Drawdown Analysis:")
                    report.append(f"  Max Drawdown: {abs(max_dd['max_drawdown_pct']):.1f}%")
                    report.append(f"  Peak: ${max_dd['peak_value']:,.0f} on {max_dd['peak_date']}")
                    report.append(f"  Trough: ${max_dd['trough_value']:,.0f} on {max_dd['trough_date']}")
                    if max_dd['is_recovered']:
                        report.append(f"  Recovery: {max_dd['recovery_duration_days']} days")

                if 'current_drawdown' in dd:
                    curr_dd = dd['current_drawdown']
                    report.append(f"  Current Drawdown: {abs(curr_dd['current_drawdown_pct']):.1f}%")
                    report.append(f"  Alert Level: {curr_dd['alert_level']}")
                report.append("")

            # Alerts
            alerts = self.get_risk_alerts(portfolio_values, positions, returns_data)
            if alerts:
                report.append("Risk Alerts:")
                for alert in alerts:
                    report.append(f"  [{alert['severity']}] {alert['message']}")
                report.append("")

            report.append("=" * 60)

            return "\n".join(report)

        except Exception as e:
            logger.error(f"Risk report generation failed: {e}")
            return f"Error generating risk report: {e}"