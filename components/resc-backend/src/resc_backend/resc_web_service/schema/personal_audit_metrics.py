# pylint: disable=no-name-in-module
# Third Party
from pydantic import BaseModel, conint


class PersonalAuditMetrics(BaseModel):
    today: conint(gt=-1) = 0
    current_week: conint(gt=-1) = 0
    last_week: conint(gt=-1) = 0
    current_month: conint(gt=-1) = 0
    current_year: conint(gt=-1) = 0
    forever: conint(gt=-1) = 0
    rank_current_week: conint(gt=-1) = 0
