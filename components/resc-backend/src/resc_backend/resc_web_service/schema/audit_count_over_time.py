# pylint: disable=no-name-in-module
# Standard Library
from typing import Dict

# Third Party
from pydantic import BaseModel


class AuditCountOverTime(BaseModel):
    time_period: str
    audit_by_auditor_count: Dict[str, int]
    total: int = 0
