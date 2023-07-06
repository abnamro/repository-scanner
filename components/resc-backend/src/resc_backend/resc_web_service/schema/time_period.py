# Standard Library
from enum import Enum


class TimePeriod(str, Enum):
    DAY = "DAY"
    WEEK = "WEEK"
    LAST_WEEK = "LAST_WEEK"
    MONTH = "MONTH"
    YEAR = "YEAR"
    FOREVER = "FOREVER"
