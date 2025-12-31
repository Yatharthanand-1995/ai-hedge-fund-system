"""
NYSE Market Calendar - Holiday detection for automated trading.

Includes NYSE holidays for 2024-2026 to determine trading days.
"""

from datetime import datetime, date
from typing import List

# NYSE Market Holidays (2024-2026)
NYSE_HOLIDAYS = [
    # 2024
    date(2024, 1, 1),   # New Year's Day
    date(2024, 1, 15),  # MLK Day
    date(2024, 2, 19),  # Presidents' Day
    date(2024, 3, 29),  # Good Friday
    date(2024, 5, 27),  # Memorial Day
    date(2024, 6, 19),  # Juneteenth
    date(2024, 7, 4),   # Independence Day
    date(2024, 9, 2),   # Labor Day
    date(2024, 11, 28), # Thanksgiving
    date(2024, 12, 25), # Christmas

    # 2025
    date(2025, 1, 1),   # New Year's Day
    date(2025, 1, 20),  # MLK Day
    date(2025, 2, 17),  # Presidents' Day
    date(2025, 4, 18),  # Good Friday
    date(2025, 5, 26),  # Memorial Day
    date(2025, 6, 19),  # Juneteenth
    date(2025, 7, 4),   # Independence Day
    date(2025, 9, 1),   # Labor Day
    date(2025, 11, 27), # Thanksgiving
    date(2025, 12, 25), # Christmas

    # 2026
    date(2026, 1, 1),   # New Year's Day
    date(2026, 1, 19),  # MLK Day
    date(2026, 2, 16),  # Presidents' Day
    date(2026, 4, 3),   # Good Friday
    date(2026, 5, 25),  # Memorial Day
    date(2026, 6, 19),  # Juneteenth
    date(2026, 7, 3),   # Independence Day (observed)
    date(2026, 9, 7),   # Labor Day
    date(2026, 11, 26), # Thanksgiving
    date(2026, 12, 25), # Christmas
]


def is_trading_day(check_date: datetime = None) -> bool:
    """
    Check if a given date is a trading day.

    Trading days are weekdays (Mon-Fri) that are not NYSE holidays.

    Args:
        check_date: Date to check (defaults to today)

    Returns:
        True if market is open for trading, False otherwise
    """
    if check_date is None:
        check_date = datetime.now()

    # Convert to date if datetime
    if isinstance(check_date, datetime):
        check_date = check_date.date()

    # Check if weekend
    if check_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False

    # Check if holiday
    if check_date in NYSE_HOLIDAYS:
        return False

    return True


def is_market_open(check_time: datetime = None) -> bool:
    """
    Check if market is currently open for trading.

    NYSE Regular hours: 9:30 AM - 4:00 PM ET

    Args:
        check_time: Time to check (defaults to now)

    Returns:
        True if market is open, False otherwise
    """
    if check_time is None:
        check_time = datetime.now()

    # First check if it's a trading day
    if not is_trading_day(check_time):
        return False

    # Check trading hours (9:30 AM - 4:00 PM ET)
    # For simplicity, we're assuming check_time is already in ET
    hour = check_time.hour
    minute = check_time.minute

    # Market opens at 9:30 AM
    if hour < 9:
        return False
    if hour == 9 and minute < 30:
        return False

    # Market closes at 4:00 PM
    if hour >= 16:
        return False

    return True


def get_next_trading_day(from_date: datetime = None) -> date:
    """
    Get the next trading day after given date.

    Args:
        from_date: Starting date (defaults to today)

    Returns:
        Next trading day
    """
    if from_date is None:
        from_date = datetime.now()

    current_date = from_date.date() if isinstance(from_date, datetime) else from_date

    # Check up to 10 days ahead (handles long weekends)
    for i in range(1, 11):
        from datetime import timedelta
        next_date = current_date + timedelta(days=i)
        if is_trading_day(next_date):
            return next_date

    # Fallback
    return current_date


def get_trading_days_in_month(year: int, month: int) -> List[date]:
    """
    Get all trading days in a given month.

    Args:
        year: Year
        month: Month (1-12)

    Returns:
        List of trading days
    """
    from calendar import monthrange

    _, last_day = monthrange(year, month)
    trading_days = []

    for day in range(1, last_day + 1):
        check_date = date(year, month, day)
        if is_trading_day(check_date):
            trading_days.append(check_date)

    return trading_days
