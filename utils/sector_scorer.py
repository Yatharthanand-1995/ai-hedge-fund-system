"""
Sector-Aware Scoring System
Adjusts scoring thresholds based on sector-specific characteristics
"""

from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class SectorBenchmarks:
    """
    Sector-specific benchmarks for financial metrics
    Based on historical averages and industry standards
    """

    # Sector-specific thresholds for fundamentals
    SECTOR_FUNDAMENTALS = {
        'Technology': {
            'roe': {
                'excellent': 12.0,   # Tech can have lower ROE due to asset-light
                'good': 10.0,
                'acceptable': 7.0
            },
            'pe_ratio': {
                'excellent': 30.0,   # Higher P/E acceptable for growth
                'good': 40.0,
                'acceptable': 50.0,
                'max_acceptable': 60.0
            },
            'net_margin': {
                'excellent': 20.0,   # Tech typically has high margins
                'good': 15.0,
                'acceptable': 10.0
            },
            'revenue_growth': {
                'excellent': 15.0,   # High growth expected
                'good': 10.0,
                'acceptable': 5.0
            },
            'debt_to_equity': {
                'excellent': 0.3,    # Low debt preferred
                'good': 0.5,
                'acceptable': 1.0
            }
        },

        'Healthcare': {
            'roe': {
                'excellent': 15.0,
                'good': 12.0,
                'acceptable': 8.0
            },
            'pe_ratio': {
                'excellent': 20.0,   # Moderate P/E
                'good': 30.0,
                'acceptable': 40.0,
                'max_acceptable': 50.0
            },
            'net_margin': {
                'excellent': 15.0,
                'good': 12.0,
                'acceptable': 8.0
            },
            'revenue_growth': {
                'excellent': 12.0,
                'good': 8.0,
                'acceptable': 4.0
            },
            'debt_to_equity': {
                'excellent': 0.4,
                'good': 0.7,
                'acceptable': 1.2
            }
        },

        'Financial': {
            'roe': {
                'excellent': 10.0,   # Lower ROE is normal for banks
                'good': 8.0,
                'acceptable': 6.0
            },
            'pe_ratio': {
                'excellent': 12.0,   # Value sector - lower P/E
                'good': 15.0,
                'acceptable': 20.0,
                'max_acceptable': 25.0
            },
            'net_margin': {
                'excellent': 20.0,   # Banks can have good margins
                'good': 15.0,
                'acceptable': 10.0
            },
            'revenue_growth': {
                'excellent': 8.0,    # Slower growth
                'good': 5.0,
                'acceptable': 2.0
            },
            'debt_to_equity': {
                'excellent': 1.5,    # Higher debt is normal for financials
                'good': 2.5,
                'acceptable': 4.0
            }
        },

        'Consumer': {
            'roe': {
                'excellent': 15.0,
                'good': 12.0,
                'acceptable': 8.0
            },
            'pe_ratio': {
                'excellent': 20.0,
                'good': 25.0,
                'acceptable': 30.0,
                'max_acceptable': 35.0
            },
            'net_margin': {
                'excellent': 10.0,   # Retail has lower margins
                'good': 7.0,
                'acceptable': 4.0
            },
            'revenue_growth': {
                'excellent': 10.0,
                'good': 6.0,
                'acceptable': 3.0
            },
            'debt_to_equity': {
                'excellent': 0.5,
                'good': 1.0,
                'acceptable': 2.0
            }
        },

        'Energy': {
            'roe': {
                'excellent': 12.0,
                'good': 9.0,
                'acceptable': 6.0
            },
            'pe_ratio': {
                'excellent': 12.0,   # Cyclical, lower P/E
                'good': 15.0,
                'acceptable': 20.0,
                'max_acceptable': 25.0
            },
            'net_margin': {
                'excellent': 8.0,    # Commodity-driven margins
                'good': 5.0,
                'acceptable': 2.0
            },
            'revenue_growth': {
                'excellent': 8.0,
                'good': 5.0,
                'acceptable': 0.0    # Can be flat in down cycles
            },
            'debt_to_equity': {
                'excellent': 0.3,
                'good': 0.6,
                'acceptable': 1.0
            }
        },

        'Industrial': {
            'roe': {
                'excellent': 14.0,
                'good': 11.0,
                'acceptable': 7.0
            },
            'pe_ratio': {
                'excellent': 18.0,
                'good': 22.0,
                'acceptable': 28.0,
                'max_acceptable': 35.0
            },
            'net_margin': {
                'excellent': 12.0,
                'good': 8.0,
                'acceptable': 5.0
            },
            'revenue_growth': {
                'excellent': 10.0,
                'good': 6.0,
                'acceptable': 2.0
            },
            'debt_to_equity': {
                'excellent': 0.5,
                'good': 1.0,
                'acceptable': 2.0
            }
        },

        'Communication': {
            'roe': {
                'excellent': 15.0,
                'good': 12.0,
                'acceptable': 8.0
            },
            'pe_ratio': {
                'excellent': 25.0,   # Media/entertainment growth premiums
                'good': 35.0,
                'acceptable': 45.0,
                'max_acceptable': 55.0
            },
            'net_margin': {
                'excellent': 15.0,
                'good': 10.0,
                'acceptable': 5.0
            },
            'revenue_growth': {
                'excellent': 12.0,
                'good': 8.0,
                'acceptable': 3.0
            },
            'debt_to_equity': {
                'excellent': 0.5,
                'good': 1.0,
                'acceptable': 2.0
            }
        }
    }

    # Default benchmarks for unknown sectors
    DEFAULT_BENCHMARKS = {
        'roe': {'excellent': 15.0, 'good': 12.0, 'acceptable': 8.0},
        'pe_ratio': {'excellent': 20.0, 'good': 25.0, 'acceptable': 30.0, 'max_acceptable': 40.0},
        'net_margin': {'excellent': 15.0, 'good': 10.0, 'acceptable': 5.0},
        'revenue_growth': {'excellent': 10.0, 'good': 6.0, 'acceptable': 3.0},
        'debt_to_equity': {'excellent': 0.5, 'good': 1.0, 'acceptable': 2.0}
    }


class SectorAwareScorer:
    """
    Provides sector-adjusted scoring for financial metrics
    """

    def __init__(self):
        self.benchmarks = SectorBenchmarks()
        logger.info("SectorAwareScorer initialized with 7 sector profiles")

    def get_sector_benchmarks(self, sector: str) -> Dict:
        """Get benchmarks for a specific sector"""
        return self.benchmarks.SECTOR_FUNDAMENTALS.get(
            sector,
            self.benchmarks.DEFAULT_BENCHMARKS
        )

    def score_roe_sector_adjusted(self, roe: float, sector: str) -> float:
        """
        Score ROE based on sector-specific thresholds

        Args:
            roe: Return on Equity (%)
            sector: Sector name

        Returns:
            Score from 0-40
        """
        benchmarks = self.get_sector_benchmarks(sector)
        roe_thresholds = benchmarks.get('roe', self.benchmarks.DEFAULT_BENCHMARKS['roe'])

        if roe >= roe_thresholds['excellent']:
            return 40.0
        elif roe >= roe_thresholds['good']:
            # Linear interpolation between good and excellent
            progress = (roe - roe_thresholds['good']) / (roe_thresholds['excellent'] - roe_thresholds['good'])
            return 35.0 + (5.0 * progress)
        elif roe >= roe_thresholds['acceptable']:
            # Linear interpolation between acceptable and good
            progress = (roe - roe_thresholds['acceptable']) / (roe_thresholds['good'] - roe_thresholds['acceptable'])
            return 25.0 + (10.0 * progress)
        elif roe > 0:
            # Some points for positive ROE
            progress = roe / roe_thresholds['acceptable']
            return min(15.0 * progress, 15.0)
        else:
            return 0.0

    def score_pe_ratio_sector_adjusted(self, pe: float, sector: str) -> float:
        """
        Score P/E ratio based on sector-specific thresholds

        Args:
            pe: Price to Earnings ratio
            sector: Sector name

        Returns:
            Score from 0-40
        """
        if pe <= 0:
            return 0.0

        benchmarks = self.get_sector_benchmarks(sector)
        pe_thresholds = benchmarks.get('pe_ratio', self.benchmarks.DEFAULT_BENCHMARKS['pe_ratio'])

        if pe <= pe_thresholds['excellent']:
            return 40.0
        elif pe <= pe_thresholds['good']:
            # Linear interpolation
            progress = (pe_thresholds['good'] - pe) / (pe_thresholds['good'] - pe_thresholds['excellent'])
            return 30.0 + (10.0 * progress)
        elif pe <= pe_thresholds['acceptable']:
            progress = (pe_thresholds['acceptable'] - pe) / (pe_thresholds['acceptable'] - pe_thresholds['good'])
            return 20.0 + (10.0 * progress)
        elif pe <= pe_thresholds['max_acceptable']:
            progress = (pe_thresholds['max_acceptable'] - pe) / (pe_thresholds['max_acceptable'] - pe_thresholds['acceptable'])
            return 10.0 + (10.0 * progress)
        else:
            # Beyond max acceptable, penalize heavily
            return max(5.0 - (pe - pe_thresholds['max_acceptable']), 0.0)

    def score_net_margin_sector_adjusted(self, margin: float, sector: str) -> float:
        """
        Score net margin based on sector-specific thresholds

        Args:
            margin: Net profit margin (%)
            sector: Sector name

        Returns:
            Score from 0-30
        """
        benchmarks = self.get_sector_benchmarks(sector)
        margin_thresholds = benchmarks.get('net_margin', self.benchmarks.DEFAULT_BENCHMARKS['net_margin'])

        if margin >= margin_thresholds['excellent']:
            return 30.0
        elif margin >= margin_thresholds['good']:
            progress = (margin - margin_thresholds['good']) / (margin_thresholds['excellent'] - margin_thresholds['good'])
            return 25.0 + (5.0 * progress)
        elif margin >= margin_thresholds['acceptable']:
            progress = (margin - margin_thresholds['acceptable']) / (margin_thresholds['good'] - margin_thresholds['acceptable'])
            return 20.0 + (5.0 * progress)
        elif margin > 0:
            progress = margin / margin_thresholds['acceptable']
            return min(12.0 * progress, 12.0)
        else:
            return 0.0

    def score_revenue_growth_sector_adjusted(self, growth: float, sector: str) -> float:
        """
        Score revenue growth based on sector-specific thresholds

        Args:
            growth: Revenue growth (%)
            sector: Sector name

        Returns:
            Score from 0-40
        """
        benchmarks = self.get_sector_benchmarks(sector)
        growth_thresholds = benchmarks.get('revenue_growth', self.benchmarks.DEFAULT_BENCHMARKS['revenue_growth'])

        if growth >= growth_thresholds['excellent']:
            return 40.0
        elif growth >= growth_thresholds['good']:
            progress = (growth - growth_thresholds['good']) / (growth_thresholds['excellent'] - growth_thresholds['good'])
            return 30.0 + (10.0 * progress)
        elif growth >= growth_thresholds['acceptable']:
            progress = (growth - growth_thresholds['acceptable']) / (growth_thresholds['good'] - growth_thresholds['acceptable'])
            return 25.0 + (5.0 * progress)
        elif growth > 0:
            progress = growth / growth_thresholds['acceptable']
            return min(15.0 * progress, 15.0)
        else:
            # Negative growth
            return max(8.0 + growth, 0.0)  # Penalty for decline

    def score_debt_to_equity_sector_adjusted(self, debt_to_equity: float, sector: str) -> float:
        """
        Score debt-to-equity based on sector-specific thresholds

        Args:
            debt_to_equity: Debt to Equity ratio
            sector: Sector name

        Returns:
            Score from 0-35
        """
        benchmarks = self.get_sector_benchmarks(sector)
        debt_thresholds = benchmarks.get('debt_to_equity', self.benchmarks.DEFAULT_BENCHMARKS['debt_to_equity'])

        if debt_to_equity <= debt_thresholds['excellent']:
            return 35.0
        elif debt_to_equity <= debt_thresholds['good']:
            progress = (debt_thresholds['good'] - debt_to_equity) / (debt_thresholds['good'] - debt_thresholds['excellent'])
            return 25.0 + (10.0 * progress)
        elif debt_to_equity <= debt_thresholds['acceptable']:
            progress = (debt_thresholds['acceptable'] - debt_to_equity) / (debt_thresholds['acceptable'] - debt_thresholds['good'])
            return 15.0 + (10.0 * progress)
        else:
            # High debt penalty
            excess = debt_to_equity - debt_thresholds['acceptable']
            return max(5.0 - (excess * 2), 0.0)

    def get_sector_summary(self, sector: str) -> str:
        """Get a summary of sector characteristics"""
        benchmarks = self.get_sector_benchmarks(sector)

        return f"""
Sector: {sector}
- Excellent ROE: ≥{benchmarks['roe']['excellent']}%
- Acceptable P/E: ≤{benchmarks['pe_ratio']['acceptable']}x
- Good Net Margin: ≥{benchmarks['net_margin']['good']}%
- Excellent Revenue Growth: ≥{benchmarks['revenue_growth']['excellent']}%
- Good Debt/Equity: ≤{benchmarks['debt_to_equity']['good']}x
        """.strip()


# Global instance
sector_scorer = SectorAwareScorer()
