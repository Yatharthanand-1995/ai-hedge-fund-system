"""
US Top 100 Stocks List - Market Cap Based
Updated list of largest US companies by market capitalization
"""

from typing import List, Dict
import yfinance as yf
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# US Top 50 Elite Stocks - Professional Hedge Fund Universe
# Curated selection of highest-quality S&P 100 companies with excellent data quality and liquidity
US_TOP_100_STOCKS = [
    # Technology (15 stocks - 30% of universe)
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AVGO',
    'CRM', 'ORCL', 'CSCO', 'INTC', 'AMD', 'QCOM', 'ADBE',

    # Healthcare (10 stocks - 20% of universe)
    'UNH', 'JNJ', 'LLY', 'ABBV', 'PFE', 'MRK', 'TMO', 'DHR', 'BMY', 'AMGN',

    # Financial (8 stocks - 16% of universe)
    'V', 'JPM', 'MA', 'BAC', 'WFC', 'MS', 'GS', 'C',

    # Consumer (8 stocks - 16% of universe)
    'WMT', 'PG', 'HD', 'KO', 'COST', 'NKE', 'MCD', 'SBUX',

    # Energy (3 stocks - 6% of universe)
    'CVX', 'XOM', 'COP',

    # Industrial (4 stocks - 8% of universe)
    'BA', 'CAT', 'HON', 'GE',

    # Communication (2 stocks - 4% of universe)
    'NFLX', 'DIS'
]

# Sector classifications for Top 50 Elite Stocks
SECTOR_MAPPING = {
    'Technology': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AVGO',
                   'CRM', 'ORCL', 'CSCO', 'INTC', 'AMD', 'QCOM', 'ADBE'],

    'Healthcare': ['UNH', 'JNJ', 'LLY', 'ABBV', 'PFE', 'MRK', 'TMO', 'DHR', 'BMY', 'AMGN'],

    'Financial': ['V', 'JPM', 'MA', 'BAC', 'WFC', 'MS', 'GS', 'C'],

    'Consumer': ['WMT', 'PG', 'HD', 'KO', 'COST', 'NKE', 'MCD', 'SBUX'],

    'Energy': ['CVX', 'XOM', 'COP'],

    'Industrial': ['BA', 'CAT', 'HON', 'GE'],

    'Communication': ['NFLX', 'DIS']
}

# Market cap tiers
MARKET_CAP_TIERS = {
    'Mega Cap': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B'],
    'Large Cap': [symbol for symbol in US_TOP_100_STOCKS
                  if symbol not in ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B']]
}


class USTop100StockManager:
    """Manager for US Top 100 stocks data and operations"""

    def __init__(self):
        self.stocks = US_TOP_100_STOCKS
        self.sector_mapping = SECTOR_MAPPING
        self.market_cap_tiers = MARKET_CAP_TIERS
        logger.info(f"Initialized US Top 50 Elite Stock Manager with {len(self.stocks)} stocks across {len(self.sector_mapping)} sectors")

    def get_all_symbols(self) -> List[str]:
        """Get all stock symbols"""
        return self.stocks.copy()

    def get_by_sector(self, sector: str) -> List[str]:
        """Get stocks by sector"""
        return self.sector_mapping.get(sector, [])

    def get_by_tier(self, tier: str) -> List[str]:
        """Get stocks by market cap tier"""
        return self.market_cap_tiers.get(tier, [])

    def get_sector_for_symbol(self, symbol: str) -> str:
        """Get sector for a specific symbol"""
        for sector, symbols in self.sector_mapping.items():
            if symbol in symbols:
                return sector
        return 'Unknown'

    def get_tier_for_symbol(self, symbol: str) -> str:
        """Get market cap tier for a specific symbol"""
        for tier, symbols in self.market_cap_tiers.items():
            if symbol in symbols:
                return tier
        return 'Unknown'

    def validate_symbols(self, symbols: List[str] = None) -> Dict[str, bool]:
        """
        Validate that symbols have data available
        Returns dict of symbol -> has_data
        """
        if symbols is None:
            symbols = self.stocks

        validation_results = {}

        for symbol in symbols:
            try:
                # Try to fetch 1 day of data to validate
                data = yf.download(symbol, period='1d', progress=False)
                validation_results[symbol] = not data.empty

            except Exception as e:
                logger.warning(f"Failed to validate {symbol}: {e}")
                validation_results[symbol] = False

        valid_count = sum(validation_results.values())
        logger.info(f"Validated {valid_count}/{len(symbols)} symbols")

        return validation_results

    def get_stock_info(self, symbol: str) -> Dict:
        """Get detailed stock information"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            return {
                'symbol': symbol,
                'name': info.get('longName', 'N/A'),
                'sector': self.get_sector_for_symbol(symbol),
                'tier': self.get_tier_for_symbol(symbol),
                'market_cap': info.get('marketCap', 0),
                'industry': info.get('industry', 'N/A'),
                'country': info.get('country', 'N/A'),
                'exchange': info.get('exchange', 'N/A'),
                'currency': info.get('currency', 'USD')
            }

        except Exception as e:
            logger.error(f"Failed to get info for {symbol}: {e}")
            return {
                'symbol': symbol,
                'name': 'N/A',
                'sector': self.get_sector_for_symbol(symbol),
                'tier': self.get_tier_for_symbol(symbol),
                'error': str(e)
            }

    def create_stock_universe_df(self) -> pd.DataFrame:
        """Create a comprehensive DataFrame of all stocks with metadata"""
        stock_data = []

        for symbol in self.stocks:
            info = self.get_stock_info(symbol)
            stock_data.append(info)

        df = pd.DataFrame(stock_data)
        return df

    def get_liquid_stocks(self, min_volume: int = 1000000) -> List[str]:
        """
        Get stocks with sufficient liquidity

        Args:
            min_volume: Minimum average daily volume
        """
        liquid_stocks = []

        for symbol in self.stocks:
            try:
                # Get 30 days of data to check volume
                data = yf.download(symbol, period='30d', progress=False)

                if not data.empty and 'Volume' in data.columns:
                    avg_volume = data['Volume'].mean()
                    if avg_volume >= min_volume:
                        liquid_stocks.append(symbol)

            except Exception as e:
                logger.warning(f"Failed to check liquidity for {symbol}: {e}")

        logger.info(f"Found {len(liquid_stocks)} liquid stocks (min volume: {min_volume:,})")
        return liquid_stocks

    def get_recommended_backtest_universe(self) -> Dict[str, List[str]]:
        """
        Get recommended stock universes for different backtest scenarios
        """
        return {
            'mega_cap_tech': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META'],
            'mega_cap_diversified': self.get_by_tier('Mega Cap'),
            'tech_focused': self.get_by_sector('Technology')[:20],
            'healthcare_focused': self.get_by_sector('Healthcare')[:15],
            'financial_focused': self.get_by_sector('Financial')[:15],
            'balanced_top_50': self.stocks[:50],
            'full_universe': self.stocks,
            'liquid_only': self.get_liquid_stocks(),
            'sector_leaders': [
                # Tech leaders
                'AAPL', 'MSFT', 'GOOGL', 'NVDA',
                # Healthcare leaders
                'UNH', 'JNJ', 'PFE', 'ABBV',
                # Financial leaders
                'JPM', 'V', 'MA', 'BAC',
                # Consumer leaders
                'AMZN', 'WMT', 'HD', 'PG',
                # Energy leaders
                'XOM', 'CVX',
                # Industrial leaders
                'BA', 'CAT'
            ]
        }


# Global instance
stock_manager = USTop100StockManager()

# Convenience functions
def get_us_top_100() -> List[str]:
    """Get all US Top 100 stock symbols"""
    return stock_manager.get_all_symbols()

def get_stocks_by_sector(sector: str) -> List[str]:
    """Get stocks by sector"""
    return stock_manager.get_by_sector(sector)

def get_backtest_universe(universe_name: str) -> List[str]:
    """Get predefined backtest universe"""
    universes = stock_manager.get_recommended_backtest_universe()
    return universes.get(universe_name, [])

def validate_stock_data(symbols: List[str] = None) -> Dict[str, bool]:
    """Validate stock data availability"""
    return stock_manager.validate_symbols(symbols)