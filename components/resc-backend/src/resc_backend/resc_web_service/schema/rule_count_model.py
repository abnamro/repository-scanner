# pylint: disable=no-name-in-module
# Third Party
from pydantic import BaseModel, conint, conlist, constr

# First Party
from resc_backend.constants import MAX_RECORDS_PER_PAGE_LIMIT
from resc_backend.resc_web_service.schema.status_count import StatusCount


class RuleFindingCountModel(BaseModel):
    """
    :param Generic[Model]:
        Type of the object in the data list
    """
    rule_name: constr(max_length=100)
    finding_count: conint(gt=-1) = 0
    finding_statuses_count: conlist(item_type=StatusCount, min_items=None, max_items=MAX_RECORDS_PER_PAGE_LIMIT) = []

    class Config:
        orm_mode = True
