# pylint: disable=no-name-in-module
# Standard Library
from typing import List

# Third Party
from pydantic import BaseModel, conint, constr

# First Party
from resc_backend.resc_web_service.schema.status_count import StatusCount


class RuleFindingCountModel(BaseModel):
    """
    :param Generic[Model]:
        Type of the object in the data list
    """
    rule_name: constr(max_length=100)
    finding_count: conint(gt=-1) = 0
    finding_statuses_count: List[StatusCount] = []

    class Config:
        orm_mode = True
