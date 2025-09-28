"""
Data Quality Validation Layer
Validates and scores data quality for improved agent accuracy
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class DataQualityValidator:
    """
    Validates data quality and provides confidence scores
    """

    def __init__(self):
        self.required_metrics = {
            'fundamentals': [
                'returnOnEquity', 'profitMargins', 'operatingMargins',
                'revenueGrowth', 'earningsGrowth', 'currentRatio',
                'debtToEquity', 'freeCashflow', 'trailingPE', 'priceToBook'
            ],
            'price': ['Open', 'High', 'Low', 'Close', 'Volume'],
            'market': ['marketCap', 'currentPrice']
        }

    def validate_fundamentals_data(self, info: Dict, financials: pd.DataFrame,
                                 balance_sheet: pd.DataFrame) -> Dict:
        """
        Validate fundamentals data quality

        Returns:
            {
                'quality_score': 0-1,
                'missing_critical': [],
                'available_metrics': int,
                'data_freshness': 0-1,
                'confidence_multiplier': 0-1
            }
        """

        validation_result = {
            'quality_score': 0.0,
            'missing_critical': [],
            'available_metrics': 0,
            'data_freshness': 0.0,
            'confidence_multiplier': 1.0
        }

        # Check availability of required metrics
        available_count = 0
        missing_critical = []

        for metric in self.required_metrics['fundamentals']:
            value = info.get(metric)
            if value is not None and value != 0 and not (isinstance(value, float) and np.isnan(value)):
                available_count += 1
            else:
                missing_critical.append(metric)

        validation_result['available_metrics'] = available_count
        validation_result['missing_critical'] = missing_critical

        # Calculate quality score
        total_metrics = len(self.required_metrics['fundamentals'])
        availability_ratio = available_count / total_metrics
        validation_result['quality_score'] = availability_ratio

        # Check financial statements quality
        statements_quality = self._validate_financial_statements(financials, balance_sheet)
        validation_result['quality_score'] = (validation_result['quality_score'] + statements_quality) / 2

        # Data freshness check (based on available data recency)
        freshness = self._assess_data_freshness(info)
        validation_result['data_freshness'] = freshness

        # Calculate confidence multiplier
        confidence_multiplier = self._calculate_confidence_multiplier(
            validation_result['quality_score'],
            freshness,
            len(missing_critical)
        )
        validation_result['confidence_multiplier'] = confidence_multiplier

        return validation_result

    def validate_price_data(self, data: pd.DataFrame) -> Dict:
        """
        Validate price/volume data quality
        """
        validation_result = {
            'quality_score': 0.0,
            'data_points': 0,
            'missing_days': 0,
            'volume_quality': 0.0,
            'price_consistency': 0.0
        }

        if data.empty:
            return validation_result

        # Flatten MultiIndex columns if needed
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]

        # Check required columns
        required_cols = self.required_metrics['price']
        available_cols = [col for col in required_cols if col in data.columns]

        validation_result['data_points'] = len(data)

        if len(available_cols) == len(required_cols):
            validation_result['quality_score'] += 0.5

        # Volume quality check
        if 'Volume' in data.columns:
            volume_data = data['Volume'].dropna()
            if len(volume_data) > 0:
                avg_volume = volume_data.mean()
                zero_volume_days = (volume_data == 0).sum()
                volume_quality = 1.0 - (zero_volume_days / len(volume_data))
                validation_result['volume_quality'] = volume_quality
                validation_result['quality_score'] += 0.3 * volume_quality

        # Price consistency check
        if 'Close' in data.columns:
            close_data = data['Close'].dropna()
            if len(close_data) > 1:
                price_changes = np.diff(close_data) / close_data[:-1]
                # Check for unrealistic price movements (>50% daily change)
                extreme_moves = np.abs(price_changes) > 0.5
                consistency = 1.0 - (extreme_moves.sum() / len(price_changes))
                validation_result['price_consistency'] = consistency
                validation_result['quality_score'] += 0.2 * consistency

        # Cap quality score at 1.0
        validation_result['quality_score'] = min(validation_result['quality_score'], 1.0)

        return validation_result

    def _validate_financial_statements(self, financials: pd.DataFrame,
                                     balance_sheet: pd.DataFrame) -> float:
        """Validate financial statements data quality"""
        score = 0.0

        # Check if financials are available
        if not financials.empty:
            score += 0.5
            # Check for key revenue data
            if 'Total Revenue' in financials.index:
                revenue_data = financials.loc['Total Revenue'].dropna()
                if len(revenue_data) >= 2:  # At least 2 years of data
                    score += 0.25

        # Check if balance sheet is available
        if not balance_sheet.empty:
            score += 0.25

        return min(score, 1.0)

    def _assess_data_freshness(self, info: Dict) -> float:
        """Assess how fresh/recent the data appears to be"""
        freshness_score = 0.5  # Default neutral

        # Check if we have current price
        if info.get('currentPrice') and info.get('currentPrice') > 0:
            freshness_score += 0.2

        # Check if we have recent financial metrics
        recent_metrics = ['trailingPE', 'profitMargins', 'operatingMargins']
        available_recent = sum(1 for metric in recent_metrics if info.get(metric) is not None)
        freshness_score += 0.3 * (available_recent / len(recent_metrics))

        return min(freshness_score, 1.0)

    def _calculate_confidence_multiplier(self, quality_score: float,
                                       freshness: float, missing_count: int) -> float:
        """Calculate confidence multiplier based on data quality factors"""

        # Base multiplier from quality score
        multiplier = quality_score

        # Adjust for data freshness
        multiplier *= (0.7 + 0.3 * freshness)

        # Penalty for missing critical metrics
        if missing_count > 5:  # More than half missing
            multiplier *= 0.6
        elif missing_count > 3:
            multiplier *= 0.8

        # Ensure minimum confidence
        return max(multiplier, 0.2)

    def validate_agent_inputs(self, symbol: str, **kwargs) -> Dict:
        """
        Comprehensive validation for all agent inputs
        """
        validation_summary = {
            'symbol': symbol,
            'overall_quality': 0.0,
            'fundamentals_quality': None,
            'price_quality': None,
            'issues': [],
            'recommendations': []
        }

        issues = []
        recommendations = []
        quality_scores = []

        # Validate fundamentals data if provided
        if 'info' in kwargs:
            fund_validation = self.validate_fundamentals_data(
                kwargs.get('info', {}),
                kwargs.get('financials', pd.DataFrame()),
                kwargs.get('balance_sheet', pd.DataFrame())
            )
            validation_summary['fundamentals_quality'] = fund_validation
            quality_scores.append(fund_validation['quality_score'])

            if fund_validation['quality_score'] < 0.5:
                issues.append(f"Low fundamentals data quality ({fund_validation['quality_score']:.2f})")
                recommendations.append("Consider using partial scoring or longer data collection period")

        # Validate price data if provided
        if 'price_data' in kwargs:
            price_validation = self.validate_price_data(kwargs['price_data'])
            validation_summary['price_quality'] = price_validation
            quality_scores.append(price_validation['quality_score'])

            if price_validation['quality_score'] < 0.6:
                issues.append(f"Poor price data quality ({price_validation['quality_score']:.2f})")
                recommendations.append("Check data source and consider alternative price feeds")

        # Calculate overall quality
        if quality_scores:
            validation_summary['overall_quality'] = np.mean(quality_scores)

        validation_summary['issues'] = issues
        validation_summary['recommendations'] = recommendations

        return validation_summary

    def get_quality_adjusted_confidence(self, base_confidence: float,
                                      data_quality: Dict) -> float:
        """
        Adjust agent confidence based on data quality
        """
        if not data_quality:
            return base_confidence

        # Apply quality multiplier
        quality_multiplier = data_quality.get('confidence_multiplier', 1.0)
        adjusted_confidence = base_confidence * quality_multiplier

        # Ensure confidence bounds
        return max(min(adjusted_confidence, 1.0), 0.1)


# Global validator instance
data_validator = DataQualityValidator()