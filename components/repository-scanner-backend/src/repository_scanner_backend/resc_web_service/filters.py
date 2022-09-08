# pylint: disable=R0902
# Standard Library
from datetime import datetime
from typing import List

# Third Party
from pydantic import validator
from pydantic.dataclasses import dataclass

# First Party
from repository_scanner_backend.resc_web_service.schema.finding_status import FindingStatus
from repository_scanner_backend.resc_web_service.schema.vcs_provider import VCSProviders


@dataclass
class FindingsFilter:
    vcs_providers: List[VCSProviders] = None
    finding_statuses: List[FindingStatus] = None
    rule_names: List[str] = None
    project_name: str = None
    repository_name: str = None
    branch_name: str = None
    scan_ids: List[int] = None
    start_date_range: datetime = None
    end_date_range: datetime = None
    event_sent: bool = None

    @validator("end_date_range")
    @classmethod
    def date_range_check(cls, end_date_range: datetime, values: dict):
        if end_date_range and values["start_date_range"]:
            if values["start_date_range"] >= end_date_range:
                raise ValueError("the start of the date range needs to be prior to the end of it.")

        return end_date_range
