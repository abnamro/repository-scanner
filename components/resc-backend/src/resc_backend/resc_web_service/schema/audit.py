# pylint: disable=no-name-in-module
# Third Party
from pydantic import BaseModel, conlist, constr

# First Party
from resc_backend.resc_web_service.schema.finding_status import FindingStatus


class AuditSingle(BaseModel):
    status: FindingStatus
    comment: constr(max_length=255)


class AuditMultiple(BaseModel):
    finding_ids: conlist(int, min_items=1)
    status: FindingStatus
    comment: constr(max_length=255)
