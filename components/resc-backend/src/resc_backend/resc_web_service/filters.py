# pylint: disable=R0902
# Standard Library
from datetime import datetime
from typing import List

# Third Party
from pydantic import validator
from pydantic.dataclasses import dataclass

# First Party
from resc_backend.resc_web_service.schema.finding_status import FindingStatus
from resc_backend.resc_web_service.schema.vcs_provider import VCSProviders


@dataclass
class FindingsFilter:
    vcs_providers: List[VCSProviders] = None
    finding_statuses: List[FindingStatus] = None
    rule_names: List[str] = None
    rule_tags: List[str] = None
    project_name: str = None
    repository_name: str = None
    branch_name: str = None
    scan_ids: List[int] = None
    start_date_time: datetime = None
    end_date_time: datetime = None
    event_sent: bool = None
    rule_pack_versions: List[str] = None

    @validator("end_date_time")
    @classmethod
    def date_range_check(cls, end_date_time: datetime, values: dict):
        if end_date_time and values["start_date_time"]:
            if values["start_date_time"] >= end_date_time:
                raise ValueError("the start of the date range needs to be prior to the end of it.")

        return end_date_time
