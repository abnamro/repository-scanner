# pylint: disable=no-name-in-module
# Standard Library
import datetime
import sys
from typing import List, Optional

# Third Party
from pydantic import BaseModel, conint, conlist, constr

# First Party
from resc_backend.db.model import DBfinding


class FindingBase(BaseModel):
    file_path: constr(max_length=500)
    line_number: conint(gt=-1)
    column_start: conint(gt=-1)
    column_end: conint(gt=-1)
    commit_id: constr(max_length=120)
    commit_message: str
    commit_timestamp: datetime.datetime
    author: constr(max_length=200)
    email: constr(max_length=100)
    event_sent_on: Optional[datetime.datetime]
    rule_name: constr(max_length=400)


class FindingPatch(BaseModel):
    event_sent_on: datetime.datetime


class FindingCreate(FindingBase):
    repository_id: conint(gt=0)

    @classmethod
    def create_from_base_class(cls, base_object: FindingBase, repository_id: int):
        return cls(**(dict(base_object)), repository_id=repository_id)


class Finding(FindingBase):
    pass


class FindingRead(FindingCreate):
    id_: conint(gt=0)
    scan_ids: Optional[conlist(conint(gt=0), min_items=None, max_items=sys.maxsize)]

    class Config:
        orm_mode = True

    @classmethod
    def create_from_db_entities(cls, db_finding: DBfinding, scan_ids: List[int]):
        return FindingRead(
            id_=db_finding.id_,
            file_path=db_finding.file_path,
            line_number=db_finding.line_number,
            column_start=db_finding.column_start,
            column_end=db_finding.column_end,
            commit_id=db_finding.commit_id,
            commit_message=db_finding.commit_message,
            commit_timestamp=db_finding.commit_timestamp,
            author=db_finding.author,
            email=db_finding.email,
            event_sent_on=db_finding.event_sent_on,
            rule_name=db_finding.rule_name,
            repository_id=db_finding.repository_id,
            scan_ids=scan_ids
        )
