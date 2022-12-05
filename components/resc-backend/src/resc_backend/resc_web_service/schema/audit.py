# pylint: disable=no-name-in-module
# Third Party
from pydantic import BaseModel, conint, conlist, constr

# First Party
from resc_backend.resc_web_service.schema.finding_status import FindingStatus


class AuditMultiple(BaseModel):
    finding_ids: conlist(conint(gt=0), min_items=1, max_items=500)
    status: FindingStatus
    comment: constr(max_length=255)
