# pylint: disable=R0916,R0912,C0121
# Standard Library
import logging
from datetime import datetime

# Third Party
from sqlalchemy import func
from sqlalchemy.orm import Session

# First Party
from resc_backend.constants import DEFAULT_RECORDS_PER_PAGE_LIMIT, MAX_RECORDS_PER_PAGE_LIMIT
from resc_backend.db import model
from resc_backend.resc_web_service.schema.finding_status import FindingStatus

logger = logging.getLogger(__name__)


def create_audit(db_connection: Session, finding_id: int, auditor: str,
                 status: FindingStatus, comment: str = "") -> model.DBaudit:
    """
        Audit finding, updating the status and comment
    :param db_connection:
        Session of the database connection
    :param finding_id:
        id of the finding to audit
    :param auditor:
        identifier of the person performing the audit action
    :param status:
        audit status to set, type FindingStatus
    :param comment:
        audit comment to set
    :return: DBaudit
        The output will contain the audit that was created
    """
    db_audit = model.audit.DBaudit(
        finding_id=finding_id,
        auditor=auditor,
        status=status,
        comment=comment,
        timestamp=datetime.utcnow()
    )
    db_connection.add(db_audit)
    db_connection.commit()
    db_connection.refresh(db_audit)

    return db_audit


def get_finding_audits(db_connection: Session, finding_id: int, skip: int = 0,
                       limit: int = DEFAULT_RECORDS_PER_PAGE_LIMIT) -> [model.DBaudit]:
    """
        Get Audit entries for finding
    :param db_connection:
        Session of the database connection
    :param finding_id:
        id of the finding to audit
    :param skip:
        integer amount of records to skip to support pagination
    :param limit:
        integer amount of records to return, to support pagination
    :return: [DBaudit]
        The output will contain the list of audit items for the given finding
    """
    limit_val = MAX_RECORDS_PER_PAGE_LIMIT if limit > MAX_RECORDS_PER_PAGE_LIMIT else limit
    query = db_connection.query(model.DBaudit).filter(model.DBaudit.finding_id == finding_id)
    query = query.order_by(model.DBaudit.id_.desc()).offset(skip).limit(limit_val)
    finding_audits = query.all()
    return finding_audits


def get_finding_audits_count(db_connection: Session, finding_id: int) -> int:
    """
        Get count of Audit entries for finding
    :param db_connection:
        Session of the database connection
    :param finding_id:
        id of the finding to audit
    :return: total_count
        count of audit entries
    """
    total_count = db_connection.query(func.count(model.DBaudit.id_))\
        .filter(model.DBaudit.finding_id == finding_id).scalar()
    return total_count
