# pylint: disable=no-name-in-module
# Standard Library
import datetime
from typing import Optional

# Third Party
from pydantic import BaseModel, conint, constr


class BranchBase(BaseModel):
    branch_id: constr(min_length=1, max_length=200)
    branch_name: constr(min_length=1, max_length=200)
    last_scanned_commit: constr(min_length=1, max_length=100)


class BranchCreate(BranchBase):
    repository_id: conint(gt=0)

    @classmethod
    def create_from_base_class(cls, base_object: BranchBase, repository_id: int):
        return cls(**(dict(base_object)), repository_id=repository_id)


class Branch(BranchBase):
    pass


class BranchRead(BranchCreate):
    id_: conint(gt=0)

    class Config:
        orm_mode = True


class ViewableBranch(BranchRead):
    last_scan_datetime: Optional[datetime.datetime]
    last_scan_id: Optional[conint(gt=0)]
    last_scan_finding_count: Optional[conint(gt=-1)]
    scan_finding_count: Optional[conint(gt=-1)]

    class Config:
        orm_mode = True
