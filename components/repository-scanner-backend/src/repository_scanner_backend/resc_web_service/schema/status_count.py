# pylint: disable=no-name-in-module
# Third Party
from pydantic import BaseModel

# First Party
from repository_scanner_backend.resc_web_service.schema.finding_status import FindingStatus


class StatusCount(BaseModel):
    status: FindingStatus
    count: int = 0
