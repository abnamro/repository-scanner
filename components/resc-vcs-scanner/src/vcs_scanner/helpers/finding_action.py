# Standard Library
from enum import Enum


class FindingAction(str, Enum):
    INFO = "Info"
    WARN = "Warn"
    BLOCK = "Block"
