from datetime import date, timedelta
from enum import Enum

class Period(str, Enum):
    today = "today"
    week = "week"
    month = "month"
    all = "all"

def get_date_from(period: Period) -> date | None:
    today = date.today()
    if period == Period.today:
        return today
    if period == Period.week:
        return today - timedelta(days=7)
    if period == Period.month:
        return today - timedelta(days=30)
    return None