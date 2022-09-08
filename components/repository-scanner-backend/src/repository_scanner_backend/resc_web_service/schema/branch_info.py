# pylint: disable=no-name-in-module
# Standard Library
import datetime
from typing import Optional

# Third Party
from pydantic import BaseModel, conint, constr


class BranchInfoBase(BaseModel):
    branch_id: constr(min_length=1, max_length=200)
    branch_name: constr(min_length=1, max_length=200)
    last_scanned_commit: constr(min_length=1, max_length=100)


class BranchInfoCreate(BranchInfoBase):
    repository_info_id: conint(gt=0)

    @classmethod
    def create_from_base_class(cls, base_object: BranchInfoBase, repository_info_id: int):
        return cls(**(dict(base_object)), repository_info_id=repository_info_id)


class BranchInfo(BranchInfoBase):
    pass


class BranchInfoRead(BranchInfoCreate):
    id_: conint(gt=0)

    class Config:
        orm_mode = True


class ViewableBranchInfo(BranchInfoRead):
    last_scan_datetime: Optional[datetime.datetime]
    last_scan_id: Optional[conint(gt=0)]
    last_scan_finding_count: Optional[conint(gt=-1)]
    scan_finding_count: Optional[conint(gt=-1)]

    class Config:
        orm_mode = True
