# Standard Library
from enum import Enum


class DateFilter(str, Enum):
    MONTH = "month"
    WEEK = "week"
    DAY = "day"
