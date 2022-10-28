# pylint: disable=no-name-in-module
# Standard Library
import datetime

# Third Party
from pydantic import BaseModel, conint, constr

# First Party
from resc_backend.resc_web_service.schema.scan_type import ScanType


class ScanBase(BaseModel):
    scan_type: ScanType = ScanType.BASE
    last_scanned_commit: constr(min_length=1, max_length=100)
    timestamp: datetime.datetime
    increment_number: conint(gt=-1) = 0
    rule_pack: constr(max_length=100)


class ScanCreate(ScanBase):
    branch_id: conint(gt=0)

    @classmethod
    def create_from_base_class(cls, base_object: ScanBase, branch_id: int):
        return cls(**(dict(base_object)), branch_id=branch_id)


class Scan(ScanBase):
    pass


class ScanRead(ScanCreate):
    id_: conint(gt=0)

    class Config:
        orm_mode = True
