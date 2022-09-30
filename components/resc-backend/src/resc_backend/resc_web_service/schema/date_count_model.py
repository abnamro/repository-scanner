# pylint: disable=no-name-in-module
# Third Party
from pydantic import BaseModel, conint, constr


class DateCountModel(BaseModel):
    date_lable: constr(max_length=100)
    finding_count: conint(gt=-1) = 0

    class Config:
        orm_mode = True
