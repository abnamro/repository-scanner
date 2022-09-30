# pylint: disable=no-name-in-module
# Standard Library
import datetime
from typing import List, Optional

# Third Party
from pydantic import BaseModel, conint, constr

# First Party
from resc_backend.db.model import DBfinding
from resc_backend.resc_web_service.schema.finding_status import FindingStatus


class FindingBase(BaseModel):
    file_path: constr(max_length=500)
    line_number: conint(gt=-1)
    commit_id: constr(max_length=120)
    commit_message: str
    commit_timestamp: datetime.datetime
    author: constr(max_length=200)
    email: constr(max_length=100)
    status: FindingStatus = FindingStatus.NOT_ANALYZED
    comment: Optional[constr(max_length=255)] = None
    event_sent_on: Optional[datetime.datetime]
    rule_name: constr(max_length=400)


class FindingUpdate(BaseModel):
    file_path: Optional[constr(max_length=500)]
    line_number: Optional[conint(gt=-1)]
    commit_id: Optional[constr(max_length=120)]
    commit_message: Optional[str]
    commit_timestamp: Optional[datetime.datetime]
    author: Optional[constr(max_length=200)]
    email: Optional[constr(max_length=100)]
    status: Optional[FindingStatus]
    comment: Optional[constr(max_length=255)]
    event_sent_on: Optional[datetime.datetime]
    rule_name: Optional[constr(max_length=400)]


class FindingCreate(FindingBase):
    branch_info_id: conint(gt=0)

    @classmethod
    def create_from_base_class(cls, base_object: FindingBase, branch_info_id: int):
        return cls(**(dict(base_object)), branch_info_id=branch_info_id)


class Finding(FindingBase):
    pass


class FindingRead(FindingCreate):
    id_: conint(gt=0)
    scan_ids: Optional[List[conint(gt=0)]]

    class Config:
        orm_mode = True

    @classmethod
    def create_from_db_entities(cls, db_finding: DBfinding, scan_ids: List[int]):
        return FindingRead(
            id_=db_finding.id_,
            file_path=db_finding.file_path,
            line_number=db_finding.line_number,
            commit_id=db_finding.commit_id,
            commit_message=db_finding.commit_message,
            commit_timestamp=db_finding.commit_timestamp,
            author=db_finding.author,
            email=db_finding.email,
            status=db_finding.status,
            comment=db_finding.comment,
            event_sent_on=db_finding.event_sent_on,
            rule_name=db_finding.rule_name,
            branch_info_id=db_finding.branch_info_id,
            scan_ids=scan_ids
        )
